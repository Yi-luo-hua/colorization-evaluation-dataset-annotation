import json
import numpy as np
from PIL import Image

with open('LS_lcad_reviewer/tasks_lcad_10000.json', 'r', encoding='utf-8') as f:
    raw_tasks = json.load(f)

with open('LS_lcad_reviewer/intermediate/scripts/batch_43_meta_summary.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

for s in [18, 19, 20]:
    start_i = (s - 1) * 6
    sheet_items = items[start_i:start_i+6]
    print(f'=== Sheet {s} ===')
    for it in sheet_items:
        t_id = it['task_id']
        raw = raw_tasks[t_id - 1]
        rec = raw['data']['original_record']
        img_id = rec['file_path']
        fname = img_id.split('/')[-1].replace('.png', '.jpg')
        gt_path = f'9_14_10000GT_V1/image/{fname}'
        gen_path = f'9_14_10000GT_V1/model/{img_id}'
        
        orig_score = rec.get('gpt_score', 0)
        orig_defects = [(d['id'], d.get('severity', '')) for d in rec.get('defects', [])]
        
        try:
            gen_pil = Image.open(gen_path).convert('RGB')
            gt_pil = Image.open(gt_path).convert('RGB').resize(gen_pil.size, Image.Resampling.BILINEAR)
            
            gt_img = np.array(gt_pil, dtype=np.float32) / 255.0
            gen_img = np.array(gen_pil, dtype=np.float32) / 255.0
            
            diff = np.abs(gt_img - gen_img)
            dc = np.mean(diff)
            
            # color opponent
            # RG = R - G, YB = 0.5*(R + G) - B
            rg_gt = gt_img[:,:,0] - gt_img[:,:,1]
            yb_gt = 0.5*(gt_img[:,:,0] + gt_img[:,:,1]) - gt_img[:,:,2]
            rg_gen = gen_img[:,:,0] - gen_img[:,:,1]
            yb_gen = 0.5*(gen_img[:,:,0] + gen_img[:,:,1]) - gen_img[:,:,2]
            
            delta_rg = np.mean(rg_gen) - np.mean(rg_gt)
            delta_yb = np.mean(yb_gen) - np.mean(yb_gt)
            delta_c = np.sqrt(delta_rg**2 + delta_yb**2)
            
            s_gt = np.max(gt_img, axis=-1) - np.min(gt_img, axis=-1)
            s_gen = np.max(gen_img, axis=-1) - np.min(gen_img, axis=-1)
            r_sat = (np.mean(s_gen) + 1e-4) / (np.mean(s_gt) + 1e-4)
            print(f"Task #{t_id}: score={orig_score}, dc={delta_c:.3f}, r_sat={r_sat:.2f}, drg={delta_rg:+.3f}, dyb={delta_yb:+.3f}, def={orig_defects}")
        except Exception as e:
            print(f"Task #{t_id}: score={orig_score}, def={orig_defects}, err={e}")
