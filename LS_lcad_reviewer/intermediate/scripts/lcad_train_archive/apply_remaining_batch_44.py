# -*- coding: utf-8 -*-
"""
Batch 44 review data dictionary and application script.
Tasks: #8717 to #8901 (120 tasks)
"""
import json
import os

BATCH_44_REVIEWS = {
    # === Sheet 01 ===
    8717: {
        "defects": [],
        "review_note": "审查通过"
    },
    8718: {
        "defects": [],
        "review_note": "审查通过"
    },
    8721: {
        "defects": [],
        "review_note": "审查通过"
    },
    8722: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "黄昏十字路口上方原本深邃纯净的宝蓝色夜空被颠覆性严重脱色错染为暗淡浑浊的灰黑死色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "路面沥青与周围建筑物大面积浸染失真偏暗的冷灰青偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "黄昏天空原本深邃纯净的宝蓝色彩大面积严重脱色褪变。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "天空与地面色彩灰暗失真，视觉质感极为粗糙。"}
        ],
        "review_note": "黄昏十字路口上方原本深邃纯净的宝蓝色夜空被颠覆性严重脱色错染为暗淡浑浊的灰黑死色，路面沥青大面积浸染失真偏暗的冷灰青偏色。"
    },
    8725: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "糖果店门前路面与背景墙壁大面积微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "糖果店门前彩绘木桩表面的彩色油漆与红色消防栓大面积欠饱和脱色发暗。"}
        ],
        "review_note": "糖果店门前彩绘木桩表面的彩色油漆与红色消防栓大面积欠饱和脱色发暗，路面微染冷灰偏色。"
    },
    8726: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "雨后街头沿街商铺明亮的暖黄色橱窗灯光及湿滑沥青路面的金黄反光大面积浸染失真偏暗的冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "商铺橱窗与路面反光原本温馨璀璨的金黄色大面积欠饱和严重脱色褪变为冰冷灰白淡色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "雨后温馨暖黄夜景完全被破坏为冰冷青灰，视觉氛围严重失真。"}
        ],
        "review_note": "雨后街头沿街商铺明亮的暖黄色橱窗灯光及湿滑沥青路面的金黄反光大面积浸染失真偏暗的冷青蓝偏色，严重欠饱和脱色发暗。"
    },

    # === Sheet 02 ===
    8727: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "摩托车金属车把与反光镜边缘微染冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "摩托车车把后方原本温馨柔和的米黄色瓷砖墙面大面积欠饱和脱色偏冷灰。"}
        ],
        "review_note": "摩托车车把后方原本温馨柔和的米黄色瓷砖墙面大面积欠饱和脱色偏冷灰，金属车把微染冷青蓝偏色。"
    },
    8728: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "深色餐盘表面微染深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "深色餐盘中摆放的海鲜食材表面橙红色调过度浓艳刺眼。"}
        ],
        "review_note": "深色餐盘中摆放的海鲜食材表面橙红色调过度浓艳刺眼，餐盘表面微染深红棕暖偏色。"
    },
    8729: {
        "defects": [],
        "review_note": "审查通过"
    },
    8731: {
        "defects": [],
        "review_note": "审查通过"
    },
    8732: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "炭烤炉金属边缘与周围石板路面大面积微染红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "黑色炭烤炉铁丝网上烘烤的披萨表面番茄肉类食材色彩过度浓艳发红。"}
        ],
        "review_note": "黑色炭烤炉铁丝网上烘烤的披萨表面番茄肉类食材色彩过度浓艳发红，烤炉金属边缘微染红棕暖偏色。"
    },
    8733: {
        "defects": [],
        "review_note": "审查通过"
    },

    # === Sheet 03 ===
    8734: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "斑马身体黑白条纹边缘与泥土阴影微染偏暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "草原上斑马母子脚下的草坪植被色彩过度浓艳偏黄绿。"}
        ],
        "review_note": "草原上斑马母子脚下的草坪植被色彩过度浓艳偏黄绿，斑马黑白条纹边缘微染偏暖偏色。"
    },
    8735: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "卧铺车厢内壁与金属扶手微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "卧铺车厢内原本温馨明亮的暖橙色床垫与床单被褥大面积欠饱和严重脱色褪变为冰冷灰白淡色。"}
        ],
        "review_note": "卧铺车厢内原本温馨明亮的暖橙色床垫与床单被褥大面积欠饱和严重脱色褪变为冰冷灰白淡色，车厢内壁微染冷灰偏色。"
    },
    8737: {
        "defects": [],
        "review_note": "审查通过"
    },
    8738: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "工作台沥水架上堆放的白瓷碗盘与不锈钢锅具表面大面积浸染失真偏暗的红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "陶瓷洁白釉面与金属表面反光发黄发红过度浓艳。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "碗碟失真红棕暖偏色破坏了厨房餐具的洁净感。"}
        ],
        "review_note": "工作台沥水架上堆放的白瓷碗盘与不锈钢锅具表面大面积浸染失真偏暗的红棕暖偏色，洁白釉面发黄发暗。"
    },
    8740: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "背景红砖建筑钟楼与塑胶篮球场地面微染红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "篮球场上投篮少年身穿的红色球服背心色彩极度浓艳刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "球服过度发红与周围环境光照不协调。"}
        ],
        "review_note": "篮球场上投篮少年身穿的红色球服背心色彩极度浓艳刺眼，背景红砖建筑与地面微染红棕暖偏色。"
    },
    8741: {
        "defects": [],
        "review_note": "审查通过"
    },

    # === Sheet 04 ===
    8742: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "婴儿口中咬着的黄色塑料勺手柄被颠覆性错染为深青蓝异色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "婴儿面颊肤色微染深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "错色的塑料勺青蓝色料略显过度浓艳。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "婴儿用品错色失真，破坏面部柔和氛围。"}
        ],
        "review_note": "婴儿口中咬着的黄色塑料勺手柄被颠覆性错染为深青蓝异色，婴儿面颊肤色微染深红棕暖偏色。"
    },
    8744: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "沥青路面阴影微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "街道沥青路面上卧着的白牛皮毛暖色光晕与后方三轮车红色遮阳篷布大面积欠饱和脱色发暗。"}
        ],
        "review_note": "街道沥青路面上卧着的白牛皮毛暖色光晕与后方三轮车红色遮阳篷布大面积欠饱和脱色发暗，微染冷灰偏色。"
    },
    8745: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "棒球场开阔的草坪植被与观众看台栏杆大面积浸染失真偏暗的冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "内场红土地面色彩略显欠饱和脱色发暗。"}
        ],
        "review_note": "棒球场开阔的草坪植被与观众看台栏杆大面积浸染失真偏暗的冷青蓝偏色，内场红土地面色彩略显欠饱和脱色发暗。"
    },
    8746: {
        "defects": [],
        "review_note": "审查通过"
    },
    8748: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "湖面水体大面积浸染失真偏暗的冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "湖面滑水运动员身穿的原本鲜艳明亮的亮黄色救生背心大面积欠饱和脱色发暗。"}
        ],
        "review_note": "湖面滑水运动员身穿的原本鲜艳明亮的亮黄色救生背心大面积欠饱和脱色发暗，湖面水体大面积浸染失真偏暗的冷青蓝偏色。"
    },
    8749: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "后方圣诞树枝叶阴影微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "客厅靠背木椅的深色红木扶手与椅背大面积略显欠饱和脱色发暗。"}
        ],
        "review_note": "客厅靠背木椅的深色红木扶手与椅背大面积略显欠饱和脱色发暗，后方圣诞树枝叶微染冷灰偏色。"
    },

    # === Sheet 05 ===
    8750: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "周围蔬菜绿叶与木筐表面微染深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "菜市场摊位上码放的胡萝卜堆橙红色彩过度浓艳刺眼。"}
        ],
        "review_note": "菜市场摊位上码放的胡萝卜堆橙红色彩过度浓艳刺眼，周围蔬菜绿叶与木筐表面微染深红棕暖偏色。"
    },
    8752: {
        "defects": [
            {"id": "B", "name": "溢色", "severity": "L1", "description": "儿童手中握着的彩色气球玩偶表面色彩出现轻微边缘溢色侵染。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "儿童面部阴影微染冷灰偏色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "气球玩偶色块边缘衔接略有不自然溢彩。"}
        ],
        "review_note": "儿童手中握着的彩色气球玩偶表面色彩出现轻微边缘溢色侵染，儿童面部阴影微染冷灰偏色。"
    },
    8753: {
        "defects": [],
        "review_note": "审查通过"
    },
    8755: {
        "defects": [],
        "review_note": "审查通过"
    },
    8756: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "右侧青年身穿的衣物与披萨外卖盒原本鲜明的色彩错变为惨白无血色的灰白色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "聚会桌面与人物阴影微染冷青色偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "聚会餐桌前青年身穿的彩色短袖T恤与披萨外卖包装盒大面积欠饱和严重脱色褪变为冰冷灰白淡色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "衣物脱色严重失真，聚会气氛呆板不自然。"}
        ],
        "review_note": "聚会餐桌前青年身穿的彩色短袖T恤与披萨外卖包装盒大面积欠饱和严重脱色褪变为冰冷灰白淡色，微染冷青色偏色。"
    },
    8758: {
        "defects": [],
        "review_note": "审查通过"
    },

    # === Sheet 06 ===
    8759: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "披萨餐厅就餐区域背景墙面与餐桌表面大面积浸染失真深重的冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "幼儿面部肤色与披萨食材色彩欠饱和脱色发暗。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "原本温馨的餐厅暖黄光影完全被破坏为冷寂青绿，氛围失真。"}
        ],
        "review_note": "披萨餐厅就餐区域背景墙面与餐桌表面大面积浸染失真深重的冷青蓝偏色，幼儿面部肤色与披萨食材色彩欠饱和脱色发暗。"
    },
    8760: {
        "defects": [],
        "review_note": "审查通过"
    },
    8761: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "小女孩身穿的原本鲜艳纯正的大红色长袖卫衣被颠覆性严重脱色错染为灰白死色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "地面木质反光微染偏暗冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "身下金黄色实木地板大面积欠饱和严重脱色褪变为冰冷惨白的浅灰白色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "红衣与金黄地板全域脱色褪变为单薄灰白，视觉真实感遭到严重破坏。"}
        ],
        "review_note": "小女孩身穿的原本鲜艳纯正的大红色长袖卫衣被颠覆性严重脱色错染为灰白死色，身下金黄色实木地板大面积欠饱和严重脱色褪变为冰冷惨白的浅灰白色。"
    },
    8762: {
        "defects": [],
        "review_note": "审查通过"
    },
    8765: {
        "defects": [],
        "review_note": "审查通过"
    },
    8766: {
        "defects": [],
        "review_note": "审查通过"
    },

    # === Sheet 07 ===
    8767: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "卧室白色墙面乳胶漆与铁艺床架大面积浸染失真偏暗的红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "格纹床单红色织物色彩略显过度浓艳。"}
        ],
        "review_note": "卧室白色墙面乳胶漆与铁艺床架大面积浸染失真偏暗的红棕暖偏色，格纹床单红色织物色彩略显过度浓艳。"
    },
    8770: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "沙土地面微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "沙地上行走的非洲小象体表红褐色泥浆与周围沙土地面大面积欠饱和严重脱色褪变为冰冷干瘪的灰白淡色。"}
        ],
        "review_note": "沙地上行走的非洲小象体表红褐色泥浆与周围沙土地面大面积欠饱和严重脱色褪变为冰冷干瘪的灰白淡色。"
    },
    8771: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "周围沙发布艺微染冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "毛绒小熊玩偶原本温暖的米黄色绒毛表面大面积欠饱和脱色发暗。"}
        ],
        "review_note": "毛绒小熊玩偶原本温暖的米黄色绒毛表面大面积欠饱和脱色发暗，周围沙发布艺微染冷青蓝偏色。"
    },
    8772: {
        "defects": [],
        "review_note": "审查通过"
    },
    8774: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "厨房背景墙壁微染冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "烘焙厨房长桌木质台面与背景墙壁大面积欠饱和脱色发暗。"}
        ],
        "review_note": "烘焙厨房长桌木质台面与背景墙壁大面积欠饱和脱色发暗，微染冷青蓝偏色。"
    },
    8775: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "周围茂密树木绿色枝叶被严重错染为发红发紫的枯萎异色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "林间树荫下摆放的木质长椅表面与周围树林大面积浸染失真深重的暗红紫暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错色的暗红树叶与木椅色彩过度浓艳深重。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "林间一片诡异暗红，严重破坏了自然森林生机。"}
        ],
        "review_note": "林间树荫下摆放的木质长椅表面与周围茂密树木枝叶大面积浸染失真深重的暗红紫暖偏色，绿色树叶被严重错染为发红发紫的枯萎异色。"
    },

    # === Sheet 08 ===
    8776: {
        "defects": [
            {"id": "B", "name": "溢色", "severity": "L1", "description": "电脑屏幕发光边缘有轻微色差溢出侵染。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "书房办公桌木质桌面与电脑屏幕边缘大面积浸染失真偏暗的冷青蓝偏色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "桌面冷调与室内自然光线不协调。"}
        ],
        "review_note": "书房办公桌木质桌面与电脑屏幕边缘大面积浸染失真偏暗的冷青蓝偏色，屏幕发光边缘有轻微色差溢出。"
    },
    8779: {
        "defects": [],
        "review_note": "审查通过"
    },
    8780: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "夜景古建筑石墙大面积浸染失真偏暗的冷青蓝偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "外墙悬挂的华尔街与百老汇路标文字色彩过度浓艳刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "荧光路标与冷蓝夜景建筑光照脱节。"}
        ],
        "review_note": "夜景古建筑外墙悬挂的华尔街与百老汇路标文字色彩过度浓艳刺眼，建筑石墙大面积浸染失真偏暗的冷青蓝偏色。"
    },
    8782: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "自助餐厅餐台金属表面微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "餐台上摆放的新鲜切片西瓜与冷盘熟食表面色彩过度浓艳发深。"}
        ],
        "review_note": "自助餐厅餐台上摆放的新鲜切片西瓜与冷盘熟食表面色彩过度浓艳发深，餐台金属表面微染偏深红棕暖偏色。"
    },
    8783: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "厨房料理台上摆放的红色小画框被颠覆性错染为过度浓艳刺眼的荧光深洋红紫色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "操作台大面积浸染失真深重的暗冷青紫偏色与杂色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "画框洋红紫色调与前景食材过度浓艳刺目。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "荧光洋红画框与冷青紫操作台光影混乱失真。"}
        ],
        "review_note": "厨房料理台上摆放的红色小画框被颠覆性错染为过度浓艳刺眼的荧光深洋红紫色，操作台大面积浸染失真深重的暗冷青紫偏色与杂色。"
    },
    8784: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "夜间公园长椅周围地面与古典建筑石墙大面积微染偏深暗红棕暖偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "长椅上坐憩男子服饰与石墙色彩略显欠饱和脱色发暗。"}
        ],
        "review_note": "夜间公园长椅上的坐憩男子服饰与背景古典建筑石墙大面积微染偏深暗红棕暖偏色，且色彩略显欠饱和脱色发暗。"
    },

    # === Sheet 09 ===
    8785: {
        "defects": [],
        "review_note": "审查通过"
    },
    8788: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "工业厨房车间地面与墙面大面积浸染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "工业厨房不锈钢加工设备原本在暖光照耀下的金黄色反光与车间地面大面积欠饱和严重脱色褪变为冰冷灰白淡色。"}
        ],
        "review_note": "工业厨房不锈钢加工设备原本在暖光照耀下的金黄色反光与车间地面大面积欠饱和严重脱色褪变为冰冷灰白淡色，环境微染冷灰偏色。"
    },
    8789: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "机场跑道沥青地面与低空天空大面积浸染失真深重的红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "客机红色尾翼色彩略显过度浓艳。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "跑道与天空整体发红泛黄，环境真实感不足。"}
        ],
        "review_note": "机场跑道沥青地面与低空天空大面积浸染失真深重的红棕暖偏色，客机红色尾翼色彩略显过度浓艳。"
    },
    8790: {
        "defects": [],
        "review_note": "审查通过"
    },
    8792: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "沙发靠背与暗部微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "花斑猫趴卧的花纹布艺沙发毯表面翠绿色底色大面积欠饱和脱色发暗。"}
        ],
        "review_note": "花斑猫趴卧的花纹布艺沙发毯表面翠绿色底色大面积欠饱和脱色发暗，微染冷灰偏色。"
    },
    8793: {
        "defects": [],
        "review_note": "审查通过"
    },

    # === Sheet 10 ===
    8794: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "撑伞画面大面积浸染失真冷青灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "暴雨中撑伞路人脚下湿滑石砖路面原本倒映的金黄色路灯暖光大面积欠饱和严重脱色褪变为冰冷惨白的黑灰死色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "雨夜金黄水光完全消失，水光倒影失去真实立体质感。"}
        ],
        "review_note": "暴雨中撑伞路人脚下湿滑石砖路面原本倒映的金黄色路灯暖光大面积欠饱和严重脱色褪变为冰冷惨白的黑灰死色，画面微染冷青灰偏色。"
    },
    8795: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "木质桌面大面积浸染失真偏暗的冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "摆放掌上游戏机的木质桌面原本温暖醇厚的红棕木色大面积欠饱和严重脱色褪变为冰冷灰白淡色。"}
        ],
        "review_note": "摆放掌上游戏机的木质桌面原本温暖醇厚的红棕木色大面积欠饱和严重脱色褪变为冰冷灰白淡色，大面积浸染失真偏暗的冷青蓝偏色。"
    },
    8797: {
        "defects": [],
        "review_note": "审查通过"
    },
    8800: {
        "defects": [],
        "review_note": "审查通过"
    },
    8801: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "周围木质墙壁与灶台大面积微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "乡村厨房灶台前农妇佩戴的彩色围巾色彩过度浓艳发红。"}
        ],
        "review_note": "乡村厨房灶台前农妇佩戴的彩色围巾色彩过度浓艳发红，周围木质墙壁与灶台大面积微染偏深红棕暖偏色。"
    },
    8802: {
        "defects": [],
        "review_note": "审查通过"
    },

    # === Sheet 11 ===
    8803: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "金黄色香蕉表皮与键盘阴影微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "木质桌面上摆放的红苹果表皮色彩略显过度浓艳偏深。"}
        ],
        "review_note": "木质桌面上摆放的红苹果表皮色彩略显过度浓艳偏深，金黄色香蕉表皮与键盘阴影微染偏深红棕暖偏色。"
    },
    8804: {
        "defects": [],
        "review_note": "审查通过"
    },
    8805: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "木质切菜砧板大面积微染红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "餐台塑料碗中盛放的草莓酸奶色彩过度浓艳刺眼发深荧光粉红。"}
        ],
        "review_note": "餐台塑料碗中盛放的草莓酸奶色彩过度浓艳刺眼发深荧光粉红，木质切菜砧板大面积微染红棕暖偏色。"
    },
    8806: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "奶牛场挤奶女工面部肤色与后方木质牛栏护栏大面积浸染失真偏暗的红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "牛栏木料红棕色彩略显过度浓艳。"}
        ],
        "review_note": "奶牛场挤奶女工面部肤色与后方木质牛栏护栏大面积浸染失真偏暗的红棕暖偏色，色彩略显过度浓艳。"
    },
    8807: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "餐盘边沿与桌面微染冷青色偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "餐盘中摆放的调料蘸酱小碟及炸鸡块表面大面积略显欠饱和脱色发暗。"}
        ],
        "review_note": "餐盘中摆放的调料蘸酱小碟及炸鸡块表面大面积略显欠饱和脱色发暗，微染冷青色偏色。"
    },
    8808: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "室内大面积浸染失真偏暗的冷青蓝偏色，青年面部肤色惨淡发青。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "室内原本温暖明亮的金黄色木门与背景乳胶漆墙面大面积欠饱和严重脱色褪变为冰冷惨白的淡灰白色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "金黄木门与墙面严重脱色褪变，人物面部青冷失真。"}
        ],
        "review_note": "室内原本温暖明亮的金黄色木门与背景乳胶漆墙面大面积欠饱和严重脱色褪变为冰冷惨白的淡灰白色，大面积浸染失真偏暗的冷青蓝偏色。"
    },

    # === Sheet 12 ===
    8809: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "草地上告示牌下方趴卧的原本鲜明暖橙色的橘猫被颠覆性严重脱色错染为冰冷灰蓝色死色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "告示牌周围草坪植被大面积浸染失真冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "橘猫全身暖橙色毛发大面积彻底脱色灰化。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "猫咪颜色彻底颠覆错位，毛发色彩粗糙失真。"}
        ],
        "review_note": "草地上告示牌下方趴卧的原本鲜明暖橙色的橘猫被颠覆性严重脱色错染为冰冷灰蓝色死色，周围草坪植被大面积浸染失真冷青蓝偏色。"
    },
    8811: {
        "defects": [],
        "review_note": "审查通过"
    },
    8812: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "马厩中右侧马匹身上原本鲜艳的粉红色绶带被颠覆性错染为冰冷淡青蓝色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "马厩背景大面积浸染失真深重的冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "左侧骏马原本红润的棕色毛皮大面积欠饱和脱色发暗。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "粉红绶带错涂天蓝且马体脱色，视觉反差生硬。"}
        ],
        "review_note": "马厩中右侧马匹身上原本鲜艳的粉红色绶带被颠覆性错染为冰冷淡青蓝色，左侧骏马原本红润的棕色毛皮大面积欠饱和脱色发暗，微染冷青蓝偏色。"
    },
    8814: {
        "defects": [],
        "review_note": "审查通过"
    },
    8816: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内大理石浴缸台面与窗框大面积微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "落地窗外城市天际线晚霞天空色彩过度浓艳发红橙。"}
        ],
        "review_note": "落地窗外城市天际线晚霞天空色彩过度浓艳发红橙，室内大理石浴缸台面与窗框大面积微染偏深红棕暖偏色。"
    },
    8817: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白瓷餐盘中盛放的黑巧克力蛋糕表面与餐盘边缘大面积微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "巧克力淋面色彩略显过度浓艳。"}
        ],
        "review_note": "白瓷餐盘中盛放的黑巧克力蛋糕表面与餐盘边缘大面积微染偏深红棕暖偏色，巧克力淋面色彩略显过度浓艳。"
    },

    # === Sheet 13 ===
    8818: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "乡村公路沥青路面与天空大面积浸染失真偏暗的冷青蓝偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "公路两侧草坪植被色彩过度浓艳发亮绿。"}
        ],
        "review_note": "乡村公路两侧草坪植被色彩过度浓艳发亮绿，沥青路面与天空大面积浸染失真偏暗的冷青蓝偏色。"
    },
    8819: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "料理台表面大面积微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "厨房整体橱柜木质百叶窗门板与储物柜表面色彩过度浓艳发深。"}
        ],
        "review_note": "厨房整体橱柜木质百叶窗门板与料理台表面色彩过度浓艳发深，大面积微染偏深红棕暖偏色。"
    },
    8820: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "复古红木餐边柜上陈列的原本鲜艳纯正的三个宝蓝色装饰陶瓷花瓶被颠覆性严重脱色错染为土灰白死色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "背景墙面与地面微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "三个宝蓝陶瓷花瓶原本明丽的孔雀蓝色彩大面积彻底脱色灰化。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "鲜亮宝蓝花瓶变灰土色，室内陈设质感极为粗糙。"}
        ],
        "review_note": "复古红木餐边柜上陈列的原本鲜艳纯正的三个宝蓝色装饰陶瓷花瓶被颠覆性严重脱色错染为土灰白死色，餐边柜实木表面大面积欠饱和脱色发暗。"
    },
    8822: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "母子面部肤色微染冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "餐厅餐桌前母亲身穿的深紫色背心大面积欠饱和严重脱色褪变为发暗冷灰色。"}
        ],
        "review_note": "餐厅餐桌前母亲身穿的深紫色背心大面积欠饱和严重脱色褪变为发暗冷灰色，母子面部肤色微染冷青蓝偏色。"
    },
    8823: {
        "defects": [],
        "review_note": "审查通过"
    },
    8824: {
        "defects": [],
        "review_note": "审查通过"
    },

    # === Sheet 14 ===
    8825: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "披萨店长条木质餐台表面大面积浸染失真深重的冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "烘烤披萨芝士表面色彩欠饱和脱色发暗。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "实木餐台深重偏冷青蓝完全破坏了烘焙店的温暖氛围。"}
        ],
        "review_note": "披萨店长条木质餐台表面大面积浸染失真深重的冷青蓝偏色，烘烤披萨芝士表面色彩欠饱和脱色发暗。"
    },
    8826: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "女孩面部肤色与书桌微染冷灰偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "书桌前右侧女孩身穿的绿色针织衫织物色彩略显过度浓艳发深。"}
        ],
        "review_note": "书桌前右侧女孩身穿的绿色针织衫织物色彩略显过度浓艳发深，女孩面部肤色微染冷灰偏色。"
    },
    8828: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "背景灌木树林微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "草地上行走的成年长颈鹿身体红棕色斑纹色彩大面积略显欠饱和脱色发暗。"}
        ],
        "review_note": "草地上行走的成年长颈鹿身体红棕色斑纹色彩大面积略显欠饱和脱色发暗，背景灌木树林微染冷灰偏色。"
    },
    8829: {
        "defects": [],
        "review_note": "审查通过"
    },
    8831: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "卫生间墙壁上方两块正方形灯箱原本散发的深邃冰蓝色荧光被颠覆性严重脱色错染为惨白灰光。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "洗手台周围墙面微染冷灰暗色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "洗手台大理石台面大面积欠饱和严重脱色褪变为黑灰死色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "冷艳荧光完全消失，暗光氛围单薄苍白。"}
        ],
        "review_note": "卫生间墙壁上方两块正方形灯箱原本散发的深邃冰蓝色荧光被颠覆性严重脱色错染为惨白灰光，洗手台大理石台面大面积欠饱和严重脱色褪变为黑灰死色。"
    },
    8834: {
        "defects": [],
        "review_note": "审查通过"
    },

    # === Sheet 15 ===
    8838: {
        "defects": [],
        "review_note": "审查通过"
    },
    8839: {
        "defects": [],
        "review_note": "审查通过"
    },
    8840: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "糕点暗部微染冷青灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "红色礼盒内装放的烘焙蛋挞与甜点表面金黄麦香色泽大面积欠饱和脱色发暗。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "烘焙蛋挞脱色变灰，失去食物诱人光泽。"}
        ],
        "review_note": "红色礼盒内装放的烘焙蛋挞与甜点表面金黄麦香色泽大面积欠饱和脱色发暗，微染冷青灰偏色。"
    },
    8841: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "挑高木屋客厅人字形木质屋顶横梁与实木地板大面积浸染失真偏暗的红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "屋顶木材暖红色彩略显过度浓艳。"}
        ],
        "review_note": "挑高木屋客厅人字形木质屋顶横梁与实木地板大面积浸染失真偏暗的红棕暖偏色，色彩略显过度浓艳。"
    },
    8844: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "放飞风筝的户外公园原本葱郁青翠的树林枝叶与草地被颠覆性错染为枯萎浑浊的黄灰异色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "草地与树木大面积浸染失真深重的暗冷青紫偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "草坪与树林大面积欠饱和严重脱色褪变。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "青翠草地完全变为枯黄冷紫异色，视觉严重违和。"}
        ],
        "review_note": "放飞风筝的户外公园原本葱郁青翠的树林枝叶与草地被颠覆性错染为枯萎浑浊的黄灰异色，大面积欠饱和严重脱色褪变，微染冷青紫偏色。"
    },
    8846: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "背景竹林与地面微染冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "动物园黑熊展区后方原本苍翠生机的竹林与树木枝叶大面积欠饱和脱色发暗。"}
        ],
        "review_note": "动物园黑熊展区后方原本苍翠生机的竹林与树木枝叶大面积欠饱和脱色发暗，微染冷青蓝偏色。"
    },

    # === Sheet 16 ===
    8848: {
        "defects": [],
        "review_note": "审查通过"
    },
    8849: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "金属齿轮与铁架微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "废弃工业机械生锈的转轮与铁架表面红褐色铁锈大面积欠饱和脱色发暗。"}
        ],
        "review_note": "废弃工业机械生锈的转轮与铁架表面红褐色铁锈大面积欠饱和脱色发暗，微染冷灰偏色。"
    },
    8853: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "金属立柱与周围草丛微染冷灰青偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街道路口红色八角形停止交通标牌表面纯正大红色底漆大面积欠饱和严重脱色褪变为暗淡灰暗的浅粉白色。"}
        ],
        "review_note": "街道路口红色八角形停止交通标牌表面纯正大红色底漆大面积欠饱和严重脱色褪变为暗淡灰暗的浅粉白色。"
    },
    8854: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "后方观众看台大面积浸染失真偏暗的冷青蓝偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "棒球场草坪塑胶植被色彩过度浓艳发荧光黄绿。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "荧光绿草坪与冷蓝看台反差刺眼失真。"}
        ],
        "review_note": "棒球场草坪塑胶植被色彩过度浓艳发荧光黄绿，后方观众看台大面积浸染失真偏暗的冷青蓝偏色。"
    },
    8856: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "沙滩上海浪冲刷的木质渔船船体与沙滩地表大面积浸染失真偏暗的红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "沙滩石子与渔船红棕色调色彩略显过度浓艳。"}
        ],
        "review_note": "沙滩上海浪冲刷的木质渔船船体与沙滩地表大面积浸染失真偏暗的红棕暖偏色，色彩略显过度浓艳。"
    },
    8859: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "火车站台上停靠的复古客运列车绿色车厢表面与蒸汽机车车头大面积微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "车体墨绿色彩略显过度浓艳。"}
        ],
        "review_note": "火车站台上停靠的复古客运列车绿色车厢表面与蒸汽机车车头大面积微染偏深红棕暖偏色，车体墨绿色彩略显过度浓艳。"
    },

    # === Sheet 17 ===
    8861: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "开放式厨房整体橱柜面板与吊顶在灯光照耀下大面积微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "橱柜木纹局部反光色彩略显过度浓艳。"}
        ],
        "review_note": "开放式厨房整体橱柜面板与吊顶在灯光照耀下大面积微染偏深红棕暖偏色，局部反光色彩略显过度浓艳。"
    },
    8863: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "黑狗趴卧的房间实木地面大面积浸染失真偏暗的冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "黑狗趴卧的实木地板原本温暖醇厚的红棕色大面积欠饱和严重脱色褪变为冰冷灰白淡色。"}
        ],
        "review_note": "黑狗趴卧的实木地板原本温暖醇厚的红棕色大面积欠饱和严重脱色褪变为冰冷灰白淡色，大面积浸染失真偏暗的冷青蓝偏色。"
    },
    8865: {
        "defects": [],
        "review_note": "审查通过"
    },
    8866: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "浴室镜前壁灯光晕与大理石台面微染冷青灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "双台盆浴室梳妆镜后方原本温馨柔和的米黄色乳胶漆墙面大面积欠饱和脱色偏冷灰。"}
        ],
        "review_note": "双台盆浴室梳妆镜后方原本温馨柔和的米黄色乳胶漆墙面大面积欠饱和脱色偏冷灰，微染冷青灰偏色。"
    },
    8867: {
        "defects": [],
        "review_note": "审查通过"
    },
    8868: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "男士西装胸前佩戴的橙白斜条纹真丝领带表面大面积微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "领带橙色条纹色彩略显过度浓艳。"}
        ],
        "review_note": "男士西装胸前佩戴的橙白斜条纹真丝领带表面大面积微染偏深红棕暖偏色，橙色条纹色彩略显过度浓艳。"
    },

    # === Sheet 18 ===
    8869: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "炸鸡块与餐盘表面大面积微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "餐盘中摆放的小胡萝卜条表面橙红色彩过度浓艳刺眼。"}
        ],
        "review_note": "餐盘中摆放的小胡萝卜条表面橙红色彩过度浓艳刺眼，炸鸡块与餐盘表面大面积微染偏深红棕暖偏色。"
    },
    8874: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "飞盘运动员脚下开阔的草坪植被大面积浸染失真偏暗的冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "草坪色彩略显欠饱和脱色发暗。"}
        ],
        "review_note": "飞盘运动员脚下开阔的草坪植被大面积浸染失真偏暗的冷青蓝偏色，草坪色彩略显欠饱和脱色发暗。"
    },
    8876: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "新郎身穿的西装白衬衫与背景建筑石柱大面积浸染失真深重的冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "室内原本温馨的暖黄光影完全被破坏，画面泛冷发灰。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "新郎西服与背景光影冷蓝偏色失真严重。"}
        ],
        "review_note": "新郎身穿的西装白衬衫与背景建筑石柱大面积浸染失真深重的冷青蓝偏色，室内原本温馨的暖黄光影完全被破坏。"
    },
    8877: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "浅滩河水中飞溅的水花与河面大面积微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "水流落日反光色彩略显过度浓艳。"}
        ],
        "review_note": "浅滩河水中飞溅的水花与河面大面积微染偏深红棕暖偏色，水流反光色彩略显过度浓艳。"
    },
    8878: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "宠物犬依偎的折叠床布艺表面与主人手臂肤色大面积微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "手臂肤色与布面色彩略显过度浓艳发红。"}
        ],
        "review_note": "宠物犬依偎的折叠床布艺表面与主人手臂肤色大面积微染偏深红棕暖偏色，色彩略显过度浓艳。"
    },
    8882: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "背景砖墙与地面大面积浸染失真偏暗的冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "木桩花瓶后方原本翠绿生机的草坪植被大面积欠饱和严重脱色褪变为冰冷灰白淡色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "背景草坪青绿完全丧失，空间层次脱节。"}
        ],
        "review_note": "木桩花瓶后方原本翠绿生机的草坪植被大面积欠饱和严重脱色褪变为冰冷灰白淡色，大面积浸染失真偏暗的冷青蓝偏色。"
    },

    # === Sheet 19 ===
    8885: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "餐厅外墙悬挂的时钟上方墙面被颠覆性错染为深洋红紫色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "霓虹招牌字母与石墙大面积浸染失真红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错色的洋红墙面与霓虹文字色彩过度浓艳刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "洋红大色斑在深色砖墙上异常突兀违和。"}
        ],
        "review_note": "餐厅外墙悬挂的时钟上方墙面被颠覆性错染为深洋红紫色，霓虹招牌字母与石墙大面积浸染失真红棕暖偏色，色彩过度浓艳。"
    },
    8886: {
        "defects": [],
        "review_note": "审查通过"
    },
    8887: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "沥青路面与车底暗部微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "街头行驶的双层巴士绿色车漆色彩过度浓艳发亮绿。"}
        ],
        "review_note": "街头行驶的双层巴士绿色车漆色彩过度浓艳发亮绿，沥青路面与车底暗部微染偏深红棕暖偏色。"
    },
    8888: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "芦苇枯枝暗部微染冷青灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "水塘边水鸟身旁的水面大面积欠饱和脱色发暗。"}
        ],
        "review_note": "水塘边水鸟身旁的水面大面积欠饱和脱色发暗，微染冷青灰偏色。"
    },
    8889: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "餐盘与桌面微染冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "早餐餐桌瓷盘中摆放的草莓派表面草莓淋酱原本鲜艳的红色大面积欠饱和严重脱色褪变为干瘪灰黑死色。"}
        ],
        "review_note": "早餐餐桌瓷盘中摆放的草莓派表面草莓淋酱原本鲜艳的红色大面积欠饱和严重脱色褪变为干瘪灰黑死色，餐盘与桌面微染冷青蓝偏色。"
    },
    8892: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "草地上少年伸手拿取的黄色飞盘被颠覆性错染为淡冷青色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "周围草坪微染冷青色偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "红色飞盘与周围草坪略显欠饱和脱色发暗。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "飞盘错色生硬，与运动场景氛围不搭。"}
        ],
        "review_note": "草地上少年伸手拿取的黄色飞盘被颠覆性错染为淡冷青色，红色飞盘与周围草坪略显欠饱和脱色发暗，微染冷青色偏色。"
    },

    # === Sheet 20 ===
    8893: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "周围草地略显欠饱和脱色发暗，微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "复古甲壳虫轿车后方原本鲜艳夺目的紫红色野花丛大面积欠饱和严重脱色褪变为冰冷灰白淡色。"}
        ],
        "review_note": "复古甲壳虫轿车后方原本鲜艳夺目的紫红色野花丛大面积欠饱和严重脱色褪变为冰冷灰白淡色，周围草地略显欠饱和脱色发暗。"
    },
    8895: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "复古卧室内墙面花纹壁纸大面积欠饱和脱色偏冷青灰。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "婴儿床上红色布艺织物色彩略显发暗脱色。"}
        ],
        "review_note": "复古卧室内墙面花纹壁纸大面积欠饱和脱色偏冷青灰，婴儿床上红色布艺织物色彩略显发暗。"
    },
    8896: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "猫咪背毛微染冷青灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "猫咪上方遮阳伞原本鲜艳纯正的明黄色条纹布料大面积欠饱和脱色发暗。"}
        ],
        "review_note": "猫咪上方遮阳伞原本鲜艳纯正的明黄色条纹布料大面积欠饱和脱色发暗，微染冷青灰偏色。"
    },
    8897: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "角色扮演少女身后的背景墙面被颠覆性错染为深洋红粉紫色伪色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "少女发丝与服饰边缘微染深洋红暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "少女身前披萨与绿色假发色彩过度浓艳刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "背景大面积恶性洋红紫伪色，画面色彩失真。"}
        ],
        "review_note": "角色扮演少女身后的背景墙面被颠覆性错染为深洋红粉紫色伪色，少女身前披萨与绿色假发色彩过度浓艳刺眼。"
    },
    8898: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "餐盘中摆放的汉堡面包胚切面与火腿切片大面积微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "面包表皮烘烤焦糖色彩略显过度浓艳。"}
        ],
        "review_note": "餐盘中摆放的汉堡面包胚切面与火腿切片大面积微染偏深红棕暖偏色，面包表皮色彩略显过度浓艳。"
    },
    8901: {
        "defects": [],
        "review_note": "审查通过"
    }
}


