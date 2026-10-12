# -*- coding: utf-8 -*-
"""
应用 Batch 28 审核具象定物判决字典并双向同步至正式交付文件
Batch 28: Task #5736 ~ #5921 (共 120 组)
"""

import json
import os
import re

# 120 组人工直审与具象定物判决字典
REVIEWS_B28 = {
    # Sheet 01
    5736: {
        "score": 2.61,
        "severities": {"D": "L2", "E2": "L1", "F": "L1"},
        "note": "商用厨房操作台面与储物柜金属银白反光系统性偏暗浑浊暖黄褐(D-L2, E2-L1, F-L1)。"
    },
    5737: {
        "score": 2.17,
        "severities": {"E1": "L2", "D": "L1", "F": "L2"},
        "note": "餐桌食客面部手臂肤色与白色餐盘严重过饱和泛刺目红铜与深紫红假色(E1-L2, D-L1, F-L2)。"
    },
    5738: {
        "score": 2.47,
        "severities": {"E2": "L2", "C": "L1", "F": "L1"},
        "note": "比萨饼上的新鲜翠绿青椒圈与红番茄块严重脱色发灰欠饱和缺乏生机(E2-L2, C-L1, F-L1)。"
    },
    5739: {
        "score": 2.47,
        "severities": {"C": "L2", "E2": "L2", "D": "L1", "F": "L2"},
        "note": "侧翻客车车厢原本鲜明的蓝灰色烤漆颠覆性严重错涂为发暗土黄与锈褐色(C-L2, E2-L2, D-L1, F-L2)。"
    },
    5741: {
        "score": 2.17,
        "severities": {"E1": "L2", "D": "L1", "F": "L1"},
        "note": "古典钟楼大厦外立面夜景照明严重过饱和泛浓烈深橙红铜色失真(E1-L2, D-L1, F-L1)。"
    },
    5742: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：小男孩浅色T恤胸前鲜红与黄绿卡通印花大面积脱色褪变为苍白肉灰粉色(C-L2, E2-L2, F-L1)。"
    },

    # Sheet 02
    5743: {
        "score": 5.0,
        "severities": {"C": "L1", "E2": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：客厅暖黄木门与茶几上的鲜橙色甜橙色彩严重冲淡脱色泛冷灰(C-L1, E2-L2, D-L1, F-L1)。"
    },
    5744: {
        "score": 2.17,
        "severities": {"E1": "L2", "D": "L1", "F": "L2"},
        "note": "宴会圆桌深紫罗兰桌布及椅套过饱和泛刺目电光青蓝紫假色(E1-L2, D-L1, F-L2)。"
    },
    5745: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：雪地滑雪者身上原本鲜艳醒目的朱红羽绒服严重脱色欠饱和褪变为发暗脏灰红(C-L2, E2-L2, F-L1)。"
    },
    5746: {
        "score": 2.43,
        "severities": {"C": "L2", "E2": "L2", "D": "L1", "F": "L1"},
        "note": "甜点盘上原本娇艳鲜红的草莓巧克力球严重脱色泛暗紫发灰(C-L2, E2-L2, D-L1, F-L1)。"
    },
    5747: {
        "score": 2.47,
        "severities": {"D": "L2", "E2": "L1", "F": "L1"},
        "note": "翻滚海浪与飞溅浪花系统性偏浑浊发暗的黄绿青灰色(D-L2, E2-L1, F-L1)。"
    },
    5748: {
        "score": 2.17,
        "severities": {"D": "L2", "E2": "L1", "F": "L1"},
        "note": "洗手间镜前壁灯光照下的大理石台面严重泛冷青暗绿杂色(D-L2, E2-L1, F-L1)。"
    },

    # Sheet 03
    5751: {
        "score": 5.0,
        "severities": {"E2": "L2", "C": "L1", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：长颈鹿身躯原本浓郁金红的网状斑纹严重脱色发灰欠饱和(E2-L2, C-L1, D-L1, F-L1)。"
    },
    5753: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：纪念碑前的大草坪原本生机翠绿严重褪变为偏枯黄灰绿(D-L1, E2-L2, F-L1)。"
    },
    5754: {
        "score": 2.23,
        "severities": {"C": "L2", "D": "L1", "F": "L2"},
        "note": "圆镜内反射的室内门框与背景严重泛起发暗冷青灰紫杂色(C-L2, D-L1, F-L2)。"
    },
    5755: {
        "score": 4.46,
        "severities": {"C": "L3", "E2": "L3", "D": "L1", "F": "L2"},
        "note": "后备箱内原本鲜艳夺目的亮玫粉与湖蓝色滑雪背包装备颠覆性彻底脱色错涂为灰黑白(C-L3, E2-L3, D-L1, F-L2)。"
    },
    5757: {
        "score": 5.0,
        "severities": {"E2": "L1", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：草场上骏马原本浓润光洁的栗红褐色皮毛明显欠饱和脱色偏淡土黄(E2-L1, D-L1, F-L1)。"
    },
    5759: {
        "score": 4.46,
        "severities": {"C": "L3", "E2": "L3", "D": "L2", "F": "L2"},
        "note": "巴士车身侧面原本明快鲜艳的暖红与孔雀蓝烤漆被颠覆性彻底脱色错涂为冰冷水泥灰白(C-L3, E2-L3, D-L2, F-L2)。"
    },

    # Sheet 04
    5760: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：卡通猫咪风筝下方的粉红与天蓝彩色飘带大面积脱色褪为苍白灰(C-L2, E2-L2, F-L1)。"
    },
    5761: {
        "score": 1.08,
        "severities": {"C": "L3", "E1": "L3", "D": "L2", "F": "L3"},
        "note": "玻璃杯中原本金黄澄澈的啤酒液体颠覆性严重错涂为刺眼深紫红与荧光洋红色(C-L3, E1-L3, D-L2, F-L3)。"
    },
    5762: {
        "score": 2.47,
        "severities": {"C": "L1", "D": "L1", "E2": "L2", "F": "L1"},
        "note": "厨房操作台的红木橱柜边框与大理石台面严重泛冷青暗灰杂色(C-L1, D-L1, E2-L2, F-L1)。"
    },
    5763: {
        "score": 2.36,
        "severities": {"C": "L2", "E2": "L2", "D": "L1", "F": "L2"},
        "note": "街头人行道右侧金黄夕阳强光照射下的红砖墙严重脱色泛冷灰(C-L2, E2-L2, D-L1, F-L2)。"
    },
    5764: {
        "score": 2.23,
        "severities": {"C": "L1", "E2": "L2", "D": "L1", "F": "L1"},
        "note": "公园木质长椅的深红棕座板与靠背严重泛浅淡漂白黄白灰(C-L1, E2-L2, D-L1, F-L1)。"
    },
    5765: {
        "score": 2.13,
        "severities": {"B": "L2", "C": "L2", "E1": "L2", "D": "L1", "F": "L2"},
        "note": "窗框与周围窗帘织物严重泛起刺目荧光深洋红紫假色并越界溢色(B-L2, C-L2, E1-L2, D-L1, F-L2)。"
    },

    # Sheet 05
    5766: {
        "score": 2.3,
        "severities": {"C": "L3", "F": "L3", "B": "L1"},
        "note": "白色奶牛背部与臀部皮毛被恶性涂抹大面积刺眼的孔雀蓝绿色伪色斑块(C-L3, F-L3, B-L1)。"
    },
    5767: {
        "score": 2.47,
        "severities": {"D": "L2", "C": "L1", "F": "L1"},
        "note": "背景树木翠绿枝叶与长颈鹿斑纹系统性偏暗浑浊红褐调(D-L2, C-L1, F-L1)。"
    },
    5768: {
        "score": 2.17,
        "severities": {"C": "L2", "E1": "L2", "D": "L1", "F": "L2"},
        "note": "电推剪刀头接触的厚重白色羊毛表面被泼染刺目浓艳深洋红紫假色(C-L2, E1-L2, D-L1, F-L2)。"
    },
    5769: {
        "score": 5.0,
        "severities": {"E1": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：棒球场内野整片红土跑道严重过饱和刺目泛火红橙色(E1-L2, D-L1, F-L1)。"
    },
    5770: {
        "score": 2.43,
        "severities": {"C": "L2", "E2": "L2", "D": "L1", "F": "L2"},
        "note": "室内演讲台原本鲜明纯正的墨绿桌布严重脱色错涂为发暗枯褐灰黑(C-L2, E2-L2, D-L1, F-L2)。"
    },
    5772: {
        "score": 5.0,
        "severities": {"C": "L1", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：枝头右上角原本浓烈金黄灿烂的秋日树叶簇严重脱色泛苍白灰黄(C-L1, E2-L2, F-L1)。"
    },

    # Sheet 06
    5773: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1", "C": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：街头防撞警示柱原本纯正的鲜黄色与天蓝色严重发暗脱色且消防栓过艳(D-L1, E1-L1, C-L1, F-L1)。"
    },
    5775: {
        "score": 5.0,
        "severities": {"D": "L2", "C": "L2", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：整片起伏的干燥金黄沙丘地面大面积严重偏冷泛青蓝暗灰色(D-L2, C-L2, F-L2)。"
    },
    5777: {
        "score": 5.0,
        "severities": {"C": "L3", "E2": "L3", "D": "L2", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：桌面上的复古皮革眼镜盒原本纯正温润的焦糖暖红棕色颠覆性彻底脱色错涂为深黑墨绿冷灰(C-L3, E2-L3, D-L2, F-L2)。"
    },
    5778: {
        "score": 1.08,
        "severities": {"E2": "L3", "D": "L1", "F": "L2"},
        "note": "卫生间陶瓷洗脸盆与背景马赛克瓷砖墙面极度欠饱和濒临黑白死灰(E2-L3, D-L1, F-L2)。"
    },
    5780: {
        "score": 2.25,
        "severities": {"C": "L2", "D": "L2", "F": "L2"},
        "note": "电脑桌上的白色记事本与木质桌面严重泛发暗冷青蓝紫杂色(C-L2, D-L2, F-L2)。"
    },
    5783: {
        "score": 5.0,
        "severities": {"C": "L1", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：网球场上女选手身上鲜艳纯正的大红运动背心明显脱色欠饱和变暗褐(C-L1, E2-L2, F-L1)。"
    },

    # Sheet 07
    5785: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：桌面中央陈列的晶莹青蓝荧光玻璃工艺水瓶大面积脱色欠饱和褪变为苍白灰白(C-L2, E2-L2, F-L1)。"
    },
    5790: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：靠窗办公桌面与室内环境整体偏向冰冷生硬的青灰暗蓝调(D-L1, F-L1)。"
    },
    5792: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：内燃机车车头前脸原本醒目鲜艳的明黄色警示烤漆大面积脱色变暗偏土灰褐(C-L2, E2-L2, D-L1, F-L1)。"
    },
    5794: {
        "score": 2.23,
        "severities": {"C": "L2", "D": "L1", "E2": "L1", "F": "L1"},
        "note": "白瓷餐盘内的冷切火腿肉片原本鲜嫩粉红严重错涂为发暗猪肝暗紫黑(C-L2, D-L1, E2-L1, F-L1)。"
    },
    5797: {
        "score": 2.47,
        "severities": {"C": "L2", "D": "L2", "F": "L2"},
        "note": "金发青年原本柔和纯净的浅金色头发大面积严重泛冷灰泛绿杂色(C-L2, D-L2, F-L2)。"
    },
    5798: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "D": "L1", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：滑板公园背景中原本绚烂浓艳的明黄与大红色艺术雕塑圆环大面积脱色欠饱和褪变为苍白灰白(C-L2, E2-L2, D-L1, F-L2)。"
    },

    # Sheet 08
    5801: {
        "score": 4.46,
        "severities": {"C": "L2", "D": "L1", "F": "L1"},
        "note": "和室榻榻米草席与木质移门严重泛冷青暗灰紫杂色(C-L2, D-L1, F-L1)。"
    },
    5802: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：网球场左上方原本醒目的荧光黄绿网球严重脱色欠饱和褪变为发灰白黄色(C-L2, E2-L2, F-L1)。"
    },
    5803: {
        "score": 2.47,
        "severities": {"E1": "L2", "D": "L1", "F": "L1"},
        "note": "围坐男子手臂肤色与红色短袖T恤严重过饱和泛刺目深红铜色(E1-L2, D-L1, F-L1)。"
    },
    5804: {
        "score": 5.0,
        "severities": {"C": "L1", "E2": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：蛋糕盘下原本浓润的红棕色餐垫明显脱色泛暗灰褐色(C-L1, E2-L2, D-L1, F-L1)。"
    },
    5805: {
        "score": 2.73,
        "severities": {"C": "L2", "E2": "L2", "F": "L1"},
        "note": "雪道中央滑雪者身穿的亮荧光黄绿雪服严重脱色褪变为发暗脏灰绿(C-L2, E2-L2, F-L1)。"
    },
    5807: {
        "score": 5.0,
        "severities": {"E1": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：翻修房间粉刷的浅天蓝色乳胶漆墙面过饱和偏刺目深紫青蓝且门洞泛紫(E1-L2, D-L1, F-L1)。"
    },

    # Sheet 09
    5809: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：池塘背景水草植物原本鲜活翠绿系统性偏冷褪为发暗青蓝灰(D-L1, E2-L1, F-L1)。"
    },
    5810: {
        "score": 5.0,
        "severities": {"C": "L3", "E2": "L3", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：日本航空客机尾翼上标志性鲜艳朱红“鹤丸”标志大面积严重脱色褪为发暗灰黑粉色(C-L3, E2-L3, F-L2)。"
    },
    5813: {
        "score": 5.0,
        "severities": {"C": "L1", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：餐盘中的新鲜翠绿蔬菜沙拉严重偏黄褐枯萎暗沉(C-L1, D-L1, F-L1)。"
    },
    5815: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L1", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：白色快艇船身表面与金毛犬皮毛严重泛刺目深洋红与冷紫假色(C-L2, D-L1, F-L2)。"
    },
    5817: {
        "score": 2.73,
        "severities": {"C": "L3", "E1": "L2", "D": "L2", "F": "L3"},
        "note": "背景天空与街景建筑颠覆性严重错涂为刺眼发光的霓虹深洋红紫假色(C-L3, E1-L2, D-L2, F-L3)。"
    },
    5819: {
        "score": 5.0,
        "severities": {"C": "L1", "D": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：观景台前飞瀑溪流原本清澈碧绿的水体严重偏枯黄泥浆色(C-L1, D-L2, F-L1)。"
    },

    # Sheet 10
    5820: {
        "score": 2.32,
        "severities": {"C": "L2", "D": "L1", "F": "L2"},
        "note": "肖像照片中男子面部肤色大面积泛起不自然的冷青紫与暗灰斑块(C-L2, D-L1, F-L2)。"
    },
    5821: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：雨中合影人群原本明亮鲜艳的明黄色工装T恤大面积脱色欠饱和褪变为发灰枯黄(C-L2, E2-L2, F-L1)。"
    },
    5822: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L2", "E2": "L1", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：汹涌海浪原本深邃蔚蓝的深海水体大面积严重错涂为发暗泥浆红褐与深灰紫(C-L2, D-L2, E2-L1, F-L2)。"
    },
    5824: {
        "score": 4.55,
        "severities": {"C": "L2", "D": "L2", "E2": "L1", "F": "L2"},
        "note": "手持手机的手指与手背皮肤严重偏冷脱色泛发青灰蓝(C-L2, D-L2, E2-L1, F-L2)。"
    },
    5825: {
        "score": 2.36,
        "severities": {"C": "L3", "E1": "L2", "F": "L2"},
        "note": "广场古典街钟的深铁艺墨绿立柱与钟盘外壳颠覆性错涂为刺眼艳俗荧光青苹果绿(C-L3, E1-L2, F-L2)。"
    },
    5827: {
        "score": 5.0,
        "severities": {"E1": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：背景大楼红砖外立面与行人红色运动服过饱和偏刺目荧光深橙红(E1-L2, D-L1, F-L1)。"
    },

    # Sheet 11
    5828: {
        "score": 5.0,
        "severities": {"E1": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：棒球场内野红土与吉祥物紫色球衣过饱和泛刺目鲜橙红与荧光紫(E1-L2, D-L1, F-L1)。"
    },
    5830: {
        "score": 2.47,
        "severities": {"C": "L2", "D": "L1", "F": "L2"},
        "note": "笔记本电脑白色键盘上方功能键区域严重泛起发暗脏青绿色伪色杂斑(C-L2, D-L1, F-L2)。"
    },
    5831: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：广场立钟下方圆形花坛中原本娇艳的大红与明黄鲜花严重脱色欠饱和枯萎暗沉(C-L2, E2-L2, F-L1)。"
    },
    5834: {
        "score": 2.36,
        "severities": {"C": "L2", "D": "L2", "F": "L2"},
        "note": "体育场看台大面积洁白塑料座椅严重泛起刺眼发霉的青绿与深蓝紫斑驳假色(C-L2, D-L2, F-L2)。"
    },
    5835: {
        "score": 2.43,
        "severities": {"C": "L2", "E2": "L2", "D": "L1", "F": "L1"},
        "note": "铁轨工程作业车原本鲜艳夺目的明黄烤漆车体严重脱色发白变灰暗(C-L2, E2-L2, D-L1, F-L1)。"
    },
    5836: {
        "score": 2.47,
        "severities": {"C": "L3", "E2": "L3", "D": "L1", "F": "L2"},
        "note": "行李箱内原本鲜艳夺目的亮玫粉色内衣与白袜上的鲜红爱心图案被颠覆性彻底脱色错涂为纯暗灰白(C-L3, E2-L3, D-L1, F-L2)。"
    },

    # Sheet 12
    5837: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：越野摩托车油箱外壳原本鲜艳纯正的宝蓝烤漆大面积严重脱色欠饱和褪变为浅灰蓝(C-L2, E2-L2, F-L1)。"
    },
    5838: {
        "score": 5.0,
        "severities": {"E2": "L1", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：床单上小狗面部与耳部原本金棕栗色的毛斑明显脱色发灰暗沉(E2-L1, D-L1, F-L1)。"
    },
    5839: {
        "score": 2.3,
        "severities": {"E1": "L2", "D": "L1", "F": "L2"},
        "note": "街区夜景霓虹灯招牌与湿滑路面反光严重过饱和泛刺目深洋红与电光紫(E1-L2, D-L1, F-L2)。"
    },
    5840: {
        "score": 5.0,
        "severities": {"C": "L1", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：木围栏内的小猪皮毛原本自然的浅肉粉色严重脱色褪为苍白灰(C-L1, E2-L2, F-L1)。"
    },
    5841: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：小女孩身穿的娇艳玫粉色绸缎睡袍严重脱色变暗且泛冷青灰紫(C-L2, E2-L2, D-L1, F-L1)。"
    },
    5842: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：草丛中小狐狸原本浓润金黄红褐色的皮毛严重偏暗浑浊泛青灰土黄(C-L2, D-L1, E2-L1, F-L1)。"
    },

    # Sheet 13
    5845: {
        "score": 2.61,
        "severities": {"E1": "L2", "D": "L2", "F": "L2"},
        "note": "毛绒玩具泰迪熊原本清爽淡雅的灰褐绒毛严重过饱和偏浓烈焦糖深金红(E1-L2, D-L2, F-L2)。"
    },
    5847: {
        "score": 2.17,
        "severities": {"C": "L3", "D": "L2", "F": "L2"},
        "note": "长毛宠物犬柔顺皮毛与背景柔光伞原本浅粉紫光泽颠覆性错涂为阴暗发霉草绿黄调(C-L3, D-L2, F-L2)。"
    },
    5848: {
        "score": 5.0,
        "severities": {"C": "L1", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：主人身穿的浅天蓝色运动卫衣偏深浓艳泛刺目青紫蓝调(C-L1, D-L1, F-L1)。"
    },
    5849: {
        "score": 2.43,
        "severities": {"E1": "L2", "D": "L1", "F": "L2"},
        "note": "陈列架上的多彩丝绸丝巾与上方遮阳伞严重过饱和泛刺目深洋红紫假色(E1-L2, D-L1, F-L2)。"
    },
    5850: {
        "score": 1.07,
        "severities": {"C": "L3", "E2": "L3", "F": "L2"},
        "note": "两台电脑显示器屏幕中原本鲜艳纯正的深海蔚蓝桌面壁纸颠覆性彻底脱色错涂为深黑冷灰(C-L3, E2-L3, F-L2)。"
    },
    5851: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：奔跑边牧正追逐的鲜艳亮橙红玩具球严重脱色变暗褪为发灰暗土黄(C-L2, E2-L2, F-L1)。"
    },

    # Sheet 14
    5852: {
        "score": 5.0,
        "severities": {"C": "L1", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：生日纸盒上原本明亮醒目的黄色蜡烛棒明显脱色发灰变浅暗(C-L1, E2-L2, F-L1)。"
    },
    5854: {
        "score": 1.04,
        "severities": {"C": "L3", "E1": "L3", "D": "L2", "F": "L3"},
        "note": "棒球场大面积生机翠绿草坪颠覆性错涂为刺眼诡异的火红与深洋红色(C-L3, E1-L3, D-L2, F-L3)。"
    },
    5855: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：扎啤杯中金黄冰啤酒与餐盘内新鲜翠绿生菜沙拉大面积脱色欠饱和枯萎暗沉(C-L2, E2-L2, F-L1)。"
    },
    5856: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：面包中夹着的深红焦香烤热狗香肠大面积脱色褪变为苍白浅肉灰色(C-L2, E2-L2, F-L1)。"
    },
    5858: {
        "score": 2.43,
        "severities": {"C": "L2", "D": "L2", "F": "L2"},
        "note": "古典书房墙面与百叶窗原本温润明亮的米杏黄色严重偏向发暗脏绿冷青灰调(C-L2, D-L2, F-L2)。"
    },
    5860: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：铁轨红色调车机车车身原本纯正鲜亮的正红烤漆严重脱色褪变为发暗脏紫褐色(C-L2, E2-L2, D-L1, F-L1)。"
    },

    # Sheet 15
    5862: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：峡谷铁路货运机车车头原本纯正耀眼的明黄色工程烤漆严重脱色欠饱和变暗土黄(C-L2, E2-L2, D-L1, F-L1)。"
    },
    5863: {
        "score": 2.47,
        "severities": {"C": "L2", "D": "L1", "F": "L2"},
        "note": "圣诞客厅背景沙发与墙面严重泛起刺目深洋红与冷紫杂光(C-L2, D-L1, F-L2)。"
    },
    5864: {
        "score": 5.0,
        "severities": {"C": "L3", "E2": "L3", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：左侧女士身上原本鲜艳饱满的亮紫色长袖运动服颠覆性彻底脱色错涂为暗黑墨灰绿(C-L3, E2-L3, F-L2)。"
    },
    5865: {
        "score": 2.17,
        "severities": {"C": "L2", "E2": "L2", "D": "L2", "F": "L2"},
        "note": "卫生间原本温和明亮的杏黄米白墙面与洗手台颠覆性错涂为阴森发霉水泥暗青灰绿(C-L2, E2-L2, D-L2, F-L2)。"
    },
    5866: {
        "score": 2.27,
        "severities": {"C": "L2", "D": "L2", "E2": "L2", "F": "L2"},
        "note": "夕阳斜照下的木栈道与木质长椅原本温暖金红大面积严重偏冷泛发暗青灰紫(C-L2, D-L2, E2-L2, F-L2)。"
    },
    5868: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：高尔夫球场大面积生机草坪原本青翠鲜绿系统性偏冷泛暗青蓝发灰(D-L1, E2-L1, F-L1)。"
    },

    # Sheet 16
    5869: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：玩具模型屋卫生间墙壁原本温暖明净的金黄杏色大面积脱色褪为苍白灰(C-L2, E2-L2, D-L1, F-L1)。"
    },
    5870: {
        "score": 2.17,
        "severities": {"C": "L2", "D": "L2", "F": "L2"},
        "note": "拉马车的白马全身皮毛严重泛起发暗刺目的阴冷青灰绿杂色(C-L2, D-L2, F-L2)。"
    },
    5871: {
        "score": 2.43,
        "severities": {"E1": "L2", "D": "L1", "F": "L2"},
        "note": "棒球场后方防护挡墙与草坪过饱和泛刺目电光青蓝假色(E1-L2, D-L1, F-L2)。"
    },
    5874: {
        "score": 2.56,
        "severities": {"E1": "L2", "F": "L1"},
        "note": "浴室地面铺设的草绿色防滑地垫与挂毛巾严重过饱和泛刺目荧光翠绿(E1-L2, F-L1)。"
    },
    5876: {
        "score": 2.17,
        "severities": {"E1": "L2", "D": "L1", "F": "L2"},
        "note": "聚会男士面部肤色与额头严重过饱和泛刺目深洋红与冷紫假色(E1-L2, D-L1, F-L2)。"
    },
    5878: {
        "score": 5.0,
        "severities": {"C": "L1", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：越野车尾灯亮起原本鲜艳耀眼的刹车红光明显脱色变暗褪为发灰暗红粉色(C-L1, E2-L2, F-L1)。"
    },

    # Sheet 17
    5880: {
        "score": 4.46,
        "severities": {"C": "L1", "D": "L1", "F": "L1"},
        "note": "餐馆木质餐桌与背景墙面严重泛冷青暗黄绿杂色(C-L1, D-L1, F-L1)。"
    },
    5881: {
        "score": 4.55,
        "severities": {"C": "L3", "E2": "L3", "D": "L2", "F": "L2"},
        "note": "欧式哥特大教堂与议会大厦原本壮丽浓郁的金黄朝阳照射颠覆性彻底脱色错涂为惨淡水泥灰白(C-L3, E2-L3, D-L2, F-L2)。"
    },
    5882: {
        "score": 5.0,
        "severities": {"E1": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：餐盘内的意面番茄肉酱与香蕉严重过饱和浓艳刺目泛荧光深橙红(E1-L2, D-L1, F-L1)。"
    },
    5883: {
        "score": 1.2,
        "severities": {"C": "L3", "B": "L1", "D": "L1", "F": "L2"},
        "note": "砂石地上的消防栓原本鲜艳夺目的暖橙红工程防锈漆颠覆性严重错涂为脏暗芥末土黄色(C-L3, B-L1, D-L1, F-L2)。"
    },
    5888: {
        "score": 4.17,
        "severities": {"C": "L2", "D": "L1", "F": "L1"},
        "note": "地面放置的米白色帆布托特包表面严重泛发暗冷青灰蓝杂色(C-L2, D-L1, F-L1)。"
    },
    5890: {
        "score": 2.36,
        "severities": {"C": "L2", "D": "L2", "F": "L2"},
        "note": "沙滩冲浪者身上宝蓝色防晒服与周围金黄沙滩大面积严重偏冷泛暗青灰蓝调(C-L2, D-L2, F-L2)。"
    },

    # Sheet 18
    5891: {
        "score": 2.23,
        "severities": {"C": "L2", "E2": "L2", "F": "L1"},
        "note": "地板上两只小狗原本浓郁金黄暖红的皮毛严重脱色欠饱和变灰暗(C-L2, E2-L2, F-L1)。"
    },
    5893: {
        "score": 4.46,
        "severities": {"C": "L1", "E2": "L2", "F": "L1"},
        "note": "花瓶内插置的明黄与玫粉色菊花花束明显脱色欠饱和变暗枯黄(C-L1, E2-L2, F-L1)。"
    },
    5894: {
        "score": 2.47,
        "severities": {"C": "L1", "E2": "L2", "D": "L1", "F": "L1"},
        "note": "棒球赛场内野红土跑道原本浓郁纯正的陶土红褐色明显脱色泛暗土灰(C-L1, E2-L2, D-L1, F-L1)。"
    },
    5895: {
        "score": 4.23,
        "severities": {"C": "L3", "E2": "L3", "F": "L2"},
        "note": "沙滩上空翱翔的菱形风筝原本极度醒目的鲜艳明黄色颠覆性彻底脱色错涂为苍白水冷青灰(C-L3, E2-L3, F-L2)。"
    },
    5896: {
        "score": 2.17,
        "severities": {"C": "L2", "E1": "L2", "D": "L1", "F": "L2"},
        "note": "浴室马赛克瓷砖墙面与周围墙体严重泛起刺目荧光深洋红紫假色(C-L2, E1-L2, D-L1, F-L2)。"
    },
    5897: {
        "score": 2.36,
        "severities": {"C": "L2", "E1": "L2", "D": "L1", "F": "L1"},
        "note": "金属烤盘内两张披萨表面的融化芝士与番茄酱过饱和偏深焦红褐与暗青黄(C-L2, E1-L2, D-L1, F-L1)。"
    },

    # Sheet 19
    5902: {
        "score": 4.55,
        "severities": {"E1": "L2", "D": "L1", "F": "L1"},
        "note": "草场飞驰骏马原本深栗红褐色皮毛过饱和偏浓烈鲜亮橙红铜色(E1-L2, D-L1, F-L1)。"
    },
    5904: {
        "score": 5.0,
        "severities": {"C": "L3", "E2": "L3", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：宠物生日蛋糕表面原本娇艳纯正的鲜粉红玫瑰糖花彻底脱色错涂为苍白米黄肉色(C-L3, E2-L3, F-L2)。"
    },
    5907: {
        "score": 5.0,
        "severities": {"C": "L1", "E2": "L1", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：小女孩身穿的粉红碎花上衣明显脱色且背景墙面泛冷青紫暗影(C-L1, E2-L1, D-L1, F-L1)。"
    },
    5908: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：林间棕熊原本厚重深邃的棕黑皮毛大面积偏发锈红橙与脏黄褐色(C-L2, D-L2, F-L1)。"
    },
    5909: {
        "score": 4.46,
        "severities": {"C": "L2", "D": "L2", "E2": "L1", "F": "L2"},
        "note": "古典欧式客厅原本浓郁温馨的浅金暖黄灯光环境大面积被冲淡错涂为冰冷浅青灰(C-L2, D-L2, E2-L1, F-L2)。"
    },
    5911: {
        "score": 2.43,
        "severities": {"C": "L2", "E1": "L2", "D": "L1", "F": "L2"},
        "note": "篮球馆看台观众席与上方电子计分牌严重泛起刺目荧光深洋红紫假色(C-L2, E1-L2, D-L1, F-L2)。"
    },

    # Sheet 20
    5912: {
        "score": 2.23,
        "severities": {"E1": "L2", "D": "L1", "F": "L1"},
        "note": "切角披萨表面的番茄酱与旁边可乐罐严重过饱和泛刺目深洋红紫假色(E1-L2, D-L1, F-L1)。"
    },
    5916: {
        "score": 2.61,
        "severities": {"C": "L2", "D": "L2", "F": "L2"},
        "note": "城市快速路夜景路面与远景建筑严重泛起刺目深紫红与冷青暗色杂光(C-L2, D-L2, F-L2)。"
    },
    5918: {
        "score": 5.0,
        "severities": {"C": "L1", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：户外野餐桌上摆放的果酱罐与餐具明显脱色欠饱和变暗(C-L1, E2-L2, F-L1)。"
    },
    5919: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：雪山绝壁上空原本高远纯净的湛蓝天空明显脱色冲淡偏苍白灰蓝(D-L1, E2-L1, F-L1)。"
    },
    5920: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：放风筝草坪原本生机盎然的翠绿色大面积偏枯黄暗淡欠饱和(D-L1, E2-L2, F-L1)。"
    },
    5921: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：飞流直下的瀑布水体与深潭原本清澈碧绿的水色严重错涂为发暗泥浆土黄色(C-L2, D-L1, F-L1)。"
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

FORBIDDEN_WORDS = ["关键区域", "某些区域", "局部区域", "某些物体", "关键主体", "特定区域", "画面局部"]

def validate_reviews(reviews):
    """严格断言词汇与逻辑规范"""
    for tid, r in reviews.items():
        note = r.get("note", "")
        # 1. 禁用词校验
        for w in FORBIDDEN_WORDS:
            if w in note:
                raise ValueError(f"Task #{tid} 评语包含违禁抽象代词: '{w}' -> {note}")
        
        sevs = r.get("severities", {})
        # 2. 互斥断言: E1 与 E2 不能共存
        if "E1" in sevs and "E2" in sevs:
            raise ValueError(f"Task #{tid} 同时包含互斥的 E1 与 E2 缺陷！")
        
        # 3. 熔断断言: A 项不能有 L1~L3 严重度
        if "A" in sevs and sevs["A"] != "":
            raise ValueError(f"Task #{tid} A项缺色不得有级别！必须为空字符串。")
    print(f"[PASS] 词汇与逻辑规范 100% 通过（共 {len(reviews)} 组）")

def build_defects_list(severities, note):
    """根据严重度字典构建标准缺陷列表"""
    defects = []
    # 按照标准顺序排列
    order = ["A", "B", "C", "D", "E1", "E2", "F"]
    for code in order:
        if code in severities:
            sev = severities[code]
            desc = note
            # 若包含原5.0满分严重漏检前缀，在 description 中清洗前缀
            clean_desc = re.sub(r"^原\s*5\.0\s*满分严重漏检，核查发现：\s*", "", desc)
            clean_desc = re.sub(r"^核查发现：\s*", "", clean_desc)
            defects.append({
                "id": code,
                "name": DEFECT_NAMES[code],
                "severity": sev,
                "description": clean_desc
            })
    return defects

def apply_and_sync():
    validate_reviews(REVIEWS_B28)

    # 1. 保存中间定物 JSON
    out_grounding_path = "LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_28.json"
    grounding_data = {}
    for tid, r in REVIEWS_B28.items():
        grounding_data[str(tid)] = {
            "score": r["score"],
            "severities": r["severities"],
            "note": r["note"],
            "defects": build_defects_list(r["severities"], r["note"])
        }
    with open(out_grounding_path, "w", encoding="utf-8") as f:
        json.dump(grounding_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] 中间定物字典已保存: {out_grounding_path}")

    # 2. 更新 exports/reviewed_1_10000_all.json
    all_file = "LS_lcad_reviewer/exports/reviewed_1_10000_all.json"
    with open(all_file, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    applied_all_count = 0
    pass_count = 0
    revise_count = 0
    for ann in all_data["annotations"]:
        tid = ann["human_review"]["task_id"]
        if tid in REVIEWS_B28:
            r = REVIEWS_B28[tid]
            sevs = r["severities"]
            note = r["note"]
            
            # 判断是否为放行
            if len(sevs) == 0:
                ann["defects"] = []
                ann["review_note"] = "审查通过"
                ann["reviewed_score"] = None
                ann["needs_rescoring"] = True
                pass_count += 1
            else:
                ann["defects"] = build_defects_list(sevs, note)
                ann["review_note"] = note
                if "A" in sevs:
                    ann["reviewed_score"] = 1.0
                    ann["needs_rescoring"] = False
                else:
                    ann["reviewed_score"] = None
                    ann["needs_rescoring"] = True
                revise_count += 1
            ann["review_status"] = "已核验"
            applied_all_count += 1

    with open(all_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] 同步至 all 版本: {all_file}")
    print(f"   - 成功覆盖: {applied_all_count} 组 (其中 PASS: {pass_count} 例, REVISE: {revise_count} 例)")

    # 3. 更新 exports/reviewed_1_10000_clean.json
    clean_file = "LS_lcad_reviewer/exports/reviewed_1_10000_clean.json"
    with open(clean_file, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    applied_clean_count = 0
    for ann in clean_data["annotations"]:
        tid = ann["human_review"]["task_id"]
        if tid in REVIEWS_B28:
            r = REVIEWS_B28[tid]
            sevs = r["severities"]
            note = r["note"]
            
            if len(sevs) == 0:
                ann["defects"] = []
                ann["review_note"] = ""
                ann["reviewed_score"] = None
                ann["needs_rescoring"] = True
            else:
                ann["defects"] = build_defects_list(sevs, note)
                ann["review_note"] = ""
                if "A" in sevs:
                    ann["reviewed_score"] = 1.0
                    ann["needs_rescoring"] = False
                else:
                    ann["reviewed_score"] = None
                    ann["needs_rescoring"] = True
            ann["review_status"] = "已核验"
            applied_clean_count += 1

    with open(clean_file, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] 同步至 clean 版本: {clean_file}")
    print(f"   - 成功覆盖: {applied_clean_count} 组 (其中 PASS: {pass_count} 例, REVISE: {revise_count} 例)")
    print("=== Batch 28 审校应用同步完毕！ ===")

if __name__ == "__main__":
    apply_and_sync()
