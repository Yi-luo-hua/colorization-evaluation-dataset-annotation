"""Sync legacy baseline without touching human work; export finalized records."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json

from prepare import HERE, ROOT, sha, write
from labelstudio import BASE, BASELINE_VERSION, NAMES, access_token, api, interface, task
from descriptions import clean_result, description_only
from gt_review import quality_for, effective_quality, RUN as GT_RUN


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


def is_final(annotation):
    return not annotation.get('was_cancelled') and any(
        r['from_name']=='review_status' and r.get('value',{}).get('choices')==['已定稿']
        for r in annotation['result'])


def sync_views(pid, token):
    views = api(BASE,token,f'/api/dm/views?project={pid}')
    quality = {'filter':'filter:tasks:data.gt_quality_status','operator':'equal','type':'String','value':'keep'}
    submitted = {'filter':'filter:tasks:total_annotations','operator':'greater','type':'Number','value':0}
    hidden = {'explore':['tasks:data.'+f for f in ['review_info','original_html','ai_reference_html','standard_html',
        'original_defects','ai_revision','sampling','source_record','batch','role','gt_quality']]}
    hidden['labeling'] = hidden['explore'].copy()
    system_columns = ['annotations_ids','annotations_results','avg_lead_time','created_at','draft_exists',
        'file_upload','inner_id','predictions_model_versions','predictions_results','predictions_score',
        'storage_filename','updated_at','updated_by']
    hidden['explore'] += ['tasks:'+f for f in system_columns]
    hidden['labeling'] += ['tasks:'+f for f in system_columns+['id','completed_at','cancelled_annotations',
        'total_predictions','annotators']]
    hidden['labeling'] += ['tasks:data.'+f for f in ['review_info','gt_quality_info','uncertainty_note',
        'source_sample_key','reference','review_index','gt_quality_status']]
    configs = [
        ('GT可用及已提交 · 连续审核',{'conjunction':'or','items':[quality,submitted]}),
        ('GT需处理 · 停用与待确认',{'conjunction':'and','items':[{**quality,'operator':'not_equal'}]}),
        ('全部样本 · 保留追溯',{'conjunction':'and','items':[]}),
        ('已提交 · 保留人审结果',{'conjunction':'and','items':[submitted]})]
    for index,(title,filters) in enumerate(configs):
        matching = min(views,key=lambda v:v['id']) if index==0 and views else next(
            (v for v in views if v['data'].get('title')==title),None)
        data = {**(matching['data'] if matching else {}),'title':title,'type':'list','target':'tasks',
            'filters':filters,'hiddenColumns':hidden}
        if matching:
            api(BASE,token,f'/api/dm/views/{matching["id"]}/','PATCH',{'data':data,'ordering':['tasks:id']})
        else:
            views.append(api(BASE,token,'/api/dm/views/','POST',{'project':pid,'data':data,'ordering':['tasks:id']}))
    return api(BASE,token,f'/api/dm/views?project={pid}')


def preserve_finalized():
    """Read-only snapshot of all human work; update navigation views only."""
    token = access_token(BASE)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    folder = HERE/'local'/f'human_preserved_{stamp}'
    folder.mkdir()
    receipts = []
    for batch in range(1,7):
        project,rows = details(batch,token)
        pid = project['id']
        path = folder/f'batch_{batch:02d}.json'
        write(path,{'project_id':pid,'captured_at':datetime.now(timezone.utc).isoformat(),
            'tasks':rows,'views_before':api(BASE,token,f'/api/dm/views?project={pid}')})
        finals = [{'task_id':r['id'],'review_index':r['data']['review_index'],
            'source_sample_key':r['data']['source_sample_key'],'gt_quality':r['data'].get('gt_quality'),
            'annotation':a} for r in rows for a in r['annotations'] if is_final(a)]
        write(folder/f'finalized_{batch:02d}.json',finals)
        views = sync_views(pid,token)
        receipt = {'batch':batch,'project_id':pid,'finalized':len(finals),
            'annotations':sum(len(r['annotations']) for r in rows),
            'drafts':sum(len(r.get('drafts',[])) for r in rows),
            'snapshot':str(path),'sha256':sha(path),'human_endpoint_writes':0,
            'views':[{'id':v['id'],'title':v['data']['title']} for v in views]}
        receipts.append(receipt)
        print(json.dumps(receipt,ensure_ascii=False),flush=True)
    write(folder/'receipt.json',{'captured_at':stamp,'finalized':sum(r['finalized'] for r in receipts),
        'human_endpoint_writes':0,'projects':receipts})
    print(str(folder),flush=True)


def sync(clean_human=False):
    manifest, revisions = material()
    token = access_token(BASE)
    receipts = []
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = HERE/'local'/f'before_baseline_sync_{stamp}'
    backup.mkdir()
    for batch in range(1,7):
        project, rows = details(batch,token)
        pid = project['id']
        write(backup/f'batch_{batch:02d}.json',{'project':api(BASE,token,f'/api/projects/{pid}/'),'tasks':rows,
            'views':api(BASE,token,f'/api/dm/views?project={pid}')})
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
            changed = {'annotations':0,'drafts':0}
            restored_drafts = {}
            clean_row = clean_human and not any(is_final(a) for a in row['annotations'])
            if clean_row:
                for item in row['annotations']:
                    cleaned = clean_result(item['result'])
                    if cleaned!=item['result']:
                        api(BASE,token,f'/api/annotations/{item["id"]}/','PATCH',{'result':cleaned})
                        changed['annotations'] += 1
                # Label Studio deletes associated drafts when an annotation is
                # saved. Restore their content through its native draft API.
                remaining = {d['id'] for d in api(BASE,token,f'/api/tasks/{row["id"]}/').get('drafts',[])}
                for item in row.get('drafts',[]):
                    cleaned = clean_result(item['result'])
                    if item['id'] not in remaining:
                        path = f'/api/tasks/{row["id"]}/'+(f'annotations/{item["annotation"]}/' if item.get('annotation') else '')+'drafts'
                        data = {k:item[k] for k in ('lead_time','was_postponed')}
                        data.update(result=cleaned,import_id=item['id'])
                        new = api(BASE,token,path,'POST',data)
                        restored_drafts[item['id']] = new['id']
                    elif cleaned!=item['result']:
                        api(BASE,token,f'/api/drafts/{item["id"]}/','PATCH',{'result':cleaned})
                    if cleaned!=item['result']:
                        changed['drafts'] += 1
            stored = api(BASE,token,f'/api/tasks/{row["id"]}/')
            assert stored['data']==fresh['data']
            assert stored['predictions'][0]['result']==fresh['predictions'][0]['result']
            assert stored['predictions'][0]['model_version']==BASELINE_VERSION
            human_before = [('annotations',before_annotations[row['id']]),('drafts',before_drafts[row['id']])]
            for field, before in human_before if clean_human else []:
                actual = {item['id']:item for item in stored.get(field,[])}
                mapped_id = lambda item: restored_drafts.get(item['id'],item['id']) if field=='drafts' else item['id']
                assert set(actual)=={mapped_id(item) for item in before}
                for item in before:
                    saved = actual[mapped_id(item)]
                    expected_result = clean_result(item['result']) if clean_row else item['result']
                    assert saved['result']==expected_result
                    for key in ('completed_by','user','was_cancelled','created_at','lead_time','annotation'):
                        if key=='created_at' and field=='drafts' and item['id'] in restored_drafts:
                            continue
                        assert saved.get(key)==item.get(key), (field,item['id'],key)
            stored['_format_cleaned'] = changed
            stored['_restored_drafts'] = restored_drafts
            # A normal sync never writes human endpoints. The user can keep
            # labeling while it runs; record new human progress, never reset it.
            stored['_human_progress'] = any({x['id']:x['result'] for x in before}!=
                {x['id']:x['result'] for x in stored.get(field,[])} for field,before in human_before)
            return stored
        with ThreadPoolExecutor(max_workers=5) as pool:
            stored = list(pool.map(update,rows))
        api(BASE,token,f'/api/projects/{pid}/','PATCH',{'model_version':BASELINE_VERSION})
        views = sync_views(pid,token)
        folder = HERE/f'local/batch_{batch:02d}'
        write(folder/'tasks_import.json',list(expected.values()))
        (folder/'interface.xml').write_text(interface(),encoding='utf-8')
        receipt = {'batch':batch,'project_id':pid,'url':f'http://localhost:8080/projects/{pid}/data/',
            'tasks':len(stored),'predictions':sum(len(x['predictions']) for x in stored),
            'human_annotations':sum(len(x['annotations']) for x in stored),'human_decisions_preserved':True,
            'human_drafts':sum(len(x.get('drafts',[])) for x in stored),
            'format_cleaned':{f:sum(x['_format_cleaned'][f] for x in stored) for f in ('annotations','drafts')},
            'restored_draft_ids':{str(x['id']):x['_restored_drafts'] for x in stored if x['_restored_drafts']},
            'description_format':'plain_natural_language',
            'gt_quality_counts':dict(Counter(x['data']['gt_quality_status'] for x in stored)),
            'human_progress_observed_task_ids':[x['id'] for x in stored if x['_human_progress']],
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
    gt = effective_quality(annotation,sample)
    if gt['status']!='keep':
        raise ValueError(f'$.gt_quality: GT仍为{gt["status"]}，须先裁决GT可用性，不进入金标准')
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
        # The UI records one severity per category. Preserve every description,
        # without inventing object names or unrecorded per-instance severities.
        ds.append({'id':c,'severity':'' if c=='A' else level,'object':'',
            'description':'\n'.join(description_only(line) for line in lines)})
    return {'review_index':sample['review_index'],'source_sample_key':sample['source_sample_key'],
        'role':sample['role'],'record':sample['record'],'defects':ds,
        'defect_granularity':'category','description_format':'plain_natural_language',
        'gt_quality':gt,
        'category_checks':{c:{'status':('not_applicable' if selected['A']=='命中' and c!='A' else 'hit' if any(d['id']==c for d in ds) else 'clear')} for c in NAMES},
        'sampling':{k:sample[k] for k in ['stratum','weight','inclusion_probability']},
        'original_defects':sample['original_defects'],
        'human_review':{k:annotation.get(k) for k in ['id','completed_by','created_at','updated_at','lead_time']},
        'human_raw_result':annotation['result']}


def export(role):
    manifest,_ = material()
    token = access_token(BASE)
    final,preserved,issues,counts = [],[],[],Counter()
    selected = {s['source_sample_key']:s for s in manifest['samples'] if s['role']==role}
    for batch in ([1,2,3] if role=='development' else [4,5,6]):
        _,rows = details(batch,token)
        for row in rows:
            sample = selected[row['data']['source_sample_key']]
            submitted = [a for a in row['annotations'] if not a.get('was_cancelled')]
            preserved.extend({'task_id':row['id'],'review_index':sample['review_index'],
                'source_sample_key':sample['source_sample_key'],'annotation':a,
                'gt_quality':effective_quality(a,sample)} for a in submitted if is_final(a))
            if not submitted:
                quality = quality_for(sample)['status']
                counts[{'exclude':'gt_excluded','review':'gt_pending'}.get(quality,'unsubmitted')] += 1
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
    write(output,{'schema':'human_standard_600_gold_v2','role':role,
        'reference_status':'human_finalized' if final else 'no_human_finalized_samples',
        'standard_sha256':manifest['standard_sha256'],'manifest_sha256':sha(HERE/'local/manifest.json'),
        'gt_screening_sha256':sha(GT_RUN/'report.json') if (GT_RUN/'report.json').exists() else None,
        'reviews':sorted(final,key=lambda x:x['review_index']),
        'human_finalized_preserved':preserved,
        'preservation_note':'All finalized human submissions retained here, including unresolved GT cases; only reviews are gold-eligible.',
        'counts':dict(counts),'issues':issues})
    print(json.dumps({'role':role,'human_finalized':len(final),'counts':dict(counts),'issues':len(issues),'output':str(output)},ensure_ascii=False))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('sync')
    sub.add_parser('clean-descriptions')
    sub.add_parser('preserve-finalized')
    e=sub.add_parser('export')
    e.add_argument('--role',choices=['development','evaluation'],default='development')
    args=p.parse_args()
    if args.command in ('sync','clean-descriptions'):
        sync(clean_human=args.command=='clean-descriptions')
    elif args.command=='preserve-finalized':
        preserve_finalized()
    else:
        export(args.role)
