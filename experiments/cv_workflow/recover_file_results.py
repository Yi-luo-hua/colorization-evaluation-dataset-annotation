"""Offline recovery of completed actual files; preserve native failures and nulls."""
import argparse
from pathlib import Path
from compact_harness import expand
from workflow import read_json,write_json,utc,verify_sources,validate_reviews,import_reviews,export_candidate,merge_fixed_a,visual_records


def recover(batch):
    manifest=verify_sources(batch);recovered=[];incomplete=[];rows=[]
    if not visual_records(manifest) and (batch/'visual_reviews.json').exists():
        validate_reviews(manifest,read_json(batch/'visual_reviews.json'))
        result={'created_at':utc(),'new_AI_calls':0,'state':'fixed_A_complete_no_model_call_required',
                'complete_file_rows':len(manifest['records']),'incomplete_jobs':[],'batch_merged':True}
        write_json(batch/'file_recovery.json',result);return result
    children=sorted(batch.glob('parts/job_*')) if (batch/'parts').exists() else [batch]
    def resolved(payload):
        return all(r['decision']!='uncertain' and not r['uncertainties'] and not r['needs_crops'] for r in payload['reviews'])
    for child in children:
        if not list(child.glob('agy_calls/*/result.json')):
            incomplete.append({'job':child.name,'reason':'native call not finished'});continue
        m=verify_sources(child)
        try:
            payload=expand(m,read_json(child/'reviews_gemini.json'));validate_reviews(m,payload)
        except ValueError as error:
            incomplete.append({'job':child.name,'reason':str(error)});continue
        if not (child/'visual_reviews.json').exists():
            target=child/'reviews_file_recovered.json';write_json(target,payload)
            import_reviews(argparse.Namespace(batch=child,reviews=target))
            if resolved(payload):export_candidate(argparse.Namespace(batch=child))
            write_json(child/'file_recovery.json',{'created_at':utc(),'state':'actual_complete_file_recovered','new_AI_calls':0,
                       'native_result_preserved':True,'source':'reviews_gemini.json','rows':len(payload['reviews'])})
            recovered.append(child.name)
        rows.extend(payload['reviews'])
    merged=False
    rows=merge_fixed_a(manifest,rows)
    if len(rows)==len(manifest['records']) and not incomplete:
        payload={'schema_version':'visual_review_v1','reviewer':manifest['configuration']['external_reviewer'],
                 'reviews':rows,'completion_fields_source':'actual complete per-task files; native failures kept separately'}
        validate_reviews(manifest,payload);target=batch/'reviews_file_recovered.json';write_json(target,payload)
        if children!=[batch]:
            import_reviews(argparse.Namespace(batch=batch,reviews=target))
            if resolved(payload):export_candidate(argparse.Namespace(batch=batch))
        merged=True
    result={'created_at':utc(),'new_AI_calls':0,'recovered_jobs':recovered,'incomplete_jobs':incomplete,'complete_file_rows':len(rows),
            'batch_merged':merged,'timing':'offline postprocessing only; initial native timing and failures retained'}
    write_json(batch/'file_recovery.json',result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--batch',type=Path,required=True);args=p.parse_args()
    print(recover(args.batch.resolve()))
