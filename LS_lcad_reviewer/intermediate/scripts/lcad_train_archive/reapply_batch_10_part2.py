import json

GROUNDING_B10_PART2 = {
    2002: {
        "score": None,
        "severities": {"E2": "L3", "D": "L1", "F": "L2"},
        "descriptions": {
            "E2": "卫生间原本清爽的淡青色瓷砖墙面与地面严重脱色，大面积发白发灰接近单色灰度。",
            "D": "瓷砖阴影与角落处附带浑浊的暗黄灰土色偏。",
            "F": "整体脱色使卫生间环境极为灰暗沉闷，完全丧失真实卫浴采光的通透感。"
        },
        "note": "卫生间淡青色瓷砖墙面与地面严重脱色发白发灰近单色灰度（E2-L3），角落带有暗黄灰偏色（D-L1, F-L2）。"
    },
    2102: {
        "score": None,
        "severities": {"E2": "L2", "F": "L1"},
        "descriptions": {
            "E2": "果蔬货架上陈列的绿叶蔬菜、胡萝卜与洋葱大面积欠饱和褪色发白。",
            "F": "脱色导致新鲜蔬果显得干瘪灰暗，削弱了生鲜超市的真实感。"
        },
        "note": "果蔬货架上陈列的绿叶蔬菜、胡萝卜与洋葱大面积欠饱和褪色发白（E2-L2, F-L1）。"
    },
    2137: {
        "score": None,
        "severities": {"E2": "L1", "D": "L1"},
        "descriptions": {
            "E2": "客厅电视机液晶屏幕上正在播放的卡通游戏画面色彩欠饱和发白，对比度不足。",
            "D": "背景红砖墙与木质书架略带暗灰偏色。"
        },
        "note": "客厅电视屏幕卡通游戏画面色彩欠饱和发白，背景红砖墙略带暗灰偏色（E2-L1, D-L1）。"
    },
    2141: {
        "score": None,
        "severities": {"D": "L1"},
        "descriptions": {
            "D": "机场候机大厅背景墙面与旅客浅色服饰轻微偏冷青蓝调。"
        },
        "note": "机场候机大厅背景墙面与旅客浅色服饰轻微偏冷青蓝调（D-L1）。"
    },
    2147: {
        "score": None,
        "severities": {"D": "L1"},
        "descriptions": {
            "D": "砧板上涂抹草莓果酱的吐司切片与金属黄油刀轻微偏冷青蓝调。"
        },
        "note": "砧板上涂抹草莓果酱的吐司切片与黄油刀轻微偏冷青蓝调（D-L1）。"
    },
    2156: {
        "score": None,
        "severities": {"E2": "L2", "D": "L1"},
        "descriptions": {
            "E2": "公园林荫道两侧茂密的行道树绿荫大面积褪色发灰，缺少生机。",
            "D": "漫步市民的衣服与沥青路面微偏黄褐色调。"
        },
        "note": "公园林荫道行道树绿荫大面积褪色发灰，市民服饰与路面微偏黄褐调（E2-L2, D-L1）。"
    },
    2163: {
        "score": None,
        "severities": {"D": "L2", "E2": "L1", "F": "L1"},
        "descriptions": {
            "D": "白色博美犬趴着的紫色毛绒狗窝周围木地板与墙角被错染为不自然的粉紫色偏色。",
            "E2": "右侧鲜红色皮质沙发大面积欠饱和暗淡。",
            "F": "木地板粉紫杂色使地面呈现污损般的虚假感。"
        },
        "note": "紫色毛绒狗窝周围木地板被错染为粉紫色偏色，右侧鲜红色沙发欠饱和暗淡（D-L2, E2-L1, F-L1）。"
    },
    2171: {
        "score": None,
        "severities": {"E2": "L2", "D": "L1"},
        "descriptions": {
            "E2": "街角商铺的红砖外墙、橱窗遮阳篷与停放车辆大面积欠饱和泛灰。",
            "D": "人行道路面与天空微带冷青灰偏色。"
        },
        "note": "街角商铺红砖外墙与遮阳篷大面积欠饱和泛灰，路面微偏冷青灰（E2-L2, D-L1）。"
    },
    2183: {
        "score": None,
        "severities": {"D": "L1"},
        "descriptions": {
            "D": "室内客厅燃木壁炉的砖石护壁与地毯轻微偏暖红黄调。"
        },
        "note": "客厅燃木壁炉砖石护壁轻微偏暖红黄调（D-L1）。"
    },
    2190: {
        "score": None,
        "severities": {"E2": "L2", "D": "L1"},
        "descriptions": {
            "E2": "白色餐盘中摆放的烤鸡原本金黄焦脆的表皮大面积褪色暗淡发灰。",
            "D": "餐盘边沿与周围暗部微带冷灰偏色。"
        },
        "note": "餐盘中烤鸡金黄焦脆表皮大面积褪色暗淡发灰，缺乏诱人色泽（E2-L2, D-L1）。"
    },
    2192: {
        "score": None,
        "severities": {"E2": "L2", "F": "L1"},
        "descriptions": {
            "E2": "棒球运动场看台观众席与外野草坪大面积欠饱和褪色发灰，层次平淡。",
            "F": "灰淡无色的背景看台与场上活跃球员之间色彩对比不够生动协调。"
        },
        "note": "棒球运动场看台观众席与外野草坪大面积欠饱和褪色发灰（E2-L2, F-L1）。"
    },
    2204: {
        "score": None,
        "severities": {"E1": "L2", "D": "L1", "F": "L1"},
        "descriptions": {
            "E1": "木质早餐桌上的圆形甜瓜表皮呈现过度浓艳刺眼的荧光橙红色，饱和度严重超标。",
            "D": "玻璃茶杯内红茶色泽偏冷淡偏紫红。",
            "F": "甜瓜强烈的荧光质感与自然水果表皮不符，呈现明显人工塑料感。"
        },
        "note": "木质早餐桌上的甜瓜表皮呈现过度浓艳刺眼的荧光橙红色，茶水偏冷淡（E1-L2, D-L1, F-L1）。"
    },
    2206: {
        "score": None,
        "severities": {"D": "L2", "E1": "L2", "F": "L1"},
        "descriptions": {
            "D": "窗台摆放的花瓶插花枝叶与木质台面受到窗外强烈偏黄绿暖色眩光侵染。",
            "E1": "高光照射下的绿叶与窗框边缘饱和度偏高浓艳。",
            "F": "刺眼的黄绿光晕削弱了窗台采光的柔和自然感。"
        },
        "note": "窗台摆放的花瓶插花枝叶与台面受到窗外强烈黄绿暖色眩光侵染（D-L2, E1-L2, F-L1）。"
    },
    2213: {
        "score": None,
        "severities": {"E2": "L2", "D": "L1"},
        "descriptions": {
            "E2": "海滨沙滩原本金黄细腻的沙地与湛蓝海浪大面积暗淡褪色泛灰。",
            "D": "海滩整体色温略带青灰冷调。"
        },
        "note": "海滨沙滩金黄沙地与湛蓝海浪大面积暗淡褪色泛灰，色温偏青冷（E2-L2, D-L1）。"
    },
    2224: {
        "score": None,
        "severities": {"D": "L2", "F": "L1"},
        "descriptions": {
            "D": "特写男子脸部肤色与棒球帽边缘受到不自然的橙黄偏色侵染。",
            "F": "面部阴影过渡生硬且泛黄，降低了人像皮肤质感的真实度。"
        },
        "note": "特写男子脸部肤色与棒球帽边缘受到不自然的橙黄偏色侵染，阴影泛黄生硬（D-L2, F-L1）。"
    },
    2227: {
        "score": None,
        "severities": {"D": "L1"},
        "descriptions": {
            "D": "雪山缆车旁滑雪者的鲜艳滑雪服与雪地背阴处轻微偏暖红调。"
        },
        "note": "雪山缆车旁滑雪服与雪地背阴处轻微偏暖红调（D-L1）。"
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
    print(f"=== 开始注入 Batch 10 剩余 {len(GROUNDING_B10_PART2)} 个任务 ===")
    
    # 1. 更新 grounding_remaining_batch_10.json
    g10_path = 'LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_10.json'
    with open(g10_path, 'r', encoding='utf-8') as f:
        g10_data = json.load(f)
        
    for tid, fix in GROUNDING_B10_PART2.items():
        tid_str = str(tid)
        defects_list = []
        for did, sev in fix["severities"].items():
            defects_list.append({
                "id": did,
                "name": DEFECT_NAMES[did],
                "severity": sev,
                "description": fix["descriptions"][did]
            })
        g10_data[tid_str] = {
            "task_idx": tid,
            "score": fix["score"],
            "defects": defects_list,
            "note": fix["note"]
        }
    with open(g10_path, 'w', encoding='utf-8') as f:
        json.dump(g10_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] 已更新 {g10_path}")
    
    # 2. 更新 all.json
    all_path = 'LS_lcad_reviewer/exports/reviewed_1_10000_all.json'
    with open(all_path, 'r', encoding='utf-8') as f:
        all_data = json.load(f)
    anno_by_tid = {a['human_review']['task_id']: a for a in all_data['annotations'] if a.get('human_review')}
    
    c = 0
    for tid, fix in GROUNDING_B10_PART2.items():
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
    for tid, fix in GROUNDING_B10_PART2.items():
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
    
    print("\nBatch 10 第二批严格重审注入成功！")

if __name__ == '__main__':
    main()
