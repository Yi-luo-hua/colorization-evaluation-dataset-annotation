"""Reconcile actual item-review decisions, merged labels and the designated Label Studio import."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sqlite3
from prepare import PROJECT, ROOT, read, write, sha
from review_contract import validate_file
from secondary_review import merge_sample, POLICY

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--project-id',type=int,required=True)
parser.add_argument('--export-name',required=True)
args = parser.parse_args()
run = PROJECT/'runtime/secondary_review_trial48_20261015_01'
state = read(run/'checkpoint.json')
final = read(run/'visual_reviews.json')
assert state['active_calls']==0 and state['final_completed']==len(final['reviews'])
assert final['secondary_merge_policy']==POLICY
source_hash = read(run/'source_snapshot.json')['original_reviewed_source_sha256']
assert sha(ROOT/'LS_lcad_reviewer/exports/reviewed_1_10000_clean.json')==source_hash
target = {r['source_sample_key'] for r in read(PROJECT/'runtime/pilot_384_20261015_01/visual_reviews.json')['reviews']}
assert {k for j in state['jobs'].values() for k in j['source_sample_keys']}==target
calls = [a for j in state['jobs'].values() for a in j['attempts']]
conversations = {a['conversation_id'] for a in calls if a.get('conversation_id')}
final_by_key = {r['source_sample_key']:r for r in final['reviews']}
assert len(final_by_key)==len(final['reviews'])
baseline_items = 0
for job in state['jobs'].values():
    for call in job['attempts']:
        directory = Path(call['path'])
        request = read(directory/'request.json')
        mapping = read(directory/'manifest_private.json')['sample_mapping']
        raw = read(directory/'reviews_gemini.json')
        accepted,pending = validate_file(raw,request,mapping)
        assert len(accepted)==call['accepted_samples']
        for sample,row in mapping.items():
            identity = row['source_sample_key']
            if identity in accepted and final_by_key[identity]['provenance']['call_path']==str(directory):
                assert final_by_key[identity]['defects']==merge_sample(raw['reviews'][sample],request['secondary_baseline'][sample])
                assert final_by_key[identity]['baseline_review']==raw['reviews'][sample]
                baseline_items += len(request['secondary_baseline'][sample]['other_defects'])
        for sheet in request['sheets']:
            assert sha(sheet['path'])==sheet['sha256']
export = read(run/'exports'/args.export_name)
assert len(export)==len(final_by_key)
by_key = {t['data']['source_sample_key']:t for t in export}
assert set(by_key)==set(final_by_key)
db = sqlite3.connect('file:'+str(ROOT/'LS_lcad_reviewer/data/label_studio.sqlite3')+'?mode=ro',uri=True)
rows = db.execute('select t.id,t.data,p.result from task t join prediction p on p.task_id=t.id where t.project_id=? order by t.id',(args.project_id,)).fetchall()
assert len(rows)==len(export)
ids = {}
for task_id,data,result in rows:
    data,result = json.loads(data),json.loads(result)
    task = by_key[data['source_sample_key']]
    assert data==task['data'] and result==task['predictions'][0]['result']
    ids[data['source_sample_key']]=task_id
title,xml = db.execute('select title,label_config from project where id=?',(args.project_id,)).fetchone()
annotations = db.execute('select count(*) from task_completion where project_id=?',(args.project_id,)).fetchone()[0]
assert annotations==0
db.close()
assert 'review_audit_html' in xml
(run/'interface_saved_in_label_studio.xml').write_text(xml,encoding='utf-8')
actions = Counter(d['action'] for r in final['reviews'] for d in r['baseline_review']['other_decisions'].values())
assert sum(actions.values())==baseline_items
result = {'samples':len(export),'target_samples':48,'complete':len(export)==48,'new_unique_coverage':0,
    'source_unchanged':True,'same_target48':True,'BCDF_items_reviewed':baseline_items,'BCDF_items_target':77,
    'every_original_item_has_explicit_decision':True,'review_actions':dict(actions),
    'merged_labels_reconstructed_exactly':True,'database_matches_export':True,'predictions':len(rows),
    'human_annotations':annotations,'conversation_ids':sorted(conversations),'calls':len(calls),
    'explicit_session_reuse':any(a.get('resumed_conversation_id') in conversations for a in calls),
    'final_categories':dict(Counter(d['id'] for r in final['reviews'] for d in r['defects'])),
    'semantic_accuracy_verified':False,'stop_reason':state['stop_reason']}
write(run/'verification.json',result)
write(run/'label_studio_project.json',{'project_id':args.project_id,'title':title,
    'review_url':f'http://localhost:8080/projects/{args.project_id}/data?labeling=1','task_ids':ids,
    'samples':len(rows),'target_samples':48,'prompt_revision':final['prompt_revision']})
print(json.dumps(result,ensure_ascii=False,indent=2))
