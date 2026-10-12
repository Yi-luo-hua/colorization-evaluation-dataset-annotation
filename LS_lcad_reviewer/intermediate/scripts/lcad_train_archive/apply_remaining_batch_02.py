# -*- coding: utf-8 -*-
"""
脚本：Batch 02 视觉大图直审具象定物全量落地与同步
涵盖：Task #213 ~ Task #404 共 120 组任务
重点：
- Task #271, #275, #395: 全域上色失败熔断项 A，锁定 reviewed_score=1.0, needs_rescoring=False
- Task #225, #250, #254, #259, #277, #290, #302, #303, #306, #315, #317, #319, #321, #326, #327, #329, #336, #343, #344, #347, #348, #354, #357, #360, #368, #375, #379, #385, #388, #389, #397, #398, #403, #404: 视觉表现优异，纠偏为零缺陷审查通过放行
- 其余各项严格完成视觉具象定物，指明具体真实物体，彻底消灭抽象代词
"""

import json
import os
import sys

GROUNDING_DATA = {
    # Sheet 01 (Tasks 213, 220, 221, 222, 225, 226)
    213: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "地面下方的草绿色波浪花纹图案被严重错涂为红粉色。"},
            {"id": "B", "name": "溢色", "severity": "L1", "description": "跳跃人物红色服饰及波浪花纹边缘有轻度色彩渗透。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：草绿色波浪花纹图案被错涂为红粉色(C-L2)；红色服饰与花纹边缘轻度溢色(B-L1)。"
    },
    220: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "猫咪后方左侧背景中的青蓝色窗帘墙面被严重褪色变暗为暗褐灰色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "猫咪白色毛皮与暗木色背景交界处色调偏暗沉冷灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：左侧青蓝窗帘墙面严重褪色变暗为暗褐灰(C-L2)；猫咪毛皮边缘色调偏暗冷灰(D-L1)。"
    },
    221: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "餐桌后方白色与灰蓝色背景墙面系统性泛冷青蓝调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "黑白格子桌布上的调味罐与餐具局部饱和度偏低偏灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：背景墙面系统性泛冷青蓝调(D-L1)；桌上调味罐餐具偏灰欠饱和(E2-L1)。"
    },
    222: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "婴儿推车靠垫与安全带织物呈现出刺眼的荧光深蓝与艳紫色，饱和度明显过高浓艳。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：婴儿推车织物靠垫与安全带呈现刺眼荧光深蓝与艳紫色，过度浓艳(E1-L2)。"
    },
    225: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    226: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "两头大象的灰褐色厚皮受冷色调浸染呈现出青灰色，背景热带雨林植被整体轻微偏冷青调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：大象灰褐色厚皮与背景雨林植被整体轻微偏冷青蓝调(D-L1)。"
    },

    # Sheet 02 (Tasks 227, 229, 230, 232, 233, 234)
    227: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "击球网球运动员身穿的鲜艳橙黄色运动球服被完全脱色成灰白无光。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "蓝色硬地网球场地表略显灰暗欠饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：网球运动员橙黄运动服被脱色成灰白(C-L2)；蓝色球场地表偏暗灰(E2-L1)。"
    },
    229: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "打电话男子身穿的淡粉红色长袖衬衫被脱色退化为普通灰白色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "男子面部与后方红砖建筑物边缘轻度偏冷灰暗。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：男子淡粉红长袖衬衫脱色退化为灰白(C-L2)；红砖墙面与肤色偏冷灰暗(D-L1)。"
    },
    230: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "草坪前方鲜红色的“I'M ADOPTED”英文字母标语被完全错涂为暗黄绿色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：“I'M ADOPTED”英文字母标语由正红错涂为暗黄绿色(C-L2)。"
    },
    232: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "左上方原本鲜艳盛开的洋红色花朵被彻底误涂为草绿与暗灰色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "中间装饰小纸伞及泥土地面泛冷青调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：左上方洋红花朵被彻底错涂为草绿暗灰(C-L3)；装饰小纸伞与泥土泛冷青调(D-L1)。"
    },
    233: {
        "defects": [
            {"id": "B", "name": "溢色", "severity": "L1", "description": "白瓷餐盘内的香肠热狗上淋抹的番茄酱在边缘面包接缝处存在轻度溢色渗染。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：香肠热狗上淋抹的番茄酱在面包边缘轻度溢色渗染(B-L1)。"
    },
    234: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "长椅上阅读女子所穿的鲜艳湖蓝色无袖上衣被严重错脱色为暗灰深褐色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "身边放置的蓝色提包同样脱色泛灰，严重缺乏色彩。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：女子湖蓝色无袖上衣严重脱色错变为暗灰深褐色(C-L3)；身边提包脱色泛灰(E2-L2)。"
    },

    # Sheet 03 (Tasks 235, 236, 237, 238, 240, 242)
    235: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "暹罗猫身后的木质橱柜和下方台面木纹被渲染得过度浓艳偏赤橙色，饱和度过高。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：木质橱柜与操作台面木纹过度浓艳偏赤橙色，饱和度偏高(E1-L1)。"
    },
    236: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "笔记本电脑屏幕显示的白色与浅蓝色窗口严重泛黄绿色偏色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白色外接键盘和工作桌面泛冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：笔记本屏幕窗口泛黄绿偏色(D-L1)；外接键盘与桌面泛冷青灰(D-L1)。"
    },
    237: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "象群后方大片热带森林树冠绿意严重萎缩褪色为暗灰绿色，泥水河滩偏灰欠饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：背景森林树冠绿意萎缩褪色为暗灰绿，河滩欠饱和(E2-L1)。"
    },
    238: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "小男孩周围的花丛被渲染出刺眼的荧光粉红与高光翠绿色。"},
            {"id": "B", "name": "溢色", "severity": "L2", "description": "花草高饱和色素大面积越界渗透侵染小男孩的白色衬衫袖口与帽子边缘。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：周围花丛呈刺眼荧光粉红与翠绿(E1-L2)；色素大面积溢出色晕渗透衬衫袖口与帽子(B-L2)。"
    },
    240: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "雪地路口的八角形“STOP”停止交通标志牌鲜红色标面严重暗淡褪色为暗褐红色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：八角形STOP停止标志牌鲜红漆面暗淡褪色为暗褐红(E2-L1)。"
    },
    242: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "北极熊身躯与后背毛皮泛出不自然的暗沉土黄绿色偏色，身下灰色岩石边缘有轻度黄色渗透。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：北极熊身躯毛皮泛不自然土黄绿偏色，岩石边缘有黄色渗透(D-L1)。"
    },

    # Sheet 04 (Tasks 244, 245, 247, 249, 250, 252)
    244: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "木屋客厅内的承重木立柱与天花板横梁暖棕木色减退，整体偏冷青灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：承重木立柱与天花板横梁暖木色减退偏冷青灰(D-L1)。"
    },
    245: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "纸杯蛋糕上方的奶油霜与黄色烘焙纸托边缘轻微泛红，红白格子餐布略微偏洋红紫调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：纸杯蛋糕奶油与纸托边缘轻度泛红，餐布偏洋红紫调(D-L1)。"
    },
    247: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "围栏前小女孩头戴的粉红色遮阳帽被脱色变浅为灰白色，父亲的浅蓝色短袖T恤色彩偏淡。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：小女孩粉红遮阳帽脱色变灰白(C-L2)；父亲浅蓝T恤偏淡欠饱和。"
    },
    249: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "电脑显示器底座及多媒体键盘上方的发光深蓝控制面板被彻底错涂为草绿色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：显示器底座发光深蓝控制面板被错涂为草绿色(C-L2)。"
    },
    250: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    252: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "小女孩身后商场货架上方的深蓝色背景与招牌被严重错涂为草绿色。"},
            {"id": "B", "name": "溢色", "severity": "L1", "description": "手持的意大利香肠披萨表面红酱有轻微溢色渗染。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：商场货架上方深蓝背景招牌错涂为草绿(C-L2)；披萨红酱轻度溢色(B-L1)。"
    },

    # Sheet 05 (Tasks 253, 254, 257, 259, 261, 262)
    253: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "夜间街头原本暖黄色的路灯照明被严重错涂为诡异刺眼的洋红色与紫红色光芒。"},
            {"id": "B", "name": "溢色", "severity": "L2", "description": "路面人行道与路边消防栓被大面积紫红杂光侵染渗透。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：路灯暖黄照明错涂为诡异洋红紫光(C-L2)；路面人行道被大面积紫红杂光侵染渗透(B-L2)。"
    },
    254: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    257: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "广场中央的复古木质时钟亭原本明亮的红色漆面严重褪色剥落为暗褐土灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "时钟亭整体色彩饱和度偏低偏灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：复古时钟亭红色漆面褪色剥落为暗褐土灰(C-L2)；整体欠饱和(E2-L1)。"
    },
    259: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    261: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "餐盘正中央原本鲜黄色的新鲜芒果被严重错涂为鲜艳红粉色。"},
            {"id": "B", "name": "溢色", "severity": "L1", "description": "周围紫色甘蓝沙拉边缘存在轻微色彩溢出渗染。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：餐盘中央鲜黄色芒果严重错涂为鲜粉红(常识错色 C-L3)；紫甘蓝沙拉边缘轻度溢色(B-L1)。"
    },
    262: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "车后座牧羊犬右耳侧面及后颈原本纯净的黑白毛发上出现明显的暗红斑点伪色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "杂色暗红斑点破坏了犬只毛色的整体视觉自然可信度。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：牧羊犬耳侧及后颈纯黑白毛发上出现暗红伪色色斑(C-L2)；破坏视觉自然度(F-L1)。"
    },

    # Sheet 06 (Tasks 265, 269, 271, 273, 275, 277)
    265: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "路口法文八角形“ARRÊT”停止标志牌深红标面严重暗淡褪色。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "下方的明黄色弯道警告箭头牌彻底脱色泛白。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：ARRÊT八角形停止牌红面暗淡褪色(E2-L2)；明黄弯道警告牌彻底脱色泛白(C-L2)。"
    },
    269: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "9462号轨道列车银白车顶与金属车厢外立面泛冷青蓝灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：轨道列车车顶与金属车厢外立面泛冷青蓝灰调(D-L1)。"
    },
    271: {
        "defects": [
            {"id": "A", "name": "缺色", "severity": "", "description": "托盘上原本翠绿的蔬菜沙拉、桌椅与背景窗户全域严重上色失败脱色成近乎纯灰阶黑白图像。"}
        ],
        "reviewed_score": 1.0,
        "needs_rescoring": False,
        "note": "视觉直审具象定物：托盘蔬菜沙拉与背景窗户全域上色失败退化为纯灰阶黑白图像，触发A项缺色熔断，总分锁定1.0分。"
    },
    273: {
        "defects": [
            {"id": "B", "name": "溢色", "severity": "L1", "description": "鸡尾酒会上交谈女士的橙粉色晚礼服及肩颈边缘存在轻度色彩溢出渗透。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：女士橙粉晚礼服及肩颈边缘存在轻度色彩溢出渗透(B-L1)。"
    },
    275: {
        "defects": [
            {"id": "A", "name": "缺色", "severity": "", "description": "海滨路边的双头停车计时表与背景天空、海面全域上色失败脱色成单色灰度图像。"}
        ],
        "reviewed_score": 1.0,
        "needs_rescoring": False,
        "note": "视觉直审具象定物：海滨停车计时表与背景海天全域上色失败退化为单色灰度图像，触发A项缺色熔断，总分锁定1.0分。"
    },
    277: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 07 (Tasks 279, 280, 281, 282, 284, 285)
    279: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "躺在碎花床褥上的猫咪原本暖金黄色的毛皮严重褪色变暗为发灰的冷灰褐色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "猫咪与花床单红色碎花整体色彩饱和度偏低。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：猫咪暖金黄毛皮严重褪色为冷灰褐色(C-L2)；床褥碎花整体偏淡欠饱和(E2-L1)。"
    },
    280: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "草坪合影团队全体成员身穿的鲜艳亮粉红色文化衫严重褪色泛白、欠饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：全体队员鲜亮粉红文化衫大面积褪色泛白、严重欠饱和(E2-L2)。"
    },
    281: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "盘绕白粗麻绳中的金属大剪刀手柄及边缘泛出不自然的黄褐色杂色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：白粗麻绳中金属剪刀把柄及边缘泛不自然黄褐杂色(D-L1)。"
    },
    282: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "烛光晚宴餐桌上花瓶内插置的深紫色鲜花被严重褪色错变为暗灰褐色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：花瓶中深紫色鲜花严重褪色脱落为暗灰褐色(C-L2)。"
    },
    284: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "水塘中的两头黄牛金黄棕色皮毛系统性泛冷偏青灰，失去原本温暖的棕黄色泽。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：两头黄牛金黄棕色皮毛系统性泛冷偏青灰(D-L1)。"
    },
    285: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "运河水面行驶的观光游船顶棚上的红色彩条严重褪色脱落成暗白灰色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：运河游船顶棚鲜艳红色彩条褪色脱落成暗白灰(C-L2)。"
    },

    # Sheet 08 (Tasks 286, 288, 289, 290, 292, 296)
    286: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "窗格后方室内原本强烈的洋红粉紫霓虹灯光被完全脱色还原为平淡灰白光。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "场景整体色彩偏暗淡灰冷。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：窗后室内洋红粉紫霓虹灯光完全脱色为平淡灰白(C-L2)；整体欠饱和(E2-L1)。"
    },
    288: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "铁轨上疾驰的高速列车车头的深蓝漆面与红色警示腰线轻度褪色变暗、欠饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：高速列车车头深蓝漆面与红色警示腰线轻度褪色变暗(E2-L1)。"
    },
    289: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "重型摩托车金属油箱外壳与发动机镀铬构件边缘轻度泛暗红紫光。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：摩托车金属油箱与发动机镀铬边缘轻度泛暗红紫光(D-L1)。"
    },
    290: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    292: {
        "defects": [
            {"id": "B", "name": "溢色", "severity": "L1", "description": "自行车把手部位及深蓝车架与背景石柱交接边缘存在轻度蓝色溢色渗染。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：深蓝自行车车架与把手边缘在背景石柱上有轻度蓝色溢色渗染(B-L1)。"
    },
    296: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "斑马背后的干燥岩石壁阴影与枯木根部被大面积错涂为不合常理的草绿色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：干燥岩石壁阴影与枯木根部被大面积错涂为不合常理的草绿色(C-L2)。"
    },

    # Sheet 09 (Tasks 298, 299, 300, 302, 303, 304)
    298: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "雨夜中女士手撑的翠绿色雨伞被严重错涂为暗沉污浊的黄灰绿色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "伞缘与女士颈部红色围巾色彩偏灰暗欠饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：女士手撑翠绿雨伞错涂为暗沉黄灰绿色(C-L2)；红色围巾欠饱和偏灰(E2-L1)。"
    },
    299: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "滑雪场背景蔚蓝晴空严重褪色发灰失真。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "雪道上游客身上各色滑雪防寒服轻微欠饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：滑雪场背景蔚蓝晴空严重褪色发灰(E2-L2)；游客滑雪服轻度欠饱和(E2-L1)。"
    },
    300: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "餐桌上盛装麦片粥的鲜艳蓝色塑料大碗边缘轻微褪色泛灰、欠饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：盛麦片粥的蓝色塑料大碗边缘轻微褪色泛灰(E2-L1)。"
    },
    302: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    303: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    304: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "餐桌旁大杯冰镇冷饮杯身及其周围阴影泛出不自然的浓重蓝紫色伪色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：大杯冰镇冷饮杯身及周围阴影泛不自然浓重蓝紫色伪色(D-L1)。"
    },

    # Sheet 10 (Tasks 305, 306, 307, 308, 309, 312)
    305: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "棒球场上击球小男孩的深蓝色短裤与球服阴影系统性偏冷青蓝调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：击球小男孩深蓝短裤与球服阴影系统性偏冷青蓝调(D-L1)。"
    },
    306: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    307: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "右侧肉牛原本温润油亮的红棕色皮毛及耳朵上的红色耳标轻微褪色暗淡。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：肉牛红棕皮毛及红色耳标轻度褪色暗淡(D-L1)。"
    },
    308: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "海滨灯塔与飞翔海鸥背景深邃蔚蓝的天空与海水大面积褪色泛白、严重欠饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：海滨灯塔背景蔚蓝天空与海水大面积褪色泛白、严重欠饱和(E2-L2)。"
    },
    309: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "斑马围栏背景中的绿色灌木及黄色干燥土地整体略显泛灰暗淡，轻度偏暖黄调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：斑马围栏背景灌木与黄土地整体偏灰暗淡，轻度偏暖黄调(D-L1)。"
    },
    312: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "远方起伏的高原山脉及天际线受冷紫色偏色侵染泛出不自然的紫蓝调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：远方高原山脉与天际线受冷紫色侵染泛不自然紫蓝调(D-L1)。"
    },

    # Sheet 11 (Tasks 313, 315, 316, 317, 319, 321)
    313: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "厨房木质橱柜表面及右侧窗帘布艺被严重错涂为刺眼违和的冷青蓝色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：厨房木质橱柜与窗帘被严重错涂为刺眼冷青蓝色(常识错色 C-L3)。"
    },
    315: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    316: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街边历史建筑米黄色砖石外墙与窗台木构严重褪色漂白为苍白无光的死白色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：历史建筑米黄色砖石外墙严重褪色漂白为苍白死白(E2-L2)。"
    },
    317: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    319: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    321: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 12 (Tasks 326, 327, 329, 333, 334, 335)
    326: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    327: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    329: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    333: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "猎犬戏水奔跑的清澈浅绿海湾水域被彻底错涂为浑浊泛黄的泥浆水色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：清澈浅绿海湾水域被彻底错涂为浑浊泛黄泥浆水色(常识错色 C-L2)。"
    },
    334: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "水面上游泳的小狗周围原本泛着生机绿意的清澈湖水被褪色错变为暗灰蓝色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "湖水整体色彩偏暗灰、欠饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：清澈湖水褪色错变为暗灰蓝色(C-L2)；水面整体欠饱和(E2-L1)。"
    },
    335: {
        "defects": [
            {"id": "B", "name": "溢色", "severity": "L1", "description": "盘中胡萝卜精细雕刻的宝塔造型边缘及层叠凹槽处存在轻度橙色溢色渗染。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：胡萝卜雕刻宝塔边缘存在轻度橙色溢色渗染(B-L1)。"
    },

    # Sheet 13 (Tasks 336, 338, 339, 340, 341, 343)
    336: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    338: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "沙滩冲浪场景背景原本灰蓝的海面与低云天空被严重错涂为青绿色调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：原本灰蓝的海面与低云天空被严重错涂为青绿色调(常识错色 C-L2)。"
    },
    339: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "路边小吃摊位手绘美食招牌“FROG LEGS”与“ZUCCHINI”的荧光彩字色彩过于浓艳刺眼。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：手绘美食招牌荧光彩字色彩过于浓艳刺眼(E1-L1)。"
    },
    340: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "土崖上方原本澄澈蔚蓝的天空被严重错涂为草绿色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：土崖上方蔚蓝天空被严重错涂为草绿色(常识错色 C-L3)。"
    },
    341: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "盘中热压三明治夹层的烤肉馅料色彩过度浓艳发红。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：热压三明治夹层烤肉馅料色彩过度浓艳发红(E1-L1)。"
    },
    343: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 14 (Tasks 344, 346, 347, 348, 351, 353)
    344: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    346: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "门前停放的前卫造型流线型跑车车体由鲜艳樱桃红色被彻底错涂为暗黄绿色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：跑车流线型车体由鲜艳樱桃红被彻底错涂为暗黄绿(常识错色 C-L3)。"
    },
    347: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    348: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    351: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "铁道枢纽道岔区周边的大片茂密绿化树林严重褪色暗淡变灰，绿意大面积丧失。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：铁道枢纽周边绿化树林大面积褪色暗淡变灰(E2-L2)。"
    },
    353: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "夜间街头左上方深蓝色夜空被错涂为黄白色。"},
            {"id": "B", "name": "溢色", "severity": "L1", "description": "路边红色消防栓边缘受黄色路灯光溢色渗染。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：夜空被错涂为黄白色(C-L2)；红色消防栓边缘受黄色路灯光溢色渗染(B-L1)。"
    },

    # Sheet 15 (Tasks 354, 357, 358, 359, 360, 361)
    354: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    357: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    358: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "烤盘上的烘烤披萨芝士表面及木质托盘边缘系统性泛暖红偏色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：烘烤披萨芝士表面及木质托盘边缘系统性泛暖红偏色(D-L1)。"
    },
    359: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "草地上铺垫的鲜艳深蓝色野餐毛毯严重褪色暗淡变灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：深蓝色野餐毛毯严重褪色暗淡变灰(C-L2)。"
    },
    360: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    361: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "赛马场领跑骑师身穿的鲜红色赛马比赛服被严重错涂为暗青灰蓝色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：领跑骑师鲜红比赛服被严重错涂为暗青灰蓝色(常识错色 C-L3)。"
    },

    # Sheet 16 (Tasks 362, 363, 364, 366, 367, 368)
    362: {
        "defects": [
            {"id": "B", "name": "溢色", "severity": "L1", "description": "队列中军人所穿的城市蓝色迷彩服高光部位及肩颈边缘存在明显荧光蓝紫色溢色渗染。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：军人城市蓝色迷彩服高光部位存在荧光蓝紫溢色渗染(B-L1)。"
    },
    363: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "水面上漂浮浮木周围原本清亮碧绿的湖水被严重褪色变暗为发灰的暗蓝色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：清亮碧绿湖水被严重褪色变暗为发灰暗蓝色(C-L2)。"
    },
    364: {
        "defects": [
            {"id": "B", "name": "溢色", "severity": "L1", "description": "酒吧内举杯饮酒女子的面部肤色及身旁男子手持的玻璃酒杯边缘存在轻度杂色溢出。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：饮酒女子面部及玻璃酒杯边缘存在轻度杂色溢出(B-L1)。"
    },
    366: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "厨房微波炉黑色镜面门框与金属控制面板边缘轻微泛冷青蓝偏色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：微波炉镜面门框与金属控制面板边缘轻微泛冷青蓝偏色(D-L1)。"
    },
    367: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "蛋糕餐盘左上方背景中原本淡黄色的餐巾纸被严重错涂为刺眼的荧光粉红色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：背景中淡黄色餐巾纸被严重错涂为刺眼荧光粉红色(常识错色 C-L2)。"
    },
    368: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 17 (Tasks 369, 373, 375, 376, 377, 379)
    369: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "稀树草原上原本广阔干燥的金黄色草甸被严重错涂为暗青绿色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：旱季金黄色草甸被严重错涂为暗青绿色(常识错色 C-L2)。"
    },
    373: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "水泥桥墩街头涂鸦作品中原本鲜艳浓烈的橙红与青蓝色大色块严重脱色褪白为暗淡水泥灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：街头涂鸦原本浓烈的橙红与青蓝色块严重脱色褪白为暗淡水泥灰(E2-L3)。"
    },
    375: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    376: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "街边停靠的复古机车油箱与前后挡泥板的鲜红金属漆面轻度褪色暗淡。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：复古机车鲜红金属油箱与挡泥板漆面轻度褪色暗淡(E2-L1)。"
    },
    377: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "滑板场背景悬挂的“ELECTRIC”闪电标志旗帜原本黑白冷峻的色调被严重错涂为发暗的黄绿泥褐色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：“ELECTRIC”闪电标志大旗被错涂为暗发黄绿泥褐色(C-L2)。"
    },
    379: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 18 (Tasks 380, 383, 384, 385, 386, 387)
    380: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "两位女孩身后的木质书架阴影及门框背景轻微偏冷青蓝调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：书架阴影及门框背景轻微偏冷青蓝调(D-L1)。"
    },
    383: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "水中给大象冲凉的训象师所穿的深蓝色长袖上衣被严重褪色脱落成浅灰白色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：训象师深蓝色长袖上衣被严重褪色脱落成浅灰白色(C-L2)。"
    },
    384: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "剪彩仪式后方观礼人群衣物与活动背景色调普遍褪色偏灰、欠饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：剪彩仪式后方观礼人群衣物普遍褪色偏灰欠饱和(E2-L1)。"
    },
    385: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    386: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "小男孩躺卧的背景丁香紫色毛毯颜色偏深浓艳，且在泰迪熊玩偶边缘存在轻度冷紫溢色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：背景丁香紫毛毯颜色过深浓艳，且在小熊玩偶边缘存在冷紫溢色(D-L1)。"
    },
    387: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "海滨渔村石屋旁停靠的木质渔船船体深蓝色漆面轻度褪色暗淡。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：木质渔船船体深蓝色漆面轻度褪色暗淡(E2-L1)。"
    },

    # Sheet 19 (Tasks 388, 389, 390, 391, 395, 397)
    388: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    389: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    390: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "小牛嬉戏后方原本深绿色的围栏林木背景被严重错涂为红棕深褐色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：小牛后方深绿色围栏林木被严重错涂为红棕深褐色(常识错色 C-L2)。"
    },
    391: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "宇航员太空漫步背景中地球弧线原本深邃纯蓝的大气边缘被错涂为青黄浑浊色调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：地球弧线原本深蓝大气层边缘被错涂为青黄浑浊色调(C-L2)。"
    },
    395: {
        "defects": [
            {"id": "A", "name": "缺色", "severity": "", "description": "滑雪运动员身上原本鲜艳的红黄蓝比赛服与背景松林全域上色失败退化为纯黑白单色灰度图像。"}
        ],
        "reviewed_score": 1.0,
        "needs_rescoring": False,
        "note": "视觉直审具象定物：滑雪运动员红黄蓝比赛服全域上色失败退化为纯黑白灰阶，触发A项缺色熔断，总分锁定1.0分。"
    },
    397: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 20 (Tasks 398, 400, 401, 402, 403, 404)
    398: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    400: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "花瓶中插放的大蓬冬青植物原本鲜红色的浆果被严重错涂为发灰的橙黄枯褐色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：冬青植物鲜红浆果被严重错涂为发灰橙黄枯褐色(常识错色 C-L2)。"
    },
    401: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "草坪中央的老式金属消防栓深红漆面轻微暗淡褪色、欠饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：金属消防栓深红漆面轻微暗淡褪色欠饱和(E2-L1)。"
    },
    402: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "展翅翱翔的海鸟背景原本澄澈湛蓝的天空被严重错涂为泛灰暗草绿色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：海鸟背景蔚蓝天空被严重错涂为泛灰暗草绿色(常识错色 C-L2)。"
    },
    403: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    404: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    }
}

