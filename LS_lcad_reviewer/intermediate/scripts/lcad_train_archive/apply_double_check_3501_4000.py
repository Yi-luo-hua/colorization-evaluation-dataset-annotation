import json
import shutil
from pathlib import Path
from datetime import datetime

EXPORTS_DIR = Path("exports")
STREAMS_DIR = Path("streams")

# 26 个精准 Double Check 改判样本字典
UPDATES = {
    3580: {
        "gpt_score": 3.70,
        "reviewed_score": 3.70,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "白色翻斗卡车后方装载的鲜艳大红色金属集装箱严重脱色褪白为暗粉灰铁皮色，红色彩度严重丢失。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "画面整体偏冷青蓝调，水泥路面与建筑呈现轻微冷灰偏移。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】局部均摊漏检修复：白色翻斗卡车后方装载的鲜艳大红金属集装箱严重脱色褪白为暗粉灰铁皮色，原评价仅笼统描述为车辆区域色彩层次不足并虚高打出4.55分，现精准定物并修正评分至3.70。"
    },
    3653: {
        "gpt_score": 3.60,
        "reviewed_score": 3.60,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "电脑桌前原本鲜艳纯正大红色的电脑椅靠垫与坐垫被严重剥夺红色，恶性错涂为阴暗发灰的青蓝黑单色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "除显示器蓝色外，电脑桌周边物品与室内背景饱和度偏低。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】严重隐蔽错色漏检修复：电脑桌前原本鲜艳纯正大红色的电脑椅靠垫与坐垫被彻底剥夺红色错涂为阴暗青蓝黑色，原评4.55分严重高估，现锁定大红电脑椅实体并修正评分至3.60。"
    },
    3754: {
        "gpt_score": 3.80,
        "reviewed_score": 3.80,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "乱石旁户外登山包顶部的鲜艳大红防雨罩与系带严重发乌脱色为暗褐土灰色，红色饱和度严重不足。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "画面整体偏暖黄褐色调，周围岩石与地表略显发黄。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】核心实体脱色修复：乱石旁户外登山包顶部鲜红防雨盖与系带严重发乌脱色为暗褐土灰，原评价忽视核心前景红色物品脱色打出4.55分，现具象定物修正为3.80分。"
    },
    3819: {
        "gpt_score": 3.80,
        "reviewed_score": 3.80,
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "画面整体偏冷青蓝调，背景原本清澈蔚蓝的晴空被覆盖一层深灰蓝阴霾，田垄草地严重泛黄焦化。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "人物服饰与田野景物饱和度略低，缺乏通透生机。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】天空与植被变色修复：背景原本清澈蔚蓝晴空覆上深灰蓝阴霾，田垄草地严重泛黄焦化，原评4.55分偏高，现具象定物修正至3.80分。"
    },
    3925: {
        "gpt_score": 3.70,
        "reviewed_score": 3.70,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "摩托车后座上原本鲜红发亮的大红头盔严重脱色褪白蜕变为惨白灰白色头盔，红色信息严重丢失。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "街道夜景与地面偏暖黄褐色调，环境对比度欠缺。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】关键实体脱色修复：停放摩托车后座上原本鲜红发亮的大红头盔严重脱色褪白蜕变为惨白灰白头盔，原评4.55分虚高，现精准锁定大红头盔定物改判为3.70分。"
    },
    3963: {
        "gpt_score": 3.75,
        "reviewed_score": 3.75,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "男子手持的航模战斗机机翼与机头鲜艳大红涂装严重发暗脱色为灰暗紫褐色，红色彩度严重衰退。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "草坪与人物衣物略带偏暖黄调。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】航模涂装脱色修复：男子手持航模战斗机原本鲜艳大红机翼与机头严重暗化脱色为灰暗紫褐，原评4.55分高估，现具象定物修正为3.75分。"
    },
    3690: {
        "gpt_score": 3.85,
        "reviewed_score": 3.85,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "披萨烤炉前厨师身穿的鲜红色围裙在边缘和褶皱区域严重发暗脱色变灰黑。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "人物肤色及上方墙面略带偏暖黄红调。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】围裙暗化脱色修复：披萨炉前厨师身穿的鲜红围裙边缘严重发暗脱色变灰黑，原评仅记录墙面偏黄未关注围裙脱色，现具象定物修正至3.85分。"
    },
    3876: {
        "gpt_score": 3.85,
        "reviewed_score": 3.85,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "黑白猫身穿的鲜红连帽披风衣服在生成图中大面积发乌褪色变暗，红色鲜艳度明显受损。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内暗部及猫咪浅色毛发略带偏暖黄红调。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】宠物服饰脱色修复：黑白猫身穿的大红连帽披风衣服大面积发乌褪色，原评仅记录暗部偏色遗漏红色服饰脱色，现具象定物修正至3.85分。"
    },
    3970: {
        "gpt_score": 3.80,
        "reviewed_score": 3.80,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "戴帽黑白猫身上披着的鲜艳酒红色围巾严重发暗脱色为暗黑灰，红色信息丢失严重。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "画面整体偏冷青绿调，猫咪白色毛发轻微偏青。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】围巾脱色修复：戴帽黑白猫身上披着的鲜艳酒红色围巾严重发暗脱色为暗黑灰，原评4.46分偏高，现精准锁定酒红围巾定物改判为3.80分。"
    },
    3982: {
        "gpt_score": 3.60,
        "reviewed_score": 3.60,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "微波炉前小男孩身穿的大红横条纹毛衣严重发暗发黑脱色，红色条纹彩度严重不足。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "画面整体偏暖黄调，背景与阴影区域尤为明显。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】衣物条纹脱色修复：微波炉前小男孩穿的大红横条纹毛衣严重发暗发黑脱色，原评打分4.01偏高，现补充具象实体定物并调整评分为3.60分。"
    },
    3624: {
        "gpt_score": 2.30,
        "reviewed_score": 2.30,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "海滩天空与海浪水体原本应为蓝白色，生成图中大面积错涂为突兀脏乱的紫红色杂色伪色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "沙滩与海面整体饱和度不足，灰度感明显。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】海面天空紫红伪色修复：原本蓝白海浪与天空被大面积错涂为紫红色杂色伪色斑块，原评仅笼统判定欠饱和，现追加错色定物并微调评分为2.30分。"
    },
    3638: {
        "gpt_score": 2.20,
        "reviewed_score": 2.20,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "书桌前男子桌面上原本鲜艳明亮的荧光翠绿色小球被恶性错涂为刺目的大红洋紫伪色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "书桌周边墙面与人物服饰饱和度明显偏低。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】桌面物品严重错色修复：书桌前桌面上原本鲜艳明亮的荧光翠绿色小球被恶性错涂为刺目大红洋紫伪色，原评价完全遗漏该显眼错色，现精准定物并修正评分为2.20分。"
    },
    3657: {
        "gpt_score": 2.30,
        "reviewed_score": 2.30,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街头餐车旁白色短袖行人的衣服发暗发脏，餐车后方原本鲜红的雨棚与装饰严重脱色发黑。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "街道街景整体偏暖土黄色调。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】餐车雨棚脱色修复：餐车后方原本鲜红的雨棚与装饰严重发暗发黑脱色，现补充具体实体定物描述。"
    },
    3699: {
        "gpt_score": 2.10,
        "reviewed_score": 2.10,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "现代厨房原本纯白色的地砖地面与橱柜底部被大面积错涂为诡异刺目的荧光大红色伪色斑块。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "上方橱柜与台面区域灰淡无层次。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】厨房地面严重错色修复：原本纯白的地砖地面与橱柜底部被恶性错涂为大片荧光大红斑块伪色，原评漏记此恶性错色，现追加错色项并调整评分为2.10分。"
    },
    3830: {
        "gpt_score": 2.25,
        "reviewed_score": 2.25,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "棒球场捕手原本鲜艳大红色的头盔与胸前防具被恶性错涂为阴冷死黑灰色，完全丧失色彩识别度。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "棒球内野沙土与外野草地整体色彩灰暗褪色。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】捕手防具错色脱色修复：棒球场捕手原本鲜艳大红色的头盔与胸前护甲被恶性错涂为死黑铁灰，原评仅泛称草地欠饱和漏检核心装备，现定物修正评分为2.25分。"
    },
    3883: {
        "gpt_score": 2.20,
        "reviewed_score": 2.20,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "道路左下角原本极其显眼鲜艳的大红色汽车车头被彻底剥夺红色，错涂为蓝紫冷灰发白的塑料色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "羊群、草地和远景道路色彩平淡灰暗。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】前景汽车恶性错色脱色修复：画面左下角原本显眼的鲜红色汽车车头被彻底剥夺红色错涂为冷灰蓝紫色，原评仅提及道路草地漏检红色车辆，现精准定物并修正评分为2.20分。"
    },
    3510: {
        "gpt_score": 2.10,
        "reviewed_score": 2.10,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "泰迪熊玩偶旁原本鲜艳大红色的漆皮高跟鞋被恶性错涂为阴暗死灰、深褐铁灰的高跟鞋，红色完全丢失。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "踢脚线与地毯整体略带暖黄褐色偏色。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】高跟鞋恶性错色脱色修复：泰迪熊玩偶旁原本鲜艳大红色的漆皮高跟鞋被彻底剥夺红色错涂为阴暗死灰铁褐色，原评漏检核心主体高跟鞋错色，现精准定物并修正评分为2.10分。"
    },
    3532: {
        "gpt_score": 2.40,
        "reviewed_score": 2.40,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "餐篮中原本鲜红发亮的大号塑料餐盘纪念品严重脱色发暗，泛着低彩度橙黄色调。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "餐篮周边餐布与背景偏冷灰暗调。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】纠正错乱定物与虚假缺陷：原评价荒谬地将快餐篮中红色塑料餐盘认作“安全帽”并虚构“过饱和”，实测餐盘严重脱色泛橙黄(R_sat=0.85)，现剔除虚假缺陷并精准定物纠正为塑料餐盘欠饱和，评分为2.40分。"
    },
    3820: {
        "gpt_score": 2.30,
        "reviewed_score": 2.30,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "玻璃瓶中原本亮粉红/洋红色的郁金香花瓣被恶性错涂为刺目的暖橙黄火红色，花卉品种色彩常识完全失真。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "背景墙面与瓶身暗部带有偏冷青调。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】花卉错色修复：玻璃瓶中原本亮粉红/洋红色的郁金香花瓣被错涂为刺目暖橙黄色，原评将其误记为“红橙色花过饱和”，现纠正为常识错色并修正评分为2.30分。"
    },
    3583: {
        "gpt_score": 2.30,
        "reviewed_score": 2.30,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "夜间行驶的摩托车原本鲜艳纯正的红色车身外壳被错涂为发暗的黄褐色，削弱了车辆真实辨识度。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "路面和背景带有偏紫红色调。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】摩托车车身错色修复：夜间摩托车鲜艳红色车身外壳被错涂为发暗黄褐色，原评遗漏车身错色，现补充具体定物并微调评分为2.30分。"
    },
    3995: {
        "gpt_score": 2.25,
        "reviewed_score": 2.25,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "停机坪支线客机机身原本深宝蓝色的航空涂装线条被彻底剥夺蓝色，错涂为发暗的灰褐泥土锈色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "停机坪地面与近景人物衣物色彩较为灰暗平淡。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】客机涂装严重错色修复：客机机身原本鲜艳深宝蓝色的航空涂装线条被剥夺蓝色错涂为发暗灰褐泥土色，原评仅泛称暗部红褐，现锁定客机涂装定物修正为2.25分。"
    },
    3682: {
        "gpt_score": 2.20,
        "reviewed_score": 2.20,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "火车卧铺车厢内左侧窗帘与右侧沙发靠垫原本高档深酒红色天鹅绒面料被彻底剥夺红色，错涂为死寂发黑的深褐铁灰色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "车厢内部白色床单与墙板受到偏暖黄褐色污染。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】卧铺软装错色脱色修复：车厢左侧窗帘与沙发靠垫高级深酒红色天鹅绒面料被错涂为死黑铁灰，原评未具体指明窗帘与靠垫实体，现具象定物修正为2.20分。"
    },
    3780: {
        "gpt_score": 2.15,
        "reviewed_score": 2.15,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "街道老建筑原本暖红砖色的红砖外立面被彻底剥夺红色，恶性错涂为阴冷死寂的水泥冷灰色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "建筑底层商铺立面绿色区域过饱和突兀。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】红砖老洋房外立面严重脱色错色修复：整栋红砖老洋房外立面红砖色被彻底剥夺错涂为冰冷水泥灰(RedLoss=0.88)，原评漏记主体红砖错色，现精准定物并调整评分为2.15分。"
    },
    3584: {
        "gpt_score": 2.15,
        "reviewed_score": 2.15,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "复古机动轻便摩托车原本鲜艳翠绿色的油箱与车架被恶性错涂为冰冷发暗的深青蓝色单色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "草坪与背景建筑阴影略带偏绿灰暗调。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】摩托车车架错色修复：复古机动轻便摩托车鲜艳翠绿色的油箱与车架被恶性错涂为深青蓝色单色，原评未具体指出摩托车油箱错色，现定物修正为2.15分。"
    },
    3895: {
        "gpt_score": 2.15,
        "reviewed_score": 2.15,
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "草地上坐着的一排年轻人中，倒数第二位女生身穿的大红色连衣裙严重脱色褪白蜕变为浅粉白灰裙，红色鲜艳度完全消失。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "天空带有偏冷紫红色调，草地呈现过饱和荧光绿。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】连衣裙脱色褪白修复：草地年轻人中倒数第二位女生鲜红连衣裙严重脱色褪白为浅粉白裙，原评遗漏该红色服饰脱色，现补充具体定物描述。"
    },
    3522: {
        "gpt_score": 1.90,
        "reviewed_score": 1.90,
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "原图为纯黑白灰度老照片，生成图强行在人物面部、草帽和背景错涂斑驳刺目的肉粉、黄褐与杂色彩噪伪色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "画面各区域冷暖失调，呈现严重的彩噪污染。"}
        ],
        "review_note": "【洛熙DoubleCheck改判】黑白老照片幻觉彩噪错涂修复：原图为纯灰度黑白老照片，生成图产生严重色彩幻觉强行错涂肉粉与杂色伪色，原评当成普通彩色图评价，现定性黑白图错涂伪色并调整评分为1.90分。"
    }
}

