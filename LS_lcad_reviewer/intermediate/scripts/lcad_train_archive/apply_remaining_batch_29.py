# -*- coding: utf-8 -*-
"""
应用 Batch 29 审核具象定物判决字典并双向同步至正式交付文件
Batch 29: Task #5923 ~ #6116 (共 120 组)
"""

import json
import os
import re

# 120 组人工直审与具象定物判决字典
REVIEWS_B29 = {
    # Sheet 01
    5923: {
        "score": 2.47,
        "severities": {"C": "L2", "D": "L1", "F": "L1"},
        "note": "吹风机下白色小狗毛皮泛发暗阴冷青灰绿杂色且床单粉色脱色(C-L2, D-L1, F-L1)。"
    },
    5924: {
        "score": 4.46,
        "severities": {"C": "L1", "D": "L1", "F": "L1"},
        "note": "雨中撑伞女士所穿的鲜红披肩外套大面积严重偏暗发紫泛刺目洋红(C-L1, D-L1, F-L1)。"
    },
    5929: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：海滩救生冲浪板原本极度醒目的鲜亮明黄色大面积脱色变暗偏土灰黄(C-L2, E2-L2, F-L1)。"
    },
    5930: {
        "score": 2.47,
        "severities": {"C": "L2", "D": "L1", "E2": "L2", "F": "L1"},
        "note": "滑板公园上方原本纯正湛蓝的晴朗天空严重脱色泛淡青灰冷调(C-L2, D-L1, E2-L2, F-L1)。"
    },
    5931: {
        "score": 2.36,
        "severities": {"C": "L3", "E1": "L2", "D": "L2", "F": "L3"},
        "note": "两岸热带雨林原本青翠茂盛的树冠枝叶颠覆性错涂为刺眼浓烈发锈红褐色(C-L3, E1-L2, D-L2, F-L3)。"
    },
    5932: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：背景森林树木原本生机翠绿系统性偏冷褪为发暗青蓝黑灰(D-L1, E2-L1, F-L1)。"
    },

    # Sheet 02
    5933: {
        "score": 2.30,
        "severities": {"D": "L2", "E2": "L2", "F": "L1"},
        "note": "卫生间白色坐便器隔板与墙体大面积严重偏暗脏黄泥土色(D-L2, E2-L2, F-L1)。"
    },
    5934: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：巨型甜甜圈招牌雕塑原本浓郁诱人的深焦糖金红褐色大面积严重脱色褪为苍白灰黄(C-L2, E2-L2, F-L1)。"
    },
    5935: {
        "score": 2.36,
        "severities": {"C": "L3", "E2": "L3", "F": "L2"},
        "note": "小女孩头上佩戴的娇艳玫红洋红色头巾颠覆性彻底脱色错涂为发暗泥浆土黄色(C-L3, E2-L3, F-L2)。"
    },
    5936: {
        "score": 4.46,
        "severities": {"C": "L1", "D": "L1", "F": "L1"},
        "note": "餐桌上的白色毛绒小熊与木椅背景严重泛起刺目深洋红与冷紫杂光(C-L1, D-L1, F-L1)。"
    },
    5937: {
        "score": 2.61,
        "severities": {"C": "L2", "D": "L2", "F": "L1"},
        "note": "厨房烤箱上方的红砖墙面与红木橱柜大面积严重偏冷泛暗青灰黑(C-L2, D-L2, F-L1)。"
    },
    5939: {
        "score": 4.46,
        "severities": {"C": "L1", "D": "L1", "F": "L1"},
        "note": "木质柜体表面原本温润纯正的深樱桃红木色严重偏冷泛发暗青灰紫(C-L1, D-L1, F-L1)。"
    },

    # Sheet 03
    5940: {
        "score": 5.0,
        "severities": {"C": "L3", "D": "L1", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：街头车辆旁的折叠警示三角牌原本鲜艳纯正的明黄色颠覆性严重错涂为鲜红血色(C-L3, D-L1, F-L2)。"
    },
    5942: {
        "score": 1.06,
        "severities": {"C": "L3", "E1": "L3", "D": "L2", "F": "L3"},
        "note": "十字路口红绿灯上方整片天空与金属悬臂颠覆性错涂为刺眼深洋红与冷紫假色且过饱和失真(C-L3, E1-L3, D-L2, F-L3)。"
    },
    5943: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：高脚玻璃杯内盛放的红葡萄酒原本晶莹宝石红色明显脱色变暗褪为发黑墨褐(C-L2, E2-L2, F-L1)。"
    },
    5944: {
        "score": 2.56,
        "severities": {"E1": "L2", "D": "L1", "F": "L1"},
        "note": "街边停靠的复古客车车身原本清爽的浅海宝蓝烤漆严重过饱和偏刺目深电光青蓝(E1-L2, D-L1, F-L1)。"
    },
    5945: {
        "score": 2.27,
        "severities": {"C": "L3", "D": "L2", "F": "L2"},
        "note": "草原壁画上方原本蔚蓝纯净的天空严重错涂为发暗浑浊的铁锈红褐色(C-L3, D-L2, F-L2)。"
    },
    5946: {
        "score": 2.17,
        "severities": {"B": "L2", "C": "L2", "E1": "L2", "D": "L1", "F": "L2"},
        "note": "海滩小女孩所穿吊带裙严重泛起刺目荧光深洋红紫假色并伴随风筝边缘溢色(B-L2, C-L2, E1-L2, D-L1, F-L2)。"
    },

    # Sheet 04
    5949: {
        "score": 2.36,
        "severities": {"C": "L2", "D": "L1", "F": "L2"},
        "note": "客厅沙发靠垫与铺盖毛毯严重泛起刺目深洋红与冷紫假色(C-L2, D-L1, F-L2)。"
    },
    5954: {
        "score": 4.46,
        "severities": {"C": "L1", "E2": "L2", "F": "L1"},
        "note": "车内小狗脖颈佩戴的鲜红项圈明显脱色欠饱和褪变为发暗脏灰肉红(C-L1, E2-L2, F-L1)。"
    },
    5955: {
        "score": 5.0,
        "severities": {"C": "L1", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：铁路道口警示标志与平交道护栏大面积泛深紫红暗色且黄漆脱色变暗(C-L1, D-L1, F-L1)。"
    },
    5956: {
        "score": 4.46,
        "severities": {"C": "L1", "D": "L1", "F": "L1"},
        "note": "室内背景储物柜与黑色行李箱边缘严重泛起刺目深洋红与冷紫杂光(C-L1, D-L1, F-L1)。"
    },
    5957: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：背景热带椰林树冠原本生机翠绿系统性偏冷泛暗青蓝黑灰(D-L1, E2-L1, F-L1)。"
    },
    5959: {
        "score": 2.73,
        "severities": {"C": "L2", "E2": "L2", "D": "L1", "F": "L1"},
        "note": "白瓷花盆内水培绿植翠绿枝叶严重脱色发灰且背景暖墙泛冷青白(C-L2, E2-L2, D-L1, F-L1)。"
    },

    # Sheet 05
    5962: {
        "score": 1.07,
        "severities": {"C": "L2", "E1": "L3", "D": "L2", "F": "L3"},
        "note": "打字双手手背皮肤与键盘右侧严重泛起刺目荧光深洋红紫假色且桌面过饱和(C-L2, E1-L3, D-L2, F-L3)。"
    },
    5963: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：海滩排排遮阳伞与沿岸建筑原本暖光大面积系统性偏冷泛暗青蓝灰(D-L1, E2-L1, F-L1)。"
    },
    5965: {
        "score": 5.0,
        "severities": {"C": "L1", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：雪道滑雪者身上鲜亮大红滑雪服严重脱色变暗褪为发灰暗红粉色(C-L1, E2-L2, F-L1)。"
    },
    5966: {
        "score": 2.25,
        "severities": {"C": "L2", "D": "L2", "E2": "L1", "F": "L2"},
        "note": "衣柜木质格板与蜷缩花猫身周严重泛起发暗冷青蓝紫杂色且粉垫脱色(C-L2, D-L2, E2-L1, F-L2)。"
    },
    5967: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：高架轻轨车身原本醒目鲜艳的明黄与草绿烤漆大面积脱色变暗偏土灰绿(C-L2, E2-L2, D-L1, F-L1)。"
    },
    5968: {
        "score": 2.27,
        "severities": {"C": "L3", "E2": "L3", "D": "L1", "F": "L2"},
        "note": "公园林荫草坪与灌木丛原本生机翠绿颠覆性彻底脱色错涂为惨淡枯灰土黄(C-L3, E2-L3, D-L1, F-L2)。"
    },

    # Sheet 06
    5970: {
        "score": 4.30,
        "severities": {"D": "L2", "E1": "L1", "F": "L1"},
        "note": "厨房内浅黄色吊柜与薄荷绿餐椅大面积严重偏冷泛刺目深青蓝冷灰调(D-L2, E1-L1, F-L1)。"
    },
    5971: {
        "score": 2.56,
        "severities": {"E1": "L2", "F": "L1"},
        "note": "火车站内停靠的流线型动车组车头与车身侧面深蓝装饰条纹过饱和刺目泛电光蓝(E1-L2, F-L1)。"
    },
    5972: {
        "score": 5.0,
        "severities": {"E1": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：餐盘内堆放的新鲜圣女果、西蓝花与黄柠檬水果拼盘系统性严重偏向刺目火红橙色过饱和失真(E1-L2, D-L1, F-L1)。"
    },
    5973: {
        "score": 4.55,
        "severities": {"E1": "L2", "D": "L1", "F": "L1"},
        "note": "沙发上依偎在主人身旁的哈巴狗面部与浅棕毛皮严重过饱和偏刺目深红铜色(E1-L2, D-L1, F-L1)。"
    },
    5974: {
        "score": 5.0,
        "severities": {"C": "L1", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：草场上两匹受训骏马原本纯正深栗红褐色皮毛大面积脱色欠饱和变暗土黄(C-L1, E2-L2, F-L1)。"
    },
    5976: {
        "score": 2.56,
        "severities": {"C": "L2", "E1": "L2", "D": "L1", "F": "L1"},
        "note": "书桌台灯暖黄灯罩与电脑屏幕边缘严重泛起刺目荧光深洋红紫假色(C-L2, E1-L2, D-L1, F-L1)。"
    },

    # Sheet 07
    5984: {
        "score": 2.32,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "双人床上的实木床头板与暖色床单大面积脱色欠饱和且偏冷青暗灰调(D-L1, E2-L1, F-L1)。"
    },
    5985: {
        "score": 2.05,
        "severities": {"C": "L2", "D": "L2", "E2": "L2", "F": "L2"},
        "note": "壁炉台上古典时钟与金属摆件原本灿烂温暖的金黄色泽严重脱色发暗，底座及横幅区域被大面积错涂为违和的冷蓝紫色杂光(C-L2, D-L2, E2-L2, F-L2)。"
    },
    5988: {
        "score": 2.43,
        "severities": {"C": "L3", "E1": "L1", "F": "L3"},
        "note": "烤盘内放置的整只生鸡表面颠覆性错涂为极其诡异刺目的鲜亮草绿色，配菜胡萝卜橙红偏浓(C-L3, E1-L1, F-L3)。"
    },
    5989: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：街头骑行者身穿的夹克与背景玻璃幕墙系统性偏暗暖红黄暗调，头巾边缘浑浊(D-L1, F-L1)。"
    },
    5991: {
        "score": 2.73,
        "severities": {"C": "L2", "E2": "L2", "D": "L1", "F": "L2"},
        "note": "公路边坡与防护栏身后的草坪绿重大面积严重脱色褪变为发暗干枯的灰土黄色(C-L2, E2-L2, D-L1, F-L2)。"
    },
    5992: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：快餐店内柜台背景货架与吃甜甜圈女孩的面部肤色系统性偏冷青蓝暗调，粉红糖霜颜色暗淡(D-L1, F-L1)。"
    },

    # Sheet 08
    5993: {
        "score": 2.56,
        "severities": {"E1": "L2", "F": "L1"},
        "note": "教堂尖顶上方的蓝天天色过于深沉浓郁，过饱和失真严重(E1-L2, F-L1)。"
    },
    5994: {
        "score": 2.43,
        "severities": {"C": "L2", "E2": "L2", "D": "L1", "F": "L1"},
        "note": "热狗大赛桌面上铺设的鲜黄塑料桌布大面积脱色发暗褪为脏污泥褐色，背景横幅文字色彩暗淡(C-L2, E2-L2, D-L1, F-L1)。"
    },
    5995: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    5997: {
        "score": 2.43,
        "severities": {"D": "L2", "E2": "L1", "F": "L1"},
        "note": "农舍餐厅内的暖米色墙壁与木质天花板大面积严重偏冷发暗，褪变为冰冷青灰调，实木餐桌椅欠饱和褪色(D-L2, E2-L1, F-L1)。"
    },
    5998: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：猫爬架右侧的窗台与墙壁表面大面积泛起脏污暖黄与红褐色杂光，偏色失真(D-L1, F-L1)。"
    },
    5999: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：钟楼外墙的红褐木构架与下方招牌整体色调系统性偏冷青蓝灰，原木质感偏冷暗(D-L1, F-L1)。"
    },

    # Sheet 09
    6000: {
        "score": 2.36,
        "severities": {"D": "L2", "F": "L2"},
        "note": "婚礼切蛋糕现场的新郎西装、新娘身侧拱门背景大面积严重偏向暗红褐色与浑浊红光(D-L2, F-L2)。"
    },
    6001: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6002: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：红色双层巴士身后的古典石砌建筑与天空背景整体色调轻微偏冷青蓝暗调(D-L1, F-L1)。"
    },
    6003: {
        "score": 2.43,
        "severities": {"C": "L2", "D": "L1", "F": "L2"},
        "note": "吃热狗青年身上穿着的纯白短袖T恤被大面积严重错涂为鲜亮天蓝色，草坪背景轻微偏冷(C-L2, D-L1, F-L2)。"
    },
    6004: {
        "score": 1.0,
        "severities": {},
        "note": "审查通过"
    },
    6006: {
        "score": 4.46,
        "severities": {"D": "L1", "F": "L1"},
        "note": "滑雪场地雪地阴影与后方树林枝杈整体色调偏向冷暗蓝紫调(D-L1, F-L1)。"
    },

    # Sheet 10
    6007: {
        "score": 2.61,
        "severities": {"D": "L2", "F": "L1"},
        "note": "电脑桌前侧坐青年的面部皮肤与短袖大面积严重偏向暗红褐色与冷紫发暗杂色(D-L2, F-L1)。"
    },
    6008: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：石砌钟楼塔身外墙大面积偏向浓艳的深焦糖暖红黄褐色，颜色失真(D-L1, E1-L1, F-L1)。"
    },
    6009: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6010: {
        "score": 4.46,
        "severities": {"D": "L1", "F": "L1"},
        "note": "客厅后方拱门处的垂幔窗帘与木地板表面系统性偏向脏污暖红黄调(D-L1, F-L1)。"
    },
    6011: {
        "score": 2.36,
        "severities": {"C": "L3", "D": "L2", "E1": "L2", "F": "L3"},
        "note": "网球场地表颠覆性错涂为大面积浓烈刺目的血红火红色，运动员运动衫错涂为孔雀蓝，视觉极其违和(C-L3, D-L2, E1-L2, F-L3)。"
    },
    6013: {
        "score": 2.13,
        "severities": {"C": "L2", "D": "L1", "E2": "L1", "F": "L2"},
        "note": "背景生机盎然的阳光绿树大面积脱色欠饱和偏冷青，男子面部肤色严重偏冷泛发暗青灰紫调，红色领结暗淡(C-L2, D-L1, E2-L1, F-L2)。"
    },

    # Sheet 11
    6014: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6015: {
        "score": 4.46,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "卧室内的暖米色墙壁与单人床铺整体色调系统性严重偏冷发暗，温馨暖光彻底褪为冰冷青灰调(D-L2, E2-L2, F-L2)。"
    },
    6016: {
        "score": 2.73,
        "severities": {"B": "L1", "D": "L1", "E2": "L1", "F": "L1"},
        "note": "滑板少年背景的山坡砂石与路边草木大面积脱色欠饱和偏冷青灰，少年手臂边缘轻微溢色(B-L1, D-L1, E2-L1, F-L1)。"
    },
    6017: {
        "score": 2.47,
        "severities": {"B": "L1", "C": "L2", "D": "L1", "F": "L2"},
        "note": "电视机屏幕显示的雪花噪点大面积错涂为浓艳刺目的蓝紫色，边框及男子手臂轮廓伴有边缘色料溢出(B-L1, C-L2, D-L1, F-L2)。"
    },
    6019: {
        "score": 2.23,
        "severities": {"C": "L1", "D": "L2", "E2": "L1", "F": "L1"},
        "note": "火车站台边缘原本鲜亮醒目的明黄色安全盲道线脱色变暗偏土黄色，高架水泥立柱系统性偏冷青蓝暗调(C-L1, D-L2, E2-L1, F-L1)。"
    },
    6020: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 12
    6022: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：厨房内木质地板与背景柜体系统性偏冷青蓝暗调，木材质感冰冷(D-L1, F-L1)。"
    },
    6023: {
        "score": 2.23,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "厨房内部木质橱柜立面大面积脱色欠饱和且偏冷青蓝暗调，木材质感暗沉冰冷(D-L1, E2-L1, F-L1)。"
    },
    6025: {
        "score": 4.55,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "白色旅游客车身后街景建筑与商铺招牌轻微脱色欠饱和且偏冷灰(D-L1, E2-L1, F-L1)。"
    },
    6030: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L1", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：复古摩托车的豹纹坐垫及车把边缘严重泛起冷青绿与蓝紫杂光，背景绿化与路面偏冷青蓝调(C-L2, D-L1, F-L2)。"
    },
    6032: {
        "score": 1.01,
        "severities": {"B": "L2", "C": "L3", "D": "L1", "E1": "L2", "F": "L3"},
        "note": "庭院木栅栏与背景墙体颠覆性大面积错涂为极其刺目的亮天蓝色假色，且蓝色色料严重溢出侵染芭蕉树叶(B-L2, C-L3, D-L1, E1-L2, F-L3)。"
    },
    6034: {
        "score": 2.47,
        "severities": {"D": "L1", "E2": "L2", "F": "L1"},
        "note": "湖畔露天木质餐桌与桌上菜盘大面积脱色欠饱和，人物肤色与群山背景整体色调偏冷青蓝暗调(D-L1, E2-L2, F-L1)。"
    },

    # Sheet 13
    6040: {
        "score": 2.61,
        "severities": {"D": "L2", "F": "L1"},
        "note": "新郎与新娘的面部皮肤及背景实木屋顶大梁大面积偏向浑浊暗红褐色与紫红暗调(D-L2, F-L1)。"
    },
    6046: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：台面上放置的香蕉果皮明黄色泽大面积脱色欠饱和，果蒂微绿褪色且表面轻微泛冷青灰(D-L1, E2-L1, F-L1)。"
    },
    6047: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：厨房灶台两侧的实木橱柜立面大面积脱色欠饱和，且系统性偏向暗冷青蓝灰调(D-L1, E2-L1, F-L1)。"
    },
    6048: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：客厅内部的米白墙壁与浅色地毯系统性偏冷青蓝暗调，室内暖光感偏弱(D-L1, F-L1)。"
    },
    6049: {
        "score": 2.36,
        "severities": {"C": "L2", "D": "L2", "F": "L2"},
        "note": "会议室内青年身后的背景墙壁与笔记本电脑桌面大面积错涂为发暗诡异的青绿冷调(C-L2, D-L2, F-L2)。"
    },
    6050: {
        "score": 1.08,
        "severities": {"C": "L3", "D": "L1", "E2": "L2", "F": "L2"},
        "note": "沙地马场上骑手身穿的鲜红长袖衬衫彻底脱色，颠覆性褪变错涂为极其暗淡干枯的泥浆灰肉粉色(C-L3, D-L1, E2-L2, F-L2)。"
    },

    # Sheet 14
    6051: {
        "score": 2.36,
        "severities": {"D": "L2", "F": "L1"},
        "note": "手握游戏方向盘的女士面部肤色及金色头发严重偏向暗紫红与暗冷青灰杂色(D-L2, F-L1)。"
    },
    6052: {
        "score": 2.36,
        "severities": {"D": "L1", "E2": "L1", "F": "L2"},
        "note": "网球场身后的大面积深红挡风网严重脱色发暗，褪变为发暗冷青黑灰调(D-L1, E2-L1, F-L2)。"
    },
    6055: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6059: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6061: {
        "score": 4.55,
        "severities": {"D": "L1", "F": "L1"},
        "note": "牧场大面积绿化草坪与远景木质马厩围栏轻微偏暗冷青绿调(D-L1, F-L1)。"
    },
    6062: {
        "score": 4.55,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "布置有三角彩旗的客厅墙壁与实木茶几轻微脱色欠饱和，且色调偏冷青灰(D-L1, E2-L1, F-L1)。"
    },

    # Sheet 15
    6063: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：宝马越野摩托车身后的野外灌木丛与金属车架整体色调轻微偏冷青蓝灰暗调(D-L1, F-L1)。"
    },
    6064: {
        "score": 4.30,
        "severities": {"C": "L1", "E1": "L2", "F": "L1"},
        "note": "厨房料理机底座旋钮区域错涂为艳亮天蓝，且透明杯身边缘及背景瓷砖深蓝过饱和浓艳(C-L1, E1-L2, F-L1)。"
    },
    6066: {
        "score": 4.55,
        "severities": {"D": "L1", "F": "L1"},
        "note": "喷泉池边沉思男子的手臂肤色与石砌基座整体色调轻微偏冷暗青灰调(D-L1, F-L1)。"
    },
    6067: {
        "score": 2.73,
        "severities": {"D": "L1", "E2": "L2", "F": "L1"},
        "note": "窗台上的白色陶瓷花瓶与窗框背景大面积偏向发暗浑浊的暗红黄杂色，绿植枝叶脱色发暗(D-L1, E2-L2, F-L1)。"
    },
    6068: {
        "score": 2.61,
        "severities": {"D": "L2", "F": "L1"},
        "note": "书桌上的电脑显示器底座与桌面表面大面积偏向浑浊刺目的暗红褐色与紫红杂光(D-L2, F-L1)。"
    },
    6071: {
        "score": 1.07,
        "severities": {"C": "L3", "D": "L2", "E2": "L3", "F": "L3"},
        "note": "大床上铺设的鲜红床单被套大面积严重脱色，颠覆性错涂褪变为肮脏暗沉的枯灰泥浆褐色(C-L3, D-L2, E2-L3, F-L3)。"
    },

    # Sheet 16
    6072: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：冬日路牌上方的晴空天色大面积严重过饱和，偏向刺目的深电光天蓝色(D-L1, E1-L2, F-L1)。"
    },
    6074: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6075: {
        "score": 2.23,
        "severities": {"C": "L2", "D": "L2", "F": "L2"},
        "note": "复古老照片边框温暖泛黄的纸张质感大面积脱色，被错涂为冰冷发青的淡青白调，男孩胸前领带偏色(C-L2, D-L2, F-L2)。"
    },
    6077: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6081: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：沙发后方室内绿植盆栽与墙角区域整体色调轻微偏冷青蓝暗调(D-L1, F-L1)。"
    },
    6083: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 17
    6086: {
        "score": 4.46,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "酒店客房内的壁挂液晶电视屏幕画面脱色欠饱和，墙壁与床单色调系统性轻微偏冷青暗灰调(D-L1, E2-L1, F-L1)。"
    },
    6087: {
        "score": 2.17,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "大象行走的沙土地面与围观人群背景大面积偏向浓烈刺目的深焦糖暖红黄褐色，过饱和失真严重(D-L2, E1-L2, F-L2)。"
    },
    6088: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6089: {
        "score": 1.0,
        "severities": {"A": ""},
        "note": "全图彻底上色失败，公园木质长椅、草坪绿化、坐着的人影与趴着的小白狗均未渲染任何色彩，呈现彻底的纯灰阶黑白状态(A)。"
    },
    6090: {
        "score": 2.56,
        "severities": {"C": "L2", "D": "L1", "F": "L1"},
        "note": "面包烘焙师傅身穿的鲜红工作T恤偏暗发紫泛刺目洋红，身后悬挂的绿植装饰偏冷青蓝暗调(C-L2, D-L1, F-L1)。"
    },
    6091: {
        "score": 4.46,
        "severities": {"D": "L1", "F": "L1"},
        "note": "厨房上方的实木吊柜与墙面整体色调轻微偏冷青蓝暗调，木饰面暖感微淡(D-L1, F-L1)。"
    },

    # Sheet 18
    6093: {
        "score": 2.36,
        "severities": {"C": "L3", "D": "L1", "F": "L2"},
        "note": "手托香蕉的人手手背与手指皮肤被颠覆性错涂为刺目浓艳的鲜红血色，香蕉表皮泛杂色(C-L3, D-L1, F-L2)。"
    },
    6095: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：酒店客厅上方的窗帘垂幔与天花板大面积偏向浓郁焦糖暖红黄暗调(D-L1, F-L1)。"
    },
    6096: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6097: {
        "score": 2.56,
        "severities": {"C": "L2", "E1": "L1", "F": "L1"},
        "note": "废弃房间左侧窗户玻璃与铁格栅颠覆性错涂为大面积浓艳刺目的明黄色假光(C-L2, E1-L1, F-L1)。"
    },
    6098: {
        "score": 2.43,
        "severities": {"B": "L1", "C": "L2", "E1": "L2", "F": "L2"},
        "note": "花园中大红非洲菊花瓣被错涂为刺目橙火红色且严重过饱和，花瓣边缘色料溢出侵染小猫面部胡须(B-L1, C-L2, E1-L2, F-L2)。"
    },
    6099: {
        "score": 2.17,
        "severities": {"D": "L1", "E2": "L2", "F": "L2"},
        "note": "酒店客房内的暖米色墙壁与木质地板整体色调严重偏冷发暗，温馨暖光彻底脱色褪变为阴冷青灰调(D-L1, E2-L2, F-L2)。"
    },

    # Sheet 19
    6100: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：斑马颈部的白色毛皮条纹大面积偏向浓郁焦糖暖红黄色调，色泽过暖发黄(D-L1, F-L1)。"
    },
    6101: {
        "score": 4.23,
        "severities": {"D": "L1", "F": "L1"},
        "note": "古典大厅内的整排红木陈列柜与雕花窗格大面积偏向暗红褐色与刺目冷紫杂光(D-L1, F-L1)。"
    },
    6102: {
        "score": 1.02,
        "severities": {"C": "L3", "D": "L2", "E2": "L3", "F": "L3"},
        "note": "夜晚街道上通体鲜艳明黄色的城市公交客车车身颠覆性彻底脱色，被严重错涂为发暗冰冷的蓝灰冷调(C-L3, D-L2, E2-L3, F-L3)。"
    },
    6103: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L1", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：女子身后的黄昏晚霞天空原本绚烂温暖的橙红晚霞大面积脱色，褪变为发暗阴冷的青灰调(C-L2, D-L1, E2-L2, F-L1)。"
    },
    6105: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：铁轨上行驶的电力机车车头红漆与沿线铁路绿化护坡整体色调轻微偏冷青蓝暗调(D-L1, F-L1)。"
    },
    6106: {
        "score": 1.0,
        "severities": {"A": ""},
        "note": "全图彻底上色失败，海滩沙滩、手抱冲浪板奔跑的冲浪者、海浪水花及背景天空均未渲染任何色彩，呈现彻底的纯灰阶黑白状态(A)。"
    },

    # Sheet 20
    6107: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：厨房双门不锈钢冰箱旁的实木橱柜立面整体色调轻微偏暖红黄褐色(D-L1, F-L1)。"
    },
    6110: {
        "score": 4.55,
        "severities": {"D": "L1", "E2": "L1", "F": "L2"},
        "note": "客厅内部原本明亮温暖的鹅黄色墙壁大面积严重脱色发暗，系统性偏向冰冷阴暗的青灰调(D-L1, E2-L1, F-L2)。"
    },
    6111: {
        "score": 2.17,
        "severities": {"D": "L1", "E1": "L2", "F": "L2"},
        "note": "野餐桌上摆放的番茄酱瓶、烤香肠拼盘大面积偏向浓烈刺目的深焦糖暖红黄色，过饱和失真严重(D-L1, E1-L2, F-L2)。"
    },
    6113: {
        "score": 2.17,
        "severities": {"C": "L2", "D": "L2", "E1": "L1", "F": "L2"},
        "note": "露天餐桌桌面与玻璃水杯边缘大面积泛起浓艳刺目的深洋红与冷紫杂光(C-L2, D-L2, E1-L1, F-L2)。"
    },
    6114: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6116: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：三头奶牛栖息的起伏草坡绿化草坪大面积严重过饱和，偏向刺目浓烈的荧光艳绿色(D-L1, E1-L2, F-L1)。"
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

