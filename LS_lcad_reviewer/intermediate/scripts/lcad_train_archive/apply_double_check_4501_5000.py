"""Apply Double Check updates for batch 4501-5000 pass tasks.
Updates reviewed_4501_5000, stream package, and full 1-10000 exports.
"""
import json
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"
STREAMS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "streams"

# 19 Grounded Double Check Corrections
DC_CORRECTIONS = {
    4557: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "铁轨上内燃机车原本鲜艳亮丽的深宝蓝色车身与明黄色车头驾驶室，在LCAD生成图中被恶性错涂为阴暗死灰、深炭灰黑色的单色铁皮车身，整车严重错色"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "机车整体工业涂装色彩被严重剥夺，前脸警示黄色欠饱和脱色发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：铁轨上内燃机车鲜艳深宝蓝车身与明黄驾驶室被恶性错涂为阴暗深炭灰黑色铁皮车身，整车严重错色(C-L2)且局部欠饱和(E2-L1)。"
    },
    4597: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "海滩滑板男子身后沙滩背景上立着的亮橙红色交通路锥（雪糕筒），在LCAD生成图中色彩被严重剥夺，彻底脱色褪白为浅土灰白色，鲜艳警示度完全丧失"}
        ],
        "review_note": "Double Check复核改判：核查发现：沙滩背景上的亮橙红色交通路锥(雪糕筒)严重脱色褪白为浅土灰白色(RedLoss=0.86)，改判欠饱和(E2-L2)。"
    },
    4885: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "轻轨铁轨两侧平展的生机草地与背景树林，在LCAD生成图中大面积严重枯槁焦化，原本清脆的草绿色被恶性错涂为一片发暗发焦的锈红黄褐色铁锈调"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "铁轨沿线自然植被环境明显偏发暗铁锈红黄调，整体色相发生严重偏差"}
        ],
        "review_note": "Double Check复核改判：核查发现：轻轨铁轨两侧草地与背景树林生机苍翠绿色被严重焦化，恶性错涂为发暗锈红黄褐色铁锈调(DeltaC=0.103)，改判错色(C-L2)与偏色(D-L2)。"
    },
    4897: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "客厅花伞下方木地板暗处原本纯正鲜艳的红色地毯垫子与红花装饰，在LCAD生成图中红色被严重剥夺发乌，退化蜕变为暗黑灰泥色"}
        ],
        "review_note": "Double Check复核改判：核查发现：客厅花伞下木地板暗处纯正红色地毯垫子与红花脱色发乌为暗黑灰泥色(RedLoss=0.94)，改判欠饱和(E2-L2)。"
    },
    4991: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "公园长椅旁小男孩手中高举的纯鲜艳明黄色塑料飞盘，在LCAD生成图中被恶性错涂为刺目浓艳的大红橙色塑料飞盘，与真值黄色发生严重色相偏差"}
        ],
        "review_note": "Double Check复核改判：核查发现：公园长椅旁小男孩手中鲜艳明黄色塑料飞盘被恶性错涂为刺目浓艳大红橙色，差分图高亮，改判错色(C-L2)。"
    },
    4528: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "室内打电话女士身穿的原本纯白色的针织开衫外套，在LCAD生成图中被大面积错涂为突兀发粉、荧光肉粉色的脏乱粉色衣服，与白色羊毛原色发生明显色偏错色"}
        ],
        "review_note": "Double Check复核改判：核查发现：打电话女士原本纯白针织开衫外套被大面积错涂为突兀发粉荧光肉粉色衣服，改判错色(C-L2)。"
    },
    4735: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "爬行婴儿面前纸箱上放着的鲜黄色柠檬，在LCAD生成图中被恶性错涂为深橙红色/红橙色柑橘（橘子），与鲜黄柠檬真值发生明确错色"}
        ],
        "review_note": "Double Check复核改判：核查发现：婴儿面前纸箱上的鲜黄色柠檬被恶性错涂为深橙红色/红橙色柑橘，改判错色(C-L2)。"
    },
    4518: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "薄底披萨表面的鲜红色意大利辣香肠片（辣肉肠）与红番茄酱底严重脱色发乌，退化蜕变为暗褐灰黑色，食欲感大幅降低"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "披萨配菜青椒丝与表面烤芝士颜色发暗偏灰，整体色调欠饱和发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：薄底披萨表面鲜红辣香肠片与番茄酱严重脱色发乌为暗褐灰黑(DeltaC=0.119, RedLoss=0.32)，改判欠饱和(E2-L2)与偏色(D-L1)。"
    },
    4642: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "青年男子背包上插着的滑板鲜红色滑板轮与支架配件在LCAD生成图中严重脱色蜕变为灰白色，男子右臂佩戴的鲜红色袖章亦脱色变浅发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：背包上的滑板鲜红滑板轮与配件脱色为灰白色(RedLoss=0.80)，手臂鲜红袖章脱色，改判欠饱和(E2-L2)。"
    },
    4541: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "卫生间左侧门上张贴的明黄色小心地滑三角形警告标牌与洗手台上的彩色洗手液瓶在LCAD生成图中被完全剥夺色彩，彻底退化为黑白灰暗单色标牌，警示色彩完全丧失"}
        ],
        "review_note": "Double Check复核改判：核查发现：卫生间门上明黄色小心地滑三角警告标牌与洗手台彩色洗手液严重脱色褪白为黑灰单色(RedLoss=1.0, R_sat=0.25)，改判欠饱和(E2-L2)。"
    },
    4651: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "快艇甲板内部平铺的翠绿色防滑地面在LCAD生成图中严重脱色蜕变为浅土灰褐色，且船头系缆处的鲜艳大红色球形防撞碰垫（气囊）彻底脱色发黑为深铁灰色"}
        ],
        "review_note": "Double Check复核改判：核查发现：快艇甲板翠绿防滑地面脱色为浅土灰褐，船头大红防撞碰垫脱色为深铁灰色(RedLoss=0.98)，改判欠饱和(E2-L2)。"
    },
    4816: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "滑板少年下半身身穿的鲜艳紫色运动长裤在LCAD生成图中严重脱色，退化蜕变为浅灰白色/暗灰色牛仔裤，下装鲜明色彩完全丧失"}
        ],
        "review_note": "Double Check复核改判：核查发现：滑板少年身穿的鲜艳紫色运动长裤严重脱色蜕变为浅灰白/暗灰长裤(RedLoss=0.85)，改判欠饱和(E2-L2)。"
    },
    4901: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "摩托车后视镜中倒映的鲜红色八角形 STOP 停车交通标志牌与机车车头鲜红色车标贴花在LCAD生成图中脱色发乌为暗土褐灰色，警示红完全失效"}
        ],
        "review_note": "Double Check复核改判：核查发现：摩托车后视镜中倒映的鲜红八角形STOP停车标志牌与车头红标脱色为暗土褐灰(RedLoss=1.0)，改判欠饱和(E2-L2)。"
    },
    4981: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "前院黄色消防栓旁草坪上倒放的亮粉红色儿童自行车车架与背景洋红色大门在LCAD生成图中严重脱色为浅灰白与暗土褐泥色，鲜艳涂装严重褪白"}
        ],
        "review_note": "Double Check复核改判：核查发现：草坪上亮粉红色儿童自行车车架与洋红色大门严重脱色为浅灰白与暗土褐(RedLoss=0.71)，改判欠饱和(E2-L2)。"
    },
    4533: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "草地上连帽衫男子手中持有的亮天蓝色塑料飞盘在LCAD生成图中严重脱色发乌，蜕变为暗灰青色；男子深蓝连帽卫衣色彩亦稍显发乌沉闷"}
        ],
        "review_note": "Double Check复核改判：核查发现：连帽衫男子手中天蓝色塑料飞盘脱色发乌为暗灰青色，改判欠饱和(E2-L2)。"
    },
    4670: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "公路护栏旁立着的白底红圈禁止调头交通指示牌（红色圆形边框与红斜杠）在LCAD生成图中严重脱色褪白为灰褐色暗白线条，禁令交通标识特征被破坏"}
        ],
        "review_note": "Double Check复核改判：核查发现：公路护栏旁禁止调头交通指示牌的红圈红杠警示线条严重脱色为暗白灰褐(RedLoss=0.74)，改判欠饱和(E2-L2)。"
    },
    4717: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "木屋前接飞盘女子身穿的亮蓝色牛仔长袖衬衫在LCAD生成图中被恶性错涂为发乌的暗红褐色上衣，与真值亮蓝色发生严重相反色相偏移"}
        ],
        "review_note": "Double Check复核改判：核查发现：接飞盘女子身穿的亮蓝色牛仔长袖衬衫被恶性错涂为发乌暗红褐色上衣，差分图高亮，改判错色(C-L2)。"
    },
    4829: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "海滩抱冲浪板女子腋下夹着的原本鲜艳纯正的鲜红色冲浪板，在LCAD生成图中被恶性错涂为黄绿色/草绿色冲浪板，发生明显错相错色"}
        ],
        "review_note": "Double Check复核改判：核查发现：海滩女子腋下夹着的鲜红色冲浪板被恶性错涂为黄绿色/草绿色冲浪板(RedLoss=0.54)，改判错色(C-L2)。"
    },
    4867: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "机场候机大厅整齐排列的行李手手推车鲜红色塑料把手与第一辆推车上的红色行李箱在LCAD生成图中脱色发乌为暗灰色与深黑色，色彩大幅衰减"}
        ],
        "review_note": "Double Check复核改判：核查发现：机场行李手推车鲜红塑料把手与红色行李箱严重脱色发乌为暗灰与深黑(RedLoss=0.53)，改判欠饱和(E2-L2)。"
    }
}

