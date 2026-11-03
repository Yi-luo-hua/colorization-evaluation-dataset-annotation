"""Archive one human-reviewed batch without changing Label Studio results."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json

from manage import material, details, parse_final, is_final
from labelstudio import BASE, access_token, api
from prepare import HERE, sha, write
from gt_review import effective_quality, RUN as GT_RUN


def archive(batch):
    manifest,_ = material()
    token = access_token(BASE)
    project,rows = details(batch,token)
    folder = HERE/f'local/batch_{batch:02d}'/('human_archive_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    folder.mkdir()
    write(folder/'raw_snapshot.json',{'project':api(BASE,token,f'/api/projects/{project["id"]}/'),
        'captured_at':datetime.now(timezone.utc).isoformat(),'tasks':rows})
    samples = {s['source_sample_key']:s for s in manifest['samples'] if s['batch']==batch}
    assert len(rows)==100 and {r['data']['source_sample_key'] for r in rows}==set(samples)
    counts = Counter(tasks=len(rows))
    final,preserved,issues = [],[],[]
    for row in rows:
        sample = samples[row['data']['source_sample_key']]
        submitted = [a for a in row['annotations'] if not a.get('was_cancelled')]
        identity = {'review_index':sample['review_index'],'task_id':row['id'],
            'source_sample_key':sample['source_sample_key']}
        counts['submitted_tasks'] += bool(submitted)
        counts['finalized'] += sum(is_final(a) for a in submitted)
        preserved.extend({**identity,'annotation':a,'gt_quality':effective_quality(a,sample)}
            for a in submitted if is_final(a))
        if len(submitted)!=1:
            issues.append({**identity,'reason':'$.annotations: 未提交或有多份有效提交，需明确裁决'})
            continue
        try:
            result = parse_final(submitted[0],sample)
            if result is None:
                issues.append({**identity,'reason':'$.result[from_name=review_status]: 尚未选择已定稿'})
            else:
                final.append({**result,'task_id':row['id']})
        except ValueError as exc:
            issues.append({**identity,'reason':str(exc)})
    receipt = {'batch':batch,'role':'development' if batch<=3 else 'evaluation','counts':dict(counts),
        'gold_eligible':len(final),'issues':issues,'human_endpoint_writes':0,
        'raw_snapshot_sha256':sha(folder/'raw_snapshot.json')}
    write(folder/'human_gold.json',{'schema':'human_standard_600_gold_v2',**receipt,
        'standard_sha256':manifest['standard_sha256'],'manifest_sha256':sha(HERE/'local/manifest.json'),
        'gt_screening_sha256':sha(GT_RUN/'report.json'),
        'reviews':sorted(final,key=lambda r:r['review_index']),
        'human_finalized_preserved':preserved,
        'preservation_note':'Raw snapshot retains all submissions and drafts; only reviews are gold-eligible.'})
    receipt['human_gold_sha256'] = sha(folder/'human_gold.json')
    write(folder/'receipt.json',receipt)
    lines = [f'# 第{batch}批人工审核归档','',
        f"共{len(rows)}张，已有人工提交{counts['submitted_tasks']}张，已定稿{counts['finalized']}份，可导出金标准{len(final)}张。",
        '','全部人工提交及草稿完整留存于raw_snapshot.json，未写入或修改任何人审结果。',
        'A类命中不分级并熔断其他类别；描述可留空，导出不补造文字。',
        '', '## 待处理项','', '| 编号 | 任务 | 原因 |','|---|---|---|']
    for item in issues:
        url = f'http://localhost:8080/projects/{project["id"]}/data/?tab={project["id"]}&labeling=1&task={item["task_id"]}'
        lines.append(f'| {item["review_index"]} | [{item["task_id"]}]({url}) | {item["reason"]} |')
    (folder/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'archive':str(folder),**receipt},ensure_ascii=False),flush=True)


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch',type=int,choices=range(1,7),required=True)
    archive(parser.parse_args().batch)
