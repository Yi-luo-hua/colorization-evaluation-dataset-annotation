# -*- coding: utf-8 -*-
"""
Apply visual grounding reviews for Remaining Batch 19 (Tasks #4155 ~ #4339, total 120 tasks across 20 sheets).
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
GROUNDING_OUT_PATH = os.path.join(PROJECT_ROOT, "LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_19.json")

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

# 120 Reviews for Batch 19
BATCH_19_REVIEWS = {
    # Sheet 01
    4155: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "聚会餐桌前左侧男子身穿的蓝紫扎染花衬衫被错涂为暗淡灰黑色。"},
            {"id": "E2", "severity": "L2", "description": "男子佩戴的彩色花环与扎染衬衫色彩严重欠饱和发暗脱色。"},
            {"id": "D", "severity": "L1", "description": "酒瓶与木质餐桌略偏暗暖灰调。"}
        ],
        "note": "左侧男子蓝紫扎染衬衫错涂为暗淡灰黑(错色 C-L2)，彩色花环与衬衫严重欠饱和脱色(欠饱和 E2-L2)，餐桌略偏暗暖灰(偏色 D-L1)。"
    },
    4156: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4159: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "公园长椅上幼儿所穿的鲜艳黄绿色毛衣被彻底剥夺错涂为冷灰白色。"},
            {"id": "D", "severity": "L2", "description": "木质靠背长椅与地面严重偏冷青暗灰调。"},
            {"id": "E2", "severity": "L2", "description": "幼儿毛衣原本鲜活的荧光黄绿色彩完全丧失严重欠饱和。"}
        ],
        "note": "幼儿黄绿毛衣彻底错涂为冷灰白(错色 C-L3)，木长椅偏冷青暗灰(偏色 D-L2)，毛衣活力完全丧失(欠饱和 E2-L2)。"
    },
    4161: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "沿街建筑红砖外墙与湿滑地面反光严重偏冷蓝紫杂色调。"},
            {"id": "C", "severity": "L2", "description": "墙面菱形警示标牌由红色错涂为发暗紫黑色。"},
            {"id": "E1", "severity": "L1", "description": "临街暖黄窗户光线局部过浓发闷。"}
        ],
        "note": "建筑红砖外墙与地面偏冷蓝紫(偏色 D-L2)，菱形警示标牌错涂为发暗紫黑(错色 C-L2)，窗户暖光局部过浓(过饱和 E1-L1)。"
    },
    4163: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "客厅原本明亮温暖的黄色壁纸墙面被彻底剥夺错涂为冰冷水泥灰白色。"},
            {"id": "D", "severity": "L2", "description": "布艺沙发与地毯严重偏冷青暗灰调。"},
            {"id": "E2", "severity": "L2", "description": "室内壁灯与墙面温润暖光完全丧失严重欠饱和。"}
        ],
        "note": "客厅黄色壁纸墙面彻底错涂为冰冷水泥灰白(错色 C-L3)，沙发与地毯偏冷青暗灰(偏色 D-L2)，壁灯暖光完全丧失(欠饱和 E2-L2)。"
    },
    4169: {
        "pass": False,
        "defects": [
            {"id": "B", "severity": "L1", "description": "水泥立柱悬挂的美国国旗红白条纹边缘向浅灰色混凝土柱身发生轻微红色溢色晕染。"}
        ],
        "note": "美国国旗红白条纹边缘向水泥柱身溢色晕染(溢色 B-L1)。"
    },

    # Sheet 02
    4170: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "床头暖橘红色台灯灯罩与投射暖光被错涂为冰冷白光。"},
            {"id": "D", "severity": "L2", "description": "卧室床铺深色床单与右侧墙面严重偏冷暗青灰调。"},
            {"id": "E2", "severity": "L1", "description": "床头灯暖光氛围欠饱和严重丧失。"}
        ],
        "note": "床头暖橘红台灯与投射暖光错涂为冷白光(错色 C-L2)，床铺与右侧墙面偏冷暗青灰(偏色 D-L2)，暖光氛围欠饱和(欠饱和 E2-L1)。"
    },
    4171: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "玻璃花瓶中盛开的红色花朵花瓣色彩过度浓艳刺眼呈荧光洋红。"},
            {"id": "F", "severity": "L1", "description": "花朵高光边缘过浓略显油腻失真。"}
        ],
        "note": "红色花朵花瓣过度浓艳刺眼呈荧光洋红(过饱和 E1-L2)，花朵边缘略失真(自然度 F-L1)。"
    },
    4172: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "地下停车场背景暖黄顶棚灯光与停放车辆严重偏冷暗蓝紫调。"},
            {"id": "E1", "severity": "L1", "description": "缴费机操作面板高光反光略显浓艳生硬。"},
            {"id": "F", "severity": "L1", "description": "停车场原本温馨的暖黄照明变为冷冽蓝光，破坏视觉自然度。"}
        ],
        "note": "地下停车场暖黄照明偏冷暗蓝紫(偏色 D-L2)，缴费机反光略浓艳(过饱和 E1-L1)，环境变冷破坏自然度(自然度 F-L1)。"
    },
    4175: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "餐厅原本温暖明亮的米黄色背景墙面被彻底剥夺错涂为冰冷浅灰白色。"},
            {"id": "C", "severity": "L2", "description": "婴儿餐椅靠背与边缘被错涂为冷青湖蓝色。"},
            {"id": "D", "severity": "L2", "description": "婴儿面部与餐桌托盘全景严重偏冷青暗灰调。"},
            {"id": "E2", "severity": "L1", "description": "墙面与餐椅暖色严重欠饱和丧失。"}
        ],
        "note": "米黄色背景墙彻底错涂为冰冷浅灰白(错色 C-L3)，婴儿餐椅错涂为冷青湖蓝(错色 C-L2)，婴儿面部偏冷青暗灰(偏色 D-L2)，暖色欠饱和丧失(欠饱和 E2-L1)。"
    },
    4178: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "餐盘左上方原本金黄色的烘焙面包/暖黄餐巾被彻底错涂为发暗青蓝紫色。"},
            {"id": "D", "severity": "L2", "description": "盛放炒蛋西兰花的白瓷餐盘与桌面严重偏冷暗蓝紫调。"},
            {"id": "E2", "severity": "L1", "description": "面包与餐具暖色调严重欠饱和。"}
        ],
        "note": "左上方金黄面包/餐巾错涂为发暗青蓝紫(错色 C-L3)，白瓷餐盘偏冷暗蓝紫(偏色 D-L2)，暖色严重欠饱和(欠饱和 E2-L1)。"
    },
    4179: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 03
    4180: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "街边米黄色石砌房屋外墙被错涂为冰冷浅灰白色。"},
            {"id": "D", "severity": "L1", "description": "柏油路面与白色围墙立柱略偏冷暗青灰调。"},
            {"id": "E2", "severity": "L1", "description": "建筑外墙石材温暖质感欠饱和发灰。"}
        ],
        "note": "街边米黄石砌房屋外墙错涂为冰冷浅灰白(错色 C-L2)，路面与围墙立柱略偏冷暗青灰(偏色 D-L1)，石材暖色欠饱和(欠饱和 E2-L1)。"
    },
    4182: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4183: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "户外训练场翠绿草坪被错涂为枯黄橄榄黄绿色。"},
            {"id": "D", "severity": "L1", "description": "女士所穿粉色T恤与柏油路面略偏暗黄褐调。"},
            {"id": "E2", "severity": "L1", "description": "草坪草色与服饰色彩欠饱和发暗。"}
        ],
        "note": "户外翠绿草坪错涂为枯黄橄榄黄绿(错色 C-L2)，女士粉色T恤略偏暗黄褐(偏色 D-L1)，草坪欠饱和发暗(欠饱和 E2-L1)。"
    },
    4184: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4186: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "男士面部肤色与百叶窗略偏暗红褐调。"},
            {"id": "E2", "severity": "L1", "description": "餐盘中食物色彩与果汁欠饱和微弱发暗。"}
        ],
        "note": "男士面部肤色与百叶窗略偏暗红褐(偏色 D-L1)，食物与果汁欠饱和微暗(欠饱和 E2-L1)。"
    },
    4189: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "客厅原本温暖柔和的米黄色粉刷墙面被彻底剥夺错涂为冰冷浅灰白色。"},
            {"id": "D", "severity": "L2", "description": "鸟笼铁丝框架与木质镜框严重偏冷青暗灰调。"},
            {"id": "E2", "severity": "L1", "description": "室内温馨暖光调严重欠饱和丧失。"}
        ],
        "note": "客厅米黄色粉刷墙面彻底错涂为冰冷浅灰白(错色 C-L3)，鸟笼与镜框偏冷青暗灰(偏色 D-L2)，室内暖光严重欠饱和(欠饱和 E2-L1)。"
    },

    # Sheet 04
    4193: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "越野摩托车荧光亮绿色的前挡泥板与赛车服荧光饰条被错涂为发暗灰橄榄色。"},
            {"id": "E2", "severity": "L1", "description": "越野摩托车赛车涂装与赞助商标识鲜艳色彩欠饱和暗淡。"},
            {"id": "D", "severity": "L1", "description": "赛道泥土地面与围栏略偏暗灰调。"}
        ],
        "note": "越野摩托车荧光绿挡泥板与赛车服饰条错涂为发暗灰橄榄色(错色 C-L2)，赛车涂装色彩欠饱和(欠饱和 E2-L1)，泥土地面略偏暗灰(偏色 D-L1)。"
    },
    4194: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4195: {
        "pass": False,
        "defects": [
            {"id": "B", "severity": "L1", "description": "天空中漂浮的风筝边缘向云层天空发生轻微溢色晕染。"},
            {"id": "E2", "severity": "L1", "description": "草坪上放风筝人群服饰色彩欠饱和微弱发暗。"}
        ],
        "note": "天空风筝边缘向云层溢色晕染(溢色 B-L1)，人群服饰色彩欠饱和发暗(欠饱和 E2-L1)。"
    },
    4197: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "三明治中夹心烤牛肉切片由红褐色被错涂为发暗冷灰褐色。"},
            {"id": "D", "severity": "L1", "description": "百事可乐罐与餐盘边缘微偏冷暗青灰调。"},
            {"id": "E2", "severity": "L1", "description": "三明治面包金黄焦香烘烤感欠饱和暗淡。"}
        ],
        "note": "三明治烤牛肉切片错涂为发暗冷灰褐(错色 C-L2)，百事可乐罐微偏冷暗青灰(偏色 D-L1)，面包烘烤感欠饱和(欠饱和 E2-L1)。"
    },
    4199: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "走廊通道原本暖黄绿色的粉刷墙面被彻底剥夺错涂为冷暗灰白色。"},
            {"id": "D", "severity": "L2", "description": "镜面中倒映的瓷砖地面与镜框严重偏冷青暗灰调。"},
            {"id": "E2", "severity": "L2", "description": "墙面原有黄绿色调完全丧失严重欠饱和。"}
        ],
        "note": "走廊暖黄绿色粉刷墙面错涂为冷暗灰白(错色 C-L3)，镜中地面偏冷青暗灰(偏色 D-L2)，墙面色彩严重欠饱和(欠饱和 E2-L2)。"
    },
    4201: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "企鹅雕像胸腹部鲜艳明黄羽毛斑块被错涂为发暗橄榄黄褐色。"},
            {"id": "D", "severity": "L2", "description": "厨房绿色橱柜与白色冰箱严重偏暗冷绿青调。"},
            {"id": "E2", "severity": "L1", "description": "企鹅羽毛明黄色彩欠饱和暗淡。"}
        ],
        "note": "企鹅雕像胸前明黄斑块错涂为发暗橄榄黄褐(错色 C-L2)，厨房橱柜偏暗冷绿青(偏色 D-L2)，羽毛黄色欠饱和暗淡(欠饱和 E2-L1)。"
    },

    # Sheet 05
    4202: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "卧室粉刷墙壁与床头背景严重偏暗暖橙黄调。"},
            {"id": "E1", "severity": "L1", "description": "红白条纹床尾毛毯红色线条局部略显浓艳发闷。"},
            {"id": "F", "severity": "L1", "description": "窗帘红花纹理与窗框采光反差略显生硬。"}
        ],
        "note": "卧室墙壁偏暗暖橙黄(偏色 D-L2)，条纹毛毯局部过浓发闷(过饱和 E1-L1)，窗帘反差略显生硬(自然度 F-L1)。"
    },
    4203: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "前排自行车车轮上装配的亮绿色荧光灯条错涂为暗沉黄光。"},
            {"id": "D", "severity": "L1", "description": "聚会人群衣着与夜景街面略偏暗暖红调。"},
            {"id": "E2", "severity": "L1", "description": "自行车彩色LED灯轮活力欠饱和微弱发暗。"}
        ],
        "note": "自行车车轮亮绿荧光灯条错涂为暗沉黄光(错色 C-L2)，人群衣着略偏暗暖红(偏色 D-L1)，LED灯轮欠饱和(欠饱和 E2-L1)。"
    },
    4204: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4205: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "滑板公园背景原本郁郁葱葱的翠绿草坪被大面积错涂为发暗枯灰浅草色。"},
            {"id": "D", "severity": "L2", "description": "沥青路面与滑板滑手衣裤严重偏冷青暗灰调。"},
            {"id": "E2", "severity": "L2", "description": "公园草坪翠绿生机彻底丧失严重欠饱和。"}
        ],
        "note": "滑板公园翠绿草坪大面积错涂为发暗枯灰草色(错色 C-L3)，路面与衣裤偏冷青暗灰(偏色 D-L2)，草坪严重欠饱和(欠饱和 E2-L2)。"
    },
    4207: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "白瓷餐盘中焦香多汁的烤肉排红褐色酱汁被错涂为暗沉发黄的浅肉褐色。"},
            {"id": "D", "severity": "L1", "description": "餐盘底部与鲜脆生菜略偏暗冷青调。"},
            {"id": "E2", "severity": "L1", "description": "玉米棒与烤肉排整体色泽欠饱和暗淡。"}
        ],
        "note": "白瓷餐盘烤肉排酱汁错涂为暗沉发黄浅肉褐色(错色 C-L2)，生菜略偏暗冷青(偏色 D-L1)，玉米与肉排欠饱和(欠饱和 E2-L1)。"
    },
    4210: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "马厩门口探头张望的骏马原本温暖金黄栗色的被毛被严重错涂为冰冷浅灰白色。"},
            {"id": "D", "severity": "L2", "description": "马厩木门框与室内木质围栏严重偏冷青暗灰调。"},
            {"id": "E2", "severity": "L2", "description": "骏马原本温润丰满的栗色毛发严重欠饱和脱色。"}
        ],
        "note": "马厩骏马金黄栗色毛被错涂为冰冷浅灰白(错色 C-L3)，马厩门框偏冷青暗灰(偏色 D-L2)，毛发严重欠饱和脱色(欠饱和 E2-L2)。"
    },

    # Sheet 06
    4211: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "棒球场内野跑道原本鲜明的红棕色黏土泥面被错涂为发暗黄褐色。"},
            {"id": "E2", "severity": "L1", "description": "棒球场草坪与红土色彩欠饱和微弱发暗。"},
            {"id": "D", "severity": "L1", "description": "隔离防护铁丝网与天空微偏暗灰调。"}
        ],
        "note": "棒球场红棕色红土泥面错涂为发暗黄褐(错色 C-L2)，草坪与红土欠饱和(欠饱和 E2-L1)，防护网微偏暗灰(偏色 D-L1)。"
    },
    4212: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "室内交谈男女二人面部肤色偏冷暗紫褐调。"},
            {"id": "E2", "severity": "L1", "description": "人物面部健康血色欠饱和略显发灰。"},
            {"id": "F", "severity": "L1", "description": "面部肤色发暗导致肖像视觉自然度下降。"}
        ],
        "note": "男女二人面部肤色偏冷暗紫褐(偏色 D-L2)，面部血色欠饱和发灰(欠饱和 E2-L1)，肖像自然度下降(自然度 F-L1)。"
    },
    4215: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "飞盘赛场中央选手所穿的鲜红运动球衣被严重错涂为发暗深褐红色。"},
            {"id": "C", "severity": "L2", "description": "飞盘赛场翠绿草坪被大面积错涂为枯黄橄榄黄绿色。"},
            {"id": "D", "severity": "L2", "description": "全景背景树林与观赛人群严重偏冷青暗灰调。"},
            {"id": "E2", "severity": "L2", "description": "红色球衣与绿茵草坪色彩活力严重欠饱和褪色。"}
        ],
        "note": "飞盘选手鲜红球衣错涂为发暗深褐红(错色 C-L3)，草坪错涂为枯黄橄榄黄绿(错色 C-L2)，背景偏冷青暗灰(偏色 D-L2)，球衣与草坪严重欠饱和(欠饱和 E2-L2)。"
    },
    4216: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4217: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "街巷右侧历史建筑醒目的珊瑚橘红与明黄色粉刷立面被错涂为发暗砖红灰黄色。"},
            {"id": "D", "severity": "L1", "description": "沥青路面与停放自行车微偏冷暗青灰调。"},
            {"id": "E2", "severity": "L1", "description": "沿街建筑外墙鲜艳暖色调欠饱和微弱发暗。"}
        ],
        "note": "街巷右侧珊瑚橘红立面错涂为发暗砖红灰黄(错色 C-L2)，路面微偏冷暗青灰(偏色 D-L1)，外墙暖色欠饱和发暗(欠饱和 E2-L1)。"
    },
    4218: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "幼童面部肤色与头发严重偏冷暗青灰杂色调。"},
            {"id": "E2", "severity": "L1", "description": "幼童面部原本红润健康的血色欠饱和暗淡。"},
            {"id": "F", "severity": "L1", "description": "室内温馨暖光转为阴冷，幼童面部光影略显发僵。"}
        ],
        "note": "幼童面部肤色与头发偏冷暗青灰(偏色 D-L2)，面部红润血色欠饱和(欠饱和 E2-L1)，光影发僵破坏自然度(自然度 F-L1)。"
    },

    # Sheet 07
    4219: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "宴会餐桌原本鲜艳生动的翠绿色桌布被错涂为发暗橄榄灰褐色。"},
            {"id": "D", "severity": "L2", "description": "就餐长者服饰与宴会厅米黄墙面严重偏冷暗青灰调。"},
            {"id": "E2", "severity": "L1", "description": "桌布与长者彩色开衫毛衣色彩欠饱和发暗。"}
        ],
        "note": "宴会餐桌翠绿桌布错涂为发暗橄榄灰褐(错色 C-L2)，长者服饰与墙面偏冷暗青灰(偏色 D-L2)，彩色毛衣欠饱和发暗(欠饱和 E2-L1)。"
    },
    4221: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4222: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4223: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "白瓷沙拉碗中新鲜翠绿生菜与红番茄被错涂为发暗橄榄青褐色。"},
            {"id": "D", "severity": "L1", "description": "餐盘切片全麦面包与啤酒杯略偏暗冷灰调。"},
            {"id": "E2", "severity": "L2", "description": "沙拉新鲜蔬菜食材生机感严重欠饱和褪色。"}
        ],
        "note": "沙拉碗新鲜生菜与红番茄错涂为发暗橄榄青褐(错色 C-L2)，面包与啤酒略偏暗冷灰(偏色 D-L1)，蔬菜生机感严重欠饱和(欠饱和 E2-L2)。"
    },
    4224: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4226: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "牧场站立骏马原本温润红亮的栗色皮毛被错涂为发暗紫黑色。"},
            {"id": "D", "severity": "L1", "description": "牧场绿茵草坪与远景树林微偏暗冷青调。"},
            {"id": "E2", "severity": "L1", "description": "骏马栗色皮毛温润光泽欠饱和发暗。"}
        ],
        "note": "站立骏马红亮栗色皮毛错涂为发暗紫黑色(错色 C-L2)，草坪树林微偏暗冷青(偏色 D-L1)，皮毛光泽欠饱和发暗(欠饱和 E2-L1)。"
    },

    # Sheet 08
    4227: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4228: {
        "pass": False,
        "defects": [
            {"id": "B", "severity": "L1", "description": "沙发上摆放的彩色抱枕与玩具塑料边缘向浅灰布艺沙发表面发生轻微溢色晕染。"},
            {"id": "D", "severity": "L1", "description": "客厅粉刷墙面与电视机柜略偏暗冷青灰调。"},
            {"id": "E2", "severity": "L1", "description": "彩色抱枕与装饰小物件色彩欠饱和发暗。"}
        ],
        "note": "彩色抱枕边缘向浅灰布艺沙发溢色(溢色 B-L1)，墙面与电视机柜偏冷青暗灰(偏色 D-L1)，抱枕色彩欠饱和(欠饱和 E2-L1)。"
    },
    4229: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "传统木骨架建筑外墙与窗框严重偏暗红褐杂色调。"},
            {"id": "E1", "severity": "L1", "description": "店铺橱窗内部暖色照明局部略显浓艳过火。"},
            {"id": "F", "severity": "L1", "description": "建筑外墙暗红偏色使古建木质自然质感明显受损。"}
        ],
        "note": "木骨架建筑外墙偏暗红褐杂色(偏色 D-L2)，橱窗暖光局部过浓(过饱和 E1-L1)，古建筑自然质感下降(自然度 F-L1)。"
    },
    4230: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "瑞士军刀标志性红色手柄塑料外壳色彩过度浓艳刺眼呈荧光鲜红。"},
            {"id": "D", "severity": "L1", "description": "衬托军刀的陈旧木质桌面略偏暗红褐调。"},
            {"id": "F", "severity": "L1", "description": "军刀外壳塑料过度浓艳失真略显塑料感过强。"}
        ],
        "note": "瑞士军刀红色外壳过度浓艳呈荧光鲜红(过饱和 E1-L2)，木质桌面略偏暗红褐(偏色 D-L1)，外壳过度浓艳失真(自然度 F-L1)。"
    },
    4231: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "篮球运动员身穿的白色球衣领口与袖口绿色边条被错涂为发暗青灰黑色。"},
            {"id": "D", "severity": "L2", "description": "运动员面部与手臂肤色严重偏冷紫褐发暗。"},
            {"id": "E2", "severity": "L1", "description": "篮球皮革原本红棕色泽欠饱和微弱发暗。"}
        ],
        "note": "运动员球衣绿色饰边错涂为发暗青灰黑(错色 C-L2)，面部肤色偏冷紫褐发暗(偏色 D-L2)，篮球皮革欠饱和(欠饱和 E2-L1)。"
    },
    4232: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "庭院劳作左侧人员身穿的黄绿相间条纹上衣错涂为发暗浅灰蓝色。"},
            {"id": "C", "severity": "L2", "description": "右侧人员明亮粉红色长袖上衣错涂为暗淡浅灰紫色。"},
            {"id": "D", "severity": "L1", "description": "庭院草坪与大树树冠略偏冷暗青绿调。"},
            {"id": "E2", "severity": "L1", "description": "人员衣着与绿化草坪色彩欠饱和暗淡。"}
        ],
        "note": "左侧人员黄绿条纹上衣错涂为发暗浅灰蓝(错色 C-L2)，右侧人员粉红上衣错涂为暗淡浅灰紫(错色 C-L2)，庭院草坪略偏冷暗青绿(偏色 D-L1)，衣着与草坪欠饱和(欠饱和 E2-L1)。"
    },

    # Sheet 09
    4234: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "笔记本电脑显示屏与桌面饮料杯严重偏冷青蓝调。"},
            {"id": "E2", "severity": "L1", "description": "玻璃杯中柠檬片色彩欠饱和微弱发暗。"}
        ],
        "note": "笔记本显示屏与饮料杯偏冷青蓝(偏色 D-L1)，柠檬切片色彩欠饱和(欠饱和 E2-L1)。"
    },
    4235: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "工作室白色展示桌与粉刷墙面略偏暗暖黄调。"},
            {"id": "E2", "severity": "L1", "description": "人物面部肤色欠饱和微弱发暗。"}
        ],
        "note": "白色展示桌与墙面略偏暗暖黄(偏色 D-L1)，人物面部肤色欠饱和(欠饱和 E2-L1)。"
    },
    4236: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "海滩风筝冲浪翼深绿色布面错涂为冷青墨绿色。"},
            {"id": "E1", "severity": "L2", "description": "冲浪翼大红色条纹帆面过度浓艳刺眼呈荧光洋红。"},
            {"id": "D", "severity": "L1", "description": "海滩沙地与海水边缘略偏冷暗青灰调。"}
        ],
        "note": "冲浪翼深绿布面错涂为冷青墨绿(错色 C-L2)，大红帆面过度浓艳呈荧光洋红(过饱和 E1-L2)，海滩沙地略偏冷暗青灰(偏色 D-L1)。"
    },
    4238: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "公共巴士车头标语中鲜艳的红色爱心图案被错涂为发暗灰褐色。"},
            {"id": "C", "severity": "L2", "description": "巴士车身侧面深宝蓝色涂装条纹错涂为发暗灰紫蓝色。"},
            {"id": "D", "severity": "L1", "description": "车站水泥路面与人行道微偏冷暗紫灰调。"},
            {"id": "E2", "severity": "L1", "description": "巴士车体涂装与警示标识色彩欠饱和暗淡。"}
        ],
        "note": "巴士红色爱心错涂为发暗灰褐(错色 C-L2)，深宝蓝涂装错涂为灰紫蓝(错色 C-L2)，车站路面微偏冷暗紫灰(偏色 D-L1)，车体色彩欠饱和(欠饱和 E2-L1)。"
    },
    4239: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "公共卫生间圆弧形墙面原本温暖明亮的米黄色马赛克瓷砖被彻底剥夺错涂为冰冷浅灰白色。"},
            {"id": "D", "severity": "L2", "description": "马桶陶瓷本体与瓷砖地面严重偏冷暗青蓝调。"},
            {"id": "E2", "severity": "L2", "description": "卫生间原有的温暖米黄暖光氛围完全丧失严重欠饱和。"},
            {"id": "F", "severity": "L2", "description": "室内光环境由暖转冷，瓷砖墙面色彩严重失真破坏视觉自然度。"}
        ],
        "note": "米黄色马赛克瓷砖墙面彻底错涂为冰冷浅灰白(错色 C-L3)，马桶与地面严重偏冷暗青蓝(偏色 D-L2)，暖色调严重欠饱和完全丧失(欠饱和 E2-L2)，破坏自然度(自然度 F-L2)。"
    },
    4240: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 10
    4241: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4242: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4243: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4244: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4245: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "网球场原本明亮鲜艳的翠绿色塑胶地面被错涂为发暗青灰水泥色。"},
            {"id": "D", "severity": "L1", "description": "远景绿化树木与铁丝护网略偏冷暗青调。"},
            {"id": "E2", "severity": "L1", "description": "运动员粉红护腕与网球拍把手色彩欠饱和发暗。"}
        ],
        "note": "网球场翠绿塑胶地面错涂为发暗青灰水泥色(错色 C-L2)，远景树木略偏冷暗青(偏色 D-L1)，护腕与球拍欠饱和(欠饱和 E2-L1)。"
    },
    4247: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "巧克力布朗尼表面撒缀的红浆果果碎与坚果颗粒色泽过度浓艳呈荧光粉紫。"},
            {"id": "D", "severity": "L1", "description": "瓷质茶杯与餐盘白瓷表面微偏暗冷青灰调。"},
            {"id": "F", "severity": "L1", "description": "甜点表面果碎荧光过艳略显失真。"}
        ],
        "note": "布朗尼红浆果果碎过度浓艳呈荧光粉紫(过饱和 E1-L2)，茶杯与餐盘微偏暗冷青灰(偏色 D-L1)，果碎过艳略显失真(自然度 F-L1)。"
    },

    # Sheet 11
    4248: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "背景树林郁郁葱葱的翠绿树冠被错涂为发暗橄榄黄褐色。"},
            {"id": "D", "severity": "L2", "description": "大象庞大身躯皮褶严重偏冷紫褐发暗。"},
            {"id": "E2", "severity": "L1", "description": "背景树木绿意生机欠饱和暗淡。"}
        ],
        "note": "背景翠绿树冠错涂为发暗橄榄黄褐(错色 C-L2)，大象身躯皮褶偏冷紫褐发暗(偏色 D-L2)，树木绿意欠饱和(欠饱和 E2-L1)。"
    },
    4249: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "地铁车厢内部明亮温暖的黄色金属内饰壁面被彻底剥夺错涂为冰冷浅灰白色。"},
            {"id": "C", "severity": "L2", "description": "乘客连排座椅鲜艳明快的亮橙色坐垫被错涂为暗淡焦褐橙色。"},
            {"id": "D", "severity": "L2", "description": "不锈钢扶手立柱与车门严重偏冷暗青灰调。"},
            {"id": "E2", "severity": "L2", "description": "车厢内饰温暖黄色与橙色严重欠饱和脱色。"}
        ],
        "note": "地铁车厢黄色金属内壁彻底错涂为冰冷浅灰白(错色 C-L3)，亮橙色坐垫错涂为暗淡焦褐橙(错色 C-L2)，扶手立柱偏冷暗青灰(偏色 D-L2)，内饰严重欠饱和(欠饱和 E2-L2)。"
    },
    4250: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4251: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "动物园长颈鹿展区背景茂密翠绿树林被错涂为发暗灰橄榄色。"},
            {"id": "D", "severity": "L1", "description": "长颈鹿沙土地面略偏冷暗青灰调。"},
            {"id": "E2", "severity": "L2", "description": "树林绿色植被色彩严重欠饱和发暗。"}
        ],
        "note": "展区翠绿树林错涂为发暗灰橄榄色(错色 C-L2)，沙土地面略偏冷暗青灰(偏色 D-L1)，树林植被严重欠饱和(欠饱和 E2-L2)。"
    },
    4252: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "辽阔牧场郁郁葱葱的深翠绿色天然草场被大面积荒唐错涂为枯黄泥草色。"},
            {"id": "D", "severity": "L2", "description": "天空阴云与远景山丘严重偏暗冷灰调。"},
            {"id": "E2", "severity": "L2", "description": "绿茵草地生机感完全剥落严重欠饱和。"}
        ],
        "note": "辽阔牧场深翠绿草场大面积错涂为枯黄泥草色(错色 C-L3)，天空与山丘偏暗冷灰(偏色 D-L2)，草地生机感严重欠饱和(欠饱和 E2-L2)。"
    },
    4253: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "观兽台右侧游客身穿的鲜艳宝蓝色冲锋衣外套被彻底错涂为发暗灰黑色。"},
            {"id": "D", "severity": "L1", "description": "黑熊身后石壁与绿植略偏暗草绿黄调。"},
            {"id": "E2", "severity": "L1", "description": "游客服饰色彩欠饱和脱色。"}
        ],
        "note": "右侧游客宝蓝色冲锋衣彻底错涂为发暗灰黑色(错色 C-L3)，石壁与绿植略偏暗草绿黄(偏色 D-L1)，服饰色彩欠饱和(欠饱和 E2-L1)。"
    },

    # Sheet 12
    4254: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4255: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4257: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "趴卧黑白小狗身上佩戴的鲜艳亮紫色背带牵引绳被错涂为发暗粉灰白色。"},
            {"id": "C", "severity": "L2", "description": "泥地上放置的亮黄色飞盘被错涂为暗淡黄褐色。"},
            {"id": "D", "severity": "L1", "description": "碎石泥土路面与绿草略偏冷暗青灰调。"},
            {"id": "E2", "severity": "L1", "description": "宠物用品鲜艳色彩欠饱和暗淡。"}
        ],
        "note": "趴卧小狗亮紫色牵引绳错涂为发暗粉灰白(错色 C-L2)，黄色飞盘错涂为暗淡黄褐(错色 C-L2)，泥土路面略偏冷暗青灰(偏色 D-L1)，宠物用品欠饱和(欠饱和 E2-L1)。"
    },
    4260: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4262: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "航空博物馆中悬吊战机原本标志性的天蓝色/海灰色机身被彻底错涂为暗沉泥黄褐色。"},
            {"id": "D", "severity": "L2", "description": "战机金属螺旋桨与机库背景严重偏暗黄褐调。"},
            {"id": "E2", "severity": "L1", "description": "历史战机涂装色彩欠饱和失色。"}
        ],
        "note": "悬吊战机天蓝海灰色机身彻底错涂为暗沉泥黄褐色(错色 C-L3)，螺旋桨与机库偏暗黄褐(偏色 D-L2)，战机涂装色彩欠饱和(欠饱和 E2-L1)。"
    },
    4265: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "湖畔木栈道右侧休闲木椅原本古朴的砖红色被错涂为俗艳刺眼的荧光亮粉红色。"},
            {"id": "E1", "severity": "L2", "description": "左侧木椅草绿色涂装过度浓艳呈荧光翠绿。"},
            {"id": "F", "severity": "L2", "description": "两把木椅荧光色泽过度刺眼严重破坏湖畔宁静自然度。"}
        ],
        "note": "右侧木椅错涂为俗艳荧光亮粉红(错色 C-L2)，左侧木椅过度浓艳呈荧光翠绿(过饱和 E1-L2)，双椅荧光刺眼破坏自然度(自然度 F-L2)。"
    },

    # Sheet 13
    4268: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "棒球打击区红土与捕手护具严重偏冷暗紫褐调。"},
            {"id": "E1", "severity": "L1", "description": "击球手头盔反光局部略显浓艳生硬。"},
            {"id": "F", "severity": "L1", "description": "棒球场红土与草坪交界色泽过渡略显不自然。"}
        ],
        "note": "棒球打击区红土与捕手护具偏冷暗紫褐(偏色 D-L2)，头盔反光略浓艳(过饱和 E1-L1)，草坪交界略不自然(自然度 F-L1)。"
    },
    4269: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "阳台趴卧金毛寻回犬金黄毛色过度浓艳刺眼偏火红橙色。"},
            {"id": "D", "severity": "L2", "description": "阳台白色矮墙与远景海湾严重偏冷暗青灰调。"},
            {"id": "F", "severity": "L2", "description": "金毛犬被毛过度浓艳泛红产生灼烧失真感。"}
        ],
        "note": "金毛犬金黄被毛过度浓艳偏火红橙色(过饱和 E1-L2)，阳台矮墙与海湾偏冷暗青灰(偏色 D-L2)，被毛泛红灼烧感破坏自然度(自然度 F-L2)。"
    },
    4270: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4271: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "刚出炉比萨饼原本金黄诱人的融化芝士与烘烤面饼被彻底错涂为发暗青灰粉紫色。"},
            {"id": "D", "severity": "L1", "description": "金属比萨烤盘与桌面略偏暗冷青灰调。"},
            {"id": "F", "severity": "L3", "description": "食物表面大面积粉紫暗灰伪色带来强烈变质霉变感，视觉自然度极度恶化。"}
        ],
        "note": "比萨饼金黄芝士与面饼彻底错涂为发暗青灰粉紫(错色 C-L3)，金属托盘略偏暗冷青灰(偏色 D-L1)，严重变质霉变感破坏自然度(自然度 F-L3)。"
    },
    4272: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4273: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "海滩晴空原本明澈蔚蓝的天空与碧蓝海水被大面积错涂为阴沉冷灰白色。"},
            {"id": "D", "severity": "L1", "description": "海滩沙地与冲浪少年肤色略偏暗暖灰褐调。"},
            {"id": "E2", "severity": "L2", "description": "蓝天碧海与少年泳装色彩活力严重欠饱和褪色。"}
        ],
        "note": "晴空蔚蓝天空与碧蓝海水大面积错涂为阴沉冷灰白(错色 C-L3)，沙滩与肤色略偏暗暖灰褐(偏色 D-L1)，蓝天碧海严重欠饱和(欠饱和 E2-L2)。"
    },

    # Sheet 14
    4274: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "卫生间瓷砖墙面与白瓷洗手台盆严重偏冷青暗灰调。"},
            {"id": "E2", "severity": "L2", "description": "瓷砖原本柔和温润的浅粉暖色严重欠饱和褪色。"},
            {"id": "F", "severity": "L2", "description": "室内暖色完全剥落导致卫浴环境冰冷空洞。"}
        ],
        "note": "卫生间瓷砖墙面偏冷青暗灰(偏色 D-L2)，浅粉暖色严重欠饱和褪色(欠饱和 E2-L2)，卫浴环境冰冷空洞破坏自然度(自然度 F-L2)。"
    },
    4275: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4277: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "无障碍卫生间米黄色防滑瓷砖地面与墙面被错涂为发暗青灰白色。"},
            {"id": "D", "severity": "L2", "description": "金属安全扶手与马桶陶瓷本体严重偏冷青暗灰调。"},
            {"id": "E2", "severity": "L2", "description": "卫生间瓷砖原有暖黄色泽严重欠饱和完全丧失。"}
        ],
        "note": "无障碍卫生间米黄瓷砖地面错涂为发暗青灰白(错色 C-L2)，安全扶手与马桶偏冷青暗灰(偏色 D-L2)，瓷砖暖黄欠饱和(欠饱和 E2-L2)。"
    },
    4278: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4279: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "两只大象身体皮肤褶皱与耳廓严重偏暗红褐调。"},
            {"id": "E1", "severity": "L1", "description": "象体高光处红褐色泽略显浓重发闷。"}
        ],
        "note": "大象皮肤褶皱与耳廓偏暗红褐(偏色 D-L2)，象体高光红褐色略浓重(过饱和 E1-L1)。"
    },
    4281: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "复古起居室碎花壁纸全景严重偏俗艳亮粉红洋红杂色调。"},
            {"id": "E1", "severity": "L2", "description": "壁纸粉红印花过度浓艳刺眼泛荧光。"},
            {"id": "F", "severity": "L2", "description": "整个房间被大面积俗艳粉紫偏色笼罩，室内古雅氛围严重崩解。"}
        ],
        "note": "起居室碎花壁纸严重偏俗艳亮粉红(偏色 D-L2)，壁纸印花过度浓艳泛荧光(过饱和 E1-L2)，粉紫笼罩破坏古典自然度(自然度 F-L2)。"
    },

    # Sheet 15
    4282: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "浴室地面铺设的鲜艳深宝蓝色长毛地垫被错涂为暗沉灰蓝灰色。"},
            {"id": "D", "severity": "L1", "description": "白瓷洗手台与马桶陶瓷表面微偏暗冷青灰调。"},
            {"id": "E2", "severity": "L2", "description": "蓝色地垫原本饱满鲜丽的色泽严重欠饱和褪色。"}
        ],
        "note": "浴室深宝蓝长毛地垫错涂为暗沉灰蓝灰(错色 C-L2)，洗手台微偏暗冷青灰(偏色 D-L1)，地垫色彩严重欠饱和(欠饱和 E2-L2)。"
    },
    4283: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4284: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "海边灯塔主体大红色漆面过度浓艳刺眼偏荧光洋红色。"},
            {"id": "D", "severity": "L1", "description": "海面翻滚浪花与天空阴云略偏暗冷青灰调。"},
            {"id": "F", "severity": "L1", "description": "灯塔红色漆面过度浓艳失真略显浮夸。"}
        ],
        "note": "灯塔大红漆面过度浓艳偏荧光洋红(过饱和 E1-L2)，海面浪花略偏暗冷青灰(偏色 D-L1)，漆面过艳略失真(自然度 F-L1)。"
    },
    4285: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "工作室粉刷墙壁与天花板严重偏暗粉红紫褐杂色调。"},
            {"id": "F", "severity": "L2", "description": "室内漫反射大面积诡异粉紫杂色严重破坏办公空间自然度。"},
            {"id": "E2", "severity": "L1", "description": "窗外绿树与投影幕布边缘欠饱和微弱发暗。"}
        ],
        "note": "工作室墙壁与天花板偏暗粉红紫褐(偏色 D-L2)，大面积粉紫杂斑破坏自然度(自然度 F-L2)，窗外绿树欠饱和(欠饱和 E2-L1)。"
    },
    4287: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "淋浴房置物壁龛内原本鲜亮清爽的湖水浅蓝绿色装饰背景墙被彻底错涂为发暗米灰白色。"},
            {"id": "D", "severity": "L1", "description": "白色独立浴缸与淋浴龙头微偏暗暖黄调。"},
            {"id": "E2", "severity": "L1", "description": "壁龛装饰墙面色彩欠饱和严重脱色。"}
        ],
        "note": "置物壁龛湖水蓝绿背景墙彻底错涂为发暗米灰白(错色 C-L3)，浴缸微偏暗暖黄(偏色 D-L1)，装饰墙面欠饱和脱色(欠饱和 E2-L1)。"
    },
    4288: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "厨房不锈钢冰箱与吊顶天花板略偏暗暖黄褐调。"},
            {"id": "E2", "severity": "L1", "description": "厨房岛台水槽龙头金属光泽欠饱和微弱发暗。"}
        ],
        "note": "不锈钢冰箱与吊顶略偏暗暖黄褐(偏色 D-L1)，水槽龙头金属光泽欠饱和(欠饱和 E2-L1)。"
    },

    # Sheet 16
    4289: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "席地玩耍幼儿金黄色头发被错涂为冰冷浅灰白色。"},
            {"id": "D", "severity": "L2", "description": "幼儿面部与手臂肤色严重偏冷紫褐发暗。"},
            {"id": "F", "severity": "L2", "description": "幼童头部与肤色冷灰暗淡严重破坏儿童肖像自然度。"}
        ],
        "note": "幼儿金黄头发错涂为冰冷浅灰白(错色 C-L2)，面部肤色偏冷紫褐发暗(偏色 D-L2)，儿童肖像失真破坏自然度(自然度 F-L2)。"
    },
    4290: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "人行道旁背景成排绿化树木郁郁葱葱的深绿色树冠被大面积错涂为发暗灰青浅草色。"},
            {"id": "D", "severity": "L1", "description": "水泥路面与深蓝旅行箱略偏冷暗青灰调。"},
            {"id": "E2", "severity": "L2", "description": "绿化树冠与橙色反光路锥色彩严重欠饱和脱色。"}
        ],
        "note": "背景深绿树冠大面积错涂为发暗灰青浅草色(错色 C-L3)，路面略偏冷暗青灰(偏色 D-L1)，树冠与路锥严重欠饱和脱色(欠饱和 E2-L2)。"
    },
    4291: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "杯中插放的熟透香蕉原本鲜亮明黄的果皮被错涂为暗沉发灰的橄榄黄绿色。"},
            {"id": "D", "severity": "L1", "description": "书桌台面与红色马克杯略偏暗冷青调。"},
            {"id": "E2", "severity": "L1", "description": "香蕉鲜果明亮黄色欠饱和发暗。"}
        ],
        "note": "熟透香蕉明黄果皮错涂为发暗橄榄黄绿(错色 C-L2)，书桌略偏暗冷青(偏色 D-L1)，香蕉果皮欠饱和发暗(欠饱和 E2-L1)。"
    },
    4294: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "仿古青花陶瓷双耳大罐蓝色釉面色彩过度浓艳呈刺眼高饱和宝蓝。"},
            {"id": "D", "severity": "L2", "description": "陶瓷罐双耳手柄与展示台面严重偏暗红褐杂色调。"},
            {"id": "F", "severity": "L2", "description": "陶瓷器物过度浓艳刺眼破坏古典陶瓷温润典雅自然度。"}
        ],
        "note": "陶瓷双耳罐蓝色釉面过度浓艳呈刺眼宝蓝(过饱和 E1-L2)，手柄与台面偏暗红褐杂色(偏色 D-L2)，过度浓艳破坏古典自然度(自然度 F-L2)。"
    },
    4296: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4297: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "客厅木质地板与电脑桌略偏暗暖红褐调。"},
            {"id": "E1", "severity": "L1", "description": "前景地毯与杂物高光处红褐色泽略显浓重发闷。"}
        ],
        "note": "客厅地板与电脑桌略偏暗暖红褐(偏色 D-L1)，地毯高光红褐色略浓重(过饱和 E1-L1)。"
    },

    # Sheet 17
    4299: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "飞盘运动员跃起接取的亮紫色飞盘被错涂为发暗浅灰紫色。"},
            {"id": "D", "severity": "L1", "description": "运动场绿茵草坪与远景松树略偏冷暗青灰调。"},
            {"id": "E2", "severity": "L1", "description": "运动员肤色与紫色飞盘色彩欠饱和暗淡。"}
        ],
        "note": "跃起接取的亮紫色飞盘错涂为发暗浅灰紫(错色 C-L2)，草坪与松树略偏冷暗青灰(偏色 D-L1)，飞盘色彩欠饱和(欠饱和 E2-L1)。"
    },
    4300: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "街边花园消火栓周边原本青翠葱郁的灌木灌丛被错涂为发暗枯黄橄榄色。"},
            {"id": "D", "severity": "L1", "description": "砾石花坛地面微偏冷暗青灰调。"},
            {"id": "E2", "severity": "L1", "description": "花园灌木绿叶色彩欠饱和微弱发暗。"}
        ],
        "note": "消火栓周边青翠灌木错涂为发暗枯黄橄榄色(错色 C-L2)，砾石地面微偏冷暗青灰(偏色 D-L1)，灌木绿叶欠饱和(欠饱和 E2-L1)。"
    },
    4301: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4304: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "晚霞落日原本漫天壮丽金黄炽烈的夕阳天空被彻底荒唐错涂为冰冷浅青蓝天光。"},
            {"id": "D", "severity": "L2", "description": "木桩顶部海鸥倒影与水面波光严重偏冷青蓝调。"},
            {"id": "E2", "severity": "L2", "description": "夕阳晚霞炽烈暖金色彩完全丧失严重欠饱和。"},
            {"id": "F", "severity": "L3", "description": "严重违背落日晚霞真实自然色彩常识，画面视觉效果彻底崩溃。"}
        ],
        "note": "金黄炽烈夕阳天空彻底错涂为冰冷浅青蓝(错色 C-L3)，海鸥木桩偏冷青蓝(偏色 D-L2)，夕阳色彩完全丧失(欠饱和 E2-L2)，严重违背自然常识导致视觉崩溃(自然度 F-L3)。"
    },
    4305: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "厨房餐桌花瓶中盛插的明黄色向日葵与鲜红郁金香被错涂为暗淡黄绿与深砖红色。"},
            {"id": "D", "severity": "L1", "description": "木质备餐台面与厨师白色制服微偏暗冷青灰调。"},
            {"id": "E2", "severity": "L1", "description": "鲜切花束整体鲜活色彩欠饱和暗淡。"}
        ],
        "note": "向日葵与郁金香错涂为暗淡黄绿与深砖红(错色 C-L2)，备餐台面微偏暗冷青灰(偏色 D-L1)，鲜切花束色彩欠饱和(欠饱和 E2-L1)。"
    },
    4306: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "滑板少年面部与白色短袖T恤严重偏俗艳粉紫杂色调。"},
            {"id": "E1", "severity": "L2", "description": "U池水泥墙面涂鸦色彩局部过度浓艳刺眼泛荧光。"},
            {"id": "F", "severity": "L2", "description": "少年身上大面积粉紫杂色色斑严重破坏滑板街拍自然度。"}
        ],
        "note": "滑板少年面部与T恤偏俗艳粉紫杂色(偏色 D-L2)，涂鸦过度浓艳泛荧光(过饱和 E1-L2)，杂斑破坏滑板街拍自然度(自然度 F-L2)。"
    },

    # Sheet 18
    4309: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "评奖展台右侧裱花蛋糕白色奶油糖霜被错涂为发暗青黄杂色。"},
            {"id": "C", "severity": "L2", "description": "蛋糕底部托垫原本鲜艳的亮紫色纸盘被错涂为暗淡灰蓝色。"},
            {"id": "D", "severity": "L1", "description": "墨绿色展示台布与烘焙蛋糕略偏暗草绿黄调。"},
            {"id": "E2", "severity": "L1", "description": "获奖第一名彩色缎带色彩欠饱和微弱发暗。"}
        ],
        "note": "裱花蛋糕奶油糖霜错涂为发暗青黄杂色(错色 C-L2)，亮紫色托垫纸盘错涂为暗淡灰蓝(错色 C-L2)，台布偏草绿黄(偏色 D-L1)，获奖缎带欠饱和(欠饱和 E2-L1)。"
    },
    4310: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4313: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4314: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4315: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "连绵起伏的山丘草场与放牧草坪全景严重偏暖黄绿杂色调。"},
            {"id": "E1", "severity": "L1", "description": "山地草坡草色局部饱和度略显浓重发闷。"},
            {"id": "F", "severity": "L2", "description": "漫山遍野草色偏暖泛黄使广袤牧场原有清新自然度受损。"}
        ],
        "note": "山丘草场全景严重偏暖黄绿杂色(偏色 D-L2)，草地局部偏浓发闷(过饱和 E1-L1)，草色泛黄破坏清新自然度(自然度 F-L2)。"
    },
    4316: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "海滩晚霞天空与夕阳余晖略偏暗红褐调。"},
            {"id": "E1", "severity": "L1", "description": "晚霞高光处橙红光晕局部略显浓艳发沉。"}
        ],
        "note": "海滩晚霞与夕阳余晖略偏暗红褐(偏色 D-L1)，晚霞光晕局部略浓艳发沉(过饱和 E1-L1)。"
    },

    # Sheet 19
    4320: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4323: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4326: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "草原漫步长颈鹿身上棕褐色斑块被毛过度浓艳刺眼呈亮红橙色。"},
            {"id": "D", "severity": "L1", "description": "金合欢树树冠与稀树草原地面略偏暗暖红调。"},
            {"id": "F", "severity": "L1", "description": "长颈鹿被毛过度鲜艳略失真。"}
        ],
        "note": "长颈鹿斑块被毛过度浓艳呈亮红橙色(过饱和 E1-L2)，稀树草原地面略偏暗暖红(偏色 D-L1)，被毛过艳略失真(自然度 F-L1)。"
    },
    4328: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "黑色背景前静物红苹果与香蕉果皮严重偏冷紫褐发暗。"},
            {"id": "E2", "severity": "L1", "description": "香蕉与红苹果新鲜果皮光泽欠饱和微弱发暗。"},
            {"id": "F", "severity": "L1", "description": "水果表皮暗紫杂色破坏静物写生真实自然度。"}
        ],
        "note": "静物红苹果与香蕉果皮偏冷紫褐发暗(偏色 D-L2)，果皮光泽欠饱和(欠饱和 E2-L1)，暗紫杂色破坏自然度(自然度 F-L1)。"
    },
    4330: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "卫生间原本温暖明亮的米黄色粉刷墙面被彻底剥夺错涂为冰冷浅灰白色。"},
            {"id": "D", "severity": "L2", "description": "实木镜柜边框与马桶陶瓷本体严重偏冷青暗灰调。"},
            {"id": "E2", "severity": "L2", "description": "卫浴空间温馨暖色氛围完全丧失严重欠饱和。"}
        ],
        "note": "卫生间米黄粉刷墙面彻底错涂为冰冷浅灰白(错色 C-L3)，实木镜柜偏冷青暗灰(偏色 D-L2)，暖色氛围严重欠饱和(欠饱和 E2-L2)。"
    },
    4331: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "卫生间洗手台旁原本温暖柔和的浅粉色瓷砖墙面被彻底错涂为冰冷浅青灰白色。"},
            {"id": "D", "severity": "L2", "description": "洗手台台盆台面与水龙头金属严重偏冷青蓝调。"},
            {"id": "E2", "severity": "L2", "description": "瓷砖原本温润的粉暖色泽严重欠饱和完全脱色。"}
        ],
        "note": "洗手台浅粉色瓷砖墙面彻底错涂为冰冷浅青灰白(错色 C-L3)，洗手台偏冷青蓝(偏色 D-L2)，瓷砖粉暖色严重欠饱和脱色(欠饱和 E2-L2)。"
    },

    # Sheet 20
    4332: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "餐桌前长者面部与手臂肤色严重偏冷紫褐发暗。"},
            {"id": "E2", "severity": "L1", "description": "餐盘中煎蛋、番茄酱与松饼色彩欠饱和微弱发暗。"},
            {"id": "F", "severity": "L1", "description": "长者面部光影发暗发青破坏人物自然度。"}
        ],
        "note": "长者面部肤色偏冷紫褐发暗(偏色 D-L2)，煎蛋与松饼色彩欠饱和(欠饱和 E2-L1)，面部光影发暗破坏自然度(自然度 F-L1)。"
    },
    4333: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "展厅天花板与圆柱表面严重偏暗粉红紫褐杂色调。"},
            {"id": "E1", "severity": "L2", "description": "前景圆形蓝白相间软包座椅高光处泛起刺眼荧光杂色。"},
            {"id": "F", "severity": "L2", "description": "整个展厅清爽的青蓝冷调被大面积粉紫杂色侵染，视觉自然度明显受损。"}
        ],
        "note": "展厅天花板与圆柱偏暗粉红紫褐(偏色 D-L2)，圆形软包座椅高光泛荧光杂色(过饱和 E1-L2)，粉紫侵染破坏自然度(自然度 F-L2)。"
    },
    4336: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "男士面部与颈部肤色严重偏冷暗青灰调。"},
            {"id": "E2", "severity": "L1", "description": "橙色领带与面部健康光泽欠饱和微弱发暗。"},
            {"id": "F", "severity": "L1", "description": "肤色冷灰失调使肖像光泽感减弱。"}
        ],
        "note": "男士面部肤色偏冷暗青灰(偏色 D-L2)，橙色领带与面部光泽欠饱和(欠饱和 E2-L1)，肖像光泽减弱(自然度 F-L1)。"
    },
    4337: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "草坪奔跑右侧女孩所穿鲜艳正红色运动T恤被错涂为发暗灰褐砖红色。"},
            {"id": "C", "severity": "L2", "description": "左侧女孩翠绿色短袖T恤错涂为发暗橄榄灰绿色。"},
            {"id": "D", "severity": "L1", "description": "奔跑草坪与背景树林略偏暗冷青调。"},
            {"id": "E2", "severity": "L1", "description": "女孩运动服饰色彩欠饱和暗淡。"}
        ],
        "note": "右侧女孩正红T恤错涂为发暗灰褐砖红(错色 C-L2)，左侧女孩翠绿T恤错涂为发暗橄榄灰绿(错色 C-L2)，草坪树林略偏冷暗青(偏色 D-L1)，服饰色彩欠饱和(欠饱和 E2-L1)。"
    },
    4338: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "斗牛犬面部皮褶与眼周严重偏暗红褐杂色调。"},
            {"id": "E1", "severity": "L1", "description": "餐椅橙色座套色彩局部略显浓艳发闷。"},
            {"id": "F", "severity": "L2", "description": "斗牛犬面部红褐杂色斑块破坏宠物自然可爱感。"}
        ],
        "note": "斗牛犬面部皮褶偏暗红褐杂色(偏色 D-L2)，餐椅座套局部偏浓发闷(过饱和 E1-L1)，杂色斑块破坏自然度(自然度 F-L2)。"
    },
    4339: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    }
}


def run_checks_and_apply():
    print(f"Total reviews in Batch 19: {len(BATCH_19_REVIEWS)}")
    assert len(BATCH_19_REVIEWS) == 120, f"Expected 120 reviews, got {len(BATCH_19_REVIEWS)}"

    # Check validity
    pass_count = 0
    revise_count = 0
    banned_violations = []

    for tid, review in BATCH_19_REVIEWS.items():
        if review["pass"]:
            pass_count += 1
            assert len(review["defects"]) == 0, f"Task #{tid}: Pass task must have empty defects"
            assert review["note"] == "审查通过", f"Task #{tid}: Pass note must be '审查通过'"
        else:
            revise_count += 1
            assert len(review["defects"]) > 0, f"Task #{tid}: Revision task must have defects"
            assert review["note"] != "审查通过", f"Task #{tid}: Revision note cannot be '审查通过'"

            # Validate each defect
            for d in review["defects"]:
                assert d["id"] in DEFECT_NAME_MAP, f"Task #{tid}: Invalid defect id {d['id']}"
                if d["id"] == "A":
                    assert d["severity"] == "", f"Task #{tid}: Defect A must have empty severity"
                else:
                    assert d["severity"] in ["L1", "L2", "L3"], f"Task #{tid}: Invalid severity {d['severity']}"
                
                # Check banned words
                for bw in BANNED_WORDS:
                    if bw in d["description"]:
                        banned_violations.append((tid, bw, d["description"]))

            for bw in BANNED_WORDS:
                if bw in review["note"]:
                    banned_violations.append((tid, bw, review["note"]))

    if banned_violations:
        print(f"[FAIL] Found {len(banned_violations)} banned word violations:")
        for tid, bw, text in banned_violations:
            print(f"  - Task #{tid}: contains '{bw}' -> {text}")
        raise ValueError("Banned words detected!")
    else:
        print("[PASS] Zero banned words detected across all descriptions and notes.")

    print(f"[STAT] Pass: {pass_count} ({pass_count/120*100:.1f}%), Revisions: {revise_count} ({revise_count/120*100:.1f}%)")

    # Save grounding json
    grounding_data = {}
    for tid, review in BATCH_19_REVIEWS.items():
        grounding_data[str(tid)] = {
            "pass": review["pass"],
            "defects": [
                {
                    "id": d["id"],
                    "name": DEFECT_NAME_MAP[d["id"]],
                    "severity": d["severity"],
                    "description": d["description"]
                }
                for d in review["defects"]
            ],
            "note": review["note"]
        }
    
    with open(GROUNDING_OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(grounding_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved grounding JSON to {GROUNDING_OUT_PATH}")

    # Synchronize into deliverables
    sync_deliverables(grounding_data)


def sync_deliverables(grounding_data):
    print("\nSynchronizing into reviewed_1_10000_all.json and clean.json...")
    
    with open(ALL_JSON_PATH, "r", encoding="utf-8") as f:
        all_data = json.load(f)
        
    with open(CLEAN_JSON_PATH, "r", encoding="utf-8") as f:
        clean_data = json.load(f)
        
    # Map tasks by task_id in human_review
    all_map = {item["human_review"]["task_id"]: item for item in all_data["annotations"]}
    clean_map = {item["human_review"]["task_id"]: item for item in clean_data["annotations"]}
    
    for task_id_str, g_item in grounding_data.items():
        tid = int(task_id_str)
        assert tid in all_map, f"Task #{tid} not found in all.json"
        assert tid in clean_map, f"Task #{tid} not found in clean.json"
        
        all_item = all_map[tid]
        clean_item = clean_map[tid]
        
        # Format defects for deliverable
        formatted_defects = []
        has_defect_a = False
        for d in g_item["defects"]:
            if d["id"] == "A":
                has_defect_a = True
            formatted_defects.append({
                "id": d["id"],
                "name": DEFECT_NAME_MAP[d["id"]],
                "severity": d["severity"],
                "description": d["description"]
            })
            
        # Update all.json
        all_item["defects"] = formatted_defects
        all_item["review_status"] = "已核验"
        all_item["review_note"] = g_item["note"]
        if has_defect_a:
            all_item["reviewed_score"] = 1.0
            all_item["needs_rescoring"] = False
        else:
            all_item["reviewed_score"] = None
            all_item["needs_rescoring"] = True
            
        # Update clean.json (review_note must be empty string "")
        clean_item["defects"] = formatted_defects
        clean_item["review_status"] = "已核验"
        clean_item["review_note"] = ""
        if has_defect_a:
            clean_item["reviewed_score"] = 1.0
            clean_item["needs_rescoring"] = False
        else:
            clean_item["reviewed_score"] = None
            clean_item["needs_rescoring"] = True

    with open(ALL_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Successfully updated {ALL_JSON_PATH}")

    with open(CLEAN_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Successfully updated {CLEAN_JSON_PATH}")


if __name__ == "__main__":
    run_checks_and_apply()
