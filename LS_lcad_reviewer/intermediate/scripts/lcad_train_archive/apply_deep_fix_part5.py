#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_deep_fix_part5.py
精准应用 Part 5 (Batch 7: 48 例 + Batch 9: 2 例，共 50 个高危样本) 的视觉大图直审改判结果：
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

# Part 5 (50 例) 视觉大图核验改判映射
PART5_REVIEWS = {
    # Sheet 01
    3014: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "猫咪趴卧的鲜红色软垫底座欠饱和脱色变灰暗深褐。"}],
        "note": "核查发现：猫咪趴卧的鲜红色软垫底座欠饱和脱色变灰暗深褐(C-L2)。"
    },
    3038: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "背景蔚蓝晴空严重脱色褪变为发黄发暗的阴霾天幕。"}],
        "note": "核查发现：背景蔚蓝晴空严重脱色褪变为发黄发暗的阴霾天幕(C-L2)。"
    },
    3052: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "玻璃杯中盛放的原本极其鲜亮诱人的橙黄色鲜榨果汁被恶性错涂为浅粉紫色。"}],
        "note": "核查发现：原本鲜亮的橙黄色鲜榨果汁被恶性错涂为浅粉紫色(C-L2)。"
    },
    3062: {
        "defects": [],
        "note": "餐盘蛋糕白奶油、金黄橙子片与黑咖啡还原准确，兰花插花色彩自然协调，物理自洽放行。"
    },
    3091: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "羊圈农夫身上穿着的淡天蓝色工装长袖上衣欠饱和脱色漂白为灰白色。"}],
        "note": "核查发现：农夫身上穿着的淡天蓝色工装长袖上衣欠饱和脱色漂白为灰白色(C-L2)。"
    },
    3108: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "背景蔚蓝天空严重泛黄暗沉，红底 STOP 交通标志与花坛红花欠饱和发暗。"}],
        "note": "核查发现：背景天空严重泛黄暗沉，红底 STOP 标志欠饱和发暗(C-L2)。"
    },

    # Sheet 02
    3116: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "女孩身上穿着的鲜亮粉红色条纹短袖T恤严重欠饱和脱色漂白为灰暗条纹。"}],
        "note": "核查发现：女孩鲜亮粉红色条纹短袖T恤欠饱和脱色漂白为灰暗条纹(C-L2)。"
    },
    3125: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "女童戴的粉红色遮阳帽与身下的彩色卡通浮板严重欠饱和脱色变灰暗。"}],
        "note": "核查发现：女童粉红色遮阳帽与彩色卡通浮板欠饱和脱色变灰暗(C-L2)。"
    },
    3137: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "室内落地窗周围墙体与天花板被大面积恶性错涂为荧光黄绿与灰白色伪色。"}],
        "note": "核查发现：室内落地窗周围墙体与天花板被错涂荧光黄绿伪色(C-L2)。"
    },
    3154: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "铁轨上行驶的原本极其醒目的大红色轻轨列车车身完全欠饱和脱色褪暗为灰黑色。"}],
        "note": "核查发现：原本极其醒目的大红色轻轨列车车身完全欠饱和脱色褪暗为灰黑色(C-L2)。"
    },
    3162: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "棒球场内野红土跑道被恶性错涂为突兀浅黄绿色，草坪过饱和偏色。"}],
        "note": "核查发现：棒球场内野红土跑道被错涂为突兀浅黄绿色(C-L2)。"
    },
    3166: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "盘中原本鲜亮诱人的橙红色熟胡萝卜块被恶性错涂为发暗枯黄土褐色，餐盘偏深蓝。"}],
        "note": "核查发现：熟胡萝卜块被恶性错涂为发暗枯黄土褐色，餐盘偏深蓝(C-L2)。"
    },

    # Sheet 03
    3174: {
        "defects": [],
        "note": "北极熊毛色微泛浅黄白，海滩沙地灰暗自然，整体景深色调协调，物理自洽放行。"
    },
    3181: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "蛋糕表面书写的祝贺手写体文字原本为翠绿色，被恶性错涂为深宝蓝色伪色。"}],
        "note": "核查发现：蛋糕表面的翠绿色祝贺文字被恶性错涂为深宝蓝色伪色(C-L2)。"
    },
    3185: {
        "defects": [{"id": "C", "name": "错色", "severity": "L1", "description": "空中逆光飞行的飞盘上的鲜艳彩色环状条纹欠饱和脱色变灰暗。"}],
        "note": "核查发现：空中逆光飞盘上的彩色环状条纹欠饱和脱色变灰暗(C-L1)。"
    },
    3198: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "卫生间原本统一冷青灰色调的墙面与地面被恶性错涂为不协调的暗紫褐色。"}],
        "note": "核查发现：卫生间冷青灰墙面与地面被恶性错涂为暗紫褐色(C-L2)。"
    },
    3202: {
        "defects": [{"id": "C", "name": "错色", "severity": "L1", "description": "运动员所穿球衣的鲜艳翠绿衣领及手腕上的亮橙色运动手环欠饱和脱色。"}],
        "note": "核查发现：球衣翠绿衣领及手腕亮橙色运动手环轻度脱色(C-L1)。"
    },
    3206: {
        "defects": [],
        "note": "商业步行街长廊地面淡蓝灰与原木门框、白色长椅搭配协调，空间透视自然，物理自洽放行。"
    },

    # Sheet 04
    3223: {
        "defects": [],
        "note": "硬地网球场淡天蓝内场与深宝蓝外场还原精准，看台观众与球网自然，物理自洽放行。"
    },
    3238: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "篮中切块的紫红色甜菜根与鲜橙色胡萝卜严重欠饱和脱色泛枯暗灰褐。"}],
        "note": "核查发现：紫红色甜菜根与橙色胡萝卜严重欠饱和脱色泛灰褐(C-L2)。"
    },
    3277: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "大本钟表盘及钟楼塔身原本通透温暖的金黄色夜景照明灯光被恶性错涂为荧光黄绿色。"}],
        "note": "核查发现：大本钟表盘夜景照明金黄灯光被错涂荧光黄绿色(C-L2)。"
    },
    3291: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "男子手持的鲜黄色菱形 NEW 标识牌严重欠饱和脱色漂白为灰白色。"}],
        "note": "核查发现：男子手持的鲜黄色 NEW 标识牌欠饱和脱色漂白为灰白色(C-L2)。"
    },
    3292: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "室内网球场女运动员下身穿着的鲜红色运动长裤被恶性错涂为冷灰浅蓝色。"}],
        "note": "核查发现：女运动员下身穿着的鲜红色运动长裤被错涂为冷灰浅蓝色(C-L2)。"
    },
    3298: {
        "defects": [],
        "note": "冲浪手在碧海白浪中穿行，海面与水花过渡自然，无偏色，物理自洽放行。"
    },

    # Sheet 05
    3307: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "沙滩特种轮椅下方的暖木质甲板地面被恶性错涂为冰冷浅灰白色。"}],
        "note": "核查发现：沙滩轮椅下方的暖木质甲板地面被错涂为浅灰白色(C-L2)。"
    },
    3308: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "摩托车车把左下方堆放的原本鲜红色线缆/布料被恶性错涂为深棕土褐色。"}],
        "note": "核查发现：车把左下方鲜红色线缆布料被恶性错涂为深棕土褐色(C-L2)。"
    },
    3333: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "棒球场外场原本平整翠绿的草坪被恶性错涂为突兀的青蓝与紫灰伪色。"}],
        "note": "核查发现：棒球场外场翠绿草坪被恶性错涂为青蓝与紫灰伪色(C-L2)。"
    },
    3336: {
        "defects": [{"id": "C", "name": "错色", "severity": "L1", "description": "切菜少年内搭的鲜亮黄色印花T恤欠饱和脱色漂白为灰白色。"}],
        "note": "核查发现：少年内搭鲜亮黄色印花T恤欠饱和脱色漂白为灰白色(C-L1)。"
    },
    3337: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "法网公开赛极其标志性的平整砖红橙色红土球场地面被彻底恶性错涂为冷青灰墨绿色硬地伪色。"}],
        "note": "核查发现：标志性砖红橙色红土球场被彻底错涂为冷青灰墨绿色硬地(C-L2)。"
    },
    3343: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "卫生间小便池背后原本温暖的红褐色瓷砖墙体完全脱色蜕变为阴冷惨白的灰白砖墙。"}],
        "note": "核查发现：小便池背后红褐色瓷砖墙完全脱色褪暗为阴冷惨白的灰白墙(C-L2)。"
    },

    # Sheet 06
    3372: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "逆光海面与天空原本金黄璀璨的落日余晖光泽严重欠饱和脱色褪暗为灰白色。"}],
        "note": "核查发现：海面与天空金黄璀璨的落日余晖严重脱色褪暗为灰白色(C-L2)。"
    },
    3378: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "海面上空飞行的原本鲜红色小型双翼螺旋桨飞机机身欠饱和脱色变灰暗。"}],
        "note": "核查发现：原本鲜红色小型双翼螺旋桨飞机机身欠饱和脱色变灰暗(C-L2)。"
    },
    3382: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "卧室床头背后原本温暖的红褐色乳胶漆背景墙面被恶性错涂为冷青灰石板色。"}],
        "note": "核查发现：床头背后红褐色乳胶漆背景墙面被恶性错涂为冷青灰石板色(C-L2)。"
    },
    3385: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "长毛白猫身下趴卧的原本鲜艳的深酒红色绒布软垫欠饱和脱色蜕变为暗黑灰色。"}],
        "note": "核查发现：白猫身下深酒红色绒布软垫欠饱和脱色蜕变为暗黑灰色(C-L2)。"
    },
    3398: {
        "defects": [],
        "note": "街头红砖建筑与苍翠行道树绿荫层次分明，行人与路面色调自然协调，物理自洽放行。"
    },
    3402: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "交通信号灯立柱最上方亮起的原本极其醒目的鲜红色指示圆灯严重脱色发暗变枯灰。"}],
        "note": "核查发现：交通信号灯最上方鲜红色指示圆灯严重脱色发暗变枯灰(C-L2)。"
    },

    # Sheet 07
    3416: {
        "defects": [],
        "note": "复古客厅皮沙发、茶色木几与浅蓝单人布艺椅色调舒适和谐，无恶性失真，物理自洽放行。"
    },
    3445: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "天花板下方悬挂的多彩节庆流苏挂毯与工艺伞饰严重欠饱和脱色变灰暗。"}],
        "note": "核查发现：天花板下方多彩节庆流苏挂毯与工艺伞饰严重欠饱和脱色变灰暗(C-L2)。"
    },
    3454: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "青年男子身后原本温暖的暖木色背景墙体被恶性错涂为冰冷浅灰白色。"}],
        "note": "核查发现：青年男子身后原本温暖的暖木色背景墙被错涂为浅灰白色(C-L2)。"
    },
    3458: {
        "defects": [],
        "note": "现代厨房嵌入式烤箱不锈钢金属质感纯正，灰色极简橱柜光影自洽，物理自洽放行。"
    },
    3459: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "蛋糕顶部的红色火车头模型与方形蛋糕表面的粉红色糖霜奶油严重欠饱和脱色变脏暗。"}],
        "note": "核查发现：蛋糕顶部红色火车头与粉红糖霜奶油严重欠饱和脱色变脏暗(C-L2)。"
    },
    3461: {
        "defects": [],
        "note": "花猫毛色真实自然，身下民族刺绣地毯红黄蓝绿拼花鲜艳分明、还原度极佳，物理自洽放行。"
    },

    # Sheet 08
    3463: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "客机机身与尾翼原本标志性的红色与蓝色航空涂装条纹严重欠饱和脱色变灰暗。"}],
        "note": "核查发现：客机机身原本标志性的红蓝航空涂装条纹严重欠饱和脱色变灰暗(C-L2)。"
    },
    3471: {
        "defects": [],
        "note": "草原草地上漫步的大象灰白皮毛真实，黄绿草坪与光影过渡自然，物理自洽放行。"
    },
    3472: {
        "defects": [],
        "note": "商场展柜前礼仪小姐黑色连衣裙纯正，冰箱内部各色饮料还原逼真，物理自洽放行。"
    },
    3496: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "女子身上穿着的原本纯黑色短袖T恤被恶性错涂为突兀的暗红色。"}],
        "note": "核查发现：女子身上穿着的纯黑色短袖T恤被恶性错涂为突兀暗红色(C-L2)。"
    },
    3497: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "草坪少女身上穿着的原本鲜亮醒目的大红色短袖T恤严重欠饱和脱色褪暗。"}],
        "note": "核查发现：草坪少女原本鲜亮醒目的大红色短袖T恤严重欠饱和脱色褪暗(C-L2)。"
    },
    3499: {
        "defects": [],
        "note": "舞台红地毯艳丽，舞者天蓝色戏服与彩伞纯正自然，整体节日氛围浓郁，物理自洽放行。"
    },

    # Sheet 09 (Batch 9 遗留 2 例)
    4092: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "横跨街道正上方最醒目的大型霓虹灯箱招牌原本为亮黄色底，被恶性错涂为冰冷浅蓝色伪色。"}],
        "note": "核查发现：街道上方最醒目的大型霓虹灯箱招牌被恶性错涂为浅蓝色伪色(C-L2)。"
    },
    4459: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "广场中央喷泉圆形水池中的水体被恶性错涂为刺眼突兀的荧光天青蓝色伪色。"}],
        "note": "核查发现：广场中央喷泉水池水体被恶性错涂为刺眼荧光天青蓝色伪色(C-L2)。"
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
        if tid in PART5_REVIEWS:
            rev = PART5_REVIEWS[tid]
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

    print(f"Updated {updated_count} Part 5 high-risk items in memory.")
    assert updated_count == 50, f"Expected 50 updated items, got {updated_count}"

    with open(ALL_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved: {ALL_FILE.name}")

    with open(CLEAN_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved: {CLEAN_FILE.name}")

    print("\n[SUCCESS] Part 5 deep fix successfully applied to all exports!")

if __name__ == "__main__":
    main()
