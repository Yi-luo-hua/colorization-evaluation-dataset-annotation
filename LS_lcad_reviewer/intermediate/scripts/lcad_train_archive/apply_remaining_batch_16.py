# -*- coding: utf-8 -*-
"""
Apply visual grounding reviews for Remaining Batch 16 (Tasks #3600 ~ #3792, total 120 tasks across 20 sheets).
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
GROUNDING_OUT_PATH = os.path.join(PROJECT_ROOT, "LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_16.json")

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

# 120 Reviews for Batch 16
BATCH_16_REVIEWS = {
    # Sheet 01
    3600: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "路口金属立柱上原本鲜红色的STOP停止交通标志牌被严重错涂为草黄绿色。"},
            {"id": "D", "severity": "L2", "description": "街道沥青路面与背景天空全景严重偏冷青暗灰调。"},
            {"id": "F", "severity": "L2", "description": "STOP标志牌错色严重违背交通标志常理，视觉极为违和。"}
        ],
        "note": "路口金属立柱上原本鲜红色的STOP停止交通标志牌被严重错涂为草黄绿色(错色 C-L3)，街道沥青路面与背景天空偏冷青(偏色 D-L2)，交通标志错色违背常识(自然度 F-L2)。"
    },
    3601: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "厨房白色台面上摆放的整串香蕉表皮黄色过度浓艳刺眼，高光边缘发硬。"}
        ],
        "note": "厨房白色台面上摆放的整串香蕉表皮黄色过度浓艳刺眼(过饱和 E1-L2)。"
    },
    3603: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "厨房中原本浅粉色的复古双门冰箱被完全脱色错涂为灰白金属色。"},
            {"id": "E2", "severity": "L2", "description": "复古冰箱粉红烤漆及厨房木质橱柜严重欠饱和褪色发灰。"},
            {"id": "D", "severity": "L1", "description": "厨房地砖与天花板略偏暗灰褐调。"}
        ],
        "note": "原本浅粉色的复古双门冰箱被脱色错涂为灰白金属色(错色 C-L2)，复古冰箱与木质橱柜严重欠饱和(欠饱和 E2-L2)，地砖天花板略偏暗(偏色 D-L1)。"
    },
    3604: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "比萨饼表面原本鲜红色的香肠切片被脱色错涂为暗焦黄色。"},
            {"id": "E2", "severity": "L1", "description": "比萨表面番茄酱汁与肉类馅料欠饱和发暗。"},
            {"id": "F", "severity": "L1", "description": "香肠切片色泽干瘪焦暗缺乏食欲感。"}
        ],
        "note": "比萨表面鲜红香肠切片被脱色错涂为暗焦黄色(错色 C-L2)，番茄酱汁欠饱和(欠饱和 E2-L1)，肉片干瘪暗沉(自然度 F-L1)。"
    },
    3605: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3607: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "城市街道上方原本晴朗湛蓝的天空被颠覆错涂为火烧云般的烈火橙红色。"},
            {"id": "D", "severity": "L2", "description": "临街红砖建筑立面与树木受橙红天空漫射全域严重偏暖橙红调。"},
            {"id": "F", "severity": "L2", "description": "大白天城市街景出现晚霞烈火天空，违背真实自然光照规律。"}
        ],
        "note": "城市街道原本晴朗湛蓝的天空被颠覆错涂为烈火橙红色(错色 C-L3)，红砖建筑与街道偏暖橙红(偏色 D-L2)，日光白昼与晚霞天空冲突(自然度 F-L2)。"
    },

    # Sheet 02
    3609: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "商业街红砖外墙上原本极其鲜红醒目的Levi's招牌被彻底剥夺脱色错涂为灰褐泥垢色。"},
            {"id": "E2", "severity": "L2", "description": "品牌招牌红色字体及街道砖墙严重欠饱和泛灰失色。"},
            {"id": "D", "severity": "L1", "description": "街景路面与建筑外墙略偏暗灰冷调。"}
        ],
        "note": "红砖外墙上原本鲜红醒目的Levi's招牌被剥夺脱色错涂为灰褐色(错色 C-L3)，招牌红色完全褪色(欠饱和 E2-L2)，街景略偏暗灰(偏色 D-L1)。"
    },
    3610: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3612: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "卫生间角落原本浅紫色的塑料水桶被严重错涂为深蓝色。"},
            {"id": "B", "severity": "L1", "description": "塑料水桶深蓝颜料向地面白色瓷砖接缝边缘溢色。"},
            {"id": "D", "severity": "L1", "description": "卫生间地面瓷砖与墙壁略偏冷青蓝调。"}
        ],
        "note": "原本浅紫色的塑料水桶被错涂为深蓝色(错色 C-L2)，水桶边缘向瓷砖溢色(溢色 B-L1)，瓷砖偏冷蓝(偏色 D-L1)。"
    },
    3613: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "集会现场奥巴马竞选看板原本鲜艳纯正的宝蓝背景被脱色错涂为深黑无色。"},
            {"id": "E2", "severity": "L2", "description": "竞选标语红白蓝三色看板严重欠饱和褪色发暗。"},
            {"id": "D", "severity": "L1", "description": "集会人群服饰与背景遮阳棚略偏暗灰冷青调。"}
        ],
        "note": "竞选看板原本宝蓝色背景被脱色错涂为深黑色(错色 C-L2)，看板文字严重欠饱和(欠饱和 E2-L2)，人群略偏冷暗(偏色 D-L1)。"
    },
    3615: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "雨天街头行走女子身穿的红色风衣与手撑的彩色雨伞色彩欠饱和泛灰发暗。"},
            {"id": "D", "severity": "L1", "description": "湿滑人行道沥青地面与临街店铺略偏冷青暗灰。"}
        ],
        "note": "女子红色风衣与手撑彩色雨伞色彩欠饱和泛灰发暗(欠饱和 E2-L1)，湿滑路面略偏冷青(偏色 D-L1)。"
    },
    3616: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "面包房蛋糕展示柜台前原本纯洁雪白的展示桌布被大面积严重错涂为刺眼荧光洋红色。"},
            {"id": "E1", "severity": "L1", "description": "台布洋红染料过度鲜艳刺眼，荧光感强烈。"}
        ],
        "note": "蛋糕展示台原本雪白的展示桌布被严重错涂为刺眼荧光洋红色(错色 C-L3)，台布洋红色过度刺眼(过饱和 E1-L1)。"
    },

    # Sheet 03
    3619: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "城市街道上方原本深邃碧蓝的夜空被完全荒谬地误涂为浑浊明亮的暖黄色与土黄白昼色。"},
            {"id": "D", "severity": "L2", "description": "街道两旁路灯、绿化树与行车道全景严重泛混杂暖黄褐冷浊色。"},
            {"id": "F", "severity": "L1", "description": "黑夜城市夜景出现白天亮黄色天空，光照逻辑严重失真。"}
        ],
        "note": "深邃碧蓝的夜空被误涂为浑浊明亮的暖黄色(错色 C-L3)，街道两旁全景泛黄褐偏色(偏色 D-L2)，夜景昼夜光照矛盾(自然度 F-L1)。"
    },
    3620: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "电脑桌上原本纯白色的键盘键帽与鼠标外壳全域严重偏油黄棕褐色，呈发霉泛旧感。"},
            {"id": "F", "severity": "L1", "description": "白色键盘按键受黄色污斑浸染，光洁度破坏。"}
        ],
        "note": "白色键盘键帽与鼠标外壳全域严重偏油黄棕褐色(偏色 D-L2)，键盘表面出现泛黄污迹感(自然度 F-L1)。"
    },
    3621: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3622: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "乡村公路旁停靠的厢式货车原本明黄色的车厢外壳被严重脱色错涂为惨白灰黑色。"},
            {"id": "E2", "severity": "L2", "description": "黄色厢式货车车体及路边草地牛群严重欠饱和褪色发灰。"}
        ],
        "note": "厢式货车明黄色车厢外壳被脱色错涂为惨白色(错色 C-L2)，货车与周边景物严重欠饱和(欠饱和 E2-L2)。"
    },
    3623: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3625: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "客厅米黄色墙壁、布艺双人沙发与木质茶几全景严重偏冰冷青白色，丧失室内温馨暖光。"},
            {"id": "E2", "severity": "L1", "description": "沙发靠垫与木地板色彩欠饱和微弱发灰。"}
        ],
        "note": "客厅米黄墙壁与布艺沙发全景严重偏冰冷青白(偏色 D-L2)，沙发靠垫欠饱和发灰(欠饱和 E2-L1)。"
    },

    # Sheet 04
    3626: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "铁路轨道上内燃机车车头原本极其醒目的金黄色防撞警示涂装被剥夺脱色错涂为灰白色。"},
            {"id": "E2", "severity": "L2", "description": "火车机车黄色涂装与车窗边缘严重欠饱和泛灰失色。"}
        ],
        "note": "内燃机车车头金黄色警示涂装被剥夺脱色错涂为灰白色(错色 C-L2)，火车黄色机身严重欠饱和(欠饱和 E2-L2)。"
    },
    3627: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3629: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "客厅布艺条纹沙发红色座垫与背后墙壁涂装略微偏暗暖红调。"}
        ],
        "note": "布艺条纹沙发红色座垫与背后墙壁涂装略微偏暗暖红(偏色 D-L1)。"
    },
    3631: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3634: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "草地上放置的原本深蓝色的塑料飞盘被错涂脱色为浅灰黄色。"},
            {"id": "E2", "severity": "L1", "description": "塑料飞盘及周边草皮色彩欠饱和略显发暗。"}
        ],
        "note": "原本深蓝色的塑料飞盘被错涂脱色为浅灰黄色(错色 C-L2)，飞盘与草坪欠饱和(欠饱和 E2-L1)。"
    },
    3636: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "牧羊犬嘴里叼着的亮黄色塑料飞盘色彩过度浓艳刺眼，高光处溢出。"},
            {"id": "D", "severity": "L1", "description": "牧羊犬头部毛发与周边草地略偏暖黄绿色。"}
        ],
        "note": "牧羊犬嘴里叼着的亮黄色塑料飞盘色彩过度浓艳刺眼(过饱和 E1-L2)，犬毛与草地偏暖黄(偏色 D-L1)。"
    },

    # Sheet 05
    3637: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "室内男子身穿的原本深蓝色的纯棉T恤被严重脱色错涂为白灰色。"},
            {"id": "E2", "severity": "L2", "description": "深蓝短袖T恤染料完全剥落发白，严重欠饱和。"},
            {"id": "D", "severity": "L2", "description": "室内木质家具与人物皮肤整体偏青冷暗灰调。"}
        ],
        "note": "男子身上原本深蓝色的纯棉T恤被脱色错涂为白灰色(错色 C-L2)，T恤严重欠饱和发白(欠饱和 E2-L2)，室内全景偏青冷暗灰(偏色 D-L2)。"
    },
    3639: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "沙滩上身穿粉红色碎花连衣裙的年轻女子及粉色防晒帽色彩欠饱和发暗。"},
            {"id": "B", "severity": "L1", "description": "粉色连衣裙裙摆边缘粉色颜料向沙滩浅滩微弱扩散渗色。"},
            {"id": "D", "severity": "L2", "description": "海面海水与沙滩全景严重偏灰冷青调，缺乏热带阳光氛围。"},
            {"id": "F", "severity": "L2", "description": "人物粉裙边缘与沙滩水流交界处色彩过渡模糊发暗。"}
        ],
        "note": "女子粉红碎花连衣裙及小帽欠饱和发暗(欠饱和 E2-L1)，裙摆向沙滩溢色(溢色 B-L1)，海天全景偏冷青(偏色 D-L2)，过渡模糊生硬(自然度 F-L2)。"
    },
    3641: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "雪山合影登山队员身上穿着的红色冲锋衣与蓝色防寒服色彩偏淡发暗欠饱和。"},
            {"id": "D", "severity": "L1", "description": "雪地高光与背景针叶林略微偏冷青暗灰。"}
        ],
        "note": "登山队员红色与蓝色防寒服色彩偏淡欠饱和(欠饱和 E2-L1)，雪地与树木略偏冷青(偏色 D-L1)。"
    },
    3643: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3644: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "客厅纯白墙壁、窗框以及木质电视柜略微偏暗暖红调。"}
        ],
        "note": "客厅白色墙壁、窗框与电视柜略微偏暗暖红(偏色 D-L1)。"
    },
    3645: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "海滨草坪野餐男子背后原本纯净湛蓝的天空被错涂为惨白泛紫天色。"},
            {"id": "E1", "severity": "L2", "description": "野餐草坪嫩绿色草地被渲染得过度荧光浓艳，刺眼失真。"},
            {"id": "D", "severity": "L1", "description": "野餐布与人物服饰略偏冷青暗调。"},
            {"id": "F", "severity": "L1", "description": "荧光绿草坪与发白天空反差强烈视觉不协调。"}
        ],
        "note": "背景湛蓝天空被错涂为惨白泛紫天色(错色 C-L2)，草坪过度荧光浓艳(过饱和 E1-L2)，野餐布偏冷暗(偏色 D-L1)，反差不自然(自然度 F-L1)。"
    },

    # Sheet 06
    3651: {
        "pass": False,
        "defects": [
            {"id": "B", "severity": "L1", "description": "十字路口红灯亮起处强烈的红色光晕向湿滑夜雨天空及电线边缘溢色扩张。"},
            {"id": "D", "severity": "L2", "description": "雨夜湿滑沥青路面与车道全景整体偏暗暖黄红调，失去雨夜清冷反光。"}
        ],
        "note": "红灯红色光晕向夜雨天空溢色(溢色 B-L1)，湿滑沥青路面整体偏暖黄红调失真(偏色 D-L2)。"
    },
    3652: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3654: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3656: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3658: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "原野棕榈树下的长颈鹿群黄褐色网状斑块及棕榈树干泛灰欠饱和。"}
        ],
        "note": "长颈鹿群黄褐色斑块与棕榈树干泛灰欠饱和(欠饱和 E2-L1)。"
    },
    3660: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 07
    3662: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "户外餐桌旁交谈的白胡须老者面部与双手皮肤血色欠缺，呈现泛灰苍白失润。"}
        ],
        "note": "老者面部与双手皮肤血色欠缺泛灰苍白(欠饱和 E2-L1)。"
    },
    3665: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3666: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3668: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "浴室瓷砖墙面原本温暖明亮的浅米黄色被严重错涂为冷青灰褐色。"},
            {"id": "D", "severity": "L2", "description": "椭圆挂镜中自拍男子面部与浴室全景系统性偏冷青灰暗调。"},
            {"id": "E2", "severity": "L2", "description": "镜中男子面部肤色及胡茬严重脱色泛灰。"}
        ],
        "note": "原本米黄色浴室瓷砖墙面被错涂为冷青灰褐色(错色 C-L2)，浴室全景偏冷青灰(偏色 D-L2)，男子肤色严重脱色泛灰(欠饱和 E2-L2)。"
    },
    3671: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "欧式豪华卧室大床床头金黄色软包背景墙色彩过度浓艳刺眼，荧光感强烈。"},
            {"id": "D", "severity": "L1", "description": "白色大床被褥及床幔略偏冷青调。"},
            {"id": "F", "severity": "L1", "description": "金黄色软包强光与冷色床品过渡生硬不自然。"}
        ],
        "note": "床头金黄色软包背景墙过度浓艳刺眼(过饱和 E1-L2)，白色被褥略偏冷青(偏色 D-L1)，光影过渡生硬(自然度 F-L1)。"
    },
    3675: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "客厅布艺双人沙发及落地电风扇金属网罩色泽略显偏淡发灰欠饱和。"},
            {"id": "D", "severity": "L1", "description": "木质地板与茶几表面略偏暗暖褐色调。"}
        ],
        "note": "客厅布艺沙发与落地电风扇网罩色泽偏淡欠饱和(欠饱和 E2-L1)，木地板略偏暗暖褐(偏色 D-L1)。"
    },

    # Sheet 08
    3676: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "棒球场击球手身穿的原本鲜艳纯正的红色长袖运动内衬与红袜被完全脱色错涂为灰白色。"},
            {"id": "E2", "severity": "L2", "description": "击球区红土与击球手服饰严重欠饱和褪色发白。"},
            {"id": "D", "severity": "L2", "description": "棒球场草坪与红土打击区全景整体偏冷青发灰。"}
        ],
        "note": "击球手鲜艳红色长袖球衣与红袜被完全脱色错涂为灰白色(错色 C-L3)，红土与服饰严重欠饱和(欠饱和 E2-L2)，全景偏冷青发灰(偏色 D-L2)。"
    },
    3680: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "草地上男青年身穿的原本纯正深蓝色短袖T恤被严重错涂为红黄杂色斑块。"},
            {"id": "E1", "severity": "L1", "description": "草坪上插放的红色与蓝色小风车羽翼过于浓艳刺眼。"}
        ],
        "note": "男青年深蓝色T恤被严重错涂为红黄杂色斑块(错色 C-L2)，草地上彩色小风车浓艳刺眼(过饱和 E1-L1)。"
    },
    3681: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "礁石背景原本晴朗蔚蓝的海天被错涂褪色为惨白无色的冷灰色。"},
            {"id": "E2", "severity": "L2", "description": "海风吹拂的灰发女士身穿的牛仔裤及大海海浪严重欠饱和泛灰。"},
            {"id": "D", "severity": "L1", "description": "海景礁石全图色调偏冷青发暗。"}
        ],
        "note": "原本蔚蓝海天被错涂褪色为惨白冷灰(错色 C-L2)，女士牛仔裤及海浪欠饱和发灰(欠饱和 E2-L2)，全图偏冷青暗调(偏色 D-L1)。"
    },
    3683: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3685: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3686: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "红土网球场看台四周原本墨绿色的赞助商广告挡板被严重错涂为青灰泛紫调。"},
            {"id": "D", "severity": "L1", "description": "红土网球场地表面与看台观众席整体偏冷青紫调。"}
        ],
        "note": "红土网球场看台四周墨绿色广告挡板被错涂为青灰泛紫(错色 C-L2)，红土场地与看台偏冷青紫(偏色 D-L1)。"
    },

    # Sheet 09
    3688: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "原本通透碧蓝的热带海面被严重错涂为浑浊肮脏的灰绿与暗黄褐泥浆色。"},
            {"id": "D", "severity": "L2", "description": "海天相接全景严重泛黄绿冷浊偏色，丧失热带海洋澄澈感。"},
            {"id": "E2", "severity": "L1", "description": "木船白色船体与棚顶欠饱和发灰。"}
        ],
        "note": "通透碧蓝海面被严重错涂为浑浊灰绿与暗黄褐色(错色 C-L3)，海天全景严重偏黄绿冷浊(偏色 D-L2)，木船欠饱和发灰(欠饱和 E2-L1)。"
    },
    3691: {
        "pass": False,
        "defects": [
            {"id": "B", "severity": "L1", "description": "孔雀颈部浓重翠蓝羽毛向背部羽毛及周围空气扩散溢色。"},
            {"id": "D", "severity": "L2", "description": "花园砖石背景墙与木质长椅严重偏洋红紫调。"},
            {"id": "F", "severity": "L2", "description": "孔雀翠绿覆羽与洋红背景产生强烈杂色违和斑块。"}
        ],
        "note": "孔雀翠蓝颈部羽毛向外溢色(溢色 B-L1)，花园砖墙与木椅严重偏洋红紫(偏色 D-L2)，羽毛与背景杂色违和(自然度 F-L2)。"
    },
    3693: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "长颈鹿面颊下颚与喂食女子服饰大面积严重偏冷紫褐调。"},
            {"id": "C", "severity": "L2", "description": "长颈鹿头部原本金黄色的毛发被错涂为暗紫灰色。"},
            {"id": "F", "severity": "L1", "description": "长颈鹿面部光影过渡带有突兀的紫青色斑。"}
        ],
        "note": "长颈鹿面颊与女子服饰严重偏冷紫褐调(偏色 D-L2)，长颈鹿头部毛发错涂为暗紫灰(错色 C-L2)，面颊紫青杂斑不自然(自然度 F-L1)。"
    },
    3695: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3696: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3700: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 10
    3702: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3704: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3705: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "游乐设施骑乘者身穿的亮黄色工装外套色彩过度浓艳刺眼，荧光感强烈。"},
            {"id": "D", "severity": "L1", "description": "游乐设施金属支架与暗处背景偏青冷紫调。"},
            {"id": "F", "severity": "L1", "description": "荧光黄外套与背景过渡生硬不自然。"}
        ],
        "note": "骑乘者亮黄色外套色彩过度浓艳刺眼(过饱和 E1-L2)，金属支架偏冷紫(偏色 D-L1)，光影过渡生硬(自然度 F-L1)。"
    },
    3706: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "桌面木纹及餐巾纸整体偏冷青发暗，甜甜圈表面蒙上一层发暗的青黄浊色。"},
            {"id": "F", "severity": "L1", "description": "鲜牛奶白瓷杯与甜甜圈表面呈现微弱青绿杂色光晕。"}
        ],
        "note": "桌面木纹与餐巾纸偏冷青发暗(偏色 D-L1)，牛奶杯与甜甜圈呈现青绿杂色光晕(自然度 F-L1)。"
    },
    3708: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "室内墙壁偏草绿暗黄，母亲面部与手臂肤色严重偏冷紫发黑。"},
            {"id": "F", "severity": "L2", "description": "人物皮肤与生日蛋糕表面出现大面积违和杂色暗斑。"}
        ],
        "note": "室内墙壁偏草绿暗黄且母亲肤色偏冷紫发黑(偏色 D-L2)，皮肤与蛋糕表面散布违和暗斑(自然度 F-L2)。"
    },
    3709: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "客厅天花板射灯光照区域与米色落地窗帘略偏冷淡白光。"},
            {"id": "E2", "severity": "L1", "description": "双人沙发红色靠垫与棕色皮质沙发欠饱和微弱发暗。"}
        ],
        "note": "天花板射灯区域略偏冷淡白光(偏色 D-L1)，红色靠垫欠饱和发暗(欠饱和 E2-L1)。"
    },

    # Sheet 11
    3711: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3713: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3714: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "街头橱窗人偶头戴的原本鲜艳纯正的红色毛线贝雷帽被完全脱色错涂为灰黑杂色。"},
            {"id": "E2", "severity": "L2", "description": "人偶红色围巾及行人浅蓝衬衫严重欠饱和褪色。"},
            {"id": "D", "severity": "L1", "description": "人行道街景全图整体偏冷青发灰。"}
        ],
        "note": "橱窗人偶鲜红毛线贝雷帽被脱色错涂为灰黑杂色(错色 C-L3)，红色围巾严重欠饱和(欠饱和 E2-L2)，街景全图偏冷青灰(偏色 D-L1)。"
    },
    3715: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "晴朗蔚蓝的背景天空被严重错涂为惨白无色的冷青灰天。"},
            {"id": "D", "severity": "L1", "description": "大象粗糙皮肤及泥沙地面偏冷灰发暗。"},
            {"id": "E2", "severity": "L1", "description": "泥土喷洒的大象全身整体色彩欠饱和褪色。"}
        ],
        "note": "晴朗蔚蓝天空错涂为惨白冷青灰(错色 C-L2)，大象皮肤泥沙偏冷灰(偏色 D-L1)，大象欠饱和褪色(欠饱和 E2-L1)。"
    },
    3716: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "室内原本淡雅的米白色走廊墙壁与门框被严重错涂为浓烈刺眼的柠檬黄色。"},
            {"id": "E1", "severity": "L2", "description": "走廊墙面柠檬黄色过度浓艳刺眼，高光过饱和。"},
            {"id": "D", "severity": "L2", "description": "镜前自拍男子面部肤色及络腮胡须严重偏黄褐色。"}
        ],
        "note": "米白走廊墙壁与门框错涂为浓烈柠檬黄(错色 C-L2)，墙面过度浓艳刺眼(过饱和 E1-L2)，男子肤色偏黄褐(偏色 D-L2)。"
    },
    3717: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 12
    3718: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3719: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "集市排队人群服饰及餐车彩色招牌略偏青冷微暗。"},
            {"id": "E2", "severity": "L1", "description": "排队顾客红色T恤及柠檬水餐车黄色标牌欠饱和泛淡。"}
        ],
        "note": "集市排队人群及餐车招牌略偏青冷(偏色 D-L1)，红衣顾客及黄色招牌欠饱和(欠饱和 E2-L1)。"
    },
    3720: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "商铺内部商品货架与灯光照明严重偏冷青蓝紫调。"},
            {"id": "E2", "severity": "L1", "description": "站立男士身穿的迷彩外套与肤色欠饱和泛黑发暗。"},
            {"id": "F", "severity": "L1", "description": "货架暗处阴影冷青色过渡突兀不自然。"}
        ],
        "note": "商铺货架与灯光严重偏冷青蓝紫(偏色 D-L2)，男士迷彩服欠饱和发暗(欠饱和 E2-L1)，暗处阴影过渡突兀(自然度 F-L1)。"
    },
    3721: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3722: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3723: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "果摊上鲜嫩青绿的香蕉果串被严重错涂为发暗的红褐色与焦黄杂斑。"},
            {"id": "D", "severity": "L2", "description": "香蕉表皮与果轴整体严重偏暗红褐色偏色。"},
            {"id": "F", "severity": "L2", "description": "青香蕉果皮表面散布突兀的黑红污斑，视觉极不协调。"}
        ],
        "note": "鲜嫩青香蕉果串错涂为暗红褐与焦黄杂斑(错色 C-L2)，果轴整体偏暗红褐(偏色 D-L2)，表皮黑红污斑不自然(自然度 F-L2)。"
    },

    # Sheet 13
    3724: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3725: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3726: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "两只斑马黑白相间的皮毛条纹全域严重偏冷蓝紫调，黑色鬃毛泛上深蓝冷光。"},
            {"id": "F", "severity": "L1", "description": "斑马面颊与脖颈白色条纹泛冷光偏色不自然。"}
        ],
        "note": "两只斑马黑白皮毛条纹严重偏冷蓝紫调(偏色 D-L2)，白条纹泛冷光不自然(自然度 F-L1)。"
    },
    3728: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "水边原本鲜绿茂盛的绿草坪被严重脱色错涂为惨白无色的灰石地。"},
            {"id": "E2", "severity": "L2", "description": "野鸭群羽毛及背景草坪欠饱和褪色严重。"},
            {"id": "D", "severity": "L1", "description": "草地野鸭全图整体偏冷青灰白调。"}
        ],
        "note": "鲜绿草坪被脱色错涂为惨白灰石地(错色 C-L3)，野鸭羽毛与草坪欠饱和严重(欠饱和 E2-L2)，全图偏冷青灰白(偏色 D-L1)。"
    },
    3729: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "服装店内衣架悬挂的原本纯黑深色衣物被严重错涂为大片鲜艳血红与橙红杂色。"},
            {"id": "B", "severity": "L2", "description": "红色颜料向衣架周围及白色柜台金属支架大面积渗色溢色。"},
            {"id": "D", "severity": "L1", "description": "服装店天花板射灯与墙面略偏冷青暗灰。"}
        ],
        "note": "衣架悬挂纯黑衣物被错涂为大片血红橙红色(错色 C-L3)，红色向柜台支架渗色(溢色 B-L2)，天花板偏冷青灰(偏色 D-L1)。"
    },
    3730: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "手工作品展示台深蓝背景幕布及纸伞被严重错涂为刺眼洋红与荧光黄杂色。"},
            {"id": "E1", "severity": "L2", "description": "折纸伞面与船身彩色纸张过度荧光浓艳失真。"},
            {"id": "D", "severity": "L2", "description": "小船模型全景偏洋红紫光偏色严重。"},
            {"id": "F", "severity": "L2", "description": "模型背景与工艺品色彩混乱毫无真实感。"}
        ],
        "note": "深蓝背景幕布错涂为刺眼洋红荧光黄(错色 C-L3)，折纸伞面过度荧光浓艳(过饱和 E1-L2)，全景偏洋红紫(偏色 D-L2)，色彩混乱失真(自然度 F-L2)。"
    },

    # Sheet 14
    3731: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3735: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "浴室天花板与古典吊灯周围墙面略偏暖黄泛暗。"},
            {"id": "E2", "severity": "L1", "description": "拱形窗框黑色金属漆与大浴缸大理石台面欠饱和微弱发灰。"}
        ],
        "note": "浴室天花板与吊灯周围略偏暗暖黄(偏色 D-L1)，窗框与浴缸台面欠饱和发灰(欠饱和 E2-L1)。"
    },
    3736: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "酒吧室内聚会墙壁与围坐年轻人面部肤色全域严重偏暖橙红调。"},
            {"id": "F", "severity": "L1", "description": "人物面颊高光过热红晕油腻，过渡不自然。"}
        ],
        "note": "酒吧墙壁与人物面部肤色严重偏暖橙红(偏色 D-L2)，面颊高光过热过渡不自然(自然度 F-L1)。"
    },
    3739: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "家庭餐厅全景墙壁与室内吊灯光照略偏暗黄褐色调。"},
            {"id": "E2", "severity": "L1", "description": "长餐桌中央绿色盆栽植物与就餐老人服饰欠饱和发暗。"}
        ],
        "note": "餐厅全景墙壁略偏暗黄褐(偏色 D-L1)，餐桌绿植与老人服饰欠饱和发暗(欠饱和 E2-L1)。"
    },
    3743: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3745: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "老式卧室原本温暖的米黄色墙壁被严重错涂为青绿冷蓝色，床上鲜艳紫红床单被完全脱色错涂为灰黑。"},
            {"id": "D", "severity": "L2", "description": "铁艺床架与室内空间全域严重偏冷青绿蓝调。"},
            {"id": "E2", "severity": "L2", "description": "床上被单被褥严重欠饱和褪色发黑。"}
        ],
        "note": "米黄墙壁错涂为青绿冷蓝且紫红床单错涂为灰黑(错色 C-L3)，室内全域偏冷青绿蓝(偏色 D-L2)，床品欠饱和褪色严重(欠饱和 E2-L2)。"
    },

    # Sheet 15
    3746: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "室内男子身上原本鲜艳翠绿色的短袖POLO衫被严重颠覆错涂为亮黄色伴随橙红阴影。"},
            {"id": "D", "severity": "L1", "description": "男子面部肤色与室内暗处偏冷紫调。"},
            {"id": "F", "severity": "L1", "description": "黄色衣服褶皱阴影过渡突兀发黑不自然。"}
        ],
        "note": "男子鲜绿短袖POLO衫被颠覆错涂为亮黄色(错色 C-L3)，面部肤色偏冷紫(偏色 D-L1)，黄色阴影过渡突兀(自然度 F-L1)。"
    },
    3747: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "树林树冠逆光透射高光与茂盛树叶色彩过度浓艳刺眼。"},
            {"id": "D", "severity": "L1", "description": "树顶高光漫射区域偏冷青白紫调。"},
            {"id": "F", "severity": "L1", "description": "逆光高光处泛白发硬过渡生硬。"}
        ],
        "note": "树冠逆光高光与树叶过度浓艳刺眼(过饱和 E1-L2)，高光漫射偏冷青白紫(偏色 D-L1)，高光生硬发硬(自然度 F-L1)。"
    },
    3748: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "雪地里滑雪老者身穿的鲜红冲锋衣被脱色错涂为暗赭褐色。"},
            {"id": "E2", "severity": "L2", "description": "滑雪者冲锋衣及同行者毛线围巾严重欠饱和发暗。"},
            {"id": "D", "severity": "L1", "description": "雪地山林与背景天空全景偏冷青暗灰。"}
        ],
        "note": "老者鲜红冲锋衣被脱色错涂为暗赭褐(错色 C-L2)，冲锋衣与围巾严重欠饱和(欠饱和 E2-L2)，雪地全景偏冷青灰(偏色 D-L1)。"
    },
    3749: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3750: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "公园里两位小女孩身穿的粉紫色羽绒服与红格子围巾色彩欠饱和发淡。"},
            {"id": "D", "severity": "L1", "description": "人物面部肤色及水泥路面略偏冷青暗灰。"}
        ],
        "note": "小女孩粉紫羽绒服与红围巾欠饱和色泽发淡(欠饱和 E2-L1)，面部肤色略偏冷青(偏色 D-L1)。"
    },
    3751: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "网球公开赛红土场地原本经典的砖红色地面被彻底颠覆错涂为墨绿色草坪地。"},
            {"id": "D", "severity": "L2", "description": "球场看台挡板与红土全场系统性偏冷绿青调。"},
            {"id": "F", "severity": "L2", "description": "世界级红土大满贯赛场被涂成草地色，违背常识荒谬失真。"}
        ],
        "note": "红土网球场砖红地面被彻底错涂为墨绿草坪色(错色 C-L3)，全场严重偏冷绿青(偏色 D-L2)，红土场地错色违背常识(自然度 F-L2)。"
    },

    # Sheet 16
    3752: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3753: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3755: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "雪山合影背景原本纯净晴朗的蓝天被严重错涂为过饱和浓重的深宝蓝与青紫色。"},
            {"id": "E1", "severity": "L2", "description": "背景天空与雪地反光过度浓艳刺眼。"},
            {"id": "D", "severity": "L2", "description": "雪山林海全景严重偏冷青蓝紫光。"}
        ],
        "note": "背景蓝天被错涂为过饱和深宝蓝青紫色(错色 C-L2)，天空与雪面过度浓艳(过饱和 E1-L2)，全景偏冷青蓝紫(偏色 D-L2)。"
    },
    3756: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "庭院石墙与地面严重偏洋红紫调，白色马桶表面散布紫青杂色。"},
            {"id": "E1", "severity": "L1", "description": "盆栽绿叶局部过度浓艳发焦黑。"},
            {"id": "F", "severity": "L2", "description": "白色陶瓷马桶与砖墙周边散布突兀的紫青杂斑不自然。"}
        ],
        "note": "庭院石墙与地面严重偏洋红紫调(偏色 D-L2)，盆栽绿叶局部发焦浓艳(过饱和 E1-L1)，马桶砖墙散布紫青杂斑(自然度 F-L2)。"
    },
    3757: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "卫生间原本浅雅清爽的淡蓝竖条纹壁纸被严重错涂加深为偏紫冷水蓝色。"},
            {"id": "D", "severity": "L2", "description": "卫生间天花板及马桶水箱反光全域严重偏冷蓝紫调。"}
        ],
        "note": "淡蓝竖条纹壁纸错涂加深为偏紫冷水蓝(错色 C-L2)，天花板与马桶反光严重偏冷蓝紫(偏色 D-L2)。"
    },
    3758: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 17
    3759: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "客厅茶几中央摆放的鲜艳花束色彩欠饱和褪色发暗。"}
        ],
        "note": "客厅茶几中央摆放的鲜花花束色彩欠饱和发暗(欠饱和 E2-L1)。"
    },
    3762: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3763: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "床上女子原本鲜艳纯正的西瓜红无袖背心被严重脱色错涂为灰黄色。"},
            {"id": "E2", "severity": "L2", "description": "女子背心及床上被单严重欠饱和发白褪色。"},
            {"id": "D", "severity": "L1", "description": "卧室内景与猫咪皮毛全景偏冷青暗灰。"}
        ],
        "note": "女子西瓜红无袖背心被脱色错涂为灰黄色(错色 C-L3)，背心与被单严重欠饱和(欠饱和 E2-L2)，全景偏冷青暗灰(偏色 D-L1)。"
    },
    3764: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "比萨表面番茄酱红肉切片及外卖包装纸盒红色印刷欠饱和发暗。"},
            {"id": "D", "severity": "L1", "description": "餐桌桌面与餐具略偏暗黄灰调。"}
        ],
        "note": "比萨肉片及外卖盒红色印刷欠饱和发暗(欠饱和 E2-L1)，桌面餐具略偏暗黄灰(偏色 D-L1)。"
    },
    3767: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "乡村泥土路上的白色瘤牛身体及泥土地面略显欠饱和偏冷灰。"}
        ],
        "note": "白色瘤牛身体及泥土地面略显欠饱和偏冷灰(欠饱和 E2-L1)。"
    },
    3768: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "港口码头原本清澈通透的水面被严重错涂为发暗的灰紫与粉红色污斑。"},
            {"id": "D", "severity": "L2", "description": "水面水域及停靠游船船体全景严重偏洋红紫光偏色。"},
            {"id": "E2", "severity": "L2", "description": "船上观光游客身穿的彩色服饰严重欠饱和发暗。"}
        ],
        "note": "清澈港口水面错涂为发暗灰紫粉红污斑(错色 C-L3)，水域船体严重偏洋红紫光(偏色 D-L2)，游客服饰严重欠饱和(欠饱和 E2-L2)。"
    },

    # Sheet 18
    3769: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "夜间棒球场内野草坪原本鲜绿色的草地被严重错涂为偏暗冷青蓝紫色。"},
            {"id": "D", "severity": "L2", "description": "棒球场看台观众席与击球区全景严重偏冷青蓝紫调。"}
        ],
        "note": "棒球场内野草坪错涂为偏暗冷青蓝紫色(错色 C-L2)，看台与击球区严重偏冷青蓝紫(偏色 D-L2)。"
    },
    3770: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "牧场草坪及背景针叶林草木色泽欠饱和偏淡发灰，马匹毛发干瘪。"}
        ],
        "note": "牧场草坪与背景针叶林草木欠饱和发灰(欠饱和 E2-L1)。"
    },
    3772: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "金属盆中盛开的百合花橙红色花瓣色彩过度浓艳刺眼，高光处过饱和。"},
            {"id": "F", "severity": "L1", "description": "百合花瓣边缘与金属盆光影过渡生硬不自然。"}
        ],
        "note": "百合花橙红花瓣过度浓艳刺眼(过饱和 E1-L2)，花瓣与金属盆光影过渡生硬(自然度 F-L1)。"
    },
    3773: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "大型客车车厢内部透出的顶灯灯光偏暗橙黄且车顶略偏暗紫调。"},
            {"id": "E2", "severity": "L1", "description": "客车车身金属漆面与车轮部位欠饱和发暗。"}
        ],
        "note": "客车车厢内部灯光偏暗橙黄车顶偏紫(偏色 D-L1)，车身金属漆欠饱和发暗(欠饱和 E2-L1)。"
    },
    3774: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3775: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 19
    3776: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "展位栖架上猫头鹰羽毛斑纹及背景帐篷白绿帆布欠饱和泛淡发灰。"},
            {"id": "D", "severity": "L1", "description": "户外展位全景环境光略偏冷青暗灰。"}
        ],
        "note": "猫头鹰羽毛斑纹与帐篷帆布欠饱和发灰(欠饱和 E2-L1)，全景略偏冷青暗灰(偏色 D-L1)。"
    },
    3777: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "动物园长颈鹿背后原本鲜绿茂盛的草坡被严重脱色错涂为枯黄泛灰的土黄色。"},
            {"id": "E2", "severity": "L2", "description": "长颈鹿身体斑纹与背景草地严重欠饱和发暗。"},
            {"id": "D", "severity": "L1", "description": "背景树木与动物全景偏冷暗灰调。"}
        ],
        "note": "长颈鹿背后鲜绿草坡被脱色错涂为枯黄土色(错色 C-L3)，斑纹与草地严重欠饱和(欠饱和 E2-L2)，全景偏冷暗灰(偏色 D-L1)。"
    },
    3778: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "MP3透明包装盒右侧原本鲜绿带橙的挂绳手柄被严重脱色错涂为灰白色。"},
            {"id": "D", "severity": "L1", "description": "透明塑料包装壳与MP3机身略偏冷青紫调。"}
        ],
        "note": "MP3包装盒右侧鲜绿挂绳手柄脱色错涂为灰白(错色 C-L2)，塑料壳与机身略偏冷青紫(偏色 D-L1)。"
    },
    3779: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "桌面上卡通闹钟背景原本温暖柔和的米黄色墙壁被严重错涂为冰冷惨白的青灰色。"},
            {"id": "D", "severity": "L2", "description": "熊猫造型闹钟与桌面木质摆件全域严重偏冷青灰蓝调。"},
            {"id": "E2", "severity": "L1", "description": "熊猫闹钟底座色彩欠饱和发暗。"}
        ],
        "note": "米黄背景墙错涂为冰冷惨白青灰色(错色 C-L2)，熊猫闹钟与摆件全域偏冷青灰蓝(偏色 D-L2)，底座欠饱和发暗(欠饱和 E2-L1)。"
    },
    3781: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "道路上超宽特种工程作业车车身及黄色警示标牌色彩欠饱和偏淡。"},
            {"id": "D", "severity": "L1", "description": "道路沥青地面与天空背景略偏冷青暗灰。"}
        ],
        "note": "特种作业车黄色警示标牌欠饱和偏淡(欠饱和 E2-L1)，路面与天空偏冷青暗灰(偏色 D-L1)。"
    },
    3782: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "后厨厨师身穿的白色工作服与不锈钢操作台略微偏暗暖黄调。"},
            {"id": "E2", "severity": "L1", "description": "后厨墙面瓷砖与吊顶欠饱和微弱发暗。"}
        ],
        "note": "厨师白色工作服与不锈钢操作台略偏暗暖黄(偏色 D-L1)，后厨墙砖欠饱和微暗(欠饱和 E2-L1)。"
    },

    # Sheet 20
    3783: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3785: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "餐盘中切丝胡萝卜与金黄炸薯条色彩过度浓艳刺眼，荧光橙过亮。"},
            {"id": "D", "severity": "L1", "description": "蓝白格子桌布与红酒杯略偏冷青暗蓝调。"}
        ],
        "note": "切丝胡萝卜与炸薯条过度浓艳刺眼(过饱和 E1-L2)，桌布酒杯略偏冷青暗蓝(偏色 D-L1)。"
    },
    3786: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3787: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "人行道原本干净的浅灰色大理石地砖路面被大面积严重错涂为发霉般的荧光青绿色。"},
            {"id": "D", "severity": "L2", "description": "街道欧式建筑立面与立式广告牌周边全景严重偏冷青黄绿调。"},
            {"id": "F", "severity": "L2", "description": "人行道路面杂色斑块极度违和刺眼，严重破坏视觉自然度。"}
        ],
        "note": "人行道浅灰地砖被大面积错涂为发霉般荧光青绿色(错色 C-L3)，街道建筑全景严重偏冷青黄绿(偏色 D-L2)，路面杂色违和(自然度 F-L2)。"
    },
    3790: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3792: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L3", "description": "哥特式教堂背景火烧云天空红色过度浓艳刺眼，高光处严重过曝死白炸裂。"},
            {"id": "C", "severity": "L2", "description": "教堂石砌钟楼尖顶边缘受暴烈红光污染严重错色。"},
            {"id": "F", "severity": "L2", "description": "天空红色炸裂过曝，与古建筑过渡生硬极不自然。"}
        ],
        "note": "背景火烧云天空红色过度浓艳刺眼且高光死白(过饱和 E1-L3)，钟楼尖顶受红光污染严重错色(错色 C-L2)，过渡生硬极不自然(自然度 F-L2)。"
    }
}


def run_checks_and_apply():
    print("=" * 60)
    print("Checking BATCH_16_REVIEWS against quality rules...")
    print("=" * 60)
    
    assert len(BATCH_16_REVIEWS) == 120, f"Expected 120 reviews, got {len(BATCH_16_REVIEWS)}"
    
    pass_count = 0
    revise_count = 0
    
    for task_id, review in BATCH_16_REVIEWS.items():
        is_pass = review["pass"]
        defects = review["defects"]
        note = review["note"]
        
        if is_pass:
            pass_count += 1
            assert len(defects) == 0, f"Task #{task_id}: Pass task must have defects=[]"
            assert note == "审查通过", f"Task #{task_id}: Pass task must have note='审查通过'"
        else:
            revise_count += 1
            assert len(defects) > 0, f"Task #{task_id}: Revision task must have defects > 0"
            assert note != "审查通过", f"Task #{task_id}: Revision task cannot have note='审查通过'"
            
            # Check banned words
            for bw in BANNED_WORDS:
                assert bw not in note, f"Task #{task_id} note contains banned word '{bw}'"
                for d in defects:
                    assert bw not in d["description"], f"Task #{task_id} defect description contains banned word '{bw}'"
                    
            # Check defect structure
            for d in defects:
                d_id = d["id"]
                sev = d.get("severity")
                desc = d["description"]
                assert d_id in DEFECT_NAME_MAP, f"Task #{task_id} unknown defect id '{d_id}'"
                if d_id == "A":
                    assert sev == "", f"Task #{task_id} defect A must have severity ''"
                else:
                    assert sev in ["L1", "L2", "L3"], f"Task #{task_id} defect {d_id} invalid severity '{sev}'"
                assert len(desc) >= 8, f"Task #{task_id} defect description too short: {desc}"

    print(f"[OK] All 120 reviews passed local checks!")
    print(f"Pass tasks: {pass_count}")
    print(f"Revision tasks: {revise_count}")
    
    # Save grounding json
    grounding_data = {}
    for task_id, review in BATCH_16_REVIEWS.items():
        grounding_data[str(task_id)] = {
            "task_id": task_id,
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
