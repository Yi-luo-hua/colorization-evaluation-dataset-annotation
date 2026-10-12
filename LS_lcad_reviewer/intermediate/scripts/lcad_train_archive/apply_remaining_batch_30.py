# -*- coding: utf-8 -*-
"""
应用 Batch 30 审核具象定物判决字典并双向同步至正式交付文件
Batch 30: Task #6117 ~ #6302 (共 120 组)
"""

import json
import os
import re

# 120 组人工直审与具象定物判决字典
REVIEWS_B30 = {
    # Sheet 01
    6117: {
        "score": 2.56,
        "severities": {"D": "L1", "E1": "L2", "F": "L1"},
        "note": "高尔夫果岭与大面积草坪严重过饱和偏刺目荧光草绿色(E1-L2, D-L1, F-L1)。"
    },
    6119: {
        "score": 5.0,
        "severities": {"C": "L3", "D": "L1", "E2": "L2", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：交通信号灯原本鲜亮明黄外壳颠覆性彻底脱色错涂为冷青灰白调(C-L3, E2-L2, D-L1, F-L2)。"
    },
    6120: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：网球运动员身穿的鲜亮荧光粉红无袖运动衫大面积脱色发暗偏紫(C-L2, E2-L1, D-L1, F-L1)。"
    },
    6121: {
        "score": 2.61,
        "severities": {"D": "L2", "F": "L1"},
        "note": "吃蛋糕女士的面部肤色及发丝严重偏向暗红褐色与浑浊暗冷杂光(D-L2, F-L1)。"
    },
    6124: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6125: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：大象厚重象皮表面及背部轻微泛起不自然的草绿黄色杂光(D-L1, F-L1)。"
    },

    # Sheet 02
    6127: {
        "score": 2.23,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "白色轿车车身车顶与反光镜大面积偏向浓郁刺目的深焦糖暖红黄褐色，过饱和失真(D-L2, E1-L2, F-L2)。"
    },
    6128: {
        "score": 2.47,
        "severities": {"C": "L2", "D": "L2", "E2": "L1", "F": "L2"},
        "note": "草地上放置的浅蓝绿陶瓷马桶大面积脱色错涂为脏污灰白色，背景偏暖(C-L2, D-L2, E2-L1, F-L2)。"
    },
    6129: {
        "score": 2.36,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "街头路牌上方的整片天空大面积偏向浓烈刺目的深洋红与紫红晚霞光晕，过饱和失真(D-L2, E1-L2, F-L2)。"
    },
    6130: {
        "score": 2.17,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "门缝旁的白色门框与室内墙壁大面积严重偏向浑浊发暗的暖黄泥土色(D-L1, E2-L1, F-L1)。"
    },
    6133: {
        "score": 2.17,
        "severities": {"C": "L3", "D": "L1", "E2": "L2", "F": "L2"},
        "note": "小型客机展台周围原本生机翠绿的草坪大面积严重脱色错涂为焦黑枯黄泥土杂色(C-L3, E2-L2, D-L1, F-L2)。"
    },
    6134: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：高原草甸上的棕黄骏马皮毛与天空背景整体色调偏暗暖红黄褐色(D-L1, F-L1)。"
    },

    # Sheet 03
    6135: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：躺在床上的女孩身上原本鲜艳的大红毛衣被严重错涂为粉红玫红色(C-L2, D-L1, F-L1)。"
    },
    6140: {
        "score": 2.47,
        "severities": {"D": "L2", "E2": "L1", "F": "L1"},
        "note": "手绘涂鸦卫生间内的瓷砖墙壁大面积严重偏冷发暗，温暖暖色彻底褪变为阴冷青灰调(D-L2, E2-L1, F-L1)。"
    },
    6142: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6150: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6151: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6152: {
        "score": 2.23,
        "severities": {"C": "L2", "D": "L2", "F": "L2"},
        "note": "停放摩托车的车库外墙及卷帘门周边大面积偏向诡异不自然的草绿黄色调(C-L2, D-L2, F-L2)。"
    },

    # Sheet 04
    6153: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6156: {
        "score": 2.61,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "掷飞盘场地后方的林木树冠与草坪大面积偏向发暗浓重的冷青蓝绿色(D-L1, E1-L1, F-L1)。"
    },
    6158: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6159: {
        "score": 4.55,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "餐桌上的彩色条纹织物桌布大面积偏向发暗冷沉的洋红蓝紫调，水果色泽欠饱和(D-L1, E2-L1, F-L1)。"
    },
    6160: {
        "score": 2.30,
        "severities": {"C": "L2", "D": "L2", "F": "L2"},
        "note": "手工操作台上的剪纸图样与相框周边大面积泛起浓艳刺目的深洋红与冷紫假色(C-L2, D-L2, F-L2)。"
    },
    6162: {
        "score": 2.73,
        "severities": {"D": "L2", "E2": "L1", "F": "L2"},
        "note": "撑伞男女上方的阴天天空与大雨伞大面积偏向浑浊发暗的暗红黄褐色调(D-L2, E2-L1, F-L2)。"
    },

    # Sheet 05
    6164: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6165: {
        "score": 2.17,
        "severities": {"D": "L1", "E1": "L3", "F": "L2"},
        "note": "公路背景原本浅灰阴暗的天空被严重错涂为大面积浓烈刺目的荧光深天蓝色，过饱和失真(D-L1, E1-L3, F-L2)。"
    },
    6166: {
        "score": 2.47,
        "severities": {"D": "L2", "F": "L1"},
        "note": "火车站内站台水泥立柱与橙黄动车组车头大面积泛起浓重浑浊的暗红褐色与冷紫发暗杂光(D-L2, F-L1)。"
    },
    6167: {
        "score": 2.25,
        "severities": {"D": "L2", "E2": "L1", "F": "L2"},
        "note": "卫生间内的大理石梳妆台台面与白色储物柜整体色调严重偏冷发暗，温馨暖黄色温彻底褪为阴冷青灰(D-L2, E2-L1, F-L2)。"
    },
    6168: {
        "score": 2.43,
        "severities": {"D": "L1", "E1": "L2", "F": "L2"},
        "note": "餐盘内烤制帕尼尼三明治面包表面大面积偏向浓烈刺目的火红橙色，过饱和失真(D-L1, E1-L2, F-L2)。"
    },
    6169: {
        "score": 2.56,
        "severities": {"C": "L2", "D": "L2", "E2": "L2", "F": "L1"},
        "note": "冲浪少年身下的整片海洋海水与翻滚浪花大面积严重脱色，被错涂为浑浊暗淡的脏泥红褐色(C-L2, D-L2, E2-L2, F-L1)。"
    },

    # Sheet 06
    6170: {
        "score": 2.23,
        "severities": {"D": "L2", "E2": "L2", "F": "L1"},
        "note": "旷野中的枯树灌木林与地面草丛大面积脱色欠饱和，系统性偏向暗冷青灰黑调(D-L2, E2-L2, F-L1)。"
    },
    6171: {
        "score": 2.27,
        "severities": {"D": "L1", "E2": "L2", "F": "L2"},
        "note": "卫生间内的淋浴墙壁与独立浴缸大面积严重偏冷发暗，温馨暖黄色温彻底脱色褪变为阴暗青灰调(D-L1, E2-L2, F-L2)。"
    },
    6174: {
        "score": 4.23,
        "severities": {"D": "L1", "F": "L1"},
        "note": "玩游戏机男子身旁的老式CRT电视机外壳与背景墙面泛起刺目的暗红褐色与冷紫发暗杂光(D-L1, F-L1)。"
    },
    6175: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6177: {
        "score": 4.55,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "停机坪上总统专机机身浅天蓝涂装轻微偏暗发紫，地面防撞警示锥橙色微淡(D-L1, E2-L1, F-L1)。"
    },
    6178: {
        "score": 1.04,
        "severities": {"C": "L3", "D": "L2", "E1": "L3", "F": "L3"},
        "note": "夜景彩绘巴士的车头挡风玻璃与车身霓虹车标颠覆性错涂为大面积极其浓烈刺目的荧光大红与深洋红色，极度过饱和失真(C-L3, D-L2, E1-L3, F-L3)。"
    },

    # Sheet 07
    6179: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6181: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：切开的新鲜橙子身后的实木背景板整体色调轻微偏冷青蓝暗调(D-L1, F-L1)。"
    },
    6182: {
        "score": 2.25,
        "severities": {"D": "L2", "E2": "L1", "F": "L1"},
        "note": "复古黑胶唱片机周边的木质地板与后方木椅大面积脱色欠饱和，系统性偏向暗冷青黑灰调(D-L2, E2-L1, F-L1)。"
    },
    6183: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6184: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6185: {
        "score": 2.61,
        "severities": {"D": "L2", "F": "L1"},
        "note": "卧榻上的斑马纹绒毯与黑色猫咪毛皮大面积偏向暗红褐色与浑浊冷紫发暗杂色(D-L2, F-L1)。"
    },

    # Sheet 08
    6186: {
        "score": 2.73,
        "severities": {"C": "L2", "D": "L1", "E2": "L2", "F": "L1"},
        "note": "繁华街头悬挂的鲜黄色商业店面招牌大面积脱色欠饱和，严重褪变为暗淡灰白色(C-L2, D-L1, E2-L2, F-L1)。"
    },
    6189: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6191: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6192: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L1", "E1": "L2", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：敞篷摩托车上老者身穿的衣物与面部皮肤严重错涂为刺目浓艳的深洋红紫色，背景红墙浓艳失真(C-L2, D-L1, E1-L2, F-L2)。"
    },
    6193: {
        "score": 2.61,
        "severities": {"D": "L2", "F": "L1"},
        "note": "林荫道上行驶的红色双层公共汽车车身与沥青路面大面积偏向暗红褐色与浑浊冷紫发暗杂色(D-L2, F-L1)。"
    },
    6194: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 09
    6195: {
        "score": 2.43,
        "severities": {"E1": "L2", "F": "L2"},
        "note": "草绿色餐盘内盛放的草莓蛋糕横切面大面积偏向浓烈刺目的荧光血红色，过饱和失真严重(E1-L2, F-L2)。"
    },
    6196: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6197: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：热带海滩远景海湾岛屿植被与深水海面整体色调轻微偏冷青蓝暗调(D-L1, F-L1)。"
    },
    6199: {
        "score": 2.36,
        "severities": {"D": "L2", "F": "L2"},
        "note": "室内暖光台灯身后的背景大白墙大面积偏向暗红褐色与浑浊冷紫发暗杂色(D-L2, F-L2)。"
    },
    6200: {
        "score": 2.25,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "重型摩托车身后的整片树林树冠大面积偏向浓烈刺目的荧光草绿黄色，过饱和失真严重(D-L2, E1-L2, F-L2)。"
    },
    6202: {
        "score": 1.07,
        "severities": {"C": "L3", "D": "L2", "E1": "L2", "F": "L3"},
        "note": "野餐垫周边的整片绿色草坪颠覆性严重错涂褪变为焦烂发暗的深焦糖暗红泥黄色，过饱和失真严重(C-L3, D-L2, E1-L2, F-L3)。"
    },

    # Sheet 10
    6203: {
        "score": 5.0,
        "severities": {"C": "L1", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：双人床上的大红被褥大面积偏暗发紫泛刺目洋红，背景实木床头板与墙面偏冷青暗灰(C-L1, D-L1, F-L1)。"
    },
    6204: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6205: {
        "score": 2.23,
        "severities": {"D": "L2", "E2": "L2", "F": "L1"},
        "note": "角马与斑马群奔跑的大草原草地大面积脱色欠饱和，系统性偏向暗冷青灰黑调(D-L2, E2-L2, F-L1)。"
    },
    6213: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：石砌建筑外墙与复古铁艺路灯底座整体色调轻微偏冷青蓝暗调(D-L1, F-L1)。"
    },
    6214: {
        "score": 2.23,
        "severities": {"D": "L2", "F": "L1"},
        "note": "整理西服男士的面部皮肤与双手大面积偏向暗红褐色与浑浊冷紫发暗杂色(D-L2, F-L1)。"
    },
    6215: {
        "score": 2.36,
        "severities": {"D": "L1", "F": "L1"},
        "note": "街头商铺玻璃门面与停车缴费机表面大面积泛起暗冷深紫红发暗杂光(D-L1, F-L1)。"
    },

    # Sheet 11
    6216: {
        "score": 2.05,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "木板墙上悬挂的一排木雕面具与草编玩偶整体严重褪色泛灰，头顶原本鲜亮的绿色装饰与彩绘花纹几乎完全丧失色彩活力(D-L2, E2-L2, F-L2)。"
    },
    6217: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：鱼眼镜头画面边缘的天空与远景草坪整体色调轻微偏冷青暗调，红气球与手臂肤色还原尚可(D-L1, F-L1)。"
    },
    6218: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6219: {
        "score": 2.18,
        "severities": {"B": "L1", "D": "L1", "E2": "L1", "F": "L1"},
        "note": "仰头喝水男士身穿的卡其色短袖T恤及女士面部手臂肤色偏暗发灰泛青紫杂色，人物轮廓边缘伴有轻微色晕扩散(B-L1, D-L1, E2-L1, F-L1)。"
    },
    6223: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：托举编织甜甜圈玩偶的手掌手指皮肤表面轻微偏向暗黄绿色，略显苍白不自然，甜甜圈红黄色调还原良好(D-L1, F-L1)。"
    },
    6224: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 12
    6227: {
        "score": 4.46,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "雪地滑雪场远景围栏与雪地表面整体色调轻微偏冷青蓝暗调，滑雪者深色防寒服还原尚可(D-L1, E2-L1)。"
    },
    6228: {
        "score": 2.27,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "鱼眼镜头下的棒球手手中握持的木质球棒与身后大面积草坪褪色发暗偏青灰，失去原本草地生机感(D-L1, E2-L1, F-L1)。"
    },
    6230: {
        "score": 1.06,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "夜幕下的欧式石砌宫殿建筑外墙、罗马廊柱与天空大面积偏向浓重刺目的深洋红与冷靛紫假色，过饱和失真严重(D-L2, E1-L2, F-L2)。"
    },
    6231: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L2", "E2": "L1", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：电脑桌身后原本鲜艳温暖的橙红暖色背景墙面颠覆性脱色错涂为阴冷惨白的青灰白调，木桌表面暖木色显著褪色(C-L2, D-L2, E2-L1, F-L2)。"
    },
    6232: {
        "score": 2.61,
        "severities": {"D": "L1", "F": "L1"},
        "note": "斑马黑白条纹毛皮的白色缝隙边缘微弱泛起极淡的不自然青冷杂光，整体黑白质感保持良好(D-L1, F-L1)。"
    },
    6233: {
        "score": 4.46,
        "severities": {"D": "L1"},
        "note": "书房书桌左侧背光处窗帘及阴影区域轻微泛起暗冷紫红杂光，台灯暖光与海报木桌还原自然(D-L1)。"
    },

    # Sheet 13
    6234: {
        "score": 2.56,
        "severities": {"E1": "L1", "F": "L1"},
        "note": "平房住宅的墨绿色木质外墙表面绿色偏向略微鲜亮刺目，停车计时器与白色窗框还原正常(E1-L1, F-L1)。"
    },
    6237: {
        "score": 4.55,
        "severities": {"D": "L2", "E2": "L2", "F": "L1"},
        "note": "雪山滑雪场原本温暖泛黄的怀旧胶片色调被彻底替换为阴暗单调的冷白青灰调，雪地表面整体欠饱和发暗(D-L2, E2-L2, F-L1)。"
    },
    6238: {
        "score": 2.47,
        "severities": {"D": "L2", "E2": "L1", "F": "L1"},
        "note": "西装男子脚下的草坪草地与后方绿植大面积脱色发暗，画面整体系统性偏向暗冷青灰紫调，丧失户外生机(D-L2, E2-L1, F-L1)。"
    },
    6239: {
        "score": 2.25,
        "severities": {"C": "L2", "D": "L2", "E2": "L1", "F": "L2"},
        "note": "街头大象身后原本鲜亮的天蓝色商业旅馆招牌被严重错涂为发暗的泥土黄褐色，大象背部厚皮泛起不自然的暗冷杂色(C-L2, D-L2, E2-L1, F-L2)。"
    },
    6240: {
        "score": 2.25,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "水上冲浪少年身后的湖泊水面与远山植被整体色调轻微偏冷青暗沉，水花与皮肤细节还原尚可(D-L1, E2-L1, F-L1)。"
    },
    6242: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：皮卡车货厢后斗内原本深蓝紫色的防水遮雨篷布严重脱色错涂为脏污暗淡的灰褐土色，丧失原本织物色彩(C-L2, E2-L1, F-L1)。"
    },

    # Sheet 14
    6243: {
        "score": 2.25,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "双层公共汽车车身草绿色涂装过于鲜亮刺目，伴随背景天空与建筑大面积偏向暗冷紫红假色(D-L2, E1-L2, F-L2)。"
    },
    6244: {
        "score": 4.46,
        "severities": {"D": "L1"},
        "note": "桌面摆放的多款手机背壳及硅胶挂件色彩还原基本准确，仅局部阴影缝隙微泛暗冷色调(D-L1)。"
    },
    6246: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：鲜红消防栓身后的绿植灌木丛叶片整体色彩欠饱和发暗，原本生机翠绿褪色偏灰(D-L1, E2-L1, F-L1)。"
    },
    6247: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "原5.0满分严重漏检，核查发现：沙滩上海浪与近岸海水整体色调偏向较深的冷青蓝色，略显浓重沉闷(D-L1, E1-L1)。"
    },
    6249: {
        "score": 2.73,
        "severities": {"D": "L1", "E2": "L2", "F": "L1"},
        "note": "路口八角形红色STOP停车标志牌与顶部小国旗红白条纹大面积褪色发暗，鲜红底色严重欠饱和退化为暗褐红(D-L1, E2-L2, F-L1)。"
    },
    6250: {
        "score": 2.36,
        "severities": {"D": "L2", "E1": "L1", "F": "L2"},
        "note": "室内黄色猎犬身旁的背景墙壁与地面大面积泛起浓重不自然的暗冷深紫假色，犬只背部毛色略显红浓(D-L2, E1-L1, F-L2)。"
    },

    # Sheet 15
    6252: {
        "score": 2.36,
        "severities": {"D": "L1", "F": "L1"},
        "note": "手臂佩戴的白色石膏固定夹板表面严重泛起不自然的暗粉红与冷紫杂光假色，披萨饼表面色泽还原尚可(D-L1, F-L1)。"
    },
    6253: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：温馨客厅内台灯照射下的米黄背景墙面与布艺沙发整体色调偏冷发白，缺失原有温暖的金黄灯光氛围(D-L1, E2-L1, F-L1)。"
    },
    6255: {
        "score": 4.46,
        "severities": {"D": "L1"},
        "note": "微波炉金属不锈钢外壳暗面微弱泛起暗冷青灰调，炉门玻璃与内部食物烘烤色泽还原自然(D-L1)。"
    },
    6256: {
        "score": 1.20,
        "severities": {},
        "note": "审查通过"
    },
    6257: {
        "score": 2.17,
        "severities": {"D": "L2", "E2": "L1", "F": "L2"},
        "note": "室内举臂男士的面部皮肤与颈部手臂大面积泛起不自然的暗冷粉紫杂色，背景墙面整体色调偏暗沉(D-L2, E2-L1, F-L2)。"
    },
    6258: {
        "score": 1.06,
        "severities": {"D": "L2", "E1": "L1", "F": "L2"},
        "note": "斑马臀部黑白条纹毛皮与后腿内侧大面积泛起浓重违和的冷紫靛蓝假色光斑，破坏原本黑白毛皮质感(D-L2, E1-L1, F-L2)。"
    },

    # Sheet 16
    6260: {
        "score": 4.17,
        "severities": {"B": "L1", "E1": "L1"},
        "note": "小女孩手持的甜甜圈表面亮粉色糖霜边缘轻微渗透扩散至面包边缘，糖霜饱和度略高(B-L1, E1-L1)。"
    },
    6261: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6263: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6264: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：自行车车把上小鸟身后的草坪背景整体色调偏暗偏冷，生机鲜绿退化为发暗的灰绿橄榄色(D-L1, E2-L1, F-L1)。"
    },
    6265: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6267: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 17
    6268: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：棒球场内野红土赛道表面色调轻微偏向暗暖黄褐色，外野草坪与球员球服还原良好(D-L1, F-L1)。"
    },
    6269: {
        "score": 5.0,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：自行车身后木质平房建筑原本鲜亮温暖的橙黄木板外墙大面积褪色发暗，退化为发灰的土灰黄色(D-L2, E2-L2, F-L2)。"
    },
    6270: {
        "score": 5.0,
        "severities": {"D": "L1"},
        "note": "原5.0满分严重漏检，核查发现：青年男子头戴的明黄色针织冷帽与黄色领巾边缘微弱泛起暗暖杂色，面部络腮胡肤色还原生动(D-L1)。"
    },
    6271: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6272: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：长椅上方原本翠绿色的布艺坐垫被明显错涂为冷青湖蓝色，小狗浅黄皮毛略微泛白(C-L2, D-L1, F-L1)。"
    },
    6273: {
        "score": 2.25,
        "severities": {"D": "L2", "E2": "L1", "F": "L2"},
        "note": "停放在草地上的重型巡航摩托车金属烤漆车身大面积泛起违和的冷紫靛蓝反光假色，周边草地色泽发暗(D-L2, E2-L1, F-L2)。"
    },

    # Sheet 18
    6275: {
        "score": 1.00,
        "severities": {"A": ""},
        "note": "古老欧式石砌建筑外墙、窗框与地面长凳全域上色失败，整体画面呈现无任何色彩信息的纯灰度图像(A)。"
    },
    6276: {
        "score": 2.17,
        "severities": {"D": "L1", "E1": "L1", "F": "L2"},
        "note": "棒球场观众席看台与内野防护栏区域大面积泛起浓重不自然的暗冷紫红假色，跑垒员球服微泛紫光(D-L1, E1-L1, F-L2)。"
    },
    6277: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6278: {
        "score": 2.36,
        "severities": {"D": "L2", "F": "L2"},
        "note": "室内吊灯照射下的背景墙面与天花板大面积偏向暗冷青灰紫调，破坏原有温馨金黄暖光氛围(D-L2, F-L2)。"
    },
    6279: {
        "score": 2.17,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "围栏内马群棕红骏马皮毛与草地色彩略显浓郁鲜亮，白马皮毛与背景山峦还原逼真(D-L1, E1-L1)。"
    },
    6283: {
        "score": 1.00,
        "severities": {"A": ""},
        "note": "海滩遮阳草棚、沙滩与整片海洋全域上色失败，画面整体沦为无色彩信息的纯灰度图像(A)。"
    },

    # Sheet 19
    6284: {
        "score": 2.47,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "长椅上看书女士身后的草坪整体色调偏暗偏冷，嫩绿草地生机感轻微褪色欠饱和(D-L1, E2-L1, F-L1)。"
    },
    6285: {
        "score": 1.04,
        "severities": {"D": "L2", "E1": "L3", "F": "L3"},
        "note": "夜景街道路灯光晕、周边夜空与红砖历史建筑通体颠覆性偏向极其浓烈刺目的血红焦糖假色，过饱和失真严重(D-L2, E1-L3, F-L3)。"
    },
    6286: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6287: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6288: {
        "score": 2.23,
        "severities": {"D": "L2", "F": "L1"},
        "note": "快餐桌上摆放的水果饮料金属易拉罐表面与阴影处大面积泛起违和的暗冷紫蓝杂光假色，热狗色泽还原尚可(D-L2, F-L1)。"
    },
    6289: {
        "score": 4.17,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 20
    6290: {
        "score": 4.30,
        "severities": {"C": "L2", "D": "L1", "E2": "L2", "F": "L2"},
        "note": "观光马车原本鲜艳红色的车轮轮圈与辐条颠覆性严重脱色错涂为惨白无色，马车车厢织物色彩明显欠饱和(C-L2, D-L1, E2-L2, F-L2)。"
    },
    6294: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6297: {
        "score": 2.14,
        "severities": {"C": "L2", "D": "L1", "E2": "L1", "F": "L2"},
        "note": "猕猴额头及眼部周围皮肤被颠覆性错涂上浓重违和的橙红与紫红假色斑块，身体皮毛与周边草地则欠饱和发灰(C-L2, D-L1, E2-L1, F-L2)。"
    },
    6300: {
        "score": 2.36,
        "severities": {"B": "L1", "D": "L2", "F": "L2"},
        "note": "室内茶几上摆放的花卉盆栽与绿植叶片边缘大面积泛起不自然的暗冷深紫溢色与荧光假色(B-L1, D-L2, F-L2)。"
    },
    6301: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6302: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：海滩垂钓者脚下的沙滩表面大面积偏向暗冷土黄色，丧失原有金黄砂砾色泽，海水边缘微泛冷调(D-L1, E2-L1, F-L1)。"
    }
}

