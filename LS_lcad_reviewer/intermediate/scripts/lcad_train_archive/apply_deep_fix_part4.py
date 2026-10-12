#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_deep_fix_part4.py
精准应用 Part 4 (Batch 6, Task ID 2501-3000, 73 个高危样本) 的视觉大图直审改判结果：
- 严格遵循 AGENTS.md 规范与基准 schema
- 消灭抽象代词，严格实体定物
- 更新 reviewed_1_10000_all.json
- 更新 reviewed_1_10000_clean.json
"""

import json
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
ALL_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_all.json"
CLEAN_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_clean.json"

# Part 4 (73 例) 视觉大图核验改判映射
PART4_REVIEWS = {
    # Sheet 01
    2503: {
        "defects": [],
        "note": "三明治切面生菜与火腿、咖啡纸杯白盖与黄褐面包皮色彩自然协调，环境光色调舒适，物理自洽放行。"
    },
    2510: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "草坪与路基旁灌木丛严重欠饱和脱色泛灰紫，绿色植被质感明显受损。"}],
        "note": "核查发现：草坪与路基旁灌木丛严重欠饱和脱色泛灰紫(C-L2)。"
    },
    2535: {
        "defects": [],
        "note": "厨房操作台与后方墙面暖灰白调自然和谐，天花板与拱门色泽自洽，物理自洽放行。"
    },
    2540: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "逆光天空与远山被错涂为冷青蓝色，破坏黄昏金黄逆光氛围。"}],
        "note": "核查发现：逆光天空与远山被错涂为冷青蓝色，破坏黄昏金黄逆光氛围(C-L2)。"
    },
    2541: {
        "defects": [],
        "note": "小男孩白衬衫纯正，黄黑条纹领带与暗红女上衣还原准确，色调自然协调，物理自洽放行。"
    },
    2546: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "马路右侧专用车道砖红色沥青路面完全欠饱和脱色变冷暗灰水泥路。"}],
        "note": "核查发现：马路右侧专用车道砖红色沥青路面完全欠饱和脱色变冷暗灰(C-L2)。"
    },

    # Sheet 02
    2549: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "冲浪少年胸前的鲜红色与袖口翠绿色潜水冲浪服严重欠饱和脱色泛黑灰。"}],
        "note": "核查发现：冲浪少年胸前的鲜红色与袖口翠绿色潜水冲浪服严重欠饱和脱色泛黑灰(C-L2)。"
    },
    2557: {
        "defects": [{"id": "C", "name": "错色", "severity": "L1", "description": "洗手台上摆放的紫红色液体瓶轻度欠饱和脱色泛灰白。"}],
        "note": "核查发现：洗手台上摆放的紫红色液体瓶轻度欠饱和脱色泛灰白(C-L1)。"
    },
    2558: {
        "defects": [],
        "note": "牢房铁栏杆锈黑与内部单人床、木桌灰度层次自然，无恶性偏色，物理自洽放行。"
    },
    2571: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "背后天空与远处山峦呈现不自然蓝紫色偏色，废弃皮卡车周草坪欠饱和发暗。"}],
        "note": "核查发现：背后天空与远处山峦呈现不自然蓝紫色偏色，车周草坪欠饱和(C-L2)。"
    },
    2572: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "大面积翠绿草坪与牧草严重欠饱和脱色发灰泛枯黄。"}],
        "note": "核查发现：大面积翠绿草坪与牧草严重欠饱和脱色发灰泛枯黄(C-L2)。"
    },
    2592: {
        "defects": [],
        "note": "冲浪手破浪行进，冲浪板与白浪色调逼真自洽，无恶性失真，物理自洽放行。"
    },

    # Sheet 03
    2596: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "餐桌上的果汁杯、西瓜水果切片及蔬菜沙拉轻度欠饱和发暗。"}],
        "note": "核查发现：餐桌上的果汁杯、西瓜水果切片及蔬菜沙拉轻度欠饱和发暗(C-L2)。"
    },
    2603: {
        "defects": [],
        "note": "白色马桶与冷白地砖色调纯净，暖灰墙壁过渡自然，物理自洽放行。"
    },
    2606: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "摩托车后座驮载的巨大捆鲜红花卉盆栽完全脱色褪变为枯暗土灰草木。"}],
        "note": "核查发现：摩托车后座驮载的巨大捆鲜红花卉盆栽完全脱色褪变为枯暗土灰草木(C-L2)。"
    },
    2608: {
        "defects": [],
        "note": "狭小卫生间白色马桶与台盆光洁，环境灰度均匀自然，物理自洽放行。"
    },
    2621: {
        "defects": [],
        "note": "复古黑白台阶人像照片灰阶过渡平滑自然，无恶性杂色，物理自洽放行。"
    },
    2629: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "行李推车左下角原本鲜艳的大红色长椅被错涂为橙黄色。"}],
        "note": "核查发现：行李推车左下角原本鲜艳的大红色长椅被错涂为橙黄色(C-L2)。"
    },

    # Sheet 04
    2632: {
        "defects": [],
        "note": "西装人群笔记本电脑操作场景，领带深红与蓝灰色泽纯正，肤色自然，物理自洽放行。"
    },
    2634: {
        "defects": [{"id": "C", "name": "错色", "severity": "L1", "description": "背景远处行道树茂密树冠欠饱和发暗泛灰。"}],
        "note": "核查发现：背景远处行道树茂密树冠欠饱和发暗泛灰(C-L1)。"
    },
    2647: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "盘中三明治的牛肉肉层与酱料被恶性错涂为紫红与荧光黄绿伪色。"}],
        "note": "核查发现：盘中三明治的牛肉肉层与酱料被恶性错涂为紫红与荧光黄绿伪色(C-L2)。"
    },
    2649: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "窗外背景树木绿化严重欠饱和脱色泛紫灰冷色。"}],
        "note": "核查发现：窗外背景树木绿化严重欠饱和脱色泛紫灰冷色(C-L2)。"
    },
    2659: {
        "defects": [],
        "note": "黄昏尖顶教堂在余晖中色调和谐自然，晚霞与剪影过渡逼真，物理自洽放行。"
    },
    2662: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "盘中原本鲜红诱人的意大利面番茄酱欠饱和脱色泛枯暗黄褐。"}],
        "note": "核查发现：盘中原本鲜红诱人的意大利面番茄酱欠饱和脱色泛枯暗黄褐(C-L2)。"
    },

    # Sheet 05
    2667: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "夜景右侧桥墩立柱与天空被恶性错涂为突兀刺眼的蓝紫色伪色。"}],
        "note": "核查发现：夜景右侧桥墩立柱与天空被恶性错涂为突兀刺眼的蓝紫色伪色(C-L2)。"
    },
    2675: {
        "defects": [],
        "note": "矩形披萨深红辣香肠片、金黄芝士与翠绿罗勒叶色调鲜明诱人，物理自洽放行。"
    },
    2678: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "女童下身穿着的深酒红色长裤严重欠饱和脱色变灰暗泥褐。"}],
        "note": "核查发现：女童下身穿着的深酒红色长裤严重欠饱和脱色变灰暗泥褐(C-L2)。"
    },
    2680: {
        "defects": [],
        "note": "卫生间暖黄与浅粉双色墙面过渡自然，镜子与马桶色泽自洽，物理自洽放行。"
    },
    2685: {
        "defects": [],
        "note": "外卖披萨金黄微焦，鲜红番茄酱料包与纯白餐巾纸还原极佳，物理自洽放行。"
    },
    2688: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "墙壁吐司机涂鸦左侧及边缘的大红色块欠饱和脱色变暗冷灰紫。"}],
        "note": "核查发现：墙壁吐司机涂鸦左侧及边缘的大红色块欠饱和脱色变暗冷灰紫(C-L2)。"
    },

    # Sheet 06
    2689: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "妇女身穿的花衬衫上的鲜艳红色花纹欠饱和脱色变灰暗。"}],
        "note": "核查发现：妇女身穿的花衬衫上的鲜艳红色花纹欠饱和脱色变灰暗(C-L2)。"
    },
    2700: {
        "defects": [],
        "note": "棒球场低彩度写实抓拍，裁判深灰黑与球员浅白球衣自然纯粹，物理自洽放行。"
    },
    2702: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "笔记本电脑键盘掌托与触控板区域被大面积错涂为土黄色。"}],
        "note": "核查发现：笔记本电脑键盘掌托与触控板区域被大面积错涂为土黄色(C-L2)。"
    },
    2703: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "盘中大阪烧表面的翠绿海苔碎与特制酱料被错涂为暗青黑与灰绿色。"}],
        "note": "核查发现：盘中大阪烧表面的翠绿海苔碎与特制酱料被错涂为暗青黑与灰绿色(C-L2)。"
    },
    2713: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "背景石墙上原本大面积爬满的生机翠绿青苔与常春藤完全脱色褪暗为灰褐色。"}],
        "note": "核查发现：背景石墙上原本大面积爬满的生机翠绿青苔与常春藤完全脱色褪暗为灰褐色(C-L2)。"
    },
    2720: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "马路中央极其醒目的亮黄色双层公交车车身完全欠饱和脱色漂白为灰白色。"}],
        "note": "核查发现：马路中央极其醒目的亮黄色双层公交车车身完全欠饱和脱色漂白为灰白色(C-L2)。"
    },

    # Sheet 07
    2725: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "车后座原本淡蓝色的布艺靠毯严重欠饱和脱色变暗黄土灰。"}],
        "note": "核查发现：车后座原本淡蓝色的布艺靠毯严重欠饱和脱色变暗黄土灰(C-L2)。"
    },
    2735: {
        "defects": [],
        "note": "古石柱雪景废墟黑白伞与纯白雪地还原极佳，无恶性失真，物理自洽放行。"
    },
    2736: {
        "defects": [],
        "note": "透明雨伞下白猫纯正纯洁，眼睛橙黄灵动，物理自洽放行。"
    },
    2742: {
        "defects": [],
        "note": "海滩放风筝开阔全景，碧海天际线与沙滩色调自然，无偏色，物理自洽放行。"
    },
    2748: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "欧式钟楼原本暖红砖砌筑的塔身严重欠饱和脱色褪暗为灰暗土黄褐。"}],
        "note": "核查发现：欧式钟楼原本暖红砖砌筑的塔身严重欠饱和脱色褪暗为灰暗土黄褐(C-L2)。"
    },
    2773: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "盘中汉堡里夹着的鲜红香肠肉片以及左侧碗中的烤香肠肉块欠饱和脱色泛枯暗黄绿。"}],
        "note": "核查发现：盘中汉堡里夹着的鲜红香肠肉片以及左侧烤香肠块欠饱和脱色(C-L2)。"
    },

    # Sheet 08
    2783: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "面粉桌面上正在制作的几枚小披萨表面涂抹的鲜红番茄酱严重欠饱和脱色发暗变枯褐色。"}],
        "note": "核查发现：面粉桌面上正在制作的小披萨鲜红番茄酱严重欠饱和脱色变枯褐(C-L2)。"
    },
    2785: {
        "defects": [],
        "note": "清澈水中群鱼活动，水波灰绿自然微润，物理自洽放行。"
    },
    2786: {
        "defects": [],
        "note": "厨房白色微波炉与暖色木质橱柜搭配自然，操作台色调统一，物理自洽放行。"
    },
    2790: {
        "defects": [],
        "note": "卫生间镜子、大理石洗手台与纯白毛巾色调一致，暖色照明自洽，物理自洽放行。"
    },
    2798: {
        "defects": [],
        "note": "单人卧室蓝色背景墙与白色床品色调和谐统一，光影自然，物理自洽放行。"
    },
    2801: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "In-N-Out 移动餐车的纯白车身表面被恶性错涂大面积深青蓝与灰紫色阴霾伪色。"}],
        "note": "核查发现：In-N-Out 移动餐车的纯白车身表面被恶性错涂大面积深青蓝与灰紫色伪色(C-L2)。"
    },

    # Sheet 09
    2806: {
        "defects": [],
        "note": "复古客厅老电视机、深棕木柜与地毯色泽和谐自洽，无恶性偏色，物理自洽放行。"
    },
    2810: {
        "defects": [],
        "note": "现代黑色蜂窝砖墙与极简纯白洗手台黑白对比纯正精准，极高还原度，物理自洽放行。"
    },
    2817: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "沙丘顶部聚集处插着的多顶红色大遮阳伞严重欠饱和脱色漂白为灰白色。"}],
        "note": "核查发现：沙丘顶部聚集处插着的多顶红色大遮阳伞严重欠饱和脱色漂白为灰白色(C-L2)。"
    },
    2821: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "会议主席台长桌前悬挂的印有文字的蓝色宣传横幅严重欠饱和脱色变灰暗紫褐。"}],
        "note": "核查发现：会议主席台长桌前悬挂的蓝色宣传横幅严重欠饱和脱色变灰暗紫褐(C-L2)。"
    },
    2822: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "右侧盛装骏马的头部及毛皮被恶性错涂为极其突兀惊悚的深宝蓝色伪色。"}],
        "note": "核查发现：右侧盛装骏马的头部及毛皮被恶性错涂为极其突兀惊悚的深宝蓝色伪色(C-L2)。"
    },
    2831: {
        "defects": [],
        "note": "海边黑色巨石岛礁、海鸟与黄昏余晖白浪还原逼真自然，物理自洽放行。"
    },

    # Sheet 10
    2841: {
        "defects": [],
        "note": "卫生间花洒马桶与瓷砖墙面色泽统一，冷暖对比自然，物理自洽放行。"
    },
    2872: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "室内原本光洁温润的原木地板大面积泛青灰冷色，木质质感失真。"}],
        "note": "核查发现：室内原本光洁温润的原木地板大面积泛青灰冷色，木质质感失真(C-L2)。"
    },
    2885: {
        "defects": [],
        "note": "炸薯条金黄酥脆，汉堡面包与白瓷咖啡杯色泽诱人自然，物理自洽放行。"
    },
    2899: {
        "defects": [],
        "note": "冲浪手破浪场景海天一色，碧蓝海面与浪花还原精准，物理自洽放行。"
    },
    2907: {
        "defects": [],
        "note": "雪原滑雪者黑衣黑裤与雪地对比分明，阴沉天空过渡写实自然，物理自洽放行。"
    },
    2915: {
        "defects": [{"id": "C", "name": "错色", "severity": "L1", "description": "天空中飞翔的小型彩色风筝欠饱和脱色变灰暗。"}],
        "note": "核查发现：天空中飞翔的小型彩色风筝欠饱和脱色变灰暗(C-L1)。"
    },

    # Sheet 11
    2916: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "盘中甜甜圈表面原本鲜艳的粉红色草莓糖霜被恶性错涂为浅天蓝色。"}],
        "note": "核查发现：盘中甜甜圈表面原本鲜艳的粉红色草莓糖霜被恶性错涂为浅天蓝色(C-L2)。"
    },
    2924: {
        "defects": [],
        "note": "深色皮沙发后探出头的黑狗毛色自然纯正，室内暗光自洽，物理自洽放行。"
    },
    2925: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "冲浪手身上原本鲜艳醒目的大红色短袖上衣严重欠饱和脱色泛黑灰。"}],
        "note": "核查发现：冲浪手身上原本鲜艳醒目的大红色短袖上衣严重欠饱和脱色泛黑灰(C-L2)。"
    },
    2929: {
        "defects": [],
        "note": "卫生间白色浴帘与台盆纯净洁白，镜子与墙面光照自然，物理自洽放行。"
    },
    2933: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "滑雪者身上穿着的鲜艳宝蓝色防寒夹克严重欠饱和脱色漂白为灰白色。"}],
        "note": "核查发现：滑雪者身上穿着的鲜艳宝蓝色防寒夹克严重欠饱和脱色漂白为灰白色(C-L2)。"
    },
    2949: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "牧场大面积翠绿草坪欠饱和脱色泛枯黄暗灰。"}],
        "note": "核查发现：牧场大面积翠绿草坪欠饱和脱色泛枯黄暗灰(C-L2)。"
    },

    # Sheet 12
    2951: {
        "defects": [],
        "note": "田埂牧羊人与羊群，绿坡草地与田野阴天色彩和谐自洽，物理自洽放行。"
    },
    2960: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "地面堆放的各类彩色行李包与彩色杂物零配件欠饱和脱色变灰暗。"}],
        "note": "核查发现：地面堆放的各类彩色行李包与彩色杂物零配件欠饱和脱色变灰暗(C-L2)。"
    },
    2976: {
        "defects": [],
        "note": "木屋厕所白色蹲便器与原木板墙泥地色泽质朴真实，物理自洽放行。"
    },
    2977: {
        "defects": [],
        "note": "黄色笑脸奶油蛋糕金黄灿烂，红色果酱笔触与白瓷托盘还原完美，物理自洽放行。"
    },
    2979: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "客厅原本极其鲜亮醒目的柠檬黄色背景墙面完全欠饱和脱色蜕变为灰白色。"}],
        "note": "核查发现：客厅原本极其鲜亮醒目的柠檬黄色背景墙面完全欠饱和脱色蜕变为灰白色(C-L2)。"
    },
    2983: {
        "defects": [],
        "note": "开放式厨房原木地板与黑色燃气灶台、木质餐桌椅搭配和谐自然，物理自洽放行。"
    },

    # Sheet 13
    3000: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "门前倚靠的原本鲜红色单板滑雪板被恶性错涂为亮黄与草绿色。"}],
        "note": "核查发现：门前倚靠的原本鲜红色单板滑雪板被恶性错涂为亮黄与草绿色(C-L2)。"
    }
}

def main():
    print(f"Loading {ALL_FILE}...")
    with open(ALL_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    print(f"Loading {CLEAN_FILE}...")
    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    anns_all = all_data["annotations"]
    anns_clean = clean_data["annotations"]

    updated_count = 0
    for ann_a, ann_c in zip(anns_all, anns_clean):
        tid = ann_a["human_review"]["task_id"]
        if tid in PART4_REVIEWS:
            rev = PART4_REVIEWS[tid]
            has_defect_a = any(d.get("id") == "A" for d in rev["defects"])

            # 更新 all_data
            ann_a["defects"] = rev["defects"]
            ann_a["review_note"] = rev["note"]
            ann_a["reviewed_score"] = 1.0 if has_defect_a else None
            ann_a["needs_rescoring"] = not has_defect_a
            ann_a["review_status"] = "已核验"

            # 更新 clean_data (review_note 严格保持 "")
            ann_c["defects"] = rev["defects"]
            ann_c["review_note"] = ""
            ann_c["reviewed_score"] = 1.0 if has_defect_a else None
            ann_c["needs_rescoring"] = not has_defect_a
            ann_c["review_status"] = "已核验"

            updated_count += 1

    print(f"Updated {updated_count} Part 4 high-risk items in memory.")
    assert updated_count == 73, f"Expected 73 updated items, got {updated_count}"

    with open(ALL_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved: {ALL_FILE.name}")

    with open(CLEAN_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved: {CLEAN_FILE.name}")

    print("\n[SUCCESS] Part 4 deep fix successfully applied to all exports!")

if __name__ == "__main__":
    main()
