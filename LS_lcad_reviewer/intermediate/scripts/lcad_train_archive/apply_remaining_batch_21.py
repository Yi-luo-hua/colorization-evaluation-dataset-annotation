# -*- coding: utf-8 -*-
"""
apply_remaining_batch_21.py - Apply Batch 21 (Tasks #4519 ~ #4695) Reviews
"""

import json
import os
import re

BATCH_NO = 21
GROUNDING_FILE = "LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_21.json"
ALL_FILE = "LS_lcad_reviewer/exports/reviewed_1_10000_all.json"
CLEAN_FILE = "LS_lcad_reviewer/exports/reviewed_1_10000_clean.json"

BANNED_WORDS = [
    "局部关键区域", "关键主体或背景", "轮廓边缘处", "局部细节", "重要区域", "某些区域", "局部画面",
    "画面关键区域", "边缘区域", "主体部分", "背景区域", "关键物体", "部分区域"
]

def make_pass_review(task_id):
    return {
        "status": "PASS",
        "defects": [],
        "note": "审查通过"
    }

def make_revision_review(task_id, defects, note):
    return {
        "status": "REVISION",
        "defects": defects,
        "note": note
    }

REVIEWS = {
    # Sheet 01: [4519, 4521, 4522, 4523, 4526, 4527]
    4519: make_revision_review(4519, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "双人床床尾原本鲜艳明亮的深蓝色床旗被严重脱色错涂为暗沉灰白色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "床尾折叠毛巾与床单整体暗淡发灰，欠饱和。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "床头台灯照明暖光与墙面色调略显冷暗偏绿。"}
    ], "双人床床尾深蓝色床旗严重脱色错涂为灰白色，床头台灯暖色偏暗偏绿(C-L2, E2-L2, D-L1)"),

    4521: make_revision_review(4521, [
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "背景涂鸦墙的红紫与明黄喷绘色调浓艳刺眼，饱和度过度过曝。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "男子脖颈及耳部肤色被涂覆异常黄褐色污斑，左后方路人橙色服饰发灰。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "涂鸦墙与人物边缘杂色混浊，视觉自然度明显受损。"}
    ], "背景涂鸦墙红紫喷绘过于浓艳刺眼，男子颈部肤色出现黄褐污斑且边缘混浊(E1-L2, C-L2, F-L2)"),

    4522: make_revision_review(4522, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "白瓷花瓶的深褐红色瓶嘴与瓶口边缘被错涂为冷紫红色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "实木桌面原本温润红木色泽偏冷发紫，花瓶彩绘花朵轻微欠饱和。"},
        {"id": "B", "name": "溢色", "severity": "L1", "description": "瓶身彩绘色彩向白瓷边缘轻微溢出。"}
    ], "白瓷花瓶深褐红瓶嘴错涂为冷紫红色，实木桌面红木色泽偏冷发紫(C-L2, D-L2, B-L1)"),

    4523: make_revision_review(4523, [
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "棒球队员所穿的长袖深蓝内衬袖套与球帽色彩欠饱和偏暗，草坪绿茵略显枯黄。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "球场草坪与背景金属铁丝网偏暗发橄榄色。"}
    ], "棒球队员深蓝色内衬袖套与球帽偏暗泛灰，草坪绿茵饱和度偏低(E2-L1, D-L1)"),

    4526: make_revision_review(4526, [
        {"id": "D", "name": "偏色", "severity": "L1", "description": "阳台窗前采光区木地板及右侧办公椅面偏暗偏灰。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "室内堆叠的瓦楞纸箱及红色布艺小凳色彩略微暗淡欠饱和。"}
    ], "阳台窗边木地板与右侧办公椅偏暗偏灰，室内瓦楞纸箱色彩略显暗淡(D-L1, E2-L1)"),

    4527: make_revision_review(4527, [
        {"id": "A", "name": "缺色", "severity": "", "description": "全图上色失败呈现纯灰阶黑白图像，客机机身鲜艳橙红涂装与机鼻、垂直尾翼色彩彻底缺失。"}
    ], "全图上色失败呈现纯灰阶图像，客机橙红色机身涂装与机鼻尾翼完全未渲染呈现黑白(A)"),

    # Sheet 02: [4529, 4531, 4532, 4535, 4536, 4537]
    4529: make_revision_review(4529, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "夜景路灯下的木质长椅及地面照射区域偏生硬的黄绿冷色调，缺失GT温暖醇厚的金黄夜间灯光氛围。"},
        {"id": "C", "name": "错色", "severity": "L1", "description": "地面觅食鸽子的羽毛受青绿杂光污染。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "光晕过渡生硬，长椅背侧光影自然度受损。"}
    ], "夜景路灯下的木质长椅及地面偏生硬黄绿色调，地面鸽子羽毛受青绿杂光污染(D-L2, C-L1, F-L2)"),

    4531: make_pass_review(4531),

    4532: make_revision_review(4532, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "电线杆上的黄黑相间斜纹反光警示漆严重褪色发灰，丧失鲜艳明黄色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "左侧男子所穿的蓝白碎花短袖衬衫色彩欠饱和偏暗。"}
    ], "电线杆黄黑相间警示漆严重褪色发白，左侧男子蓝白碎花衬衫色彩暗淡欠饱和(C-L2, E2-L2)"),

    4535: make_revision_review(4535, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "矗立在雪地中的“DEAD END”菱形警示路牌黄色底漆严重褪色错涂为灰白色。"},
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "背景天空湛蓝色彩过于浓艳过饱和，饱和度显著虚高。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "雪地表面阴影区域色调偏暗偏蓝。"}
    ], "雪地中DEAD END菱形警示路牌黄色底漆褪色错涂为灰白，背景天空色彩过饱和(C-L2, E1-L2, D-L1)"),

    4536: make_revision_review(4536, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "两侧茂密的山体森林与铁轨路基整体严重偏冷发蓝紫，丢失GT自然深邃的墨绿植被色调。"},
        {"id": "E1", "name": "过饱和", "severity": "L1", "description": "火车车头前脸黄色警示漆与车灯泛光略显浓艳。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "森林树冠暗部泛冷光紫雾，视觉自然度明显受损。"}
    ], "山体茂密森林与铁轨路基整体偏冷发蓝紫，车头黄色漆浓艳且暗部泛紫雾(D-L2, E1-L1, F-L2)"),

    4537: make_revision_review(4537, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "击球手身穿的绿色棒球运动球衣被严重错涂为鲜红橙色。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "内野泥土红土球场与后方草坪色调轻微偏暖偏暗。"}
    ], "小棒球员击球手身穿的绿色运动球衣被严重错涂为鲜艳红橙色(C-L3, D-L1)"),

    # Sheet 03: [4538, 4540, 4542, 4544, 4546, 4548]
    4538: make_revision_review(4538, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "黑狗口中咬着的飞盘由鲜艳粉红色错涂为青蓝色，后方橙白相间交通锥错涂为绿白色。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "背景树木与路面偏暗发黄。"}
    ], "黑狗嘴里咬着的飞盘由鲜粉红错涂为青蓝色，背景橙白交通锥错涂为绿白色(C-L2, D-L1)"),

    4540: make_revision_review(4540, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "停在林道间的机车车身与侧边收纳边箱原本耀眼的荧光亮黄色被彻底脱色错涂为惨白灰白色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "机车整体严重脱色变白，饱和度极低。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "林间泥土小道与背景树木色彩略微发暗。"}
    ], "林间停放的摩托车车身与荧光黄边箱严重脱色错涂为惨白色(C-L3, E2-L3, D-L1)"),

    4542: make_revision_review(4542, [
        {"id": "E1", "name": "过饱和", "severity": "L1", "description": "水泥墙体中央的拱形木门红色油漆略微浓艳过饱和。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "水泥墙面略微偏冷偏灰，草坪绿意稍显暗淡。"}
    ], "拱形木门红色油漆略微浓艳过饱和，水泥墙面略微偏冷偏灰(E1-L1, D-L1)"),

    4544: make_revision_review(4544, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "整个厨房餐厅的天花板、木质料理台及橱柜全域严重泛暗暖黄褐色偏色，丢失GT清透自然明亮的日光环境。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "室内光影沉闷发暗，视觉自然度明显受损。"}
    ], "厨房天花板、料理台与橱柜全域严重泛暗暖黄褐色偏色，室内光影沉闷发暗(D-L2, F-L2)"),

    4546: make_pass_review(4546),

    4548: make_revision_review(4548, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "酒店客房天花板、白色窗帘及人物白衬衫全域严重偏暗黄褐色，丧失GT窗边清透自然日光。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "室内阴影发沉发乌，视觉自然度受损。"}
    ], "酒店客房天花板、窗帘及白衬衫全域严重偏暗黄褐色，光影发沉发乌(D-L2, F-L1)"),

    # Sheet 04: [4550, 4552, 4554, 4556, 4561, 4562]
    4550: make_revision_review(4550, [
        {"id": "D", "name": "偏色", "severity": "L1", "description": "白色四柱床架、床单被褥及墙面整体色调轻微泛暖偏黄，缺乏GT纯正洁净的素白色泽。"}
    ], "白色四柱床架与床单被褥色调轻微泛暖偏黄，缺乏纯净素白质感(D-L1)"),

    4552: make_revision_review(4552, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "古典油画中的石拱廊与壁画整体严重偏冷发红绿杂色，丢失GT油画原本厚重古朴的金黄暖褐色调。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "白马与花豹皮毛色彩饱和度偏低。"}
    ], "古典壁画石拱廊偏冷泛杂色，丢失原本厚重古朴的金黄暖褐色调(D-L2, E2-L1)"),

    4554: make_revision_review(4554, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "滑雪运动员身穿的浅蓝色滑雪服及雪裤被错涂并加深为深蓝紫色。"},
        {"id": "E1", "name": "过饱和", "severity": "L1", "description": "滑雪服与滑雪板边缘色彩浓艳偏深。"}
    ], "滑雪运动员所穿浅天蓝滑雪服及雪裤错涂加深为深蓝紫色(C-L2, E1-L1)"),

    4556: make_revision_review(4556, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "前景男子身穿的珊瑚橙红色Polo衫被明显错涂为浓艳刺眼的洋红色/荧光粉红。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "厨房背景橱柜与操作台偏冷偏暗。"}
    ], "前景男子身穿的珊瑚橙红Polo衫错涂为刺眼洋红粉色，厨房背景偏暗偏冷(C-L2, D-L1)"),

    4561: make_revision_review(4561, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "点心架顶层的粉红色精致法式小蛋糕严重褪色错涂为灰褐色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "整个点心托盘上的甜品色泽暗淡欠饱和，丧失诱人甜美光泽。"}
    ], "点心架顶层粉红色蛋糕甜品褪色错涂为灰褐色，糕点整体色彩暗淡欠饱和(C-L2, E2-L2)"),

    4562: make_revision_review(4562, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "冲浪者防寒服上的鲜橙红色头部风帽被完全脱色错涂为灰黑色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "海面波浪海水整体严重褪色发灰，丧失GT碧海蓝天的自然蔚蓝水色。"}
    ], "冲浪者鲜艳橙红色防寒风帽被脱色错涂为灰黑色，海浪海水严重泛灰褪色(C-L2, E2-L2)"),

    # Sheet 05: [4565, 4567, 4568, 4569, 4570, 4572]
    4565: make_revision_review(4565, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "击球手脚下的内野沙土区域大面积错涂为青绿色与草斑色，违背棒球红土常识。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "击球手橙红色球衣与捕手护具色温偏暗偏紫，外野草坪偏浓艳青绿。"},
        {"id": "E1", "name": "过饱和", "severity": "L1", "description": "外野草坪绿意过饱和。"}
    ], "内野沙土区域大面积错涂为异常草绿色，击球手橙红球衣偏暗偏紫(C-L2, D-L2, E1-L1)"),

    4567: make_revision_review(4567, [
        {"id": "D", "name": "偏色", "severity": "L3", "description": "全图系统性严重偏向赤红暖褐色调，背景冷色木墙与右侧奶牛毛色被染成刺眼红褐色。"},
        {"id": "C", "name": "错色", "severity": "L3", "description": "前景女孩所穿的鲜艳青蓝色外套被严重脱色错涂为灰褐色。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "肤色与环境光影过度泛红过曝，视觉可信度严重失真。"}
    ], "全图严重泛赤红暖褐色偏色，前景女孩青蓝色外套严重脱色错涂为灰褐色(D-L3, C-L3, F-L2)"),

    4568: make_pass_review(4568),

    4569: make_revision_review(4569, [
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "客厅内的皮质扶手椅被涂覆为刺眼过饱和的赤红/紫红色，饱和度严重溢出。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "地毯与墙面整体偏冷偏紫，丢失GT自然米黄色温馨氛围。"}
    ], "客厅皮质扶手椅涂覆刺眼过饱和的紫红色，地毯与墙面偏冷偏紫(E1-L2, D-L2)"),

    4570: make_revision_review(4570, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "厨房水槽上方的百叶窗及透过窗户的室外天光整体严重偏暗黄褐色，丧失GT窗边清透自然采光。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "不锈钢水槽与水龙头金属冷色质感略显发灰。"}
    ], "厨房百叶窗与室外采光全域偏暗黄褐色，不锈钢水槽金属质感发灰(D-L2, E2-L1)"),

    4572: make_pass_review(4572),

    # Sheet 06: [4574, 4575, 4576, 4577, 4579, 4582]
    4574: make_revision_review(4574, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "消防栓顶部的深蓝色星条旗圆顶漆料变暗发脏，红色条纹漆面发污欠饱和。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "消防栓红色漆料与草地绿意欠饱和。"}
    ], "消防栓顶部的深蓝色星条圆顶漆面发暗变脏，红白条纹漆料暗沉欠饱和(C-L2, E2-L1)"),

    4575: make_revision_review(4575, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "合影滑雪者身穿的亮青蓝色防寒服及亮黄绿色滑雪外套严重褪色错涂为深灰黑色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "左侧女士洋红色羽绒服色泽暗淡严重欠饱和。"}
    ], "滑雪者身穿的亮青蓝色与亮黄绿滑雪外套严重脱色错涂为深灰黑色(C-L2, E2-L2)"),

    4576: make_revision_review(4576, [
        {"id": "D", "name": "偏色", "severity": "L1", "description": "男子面部与颈部肤色略微偏冷偏粉，缺乏GT自然的健康暖色血色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "手中披萨饼底烘焙金黄焦香质感略显发灰。"}
    ], "男子面部肤色略微偏冷偏粉，披萨饼皮金黄烘焙色泽略显发灰(D-L1, E2-L1)"),

    4577: make_revision_review(4577, [
        {"id": "D", "name": "偏色", "severity": "L1", "description": "客房墙面与室内采光整体偏暗偏黄绿，空间通透度不足。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "床头深红布艺扶手椅及行李架红漆色泽暗淡欠饱和。"}
    ], "客房整体光影偏暗发黄绿，深红色布艺扶手椅色泽暗淡欠饱和(D-L1, E2-L1)"),

    4579: make_pass_review(4579),

    4582: make_revision_review(4582, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "背景繁茂森林树冠全域严重偏暗黄褐色，丧失GT生机盎然的自然浓绿生机。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "骑马者服饰及马匹毛色欠饱和偏灰。"}
    ], "背景繁茂森林树冠全域偏暗黄褐色，骑马者服饰与马匹色泽暗淡欠饱和(D-L2, E2-L2)"),

    # Sheet 07: [4584, 4585, 4587, 4588, 4589, 4590]
    4584: make_revision_review(4584, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "左侧场边观众所穿的鲜艳亮橙色卫衣被彻底错涂为冷青蓝色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "外野草坪及击球手红色球衣色彩偏暗欠饱和。"}
    ], "场边观众身穿的鲜艳亮橙色卫衣被严重错涂为青蓝色，草坪色彩偏暗(C-L3, E2-L1)"),

    4585: make_revision_review(4585, [
        {"id": "D", "name": "偏色", "severity": "L1", "description": "厨房下层橱柜及不锈钢家电表面略微偏暗偏红紫，金属原色稍显失真。"}
    ], "厨房下层橱柜及不锈钢家电表面略微偏暗发紫红，金属冷光质感轻微受损(D-L1)"),

    4587: make_revision_review(4587, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "落地大窗外的茂密绿化树木被严重脱色错涂为灰褐色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "窗外植被色彩严重欠饱和。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "室内白色天花板与沙发阴影偏冷发蓝紫。"}
    ], "落地窗外原本葱郁的绿化树木脱色错涂为灰褐色，室内色调偏冷发蓝紫(C-L2, E2-L2, D-L1)"),

    4588: make_revision_review(4588, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "玻璃果盘中的青绿/浅红葡萄串被错涂为浓艳刺眼的胡萝卜橙红色。"},
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "水果整体饱和度严重虚高过饱和，高光区域泛荧光感。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "葡萄与果盘边缘溢色生硬，视觉自然度明显受损。"}
    ], "果盘中的葡萄串被严重错涂为浓艳刺眼的橙红色，水果饱和度过饱和且边缘生硬(C-L2, E1-L2, F-L2)"),

    4589: make_revision_review(4589, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "四格拼图中泰迪熊的姜黄色连帽衫被错涂为暗沉紫灰色，下方纸杯蛋糕的明黄色糖霜错涂发污。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "毛绒玩具被毛与烘焙甜点全域严重偏冷泛蓝紫杂色。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "色彩交界处杂色斑驳，自然度严重受损。"}
    ], "泰迪熊姜黄连帽衫错涂为暗沉紫灰色，蛋糕糖霜偏暗发污且全图泛蓝紫杂色(C-L2, D-L2, F-L2)"),

    4590: make_pass_review(4590),

    # Sheet 08: [4591, 4592, 4594, 4595, 4596, 4598]
    4591: make_revision_review(4591, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "街道上方悬挂的明黄色与鲜橙色雨伞天棚大面积错涂为青绿及灰紫色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "伞顶漫射光与下方行人街景全域严重偏冷泛青蓝。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "伞面色彩杂乱交织且过渡粗糙，自然度受损。"}
    ], "街道上方悬挂的明黄与鲜橙色彩伞错涂为青绿及灰紫色，全图严重偏冷泛青(C-L2, D-L2, F-L2)"),

    4592: make_revision_review(4592, [
        {"id": "D", "name": "偏色", "severity": "L1", "description": "拆包裹的手部肤色与牛皮纸箱表面略微偏冷偏粉，缺乏自然暖褐色泽。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "箱内红色物品包装色彩纯度略显欠饱和。"}
    ], "拆包裹的手部肤色与牛皮纸箱表面偏冷偏粉，箱内红色物品色彩略显暗淡(D-L1, E2-L1)"),

    4594: make_pass_review(4594),

    4595: make_revision_review(4595, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "铁道货运场上方原本深邃湛蓝的暮色天空被严重错涂为灰红粉褐色。"},
        {"id": "D", "name": "偏色", "severity": "L3", "description": "天空与远方地平线晚霞全域严重偏冷泛脏粉红，彻底丢失GT暮色晚霞的冷暖强烈对比。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "铁轨路基与信号灯光色泽暗淡欠饱和。"}
    ], "深邃湛蓝暮色夜空被严重错涂为脏粉灰褐色，彻底丢失暮色晚霞的冷暖反差(C-L3, D-L3, E2-L2)"),

    4596: make_revision_review(4596, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "果盘托盘中成熟金黄的香蕉被错涂为荧光生硬的青黄杂色。"},
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "托盘旁垂落的洋红色布巾色彩浓艳过饱和。"},
        {"id": "B", "name": "溢色", "severity": "L1", "description": "洋红布巾色彩向白色托盘边缘轻微溢出。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "水果与布艺高光生硬违和，视觉自然度明显受损。"}
    ], "托盘中成熟金黄香蕉错涂为荧光青黄色，洋红布巾过饱和且边缘溢色(C-L2, E1-L2, B-L1, F-L2)"),

    4598: make_pass_review(4598),

    # Sheet 09: [4599, 4600, 4602, 4603, 4605, 4606]
    4599: make_pass_review(4599),

    4600: make_revision_review(4600, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "浴室墙面、镜框与洗手台全域严重偏暖发暗红褐色，丢失GT原本清爽淡雅的灰绿漆面环境。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "灰绿色墙壁被整体错涂为暗沉棕褐色。"}
    ], "浴室灰绿色墙面被大面积错涂为暗红褐色，全图色调严重偏暖泛黄褐(D-L2, C-L2)"),

    4602: make_pass_review(4602),

    4603: make_revision_review(4603, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "漫步在土路上的非洲象群粗糙皮肤被错涂为异常浓重的赤红泥褐色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "全图系统性偏暖泛红黄，道路与树冠暗部偏暖色。"}
    ], "非洲象群粗糙皮肤被明显错涂为浓重赤红褐色，全图色调偏暖泛红黄(C-L2, D-L2)"),

    4605: make_revision_review(4605, [
        {"id": "E1", "name": "过饱和", "severity": "L1", "description": "餐盘中烘焙吐司及果酱色泽略微过饱和偏艳。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "白色餐盘阴影与顶部庭院树冠略微偏冷偏紫。"}
    ], "餐盘烘焙吐司色泽略显过饱和，白色餐盘阴影及庭院绿树略显偏冷发紫(E1-L1, D-L1)"),

    4606: make_revision_review(4606, [
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "前景深盘披萨的金黄芝士与番茄红酱过于浓艳过饱和，高光刺眼。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "背景餐馆木质卡座与女子面部肤色略微偏粉红。"}
    ], "深盘披萨金黄芝士与番茄红酱过于浓艳过饱和，背景卡座色温偏粉(E1-L2, D-L1)"),

    # Sheet 10: [4607, 4608, 4610, 4611, 4612, 4613]
    4607: make_revision_review(4607, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "厨房台面上的翠绿色佐料小碗被错涂为深青蓝色，咖啡伴侣包装罐红色标签偏冷泛紫。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "台面香蕉与整体光照偏暗偏冷。"}
    ], "厨房台面翠绿色佐料小碗错涂为深青蓝色，包装罐红色标签偏冷泛紫(C-L2, D-L1)"),

    4608: make_revision_review(4608, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "户外街道、桥梁护栏与人物衣着全域严重偏冷泛洋红紫光，彻底丢失GT原本明亮温润的下午暖阳氛围。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "逆光高光区域泛紫色雾状光晕，视觉自然度明显受损。"}
    ], "全图严重泛洋红紫光偏色，丢失原本明媚暖阳氛围且高光区域泛紫雾(D-L2, F-L2)"),

    4610: make_revision_review(4610, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "弧形木质吧台操作台面及地砖全域严重偏暗红褐色，丢失GT自然清新的原木浅黄质感。"}
    ], "弧形木质吧台台面及地砖全域严重偏暗红褐色，丢失自然原木浅黄色泽(D-L2)"),

    4611: make_pass_review(4611),

    4612: make_revision_review(4612, [
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "公园草坪绿草过于浓艳刺眼呈荧光黄绿色，饱和度显著过饱和。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "青年所穿牛仔裤及运动鞋色调偏暗泛紫，与草坪形成违和反差。"}
    ], "公园草坪呈过于浓艳刺眼的荧光黄绿色，青年牛仔裤色调偏暗泛紫(E1-L2, D-L2)"),

    4613: make_revision_review(4613, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "停靠在街角的福特复古卡车明亮的天蓝色车漆被严重褪色错涂为灰暗的蓝紫灰色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "复古卡车天蓝色漆面严重欠饱和褪色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "沿街建筑立面与街景全域偏冷发灰绿，丧失GT阳光明媚的暖黄街景氛围。"}
    ], "福特复古卡车明亮天蓝车身严重脱色错涂为灰暗蓝紫色，沿街建筑偏冷泛灰(C-L2, E2-L2, D-L2)"),

    # Sheet 11: [4615, 4617, 4618, 4620, 4621, 4622]
    4615: make_revision_review(4615, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "背景天空与树枝绿叶整体偏暗发灰泛青蓝偏色，丢失GT清朗蓝天的通透感。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "树枝上挂着的熟透柑橘橙红色彩略显暗淡欠饱和。"}
    ], "背景天空与树叶整体偏暗发灰泛冷，树上成熟柑橘色彩略显暗淡(D-L2, E2-L1)"),

    4617: make_revision_review(4617, [
        {"id": "E1", "name": "过饱和", "severity": "L1", "description": "架子上的台灯照明高光区域泛明黄过曝，光晕边缘生硬。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "红色真皮单人沙发与地板阴影偏暗泛紫。"}
    ], "架上台灯照明高光过度泛黄过曝，红色单人沙发与地面阴影偏暗泛紫(E1-L1, D-L1)"),

    4618: make_pass_review(4618),

    4620: make_pass_review(4620),

    4621: make_revision_review(4621, [
        {"id": "D", "name": "偏色", "severity": "L3", "description": "整个浴室洗漱间严重偏向惨白青蓝色冷调，彻底抹杀GT原本温馨浓郁的金黄暖光照明氛围。"},
        {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "墙面、镜面与白色浴巾色彩被大面积抽空脱色，呈现冰冷灰白的严重欠饱和感。"}
    ], "浴室全域严重偏冷泛惨白青蓝色，彻底抹杀原本温馨浓郁的金黄暖光氛围(D-L3, E2-L3)"),

    4622: make_revision_review(4622, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "斑马身上的黑白条纹与木质围栏全域严重偏冷泛洋红紫光，丢失GT原木暖褐与自然毛色质感。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "围栏原木暗部泛紫色杂光，视觉自然度受损。"}
    ], "斑马黑白条纹与木质围栏全域严重偏冷泛洋红紫光，丢失原本自然暖褐色调(D-L2, F-L1)"),

    # Sheet 12: [4624, 4625, 4626, 4630, 4631, 4632]
    4624: make_revision_review(4624, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "历史复古明信片原本统一的单色褐灰墨迹被过度上色渲染为蓝绿水域与彩色地貌。"}
    ], "历史复古明信片原本统一的褐灰单色调被过度渲染为蓝绿水域与杂色地表(C-L2)"),

    4625: make_revision_review(4625, [
        {"id": "B", "name": "溢色", "severity": "L2", "description": "竹编淘箩右侧背景出现明显的彩色杂色溢色与条带状彩斑伪影。"},
        {"id": "E1", "name": "过饱和", "severity": "L1", "description": "局部溢色杂斑饱和度刺眼浓艳。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "边缘彩条伪影严重破坏静物画面的视觉自然度。"}
    ], "竹编淘箩右侧背景出现明显的彩条溢色与高饱和色斑伪影(B-L2, E1-L1, F-L2)"),

    4626: make_revision_review(4626, [
        {"id": "D", "name": "偏色", "severity": "L1", "description": "涉水奔跑的马群、浅水河滩与背景树木略微偏冷泛蓝紫杂色。"}
    ], "浅水河滩与背景灌木色调略微偏冷泛蓝紫，河水倒影杂色轻微(D-L1)"),

    4630: make_pass_review(4630),

    4631: make_pass_review(4631),

    4632: make_revision_review(4632, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "操作移动披萨烤炉的男子面部、手臂及衣服严重偏向刺眼洋红紫光。"},
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "人物肤色与衣服饱和度过度充盈，呈现不自然的粉紫色过曝。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "烤炉金属外壳反射大面积紫雾杂斑，视觉可信度受损。"}
    ], "操作移动烤炉的男子肤色与衣着严重偏向刺眼洋红粉色，金属烤炉泛紫斑(D-L2, E1-L2, F-L2)"),

    # Sheet 13: [4633, 4635, 4638, 4643, 4644, 4645]
    4633: make_revision_review(4633, [
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "动态模糊的红色双层巴士车身红色车漆过于浓艳刺眼，饱和度严重溢出。"},
        {"id": "B", "name": "溢色", "severity": "L2", "description": "巴士红色动态拖影向沿街英伦石砌建筑与路面明显漫延溢色。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "运动模糊边缘伪影生硬，视觉自然度明显受损。"}
    ], "红色双层巴士动态拖影过于浓艳刺眼，红色漆料向沿街建筑严重溢色(E1-L2, B-L2, F-L2)"),

    4635: make_revision_review(4635, [
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "特技飞行编队的四架战机机身色彩及原本晴朗的蔚蓝天空严重发灰褪色，丧失通透蓝天。"}
    ], "特技飞行战机机身涂装及背景晴朗蔚蓝天空严重褪色发灰，饱和度显著偏低(E2-L2)"),

    4638: make_revision_review(4638, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "室内背景墙面整体严重偏冷发荧光青绿色，西服套装偏暗泛紫。"}
    ], "室内背景墙面整体偏冷泛青绿杂色，西服套装色调偏暗泛紫(D-L2)"),

    4643: make_pass_review(4643),

    4644: make_revision_review(4644, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "停在站台的CityBus城市公交车下半部分原本明亮的皇家深蓝色车身被严重错涂为鲜红色。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "背景树木与路面略微泛暗。"}
    ], "CityBus城市公交车下半部分原本深蓝色车漆被严重错涂为鲜红色(C-L3, D-L1)"),

    4645: make_revision_review(4645, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "非洲草原金黄色枯草地被大面积抽空暖色偏冷发灰，彻底丧失GT热带荒原的金黄阳光感。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "整个地面植被严重欠饱和褪色发白。"}
    ], "非洲草原原本金黄色的荒草地大面积脱色偏冷发灰白，严重欠饱和(D-L2, E2-L2)"),

    # Sheet 14: [4646, 4647, 4648, 4649, 4650, 4652]
    4646: make_pass_review(4646),

    4647: make_pass_review(4647),

    4648: make_revision_review(4648, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "桌面原本清爽的青绿色餐垫被错涂为深蓝紫色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "蛋糕顶部的糖霜及白色餐盘反光严重偏冷泛红紫杂色。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "餐具与食物冷暖光影不协调，视觉自然度受损。"}
    ], "桌面青绿色餐垫被错涂为深蓝紫色，白色餐盘与蛋糕糖霜偏冷泛紫(C-L2, D-L2, F-L1)"),

    4649: make_revision_review(4649, [
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "背景天空被渲染为过于浓艳偏暗的青蓝色，饱和度明显过饱和。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "加航客机机身腹部与机翼背光面偏暗泛冷紫。"}
    ], "背景天空被渲染为过度浓艳的青蓝色，客机腹部阴影偏暗发冷紫(E1-L2, D-L1)"),

    4650: make_revision_review(4650, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "街边摊位的红黄相间条纹遮阳伞蓬被严重错涂为异常草绿色与枯黄色。"},
        {"id": "B", "name": "溢色", "severity": "L2", "description": "伞蓬绿色杂色向下方行人白色服饰与汽车引擎盖严重漫延溢色。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "街道摊位色彩杂乱失真，视觉自然度严重受损。"}
    ], "摊位红黄条纹遮阳伞蓬被严重错涂为草绿枯黄色，且杂色向行人服饰大面积溢色(C-L3, B-L2, F-L2)"),

    4652: make_revision_review(4652, [
        {"id": "D", "name": "偏色", "severity": "L1", "description": "棕褐色真皮沙发及地板阴影整体偏冷偏暗泛青黑，缺乏天然皮革润泽光泽。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "实木茶几木纹质感略显发灰暗淡。"}
    ], "棕色真皮沙发与地面阴影偏冷泛青黑，实木茶几色泽暗淡欠饱和(D-L1, E2-L1)"),

    # Sheet 15: [4653, 4654, 4655, 4656, 4657, 4658]
    4653: make_revision_review(4653, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "栖息在金属刹车盘孔洞中的麻雀羽翼末端被染上异常刺眼的洋红杂斑。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "机械刹车盘金属轮毂表面严重偏冷泛蓝紫光。"},
        {"id": "B", "name": "溢色", "severity": "L1", "description": "轮毂红杂色向鸟羽周围渗入溢色。"}
    ], "麻雀翅膀末端羽毛被染上异常洋红杂斑，金属轮毂表面严重偏冷泛蓝紫(C-L2, D-L2, B-L1)"),

    4654: make_pass_review(4654),

    4655: make_pass_review(4655),

    4656: make_revision_review(4656, [
        {"id": "D", "name": "偏色", "severity": "L1", "description": "水边礁石表面色调略微偏冷偏灰，缺乏自然砂岩质感。"}
    ], "水边礁石表面色调略微偏冷偏灰，缺乏自然砂岩质感(D-L1)"),

    4657: make_pass_review(4657),

    4658: make_revision_review(4658, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "前景圆柱原本鲜艳的赤红色被错涂为深蓝紫色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "背景墙面与走廊采光全域严重偏冷泛青蓝白，彻底抹杀GT原本温馨通透的米金暖光氛围。"}
    ], "室内大堂立柱原本鲜艳赤红错涂为深蓝紫色，背景走廊严重偏冷泛青蓝(C-L2, D-L2)"),

    # Sheet 16: [4660, 4661, 4662, 4663, 4665, 4666]
    4660: make_revision_review(4660, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "手中纸巾托着的金黄烘焙甜甜圈被严重错涂为发霉般的暗青绿杂色。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "背景果盘中的水果被粗糙错涂为生硬蓝色。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "甜甜圈绿斑使食物质感完全失真，视觉自然度严重受损。"}
    ], "手中金黄烘焙甜甜圈严重错涂为发霉般的暗青绿色，背景果盘错涂为生硬蓝色(C-L3, C-L2, F-L2)"),

    4661: make_revision_review(4661, [
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "网球运动员所穿的青绿色运动T恤与短裤严重发灰褪色，色彩饱和度极低。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "网球场地面及背景围网偏冷偏暗。"}
    ], "网球运动员运动短袖与短裤严重发灰脱色，网球场及围网偏暗泛冷(E2-L2, D-L1)"),

    4662: make_revision_review(4662, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "浴室瓷砖墙面与镜子边缘严重偏冷发青蓝，丢失GT原本温馨的暖黄采光。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "幼童面颊及额头受冷色杂光污染呈现生硬青绿色斑。"}
    ], "浴室瓷砖全域严重偏冷泛青蓝，幼童面部肤色受冷光污染呈现生硬青绿杂斑(D-L2, C-L2)"),

    4663: make_revision_review(4663, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "厨房原本温润金黄的原木橱柜被大面积严重脱色错涂为惨白灰白色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "橱柜原木材质色彩严重欠饱和抽空。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "室内墙面与操作台全域偏冷发灰绿，丧失家庭厨房的温馨感。"}
    ], "厨房温润金黄的原木橱柜被大面积严重脱色错涂为惨白色，室内全域偏冷发灰(C-L2, E2-L2, D-L2)"),

    4665: make_pass_review(4665),

    4666: make_revision_review(4666, [
        {"id": "D", "name": "偏色", "severity": "L1", "description": "紧凑盥洗室内马桶圈边缘及不锈钢洗手池轻微泛冷光偏色。"}
    ], "盥洗室马桶圈边缘及金属洗手池轻微泛冷光偏色(D-L1)"),

    # Sheet 17: [4669, 4671, 4672, 4673, 4674, 4675]
    4669: make_revision_review(4669, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "草原高草植被全域严重偏暗黄褐色，丧失GT生机盎然的清翠绿意。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "斑马母子身上的毛色略微暗淡欠饱和。"}
    ], "草原植被全域严重偏暗黄褐色，斑马毛色略显暗淡欠饱和(D-L2, E2-L1)"),

    4671: make_revision_review(4671, [
        {"id": "D", "name": "偏色", "severity": "L1", "description": "室内墙面珊瑚橙红漆面与窗帘暗部色调略微偏深偏暗。"}
    ], "室内珊瑚橙红漆面与窗帘暗部色调略显沉闷偏深(D-L1)"),

    4672: make_revision_review(4672, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "背景白色墙面、门框与室内采光全域严重泛暗暖黄褐色偏色，丢失GT原本干净明亮的白墙质感。"}
    ], "背景白色墙壁与门框全域严重泛暗黄褐色偏色，丢失原本明亮干净质感(D-L2)"),

    4673: make_revision_review(4673, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "黄色跑车引擎盖与轮拱高光漆面被严重错涂并混入生硬的青蓝/紫色杂光反光。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "车身漆面及轮毂阴影偏冷发蓝紫。"}
    ], "黄色跑车引擎盖与轮拱漆面混入生硬青蓝紫光杂色，轮毂阴影偏冷(C-L2, D-L2)"),

    4674: make_revision_review(4674, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "行人肩上原本鲜艳的玫粉色挎包被严重脱色错涂为灰褐色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "女士手持的粉色雨伞及背景复古卡车车身色彩暗淡欠饱和。"}
    ], "行人原本鲜艳的玫粉色挎包脱色错涂为灰褐色，雨伞色彩暗淡欠饱和(C-L2, E2-L2)"),

    4675: make_revision_review(4675, [
        {"id": "E1", "name": "过饱和", "severity": "L1", "description": "深盘披萨顶部的浓稠番茄红酱略显浓艳过饱和。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "烤制厚饼皮边缘焦香色泽偏冷偏灰，缺失GT金黄烘焙原色。"}
    ], "深盘披萨顶部番茄红酱略显浓艳过饱和，厚饼皮边缘色泽偏冷发灰(E1-L1, D-L1)"),

    # Sheet 18: [4676, 4677, 4678, 4680, 4681, 4682]
    4676: make_revision_review(4676, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "老人面部受光面与灰白头发被染上不自然的生硬黄绿色杂光。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "肤色过渡杂乱且泛油光荧光，视觉自然度明显受损。"}
    ], "老人面部与灰白头发染上不自然生硬黄绿杂光，肤色过渡生硬失真(D-L2, F-L2)"),

    4677: make_pass_review(4677),

    4678: make_pass_review(4678),

    4680: make_revision_review(4680, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "厨房木质吊柜与玻璃橱柜全域偏冷发暗青褐色，丢失GT原本温润金黄的原木暖光。"}
    ], "厨房木质吊柜全域偏冷发暗青褐色，丢失原本温润金黄原木暖光(D-L2)"),

    4681: make_pass_review(4681),

    4682: make_revision_review(4682, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "蛋糕托盘下方原本鲜绿色的桌面被彻底严重错涂为赤红橙色。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "毛毛虫造型蛋糕的绿色糖霜被严重混入发污的青蓝与暗紫色斑。"}
    ], "摆放蛋糕的鲜绿色桌面被彻底错涂为赤红橙色，蛋糕绿色糖霜混入暗紫斑(C-L3, C-L2)"),

    # Sheet 19: [4683, 4684, 4685, 4686, 4687, 4688]
    4683: make_revision_review(4683, [
        {"id": "D", "name": "偏色", "severity": "L1", "description": "早餐餐桌桌面及瓷咖啡杯阴影偏冷发蓝紫。"}
    ], "早餐餐桌桌面及瓷咖啡杯阴影偏冷泛蓝紫(D-L1)"),

    4684: make_revision_review(4684, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "前方飞机座椅靠背及小桌板航空餐食全域严重偏暗黄绿色，丢失GT原本清爽干净的机舱色调。"}
    ], "飞机座椅靠背及折叠小桌板航空餐全域偏暗泛黄绿，食物色泽发暗(D-L2)"),

    4685: make_pass_review(4685),

    4686: make_revision_review(4686, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "烤架上炙烤的香肠与肉排被错涂为浓艳刺眼的洋红鲜粉色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "金属烧烤网架及周围操作台偏冷泛紫光。"}
    ], "烤架上炙烤的香肠与肉排被错涂为刺眼洋红粉色，金属烤网偏冷泛紫(C-L2, D-L2)"),

    4687: make_pass_review(4687),

    4688: make_revision_review(4688, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "儿童短袖T恤上的哆啦A梦卡通头像经典亮蓝色头部被错涂为灰暗淡紫灰色。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "雨伞伞面与衣角阴影略微偏冷泛紫。"}
    ], "儿童T恤上的哆啦A梦卡通图案经典天蓝头部错涂为灰暗淡紫灰色(C-L2, D-L1)"),

    # Sheet 20: [4689, 4690, 4691, 4692, 4694, 4695]
    4689: make_revision_review(4689, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "白瓷餐盘中红烧牛肉酱汁边缘出现大面积刺眼的不自然亮黄色晕染杂斑。"},
        {"id": "E1", "name": "过饱和", "severity": "L1", "description": "西兰花绿色蔬菜过于浓艳荧光。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "酱汁黄斑与食材边缘生硬违和，严重破坏美食视觉可信度。"}
    ], "牛肉浓汁边缘出现大面积刺眼的亮黄色晕染杂斑，西兰花过于荧光浓艳(C-L2, E1-L1, F-L2)"),

    4690: make_revision_review(4690, [
        {"id": "D", "name": "偏色", "severity": "L3", "description": "背景木质电视柜、墙面及茶几全域严重偏冷偏蓝，彻底抹杀GT温暖温润的木纹与室内暖光。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "原木色茶几与背景木柜被大面积错涂为灰冷青蓝色。"}
    ], "背景木质电视柜、墙面及茶几全域严重偏冷泛青蓝，原木暖黄色调彻底丢失(D-L3, C-L2)"),

    4691: make_revision_review(4691, [
        {"id": "D", "name": "偏色", "severity": "L1", "description": "观光马车后方历史建筑石墙及树木略微偏冷泛暗。"}
    ], "马车后方建筑石墙与树木色调略微偏冷发暗(D-L1)"),

    4692: make_revision_review(4692, [
        {"id": "E1", "name": "过饱和", "severity": "L3", "description": "公园草坪绿草过于浓艳刺眼呈极度过饱和的荧光青绿色，高光溢出失真。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "木质长椅暗部与背景车辆偏暗泛紫。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "极度刺眼的荧光草色严重破坏整体视觉自然度。"}
    ], "公园草坪呈极度刺眼过饱和的荧光青绿色，木质长椅阴影偏暗泛紫(E1-L3, D-L1, F-L2)"),

    4694: make_revision_review(4694, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "披萨饼上的新鲜罗勒绿叶被严重错涂为发污的暗紫黑色，金黄鸡蛋与芝士褪色发白。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "披萨烘焙金黄芝士与熟鸡蛋严重欠饱和。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "烤制饼皮严重偏冷发灰，彻底丧失新鲜出炉烘焙香脆金黄光泽。"}
    ], "披萨罗勒绿叶严重错涂为暗紫黑色，金黄芝士鸡蛋褪色，饼皮偏冷发灰(C-L2, E2-L2, D-L2)"),

    4695: make_revision_review(4695, [
        {"id": "D", "name": "偏色", "severity": "L1", "description": "幼猫胸前及爪部白色软毛受杂光影响略微偏冷偏紫。"}
    ], "幼猫胸前及爪部白毛受环境杂光影响略显偏冷泛紫(D-L1)")
}

