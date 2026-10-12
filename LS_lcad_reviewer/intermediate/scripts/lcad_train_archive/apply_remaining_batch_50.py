# -*- coding: utf-8 -*-
"""
应用 Batch 50 审核具象定物判决字典并双向同步至正式交付文件
Batch 50: Task #9888 ~ #9993 (共 64 组) —— 全项目终局收官批次！
"""

import json
import os
import re

# 64 组人工直审与具象定物判决字典
REVIEWS_B50 = {
    # Sheet 01
    9888: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    9889: {
        "score": 2.73,
        "severities": {"D": "L1", "E2": "L2"},
        "note": "室内沙发抱枕与暗红色木质茶几严重欠饱和褪色发灰(E2-L2)，全图整体光照泛暖黄偏色(D-L1)。"
    },
    9890: {
        "score": 2.43,
        "severities": {"E2": "L1", "F": "L2"},
        "note": "餐厅餐桌上盛放的烤火鸡与蔬菜沙拉盘欠饱和褪色发暗(E2-L1)，食物失去新鲜食欲感破坏画面自然度(F-L2)。"
    },
    9891: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    9893: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    9895: {
        "score": 4.46,
        "severities": {"D": "L1"},
        "note": "街景建筑外墙红砖立面与人行道地面全图轻微泛冷青偏色(D-L1)。"
    },

    # Sheet 02
    9896: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    9898: {
        "score": 2.23,
        "severities": {"D": "L2", "E2": "L2", "F": "L1"},
        "note": "客厅深褐色木质书架与室内地毯严重欠饱和发灰脱色(E2-L2)，全图呈现明显冷青冷灰偏色(D-L2)，室内光影层次失真破坏视觉自然度(F-L1)。"
    },
    9900: {
        "score": 4.55,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "厨房大理石操作台与背景瓷砖墙面色彩欠饱和泛灰(E2-L1)，全图环境光泛冷青偏色(D-L1)。"
    },
    9901: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    9903: {
        "score": 2.17,
        "severities": {"D": "L2", "E2": "L2", "F": "L2"},
        "note": "街道两侧停放的深色轿车与红砖沿街商铺立面大面积严重欠饱和褪色(E2-L2)，全图呈现深冷青灰偏色(D-L2)，街景沉闷破坏视觉自然度(F-L2)。"
    },
    9906: {
        "score": 5.0,
        "severities": {"E2": "L1"},
        "note": "公园草坪与行道树深绿树冠欠饱和发暗褪色(E2-L1)。"
    },

    # Sheet 03
    9909: {
        "score": 4.46,
        "severities": {"D": "L1"},
        "note": "办公室办公桌木纹台面与背景白色百叶窗全图轻微泛暖黄偏色(D-L1)。"
    },
    9910: {
        "score": 2.25,
        "severities": {"D": "L2", "E2": "L1", "F": "L2"},
        "note": "卧室双人床铺上的花纹床单与木质床头柜色彩欠饱和发灰(E2-L1)，全图呈现明显冷青偏色(D-L2)，卧室空间光影沉闷破坏视觉自然度(F-L2)。"
    },
    9911: {
        "score": 2.26,
        "severities": {"B": "L2", "D": "L2", "F": "L2"},
        "note": "自行车车架金属漆料越界溢色至车轮辐条与沥青路面(B-L2)，街道整体呈现显著冷灰偏色(D-L2)，边缘虚化破坏视觉自然度(F-L2)。"
    },
    9915: {
        "score": 4.46,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "果盘中摆放的鲜红苹果与黄香蕉色彩过于浓艳刺眼(E1-L1)，餐桌台布轻微泛暖黄偏色(D-L1)。"
    },
    9916: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    9918: {
        "score": 2.43,
        "severities": {"D": "L2", "E2": "L1"},
        "note": "城市火车站台水泥立柱与轨道道砟碎石色彩欠饱和暗淡(E2-L1)，站台全景呈现明显偏冷青灰调(D-L2)。"
    },

    # Sheet 04
    9920: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    9922: {
        "score": 2.73,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "客厅布艺转角沙发与木质茶几欠饱和泛灰褪色(E2-L1)，室内整体光影泛暖黄偏色(D-L1)。"
    },
    9923: {
        "score": 2.17,
        "severities": {"D": "L1", "E1": "L2", "F": "L2"},
        "note": "花园中盛开的粉红玫瑰与嫩绿枝叶色彩过度浓艳饱和(E1-L2)，全图泛青冷杂色(D-L1)，过饱和破坏花卉质感与视觉自然度(F-L2)。"
    },
    9924: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    9928: {
        "score": 2.17,
        "severities": {"D": "L1", "E2": "L2", "F": "L2"},
        "note": "棒球场看台观众红色服饰与绿茵草地大面积严重脱色发灰(E2-L2)，全图呈现明显泛暖黄暗沉偏色(D-L1)，赛场活力丧失严重破坏视觉自然度(F-L2)。"
    },
    9931: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 05
    9932: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    9933: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "餐桌上黄色向日葵花瓣色彩过于浓艳刺眼(E1-L1)，花瓶与白色桌布泛暖黄偏色(D-L1)。"
    },
    9934: {
        "score": 5.0,
        "severities": {"E2": "L1"},
        "note": "网球场绿色塑胶地面与球网白边欠饱和发暗褪色(E2-L1)。"
    },
    9935: {
        "score": 5.0,
        "severities": {"D": "L1"},
        "note": "厨房木质橱柜与大理石操作台面整体泛轻微暖黄偏色(D-L1)。"
    },
    9936: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    9937: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 06
    9939: {
        "score": 5.0,
        "severities": {"D": "L1", "E1": "L1"},
        "note": "街道上黄色出租车车身黄色车漆过于浓艳刺眼(E1-L1)，柏油马路与行道树泛冷青偏色(D-L1)。"
    },
    9940: {
        "score": 2.25,
        "severities": {"D": "L2", "E1": "L1", "F": "L2"},
        "note": "儿童房间粉色塑料玩具车与彩色积木过度浓艳(E1-L1)，木地板与墙面呈现明显冷灰偏色(D-L2)，色调冲突破坏视觉自然度(F-L2)。"
    },
    9942: {
        "score": 2.47,
        "severities": {"D": "L2", "E2": "L1", "F": "L1"},
        "note": "港口停泊的白色游艇船身与深蓝海水欠饱和发灰(E2-L1)，码头全景呈现明显偏冷青蓝调(D-L2)，画面通透度下降(F-L1)。"
    },
    9944: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    9945: {
        "score": 5.0,
        "severities": {"D": "L1"},
        "note": "湖畔木质码头栈桥与远方山林倒影整体泛轻微冷青偏色(D-L1)。"
    },
    9946: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 07
    9947: {
        "score": 5.0,
        "severities": {"D": "L1"},
        "note": "客厅摆放的红木茶几与单人扶手皮沙发欠饱和褪色偏暗，全图室内光照泛轻微冷灰偏色(D-L1)。"
    },
    9951: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    9952: {
        "score": 5.0,
        "severities": {"D": "L1"},
        "note": "铁道博物馆废弃老式黑色蒸汽机车铁皮外壳与钢轨地面全图泛冷青偏色(D-L1)。"
    },
    9953: {
        "score": 2.43,
        "severities": {"E2": "L2", "F": "L2"},
        "note": "亚洲风味餐盘中金黄炸春卷与翠绿香菜叶严重欠饱和褪色泛灰(E2-L2)，食物色彩丧失严重破坏视觉食欲与自然度(F-L2)。"
    },
    9954: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    9955: {
        "score": 2.73,
        "severities": {"D": "L1", "E1": "L2"},
        "note": "夜间酒吧吧台绚烂的霓虹灯招牌与酒瓶光晕色彩过于浓艳溢出(E1-L2)，吧台大理石台面泛偏青冷调(D-L1)。"
    },

    # Sheet 08
    9956: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    9959: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    9960: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    9961: {
        "score": 5.0,
        "severities": {"D": "L1"},
        "note": "现代咖啡馆木质吧台与悬挂吊灯全图光照泛明显冷青偏色(D-L1)。"
    },
    9962: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    9963: {
        "score": 5.0,
        "severities": {"D": "L1"},
        "note": "机场停机坪黄昏晚霞光影下停靠的白色双发客机与跑道地面全景呈现偏青冷色调(D-L1)。"
    },

    # Sheet 09
    9964: {
        "score": 2.73,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "沙滩海滨长椅场景中蓝白色公园长椅油漆欠饱和发灰褪色(E2-L1)，沙滩地面与天空整体泛冷青偏色(D-L1)。"
    },
    9966: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "棒球场背景高耸深绿树木与灌木护栏严重发灰褪色暗沉(E2-L1)，红土跑道与全景环境光泛冷青偏色(D-L1)。"
    },
    9967: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L1"},
        "note": "雪山滑雪场左侧滑雪者身穿的亮红色专业滑雪冲锋衣与滑雪裤被严重错涂为暗卡其橄榄绿色(C-L2)，林海雪原背景树木阴影泛暗草绿偏色(D-L1)。"
    },
    9970: {
        "score": 4.55,
        "severities": {"E2": "L1"},
        "note": "海景露台前景室内深蓝色布艺软垫与茶几台面欠饱和发灰褪色(E2-L1)，遮阳伞与户外海湾还原自然良好。"
    },
    9971: {
        "score": 2.47,
        "severities": {"D": "L1", "E2": "L2"},
        "note": "快餐餐桌上夏威夷果汁易拉罐红色罐口与紫色图案大面积欠饱和褪色发灰(E2-L2)，包装纸与桌面整体泛冷灰色偏(D-L1)。"
    },
    9974: {
        "score": 2.73,
        "severities": {"D": "L2", "E2": "L2"},
        "note": "广阔山坡牧场上大片翠绿草坪严重泛青冷褪色发灰(E2-L2)，放牧绵羊羊群与草地全域呈现显著冷青冷灰偏色(D-L2)。"
    },

    # Sheet 10
    9978: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    9979: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    9980: {
        "score": 1.08,
        "severities": {"D": "L2", "E2": "L2", "F": "L1"},
        "note": "极限滑板场水泥碗池坡道上喷绘的明橙与粉紫街头涂鸦壁画大面积严重欠饱和褪色泛灰(E2-L2)，水泥地面与草坡呈现明显冷青冷灰偏色(D-L2)，涂鸦色彩丧失破坏视觉自然度(F-L1)。"
    },
    9983: {
        "score": 2.17,
        "severities": {"C": "L2", "D": "L1", "E1": "L1"},
        "note": "定制西服展示模特浅蓝商务衬衫与粉蓝提花丝绸领带色彩过于浓艳(E1-L1)，背景原本柔和温暖的米黄灯光被常识性错涂为刺眼黄绿色(C-L2)，金属衣架与西服泛青冷杂色(D-L1)。"
    },
    9984: {
        "score": 2.17,
        "severities": {"C": "L2", "D": "L2"},
        "note": "热带稀树草原前景翠绿草地被严重错涂为暗棕褐色荒地(C-L2)，三只漫步的长颈鹿及整个天空全域笼罩在浓重黄褐暖色滤镜之中(D-L2)。"
    },
    9986: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 11
    9987: {
        "score": 2.08,
        "severities": {"C": "L2", "D": "L1", "E2": "L1"},
        "note": "幼童身穿的鲜艳酒红色长袖上衣大面积褪色发灰失真(E2-L1)，黑色花纹领带夹被常识性错涂为异样亮绿色(C-L2)，面部与头部肤色呈现过度泛红发烫的非自然色偏(D-L1)。"
    },
    9988: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "客厅中央摆放的鲜艳大红色双人布艺沙发严重欠饱和褪色为暗赭红褐色(E2-L1)，左侧装饰圣诞树松针与室内墙壁环境呈现整体偏黄绿调(D-L1)。"
    },
    9989: {
        "score": 2.73,
        "severities": {"D": "L2", "E2": "L2"},
        "note": "特写镜头下被抚摸的暖棕褐色虎斑猫全身浓密毛发完全丧失暖金底色，严重褪色脱色为冷银灰色(E2-L2)，人手肤色与背景床品全域泛冷青冷灰(D-L2)。"
    },
    9993: {
        "score": 5.0,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "街角复古绿色铜铸大钟两侧悬挂的美国国旗鲜艳红色条纹严重欠饱和发黄褪色(E2-L1)，钟楼石砌建筑外立面与悬挂钢架结构整体泛轻微冷青偏色(D-L1)。"
    }
}

