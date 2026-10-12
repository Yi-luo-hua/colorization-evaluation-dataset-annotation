# -*- coding: utf-8 -*-
"""
Apply visual grounding reviews for Remaining Batch 15 (Tasks #3284 ~ #3599, total 120 tasks across 20 sheets).
V4 Standards Compliant:
- Defect IDs: A, B, C, D, E1, E2, F
- Severities: L1, L2, L3 (A has no severity)
- Concrete physical entities grounded (Zero abstract placeholder words)
- Double-gate check for pass (defects=[])
"""

import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../.."))
ALL_JSON_PATH = os.path.join(PROJECT_ROOT, "LS_lcad_reviewer/exports/reviewed_1_10000_all.json")
CLEAN_JSON_PATH = os.path.join(PROJECT_ROOT, "LS_lcad_reviewer/exports/reviewed_1_10000_clean.json")
GROUNDING_OUT_PATH = os.path.join(PROJECT_ROOT, "LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_15.json")

BANNED_WORDS = [
    "局部关键区域", "关键主体或背景", "轮廓边缘处", "关键区域", "局部主体",
    "部分区域", "某些区域", "画面主体", "某些物体", "某些部位"
]

DEFECT_NAME_MAP = {
    "A": "缺色",
    "B": "溢色",
    "C": "错色",
    "D": "偏色",
    "E1": "过饱和",
    "E2": "欠饱和",
    "F": "视觉自然度"
}

