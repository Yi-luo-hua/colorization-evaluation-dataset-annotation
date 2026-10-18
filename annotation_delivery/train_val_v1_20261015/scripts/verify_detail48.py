"""Reconcile actual rerun rows and imported predictions; no semantic labeling."""
from collections import Counter
import argparse
import json
from pathlib import Path
import sqlite3
from prepare import PROJECT, ROOT, SIX, read, write, sha
from review_contract import validate_file

run = PROJECT / 'runtime/rerun48_detail_20261015_01'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--export-name',default='tasks_NR_detail_rerun48_stream.json')
args = parser.parse_args()
source = PROJECT / 'runtime/pilot_384_20261015_01'
state = read(run / 'checkpoint.json')
final = read(run / 'visual_reviews.json')
assert state['final_completed'] == len(final['reviews']) == final['completed_samples'] and state['active_calls'] == 0
count = final['completed_samples']
old = read(source / 'visual_reviews.json')
assert {r['source_sample_key'] for r in final['reviews']} <= {r['source_sample_key'] for r in old['reviews']}
assert {k for j in state['jobs'].values() for k in j['source_sample_keys']} == {r['source_sample_key'] for r in old['reviews']}
assert sha(source / 'visual_reviews.json') == read(run/'source_snapshot.json')['source_reviews_sha256']
calls = [a for j in state['jobs'].values() for a in j['attempts']]
conversations = {a['conversation_id'] for a in calls if a.get('conversation_id')}
assert len(conversations) == 1
assert any(a['resumed_conversation_id'] == next(iter(conversations)) for a in calls)
for job in state['jobs'].values():
    for call in job['attempts']:
        attempt = Path(call['path'])
        accepted, pending = validate_file(read(attempt/'reviews_gemini.json'),read(attempt/'request.json'),read(attempt/'manifest_private.json')['sample_mapping'])
        assert len(accepted) == call['accepted_samples']
        for sheet in read(attempt/'request.json')['sheets']:
            assert sha(sheet['path']) == sheet['sha256']
export = read(run/'exports'/args.export_name)
assert len(export) == count
database = sqlite3.connect('file:' + str(ROOT/'LS_lcad_reviewer/data/label_studio.sqlite3') + '?mode=ro',uri=True)
rows = database.execute('select t.id,t.data,p.result,p.model_version from task t join prediction p on p.task_id=t.id where t.project_id=18 order by t.id').fetchall()
assert len(rows) == count
expected = {t['data']['source_sample_key']:t for t in export}
task_ids = {}
for task_id,data,result,model_version in rows:
    data,result = json.loads(data),json.loads(result)
    task = expected[data['source_sample_key']]
    assert data == task['data'] and result == task['predictions'][0]['result']
    assert model_version == task['predictions'][0]['model_version']
    task_ids[data['source_sample_key']] = task_id
annotations = database.execute('select count(*) from task_completion where project_id=18').fetchone()[0]
assert annotations == 0
project_title = database.execute('select title from project where id=18').fetchone()[0]
database.close()
verification = {'samples':count,'target_samples':48,'complete':count==48,'new_unique_coverage':0,'target_source_identity_set_equal':True,
    'source_old_results_unchanged':True,'exact_original_board_bytes':True,'category_records':count*len(SIX),
    'category_checks_consistent_with_defects':True,'calls':len(calls),'conversation_ids':sorted(conversations),
    'explicit_conversation_reuse_verified':True,'predictions':count,'submitted_annotations':annotations,
    'database_payload_matches_export':True,'semantic_accuracy_verified':False,
    'before_distribution_all_48':dict(Counter(len(r['defects']) for r in old['reviews'])),
    'matched_before_distribution':dict(Counter(len(r['defects']) for r in old['reviews'] if r['source_sample_key'] in expected)),
    'matched_before_total_defects':sum(len(r['defects']) for r in old['reviews'] if r['source_sample_key'] in expected),
    'after_distribution':dict(Counter(len(r['defects']) for r in final['reviews'])),
    'total_defects':sum(len(r['defects']) for r in final['reviews']),
    'categories':dict(Counter(d['id'] for r in final['reviews'] for d in r['defects'])),
    'severities':dict(Counter(d['severity'] for r in final['reviews'] for d in r['defects']))}
write(run/'verification.json',verification)
write(run/'label_studio_project.json',{'project_id':18,'title':project_title,
    'url':'http://localhost:8080/projects/18/data?labeling=1','state':'imported_partial_predictions_provider_access_stopped' if count<48 else 'imported_predictions_waiting_human_review',
    'task_ids':task_ids,'samples':count,'target_samples':48,'prompt_revision':final['prompt_revision']})
print(json.dumps(verification,ensure_ascii=False,indent=2))
