"""Round 14: conservative GT gate and bounded reference-free pilot, not production."""
import argparse
import copy
import csv
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image,ImageDraw

import engine
import compact_harness
from workflow import OUTPUT,read_json,write_json,font,utc,render,model_image,align,verify_sources

PREFIX='gt_reference_round14'


def scout():
    profiles=engine.ROOT/'LS_lcad_reviewer/intermediate/audits/cv_workflow_experiment_20261012_01/gt_profiles.csv'
    with profiles.open(encoding='utf-8-sig') as source:rows=list(csv.DictReader(source))
    rows=[r for r in rows if r['split']=='train']
    selected=[]
    def add(items):
        for r in items:
            if r['image_id'] not in {v['image_id'] for v in selected}:selected.append(r)
    add(sorted(rows,key=lambda r:float(r['mean_c']))[:12])
    for key in ['mean_b','mean_a']:
        for reverse in [True,False]:add(sorted(rows,key=lambda r:float(r[key]),reverse=reverse)[:6])
    add(sorted(rows,key=lambda r:math.hypot(float(r['mean_a']),float(r['mean_b']))/float(r['mean_c']),reverse=True)[:12])
    out=OUTPUT/f'{PREFIX}_scout_20261013';out.mkdir()
    cfg=read_json(Path(__file__).with_name('config.json'))
    canvas=Image.new('RGB',(1800,245*math.ceil(len(selected)/6)),(242,244,247));draw=ImageDraw.Draw(canvas)
    for i,r in enumerate(selected):
        left=(i%6)*300;top=(i//6)*245
        image=Image.open(engine.ROOT/cfg['datasets']['train']/'image'/f"{r['image_id']}.jpg").convert('RGB')
        image.thumbnail((288,208));canvas.paste(image,(left+(300-image.width)//2,top+28+(208-image.height)//2))
        draw.text((left+8,top+3),f"G{i+1:02d} C={float(r['mean_c']):.1f} P95={float(r['p95_c']):.1f}",fill='black',font=font(16))
        r['scout_key']=f'G{i+1:02d}'
    canvas.save(out/'GT_scout.png');write_json(out/'internal_selection.json',selected)
    print(out/'GT_scout.png')


def transform(pixels,mode,settings):
    if mode=='identity':return pixels.copy()
    lab=engine.lab(pixels)
    if mode=='gray':lab[...,1:]=0
    elif mode=='scale':lab[...,1:]*=settings['scale']
    elif mode=='cast':lab[...,1:]+=settings['cast_ab']
    else:raise ValueError(mode)
    return engine.rgb(lab)


def prepare():
    cv2.setNumThreads(1)
    settings=read_json(Path(__file__).with_name('gt_reference_round14_config.json'))
    cfg=read_json(Path(__file__).with_name('config.json'))
    scout_rows=read_json(OUTPUT/f'{PREFIX}_scout_20261013/internal_selection.json')
    scout_map={r['scout_key']:r for r in scout_rows}
    setup=OUTPUT/f'{PREFIX}_setup_20261013';setup.mkdir();(setup/'assets').mkdir()
    pools={};source_hashes={};records=[]
    for split in ['train','val']:
        path=next((engine.ROOT/'LS_lcad_reviewer/tasks_pool'/split).glob('*lcad*.json'))
        tasks=read_json(path);pools[split]={Path(t['data']['original_record']['image_id']).stem:(i,t) for i,t in enumerate(tasks,1)}
        source_hashes[str(path.relative_to(engine.ROOT))]=engine.sha256(path)
    def add(split,stem,case,GT_path=None,generated_path=None):
        index,task=pools[split][stem];original=copy.deepcopy(task['data']['original_record'])
        root=engine.ROOT/cfg['datasets'][split]
        gt=GT_path or root/'image'/f'{stem}.jpg'
        gen=generated_path or model_image(root/'model/lcad',stem)
        gr=engine.read_rgb(gt,cfg['analysis_max_side']);mr=align(gr,engine.read_rgb(gen,cfg['analysis_max_side']))
        metrics,flags,_=engine.measure(engine.lab(gr),engine.lab(mr),cfg)
        data=copy.deepcopy(task['data'])
        if case['kind']=='synthetic_control':
            original['image_id']=original['file_path']=f'lcad/round14_control_{len(records)+1:03d}.png'
            data.update(image='/data/local-files/?d='+str(gen.relative_to(engine.ROOT)).replace('\\','/'),
                        reference='/data/local-files/?d='+str(gt.relative_to(engine.ROOT)).replace('\\','/'),
                        image_id=original['image_id'],sample_title=original['image_id'],original_record=copy.deepcopy(original),
                        source_info='Round14 synthetic diagnostic control; never merge into production dataset')
        records.append({'sample_key':f'S{len(records)+1:03d}','source_sample_key':f'{split}/lcad/{stem}/{case["case"]}',
                        'task_idx':index,'split':split,'model':'lcad','gt_path':str(gt.relative_to(engine.ROOT)),
                        'model_path':str(gen.relative_to(engine.ROOT)),'gt_sha256':engine.sha256(gt),'model_sha256':engine.sha256(gen),
                        'original_record':original,'source_task_data':data,'metrics':metrics,'cv_flags':flags,
                        'region_candidates':[],'region_analysis_max_side':cfg['regions']['max_side'],'diagnostic':case})
    for key in settings['real_scout_keys']:
        row=scout_map[key]
        add('train',row['image_id'],{'kind':'host_visual_diagnostic','case':key,'expected_GT_untrusted':False,
                                   'note':'GT retains valid object colors or scene lighting/style can explain appearance; uncertain remains trusted.'})
    add('val','000000509699',{'kind':'host_visual_diagnostic','case':'old_BW_photo','expected_GT_untrusted':True,
                            'note':'Photo subjects grayscale; border holes do not provide object color reference.'})
    add('val','000000224119',{'kind':'host_visual_diagnostic','case':'blue_aircraft_seats','expected_GT_untrusted':False,
                            'note':'Blue seats are a valid color reference; known prior false exclusion.'})
    for key in settings['control_base_keys']:
        stem=scout_map[key]['image_id'];pixels=engine.read_rgb(engine.ROOT/cfg['datasets']['train']/'image'/f'{stem}.jpg')
        for intervention in settings['control_interventions']:
            parameters={**settings,**intervention};paths={}
            for name,mode in [('GT',intervention['GT']),('generated',intervention['generated'])]:
                path=setup/'assets'/f'{key}_{intervention["name"]}_{name}.png'
                Image.fromarray(transform(pixels,mode,parameters)).save(path);paths[name]=path
            add('train',stem,{'kind':'synthetic_control','base':key,'case':intervention['name'],
                             'expected_GT_untrusted':True,'expected_category':intervention['expected_category'],
                             'expected_GT_reason':'black_and_white' if intervention['GT']=='gray' else 'abnormal_global_cast'},
                paths['GT'],paths['generated'])
    for policy,suffix in [('visual_confirm_BF_only','BF36'),('visual_confirm_reference_free','NR36')]:
        run=OUTPUT/f'{PREFIX}_{suffix}_20261013';run.mkdir();(run/'sheets').mkdir()
        config=copy.deepcopy(cfg);config['gt_reference']['policy']=policy
        config['visual_harness']['label_boundary_version']='conservative_GT_NR_pilot_round14'
        rows=copy.deepcopy(records);sheets=render(rows,run,config)
        manifest={'schema_version':'cv_handoff_v2','created_at':utc(),'state':'awaiting_external_visual_review',
                  'configuration':config,'source_task_sha256':source_hashes,'records':rows,'sheets':sheets,
                  'experimental_diagnostic_only':True,'contains_synthetic_controls':True,
                  'source_code_sha256':{p.name:engine.sha256(p) for p in [Path(__file__),Path(__file__).with_name('compact_harness.py'),Path(__file__).with_name('workflow.py')]}}
        write_json(run/'manifest.json',manifest)
        request={'schema_version':'visual_review_v1','reviewer':config['external_reviewer'],'sheet_groups':6,
                 'display':config['display'],'visual_harness':config['visual_harness'],
                 'gt_reference_policy':policy,'gt_reliability':config['gt_reference']['reliability'],
                 'low_chroma_GT_candidates':[r['sample_key'] for r in rows if r['cv_flags']['gt_low_chroma_candidate']],
                 'samples':[{k:r[k] for k in ['sample_key','sheet','sheet_row']} for r in rows]}
        write_json(run/'review_request.json',request);write_json(run/'review_template.json',compact_harness.template(request))
        (run/'ANTIGRAVITY_HANDOFF.md').write_bytes(Path(__file__).with_name('ANTIGRAVITY_HANDOFF.md').read_bytes())
        from review_boundaries import write_start_instructions
        write_start_instructions(run,manifest);verify_sources(run)
    left=OUTPUT/f'{PREFIX}_BF36_20261013';right=OUTPUT/f'{PREFIX}_NR36_20261013'
    lm=read_json(left/'manifest.json');rm=read_json(right/'manifest.json')
    assert [s['sha256'] for s in lm['sheets']]==[s['sha256'] for s in rm['sheets']]
    write_json(setup/'manifest.json',{'created_at':utc(),'baseline':left.name,'trial':right.name,'samples_per_condition':len(records),
               'real_samples':18,'synthetic_controls':18,'control_GT_bases':3,'same_sheet_hashes':True,
               'changed_surface':'reference-free branch only; same conservative GT gate, boards and numerical CV',
               'note':settings['note'],'source_code_sha256':lm['source_code_sha256']})
    for name in ['experiment_gt_reference.py','gt_reference_round14_config.json','compact_harness.py','workflow.py']:
        (setup/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    print('Prepared paired conditions:',left.name,right.name,len(records),'samples each')


def analyze():
    setup=OUTPUT/f'{PREFIX}_setup_20261013';plan=read_json(setup/'manifest.json');conditions={}
    for label,run_name in [('BF',plan['baseline']),('NR',plan['trial'])]:
        run=OUTPUT/run_name;manifest=verify_sources(run)
        reviews={r['sample_key']:r for r in read_json(run/'visual_reviews.json')['reviews']}
        jobs=[read_json(p) for p in run.glob('parts/job_*/agy_calls/*/result.json')]
        rows=[];gates={}
        for record in manifest['records']:
            review=reviews[record['sample_key']];diag=record['diagnostic']
            excluded=review.get('review_scope','').startswith('reference_free_')
            codes=sorted({d['id'] for d in review['defects']})
            rows.append({'sample_key':record['sample_key'],'diagnostic':diag,'GT_excluded':excluded,
                         'GT_reason':review.get('GT_reason'),'scope':review.get('review_scope','reference'),
                         'defect_ids':codes,'defects':review['defects'],
                         'expected_category_present':diag.get('expected_category') in codes if diag.get('expected_category') else None})
        for kind in ['host_visual_diagnostic','synthetic_control']:
            subset=[r for r in rows if r['diagnostic']['kind']==kind]
            gates[kind]={'samples':len(subset),
                'correct_exclusions':sum(r['GT_excluded'] and r['diagnostic']['expected_GT_untrusted'] for r in subset),
                'false_exclusions':sum(r['GT_excluded'] and not r['diagnostic']['expected_GT_untrusted'] for r in subset),
                'missed_untrusted':sum(not r['GT_excluded'] and r['diagnostic']['expected_GT_untrusted'] for r in subset),
                'retained_trusted':sum(not r['GT_excluded'] and not r['diagnostic']['expected_GT_untrusted'] for r in subset)}
        controlled={}
        for case in sorted({r['diagnostic']['case'] for r in rows if r['diagnostic']['kind']=='synthetic_control'}):
            subset=[r for r in rows if r['diagnostic']['kind']=='synthetic_control' and r['diagnostic']['case']==case]
            controlled[case]={'samples':len(subset),'excluded_GT':sum(r['GT_excluded'] for r in subset),
                'expected_category':subset[0]['diagnostic']['expected_category'],
                'expected_category_present':sum(r['expected_category_present'] is True for r in subset),
                'generated_identity_color_penalties':sum(bool(set(r['defect_ids'])&{'A','D','E1','E2'}) for r in subset) if subset[0]['diagnostic']['expected_category'] is None else None,
                'rows':[{k:r[k] for k in ['sample_key','scope','defect_ids']} for r in subset]}
        invariance=[]
        for base in read_json(Path(__file__).with_name('gt_reference_round14_config.json'))['control_base_keys']:
            pair=[next(r for r in rows if r['diagnostic'].get('base')==base and r['diagnostic']['case']==case) for case in ['bw_natural','cast_natural']]
            invariance.append({'base':base,'same_generated_pixels':True,
                'both_GT_excluded':all(r['GT_excluded'] for r in pair),
                'same_defect_category_set':pair[0]['defect_ids']==pair[1]['defect_ids'],'samples':[r['sample_key'] for r in pair]})
        timing=read_json(run/'agy_calls/parallel/result.json')
        conditions[label]={'run':run_name,'gate':gates,'controls':controlled,'counterfactual_same_generated':invariance,
                           'timing':timing,'mean_call_seconds':sum(j['elapsed_seconds'] for j in jobs)/len(jobs),
                           'unresolved':sum(r['decision']=='uncertain' for r in reviews.values()),'rows':rows}
    report={'created_at':utc(),'conditions':conditions,
            'meaning':'Synthetic known interventions and Codex scene observations reported separately; not dataset population accuracy. Chroma scaling is a known intervention, not proof of a perceptual defect in every scene.',
            'default_config_unchanged':read_json(Path(__file__).with_name('config.json'))['gt_reference']['policy']=='visual_confirm_BF_only'}
    write_json(setup/'results.json',report)
    for label,result in conditions.items():
        print(label,result['gate'],'mean call',round(result['mean_call_seconds'],2))
        print('controls',result['controls'])


def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['scout','prepare','analyze'])
    args=parser.parse_args()
    if args.command=='scout':scout()
    elif args.command=='prepare':prepare()
    elif args.command=='analyze':analyze()


if __name__=='__main__':main()
