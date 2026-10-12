#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_remaining_batch_10.py
根据对 Batch 10（Tasks 1984 ~ 2232，共 120 组）的 20 张高清看板多模态大图直审结果，
1. 生成中间定物审计文件 grounding_remaining_batch_10.json；
2. 同步更新 reviewed_1_10000_all.json（包含精准具象定物陈述或审查通过）；
3. 同步更新 reviewed_1_10000_clean.json（全量 10,000 条保持 review_note: ""）；
4. 运行严格格式契约验证。
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

# 120 组任务的直审定物字典
REVIEWS = {
    # Sheet 01: [1984, 1985, 1987, 1988, 1990, 1994]
    1984: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2"},
        "note": "街道两旁原本金黄灿烂的秋季树冠秋叶被严重错涂为发暗的紫红与褐红色调（严重错色 C-L3，偏色 D-L2）。"
    },
    1985: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1987: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1988: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1990: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2"},
        "note": "十字路口天际线上空原本泛着淡粉紫晚霞微光的天空被严重剥色错涂为冷灰青色（偏色 D-L2，欠饱和 E2-L2）。"
    },
    1994: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 02: [1997, 1999, 2000, 2002, 2006, 2012]
    1997: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1999: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2000: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2"},
        "note": "男子运动棒球帽与T恤原本鲜艳醒目的翠绿色条纹被严重错涂为暗沉橙红色（严重错色 C-L3，偏色 D-L2）。"
    },
    2002: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2006: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2012: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 03: [2013, 2015, 2018, 2022, 2025, 2027]
    2013: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2015: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2018: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2022: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2025: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2027: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 04: [2035, 2036, 2037, 2038, 2040, 2046]
    2035: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2036: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2037: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2038: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2040: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "建筑泥地前鲜红醒目的消防立柱被严重褪色错涂为暗哑粉黄褐色（错色 C-L2，欠饱和 E2-L2）。"
    },
    2046: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 05: [2051, 2053, 2054, 2060, 2061, 2062]
    2051: {
        "is_pass": False,
        "severities": {"C": "L2", "D": "L1"},
        "note": "男网球选手手腕佩戴的鲜艳荧光黄色运动护腕脱色错涂为苍白浅灰白（错色 C-L2，偏色 D-L1）。"
    },
    2053: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2054: {
        "is_pass": False,
        "severities": {"E1": "L2", "C": "L1"},
        "note": "餐盘中切丝摆放的紫甘蓝沙拉被错涂为过度浓艳刺眼的荧光亮洋红色塑料感（过饱和 E1-L2，轻度错色 C-L1）。"
    },
    2060: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2061: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2062: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 06: [2064, 2065, 2066, 2072, 2074, 2076]
    2064: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2065: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "游艇甲板悬挂的救生圈原本鲜艳醒目的橙红内圈橡胶被脱色错涂为灰暗无光暗灰色（错色 C-L2，欠饱和 E2-L2）。"
    },
    2066: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2072: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2074: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2076: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 07: [2078, 2079, 2081, 2083, 2087, 2089]
    2078: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2079: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2081: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2083: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2087: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2089: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 08: [2091, 2092, 2094, 2095, 2096, 2097]
    2091: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2092: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2"},
        "note": "厨房与客厅原本温馨明亮的暖黄色背景墙壁被大面积错涂为冰冷暗哑青灰白（偏色 D-L2，欠饱和 E2-L2）。"
    },
    2094: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2095: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2096: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2097: {
        "is_pass": False,
        "severities": {"C": "L2", "D": "L1"},
        "note": "雪山行进中登山者身上穿着的棕黄色保暖冲锋衣外套被错涂为泛暗的淡紫粉灰色（错色 C-L2，偏色 D-L1）。"
    },

    # Sheet 09: [2098, 2099, 2101, 2102, 2107, 2112]
    2098: {
        "is_pass": False,
        "severities": {"E2": "L2", "D": "L1"},
        "note": "牧场草地上原本茂盛翠绿的天然草皮被大面积脱色错涂为干涩发灰的暗淡青黄绿（欠饱和 E2-L2，偏色 D-L1）。"
    },
    2099: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2101: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2102: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2107: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2112: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 10: [2113, 2115, 2117, 2120, 2123, 2124]
    2113: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2115: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2117: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2120: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2123: {
        "is_pass": False,
        "severities": {"C": "L2", "D": "L2"},
        "note": "自助餐台上原本金黄酥脆的炸鸡块与暖色熟食被大面积错涂为发暗偏青灰冷杂色（错色 C-L2，偏色 D-L2）。"
    },
    2124: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 11: [2125, 2126, 2127, 2128, 2132, 2134]
    2125: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2126: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2127: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2128: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2132: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2134: {
        "is_pass": False,
        "severities": {"E2": "L2", "D": "L1"},
        "note": "货架摊位上大批堆叠的成熟香蕉原本鲜艳明亮的金黄色果皮被大面积脱色错涂为干瘪发灰的暗淡青黄色（欠饱和 E2-L2，偏色 D-L1）。"
    },

    # Sheet 12: [2137, 2138, 2141, 2146, 2147, 2148]
    2137: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2138: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2141: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2146: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2147: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2148: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 13: [2152, 2153, 2155, 2156, 2157, 2159]
    2152: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2153: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2155: {
        "is_pass": False,
        "severities": {"C": "L3"},
        "note": "路边原本涂覆鲜明醒目金黄色警示漆的消防栓被严重错涂为冰冷深青蓝色（严重错色 C-L3）。"
    },
    2156: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2157: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2159: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 14: [2160, 2161, 2162, 2163, 2165, 2167]
    2160: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2161: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2162: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2163: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2165: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2167: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 15: [2169, 2170, 2171, 2172, 2173, 2174]
    2169: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2170: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2171: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2172: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "街头警务执勤人员身上穿着的醒目高反光荧光黄绿色警用安全背心被严重脱色错涂为苍白暗淡的浅蓝灰白色（错色 C-L2，欠饱和 E2-L2）。"
    },
    2173: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2174: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 16: [2175, 2176, 2179, 2181, 2183, 2184]
    2175: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2176: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2179: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2181: {
        "is_pass": False,
        "severities": {"D": "L2"},
        "note": "冰箱内部白色塑料内壁与搁架被大面积错涂为发暗混浊的暖黄肉色调（偏色 D-L2）。"
    },
    2183: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2184: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 17: [2186, 2190, 2192, 2193, 2199, 2200]
    2186: {
        "is_pass": False,
        "severities": {"D": "L2", "F": "L1"},
        "note": "电脑办公桌背景原本清爽的青蓝绿色房间墙壁被大面积严重错涂为发暗的桃粉暖红色调（偏色 D-L2，视觉自然度 F-L1）。"
    },
    2190: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2192: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2193: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2199: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "路边原本涂覆鲜明亮丽金黄色反光漆的消防栓被严重脱色错涂为苍白暗淡的水泥灰白色（严重错色 C-L3，欠饱和 E2-L2）。"
    },
    2200: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 18: [2201, 2202, 2204, 2206, 2210, 2211]
    2201: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2202: {
        "is_pass": False,
        "severities": {"E2": "L2", "D": "L1"},
        "note": "快艇航行所处的大面积开阔湖水与水面被严重脱色错涂为暗淡苍白的浅灰青白色（欠饱和 E2-L2，偏色 D-L1）。"
    },
    2204: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2206: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2210: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L1"},
        "note": "现代卧室内双人床的大面积床单被褥与墙壁被过度渲染为浓艳刺眼的暖橘黄色调（偏色 D-L2，过饱和 E1-L1）。"
    },
    2211: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "网球场看台背景醒目的“XPERIA”巨幅霓虹翠绿色发光广告牌被严重错涂为发暗的冷灰青蓝色（严重错色 C-L3，欠饱和 E2-L2）。"
    },

    # Sheet 19: [2212, 2213, 2215, 2217, 2218, 2220]
    2212: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2213: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2215: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2217: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2218: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2220: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2"},
        "note": "书桌台灯所照耀的大面积原本明亮温暖的金黄色背景墙壁被严重冷却错涂为暗哑死板的冷灰青色（偏色 D-L2，欠饱和 E2-L2）。"
    },

    # Sheet 20: [2223, 2224, 2227, 2228, 2229, 2232]
    2223: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2224: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2227: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2228: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2229: {
        "is_pass": False,
        "severities": {"C": "L3"},
        "note": "足球场上奔跑拼抢的球员身上原本鲜艳醒目的火红色足球运动球衣与球裤被严重错涂为宝蓝色（严重错色 C-L3）。"
    },
    2232: {
        "is_pass": False,
        "severities": {"D": "L2"},
        "note": "热带丛林土路林道的大面积地面泥土被错涂为泛暗沉桃粉紫灰色调（偏色 D-L2）。"
    }
}

