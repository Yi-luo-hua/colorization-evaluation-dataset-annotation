# -*- coding: utf-8 -*-
"""
应用 Batch 31 审核具象定物判决字典并双向同步至正式交付文件
Batch 31: Task #6304 ~ #6471 (共 120 组)
"""

import json
import os
import re

# 120 组人工直审与具象定物判决字典
REVIEWS_B31 = {
    # Sheet 01
    6304: {
        "score": 2.14,
        "severities": {"E2": "L1", "D": "L1", "F": "L1"},
        "note": "明黄色标题文字与嫩绿食材包装大面积欠饱和褪色发暗，背景泛暗冷偏色(E2-L1, D-L1, F-L1)。"
    },
    6307: {
        "score": 2.36,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "复古厨房实木吊柜柜门与台面大面积偏暗发灰，木质光泽感欠饱和褪色(D-L1, E2-L1)。"
    },
    6309: {
        "score": 2.17,
        "severities": {"D": "L2", "E1": "L1", "F": "L2"},
        "note": "双手拉扯披萨拉丝芝士时手指皮肤与餐盘边缘大面积泛起浓重暗冷青紫与暗红杂色(D-L2, E1-L1, F-L2)。"
    },
    6310: {
        "score": 2.43,
        "severities": {"E2": "L1", "D": "L1", "F": "L1"},
        "note": "怀抱棕色小狗青年身后背景草坪与绿植欠饱和褪色偏灰，色调微偏冷(E2-L1, D-L1, F-L1)。"
    },
    6311: {
        "score": 2.14,
        "severities": {"C": "L2", "D": "L1", "E1": "L1", "F": "L1"},
        "note": "网球运动员身穿的宝蓝色短袖运动T恤大面积脱色错涂为发暗灰紫浅蓝调(C-L2, D-L1, E1-L1, F-L1)。"
    },
    6312: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 02
    6313: {
        "score": 2.47,
        "severities": {"D": "L2", "E2": "L1", "F": "L1"},
        "note": "长颈鹿身后原本晴朗湛蓝的天空大面积褪色偏向暗冷灰白调，色彩活力受损(D-L2, E2-L1, F-L1)。"
    },
    6314: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6315: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6316: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6318: {
        "score": 2.27,
        "severities": {"C": "L2", "E1": "L2", "F": "L2"},
        "note": "停在树枝上的飞鸟胸脯与腹部羽毛被大面积错涂为刺目浓艳的荧光翠绿色伪色(C-L2, E1-L2, F-L2)。"
    },
    6319: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 03
    6321: {
        "score": 1.08,
        "severities": {"D": "L1"},
        "note": "水面上飞掠白海鸥与金黄芦苇水波光影暗部微弱偏色，整体还原度良好(D-L1)。"
    },
    6322: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6325: {
        "score": 4.46,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "卫生间门框与瓷砖墙面阴影暗部轻微偏向暗冷青灰调，微欠饱和(D-L1, E2-L1)。"
    },
    6326: {
        "score": 4.17,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "玻璃保鲜盒内火腿三明治肉质切面色泽欠饱和微泛暗灰，新鲜感略降(D-L1, E2-L1)。"
    },
    6330: {
        "score": 1.02,
        "severities": {"C": "L2", "D": "L2", "E2": "L2", "F": "L3"},
        "note": "西餐桌三明治与室内金黄暖光氛围被颠覆性篡改为惨淡发青的冷蓝阴影调，严重失真(C-L2, D-L2, E2-L2, F-L3)。"
    },
    6332: {
        "score": 2.47,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "咖喱蛋包饭表面金黄蛋皮大面积欠饱和褪色偏向苍白灰黄，室内暖光氛围冷化(D-L2, E2-L2, F-L2)。"
    },

    # Sheet 04
    6334: {
        "score": 2.17,
        "severities": {"E2": "L2", "D": "L1", "F": "L1"},
        "note": "腾空跳跃滑板青年身穿的宝蓝短袖T恤大面积严重脱色褪为暗灰白色(E2-L2, D-L1, F-L1)。"
    },
    6335: {
        "score": 2.17,
        "severities": {"D": "L2", "E2": "L1", "F": "L2"},
        "note": "复古车库展示厅墙面大面积泛发暗冷青蓝紫光晕，机车红色油箱微欠饱和(D-L2, E2-L1, F-L2)。"
    },
    6336: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6337: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6338: {
        "score": 2.17,
        "severities": {"D": "L2", "E2": "L1", "F": "L2"},
        "note": "四台笔记本电脑屏幕桌面壁纸大面积泛发暗红褐色与冷紫发暗杂色伪色(D-L2, E2-L1, F-L2)。"
    },
    6340: {
        "score": 2.17,
        "severities": {"D": "L2", "E2": "L1", "F": "L1"},
        "note": "夜景钟楼石砌外墙由金黄暖调褪色偏向惨淡冷黄灰，暖光氛围冷化受损(D-L2, E2-L1, F-L1)。"
    },

    # Sheet 05
    6342: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6343: {
        "score": 5.0,
        "severities": {"D": "L1"},
        "note": "公交站台左侧广告灯箱与地面阴影轻微泛发暗冷青绿杂色(D-L1)。"
    },
    6344: {
        "score": 2.13,
        "severities": {"E2": "L1", "D": "L1", "F": "L1"},
        "note": "卫生间马桶身后原本浅蓝瓷砖墙面大面积脱色褪为发暗青灰白，微有色偏(E2-L1, D-L1, F-L1)。"
    },
    6345: {
        "score": 2.47,
        "severities": {"D": "L1"},
        "note": "戴报童帽青年男士络腮胡与外套暗部微泛暖褐色调，主体肤色自然(D-L1)。"
    },
    6346: {
        "score": 2.11,
        "severities": {"D": "L2", "F": "L2"},
        "note": "双扇木窗周围草绿色墙面大面积泛起浓重刺目的深紫伪色杂斑(D-L2, F-L2)。"
    },
    6347: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 06
    6348: {
        "score": 2.43,
        "severities": {"E2": "L1", "D": "L1", "F": "L1"},
        "note": "斑马身旁年轻游客身穿的深绿短袖T恤大面积严重褪色发暗发灰(E2-L1, D-L1, F-L1)。"
    },
    6350: {
        "score": 4.17,
        "severities": {},
        "note": "审查通过"
    },
    6351: {
        "score": 2.47,
        "severities": {"D": "L1"},
        "note": "办公室电脑前女士面部背光处与发光屏幕暗部轻微泛发暗杂色(D-L1)。"
    },
    6352: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6355: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：停放摩托车场地前方翠绿色金属隔离护栏错涂为发暗泥土红褐色(C-L2, E2-L1, F-L1)。"
    },
    6357: {
        "score": 4.46,
        "severities": {"C": "L2", "F": "L1"},
        "note": "不锈钢冷柜柜门上方明黄色食品标签标贴被严重错涂为鲜红色(C-L2, F-L1)。"
    },

    # Sheet 07
    6358: {
        "score": 5.0,
        "severities": {"D": "L2", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：烤箱发热管橙红火光冷化发白褪色，内壁大面积偏冷青灰色(D-L2, E2-L1, F-L1)。"
    },
    6359: {
        "score": 2.47,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "长颈鹿身后森林树冠翠绿偏冷偏暗退化为青蓝暗绿色，欠饱和发灰(D-L1, E2-L1, F-L1)。"
    },
    6360: {
        "score": 2.17,
        "severities": {"E1": "L2", "D": "L1", "F": "L2"},
        "note": "菜地西蓝花左侧嫩绿叶片大面积涂抹上刺目荧光翠绿色，过饱和失真(E1-L2, D-L1, F-L2)。"
    },
    6362: {
        "score": 2.56,
        "severities": {},
        "note": "审查通过"
    },
    6365: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6366: {
        "score": 2.43,
        "severities": {"E2": "L1", "D": "L1", "F": "L1"},
        "note": "黑色卷毛犬颈部佩戴的宝蓝项圈大面积脱色褪为发暗浅灰蓝，色彩活力受损(E2-L1, D-L1, F-L1)。"
    },

    # Sheet 08
    6368: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6369: {
        "score": 2.17,
        "severities": {"D": "L2", "E2": "L1", "F": "L2"},
        "note": "夜景雪地小镇街头暖黄灯光氛围冷化替换为阴冷青蓝，红色招牌大面积褪色偏冷(D-L2, E2-L1, F-L2)。"
    },
    6370: {
        "score": 4.46,
        "severities": {"C": "L2", "D": "L1", "F": "L1"},
        "note": "洗手台上李施德林薄荷绿漱口水透明液体被严重错涂为冷青湖蓝色(C-L2, D-L1, F-L1)。"
    },
    6371: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    6372: {
        "score": 5.0,
        "severities": {"E2": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：焗烤千层面表面芝士大面积褪色发白，焦香金黄斑块严重欠饱和(E2-L2, D-L1, F-L1)。"
    },
    6373: {
        "score": 2.73,
        "severities": {"E2": "L2", "D": "L1", "F": "L1"},
        "note": "卡车身旁路人鲜红外套与红帽大面积严重脱色褪为发暗肉粉白灰，欠饱和(E2-L2, D-L1, F-L1)。"
    },

    # Sheet 09
    6376: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：砧板上鲜橙色胡萝卜大面积脱色错涂为发暗肉粉灰调(C-L2, D-L1, F-L1)。"
    },
    6377: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6380: {
        "score": 5.0,
        "severities": {"E2": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：滑板道水泥边缘鲜红字母涂鸦彩绘大面积严重脱色褪为苍白暗灰色(E2-L2, D-L1, F-L1)。"
    },
    6381: {
        "score": 4.17,
        "severities": {},
        "note": "审查通过"
    },
    6382: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6385: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 10
    6386: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6387: {
        "score": 2.43,
        "severities": {"D": "L2", "E2": "L1", "F": "L1"},
        "note": "浴室淋浴隔间米黄色瓷砖墙面大面积偏向发暗冷淡青绿灰，欠饱和且色温冷化(D-L2, E2-L1, F-L1)。"
    },
    6388: {
        "score": 2.43,
        "severities": {"E1": "L1", "D": "L1", "F": "L1"},
        "note": "陶瓷花盆表面草绿色釉面浓艳发亮偏向刺目荧光翠绿色，过饱和失真(E1-L1, D-L1, F-L1)。"
    },
    6389: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6390: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6391: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 11
    6392: {
        "score": 2.43,
        "severities": {},
        "note": "审查通过"
    },
    6393: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6394: {
        "score": 4.46,
        "severities": {},
        "note": "审查通过"
    },
    6396: {
        "score": 5.0,
        "severities": {"D": "L2", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：厨房餐厅橙黄色暖色瓷砖墙面与吊顶偏冷发白退化为阴冷青灰色(D-L2, E2-L1, F-L1)。"
    },
    6397: {
        "score": 2.17,
        "severities": {},
        "note": "审查通过"
    },
    6399: {
        "score": 1.04,
        "severities": {"D": "L2", "E1": "L3", "F": "L3"},
        "note": "夜景街区黄色出租车烤漆与沥青道路通体浸染深紫罗兰冷靛蓝刺目假色，严重失真(D-L2, E1-L3, F-L3)。"
    },

    # Sheet 12
    6400: {
        "score": 5.0,
        "severities": {"E2": "L1", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：石砌街道上游客鲜红外套大面积褪色偏向暗冷紫红，色彩欠饱和(E2-L1, D-L1, F-L1)。"
    },
    6401: {
        "score": 2.14,
        "severities": {"E1": "L1", "D": "L1"},
        "note": "大串香蕉金黄色表皮略显浓艳深黄，整体色彩饱和度微偏高(E1-L1, D-L1)。"
    },
    6402: {
        "score": 2.12,
        "severities": {},
        "note": "审查通过"
    },
    6403: {
        "score": 5.0,
        "severities": {"D": "L2", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：夜景滑雪道深邃夜空大面积泛起浓重暗红紫光伪色(D-L2, F-L2)。"
    },
    6406: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6407: {
        "score": 4.46,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 13
    6408: {
        "score": 4.17,
        "severities": {},
        "note": "审查通过"
    },
    6409: {
        "score": 2.61,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "厨房纯白橱柜柜门与抽屉面板大面积偏向浓郁发暗暖黄泥土杂色，过饱和偏色(D-L2, E1-L2, F-L2)。"
    },
    6411: {
        "score": 1.02,
        "severities": {"C": "L2", "E2": "L1", "D": "L1", "F": "L2"},
        "note": "滑板少年身后草坪生机翠绿错涂褪色为发暗泥土灰褐色，绿植生机严重受损(C-L2, E2-L1, D-L1, F-L2)。"
    },
    6412: {
        "score": 1.01,
        "severities": {"C": "L3", "B": "L2", "E1": "L2", "F": "L3"},
        "note": "纯白绵羊通体羊毛被颠覆性荒谬错涂为极其刺目违和的荧光亮天蓝色，溢色失真(C-L3, B-L2, E1-L2, F-L3)。"
    },
    6413: {
        "score": 5.0,
        "severities": {"D": "L1"},
        "note": "劳力士墨绿立钟金属表壳背光暗面轻微偏向暗冷杂色光晕(D-L1)。"
    },
    6414: {
        "score": 2.27,
        "severities": {"D": "L1", "E1": "L2", "F": "L2"},
        "note": "餐盘中水果奶油蛋糕切面与奶油大面积偏向浓艳暗红粉紫假色，过饱和失真(D-L1, E1-L2, F-L2)。"
    },

    # Sheet 14
    6416: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：大草原长颈鹿身后天空大面积褪色偏冷灰白，地表沙土略欠饱和(D-L1, E2-L1, F-L1)。"
    },
    6417: {
        "score": 5.0,
        "severities": {"D": "L1"},
        "note": "草地上野生象群象皮背光阴影区域轻微偏冷青暗灰(D-L1)。"
    },
    6419: {
        "score": 4.55,
        "severities": {"D": "L2", "E1": "L1", "F": "L2"},
        "note": "古堡钟楼淡雅米白石砌外墙大面积偏向浓重刺目深焦糖暖红黄褐色，色温过暖(D-L2, E1-L1, F-L2)。"
    },
    6420: {
        "score": 2.17,
        "severities": {"D": "L1", "F": "L1"},
        "note": "观光越野车白色金属车身侧面与阴影处轻微泛起暗粉紫杂色光晕(D-L1, F-L1)。"
    },
    6421: {
        "score": 2.47,
        "severities": {"D": "L2", "E1": "L1", "F": "L2"},
        "note": "双人床上碎花床单与白纱窗帘边缘大面积泛起暗冷青蓝与冷紫假色伪色(D-L2, E1-L1, F-L2)。"
    },
    6422: {
        "score": 4.17,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 15
    6424: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6425: {
        "score": 5.0,
        "severities": {"E2": "L1", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：笔记本电脑屏幕前金毛寻回犬面部毛发欠饱和发暗微泛冷紫(E2-L1, D-L1, F-L1)。"
    },
    6426: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6427: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6428: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6430: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 16
    6431: {
        "score": 2.73,
        "severities": {"D": "L2", "F": "L1"},
        "note": "柏油路面上骑马者身后天空与白色建筑外墙大面积泛发暗暖黄偏色，树木翠绿色温整体失真(D-L2, F-L1)。"
    },
    6432: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    6435: {
        "score": 4.46,
        "severities": {"E2": "L1", "D": "L1"},
        "note": "餐桌前方的红紫色新鲜葡萄表皮色泽欠饱和偏暗泛灰褐色，色泽鲜活感略有受损(E2-L1, D-L1)。"
    },
    6436: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6437: {
        "score": 2.27,
        "severities": {},
        "note": "审查通过"
    },
    6439: {
        "score": 5.0,
        "severities": {"E2": "L1", "D": "L1", "F": "L1"},
        "note": "立交桥旁露天停车场周边绿化灌木草坪大面积欠饱和严重褪色发暗，桥梁与阴天天空色调偏冷灰(E2-L1, D-L1, F-L1)。"
    },

    # Sheet 17
    6440: {
        "score": 4.46,
        "severities": {},
        "note": "审查通过"
    },
    6442: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6443: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6444: {
        "score": 2.43,
        "severities": {"D": "L2", "E1": "L1", "F": "L2"},
        "note": "遥控器银灰色塑料机身外壳与按键区域大面积浸染浓重刺目的粉紫与冷青蓝杂色伪色(D-L2, E1-L1, F-L2)。"
    },
    6445: {
        "score": 2.27,
        "severities": {"D": "L2", "E1": "L1", "F": "L2"},
        "note": "桌面散落的白色文件纸张与吉他英雄包装周边大面积泛起浓重刺目的洋红粉紫与冷蓝假色斑块(D-L2, E1-L1, F-L2)。"
    },
    6447: {
        "score": 2.3,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 18
    6448: {
        "score": 2.61,
        "severities": {},
        "note": "审查通过"
    },
    6450: {
        "score": 2.47,
        "severities": {"D": "L2", "F": "L1"},
        "note": "洗手间浴室瓷砖墙面与吊顶暗部阴影大面积浸染浓重深黄红褐色调，室内暖光氛围色偏失真(D-L2, F-L1)。"
    },
    6451: {
        "score": 4.46,
        "severities": {},
        "note": "审查通过"
    },
    6452: {
        "score": 2.73,
        "severities": {"E2": "L2", "D": "L1", "F": "L2"},
        "note": "卫生间天花板吊顶区域原本鲜艳的暖橙色乳胶漆大面积严重脱色褪为苍白暗灰，丧失原本活力(E2-L2, D-L1, F-L2)。"
    },
    6454: {
        "score": 5.0,
        "severities": {"C": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：草坪上站立男青年身穿的卡其灰褐色短袖T恤被严重错涂为鲜艳正红色(C-L2, F-L1)。"
    },
    6456: {
        "score": 2.17,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 19
    6457: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6459: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6460: {
        "score": 4.46,
        "severities": {"C": "L2", "D": "L1", "F": "L1"},
        "note": "小男孩身穿的鲜艳玫红色印花短袖T恤被严重错涂为发暗的朱红暖橙色(C-L2, D-L1, F-L1)。"
    },
    6461: {
        "score": 1.04,
        "severities": {"D": "L1"},
        "note": "暗光室内右侧女士脸庞轮廓与发丝暗处微泛杂色光晕，整体色彩还原度良好(D-L1)。"
    },
    6463: {
        "score": 2.14,
        "severities": {"E2": "L1", "D": "L1", "F": "L1"},
        "note": "骑象女孩身穿的荧光玫粉色无袖背心大面积欠饱和褪色为暗淡肉粉白，色彩活力受损(E2-L1, D-L1, F-L1)。"
    },
    6464: {
        "score": 2.36,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 20
    6465: {
        "score": 5.0,
        "severities": {"E2": "L1", "C": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：立柱下方20 Km/h限速标志牌黄色底色大面积欠饱和褪色为苍白灰白色(E2-L1, C-L1, F-L1)。"
    },
    6466: {
        "score": 2.47,
        "severities": {},
        "note": "审查通过"
    },
    6467: {
        "score": 2.43,
        "severities": {},
        "note": "审查通过"
    },
    6468: {
        "score": 4.46,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "户外餐桌三位聚餐女士面部肤色与背景阳光树林大面积严重偏向浓艳的焦糖红黄调，过饱和发红(D-L2, E1-L2, F-L2)。"
    },
    6470: {
        "score": 4.17,
        "severities": {},
        "note": "审查通过"
    },
    6471: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    }
}

DEFECT_NAME_MAP = {
    "A": "缺色",
    "B": "溢色",
    "C": "错色",
    "D": "偏色",
    "E1": "过饱和",
    "E2": "欠饱和",
    "F": "视觉自然度"
}

def build_defect_list(severities, note):
    """根据严重度字典与定物描述构建标准 defects 列表"""
    defects = []
    # 纯净描述提取：去除末尾 (D-L1, ...) 或 【...】
    clean_desc = re.sub(r"[\(（][A-Z0-9\s,\-]+[\)）]", "", note).strip()
    clean_desc = re.sub(r"【.*?】", "", clean_desc).strip()
    clean_desc = re.sub(r"^原5\.0满分严重漏检，核查发现：", "", clean_desc).strip()

    # 缺陷顺序
    order = ["A", "B", "C", "D", "E1", "E2", "F"]
    for d_id in order:
        if d_id in severities:
            sev = severities[d_id]
            defects.append({
                "id": d_id,
                "name": DEFECT_NAME_MAP[d_id],
                "severity": "" if d_id == "A" else sev,
                "description": clean_desc
            })
    return defects

def validate_reviews(reviews):
    """前置强校验：确保断言 100% 通过"""
    print(f"[*] 开始断言校验 Batch 31 定物判决字典 (共 {len(reviews)} 组)...")
    assert len(reviews) == 120, f"任务数不为 120: {len(reviews)}"

    abstract_words = ["关键区域", "某些区域", "局部区域", "特定区域", "局部关键", "整体区域"]

    for tid, r in reviews.items():
        sevs = r["severities"]
        note = r["note"]

        # 1. 抽象代词断言
        for word in abstract_words:
            assert word not in note, f"Task #{tid} 违规包含抽象代词 '{word}': {note}"

        # 2. 互斥断言 E1 / E2
        assert not ("E1" in sevs and "E2" in sevs), f"Task #{tid} 同时存在互斥标签 E1 和 E2!"

        # 3. 缺色 A 断言
        if "A" in sevs:
            assert sevs["A"] == "", f"Task #{tid} 缺色 A 的 severity 必须为 ''，实际为 '{sevs['A']}'"

        # 4. 放行断言
        if not sevs:
            assert note == "审查通过", f"Task #{tid} 无缺陷但 note 不为 '审查通过': {note}"

    print("[PASS] 100% 规则契约与反抽象代词断言核验通过！")

def main():
    validate_reviews(REVIEWS_B31)

    base_dir = r"d:\学业文件\MCL\上色评价_数据集标注\LS_lcad_reviewer"
    intermediate_dir = os.path.join(base_dir, "intermediate")
    all_export_path = os.path.join(base_dir, "exports", "reviewed_1_10000_all.json")
    clean_export_path = os.path.join(base_dir, "exports", "reviewed_1_10000_clean.json")
    grounding_out_path = os.path.join(intermediate_dir, "audits", "grounding_remaining_batch_31.json")

    # 1. 导出中间定物字典
    with open(grounding_out_path, "w", encoding="utf-8") as f:
        json.dump(REVIEWS_B31, f, ensure_ascii=False, indent=2)
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

    for tid, r in REVIEWS_B31.items():
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
