# -*- coding: utf-8 -*-
"""
脚本：Batch 05 视觉大图直审具象定物全量落地与同步
涵盖：Task #1118 ~ Task #1251 共 120 组任务
重点：
- 放行纠偏：62 组任务视觉表现优异、真实自然，纠偏为零缺陷审查通过放行 (defects=[])
- 具象定物：58 组任务严格完成视觉多模态直审与具象定物，指明真实物体名称，彻底消灭抽象代词
"""

import json
import os
import sys

GROUNDING_DATA = {
    # Sheet 01 (Tasks 1118, 1119, 1120, 1121, 1122, 1123)
    1118: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "卫生间原本温暖舒适的暖黄色灯光与米黄瓷砖墙面被彻底错涂为冰冷生硬的青灰冷调。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "暖色调照明氛围完全丢失，被错涂为惨白偏冷色调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：卫生间暖黄灯光被彻底错涂为冰冷生硬的青灰冷调(D-L2, C-L2)。"
    },
    1119: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "树枝上小鸟背景原本翠绿繁茂的树叶虚化光斑被严重错涂为反常的明亮天蓝色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：树枝上小鸟背景原本翠绿的树叶虚化光斑被错涂为明亮天蓝(C-L2)。"
    },
    1120: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1121: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "炒锅中原本清脆碧绿的青椒豆荚被彻底错涂为熟透的橙红色与焦黄色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：炒锅中清脆碧绿的青椒豆荚被彻底错涂为熟透的橙红焦黄色(C-L3)。"
    },
    1122: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "休息区温馨浓郁的暖黄壁灯与落地灯光晕完全丢失，被大面积错涂为冰冷单调的白炽荧光冷光。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "原本温暖舒适的室内光照环境错涂为生硬惨白冷光。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：休息区温馨暖黄壁灯光晕丢失，被错涂为单调白炽冷光(D-L2, C-L2)。"
    },
    1123: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "岸边背双肩包男子身后的树林与河水呈现偏冷青绿调。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "双肩包防雨罩出现反常浅蓝伪色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：岸边背双肩包男子身后的树林与河水偏冷青绿调(D-L1, C-L1)。"
    },

    # Sheet 02 (Tasks 1124, 1125, 1126, 1127, 1128, 1129)
    1124: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "草坪放风筝场景上空的层状阴云呈现偏暖黄灰褐色，清冷蓝灰色调减弱。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "远处天际线与草坪色彩略显褪色发干。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：草坪放风筝场景上空阴云呈现偏暖黄灰褐色(D-L1, E2-L1)。"
    },
    1125: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1126: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1127: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "餐厅通往厨房的门廊墙面与天花板略显偏暖浅粉黄调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：餐厅通往厨房的门廊墙面略显偏暖浅粉黄调(D-L1)。"
    },
    1128: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1129: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 03 (Tasks 1130, 1131, 1132, 1133, 1134, 1135)
    1130: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1131: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1132: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1133: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "小狗脖颈项圈上的红黄彩色花纹略显褪色泛冷青。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "犬用编织项圈色彩艳丽度有所下降。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：小狗脖颈项圈上的红黄彩色花纹略显褪色泛冷青(D-L1, E2-L1)。"
    },
    1134: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1135: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "浓郁巧克力蛋糕表层的淋酱与切面海绵蛋糕略显偏红褐色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：浓郁巧克力蛋糕淋酱与切面略显偏红褐色(D-L1)。"
    },

    # Sheet 04 (Tasks 1136, 1137, 1138, 1139, 1140, 1141)
    1136: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1137: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内滑板场原木碗池与拱形墙面暖光褪色，整体呈现偏冷暗灰调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "木质滑板碗池表面纹理色彩明显泛灰暗淡。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：室内滑板场原木碗池与拱形墙面偏冷暗灰调(D-L1, E2-L1)。"
    },
    1138: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1139: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "卫生间台盆区域温暖的金黄暖光氛围彻底丢失，被错涂为冰冷单调的灰白冷光。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：卫生间台盆区域金黄暖光彻底丢失被错涂为灰白冷光(D-L2)。"
    },
    1140: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "双层翻糖蛋糕背景桌布与后方布帘绿色略显暗淡偏灰。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "绿色桌布饱和度下降偏暗。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：双层翻糖蛋糕背景桌布与后方布帘绿色略暗淡偏灰(D-L1, E2-L1)。"
    },
    1141: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 05 (Tasks 1142, 1143, 1144, 1145, 1146, 1147)
    1142: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "斑马群黑白斑纹中的白色皮毛略显偏洋红紫光泽，草坪局部色调偏暖。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：斑马群黑白斑纹中的白色皮毛略显偏洋红紫光泽(D-L1)。"
    },
    1143: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1144: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "废弃微波炉所在房间原本清冷的青绿荧光环境被大面积错涂偏染为暗红褐色。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "地面与墙面冷色调荧光完全被浑浊暗红替代。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：微波炉所在房间原本清冷的青绿荧光错涂偏染为暗红褐色(D-L1, C-L2)。"
    },
    1145: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1146: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1147: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "路边消防栓原本明黄色的底座套环与凸起部位被彻底脱色错涂为纯白灰底。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "底座黄色油漆完全丧失原有饱和度。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：路边消防栓原本明黄色的底座套环脱色错涂为纯白灰底(C-L2, E2-L2)。"
    },

    # Sheet 06 (Tasks 1148, 1149, 1150, 1151, 1152, 1153)
    1148: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "草坪旁红色消防栓下方的石砾花坛与周围草坪色彩略微偏黄。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：草坪旁红色消防栓下方的石砾花坛与草坪略微偏黄(D-L1)。"
    },
    1149: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1150: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "盛放烤鸡腿餐盘外围的木质餐桌与垫布被错涂偏染为冷淡的青蓝灰色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "餐桌原本温馨的原木色调出现冷青偏色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：烤鸡腿餐盘外围木餐桌被错涂偏染为冷淡青蓝灰色(C-L2, D-L1)。"
    },
    1151: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1152: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "厨房岛台旁年轻女性穿着的翠绿色短袖上衣色彩过度浓艳微过饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：厨房岛台旁女性身穿的翠绿色上衣色彩过度浓艳微过饱和(E1-L1)。"
    },
    1153: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 07 (Tasks 1154, 1155, 1158, 1159, 1160, 1161)
    1154: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "道路立交桥上方开阔天空大面积褪色泛白发灰，高架桥广告牌色彩略显暗淡。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "晴朗天际边缘略带灰黄偏色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：立交桥上方天空大面积褪色泛白发灰(E2-L1, D-L1)。"
    },
    1155: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "商铺玻璃陈列柜内展示厨具与木质展架温暖黄光丢失，显现偏冷青灰调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "陈列架色彩暗淡泛灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：商铺陈列柜内厨具展架温暖黄光丢失显偏冷青灰调(D-L1, E2-L1)。"
    },
    1158: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "山坡草甸原本干枯金黄的秋季草地被大面积错涂为深绿色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：山坡草甸原本干枯金黄的草地被错涂为深绿色(C-L2)。"
    },
    1159: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1160: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1161: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "卧室内双人床原本清新的浅蓝色床单与被褥被严重脱色错涂为泛黄暗米色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "床铺区域整体偏染泛黄暗色调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：卧室双人床原本浅蓝床单被褥脱色错涂为泛黄暗米色(C-L2, D-L1)。"
    },

    # Sheet 08 (Tasks 1162, 1163, 1164, 1165, 1166, 1167)
    1162: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1163: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "书房整面原木书架与书桌木质表面色彩略微偏冷偏灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：书房原木书架与书桌木质表面色彩略偏冷偏灰(D-L1)。"
    },
    1164: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1165: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1166: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1167: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 09 (Tasks 1168, 1169, 1170, 1172, 1173, 1174)
    1168: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1169: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "越野车挡风玻璃前方的荒原原野与远方大象风景暖金光芒丢失，显现偏冷青灰调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "原野草木色泽暗淡欠饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：车窗前荒原与远方大象暖金光芒丢失显偏冷青灰调(D-L1, E2-L1)。"
    },
    1170: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "蓝天下飞扑飞盘的年轻女性面部与手臂肤色略显偏暖泛红。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：蓝天下飞扑飞盘的女性面部与手臂肤色略偏暖泛红(D-L1)。"
    },
    1172: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "混凝土阶梯步道与采光天窗整体呈现轻微偏黄绿调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：混凝土阶梯步道与采光天窗整体呈现轻微偏黄绿调(D-L1)。"
    },
    1173: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1174: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "室内网球场原本蓝灰色的硬地球场地表被错涂为红土网球场色调。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "后方教练短袖上衣被错涂为荧光亮绿色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：网球场硬地错涂为红土色(C-L2)，后方教练上衣错涂为荧光亮绿(C-L2)。"
    },

    # Sheet 10 (Tasks 1175, 1177, 1178, 1180, 1181, 1182)
    1175: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1177: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内坐着的青年男子面部肤色与浅色衬衫领口略微偏暖泛红。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：青年男子面部肤色与衬衫领口略微偏暖泛红(D-L1)。"
    },
    1178: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1180: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "电脑书桌桌面与地毯原本温暖的暖木色调完全脱色退化为冰冷青灰调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "办公椅与桌面色彩褪色变暗。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：电脑书桌与地毯原本暖木色调完全脱色退化为冰冷青灰调(D-L1, E2-L1)。"
    },
    1181: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1182: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "汽车车窗外原本晴朗蔚蓝的开阔晴空被严重错涂为浑浊焦黄色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "路旁绿树偏暗泛黄褐色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：车窗外晴朗蔚蓝晴空错涂为浑浊焦黄(C-L2)，路旁绿树泛黄褐(D-L2)。"
    },

    # Sheet 11 (Tasks 1184, 1185, 1186, 1187, 1188, 1189)
    1184: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1185: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1186: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1187: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "男子身后原本鲜艳的大红色背景墙面被严重脱色错涂为暗灰青色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "背景墙面完全失去原有的红色饱和度。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：男子身后鲜艳大红色背景墙面被脱色错涂为暗灰青色(C-L2, E2-L2)。"
    },
    1188: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1189: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "静物油画中玻璃广口瓶内的液体与倒影被错涂为偏暖红褐色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：静物油画中玻璃广口瓶内的液体与倒影错涂为偏暖红褐(C-L2)。"
    },

    # Sheet 12 (Tasks 1190, 1191, 1192, 1193, 1194, 1195)
    1190: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "草坪上腾空扑跃的宠物犬金黄色毛发严重褪色泛白变灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "犬只原本浓密金黄的被毛呈现灰白暗哑。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：腾空扑跃的宠物犬金黄色毛发严重褪色泛白变灰(E2-L1, C-L1)。"
    },
    1191: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1192: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "历史建筑前停放的古董红色马车车厢与木质车轮色彩略显偏深红焦黄。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：古董红色马车车厢与木质车轮略偏深红焦黄(D-L1)。"
    },
    1193: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1194: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "天台放风筝场景原本绚烂温暖的黄昏落日余晖天空被彻底错涂为灰冷阴天。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "落日余晖金色霞光完全丢失。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：天台放风筝场景原本绚烂温暖的黄昏落日天空错涂为灰冷阴天(D-L2, C-L2)。"
    },
    1195: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 13 (Tasks 1196, 1198, 1202, 1203, 1204, 1205)
    1196: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "街头自行车拖车广告牌顶部的醒目红色横幅文字大面积褪色变浅。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：自行车拖车广告牌顶部的醒目红色横幅文字褪色变浅(E2-L1)。"
    },
    1198: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "金发小女孩身穿的暖橘红色上衣色彩褪色泛浅，伴侣犬毛色偏暗偏冷。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "小女孩服饰与室内光照温暖感减弱。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：小女孩暖橘红上衣褪色泛浅，伴侣犬毛色偏暗偏冷(D-L1, E2-L1)。"
    },
    1202: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1203: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1204: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "餐厅原本浓郁温暖的金黄暖光氛围彻底丢失，木质餐边柜与墙面错涂为冰冷生硬的青灰冷调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：餐厅温暖金黄暖光彻底丢失，餐边柜与墙面错涂为冰冷青灰冷调(D-L2)。"
    },
    1205: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 14 (Tasks 1206, 1207, 1208, 1209, 1210, 1211)
    1206: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1207: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "餐厅餐桌玻璃甜点罐与红酒杯周围温馨暖光氛围减弱，呈现暗沉灰冷调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "甜点草莓酱与餐桌反光色彩暗淡。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：餐桌玻璃甜点罐与红酒杯周围温馨暖光减弱呈暗沉灰冷调(D-L1, E2-L1)。"
    },
    1208: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "冲浪海面原本清澈翠绿的翡翠色海浪被严重脱色错涂为浑浊暗淡的灰白色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "海水浪花完全失去原有清澈翠绿生机。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：冲浪海面原本清澈翠绿的海浪脱色错涂为浑浊暗淡灰白(C-L3, E2-L2)。"
    },
    1209: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "睡猫依偎的复古扶手椅原本浓郁温暖的酒红色天鹅绒靠背被大面积脱色退化为暗褐灰色。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "扶手椅天鹅绒红色调彻底丢失被置换为单调冷灰褐。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：复古扶手椅酒红天鹅绒靠背大面积脱色退化为暗褐灰(E2-L3, C-L2)。"
    },
    1210: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1211: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "面包甜品店柜台后方烘焙师面部与背景陈列架色彩略偏冷泛淡。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：面包甜品店烘焙师面部与背景陈列架色彩略偏冷泛淡(D-L1)。"
    },

    # Sheet 15 (Tasks 1212, 1213, 1214, 1215, 1217, 1218)
    1212: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1213: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1214: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1215: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "金属托盘中清洗的荧光绿海绵与紫色刷毛色彩略有偏色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：金属托盘中清洗的荧光绿海绵与紫色刷毛色彩略有偏色(D-L1)。"
    },
    1217: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1218: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "餐盘中原本鲜艳亮橙色的烤南瓜/红薯切片被严重错涂为浅粉肉粉色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：餐盘中亮橙色烤南瓜红薯切片被严重错涂为浅粉肉色(C-L3)。"
    },

    # Sheet 16 (Tasks 1219, 1220, 1221, 1222, 1223, 1224)
    1219: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "生日蜡烛烛光与俯身吹蜡烛人物面部被过度渲染为浓艳刺眼的血红焦黄。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "桌面与背景偏染深红。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：生日蜡烛与吹蜡烛人物面部过度渲染为刺眼血红焦黄(E1-L2, D-L1)。"
    },
    1220: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1221: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "海滩上海鸥栖息的沙地与枯木色彩偏冷暗，沙滩黄色暖感偏弱。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：海滩上海鸥栖息的沙地与枯木偏冷暗沙滩暖感弱(D-L1)。"
    },
    1222: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "儿童游戏桌周围的地面与墙壁略显偏暖浅黄色调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：儿童游戏桌周围地面与墙壁略显偏暖浅黄色调(D-L1)。"
    },
    1223: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1224: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 17 (Tasks 1225, 1226, 1227, 1228, 1229, 1230)
    1225: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1226: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "临河钟楼建筑上方的阴天暮空被大面积错涂偏染为浓重粉红色晚霞。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "河面与云层原本冷静的灰蓝暮色被替换为戏剧化粉红偏色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：临河钟楼上方阴天暮空大面积错涂偏染为浓重粉红晚霞(D-L2, C-L2)。"
    },
    1227: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1228: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1229: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "电力机车车头原本深绿色的车身涂装严重脱色退化为暗灰米色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "机车绿色喷漆完全丧失原有饱和色彩。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：电力机车车头原本深绿色的车身涂装脱色退化为暗灰米色(C-L2, E2-L2)。"
    },
    1230: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "雨夜潮湿路面上原本暖橙色的汽车灯光倒影被严重错涂为刺眼的荧光亮青蓝色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：雨夜潮湿路面暖橙色车灯倒影被严重错涂为刺眼荧光青蓝(C-L3)。"
    },

    # Sheet 18 (Tasks 1231, 1232, 1233, 1234, 1235, 1236)
    1231: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1232: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "吉祥物毛绒大熊身穿的标志性明黄色短袖T恤被严重错涂为反常的湖水青蓝色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：吉祥物毛绒大熊明黄色T恤被严重错涂为湖水青蓝色(C-L3)。"
    },
    1233: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "网球场原本草绿色的球场地表被严重错涂为红褐色地表。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：网球场原本草绿色的球场地表被严重错涂为红褐色地表(C-L2)。"
    },
    1234: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1235: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "圆形烧烤架上烘烤的香肠色泽偏暗红焦黄，周围草坪绿色略有减弱。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "肉肠光泽略显暗淡。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：烧烤架上香肠偏暗红焦黄周围草坪绿色减弱(D-L1, E2-L1)。"
    },
    1236: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 19 (Tasks 1237, 1239, 1240, 1242, 1243, 1244)
    1237: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1239: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1240: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1242: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1243: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1244: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 20 (Tasks 1245, 1246, 1247, 1248, 1250, 1251)
    1245: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1246: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "棒球场内野红土泥土地表与投手丘色彩略显偏黄，泥土红褐色调略有减弱。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：棒球场内野红土泥土地表与投手丘略偏黄红褐感减弱(D-L1)。"
    },
    1247: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "长颈鹿身体深褐斑块与身后砖石墙面色彩略显偏暖泛黄。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：长颈鹿深褐斑块与身后砖石墙面色彩略偏暖泛黄(D-L1)。"
    },
    1248: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "盛放披萨与调味瓶的餐桌台面原本清冷的灰蓝色被错涂为大面积草绿偏黄调。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "餐桌整体明显偏草绿暖色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：盛放披萨餐桌台面灰蓝色错涂为大面积草绿偏黄调(C-L2, D-L2)。"
    },
    1250: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "刚出炉披萨表面点缀的香草碎末绿色褪色，番茄酱与奶酪略显偏洋红暗色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "披萨配料香草绿色明显暗淡。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：刚出炉披萨香草绿色褪色番茄酱与奶酪偏洋红暗色(D-L1, E2-L1)。"
    },
    1251: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "准备儿童餐点托盘中的天蓝色烘焙硅胶模具杯被严重错涂为鲜艳的粉紫色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：托盘中天蓝色烘焙硅胶模具杯被严重错涂为鲜艳粉紫色(C-L3)。"
    }
}

