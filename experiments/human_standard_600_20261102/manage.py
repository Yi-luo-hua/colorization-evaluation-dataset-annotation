"""Sync legacy baseline without touching human work; export finalized records."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json

from prepare import HERE, ROOT, sha, write
from labelstudio import BASE, BASELINE_VERSION, NAMES, access_token, api, interface, task


def material():
    p = HERE/'local'
    return json.loads((p/'manifest.json').read_text(encoding='utf-8')), json.loads((p/'revisions.json').read_text(encoding='utf-8'))


def details(batch, token):
    folder = HERE/f'local/batch_{batch:02d}'
    project = json.loads((folder/'project.json').read_text(encoding='utf-8'))
    listing = api(BASE, token, f'/api/tasks?project={project["id"]}&page_size=100')['tasks']
    with ThreadPoolExecutor(max_workers=5) as pool:
        rows = list(pool.map(lambda x: api(BASE,token,f'/api/tasks/{x["id"]}/'),listing))
    return project, rows


def sync():
    manifest, revisions = material()
    token = access_token(BASE)
    receipts = []
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = HERE/'local'/f'before_baseline_sync_{stamp}'
    backup.mkdir()
    for batch in range(1,7):
        project, rows = details(batch,token)
        pid = project['id']
        write(backup/f'batch_{batch:02d}.json',{'project':api(BASE,token,f'/api/projects/{pid}/'),'tasks':rows})
        api(BASE,token,f'/api/projects/{pid}/','PATCH',{'label_config':interface(),'show_collab_predictions':True,
            'enable_empty_annotation':False,
            'description':'旧工作流标注为可编辑基底；洛熙11.2新标注为只读参考。人工定稿后才作金标准。评测集不得用于工作流修改。'})
        samples = {s['source_sample_key']:s for s in manifest['samples'] if s['batch']==batch}
        assert len(rows)==100 and {x['data']['source_sample_key'] for x in rows}==set(samples)
        before_annotations = {r['id']:r['annotations'] for r in rows}
        before_drafts = {r['id']:r.get('drafts',[]) for r in rows}
        expected = {}
        for row in rows:
            sample = samples[row['data']['source_sample_key']]
            expected[row['id']] = task(sample,revisions[str(sample['review_index'])])
        def update(row):
            fresh = expected[row['id']]
            assert len(row['predictions'])==1
            if row['data']!=fresh['data']:
                api(BASE,token,f'/api/tasks/{row["id"]}/','PATCH',{'data':fresh['data']})
            prediction = row['predictions'][0]
            if any(prediction.get(k)!=fresh['predictions'][0][k] for k in ('result','model_version')):
                api(BASE,token,f'/api/predictions/{prediction["id"]}/','PATCH',fresh['predictions'][0])
            stored = api(BASE,token,f'/api/tasks/{row["id"]}/')
            assert stored['data']==fresh['data']
            assert stored['predictions'][0]['result']==fresh['predictions'][0]['result']
            assert stored['predictions'][0]['model_version']==BASELINE_VERSION
            assert stored['annotations']==before_annotations[row['id']], 'Human annotation changed unexpectedly'
            assert stored.get('drafts',[])==before_drafts[row['id']], 'Human draft changed unexpectedly'
            return stored
        with ThreadPoolExecutor(max_workers=5) as pool:
            stored = list(pool.map(update,rows))
        api(BASE,token,f'/api/projects/{pid}/','PATCH',{'model_version':BASELINE_VERSION})
        views = api(BASE,token,f'/api/dm/views?project={pid}')
        if not views:
            views = [api(BASE,token,'/api/dm/views/','POST',{'project':pid,'data':{
                'title':'按编号连续审核','type':'list','target':'tasks',
                'filters':{'conjunction':'and','items':[]}},'ordering':['tasks:id']})]
        # Existing data-manager views remain usable but no longer render huge JSON cells.
        for view in views:
            data = view['data']
            hidden = data.setdefault('hiddenColumns',{})
            raw = ['review_info','original_html','ai_reference_html','standard_html','original_defects','ai_revision','sampling','source_record','batch','role']
            hidden['explore'] = sorted(set(hidden.get('explore',[]))|{'tasks:data.'+f for f in raw})
            data['title'] = '按编号连续审核'
            api(BASE,token,f'/api/dm/views/{view["id"]}/','PATCH',{'data':data,'ordering':['tasks:id']})
        folder = HERE/f'local/batch_{batch:02d}'
        write(folder/'tasks_import.json',list(expected.values()))
        (folder/'interface.xml').write_text(interface(),encoding='utf-8')
        receipt = {'batch':batch,'project_id':pid,'url':f'http://localhost:8080/projects/{pid}/data/',
            'tasks':len(stored),'predictions':sum(len(x['predictions']) for x in stored),
            'human_annotations':sum(len(x['annotations']) for x in stored),'human_annotations_unchanged':True,
            'human_drafts':sum(len(x.get('drafts',[])) for x in stored),'human_drafts_unchanged':True,
            'editable_baseline':BASELINE_VERSION,'ai_revision_display':'read_only_reference','backup':str(backup/f'batch_{batch:02d}.json'),
            'uncertain_samples':sum(bool(x['data']['ai_revision']['uncertain_categories']) for x in stored),
            'payload_verified':True,'view_ids':[v['id'] for v in views]}
        write(folder/'final_receipt.json',receipt)
        receipts.append(receipt)
        print(json.dumps(receipt,ensure_ascii=False),flush=True)
    dev = {s['record']['gt_sha256'] for s in manifest['samples'] if s['role']=='development'}
    ev = {s['record']['gt_sha256'] for s in manifest['samples'] if s['role']=='evaluation'}
    assert not dev & ev
    assert sha(manifest['source_db'])==manifest['source_db_sha256']
    summary = {'source_db_unchanged':True,'source_group_hash_overlap':0,'unique_generated_samples':600,
        'unique_source_images':len(dev|ev),'roles':{'development':300,'evaluation':300},
        'model_split_counts':dict(Counter('/'.join(s['stratum'][1:3]) for s in manifest['samples'])),
        'original_empty':sum(not s['original_defects'] for s in manifest['samples']),
        'original_A':sum(any(d['id']=='A' for d in s['original_defects']) for s in manifest['samples']),
        'strata':manifest['strata'],'projects':receipts,
        'verification':'Source/identity/schema/import verification is separate from semantic correctness; all AI drafts await human adjudication.'}
    write(HERE/'local/verification.json',summary)


def parse_final(annotation, sample):
    results = {r['from_name']:r for r in annotation['result']}
    def choice(name):
        values = results.get(name,{}).get('value',{}).get('choices',[])
        if len(values)!=1:
            raise ValueError(f'$.result[from_name={name}].value.choices: 需要唯一选择')
        return values[0]
    status = choice('review_status')
    if status!='已定稿':
        return None
    selected = {c:choice('severity_'+c) for c in NAMES}
    if selected['A']!='命中' and '不确定' in selected.values():
        raise ValueError('$.result: 已定稿仍含“不确定”，暂不进入金标准')
    categories = ['A'] if selected['A']=='命中' else list(NAMES)[1:]
    ds = []
    for c in categories:
        level = selected[c]
        if level in ['未命中','无此缺陷']:
            continue
        text = results.get('instances_'+c,{}).get('value',{}).get('text',[])
        lines = [line.strip() for value in text for line in value.splitlines() if line.strip()]
        if not lines:
            raise ValueError(f'$.result[from_name=instances_{c}].value.text: 命中缺少对象与描述')
        items = []
        for j,line in enumerate(lines):
            parts = line.split('｜',2)
            if len(parts)!=3 or not all(parts):
                raise ValueError(f'$.result[from_name=instances_{c}].value.text[{j}]: 应为“对象｜等级｜描述”')
            obj,item_level,description = parts
            if c=='A':
                item_level = ''
            elif len(lines)==1:
                # A single instance uses the explicit button selection, so a
                # severity-only human edit needs no duplicate text edit.
                item_level = level
            elif item_level not in ['L1','L2','L3']:
                raise ValueError(f'$.result[from_name=instances_{c}].value.text[{j}]: 等级非法')
            items.append({'id':c,'severity':item_level,'object':obj,'description':description})
        if c!='A' and len(items)>1 and max(d['severity'] for d in items)!=level:
            raise ValueError(f'$.result[from_name=severity_{c}]: 按钮须等于同类多实例最高等级')
        ds.extend(items)
    return {'review_index':sample['review_index'],'source_sample_key':sample['source_sample_key'],
        'role':sample['role'],'record':sample['record'],'defects':ds,
        'category_checks':{c:{'status':('not_applicable' if selected['A']=='命中' and c!='A' else 'hit' if any(d['id']==c for d in ds) else 'clear')} for c in NAMES},
        'sampling':{k:sample[k] for k in ['stratum','weight','inclusion_probability']},
        'original_defects':sample['original_defects'],
        'human_review':{k:annotation.get(k) for k in ['id','completed_by','created_at','updated_at','lead_time']},
        'human_raw_result':annotation['result']}


def export(role):
    manifest,_ = material()
    token = access_token(BASE)
    final,issues,counts = [],[],Counter()
    selected = {s['source_sample_key']:s for s in manifest['samples'] if s['role']==role}
    for batch in ([1,2,3] if role=='development' else [4,5,6]):
        _,rows = details(batch,token)
        for row in rows:
            sample = selected[row['data']['source_sample_key']]
            submitted = [a for a in row['annotations'] if not a.get('was_cancelled')]
            if not submitted:
                counts['unsubmitted'] += 1
                continue
            if len(submitted)!=1:
                issues.append({'task_id':row['id'],'path':'$.annotations','reason':'存在多份有效人工提交，须明确裁决，不自动选择'})
                continue
            try:
                result = parse_final(submitted[0],sample)
                if result is None:
                    counts['submitted_not_final'] += 1
                else:
                    result['task_id'] = row['id']
                    final.append(result)
            except ValueError as exc:
                issues.append({'task_id':row['id'],'source_sample_key':sample['source_sample_key'],'reason':str(exc)})
    folder = HERE/('local/development' if role=='development' else 'local/sealed_evaluation')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    output = folder/f'human_gold_{stamp}.json'
    write(output,{'schema':'human_standard_600_gold_v1','role':role,
        'reference_status':'human_finalized' if final else 'no_human_finalized_samples',
        'standard_sha256':manifest['standard_sha256'],'manifest_sha256':sha(HERE/'local/manifest.json'),
        'reviews':sorted(final,key=lambda x:x['review_index']),'counts':dict(counts),'issues':issues})
    print(json.dumps({'role':role,'human_finalized':len(final),'counts':dict(counts),'issues':len(issues),'output':str(output)},ensure_ascii=False))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('sync')
    e=sub.add_parser('export')
    e.add_argument('--role',choices=['development','evaluation'],default='development')
    args=p.parse_args()
    sync() if args.command=='sync' else export(args.role)
