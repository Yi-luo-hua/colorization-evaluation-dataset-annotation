#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reapply_batch_10_strict.py
执行“双重硬门槛放行准则”严格回溯重审 Batch 10：
纠正原先放行宽松滑坡问题，将 28 例误放行低分/高色差样本改判为精准具象实体定物。
更新产物：
1. grounding_remaining_batch_10.json
2. reviewed_1_10000_all.json
3. reviewed_1_10000_clean.json
"""

import json
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
AUDITS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits"
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"

ALL_EXPORT = EXPORTS_DIR / "reviewed_1_10000_all.json"
CLEAN_EXPORT = EXPORTS_DIR / "reviewed_1_10000_clean.json"
OUT_GROUNDING_FILE = AUDITS_DIR / "grounding_remaining_batch_10.json"

DEFECT_NAMES = {
    "A": "缺色",
    "B": "溢色",
    "C": "错色",
    "D": "偏色",
    "E1": "过饱和",
    "E2": "欠饱和",
    "F": "视觉自然度"
}

# 28 例重审后明确具体受损物体的定物字典
NEW_GROUNDINGS = {
    1987: {
        "severities": {"D": "L2", "E2": "L2"},
        "note": "复古做旧老照片中大象原本带有温暖橙黄色泽的皮毛与背景地面被大面积剥色，错涂为冰冷暗淡的发青灰白色（中度偏色 D-L2，中度欠饱和 E2-L2）。"
    },
    1994: {
        "severities": {"D": "L2", "F": "L1"},
        "note": "夜景街道背景原本受金黄色泛光照明的大楼外墙被严重冷却错涂为暗淡青冷灰色，破坏夜景真实暖光氛围（中度偏色 D-L2，轻度自然度受损 F-L1）。"
    },
    1999: {
        "severities": {"D": "L2"},
        "note": "男子自拍肖像背景原本清爽的浅青绿色室内墙面被大面积错涂为浑浊暗黄肉色调（中度偏色 D-L2）。"
    },
    2006: {
        "severities": {"F": "L2", "D": "L2"},
        "note": "烘焙操作台面木质桌板下半部突兀出现大面积发霉般的异常青蓝紫色杂色色斑，严重破坏木纹自然质感（中度自然度受损 F-L2，中度偏色 D-L2）。"
    },
    2015: {
        "severities": {"C": "L2", "D": "L2", "E2": "L2"},
        "note": "复古做旧照片中背景原本泛着柔和棕黄色调的草木背景被严重错涂为生硬突兀的翠绿色，男孩服饰脱色泛青灰（中度错色 C-L2，中度偏色 D-L2，中度欠饱和 E2-L2）。"
    },
    2018: {
        "severities": {"F": "L2", "C": "L1"},
        "note": "商用冷柜上方原本中性透明的塑料顶棚与金属边框被异常错染为大片不自然的深红紫色色晕（中度自然度受损 F-L2，轻度错色 C-L1）。"
    },
    2025: {
        "severities": {"C": "L2", "D": "L1"},
        "note": "餐桌玻璃杯中原本鲜艳诱人的橙黄色鲜榨果汁被严重错涂为发暗的灰绿色液体（中度错色 C-L2，轻度偏色 D-L1）。"
    },
    2038: {
        "severities": {"D": "L2", "F": "L1"},
        "note": "公园木质长椅上方原本清澈纯净的淡蓝色白天晴空被大面积错涂为不自然泛紫红的虚假霞光色斑（中度偏色 D-L2，轻度自然度受损 F-L1）。"
    },
    2064: {
        "severities": {"C": "L2", "D": "L1"},
        "note": "客厅墙面悬挂的原本纯正鲜红色KEEP CALM标语海报被错涂为暗哑发紫的深桃红色（中度错色 C-L2，轻度偏色 D-L1）。"
    },
    2066: {
        "severities": {"D": "L2", "F": "L1"},
        "note": "足球场背景原本茂盛青翠的树冠枝叶被大面积错染为发暗的红褐色与杂乱紫斑（中度偏色 D-L2，轻度自然度受损 F-L1）。"
    },
    2072: {
        "severities": {"D": "L1"},
        "note": "餐桌背景的水果沙拉杯与草莓色彩偏暗偏浊（轻度偏色 D-L1）。"
    },
    2076: {
        "severities": {"C": "L2", "E2": "L2"},
        "note": "滑板场墙面上原本鲜艳醒目的金黄色街头涂鸦大字被严重错涂为暗淡青紫冷色，地面色彩褪色泛灰（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },
    2089: {
        "severities": {"D": "L2", "E2": "L2"},
        "note": "乡间小路原本浓烈明亮的傍晚日落金黄色逆光环境被严重削弱，泥土道路与耕牛皮毛大面积褪色错涂为冷暗灰白调（中度偏色 D-L2，中度欠饱和 E2-L2）。"
    },
    2094: {
        "severities": {"E2": "L1", "D": "L1"},
        "note": "餐盘中剖开的烤红薯金黄色果肉被脱色暗淡，错涂为缺乏食欲的发干暗黄色（轻度欠饱和 E2-L1，轻度偏色 D-L1）。"
    },
    2096: {
        "severities": {"E2": "L2", "D": "L1"},
        "note": "广阔草坪原本生机盎然的青翠绿意被大面积褪色发白，错涂为干涩暗淡的浅青冷灰色，小女孩紫红运动裤色彩退化（中度欠饱和 E2-L2，轻度偏色 D-L1）。"
    },
    2099: {
        "severities": {"C": "L2", "D": "L1"},
        "note": "棒球赛场看台观众身上穿的原本鲜艳红色球服被错涂为暗紫红与杂色色晕（中度错色 C-L2，轻度偏色 D-L1）。"
    },
    2112: {
        "severities": {"D": "L2", "E2": "L2"},
        "note": "房间右侧台灯原本极其温馨明亮的金黄色照明暖光被完全冷却，错涂为惨白刺眼的冷光，导致冰箱侧壁暖光映射完全丧失（中度偏色 D-L2，中度欠饱和 E2-L2）。"
    },
    2125: {
        "severities": {"C": "L3", "D": "L2"},
        "note": "街头左侧原本金黄色调的艺术涂鸦墙面被大面积错涂为青绿色，右侧时尚女郎海报背景错涂为冷暗深蓝紫色（严重错色 C-L3，中度偏色 D-L2）。"
    },
    2128: {
        "severities": {"D": "L1"},
        "note": "开放式厨房天花板与背景原本温暖的浅黄乳胶漆墙面被轻度冷却泛白（轻度偏色 D-L1）。"
    },
    2132: {
        "severities": {"D": "L2", "E2": "L2"},
        "note": "卫生间淋浴区与洗漱台大面积原本带有暖黄色泽的瓷砖与浴帘被严重脱色错涂为冷灰青色（中度偏色 D-L2，中度欠饱和 E2-L2）。"
    },
    2138: {
        "severities": {"C": "L2", "D": "L2"},
        "note": "客厅窗外原本晴朗清澈的淡蓝色白天晴空被大面积错涂为不自然浑浊的紫红泛光杂色（中度错色 C-L2，中度偏色 D-L2）。"
    },
    2146: {
        "severities": {"C": "L2", "D": "L2"},
        "note": "公厕洗手间原本清澈淡雅的浅水鸭青色瓷砖墙面被严重错涂为浓重深沉的钴蓝色调（中度错色 C-L2，中度偏色 D-L2）。"
    },
    2152: {
        "severities": {"C": "L2", "E2": "L2"},
        "note": "烘焙传送带上滚落的原本金黄酥脆的油炸小面包圈被严重脱色错涂为苍白暗淡的浅灰青色，丧失新鲜烘焙熟食固有色泽（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },
    2161: {
        "severities": {"C": "L2", "F": "L1"},
        "note": "西餐盘中原本焦香深红褐色的熟培根肉片被错涂为生肉般违和失真的浅粉紫红色（中度错色 C-L2，轻度自然度受损 F-L1）。"
    },
    2167: {
        "severities": {"D": "L2", "F": "L1"},
        "note": "家庭客厅原本米白色的室内天花板与墙面大面积泛出突兀失真的桃红紫色杂色光晕（中度偏色 D-L2，轻度自然度受损 F-L1）。"
    },
    2169: {
        "severities": {"D": "L2", "E2": "L2"},
        "note": "阅览室室内原本温暖的木质书架与电脑桌椅被大面积脱色错涂为冷暗青灰色（中度偏色 D-L2，中度欠饱和 E2-L2）。"
    },
    2174: {
        "severities": {"C": "L3", "E2": "L2"},
        "note": "户外草地上停放的原本鲜红醒目的红色厢式卡车车身被严重脱色错涂为暗淡灰白色，周边绿草地大面积褪色泛灰（严重错色 C-L3，中度欠饱和 E2-L2）。"
    },
    2218: {
        "severities": {"C": "L1", "D": "L1"},
        "note": "餐桌上卡通餐垫原本鲜艳红润的西瓜切片图案被轻度错涂为发暗淡粉红色（轻度错色 C-L1，轻度偏色 D-L1）。"
    }
}

def main():
    with open(OUT_GROUNDING_FILE, "r", encoding="utf-8") as f:
        reviews = json.load(f)

    print(f"Original Batch 10 reviews count: {len(reviews)}")

    # 应用 28 例重审改判
    for tid, info in NEW_GROUNDINGS.items():
        tid_str = str(tid)
        reviews[tid_str] = {
            "is_pass": False,
            "severities": info["severities"],
            "note": info["note"]
        }

    with open(OUT_GROUNDING_FILE, "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)
    print(f"Updated intermediate audit: {OUT_GROUNDING_FILE}")

    # 读取并同步至全量交付文件
    with open(ALL_EXPORT, "r", encoding="utf-8") as f:
        all_data = json.load(f)
    with open(CLEAN_EXPORT, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    all_map = {item["human_review"]["task_id"]: item for item in all_data["annotations"]}
    clean_map = {item["human_review"]["task_id"]: item for item in clean_data["annotations"]}

    for tid, info in NEW_GROUNDINGS.items():
        item_all = all_map[tid]
        item_clean = clean_map[tid]
        defects_list = []
        for d_id, sev in info["severities"].items():
            defects_list.append({
                "id": d_id,
                "name": DEFECT_NAMES[d_id],
                "severity": sev,
                "description": info["note"]
            })
        item_all["defects"] = defects_list
        item_all["review_note"] = info["note"]
        item_clean["defects"] = defects_list
        item_clean["review_note"] = ""

    with open(ALL_EXPORT, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {ALL_EXPORT}")

    with open(CLEAN_EXPORT, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {CLEAN_EXPORT}")

    pass_cnt = sum(1 for r in reviews.values() if r.get("is_pass"))
    ground_cnt = len(reviews) - pass_cnt
    print(f"Batch 10 Strict Re-review Complete: {ground_cnt} Grounded, {pass_cnt} Passed (Ratio: {pass_cnt/len(reviews)*100:.1f}%).")

if __name__ == "__main__":
    main()
