"""Round 15: GT-disjoint physical controls and frozen-board A/E2 prompt trials."""
import argparse
import copy
import itertools
import shutil
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

import engine
import global_models as gm
import compact_harness
from select_boundaries import prior_sources
from run_harness_trial import prepare_trial
from workflow import OUTPUT,read_json,write_json,utc,prepare,render,align,verify_sources


def transformations(gt,settings):
    lab=engine.lab(gt);rng=np.random.default_rng(settings['seed']);items=[]
    def add(name,ab,a_expected,scope):
        value=lab.copy();value[...,1:]=ab
        items.append((name,gt.copy() if name=='identity' else engine.rgb(value),a_expected,scope))
    add('identity',lab[...,1:],False,'identity')
    add('grayscale',np.zeros_like(lab[...,1:]),True,'whole_color_structure_removed')
    add('single_tint',settings['single_tint_ab'],True,'whole_color_structure_removed')
    add('brightness_tint',lab[...,:1]/100*np.array(settings['single_tint_ab']),True,'whole_color_structure_removed')
    for scale in settings['fade_scales']:
        add(f'fade_{scale}',lab[...,1:]*scale,False,'color_structure_scaled')
    for fraction in settings['local_gray_fractions']:
        ab=lab[...,1:].copy();ab[:,:round(ab.shape[1]*fraction)]=0
        add(f'local_gray_{fraction}',ab,False,'partial_color_structure_retained')
    for sigma in settings['noise_sigma']:
        noise=rng.normal(0,sigma,lab[...,1:].shape)
        add(f'gray_noise_{sigma}',noise,True,'noise_without_object_colors')
        add(f'fade_noise_{sigma}',lab[...,1:]*settings['fade_scales'][0]+noise,False,'weak_color_structure_plus_noise')
    return items


def confusion(rows,params):
    result={'TP':0,'FN':0,'FP':0,'TN':0}
    for r in rows:
        metrics=r['metrics'];base_cfg=r['baseline_config']
        baseline=((metrics['mean_c_model']<=base_cfg['maximum_mean_chroma'] and metrics['chroma_ratio']<=base_cfg['maximum_chroma_ratio']) or
                  (metrics['centered_spread_model']<=base_cfg['maximum_centered_spread'] and metrics['spread_ratio']<=base_cfg['maximum_spread_ratio']))
        pred=gm.predict_a({'baseline_a':baseline,'models':metrics['global_models'],'metrics':metrics},params)
        result['TP' if pred and r['expected_A'] else 'FP' if pred else 'FN' if r['expected_A'] else 'TN']+=1
    return result


