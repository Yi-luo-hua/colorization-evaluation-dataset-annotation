"""Round22 numerical colour-scope probes; physical targets are not semantic gold."""
import argparse
import copy
from pathlib import Path
import cv2
import numpy as np

import engine
import global_rotation
import workflow as wf
from select_boundaries import prior_sources
from run_harness_trial import prepare_trial

SETUP=wf.OUTPUT/'cd_round22_setup_20261013'
SOURCE=wf.OUTPUT/'cd_round22_source36_20261013'
KINDS=['identity','exposure','chroma_fade','global_shift','global_rotation20','global_rotation40','global_white_balance',
       'local_shift','local_rotation','selective_rotation','component_rotation','component_fade']
GLOBAL={'global_shift','global_rotation20','global_rotation40','global_white_balance'}
VISUAL=['identity','global_shift','global_rotation40','component_rotation','chroma_fade','local_rotation']


def component(rgb):
    lab=engine.lab(rgb);h,w=rgb.shape[:2];ab=lab[...,1:].reshape(-1,2)
    cv2.setRNGSeed(22)
    _,labels,centres=cv2.kmeans(ab.astype(np.float32),3,None,(cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER,30,.1),1,cv2.KMEANS_PP_CENTERS)
    major=int(np.argmax(np.bincount(labels[:,0],minlength=3)));palette=(labels.reshape(h,w)==major).astype(np.uint8)
    count,connected,stats,_=cv2.connectedComponentsWithStats(palette,8)
    biggest=1+int(np.argmax(stats[1:,cv2.CC_STAT_AREA]))
    return palette.astype(bool),connected==biggest


def transform(rgb,kind,masks):
    if kind=='identity':return rgb.copy()
    if kind=='exposure':return np.rint(rgb*.75).astype(np.uint8)
    if kind=='global_white_balance':return np.clip(np.rint(rgb*np.array([1.15,.96,.80])),0,255).astype(np.uint8)
    lab=engine.lab(rgb);h,w=rgb.shape[:2];mask=np.ones((h,w),bool)
    if kind.startswith('local_'):mask[:,round(w*.75):]=False
    if kind.startswith('selective_'):mask=masks[0]
    if kind.startswith('component_'):mask=masks[1]
    if 'rotation' in kind:
        angle=20 if kind=='global_rotation20' else 40
        t=np.radians(angle);rotation=np.array([[np.cos(t),-np.sin(t)],[np.sin(t),np.cos(t)]])
        lab[...,1:][mask]=lab[...,1:][mask]@rotation.T
    elif 'shift' in kind:lab[...,1:][mask]+=np.array([8,12])
    elif 'fade' in kind:lab[...,1:][mask]*=.55
    return engine.rgb(lab)


def selection(cfg):
    registry=wf.read_json(engine.ROOT/cfg['gt_filter']['exclude_manifest']);seen=prior_sources();out=[]
    for split in ['train','test']:
        blocked={r['image_id'] for r in registry['excluded_GT'] if r['split']==split}
        pool=next((wf.BASE/'tasks_pool'/split).glob('*lcad*.json'));tasks=wf.read_json(pool)
        indexed={Path(t['data']['original_record']['image_id']).stem:i for i,t in enumerate(tasks,1)}
        eligible=sorted(set(indexed)-blocked-seen);chosen=np.random.default_rng(222013+(split=='test')).choice(eligible,24,replace=False)
        out.extend({'split':split,'image_id':stem,'task_idx':indexed[stem],'gt_path':str(Path(cfg['datasets'][split])/'image'/f'{stem}.jpg'),'pool':str(pool.relative_to(engine.ROOT))} for stem in chosen)
    return out


