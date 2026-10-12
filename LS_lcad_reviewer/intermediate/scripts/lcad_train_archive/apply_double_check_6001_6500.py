"""Apply Double Check updates for batch 6001-6500 pass tasks.
Updates reviewed_6001_6500, stream package, and full 1-10000 exports.
Follows the exact V4 schema contract from AGENTS.md.
"""
import json
import os
import shutil
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"
STREAMS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "streams"

# 22 Grounded Double Check Corrections for 6001-6500
DC_CORRECTIONS = {
    6005: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "长颈鹿伸出的长条粉红舌头在LCAD生成图中严重脱色褪白，退化为无血色的惨白灰白长条，肉质红润感完全丧失"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "长颈鹿舌尖局部略带发暗灰褐色污渍错色"}
        ],
        "review_note": "Double Check复核改判：核查发现：长颈鹿进食伸出的长条粉红舌头在LCAD中严重脱色褪白为无血色惨白灰条，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6018: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "停靠路边的三轮摩托车旁大树下草坪与湖水在LCAD生成图中被恶性错涂为发暗焦枯、干枯发黄的深黄褐色，草地与清澈水面失真"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "背景建筑与远景水泥地面整体泛暗泛黄"}
        ],
        "review_note": "Double Check复核改判：核查发现：停靠三轮摩托车旁大树下草坪与湖水被恶性错涂为暗焦枯黄褐色，改判错色(C-L2)与偏色(D-L1)。"
    },
    6031: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "道路左侧立式红绿灯亮起极鲜艳纯正的大红交通信号灯红光在LCAD生成图中严重脱色漂白为惨白灰白发亮圆圈，警示红光彻底丧失"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "边缘路牌与灯罩铁皮轻微泛灰发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：道路左侧红绿灯鲜艳大红交通信号灯红光彻底脱色发白为惨白圆圈，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6033: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "卫生间原本铺设的明亮纯正深宝蓝色防滑地砖在LCAD生成图中大面积泛紫发暗变深紫蓝冷色，地砖色彩严重失真"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "右侧卫生间隔板与金属门把手处略泛生硬发青冷光"}
        ],
        "review_note": "Double Check复核改判：核查发现：卫生间明亮鲜艳深宝蓝地面在LCAD中大面积泛紫发暗变深紫蓝冷色，隔板泛冷，改判偏色(D-L1)与过饱和(E1-L1)。"
    },
    6038: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "单板滑雪运动员横抱的滑雪板背面原本鲜艳夺目的洋红色与紫红色潮酷花纹在LCAD生成图中严重脱色发暗，退化为灰暗发黑、脏污死灰的无色图案"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "滑雪板边缘与板尾轻微偏黄暗淡"}
        ],
        "review_note": "Double Check复核改判：核查发现：单板滑雪运动员手中单板滑雪板原本鲜艳亮丽的紫色/洋红色花纹严重脱色变暗黑灰，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6044: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "公路上红色重型摩托车前挡风车脸与骑手穿戴的红白相间骑行服红色部件在LCAD生成图中严重脱色为发暗发脏的暗褐土灰色，鲜红质感完全丧失"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "摩托车前轮减震器与金属构件错涂发暗土黄褐"}
        ],
        "review_note": "Double Check复核改判：核查发现：公路上红色重型摩托车前脸与红白骑行服在LCAD中严重脱色为发暗发脏的暗褐土灰色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6053: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "消防车接口处接出的粗大高压消防水带原本具有醒目纯正的鲜黄色，在LCAD生成图中严重脱色发暗，退化为浅土黄暗白灰，警示饱和度大幅衰退"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "路面阴影与消火栓基座发乌偏灰偏冷"}
        ],
        "review_note": "Double Check复核改判：核查发现：消防车接出的粗大明黄色消防水带与消火栓接口严重脱色发暗，黄色鲜艳度大幅衰退，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6069: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "游艇甲板上小男孩手提鲜艳纯正的紫红色/洋红色塑料购物手提袋在LCAD生成图中严重脱色为发乌暗棕褐色与脏泥土色，塑料袋色相质感严重受损"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "甲板木质纹理与船舷反光局部泛冷发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：游艇甲板上小男孩手提鲜艳紫红/洋红色塑料购物袋严重脱色为发乌暗棕褐色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6073: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "沙滩边大型遮阳伞伞面上鲜艳纯正的明黄色拼块在LCAD生成图中完全脱色褪白为纯灰白色帆布，鲜黄色完全脱失"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "遮阳伞伞骨在沙滩上的阴影局部泛冷发灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：沙滩边太阳伞鲜艳明黄色拼块完全脱色褪白为纯灰白色帆布，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6092: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "电脑显示器旁木质书桌上摆放的鲜艳荧光黄色橡皮小鸭与粉红玩具在LCAD生成图中脱色发灰发暗，色彩鲜活度受损"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "木质桌面与背景墙壁在暗光下局部泛冷发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：电脑显示器旁木质书桌上黄色荧光小鸭与粉红玩具脱色发灰发暗，桌面泛冷，改判欠饱和(E2-L1)与偏色(D-L1)。"
    },
    6094: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "户外草坪飞盘运动员身穿原本鲜艳纯正的草绿色短袖与天蓝色短袖T恤在LCAD生成图中严重脱色发暗，退化为灰暗无生气的浅白灰冷色汗衫"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "飞盘原本明亮的橙黄色局部色相发乌"}
        ],
        "review_note": "Double Check复核改判：核查发现：飞盘运动员身穿的鲜艳草绿色与天蓝色运动T恤严重脱色发暗，蜕变为灰暗浅白汗衫，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6144: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "足球场上运动员脚下踩着的纯正鲜明黄色足球在LCAD生成图中脱色发暗，表面呈现发脏的浅灰黄色与暗灰污渍"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "草坪局部光照处色相略微泛黄"}
        ],
        "review_note": "Double Check复核改判：核查发现：足球运动员脚下踩着的纯鲜黄色足球在LCAD中脱色发暗，表面呈现灰黄污渍，改判欠饱和(E2-L1)与错色(C-L1)。"
    },
    6172: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "绿草坪上立着的鲜亮纯正天蓝色冲浪板在LCAD生成图中表面与边缘明显泛青绿偏色，色相向湖绿漂移"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "下方草坪受阴影影响局部发焦发暗发灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：草地上立着的鲜亮天蓝色冲浪板在LCAD中边缘泛青绿偏色，草坪色彩发乌，改判偏色(D-L1)与错色(C-L1)。"
    },
    6206: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "操场上平整鲜亮翠绿色的塑胶/草地跑道地面在LCAD生成图中被恶性错涂为冷青灰色水泥硬地，草绿生机完全丧失"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "棒球手套暖橙色皮质脱色发暗，色彩欠饱满"}
        ],
        "review_note": "Double Check复核改判：核查发现：操场塑胶跑道原本鲜亮翠绿色地面被恶性错涂为冷青灰色硬地，棒球手套暖橙色发乌，改判错色(C-L2)与欠饱和(E2-L1)。"
    },
    6211: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "动物园水池边母熊与两只幼熊原本温暖纯正的棕红/红褐色皮毛在LCAD生成图中被恶性错涂为阴暗死灰、深青黑发冷的脏污毛色，皮毛暖感被剥夺"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "水泥台面与水池暗部略微泛冷发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：动物园水泥池中两只棕色幼熊与母熊温暖红褐色皮毛被恶性错涂为阴暗死灰黑冷毛色，改判错色(C-L2)与偏色(D-L1)。"
    },
    6222: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "海浪中冲浪者身穿高可见度的鲜艳亮橙红色冲浪服在LCAD生成图中严重脱色发暗，蜕变为黑灰深暗棕色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "浪花泡沫阴影处轻微泛黄发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：海中冲浪者身穿的鲜艳亮橙红色冲浪服严重脱色发暗蜕变为黑灰暗棕色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6274: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "新鲜热狗面包上方挤着的新鲜鲜红番茄酱与金黄芥末酱在LCAD生成图中严重脱色发乌发暗，退化为深褐暗红与脏土灰色，食品食欲感严重受损"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "面包金黄表皮略带发暗灰斑"}
        ],
        "review_note": "Double Check复核改判：核查发现：热狗上方挤着的鲜红番茄酱与金黄芥末酱严重脱色发乌发暗，失去新鲜食欲感，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6282: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "海滩上空飘扬的大型鲜艳正红色章鱼造型风筝在LCAD生成图中头部与飘带大红色严重脱色发乌，蜕变为暗紫褐色与脏暗灰红色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "蓝天天际线局部受风筝边缘影响轻微泛暗发灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：海滩上空飞翔的大型鲜红色章鱼风筝在LCAD中尾部与头部红色严重脱色发乌为暗紫褐色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6374: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "卫生间墙面铺设极其浓郁鲜艳的洋红粉紫色复古瓷砖在LCAD生成图中被恶性错涂为脏污红褐色与水泥灰黄杂色，瓷砖色相完全失真"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "白色浴帘与洗手台阴影泛发暗脏泥土色，整体空间色温严重失衡"}
        ],
        "review_note": "Double Check复核改判：核查发现：卫生间原本极其浓郁鲜艳的洋红粉紫瓷砖墙面被恶性错涂为脏污红褐色与灰泥色，浴帘发乌，改判错色(C-L2)与偏色(D-L2)。"
    },
    6433: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "原野草地上飞盘高尔夫铁架篮链条上绑着的鲜艳粉红色靶标识别布条在LCAD生成图中严重脱色褪淡发暗，退化为无色灰白"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "远山与树冠天际线略微泛发焦黄褐色"}
        ],
        "review_note": "Double Check复核改判：核查发现：草原上飞盘铁架篮上系着的鲜艳粉红色靶标布条严重脱色发暗，远山天际线泛发焦黄褐，改判欠饱和(E2-L1)与偏色(D-L1)。"
    },
    6462: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "城市街头可口可乐涂装双层观光巴士车身大面积极其鲜艳抢眼的正红色在LCAD生成图中严重脱色为发暗发脏的紫暗红色与深褐灰红"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "车窗与车顶反光处局部泛暗发灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：可口可乐双层红色旅游巴士车身极其鲜艳的正红色严重脱色为发暗发脏的紫暗红色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6500: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "打电话青年身穿的带有清新草绿色格纹连帽休闲开衫外衣在LCAD生成图中被恶性错涂为冷蓝紫灰、发暗牛仔布蓝灰色，绿色格纹被彻底篡改剥夺"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "背景室内墙面轻微泛冷偏蓝灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：打电话青年身穿的原本带有草绿格纹连帽开衫被恶性错涂为冷蓝紫灰牛仔布色，色相严重错移，改判错色(C-L2)与偏色(D-L1)。"
    }
}

