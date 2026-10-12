"""Apply Double Check updates for batch 5501-6000 pass tasks.
Updates reviewed_5501_6000, stream package, and full 1-10000 exports.
Follows the exact V4 schema contract from AGENTS.md.
"""
import json
import os
import shutil
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"
STREAMS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "streams"

# 23 Grounded Double Check Corrections for 5501-6000
DC_CORRECTIONS = {
    5806: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "雪地捕手与喂鸭男子身旁原本清冽浅色的河水在LCAD生成图中严重浑浊发黄，恶性错涂为深褐色与泥土黄河水"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "右侧雪人底座与周围泥土略微泛暗发黄"}
        ],
        "review_note": "Double Check复核改判：核查发现：雪地喂鸭男子身旁清冽浅色河水在LCAD中严重浑浊发黄，恶性错涂为深褐泥土黄河水，改判错色(C-L2)与偏色(D-L1)。"
    },
    5853: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "桥下滑板少年全图严重欠饱和脱色(R_sat=0.26)，GT中石桥栏杆、绿植与河流水面色彩饱满，LCAD生成图大面积灰暗失色退化为接近黑白"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "滑板少年红色短袖与黄色防护栏颜色暗淡褪色，色相明显发乌"}
        ],
        "review_note": "Double Check复核改判：核查发现：桥下滑板少年整体严重欠饱和脱色(R_sat=0.26)，石桥与水面大面积灰暗失色，少年红衣发乌，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    5597: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "办公室电脑书桌GT原本温馨的暖黄台灯照明与米黄色墙壁，在LCAD生成图中墙面明显泛冷发青发灰，色温发生显著偏差"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "书架上的书籍与桌面笔记本外壳色彩欠饱和发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：办公室电脑书桌原本温馨暖黄台灯照明与米黄墙壁被错涂为泛冷发青发灰冷调，改判偏色(D-L2)与欠饱和(E2-L1)。"
    },
    5607: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "牧场前景棕褐色母牛温暖毛色在LCAD生成图中泛冷发暗，远景山坡与草地整体偏灰偏冷，失去秋季牧场金黄温暖色调"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "母牛皮毛原本饱满的红褐光泽脱色发乌"}
        ],
        "review_note": "Double Check复核改判：核查发现：牧场棕褐色母牛温暖毛色与远景草地泛冷发暗发灰，母牛皮毛红褐色泽脱色，改判偏色(D-L2)与欠饱和(E2-L1)。"
    },
    5619: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "网球场红土球场原本鲜艳温暖的砖红橙色地面，在LCAD生成图中被恶性错涂为暗沉发灰褐的冷泥土色，红土地质感严重失真"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "两位小女孩的粉红色上衣脱色发暗，饱和度明显不足"}
        ],
        "review_note": "Double Check复核改判：核查发现：网球红土球场温暖砖红橙色地面被错涂为暗沉发灰褐色，小女孩粉红上衣脱色发暗，改判错色(C-L2)与欠饱和(E2-L1)。"
    },
    5875: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "非洲草原晴朗蔚蓝天空在LCAD生成图中整体偏暗偏灰，天际线被冷灰阴霾覆盖"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "前景树冠与长颈鹿活动的灌木丛原本生机绿意发暗发灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：非洲草原蔚蓝晴空与天际线发暗泛灰，灌木树林绿色欠饱和发乌，改判偏色(D-L1)与欠饱和(E2-L1)。"
    },
    5915: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "赛马场夕阳暖光沐浴下的多名骑手鲜艳蓝黑制服与骏马棕红毛色，在LCAD生成图中大面积脱色发灰发暗，色彩鲜活度严重折损"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "沙滩赛道原本温暖金黄的夕阳余晖明显偏灰偏冷"}
        ],
        "review_note": "Double Check复核改判：核查发现：海滩赛马场骑手制服鲜艳蓝色与骏马棕红毛发大面积脱色发暗发灰，沙滩夕阳光偏冷，改判欠饱和(E2-L2)与偏色(D-L1)。"
    },
    5925: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "卧室大床上原本质感清晰的冷灰黑色被子与冷灰枕头，在LCAD生成图中被严重烘烤发黄变暖，恶性错涂为泛脏黄暖褐色被褥"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "深灰被罩色相严重漂移为土黄暖褐色"}
        ],
        "review_note": "Double Check复核改判：核查发现：卧室冷灰黑被子与枕头被严重烘烤发黄变暖，恶性错涂为泛脏黄暖褐色被褥，改判偏色(D-L2)与错色(C-L1)。"
    },
    5951: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "雪地公路上除雪作业人员身上穿戴的高可见度荧光黄色反光背心，在LCAD生成图中严重脱色蜕白发暗，警示黄色几乎完全褪色消失"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "右侧油罐车原本橙黄鲜艳罐体颜色发暗失色"}
        ],
        "review_note": "Double Check复核改判：核查发现：雪地除雪作业人员原本高可见度荧光黄色反光背心严重脱色蜕白发暗，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    5987: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "医院急救室原本鲜艳翠绿色的病床护栏与输液架，在LCAD生成图中被恶性错涂为发暗阴冷的灰褐色与脏污死灰色"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "病房内红色床垫靠背与蓝色屏风严重脱色蜕淡，医护环境色彩被大面积抹杀"}
        ],
        "review_note": "Double Check复核改判：核查发现：急救室翠绿色病床护栏被错涂为阴暗灰褐色，红色床垫靠背与蓝色屏风严重脱色，改判错色(C-L2)与欠饱和(E2-L2)。"
    },
    5663: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "墨西哥卷饼餐盘中炸薯条金黄酥脆的色泽在LCAD生成图中偏深发暗发焦，鳄梨色拉酱原本清新的鲜绿色严重偏暗偏褐"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "卷饼内部红番茄肉馅色彩脱色发暗，食物可口诱人度显著降低"}
        ],
        "review_note": "Double Check复核改判：核查发现：墨西哥卷饼炸薯条与鳄梨酱严重发焦发暗发褐，番茄肉馅脱色，食物色泽受损，改判偏色(D-L2)与欠饱和(E2-L1)。"
    },
    5779: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "海滩男子手中展开的彩色风筝上原本鲜艳纯正的洋红粉紫与明黄色拼接色块，在LCAD生成图中大面积脱色蜕变发暗灰粉色与枯黄色"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "远景蔚蓝清澈的海水被涂抹为暗沉发灰绿的浑浊海面"}
        ],
        "review_note": "Double Check复核改判：核查发现：海滩彩色风筝鲜艳洋红与明黄拼块严重脱色发暗，背景蔚蓝海水偏暗灰绿，改判错色(C-L2)与偏色(D-L1)。"
    },
    5892: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "公园老人身穿的原本极其鲜亮明艳的蓝紫色花衬衫，在LCAD生成图中被严重剥夺色彩，蜕变为几乎全灰黑白、仅残留极微弱色渍的灰暗印花衫"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "花衬衫领口与胸前原本饱和的紫红花瓣发生严重脱色错相"}
        ],
        "review_note": "Double Check复核改判：核查发现：公园老人身上极明艳的蓝紫色花衬衫被严重剥夺色彩，大面积退化为黑白灰暗印花衫(R_sat=0.55)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    5734: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "花瓶中盛开的鲜红色玫瑰与菊花原本花瓣饱满欲滴，在LCAD生成图中花瓣红色严重脱色发乌发深，蜕变为干枯暗焦红褐色"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白瓷花瓶与桌面原本干净的浅色调被轻微烘烤泛暖黄"}
        ],
        "review_note": "Double Check复核改判：核查发现：花瓶中鲜红玫瑰与菊花花瓣严重脱色发乌蜕变为干枯暗焦红褐，白瓷花瓶泛暖黄，改判欠饱和(E2-L2)与偏色(D-L1)。"
    },
    5606: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "电脑工作台周围环境在GT中为温馨柔和的暖黄台灯与原木橱柜，在LCAD生成图中整体被恶性错涂为阴冷刺目的紫蓝冷色调，色温严重颠倒"},
            {"id": "B", "name": "溢色", "severity": "L1", "description": "笔记本电脑液晶屏幕发出的蓝白荧光越界扩散侵染到键盘与桌面"}
        ],
        "review_note": "Double Check复核改判：核查发现：电脑桌暖黄台灯与原木橱柜被恶性错涂为阴冷刺目紫蓝调，屏幕荧光越界溢色，改判偏色(D-L2)与溢色(B-L1)。"
    },
    5914: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "街角垃圾箱旁遗弃的鲜艳纯正天蓝色毛绒泰迪熊，在LCAD生成图中被恶性错涂为深暗沉郁的暗紫蓝色与发脏蓝紫伪色，熊身色相显著偏离"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "泰迪熊胸前黄色装饰花朵脱色发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：街头天蓝色毛绒泰迪熊被恶性错涂为暗沉发脏深蓝紫伪色，胸前黄花脱色，改判错色(C-L2)与欠饱和(E2-L1)。"
    },
    5964: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "原野长颈鹿背景后方原本生机盎然的翠绿树林与开阔草地，在LCAD生成图中被恶性错涂为枯槁焦黑的深暗红褐树冠与发灰天际线"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "全图草木植被大面积泛暗泛焦褐，自然野外生态色彩完全丧失"}
        ],
        "review_note": "Double Check复核改判：核查发现：长颈鹿背景后方生机翠绿树林被恶性错涂为枯槁焦黑的深暗红褐树冠，全图植被发焦，改判错色(C-L2)与偏色(D-L2)。"
    },
    5530: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "年轻男子身后原本鲜艳醒目的粉红色/洋红色室内艺术装饰背景墙面，在LCAD生成图中被恶性错涂为发暗阴冷的灰紫泥土色墙面，主色调严重偏差"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "蓝色行李箱拉杆与周围衣物色彩饱和度偏低发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：室内男子背后鲜艳粉红洋红色背景装饰墙被恶性错涂为发暗阴冷灰紫泥色，改判错色(C-L2)与欠饱和(E2-L1)。"
    },
    5574: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "火车车厢窗外铁路轨道两侧原本生机浓郁的翠绿色防护林与草地，在LCAD生成图中大面积严重枯化焦化，被恶性错涂为发暗枯焦的黄褐色荒草树木"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "窗外风景整体色温严重偏发焦暖黄褐"}
        ],
        "review_note": "Double Check复核改判：核查发现：铁路轨道两侧生机翠绿防护林被恶性错涂为枯焦发暗黄褐荒木，草地严重焦化，改判错色(C-L2)与偏色(D-L1)。"
    },
    5756: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "温馨双人卧室中靠窗原本温暖金黄/浅驼色的床单与毛毯，在LCAD生成图中被恶性错涂为阴暗死冷、发乌深灰褐色的旧毯子，卧室内温馨感丧失"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "卧室木质家具与暖黄灯光整体泛暗泛青冷，色温失真"}
        ],
        "review_note": "Double Check复核改判：核查发现：双人卧室原本温暖金黄浅驼色床单被恶性错涂为阴暗死灰褐色旧毯，室内暖光泛暗泛冷，改判错色(C-L2)与偏色(D-L2)。"
    },
    5917: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "草原野外原本通体为温暖红褐色、金棕色皮毛的野外灰熊，在LCAD生成图中头部与背部皮毛被恶性错涂为阴暗死黑、发青灰黑色的冷色皮毛，棕熊特有暖褐色完全失真"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "周围草地整体偏冷发灰，缺乏高寒草原阳光沐浴感"}
        ],
        "review_note": "Double Check复核改判：核查发现：野外棕褐色皮毛灰熊在LCAD中被恶性错涂为阴冷死黑、发青灰黑色冷色皮毛，熊毛色相严重失真，改判错色(C-L2)与偏色(D-L1)。"
    },
    5926: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "草场上吃草的原本毛色对比极其鲜明的棕白花斑小马与母马，在LCAD生成图中棕红皮毛被恶性错涂为发暗死灰、深青黑褐色的脏污马身，毛色光泽被剥夺"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "背景树林原本纯净的绿色欠饱和发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：草场棕白花斑骏马鲜艳棕红皮毛被恶性错涂为发暗死灰深青黑褐色脏污毛色，改判错色(C-L2)与欠饱和(E2-L1)。"
    },
    5969: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "公共卫生间洗手池周围原本干净温馨的暖白黄色瓷砖与暖色照明，在LCAD生成图中整体被恶性错涂为阴森冰冷、发青发蓝绿的冷灰调，色温严重颠倒(DeltaC=0.102)"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "洗手镜前灯光原本温暖的光晕褪淡发白，照明氛围严重破坏"}
        ],
        "review_note": "Double Check复核改判：核查发现：卫生间洗手池暖白黄瓷砖与暖色灯光整体被恶性错涂为阴森冰冷发青蓝绿调(DeltaC=0.102)，改判偏色(D-L2)与欠饱和(E2-L1)。"
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
    stream_path = STREAMS_DIR / "tasks_lcad_5501_6000_stream.json"
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
    print("Applying Double Check updates for 5501-6000...")
    
    # 1. Update batch 5501-6000
    b_path = EXPORTS_DIR / "reviewed_5501_6000_20260930_150135.json"
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

    print("Double check updates for 5501-6000 completed successfully!")

if __name__ == "__main__":
    main()
