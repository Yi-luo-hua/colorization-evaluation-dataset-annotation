#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_cv_audit_round1.py
Round 1 (Sheet 01 - Sheet 20, 共 120 组高危任务) 全量像素级直审定物改判落地脚本：
- 严格遵循 AGENTS.md 规范与基准 schema
- 消灭抽象代词，严格实体具象定物
- 更新 reviewed_1_10000_all.json
- 更新 reviewed_1_10000_clean.json
"""

import json
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
ALL_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_all.json"
CLEAN_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_clean.json"

ROUND1_FIXES = {
    # ================= Sheet 01 (Tasks 1 - 6) =================
    13: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "室内背景鲜艳砖红暖色背景墙完全脱色错涂为暗灰绿色冷调水泥墙。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "砖红背景墙与室内木质家具整体大幅脱色褪变发灰。"}
        ],
        "note": "核查发现：鲜艳砖红背景墙完全脱色错涂为暗灰绿冷墙(C-L2, E2-L2)。"
    },
    212: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "道路上鲜艳亮红色轿车车体彻底恶性错涂为冰冷深蓝灰色，产生严重颠倒错色。"}
        ],
        "note": "核查发现：鲜红轿车车体彻底恶性颠倒错涂为深蓝冷灰色(C-L3)。"
    },
    3070: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "GAIN 标志鲜艳亮宝蓝色运动球衣彻底恶性错涂为暗红褐色球衣，严重颠倒错色。"}
        ],
        "note": "核查发现：宝蓝色运动球衣恶性颠倒错涂为暗红褐色(C-L3)。"
    },
    3085: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "经典黑白花斑奶牛黑色毛皮被恶性错涂为红褐色棕牛皮毛。"}
        ],
        "note": "核查发现：黑白花斑母牛黑色毛皮错涂为红褐色棕牛皮毛(C-L2)。"
    },
    3439: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "明黄色塑料婴儿餐椅彻底脱色蜕变为惨白灰色餐椅，蛋糕奶油边缘染发暗伪蓝。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "鲜亮明黄色餐椅大面积脱色退化。"}
        ],
        "note": "核查发现：明黄塑料婴儿餐椅彻底脱色蜕变为惨白灰(C-L2, E2-L2)。"
    },
    3475: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "户外庭院清澈水池被错涂为不自然灰蓝青色伪色水体。"}
        ],
        "note": "核查发现：清澈水池被错涂为不自然灰蓝青色伪色(C-L2)。"
    },

    # ================= Sheet 02 (Tasks 7 - 12) =================
    3481: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "室内展柜浅绿背景与暖黄色照明脱色退化为发暗冷灰色。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "柜体局部反光略带杂色。"}
        ],
        "note": "核查发现：展柜浅绿背景与暖黄灯光脱色退化为发暗冷灰(E2-L2, C-L1)。"
    },
    264: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "餐桌上豆绿色陶瓷花瓶彻底脱色蜕变为惨淡灰白瓷瓶。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "花瓶豆绿色釉面与花枝生机翠绿完全脱色。"}
        ],
        "note": "核查发现：豆绿色陶瓷花瓶彻底脱色蜕变为惨白灰瓷瓶(C-L2, E2-L2)。"
    },
    294: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "厨房窗外晴朗天蓝色天空完全脱色蜕变惨灰白天幕。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "窗外蓝天与绿化景致完全脱色退化。"}
        ],
        "note": "核查发现：厨房窗外晴朗天蓝色天空完全脱色蜕变惨灰白天幕(C-L2, E2-L2)。"
    },
    318: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "货车清爽天蓝色车身栏板恶性颠倒错涂为刺目深洋红粉紫色伪色。"}
        ],
        "note": "核查发现：货车天蓝色车身栏板恶性颠倒错涂为深洋红紫伪色(C-L3)。"
    },
    324: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "鲜橙红色塑料餐盘彻底颠倒错涂为艳俗粉紫色餐盘。"}
        ],
        "note": "核查发现：鲜橙红色塑料餐盘彻底颠倒错涂为艳俗粉紫色餐盘(C-L3)。"
    },
    396: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "放风筝女孩明黄色短袖上衣严重脱色退化为灰白色素衫。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "黄色上衣与彩色风筝大面积脱色衰退。"}
        ],
        "note": "核查发现：女孩明黄色短袖上衣严重脱色退化为灰白色素衫(C-L2, E2-L2)。"
    },

    # ================= Sheet 03 (Tasks 13 - 18) =================
    473: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "网球少年鲜艳深宝蓝色短袖球衣彻底错涂为暗炭灰色T恤。"}
        ],
        "note": "核查发现：网球少年鲜艳深宝蓝色短袖球衣彻底错涂为暗炭灰色T恤(C-L3)。"
    },
    501: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "冲浪板艳丽红白条纹严重脱色变暗黑灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "冲浪服与海水边缘色阶略有衰退。"}
        ],
        "note": "核查发现：冲浪板艳丽红白条纹严重脱色变暗黑灰(E2-L2, C-L1)。"
    },
    503: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "滑板公园右侧涂鸦墙鲜艳黄色与橙色严重脱色变冷灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "涂鸦字体边缘略带发暗灰彩。"}
        ],
        "note": "核查发现：滑板公园右侧涂鸦墙鲜艳黄色与橙色严重脱色变冷灰(E2-L2, C-L1)。"
    },
    584: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "餐厅暖黄吊灯光晕与原木桌椅错涂为冷青灰色调。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内整体色调泛冷发青。"}
        ],
        "note": "核查发现：餐厅暖黄吊灯光晕与原木桌椅错涂为冷青灰色调(C-L2, D-L1)。"
    },
    597: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "休息区右侧朱红色地面大面积严重脱色退化为暗灰白地砖。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "朱红地面大面积脱色衰减。"}
        ],
        "note": "核查发现：休息区右侧朱红色地面大面积严重脱色退化为暗灰白(C-L2, E2-L2)。"
    },
    686: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "洗碗女士明黄色长袖针织衫彻底脱色退化为苍白灰白色素衣。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "明黄色针织衫色彩彻底褪失。"}
        ],
        "note": "核查发现：洗碗女士明黄色长袖针织衫彻底脱色退化为苍白灰白色素衣(C-L2, E2-L2)。"
    },

    # ================= Sheet 04 (Tasks 19 - 24) =================
    714: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "室内原木色储物柜与暖黄木门褪色为冷灰色调。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "全屋偏冷偏暗发灰。"}
        ],
        "note": "核查发现：室内原木色储物柜与暖黄木门褪色为冷灰色调(E2-L2, D-L1)。"
    },
    762: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街景路边大红色消火栓脱色退化为发暗黑灰色。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "红色金属漆面微弱泛蓝褐。"}
        ],
        "note": "核查发现：街景路边大红色消火栓脱色退化为发暗黑灰色(E2-L2, C-L1)。"
    },
    792: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "婴儿车深宝蓝色遮阳篷错涂为发暗青灰褐色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "遮阳篷色彩饱和度显著降低。"}
        ],
        "note": "核查发现：婴儿车深宝蓝色遮阳篷错涂为发暗青灰褐色(C-L2, E2-L1)。"
    },
    808: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "书桌背景明亮天青蓝色墙面彻底脱色退化为惨淡暗灰无色墙。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "背景天青蓝色大面积严重脱色退化。"}
        ],
        "note": "核查发现：书桌背景明亮天青蓝色墙面彻底脱色退化为惨淡暗灰无色墙(C-L2, E2-L2)。"
    },
    3055: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "盘边翠绿色餐布完全脱色蜕变为暗灰白布。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "翠绿色餐布大面积脱色变白。"}
        ],
        "note": "核查发现：盘边翠绿色餐布完全脱色蜕变为暗灰白布(C-L2, E2-L2)。"
    },
    3092: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "卧室暖橙红拼布床单完全脱色蜕变为暗灰白。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "全屋严重笼罩阴森冷灰紫调偏色。"}
        ],
        "note": "核查发现：暖橙红床单蜕变暗灰白(C-L2)；全屋偏阴冷灰紫(D-L2)。"
    },

    # ================= Sheet 05 (Tasks 25 - 30) =================
    3105: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "网球拍鲜艳荧光草绿色拍线完全脱色退化为惨白色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "荧光绿拍线与绿色球体脱色衰退。"}
        ],
        "note": "核查发现：网球拍鲜艳荧光草绿色拍线完全脱色退化为惨白色(C-L2, E2-L2)。"
    },
    3195: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "禁止停车红圈红杠交通标志牌彻底脱色蜕变为黑灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "标志红色警示反光膜完全脱色退化。"}
        ],
        "note": "核查发现：禁止停车红圈红杠交通标志牌彻底脱色蜕变为黑灰色(C-L2, E2-L2)。"
    },
    3207: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "卷饼配料生机深绿青椒丝严重脱色蜕变为暗灰白色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "蔬菜配料大面积脱色衰减。"}
        ],
        "note": "核查发现：卷饼配料生机深绿青椒丝严重脱色蜕变为暗灰白色(C-L2, E2-L2)。"
    },
    3342: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "冲浪帆翼橙红色拉花恶性颠倒错涂为深蓝色。"}
        ],
        "note": "核查发现：冲浪帆翼橙红色拉花恶性颠倒错涂为深蓝色(C-L2)。"
    },
    3346: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "红砖钟楼立面与火红枫树严重脱色退化为惨淡灰白色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "红砖建筑与秋季红叶彻底脱色变灰。"}
        ],
        "note": "核查发现：红砖钟楼立面与火红枫树严重脱色退化为惨淡灰白色(C-L2, E2-L2)。"
    },
    3500: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "训象员纯白上衣被彻底恶性错涂为刺目深宝蓝色。"}
        ],
        "note": "核查发现：训象员纯白上衣被彻底恶性错涂为刺目深宝蓝色(C-L2)。"
    },

    # ================= Sheet 06 (Tasks 31 - 36) =================
    17: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "棒球手深红色短袖球衣与护肘大面积脱色衰减为发暗深褐灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "红色球衣泛暗土褐色。"}
        ],
        "note": "核查发现：棒球手深红色短袖球衣与护肘大面积脱色衰减为发暗深褐灰(E2-L2, C-L1)。"
    },
    31: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "餐厅餐盘橙红番茄意面脱色为灰黄色，青翠罗勒叶发暗枯黄。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "番茄酱色泽暗淡偏土黄。"}
        ],
        "note": "核查发现：橙红番茄意面脱色为灰黄，罗勒叶发暗枯黄(E2-L2, C-L1)。"
    },
    35: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "户外野餐金黄玉米棒脱色蜕变为惨淡浅米白。"}
        ],
        "note": "核查发现：户外野餐金黄玉米棒脱色蜕变为惨淡浅米白(E2-L2)。"
    },
    126: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "卧室暖黄床头壁灯与金黄床品脱色为发暗冷灰调。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内整体光影泛冷发青。"}
        ],
        "note": "核查发现：卧室暖黄壁灯与金黄床品脱色为发暗冷灰调(E2-L2, D-L1)。"
    },
    178: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "赛马骑手鲜红夹克与红马鞍垫脱色衰退为发暗土褐。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "红色布料泛暗土黄色。"}
        ],
        "note": "核查发现：赛马骑手鲜红夹克与红马鞍垫脱色衰退为发暗土褐(E2-L2, C-L1)。"
    },
    203: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街头大红色双层巴士脱色褪变发暗紫黑灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "巴士车体漆面偏暗紫黑。"}
        ],
        "note": "核查发现：街头大红色双层巴士脱色褪变发暗紫黑灰(E2-L2, C-L1)。"
    },

    # ================= Sheet 07 (Tasks 37 - 42) =================
    223: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "绿茵球场平展翠绿草坪脱色为发暗枯草黄绿。"}
        ],
        "note": "核查发现：绿茵球场平展翠绿草坪脱色为发暗枯草黄绿(E2-L2)。"
    },
    314: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "客厅复古暖黄色印花地毯脱色为惨白冷灰地毯。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内整体偏冷色调。"}
        ],
        "note": "核查发现：客厅复古暖黄色印花地毯脱色为惨白冷灰地毯(E2-L2, D-L1)。"
    },
    461: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "披萨表面鲜红熟透番茄片脱色为发灰暗黄褐。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "番茄切片色泽泛土灰黄。"}
        ],
        "note": "核查发现：披萨表面鲜红番茄片脱色为发灰暗黄褐(E2-L2, C-L1)。"
    },
    521: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "沙滩排球运动员鲜艳天蓝运动背心脱色为惨白老头汗衫。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "背心微弱泛冷灰伪色。"}
        ],
        "note": "核查发现：运动员天蓝运动背心脱色为惨白老头汗衫(E2-L2, C-L1)。"
    },
    816: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街边橙黄色垃圾桶与警示标牌脱色褪变为土黄色。"}
        ],
        "note": "核查发现：街边橙黄色垃圾桶与警示标牌脱色褪变为土黄色(E2-L2)。"
    },
    848: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "棕色骏马与金黄草场严重退化为纯黑白灰度图。"}
        ],
        "note": "核查发现：棕色骏马与金黄草场严重退化为纯黑白灰度图(E2-L3)。"
    },

    # ================= Sheet 08 (Tasks 43 - 48) =================
    849: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "厨房红木餐椅与深色橱柜脱色偏冷发灰。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "木质家具泛冷灰色。"}
        ],
        "note": "核查发现：厨房红木餐椅与深色橱柜脱色偏冷发灰(E2-L2, D-L1)。"
    },
    879: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "农田金黄色熟麦地大面积脱色为发冷暗草绿。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "麦地泛冷青绿色。"}
        ],
        "note": "核查发现：农田金黄色熟麦地大面积脱色为发冷暗草绿(E2-L2, C-L1)。"
    },
    961: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "积木客厅鲜红色单人沙发彻底恶性错涂为暗沉军绿墨绿色。"}
        ],
        "note": "核查发现：积木客厅鲜红色单人沙发彻底恶性错涂为暗沉军绿墨绿色(C-L3)。"
    },
    47: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "绿化带草坪与乔木轻微偏暖发暗。"}
        ],
        "note": "核查确认：绿化带草坪与乔木轻微偏暖发暗(D-L1)。"
    },
    152: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "棒球场红褐色泥土内野被荒唐错涂为大面积生机翠绿草坪伪色。"}
        ],
        "note": "核查发现：棒球场红褐色泥土内野荒唐错涂为大面积生机翠绿草坪(C-L3)。"
    },
    153: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "机场跑道蔚蓝晴空与客机蓝涂装脱色变暗冷灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "天空色泽偏阴冷暗灰。"}
        ],
        "note": "核查发现：机场跑道蔚蓝晴空与客机蓝涂装脱色变暗冷灰(E2-L2, C-L1)。"
    },

    # ================= Sheet 09 (Tasks 49 - 54) =================
    206: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "街道交通红绿灯大红圆灯脱色蜕变惨白光圈。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "红色交通灯与周围指示标牌严重脱色。"}
        ],
        "note": "核查发现：交通红绿灯大红圆灯脱色蜕变惨白光圈(C-L2, E2-L2)。"
    },
    218: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "卧室原木床架与米黄壁纸泛冷发青发灰。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "室内暖光饱和度微弱降低。"}
        ],
        "note": "核查发现：卧室原木床架与米黄壁纸泛冷发青发灰(D-L1, E2-L1)。"
    },
    345: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "厨柜木纹与微波炉暖黄灯光脱色变冷暗白。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "整体略显生冷偏暗。"}
        ],
        "note": "核查发现：厨柜木纹与微波炉暖黄灯光脱色变冷暗白(E2-L2, D-L1)。"
    },
    3003: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "街道右侧生机翠绿草坪完全脱色蜕变为暗黑枯草地。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "绿化草地翠绿生机被彻底剥离。"}
        ],
        "note": "核查发现：街道右侧生机翠绿草坪完全脱色蜕变为暗黑枯草地(C-L2, E2-L2)。"
    },
    3032: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "欧式卫生间暖白瓷砖遭恶性烘烤严重偏脏暖黄土褐。"}
        ],
        "note": "核查发现：欧式卫生间暖白瓷砖遭恶性烘烤严重偏脏暖黄土褐(D-L2)。"
    },
    3042: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "护栏大红色导览立牌严重脱色退化为暗黑灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "导览牌红色漆面彻底褪色。"}
        ],
        "note": "核查发现：护栏大红色导览立牌严重脱色退化为暗黑灰色(C-L2, E2-L2)。"
    },

    # ================= Sheet 10 (Tasks 55 - 60) =================
    3065: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "沙拉餐盘生机翠绿蔬菜严重焦化变黑，胡萝卜碎脱色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "餐盘生鲜配菜大幅欠饱和脱色变暗。"}
        ],
        "note": "核查发现：沙拉餐盘生机翠绿蔬菜严重焦化变黑(C-L2, E2-L2)。"
    },
    3080: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "滑雪少年天蓝色防风头巾脱色褪变苍白灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "头巾微带冷灰伪色。"}
        ],
        "note": "核查发现：滑雪少年天蓝色防风头巾脱色褪变苍白灰(E2-L2, C-L1)。"
    },
    3115: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街角黄色出租车车顶灯与路标脱色衰减。"}
        ],
        "note": "核查发现：街角黄色出租车车顶灯与路标脱色衰减(E2-L2)。"
    },
    3135: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "码头游艇深蓝船舷脱色衰退为深灰。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "船体色调偏暗偏灰。"}
        ],
        "note": "核查发现：码头游艇深蓝船舷脱色衰退为深灰(E2-L1, D-L1)。"
    },
    3139: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "公园木长椅暖褐漆面泛冷发灰。"}
        ],
        "note": "核查确认：公园木长椅暖褐漆面泛冷发灰(D-L1)。"
    },
    3153: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "客厅深红地毯脱色变暗褐灰。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "地毯色泽发暗发脏。"}
        ],
        "note": "核查发现：客厅深红地毯脱色变暗褐灰(E2-L2, D-L1)。"
    },

    # ================= Sheet 11 (Tasks 61 - 66) =================
    3163: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "滑雪者淡薄荷青绿滑雪服恶性错涂为暗脏黄色。"}
        ],
        "note": "核查发现：滑雪者淡薄荷青绿滑雪服恶性错涂为暗脏黄色(C-L2)。"
    },
    3164: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "风之宫标志性砖红色砂岩外墙大面积严重脱色褪白为惨灰水泥色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "砖红古建筑外立面彻底脱色蜕变发灰。"}
        ],
        "note": "核查发现：风之宫砖红外墙严重脱色褪白为惨灰水泥色(C-L2, E2-L2)。"
    },
    3183: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "厨房红木餐桌与暖黄橱柜大面积偏暗偏黄土色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "木质色泽微弱衰减。"}
        ],
        "note": "核查发现：红木餐桌与暖黄橱柜大面积偏暗偏黄土色(D-L1, E2-L1)。"
    },
    3189: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "草坪上大红野餐毯脱色变暗粉灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "野餐毯边缘发暗微红褐。"}
        ],
        "note": "核查发现：草坪上大红野餐毯脱色变暗粉灰(E2-L2, C-L1)。"
    },
    3191: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "滑板少年明黄色T恤脱色蜕变灰白老头衫。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "亮黄色短袖大面积严重脱色。"}
        ],
        "note": "核查发现：滑板少年明黄色T恤脱色蜕变灰白老头衫(C-L2, E2-L2)。"
    },
    3212: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "卫生间洗手台冷白瓷盆遭烘烤泛黄土色。"}
        ],
        "note": "核查发现：卫生间洗手台冷白瓷盆遭烘烤泛黄土色(D-L1)。"
    },

    # ================= Sheet 12 (Tasks 67 - 72) =================
    3217: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "餐桌明黄色芥末酱瓶严重脱色退化为浅灰白色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "芥末酱瓶黄色塑料外壳完全褪色。"}
        ],
        "note": "核查发现：餐桌明黄色芥末酱瓶严重脱色退化为浅灰白色(C-L2, E2-L2)。"
    },
    3228: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街头大红色消火栓脱色退化为发乌深褐灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "金属漆面色调发暗偏褐。"}
        ],
        "note": "核查发现：街头大红色消火栓脱色退化为发乌深褐灰(E2-L2, C-L1)。"
    },
    3241: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "划桨板男子鲜艳深宝蓝潜水服彻底错涂为发暗炭黑灰。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "潜水服宝蓝色大面积脱色衰退。"}
        ],
        "note": "核查发现：男子深宝蓝潜水服彻底错涂为发暗炭黑灰(C-L2, E2-L2)。"
    },
    3253: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "幼童手中鲜红色牙刷柄被恶性错涂为浅青蓝天蓝色。"}
        ],
        "note": "核查发现：幼童手中鲜红色牙刷柄被恶性错涂为浅青蓝天蓝色(C-L2)。"
    },
    3259: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "卧室浅蓝窗帘脱色为冷灰白色。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "窗帘褶皱略带暗色。"}
        ],
        "note": "核查发现：卧室浅蓝窗帘脱色为冷灰白色(E2-L2, C-L1)。"
    },
    3266: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "厨房金黄烤面包脱色蜕变发暗土黄灰。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "吐司面包色泽偏暗偏干。"}
        ],
        "note": "核查发现：厨房金黄烤面包脱色蜕变发暗土黄灰(E2-L1, D-L1)。"
    },

    # ================= Sheet 13 (Tasks 73 - 78) =================
    3273: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "户外儿童鲜橙色救生衣脱色变枯黄土灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "救生衣亮橙色微偏暗黄。"}
        ],
        "note": "核查发现：儿童鲜橙色救生衣脱色变枯黄土灰(E2-L2, C-L1)。"
    },
    3288: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "办公室天蓝办公椅脱色退化为冷灰色。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "椅背布面偏暗灰。"}
        ],
        "note": "核查发现：办公室天蓝办公椅脱色退化为冷灰色(E2-L2, C-L1)。"
    },
    3289: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "码头大红色警示浮标脱色褪变黑灰色。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "浮标泛暗黑灰伪色。"}
        ],
        "note": "核查发现：码头大红色警示浮标脱色褪变黑灰色(E2-L2, C-L1)。"
    },
    3303: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "水池后方冷灰假山岩石恶性错涂为刺目火红橙色伪色。"}
        ],
        "note": "核查发现：水池后方冷灰假山岩石恶性错涂为刺目火红橙色伪色(C-L2)。"
    },
    3317: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街景黄色出租车脱色发灰，红绿灯红灯褪色。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "车身黄色漆面略偏暗。"}
        ],
        "note": "核查发现：街景黄色出租车脱色发灰，红绿灯红灯褪色(E2-L2, C-L1)。"
    },
    3326: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "网球选手鲜红头带与红球拍脱色变暗粉灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "红色装备局部褪变灰褐。"}
        ],
        "note": "核查发现：网球选手鲜红头带与红球拍脱色变暗粉灰(E2-L2, C-L1)。"
    },

    # ================= Sheet 14 (Tasks 79 - 84) =================
    3349: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "马夫球衣上的明黄色“6”号背号严重脱色蜕变为灰白色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "球衣背号数字黄色大幅衰减。"}
        ],
        "note": "核查发现：马夫球衣明黄背号数字脱色蜕变为灰白(C-L2, E2-L1)。"
    },
    3352: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "草丛盛开的鲜艳紫粉色野花群严重脱色枯萎衰减。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "野花花瓣色彩大面积退化。"}
        ],
        "note": "核查发现：草丛鲜艳紫粉色野花群严重脱色枯萎衰减(C-L2, E2-L2)。"
    },
    3404: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "高山深邃湛蓝晴空彻底脱色退化为苍白浅青灰死天幕。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "天空大面积脱色衰减。"}
        ],
        "note": "核查发现：高山深邃湛蓝晴空彻底脱色退化为苍白浅青灰死天幕(C-L2, E2-L2)。"
    },
    3414: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "餐厅暖黄吊灯烘烤整面墙壁泛发焦土黄色。"}
        ],
        "note": "核查发现：餐厅暖黄吊灯烘烤整面墙壁泛发焦土黄色(D-L1)。"
    },
    3423: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "海滩彩色风筝鲜艳红色拼面脱色衰退为暗褐。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "红色风筝略显发脏偏暗。"}
        ],
        "note": "核查发现：海滩彩色风筝鲜艳红色拼面脱色衰退为暗褐(E2-L2, C-L1)。"
    },
    3440: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "客厅浅天蓝沙发脱色退化为苍白冷灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "沙发面料略泛冷暗灰。"}
        ],
        "note": "核查发现：客厅浅天蓝沙发脱色退化为苍白冷灰(E2-L2, C-L1)。"
    },

    # ================= Sheet 15 (Tasks 85 - 90) =================
    3464: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "浴室明黄毛巾脱色退化为白毛巾。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "毛巾泛冷白灰。"}
        ],
        "note": "核查发现：浴室明黄毛巾脱色退化为白毛巾(E2-L2, C-L1)。"
    },
    3482: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街头红色邮筒脱色褪变发暗深灰红。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "邮筒漆面偏暗紫黑。"}
        ],
        "note": "核查发现：街头红色邮筒脱色褪变发暗深灰红(E2-L2, C-L1)。"
    },
    3485: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "棒球手深宝蓝球衣脱色变暗炭黑灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "球衣漆面偏暗灰。"}
        ],
        "note": "核查发现：棒球手深宝蓝球衣脱色变暗炭黑灰(E2-L2, C-L1)。"
    },
    3486: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "厨房翠绿蔬菜沙拉脱色枯焦变暗黄灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "蔬菜色泽发焦偏暗。"}
        ],
        "note": "核查发现：厨房翠绿蔬菜沙拉脱色枯焦变暗黄灰(E2-L2, C-L1)。"
    },
    3490: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内原木复合地板泛冷发青发灰。"}
        ],
        "note": "核查确认：室内原木复合地板泛冷发青发灰(D-L1)。"
    },
    578: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "卧室粉红床单脱色退化为惨白素灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "床单略带冷灰调。"}
        ],
        "note": "核查发现：卧室粉红床单脱色退化为惨白素灰(E2-L2, C-L1)。"
    },

    # ================= Sheet 16 (Tasks 91 - 96) =================
    151: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "绿茵操场翠绿草坪大面积脱色为发暗枯草黄褐。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "草坪色泽偏暗发干。"}
        ],
        "note": "核查发现：绿茵操场翠绿草坪大面积脱色为发暗枯草黄褐(E2-L2, C-L1)。"
    },
    3001: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街头天蓝色敞篷轿车脱色衰退为发暗水泥冷灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "车身漆面泛水泥冷灰。"}
        ],
        "note": "核查发现：天蓝色敞篷车脱色衰退为发暗水泥冷灰(E2-L2, C-L1)。"
    },
    3173: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "餐厅深红木质餐桌与暖黄吊灯烘烤泛土黄褐。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "桌面色彩略有衰退。"}
        ],
        "note": "核查发现：深红木餐桌与暖黄吊灯烘烤泛土黄褐(D-L1, E2-L1)。"
    },
    3244: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "列车车身深酒红涂装恶性错涂为刺目洋红粉红色伪色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "车厢涂装色相明显偏粉紫。"}
        ],
        "note": "核查发现：列车车身深酒红涂装恶性错涂为刺目洋红粉红色伪色(C-L2, D-L1)。"
    },
    3339: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "沙滩大红色遮阳伞脱色蜕变发暗灰白米色伞。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "遮阳伞红色完全脱色。"}
        ],
        "note": "核查发现：沙滩大红色遮阳伞脱色蜕变发暗灰白米色伞(C-L2, E2-L2)。"
    },
    3376: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "复古车厢车体被恶性颠倒错涂为暗红褐色。"}
        ],
        "note": "核查发现：复古车厢车体被恶性颠倒错涂为暗红褐色(C-L2)。"
    },

    # ================= Sheet 17 (Tasks 97 - 102) =================
    3484: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街景路边大红色消火栓脱色衰退为发暗深褐灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "消火栓漆面泛黑灰。"}
        ],
        "note": "核查发现：路边大红色消火栓脱色衰退为发暗深褐灰(E2-L2, C-L1)。"
    },
    551: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "卧室冷白瓷砖与墙面遭受严重恶性烘烤偏暗暖黄土褐。"}
        ],
        "note": "核查发现：卧室冷白瓷砖遭受严重恶性烘烤偏暗暖黄土褐(D-L2)。"
    },
    574: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "棒球打者亮黄色运动头盔脱色蜕变浅灰白。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "黄色头盔塑料质感完全蜕色。"}
        ],
        "note": "核查发现：打者亮黄色头盔脱色蜕变浅灰白(C-L2, E2-L2)。"
    },
    734: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内原木餐椅与木地板脱色泛青泛灰。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "木质暖感微弱衰退。"}
        ],
        "note": "核查发现：原木餐椅与木地板脱色泛青泛灰(D-L1, E2-L1)。"
    },
    811: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "厨柜明黄色把手与暖光照明脱色为冷灰。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "橱柜整体色调偏暗偏灰。"}
        ],
        "note": "核查发现：厨柜明黄把手与暖光照明脱色为冷灰(E2-L2, D-L1)。"
    },
    867: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "卫生间冷白洗手台与瓷砖偏暖偏黄。"}
        ],
        "note": "核查确认：卫生间冷白洗手台与瓷砖偏暖偏黄(D-L1)。"
    },

    # ================= Sheet 18 (Tasks 103 - 108) =================
    1041: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "老旧复古暖黄泛棕色调被剥离蜕变为冷灰黑白。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "老照片整体泛冷偏灰。"}
        ],
        "note": "核查发现：老照片复古暖黄棕调被剥离蜕变冷灰黑白(E2-L2, D-L1)。"
    },
    1044: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "牧场金黄色干燥草甸被错涂为暗灰青绿色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "金黄色草场大面积脱色衰减，羊群毛皮变冷灰。"}
        ],
        "note": "核查发现：金黄草场被错涂为暗灰青绿(C-L2, E2-L2)。"
    },
    1051: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "远景蔚蓝雪山山峦与滑雪者红棕头发脱色衰减。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "雪原背光阴影略显发灰泛暗。"}
        ],
        "note": "核查发现：远景蔚蓝雪山山峦与滑雪者红发脱色衰减(E2-L2, C-L1)。"
    },
    1067: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "滑板少年鲜艳宝蓝外套彻底脱色错涂为深黑灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "红色滑板帽与宝蓝外套完全严重脱色退化。"}
        ],
        "note": "核查发现：滑板少年鲜艳宝蓝外套彻底脱色错涂为深黑灰色(C-L2, E2-L2)。"
    },
    1068: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "泥滩暖褐泛红地表与湿地水体严重脱色变暗灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "草原水洼倒影略显发暗。"}
        ],
        "note": "核查发现：泥滩暖褐泛红地表与湿地水体严重脱色变暗灰(E2-L2, C-L1)。"
    },
    1156: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "列车车体鲜红色反光装饰条纹完全脱色蜕变为暗灰黑条。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "站台车厢暖色照明大面积脱色变冷。"}
        ],
        "note": "核查发现：列车鲜红反光条纹完全脱色蜕变为暗灰黑条(C-L2, E2-L2)。"
    },

    # ================= Sheet 19 (Tasks 109 - 114) =================
    1157: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "露台后方绿化草坪与灌木生机翠绿严重脱色发灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "露天遮阳伞反光略带暗调。"}
        ],
        "note": "核查发现：露台后方绿化草坪与灌木生机翠绿严重脱色发灰(E2-L2, C-L1)。"
    },
    1171: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "棒球打者鲜艳深宝蓝色球衣与头盔完全脱色错涂为深黑灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "红土击球区泥土与外野草坪脱色发暗。"}
        ],
        "note": "核查发现：打者鲜艳深宝蓝色球衣与头盔完全脱色错涂为深黑灰(C-L2, E2-L2)。"
    },
    1176: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "连续动作中滑板少年牛仔蓝短裤与板鞋细节完全脱色错涂为纯灰黑色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "地面暖色反光剥离退化。"}
        ],
        "note": "核查发现：滑板少年牛仔蓝短裤与板鞋完全脱色错涂为纯灰黑(C-L2, E2-L2)。"
    },
    1197: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "海水碧蓝清澈度略微衰减。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "海面色调轻微泛灰冷淡。"}
        ],
        "note": "核查发现：海水碧蓝清澈度略微衰减，海面轻微泛灰(E2-L1, D-L1)。"
    },
    1199: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "披萨鲜红番茄酱脱色错涂为发暗黄褐色且人脸肤色泛青灰。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "红酒与番茄配料脱色衰减。"}
        ],
        "note": "核查发现：披萨鲜红番茄酱错涂发暗黄褐且肤色泛青灰(C-L2, E2-L2)。"
    },
    1200: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街头彩色广告牌、车辆与暖色石板路面大面积脱色衰减。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "整体街景泛阴冷暗灰色。"}
        ],
        "note": "核查发现：街头彩色广告牌、车辆与暖色路面大面积脱色(E2-L2, C-L1)。"
    },

    # ================= Sheet 20 (Tasks 115 - 120) =================
    1216: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "网球少年深海蓝色运动球衣与短裤彻底脱色错涂为深黑炭灰。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "球拍细节与球场绿地脱色衰减。"}
        ],
        "note": "核查发现：网球少年深海蓝色球衣短裤彻底脱色错涂为深黑炭灰(C-L2, E2-L2)。"
    },
    1238: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "左侧青年橄榄绿长袖卫衣脱色错涂为发脏灰白粉灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "背景蔚蓝天空与金黄草甸大面积脱色衰减。"}
        ],
        "note": "核查发现：青年橄榄绿长袖卫衣脱色错涂为发脏灰白粉灰(C-L2, E2-L2)。"
    },
    1241: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "高脚酒杯中澄澈玫瑰粉红葡萄酒脱色衰减为发暗浑浊灰粉色。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "酒液反光微弱偏灰偏暗。"}
        ],
        "note": "核查发现：高脚杯玫瑰粉红葡萄酒脱色衰减为发暗浑浊灰粉(E2-L2, C-L1)。"
    },
    1249: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "斑马觅食的生机翠绿草地大面积脱色衰退为枯草泥灰色。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "翠绿草场错涂为暗黄泥灰硬地。"}
        ],
        "note": "核查发现：斑马生机翠绿草地大面积脱色衰退为枯草泥灰(E2-L2, C-L2)。"
    },
    1261: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "街头活动深宝蓝色帐篷遮阳棚彻底脱色错涂为暗褐灰黑色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "黄色道具立柱与人群彩衣脱色衰减。"}
        ],
        "note": "核查发现：街头活动深宝蓝色帐篷彻底脱色错涂为暗褐灰黑(C-L2, E2-L2)。"
    },
    1322: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "马路中央鲜艳砖红色自行车道完全脱色为暗灰柏油路，左侧翠绿色货车完全脱色错涂为白灰色货车。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街景彩色设施严重脱色衰减。"}
        ],
        "note": "核查发现：红色自行车道蜕变暗灰路，翠绿货车脱色为白灰车(C-L3, E2-L2)。"
    }
}

def main():
    print(f"Applying visual audit fixes for {len(ROUND1_FIXES)} tasks in Round 1...")

    with open(ALL_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)
    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    all_anns = all_data["annotations"]
    clean_anns = clean_data["annotations"]

    all_map = {ann["human_review"]["task_id"]: ann for ann in all_anns}
    clean_map = {ann["human_review"]["task_id"]: ann for ann in clean_anns}

    applied_count = 0
    for tid, fix_info in ROUND1_FIXES.items():
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
        else:
            print(f"Warning: Task {tid} not found in annotations!")

    print(f"Successfully applied fixes to {applied_count} / {len(ROUND1_FIXES)} tasks!")

    with open(ALL_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    with open(CLEAN_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)

    print("Both all.json and clean.json updated successfully!")

if __name__ == "__main__":
    main()