def counts(rows,threshold=None):
    tp=fn=fp=tn=0
    for r in rows:
        predicted=r['baseline_D'] or (threshold is not None and r['rotation']['score_degrees']>=threshold)
        target=r['physical_global_target'];tp+=int(target and predicted);fn+=int(target and not predicted);fp+=int(not target and predicted);tn+=int(not target and not predicted)
    return {'global_detected':tp,'global_missed':fn,'selective_or_scale_as_global':fp,'selective_or_scale_not_global':tn}


def offline():
    cfg=wf.read_json(Path(__file__).with_name('config.json'));sources=selection(cfg);rows=[]
    wf.write_json(SETUP/'selection.json',sources)
    wf.write_json(SETUP/'manifest.json',{'schema_version':'physical_cd_v1','samples':[s['image_id'] for s in sources],'new_GT':48,'development_GT':24,'confirmation_GT':24})
    for index,s in enumerate(sources,1):
        gt=engine.read_rgb(engine.ROOT/s['gt_path'],cfg['analysis_max_side']);gt_lab=engine.lab(gt);masks=component(gt)
        for kind in KINDS:
            gen=transform(gt,kind,masks);gen_lab=engine.lab(gen)
            metrics,flags,_=engine.measure(gt_lab,gen_lab,cfg,generated_rgb=gen)
            rotation=global_rotation.measure(gt_lab,gen_lab,cfg)
            rows.append({**s,'kind':kind,'physical_global_target':kind in GLOBAL,'baseline_D':flags['d_candidate'],
                         'baseline_broad_D':flags.get('d_broad_candidate'),'rotation':rotation,
                         'chroma_ratio':metrics['chroma_ratio'],'active_pixel_fraction':metrics['active_pixel_coverage'],
                         'group_projection_q':metrics['color_group_projection_q'],'component_fraction':float(masks[1].mean()),
                         'palette_fraction':float(masks[0].mean())})
        if index%8==0:print(f'Offline GT{index}/48',flush=True)
    dev=[r for r in rows if r['split']=='train'];confirm=[r for r in rows if r['split']=='test'];fit=global_rotation.fit(dev)
    threshold=fit['rule']['minimum_rotation_score_degrees']
    wf.write_json(SETUP/'physical_rows.json',rows);wf.write_json(SETUP/'rotation_fit.json',fit)
    summary={'development_baseline':counts(dev),'development_supplement':counts(dev,threshold),
             'confirmation_baseline':counts(confirm),'confirmation_supplement':counts(confirm,threshold),
             'threshold_degrees':threshold,'GT':48,'variants':576,'parameters_fit_on_confirmation':False,
             'limits':'Global/selective intervention scope is known, semantic D versus C is not gold. Uniform full rotation on a single coloured object can equal selective recolouring.'}
    wf.write_json(SETUP/'physical_summary.json',summary);print(summary,flush=True)


