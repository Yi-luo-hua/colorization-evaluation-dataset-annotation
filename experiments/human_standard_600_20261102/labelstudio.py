"""Editable legacy baseline, read-only AI reference, separate human submissions."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from html import escape
import json
from pathlib import Path
import sys
from urllib.parse import quote
import urllib.request

from prepare import HERE, ROOT, sha, write
from descriptions import description_only
from gt_review import quality_for, STATUS_NAMES

sys.path.insert(0, str(ROOT/'annotation_delivery/train_val_v1_20261015/scripts'))
from pipeline_credentials import access_token, payload

BASE = 'http://127.0.0.1:8080'
BASELINE_VERSION = 'Legacy_workflow_baseline_v1'


def api(base, token, path, method='GET', data=None):
    headers = {'Authorization':('Bearer' if payload(token).get('token_type')=='access' else 'Token')+' '+token, 'Content-Type':'application/json'}
    request = urllib.request.Request(base+path,headers=headers,method=method,data=json.dumps(data,ensure_ascii=False).encode('utf-8') if data is not None else None)
    with urllib.request.urlopen(request,timeout=90) as response:
        raw = response.read()
        return json.loads(raw) if raw else None


NAMES = {'A':'缺色','B':'溢色','C':'语义错色','D':'偏色','E1':'过饱和','E2':'欠饱和','F':'自然度'}
RULES = {
    'A':'只有纯灰阶、完全无可辨色调才命中；微弱彩色归E2/必要时D。命中A不分级并熔断其余类别。',
    'B':'参考GT观察物体边缘的颜色跨界污染。L1轻微边缘溢出；L2明显污染邻物；L3扩散全场。',
    'C':'不参考GT定错。L1违背光照/时间/天气语境；L2多区或整体组合不协调；L3违反物体固有色常识。合理换色不罚。',
    'D':'参考GT判断语义区域或全图系统性偏色。L1单区轻微可接受；L2单区明显不可接受；L3全图统一偏色、不可信。',
    'E1':'参考GT。L1局部轻微、不影响周边；L2明显刺眼或扩大至邻区；L3全图过艳、感官极差。',
    'E2':'参考GT。L1局部轻微、不影响周边；L2明显发灰或扩大至邻区；L3全图褪色、感官极差。',
    'F':'参考GT辅助，独立观察自然真实感。L1仔细看才发现；L2一眼可见的局部不自然；L3整体不像真实照片。'}


def interface():
    cards = []
    for c,n in NAMES.items():
        values = ['未命中','命中','不确定'] if c=='A' else ['无此缺陷','L1','L2','L3','不确定']
        choices = ''.join(f'<Choice value="{v}"/>' for v in values)
        cards.append(f'''<View className="category-row"><Header value="{c} · {n}" size="5"/>
<Choices name="severity_{c}" toName="image" choice="single" showInline="true" required="true">{choices}</Choices>
<TextArea name="instances_{c}" toName="image" editable="true" transcription="true" rows="2" maxSubmissions="1" placeholder="只填写自然语言描述，不加对象、等级或类别前缀；多条描述可分行。无缺陷可留空。"/>
<Collapse><Panel value="分级标准"><Text name="guide_{c}" value="{escape(RULES[c], quote=True)}"/></Panel></Collapse></View>''')
    return '''<View><Style>
.review-layout{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr);gap:14px;align-items:start}
.review-pictures{position:sticky;top:8px}.picture-pair{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.edit-panel{max-height:78vh;overflow:auto;padding-right:10px}.category-row{border-bottom:1px solid #ddd;padding:4px 4px 8px;margin-bottom:8px}
.category-row h5{margin:3px 0}.review-banner{padding:8px;background:#eef5fa;border-radius:4px;margin-bottom:8px}
.ai-reference{max-height:30vh;overflow:auto;background:#f5f8fc;padding:8px;margin-top:8px}.ai-reference table{width:100%;border-collapse:collapse}.ai-reference td,.ai-reference th{border:1px solid #ddd;padding:4px;text-align:left}
@media(max-width:700px){.review-layout{display:block}.review-pictures{position:static}.edit-panel{max-height:none}}
</Style><Header value="$sample_title" size="4"/>
<View className="review-banner"><Text name="review_info" value="$review_info"/></View>
<View className="review-banner"><Text name="gt_quality_info" value="$gt_quality_info"/></View>
<View className="review-layout"><View className="review-pictures"><View className="picture-pair">
<View><Header value="GT · B/D/E/F参考" size="5"/><Image name="reference" value="$reference" zoom="true" maxWidth="100%"/></View>
<View><Header value="待评价生成图 · C只看本图" size="5"/><Image name="image" value="$image" zoom="true" maxWidth="100%"/></View>
</View><View className="ai-reference"><Header value="洛熙新标注 · 只读参考" size="5"/><HyperText name="ai_reference" value="$ai_reference_html"/><Text name="uncertainty" value="$uncertainty_note"/></View>
<Collapse><Panel value="旧工作流原标签（只读追溯）"><HyperText name="original" value="$original_html"/></Panel>
<Panel value="完整11.2标准"><HyperText name="standard" value="$standard_html"/></Panel></Collapse>
<Header value="右侧以旧标注为基底；修改后选择已定稿再提交，疑点请选择保留疑点。" size="6"/>
</View><View className="edit-panel"><Header value="旧工作流标注基底 · 在此修改" size="5"/>''' + ''.join(cards) + '''
<Header value="人工订正状态" size="5"/><Choices name="review_status" toName="image" choice="single-radio" showInline="true" required="true"><Choice value="待人审"/><Choice value="已定稿"/><Choice value="保留疑点"/></Choices>
<Header value="GT可用性裁决（可选，影响金标准资格）" size="5"/><Choices name="gt_review_status" toName="image" choice="single" showInline="true"><Choice value="沿用GT筛查建议"/><Choice value="GT可用"/><Choice value="GT停用"/><Choice value="GT待确认"/></Choices>
<TextArea name="review_note" toName="image" editable="true" transcription="true" rows="3" maxSubmissions="1" placeholder="改判理由或疑点（可选）"/>
</View></View></View>'''


def table(defects, empty='旧工作流未列缺陷，仍需逐类检查。'):
    if not defects:
        return '<p>'+escape(empty)+'</p>'
    return '<table><tr><th>类别</th><th>等级</th><th>对象</th><th>描述</th></tr>'+''.join('<tr>'+''.join('<td>'+escape(str(d.get(k,'')))+'</td>' for k in ['id','severity','object','description'])+'</tr>' for d in defects)+'</table>'


def task(sample, revision):
    i = sample['review_index']
    ds = sample['original_defects']
    results = []
    for cat in NAMES:
        selected = [d for d in ds if d['id']==cat]
        level = ('命中' if selected else '未命中') if cat=='A' else max((d['severity'] for d in selected), default='无此缺陷')
        results.append({'id':f'r{i}_{cat}', 'from_name':'severity_'+cat, 'to_name':'image','type':'choices','value':{'choices':[level]}})
        results.append({'id':f't{i}_{cat}', 'from_name':'instances_'+cat, 'to_name':'image','type':'textarea', 'value':{'text':['\n'.join(description_only(d['description']) for d in selected)]}})
    results.append({'id':f's{i}', 'from_name':'review_status','to_name':'image','type':'choices','value':{'choices':['待人审']}})
    results.append({'id':f'g{i}', 'from_name':'gt_review_status','to_name':'image','type':'choices','value':{'choices':['沿用GT筛查建议']}})
    gt = quality_for(sample)
    role = '校准' if sample['role']=='development' else '封存评测'
    return {'data':{'review_index':i,'batch':sample['batch'],'role':sample['role'],
        'source_sample_key':sample['source_sample_key'],
        'sample_title':f"{role} · 第{sample['batch']}批 · {i:03d}/600 · {sample['source_sample_key']}",
        'review_info':'旧工作流标注为可编辑基底；洛熙11.2新标注仅供左侧参考。描述框只保留自然语言描述；等级由该类按钮记录，多条描述可分行。',
        'gt_quality_status':gt['status'],'gt_quality':gt,
        'gt_quality_info':f"GT复筛（AI建议）：{STATUS_NAMES[gt['status']]}。{gt['reason']}"+(' GT问题未解决前暂停缺陷定稿，可在底部单独裁决GT可用性。' if gt['status']!='keep' else ''),
        'image':'/data/local-files/?d='+quote(sample['record']['model_path'],safe='/'),
        'reference':'/data/local-files/?d='+quote(sample['record']['gt_path'],safe='/'),
        'uncertainty_note':('新标注参考疑点类别：'+ '、'.join(revision['uncertain_categories'])+'。' if revision.get('uncertain_categories') else '')+(revision['uncertainty_note'] or '新标注未另列疑点，仍需人工逐类核验。'),
        'original_html':table(sample['original_defects']),
        'ai_reference_html':table(revision['defects'], '洛熙新标注暂未列缺陷；仍需人工核验。'),
        'standard_html':'<br/>'.join('<b>'+c+' '+NAMES[c]+'</b>：'+RULES[c] for c in NAMES),
        'original_defects':sample['original_defects'],'ai_revision':revision,
        'sampling':{k:sample[k] for k in ['stratum','weight','inclusion_probability']},
        'source_record':sample['record']},
        'predictions':[{'model_version':BASELINE_VERSION, 'result':results}]}


def import_batch(batch):
    manifest = json.loads((HERE/'local/manifest.json').read_text(encoding='utf-8'))
    revisions = json.loads((HERE/'local/revisions.json').read_text(encoding='utf-8'))
    samples = [s for s in manifest['samples'] if s['batch']==batch]
    assert len(samples)==100 and all(str(s['review_index']) in revisions for s in samples)
    tasks = [task(s,revisions[str(s['review_index'])]) for s in samples]
    folder = HERE/f'local/batch_{batch:02d}'
    write(folder/'tasks_import.json',tasks)
    (folder/'interface.xml').write_text(interface(),encoding='utf-8')
    token = access_token(BASE)
    project_file = folder/'project.json'
    if project_file.exists():
        project = json.loads(project_file.read_text(encoding='utf-8'))
    else:
        role = '校准集' if batch<=3 else '封存评测集'
        project = api(BASE,token,'/api/projects/','POST',{'title':f'11.2人工标准 · {role} · {batch}/6 · 100张',
            'description':'600张分层抽样；旧标注为编辑基底，新AI标注仅供参考。人工提交且已定稿后才可作金标准。评测集不得用于修改工作流。',
            'label_config':interface(),'show_collab_predictions':True,'show_skip_button':True,
            'show_annotation_history':True,'evaluate_predictions_automatically':False})
        write(project_file,{'id':project['id'],'title':project['title']})
    pid = project['id']
    response = api(BASE,token,f'/api/tasks?project={pid}&page_size=100')
    existing = response.get('tasks',response.get('results',[])) if isinstance(response,dict) else response
    keys = {t['data']['source_sample_key'] for t in existing}
    assert keys <= {s['source_sample_key'] for s in samples}
    pending = [t for t in tasks if t['data']['source_sample_key'] not in keys]
    if pending:
        write(folder/'import_response.json',api(BASE,token,f'/api/projects/{pid}/import','POST',pending))
    api(BASE,token,f'/api/projects/{pid}/','PATCH',{'model_version':BASELINE_VERSION})
    response = api(BASE,token,f'/api/tasks?project={pid}&page_size=100')
    listing = response.get('tasks',response.get('results',[])) if isinstance(response,dict) else response
    details = [api(BASE,token,f'/api/tasks/{t["id"]}/') for t in listing]
    expected = {t['data']['source_sample_key']:t for t in tasks}
    assert len(details)==100 and len({t['data']['source_sample_key'] for t in details})==100
    for t in details:
        assert t['data']==expected[t['data']['source_sample_key']]['data']
        assert len(t['predictions'])==1 and t['predictions'][0]['result']==expected[t['data']['source_sample_key']]['predictions'][0]['result']
        assert t['predictions'][0]['model_version']==BASELINE_VERSION
    headers = {'Authorization':('Bearer' if payload(token).get('token_type')=='access' else 'Token')+' '+token}
    def check_image(url):
        with urllib.request.urlopen(urllib.request.Request(BASE+url, headers=headers),timeout=30) as response:
            assert response.status==200 and response.headers.get('Content-Type','').startswith('image/')
            return {'url':url,'status':200,'bytes':len(response.read())}
    with ThreadPoolExecutor(max_workers=6) as pool:
        images = list(pool.map(check_image,sorted({t['data'][k] for t in tasks for k in ('image','reference')})))
    receipt={'batch':batch,'project_id':pid,'url':f'{BASE}/projects/{pid}/data?labeling=1',
        'tasks':len(details),'predictions':sum(len(t['predictions']) for t in details),
        'human_annotations':sum(len(t.get('annotations',[])) for t in details), 'images':images,
        'mapping':[{'task_id':t['id'],'review_index':t['data']['review_index'],'source_sample_key':t['data']['source_sample_key']} for t in details]}
    write(folder/'import_receipt.json',receipt)
    print(json.dumps({k:receipt[k] for k in ['batch','project_id','url','tasks','predictions','human_annotations']},ensure_ascii=False))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('batch',type=int)
    args=p.parse_args()
    import_batch(args.batch)
