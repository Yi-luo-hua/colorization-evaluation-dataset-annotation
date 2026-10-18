"""Meaningful numerical and handoff contract checks, synthetic fixtures only."""
import argparse
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

import engine
import workflow as wf

CONFIG=wf.read_json(Path(__file__).with_name('config.json'))
CONFIG['gt_filter'].pop('exclude_manifest',None)  # Fixtures are independent of the live dataset registry.


class NumericalChecks(unittest.TestCase):
    def test_known_offset_and_iso_chroma_hue(self):
        gt=np.zeros((64,64,3),np.float32);gt[...,0]=50;gt[...,1]=np.linspace(-20,20,64)[None,:];gt[...,2]=10
        changed=gt.copy();changed[...,1:]+=np.array([6,8]);m,flags,_=engine.measure(gt,changed,CONFIG)
        self.assertAlmostEqual(m['robust_shift_norm'],10,places=5);self.assertTrue(flags['d_candidate']);self.assertFalse(flags['a_candidate'])
        changed=gt.copy();changed[...,1]=-gt[...,2];changed[...,2]=gt[...,1]
        m,_,maps=engine.measure(gt,changed,CONFIG)
        self.assertLess(m['abs_dc_p95'],1e-5);self.assertGreater(m['hue_component_max'],10)
        self.assertEqual(np.count_nonzero(engine.heatmap(gt,gt,CONFIG['display'])),0)

    def test_signed_heatmap_and_small_region(self):
        gt=np.zeros((100,100,3),np.float32);gt[...,0]=50;gt[...,1]=20
        gen=gt.copy();gen[:,:50,1]=40;gen[:,50:,1]=5
        heat=engine.heatmap(gt,gen,CONFIG['display'])
        self.assertGreater(heat[50,20,0],heat[50,20,2]);self.assertGreater(heat[50,80,2],heat[50,80,0])
        gen=gt.copy();gen[10:14,10:14,1]=0;gen[10:14,10:14,2]=20
        _,_,maps=engine.measure(gt,gen,CONFIG)
        candidates=engine.regions(maps,CONFIG)
        self.assertTrue(any(r['kind']=='hue_change' for r in candidates))