def update_export_file(file_path, is_clean=False):
    if not file_path.exists():
        print(f"Skipping non-existent: {file_path}")
        return
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    updated_cnt = 0
    for ann in data["annotations"]:
        t_id = ann["human_review"]["task_id"]
        if t_id in DC_CORRECTIONS:
            c = DC_CORRECTIONS[t_id]
            ann["defects"] = c["defects"]
            ann["review_note"] = "" if is_clean else c["review_note"]
            ann["review_status"] = "已核验"
            ann["reviewed_score"] = None
            ann["needs_rescoring"] = True
            updated_cnt += 1

    if "meta" in data:
        # 严守契约：meta 只能有 exported_at, total_images, needs_rescoring，严禁额外字段
        extra_keys = [k for k in data["meta"] if k not in ("exported_at", "total_images", "needs_rescoring")]
        for k in extra_keys:
            del data["meta"][k]

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Updated {updated_cnt} tasks in {file_path.name}")

def update_stream_file():
    stream_path = STREAMS_DIR / "tasks_lcad_4501_5000_stream.json"
    if not stream_path.exists():
        print(f"Stream file not found: {stream_path}")
        return
    with open(stream_path, "r", encoding="utf-8") as f:
        stream_data = json.load(f)

    updated_cnt = 0
    for item in stream_data:
        t_id = item["data"]["task_idx"]
        if t_id in DC_CORRECTIONS:
            c = DC_CORRECTIONS[t_id]
            item["data"]["review_tag"] = "洛熙视觉改判"
            item["data"]["review_note"] = c["review_note"]
            item["data"]["original_record"]["defects"] = c["defects"]
            updated_cnt += 1

    with open(stream_path, "w", encoding="utf-8") as f:
        json.dump(stream_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {updated_cnt} tasks in stream package {stream_path.name}")

def main():
    print("Applying Double Check updates for 4501-5000...")
    # 1. Update batch 4501-5000
    b_path = EXPORTS_DIR / "reviewed_4501_5000_20260930_140753.json"
    update_export_file(b_path, is_clean=False)

    # 2. Update stream package
    update_stream_file()

    # 3. Update all 1-10000 files
    full_process_files = [
        EXPORTS_DIR / "reviewed_1_10000_20260930_200411.json",
        EXPORTS_DIR / "reviewed_1_10000_all.json"
    ]
    for p in full_process_files:
        update_export_file(p, is_clean=False)

    clean_files = [
        EXPORTS_DIR / "reviewed_1_10000_clean_20260930_202516.json",
        EXPORTS_DIR / "reviewed_1_10000_clean.json"
    ]
    for p in clean_files:
        update_export_file(p, is_clean=True)

    print("Double check updates for 4501-5000 completed successfully!")

if __name__ == "__main__":
    main()
