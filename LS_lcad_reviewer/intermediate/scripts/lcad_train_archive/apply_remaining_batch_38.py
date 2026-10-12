# -*- coding: utf-8 -*-
"""
应用 Batch 38 审核具象定物判决字典并双向同步至正式交付文件
Batch 38: Task #7566 ~ #7755 (共 120 组)
"""

import json
import os
import re

# 120 组人工直审与具象定物判决字典
REVIEWS_B38 = {
    # Sheet 01
    7566: {
        "score": 2.47,
        "severities": {"C": "L2", "D": "L2", "E2": "L2", "F": "L2"},
        "note": "餐桌铺设的暖黄桌布与披萨表面翠绿芝麻菜大面积严重欠饱和脱色错涂为灰白死色，食材色泽严重受损(C-L2, D-L2, E2-L2, F-L2)。"
    },
    7568: {
        "score": 4.46,
        "severities": {},
        "note": "审查通过"
    },
    7569: {
        "score": 1.20,
        "severities": {"C": "L2", "E2": "L2", "F": "L2"},
        "note": "废墟空地上放置的粉橙色电脑桌抽屉柜被彻底脱色错涂为惨白暗灰水泥色，原物品鲜明色彩彻底丧失(C-L2, E2-L2, F-L2)。"
    },
    7571: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7572: {
        "score": 2.56,
        "severities": {"E1": "L1"},
        "note": "古典客厅室内橘黄墙面与地面红色碎花地毯色彩略显过于浓艳刺眼，轻度过饱和(E1-L1)。"
    },
    7574: {
        "score": 2.36,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "餐碗中盛放的蔬菜杂烩周围及碗沿大面积浸染失真的洋红紫冷色偏色，食物色泽失真(D-L1, E1-L1, F-L1)。"
    },

    # Sheet 02
    7575: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7576: {
        "score": 2.56,
        "severities": {},
        "note": "审查通过"
    },
    7577: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7579: {
        "score": 1.06,
        "severities": {"D": "L1", "E1": "L2", "F": "L2"},
        "note": "头戴学士帽打电话的毕业生面部皮肤与五官轮廓大面积浸染失真浓艳的洋红紫冷色偏色，气色严重失真(D-L1, E1-L2, F-L2)。"
    },
    7582: {
        "score": 2.23,
        "severities": {"C": "L2", "E2": "L1", "F": "L1"},
        "note": "改装摩托车金属油箱侧面原本鲜艳明亮的金黄色拉花涂装大面积欠饱和脱色为暗沉灰黄色(C-L2, E2-L1, F-L1)。"
    },
    7584: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "海滨停车场旁棕色马匹后背毛皮大面积欠饱和脱色偏灰白，车辆轮廓阴影微偏冷(D-L1, E2-L1, F-L1)。"
    },

    # Sheet 03
    7587: {
        "score": 2.73,
        "severities": {"C": "L2", "D": "L2", "E2": "L2", "F": "L2"},
        "note": "碧海蓝天中冲浪海面与背景天空大面积严重欠饱和脱色错涂为惨白青灰死色，热带海滨风光严重失真(C-L2, D-L2, E2-L2, F-L2)。"
    },
    7589: {
        "score": 2.61,
        "severities": {"B": "L1", "D": "L1", "F": "L1"},
        "note": "金属道路指示牌正面与红色停止标志边缘发生颜色溢出，暗部微泛红紫杂色偏色(B-L1, D-L1, F-L1)。"
    },
    7590: {
        "score": 2.47,
        "severities": {"C": "L3", "D": "L2", "E2": "L2", "F": "L2"},
        "note": "水族馆水体原本清澈翠绿的海水被彻底颠覆性错涂为枯槁灰黄泥浆色，海洋生态氛围彻底失真(C-L3, D-L2, E2-L2, F-L2)。"
    },
    7591: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7592: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7593: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 04
    7594: {
        "score": 2.43,
        "severities": {"C": "L2", "D": "L2", "E1": "L2", "F": "L2"},
        "note": "海滨栈桥下冲浪者手持的宝蓝冲浪板与海浪大面积浸染刺眼浓艳的洋红紫荧光偏色，全图色调严重失真(C-L2, D-L2, E1-L2, F-L2)。"
    },
    7596: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7598: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7599: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "室内小狗身后的浅色墙面与阴影大面积丧失温暖色泽，呈现冰冷泛青暗灰偏色(D-L1, E2-L1, F-L1)。"
    },
    7600: {
        "score": 2.17,
        "severities": {"D": "L1", "F": "L1"},
        "note": "卫生间洗手台盆陶瓷暗部与周围墙壁大面积浸染不自然的深青蓝色偏色(D-L1, F-L1)。"
    },
    7601: {
        "score": 2.36,
        "severities": {"D": "L1", "F": "L1"},
        "note": "街头垃圾桶上方强光区域及右侧停放车辆车顶浸染失真的紫红眩光偏色(D-L1, F-L1)。"
    },

    # Sheet 05
    7602: {
        "score": 2.47,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "长椅上撑蕾丝阳伞的妇女浅色裙装与阳伞蕾丝在阳光下略显欠饱和偏冷青灰(D-L1, E2-L1)。"
    },
    7603: {
        "score": 2.56,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "院子里玩耍的红衣小女孩上衣与黄色消防栓涂装略显欠饱和发暗(E2-L1, F-L1)。"
    },
    7607: {
        "score": 2.25,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "街头并排行走的年轻女子无袖背心亮黄色与浅蓝牛仔裤略显过于浓艳刺眼(D-L1, E1-L1, F-L1)。"
    },
    7609: {
        "score": 5.0,
        "severities": {"E2": "L1"},
        "note": "海滩滩涂觅食的小涉禽羽毛暗部在泥滩水面反射下略显欠饱和偏暗灰(E2-L1)。"
    },
    7611: {
        "score": 4.55,
        "severities": {"E2": "L1"},
        "note": "围栏前抚摸大象的长发女子所穿的明艳红粉色外套大面积欠饱和褪色泛灰(E2-L1)。"
    },
    7612: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 06
    7613: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7615: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7616: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7618: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7619: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "长颈鹿颈部原本鲜明温暖的金黄色网状皮毛整体偏冷偏青，色彩欠饱和发灰(D-L1, E2-L1)。"
    },
    7620: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 07
    7621: {
        "score": 2.47,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "卧室背景米白墙面与小女孩粉红连体睡裙浸染过度浓艳的焦黄暖色偏色，色彩轻度过饱和(D-L1, E1-L1)。"
    },
    7623: {
        "score": 4.46,
        "severities": {"D": "L2", "E2": "L1"},
        "note": "卫生间马桶周围地面与墙壁的暖黄瓷砖大面积欠饱和脱色为冰冷青灰死色，环境色温严重失真偏冷(D-L2, E2-L1)。"
    },
    7626: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7628: {
        "score": 2.36,
        "severities": {},
        "note": "审查通过"
    },
    7629: {
        "score": 2.25,
        "severities": {},
        "note": "审查通过"
    },
    7631: {
        "score": 5.0,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "雪山顶插着的两块滑雪单板与双板明艳鲜亮的橙红色与亮绿色板面大面积欠饱和褪色发暗(E2-L1, F-L1)。"
    },

    # Sheet 08
    7634: {
        "score": 5.0,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "雪道上滑雪运动员身穿的明亮蓝红拼色滑雪服与赛道旗门布套大面积欠饱和褪色发暗(E2-L1, F-L1)。"
    },
    7635: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7636: {
        "score": 2.17,
        "severities": {"C": "L2", "D": "L2", "E1": "L2", "F": "L2"},
        "note": "海上日落晚霞与海面波光大面积浸染失真浓艳的洋红紫荧光偏色，晚霞原本的金黄夕阳色泽彻底失真(C-L2, D-L2, E1-L2, F-L2)。"
    },
    7638: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7639: {
        "score": 1.20,
        "severities": {},
        "note": "审查通过"
    },
    7640: {
        "score": 2.36,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "餐桌摆放的洋酒玻璃瓶身与桌面白色餐布大面积浸染失真的红紫杂色偏色，室内暖光过度浓艳(D-L1, E1-L1, F-L1)。"
    },

    # Sheet 09
    7642: {
        "score": 5.0,
        "severities": {"D": "L1"},
        "note": "男子身穿的短袖T恤暗部略显偏冷蓝紫杂色偏色(D-L1)。"
    },
    7644: {
        "score": 2.56,
        "severities": {"D": "L1", "E1": "L2", "F": "L1"},
        "note": "餐厅红色烤漆桌面与白色餐盘内的油炸鸡块表面大面积浸染过度浓艳刺眼的火红暖偏色，色彩严重过饱和(D-L1, E1-L2, F-L1)。"
    },
    7645: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7646: {
        "score": 4.46,
        "severities": {},
        "note": "审查通过"
    },
    7651: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7652: {
        "score": 2.17,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 10
    7653: {
        "score": 2.47,
        "severities": {},
        "note": "审查通过"
    },
    7654: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7655: {
        "score": 2.17,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "复古皮革行李箱黄色皮革箱面色彩略显过于浓艳鲜亮，轻度偏黄(D-L1, E1-L1)。"
    },
    7656: {
        "score": 2.43,
        "severities": {"C": "L2", "D": "L1", "E2": "L1"},
        "note": "稀树草原上空的清澈蓝天大面积欠饱和褪色为惨白色，大象灰褐皮毛与游客墨绿服饰略显泛白(C-L2, D-L1, E2-L1)。"
    },
    7658: {
        "score": 2.73,
        "severities": {"C": "L2", "D": "L2", "E2": "L2", "F": "L2"},
        "note": "室外地面与建筑物外墙的温暖夕阳斜照大面积欠饱和严重脱色为冰冷惨白灰死色，环境氛围严重失真(C-L2, D-L2, E2-L2, F-L2)。"
    },
    7659: {
        "score": 2.07,
        "severities": {"B": "L1", "D": "L1", "F": "L1"},
        "note": "竞技场沙地表面与看台观众区顶棚边缘色彩略有溢出扩散，沙地微泛不均匀淡红杂色(B-L1, D-L1, F-L1)。"
    },

    # Sheet 11
    7661: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7662: {
        "score": 4.46,
        "severities": {},
        "note": "审查通过"
    },
    7665: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "F": "L1"},
        "note": "湖面上游艇拖曳的明黄色充气滑水圈大面积欠饱和严重褪色变白(C-L2, E2-L2, F-L1)。"
    },
    7666: {
        "score": 2.43,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "卧室地面铺设的深红紫碎花地毯与床前脚凳色彩略显欠饱和偏灰暗(E2-L1, F-L1)。"
    },
    7668: {
        "score": 2.17,
        "severities": {},
        "note": "审查通过"
    },
    7669: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 12
    7670: {
        "score": 1.07,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "室内砖石壁炉与木质地板表面大面积浸染过度浓艳的焦糖红黄暖偏色，室内色温严重偏暖过饱和(D-L1, E1-L1, F-L1)。"
    },
    7675: {
        "score": 4.46,
        "severities": {},
        "note": "审查通过"
    },
    7676: {
        "score": 4.46,
        "severities": {"C": "L2", "D": "L1", "E1": "L1"},
        "note": "办公室与洗手间隔断墙壁原本淡灰蓝色墙面大面积错涂为浓艳刺眼的蓝绿色偏色，色彩明显过饱和(C-L2, D-L1, E1-L1)。"
    },
    7677: {
        "score": 2.73,
        "severities": {},
        "note": "审查通过"
    },
    7678: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7679: {
        "score": 2.43,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "餐桌巧克力蛋糕后方虚化背景中的玻璃杯与桌面大面积浸染失真的青蓝与火红杂色偏色，色彩过度浓艳(D-L1, E1-L1, F-L1)。"
    },

    # Sheet 13
    7682: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L1"},
        "note": "餐桌摆放的陶瓷调味小碗内的红色酱料大面积欠饱和严重褪色变暗(C-L2, E2-L1)。"
    },
    7684: {
        "score": 5.0,
        "severities": {"C": "L2", "F": "L1"},
        "note": "棒球场垒包上防守球员身穿的蓝绿色运动上衣被彻底颠覆性错涂为亮红色(C-L2, F-L1)。"
    },
    7686: {
        "score": 2.36,
        "severities": {},
        "note": "审查通过"
    },
    7687: {
        "score": 5.0,
        "severities": {"C": "L3", "D": "L2", "F": "L2"},
        "note": "卧室大床后方的孔雀蓝背景墙壁被彻底颠覆性错涂为大红色，室内色彩基调完全颠覆(C-L3, D-L2, F-L2)。"
    },
    7689: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "客厅室内墙壁与门廊原本温馨的淡黄绿暖光墙面大面积欠饱和褪色为灰白冷调(D-L1, E2-L1)。"
    },
    7691: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "暮色中石砌钟楼外墙原本沐浴的金黄夕阳余晖大面积欠饱和褪色为冰冷青灰死色(D-L1, E2-L1)。"
    },

    # Sheet 14
    7692: {
        "score": 2.43,
        "severities": {},
        "note": "审查通过"
    },
    7693: {
        "score": 1.0,
        "severities": {"A": ""},
        "note": "厨房餐桌与老夫妇全身及背景家具全域上色彻底失败，呈现完全无色彩的纯黑白灰阶状态(A)。"
    },
    7694: {
        "score": 4.55,
        "severities": {"C": "L2", "E2": "L2", "F": "L1"},
        "note": "草坪空地上放置的亮天蓝色儿童塑料泳池大面积欠饱和严重脱色错涂为泥污灰白色(C-L2, E2-L2, F-L1)。"
    },
    7695: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7696: {
        "score": 2.47,
        "severities": {"C": "L2", "D": "L2", "E2": "L2"},
        "note": "稀树草原地面的浅绿草皮与黄土地表大面积欠饱和严重脱色为冰冷泛白死灰色，植被生机彻底丧失(C-L2, D-L2, E2-L2)。"
    },
    7697: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 15
    7698: {
        "score": 2.17,
        "severities": {},
        "note": "审查通过"
    },
    7700: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7703: {
        "score": 2.43,
        "severities": {},
        "note": "审查通过"
    },
    7704: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L1"},
        "note": "吃点心的小男孩身上穿着的鲜艳明黄色连帽卫衣大面积欠饱和褪色泛灰(C-L2, E2-L1)。"
    },
    7705: {
        "score": 2.17,
        "severities": {"C": "L3", "D": "L2", "E2": "L2", "F": "L2"},
        "note": "消防栓周围原本生机勃勃的翠绿草坪被大面积严重脱色错涂为枯槁灰黄泥土死色，黄色消防栓柱身欠饱和褪色(C-L3, D-L2, E2-L2, F-L2)。"
    },
    7707: {
        "score": 2.36,
        "severities": {"D": "L2", "E2": "L1", "F": "L1"},
        "note": "浴室镜面、玻璃淋浴房与墙壁大面积浸染失真的冰冷青绿杂色偏色，室内原本的温馨暖光环境严重失真(D-L2, E2-L1, F-L1)。"
    },

    # Sheet 16
    7709: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "F": "L1"},
        "note": "公园草坪中央放置的明黄色巨型充气黄鸭大面积欠饱和严重脱色错涂为惨白淡蓝色(C-L2, E2-L2, F-L1)。"
    },
    7711: {
        "score": 2.30,
        "severities": {"C": "L2", "D": "L2", "E2": "L2", "F": "L2"},
        "note": "街道建筑外立面与水泥楼梯的暖黄橙色灰泥墙壁大面积欠饱和严重脱色为冰冷死灰色，暖色环境氛围严重失真(C-L2, D-L2, E2-L2, F-L2)。"
    },
    7713: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "厨房岛台实木橱柜与大理石台面大面积欠饱和褪色为阴冷灰白色，失去原木温暖色调(D-L1, E2-L1)。"
    },
    7714: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7715: {
        "score": 2.17,
        "severities": {},
        "note": "审查通过"
    },
    7716: {
        "score": 4.55,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "沿街店铺外墙招牌与顶棚大面积浸染失真浓艳的红紫杂色偏色，局部色彩明显过饱和(D-L1, E1-L1, F-L1)。"
    },

    # Sheet 17
    7720: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L1"},
        "note": "棒球场上防守捕手身穿的鲜蓝防具背心与护腿大面积欠饱和严重褪色变暗灰(C-L2, E2-L1)。"
    },
    7723: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7724: {
        "score": 2.47,
        "severities": {},
        "note": "审查通过"
    },
    7726: {
        "score": 5.0,
        "severities": {"C": "L1", "E2": "L1"},
        "note": "金属交通指示牌外圈鲜红警示边框与中心蓝色衬底大面积欠饱和褪色偏暗灰(C-L1, E2-L1)。"
    },
    7727: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7728: {
        "score": 2.73,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 18
    7729: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L1"},
        "note": "观景台上游客男子身穿的鲜艳橙红色短袖T恤大面积欠饱和褪色为暗沉灰粉色(C-L2, E2-L1)。"
    },
    7730: {
        "score": 2.36,
        "severities": {"D": "L2", "E2": "L2", "F": "L1"},
        "note": "室内窗边暖黄窗帘与背景墙壁大面积欠饱和褪色为冰冷青灰死色，室内色温严重偏冷(D-L2, E2-L2, F-L1)。"
    },
    7731: {
        "score": 2.56,
        "severities": {"D": "L1", "E1": "L2", "F": "L1"},
        "note": "打电话的老人身穿的深蓝色夹克外套大面积浸染过于浓艳刺眼的洋红紫冷色偏色，色彩明显过饱和(D-L1, E1-L2, F-L1)。"
    },
    7734: {
        "score": 2.17,
        "severities": {"C": "L3", "D": "L2", "F": "L2"},
        "note": "网球场地面的翠绿色人工草皮被大面积严重错涂为枯槁暗黄泥土地面，色彩严重失真颠覆(C-L3, D-L2, F-L2)。"
    },
    7737: {
        "score": 4.46,
        "severities": {"C": "L2", "E2": "L1"},
        "note": "餐桌右上角玻璃杯内盛放的鲜亮橙黄色果汁大面积欠饱和严重脱色为发白冷色(C-L2, E2-L1)。"
    },
    7738: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 19
    7739: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "林地岩石旁趴卧的白熊毛皮大面积欠饱和泛冷灰，缺乏阳光原本的温润暖色(D-L1, E2-L1)。"
    },
    7740: {
        "score": 2.56,
        "severities": {},
        "note": "审查通过"
    },
    7743: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L1"},
        "note": "室内体验体感游戏的女子身穿的彩色横条纹上衣与后方男子的粉红卫衣大面积欠饱和褪色为灰白色(C-L2, E2-L1)。"
    },
    7744: {
        "score": 2.43,
        "severities": {"C": "L3", "D": "L1", "F": "L2"},
        "note": "草坪旁并排的消防栓中，原本翠绿色的金属顶盖被彻底颠覆性错涂为鲜艳火红色(C-L3, D-L1, F-L2)。"
    },
    7745: {
        "score": 2.25,
        "severities": {},
        "note": "审查通过"
    },
    7746: {
        "score": 2.39,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 20
    7747: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7748: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "街头行走的黄牛浅黄褐色皮毛大面积欠饱和褪色发冷灰，缺乏温润质感(D-L1, E2-L1)。"
    },
    7749: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7751: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    7753: {
        "score": 2.25,
        "severities": {},
        "note": "审查通过"
    },
    7755: {
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

def main():
    print(f"Total reviews in Batch 38: {len(REVIEWS_B38)}")
    
    # 1. 保存具象定物字典至 intermediate/audits/grounding_remaining_batch_38.json
    out_grounding_path = "LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_38.json"
    with open(out_grounding_path, "w", encoding="utf-8") as f:
        json.dump(REVIEWS_B38, f, ensure_ascii=False, indent=2)
    print(f"Saved grounding reviews to {out_grounding_path}")

    # 2. 读取正式交付文件并双向同步
    all_path = "LS_lcad_reviewer/exports/reviewed_1_10000_all.json"
    clean_path = "LS_lcad_reviewer/exports/reviewed_1_10000_clean.json"

    with open(all_path, "r", encoding="utf-8") as f:
        data_all = json.load(f)

    with open(clean_path, "r", encoding="utf-8") as f:
        data_clean = json.load(f)

    anns_all = data_all["annotations"]
    anns_clean = data_clean["annotations"]

    # 建立 task_id 索引（从 human_review.task_id 读取）
    idx_map_all = {ann["human_review"]["task_id"]: i for i, ann in enumerate(anns_all)}
    idx_map_clean = {ann["human_review"]["task_id"]: i for i, ann in enumerate(anns_clean)}

    updated_count = 0
    passed_count = 0
    revised_count = 0

    for tid, rev in REVIEWS_B38.items():
        if tid not in idx_map_all or tid not in idx_map_clean:
            print(f"Warning: task_id {tid} not found in annotations!")
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
