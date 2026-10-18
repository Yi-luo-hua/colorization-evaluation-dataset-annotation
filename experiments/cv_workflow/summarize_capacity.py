"""Capacity diagnostics from actual files, including partial attempts and positions."""
import argparse
from pathlib import Path

from workflow import read_json,write_json,validate_reviews,utc
from compact_harness import expand


def inspect(batch):
    manifest=read_json(batch/'manifest.json');expected={r['sample_key']:r for r in manifest['records']}
    rows={};jobs=[];positions=[]
    for child in sorted(batch.glob('parts/job_*')):
        m=read_json(child/'manifest.json');keys=[r['sample_key'] for r in m['records']]
        result_files=sorted(child.glob('agy_calls/*/result.json'))
        result=read_json(result_files[-1]) if result_files else {}
        rawfile=child/'reviews_gemini.json';values={};invalid=[]
        if rawfile.exists():
            try:values=read_json(rawfile)['reviews']
            except ValueError:invalid=['partially_written_or_invalid_json']
        valid={}
        for key,value in values.items():
            if value is None:continue
            one={**m,'records':[r for r in m['records'] if r['sample_key']==key]}
            try:
                payload=expand(one,{'reviews':{key:value}});validate_reviews(one,payload)
                valid[key]=payload['reviews'][0]
            except ValueError:invalid.append(key)
        rows.update(valid)
        resolved={key:r for key,r in valid.items() if r['decision']!='uncertain' and not r['uncertainties']
                  and not r['needs_crops'] and all(d['severity'] is not None for d in r['defects'])}
        jobs.append({'job':child.name,'samples':len(keys),'sheets':len(m['sheets']),
            'valid_rows':len(valid),'resolved_rows':len(resolved),'null_keys':[k for k in keys if values.get(k) is None],
            'invalid_rows':invalid,'state':result.get('state','running_or_not_started'),
            'call_seconds':result.get('elapsed_seconds'),'usage':result.get('usage'),'error':result.get('error'),
            'native_num_turns':result.get('num_turns'),
            'read_count':None,'read_count_note':'Current CLI logs do not expose reliable per-board tool traces.'})
        for index,key in enumerate(keys):
            row=valid.get(key);control=expected[key].get('experiment_control')
            positions.append({'sample_key':key,'job':child.name,'local_index':index+1,'local_samples':len(keys),
                'third':min(2,index*3//len(keys)),'inspected_file_entry':row is not None,
                'resolved':key in resolved,'control':control,
                'categories':[d['id'] for d in row['defects']] if row else None,
                'defects':row['defects'] if row else None,
                'A_target_mismatch':(any(d['id']=='A' for d in row['defects'])!=control['expected_A']) if control and row else None})
    return manifest,rows,jobs,positions


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prefix',default='capacity_round19_balanced');args=parser.parse_args()
    from workflow import OUTPUT
    setup=OUTPUT/f'{args.prefix}_setup_20261013'
    conditions=[];baseline=None
    for capacity in [2,4,8,12,16]:
        batch=OUTPUT/f'{args.prefix}_s{capacity:02d}_96_20261013'
        if not (batch/'parts').exists():continue
        manifest,rows,jobs,positions=inspect(batch)
        if capacity==2:baseline=rows
        full=[j for j in jobs if j['samples']==capacity*6 and j['call_seconds'] is not None]
        full_seconds=sum(j['call_seconds'] for j in full)
        parallel=read_json(batch/'agy_calls/parallel/result.json') if (batch/'agy_calls/parallel/result.json').exists() else {}
        controls=[p for p in positions if p['control'] and p['inspected_file_entry']]
        thirds=[]
        for third in range(3):
            bucket=[p for p in positions if p['third']==third]
            real=[p for p in bucket if not p['control'] and p['inspected_file_entry']]
            thirds.append({'third':third,'samples':len(bucket),'file_entries':sum(p['inspected_file_entry'] for p in bucket),
                'resolved':sum(p['resolved'] for p in bucket),'A_control_mismatches':sum(p['A_target_mismatch'] is True for p in bucket),
                'real_no_defect_rows':sum(p['categories']==[] for p in real),'real_rows_seen':len(real),
                'real_defect_items':sum(len(p['defects']) for p in real)})
        comparison=[]
        if baseline is not None and capacity!=2:
            for key,row in rows.items():
                if key not in baseline or 'experiment_control' in next(r for r in manifest['records'] if r['sample_key']==key):continue
                before=set(d['id'] for d in baseline[key]['defects']);after=set(d['id'] for d in row['defects'])
                if before!=after:comparison.append({'sample_key':key,'baseline_categories':sorted(before),
                    'current_categories':sorted(after),'baseline_defects':baseline[key]['defects'],'current_defects':row['defects']})
        conditions.append({'capacity':capacity,'valid_file_rows':len(rows),'resolved_rows':sum(p['resolved'] for p in positions),
            'jobs':jobs,'batch_result':parallel,'A_positive_hits':sum(p['control']['expected_A'] and 'A' in p['categories'] for p in controls),
            'A_positive_seen':sum(p['control']['expected_A'] for p in controls),
            'A_false_positive_on_controls':sum(not p['control']['expected_A'] and 'A' in p['categories'] for p in controls),
            'fading_E2_hits':sum(p['control']['kind']=='fading' and 'E2' in p['categories'] for p in controls),
            'fading_controls_seen':sum(p['control']['kind']=='fading' for p in controls),
            'control_rows_empty':[p['sample_key'] for p in controls if p['categories']==[]],
            'A_control_mismatches':[p for p in controls if p['A_target_mismatch']],
            'full_job_native_effective_samples_per_minute':sum(j['resolved_rows'] for j in full)*60/full_seconds if full_seconds else None,
            'position_thirds':thirds,'real_category_changes_from_2_sheet':comparison,
            'all_positions':positions})
    result={'created_at':utc(),'conditions':conditions,
        'limits':['Actual compact files can contain usable partial rows even when CLI failed; they are retained for recovery.',
                  'Known A controls are diagnostic targets; fading E2 presence and real-category changes are diagnostics, not human accuracy.',
                  'Different actual concurrency and ascending condition order confound initial wall-clock comparisons; confirm selected conditions.',
                  'Reliable per-board read counts are unavailable; no claim that JSON completeness proves every image was viewed.']}
    write_json(setup/'quality_timing_details.json',result)
    print([(c['capacity'],c['resolved_rows'],c['A_positive_hits'],c['A_false_positive_on_controls']) for c in conditions])


if __name__=='__main__':main()
