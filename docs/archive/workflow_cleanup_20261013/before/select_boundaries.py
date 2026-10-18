"""Choose diagnostic GT clusters without treating CV candidates as ground truth."""
import argparse
import hashlib
from pathlib import Path

import engine
from workflow import OUTPUT,read_json,write_json,utc


def prior_sources():
    seen=set()
    initial=OUTPUT.parent/'audits'/'cv_workflow_experiment_20261012_01'
    paths=list(OUTPUT.glob('*/manifest.json'))+[initial/name for name in ['synthetic_sample_manifest.json','v2_manifest.json']]
    for path in paths:
        obj=read_json(path)
        samples=obj.get('samples',[])
        # Some summary manifests store a count rather than the source list.
        for sample in samples if isinstance(samples,list) else []:
            seen.add(sample if isinstance(sample,str) else sample[0])
        if obj.get('schema_version') in ['cv_handoff_v1','cv_handoff_v2']:seen.update(r.get('source_sample_key',r['sample_key']).split('/')[-1] for r in obj['records'])
        seen.update(obj.get('prior_gt_excluded',[]))
    return seen


def choose(rows,count,seen,include_anchor=True):
    groups={}
    for row in rows:groups.setdefault(row['image_id'],{})[row['model']]=row
    groups={k:v for k,v in groups.items() if set(v)=={'lcad','unicolor'}}
    selected=[];used=set()
    def ranking(group,kind):
        rr=list(group.values())
        if kind=='a_boundary':return -min(r['metrics']['brightness_conditioned_color_ratio']+r['metrics']['chroma_ratio'] for r in rr)
        if kind=='d_local_conflict':return max((int(r['cv_flags']['d_candidate']),r['metrics']['gain_fit_residual']) for r in rr)
        if kind=='model_disagreement':
            a,b=rr;return (int(any(a['cv_flags'][k]!=b['cv_flags'][k] for k in ['a_candidate','d_candidate'])),
                          abs(a['metrics']['robust_shift_norm']-b['metrics']['robust_shift_norm'])+abs(a['metrics']['chroma_ratio']-b['metrics']['chroma_ratio']))
        if kind=='mixed_chroma':return max(min(max(0,-r['metrics']['dc_p05']),max(0,r['metrics']['dc_p95'])) for r in rr)
        if kind=='low_chroma_control':return -rr[0]['metrics']['mean_c_gt']
        return hashlib.sha256(f'20261012:real-control:{rr[0]["image_id"]}'.encode()).hexdigest()
    kinds=['a_boundary','d_local_conflict','model_disagreement','mixed_chroma','low_chroma_control','random_control']
    for kind in kinds:
        pool=[k for k in groups if k not in used and k not in seen]
        pool.sort(key=lambda k:ranking(groups[k],kind),reverse=True)
        chosen=pool[:count]
        # Explicit previously inspected anchor; never claim this source is fresh.
        if include_anchor and kind=='d_local_conflict' and '000000000785' in groups and '000000000785' not in used:
            chosen=['000000000785']+chosen[:count-1]
        if len(chosen)!=count:raise ValueError('Insufficient unique GT sources for the requested strata')
        for stem in chosen:
            used.add(stem);selected.append({'stratum':kind,'image_id':stem,'previously_seen_anchor':stem in seen,
                                          'members':list(groups[stem].values())})
    return selected


def selection(groups):
    return {'split':'val','samples':[{'model':r['model'],'task_idx':r['task_idx'],'sample_key':r['sample_key']}
                                     for g in groups for r in g['members']]}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--screen',type=Path,required=True)
    parser.add_argument('--out-dir',type=Path);parser.add_argument('--per-stratum',type=int,default=3)
    parser.add_argument('--fresh-only',action='store_true');args=parser.parse_args()
    screen=args.screen.resolve();out=args.out_dir.resolve() if args.out_dir else screen
    rows=read_json(screen/'records.json');manifest=read_json(screen/'manifest.json')
    for path,sha in manifest['source_task_sha256'].items():
        if engine.sha256(engine.ROOT/path)!=sha:raise ValueError('Task source changed since screening')
    if (out/'boundary_selection.json').exists():raise ValueError('Selection already exists')
    seen=prior_sources();selected=choose(rows,args.per_stratum,seen,include_anchor=not args.fresh_only)
    pilot=[next(g for g in selected if g['stratum']==kind) for kind in dict.fromkeys(g['stratum'] for g in selected)]
    out.mkdir(parents=True,exist_ok=True)
    write_json(out/'boundary_selection.json',selection(selected));write_json(out/'pilot_selection.json',selection(pilot))
    write_json(out/'selection_manifest.json',{'created_at':utc(),'screen_records_sha256':engine.sha256(screen/'records.json'),
               'selector_sha256':engine.sha256(Path(__file__)),'GT_clusters':selected,'pilot_GT_ids':[g['image_id'] for g in pilot],
               'purpose':'Diagnostic boundary sampling, not an unbiased accuracy/prevalence sample.',
               'sampling_parameters':{'GT_per_stratum':args.per_stratum,'strata':6,'pilot_GT_per_stratum':1,'fresh_only':args.fresh_only},
               'excluded_prior_GT_ids':sorted(seen),'screen_configuration_version':manifest['configuration']['version'],
               'parameters_fitted_to_real_labels':False,'historical_labels_used':False})
    print(f'Selected {len(selected)} GT clusters / {2*len(selected)} pairs; pilot {len(pilot)} GT / {2*len(pilot)} pairs')


if __name__=='__main__':main()