def main():
    base_dir = r"d:\学业文件\MCL\上色评价_数据集标注\LS_lcad_reviewer"
    audit_out_path = os.path.join(base_dir, "intermediate", "audits", "grounding_remaining_batch_05.json")
    all_export_path = os.path.join(base_dir, "exports", "reviewed_1_10000_all.json")
    clean_export_path = os.path.join(base_dir, "exports", "reviewed_1_10000_clean.json")

    print(f"[*] 正在保存 Batch 05 具象定物映射至: {audit_out_path}")
    with open(audit_out_path, "w", encoding="utf-8") as f:
        json.dump(GROUNDING_DATA, f, ensure_ascii=False, indent=2)
    print(f"[+] 成功保存 {len(GROUNDING_DATA)} 条具象定物记录！")

    # 统计数据
    pass_count = sum(1 for v in GROUNDING_DATA.values() if not v["defects"])
    ground_count = len(GROUNDING_DATA) - pass_count
    print(f"[*] 统计分布: 放行纠偏 {pass_count} 例, 具象定物改判 {ground_count} 例")

    # 同步更新 reviewed_1_10000_all.json
    print(f"[*] 正在同步更新: {all_export_path}")
    with open(all_export_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    updated_all = 0
    for ann in all_data["annotations"]:
        tid = ann.get("human_review", {}).get("task_id")
        if tid in GROUNDING_DATA:
            g = GROUNDING_DATA[tid]
            ann["defects"] = g["defects"]
            ann["review_status"] = "已核验"
            ann["reviewed_score"] = g["reviewed_score"]
            ann["needs_rescoring"] = g["needs_rescoring"]
            ann["review_note"] = g["note"]
            updated_all += 1

    with open(all_export_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"[+] reviewed_1_10000_all.json 更新完成，匹配写入 {updated_all} 条记录！")

    # 同步更新 reviewed_1_10000_clean.json
    print(f"[*] 正在同步更新: {clean_export_path}")
    with open(clean_export_path, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    updated_clean = 0
    for ann in clean_data["annotations"]:
        tid = ann.get("human_review", {}).get("task_id")
        if tid in GROUNDING_DATA:
            g = GROUNDING_DATA[tid]
            ann["defects"] = g["defects"]
            ann["review_status"] = "已核验"
            ann["reviewed_score"] = g["reviewed_score"]
            ann["needs_rescoring"] = g["needs_rescoring"]
            ann["review_note"] = ""  # 纯净版保持空字符串
            updated_clean += 1

    with open(clean_export_path, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"[+] reviewed_1_10000_clean.json 更新完成，匹配写入 {updated_clean} 条记录！")

if __name__ == "__main__":
    main()
