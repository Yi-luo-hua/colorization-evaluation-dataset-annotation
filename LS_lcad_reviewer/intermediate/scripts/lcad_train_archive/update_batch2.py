# -*- coding: utf-8 -*-
"""
update_batch2.py
更新 Batch 2 (Sheet 21..40, Cards 121..240, Tasks 2368..6470) 的审核结果：
1. 确认并更新 genuine passes（视觉差分纯黑的高保真放行项）
2. 注入多模态视觉直审的具象定物改判描述（重点错色 C-L2、E1、偏色 D、欠饱和 E2）
3. 严格遵循双轨制：
   - clean.json 的 review_note 100% 为 ""
   - all.json 的 review_note 详细记录具象定物描述（不带【...】前缀）
   - gpt_score 与 original_gpt_score 严格保持不变
   - defects 字段包含完整的 id, name, severity, description
   - 零抽象占位符，零 E1/E2 互斥
"""

import json
import shutil
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
PLAN_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "suspect_pass_revisions_plan.json"
ALL_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_all.json"
CLEAN_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_clean.json"

# Batch 2 confirmed genuine passes through visual inspection (diff heatmap pitch black & high fidelity)
BATCH2_GENUINE_PASSES = {
    2592, # 冲浪者在阴天海面冲浪
    2735, # 雪中古老石砌遗迹与撑伞行人
    2790, # 卫生间镜面、白色洗脸台与白毛巾
    2810, # 黑色六角瓷砖墙壁与白色洗脸盆
    2924, # 深色皮沙发后熟睡的黑狗
    2976, # 阁楼木地板与蹲式马桶
    4147, # 白色马桶与玻璃淋浴门
    4945, # 雪地中散步的行人与伯恩山犬
    6004, # 现代梳妆台与黑白挂钟/挂历
    6447, # 客厅壁炉与石砖墙面
}

