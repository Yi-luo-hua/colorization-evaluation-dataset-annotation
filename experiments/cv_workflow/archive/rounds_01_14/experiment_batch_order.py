"""Matched CV8 trial: grouped-model order, adjacent GT pairs, and 12-row batches.

All model images, neutral CV values and prompt rules are frozen. No prior labels
enter the new requests. Every board still contains six full three-panel groups.
"""
import argparse
import copy
from collections import Counter
from pathlib import Path

import cv2

import engine
import compact_harness
from workflow import OUTPUT,read_json,write_json,prepare,render,verify_sources,utc
from run_harness_trial import prepare_trial


def refresh(run,manifest,request,records):
    manifest['records']=records
    manifest['sheets']=render(records,run,manifest['configuration'])
    lookup={r['sample_key']:r for r in request['samples']};samples=[]
    for r in records:
        public=copy.deepcopy(lookup[r['sample_key']]);public.update(sheet=r['sheet'],sheet_row=r['sheet_row']);samples.append(public)
    request['samples']=samples
    keys={r['sample_key'] for r in records}
    request['low_chroma_GT_candidates']=[k for k in request.get('low_chroma_GT_candidates',[]) if k in keys]
    write_json(run/'manifest.json',manifest);write_json(run/'review_request.json',request)
    write_json(run/'review_template.json',compact_harness.template(request))
    from review_boundaries import write_start_instructions
    write_start_instructions(run,manifest)


def setup():
    cv2.setNumThreads(1);out=OUTPUT/'batch_order_round10_20261013';out.mkdir()
    source=verify_sources(OUTPUT/'round9_fresh24_legacy_20261013')
    selection={'split':'val','samples':[{'model':r['model'],'task_idx':r['task_idx'],'sample_key':r['source_sample_key']} for r in source['records']]}
    write_json(out/'selection.json',selection)
    cfg=read_json(Path(__file__).with_name('config.json'))
    baseline=OUTPUT/'round10_base24_20261013'
    prepare(argparse.Namespace(model='both',split='val',start=1,end=12,selection=out/'selection.json',run_id=baseline.name),cfg)
    paired=OUTPUT/'round10_paired24_20261013';pm=prepare_trial(baseline,paired,'compact')
    groups={}
    for r in pm['records']:groups.setdefault(r['source_sample_key'].split('/')[-1],[]).append(r)
    if any({r['model'] for r in rr}!={'lcad','unicolor'} for rr in groups.values()):raise ValueError('Expected two model outputs for each GT')
    paired_records=[r for rr in groups.values() for r in sorted(rr,key=lambda r:r['model'])]
    refresh(paired,pm,read_json(paired/'review_request.json'),paired_records)
    parent=OUTPUT/'round10_split12_20261013';parent_manifest=prepare_trial(paired,parent,'compact');children=[]
    for start in [0,12]:
        child=OUTPUT/f'{parent.name}_{start//12+1}';cm=prepare_trial(paired,child,'compact')
        selected=copy.deepcopy(cm['records'][start:start+12]);refresh(child,cm,read_json(child/'review_request.json'),selected)
        children.append(child.name)
    write_json(parent/'model_batch_trial.json',{'created_at':utc(),'children':children,
        'changed_surface':'same adjacent-pair order, two sequential 12-row contexts instead of one 24-row context',
        'no_old_labels_copied':True,'not_per_sheet_workers':True})
    manifests=[verify_sources(p) for p in [baseline,paired,parent]]
    signatures=[{r['sample_key']:(r['source_sample_key'],r['gt_sha256'],r['model_sha256'],r['metrics'],r['cv_flags']) for r in m['records']} for m in manifests]
    assert signatures[0]==signatures[1]==signatures[2]
    write_json(out/'manifest.json',{'created_at':utc(),'samples':24,'GT_clusters':12,'baseline':baseline.name,
        'paired':paired.name,'split':parent.name,'children':children,
        'matched_source_pairs_and_CV_by_id':True,'same_prompt_policy':True,'prior_labels_provided':False,
        'selection_is_targeted_not_representative':True,'source_sha256':engine.sha256(Path(__file__))})
    (out/'experiment_source.py').write_bytes(Path(__file__).read_bytes())
    print(out)


def summarize():
    out=OUTPUT/'batch_order_round10_20261013';m=read_json(out/'manifest.json');runs=[OUTPUT/m[k] for k in ['baseline','paired','split']]
    manifests=[verify_sources(p) for p in runs]
    sig=lambda x:{r['sample_key']:(r['source_sample_key'],r['gt_sha256'],r['model_sha256'],r['metrics'],r['cv_flags']) for r in x['records']}
    assert sig(manifests[0])==sig(manifests[1])==sig(manifests[2])
    calls=[read_json(next(p.glob('agy_calls/*/result.json'))) for p in runs]
    reviews=[{r['sample_key']:r for r in read_json(p/'visual_reviews.json')['reviews']} for p in runs]
    scores=[]
    for p,c,rv in zip(runs,calls,reviews):
        scores.append({'run':p.name,'state':c['state'],'model':c['model'],'elapsed_seconds':c['elapsed_seconds'],
            'usage':c['usage'],'decisions':dict(Counter(r['decision'] for r in rv.values())),
            'reference_free_samples':[k for k,r in rv.items() if r.get('review_scope')=='reference_free_BF_only'],
            'A_samples':[k for k,r in rv.items() if any(d['id']=='A' for d in r['defects'])],
            'defects':dict(Counter(d['id'] for r in rv.values() for d in r['defects']))})
    result={'same_source_pairs_and_CV_by_id':True,'samples':24,'reference_is_AI_not_human':True,'runs':scores,
        'order':[ [r['sample_key'] for r in mm['records']] for mm in manifests],
        'all_reviews_by_id':{k:[rv[k] for rv in reviews] for k in reviews[0]}}
    write_json(out/'results.json',result);print(scores)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['prepare','summarize']);args=p.parse_args()
    if args.command=='prepare':setup()
    else:summarize()
