# -*- coding: utf-8 -*-
"""
apply_b04_strict.py:
Strictly apply physical grounding to the 18 violation tasks in Batch 04,
updating grounding_remaining_batch_04.json, reviewed_1_10000_all.json, and reviewed_1_10000_clean.json.
"""

import json
from pathlib import Path

GROUNDING_FILE = Path("LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_04.json")
EXPORTS_ALL = Path("LS_lcad_reviewer/exports/reviewed_1_10000_all.json")
EXPORTS_CLEAN = Path("LS_lcad_reviewer/exports/reviewed_1_10000_clean.json")

B04_FIXES = {
    958: {
        "score": 1.44,
        "severities": ["F-L3"],
        "descriptions": [
            "沙漠沙丘交界处天空存在明显的弧形拼接错位与断层瑕疵。"
        ],
        "note": "视觉改判：沙漠沙丘交界处天空存在明显的弧形拼接错位与断层瑕疵 (F-L3)"
    },
    1007: {
        "score": 5.0,
        "severities": ["D-L1"],
        "descriptions": [
            "远景雪山山峦与近处地面整体泛微暖黄偏色。"
        ],
        "note": "视觉改判：远景雪山山峦与近处地面整体泛微暖黄偏色 (D-L1)"
    },
    1011: {
        "score": 4.46,
        "severities": ["D-L1"],
        "descriptions": [
            "街道两侧红砖建筑墙体与柏油马路整体泛冷青蓝偏色。"
        ],
        "note": "视觉改判：街道两侧红砖建筑墙体与柏油马路整体泛冷青蓝偏色 (D-L1)"
    },
    1017: {
        "score": 5.0,
        "severities": ["D-L1", "E2-L1"],
        "descriptions": [
            "餐桌台面整体泛暖偏黄，切片西瓜与青菜段色调受轻度环境偏色影响。",
            "餐盘中的切片西瓜与绿色芹菜色泽偏浅发白，饱和度轻度不足。"
        ],
        "note": "视觉改判：餐桌台面整体泛暖偏黄且切片西瓜与青菜色泽偏浅欠饱和 (D-L1, E2-L1)"
    },
    1031: {
        "score": 5.0,
        "severities": ["D-L1", "E2-L1"],
        "descriptions": [
            "室内背景木栅栏与整体环境光泛冷青蓝偏色。",
            "小女孩身穿的红色羽绒服色泽发暗，饱和度明显不足。"
        ],
        "note": "视觉改判：室内木栅栏环境泛冷偏青且小女孩红色羽绒服饱和度不足 (D-L1, E2-L1)"
    },
    1036: {
        "score": 5.0,
        "severities": ["D-L1"],
        "descriptions": [
            "猫咪胸口与下颚的白色毛发及背景木墙整体泛暖偏黄。"
        ],
        "note": "视觉改判：猫咪胸口与下颚白色毛发及背景木墙整体泛暖偏黄 (D-L1)"
    },
    1050: {
        "score": 1.07,
        "severities": ["E2-L2", "D-L2"],
        "descriptions": [
            "芦苇丛中的猎人衣着及身旁的两只猎犬皮毛严重褪色泛灰褐，缺乏暖金色彩层次。",
            "全图整体色调由原本金暖调严重退化为灰褐单调色偏。"
        ],
        "note": "视觉改判：芦苇丛中猎人衣着与猎犬皮毛褪色泛灰褐且全图色偏严重 (E2-L2, D-L2)"
    },
    1054: {
        "score": 5.0,
        "severities": ["D-L1"],
        "descriptions": [
            "办公室背景墙面与男子的浅色衬衫整体泛冷青蓝偏色。"
        ],
        "note": "视觉改判：办公室背景墙面与男子浅色衬衫泛冷青蓝偏色 (D-L1)"
    },
    1055: {
        "score": 2.17,
        "severities": ["D-L2", "C-L1"],
        "descriptions": [
            "夜景户外台阶与金属扶手大面积泛暖红黄偏色。",
            "夜空原本纯净深蓝被涂染为混浊暖暗色，违背夜景常理。"
        ],
        "note": "视觉改判：夜景户外台阶扶手泛暖红黄偏色且夜空常识失真 (D-L2, C-L1)"
    },
    1066: {
        "score": 2.27,
        "severities": ["E2-L2", "F-L1"],
        "descriptions": [
            "公路上行走的两名行人服装色彩发灰褪色，缺乏活力。",
            "柏油路面色泽暗淡且行人与背景色彩融合度下降。"
        ],
        "note": "视觉改判：公路上行走的行人服装色彩发灰褪色且路面质感欠佳 (E2-L2, F-L1)"
    },
    1069: {
        "score": 2.56,
        "severities": ["E1-L2", "F-L1"],
        "descriptions": [
            "切开的紫甘蓝内部切面紫蓝色过于浓艳，高饱和溢出。",
            "胡萝卜与紫甘蓝局部色彩对比过强，视觉生硬。"
        ],
        "note": "视觉改判：切开的紫甘蓝切面紫蓝色过饱和浓艳 (E1-L2, F-L1)"
    },
    1074: {
        "score": 2.56,
        "severities": ["E1-L2", "F-L1"],
        "descriptions": [
            "红色复古皮卡车漆饱和度过高，红色高光溢出浓艳。",
            "高饱和车漆反光边缘较硬，视觉自然度轻度受损。"
        ],
        "note": "视觉改判：红色复古皮卡车漆过饱和浓艳且高光溢出 (E1-L2, F-L1)"
    },
    1076: {
        "score": 2.17,
        "severities": ["D-L2", "E1-L1", "F-L1"],
        "descriptions": [
            "马匹面部皮毛与马具缰绳局部泛异常粉红偏色。",
            "背景树木与古堡城墙色彩过浓，饱和度略显过高。",
            "马匹毛色与背景色彩过渡生硬，视觉自然度下降。"
        ],
        "note": "视觉改判：马匹面部皮毛泛异常粉红偏色且背景色彩过浓 (D-L2, E1-L1, F-L1)"
    },
    1088: {
        "score": 2.47,
        "severities": ["D-L2", "F-L1"],
        "descriptions": [
            "室内背景墙面与白色相框整体泛粉红紫偏色。",
            "绿叶盆栽摆件边缘色调不自然，色彩融合度欠佳。"
        ],
        "note": "视觉改判：室内背景墙面与白色相框泛粉红紫偏色 (D-L2, F-L1)"
    },
    1094: {
        "score": 2.47,
        "severities": ["D-L1", "F-L1"],
        "descriptions": [
            "客厅室内墙面与窗户整体偏向浑浊黄暖偏色。",
            "室内灯光与窗外夜景交界处色彩层次生硬，不够自然。"
        ],
        "note": "视觉改判：客厅室内墙面与窗外夜景泛浑浊黄暖偏色 (D-L1, F-L1)"
    },
    1107: {
        "score": 2.27,
        "severities": ["E2-L2", "F-L1"],
        "descriptions": [
            "厨房白色厨柜面板与微波炉严重泛灰发暗，欠饱和明显。",
            "室内整体光影发闷，视觉自然度轻度下降。"
        ],
        "note": "视觉改判：厨房白色厨柜与微波炉发灰暗淡欠饱和 (E2-L2, F-L1)"
    },
    1112: {
        "score": 2.23,
        "severities": ["D-L2", "E2-L1"],
        "descriptions": [
            "窗边停放的摩托车金属车身及室内地面泛红褐色偏色。",
            "摩托车金属反光与车轮橡胶缺乏正常光泽，略显发灰欠饱和。"
        ],
        "note": "视觉改判：窗边摩托车金属车身与地面泛红褐偏色且欠饱和 (D-L2, E2-L1)"
    },
    1115: {
        "score": 2.24,
        "severities": ["D-L1", "E2-L1"],
        "descriptions": [
            "卧室墙面由原青蓝色偏移为泛黄发灰偏色。",
            "木质床头柜与床铺色彩欠饱和发暗。"
        ],
        "note": "视觉改判：卧室墙面泛黄发灰偏色且床头柜色彩欠饱和 (D-L1, E2-L1)"
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
    # 1. Update grounding_remaining_batch_04.json
    with open(GROUNDING_FILE, "r", encoding="utf-8") as f:
        grounding_data = json.load(f)
    
    for t_idx, fix in B04_FIXES.items():
        grounding_data[str(t_idx)] = fix
    
    with open(GROUNDING_FILE, "w", encoding="utf-8") as f:
        json.dump(grounding_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {GROUNDING_FILE} with {len(B04_FIXES)} fixes.")

    # 2. Update reviewed_1_10000_all.json
    with open(EXPORTS_ALL, "r", encoding="utf-8") as f:
        data_all = json.load(f)
    
    for item in data_all["annotations"]:
        tid = item["human_review"]["task_id"]
        if tid in B04_FIXES:
            fix = B04_FIXES[tid]
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
        if tid in B04_FIXES:
            fix = B04_FIXES[tid]
            item["defects"] = make_defect_list(fix["severities"], fix["descriptions"])
            item["review_note"] = ""
            item["reviewed_score"] = 1.0 if any(s.startswith("A") for s in fix["severities"]) else None
            item["needs_rescoring"] = False if any(s.startswith("A") for s in fix["severities"]) else True
            
    with open(EXPORTS_CLEAN, "w", encoding="utf-8") as f:
        json.dump(data_clean, f, ensure_ascii=False, indent=2)
    print(f"Updated {EXPORTS_CLEAN}.")

if __name__ == "__main__":
    main()
