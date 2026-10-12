#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_remaining_batch_13.py
根据对 Batch 13（Tasks 2673 ~ 2903，共 120 组）的 20 张高清看板多模态大图直审结果，
1. 生成中间定物审计文件 grounding_remaining_batch_13.json；
2. 同步更新 reviewed_1_10000_all.json（包含精准具象定物陈述或审查通过）；
3. 同步更新 reviewed_1_10000_clean.json（全量 10,000 条保持 review_note: ""）；
4. 运行严格格式契约验证。
"""

import json
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
AUDITS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits"
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"

ALL_EXPORT = EXPORTS_DIR / "reviewed_1_10000_all.json"
CLEAN_EXPORT = EXPORTS_DIR / "reviewed_1_10000_clean.json"
OUT_GROUNDING_FILE = AUDITS_DIR / "grounding_remaining_batch_13.json"

DEFECT_NAMES = {
    "A": "缺色",
    "B": "溢色",
    "C": "错色",
    "D": "偏色",
    "E1": "过饱和",
    "E2": "欠饱和",
    "F": "视觉自然度"
}

# 120 组任务的直审定物字典
REVIEWS = {
    # Sheet 01: [2673, 2674, 2677, 2681, 2682, 2683]
    2673: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2", "C": "L2"},
        "note": "日式餐馆门头金黄暖色照明与红色装饰门帘被严重漂染脱色为冰冷青暗灰色，夜晚温馨街景氛围严重受损（偏色 D-L2，欠饱和 E2-L2，错色 C-L2）。"
    },
    2674: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2677: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2681: {
        "is_pass": False,
        "severities": {"E2": "L1", "D": "L1"},
        "note": "街头推婴儿车行人身穿的粉红格子衬衫与婴儿推车红色漆面色泽略显暗淡泛灰（轻度欠饱和 E2-L1，轻度偏色 D-L1）。"
    },
    2682: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "卡通消防栓底座鲜艳粉红色与侧面配件常识性严重错涂为暗沉红褐色（严重错色 C-L3，欠饱和 E2-L2）。"
    },
    2683: {
        "is_pass": False,
        "severities": {"D": "L3", "C": "L2"},
        "note": "城市天际线落日余晖中金黄绚丽的晚霞被大面积严重错涂漂染为冰冷的水蓝色，黄昏天光意境严重倒错（严重偏色 D-L3，常识错色 C-L2）。"
    },

    # Sheet 02: [2686, 2687, 2690, 2691, 2693, 2694]
    2686: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L3"},
        "note": "快艇上男子身穿的鲜艳亮红色救生防护服被严重剥色错涂为纯黑色（严重常识错色 C-L3，严重欠饱和 E2-L3）。"
    },
    2687: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L1"},
        "note": "车窗外庭院地面原本鲜明的红砖铺地被大面积脱色误涂为暗冷水泥灰色（常识错色 C-L2，轻度欠饱和 E2-L1）。"
    },
    2690: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2691: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2", "D": "L1"},
        "note": "餐桌烘焙羊角面包与金黄馅饼色泽暗淡发灰，右侧火腿切片鲜艳粉红严重脱色变白（错色 C-L2，欠饱和 E2-L2，偏色 D-L1）。"
    },
    2693: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2694: {
        "is_pass": False,
        "severities": {"C": "L3", "F": "L2"},
        "note": "窗台停歇的小鹦鹉头顶与胸腹部原本鲜艳的大红色羽毛被常识性严重错涂为发暗的灰绿色杂色（严重错色 C-L3，视觉自然度受损 F-L2）。"
    },

    # Sheet 03: [2695, 2696, 2697, 2698, 2701, 2704]
    2695: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "山坡上红色砖石建筑群原本鲜明的砖红色彩被大面积剥色退化为冷灰色，红砖质感严重丧失（错色 C-L2，欠饱和 E2-L2）。"
    },
    2696: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L1"},
        "note": "电脑办公桌红棕色实木台面整体泛发暗冷灰偏色，失去木质温润光泽（偏色 D-L2，轻度欠饱和 E2-L1）。"
    },
    2697: {
        "is_pass": False,
        "severities": {"D": "L2", "F": "L1"},
        "note": "复古餐厅木质圆桌、餐椅与背景墙面被大面积涂染为浑浊沉闷的焦糖暗黄褐色（偏色 D-L2，视觉自然度受损 F-L1）。"
    },
    2698: {
        "is_pass": False,
        "severities": {"D": "L3", "E2": "L2", "C": "L2"},
        "note": "海滨沙滩上空落日晚霞绚丽暖黄霞光被彻底漂变为冰冷暗灰蓝色，海面波光色彩同步冷化（严重偏色 D-L3，欠饱和 E2-L2，错色 C-L2）。"
    },
    2701: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "斑马脚下原本生机勃勃的鲜绿色草坪被严重大面积脱色误涂为苍白枯黄色（严重常识错色 C-L3，欠饱和 E2-L2）。"
    },
    2704: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "斑马身后灌木树丛原本翠绿的枝叶色调变暗泛枯褐灰色（轻度偏色 D-L1，轻度欠饱和 E2-L1）。"
    },

    # Sheet 04: [2705, 2707, 2710, 2711, 2716, 2717]
    2705: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "欧式白色圆顶凉亭基座周围鲜艳紫红色杜鹃花丛严重脱色误涂为暗淡枯褐色（严重常识错色 C-L3，欠饱和 E2-L2）。"
    },
    2707: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L1"},
        "note": "丹佛会展中心玻璃幕墙前巨型大熊雕塑鲜艳深宝蓝色被常识性严重错涂为发暗墨绿色（严重常识错色 C-L3，偏色 D-L1）。"
    },
    2710: {
        "is_pass": False,
        "severities": {"D": "L2", "F": "L2"},
        "note": "桌面上摆放的毛绒玩偶熊与背景桌面被严重涂染为突兀刺眼的荧光粉紫偏色（偏色 D-L2，视觉自然度受损 F-L2）。"
    },
    2711: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2716: {
        "is_pass": False,
        "severities": {"D": "L3", "E2": "L2"},
        "note": "客厅木质地板与墙面装饰壁灯温馨暖黄光泽彻底漂变为冰冷暗青灰色（严重偏色 D-L3，欠饱和 E2-L2）。"
    },
    2717: {
        "is_pass": False,
        "severities": {"D": "L1", "F": "L1"},
        "note": "复古展示车车顶漆面与挡风玻璃暗部微泛青蓝冷色杂斑（轻度偏色 D-L1，轻度自然度受损 F-L1）。"
    },

    # Sheet 05: [2718, 2719, 2723, 2726, 2727, 2728]
    2718: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2719: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2", "D": "L1"},
        "note": "枝头冠鸠腹部原本柔和的粉红羽毛严重脱色误涂为暗冷灰色（错色 C-L2，欠饱和 E2-L2，轻度偏色 D-L1）。"
    },
    2723: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2726: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "雪地树林徒步人员身穿的亮黄色与深红色羽绒服大面积褪色发暗，鲜明防寒服辨识度降低（错色 C-L2，欠饱和 E2-L2）。"
    },
    2727: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2728: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L3", "F": "L3"},
        "note": "烘焙披萨表面原本金黄焦香的融化芝士与番茄红酱恶性错涂为大片发紫变质般的暗紫黑色，严重毁坏食欲（恶性错色 C-L3，严重偏色 D-L3，视觉自然度极度恶化 F-L3）。"
    },

    # Sheet 06: [2730, 2731, 2732, 2737, 2738, 2739]
    2730: {
        "is_pass": False,
        "severities": {"E1": "L1", "F": "L1"},
        "note": "游客身穿的红色短袖上衣在阳光直射下高光过饱和略显刺眼（轻度过饱和 E1-L1，视觉自然度轻度受损 F-L1）。"
    },
    2731: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2732: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2"},
        "note": "幼童脚下踩踏的鲜艳玫红色塑料平衡踏板被常识性严重错涂为亮蓝色（严重常识错色 C-L3，偏色 D-L2）。"
    },
    2737: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "办公隔间天蓝色桌上隔板被严重剥色退化为冰冷暗水泥灰色（错色 C-L2，欠饱和 E2-L2）。"
    },
    2738: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2739: {
        "is_pass": False,
        "severities": {"C": "L3", "F": "L2"},
        "note": "草坪上飞盘少年身穿的鲜艳亮红色运动T恤被常识性严重错涂为深蓝紫色（严重常识错色 C-L3，视觉自然度受损 F-L2）。"
    },

    # Sheet 07: [2740, 2741, 2745, 2746, 2747, 2749]
    2740: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L3"},
        "note": "铁道沿线鲜绿色护坡草坪严重大面积脱色误涂为干枯灰褐泥土色（严重常识错色 C-L3，严重欠饱和 E2-L3）。"
    },
    2741: {
        "is_pass": False,
        "severities": {"D": "L1", "F": "L1"},
        "note": "拉链行李箱内收纳衣物折痕处微泛紫红杂色伪色（轻度偏色 D-L1，轻度自然度受损 F-L1）。"
    },
    2745: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L3"},
        "note": "草坪跳跃青年原本身穿的亮黄色短袖T恤被彻底脱色剥除为惨灰白色（严重常识错色 C-L3，严重欠饱和 E2-L3）。"
    },
    2746: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "网球场看台西铁城赞助商深蓝色背景挡板严重脱色误涂为暗冷灰色（错色 C-L2，欠饱和 E2-L2）。"
    },
    2747: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L2", "B": "L2", "F": "L2"},
        "note": "黄昏街道上空突兀出现大面积失真的荧光洋红伪色光斑且边缘严重溢色（偏色 D-L2，过饱和 E1-L2，溢色 B-L2，视觉自然度受损 F-L2）。"
    },
    2749: {
        "is_pass": False,
        "severities": {"D": "L3", "E2": "L3"},
        "note": "卫生间马桶上方暖黄褐壁纸被彻底漂白剥变为冰冷水泥灰白色（严重偏色 D-L3，严重欠饱和 E2-L3）。"
    },

    # Sheet 08: [2752, 2753, 2755, 2756, 2757, 2763]
    2752: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "庭院草坪原本深沉的草绿色大面积泛黄偏亮，绵羊毛发微泛冷灰（轻度偏色 D-L1，轻度欠饱和 E2-L1）。"
    },
    2753: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2755: {
        "is_pass": False,
        "severities": {"D": "L2", "F": "L3"},
        "note": "车库停放的定制摩托车金属车体被大面积染上刺眼荧光紫红杂色，金属质感严重破坏（偏色 D-L2，视觉自然度极度恶化 F-L3）。"
    },
    2756: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "露天休闲平台深紫色沙发软垫被严重脱色误涂为暗冷灰色（错色 C-L2，欠饱和 E2-L2）。"
    },
    2757: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2"},
        "note": "黑犬嘴中叼着的鲜绿色塑料飞盘被常识性严重错涂为浅天蓝色（严重常识错色 C-L3，偏色 D-L2）。"
    },
    2763: {
        "is_pass": False,
        "severities": {"A": ""},
        "note": "熔断项 A 命中：全域上色彻底失败呈现纯灰度黑白画面，未产生任何色彩信息（熔断项 A 缺色）。"
    },

    # Sheet 09: [2764, 2766, 2771, 2772, 2778, 2780]
    2764: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "牛仔裤腰际悬挂的手工皮质小包鲜艳大红色被严重错涂为暗淡土黄色（严重常识错色 C-L3，欠饱和 E2-L2）。"
    },
    2766: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "沙滩冲浪手鲜艳橙红冲浪板大面积剥色退化为灰米色（错色 C-L2，欠饱和 E2-L2）。"
    },
    2771: {
        "is_pass": False,
        "severities": {"C": "L2", "D": "L2", "E2": "L1"},
        "note": "聚会背景喜庆红褐色印花壁纸大面积剥色错涂为冷青灰色（错色 C-L2，偏色 D-L2，欠饱和 E2-L1）。"
    },
    2772: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2778: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "办公室左侧墙面淡蓝色墙漆大面积剥色褪化为惨白灰水泥色（错色 C-L2，欠饱和 E2-L2）。"
    },
    2780: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "电脑桌置物架顶层鲜红色圆形容器罐严重脱色错涂为暗黑灰色（严重常识错色 C-L3，欠饱和 E2-L2）。"
    },

    # Sheet 10: [2784, 2787, 2788, 2789, 2794, 2796]
    2784: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L3"},
        "note": "蒸汽机车头展示背景柠檬黄墙面大面积剥色错涂为冷灰色（严重常识错色 C-L3，严重欠饱和 E2-L3）。"
    },
    2787: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2788: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2789: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "机动三轮车车厢侧挡板亮黄色与橙色漆面严重错涂脱色为暗青灰泥土色（严重常识错色 C-L3，欠饱和 E2-L2）。"
    },
    2794: {
        "is_pass": False,
        "severities": {"E2": "L1", "D": "L1"},
        "note": "斑马展区背景树木枝叶原本嫩绿色彩略微欠饱和泛冷灰（轻度欠饱和 E2-L1，轻度偏色 D-L1）。"
    },
    2796: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "网球场底线后方深蓝色 POLO 赞助商广告挡板严重脱色错涂为冷青灰色（错色 C-L2，欠饱和 E2-L2）。"
    },

    # Sheet 11: [2804, 2805, 2808, 2809, 2811, 2812]
    2804: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2"},
        "note": "铁丝网后击球手深海蓝色棒球比赛服被常识性严重错涂为鲜红粉色（严重常识错色 C-L3，偏色 D-L2）。"
    },
    2805: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "皮沙发扶手天蓝色雪尼尔除尘手套严重剥色错涂为纯白灰色（错色 C-L2，欠饱和 E2-L2）。"
    },
    2808: {
        "is_pass": False,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "金毛猎犬金黄毛发表层强光照射处偏浓微泛暖红偏色（轻度偏色 D-L1，轻度过饱和 E1-L1）。"
    },
    2809: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2811: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L2", "F": "L3"},
        "note": "聚会餐桌印花桌布与背景墙面被严重涂染为刺眼不自然的荧光紫红色调（偏色 D-L2，过饱和 E1-L2，视觉自然度极度恶化 F-L3）。"
    },
    2812: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 12: [2814, 2815, 2818, 2819, 2820, 2825]
    2814: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2815: {
        "is_pass": False,
        "severities": {"D": "L1", "F": "L1"},
        "note": "男子飞盘运动面部肤色出现局部暗红泛紫杂斑（轻度偏色 D-L1，视觉自然度轻度受损 F-L1）。"
    },
    2818: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L2", "F": "L3"},
        "note": "露天泳池庭院木桌与墙面被大面积染上刺眼荧光洋红与紫红偏色（偏色 D-L2，过饱和 E1-L2，视觉自然度极度恶化 F-L3）。"
    },
    2819: {
        "is_pass": False,
        "severities": {"D": "L1", "F": "L1"},
        "note": "卫生间洗手台镜前灯光照区域过饱和泛发红暖黄色偏（轻度偏色 D-L1，视觉自然度轻度受损 F-L1）。"
    },
    2820: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "雪地滑雪运动员防寒服微泛色偏，雪地微泛青冷暗淡（轻度偏色 D-L1，轻度欠饱和 E2-L1）。"
    },
    2825: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 13: [2826, 2827, 2828, 2829, 2830, 2832]
    2826: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2827: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2", "D": "L1"},
        "note": "水族馆观赏窗口透出的蔚蓝水体被大面积剥色退化为冰冷灰白色，水中白鲸游动的水体生机彻底丧失（严重常识错色 C-L3，欠饱和 E2-L2，偏色 D-L1）。"
    },
    2828: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2829: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "沙发上男子身穿的鲜艳亮蓝色短袖T恤被常识性严重错涂剥除为发暗灰白色，左侧红靠垫严重褪色发暗（严重常识错色 C-L3，欠饱和 E2-L2）。"
    },
    2830: {
        "is_pass": False,
        "severities": {"E1": "L2", "D": "L1", "F": "L2"},
        "note": "客舱座椅靠背深蓝色与乘客身穿的浅黄绿衬衫过度浓艳刺眼，机舱光影呈现不自然荧光感（过饱和 E1-L2，轻度偏色 D-L1，视觉自然度受损 F-L2）。"
    },
    2832: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L1"},
        "note": "室内百叶窗与窗台墙面大面积严重泛发浑浊焦黄偏色，窗外绿植色彩微暗（偏色 D-L2，轻度欠饱和 E2-L1）。"
    },

    # Sheet 14: [2833, 2834, 2835, 2837, 2839, 2840]
    2833: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2", "E2": "L2"},
        "note": "户外绿意盎然的夏日草坪与树林被严重错涂为枯黄红褐色的深秋落叶色泽，右侧儿童绿衣脱色发灰（严重常识错色 C-L3，偏色 D-L2，欠饱和 E2-L2）。"
    },
    2834: {
        "is_pass": False,
        "severities": {"D": "L1", "F": "L1"},
        "note": "庭院木质长椅表面与背景草地部分反光处偏浓且微泛冷青偏色，呈现轻微不自然伪色（轻度偏色 D-L1，轻度自然度受损 F-L1）。"
    },
    2835: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2", "F": "L2"},
        "note": "夜间派对男子身穿的深蓝色短袖T恤被常识性严重错涂为暗紫红褐色，背景与肤色泛暗红偏色（严重常识错色 C-L3，偏色 D-L2，视觉自然度受损 F-L2）。"
    },
    2837: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L1"},
        "note": "书房室内墙面与电脑书桌周边大面积严重偏暖泛黄褐调，背光暗部微暗（偏色 D-L2，轻度欠饱和 E2-L1）。"
    },
    2839: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "海滩遮阳伞原本鲜艳明亮的橙红色相间条纹被严重脱色错涂为暗淡黄灰色，鲜活色彩彻底退化丧失（严重常识错色 C-L3，欠饱和 E2-L2）。"
    },
    2840: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 15: [2842, 2843, 2844, 2846, 2847, 2851]
    2842: {
        "is_pass": False,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "note": "庭院草坪背阴树影与木质甲板表面微泛青蓝冷色杂斑，高光反光略显浓艳（轻度偏色 D-L1，轻度过饱和 E1-L1，视觉自然度轻度受损 F-L1）。"
    },
    2843: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2844: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2846: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L1"},
        "note": "小女孩身后的室内靠垫与背景墙面大面积泛发暗冷青灰色调，人物肤色与服饰暖意脱色发暗（偏色 D-L2，轻度欠饱和 E2-L1）。"
    },
    2847: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2851: {
        "is_pass": False,
        "severities": {"E2": "L2", "D": "L1"},
        "note": "斑马站立的草地与周围灌木林地生机翠绿色彩严重发灰脱色，全图微泛冷青偏色（欠饱和 E2-L2，轻度偏色 D-L1）。"
    },

    # Sheet 16: [2855, 2856, 2859, 2861, 2863, 2864]
    2855: {
        "is_pass": False,
        "severities": {"E2": "L1", "D": "L1"},
        "note": "沙滩长尾木船船头悬挂的鲜红与粉红多彩装饰丝带色泽轻度褪色发暗（轻度欠饱和 E2-L1，轻度偏色 D-L1）。"
    },
    2856: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L1", "F": "L1"},
        "note": "阳光房室内木地板与窗外绿植树叶整体严重偏暖泛黄褐调，强光照射区域略显过饱和（偏色 D-L2，轻度过饱和 E1-L1，视觉自然度轻度受损 F-L1）。"
    },
    2859: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "会议室背景悬挂的加拿大枫叶国旗鲜艳正红条纹被严重剥色错涂为冷灰水泥色，代表性鲜红辨识度完全剥除（严重常识错色 C-L3，欠饱和 E2-L2）。"
    },
    2861: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L1"},
        "note": "西餐厅实木餐桌整体被严重错涂漂变为冰冷暗青灰色调，盘中熟蔬菜鲜艳色泽脱色褪淡（偏色 D-L2，轻度欠饱和 E2-L1）。"
    },
    2863: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2864: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 17: [2865, 2866, 2868, 2869, 2870, 2873]
    2865: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L1", "F": "L1"},
        "note": "厨房背景橱柜、门框与墙壁严重偏暖泛发砖红偏色，红木色调略显浓艳（偏色 D-L2，轻度过饱和 E1-L1，视觉自然度轻度受损 F-L1）。"
    },
    2866: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2"},
        "note": "海边沙滩大面积泛发暗冷青灰偏色，沙滩暖黄金色质感严重褪色丧失（偏色 D-L2，欠饱和 E2-L2）。"
    },
    2868: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2", "B": "L2", "F": "L3"},
        "note": "晴朗蔚蓝的纯净天空被恶性错涂漂染为大片沉闷紫粉色，且小狗身体边缘溢色明显，画面视觉可信度严重受损（严重常识错色 C-L3，偏色 D-L2，溢色 B-L2，视觉自然度严重恶化 F-L3）。"
    },
    2869: {
        "is_pass": False,
        "severities": {"C": "L2", "D": "L1"},
        "note": "餐盘后方玻璃碗盛放的深色蘸酱被错涂为浅黄绿色，甜甜圈外皮略微偏淡发黄（错色 C-L2，轻度偏色 D-L1）。"
    },
    2870: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "海滨广场空中跳跃滑板青年身后蔚蓝天空上层微泛轻微暗青偏色（轻度偏色 D-L1）。"
    },
    2873: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 18: [2874, 2877, 2878, 2880, 2881, 2882]
    2874: {
        "is_pass": False,
        "severities": {"E1": "L2", "D": "L1", "F": "L1"},
        "note": "户外生锈铁皮箱表面的红褐铁锈过度浓艳刺眼，全图微泛暖黄红偏色，铁皮质感失真（过饱和 E1-L2，轻度偏色 D-L1，视觉自然度轻度受损 F-L1）。"
    },
    2877: {
        "is_pass": False,
        "severities": {"E1": "L2", "D": "L1"},
        "note": "集市上成捆堆积的香蕉鲜黄色泽过于浓艳刺眼，全图微泛暖黄偏色（过饱和 E1-L2，轻度偏色 D-L1）。"
    },
    2878: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2880: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2881: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2882: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L1", "F": "L1"},
        "note": "书桌台面与书籍封面大面积偏暖泛发红焦黄调，暖光高光区域略显浓艳（偏色 D-L2，轻度过饱和 E1-L1，视觉自然度轻度受损 F-L1）。"
    },

    # Sheet 19: [2884, 2886, 2887, 2889, 2891, 2892]
    2884: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2886: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "被厚雪覆盖的树林积雪与枯枝树干暗部微泛冷青偏色，雪景还原忠实但色温略显单一（轻度偏色 D-L1）。"
    },
    2887: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2889: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2891: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2892: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2", "E2": "L2"},
        "note": "浴室洗手台镜面与墙面瓷砖未能还原原图特有的浓烈黄绿环境光源，整体严重偏冷漂白为冷灰色（严重常识错色 C-L3，偏色 D-L2，欠饱和 E2-L2）。"
    },

    # Sheet 20: [2893, 2894, 2895, 2896, 2900, 2903]
    2893: {
        "is_pass": False,
        "severities": {"E2": "L1", "D": "L1"},
        "note": "海滨沙滩漫步游客身穿的彩色防风服饰与空中风筝色彩轻微褪色脱色，沙滩微泛暖色偏（轻度欠饱和 E2-L1，轻度偏色 D-L1）。"
    },
    2894: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2"},
        "note": "卫生间木隔断与墙面被严重漂染为冰冷深青灰色调，原图温馨暖木色调严重丧失（偏色 D-L2，欠饱和 E2-L2）。"
    },
    2895: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L1", "F": "L1"},
        "note": "厨房灶台大铁锅蒸腾热气与周围环境微泛青蓝冷色偏，锅具边缘色彩偏浓（偏色 D-L2，轻度过饱和 E1-L1，视觉自然度轻度受损 F-L1）。"
    },
    2896: {
        "is_pass": False,
        "severities": {"C": "L2", "D": "L2", "E2": "L2"},
        "note": "水塘边原本暖黄的大地泥土与干草垛被错涂脱色为苍白冷灰色，牛群毛皮色彩发灰褪色（错色 C-L2，偏色 D-L2，欠饱和 E2-L2）。"
    },
    2900: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L1"},
        "note": "棒球场看台后方红砖建筑外墙上的橙红色大型商业广告牌被常识性严重错涂为浅草绿色（严重常识错色 C-L3，轻度欠饱和 E2-L1）。"
    },
    2903: {
        "is_pass": False,
        "severities": {"D": "L3", "E1": "L2", "F": "L3"},
        "note": "复古客厅墙面壁纸、老式电视机外壳与书架大面积被严重涂染为刺眼不自然的荧光紫红偏色（严重偏色 D-L3，过饱和 E1-L2，视觉自然度极度恶化 F-L3）。"
    }
}

def main():
    print(f"Total reviews defined: {len(REVIEWS)}")
    assert len(REVIEWS) == 120, f"Expected 120 reviews, got {len(REVIEWS)}"

    # 1. 验证所有 defect descriptions 均符合具象实体定物规则（消灭抽象代词）
    abstract_words = ["局部关键区域", "关键主体或背景", "局部区域", "轮廓边缘处", "关键区域"]
    for tid, rev in REVIEWS.items():
        note = rev["note"]
        for w in abstract_words:
            assert w not in note, f"Task #{tid} contains abstract word '{w}': {note}"

    # 2. 生成中间定物审计文件
    grounding_data = {}
    for tid, rev in REVIEWS.items():
        grounding_data[str(tid)] = {
            "task_id": tid,
            "is_pass": rev["is_pass"],
            "severities": rev["severities"],
            "note": rev["note"]
        }
    with open(OUT_GROUNDING_FILE, "w", encoding="utf-8") as f:
        json.dump(grounding_data, f, ensure_ascii=False, indent=2)
    print(f"Saved grounding audit to {OUT_GROUNDING_FILE}")

    # 3. 同步更新 reviewed_1_10000_all.json
    print(f"Loading {ALL_EXPORT}...")
    with open(ALL_EXPORT, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    all_map = {ann["human_review"]["task_id"]: ann for ann in all_data["annotations"]}
    updated_count = 0

    for tid, rev in REVIEWS.items():
        if tid not in all_map:
            print(f"Warning: Task #{tid} not found in {ALL_EXPORT}")
            continue
        ann = all_map[tid]
        is_pass = rev["is_pass"]
        sevs = rev["severities"]
        note = rev["note"]

        if is_pass:
            ann["defects"] = []
            ann["review_note"] = "审查通过"
            ann["reviewed_score"] = None
            ann["needs_rescoring"] = True
        else:
            def_list = []
            for did, sev in sevs.items():
                def_list.append({
                    "id": did,
                    "name": DEFECT_NAMES[did],
                    "severity": sev,
                    "description": note
                })
            ann["defects"] = def_list
            ann["review_note"] = note
            if "A" in sevs:
                ann["reviewed_score"] = 1.0
                ann["needs_rescoring"] = False
            else:
                ann["reviewed_score"] = None
                ann["needs_rescoring"] = True

        ann["review_status"] = "已核验"
        updated_count += 1

    with open(ALL_EXPORT, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {updated_count} items in {ALL_EXPORT}")

    # 4. 同步更新 reviewed_1_10000_clean.json
    print(f"Loading {CLEAN_EXPORT}...")
    with open(CLEAN_EXPORT, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    clean_map = {ann["human_review"]["task_id"]: ann for ann in clean_data["annotations"]}

    for tid, rev in REVIEWS.items():
        if tid not in clean_map:
            continue
        ann = clean_map[tid]
        is_pass = rev["is_pass"]
        sevs = rev["severities"]
        note = rev["note"]

        if is_pass:
            ann["defects"] = []
            ann["review_note"] = ""
            ann["reviewed_score"] = None
            ann["needs_rescoring"] = True
        else:
            def_list = []
            for did, sev in sevs.items():
                def_list.append({
                    "id": did,
                    "name": DEFECT_NAMES[did],
                    "severity": sev,
                    "description": note
                })
            ann["defects"] = def_list
            ann["review_note"] = ""
            if "A" in sevs:
                ann["reviewed_score"] = 1.0
                ann["needs_rescoring"] = False
            else:
                ann["reviewed_score"] = None
                ann["needs_rescoring"] = True

        ann["review_status"] = "已核验"

    with open(CLEAN_EXPORT, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {updated_count} items in {CLEAN_EXPORT}")

if __name__ == "__main__":
    main()
