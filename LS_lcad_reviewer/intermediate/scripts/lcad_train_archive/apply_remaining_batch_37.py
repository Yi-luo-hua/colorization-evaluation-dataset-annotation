# -*- coding: utf-8 -*-
"""
应用 Batch 37 审核具象定物判决字典并双向同步至正式交付文件
Batch 37: Task #7399 ~ #7564 (共 120 组)
"""

import json
import os
import re

# 120 组人工直审与具象定物判决字典
REVIEWS_B37 = {
    # Sheet 01
    7399: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7400: {
        "score": 5.0,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "动物园岩石斜坡与后方背光岩壁色彩略显欠饱和偏灰暗，缺乏岩石原本青绿青灰层次(E2-L1, F-L1)。"
    },
    7401: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7402: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7404: {
        "score": 2.47,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "客厅左侧单人沙发与室内地板木纹大面积浸染过度浓艳的焦糖红黄暖偏色，色彩轻度过饱和(D-L1, E1-L1)。"
    },
    7406: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 02
    7407: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7408: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7410: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "草地上的复古铸铁消防栓柱身表面大面积浸染过于浓艳的粉红暖偏色，色彩轻度过饱和(D-L1, E1-L1)。"
    },
    7411: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7413: {
        "score": 2.47,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "实木吧台吊顶木梁表面浸染过度浓艳的焦糖红黄暖偏色，色彩轻度过饱和(D-L1, E1-L1)。"
    },
    7414: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 03
    7415: {
        "score": 2.43,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "手持红葡萄酒瓶的手腕皮肤与酒标纸张在室内顶灯下略显欠饱和偏冷青灰暗淡(D-L1, E2-L1)。"
    },
    7417: {
        "score": 2.47,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "刷牙婴儿的面颊皮肤与后方背景墙面完全丧失原本温暖光照，大面积严重偏向冰冷泛青暗灰偏色(D-L1, E2-L1, F-L1)。"
    },
    7418: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7420: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7421: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7422: {
        "score": 2.23,
        "severities": {"C": "L2", "D": "L1", "F": "L1"},
        "note": "长颈鹿身后的茂密树冠由原本葱郁的翠绿色被严重错涂为枯黄焦褐色，自然季节感失真（错色 C-L2）(C-L2, D-L1, F-L1)。"
    },

    # Sheet 04
    7423: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7424: {
        "score": 1.07,
        "severities": {"C": "L2", "D": "L2", "E1": "L2", "F": "L2"},
        "note": "餐盘中盛放的烤鱼表面大面积浸染刺眼失真的荧光粉红偏色，鱼肉焦香金黄质感完全丧失(C-L2, D-L2, E1-L2, F-L2)。"
    },
    7425: {
        "score": 2.36,
        "severities": {"D": "L1", "F": "L1"},
        "note": "废墟中废弃马桶陶瓷内壁与排污管道暗部浸染失真的红紫杂色斑块(D-L1, F-L1)。"
    },
    7426: {
        "score": 2.06,
        "severities": {"C": "L2", "D": "L1", "E1": "L2", "F": "L2"},
        "note": "塑料餐盒内分装的水果切块与坚果大面积浸染刺眼失真的荧光粉紫偏色，全图色调严重失真(C-L2, D-L1, E1-L2, F-L2)。"
    },
    7427: {
        "score": 2.73,
        "severities": {"C": "L2", "E2": "L2", "F": "L2"},
        "note": "铁路轨道上行驶的内燃机车车头亮橙色涂装大面积欠饱和脱色为暗沉红褐色，标志性车头色彩严重衰减（错色 C-L2）(C-L2, E2-L2, F-L2)。"
    },
    7428: {
        "score": 4.46,
        "severities": {"C": "L1", "D": "L1", "F": "L1"},
        "note": "客舱洗手间马桶坐便盖板由红棕木纹被错涂为暗焦黄色，坐便盆内壁微泛杂色(C-L1, D-L1, F-L1)。"
    },

    # Sheet 05
    7429: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7430: {
        "score": 2.12,
        "severities": {"C": "L2", "D": "L2", "E2": "L2", "F": "L2"},
        "note": "卫生间暖黄瓷砖墙面与三花猫金黄背毛被严重脱色错涂为冰冷惨白的青白死灰，猫咪毛色与室内温馨氛围彻底丧失（严重错色 C-L2）(C-L2, D-L2, E2-L2, F-L2)。"
    },
    7431: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    7432: {
        "score": 2.36,
        "severities": {"D": "L1", "E1": "L2", "F": "L2"},
        "note": "夜间车站轻轨列车与铁轨周围大面积浸染刺眼浓艳的紫红光晕与过饱和偏色，夜景自然度严重受损(D-L1, E1-L2, F-L2)。"
    },
    7433: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7434: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 06
    7436: {
        "score": 2.73,
        "severities": {"D": "L1", "E1": "L2", "F": "L1"},
        "note": "复古黑胶唱机翻盖内衬表面大面积浸染过于浓艳刺眼的鲜红偏色，色彩轻度过饱和(D-L1, E1-L2, F-L1)。"
    },
    7437: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7438: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7440: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7441: {
        "score": 1.05,
        "severities": {"C": "L2", "D": "L2", "E2": "L2", "F": "L2"},
        "note": "广场欧式古典建筑大理石外墙与后方施工塔吊大面积欠饱和脱色错涂为暗淡青灰死色，温暖阳光氛围完全丧失（严重错色 C-L2）(C-L2, D-L2, E2-L2, F-L2)。"
    },
    7442: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 07
    7443: {
        "score": 2.36,
        "severities": {"B": "L1", "D": "L1", "F": "L1"},
        "note": "夜间路边立着的水泥电线杆柱身表面浸染失真的蓝紫色偏色，边缘轻微溢色(B-L1, D-L1, F-L1)。"
    },
    7444: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "棒球击球手后方防护铁丝网与球员休息席在强光下略显偏红偏浓，草坪色差微弱(D-L1, F-L1)。"
    },
    7447: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7451: {
        "score": 2.47,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "托起芭蕉的人手掌心皮肤大面积浸染失真浓艳的红粉暖偏色，肤色略显过饱和(D-L1, E1-L1, F-L1)。"
    },
    7453: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7454: {
        "score": 2.17,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "机场停机坪客机机身暗部与背景天空大面积欠饱和偏冷青灰暗淡(D-L1, E2-L1)。"
    },

    # Sheet 08
    7455: {
        "score": 4.55,
        "severities": {"B": "L1", "D": "L1", "F": "L1"},
        "note": "室内窗边悬挂的布艺窗帘边缘发生轻微溢色，暗部微泛红紫杂色偏色(B-L1, D-L1, F-L1)。"
    },
    7459: {
        "score": 2.47,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "宽敞室内空间地面与远端墙面大面积丧失温暖阳光质感，呈现深冷青灰暗淡偏色(D-L1, E2-L1, F-L1)。"
    },
    7460: {
        "score": 2.56,
        "severities": {"E1": "L1"},
        "note": "道路旁草坪与灌木绿意略显过于浓艳刺眼，色彩轻度过饱和(E1-L1)。"
    },
    7461: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "早餐餐桌实木桌面与煎蛋餐盘边缘完全丧失温暖红棕暖色，大面积偏向冰冷泛青暗灰偏色(D-L1, E2-L1, F-L1)。"
    },
    7462: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7463: {
        "score": 5.0,
        "severities": {"C": "L3", "E2": "L2", "F": "L2"},
        "note": "露天餐厅就座男子所穿的鲜红色短袖T恤被彻底脱色错涂为暗沉灰黑色，背景红砖墙亦褪色发暗（严重错色 C-L3）(C-L3, E2-L2, F-L2)。"
    },

    # Sheet 09
    7464: {
        "score": 5.0,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "街道上行驶的公交车侧身红色广告横幅大面积欠饱和脱色发暗，车身艳丽度明显衰减(E2-L1, F-L1)。"
    },
    7466: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7469: {
        "score": 1.20,
        "severities": {"C": "L2", "D": "L2", "E2": "L2", "F": "L2"},
        "note": "大草原地表草坪与长颈鹿斑纹大面积严重欠饱和脱色错涂为灰白死色，画面生机严重丧失（严重错色 C-L2）(C-L2, D-L2, E2-L2, F-L2)。"
    },
    7470: {
        "score": 4.17,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "卫生间浅色墙面与木质洗手台面完全丧失原本温暖暖黄光晕，整体大面积偏向冷青暗灰偏色(D-L1, E2-L1, F-L1)。"
    },
    7471: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L1", "F": "L1"},
        "note": "路边设立的金属停车计时器外壳原本青蓝色漆面大面积欠饱和脱色为暗沉金属灰（错色 C-L2）(C-L2, E2-L1, F-L1)。"
    },
    7472: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 10
    7474: {
        "score": 2.27,
        "severities": {"D": "L1", "E1": "L2", "F": "L2"},
        "note": "室内展台摆放的和风折扇与工艺雨伞大面积浸染刺眼浓艳的洋红紫红荧光偏色，全图色调严重失真(D-L1, E1-L2, F-L2)。"
    },
    7476: {
        "score": 2.23,
        "severities": {"B": "L1", "C": "L3", "F": "L2"},
        "note": "白色砧板上原本切碎的鲜绿色蔬菜被颠覆性错涂为深艳紫甘蓝杂色，砧板边缘严重溢色渗透（严重错色 C-L3）(B-L1, C-L3, F-L2)。"
    },
    7477: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7478: {
        "score": 1.34,
        "severities": {"C": "L2", "D": "L2", "E2": "L2", "F": "L2"},
        "note": "卫生间原本温馨暖黄的墙壁乳胶漆被大面积严重脱色错涂为冰冷惨白的青白死灰，室内氛围严重失真（严重错色 C-L2）(C-L2, D-L2, E2-L2, F-L2)。"
    },
    7479: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7480: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 11
    7481: {
        "score": 2.61,
        "severities": {"D": "L1", "E1": "L2", "F": "L1"},
        "note": "农场女子牵引的小马身躯毛皮大面积浸染过于浓艳刺眼的亮焦糖红黄偏色，色彩明显过饱和(D-L1, E1-L2, F-L1)。"
    },
    7482: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "棒球场本垒击球手白色球服暗部与后方红土跑道色彩略显偏红偏深(D-L1, F-L1)。"
    },
    7483: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7484: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7485: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7487: {
        "score": 4.55,
        "severities": {"C": "L1", "D": "L1", "E2": "L1", "F": "L1"},
        "note": "室内滑板场地表木质滑板坡道大面积欠饱和脱色为暗淡冷灰白，木质温暖感明显受损(C-L1, D-L1, E2-L1, F-L1)。"
    },

    # Sheet 12
    7488: {
        "score": 4.46,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "吹风机吹头发男子面部皮肤与室内背景墙壁完全丧失原本温暖光晕，大面积偏向冰冷泛青暗灰偏色(D-L1, E2-L1, F-L1)。"
    },
    7489: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7490: {
        "score": 2.47,
        "severities": {"D": "L1", "F": "L1"},
        "note": "电脑办公桌上笔记本键盘与屏幕显示区域浸染失真的紫红冷色偏色(D-L1, F-L1)。"
    },
    7492: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7494: {
        "score": 2.61,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "大草原地表草甸与长颈鹿身躯斑纹大面积浸染过度浓艳的焦糖橙黄暖偏色，色彩轻度过饱和(D-L1, E1-L1)。"
    },
    7495: {
        "score": 5.0,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "网球场挥拍女孩的网球拍红色边框及服饰色彩略显欠饱和偏深暗(E2-L1, F-L1)。"
    },

    # Sheet 13
    7497: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7499: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7501: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7502: {
        "score": 4.46,
        "severities": {},
        "note": "审查通过"
    },
    7503: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "玄关更衣柜木质门框与室内暖光照明大面积丧失温暖色泽，呈现冰冷泛青暗灰偏色(D-L1, E2-L1, F-L1)。"
    },
    7505: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 14
    7506: {
        "score": 2.17,
        "severities": {"D": "L1", "E1": "L2", "F": "L2"},
        "note": "老式电视机屏幕转播棒球画面大面积浸染刺眼失真的紫红荧光与过饱和偏色，转播画质严重失真(D-L1, E1-L2, F-L2)。"
    },
    7507: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    7508: {
        "score": 2.36,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "客厅室内墙壁与沙发面料大面积浸染过度浓艳的焦糖红黄暖偏色，圣诞树周围色彩轻度过饱和(D-L1, E1-L1, F-L1)。"
    },
    7509: {
        "score": 2.17,
        "severities": {"D": "L1", "E1": "L2", "F": "L1"},
        "note": "全自动甜甜圈炸制机不锈钢外壳与油锅内部浸染过于浓烈刺眼的红橙暖偏色，色彩严重过饱和(D-L1, E1-L2, F-L1)。"
    },
    7510: {
        "score": 2.56,
        "severities": {"C": "L1", "F": "L1"},
        "note": "街头骑警所穿的高反光巡逻背心荧光绿微显偏黄，马匹鬃毛暗部略显偏深(C-L1, F-L1)。"
    },
    7512: {
        "score": 2.43,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "三联屏电脑桌背景墙面与显示器高光边缘浸染失真的洋红紫冷色偏色，室内暖光氛围受损(D-L1, E1-L1, F-L1)。"
    },

    # Sheet 15
    7513: {
        "score": 4.46,
        "severities": {"B": "L1", "D": "L1", "E2": "L1", "F": "L1"},
        "note": "沙发上放置的圆形猫窝鲜红色毛绒布料大面积欠饱和褪色发暗，边缘轻微溢色(B-L1, D-L1, E2-L1, F-L1)。"
    },
    7514: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7515: {
        "score": 2.61,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "豪华卫生间大理石洗手台面与室内墙壁完全丧失温馨暖黄灯光氛围，整体严重偏向冰冷泛青暗灰偏色(D-L1, E2-L1, F-L1)。"
    },
    7516: {
        "score": 2.17,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "刚铺好番茄芝士配料的生披萨饼面与木质操作台表面大面积欠饱和偏冷青灰暗淡偏色(D-L1, E2-L1, F-L1)。"
    },
    7517: {
        "score": 2.43,
        "severities": {"C": "L2", "D": "L2", "E2": "L2", "F": "L2"},
        "note": "卧室双人床上堆放的彩色靠枕与被褥大面积严重欠饱和脱色为暗沉死灰色，织物艳丽色彩彻底丧失（严重错色 C-L2）(C-L2, D-L2, E2-L2, F-L2)。"
    },
    7521: {
        "score": 2.73,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "派对餐桌边缘与方形翻糖蛋糕周围大面积浸染刺眼失真的荧光洋红紫光偏色，全图色调严重失真(D-L2, E1-L2, F-L2)。"
    },

    # Sheet 16
    7522: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L1", "F": "L1"},
        "note": "林荫道旁立着的道路指引路名蓝牌大面积欠饱和脱色为暗淡灰白，字牌标志色泽明显衰减（错色 C-L2）(C-L2, E2-L1, F-L1)。"
    },
    7523: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7524: {
        "score": 4.46,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "办公桌上两台笔记本电脑屏幕及周围桌面浸染失真的洋红紫冷色偏色，室内光照色温明显失衡(D-L1, E1-L1, F-L1)。"
    },
    7525: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    7526: {
        "score": 5.0,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "皮质沙发上就座小男孩所穿的红色短袖T恤与靠枕大面积欠饱和脱色发暗，服饰艳丽度衰减(E2-L1, F-L1)。"
    },
    7527: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 17
    7530: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7531: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7532: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "餐桌托盘上摆放的羊角面包表面大面积欠饱和偏冷青灰暗淡，奶泡边缘微泛杂色(D-L1, E2-L1, F-L1)。"
    },
    7536: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "聚会就座女士的红色上衣与背景木墙大面积浸染过度浓艳的焦糖红黄偏色，色彩轻度过饱和(D-L1, E1-L1, F-L1)。"
    },
    7538: {
        "score": 1.01,
        "severities": {"B": "L1", "C": "L3", "F": "L2"},
        "note": "纸盘上盛放的彩虹千层蛋糕底部蓝色与紫色糕体被颠覆性错涂为刺眼洋红色，色彩层次严重错乱（严重错色 C-L3）(B-L1, C-L3, F-L2)。"
    },
    7539: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L2", "F": "L1"},
        "note": "冲浪海域翻滚的巨浪海水大面积浸染过于浓烈刺眼的深青绿过饱和偏色，海水自然度受损(D-L1, E1-L2, F-L1)。"
    },

    # Sheet 18
    7540: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7541: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "餐盘中摆放的三明治切片吐司与酥脆薯片大面积欠饱和偏冷青灰暗淡(D-L1, E2-L1, F-L1)。"
    },
    7543: {
        "score": 2.43,
        "severities": {"D": "L1"},
        "note": "火车站月台候车区域地面与列车站房暗部在强逆光下略显偏暗偏深(D-L1)。"
    },
    7545: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7546: {
        "score": 2.17,
        "severities": {"C": "L2", "E2": "L2", "F": "L2"},
        "note": "网球拍网上静置的荧光黄绿网球被严重脱色错涂为惨白灰白，网球标志性荧光色彩彻底丧失（严重错色 C-L2）(C-L2, E2-L2, F-L2)。"
    },
    7547: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 19
    7548: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7549: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L1", "F": "L1"},
        "note": "运象卡车后方的晴朗蓝天被大面积错涂为枯黄尘土色，树冠背光面微泛红褐偏色（错色 C-L2）(C-L2, D-L1, F-L1)。"
    },
    7550: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7551: {
        "score": 2.61,
        "severities": {"D": "L2", "E1": "L1", "F": "L1"},
        "note": "海滩悬崖观景台木质长椅与沙质地面大面积浸染刺眼浓艳的焦糖红黄暖偏色，色彩轻度过饱和(D-L2, E1-L1, F-L1)。"
    },
    7553: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "餐碗中盛放的咖喱胡萝卜块与蔬菜汤汁色彩略显偏深偏暗(D-L1, F-L1)。"
    },
    7554: {
        "score": 4.46,
        "severities": {"D": "L1", "E1": "L2", "F": "L1"},
        "note": "街道上行驶的马车木架与马匹毛皮大面积浸染过于浓烈刺眼的焦糖橙红偏色，色彩严重过饱和(D-L1, E1-L2, F-L1)。"
    },

    # Sheet 20
    7555: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7558: {
        "score": 2.47,
        "severities": {"D": "L1"},
        "note": "室内站立男子针织衫暗部与后方墙角阴影色调略显偏深发暗(D-L1)。"
    },
    7561: {
        "score": 4.55,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "街头老式铸铁消防栓柱身与水泥地砖色彩略显欠饱和偏冷灰暗淡(D-L1, E2-L1)。"
    },
    7562: {
        "score": 2.47,
        "severities": {"D": "L1", "E1": "L2", "F": "L1"},
        "note": "复式公寓客厅地毯与室内墙面大面积浸染过度浓艳的焦糖红黄暖偏色，色彩严重过饱和(D-L1, E1-L2, F-L1)。"
    },
    7563: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7564: {
        "score": 2.43,
        "severities": {"B": "L1", "C": "L3", "F": "L2"},
        "note": "雪地上搭建的户外露营帐篷原本鲜艳的翠绿色帐顶被彻底颠覆性错涂为刺眼的大红色与亮橙色，装备色彩完全错配（严重错色 C-L3）(B-L1, C-L3, F-L2)。"
    },
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

