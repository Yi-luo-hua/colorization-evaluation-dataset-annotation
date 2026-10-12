# -*- coding: utf-8 -*-
import json
import os
import sys

BASE_DIR = r"d:\学业文件\MCL\上色评价_数据集标注"
GROUNDING_FILE = os.path.join(BASE_DIR, "LS_lcad_reviewer", "intermediate", "audits", "grounding_remaining_batch_07.json")
ALL_EXPORT = os.path.join(BASE_DIR, "LS_lcad_reviewer", "exports", "reviewed_1_10000_all.json")
CLEAN_EXPORT = os.path.join(BASE_DIR, "LS_lcad_reviewer", "exports", "reviewed_1_10000_clean.json")

NEW_GROUNDINGS = {
    1378: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "地面黄土与背景岩石泛暗红褐色偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "绵羊背部标记与人物衣物色彩欠饱和发灰。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "整幅画面色彩缺乏层次与真实质感。"}
        ],
        "note": "洛熙视觉改判：绵羊背部标记与人物衣物欠饱和(E2-L2)，地面与背景岩石泛暗红褐偏色(D-L2)。"
    },
    1379: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L3", "description": "室内背景浅色墙面与高光区域严重泛惨白暖黄且过曝失真。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "男子身穿的深蓝色短袖及面部肤色对比过于浓烈生硬。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "室内光影明暗交界过渡粗糙失真。"}
        ],
        "note": "洛熙视觉改判：背景浅色墙面严重泛黄过曝(D-L3)，深蓝短袖及面部肤色对比过于浓烈(E1-L2)。"
    },
    1385: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L3", "description": "笔记本电脑屏幕偏冷紫光，暗部背景与手指受光严重失调。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "手部受光面过度偏黄褐且局部色彩浓烈生硬。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "键盘按键与暗部背景边缘过渡不自然。"}
        ],
        "note": "洛熙视觉改判：笔记本屏幕偏紫冷光(D-L3)，手指受光面过度偏黄且对比生硬(E1-L2)。"
    },
    1394: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "卫生间洗手台台面、马桶座圈及墙面瓷砖严重泛青冷蓝灰色调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "室内整体卫浴色彩欠饱和发灰发冷。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "卫生间光影与洁具色彩显得冰冷不自然。"}
        ],
        "note": "洛熙视觉改判：洗手台与马桶座圈严重泛青冷蓝灰偏色(D-L2)，色彩欠饱和发冷(E2-L2)。"
    },
    1417: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "客厅墙壁与天花板整体泛暗黄褐色偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "深色沙发与茶几在阴影中色彩欠饱和发灰发暗。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "室内采光与家具质感缺乏通透感。"}
        ],
        "note": "洛熙视觉改判：客厅墙面天花板泛暗黄褐偏色(D-L2)，深色沙发与阴影家具欠饱和(E2-L2)。"
    },
    1424: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "陶瓷马桶盖、马桶圈与内壁泛浑浊暖黄色偏。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "旁边悬挂的毛巾与瓷砖欠饱和发灰。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "陶瓷洁具与卫生间色彩质感欠自然。"}
        ],
        "note": "洛熙视觉改判：马桶圈与内壁泛浑浊暖黄色偏(D-L2)，悬挂毛巾欠饱和发灰(E2-L2)。"
    },
    1439: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "水泥地面及背景桥梁泛暗红偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "自行车车筐物品与远处绿化带植物欠饱和泛灰。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "户外路面光影与色彩对比略显失真。"}
        ],
        "note": "洛熙视觉改判：水泥路面及背景桥梁泛暗红偏色(D-L2)，车筐物品与绿植欠饱和(E2-L2)。"
    },
    1440: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "室内白色罗马立柱、门框与天花板泛暖黄偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "深色木质扶手椅与阴影处家具色彩欠饱和发暗。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "室内灯光照射下的色彩层次略显单一。"}
        ],
        "note": "洛熙视觉改判：白色立柱与天花板泛暖黄偏色(D-L2)，阴影处扶手椅色彩欠饱和(E2-L2)。"
    },
    1443: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "长毛猫咪的白色与灰色毛发大面积泛暗红褐色偏色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "猫咪毛发与周围深色织物背景边缘泛红杂色且质感不自然。"}
        ],
        "note": "洛熙视觉改判：长毛猫咪毛发大面积泛暗红褐色偏色(D-L2)，毛发边缘带有杂色(F-L2)。"
    },
    1476: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "公园长椅与背景草坪植物绿色过于浓艳刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "白色卷毛狗毛发边缘略带杂色且与周围绿草对比生硬。"}
        ],
        "note": "洛熙视觉改判：公园长椅与背景草坪绿色过于浓艳(E1-L2)，小狗毛发边缘杂色(F-L1)。"
    },
    1479: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "木质餐桌台面与披萨托盘整体色调偏暗且泛微冷红偏色。"}
        ],
        "note": "洛熙视觉改判：木质餐桌台面与披萨托盘整体泛微冷红偏色(D-L1)。"
    },
    1485: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "沙滩海边摆放的黄色与蓝色条纹遮阳伞、躺椅及沙滩地面整体偏暗且泛暖灰偏色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "沙滩受光面与遮阳伞边缘色彩过渡生硬。"}
        ],
        "note": "洛熙视觉改判：遮阳伞、沙滩椅及沙滩地面整体偏暗泛暖灰(D-L2)，光影过渡生硬(F-L2)。"
    },
    1492: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "小女孩的手臂与面部肤色及身后的墙面整体严重泛暖红偏色。"}
        ],
        "note": "洛熙视觉改判：小女孩面部、手臂肤色及身后墙面严重泛暖红偏色(D-L2)。"
    },
    1494: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "床头悬挂油画的墙壁与长耳猎犬毛发及床单整体泛暖黄暗褐色偏色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "床头暖灯光照下的受光过渡稍显僵硬。"}
        ],
        "note": "洛熙视觉改判：床头墙壁、长耳猎犬毛发泛暖黄暗褐色偏色(D-L2)。"
    },
    1496: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "滑雪场夜间地面积雪及远处雪坡整体严重泛暗红紫色偏。"}
        ],
        "note": "洛熙视觉改判：滑雪场夜间地面积雪及远处雪坡整体泛暗红紫色偏(D-L2)。"
    },
    1497: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "农场围栏内地面泥土及公牛头部毛发严重泛猪肝红偏色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "公牛身躯边缘与背景绿树红土的色彩过渡不自然。"}
        ],
        "note": "洛熙视觉改判：围栏内泥土及公牛头部毛发严重泛猪肝红偏色(D-L2)。"
    },
    1504: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L3", "description": "羽衣甘蓝蔬菜叶片及叶脉严重褪色并泛暗黄褐色偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "植物叶片整体欠饱和发灰，丧失绿色生机。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "蔬菜植株新鲜生机感严重缺失。"}
        ],
        "note": "洛熙视觉改判：羽衣甘蓝蔬菜叶片泛暗黄褐色(D-L3)，叶片欠饱和严重发灰(E2-L2)。"
    },
    1507: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "背景灌木树丛及荒原枯草严重偏暗黄发灰。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "绿色灌木植被色彩欠饱和褪色。"}
        ],
        "note": "洛熙视觉改判：背景灌木树丛及荒原枯草偏暗黄发灰(D-L1)，灌木欠饱和褪色(E2-L2)。"
    }
}

# 1. 更新 grounding_remaining_batch_07.json
with open(GROUNDING_FILE, "r", encoding="utf-8") as f:
    groundings = json.load(f)

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

print("Batch 07 strict re-audit application complete!")
