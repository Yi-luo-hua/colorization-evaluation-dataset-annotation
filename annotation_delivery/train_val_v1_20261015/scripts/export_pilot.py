"""Export only accepted final six-category pilot files to Label Studio predictions."""
import argparse
from collections import Counter
import copy
from html import escape
from pathlib import Path
from urllib.parse import quote

from prepare import PROJECT, ROOT, SIX, lines, read, write, sha
from review_contract import validate_entry

NAMES = {'B':'溢色','C':'错色','D':'偏色','E1':'过饱和','E2':'欠饱和','F':'视觉自然度'}


def review_audit_html(baseline, review):
    delta = review.get('baseline_review')
    if not delta:
        return '<p>此历史结果没有逐项review记录。</p>'
    original = {f'P{i:03d}':d for i,d in enumerate(baseline['defects'],1) if d['id'] in ['B','C','D','F']}
    names = {'retain':'保留','correct':'纠正','remove':'删除','uncertain':'待处理'}
    rows = []
    for identifier, old in original.items():
        decision = delta['other_decisions'][identifier]
        action = decision['action']
        current = decision.get('defect') if action=='correct' else ((copy.deepcopy(old)
            if decision.get('inherit') is True else {'id':old['id'],'severity':old['severity'],
            'description':decision['description']}) if action=='retain' else None)
        values = [identifier, NAMES[old['id']]+' '+old['severity'],old.get('description',''),names[action],
                  (NAMES[current['id']]+' '+current['severity']+' · '+current['description']) if current else '—',decision['reason']]
        rows.append('<tr>'+''.join('<td style="padding:6px;border:1px solid #ddd;vertical-align:top">'+escape(str(v))+'</td>' for v in values)+'</tr>')
    if not rows:
        return '<p>原底稿没有B/C/D/F条目；本轮E重标及明显漏项见最终标签。</p>'
    return ('<p>以下原描述仅供追溯；最终训练描述见上方。每条原标签均有明确审核去向。</p>'
        '<table style="width:100%;border-collapse:collapse"><thead><tr><th>原标签编号</th><th>原类别等级</th><th>原底稿描述</th><th>审核动作</th><th>当前结果</th><th>审核理由</th></tr></thead><tbody>'
        +''.join(rows)+'</tbody></table>')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, default=PROJECT / 'runtime/pilot_384_20261015_01')
    parser.add_argument('--allow-partial', action='store_true')
    parser.add_argument('--output-name')
    parser.add_argument('--model-version', default='gemini-3.8-flash-high / NR_v2 / pilot_384')
    parser.add_argument('--review-info', default='Gemini High单图质量试标 · 六类完成 · 待主人复核 · 无新评分')
    args = parser.parse_args()
    payload = read(args.run / 'visual_reviews.json')
    if not payload['complete'] and not args.allow_partial:
        raise ValueError(f'Run incomplete: {payload["completed_samples"]}/{payload["target_samples"]}; no full stream exported')
    cfg = read(PROJECT / 'config.json')
    inventory = {r['source_sample_key']: r for r in lines(PROJECT / cfg['preparation']['inventory'] / 'inventory.jsonl')}
    tasks, provenance = [], []
    pool_cache = {}
    for index, review in enumerate(payload['reviews'], 1):
        record = inventory[review['source_sample_key']]
        error = validate_entry(review['defects'], SIX)
        if error:
            raise ValueError(error)
        source = record['source_task']
        if source['path'] not in pool_cache:
            if sha(ROOT / source['path']) != source['sha256']:
                raise ValueError('Source task pool changed')
            pool_cache[source['path']] = read(ROOT / source['path'])
        original_task = pool_cache[source['path']][record['task_idx'] - 1]
        data = {'image': '/data/local-files/?d=' + quote(record['model_path'], safe='/'),
                'reference': '/data/local-files/?d=' + quote(record['gt_path'], safe='/'),
                'sample_title': f'{index:04d} · {review["source_sample_key"]}',
                'source_sample_key': review['source_sample_key'], 'dataset_split': record['split'], 'model_role': record['model'],
                'image_id': record['image_id'], 'annotation_contract': cfg['annotation_contract'],
                'original_record': copy.deepcopy(original_task['data']['original_record']),
                'review_baseline': copy.deepcopy(record['baseline']),
                'nr_AI_review': copy.deepcopy(review),
                'review_info': args.review_info}
        rows = ''.join('<tr>' + ''.join(f'<td style="padding:5px;border:1px solid #ddd">{escape(str(value))}</td>' for value in
                       [NAMES[d['id']],d['severity'],d['object'],d['description']]) + '</tr>' for d in review['defects'])
        data['defect_details_html'] = ('<table style="width:100%;border-collapse:collapse"><thead><tr><th>类别</th><th>等级</th><th>对象</th><th>自然语言描述</th></tr></thead><tbody>'
                                       + rows + '</tbody></table>') if rows else '<p>六类逐项检查后未见缺陷，待主人复核。</p>'
        data['review_audit_html'] = review_audit_html(record['baseline'],review)
        result = [{'from_name':'severity_A','to_name':'colorized','type':'choices','value':{'choices':['未命中']}},
                  {'from_name':'review_status','to_name':'colorized','type':'choices','value':{'choices':['待复核']}}]
        for category in SIX:
            defects = [d for d in review['defects'] if d['id'] == category]
            severity = max((d['severity'] for d in defects), default='无此缺陷')
            result.append({'from_name':'severity_'+category,'to_name':'colorized','type':'choices','value':{'choices':[severity]}})
            if defects:
                result.append({'from_name':'description_'+category,'to_name':'colorized','type':'textarea',
                               'value':{'text':['\n'.join(d['description'] for d in defects)]}})
        for number, item in enumerate(result):
            item['id'] = f'r{index:04d}_{number:02d}'
        tasks.append({'data':data,'predictions':[{'model_version':args.model_version,'result':result}]})
        provenance.append({'source_sample_key':review['source_sample_key'], 'AI_provenance':review['provenance'],
                           'initial_provenance':next((j['accepted'][review['source_sample_key']]['provenance']
                              for j in read(args.run/'checkpoint.json')['jobs'].values()
                              if j['stage']=='initial_rgb' and review['source_sample_key'] in j['accepted']), None)})
    out = args.run / 'exports'
    out.mkdir(exist_ok=True)
    name = args.output_name or (f'tasks_NR_pilot_{payload["target_samples"]}_stream.json' if payload['complete'] else f'tasks_NR_pilot_partial_{len(tasks)}_stream.json')
    target = out / name
    if target.exists():
        raise ValueError('Preserve existing export')
    write(target, tasks)
    write(out / 'provenance.json', {'annotation_contract':cfg['annotation_contract'],'samples':len(tasks),
          'experiment_annotations_used':0,'human_annotations_created':0,'scores_recomputed':False,'records':provenance})
    write(out / 'export_verification.json', {'samples':len(tasks),'unique_samples':len({t['data']['source_sample_key'] for t in tasks}),
          'predictions':sum(len(t['predictions']) for t in tasks), 'complete':payload['complete'],
          'natural_language_format_checked':True,'semantic_accuracy_verified':False,
          'split_model_counts':dict(Counter(f'{t["data"]["dataset_split"]}/{t["data"]["model_role"]}' for t in tasks)),
          'stream_sha256':sha(target), 'human_annotations_created':0})
    print(f'Exported {len(tasks)} predictions: {target}')


if __name__ == '__main__':
    main()