def main():
    print(f"=== Validating and Applying Batch {BATCH_NO:02d} Reviews ===")
    assert len(REVIEWS) == 120, f"Expected 120 reviews, got {len(REVIEWS)}"

    # 1. Check banned words
    violation_count = 0
    for tid, rev in REVIEWS.items():
        text_to_check = rev["note"] + " " + " ".join(d["description"] for d in rev["defects"])
        for bw in BANNED_WORDS:
            if bw in text_to_check:
                print(f"[ERROR] Task #{tid} contains banned word '{bw}'!")
                violation_count += 1
    assert violation_count == 0, f"Found {violation_count} banned word violations!"
    print("[PASS] Banned words audit: 100% clean (0 violations).")

    # 2. Check Defect A and logic
    for tid, rev in REVIEWS.items():
        has_a = any(d["id"] == "A" for d in rev["defects"])
        if has_a:
            assert len(rev["defects"]) == 1, f"Task #{tid} has Defect A but has other defects!"
            assert rev["defects"][0]["severity"] == "", f"Task #{tid} Defect A severity must be empty string!"

    pass_count = sum(1 for r in REVIEWS.values() if r["status"] == "PASS")
    rev_count = sum(1 for r in REVIEWS.values() if r["status"] == "REVISION")
    print(f"[STAT] Total: 120 | Pass: {pass_count} ({pass_count/len(REVIEWS)*100:.1f}%), Revisions: {rev_count} ({rev_count/len(REVIEWS)*100:.1f}%)")

    # 3. Save grounding JSON
    with open(GROUNDING_FILE, "w", encoding="utf-8") as f:
        json.dump(REVIEWS, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved grounding JSON to {os.path.abspath(GROUNDING_FILE)}")

    # 4. Synchronize into reviewed_1_10000_all.json and clean.json
    print("\nSynchronizing into reviewed_1_10000_all.json and clean.json...")
    with open(ALL_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    all_task_map = {ann["human_review"]["task_id"]: ann for ann in all_data["annotations"]}
    clean_task_map = {ann["human_review"]["task_id"]: ann for ann in clean_data["annotations"]}

    for tid, rev in REVIEWS.items():
        if tid not in all_task_map:
            print(f"[WARN] Task #{tid} not found in all_data annotations!")
            continue

        ann_all = all_task_map[tid]
        ann_clean = clean_task_map[tid]

        if rev["status"] == "PASS":
            ann_all["review_status"] = "已核验"
            ann_all["review_note"] = "审查通过"
            ann_all["defects"] = []
            ann_all["reviewed_score"] = None
            ann_all["needs_rescoring"] = True

            ann_clean["review_status"] = "已核验"
            ann_clean["review_note"] = ""
            ann_clean["defects"] = []
            ann_clean["reviewed_score"] = None
            ann_clean["needs_rescoring"] = True
        else:
            has_a = any(d["id"] == "A" for d in rev["defects"])
            ann_all["review_status"] = "已核验"
            ann_all["review_note"] = rev["note"]
            ann_all["defects"] = rev["defects"]
            ann_all["reviewed_score"] = 1.0 if has_a else None
            ann_all["needs_rescoring"] = False if has_a else True

            ann_clean["review_status"] = "已核验"
            ann_clean["review_note"] = ""
            ann_clean["defects"] = rev["defects"]
            ann_clean["reviewed_score"] = 1.0 if has_a else None
            ann_clean["needs_rescoring"] = False if has_a else True

    with open(ALL_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Successfully updated {os.path.abspath(ALL_FILE)}")

    with open(CLEAN_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Successfully updated {os.path.abspath(CLEAN_FILE)}")

if __name__ == "__main__":
    main()
