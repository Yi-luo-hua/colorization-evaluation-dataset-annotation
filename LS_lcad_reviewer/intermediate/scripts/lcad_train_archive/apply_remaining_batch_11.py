#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_remaining_batch_11.py
根据对 Batch 11（Tasks 2233 ~ 2453，共 120 组）的 20 张高清看板多模态大图直审结果，
1. 生成中间定物审计文件 grounding_remaining_batch_11.json；
2. 同步更新 reviewed_1_10000_all.json（包含精准具象定物陈述或审查通过）；
3. 同步更新 reviewed_1_10000_clean.json（全量 10,000 条保持 review_note: ""）；
4. 运行严格格式契约验证。
"""

import json
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
AUDITS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits"
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"

ALL_EXPORT = EXPORTS_DIR / "reviewed_1_10000_all.json"
CLEAN_EXPORT = EXPORTS_DIR / "reviewed_1_10000_clean.json"
OUT_GROUNDING_FILE = AUDITS_DIR / "grounding_remaining_batch_11.json"

DEFECT_NAMES = {
    "A": "缺色",
    "B": "溢色",
    "C": "错色",
    "D": "偏色",
    "E1": "过饱和",
    "E2": "欠饱和",
    "F": "视觉自然度"
}

# 120 组任务的直审定物字典
REVIEWS = {
    # Sheet 01: [2233, 2234, 2237, 2238, 2241, 2245]
    2233: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2", "D": "L1"},
        "note": "双人床上铺着的鲜艳松石青蓝毛毯严重褪色剥落，被错涂为浑浊暗淡的灰黄褐色，且室内墙面整体泛暖黄（错色 C-L2，欠饱和 E2-L2，轻度偏色 D-L1）。"
    },
    2234: {
        "is_pass": False,
        "severities": {"E2": "L2", "B": "L1", "F": "L1"},
        "note": "卫生间马桶后方墙面原本清晰醒目的蓝色瓷砖装饰线条严重褪色泛灰绿，马桶盖与水箱边缘出现轻微溢色污染（欠饱和 E2-L2，轻度溢色 B-L1，视觉自然度受损 F-L1）。"
    },
    2237: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "卧室内双人床上铺盖的鲜艳深红色床单被罩被大面积剥色，严重错涂为发暗的灰褐浅绿杂色（严重错色 C-L3，欠饱和 E2-L2）。"
    },
    2238: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2"},
        "note": "冲浪海域原本蔚蓝纯净的海水与上空碧蓝天际被大面积常识性误涂为浑浊发暗的草绿色与灰青色（常识错色 C-L3，系统性偏色 D-L2）。"
    },
    2241: {
        "is_pass": False,
        "severities": {"D": "L2", "F": "L1"},
        "note": "海浪翻滚的浪花与近海海水原本纯净清澈的深蓝色被错涂为泛黄偏绿的浑浊色调，波浪暗部偏色（偏色 D-L2，轻度自然度受损 F-L1）。"
    },
    2245: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L1"},
        "note": "户外展示装置中固定玻璃胶囊的红铜色金属固定环与基座严重褪色，金属光泽剥落错涂为暗哑冷灰色（中度偏色 D-L2，欠饱和 E2-L1）。"
    },

    # Sheet 02: [2246, 2252, 2253, 2256, 2258, 2262]
    2246: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "羊圈左侧围栏处挂放的粉红色料桶被严重剥色错涂为暗青灰色，羊毛阴影部略微偏黄（错色 C-L2，欠饱和 E2-L2）。"
    },
    2252: {
        "is_pass": False,
        "severities": {"E2": "L2", "D": "L2", "F": "L1"},
        "note": "西兰花底部衬托的深蓝鲜艳桌布大面积褪色泛青绿，西兰花茎部出现不自然的荧光黄绿色高光（欠饱和 E2-L2，偏色 D-L2，视觉自然度受损 F-L1）。"
    },
    2253: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L3", "F": "L2"},
        "note": "停机坪停放的民航客机机身与整片天空背景被严重常识性错涂为浑浊病态的草绿色，全图系统性严重偏绿（常识错色 C-L3，严重偏色 D-L3，自然度恶化 F-L2）。"
    },
    2256: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "室内餐桌上的花生酱罐标签与用餐人员手臂皮肤被严重涂抹为浓艳刺眼的火红色与紫红色调，高光严重溢出偏色（严重偏色 D-L2，过饱和 E1-L2，自然度恶化 F-L2）。"
    },
    2258: {
        "is_pass": False,
        "severities": {"B": "L2", "E1": "L1", "F": "L1"},
        "note": "男子腰部穿着的白色T恤下摆及右侧背景突兀出现异常刺眼的亮红色彩晕污染，牛仔裤暗部泛紫红（轻度溢色 B-L2，轻度过饱和 E1-L1，视觉自然度受损 F-L1）。"
    },
    2262: {
        "is_pass": False,
        "severities": {"D": "L2", "F": "L1"},
        "note": "笔记本电脑屏幕边框上停歇的蜻蜓翅膀与腹部被异常渲染出紫红色杂色色斑，破坏昆虫甲壳自然半透明光泽（偏色 D-L2，视觉自然度受损 F-L1）。"
    },

    # Sheet 03: [2263, 2265, 2266, 2270, 2271, 2275]
    2263: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2265: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "草坪上耸立的消防栓原本鲜红夺目的红色漆面被严重褪色错涂为粉白带淡紫的浅色调（严重错色 C-L2，欠饱和 E2-L2）。"
    },
    2266: {
        "is_pass": False,
        "severities": {"E2": "L2", "D": "L1", "F": "L1"},
        "note": "餐厅餐桌旁就座女孩身上鲜艳的洋红色休闲外套褪色偏暗紫，木质餐桌表面局部出现异常青冷色斑（欠饱和 E2-L2，轻度偏色 D-L1，视觉自然度受损 F-L1）。"
    },
    2270: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2"},
        "note": "棒球场击球区后方原本明朗的蓝天被彻底错涂为发暗的灰褐色树丛背景，红土内野地面颜色泛紫偏暗（常识错色 C-L3，严重偏色 D-L2）。"
    },
    2271: {
        "is_pass": False,
        "severities": {"D": "L1"},
        "note": "餐盘周围铺设的深红鲜艳桌布色彩饱和度略降且微泛暗褐，顶部配菜绿叶边缘略有轻微偏色（轻度偏色 D-L1）。"
    },
    2275: {
        "is_pass": False,
        "severities": {"C": "L3", "B": "L2", "F": "L2"},
        "note": "街头雨中人群撑开的深灰色折叠伞面被常识性错涂为明亮突兀的亮黄色，雨伞边缘与服饰产生大面积杂色污染（常识错色 C-L3，轻度溢色 B-L2，视觉自然度受损 F-L2）。"
    },

    # Sheet 04: [2276, 2278, 2281, 2283, 2285, 2286]
    2276: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "网球防护网内击球人员原本鲜红醒目的红色运动短袖T恤被严重褪色，错涂为暗哑青灰带浅紫调（错色 C-L2，欠饱和 E2-L2）。"
    },
    2278: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "斑马围栏背景建筑左上方天窗透出的自然蓝色天光被褪色涂为暗黄灰白，斑马黑白条纹边缘略有轻微发黄（偏色 D-L1，欠饱和 E2-L1）。"
    },
    2281: {
        "is_pass": False,
        "severities": {"E2": "L1", "D": "L1"},
        "note": "街道左侧停放的三轮车及上方悬挂的商铺遮阳棚广告招牌鲜艳彩绘略有褪色，局部边缘色彩饱和度不足（欠饱和 E2-L1，轻度偏色 D-L1）。"
    },
    2283: {
        "is_pass": False,
        "severities": {"E2": "L1", "D": "L1"},
        "note": "草原上伫立的长颈鹿身体红褐色斑纹饱和度偏低褪色，背景开阔草地与天空交界处色彩层次偏淡（欠饱和 E2-L1，轻度偏色 D-L1）。"
    },
    2285: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2286: {
        "is_pass": False,
        "severities": {"D": "L2", "F": "L2"},
        "note": "拿汉堡的男孩面部五官及额头阴影处突兀出现发青发暗的灰暗色斑，破坏真实健康的人体肤色质感（中度偏色 D-L2，视觉自然度受损 F-L2）。"
    },

    # Sheet 05: [2287, 2288, 2292, 2293, 2296, 2297]
    2287: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2", "D": "L2"},
        "note": "卧室内床铺上铺垫的鲜艳暖橙色床单被大面积褪色错涂为苍白带淡紫的冷白色，书桌木质椅面严重偏色（严重错色 C-L3，欠饱和 E2-L2，偏色 D-L2）。"
    },
    2288: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "街景右侧红砖建筑外墙及骑行者手臂皮肤色温偏冷暗淡，红砖墙面原本温暖的砖红质感有所减损（轻度偏色 D-L1，欠饱和 E2-L1）。"
    },
    2292: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "铁栏杆旁打电话男子身穿的鲜艳亮橙红色长袖卫衣被大面积剥色，严重错涂为发暗的苍灰褐色（严重错色 C-L3，严重欠饱和 E2-L2）。"
    },
    2293: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2"},
        "note": "骑马者脚下原本泛着温暖黄褐色的沙丘地面被常识性误涂为冰冷刺眼的白雪与青蓝色积雪冰原（常识错色 C-L3，系统性偏色 D-L2）。"
    },
    2296: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "微波炉上方放置的立顿红茶明黄色包装盒严重褪色泛白，后方浅绿色墙面脱色退化为冷灰白（错色 C-L2，欠饱和 E2-L2）。"
    },
    2297: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 06: [2299, 2302, 2303, 2305, 2307, 2309]
    2299: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L1"},
        "note": "棒球击球手后方看台防护栏上原本鲜艳的青蓝色广告防撞垫被错涂为暗哑浑浊的墨绿色，棒球手蓝色护臂略微发灰（错色 C-L2，欠饱和 E2-L1）。"
    },
    2302: {
        "is_pass": False,
        "severities": {"E2": "L2", "C": "L2"},
        "note": "多图拼贴网格缩略图中篮球的鲜红球皮、摩托车及多处彩色生活照被大面积剥色抽色，退化为死气沉沉的单调黑白灰（严重欠饱和 E2-L2，错色 C-L2）。"
    },
    2303: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "椰林绿洲上方开阔的天空原本纯净的淡天蓝色被错涂为泛青灰白，远方密集椰子树树冠阴影泛青冷色（偏色 D-L1，欠饱和 E2-L1）。"
    },
    2305: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2307: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2309: {
        "is_pass": False,
        "severities": {"C": "L2", "D": "L2", "F": "L2"},
        "note": "室内更衣男子身后的房间背景墙壁被严重常识性错涂为突兀泛荧光的草绿色，白衬衫暗部与男子发际线受到冷绿反光污染（常识错色 C-L2，中度偏色 D-L2，视觉自然度受损 F-L2）。"
    },

    # Sheet 07: [2311, 2313, 2314, 2315, 2317, 2318]
    2311: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2313: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "街道人行道旁的三角警示交通标志牌及周围墙面涂鸦色彩还原欠佳，局部边缘出现发青偏色（轻度偏色 D-L1，欠饱和 E2-L1）。"
    },
    2314: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "草坪停机坪上停放的小型螺旋桨飞机机翼支架、机身红色彩条及尾翼鲜艳红漆被大面积剥色，严重错涂为发暗的灰蓝与灰黑色（严重错色 C-L3，欠饱和 E2-L2）。"
    },
    2315: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2317: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L3", "D": "L2"},
        "note": "海滨沙滩浴场原本碧蓝通透的海水与晴朗蔚蓝的天空被严重剥色抽色，整体错涂为阴沉暗哑的铅灰色，海岛度假氛围彻底丧失（严重错色 C-L3，严重欠饱和 E2-L3，偏色 D-L2）。"
    },
    2318: {
        "is_pass": False,
        "severities": {"C": "L2", "D": "L1"},
        "note": "站在镜子前的戴眼镜男子身后的浅橄榄绿房间墙壁严重褪色，被错涂为浑浊泛暖黄的米白色（错色 C-L2，偏色 D-L1）。"
    },

    # Sheet 08: [2320, 2322, 2324, 2325, 2326, 2328]
    2320: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2322: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2324: {
        "is_pass": False,
        "severities": {"C": "L3", "F": "L2"},
        "note": "白色餐盘中切片的烤牛肉原本鲜嫩多汁的粉褐肉色被严重错涂为发霉般的灰绿色腐败肉感，令人食欲全无（严重错色 C-L3，视觉自然度恶化 F-L2）。"
    },
    2325: {
        "is_pass": False,
        "severities": {"B": "L1", "D": "L1"},
        "note": "小男孩撑起的紫色雨伞伞面边缘出现轻微颜色溢出，深蓝短袖T恤领口及衣袖处略带杂色反光（轻度溢色 B-L1，轻度偏色 D-L1）。"
    },
    2326: {
        "is_pass": False,
        "severities": {"E2": "L1", "D": "L1"},
        "note": "沿街商铺“上海陆杨邨”招牌上的翠绿与红色字样色彩饱和度不足，上方雨棚暗部微泛偏色（欠饱和 E2-L1，轻度偏色 D-L1）。"
    },
    2328: {
        "is_pass": False,
        "severities": {"C": "L3", "E1": "L1"},
        "note": "水果摊左下方竹筐中堆放的浅褐色洋葱/土豆被常识性严重错涂为鲜艳刺眼的洋红色草莓/红心萝卜（严重常识错色 C-L3，轻度过饱和 E1-L1）。"
    },

    # Sheet 09: [2329, 2330, 2331, 2333, 2334, 2335]
    2329: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "沙滩躺椅上方遮阳的大型太阳伞原本鲜艳夺目的暖橙色伞面严重褪色，被错涂为暗哑浅土黄色（错色 C-L2，欠饱和 E2-L2）。"
    },
    2330: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2331: {
        "is_pass": False,
        "severities": {"E2": "L1", "D": "L1"},
        "note": "激流冲浪河岸边等待的冲浪板上明艳的黄绿配色饰条褪色泛暗灰，河水翻涌浪花暗部略带发暗偏色（欠饱和 E2-L1，轻度偏色 D-L1）。"
    },
    2333: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "编织餐桌上比萨饼表面铺洒的翠绿罗勒叶与新鲜芝麻菜被大面积褪色错涂为浑浊焦糊的暗褐色（严重错色 C-L3，欠饱和 E2-L2）。"
    },
    2334: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2335: {
        "is_pass": False,
        "severities": {"E2": "L2", "D": "L1"},
        "note": "白色餐盘下方衬垫的深蓝鲜艳桌布大面积褪色，被错涂为浑浊灰暗的蓝紫色（欠饱和 E2-L2，偏色 D-L1）。"
    },

    # Sheet 10: [2336, 2337, 2339, 2341, 2342, 2343]
    2336: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L1"},
        "note": "电脑书桌层架上放置的红色模型车与彩色光盘收纳盒色彩被剥离泛暗灰，书架局部偏色（错色 C-L2，欠饱和 E2-L1）。"
    },
    2337: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2339: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "木质餐桌上披萨饼与烘焙馅饼表皮原本金黄诱人的色泽微泛冷调，餐盘边缘与桌面受光略带暗紫偏色（轻度偏色 D-L1，欠饱和 E2-L1）。"
    },
    2341: {
        "is_pass": False,
        "severities": {"C": "L3", "F": "L2"},
        "note": "棒球投手脚下原本大面积翠绿鲜活的草坪场地被严重常识性错涂为大片刺眼的珊瑚粉红色内野红土（常识错色 C-L3，视觉自然度恶化 F-L2）。"
    },
    2342: {
        "is_pass": False,
        "severities": {"B": "L2", "D": "L2", "F": "L2"},
        "note": "墙面挂置的古董短剑周围背景墙壁突兀出现大面积黄蓝彩虹杂色光晕污染，刀身轮廓边缘严重溢色（中度溢色 B-L2，偏色 D-L2，视觉自然度恶化 F-L2）。"
    },
    2343: {
        "is_pass": False,
        "severities": {"D": "L2", "B": "L1", "F": "L1"},
        "note": "自拍女子脸颊面部肤色受到严重红紫偏色污染，呈现不自然的潮红暗斑，手机屏幕周围泛青蓝色溢色（中度偏色 D-L2，轻度溢色 B-L1，自然度受损 F-L1）。"
    },

    # Sheet 11: [2346, 2349, 2351, 2352, 2353, 2356]
    2346: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L3", "D": "L2"},
        "note": "秃鹫栖息的暖橙色砂岩岩壁被大面积严重剥色错涂为冷淡灰白色，秃鹫头部裸露的橙红皮肤褪色发黑（严重错色 C-L3，严重欠饱和 E2-L3，中度偏色 D-L2）。"
    },
    2349: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2351: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2352: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "棒球击球手身后左侧看台围栏上原本鲜艳醒目的红色广告背景板被大面积错涂为暗哑发灰的深褐色（严重错色 C-L3，欠饱和 E2-L2）。"
    },
    2353: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L3"},
        "note": "遮阳伞面左侧原本鲜红醒目的三角形伞布被彻底剥色抽色，严重错涂为发暗的苍灰褐色（严重错色 C-L3，严重欠饱和 E2-L3）。"
    },
    2356: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "停放皮卡车旁站立的小男孩身上穿着的翠绿色短袖T恤严重褪色，被错涂为浑浊暗淡的灰褐色（错色 C-L2，欠饱和 E2-L2）。"
    },

    # Sheet 12: [2357, 2359, 2360, 2361, 2364, 2365]
    2357: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2359: {
        "is_pass": False,
        "severities": {"D": "L1", "E2": "L1"},
        "note": "阴天海域中海面海水与天际线上空色彩整体泛冷，波浪翻滚暗部青蓝色调过重（偏色 D-L1，欠饱和 E2-L1）。"
    },
    2360: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2", "D": "L2"},
        "note": "两只斑马脚下原本温暖金黄的干草荒原地面被大面积剥色，严重错涂为冰冷暗淡的枯灰色泥地（错色 C-L2，欠饱和 E2-L2，偏色 D-L2）。"
    },
    2361: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2364: {
        "is_pass": False,
        "severities": {"D": "L2", "F": "L1"},
        "note": "翻滚巨浪的卷曲浪壁与深水区原本深沉的幽蓝色被错涂为浑浊的墨绿色，波浪暗部偏色（偏色 D-L2，视觉自然度受损 F-L1）。"
    },
    2365: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 13: [2366, 2370, 2373, 2374, 2376, 2378]
    2366: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2370: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "曼谷街头素坤逸巷“Sukhumvit 6”路牌原本深蓝绿色的底漆严重褪色，被错涂为暗哑发灰的深紫灰色（错色 C-L2，欠饱和 E2-L2）。"
    },
    2373: {
        "is_pass": False,
        "severities": {"E2": "L1", "D": "L1"},
        "note": "单板滑雪者空中跳跃手中高举的彩色旗帜局部条纹脱色，旗面鲜艳度有所减损（欠饱和 E2-L1，轻度偏色 D-L1）。"
    },
    2374: {
        "is_pass": False,
        "severities": {"D": "L2", "F": "L2"},
        "note": "敞开的双门冰箱内部保鲜室原本洁白清爽的内壁被异常渲染出大面积诡异刺眼的粉红肉色反光，破坏家电内部真实质感（严重偏色 D-L2，视觉自然度恶化 F-L2）。"
    },
    2376: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2378: {
        "is_pass": False,
        "severities": {"C": "L3", "B": "L2", "F": "L2"},
        "note": "分格便当盒上方原本金黄浓郁的咖喱蛋羹被极其荒唐地严重错涂为荧光青蓝色化工液体，右侧烤肉边缘溢色（严重常识错色 C-L3，轻度溢色 B-L2，视觉自然度恶化 F-L2）。"
    },

    # Sheet 14: [2379, 2381, 2382, 2384, 2385, 2386]
    2379: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2381: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L1"},
        "note": "农家院落红砖房前草坪原本鲜嫩葱绿的草地大面积褪色泛枯黄，红砖围墙色调微泛暗哑（错色 C-L2，欠饱和 E2-L1）。"
    },
    2382: {
        "is_pass": False,
        "severities": {"B": "L1", "E1": "L2", "F": "L1"},
        "note": "黑熊母子觅食的草地背景被过度涂染为浓艳刺眼的荧光亮黄绿色，黑熊毛发边缘泛紫红杂色溢色（轻度溢色 B-L1，过饱和 E1-L2，视觉自然度受损 F-L1）。"
    },
    2384: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2385: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2386: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 15: [2388, 2390, 2392, 2393, 2394, 2395]
    2388: {
        "is_pass": False,
        "severities": {"C": "L3", "E1": "L1", "D": "L2"},
        "note": "卧室电脑桌上笔记本与外接显示器屏幕原本明亮清澈的青蓝色画面被严重错涂为诡异刺眼的洋红色强光（严重错色 C-L3，轻度过饱和 E1-L1，偏色 D-L2）。"
    },
    2390: {
        "is_pass": False,
        "severities": {"D": "L2", "F": "L1"},
        "note": "夜间街道十字路口原本深邃纯净的夜空背景突兀出现大面积发灰泛紫的浑浊光晕，破坏夜景环境光效（中度偏色 D-L2，视觉自然度受损 F-L1）。"
    },
    2392: {
        "is_pass": False,
        "severities": {"C": "L3", "E2": "L2"},
        "note": "山顶远眺城市俯景的青年男子身上原本深红紫色的格子长袖衬衫被严重常识性错涂为灰绿色（严重错色 C-L3，欠饱和 E2-L2）。"
    },
    2393: {
        "is_pass": False,
        "severities": {"D": "L2", "C": "L2"},
        "note": "起居室壁炉两侧原本泛着温暖杏黄色调的室内墙壁大面积严重错涂为发暗的灰紫冷调，房间温馨氛围受损（中度偏色 D-L2，错色 C-L2）。"
    },
    2394: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2395: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "儿童绘本与毛绒玩具堆中左侧放置的蓝色图画书封面大面积脱色泛白，后方条纹织物暗部色彩饱和度受损（错色 C-L2，欠饱和 E2-L2）。"
    },

    # Sheet 16: [2397, 2398, 2401, 2404, 2405, 2412]
    2397: {
        "is_pass": False,
        "severities": {"E2": "L2", "D": "L1"},
        "note": "厨房百叶窗外透出的绿树植被与自然天光大面积褪色泛白，窗台下白色橱柜暗部略显偏暗（欠饱和 E2-L2，轻度偏色 D-L1）。"
    },
    2398: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2401: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L3", "E2": "L3"},
        "note": "复古老旧相册原本温暖浓郁的琥珀黄褐色调及木地板被严重系统性剥色，错涂为冰冷暗淡的死灰水泥色（严重错色 C-L3，严重偏色 D-L3，欠饱和 E2-L3）。"
    },
    2404: {
        "is_pass": False,
        "severities": {"C": "L3", "E1": "L2", "B": "L2", "F": "L2"},
        "note": "包装纸上放置的长条潜艇堡面包前沿原本深褐色的烧烤酱汁被极其荒谬地错涂为浓艳刺眼的荧光亮橙红色，严重溢色污染面包皮（严重错色 C-L3，过饱和 E1-L2，中度溢色 B-L2，自然度恶化 F-L2）。"
    },
    2405: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "大巴车身喷涂的“TRAVEL BY BUS!”广告标语中原本鲜绿醒目的字母“TRAVEL”严重褪色退化为冷灰色（错色 C-L2，欠饱和 E2-L2）。"
    },
    2412: {"is_pass": True, "severities": {}, "note": "审查通过"},

    # Sheet 17: [2416, 2418, 2420, 2421, 2422, 2424]
    2416: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L3", "E2": "L2"},
        "note": "海滩沙滩与海天交界线原本晴朗纯净的碧蓝天际被大面积系统性错涂为浑浊昏黄的沙尘土黄色（常识错色 C-L3，系统性偏色 D-L3，欠饱和 E2-L2）。"
    },
    2418: {
        "is_pass": False,
        "severities": {"D": "L2", "E1": "L1", "F": "L1"},
        "note": "卫生间洗手台旁嵌入式收纳壁龛内部突兀出现过度浓艳刺眼的火红色强光过曝，破坏现代卫浴柔和质感（偏色 D-L2，轻度过饱和 E1-L1，视觉自然度受损 F-L1）。"
    },
    2420: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L2", "F": "L2"},
        "note": "围栏内绵羊身上原本温暖质朴的乳白色羊毛被严重错涂为诡异冰冷的蓝紫色调（严重错色 C-L3，偏色 D-L2，自然度恶化 F-L2）。"
    },
    2421: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "骑马女牛仔坐骑上原本鲜艳醒目的洋红色马鞍垫布被严重褪色错涂为暗哑黄褐色（错色 C-L2，欠饱和 E2-L2）。"
    },
    2422: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2424: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L1"},
        "note": "室内墙壁上方喷涂的“CLEMSON”橙色大学英文校名标识色彩严重褪色泛灰，坐地男子的衬衫暗部色彩饱和度偏低（错色 C-L2，欠饱和 E2-L1）。"
    },

    # Sheet 18: [2425, 2427, 2429, 2431, 2432, 2434]
    2425: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "窗外对街居民楼外立面原本鲜艳明朗的青蓝色墙面严重褪色，被错涂为暗哑苍白的灰白色（错色 C-L2，欠饱和 E2-L2）。"
    },
    2427: {
        "is_pass": False,
        "severities": {"D": "L1", "F": "L1"},
        "note": "白色餐盘中盛放的炒面与肉丝表面出现不自然的暗红与泛紫油渍反光，蔬菜绿叶暗部轻度偏色（偏色 D-L1，视觉自然度受损 F-L1）。"
    },
    2429: {
        "is_pass": False,
        "severities": {"B": "L2", "F": "L1"},
        "note": "沙拉盘中红番茄块边缘红色汁水严重越界溢出，浸染污染周围翠绿色的生菜嫩叶（轻度溢色 B-L2，视觉自然度受损 F-L1）。"
    },
    2431: {
        "is_pass": False,
        "severities": {"B": "L1", "D": "L1"},
        "note": "枯草山坡上耸立的明黄色消防栓底座边缘出现轻微黄色溢色，坡地干草植被层次微泛暗淡（轻度溢色 B-L1，轻度偏色 D-L1）。"
    },
    2432: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2"},
        "note": "街边停放的货运三轮车前方木质车厢原本鲜艳的橙红漆面严重褪色，被错涂为暗哑发绿的灰褐色（错色 C-L2，欠饱和 E2-L2）。"
    },
    2434: {
        "is_pass": False,
        "severities": {"D": "L1", "F": "L1"},
        "note": "动物园大象展区喂食游客身上穿着的格子衬衫色彩产生偏差，人物皮肤与大象面部阴影处微泛暗红（轻度偏色 D-L1，视觉自然度受损 F-L1）。"
    },

    # Sheet 19: [2435, 2436, 2437, 2438, 2440, 2441]
    2435: {
        "is_pass": False,
        "severities": {"D": "L2", "E2": "L1"},
        "note": "婴儿床上铺垫的浅粉色印花被褥及婴儿连体衣色彩偏冷发暗，婴儿面部肤色层次略显粗糙（偏色 D-L2，欠饱和 E2-L1）。"
    },
    2436: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2437: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2438: {
        "is_pass": False,
        "severities": {"C": "L3", "D": "L3", "E2": "L2"},
        "note": "盥洗室木框镜子周围原本浓郁温暖的金黄暖光照明被大面积剥色，墙面与镜框错涂为苍白冰冷的米白色（严重错色 C-L3，系统性偏色 D-L3，欠饱和 E2-L2）。"
    },
    2440: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L1"},
        "note": "储物架左侧格子里放置的亮绿色收纳盒与日用品严重褪色，冰箱侧面暗部色彩偏深泛暗黑（错色 C-L2，欠饱和 E2-L1）。"
    },
    2441: {
        "is_pass": False,
        "severities": {"C": "L3", "E1": "L2", "F": "L2"},
        "note": "仿古羊皮纸油画中人物面部突兀出现过度饱和刺眼的亮黄荧光光斑，画卷残破裂纹处出现异常青蓝伪色（严重常识错色 C-L3，过饱和 E1-L2，视觉自然度严重恶化 F-L2）。"
    },

    # Sheet 20: [2443, 2444, 2446, 2450, 2452, 2453]
    2443: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2444: {"is_pass": True, "severities": {}, "note": "审查通过"},
    2446: {
        "is_pass": False,
        "severities": {"C": "L2", "E2": "L2", "D": "L1"},
        "note": "斑马吃草的非洲原野前景原本呈现浓烈红土橙褐色的地表泥土被大面积褪色，错涂为暗哑发绿的灰土色（错色 C-L2，欠饱和 E2-L2，偏色 D-L1）。"
    },
    2450: {
        "is_pass": False,
        "severities": {"C": "L2", "B": "L1"},
        "note": "足球场上拼抢的小球员身上原本深蓝色的球衣领口被错涂为刺眼的荧光黄绿色，右侧球员红球衣边缘略带溢色（错色 C-L2，轻度溢色 B-L1）。"
    },
    2452: {
        "is_pass": False,
        "severities": {"D": "L3", "C": "L2", "F": "L2"},
        "note": "浴室卫生间原本整洁现代的冷灰色瓷砖墙壁被严重系统性错涂为陈旧浑浊的脏黄色调（严重偏色 D-L3，错色 C-L2，视觉自然度受损 F-L2）。"
    },
    2453: {"is_pass": True, "severities": {}, "note": "审查通过"}
}

def main():
    print(f"Total reviews defined: {len(REVIEWS)}")
    assert len(REVIEWS) == 120, f"Expected 120 reviews, got {len(REVIEWS)}"

    # 1. 自动核验双重硬门槛放行准则与禁词
    plan_file = AUDITS_DIR / "remaining_visual_audit_plan_50_batches.json"
    with open(plan_file, "r", encoding="utf-8") as f:
        plan = json.load(f)
    b11 = next(b for b in plan["batches"] if b["batch_no"] == 11)
    item_map = {it["task_id"]: it for it in b11["items"]}

    pass_count = 0
    defect_count = 0

    for tid, rev in REVIEWS.items():
        assert tid in item_map, f"Task {tid} not found in Batch 11 plan"
        item = item_map[tid]
        sc = item.get("original_gpt_score", 5.0)
        dc = item.get("metrics", {}).get("delta_c", 0.0)

        is_pass = rev["is_pass"]
        note = rev["note"]
        sevs = rev["severities"]

        if is_pass:
            pass_count += 1
            assert note == "审查通过", f"Task {tid} marked pass but note is not '审查通过'"
            assert len(sevs) == 0, f"Task {tid} marked pass but has defects"
            # 严格门槛断言
            if sc < 4.5:
                raise ValueError(f"GATE VIOLATION: Task {tid} scored {sc} (< 4.5) cannot be passed!")
            if dc >= 0.08:
                raise ValueError(f"GATE VIOLATION: Task {tid} has Delta_C {dc:.3f} (>= 0.08) cannot be passed!")
        else:
            defect_count += 1
            assert note != "审查通过", f"Task {tid} marked defect but note is '审查通过'"
            assert len(sevs) > 0, f"Task {tid} marked defect but severities empty"
            # 检查禁词
            forbidden_words = ["局部关键区域", "关键主体或背景", "轮廓边缘处", "场景物体轮廓"]
            for fw in forbidden_words:
                if fw in note:
                    raise ValueError(f"FORBIDDEN WORD: Task {tid} contains '{fw}'")

    print(f"Double-Gate check passed: {pass_count} Passed, {defect_count} Defect Groundings.")

    # 2. 写入 grounding_remaining_batch_11.json
    out_grounding = {str(k): v for k, v in REVIEWS.items()}
    with open(OUT_GROUNDING_FILE, "w", encoding="utf-8") as f:
        json.dump(out_grounding, f, ensure_ascii=False, indent=2)
    print(f"Saved: {OUT_GROUNDING_FILE}")

    # 3. 同步更新 reviewed_1_10000_all.json
    print(f"Loading {ALL_EXPORT}...")
    with open(ALL_EXPORT, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    all_map = {ann["human_review"]["task_id"]: ann for ann in all_data["annotations"]}

    updated_count = 0
    for tid, rev in REVIEWS.items():
        if tid not in all_map:
            print(f"Warning: Task {tid} not in {ALL_EXPORT}")
            continue

        ann = all_map[tid]
        is_pass = rev["is_pass"]
        note = rev["note"]
        sevs = rev["severities"]

        if is_pass:
            ann["defects"] = []
            ann["review_note"] = "审查通过"
            ann["reviewed_score"] = None
            ann["needs_rescoring"] = True
        else:
            def_list = []
            for did, sev in sevs.items():
                def_list.append({
                    "id": did,
                    "name": DEFECT_NAMES[did],
                    "severity": sev,
                    "description": note
                })
            ann["defects"] = def_list
            ann["review_note"] = note
            if "A" in sevs:
                ann["reviewed_score"] = 1.0
                ann["needs_rescoring"] = False
            else:
                ann["reviewed_score"] = None
                ann["needs_rescoring"] = True

        ann["review_status"] = "已核验"
        updated_count += 1

    with open(ALL_EXPORT, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {updated_count} items in {ALL_EXPORT}")

    # 4. 同步更新 reviewed_1_10000_clean.json
    print(f"Loading {CLEAN_EXPORT}...")
    with open(CLEAN_EXPORT, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    clean_map = {ann["human_review"]["task_id"]: ann for ann in clean_data["annotations"]}

    for tid, rev in REVIEWS.items():
        if tid not in clean_map:
            continue
        ann = clean_map[tid]
        is_pass = rev["is_pass"]
        sevs = rev["severities"]
        note = rev["note"]

        if is_pass:
            ann["defects"] = []
            ann["review_note"] = ""
            ann["reviewed_score"] = None
            ann["needs_rescoring"] = True
        else:
            def_list = []
            for did, sev in sevs.items():
                def_list.append({
                    "id": did,
                    "name": DEFECT_NAMES[did],
                    "severity": sev,
                    "description": note
                })
            ann["defects"] = def_list
            ann["review_note"] = ""
            if "A" in sevs:
                ann["reviewed_score"] = 1.0
                ann["needs_rescoring"] = False
            else:
                ann["reviewed_score"] = None
                ann["needs_rescoring"] = True

        ann["review_status"] = "已核验"

    with open(CLEAN_EXPORT, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {updated_count} items in {CLEAN_EXPORT}")

if __name__ == "__main__":
    main()
