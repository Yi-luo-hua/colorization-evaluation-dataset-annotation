"""Round22 follow-up: retention-aware scope, positive-only visual hints.

Previous v1 outputs remain unchanged. Confirmation IDs were already inspected
in v1; this is a refinement check, not a fresh blind validation cohort.
"""
import argparse
from pathlib import Path
import numpy as np
import engine
import workflow as wf
import global_rotation_supported as rotation
from experiment_cd import SETUP,SOURCE,KINDS,GLOBAL,component,transform,counts
from run_harness_trial import prepare_trial

OUT=wf.OUTPUT/'cd_round22_supported_offline_20261013'
VISUAL=wf.OUTPUT/'cd_round22_supported_positive36_20261013'
EXTRA=['component_rotation_other_fade','rotation_fade_05','rotation_fade_55']


def extra(rgb,kind,masks):
    if kind=='component_rotation_other_fade':
        lab=engine.lab(transform(rgb,'component_rotation',masks));lab[...,1:][~masks[1]]*=.05
    else:
        lab=engine.lab(transform(rgb,'global_rotation40',masks));lab[...,1:]*=.05 if kind.endswith('05') else .55
    return engine.rgb(lab)


def offline():
    OUT.mkdir();cfg=wf.read_json(Path(__file__).with_name('config.json'));rows=[]
    sources=wf.read_json(SETUP/'selection.json')
    for i,s in enumerate(sources,1):
        gt=engine.read_rgb(engine.ROOT/s['gt_path'],cfg['analysis_max_side']);gl=engine.lab(gt);masks=component(gt)
        for kind in KINDS+EXTRA:
            gen=extra(gt,kind,masks) if kind in EXTRA else transform(gt,kind,masks)
            ml=engine.lab(gen);metrics,flags,_=engine.measure(gl,ml,cfg,generated_rgb=gen)
            rows.append({**s,'kind':kind,'physical_global_target':kind in GLOBAL or kind=='rotation_fade_55',
                         'baseline_D':flags['d_candidate'],'rotation':rotation.measure(gl,ml,cfg)})
        if i%8==0:print(f'Supported offline GT {i}/48',flush=True)
    dev=[r for r in rows if r['split']=='train'];test=[r for r in rows if r['split']=='test']
    fit=rotation.fit(dev);threshold=fit['rule']['minimum_rotation_score_degrees']
    summary={'GT':48,'variants':len(rows),'new_GT':0,'threshold_degrees':threshold,
             'development_baseline':counts(dev),'development_supplement':counts(dev,threshold),
             'confirmation_baseline':counts(test),'confirmation_supplement':counts(test,threshold),
             'by_kind':{split:{k:{'n':len(rr:=[r for r in rows if r['split']==split and r['kind']==k]),
                        'baseline':sum(r['baseline_D'] for r in rr),
                        'rotation_supported':sum(r['rotation']['score_degrees']>=threshold for r in rr),
                        'score_median':float(np.median([r['rotation']['score_degrees'] for r in rr]))} for k in KINDS+EXTRA} for split in ['train','test']},
             'support_quantile':.1,'fit_on_confirmation':False,'confirmation_previously_seen_in_v1':True,
             'limits':'Numerical intervention/signal visibility controls; not semantic C/D gold. Weak rotation is a low-evidence control, not a verified negative D label.'}
    wf.write_json(OUT/'rows.json',rows);wf.write_json(OUT/'fit.json',fit);wf.write_json(OUT/'summary.json',summary)
    for name in ['global_rotation_supported.py','global_rotation.py','experiment_cd_supported.py','check_rotation.py']:
        (OUT/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    print(summary,flush=True)


def prepare():
    trial=prepare_trial(SOURCE,VISUAL,'compact');cfg=trial['configuration']
    cfg['visual_harness'].update(d_rotation_evidence=True,d_rotation_positive_only=True,
        rotation_threshold_degrees=wf.read_json(OUT/'fit.json')['rule']['minimum_rotation_score_degrees'])
    for r in trial['records']:
        gt=engine.read_rgb(engine.ROOT/r['gt_path'],cfg['analysis_max_side'])
        gen=engine.read_rgb(engine.ROOT/r['model_path'],cfg['analysis_max_side'])
        r['metrics']['rotation_evidence']=rotation.measure(engine.lab(gt),engine.lab(gen),cfg)
    trial['experiment']['changed_surface']='GT-weighted retained-chroma rotation evidence plus positive-only hints; composite proposal, not a single-factor prompt comparison'
    trial['source_code_sha256']['global_rotation_supported.py']=engine.sha256(Path(rotation.__file__))
    wf.write_json(VISUAL/'manifest.json',trial);wf.write_handoff(VISUAL,trial)
    print(VISUAL,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['offline','prepare']);args=p.parse_args()
    {'offline':offline,'prepare':prepare}[args.command]()
