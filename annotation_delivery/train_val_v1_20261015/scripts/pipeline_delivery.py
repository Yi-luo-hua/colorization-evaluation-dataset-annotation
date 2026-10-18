"""Serialized, idempotent exports and optional authenticated Label Studio delivery."""
import copy
from html import escape
import json
import os
import threading
from pathlib import Path
import urllib.request
from urllib.parse import quote

from prepare import write, sha
from export_pilot import NAMES, review_audit_html
from pipeline_credentials import access_token, payload
from pipeline_store import now, pid_alive


def select_rows(store, selection=None):
    """Stable range in the filtered source order, including unfinished positions."""
    selection=selection or {}
    split=selection.get('split','all');model=selection.get('model','all')
    if split not in ['all','train','val'] or model not in ['all','lcad','unicolor']:
        raise ValueError('无效的数据集或模型范围')
    start=int(selection.get('start',1));end=int(selection.get('end',2**31-1))
    if start<1 or end<start:
        raise ValueError('起始序号须至少为1，结束序号不能小于起始序号')
    rows=[r for r in store.rows() if
        (split=='all' or r['record'].get('split',r['source_sample_key'].split('/')[0])==split) and
        (model=='all' or r['record'].get('model',r['source_sample_key'].split('/')[1])==model)]
    selected=rows[start-1:end]
    eligible=sum(r['state'] in ['completed','fixed_a'] for r in selected)
    return selected,{'split':split,'model':model,'start':start,'end':min(end,len(rows)),
        'filtered_total':len(rows),'selected':len(selected),'eligible':eligible,
        'excluded':len(selected)-eligible,'first':selected[0]['source_sample_key'] if selected else None,
        'last':selected[-1]['source_sample_key'] if selected else None}


def queue_import(store, selection):
    _,preview=select_rows(store,selection)
    if not preview['eligible']:
        raise ValueError('所选范围没有已完成结果可导入')
    with store.tx() as db:
        found=db.execute("SELECT value FROM meta WHERE key='import_job'").fetchone()
        previous=json.loads(found[0]) if found else {}
        if previous.get('status') in ['queued','running'] and pid_alive(previous.get('owner_pid')):
            raise ValueError('已有导入任务正在执行，请等待完成')
        job={'status':'queued','selection':preview,'owner_pid':os.getpid(),'started_at':now()}
        store.put_meta(db,'import_job',job)
    def run():
        store.update_meta(import_job={**job,'status':'running'})
        try:
            result=sync(store,selection)
            store.update_meta(import_job={**job,'status':result['status'],'finished_at':now(),'detail':result.get('detail')})
        except Exception as exc:
            store.update_meta(import_job={**job,'status':'failed','finished_at':now(),'detail':str(exc)})
    threading.Thread(target=run,name='manual-labelstudio-import',daemon=True).start()
    return preview


def make_task(row):
    record = row['record']
    defects = row['defects']
    fixed = row['state']=='fixed_a'
    names = {'A':'缺色',**NAMES}
    cells = ['<tr>'+''.join('<td style="padding:6px;border:1px solid #ddd">'+escape(str(v))+'</td>'
        for v in [names[d['id']],d['severity'],d.get('object','全图'),d['description']])+'</tr>' for d in defects]
    data = {'source_sample_key':row['source_sample_key'],'image':'/data/local-files/?d='+quote(record['model_path'],safe='/'),
        'reference':'/data/local-files/?d='+quote(record['gt_path'],safe='/'),
        'sample_title':row['source_sample_key'],'review_info':'程序校验通过 · AI结果待人工复核' if not fixed else '冻结人工A直接结果',
        'defect_details_html':('<table style="width:100%;border-collapse:collapse"><tr><th>类别</th><th>等级</th><th>对象</th><th>描述</th></tr>'
            +''.join(cells)+'</table>') if cells else '<p>AI未列缺陷，待人工复核。</p>',
        'review_audit_html':review_audit_html(record.get('baseline') or {'defects':[]},
            {'baseline_review':row.get('baseline_review')}) if not fixed else '<p>人工A名单直接结果，不检查其他六类。</p>',
        'review_baseline':copy.deepcopy(record.get('baseline')),
        'pipeline_review':{'defects':copy.deepcopy(defects),'provenance':copy.deepcopy(row.get('provenance')),
            'category_checks':copy.deepcopy(row.get('category_checks')),'checked_categories':['A'] if fixed else list(NAMES)},
        'source_record':copy.deepcopy(record)}
    result = [{'from_name':'severity_A','to_name':'image','type':'choices','value':{'choices':['命中' if fixed else '未命中']}},
        {'from_name':'review_status','to_name':'image','type':'choices','value':{'choices':['待复核']}}]
    if not fixed:
        for category in NAMES:
            ds = [d for d in defects if d['id']==category]
            result.append({'from_name':'severity_'+category,'to_name':'image','type':'choices',
                'value':{'choices':[max((d['severity'] for d in ds),default='无此缺陷')]}})
            if ds:
                result.append({'from_name':'description_'+category,'to_name':'image','type':'textarea',
                    'value':{'text':['\n'.join(d['description'] for d in ds)]}})
    for i,r in enumerate(result):
        r['id'] = 'r'+row['source_sample_key'].replace('/','_')+'_'+str(i)
    prediction = {'model_version':row.get('provenance',{}).get('model','frozen_human_A' if fixed else 'gemini-3.8-flash-high'),
        'result':result}
    # A score is a frozen human rule. No AI confidence/quality score is fabricated.
    if fixed:
        data['fixed_A_score'] = 1.0
    return {'data':data,'predictions':[prediction]}