DEFECT_NAMES = {
    "A": "缺色",
    "B": "溢色",
    "C": "错色",
    "D": "偏色",
    "E1": "过饱和",
    "E2": "欠饱和",
    "F": "视觉自然度"
}

FORBIDDEN_WORDS = ["关键区域", "某些区域", "局部区域", "某些部分", "局部边缘区域", "主体或背景"]

def validate_reviews():
    print(f"[*] 正在核查 Batch 30 的 {len(REVIEWS_B30)} 组具象定物判决规则...")
    assert len(REVIEWS_B30) == 120, f"数量不匹配，期望 120，实际 {len(REVIEWS_B30)}"

    for tid, r in REVIEWS_B30.items():
        note = r["note"]
        sevs = r["severities"]

        # 1. 禁用抽象代词核查
        for fw in FORBIDDEN_WORDS:
            assert fw not in note, f"Task #{tid} 包含禁用抽象词 '{fw}': {note}"

        # 2. 互斥标签核查 (E1 vs E2)
        if "E1" in sevs and "E2" in sevs:
            raise AssertionError(f"Task #{tid} 同时包含 E1 和 E2 互斥标签！")

        # 3. 熔断项 A 规范核查
        if "A" in sevs:
            assert sevs["A"] == "", f"Task #{tid} A 熔断项 severity 必须为空字符串！"
            assert len(sevs) == 1, f"Task #{tid} 命中 A 熔断项时不可并存其他缺陷！"

        # 4. 放行规范
        if not sevs:
            assert note == "审查通过", f"Task #{tid} 放行项 review_note 必须为 '审查通过'！"

    print("[+] 全部 120 组规则校验断言 100% 通过！无抽象词，无逻辑互斥！")

