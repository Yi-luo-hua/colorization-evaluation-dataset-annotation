"""Read-only reconciliation of the designated pilot project with its exported predictions."""
import json
import sqlite3
from datetime import datetime, timezone
from prepare import ROOT, PROJECT, read, write

run = PROJECT / 'runtime/pilot_384_20261015_01'
db = sqlite3.connect('file:' + str(ROOT / 'LS_lcad_reviewer/data/label_studio.sqlite3') + '?mode=ro', uri=True)
tables = [row[0] for row in db.execute("select name from sqlite_master where type='table'")]
print('Relevant tables:', [t for t in tables if any(part in t for part in ['task', 'prediction', 'annotation'])])
for name in ['task', 'prediction', 'annotation']:
    if name in tables:
        print(name, [row[1] for row in db.execute(f'pragma table_info({name})')])
project = db.execute('select title from project where id=17').fetchone()[0]
tasks = db.execute('select id,data from task where project_id=17 order by id').fetchall()
export = read(run / 'exports/tasks_NR_pilot_partial_48_stream.json')
assert len(tasks) == len(export) == 48
assert [json.loads(row[1]) for row in tasks] == [task['data'] for task in export]
predictions = db.execute('select task_id,result from prediction where project_id=17 order by task_id').fetchall()
assert len(predictions) == 48
assert [json.loads(row[1]) for row in predictions] == [task['predictions'][0]['result'] for task in export]
annotations = db.execute('select count(*) from task_completion where project_id=17').fetchone()[0]
assert annotations == 0
checkpoint = read(run / 'checkpoint.json')
assert checkpoint['active_calls'] == 0
write(run / 'label_studio_project.json', {
    'project_id': 17, 'title': project, 'url': 'http://localhost:8080/projects/17/data',
    'review_url': 'http://localhost:8080/projects/17/data?labeling=1',
    'example_url': 'http://localhost:8080/projects/17/data?tab=12&task=44233',
    'state': 'partial_imported_quota_stopped', 'target':384, 'completed_final':48,
    'initial_only':48, 'remaining_final':336,
    'tasks':48, 'predictions':48, 'human_annotations':annotations,
    'database_payload_matches_export':True,
    'ui_verified':['reference_and_generated_images','empty_defects','E2_L2_and_plain_description','continuous_labeling_entry'],
    'semantic_accuracy_verified':False, 'verified_at':datetime.now(timezone.utc).isoformat(),
    'task_ids':[row[0] for row in tasks]
})
print('Verified project 17: 48 exact tasks, 48 exact predictions, 0 submitted annotations; active calls 0')
