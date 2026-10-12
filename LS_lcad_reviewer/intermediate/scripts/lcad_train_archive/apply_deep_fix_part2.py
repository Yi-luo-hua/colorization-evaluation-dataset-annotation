#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_deep_fix_part2.py
精准应用 Part 2 (Batch 4, Task ID 1501-2000, 77 个高危样本) 的视觉大图直审改判结果：
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

# Part 2 (77 例) 视觉大图核验改判映射
PART2_REVIEWS = {
    # Sheet 01
    1502: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "花斑奶牛皮毛红棕色斑块脱色发灰且背景人群服饰色泽剥夺衰减。"}],
        "note": "核查发现：花斑奶牛皮毛红棕斑块脱色发灰，街头商铺与服饰色彩衰减(C-L2)。"
    },
    1505: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "水边野生动物身后蔚蓝水面与天际线饱和度严重衰减脱色泛冷灰。"}],
        "note": "核查发现：水面与天际线蔚蓝色严重脱色泛冷灰(C-L2)。"
    },
    1514: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "站台金属钢架顶棚暖黄反光脱色泛冷灰，深蓝列车车头轻度暗化。"}],
        "note": "核查发现：站台金属钢架顶棚暖黄反光脱色泛冷灰，深蓝列车车头轻微暗化(C-L2)。"
    },
    1523: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "河面古建筑群日落暖金辉光脱色发灰，木舟与水体严重暗化焦枯。"}],
        "note": "核查发现：古建筑日落暖金辉光严重脱色，木舟与水体暗化焦枯(C-L2)。"
    },
    1525: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "广阔草坪生机翠绿脱色衰减为发冷暗淡浅灰绿，斑马黑白条纹轻微偏蓝冷感。"}],
        "note": "核查发现：广阔草坪生机翠绿脱色发灰，斑马黑白条纹微泛冷蓝(C-L2)。"
    },
    1535: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "左侧墙面与门框边缘严重溢出紫红伪色斑块，侍者面部肤色发红偏深。"}],
        "note": "核查发现：左侧墙壁与门框边缘严重溢出紫红伪色，侍者肤色过饱和发红(C-L2)。"
    },

    # Sheet 02
    1537: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "沙滩浅黄与蔚蓝天空脱色发灰，海浪水色泛冷暗沉。"}],
        "note": "核查发现：沙滩浅黄与蔚蓝天空脱色发灰，海浪水色泛冷暗沉(C-L2)。"
    },
    1540: {
        "defects": [{"id": "C", "name": "错色", "severity": "L1", "description": "室内暖黄墙面与木质桌椅饱和度轻度衰减偏暗。"}],
        "note": "核查发现：室内暖黄墙面与木质桌椅饱和度轻度衰减偏暗(C-L1)。"
    },
    1543: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "老树茂密生机绿叶树冠大面积恶性错涂为暗枯紫褐伪色。"}],
        "note": "核查发现：老树茂密树冠大面积恶性错涂为暗枯紫褐色伪色(C-L2)。"
    },
    1546: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "背景天空脱色暗化并泛不自然洋红微偏色，草地色泽略有衰减。"}],
        "note": "核查发现：背景天空脱色暗化并泛洋红微偏色，草地略有暗化(C-L2)。"
    },
    1552: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "厨师纯白工作服被严重污染泛冷蓝灰伪色，红色座椅靠背饱和度衰减发暗。"}],
        "note": "核查发现：厨师纯白工作服被严重污染泛冷蓝灰伪色，红色椅背发暗(C-L2)。"
    },
    1556: {
        "defects": [{"id": "C", "name": "错色", "severity": "L1", "description": "土坯房外墙暖土黄色调轻微衰减泛冷，坡地色泽轻度暗化。"}],
        "note": "核查发现：土坯房外墙暖土黄色调轻微衰减泛冷，坡地色泽轻度暗化(C-L1)。"
    },

    # Sheet 03
    1558: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "北极熊温暖奶黄毛皮被错涂为阴冷青蓝灰调，头部失去天然毛色生机。"}],
        "note": "核查发现：北极熊温暖奶黄毛皮被错涂为阴冷青蓝灰调，毛色生机受损(C-L2)。"
    },
    1569: {
        "defects": [],
        "note": "模型对金属停车收费表与街道沥青路面上色准确，反光质感自然，物理指标自洽放行。"
    },
    1570: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "中间记事本封皮鲜艳彩色严重脱色蜕变为暗灰白色，右侧彩色小配件饱和度衰减。"}],
        "note": "核查发现：中间记事本彩色封皮严重脱色蜕变为暗灰白色(C-L2)。"
    },
    1572: {
        "defects": [{"id": "C", "name": "错色", "severity": "L1", "description": "球场红土内场与背景看台观众席饱和度轻微衰减偏暗。"}],
        "note": "核查发现：球场红土内场与看台观众席饱和度轻微衰减偏暗(C-L1)。"
    },
    1573: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "户外玻璃桌面天空倒影脱色发暗，三明治新鲜番茄与生菜色泽严重暗化。"}],
        "note": "核查发现：玻璃桌面天空倒影脱色发暗，三明治番茄与生菜色泽暗化(C-L2)。"
    },
    1581: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "广阔生机草坪严重脱色泛白泛灰，奔马骑手服饰饱和度明显衰减。"}],
        "note": "核查发现：生机草坪大面积严重脱色泛灰白，骑手服饰饱和度衰减(C-L2)。"
    },

    # Sheet 04
    1582: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "男童浅蓝衬衫严重脱色衰减为暗灰色，面部肤色发青偏冷。"}],
        "note": "核查发现：男童浅蓝衬衫严重脱色衰减为暗灰色，肤色微泛冷青(C-L2)。"
    },
    1586: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "青年白衬衫与背景墙面被严重污染泛冷蓝紫伪色，肤色轻度偏冷。"}],
        "note": "核查发现：青年白衬衫与背景墙面严重污染泛冷蓝紫伪色(C-L2)。"
    },
    1587: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "男子衬衫泛紫灰偏色伪色，背景鲜红靠背脱色暗沉。"}],
        "note": "核查发现：男子衬衫泛紫灰伪色，背景鲜红靠垫脱色暗沉(C-L2)。"
    },
    1623: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "厨房木质吊柜与操作台面错涂泛暗绿偏色，木纹天然暖色脱色。"}],
        "note": "核查发现：厨房木质橱柜与操作台面错涂泛暗绿偏色，暖木色脱色(C-L2)。"
    },
    1634: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "客机机身周围晚霞炽热橙红云层恶性破损，错涂阴冷蓝灰斑块伪色。"}],
        "note": "核查发现：客机周围晚霞炽热橙红云层错涂阴冷蓝灰斑块伪色(C-L2)。"
    },
    1637: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "披萨饼底新鲜番茄酱脱色暗化泛紫发灰，料理台木质暖色调衰减。"}],
        "note": "核查发现：披萨新鲜番茄酱脱色暗化泛灰紫，料理台暖色衰减(C-L2)。"
    },

    # Sheet 05
    1638: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "棒球场内场泥土地面暖黄色泽脱色衰减为发冷暗灰，草地轻度暗化。"}],
        "note": "核查发现：棒球场内场泥土地面暖黄质感脱色衰减为发冷暗灰(C-L2)。"
    },
    1650: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "卫生间纯白瓷砖、毛巾与马桶大面积恶性错涂为发脏发暗暖黄土褐调。"}],
        "note": "核查发现：卫生间纯白瓷砖、毛巾与马桶大面积恶性错涂为发脏暖黄土褐调(C-L2)。"
    },
    1656: {
        "defects": [],
        "note": "模型对骑警队列、战马毛色与明亮天空上色准确，边缘整洁无明显溢色，物理指标自洽放行。"
    },
    1666: {
        "defects": [],
        "note": "模型对骑行青年、格纹衬衫、自行车金属车架及街景上色逼真协调，微弱色差属合理自然光影，物理自洽放行。"
    },
    1667: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "CRT显示器屏幕图像严重错涂泛暗紫红伪色，屏幕中心出现暗斑溢色。"}],
        "note": "核查发现：CRT显示器屏幕图像严重错涂泛暗紫红伪色并出现暗斑溢色(C-L2)。"
    },
    1671: {
        "defects": [{"id": "C", "name": "错色", "severity": "L1", "description": "背景远方稀树灌木丛饱和度轻度衰减，略泛冷调微偏色。"}],
        "note": "核查发现：背景稀树灌木丛饱和度轻度衰减，略泛冷调微偏色(C-L1)。"
    },

    # Sheet 06
    1684: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "多功能大厅内景整体严重偏色泛黄泛青，后方观众席彩色服饰脱色暗化。"}],
        "note": "核查发现：多功能大厅内景整体严重偏色泛黄泛青，后方观众席服饰脱色暗化(C-L2)。"
    },
    1686: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "新鲜胡萝卜与生菜蔬菜色泽严重错涂暗化，呈现枯萎泥土褐色。"}],
        "note": "核查发现：砧板胡萝卜与新鲜蔬菜色泽严重错涂暗化，呈泥土褐色(C-L2)。"
    },
    1689: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "背景天空与树林严重错涂暗枯黄褐色伪色，青绿色调彻底丧失。"}],
        "note": "核查发现：背景天空与树林严重错涂暗枯黄褐色伪色，失去天然生机(C-L2)。"
    },
    1694: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "浅滩水面夕阳暖金倒影脱色衰减，呈现阴冷暗淡紫灰调。"}],
        "note": "核查发现：浅滩水面夕阳暖金倒影脱色衰减，呈现阴冷暗淡紫灰调(C-L2)。"
    },
    1699: {
        "defects": [{"id": "C", "name": "错色", "severity": "L1", "description": "年轻女子粉红吊带上衣饱和度轻度衰减，盘中食物色泽轻微暗化。"}],
        "note": "核查发现：年轻女子粉红吊带上衣饱和度轻度衰减，盘中食物微暗(C-L1)。"
    },
    1703: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "特写镜头下新郎新娘佩戴婚戒的双手肤色明显过饱和发红，衣物边缘微泛紫红伪色。"}],
        "note": "核查发现：新人双手肤色过饱和发红，衣物边缘微泛紫红伪色(C-L2)。"
    },

    # Sheet 07
    1707: {
        "defects": [],
        "note": "模型对斑马头部黑白斑纹与背景红土沙地上色逼真，毛发细节分明，物理自洽放行。"
    },
    1708: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "宫殿大理石廊柱与地面严重错涂发脏土黄褐伪色，大象红色鞍毯饱和度衰减。"}],
        "note": "核查发现：宫殿大理石廊柱与地面错涂发脏土黄褐伪色，大象红色鞍毯脱色(C-L2)。"
    },
    1711: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "青年白色衬衫与背景街景建筑大面积错涂发脏暗红紫伪色，肤色严重偏深。"}],
        "note": "核查发现：青年白衬衫与背景建筑错涂发脏暗红紫伪色，肤色偏深(C-L2)。"
    },
    1715: {
        "defects": [],
        "note": "模型对俯视棒球场翠绿草坪、扇形泥土内场及攻防球员上色准确自然，物理指标自洽放行。"
    },
    1717: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "白瓷盘中香煎鱼肉表面金黄质感恶性暗化焦黑，奶油浓汁与紫色甘蓝配菜脱色严重。"}],
        "note": "核查发现：盘中香煎鱼肉金黄质感恶性暗化焦黑，奶油浓汁与甘蓝配菜脱色(C-L2)。"
    },
    1721: {
        "defects": [{"id": "C", "name": "错色", "severity": "L1", "description": "笔记本外壳彩色个性贴纸与桌面杂物饱和度轻度衰减偏暗。"}],
        "note": "核查发现：笔记本外壳彩色贴纸与桌面杂物饱和度轻度衰减偏暗(C-L1)。"
    },

    # Sheet 08
    1728: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "卫生间百叶窗透光区域恶性错涂为刺目洋红紫伪色，瓷砖墙面微泛暖褐。"}],
        "note": "核查发现：卫生间百叶窗透光区域恶性错涂为刺目洋红紫伪色(C-L2)。"
    },
    1735: {
        "defects": [],
        "note": "模型对欧式厨房白色橱柜、米黄墙壁及窗台光影上色真实协调，符合室内光环境，物理自洽放行。"
    },
    1736: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "戴太阳镜男子面部肤色严重错涂暗红发黑，呈现不自然的重度灼伤感偏色。"}],
        "note": "核查发现：男子面部肤色严重错涂暗红发黑，呈现重度灼伤感偏色(C-L2)。"
    },
    1741: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "双肩背包表面鲜红刺绣品牌Logo脱色蜕变灰黑，背包面料轻微偏色。"}],
        "note": "核查发现：双肩背包表面鲜红刺绣品牌Logo脱色蜕变灰黑(C-L2)。"
    },
    1744: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "餐桌中央艺术插花鲜艳花束严重脱色枯萎暗化，餐厅暖黄氛围略有衰减。"}],
        "note": "核查发现：餐桌艺术插花鲜艳花束严重脱色枯萎暗化，餐厅暖色衰减(C-L2)。"
    },
    1753: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "操作台新鲜红番茄与部分果蔬严重脱色暗化，生机鲜润质感衰减。"}],
        "note": "核查发现：操作台新鲜红番茄与部分果蔬严重脱色暗化(C-L2)。"
    },

    # Sheet 09
    1758: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "厨房木质岛台与橱柜表面恶性错涂暗蓝紫伪色，室内光影严重失真。"}],
        "note": "核查发现：厨房木质岛台与橱柜表面恶性错涂暗蓝紫伪色(C-L2)。"
    },
    1772: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "餐盘中现烤披萨切片番茄红酱与金黄芝士严重脱色发白，色泽苍白暗淡。"}],
        "note": "核查发现：餐盘现烤披萨切片番茄红酱与金黄芝士严重脱色发白(C-L2)。"
    },
    1782: {
        "defects": [{"id": "C", "name": "错色", "severity": "L1", "description": "棒球捕手鲜红头盔与护具饱和度轻度衰减偏暗，球场红土轻微脱色。"}],
        "note": "核查发现：棒球捕手鲜红头盔与护具饱和度轻度衰减偏暗(C-L1)。"
    },
    1783: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "宴会餐桌右侧女士服饰边缘严重溢出刺目红斑伪色，人物肤色局部泛青。"}],
        "note": "核查发现：宴会餐桌右侧女士服饰边缘严重溢出刺目红斑伪色(C-L2)。"
    },
    1793: {
        "defects": [],
        "note": "模型对客运机舱整排紫色头枕套、深蓝座椅及行李架漫射光上色逼真协调，结构边缘无溢色，物理自洽放行。"
    },
    1799: {
        "defects": [{"id": "C", "name": "错色", "severity": "L1", "description": "年轻女子酒红针织衫饱和度轻度衰减偏暗褐，面部肤色微泛冷暗。"}],
        "note": "核查发现：年轻女子酒红针织衫饱和度轻度衰减偏暗褐(C-L1)。"
    },

    # Sheet 10
    1802: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "涉水象夫鲜红上衣严重脱色发暗，大象背部骑乘装具饱和度衰减。"}],
        "note": "核查发现：涉水象夫鲜红上衣严重脱色发暗，大象鞍座饱和度衰减(C-L2)。"
    },
    1845: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "棒球击球手纯白运动球裤大面积恶性错涂为深蓝冷灰伪色，球场草皮微泛冷调。"}],
        "note": "核查发现：击球手纯白球裤大面积恶性错涂为深蓝冷灰伪色(C-L2)。"
    },
    1855: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "推婴儿车母亲深红上衣脱色发暗，背景长颈鹿身躯恶性溢出蓝紫偏色伪色。"}],
        "note": "核查发现：推婴儿车母亲深红上衣脱色发暗，长颈鹿身躯恶性溢出蓝紫伪色(C-L2)。"
    },
    1864: {
        "defects": [],
        "note": "模型对白墙下木质长椅、藤蔓植物及投影光影上色干净逼真，物理指标自洽放行。"
    },
    1868: {
        "defects": [],
        "note": "模型对站台停靠列车的明黄色车体、弧形拱顶与站台地面上色协调精准，物理自洽放行。"
    },
    1873: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "卫生间米暖色墙面隔板恶性错涂为阴冷青绿色伪色，瓷砖色温严重倒错。"}],
        "note": "核查发现：卫生间米暖色墙面隔板恶性错涂为阴冷青绿色伪色(C-L2)。"
    },

    # Sheet 11
    1888: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "走廊通道与深处房间内部严重错涂深青蓝伪色，木质橱柜暖色衰减。"}],
        "note": "核查发现：走廊通道与深处房间内部严重错涂深青蓝伪色(C-L2)。"
    },
    1892: {
        "defects": [],
        "note": "模型对车库多功能区木质餐桌椅及周围生活杂物上色逼真协调，明暗对比自然，物理指标自洽放行。"
    },
    1893: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "并排卫生间马桶暖黄塑料座圈严重脱色漂白为惨白灰，塑料原有暖色剥夺。"}],
        "note": "核查发现：马桶暖黄塑料座圈严重脱色漂白为惨白灰，暖色剥夺(C-L2)。"
    },
    1902: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "青年胸前鲜艳红白斜纹领带恶性错涂为蓝黑暗纹伪色，西装面料偏色。"}],
        "note": "核查发现：青年胸前鲜艳红白斜纹领带恶性错涂为蓝黑暗纹伪色(C-L2)。"
    },
    1910: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "白色被褥大面积恶性溢出紫红偏色伪色，被面刺绣雪花图案饱和度衰减。"}],
        "note": "核查发现：白色被褥大面积恶性溢出紫红偏色伪色(C-L2)。"
    },
    1924: {
        "defects": [],
        "note": "模型对野生动物园灌木丛、大象身躯与背景树木上色自然连贯，植物生机充足，物理指标自洽放行。"
    },

    # Sheet 12
    1925: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "古老石砌教堂钟楼与天空恶性错涂暖红褐色伪色，失去天然冷石质感。"}],
        "note": "核查发现：古老石砌教堂钟楼与天空恶性错涂暖红褐色伪色(C-L2)。"
    },
    1926: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "纸杯蛋糕顶部鲜艳柠檬黄奶油严重脱色蜕变为灰白色，甜点质感衰减。"}],
        "note": "核查发现：纸杯蛋糕顶部鲜艳柠檬黄奶油严重脱色蜕变为灰白色(C-L2)。"
    },
    1945: {
        "defects": [],
        "note": "模型对客厅大体量布艺沙发、木质茶几及窗外柔和采光上色自然和谐，物理指标自洽放行。"
    },
    1952: {
        "defects": [],
        "note": "模型对明亮卫浴空间、黄色塑料收纳箱与白色洗手台面上色准确真实，物理指标自洽放行。"
    },
    1954: {
        "defects": [],
        "note": "模型对阁楼斜顶木梁结构与儿童床幔上色逼真，原木质感自然，物理指标自洽放行。"
    },
    1967: {
        "defects": [{"id": "C", "name": "错色", "severity": "L1", "description": "同行女士手提金属光泽包袋与金黄毛绒玩偶饱和度轻度衰减偏暗。"}],
        "note": "核查发现：女士手提金属光泽包袋与金黄毛绒玩偶饱和度轻度衰减偏暗(C-L1)。"
    },

    # Sheet 13
    1970: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "池塘林荫下原本极其醒目的大红长木椅严重脱色蜕变为惨白色，色彩识别度彻底丧失。"}],
        "note": "核查发现：池塘林荫下原本极其醒目的大红长木椅严重脱色蜕变为惨白色(C-L2)。"
    },
    1973: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "复古撑伞游人粉红衣衫严重脱色衰减，林间人像氛围偏暗发灰。"}],
        "note": "核查发现：复古撑伞游人粉红衣衫严重脱色衰减，人像氛围偏暗发灰(C-L2)。"
    },
    1983: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "海滩明黄色与天蓝色遮阳伞严重脱色发白，海面水色饱和度衰减。"}],
        "note": "核查发现：海滩明黄与天蓝遮阳伞严重脱色发白，海水色泽衰减(C-L2)。"
    },
    1989: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "轿车车内大红座椅与装饰严重脱色暗化泛黑，玻璃反光色泽衰减。"}],
        "note": "核查发现：轿车车内大红座椅与装饰严重脱色暗化泛黑(C-L2)。"
    },
    1992: {
        "defects": [],
        "note": "模型对大型客车白色车身、晚霞粉紫天空及街景立面上色逼真协调，色调自然，物理自洽放行。"
    }
}