def main():
    grounding_path = "LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_44.json"
    with open(grounding_path, "w", encoding="utf-8") as f:
        json.dump(BATCH_44_REVIEWS, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(BATCH_44_REVIEWS)} reviews to {grounding_path}")

    all_path = "LS_lcad_reviewer/exports/reviewed_1_10000_all.json"
    clean_path = "LS_lcad_reviewer/exports/reviewed_1_10000_clean.json"

    with open(all_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    with open(clean_path, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    pass_count = 0
    revised_count = 0
    meltdown_count = 0

    for t_id, rev in BATCH_44_REVIEWS.items():
        idx = t_id - 1
        rec_all = all_data["annotations"][idx]
        rec_clean = clean_data["annotations"][idx]

        is_pass = len(rev["defects"]) == 0
        if is_pass:
            pass_count += 1
        else:
            revised_count += 1

        rec_all["defects"] = rev["defects"]
        rec_all["review_note"] = rev["review_note"]
        rec_all["review_status"] = "已核验"

        rec_clean["defects"] = rev["defects"]
        rec_clean["review_note"] = ""
        rec_clean["review_status"] = "已核验"

        is_meltdown = any(d.get("id") == "A" for d in rev["defects"])
        if is_meltdown:
            meltdown_count += 1
            rec_all["reviewed_score"] = 1.0
            rec_all["needs_rescoring"] = False
            rec_clean["reviewed_score"] = 1.0
            rec_clean["needs_rescoring"] = False
        else:
            rec_all["reviewed_score"] = None
            rec_all["needs_rescoring"] = True
            rec_clean["reviewed_score"] = None
            rec_clean["needs_rescoring"] = True

    with open(all_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)

    print(f"Batch 44 applied successfully!")
    print(f"Total: {len(BATCH_44_REVIEWS)}, Passes: {pass_count} ({pass_count/len(BATCH_44_REVIEWS)*100:.2f}%), Revised: {revised_count} ({revised_count/len(BATCH_44_REVIEWS)*100:.2f}%), Meltdown A: {meltdown_count}")

if __name__ == "__main__":
    main()
