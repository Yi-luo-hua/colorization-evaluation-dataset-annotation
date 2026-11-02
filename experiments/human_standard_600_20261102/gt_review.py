"""Image-based GT suitability review of the frozen 600-sample selection only."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from prepare import HERE, ROOT, sha, write

RUN = HERE/'local/gt_rescreen_20261102'
STATUS_NAMES = {'keep':'可继续审核','exclude':'建议停用','review':'待主人确认','not_screened':'尚未复筛'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


@lru_cache(maxsize=1)
def screening():
    path = RUN/'report.json'
    return {s['source_sample_key']:s for s in read(path)['samples']} if path.exists() else {}


def quality_for(sample):
    return screening().get(sample['source_sample_key'],{'status':'not_screened','reason':'尚未进行本轮GT复筛。'})


def effective_quality(annotation, sample):
    screen = quality_for(sample)
    choices = next((r.get('value',{}).get('choices',[]) for r in annotation.get('result',[])
        if r.get('from_name')=='gt_review_status'),[])
    decision = choices[0] if len(choices)==1 else '沿用GT筛查建议'
    status = {'GT可用':'keep','GT停用':'exclude','GT待确认':'review'}.get(decision,screen['status'])
    return {'status':status,'human_decision':decision,'screening':screen}


def prepare():
    RUN.mkdir(exist_ok=True)
    if (RUN/'manifest.json').exists():
        print('GT review manifest already frozen.')
        return
    groups = {}
    for sample in read(HERE/'local/manifest.json')['samples']:
        rec = sample['record']
        group = groups.setdefault(rec['gt_sha256'],{'gt_path':rec['gt_path'],'gt_sha256':rec['gt_sha256'],'samples':[]})
        group['samples'].append({k:sample[k] for k in ('review_index','source_sample_key','role','batch')})
    rows = list(groups.values())
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
    for i,row in enumerate(rows):
        row.update(gt_id=f'G{i+1:03d}',sheet=i//8+1)
        assert sha(ROOT/row['gt_path'])==row['gt_sha256']
    for offset in range(0,len(rows),8):
        board = Image.new('RGB',(1960,1080),'#eeeeee')
        draw = ImageDraw.Draw(board)
        for j,row in enumerate(rows[offset:offset+8]):
            x,y = (j%4)*490,(j//4)*540
            ids = ','.join(str(s['review_index']) for s in row['samples'])
            draw.text((x+6,y+5),f"{row['gt_id']}  review {ids}",fill='black',font=font)
            with Image.open(ROOT/row['gt_path']) as original:
                picture = ImageOps.contain(original.convert('RGB'),(480,500))
                board.paste(picture,(x+(490-picture.width)//2,y+35+(500-picture.height)//2))
        board.save(RUN/f'sheet_{offset//8+1:02d}.jpg',quality=97,subsampling=0)
    write(RUN/'manifest.json',{'scope':'600 selected generated results, GT only','unique_GT':len(rows),
        'original_selection_sha256':sha(HERE/'local/manifest.json'),'records':rows,
        'review_method':'Whole GT, fitted to at most 480x500 without cropping or color adjustment. Borderline cases inspected at original size.',
        'policy':{'exclude':'Clear major degradation or photographic processing makes GT an unreliable color/structure reference.',
            'review':'Borderline reference suitability requires human decision; excluded from gold export until resolved.',
            'keep':'No clear disqualifying issue observed; not a guarantee of perfect GT.',
            'normal_scene':'Warm/night lighting, shallow depth of field, natural low saturation, artwork or monochrome objects alone do not disqualify.'}})
    print(f'{len(rows)} unique GT; {(len(rows)+7)//8} sheets generated.')


def record(decisions):
    if 'keep' in decisions:
        group = decisions
        decisions = {f'G{i:03d}':{'status':'keep','reason':'逐图查看，未见足以妨碍颜色或结构参照的明显GT质量问题。'} for i in group['keep']}
        for status in ('exclude','review'):
            for i,reason in group.get(status,{}).items():
                key = f'G{int(i):03d}'
                assert key not in decisions
                decisions[key] = {'status':status,'reason':reason}
    manifest = read(RUN/'manifest.json')
    known = {r['gt_id']:r for r in manifest['records']}
    path = RUN/'decisions.json'
    previous = read(path) if path.exists() else {}
    for key,value in decisions.items():
        assert key in known and value['status'] in ('keep','exclude','review') and value['reason']
        previous[key] = {**value,'gt_sha256':known[key]['gt_sha256'],'reviewer':'Codex visual GT suitability review',
            'reviewed_at':datetime.now(timezone.utc).isoformat()}
    write(path,previous)
    print(json.dumps({'reviewed_unique_GT':len(previous),'counts':dict(Counter(v['status'] for v in previous.values()))},ensure_ascii=False))


def summarize():
    manifest, decisions = read(RUN/'manifest.json'), read(RUN/'decisions.json')
    assert set(decisions)=={r['gt_id'] for r in manifest['records']}
    rows = [{**r,**decisions[r['gt_id']]} for r in manifest['records']]
    samples = [{**s,'gt_id':r['gt_id'],'status':r['status'],'reason':r['reason'],'gt_path':r['gt_path'],
        'gt_sha256':r['gt_sha256']} for r in rows for s in r['samples']]
    detailed = read(RUN/'detail_review.json')
    assert set(detailed)=={r['gt_id'] for r in read(RUN/'detail_manifest.json')['records']}
    write(RUN/'report.json',{'scope_generated_results':600,'unique_GT':len(rows),
        'unique_GT_counts':dict(Counter(r['status'] for r in rows)),
        'generated_result_counts':dict(Counter(s['status'] for s in samples)),
        'all_original_GT_hashes_verified':all(sha(ROOT/r['gt_path'])==r['gt_sha256'] for r in rows),
        'source_selection_unchanged':sha(HERE/'local/manifest.json')==manifest['original_selection_sha256'],
        'records':rows,'samples':samples,'provenance':'AI visual review; no human adjudication fabricated. No original image or historical frozen exclusion list modified.'})
    lines = ['# 当前600例 GT 复筛报告','',
        '本轮逐图检查588张不重复GT，并对118张初筛问题图复看原尺寸。全图观察，不裁剪、不改色。结果为AI筛查建议，疑点等待主人裁决。',
        '', '原600例、历史标签、原图与旧冻结名单均保留；未自动补抽替换。停用和待确认项不进入金标准，主人可在Label Studio单独确认GT可用性。','',
        '| 用途 | 可继续审核 | 建议停用 | 待确认 |','|---|---:|---:|---:|']
    for role,name in [('development','校准集'),('evaluation','封存评测集')]:
        counts = Counter(s['status'] for s in samples if s['role']==role)
        lines.append(f"| {name} | {counts['keep']} | {counts['exclude']} | {counts['review']} |")
        folder = RUN/role
        folder.mkdir(exist_ok=True)
        write(folder/'gt_decisions.json',[s for s in samples if s['role']==role])
    lines += ['', '## 需要处理的GT','', '| GT编号 | 样本编号 | 建议 | 原因 |','|---|---|---|---|']
    for r in rows:
        if r['status']=='keep': continue
        ids = ', '.join(str(s['review_index']) for s in r['samples'])
        lines.append(f"| {r['gt_id']} | {ids} | {STATUS_NAMES[r['status']]} | {r['reason']} |")
    (RUN/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'unique_GT':dict(Counter(r['status'] for r in rows)),
        'generated_results':dict(Counter(s['status'] for s in samples))},ensure_ascii=False))


def confirm(boards, changes):
    record(changes)
    path = RUN/'detail_review.json'
    receipts = read(path) if path.exists() else {}
    for row in read(RUN/'detail_manifest.json')['records']:
        if row['detail_sheet'] in boards:
            board = RUN/f"detail_{row['detail_sheet']:02d}.jpg"
            receipts[row['gt_id']] = {'sheet':board.name,'sheet_sha256':sha(board),
                'whole_original_size_viewed':True,'amended':row['gt_id'] in changes}
    write(path,receipts)
    print(f'Original-size second looks recorded: {len(receipts)}')


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('command',choices=['prepare','record','summarize'])
    p.add_argument('--file',type=Path)
    args=p.parse_args()
    if args.command=='prepare': prepare()
    elif args.command=='record': record(read(args.file))
    else: summarize()
