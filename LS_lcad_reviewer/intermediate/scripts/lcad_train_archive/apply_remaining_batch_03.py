# -*- coding: utf-8 -*-
"""
脚本：Batch 03 视觉大图直审具象定物全量落地与同步
涵盖：Task #405 ~ Task #945 共 120 组任务
重点：
- 放行纠偏：36 组任务视觉表现优异、真实自然，纠偏为零缺陷审查通过放行 (defects=[])
- 具象定物：84 组任务严格完成视觉多模态直审与具象定物，指明真实物体名称，彻底消灭抽象代词
"""

import json
import os
import sys

GROUNDING_DATA = {
    # Sheet 01 (Tasks 405, 406, 407, 408, 410, 411)
    405: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "孔雀蓝运动背心色彩偏浅微泛灰，后方铁丝网与草坪背景轻微偏冷青蓝调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：孔雀蓝背心偏浅微灰，后方铁丝网与草坪偏冷青调(D-L1)。"
    },
    406: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "充气玩具棒球棒原本鲜红色被彻底错涂为反常荧光黄绿色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "右侧露营帐篷与周围草地色彩明显褪色泛灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：充气玩具棒球棒由鲜红错涂为荧光黄绿(C-L3)；右侧帐篷褪色泛灰(E2-L2)。"
    },
    407: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    408: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    410: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "列车车厢车门红色警示色块暗淡褪色，站台路面黄色安全线色彩变淡偏灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：列车车门红色色块暗淡褪色，站台黄色安全线偏灰(E2-L2)。"
    },
    411: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "列车原本深酒红色机车头车身涂装被彻底剥落脱色为单调的灰白色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：列车深酒红色车头涂装被彻底脱色为灰白色(C-L3)。"
    },

    # Sheet 02 (Tasks 412, 413, 414, 416, 418, 419)
    412: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "八角形ALTO西班牙语停止牌鲜红色牌面暗淡褪色为暗红褐色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：ALTO停止牌鲜红面暗淡褪色为暗褐红(E2-L1)。"
    },
    413: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    414: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    416: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "水面游弋的白天鹅羽毛阴影受水波反光浸染明显泛冷青蓝偏色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：白天鹅背羽阴影受水波反光浸染泛冷青蓝偏色(D-L1)。"
    },
    418: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "游行集会人群手持的亮黄色Prop 8宣传标语牌轻微欠饱和偏淡。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：游行人群手持亮黄色宣传标语牌轻微欠饱和偏淡(E2-L1)。"
    },
    419: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "街角商铺门头原本深蓝色遮阳棚与门面招牌被严重错涂为草绿色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：商铺深蓝色遮阳棚与招牌错涂为草绿(C-L2)。"
    },

    # Sheet 03 (Tasks 421, 422, 423, 425, 426, 428)
    421: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    422: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "棒球场草坪地表轻微偏冷青蓝调，白色球服背后53号红字背号略显暗淡。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：草坪轻度偏冷青调，白色球服背后53号红字略显暗淡(D-L1)。"
    },
    423: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "雨中小巷两侧商铺招牌与遮雨布色彩欠饱和褪色偏灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：雨中小巷商铺各色彩招牌与遮雨布欠饱和褪色偏灰(E2-L1)。"
    },
    425: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "古典高层建筑原本受夕阳照耀的温暖金黄立面被错涂为阴暗冷灰调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "建筑立面与街景饱和度严重缺失发灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：古典高层建筑夕阳暖金立面褪色变为阴冷灰调(C-L2, E2-L2)。"
    },
    426: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "小狗嘴中叼着的亮橙色胡萝卜磨牙胶棒严重褪色为灰土黄色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：小狗嘴叼亮橙色胡萝卜磨牙胶棒褪色为灰土黄色(E2-L1)。"
    },
    428: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "烤披萨饼面上原本鲜红浓郁的番茄酱与意大利香肠片严重脱色变为灰暗肉色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "披萨配料整体缺乏红润色泽，发灰暗淡。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：披萨鲜红番茄酱与香肠片脱色发灰(C-L2, E2-L2)。"
    },

    # Sheet 04 (Tasks 430, 431, 436, 437, 438, 439)
    430: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "窗台木框与餐桌木纹温润红棕色褪变为冷灰青调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "室内盆栽绿植叶片欠饱和偏灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：窗台木框与餐桌红棕木色偏冷灰青(D-L1)；盆栽叶片欠饱和偏灰(E2-L1)。"
    },
    431: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    436: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "木桩上猎隼背羽油亮棕褐色褪色发灰，晴朗蓝天大面积褪色泛白。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：猎隼油亮棕褐背羽褪色发灰，蓝天大面积脱色泛白(E2-L2)。"
    },
    437: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "大象母子厚皮被过度浓艳渲染为赤黄褐色，色彩饱和度偏高。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：大象母子灰褐厚皮被过度渲染为浓艳赤黄褐色(E1-L1)。"
    },
    438: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "女士原本纯正深蓝色的商务西装外套被严重错涂为暗灰深褐色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：女士深蓝色西装外套被错涂为暗灰深褐色(C-L2)。"
    },
    439: {
        "defects": [
            {"id": "B", "name": "溢色", "severity": "L1", "description": "小女孩手持手工塑料花枝的绿色花茎与粉红花瓣边缘有轻度色彩渗透。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：女孩手持塑料花茎与粉红花瓣边缘轻度溢色(B-L1)。"
    },

    # Sheet 05 (Tasks 442, 443, 444, 445, 446, 447)
    442: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "极限飞盘防守队员身穿的深蓝色运动短裤被严重错涂为草绿色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：飞盘防守队员深蓝色短裤错涂为草绿(C-L2)。"
    },
    443: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "河流背景中的芦苇灌木与水面倒影色彩过度浓艳发暖黄。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：大象戏水河道后方芦苇草丛过度浓艳偏暖黄(E1-L1)。"
    },
    444: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    445: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    446: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "滑雪者纯白色滑雪羽绒外套与针织保暖帽被严重错涂为刺眼的荧光亮橙黄色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：滑雪者纯白羽绒服与针织帽严重错涂为刺眼亮橙黄(C-L3)。"
    },
    447: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "大草原斑马背景中湛蓝天空大面积褪色泛白、严重欠饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：草原斑马背景蔚蓝天空大面积褪色泛白欠饱和(E2-L2)。"
    },

    # Sheet 06 (Tasks 448, 449, 450, 453, 455, 457)
    448: {
        "defects": [
            {"id": "B", "name": "溢色", "severity": "L1", "description": "花瓶中明黄色与艳红色羽毛干花边缘有轻度色彩扩散渗透。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：花瓶中明黄与艳红羽毛干花边缘轻度溢色(B-L1)。"
    },
    449: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    450: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "游船船舷上的亮橙红救生圈轻微褪色暗淡，背景林木欠饱和偏冷灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：游船船舷亮橙红救生圈暗淡褪色，背景林木欠饱和(E2-L1)。"
    },
    453: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "骑马队伍中前排骑手的深蓝色外衣色彩略显暗淡褪色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：骑手深蓝色服饰轻度褪色变暗、欠饱和(E2-L1)。"
    },
    455: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    457: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "卧室窗台上的盆栽绿叶与窗外树木枝叶被错涂为暗沉草绿色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：窗台盆栽绿叶及窗外树冠错涂为暗草绿(C-L2)。"
    },

    # Sheet 07 (Tasks 459, 464, 465, 467, 469, 471)
    459: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "吃披萨男子后方原本偏冷的柜台与背景墙面泛轻微暖黄红偏色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：后方蓝色柜台与背景墙面泛轻微暖黄偏色(D-L1)。"
    },
    464: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    465: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "铁路两侧原本金黄绚丽的秋季草甸大面积脱色褪白为冷灰土色，严重欠饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：铁路转弯线两侧金黄秋季草甸严重脱色褪白为冷灰土色(E2-L3)。"
    },
    467: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "客厅小女孩原本鲜艳的粉红色长袖上衣褪色变浅泛白。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：小女孩原本鲜艳粉红长袖上衣褪色变浅欠饱和(E2-L1)。"
    },
    469: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "切片苹果原本鲜亮的正红色果皮被严重错涂为暗沉橙黄褐色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：切片苹果鲜亮正红果皮错涂为暗橙黄褐(C-L2)。"
    },
    471: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "雨天行人群体手撑的亮红与明黄雨伞伞面色彩略显暗淡褪色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：雨天行人各色雨伞（鲜红与明黄伞面）暗淡褪色(E2-L1)。"
    },

    # Sheet 08 (Tasks 475, 477, 479, 480, 481, 483)
    475: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    477: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "红发女士浅绿色长袖上衣色彩变淡泛灰、欠饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：红发女士浅绿长袖上衣褪色变浅泛灰(E2-L1)。"
    },
    479: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "亮黄双翼飞机停放的机库地面与后方金属卷帘门被严重错涂为草绿色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：亮黄飞机下方机库地面与卷帘门错涂为草绿(C-L2)。"
    },
    480: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    481: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "快餐桌背景墙面与男子深色西服整体偏冷青灰色调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：背景墙面与深色西装偏冷青灰色调(D-L1)。"
    },
    483: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 09 (Tasks 485, 486, 492, 496, 497, 499)
    485: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "背景墙悬挂海报的鲜红色相框边条严重脱色发灰。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "相框红色油漆饱和度严重缺失。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：海报鲜红相框边条严重脱色泛灰白(C-L2, E2-L1)。"
    },
    486: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "圆顶钟楼背景湛蓝天空大面积脱色褪白，饱和度严重不足。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：圆顶钟楼背景深邃蔚蓝天空大面积褪色变白(E2-L2)。"
    },
    492: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    496: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    497: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "果盘中黄苹果表皮色彩过于浓艳刺眼，饱和度偏高。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：果盘黄苹果表皮过度浓艳呈荧光感(E1-L1)。"
    },
    499: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 10 (Tasks 514, 524, 528, 543, 545, 565)
    514: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    524: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    528: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    543: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    545: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "极限滑雪者脚踩的双板滑雪板被渲染出刺眼的荧光亮蓝色，色彩过饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：极限滑雪者脚下滑雪双板呈刺眼荧光亮蓝(E1-L2)。"
    },
    565: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 11 (Tasks 573, 587, 590, 608, 615, 621)
    573: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    587: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    590: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "街角红色施工警示牌（MASON ST CLOSED）鲜红底色褪色暗淡变黑褐。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：街角红色施工警示牌鲜红底色褪色暗淡变黑褐(E2-L1)。"
    },
    608: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "卫生间白色瓷砖墙面与白瓷洗手水槽呈现明显暖黄偏色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：卫生间白色瓷砖墙面与水槽呈现暖黄偏色(D-L1)。"
    },
    615: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "金发小女孩身后的室内背景墙面及阴影轻微泛暖偏色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：室内背景墙面及阴影轻微泛暖偏色(D-L1)。"
    },
    621: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "草地上拉伸运动的女子深色运动上衣与袖套被严重错涂为反常的浅粉紫色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：草地上拉伸女子的深色运动上衣被错涂为浅粉紫(C-L3)。"
    },

    # Sheet 12 (Tasks 628, 640, 648, 649, 652, 655)
    628: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "庭院蓝色木质长椅与男子牛仔裤色彩浓艳，饱和度偏高。"},
            {"id": "B", "name": "溢色", "severity": "L1", "description": "木长椅蓝色边缘轻度侵染扩散至周边木板。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：庭院蓝木长椅与牛仔裤浓艳过饱和(E1-L1)，木椅蓝色轻度溢色(B-L1)。"
    },
    640: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L3", "description": "网球场清澈蔚蓝的天空大面积严重泛黄绿浑浊偏色。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "网球场地表原本蓝绿硬地被严重错涂为紫红褐色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：网球场蔚蓝天空严重泛黄绿浑浊偏色(D-L3)；场地表错涂为紫红褐(C-L2)。"
    },
    648: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "晚宴正装合影中人物面部肤色受暗光影响轻度泛红暖偏色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：晚宴正装合影人物面部肤色轻度泛红暖偏色(D-L1)。"
    },
    649: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "办公室电脑显示器屏幕原本明亮纯正的亮蓝色严重脱色泛白发灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：电脑显示器屏幕明亮纯正亮蓝严重脱色泛白发灰(E2-L2)。"
    },
    652: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    655: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "椅子上猫咪背部的淡灰褐色斑纹被错涂为过浓的红棕焦黄色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：椅子上猫咪背部淡灰褐斑纹错涂为过浓红棕焦黄色(C-L2)。"
    },

    # Sheet 13 (Tasks 656, 657, 666, 671, 672, 677)
    656: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "雨中撑伞男子原本清新的浅浅果绿色Polo短袖被彻底褪色错涂为灰白色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：男子浅果绿Polo短袖彻底褪色错涂为灰白色(C-L2)。"
    },
    657: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    666: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "简陋卫生间的水泥墙面与白色马桶洁具略显泛暖黄偏色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：水泥墙面与白色马桶洁具略显泛暖黄偏色(D-L1)。"
    },
    671: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "停靠的面包车车顶及侧面车身被异常错涂附着红褐色斑块。"},
            {"id": "B", "name": "溢色", "severity": "L1", "description": "车身红色杂斑边缘有轻度溢色渗透。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：面包车车顶及车身被错涂附着红褐斑块(C-L2)，边缘轻度溢色(B-L1)。"
    },
    672: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "复古老照片场景中上方天空被上色为淡青蓝色，与原片整体暖黄褐旧照色调存在偏差。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：复古老照片天空淡青蓝与原片暖黄褐老照片色调偏差(D-L1)。"
    },
    677: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 14 (Tasks 679, 687, 707, 708, 721, 727)
    679: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "街边摊位左下角木箱与杂物原本的暖红木色褪色暗淡变灰黑。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：街边摊位左下角木箱暖红木色褪色变暗发灰黑(E2-L1)。"
    },
    687: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "仓鼠身后的室内背景软包沙发翠绿反光略显不自然。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：背景软包沙发翠绿反光略显不自然(D-L1)。"
    },
    707: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "北极熊全身毛发严重泛荧光黄绿偏色。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "北极熊原本白中带微黄毛皮被错涂为荧光黄绿色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：北极熊全身毛发被严重错涂为反常刺眼荧光黄绿(D-L2, C-L2)。"
    },
    708: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    721: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "白色冰箱表面张贴的彩色照片与便签纸张色彩饱和度不足、略显褪色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：冰箱表面张贴彩色照片与便利贴纸色彩变淡褪色(E2-L1)。"
    },
    727: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "木质浴室木板墙与小烛光氛围被大面积偏染为暗红紫色调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：木质浴室木板墙与烛光氛围被严重偏染为暗红紫调(D-L2)。"
    },

    # Sheet 15 (Tasks 729, 738, 740, 742, 763, 770)
    729: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    738: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "足球场颠球男子的黑色运动夹克局部被错涂渲染为浅青紫色杂斑。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：颠球男子黑色运动夹克局部错涂为浅青紫杂斑(C-L2)。"
    },
    740: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    742: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "重型多轴卡车车轮轮毂上的鲜红色装饰圈彻底褪色脱落为灰褐色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：多轴卡车车轮轮毂鲜红装饰圈彻底脱色为灰褐色(C-L2)。"
    },
    763: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "自动步道上黑色行李箱正面的明黄色拉链饰条严重脱色泛白变浅灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：行李箱正面明黄拉链饰条严重脱色泛白变浅灰(E2-L2)。"
    },
    770: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "面包摊位红白遮阳棚下方的货架阴影区域轻微偏冷蓝暗调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：面包摊位货架阴影区域轻微偏冷蓝暗调(D-L1)。"
    },

    # Sheet 16 (Tasks 773, 778, 780, 790, 799, 802)
    773: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "公交站牌身后的粉红橙色建筑外墙被严重错涂为发灰的青绿冷调。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "建筑外墙整体严重偏冷青灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：公交站牌后粉红橙建筑外墙错涂为发灰青绿冷调(C-L2, D-L2)。"
    },
    778: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    780: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "手持香蕉的男子面部肤色被过度偏染为不自然的粉红紫红色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：手持香蕉男子面部肤色被过度偏染为粉红紫红色(D-L2)。"
    },
    790: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "高速公路龙门架上的标准墨绿色指路交通路牌被严重错涂为暗红褐色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：高速公路龙门架墨绿指路路牌错涂为暗红褐色(C-L2)。"
    },
    799: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "豪华浴室墙面瓷砖与镜框大面积偏染为暗哑冷灰青调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "浴室环境光色严重发灰失真、欠饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：浴室墙面瓷砖与镜框大面积偏染为暗哑冷灰青调(D-L2, E2-L2)。"
    },
    802: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "塑料小剪刀手柄原本鲜亮的宝蓝色彻底褪色脱白变灰。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "小剪刀手柄色彩饱和度彻底丧失。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：塑料小剪刀手柄原本宝蓝色彻底褪色脱白变灰(C-L2, E2-L2)。"
    },

    # Sheet 17 (Tasks 814, 818, 821, 823, 829, 846)
    814: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "特写男子的面部与耳廓肤色略显苍白泛青灰、欠缺自然血色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：特写男子面部与耳廓肤色略显苍白泛青灰(D-L1)。"
    },
    818: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    821: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "果树枝头的成熟橙子色彩过于深红浓艳，饱和度偏高。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：果树枝头成熟橙子色彩过度深红浓艳(E1-L1)。"
    },
    823: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "天台后方原本醒目亮黄色的塑料蓄水箱被错涂褪色为暗哑土灰粉色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：天台后方醒目亮黄塑料蓄水箱错涂褪色为土灰粉色(C-L2)。"
    },
    829: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "街头行走的商务男子原本深邃纯正的海军蓝西服套装被严重错涂为暗哑灰褐色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：商务男子深邃纯正海军蓝西装外套错涂为暗哑灰褐色(C-L2)。"
    },
    846: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "雪地羊群身后深邃冷蓝色的夜空背景被严重偏染为浑浊暗红棕褐色。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "纯净夜空冷蓝色被严重错涂为暗红褐色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：雪地羊群身后冷蓝夜空严重错涂偏染为浑浊暗红棕褐色(D-L2, C-L2)。"
    },

    # Sheet 18 (Tasks 852, 875, 880, 891, 892, 894)
    852: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "男子嘴中咬着的塑料牙刷上的宝蓝色刷毛被彻底脱色退化为灰白色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "塑料牙刷刷毛色彩饱和度严重丢失。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：咬着的塑料牙刷宝蓝刷毛彻底脱色退化为灰白色(C-L2, E2-L2)。"
    },
    875: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "笔记本电脑液晶显示屏幕轻微偏冷青蓝调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：笔记本电脑屏幕轻微偏冷青蓝色调(D-L1)。"
    },
    880: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    891: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    892: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "红酒瓶身左侧的室内墙面与高光反光被过度偏染为浓重焦黄色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：红酒瓶身左侧室内墙面与反光被过度偏染为浓重焦黄色(D-L2)。"
    },
    894: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "两只幼年北极熊身后的苔原草地被过度渲染为刺眼浓艳的青翠绿色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：北极熊身后的苔原草地过度渲染为刺眼浓艳青翠绿(E1-L2)。"
    },

    # Sheet 19 (Tasks 901, 902, 904, 908, 909, 916)
    901: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "客厅沙发上摆放的鲜艳青绿色布艺抱枕被错涂褪色为暗黑灰青色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：客厅沙发鲜艳青绿抱枕错涂褪色为暗黑灰青色(C-L2)。"
    },
    902: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "双层观光巴士车身侧面红色饰条与车头黄色线路牌色彩饱和度略显偏淡。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：双层巴士车身红色饰条与车头黄色线路牌轻度欠饱和(E2-L1)。"
    },
    904: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "手腕上原本浅黄米白色的手环饰品被错涂为亮翠绿色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：手腕原本浅黄米白手环被错涂为亮翠绿色(C-L2)。"
    },
    908: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "单门电冰箱侧面原本明亮纯正的天蓝色漆面被彻底脱色退化为单调灰白色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：单门电冰箱侧面天蓝漆面彻底脱色退化为单调灰白色(C-L3)。"
    },
    909: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "卧室窗台上摆放的鲜艳洋红紫色玻璃花瓶饰品脱色褪化为暗黑色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：窗台鲜艳洋红紫玻璃花瓶饰品脱色褪化为暗黑色(C-L2)。"
    },
    916: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "坡道滑板少年短袖上衣、小狗毛色及背景树林大面积严重脱色泛白。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "原本鲜艳的粉紫色短袖T恤退化为单调浅灰白色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：滑板少年粉紫短袖上衣及背景树林严重脱色泛白(E2-L3, C-L2)。"
    },

    # Sheet 20 (Tasks 922, 925, 927, 932, 934, 945)
    922: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    925: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "系泊小木船周围的海水水体色彩轻微泛灰、饱和度稍显不足。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：小木船周围海水色彩轻微泛灰、饱和度稍显不足(E2-L1)。"
    },
    927: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    932: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "稀疏荒原草甸上的白灰色马匹被严重错涂为红棕栗色马。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：稀疏草甸上的白灰色马匹被严重错涂为红棕栗色马(C-L2)。"
    },
    934: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "50欧元纸币票面原本经典的暖橙黄色大面积褪色泛白变灰。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "钞票黄色油墨大面积脱色发灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：50欧元纸币经典暖橙黄票面大面积褪色泛白变灰(C-L2, E2-L2)。"
    },
    945: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    }
}


def main():
    print(f"[INFO] Batch 03 包含 {len(GROUNDING_DATA)} 个任务的具象定物配置。")
    assert len(GROUNDING_DATA) == 120, f"Expected 120 tasks, got {len(GROUNDING_DATA)}"

    # 1. 保存中间定物文件
    grounding_path = "LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_03.json"
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
