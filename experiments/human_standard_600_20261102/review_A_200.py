"""Record the explicit visual A audit; pixel differences are supporting evidence."""
from datetime import datetime, timezone
import json
import numpy as np
from PIL import Image

from prepare import HERE, ROOT, sha, write
from summarize_200 import SOURCES

DECISIONS = {
    8:('suggest_not_A','猫眼与耳部有微弱暖色残留，画面部分浅色区带淡暖灰色调。'),
    42:('suggest_not_A','天空和地面浅色区域存在一致的淡暖黄褐色调，接近灰阶但仍可辨暖色。'),
    63:('suggest_not_A','墙砖与浅色洁具带淡黄暖灰色调，未完全呈中性灰阶。'),
    101:('borderline','建筑整体视觉近灰阶，部分石砖有极弱的局部色彩残留；原图仅256×256，是否达到可辨色调边界仍需人裁决。'),
    102:('support_A','原尺寸观察未见稳定可辨的色调，视觉呈灰阶；少量通道差异不足以单独否定A。'),
    122:('suggest_not_A','列车车体、站台和人物整体呈可辨淡棕褐色，属于极低饱和度彩色。'),
    161:('support_A','建筑和雕像视觉呈灰阶，未见稳定可辨色调；微小通道差异不足以单独否定A。'),
    164:('suggest_not_A','钟面有可辨的淡黄偏绿暖色，与周边近灰阶建筑形成区别。'),
    166:('support_A','人像与背景在原尺寸下视觉呈灰阶，未见稳定可辨色调；极小通道差异不足以单独否定A。'),
    194:('suggest_not_A','球场、墙面及人物存在一致的灰黄绿色调，并非无可辨色调的灰阶。')}


def audit():
    override = HERE/'local/A_gray_review_20261104/human_override.json'
    if override.exists():
        print('Historical AI rejection suggestions are withdrawn. All ten human A labels are authoritative; see A_CALIBRATION_20261104.md.')
        return
    records = []
    for source in SOURCES:
        for row in json.loads(source.read_text(encoding='utf-8'))['reviews']:
            if not any(d['id']=='A' for d in row['defects']):
                continue
            index = row['review_index']
            path = ROOT/row['record']['model_path']
            assert sha(path)==row['record']['model_sha256']
            with Image.open(path) as image:
                rgb = np.array(image.convert('RGB')).astype(np.int16)
                spread = rgb.max(2)-rgb.min(2)
                status,evidence = DECISIONS[index]
                records.append({'review_index':index,'task_id':row['task_id'],
                    'source_sample_key':row['source_sample_key'],'model_path':str(path),'image_sha256':sha(path),
                    'original_size':image.size,'original_mode':image.mode,
                    'status':status,'visual_evidence':evidence,'original_image_visually_viewed':True,
                    'second_look':index in [8,101,102],
                    'pixel_evidence':{'exactly_equal_RGB_fraction':float((spread==0).mean()),
                        'channel_spread_max':int(spread.max()),'channel_spread_median':float(np.median(spread)),
                        'channel_spread_p95':float(np.percentile(spread,95)),
                        'channel_spread_gt5_fraction':float((spread>5).mean()),
                        'mean_R_minus_G':float((rgb[:,:,0]-rgb[:,:,1]).mean()),
                        'mean_B_minus_G':float((rgb[:,:,2]-rgb[:,:,1]).mean())}})
    assert {r['review_index'] for r in records}==set(DECISIONS)
    folder = HERE/'local/A_gray_review_20261104'
    folder.mkdir(exist_ok=True)
    write(folder/'visual_audit.json',{'reviewed_at':datetime.now(timezone.utc).isoformat(),
        'scope':'10 human A samples in first 200, generated images only',
        'criterion':'No perceptible chromatic tone, per 11.2 standard. Exact RGB equality is distinct from visual achromaticity.',
        'source_archives':[{'path':str(p),'sha256':sha(p)} for p in SOURCES],
        'records':records,'human_endpoint_writes':0,'human_finalized_labels_unchanged':True,
        'limitations':'Native image viewing and decoded RGB statistics; no saturation amplification, cropping, new defect grades or human adjudication fabricated.'})
    names = {'support_A':'支持保留A','suggest_not_A':'不建议判A','borderline':'边界待确认'}
    lines = ['# 前200张人工A样本视觉复核','',
        '逐张查看10张原始生成图，未修改图片或人工标注。判断采用11.2“无任何可辨色调”的视觉标准。',
        '全部10张解码后RGB均非逐像素完全相等；该数学结果不能直接用作肉眼可辨色调的判定。',
        '', '结论：3张支持保留A，6张不建议判A，1张边界待确认。建议改判项应沿E2方向结合GT另定等级，本轮不补造等级或其他缺陷。',
        '', '| 编号 | 建议 | 原尺寸观察 |','|---|---|---|']
    for r in sorted(records,key=lambda r:r['review_index']):
        batch = 1 if r['review_index']<=100 else 2
        pid = 31+batch
        url = f'http://localhost:8080/projects/{pid}/data/?tab={pid}&labeling=1&task={r["task_id"]}'
        lines.append(f'| [{r["review_index"]}]({url}) | {names[r["status"]]} | {r["visual_evidence"]} |')
    (folder/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({key:[r['review_index'] for r in records if r['status']==key] for key in names}))


if __name__=='__main__': audit()
