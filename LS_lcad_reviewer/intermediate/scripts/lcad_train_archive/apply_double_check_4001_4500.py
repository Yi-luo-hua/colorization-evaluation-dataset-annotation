"""Apply Double Check updates for batch 4001-4500 pass tasks.
Updates reviewed_4001_4500, stream package, and full 1-10000 exports.
"""
import json
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"
STREAMS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "streams"

# 15 Grounded Double Check Corrections
DC_CORRECTIONS = {
    4018: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "停机坪地勤行李牵引拖车原本鲜艳橙黄色车身被严重错涂为发暗阴绿铁锈灰绿伪色"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "画面整体明显偏草绿黄调，机械设施表面色阶严重漂移"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "客机机头防撞涂装与牵引车色彩严重欠饱和脱色发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：停机坪鲜艳橙黄行李牵引车严重错涂为阴绿铁锈灰绿(C-L2, D-L2偏草绿黄调)；机头涂装与车体明显欠饱和褪色(E2-L2)。"
    },
    4042: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "八角楼钟楼走廊栏杆与彩钢瓦大面积欠饱和褪色，原有淡天蓝色丢失蜕变为发暗灰白"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "画面整体轻微偏冷青蓝调，建筑顶部受损色阶微漂"}
        ],
        "review_note": "Double Check复核改判：核查发现：八角楼钟楼特色淡天蓝走廊栏杆与彩钢瓦严重欠饱和脱色为发暗灰白(E2-L2)；建筑整体轻微偏冷青蓝调(D-L1)。"
    },
    4051: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "餐桌左侧大碗鲜红欲滴的水果罐头被严重错涂为刺目荧光玫红洋紫伪色"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "水果罐头及餐盘区域明显偏洋红紫调，严重破坏食品真实质感"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "水果罐头洋红假色浓艳刺眼、高光溢出伪色色块"}
        ],
        "review_note": "Double Check复核改判：核查发现：餐桌左侧大碗鲜红水果罐头恶性错涂为刺目荧光玫红洋紫伪色(C-L2, D-L2偏洋红紫调, E1-L2)；破坏食品质感(F-L2)。"
    },
    4058: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "自行车青草翠绿色金属车架极其严重欠饱和脱色，原有鲜绿色彩完全丢失蜕变为冷铁灰"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "画面整体轻微偏冷青蓝调，车身阴影发乌"}
        ],
        "review_note": "Double Check复核改判：核查发现：自行车原本鲜艳的青草翠绿色金属车架严重欠饱和脱色为发暗铁灰(E2-L3)；全图轻微偏冷青蓝调(D-L1)。"
    },
    4128: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "厨房案板上原本金黄鲜亮的切半鲜柠檬被严重错涂为刺目青绿柠檬伪色"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "柠檬果肉与果皮明显偏草绿黄调，刨丝器手柄色彩异常"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "青柠檬与刨丝器塑料手柄荧光草绿过饱和"}
        ],
        "review_note": "Double Check复核改判：核查发现：厨房案板上金黄鲜柠檬严重错涂为刺目青绿柠檬伪色(C-L2, D-L2偏草绿黄调)；刨丝器手柄荧光草绿过饱和(E1-L1)。"
    },
    4192: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街头STOP标志牌鲜艳大红底面严重欠饱和褪色，色彩暗淡蜕变为发暗铁锈褐"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "画面整体轻微偏暖红黄调，路牌阴影偏暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：街头大号STOP标志牌鲜艳大红金属底面严重欠饱和褪色为发暗铁锈褐(E2-L2)；全图轻微偏暖红黄调(D-L1)。"
    },
    4220: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "足球场前景球员原本鲜亮夺目的金黄色球衣严重欠饱和脱色，色彩发灰发暗蜕变为土黄色"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "画面整体轻微偏草绿黄调，球场局部受损色阶微漂"}
        ],
        "review_note": "Double Check复核改判：核查发现：绿茵足球场球员原本鲜亮夺目的金黄色球衣严重欠饱和褪色为暗淡黄土灰(E2-L2)；轻微偏草绿黄调(D-L1)。"
    },
    4246: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "背景茂盛青翠的远景山峦被严重错涂为死寂阴冷的暗蓝灰岩石秃山伪色"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "湖面帆船原本鲜艳的橙红色风帆严重欠饱和脱色褪白为惨白灰影"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "画面整体明显偏冷青蓝调，水体与山体阴郁发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：湖面帆船鲜艳橙红风帆严重脱色褪白(E2-L2)；背景青翠远山被剥夺绿色错涂为死寂暗蓝灰(C-L2, D-L2偏冷青蓝调)。"
    },
    4264: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "室内半透明纯白卷帘窗户下半部分被大面积错涂为突兀的粉红暖橙色伪色斑块"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "卷帘窗户区域明显偏暖红黄调，透光白光被染色"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "窗面出现不自然的大面积粉橙色斑，破坏真实采光质感"}
        ],
        "review_note": "Double Check复核改判：核查发现：室内半透明纯白卷帘窗户下半部分大面积错涂为粉红暖橙色伪色斑块(C-L2, D-L2偏暖红黄调, F-L2)。"
    },
    4312: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "笔记本电脑屏幕原本色彩极其绚丽的霓虹彩图壁纸严重欠饱和脱色，色彩几近完全丧失蜕变为惨白灰蓝单色"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "屏幕与键盘区域轻微偏冷青蓝调"}
        ],
        "review_note": "Double Check复核改判：核查发现：笔记本电脑屏幕绚丽霓虹抽象壁纸被严重剥夺色彩脱色为惨白灰蓝单色(E2-L3)；整体轻微偏冷青蓝调(D-L1)。"
    },
    4353: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "海滩浅滩小狗嘴中叼着的原本鲜艳明亮的柠檬黄色网球被恶性错涂为刺目荧光翠绿色"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "网球表面明显偏草绿黄调，荧光假色突兀"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "网球荧光翠绿色过饱和刺目"}
        ],
        "review_note": "Double Check复核改判：核查发现：小狗嘴中鲜艳柠檬黄色网球被恶性错涂为刺目荧光翠绿色(C-L2, D-L2偏草绿黄调, E1-L1)。"
    },
    4373: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "女服务员腰间鲜亮金黄橙色围裙与配餐台沙拉食材严重欠饱和脱色，色彩发暗发脏蜕变为暗黄灰土色"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "服务员天蓝上衣发暗偏青，画面整体明显偏冷青蓝调"}
        ],
        "review_note": "Double Check复核改判：核查发现：女服务员鲜艳金黄橙色围裙严重脱色发脏变暗黄灰(E2-L2)；天蓝上衣明显偏冷青蓝调(D-L2)。"
    },
    4401: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "棒球场小击球手身穿的墨绿色短袖球衣与球帽被恶性错涂为阴暗深宝蓝色与冷灰伪色"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "球服与球帽明显偏冷青蓝调，原有墨绿质感丢失"}
        ],
        "review_note": "Double Check复核改判：核查发现：小击球手墨绿色短袖球衣与球帽被恶性错涂为阴暗深宝蓝与冷灰伪色(C-L2, D-L2偏冷青蓝调)。"
    },
    4402: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "河流原本清澈蔚蓝的水体被严重错涂为发暗浑浊的黄土泥浆水伪色"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "河流水面整体明显偏暖红黄调，与清澈蔚蓝原貌严重违背"},
            {"id": "B", "name": "溢色", "severity": "L1", "description": "大象腿部与河边岩石边缘渗色，泛起紫红色杂色光晕"}
        ],
        "review_note": "Double Check复核改判：核查发现：大象戏水清澈蔚蓝河水被严重错涂为浑浊黄土泥浆水(C-L3, D-L2偏暖红黄调)；水体岩石边缘轻微溢色(B-L1)。"
    },
    4429: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "标志性的伦敦双层巴士鲜艳大红色车身被灾难性错涂为发灰暗青蓝与灰绿色混杂的阴冷伪色"},
            {"id": "D", "name": "偏色", "severity": "L3", "description": "公交车身严重偏冷青蓝调，完全破坏英伦大红双层巴士经典色彩标识"}
        ],
        "review_note": "Double Check复核改判：核查发现：标志性伦敦鲜红双层巴士被恶性错涂为发灰暗青蓝与灰绿色混杂伪色(C-L3, D-L3偏冷青蓝调)。"
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
            updated_cnt += 1
            
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Updated {updated_cnt} tasks in {file_path.name}")

def update_stream_file():
    stream_path = STREAMS_DIR / "tasks_lcad_4001_4500_stream.json"
    if not stream_path.exists():
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
    print("Applying Double Check updates...")
    # 1. Update batch 4001-4500
    b_path = EXPORTS_DIR / "reviewed_4001_4500_20260930_135528.json"
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

    print("Double check updates completed successfully!")

if __name__ == "__main__":
    main()