# Specific visual groundings from direct sheet inspection (Sheet 21..40)
SPECIFIC_GROUNDINGS = {
    3255: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "棒球击球手佩戴的鲜艳亮红色棒球帽及球衣红色领口饰边被严重错涂为深藏青色。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L1",
                "description": "击球手皮肤与白色球衣整体带有轻度冷青色偏移。"
            }
        ],
        "note": "棒球击球手佩戴的鲜艳亮红色棒球帽及球衣红色领口饰边被严重错涂为深藏青色。"
    },
    3269: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "红色机车车头与车身正红色漆面大面积色偏泛灰暗紫蓝色。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L1",
                "description": "铁轨及机车周边地面整体泛冷蓝紫调。"
            }
        ],
        "note": "红色机车车头与车身正红色漆面大面积色偏泛灰暗紫蓝色。"
    },
    3298: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "海面上灰白色阴天海浪翻滚的浪花被错误涂染为刺眼不自然的翠绿色。"
            },
            {
                "id": "E1",
                "name": "过饱和",
                "severity": "L3",
                "description": "海浪被施加了过高的饱和度，青翠伪色极其浓艳刺目。"
            }
        ],
        "note": "海面上灰白色阴天海浪翻滚的浪花被错误涂染为刺眼不自然的翠绿色，且局部过饱和刺目。"
    },
    4376: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "复古老爷车原本低调的橄榄灰绿车身被错误喷涂为过于鲜艳刺目的翠绿草绿色。"
            },
            {
                "id": "E1",
                "name": "过饱和",
                "severity": "L1",
                "description": "老爷车车身金属漆面绿色过于浓重鲜亮。"
            }
        ],
        "note": "复古老爷车原本低调的橄榄灰绿车身被错误喷涂为过于鲜艳刺目的翠绿草绿色。"
    },
    6350: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "老人佩戴的亮青柠檬绿围巾严重脱色并泛淡黄白色，丧失鲜亮色彩。"
            }
        ],
        "note": "老人佩戴的亮青柠檬绿围巾严重脱色并泛淡黄白色，丧失鲜亮色彩。"
    },
    6382: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "幼儿熟睡时身上包裹的鲜亮红色毛毯整体褪色严重，错退为暗褐红色。"
            }
        ],
        "note": "幼儿熟睡时身上包裹的鲜亮红色毛毯整体褪色严重，错退为暗褐红色。"
    },
    6422: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L1",
                "description": "蛋糕侧面的粉红色CAKE糖霜艺术字褪色发浅灰，缺乏原样粉润质感。"
            },
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L1",
                "description": "蛋糕表面和周围托盘的暖色反光略显暗淡欠饱和。"
            }
        ],
        "note": "蛋糕侧面的粉红色CAKE糖霜艺术字褪色发浅灰，缺乏原样粉润质感。"
    },
    6437: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "生日蛋糕顶部的彩色糖果颗粒与奶油花饰严重脱色并混杂蓝紫色伪色斑块。"
            }
        ],
        "note": "生日蛋糕顶部的彩色糖果颗粒与奶油花饰严重脱色并混杂蓝紫色伪色斑块。"
    },
    6440: {
        "defects": [
            {
                "id": "D",
                "name": "偏色",
                "severity": "L1",
                "description": "办公室办公桌桌面纸张、键盘以及地面整体偏暗冷青绿色调。"
            }
        ],
        "note": "办公室办公桌桌面纸张、键盘以及地面整体偏暗冷青绿色调。"
    },
    6448: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "木质梳妆台上原本鲜艳粉红色的护肤乳液瓶身被彻底错涂为淡天蓝色。"
            }
        ],
        "note": "木质梳妆台上原本鲜艳粉红色的护肤乳液瓶身被彻底错涂为淡天蓝色。"
    },
    6451: {
        "defects": [
            {
                "id": "D",
                "name": "偏色",
                "severity": "L1",
                "description": "自拍男士的面部肤色泛不自然的灰粉紫红色调，中性肤色失真。"
            },
            {
                "id": "F",
                "name": "视觉自然度",
                "severity": "L1",
                "description": "面部皮肤存在轻微色斑不均感。"
            }
        ],
        "note": "自拍男士的面部肤色泛不自然的灰粉紫红色调，中性肤色失真。"
    },
    6456: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "海面冲浪者脚下的亮粉红色冲浪板严重脱色错涂为灰白色。"
            },
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L2",
                "description": "原本鲜艳的冲浪板严重丧失色彩活力。"
            }
        ],
        "note": "海面冲浪者脚下的亮粉红色冲浪板严重脱色错涂为灰白色。"
    },
    6459: {
        "defects": [
            {
                "id": "E1",
                "name": "过饱和",
                "severity": "L2",
                "description": "草地上中间母鸡身躯的羽毛被涂染成过于浓艳浓重的鲜红棕色。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L1",
                "description": "绿草地与母鸡羽毛整体偏红偏暖。"
            }
        ],
        "note": "草地上中间母鸡身躯的羽毛被涂染成过于浓艳浓重的鲜红棕色。"
    },
    6464: {
        "defects": [
            {
                "id": "D",
                "name": "偏色",
                "severity": "L1",
                "description": "厨房浅色原木吊柜与橱柜木纹表面整体偏红偏暖棕色调。"
            }
        ],
        "note": "厨房浅色原木吊柜与橱柜木纹表面整体偏红偏暖棕色调。"
    },
    6466: {
        "defects": [
            {
                "id": "D",
                "name": "偏色",
                "severity": "L1",
                "description": "卫生间洗手台及百叶窗区域暖黄色温有所减弱泛微冷调。"
            }
        ],
        "note": "卫生间洗手台及百叶窗区域暖黄色温有所减弱泛微冷调。"
    },
    6467: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "厨房窗台后原本清新的浅苹果绿背景墙面被大面积错涂为暖米黄色。"
            }
        ],
        "note": "厨房窗台后原本清新的浅苹果绿背景墙面被大面积错涂为暖米黄色。"
    },
    6470: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L1",
                "description": "室外红色消防栓顶部红漆褪色发暗灰红，缺乏原样鲜亮纯正红色。"
            },
            {
                "id": "B",
                "name": "溢色",
                "severity": "L1",
                "description": "消防栓后方白色木栏杆底部阴影区域渗入轻微红紫色溢色污染。"
            }
        ],
        "note": "室外红色消防栓顶部红漆褪色发暗灰红，后方白色木栏杆底部阴影有轻微红紫溢色。"
    }
}