def physical(args):
    cfg=read_json(args.baseline_config or Path(__file__).with_name('config.json'));settings=read_json(args.settings)
    screen=read_json(args.screen/'records.json');screen_manifest=read_json(args.screen/'manifest.json')
    for name,sha in screen_manifest['source_task_sha256'].items():
        assert engine.sha256(engine.ROOT/name)==sha
    out=OUTPUT/args.run_id;out.mkdir();(out/'controls').mkdir()
    seen=prior_sources();unique={r['image_id']:r for r in screen if r['model']=='lcad' and r['image_id'] not in seen}
    pool=sorted(unique.values(),key=lambda r:r['metrics']['mean_c_gt']);chosen=[];used=set()
    # Neighbouring colourfulness ranks go to different GT groups, never split variants of one GT.
    for q in settings['GT_quantiles']:
        center=round(q*(len(pool)-1));candidates=sorted(range(len(pool)),key=lambda i:abs(i-center))
        for phase in ['development','confirmation']:
            index=next(i for i in candidates if pool[i]['image_id'] not in used)
            row=pool[index];used.add(row['image_id']);chosen.append({**row,'partition':phase})
    rows=[]
    for number,source in enumerate(chosen,1):
        gp=engine.ROOT/cfg['datasets']['val']/'image'/f"{source['image_id']}.jpg"
        gt=engine.read_rgb(gp)
        for name,pixels,expected,scope in transformations(gt,settings):
            path=out/'controls'/f'{number:02d}_{name}.png';Image.fromarray(pixels).save(path)
            small_gt=engine.read_rgb(gp,cfg['analysis_max_side']);small_model=align(small_gt,engine.read_rgb(path,cfg['analysis_max_side']))
            metrics,flags,_=engine.measure(engine.lab(small_gt),engine.lab(small_model),cfg)
            rows.append({'source_GT':source['image_id'],'task_idx':source['task_idx'],'partition':source['partition'],
                         'variant':name,'physical_scope':scope,'expected_A':expected,'GT_path':str(gp.relative_to(engine.ROOT)),
                         'model_path':str(path.relative_to(engine.ROOT)),'metrics':metrics,'cv_flags':flags,'baseline_config':cfg['a']})
    base=cfg['global_models']['a'];dev=[r for r in rows if r['partition']=='development'];hold=[r for r in rows if r['partition']=='confirmation']
    searched=[]
    for gain,residual in itertools.product(settings['search']['minimum_retained_gain'],settings['search']['maximum_residual']):
        params=copy.deepcopy(base);params['scale_competition'].update(minimum_retained_gain=gain,maximum_residual=residual)
        counts=confusion(dev,params);searched.append({'parameters':params,'development':counts})
    ranked=sorted(searched,key=lambda r:(r['development']['FP']+r['development']['FN'],
                    abs(r['parameters']['scale_competition']['maximum_residual']-base['scale_competition']['maximum_residual']),
                    abs(r['parameters']['scale_competition']['minimum_retained_gain']-base['scale_competition']['minimum_retained_gain'])))
    selected=ranked[0];selected['confirmation']=confusion(hold,selected['parameters'])
    per_variant={name:confusion([r for r in rows if r['variant']==name],base) for name in dict.fromkeys(r['variant'] for r in rows)}
    summary={'created_at':utc(),'pairs':len(rows),'GT_count':len(chosen),'previously_seen_GT':0,
             'development':confusion(dev,base),'confirmation':confusion(hold,base),'per_variant':per_variant,
             'selected_on_development_only':selected,'search':searched,'default_parameters_changed':False,
             'warning':'Known transformation scope diagnoses CV; weak colour plus noise and partial strips are not human semantic labels or population accuracy.'}
    write_json(out/'physical_records.json',rows);write_json(out/'physical_summary.json',summary)
    write_json(out/'experiment.json',{'created_at':utc(),'configuration':cfg,'settings':settings,'sources':chosen,
                 'source_task_sha256':screen_manifest['source_task_sha256'],'screen_sha256':engine.sha256(args.screen/'records.json'),
                 'source_code_sha256':{p.name:engine.sha256(p) for p in [Path(__file__),Path(engine.__file__),Path(gm.__file__)]},
                 'state':'physical_complete_visual_pending','model_calls':[]})
    shutil.copy2(Path(__file__),out/'ae_diagnostic_source.py');shutil.copy2(args.settings,out/'settings.json')
    print({k:summary[k] for k in ['pairs','GT_count','development','confirmation','selected_on_development_only']},flush=True)


