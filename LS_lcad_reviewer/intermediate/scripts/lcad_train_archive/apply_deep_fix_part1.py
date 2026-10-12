#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_deep_fix_part1.py
将 Part 1 (57 例高危样本，涵盖 Batch 1 与 Batch 3) 的大图视觉细致核验成果
精准更新至 exports/reviewed_1_10000_all.json 与 exports/reviewed_1_10000_clean.json 中。
消灭抽象代词，严格实体定物，修复 Task 1 餐盒错色、Task 1179 纯黑白漏检熔断等硬伤。
"""

import json
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"
ALL_FILE = EXPORTS_DIR / "reviewed_1_10000_all.json"
CLEAN_FILE = EXPORTS_DIR / "reviewed_1_10000_clean.json"

# Part 1 视觉大图细致直审改判字典 (57 例)
# 格式: task_id -> {score, defects: [{id, name, severity, description}], note}
PART1_REVIEWS = {
    # Sheet 01
    1: {
        "score": 2.5,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "下方盛放西兰花与肉丸的明黄色塑料餐盒被错误涂为草绿色，与西兰花蔬菜颜色发生语义蔓延错配。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "草绿色餐盒边缘与西兰花边界色彩过渡粘连生硬，容器塑料质感略显失真。"}
        ],
        "note": "核查发现：下方明黄色塑料餐盒严重错色涂为草绿色(C-L2)；容器边界色阶轻度生硬(F-L1)。"
    },
    23: {
        "score": 2.2,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "右下角草坪翠绿生机被彻底剥夺，完全脱色蜕变惨白浅灰色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "马匹皮毛与全景画面轻度偏冷青蓝调。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "草地脱色区域与主体明暗对比失真。"}
        ],
        "note": "核查发现：右下角翠绿草坪完全脱色蜕变惨白浅灰(E2-L2)；全图轻微偏冷青蓝调(D-L1)。"
    },
    31: {
        "score": 1.5,
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "会议室暖黄木质墙壁与窗帘被大幅度错涂为阴冷惨白的青蓝冷调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "参会人员面部肤色发青苍白，严重欠饱和脱色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "冷青色调笼罩全屋，呈现诡异阴森失真感。"}
        ],
        "note": "核查发现：会议室暖黄墙壁与窗帘严重偏冷青蓝调(D-L2)；人物肤色脱色发青(E2-L2, F-L2)。"
    },
    34: {
        "score": 2.2,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "猫咪右侧原本清爽的浅天蓝色行李箱完全褪色发灰，丧失色彩活力。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "画面整体暗部色温轻微偏暖红黄调。"}
        ],
        "note": "核查发现：右侧浅天蓝行李箱严重欠饱和褪色发灰(E2-L2)；全图轻度偏暖红黄调(D-L1)。"
    },
    36: {
        "score": 1.5,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "温馨暖黄实木地板与窗外绿植完全被剥夺生机，大面积脱色为阴冷死黑灰硬地。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "客厅全景系统性偏冷青蓝死灰调。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "地板和家具丧失原木温润质感，整体视觉灰暗死寂。"}
        ],
        "note": "核查发现：温馨暖黄实木地板完全脱色为死灰硬地(E2-L3)；全屋偏冷青蓝调(D-L2, F-L2)。"
    },
    49: {
        "score": 2.2,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "长椅周围铺满的金黄落叶沙土地面严重脱色，泛出冰冷死灰土泥色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "树林林地轻度偏冷青蓝调。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "林地自然暖意丧失，地表色阶过渡生硬。"}
        ],
        "note": "核查发现：长椅周围金黄落叶地面严重欠饱和脱色(E2-L2)；全图轻微偏冷青蓝调(D-L1)。"
    },

    # Sheet 02
    50: {
        "score": 1.5,
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L3", "description": "林间小道与绿树全景遭受恶性火炉烘烤，暴烈错涂为刺目焦黄猩红色温。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "道路与行人体表红色与橙黄高光严重过饱和溢出。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "全图严重失真变色，如同烈火燃烧般的非现实视觉假象。"}
        ],
        "note": "核查发现：全景遭受恶性火炉烘烤偏暖红黄调(D-L3)；林地与人物刺目过饱和(E1-L2, F-L2)。"
    },
    58: {
        "score": 1.5,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "两辆经典标志性明黄色校车车身黄色被彻底剥夺，错误褪色涂为惨白灰白色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "校车涂装整体严重欠饱和发白发灰，形同报废褪色车辆。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "公共校车标志性黄黑配色丧失，视觉辨识度严重受损。"}
        ],
        "note": "核查发现：经典明黄色校车完全脱色褪白为灰白老车(C-L2, E2-L3, F-L2)。"
    },
    59: {
        "score": 2.4,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "笔记本电脑右侧温暖大面积粉红毛毯完全脱色变惨白死灰。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内书桌与电脑区域轻微偏冷青蓝调。"}
        ],
        "note": "核查发现：右侧大面积粉红毛毯完全脱色变惨白灰死(E2-L2)；全图轻微偏冷青蓝调(D-L1)。"
    },
    64: {
        "score": 2.3,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "野外开阔草坡整体严重欠饱和发暗发灰，背景绿树丧失葱郁生机。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "草地全景轻度偏冷青蓝调。"}
        ],
        "note": "核查发现：野外开阔草坡与绿林整体严重欠饱和发暗发灰(E2-L2)；轻度偏冷青蓝调(D-L1)。"
    },
    65: {
        "score": 2.3,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "槌球草坪生机翠绿褪色发暗发黄，青年男子蓝绿运动衫脱色退化灰白汗衫。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "右侧女士红色短袖脱色发暗，全景轻度偏冷青蓝调。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "草坪与人物衣物色彩干枯失真。"}
        ],
        "note": "核查发现：槌球草坪与蓝绿运动衫严重欠饱和脱色(E2-L2)；全图轻度偏冷青蓝调(D-L1)。"
    },
    71: {
        "score": 2.5,
        "defects": [
            {"id": "B", "name": "溢色", "severity": "L2", "description": "蛋糕表面红色 Amelie 草写字母边框颜色严重越界渗漏污染蛋糕浅绿底座。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "翻糖蛋糕绿色海浪与红色字体过于浓艳刺眼，高光溢出。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "甜品边缘颜色渗透，呈现生硬塑料感。"}
        ],
        "note": "核查发现：蛋糕红色字体边缘严重溢色侵染底座(B-L2)；绿浪与红字过于浓艳刺眼(E1-L2)。"
    },

    # Sheet 03
    82: {
        "score": 1.5,
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "酒店卧室温馨金黄床头灯光与温暖被褥被系统性错涂为阴暗死灰青蓝冷调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "卧室布艺床罩与床头靠背色彩严重暗淡脱色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "暖意全无，环境色温严重违和失真。"}
        ],
        "note": "核查发现：酒店卧室温馨灯光与床铺严重偏冷青蓝调(D-L2)；床罩欠饱和脱色(E2-L2, F-L2)。"
    },
    92: {
        "score": 2.3,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "生锈铁剪刀周围暖黄色展台与玻璃器皿严重欠饱和发暗发灰。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "陈列台面暗部轻度偏冷青蓝调。"}
        ],
        "note": "核查发现：玻璃器皿与展台整体严重欠饱和发灰褪色(E2-L2)；轻度偏冷青蓝调(D-L1)。"
    },
    95: {
        "score": 2.3,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "撑伞女子身穿的鲜亮桃粉色外套被严重脱色错涂为发暗的灰褐杂色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "女子面部原本健康的红润肤色完全褪去，面无血色惨白发灰。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "画面整体色彩泛冷偏青。"}
        ],
        "note": "核查发现：撑伞女子桃粉色外套脱色为暗灰褐(C-L2)；肤色欠饱和苍白发灰(E2-L2)。"
    },
    98: {
        "score": 2.4,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "骑车男子下身鲜蓝牛仔裤严重脱色发灰，身后草坡金黄生机干枯。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "骑行场景全图轻微偏冷青蓝调。"}
        ],
        "note": "核查发现：男子牛仔裤严重脱色发灰(E2-L2)；骑行草坡色彩干枯偏冷灰(D-L1)。"
    },
    100: {
        "score": 2.5,
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "棒球内场平整红土地面颜色过于鲜红刺眼，草坪与红土边缘高光溢出。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "球场地面与看台边缘界限分明，色阶过渡生硬。"}
        ],
        "note": "核查发现：棒球场内场红土地面过于浓艳刺眼(E1-L2)；草地与红土过渡生硬(F-L1)。"
    },
    114: {
        "score": 2.5,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "餐桌右上方原本鲜艳的明黄色清洁布完全褪色泛白为苍白抹布。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "餐盘酱汁与桌面色彩对比失调，呈现发暗油腻感。"}
        ],
        "note": "核查发现：餐桌右上方明黄色清洁布严重脱色泛白(E2-L2)；餐盘色调略显生硬(F-L1)。"
    },

    # Sheet 04
    119: {
        "score": 1.5,
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L3", "description": "林地摩托车全景遭受到恶性冷青绿色渲染，林地树木与地面全被染成刺眼霉绿冷调。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "整幅画面色彩失真怪异，丧失自然风光可信度。"}
        ],
        "note": "核查发现：全景遭受恶性偏冷青绿调渲染(D-L3)；摩托车周围林地严重失真(F-L2)。"
    },
    134: {
        "score": 2.3,
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "近景白衬衫男子面容与衣物大面积泛阴冷青蓝偏色，暖调氛围被毁。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "背景青年男女服饰色彩发暗欠饱和。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "肤色冷暖过渡断层失真。"}
        ],
        "note": "核查发现：白衬衫男子面部与衣着明显泛青蓝冷偏色(D-L2)；背景欠饱和(E2-L1)。"
    },
    143: {
        "score": 2.2,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "清澈通透的蔚蓝天空被严重脱色错涂为暗沉阴冷的深灰发白阴霾天幕。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "放风筝人物衣物与天空整体严重欠饱和发暗。"}
        ],
        "note": "核查发现：纯净蔚蓝天空严重脱色退化为阴冷灰白天幕(C-L2, E2-L2)。"
    },
    146: {
        "score": 2.3,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "右侧女士身穿的鲜艳亮粉红礼服外套被严重脱色错涂为灰暗无生机的土灰杂色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "泰迪熊玩偶皮毛与左侧女士衣服大面积发灰褪色。"}
        ],
        "note": "核查发现：右侧女士亮粉红礼服脱色为暗土灰色(C-L2)；玩偶与服饰严重欠饱和(E2-L2)。"
    },
    162: {
        "score": 2.2,
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "夜间卧室温馨暖黄照明被错涂为阴暗死灰的青蓝冷调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "白色床单与室内木质家具欠饱和暗沉。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "屏幕蓝光与室内环境色阶过渡割裂。"}
        ],
        "note": "核查发现：夜间卧室暖黄氛围严重偏冷青蓝调(D-L2)；床铺与家具发暗欠饱和(E2-L2)。"
    },
    164: {
        "score": 2.0,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "果盘中明黄香蕉被恶性烘烤错涂为发焦暗红色，墙面砖石与橱柜暴烈泛焦红。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "红色水果与室内木柜色彩浓艳刺目，高光严重溢出。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "全景系统性偏暖红黄调严重。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "室内宛如烤炉，色彩失真生硬。"}
        ],
        "note": "核查发现：黄色水果被恶性错涂为焦暗红色(C-L2)；室内大面积焦红过饱和偏色(E1-L2, D-L2)。"
    },

    # Sheet 05
    171: {
        "score": 2.4,
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "酒店卧室床头暖黄色调被冲淡，全图暗部轻度偏冷青蓝调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "床铺米黄被罩与床头壁画色彩轻度暗淡发灰。"}
        ],
        "note": "核查发现：酒店卧室暖黄照明偏冷青蓝调(D-L1)；床品轻度欠饱和(E2-L1)。"
    },
    178: {
        "score": 1.0,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "棒球投手标志性鲜艳大红球帽与大红长袖内衬被彻底剥夺红色，恶性错涂为深黑发黄杂色。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "投手身后平展翠绿草坪被彻底剥夺绿色，恶性错涂为一片枯死的土黄荒地。"},
            {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "球帽、衣物与草地核心色彩全域崩溃脱色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "原图鲜明生机被彻底破坏，呈现荒诞错配感。"}
        ],
        "note": "核查发现：大红球帽与内衬恶性错涂为深黑黄褐(C-L3)；翠绿草地错涂枯死土黄荒地(C-L2, E2-L3)。"
    },
    191: {
        "score": 2.5,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "水边海鸥羽毛与周围水色轻度欠饱和发暗发灰。"}
        ],
        "note": "核查发现：水边海鸥羽毛与近景地面轻度欠饱和褪色(E2-L1)。"
    },
    205: {
        "score": 2.2,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街角醒目的洋红粉色停车指示标牌完全褪色发灰为暗土杂色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "墙体与自行车车身轻度偏冷青蓝调。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "指示牌字迹辨识度下降，色彩生硬。"}
        ],
        "note": "核查发现：街角洋红指示标牌严重脱色褪淡(E2-L2)；自行车与墙面偏冷青蓝调(D-L1)。"
    },
    214: {
        "score": 1.5,
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L3", "description": "滑板街道全景被暴烈错涂为发青发蓝的刺目冷青绿调，欧式建筑完全变色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "青色高光在地面与消火栓上严重溢出刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "整个户外场景宛如水下阴冷世界，真实感彻底丧失。"}
        ],
        "note": "核查发现：滑板街景遭受恶性青绿冷偏色错涂(D-L3)；建筑与街道刺目过饱和(E1-L2, F-L2)。"
    },
    224: {
        "score": 2.2,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "幼童与父亲面部原本健康红润的肤色严重脱色，泛出病态苍白灰暗。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "人像背景轻度偏冷青蓝调。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "人物肤色质感塑料发灰，缺乏生机活力。"}
        ],
        "note": "核查发现：幼童与父亲肤色严重欠饱和脱色苍白(E2-L2)；画面轻度偏冷青蓝调(D-L1)。"
    },

    # Sheet 06
    231: {
        "score": 2.3,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "餐桌右侧浅天蓝饮料瓶与蛋糕边缘严重欠饱和脱色发暗。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "餐盘阴影轻度偏冷青蓝调。"}
        ],
        "note": "核查发现：天蓝饮料瓶与蛋糕色彩欠饱和褪色发灰(E2-L2)；轻度偏冷青蓝调(D-L1)。"
    },
    241: {
        "score": 2.4,
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "红木橱柜色温轻微偏暖红黄调，暗部色阶微浮。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "双门冰箱表面金属光泽过渡略生硬。"}
        ],
        "note": "核查发现：红木橱柜色温偏暖红黄调(D-L1)；冰箱金属质感略微生硬(F-L1)。"
    },
    246: {
        "score": 2.0,
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "红砖街景与路面遭受恶性暖红洋紫染色，柏油路面被错涂为刺眼红紫色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "双层巴士车身与街角建筑红色过饱和溢出。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "路面发紫失真，环境真实感明显受损。"}
        ],
        "note": "核查发现：街道与沥青路面严重偏洋红紫调(D-L2)；巴士与建筑红砖过饱和(E1-L2)。"
    },
    248: {
        "score": 2.4,
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "复古电视机屏幕内圣诞树彩灯高光刺目溢出，过饱和严重。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "屏幕与黑猫边缘高光过于突兀失真。"}
        ],
        "note": "核查发现：电视屏幕内部圣诞彩灯严重过饱和刺目(E1-L2)；边缘过渡生硬(F-L1)。"
    },
    258: {
        "score": 2.2,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "原本温润的木质鼠标垫与书本完全褪色，全图发青发灰欠饱和。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "画面整体暗部偏冷青蓝调。"}
        ],
        "note": "核查发现：木质鼠标垫与书页严重欠饱和褪色(E2-L2)；全图偏冷青蓝调(D-L1)。"
    },
    274: {
        "score": 2.2,
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "探头骏马红褐色毛皮过于刺眼浓艳，马头过饱和溢出。"},
            {"id": "B", "name": "溢色", "severity": "L1", "description": "小女孩黄色短袖与木门边框处颜色溢出。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "骏马皮毛呈现塑料反光质感。"}
        ],
        "note": "核查发现：马头红褐毛皮浓艳过饱和(E1-L2)；女孩短袖边框轻度溢色(B-L1)。"
    },

    # Sheet 07
    278: {
        "score": 2.2,
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "卫生间暖木色洗手台与瓷砖被错涂为阴暗死灰的冷青蓝紫调。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "室内色温阴森违和，卫浴洁净感丧失。"}
        ],
        "note": "核查发现：卫生间洗手台与瓷砖严重偏冷青蓝调(D-L2)；色温阴暗失真(F-L1)。"
    },
    293: {
        "score": 2.3,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "红色运动鞋周围原本生机勃勃的翠绿草坪完全枯萎褪色为死灰黄草地。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "全景暗部轻微偏冷青蓝调。"}
        ],
        "note": "核查发现：运动鞋周围翠绿草坪严重脱色为死灰草地(E2-L2)；轻度偏冷青蓝调(D-L1)。"
    },
    320: {
        "score": 2.2,
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "轮滑少年脚部全景遭受浓重洋红橙黄染色，牛仔裤发暗发红。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "地面暖色高光轻度过饱和。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "运动鞋边缘轮廓色阶粘连。"}
        ],
        "note": "核查发现：轮滑少年脚部与地面严重偏洋红暖调(D-L2)；高光轻度过饱和(E1-L1)。"
    },
    325: {
        "score": 2.0,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "斑马原本清晰分明的黑白相间条纹被严重错涂为发暗的深蓝紫色伪色条纹。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "草原翠绿草坪严重欠饱和脱色，变枯干暗草地。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "斑马身躯色彩斑驳，违背自然常态。"}
        ],
        "note": "核查发现：斑马黑白条纹恶性错涂为深蓝紫色伪色(C-L2)；草坪严重欠饱和脱色(E2-L2)。"
    },
    328: {
        "score": 2.4,
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "炒菜蔬菜翠绿叶片过于浓艳刺目，高光泛白泛荧光，过饱和明显。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "食物质感略显生硬塑料。"}
        ],
        "note": "核查发现：炒菜翠绿蔬菜浓艳刺目过饱和(E1-L2)；食物质感略显塑料失真(F-L1)。"
    },
    352: {
        "score": 1.5,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "开放式餐厅正中央标志性明黄色料理工作台面被彻底剥夺黄色，错涂为惨白的冷灰白色金属台。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "厨房整体氛围偏冷青灰暗调，暖光被扑灭。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "料理台与橱柜大面积色彩暗淡脱色。"}
        ],
        "note": "核查发现：标志性明黄工作台面被彻底错涂为惨白冷灰(C-L2, E2-L2)；全景偏冷青暗调(D-L2)。"
    },

    # Sheet 08
    392: {
        "score": 2.2,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "夜景中醒目大红八角形 STOP 标志及周围建筑发暗欠饱和，色彩枯淡。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "夜空与街道阴影轻度偏冷青蓝调。"}
        ],
        "note": "核查发现：大红STOP停牌欠饱和褪色发暗(E2-L2)；夜景轻度偏冷青蓝调(D-L1)。"
    },
    393: {
        "score": 2.3,
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "烤香肠与肉饼表面红色过于浓艳刺眼，高光严重溢出。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "食物边框与餐盘交界生硬。"}
        ],
        "note": "核查发现：餐盘中烤肠与肉丸红色浓艳过饱和(E1-L2)；食物边框过渡生硬(F-L1)。"
    },
    394: {
        "score": 1.8,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "母子共进晚餐中，母亲的右上臂皮肤被大面积恶性错涂为惊悚的鲜艳荧光大红橙伪色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "大披萨表面番茄酱与香肠浓艳发光，高光溢出。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "手臂惊悚红斑与幼儿肤色割裂，极度不自然。"}
        ],
        "note": "核查发现：母亲手臂皮肤被恶性错涂为荧光大红橙(C-L2)；披萨浓艳过饱和(E1-L2, F-L2)。"
    },
    399: {
        "score": 1.8,
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "白色键盘与桌面全景泛出浓重刺目的洋红粉紫与高饱和色偏。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "键盘按键表面洋红色光芒过饱和溢出。"},
            {"id": "B", "name": "溢色", "severity": "L1", "description": "键帽边缘粉红色泽扩散渗漏到周围按键缝隙。"}
        ],
        "note": "核查发现：键盘全景严重偏洋红粉紫调(D-L2)；高光过饱和溢出(E1-L2, B-L1)。"
    },
    420: {
        "score": 2.2,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "棒球击球手脚下的生机翠绿草坪大面积脱色褪变为枯黄暗泥草地。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "红土内场与看台阴影轻度偏冷青蓝调。"}
        ],
        "note": "核查发现：球场翠绿草坪大面积严重欠饱和脱色(E2-L2)；画面轻度偏冷青蓝调(D-L1)。"
    },
    440: {
        "score": 2.2,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "水边棕熊温润厚重的棕红毛皮在背部被严重错涂为发暗的阴冷死灰蓝紫伪色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "草丛与水体环境色偏冷。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "熊背部毛发色彩死寂，与健康皮毛反差明显。"}
        ],
        "note": "核查发现：棕熊背部皮毛被恶性错涂为阴冷死灰蓝紫色(C-L2)；全景轻度偏冷(D-L1)。"
    },

    # Sheet 09
    460: {
        "score": 2.3,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "雪原晚霞原本温暖的红橙霞光完全褪色，全景严重欠饱和呈现冰冷死灰。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "雪地暗部与汽车车身轻度偏冷青蓝调。"}
        ],
        "note": "核查发现：雪原晚霞红橙光芒完全脱色(E2-L2)；全景欠饱和偏冷灰(D-L1)。"
    },
    463: {
        "score": 2.2,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "大红 STOP 停牌下方的经典蓝底 MAIN ST 路牌被严重错涂褪色为发脏的黄绿色伪色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "晴朗蓝天明显泛冷青绿偏色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "路牌字迹边缘色彩渗透，辨识度受损。"}
        ],
        "note": "核查发现：蓝底MAIN ST路牌恶性错涂为发脏黄绿伪色(C-L2)；蓝天泛青绿偏色(D-L1)。"
    },
    470: {
        "score": 2.0,
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "航空博物馆展厅温馨暖黄照明被彻底扑灭，全馆遭受阴森冰冷的惨白青灰色调浸染。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "展品机翼两侧星条旗红白条纹欠饱和严重褪色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "大型飞机展厅色温阴森违和。"}
        ],
        "note": "核查发现：航空博物馆展厅暖黄光彻底被青冷灰色扑灭(D-L2)；国旗色彩脱色(E2-L2)。"
    },
    472: {
        "score": 2.2,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "并排四只泰迪熊中，第三只鲜艳亮粉红小熊完全脱色错涂为暗沉发脏的黄灰色老熊。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "毛绒玩具整体欠饱和发暗发灰。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "粉色玩具熊脱色失真，破坏四色对比序列。"}
        ],
        "note": "核查发现：亮粉红泰迪熊恶性脱色错涂为发脏黄灰小熊(C-L2)；全景欠饱和(E2-L2)。"
    },
    482: {
        "score": 2.0,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "翻糖小火车蛋糕原本清淡的浅天蓝微绿车身被恶性错涂为刺眼发光的鲜艳荧光草绿色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "小火车车身浓绿釉面高光严重过饱和溢出。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "甜品色彩塑料失真，失去自然奶油质感。"}
        ],
        "note": "核查发现：浅天蓝小火车车身被严重错涂为发光荧光草绿(C-L2)；浓艳过饱和(E1-L2)。"
    },
    490: {
        "score": 2.2,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "餐桌两个白色蛋糕盘外围原本鲜明的纯深蓝色装饰圆环被严重错涂为鲜艳刺眼的洋红粉紫色伪色环。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "草莓点缀发暗，餐盘伪色环与整体环境反差突兀。"}
        ],
        "note": "核查发现：蛋糕盘纯深蓝边环被恶性错涂为刺眼洋红粉紫环(C-L2)；草莓发暗(F-L1)。"
    },

    # Sheet 10
    491: {
        "score": 2.3,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L1", "description": "电脑显示屏原本清爽的青绿自然壁纸被错涂为发暗的灰红粉紫界面。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "桌面与全屋灯光轻度偏暖红黄调。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "屏幕显示内容受环境光溢色侵染。"}
        ],
        "note": "核查发现：电脑青绿桌面壁纸错涂发暗灰红粉紫(C-L1)；全图偏暖红黄调(D-L1)。"
    },
    498: {
        "score": 2.0,
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "石屋厨房全景系统性偏冷青蓝死灰调，原木吊柜被扑灭暖色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "右侧深海蓝橱柜门板高光刺目溢出。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "石壁纹理阴冷失真，居住温馨感破坏。"}
        ],
        "note": "核查发现：石屋厨房全景严重偏冷青蓝调(D-L2)；深蓝柜门过饱和刺目(E1-L1)。"
    },
    1179: {
        "score": 1.0,
        "defects": [
            {"id": "A", "name": "缺色", "severity": "", "description": "全域上色彻底失败，图像呈现纯灰阶黑白状态，无任何有效色彩信息渲染，触发全局熔断。"}
        ],
        "note": "核查确证：全域上色彻底失败，图像呈现纯灰阶黑白状态(命中A项缺色熔断，总分锁定1.0)。"
    }
}

def main():
    print(f"Loading {ALL_FILE.name}...")
    with open(ALL_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    print(f"Loading {CLEAN_FILE.name}...")
    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    anns_all = all_data["annotations"]
    anns_clean = clean_data["annotations"]

    updated_count = 0

    for ann_a, ann_c in zip(anns_all, anns_clean):
        tid = ann_a["human_review"]["task_id"]
        if tid in PART1_REVIEWS:
            rev = PART1_REVIEWS[tid]
            
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

    print(f"Updated {updated_count} high-risk items in memory.")

    with open(ALL_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"Saved: {ALL_FILE.name}")

    with open(CLEAN_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"Saved: {CLEAN_FILE.name}")

    print("\n[SUCCESS] Part 1 deep fix successfully applied to all exports!")

if __name__ == "__main__":
    main()