class ContractChecks(unittest.TestCase):
    def test_unscored_source_keeps_labels_without_fabricating_legacy_metadata(self):
        original=self.manifest['records'][0]['original_record']
        original['gpt_score']=None;original.pop('labeling_model');original.pop('labeling_timestamp')
        wf.write_json(self.run/'manifest.json',self.manifest)
        payload=self.payload();path=self.run/'unscored_reviews.json';wf.write_json(path,payload)
        wf.import_reviews(argparse.Namespace(batch=self.run,reviews=path))
        self.assertFalse(wf.export_candidate(argparse.Namespace(batch=self.run)))
        self.assertTrue((self.run/'visual_reviews.json').exists())
        self.assertFalse((self.run/'exports/reviewed_candidate.json').exists())
        pending=wf.read_json(self.run/'source_metadata_pending.json')
        self.assertEqual(pending['samples'][0]['missing_fields'],['gpt_score','labeling_model','labeling_timestamp'])
        saved=wf.read_json(self.run/'manifest.json')['records'][0]['original_record']
        self.assertIsNone(saved['gpt_score']);self.assertNotIn('labeling_model',saved)

    def test_downstream_cannot_rejudge_GT_or_shrink_categories(self):
        from compact_harness import expand
        base={'reviews':{r['sample_key']:[] for r in self.manifest['records']}}
        for legacy in [{'exclude_GT':'black_and_white'},{'BF_only':[]},{'NR':[]}]:
            raw=copy.deepcopy(base);raw['reviews']['S001']=legacy
            with self.assertRaises(ValueError):expand(self.manifest,raw)
        for category_list in [[],['B','F'],[k for k in wf.TAXONOMY if k!='C']]:
            payload=self.payload();payload['reviews'][0]['checked_categories']=category_list
            with self.assertRaises(ValueError):wf.validate_reviews(self.manifest,payload)
        for extra in [{'review_scope':'reference_free_BF_only'},{'GT_reason':'black_and_white'}]:
            payload=self.payload();payload['reviews'][0].update(extra)
            with self.assertRaises(ValueError):wf.validate_reviews(self.manifest,payload)
        payload=self.payload();payload['reviews'][0]['decision']='excluded_GT'
        with self.assertRaises(ValueError):wf.validate_reviews(self.manifest,payload)

    def test_same_GT_all_model_samples_remain_in_annotation_exports(self):
        first,second=self.manifest['records'][:2]
        second['gt_path']=first['gt_path'];second['gt_sha256']=first['gt_sha256']
        wf.write_json(self.run/'manifest.json',self.manifest)
        payload=self.payload();first_review=payload['reviews'][0]
        first_review.update(decision='defects',defects=[{'id':'A','severity':'','object':'全图','description':'生成图全图灰阶，上色失败。'}])
        path=self.run/'labels.json';wf.write_json(path,payload)
        wf.import_reviews(argparse.Namespace(batch=self.run,reviews=path))
        self.assertTrue(wf.export_candidate(argparse.Namespace(batch=self.run)))
        candidate=wf.read_json(self.run/'exports/reviewed_candidate.json')
        self.assertEqual(candidate['meta']['total_images'],6)
        self.assertEqual(len(wf.read_json(self.run/'exports/tasks_reviewed_stream.json')),6)
        self.assertFalse((self.run/'exports/excluded_GT.json').exists())
        self.assertEqual(candidate['annotations'][0]['reviewed_score'],1.0)
        self.assertEqual(candidate['annotations'][1]['defects'],[])

    def test_old_contract_is_readable_but_cannot_start_or_import_new_labels(self):
        old=copy.deepcopy(self.manifest);old['configuration']['annotation_contract']='post_screened_GT_generated_only_v1'
        payload=self.payload();wf.write_json(self.run/'manifest.json',old);wf.verify_sources(self.run)
        with self.assertRaises(ValueError):wf.validate_reviews(old,payload)
        from run_harness_trial import prepare_trial
        with self.assertRaises(ValueError):prepare_trial(self.run,wf.OUTPUT/'old_clone','compact')
        self.assertFalse((wf.OUTPUT/'old_clone').exists())

    def test_prepare_excludes_registered_GT_before_CV_and_keeps_task_indices(self):
        cfg=copy.deepcopy(CONFIG);cfg['gt_filter']['exclude_manifest']='excluded_GT.json'
        wf.write_json(self.temp/'excluded_GT.json',{'excluded_GT':[{'split':'val','image_id':'000000000001'}],'unresolved':[]})
        wf.prepare(argparse.Namespace(run_id='filtered',model='lcad',split='val',start=1,end=6),cfg)
        m=wf.verify_sources(wf.OUTPUT/'filtered')
        self.assertEqual([r['task_idx'] for r in m['records']],[1,3,4,5,6])
        self.assertEqual(m['GT_quality_filter']['skipped_samples'][0]['task_idx'],2)

    def setUp(self):
        wf.OUTPUT.mkdir(parents=True,exist_ok=True);self.parent=wf.OUTPUT.resolve();self.temp=Path(tempfile.mkdtemp(prefix='contract_check_',dir=self.parent)).resolve()
        assert self.temp.parent==self.parent
        self.old_root,self.old_base,self.old_output=engine.ROOT,wf.BASE,wf.OUTPUT
        engine.ROOT=self.temp;wf.BASE=self.temp/'LS_lcad_reviewer';wf.OUTPUT=wf.BASE/'intermediate/experiments'
        (wf.BASE/'tasks_pool/val').mkdir(parents=True);(wf.BASE/'core_pipeline').mkdir()
        shutil.copy2(self.old_base/'core_pipeline/validate_export_schema.py',wf.BASE/'core_pipeline/validate_export_schema.py')
        data=self.temp/CONFIG['datasets']['val'];(data/'image').mkdir(parents=True);(data/'model/lcad').mkdir(parents=True)
        tasks=[]
        for i in range(6):
            stem=f'{i:012d}';image=np.zeros((90,120,3),np.uint8);image[:,:60]=[130,80+i*5,30];image[:,60:]=[40,110,180]
            Image.fromarray(image).save(data/'image'/f'{stem}.jpg');Image.fromarray(image).save(data/'model/lcad'/f'{stem}.png')
            record={'image_id':f'lcad/{stem}.png','file_path':f'lcad/{stem}.png','source_dataset':'coco','role':'lcad','defects':[],
                    'gpt_score':4.5,'labeling_model':'gpt-5.6-sol','labeling_timestamp':'2026-10-12T00:00:00+00:00'}
            tasks.append({'data':{'image_id':record['image_id'],'original_record':record}})
        wf.write_json(wf.BASE/'tasks_pool/val/tasks_lcad_val_1428.json',tasks)
        wf.prepare(argparse.Namespace(run_id='fixture',model='lcad',split='val',start=1,end=6),CONFIG)
        self.run=wf.OUTPUT/'fixture';self.manifest=wf.verify_sources(self.run)

    def tearDown(self):
        engine.ROOT,wf.BASE,wf.OUTPUT=self.old_root,self.old_base,self.old_output
        assert self.temp.resolve().parent==self.parent and self.temp.name.startswith('contract_check_')
        shutil.rmtree(self.temp)

    def payload(self):
        p=wf.read_json(self.run/'review_template.json')
        if p['schema_version']=='visual_review_compact_v1':
            from compact_harness import expand
            return expand(self.manifest,{'reviews':{key:[] for key in p['reviews']}})
        for r in p['reviews']:
            r.update(inspection_complete=True,decision='no_defects',checked_categories=list(wf.TAXONOMY),uncertainties=[],needs_crops=[])
        return p

    def test_compact_description_exports_without_invented_color_fields(self):
        from compact_harness import expand
        raw={'schema_version':'visual_review_compact_v1','reviews':{r['sample_key']:[] for r in self.manifest['records']}}
        raw['reviews']['S001']=[{'id':'C','severity':'L2','object':'外套','description':'GT红色，生成紫色。'}]
        wf.write_json(self.run/'reviews_gemini.json',raw)
        wf.import_reviews(argparse.Namespace(batch=self.run,reviews=self.run/'reviews_gemini.json'))
        wf.export_candidate(argparse.Namespace(batch=self.run))
        record=wf.read_json(self.run/'exports/reviewed_candidate.json')['annotations'][0]
        self.assertEqual(record['defects'][0]['description'],'外套：GT红色，生成紫色。')
        self.assertEqual(record['gpt_score'],self.manifest['records'][0]['original_record']['gpt_score'])

    def test_dynamic_groups_preserve_image_pixels_and_complete_handoff(self):
        from compact_harness import build_prompt
        reference_pixels={}
        for groups in [3,6,8]:
            cfg=copy.deepcopy(CONFIG);cfg['sheet']['groups_per_sheet']=groups
            run=wf.OUTPUT/f'groups_{groups}';run.mkdir();(run/'sheets').mkdir()
            records=[copy.deepcopy(self.manifest['records'][i%6]) for i in range(10)]
            for i,r in enumerate(records,1):r['sample_key']=f'S{i:03d}'
            sheets=wf.render(records,run,cfg)
            self.assertEqual([s['groups'] for s in sheets],[min(groups,10-start) for start in range(0,10,groups)])
            m={**self.manifest,'configuration':cfg,'records':records,'sheets':sheets}
            wf.write_json(run/'manifest.json',m);wf.write_handoff(run,m);wf.verify_sources(run)
            request=wf.read_json(run/'review_request.json')
            self.assertEqual(request['sheet_groups'],groups)
            self.assertEqual(len(request['samples']),10)
            self.assertIn(f'每张最多{groups}组',build_prompt(request,'reviews.json'))
            self.assertIn(f'每张最多{groups}组',(run/'START_HERE.md').read_text(encoding='utf-8'))
            for record in records:
                with Image.open(run/record['sheet']) as sheet:
                    top=(record['sheet_row']-1)*cfg['sheet']['card_height']
                    pixels=np.array(sheet.crop((0,top+94,1560,top+414)))
                if record['sample_key'] in reference_pixels:
                    np.testing.assert_array_equal(pixels,reference_pixels[record['sample_key']])
                else:reference_pixels[record['sample_key']]=pixels

    def test_six_groups_and_import_export_roundtrip(self):
        self.assertEqual(len(self.manifest['sheets']),1);self.assertEqual(self.manifest['sheets'][0]['groups'],6)
        request=wf.read_json(self.run/'review_request.json')
        self.assertEqual(request['samples'][0]['generated_color']['measurement_size'],[120,90])
        self.assertNotIn('color_structure',request['samples'][0])
        template=wf.read_json(self.run/'review_template.json')
        self.assertEqual([r['sample_key'] for r in request['samples']],[f'S{i:03d}' for i in range(1,7)])
        template_keys=list(template['reviews']) if isinstance(template['reviews'],dict) else [r['sample_key'] for r in template['reviews']]
        self.assertEqual(template_keys,[r['sample_key'] for r in request['samples']])
        if isinstance(template['reviews'],dict):self.assertTrue(all(v is None for v in template['reviews'].values()))
        text=json.dumps(request)
        for forbidden in ['gt_path','model_path','source_sample_key','000000000000','000000000005']:
            self.assertNotIn(forbidden,text)
        with Image.open(self.run/'sheets/sheet_001.png') as sheet:
            self.assertEqual(sheet.size,(1560,2580))
        p=self.payload();p['reviews'][0]['decision']='defects'
        p['reviews'][0]['defects']=[{'id':'C','object':obj,'location':'左侧','gt_color':'棕色','generated_color':'蓝色','severity':sev,'evidence':'接口测试夹具，非真实图像标注'} for obj,sev in [('门','L1'),('桌子','L2')]]
        wf.write_json(self.run/'fixture_reviews.json',p);wf.import_reviews(argparse.Namespace(batch=self.run,reviews=self.run/'fixture_reviews.json'));wf.export_candidate(argparse.Namespace(batch=self.run))
        exported=wf.read_json(self.run/'exports/reviewed_candidate.json')['annotations']
        self.assertEqual(len(exported),6);self.assertEqual(len(exported[0]['defects']),2)
        self.assertEqual(exported[0]['gpt_score'],4.5);self.assertEqual(exported[0]['original_gpt_score'],4.5);self.assertEqual(exported[0]['human_review']['completed_by'],0)
        self.assertIsNone(exported[0]['reviewed_score'])

    def test_incomplete_duplicate_and_unknown_severity_blocked(self):
        p=wf.read_json(self.run/'review_template.json')
        with self.assertRaises(ValueError):wf.validate_reviews(self.manifest,p)
        p=self.payload();p['reviews'].append(copy.deepcopy(p['reviews'][0]))
        with self.assertRaises(ValueError):wf.validate_reviews(self.manifest,p)
        p=self.payload();r=p['reviews'][0];r['decision']='defects';r['defects']=[{'id':'C','object':'门','location':'左侧','gt_color':'棕','generated_color':'蓝','severity':None,'evidence':'待等级校准'}]
        wf.validate_reviews(self.manifest,p)
        with self.assertRaises(ValueError):wf.validate_reviews(self.manifest,p,strict=True)
        r['defects'][0]['id']='A';r['defects'][0]['severity']='L1'
        with self.assertRaises(ValueError):wf.validate_reviews(self.manifest,p)

    def test_prepare_measures_colour_before_resize_and_alignment(self):
        data=self.temp/CONFIG['datasets']['val']
        generated=np.full((1600,1600,3),128,np.uint8)
        generated[0,0]=[129,128,128]
        Image.fromarray(generated).save(data/'model/lcad/000000000000.png')
        wf.prepare(argparse.Namespace(run_id='original_resolution',model='lcad',split='val',start=1,end=1),CONFIG)
        manifest=wf.verify_sources(wf.OUTPUT/'original_resolution')
        record=manifest['records'][0]
        self.assertFalse(record['cv_flags']['a_candidate'])
        self.assertEqual(record['metrics']['generated_color']['colored_pixel_count'],1)
        self.assertEqual(record['metrics']['generated_color']['measurement_size'],[1600,1600])

    def test_changed_image_rejected(self):
        path=self.temp/self.manifest['records'][0]['model_path'];Image.new('RGB',(120,90),'black').save(path)
        with self.assertRaises(ValueError):wf.verify_sources(self.run)

    def test_noncontiguous_selection_preserves_identity(self):
        path=self.temp/'selection.json';wf.write_json(path,{'split':'val','samples':[{'model':'lcad','task_idx':i} for i in [6,2,4]]})
        args=argparse.Namespace(run_id='selected',model='lcad',split='val',start=1,end=12,selection=path)
        wf.prepare(args,CONFIG);manifest=wf.verify_sources(wf.OUTPUT/'selected')
        self.assertEqual([r['task_idx'] for r in manifest['records']],[6,2,4])
        self.assertEqual([r['source_sample_key'].split('/')[-1] for r in manifest['records']],['000000000005','000000000001','000000000003'])
        self.assertEqual([r['sample_key'] for r in manifest['records']],['S001','S002','S003'])
        wf.write_json(path,{'split':'val','samples':[{'model':'lcad','task_idx':1,'sample_key':'val/lcad/999999999999'}]})
        args.run_id='wrong_identity'
        with self.assertRaises(ValueError):wf.prepare(args,CONFIG)

    def test_automatic_grouped_details_and_budget(self):
        self.manifest['configuration']['visual_harness']['maximum_detail_rounds']=1
        wf.write_json(self.run/'manifest.json',self.manifest)
        p=self.payload()
        for r in p['reviews']:
            r.update(decision='uncertain',uncertainties=['物体较小'],needs_crops=[{'sample_key':r['sample_key'],'bbox':[0.1,0.1,0.4,0.4],'reason':'查看物体边界'}])
        path=self.run/'provisional.json';wf.write_json(path,p)
        args=argparse.Namespace(batch=self.run,reviews=path);response=wf.build_detail_sheets(args)
        self.assertEqual(response['state'],'detail_sheets_ready');self.assertEqual(len(response['samples']),6)
        manifest=wf.verify_sources(self.run);sheets=manifest['detail_rounds'][0]['sheets']
        self.assertEqual(len(sheets),1);self.assertEqual(sheets[0]['groups'],6);self.assertEqual(sheets[0]['size'],[1560,2580])
        for private in ['gt_path','model_path','000000000000']:self.assertNotIn(private,json.dumps(response))
        self.assertEqual(wf.build_detail_sheets(args)['state'],'detail_budget_exhausted')
        target=self.run/sheets[0]['path'];Image.new('RGB',(1560,2580),'red').save(target)
        with self.assertRaises(ValueError):wf.verify_sources(self.run)

    def test_whole_image_detail_request_is_not_a_per_image_fallback(self):
        self.manifest['configuration']['visual_harness']['maximum_detail_rounds']=1
        wf.write_json(self.run/'manifest.json',self.manifest)
        p=self.payload();r=p['reviews'][0]
        r.update(decision='uncertain',uncertainties=['看不清'],needs_crops=[{'sample_key':r['sample_key'],'bbox':[0,0,1,1]}])
        path=self.run/'provisional.json';wf.write_json(path,p)
        response=wf.build_detail_sheets(argparse.Namespace(batch=self.run,reviews=path))
        self.assertEqual(response['state'],'no_eligible_detail_requests');self.assertEqual(response['unserved_samples'],['S001'])
        self.assertFalse((self.run/'detail_rounds').exists())

    def test_fast_default_has_no_detail_round_or_source_hints(self):
        self.assertEqual(self.manifest['configuration']['visual_harness']['maximum_detail_rounds'],0)
        request=wf.read_json(self.run/'review_request.json')
        self.assertTrue(all('region_candidates' not in r and len(r['metrics'])<=6 for r in request['samples']))
        self.assertLess(len((self.run/'review_request.json').read_text(encoding='utf-8').splitlines()),30)
        prompt=(self.run/'START_HERE.md').read_text(encoding='utf-8')
        self.assertIn('速度第一',prompt);self.assertIn('needs_crops固定[]',prompt)


if __name__=='__main__':unittest.main(verbosity=2)