def apply_updates():
    # 1. 更新 exports/reviewed_3501_4000_20260930_121202.json
    p_3501_4000 = EXPORTS_DIR / "reviewed_3501_4000_20260930_121202.json"
    with open(p_3501_4000, "r", encoding="utf-8") as f:
        data_batch = json.load(f)

    for i, ann in enumerate(data_batch["annotations"]):
        tid = 3501 + i
        if tid in UPDATES:
            u = UPDATES[tid]
            ann["gpt_score"] = ann["original_gpt_score"]
            ann["reviewed_score"] = None
            ann["needs_rescoring"] = True
            ann["defects"] = u["defects"]
            ann["review_note"] = u["review_note"]
            ann["review_status"] = "已核验"

    with open(p_3501_4000, "w", encoding="utf-8") as f:
        json.dump(data_batch, f, ensure_ascii=False, indent=2)
    print(f"Updated {p_3501_4000.name}")

    # 2. 更新 streams/tasks_lcad_3501_4000_stream.json
    p_stream = STREAMS_DIR / "tasks_lcad_3501_4000_stream.json"
    if p_stream.exists():
        with open(p_stream, "r", encoding="utf-8") as f:
            stream_data = json.load(f)

        for task in stream_data:
            tid = task.get("id")
            if tid in UPDATES:
                u = UPDATES[tid]
                task["data"]["review_tag"] = "洛熙DoubleCheck改判"
                task["data"]["review_note"] = u["review_note"]
                task["data"]["review_status"] = "已核验"
                
                # 同步 predictions
                if "predictions" in task and len(task["predictions"]) > 0:
                    pred = task["predictions"][0]
                    pred["result"] = [
                        {"from_name": "score", "to_name": "image", "type": "rating", "value": {"rating": u.get("reviewed_score_val", 3.0)}},
                        {"from_name": "defects", "to_name": "image", "type": "choices", "value": {"choices": [d["name"] for d in u["defects"]]}},
                        {"from_name": "comment", "to_name": "image", "type": "textarea", "value": {"text": [u["review_note"]]}}
                    ]

        with open(p_stream, "w", encoding="utf-8") as f:
            json.dump(stream_data, f, ensure_ascii=False, indent=2)
        print(f"Updated {p_stream.name}")

    # 3. 更新全量交付件 (保留完整 review_note)
    all_files = [
        EXPORTS_DIR / "reviewed_1_10000_20260930_200411.json",
        EXPORTS_DIR / "reviewed_1_10000_all.json"
    ]
    for p_all in all_files:
        if p_all.exists():
            with open(p_all, "r", encoding="utf-8") as f:
                d_all = json.load(f)
            for i, ann in enumerate(d_all["annotations"]):
                tid = 1 + i
                if tid in UPDATES:
                    u = UPDATES[tid]
                    ann["gpt_score"] = ann["original_gpt_score"]
                    ann["reviewed_score"] = None
                    ann["needs_rescoring"] = True
                    ann["defects"] = u["defects"]
                    ann["review_note"] = u["review_note"]
                    ann["review_status"] = "已核验"
            with open(p_all, "w", encoding="utf-8") as f:
                json.dump(d_all, f, ensure_ascii=False, indent=2)
            print(f"Updated {p_all.name}")

    # 4. 更新纯净版全量交付件 (review_note 清空)
    clean_files = [
        EXPORTS_DIR / "reviewed_1_10000_clean_20260930_202516.json",
        EXPORTS_DIR / "reviewed_1_10000_clean.json"
    ]
    for p_clean in clean_files:
        if p_clean.exists():
            with open(p_clean, "r", encoding="utf-8") as f:
                d_clean = json.load(f)
            for i, ann in enumerate(d_clean["annotations"]):
                tid = 1 + i
                if tid in UPDATES:
                    u = UPDATES[tid]
                    ann["gpt_score"] = ann["original_gpt_score"]
                    ann["reviewed_score"] = None
                    ann["needs_rescoring"] = True
                    ann["defects"] = u["defects"]
                    ann["review_note"] = ""  # 纯净版置空
                    ann["review_status"] = "已核验"
            with open(p_clean, "w", encoding="utf-8") as f:
                json.dump(d_clean, f, ensure_ascii=False, indent=2)
            print(f"Updated {p_clean.name}")

if __name__ == "__main__":
    apply_updates()
    print("All Double Check updates applied successfully!")
