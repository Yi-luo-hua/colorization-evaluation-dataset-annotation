# -*- coding: utf-8 -*-
"""
update_batch3.py
更新 Batch 3 (Sheet 41..60, Cards 241..360, Tasks 6486..8322) 的审核结果：
1. 确认并更新 genuine passes（视觉差分纯黑的高保真放行项）
2. 注入多模态视觉直审的具象定物改判描述
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

BATCH3_GENUINE_PASSES = {
    6540, # 卫生间白色马桶与瓷砖地板
    6588, # 雪地中滑雪的人与松树
    6613, # 两位男士的老式泛黄肖像黑白照片
    6641, # 火车站大钟与钢结构屋顶
    7303, # 晴空绿树下的街头观光马车
    7639, # 无障碍卫生间与不锈钢扶手马桶
    7653, # 汽车窗边的黑色拉布拉多犬
    7724, # 火车软卧车厢内的白床单与黑背包
    7775, # 欧洲中世纪钟楼建筑
    7816, # 酒吧烛光下过生日的三位好友与蛋糕
    7950, # 桌前合影的三位黑西装男士
    7992, # 海滩边的戴草帽老人与狗
    8005, # 厨房深色实木橱柜与大理石台面
    8021, # 夜间红外相机下的黑熊
    8077, # 暮色城市红灯高亮的交通信号灯
    8085, # 厨房不锈钢料理台与橱柜
    8126, # 动物园水池边的北极熊
}

SPECIFIC_GROUNDINGS_B3 = {
    6490: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "稀树草原原本葱郁的草地被严重错涂为红褐色，斑马黑白条纹边缘带有明显红紫伪色毛边。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L1",
                "description": "整个地表与斑马毛色整体带有浓重的偏暖红黄偏移。"
            }
        ],
        "note": "稀树草原原本葱郁的草地被严重错涂为红褐色，斑马条纹边缘带有明显红紫毛边。"
    },
    6497: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "水上摩托艇滑行者身上原本鲜艳亮粉玫红色的救生衣被彻底脱色错退为灰白色。"
            },
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L1",
                "description": "救生衣及周边水花反光略显暗淡欠饱和。"
            }
        ],
        "note": "水上摩托艇滑行者身上原本鲜艳亮粉玫红色的救生衣被彻底脱色错退为灰白色。"
    },
    6565: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "佩戴黄色领带与奖牌小男孩领口内侧原本鲜艳的荧光蓝绿色运动服被错退为深暗紫色。"
            }
        ],
        "note": "佩戴黄色领带与奖牌小男孩领口内侧原本鲜艳的荧光蓝绿色运动服被错退为深暗紫色。"
    },
    6642: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "餐盘上原本金黄烘烤色的汉堡顶层面包被彻底严重错涂为墨黑色，西红柿片脱色发白。"
            },
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L2",
                "description": "汉堡配料整体色彩严重脱色泛灰。"
            }
        ],
        "note": "餐盘上原本金黄烘烤色的汉堡顶层面包被彻底严重错涂为墨黑色，西红柿片脱色发白。"
    },
    6838: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "汉莎航空客机机尾垂直尾翼上标志性的明黄色飞鹤圆形LOGO严重褪色脱落成灰白色。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L1",
                "description": "机尾垂直尾翼的深蓝底色出现轻微色温偏移。"
            }
        ],
        "note": "汉莎航空客机机尾垂直尾翼上标志性的明黄色飞鹤圆形LOGO严重褪色脱落成灰白色。"
    },
    6878: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L3",
                "description": "电脑屏幕网页截图两侧边栏被大面积施加了极其刺目突兀的鲜红桃红荧光伪色。"
            },
            {
                "id": "E1",
                "name": "过饱和",
                "severity": "L3",
                "description": "两侧边栏的红桃色伪色饱和度极度浓艳溢出。"
            }
        ],
        "note": "电脑屏幕网页截图两侧边栏被大面积施加了极其刺目突兀的鲜红桃红荧光伪色。"
    },
    7502: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "披萨包装盒表面醒目的绿色Pizza艺术印刷字样大面积脱色错涂为粉红浅灰。"
            }
        ],
        "note": "披萨包装盒表面醒目的绿色Pizza艺术印刷字样大面积脱色错涂为粉红浅灰。"
    },
    7677: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "鲜花花束正中央原本盛开的鲜明大黄色菊花被彻底错涂为粉红玫瑰色。"
            }
        ],
        "note": "鲜花花束正中央原本盛开的鲜明大黄色菊花被彻底错涂为粉红玫瑰色。"
    },
    7698: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "沥青路面上的白色摩托车车头被大面积涂染上突兀艳丽的翠绿荧光伪色。"
            },
            {
                "id": "E1",
                "name": "过饱和",
                "severity": "L2",
                "description": "车头绿色伪色极为浓重高亮。"
            }
        ],
        "note": "沥青路面上的白色摩托车车头被大面积涂染上突兀艳丽的翠绿荧光伪色。"
    },
    7703: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "室内青年聚会中最左侧女子身穿的翠绿色T恤严重脱色退成暗淡灰褐色。"
            }
        ],
        "note": "室内青年聚会中最左侧女子身穿的翠绿色T恤严重脱色退成暗淡灰褐色。"
    },
    7715: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "木栅栏后原本鲜艳的正红色皮卡车脱色变暗灰褐色，马鬃毛偏深红。"
            }
        ],
        "note": "木栅栏后原本鲜艳的正红色皮卡车脱色变暗灰褐色。"
    },
    7772: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L3",
                "description": "摊位木架上的深棕褐色毛绒玩具熊被荒谬且突兀地错涂为深海青蓝色。"
            }
        ],
        "note": "摊位木架上的深棕褐色毛绒玩具熊被荒谬且突兀地错涂为深海青蓝色。"
    },
    7824: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "骑摩托车青年下身原本鲜亮湛蓝色的牛仔裤被严重脱色错退为灰白色。"
            },
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L2",
                "description": "牛仔裤色彩活力严重丧失。"
            }
        ],
        "note": "骑摩托车青年下身原本鲜亮湛蓝色的牛仔裤被严重脱色错退为灰白色。"
    },
    7840: {
        "defects": [
            {
                "id": "E1",
                "name": "过饱和",
                "severity": "L2",
                "description": "电脑桌面上原本淡粉配黑边的鼠标垫被错误喷涂为浓艳刺目的荧光粉紫色。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L1",
                "description": "电脑桌面周边反光偏紫偏红。"
            }
        ],
        "note": "电脑桌面上原本淡粉配黑边的鼠标垫被错误喷涂为浓艳刺目的荧光粉紫色。"
    },
    7877: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "复古航海版画中原本灰黑色的帆船船体被大面积染成刺眼红褐色，周围海水泛浓艳蓝紫。"
            },
            {
                "id": "E1",
                "name": "过饱和",
                "severity": "L2",
                "description": "帆船画面色彩饱和度过高。"
            }
        ],
        "note": "复古航海版画中原本灰黑色的帆船船体被大面积染成刺眼红褐色，周围海水泛浓艳蓝紫。"
    },
    7961: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "沙滩上原本清澈湛蓝色的冲浪板被大面积错涂为浓艳紫红伪色。"
            }
        ],
        "note": "沙滩上原本清澈湛蓝色的冲浪板被大面积错涂为浓艳紫红伪色。"
    },
    8019: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "城市道路沥青路面原本鲜绿色的自行车专用车道涂装大面积褪色变成灰白色。"
            }
        ],
        "note": "城市道路沥青路面原本鲜绿色的自行车专用车道涂装大面积褪色变成灰白色。"
    },
    8034: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "水塘沐浴大象旁原本绿草如茵的岸边植被被大面积错涂为焦黄红褐色。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L1",
                "description": "岸边黄土地表整体泛红偏暖。"
            }
        ],
        "note": "水塘沐浴大象旁原本绿草如茵的岸边植被被大面积错涂为焦黄红褐色。"
    },
    8067: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "跳舞青年手中原本翠绿色的发光荧光棒被彻底错涂为粉红肉色。"
            }
        ],
        "note": "跳舞青年手中原本翠绿色的发光荧光棒被彻底错涂为粉红肉色。"
    },
    8078: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "砧板上的肉馅饼金黄微红表皮严重脱色变成灰黑暗紫色，缺乏原样食欲感。"
            },
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L1",
                "description": "肉馅饼整体色彩灰暗欠饱和。"
            }
        ],
        "note": "砧板上的肉馅饼金黄微红表皮严重脱色变成灰黑暗紫色。"
    },
    8233: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "街头原本鲜艳高光的红色STOP交通停牌严重脱色褪为暗沉灰暗红紫。"
            },
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L2",
                "description": "交通停牌红色反光涂层显著失真褪色。"
            }
        ],
        "note": "街头原本鲜艳高光的红色STOP交通停牌严重脱色褪为暗沉灰暗红紫。"
    }
}

def main():
    with open(PLAN_FILE, "r", encoding="utf-8") as f:
        plan = json.load(f)

    # 1. Update genuine passes in plan
    curr_passes = set(plan.get("genuine_passes", []))
    curr_passes.update(BATCH3_GENUINE_PASSES)
    plan["genuine_passes"] = sorted(list(curr_passes))

    for pid in BATCH3_GENUINE_PASSES:
        if str(pid) in plan["revisions"]:
            del plan["revisions"][str(pid)]

    # 2. Update specific groundings in plan
    for tid, data in SPECIFIC_GROUNDINGS_B3.items():
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