# 120 Reviews for Batch 15
BATCH_15_REVIEWS = {
    # Sheet 01
    3284: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "左侧木栅栏明亮木黄色严重暗沉褪色，全图整体偏青冷暗调。"},
            {"id": "E2", "severity": "L1", "description": "木栅栏与背景草木色彩饱和度欠缺发暗。"}
        ],
        "note": "左侧木栅栏明亮木黄色严重暗沉褪色，全图整体偏青冷暗调(偏色 D-L2)，木栅栏与背景草木色彩饱和度欠缺(欠饱和 E2-L1)。"
    },
    3286: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "餐桌上的白碗中燕麦糊被过度上色为刺眼的浓郁橙黄色。"},
            {"id": "D", "severity": "L1", "description": "整体桌面与餐具环境明显偏暖黄橙色。"}
        ],
        "note": "餐桌上的白碗中燕麦糊被过度上色为刺眼的浓郁橙黄色(过饱和 E1-L2)，整体桌面与餐具环境明显偏暖黄(偏色 D-L1)。"
    },
    3290: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3293: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "黄色餐盘以及盘中的通心粉沙拉上色过于浓艳刺眼，黄色高光溢出。"}
        ],
        "note": "黄色餐盘以及盘中的通心粉沙拉上色过于浓艳刺眼，黄色高光溢出(过饱和 E1-L2)。"
    },
    3294: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "办公隔间右侧原本微暖的隔板墙面与桌面失去自然暖光，整体偏冷灰。"},
            {"id": "E2", "severity": "L1", "description": "办公隔板墙面与桌面色彩略显暗沉泛灰。"}
        ],
        "note": "办公隔间右侧原本微暖的隔板墙面与桌面失去自然暖光，整体偏冷灰(偏色 D-L1)，局部环境色彩略显暗沉泛灰(欠饱和 E2-L1)。"
    },
    3297: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "沙发上的编织毛绒小熊原本为青绿色，被明显错涂为浅棕黄色。"},
            {"id": "D", "severity": "L1", "description": "长毛小狗身后背景暗部略显偏暖红褐。"}
        ],
        "note": "沙发上的编织毛绒小熊原本为青绿色，被明显错涂为浅棕黄色(错色 C-L2)，背景局部暗部略显偏暖(偏色 D-L1)。"
    },

    # Sheet 02
    3299: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "银色皮卡车身与前保险杠金属表面略带轻微冷蓝光泽，地面枯黄草坪颜色略微偏暖。"}
        ],
        "note": "银色皮卡车身与前保险杠金属表面略带轻微冷蓝光泽，地面枯黄草坪颜色略微偏暖(偏色 D-L1)。"
    },
    3309: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L1", "description": "汽车前排座椅上的黑色双肩背包右侧暗红色拉链袋被过度渲染为鲜艳刺眼的玫粉色。"},
            {"id": "B", "severity": "L1", "description": "背包右侧拉链袋鲜艳粉色边缘向黑色背带处轻微渗透溢色。"}
        ],
        "note": "汽车前排座椅上的黑色双肩背包右侧暗红色拉链袋被过度渲染为鲜艳刺眼的玫粉色(过饱和 E1-L1)，粉色边缘有轻微向背带处渗透溢色(溢色 B-L1)。"
    },
    3315: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L2", "description": "小男孩身上的蓝白条纹翻领衬衫蓝色线条严重褪色泛灰，面部肤色苍白缺乏自然血色。"},
            {"id": "D", "severity": "L1", "description": "人物整体环境略泛青灰冷调。"},
            {"id": "F", "severity": "L1", "description": "肖像色彩整体暗淡缺乏生机。"}
        ],
        "note": "小男孩身上的蓝白条纹翻领衬衫蓝色线条严重褪色泛灰，面部肤色苍白缺乏自然血色(欠饱和 E2-L2)，人物整体环境略泛青灰冷调(偏色 D-L1)，视觉自然度略受影响(视觉自然度 F-L1)。"
    },
    3316: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "水果摊上悬挂的大串香蕉以及摊位木质货架整体被浓郁刺眼的暖黄橙光笼罩，老人发丝与背景均出现明显偏色。"},
            {"id": "E1", "severity": "L1", "description": "挂着的香蕉表皮黄色偏浓艳过饱和。"}
        ],
        "note": "水果摊上悬挂的大串香蕉以及摊位木质货架整体被浓郁刺眼的暖黄橙光笼罩，老人发丝与背景均出现明显偏色(偏色 D-L2)，香蕉表皮黄色偏浓(过饱和 E1-L1)。"
    },
    3323: {
        "pass": False,
        "defects": [
            {"id": "B", "severity": "L1", "description": "厨房操作台上男子切菜的木质砧板棕褐色漆料向灰色台面发生轻微边缘溢色。"},
            {"id": "D", "severity": "L1", "description": "木质砧板与切片白萝卜表面略微偏暖泛红。"}
        ],
        "note": "厨房操作台上男子切菜的木质砧板棕褐色漆料向灰色台面发生轻微边缘溢色(溢色 B-L1)，砧板与切片白萝卜表面略微偏暖泛红(偏色 D-L1)。"
    },
    3328: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "厨房天花板靠近吊灯边缘及远处门厅阴影处略微偏冷泛青。"}
        ],
        "note": "厨房天花板靠近吊灯边缘及远处门厅阴影处略微偏冷泛青(偏色 D-L1)。"
    },

    # Sheet 03
    3332: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "果盘中原本鲜红诱人的红苹果表面被严重错涂为诡异的荧光黄绿色斑块。"},
            {"id": "E1", "severity": "L2", "description": "盘内橙子与苹果的整体饱和度过于刺眼浓烈。"},
            {"id": "F", "severity": "L1", "description": "水果表面产生突兀违和的斑驳杂色。"}
        ],
        "note": "果盘中原本鲜红诱人的红苹果表面被严重错涂为诡异的荧光黄绿色斑块(错色 C-L2)，盘内橙子与苹果的整体饱和度过于刺眼浓烈(过饱和 E1-L2)，视觉自然度受损(视觉自然度 F-L1)。"
    },
    3334: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "停机坪上空原本清澈蔚蓝的天空被完全误涂为污浊昏暗的泥黄褐色。"},
            {"id": "D", "severity": "L2", "description": "全图天空与停机坪跑道整体严重泛暖黄泥色。"},
            {"id": "E2", "severity": "L1", "description": "白色客机机身色彩暗淡缺乏光彩。"}
        ],
        "note": "停机坪上空原本清澈蔚蓝的天空被完全误涂为污浊昏暗的泥黄褐色(常识错色 C-L3)，全图天空与停机坪整体严重泛暖黄泥色(偏色 D-L2)，白色客机机身色彩暗淡(欠饱和 E2-L1)。"
    },
    3338: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "网球场上网球手面部原本健康的肤色及白色运动T恤被大面积污染为诡异渗人的暗冷绿色。"},
            {"id": "F", "severity": "L2", "description": "人物面容呈现严重的冷绿失真与病态视觉违和感。"}
        ],
        "note": "网球场上网球手面部原本健康的肤色及白色运动T恤被大面积污染为诡异渗人的暗冷绿色(偏色 D-L2)，人物面容呈现严重的视觉失真与违和感(视觉自然度 F-L2)。"
    },
    3340: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "右侧男子深色T恤胸前原本鲜艳醒目的明黄色‘5’字印花图案被严重脱色错涂为灰白色。"},
            {"id": "E2", "severity": "L2", "description": "T恤胸前黄色数字印花色彩严重欠饱和泛灰。"}
        ],
        "note": "右侧男子深色T恤胸前原本鲜艳醒目的明黄色‘5’字印花图案被严重脱色错涂为灰白色(错色 C-L2)，印花色彩严重欠饱和泛灰(欠饱和 E2-L2)。"
    },
    3347: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3353: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "酒店客房内白色双人床床单与枕头受环境光影响略带微弱冷蓝灰偏色。"}
        ],
        "note": "酒店客房内白色双人床床单与枕头受环境光影响略带微弱冷蓝灰偏色(偏色 D-L1)。"
    },

    # Sheet 04
    3355: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L1", "description": "大棕熊背部与头顶棕色毛发色彩略显浓艳过饱和。"},
            {"id": "D", "severity": "L1", "description": "棕熊毛发表层微偏暖红褐色。"}
        ],
        "note": "大棕熊背部与头顶棕色毛发色彩略显浓艳过饱和(过饱和 E1-L1)，局部毛发表层微偏暖红褐色(偏色 D-L1)。"
    },
    3356: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "公路上的骑行男子身上原本清爽的蓝色骑行运动服被严重错涂为刺眼突兀的洋红粉紫色。"},
            {"id": "B", "severity": "L1", "description": "粉色骑行服向手臂边缘有轻微溢色扩散。"},
            {"id": "F", "severity": "L1", "description": "骑行者衣着色彩极度违和突兀。"}
        ],
        "note": "公路上的骑行男子身上原本清爽的蓝色骑行运动服被严重错涂为刺眼突兀的洋红粉紫色(常识错色 C-L3)，粉色向手臂边缘有轻微溢色扩散(溢色 B-L1)，视觉观感极为失真(视觉自然度 F-L1)。"
    },
    3360: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L1", "description": "悬挂在街道上方的红色交通信号灯与黄色路况指示牌色彩略显过于浓艳。"}
        ],
        "note": "悬挂在街道上方的红色交通信号灯与黄色路况指示牌色彩略显过于浓艳(过饱和 E1-L1)。"
    },
    3361: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "婚礼上切蛋糕的新娘面部肤色及纯白婚纱被严重污染为暗淡的冷蓝紫色。"},
            {"id": "F", "severity": "L2", "description": "新人肤色与白色礼服出现明显杂色色斑。"},
            {"id": "E2", "severity": "L1", "description": "新人面颊原本的红润血色严重缺失泛灰。"}
        ],
        "note": "婚礼上切蛋糕的新娘面部肤色及纯白婚纱被严重污染为暗淡的冷蓝紫色(偏色 D-L2)，人物肤色与白色礼服出现明显杂色色斑(视觉自然度 F-L2)，面部血色有所缺失(欠饱和 E2-L1)。"
    },
    3362: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L2", "description": "田野土路两侧原本带生机的开阔草地及远处缓坡草木严重褪色泛灰。"},
            {"id": "D", "severity": "L1", "description": "草坪整体环境略显冷暗色调偏移。"}
        ],
        "note": "田野土路两侧原本带生机的开阔草地及远处缓坡草木严重褪色泛灰(欠饱和 E2-L2)，草坪整体环境略显冷暗色调偏移(偏色 D-L1)。"
    },
    3364: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "电视机后方白色墙壁及桌面受冷光影响偏冷白色调。"}
        ],
        "note": "电视机后方白色墙壁及桌面受冷光影响偏冷白色调(偏色 D-L1)。"
    },

    # Sheet 05
    3367: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "果筐中带绿叶的鲜橙与橘子表皮橙红色泽过于浓艳刺眼。"}
        ],
        "note": "果筐中带绿叶的鲜橙与橘子表皮橙红色泽过于浓艳刺眼(过饱和 E1-L2)。"
    },
    3370: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3371: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "室内木地板靠近门口处及墙壁阴影略微泛冷蓝光晕。"}
        ],
        "note": "室内木地板靠近门口处及墙壁阴影略微泛冷蓝光晕(偏色 D-L1)。"
    },
    3373: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "穿着蕾丝花边的少女双腿上原本鲜艳醒目的大红色过膝高筒袜被严重错涂为暗沉的深蓝紫色。"},
            {"id": "F", "severity": "L2", "description": "整体腿部服饰色彩严重失真违和。"}
        ],
        "note": "穿着蕾丝花边的少女双腿上原本鲜艳醒目的大红色过膝高筒袜被严重错涂为暗沉的深蓝紫色(常识错色 C-L3)，整体服饰色彩严重失真违和(视觉自然度 F-L2)。"
    },
    3374: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "单人床铺上原本鲜亮醒目的橙黄色被褥被严重脱色错涂为苍白的淡粉灰白色。"},
            {"id": "E2", "severity": "L2", "description": "床上被褥色彩饱和度严重丢失。"}
        ],
        "note": "单人床铺上原本鲜亮醒目的橙黄色被褥被严重脱色错涂为苍白的淡粉灰白色(常识错色 C-L3)，被褥色彩饱和度严重丢失(欠饱和 E2-L2)。"
    },
    3384: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L3", "description": "卫生间内马桶、墙壁及金属扶手色彩极度匮乏几近灰阶脱色。"},
            {"id": "D", "severity": "L2", "description": "全景大面积笼罩在脏污的暗黄褐色调中。"},
            {"id": "F", "severity": "L2", "description": "视觉观感极为陈旧压抑失调。"}
        ],
        "note": "卫生间内马桶、墙壁及金属扶手色彩极度匮乏几近灰阶脱色(欠饱和 E2-L3)，全景大面积笼罩在脏污的暗黄褐色调中(偏色 D-L2)，视觉观感极为陈旧压抑(视觉自然度 F-L2)。"
    },

    # Sheet 06
    3387: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "摩托车上的金毛犬黄色毛发及骑车女子粉红外套色彩略显欠饱和发暗。"},
            {"id": "D", "severity": "L1", "description": "全景略带微弱冷灰色调偏移。"}
        ],
        "note": "摩托车上的金毛犬黄色毛发及骑车女子粉红外套色彩略显欠饱和发暗(欠饱和 E2-L1)，全景略带微弱冷灰色调偏移(偏色 D-L1)。"
    },
    3396: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "刷牙男子的面颊与鼻尖肤色受光照略微偏暖黄。"}
        ],
        "note": "刷牙男子的面颊与鼻尖肤色受光照略微偏暖黄(偏色 D-L1)。"
    },
    3397: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L1", "description": "厨房微波炉上方棕木橱柜面板以及下方黄色汤锅色彩略显浓艳过饱和。"}
        ],
        "note": "厨房微波炉上方棕木橱柜面板以及下方黄色汤锅色彩略显浓艳过饱和(过饱和 E1-L1)。"
    },
    3408: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "黄色出租车车门内饰原本明艳的亮黄色被明显偏色为浑浊的冷青绿黄色。"},
            {"id": "F", "severity": "L2", "description": "车内手部与金属部件视觉观感失调违和。"}
        ],
        "note": "黄色出租车车门内饰原本明艳的亮黄色被明显偏色为浑浊的冷青绿黄色(偏色 D-L2)，车内手部与金属部件视觉观感失调违和(视觉自然度 F-L2)。"
    },
    3409: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "海滩上抱冲浪板男子头顶原本清爽的蔚青色天空被严重误涂为浑浊的橄榄黄绿色。"},
            {"id": "D", "severity": "L2", "description": "全图天空大面积笼罩在浓厚的泥黄偏色中。"},
            {"id": "F", "severity": "L1", "description": "天空晚霞渐变层次受损失真。"}
        ],
        "note": "海滩上抱冲浪板男子头顶原本清爽的蔚青色天空被严重误涂为浑浊的橄榄黄绿色(常识错色 C-L3)，全图天空大面积笼罩在浓厚的泥黄偏色中(偏色 D-L2)，视觉自然度受损(视觉自然度 F-L1)。"
    },
    3410: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 07
    3412: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "盛装游行中的白色骏马面部与鬃毛被明显偏色为冷青紫色。"},
            {"id": "F", "severity": "L1", "description": "骑手深蓝色制服与马鞍皮带色调失真不均。"}
        ],
        "note": "盛装游行中的白色骏马面部与鬃毛被明显偏色为冷青紫色(偏色 D-L2)，骑手深蓝色制服与马鞍皮带色调失真(视觉自然度 F-L1)。"
    },
    3413: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "发言男子身后原本鲜明翠绿的会议背景展板被严重脱色错涂为灰黄泥色。"},
            {"id": "E2", "severity": "L2", "description": "会议背景展板绿色饱和度严重缺失。"}
        ],
        "note": "发言男子身后原本鲜明翠绿的会议背景展板被严重脱色错涂为灰黄泥色(错色 C-L2)，背景看板绿色饱和度严重缺失(欠饱和 E2-L2)。"
    },
    3418: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3419: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "房间内拱形大梳妆镜周围原本浅橄榄黄绿色的墙壁被严重偏色为浓重浑浊的铁锈红褐色。"},
            {"id": "F", "severity": "L1", "description": "室内整体色彩氛围严重违和发闷。"}
        ],
        "note": "房间内拱形大梳妆镜周围原本浅橄榄黄绿色的墙壁被严重偏色为浓重浑浊的铁锈红褐色(偏色 D-L2)，室内整体色彩氛围严重违和(视觉自然度 F-L1)。"
    },
    3421: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "餐桌上的粉色马克杯与小男孩面部受光略微偏暗暖。"}
        ],
        "note": "餐桌上的粉色马克杯与小男孩面部受光略微偏暗暖(偏色 D-L1)。"
    },
    3422: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L2", "description": "合欢树下长颈鹿身旁开阔草原草地原本的金黄生机色彩严重褪色泛灰。"},
            {"id": "D", "severity": "L1", "description": "草原全景略显暗冷灰色调偏移。"}
        ],
        "note": "合欢树下长颈鹿身旁开阔草原草地原本的金黄生机色彩严重褪色泛灰(欠饱和 E2-L2)，全景略显暗冷灰色调偏移(偏色 D-L1)。"
    },

    # Sheet 08
    3424: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "路边消火栓上原本鲜艳醒目的红色心形涂鸦被严重脱色错涂为暗棕灰色。"},
            {"id": "E2", "severity": "L2", "description": "红色爱心涂鸦饱和度严重缺失。"},
            {"id": "D", "severity": "L1", "description": "消火栓全景略带暗冷偏色。"}
        ],
        "note": "路边消火栓上原本鲜艳醒目的红色心形涂鸦被严重脱色错涂为暗棕灰色(常识错色 C-L3)，红色爱心饱和度严重缺失(欠饱和 E2-L2)，整体略带暗冷偏色(偏色 D-L1)。"
    },
    3434: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3437: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "棒球场防守队员身后草坪挡墙绿色上色过于浓艳刺眼。"},
            {"id": "F", "severity": "L1", "description": "棒球场整体色彩层次略显失真。"}
        ],
        "note": "棒球场防守队员身后草坪挡墙绿色上色过于浓艳刺眼(过饱和 E1-L2)，球场整体色彩层次略显失真(视觉自然度 F-L1)。"
    },
    3438: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "白色轿车旁路边原本鲜红醒目的停车计时收费表被严重脱色错涂为灰白色。"},
            {"id": "E2", "severity": "L2", "description": "停车计时收费表与右侧背景行道树色彩严重欠饱和泛灰。"}
        ],
        "note": "白色轿车旁路边原本鲜红醒目的停车计时收费表被严重脱色错涂为灰白色(错色 C-L2)，计时表与右侧背景行道树色彩严重欠饱和泛灰(欠饱和 E2-L2)。"
    },
    3443: {
        "pass": False,
        "defects": [
            {"id": "B", "severity": "L1", "description": "黄昏钟楼顶部尖塔与砖石屋檐边缘暖黄色向深蓝天空背景有轻微溢色边缘。"},
            {"id": "D", "severity": "L1", "description": "钟楼外墙红砖色调略微偏暖红。"}
        ],
        "note": "黄昏钟楼顶部尖塔与砖石屋檐边缘暖黄色向深蓝天空背景有轻微溢色边缘(溢色 B-L1)，钟楼外墙红砖色调略微偏暖(偏色 D-L1)。"
    },
    3448: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 09
    3456: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "卫生间左侧原本鲜明的橙红色塑料水桶被严重脱色错涂为暗青灰色。"},
            {"id": "E2", "severity": "L2", "description": "塑料水桶与绿色马桶盖色彩严重欠饱和发暗。"},
            {"id": "D", "severity": "L1", "description": "室内墙体略显偏冷灰调。"}
        ],
        "note": "卫生间左侧原本鲜明的橙红色塑料水桶被严重脱色错涂为暗青灰色(错色 C-L2)，水桶与绿色马桶盖色彩严重欠饱和发暗(欠饱和 E2-L2)，室内墙体略显偏冷灰调(偏色 D-L1)。"
    },
    3465: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "白鹭胸腹部雪白羽毛受环境光影响略带微弱暖灰色偏。"}
        ],
        "note": "白鹭胸腹部雪白羽毛受环境光影响略带微弱暖灰色偏(偏色 D-L1)。"
    },
    3469: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "深红棕木质餐桌及盛盘中的红烧肉菜肴整体被严重偏色为青冷暗黑色。"},
            {"id": "E2", "severity": "L2", "description": "红烧肉肉质酱色严重褪色泛灰。"},
            {"id": "F", "severity": "L2", "description": "菜肴视觉上呈现暗沉变质感。"}
        ],
        "note": "深红棕木质餐桌及盛盘中的红烧肉菜肴整体被严重偏色为青冷暗黑色(偏色 D-L2)，肉质酱色严重褪色泛灰(欠饱和 E2-L2)，菜肴视觉上呈现暗沉变质感(视觉自然度 F-L2)。"
    },
    3470: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "骑行青年身穿的无袖运动背心粉红色调略显泛暗且偏冷。"}
        ],
        "note": "骑行青年身穿的无袖运动背心粉红色调略显泛暗且偏冷(偏色 D-L1)。"
    },
    3503: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "‘STOP DRIVING’红色警示标牌后方原本葱绿茂密的行道树冠被局部错涂为冷青蓝色。"},
            {"id": "D", "severity": "L1", "description": "背景树木整体色调偏冷泛蓝。"}
        ],
        "note": "‘STOP DRIVING’红色警示标牌后方原本葱绿茂密的行道树冠被局部错涂为冷青蓝色(错色 C-L2)，背景树木整体色调偏冷泛蓝(偏色 D-L1)。"
    },
    3504: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "公路施工路段上方原本规范的深绿色大型指路交通路牌被严重错涂为浑浊的红褐色。"},
            {"id": "D", "severity": "L1", "description": "路牌边缘色调轻微偏暖。"}
        ],
        "note": "公路施工路段上方原本规范的深绿色大型指路交通路牌被严重错涂为浑浊的红褐色(常识错色 C-L3)，路牌边缘色调轻微偏暖(偏色 D-L1)。"
    },

    # Sheet 10
    3508: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3511: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "湖面水波及游动野鸭羽毛边缘受反光影响略显偏冷青灰。"}
        ],
        "note": "湖面水波及游动野鸭羽毛边缘受反光影响略显偏冷青灰(偏色 D-L1)。"
    },
    3512: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3514: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "棒球场上小击球手身穿的道奇队蓝色棒球球衣与头盔蓝色上色过于浓艳刺眼。"},
            {"id": "D", "severity": "L1", "description": "棒球场草地色彩略显偏荧光黄绿。"}
        ],
        "note": "棒球场上小击球手身穿的道奇队蓝色棒球球衣与头盔蓝色上色过于浓艳刺眼(过饱和 E1-L2)，棒球场草地色彩略显偏荧光黄绿(偏色 D-L1)。"
    },
    3515: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "放置笔记本电脑的木质地板与茶几原本温馨的暖黄色调严重流失，整体被偏色为冷白青灰色。"},
            {"id": "E2", "severity": "L1", "description": "木质表面色彩欠饱和发干。"},
            {"id": "F", "severity": "L1", "description": "室内整体光影氛围失真。"}
        ],
        "note": "放置笔记本电脑的木质地板与茶几原本温馨的暖黄色调严重流失，整体被偏色为冷白青灰色(偏色 D-L2)，木质表面色彩欠饱和(欠饱和 E2-L1)，室内整体光影氛围失真(视觉自然度 F-L1)。"
    },
    3516: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 11
    3517: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "棒球场上挥棒打者身上原本深黑色的运动长袖上衣及击球头盔被明显错涂为宝蓝色。"},
            {"id": "D", "severity": "L1", "description": "身后防护网背景略显偏暗冷。"}
        ],
        "note": "棒球场上挥棒打者身上原本深黑色的运动长袖上衣及击球头盔被明显错涂为宝蓝色(错色 C-L2)，身后防护网背景略显偏暗冷(偏色 D-L1)。"
    },
    3518: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "展示架上陈列的红、蓝、绿多彩玻璃艺术花瓶色彩过于浓艳刺眼。"},
            {"id": "D", "severity": "L1", "description": "展示木架整体色调偏暖橙红。"}
        ],
        "note": "展示架上陈列的红、蓝、绿多彩玻璃艺术花瓶色彩过于浓艳刺眼(过饱和 E1-L2)，展示木架整体色调偏暖橙红(偏色 D-L1)。"
    },
    3520: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "滑板场后方原本温馨暖黄的木质背景墙面被严重偏色为暗冷青绿色。"},
            {"id": "E2", "severity": "L1", "description": "场地木板色彩饱和度缺失。"},
            {"id": "F", "severity": "L1", "description": "画面整体视觉层次发闷。"}
        ],
        "note": "滑板场后方原本温馨暖黄的木质背景墙面被严重偏色为暗冷青绿色(偏色 D-L2)，场地木板色彩饱和度缺失(欠饱和 E2-L1)，画面整体视觉层次发闷(视觉自然度 F-L1)。"
    },
    3521: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "逆光照射下的斑马背部原本明亮温暖的金黄色皮毛被明显偏色为暗沉的冷青灰泥色。"},
            {"id": "E2", "severity": "L1", "description": "背部皮毛光泽与饱和度有所减弱。"}
        ],
        "note": "逆光照射下的斑马背部原本明亮温暖的金黄色皮毛被明显偏色为暗沉的冷青灰泥色(偏色 D-L2)，背部皮毛光泽与饱和度有所减弱(欠饱和 E2-L1)。"
    },
    3523: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3524: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "卫生间内原本温润浅黄色的陶瓷马桶与洗手台盆被严重脱色错涂为冰冷暗淡的灰白色。"},
            {"id": "E2", "severity": "L2", "description": "陶瓷洁具原本的淡黄色彩完全褪色。"}
        ],
        "note": "卫生间内原本温润浅黄色的陶瓷马桶与洗手台盆被严重脱色错涂为冰冷暗淡的灰白色(错色 C-L2)，陶瓷洁具原本的淡黄色彩完全褪色(欠饱和 E2-L2)。"
    },

    # Sheet 12
    3525: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3526: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "餐桌上的烘焙大比萨芝士金黄色泽略显欠饱和偏暗。"},
            {"id": "D", "severity": "L1", "description": "全景略带微弱冷青蓝色调偏移。"}
        ],
        "note": "餐桌上的烘焙大比萨芝士金黄色泽略显欠饱和偏暗(欠饱和 E2-L1)，全景略带微弱冷青蓝色调偏移(偏色 D-L1)。"
    },
    3528: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "切块奶油蛋糕旁叠放的浅青绿色陶瓷餐盘被明显错涂为暗蓝色。"},
            {"id": "D", "severity": "L1", "description": "白色奶油表面略带微弱冷蓝灰偏色。"}
        ],
        "note": "切块奶油蛋糕旁叠放的浅青绿色陶瓷餐盘被明显错涂为暗蓝色(错色 C-L2)，白色奶油表面略带微弱冷蓝灰偏色(偏色 D-L1)。"
    },
    3529: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L2", "description": "小男孩手中所拿卷饼内的翠绿生菜叶严重褪色错涂为灰黄泥色。"},
            {"id": "D", "severity": "L1", "description": "男孩面部与衣着环境略泛冷灰偏色。"},
            {"id": "F", "severity": "L1", "description": "食物与人物整体呈现暗沉失真感。"}
        ],
        "note": "小男孩手中所拿卷饼内的翠绿生菜叶严重褪色错涂为灰黄泥色(欠饱和 E2-L2)，男孩面部与衣着环境略泛冷灰偏色(偏色 D-L1)，食物与人物整体呈现暗沉失真感(视觉自然度 F-L1)。"
    },
    3530: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "床单散落物品中原本鲜亮醒目的明黄色便签纸被严重脱色错涂为暗灰黄色。"},
            {"id": "E2", "severity": "L2", "description": "便签纸黄色饱和度严重流失。"}
        ],
        "note": "床单散落物品中原本鲜亮醒目的明黄色便签纸被严重脱色错涂为暗灰黄色(错色 C-L2)，便签纸黄色饱和度严重流失(欠饱和 E2-L2)。"
    },
    3531: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "快餐托盘左上角透明餐盒内原本鲜红欲滴的圣女果被明显错涂为暗沉的粉紫色。"},
            {"id": "D", "severity": "L1", "description": "托盘菜品整体环境略带微弱冷紫偏色。"}
        ],
        "note": "快餐托盘左上角透明餐盒内原本鲜红欲滴的圣女果被明显错涂为暗沉的粉紫色(错色 C-L2)，托盘菜品整体环境略带微弱冷紫偏色(偏色 D-L1)。"
    },

    # Sheet 13
    3533: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "客厅白色皮质沙发背部阴影处略泛冷灰偏色。"},
            {"id": "E2", "severity": "L1", "description": "窗帘深红布料色彩饱和度微弱缺失。"}
        ],
        "note": "客厅白色皮质沙发背部阴影处略泛冷灰偏色(偏色 D-L1)，窗帘深红布料色彩饱和度微弱缺失(欠饱和 E2-L1)。"
    },
    3534: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3535: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "旧式厨房内燃气灶台、水壶及周边墙面被严重偏色为昏暗浑浊的冷暗青紫色。"},
            {"id": "F", "severity": "L1", "description": "室内呈现明显的灰紫发霉失真感。"}
        ],
        "note": "旧式厨房内燃气灶台、水壶及周边墙面被严重偏色为昏暗浑浊的冷暗青紫色(偏色 D-L2)，室内呈现明显的灰紫发霉失真感(视觉自然度 F-L1)。"
    },
    3536: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "夜间床上女孩面部肤色及黑狗身躯被严重偏色为突兀诡异的暗紫红色。"},
            {"id": "F", "severity": "L2", "description": "原本温暖的室内床头暖光氛围彻底崩解失真。"},
            {"id": "E1", "severity": "L1", "description": "局部泛紫色彩过度刺眼。"}
        ],
        "note": "夜间床上女孩面部肤色及黑狗身躯被严重偏色为突兀诡异的暗紫红色(偏色 D-L2)，原本温暖的室内床头暖光氛围彻底崩解失真(视觉自然度 F-L2)，局部泛紫色彩过度刺眼(过饱和 E1-L1)。"
    },
    3539: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "水池岸边棕熊身后的草坪局部呈现偏荧光黄绿偏色。"},
            {"id": "E1", "severity": "L1", "description": "草地局部高光过浓。"}
        ],
        "note": "水池岸边棕熊身后的草坪局部呈现偏荧光黄绿偏色(偏色 D-L1)，草地局部高光过浓(过饱和 E1-L1)。"
    },
    3540: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "桌面背景铺垫的整块大红色布料被完全脱色错涂为深黑色。"},
            {"id": "E2", "severity": "L3", "description": "红色桌布与红色剪刀把手色彩饱和度几乎彻底归零。"},
            {"id": "F", "severity": "L2", "description": "全图色彩严重崩塌失真。"}
        ],
        "note": "桌面背景铺垫的整块大红色布料被完全脱色错涂为深黑色(常识错色 C-L3)，红色桌布与红色剪刀把手色彩饱和度几乎彻底归零(欠饱和 E2-L3)，全图色彩严重崩塌(视觉自然度 F-L2)。"
    },

    # Sheet 14
    3541: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "小女孩手中撑开的粉红色遮阳伞及画面左侧黄色标志牌色彩略显发暗欠饱和。"},
            {"id": "D", "severity": "L1", "description": "人行道与背景草坪略微偏冷青蓝调。"}
        ],
        "note": "小女孩手中撑开的粉红色遮阳伞及画面左侧黄色标志牌色彩略显发暗欠饱和(欠饱和 E2-L1)，人行道与背景草坪略微偏冷青蓝调(偏色 D-L1)。"
    },
    3544: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "牧场铁丝网旁原本浅绿底白色文字的‘CAR PARKING’圆形停车标志牌被明显错涂为白底绿字。"},
            {"id": "D", "severity": "L1", "description": "标牌金属边缘微带色偏。"}
        ],
        "note": "牧场铁丝网旁原本浅绿底白色文字的‘CAR PARKING’圆形停车标志牌被明显错涂为白底绿字(错色 C-L2)，标牌金属边缘微带色偏(偏色 D-L1)。"
    },
    3545: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "长颈鹿身上深棕色网状斑纹暗部及背景远景树冠色彩略显微弱欠饱和发暗。"}
        ],
        "note": "长颈鹿身上深棕色网状斑纹暗部及背景远景树冠色彩略显微弱欠饱和发暗(欠饱和 E2-L1)。"
    },
    3546: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "草原上行走的成年长颈鹿躯干金黄色网状斑纹毛皮色彩严重欠饱和泛灰。"},
            {"id": "D", "severity": "L1", "description": "长颈鹿身躯与背景天空略显偏冷暗灰色。"}
        ],
        "note": "草原上行走的成年长颈鹿躯干金黄色网状斑纹毛皮色彩严重欠饱和泛灰(欠饱和 E2-L1)，长颈鹿身躯与背景天空略显偏冷暗灰色(偏色 D-L1)。"
    },
    3548: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3549: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 15
    3550: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "海滩上空的晚霞余晖原本浪漫温暖的淡粉紫色被完全抹去，整体被偏色为清冷的蓝灰暗色。"},
            {"id": "E2", "severity": "L1", "description": "沙滩与海水表面的暖金光泽严重褪色。"}
        ],
        "note": "海滩上空的晚霞余晖原本浪漫温暖的淡粉紫色被完全抹去，整体被偏色为清冷的蓝灰暗色(偏色 D-L2)，沙滩与海水表面的暖金光泽严重褪色(欠饱和 E2-L1)。"
    },
    3551: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "地面上的被褥及室内光影被大面积偏色为冰冷惨白的冷青蓝色。"},
            {"id": "E2", "severity": "L1", "description": "胶片原有的温润暖色饱和度严重流失。"},
            {"id": "F", "severity": "L1", "description": "全景呈现惨白违和感。"}
        ],
        "note": "地面上的被褥及室内光影被大面积偏色为冰冷惨白的冷青蓝色(偏色 D-L2)，胶片原有的温润暖色饱和度严重流失(欠饱和 E2-L1)，全景呈现惨白违和感(视觉自然度 F-L1)。"
    },
    3552: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3554: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "客厅内原本温暖明亮的浅黄墙壁与天花板被严重偏色为昏暗污浊的冷青灰色。"},
            {"id": "E2", "severity": "L1", "description": "木质地板暖色饱和度局部失调。"},
            {"id": "F", "severity": "L1", "description": "室内整体采光氛围严重破坏。"}
        ],
        "note": "客厅内原本温暖明亮的浅黄墙壁与天花板被严重偏色为昏暗污浊的冷青灰色(偏色 D-L2)，木质地板暖色饱和度局部失调(欠饱和 E2-L1)，室内整体采光氛围严重破坏(视觉自然度 F-L1)。"
    },
    3556: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "小女孩手中抱着的粉色毛绒兔玩偶表面及女孩面颊略带微弱冷蓝灰偏色。"}
        ],
        "note": "小女孩手中抱着的粉色毛绒兔玩偶表面及女孩面颊略带微弱冷蓝灰偏色(偏色 D-L1)。"
    },
    3557: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "趴在床上的两名小男孩面部肤色被严重偏色为暗淡冰冷的青灰色。"},
            {"id": "E2", "severity": "L1", "description": "幼童面颊原本健康的红润血色严重缺失泛灰。"}
        ],
        "note": "趴在床上的两名小男孩面部肤色被严重偏色为暗淡冰冷的青灰色(偏色 D-L2)，幼童面颊原本健康的红润血色严重缺失泛灰(欠饱和 E2-L1)。"
    },

    # Sheet 16
    3559: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "日落港湾上空原本金黄明亮的晚霞云层及海面反光偏冷蓝灰色。"},
            {"id": "E2", "severity": "L1", "description": "落日温暖的暖光饱和度明显缺失。"}
        ],
        "note": "日落港湾上空原本金黄明亮的晚霞云层及海面反光偏冷蓝灰色(偏色 D-L1)，落日温暖的暖光饱和度明显缺失(欠饱和 E2-L1)。"
    },
    3560: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "法棍面包上方展示柜玻璃及背景被大面积严重偏色为刺眼的荧光深蓝色。"},
            {"id": "F", "severity": "L2", "description": "金黄的面包表皮被突兀冷蓝光斑污染失真。"}
        ],
        "note": "法棍面包上方展示柜玻璃及背景被大面积严重偏色为刺眼的荧光深蓝色(偏色 D-L2)，金黄的面包表皮被突兀冷蓝光斑污染(视觉自然度 F-L2)。"
    },
    3561: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3563: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "机场停机坪上空原本清澈蔚蓝的天空被严重误涂为浑浊暗淡的橄榄黄绿色。"},
            {"id": "D", "severity": "L2", "description": "全景大面积笼罩在泥黄色调中。"},
            {"id": "E2", "severity": "L1", "description": "客机机身色彩暗淡。"}
        ],
        "note": "机场停机坪上空原本清澈蔚蓝的天空被严重误涂为浑浊暗淡的橄榄黄绿色(常识错色 C-L3)，全景大面积笼罩在泥黄色调中(偏色 D-L2)，客机机身色彩暗淡(欠饱和 E2-L1)。"
    },
    3565: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "斑马身躯黑白条纹交界边缘及地面阴影略带轻微冷蓝光泽。"}
        ],
        "note": "斑马身躯黑白条纹交界边缘及地面阴影略带轻微冷蓝光泽(偏色 D-L1)。"
    },
    3566: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 17
    3567: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3569: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "冲浪板后方原本干燥枯黄的草地被明显错涂为鲜艳的翠绿色。"},
            {"id": "E1", "severity": "L1", "description": "背景草坪与小男孩受光皮肤色彩略显浓艳过饱和。"}
        ],
        "note": "冲浪板后方原本干燥枯黄的草地被明显错涂为鲜艳的翠绿色(错色 C-L2)，背景草坪与小男孩受光皮肤色彩略显浓艳过饱和(过饱和 E1-L1)。"
    },
    3570: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3571: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L2", "description": "餐盘中原本新鲜诱人的橙红三文鱼刺身生鱼片严重褪色偏紫。"},
            {"id": "D", "severity": "L2", "description": "三文鱼片及周边洋葱圈被偏色为暗沉的冷紫灰色。"},
            {"id": "F", "severity": "L2", "description": "海鲜刺身呈现严重的变质腐败感。"}
        ],
        "note": "餐盘中原本新鲜诱人的橙红三文鱼刺身生鱼片严重褪色偏紫(欠饱和 E2-L2)，三文鱼片及周边洋葱圈被偏色为暗沉的冷紫灰色(偏色 D-L2)，海鲜刺身呈现严重的变质腐败感(视觉自然度 F-L2)。"
    },
    3572: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3573: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 18
    3574: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "海鸥飞翔的海面海水原本清澈纯正的深蓝色严重欠饱和泛灰。"},
            {"id": "D", "severity": "L1", "description": "全景海水与远处岛屿树木略显偏冷青灰。"}
        ],
        "note": "海鸥飞翔的海面海水原本清澈纯正的深蓝色严重欠饱和泛灰(欠饱和 E2-L1)，全景海水与远处岛屿树木略显偏冷青灰(偏色 D-L1)。"
    },
    3575: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3576: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "神龛前供奉的各色鲜花花环与彩绘陶罐上色过于浓艳刺眼。"},
            {"id": "F", "severity": "L1", "description": "祭坛整体色彩层次过于拥挤杂乱。"}
        ],
        "note": "神龛前供奉的各色鲜花花环与彩绘陶罐上色过于浓艳刺眼(过饱和 E1-L2)，祭坛整体色彩层次过于拥挤杂乱(视觉自然度 F-L1)。"
    },
    3577: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "铁轨上停靠的两辆老式内燃机车原本鲜明的宝蓝车身与明黄车头前脸被彻底脱色错涂为纯黑白灰阶。"},
            {"id": "E2", "severity": "L3", "description": "整列机车车漆饱和度完全归零。"},
            {"id": "F", "severity": "L2", "description": "彩色工业画面严重退化为单色黑白。"}
        ],
        "note": "铁轨上停靠的两辆老式内燃机车原本鲜明的宝蓝车身与明黄车头前脸被彻底脱色错涂为纯黑白灰阶(常识错色 C-L3)，整列机车车漆饱和度完全归零(欠饱和 E2-L3)，彩色工业画面严重退化为单色(视觉自然度 F-L2)。"
    },
    3579: {
        "pass": False,
        "defects": [
            {"id": "B", "severity": "L2", "description": "盛放烘焙面点的白瓷盘边缘青蓝碎花纹样向白色盘面发生明显扩散渗透。"},
            {"id": "E1", "severity": "L1", "description": "盘中面包圈烘焙焦糖色略显过深浓艳。"}
        ],
        "note": "盛放烘焙面点的白瓷盘边缘青蓝碎花纹样向白色盘面发生明显扩散渗透(溢色 B-L2)，盘中面包圈烘焙焦糖色略显过深浓艳(过饱和 E1-L1)。"
    },
    3585: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "沙滩上原本金黄温暖的沙地被严重偏色为冰冷泛青的灰白泥色。"},
            {"id": "E2", "severity": "L1", "description": "沙滩与地面塑料玩具色彩饱和度严重流失。"}
        ],
        "note": "沙滩上原本金黄温暖的沙地被严重偏色为冰冷泛青的灰白泥色(偏色 D-L2)，沙滩与地面塑料玩具色彩饱和度严重流失(欠饱和 E2-L1)。"
    },

    # Sheet 19
    3587: {
        "pass": False,
        "defects": [
            {"id": "B", "severity": "L2", "description": "阳光合影中两名男子所穿的深黑色短袖T恤领口与肩臂边缘发生明显的色彩渗透溢色。"},
            {"id": "F", "severity": "L2", "description": "人物衣着边缘与背景交界处色彩杂乱失调。"}
        ],
        "note": "阳光合影中两名男子所穿的深黑色短袖T恤领口与肩臂边缘发生明显的色彩渗透溢色(溢色 B-L2)，人物衣着边缘与背景交界处色彩杂乱失调(视觉自然度 F-L2)。"
    },
    3588: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "走廊靠墙放置的浅紫色拉杆旅行箱箱体表面色彩严重欠饱和褪色泛灰。"},
            {"id": "D", "severity": "L2", "description": "后方原本暖黄的木质墙面被严重偏色为暗淡的冷青灰色。"},
            {"id": "F", "severity": "L1", "description": "整体视觉色彩层次发闷。"}
        ],
        "note": "走廊靠墙放置的浅紫色拉杆旅行箱箱体表面色彩严重欠饱和褪色泛灰(欠饱和 E2-L1)，后方原本暖黄的木质墙面被严重偏色为暗淡的冷青灰色(偏色 D-L2)，整体视觉色彩层次发闷(视觉自然度 F-L1)。"
    },
    3589: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3591: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3592: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "床上原本具有明亮温暖金黄色泽的针织毛毯及橘猫毛发被完全脱色错涂为冷白灰调。"},
            {"id": "E2", "severity": "L3", "description": "毛毯与宠物毛色饱和度几乎丧失殆尽。"},
            {"id": "D", "severity": "L2", "description": "全景严重偏冷青灰。"},
            {"id": "F", "severity": "L2", "description": "原本温暖的居家光影氛围彻底崩坏。"}
        ],
        "note": "床上原本具有明亮温暖金黄色泽的针织毛毯及橘猫毛发被完全脱色错涂为冷白灰调(错色 C-L2)，毛毯与宠物毛色饱和度几乎丧失殆尽(欠饱和 E2-L3)，全景严重偏冷青灰(偏色 D-L2)，原本温暖的居家光影氛围彻底崩坏(视觉自然度 F-L2)。"
    },
    3593: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "客机商务舱座椅隔板内饰及机舱侧壁被明显偏色为清冷的蓝青紫色。"},
            {"id": "E2", "severity": "L1", "description": "座椅周边原本温馨的暖黄阅读光效严重暗淡缺失。"}
        ],
        "note": "客机商务舱座椅隔板内饰及机舱侧壁被明显偏色为清冷的蓝青紫色(偏色 D-L2)，座椅周边原本温馨的暖黄阅读光效严重暗淡缺失(欠饱和 E2-L1)。"
    },

    # Sheet 20
    3594: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L1", "description": "腾空击球的网球手所穿的亮黄色运动上衣上色过于浓艳。"},
            {"id": "B", "severity": "L1", "description": "球衣边缘黄色微向手臂外缘溢色扩散。"},
            {"id": "D", "severity": "L1", "description": "球场地表微带暖偏。"}
        ],
        "note": "腾空击球的网球手所穿的亮黄色运动上衣上色过于浓艳(过饱和 E1-L1)，球衣边缘黄色微向手臂外缘溢色扩散(溢色 B-L1)，球场地表微带暖偏(偏色 D-L1)。"
    },
    3595: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "停机坪上英航客机垂直尾翼原本鲜红醒目的航司标识被严重脱色错涂为暗沉的蓝灰色。"},
            {"id": "E2", "severity": "L2", "description": "周围客机尾翼涂装色彩普遍欠饱和发暗。"},
            {"id": "D", "severity": "L1", "description": "天空整体略泛泥黄暗调。"}
        ],
        "note": "停机坪上英航客机垂直尾翼原本鲜红醒目的航司标识被严重脱色错涂为暗沉的蓝灰色(常识错色 C-L3)，周围客机尾翼涂装色彩普遍欠饱和发暗(欠饱和 E2-L2)，天空整体略泛泥黄暗调(偏色 D-L1)。"
    },
    3596: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "室内地面原本鲜红的大面积地毯被严重偏色为暗冷浑浊的红褐色。"},
            {"id": "F", "severity": "L1", "description": "女子衣着暗部与地毯交界处呈现不自然的杂色色斑。"}
        ],
        "note": "室内地面原本鲜红的大面积地毯被严重偏色为暗冷浑浊的红褐色(偏色 D-L2)，女子衣着暗部与地毯交界处呈现不自然的杂色色斑(视觉自然度 F-L1)。"
    },
    3597: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L2", "description": "长颈鹿身后的茂密树林与地面草坪原本葱绿生机的色彩严重脱色褪白。"},
            {"id": "D", "severity": "L2", "description": "整个林地环境被严重的冷青灰偏色所笼罩。"}
        ],
        "note": "长颈鹿身后的茂密树林与地面草坪原本葱绿生机的色彩严重脱色褪白(欠饱和 E2-L2)，整个林地环境被严重的冷青灰偏色所笼罩(偏色 D-L2)。"
    },
    3598: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3599: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "办公桌面上原本鲜明醒目的蓝色文件夹及工位蓝色彩色隔板被严重脱色错涂为苍白的灰白色。"},
            {"id": "E2", "severity": "L2", "description": "办公用品色彩饱和度严重丢失。"}
        ],
        "note": "办公桌面上原本鲜明醒目的蓝色文件夹及工位蓝色彩色隔板被严重脱色错涂为苍白的灰白色(错色 C-L2)，办公用品色彩饱和度严重丢失(欠饱和 E2-L2)。"
    }
}

