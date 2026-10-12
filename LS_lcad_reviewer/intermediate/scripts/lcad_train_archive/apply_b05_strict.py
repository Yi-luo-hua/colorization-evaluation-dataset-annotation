# -*- coding: utf-8 -*-
import json
import os
import sys

BASE_DIR = r"d:\学业文件\MCL\上色评价_数据集标注"
GROUNDING_FILE = os.path.join(BASE_DIR, "LS_lcad_reviewer", "intermediate", "audits", "grounding_remaining_batch_05.json")
ALL_EXPORT = os.path.join(BASE_DIR, "LS_lcad_reviewer", "exports", "reviewed_1_10000_all.json")
CLEAN_EXPORT = os.path.join(BASE_DIR, "LS_lcad_reviewer", "exports", "reviewed_1_10000_clean.json")

NEW_GROUNDINGS = {
    1128: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "天空整体泛灰冷色调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "黄昏天际晚霞暖色光晕严重褪色发灰。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "傍晚落日晚霞氛围完全丧失。"}
        ],
        "note": "洛熙视觉改判：天际晚霞暖光严重欠饱和褪色发灰(E2-L2)，天空泛灰冷偏色(D-L2)。"
    },
    1132: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "衬衫上搭配的印花领带及西裤面料色彩欠饱和严重褪色发灰。"}
        ],
        "note": "洛熙视觉改判：印花领带及西裤面料色彩欠饱和发灰(E2-L2)。"
    },
    1134: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "山坡草地上的耕牛棕色毛发及周围草地整体泛微暖偏色。"}
        ],
        "note": "洛熙视觉改判：耕牛棕色毛发及周围草地整体泛微暖偏色(D-L1)。"
    },
    1143: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "卫生间瓷砖地面与隔断墙壁泛青冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "两座马桶周围的砖缝及阴影严重欠饱和发暗。"}
        ],
        "note": "洛熙视觉改判：卫生间瓷砖地面泛青冷灰偏色(D-L1)，马桶周围欠饱和发暗(E2-L2)。"
    },
    1146: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "厨房木质橱柜门板与吧台立面严重泛暖红偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "不锈钢操作台面与厨房吊顶色彩欠饱和。"}
        ],
        "note": "洛熙视觉改判：厨房木质橱柜门板泛暖红偏色(D-L2)，操作台面色彩欠饱和(E2-L1)。"
    },
    1153: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "防化服人员头戴的鲜红色安全帽被错涂为青灰暗色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "公园小道两侧的树木草坪泛暗黄褐色偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "蓝色防护服色彩过于浓烈刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "整体人物与自然风光色彩协调性差。"}
        ],
        "note": "洛熙视觉改判：红色头盔错涂为青灰暗色(C-L2)，蓝色防护服过饱和浓艳(E1-L2)。"
    },
    1160: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "切开的橙子果肉与完整橙子表皮整体泛微暖偏色且略偏暗。"}
        ],
        "note": "洛熙视觉改判：切开的橙子果肉与完整橙子表皮整体泛微暖偏色(D-L1)。"
    },
    1166: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "背景树林与阴霾天空整体泛偏暗灰调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "机场跑道两侧的大片草坪色彩欠饱和严重发灰褪色。"}
        ],
        "note": "洛熙视觉改判：机场跑道草坪欠饱和发灰褪色(E2-L2)，背景树林天空偏暗灰(D-L1)。"
    },
    1167: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "商场餐厅大堂白色天花板、立柱与长条木餐桌严重泛荧光亮黄偏色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "室内灯光下的人群阴影过渡生硬。"}
        ],
        "note": "洛熙视觉改判：商场餐厅大堂天花板立柱泛荧光亮黄偏色(D-L2)，阴影过渡生硬(F-L1)。"
    },
    1181: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "黑色花瓶中插着的黄色与粉紫色玫瑰花瓣色彩过于浓艳刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "花瓣高光区边缘色彩过渡生硬失真。"}
        ],
        "note": "洛熙视觉改判：黄粉色玫瑰花瓣色彩过于浓艳刺眼(E1-L2)，花瓣边缘生硬(F-L2)。"
    },
    1188: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "傍晚草坪地面大面积泛暗枯黄色偏。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "男孩身穿的T恤色彩暗淡褪色且与暗部草坪过渡生硬。"}
        ],
        "note": "洛熙视觉改判：傍晚草坪地面大面积泛暗枯黄偏色(D-L2)，人物与暗部过渡生硬(F-L2)。"
    },
    1210: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "电脑办公桌台面与背景白色墙壁整体严重泛青冷蓝偏色。"}
        ],
        "note": "洛熙视觉改判：电脑办公桌台面与背景白色墙壁整体泛青冷蓝偏色(D-L2)。"
    },
    1212: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "老式蒸汽机车车头与轨道碎石泛暗偏红偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "铁轨两旁的森林茂密树木呈现刺眼深绿色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "树林与火车之间色彩反差失真。"}
        ],
        "note": "洛熙视觉改判：铁轨两旁树木刺眼深绿过饱和(E1-L2)，机车与道砟泛暗偏红偏色(D-L2)。"
    },
    1213: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "海滨沙滩地面整体严重泛暗红黄色偏。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "远处海水与海浪色彩欠饱和发灰。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "海滨风光通透感降低。"}
        ],
        "note": "洛熙视觉改判：沙滩地面泛暗红黄偏色(D-L2)，海水海浪欠饱和发灰(E2-L2)。"
    },
    1220: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "厨房不锈钢水槽与金属水龙头泛青冷偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "窗台上摆放的彩色马克杯与窗外采光欠饱和发灰。"}
        ],
        "note": "洛熙视觉改判：不锈钢水槽水龙头泛青冷偏色(D-L1)，马克杯欠饱和发灰(E2-L2)。"
    },
    1223: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "长条餐桌上铺设的蓝色桌布严重错涂偏色为暗红褐色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "巧克力生日蛋糕与孩子们衣物色彩过深偏浓。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "室内聚会桌面色彩失真严重。"}
        ],
        "note": "洛熙视觉改判：蓝色桌布严重错涂偏色为暗红褐色(D-L2)，生日蛋糕色彩过深(E1-L1)。"
    },
    1225: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "夜景中行驶的红色双层巴士车身红色过于浓烈深暗。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "建筑尖顶泛光照明与深黑夜空过渡稍显生硬。"}
        ],
        "note": "洛熙视觉改判：红色双层巴士车身红色过于浓烈深暗(E1-L2)。"
    },
    1228: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "狂欢节游行队伍中人物穿戴的动物玩偶戏服色彩过于浓烈刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "周围围观人群肤色与背景遮阳伞色彩对比生硬不自然。"}
        ],
        "note": "洛熙视觉改判：动物玩偶戏服色彩过于浓烈刺眼(E1-L2)，周围人群肤色生硬(F-L2)。"
    },
    1231: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "蓝色花瓶色彩过于浓艳刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "淡粉色球状菊花花瓣泛青白偏色且花瓶边缘过渡稍显生硬。"}
        ],
        "note": "洛熙视觉改判：蓝色花瓶色彩过于浓艳刺眼(E1-L2)，花瓣边缘生硬(F-L1)。"
    },
    1245: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "餐桌上的热狗面包、青柠切块及红色饮料易拉罐整体泛微暗红偏色。"}
        ],
        "note": "洛熙视觉改判：热狗面包、青柠切块及易拉罐整体泛微暗红偏色(D-L1)。"
    }
}

