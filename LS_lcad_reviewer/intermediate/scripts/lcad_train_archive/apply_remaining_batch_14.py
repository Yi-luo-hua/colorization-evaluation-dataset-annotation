#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_remaining_batch_14.py
根据对 Batch 14（Tasks 2904 ~ 3272，共 120 组）的 20 张高清看板多模态大图直审结果，
1. 生成中间定物审计文件 grounding_remaining_batch_14.json；
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
OUT_GROUNDING_FILE = AUDITS_DIR / "grounding_remaining_batch_14.json"

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
    # Sheet 01: [2904, 2906, 2908, 2911, 2912, 2917]
    2904: {
        "is_pass": False,
        "severities": {"D": "L3", "E1": "L2", "F": "L2"},
        "note": "客厅墙面被大面积严重涂染为刺眼不自然的荧光紫红偏色，室内洋红伪色过于浓艳刺眼（严重偏色 D-L3，过饱和 E1-L2，视觉自然度受损 F-L2）。"
    },
    2906: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2908: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2911: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2"},
        "note": "卫生间暖黄褐色瓷砖墙面大面积泛发暗冷青灰偏色，环境暖木色瓷砖色彩严重发灰脱色（偏色 D-L2，欠饱和 E2-L2）。"
    },
    2912: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2", "F": "L1"},
        "note": "原本冷灰蓝色的桌面托盘与深蓝咖啡杯被严重错涂为焦黄砖红色，全图严重泛焦黄红偏色（严重常识错色 C-L3，偏色 D-L2，视觉自然度轻度受损 F-L1）。"
    },
    2917: {
        "is_pass": False,
        "severities": {"E2": "L1", "D": "L1"},
        "note": "夜间巡逻骑警身穿的鲜红防寒风衣外套色泽脱色暗淡发灰，左侧马匹棕黄毛皮微泛冷灰（轻度欠饱和 E2-L1，轻度偏色 D-L1）。"
    },

    # Sheet 02: [2919, 2921, 2922, 2923, 2926, 2927]
    2919: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L1", "E2": "L2"},
        "note": "大象身后生机盎然的鲜绿树丛草坡被严重错涂为干旱焦黄泥土色，自然绿色生机彻底丧失（严重常识错色 C-L3，轻度偏色 D-L1，欠饱和 E2-L2）。"
    },
    2921: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2"},
        "note": "室内暖黄墙面大面积泛发暗冷青褐偏色，橘猫毛发与环境暖色光泽严重褪色发灰（偏色 D-L2，欠饱和 E2-L2）。"
    },
    2922: {
        "is_pass": False,
        "severities": {"E1": "L1", "D": "L1"},
        "note": "女子身穿的红白碎花衬衫在室内光照下红色略显过饱和，背景盆栽绿叶微泛色偏（轻度过饱和 E1-L1，轻度偏色 D-L1）。"
    },
    2923: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L1", "F": "L1"},
        "note": "餐桌台面大面积偏暖严重泛焦黄砖红偏色，红木色调偏浓（偏色 D-L2，轻度过饱和 E1-L1，视觉自然度轻度受损 F-L1）。"
    },
    2926: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2", "B": "L2", "F": "L3"},
        "note": "网球场深灰绿地面被常识性严重恶性错涂为突兀刺眼的荧光粉红色，粉红颜色溢出色斑侵染球拍与裤管（恶性常识错色 C-L3，偏色 D-L2，溢色 B-L2，视觉自然度极度恶化 F-L3）。"
    },
    2927: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 03: [2928, 2930, 2936, 2937, 2943, 2944]
    2928: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2930: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2936: {
        "is_pass": False,
        "severities": {"E2": "L2", "D": "L1", "F": "L1"},
        "note": "游行演员身穿的亮蓝色演出服大面积脱色发灰，面部肤色微泛冷灰偏色（欠饱和 E2-L2，轻度偏色 D-L1，视觉自然度轻度受损 F-L1）。"
    },
    2937: {
        "is_pass": False,
        "severities": {"D": "L2", "F": "L2"},
        "note": "黑猫背部毛发被严重涂染为焦黄锈褐色伪色，黑猫毛发质感严重失真（偏色 D-L2，视觉自然度受损 F-L2）。"
    },
    2943: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L1", "F": "L2"},
        "note": "防守方橄榄球队员身穿的深蓝色比赛球衣被严重常识性错涂为亮黄色，两队球服颜色混淆，比赛辨识度严重受损（严重常识错色 C-L3，轻度偏色 D-L1，视觉自然度受损 F-L2）。"
    },
    2944: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2", "F": "L2"},
        "note": "原本晴朗湛蓝的纯净晴空被严重错涂为大片发红的紫粉色雾霾，全图天空与地面泛发严重紫红偏色（严重常识错色 C-L3，偏色 D-L2，视觉自然度受损 F-L2）。"
    },

    # Sheet 04: [2946, 2947, 2948, 2950, 2952, 2953]
    2946: {
        "is_pass": False,
        "severities": {"D": "L1", "F": "L1"},
        "note": "生日巧克力蛋糕外层奶油裱花与点燃蜡烛周边区域微泛冷青偏色，暖光温馨感轻微削弱（轻度偏色 D-L1，视觉自然度轻度受损 F-L1）。"
    },
    2947: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2"},
        "note": "室内鹅黄色壁纸墙面大面积泛发暗冷青灰偏色，环境暖色调与复古婴儿车色彩严重发灰脱色（偏色 D-L2，欠饱和 E2-L2）。"
    },
    2948: {
        "is_pass": False,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "停机坪汉莎航空民航客机白色机身背光面与登机廊桥金属外壳微泛青蓝冷色杂斑，反光轻微过饱和（轻度偏色 D-L1，轻度过饱和 E1-L1，视觉自然度轻度受损 F-L1）。"
    },
    2950: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "移动美食餐车醒目的亮黄绿色车体被严重剥色错涂为暗淡米白色，餐车与排队顾客服饰色彩严重褪淡发暗（严重常识错色 C-L3，欠饱和 E2-L2）。"
    },
    2952: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2953: {
        "is_pass": False,
        "severities": {"D": "L2", "F": "L2"},
        "note": "昏暗酒吧室内环境与人物面部大面积被严重涂染为焦黄红褐色伪色，暗光噪点区域色彩失真（偏色 D-L2，视觉自然度受损 F-L2）。"
    },

    # Sheet 05: [2954, 2956, 2957, 2958, 2959, 2961]
    2954: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L1", "F": "L1"},
        "note": "聚餐合影人物面部肤色大面积泛发暗冷青灰偏色，人物肤色血色褪淡（偏色 D-L2，轻度欠饱和 E2-L1，视觉自然度轻度受损 F-L1）。"
    },
    2956: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "卧室窗前原本厚重的深红色丝绒窗帘大面积剥色错涂为暗黑灰色，窗帘红色质感严重丧失（错色 C-L2，欠饱和 E2-L2）。"
    },
    2957: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2958: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L1"},
        "note": "热狗招牌外围原本明亮的浅绿色装饰边框被严重剥色错涂为苍白灰色，热狗面包微泛焦褐偏色（严重常识错色 C-L3，轻度偏色 D-L1）。"
    },
    2959: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2961: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "庭院白色木椅后方背景墙面微泛淡粉红暖色偏，盆栽绿叶色泽略深（轻度偏色 D-L1）。"
    },

    # Sheet 06: [2962, 2964, 2966, 2967, 2969, 2972]
    2962: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "青年手中抛出的鲜艳正红色塑料飞盘被常识性严重剥色错涂为浅灰白色，飞盘红色完全褪丧（严重常识错色 C-L3，欠饱和 E2-L2）。"
    },
    2964: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "树林背景绿叶与马背深棕色毛发表层微泛暗紫红杂色伪色，女孩红衣轻微褪色（轻度偏色 D-L1，轻度欠饱和 E2-L1）。"
    },
    2966: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "雨后湿滑沥青路面与后视镜反光被严重涂染为刺眼不自然的荧光紫红偏色，夜景反光过于浓艳失真（偏色 D-L2，过饱和 E1-L2，视觉自然度受损 F-L2）。"
    },
    2967: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "网球场看台后方观众席微泛轻微暖粉色偏，球场地表深蓝还原忠实（轻度偏色 D-L1）。"
    },
    2969: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2"},
        "note": "海滨沙滩背景大面积泛发暗冷青灰偏色，沙滩暖黄金色与晚霞光泽严重剥除褪丧（偏色 D-L2，欠饱和 E2-L2）。"
    },
    2972: {
        "is_pass": False,
        "severities": {"E1": "L2", "D": "L1", "F": "L1"},
        "note": "草坡公共艺术雕塑表面的天蓝与鲜绿漆面过于浓艳刺眼，阴影略显泛深墨蓝（过饱和 E1-L2，轻度偏色 D-L1，视觉自然度轻度受损 F-L1）。"
    },

    # Sheet 07: [2973, 2974, 2975, 2978, 2980, 2981]
    2973: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L1", "F": "L2"},
        "note": "双层观光敞篷巴士醒目的鲜绿色下层车体被常识性严重错涂为亮橙黄色，公共交通标识色彩严重错配（严重常识错色 C-L3，轻度偏色 D-L1，视觉自然度受损 F-L2）。"
    },
    2974: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2", "D": "L2"},
        "note": "黑猫躺卧的鲜艳大红色棉被被严重脱色错涂为暗蓝灰色，全图严重泛冷蓝紫偏色（严重常识错色 C-L3，欠饱和 E2-L2，偏色 D-L2）。"
    },
    2975: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2978: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "落地窗外庭院绿树树叶与室内红色休闲单人沙发椅色泽略显暗淡泛冷（轻度偏色 D-L1，轻度欠饱和 E2-L1）。"
    },
    2980: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "条纹桌布与蛋糕装饰物大面积泛发刺眼不自然的荧光紫红偏色，烛光反光与桌布紫红色过于浓艳（偏色 D-L2，过饱和 E1-L2，视觉自然度受损 F-L2）。"
    },
    2981: {
        "is_pass": False,
        "severities": {"E2": "L1", "D": "L1"},
        "note": "小朋友手持的彩虹拼色雨伞鲜艳红色拼块轻度脱色泛黄，雨伞鲜亮质感略降（轻度欠饱和 E2-L1，轻度偏色 D-L1）。"
    },

    # Sheet 08: [2982, 2991, 2993, 2994, 2995, 2996]
    2982: {
        "is_pass": False,
        "severities": {"E2": "L1", "D": "L1"},
        "note": "越野滑雪赛道上右侧运动员身穿的鲜艳紫红色防寒比赛服与黄色条纹色泽暗淡褪色（轻度欠饱和 E2-L1，轻度偏色 D-L1）。"
    },
    2991: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L1"},
        "note": "水槽后方背景瓷砖与水龙头整体严重偏暖泛黄褐调，香蕉表皮金黄色泽微暗（偏色 D-L2，轻度欠饱和 E2-L1）。"
    },
    2993: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L1"},
        "note": "电脑桌台面白色纸张与手机机身大面积严重偏暖泛黄褐调，暖黄高光略显浓艳（偏色 D-L2，轻度过饱和 E1-L1）。"
    },
    2994: {
        "is_pass": False,
        "severities": {"E1": "L2", "D": "L1", "F": "L1"},
        "note": "Hello Kitty 主题卫生间粉红瓷砖墙面与毛巾过于浓艳刺眼，浴室空间微泛洋红偏色（过饱和 E1-L2，轻度偏色 D-L1，视觉自然度轻度受损 F-L1）。"
    },
    2995: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L1", "F": "L1"},
        "note": "白瓷盘中盛放的新鲜绿西兰花表面大面积泛暗绿与焦枯杂色偏色，蔬菜暗部色彩过于浓黑（偏色 D-L2，轻度过饱和 E1-L1，视觉自然度轻度受损 F-L1）。"
    },
    2996: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 09: [3002, 3005, 3011, 3019, 3023, 3027]
    3002: {
        "is_pass": False,
        "severities": {"D": "L1", "F": "L1"},
        "note": "餐盘中迷你汉堡面包表皮与烤肉表面微泛暗紫红杂色伪色，生菜叶片色彩略暗（轻度偏色 D-L1，视觉自然度轻度受损 F-L1）。"
    },
    3005: {
        "is_pass": False,
        "severities": {"E2": "L1", "D": "L1"},
        "note": "跳跃击球男孩身穿的浅天蓝色短袖T恤大面积脱色发灰，蓝色活力减弱（轻度欠饱和 E2-L1，轻度偏色 D-L1）。"
    },
    3011: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "床上趴卧折耳猫胸腹部白色毛发与被单折痕微泛青蓝冷色偏（轻度偏色 D-L1）。"
    },
    3019: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "木长椅上深绿色啤酒玻璃瓶表面鲜艳的大红色商标贴纸被严重剥色错涂为暗黑灰色（严重常识错色 C-L3，欠饱和 E2-L2）。"
    },
    3023: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    3027: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L1", "F": "L1"},
        "note": "滑板公园右上方金属围栏与背光阴影区域大面积泛发刺眼荧光洋红偏色，背光伪色偏浓（偏色 D-L2，轻度过饱和 E1-L1，视觉自然度轻度受损 F-L1）。"
    },

    # Sheet 10: [3028, 3029, 3030, 3034, 3036, 3044]
    3028: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L1"},
        "note": "酒店洗手间浅黄大理石台面与墙面大面积泛发暗冷青灰偏色，暖光质感脱色（偏色 D-L2，轻度欠饱和 E2-L1）。"
    },
    3029: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L3"},
        "note": "欧式古建筑山墙屋顶边缘原本鲜明的红砖红瓦被严重剥色错涂为惨灰白石雕，红砖红色质感彻底剥除丧失（严重常识错色 C-L3，严重欠饱和 E2-L3）。"
    },
    3030: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2", "F": "L3"},
        "note": "黄色餐盘中新鲜翠绿的烤芦笋蔬菜被严重恶性错涂为诡异深蓝紫色，全图微泛蓝紫，整体视觉可信度严重破坏（恶性常识错色 C-L3，偏色 D-L2，视觉自然度严重恶化 F-L3）。"
    },
    3034: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    3036: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    3044: {
        "is_pass": False,
        "severities": {"E2": "L1", "D": "L1"},
        "note": "双层巴士车头下部原本鲜艳的红色防撞保险杠色泽脱色暗淡泛黄，巴士标识红色减弱（轻度欠饱和 E2-L1，轻度偏色 D-L1）。"
    },

    # Sheet 11: [3046, 3050, 3051, 3060, 3066, 3067]
    3046: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "复古电视机机壳周围台面与背景墙壁微泛冷青偏色，电视机屏幕反光微泛杂色（轻度偏色 D-L1）。"
    },
    3050: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "男子身穿的红色条纹短袖衬衫被严重脱色错涂为暗冷灰色，红衣服与飞盘色泽严重褪淡（错色 C-L2，欠饱和 E2-L2）。"
    },
    3051: {
        "is_pass": False,
        "severities": {"D": "L2", "B": "L1", "F": "L1"},
        "note": "卫生间洗手池台面与盆底微泛不自然的冷青紫与墨绿杂色，洗手池边缘微有轻度色差溢出（偏色 D-L2，轻度溢色 B-L1，视觉自然度轻度受损 F-L1）。"
    },
    3060: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2"},
        "note": "非洲旱季干燥金黄草原大面积泛发暗冷灰白色偏色，草原干燥金黄生机色彩严重脱色褪淡（偏色 D-L2，欠饱和 E2-L2）。"
    },
    3066: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2", "E2": "L3"},
        "note": "城市街道上空原本浓郁绚丽的橙红色黄昏晚霞被严重剥色错涂为凄冷灰暗阴云，晚霞暖色光彩彻底丧失（严重常识错色 C-L3，偏色 D-L2，严重欠饱和 E2-L3）。"
    },
    3067: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "厨房实木橱柜背光阴影区域色调微深，整体呈现微弱暖色偏移（轻度偏色 D-L1）。"
    },

    # Sheet 12: [3068, 3072, 3074, 3079, 3082, 3083]
    3068: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2", "E2": "L2"},
        "note": "棒球场外野原本青翠生机的鲜绿草坪被严重错涂为发暗凄凉的冷青灰色，全图严重泛冷青偏色，草地绿色生机彻底丧失（严重常识错色 C-L3，偏色 D-L2，欠饱和 E2-L2）。"
    },
    3072: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L3", "E1": "L2", "F": "L2"},
        "note": "窗外原本自然采光的树木与白昼光线被严重错涂为大片刺眼不自然的荧光紫红色，全图泛发严重洋红偏色（严重常识错色 C-L3，严重偏色 D-L3，过饱和 E1-L2，视觉自然度受损 F-L2）。"
    },
    3074: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    3079: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "夜间展馆深色水池中探头的海豹头部湿润皮毛暗部微泛深灰冷色偏（轻度偏色 D-L1）。"
    },
    3082: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    3083: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 13: [3084, 3089, 3093, 3097, 3098, 3101]
    3084: {
        "is_pass": False,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "展览展示机台操作面板与右侧电脑屏幕外边框微泛荧光紫红伪色，反光轻微过饱和（轻度偏色 D-L1，轻度过饱和 E1-L1，视觉自然度轻度受损 F-L1）。"
    },
    3089: {
        "is_pass": False,
        "severities": {"E1": "L2", "D": "L1"},
        "note": "人行道旁摆放的红色金属配电箱与亮黄色消防栓漆面过于浓艳刺眼（过饱和 E1-L2，轻度偏色 D-L1）。"
    },
    3093: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    3097: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    3098: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2", "F": "L3"},
        "note": "街头行为艺术家身穿的深色西装与雨伞被严重错涂为诡异深墨绿色，整体视觉可信度严重破坏（严重常识错色 C-L3，偏色 D-L2，视觉自然度严重恶化 F-L3）。"
    },
    3101: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 14: [3103, 3106, 3111, 3112, 3113, 3114]
    3103: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "手掌啄食的灰鸽颈部羽毛与手掌皮肤微泛冷青偏色，鸽子爪部微暗（轻度偏色 D-L1）。"
    },
    3106: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    3111: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    3112: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "两只长颈鹿交颈处体表斑纹与背景深绿树林阴影区域微泛暗青偏色（轻度偏色 D-L1）。"
    },
    3113: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L1", "E2": "L1"},
        "note": "男孩身后原本清爽天蓝色的床单靠垫被常识性严重错涂为浑浊焦黄草绿色（严重常识错色 C-L3，轻度偏色 D-L1，轻度欠饱和 E2-L1）。"
    },
    3114: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "大圆盘烘焙披萨表面番茄酱与融化芝士边缘微泛焦暗红杂斑（轻度偏色 D-L1）。"
    },

    # Sheet 15: [3117, 3120, 3122, 3123, 3129, 3131]
    3117: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L1"},
        "note": "客厅室内墙面与天花板大面积严重偏暖泛焦黄褐偏色，室内暖光过浓（偏色 D-L2，轻度过饱和 E1-L1）。"
    },
    3120: {
        "is_pass": False,
        "severities": {"D": "L1", "F": "L1"},
        "note": "笔记本电脑彩色显示屏与键盘台面微泛荧光洋红伪色，反光轻微过饱和（轻度偏色 D-L1，视觉自然度轻度受损 F-L1）。"
    },
    3122: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    3123: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "书桌台面左侧摆放的鲜艳大红色笔筒与彩色文具被严重剥色错涂为暗黑灰色，文具与摆件鲜活色彩严重脱色褪淡（严重常识错色 C-L3，欠饱和 E2-L2）。"
    },
    3129: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    3131: {
        "is_pass": False,
        "severities": {"E1": "L2", "D": "L1"},
        "note": "婚礼现场伴郎们身穿的深蓝西装与粉红领带颜色过度浓艳刺眼，草坪阴影略深（过饱和 E1-L2，轻度偏色 D-L1）。"
    },

    # Sheet 16: [3144, 3148, 3152, 3165, 3172, 3175]
    3144: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    3148: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "牛舍金属围栏与地面草料堆边缘微泛冷青偏色，环境暖意略有削弱（轻度偏色 D-L1）。"
    },
    3152: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "卧室百叶窗透光光照条纹与床上被单边缘微泛冷青暗调（轻度偏色 D-L1）。"
    },
    3165: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "斑马脚下泥土地面表层微泛浅淡粉红偏色，斑马黑白条纹还原逼真（轻度偏色 D-L1）。"
    },
    3172: {
        "is_pass": False,
        "severities": {"E2": "L2", "D": "L1"},
        "note": "牧场草坡原本嫩绿生机的草坪大面积发灰发暗，草色欠饱和，全图微泛冷青偏色（欠饱和 E2-L2，轻度偏色 D-L1）。"
    },
    3175: {
        "is_pass": False,
        "severities": {"C": "L2", "B": "L1", "E2": "L1"},
        "note": "电脑显示屏中的水蓝色风景壁纸被脱色错涂为苍白灰色，屏幕边缘光照溢出色斑侵染小猫耳部毛发（错色 C-L2，轻度溢色 B-L1，轻度欠饱和 E2-L1）。"
    },

    # Sheet 17: [3176, 3177, 3184, 3190, 3203, 3211]
    3176: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L1", "F": "L1"},
        "note": "男子内穿衬衫被严重涂染为刺眼不自然的荧光深粉紫偏色，衬衫伪色偏浓（偏色 D-L2，轻度过饱和 E1-L1，视觉自然度轻度受损 F-L1）。"
    },
    3177: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "涂鸦卷帘门前背双肩包行走的青年服饰与水泥地面微泛冷青偏色（轻度偏色 D-L1）。"
    },
    3184: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L1"},
        "note": "卫生间左侧原本清爽的天蓝色浴帘被严重脱色错涂为灰白色，浴帘色泽褪淡（错色 C-L2，轻度欠饱和 E2-L1）。"
    },
    3190: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L1", "F": "L2"},
        "note": "倒置滑板车支架上原本极度鲜艳的荧光绿色PU轮被严重常识性错涂为亮红色，轮子色彩错配严重（严重常识错色 C-L3，轻度偏色 D-L1，视觉自然度受损 F-L2）。"
    },
    3203: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L1"},
        "note": "盛放蛋糕的餐盘周边桌面与背景大面积泛发浑浊焦暗的红褐色偏色，暖色偏浓（偏色 D-L2，轻度过饱和 E1-L1）。"
    },
    3211: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "烤盘中烤香肠与煎吐司表面微泛暖红焦黄偏色，锡箔纸反光略深（轻度偏色 D-L1）。"
    },

    # Sheet 18: [3213, 3220, 3222, 3227, 3231, 3232]
    3213: {
        "is_pass": False,
        "severities": {"E2": "L1", "D": "L1"},
        "note": "海滨沙滩快艇上骑马人员身穿的红色短袖上衣色泽略显暗淡，快艇内部阴影微泛色偏（轻度欠饱和 E2-L1，轻度偏色 D-L1）。"
    },
    3220: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "草坡席地而坐青年身穿的鲜艳紫红色长袖卫衣被严重剥色错涂为灰白色，卫衣鲜艳色彩严重脱色褪淡（严重常识错色 C-L3，欠饱和 E2-L2）。"
    },
    3222: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L2"},
        "note": "欧式厨房墙面与实木橱柜大面积严重偏暖泛焦黄偏色，厨房暖黄光斑过于浓艳（偏色 D-L2，过饱和 E1-L2）。"
    },
    3227: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2", "F": "L2"},
        "note": "透明玻璃花瓶中原本娇艳盛开的鲜红郁金香花瓣被常识性严重错涂为枯槁黄褐色，宛如枯死花卉，郁金香花瓣鲜红生机彻底丧失（恶性常识错色 C-L3，欠饱和 E2-L2，视觉自然度受损 F-L2）。"
    },
    3231: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    3232: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 19: [3237, 3240, 3242, 3243, 3245, 3246]
    3237: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2", "D": "L1"},
        "note": "网球场原本鲜艳的红土/大红色塑胶地面被常识性严重错涂为灰黄泥土色，球场地面与服饰鲜艳色彩严重脱落（严重常识错色 C-L3，欠饱和 E2-L2，轻度偏色 D-L1）。"
    },
    3240: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    3242: {
        "is_pass": False,
        "severities": {"E2": "L1", "D": "L1"},
        "note": "电脑桌上摆放的小型便携电视机天蓝色塑料外壳脱色褪变为浅灰白色，小电视机外壳天蓝色轻度脱色（轻度欠饱和 E2-L1，轻度偏色 D-L1）。"
    },
    3243: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L1"},
        "note": "复古蒸汽机车车头前端原本醒目的鲜红色防撞横梁被剥色错涂为深黑灰色，机车红色标识脱色（错色 C-L2，轻度欠饱和 E2-L1）。"
    },
    3245: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "欧式复古卧室印花壁纸与大理石壁炉暗部微泛冷青偏色，卧室壁纸暗部微泛青冷调（轻度偏色 D-L1）。"
    },
    3246: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 20: [3251, 3255, 3258, 3267, 3269, 3272]
    3251: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "烤披萨表面番茄红酱边缘微泛暗暗的焦紫杂色偏色，木桌边缘反光微偏冷（轻度偏色 D-L1）。"
    },
    3255: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    3258: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L1"},
        "note": "监控室电脑操作台台面大面积严重偏暖泛焦黄红偏色，红木色调过浓（偏色 D-L2，轻度过饱和 E1-L1）。"
    },
    3267: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2", "F": "L2"},
        "note": "男子自拍身后原本米白色的室内背景墙面被严重错涂为大片鲜艳天蓝色，全图背景泛深冷蓝偏色（严重常识错色 C-L3，偏色 D-L2，视觉自然度受损 F-L2）。"
    },
    3269: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    3272: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    }
}