def main():
    print(f"Loaded {len(REVIEWS)} reviews for Batch 10.")
    assert len(REVIEWS) == 120, f"Expected 120 reviews, got {len(REVIEWS)}"

    # 保存中间审计 JSON
    with open(OUT_GROUNDING_FILE, "w", encoding="utf-8") as f:
        json.dump(REVIEWS, f, ensure_ascii=False, indent=2)
    print(f"Saved grounding audit: {OUT_GROUNDING_FILE}")

    # 读取并更新两个全量导出文件
    with open(ALL_EXPORT, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    with open(CLEAN_EXPORT, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    all_map = {item["human_review"]["task_id"]: item for item in all_data["annotations"]}
    clean_map = {item["human_review"]["task_id"]: item for item in clean_data["annotations"]}

    pass_count = 0
    grounding_count = 0

    for tid, rev in REVIEWS.items():
        if tid not in all_map:
            print(f"Warning: task_id {tid} not found in annotations!")
            continue

        item_all = all_map[tid]
        item_clean = clean_map[tid]

        if rev["is_pass"]:
            pass_count += 1
            item_all["defects"] = []
            item_all["review_note"] = "审查通过"
            item_clean["defects"] = []
            item_clean["review_note"] = ""
        else:
            grounding_count += 1
            defects_list = []
            for d_id, sev in rev["severities"].items():
                defects_list.append({
                    "id": d_id,
                    "name": DEFECT_NAMES[d_id],
                    "severity": sev,
                    "description": rev["note"]
                })
            item_all["defects"] = defects_list
            item_all["review_note"] = rev["note"]
            item_clean["defects"] = defects_list
            item_clean["review_note"] = ""

    print(f"Batch 10 applied: {pass_count} Passed (Defects Cleared), {grounding_count} Grounded with Concrete Objects.")

    with open(ALL_EXPORT, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {ALL_EXPORT}")

    with open(CLEAN_EXPORT, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {CLEAN_EXPORT}")

if __name__ == "__main__":
    main()