def prepare():
    cfg=wf.read_json(Path(__file__).with_name('config.json'));cfg['sheet']['show_model_name']=False
    cfg['visual_harness']['spatial_hint']=False
    rows=wf.read_json(SETUP/'physical_rows.json');threshold=wf.read_json(SETUP/'rotation_fit.json')['rule']['minimum_rotation_score_degrees']
    scored={}
    for r in rows:
        if r['split']=='test':scored.setdefault(r['image_id'],[]).append(r)
    ranking=sorted(scored,key=lambda stem:sum(r['kind'] in ['global_rotation20','global_rotation40'] and not r['baseline_D'] and r['rotation']['score_degrees']>=threshold for r in scored[stem]),reverse=True)
    selected=ranking[:6];SOURCE.mkdir();(SOURCE/'sheets').mkdir();(SOURCE/'controls').mkdir();records=[];pools={}
    for stem in selected:
        original=next(r for r in scored[stem] if r['kind']=='identity');gt_path=engine.ROOT/original['gt_path'];gt_full=engine.read_rgb(gt_path)
        masks=component(gt_full);pool=engine.ROOT/original['pool'];pools[str(pool.relative_to(engine.ROOT))]=engine.sha256(pool)
        for kind in VISUAL:
            pixels=transform(gt_full,kind,masks);target=SOURCE/'controls'/f'{stem}_{kind}.png'
            ok,png=cv2.imencode('.png',cv2.cvtColor(pixels,cv2.COLOR_RGB2BGR));assert ok;png.tofile(target)
            small=engine.resize_rgb(gt_full,cfg['analysis_max_side']);gen=engine.resize_rgb(pixels,cfg['analysis_max_side'])
            ml,gl=engine.lab(small),engine.lab(gen);metrics,flags,_=engine.measure(ml,gl,cfg,generated_rgb=pixels)
            metrics['rotation_evidence']=global_rotation.measure(ml,gl,cfg)
            side=cfg['regions']['max_side'];rg=engine.lab(engine.resize_rgb(gt_full,side));rm=engine.lab(engine.resize_rgb(pixels,side));maps=engine.difference_maps(rg,rm)
            key=f'test/control/{stem}_{kind}'
            records.append({'sample_key':key,'source_sample_key':key,'task_idx':original['task_idx'],'split':'test','model':'control',
                 'gt_path':original['gt_path'],'gt_sha256':engine.sha256(gt_path),'model_path':str(target.relative_to(engine.ROOT)),'model_sha256':engine.sha256(target),
                 'original_record':{'image_id':f'control/{stem}_{kind}.png','file_path':str(target.relative_to(engine.ROOT)),'source_dataset':'controlled_intervention','role':'control','gpt_score':None},
                 'source_task_data':{'source_kind':'controlled_intervention'},'metrics':metrics,'cv_flags':flags,'region_analysis_max_side':side,'region_candidates':engine.regions(maps,cfg),
                 'physical_intervention':{'kind':kind,'global_scope':kind in GLOBAL,'semantic_C_D_truth':None,'GT':stem}})
    order=np.random.default_rng(222014).permutation(len(records));records=[records[i] for i in order]
    for i,r in enumerate(records,1):r['sample_key']=f'S{i:03d}'
    m={'schema_version':'cv_handoff_v2','created_at':wf.utc(),'state':'awaiting_external_visual_review','configuration':cfg,
       'source_code_sha256':{name:engine.sha256(Path(__file__).with_name(name)) for name in ['experiment_cd.py','global_rotation.py','workflow.py','compact_harness.py','engine.py']},
       'source_task_sha256':pools,'records':records,'sheets':wf.render(records,SOURCE,cfg),
       'GT_quality_filter':{'exclude_manifest':cfg['gt_filter']['exclude_manifest'],'skipped_samples':[],'policy':'Only frozen-kept GT selected; no downstream qualification'},
       'experiment':{'new_visual_GT':6,'shared_with_offline_confirmation':True,'physical_controls':36,'semantic_gold':False,'selected_for_rotation_gap':True}}
    wf.write_json(SOURCE/'manifest.json',m);wf.write_handoff(SOURCE,m)
    for name,enabled in [('baseline',False),('rotation',True)]:
        out=wf.OUTPUT/f'cd_round22_{name}36_20261013';trial=prepare_trial(SOURCE,out,'compact')
        trial['configuration']['visual_harness']['d_rotation_evidence']=enabled
        trial['configuration']['visual_harness']['rotation_threshold_degrees']=threshold
        wf.write_json(out/'manifest.json',trial);wf.write_handoff(out,trial)
    wf.write_json(SETUP/'visual_protocol.json',{'state':'prepared','samples':36,'GT':6,'source':str(SOURCE),'workers':3,'sheets_per_job':2,'order':['baseline','rotation'],'threshold':threshold,'same_boards_CV':True,'only_factor':'short numerical common-hue rotation evidence','semantic_labels_not_copied':True})
    print('Prepared36 controlled outputs,6boards,2empty paired conditions.',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['offline','prepare']);args=p.parse_args()
    {'offline':offline,'prepare':prepare}[args.command]()