def validate_reviews():
    assert len(BATCH_15_REVIEWS) == 120, f"Expected 120 reviews, got {len(BATCH_15_REVIEWS)}"
    for task_id, rev in BATCH_15_REVIEWS.items():
        is_pass = rev["pass"]
        note = rev["note"]
        defects = rev["defects"]

        # Check banned words
        for bw in BANNED_WORDS:
            if bw in note:
                raise ValueError(f"Task #{task_id} contains banned word '{bw}' in note: {note}")
            for d in defects:
                if bw in d["description"]:
                    raise ValueError(f"Task #{task_id} contains banned word '{bw}' in defect description: {d['description']}")

        if is_pass:
            assert len(defects) == 0, f"Pass task #{task_id} has defects: {defects}"
            assert note == "审查通过", f"Pass task #{task_id} note is not '审查通过': {note}"
        else:
            assert len(defects) > 0, f"Non-pass task #{task_id} has no defects"
            for d in defects:
                assert d["id"] in DEFECT_NAME_MAP, f"Invalid defect id: {d['id']}"
                if d["id"] == "A":
                    assert d.get("severity") in ["", None], f"A cannot have severity: {d}"
                else:
                    assert d.get("severity") in ["L1", "L2", "L3"], f"Defect must have L1/L2/L3 severity: {d}"
                assert "name" in d or d["id"] in DEFECT_NAME_MAP

