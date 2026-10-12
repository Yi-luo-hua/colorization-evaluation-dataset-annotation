#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_cv_sample_fixes.py
精准修复从最初 CV 物理指标直接修正池抽检发现的典型恶性硬伤样本：
- 严格遵循 AGENTS.md 规范与基准 schema
- 消灭抽象代词，严格实体定物
- 更新 reviewed_1_10000_all.json
- 更新 reviewed_1_10000_clean.json
"""

import json
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
ALL_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_all.json"
CLEAN_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_clean.json"

FIX_MAPPING = {
    # Sheet 01
    18: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "卫生间灰白色木龙骨骨架被严重恶性错涂为高饱和鲜橙黄色伪色，侧墙偏青绿色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "地面木板色调偏红褐偏色。"}
        ],
        "note": "核查发现：卫生间灰白木龙骨骨架恶性错涂为鲜橙黄色伪色(C-L2)；地面木板偏红褐(D-L1)。"
    },
    260: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "热狗上方黄绿色芥末酱被错涂为深橙红色，洋葱碎局部被污染泛黄。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "肉酱与酱料边缘色阶略显生硬。"}
        ],
        "note": "核查发现：热狗黄绿芥末酱被错涂为深橙红色(C-L2)；洋葱碎被污染泛黄(F-L1)。"
    },
    478: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "卫生间浴帘上的生机翠绿色竖条纹大面积严重欠饱和脱色发暗。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "卫生间全屋瓷砖与墙面严重偏暗暖黄土褐色。"}
        ],
        "note": "核查发现：卫生间浴帘生机翠绿条纹严重脱色(E2-L2)；全屋偏暗暖黄土褐(D-L2)。"
    },
    1057: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "书桌背景明亮清爽的蒂芙尼天青蓝墙面被彻底错涂脱色退化为惨白暗灰无色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "左侧粉红色地球仪与右侧彩色折扇色彩大幅褪色衰减。"}
        ],
        "note": "原5.0满分严重漏检，核查发现：书桌天青蓝色背景墙面彻底脱色退化为惨白灰(C-L2, E2-L2)。"
    },
    1091: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "办公室电脑桌与白色墙面整体偏暖发黄。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "墙上彩色便签纸色彩饱和度轻度脱色衰减。"}
        ],
        "note": "原5.0满分复核，核查发现：电脑桌与墙面偏暖发黄(D-L1)；彩色便签轻度脱色(E2-L1)。"
    },
    1183: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "现代卫生间冷光镜前灯与石质台面被恶性烘烤为刺目发焦的暗暖黄褐调。"}
        ],
        "note": "核查发现：卫生间冷光台面遭受恶性烘烤严重偏暗暖黄褐调(D-L2)。"
    },

    # Sheet 02
    1201: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "驯象人身上原有的浅灰卡其色短袖上衣被恶性错涂为高饱和鲜橙红色假色。"},
            {"id": "B", "name": "溢色", "severity": "L1", "description": "大象鼻子边缘与人手交界处溢染红褐色杂斑。"}
        ],
        "note": "核查发现：驯象人浅卡其短袖恶性错涂为鲜橙红色(C-L2)；大象鼻部溢染红褐杂斑(B-L1)。"
    },
    1526: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "雪场中央穿深红色外套的滑雪者被彻底恶性颠倒错涂为深宝蓝色外套，左侧黑衣者被错涂为深紫红。"}
        ],
        "note": "原5.0满分严重漏检，核查发现：滑雪者深红外套被恶性颠倒错涂为深宝蓝外套(C-L3)。"
    },
    1669: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "海滩冲浪男子的粉红碎花沙滩短裤被恶性错涂为宝蓝色短裤，遮阳棚顶布亦变色。"}
        ],
        "note": "原5.0满分严重漏检，核查发现：男子粉红碎花短裤被恶性错涂为宝蓝色短裤(C-L2)。"
    },
    1798: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "便当盒旁绿色包装 ACTIVIA 经典酸奶盒被严重颠倒错涂为深宝蓝色伪色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "餐盒内鲜绿色蔬菜严重脱色褪白，胡萝卜色调泛橙焦。"}
        ],
        "note": "核查发现：绿色 ACTIVIA 酸奶盒恶性颠倒错涂为深宝蓝色(C-L3)；盒内绿蔬菜严重脱色(E2-L2)。"
    },

    # Sheet 03
    2033: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "品酒女子原本穿着的深灰绿立领风衣外套被彻底严重错涂为刺目艳俗的洋红粉紫色外套。"}
        ],
        "note": "核查发现：品酒女子深灰绿风衣外套彻底恶性错涂为刺目洋红粉紫色(C-L3)。"
    },
    2114: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "厨房右侧操作台水槽台面的生机翠绿色瓷砖完全严重脱色蜕变为惨淡米白灰色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内木质橱柜与地面整体色调偏暗偏暖。"}
        ],
        "note": "核查发现：厨房水槽台面生机翠绿瓷砖严重脱色蜕变为惨白灰(E2-L2)；室内偏暗暖(D-L1)。"
    },
    2166: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "重型卡车车头上方标志性深宝蓝色涂装彻底脱色蜕变为灰暗铁灰色。"}
        ],
        "note": "核查发现：重型卡车车头深宝蓝涂装彻底脱色蜕变铁灰(E2-L2)。"
    },

    # Sheet 04
    2941: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "林间河流清澈明亮的蒂芙尼湖水蔚蓝完全脱色蜕变为惨白浑浊死泥水。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "背景生机葱茏的山坡树林绿色饱和度明显衰减发暗。"}
        ],
        "note": "原5.0满分严重漏检，核查发现：清澈蔚蓝河流完全脱色蜕变惨白死泥水(C-L2, E2-L2)。"
    },
    2970: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "滑雪场原木深灰褐色木屋度假村墙面与屋顶被恶性错涂为刺目的高饱和鲜艳大橙色建筑。"}
        ],
        "note": "原5.0满分严重漏检，核查发现：深灰木屋度假村墙面被恶性错涂为刺目荧光大橙色(C-L2)。"
    },

    # Sheet 05
    3327: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "卫生间角落原本的亮橙红色塑料水桶被彻底恶性颠倒错涂为草绿色水桶，左门框染粉紫伪色。"}
        ],
        "note": "原5.0满分严重漏检，核查发现：亮橙红塑料水桶被彻底恶性颠倒错涂为草绿色水桶(C-L2)。"
    },
    3581: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "棒球捕手身上的鲜红色球衣与红色护具完全脱色蜕变为暗灰白色，看台红色广告牌发暗脱色。"}
        ],
        "note": "核查发现：棒球捕手鲜红球衣与护具严重脱色蜕变为暗灰白(C-L2)。"
    },
    4123: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "三角风筝骨架边缘包裹的纯正天蓝色边条被严重错涂为深紫红洋色伪色。"}
        ],
        "note": "原5.0满分严重漏检，核查发现：三角风筝天蓝色包边被严重错涂为深紫红色(C-L2)。"
    },

    # Sheet 06
    4927: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "工人们佩戴的明黄色安全帽严重脱色蜕变为苍白灰白帽子，背后大本钟背景严重褪色。"}
        ],
        "note": "核查发现：工人明黄色安全帽严重脱色褪白(E2-L2)；大本钟建筑褪色(F-L1)。"
    },
    5339: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "温馨厨房下方红色橱柜门被严重错涂为刺目的亮青蓝湖绿色伪色，暖黄吊灯失色偏暗。"}
        ],
        "note": "核查发现：厨房红色橱柜门严重恶性错涂为亮青蓝伪色(C-L2)。"
    },
    5477: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街头停靠的鲜艳明黄色三轮货车车身完全脱色蜕变为暗灰无色车厢。"}
        ],
        "note": "核查发现：街头鲜艳明黄三轮车完全脱色蜕变为暗灰白无色车(E2-L2)。"
    },
    5846: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "沙发上熟睡男子原本身穿的纯白色短袖T恤被彻底恶性错涂为刺目的深宝蓝色上衣。"}
        ],
        "note": "原5.0满分严重漏检，核查发现：男子纯白短袖T恤被彻底恶性错涂为刺目深宝蓝色(C-L3)。"
    },

    # Sheet 07
    5947: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "电脑桌地面铺设的大面积鲜艳大红色地毯被彻底错涂为发暗泥土棕褐色木地板色。"}
        ],
        "note": "原5.0满分严重漏检，核查发现：满铺鲜红地毯被彻底恶性错涂为暗泥土棕褐色(C-L3)。"
    },
    6042: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "甲板栏杆上悬挂的两个鲜艳橙红色救生圈完全脱色蜕变为暗铁灰色。"}
        ],
        "note": "核查发现：甲板橙红色救生圈完全脱色蜕变暗铁灰(E2-L2)。"
    },

    # Sheet 08
    6560: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "棒球球员身上原本纯正深宝蓝色的庆祝球衣被彻底恶性颠倒错涂为暗红褐色球衣。"}
        ],
        "note": "原5.0满分严重漏检，核查发现：棒球球员深宝蓝球衣被彻底恶性颠倒错涂为暗红褐色(C-L3)。"
    },
    6893: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "房车内部橱柜、门框与操作台几乎彻底蜕变退化为毫无色彩的黑白灰度图。"}
        ],
        "note": "核查发现：房车内部空间几乎完全蜕变为黑白灰度图严重脱色(E2-L3)。"
    },

    # Sheet 09
    7409: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "纽约街头标志性鲜艳明黄色出租车（Yellow Cab）大面积脱色蜕变发暗灰白素车。"}
        ],
        "note": "核查发现：纽约经典明黄色出租车大面积脱色蜕变为灰白色(C-L2)。"
    },
    7799: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "刷漆人员佩戴的清爽天蓝色橡胶防护手套被恶性错涂为鲜艳洋红大红色手套。"}
        ],
        "note": "核查发现：清爽天蓝橡胶手套恶性错涂为鲜艳大红色(C-L2)。"
    },

    # Sheet 10
    8643: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "温网球员身上穿着的鲜红色运动短袖T恤完全严重脱色蜕变为苍白老头汗衫，草地球场生机衰减。"}
        ],
        "note": "核查发现：球员鲜红运动短袖完全脱色蜕变为苍白素色汗衫(C-L2)。"
    }
}

def main():
    print(f"Applying fixes for {len(FIX_MAPPING)} critical CV physical flaw tasks...")

    with open(ALL_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)
    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    all_anns = all_data["annotations"]
    clean_anns = clean_data["annotations"]

    all_map = {ann["human_review"]["task_id"]: ann for ann in all_anns}
    clean_map = {ann["human_review"]["task_id"]: ann for ann in clean_anns}

    applied_count = 0
    for tid, fix_info in FIX_MAPPING.items():
        if tid in all_map:
            ann_all = all_map[tid]
            ann_clean = clean_map[tid]

            ann_all["defects"] = fix_info["defects"]
            ann_all["review_note"] = fix_info["note"]
            ann_all["reviewed_score"] = None
            ann_all["needs_rescoring"] = True
            ann_all["review_status"] = "已核验"

            ann_clean["defects"] = fix_info["defects"]
            ann_clean["review_note"] = ""
            ann_clean["reviewed_score"] = None
            ann_clean["needs_rescoring"] = True
            ann_clean["review_status"] = "已核验"

            applied_count += 1

    print(f"Successfully applied fixes to {applied_count} tasks!")

    with open(ALL_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    with open(CLEAN_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)

    print("Both all.json and clean.json updated successfully!")

if __name__ == "__main__":
    main()
