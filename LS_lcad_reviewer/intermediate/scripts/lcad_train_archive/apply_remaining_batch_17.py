# -*- coding: utf-8 -*-
"""
Apply visual grounding reviews for Remaining Batch 17 (Tasks #3793 ~ #3978, total 120 tasks across 20 sheets).
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
GROUNDING_OUT_PATH = os.path.join(PROJECT_ROOT, "LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_17.json")

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

# 120 Reviews for Batch 17
BATCH_17_REVIEWS = {
    # Sheet 01
    3793: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "婴儿床原本米黄色的床单被严重错涂为俗艳刺眼的荧光芭比粉红色。"},
            {"id": "B", "severity": "L1", "description": "床单粉红颜料向白色小猫爪毛发发生轻微溢色晕染。"},
            {"id": "E1", "severity": "L2", "description": "婴儿床床品色彩过度浓艳刺眼。"}
        ],
        "note": "婴儿床原本米黄色的床单被严重错涂为俗艳刺眼的荧光芭比粉红(错色 C-L3)，粉红颜料向白色小猫爪毛发溢色(溢色 B-L1)，婴儿床床品色彩过度浓艳(过饱和 E1-L2)。"
    },
    3794: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "客厅深黑色电视机背景墙错涂为深咖啡赭褐色。"},
            {"id": "D", "severity": "L2", "description": "全景电视机柜与地板严重偏暖红褐调。"}
        ],
        "note": "客厅深黑色电视机背景墙错涂为深咖啡赭褐色(错色 C-L2)，全景电视机柜与地板偏暖红褐调(偏色 D-L2)。"
    },
    3795: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "卫生间灰绿色瓷砖墙面错涂为发暗脏黄褐色。"},
            {"id": "D", "severity": "L2", "description": "全景洗手台与淋浴瓷砖偏暗黄褐调。"}
        ],
        "note": "卫生间灰绿色瓷砖墙面错涂为发暗脏黄褐色(错色 C-L2)，全景洗手台与淋浴瓷砖偏暗黄褐(偏色 D-L2)。"
    },
    3797: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3799: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "长颈鹿身体黄褐色网状斑块欠饱和发灰。"},
            {"id": "D", "severity": "L1", "description": "木栅栏与背景草坡略偏暗冷灰调。"}
        ],
        "note": "长颈鹿身体黄褐色网状斑块欠饱和发灰(欠饱和 E2-L1)，木栅栏与背景草坡略偏暗冷灰(偏色 D-L1)。"
    },
    3800: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "木质便当盒中雕花胡萝卜块色泽过度浓艳刺眼。"},
            {"id": "D", "severity": "L1", "description": "米饭与配菜微偏暗暖黄调。"}
        ],
        "note": "木质便当盒中雕花胡萝卜块色泽过度浓艳刺眼(过饱和 E1-L2)，米饭与配菜微偏暗暖黄调(偏色 D-L1)。"
    },

    # Sheet 02
    3803: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "网球运动员所穿的纯白运动T恤错涂为大面积泥黄紫褐杂斑。"},
            {"id": "D", "severity": "L2", "description": "球场草坪与护栏偏暗冷青调。"},
            {"id": "F", "severity": "L2", "description": "球衣大面积杂色斑块严重破坏画面视觉自然度。"}
        ],
        "note": "网球运动员所穿的纯白运动T恤错涂为大面积泥黄紫褐杂斑(错色 C-L2)，球场草坪与护栏偏暗冷青(偏色 D-L2)，球衣大面积杂色破坏视觉自然度(自然度 F-L2)。"
    },
    3804: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "白瓷餐盘中炒大虾与胡萝卜丁橙红色过度浓艳刺眼。"},
            {"id": "F", "severity": "L1", "description": "炒大虾高光边缘发硬失真。"}
        ],
        "note": "白瓷餐盘中炒大虾与胡萝卜丁橙红色过度浓艳刺眼(过饱和 E1-L2)，边缘高光发硬失真(自然度 F-L1)。"
    },
    3807: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3808: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "佩戴搞怪香蕉头套男子面颊肤色发黑严重偏冷紫铜色。"},
            {"id": "C", "severity": "L2", "description": "黄色香蕉皮错涂为发暗黄褐色杂斑。"},
            {"id": "F", "severity": "L2", "description": "人物面部色彩失真违和。"}
        ],
        "note": "佩戴搞怪香蕉头套男子面颊肤色发黑严重偏冷紫铜色(偏色 D-L2)，黄色香蕉皮错涂为发暗黄褐色杂斑(错色 C-L2)，人物面部色彩失真违和(自然度 F-L2)。"
    },
    3810: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3811: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "网球场原本墨绿色的塑胶地面被错涂为大面积发暗橄榄黄绿色。"},
            {"id": "D", "severity": "L2", "description": "球场边线与球网偏暗黄褐色调。"}
        ],
        "note": "网球场原本墨绿色的塑胶地面被错涂为大面积发暗橄榄黄绿色(错色 C-L2)，球场边线与球网偏暗黄褐(偏色 D-L2)。"
    },

    # Sheet 03
    3812: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3814: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "宏伟大教堂背后原本湛蓝的天空错涂为惨白无生气的冷灰白色。"},
            {"id": "D", "severity": "L1", "description": "大教堂石砌墙体微偏冷暗调。"}
        ],
        "note": "宏伟大教堂背后原本湛蓝的天空错涂为惨白无生气的冷灰白(错色 C-L2)，大教堂石砌墙体微偏冷暗(偏色 D-L1)。"
    },
    3815: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3816: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "室内梳妆台圆镜红木边框与趴卧灰猫皮毛微偏冷暗褐灰色。"},
            {"id": "E2", "severity": "L1", "description": "镜面反光光影欠饱和微弱发暗。"}
        ],
        "note": "室内梳妆台圆镜红木边框与趴卧灰猫皮毛微偏冷暗褐灰(偏色 D-L1)，镜面反光欠饱和微弱发暗(欠饱和 E2-L1)。"
    },
    3818: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "停靠路边的老式客车原本鲜明的蓝白腰线涂装严重脱色错涂为灰白色。"},
            {"id": "E2", "severity": "L2", "description": "车身漆面欠饱和失色。"},
            {"id": "D", "severity": "L1", "description": "路面与背景略偏暗。"}
        ],
        "note": "停靠路边的老式客车原本鲜明的蓝白腰线涂装严重脱色错涂为灰白色(错色 C-L2)，车身漆面欠饱和失色(欠饱和 E2-L2)，路面与背景略偏暗(偏色 D-L1)。"
    },
    3821: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 04
    3824: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "翻卷海浪中冲浪者紧身防晒服与彩色冲浪板色彩欠饱和微弱发灰。"},
            {"id": "D", "severity": "L1", "description": "海面波浪略偏暗冷灰青调。"}
        ],
        "note": "翻卷海浪中冲浪者紧身防晒服与彩色冲浪板色彩欠饱和微弱发灰(欠饱和 E2-L1)，海面波浪略偏暗冷灰青(偏色 D-L1)。"
    },
    3825: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "多媒体大教室日光灯天花板与浅色粉刷墙壁严重偏冷洋红紫调。"},
            {"id": "E1", "severity": "L1", "description": "局部灯盘反光略显浓艳。"}
        ],
        "note": "多媒体大教室日光灯天花板与浅色粉刷墙壁严重偏冷洋红紫调(偏色 D-L2)，局部灯盘反光略显浓艳(过饱和 E1-L1)。"
    },
    3826: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3828: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "客厅液晶电视屏幕内播放的网球赛事画面欠饱和发黑发暗。"},
            {"id": "D", "severity": "L1", "description": "电视机边框与电视柜偏暗灰褐调。"}
        ],
        "note": "客厅液晶电视屏幕内播放的网球赛事画面欠饱和发黑发暗(欠饱和 E2-L1)，电视机边框与电视柜偏暗灰褐(偏色 D-L1)。"
    },
    3829: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "逆光阳光照耀下金光粼粼的湖面被彻底剥夺金黄晨光错涂为惨白冷灰色。"},
            {"id": "D", "severity": "L2", "description": "湖岸树影与近景人物偏冷暗紫黑调。"},
            {"id": "E2", "severity": "L2", "description": "波光水面严重欠饱和失色。"}
        ],
        "note": "逆光阳光照耀下金光粼粼的湖面被彻底剥夺金黄晨光错涂为惨白冷灰(错色 C-L3)，湖岸树影与近景人物偏冷暗紫黑(偏色 D-L2)，波光水面严重欠饱和失色(欠饱和 E2-L2)。"
    },
    3831: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "病房中原本洁白的病床被褥与米黄墙壁错涂为发暗脏黄赭褐色。"},
            {"id": "D", "severity": "L2", "description": "医用仪器与床头栏杆偏暗黄褐色调。"}
        ],
        "note": "病房中原本洁白的病床被褥与米黄墙壁错涂为发暗脏黄赭褐色(错色 C-L2)，医用仪器与床头栏杆偏暗黄褐(偏色 D-L2)。"
    },

    # Sheet 05
    3832: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "餐桌前品尝牛角包的男子面颊与颈部严重偏冷紫褐发黑。"},
            {"id": "F", "severity": "L2", "description": "面颊皮肤出现不自然斑驳杂色块。"}
        ],
        "note": "餐桌前品尝牛角包的男子面颊与颈部严重偏冷紫褐发黑(偏色 D-L2)，面颊皮肤出现不自然斑驳杂色块(自然度 F-L2)。"
    },
    3833: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "靠窗写字台透过窗户眺望的外景错涂为深紫红与青蓝杂色。"},
            {"id": "D", "severity": "L2", "description": "写字台木纹与百叶窗偏冷暗紫调。"}
        ],
        "note": "靠窗写字台透过窗户眺望的外景错涂为诡异深紫红与青蓝杂色(错色 C-L2)，写字台木纹与百叶窗偏冷暗紫调(偏色 D-L2)。"
    },
    3834: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "驶向站台的通勤列车车头原本醒目的金黄色警示涂装被完全剥夺脱色成灰黑色。"},
            {"id": "E2", "severity": "L2", "description": "车头警示漆面严重欠饱和。"},
            {"id": "D", "severity": "L1", "description": "铁轨砾石微偏冷暗调。"}
        ],
        "note": "驶向站台的通勤列车车头原本醒目的金黄色警示涂装被完全剥夺脱色成灰黑色(错色 C-L3)，车头警示漆面严重欠饱和(欠饱和 E2-L2)，铁轨砾石微偏冷暗(偏色 D-L1)。"
    },
    3835: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "客厅电视机屏幕内男主播所穿蓝色衬衫与演播室背景略偏暗紫发灰。"},
            {"id": "E2", "severity": "L1", "description": "电视画面色彩欠饱和微弱发暗。"}
        ],
        "note": "客厅电视机屏幕内男主播所穿蓝色衬衫与演播室背景略偏暗紫发灰(偏色 D-L1)，电视画面色彩欠饱和微弱发暗(欠饱和 E2-L1)。"
    },
    3837: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "青花瓷碗中新鲜翠绿的西兰花被严重错涂为发霉变质般的土黄焦褐色。"},
            {"id": "D", "severity": "L2", "description": "餐盘与白米饭偏暗黄褐色调。"},
            {"id": "F", "severity": "L2", "description": "西兰花错色严重破坏食物新鲜自然度。"}
        ],
        "note": "青花瓷碗中新鲜翠绿的西兰花被严重错涂为发霉变质般的土黄焦褐色(错色 C-L3)，餐盘与白米饭偏暗黄褐(偏色 D-L2)，西兰花错色严重破坏食物新鲜自然度(自然度 F-L2)。"
    },
    3838: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 06
    3840: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "夜间棒球场内野翠绿草坪被错涂为大面积发暗冷青蓝紫杂色。"},
            {"id": "D", "severity": "L1", "description": "棒球场红土跑道与护网偏暗冷青调。"}
        ],
        "note": "夜间棒球场内野翠绿草坪被错涂为大面积发暗冷青蓝紫杂色(错色 C-L2)，棒球场红土跑道与护网偏暗冷青(偏色 D-L1)。"
    },
    3843: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "客厅米色布艺沙发与背景白色墙壁阴影处微偏暗暖黄灰色。"},
            {"id": "E2", "severity": "L1", "description": "抱枕与茶几装饰欠饱和微弱发灰。"}
        ],
        "note": "客厅米色布艺沙发与背景白色墙壁阴影处微偏暗暖黄灰(偏色 D-L1)，抱枕与茶几装饰欠饱和微弱发灰(欠饱和 E2-L1)。"
    },
    3845: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "白色双洗手台大理石台面及瓷砖墙面色彩欠饱和微弱发灰。"}
        ],
        "note": "白色双洗手台大理石台面及瓷砖墙面色彩欠饱和微弱发灰(欠饱和 E2-L1)。"
    },
    3847: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3848: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "豪华浴室中暖黄色木质百叶窗与大理石台面被完全脱色错涂为冷青灰黑色。"},
            {"id": "D", "severity": "L2", "description": "洗手盆与周围瓷砖严重偏冷青蓝调。"},
            {"id": "E2", "severity": "L2", "description": "木质构件严重欠饱和失色。"}
        ],
        "note": "豪华浴室中暖黄色木质百叶窗与大理石台面被完全脱色错涂为冷青灰黑色(错色 C-L3)，洗手盆与周围瓷砖严重偏冷青蓝调(偏色 D-L2)，木质构件严重欠饱和失色(欠饱和 E2-L2)。"
    },
    3851: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "街道金属立柱上原本大红色的圆形禁停P标志红色禁令圈斜杠错涂为刺眼荧光蓝紫色。"},
            {"id": "E1", "severity": "L2", "description": "禁令标志蓝紫色彩过于浓艳违和。"},
            {"id": "F", "severity": "L2", "description": "严重违背交通标志常理，视觉极为突兀。"}
        ],
        "note": "街道金属立柱上原本大红色的圆形禁停P标志红色禁令圈斜杠错涂为刺眼荧光蓝紫色(错色 C-L3)，禁令标志蓝紫色彩过于浓艳违和(过饱和 E1-L2)，严重违背交通标志常理(自然度 F-L2)。"
    },

    # Sheet 07
    3853: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3854: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L1", "description": "办公桌电脑屏幕前狸花猫面颊毛色过度浓艳偏亮黄色。"},
            {"id": "D", "severity": "L1", "description": "电脑键盘与桌垫微偏暗暖黄调。"}
        ],
        "note": "办公桌电脑屏幕前狸花猫面颊毛色过度浓艳偏亮黄色(过饱和 E1-L1)，电脑键盘与桌垫微偏暗暖黄(偏色 D-L1)。"
    },
    3855: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "餐盘中香煎鸡胸肉排与烤蔬菜全景严重偏冷紫褐发黑。"},
            {"id": "E1", "severity": "L1", "description": "局部焦香部位色彩过度浓艳发闷。"},
            {"id": "F", "severity": "L2", "description": "食物色泽失真严重破坏食欲自然度。"}
        ],
        "note": "餐盘中香煎鸡胸肉排与烤蔬菜全景严重偏冷紫褐发黑(偏色 D-L2)，局部焦香部位色彩过度浓艳发闷(过饱和 E1-L1)，食物色泽失真严重破坏食欲自然度(自然度 F-L2)。"
    },
    3856: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "棒球打击练习笼内小男孩所戴深蓝头盔与面部肤色偏暗红紫杂色。"},
            {"id": "E2", "severity": "L1", "description": "球棒与护网欠饱和微弱发暗。"},
            {"id": "F", "severity": "L1", "description": "面部光影过渡略显不自然。"}
        ],
        "note": "棒球打击练习笼内小男孩所戴深蓝头盔与面部肤色偏暗红紫杂色(偏色 D-L2)，球棒与护网欠饱和微弱发暗(欠饱和 E2-L1)，面部光影过渡略显不自然(自然度 F-L1)。"
    },
    3858: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3859: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "长条法棍三明治中切片红西红柿与生菜沙拉色彩过度浓艳刺眼。"}
        ],
        "note": "长条法棍三明治中切片红西红柿与生菜沙拉色彩过度浓艳刺眼(过饱和 E1-L2)。"
    },

    # Sheet 08
    3860: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "卧室床头台灯暖光下怀抱婴儿的年轻母亲全景严重偏暖橙红杂色。"},
            {"id": "E1", "severity": "L1", "description": "母子面部肤色受过浓暖光侵染。"},
            {"id": "F", "severity": "L1", "description": "室内光影层次略显发闷。"}
        ],
        "note": "卧室床头台灯暖光下怀抱婴儿的年轻母亲全景严重偏暖橙红杂色(偏色 D-L2)，母子面部肤色受过浓暖光侵染(过饱和 E1-L1)，室内光影层次略显发闷(自然度 F-L1)。"
    },
    3861: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L2", "description": "滑雪博物馆展出的复古木质滑雪板与背衬石刻铭文墙色彩严重欠饱和死灰。"},
            {"id": "D", "severity": "L1", "description": "展厅木地板与射灯略偏暗灰冷调。"}
        ],
        "note": "滑雪博物馆展出的复古木质滑雪板与背衬石刻铭文墙色彩严重欠饱和死灰(欠饱和 E2-L2)，展厅木地板与射灯略偏暗灰冷调(偏色 D-L1)。"
    },
    3862: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3864: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3867: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "卫生间原本米白色暖调瓷砖墙面与地面被错涂为大面积冷青蓝灰色。"},
            {"id": "D", "severity": "L2", "description": "洗手台白色陶瓷盆与梳妆镜严重偏冷青蓝调。"}
        ],
        "note": "卫生间原本米白色暖调瓷砖墙面与地面被错涂为大面积冷青蓝灰色(错色 C-L3)，洗手台白色陶瓷盆与梳妆镜严重偏冷青蓝调(偏色 D-L2)。"
    },
    3868: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 09
    3871: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "海滩上空迎风招展的运动特技风筝彩色飘带及海浪泡沫色彩欠饱和偏淡发灰。"}
        ],
        "note": "海滩上空迎风招展的运动特技风筝彩色飘带及海浪泡沫色彩欠饱和偏淡发灰(欠饱和 E2-L1)。"
    },
    3872: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3873: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3874: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "街头身穿白色短袖衬衫的执勤男子面部肤色略偏暗褐色。"},
            {"id": "E2", "severity": "L1", "description": "红色STOP停止手持标牌欠饱和微弱发暗。"}
        ],
        "note": "街头身穿白色短袖衬衫的执勤男子面部肤色略偏暗褐(偏色 D-L1)，红色STOP停止手持标牌欠饱和微弱发暗(欠饱和 E2-L1)。"
    },
    3875: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "地铁站台候车人群中女子所穿原本鲜艳的红色防风外套被错涂为发暗冷蓝紫灰色。"},
            {"id": "D", "severity": "L2", "description": "站台水泥地面与屏蔽门偏冷暗蓝调。"}
        ],
        "note": "地铁站台候车人群中女子所穿原本鲜艳的红色防风外套被错涂为发暗冷蓝紫灰(错色 C-L2)，站台水泥地面与屏蔽门偏冷暗蓝调(偏色 D-L2)。"
    },
    3879: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "蓝色印花陶瓷盘上刚出炉的比萨饼表面焦香奶酪略偏暗黄褐冷青调。"},
            {"id": "E2", "severity": "L1", "description": "烤肠与青椒粒欠饱和微弱发暗。"}
        ],
        "note": "蓝色印花陶瓷盘上刚出炉的比萨饼表面焦香奶酪略偏暗黄褐冷青调(偏色 D-L1)，烤肠与青椒粒欠饱和微弱发暗(欠饱和 E2-L1)。"
    },

    # Sheet 10
    3880: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3881: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3882: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "过道瓷砖与集市过道略偏暗灰褐调。"},
            {"id": "E2", "severity": "L1", "description": "室内商场集市手工艺品柜台木质展示架与红衣女摊主服饰色彩欠饱和微暗。"}
        ],
        "note": "室内商场集市手工艺品柜台木质展示架与红衣女摊主服饰色彩欠饱和微暗(欠饱和 E2-L1)，过道瓷砖偏暗灰褐(偏色 D-L1)。"
    },
    3884: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "电视机旁纯白塑料外壳的Wii体感遥控手柄被错涂为发暗泥黄色脏油污斑。"},
            {"id": "D", "severity": "L1", "description": "电视机塑料外壳与连接线偏暗灰褐色调。"}
        ],
        "note": "电视机旁纯白塑料外壳的Wii体感遥控手柄被错涂为发暗泥黄色脏油污斑(错色 C-L2)，电视机塑料外壳与连接线偏暗灰褐(偏色 D-L1)。"
    },
    3885: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "围坐切生日蛋糕庆祝的母女二人中母亲面颊与颈部严重偏冷紫褐发黑。"},
            {"id": "E2", "severity": "L1", "description": "水果蛋糕表面奶油与草莓欠饱和微弱发暗。"},
            {"id": "F", "severity": "L2", "description": "面部肤色不自然斑驳。"}
        ],
        "note": "围坐切生日蛋糕庆祝的母女二人中母亲面颊与颈部严重偏冷紫褐发黑(偏色 D-L2)，水果蛋糕表面奶油与草莓欠饱和微弱发暗(欠饱和 E2-L1)，面部肤色不自然斑驳(自然度 F-L2)。"
    },
    3889: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "红木餐桌上安睡的黄白相间橘猫毛发与桌腿微偏暗褐灰色。"},
            {"id": "E2", "severity": "L1", "description": "毛皮金色光泽欠饱和略显发暗。"}
        ],
        "note": "红木餐桌上安睡的黄白相间橘猫毛发与桌腿微偏暗褐灰(偏色 D-L1)，毛皮金色光泽欠饱和略显发暗(欠饱和 E2-L1)。"
    },

    # Sheet 11
    3890: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "卧室双人床粉色软包床头板与浅色床单严重偏暗冷紫红调。"},
            {"id": "F", "severity": "L2", "description": "床头墙壁与枕头阴影处出现不自然紫红脏色斑块。"}
        ],
        "note": "卧室双人床粉色软包床头板与浅色床单严重偏暗冷紫红调(偏色 D-L2)，床头墙壁与枕头阴影处出现不自然紫红脏色斑块(自然度 F-L2)。"
    },
    3891: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "海滩冲浪板租赁木屋前整齐排立的各色冲浪板严重欠饱和褪色错涂。"},
            {"id": "E2", "severity": "L2", "description": "冲浪板原本鲜艳的红黄青蓝漆面严重脱色失真。"},
            {"id": "D", "severity": "L1", "description": "木质外墙微偏暗灰色。"}
        ],
        "note": "海滩冲浪板租赁木屋前整齐排立的各色冲浪板严重欠饱和褪色错涂(错色 C-L2)，冲浪板原本鲜艳的红黄青蓝漆面严重脱色失真(欠饱和 E2-L2)，木质外墙微偏暗灰(偏色 D-L1)。"
    },
    3893: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "现代浴室黑色大理石洗手台面、镜框与瓷砖墙面严重偏冷暗蓝紫调。"}
        ],
        "note": "现代浴室黑色大理石洗手台面、镜框与瓷砖墙面严重偏冷暗蓝紫调(偏色 D-L2)。"
    },
    3896: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3897: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3900: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "客厅中手持白色遥控器玩体感游戏的年轻男子衣物与米色客厅背景略偏暗灰冷青调。"}
        ],
        "note": "客厅中手持白色遥控器玩体感游戏的年轻男子衣物与米色客厅背景略偏暗灰冷青(偏色 D-L1)。"
    },

    # Sheet 12
    3903: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "机场跑道停机坪停靠的小型支线双发螺旋桨客机黄色垂直尾翼欠饱和微弱发灰。"}
        ],
        "note": "机场跑道停机坪停靠的小型支线双发螺旋桨客机黄色垂直尾翼欠饱和微弱发灰(欠饱和 E2-L1)。"
    },
    3904: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "玻璃花瓶前摆放的大型雕塑胡萝卜原本橙黄表皮错涂为刺眼荧光深红杂色。"},
            {"id": "E1", "severity": "L2", "description": "胡萝卜雕塑色彩过度浓艳刺眼。"},
            {"id": "D", "severity": "L2", "description": "木质展台偏暗紫褐调。"}
        ],
        "note": "玻璃花瓶前摆放的大型雕塑胡萝卜原本橙黄表皮错涂为刺眼荧光深红杂色(错色 C-L2)，胡萝卜雕塑色彩过度浓艳(过饱和 E1-L2)，木质展台偏暗紫褐(偏色 D-L2)。"
    },
    3905: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "办公室工位电脑前工作的短发年轻男青年面部肤色偏暗黄褐色。"},
            {"id": "E2", "severity": "L1", "description": "电脑显示器与桌面文具欠饱和微弱发暗。"}
        ],
        "note": "办公室工位电脑前工作的短发年轻男青年面部肤色偏暗黄褐(偏色 D-L1)，电脑显示器与桌面文具欠饱和微弱发暗(欠饱和 E2-L1)。"
    },
    3906: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "列车维护车库中停放的现代化通勤列车车厢绿色装饰腰线过于荧光浓艳刺眼。"},
            {"id": "D", "severity": "L2", "description": "车库混凝土地面与车体偏冷暗紫蓝调。"},
            {"id": "F", "severity": "L1", "description": "高光边界发硬失真。"}
        ],
        "note": "列车维护车库中停放的现代化通勤列车车厢绿色装饰腰线过于荧光浓艳刺眼(过饱和 E1-L2)，车库混凝土地面与车体偏冷暗紫蓝(偏色 D-L2)，高光边界失真(自然度 F-L1)。"
    },
    3907: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "艺术展厅中展出的红白同心圆靶心大象彩绘雕塑靶心错涂为发暗泥灰褐色。"},
            {"id": "D", "severity": "L2", "description": "大象雕塑灰白皮肤与展台偏冷暗紫调。"}
        ],
        "note": "艺术展厅中展出的红白同心圆靶心大象彩绘雕塑靶心错涂为发暗泥灰褐色(错色 C-L2)，大象雕塑灰白皮肤与展台偏冷暗紫调(偏色 D-L2)。"
    },
    3908: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 13
    3909: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "木质围栏后站立观察的非洲斑马身体黑白相间条纹色彩欠饱和微弱发灰发暗。"}
        ],
        "note": "木质围栏后站立观察的非洲斑马身体黑白相间条纹色彩欠饱和微弱发灰发暗(欠饱和 E2-L1)。"
    },
    3910: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "晴空草坪上空翱翔的多条巨型彩色章鱼软体风筝严重欠饱和褪色错涂。"},
            {"id": "E2", "severity": "L2", "description": "风筝红黄橙条纹严重脱色发灰。"},
            {"id": "D", "severity": "L1", "description": "草坪与蓝天微偏冷暗调。"}
        ],
        "note": "晴空草坪上空翱翔的多条巨型彩色章鱼软体风筝严重欠饱和褪色错涂(错色 C-L2)，风筝红黄橙条纹严重脱色发灰(欠饱和 E2-L2)，草坪与蓝天微偏冷暗(偏色 D-L1)。"
    },
    3912: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "绿茵场上头戴白帽的男子手中紧握的荧光绿极限飞盘过于浓艳刺眼。"},
            {"id": "B", "severity": "L1", "description": "荧光绿漆料向男子指尖手臂轻微溢色。"},
            {"id": "D", "severity": "L1", "description": "背景草坪偏暗冷青调。"}
        ],
        "note": "绿茵场上头戴白帽的男子手中紧握的荧光绿极限飞盘过于浓艳刺眼(过饱和 E1-L2)，荧光绿漆料向男子指尖手臂轻微溢色(溢色 B-L1)，背景草坪偏暗冷青(偏色 D-L1)。"
    },
    3916: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "白瓷盘中精美切片蓝莓芝士蛋糕顶层紫色果酱浓汁过度浓艳刺眼。"},
            {"id": "D", "severity": "L1", "description": "餐叉与餐盘边缘微偏冷暗调。"}
        ],
        "note": "白瓷盘中精美切片蓝莓芝士蛋糕顶层紫色果酱浓汁过度浓艳刺眼(过饱和 E1-L2)，餐叉与餐盘边缘微偏冷暗(偏色 D-L1)。"
    },
    3917: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "泥土斜坡小道上牵马农夫与棕色骡马皮毛及行囊色彩欠饱和微弱发暗。"},
            {"id": "D", "severity": "L1", "description": "路面沙土与树林微偏暗冷绿调。"}
        ],
        "note": "泥土斜坡小道上牵马农夫与棕色骡马皮毛及行囊色彩欠饱和微弱发暗(欠饱和 E2-L1)，路面沙土与树林微偏暗冷绿(偏色 D-L1)。"
    },
    3918: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "室内瓷砖地面上停放的白色折叠自行车车架金属烤漆严重偏冷暗灰蓝调。"},
            {"id": "E2", "severity": "L1", "description": "车座皮革与车轮辐条欠饱和微弱发暗。"}
        ],
        "note": "室内瓷砖地面上停放的白色折叠自行车车架金属烤漆严重偏冷暗灰蓝调(偏色 D-L2)，车座皮革与车轮辐条欠饱和微弱发暗(欠饱和 E2-L1)。"
    },

    # Sheet 14
    3919: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3920: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "厨房中手捧新鲜出炉烤点心的厨师面颊与额头被染上大面积深紫红杂色斑块。"},
            {"id": "E1", "severity": "L2", "description": "厨师白色围裙与点心盘色彩局部过浓。"},
            {"id": "F", "severity": "L2", "description": "面部杂色严重破坏人物自然度。"}
        ],
        "note": "厨房中手捧新鲜出炉烤点心的厨师面颊与额头被染上大面积深紫红杂色斑块(偏色 D-L2)，厨师白色围裙与点心盘色彩局部过浓(过饱和 E1-L2)，面部杂色严重破坏人物自然度(自然度 F-L2)。"
    },
    3921: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "浴室窗户下方纯白色陶瓷洗手池盆体与瓷砖被错涂为冷青水绿微偏紫杂色。"},
            {"id": "D", "severity": "L2", "description": "金属水龙头与窗帘全景偏冷青蓝暗调。"}
        ],
        "note": "浴室窗户下方纯白色陶瓷洗手池盆体与瓷砖被错涂为冷青水绿微偏紫杂色(错色 C-L2)，金属水龙头与窗帘全景偏冷青蓝暗调(偏色 D-L2)。"
    },
    3924: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "白色厨房中不锈钢燃气灶台与白色方形瓷砖墙面严重偏冷暗灰蓝调。"},
            {"id": "E2", "severity": "L1", "description": "灶台锅具与旋钮欠饱和微弱发暗。"}
        ],
        "note": "白色厨房中不锈钢燃气灶台与白色方形瓷砖墙面严重偏冷暗灰蓝调(偏色 D-L2)，灶台锅具与旋钮欠饱和微弱发暗(欠饱和 E2-L1)。"
    },
    3927: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3928: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "阶梯多媒体大教室弧形木质长桌前操作笔记本电脑的学生服饰略偏暗冷青调。"},
            {"id": "E2", "severity": "L1", "description": "讲台背景与投影白板欠饱和微弱发暗。"}
        ],
        "note": "阶梯多媒体大教室弧形木质长桌前操作笔记本电脑的学生服饰略偏暗冷青(偏色 D-L1)，讲台背景与投影白板欠饱和微弱发暗(欠饱和 E2-L1)。"
    },

    # Sheet 15
    3929: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "温暖家庭餐桌前聚会的小女孩面颊与手臂肤色严重偏冷暗红紫杂色。"},
            {"id": "F", "severity": "L1", "description": "面部受光过渡略显生硬失真。"}
        ],
        "note": "温暖家庭餐桌前聚会的小女孩面颊与手臂肤色严重偏冷暗红紫杂色(偏色 D-L2)，面部受光过渡略显生硬失真(自然度 F-L1)。"
    },
    3930: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3931: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "特写镜头下马匹头部原本柔顺明亮的红棕色鬃毛被严重剥夺脱色错涂为惨白灰黑色。"},
            {"id": "E2", "severity": "L2", "description": "马匹皮毛严重欠饱和失色。"},
            {"id": "D", "severity": "L2", "description": "背景绿树与马辔偏冷暗紫调。"}
        ],
        "note": "特写镜头下马匹头部原本柔顺明亮的红棕色鬃毛被严重剥夺脱色错涂为惨白灰黑色(错色 C-L3)，马匹皮毛严重欠饱和失色(欠饱和 E2-L2)，背景绿树与马辔偏冷暗紫调(偏色 D-L2)。"
    },
    3932: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "广袤非洲热带草原上漫步的长颈鹿群头顶晴朗湛蓝的天空被错涂为刺眼浓艳的橙黄日落暮色。"},
            {"id": "E1", "severity": "L2", "description": "黄昏天空饱和度过高。"},
            {"id": "D", "severity": "L2", "description": "草原灌木林地全景偏冷暗紫调。"}
        ],
        "note": "广袤非洲热带草原上漫步的长颈鹿群头顶晴朗湛蓝的天空被错涂为刺眼浓艳的橙黄日落暮色(错色 C-L2)，黄昏天空饱和度过高(过饱和 E1-L2)，草原灌木林地全景偏冷暗紫调(偏色 D-L2)。"
    },
    3933: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "火车车厢墨绿色软包座椅上摆放的金黄色毛绒玩具小熊被错涂为发暗黄褐色杂斑。"},
            {"id": "D", "severity": "L2", "description": "车窗外掠过的风景与车厢内壁偏冷暗蓝紫调。"},
            {"id": "F", "severity": "L2", "description": "玩具小熊色彩质感失真违和。"}
        ],
        "note": "火车车厢墨绿色软包座椅上摆放的金黄色毛绒玩具小熊被错涂为发暗黄褐色杂斑(错色 C-L2)，车窗外掠过的风景与车厢内壁偏冷暗蓝紫(偏色 D-L2)，玩具小熊色彩质感失真(自然度 F-L2)。"
    },
    3934: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 16
    3935: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "棒球手所穿的鲜艳宝蓝色野猫队（Wildcats）球衣及球帽被严重错涂为发暗灰黑褐色。"},
            {"id": "C", "severity": "L2", "description": "球衣胸前原本纯白色 Wildcats 刺绣字样被错涂为草绿黄色。"},
            {"id": "D", "severity": "L2", "description": "全图草坪与人物肤色偏暗草绿黄调。"}
        ],
        "note": "棒球手所穿的鲜艳宝蓝色野猫队（Wildcats）球衣及球帽被严重错涂为发暗灰黑褐色(错色 C-L3)，球衣胸前原本纯白色 Wildcats 刺绣字样被错涂为草绿黄色(错色 C-L2)，全图草坪与人物肤色偏暗草绿黄调(偏色 D-L2)。"
    },
    3936: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "藤编果篮中苹果、甜橙与编织竹条全景偏冷暗红褐调。"},
            {"id": "E2", "severity": "L1", "description": "绿色手写标价纸欠饱和微弱发暗。"}
        ],
        "note": "藤编果篮中苹果、甜橙与编织竹条全景偏冷暗红褐调(偏色 D-L2)，绿色手写标价纸欠饱和微弱发暗(欠饱和 E2-L1)。"
    },
    3938: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "海面上空晴朗天空与湛蓝海水饱和度偏低发灰。"},
            {"id": "D", "severity": "L1", "description": "远景帆船船帆与海面白浪略偏暗灰冷青调。"}
        ],
        "note": "海面上空晴朗天空与湛蓝海水饱和度偏低发灰(欠饱和 E2-L1)，远景帆船船帆与海面白浪略偏暗灰冷青(偏色 D-L1)。"
    },
    3940: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3941: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3942: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "室内窗户两侧墙面与踢脚线偏冷暗灰褐调。"},
            {"id": "E2", "severity": "L2", "description": "花纹遮光卷帘透光暖色欠饱和发暗。"},
            {"id": "F", "severity": "L2", "description": "室内整体光影层次发闷丧失通透感。"}
        ],
        "note": "室内窗户两侧墙面与踢脚线偏冷暗灰褐(偏色 D-L2)，花纹遮光卷帘透光暖色欠饱和发暗(欠饱和 E2-L2)，室内整体光影层次发闷丧失通透感(自然度 F-L2)。"
    },

    # Sheet 17
    3944: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "草坪上跨栏奔跑男青年所穿的鲜艳亮红色运动T恤被彻底剥夺错涂为暗沉灰墨绿色。"},
            {"id": "E2", "severity": "L2", "description": "人物服饰严重欠饱和失色。"},
            {"id": "D", "severity": "L1", "description": "背景砖石建筑与草地整体略偏暗冷绿调。"}
        ],
        "note": "草坪上跨栏奔跑男青年所穿的鲜艳亮红色运动T恤被彻底剥夺错涂为暗沉灰墨绿色(错色 C-L3)，人物服饰严重欠饱和失色(欠饱和 E2-L2)，背景砖石建筑与草地整体略偏暗冷绿(偏色 D-L1)。"
    },
    3946: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "厨房深色木质橱柜与大理石台面偏冷暗红紫调。"},
            {"id": "E2", "severity": "L1", "description": "窗外绿植采光欠饱和微弱发暗。"}
        ],
        "note": "厨房深色木质橱柜与大理石台面偏冷暗红紫调(偏色 D-L2)，窗外绿植采光欠饱和微弱发暗(欠饱和 E2-L1)。"
    },
    3947: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3948: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3949: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "机场跑道黄褐色荒漠土地被错涂为大面积冷蓝紫灰色。"},
            {"id": "D", "severity": "L2", "description": "全图停机坪与军用运输机机身严重偏冷蓝紫调。"},
            {"id": "E2", "severity": "L1", "description": "螺旋桨桨叶红白警示标欠饱和发暗。"}
        ],
        "note": "机场跑道黄褐色荒漠土地被错涂为大面积冷蓝紫灰(错色 C-L2)，全图停机坪与军用运输机机身严重偏冷蓝紫调(偏色 D-L2)，螺旋桨桨叶红白警示标欠饱和发暗(欠饱和 E2-L1)。"
    },
    3950: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "海浪中戏水女孩所穿的粉红橙色泳衣欠饱和错涂为灰褐色。"},
            {"id": "E2", "severity": "L1", "description": "浪花中人物肤色欠饱和微弱发灰。"}
        ],
        "note": "海浪中戏水女孩所穿的粉红橙色泳衣欠饱和错涂为灰褐色(错色 C-L2)，浪花中人物肤色欠饱和微弱发灰(欠饱和 E2-L1)。"
    },

    # Sheet 18
    3951: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "夜景街头沥青路面与行进步行道严重偏暖橙红杂色。"},
            {"id": "E1", "severity": "L2", "description": "背景车灯与店铺暖色光晕过度浓艳刺眼。"},
            {"id": "F", "severity": "L2", "description": "街道夜景光斑边缘严重失真发散。"}
        ],
        "note": "夜景街头沥青路面与行进步行道严重偏暖橙红杂色(偏色 D-L2)，背景车灯与店铺暖色光晕过度浓艳刺眼(过饱和 E1-L2)，街道夜景光斑边缘严重失真发散(自然度 F-L2)。"
    },
    3952: {
        "pass": False,
        "defects": [
            {"id": "B", "severity": "L2", "description": "生日蛋糕蓝色奶油边缘严重溢色晕染至盘面与嘴角。"},
            {"id": "D", "severity": "L1", "description": "红色餐桌布与小孩面颊偏冷紫暗调。"},
            {"id": "F", "severity": "L2", "description": "小孩面部肤色出现不自然青紫杂色色斑。"}
        ],
        "note": "生日蛋糕蓝色奶油边缘严重溢色晕染至盘面与嘴角(溢色 B-L2)，红色餐桌布与小孩面颊偏冷紫暗调(偏色 D-L1)，小孩面部肤色出现不自然青紫杂色色斑(自然度 F-L2)。"
    },
    3954: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "旋转木马游乐设施左侧粉红气球立柱装饰错涂为发暗青蓝杂色。"},
            {"id": "C", "severity": "L2", "description": "小女孩身上粉红连衣裙褪色错涂为灰褐色。"},
            {"id": "D", "severity": "L2", "description": "游乐场设施背景整体偏冷蓝青暗调。"}
        ],
        "note": "旋转木马游乐设施左侧粉红气球立柱装饰错涂为发暗青蓝杂色(错色 C-L3)，小女孩身上粉红连衣裙褪色错涂为灰褐色(错色 C-L2)，游乐场设施背景整体偏冷蓝青暗调(偏色 D-L2)。"
    },
    3957: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3959: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "集市果摊棚顶与木质展示货架略偏暗暖黄灰色。"},
            {"id": "E1", "severity": "L1", "description": "摊位前排红草莓与绿叶蔬菜饱和度略显过浓。"},
            {"id": "F", "severity": "L1", "description": "密集水果堆叠处局部交界处出现轻微色彩杂色。"}
        ],
        "note": "集市果摊棚顶与木质展示货架略偏暗暖黄灰(偏色 D-L1)，摊位前排红草莓与绿叶蔬菜饱和度略显过浓(过饱和 E1-L1)，密集水果堆叠处局部交界处出现轻微色彩杂色(自然度 F-L1)。"
    },
    3960: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "餐桌左侧原本鲜艳宝蓝色的折叠餐巾纸被彻底错涂为发暗米白黄色。"},
            {"id": "D", "severity": "L2", "description": "木质餐桌与盘中烤制甜品全景偏暗红紫发黑。"},
            {"id": "E1", "severity": "L1", "description": "背景光源局部暖色浓艳发闷。"}
        ],
        "note": "餐桌左侧原本鲜艳宝蓝色的折叠餐巾纸被彻底错涂为发暗米白黄色(错色 C-L3)，木质餐桌与盘中烤制甜品全景偏暗红紫发黑(偏色 D-L2)，背景光源局部暖色浓艳发闷(过饱和 E1-L1)。"
    },

    # Sheet 19
    3964: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "宴会厅背景墙面与天花板严重偏暖橙黄调。"},
            {"id": "E1", "severity": "L2", "description": "室内吊灯与环境光色调过度浓艳刺眼。"},
            {"id": "F", "severity": "L1", "description": "人物面部肤色受浓烈黄光浸染发黄。"}
        ],
        "note": "宴会厅背景墙面与天花板严重偏暖橙黄调(偏色 D-L2)，室内吊灯与环境光色调过度浓艳刺眼(过饱和 E1-L2)，人物面部肤色受浓烈黄光浸染发黄(自然度 F-L1)。"
    },
    3965: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "室内敞开门廊上方墙壁与远景厨房严重偏冷紫蓝灰色。"},
            {"id": "E2", "severity": "L1", "description": "地面积雪倒影透光暖色欠饱和发暗。"},
            {"id": "F", "severity": "L2", "description": "室内冷暖光影对比突兀失真。"}
        ],
        "note": "室内敞开门廊上方墙壁与远景厨房严重偏冷紫蓝灰(偏色 D-L2)，地面积雪倒影透光暖色欠饱和发暗(欠饱和 E2-L1)，室内冷暖光影对比突兀失真(自然度 F-L2)。"
    },
    3966: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3967: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "树梢悬挂风筝的粉红与青绿拼接面错涂为大面积杂乱刺眼荧光洋红紫色。"},
            {"id": "B", "severity": "L2", "description": "风筝艳色严重溢出色块边缘渗透树枝。"},
            {"id": "D", "severity": "L2", "description": "蓝天与干枯树枝全景偏冷青紫发暗。"},
            {"id": "F", "severity": "L3", "description": "风筝色彩结构完全崩解失真。"}
        ],
        "note": "树梢悬挂风筝的粉红与青绿拼接面错涂为大面积杂乱刺眼荧光洋红紫(错色 C-L3)，风筝艳色严重溢出色块边缘渗透树枝(溢色 B-L2)，蓝天与干枯树枝全景偏冷青紫发暗(偏色 D-L2)，风筝色彩结构完全崩解失真(自然度 F-L3)。"
    },
    3968: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L3", "description": "浴室木质浴缸与周围瓷砖墙地面严重偏冷青蓝紫杂色。"},
            {"id": "C", "severity": "L2", "description": "浴缸内部与水面错涂为浑浊暗黄绿色。"},
            {"id": "F", "severity": "L2", "description": "浴室整体空间色温严重分裂失真。"}
        ],
        "note": "浴室木质浴缸与周围瓷砖墙地面严重偏冷青蓝紫杂色(偏色 D-L3)，浴缸内部与水面错涂为浑浊暗黄绿色(错色 C-L2)，浴室整体空间色温严重分裂失真(自然度 F-L2)。"
    },
    3969: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "多层自助餐架上汉堡切片红西红柿被错涂为发暗橙黄褐色。"},
            {"id": "D", "severity": "L2", "description": "金属点心展示架与白瓷餐盘偏冷青蓝紫调。"},
            {"id": "E2", "severity": "L1", "description": "新鲜夹馅蔬菜欠饱和微弱发暗。"}
        ],
        "note": "多层自助餐架上汉堡切片红西红柿被错涂为发暗橙黄褐色(错色 C-L2)，金属点心展示架与白瓷餐盘偏冷青蓝紫调(偏色 D-L2)，新鲜夹馅蔬菜欠饱和微弱发暗(欠饱和 E2-L1)。"
    },

    # Sheet 20
    3971: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3973: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3974: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3975: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "白炽灯暖黄光照下的卫生间墙面与洁具被彻底剥夺暖色错涂为冷青灰白色。"},
            {"id": "D", "severity": "L2", "description": "卫生间洗手台镜面与毛巾架偏冷青蓝调。"},
            {"id": "E2", "severity": "L2", "description": "室内温馨暖调光影严重欠饱和失色。"}
        ],
        "note": "白炽灯暖黄光照下的卫生间墙面与洁具被彻底剥夺暖色错涂为冷青灰白(错色 C-L3)，卫生间洗手台镜面与毛巾架偏冷青蓝调(偏色 D-L2)，室内温馨暖调光影严重欠饱和失色(欠饱和 E2-L2)。"
    },
    3977: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "历史卧室白色粉刷墙壁与天花板偏冷蓝灰暗调。"},
            {"id": "E2", "severity": "L1", "description": "四柱床深色木质立柱与游客服饰欠饱和微弱发暗。"}
        ],
        "note": "历史卧室白色粉刷墙壁与天花板偏冷蓝灰暗调(偏色 D-L2)，四柱床深色木质立柱与游客服饰欠饱和微弱发暗(欠饱和 E2-L1)。"
    },
    3978: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "金发小男孩身上原本鲜艳亮丽的明黄色翻领运动T恤被彻底剥夺错涂为暗沉灰褐色。"},
            {"id": "E2", "severity": "L2", "description": "人物服饰严重欠饱和失色。"},
            {"id": "D", "severity": "L1", "description": "木质桌面与室内背景略偏冷暗调。"}
        ],
        "note": "金发小男孩身上原本鲜艳亮丽的明黄色翻领运动T恤被彻底剥夺错涂为暗沉灰褐色(错色 C-L3)，人物服饰严重欠饱和失色(欠饱和 E2-L2)，木质桌面与室内背景略偏冷暗(偏色 D-L1)。"
    }
}


def run_checks_and_apply():
    print(f"Total reviews in Batch 17: {len(BATCH_17_REVIEWS)}")
    assert len(BATCH_17_REVIEWS) == 120, f"Expected 120 reviews, got {len(BATCH_17_REVIEWS)}"

    # Check banned words and schema compliance
    pass_count = 0
    revise_count = 0
    banned_violations = []

    for tid, review in BATCH_17_REVIEWS.items():
        is_pass = review["pass"]
        if is_pass:
            pass_count += 1
            assert review["defects"] == [], f"Task #{tid}: Pass items must have empty defects list"
            assert review["note"] == "审查通过", f"Task #{tid}: Pass items must have review_note '审查通过'"
        else:
            revise_count += 1
            assert len(review["defects"]) > 0, f"Task #{tid}: Non-pass items must have at least one defect"
            for d in review["defects"]:
                assert d["id"] in DEFECT_NAME_MAP, f"Task #{tid}: Invalid defect ID {d['id']}"
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
    for tid, review in BATCH_17_REVIEWS.items():
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