def main():
    print(f"[INFO] Batch 02 包含 {len(GROUNDING_DATA)} 个任务的具象定物配置。")
    assert len(GROUNDING_DATA) == 120, f"Expected 120 tasks, got {len(GROUNDING_DATA)}"

    # 1. 保存中间定物文件
    grounding_path = "LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_02.json"
    with open(grounding_path, "w", encoding="utf-8") as f:
        json.dump(GROUNDING_DATA, f, ensure_ascii=False, indent=2)
    print(f"[PASS] 具象定物字典已保存至: {grounding_path}")

    # 2. 读取 exports/reviewed_1_10000_all.json 并进行落地更新
    all_path = "LS_lcad_reviewer/exports/reviewed_1_10000_all.json"
    clean_path = "LS_lcad_reviewer/exports/reviewed_1_10000_clean.json"

    with open(all_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    with open(clean_path, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    updated_count = 0
    clean_updated_count = 0

    # 建立映射以 task_id 进行安全替换
    for ann in all_data["annotations"]:
        tid = ann.get("human_review", {}).get("task_id")
        if tid in GROUNDING_DATA:
            g = GROUNDING_DATA[tid]
            ann["defects"] = g["defects"]
            ann["review_note"] = g["note"]
            ann["reviewed_score"] = g["reviewed_score"]
            ann["needs_rescoring"] = g["needs_rescoring"]
            ann["review_status"] = "已核验"
            updated_count += 1

    for ann in clean_data["annotations"]:
        tid = ann.get("human_review", {}).get("task_id")
        if tid in GROUNDING_DATA:
            g = GROUNDING_DATA[tid]
            ann["defects"] = g["defects"]
            ann["review_note"] = ""  # 纯净版严格清空备注
            ann["reviewed_score"] = g["reviewed_score"]
            ann["needs_rescoring"] = g["needs_rescoring"]
            ann["review_status"] = "已核验"
            clean_updated_count += 1

    assert updated_count == 120, f"Expected 120 all annotations updated, got {updated_count}"
    assert clean_updated_count == 120, f"Expected 120 clean annotations updated, got {clean_updated_count}"

    with open(all_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"[PASS] {all_path} 成功更新 120 条定物任务！")

    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"[PASS] {clean_path} 成功更新 120 条定物任务！")

if __name__ == "__main__":
    main()