FORBIDDEN_WORDS = ["某些区域", "局部区域", "关键区域", "部分区域", "某些部位", "某些主体", "关键主体"]

def validate_reviews():
    print(f"正在核验 Batch 29 评决字典条目数: {len(REVIEWS_B29)} (预期 120 组)...")
    assert len(REVIEWS_B29) == 120, f"条目数不符: {len(REVIEWS_B29)} != 120"
    
    for task_id, data in REVIEWS_B29.items():
        note = data["note"]
        sevs = data["severities"]
        
        # 1. 禁用词检查
        for fw in FORBIDDEN_WORDS:
            assert fw not in note, f"Task #{task_id} 命中禁用代词 '{fw}': {note}"
            
        # 2. 互斥检查
        if "E1" in sevs and "E2" in sevs:
            raise AssertionError(f"Task #{task_id} 同时标注了 E1 和 E2!")
            
        # 3. 熔断检查
        if "A" in sevs:
            assert sevs["A"] == "", f"Task #{task_id} 缺色 A 的 severity 必须为空字符串!"
            assert data["score"] == 1.0, f"Task #{task_id} 命中缺色 A 但 score 不是 1.0!"
            
        # 4. 放行检查
        if note == "审查通过":
            assert len(sevs) == 0, f"Task #{task_id} 标记为审查通过但 defects 不为空: {sevs}"
            
    print("Batch 29 评决字典词汇与逻辑断言 100% 通过!")