def main():
    print(f"Total reviews defined: {len(REVIEWS)}")
    assert len(REVIEWS) == 120, f"Expected 120 reviews, got {len(REVIEWS)}"

    # 1. 验证所有 defect descriptions 均符合具象实体定物规则（消灭抽象代词）
    abstract_words = ["局部关键区域", "关键主体或背景", "局部区域", "轮廓边缘处", "关键区域"]
    for tid, rev in REVIEWS.items():
        note = rev["note"]
        for w in abstract_words:
            assert w not in note, f"Task #{tid} contains abstract word '{w}': {note}"

    # 2. 生成中间定物审计文件
    grounding_data = {}
    for tid, rev in REVIEWS.items():
        grounding_data[str(tid)] = {
            "task_id": tid,
            "is_pass": rev["is_pass"],
            "severities": rev["severities"],
            "note": rev["note"]
        }
    with open(OUT_GROUNDING_FILE, "w", encoding="utf-8") as f:
        json.dump(grounding_data, f, ensure_ascii=False, indent=2)
    print(f"Saved grounding audit to {OUT_GROUNDING_FILE}")

    # 3. 同步更新 reviewed_1_10000_all.json
    print(f"Loading {ALL_EXPORT}...")
    with open(ALL_EXPORT, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    all_map = {ann["human_review"]["task_id"]: ann for ann in all_data["annotations"]}
    updated_count = 0

    for tid, rev in REVIEWS.items():
        if tid not in all_map:
            print(f"Warning: Task #{tid} not found in {ALL_EXPORT}")
            continue
        ann = all_map[tid]
        is_pass = rev["is_pass"]
        sevs = rev["severities"]
        note = rev["note"]

        if is_pass:
            ann["defects"] = []
            ann["review_note"] = "审查通过"
            ann["reviewed_score"] = None
            ann["needs_rescoring"] = True
        else:
            def_list = []
            for did, sev in sevs.items():
                def_list.append({
                    "id": did,
                    "name": DEFECT_NAMES[did],
                    "severity": sev,
                    "description": note
                })
            ann["defects"] = def_list
            ann["review_note"] = note
            if "A" in sevs:
                ann["reviewed_score"] = 1.0
                ann["needs_rescoring"] = False
            else:
                ann["reviewed_score"] = None
                ann["needs_rescoring"] = True

        ann["review_status"] = "已核验"
        updated_count += 1

    with open(ALL_EXPORT, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {updated_count} items in {ALL_EXPORT}")

    # 4. 同步更新 reviewed_1_10000_clean.json
    print(f"Loading {CLEAN_EXPORT}...")
    with open(CLEAN_EXPORT, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    clean_map = {ann["human_review"]["task_id"]: ann for ann in clean_data["annotations"]}

    for tid, rev in REVIEWS.items():
        if tid not in clean_map:
            continue
        ann = clean_map[tid]
        is_pass = rev["is_pass"]
        sevs = rev["severities"]
        note = rev["note"]

        if is_pass:
            ann["defects"] = []
            ann["review_note"] = ""
            ann["reviewed_score"] = None
            ann["needs_rescoring"] = True
        else:
            def_list = []
            for did, sev in sevs.items():
                def_list.append({
                    "id": did,
                    "name": DEFECT_NAMES[did],
                    "severity": sev,
                    "description": note
                })
            ann["defects"] = def_list
            ann["review_note"] = ""
            if "A" in sevs:
                ann["reviewed_score"] = 1.0
                ann["needs_rescoring"] = False
            else:
                ann["reviewed_score"] = None
                ann["needs_rescoring"] = True

        ann["review_status"] = "已核验"

    with open(CLEAN_EXPORT, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {updated_count} items in {CLEAN_EXPORT}")

if __name__ == "__main__":
    main()