def boards(args):
    root=OUTPUT/args.run_id;experiment=read_json(root/'experiment.json');cfg=experiment['configuration'];settings=experiment['settings']
    rows=read_json(root/'physical_records.json');screen=read_json(args.screen/'records.json');seen=prior_sources()
    control_GT={r['source_GT'] for r in rows};available=[r for r in screen if r['image_id'] not in seen|control_GT]
    selected=[];used=set()
    # Six new GT clusters, both models: darkest colour structure / severe fading / low-colour controls.
    for kind in ['a_boundary','fading','low_chroma']:
        def rank(r):
            m=r['metrics']
            if kind=='a_boundary':return m['brightness_conditioned_color_ratio']+m['chroma_ratio']
            if kind=='fading':return m['chroma_ratio'] if not r['cv_flags']['a_candidate'] else float('inf')
            return m['mean_c_gt']
        for item in sorted(available,key=rank):
            if item['image_id'] in used:continue
            used.add(item['image_id']);selected.extend({**r,'stratum':kind} for r in screen if r['image_id']==item['image_id'])
            if sum(r['stratum']==kind for r in selected)==4:break
    selection={'split':'val','samples':[{k:r[k] for k in ['model','task_idx','sample_key']} for r in selected]}
    write_json(root/'real_selection.json',selection)
    batch=OUTPUT/(args.run_id+'_baseline48');prepare(argparse.Namespace(run_id=batch.name,model='both',split='val',start=1,end=1,selection=root/'real_selection.json'),cfg)
    manifest=read_json(batch/'manifest.json');real=manifest['records'];controls=[]
    for r in rows:
        if r['partition']!='development' or r['variant'] not in settings['visual_variants']:continue
        source=next(s for s in experiment['sources'] if s['image_id']==r['source_GT'])
        pool=read_json(next((engine.ROOT/'LS_lcad_reviewer/tasks_pool/val').glob('*lcad*.json')))
        task=copy.deepcopy(pool[source['task_idx']-1]);original=copy.deepcopy(task['data']['original_record'])
        original['image_id']=original['file_path']=f"lcad/{r['source_GT']}_diagnostic_{r['variant']}.png"
        controls.append({'sample_key':'','source_sample_key':f"val/lcad/{r['source_GT']}/control/{r['variant']}",
                'task_idx':source['task_idx'],'split':'val','model':'lcad','gt_path':r['GT_path'],'model_path':r['model_path'],
                'gt_sha256':engine.sha256(engine.ROOT/r['GT_path']),'model_sha256':engine.sha256(engine.ROOT/r['model_path']),
                'original_record':original,'source_task_data':task['data'],'metrics':r['metrics'],'cv_flags':r['cv_flags'],
                'region_candidates':[],'diagnostic_control':{'variant':r['variant'],'expected_A':r['expected_A'],'GT_partition':r['partition']}})
    # Fixed anonymous shuffle avoids putting all variants of one GT together.
    records=real+controls;np.random.default_rng(settings['seed']).shuffle(records)
    for i,r in enumerate(records,1):r['sample_key']=f'S{i:03d}'
    manifest['records']=records;manifest['sheets']=render(records,batch,cfg)
    manifest['diagnostic_only']={'real_pairs':len(real),'physical_controls':len(controls),'not_formal_dataset':True}
    write_json(batch/'manifest.json',manifest)
    request=read_json(batch/'review_request.json');request['samples']=[{k:r[k] for k in ['sample_key','sheet','sheet_row']} for r in records]
    if cfg['visual_harness'].get('a_e2_cv_evidence',False):
        for sample,record in zip(request['samples'],records):sample['color_structure']=compact_harness.color_structure_evidence(record['metrics'],cfg)
    request['low_chroma_GT_candidates']=[r['sample_key'] for r in records if r['cv_flags']['gt_low_chroma_candidate']]
    write_json(batch/'review_request.json',request);write_json(batch/'review_template.json',compact_harness.template(request));verify_sources(batch)
    trial=OUTPUT/(args.run_id+'_boundary48');prepare_trial(batch,trial,'compact')
    request=read_json(trial/'review_request.json');request['visual_harness']['a_e2_boundary_rule']=settings['candidate_boundary']
    write_json(trial/'review_request.json',request)
    manifest=read_json(trial/'manifest.json');manifest['configuration']['visual_harness']['a_e2_boundary_rule']=settings['candidate_boundary'];write_json(trial/'manifest.json',manifest)
    # Prebuilt prompts are reviewable without spending a model call.
    for directory in [batch,trial]:
        (directory/'prompt_preview.txt').write_text(compact_harness.build_prompt(read_json(directory/'review_request.json'),directory/'reviews_gemini.json'),encoding='utf-8')
    experiment['visual_batches']=[str(batch),str(trial)];experiment['real_selection']=selected
    for directory in [batch,trial]:repair_control_stream_data(directory)
    write_json(root/'experiment.json',experiment);print(f'Ready: {len(records)} samples per condition, identical boards; {batch.name}, {trial.name}',flush=True)


