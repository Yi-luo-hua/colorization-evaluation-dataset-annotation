"""Round20 paired files: matched concurrency/capacity, then independent spatial cue."""
from collections import Counter
from pathlib import Path
import experiment_capacity_round20 as exp
from summarize_capacity import inspect
from workflow import read_json,write_json,utc


def main():
    conditions=[];baseline=None
    for name,batch in [('4',exp.wf.OUTPUT/f'{exp.PREFIX}_s04_192_20261013'),('8',exp.wf.OUTPUT/f'{exp.PREFIX}_s08_192_20261013'),('8_spatial',exp.wf.OUTPUT/'capacity_round20_spatial_s08_192_20261013')]:
        if not (batch/'parts').exists():continue
        m,rows,jobs,positions=inspect(batch)
        initial_rows=len(rows);recovery=None
        recovery_path=batch/'null_retry_recovery.json'
        if recovery_path.exists():
            recovery=read_json(recovery_path);retry=exp.wf.OUTPUT/Path(recovery['retry']).name
            rr=read_json(retry/'visual_reviews.json')['reviews'];targets={r['sample_key']:r for r in m['records']}
            rows.update({r['sample_key']:r for r in rr})
            result=read_json(next(retry.glob('agy_calls/*/result.json')))
            jobs.append({'job':'null_retry_24','samples':len(rr),'sheets':4,'valid_rows':len(rr),'resolved_rows':len(rr),
                         'state':result['state'],'call_seconds':result['elapsed_seconds'],'usage':result.get('usage'),
                         'error':result.get('error'),'read_count':None,'recovery':True})
            for index,row in enumerate(rr):
                key=row['sample_key'];control=targets[key].get('experiment_control');categories=[d['id'] for d in row['defects']]
                positions.append({'sample_key':key,'job':'null_retry_24','local_index':index+1,'local_samples':len(rr),
                                  'third':index*3//len(rr),'inspected_file_entry':True,'resolved':row['decision']!='uncertain',
                                  'control':control,'categories':categories,'defects':row['defects'],
                                  'A_target_mismatch':('A' in categories)!=control['expected_A'] if control else None,'recovery':True})
        parallel_file=batch/'agy_calls/parallel/result.json'
        timing=read_json(parallel_file) if parallel_file.exists() else {}
        controls=[p for p in positions if p['control'] and p['inspected_file_entry']]
        real={r['sample_key'] for r in m['records'] if 'experiment_control' not in r}
        changes=[]
        if baseline is not None:
            for key,row in rows.items():
                if key not in baseline or key not in real:continue
                before=baseline[key]['defects'];after=row['defects']
                if before!=after:changes.append({'sample_key':key,'baseline_defects':before,'current_defects':after,'category_changed':set(d['id'] for d in before)!=set(d['id'] for d in after)})
        condition={'name':name,'batch':str(batch),'actual_file_rows':len(rows),'initial_file_rows':initial_rows,'null_retry':recovery,'resolved_rows':sum(p['resolved'] for p in positions),'jobs':jobs,'timing':timing,
                   'A_positive_hits':sum(p['control']['expected_A'] and 'A' in p['categories'] for p in controls),
                   'A_positive_seen':sum(p['control']['expected_A'] for p in controls),
                   'colored_false_A':sum(not p['control']['expected_A'] and 'A' in p['categories'] for p in controls),
                   'A_control_mismatches':[p for p in controls if p['A_target_mismatch']],
                   'real_rows':sum(k in rows for k in real),'real_empty':sum(not rows[k]['defects'] and rows[k]['decision']=='no_defects' for k in real if k in rows),
                   'real_category_items':dict(Counter(d['id'] for k in real if k in rows for d in rows[k]['defects'])),
                   'changes_from_previous':changes,'positions':positions}
        effective_seconds=recovery['failure_inclusive_active_seconds'] if recovery else timing.get('elapsed_seconds')
        if effective_seconds:
            condition['failure_inclusive_active_seconds']=effective_seconds
            condition['resolved_samples_per_active_minute']=condition['resolved_rows']*60/effective_seconds
        conditions.append(condition)
        if name=='4':baseline=rows
        if name=='8':baseline=rows  # Spatial compares only to its matched eight-sheet baseline.
    write_json(exp.SETUP/'paired_results.json',{'created_at':utc(),'conditions':conditions,'unique_inputs':192,'fresh_GT':84,'real_samples':168,'controls':24,
        'interpretation':'Category consistency/counts are diagnostics, not accuracy. Known controls target A only. Null/error attempts and recovery costs stay visible.',
        'board_read_counts':None,'read_count_note':'CLI does not provide reliable per-board tool traces.'})
    print([(c['name'],c['resolved_rows'],c['A_positive_hits'],c['colored_false_A'],c['timing'].get('elapsed_seconds')) for c in conditions])


if __name__=='__main__':main()