DEFECT_NAME_MAP = {
    "A": "缺色",
    "B": "溢色",
    "C": "错色",
    "D": "偏色",
    "E1": "过饱和",
    "E2": "欠饱和",
    "F": "视觉自然度"
}

def main():
    print(f"Batch 50 defined reviews count: {len(REVIEWS_B50)}")
    assert len(REVIEWS_B50) == 64, f"Expected 64 reviews, got {len(REVIEWS_B50)}"

    # 1. 导出中间具象定物判决 JSON
    out_grounding_path = "LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_50.json"
    with open(out_grounding_path, "w", encoding="utf-8") as f:
        json.dump(REVIEWS_B50, f, ensure_ascii=False, indent=2)
    print(f"Exported grounding reviews to {out_grounding_path}")

    # 2. 读取正式交付文件
    all_path = "LS_lcad_reviewer/exports/reviewed_1_10000_all.json"
    clean_path = "LS_lcad_reviewer/exports/reviewed_1_10000_clean.json"

    with open(all_path, "r", encoding="utf-8") as f:
        data_all = json.load(f)

    with open(clean_path, "r", encoding="utf-8") as f:
        data_clean = json.load(f)

    anns_all = data_all["annotations"]
    anns_clean = data_clean["annotations"]

    # 建立 task_id 索引映射
    idx_map_all = {ann["human_review"]["task_id"]: i for i, ann in enumerate(anns_all)}
    idx_map_clean = {ann["human_review"]["task_id"]: i for i, ann in enumerate(anns_clean)}

    updated_count = 0
    passed_count = 0
    revised_count = 0

    for tid, rev in REVIEWS_B50.items():
        if tid not in idx_map_all:
            print(f"Warning: task_id {tid} not found in all dataset!")
            continue

        ann_a = anns_all[idx_map_all[tid]]
        ann_c = anns_clean[idx_clean_map_clean if (idx_clean_map_clean := idx_map_clean.get(tid)) is not None else 0]

        severities = rev["severities"]
        note = rev["note"]

        # 构建 defects 列表
        defects = []
        if severities:
            for code, sev in severities.items():
                defects.append({
                    "id": code,
                    "name": DEFECT_NAME_MAP.get(code, code),
                    "severity": sev,
                    "description": note
                })

        # 判断是否命中 A (缺色)
        has_a = "A" in severities

        # 同步更新 all 版本
        ann_a["review_status"] = "已核验"
        ann_a["review_note"] = note
        ann_a["defects"] = defects
        if has_a:
            ann_a["reviewed_score"] = 1.0
            ann_a["needs_rescoring"] = False
        else:
            ann_a["reviewed_score"] = None
            ann_a["needs_rescoring"] = True

        # 同步更新 clean 版本 (review_note 清空)
        ann_c["review_status"] = "已核验"
        ann_c["review_note"] = ""
        ann_c["defects"] = defects
        if has_a:
            ann_c["reviewed_score"] = 1.0
            ann_c["needs_rescoring"] = False
        else:
            ann_c["reviewed_score"] = None
            ann_c["needs_rescoring"] = True

        updated_count += 1
        if len(severities) == 0:
            passed_count += 1
        else:
            revised_count += 1

    print(f"Updated: {updated_count} (Passed: {passed_count}, Revised: {revised_count})")
    print(f"Pass rate: {passed_count / updated_count * 100:.2f}%")

    # 写回文件
    with open(all_path, "w", encoding="utf-8") as f:
        json.dump(data_all, f, ensure_ascii=False, indent=2)
    print(f"Synchronized {all_path}")

    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(data_clean, f, ensure_ascii=False, indent=2)
    print(f"Synchronized {clean_path}")

if __name__ == "__main__":
    main()