def clean_description_text(note: str) -> str:
    """清理评语中冗余的前缀标签与后缀"""
    desc = re.sub(r"^原\d+\.\d+满分严重漏检[，,]?\s*(核查发现[：:]\s*)?", "", note)
    desc = re.sub(r"^核查发现[：:]\s*", "", desc)
    desc = re.sub(r"\([A-Za-z0-9_,\s-]+\)[。.]?$", "", desc)
    desc = desc.strip()
    if not desc.endswith("。") and desc:
        desc += "。"
    return desc

def build_defect_list(severities: dict, note: str):
    """根据严重度字典与定物描述构建缺陷列表"""
    if not severities:
        return []

    desc = clean_description_text(note)
    defects = []
    for code, sev in severities.items():
        name = DEFECT_NAME_MAP.get(code, "未知缺陷")
        defects.append({
            "id": code,
            "name": name,
            "severity": sev,
            "description": desc
        })
    return defects

def main():
    grounding_out_path = "LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_37.json"
    all_export_path = "LS_lcad_reviewer/exports/reviewed_1_10000_all.json"
    clean_export_path = "LS_lcad_reviewer/exports/reviewed_1_10000_clean.json"

    # 1. 导出中间定物字典
    with open(grounding_out_path, "w", encoding="utf-8") as f:
        json.dump(REVIEWS_B37, f, ensure_ascii=False, indent=2)
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

    for tid, r in REVIEWS_B37.items():
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
