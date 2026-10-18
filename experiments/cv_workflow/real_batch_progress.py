"""Collect actual completed worker files across a real batch and its recoveries."""
import argparse
from pathlib import Path
from run_harness_trial import prepare_trial
from workflow import OUTPUT,read_json,write_json,validate_reviews,import_reviews,export_candidate,utc,fixed_a_review


def collect(batch,recoveries=()):
    batch=batch.resolve();recoveries=[x.resolve() for x in recoveries]
    manifest=read_json(batch/'manifest.json');expected={r['sample_key']:r for r in manifest['records']}
    rows={};sources={}
    for record in manifest['records']:
        if record.get('annotation_route')=='fixed_A':
            rows[record['sample_key']]=fixed_a_review(record)
            sources[record['sample_key']]=manifest['fixed_A_provenance']['manifest']
    for root in [batch,*recoveries]:
        for child in sorted((root/'parts').glob('job_*')):
            file=child/'visual_reviews.json'
            if not file.exists():continue
            child_manifest=read_json(child/'manifest.json');payload=read_json(file)
            validate_reviews(child_manifest,payload)
            for row in payload['reviews']:
                key=row['sample_key'];record=next(r for r in child_manifest['records'] if r['sample_key']==key)
                if key not in expected or record['source_sample_key']!=expected[key]['source_sample_key']:
                    raise ValueError('Recovery sample identity mismatch')
                if key in rows and rows[key]!=row:raise ValueError('Conflicting completed worker results')
                rows[key]=row;sources[key]=str(file.relative_to(OUTPUT))
    missing=[key for key in expected if key not in rows]
    return manifest,rows,missing,sources


def main():
    p=argparse.ArgumentParser();p.add_argument('--batch',type=Path,required=True)
    p.add_argument('--recoveries',type=Path,nargs='*',default=[])
    p.add_argument('--ledger',type=Path,required=True)
    p.add_argument('--prepare-recovery',help='New directory name; only completely missing boards')
    p.add_argument('--completed-run-id',help='New full delivery directory; requires complete union')
    a=p.parse_args();manifest,rows,missing,sources=collect(a.batch,a.recoveries)
    state={'updated_at':utc(),'batch':str(a.batch),'recovery_batches':[str(x) for x in a.recoveries],
           'samples':len(manifest['records']),'completed':len(rows),'pending':len(missing),
           'pending_keys':missing,'actual_file_sources':sources}
    write_json(a.ledger,state)
    if a.prepare_recovery:
        pending=set(missing);sheets=[]
        for sheet in manifest['sheets']:
            keys=set(sheet['sample_keys'])
            if keys & pending:
                if not keys<=pending:raise ValueError('Partially completed board: select missing records explicitly')
                sheets.append(sheet['path'])
        if not missing:raise ValueError('No missing samples to retry')
        prepare_trial(a.batch,OUTPUT/a.prepare_recovery,'compact',selected_sheets=sheets)
        state['prepared_recovery']=a.prepare_recovery;write_json(a.ledger,state)
    if a.completed_run_id:
        if missing:raise ValueError('Incomplete batch: do not fabricate completed labels')
        out=OUTPUT/a.completed_run_id;prepared=prepare_trial(a.batch,out,'compact')
        payload={'schema_version':'visual_review_v1','reviewer':manifest['configuration']['external_reviewer'],
                 'reviews':[rows[r['sample_key']] for r in manifest['records']],
                 'completion_fields_source':'actual complete independent worker files across recoveries'}
        validate_reviews(prepared,payload);write_json(out/'reviews_merged.json',payload)
        import_reviews(argparse.Namespace(batch=out,reviews=out/'reviews_merged.json'))
        resolved=all(r['decision']!='uncertain' and not r['uncertainties'] and not r['needs_crops'] for r in rows.values())
        if resolved:export_candidate(argparse.Namespace(batch=out))
        write_json(out/'recovery_provenance.json',state)
        (out/'START_HERE.md').write_text('# 已完成汇聚\n\n完整标签已保存，勿重新调用Gemini。来源见recovery_provenance.json。\n',encoding='utf-8')
        trial=read_json(out/'trial.json');trial['purpose']='aggregate completed real annotations, no new visual call'
        write_json(out/'trial.json',trial)
    print(f"{len(rows)}/{len(manifest['records'])} complete; {len(missing)} pending")


if __name__=='__main__':main()
