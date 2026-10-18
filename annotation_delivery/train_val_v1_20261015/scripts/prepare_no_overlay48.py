"""Rebuild the same 48 offline review inputs without candidate overlays; no model calls."""
import copy
from collections import Counter
from pathlib import Path
import shutil

import numpy as np
from PIL import Image

from prepare import PROJECT, ROOT, read, write, sha, SIX
from prepare_packets import render, RENDER_REVISION
from secondary_review import prepare_secondary_files

source = PROJECT/'runtime/secondary_review_correction_20261015_01/packets'
output = PROJECT/'runtime/no_overlay_20261015_01/packets'
output.mkdir()
cfg = read(PROJECT/'config.json')
cv = read(ROOT/cfg['source_config'])
assert cv['display']['hue_outline'] is False
source_hash = sha(ROOT/cfg['sources']['legacy_reviewed'])
seen, counts, packets = set(), Counter(), []
for identifier in ['T0009','T0011']:
    old = source/identifier
    mapping = read(old/'manifest_private.json')['sample_mapping']
    assert all(r['baseline']['source']['sha256']==source_hash for r in mapping.values())
    directory = output/identifier
    (directory/'sheets').mkdir(parents=True)
    sheets = render(list(mapping.values()),'secondary_chroma',directory/'sheets',cfg,cv)
    request = read(old/'request.json')
    request.update(packet_id=identifier+'-no-overlay-v1',sheets=sheets,
        render_revision=RENDER_REVISION,candidate_overlays=False,
        checked_categories=SIX,result_file=str((directory/'reviews_gemini.json').resolve()),
        prior_reviews_file=str((directory/'prior_reviews.json').resolve()))
    request['allowed_read_files'] = [s['path'] for s in sheets]+[request['prior_reviews_file']]
    prepare_secondary_files(directory,request,mapping)
    write(directory/'request.json',request)
    write(directory/'manifest_private.json',{'sample_mapping':mapping,'host_only':True})
    common = (PROJECT/'prompts/session.md').read_text(encoding='utf-8')
    role = (PROJECT/'prompts/secondary_chroma.md').read_text(encoding='utf-8')
    current = (f'packet_id={request["packet_id"]}，stage=secondary_chroma，render_revision={RENDER_REVISION}。\n'
        f'先读匿名底稿：{request["prior_reviews_file"]}\n只修改结果：{request["result_file"]}\n'
        '指定看板，每张读取一次：\n'+'\n'.join(s['path']+': '+', '.join(s['sample_keys']) for s in sheets)
        +'\n重点重标E1/E2，原B/C/D/F逐P编号review。保存后只回复“文件已保存”。')
    (directory/'prompt_first.txt').write_text(common+'\n'+role+'\n'+current,encoding='utf-8')
    (directory/'prompt_continue.txt').write_text('继续固定二次角色，本轮S编号重新对应。\n'+role+'\n'+current,encoding='utf-8')
    old_sheets = read(old/'request.json')['sheets']
    for before, after in zip(old_sheets,sheets):
        a,b = np.array(Image.open(before['path'])),np.array(Image.open(after['path']))
        assert a.shape==b.shape and np.array_equal(a[:,:1048],b[:,:1048])
        assert not np.array_equal(a[:,1048:],b[:,1048:])
        # Signed-chroma contains red/blue, so yellow/orange candidate pixels must disappear.
        yellow = lambda x: int(np.count_nonzero((x[:,:,0]>200)&(x[:,:,1]>130)&(x[:,:,2]<80)))
        assert yellow(b[:,1048:])==0
        counts['old_yellow_overlay_pixels'] += yellow(a[:,1048:])
        counts['new_yellow_overlay_pixels'] += yellow(b[:,1048:])
    assert all(v is None for v in read(directory/'reviews_gemini.json')['reviews'].values())
    assert read(directory/'prior_reviews.json')==read(old/'prior_reviews.json')
    # Even an old config enabling hue_outline cannot restore the deleted render path.
    if identifier=='T0009':
        probe = output.parent/'old_config_render_check'
        probe.mkdir()
        stale = copy.deepcopy(cv)
        stale['display']['hue_outline'] = True
        check = render(list(mapping.values())[:6],'secondary_chroma',probe,cfg,stale)
        assert check[0]['sha256']==sheets[0]['sha256']
        # RGB retains its existing renderer and never calls candidate overlay code.
        rgb = output.parent/'rgb_preview'
        rgb.mkdir()
        render(list(mapping.values())[:6],'initial_rgb',rgb,cfg,cv)
    seen.update(r['source_sample_key'] for r in mapping.values())
    counts['original_BCDF_items'] += sum(len(x['other_defects']) for x in request['secondary_baseline'].values())
    counts['old_E_items'] += sum(len(x['old_saturation']) for x in request['secondary_baseline'].values())
    paths = [p for p in directory.rglob('*') if p.is_file()]
    write(directory/'packet_integrity.json',{str(p.relative_to(directory)):sha(p) for p in paths})
    packets.append({'packet':identifier,'samples':len(mapping),'boards':len(sheets),'path':str(directory.resolve())})
assert len(seen)==48 and counts['original_BCDF_items']==77
for path in [PROJECT/'prompts/session.md',PROJECT/'prompts/secondary_chroma.md',
             PROJECT/'scripts/prepare_packets.py',Path(__file__),ROOT/'experiments/cv_workflow/config.json']:
    target = output.parent/'sources'/path.relative_to(ROOT)
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(path,target)
write(output/'verification.json',{'render_revision':RENDER_REVISION,'samples':48,'boards':8,
    'candidate_overlays':False,'GT_and_generated_panels_byte_identical':True,
    'old_config_cannot_restore_overlay':True,'baseline_unchanged':True,'source_sha256':source_hash,
    'model_calls':0,'new_labels':0,'state':'offline_prepared_not_started',
    'counts':dict(counts),'packets':packets})
active = read(PROJECT/'ACTIVE_PREPARATION.json')
active.update(corrected_packets='runtime/no_overlay_20261015_01/packets',
    render_revision=RENDER_REVISION,candidate_overlays=False,
    no_overlay_preparation='runtime/no_overlay_20261015_01/packets/verification.json',
    historical_trial_render_has_overlays=True)
write(PROJECT/'ACTIVE_PREPARATION.json',active)
print(f'Prepared {len(seen)} samples / 8 chroma boards, no model calls; {dict(counts)}')
