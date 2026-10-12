# -*- coding: utf-8 -*-
"""
应用 Batch 39 审核具象定物判决字典并双向同步至正式交付文件
Batch 39: Task #7760 ~ #7943 (共 120 组)
"""

import json
import os
import re

# 120 组人工直审与具象定物判决字典
REVIEWS_B39 = {
    # Sheet 01
    7760: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7761: {
        "score": 4.46,
        "severities": {},
        "note": "审查通过"
    },
    7763: {
        "score": 2.47,
        "severities": {"C": "L2", "E2": "L2", "F": "L2"},
        "note": "床铺上黑白花猫身旁堆放的鲜红色针织毛衣大面积欠饱和严重脱色错涂为灰黑死色，原衣物鲜明色彩彻底丧失(C-L2, E2-L2, F-L2)。"
    },
    7764: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "沿街商铺外墙红砖立面与人行道禁停交通警示牌大面积欠饱和褪色发灰偏暗(D-L1, E2-L1)。"
    },
    7766: {
        "score": 2.17,
        "severities": {},
        "note": "审查通过"
    },
    7767: {
        "score": 2.36,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 02
    7768: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7770: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7771: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7772: {
        "score": 2.43,
        "severities": {},
        "note": "审查通过"
    },
    7774: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7775: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 03
    7776: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7777: {
        "score": 5.0,
        "severities": {"E2": "L1"},
        "note": "商场大厅人潮拥挤的顾客群众服饰大面积欠饱和发暗(E2-L1)。"
    },
    7778: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "曼哈顿街头摩天大楼背后的纯净深蓝晴空大面积欠饱和褪色为灰白泛暗阴天色(D-L1, E2-L1)。"
    },
    7779: {
        "score": 2.36,
        "severities": {"C": "L2", "D": "L2", "F": "L2"},
        "note": "晴空下的稀树草原上空原本清澈的天蓝色天空被彻底脱色错涂为惨白灰黄死色，草甸与长颈鹿浸染焦黄暖偏色(C-L2, D-L2, F-L2)。"
    },
    7781: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7782: {
        "score": 2.47,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 04
    7789: {
        "score": 2.32,
        "severities": {"D": "L2", "E1": "L1", "F": "L2"},
        "note": "码头停泊的白色机动游艇船体与水面倒影大面积浸染失真浓艳的洋红紫冷色偏色，水面色温严重失真(D-L2, E1-L1, F-L2)。"
    },
    7790: {
        "score": 2.36,
        "severities": {},
        "note": "审查通过"
    },
    7791: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "长颈鹿奔跑的稀树草原沙土干燥地面大面积浸染过度浓艳刺眼的火红砖红暖偏色，色彩明显过饱和(D-L1, E1-L1, F-L1)。"
    },
    7792: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7793: {
        "score": 2.27,
        "severities": {"C": "L3", "D": "L1", "F": "L2"},
        "note": "木吉他琴身前放置的圆形塑料飞盘外圈原本鲜艳明朗的橙红色被彻底颠覆性错涂为冰冷亮蓝色(C-L3, D-L1, F-L2)。"
    },
    7794: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 05
    7795: {
        "score": 2.47,
        "severities": {"C": "L2", "D": "L2", "E2": "L2", "F": "L1"},
        "note": "餐厅吧台背景摆放的高脚软包靠背椅原本明艳的深红紫色大面积欠饱和严重脱色错涂为灰黑死色，水杯浸染失真蓝斑(C-L2, D-L2, E2-L2, F-L1)。"
    },
    7797: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7798: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L1", "F": "L1"},
        "note": "会议办公长桌近处摆放的亮粉红色硅胶鼠标垫被颠覆性错涂为亮天蓝色(C-L2, D-L1, F-L1)。"
    },
    7800: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7803: {
        "score": 2.47,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "古典卧室木质四柱大床周围的暖黄光墙面与窗台大面积欠饱和褪色为阴冷死灰色，室内温馨氛围完全失真(D-L2, E2-L2, F-L2)。"
    },
    7804: {
        "score": 2.17,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 06
    7805: {
        "score": 2.43,
        "severities": {},
        "note": "审查通过"
    },
    7807: {
        "score": 2.73,
        "severities": {"C": "L3", "E2": "L2", "F": "L2"},
        "note": "看台通道旁人员撑着的法拉利赛车周边鲜红色雨伞与工作人员红色制服大面积欠饱和严重脱色错涂为灰黑死色，法拉利标志性红色荡然无存(C-L3, E2-L2, F-L2)。"
    },
    7808: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7811: {
        "score": 2.17,
        "severities": {"D": "L2", "E2": "L1"},
        "note": "傍晚游乐园上空原本深邃清透的深蓝色暮色晴空大面积欠饱和褪色为暗沉灰白色(D-L2, E2-L1)。"
    },
    7812: {
        "score": 2.13,
        "severities": {},
        "note": "审查通过"
    },
    7814: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "长颈鹿面部额头与鼻梁处的棕黄皮毛色彩略显过于浓艳偏红暖色，轻度过饱和(D-L1, E1-L1)。"
    },

    # Sheet 07
    7816: {
        "score": 2.17,
        "severities": {},
        "note": "审查通过"
    },
    7818: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "砖石结构钟楼外立面红砖墙体大面积浸染失真偏浓艳的紫红暖偏色，色彩轻度过饱和(D-L1, E1-L1)。"
    },
    7819: {
        "score": 4.46,
        "severities": {},
        "note": "审查通过"
    },
    7823: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7824: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7826: {
        "score": 4.55,
        "severities": {"C": "L2", "E2": "L2", "F": "L1"},
        "note": "棒球场上投手身穿的旧金山巨人队标志性鲜艳橙红色长袖训练内搭大面积欠饱和严重褪色变暗沉灰红(C-L2, E2-L2, F-L1)。"
    },

    # Sheet 08
    7828: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7829: {
        "score": 2.61,
        "severities": {"C": "L2", "D": "L2", "E2": "L2", "F": "L2"},
        "note": "卫生间洗手台周围墙面原本温暖的鹅黄色瓷砖大面积欠饱和严重脱色错涂为冰冷惨白死灰色，环境色温严重失真(C-L2, D-L2, E2-L2, F-L2)。"
    },
    7830: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7831: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "室内铺设的红褐色实木地板表面大面积欠饱和褪色为阴冷灰褐色，缺乏原本的温润木质暖色(D-L1, E2-L1)。"
    },
    7832: {
        "score": 2.23,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "酒店客房窗边垂挂的浅色窗帘与地面拼花地毯大面积欠饱和褪色为发冷死灰色，室内温馨氛围失真(D-L1, E2-L1, F-L1)。"
    },
    7833: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 09
    7834: {
        "score": 5.0,
        "severities": {"B": "L1", "D": "L1", "F": "L1"},
        "note": "警用巡逻摩托车前右侧车灯部位浸染失真浓艳的亮蓝光斑，警灯局部微泛溢色(B-L1, D-L1, F-L1)。"
    },
    7836: {
        "score": 2.47,
        "severities": {"C": "L2", "D": "L2", "E2": "L2"},
        "note": "棒球场围栏旁的红土地面与少年身穿的红白拼色球衣大面积欠饱和严重脱色为阴暗冷灰色，红土质感完全丧失(C-L2, D-L2, E2-L2)。"
    },
    7837: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7840: {
        "score": 2.73,
        "severities": {},
        "note": "审查通过"
    },
    7844: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7845: {
        "score": 2.61,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 10
    7847: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7848: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7849: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "室内男子身穿的深红色针织毛衣大面积欠饱和褪色为灰暗冷色，室内暖调变冷(D-L1, E2-L1)。"
    },
    7853: {
        "score": 2.17,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "街边黄色花岗岩交通街区路标石碑表面色彩略显过于浓艳偏红暖色，暗部微泛蓝紫杂色偏色(D-L1, E1-L1, F-L1)。"
    },
    7854: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7857: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "雪地上站立的滑雪者身穿的荧光黄绿、正红与宝蓝色滑雪服色彩明显过于浓艳刺眼，局部过饱和(D-L1, E1-L1, F-L1)。"
    },

    # Sheet 11
    7858: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "稀树草原上斑马脚下的金黄色草甸大面积欠饱和严重褪色变暗沉灰白，失去金黄热带阳光质感(D-L1, E2-L1)。"
    },
    7859: {
        "score": 2.17,
        "severities": {"D": "L1", "E2": "L2", "F": "L1"},
        "note": "卫生间洗手台陶瓷水槽与周围塑料隔板墙面大面积欠饱和脱色为冰冷泛青灰死色(D-L1, E2-L2, F-L1)。"
    },
    7860: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7862: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L1"},
        "note": "餐桌后方墙面上悬挂装饰的各色派对纸拉花彩球大面积欠饱和褪色为灰白杂色(C-L2, E2-L1)。"
    },
    7863: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L1"},
        "note": "农展会展台地面铺设的鲜红色展示绒毯与工作人员的红色领带大面积欠饱和褪色为暗沉灰白色(C-L2, E2-L1)。"
    },
    7869: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 12
    7870: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7872: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L1"},
        "note": "木地板上放置的圆形陶瓷猫盘内壁原本明亮的翠绿色釉面被颠覆性错涂为红棕色(C-L2, D-L1)。"
    },
    7873: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7877: {
        "score": 2.43,
        "severities": {},
        "note": "审查通过"
    },
    7878: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "电脑桌背景堆放的黄色CD收纳塑料包装盒大面积欠饱和褪色变发白浅黄(D-L1, E2-L1)。"
    },
    7879: {
        "score": 2.17,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 13
    7882: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7884: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L1"},
        "note": "车内儿童安全座椅杯架中放置的香蕉皮原本鲜黄果皮欠饱和脱色为暗沉枯灰色(C-L2, E2-L1)。"
    },
    7885: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7886: {
        "score": 1.06,
        "severities": {"C": "L3", "E1": "L2", "F": "L2"},
        "note": "蓝色塑料洗菜果篮中原本黄绿色的青苹果被颠覆性错涂为荧光亮粉红色(C-L3, E1-L2, F-L2)。"
    },
    7887: {
        "score": 1.0,
        "severities": {"A": ""},
        "note": "卫生间洗手台水槽与地面墙砖全域上色彻底失败，呈现完全无色彩的纯黑白灰阶状态。"
    },
    7888: {
        "score": 2.17,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 14
    7890: {
        "score": 2.17,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "长颈鹿面部与颈部的棕黄色斑纹皮毛以及背景灌木枝叶大面积欠饱和严重脱色为发暗灰褐色与阴冷灰白色，丧失原本生动的暖黄毛色(D-L2, E2-L2, F-L2)。"
    },
    7893: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    7895: {
        "score": 5.0,
        "severities": {"D": "L1"},
        "note": "车库内停放的复古双层巴士车身下半部分原本明艳的深红色漆面浸染轻微发暗的紫红偏色(D-L1)。"
    },
    7896: {
        "score": 2.32,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "卫生间洗手台陶瓷水槽、坐便器以及周围暖黄光照瓷砖墙面大面积欠饱和褪色为阴冷灰白色，室内温馨暖调环境光明显失真(D-L1, E2-L1, F-L1)。"
    },
    7898: {
        "score": 2.73,
        "severities": {"C": "L2", "E2": "L2", "F": "L2"},
        "note": "老人生日宴上老太太身穿的鲜艳深红色碎花衬衫大面积欠饱和严重脱色错涂为灰黑死色，桌上生日蛋糕的粉红奶油花色泽黯淡(C-L2, E2-L2, F-L2)。"
    },
    7899: {
        "score": 2.87,
        "severities": {"C": "L2", "D": "L2", "E2": "L2", "F": "L2"},
        "note": "保龄球馆内黄色木质保龄球道以及背景墙面原本鲜艳明快的明黄色与橙色装饰色块大面积欠饱和褪色并浸染阴冷深蓝偏色，木道温润质感丧失(C-L2, D-L2, E2-L2, F-L2)。"
    },

    # Sheet 15
    7900: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7902: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7903: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7904: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    7905: {
        "score": 2.36,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "临街店铺橱窗内展示的明黄色自行车车架与黄色招牌图案大面积欠饱和褪色变灰暗，沿街店铺外立面木质墙面浸染阴冷泛青紫偏色(D-L2, E2-L2, F-L2)。"
    },
    7908: {
        "score": 2.43,
        "severities": {"E1": "L1", "F": "L1"},
        "note": "绿茵足球场上防守队员身穿的鲜红色运动短袖T恤局部色彩略显浓暗(E1-L1)，视觉自然度轻微受损(F-L1)。"
    },

    # Sheet 16
    7909: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L2"},
        "note": "窗台上放置的玻璃密封罐内干意大利面条与毛线团色彩明显过度浓艳偏深橙黄色(E1-L2)，右侧白色墙面与窗框轻微偏暖粉红(D-L1)。"
    },
    7911: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7912: {
        "score": 2.47,
        "severities": {"D": "L1", "E1": "L2", "F": "L1"},
        "note": "室内聚会合影中女士身穿的深红紫色吊带长裙与身旁男士佩戴的红色斜纹领带色彩过度浓艳刺眼(E1-L2)，人物面部肤色微泛暖红偏色(D-L1)，视觉自然度受损(F-L1)。"
    },
    7914: {
        "score": 2.61,
        "severities": {"D": "L1"},
        "note": "立柜顶部摆放的复古红色皮革手提旅行箱表面皮革色彩略显暗沉泛棕(D-L1)，轻度偏色。"
    },
    7915: {
        "score": 2.47,
        "severities": {"C": "L2", "D": "L1", "E2": "L2", "F": "L2"},
        "note": "卫生间百叶窗上垂挂的橙黄色荷叶边窗帘布艺大面积欠饱和严重脱色错涂为灰白色，室内暖调环境光完全丧失并泛冷灰偏色(C-L2, D-L1, E2-L2, F-L2)。"
    },
    7916: {
        "score": 4.55,
        "severities": {"C": "L2", "E2": "L1", "F": "L1"},
        "note": "汽车后座安全座椅上放置的毛绒泰迪熊金黄色玩偶毛发大面积欠饱和褪色为泛白浅米色，小熊身穿的彩色小马甲印花脱色发暗(C-L2, E2-L1, F-L1)。"
    },

    # Sheet 17
    7917: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "石头垒砌矮墙前山羊脚下的绿色杂草草坡大面积欠饱和褪色为暗沉灰绿色(E2-L1)，草地微偏暗青冷调(D-L1)。"
    },
    7918: {
        "score": 2.13,
        "severities": {},
        "note": "审查通过"
    },
    7919: {
        "score": 1.05,
        "severities": {"C": "L3", "D": "L1", "E2": "L2", "F": "L2"},
        "note": "网球场内原本鲜明纯正的蓝色塑胶硬地球场地表大面积欠饱和严重脱色错涂为惨白水泥灰死色，网球场标志性蓝色涂装彻底丧失(C-L3, D-L1, E2-L2, F-L2)。"
    },
    7921: {
        "score": 2.17,
        "severities": {},
        "note": "审查通过"
    },
    7922: {
        "score": 1.07,
        "severities": {},
        "note": "审查通过"
    },
    7923: {
        "score": 2.43,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 18
    7924: {
        "score": 2.61,
        "severities": {},
        "note": "审查通过"
    },
    7927: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7928: {
        "score": 2.73,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "电脑工作台原木色电脑桌面与上方多层木质置物架大面积欠饱和褪色为灰白发暗冷色(E2-L1)，实木家具温润木色微偏冷灰(D-L1)。"
    },
    7929: {
        "score": 2.27,
        "severities": {"C": "L2", "D": "L1", "E2": "L2", "F": "L2"},
        "note": "日式料理漆器托盘中摆放的金黄酥脆天妇罗炸虾面衣大面积欠饱和严重脱色错涂为惨白死色，生鱼片刺身肉质黯淡发暗，实木桌面色温泛冷(C-L2, D-L1, E2-L2, F-L2)。"
    },
    7930: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "巨大管状海浪水幕内壁原本清澈透亮的碧绿色海水大面积欠饱和褪色为暗沉青灰色(E2-L1)，水浪色调微泛灰冷(D-L1)。"
    },
    7932: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L2", "F": "L1"},
        "note": "长颈鹿背后的茂密灌木树丛翠绿树叶大面积欠饱和严重褪色变灰白暗淡(E2-L2)，长颈鹿面部棕黄斑纹色泽暗淡泛灰冷偏色(D-L1)，视觉自然度受损(F-L1)。"
    },

    # Sheet 19
    7933: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    7934: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L1", "E2": "L1"},
        "note": "披萨外卖店门头上悬挂的鲜红色与翠绿色亚克力发光店招灯箱大面积欠饱和褪色错涂为暗沉棕红与枯黄色，店牌招牌活力严重丧失(C-L2, D-L1, E2-L1)。"
    },
    7936: {
        "score": 2.56,
        "severities": {},
        "note": "审查通过"
    },
    7938: {
        "score": 2.27,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "特写镜头中盛开的向日葵金黄色花瓣色彩略显过度浓艳刺眼(E1-L1)，前方陶瓷小碗边缘泛轻微冷偏色(D-L1)，视觉自然度轻度受损(F-L1)。"
    },
    7939: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "一次性餐盒内盛放的烤三明治表面焦香吐司面包片色彩过度浓艳偏暗红暖色(E1-L1)，蔬菜沙拉色调微偏浓深(D-L1)。"
    },
    7940: {
        "score": 2.56,
        "severities": {"D": "L2", "E1": "L1", "F": "L2"},
        "note": "棒球场本垒后方看台围栏原本翠绿色的金属防冲撞软包护网大面积浸染发暗的深青蓝色冷偏色，红土球场本垒地面偏暗红，全场冷暖色调严重失衡(D-L2, E1-L1, F-L2)。"
    },

    # Sheet 20
    7942: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "棒球场击球区铺设的红土内野地面以及击球手头戴的红色击球头盔色彩略显过度浓艳偏深红暖色(E1-L1)，场地整体色温微偏暖(D-L1)。"
    },
    7943: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    7944: {
        "score": 1.06,
        "severities": {"C": "L3", "E2": "L1", "F": "L2"},
        "note": "雪地上玩耍者右手手持的鲜艳亮粉红色圆形塑料飞盘大面积欠饱和严重脱色错涂为发暗灰红色，金毛犬背部皮毛轻微褪色(C-L3, E2-L1, F-L2)。"
    },
    7948: {
        "score": 2.47,
        "severities": {"C": "L2", "D": "L1", "E2": "L2", "F": "L2"},
        "note": "窗台前摆放的复古苹果电脑半透明青柠绿色塑料外壳与半透明球形鼠标大面积欠饱和严重脱色错涂为灰白死色，标志性苹果果冻色彩完全丧失(C-L2, D-L1, E2-L2, F-L2)。"
    },
    7950: {
        "score": 2.56,
        "severities": {},
        "note": "审查通过"
    },
    7951: {
        "score": 2.43,
        "severities": {"C": "L3", "E1": "L1", "F": "L2"},
        "note": "巡游花车车头悬挂的宣传布标横幅原本白底黑字布面被颠覆性严重错涂为高亮荧光黄绿色底，车前草绿色装饰布毯色彩轻度过饱和(C-L3, E1-L1, F-L2)。"
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
    print(f"Batch 39 defined reviews count: {len(REVIEWS_B39)}")
    assert len(REVIEWS_B39) == 120, f"Expected 120 reviews, got {len(REVIEWS_B39)}"

    # 1. 导出中间具象定物判决 JSON
    out_grounding_path = "LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_39.json"
    with open(out_grounding_path, "w", encoding="utf-8") as f:
        json.dump(REVIEWS_B39, f, ensure_ascii=False, indent=2)
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

    for tid, rev in REVIEWS_B39.items():
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
