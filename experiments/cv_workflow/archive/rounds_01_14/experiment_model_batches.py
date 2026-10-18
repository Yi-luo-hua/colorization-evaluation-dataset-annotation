"""Isolate two model families in separate whole-batch calls, with frozen boards."""
import argparse
from pathlib import Path

from workflow import OUTPUT,read_json,write_json,verify_sources,utc,import_reviews,export_candidate
from run_harness_trial import prepare_trial
import compact_harness


def prepare(baseline,run_id):
    parent=OUTPUT/run_id;m=prepare_trial(baseline,parent,'compact');children=[]
    for model in ['lcad','unicolor']:
        child=OUTPUT/f'{run_id}_{model}';cm=prepare_trial(baseline,child,'compact')
        cm['records']=[r for r in cm['records'] if r['model']==model]
        paths={r['sheet'] for r in cm['records']};cm['sheets']=[s for s in cm['sheets'] if s['path'] in paths]
        # This experiment uses source boards homogeneous by model.
        if any(set(s['sample_keys'])!={r['sample_key'] for r in cm['records'] if r['sheet']==s['path']} for s in cm['sheets']):
            raise ValueError('A mixed-model sheet cannot be reused in this trial')
        write_json(child/'manifest.json',cm)
        request=read_json(child/'review_request.json');keys={r['sample_key'] for r in cm['records']}
        request['samples']=[r for r in request['samples'] if r['sample_key'] in keys];write_json(child/'review_request.json',request)
        write_json(child/'review_template.json',compact_harness.template(request))
        from review_boundaries import write_start_instructions
        write_start_instructions(child,cm)
        children.append(child.name)
    write_json(parent/'model_batch_trial.json',{'created_at':utc(),'children':children,
        'same_source_boards':True,'changed_surface':'separate model-family contexts, sequential calls',
        'no_old_labels_copied':True,'not_per_sheet_workers':True})
    print(parent)


def aggregate(parent):
    m=verify_sources(parent);trial=read_json(parent/'model_batch_trial.json');reviews={};calls=[]
    for name in trial['children']:
        child=OUTPUT/name;verify_sources(child)
        result=read_json(next(child.glob('agy_calls/*/result.json')))
        if result['state'] not in ['candidate_exported','observations_saved_with_uncertainty']:
            raise ValueError('Both child calls must complete before aggregation')
        entries=read_json(child/'reviews_gemini.json')['reviews']
        if set(entries)&set(reviews):raise ValueError('Duplicate sample in model contexts')
        reviews.update(entries);calls.append(result)
    target=parent/'reviews_aggregated.json'
    if target.exists():raise ValueError('Aggregate already exists')
    raw={'schema_version':'visual_review_compact_v1','reviews':reviews};write_json(target,raw)
    payload=compact_harness.expand(m,raw);normalized=parent/'normalized_aggregate.json';write_json(normalized,payload)
    import_reviews(argparse.Namespace(batch=parent,reviews=normalized))
    resolved=all(r['decision']!='uncertain' and not r['uncertainties'] and not r['needs_crops'] for r in payload['reviews'])
    if resolved:export_candidate(argparse.Namespace(batch=parent))
    out=parent/'agy_calls'/'aggregate';out.mkdir(parents=True)
    usage={key:sum(c['usage'].get(key,0) for c in calls) for key in calls[0]['usage']}
    write_json(out/'result.json',{'state':'candidate_exported' if resolved else 'observations_saved_with_uncertainty',
        'model':m['configuration']['external_reviewer']['model'],
        'elapsed_seconds':round(sum(c['elapsed_seconds'] for c in calls),2),'timing':'sum of sequential child call elapsed times',
        'samples':len(reviews),'sheets':len(m['sheets']),'usage':usage,'children':calls,
        'annotation_output':'aggregate of actual child files edited by Gemini; not a third model call'})
    print(out/'result.json')


def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('prepare');a.add_argument('--baseline',type=Path,required=True);a.add_argument('--run-id',required=True)
    a=sub.add_parser('aggregate');a.add_argument('--batch',type=Path,required=True);args=p.parse_args()
    if args.command=='prepare':prepare(args.baseline,args.run_id)
    else:aggregate(args.batch)


if __name__=='__main__':main()
