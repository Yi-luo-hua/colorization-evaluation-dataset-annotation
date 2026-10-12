# -*- coding: utf-8 -*-
"""
apply_b02_strict.py:
Strictly apply physical grounding to the 16 violation tasks in Batch 02,
updating grounding_remaining_batch_02.json, reviewed_1_10000_all.json, and reviewed_1_10000_clean.json.
"""

import json
from pathlib import Path

GROUNDING_FILE = Path("LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_02.json")
EXPORTS_ALL = Path("LS_lcad_reviewer/exports/reviewed_1_10000_all.json")
EXPORTS_CLEAN = Path("LS_lcad_reviewer/exports/reviewed_1_10000_clean.json")

B02_FIXES = {
    250: {
        "score": 2.30,
        "severities": ["D-L2", "E2-L1"],
        "descriptions": [
            "男模特身穿的风衣与手持棕色皮包整体泛黄褐暖偏色。",
            "背景城市建筑与天空夕阳色彩欠饱和发灰。"
        ],
        "note": "视觉改判：男模特风衣手包泛黄褐暖偏色且背景建筑欠饱和 (D-L2, E2-L1)"
    },
    290: {
        "score": 2.43,
        "severities": ["E2-L2", "D-L1"],
        "descriptions": [
            "十字路口的红色公交车车身严重褪色泛灰发暗，欠饱和明显。",
            "雨天湿滑的柏油路面及天空整体泛黄绿偏色。"
        ],
        "note": "视觉改判：红色公交车车身严重褪色泛灰发暗且路面泛黄绿偏色 (E2-L2, D-L1)"
    },
    315: {
        "score": 2.43,
        "severities": ["E2-L2", "F-L1"],
        "descriptions": [
            "空中飞行的红色滑翔伞伞翼色泽发暗褪色，欠饱和明显。",
            "滑翔伞伞翼与背景天空边缘生硬，视觉自然度轻度受损。"
        ],
        "note": "视觉改判：空中飞行的红色滑翔伞伞翼色泽发暗褪色 (E2-L2, F-L1)"
    },
    317: {
        "score": 2.61,
        "severities": ["D-L2"],
        "descriptions": [
            "黄色消防栓周围的柏油马路与水泥路沿整体泛冷青绿偏色。"
        ],
        "note": "视觉改判：黄色消防栓周围柏油马路与水泥地面泛冷青绿偏色 (D-L2)"
    },
    319: {
        "score": 2.36,
        "severities": ["D-L2", "F-L1"],
        "descriptions": [
            "浅滩水边水面与泥沙泛混浊灰褐偏色，水面自然反光色彩丧失。",
            "黑鸟羽毛光泽暗淡，整体场景缺乏生机层次。"
        ],
        "note": "视觉改判：浅滩水边水面与泥沙泛混浊灰褐偏色 (D-L2, F-L1)"
    },
    321: {
        "score": 2.25,
        "severities": ["E1-L2", "F-L1"],
        "descriptions": [
            "草地上停放的小型拖车车厢过饱和荧光绿且与枯树环境色彩脱节。",
            "车厢鲜绿与枯树黄草反差剧烈，视觉自然度下降。"
        ],
        "note": "视觉改判：草地上停放的小型拖车车厢过饱和荧光绿刺眼 (E1-L2, F-L1)"
    },
    329: {
        "score": 2.61,
        "severities": ["D-L2"],
        "descriptions": [
            "卧室背景墙面与书架阴影区域泛冷暗紫灰偏色，暖粉灯光氛围受损。"
        ],
        "note": "视觉改判：卧室背景墙面与书架阴影泛冷暗紫灰偏色 (D-L2)"
    },
    343: {
        "score": 2.56,
        "severities": ["E2-L2", "F-L1"],
        "descriptions": [
            "铁轨上停放的蓝白相间火车车厢与站台路基色彩褪色发灰，欠饱和明显。",
            "全图整体缺乏光泽，色彩平淡发闷。"
        ],
        "note": "视觉改判：铁轨上停放的蓝白相间火车车厢与站台色彩褪色发灰 (E2-L2, F-L1)"
    },
    347: {
        "score": 2.47,
        "severities": ["E2-L2", "D-L1"],
        "descriptions": [
            "靠在木栏上的多副滑雪板板面严重褪色泛灰，原本蓝色涂装欠饱和发暗。",
            "木质栏杆及背景墙面泛黄褐微偏色。"
        ],
        "note": "视觉改判：多副滑雪板板面严重褪色泛灰且木栏泛黄褐偏色 (E2-L2, D-L1)"
    },
    354: {
        "score": 2.47,
        "severities": ["D-L2", "F-L1"],
        "descriptions": [
            "红土网球场地面偏暗泛黄且女运动员肢体皮肤泛红灰偏色。",
            "红土地面与背景广告挡板色彩对比失真，视觉自然度受损。"
        ],
        "note": "视觉改判：红土网球场地面偏暗泛黄且女运动员肢体泛红灰偏色 (D-L2, F-L1)"
    },
    357: {
        "score": 2.73,
        "severities": ["E1-L2"],
        "descriptions": [
            "汹涌海浪中冲浪者脚下的黄色冲浪板与近处海水色彩过饱和浓艳。"
        ],
        "note": "视觉改判：汹涌海浪中冲浪者黄色冲浪板与海水过饱和浓艳 (E1-L2)"
    },
    360: {
        "score": 2.43,
        "severities": ["E2-L2", "F-L1"],
        "descriptions": [
            "窗前趴着的黑猫皮毛与木质窗台严重暗淡发灰，欠饱和且光影发闷。",
            "自然采光层次丧失，视觉自然度下降。"
        ],
        "note": "视觉改判：窗前趴着的黑猫皮毛与木质窗台严重暗淡发灰 (E2-L2, F-L1)"
    },
    368: {
        "score": 2.17,
        "severities": ["E2-L2", "D-L1", "F-L1"],
        "descriptions": [
            "动物园草地植被与长颈鹿皮毛整体严重发灰褪色，欠饱和明显。",
            "远景棕榈树与天空泛暗灰冷偏色。",
            "整幅画面色彩发闷发灰，视觉真实感下降。"
        ],
        "note": "视觉改判：动物园草地植被与长颈鹿皮毛严重发灰褪色 (E2-L2, D-L1, F-L1)"
    },
    385: {
        "score": 2.26,
        "severities": ["B-L2", "F-L1"],
        "descriptions": [
            "餐桌上的彩绘气球表面多种颜料互相溢色混浊且边缘过渡脏污。",
            "彩绘气球质感与电吹风反光生硬违和。"
        ],
        "note": "视觉改判：餐桌上的彩绘气球表面多种颜料互相溢色混浊 (B-L2, F-L1)"
    },
    389: {
        "score": 2.36,
        "severities": ["D-L2", "F-L1"],
        "descriptions": [
            "卫生间白色陶瓷洗手台与马桶被异常涂染为粉紫偏色。",
            "蓝色墙面与粉紫陶瓷台面交界处色彩突兀不自然。"
        ],
        "note": "视觉改判：卫生间白色陶瓷洗手台与马桶异常涂染为粉紫偏色 (D-L2, F-L1)"
    },
    398: {
        "score": 2.17,
        "severities": ["D-L2", "E2-L1", "F-L1"],
        "descriptions": [
            "动物园斑马黑白条纹与假山沙地整体泛黄褐色偏色。",
            "背景树木植被色彩发灰暗淡，欠饱和。",
            "全图被单一土黄色调笼罩，色彩层次单调。"
        ],
        "note": "视觉改判：动物园斑马黑白条纹与假山沙地泛黄褐色偏色 (D-L2, E2-L1, F-L1)"
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
    # 1. Update grounding_remaining_batch_02.json
    with open(GROUNDING_FILE, "r", encoding="utf-8") as f:
        grounding_data = json.load(f)
    
    for t_idx, fix in B02_FIXES.items():
        grounding_data[str(t_idx)] = fix
    
    with open(GROUNDING_FILE, "w", encoding="utf-8") as f:
        json.dump(grounding_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {GROUNDING_FILE} with {len(B02_FIXES)} fixes.")

    # 2. Update reviewed_1_10000_all.json
    with open(EXPORTS_ALL, "r", encoding="utf-8") as f:
        data_all = json.load(f)
    
    for item in data_all["annotations"]:
        tid = item["human_review"]["task_id"]
        if tid in B02_FIXES:
            fix = B02_FIXES[tid]
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
        if tid in B02_FIXES:
            fix = B02_FIXES[tid]
            item["defects"] = make_defect_list(fix["severities"], fix["descriptions"])
            item["review_note"] = ""
            item["reviewed_score"] = 1.0 if any(s.startswith("A") for s in fix["severities"]) else None
            item["needs_rescoring"] = False if any(s.startswith("A") for s in fix["severities"]) else True
            
    with open(EXPORTS_CLEAN, "w", encoding="utf-8") as f:
        json.dump(data_clean, f, ensure_ascii=False, indent=2)
    print(f"Updated {EXPORTS_CLEAN}.")

if __name__ == "__main__":
    main()
