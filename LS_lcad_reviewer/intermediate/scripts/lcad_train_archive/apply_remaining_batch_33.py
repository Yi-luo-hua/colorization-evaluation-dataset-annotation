# -*- coding: utf-8 -*-
"""
应用 Batch 33 审核具象定物判决字典并双向同步至正式交付文件
Batch 33: Task #6659 ~ #6846 (共 120 组)
"""

import json
import os
import re

# 120 组人工直审与具象定物判决字典
REVIEWS_B33 = {
    # Sheet 01
    6659: {
        "score": 2.17,
        "severities": {"D": "L2", "F": "L2"},
        "note": "病房病床上卧床女子的面部与手臂皮肤受黄绿环境光污染严重泛黄发暗，白色枕头与病床床单整体偏黄绿调(D-L2, F-L2)。"
    },
    6660: {
        "score": 2.17,
        "severities": {"C": "L3", "E2": "L3", "F": "L3"},
        "note": "停机坪上空原本蔚蓝的晴空与远处起伏群山完全褪色错涂为阴沉暗淡的灰白与暗褐灰调，天际色彩严重脱色失真(C-L3, E2-L3, F-L3)。"
    },
    6661: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：重型机车金属排气管与车身金属电镀件高光区泛紫红杂斑，展厅地面地毯暗部色温轻微偏暖黄(D-L1, F-L1)。"
    },
    6662: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6663: {
        "score": 2.73,
        "severities": {"C": "L1", "E2": "L2", "F": "L1"},
        "note": "河畔蹲坐喂鸟男子羽绒服领口与帽沿原有的暗红色严重脱色褪为发暗灰黑，水面上停泊的小木船深绿漆面欠饱和发暗(C-L1, E2-L2, F-L1)。"
    },
    6665: {
        "score": 2.47,
        "severities": {"C": "L2", "E2": "L2", "F": "L2"},
        "note": "天空中放飞的章鱼风筝原本鲜艳的玫红/洋红色主翼身彻底脱色褪为苍白暗灰，风筝标志性鲜亮色彩严重丧失(C-L2, E2-L2, F-L2)。"
    },

    # Sheet 02
    6667: {
        "score": 2.36,
        "severities": {"D": "L1", "F": "L1"},
        "note": "餐厅聚餐餐桌后方木质立柱与背景墙壁暗部阴影色调泛冷暗青，餐桌上玻璃酒瓶与人物服饰略显发暗发灰(D-L1, F-L1)。"
    },
    6668: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6669: {
        "score": 5.0,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：路边木质电线杆与下方标有144号公路的棕褐色路标指示牌色彩欠饱和褪色为暗灰棕(E2-L1, F-L1)。"
    },
    6670: {
        "score": 4.46,
        "severities": {},
        "note": "审查通过"
    },
    6671: {
        "score": 2.27,
        "severities": {"E1": "L2", "D": "L1", "F": "L2"},
        "note": "骑行人物后方背景中的整排绿植树木与草丛被过度渲染为刺眼浓艳的荧光翠绿色，饱和度过高且色相失真(E1-L2, D-L1, F-L2)。"
    },
    6674: {
        "score": 2.43,
        "severities": {"D": "L2", "F": "L1"},
        "note": "城市人行道上的推车商贩小吃车、遮阳伞棚及地面石砖大面积浸染不自然的焦糖黄褐色，整体环境色温明显偏暖(D-L2, F-L1)。"
    },

    # Sheet 03
    6675: {
        "score": 2.12,
        "severities": {"C": "L2", "D": "L2", "E1": "L2", "F": "L2"},
        "note": "木餐桌上盛放分切披萨的白瓷盘与披萨番茄酱面色彩发暗偏绿，后方摆放的圣诞玩偶红色外套褪色失真且披萨芝士反光刺眼(C-L2, D-L2, E1-L2, F-L2)。"
    },
    6678: {
        "score": 2.25,
        "severities": {"D": "L2", "F": "L2"},
        "note": "靠背扶手椅鲜艳的正红色皮质座垫与靠背严重泛冷偏向洋红紫红调，毛绒猫咪皮毛及背景木质墙板色温失真泛冷(D-L2, F-L2)。"
    },
    6680: {
        "score": 2.36,
        "severities": {"C": "L2", "D": "L2", "F": "L2"},
        "note": "卧室双人床上原有的蓝灰色被褥与浅紫色枕套被大面积错涂为单调浑浊的泥黄褐色，床铺织物色彩层次严重丧失(C-L2, D-L2, F-L2)。"
    },
    6681: {
        "score": 2.25,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "圆形烤盘上的披萨番茄酱面与金黄芝士严重欠饱和发暗发灰，失去烤制新鲜光泽，桌面深绿色桌布亦暗淡失真(D-L2, E2-L2, F-L2)。"
    },
    6682: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    6683: {
        "score": 2.31,
        "severities": {"E2": "L1", "D": "L1", "F": "L1"},
        "note": "靠背座椅上端坐的狸花猫颈部佩戴的红色蝴蝶结项圈略微欠饱和脱色，猫咪面部毛发色调轻微泛冷(E2-L1, D-L1, F-L1)。"
    },

    # Sheet 04
    6686: {
        "score": 2.36,
        "severities": {"C": "L2", "D": "L2", "F": "L2"},
        "note": "人物西装西服外套原本深蓝色的布料被颠覆性错涂为深泥褐色，双腿肌肉皮肤受洋红冷色污染泛紫发暗(C-L2, D-L2, F-L2)。"
    },
    6687: {
        "score": 2.47,
        "severities": {"D": "L2", "F": "L1"},
        "note": "芦苇丛中穿行的大象面部、大耳朵及象鼻灰色粗糙皮肤泛起不自然的青紫冷调，与周围自然绿色草丛不够协调(D-L2, F-L1)。"
    },
    6688: {
        "score": 5.0,
        "severities": {"E2": "L2", "D": "L1", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：赛车赛道后方背景中的大面积绿草坪护坡严重褪色泛黄枯萎，草地鲜绿生机完全丧失(E2-L2, D-L1, F-L2)。"
    },
    6689: {
        "score": 2.25,
        "severities": {"B": "L1", "D": "L1", "F": "L2"},
        "note": "餐桌上分切烘焙甜品时，不锈钢餐刀刀面与切口处产生青蓝杂色渗染，糕点蛋黄馅心与酥皮色相偏暗偏绿(B-L1, D-L1, F-L2)。"
    },
    6692: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6693: {
        "score": 2.32,
        "severities": {"C": "L2", "D": "L2", "F": "L2"},
        "note": "餐桌托盘上的草莓奶昔玻璃杯颜色偏向冷紫，右侧桌布原本鲜艳的红色几何条纹装饰被褪色错涂为浑浊暗黄褐(C-L2, D-L2, F-L2)。"
    },

    # Sheet 05
    6695: {
        "score": 4.55,
        "severities": {"D": "L2", "E2": "L1", "F": "L2"},
        "note": "庭院雪地积雪表面大面积泛黄泛暖偏色，网球拍边框与防寒毛线帽原有的深蓝色泽褪色发暗(D-L2, E2-L1, F-L2)。"
    },
    6697: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6698: {
        "score": 5.0,
        "severities": {"C": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：长颈鹿颈部后方背景中的彩色展板/荧光灯箱亮粉色区域褪色发蓝，局部背景色彩失真(C-L1, F-L1)。"
    },
    6699: {
        "score": 2.56,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "棒球场红土内野地面被过度渲染为刺眼浓艳的橙红亮色，击球运动员球衣与背景绿草皮边缘产生杂色泛红(D-L2, E1-L2, F-L2)。"
    },
    6700: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：书桌上趴卧的猫咪毛发色调偏冷泛青，桌面上塑料文具盒与纸质杂物色彩略显欠饱和发暗(D-L1, E2-L1, F-L1)。"
    },
    6702: {
        "score": 2.73,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "热带海滩上空原本纯净透亮的蓝天与碧蓝海水色调暗淡发灰，近岸绿松石色海面欠饱和且沙滩上立插的冲浪板色彩褪色(D-L2, E2-L2, F-L2)。"
    },

    # Sheet 06
    6705: {
        "score": 2.47,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "室内房间墙壁、门框通道与木质地面大面积过度浸染浓烈刺眼的橙黄色调，环境色温严重偏暖失真(D-L2, E1-L2, F-L2)。"
    },
    6706: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：口含甜甜圈男子的背景白墙与面部皮肤色温偏冷泛青，黑色长袖上衣暗部缺乏暖度(D-L1, F-L1)。"
    },
    6707: {
        "score": 2.61,
        "severities": {"D": "L2", "F": "L1"},
        "note": "飞机客舱机顶阅读灯与空调出风口塑料面板大面积泛黄泛褐偏色，原本中性灰白的机舱内饰顶棚色调失真(D-L2, F-L1)。"
    },
    6709: {
        "score": 4.46,
        "severities": {"C": "L2", "D": "L2", "F": "L2"},
        "note": "卧室床上原本暖棕色的被褥与枕头布料颠覆性错涂为冰冷暗淡的蓝灰色调，床铺整体温暖质感严重丧失(C-L2, D-L2, F-L2)。"
    },
    6710: {
        "score": 2.08,
        "severities": {"B": "L2", "D": "L1", "F": "L2"},
        "note": "海滩遮阳伞彩色伞面边缘与沙滩上铺设的深蓝色防潮垫边界发生明显颜色外溢侵染，沙子表面泛起杂乱紫红伪色(B-L2, D-L1, F-L2)。"
    },
    6711: {
        "score": 4.17,
        "severities": {"C": "L3", "E2": "L3", "F": "L3"},
        "note": "复古服饰海报背景原本鲜艳亮丽的明黄与洋红渐变彻底褪色错涂为苍白冰冷的灰青色，模特所穿橙黄毛衣与红色领带严重脱色失真(C-L3, E2-L3, F-L3)。"
    },

    # Sheet 07
    6716: {
        "score": 2.43,
        "severities": {"B": "L1", "C": "L1", "E1": "L2", "F": "L2"},
        "note": "街道旁圆形禁止通行交通标志牌红色边框被过度渲染为浓艳荧光洋红，标牌边缘出现翠绿伪色光晕(B-L1, C-L1, E1-L2, F-L2)。"
    },
    6717: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6719: {
        "score": 2.43,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "广阔雪原上奔跑的野生动物褐色皮毛微弱褪色发暗，远处积雪山坡阴影层次略显单一平淡(E2-L1, F-L1)。"
    },
    6722: {
        "score": 2.36,
        "severities": {"D": "L2", "F": "L2"},
        "note": "茂密绿林中站立的成年母象与幼象灰色皮肤大面积泛起不自然的洋红紫调，与自然深林绿色背景产生违和(D-L2, F-L2)。"
    },
    6723: {
        "score": 1.2,
        "severities": {"E2": "L3", "C": "L2", "F": "L3"},
        "note": "水泥桥梁左侧原本茂盛的秋季红褐与翠绿树冠大面积脱色为苍白单色灰阶，桥梁栏杆与下方河水严重欠饱和失去生机(E2-L3, C-L2, F-L3)。"
    },
    6725: {
        "score": 4.46,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 08
    6726: {
        "score": 2.26,
        "severities": {"C": "L3", "D": "L2", "E2": "L2", "F": "L3"},
        "note": "室内聚会青年男子头戴的鲜亮大红色棒球帽被彻底脱色错涂为灰褐色，背景原本温暖金黄的墙面大面积泛冷褪色为灰白(C-L3, D-L2, E2-L2, F-L3)。"
    },
    6727: {
        "score": 2.17,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "雨天撑伞行人所穿的竖条纹阔腿裤棕黄色泽欠饱和发暗，人行道路面阴影色调轻微泛冷(D-L1, E2-L1, F-L1)。"
    },
    6728: {
        "score": 2.61,
        "severities": {"D": "L1", "F": "L1"},
        "note": "厨房整体木质橱柜表面色泽略微欠缺自然暖木质感，微波炉与不锈钢灶台金属反光区域色调微弱泛冷(D-L1, F-L1)。"
    },
    6729: {
        "score": 2.43,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "靠墙书桌前摆放的转椅深蓝色布艺座垫欠饱和褪色发暗，玻璃桌面及地面大面积偏暗偏灰，整体光泽受损(D-L2, E2-L2, F-L2)。"
    },
    6730: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6731: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 09
    6735: {
        "score": 2.17,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "木工展台陈列的手工雕刻木勺表面天然的蜜黄与红棕木质色泽大面积褪色发灰，失去温润质感(D-L2, E2-L2, F-L2)。"
    },
    6736: {
        "score": 2.43,
        "severities": {"D": "L2", "F": "L2"},
        "note": "原木木屋卫生间圆木墙面与木质储物柜大面积泛红偏向红褐色，洗手台旁悬挂的蓝色毛巾与台面色泽发暗(D-L2, F-L2)。"
    },
    6740: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6742: {
        "score": 5.0,
        "severities": {"C": "L3", "E2": "L2", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：八角形红色停步标牌下方悬挂的亮黄色菱形警示标牌彻底脱色错涂为纯灰白色，严重丢失警示标志色彩(C-L3, E2-L2, F-L2)。"
    },
    6746: {
        "score": 2.43,
        "severities": {"D": "L2", "F": "L2"},
        "note": "公共卫生间深绿色油漆墙面大面积产生不自然的黄绿与暗黄偏色色块，墙面色彩斑驳不均(D-L2, F-L2)。"
    },
    6747: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 10
    6749: {
        "score": 2.23,
        "severities": {"D": "L1", "F": "L1"},
        "note": "现代卫生间灰色瓷砖墙壁与白色浴缸表面略微泛暖泛黄，小窗外透出的绿色植物生机轻微减弱(D-L1, F-L1)。"
    },
    6750: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6754: {
        "score": 5.0,
        "severities": {"C": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：球场上对抗球员所穿的鲜亮荧光洋粉色球衣欠饱和褪色为浅淡灰粉，队伍球衣辨识度受损(C-L1, E2-L1, F-L1)。"
    },
    6755: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6757: {
        "score": 2.73,
        "severities": {"E2": "L2", "C": "L1", "F": "L1"},
        "note": "公园湖畔撑伞散步游客手中原本鲜艳的正红色雨伞严重欠饱和褪色为发暗褐灰，湖畔草坪与树木绿意明显转淡(E2-L2, C-L1, F-L1)。"
    },
    6758: {
        "score": 2.61,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "室内聚会人物面部肤色与后方木质墙板被过度渲染为浓烈刺眼的橙黄色，高光发红泛黄，视觉自然度明显下降(D-L2, E1-L2, F-L2)。"
    },

    # Sheet 11
    6759: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：西装男士身后背景中原本明亮鲜黄的独栋住宅外墙被完全脱色错涂为灰白色，建筑色彩严重失真(C-L2, E2-L2, F-L2)。"
    },
    6760: {
        "score": 1.12,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "室内客厅背景墙面与圆形发光壁龛原有的暖金黄色泽严重褪色泛灰泛白，室内温馨氛围与花卉陈设层次大幅削弱(D-L2, E2-L2, F-L2)。"
    },
    6761: {
        "score": 2.47,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "水岸边停靠的木质独木舟与倒映着树影的河水大面积泛暗泛褐，水体原本的深青冷翠水色褪色失真(D-L2, E2-L2, F-L2)。"
    },
    6762: {
        "score": 1.15,
        "severities": {"D": "L2", "F": "L2"},
        "note": "站台停靠的列车车头与车身红色漆面色温偏冷偏向暗紫红色，站台警示标牌与轨道环境整体泛紫失真(D-L2, F-L2)。"
    },
    6763: {
        "score": 4.46,
        "severities": {"E2": "L1", "C": "L1", "F": "L1"},
        "note": "外卖餐盒内搭配的新鲜西兰花深绿色泽有所欠饱和泛白泛黄，熟食鸡块酱汁光泽与蔬菜色差轻度失真(E2-L1, C-L1, F-L1)。"
    },
    6764: {
        "score": 1.08,
        "severities": {"C": "L2", "D": "L2", "E2": "L3", "F": "L3"},
        "note": "房间内木质琴架柜体与墙面暖黄原木色泽颠覆性褪色为冰冷死板的灰青色，沙发上的红色靠垫严重脱色失真(C-L2, D-L2, E2-L3, F-L3)。"
    },

    # Sheet 12
    6765: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：托盘中摆放的装饰纸杯蛋糕表面的彩色糖霜与小纸伞略显欠饱和，鲜红色与明黄色糖霜色泽发暗(D-L1, E2-L1, F-L1)。"
    },
    6766: {
        "score": 2.17,
        "severities": {"C": "L3", "D": "L2", "E1": "L2", "F": "L3"},
        "note": "展厅蜡像人物身上穿着的亮蓝色西装外套颠覆性错涂为深泥褐色，面部泛紫且背景装饰花草过于浓艳杂乱(C-L3, D-L2, E1-L2, F-L3)。"
    },
    6768: {
        "score": 5.0,
        "severities": {"C": "L3", "E2": "L3", "F": "L3"},
        "note": "原5.0满分严重漏检，核查发现：公交车厢内过道两侧原本鲜艳明亮的翠绿色座椅织物座垫被完全脱色错涂为纯暗灰色，车厢内饰标志性色彩彻底丧失(C-L3, E2-L3, F-L3)。"
    },
    6769: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：水面木质码头栈桥暗部木纹略微欠饱和脱色，水面蓝色遮阳伞周边水色层次稍显泛暗(D-L1, E2-L1, F-L1)。"
    },
    6770: {
        "score": 2.25,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "房间矮桌上铺设的深蓝色台布与软垫色调欠饱和泛暗，地面地毯与长毛猫咪皮毛暗部色温轻微偏暖黄(D-L1, E2-L1, F-L1)。"
    },
    6772: {
        "score": 4.46,
        "severities": {"D": "L2", "E2": "L1", "F": "L2"},
        "note": "烘焙教室中儿童穿着的鲜红色围裙大面积欠饱和褪色为暗褐红，背景墙面与操作台大面积浸染浓重暖黄偏色(D-L2, E2-L1, F-L2)。"
    },

    # Sheet 13
    6773: {
        "score": 2.73,
        "severities": {"C": "L3", "E2": "L3", "F": "L3"},
        "note": "厨房内部原本涂刷的鲜艳草绿色油漆墙面被完全脱色错涂为苍白暗淡的灰白与暗米色，整个厨房视觉色调颠覆性失真(C-L3, E2-L3, F-L3)。"
    },
    6775: {
        "score": 2.73,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "卫生间多个独立隔间门板与瓷砖墙面原有的暖黄色调完全褪色为冰冷死板的灰白色，室内空间氛围严重失真(D-L2, E2-L2, F-L2)。"
    },
    6776: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L2", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：沙发上躺卧的婴儿面部皮肤与嘴唇过度渲染为刺眼通红的洋红色，深红色皮质沙发表面高光浓艳失真(D-L1, E1-L2, F-L2)。"
    },
    6780: {
        "score": 2.73,
        "severities": {"D": "L2", "F": "L1"},
        "note": "公园前景中古老巨树粗糙树干的天然暖褐木皮色泽大面积泛冷泛青偏向蓝灰色，树干肌理真实感明显受损(D-L2, F-L1)。"
    },
    6781: {
        "score": 2.17,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "草地上叼着飞盘的浅黄宠物犬皮毛与周围草坪暗部阴影色调略显泛暗泛冷，草地鲜绿质感微弱不足(D-L1, E2-L1, F-L1)。"
    },
    6782: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 14
    6783: {
        "score": 2.47,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "高山草甸上空原本纯净蔚蓝的晴空彻底发白褪色，远景雪山与牧羊人身旁的高山草甸大面积泛黄泛褐(D-L2, E2-L2, F-L2)。"
    },
    6784: {
        "score": 2.36,
        "severities": {"D": "L1", "F": "L1"},
        "note": "卫生间镜前男子身后的瓷砖墙面与镜子边缘色调微弱泛暗泛黄，白炽灯光暖度略显不匀(D-L1, F-L1)。"
    },
    6786: {
        "score": 2.17,
        "severities": {"C": "L3", "E1": "L2", "F": "L3"},
        "note": "滑板U型池上滑板青年所穿的浅卡其色连帽卫衣被颠覆性错涂为刺眼浓艳的亮荧光洋红色，色彩严重失真违和(C-L3, E1-L2, F-L3)。"
    },
    6788: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：高山滑雪场上空湛蓝晴空被过度渲染为浓艳刺眼的电光深蓝色，雪山阴影亦轻度过饱和(D-L1, E1-L2, F-L1)。"
    },
    6789: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6790: {
        "score": 2.25,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "户外餐厅红砖建筑前撑起的红色可口可乐遮阳伞面色彩略微欠饱和发暗，砖墙暗部光影质感微弱受损(D-L1, E2-L1, F-L1)。"
    },

    # Sheet 15
    6791: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：餐厅聚餐背景中的木质门框与墙壁暗部阴影色调偏冷发灰，暖黄原木温润质感轻度欠饱和(D-L1, E2-L1, F-L1)。"
    },
    6793: {
        "score": 1.04,
        "severities": {"D": "L2", "E2": "L2", "F": "L3"},
        "note": "荒野碎石山坡表面原有的金黄与暖褐苔藓植被大面积脱色为灰白碎石，中心局部绿色杂草色调突兀生硬(D-L2, E2-L2, F-L3)。"
    },
    6795: {
        "score": 4.55,
        "severities": {"C": "L3", "D": "L2", "E2": "L2", "F": "L3"},
        "note": "滑板坡道上方原本壮美温暖的金黄色夕阳晚霞天空被颠覆性错涂为冰冷单调的淡蓝白昼天空，地面暖黄斜阳完全脱色失真(C-L3, D-L2, E2-L2, F-L3)。"
    },
    6796: {
        "score": 2.27,
        "severities": {"C": "L2", "D": "L2", "F": "L2"},
        "note": "明黄色毛毯上趴卧的宠物犬面部与颈部白色毛发受严重洋红紫伪色污染，毛发产生大面积不自然的粉紫杂斑(C-L2, D-L2, F-L2)。"
    },
    6797: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6802: {
        "score": 2.11,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "室内聚会背景原本温暖的红棕木质护墙板严重褪色发灰，站立长者所穿的绿色条纹毛衣色彩欠饱和泛白(D-L2, E2-L2, F-L2)。"
    },

    # Sheet 16
    6803: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6804: {
        "score": 2.47,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "街道停放的青绿色小客车车漆光泽与人行道树木绿叶略显欠饱和发暗，街景阴影处色彩层次略微单调(D-L1, E2-L1, F-L1)。"
    },
    6805: {
        "score": 2.36,
        "severities": {"D": "L3", "F": "L3"},
        "note": "卫生间白色陶瓷马桶、洗手池及四周瓷砖墙面被颠覆性浸染为极度不自然的冰冷电光青蓝色，全图严重色温偏冷失真(D-L3, F-L3)。"
    },
    6806: {
        "score": 2.61,
        "severities": {"D": "L1", "F": "L1"},
        "note": "卫生间洗手台红棕木质浴室柜表面木纹色泽略微欠缺红润暖光，镜框与瓷砖墙面阴影微弱泛黄(D-L1, F-L1)。"
    },
    6808: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：热带稀树草原远景合欢树冠与近景灌木丛大面积欠饱和发暗发灰，植被原本苍翠生机明显衰减(D-L1, E2-L2, F-L1)。"
    },
    6809: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 17
    6810: {
        "score": 2.61,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "昏暗光线下身穿白袍的长发男子面部与袍服大面积浸染浓烈刺眼的红橙色高光，整体饱和度明显过高偏暖(D-L2, E1-L2, F-L2)。"
    },
    6811: {
        "score": 2.32,
        "severities": {"D": "L1", "F": "L1"},
        "note": "西餐厅餐盘中摆盘的新鲜生火腿肉片与白瓷盘边缘产生轻微偏暖偏黄伪色，背景餐桌反光稍显发暗(D-L1, F-L1)。"
    },
    6812: {
        "score": 2.47,
        "severities": {"C": "L3", "D": "L2", "F": "L2"},
        "note": "网球场上发球女运动员身上穿着的亮粉珊瑚色运动短裙被颠覆性错涂为浅蓝灰冷色，球员服饰主色调严重错色(C-L3, D-L2, F-L2)。"
    },
    6813: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6815: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6816: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L2", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：公共卫生间红砖外墙大面积欠饱和褪色为灰暗杂色，上方蔚蓝天空明显泛灰脱色(D-L1, E2-L2, F-L2)。"
    },

    # Sheet 18
    6820: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6822: {
        "score": 2.47,
        "severities": {"D": "L1", "E2": "L1", "F": "L2"},
        "note": "夜景中弧形艺术建筑雕塑发光曲面原有的温暖金黄灯光色泽大面积泛白褪色，雕塑周围草木阴影泛起青紫杂色(D-L1, E2-L1, F-L2)。"
    },
    6824: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：厨房橱柜前站立幼儿所穿的橙红色短袖上衣严重偏色错涂为冷调洋粉色，服饰色彩失真(C-L2, D-L1, F-L1)。"
    },
    6826: {
        "score": 2.17,
        "severities": {"D": "L2", "F": "L1"},
        "note": "昏暗卧室四柱床帷幔帘布暗部阴影色调轻微泛暗偏绿，远景电视荧幕冷蓝光晕边缘微弱发散(D-L2, F-L1)。"
    },
    6828: {
        "score": 1.15,
        "severities": {"C": "L3", "D": "L3", "F": "L3"},
        "note": "海滩棕榈树下开阔沙滩地面被极度荒谬地颠覆性错涂为大面积荧光浅绿色，沙滩色彩严重常识性错乱(C-L3, D-L3, F-L3)。"
    },
    6829: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 19
    6830: {
        "score": 2.47,
        "severities": {"D": "L1", "F": "L1"},
        "note": "厨房白色燃气灶台上烹饪的金属汤锅与烤盘食材表面光影略显欠饱和，灶台后方墙面轻微泛黄(D-L1, F-L1)。"
    },
    6832: {
        "score": 2.17,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "海滩停靠的木质渔船船体与岸边浅滩木纹色泽略显欠饱和脱色，阴天海面暗部层次略微平淡(D-L1, E2-L1, F-L1)。"
    },
    6833: {
        "score": 4.55,
        "severities": {"D": "L2", "E1": "L1", "F": "L1"},
        "note": "棒球场铁丝防护网与内野红土击球区大面积浸染浓重刺眼的红黄色调，击球手服饰与地面色温明显过暖(D-L2, E1-L1, F-L1)。"
    },
    6834: {
        "score": 2.47,
        "severities": {"C": "L1", "D": "L2", "E2": "L1", "F": "L2"},
        "note": "公园草坪后方原本苍翠起伏的远景山丘树木大面积泛红泛褐偏色，近景草坪与木质野餐桌色调失真欠饱和(C-L1, D-L2, E2-L1, F-L2)。"
    },
    6836: {
        "score": 5.0,
        "severities": {"C": "L3", "E2": "L2", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：电脑桌后方原本涂刷的鲜艳浅蓝色油漆背景墙被颠覆性错涂为灰暗泥褐色，房间装饰色彩严重脱色(C-L3, E2-L2, F-L2)。"
    },
    6837: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 20
    6838: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6841: {
        "score": 2.2,
        "severities": {"D": "L1", "F": "L1"},
        "note": "棒球场击球区本垒红土与周边绿草地交界边缘略显杂色渗透，击球手挥动的木质球棒色泽稍显发暗(D-L1, F-L1)。"
    },
    6843: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：斑马脚下原本葱绿的草地大面积欠饱和褪色为暗灰绿色，背景树木暗部阴影色调泛冷发灰(D-L1, E2-L2, F-L1)。"
    },
    6844: {
        "score": 2.47,
        "severities": {"D": "L2", "F": "L2"},
        "note": "夜景中古老石砌钟楼外墙投射的灯光大面积偏向刺眼的黄绿与粉紫混杂伪色，原本质朴温暖的泛光夜景质感明显失真(D-L2, F-L2)。"
    },
    6845: {
        "score": 2.73,
        "severities": {"D": "L2", "F": "L1"},
        "note": "厨房整体木质橱柜表面大面积泛红偏向红褐色，烤箱金属边框与玻璃烤箱门暗部反光偏色发暗(D-L2, F-L1)。"
    },
    6846: {
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
    clean_desc = re.sub(r"[\(（][A-Z0-9\s,\-]+[\)）]", "", note).strip()
    clean_desc = re.sub(r"【.*?】", "", clean_desc).strip()
    clean_desc = re.sub(r"^原5\.0满分严重漏检，核查发现：", "", clean_desc).strip()

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
    print(f"[*] 开始断言校验 Batch 33 定物判决字典 (共 {len(reviews)} 组)...")
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
    validate_reviews(REVIEWS_B33)

    base_dir = r"d:\学业文件\MCL\上色评价_数据集标注\LS_lcad_reviewer"
    intermediate_dir = os.path.join(base_dir, "intermediate")
    all_export_path = os.path.join(base_dir, "exports", "reviewed_1_10000_all.json")
    clean_export_path = os.path.join(base_dir, "exports", "reviewed_1_10000_clean.json")
    grounding_out_path = os.path.join(intermediate_dir, "audits", "grounding_remaining_batch_33.json")

    # 1. 导出中间定物字典
    with open(grounding_out_path, "w", encoding="utf-8") as f:
        json.dump(REVIEWS_B33, f, ensure_ascii=False, indent=2)
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

    for tid, r in REVIEWS_B33.items():
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
