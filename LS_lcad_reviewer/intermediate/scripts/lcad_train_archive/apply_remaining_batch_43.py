# -*- coding: utf-8 -*-
"""
Batch 43 review data dictionary and application script.
Tasks: #8525 to #8714 (120 tasks)
"""
import json
import os

BATCH_43_REVIEWS = {
    # === Sheet 01 ===
    8525: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "路边停放的摩托车与轻便踏板车车体金属暗部与沥青地面大面积微染深暗红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "摩托车红色金属外壳漆面与坐垫边缘色彩过度浓艳刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "车体漆面浓艳反光与地面暗红阴影衔接生硬失真。"}
        ],
        "review_note": "路边停放的摩托车红色金属外壳漆面色彩过度浓艳刺眼，车体金属暗部与沥青地面微染深暗红棕暖偏色。"
    },
    8526: {
        "defects": [],
        "review_note": "审查通过"
    },
    8527: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "沥青小路路面阴影微染冷青色偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "沥青小路两侧草坪植被大面积欠饱和脱色偏黄灰暗淡。"}
        ],
        "review_note": "沥青小路两侧草坪植被大面积欠饱和脱色偏黄灰暗淡，路面阴影微染冷青色偏色。"
    },
    8529: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "室内木门前女子身穿的灰绿色短袖T恤被颠覆性严重错涂为深红棕色与暗红色异色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内木质门框与背景白墙大面积浸染失真深重的红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "女子胸前错涂的深红衣物织物色彩略显过度浓艳。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "严重错色的衣物与室内环境光照脱节，视觉违和感显著。"}
        ],
        "review_note": "室内木门前女子身穿的灰绿色短袖T恤被颠覆性严重错涂为深红棕色与暗红色异色，室内木质门框大面积浸染红棕暖偏色。"
    },
    8530: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "旷野草地微染偏暗冷青偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "旷野草地上的青草植被大面积欠饱和严重脱色褪变为暗淡干瘪的灰黄死色。"}
        ],
        "review_note": "旷野草地上的青草植被大面积欠饱和严重脱色褪变为暗淡干瘪的灰黄死色。"
    },
    8531: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "骑手外套与道路阴影微染冷青灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "滨海栈道旁观光人力车的遮阳顶棚与骑手身穿的运动外套大面积欠饱和脱色偏暗灰冷色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "人力车与衣物灰冷脱色导致整体层次单薄发灰。"}
        ],
        "review_note": "滨海栈道旁观光人力车的遮阳顶棚与骑手身穿的运动外套大面积欠饱和脱色偏暗灰冷色。"
    },

    # === Sheet 02 ===
    8533: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "餐厅餐桌上盛放热饮的陶瓷杯被颠覆性错染为深冷青蓝色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "就餐女士身穿的针织毛衣与面部阴影大面积浸染失真深重的暗红紫暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "餐桌杯具青蓝色调与女士毛衣深红色彩略显过度浓艳。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "冷蓝陶瓷杯与暖红女士衣物光影色温割裂，视觉违和。"}
        ],
        "review_note": "餐厅餐桌上盛放热饮的陶瓷杯被颠覆性错染为深冷青蓝色，就餐女士身穿的毛衣大面积浸染暗红紫暖偏色。"
    },
    8534: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "夜景隧道口周围沥青路面与水泥墙壁大面积浸染失真偏暗的红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "红色八角形停止交通标牌表面色彩过度浓艳偏深。"}
        ],
        "review_note": "夜景隧道口的红色八角形停止交通标牌表面色彩过度浓艳偏深，周围沥青路面与水泥墙壁大面积浸染失真偏暗的红棕暖偏色。"
    },
    8535: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "宴会厅壁纸背景微染冷灰青偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "宴会厅餐桌后方的复古欧式花纹壁纸与老人身穿的针织衫大面积欠饱和脱色偏暗灰冷色。"}
        ],
        "review_note": "宴会厅餐桌后方的复古欧式花纹壁纸与老人身穿的针织衫大面积欠饱和脱色偏暗灰冷色。"
    },
    8536: {
        "defects": [],
        "review_note": "审查通过"
    },
    8537: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "画框陈列的风景画中原本晴朗清澈的淡蓝色天空被颠覆性严重错涂为诡异妖艳的淡粉红与粉紫晚霞异色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "画作远景山峦与墙壁画框大面积浸染失真深重的粉紫暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "错涂的天空粉红晚霞色彩过度浓艳刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "原本宁静的蓝天风景画变为诡异粉紫，视觉真实感遭到严重破坏。"}
        ],
        "review_note": "画框陈列的风景画中原本晴朗清澈的淡蓝色天空被颠覆性严重错涂为诡异妖艳的淡粉红与粉紫晚霞异色。"
    },
    8539: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "吧台工作区阴影微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "吧台前青年身穿的印花短袖T恤与塑料量杯表面大面积欠饱和脱色偏冷灰发暗。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "吧台用具脱色发暗，画面缺乏清爽明快感。"}
        ],
        "review_note": "吧台前青年身穿的印花短袖T恤与塑料量杯表面大面积欠饱和脱色偏冷灰发暗。"
    },

    # === Sheet 03 ===
    8540: {
        "defects": [],
        "review_note": "审查通过"
    },
    8544: {
        "defects": [
            {"id": "B", "name": "溢色", "severity": "L2", "description": "蛋糕表面浓艳的青蓝糖霜严重溢色浸染周围白色奶油与金属托盘。"},
            {"id": "C", "name": "错色", "severity": "L3", "description": "托盘中摆放的奶油蛋糕表面原本淡雅的马卡龙与糖霜被颠覆性严重错涂为深红与亮青蓝伪色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "托盘金属反光与周围餐桌大面积浸染失真冷青蓝偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L3", "description": "蛋糕表面错涂的荧光青蓝与深红糖霜色彩极度浓艳刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "甜点表面恶性荧光伪色与溢色严重违背食品常理，视觉极为违和。"}
        ],
        "review_note": "托盘中摆放的奶油蛋糕表面原本淡雅的马卡龙与糖霜被颠覆性严重错涂为过度浓艳刺眼的荧光深红与亮青蓝伪色，且伴随明显溢色。"
    },
    8547: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "黄昏落日下的公路沥青路面大面积浸染失真偏暗的红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "落日天空与路面晚霞反光色彩略显过度浓艳。"}
        ],
        "review_note": "黄昏落日下的公路沥青路面大面积浸染失真偏暗的红棕暖偏色，天空晚霞反光略显过度浓艳。"
    },
    8548: {
        "defects": [],
        "review_note": "审查通过"
    },
    8549: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "篝火旁竹签上插着的棉花糖原本米白色的松软表皮被颠覆性错染为深暗焦红褐色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "周围草地与人物手部大面积浸染失真深重的暗红暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "棉花糖焦红褐色表皮色彩过度浓艳刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "棉花糖错色焦黑浓艳，破坏了烘烤食物的松软质感。"}
        ],
        "review_note": "篝火旁竹签上插着的棉花糖原本米白色的松软表皮被颠覆性错染为深暗焦红褐色，周围草地大面积浸染暗红暖偏色。"
    },
    8552: {
        "defects": [],
        "review_note": "审查通过"
    },

    # === Sheet 04 ===
    8553: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "机车后方原本淡雅的浅黄砖石建筑外墙被大面积严重错涂为亮红色红砖墙。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "机车金属反光与地面大面积浸染失真红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "错涂的砖石外墙红色色调过度浓艳刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "建筑红砖错色突兀生硬，与街景整体氛围不符。"}
        ],
        "review_note": "机车后方原本淡雅的浅黄砖石建筑外墙被大面积严重错涂为过度浓艳刺眼的亮红色红砖墙。"
    },
    8555: {
        "defects": [],
        "review_note": "审查通过"
    },
    8556: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "看台座椅表面与前方观众发丝阴影大面积微染红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "棒球场内场红土地面色彩过度浓艳偏深。"}
        ],
        "review_note": "棒球场内场红土地面色彩过度浓艳偏深，看台座椅表面与前方观众发丝阴影大面积微染红棕暖偏色。"
    },
    8557: {
        "defects": [],
        "review_note": "审查通过"
    },
    8558: {
        "defects": [],
        "review_note": "审查通过"
    },
    8559: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "女士面部阴影与背景建筑微染红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "街头合影右侧女士身穿的红色防风外套织物色彩略显过度浓艳刺眼。"}
        ],
        "review_note": "街头合影右侧女士身穿的红色防风外套织物色彩略显过度浓艳刺眼。"
    },

    # === Sheet 05 ===
    8560: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "地面瓷砖反光与塑料袋阴影微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "黑白猫爪旁的透明塑料袋内部食材大面积浸染过度浓艳刺眼的深红偏色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "袋装食材浓艳发红与透明塑料包装反光脱节。"}
        ],
        "review_note": "黑白猫爪旁的透明塑料袋内部食材大面积浸染过度浓艳刺眼的深红偏色。"
    },
    8561: {
        "defects": [],
        "review_note": "审查通过"
    },
    8562: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "展厅地面与展品阴影大面积浸染失真偏暗的冷灰青偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "展厅过道陈列的双门立式大冰箱与左侧宣传墙面大面积欠饱和严重脱色褪变为冰冷灰白淡灰色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "展厅陈列原本明亮的装饰色严重褪色失真，空间呆滞苍白。"}
        ],
        "review_note": "展厅过道陈列的双门立式大冰箱与左侧宣传墙面大面积欠饱和严重脱色褪变为冰冷灰白淡灰色。"
    },
    8564: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "雪山地表与天空大面积浸染失真偏暗的冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "雪坡上滑雪者投射的逆光阴影与雪山地表大面积欠饱和脱色偏暗灰冷青色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "雪山冷青色调偏暗失真，视觉质感偏硬。"}
        ],
        "review_note": "雪坡上滑雪者投射的逆光阴影与雪山地表大面积欠饱和脱色偏暗灰冷青色。"
    },
    8569: {
        "defects": [],
        "review_note": "审查通过"
    },
    8570: {
        "defects": [],
        "review_note": "审查通过"
    },

    # === Sheet 06 ===
    8571: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "餐桌上摆放的生鱼片拼盘与调料瓶表面微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "三文鱼生鱼片肉质纹理色彩略显过度浓艳偏深。"}
        ],
        "review_note": "餐桌上摆放的生鱼片拼盘与调料瓶表面微染偏深红棕暖偏色，刺身色彩略显过度浓艳。"
    },
    8574: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "林间落叶地面微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "林间小路上铺满的秋季落叶与两旁树干表面大面积欠饱和脱色偏暗灰冷色。"}
        ],
        "review_note": "林间小路上铺满的秋季落叶与两旁树干表面大面积欠饱和脱色偏暗灰冷色。"
    },
    8576: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "羊圈栅栏木料表面微染偏暗冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "农场羊圈内的干草饲料堆与成年母羊原本温暖米黄的羊毛大面积欠饱和严重脱色褪变为冰冷灰白死色。"}
        ],
        "review_note": "农场羊圈内的干草饲料堆与成年母羊原本温暖米黄的羊毛大面积欠饱和严重脱色褪变为冰冷灰白死色。"
    },
    8579: {
        "defects": [],
        "review_note": "审查通过"
    },
    8580: {
        "defects": [],
        "review_note": "审查通过"
    },
    8581: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "林间溪流旁的茂密树林灌木叶片与草地大面积浸染失真偏暗的冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "溪流两旁草坪青草色彩欠饱和脱色发暗。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "树林青蓝冷调与林间自然生机脱节。"}
        ],
        "review_note": "林间溪流旁的茂密树林灌木叶片与草地大面积浸染失真偏暗的冷青蓝偏色。"
    },

    # === Sheet 07 ===
    8582: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "聚会餐桌前儿童佩戴的搞怪假发头饰与桌上披萨表面大面积浸染过度浓艳刺眼的荧光深洋红紫偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "儿童假发与背景装饰织物色彩极度浓艳刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "整片洋红紫伪色严重失真，破坏了聚会室内正常光影。"}
        ],
        "review_note": "聚会餐桌前儿童佩戴的搞怪假发头饰与桌上披萨表面大面积浸染过度浓艳刺眼的荧光深洋红紫偏色。"
    },
    8583: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "大象鞍毯阴影与地面砂石大面积微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "古建筑前行进的大象背部披挂的刺绣华丽鞍毯及遮阳伞红色织物色彩过度浓艳。"}
        ],
        "review_note": "古建筑前行进的大象背部披挂的刺绣华丽鞍毯及遮阳伞红色织物色彩过度浓艳。"
    },
    8584: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "滑板场水泥斜坡平台地表大面积浸染失真偏暗的暗黄褐偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "滑板平台斜坡水泥表面色彩略显欠饱和脱色发暗。"}
        ],
        "review_note": "滑板场水泥斜坡平台地表大面积浸染失真偏暗的暗黄褐偏色。"
    },
    8585: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "街头合影右侧男士身穿的红黑格子衬衫原本鲜艳的红色条纹错退为暗淡灰白死色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "街道背景墙面与路人面部微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "格子衬衫红色条纹织物大面积欠饱和严重脱色褪变为发暗灰白色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "衬衫红色条纹完全褪色使衣物图案残缺失真。"}
        ],
        "review_note": "街头合影右侧男士身穿的红黑格子衬衫原本鲜艳的红色条纹大面积欠饱和严重脱色褪变为发暗灰白色。"
    },
    8586: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "雨天步行街上行人身穿的原本深蓝色的防雨外套被颠覆性严重错涂为过度浓艳刺眼的亮大红色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "湿滑路面反光与雨伞大面积浸染暗红暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错涂的大红色外套织物色彩极度浓艳刺目。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "暴雨阴冷环境下的突兀刺眼大红大面积错涂违背自然观感。"}
        ],
        "review_note": "雨天步行街上行人身穿的原本深蓝色的防雨外套被颠覆性严重错涂为过度浓艳刺眼的亮大红色。"
    },
    8587: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "婚礼宴会厅多层翻糖婚礼蛋糕表面装饰的糖霜花卉被错染为浑浊发暗的冷青蓝杂色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "背景布幔与宴会餐桌大面积浸染失真深重的暗冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "翻糖蛋糕洁白奶油与花卉大面积脱色发灰。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "婚礼蛋糕出现大面积冷青色斑块，严重破坏神圣喜庆氛围。"}
        ],
        "review_note": "婚礼宴会厅多层翻糖婚礼蛋糕表面装饰的糖霜花卉与背景布幔大面积浸染失真深重的暗冷青蓝偏色与杂色。"
    },

    # === Sheet 08 ===
    8588: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "酒吧吧台木质台面与酒架大面积微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "酒吧吧台放置的红色塑料冰桶与葡萄酒瓶标签表面色彩略显过度浓艳。"}
        ],
        "review_note": "酒吧吧台放置的红色塑料冰桶与葡萄酒瓶标签表面色彩略显过度浓艳，吧台微染偏深红棕暖偏色。"
    },
    8590: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "卫生间瓷砖地面阴影微染冷青灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "卫生间白色陶瓷马桶座圈与水箱釉面色彩略显欠饱和脱色偏冷灰。"}
        ],
        "review_note": "卫生间白色陶瓷马桶座圈与水箱釉面色彩略显欠饱和脱色偏冷灰。"
    },
    8591: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "酒店客房床头背景墙原本清爽典雅的橄榄绿色涂装错涂为发暗灰褐色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "客房床铺与木地板微染偏暗冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "床头背景墙原本鲜艳的绿色调大面积欠饱和严重脱色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "背景墙错色灰暗破坏了客房清新整洁感。"}
        ],
        "review_note": "酒店客房床头背景墙原本清爽典雅的橄榄绿色涂装大面积欠饱和严重脱色错涂为发暗灰褐色。"
    },
    8592: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "展馆内墙面绘制的草原壁画中原本蔚蓝的天空与远山背景错染为浑浊发暗的黄灰杂色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "展厅墙面与地毯大面积浸染失真暗黄灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "壁画中草原天空与远景大面积欠饱和脱色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "自然风光壁画大面积错色泛黄泛灰，失去生机。"}
        ],
        "review_note": "展馆内墙面绘制的草原壁画中原本蔚蓝的天空与远山背景大面积欠饱和脱色错染为浑浊发暗的黄灰杂色。"
    },
    8593: {
        "defects": [],
        "review_note": "审查通过"
    },
    8594: {
        "defects": [],
        "review_note": "审查通过"
    },

    # === Sheet 09 ===
    8595: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "雪道雪面微染冷灰淡青偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "单板滑雪选手身穿的亮绿色防风夹克及平衡滑杠表面的红色贴花大面积欠饱和严重脱色褪变为灰白暗淡色。"}
        ],
        "review_note": "单板滑雪选手身穿的亮绿色防风夹克及平衡滑杠表面的红色贴花大面积欠饱和严重脱色褪变为灰白暗淡色。"
    },
    8596: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "度假酒店客房大床上铺设的原本喜庆纯正的大红色丝绸床单被颠覆性严重脱色错染为暗淡死沉的深灰棕色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "客房床头软包与木质床架大面积浸染暗冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "大红色床单原本浓郁的大红色彩大面积彻底脱色丧失所有彩色信息。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "床单色彩彻底颠覆错位，客房视觉质感极为粗糙。"}
        ],
        "review_note": "度假酒店客房大床上铺设的原本喜庆纯正的大红色丝绸床单被颠覆性严重脱色错染为暗淡死沉的深灰棕色。"
    },
    8599: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "背景虚化枝叶微染偏深红黄偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "空中展翅飞翔的鹦鹉胸腹及翅膀羽毛黄色与绿色色彩略显过度浓艳。"}
        ],
        "review_note": "空中展翅飞翔的鹦鹉胸腹及翅膀羽毛黄色与绿色色彩略显过度浓艳。"
    },
    8600: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "小象嬉水池周围标志性的红土地表与红泥水体原本鲜明的红棕色被颠覆性严重脱色错涂为浑浊暗淡的灰泥冷灰色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "小象体表泥浆与周围土坡大面积浸染失真暗冷青灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "红土高原特有的红泥地表大面积欠饱和严重脱色褪变为干瘪冷灰色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "标志性红土泥浆变灰，完全违背原图真实地理特征与环境氛围。"}
        ],
        "review_note": "小象嬉水池周围标志性的红土地表与红泥水体原本鲜明的红棕色被颠覆性严重脱色错涂为浑浊暗淡的灰泥冷灰色。"
    },
    8601: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "微缩火车铁道模型沙盘的山体地面与铁轨碎石大面积浸染失真深重的暗冷青蓝偏色与杂色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "沙盘模型植被与建筑物表面大面积欠饱和脱色偏暗灰。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "沙盘山体覆盖严重失真的青蓝冷色杂斑，视觉生硬粗糙。"}
        ],
        "review_note": "微缩火车铁道模型沙盘的山体地面与铁轨碎石大面积浸染失真深重的暗冷青蓝偏色与杂色。"
    },
    8603: {
        "defects": [
            {"id": "A", "name": "缺色", "severity": "", "description": "夜景路灯下停靠的老爷车轿车、周围道路与后方停放的白色厢式货车全域上色失败彻底退化为黑白灰阶图像，全图严重缺色丧失所有彩色信息。"}
        ],
        "review_note": "夜景路灯下停靠的老爷车轿车、周围道路与后方白色厢式货车全域上色失败彻底退化为黑白灰阶图像，命中A熔断项。",
        "reviewed_score": 1.0,
        "needs_rescoring": False
    },

    # === Sheet 10 ===
    8604: {
        "defects": [],
        "review_note": "审查通过"
    },
    8605: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "木桌上方放置的深蓝色陶瓷插花瓶外壁大面积浸染失真偏暗的红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "陶瓷花瓶外壁釉面暗红反光色彩略显过度浓艳。"}
        ],
        "review_note": "木桌上方放置的深蓝色陶瓷插花瓶外壁大面积浸染失真偏暗的红棕暖偏色。"
    },
    8606: {
        "defects": [],
        "review_note": "审查通过"
    },
    8609: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "办公室桌面与背景墙壁阴影微染冷黄灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "办公室工位隔板与背景墙面告示白纸色彩略显欠饱和脱色偏暗灰淡黄。"}
        ],
        "review_note": "办公室工位隔板与背景墙面告示白纸色彩略显欠饱和脱色偏暗灰淡黄。"
    },
    8611: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "机房木质工作台桌面与后方实木隔断墙壁大面积浸染失真深重的暗红橙暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "木质桌面与实木墙面红橙色彩过度浓艳深重。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "工作台桌面深重红橙暖偏色导致反光异常刺眼，视觉不协调。"}
        ],
        "review_note": "机房木质工作台桌面与后方实木隔断墙壁大面积浸染失真深重的暗红橙暖偏色。"
    },
    8613: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "金属台灯灯罩与办公桌桌面微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "电脑主机旁站立的虎斑猫浅棕色背毛与金属台灯灯罩表面色彩略显欠饱和脱色偏冷灰。"}
        ],
        "review_note": "电脑主机旁站立的虎斑猫浅棕色背毛与金属台灯灯罩表面色彩略显欠饱和脱色偏冷灰。"
    },

    # === Sheet 11 ===
    8615: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "室内墙壁原本鲜艳亮丽的苹果绿色涂装脱色错变为发暗灰暗的浅黄灰死色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内木质家具与踢脚线大面积微染偏暗冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "苹果绿墙面涂层大面积欠饱和严重脱色褪变为暗淡无光的浅灰黄。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "墙壁大面积脱色使室内环境显得阴暗陈旧。"}
        ],
        "review_note": "室内墙壁原本鲜艳亮丽的苹果绿色涂装大面积欠饱和严重脱色褪变为暗淡灰暗的浅黄灰死色。"
    },
    8616: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "网球场原本开阔翠绿的塑胶草坪地面脱色错变为冰冷干瘪的灰泥死色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "网球场护栏与防风网阴影微染冷青偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "草坪地面大面积欠饱和严重脱色褪变为死灰暗淡色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "室外运动场草坪严重褪色发灰，完全破坏了运动场地的生机。"}
        ],
        "review_note": "网球场原本开阔翠绿的塑胶草坪地面大面积欠饱和严重脱色褪变为冰冷干瘪的灰泥死色。"
    },
    8617: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "棒球皮手套下方铺垫的原本纯正深海蓝色的丝绒垫布被颠覆性严重错涂为过度浓艳刺眼的深洋红紫伪色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "棒球手套皮革表面微染深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "错涂的垫布洋红紫色彩过于浓艳刺目。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "纯正海蓝垫布错变为荧光洋红紫，色彩违和突兀。"}
        ],
        "review_note": "棒球皮手套下方铺垫的原本纯正深海蓝色的丝绒垫布被颠覆性严重错涂为过度浓艳刺眼的深洋红紫伪色。"
    },
    8618: {
        "defects": [],
        "review_note": "审查通过"
    },
    8619: {
        "defects": [],
        "review_note": "审查通过"
    },
    8621: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "户外向导身穿的原本经典的军绿色工装短袖衬衫被颠覆性严重错涂为鲜艳明亮的宝蓝色异色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "向导手臂肤色与背景岩石大面积微染偏冷青蓝偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "错涂的宝蓝色衬衫织物色彩略显过度浓艳。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "工装衬衫颜色彻底颠覆性错配，在荒野自然环境中极为突兀违和。"}
        ],
        "review_note": "户外向导身穿的原本经典的军绿色工装短袖衬衫被颠覆性严重错涂为鲜艳明亮的宝蓝色异色。"
    },

    # === Sheet 12 ===
    8623: {
        "defects": [],
        "review_note": "审查通过"
    },
    8625: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "餐桌报纸上摆放的红色果酱罐塑料盖原本鲜艳的大红色被颠覆性严重错涂为发暗冷淡的灰紫蓝色异色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "餐桌报纸纸张表面微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "果酱罐身与餐具色彩略显欠饱和脱色发灰。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "鲜红瓶盖颠覆性错染为灰紫蓝，食品包装色彩严重失真。"}
        ],
        "review_note": "餐桌报纸上摆放的红色果酱罐塑料盖原本鲜艳的大红色被颠覆性严重错涂为发暗冷淡的灰紫蓝色异色。"
    },
    8626: {
        "defects": [],
        "review_note": "审查通过"
    },
    8628: {
        "defects": [],
        "review_note": "审查通过"
    },
    8629: {
        "defects": [],
        "review_note": "审查通过"
    },
    8631: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "雪道上滑行的滑雪手身穿的原本鲜艳醒目的亮橙红色防风外套被颠覆性严重错涂为冰冷浅天青蓝色异色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "雪面反光与周围滑雪器材微染冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "错涂的天青蓝外套表面色彩略显欠饱和发白淡化。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "鲜亮橙红外套被彻底颠覆错涂为冰冷天青蓝，违背原图真实服饰。"}
        ],
        "review_note": "雪道上滑行的滑雪手身穿的原本鲜艳醒目的亮橙红色防风外套被颠覆性严重错涂为冰冷浅天青蓝色异色。"
    },

    # === Sheet 13 ===
    8635: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "翻盖手机挂绳上悬挂的原本纯正红色的毛绒小熊玩偶被颠覆性错染为过度浓艳刺眼的荧光深洋红紫色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "手机机身塑料外壳与桌面大面积微染偏深红紫暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的毛绒玩偶洋红紫色彩极度浓艳刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "毛绒挂件荧光异色违背普通织物常理。"}
        ],
        "review_note": "翻盖手机挂绳上悬挂的原本纯正红色的毛绒小熊玩偶被颠覆性错染为过度浓艳刺眼的荧光深洋红紫色。"
    },
    8636: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "客厅白墙与地面微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "客厅沙发靠背与背景白墙告示海报色彩略显欠饱和脱色偏冷灰。"}
        ],
        "review_note": "客厅沙发靠背与背景白墙告示海报色彩略显欠饱和脱色偏冷灰。"
    },
    8637: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "办公桌面与键盘包装盒阴影大面积浸染失真偏暗的冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "办公桌上方陈列的苹果无线键盘包装纸盒与说明书纸张表面大面积欠饱和脱色偏暗冷灰青色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "数码产品包装纸面受冷色偏色侵染显得泛暗发脏。"}
        ],
        "review_note": "办公桌上方陈列的苹果无线键盘包装纸盒与说明书纸张表面大面积欠饱和脱色偏暗冷灰青色。"
    },
    8638: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "白瓷餐盘右侧新鲜绿叶蔬菜沙拉原本清脆的翠绿色脱色错变为暗淡灰黑死色，松饼表面麦香金黄大面积焦黑褪色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白瓷餐盘釉面微染偏暗冷青偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "盘中蔬菜沙拉叶片大面积欠饱和严重脱色褪变为发暗灰黑。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "新鲜蔬菜脱色发黑完全破坏了食品的新鲜与可口质感。"}
        ],
        "review_note": "白瓷餐盘中盛放的美式松饼表面煎烤金黄麦香大面积焦黑褪色，右侧新鲜绿叶蔬菜沙拉大面积欠饱和严重脱色褪变为暗淡灰黑死色。"
    },
    8641: {
        "defects": [],
        "review_note": "审查通过"
    },
    8642: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "动物园长颈鹿展区内的沙土地表与木质围栏大面积浸染失真偏重的深暗红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "长颈鹿身体网纹斑块与沙土红棕色调过度浓艳深重。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "全场红棕失真偏重导致户外自然开阔感丧失。"}
        ],
        "review_note": "动物园长颈鹿展区内的沙土地表与木质围栏大面积浸染失真偏重的深暗红棕暖偏色。"
    },

    # === Sheet 14 ===
    8645: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内木质地板与床架阴影大面积浸染失真偏暗的红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "木质地板反光红棕色彩略显过度浓艳。"}
        ],
        "review_note": "室内木质地板与床架阴影大面积浸染失真偏暗的红棕暖偏色。"
    },
    8646: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "海滩岩石表面与游客防晒衣微染红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "海滩岩石上游客撑起的红色油纸遮阳伞面色彩略显过度浓艳刺眼。"}
        ],
        "review_note": "海滩岩石上游客撑起的红色油纸遮阳伞面色彩略显过度浓艳刺眼。"
    },
    8653: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "背景红砖建筑外墙原本鲜艳自然的砖红色大面积欠饱和脱色错变为暗淡灰暗的浅灰褐色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "街道沥青路面与建筑阴影微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "红砖建筑外墙大面积欠饱和严重脱色褪变为干瘪暗淡色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "砖墙脱色使原本明丽的街景显得沉闷枯燥。"}
        ],
        "review_note": "背景红砖建筑外墙原本鲜艳自然的砖红色大面积欠饱和严重脱色褪变为暗淡灰暗的浅灰褐色。"
    },
    8656: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "餐盘边缘与金属餐夹微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "自助餐台陶瓷餐盘中摆放的烤牛肉片与切片面包表面色彩大面积欠饱和脱色偏暗灰冷色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "食物脱色发灰导致熟肉和面包失去诱人光泽。"}
        ],
        "review_note": "自助餐台陶瓷餐盘中摆放的烤牛肉片与切片面包表面色彩大面积欠饱和脱色偏暗灰冷色。"
    },
    8658: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "打开的黑色收纳箱内趴卧的宠物幼犬棕黄色皮毛表面大面积微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "幼犬背部棕色毛发色彩略显过度浓艳。"}
        ],
        "review_note": "打开的黑色收纳箱内趴卧的宠物幼犬棕黄色皮毛表面大面积微染偏深红棕暖偏色。"
    },
    8660: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "草地围栏木柱微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "农场草地围栏后方的茂密树林枝叶大面积欠饱和脱色偏冷灰淡绿。"}
        ],
        "review_note": "农场草地围栏后方的茂密树林枝叶大面积欠饱和脱色偏冷灰淡绿。"
    },

    # === Sheet 15 ===
    8661: {
        "defects": [],
        "review_note": "审查通过"
    },
    8662: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "陶瓷甜品碗边缘阴影微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "白瓷甜品碗中盛放的坚果碎与燕麦谷物表面色彩略显过度浓艳。"}
        ],
        "review_note": "白瓷甜品碗中盛放的坚果碎与燕麦谷物表面色彩略显过度浓艳。"
    },
    8663: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "生日聚会餐盘上摆放的点燃蜡烛的巧克力蛋糕表面大面积浸染失真偏暗的红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "蛋糕表面巧克力淋酱与草莓红色略显过度浓艳。"}
        ],
        "review_note": "生日聚会餐盘上摆放的点燃蜡烛的巧克力蛋糕表面大面积浸染失真偏暗的红棕暖偏色。"
    },
    8665: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "爵士乐演奏厅背景墙面与乐手身穿的黑色西装大面积浸染失真深重的暗冷青蓝偏色与杂色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "演奏厅乐器金属光泽与木质背景大面积欠饱和脱色偏暗灰。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "演奏厅大面积浸染冷青杂色，舞台光影氛围失真严重。"}
        ],
        "review_note": "爵士乐演奏厅背景墙面与乐手身穿的黑色西装大面积浸染失真深重的暗冷青蓝偏色与杂色。"
    },
    8666: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "欧式厨房原本纯净白皙的整体橱柜面板与大理石餐桌表面大面积浸染失真偏暗的红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "橱柜表面暖红棕色反光色彩略显过度浓艳。"}
        ],
        "review_note": "欧式厨房原本纯净白皙的整体橱柜面板与大理石餐桌表面大面积浸染失真偏暗的红棕暖偏色。"
    },
    8667: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "牧场天空与远景灌木微染冷黄偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "牧场草坪原本鲜艳生机盎然的青绿草地大面积欠饱和严重脱色褪变为干瘪枯黄暗淡色。"}
        ],
        "review_note": "牧场草坪原本鲜艳生机盎然的青绿草地大面积欠饱和严重脱色褪变为干瘪枯黄暗淡色。"
    },

    # === Sheet 16 ===
    8668: {
        "defects": [],
        "review_note": "审查通过"
    },
    8670: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "绿叶前停栖的小鸟后方背景原本纯净统一的自然虚化背景被颠覆性严重错涂为过度浓艳刺眼的荧光深洋红紫伪色斑块。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "小鸟腹部羽毛与树枝边缘大面积微染深洋红暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错涂的背景洋红紫斑块色彩极度浓艳刺目。"},
            {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "背景出现大片恶性荧光洋红伪色斑块，彻底破坏自然微距摄影的真实感。"}
        ],
        "review_note": "绿叶前停栖的小鸟后方背景原本纯净统一的自然虚化背景被颠覆性严重错涂为过度浓艳刺眼的荧光深洋红紫伪色斑块。"
    },
    8671: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "巨浪浪花阴影与海面微染偏暗冷青偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "巨浪中冲浪者操纵的风筝风帆原本鲜艳醒目的大红色帆面大面积欠饱和严重脱色褪变为暗淡灰暗的浅粉白死色。"}
        ],
        "review_note": "巨浪中冲浪者操纵的风筝风帆原本鲜艳醒目的大红色帆面大面积欠饱和严重脱色褪变为暗淡灰暗的浅粉白死色。"
    },
    8674: {
        "defects": [],
        "review_note": "审查通过"
    },
    8675: {
        "defects": [],
        "review_note": "审查通过"
    },
    8677: {
        "defects": [],
        "review_note": "审查通过"
    },

    # === Sheet 17 ===
    8680: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "网球场上网球女选手身穿的白色网球裙反光略染冷青蓝偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "网球拍边框明黄色漆面色彩略显过度浓艳。"}
        ],
        "review_note": "网球场上网球女选手身穿的白色网球裙反光略染冷青蓝偏色，网球拍边框明黄色漆面色彩略显过度浓艳。"
    },
    8682: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "街景远方楼宇与天空微染冷灰青偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "城市街道晚高峰车流行驶的沥青路面大面积欠饱和脱色发暗偏冷灰，街景红绿灯微暗。"}
        ],
        "review_note": "城市街道晚高峰车流行驶的沥青路面大面积欠饱和脱色发暗偏冷灰，街景红绿灯微暗。"
    },
    8683: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "西餐厅餐桌木纹与白瓷餐盘大面积浸染失真偏暗的红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "盘中烘焙薄饼与酱料色彩过度浓艳发红。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "餐桌与食物大面积暗红暖偏色，破坏了餐厅典雅氛围。"}
        ],
        "review_note": "西餐厅餐桌木纹与白瓷餐盘大面积浸染失真偏暗的红棕暖偏色，盘中烘焙薄饼与酱料色彩过度浓艳发红。"
    },
    8684: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白色床单与宠物周围阴影微染冷青灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "床垫上相互依偎睡觉的幼猫与黑狗皮毛边缘色彩略显欠饱和脱色发灰发冷。"}
        ],
        "review_note": "床垫上相互依偎睡觉的幼猫与黑狗皮毛边缘色彩略显欠饱和脱色发灰发冷。"
    },
    8686: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "快餐厅木质餐桌前手持汉堡就餐的女士面部肤色及夹克大面积浸染失真红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "餐桌反光与汉堡食材色彩过度浓艳发红。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "人物肤色与快餐食物红棕暖偏色深重失真。"}
        ],
        "review_note": "快餐厅木质餐桌前手持汉堡就餐的女士面部肤色及夹克大面积浸染失真红棕暖偏色，餐桌反光与汉堡食材色彩过度浓艳。"
    },
    8690: {
        "defects": [],
        "review_note": "审查通过"
    },

    # === Sheet 18 ===
    8691: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "棒球比赛现场后方看台密集的观众席与看台栏杆大面积浸染失真偏暗的冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "球场内场红土跑道与击球手球衣色彩略显欠饱和脱色发暗。"}
        ],
        "review_note": "棒球比赛现场后方看台密集的观众席与看台栏杆大面积浸染失真偏暗的冷青蓝偏色，内场红土跑道色彩略显欠饱和脱色发暗。"
    },
    8692: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "卫生间镜框阴影与水龙头金属反光微染偏冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "卫生间洗手台周围原本温馨柔和的米黄色墙面乳胶漆与洗手台大理石台面大面积欠饱和严重脱色褪变为冰冷灰白死色。"}
        ],
        "review_note": "卫生间洗手台周围原本温馨柔和的米黄色墙面乳胶漆与洗手台大理石台面大面积欠饱和严重脱色褪变为冰冷灰白死色。"
    },
    8694: {
        "defects": [],
        "review_note": "审查通过"
    },
    8695: {
        "defects": [],
        "review_note": "审查通过"
    },
    8696: {
        "defects": [
            {"id": "B", "name": "溢色", "severity": "L2", "description": "陶瓷碗碟错涂的过度浓艳荧光亮青蓝色越界严重溢色侵染周围金属托盘表面。"},
            {"id": "C", "name": "错色", "severity": "L3", "description": "置物架上陈列的原本朴素土陶与米白色陶瓷碗碟表面被颠覆性严重错涂为过度浓艳刺眼的荧光亮青蓝色伪色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错涂的青蓝色料色彩极度浓艳刺眼，高光严重溢出。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "恶性荧光青蓝伪色严重破坏了陶艺器皿的自然质朴外观。"}
        ],
        "review_note": "置物架上陈列的原本朴素土陶与米白色陶瓷碗碟表面被颠覆性严重错涂为过度浓艳刺眼的荧光亮青蓝色伪色，青蓝色彩严重溢色侵染周围金属托盘表面。"
    },
    8698: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "工地上摆放的毛绒玩具泰迪熊棕色毛绒表面及后方木料堆色彩略显欠饱和脱色偏灰浅淡色。"}
        ],
        "review_note": "工地上摆放的毛绒玩具泰迪熊棕色毛绒表面及后方木料堆色彩略显欠饱和脱色偏灰浅淡色。"
    },

    # === Sheet 19 ===
    8699: {
        "defects": [],
        "review_note": "审查通过"
    },
    8700: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "零食包装盒阴影与床品边缘微染深粉红洋红暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "卧室床上铺设的粉色床单及散落的巧克力包装盒表面大面积浸染过度浓艳刺眼的荧光深粉红洋红偏色与杂色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "洋红荧光色斑与床单原有图案光影脱节，视觉违和。"}
        ],
        "review_note": "卧室床上铺设的粉色床单及散落的巧克力包装盒表面大面积浸染过度浓艳刺眼的荧光深粉红洋红偏色与杂色。"
    },
    8701: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "夜景庭院露天餐桌椅表面被颠覆性错染为深洋红紫与冷青蓝杂色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "夜景庭院露台中串灯装饰的遮阳伞伞面及地面大面积浸染失真深重的暗红紫暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "遮阳伞与餐桌表面深洋红紫色彩过度浓艳失真。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "完全破坏了原本温馨明亮的暖黄夜景光影氛围，色彩混乱。"}
        ],
        "review_note": "夜景庭院露台中串灯装饰的遮阳伞伞面及下方露天餐桌椅表面大面积浸染过度浓艳失真的深洋红紫偏色与冷色杂斑，完全破坏了原本温馨明亮的暖黄夜景光影。"
    },
    8702: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "下方人群黑发与遮阳伞边缘阴影大面积微染冷青色偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "户外人群撑起的亮黄色遮阳伞边缘及右侧背景遮阳伞条纹织物大面积欠饱和脱色发暗。"}
        ],
        "review_note": "户外人群撑起的亮黄色遮阳伞边缘及右侧背景遮阳伞条纹织物大面积欠饱和脱色发暗，微染冷青色偏色。"
    },
    8703: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "马桶座圈阴影与地面微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "卫生间白色陶瓷马桶后方原本明亮温暖的浅黄绿色瓷砖墙面与幼童面部红润肤色大面积欠饱和严重脱色褪变为惨淡灰白死色。"}
        ],
        "review_note": "卫生间白色陶瓷马桶后方原本明亮温暖的浅黄绿色瓷砖墙面与幼童面部红润肤色大面积欠饱和严重脱色褪变为惨淡灰白死色。"
    },
    8707: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "客房地毯与窗帘阴影微染暗冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "酒店客房客厅右侧原本温馨典雅的暖棕色实木墙面与木质地板大面积欠饱和严重脱色褪变为冰冷灰白淡色。"}
        ],
        "review_note": "酒店客房客厅右侧原本温馨典雅的暖棕色实木墙面与木质地板大面积欠饱和严重脱色褪变为冰冷灰白淡色。"
    },

    # === Sheet 20 ===
    8708: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "复古欧式浴室壁灯灯罩与镜框阴影大面积浸染失真偏暗的冷灰青偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "复古欧式浴室壁灯散发的温馨金黄暖光与墙面暖黄瓷砖大面积欠饱和严重脱色褪变为冰冷惨白的灰暗死色。"}
        ],
        "review_note": "复古欧式浴室壁灯散发的温馨金黄暖光与墙面暖黄瓷砖大面积欠饱和严重脱色褪变为冰冷惨白的灰暗死色。"
    },
    8709: {
        "defects": [],
        "review_note": "审查通过"
    },
    8711: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "打开的双门冰箱冷藏室内摆放的果酱罐与饮料盒表面大面积微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "冷藏室门板上红色包装食品色彩略显过度浓艳。"}
        ],
        "review_note": "打开的双门冰箱冷藏室内摆放的果酱罐与饮料盒表面大面积微染偏深红棕暖偏色，局部红色包装色彩略显过度浓艳。"
    },
    8712: {
        "defects": [],
        "review_note": "审查通过"
    },
    8713: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "餐桌上摆放的烘焙司康面包表面及木质桌面大面积微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "面包表皮烘烤焦糖色彩略显过度浓艳偏深。"}
        ],
        "review_note": "餐桌上摆放的烘焙司康面包表面及木质桌面大面积微染偏深红棕暖偏色，面包表皮色彩略显过度浓艳。"
    },
    8714: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "茶几金属支架与沙发阴影微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "客厅摆放笔记本电脑的茶几周围原本温暖明亮的浅黄色墙壁与后方红木储物柜表面大面积欠饱和严重脱色褪变为冰冷灰白淡色。"}
        ],
        "review_note": "客厅摆放笔记本电脑的茶几周围原本温暖明亮的浅黄色墙壁与后方红木储物柜表面大面积欠饱和严重脱色褪变为冰冷灰白淡色。"
    }
}


def main():
    grounding_path = "LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_43.json"
    with open(grounding_path, "w", encoding="utf-8") as f:
        json.dump(BATCH_43_REVIEWS, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(BATCH_43_REVIEWS)} reviews to {grounding_path}")

    all_path = "LS_lcad_reviewer/exports/reviewed_1_10000_all.json"
    clean_path = "LS_lcad_reviewer/exports/reviewed_1_10000_clean.json"

    with open(all_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    with open(clean_path, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    pass_count = 0
    revised_count = 0
    meltdown_count = 0

    for t_id, rev in BATCH_43_REVIEWS.items():
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

        # Check A meltdown
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

    print(f"Batch 43 applied successfully!")
    print(f"Total: {len(BATCH_43_REVIEWS)}, Passes: {pass_count} ({pass_count/len(BATCH_43_REVIEWS)*100:.2f}%), Revised: {revised_count} ({revised_count/len(BATCH_43_REVIEWS)*100:.2f}%), Meltdown A: {meltdown_count}")

if __name__ == "__main__":
    main()
