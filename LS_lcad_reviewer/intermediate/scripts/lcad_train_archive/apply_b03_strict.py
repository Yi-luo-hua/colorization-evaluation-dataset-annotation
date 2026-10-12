# -*- coding: utf-8 -*-
"""
apply_b03_strict.py:
Strictly apply physical grounding to the 18 violation tasks in Batch 03,
updating grounding_remaining_batch_03.json, reviewed_1_10000_all.json, and reviewed_1_10000_clean.json.
"""

import json
from pathlib import Path

GROUNDING_FILE = Path("LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_03.json")
EXPORTS_ALL = Path("LS_lcad_reviewer/exports/reviewed_1_10000_all.json")
EXPORTS_CLEAN = Path("LS_lcad_reviewer/exports/reviewed_1_10000_clean.json")

B03_FIXES = {
    408: {
        "score": 2.11,
        "severities": ["B-L1", "D-L1", "F-L1"],
        "descriptions": [
            "榨汁搅拌机杯体内柠檬块偏色溢染至透明杯壁边缘。",
            "搅拌机白色机座及操作台面整体泛暖黄偏色。",
            "杯体边缘色彩过渡不够自然。"
        ],
        "note": "视觉改判：榨汁搅拌机杯内柠檬偏色溢染且机座泛暖黄偏色 (B-L1, D-L1, F-L1)"
    },
    413: {
        "score": 2.47,
        "severities": ["E2-L2", "D-L1"],
        "descriptions": [
            "卫生间马桶及墙面瓷砖严重暗淡褪色泛灰，欠饱和明显。",
            "室内光线及窗户周围轻微偏冷暗色。"
        ],
        "note": "视觉改判：卫生间马桶及墙面瓷砖暗淡褪色泛灰欠饱和 (E2-L2, D-L1)"
    },
    414: {
        "score": 2.23,
        "severities": ["E1-L2", "F-L1"],
        "descriptions": [
            "高山牧场前景草地与远处山体植被过饱和鲜艳刺眼。",
            "草地与山体色彩层次同质化，视觉生硬。"
        ],
        "note": "视觉改判：高山牧场前景草地与山体植被过饱和鲜艳刺眼 (E1-L2, F-L1)"
    },
    421: {
        "score": 2.47,
        "severities": ["E2-L2", "D-L1"],
        "descriptions": [
            "海滩浅水区水牛身体及海水与天空大面积泛灰褪色，欠饱和明显。",
            "海面与沙滩环境光轻微偏冷灰暗。"
        ],
        "note": "视觉改判：海滩浅水区水牛与海面天空大面积泛灰褪色 (E2-L2, D-L1)"
    },
    431: {
        "score": 2.45,
        "severities": ["B-L2", "C-L1"],
        "descriptions": [
            "运动男子手中网球拍击球轨迹处出现亮蓝色虚假光轨与溢色扩散。",
            "击球轨迹被异常上色为荧光亮蓝色，常识违和。"
        ],
        "note": "视觉改判：运动男子手中网球拍击球轨迹出现亮蓝溢色与异常光斑 (B-L2, C-L1)"
    },
    444: {
        "score": 2.61,
        "severities": ["D-L2"],
        "descriptions": [
            "棒球选手面部与手臂皮肤严重泛红褐色偏色。"
        ],
        "note": "视觉改判：棒球选手面部与手臂皮肤严重泛红褐色偏色 (D-L2)"
    },
    449: {
        "score": 2.43,
        "severities": ["D-L2", "E2-L1"],
        "descriptions": [
            "室内落地窗木框与木地板大面积泛黄褐暖偏色。",
            "室内桌椅等家具色调偏暗，缺乏明亮采光质感。"
        ],
        "note": "视觉改判：室内落地窗木框与木地板大面积泛黄褐暖偏色 (D-L2, E2-L1)"
    },
    475: {
        "score": 2.56,
        "severities": ["E2-L2", "F-L1"],
        "descriptions": [
            "海滩边玩耍的小男孩皮肤及沙滩海水整体严重发灰褪色，欠饱和明显。",
            "阳光沙滩整体氛围发闷发灰，视觉真实感下降。"
        ],
        "note": "视觉改判：海滩玩耍的小男孩皮肤及沙滩海水严重发灰褪色 (E2-L2, F-L1)"
    },
    483: {
        "score": 2.32,
        "severities": ["D-L2", "E2-L1"],
        "descriptions": [
            "卫生间洗手池周围墙面与地砖整体泛黄褐偏色。",
            "白色陶瓷洗手池与马桶缺乏光泽，色彩欠饱和发暗。"
        ],
        "note": "视觉改判：卫生间洗手池周围墙面与地砖泛黄褐偏色且欠饱和 (D-L2, E2-L1)"
    },
    499: {
        "score": 2.36,
        "severities": ["D-L2", "F-L1"],
        "descriptions": [
            "餐桌上的白色餐盘与烤披萨表面泛浓重红棕暖偏色，纯白餐具质感丧失。",
            "披萨表面色调与餐具色彩混浊生硬。"
        ],
        "note": "视觉改判：餐桌白色餐盘与烤披萨表面泛浓重红棕暖偏色 (D-L2, F-L1)"
    },
    524: {
        "score": 2.43,
        "severities": ["E1-L2", "F-L1"],
        "descriptions": [
            "背景行人撑着的遮阳伞局部色彩过饱和浓艳。",
            "高饱和遮阳伞与灰暗背景脱节，视觉生硬违和。"
        ],
        "note": "视觉改判：背景行人撑着的遮阳伞局部色彩过饱和浓艳 (E1-L2, F-L1)"
    },
    528: {
        "score": 1.12,
        "severities": ["D-L3", "F-L3"],
        "descriptions": [
            "女网球运动员面部、手臂及球拍出现严重青绿杂色斑块与偏色。",
            "人物面部因严重伪色色斑导致视觉毁损不自然。"
        ],
        "note": "视觉改判：女网球运动员面部与手臂出现严重青绿杂色斑块与偏色 (D-L3, F-L3)"
    },
    543: {
        "score": 2.43,
        "severities": ["E1-L2", "F-L1"],
        "descriptions": [
            "餐盘中紫甘蓝生菜与西兰花局部过饱和浓艳。",
            "蔬菜高饱和度与暗沉肉类对比生硬，视觉自然度受损。"
        ],
        "note": "视觉改判：餐盘中紫甘蓝与西兰花局部过饱和浓艳 (E1-L2, F-L1)"
    },
    565: {
        "score": 2.47,
        "severities": ["E2-L2", "D-L1"],
        "descriptions": [
            "滑板场上少年们的服装与手持滑板大面积褪色泛灰发暗，欠饱和明显。",
            "全图整体色调偏黄灰沉闷。"
        ],
        "note": "视觉改判：滑板场上少年服装与滑板大面积褪色泛灰发暗 (E2-L2, D-L1)"
    },
    778: {
        "score": 2.43,
        "severities": ["D-L2", "E2-L1"],
        "descriptions": [
            "卫生间白色陶瓷小便池与瓷砖墙面整体泛黄褐色偏色。",
            "瓷砖与陶瓷表面缺乏自然明度，偏暗欠饱和。"
        ],
        "note": "视觉改判：卫生间白色陶瓷小便池与瓷砖墙面泛黄褐偏色 (D-L2, E2-L1)"
    },
    880: {
        "score": 2.25,
        "severities": ["E2-L2", "D-L1", "F-L1"],
        "descriptions": [
            "棒球场内野红土地面与球员白色球衣大面积褪色泛灰发暗。",
            "草坪与内野交界处色彩偏灰暗冷色。",
            "比赛场景整体色彩沉闷，活力感不足。"
        ],
        "note": "视觉改判：棒球场内野红土与球员白色球衣大面积褪色泛灰发暗 (E2-L2, D-L1, F-L1)"
    },
    891: {
        "score": 2.61,
        "severities": ["D-L2"],
        "descriptions": [
            "餐桌上的披萨托盘方格衬纸与披萨饼底整体泛黄褐暖偏色。"
        ],
        "note": "视觉改判：餐桌上的披萨托盘方格衬纸与饼底泛黄褐暖偏色 (D-L2)"
    },
    945: {
        "score": 2.47,
        "severities": ["E2-L2", "D-L1"],
        "descriptions": [
            "海面上航行的渔船船体与海面整体大面积泛灰褪色，欠饱和明显。",
            "天空与海面呈现轻度灰暗冷偏色。"
        ],
        "note": "视觉改判：海面上航行的渔船船体与海面整体大面积泛灰褪色 (E2-L2, D-L1)"
    }
}