def apply_to_deliverables():
    # Save intermediate grounding JSON
    grounding_data = {}
    for task_id, rev in BATCH_15_REVIEWS.items():
        grounding_data[str(task_id)] = {
            "task_id": task_id,
            "pass": rev["pass"],
            "defects": [
                {
                    "id": d["id"],
                    "name": DEFECT_NAME_MAP[d["id"]],
                    "severity": d.get("severity", ""),
                    "description": d["description"]
                }
                for d in rev["defects"]
            ],
            "review_note": rev["note"]
        }

    with open(GROUNDING_OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(grounding_data, f, ensure_ascii=False, indent=2)
    print(f"Saved grounding audit to {GROUNDING_OUT_PATH}")

    # Synchronize reviewed_1_10000_all.json
    print(f"Loading {ALL_JSON_PATH}...")
    with open(ALL_JSON_PATH, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    updated_count = 0
    for ann in all_data.get("annotations", []):
        t_id = ann.get("human_review", {}).get("task_id")
        if t_id in BATCH_15_REVIEWS:
            rev = BATCH_15_REVIEWS[t_id]
            ann["review_status"] = "已核验"
            ann["review_note"] = rev["note"]
            ann["defects"] = [
                {
                    "id": d["id"],
                    "name": DEFECT_NAME_MAP[d["id"]],
                    "severity": d.get("severity", ""),
                    "description": d["description"]
                }
                for d in rev["defects"]
            ]
            has_A = any(d["id"] == "A" for d in rev["defects"])
            if has_A:
                ann["reviewed_score"] = 1.0
                ann["needs_rescoring"] = False
            else:
                ann["reviewed_score"] = None
                ann["needs_rescoring"] = True
            updated_count += 1

    with open(ALL_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {updated_count} items in {ALL_JSON_PATH}")

    # Synchronize reviewed_1_10000_clean.json
    print(f"Loading {CLEAN_JSON_PATH}...")
    with open(CLEAN_JSON_PATH, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    updated_clean_count = 0
    for ann in clean_data.get("annotations", []):
        t_id = ann.get("human_review", {}).get("task_id")
        if t_id in BATCH_15_REVIEWS:
            rev = BATCH_15_REVIEWS[t_id]
            ann["review_status"] = "已核验"
            ann["review_note"] = ""  # Clean version leaves note empty
            ann["defects"] = [
                {
                    "id": d["id"],
                    "name": DEFECT_NAME_MAP[d["id"]],
                    "severity": d.get("severity", ""),
                    "description": d["description"]
                }
                for d in rev["defects"]
            ]
            has_A = any(d["id"] == "A" for d in rev["defects"])
            if has_A:
                ann["reviewed_score"] = 1.0
                ann["needs_rescoring"] = False
            else:
                ann["reviewed_score"] = None
                ann["needs_rescoring"] = True
            updated_clean_count += 1

    with open(CLEAN_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {updated_clean_count} items in {CLEAN_JSON_PATH}")

if __name__ == "__main__":
    validate_reviews()
    print(f"Total reviews defined: {len(BATCH_15_REVIEWS)}")
    apply_to_deliverables()
