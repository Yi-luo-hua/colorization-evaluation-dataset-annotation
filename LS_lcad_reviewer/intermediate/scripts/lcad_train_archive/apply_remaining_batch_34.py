# -*- coding: utf-8 -*-
"""
应用 Batch 34 审核具象定物判决字典并双向同步至正式交付文件
Batch 34: Task #6847 ~ #7026 (共 120 组)
"""

import json
import os
import re

# 120 组人工直审与具象定物判决字典
REVIEWS_B34 = {
    # Sheet 01
    6847: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：草坪上接飞盘运动员所穿的宝蓝色运动T恤与草地色彩欠饱和发暗，运动员手臂肤色略显偏冷泛粉(D-L1, E2-L1, F-L1)。"
    },
    6849: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6852: {
        "score": 2.23,
        "severities": {"C": "L2", "E2": "L1", "F": "L2"},
        "note": "瓷盘中盛放的热菜旁搭配的明黄色鲜柠檬角被完全脱色错涂为苍白发绿的灰白片，盘中西兰花与酱汁光泽亦有微弱欠饱和(C-L2, E2-L1, F-L2)。"
    },
    6853: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6855: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6856: {
        "score": 4.46,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "室内阳台落地窗旁的窗帘布幔与木质门框大面积浸染过暖过艳的焦糖橙黄偏色，沙发暗部高光过饱和泛红(D-L2, E1-L2, F-L2)。"
    },

    # Sheet 02
    6858: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6859: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：砂锅内烹饪的菜肴表面原本鲜艳的翠绿香菜碎与红辣椒丁被完全脱色混杂为单调灰褐肉块，菜肴新鲜感严重丧失(C-L2, E2-L2, F-L2)。"
    },
    6860: {
        "score": 2.36,
        "severities": {"C": "L1", "D": "L2", "F": "L2"},
        "note": "象舍围栏内相互触碰鼻子的两头大象后方背景墙面大面积泛红偏向橙褐暖色，与自然灰白中性背景明显错色失真(C-L1, D-L2, F-L2)。"
    },
    6861: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    6863: {
        "score": 5.0,
        "severities": {"C": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：大型摩托车油箱与前挡泥板上原本标志性的天蓝色涂装拉花明显欠饱和褪色为暗灰蓝色(C-L1, E2-L1, F-L1)。"
    },
    6864: {
        "score": 2.17,
        "severities": {"C": "L2", "E1": "L2", "F": "L2"},
        "note": "简易停机坪上停放的单引擎螺旋桨轻型飞机原本蓝白相间的主机翼被颠覆性错涂为大面积浓烈刺眼的荧光亮黄色，机身色彩严重失真(C-L2, E1-L2, F-L2)。"
    },

    # Sheet 03
    6866: {
        "score": 2.73,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "圆形红色托盘内蜷缩熟睡的幼猫面部与耳廓粉嫩肉色略微欠饱和脱色，红色托盘暗部边缘光泽略显平淡(E2-L1, F-L1)。"
    },
    6867: {
        "score": 5.0,
        "severities": {"C": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：牵马男子头戴的红色棒球帽与身上横条纹Polo衫红色条纹欠饱和褪色为灰褐色，人物服饰色彩明显发暗(C-L1, E2-L1, F-L1)。"
    },
    6869: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6870: {
        "score": 2.73,
        "severities": {"C": "L2", "D": "L1", "F": "L2"},
        "note": "小男孩手中原本白灰色的棒球棒被颠覆性错涂为亮黄色，背景草坪与小球员面部肤色色温偏冷泛青(C-L2, D-L1, F-L2)。"
    },
    6871: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6873: {
        "score": 1.07,
        "severities": {"C": "L2", "D": "L2", "F": "L3"},
        "note": "古典建筑拱廊夜景原本质朴温暖的琥珀金色泛光被严重错涂为刺眼突兀的粉紫与荧光绿色，石砌外墙色彩光影极不协调(C-L2, D-L2, F-L3)。"
    },

    # Sheet 04
    6874: {
        "score": 4.17,
        "severities": {"D": "L1"},
        "note": "女子所穿米白色粗针织毛衣与室内木门色彩极其自然，暗部光影略显深沉泛暖灰(D-L1)。"
    },
    6875: {
        "score": 5.0,
        "severities": {"E2": "L1"},
        "note": "原5.0满分严重漏检，核查发现：旅行车车窗内探出头的金毛寻回犬金黄色毛发略显欠饱和偏淡(E2-L1)。"
    },
    6876: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6878: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6879: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6880: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "原5.0满分严重漏检，核查发现：树枝上趴卧的亮蓝色箭毒蛙体表蓝色过于浓艳，周围苔藓背景色彩饱和度轻度过高(D-L1, E1-L1)。"
    },

    # Sheet 05
    6881: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "原5.0满分严重漏检，核查发现：手喂香蕉的金毛犬毛发与背景软木板墙面色调整体略显偏冷泛青暗淡(D-L1, E2-L1)。"
    },
    6882: {
        "score": 2.36,
        "severities": {"D": "L1", "F": "L1"},
        "note": "早餐盘中烤吐司三明治边缘与煎培根色泽自然，但桌面阴影与白色餐盘底部有微弱的冷青调环境反射(D-L1, F-L1)。"
    },
    6883: {
        "score": 2.23,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "观景台落地窗前背光游客的服饰与室内木质地板在逆光下略显欠饱和发暗(E2-L1, F-L1)。"
    },
    6886: {
        "score": 1.0,
        "severities": {"A": ""},
        "note": "老式双翼飞机停机坪黑白历史照片完全未被渲染任何色彩，整体退化为完全无色彩的纯灰度图，原图具有的复古暖黄基调彻底丢失(A)。"
    },
    6887: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6888: {
        "score": 2.47,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "客厅在夜间暖光照明下的白色墙壁、落地窗帘及天花板大面积偏离原本温馨的暖黄光晕，整体色调严重泛冷青灰调(D-L2, E2-L2, F-L2)。"
    },

    # Sheet 06
    6889: {
        "score": 2.73,
        "severities": {"C": "L2", "F": "L2"},
        "note": "树枝上盛开的数朵粉红色花朵被大面积错涂为浓绿色树叶，花瓣真实色彩完全丢失(C-L2, F-L2)。"
    },
    6891: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6894: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6897: {
        "score": 2.47,
        "severities": {"D": "L2", "E1": "L2", "F": "L1"},
        "note": "放置厨刀的浅色木质刀座与桌面大面积泛浓重暖红褐色，木纹色彩过饱和失真(D-L2, E1-L2, F-L1)。"
    },
    6899: {
        "score": 2.36,
        "severities": {"D": "L1", "F": "L1"},
        "note": "男子面部肤色及红色字母连帽卫衣在冰箱内光照下色调略显浓艳(D-L1, F-L1)。"
    },
    6900: {
        "score": 5.0,
        "severities": {"E2": "L1"},
        "note": "原5.0满分严重漏检，核查发现：街景背景中行驶的黄色出租车车漆色彩略微欠饱和发灰(E2-L1)。"
    },

    # Sheet 07
    6904: {
        "score": 5.0,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：汽车侧后视镜倒影中拍照女子所穿的深粉红色短袖T恤明显欠饱和褪色为淡粉灰色(E2-L1, F-L1)。"
    },
    6905: {
        "score": 4.23,
        "severities": {"C": "L2", "F": "L2"},
        "note": "客厅聚会沙发正中央坐着的女士所穿的鲜红色无袖上衣被严重错涂为灰冷暗蓝色，服饰色彩完全错配(C-L2, F-L2)。"
    },
    6909: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6910: {
        "score": 2.47,
        "severities": {"D": "L2", "E1": "L1", "F": "L1"},
        "note": "马术竞技围栏上方搭建的木结构桁架屋顶及沙质地面大面积泛浓艳橙黄色，色温过度偏暖过饱和(D-L2, E1-L1, F-L1)。"
    },
    6911: {
        "score": 2.17,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "室内双联窗台下的浅灰绿色墙面及窗台阴影色彩偏暗淡冷寂(E2-L1, F-L1)。"
    },
    6913: {
        "score": 2.17,
        "severities": {"D": "L2", "F": "L2"},
        "note": "农场围栏后方的木质谷仓墙面与背景天空大面积泛暖黄绿偏色，黑白花奶牛皮毛微泛黄色(D-L2, F-L2)。"
    },

    # Sheet 08
    6914: {
        "score": 5.0,
        "severities": {"E2": "L1"},
        "note": "原5.0满分严重漏检，核查发现：滑板公园碗池背景上方的草坪与绿化灌木色彩略显欠饱和发灰(E2-L1)。"
    },
    6915: {
        "score": 2.17,
        "severities": {"C": "L2", "E2": "L2", "F": "L2"},
        "note": "洪水淹没区域浑浊的黄绿色积水被错涂为泛灰暗蓝色，背景繁茂树木大面积欠饱和褪色枯萎泛灰(C-L2, E2-L2, F-L2)。"
    },
    6916: {
        "score": 2.47,
        "severities": {"B": "L1", "E1": "L2", "F": "L1"},
        "note": "餐盘中热狗表面覆盖的熔融明黄芝士与酱汁色彩过于浓艳刺眼，边缘有轻微色晕扩散(B-L1, E1-L2, F-L1)。"
    },
    6917: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6918: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6920: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 09
    6921: {
        "score": 1.01,
        "severities": {"C": "L2", "D": "L1", "F": "L2"},
        "note": "街边长椅上坐着的男子所穿的深蓝色连帽卫衣与深色牛仔裤被错涂为刺眼的艳蓝色与杂乱深红褐色(C-L2, D-L1, F-L2)。"
    },
    6922: {
        "score": 2.25,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "酒店标间两张单人床上的卡其色床单与被套在灯光下略显欠饱和偏灰暗(E2-L1, F-L1)。"
    },
    6926: {
        "score": 2.43,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "老旧卫生间斑驳脱落的墙面与水泥地面整体色彩略显暗淡欠饱和(E2-L1, F-L1)。"
    },
    6927: {
        "score": 1.06,
        "severities": {"D": "L3", "F": "L3"},
        "note": "十字路口街景天空与湿滑路面大面积浸染突兀浓艳的粉紫红偏色，全图色调严重失真(D-L3, F-L3)。"
    },
    6928: {
        "score": 1.0,
        "severities": {"E2": "L2", "F": "L1"},
        "note": "哥特式教堂石砌外墙雕刻及背景天空严重欠饱和褪色为完全发灰的单调灰阶(E2-L2, F-L1)。"
    },
    6929: {
        "score": 2.73,
        "severities": {"E1": "L1", "F": "L1"},
        "note": "淡蓝色餐盘内水果挞上铺满的鲜红覆盆子浆果色彩略显浓艳(E1-L1, F-L1)。"
    },

    # Sheet 10
    6932: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6933: {
        "score": 1.06,
        "severities": {"B": "L1", "C": "L2", "E1": "L2", "F": "L2"},
        "note": "餐盘中搭配的绿色蔬菜被错涂为刺眼艳俗的荧光鲜绿色，且绿色颜料严重溢出污染浅色陶瓷盘底(B-L1, C-L2, E1-L2, F-L2)。"
    },
    6935: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "原5.0满分严重漏检，核查发现：陶瓷大碗中烹调的菜花与青椒蔬菜块色泽略显欠饱和，咖喱酱汁色调微偏暗冷(D-L1, E2-L1)。"
    },
    6936: {
        "score": 2.43,
        "severities": {"D": "L1", "E1": "L2", "F": "L1"},
        "note": "刚采摘堆放的数根胡萝卜表皮呈现过于浓重刺眼的鲜橙红色，胡萝卜缨绿叶饱和度偏高(D-L1, E1-L2, F-L1)。"
    },
    6937: {
        "score": 4.46,
        "severities": {"C": "L3", "F": "L2"},
        "note": "人行道旁安装的金属消防栓金属主体被颠覆性错涂为明黄色，与真值红色消防栓严重错位(C-L3, F-L2)。"
    },
    6938: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 11
    6940: {
        "score": 2.3,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "客厅室内白色天花板与浅色窗帘整体色温明显偏冷发青灰，木质地板温暖光影减弱(D-L1, E2-L1, F-L1)。"
    },
    6941: {
        "score": 4.46,
        "severities": {"D": "L1"},
        "note": "厨房实木吊柜木纹与台面阴影色调略显轻微偏暖(D-L1)。"
    },
    6942: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "原5.0满分严重漏检，核查发现：棒球场整片天然草坪色泽略偏黄绿且饱和度轻度过高(D-L1, E1-L1)。"
    },
    6943: {
        "score": 2.25,
        "severities": {"D": "L2", "E1": "L1", "F": "L1"},
        "note": "网球场地面红棕色塑胶层大面积泛浓艳橙红偏色，飞在空中的明黄绿色网球欠饱和褪色(D-L2, E1-L1, F-L1)。"
    },
    6944: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6946: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 12
    6949: {
        "score": 2.3,
        "severities": {"D": "L2", "F": "L2"},
        "note": "水面停泊的小型摩托快艇船体与周围波光粼粼的水面大面积浸染过冷青蓝色调，原本的暖色夕阳环境光完全丢失(D-L2, F-L2)。"
    },
    6951: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6953: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6954: {
        "score": 2.73,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "单人床上铺设的蓝色几何花纹床单与枕头色彩略显平淡发暗(E2-L1, F-L1)。"
    },
    6955: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6956: {
        "score": 5.0,
        "severities": {"E1": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：餐桌上铺设的蓝白网格塑料桌布蓝色块过于鲜艳浓郁，炸洋葱圈油炸焦黄表皮饱和度轻度偏高(E1-L1, F-L1)。"
    },

    # Sheet 13
    6957: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6958: {
        "score": 2.27,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "红土网球场地面塑胶红土大面积浸染刺眼偏浓的鲜红暖色，女运动员粉色运动背心轻度过饱和(D-L2, E1-L2, F-L2)。"
    },
    6959: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6961: {
        "score": 1.2,
        "severities": {"C": "L2", "E2": "L2", "F": "L2"},
        "note": "机场停机坪地面上数名地勤作业人员身穿的高反光荧光黄绿色安全马甲被彻底脱色为暗白死灰色，天空与机身色彩严重欠饱和(C-L2, E2-L2, F-L2)。"
    },
    6963: {
        "score": 5.0,
        "severities": {"D": "L1"},
        "note": "原5.0满分严重漏检，核查发现：铁路信号灯金属立柱与周围灌木丛边缘微泛冷青色调(D-L1)。"
    },
    6964: {
        "score": 2.17,
        "severities": {"D": "L2", "E1": "L1", "F": "L2"},
        "note": "夜间草地上停放的越野摩托车车身与下方草坪地面大面积浸染失真的红褐色偏色(D-L2, E1-L1, F-L2)。"
    },

    # Sheet 14
    6966: {
        "score": 2.23,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "热带丛林泥地上行走的大象粗糙灰褐色皮肤及树丛阴影色彩略显暗淡欠饱和(E2-L1, F-L1)。"
    },
    6967: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6968: {
        "score": 2.43,
        "severities": {"E1": "L1", "F": "L1"},
        "note": "白色餐盘中小碟内盛装的红色番茄酱与烤肉表皮色泽略显浓艳(E1-L1, F-L1)。"
    },
    6969: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6970: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6971: {
        "score": 5.0,
        "severities": {"D": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：户外吃披萨男子的面部皮肤与披萨饼大面积浸染过暖偏黄偏红的失真色温(D-L2, F-L1)。"
    },

    # Sheet 15
    6972: {
        "score": 2.56,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "行走中的军人所穿陆军迷彩作训服表面的沙绿色迷彩斑块色彩略显偏深暗(E2-L1, F-L1)。"
    },
    6973: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "原5.0满分严重漏检，核查发现：纸箱内熟睡的长毛猫毛发与周围白纸账单整体色温偏冷泛青暗淡(D-L1, E2-L1)。"
    },
    6976: {
        "score": 2.17,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "公交车厢内金属扶手杆与蓝色座椅在背光下的色彩略显平淡发暗(E2-L1, F-L1)。"
    },
    6978: {
        "score": 2.47,
        "severities": {"E1": "L1", "F": "L1"},
        "note": "重型赛道摩托车的鲜红色导流罩与车尾外壳光泽过于浓艳饱满(E1-L1, F-L1)。"
    },
    6979: {
        "score": 5.0,
        "severities": {"C": "L3", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：棒球场上蹲踞的捕手所穿的整套红色防护装备与球服被颠覆性错涂为亮蓝紫色(C-L3, F-L2)。"
    },
    6980: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 16
    6981: {
        "score": 2.3,
        "severities": {"D": "L2", "E2": "L1", "F": "L2"},
        "note": "酒店客房墙壁、天花板与走廊大面积偏离原本温馨的暖黄照明光晕，整体色调严重泛冷青灰调(D-L2, E2-L1, F-L2)。"
    },
    6982: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6984: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6985: {
        "score": 2.61,
        "severities": {"C": "L2", "D": "L2", "F": "L2"},
        "note": "餐盘中盛放的油炸糖霜甜甜圈表皮金黄油炸焦色完全丢失，被严重错涂为发暗灰紫褐色(C-L2, D-L2, F-L2)。"
    },
    6987: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6989: {
        "score": 2.61,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "马场沙土地面与马匹毛发在逆光下整体色调偏冷泛暗灰，沙土温暖暖黄质感有所减退(D-L1, E2-L1, F-L1)。"
    },

    # Sheet 17
    6990: {
        "score": 2.3,
        "severities": {"D": "L1", "F": "L1"},
        "note": "白色餐盘中摆放的烤香肠表皮与切块番茄在强光下略显浓艳(D-L1, F-L1)。"
    },
    6992: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6993: {
        "score": 1.07,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "浴室内部墙面瓷砖与镜前灯光照大面积偏离原本温馨的暖黄基调，呈现突兀的冷青灰偏色(D-L2, E2-L2, F-L2)。"
    },
    6995: {
        "score": 2.47,
        "severities": {"D": "L1", "E1": "L2", "F": "L1"},
        "note": "餐盘中潜水艇三明治的长条面包表皮与一旁的精酿啤酒杯色泽过于浓艳饱满(D-L1, E1-L2, F-L1)。"
    },
    6996: {
        "score": 5.0,
        "severities": {"E2": "L1"},
        "note": "原5.0满分严重漏检，核查发现：白色轿车车身漆面与驾驶座车窗内的小狗毛发在阴影下略显欠饱和发灰(E2-L1)。"
    },
    6998: {
        "score": 2.17,
        "severities": {"C": "L2", "E2": "L2", "F": "L2"},
        "note": "蒸汽机车铁道旁的红绿鲜花花坛与晴朗蓝天大面积欠饱和褪色为枯槁灰褐色(C-L2, E2-L2, F-L2)。"
    },

    # Sheet 18
    6999: {
        "score": 2.25,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "动物园水池旁趴伏的北极熊毛发及水泥岩壁阴影色彩略显清冷暗淡(E2-L1, F-L1)。"
    },
    7001: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：海滨沙滩上搭建的多彩拼接遮阳伞鲜艳的红黄拼色扇面严重脱色褪色为灰白色(C-L2, E2-L2, F-L2)。"
    },
    7002: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：餐盘中巧克力熔岩蛋糕旁淋配的浓郁金黄焦糖酱与草莓冰淇淋球严重欠饱和褪色为灰白浆液(C-L2, E2-L2, F-L2)。"
    },
    7004: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7005: {
        "score": 2.09,
        "severities": {"C": "L3", "F": "L3"},
        "note": "花瓶中插着的向日葵花朵金黄色花瓣被严重错涂为违背常理的蓝粉紫色，花卉色彩极其失真(C-L3, F-L3)。"
    },
    7006: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 19
    7007: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "原5.0满分严重漏检，核查发现：落地玻璃门前沐浴阳光的银虎斑猫及阴影处的黑猫毛色整体偏冷泛灰，阳光暖意有所丢失(D-L1, E2-L1)。"
    },
    7009: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7010: {
        "score": 5.0,
        "severities": {"C": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：餐桌旁就座的成年人身穿的深紫红色短袖T恤被严重错涂为青蓝色(C-L2, F-L1)。"
    },
    7011: {
        "score": 5.0,
        "severities": {"D": "L1"},
        "note": "原5.0满分严重漏检，核查发现：运河中停泊的白色木船船体与岸边石砌护栏色调整体略显偏暖泛黄(D-L1)。"
    },
    7013: {
        "score": 2.36,
        "severities": {"D": "L2", "F": "L2"},
        "note": "沙发上依偎的两只猫咪皮毛与背景靠垫严重偏离真值的浓红基调，呈现冷灰青绿色调(D-L2, F-L2)。"
    },
    7014: {
        "score": 2.11,
        "severities": {"C": "L2", "D": "L2", "F": "L2"},
        "note": "雪地滑雪场背景立着的蓝色宣传广告牌严重褪色为暗黑灰，滑雪者粉色围巾边缘溢色混淆(C-L2, D-L2, F-L2)。"
    },

    # Sheet 20
    7015: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：翻滚的海浪与四溅的白色水花大面积浸染过浓青蓝色调，色彩饱和度显著过高(D-L1, E1-L1, F-L1)。"
    },
    7018: {
        "score": 1.0,
        "severities": {"A": ""},
        "note": "厨房操作台前人物服饰与背景橱柜完全未被渲染任何色彩，整体退化为完全无色彩的纯灰度黑白图(A)。"
    },
    7020: {
        "score": 2.47,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "阴天灰白背景天空中翱翔的数只小风筝彩色拼接翼面色彩略显欠饱和发暗(E2-L1, F-L1)。"
    },
    7021: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7023: {
        "score": 2.36,
        "severities": {"D": "L1", "F": "L1"},
        "note": "沙地上卧倒休息的斑马身下沙土地面色调整体略显泛浅亮黄(D-L1, F-L1)。"
    },
    7026: {
        "score": 2.47,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "室内沙发上并排就座的人物服饰与皮质沙发在逆光下略显欠饱和偏灰暗(E2-L1, F-L1)。"
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

def clean_desc(text):
    # 去除前缀
    text = re.sub(r"^原\s*[\d\.]+\s*分.*?[，：:]\s*", "", text)
    text = re.sub(r"^核查发现[，：:]\s*", "", text)
    # 去除末尾括号
    text = re.sub(r"\([A-Za-z0-9\s,\-\_]+\)\s*$", "", text)
    return text.strip()

def build_defect_list(severities, note):
    if not severities:
        return []
    desc = clean_desc(note)
    defects = []
    for code, sev in severities.items():
        name = DEFECT_NAMES.get(code, code)
        defects.append({
            "id": code,
            "name": name,
            "severity": "" if code == "A" else sev,
            "description": desc
        })
    return defects

def main():
    print(f"[*] 开始应用 Batch 34 审核结果，总数: {len(REVIEWS_B34)}")
    assert len(REVIEWS_B34) == 120, f"Expected 120 items, got {len(REVIEWS_B34)}"

    # 路径配置
    base_dir = "LS_lcad_reviewer"
    grounding_out_path = os.path.join(base_dir, "intermediate", "audits", "grounding_remaining_batch_34.json")
    all_export_path = os.path.join(base_dir, "exports", "reviewed_1_10000_all.json")
    clean_export_path = os.path.join(base_dir, "exports", "reviewed_1_10000_clean.json")

    # 1. 导出中间定物字典
    with open(grounding_out_path, "w", encoding="utf-8") as f:
        json.dump(REVIEWS_B34, f, ensure_ascii=False, indent=2)
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

    for tid, r in REVIEWS_B34.items():
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
