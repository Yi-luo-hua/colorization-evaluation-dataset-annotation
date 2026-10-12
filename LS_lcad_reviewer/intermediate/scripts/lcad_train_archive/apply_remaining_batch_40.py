# -*- coding: utf-8 -*-
"""
应用 Batch 40 审核具象定物判决字典并双向同步至正式交付文件
Batch 40: Task #7944 ~ #8137 (共 120 组)
"""

import json
import os
import re

# 120 组人工直审与具象定物判决字典
REVIEWS_B40 = {
    # Sheet 01
    7953: {
        "score": 2.36,
        "severities": {},
        "note": "审查通过"
    },
    7955: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7956: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7957: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    7958: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L1", "E2": "L1"},
        "note": "厨房内快速走动的人身穿的红色上衣大面积欠饱和褪色为发暗浅红(C-L2, E2-L1)，实木橱柜温润木色欠饱和发暗泛冷灰(D-L1)。"
    },
    7961: {
        "score": 4.46,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 02
    7963: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7964: {
        "score": 2.36,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "夜间十字路口沿街建筑物外立面与夜空大面积浸染失真偏浓艳的紫红暖偏色(D-L1, E1-L1)，夜景灯光自然度受损(F-L1)。"
    },
    7965: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7966: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7969: {
        "score": 2.17,
        "severities": {"C": "L2", "D": "L1", "E2": "L1", "F": "L1"},
        "note": "室内地面铺设的深红色地毯大面积欠饱和褪色为灰暗冷色(E2-L1)，墙角摆放的明黄色儿童塑料小座椅欠饱和褪色发白(C-L2)，色温偏冷灰(D-L1)，视觉自然度轻度受损(F-L1)。"
    },
    7970: {
        "score": 2.47,
        "severities": {"C": "L2", "D": "L1", "E2": "L2", "F": "L2"},
        "note": "动物园草坪后方原本生机盎然的茂密翠绿树林灌木大面积欠饱和严重脱色错涂为灰白枯槁死色，斑马脚下绿茵草坪也明显褪色发暗(C-L2, D-L1, E2-L2, F-L2)。"
    },

    # Sheet 03
    7971: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7973: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L1", "E2": "L1", "F": "L1"},
        "note": "古建筑石砌门洞前女子撑着的鲜红色传统油纸伞与身上红色古装服饰大面积欠饱和褪色为暗沉枯红色(C-L2, E2-L1)，石墙背景泛冷灰偏色(D-L1)，视觉自然度受损(F-L1)。"
    },
    7977: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "男子操作的儿童笔记本电脑鲜绿色外壳局部色彩欠饱和褪色变浅(E2-L1)，草绿色泽微偏淡(D-L1)。"
    },
    7978: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "客厅内摆放的酒红色布艺双人沙发大面积浸染失真浓艳的洋红紫暖偏色(D-L1, E1-L1)，视觉自然度轻度受损(F-L1)。"
    },
    7980: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "街头啤酒巡游卡车车头木质车身与后部车厢粉红色棚罩色彩略显过度浓艳偏深红暖色(E1-L1)，局部微泛暖偏色(D-L1)。"
    },
    7981: {
        "score": 2.36,
        "severities": {"D": "L1", "E1": "L2", "F": "L1"},
        "note": "客厅内地毯上玩耍的小女孩身穿的红色上衣与背景实木电视机柜色彩过度浓艳刺眼(E1-L2)，室内原本温馨暖黄的墙壁泛阴冷灰粉偏色(D-L1)，视觉自然度受损(F-L1)。"
    },

    # Sheet 04
    7982: {
        "score": 2.17,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "卧室双人床上的浅米黄色菱形绗缝床垫织物表面大面积欠饱和严重脱色并浸染阴冷泛青蓝偏色，原本温暖的米黄织物质感完全丧失(D-L2, E2-L2, F-L2)。"
    },
    7983: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    7984: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7985: {
        "score": 2.56,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "牵着的骏马背部铺设的红色布艺马鞍垫色彩过度浓艳偏暗红(E1-L1)，沙土地面与人物服饰微偏暗暖偏色(D-L1)，视觉自然度轻度受损(F-L1)。"
    },
    7986: {
        "score": 1.12,
        "severities": {"C": "L3", "E2": "L1", "F": "L2"},
        "note": "动物园草坪背景处陈列的长颈鹿雕塑原本棕黄色的斑纹被颠覆性错涂为亮粉红色(C-L3)，近处小女孩粉红连帽卫衣局部欠饱和褪色(E2-L1)，视觉自然度受损(F-L2)。"
    },
    7988: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 05
    7990: {
        "score": 2.36,
        "severities": {},
        "note": "审查通过"
    },
    7991: {
        "score": 2.61,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "门厅上方悬挂的婚礼装饰粉白鲜花与绿色藤蔓色彩过度浓艳偏深红黄(E1-L1)，米黄墙面与环境光整体微偏暗暖偏色(D-L1)。"
    },
    7992: {
        "score": 2.56,
        "severities": {},
        "note": "审查通过"
    },
    7994: {
        "score": 2.73,
        "severities": {"C": "L2", "D": "L1", "E2": "L2", "F": "L2"},
        "note": "街角历史保护建筑外立面金黄色砖石墙体大面积欠饱和严重脱色错涂为灰褐色与阴冷灰白死色，建筑物温暖的砖石质感彻底丧失(C-L2, D-L1, E2-L2, F-L2)。"
    },
    7995: {
        "score": 2.17,
        "severities": {},
        "note": "审查通过"
    },
    7997: {
        "score": 2.56,
        "severities": {"C": "L3", "D": "L1", "E1": "L1", "F": "L2"},
        "note": "咖啡馆木桌白瓷方盘上摆放的烤吐司三明治切面原本金黄焦香面包片被颠覆性错涂为荧光黄绿色(C-L3, E1-L1)，木质桌面边缘微泛冷偏色(D-L1)，视觉自然度受损(F-L2)。"
    },

    # Sheet 06
    8001: {
        "score": 2.17,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "大教堂广场街角停放的复古明黄色观光老爷车车身黄色车漆色彩略显欠饱和偏暗(E2-L1)，石雕外墙色调微偏暗(D-L1)。"
    },
    8002: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8005: {
        "score": 2.61,
        "severities": {},
        "note": "审查通过"
    },
    8007: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8008: {
        "score": 2.36,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "围栏内两只斑马皮毛黑白条纹交界处大面积浸染过度浓艳的焦黄红棕暖偏色(E1-L1)，毛色过饱和失真(D-L1)，视觉自然度轻度受损(F-L1)。"
    },
    8010: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L1", "E2": "L1", "F": "L1"},
        "note": "摩托车旁年轻女子身后金黄色秋景树林树叶大面积欠饱和褪色为灰暗色(E2-L1)，右后方红色轿车车尾局部脱色泛暗(C-L2)，色温偏冷灰(D-L1)，视觉自然度受损(F-L1)。"
    },

    # Sheet 07
    8013: {
        "score": 2.34,
        "severities": {"C": "L2", "D": "L1", "E2": "L1", "F": "L1"},
        "note": "牧场草地上方原本纯净深蓝色的晴空背景被大面积欠饱和严重脱色错涂为阴沉灰白死色(C-L2, E2-L1)，全图微偏冷灰暗调(D-L1)，视觉自然度受损(F-L1)。"
    },
    8015: {
        "score": 2.17,
        "severities": {"C": "L2", "D": "L1", "E2": "L1", "F": "L2"},
        "note": "沿街人行道对面停放的紫红色小型轿车车身大面积欠饱和褪色为灰暗冷色(E2-L1)，街道地面金黄色阳光暖调褪色并泛冷偏色(D-L1)，视觉自然度受损(F-L2)。"
    },
    8016: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8017: {
        "score": 5.0,
        "severities": {"C": "L3", "E2": "L2", "F": "L2"},
        "note": "树林旁停放的黄色箱式搬家货车（Penske 卡车）原本标志性的明黄色大型货箱外壁大面积欠饱和严重脱色错涂为灰白色，标志性黄色完全丧失(C-L3, E2-L2, F-L2)。"
    },
    8018: {
        "score": 4.46,
        "severities": {},
        "note": "审查通过"
    },
    8019: {
        "score": 2.34,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 08
    8021: {
        "score": 1.12,
        "severities": {},
        "note": "审查通过"
    },
    8023: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8024: {
        "score": 4.23,
        "severities": {},
        "note": "审查通过"
    },
    8025: {
        "score": 2.32,
        "severities": {"D": "L2", "F": "L1"},
        "note": "车展展厅地面铺设的迎宾地毯及周围参观人群背景大面积浸染失真发暗的深青蓝冷偏色，红色复古摩托车金属油箱与环境色温严重失衡(D-L2, F-L1)。"
    },
    8027: {
        "score": 5.0,
        "severities": {"C": "L3", "E2": "L2", "F": "L2"},
        "note": "网球场上网球少女身穿的荧光黄绿条纹运动背心大面积欠饱和严重脱色错涂为灰白色，标志性鲜艳运动服色彩彻底丧失(C-L3, E2-L2, F-L2)。"
    },
    8030: {
        "score": 2.17,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 09
    8031: {
        "score": 2.73,
        "severities": {"C": "L3", "D": "L1", "E2": "L2", "F": "L2"},
        "note": "棒球场外野看台后方大面积翠绿草坪欠饱和严重脱色错涂为惨白灰暗死色，生机盎然的草坪完全变成灰白死色(C-L3, E2-L2, F-L2)，场地色调泛冷灰(D-L1)。"
    },
    8032: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8033: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8034: {
        "score": 4.23,
        "severities": {},
        "note": "审查通过"
    },
    8038: {
        "score": 2.47,
        "severities": {},
        "note": "审查通过"
    },
    8041: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 10
    8042: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L2", "F": "L1"},
        "note": "稀树草原沙土草甸原本金黄温暖的干草地表大面积欠饱和严重褪色变暗沉灰褐色(E2-L2)，长颈鹿身上棕黄色斑块色泽黯淡偏冷灰(D-L1)，视觉自然度受损(F-L1)。"
    },
    8043: {
        "score": 2.43,
        "severities": {},
        "note": "审查通过"
    },
    8044: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8045: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8046: {
        "score": 2.73,
        "severities": {"C": "L2", "D": "L2", "F": "L2"},
        "note": "海滩骑马队列背景处清澈平缓的灰蓝色浅海海面大面积被错涂为浑浊焦黄泥浆色(C-L2)，海滩地表严重浸染焦黄暗暖偏色(D-L2)，视觉自然度受损(F-L2)。"
    },
    8049: {
        "score": 2.23,
        "severities": {"C": "L3", "E2": "L2", "F": "L2"},
        "note": "展台上陈列的定制改装倒三轮摩托车原本鲜艳醒目的明黄色车架与前轮轮毂外壳大面积欠饱和严重脱色错涂为灰白死色，改装车标志性黄色完全丧失(C-L3, E2-L2, F-L2)。"
    },

    # Sheet 11
    8050: {
        "score": 2.36,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "站台旅客拉杆行李箱鲜红色外壳局部色彩略显欠饱和偏暗(E2-L1)，车体反光微泛冷偏色(D-L1)。"
    },
    8052: {
        "score": 5.0,
        "severities": {"C": "L3", "E2": "L2", "F": "L2"},
        "note": "长椅上放置的户外骑行宝蓝色双肩背包大面积欠饱和严重脱色错涂为灰白死色，红色织物衬垫也褪色发暗，背包鲜明色彩完全丧失(C-L3, E2-L2, F-L2)。"
    },
    8053: {
        "score": 2.61,
        "severities": {"D": "L1"},
        "note": "暗光办公桌面背景暖黄色台灯光晕色彩略显浓暗(D-L1)，轻度偏暖色。"
    },
    8054: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8058: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    8064: {
        "score": 2.17,
        "severities": {"C": "L3", "E2": "L2", "F": "L2"},
        "note": "厨房吧台左侧原本明艳醒目的正红色乳胶漆艺术背景墙大面积欠饱和严重脱色错涂为深褐灰死色，红墙视觉焦点彻底丧失(C-L3, E2-L2, F-L2)。"
    },

    # Sheet 12
    8065: {
        "score": 5.0,
        "severities": {"C": "L3", "D": "L1", "F": "L1"},
        "note": "海浪中冲浪者脚下踩着的原本明亮鲜艳的青绿色冲浪板板面被颠覆性错涂为亮粉红色(C-L3)，冲浪板标志性颜色错乱，视觉自然度受损(F-L1)。"
    },
    8066: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8067: {
        "score": 4.46,
        "severities": {},
        "note": "审查通过"
    },
    8068: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "卫浴间洗手台上方悬挂的深红棕色实木镜柜与置物架表面色彩过度浓艳偏深红(E1-L1)，木质家具微泛暖偏色(D-L1)。"
    },
    8069: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8071: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 13
    8073: {
        "score": 2.61,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "巨浪中冲浪者身后原本沐浴在落日余晖中的金黄色夕阳反光与晚霞大面积欠饱和严重脱色为发暗灰白冷色，浪花金黄晚霞光感彻底丧失(D-L2, E2-L2, F-L2)。"
    },
    8074: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8075: {
        "score": 5.0,
        "severities": {"C": "L3", "D": "L1", "F": "L1"},
        "note": "洗手台上白瓷马克杯上方放置的圆形塑料收纳小碗原本浅翠绿色被颠覆性错涂为亮粉红色(C-L3)，室内环境光微泛暖偏色(D-L1)。"
    },
    8076: {
        "score": 2.73,
        "severities": {"C": "L2", "D": "L1", "E2": "L1", "F": "L1"},
        "note": "棒球场击球区后方原本平整翠绿的外野草坪大面积欠饱和褪色为暗沉枯灰绿色(C-L2, E2-L1)，红土地表色温微泛暗冷(D-L1)，视觉自然度受损(F-L1)。"
    },
    8077: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8078: {
        "score": 2.36,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 14
    8079: {
        "score": 4.55,
        "severities": {"C": "L3", "E2": "L1", "F": "L2"},
        "note": "沙发上躺着的小男孩身穿的原本鲜艳明亮的正红色短袖运动T恤被彻底颠覆性错涂为冰亮天蓝色(C-L3)，原衣物红色彻底丧失，视觉自然度受损(F-L2)。"
    },
    8082: {
        "score": 2.43,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "床上散落放置的鲜黄色手工编织毛线团表面色彩略显欠饱和偏暗(E2-L1)，床单暗部微泛冷偏色(D-L1)。"
    },
    8083: {
        "score": 4.55,
        "severities": {"C": "L2", "D": "L2", "E1": "L1", "F": "L2"},
        "note": "展台左侧原本翠绿平整的草地背景大面积浸染失真偏浓艳的洋红紫偏色并严重变色(C-L2, D-L2)，浅蓝针织台布色温失真(F-L2)。"
    },
    8084: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "厨房微波炉上方实木吊柜柜门温润木色大面积欠饱和褪色为灰白发暗冷色(E2-L1)，室内色温微偏冷灰(D-L1)。"
    },
    8085: {
        "score": 2.17,
        "severities": {},
        "note": "审查通过"
    },
    8088: {
        "score": 2.43,
        "severities": {"E1": "L1", "F": "L1"},
        "note": "大象展区驯象员身穿的墨绿色工作服短袖T恤局部色彩略显偏暗(E1-L1)，视觉自然度受轻微影响(F-L1)。"
    },

    # Sheet 15
    8089: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8090: {
        "score": 1.08,
        "severities": {"D": "L2", "E1": "L1", "F": "L1"},
        "note": "棒球场夜场看台上方松下电器（Panasonic）广告牌及周围看台大面积浸染失真偏浓艳的深紫蓝冷偏色(D-L2, E1-L1)，夜间灯光自然度受损(F-L1)。"
    },
    8092: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8095: {
        "score": 2.73,
        "severities": {"C": "L2", "D": "L2", "E2": "L2", "F": "L2"},
        "note": "室内地面铺设的古典波斯红色提花羊毛地毯大面积欠饱和严重脱色错涂为灰黑冷色，橘猫身上原本温润明亮的橘黄斑纹皮毛欠饱和褪色为灰暗色(C-L2, D-L2, E2-L2, F-L2)。"
    },
    8096: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8097: {
        "score": 4.55,
        "severities": {"C": "L2", "D": "L2", "E2": "L2", "F": "L2"},
        "note": "古典钟楼背后原本清透纯正的深蓝色晴空大面积欠饱和严重脱色错涂为惨白灰暗阴天死色(C-L2, E2-L2)，钟楼红砖外墙欠饱和泛冷灰偏色(D-L2)，视觉自然度受损(F-L2)。"
    },

    # Sheet 16
    8099: {
        "score": 2.56,
        "severities": {},
        "note": "审查通过"
    },
    8100: {
        "score": 2.47,
        "severities": {"D": "L1", "E1": "L2", "F": "L1"},
        "note": "厨房黑色台面上放置的巧克力蛋糕表面与金属锡纸衬底大面积浸染过度浓艳刺眼的深洋红紫偏色(E1-L2)，暗部色温偏冷紫(D-L1)，视觉自然度受损(F-L1)。"
    },
    8101: {
        "score": 2.47,
        "severities": {},
        "note": "审查通过"
    },
    8107: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8108: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8109: {
        "score": 4.55,
        "severities": {"C": "L2", "D": "L1", "E2": "L1", "F": "L1"},
        "note": "沿街商铺门前悬挂的黄色与红色塑料遮阳雨棚大面积欠饱和严重脱色褪色为暗沉枯灰褐色(C-L2, E2-L1)，街景整体色调泛冷灰暗淡(D-L1)，视觉自然度受损(F-L1)。"
    },

    # Sheet 17
    8110: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8111: {
        "score": 2.27,
        "severities": {},
        "note": "审查通过"
    },
    8113: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8115: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "长颈鹿身旁原本茂密葱郁的翠绿色大树树冠大面积欠饱和褪色为暗沉灰白阴天色(E2-L1)，长颈鹿斑纹色泽微偏暗冷(D-L1)。"
    },
    8116: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    8117: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L1", "F": "L1"},
        "note": "铁路上驶来的通勤列车车头正面标志性的明亮橙黄色涂装横条被颠覆性错涂为亮紫粉红色(C-L2)，铁路轨道色温微偏暖偏色(D-L1)，视觉自然度受损(F-L1)。"
    },

    # Sheet 18
    8118: {
        "score": 2.23,
        "severities": {"C": "L3", "E2": "L1", "F": "L2"},
        "note": "洗漱塑料杯内插着的高露洁（Colgate）牙膏包装管原本标志性的鲜艳大红色底色被彻底颠覆性错涂为亮宝蓝色(C-L3)，牙膏管品牌色彩完全错乱，视觉自然度受损(F-L2)。"
    },
    8120: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "餐厅长桌聚餐人群后方墙壁与宾客服饰大面积浸染失真偏浓艳的洋红紫冷色偏色(D-L1, E1-L1)，室内聚餐温馨暖调氛围受损(F-L1)。"
    },
    8121: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8122: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "案板上涂抹的披萨底酱鲜红色番茄酱汁表面色彩过度浓艳偏深红(E1-L1)，案板操作台面整体微泛暖红偏色(D-L1)。"
    },
    8123: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8124: {
        "score": 2.56,
        "severities": {"C": "L3", "D": "L1", "E1": "L1", "F": "L2"},
        "note": "沿街停放的复古经典老爷车车身原本清透纯正的宝蓝色车漆被彻底颠覆性错涂为鲜艳的大红色(C-L3)，后方货车车身也出现明显变色，车辆视觉质感严重失真(F-L2)。"
    },

    # Sheet 19
    8125: {
        "score": 4.46,
        "severities": {},
        "note": "审查通过"
    },
    8126: {
        "score": 2.17,
        "severities": {},
        "note": "审查通过"
    },
    8128: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8129: {
        "score": 1.34,
        "severities": {"C": "L3", "D": "L2", "E2": "L2", "F": "L2"},
        "note": "候机大厅钢结构玻璃幕墙外原本纯净湛蓝的晴空背景大面积欠饱和严重脱色错涂为惨白阴冷死灰色，大厅地表与承重柱浸染阴冷发暗偏色(C-L3, D-L2, E2-L2, F-L2)。"
    },
    8131: {
        "score": 2.47,
        "severities": {"D": "L1"},
        "note": "餐盘内盛放的炒鸡蛋表面金黄色泽略显轻微偏淡(D-L1)，轻度偏色。"
    },
    8132: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 20
    8133: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8134: {
        "score": 2.09,
        "severities": {"C": "L3", "D": "L2", "E2": "L2", "F": "L2"},
        "note": "家庭影院室内原本温暖明快的亮橙色布艺组合沙发大面积欠饱和严重脱色错涂为惨白暗灰浅绿色死色，实木护墙板大面积欠饱和褪色发冷，温馨暖色氛围彻底丧失(C-L3, D-L2, E2-L2, F-L2)。"
    },
    8135: {
        "score": 5.0,
        "severities": {"C": "L3", "E2": "L2", "F": "L2"},
        "note": "餐桌黑漆托盘左右两侧铺垫的明亮翠绿色与亮橙色餐巾布艺大面积欠饱和严重脱色错涂为灰白死色，两块餐巾鲜明装饰色彩完全丧失(C-L3, E2-L2, F-L2)。"
    },
    8137: {
        "score": 2.17,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "电视机屏幕内转播的足球比赛绿茵场草坪色彩略显过于浓艳偏黄绿色(E1-L1)，屏幕光影微偏暖(D-L1)。"
    },
    8139: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    8142: {
        "score": 2.56,
        "severities": {},
        "note": "审查通过"
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

def main():
    print(f"Batch 40 defined reviews count: {len(REVIEWS_B40)}")
    assert len(REVIEWS_B40) == 120, f"Expected 120 reviews, got {len(REVIEWS_B40)}"

    # 1. 导出中间具象定物判决 JSON
    out_grounding_path = "LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_40.json"
    with open(out_grounding_path, "w", encoding="utf-8") as f:
        json.dump(REVIEWS_B40, f, ensure_ascii=False, indent=2)
    print(f"Exported grounding reviews to {out_grounding_path}")

    # 2. 读取正式交付文件
    all_path = "LS_lcad_reviewer/exports/reviewed_1_10000_all.json"
    clean_path = "LS_lcad_reviewer/exports/reviewed_1_10000_clean.json"

    with open(all_path, "r", encoding="utf-8") as f:
        data_all = json.load(f)

    with open(clean_path, "r", encoding="utf-8") as f:
        data_clean = json.load(f)

    anns_all = data_all["annotations"]
    anns_clean = data_clean["annotations"]

    # 建立 task_id 索引映射
    idx_map_all = {ann["human_review"]["task_id"]: i for i, ann in enumerate(anns_all)}
    idx_map_clean = {ann["human_review"]["task_id"]: i for i, ann in enumerate(anns_clean)}

    updated_count = 0
    passed_count = 0
    revised_count = 0

    for tid, rev in REVIEWS_B40.items():
        if tid not in idx_map_all:
            print(f"Warning: task_id {tid} not found in all dataset!")
            continue

        ann_a = anns_all[idx_map_all[tid]]
        ann_c = anns_clean[idx_map_clean[tid]]

        severities = rev["severities"]
        note = rev["note"]

        # 构建 defects 列表
        defects = []
        if severities:
            for code, sev in severities.items():
                defects.append({
                    "id": code,
                    "name": DEFECT_NAME_MAP.get(code, code),
                    "severity": sev,
                    "description": note
                })

        # 判断是否命中 A (缺色)
        has_a = "A" in severities

        # 同步更新 all 版本
        ann_a["review_status"] = "已核验"
        ann_a["review_note"] = note
        ann_a["defects"] = defects
        if has_a:
            ann_a["reviewed_score"] = 1.0
            ann_a["needs_rescoring"] = False
        else:
            ann_a["reviewed_score"] = None
            ann_a["needs_rescoring"] = True

        # 同步更新 clean 版本 (review_note 清空)
        ann_c["review_status"] = "已核验"
        ann_c["review_note"] = ""
        ann_c["defects"] = defects
        if has_a:
            ann_c["reviewed_score"] = 1.0
            ann_c["needs_rescoring"] = False
        else:
            ann_c["reviewed_score"] = None
            ann_c["needs_rescoring"] = True

        updated_count += 1
        if len(severities) == 0:
            passed_count += 1
        else:
            revised_count += 1

    print(f"Updated: {updated_count} (Passed: {passed_count}, Revised: {revised_count})")

    # 写回文件
    with open(all_path, "w", encoding="utf-8") as f:
        json.dump(data_all, f, ensure_ascii=False, indent=2)
    print(f"Synchronized {all_path}")

    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(data_clean, f, ensure_ascii=False, indent=2)
    print(f"Synchronized {clean_path}")

if __name__ == "__main__":
    main()
