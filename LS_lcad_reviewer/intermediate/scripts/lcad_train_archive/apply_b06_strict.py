# -*- coding: utf-8 -*-
import json
import os
import sys

BASE_DIR = r"d:\学业文件\MCL\上色评价_数据集标注"
GROUNDING_FILE = os.path.join(BASE_DIR, "LS_lcad_reviewer", "intermediate", "audits", "grounding_remaining_batch_06.json")
ALL_EXPORT = os.path.join(BASE_DIR, "LS_lcad_reviewer", "exports", "reviewed_1_10000_all.json")
CLEAN_EXPORT = os.path.join(BASE_DIR, "LS_lcad_reviewer", "exports", "reviewed_1_10000_clean.json")

NEW_GROUNDINGS = {
    1265: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "餐盘中的炒蛋与烤肉色彩偏浓艳发深。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "餐盘边缘与周围桌面光影稍显生硬。"}
        ],
        "note": "洛熙视觉改判：炒蛋与烤肉色彩偏浓艳发深(E1-L2)，餐盘边缘光影生硬(F-L1)。"
    },
    1270: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "木质办公桌台面、转椅与室内白墙整体发灰发暗，色彩欠饱和。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "室内办公环境光影通透感不足。"}
        ],
        "note": "洛熙视觉改判：办公桌、转椅与墙面整体发暗欠饱和(E2-L2)，光影通透感不足(F-L1)。"
    },
    1283: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "铁轨两旁的草坡与灌木植被色彩欠饱和褪色严重。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "橙红色机车车身与两旁褪色草坡色彩过渡生硬不自然。"}
        ],
        "note": "洛熙视觉改判：两旁草坡与灌木欠饱和褪色(E2-L2)，车身与草坡过渡生硬(F-L1)。"
    },
    1284: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "浴室白色瓷砖墙面与暖气片高光区域呈现刺眼的冷蓝高对比。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "马桶与卫浴设备在冷光下质感生硬不自然。"}
        ],
        "note": "洛熙视觉改判：白色瓷砖墙与暖气片刺眼冷蓝高对比(E1-L2)，洁具质感生硬(F-L2)。"
    },
    1298: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "城市街景天空与楼房外立面泛暗黄褐色偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "道路行驶的公交车与前景出租车车身色彩欠饱和偏灰。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "整体街景光影通透感不足。"}
        ],
        "note": "洛熙视觉改判：天空与楼房泛暗黄褐偏色(D-L2)，公交车出租车车身欠饱和(E2-L1)。"
    },
    1310: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L3", "description": "户外大面积草坪呈现极其浓烈刺眼的荧光黄绿色偏。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "草地与远处飞盘色彩对比极度过饱和刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "整体草地质感严重失真失实。"}
        ],
        "note": "洛熙视觉改判：草坪呈现严重荧光黄绿偏色(D-L3)，色彩对比极度过饱和(E1-L2)。"
    },
    1316: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "蛋糕纸盒内部与包装边缘泛暗黄褐色偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "生日蛋糕上的蓝色奶油字样与糖霜欠饱和发灰。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "食品包装整体色调昏暗失真。"}
        ],
        "note": "洛熙视觉改判：蛋糕包装纸盒泛暗黄褐偏色(D-L2)，蓝色奶油字样欠饱和发灰(E2-L1)。"
    },
    1333: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "微缩模型房间的木质墙面与家具色彩欠饱和发灰。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "室内微缩景观整体色彩对比度偏低。"}
        ],
        "note": "洛熙视觉改判：微缩模型房间木质墙面与家具欠饱和发灰(E2-L2)。"
    },
    1350: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "衬底烘焙油纸及甜甜圈阴影轮廓严重泛青冷蓝偏色。"}
        ],
        "note": "洛熙视觉改判：衬底烘焙油纸及甜甜圈阴影泛青冷蓝偏色(D-L2)。"
    },
    1354: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "搬运香蕉工人的手臂与背部皮肤泛惨白青冷偏色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "工人的皮肤质感与周围青绿香蕉对比生硬不协调。"}
        ],
        "note": "洛熙视觉改判：工人的手臂与背部皮肤泛惨白青冷偏色(D-L2)，皮肤与香蕉对比生硬(F-L2)。"
    },
    1372: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "城楼仿古红墙与琉璃瓦泛暗褐偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "广场前景游人衣物与地砖色彩欠饱和发暗。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "历史建筑与广场场景缺乏通透生动感。"}
        ],
        "note": "洛熙视觉改判：城楼红墙琉璃瓦泛暗褐偏色(D-L2)，广场前景游人衣物欠饱和(E2-L2)。"
    },
    1375: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "双人床上的白色床单与枕头泛暗发黄绿偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "室内窗帘布艺与床品色彩欠饱和。"}
        ],
        "note": "洛熙视觉改判：白色床单与枕头泛暗发黄绿偏色(D-L2)，室内布艺欠饱和(E2-L1)。"
    },
    1376: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "陶瓷马桶圈与马桶盖边缘泛暗黄偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "地面铺贴瓷砖与水管在暗处色彩欠饱和。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "洁具材质与阴影质感粗糙失真。"}
        ],
        "note": "洛熙视觉改判：马桶圈与马桶盖边缘泛暗黄偏色(D-L2)，地砖与水管欠饱和(E2-L2)。"
    }
}

# 1. 更新 grounding_remaining_batch_06.json
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

print("Batch 06 strict re-audit application complete!")