def analyze(args):
    root=OUTPUT/args.run_id;experiment=read_json(root/'experiment.json');physical_summary=read_json(root/'physical_summary.json')
    baseline,trial=map(Path,experiment['visual_batches']);manifest=verify_sources(baseline);verify_sources(trial)
    assert [s['sha256'] for s in manifest['sheets']]==[s['sha256'] for s in read_json(trial/'manifest.json')['sheets']]
    conditions={};details=[]
    directories=[('baseline',baseline),('boundary',trial)]
    if experiment.get('evidence_batches') and all((Path(p)/'visual_reviews.json').exists() for p in experiment['evidence_batches']):
        directories+=list(zip(['evidence','confirm_boundary','confirm_evidence'],map(Path,experiment['evidence_batches'])))
    for title,directory in directories:
        local_manifest=verify_sources(directory)
        reviews={r['sample_key']:r for r in read_json(directory/'visual_reviews.json')['reviews']}
        timing=read_json(directory/'agy_calls/parallel/result.json');control_rows=[];by_variant={}
        for record in local_manifest['records']:
            review=reviews[record['sample_key']];ids={d['id'] for d in review['defects']}
            control=record.get('diagnostic_control');item={'condition':title,'sample_key':record['sample_key'],
                      'source_GT':Path(record['gt_path']).stem,'variant':control['variant'] if control else 'real',
                      'decision':review['decision'],'defects':review['defects'],'CV_A':record['cv_flags']['a_candidate']}
            if control:
                item.update(expected_A=control['expected_A'],observed_A='A' in ids,observed_E2='E2' in ids)
                control_rows.append(item);by_variant.setdefault(control['variant'],[]).append(item)
            details.append(item)
        def score(items):
            evaluated=[r for r in items if r['decision'] in ['defects','no_defects']]
            return {'total':len(items),'evaluated':len(evaluated),
                    'TP':sum(r['expected_A'] and r['observed_A'] for r in evaluated),
                    'FN':sum(r['expected_A'] and not r['observed_A'] for r in evaluated),
                    'FP':sum(not r['expected_A'] and r['observed_A'] for r in evaluated),
                    'TN':sum(not r['expected_A'] and not r['observed_A'] for r in evaluated),
                    'E2':sum(r['observed_E2'] for r in evaluated)}
        conditions[title]={'controls':score(control_rows),'by_variant':{k:score(v) for k,v in by_variant.items()},
                 'real_A':sum(r['variant']=='real' and any(d['id']=='A' for d in r['defects']) for r in details if r['condition']==title),
                 'elapsed_seconds':timing['elapsed_seconds'],'usage':timing['usage'],'calls':timing['jobs'],
                 'GT_excluded':[k for k,r in reviews.items() if r['decision']=='excluded_GT'],
                 'uncertain':[k for k,r in reviews.items() if r['decision']=='uncertain']}
    comparisons=[]
    for record in manifest['records']:
        a,b=[next(r for r in details if r['condition']==condition and r['sample_key']==record['sample_key']) for condition in ['baseline','boundary']]
        if {d['id'] for d in a['defects']}!={d['id'] for d in b['defects']} or a['decision']!=b['decision']:
            comparisons.append({'sample_key':record['sample_key'],'variant':a['variant'],'baseline':a,'boundary':b})
    summary={'physical':physical_summary,'visual_conditions':conditions,'category_scope_changes':comparisons,
             'same_boards_and_CV':True,'model':'gemini-3.8-flash-high','default_changed':False,
             'warning':'Controlled diagnostic, one stochastic pass per condition. Real-case differences are observations, not labelled accuracy.'}
    if (root/'adoption.json').exists():summary.update(default_changed=True,adoption=read_json(root/'adoption.json'))
    write_json(root/'visual_details.json',details);write_json(root/'summary.json',summary)
    experiment['state']='confirmation_visual_comparison_complete' if len(directories)==5 else 'development_visual_comparison_complete'
    experiment['analysis_source_sha256']=engine.sha256(Path(__file__));write_json(root/'experiment.json',experiment)
    print(conditions,flush=True)


