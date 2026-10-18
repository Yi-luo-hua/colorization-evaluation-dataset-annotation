"""Actual-file completeness and label observations, never semantic accuracy."""
import argparse
from collections import Counter
from pathlib import Path
import workflow as wf
from compact_harness import expand
import engine

SETUP=wf.OUTPUT/'cd_round22_setup_20261013'
SOURCE=wf.OUTPUT/'cd_round22_source36_20261013'


def files(batch):
    children=sorted(batch.glob('parts/job_*')) if (batch/'parts').exists() else [batch]
    rows=[];missing=[]
    for child in children:
        path=child/'reviews_gemini.json'
        if not path.exists():missing.append({'path':str(child),'reason':'not called'});continue
        m=wf.verify_sources(child)
        try:
            payload=expand(m,wf.read_json(path));wf.validate_reviews(m,payload)
        except ValueError as error:
            missing.append({'path':str(child),'reason':str(error)});continue
        rows.extend(payload['reviews'])
    return rows,missing


def main():
    source=wf.verify_sources(SOURCE);bykey={r['sample_key']:r for r in source['records']}
    base=wf.OUTPUT/'cd_round22_baseline36_20261013';rows,missing=files(base)
    attempts=sorted(wf.OUTPUT.glob('cd_round22_baseline_retry*12*_20261013'))
    # Recovery attempts contain only the still-null final twelve rows.
    for attempt in attempts:
        recovered,failures=files(attempt)
        if recovered:
            existing={r['sample_key'] for r in rows};rows.extend(r for r in recovered if r['sample_key'] not in existing)
    conditions={'baseline':rows}
    for name,dirname in [('rotation_v1','cd_round22_rotation36_20261013'),('supported_positive_v2','cd_round22_supported_positive36_20261013')]:
        conditions[name]=files(wf.OUTPUT/dirname)[0]
    supported_attempts=sorted(wf.OUTPUT.glob('cd_round22_supported_retry*12*_20261013'))
    for attempt in supported_attempts:
        recovered,_=files(attempt);existing={r['sample_key'] for r in conditions['supported_positive_v2']}
        conditions['supported_positive_v2'].extend(r for r in recovered if r['sample_key'] not in existing)
    summaries={}
    for name,rr in conditions.items():
        kinds={}
        for kind in sorted({r['physical_intervention']['kind'] for r in source['records']}):
            subset=[r for r in rr if bykey[r['sample_key']]['physical_intervention']['kind']==kind]
            counts=Counter(d['id'] for r in subset for d in r['defects'])
            kinds[kind]={'completed':len(subset),'expected':6,'D_rows':sum(any(d['id']=='D' for d in r['defects']) for r in subset),
                         'no_defects':sum(not r['defects'] and r['decision']!='uncertain' for r in subset),'defect_counts':dict(counts)}
        summaries[name]={'complete':len(rr),'expected':36,'uncertain':sum(r['decision']=='uncertain' for r in rr),'by_kind':kinds,
            'anchor_reviews':{r['sample_key']:r['defects'] for r in rr if r['sample_key'] in ['S026','S027']}}
    calls=[]
    for batch in [base,wf.OUTPUT/'cd_round22_rotation36_20261013',wf.OUTPUT/'cd_round22_supported_positive36_20261013',*attempts,*supported_attempts]:
        for result in batch.glob('**/agy_calls/*/result.json'):
            raw=wf.read_json(result)
            if 'native_status' in raw:calls.append({'batch':batch.name,'path':str(result.relative_to(engine.ROOT)),**raw})
    result={'created_at':wf.utc(),'GT':48,'new_GT':48,'visual_GT':6,'visual_GT_in_offline_confirmation':True,'visual_unique_controls':36,
            'conditions':summaries,'native_calls':len(calls),'native_call_results':calls,
            'actual_valid_observations':sum(len(rr) for rr in conditions.values()),
            'missing_baseline_keys':sorted(set(bykey)-{r['sample_key'] for r in rows}),
            'single_board_read_count':None,'limits':'D counts are observations of numerical controls, not semantic accuracy;6 visual GT were chosen diagnostically,not an independent gold validation.'}
    common=set.intersection(*[{r['sample_key'] for r in rr} for rr in conditions.values()])
    result['paired_complete_keys']=sorted(common)
    result['paired_D_counts']={name:{kind:{'n':len(subset:=[r for r in rr if r['sample_key'] in common and bykey[r['sample_key']]['physical_intervention']['kind']==kind]),
         'D_rows':sum(any(d['id']=='D' for d in r['defects']) for r in subset)} for kind in summaries[name]['by_kind']} for name,rr in conditions.items()}
    wf.write_json(SETUP/'paired_results.json',result)
    if len(rows)==36 and not (wf.OUTPUT/'cd_round22_baseline_completed36_20261013').exists():
        from run_harness_trial import prepare_trial
        out=wf.OUTPUT/'cd_round22_baseline_completed36_20261013';m=prepare_trial(SOURCE,out,'compact')
        payload={'schema_version':'visual_review_v1','reviewer':m['configuration']['external_reviewer'],'reviews':rows}
        wf.validate_reviews(m,payload);wf.write_json(out/'reviews_merged.json',payload)
        wf.import_reviews(argparse.Namespace(batch=out,reviews=out/'reviews_merged.json'));wf.export_candidate(argparse.Namespace(batch=out))
        wf.write_json(out/'recovery_provenance.json',{'native_calls':0,'original_baseline':str(base),'attempts':[str(a) for a in attempts],
             'actual_complete_files_only':True,'original_failed_outputs_unchanged':True})
    supported=conditions['supported_positive_v2']
    if len(supported)==36 and not (wf.OUTPUT/'cd_round22_supported_completed36_20261013').exists():
        from run_harness_trial import prepare_trial
        original=wf.OUTPUT/'cd_round22_supported_positive36_20261013';out=wf.OUTPUT/'cd_round22_supported_completed36_20261013'
        m=prepare_trial(original,out,'compact');payload={'schema_version':'visual_review_v1','reviewer':m['configuration']['external_reviewer'],'reviews':supported}
        wf.validate_reviews(m,payload);wf.write_json(out/'reviews_merged.json',payload)
        wf.import_reviews(argparse.Namespace(batch=out,reviews=out/'reviews_merged.json'));wf.export_candidate(argparse.Namespace(batch=out))
        wf.write_json(out/'recovery_provenance.json',{'native_calls':0,'original':str(original),'attempts':[str(a) for a in supported_attempts],
             'actual_complete_files_only':True,'original_failed_outputs_unchanged':True})
    print({k:{'complete':v['complete'],'D_by_kind':{kind:x['D_rows'] for kind,x in v['by_kind'].items()}} for k,v in summaries.items()},flush=True)


if __name__=='__main__':main()