def apply_and_sync():
    validate_reviews()
    
    # 1. 保存独立的中间定物 JSON
    out_json = "d:/学业文件/MCL/上色评价_数据集标注/LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_29.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(REVIEWS_B29, f, ensure_ascii=False, indent=2)
    print(f"已导出中间定物字典: {out_json}")
    
    # 2. 加载全量文件同步更新
    all_path = "d:/学业文件/MCL/上色评价_数据集标注/LS_lcad_reviewer/exports/reviewed_1_10000_all.json"
    clean_path = "d:/学业文件/MCL/上色评价_数据集标注/LS_lcad_reviewer/exports/reviewed_1_10000_clean.json"
    
    print("正在加载 reviewed_1_10000_all.json...")
    with open(all_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)
        
    print("正在加载 reviewed_1_10000_clean.json...")
    with open(clean_path, "r", encoding="utf-8") as f:
        clean_data = json.load(f)
        
    anno_all_map = {item["human_review"]["task_id"]: item for item in all_data["annotations"]}
    anno_clean_map = {item["human_review"]["task_id"]: item for item in clean_data["annotations"]}
    
    updated_count = 0
    for task_id, rev in REVIEWS_B29.items():
        if task_id not in anno_all_map:
            print(f"警告: Task #{task_id} 不在 all_data 中!")
            continue
            
        item_all = anno_all_map[task_id]
        item_clean = anno_clean_map[task_id]
        
        # 构造缺陷列表
        defects = []
        is_melt_a = "A" in rev["severities"]
        for did, sev in rev["severities"].items():
            name = DEFECT_NAMES.get(did, did)
            # 描述提取
            desc = rev["note"]
            defects.append({
                "id": did,
                "name": name,
                "severity": sev,
                "description": desc
            })
            
        # 同步 item_all
        item_all["defects"] = defects
        item_all["review_status"] = "已核验"
        item_all["review_note"] = rev["note"]
        if is_melt_a:
            item_all["reviewed_score"] = 1.0
            item_all["needs_rescoring"] = False
        else:
            item_all["reviewed_score"] = None
            item_all["needs_rescoring"] = True
            
        # 同步 item_clean
        item_clean["defects"] = defects
        item_clean["review_status"] = "已核验"
        item_clean["review_note"] = ""
        if is_melt_a:
            item_clean["reviewed_score"] = 1.0
            item_clean["needs_rescoring"] = False
        else:
            item_clean["reviewed_score"] = None
            item_clean["needs_rescoring"] = True
            
        updated_count += 1
        
    print(f"成功同步更新 {updated_count} 条任务数据!")
    
    with open(all_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"已回写写入: {all_path}")
    
    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"已回写写入: {clean_path}")

if __name__ == "__main__":
    apply_and_sync()