def update_export_file(file_path: Path, is_clean: bool = False):
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
    stream_path = STREAMS_DIR / "tasks_lcad_6001_6500_stream.json"
    if not stream_path.exists():
        print(f"Stream file not found: {stream_path}")
        return
    with open(stream_path, "r", encoding="utf-8") as f:
        stream_data = json.load(f)

    updated_cnt = 0
    for item in stream_data:
        t_id = item["data"].get("task_idx")
        if t_id in DC_CORRECTIONS:
            c = DC_CORRECTIONS[t_id]
            item["data"]["review_tag"] = "洛熙视觉改判"
            item["data"]["review_note"] = c["review_note"]
            item["data"]["review_status"] = "已核验"
            if "original_record" in item["data"] and "comparison" in item["data"]["original_record"]:
                item["data"]["original_record"]["comparison"]["defects"] = c["defects"]
            elif "original_record" in item["data"]:
                item["data"]["original_record"]["defects"] = c["defects"]
            updated_cnt += 1

    with open(stream_path, "w", encoding="utf-8") as f:
        json.dump(stream_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {updated_cnt} tasks in stream package {stream_path.name}")

def main():
    print("Applying Double Check updates for 6001-6500...")
    
    # 1. Update batch 6001-6500
    b_path = EXPORTS_DIR / "reviewed_6001_6500_20260930_153605.json"
    backup = b_path.with_name(b_path.stem + "_backup_predc.json")
    if not backup.exists() and b_path.exists():
        shutil.copy2(b_path, backup)
        print(f"Backup created: {backup.name}")
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

    print("Double check updates for 6001-6500 completed successfully!")

if __name__ == "__main__":
    main()
