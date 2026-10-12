import json

with open(r'd:\学业文件\MCL\上色评价_数据集标注\LS_lcad_reviewer\intermediate\audits\deep_fix_targets_all.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

p4 = [x for x in data if x['batch_id'] == 6]
print('Part 4 count:', len(p4))
for i, item in enumerate(p4):
    sheet_idx = i // 6 + 1
    card_idx = i % 6 + 1
    t_id = item['task_id']
    img_id = item['image_id']
    orig_def = item['raw_defects']
    orig_s = item['raw_score']
    print(f"{i+1:02d} | Sheet {sheet_idx:02d} #{card_idx} | Task {t_id:04d} | Img {img_id} | OrigScore {orig_s} | Def: {orig_def}")
