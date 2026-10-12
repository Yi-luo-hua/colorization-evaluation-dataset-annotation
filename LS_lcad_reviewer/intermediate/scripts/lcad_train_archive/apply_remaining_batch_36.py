# -*- coding: utf-8 -*-
"""
应用 Batch 36 审核具象定物判决字典并双向同步至正式交付文件
Batch 36: Task #7215 ~ #7397 (共 120 组)
"""

import json
import os
import re

# 120 组人工直审与具象定物判决字典
REVIEWS_B36 = {
    # Sheet 01
    7215: {
        "score": 5.0,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "地板陈列的收纳物品中光盘盒彩色涂装与红色书籍封面色彩略显欠饱和偏灰暗(E2-L1, F-L1)。"
    },
    7217: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7218: {
        "score": 4.17,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "卧室双人床后的背景墙面与室内环境光完全丧失暖黄色调，大面积偏向冰冷泛青暗灰偏色(D-L1, E2-L1, F-L1)。"
    },
    7219: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7220: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    7222: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 02
    7223: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7225: {
        "score": 2.25,
        "severities": {"B": "L1", "D": "L1", "F": "L1"},
        "note": "餐桌上放置的玻璃啤酒瓶身与酒标边缘发生颜色溢出，后方酒吧暖色照明略显过浓偏偏红(B-L1, D-L1, F-L1)。"
    },
    7226: {
        "score": 2.61,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "宴会男子西装暗部与后方木质墙壁大面积浸染过浓焦糖暖黄色偏色，色彩轻度过饱和(D-L1, E1-L1)。"
    },
    7228: {
        "score": 2.36,
        "severities": {"C": "L3", "E2": "L2", "F": "L2"},
        "note": "网球场上青年男子所穿的鲜嫩黄绿色运动T恤被彻底脱色错涂为苍白暗淡的灰白色，背景树林亦严重泛冷青灰（严重错色 C-L3）(C-L3, E2-L2, F-L2)。"
    },
    7229: {
        "score": 4.46,
        "severities": {"D": "L1"},
        "note": "厨房餐桌左侧零食包装盒红色涂装及人物暗部阴影色调略显偏深(D-L1)。"
    },
    7231: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 03
    7234: {
        "score": 2.61,
        "severities": {"D": "L1"},
        "note": "雨天撑伞女子服饰暗部与后方街边摊位阴影在雨天光照下略显偏暗偏深(D-L1)。"
    },
    7235: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "餐馆室内抛光地砖与木质餐桌椅大面积丧失温暖暖黄灯光氛围，整体严重偏向冰冷泛青暗灰色偏色(D-L1, E2-L1, F-L1)。"
    },
    7236: {
        "score": 4.46,
        "severities": {},
        "note": "审查通过"
    },
    7237: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "酒吧实木吧台台面与后方酒架墙面大面积丧失原本温暖红棕光晕，呈现偏冷青灰暗淡偏色(D-L1, E2-L1, F-L1)。"
    },
    7238: {
        "score": 2.22,
        "severities": {"B": "L1", "C": "L2", "F": "L1"},
        "note": "海面中央漂浮的浮标由原本鲜艳的荧光粉红色被严重错涂为橙黄色，浮标与波浪边缘相互溢色渗透（错色 C-L2）(B-L1, C-L2, F-L1)。"
    },
    7239: {
        "score": 2.17,
        "severities": {"B": "L1", "D": "L1", "E2": "L2", "F": "L1"},
        "note": "微缩模型顶部的草绿色透明塑料顶盖及侧边结构大面积欠饱和脱色为暗灰褐色，塑料材质质感严重失真(B-L1, D-L1, E2-L2, F-L1)。"
    },

    # Sheet 04
    7240: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "棒球场内野沙土跑道大面积浸染过浓焦糖暖橙黄色偏色，外野草坪色彩过度浓艳(D-L1, E1-L1, F-L1)。"
    },
    7241: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    7242: {
        "score": 5.0,
        "severities": {"C": "L3", "F": "L2"},
        "note": "雨中撑黑伞人物所穿的明艳黄色连帽雨衣被颠覆性错涂为薄荷浅青绿色，服饰色彩严重错配（严重错色 C-L3）(C-L3, F-L2)。"
    },
    7243: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L2", "F": "L1"},
        "note": "瓷盘中巧克力奶油蛋糕切面与蛛网果酱装饰呈现过于浓艳刺眼的红褐过饱和偏色(D-L1, E1-L2, F-L1)。"
    },
    7245: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7246: {
        "score": 5.0,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "棒球比赛击球手后方看台栏杆与球迷看台大面积丧失原本明艳的宝蓝色调，欠饱和褪色泛黑灰(E2-L1, F-L1)。"
    },

    # Sheet 05
    7247: {
        "score": 2.30,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "卫生间墙面瓷砖与立式小便斗内壁大面积浸染刺眼浓烈的红橙暖黄色偏色，全图色调严重过饱和失真(D-L2, E1-L2, F-L2)。"
    },
    7249: {
        "score": 5.0,
        "severities": {"C": "L3", "E2": "L2", "F": "L2"},
        "note": "街道旁立着的菱形自行车警示路牌原本鲜明的明黄色被彻底脱色错涂为惨白无光的灰白色，上方红色STOP停止标志牌亦褪色发暗（严重错色 C-L3）(C-L3, E2-L2, F-L2)。"
    },
    7250: {
        "score": 2.47,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "窗边使用笔记本电脑的女子发丝与室内木地板大面积欠饱和偏冷青灰偏色(D-L1, E2-L1)。"
    },
    7251: {
        "score": 1.08,
        "severities": {"D": "L2", "F": "L2"},
        "note": "装裱老照片的泛黄外卡纸边框被严重错涂为泛绿的青黄冷色，历史黑白照片暗部浸染杂色(D-L2, F-L2)。"
    },
    7252: {
        "score": 2.17,
        "severities": {"D": "L1", "E1": "L2", "F": "L1"},
        "note": "男子手中甜甜圈表面的草莓糖霜与彩色糖粒过于浓艳刺眼，面部受反光影响浸染失真红紫偏色(D-L1, E1-L2, F-L1)。"
    },
    7255: {
        "score": 2.61,
        "severities": {"D": "L1"},
        "note": "厨房操作台前男子身穿的暗红毛衣暗部与水槽周围阴影略显偏深发暗(D-L1)。"
    },

    # Sheet 06
    7257: {
        "score": 4.32,
        "severities": {"B": "L1", "D": "L2", "E1": "L1"},
        "note": "地面铺设的灰白色地毯大面积浸染严重失真浓艳的焦糖橙黄暖偏色，行李箱轮廓边缘发生颜色溢出(B-L1, D-L2, E1-L1)。"
    },
    7258: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "客厅室内沙发与浅色墙壁完全丧失温馨暖黄灯光氛围，整体严重偏向冰冷泛青暗灰偏色(D-L1, E2-L1, F-L1)。"
    },
    7259: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "地面摆放的蓝色雪糕包装箱表面浸染失真的洋红杂色，黄色纸箱暗部光泽略显暗淡(D-L1, F-L1)。"
    },
    7260: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "牛舍围栏背景与小牛身躯背光处在日光照射下略显欠饱和偏冷青灰暗淡(D-L1, E2-L1)。"
    },
    7261: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7262: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "客厅背景墙面与装饰挂画大面积丧失温馨暖黄色调，整体呈现冰冷泛青暗灰偏色(D-L1, E2-L1, F-L1)。"
    },

    # Sheet 07
    7264: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "厨房木质橱柜与操作台背光面完全丧失原本温馨暖黄色调，大面积偏向冰冷泛青暗灰偏色(D-L1, E2-L1, F-L1)。"
    },
    7265: {
        "score": 2.73,
        "severities": {"C": "L2", "D": "L2", "E2": "L2", "F": "L2"},
        "note": "海滩上空原本纯净湛蓝的晴朗天空与远方海面大面积被错涂褪色为暗沉枯槁的灰黄泥沙色，海滨风光严重失真（严重错色 C-L2）(C-L2, D-L2, E2-L2, F-L2)。"
    },
    7266: {
        "score": 2.30,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "铁丝网围栏前马匹背光身躯在强逆光下略显欠饱和偏深暗(D-L1, E2-L1)。"
    },
    7267: {
        "score": 2.61,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "沙发面料与使用者服饰大面积浸染过度浓艳的焦糖红黄偏色，色彩轻度过饱和(D-L1, E1-L1, F-L1)。"
    },
    7268: {
        "score": 5.0,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "打电话年轻女孩面部皮肤与金色长发在日光下严重欠饱和褪色发白，人物气色明显受损(E2-L1, F-L1)。"
    },
    7270: {
        "score": 2.73,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "街头停放的重型巡航摩托车红色油箱涂装与周围人群服饰大面积欠饱和褪色发暗(E2-L1, F-L1)。"
    },

    # Sheet 08
    7271: {
        "score": 2.43,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "动物园水池旁北极熊毛发背光面与后方岩石在自然光下略显欠饱和偏冷暗灰(D-L1, E2-L1)。"
    },
    7272: {
        "score": 2.36,
        "severities": {"C": "L3", "D": "L2", "F": "L2"},
        "note": "客厅地面铺设的鲜红色地毯被彻底颠覆性错涂为深蓝紫色，浅青色组合沙发亦严重偏冷发青（严重错色 C-L3）(C-L3, D-L2, F-L2)。"
    },
    7273: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7275: {
        "score": 2.43,
        "severities": {"C": "L3", "E2": "L2", "F": "L2"},
        "note": "托盘中刚出炉的披萨表面大面积浓郁金黄芝士与红橙番茄酱被严重脱色抹平为惨白灰白色，烘焙新鲜度严重丧失（严重错色 C-L3）(C-L3, E2-L2, F-L2)。"
    },
    7277: {
        "score": 2.47,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "海滩旁停放的重型摩托车镀铬金属与骑手风衣完全丧失晚霞暖黄色泽，呈现冰冷泛青暗灰偏色(D-L1, E2-L1)。"
    },
    7279: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 09
    7280: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L1", "F": "L1"},
        "note": "露天遮阳伞下就座男子所穿的军绿开衫严重褪色错涂为暗灰色，人物面部与环境光整体偏冷青灰(C-L2, D-L1, F-L1)。"
    },
    7281: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7282: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7286: {
        "score": 2.47,
        "severities": {"D": "L1", "F": "L1"},
        "note": "餐桌白色餐布与餐盘边缘大面积浸染失真的粉红偏色，热狗香肠表面光泽微显偏红(D-L1, F-L1)。"
    },
    7287: {
        "score": 4.17,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "草地网球场地表草皮大面积浸染过浓焦糖暖黄色偏色，原本鲜嫩绿意明显衰减，记分牌边缘偏深(D-L1, E1-L1, F-L1)。"
    },
    7288: {
        "score": 2.47,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "合影男女面部皮肤与背景向日葵花瓣大面积浸染过度浓艳的橙黄暖偏色，色彩轻度过饱和(D-L1, E1-L1, F-L1)。"
    },

    # Sheet 10
    7290: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L1", "F": "L1"},
        "note": "滑板少年头戴的鲜红色安全头盔被严重脱色错涂为深灰黑色，背景建筑物外墙色调欠饱和偏冷青灰(C-L2, E2-L1, F-L1)。"
    },
    7291: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7292: {
        "score": 2.20,
        "severities": {"B": "L1", "C": "L2", "F": "L1"},
        "note": "墙面悬挂的挪威皇家盾形徽章原本鲜红的底色被颠覆性错涂为草绿色，上方金属字母边缘微弱溢色（错色 C-L2）(B-L1, C-L2, F-L1)。"
    },
    7293: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "编织竹篮与长毛猫身后的室内环境光完全丧失暖黄色泽，大面积偏向冰冷泛青灰偏色(D-L1, E2-L1, F-L1)。"
    },
    7294: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7295: {
        "score": 2.36,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "披萨店内背景木质墙面与室内灯光完全丧失原本浓郁温馨的暖黄色调，大面积严重偏向冷青暗灰偏色(D-L1, E2-L1, F-L1)。"
    },

    # Sheet 11
    7297: {
        "score": 2.61,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "厨房木质岛台与整面原木橱柜表面浸染过度浓艳的焦糖红黄偏色，色彩轻度过饱和(D-L1, E1-L1)。"
    },
    7299: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7303: {
        "score": 4.23,
        "severities": {},
        "note": "审查通过"
    },
    7304: {
        "score": 5.0,
        "severities": {"C": "L3", "F": "L2"},
        "note": "游客手腕上佩戴的鲜艳大红色手环被彻底颠覆性错涂为亮青蓝色，道具色彩严重错配（严重错色 C-L3）(C-L3, F-L2)。"
    },
    7305: {
        "score": 2.47,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "病房白色单人床被褥暗部与背景墙面在室内日光灯下略显欠饱和偏冷青灰(D-L1, E2-L1)。"
    },
    7306: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 12
    7309: {
        "score": 4.46,
        "severities": {"D": "L1", "F": "L1"},
        "note": "街边设立的禁止停车交通标志牌原本纯白底板大面积被浸染为灰青蓝色，红色警示圆圈边缘轻微偏深(D-L1, F-L1)。"
    },
    7312: {
        "score": 2.61,
        "severities": {"D": "L1"},
        "note": "卫生间白色陶瓷洗手台盆暗部与地面瓷砖略显偏暗偏深(D-L1)。"
    },
    7313: {
        "score": 2.32,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "公共卫生间陶瓷马桶背光阴影与金属隔板在顶灯照射下略显欠饱和偏深暗(D-L1, E2-L1)。"
    },
    7314: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7317: {
        "score": 2.47,
        "severities": {"D": "L1", "F": "L1"},
        "note": "婴儿餐椅后方的木质家具与背景墙面浸染失真的冷青紫色偏色，人物气色略显偏暗(D-L1, F-L1)。"
    },
    7318: {
        "score": 2.24,
        "severities": {"B": "L1", "C": "L2", "F": "L1"},
        "note": "小棕马头部系着的翠绿色尼龙缰绳被颠覆性错涂为亮橙红色，缰绳边缘与马匹毛发相互溢色渗透（错色 C-L2）(B-L1, C-L2, F-L1)。"
    },

    # Sheet 13
    7319: {
        "score": 2.30,
        "severities": {"D": "L1", "F": "L1"},
        "note": "建筑物拱门上方壁灯照射的石砌墙面与右侧绿植阴影大面积偏向冷白青灰，丧失温暖夜景氛围(D-L1, F-L1)。"
    },
    7321: {
        "score": 5.0,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "积雪覆盖的小木屋木质外墙与两头骆驼毛色在阴天下严重欠饱和脱色泛黑灰(E2-L1, F-L1)。"
    },
    7322: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "遥控器面板上的绿色操作按键与红色标识过于浓艳刺眼，按键高光轻微过饱和(D-L1, E1-L1)。"
    },
    7325: {
        "score": 5.0,
        "severities": {"C": "L3", "F": "L2"},
        "note": "汽车后座右侧小男孩所穿的亮粉红色短袖T恤被彻底颠覆性错涂为深宝蓝色，服饰色彩严重错配（严重错色 C-L3）(C-L3, F-L2)。"
    },
    7327: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "餐桌实木桌面大面积浸染过度浓艳的焦糖橙黄暖偏色，餐盘白色陶瓷边缘受反光侵染轻微偏色(D-L1, E1-L1)。"
    },
    7328: {
        "score": 2.73,
        "severities": {"C": "L2", "D": "L1", "F": "L1"},
        "note": "动物园猛兽笼舍后方的茂密绿树大面积被错涂为枯黄焦褐色，笼舍铁栅栏表面微泛暖红偏色(C-L2, D-L1, F-L1)。"
    },

    # Sheet 14
    7330: {
        "score": 1.15,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "火车站月台路灯璀璨浓郁的金黄夜景灯光与月台地面光晕被彻底抹除，整座车站与列车车厢大面积严重偏向冰冷泛青暗灰色偏色(D-L2, E2-L2, F-L2)。"
    },
    7331: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    7332: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7333: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7334: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "餐馆背景木质墙面与室内灯光大面积丧失温暖黄色，偏向冷青暗灰偏色，人物面部略显暗沉(D-L1, F-L1)。"
    },
    7340: {
        "score": 5.0,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "运河两岸集市拥挤人群原本五彩缤纷的彩色夏装与遮阳篷大面积欠饱和褪色为暗沉死灰(E2-L1, F-L1)。"
    },

    # Sheet 15
    7341: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "电脑办公桌实木桌面与后方储物搁架完全丧失温馨暖黄灯光氛围，大面积严重偏向冰冷泛青暗灰偏色(D-L1, E2-L1, F-L1)。"
    },
    7343: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7344: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7345: {
        "score": 2.17,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "客厅实木书架与背景浅色墙壁大面积浸染过度浓艳的焦糖红黄偏色，色彩轻度过饱和(D-L1, E1-L1)。"
    },
    7346: {
        "score": 2.17,
        "severities": {"B": "L1", "D": "L1", "E1": "L2", "F": "L1"},
        "note": "欧式古典壁灯下方悬挂的复古圆形挂钟表盘被过度浸染为浓艳刺眼的橙黄色，壁灯灯罩边缘发生明显颜色溢出(B-L1, D-L1, E1-L2, F-L1)。"
    },
    7347: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 16
    7348: {
        "score": 5.0,
        "severities": {"C": "L3", "F": "L2"},
        "note": "空中飞行的塑料飞盘由原本鲜艳的玫粉红色被颠覆性错涂为灰青蓝色，玩具道具严重错色（严重错色 C-L3）(C-L3, F-L2)。"
    },
    7349: {
        "score": 2.25,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "餐桌上放置的黄色波点马克杯表面及金属咖啡壶反光浸染过浓焦糖红黄暖偏色，色彩轻度过饱和(D-L1, E1-L1)。"
    },
    7350: {
        "score": 1.06,
        "severities": {"D": "L2", "E2": "L1", "F": "L2"},
        "note": "玄关柜台上的台灯完全丧失原本浓郁温馨的暖黄色光晕，台面摆件与盆栽大面积严重偏向冰冷泛青暗紫灰偏色(D-L2, E2-L1, F-L2)。"
    },
    7353: {
        "score": 2.07,
        "severities": {"B": "L1", "D": "L1", "E2": "L1", "F": "L1"},
        "note": "花园泥地碎石间觅食的小鸟鲜红羽毛大面积欠饱和褪色发暗，鸟身轮廓边缘发生轻微溢色侵染(B-L1, D-L1, E2-L1, F-L1)。"
    },
    7356: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "微波炉上方放置的老式座钟木质边框大面积浸染过度浓艳的焦糖红黄暖偏色，色彩轻度过饱和(D-L1, E1-L1)。"
    },
    7357: {
        "score": 2.36,
        "severities": {"C": "L3", "E2": "L2", "F": "L2"},
        "note": "球拍边框与拍套原本鲜艳纯正的荧光玫粉红色被颠覆性错涂为暗青灰黑色，球拍艳丽色彩彻底丧失（严重错色 C-L3）(C-L3, E2-L2, F-L2)。"
    },

    # Sheet 17
    7359: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    7360: {
        "score": 2.73,
        "severities": {"C": "L2", "E2": "L2", "F": "L2"},
        "note": "港口码头立着的菱形警示标牌鲜艳黄色被严重脱色错涂为暗淡灰白，背景晴朗蓝天亦大面积脱色泛死灰（严重错色 C-L2）(C-L2, E2-L2, F-L2)。"
    },
    7361: {
        "score": 2.56,
        "severities": {"D": "L1"},
        "note": "卧室单人床头木质框架暗部与墙角阴影在背光下略显偏暗偏深(D-L1)。"
    },
    7362: {
        "score": 2.23,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "现代化整体厨房白色橱柜与操作台面完全丧失原本温暖温馨的暖黄光照，整体大面积偏向冰冷泛青暗灰偏色(D-L1, E2-L1, F-L1)。"
    },
    7366: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "餐厅实木餐桌椅与木质地板大面积丧失温暖红棕暖色，呈现偏冷青灰暗淡偏色(D-L1, E2-L1, F-L1)。"
    },
    7368: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 18
    7370: {
        "score": 2.17,
        "severities": {"C": "L2", "E2": "L2", "F": "L2"},
        "note": "宠物狗爪按着的维生素饮料瓶身上原本鲜艳明亮的苹果绿标签条被严重脱色错涂为泛灰暗黄色（错色 C-L2）(C-L2, E2-L2, F-L2)。"
    },
    7372: {
        "score": 2.36,
        "severities": {"D": "L1", "F": "L1"},
        "note": "快餐店聚餐照片外白色卡纸边框微泛青绿偏色，人物面部阴影略显偏深(D-L1, F-L1)。"
    },
    7374: {
        "score": 2.47,
        "severities": {"D": "L2", "F": "L2"},
        "note": "夜间路灯高光光晕周围严重浸染一圈失真诡异的深蓝紫色光环偏色，夜空背景自然度受损(D-L2, F-L2)。"
    },
    7375: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7376: {
        "score": 1.15,
        "severities": {"C": "L3", "F": "L2"},
        "note": "庆祝女子身上所穿的鲜绿色长袖上衣被彻底颠覆性错涂为深焦糖黄褐色，服饰色彩完全错配失真（严重错色 C-L3）(C-L3, F-L2)。"
    },
    7380: {
        "score": 4.55,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "街角背景建筑物外墙完全丧失原本温暖的橙黄色调，大面积严重偏向冰冷泛青暗灰色偏色(D-L1, E2-L1, F-L1)。"
    },

    # Sheet 19
    7381: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7383: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "餐厅餐桌表面与烤土司三明治阴影在室内光照下略显欠饱和偏冷青灰暗淡(D-L1, E2-L1)。"
    },
    7384: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7385: {
        "score": 5.0,
        "severities": {"E1": "L1"},
        "note": "看台栏杆插放的双板滑雪板红色涂装略显过于浓艳刺眼，木窗边缘轻度过饱和(E1-L1)。"
    },
    7387: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "复古铁皮玩具车车身金属漆面与彩色标识大面积欠饱和偏冷青灰，色彩层次平淡(D-L1, E2-L1)。"
    },
    7388: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "聚会餐桌红色桌布与男子面部反光大面积浸染过度浓艳的橙红暖偏色，色彩轻度过饱和(D-L1, E1-L1)。"
    },

    # Sheet 20
    7389: {
        "score": 5.0,
        "severities": {"D": "L1"},
        "note": "草坪上扑球棒球防守队员球服暗部与后方停放的白色轿车车身在强光下略显偏暗偏深(D-L1)。"
    },
    7391: {
        "score": 2.25,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "聚会餐桌前招手男子面部受室内暖黄顶灯过度照射，面颊与手掌过度偏红偏浓艳(D-L1, E1-L1, F-L1)。"
    },
    7392: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "合影年轻人身后的客厅沙发暗部与室内墙面大面积泛冷发青发灰，色温略显偏冷(D-L1, E2-L1, F-L1)。"
    },
    7394: {
        "score": 2.17,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "街道上停放的绿色双层巴士车头与周围骑车人服饰在顶光下略显过饱和偏浓深(D-L1, E1-L1, F-L1)。"
    },
    7395: {
        "score": 4.55,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "卧室双人床铺上紫色被褥与趴着的猫咪背部毛发色彩略显浓艳过饱和(D-L1, E1-L1)。"
    },
    7397: {
        "score": 2.61,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "客厅餐桌上摆放的百合切花与红色花瓶表面光泽过度浓艳泛红橙偏色(D-L1, E1-L1, F-L1)。"
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
    grounding_out_path = "LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_36.json"
    all_export_path = "LS_lcad_reviewer/exports/reviewed_1_10000_all.json"
    clean_export_path = "LS_lcad_reviewer/exports/reviewed_1_10000_clean.json"

    # 1. 导出中间定物字典
    with open(grounding_out_path, "w", encoding="utf-8") as f:
        json.dump(REVIEWS_B36, f, ensure_ascii=False, indent=2)
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

    for tid, r in REVIEWS_B36.items():
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
