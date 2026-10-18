"""Offline descriptive audit of actual pilot labels and local image-read evidence."""
from collections import Counter
import json
from pathlib import Path
import re
import sqlite3
from PIL import Image
from prepare import PROJECT, ROOT, read, write, sha

run = PROJECT / 'runtime/pilot_384_20261015_01'
out = run / 'quality_audit_20261015'
out.mkdir(exist_ok=True)
checkpoint = read(run / 'checkpoint.json')
export = read(run / 'exports/tasks_NR_pilot_partial_48_stream.json')
stats = {}
comparisons = []
trace = {}
for task_id, job in checkpoint['jobs'].items():
    if job['state'] != 'completed':
        continue
    attempt = Path(next(a['path'] for a in reversed(job['attempts']) if a.get('accepted_samples') == 24))
    raw = read(attempt / 'reviews_gemini.json')['reviews']
    prior = read(attempt / 'prior_reviews.json')['reviews'] if (attempt / 'prior_reviews.json').exists() else None
    mapping = read(attempt / 'manifest_private.json')['sample_mapping']
    counts = Counter(len(v) for v in raw.values())
    stats[task_id] = {'stage':job['stage'], 'samples':len(raw), 'defect_count_distribution':dict(counts),
        'categories':dict(Counter(d['id'] for v in raw.values() for d in v)),
        'severities':dict(Counter(d['severity'] for v in raw.values() for d in v)),
        'total_defects':sum(len(v) for v in raw.values()),
        'prior_total_defects':sum(len(v) for v in prior.values()) if prior else None}
    for sample, defects in raw.items():
        identity = mapping[sample]['source_sample_key']
        assert defects == job['accepted'][identity]['defects']
        if prior is not None:
            matching = [t for t in export if t['data']['source_sample_key'] == identity]
            assert len(matching) == 1 and matching[0]['data']['nr_AI_review']['defects'] == defects
            comparisons.append({'task':task_id,'sample':sample,'source_sample_key':identity,
                'prior':prior[sample], 'final':defects})
    for attempt_info in job['attempts']:
        conversation = attempt_info.get('conversation_id')
        if not conversation or conversation in trace:
            continue
        database = Path.home() / f'.gemini/antigravity-cli/conversations/{conversation}.db'
        db = sqlite3.connect('file:' + str(database) + '?mode=ro', uri=True)
        calls = []
        for idx, status, payload in db.execute('select idx,status,step_payload from steps where step_type=132 order by idx'):
            text = payload.decode('utf-8', errors='ignore')
            # Retain only tool input paths and image metadata, never model reasoning or unrelated context.
            args = re.search(r'\{"AbsolutePath":.*?\}', text)
            if not args:
                continue
            fields = json.loads(args[0])
            media = sorted(set(re.findall(r'C:/Users/[^\x00-\x1f]*?\.tempmediaStorage/[^\x00-\x1f]*?\.png', text)))
            calls.append({'step':idx, 'status':status,'path':fields['AbsolutePath'],
                'image_media':[{'path':p,'size':list(Image.open(p).size),'bytes':Path(p).stat().st_size} for p in media if Path(p).exists()]})
        db.close()
        trace[conversation] = calls

final = [v for v in stats.values() if v['stage'] == 'secondary_chroma']
summary = {'scope':'actual_48_final_and_48_initial_only_not_384',
    'final_samples':sum(v['samples'] for v in final),
    'final_count_distribution':dict(sum((Counter(v['defect_count_distribution']) for v in final),Counter())),
    'final_categories':dict(sum((Counter(v['categories']) for v in final),Counter())),
    'final_severities':dict(sum((Counter(v['severities']) for v in final),Counter())),
    'per_task':stats, 'raw_to_checkpoint_to_export_identical':True,
    'negative_rows_have_no_per_category_observation_evidence':True,
    'legacy_is_not_ground_truth':True,
    'original_stream_sha256':sha(run / 'exports/tasks_NR_pilot_partial_48_stream.json')}
database = sqlite3.connect('file:' + str(ROOT / 'LS_lcad_reviewer/data/label_studio.sqlite3') + '?mode=ro', uri=True)
imported = database.execute('select t.id,t.data,p.result from task t join prediction p on p.task_id=t.id where t.project_id=17 order by t.id').fetchall()
by_key = {t['data']['source_sample_key']:t for t in export}
assert len(imported) == len(export)
for task_id, data, result in imported:
    data, result = json.loads(data), json.loads(result)
    source = by_key[data['source_sample_key']]
    assert data == source['data'] and result == source['predictions'][0]['result']
    for row in comparisons:
        if row['source_sample_key'] == data['source_sample_key']:
            row['label_studio_task_id'] = task_id
database.close()
summary['label_studio_predictions_exactly_match_export'] = True
write(out / 'counts_and_integrity.json', summary)
write(out / 'prior_final_comparison.json', comparisons)
write(out / 'image_read_evidence.json', trace)
print(json.dumps(summary, ensure_ascii=False, indent=2))
print('Image read evidence:', json.dumps({key:[{'step':c['step'],'path':c['path'],'size':[m['size'] for m in c['image_media']]} for c in value if c['path'].endswith('.png')] for key,value in trace.items()},ensure_ascii=False,indent=2))
