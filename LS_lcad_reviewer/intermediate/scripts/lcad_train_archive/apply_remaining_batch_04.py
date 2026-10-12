# -*- coding: utf-8 -*-
"""
脚本：Batch 04 视觉大图直审具象定物全量落地与同步
涵盖：Task #947 ~ Task #1117 共 120 组任务
重点：
- 放行纠偏：48 组任务视觉表现优异、真实自然，纠偏为零缺陷审查通过放行 (defects=[])
- 具象定物：72 组任务严格完成视觉多模态直审与具象定物，指明真实物体名称，彻底消灭抽象代词
"""

import json
import os
import sys

GROUNDING_DATA = {
    # Sheet 01 (Tasks 947, 948, 958, 963, 964, 965)
    947: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "红棕栗色马匹毛色过于鲜亮浓艳，背部与颈部高光区域红色偏重。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：红棕栗色马匹毛色过度浓艳赤红(E1-L2)。"
    },
    948: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    958: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    963: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "星巴克抹茶星冰乐透明塑料杯内的翠绿色饮品彻底脱色退化为苍白奶黄色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：星巴克抹茶绿星冰乐被脱色退化为奶黄色(C-L3)。"
    },
    964: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "机场候机大厅大理石地砖与白色支撑立柱色彩略显偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：候机大厅地砖与白色立柱略偏冷青灰色(D-L1)。"
    },
    965: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "人行道旁金属自动售报机的明黄色与正红色金属漆面略显褪色暗淡。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：人行道旁自动售报机黄色与红色漆面略显褪色暗淡(E2-L1)。"
    },

    # Sheet 02 (Tasks 970, 979, 991, 998, 1001, 1002)
    970: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "十字路口八角形红色停步交通标志牌牌面红色略微褪色变暗。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：街头八角形STOP红色标志牌面略显暗淡褪色(E2-L1)。"
    },
    979: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    991: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    998: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "昏暗餐室内交谈男子的面部肤色与背景木质墙壁略显泛黄褐色偏色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：昏暗餐室内男子肤色与背景木质墙壁略显泛黄褐(D-L1)。"
    },
    1001: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "网球场原本红褐色的红土球场地表严重脱色错涂为灰米白色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "球场看台塑料座椅与防风网色彩明显褪色变浅。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：网球场红土球场地表严重脱色褪白为灰米色(C-L2)，看台塑料椅褪色(E2-L2)。"
    },
    1002: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L3", "description": "公园清澈晴朗的湛蓝天空被大面积错涂为浑浊的灰绿偏黄色调。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "公园木质长椅与树荫区域严重泛焦黄色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：晴朗天空大面积错涂为浑浊绿黄偏色(D-L3)，长椅泛焦黄(C-L2)。"
    },

    # Sheet 03 (Tasks 1003, 1004, 1005, 1006, 1007, 1008)
    1003: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1004: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1005: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "自行车后座装载的大捆新鲜青香蕉被严重错涂为熟透的暗焦黄色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：自行车后座装载的大捆青香蕉被严重错涂为暗焦黄色(C-L3)。"
    },
    1006: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "卫生间白色陶瓷洗手盆与瓷砖墙面略微泛暗冷灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：卫生间白色陶瓷洗手盆与瓷砖墙面略泛暗冷灰调(D-L1)。"
    },
    1007: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1008: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 04 (Tasks 1009, 1010, 1011, 1012, 1013, 1014)
    1009: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "洗手间化妆镜反射区域与墙角阴影色彩略微偏冷青灰调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：洗手间化妆镜反光与墙角阴影略微偏冷青灰(D-L1)。"
    },
    1010: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1011: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1012: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1013: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "内燃机车车头正面的防撞醒目亮黄色涂装被严重错涂为暗沉的深蓝黑色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：列车车头亮黄色防撞涂装被严重错涂为深蓝色(C-L2)。"
    },
    1014: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "航模滑翔机原本洁白的流线型机身与红色机翼尖端被彻底错涂为刺眼的荧光黄绿色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：洁白机身与红色翼尖的滑翔机被彻底错涂为荧光黄绿色(C-L3)。"
    },

    # Sheet 05 (Tasks 1015, 1016, 1017, 1018, 1019, 1020)
    1015: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1016: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1017: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1018: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "西装小男孩胸前佩戴的红白斜条纹领带中红色条纹略显褪色暗淡。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：小男孩红白条纹领带中红色部分明显褪色暗淡(E2-L1)。"
    },
    1019: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "棒球场看台观众身穿的纽约大都会队标志性亮橙色球衣被彻底脱色退化为苍白灰白色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：看台观众标志性亮橙色球迷球衣被彻底脱色为灰白色(C-L3)。"
    },
    1020: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "夜间滑雪场原本由高压钠灯照耀的金黄暖色雪道被渲染为冰冷死寂的灰白色调。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "雪道两侧的暖黄色照明灯光大面积丢失被错涂为惨白冷光。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：夜场滑雪道暖黄钠灯光芒错涂为惨白夜色(D-L2, C-L2)。"
    },

    # Sheet 06 (Tasks 1021, 1022, 1023, 1024, 1025, 1026)
    1021: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "训鹰人手臂上站立的野生灰褐色猛禽猎鹰被荒谬错涂为金黄头顶与宝蓝色羽毛的热带鹦鹉。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：灰褐色猎鹰被荒谬错涂为黄顶宝蓝羽鹦鹉(C-L3)。"
    },
    1022: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "餐桌金属刀叉反光与周围桌布阴影色彩略显偏冷青灰暗淡。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：披萨餐桌金属刀叉与周围桌布阴影略微偏冷青灰(D-L1)。"
    },
    1023: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1024: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "盛放午餐的塑料托盘原本纯正的天蓝色彻底脱色错涂为浅灰白色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "托盘与配餐纸巾整体色彩明显欠饱和发灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：午餐塑料托盘天蓝色彻底脱色为浅灰白(C-L2, E2-L2)。"
    },
    1025: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1026: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "城市黄昏天际线上方深邃的冷蓝色暮光被大面积偏染为暗红褐色。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "冷蓝色晚霞天空大面积错涂为浑浊暗褐调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：深冷青蓝暮色晚霞大面积错涂偏染为暗红褐色(D-L2, C-L2)。"
    },

    # Sheet 07 (Tasks 1027, 1028, 1029, 1030, 1031, 1032)
    1027: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "沙滩上放风筝男子身穿的深蓝色短袖T恤被错涂为暗沉无光泽的黑褐色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：放风筝男子深蓝色T恤错涂为暗黑褐色(C-L2)。"
    },
    1028: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "工业货运仓库水泥地面与卡车装卸平台整体大面积偏染紫红与黄褐色调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：货运装卸车间水泥地面与卡车整体偏染紫红与黄褐色(D-L2)。"
    },
    1029: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1030: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "陶土花盆中种植的新鲜翠绿针叶松柏盆景被严重错涂为干枯病态的暗紫褐色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：陶土花盆中翠绿针叶小松柏被严重错涂为暗紫褐色(C-L2)。"
    },
    1031: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1032: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "现代厨房中双门电冰箱的侧面喷漆被过度渲染为浓艳刺眼的荧光亮粉色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：双门电冰箱侧面喷漆过度渲染为浓艳刺眼的荧光亮粉色(E1-L2)。"
    },

    # Sheet 08 (Tasks 1033, 1034, 1035, 1036, 1037, 1038)
    1033: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "野生动物保护区斑马身后原本茂密繁盛的深绿色树木灌木被大面积严重错涂为干枯的暗红褐色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：斑马身后背景繁茂绿树大面积被严重错涂为暗红褐色(C-L3)。"
    },
    1034: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "棒球场背景墙上鲜艳纯正的深蓝色赞助商广告挡板彻底脱色错涂为深黑灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "场边挡板区域完全丧失原有饱和色彩，退化为死板单色灰度。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：棒球场背景深蓝色广告挡板彻底脱色退化为单调暗黑灰色(C-L3, E2-L3)。"
    },
    1035: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1036: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1037: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "繁华街头标志性的亮黄色出租车车身被严重错涂并褪色为暗淡的冷灰蓝色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：街头亮黄色出租车被严重错涂褪色为暗冷灰蓝色(C-L3)。"
    },
    1038: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "厨房整体木质橱柜表面与操作台面被大面积严重偏染为浓重刺眼的焦黄橘橙色调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：厨房木质吊柜与料理台面大面积偏染为刺眼焦黄橘橙色(D-L2)。"
    },

    # Sheet 09 (Tasks 1039, 1040, 1042, 1043, 1045, 1046)
    1039: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "足球场边观赛教练身穿的鲜艳大红色保暖羽绒服被严重错涂褪色为暗灰蓝色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：球场边教练鲜红羽绒服被严重错涂褪色为暗灰蓝色(C-L2)。"
    },
    1040: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "翻盖手机外屏数码时钟原本清爽的荧光青蓝色数字界面被错涂为浑浊的橙红色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：手机外屏数码时钟清爽青蓝数字界面被错涂为浑浊橙红(C-L2)。"
    },
    1042: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "住宅卫生间洁白干净的陶瓷抽水马桶座圈与洗脸陶瓷水盆被荒唐错涂为鲜艳的粉红色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：卫生间纯白陶瓷马桶座与洗脸水池被荒谬错涂为粉红色(C-L3)。"
    },
    1043: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "小女孩双手翻花绳翻飞的编织细绳色彩略显暗淡欠饱和。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：小女孩手中翻飞的彩线细绳略显暗淡褪色(E2-L1)。"
    },
    1045: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "面包甜点烘焙坊内工作人员身穿的暗色工作服被错涂为反常的浅天蓝色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：面包甜品店内工作人员工作服被错涂为浅天蓝色(C-L2)。"
    },
    1046: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "篮球赛场上贴身防守球员身穿的鲜艳正红色运动球衣被彻底脱色错涂为死气沉沉的暗灰紫黑色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：防守球员鲜艳正红运动球衣被严重脱色错涂为暗灰紫黑色(C-L3)。"
    },

    # Sheet 10 (Tasks 1047, 1048, 1049, 1050, 1052, 1053)
    1047: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1048: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "自习阅览室天花板悬挂的锥形吊灯灯罩天蓝色表面色彩略显泛白褪色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：阅读室天花板锥形吊灯灯罩天蓝色表面略显泛白变浅(E2-L1)。"
    },
    1049: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "雨中过马路行人撑开的醒目明黄色大雨伞伞面被严重错涂为浅粉紫色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：雨天街头行人的明黄色大雨伞被严重错涂为浅粉紫色(C-L2)。"
    },
    1050: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1052: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1053: {
        "defects": [
            {"id": "B", "name": "溢色", "severity": "L1", "description": "伫立在大象背部的洁白牛背鹭头顶与羽冠处边缘轻微受到背景杂色溢色侵染浅黄。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：大象背部纯白牛背鹭羽冠处受背景溢色轻度侵染浅黄(B-L1)。"
    },

    # Sheet 11 (Tasks 1054, 1055, 1056, 1058, 1059, 1060)
    1054: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1055: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1056: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "与羊驼互动女性原本鲜艳夺目的桃粉色短袖T恤被严重错涂为灰暗脏污的暗灰绿色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：女子原本鲜艳夺目的桃粉色T恤被严重错涂为暗灰绿色(C-L3)。"
    },
    1058: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "海滨沙滩上遮蔽烈日的大红色遮阳伞大伞面被彻底脱色错涂为干枯暗哑的灰绿色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：沙滩大红色遮阳伞伞面被彻底脱色错涂为干枯灰绿色(C-L3)。"
    },
    1059: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "道路上方安装的红灯禁止掉头交通标识牌原本规范的纯白反光底色被错涂为明黄色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：红灯禁止掉头标识牌纯白反光底色被错涂为明黄色(C-L2)。"
    },
    1060: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 12 (Tasks 1061, 1062, 1063, 1064, 1065, 1066)
    1061: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "开放式厨房与客厅交界处的白色天花板及走廊墙面略微泛暗冷灰蓝调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：厨房与客厅交界处天花板与墙面略泛暗冷灰蓝调(D-L1)。"
    },
    1062: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1063: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "荒野枯木上栖息的两只秃鹫原本油亮深棕褐色的背部羽毛彻底脱色错涂为苍白的浅灰白色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "猛禽羽翼与枯树干色彩严重欠饱和发灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：两只秃鹫深棕褐色背羽脱色错涂为苍白浅灰白色(C-L2, E2-L2)。"
    },
    1064: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "口中咬着新鲜切片橙子的年轻女性面部受光肤色略显泛洋红偏色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：咬着橙子切片的女士面部肤色略显泛洋红偏色(D-L1)。"
    },
    1065: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1066: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 13 (Tasks 1069, 1070, 1071, 1072, 1073, 1074)
    1069: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1070: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1071: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "夜幕降临的十字路口上方清冷深青色的天空被偏染为浑浊的暗灰褐色。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "晚霞暮空错涂为泛黄偏褐夜色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：路口深冷青色暮空错涂偏染为暗灰褐色(D-L1, C-L2)。"
    },
    1072: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "手持黑莓全键盘商务手机原本深黑色的全黑机身面板与边缘按键被错涂为反常的紫粉色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：黑莓手机纯黑色面板与按键边框被错涂为反常紫粉色(C-L2)。"
    },
    1073: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1074: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 14 (Tasks 1075, 1076, 1077, 1078, 1079, 1080)
    1075: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "卫生间洗漱台镜面金属水龙头反光与背景白色瓷砖被大面积严重偏染为浓重刺眼的焦黄色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：洗漱台金属水龙头反光与背景瓷砖严重偏染为浓重焦黄(D-L2)。"
    },
    1076: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1077: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "采光窗台原木窗框与窗帘折痕阴影色彩略显偏深红暗沉。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：窗台原木窗框与窗帘折痕阴影略微偏深红暗沉(D-L1)。"
    },
    1078: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1079: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "复古艺术照片中原本浓烈温暖的红色环境溢光被彻底脱色退化为冰冷死板的灰白色。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "整幅画面的暖红色调氛围彻底丢失被错置为冷灰基调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：复古艺术照片中浓郁温暖红光彻底脱色退化为冷死灰白(E2-L3, C-L2)。"
    },
    1080: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 15 (Tasks 1081, 1082, 1083, 1084, 1085, 1086)
    1081: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1082: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "室内窗台玻璃花瓶外原本晴朗蔚蓝的开阔天空严重脱色泛白发灰。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "窗外风景与窗框阴影呈现轻微偏灰白冷色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：窗台花瓶身后的晴朗蓝天严重脱色泛白变灰(E2-L2, D-L1)。"
    },
    1083: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "古典街头红色立柱大钟上方的湛蓝天空大面积褪色泛白变浅。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：红色街钟上方湛蓝天空大面积褪色泛白变浅(E2-L1)。"
    },
    1084: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1085: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "新鲜出炉烤披萨表面涂抹的浓郁番茄红酱与烤香肠片过度渲染为刺眼的荧光粉红色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：烤披萨表面番茄酱与香肠片过度渲染为荧光粉红(E1-L2)。"
    },
    1086: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "暗室中笔记本发光屏幕原本投射在眼镜男子面部的荧光青冷蓝光被错涂为浑浊焦黄色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：暗室中屏幕投射在男子面部的荧光青冷光芒被错涂为焦黄(C-L2)。"
    },

    # Sheet 16 (Tasks 1087, 1088, 1089, 1090, 1092, 1093)
    1087: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "雨天汽车挡风玻璃透出的林荫街道场景与远方建筑整体略带偏冷青绿调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：雨中车窗外的林木与街道场景整体略偏冷青绿调(D-L1)。"
    },
    1088: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1089: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1090: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1092: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1093: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "日式榻榻米餐厅竹编草席与矮餐桌底部的阴影区域略显偏染暗红洋红色调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：日式餐厅榻榻米草席与餐桌阴影略显偏染暗红洋红(D-L1)。"
    },

    # Sheet 17 (Tasks 1094, 1095, 1096, 1097, 1098, 1099)
    1094: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1095: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "牧场围栏边特写白绵羊的面部皮肤、眼圈与耳鼻毛皮被大面积偏染为冰冷死灰青蓝色。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "羊头粉嫩自然的肤色被错涂为冷青灰色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：白绵羊面部与耳鼻毛皮被大面积偏染错涂为死灰青蓝(D-L2, C-L2)。"
    },
    1096: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "双层客运列车车窗下方原本醒目亮丽的橙黄色外壳涂装被彻底脱色退化为苍白灰白色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：客运列车车窗下方橙黄色外壳涂装彻底脱色为灰白色(C-L3)。"
    },
    1097: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1098: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "在展厅交谈的左侧男子身穿的深蓝色夹克外套及背部阴影略显偏暗偏紫褐色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：展厅左侧男子深蓝夹克外套及背部阴影略偏暗偏紫褐(D-L1)。"
    },
    1099: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },

    # Sheet 18 (Tasks 1100, 1101, 1102, 1103, 1104, 1105)
    1100: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1101: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1102: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "两只泰迪熊怀中抱着的彩色小球中，最核心位置原本鲜艳明亮的小黄球被彻底脱色错涂为纯白灰球。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "毛绒玩具怀中的彩色塑料球整体色彩欠饱和发白。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：泰迪熊抱着的彩色小球中核心小黄球脱色错涂为纯白(C-L2, E2-L2)。"
    },
    1103: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "非洲稀树草原两只长颈鹿身后高空开阔的蔚蓝晴空大面积褪色泛白变浅。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "晴朗蓝天边缘略显泛灰黄色调。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：草原长颈鹿身后蔚蓝晴空大面积褪色泛白变浅微偏灰黄(E2-L1, D-L1)。"
    },
    1104: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1105: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "旷野漫步大象身后的万里晴空严重脱色泛白变灰。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "开阔草原与大象粗糙灰皮整体色调略显冷暗偏色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：大象身后的开阔晴空脱色泛白发灰黄，大象与草甸偏冷暗(E2-L2, D-L1)。"
    },

    # Sheet 19 (Tasks 1106, 1107, 1108, 1109, 1110, 1111)
    1106: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "草坪与背景观众席整体色彩略微偏暖红黄调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "仿真战马木藤道具身上的紫色装饰花环与织物略显褪色暗淡。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：草坪与观众席微偏暖(D-L1)，仿真战马身上的紫色花环褪色暗淡(E2-L1)。"
    },
    1107: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1108: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "超市货架上陈列的成熟黄色香蕉色泽偏深浓重，阴影处略微偏深焦黄。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：超市货架上陈列的成熟黄色香蕉色泽偏深浓重微过饱和(E1-L1)。"
    },
    1109: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1110: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "动物园长颈鹿展区背景开阔天空微有褪色泛白变灰。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：动物园长颈鹿展区背景天空微有褪色泛白变灰(E2-L1)。"
    },
    1111: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "展厅中古董摩托车旁的两位男子面部与手臂肤色略显泛红，左侧男子夹克外套略带黄褐偏色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：展厅摩托车旁两位男子肤色略泛红，左侧男子外套略偏黄褐(D-L1)。"
    },

    # Sheet 20 (Tasks 1112, 1113, 1114, 1115, 1116, 1117)
    1112: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1113: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "山丘放风筝场景原本绚烂的落日余晖晚霞被偏染为冰冷青灰调。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "黄昏暖橙色霞光天空大面积错涂为平淡的冷青灰色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：山丘放风筝场景落日余晖暖橙色霞光缺失变冷(D-L1, C-L2)。"
    },
    1114: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "飞鸟掠过的天空原本澄澈湛蓝被严重错涂为灰黄色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "斑驳破旧的建筑物外墙与木质窗框整体泛黄褐色偏色。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：飞鸟掠过的湛蓝天空错涂为灰黄(C-L2)，斑驳外墙泛黄褐偏色(D-L2)。"
    },
    1115: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1116: {
        "defects": [],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "审查通过"
    },
    1117: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "运河两岸林荫树木色彩略微偏黄绿泛焦，河道水面与远处教堂建筑倒影轻微偏暖。"}
        ],
        "reviewed_score": None,
        "needs_rescoring": True,
        "note": "视觉直审具象定物：运河两岸林荫树木略偏黄绿泛焦，水面与远处教堂倒影轻微偏暖(D-L1)。"
    }
}

def main():
    base_dir = r"d:\学业文件\MCL\上色评价_数据集标注\LS_lcad_reviewer"
    audit_out_path = os.path.join(base_dir, "intermediate", "audits", "grounding_remaining_batch_04.json")
    all_export_path = os.path.join(base_dir, "exports", "reviewed_1_10000_all.json")
    clean_export_path = os.path.join(base_dir, "exports", "reviewed_1_10000_clean.json")

    print(f"[*] 正在保存 Batch 04 具象定物映射至: {audit_out_path}")
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
