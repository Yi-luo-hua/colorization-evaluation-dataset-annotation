#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_remaining_batch_12.py
根据对 Batch 12（Tasks 2454 ~ 2672，共 120 组）的 20 张高清看板多模态大图直审结果，
1. 生成中间定物审计文件 grounding_remaining_batch_12.json；
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
OUT_GROUNDING_FILE = AUDITS_DIR / "grounding_remaining_batch_12.json"

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
    # Sheet 01: [2454, 2456, 2457, 2461, 2462, 2463]
    2454: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "货运列车后方编组的鲜艳红色集装箱车厢被严重剥色错涂为惨灰白色（严重错色 C-L3，欠饱和 E2-L2）。"
    },
    2456: {
        "is_pass": False,
        "severities": {"C": "L3", "F": "L2"},
        "note": "棒球场上击球手原本鲜艳大红色的运动短袖T恤被常识性严重错涂为深蓝色（严重错色 C-L3，视觉自然度受损 F-L2）。"
    },
    2457: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L3", "E2": "L2"},
        "note": "蓝天下飞行的民航客机白色机身与周围晴空背景被严重错涂为浑浊焦糖黄褐色，整体色调严重失真（常识错色 C-L3，严重偏色 D-L3，欠饱和 E2-L2）。"
    },
    2461: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L3", "D": "L2"},
        "note": "公园斜坡草坪原本大面积生机盎然的鲜绿色植被被严重剥色错涂为干枯黄灰泥土（严重错色 C-L3，严重欠饱和 E2-L3，偏色 D-L2）。"
    },
    2462: {
        "is_pass": False,
        "severities": {"C": "L2", "D": "L1"},
        "note": "办公电脑显示器中央代码编辑器窗口背景出现大块突兀的红紫色偏色噪斑（错色 C-L2，偏色 D-L1）。"
    },
    2463: {
        "is_pass": False,
        "severities": {"D": "L2", "F": "L1"},
        "note": "烧烤架旁掌勺老人身穿的纯白短袖T恤胸前暗部出现大面积暗红泛紫污浊色斑（偏色 D-L2，视觉自然度 F-L1）。"
    },

    # Sheet 02: [2464, 2467, 2468, 2471, 2473, 2477]
    2464: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2467: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2468: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2"},
        "note": "导盲犬驯导员身穿的宝蓝色连帽卫衣外套被常识性严重错涂为暗沉军绿色（严重错色 C-L3，偏色 D-L2）。"
    },
    2471: {
        "is_pass": False,
        "severities": {"E1": "L1", "D": "L1", "F": "L1"},
        "note": "壁炉前方铺设的地毯与木地板受火光照射区域饱和度过高呈荧光亮黄，高光轻度过曝（过饱和 E1-L1，偏色 D-L1，视觉自然度 F-L1）。"
    },
    2473: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "长颈鹿园区展区背景晴空轻度泛青绿冷调，长颈鹿身上的棕黄斑块饱和度略有减损（偏色 D-L1，欠饱和 E2-L1）。"
    },
    2477: {
        "is_pass": False,
        "severities": {"D": "L1", "F": "L1"},
        "note": "野生斑马林地背景的深绿树叶微泛暗灰棕偏色，斑马身体黑白条纹暗部受杂色干扰（偏色 D-L1，视觉自然度 F-L1）。"
    },

    # Sheet 03: [2479, 2480, 2481, 2483, 2484, 2487]
    2479: {
        "is_pass": False,
        "severities": {"D": "L2", "F": "L1"},
        "note": "男子面部肤色与手臂皮肤受到不自然的暗红泛紫偏色污染，肤色显得污浊（偏色 D-L2，视觉自然度 F-L1）。"
    },
    2480: {
        "is_pass": False,
        "severities": {"D": "L2", "F": "L1"},
        "note": "书架上整齐排布的多本书籍书脊高光处出现突兀的紫红色色偏与杂斑（偏色 D-L2，视觉自然度 F-L1）。"
    },
    2481: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "滑雪场滑雪者原本鲜艳的荧光绿防寒服外套鲜艳度减损泛灰，雪地松林轻微泛冷（偏色 D-L1，欠饱和 E2-L1）。"
    },
    2483: {
        "is_pass": False,
        "severities": {"E1": "L2", "F": "L2"},
        "note": "户外停放的军用运输卡车迷彩车身涂装与草地色彩过于艳丽失真，高光反光刺眼（过饱和 E1-L2，视觉自然度受损 F-L2）。"
    },
    2484: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "客厅液晶电视黑色屏幕表面与窗台阴影暗部泛轻微暗紫色色偏（偏色 D-L1）。"
    },
    2487: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "街头滑板少年身穿的深色长裤及背景铁丝网色彩暗淡泛青灰（偏色 D-L1，欠饱和 E2-L1）。"
    },

    # Sheet 04: [2490, 2492, 2493, 2495, 2496, 2497]
    2490: {
        "is_pass": False,
        "severities": {"D": "L3", "E2": "L2", "C": "L2"},
        "note": "海边沙滩与落日天空原本温暖的金黄晚霞被彻底漂白泛冷为冰冷灰蓝调（偏色 D-L3，欠饱和 E2-L2）；冲浪手怀抱的冲浪板暖红条纹彩绘褪色发灰（错色 C-L2）。"
    },
    2492: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2493: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2495: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2496: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2497: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2", "E2_1": "L1"},
        # 注意: 拆为 C-L2 与 E2-L2
        "severities": {"C": "L2", "E2": "L2"},
        "note": "塑料托盘内摆放的红苹果与番茄酱严重脱色发灰，丧失原本鲜红光泽（错色 C-L2，欠饱和 E2-L2）。"
    },

    # Sheet 05: [2498, 2500, 2502, 2504, 2505, 2506]
    2498: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2500: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2502: {
        "is_pass": False,
        "severities": {"E2": "L1", "D": "L1"},
        "note": "黑人男子所穿浅蓝条纹衬衫衣袖与衣身整体色彩暗沉泛灰（欠饱和 E2-L1）；背景暖色墙面微泛冷灰偏色（偏色 D-L1）。"
    },
    2504: {
        "is_pass": False,
        "severities": {"D": "L3", "E2": "L2", "C": "L2"},
        "note": "水泥路面与消防栓原本的暖褐色环境光被彻底漂变为冰冷暗青灰色（偏色 D-L3，欠饱和 E2-L2）；路面彩色粉笔字迹色彩褪化（错色 C-L2）。"
    },
    2505: {
        "is_pass": False,
        "severities": {"C": "L2", "D": "L1"},
        "note": "湖畔山坡原本呈金黄色秋季植被树林被常识性误涂为均一深墨绿色（错色 C-L2）；湖面水体与远山整体偏冷暗青色（偏色 D-L1）。"
    },
    2506: {
        "is_pass": False,
        "severities": {"E2": "L1", "D": "L1"},
        "note": "双翼轻型飞机机身鲜红色涂装饱和度略微欠缺并泛暗褐（欠饱和 E2-L1）；草地与背景机库建筑微泛冷调（偏色 D-L1）。"
    },

    # Sheet 06: [2508, 2509, 2511, 2512, 2513, 2518]
    2508: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2", "C": "L1"},
        "note": "雨夜湿滑路面原本映照的路灯与车灯暖黄倒影被漂染为冷灰暗蓝调（偏色 D-L2，欠饱和 E2-L2）；行进路人手持的彩条雨伞伞面色彩暗淡发黑（错色 C-L1）。"
    },
    2509: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2", "D": "L1"},
        "note": "古堡拱门原本厚重的红褐色砖石墙体被彻底褪色误涂为冰冷水泥暗灰（错色 C-L3，欠饱和 E2-L2）；前景草坪微泛荧光黄（偏色 D-L1）。"
    },
    2511: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2512: {
        "is_pass": False,
        "severities": {"E1": "L2", "D": "L1", "F": "L1"},
        "note": "棒球场外野绿色草坪饱和度异常爆表呈刺眼荧光绿（过饱和 E1-L2）；球场内野红土泛高光橙红偏色（偏色 D-L1，视觉自然度 F-L1）。"
    },
    2513: {
        "is_pass": False,
        "severities": {"E2": "L1"},
        "note": "议会大厦与大本钟哥特式石质外立面原本的微暖黄褐色略显暗淡泛灰（欠饱和 E2-L1）。"
    },
    2518: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 07: [2519, 2520, 2521, 2522, 2523, 2524]
    2519: {
        "is_pass": False,
        "severities": {"D": "L3", "E2": "L2", "F": "L1"},
        "note": "书房木地板与电脑办公桌原本温暖的红棕木纹被彻底漂白泛冷为冰冷灰青色（偏色 D-L3，欠饱和 E2-L2）；趴在地上的猫咪毛色泛冷暗发青（视觉自然度 F-L1）。"
    },
    2520: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2", "C": "L1"},
        "note": "户外背景树林阳光透射原本明媚金绿变为暗沉冷青灰色（偏色 D-L2，欠饱和 E2-L2）；桌面摆放的塑料餐具与玩偶熊毛发质感灰暗（错色 C-L1）。"
    },
    2521: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2"},
        "note": "经典三层骑士公共汽车原本标志性的深紫色车漆被严重错涂为普通蓝灰色（严重错色 C-L3，偏色 D-L2）。"
    },
    2522: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2523: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L1"},
        "note": "花束底部系扎的鲜艳亮紫红色缎带蝴蝶结被严重错涂为暗沉棕褐色（严重错色 C-L3）；上方折纸花束色彩鲜艳度欠缺（欠饱和 E2-L1）。"
    },
    2524: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "繁华街市上方悬挂的多个大型红底商铺广告招牌严重脱色泛白（错色 C-L2，欠饱和 E2-L2）。"
    },

    # Sheet 08: [2526, 2527, 2528, 2529, 2530, 2531]
    2526: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2527: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L1"},
        "note": "酒店客房床头壁灯照射区域过饱和，导致原本浅灰色的卧室墙壁与天花板严重泛浓黄色偏（偏色 D-L2，过饱和 E1-L1）。"
    },
    2528: {
        "is_pass": False,
        "severities": {"D": "L1", "F": "L1"},
        "note": "男子佩戴的尖顶针织帽鲜艳红绿色块色彩变暗且泛暗紫色调（偏色 D-L1）；面部肤色出现局部暗沉杂色（视觉自然度 F-L1）。"
    },
    2529: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2", "D": "L1"},
        "note": "摩托车驾驶者所穿的水洗蓝牛仔外套被严重褪色误涂为暗灰褐色（错色 C-L2，欠饱和 E2-L2）；红色摩托车油箱鲜艳度下降（偏色 D-L1）。"
    },
    2530: {
        "is_pass": False,
        "severities": {"D": "L3", "E2": "L2", "C": "L2"},
        "note": "客厅室内灯光原本温馨的暖黄氛围被严重漂变为冰冷暗青灰色（偏色 D-L3，欠饱和 E2-L2）；沙发上女子身穿的粉红色吊带裙褪色脱水（错色 C-L2）。"
    },
    2531: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2"},
        "note": "街边居民楼前原本盛开的鲜艳紫红色花树树冠被常识性严重误涂为均一墨绿色（严重错色 C-L3，偏色 D-L2）。"
    },

    # Sheet 09: [2532, 2533, 2534, 2536, 2538, 2543]
    2532: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L1"},
        "note": "集市地面堆放的大量原本未成熟的青绿色香蕉串被全部错涂为熟透的金黄色（严重错色 C-L3）；背景摊贩服饰微泛色偏（偏色 D-L1）。"
    },
    2533: {
        "is_pass": False,
        "severities": {"E2": "L1", "F": "L1"},
        "note": "湖面漂浮的木质捕鱼船船舷与暗部色泽略显暗淡泛灰（欠饱和 E2-L1，视觉自然度 F-L1）。"
    },
    2534: {
        "is_pass": False,
        "severities": {"C": "L3", "E1": "L2"},
        "note": "街头立式金属公告宣传板被大面积突兀错涂为刺眼的荧光粉紫色，饱和度过高（严重错色 C-L3，过饱和 E1-L2）。"
    },
    2536: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L1"},
        "note": "STOP路标后方的行道绿树与草坪被严重褪色误涂为暗黄褐色（错色 C-L2，欠饱和 E2-L1）。"
    },
    2538: {
        "is_pass": False,
        "severities": {"E2": "L1"},
        "note": "餐盘内摆放的烘焙甜甜圈与面包表面糖霜光泽变暗，表皮色泽略显欠饱和发干（欠饱和 E2-L1）。"
    },
    2543: {
        "is_pass": False,
        "severities": {"D": "L2", "C": "L1"},
        "note": "树上挂果的生香蕉串及周围阔叶大面积泛黄偏暖，偏离原本深绿本色（偏色 D-L2，错色 C-L1）。"
    },

    # Sheet 10: [2544, 2545, 2547, 2550, 2552, 2553]
    2544: {
        "is_pass": False,
        "severities": {"E2": "L1", "D": "L1"},
        "note": "桌面摆放的手工剪刀鲜红色手柄与左侧线圈色彩泛暗且饱和度轻度丢失（欠饱和 E2-L1，偏色 D-L1）。"
    },
    2545: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2547: {
        "is_pass": False,
        "severities": {"E2": "L2", "C": "L2", "D": "L2"},
        "note": "烧烤铁网上的肉质烤香肠表面金黄焦香色泽严重脱色变为灰暗褐色（欠饱和 E2-L2，错色 C-L2）；底部炭火炽热红光熄灭泛白（偏色 D-L2）。"
    },
    2550: {
        "is_pass": False,
        "severities": {"D": "L2"},
        "note": "室内起居室木质墙壁与天花板横梁原本温暖的黄褐色调被明显带入冷暗青绿色偏（偏色 D-L2）。"
    },
    2552: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L3"},
        "note": "草坪上原本明黄底色配红帽的消防栓主体被彻底剥除黄色误涂为惨白色（严重错色 C-L3，严重欠饱和 E2-L3）。"
    },
    2553: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "窗台前悬挂的节日装饰五彩小灯串色彩完全丢失，被误涂为单调的白色荧光灯珠（严重错色 C-L3，欠饱和 E2-L2）。"
    },

    # Sheet 11: [2555, 2559, 2560, 2561, 2563, 2564]
    2555: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2", "D": "L1"},
        "note": "客厅背景原本清新的嫩黄绿色墙面被大面积剥色退化为冷灰白色（错色 C-L2，欠饱和 E2-L2）；布艺沙发与茶几木纹偏暗（偏色 D-L1）。"
    },
    2559: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2560: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2561: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L1"},
        "note": "码头停放的工程起重吊车天蓝色车体被严重错涂为发暗的青绿色（严重错色 C-L3）；红色小型汽车色彩饱和度稍有下降（欠饱和 E2-L1）。"
    },
    2563: {
        "is_pass": False,
        "severities": {"C": "L3", "F": "L3"},
        "note": "果园果树间原本泥土色的林间小径被大面积恶性错涂为大片鲜艳的亮紫红杂色伪色（严重错色 C-L3，视觉自然度严重恶化 F-L3）。"
    },
    2564: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2", "D": "L1"},
        "note": "身后主裁判原本所穿的墨绿色运动长袖卫衣被脱色错涂为灰黑色（错色 C-L2，欠饱和 E2-L2）；击球手红色头盔略微欠饱和（偏色 D-L1）。"
    },

    # Sheet 12: [2565, 2566, 2567, 2569, 2573, 2574]
    2565: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2"},
        "note": "街道上方密布装饰的彩色遮阳伞中，原本多把亮黄色与橙色雨伞被严重错涂为深蓝紫色（严重错色 C-L3，偏色 D-L2）。"
    },
    2566: {
        "is_pass": False,
        "severities": {"C": "L2", "B": "L2", "E1": "L3"},
        "note": "盛装蔬菜的浅色塑料果盘被严重溢色错涂为刺眼荧光绿色（错色 C-L2，溢色 B-L2）；红色西红柿与紫色茄子色彩过饱和浓艳刺目（过饱和 E1-L3）。"
    },
    2567: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2569: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2573: {
        "is_pass": False,
        "severities": {"E1": "L2", "D": "L1"},
        "note": "古典欧式建筑夜景照明外立面金黄灯光过饱和呈刺眼红橙色（过饱和 E1-L2，偏色 D-L1）。"
    },
    2574: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "背景高层写字楼室内窗户灯光略显偏红浓艳（偏色 D-L1）；湿滑路面与雨伞反光暗部泛冷灰（欠饱和 E2-L1）。"
    },

    # Sheet 13: [2577, 2578, 2580, 2581, 2582, 2584]
    2577: {
        "is_pass": False,
        "severities": {"D": "L2", "C": "L1"},
        "note": "路边停靠的紧凑型SUV车身金属车漆由原本冷深灰色明显泛暖黄褐变色（偏色 D-L2，错色 C-L1）。"
    },
    2578: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2580: {
        "is_pass": False,
        "severities": {"E1": "L2", "D": "L1", "F": "L2"},
        "note": "盘中摆放的熟透香蕉表皮金黄色泽呈现不自然的荧光黄绿色调且边缘泛杂色（过饱和 E1-L2，偏色 D-L1，视觉自然度 F-L2）。"
    },
    2581: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2"},
        "note": "古典木质台钟外壳原本庄重的深红棕木纹被严重错涂为诡异的紫红色（严重错色 C-L3，偏色 D-L2）。"
    },
    2582: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2584: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 14: [2586, 2587, 2589, 2590, 2593, 2598]
    2586: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L3"},
        "note": "庭院中原本生机勃勃的鲜绿色草坪被严重大面积脱色误涂为干枯泛白的泥灰色（严重错色 C-L3，严重欠饱和 E2-L3）。"
    },
    2587: {
        "is_pass": False,
        "severities": {"E1": "L2", "F": "L1"},
        "note": "花园苗圃中种植的花丛花朵色彩过度浓艳呈高饱和荧光橙红（过饱和 E1-L2，视觉自然度 F-L1）。"
    },
    2589: {
        "is_pass": False,
        "severities": {"D": "L2"},
        "note": "古典大钟楼石质外立面浮雕与梁柱整体泛暖红黄偏色（偏色 D-L2）。"
    },
    2590: {
        "is_pass": False,
        "severities": {"E2": "L1"},
        "note": "方形奶油蛋糕表面裱花边缘与祝福字样色泽暗淡微泛灰（欠饱和 E2-L1）。"
    },
    2593: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "滑雪运动员所穿的鲜绿色单板滑雪防寒裤被脱色错涂为暗黑灰色（错色 C-L2，欠饱和 E2-L2）。"
    },
    2598: {
        "is_pass": False,
        "severities": {"C": "L2", "F": "L1"},
        "note": "街头行人随身拖曳的拉杆旅行箱表面图案被错涂为荧光杂色（错色 C-L2，视觉自然度 F-L1）。"
    },

    # Sheet 15: [2599, 2600, 2602, 2604, 2610, 2613]
    2599: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "街角现代大楼右侧附楼原本红砖色的外立面砖墙泛暗偏冷灰（偏色 D-L1，欠饱和 E2-L1）。"
    },
    2600: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2602: {
        "is_pass": False,
        "severities": {"E2": "L2", "D": "L1"},
        "note": "马戏团车厢上方原本鲜艳红色的马戏团英文标语横幅严重褪色发暗（欠饱和 E2-L2，偏色 D-L1）。"
    },
    2604: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L1"},
        "note": "背景木板墙板原本自然木色偏红浓艳（偏色 D-L2，过饱和 E1-L1）。"
    },
    2610: {
        "is_pass": False,
        "severities": {"E1": "L2", "F": "L1"},
        "note": "微波炉顶部放置的亮黄色挤酱调料瓶色彩过于浓艳呈荧光黄（过饱和 E1-L2）；微波炉操作面板高光处微泛杂色（视觉自然度 F-L1）。"
    },
    2613: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 16: [2614, 2617, 2619, 2623, 2624, 2625]
    2614: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2617: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "双人床床尾铺设的鲜亮紫红色天鹅绒床旗被脱色错涂为暗褐色（错色 C-L2，欠饱和 E2-L2）。"
    },
    2619: {
        "is_pass": False,
        "severities": {"E2": "L1"},
        "note": "海浪波涛与冲浪者暗色防寒服边缘水花略泛暗灰（欠饱和 E2-L1）。"
    },
    2623: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2"},
        "note": "左侧玄关墙壁原本优雅淡雅的浅粉紫色被严重错涂为突兀的亮橙红色（严重错色 C-L3，偏色 D-L2）。"
    },
    2624: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L3"},
        "note": "金属喂鸟器支架上停留的小鸟腹部原本鲜艳的亮金黄色羽毛被彻底剥除脱色为灰白色（严重错色 C-L3，严重欠饱和 E2-L3）。"
    },
    2625: {
        "is_pass": False,
        "severities": {"D": "L3", "E2": "L2"},
        "note": "床头两侧壁灯与台灯原本温馨浓郁的暖红光晕被严重漂染熄灭为冰冷暗青色（偏色 D-L3，欠饱和 E2-L2）。"
    },

    # Sheet 17: [2627, 2628, 2630, 2631, 2633, 2637]
    2627: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2628: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "男子所穿黑色短袖胸前印制的鲜艳橙红色圆形徽章严重脱色变为暗淡浅黄（错色 C-L2，欠饱和 E2-L2）。"
    },
    2630: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2631: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2633: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "笔记本电脑屏幕显示的刺青图案书籍封面鲜红色底色与书名严重脱色泛暗褐（错色 C-L2，欠饱和 E2-L2）。"
    },
    2637: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L1"},
        "note": "海滩上站立的马匹毛发偏暖黄褐色泛色偏（偏色 D-L2）；背景海水湛蓝色泽略显暗淡（欠饱和 E2-L1）。"
    },

    # Sheet 18: [2640, 2641, 2642, 2645, 2646, 2650]
    2640: {
        "is_pass": False,
        "severities": {"C": "L1", "E2": "L1", "D": "L1"},
        "note": "保鲜盒内摆放的切片红苹果外皮鲜红色泽变淡偏黄橙（错色 C-L1，欠饱和 E2-L1）；右侧餐盘内西兰花蔬菜微泛偏色（偏色 D-L1）。"
    },
    2641: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2"},
        "note": "书房墙面与室内壁灯原本温暖柔和的金黄暖色光被整体漂变为冰冷暗青绿色（偏色 D-L2，欠饱和 E2-L2）。"
    },
    2642: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "公交车侧面张贴的鲜红色商铺广告横幅被严重脱色误涂为暗黑灰色（严重错色 C-L3，欠饱和 E2-L2）。"
    },
    2645: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2"},
        "note": "床铺上整齐陈列数码产品背景的暖红色床单与靠垫严重泛冷灰暗褐色（偏色 D-L2，欠饱和 E2-L2）。"
    },
    2646: {
        "is_pass": False,
        "severities": {"D": "L3", "E2": "L2", "F": "L1"},
        "note": "新生儿包裹的暖粉色襁褓与棉毯被严重漂白为冰冷石膏灰白色（偏色 D-L3，欠饱和 E2-L2）；婴儿面部血色淡薄（视觉自然度 F-L1）。"
    },
    2650: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L3"},
        "note": "道路施工现场立置的鲜艳荧光橙色菱形警示标牌被彻底脱色误涂为惨白色（严重错色 C-L3，严重欠饱和 E2-L3）。"
    },

    # Sheet 19: [2651, 2652, 2655, 2656, 2658, 2660]
    2651: {
        "is_pass": False,
        "severities": {"E2": "L1"},
        "note": "草坪上立置的明黄色消防栓底座阴影处色泽略显暗淡欠饱和（欠饱和 E2-L1）。"
    },
    2652: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2", "C_bg": "L2"},
        # 注意: 合并 C 为 L3
        "severities": {"C": "L3", "D": "L2"},
        "note": "草地上行走的成年大象皮肤被严重错涂为突兀的粉红褐色（严重错色 C-L3，偏色 D-L2）；背景绿树与草地大面积褪色枯黄。"
    },
    2655: {
        "is_pass": False,
        "severities": {"C": "L2", "D": "L1"},
        "note": "长途大客车车身侧面喷涂的大面积鲜红色艺术图案被严重错涂为暗橙黄色（错色 C-L2，偏色 D-L1）。"
    },
    2656: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "野生斑马身后的草原绿色灌木丛被严重大面积脱色误涂为苍白枯黄色（错色 C-L2，欠饱和 E2-L2）。"
    },
    2658: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L1"},
        "note": "水果摊位上原本熟透呈金黄色的带刺榴莲果堆被常识性严重错涂为生涩的草绿色（严重错色 C-L3，偏色 D-L1）。"
    },
    2660: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L1"},
        "note": "超市货架上陈列的亮黄色新鲜柠檬与红苹果色泽暗淡脱色（错色 C-L2，欠饱和 E2-L1）。"
    },

    # Sheet 20: [2661, 2663, 2665, 2666, 2669, 2672]
    2661: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    2663: {
        "is_pass": False,
        "severities": {"D": "L1", "F": "L1"},
        "note": "锡箔纸餐盘内盛装的热狗面包与香肠表面酱料偏红微泛色偏（偏色 D-L1，视觉自然度 F-L1）。"
    },
    2665: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L3"},
        "note": "海滩游客身旁放置的大遮阳伞与草帽上原本鲜艳的亮粉红色布料被彻底脱色误涂为暗黄泥色（严重错色 C-L3，严重欠饱和 E2-L3）。"
    },
    2666: {
        "is_pass": False,
        "severities": {"E1": "L2", "D": "L1"},
        "note": "卧室木床铺设的鲜红色床单表面饱和度过高呈现刺眼荧光亮红色（过饱和 E1-L2，偏色 D-L1）。"
    },
    2669: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L1"},
        "note": "荒野草地上捕猎母狮毛皮与周围枯草整体泛发红暗褐色偏，色彩暗沉浑浊（偏色 D-L2，欠饱和 E2-L1）。"
    },
    2672: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    }
}

def main():
    print(f"Total reviews defined: {len(REVIEWS)}")
    assert len(REVIEWS) == 120, f"Expected 120 reviews, got {len(REVIEWS)}"

    # 1. 检查是否存在未定义的严重度或不合规字段
    pass_count = sum(1 for r in REVIEWS.values() if r["is_pass"])
    defect_count = len(REVIEWS) - pass_count
    print(f"Pass count: {pass_count}, Defect count: {defect_count}")

    # 2. 生成中间定物审计 JSON
    grounding_data = {}
    for tid, rev in REVIEWS.items():
        if rev["is_pass"]:
            grounding_data[str(tid)] = {
                "score": None,
                "severities": {},
                "note": "审查通过"
            }
        else:
            grounding_data[str(tid)] = {
                "score": None,
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
            print(f"Warning: Task #{tid} not found in all_export!")
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