def main():
    with open(PLAN_FILE, "r", encoding="utf-8") as f:
        plan = json.load(f)

    # 1. Update genuine passes in plan
    curr_passes = set(plan.get("genuine_passes", []))
    curr_passes.update(BATCH2_GENUINE_PASSES)
    plan["genuine_passes"] = sorted(list(curr_passes))

    # Remove genuine passes from revisions
    for pid in BATCH2_GENUINE_PASSES:
        if str(pid) in plan["revisions"]:
            del plan["revisions"][str(pid)]

    # 2. Update specific groundings in plan
    for tid, data in SPECIFIC_GROUNDINGS.items():
        st = str(tid)
        if st in plan["revisions"]:
            plan["revisions"][st]["defects"] = data["defects"]
            plan["revisions"][st]["review_note"] = data["note"]
        else:
            plan["revisions"][st] = {
                "task_id": tid,
                "defects": data["defects"],
                "review_note": data["note"]
            }

    with open(PLAN_FILE, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    print(f"Plan file updated. Genuine passes count: {len(plan['genuine_passes'])}, Revisions: {len(plan['revisions'])}")

    # 3. Update ALL_FILE
    print(f"Updating {ALL_FILE.name}...")
    with open(ALL_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    now_iso = datetime.now(timezone.utc).isoformat()
    rev_map = plan["revisions"]
    passes_set = set(plan["genuine_passes"])

    updated_all = 0
    for ann in all_data["annotations"]:
        tid = ann["human_review"]["task_id"]
        # Check if genuine pass
        if tid in passes_set:
            if ann["defects"] != [] or ann["review_note"] != "审查通过":
                ann["defects"] = []
                ann["review_note"] = "审查通过"
                ann["review_status"] = "已核验"
                ann["reviewed_score"] = None
                ann["needs_rescoring"] = True
                ann["human_review"]["updated_at"] = now_iso
                updated_all += 1
        elif str(tid) in rev_map:
            r = rev_map[str(tid)]
            ann["defects"] = r["defects"]
            ann["review_note"] = r["review_note"]
            ann["review_status"] = "已核验"
            ann["reviewed_score"] = None
            ann["needs_rescoring"] = True
            ann["human_review"]["updated_at"] = now_iso
            updated_all += 1

    all_data["meta"]["exported_at"] = now_iso
    with open(ALL_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {ALL_FILE.name}")

    # 4. Update CLEAN_FILE
    print(f"Updating {CLEAN_FILE.name}...")
    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    updated_clean = 0
    for ann in clean_data["annotations"]:
        tid = ann["human_review"]["task_id"]
        if tid in passes_set:
            if ann["defects"] != []:
                ann["defects"] = []
                ann["review_note"] = ""
                ann["review_status"] = "已核验"
                ann["reviewed_score"] = None
                ann["needs_rescoring"] = True
                ann["human_review"]["updated_at"] = now_iso
                updated_clean += 1
        elif str(tid) in rev_map:
            r = rev_map[str(tid)]
            ann["defects"] = r["defects"]
            ann["review_note"] = ""  # Clean always empty string
            ann["review_status"] = "已核验"
            ann["reviewed_score"] = None
            ann["needs_rescoring"] = True
            ann["human_review"]["updated_at"] = now_iso
            updated_clean += 1
        else:
            ann["review_note"] = ""

    clean_data["meta"]["exported_at"] = now_iso
    with open(CLEAN_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {CLEAN_FILE.name}")

if __name__ == "__main__":
    main()
