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
        for r in p['reviews']:
            r.update(inspection_complete=True,decision='no_defects',checked_categories=list(wf.TAXONOMY),uncertainties=[],needs_crops=[])
        return p

    def test_six_groups_and_import_export_roundtrip(self):
        self.assertEqual(len(self.manifest['sheets']),1);self.assertEqual(self.manifest['sheets'][0]['groups'],6)
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

    def test_changed_image_rejected(self):
        path=self.temp/self.manifest['records'][0]['model_path'];Image.new('RGB',(120,90),'black').save(path)
        with self.assertRaises(ValueError):wf.verify_sources(self.run)

    def test_noncontiguous_selection_preserves_identity(self):
        path=self.temp/'selection.json';wf.write_json(path,{'split':'val','samples':[{'model':'lcad','task_idx':i} for i in [6,2,4]]})
        args=argparse.Namespace(run_id='selected',model='lcad',split='val',start=1,end=12,selection=path)
        wf.prepare(args,CONFIG);manifest=wf.verify_sources(wf.OUTPUT/'selected')
        self.assertEqual([r['task_idx'] for r in manifest['records']],[6,2,4])
        self.assertEqual([r['sample_key'].split('/')[-1] for r in manifest['records']],['000000000005','000000000001','000000000003'])
        wf.write_json(path,{'split':'val','samples':[{'model':'lcad','task_idx':1,'sample_key':'val/lcad/999999999999'}]})
        args.run_id='wrong_identity'
        with self.assertRaises(ValueError):wf.prepare(args,CONFIG)


if __name__=='__main__':unittest.main(verbosity=2)
