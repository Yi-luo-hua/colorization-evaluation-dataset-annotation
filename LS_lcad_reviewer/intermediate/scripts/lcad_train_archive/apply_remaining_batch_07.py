"""
apply_remaining_batch_07.py
Batch 07 (Tasks #1377 ~ #1510, 120 tasks)
Multimodal visual concrete physical object grounding review updater.
"""

import json
import os
import sys

BASE_DIR = r"d:\学业文件\MCL\上色评价_数据集标注\LS_lcad_reviewer"
ALL_FILE = os.path.join(BASE_DIR, "exports", "reviewed_1_10000_all.json")
CLEAN_FILE = os.path.join(BASE_DIR, "exports", "reviewed_1_10000_clean.json")
GROUNDING_OUT = os.path.join(BASE_DIR, "intermediate", "audits", "grounding_remaining_batch_07.json")

DEFECT_NAMES = {
    "A": "缺色",
    "B": "溢色",
    "C": "错色",
    "D": "偏色",
    "E1": "过饱和",
    "E2": "欠饱和",
    "F": "视觉自然度"
}

BATCH_07_REVIEWS = {
    # --- Sheet 01 (#1377 ~ #1382) ---
    1377: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1378: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1379: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1380: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L1"},
        "note": "演播室访谈台前原本鲜艳亮丽的浅蓝色翻糖蛋糕被错涂脱色为暗紫灰色（中度错色 C-L2，轻度欠饱和 E2-L1）。"
    },
    1381: {
        "is_pass": False,
        "severities": {"D": "L2"},
        "note": "火车站候车月台上方原本中性冷灰的钢架穹顶与指示牌被整体错涂偏染为较重的红褐色调（中度偏色 D-L2）。"
    },
    1382: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2"},
        "note": "室内原本温馨的暖黄光照环境彻底丢失，女子身后的背景墙面与所戴礼帽被错涂为冰冷浅灰白色（中度偏色 D-L2，中度欠饱和 E2-L2）。"
    },

    # --- Sheet 02 (#1384 ~ #1389) ---
    1384: {
        "is_pass": False,
        "severities": {"D": "L3", "E1": "L3"},
        "note": "卧室窗前百叶窗与室内空间被极度严重过度涂染为大面积浓烈刺眼的血红色，完全丧失原本室内光影明暗层次（严重偏色 D-L3，严重过饱和 E1-L3）。"
    },
    1385: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1386: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "水面高速航行的海岸警卫队救援巡逻艇橙红色船体外壳局部色泽略深（轻度偏色 D-L1）。"
    },
    1387: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "熟睡爱犬身下的地毯背景色调略微偏冷偏灰（轻度偏色 D-L1）。"
    },
    1388: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "会议宴会厅木质座椅与后方人物面部在暖色吊灯照射下局部暗影略显偏红（轻度偏色 D-L1）。"
    },
    1389: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 03 (#1390 ~ #1398) ---
    1390: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "手持体感方向盘的玩家双手与背景墙面在室内光照下略显微偏暖黄（轻度偏色 D-L1）。"
    },
    1392: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "书架上陈列的书籍封面书脊黄色与深红色装饰色调略显偏浓（轻度偏色 D-L1）。"
    },
    1393: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1394: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1395: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2"},
        "note": "华盛顿纪念碑方尖碑上方的晴朗蓝天大面积褪色发白，天空色彩饱和度显著不足（中度偏色 D-L2，中度欠饱和 E2-L2）。"
    },
    1398: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "街头立柱上的红色停止交通标志牌红色底色偏暗偏褐，天空青蓝感稍有减弱（轻度偏色 D-L1）。"
    },

    # --- Sheet 04 (#1399 ~ #1404) ---
    1399: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1400: {
        "is_pass": False,
        "severities": {"C": "L2"},
        "note": "临窗餐桌上原本盛放鲜红色果汁的玻璃高脚杯被严重错涂为浅黄绿色（中度错色 C-L2）。"
    },
    1401: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "斑马群周围的热带灌木丛与草木叶片原本鲜绿生机减弱，色调略显偏暗偏黄（轻度偏色 D-L1，轻度欠饱和 E2-L1）。"
    },
    1402: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "电子维修工作台上黄色便签纸与技术人员操作手部肤色略微偏深（轻度偏色 D-L1）。"
    },
    1403: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1404: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L1"},
        "note": "厨房内原本温暖明亮的木质橱柜与操作台面被错涂偏染为冷淡灰暗的深褐灰调（中度偏色 D-L2，轻度欠饱和 E2-L1）。"
    },

    # --- Sheet 05 (#1406 ~ #1411) ---
    1406: {
        "is_pass": False,
        "severities": {"C": "L2", "E1": "L2"},
        "note": "酒店大堂休息区沙发原本明快的金黄色布艺被严重错涂为刺眼的荧光酸性黄绿色（中度错色 C-L2，中度过饱和 E1-L2）。"
    },
    1407: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1408: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "生日派对大蛋糕周围的鲜艳蓝色裱花边框色彩饱和度略显偏淡，局部偏暗（轻度偏色 D-L1，轻度欠饱和 E2-L1）。"
    },
    1409: {
        "is_pass": False,
        "severities": {"C": "L2", "D": "L2"},
        "note": "办公电脑桌左侧原本清爽淡蓝色的隔断墙面被严重错涂偏染为暖米黄色（中度错色 C-L2，中度偏色 D-L2）。"
    },
    1410: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1411: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 06 (#1412 ~ #1417) ---
    1412: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "电脑桌上熟睡的三花猫头部与背部原本鲜艳的橘黄色毛发明显褪色发灰，橘黄特征有所减弱（轻度偏色 D-L1，轻度欠饱和 E2-L1）。"
    },
    1413: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1414: {
        "is_pass": False,
        "severities": {"D": "L2", "C": "L2"},
        "note": "地铁车厢内原本中性冷灰的车体壁板与车窗框架被大面积错涂偏染为浓重的黄褐色调（中度偏色 D-L2，中度错色 C-L2）。"
    },
    1415: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1416: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L2"},
        "note": "老旧复古照片中的花瓶周围背景被严重过度渲染为刺眼灼热的红橙色偏色伪影（中度偏色 D-L2，中度过饱和 E1-L2）。"
    },
    1417: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 07 (#1418 ~ #1423) ---
    1418: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "丛林大象骑行路线上的泥土小路整体色调略显偏红褐橙色，路面沙土质感稍显偏暖（轻度偏色 D-L1）。"
    },
    1419: {
        "is_pass": False,
        "severities": {"D": "L1", "C": "L1"},
        "note": "棒球小球员身穿的球服原本沉稳的墨绿色被错涂为偏亮的翠蓝青绿（轻度偏色 D-L1，轻度错色 C-L1）。"
    },
    1420: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1421: {
        "is_pass": False,
        "severities": {"D": "L2", "C": "L2"},
        "note": "雨夜城市街道原本温馨浓郁的暖黄街灯与橱窗光晕彻底丢失，街景与撑伞行人被整体错涂偏染为冰冷青蓝调（中度偏色 D-L2，中度错色 C-L2）。"
    },
    1422: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "咖啡厅木质桌面被过度渲染为浓郁的黄褐色调，台面色温明显失真偏黄（轻度偏色 D-L1）。"
    },
    1423: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 08 (#1424 ~ #1429) ---
    1424: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1425: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "茶室背景黄色陈列木架与茶具茶杯色彩还原鲜亮，仅人物衣物与局部光影稍显偏深（轻度偏色 D-L1）。"
    },
    1426: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "砂石路旁原本鲜绿青翠的草坪地表严重褪色泛黄，饱和度有所降低（轻度偏色 D-L1，轻度欠饱和 E2-L1）。"
    },
    1427: {
        "is_pass": False,
        "severities": {"D": "L1", "C": "L1"},
        "note": "条纹靠垫上熟睡的猫咪原本银灰色的毛发被错涂偏染为明显的红褐色（轻度偏色 D-L1，轻度错色 C-L1）。"
    },
    1428: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "木栅栏上休憩的模特身穿的原本鲜艳大红色的风衣外套被严重脱色错涂为暗灰紫褐色（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },
    1429: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L3"},
        "note": "浮筒水上飞机停靠水域上方的原本纯净湛蓝的晴朗蓝天被彻底脱色退化为灰暗阴沉的铅灰色（严重错色 C-L3，严重欠饱和 E2-L3）。"
    },

    # --- Sheet 09 (#1430 ~ #1436) ---
    1430: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "斑马身后的岩石洞穴背景石壁色彩略微偏暗偏红（轻度偏色 D-L1）。"
    },
    1431: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1432: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1433: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2"},
        "note": "阳台落地窗纱帘与室内原本沐浴在金黄暖阳下的温馨光照彻底丢失，被大面积错涂为冰冷单调的灰白色冷调（中度偏色 D-L2，中度欠饱和 E2-L2）。"
    },
    1434: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "夜市红色遮阳伞篷面在灯光照射下局部红光略显偏浓偏艳（轻度偏色 D-L1）。"
    },
    1436: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 10 (#1437 ~ #1443) ---
    1437: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "餐盘中双色甜甜圈与饮料杯色彩鲜艳，仅托盘边缘阴影略显偏冷（轻度偏色 D-L1）。"
    },
    1438: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "餐厅天花板小射灯温暖光照在酒柜与木质吧台上的漫射反光略微偏浓（轻度偏色 D-L1）。"
    },
    1439: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1440: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1442: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "牧场草原斑马群后方山坡枯黄草地与针叶林绿意还原极高，仅近处草坪局部略偏暗（轻度偏色 D-L1）。"
    },
    1443: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 11 (#1444 ~ #1449) ---
    1444: {
        "is_pass": False,
        "severities": {"C": "L1", "E2": "L1"},
        "note": "葡萄酒窖内品酒女游客原本鲜亮醒目的鹅黄色短袖T恤褪色发白，色彩饱和度有所下降（轻度错色 C-L1，轻度欠饱和 E2-L1）。"
    },
    1445: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1446: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2"},
        "note": "老照片原本复古做旧的浓郁暖黄褐色调完全脱色为中性黑白冷灰色，整体色调显著偏冷且严重褪色（中度偏色 D-L2，中度欠饱和 E2-L2）。"
    },
    1447: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L1"},
        "note": "空中飞跃特技越野摩托车前挡泥板与车身架上原本鲜亮耀眼的荧光草绿色漆面被彻底错涂脱色为暗灰色（严重错色 C-L3，轻度偏色 D-L1）。"
    },
    1448: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1449: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "餐桌后方木质餐椅与背景墙板在光照下色调略显偏红偏浓，略微偏向红褐暖调（轻度偏色 D-L1）。"
    },

    # --- Sheet 12 (#1450 ~ #1455) ---
    1450: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1451: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1452: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "台面后方蓝色保鲜盒上的红色文字条带与热狗夹层香肠色泽略显偏暗偏褐，鲜红度略有不足（轻度偏色 D-L1，轻度欠饱和 E2-L1）。"
    },
    1453: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1454: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L2"},
        "note": "餐桌上的蓝色陶瓷餐盘与红酒玻璃杯被过度渲染为刺眼的电光蓝与浓艳紫红光，高光与色彩饱和度明显过度（中度偏色 D-L2，中度过饱和 E1-L2）。"
    },
    1455: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 13 (#1457 ~ #1462) ---
    1457: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1458: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "桌面与左侧陶瓷花瓶原本温润的米黄色调略显偏冷发灰，环境色温稍有偏差（轻度偏色 D-L1）。"
    },
    1459: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1460: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "白色调色盘内盛装的明黄色颜料与桌面彩色画笔笔杆明显褪色脱色，饱和度大幅度降低且色调偏灰（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },
    1461: {
        "is_pass": False,
        "severities": {"C": "L2"},
        "note": "黄色消防栓后方原本红砖质感的建筑外墙被严重常识性错涂为冰冷的湖水蓝灰色（中度错色 C-L2）。"
    },
    1462: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "停靠在街边的摩托车后方红砖建筑外墙色调略微偏浓偏暗红，阴影处色温略偏暖（轻度偏色 D-L1）。"
    },

    # --- Sheet 14 (#1463 ~ #1468) ---
    1463: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "长毛猎犬头部与脊背上原本亮丽浓郁的金红色毛发大面积严重脱色褪化为灰白淡黄，丧失鲜艳毛色特征（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },
    1464: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1465: {
        "is_pass": False,
        "severities": {"C": "L3"},
        "note": "哈雷摩托车后方停靠的原为醒目大红色的厢式货车箱体被彻底大面积错涂为深蓝色（严重错色 C-L3）。"
    },
    1466: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1467: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1468: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "电脑显示器屏幕显示的蓝色软件界面略微偏暗偏紫，键盘上的浅色毛绒玩具熊毛发色调略显偏暖（轻度偏色 D-L1）。"
    },

    # --- Sheet 15 (#1470 ~ #1475) ---
    1470: {
        "is_pass": False,
        "severities": {"C": "L1", "D": "L1"},
        "note": "棒球击球手头上佩戴的球帽与球服长袖原本暗调沉稳的深藏青色被错涂为偏艳的明宝蓝色（轻度错色 C-L1，轻度偏色 D-L1）。"
    },
    1471: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1472: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "书桌上的木质书架与金属电风扇在暖色台灯直射下色调略显偏浓发红（轻度偏色 D-L1）。"
    },
    1473: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1474: {
        "is_pass": False,
        "severities": {"C": "L2", "D": "L2"},
        "note": "写字台后方原本粉刷为清爽青绿色的室内墙面被大面积严重错涂为暗淡单调的米黄色与浅灰白（中度错色 C-L2，中度偏色 D-L2）。"
    },
    1475: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 16 (#1476 ~ #1482) ---
    1476: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1478: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "黄色消防栓后方的欧式石质建筑立面与晴朗蓝天整体色调略显偏冷泛青灰，天空鲜蓝感稍有褪淡（轻度偏色 D-L1）。"
    },
    1479: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1480: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "烤箱内部金属烤架与盛放的烘焙蛋挞在烘烤光照下整体色调略显偏浓偏红褐（轻度偏色 D-L1）。"
    },
    1481: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2"},
        "note": "宴会餐桌后方原本沐浴在温馨暖光中的室内墙面与白色桌布被错涂为冰冷的灰白色调，环境暖黄光影彻底丧失（中度偏色 D-L2，中度欠饱和 E2-L2）。"
    },
    1482: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "白瓷餐盘中的薄底烘焙披萨表面原本焦黄油润的烤芝士色泽明显褪色泛灰，色温偏冷且色彩饱和度不足（轻度偏色 D-L1，轻度欠饱和 E2-L1）。"
    },

    # --- Sheet 17 (#1483 ~ #1489) ---
    1483: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "水池中游泳嬉戏的北极熊毛发与周围水体整体色调偏暗发冷灰，水面原本清澈的青绿水感略有减退（轻度偏色 D-L1）。"
    },
    1484: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1485: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1486: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "天空中放飞的大型软体鱼形风筝腹部原本鲜艳清透的湖水蓝色被彻底错涂脱色为暗淡的浅灰粉白色（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },
    1487: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "餐盘内的新鲜生菜沙拉叶片原本鲜嫩翠绿的色泽略微偏暗偏灰，整体色彩饱和度稍有不足（轻度偏色 D-L1，轻度欠饱和 E2-L1）。"
    },
    1489: {
        "is_pass": False,
        "severities": {"C": "L3"},
        "note": "画廊门前原本喷涂为醒目鲜艳大红色的金属卷闸门被彻底大面积错涂为亮电光蓝色（严重错色 C-L3）。"
    },

    # --- Sheet 18 (#1490 ~ #1495) ---
    1490: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "盛装糖霜甜甜圈的硬纸包装盒内衬色调略微偏暗发灰，室内暖光漫射稍有欠缺（轻度偏色 D-L1）。"
    },
    1491: {
        "is_pass": False,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "餐盘内热狗面包表面浇淋的番茄酱汁被过度渲染为浓艳刺目的亮荧光橙红，饱和度略显偏高（轻度偏色 D-L1，轻度过饱和 E1-L1）。"
    },
    1492: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1493: {
        "is_pass": False,
        "severities": {"C": "L3"},
        "note": "女孩躺入的便携乐器硬壳箱外表原本鲜艳醒目的大红色帆布面料被彻底错涂为暗沉军绿色（严重错色 C-L3）。"
    },
    1494: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1495: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 19 (#1496 ~ #1501) ---
    1496: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1497: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1498: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "餐桌旁的老人面部与颈部肤色在室内灯光映衬下被过度渲染为偏深偏浓的红褐色（轻度偏色 D-L1）。"
    },
    1499: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1500: {
        "is_pass": False,
        "severities": {"C": "L1", "D": "L1"},
        "note": "车厢内停放的公路自行车金属车架原本低调暗色的涂层被过度渲染为刺目显眼的亮宝蓝色（轻度错色 C-L1，轻度偏色 D-L1）。"
    },
    1501: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2"},
        "note": "海边沙滩上方原本纯净开阔的湛蓝天空大面积褪色发白偏灰，蓝天色彩饱和度显著降低（中度偏色 D-L2，中度欠饱和 E2-L2）。"
    },

    # --- Sheet 20 (#1503 ~ #1510) ---
    1503: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1504: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1507: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1508: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "吧台木质台面与后方装饰墙面在壁灯暖光直射下色调略显偏浓偏红褐色（轻度偏色 D-L1）。"
    },
    1509: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1510: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    }
}