def confirmation_boards(args):
    root=OUTPUT/args.run_id;experiment=read_json(root/'experiment.json');settings=experiment['settings'];cfg=experiment['configuration']
    baseline,previous=map(Path,experiment['visual_batches'])
    cv_trial=OUTPUT/(args.run_id+'_evidence48');prepare_trial(previous,cv_trial,'compact')
    def add_evidence(directory):
        manifest=read_json(directory/'manifest.json');request=read_json(directory/'review_request.json')
        manifest['configuration']['visual_harness']['a_e2_cv_evidence']=True
        request['visual_harness']['a_e2_cv_evidence']=True
        mapping={r['sample_key']:r for r in manifest['records']}
        for sample in request['samples']:sample['color_structure']=compact_harness.color_structure_evidence(mapping[sample['sample_key']]['metrics'],cfg)
        write_json(directory/'manifest.json',manifest);write_json(directory/'review_request.json',request)
        (directory/'prompt_preview.txt').write_text(compact_harness.build_prompt(request,directory/'reviews_gemini.json'),encoding='utf-8')
    add_evidence(cv_trial)
    confirmation=OUTPUT/(args.run_id+'_confirm_boundary36');prepare_trial(previous,confirmation,'compact')
    manifest=read_json(confirmation/'manifest.json');request=read_json(confirmation/'review_request.json')
    template=next(r for r in manifest['records'] if r.get('diagnostic_control'));records=[]
    pool=read_json(next((engine.ROOT/'LS_lcad_reviewer/tasks_pool/val').glob('*lcad*.json')))
    for physical_row in read_json(root/'physical_records.json'):
        if physical_row['partition']!='confirmation' or physical_row['variant'] not in settings['visual_variants']:continue
        source=next(s for s in experiment['sources'] if s['image_id']==physical_row['source_GT'])
        r=copy.deepcopy(template);task=copy.deepcopy(pool[source['task_idx']-1]);original=copy.deepcopy(task['data']['original_record'])
        original['image_id']=original['file_path']=f"lcad/{physical_row['source_GT']}_diagnostic_{physical_row['variant']}.png"
        r.update(source_sample_key=f"val/lcad/{physical_row['source_GT']}/control/{physical_row['variant']}",
                 task_idx=source['task_idx'],gt_path=physical_row['GT_path'],model_path=physical_row['model_path'],
                 gt_sha256=engine.sha256(engine.ROOT/physical_row['GT_path']),model_sha256=engine.sha256(engine.ROOT/physical_row['model_path']),
                 original_record=original,source_task_data=task['data'],metrics=physical_row['metrics'],cv_flags=physical_row['cv_flags'],
                 diagnostic_control={'variant':physical_row['variant'],'expected_A':physical_row['expected_A'],'GT_partition':'confirmation'})
        records.append(r)
    np.random.default_rng(settings['seed']+1).shuffle(records)
    for i,r in enumerate(records,1):r['sample_key']=f'S{i:03d}'
    manifest.update(records=records,sheets=render(records,confirmation,cfg),diagnostic_only={'real_pairs':0,'physical_controls':36,'not_formal_dataset':True})
    request['samples']=[{k:r[k] for k in ['sample_key','sheet','sheet_row']} for r in records];request['low_chroma_GT_candidates']=[]
    # Remove copied surplus boards from the listed manifest only; Gemini reads the six listed PNGs.
    write_json(confirmation/'manifest.json',manifest);write_json(confirmation/'review_request.json',request)
    write_json(confirmation/'review_template.json',compact_harness.template(request));verify_sources(confirmation)
    confirm_cv=OUTPUT/(args.run_id+'_confirm_evidence36');prepare_trial(confirmation,confirm_cv,'compact');add_evidence(confirm_cv)
    experiment['evidence_batches']=[str(cv_trial),str(confirmation),str(confirm_cv)]
    experiment['evidence_frozen_before_confirmation']=True;write_json(root/'experiment.json',experiment)
    shutil.copy2(Path(__file__),root/'evidence_driver_source.py')
    for directory in [cv_trial,confirmation,confirm_cv]:repair_control_stream_data(directory)
    print('Ready: development evidence48 + held-out boundary36/evidence36',flush=True)


def repair_control_stream_data(directory):
    """Only experimental control task display data; no labels or real source pools change."""
    manifest=read_json(directory/'manifest.json');changed=False
    for r in manifest['records']:
        if not r.get('diagnostic_control'):continue
        data=r['source_task_data'];data.update(image='/data/local-files/?d='+r['model_path'].replace('\\','/'),
                image_id=r['original_record']['image_id'],sample_title=r['original_record']['image_id'],
                original_record=copy.deepcopy(r['original_record']),source_info='A/E2物理诊断控制，不属于真实模型交付')
        changed=True
    if changed:write_json(directory/'manifest.json',manifest)
    stream=directory/'exports/tasks_reviewed_stream.json'
    if changed and stream.exists():
        items=read_json(stream)
        by_id={r['original_record']['image_id']:r['source_task_data'] for r in manifest['records']}
        # Synthetic task data initially carried the real source identity; match by stable export order.
        annotations=read_json(directory/'exports/reviewed_candidate.json')['annotations']
        assert len(items)==len(annotations)
        for item,annotation in zip(items,annotations):item['data']=by_id[annotation['image_id']]
        write_json(stream,items)
    for child in (directory/'parts').glob('job_*'):repair_control_stream_data(child)


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['physical','boards','analyze','confirmation_boards']);p.add_argument('--run-id',required=True)
    p.add_argument('--screen',type=Path,required=True);p.add_argument('--settings',type=Path,default=Path(__file__).with_name('ae_round15_config.json'))
    p.add_argument('--baseline-config',type=Path,help='Frozen configuration for reproducing an earlier baseline');args=p.parse_args()
    cv2.setNumThreads(1)
    {'physical':physical,'boards':boards,'analyze':analyze,'confirmation_boards':confirmation_boards}[args.stage](args)


if __name__=='__main__':main()
