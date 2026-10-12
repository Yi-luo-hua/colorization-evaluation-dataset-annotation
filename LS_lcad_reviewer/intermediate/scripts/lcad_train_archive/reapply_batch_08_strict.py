import json
import os
import sys

GROUNDING_B08_FIXES = {
    1544: {
        "score": None,
        "severities": {"D": "L1"},
        "descriptions": {
            "D": "室内大厅背景墙面与白色地面瓷砖轻微偏冷青蓝调。"
        },
        "note": "室内大厅背景墙面与地面瓷砖轻微偏冷青蓝调（D-L1）。"
    },
    1553: {
        "score": None,
        "severities": {"D": "L1", "F": "L1"},
        "descriptions": {
            "D": "火车站台钢结构顶棚与暗部柱体略带黄绿偏色。",
            "F": "站台暗部细节过渡略显生硬沉闷。"
        },
        "note": "火车站台钢结构顶棚与暗部柱体略带黄绿偏色，细节过渡偏沉闷（D-L1, F-L1）。"
    },
    1561: {
        "score": None,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "descriptions": {
            "D": "木质窗框与左侧浅色墙面呈现明显的紫红色偏色染污。",
            "E1": "窗台中央陈列装饰摆件的翠绿与鲜蓝饱和度过高发亮，呈现刺眼荧光感。",
            "F": "高饱和装饰物与昏暗紫红背景融合极差，整体观感割裂生硬。"
        },
        "note": "木质窗框与墙面呈现明显紫红偏色，窗台摆件蓝绿两色过度荧光浓艳（D-L2, E1-L2, F-L2）。"
    },
    1567: {
        "score": None,
        "severities": {"D": "L2", "F": "L1"},
        "descriptions": {
            "D": "花猫毛发、木质地板与周围环境大面积被浑浊的黄褐色偏色笼罩。",
            "F": "整体色调泛脏泛旧，削弱了猫咪毛发原本柔顺的色彩层次。"
        },
        "note": "花猫毛发与木地板大面积被浑浊的黄褐色偏色笼罩，层次泛脏发暗（D-L2, F-L1）。"
    },
    1571: {
        "score": None,
        "severities": {"D": "L1", "E1": "L1", "F": "L1"},
        "descriptions": {
            "D": "舞台聚光灯环境整体微偏冷青蓝调。",
            "E1": "表演者所穿的紫红色上衣与亮蓝色长裤饱和度略显偏高浓烈。",
            "F": "人物服饰冷暖高光反差稍显人工。"
        },
        "note": "舞台表演者服饰紫红与亮蓝饱和度略显偏高浓艳，环境微偏冷青蓝（D-L1, E1-L1, F-L1）。"
    },
    1578: {
        "score": None,
        "severities": {"B": "L2", "D": "L1", "F": "L2"},
        "descriptions": {
            "B": "中央人物所穿白色上衣、手臂轮廓及左下方提花地毯边缘严重渗染出刺眼的粉红色伪色杂斑。",
            "D": "室内背景家具与墙面整体微偏冷青蓝调。",
            "F": "白色衣服与地毯上的粉红渗色严重破坏了织物材质真实感。"
        },
        "note": "人物白色上衣、手臂及提花地毯边缘严重溢色渗出粉红杂斑（B-L2, D-L1, F-L2）。"
    },
    1592: {
        "score": None,
        "severities": {"D": "L2"},
        "descriptions": {
            "D": "办公桌面台灯照射区域与木质桌面呈现过于浓厚的黄橙色偏色，色温过度偏暖。"
        },
        "note": "办公桌面台灯光照区与木质桌面呈现过度浓厚的黄橙色偏色（D-L2）。"
    },
    1606: {
        "score": None,
        "severities": {"D": "L1"},
        "descriptions": {
            "D": "街头红砖建筑外墙与人行道地面轻微偏暖红黄调。"
        },
        "note": "街头红砖建筑外墙与人行道轻微偏暖红黄调（D-L1）。"
    },
    1607: {
        "score": None,
        "severities": {"D": "L1"},
        "descriptions": {
            "D": "马路交叉路口沥青路面与两侧树丛轻微偏暖红黄调。"
        },
        "note": "马路沥青路面与两侧树丛轻微偏暖红黄调（D-L1）。"
    },
    1608: {
        "score": None,
        "severities": {"D": "L1"},
        "descriptions": {
            "D": "公园草坪长椅与林荫道地面轻微偏暖红黄调。"
        },
        "note": "公园草坪长椅与林荫道轻微偏暖红黄调（D-L1）。"
    },
    1612: {
        "score": None,
        "severities": {"D": "L2"},
        "descriptions": {
            "D": "餐厅木质餐桌、背景墙面与餐盘中盛放的热狗食物全域笼罩在浓厚的暖黄橙色调中。"
        },
        "note": "木质餐桌与餐盘热狗食物全域明显偏暖黄橙色调（D-L2）。"
    },
    1617: {
        "score": None,
        "severities": {"D": "L1"},
        "descriptions": {
            "D": "城市街道商业招牌与沿街建筑立面轻微偏暖红黄调。"
        },
        "note": "沿街建筑立面与商业招牌轻微偏暖红黄调（D-L1）。"
    },
    1618: {
        "score": None,
        "severities": {"D": "L2"},
        "descriptions": {
            "D": "家庭客厅布艺沙发、茶几与木质地板全域呈现明显的暖红黄偏色。"
        },
        "note": "客厅布艺沙发、茶几与木地板全域呈现明显暖红黄偏色（D-L2）。"
    },
    1627: {
        "score": None,
        "severities": {"D": "L1"},
        "descriptions": {
            "D": "卧室白色双人床床单与床头木饰面板轻微偏洋红紫调。"
        },
        "note": "卧室白色床单与床头木饰面轻微偏洋红紫调（D-L1）。"
    },
    1641: {
        "score": None,
        "severities": {"D": "L1"},
        "descriptions": {
            "D": "滑雪场白雪皑皑的山体表面与缆车支撑钢柱轻微偏冷青蓝调。"
        },
        "note": "滑雪场覆雪山体与缆车钢柱轻微偏冷青蓝调（D-L1）。"
    },
    1644: {
        "score": None,
        "severities": {"D": "L1"},
        "descriptions": {
            "D": "机场停机坪客机白色机身与周围地勤车辆轻微偏冷青蓝调。"
        },
        "note": "停机坪客机白色机身轻微偏冷青蓝调（D-L1）。"
    },
    1646: {
        "score": None,
        "severities": {"D": "L2"},
        "descriptions": {
            "D": "起居室白色乳胶漆墙面与中性灰地毯带有较明显的粉红偏暖色调染色。"
        },
        "note": "起居室白色墙面与地毯带有较明显的粉红偏暖色调染色（D-L2）。"
    },
    1652: {
        "score": None,
        "severities": {"E1": "L2", "F": "L1"},
        "descriptions": {
            "E1": "公园草坪与绿化树木的绿色过于鲜艳浓烈，呈现出明显的人工荧光绿质感。",
            "F": "高饱和翠绿草地与周围自然光照环境失衡，降低了户外园林真实感。"
        },
        "note": "公园草坪与树木绿色过度浓艳发亮，呈现人工荧光质感（E1-L2, F-L1）。"
    },
    1658: {
        "score": None,
        "severities": {"E2": "L2", "F": "L1"},
        "descriptions": {
            "E2": "露天球场上运动的人物服饰、地面硬化跑道与后方看台色彩严重灰暗低饱和。",
            "F": "整幅画面色彩缺乏明亮对比，显得平淡灰哑丧失生机。"
        },
        "note": "露天球场运动人物服饰与跑道大面积欠饱和褪色泛灰（E2-L2, F-L1）。"
    },
    1679: {
        "score": None,
        "severities": {"B": "L2", "F": "L2"},
        "descriptions": {
            "B": "骑手所穿青绿色防风外套的颜色大面积向棕色马匹头颈部及皮革缰绳严重溢出渗染。",
            "F": "人马交界处突兀出现的青绿色晕染块产生严重的边界污损割裂感。"
        },
        "note": "骑手青绿外套颜色向棕马头颈与皮缰绳严重溢色渗透，交界处杂色割裂（B-L2, F-L2）。"
    },
    1680: {
        "score": None,
        "severities": {"D": "L1"},
        "descriptions": {
            "D": "欧式古典建筑石砌拱门与广场地砖轻微偏暖红黄调。"
        },
        "note": "古典建筑石砌拱门与地砖轻微偏暖红黄调（D-L1）。"
    },
    1681: {
        "score": None,
        "severities": {"D": "L1", "E1": "L1", "F": "L2"},
        "descriptions": {
            "D": "古堡护城河石砌护墙整体偏冷青蓝调。",
            "E1": "岸边攀附的绿植青苔色彩偏浓绿浓艳。",
            "F": "冷青石墙、浓绿水草与偏黄河水之间色彩过渡生硬，缺乏自然统一的采光融合。"
        },
        "note": "古堡护城河冷青石墙与浓绿水草色彩过渡生硬，略偏冷调（D-L1, E1-L1, F-L2）。"
    },
    1683: {
        "score": None,
        "severities": {"D": "L2", "E2": "L2"},
        "descriptions": {
            "D": "客厅木质立钟外壳与周围白色墙壁呈现出明显的黄绿色偏色染污。",
            "E2": "整体色彩较为灰暗低饱和，木质钟体纹理色彩层次不够鲜明。"
        },
        "note": "客厅木质立钟外壳与墙面呈现黄绿色偏色，色彩灰暗欠饱和（D-L2, E2-L2）。"
    },
    1687: {
        "score": None,
        "severities": {"D": "L1"},
        "descriptions": {
            "D": "沙滩排球场地的细沙与球员浅色球衣轻微偏暖泛黄。"
        },
        "note": "沙滩排球场细沙与球员球衣轻微偏暖泛黄（D-L1）。"
    },
    1722: {
        "score": None,
        "severities": {"D": "L1"},
        "descriptions": {
            "D": "商业街区行人服饰与道路砖石铺装轻微偏暖红黄调。"
        },
        "note": "商业街区行人服饰与道路铺装轻微偏暖红黄调（D-L1）。"
    },
    1723: {
        "score": None,
        "severities": {"D": "L1", "F": "L1"},
        "descriptions": {
            "D": "动物园水池边大象厚重粗糙的灰色皮肤与周围黄土泥地受到较重的暖橙黄偏色侵染。",
            "F": "环境过暖的色调压平了大象皮肤原有的冷灰肌理层次。"
        },
        "note": "大象厚重皮肤与周围黄土泥地受到较重暖橙黄偏色侵染（D-L1, F-L1）。"
    },
    1725: {
        "score": None,
        "severities": {"D": "L2"},
        "descriptions": {
            "D": "室内客厅白色墙面、布艺沙发与人物面部肤色大面积呈现出明显的粉紫色偏色。"
        },
        "note": "室内墙面、布艺沙发与人物肤色呈现明显粉紫色偏色（D-L2）。"
    },
    1737: {
        "score": None,
        "severities": {"B": "L2", "E1": "L2", "F": "L2"},
        "descriptions": {
            "B": "河道对岸背景青绿水草颜色向右侧成年大象后腿及臀部轮廓严重渗入，边缘呈现不自然青白光晕。",
            "E1": "岸边水草植被与河水表面青绿色饱和度过高浓艳，呈现荧光感。",
            "F": "灰褐大象与过饱和荧光水草之间生硬割裂，边缘渗色显著破坏了野生生态真实度。"
        },
        "note": "岸边水草向大象腿部边缘严重溢色渗染，水草植被饱和度过高浓艳（B-L2, E1-L2, F-L2）。"
    },
    1743: {
        "score": None,
        "severities": {"D": "L2", "E1": "L1"},
        "descriptions": {
            "D": "餐桌上切块披萨饼底、托盘与木质桌面整体出现明显的红橙色调偏移。",
            "E1": "披萨烘烤饼边与焦脆边缘红橙色过于浓烈刺眼。"
        },
        "note": "切块披萨饼底与木质桌面整体出现明显红橙色调偏移（D-L2, E1-L1）。"
    },
    1749: {
        "score": None,
        "severities": {"D": "L1", "E1": "L2", "F": "L2"},
        "descriptions": {
            "D": "室内花卉摆台与背景墙面整体微偏暖红黄调。",
            "E1": "玻璃花瓶中盛开的花朵与绿色枝叶色彩饱和度过度浓艳，呈现刺眼假花质感。",
            "F": "过度浓艳的花草配色破坏了插花艺术的柔美清新自然度。"
        },
        "note": "玻璃花瓶中盛开的花朵与绿叶饱和度过度浓艳刺眼，整体微偏暖红调（D-L1, E1-L2, F-L2）。"
    },
    1751: {
        "score": None,
        "severities": {"D": "L1"},
        "descriptions": {
            "D": "现代摩天大楼玻璃幕墙与天际线晴空轻微偏冷青蓝调。"
        },
        "note": "摩天大楼玻璃幕墙与天际线晴空轻微偏冷青蓝调（D-L1）。"
    },
    1757: {
        "score": None,
        "severities": {"D": "L2"},
        "descriptions": {
            "D": "室内两位合影女士的面部肤色与手臂皮肤被错染为明显的粉红色偏，与周围中性背景失衡。"
        },
        "note": "合影女士面部肤色与手臂皮肤被错染为明显的粉红偏色（D-L2）。"
    }
}

