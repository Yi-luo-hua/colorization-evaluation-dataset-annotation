"""Prepare the same 48 samples for saturation relabeling plus preserved-baseline review; no model calls."""
import shutil
from collections import Counter
from pathlib import Path
from prepare import PROJECT, ROOT, read, write, sha, SIX
from secondary_review import POLICY, REVISION, prepare_secondary_files, baseline_from_mapping

source = PROJECT/'runtime/pilot_384_20261015_01'
output = PROJECT/'runtime/secondary_review_correction_20261015_01/packets'
output.mkdir()
cfg = read(PROJECT/'config.json')
old = read(source/'checkpoint.json')
target = {r['source_sample_key'] for r in read(source/'visual_reviews.json')['reviews']}
source_hash = sha(ROOT/cfg['sources']['legacy_reviewed'])
seen, packet_index = set(), []
totals = Counter()
for identifier in ['T0009','T0011']:
    original = Path(next(a['path'] for a in reversed(old['jobs'][identifier]['attempts']) if a.get('accepted_samples')==24))
    mapping = read(original/'manifest_private.json')['sample_mapping']
    assert all(row['baseline']['source']['sha256']==source_hash for row in mapping.values())
    destination = output/identifier
    (destination/'sheets').mkdir(parents=True)
    sheets = []
    for sheet in read(original/'request.json')['sheets']:
        path = destination/'sheets'/Path(sheet['path']).name
        shutil.copy2(sheet['path'],path)
        assert sha(path)==sheet['sha256']
        sheets.append({**sheet,'path':str(path.resolve())})
    request = {'annotation_contract':cfg['annotation_contract'],'stage':'secondary_chroma',
        'packet_id':identifier+'-preserve-review-v1','checked_categories':SIX,'sheets':sheets}
    prepare_secondary_files(destination,request,mapping)
    write(destination/'request.json',request)
    write(destination/'manifest_private.json',{'sample_mapping':mapping,'host_only':True})
    common = (PROJECT/'prompts/session.md').read_text(encoding='utf-8')
    role = (PROJECT/'prompts/secondary_chroma.md').read_text(encoding='utf-8')
    listing = '\n'.join(s['path']+': '+', '.join(s['sample_keys']) for s in sheets)
    current = (f'packet_id={request["packet_id"]}，annotation_contract={request["annotation_contract"]}，stage=secondary_chroma。\n'
        f'先读取匿名审核底稿：{(destination/"prior_reviews.json").resolve()}\n'
        f'只修改结果：{(destination/"reviews_gemini.json").resolve()}\n'
        '本轮看板，每张读取一次：\n'+listing+'\n重点重标E1/E2；原B/C/D/F逐P编号审核，不能用六类自由重标覆盖底稿。保存后只回复“文件已保存”。')
    (destination/'prompt_first.txt').write_text(common+'\n'+role+'\n'+current,encoding='utf-8')
    (destination/'prompt_continue.txt').write_text('继续固定二次审核角色，按NR_secondary_preserve_20261015_04执行。\n'+role+'\n'+current,encoding='utf-8')
    baseline = baseline_from_mapping(mapping)
    for row in baseline.values():
        totals['B_C_D_F_items'] += len(row['other_defects'])
        totals['old_E_items'] += len(row['old_saturation'])
    seen.update(row['source_sample_key'] for row in mapping.values())
    packet_index.append({'packet':identifier,'samples':len(mapping),'boards':len(sheets),'path':str(destination.resolve())})
assert seen==target and len(seen)==48
write(output/'verification.json',{'prompt_revision':REVISION,'secondary_merge_policy':POLICY,
    'samples':48,'original_source_unchanged':True,'source_sha256':source_hash,'same_48_source_identities':True,
    'original_board_bytes_unchanged':True,'baseline_counts':dict(totals),'model_calls':0,
    'new_policy_completed':0,'state':'prepared_not_started_provider_access_blocked','packets':packet_index})
print('Prepared exactly48; baseline item counts',dict(totals),'; model calls0')
