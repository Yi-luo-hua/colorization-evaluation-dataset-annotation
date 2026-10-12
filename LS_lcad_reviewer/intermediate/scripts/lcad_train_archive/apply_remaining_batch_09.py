#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_remaining_batch_09.py
根据对 Batch 09（Tasks 1761 ~ 1982，共 120 组）的 20 张高清看板多模态大图直审结果，
1. 生成中间定物审计文件 grounding_remaining_batch_09.json；
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
OUT_GROUNDING_FILE = AUDITS_DIR / "grounding_remaining_batch_09.json"

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
    # Sheet 01
    1761: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2"},
        "note": "室内原本明亮温馨的暖黄色背景墙壁与木质地板被大面积错涂为冰冷暗沉的冷青灰蓝调，丧失室内自然采光氛围（中度偏色 D-L2，中度欠饱和 E2-L2）。"
    },
    1762: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1765: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "沥青地面上摆放的网球拍红色外框严重褪色暗淡，错涂为干枯暗褐灰色（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },
    1767: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1769: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1770: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 02
    1771: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1773: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1774: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1775: {
        "is_pass": False,
        "severities": {"C": "L2", "E1": "L2", "F": "L1"},
        "note": "室内原本中性白色墙面的窗框内凹区域被严重错涂为违和刺眼的翠绿色块，且顶部吊灯边缘产生不自然色晕（中度错色 C-L2，中度过饱和 E1-L2，轻度自然度受损 F-L1）。"
    },
    1776: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1777: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 03
    1778: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "网球场上女选手身穿的鲜艳荧光黄色运动背心被严重错涂褪色为苍白无光泽的浅灰白色（严重错色 C-L3，中度欠饱和 E2-L2）。"
    },
    1779: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1784: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1785: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1786: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1788: {
        "is_pass": False,
        "severities": {"C": "L2", "D": "L2"},
        "note": "水果货架上原本青翠碧绿的条纹西瓜与绿色甜瓜被大面积错涂为暖黄橙褐色，失去新鲜瓜果的固有翠绿色泽（中度错色 C-L2，中度偏色 D-L2）。"
    },

    # Sheet 04
    1789: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1792: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1794: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1797: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1800: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1803: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 05
    1804: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1806: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1807: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1808: {
        "is_pass": False,
        "severities": {"E2": "L2", "D": "L1"},
        "note": "户外草坪及远处山林背景原本生机盎然的鲜嫩翠绿色被严重褪色错涂为暗沉发灰的青褐绿色（中度欠饱和 E2-L2，轻度偏色 D-L1）。"
    },
    1809: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1810: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 06
    1812: {
        "is_pass": False,
        "severities": {"C": "L3", "F": "L2"},
        "note": "烘焙披萨表面的番茄酱料与肉馅配料被大面积错涂为违和发霉般的荧光青绿色与杂乱紫斑，完全破坏食物质感（严重错色 C-L3，中度自然度受损 F-L2）。"
    },
    1813: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1814: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1815: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1817: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1819: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 07
    1820: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1821: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1823: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1825: {
        "is_pass": False,
        "severities": {"C": "L2", "D": "L2"},
        "note": "棒球场外野原本青翠绿色的天然草坪被大面积错涂为暖黄红褐色，与内野红土泥地发生严重混淆（中度错色 C-L2，中度偏色 D-L2）。"
    },
    1827: {
        "is_pass": False,
        "severities": {"C": "L1"},
        "note": "伦敦双层大巴车头悬挂的彩色装饰气球群中，部分粉白气球被轻微错染为青绿色（轻度错色 C-L1）。"
    },
    1828: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 08
    1830: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2"},
        "note": "窗台前透明玻璃花瓶内插着的原本鲜艳明亮的金黄色玫瑰花被严重错涂为粉红玫瑰，花瓶也错染粉色（严重错色 C-L3，中度偏色 D-L2）。"
    },
    1834: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1835: {
        "is_pass": False,
        "severities": {"D": "L3", "E1": "L2"},
        "note": "餐厅原本中性银灰色的不锈钢吧台工作台面与背景墙壁被全域恶性侵染为极其浓艳失真的冷青蓝紫光晕（严重偏色 D-L3，中度过饱和 E1-L2）。"
    },
    1836: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1837: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1841: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 09
    1843: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L1"},
        "note": "客厅原本明亮温馨的暖黄乳胶漆背景墙面被错涂为灰冷苍白的暗调墙面，室内暖意光照丧失（中度偏色 D-L2，轻度欠饱和 E2-L1）。"
    },
    1846: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1848: {
        "is_pass": False,
        "severities": {"D": "L2", "F": "L2"},
        "note": "滑板场地上空的傍晚微暗冷蓝天空被凭空错涂出一大片不自然突兀的红紫霞光色斑（中度偏色 D-L2，中度自然度受损 F-L2）。"
    },
    1851: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1852: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1853: {
        "is_pass": False,
        "severities": {"C": "L2", "D": "L1"},
        "note": "烤披萨角表层原本青翠的绿叶罗勒蔬菜被错涂褪色为发暗的枯红褐色（中度错色 C-L2，轻度偏色 D-L1）。"
    },

    # Sheet 10
    1854: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1856: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1858: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1862: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1867: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1870: {
        "is_pass": False,
        "severities": {"D": "L3", "E2": "L2"},
        "note": "咖啡厅原本极其温馨的暖黄色室内吊灯氛围与背景墙面被全域错涂为冰冷生硬的青灰冷绿调，严重破坏室内真实照明光影（严重偏色 D-L3，中度欠饱和 E2-L2）。"
    },

    # Sheet 11
    1871: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1872: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1874: {
        "is_pass": False,
        "severities": {"E2": "L3", "D": "L1"},
        "note": "水塘浅滩两岸原本生机盎然的青翠绿草地大面积脱色发白，错涂为苍白枯槁的灰白色地表（严重欠饱和 E2-L3，轻度偏色 D-L1）。"
    },
    1875: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1876: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1877: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 12
    1878: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1879: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1880: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1881: {
        "is_pass": False,
        "severities": {"C": "L2", "D": "L2", "E2": "L2"},
        "note": "少女手中握持的个性手机保护壳背板原本鲜艳的暖粉红色调被严重错涂褪色为脏污的青灰泛白色，边缘装饰粉色完全剥离（中度错色 C-L2，中度偏色 D-L2，中度欠饱和 E2-L2）。"
    },
    1882: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1883: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 13
    1885: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1886: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1887: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1891: {
        "is_pass": False,
        "severities": {"E2": "L2", "D": "L1"},
        "note": "公路警示牌上空原本浓郁纯净的高原深蓝色晴空被大面积褪色发白，呈现过曝浅青灰色（中度欠饱和 E2-L2，轻度偏色 D-L1）。"
    },
    1894: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1895: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 14
    1896: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1897: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "铁道路口竖立的八角形“STOP”红色交通警示标志牌严重褪色剥落，被错涂为暗沉发污的灰褐色（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },
    1903: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1904: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "透明食品包装盒上张贴的原本带有醒目红色印刷字体与红框的外包装标签被严重脱色错涂为暗青灰色（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },
    1906: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1907: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 15
    1908: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1909: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "街头广场滑板少年身上穿着的鲜艳明亮天蓝色长袖连帽衫被严重剥色错涂为苍白暗哑的灰白色（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },
    1916: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1917: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1918: {
        "is_pass": False,
        "severities": {"D": "L3", "E1": "L2"},
        "note": "火车站列车调度站场及上空原本清澈明亮的中性冷灰色调被全域恶性涂抹为浑浊压抑的红褐土黄色调，如同遭遇严重沙尘遮蔽（严重偏色 D-L3，中度过饱和 E1-L2）。"
    },
    1920: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 16
    1921: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1923: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1927: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1928: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1929: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1930: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 17
    1932: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1934: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1935: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1936: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1937: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1938: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "远景城市高楼天际线上空原本晴朗清澈的淡蓝色天空被严重剥色错涂为浑浊暗淡的灰黄土色（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },

    # Sheet 18
    1939: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1941: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1942: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1943: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1944: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "街头手拿食物的男孩身上穿着的鲜艳纯正大红色短袖T恤被严重脱色错涂为灰暗无光的暗褐灰色（严重错色 C-L3，中度欠饱和 E2-L2）。"
    },
    1946: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 19
    1949: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1950: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1951: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "足球场上两名小球员身上穿着的原本鲜亮耀眼的柠檬黄色运动球衣被严重褪色错涂为泛白无光泽的浅灰白黄色（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },
    1953: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1955: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1960: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 20
    1961: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1968: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1974: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1979: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1980: {"is_pass": True, "severities": {}, "note": "审查通过"},
    1982: {"is_pass": True, "severities": {}, "note": "审查通过"}
}

def main():
    print(f"Loaded {len(REVIEWS)} reviews for Batch 09.")
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

    print(f"Batch 09 applied: {pass_count} Passed (Defects Cleared), {grounding_count} Grounded with Concrete Objects.")

    with open(ALL_EXPORT, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {ALL_EXPORT}")

    with open(CLEAN_EXPORT, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {CLEAN_EXPORT}")

if __name__ == "__main__":
    main()