DEFECT_NAMES = {
    "A": "缺色",
    "B": "溢色",
    "C": "错色",
    "D": "偏色",
    "E1": "过饱和",
    "E2": "欠饱和",
    "F": "视觉自然度"
}

def main():
    print(f"=== 开始严格重审并注入 Batch 08 违规任务（共 {len(GROUNDING_B08_FIXES)} 个）===")
    
    # 1. 更新 grounding_remaining_batch_08.json
    g08_path = 'LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_08.json'
    with open(g08_path, 'r', encoding='utf-8') as f:
        g08_data = json.load(f)
        
    for tid, fix in GROUNDING_B08_FIXES.items():
        tid_str = str(tid)
        defects_list = []
        for did, sev in fix["severities"].items():
            defects_list.append({
                "id": did,
                "name": DEFECT_NAMES[did],
                "severity": sev,
                "description": fix["descriptions"][did]
            })
        g08_data[tid_str] = {
            "task_idx": tid,
            "score": fix["score"],
            "defects": defects_list,
            "note": fix["note"]
        }
    with open(g08_path, 'w', encoding='utf-8') as f:
        json.dump(g08_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] 已更新 {g08_path}")
    
    # 2. 更新 all.json
    all_path = 'LS_lcad_reviewer/exports/reviewed_1_10000_all.json'
    with open(all_path, 'r', encoding='utf-8') as f:
        all_data = json.load(f)
    anno_by_tid = {a['human_review']['task_id']: a for a in all_data['annotations'] if a.get('human_review')}
    
    c = 0
    for tid, fix in GROUNDING_B08_FIXES.items():
        if tid in anno_by_tid:
            ann = anno_by_tid[tid]
            defects_list = []
            for did, sev in fix["severities"].items():
                defects_list.append({
                    "id": did,
                    "name": DEFECT_NAMES[did],
                    "severity": sev,
                    "description": fix["descriptions"][did]
                })
            ann['defects'] = defects_list
            ann['review_status'] = "已核验"
            ann['review_note'] = fix['note']
            ann['reviewed_score'] = fix['score']
            ann['needs_rescoring'] = True
            c += 1
            
    with open(all_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] 已更新 {all_path}，同步修改: {c}")
    
    # 3. 更新 clean.json
    clean_path = 'LS_lcad_reviewer/exports/reviewed_1_10000_clean.json'
    with open(clean_path, 'r', encoding='utf-8') as f:
        clean_data = json.load(f)
    anno_clean_by_tid = {a['human_review']['task_id']: a for a in clean_data['annotations'] if a.get('human_review')}
    
    c = 0
    for tid, fix in GROUNDING_B08_FIXES.items():
        if tid in anno_clean_by_tid:
            ann = anno_clean_by_tid[tid]
            defects_list = []
            for did, sev in fix["severities"].items():
                defects_list.append({
                    "id": did,
                    "name": DEFECT_NAMES[did],
                    "severity": sev,
                    "description": fix["descriptions"][did]
                })
            ann['defects'] = defects_list
            ann['review_status'] = "已核验"
            ann['review_note'] = ""
            ann['reviewed_score'] = fix['score']
            ann['needs_rescoring'] = True
            c += 1
            
    with open(clean_path, 'w', encoding='utf-8') as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] 已更新 {clean_path}，同步修改: {c}")
    
    print("\nBatch 08 严格重审注入成功！")

if __name__ == '__main__':
    main()
