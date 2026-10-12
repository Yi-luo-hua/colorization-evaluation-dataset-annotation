# -*- coding: utf-8 -*-
"""
应用 Batch 35 审核具象定物判决字典并双向同步至正式交付文件
Batch 35: Task #7027 ~ #7214 (共 120 组)
"""

import json
import os
import re

# 120 组人工直审与具象定物判决字典
REVIEWS_B35 = {
    # Sheet 01
    7027: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7029: {
        "score": 2.27,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "机场停机坪客机机身阴影与后方航站楼外墙在强光照射下略显欠饱和偏灰暗(E2-L1, F-L1)。"
    },
    7030: {
        "score": 4.17,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "长颈鹿身躯网状棕黄斑纹与背景石砌矮墙色彩略显欠饱和偏暗冷(D-L1, E2-L1)。"
    },
    7033: {
        "score": 1.48,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "草丛与灌木叶片被大面积严重错涂为刺眼浓艳的妖异粉紫红偏色，全图色调严重失真(D-L2, E1-L2, F-L2)。"
    },
    7035: {
        "score": 2.36,
        "severities": {"D": "L1", "E1": "L2", "F": "L1"},
        "note": "街道旁立着的菱形行人过街警示黄牌与背景行道树草坪大面积浸染过于浓烈刺眼的荧光黄色与过浓绿意(D-L1, E1-L2, F-L1)。"
    },
    7036: {
        "score": 4.46,
        "severities": {"D": "L1", "F": "L1"},
        "note": "草坡上吃草的羊群毛发高光反光略显偏蓝，远方晚霞山峦色泽轻微浓艳(D-L1, F-L1)。"
    },

    # Sheet 02
    7037: {
        "score": 2.06,
        "severities": {"C": "L2", "E2": "L2", "F": "L2"},
        "note": "左侧原本毛色鲜亮金黄的橘猫被严重脱色错涂为暗淡单调的冷灰白毛发，猫咪品种特征与色彩完全丢失(C-L2, E2-L2, F-L2)。"
    },
    7038: {
        "score": 2.36,
        "severities": {"C": "L2", "F": "L1"},
        "note": "草坪上凌空跃起的白狗口中叼着的红色飞盘被颠覆性错涂为亮绿色，玩具道具色彩严重错配(C-L2, F-L1)。"
    },
    7039: {
        "score": 2.50,
        "severities": {"E1": "L1", "F": "L1"},
        "note": "夜间街头行驶车辆的高亮前大灯光晕与沿街暖光照明略显过饱和刺眼(E1-L1, F-L1)。"
    },
    7042: {
        "score": 4.17,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "卫生间洗手台面上并排坐着的两只长毛猫毛色与背景瓷砖在日光灯下略显平淡发暗(E2-L1, F-L1)。"
    },
    7043: {
        "score": 1.25,
        "severities": {"C": "L2", "E2": "L3", "F": "L2"},
        "note": "滑雪者身穿的鲜红色马甲完全褪色错涂为深黑灰色，背景晴朗蓝天严重脱色为死灰白，整体色彩严重衰减(C-L2, E2-L3, F-L2)。"
    },
    7046: {
        "score": 4.46,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "草坪边缘设立的黄色消防栓与金属阻车杆表皮油漆色彩略显偏深暗(E2-L1, F-L1)。"
    },

    # Sheet 03
    7047: {
        "score": 2.36,
        "severities": {"C": "L1", "E1": "L1", "F": "L1"},
        "note": "卫生间马桶旁铺设的红白条纹地毯边缘过饱和，右侧放置的绿色塑料收纳桶错涂为暗黄色(C-L1, E1-L1, F-L1)。"
    },
    7048: {
        "score": 2.11,
        "severities": {"C": "L2", "E2": "L2", "F": "L2"},
        "note": "湖畔停栖鸬鹚水鸟下方的清澈湖面与晴朗天空大面积欠饱和褪色为泛灰暗黄色(C-L2, E2-L2, F-L2)。"
    },
    7051: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7052: {
        "score": 2.06,
        "severities": {"C": "L2", "E2": "L2", "F": "L2"},
        "note": "合影中右侧青年身穿的鲜红色短袖T恤与中间长辈的金黄色服饰严重脱色褪为暗灰白色(C-L2, E2-L2, F-L2)。"
    },
    7054: {
        "score": 2.36,
        "severities": {"D": "L2", "E1": "L1", "F": "L1"},
        "note": "室内天花板中央空调出风口周围的墙面与照明灯光大面积泛浓艳刺眼的橙黄色偏色(D-L2, E1-L1, F-L1)。"
    },
    7055: {
        "score": 1.48,
        "severities": {"C": "L3", "E1": "L2", "F": "L2"},
        "note": "毛绒泰迪熊怀中抱着的塑料尺子被颠覆性错涂为刺眼突兀的荧光粉红色与绿色杂色(C-L3, E1-L2, F-L2)。"
    },

    # Sheet 04
    7057: {
        "score": 4.46,
        "severities": {"D": "L1"},
        "note": "红色旅行拉杆箱表面织物与提手暗部色彩略显轻微偏深暗(D-L1)。"
    },
    7058: {
        "score": 2.43,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "繁华街道街角背景中的红砖历史建筑外墙及人行道阴影色彩略显平淡发暗(E2-L1, F-L1)。"
    },
    7059: {
        "score": 4.46,
        "severities": {"E1": "L1", "F": "L1"},
        "note": "街边白色金属箱正面张贴的红色英文标语贴纸色调略显浓艳(E1-L1, F-L1)。"
    },
    7060: {
        "score": 2.36,
        "severities": {"D": "L1", "E1": "L2", "F": "L1"},
        "note": "水果摊前小女孩佩戴的鲜红色头巾及后方悬挂的香蕉串色彩过于浓艳刺眼(D-L1, E1-L2, F-L1)。"
    },
    7061: {
        "score": 2.43,
        "severities": {"D": "L2", "F": "L1"},
        "note": "餐桌旁看手机男子手部皮肤与桌上白色餐巾纸边缘浸染失真的红紫暖色偏色(D-L2, F-L1)。"
    },
    7064: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 05
    7067: {
        "score": 2.27,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "城市街道上方林肯隧道指示牌与沿街高楼在阴影下略显欠饱和偏灰暗(E2-L1, F-L1)。"
    },
    7068: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7069: {
        "score": 4.46,
        "severities": {"D": "L1"},
        "note": "夜间足球场草坪在泛光灯照射下色调整体略显轻微偏深(D-L1)。"
    },
    7071: {
        "score": 1.48,
        "severities": {"C": "L3", "E2": "L2", "F": "L2"},
        "note": "棒球场上击球小球员身穿的鲜红色短袖运动球服被完全脱色错涂为苍白暗淡的灰白色，服饰特征彻底丧失(C-L3, E2-L2, F-L2)。"
    },
    7072: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7073: {
        "score": 2.36,
        "severities": {"D": "L2", "F": "L2"},
        "note": "水上飞机停靠码头上空晴朗蓝天与海湾水面大面积泛黄泛暖偏色，天空纯净青蓝质感严重失真(D-L2, F-L2)。"
    },

    # Sheet 06
    7075: {
        "score": 2.06,
        "severities": {"C": "L2", "E2": "L2", "F": "L2"},
        "note": "单板滑雪者扛在肩上的滑雪板红色底面涂层严重欠饱和脱色为暗黑灰绿色(C-L2, E2-L2, F-L2)。"
    },
    7076: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7077: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7078: {
        "score": 2.06,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "客厅室内浅色墙壁与地毯整体色温严重偏冷发青暗淡，暗部光影欠饱和严重(D-L2, E2-L2, F-L2)。"
    },
    7079: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7083: {
        "score": 4.46,
        "severities": {"D": "L1", "F": "L1"},
        "note": "聚会客厅茶几上的金黄柑橘水果盘及人物服饰暗部在暖黄光照下略显偏深(D-L1, F-L1)。"
    },

    # Sheet 07
    7084: {
        "score": 2.43,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "露天海景餐桌前女子的面部与手臂皮肤在自然日光照射下略显欠饱和偏灰暗(E2-L1, F-L1)。"
    },
    7085: {
        "score": 2.43,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "露天咖啡座撑开的条纹遮阳伞与餐桌红色桌布色彩略显欠饱和褪色泛暗灰(E2-L1, F-L1)。"
    },
    7086: {
        "score": 2.06,
        "severities": {"C": "L2", "E2": "L2", "F": "L2"},
        "note": "站立在绿叶墙前的青年男子所穿的深蓝色正装衬衫被错涂为完全褪色的灰黑色，失去原有的蓝调(C-L2, E2-L2, F-L2)。"
    },
    7087: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7088: {
        "score": 2.43,
        "severities": {"D": "L2", "F": "L1"},
        "note": "木桌上放置的透明玻璃奶瓶瓶口与背景地面浸染失真的粉红暖色偏色(D-L2, F-L1)。"
    },
    7089: {
        "score": 2.43,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "小男孩手中举着的多彩拼接大风筝鲜艳的红黄翼面色彩略显欠饱和褪色发暗(E2-L1, F-L1)。"
    },

    # Sheet 08
    7091: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7094: {
        "score": 2.06,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "书房电脑桌面与背景墙壁大面积丧失温暖的金黄灯光氛围，严重偏向冷青灰调(D-L2, E2-L2, F-L2)。"
    },
    7095: {
        "score": 4.46,
        "severities": {"D": "L1", "F": "L1"},
        "note": "道路交叉口红绿灯立柱与限速40标志牌在逆光下阴影色彩略显偏深(D-L1, F-L1)。"
    },
    7096: {
        "score": 2.43,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "海滩浪花中手持冲浪板少年的逆光剪影在夕阳余晖下色彩层次略显平淡(E2-L1, F-L1)。"
    },
    7100: {
        "score": 2.43,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "重型警用摩托车车头荧光绿警用拉花与交警身穿的高反光黄绿背心色彩欠饱和褪色发白(E2-L1, F-L1)。"
    },
    7101: {
        "score": 4.46,
        "severities": {"D": "L1"},
        "note": "卫生间陶瓷洗手台盆底部及金属水龙头反光略显暗淡偏深(D-L1)。"
    },

    # Sheet 09
    7102: {
        "score": 2.36,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "木屋客厅木质地板与茶几家具大面积浸染过浓焦糖暖黄偏色，色彩饱和度轻度过高(D-L1, E1-L1, F-L1)。"
    },
    7103: {
        "score": 2.06,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "餐馆餐桌前吃披萨男子的面部皮肤与周围环境完全丧失原本浓郁的暖红光晕，呈现严重冷青灰偏色(D-L2, E2-L2, F-L2)。"
    },
    7105: {
        "score": 2.23,
        "severities": {"C": "L2", "F": "L2"},
        "note": "酒店客房左侧单人床上原本深蓝色的床单被褥被颠覆性错涂为深红褐色，织物色彩完全错配(C-L2, F-L2)。"
    },
    7107: {
        "score": 2.27,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "航站楼扶梯上拖行李箱女子的服饰与拉杆箱在室内顶灯照明下略显欠饱和偏灰暗(E2-L1, F-L1)。"
    },
    7109: {
        "score": 1.48,
        "severities": {"C": "L3", "E2": "L2", "F": "L2"},
        "note": "庭院木桌周围原本郁郁葱葱的茂密草坪大面积严重脱色褪色为毫无生机的灰砂土色(C-L3, E2-L2, F-L2)。"
    },
    7111: {
        "score": 4.46,
        "severities": {"D": "L1"},
        "note": "冷餐台前挑选食物的长辈服饰与餐盘暗部色彩略显轻微偏深(D-L1)。"
    },

    # Sheet 10
    7112: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7115: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7116: {
        "score": 2.23,
        "severities": {"D": "L2", "F": "L2"},
        "note": "披萨店餐桌上摆放的数盘现烤披萨表面芝士与番茄酱大面积泛蓝紫冷偏色，烤制色泽严重失真(D-L2, F-L2)。"
    },
    7117: {
        "score": 2.27,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "城市滑板公园水泥斜坡与背景绿化灌木在日光下略显欠饱和偏灰(E2-L1, F-L1)。"
    },
    7120: {
        "score": 4.46,
        "severities": {"D": "L1", "F": "L1"},
        "note": "餐桌旁就座男子的面部皮肤与桌上大号披萨饼色温过度偏暖泛红橙色(D-L1, F-L1)。"
    },
    7121: {
        "score": 2.27,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "卧室单人床铺与窗台下方实木床架阴影在背光下略显欠饱和偏灰暗(E2-L1, F-L1)。"
    },

    # Sheet 11
    7122: {
        "score": 4.46,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "室内地面铺设的米色地毯与瓦楞纸箱在顶光照射下色彩略显过饱和偏暖黄(D-L1, E1-L1)。"
    },
    7123: {
        "score": 2.43,
        "severities": {"D": "L2", "F": "L1"},
        "note": "马群奔跑经过的起伏山坡天然草场大面积泛暖黄枯草色偏色，绿意严重衰减(D-L2, F-L1)。"
    },
    7124: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7126: {
        "score": 4.46,
        "severities": {"E2": "L1"},
        "note": "公园步道两旁的常绿松树针叶与灌木丛色彩略显欠饱和偏深暗(E2-L1)。"
    },
    7127: {
        "score": 2.43,
        "severities": {"D": "L2", "F": "L1"},
        "note": "公园中央远处的红砖钟楼立面及周围树木大面积浸染过暖偏红偏浓的失真色调(D-L2, F-L1)。"
    },
    7133: {
        "score": 2.27,
        "severities": {"D": "L2", "E2": "L1", "F": "L2"},
        "note": "玻璃陈列柜内展示的新鲜热带水果及外侧黄色塑料水盆大面积浸染失真的冷青灰色调(D-L2, E2-L1, F-L2)。"
    },

    # Sheet 12
    7136: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7137: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7138: {
        "score": 4.46,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "树冠枝叶与远景绿化带色彩略显欠饱和泛灰冷(D-L1, E2-L1)。"
    },
    7139: {
        "score": 2.36,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "河流浅滩中大象群戏水周围的茂密水草林地色彩轻微浓艳过饱和(D-L1, E1-L1, F-L1)。"
    },
    7143: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7144: {
        "score": 2.43,
        "severities": {"D": "L2", "E2": "L1", "F": "L1"},
        "note": "荒原泥地上两匹黑马身下的大面积沙土地面严重偏离暖黄沙色，呈现冰冷泛青灰偏色(D-L2, E2-L1, F-L1)。"
    },

    # Sheet 13
    7145: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7146: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7147: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7148: {
        "score": 2.36,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "卧室天花板与浅色墙壁大面积浸染过浓暖黄色偏色，落地窗外阳台矮墙色调略显过饱和偏浓(D-L1, E1-L1, F-L1)。"
    },
    7149: {
        "score": 2.36,
        "severities": {"B": "L1", "D": "L1", "F": "L1"},
        "note": "网球拍黑色边框与后方散落的深蓝色运动装备包边缘相互渗透溢色，局部杂物色调略显偏冷(B-L1, D-L1, F-L1)。"
    },
    7150: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 14
    7151: {
        "score": 2.27,
        "severities": {"D": "L1", "E2": "L2", "F": "L1"},
        "note": "长颈鹿身后的茂密灌木树丛大面积欠饱和褪色为枯黄灰褐色，自然生机严重受损(D-L1, E2-L2, F-L1)。"
    },
    7152: {
        "score": 4.46,
        "severities": {"D": "L1"},
        "note": "卫生间洗手台大理石台面与玻璃淋浴房反射光线在日光灯下略显偏暗偏冷(D-L1)。"
    },
    7154: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7155: {
        "score": 4.46,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "餐盘中油炸鸡柳酥脆表皮与金黄蘸酱色温过度偏暖泛红，色彩略显浓艳(D-L1, E1-L1)。"
    },
    7157: {
        "score": 1.0,
        "severities": {"A": ""},
        "note": "滑雪者脚下单板底面的亮蓝色与粉红色艺术英文字母图案及全图色彩彻底未渲染，整张图像完全退化为纯黑白单色灰阶（缺色 A）。"
    },
    7159: {
        "score": 4.46,
        "severities": {"D": "L1"},
        "note": "棒球场上击球小球员身穿的绿色球衣暗部与远处草坪在强日光下略显偏暗偏深(D-L1)。"
    },

    # Sheet 15
    7163: {
        "score": 2.27,
        "severities": {"D": "L2", "E2": "L1", "F": "L1"},
        "note": "卫生间浅色瓷砖墙面与淋浴房磨砂玻璃完全丧失原本温馨的暖黄光照，整体严重偏向冰冷泛青灰色调(D-L2, E2-L1, F-L1)。"
    },
    7164: {
        "score": 2.36,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "黑白猫咪身后的木质家具与暖色背景环境光严重脱色泛冷，整体呈现偏冷青灰色偏色(D-L1, E2-L1, F-L1)。"
    },
    7166: {
        "score": 2.43,
        "severities": {"D": "L2", "E2": "L1"},
        "note": "卫生间双洗手台陶瓷盆暗部与镜框墙面大面积泛暗冷青灰调，整体缺乏原本温暖的日光感(D-L2, E2-L1)。"
    },
    7167: {
        "score": 1.48,
        "severities": {"C": "L3", "E2": "L2", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：洗手台台面上右侧原本通体毛色鲜亮金黄的橘猫被严重脱色错涂为暗沉无光的纯灰黑猫，猫咪品种色彩完全失真（严重错色 C-L3, E2-L2, F-L2）。"
    },
    7170: {
        "score": 2.23,
        "severities": {"C": "L2", "E1": "L2", "F": "L2"},
        "note": "地面放置的塑料收纳盆及盆内牙刷把手色彩被颠覆性错涂为浓艳刺眼的桃红与红紫色，色彩明显过饱和失真(C-L2, E1-L2, F-L2)。"
    },
    7171: {
        "score": 1.95,
        "severities": {"B": "L2", "D": "L1", "E1": "L2", "F": "L2"},
        "note": "海报背景大面积浸染失真浓艳的荧光粉红紫底色，画框边缘与跃起的白狗轮廓发生明显溢色侵染(B-L2, D-L1, E1-L2, F-L2)。"
    },

    # Sheet 16
    7172: {
        "score": 2.43,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：卧室右侧木质护墙板与实木地板大面积丧失温暖日光感，严重欠饱和脱色泛冷灰偏色(D-L1, E2-L1, F-L1)。"
    },
    7176: {
        "score": 2.23,
        "severities": {"D": "L1", "E1": "L2", "F": "L2"},
        "note": "玩偶微缩餐桌上铺设的嫩绿色桌布色彩过于浓艳刺眼，上方小木屋屋梁边缘浸染失真紫红偏色(D-L1, E1-L2, F-L2)。"
    },
    7177: {
        "score": 1.95,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "高档餐厅吧台上方的金黄吊灯暖光与室内照明氛围完全丧失，整座吧台与背景墙壁大面积严重偏向冰冷泛青泛灰偏色(D-L2, E2-L2, F-L2)。"
    },
    7178: {
        "score": 2.43,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "夜间城市街道上的沿街建筑外墙与路面大面积丧失温暖夜景灯光，整体色调严重泛冷青暗灰(D-L1, E2-L1, F-L1)。"
    },
    7181: {
        "score": 4.17,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "海滨野餐区沙滩地面与木质野餐桌椅在阴天下色调略显偏暗偏冷青灰(D-L1, E2-L1)。"
    },
    7182: {
        "score": 2.36,
        "severities": {"C": "L2", "D": "L1", "F": "L1"},
        "note": "动物园铁丝网栅栏外侧原本郁郁葱葱的茂密绿叶灌木被大面积错涂为枯黄焦褐色，斑马黑白毛发边缘轻微泛黄(C-L2, D-L1, F-L1)。"
    },

    # Sheet 17
    7183: {
        "score": 2.36,
        "severities": {"D": "L2", "E2": "L1", "F": "L1"},
        "note": "室内墙面悬挂的美国星条旗红色条纹严重褪色暗淡，人物军装与室内光线整体偏向冷青暗灰偏色(D-L2, E2-L1, F-L1)。"
    },
    7185: {
        "score": 4.17,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "羊圈围栏旁小绵羊身上的羊毛及地面干草秸秆色调略显欠饱和偏冷青灰(D-L1, E2-L1)。"
    },
    7186: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7187: {
        "score": 2.36,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "街道模型中的多辆小汽车车身漆面及背景街景大面积浸染过浓焦糖暖黄偏色，色彩轻度过饱和(D-L1, E1-L1, F-L1)。"
    },
    7188: {
        "score": 2.36,
        "severities": {"C": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：棒球投手头戴的深蓝色球帽与贴身长袖打底衫被错涂为草绿褐色，球服胸前红色英文字体及背景看台严重偏暖泛红（错色 C-L2, D-L1, F-L1）。"
    },
    7189: {
        "score": 1.48,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "黑白猫咪的面部与前胸白色毛发被严重浸染为刺眼浓艳的深红紫色，全图暗角环境过度过饱和泛红失真(D-L2, E1-L2, F-L2)。"
    },

    # Sheet 18
    7190: {
        "score": 2.36,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "黑色皮椅背后的背景墙面与椅面坐垫浸染过度浓艳的红褐暖偏色，左侧绿植背景严重偏色(D-L1, E1-L1, F-L1)。"
    },
    7191: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7192: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7193: {
        "score": 2.27,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "休闲客厅原本明艳的淡黄色墙壁大面积欠饱和褪色为泛冷暗黄灰色，靠椅与地面光影氛围暗淡(D-L1, E2-L1, F-L1)。"
    },
    7195: {
        "score": 4.46,
        "severities": {"D": "L1"},
        "note": "餐厅实木餐桌椅与桌面白色餐布在顶灯照射下色调略显偏暖泛红橙色(D-L1)。"
    },
    7196: {
        "score": 2.36,
        "severities": {"D": "L2", "F": "L2"},
        "note": "生日蛋糕上点燃的蜡烛烛光与小女孩面部反光大面积泛失真诡异的绿黄偏色，背景窗格色调发绿(D-L2, F-L2)。"
    },

    # Sheet 19
    7197: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7198: {
        "score": 2.43,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：雪地边缘矗立的两尊人物青铜雕塑身躯色彩严重欠饱和褪色为死黑死灰，失去原本青铜与服饰层次(D-L1, E2-L1, F-L1)。"
    },
    7199: {
        "score": 4.17,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "街边设立的立式停车计时器金属外壳表面完全失去原本暖黄路灯反光，呈现偏冷青灰暗淡偏色(D-L1, E2-L1)。"
    },
    7200: {
        "score": 2.43,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "窗台上玻璃花瓶中插着的深红色干花花束大面积欠饱和褪色为暗灰褐色，木质窗框色彩平淡(E2-L1, F-L1)。"
    },
    7203: {
        "score": 1.95,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "卫生间大理石洗手台面与镜子周围完全丧失原本浓郁明亮的暖黄顶灯光晕，大面积严重偏向冰冷泛青灰偏色(D-L2, E2-L2, F-L2)。"
    },
    7205: {
        "score": 4.46,
        "severities": {"D": "L1"},
        "note": "庭院草坪上安放的小女孩与幼犬雕塑金属石材表面反光略显轻微偏深(D-L1)。"
    },

    # Sheet 20
    7206: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7208: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7210: {
        "score": 1.0,
        "severities": {"A": ""},
        "note": "白马身后原本明亮的黄绿草地与木质围栏全域色彩彻底未渲染，整张图像完全沦为纯黑白单色灰阶（缺色 A）。"
    },
    7211: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    7212: {
        "score": 4.17,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "原5.0满分严重漏检，核查发现：石砌围墙后方的茂密绿草坪大面积欠饱和褪色泛冷青灰，棕熊身上的毛发光泽略显暗淡(D-L1, E2-L1)。"
    },
    7214: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
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
    grounding_out_path = "LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_35.json"
    all_export_path = "LS_lcad_reviewer/exports/reviewed_1_10000_all.json"
    clean_export_path = "LS_lcad_reviewer/exports/reviewed_1_10000_clean.json"

    # 1. 导出中间定物字典
    with open(grounding_out_path, "w", encoding="utf-8") as f:
        json.dump(REVIEWS_B35, f, ensure_ascii=False, indent=2)
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

    for tid, r in REVIEWS_B35.items():
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
