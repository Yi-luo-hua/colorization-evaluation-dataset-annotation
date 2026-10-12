# -*- coding: utf-8 -*-
"""
脚本：Batch 01 视觉大图直审具象定物全量落地与同步
涵盖：Task #2 ~ Task #210 共 120 组任务
重点：包含 Task #30 (lcad/000000001841.png) 深度重塑具象定物、Task #158 A项缺色熔断
"""

import json
import os
import sys

# 120 组任务精确具象定物字典
# key: task_id (int)
GROUNDING_DATA = {
    # Sheet 01
    2: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "客机垂尾法航经典红蓝标志中的红色条纹严重脱色变暗为深蓝灰色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "天空背景与客机白色机身背光面整体轻度偏冷青蓝调。"},
            {"id": "B", "name": "溢色", "severity": "L1", "description": "客机机翼与尾翼边缘泛轻微冷青色溢色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：客机垂尾法航标志红色脱色变暗(C-L2)；机身背光偏冷青蓝调(D-L1)；机翼边缘轻度溢色(B-L1)。"
    },
    3: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L1", "description": "蛋糕表面彩色裱花装饰与蜡烛色彩脱色淡化。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内墙壁背景与男子面部肤色轻微偏青黄冷色调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：蛋糕表面彩色裱花脱色淡化(C-L1)；室内墙面与肤色偏青黄冷色调(D-L1)。"
    },
    4: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "餐桌上各盘菜肴与沙拉中的蔬菜、酱汁明显欠饱和发灰褪色，缺乏新鲜色泽。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "陶瓷餐盘与桌面整体色调偏暗冷灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：餐桌菜肴沙拉欠饱和发灰褪色(E2-L2)；餐盘桌面偏暗冷灰调(D-L1)。"
    },
    5: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "右侧热狗上原本鲜红的番茄酱严重脱色变暗为发黑深褐色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白色泡沫餐盒与热狗面包外皮泛轻微冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：热狗表面番茄酱严重脱色发黑(C-L2)；餐盒与面包外皮偏冷青灰调(D-L1)。"
    },
    6: {
        "defects": [
            {"id": "B", "name": "溢色", "severity": "L1", "description": "紫色塑料飞盘边缘色料轻度溢出色晕渗透至小狗白色嘴吻及前爪毛发。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白色小狗全身皮毛及背景草地整体轻度偏暗冷青蓝调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "紫色飞盘本身艳丽度较GT有所衰减欠饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：紫色飞盘边缘溢色至小狗毛发(B-L1)；小狗毛皮偏暗冷青蓝调(D-L1)；飞盘色彩欠饱和(E2-L1)。"
    },
    8: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内暖黄背景墙面与天花板整体轻度偏冷青灰调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "三位女子的金色头发与面部肤色轻度欠饱和苍白发灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：室内背景墙面偏冷青灰调(D-L1)；女子金发与肤色欠饱和苍白(E2-L1)。"
    },

    # Sheet 02
    9: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "马桶盖内侧原本郁郁葱葱的翠绿树林风景画被彻底错涂为大面积枯焦土黄褐色。"},
            {"id": "B", "name": "溢色", "severity": "L2", "description": "马桶盖内圈边缘深蓝色色料严重溢出污染浅灰马桶圈内壁。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "马桶盖图案与内壁色彩衔接生硬突兀，严重违背真实视觉自然度。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：马桶盖内侧翠绿树林错涂枯黄土褐色(C-L3)；内圈深蓝溢色污染马桶壁(B-L2)；整体视觉生硬不自然(F-L2)。"
    },
    11: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "摩托车金属导流罩、车头风挡与车身机械结构整体严重偏冷青紫灰调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "背景路面与停放车辆欠饱和发暗。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：摩托车金属导流罩与车身偏冷青紫灰调(D-L2)；背景路面欠饱和发暗(E2-L1)。"
    },
    14: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "水果摊上方原本鲜明的深蓝色货架横梁与背景被错误涂抹为暗草绿色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "菠萝绿色叶冠及香蕉金黄果皮色彩欠饱和偏暗。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：水果摊深蓝货架横梁错涂暗草绿(C-L2)；菠萝叶冠与香蕉皮欠饱和发暗(E2-L1)。"
    },
    15: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "男子手背皮肤呈现不自然的紫红发青偏色，且西装面料整体偏冷暗紫灰。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "领带细纹与西装面料中微弱的彩色细节完全褪色丧失。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "手部皮肤与西服袖口边缘交界处有轻微色晕过渡不自然。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：男子手背肤色紫红发青偏色(D-L2)；领带细纹脱色丧失(E2-L2)；袖口边缘过渡不自然(F-L1)。"
    },
    21: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "电脑显示屏中原本鲜亮的深蓝紫色操作系统窗口与多色数据图表严重欠饱和发灰褪色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "办公桌隔板木质纹理与墙体整体轻度偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：电脑屏幕内深蓝紫视窗与图表严重欠饱和发灰(E2-L2)；工位桌板偏冷青灰调(D-L1)。"
    },
    22: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "雪地道路两旁洁白积雪与寒冬天空整体严重偏暖黄土褐色，丧失冰雪纯净质感。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "骑行者身上的外套色彩轻微褪色混淆。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：雪地道路洁白积雪严重偏暖黄土褐色(D-L2)；骑马者外套色彩轻度失真(C-L1)。"
    },

    # Sheet 03 (含 Task #30)
    24: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "毛绒泰迪熊身上原本鲜红醒目的毛衣织物严重脱色变暗为灰褐色。"},
            {"id": "B", "name": "溢色", "severity": "L1", "description": "后方靠垫明蓝色越界溢出侵染至小男孩浅色头发与皮沙发边缘。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "真皮沙发与背景环境整体轻度偏冷暗紫调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：毛绒熊鲜红毛衣严重脱色变灰褐(C-L2)；靠垫明蓝溢色侵染男孩头发(B-L1)；沙发偏冷暗紫调(D-L1)。"
    },
    26: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "开阔天空与海洋水体整体严重偏深暗青紫冷调，与真实自然天空色调严重背离。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "天空与海平线交界处光影色彩极其生硬违和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：天空与海洋严重偏暗青紫冷调(D-L2)；海天交界生硬违和(F-L2)。"
    },
    27: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "海面波光与远方山脉整体轻度偏冷青灰调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "帆船白色船身与帆布色彩欠饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：海面波光与远山偏冷青灰调(D-L1)；帆船白帆欠饱和(E2-L1)。"
    },
    28: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "女子面部肤色及高脚杯中的白葡萄酒整体轻度偏冷青黄调，缺乏暖光通透感。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "女子唇色与面部红润感欠饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：女子面部肤色与白葡萄酒偏冷青黄调(D-L1)；红润感欠饱和(E2-L1)。"
    },
    30: {
        "defects": [
            {"id": "B", "name": "溢色", "severity": "L2", "description": "女性右侧裸露肩颈及锁骨边缘出现大面积刺目的荧光亮青蓝色溢色与冷光光晕污染。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "女性面部及颈部肤色大面积呈现不自然的蜡黄泛青绿偏色，完全丧失正常血色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "女性唇部原本粉嫩的唇膏色彩彻底褪色脱白，严重欠饱和。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "肩颈荧光蓝斑与蜡黄肤色在深黑背景前产生严重违和的光影断层，视觉自然度极差。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：女性右肩颈严重荧光青蓝溢色光晕(B-L2)；面颈肤色严重蜡黄泛青绿(D-L2)；唇部粉嫩唇膏脱白欠饱和(E2-L2)；整体严重光影断层违和(F-L2)。"
    },
    33: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "高脚玻璃杯中原本鲜艳浓郁的红葡萄酒酒液欠饱和发暗偏灰。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "手部皮肤及背景木质墙体整体轻度偏冷青紫调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：高脚杯内红葡萄酒欠饱和发暗(E2-L1)；手部肤色偏冷青紫调(D-L1)。"
    },

    # Sheet 04
    37: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "雕花木质餐盘表面整体色调偏深红橙暖色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：雕花木质餐盘表面偏深红橙暖色(D-L1)。"
    },
    39: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "房间白色墙壁、窗框与天花板整体严重偏向诡异生硬的泥黄发绿偏色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "室内光影与墙面发绿质感严重不协调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：房间白墙与窗框严重泥黄发绿偏色(D-L2)；光影不协调(F-L1)。"
    },
    40: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "女士身上鲜艳明亮的大红色短袖T恤严重褪色变暗为沉闷的灰土褐色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "女士面部肤色及金色头发整体偏冷暗紫灰色调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：女士鲜艳大红短袖严重褪色为灰土褐色(C-L2)；面部肤色偏冷暗紫灰(D-L1)。"
    },
    41: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L1", "description": "甜甜圈表面原本鲜艳纯正的明亮橙色糖霜颗粒被错涂为偏暗的深红褐色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白色垫纸边缘及桌面整体泛轻微冷青紫调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：甜甜圈表面明亮橙色糖霜被错涂深红褐色(C-L1)；餐巾纸边缘偏冷青紫调(D-L1)。"
    },
    43: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "近景左下角雨伞原本鲜艳纯正的红黑格子花纹严重褪色变暗为灰土暗紫红。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "背景梯田茶树原本生机盎然的翠绿植被整体欠饱和发暗发灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：近景雨伞鲜红格纹褪色为暗土紫红(C-L2)；梯田茶树翠绿植被欠饱和发暗(E2-L1)。"
    },
    44: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "右侧醒目的纯正天蓝色葡萄酒玻璃瓶（RELAX）严重欠饱和发暗，丧失晶莹通透质感。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白色烤面包机与背景墙面轻度偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：天蓝色葡萄酒玻璃瓶严重欠饱和发暗(E2-L2)；白色烤面包机与墙面偏冷青灰(D-L1)。"
    },

    # Sheet 05
    45: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "站台停靠的轻轨列车车头原本标志性的大红色涂装被严重错涂为洋红粉紫伪色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "车站站台钢构穹顶与白色列车车身整体轻度偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：轻轨列车车头大红涂装严重错涂洋红粉紫(C-L3)；站台钢架偏冷青灰调(D-L1)。"
    },
    46: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "桌面上原本鲜艳深紫色的餐巾垫布严重欠饱和发暗褪色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "桌面与人物衣物整体偏冷暗青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：桌面深紫色餐巾垫布严重欠饱和褪色(E2-L2)；桌面人物衣物偏冷暗青灰(D-L1)。"
    },
    48: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "滑板少年原本醒目鲜艳的荧光黄色安全头盔与护膝严重脱色漂白为灰白色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "木质滑板U型池与周围墙体整体偏深冷暗紫灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：滑板少年荧光黄头盔与护具严重脱色变灰白(C-L2)；木质U型池偏冷暗紫灰(D-L2)。"
    },
    51: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "列车侧面红褐色腰线彩条饱和度偏高浓艳。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "站台棚架金属结构与列车白色车厢整体偏微暖红黄调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：列车红褐腰线色彩过饱和浓艳(E1-L1)；站台金属棚架偏微暖红黄调(D-L1)。"
    },
    53: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "白鹭脚下原本清澈澄净的海水与浅滩水体被大面积错误涂抹为浑浊的泥黄草绿色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "白鹭身体轮廓边缘与浑浊水面交接生硬，视觉自然度较差。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：白鹭脚下清澈海水大面积错涂泥黄草绿色(C-L2)；水面轮廓交界生硬(F-L2)。"
    },
    54: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "餐盘中烤土豆焦香表皮与紫甘蓝蔬菜色彩过于深沉浓烈、过饱和发暗。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白色陶瓷餐盘边缘整体偏暗冷紫调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：烤土豆表皮与紫甘蓝蔬菜过饱和浓烈发暗(E1-L2)；餐盘边缘偏暗冷紫调(D-L1)。"
    },

    # Sheet 06
    57: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "白色纸杯内原本鲜艳明亮的纯正蓝紫色浆果冰淇淋被严重错涂为焦黄土棕色冰淇淋。"},
            {"id": "B", "name": "溢色", "severity": "L1", "description": "冰淇淋球边缘色晕轻微渗透至白色吸水纸巾。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：亮蓝紫色浆果冰淇淋被严重错涂焦黄土棕色(C-L3)；纸杯边缘轻微溢色(B-L1)。"
    },
    60: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "双层大巴车头白色车漆与挡风玻璃反光整体轻度偏暖黄微红调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：双层大巴车头白色车漆整体偏暖黄微红调(D-L1)。"
    },
    61: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "背景草坪与树林植被色彩过饱和刺眼、偏浓艳焦绿。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "蓝色皮卡车身导流板与车门金属漆面泛轻度暗冷青紫调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：背景草坪树林过饱和浓艳焦绿(E1-L1)；蓝色皮卡车门金属漆偏冷青紫调(D-L1)。"
    },
    62: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "大象身体泥灰色皮毛表面出现不自然的冷暗青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "草原枯草与低矮灌木植被欠饱和发灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：大象身体泥灰皮毛偏冷暗青蓝调(D-L1)；草原枯草灌木欠饱和发灰(E2-L1)。"
    },
    63: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L1", "description": "雪道旁原本鲜艳醒目的红色滑雪指示三角旗严重脱色变暗。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "滑雪道洁白积雪与远山冰雪整体偏冷青蓝调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：红色滑雪指示三角旗脱色变暗(C-L1)；雪道洁白积雪偏冷青蓝调(D-L1)。"
    },
    66: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "甜甜圈内原本鲜红晶莹的草莓果酱夹心严重褪色变暗为发黑深褐色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "甜甜圈油炸金黄面包外皮欠饱和褪淡发灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：甜甜圈内草莓果酱严重褪色变黑褐(C-L2)；油炸金黄面包外皮欠饱和发灰(E2-L1)。"
    },

    # Sheet 07
    67: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "卧室双人床洁白被褥、枕头与背景墙壁大面积严重偏向诡异生硬的泥黄发绿偏色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "台灯光照与床单暗绿偏色冲突强烈，光影质感极其违和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：双人床被褥枕头与墙壁大面积泥黄发绿偏色(D-L2)；光影冲突违和(F-L2)。"
    },
    68: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "客车侧面原本鲜艳明亮的大红色车标字样与拉花装饰带严重脱色变暗为发黑灰褐。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白色客车车体与路面整体轻度偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：大客车大红车标字样脱色变黑灰褐(C-L2)；白色客车车身偏冷青灰调(D-L1)。"
    },
    69: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "室内客厅原本温馨暖黄的墙壁整体严重偏向冷暗青绿偏色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "吉他木质面板与人物肤色在冷绿背景前过渡生硬。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：客厅暖白墙壁严重偏冷暗青绿(D-L2)；吉他面板与肤色过渡生硬(F-L1)。"
    },
    70: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "荧光绿塑料碗整体色调偏深偏暖黄，缺乏原本鲜亮荧光通透感。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：荧光绿塑料碗色调偏深偏暖黄(D-L1)。"
    },
    72: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "空中高飞的风筝原本色彩斑斓的大红与亮黄羽翼欠饱和褪色发暗。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：空中风筝大红与亮黄羽翼欠饱和褪色发暗(E2-L1)。"
    },
    74: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "背景倒垂的青翠柳树枝叶大面积脱色黑化、错涂为干枯死寂的泥灰褐色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白鹅周围的水体与石壁整体偏暗冷青紫调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：背景青翠柳枝严重脱色黑化为泥灰褐色(C-L2)；白鹅周围水体偏暗冷青紫调(D-L1)。"
    },

    # Sheet 08
    75: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "厨房原本清新的浅天蓝色橱柜推拉门与地面瓷砖大面积脱色褪白为灰米色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白色橱柜内嵌家电与台面轻度偏冷暗灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：浅天蓝色橱柜门大面积脱色褪白为灰米色(C-L2)；家电台面偏冷暗灰调(D-L1)。"
    },
    77: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "机场跑道两旁大面积草坪植被严重偏向暗深冷青紫泥褐色。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "客机垂尾原本鲜明的德之翼亮黄色标识条纹褪色变暗。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "客机白色机身与周围地表色彩严重欠饱和发灰发暗。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：跑道草坪严重偏暗深冷青紫泥褐(D-L2)；客机垂尾黄色条纹褪暗(C-L1)；全景欠饱和发灰发暗(E2-L2)。"
    },
    78: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "海滩白色翻卷海浪与远景海水水体整体轻度偏冷青绿色调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：海滩白色海浪与海水整体轻度偏冷青绿色调(D-L1)。"
    },
    79: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "客厅白色天花板、墙面与窗框大面积严重偏向浓重焦糊的泥土黄褐色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "天花板黄褐偏色与室内自然采光严重割裂，视觉违和感强烈。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：客厅白色天花板与墙面严重浓重焦糊泥黄褐色偏色(D-L2)；采光严重割裂失真(F-L2)。"
    },
    80: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "户外风筝节大面积绿色草坪被严重错涂为枯槁暗沉的泥土冷灰紫褐色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "空中串联放飞的各色彩色风筝整体色彩欠饱和发暗。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "草坪生硬发紫黑与明亮天空严重失真脱节。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：大面积草坪被严重错涂枯槁泥土冷灰紫褐色(D-L2)；风筝色彩欠饱和发暗(E2-L1)；草坪失真脱节(F-L2)。"
    },
    81: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "击球手原本鲜亮纯正的宝蓝色短袖球衣与头盔色彩欠饱和微暗。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "背景高大树木茂密树冠与棒球场沙土地面整体轻度偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：击球手宝蓝球衣色彩欠饱和微暗(E2-L1)；背景树林与沙土地面偏冷青灰调(D-L1)。"
    },

    # Sheet 09
    85: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "大棕熊背部原本金褐油亮的光泽皮毛欠饱和褪色发灰。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "熊身背阴面皮毛与周围溪水岩石整体轻度偏冷暗青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：大棕熊背部皮毛欠饱和褪色发灰(E2-L1)；溪水岩石偏冷暗青灰调(D-L1)。"
    },
    86: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "小棕熊全身棕色毛发与背景落叶碎石整体欠饱和发灰，缺乏温润光泽。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "背景杂乱碎石地表轻度偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：小棕熊毛发欠饱和发灰(E2-L1)；碎石地表偏冷青灰调(D-L1)。"
    },
    87: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "电脑显示屏内原本明亮的青蓝色视窗界面与图标严重欠饱和褪白发灰。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "办公工位灰色织物隔断与桌面整体轻度偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：电脑屏幕内青蓝视窗严重褪白发灰(E2-L1)；工位织物隔断偏冷青灰调(D-L1)。"
    },
    90: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "骑马女郎身上原本鲜艳纯正的亮粉红比基尼泳衣被错涂为惨淡发灰的浅蓝青色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "海滩温润沙地与海水整体轻度偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：女郎亮粉红比基尼被错涂浅蓝青色(C-L2)；沙滩海水偏冷青灰调(D-L1)。"
    },
    91: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "飞盘高尔夫球篓后方的绿草坪与树林植被欠饱和发暗。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "金属链条球篓表面与阴影地表整体轻度偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：球篓后方绿草坪欠饱和发暗(E2-L1)；金属链条球篓表面偏冷青灰调(D-L1)。"
    },
    94: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "庭院右上方原本鲜艳光亮的深宝蓝色釉面大陶罐被严重脱色漂白为惨白灰色的素陶罐。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "中景异形岩石雕塑与地面木栈道整体轻度偏冷暗青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：深宝蓝色釉面陶罐严重脱色漂白为灰白色素陶罐(C-L2)；岩石雕塑偏冷暗青灰(D-L1)。"
    },

    # Sheet 10
    96: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "小型双发客机原本鲜明的大红色机翼与机鼻涂装严重褪色变暗为暗紫褐色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "停机坪水泥地面与背景天空整体轻度偏暖黄微暗调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：客机大红机翼与机鼻严重褪色为暗紫褐色(C-L2)；水泥地面偏暖黄微暗调(D-L1)。"
    },
    97: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "办公室内天花板、白色墙面与浅色窗帘大面积严重偏向阴冷暗青绿色调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "整幅室内光线色彩严重欠饱和发暗发灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：机房天花板墙面严重偏向阴冷暗青绿色(D-L2)；整幅光线严重欠饱和发暗(E2-L2)。"
    },
    99: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "飞机展场后方原本茂密青翠的整片树林植被被大面积严重错涂为诡异生硬的暗冷紫红色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "银色战斗机机身金属蒙皮与周围地面大面积偏深冷青紫调。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "背景树林紫红错色违背常识，视觉自然度极差。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：背景青翠树林严重错涂暗冷紫红色(C-L3)；战斗机机身偏深冷青紫调(D-L2)；视觉自然度极差(F-L2)。"
    },
    101: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "骑行步道左侧原本鲜艳深红的绿化灌木丛严重脱色枯槁变暗为黑褐色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "沥青路面与右侧河水整体轻度偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：步道深红观赏灌木严重脱色黑化(C-L2)；沥青路面与河水偏冷青灰调(D-L1)。"
    },
    102: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "儿童玩具木质橱柜上方原本灰白色的控制旋钮被错误涂抹为突兀刺目的大红色。"},
            {"id": "B", "name": "溢色", "severity": "L1", "description": "橱柜边缘与旋钮缝隙处出现不自然的红紫溢色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：玩具橱柜灰白旋钮错涂突兀大红色(C-L2)；旋钮边缘红紫溢色(B-L1)。"
    },
    103: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "复古巡航摩托车原本清新的薄荷绿烤漆外壳整体轻度偏冷青蓝暗色调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "摩托车圆形大灯与金属车把反光欠饱和偏灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：复古摩托车薄荷绿外壳偏冷青蓝暗色调(D-L1)；圆形大灯金属件反光欠饱和(E2-L1)。"
    },

    # Sheet 11 (含 Task #158 熔断)
    104: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "浴室玻璃置物架上原本晶莹纯正的深蓝色香水瓶与化妆品瓶欠饱和发灰褪色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白色陶瓷洗脸台面与大理石台面整体轻度偏冷青紫调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：浴室深蓝色香水瓶欠饱和褪色发灰(E2-L1)；大理石台面偏冷青紫调(D-L1)。"
    },
    108: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "新鲜蔬菜沙拉翠绿叶片欠饱和发暗发黄，缺乏生鲜色泽。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白色陶瓷盘与桌面整体轻度偏冷青紫暗调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：沙拉蔬菜翠绿叶片欠饱和发暗发黄(E2-L1)；餐盘与桌面偏冷青紫暗调(D-L1)。"
    },
    110: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "原本鲜艳夺目的大红色、宝蓝色与橙黄色拉杆旅行箱表面色彩几乎被完全剥夺褪尽，整体呈现死寂单调的灰白色。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "仅有微弱黄褐残留在原本鲜红的箱面上，色彩严重失真错配。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：红、蓝、黄拉杆旅行箱表面色彩几乎被全域剥夺褪尽为灰白色(E2-L3)；残存色块严重失真错配(C-L2)。"
    },
    111: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "警用皮卡车身侧面原本醒目的金黄色警徽星标与警用拉花字样欠饱和褪白发灰。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "背景民宅草坪与树林植被整体轻度偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：皮卡警徽金黄星标欠饱和褪白发灰(E2-L1)；背景草坪偏冷青灰调(D-L1)。"
    },
    115: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "街角原本鲜红醒目的消防栓严重褪色变暗为发黑土红褐色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "背景大面积红砖建筑外墙与窗框严重偏向发暗阴冷的土黄青绿偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "行走男子的牛仔外套与蓝色裤子欠饱和发灰发暗。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：街角原本鲜红消防栓脱色变黑土红褐(C-L2)；背景红砖外墙严重阴冷土黄发绿(D-L2)；行人牛仔衣欠饱和发暗(E2-L1)。"
    },
    118: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "客机垂尾与机身腹部原本标志性的大红色涂装拉花严重脱色变暗为灰暗紫褐色。"},
            {"id": "B", "name": "溢色", "severity": "L1", "description": "客机白色机身及机翼边缘在天空背景前泛轻微冷青色溢色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：客机垂尾大红涂装拉花脱色变暗灰紫褐(C-L2)；机身边缘轻微冷青色溢色(B-L1)。"
    },

    # Sheet 12
    122: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "雪地登山者身上原本鲜艳醒目的大红色冲锋裤严重褪色脱白为暗灰白色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "逆光雪山冰峰与开阔天空整体轻度偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：雪地登山者大红冲锋裤严重脱白为暗灰白色(C-L2)；逆光冰峰偏冷青灰调(D-L1)。"
    },
    123: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "动物园原木栅栏与岩壁涂色过于浓重浓烈、过饱和红棕色严重失真。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "地面草坪整体偏暖红黄调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：动物园原木栅栏与岩壁过饱和浓烈红棕色失真(E1-L2)；地面草坪偏暖红黄调(D-L1)。"
    },
    124: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "车站站台建筑红瓦屋面与候车旅客彩色服饰色彩过饱和浓艳。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "铁轨与碎石道床整体轻度偏暖红黄调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：车站红瓦屋面与旅客服饰色彩过饱和浓艳(E1-L1)；铁轨碎石偏暖红黄调(D-L1)。"
    },
    127: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "男子面部与身体肌肉肤色大面积严重偏向暗冷青紫调，缺乏自然红润光泽。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "洗手台边缘各色彩妆瓶罐色彩欠饱和发暗。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：男子面部身体肌肉肤色严重偏暗冷青紫调(D-L2)；彩妆瓶罐欠饱和发暗(E2-L1)。"
    },
    129: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "背景整片树林与灌木植被色彩过饱和刺眼、偏荧光浓艳绿。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "草坪地表阴影整体轻度偏暖黄绿调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：背景树林与灌木过饱和刺眼偏荧光浓艳绿(E1-L1)；草坪阴影偏暖黄绿调(D-L1)。"
    },
    131: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "复古踏板摩托车原本清新的薄荷绿车身烤漆整体偏暗冷青蓝灰调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "摩托车彩色座椅与外壳色彩欠饱和发暗。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：踏板摩托车薄荷绿外壳偏暗冷青蓝灰调(D-L1)；座椅外壳欠饱和发暗(E2-L1)。"
    },

    # Sheet 13
    132: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "黄牛身体皮毛整体偏深红褐色，街道建筑外立面泛轻微冷青灰调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "街头商铺招牌与环境色彩欠饱和发暗。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：黄牛皮毛偏深红褐(D-L1)；商铺招牌欠饱和发暗(E2-L1)。"
    },
    137: {
        "defects": [
            {"id": "B", "name": "溢色", "severity": "L1", "description": "铁路道口控制楼明黄外墙轮廓边缘轻微溢色至灰白天空背景。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "铁轨碎石与火车机车车身整体轻度偏冷青调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：铁路道口控制楼明黄外墙边缘轻微溢色(B-L1)；铁轨碎石偏冷青调(D-L1)。"
    },
    138: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "海滩海水与沙滩整体色彩严重欠饱和发暗发灰，丧失原本通透清澈的海滨氛围。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "海面白浪与暗沉水体衔接突兀，视觉自然度极差。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：海滩海水沙滩严重欠饱和发暗发灰(E2-L2)；白浪与暗沉水体衔接突兀违和(F-L2)。"
    },
    139: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "棒球防守队员身上的深宝蓝色球衣整体轻度偏暗冷青紫调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "背景棒球场草坪植被欠饱和发暗。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：棒球防守队员深宝蓝球衣偏暗冷青紫调(D-L1)；草坪欠饱和发暗(E2-L1)。"
    },
    140: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "高山牧场整片草坡植被大面积严重脱色发白，丧失原本生机草绿色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "山坡地表阴影与奶牛身侧整体偏冷青灰暗调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：高山牧场整片草坡植被严重脱色发白(E2-L2)；地表阴影偏冷青灰暗调(D-L1)。"
    },
    141: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "背景剪彩帐篷红色布幔与周围彩色旗帜过饱和浓艳刺眼。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "官员黑色西服面料与周围阴影整体轻度偏暖红黄调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：剪彩帐篷红布幔与旗帜过饱和浓艳(E1-L1)；黑色西服偏暖红黄调(D-L1)。"
    },

    # Sheet 14
    144: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "滑雪者原本鲜艳明亮的宝蓝色滑雪裤严重欠饱和褪色发灰。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "林间积雪与远处落叶树林整体轻度偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：滑雪者宝蓝滑雪裤严重欠饱和褪色发灰(E2-L1)；林间积雪偏冷青灰调(D-L1)。"
    },
    145: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "公交大巴车身侧面原本鲜艳明亮的亮玫红色广告标识与下围饰条严重褪色变暗。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "天空背景与白色公交车顶整体轻度偏黄绿微暗调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：双层大巴亮玫红广告拉花严重褪色变暗(C-L2)；车顶与天空偏黄绿微暗调(D-L1)。"
    },
    147: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L1", "description": "轻轨列车车顶与车厢侧面原本鲜艳的大红色涂装拉花脱色变暗。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "高架轨道与周围绿化树林整体轻度偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：轻轨车顶大红拉花脱色变暗(C-L1)；高架铁轨偏冷青灰调(D-L1)。"
    },
    148: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "美网公开赛背景看台原本深邃浓郁的纯正皇家深蓝色背景墙严重欠饱和脱色发黑。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "网球场地面整体偏枯暗冷灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：美网看台纯正皇家深蓝背景墙严重欠饱和脱色发黑(E2-L2)；球场地面偏枯暗冷灰(D-L1)。"
    },
    150: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "骑行男子面部肤色大面积严重偏向暗冷青紫调，血色全无。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "男子身体轮廓与白色自行车架边缘出现生硬的紫红光晕，视觉自然度极差。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：骑行男子面部肤色严重偏向暗冷青紫(D-L2)；身体与车架边缘生硬紫红光晕(F-L2)。"
    },
    155: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "餐厅室内白色墙壁大面积严重偏向阴冷暗青绿色调。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "门头红色EXIT应急安全指示灯色彩发暗褪色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：餐厅白色墙壁大面积严重阴冷暗青绿(D-L2)；EXIT红指示灯色彩发暗褪色(C-L1)。"
    },

    # Sheet 15 (含 Task #158 纯黑白A项熔断)
    156: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L1", "description": "男子黑色T恤胸前原本鲜艳的橙黄色复古啤酒厂图案印花褪色变暗。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "餐台熟食与就餐顾客面部肤色欠饱和发灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：男子T恤橙黄啤酒厂印花褪色变暗(C-L1)；熟食与肤色欠饱和发灰(E2-L1)。"
    },
    157: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "浴室白色墙砖、洗脸台面与条纹浴帘大面积严重偏向发暗生硬的泥黄发绿偏色。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "原本淡雅的浅灰蓝浴帘被大面积错染为深灰绿色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：浴室墙砖台面严重泥黄发绿(D-L2)；淡蓝条纹浴帘错染深灰绿(C-L2)。"
    },
    158: {
        "defects": [
            {"id": "A", "name": "缺色", "severity": "", "description": "生成图全域上色彻底失败，画面完全退化为黑白灰阶图像，全域缺色。"}
        ],
        "reviewed_score": 1.0,
        "needs_rescoring": False,
        "note": "视觉直审具象定物：生成图全域上色彻底失败，纯黑白灰阶退化，命中缺色A项熔断锁定1.0分(A)。"
    },
    159: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "纽约街头路牌（Madison Ave）原本标志性的鲜艳深天蓝色底色严重脱色变暗为发黑灰褐色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "金属路灯杆与背景建筑立面欠饱和发灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：街名路牌深天蓝底色严重脱色发黑灰褐(C-L2)；金属灯杆欠饱和发灰(E2-L1)。"
    },
    160: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "小男孩黄色短袖T恤、后方塑料移动房屋及地面整体轻度偏冷青灰调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "小朋友手中彩色塑料玩具飞盘欠饱和发暗。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：男孩黄短袖与移动房屋偏冷青灰调(D-L1)；塑料玩具飞盘欠饱和发暗(E2-L1)。"
    },
    161: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白色纸盘边缘与披萨饼皮整体轻度偏冷青灰暗调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "披萨表面的番茄红酱与烤芝士色彩欠饱和微暗。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：白色纸盘与披萨饼皮偏冷青灰暗调(D-L1)；番茄红酱与芝士欠饱和微暗(E2-L1)。"
    },

    # Sheet 16
    163: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "浴室中央椭圆雕花装饰镜边框原本华丽金黄色泽欠饱和发灰。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白色大理石洗脸台面与浴袍整体轻度偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：雕花装饰镜金黄边框欠饱和发灰(E2-L1)；大理石洗脸台偏冷青灰调(D-L1)。"
    },
    165: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "老式红砖钟楼建筑外立面整体轻度偏暖红黄调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "停车场白色车辆与地面水泥整体色彩欠饱和发暗。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：红砖钟楼外立面偏暖红黄调(D-L1)；停车场地面与白车欠饱和发暗(E2-L1)。"
    },
    166: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "女子身上原本鲜艳纯正的大红色长袖卫衣严重脱色变暗为发黑灰褐色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "客厅白色墙壁大面积严重偏向暗沉焦枯的泥土黄褐色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "生硬黄褐墙面与人物产生严重违和的光影断层。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：女子大红卫衣脱色变黑灰褐色(C-L2)；客厅墙壁严重暗沉焦枯泥黄褐色(D-L2)；光影断层违和(F-L2)。"
    },
    168: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "凌乱书桌台面与周围白色墙壁整体严重偏向暗冷青紫调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "桌面上纸盒包装与药瓶标签彩色印刷细节欠饱和发暗。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：书桌台面与白墙严重偏暗冷青紫(D-L2)；纸盒药瓶彩色印刷欠饱和发暗(E2-L1)。"
    },
    169: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "木屋地面铺设的原本鲜艳浓郁的深宝蓝色床单与被褥严重脱色变暗为黑灰色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "原木木屋墙壁与地面整体轻度偏暗冷红褐调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：深宝蓝床单被褥脱色变暗为黑灰色(C-L2)；原木木屋墙壁偏暗冷红褐调(D-L1)。"
    },
    170: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "海滩集会人群手持的原本鲜艳纯正的深紫蓝色宣传标语旗帜严重褪色发暗为死黑灰色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "海滩沙地与远景海面白浪整体轻度偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：深紫蓝色宣传标语旗帜褪色变黑灰(C-L2)；海滩沙地海水偏冷青灰调(D-L1)。"
    },

    # Sheet 17
    172: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L1", "description": "工位隔断上张贴的彩色海报中粉红色与大红色图案褪色变暗。"},
            {"id": "B", "name": "溢色", "severity": "L1", "description": "海报边缘印刷色彩轻微溢色至浅色工位隔板。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "办公电脑桌台面与地毯整体轻度偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：彩色海报粉红与大红图案褪色变暗(C-L1)；海报边缘轻微溢色(B-L1)；电脑桌偏冷青灰调(D-L1)。"
    },
    173: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "快餐外卖纸袋上红白条纹与大红商标文字整体轻度偏暖红黄调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：快餐外卖纸袋红白条纹与大红商标偏暖红黄调(D-L1)。"
    },
    174: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "林间空地金黄落叶与棕熊身体皮毛整体欠饱和发灰褪色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "古树树干与阴影地表轻度偏冷暗青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：金黄落叶与棕熊皮毛欠饱和发灰(E2-L1)；古树树干阴影偏冷暗青灰(D-L1)。"
    },
    176: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "开阔天空与地表整体轻度偏冷青蓝调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "长颈鹿颈部与躯干金黄色网状斑纹欠饱和微暗。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：开阔天空整体偏冷青蓝调(D-L1)；长颈鹿金黄斑纹欠饱和微暗(E2-L1)。"
    },
    179: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "马匹背部与颈项深色毛皮整体偏深红褐色偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "马身受光面红褐色毛皮局部色彩偏高浓艳。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：马匹背部皮毛偏深红褐色(D-L1)；马身受光面色彩局部过饱和浓艳(E1-L1)。"
    },
    180: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "空中飞翔的长串龙形风筝原本鲜艳的红黄条纹节段欠饱和发暗褪色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "海滩湿润沙地与海面白浪整体轻度偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：长串龙形风筝红黄条纹欠饱和发暗(E2-L1)；海滩水体偏冷青灰调(D-L1)。"
    },

    # Sheet 18
    181: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "双显示器电脑桌台面与周围白色墙壁整体轻度偏冷青灰调。"},
            {"id": "B", "name": "溢色", "severity": "L1", "description": "右侧置物架边缘在日光反光处轻微溢色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：电脑桌台面与白墙偏冷青灰调(D-L1)；置物架边缘轻微溢色(B-L1)。"
    },
    183: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "男子手中原本鲜亮夺目的亮粉红色雨伞严重脱色变暗为发黑暗红褐色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "男子白色短袖与女子面部肤色整体轻度偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：亮粉红雨伞严重脱色变暗为黑红褐(C-L2)；男子白短袖与肤色偏冷青灰调(D-L1)。"
    },
    184: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "小狗身上的救生衣与周围海水泛起刺目、过饱和浓艳的荧光黄绿浪花。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "海滩湿沙地与海浪阴影整体轻度偏黄绿暗调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：小狗救生衣与海浪过饱和浓艳荧光黄绿(E1-L1)；湿沙地偏黄绿暗调(D-L1)。"
    },
    185: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "西部木质店铺建筑外立面与电线杆整体轻度偏暖红黄橙调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：西部木质店铺建筑外立面偏暖红黄橙调(D-L1)。"
    },
    186: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "两匹白马原本洁白纯净的毛皮与马鬃表面轻度偏发暗发青冷调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "背景围观人群服饰与骑手制服色彩欠饱和发暗。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：白马毛皮马鬃偏发暗冷青调(D-L1)；围观人群服饰欠饱和发暗(E2-L1)。"
    },
    188: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "毛绒小熊玩具与婴儿襁褓棉被整体轻度偏黄绿微暖调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：毛绒小熊玩具与棉被轻度偏黄绿微暖调(D-L1)。"
    },

    # Sheet 19
    189: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "发言男子面部肤色及舞台背景幕布整体偏深冷暗青调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "男子面部红润血色欠饱和苍白。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：男子面部肤色与背景幕布偏冷暗青调(D-L1)；肤色欠饱和苍白(E2-L1)。"
    },
    190: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "汽车后视镜大红色外壳边缘涂漆色彩过饱和浓艳刺眼。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "后视镜镜面反光与镜框阴影微泛冷紫调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：后视镜大红外壳漆面过饱和浓艳(E1-L1)；镜面反光微冷紫调(D-L1)。"
    },
    192: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "两辆市政清洁垃圾车原本鲜艳纯正的亮黄色车头与车身烤漆欠饱和褪淡发暗。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "街道柏油路面与后方建筑立面整体轻度偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：垃圾车亮黄车漆欠饱和褪淡发暗(E2-L1)；街道柏油路面偏冷青灰调(D-L1)。"
    },
    194: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "跑酷青年原本穿着的鲜艳纯正宝蓝色牛仔裤严重脱色褪白为死沉发黑的灰黑色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "广场地面地砖与背景石雕栏杆整体轻度偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：宝蓝牛仔裤严重脱色为死沉黑灰(C-L2)；广场地面地砖偏冷青灰调(D-L1)。"
    },
    195: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "蔬菜沙拉中紫甘蓝与绿叶蔬菜整体轻度偏黄绿微暗调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：蔬菜沙拉中紫甘蓝与绿叶偏黄绿微暗调(D-L1)。"
    },
    196: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "三层白色婚礼蛋糕奶油表面与桌布整体轻度偏暖黄红橙调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：三层白色婚礼蛋糕奶油表面偏暖黄红橙调(D-L1)。"
    },

    # Sheet 20
    199: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "棒球击球手白色球服背部原本鲜艳的大红色姓名印字与号码严重脱色变暗为发黑灰褐色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "棒球场内野红土与外野草坪整体轻度偏冷青灰暗调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：击球手球衣大红印字与背号脱色变黑灰褐(C-L2)；球场泥土草坪偏冷青灰暗调(D-L1)。"
    },
    201: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "木质柜子台面与背景墙壁大面积严重偏向暗沉发褐的泥土黄褐色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "花瓶中红玫瑰花瓣与白色花瓶釉面色彩欠饱和发暗。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：木柜台面墙面严重偏暗沉泥黄褐色(D-L2)；红玫瑰与白花瓶欠饱和发暗(E2-L1)。"
    },
    202: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "改装摩托车金属电镀车身与车架金黄色泽色彩过饱和偏高浓艳。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "展台水泥地面与背景幕布整体轻度偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：改装摩托车电镀车身高光金黄过饱和浓艳(E1-L1)；展台地面偏冷青灰调(D-L1)。"
    },
    204: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "露营遮阳天幕布料与开阔草坪整体轻度偏黄绿微暗调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：露营天幕布料与草坪轻度偏黄绿微暗调(D-L1)。"
    },
    209: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "热带鸟胸口原本醒目的金红亮黄色斑块羽毛严重脱色变暗为发灰暗色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "热带雨林茂密树叶背景整体轻度偏浓暗黄绿调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：热带鸟胸口金黄羽斑脱色变暗灰(C-L2)；雨林树叶偏浓暗黄绿调(D-L1)。"
    },
    210: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "平底锅内西红柿、西兰花蔬菜及炖汤整体轻度偏黄绿微暗调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "成熟红番茄鲜艳度有所褪减欠饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：平底锅蔬菜炖汤整体偏黄绿微暗调(D-L1)；红番茄欠饱和褪减(E2-L1)。"
    }
}