def main():
    print(f"Total Part 2 fixes defined: {len(PART2_REVIEWS)}")
    assert len(PART2_REVIEWS) == 77, f"Expected 77 fixes, got {len(PART2_REVIEWS)}"

    with open(ALL_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    anns_all = all_data["annotations"]
    anns_clean = clean_data["annotations"]

    updated_count = 0
    for ann_a, ann_c in zip(anns_all, anns_clean):
        tid = ann_a["human_review"]["task_id"]
        if tid in PART2_REVIEWS:
            rev = PART2_REVIEWS[tid]
            has_defect_a = any(d.get("id") == "A" for d in rev["defects"])

            # 更新 all_data
            ann_a["defects"] = rev["defects"]
            ann_a["review_note"] = rev["note"]
            ann_a["reviewed_score"] = 1.0 if has_defect_a else None
            ann_a["needs_rescoring"] = not has_defect_a
            ann_a["review_status"] = "已核验"

            # 更新 clean_data (review_note 严格保持 "")
            ann_c["defects"] = rev["defects"]
            ann_c["review_note"] = ""
            ann_c["reviewed_score"] = 1.0 if has_defect_a else None
            ann_c["needs_rescoring"] = not has_defect_a
            ann_c["review_status"] = "已核验"

            updated_count += 1

    print(f"Updated {updated_count} Part 2 high-risk items in memory.")
    assert updated_count == 77, f"Expected 77 updated items, got {updated_count}"

    with open(ALL_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved: {ALL_FILE.name}")

    with open(CLEAN_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved: {CLEAN_FILE.name}")

    print("\n[SUCCESS] Part 2 deep fix successfully applied to all exports!")

if __name__ == "__main__":
    main()
