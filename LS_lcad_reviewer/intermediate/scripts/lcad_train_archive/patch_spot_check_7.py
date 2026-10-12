# -*- coding: utf-8 -*-
"""
patch_spot_check_7.py
将 100 张放行抽检中发现的 7 例确凿漏网伪放行样本打补丁更新至正式交付文件
"""

import json

PATCH_REVIEWS = {
    84: {
        "score": 4.55,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "草坪上飞盘运动青年身穿的鲜艳荧光黄绿色运动T恤在生成图中被完全褪色错涂为灰白色，红色运动鞋变黑灰色(C-L2, E2-L2)。"
    },
    291: {
        "score": 4.55,
        "severities": {"D": "L1"},
        "note": "火车站台水泥地面与红色客车车身泛明显暖黄青蓝偏色，全图环境色温失调(D-L1)。"
    },
    344: {
        "score": 4.55,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "海滩沙滩上散步男子身穿的深蓝色连帽卫衣欠饱和发灰泛暗紫，金色沙滩泛冷，全图环境微偏青蓝(D-L1, E2-L1)。"
    },
    2996: {
        "score": 5.0,
        "severities": {"C": "L2"},
        "note": "与长颈鹿合影的女性身穿的鲜艳宝蓝色耐克连帽衫被严重常识性错涂为豆沙浅草绿色(C-L2)。"
    },
    3370: {
        "score": 4.55,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "林间公园木质长椅地面铺满的厚重暖铜褐色秋日落叶大面积欠饱和严重脱色泛灰泛绿(D-L1, E2-L1)。"
    },
    4002: {
        "score": 4.55,
        "severities": {"C": "L2"},
        "note": "观赏长颈鹿的左侧游客所穿的亮深红色短袖T恤被明显错涂为暗卡其棕褐色(C-L2)。"
    },
    7805: {
        "score": 2.43,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "佩戴猫咪领带女士身穿的翡翠绿缎面衬衫在生成图中明显发暗偏向橄榄褐灰，领带猫咪花纹欠饱和(D-L1, E2-L1)。"
    }
}

DEFECT_NAME_MAP = {
    "A": "缺色",
    "B": "溢色",
    "C": "错色",
    "D": "偏色",
    "E1": "过饱和",
    "E2": "欠饱和",
    "F": "视觉自然度"
}

def apply_patch():
    all_path = "LS_lcad_reviewer/exports/reviewed_1_10000_all.json"
    clean_path = "LS_lcad_reviewer/exports/reviewed_1_10000_clean.json"

    with open(all_path, "r", encoding="utf-8") as f:
        data_all = json.load(f)
    with open(clean_path, "r", encoding="utf-8") as f:
        data_clean = json.load(f)

    anns_all = data_all["annotations"]
    anns_clean = data_clean["annotations"]

    idx_map_all = {ann["human_review"]["task_id"]: i for i, ann in enumerate(anns_all)}
    idx_map_clean = {ann["human_review"]["task_id"]: i for i, ann in enumerate(anns_clean)}

    for tid, rev in PATCH_REVIEWS.items():
        if tid not in idx_map_all:
            print(f"Warning: Task #{tid} not found in dataset!")
            continue

        ann_a = anns_all[idx_map_all[tid]]
        ann_c = anns_clean[idx_map_clean[tid]]

        severities = rev["severities"]
        note = rev["note"]

        defects = []
        for code, sev in severities.items():
            defects.append({
                "id": code,
                "name": DEFECT_NAME_MAP.get(code, code),
                "severity": sev,
                "description": note
            })

        ann_a["review_status"] = "已核验"
        ann_a["review_note"] = note
        ann_a["defects"] = defects
        ann_a["reviewed_score"] = None
        ann_a["needs_rescoring"] = True

        ann_c["review_status"] = "已核验"
        ann_c["review_note"] = ""
        ann_c["defects"] = defects
        ann_c["reviewed_score"] = None
        ann_c["needs_rescoring"] = True

        print(f"Patched Task #{tid}: {list(severities.keys())} -> {note[:30]}...")

    with open(all_path, "w", encoding="utf-8") as f:
        json.dump(data_all, f, ensure_ascii=False, indent=2)
    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(data_clean, f, ensure_ascii=False, indent=2)

    print("Patched both all and clean exports successfully!")

if __name__ == "__main__":
    apply_patch()
