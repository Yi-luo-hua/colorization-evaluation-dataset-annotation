# -*- coding: utf-8 -*-
"""
update_batch4.py
更新 Batch 4 (Sheet 61..62, Cards 361..371, Tasks 8363..9951) 的审核结果：
1. 确认并更新 genuine passes（Task 9209）
2. 注入多模态视觉直审的具象定物改判描述（重点错色 C-L2/L3、过饱和 E1-L2/L3）
3. 严格遵循双轨制：
   - clean.json 的 review_note 100% 为 ""
   - all.json 的 review_note 详细记录具象定物描述（不带【...】前缀）
   - gpt_score 与 original_gpt_score 严格保持不变
   - defects 字段包含完整的 id, name, severity, description
   - 零抽象占位符，零 E1/E2 互斥
"""

import json
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
PLAN_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "suspect_pass_revisions_plan.json"
ALL_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_all.json"
CLEAN_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_clean.json"

BATCH4_GENUINE_PASSES = {
    9209, # 清晨/薄暮河流上的古桥
}

SPECIFIC_GROUNDINGS_B4 = {
    8921: {
        "defects": [
            {
                "id": "E1",
                "name": "过饱和",
                "severity": "L2",
                "description": "房间地板上女子所穿T恤被施加了过高的鲜亮紫红伪色，地板粉红拖鞋过于浓艳刺眼。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L1",
                "description": "女子衣物和拖鞋周边带有明显的偏紫红偏色。"
            }
        ],
        "note": "房间地板上女子所穿T恤被施加了过高的鲜亮紫红伪色，地板粉红拖鞋过于浓艳刺眼。"
    },
    9243: {
        "defects": [
            {
                "id": "E1",
                "name": "过饱和",
                "severity": "L1",
                "description": "积雪停车计时器中间铭牌上的红色警告字体过于鲜艳浓重。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L1",
                "description": "停车计时器底座及积雪反光带有轻微暖红偏移。"
            }
        ],
        "note": "积雪停车计时器中间铭牌上的红色警告字体过于鲜艳浓重。"
    },
    9502: {
        "defects": [
            {
                "id": "E1",
                "name": "过饱和",
                "severity": "L2",
                "description": "白瓷盘上胡萝卜蛋糕顶部的橙色糖渍配料被染成过于浓艳高光的亮橘红伪色。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L1",
                "description": "蛋糕表面和餐盘边缘反光带有轻微偏暖偏红。"
            }
        ],
        "note": "白瓷盘上胡萝卜蛋糕顶部的橙色糖渍配料被染成过于浓艳高光的亮橘红伪色。"
    },
    9826: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "正在喷射水流的室外消防栓原本明黄色的金属柱身被彻底严重错涂为高光粉红艳红色。"
            },
            {
                "id": "E1",
                "name": "过饱和",
                "severity": "L2",
                "description": "消防栓柱身错涂的粉红艳红色饱和度显著溢出，视觉违和刺目。"
            }
        ],
        "note": "正在喷射水流的室外消防栓原本明黄色的金属柱身被彻底严重错涂为高光粉红艳红色。"
    },
    9867: {
        "defects": [
            {
                "id": "E1",
                "name": "过饱和",
                "severity": "L2",
                "description": "停车场远处停靠的轿车被涂染成过于浓艳刺目的金黄色伪色。"
            },
            {
                "id": "C",
                "name": "错色",
                "severity": "L1",
                "description": "远处商场建筑物招牌色彩过于浓艳失真。"
            }
        ],
        "note": "停车场远处停靠的轿车被涂染成过于浓艳刺目的金黄色伪色。"
    },
    9951: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L3",
                "description": "游泳池边女童原本柔和的粉紫泳衣被彻底涂染成极为刺目浓艳的荧光亮粉红伪色，前排男童亮黄泳装领口脱色。"
            },
            {
                "id": "E1",
                "name": "过饱和",
                "severity": "L3",
                "description": "泳池边儿童泳装的粉红高光极为刺眼溢出，出现恶性荧光感。"
            }
        ],
        "note": "游泳池边女童原本柔和的粉紫泳衣被彻底涂染成极为刺目浓艳的荧光亮粉红伪色。"
    }
}

def main():
    with open(PLAN_FILE, "r", encoding="utf-8") as f:
        plan = json.load(f)

    # 1. Update genuine passes in plan
    curr_passes = set(plan.get("genuine_passes", []))
    curr_passes.update(BATCH4_GENUINE_PASSES)
    plan["genuine_passes"] = sorted(list(curr_passes))

    for pid in BATCH4_GENUINE_PASSES:
        if str(pid) in plan["revisions"]:
            del plan["revisions"][str(pid)]

    # 2. Update specific groundings in plan
    for tid, data in SPECIFIC_GROUNDINGS_B4.items():
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