def interface_xml():
    cards = []
    for category,name in {'A':'冻结人工A',**NAMES}.items():
        values = ['未命中','命中'] if category=='A' else ['无此缺陷','L1','L2','L3']
        choices = ''.join('<Choice value="'+v+'"/>' for v in values)
        cards.append(f'<View className="card"><Header value="{category} · {name}" size="5"/>'
            f'<Choices name="severity_{category}" toName="image" choice="single" showInline="true">{choices}</Choices>'
            f'<TextArea name="description_{category}" toName="image" editable="true" rows="2" maxSubmissions="1"/></View>')
    return ('<View><Style>.pictures,.options{display:grid;grid-template-columns:1fr 1fr;gap:12px}.card{padding:10px;border:1px solid #ddd;border-radius:6px}'
        '.pictures .lsf-object{height:300px;display:flex;justify-content:center}</Style>'
        '<Header value="$sample_title"/><Text name="review_info" value="$review_info"/>'
        '<View className="pictures"><View><Header value="参考GT（仅辅助）" size="5"/><Image name="reference" value="$reference" maxWidth="460px" zoom="true"/></View>'
        '<View><Header value="待评价图" size="5"/><Image name="image" value="$image" maxWidth="460px" zoom="true"/></View></View>'
        '<HyperText name="defect_details" value="$defect_details_html"/><Collapse><Panel value="原B/C/D/F逐条review记录">'
        '<HyperText name="review_audit" value="$review_audit_html"/></Panel></Collapse><View className="options">'+''.join(cards)+
        '<View className="card"><Header value="人工复核" size="5"/><Choices name="review_status" toName="image" choice="single">'
        '<Choice value="待复核"/><Choice value="已核验"/></Choices><TextArea name="review_note" toName="image" editable="true" rows="2"/></View></View></View>')


def export(store):
    """Called only by executor/coordinator while holding its owner lease."""
    rows = [r for r in store.rows() if r['state'] in ['completed','fixed_a']]
    directory = store.run_dir/'exports'
    directory.mkdir(exist_ok=True)
    tasks = [make_task(r) for r in rows]
    previous = store.meta().get('export',{})
    target = directory/'tasks_stream.json'
    write(target,tasks)
    fingerprint = sha(target)
    revision = previous.get('revision',0)
    if fingerprint != previous.get('sha256'):
        revision += 1
        revisions = directory/'revisions'
        revisions.mkdir(exist_ok=True)
        old_keys = set(previous.get('keys',[]))
        delta = [t for t in tasks if t['data']['source_sample_key'] not in old_keys]
        write(revisions/f'{revision:05d}.json',delta)
        removed=old_keys-{r['source_sample_key'] for r in rows}
        if removed:
            withdrawals=directory/'withdrawals';withdrawals.mkdir(exist_ok=True)
            write(withdrawals/f'{revision:05d}.json',{'host_only':True,'removed_final_identities':sorted(removed),
                'instruction':'Excluded from final package; API delivery marks existing tasks returned and preserves historical predictions.'})
    (directory/'interface.xml').write_text(interface_xml(),encoding='utf-8')
    report = {'samples':len(rows),'sha256':fingerprint,'revision':revision,
        'keys':[r['source_sample_key'] for r in rows],'labelstudio_status':'outbox_ready',
        'human_accuracy_verified':False}
    store.update_meta(export=report)
    write(directory/'verification.json',{k:v for k,v in report.items() if k!='keys'})
    return report


