"""
apply_remaining_batch_08.py
Batch 08 (Tasks #1513 ~ #1760, 120 tasks)
Multimodal visual concrete physical object grounding review updater.
"""

import json
import os
import sys

BASE_DIR = r"d:\学业文件\MCL\上色评价_数据集标注\LS_lcad_reviewer"
ALL_FILE = os.path.join(BASE_DIR, "exports", "reviewed_1_10000_all.json")
CLEAN_FILE = os.path.join(BASE_DIR, "exports", "reviewed_1_10000_clean.json")
GROUNDING_OUT = os.path.join(BASE_DIR, "intermediate", "audits", "grounding_remaining_batch_08.json")

DEFECT_NAMES = {
    "A": "缺色",
    "B": "溢色",
    "C": "错色",
    "D": "偏色",
    "E1": "过饱和",
    "E2": "欠饱和",
    "F": "视觉自然度"
}

BATCH_08_REVIEWS = {
    # --- Sheet 01 (#1513 ~ #1522) ---
    1513: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "摩托车后方的车库卷帘门原本鲜明红润的砖橙色漆面色调偏暗发灰，饱和度有所降低（轻度偏色 D-L1，轻度欠饱和 E2-L1）。"
    },
    1515: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "人群中停放的电动代步车原本鲜艳酒红色的金属车壳被严重错涂脱色为浅冷银灰色（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },
    1518: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1519: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "海景露台上的遮阳伞与躺椅布面整体色调略显偏暗发冷灰，碧海蓝天光照通透感稍有减退（轻度偏色 D-L1）。"
    },
    1521: {
        "is_pass": False,
        "severities": {"C": "L1", "D": "L1"},
        "note": "马匹后方原本连绵泛金黄色的牧场草甸被错涂偏染为暗沉的墨绿色与褐灰色（轻度错色 C-L1，轻度偏色 D-L1）。"
    },
    1522: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 02 (#1524 ~ #1536) ---
    1524: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "奶牛雕塑周围原本鲜嫩翠绿的草坪地表色调略显偏暗偏黄，鲜活性稍显不足（轻度偏色 D-L1）。"
    },
    1527: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L3", "E1": "L3"},
        "note": "明黄色踏板摩托车车身被错涂为刺眼荧光绿，且夜空背景与建筑墙面被极度过度渲染为大面积通红灼热的严重偏色伪影（严重偏色 D-L3，严重错色 C-L3，严重过饱和 E1-L3）。"
    },
    1532: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1533: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1534: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1536: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "复古观光巴士车顶原本鲜艳翠绿的遮阳篷布被严重脱色错涂为灰白色，车体红色涂漆与彩绘色彩饱和度明显不足（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },

    # --- Sheet 03 (#1539 ~ #1553) ---
    1539: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "草地上放飞的特技风筝原本鲜艳醒目的玫红色面料色泽偏暗发褐，整体色彩饱和度有所下降（轻度偏色 D-L1，轻度欠饱和 E2-L1）。"
    },
    1541: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "冲浪滑板下方的翻卷海浪原本清透纯净的碧蓝色被严重错涂为灰暗浑浊的铅灰水体，海洋水色严重失真（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },
    1544: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1545: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "玻璃橱窗内张贴的美国国旗贴纸红色条纹色调偏暗发褐，红白条纹色彩鲜明度有所降低（轻度偏色 D-L1，轻度欠饱和 E2-L1）。"
    },
    1551: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1553: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 04 (#1554 ~ #1571) ---
    1554: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1561: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1563: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "黑熊穿行的林间草丛与灌木叶片原本鲜绿生机有所减弱，整体色调略显偏冷偏青灰（轻度偏色 D-L1）。"
    },
    1564: {
        "is_pass": False,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "白瓷餐盘后方的木质吧台桌面被过度渲染为浓艳发亮的金黄明亮调，木质自然色调略显失真（轻度偏色 D-L1，轻度过饱和 E1-L1）。"
    },
    1567: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1571: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 05 (#1574 ~ #1579) ---
    1574: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "棒球红土场地上垒球手身穿的原本鲜艳红润的运动短裤严重脱色褪化为浅淡灰粉色（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },
    1575: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L2"},
        "note": "海滩冲浪者头顶原本清透湛蓝的天空大面积褪色泛灰发白，天空色彩饱和度与通透感显著降低（中度偏色 D-L2，中度欠饱和 E2-L2）。"
    },
    1576: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "沙发上就坐男子身穿的原本鲜亮醒目的橘红色短袖T恤被严重脱色错涂为暗沉无光的浅褐灰色（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },
    1577: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L3"},
        "note": "棒球击球手头上佩戴的球盔与所穿比赛球服原本鲜艳夺目的大红色被彻底大面积错涂为暗淡浑浊的紫褐色（严重错色 C-L3，严重欠饱和 E2-L3）。"
    },
    1578: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1579: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 06 (#1583 ~ #1592) ---
    1583: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1584: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1585: {
        "is_pass": False,
        "severities": {"D": "L3", "C": "L3"},
        "note": "整张做旧老照片中人物大衣、背景建筑与老爷车原本浓郁温馨的复古暖黄调被彻底颠倒错涂为冰冷刺目的电光蓝紫色（严重偏色 D-L3，严重错色 C-L3）。"
    },
    1590: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1591: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "卫生间白色陶瓷洗手盆与周围瓷砖墙面被过度渲染为明显的暖粉红黄调，冷色环境光影有所偏差（轻度偏色 D-L1）。"
    },
    1592: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 07 (#1593 ~ #1600) ---
    1593: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1595: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1596: {
        "is_pass": False,
        "severities": {"C": "L1", "E2": "L1"},
        "note": "餐桌上插花花瓶中的红色花朵与黄色陶瓷马克杯色泽明显发暗褪色，整体环境光影偏暗发灰（轻度错色 C-L1，轻度欠饱和 E2-L1）。"
    },
    1597: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "雪地上平铺的大型特技风筝表面原本鲜明艳丽的亮黄与翠绿色拼接面料严重脱色褪化为灰白暗色（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },
    1598: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "微缩野餐桌前中间玩偶小熊身穿的原本鲜明纯净的天蓝色针织衫色泽偏暗褪色发灰（轻度偏色 D-L1，轻度欠饱和 E2-L1）。"
    },
    1600: {
        "is_pass": False,
        "severities": {"C": "L1", "E2": "L1"},
        "note": "电脑桌上黑白猫咪下巴枕靠的原本亮粉红色的电脑鼠标严重脱色褪化为暗淡浅肉色（轻度错色 C-L1，轻度欠饱和 E2-L1）。"
    },

    # --- Sheet 08 (#1603 ~ #1609) ---
    1603: {
        "is_pass": False,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "木质阳台桌面上摆放的插花花瓶与桌面木纹在光照下色调偏浓偏艳，略显刺眼的黄绿光晕（轻度偏色 D-L1，轻度过饱和 E1-L1）。"
    },
    1604: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1606: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1607: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1608: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1609: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 09 (#1611 ~ #1618) ---
    1611: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "空中编队特技表演喷气机原本鲜明夺目的大红色机身涂漆色调略显偏暗偏褐，鲜艳度稍有不足（轻度偏色 D-L1）。"
    },
    1612: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1615: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1616: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1617: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1618: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 10 (#1621 ~ #1632) ---
    1621: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "装载南瓜的皮卡车金属车身与车尾挡板被过度渲染为较重的红褐色，金属漆面原有色调略有失真（轻度偏色 D-L1）。"
    },
    1622: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1624: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L3"},
        "note": "撑黑伞行走的行人下身所穿的原本鲜艳亮丽的大红色长裤被彻底严重脱色错涂为暗哑黑灰色（严重错色 C-L3，严重欠饱和 E2-L3）。"
    },
    1627: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1628: {
        "is_pass": False,
        "severities": {"C": "L1", "E2": "L1"},
        "note": "白色餐盘中盛装的熟透香蕉果皮原本金黄诱人的色泽明显褪色发灰，饱和度偏低且略带冷绿调（轻度错色 C-L1，轻度欠饱和 E2-L1）。"
    },
    1632: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 11 (#1633 ~ #1644) ---
    1633: {
        "is_pass": False,
        "severities": {"D": "L3", "E2": "L3"},
        "note": "小狗侧影背后的古董世界地图原本浓郁温润的金黄做旧色调被彻底严重脱色错涂为冰冷暗淡的铅灰白色（严重偏色 D-L3，严重欠饱和 E2-L3）。"
    },
    1635: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1640: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "圆盘中的烘焙薄底披萨表面原本金红油润的萨拉米香肠肉片明显褪色脱色，色温显著偏冷且色彩发灰（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },
    1641: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1643: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1644: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 12 (#1645 ~ #1652) ---
    1645: {
        "is_pass": False,
        "severities": {"D": "L3", "E1": "L3"},
        "note": "草地后方原本被薄雾笼罩的针叶树林与天空被极度严重过度渲染为大面积刺眼灼热的血红色偏色伪影（严重偏色 D-L3，严重过饱和 E1-L3）。"
    },
    1646: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1647: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "沙滩上搁浅的小型快艇原本鲜艳醒目的朱红色漆面船壳严重脱色褪化为灰白浅褐调（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },
    1649: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1651: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "餐厅内的红砖拱形墙面与木质餐桌在射灯照射下整体色调略显偏浓偏暗红（轻度偏色 D-L1）。"
    },
    1652: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 13 (#1653 ~ #1668) ---
    1653: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "厨房内的白色橱柜与立式冰箱表面被过度渲染为明显的暖黄褐色，环境冷白光有所失真（轻度偏色 D-L1）。"
    },
    1658: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1659: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1662: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1665: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "卫生间镜前自拍女士原本鲜亮明快的橘红色头发被严重脱色错涂为暗沉发灰的深黑褐色（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },
    1668: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "远方雪山脊线上方原本纯净开阔的湛蓝晴空大面积严重褪色脱色为暗淡的浅灰白色（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },

    # --- Sheet 14 (#1670 ~ #1680) ---
    1670: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1673: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "巡游大象脊背上披挂的原为鲜艳大红色的装饰鞍毯严重脱色错涂为灰暗黄褐调（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },
    1674: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1675: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "电力机车车头上方原本晴朗纯净的湛蓝天空大面积严重脱色褪化为浑浊灰沉的铅灰色（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },
    1679: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1680: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 15 (#1681 ~ #1691) ---
    1681: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1682: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1683: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1685: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1687: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1691: {
        "is_pass": False,
        "severities": {"D": "L3", "E2": "L3"},
        "note": "两只斑马身后的广袤草甸原本连绵浓郁的金黄色秋草被彻底大面积脱色错涂为冰冷暗淡的铅灰白色（严重偏色 D-L3，严重欠饱和 E2-L3）。"
    },

    # --- Sheet 16 (#1693 ~ #1704) ---
    1693: {
        "is_pass": False,
        "severities": {"C": "L1", "E2": "L1"},
        "note": "家庭聚餐桌旁母亲身穿的原为鲜艳醒目的大红色短袖T恤色泽偏暗发褐，红色饱和度有所不足（轻度错色 C-L1，轻度欠饱和 E2-L1）。"
    },
    1695: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "街头墙面上张贴的家具店横幅广告原本鲜明醒目的明黄色底色略显偏暗发灰，饱和度有所降低（轻度偏色 D-L1，轻度欠饱和 E2-L1）。"
    },
    1696: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "复式住宅内的木质地板在自然采光下色调略显偏浓偏橙黄，木色温润度略有失真（轻度偏色 D-L1）。"
    },
    1701: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1702: {
        "is_pass": False,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "桌面玻璃花瓶中盛插的鲜红花束在光照下被过度渲染为刺眼偏冷的洋红色，色调与饱和度略显偏高（轻度偏色 D-L1，轻度过饱和 E1-L1）。"
    },
    1704: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 17 (#1712 ~ #1722) ---
    1712: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1714: {
        "is_pass": False,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "木桌上摆放的新鲜番茄与蔬菜叶片被过度涂染为浓艳刺眼的深红与亮橙色，高光处饱和度过高（轻度偏色 D-L1，轻度过饱和 E1-L1）。"
    },
    1718: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1719: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1720: {
        "is_pass": False,
        "severities": {"C": "L1", "E2": "L1"},
        "note": "车库前放置的原为鲜艳纯净明蓝色的大型塑料垃圾桶严重脱色褪化为灰淡浅青色（轻度错色 C-L1，轻度欠饱和 E2-L1）。"
    },
    1722: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 18 (#1723 ~ #1740) ---
    1723: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1724: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "自行车车架横梁上绑扎的原为鲜亮大红色的折叠雨伞布料略显偏暗发褐，红色饱和度有所减退（轻度偏色 D-L1，轻度欠饱和 E2-L1）。"
    },
    1725: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1730: {
        "is_pass": False,
        "severities": {"D": "L3", "E1": "L3"},
        "note": "集市道路路面、撑红伞行人与周围车辆被极度严重过度渲染为大面积刺眼灼热的血红色偏色伪影（严重偏色 D-L3，严重过饱和 E1-L3）。"
    },
    1737: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1740: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },

    # --- Sheet 19 (#1743 ~ #1750) ---
    1743: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1745: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "货运铁路上空原本清澈通透的湛蓝晴空大面积严重脱色褪化为浑浊暗淡的灰白阴云天（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },
    1746: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1747: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1749: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1750: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "棒球比赛本垒捕手身上佩戴的原为鲜艳醒目的大红色防护护胸严重脱色褪化为灰淡暗褐色（中度错色 C-L2，中度欠饱和 E2-L2）。"
    },

    # --- Sheet 20 (#1751 ~ #1760) ---
    1751: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1752: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L3"},
        "note": "列车车窗外原本开阔明净的湛蓝天空被彻底大面积脱色褪化为阴沉暗淡的铅灰白色（严重错色 C-L3，严重欠饱和 E2-L3）。"
    },
    1754: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1756: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "海滨沙丘上空放飞的龙形长条风筝原本鲜艳醒目的红黄彩绘飘带色泽偏暗发灰，饱和度有所降低（轻度偏色 D-L1，轻度欠饱和 E2-L1）。"
    },
    1757: {
        "is_pass": True,
        "severities": {},
        "note": "审查通过"
    },
    1760: {
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
    print(f"[*] Processing Batch 08: Total {len(BATCH_08_REVIEWS)} reviewed tasks.")

    # 1. 保存中间定物 JSON
    with open(GROUNDING_OUT, "w", encoding="utf-8") as f:
        json.dump(BATCH_08_REVIEWS, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved intermediate grounding review to {GROUNDING_OUT}")

    # 2. 更新 exports/reviewed_1_10000_all.json
    print(f"[*] Loading {ALL_FILE}...")
    with open(ALL_FILE, "r", encoding="utf-8") as f:
        data_all = json.load(f)

    all_map = {}
    for item in data_all["annotations"]:
        t_id = item["human_review"]["task_id"]
        all_map[t_id] = item

    updated_all_count = 0
    pass_all_count = 0
    modify_all_count = 0

    for t_id, rev in BATCH_08_REVIEWS.items():
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
    for t_id, rev in BATCH_08_REVIEWS.items():
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

    print("[SUCCESS] Batch 08 successfully applied to both all and clean exports!")


if __name__ == "__main__":
    main()