def build_defect_list(sevs, note):
    if not sevs:
        return []
    
    # 清洗 note 去除提示前缀
    clean_desc = re.sub(r"^原[\d\.]+满分.*?核查发现[：:]\s*", "", note)
    clean_desc = re.sub(r"^[【\[].*?[\]】]\s*", "", clean_desc)
    clean_desc = clean_desc.strip()

    defects = []
    for did, sev in sevs.items():
        defects.append({
            "id": did,
            "name": DEFECT_NAMES[did],
            "severity": sev,
            "description": clean_desc
        })
    return defects

def main():
    validate_reviews()

    # __file__ is in LS_lcad_reviewer/intermediate/scripts/
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    intermediate_dir = os.path.dirname(scripts_dir)
    base_dir = os.path.dirname(intermediate_dir)  # LS_lcad_reviewer

    all_export_path = os.path.join(base_dir, "exports", "reviewed_1_10000_all.json")
    clean_export_path = os.path.join(base_dir, "exports", "reviewed_1_10000_clean.json")
    grounding_out_path = os.path.join(intermediate_dir, "audits", "grounding_remaining_batch_30.json")

    # 1. 导出中间定物字典
    with open(grounding_out_path, "w", encoding="utf-8") as f:
        json.dump(REVIEWS_B30, f, ensure_ascii=False, indent=2)
    print(f"[+] 导出中间定物字典 -> {grounding_out_path}")

    # 2. 读取两份全量导出文件并同步更新
    with open(all_export_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)
    with open(clean_export_path, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    all_tasks = all_data["annotations"]
    clean_tasks = clean_data["annotations"]

    updated_count = 0
    pass_count = 0
    fail_count = 0
    a_melt_count = 0

    for tid, r in REVIEWS_B30.items():
        idx = tid - 1  # 1-based to 0-based
        sevs = r["severities"]
        note = r["note"]
        defects = build_defect_list(sevs, note)

        # 确定 review_note
        if not sevs:
            all_note = "审查通过"
            pass_count += 1
        else:
            all_note = note
            fail_count += 1
            if "A" in sevs:
                a_melt_count += 1

        is_a_melt = ("A" in sevs)
        reviewed_score = 1.0 if is_a_melt else None
        needs_rescoring = False if is_a_melt else True

        # 更新 all_tasks
        item_all = all_tasks[idx]
        item_all["defects"] = defects
        item_all["review_status"] = "已核验"
        item_all["review_note"] = all_note
        item_all["reviewed_score"] = reviewed_score
        item_all["needs_rescoring"] = needs_rescoring

        # 更新 clean_tasks (纯净交付版 review_note 统一为 "")
        item_clean = clean_tasks[idx]
        item_clean["defects"] = defects
        item_clean["review_status"] = "已核验"
        item_clean["review_note"] = ""
        item_clean["reviewed_score"] = reviewed_score
        item_clean["needs_rescoring"] = needs_rescoring

        updated_count += 1

    print(f"[*] 成功更新 {updated_count} 组任务！放行通过: {pass_count} 组，改判扣分: {fail_count} 组（其中缺色A熔断: {a_melt_count} 组）")

    # 写回文件
    with open(all_export_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"[+] 写回全量详细交付文件 -> {all_export_path}")

    with open(clean_export_path, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"[+] 写回全量纯净交付文件 -> {clean_export_path}")

if __name__ == "__main__":
    main()