def api(base, token, path, method='GET', body=None):
    request = urllib.request.Request(base.rstrip('/')+path,method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={'Authorization':('Bearer' if payload(token).get('token_type')=='access' else os.environ.get('LABEL_STUDIO_AUTH_SCHEME','Token'))+' '+token,
            'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=30) as response:
        return json.load(response)


def sync(store, selection=None):
    """Dedicated project per run; identity scan before import prevents duplicate retries."""
    delivery = store.meta().get('delivery',{})
    all_rows,preview=select_rows(store,selection)
    delivery.update(mode='manual',selection=preview)
    base = os.environ.get('LABEL_STUDIO_URL','http://127.0.0.1:8080')
    try:
        token = access_token(base)
        if not token:
            delivery.update(status='authentication_required',detail='手动导入需要Label Studio API认证；未导入，可修复认证后重试。')
            store.update_meta(delivery=delivery)
            return delivery
        delivery.update(status='syncing',detail='正在核对源身份并增量推送。')
        store.update_meta(delivery=delivery)
        project_id = delivery.get('project_id')
        title = '上色评价_恢复批次_'+store.run_dir.name
        if not project_id:
            listing = api(base,token,'/api/projects?page_size=100')
            projects = listing.get('results',[]) if isinstance(listing,dict) else listing
            project = next((p for p in projects if p['title']==title),None)
            if not project:
                project = api(base,token,'/api/projects/','POST',{'title':title,'label_config':interface_xml()})
            project_id = project['id']
            delivery['project_id'] = project_id
            store.update_meta(delivery=delivery)
        existing,page = {},1
        while True:
            result = api(base,token,f'/api/tasks?project={project_id}&page={page}&page_size=100&include=id,data')
            items = result.get('tasks',result.get('results',[])) if isinstance(result,dict) else result
            existing.update((t['data'].get('source_sample_key'),t) for t in items)
            if len(items)<100:
                break
            page += 1
        returned=0
        for row in all_rows:
            previous=existing.get(row['source_sample_key'])
            if not previous:
                continue
            task_id=previous['id']
            if row['state'] in ['completed','fixed_a']:
                task=make_task(row)
                if previous['data']!=task['data']:
                    details=api(base,token,f'/api/tasks/{task_id}/')
                    predictions=details.get('predictions',[])
                    prediction=task['predictions'][0]
                    if predictions:
                        api(base,token,f'/api/predictions/{predictions[0]["id"]}/','PATCH',prediction)
                    else:
                        api(base,token,'/api/predictions/','POST',{'task':task_id,**prediction})
                    # Data is the commit marker: retry repeats prediction update if data PATCH failed.
                    api(base,token,f'/api/tasks/{task_id}/','PATCH',{'data':task['data']})
            else:
                returned+=1
                data=copy.deepcopy(previous['data'])
                if data.get('pipeline_review',{}).get('status')!='returned':
                    data['returned_pipeline_review']=copy.deepcopy(data.get('pipeline_review'))
                data['pipeline_review']={'status':'returned','defects':None,'reason':row.get('last_feedback')}
                data.update(review_info='已打回待补正；当前旧预测仅供追溯，不能作为最终训练标签。',
                    pipeline_return={'state':row['state'],'reason':row.get('last_feedback')})
                if data!=previous['data']:
                    api(base,token,f'/api/tasks/{task_id}/','PATCH',{'data':data})
        rows = [r for r in all_rows if r['state'] in ['completed','fixed_a'] and r['source_sample_key'] not in existing]
        for offset in range(0,len(rows),100):
            api(base,token,f'/api/projects/{project_id}/import','POST',[make_task(r) for r in rows[offset:offset+100]])
            delivery.update(samples=len(existing)+min(offset+100,len(rows)),detail='已推送，正在完成本轮同步核对。')
            store.update_meta(delivery=delivery)
        delivery.update(status='synced',samples=sum(r['state'] in ['completed','fixed_a'] for r in all_rows),
            project_tasks=len(existing)+len(rows),returned_tasks=returned,
            detail=f'本次所选范围已导入 {preview["eligible"]} 条；跳过未完成 {preview["excluded"]} 条。按源身份去重。')
    except Exception as exc:
        # Delivery failure never causes another image/model annotation call.
        delivery.update(status='pending',detail=type(exc).__name__+'；推流保留待补送，不重标。')
    store.update_meta(delivery=delivery)
    return delivery