DEFECT_NAMES = {
    "A": "缺色", "B": "溢色", "C": "错色", "D": "偏色",
    "E1": "过饱和", "E2": "欠饱和", "F": "视觉自然度"
}

def make_defect_list(severities, descriptions):
    defs = []
    for sev, desc in zip(severities, descriptions):
        code, level = sev.split("-") if "-" in sev else (sev, "")
        defs.append({
            "id": code,
            "name": DEFECT_NAMES.get(code, code),
            "severity": level,
            "description": desc
        })
    return defs

def main():
    # 1. Update grounding_remaining_batch_03.json
    with open(GROUNDING_FILE, "r", encoding="utf-8") as f:
        grounding_data = json.load(f)
    
    for t_idx, fix in B03_FIXES.items():
        grounding_data[str(t_idx)] = fix
    
    with open(GROUNDING_FILE, "w", encoding="utf-8") as f:
        json.dump(grounding_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {GROUNDING_FILE} with {len(B03_FIXES)} fixes.")

    # 2. Update reviewed_1_10000_all.json
    with open(EXPORTS_ALL, "r", encoding="utf-8") as f:
        data_all = json.load(f)
    
    for item in data_all["annotations"]:
        tid = item["human_review"]["task_id"]
        if tid in B03_FIXES:
            fix = B03_FIXES[tid]
            item["defects"] = make_defect_list(fix["severities"], fix["descriptions"])
            item["review_note"] = fix["note"]
            item["reviewed_score"] = 1.0 if any(s.startswith("A") for s in fix["severities"]) else None
            item["needs_rescoring"] = False if any(s.startswith("A") for s in fix["severities"]) else True
    
    with open(EXPORTS_ALL, "w", encoding="utf-8") as f:
        json.dump(data_all, f, ensure_ascii=False, indent=2)
    print(f"Updated {EXPORTS_ALL}.")

    # 3. Update reviewed_1_10000_clean.json
    with open(EXPORTS_CLEAN, "r", encoding="utf-8") as f:
        data_clean = json.load(f)
    
    for item in data_clean["annotations"]:
        tid = item["human_review"]["task_id"]
        if tid in B03_FIXES:
            fix = B03_FIXES[tid]
            item["defects"] = make_defect_list(fix["severities"], fix["descriptions"])
            item["review_note"] = ""
            item["reviewed_score"] = 1.0 if any(s.startswith("A") for s in fix["severities"]) else None
            item["needs_rescoring"] = False if any(s.startswith("A") for s in fix["severities"]) else True
            
    with open(EXPORTS_CLEAN, "w", encoding="utf-8") as f:
        json.dump(data_clean, f, ensure_ascii=False, indent=2)
    print(f"Updated {EXPORTS_CLEAN}.")

if __name__ == "__main__":
    main()