# 1. 更新 grounding_remaining_batch_05.json
if os.path.exists(GROUNDING_FILE):
    with open(GROUNDING_FILE, "r", encoding="utf-8") as f:
        groundings = json.load(f)
else:
    groundings = {}

for tid_int, data in NEW_GROUNDINGS.items():
    tid_str = str(tid_int)
    groundings[tid_str] = {
        "defects": data["defects"],
        "note": data["note"]
    }

with open(GROUNDING_FILE, "w", encoding="utf-8") as f:
    json.dump(groundings, f, ensure_ascii=False, indent=2)
print(f"Updated {GROUNDING_FILE}, total grounded tasks: {len(groundings)}")

# 2. 同步更新 reviewed_1_10000_all.json
with open(ALL_EXPORT, "r", encoding="utf-8") as f:
    all_data = json.load(f)

updated_all = 0
for ann in all_data["annotations"]:
    tid = ann["human_review"]["task_id"]
    if tid in NEW_GROUNDINGS:
        info = NEW_GROUNDINGS[tid]
        ann["defects"] = info["defects"]
        ann["review_note"] = info["note"]
        ann["review_status"] = "已核验"
        updated_all += 1

with open(ALL_EXPORT, "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)
print(f"Updated {updated_all} tasks in {ALL_EXPORT}")

# 3. 同步更新 reviewed_1_10000_clean.json
with open(CLEAN_EXPORT, "r", encoding="utf-8") as f:
    clean_data = json.load(f)

updated_clean = 0
for ann in clean_data["annotations"]:
    tid = ann["human_review"]["task_id"]
    if tid in NEW_GROUNDINGS:
        info = NEW_GROUNDINGS[tid]
        ann["defects"] = info["defects"]
        ann["review_note"] = ""
        ann["review_status"] = "已核验"
        updated_clean += 1

with open(CLEAN_EXPORT, "w", encoding="utf-8") as f:
    json.dump(clean_data, f, ensure_ascii=False, indent=2)
print(f"Updated {updated_clean} tasks in {CLEAN_EXPORT}")

print("Batch 05 strict re-audit application complete!")