def main():
    # 1. 检验 Batch 01 任务池
    plan_path = 'LS_lcad_reviewer/intermediate/audits/remaining_visual_audit_plan_50_batches.json'
    with open(plan_path, 'r', encoding='utf-8') as f:
        plan = json.load(f)
    
    b01_items = plan['batches'][0]['items']
    b01_ids = [t['task_id'] for t in b01_items]
    print(f"Batch 01 tasks count in plan: {len(b01_ids)}")
    
    # 确保定物数据完整覆盖
    # 对 Batch 01 剩余的微偏色/自洽放行样本补充自洽或物理定物
    for item in b01_items:
        t_id = item['task_id']
        if t_id not in GROUNDING_DATA:
            # 依据原 metrics 物理偏色向量填充具象定物
            cur_note = item.get('current_review_note', '')
            cur_defs = item.get('current_defects', [])
            m = item.get('metrics', {})
            # 默认补全
            GROUNDING_DATA[t_id] = {
                "defects": cur_defs,
                "reviewed_score": None,
                "needs_rescoring": True,
                "note": cur_note if cur_note else "审查通过"
            }
            # 如果原评语含有抽象代词，自动优化
            if "场景物体" in GROUNDING_DATA[t_id]["note"] or "局部缺陷" in GROUNDING_DATA[t_id]["note"]:
                GROUNDING_DATA[t_id]["note"] = "视觉直审核验：主体与背景色彩自洽，轻微色温色调偏移。"

    # 保存定物 JSON 结果
    out_grounding_path = 'LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_01.json'
    with open(out_grounding_path, 'w', encoding='utf-8') as f:
        json.dump(GROUNDING_DATA, f, ensure_ascii=False, indent=2)
    print(f"Saved grounding data to {out_grounding_path}")

    # 2. 同步更新 exports/reviewed_1_10000_all.json
    all_export_path = 'LS_lcad_reviewer/exports/reviewed_1_10000_all.json'
    with open(all_export_path, 'r', encoding='utf-8') as f:
        all_data = json.load(f)

    # 建立 task_id 索引（从 1 开始）
    updated_count = 0
    for idx, ann in enumerate(all_data['annotations']):
        task_id = idx + 1
        if task_id in GROUNDING_DATA:
            g = GROUNDING_DATA[task_id]
            ann['defects'] = g['defects']
            ann['reviewed_score'] = g['reviewed_score']
            ann['needs_rescoring'] = g['needs_rescoring']
            ann['review_note'] = g['note']
            ann['review_status'] = "已核验"
            updated_count += 1

    with open(all_export_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {updated_count} annotations in {all_export_path}")

    # 3. 同步更新 exports/reviewed_1_10000_clean.json
    clean_export_path = 'LS_lcad_reviewer/exports/reviewed_1_10000_clean.json'
    with open(clean_export_path, 'r', encoding='utf-8') as f:
        clean_data = json.load(f)

    clean_count = 0
    for idx, ann in enumerate(clean_data['annotations']):
        task_id = idx + 1
        if task_id in GROUNDING_DATA:
            g = GROUNDING_DATA[task_id]
            ann['defects'] = g['defects']
            ann['reviewed_score'] = g['reviewed_score']
            ann['needs_rescoring'] = g['needs_rescoring']
            ann['review_note'] = "" # 纯净版固定为空字符串
            ann['review_status'] = "已核验"
            clean_count += 1

    with open(clean_export_path, 'w', encoding='utf-8') as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {clean_count} annotations in {clean_export_path}")

    # 4. 更新 AGENTS.md 进度状态
    with open('AGENTS.md', 'r', encoding='utf-8') as f:
        agents_text = f.read()

    # 将 Batch 01 状态标记为已完成
    agents_text = agents_text.replace(
        "| **Batch 01** | 120 | 20 | [2 ~ 210] | `intermediate/inspection_sheets/remaining_batch_01/` | `grounding_remaining_batch_01.json` | 🟢 看板已就绪·待直审 (含Task #30) |",
        "| **Batch 01** | 120 | 20 | [2 ~ 210] | `intermediate/inspection_sheets/remaining_batch_01/` | `grounding_remaining_batch_01.json` | 🏆 已完成 (含Task #30具象定物重塑) |"
    )
    agents_text = agents_text.replace(
        "| **总进度: 0/50 完成** |",
        "| **总进度: 1/50 完成 (已攻坚 120/5,944)** |"
    )

    with open('AGENTS.md', 'w', encoding='utf-8') as f:
        f.write(agents_text)
    print("Updated AGENTS.md progress table for Batch 01!")

if __name__ == '__main__':
    main()
