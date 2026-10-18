"""Add image/UI fields to the user's trial100 stream without changing its labels."""
import copy
from html import escape
import json
from pathlib import Path
import sqlite3
from urllib.parse import quote

from prepare import PROJECT, ROOT, read, write, sha
from secondary_review import merge_sample
from export_pilot import review_audit_html, NAMES

run = PROJECT/'runtime/trial100_8sheets_20261016_01'
source = run/'exports/tasks_secondary_trial100_stream.json'
output = run/'label_studio_import_20261016'
output.mkdir()
tasks = read(source)
assert len(tasks)==100 and len({t['data']['source_sample_key'] for t in tasks})==100
records = {}
for directory in sorted((run/'packets').iterdir()):
    mapping = read(directory/'manifest_private.json')['sample_mapping']
    raw,request = read(directory/'reviews_gemini.json'),read(directory/'request.json')
    for sample,row in mapping.items():
        assert row['source_sample_key'] not in records
        records[row['source_sample_key']] = (row,raw['reviews'][sample],request['secondary_baseline'][sample])

converted, defect_count = [], 0
for index,task in enumerate(tasks,1):
    identity = task['data']['source_sample_key']
    row,delta,baseline = records[identity]
    prediction = copy.deepcopy(task['predictions'][0])
    assert len(task['predictions'])==1 and len(prediction['result'])==1
    labels = json.loads(prediction['result'][0]['value']['text'][0])
    assert labels==merge_sample(delta,baseline)
    defect_count += len(labels)
    for kind,path,expected in [('image',row['model_path'],row['model_sha256']),('reference',row['gt_path'],row['gt_sha256'])]:
        assert sha(ROOT/path)==expected
    data = copy.deepcopy(task['data'])
    data.update(image='/data/local-files/?d='+quote(row['model_path'],safe='/'),
        reference='/data/local-files/?d='+quote(row['gt_path'],safe='/'),
        sample_title=f'{index:03d} / 100 · {identity}',
        review_info='100张二次试标 · E1/E2重点重标 · B/C/D/F逐项review · AI预测待主人复核',
        source_stream_task_id=task.get('id'),source_stream_sha256=sha(source),
        review_baseline=copy.deepcopy(row['baseline']),
        nr_AI_review={'defects':labels,'baseline_review':delta},
        review_audit_html=review_audit_html(row['baseline'],{'baseline_review':delta}))
    rows = ['<tr>'+''.join('<td style="padding:6px;border:1px solid #ddd">'+escape(str(v))+'</td>'
        for v in [NAMES[d['id']],d['severity'],d['object'],d['description']])+'</tr>' for d in labels]
    data['defect_details_html'] = ('<table style="width:100%;border-collapse:collapse"><tr><th>类别</th><th>等级</th><th>对象</th><th>描述</th></tr>'
        +''.join(rows)+'</table>') if rows else '<p>本条AI结果未列缺陷，待主人复核。</p>'
    result = prediction['result']
    result += [{'from_name':'severity_A','to_name':'image','type':'choices','value':{'choices':['未命中']}},
               {'from_name':'review_status','to_name':'image','type':'choices','value':{'choices':['待复核']}}]
    for category in NAMES:
        ds = [d for d in labels if d['id']==category]
        result.append({'from_name':'severity_'+category,'to_name':'image','type':'choices',
            'value':{'choices':[max((d['severity'] for d in ds),default='无此缺陷')]}})
        if ds:
            result.append({'from_name':'description_'+category,'to_name':'image','type':'textarea',
                'value':{'text':['\n'.join(d['description'] for d in ds)]}})
    for number,item in enumerate(result):
        item['id'] = f't{index:03d}_{number:02d}'
    converted.append({'data':data,'predictions':[prediction]})

db = sqlite3.connect('file:'+str(ROOT/'LS_lcad_reviewer/data/label_studio.sqlite3')+'?mode=ro',uri=True)
xml = db.execute('select label_config from project where id=19').fetchone()[0]
db.close()
xml = xml.replace('colorized','image')
ending = '<Collapse><Panel value="原始标签JSON（保留导入包）"><TextArea name="defects" toName="image" editable="true" maxSubmissions="1" rows="8"/></Panel></Collapse>'
xml = xml.rsplit('</View>',1)[0]+ending+'</View>'
(output/'interface.xml').write_text(xml,encoding='utf-8')
write(output/'tasks_secondary_trial100_labelstudio.json',converted)
write(output/'preparation_verification.json',{'source':str(source),'source_sha256':sha(source),'tasks':100,
    'predictions':100,'defect_items':defect_count,'original_label_JSON_preserved':True,
    'raw_delta_merges_match_stream':True,'all_200_image_hashes_match':True,'human_annotations_created':0,
    'semantic_labels_changed':False,'top_level_string_ids_moved_to_data':True,
    'prediction_score_preserved_as_source_field_not_quality_rating':True,
    'output_sha256':sha(output/'tasks_secondary_trial100_labelstudio.json')})
print(f'Prepared 100 tasks / 100 predictions / {defect_count} unchanged defects; all image hashes match.')