def build_defect_list(severities, note):
    defects = []
    for d_id, sev in severities.items():
        name = DEFECT_NAMES.get(d_id, "未知")
        defects.append({
            "id": d_id,
            "name": name,
            "severity": sev,
            "description": note
        })
    return defects


def main():
    print(f"[*] Processing Batch 07: Total {len(BATCH_07_REVIEWS)} reviewed tasks.")

    # 1. 保存中间定物 JSON
    with open(GROUNDING_OUT, "w", encoding="utf-8") as f:
        json.dump(BATCH_07_REVIEWS, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved intermediate grounding review to {GROUNDING_OUT}")

    # 2. 更新 exports/reviewed_1_10000_all.json
    print(f"[*] Loading {ALL_FILE}...")
    with open(ALL_FILE, "r", encoding="utf-8") as f:
        data_all = json.load(f)

    # 建立 task_id 索引映射
    all_map = {}
    for item in data_all["annotations"]:
        t_id = item["human_review"]["task_id"]
        all_map[t_id] = item

    updated_all_count = 0
    pass_all_count = 0
    modify_all_count = 0

    for t_id, rev in BATCH_07_REVIEWS.items():
        if t_id not in all_map:
            print(f"[!] Warning: task_id {t_id} not found in all dataset!")
            continue
        item = all_map[t_id]
        if rev["is_pass"]:
            item["defects"] = []
            item["review_status"] = "已核验"
            item["review_note"] = "审查通过"
            item["reviewed_score"] = None
            item["needs_rescoring"] = True
            pass_all_count += 1
        else:
            item["defects"] = build_defect_list(rev["severities"], rev["note"])
            item["review_status"] = "已核验"
            item["review_note"] = rev["note"]
            item["reviewed_score"] = None
            item["needs_rescoring"] = True
            modify_all_count += 1
        updated_all_count += 1

    print(f"[*] Saving updated {ALL_FILE} (Updated: {updated_all_count}, Pass: {pass_all_count}, Modified: {modify_all_count})...")
    with open(ALL_FILE, "w", encoding="utf-8") as f:
        json.dump(data_all, f, ensure_ascii=False, indent=2)

    # 3. 更新 exports/reviewed_1_10000_clean.json (review_note 必须为 "")
    print(f"[*] Loading {CLEAN_FILE}...")
    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        data_clean = json.load(f)

    clean_map = {}
    for item in data_clean["annotations"]:
        t_id = item["human_review"]["task_id"]
        clean_map[t_id] = item

    updated_clean_count = 0
    for t_id, rev in BATCH_07_REVIEWS.items():
        if t_id not in clean_map:
            print(f"[!] Warning: task_id {t_id} not found in clean dataset!")
            continue
        item = clean_map[t_id]
        if rev["is_pass"]:
            item["defects"] = []
            item["review_status"] = "已核验"
            item["review_note"] = ""
            item["reviewed_score"] = None
            item["needs_rescoring"] = True
        else:
            item["defects"] = build_defect_list(rev["severities"], rev["note"])
            item["review_status"] = "已核验"
            item["review_note"] = ""
            item["reviewed_score"] = None
            item["needs_rescoring"] = True
        updated_clean_count += 1

    print(f"[*] Saving updated {CLEAN_FILE} (Updated: {updated_clean_count})...")
    with open(CLEAN_FILE, "w", encoding="utf-8") as f:
        json.dump(data_clean, f, ensure_ascii=False, indent=2)

    print("[SUCCESS] Batch 07 successfully applied to both all and clean exports!")


if __name__ == "__main__":
    main()
