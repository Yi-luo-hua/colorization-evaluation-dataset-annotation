# -*- coding: utf-8 -*-
"""
Apply visual grounding reviews for Remaining Batch 18 (Tasks #3979 ~ #4154, total 120 tasks across 20 sheets).
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
GROUNDING_OUT_PATH = os.path.join(PROJECT_ROOT, "LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_18.json")

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

# 120 Reviews for Batch 18
BATCH_18_REVIEWS = {
    # Sheet 01
    3979: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "厨房左侧站立女子所穿的鲜艳宝蓝色毛衣被严重错涂为发暗灰黑褐色。"},
            {"id": "D", "severity": "L1", "description": "厨房木质橱柜与操作台面略偏暗暖灰褐调。"},
            {"id": "E2", "severity": "L2", "description": "女子毛衣与厨房内饰色彩严重欠饱和泛灰失色。"}
        ],
        "note": "厨房左侧女子鲜艳宝蓝毛衣被严重错涂为发暗灰黑褐色(错色 C-L3)，橱柜与台面略偏暗暖灰褐(偏色 D-L1)，毛衣色彩严重欠饱和(欠饱和 E2-L2)。"
    },
    3980: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3981: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3983: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "定制摩托车车轮与发动机周边炫彩霓虹氛围灯被错涂为暗沉黄光。"},
            {"id": "D", "severity": "L2", "description": "摩托车金属车架与展厅地面严重偏暗暖黄调。"},
            {"id": "E2", "severity": "L1", "description": "彩色氛围灯光活力欠饱和发暗。"}
        ],
        "note": "定制摩托车彩色霓虹氛围灯被错涂为暗沉黄光(错色 C-L2)，金属车架与地面偏暗暖黄(偏色 D-L2)，氛围灯光欠饱和(欠饱和 E2-L1)。"
    },
    3984: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3985: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "餐厅餐桌前交谈女士面部与胸前肤色严重偏冷紫褐发暗。"},
            {"id": "F", "severity": "L2", "description": "女士面部出现发黑斑驳杂色色斑，破坏面部质感自然度。"},
            {"id": "E2", "severity": "L1", "description": "女士服饰色彩欠饱和微弱发灰。"}
        ],
        "note": "餐桌前交谈女士面部与胸前肤色偏冷紫褐发暗(偏色 D-L2)，面部发黑斑驳破坏视觉自然度(自然度 F-L2)，服饰欠饱和(欠饱和 E2-L1)。"
    },

    # Sheet 02
    3986: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3990: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "水塘水面倒影与水草偏冷暗绿灰色调。"},
            {"id": "E2", "severity": "L1", "description": "涉禽身体羽毛欠饱和微弱发灰发暗。"},
            {"id": "F", "severity": "L1", "description": "水面光影过渡略显生硬发暗。"}
        ],
        "note": "水塘倒影与水草偏冷暗绿灰(偏色 D-L1)，涉禽羽毛欠饱和微弱发灰(欠饱和 E2-L1)，水面光影略生硬(自然度 F-L1)。"
    },
    3991: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "街角建筑明黄色防盗卷帘门被严重错涂为冷青灰白色。"},
            {"id": "C", "severity": "L2", "description": "人行道旁大红色消防栓被错涂为发暗深紫灰色。"},
            {"id": "D", "severity": "L2", "description": "建筑红砖外墙与街道地面严重偏冷暗紫灰调。"},
            {"id": "F", "severity": "L2", "description": "卷帘门与消防栓严重褪色错色导致街景视觉自然度明显下降。"}
        ],
        "note": "建筑明黄色卷帘门错涂为冷青灰白(错色 C-L3)，红色消防栓错涂为发暗深紫灰(错色 C-L2)，红砖外墙严重偏冷暗紫灰(偏色 D-L2)，街景视觉自然度下降(自然度 F-L2)。"
    },
    3992: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3994: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    3997: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "特写家猫耳廓内侧肉粉色与头顶边缘毛发过度浓艳偏火红橙色。"},
            {"id": "D", "severity": "L1", "description": "猫咪面部白色毛发略带暗暖黄偏色。"},
            {"id": "F", "severity": "L2", "description": "猫咪耳廓过度浓艳失真产生灼烧感。"}
        ],
        "note": "特写家猫耳廓内侧与头顶毛发过度浓艳偏火红橙色(过饱和 E1-L2)，面部白毛微偏暗暖黄(偏色 D-L1)，耳廓过度浓艳灼烧感破坏自然度(自然度 F-L2)。"
    },

    # Sheet 03
    3999: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4001: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "泥土沙地球场被大面积荒唐错涂为发暗的橄榄淡草绿色。"},
            {"id": "D", "severity": "L2", "description": "球场看台水泥台阶与背景围网严重偏暗冷青紫调。"},
            {"id": "E2", "severity": "L1", "description": "球员球衣色彩欠饱和略显发灰。"}
        ],
        "note": "泥土沙地球场大面积错涂为橄榄淡草绿(错色 C-L3)，球场水泥看台偏暗冷青紫(偏色 D-L2)，球衣欠饱和发灰(欠饱和 E2-L1)。"
    },
    4002: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4004: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4005: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "流动图书馆厢式货车侧面醒目的暖橙黄色车厢被错涂为发暗的橄榄黄绿色。"},
            {"id": "D", "severity": "L1", "description": "货车驾驶室白色漆面略偏暗暖灰。"},
            {"id": "E2", "severity": "L1", "description": "货车侧面车体涂装活力欠饱和发暗。"}
        ],
        "note": "流动图书馆货车侧面暖橙车厢错涂为发暗橄榄黄绿(错色 C-L2)，驾驶室略偏暗暖灰(偏色 D-L1)，车体涂装欠饱和(欠饱和 E2-L1)。"
    },
    4008: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 04
    4010: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "火车站拱形钢结构穹顶与月台地面偏冷暗青灰调。"},
            {"id": "E2", "severity": "L1", "description": "停靠的墨绿色旅客列车漆面欠饱和微弱发暗。"}
        ],
        "note": "火车站拱形穹顶与月台偏冷暗青灰(偏色 D-L1)，墨绿列车漆面欠饱和微弱发暗(欠饱和 E2-L1)。"
    },
    4012: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "电脑写字台桌面与粉刷墙壁全景严重偏暖橙黄杂色调。"},
            {"id": "E1", "severity": "L2", "description": "电脑桌木纹与白墙暖光过度浓艳发闷。"},
            {"id": "F", "severity": "L2", "description": "室内光线失真泛黄严重影响视觉自然度。"}
        ],
        "note": "电脑写字台与粉刷墙壁严重偏暖橙黄(偏色 D-L2)，桌面木纹与白墙过度浓艳(过饱和 E1-L2)，室内光线失真影响自然度(自然度 F-L2)。"
    },
    4013: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4016: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "怪兽毛绒玩偶身下浅蓝白色床单被大面积错涂为脏黄褐色。"},
            {"id": "E1", "severity": "L2", "description": "紫色怪兽玩偶身上长毛色泽过度浓艳呈刺眼洋红色。"},
            {"id": "D", "severity": "L2", "description": "卧室床铺及背景墙面严重偏暗暖黄调。"}
        ],
        "note": "怪兽毛绒玩偶身下浅蓝白床单错涂为脏黄褐(错色 C-L2)，玩偶长毛过度浓艳刺眼(过饱和 E1-L2)，床铺与墙面偏暗暖黄(偏色 D-L2)。"
    },
    4019: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4021: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "母亲所穿的鲜红色针织开衫被严重错涂为发暗紫褐色。"},
            {"id": "D", "severity": "L2", "description": "母女二人面部与手臂肤色严重偏冷紫褐发暗。"},
            {"id": "E2", "severity": "L2", "description": "红色针织开衫严重欠饱和褪色发闷。"}
        ],
        "note": "母亲鲜红针织开衫被错涂为发暗紫褐色(错色 C-L3)，母女面部肤色偏冷紫褐发暗(偏色 D-L2)，开衫严重欠饱和褪色(欠饱和 E2-L2)。"
    },

    # Sheet 05
    4022: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "深红咖啡杯中拿铁咖啡浅棕色油脂拉花被错涂为发暗黄绿色。"},
            {"id": "D", "severity": "L1", "description": "白瓷托盘与咖啡杯边缘微带暗暖灰调。"}
        ],
        "note": "拿铁咖啡浅棕油脂拉花错涂为发暗黄绿(错色 C-L2)，托盘与咖啡杯微带暗暖灰(偏色 D-L1)。"
    },
    4023: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "电脑显示器外框与键盘按键略偏暗冷青灰调。"},
            {"id": "E2", "severity": "L1", "description": "白猫耳廓内侧浅粉色与电脑桌欠饱和微弱发暗。"}
        ],
        "note": "电脑显示器与键盘略偏暗冷青灰(偏色 D-L1)，白猫耳廓与电脑桌欠饱和微暗(欠饱和 E2-L1)。"
    },
    4024: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "铁道两侧原本郁郁葱葱的翠绿树林被大面积错涂为枯黄秋叶色。"},
            {"id": "D", "severity": "L2", "description": "铁轨路基碎石与路面偏暗暖黄褐色调。"},
            {"id": "E1", "severity": "L1", "description": "树林枯黄色调局部略显浓艳失真。"}
        ],
        "note": "铁道两侧翠绿树林大面积错涂为枯黄秋叶色(错色 C-L2)，铁轨碎石偏暗暖黄褐(偏色 D-L2)，树林局部色调偏浓(过饱和 E1-L1)。"
    },
    4025: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4026: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "沙拉切片水萝卜鲜红表皮过度浓艳刺眼呈荧光洋红色。"},
            {"id": "F", "severity": "L2", "description": "水萝卜表皮过度荧光刺眼破坏生鲜食材真实自然度。"},
            {"id": "D", "severity": "L1", "description": "瓷碗内底部生菜与沙拉酱略偏暗暖灰。"}
        ],
        "note": "沙拉水萝卜表皮过度浓艳刺眼呈荧光洋红(过饱和 E1-L2)，破坏食材自然度(自然度 F-L2)，生菜与酱汁略偏暗暖灰(偏色 D-L1)。"
    },
    4027: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "铁丝围栏与背景树林严重偏冷青紫暗调。"},
            {"id": "E1", "severity": "L2", "description": "前景草坪过度荧光浓艳发亮。"},
            {"id": "F", "severity": "L2", "description": "女士手臂及服饰出现斑驳杂色，视觉自然度明显受损。"}
        ],
        "note": "铁丝围栏与背景树林偏冷青紫(偏色 D-L2)，前景草坪过度荧光浓艳(过饱和 E1-L2)，手臂及服饰杂色斑驳(自然度 F-L2)。"
    },

    # Sheet 06
    4028: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "浴室洗手台后方原本湛蓝亮丽的瓷砖墙面被彻底剥夺错涂为冷青灰白色。"},
            {"id": "C", "severity": "L2", "description": "台面红色漱口塑料杯错涂为发暗黄褐色。"},
            {"id": "E2", "severity": "L2", "description": "瓷砖墙面与漱口杯色彩严重欠饱和发灰脱色。"},
            {"id": "D", "severity": "L2", "description": "白瓷水槽与金属龙头偏冷青灰暗调。"}
        ],
        "note": "浴室湛蓝瓷砖墙面彻底错涂为冷青灰白(错色 C-L3)，红色漱口杯错涂为黄褐(错色 C-L2)，墙面严重欠饱和脱色(欠饱和 E2-L2)，洗手台偏冷青灰(偏色 D-L2)。"
    },
    4031: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4032: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "男青年身后暖黄色百叶窗帘布褶皱处被错涂为大面积发暗冷青灰斑。"},
            {"id": "D", "severity": "L1", "description": "室内米白墙面与男青年面部肤色微偏冷青暗灰调。"},
            {"id": "E2", "severity": "L1", "description": "百叶窗帘整体色彩欠饱和发暗。"}
        ],
        "note": "暖黄百叶窗帘褶皱处错涂为发暗冷青灰斑(错色 C-L2)，室内白墙微偏冷青暗灰(偏色 D-L1)，窗帘欠饱和发暗(欠饱和 E2-L1)。"
    },
    4033: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4034: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "室内原本明亮温暖的黄色背景墙面被彻底剥夺错涂为冷青灰白色。"},
            {"id": "D", "severity": "L2", "description": "画面人物面部与手臂肤色严重偏冷紫褐发黑。"},
            {"id": "F", "severity": "L2", "description": "室内光线由暖变冷严重破坏画面原有的温馨视觉自然度。"}
        ],
        "note": "室内明亮黄色背景墙被彻底错涂为冷青灰白(错色 C-L3)，人物面部肤色偏冷紫褐发黑(偏色 D-L2)，室内暖光破坏自然度(自然度 F-L2)。"
    },
    4035: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "室内木质楼梯踏步板与踢脚线严重偏暗红褐调。"},
            {"id": "E2", "severity": "L1", "description": "楼梯旁浅绿粉刷墙面欠饱和微弱发灰。"}
        ],
        "note": "木质楼梯踏步板严重偏暗红褐(偏色 D-L2)，浅绿粉刷墙面欠饱和发灰(欠饱和 E2-L1)。"
    },

    # Sheet 07
    4036: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "宅急便货车车身下部青绿与亮黄条纹被错涂为发暗灰白色。"},
            {"id": "E2", "severity": "L2", "description": "货车涂装条纹与车标严重欠饱和褪色。"},
            {"id": "D", "severity": "L1", "description": "货车车身与道路沥青略偏冷暗青灰调。"}
        ],
        "note": "宅急便货车青绿亮黄条纹错涂为发暗灰白(错色 C-L2)，涂装严重欠饱和褪色(欠饱和 E2-L2)，车身与道路略偏冷暗青灰(偏色 D-L1)。"
    },
    4037: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "卫生间明亮温暖的鹅黄色瓷砖墙面被彻底剥夺错涂为冰冷青灰白色。"},
            {"id": "D", "severity": "L2", "description": "马桶安全金属扶手与地砖严重偏冷暗蓝调。"},
            {"id": "E2", "severity": "L2", "description": "瓷砖墙壁暖色彻底丢失严重欠饱和。"}
        ],
        "note": "卫生间鹅黄色瓷砖墙面彻底错涂为冰冷青灰白(错色 C-L3)，安全扶手与地砖偏冷暗蓝(偏色 D-L2)，墙面暖色欠饱和丢失(欠饱和 E2-L2)。"
    },
    4038: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "机场行李大厅密集堆叠的鲜红与亮蓝拉杆箱被错涂为发暗紫灰褐色。"},
            {"id": "E2", "severity": "L2", "description": "密集旅行行李箱色彩活力严重欠饱和褪色发暗。"},
            {"id": "D", "severity": "L1", "description": "大厅地面与行李输送架略偏暗灰调。"}
        ],
        "note": "机场大厅鲜红亮蓝拉杆箱错涂为发暗紫灰褐(错色 C-L2)，旅行箱色彩严重欠饱和褪色(欠饱和 E2-L2)，大厅地面略偏暗灰(偏色 D-L1)。"
    },
    4040: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "水果盘中香蕉苹果甜瓜全景严重偏冷紫褐发黑。"},
            {"id": "F", "severity": "L2", "description": "香蕉表皮与果肉切面出现大块蓝紫杂色暗斑，破坏水果新鲜自然度。"},
            {"id": "E2", "severity": "L1", "description": "甜瓜与苹果色彩欠饱和微弱发暗。"}
        ],
        "note": "果盘香蕉苹果甜瓜偏冷紫褐发黑(偏色 D-L2)，香蕉表皮蓝紫暗斑破坏自然度(自然度 F-L2)，甜瓜与苹果欠饱和(欠饱和 E2-L1)。"
    },
    4041: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4043: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 08
    4044: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "红发男子原本明丽的荧光洋红粉色T恤被彻底错涂为发暗泥灰白色。"},
            {"id": "E2", "severity": "L2", "description": "男子运动T恤色彩完全丧失严重欠饱和。"},
            {"id": "D", "severity": "L1", "description": "男子面部与红发略偏暗灰红调。"}
        ],
        "note": "红发男子明丽荧光洋红T恤彻底错涂为发暗泥灰白(错色 C-L3)，T恤严重欠饱和(欠饱和 E2-L2)，面部略偏暗灰红(偏色 D-L1)。"
    },
    4045: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L1", "description": "汽车座椅上蜷缩幼猫的皮毛欠饱和微弱发灰。"},
            {"id": "D", "severity": "L1", "description": "汽车皮质座椅与安全带略偏冷暗青灰调。"}
        ],
        "note": "幼猫皮毛欠饱和微弱发灰(欠饱和 E2-L1)，汽车皮质座椅略偏冷暗青灰(偏色 D-L1)。"
    },
    4046: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "消防救援皮卡车醒目的鲜红车漆涂装严重褪色错涂为发暗深褐红色。"},
            {"id": "D", "severity": "L2", "description": "背景草坪与路基严重偏暗黄褐色调。"},
            {"id": "E2", "severity": "L1", "description": "消防车红色警示涂装欠饱和暗淡。"}
        ],
        "note": "消防救援皮卡车鲜红涂装错涂为发暗深褐红(错色 C-L2)，背景草坪偏暗黄褐(偏色 D-L2)，车漆涂装欠饱和暗淡(欠饱和 E2-L1)。"
    },
    4047: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "体感游戏青年所穿的鲜艳正红色运动T恤被严重错涂为发暗灰褐杂色。"},
            {"id": "D", "severity": "L2", "description": "客厅电视柜与背景墙面严重偏冷青暗灰调。"},
            {"id": "E2", "severity": "L2", "description": "青年红色T恤严重欠饱和发暗脱色。"}
        ],
        "note": "体感游戏青年鲜艳正红T恤错涂为发暗灰褐杂色(错色 C-L3)，客厅背景偏冷青暗灰(偏色 D-L2)，T恤严重欠饱和脱色(欠饱和 E2-L2)。"
    },
    4048: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "淋浴房米黄色瓷砖墙面被错涂为大面积冰冷灰蓝白色。"},
            {"id": "D", "severity": "L2", "description": "淋浴玻璃隔断与地面严重偏冷青蓝调。"},
            {"id": "E2", "severity": "L1", "description": "米黄瓷砖原有的暖色调欠饱和丧失。"}
        ],
        "note": "淋浴房米黄瓷砖墙面错涂为冰冷灰蓝白(错色 C-L2)，玻璃隔断与地面偏冷青蓝(偏色 D-L2)，瓷砖暖色欠饱和(欠饱和 E2-L1)。"
    },
    4053: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 09
    4054: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "汽车内顶棚与男士服饰全景严重偏冷蓝紫暗调。"},
            {"id": "E1", "severity": "L2", "description": "车窗外透入的冷蓝光线过度浓艳溢出。"},
            {"id": "F", "severity": "L2", "description": "男士面部肤色受强冷蓝光侵染发黑，严重破坏肖像自然度。"}
        ],
        "note": "车内顶棚与男士服饰偏冷蓝紫暗调(偏色 D-L2)，冷蓝光线过度浓艳(过饱和 E1-L2)，面部肤色受冷光侵染发黑破坏自然度(自然度 F-L2)。"
    },
    4055: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4057: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "浅水沼泽绿茵草坪被错涂为大面积发暗橄榄黄绿色。"},
            {"id": "D", "severity": "L1", "description": "沙丘鹤羽毛与水面微偏暗灰青调。"},
            {"id": "E2", "severity": "L1", "description": "沙丘鹤头顶鲜红额冠欠饱和微弱发暗。"}
        ],
        "note": "绿茵草坪错涂为发暗橄榄黄绿(错色 C-L2)，水面微偏暗灰青(偏色 D-L1)，沙丘鹤红色额冠欠饱和微暗(欠饱和 E2-L1)。"
    },
    4059: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4060: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "飞盘公园草地被错涂为发暗橄榄黄绿色。"},
            {"id": "D", "severity": "L1", "description": "远景树木与天空略偏暗冷灰调。"},
            {"id": "E2", "severity": "L1", "description": "运动玩家服饰与飞盘色彩欠饱和发暗。"}
        ],
        "note": "飞盘公园草地错涂为发暗橄榄黄绿(错色 C-L2)，远景树木略偏暗冷灰(偏色 D-L1)，玩家服饰欠饱和(欠饱和 E2-L1)。"
    },
    4061: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "科技展厅米白色暖光展墙被严重错涂为大面积深冷蓝紫色。"},
            {"id": "D", "severity": "L2", "description": "老式电脑展台与展示柜台严重偏冷青蓝调。"},
            {"id": "F", "severity": "L2", "description": "展厅墙面深冷蓝紫光染严重破坏室内陈列真实视觉自然度。"}
        ],
        "note": "科技展厅米白展墙严重错涂为深冷蓝紫色(错色 C-L3)，电脑展台严重偏冷青蓝(偏色 D-L2)，墙面冷光污染破坏自然度(自然度 F-L2)。"
    },

    # Sheet 10
    4063: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4064: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "炒面面条酱汁与胡萝卜丝色泽过度浓艳刺眼偏荧光红橙。"},
            {"id": "D", "severity": "L1", "description": "西兰花与餐盒边缘略偏暗冷青调。"},
            {"id": "F", "severity": "L1", "description": "炒面酱汁过度鲜艳略显油腻失真。"}
        ],
        "note": "炒面面条酱汁与胡萝卜丝过度浓艳偏荧光红橙(过饱和 E1-L2)，西兰花略偏暗冷青(偏色 D-L1)，酱汁略油腻失真(自然度 F-L1)。"
    },
    4065: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4066: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "猛禽老鹰头部与胸腹部棕黄斑纹羽毛被错涂为暗沉灰褐色。"},
            {"id": "E2", "severity": "L2", "description": "老鹰羽毛与周边树叶色彩严重欠饱和发灰脱色。"},
            {"id": "D", "severity": "L1", "description": "树枝与背景天空略偏冷暗青灰调。"}
        ],
        "note": "老鹰头部胸腹棕黄羽毛错涂为暗沉灰褐(错色 C-L2)，羽毛与树叶严重欠饱和发灰(欠饱和 E2-L2)，背景略偏冷暗青灰(偏色 D-L1)。"
    },
    4067: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4068: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 11
    4070: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4071: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4072: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4073: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "庭院建筑水泥外墙与地面回廊严重偏冷紫暗调。"},
            {"id": "C", "severity": "L2", "description": "庭院中央绿化草坪错涂为发暗青蓝杂色。"},
            {"id": "E2", "severity": "L1", "description": "庭院绿植与建筑装饰欠饱和发灰发暗。"}
        ],
        "note": "庭院建筑外墙与地面严重偏冷紫暗调(偏色 D-L2)，绿化草坪错涂为发暗青蓝杂色(错色 C-L2)，绿植欠饱和发灰(欠饱和 E2-L1)。"
    },
    4074: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4076: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 12
    4077: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L2", "description": "冲浪者所穿潜水服与冲浪板色彩严重欠饱和发黑失色。"},
            {"id": "D", "severity": "L1", "description": "沙滩与海面浪花略偏暗冷灰青调。"}
        ],
        "note": "冲浪者潜水服与冲浪板严重欠饱和发黑失色(欠饱和 E2-L2)，沙滩海面略偏暗冷灰青(偏色 D-L1)。"
    },
    4078: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "卫生间橙色背景墙与实木镜框略偏暗红褐调。"},
            {"id": "E1", "severity": "L1", "description": "橙色背景墙局部饱和度略显浓重发闷。"}
        ],
        "note": "卫生间橙色背景墙与木镜框略偏暗红褐(偏色 D-L1)，背景墙局部偏浓重发闷(过饱和 E1-L1)。"
    },
    4079: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4084: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "艺术展厅原本金黄色暖光墙壁被严重剥夺错涂为冷灰白色。"},
            {"id": "D", "severity": "L2", "description": "石膏天花板与展示台面严重偏冷青灰调。"},
            {"id": "E2", "severity": "L2", "description": "金黄墙壁原本丰满的暖光严重欠饱和剥落。"}
        ],
        "note": "艺术展厅金黄暖光墙壁错涂为冷灰白(错色 C-L3)，石膏天花板偏冷青灰(偏色 D-L2)，金黄暖光严重欠饱和剥落(欠饱和 E2-L2)。"
    },
    4085: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4087: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "欧式复古拱廊暖黄色墙面与拱券被彻底剥夺错涂为冰冷灰白色。"},
            {"id": "D", "severity": "L2", "description": "拱廊走道排椅与地面严重偏冷暗蓝调。"},
            {"id": "E2", "severity": "L2", "description": "暖黄色古典拱廊氛围严重欠饱和变为冷淡空洞。"}
        ],
        "note": "欧式拱廊暖黄色墙面与拱券错涂为冰冷灰白(错色 C-L3)，走道排椅偏冷暗蓝(偏色 D-L2)，复古暖黄氛围严重欠饱和(欠饱和 E2-L2)。"
    },

    # Sheet 13
    4088: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4090: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "沙发上两只猫咪身下鲜艳深红色坐垫布被严重错涂为发暗黄褐色。"},
            {"id": "D", "severity": "L2", "description": "布艺沙发靠背与木地板偏暗黄褐调。"},
            {"id": "E2", "severity": "L2", "description": "红色坐垫布鲜红色彩严重欠饱和丧失。"}
        ],
        "note": "猫咪身下鲜艳深红坐垫布错涂为发暗黄褐色(错色 C-L3)，布艺沙发偏暗黄褐(偏色 D-L2)，坐垫红色严重欠饱和丧失(欠饱和 E2-L2)。"
    },
    4093: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "冰箱门架上塑料牛奶桶瓶盖由天蓝色错涂为鲜绿色。"},
            {"id": "D", "severity": "L1", "description": "冷藏室内壁与调料瓶略偏冷暗青灰调。"},
            {"id": "E2", "severity": "L1", "description": "冷藏室食品包装色彩欠饱和微弱发暗。"}
        ],
        "note": "冰箱门架牛奶桶天蓝瓶盖错涂为鲜绿色(错色 C-L2)，冷藏室内壁略偏冷暗青灰(偏色 D-L1)，食品包装欠饱和微暗(欠饱和 E2-L1)。"
    },
    4094: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "大象表演场遮阳棚与沙土地面偏冷暗紫灰调。"},
            {"id": "F", "severity": "L2", "description": "大象头部与节庆饰帽边缘出现不自然蓝紫杂色色斑，破坏动物自然度。"},
            {"id": "E2", "severity": "L1", "description": "大象节庆饰帽彩色流苏欠饱和发暗。"}
        ],
        "note": "大象表演场遮阳棚偏冷暗紫灰(偏色 D-L1)，大象头部边缘蓝紫杂斑破坏自然度(自然度 F-L2)，节庆饰帽欠饱和发暗(欠饱和 E2-L1)。"
    },
    4095: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4096: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "网球少年红白相间运动T恤红色条纹被彻底错涂为发暗橄榄黄绿色。"},
            {"id": "D", "severity": "L1", "description": "网球场地塑胶地面略偏暗灰青调。"},
            {"id": "E2", "severity": "L1", "description": "少年运动T恤与网球拍欠饱和微弱发暗。"}
        ],
        "note": "网球少年运动T恤红色条纹彻底错涂为发暗橄榄黄绿(错色 C-L3)，塑胶地面略偏暗灰青(偏色 D-L1)，T恤与球拍欠饱和(欠饱和 E2-L1)。"
    },

    # Sheet 14
    4097: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "小小棒球投手原本浅天蓝色的球衣与球帽被错涂为发暗紫青色。"},
            {"id": "D", "severity": "L1", "description": "棒球场红土与围网微偏暗冷青调。"},
            {"id": "F", "severity": "L1", "description": "投手球衣边缘色泽过渡生硬。"}
        ],
        "note": "棒球投手浅天蓝球衣与球帽错涂为发暗紫青色(错色 C-L2)，球场红土微偏暗冷青(偏色 D-L1)，球衣过渡略显生硬(自然度 F-L1)。"
    },
    4098: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "盛放火龙果与甜橙的翠绿色塑料周转筐被错涂为发暗墨绿灰黑色。"},
            {"id": "D", "severity": "L2", "description": "水果陈列木货架与店铺地面严重偏暗红褐调。"},
            {"id": "E1", "severity": "L1", "description": "火龙果表皮玫红色局部略显浓艳过火。"}
        ],
        "note": "翠绿塑料周转筐错涂为发暗墨绿灰黑(错色 C-L2)，水果木货架严重偏暗红褐(偏色 D-L2)，火龙果表皮局部过浓(过饱和 E1-L1)。"
    },
    4099: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "自拍女孩棕红发色与面部肤色严重偏冷紫褐发暗。"},
            {"id": "E2", "severity": "L1", "description": "女孩所穿橙色夹克与打底衫欠饱和泛灰发暗。"},
            {"id": "F", "severity": "L1", "description": "女孩面部光影发暗破坏肖像自然度。"}
        ],
        "note": "自拍女孩面部肤色偏冷紫褐发暗(偏色 D-L2)，橙色夹克欠饱和泛灰(欠饱和 E2-L1)，面部光影发暗破坏自然度(自然度 F-L1)。"
    },
    4100: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "山坡丘陵远景树林枯树枝被大面积错涂为诡异刺眼的暗红粉紫色。"},
            {"id": "D", "severity": "L2", "description": "整个山地缓坡与灌木丛严重偏暗红紫杂色调。"},
            {"id": "F", "severity": "L2", "description": "树林大面积诡异粉紫杂色严重违背自然地貌常识。"}
        ],
        "note": "丘陵树林枯树枝错涂为诡异暗红粉紫色(错色 C-L2)，山地缓坡偏暗红紫杂色(偏色 D-L2)，粉紫树林违背地貌常识破坏自然度(自然度 F-L2)。"
    },
    4104: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4105: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 15
    4106: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "卫生间深红棕色实木百叶门被错涂为发暗灰褐色。"},
            {"id": "D", "severity": "L2", "description": "卫生间墙面瓷砖与洗手台面严重偏冷青暗灰调。"},
            {"id": "E2", "severity": "L1", "description": "实木百叶门原本温润红木色泽欠饱和褪色。"}
        ],
        "note": "卫生间深红棕实木百叶门错涂为发暗灰褐色(错色 C-L2)，墙面瓷砖严重偏冷青暗灰(偏色 D-L2)，木门色泽欠饱和褪色(欠饱和 E2-L1)。"
    },
    4108: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "机场停机坪水泥地面与地勤行李牵引车全景严重偏冷紫褐发暗。"},
            {"id": "E2", "severity": "L1", "description": "地勤行李牵引车黄色警示涂装欠饱和发暗。"},
            {"id": "F", "severity": "L1", "description": "停机坪地面出现轻微冷青杂色斑块。"}
        ],
        "note": "机场停机坪与行李牵引车偏冷紫褐发暗(偏色 D-L2)，牵引车黄色涂装欠饱和(欠饱和 E2-L1)，停机坪轻微杂色斑块(自然度 F-L1)。"
    },
    4109: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "货架左侧小玩具熊由暖橙黄色被彻底错涂为俗艳刺眼的荧光亮粉红色。"},
            {"id": "E1", "severity": "L2", "description": "紫色毛绒熊毛绒色泽过度浓艳刺眼。"},
            {"id": "D", "severity": "L1", "description": "玩具展架背景略偏暗暖黄调。"}
        ],
        "note": "左侧小玩具熊暖橙黄彻底错涂为荧光亮粉红(错色 C-L3)，紫色毛绒熊过度浓艳刺眼(过饱和 E1-L2)，玩具展架略偏暗暖黄(偏色 D-L1)。"
    },
    4110: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "全日空（ANA）客机机身侧面标志性的深蓝色腰线涂装被彻底错涂为深红褐色。"},
            {"id": "D", "severity": "L1", "description": "机场跑道沥青与机身白色蒙皮微偏暗暖黄灰。"},
            {"id": "F", "severity": "L2", "description": "航空公司经典深蓝涂装被篡改严重破坏客机辨识度与自然度。"}
        ],
        "note": "全日空客机深蓝条纹涂装彻底错涂为深红褐色(错色 C-L3)，跑道微偏暗暖黄灰(偏色 D-L1)，航空标志性涂装被篡改破坏自然度(自然度 F-L2)。"
    },
    4111: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "卧室原本温暖柔和的暖金色丝绸幔帐被错涂为斑驳刺眼的荧光黄绿与洋红紫杂色。"},
            {"id": "D", "severity": "L2", "description": "双人床床头靠背与木质地板严重偏冷青紫杂色调。"},
            {"id": "E1", "severity": "L2", "description": "幔帐荧光杂色局部过度浓艳刺目。"},
            {"id": "F", "severity": "L3", "description": "幔帐大面积发生严重伪色溃散崩溃，视觉自然度极度恶化。"}
        ],
        "note": "暖金色丝绸幔帐错涂为荧光黄绿与洋红紫杂色(错色 C-L3)，床头与地板偏冷青紫(偏色 D-L2)，幔帐荧光杂色过浓(过饱和 E1-L2)，伪色溃散破坏自然度(自然度 F-L3)。"
    },
    4112: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "夜景露天停车场水泥地面与半挂车底盘严重偏冷紫褐发黑。"},
            {"id": "E2", "severity": "L1", "description": "红色卡车车头金属漆光泽欠饱和微弱发暗。"}
        ],
        "note": "夜景露天停车场与半挂车底盘偏冷紫褐发黑(偏色 D-L2)，红色卡车车头金属漆欠饱和微暗(欠饱和 E2-L1)。"
    },

    # Sheet 16
    4113: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "奶牛身体棕黄色斑块毛色过度浓艳刺眼呈亮橙黄色。"},
            {"id": "D", "severity": "L2", "description": "乡村泥土路面与背景树林严重偏暖黄绿杂色调。"},
            {"id": "F", "severity": "L1", "description": "奶牛棕黄毛斑光影微显发硬失真。"}
        ],
        "note": "奶牛身体棕黄斑块过度浓艳偏亮橙黄(过饱和 E1-L2)，乡村泥土路偏暖黄绿杂色(偏色 D-L2)，毛斑光影微失真(自然度 F-L1)。"
    },
    4114: {
        "pass": False,
        "defects": [
            {"id": "E2", "severity": "L2", "description": "沿街建筑红砖外墙严重欠饱和发暗呈灰褐色。"},
            {"id": "C", "severity": "L2", "description": "建筑首层绿色木质窗框错涂为发暗橄榄灰绿色。"},
            {"id": "D", "severity": "L1", "description": "人行道石板路面略偏冷暗青灰调。"}
        ],
        "note": "沿街建筑红砖外墙严重欠饱和呈灰褐(欠饱和 E2-L2)，绿色木窗框错涂为发暗橄榄灰绿(错色 C-L2)，石板路略偏冷暗青灰(偏色 D-L1)。"
    },
    4115: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "夜景出租车前挡风玻璃与沥青地面严重偏冷蓝紫杂色调。"},
            {"id": "F", "severity": "L2", "description": "出租车黄色车顶灯与车身反光杂斑斑驳，破坏夜景视觉自然度。"},
            {"id": "E2", "severity": "L1", "description": "街景建筑灯光色彩欠饱和发暗。"}
        ],
        "note": "出租车挡风玻璃与地面偏冷蓝紫杂色(偏色 D-L2)，车顶灯反光杂斑破坏自然度(自然度 F-L2)，街景灯光欠饱和发暗(欠饱和 E2-L1)。"
    },
    4116: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4119: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4120: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "木屋起居室石砌壁炉严重偏冷青暗灰调。"},
            {"id": "E1", "severity": "L1", "description": "木屋原木墙壁木纹局部过浓发闷。"},
            {"id": "F", "severity": "L1", "description": "石砌壁炉冷灰感与原木暖调产生生硬割裂。"}
        ],
        "note": "木屋起居室石砌壁炉严重偏冷青暗灰(偏色 D-L2)，原木墙壁局部过浓发闷(过饱和 E1-L1)，壁炉冷调与原木割裂(自然度 F-L1)。"
    },

    # Sheet 17
    4121: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "等待通行的红色家用轿车车尾鲜红金属漆被错涂为发暗灰红色。"},
            {"id": "E2", "severity": "L1", "description": "红色轿车金属车漆与刹车尾灯欠饱和微弱发暗。"}
        ],
        "note": "红色家用轿车车尾鲜红车漆错涂为发暗灰红(错色 C-L2)，车漆与尾灯欠饱和发暗(欠饱和 E2-L1)。"
    },
    4122: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4124: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "室内实木地板与背景墙体略偏暗暖灰褐色调。"},
            {"id": "E2", "severity": "L1", "description": "地板上毛毯红色条纹与趴卧幼犬毛色欠饱和微弱发暗。"}
        ],
        "note": "室内实木地板与背景略偏暗暖灰褐(偏色 D-L1)，毛毯红条纹与幼犬毛色欠饱和发暗(欠饱和 E2-L1)。"
    },
    4126: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "青年刺猬头发型与颈部肤色略偏暗红褐调。"},
            {"id": "E2", "severity": "L1", "description": "青年身后傍晚树林与天空欠饱和微弱发暗。"}
        ],
        "note": "青年刺猬头发型与颈部肤色略偏暗红褐(偏色 D-L1)，傍晚树林欠饱和发暗(欠饱和 E2-L1)。"
    },
    4127: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "保龄球馆原本明亮温暖的黄色抛光木质球道被彻底剥夺错涂为冰冷青灰白色。"},
            {"id": "D", "severity": "L2", "description": "保龄球馆天花板吊顶与记分屏支架严重偏冷蓝紫暗调。"},
            {"id": "E2", "severity": "L2", "description": "暖黄色抛光木质球道暖光完全丧失严重欠饱和。"}
        ],
        "note": "保龄球馆黄色抛光木质球道错涂为冰冷青灰白(错色 C-L3)，吊顶与支架偏冷蓝紫暗调(偏色 D-L2)，木球道暖光严重欠饱和(欠饱和 E2-L2)。"
    },
    4129: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 18
    4130: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4131: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "比萨饼切片金黄焦香饼皮边缘与番茄酱汁过度浓艳刺眼偏荧光红橙色。"},
            {"id": "D", "severity": "L1", "description": "餐盘白瓷与垫纸微偏暗暖黄调。"},
            {"id": "F", "severity": "L1", "description": "比萨饼番茄酱汁过度浓艳略显生硬失真。"}
        ],
        "note": "比萨饼切片焦香饼皮与番茄酱汁过度浓艳偏荧光红橙(过饱和 E1-L2)，餐盘微偏暗暖黄(偏色 D-L1)，番茄酱汁生硬失真(自然度 F-L1)。"
    },
    4132: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4134: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "刚出炉热比萨饼金黄芝士与烘烤面饼被大面积荒唐错涂为发暗青蓝紫杂色。"},
            {"id": "D", "severity": "L2", "description": "盛放比萨饼的金属托盘与餐桌严重偏暗冷青紫调。"},
            {"id": "F", "severity": "L3", "description": "食物表面大面积青蓝紫伪色带来强烈变质感与毒性视觉感，极度破坏自然度。"}
        ],
        "note": "刚出炉比萨饼芝士与面饼错涂为发暗青蓝紫杂色(错色 C-L3)，金属托盘偏暗冷青紫(偏色 D-L2)，食物严重伪色变质感破坏自然度(自然度 F-L3)。"
    },
    4135: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "窗台左侧明亮蜜黄色实木包边墙板被错涂为发暗灰褐色。"},
            {"id": "D", "severity": "L1", "description": "窗框与窗外采光微偏暗冷青灰调。"},
            {"id": "E2", "severity": "L1", "description": "原木包边墙板原本温暖色泽欠饱和暗淡。"}
        ],
        "note": "窗台蜜黄色实木包边墙板错涂为发暗灰褐色(错色 C-L2)，窗框微偏暗冷青灰(偏色 D-L1)，原木暖色欠饱和暗淡(欠饱和 E2-L1)。"
    },
    4136: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "英国铁路内燃机车车头醒目的明黄警示防撞面被彻底错涂为发暗肉粉淡白色。"},
            {"id": "C", "severity": "L2", "description": "机车车身原本经典的墨绿车体涂装被错涂为冷青湖蓝灰色。"},
            {"id": "D", "severity": "L2", "description": "车站站台水泥地面与铁轨钢轨严重偏冷暗青蓝调。"},
            {"id": "F", "severity": "L2", "description": "火车机车经典涂装与警示标识严重错色破坏历史机车真实自然度。"}
        ],
        "note": "机车车头明黄警示面错涂为发暗肉粉淡白(错色 C-L3)，墨绿车身错涂为冷青湖蓝灰(错色 C-L2)，站台水泥偏冷暗青蓝(偏色 D-L2)，机车涂装失真破坏自然度(自然度 F-L2)。"
    },

    # Sheet 19
    4137: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L1", "description": "人行道旁明黄色消防栓漆面饱和度偏高略显荧光刺眼。"},
            {"id": "D", "severity": "L1", "description": "路面积雪背阴处阴影与沥青路面微偏暗冷青调。"}
        ],
        "note": "人行道明黄消防栓漆面偏高略显荧光刺眼(过饱和 E1-L1)，积雪背阴阴影微偏暗冷青(偏色 D-L1)。"
    },
    4138: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4139: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4140: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L1", "description": "大本钟石砌钟楼塔身与路面略偏暗黄褐色调。"},
            {"id": "E2", "severity": "L1", "description": "街头游客所举英国米字国旗红蓝图案欠饱和微弱发暗。"}
        ],
        "note": "大本钟石砌钟楼略偏暗黄褐(偏色 D-L1)，米字国旗图案欠饱和微暗(欠饱和 E2-L1)。"
    },
    4143: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L3", "description": "网球场原本明亮鲜艳的砖红橙色塑胶地面被彻底错涂为发暗青灰水泥色。"},
            {"id": "D", "severity": "L2", "description": "网球场围网与远景绿树严重偏暗冷青灰调。"},
            {"id": "E2", "severity": "L2", "description": "红土/红塑胶球场特征色彩完全剥落丧失。"},
            {"id": "F", "severity": "L2", "description": "砖红球场被错涂为冷灰水泥地严重违背网球场地常识。"}
        ],
        "note": "网球场砖红橙色地面彻底错涂为发暗青灰水泥色(错色 C-L3)，球场围网偏暗冷青灰(偏色 D-L2)，球场红色完全丧失(欠饱和 E2-L2)，违背常识破坏自然度(自然度 F-L2)。"
    },
    4146: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 20
    4147: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    },
    4148: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "牧场草坡泥土地面与石块严重偏冷紫褐发暗。"},
            {"id": "E2", "severity": "L2", "description": "两只依偎的小羊羔身体羊毛暖黄色严重欠饱和褪色呈冷灰白色。"},
            {"id": "F", "severity": "L2", "description": "小羊羔羊毛严重冷灰发暗使可爱幼崽失去生机活力。"}
        ],
        "note": "牧场草坡泥土偏冷紫褐发暗(偏色 D-L2)，小羊羔身体羊毛严重欠饱和呈冷灰白(欠饱和 E2-L2)，幼崽失真失去生机破坏自然度(自然度 F-L2)。"
    },
    4150: {
        "pass": False,
        "defects": [
            {"id": "E1", "severity": "L2", "description": "动物园水池边北极熊头部与颈部被毛黄色过度浓艳刺眼偏亮橙黄色。"},
            {"id": "D", "severity": "L1", "description": "水池水面与背景岩石略偏暗暖黄调。"}
        ],
        "note": "北极熊头部与颈部被毛过度浓艳偏亮橙黄(过饱和 E1-L2)，水池水面略偏暗暖黄(偏色 D-L1)。"
    },
    4151: {
        "pass": False,
        "defects": [
            {"id": "C", "severity": "L2", "description": "双层客运通勤列车醒目的鲜红腰线涂装错涂为发暗深褐红色。"},
            {"id": "E2", "severity": "L1", "description": "前景公路骑行者所穿亮黄色风衣欠饱和微弱发暗。"},
            {"id": "D", "severity": "L1", "description": "铁路高架桥与周边灌木微偏冷暗青灰调。"}
        ],
        "note": "双层客车鲜红腰线涂装错涂为发暗深褐红(错色 C-L2)，骑行者黄风衣欠饱和发暗(欠饱和 E2-L1)，高架桥微偏冷暗青灰(偏色 D-L1)。"
    },
    4152: {
        "pass": False,
        "defects": [
            {"id": "D", "severity": "L2", "description": "草坪地面与背景树林天空全景严重偏暖橙红杂色调。"},
            {"id": "E1", "severity": "L2", "description": "停放的两辆皮卡车车漆与周边草木过度浓艳刺眼且发闷。"},
            {"id": "F", "severity": "L2", "description": "浓重的暖橙红偏色笼罩整个乡村户外场景，严重破坏视觉自然度。"}
        ],
        "note": "草坪与树林天空严重偏暖橙红杂色(偏色 D-L2)，皮卡车车漆与草木过度浓艳发闷(过饱和 E1-L2)，暖橙红偏色笼罩破坏自然度(自然度 F-L2)。"
    },
    4154: {
        "pass": True,
        "defects": [],
        "note": "审查通过"
    }
}


def run_checks_and_apply():
    print(f"Total reviews in Batch 18: {len(BATCH_18_REVIEWS)}")
    assert len(BATCH_18_REVIEWS) == 120, f"Expected 120 reviews, got {len(BATCH_18_REVIEWS)}"

    # Check validity
    pass_count = 0
    revise_count = 0
    banned_violations = []

    for tid, review in BATCH_18_REVIEWS.items():
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
    for tid, review in BATCH_18_REVIEWS.items():
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
