import json
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"
ALL_FILE = EXPORTS_DIR / "reviewed_1_10000_all.json"
CLEAN_FILE = EXPORTS_DIR / "reviewed_1_10000_clean.json"

TAXONOMY = {
    "A": "缺色",
    "B": "溢色",
    "C": "错色",
    "D": "偏色",
    "E1": "过饱和",
    "E2": "欠饱和",
    "F": "视觉自然度"
}

# Round 4 逐组具象化物理实体改判映射字典 (共 157 组)
ROUND4_FIXES = {
    # Sheet 01 (Tasks 3031, 3033, 3035, 3047, 3048, 3059)
    3031: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "白色猫咪背部白色皮毛大面积烘烤泛黄，木地板与床单暖色过度。"
    },
    3033: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "户外餐椅鲜红色软垫严重脱色退化为发暗灰黑灰褐色，原木餐桌偏灰。"
    },
    3035: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "F", "name": "视觉自然度", "severity": "L1"}
        ],
        "note": "室内书桌与电脑显示器周边弱光环境轻微偏暗泛冷，色调过渡略显生硬。"
    },
    3047: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "C", "name": "错色", "severity": "L1"}
        ],
        "note": "羊圈绵羊白色皮毛与干草料全景严重恶性烘烤泛黄泛焦，木围栏偏暗。"
    },
    3048: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "街边鲜艳大红色金属消火栓严重脱色退化呈现浅粉灰冷色，水泥路面泛暗。"
    },
    3059: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "骑警身后路人原本鲜艳的亮粉红色上衣被彻底恶性错涂为亮青蓝色伪色。"
    },

    # Sheet 02 (Tasks 3071, 3077, 3087, 3095, 3099, 3121)
    3071: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "古典钟楼红砖立面与石雕装饰微弱偏暗泛冷，砖红色度略显不足。"
    },
    3077: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "边牧犬背着的鲜艳宝蓝色宠物背包彻底脱色为深黑灰色，草坪绿意不足。"
    },
    3087: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "F", "name": "视觉自然度", "severity": "L1"}
        ],
        "note": "网球场看台观众席与防风挡网局部微弱偏暗泛灰，冷暖对比微弱平淡。"
    },
    3095: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "盘装煎肉排与配菜微弱泛暗偏焦，新鲜柠檬片黄度轻微欠饱和。"
    },
    3099: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "F", "name": "视觉自然度", "severity": "L1"}
        ],
        "note": "长颈鹿与草地泥土环境色温微弱偏暗泛红黄，阴影层次略显生硬。"
    },
    3121: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "运河对岸欧式古典建筑红砖外墙大面积脱色为冷灰水泥色，河水微暗。"
    },

    # Sheet 03 (Tasks 3124, 3133, 3140, 3143, 3160, 3187)
    3124: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "剧院建筑正立面砖红粉橘色墙面严重脱色褪白为冷白水泥墙，广场地砖偏冷。"
    },
    3133: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "C", "name": "错色", "severity": "L1"}
        ],
        "note": "豪华客厅皮质沙发与米白地毯全景恶性烘烤偏色为浑浊暖褐土色，墙面发黄。"
    },
    3140: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "车站月台轨道与列车金属侧板微弱偏暗泛冷，黄色警示盲道略欠饱和。"
    },
    3143: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "F", "name": "视觉自然度", "severity": "L1"}
        ],
        "note": "餐桌上烤肉与土豆泥局部阴影微弱偏焦暗，餐盘边缘反光平淡。"
    },
    3160: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "树下行路人员身穿的鲜艳橘红色短袖上衣被恶性错涂为发暗青蓝绿蓝假色。"
    },
    3187: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "滑雪场山体雪道与远处松树林微弱偏暗泛冷灰，雪地高光色阶层次偏平。"
    },

    # Sheet 04 (Tasks 3188, 3199, 3201, 3214, 3230, 3248)
    3188: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "F", "name": "视觉自然度", "severity": "L1"}
        ],
        "note": "厨房大理石操作台面与不锈钢水槽反光微弱偏暖泛黄，材质光泽略平。"
    },
    3199: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "滑雪女孩身穿的鲜艳亮橙红滑雪手套严重脱色退化为浅灰白色，雪板微暗。"
    },
    3201: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "客运大巴车身下部鲜艳红色涂装严重欠饱和退化为发暗粉紫色，车窗发暗。"
    },
    3214: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "D", "name": "偏色", "severity": "L2"}
        ],
        "note": "现代卫生间米白墙面与原木置物架被恶性错涂为冰冷深青蓝死冷色调，木色尽失。"
    },
    3230: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "停靠在站台旁的双层客车车头局部金属漆面微弱偏冷发暗，车灯色泽欠饱和。"
    },
    3248: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "沙发靠垫深红布艺面料脱色发暗为灰褐色，木质茶几纹理偏冷发灰。"
    },

    # Sheet 05 (Tasks 3261, 3274, 3282, 3283, 3324, 3331)
    3261: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L1"},
            {"id": "D", "name": "偏色", "severity": "L1"}
        ],
        "note": "古典钟楼石墙与表盘发暗泛冷偏色，建筑外立面暖沙色泽微弱不足。"
    },
    3274: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "C", "name": "错色", "severity": "L1"}
        ],
        "note": "餐盘烤鱼与烤面包表面严重恶性烘烤泛红发焦，白瓷餐盘边缘泛黄。"
    },
    3282: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "F", "name": "视觉自然度", "severity": "L1"}
        ],
        "note": "体感游戏室内白色背景墙面与青年白色T恤严重烘烤泛黄，室内光照失真。"
    },
    3283: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L1"},
            {"id": "D", "name": "偏色", "severity": "L1"}
        ],
        "note": "室内滑雪场远处木屋墙面与雪地反光严重发暗发焦，滑雪设施泛冷发灰。"
    },
    3324: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L1"},
            {"id": "D", "name": "偏色", "severity": "L1"}
        ],
        "note": "聚餐长桌彩色桌布与餐盘水果烘烤发暗，红苹果色泽偏焦红发暗。"
    },
    3331: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "牛棚中小牛红褐色皮毛局部发暗偏冷，干草料金黄色调微弱欠饱和。"
    },

    # Sheet 06 (Tasks 3344, 3354, 3365, 3388, 3399, 3406)
    3344: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "F", "name": "视觉自然度", "severity": "L1"}
        ],
        "note": "黑色机械键盘键帽与深色实木桌面微弱烘烤偏暖泛黄，材质纯黑度不足。"
    },
    3354: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "窗台扶手椅黄色抱枕严重脱色褪白，窗外金秋树林金黄色彩大幅流失。"
    },
    3365: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L1"},
            {"id": "D", "name": "偏色", "severity": "L1"}
        ],
        "note": "哥特式西敏寺大教堂双塔石雕立面微弱偏色发暗，背景阴天泛青灰。"
    },
    3388: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "草地上的绵羊羊毛与草场整体轻微偏暖发暗，草地嫩绿色彩度偏低。"
    },
    3399: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "果蔬拼盘中新鲜红苹果与青菜严重脱色发暗，番茄与绿叶生机彩度流失。"
    },
    3406: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "宠物狗戴着的鲜艳菠萝黄帽子与顶端绿叶严重脱色发暗，黄色调大幅丧失。"
    },

    # Sheet 07 (Tasks 3415, 3425, 3431, 3433, 3436, 3444)
    3415: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "铁板烧餐厅上方橘红色吊灯罩与桌面橙色口布脱色泛黄泛白，暖红光照被削弱。"
    },
    3425: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "背景森林树叶与泥土路面整体轻微偏暗偏冷，马车红木色车斗轻微脱色。"
    },
    3431: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "列车车身MARC标志鲜艳橘红与宝蓝涂装线条脱色暗淡，橙红腰线褪色脱白。"
    },
    3433: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "旅馆双人卧室地面深红地毯与床头红色软包脱色为暗灰褐土色，红调完全丢失。"
    },
    3436: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "宴会果盘中间金黄色菠萝与香蕉色泽偏暗发乌，顶部草莓与红苹果红色欠饱和。"
    },
    3444: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "温馨客厅室内暖黄灯光环境整体偏冷偏灰，实木橱柜与地毯暖色温严重不足。"
    },

    # Sheet 08 (Tasks 3447, 3449, 3477, 3479, 3488, 3491)
    3447: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "客厅红木装饰墙面与室内暖光微弱偏冷偏暗，红木色泽饱和度略显不足。"
    },
    3449: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "F", "name": "视觉自然度", "severity": "L1"}
        ],
        "note": "草原草地与泥土环境微弱偏黄绿偏暖，斑马黑白条纹与地表过渡略显生硬。"
    },
    3477: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "石碑上的浅棕黄色毛绒小熊脱色褪白为灰白冷色，泰迪熊棕黄皮毛严重欠饱和。"
    },
    3479: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "海湾对岸欧式古典建筑群黄色与红砖外墙脱色为冷灰水泥色，暖色彩度大幅丢失。"
    },
    3488: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "列车深宝蓝车体涂装严重发黑偏暗，车头明黄色漆面与宝蓝车身对比生硬。"
    },
    3491: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "八角形STOP交通警示标牌鲜红色脱色发暗呈现灰紫红色，警示底色严重欠饱和。"
    },

    # Sheet 09 (Tasks 544, 623, 712, 731, 772, 856)
    544: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "套房客厅地面鲜艳红花图案地毯脱色发暗呈现枯褐暗黄色，暖橙灯光氛围削弱。"
    },
    623: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "B", "name": "溢色", "severity": "L1"}
        ],
        "note": "红翅黑鹂腹部纯黑羽毛被大面积错涂为深红褐伪色，翅根鲜红斑块向腹部溢色。"
    },
    712: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "F", "name": "视觉自然度", "severity": "L1"}
        ],
        "note": "湖面水体与白天鹅倒影微弱偏暗泛冷，水面涟漪反光层次略显平淡。"
    },
    731: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "典雅双床卧室浅绿黄壁纸与原木地板微弱偏冷发灰，墙面淡雅色彩欠饱和。"
    },
    772: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "人行道红色金属消火栓脱色发暗呈现灰黑暗红色，红砖路面彩度轻微流失。"
    },
    856: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "D", "name": "偏色", "severity": "L2"}
        ],
        "note": "披萨表面金黄奶酪与菌菇馅料严重烘烤发红发焦，饼面整体严重偏红焦化。"
    },

    # Sheet 10 (Tasks 928, 956, 990, 12, 19, 116)
    928: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "露天摆放的马桶群右下角浅蓝色马桶座便器被恶性错涂为亮粉红色伪色。"
    },
    956: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "F", "name": "视觉自然度", "severity": "L2"}
        ],
        "note": "摩托车前脸与侧包围原本标志性的荧光草绿车漆被恶性错涂为深红色伪色。"
    },
    990: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "客厅墨绿色布艺双人沙发脱色发暗呈现灰黑色，地毯与实木茶几暖调削弱。"
    },
    12: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "D", "name": "偏色", "severity": "L2"}
        ],
        "note": "浅青灰色床头柜被严重烘烤错涂为金黄暖木色，室内地面与墙面严重泛黄。"
    },
    19: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "早餐水果碗中鲜红西瓜果肉完全脱色褪白为苍白浅粉色，新鲜果肉色度全失。"
    },
    116: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "D", "name": "偏色", "severity": "L2"}
        ],
        "note": "骑三轮车老人所穿深色外套被错涂为发暗紫红色伪色，茶餐厅街景过度偏红偏暗。"
    },

    # Sheet 11 (Tasks 200, 239, 311, 355, 372, 382)
    200: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "八角形ALTO红色交通停步标牌被恶性错涂为暗黄橙色伪色，红色警示完全丢失。"
    },
    239: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E1", "name": "过饱和", "severity": "L1"}
        ],
        "note": "露天马桶群右侧多只白色马桶座便器被恶性错涂为柠檬黄与亮绿色伪色斑块。"
    },
    311: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "F", "name": "视觉自然度", "severity": "L2"}
        ],
        "note": "法网红土球场右半部砖红红土地面被恶性错涂为蓝灰色硬地球场伪色，割裂违和。"
    },
    355: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "餐厅室内暖黄聚餐光照系统性偏冷偏青蓝，餐盘披萨与人物肤色暖调不足。"
    },
    372: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "猫咪窝垫与植物盆栽发暗脱色呈现死灰冷蓝色，绿植与猫毛饱和度偏低。"
    },
    382: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "自拍女子身穿的砖红色长袖卫衣脱色发暗呈现灰粉紫冷调，卫衣鲜红色调流失。"
    },

    # Sheet 12 (Tasks 462, 466, 474, 3009, 3037, 3061)
    462: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "D", "name": "偏色", "severity": "L2"}
        ],
        "note": "机库前停放的红色皮卡车脱色为灰黑色死色，乡村碎石地面与天空泛冷发青蓝。"
    },
    466: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "C", "name": "错色", "severity": "L1"}
        ],
        "note": "烘焙披萨与木质餐桌全图严重偏红黄焦化，表面菌菇焦红发黑过度烘烤。"
    },
    474: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "自拍女孩与长毛猫皮毛全图系统性偏冷青蓝调，人物肤色与猫毛暖色温被剥夺。"
    },
    3009: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "C", "name": "错色", "severity": "L2"}
        ],
        "note": "下方作为嘴巴的一排翠绿青香蕉被恶性错涂为鲜红色伪色，上方白南瓜错涂为明黄。"
    },
    3037: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "甜甜圈表面丰富的彩色水果麦圈彻底脱色为单一灰白色，彩色度完全丢失。"
    },
    3061: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "盛放千层蛋糕的嫩黄绿色玻璃餐盘脱色为纯白冷盘，甜点配饰色彩欠饱和。"
    },

    # Sheet 13 (Tasks 3134, 3206, 3223, 3270, 3359, 3398)
    3134: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "复古行李箱内原本鲜艳的金黄、亮橙各色彩球彻底脱色褪白为灰白冷球，箱体发灰。"
    },
    3206: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "商场步行街地面反光与橱窗灯光整体偏冷发灰，室内暖黄色温严重欠饱和。"
    },
    3223: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "F", "name": "视觉自然度", "severity": "L1"}
        ],
        "note": "网球硬地外场蓝色地坪与看台背板微弱偏暗泛深，场馆大面积色彩过渡略显生硬。"
    },
    3270: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "冲浪店橱窗内彩色冲浪板与左侧海滩彩色招贴壁画严重脱色发暗，彩度大幅流失。"
    },
    3359: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "草地上极醒目的荧光亮粉红色飞盘彻底脱色漂白为惨白塑料盘，右侧红色背包发黑。"
    },
    3398: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "街头古典红砖建筑物与天空整体微弱偏灰偏暖，红砖色度与绿树层次微弱不足。"
    },

    # Sheet 14 (Tasks 3458, 3460, 3461, 3499, 4452, 510)
    3458: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "现代厨房原木色橱柜门面脱色发暗呈现冷灰色，木质纹理暖色调严重流失。"
    },
    3460: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "海报中央标志性的大红涂装流线型机车被恶性错涂为深蓝色伪色，文字脱色。"
    },
    3461: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "民族风手工刺绣毯子上的鲜红色与明黄色滚边脱色发暗，织物色彩欠饱和。"
    },
    3499: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "舞台大红地毯与背景展板整体偏紫偏暗，舞者翠绿演出裤袜与彩伞彩度不足。"
    },
    4452: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "C", "name": "错色", "severity": "L1"}
        ],
        "note": "现代金属卫生间马桶与墙面严重烘烤偏暖偏暗黄，不锈钢金属质感被黄化失真。"
    },
    510: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "棒球场红土内野地面严重脱色为发暗灰泥色，跑道红土与蓝白球衣色度偏低。"
    },

    # Sheet 15 (Tasks 516, 527, 530, 533, 541, 558)
    516: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "背景室内茂密绿植严重脱色发黑灰，聚餐金黄披萨包装盒色彩严重不足。"
    },
    527: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "D", "name": "偏色", "severity": "L2"}
        ],
        "note": "平底锅中洋葱与炒肉被恶性错涂为深红褐色伪色，整道菜肴偏红焦化失真。"
    },
    530: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "D", "name": "偏色", "severity": "L2"}
        ],
        "note": "厨房原木色吊柜被错涂为发暗灰紫褐色伪色，墙面与橱柜整体色温系统性偏冷偏紫。"
    },
    533: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L1"},
            {"id": "D", "name": "偏色", "severity": "L1"}
        ],
        "note": "沙发上天蓝色抱枕脱色发灰暗淡，室内弱光环境下沙发与背景微弱偏暗泛冷。"
    },
    541: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "客厅原木实木地板与真皮沙发整体偏冷偏灰，地面与家具暖色调欠饱和。"
    },
    558: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "门廊背景明亮天蓝色木板墙严重脱色褪白为灰白色，门廊木墙蓝色彩度大幅丢失。"
    },

    # Sheet 16 (Tasks 567, 570, 583, 588, 591, 596)
    567: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "玩体感游戏的男子身穿的草绿色毛衣被彻底脱色为浅灰白色，草绿色彩完全丢失。"
    },
    570: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "前方小男孩身穿的鲜红色长袖卫衣被恶性错涂为深青灰色伪色，红色彩完全剥夺。"
    },
    583: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E1", "name": "过饱和", "severity": "L2"}
        ],
        "note": "棒球场原本平整的泥土内野被恶性错涂为大片荧光翠绿草坪伪色，刺目失真。"
    },
    588: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L1"},
            {"id": "D", "name": "偏色", "severity": "L1"}
        ],
        "note": "红色消火栓金属构件脱色发暗呈现灰黑调，路面与建筑背景微弱偏冷。"
    },
    591: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E1", "name": "过饱和", "severity": "L2"}
        ],
        "note": "林间原本干枯黄褐色的落叶地面被恶性错涂为大片鲜红与艳绿伪色，过度饱和。"
    },
    596: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "香煎三文鱼诱人的金黄焦糖色泽彻底脱色为苍白冷肉色，熟鱼肉暖色大幅流失。"
    },

    # Sheet 17 (Tasks 598, 599, 600, 603, 627, 629)
    598: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "走廊深处厨房暖黄照明系统性偏冷偏白，实木地板温暖光照饱和度丧失。"
    },
    599: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "D", "name": "偏色", "severity": "L2"}
        ],
        "note": "棒球场原本冷灰色的碎石内野硬地被恶性错涂为大片深红褐色伪色，偏红严重。"
    },
    600: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "餐盘食物与马克杯受暖光照射整体严重偏冷偏蓝，烤肉与蔬菜暖色彩度不足。"
    },
    603: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "E1", "name": "过饱和", "severity": "L1"}
        ],
        "note": "展台背景墙与强光照明整体严重偏洋红泛紫，形成刺目的假色光污染。"
    },
    627: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "F", "name": "视觉自然度", "severity": "L1"}
        ],
        "note": "盘中红酒炖肉与烤土豆色调微弱偏暗泛黄，烤肉光泽层次略显平淡。"
    },
    629: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "下方货架上的一整筐金黄色香蕉被恶性错涂为深红褐色伪色，上方蔬菜发暗。"
    },

    # Sheet 18 (Tasks 632, 636, 637, 639, 642, 643)
    632: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "下方大面积金黄色麦田农田彻底脱色蜕变为暗灰泥土色，成熟麦田金色全失。"
    },
    636: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "D", "name": "偏色", "severity": "L1"}
        ],
        "note": "路口路灯暖橙黄色照明被错涂为冷白光，夜间街景局部暗部轻微偏紫红。"
    },
    637: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "E1", "name": "过饱和", "severity": "L1"}
        ],
        "note": "吃热狗女孩全图环境严重烘烤偏暖偏橙红，热狗香肠与衣物暖色略显过冲。"
    },
    639: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "D", "name": "偏色", "severity": "L2"}
        ],
        "note": "电脑桌上的鼠标与外设被恶性错涂为金黄色伪色，男子深色上衣严重偏紫红。"
    },
    642: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "男子身穿的清爽天蓝色短袖T恤彻底脱色蜕变为灰黑色，彩色碎花布垫脱色发灰白。"
    },
    643: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "F", "name": "视觉自然度", "severity": "L2"}
        ],
        "note": "欧式卧室原本暖米黄色的典雅壁纸与窗帘被恶性错涂为大片刺目荧光翠绿伪色。"
    },

    # Sheet 19 (Tasks 646, 647, 658, 659, 660, 667)
    646: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "F", "name": "视觉自然度", "severity": "L1"}
        ],
        "note": "双胞胎幼童肤色与卫生间瓷砖整体系统性偏紫红发灰，血色呈现不均匀。"
    },
    647: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L3"},
            {"id": "E1", "name": "过饱和", "severity": "L2"}
        ],
        "note": "繁华夜市街景全景建筑与霓虹广告被严重恶性烘烤为通体深橙红泛黄，极其失真。"
    },
    658: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "外卖自行车车尾披萨外卖保温箱鲜红色脱色发暗变灰紫，黄色车架彩度不足。"
    },
    659: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "古典宴会厅室内拱窗与墙壁整体严重偏暖偏橙红，家具冷暖对比弱化。"
    },
    660: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "C", "name": "错色", "severity": "L1"}
        ],
        "note": "舞台聚光灯照明与杂技演员全身整体严重偏洋红泛暖，纯白演出服烘烤泛红。"
    },
    667: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E1", "name": "过饱和", "severity": "L2"}
        ],
        "note": "行李箱底部两排鲜艳抹茶绿包装零食被恶性错涂为刺目大红橙色伪色，过度饱和。"
    },

    # Sheet 20 (Tasks 670, 682, 685, 692, 701, 737)
    670: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "展厅内标志性的金黄色陈列展台被彻底脱色漂白为惨白灰台，爱心红色脱色。"
    },
    682: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "路面金属防滑盖板与沥青地面严重偏冷偏青蓝，黄色消火栓色泽暗淡。"
    },
    685: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E1", "name": "过饱和", "severity": "L2"}
        ],
        "note": "荒漠原本干燥土黄色的碎石沙地被恶性错涂为大片刺目荧光翠绿草地伪色。"
    },
    692: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E1", "name": "过饱和", "severity": "L1"}
        ],
        "note": "户外右侧浅色古典木构设施被恶性错涂为大红色伪色，红色块过于刺目。"
    },
    701: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "站台尽头鲜红色铁架安全挡板脱色发暗呈现灰黑暗红，黄色盲道偏暗。"
    },
    737: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "车厢内饰暖黄顶棚与乘客衣物环境整体偏冷偏灰，车厢内部暖色调欠饱和。"
    },

    # Sheet 21 (Tasks 748, 751, 755, 768, 775, 776)
    748: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "厨房右侧鲜艳的薄荷绿墙面与橱柜被恶性错涂为深宝蓝色伪色，烤箱金属微灰。"
    },
    751: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "F", "name": "视觉自然度", "severity": "L1"}
        ],
        "note": "草地网球场与裁判席遮阳伞局部微弱偏暗泛黄，草坪细腻色阶层次略显平淡。"
    },
    755: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "背景花坛中盛开的洋红色花朵严重脱色发黑灰，红色宠物牵引绳鲜艳度不足。"
    },
    768: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "铁板烧表面沙拉酱与浓郁酱汁系统性偏冷偏青发灰，煎饼焦糖色泽欠饱和。"
    },
    775: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "左侧极其醒目的大红色特种消防车辆被恶性错涂为墨绿黑灰假色，红漆被剥夺。"
    },
    776: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E1", "name": "过饱和", "severity": "L2"}
        ],
        "note": "生日蛋糕基底奶油被恶性错涂为大片刺目大红色与高饱和黄斑伪色，严重过冲。"
    },

    # Sheet 22 (Tasks 786, 788, 793, 797, 806, 810)
    786: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E1", "name": "过饱和", "severity": "L2"}
        ],
        "note": "铺满地面的整片金黄色柑橘与柠檬被恶性错涂为紫红与洋红色伪色，过度饱和。"
    },
    788: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L1"},
            {"id": "D", "name": "偏色", "severity": "L1"}
        ],
        "note": "餐桌上绿色塑料饮料杯色彩轻微过冲，货架背景与人物肤色局部微弱偏冷发青。"
    },
    793: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E1", "name": "过饱和", "severity": "L2"}
        ],
        "note": "厨房左侧与背景墙面被恶性错涂为刺目的荧光翠绿伪色，大厨身旁红砖发焦。"
    },
    797: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "卫生间墙面淡雅浅黄绿色小瓷砖脱色褪白为灰暗冷白色，温润黄绿色彩完全丧失。"
    },
    806: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "婚礼宴会现场浪漫温馨的暖粉橙色光照系统性偏冷偏白，烛光暖色温欠饱和。"
    },
    810: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "雪场白雪与女孩滑雪服整体偏冷偏青蓝，雪道夕阳暖反光被大面积剥夺。"
    },

    # Sheet 23 (Tasks 813, 817, 830, 832, 850, 859)
    813: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E1", "name": "过饱和", "severity": "L1"}
        ],
        "note": "中间悬挂的鲜红色塑料水桶被恶性错涂为浅蓝紫粉色伪色，悬挂香蕉过冲。"
    },
    817: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "F", "name": "视觉自然度", "severity": "L1"}
        ],
        "note": "蓝色床单与女子肤色局部微弱偏冷发暗，面部高光与阴影过渡略生硬。"
    },
    830: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "D", "name": "偏色", "severity": "L2"}
        ],
        "note": "厨房原本浅灰白色的灶台与墙壁被恶性烘烤错涂为大片粉红色伪色，全景偏红。"
    },
    832: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "深蓝色健身瑜伽球与电脑屏幕反光严重偏紫红，球体纯正宝蓝色相受损。"
    },
    850: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L1"},
            {"id": "D", "name": "偏色", "severity": "L1"}
        ],
        "note": "网球选手所穿深宝蓝运动短袖偏紫发暗，选手面部肤色微弱偏暗泛红。"
    },
    859: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "D", "name": "偏色", "severity": "L2"}
        ],
        "note": "便当盒外壳天蓝色被恶性错涂为深紫蓝色，盒内蔬菜水果整体偏焦红偏暗。"
    },

    # Sheet 24 (Tasks 866, 870, 887, 893, 896, 920)
    866: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E1", "name": "过饱和", "severity": "L2"}
        ],
        "note": "碗中紫甘蓝与新鲜蔬菜被恶性错涂为大片刺目荧光亮紫色伪色，多重色块过饱和。"
    },
    870: {
        "defects": [
            {"id": "E1", "name": "过饱和", "severity": "L1"},
            {"id": "D", "name": "偏色", "severity": "L1"}
        ],
        "note": "碗中切片黄柠檬局部饱和度偏高微刺目，红苹果与绿叶局部微弱偏暗泛冷。"
    },
    887: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "D", "name": "偏色", "severity": "L2"}
        ],
        "note": "客厅原本清爽优雅的天蓝色真皮沙发被恶性烘烤错涂为暗黄褐色伪色，墙面发黄。"
    },
    893: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "冰场护栏经典可口可乐Coca-Cola大红广告牌严重脱色为灰褐脏红，赛道标志欠饱和。"
    },
    896: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "前方平整的大面积翠绿草坪被彻底脱色为浅灰紫色死地，天然绿色彻底剥夺。"
    },
    920: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "D", "name": "偏色", "severity": "L1"}
        ],
        "note": "右侧男子身穿的宝蓝色夏威夷印花短袖被错涂为暗沉深紫蓝色，白墙微泛暖黄。"
    },

    # Sheet 25 (Tasks 924, 941, 950, 954, 959, 960)
    924: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "D", "name": "偏色", "severity": "L2"}
        ],
        "note": "透明玻璃罐与背景原本清澈的冷青蓝色被烘烤错涂为发暗脏黄色，色彩偏脏。"
    },
    941: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "车载摆件夏威夷草裙舞女郎鲜艳草绿色草裙与底座彻底脱色为浅灰白，彩度丧失。"
    },
    950: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "D", "name": "偏色", "severity": "L1"}
        ],
        "note": "度假村酒吧吧台台面被错涂为高饱和焦橙色伪色，茅草屋顶与木质结构偏红发焦。"
    },
    954: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "练习棒球的小女孩身穿的明黄色短袖T恤彻底脱色蜕变为惨淡灰白色，内野泥土脱色。"
    },
    959: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "D", "name": "偏色", "severity": "L2"}
        ],
        "note": "老旧卫生间原本涂刷的天蓝色油漆墙面被恶性烘烤错涂为发脏暗黄泥浆色伪色。"
    },
    960: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E1", "name": "过饱和", "severity": "L1"}
        ],
        "note": "水果摊底层大堆鲜艳饱满的橙红色鲜橙被恶性错涂为青绿色伪色，违和失真。"
    },

    # Sheet 26 (Tasks 966, 972, 976, 981, 983, 985)
    966: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "街角原本金黄暖砖红色的古典大楼外墙被彻底脱色冷化为青灰色水泥楼，红砖色度全失。"
    },
    972: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "女士身穿的鲜艳湖水天蓝色短袖T恤被彻底脱色蜕变为惨淡灰白汗衫，绿托盘发灰。"
    },
    976: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "红玫瑰花瓣与草绿背景细网局部轻微偏暗偏冷，鲜艳玫瑰红色略显暗淡。"
    },
    981: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "D", "name": "偏色", "severity": "L1"}
        ],
        "note": "客房内醒目的暖金黄色落地窗帘脱色发暗呈现灰土色，室内整体暖黄色温被削弱。"
    },
    983: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "背景墙面鲜红色警示宣传海报展板严重脱色为浅土灰白色，红色宣传板色度丢失。"
    },
    985: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1"},
            {"id": "E1", "name": "过饱和", "severity": "L1"}
        ],
        "note": "玻璃花瓶中盛开的洋红菊花局部偏深偏紫，中心花蕊与局部花瓣色度过冲。"
    },

    # Sheet 27 (Task 996)
    996: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3"},
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "背景生机盎然的翠绿树林被恶性烘烤脱色为焦黄枯叶色伪色，大象皮毛严重泛黄焦化。"
    }
}

def main():
    print(f"Applying visual audit fixes for {len(ROUND4_FIXES)} tasks in Round 4...")

    with open(ALL_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)
    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    all_anns = all_data["annotations"]
    clean_anns = clean_data["annotations"]

    all_map = {ann["human_review"]["task_id"]: ann for ann in all_anns}
    clean_map = {ann["human_review"]["task_id"]: ann for ann in clean_anns}

    applied_count = 0
    for tid, fix_info in ROUND4_FIXES.items():
        if tid in all_map:
            ann_all = all_map[tid]
            ann_clean = clean_map[tid]

            raw_defects = fix_info["defects"]
            note = fix_info["note"]

            # 标准化缺陷对象，必须严格包含 id, name, severity, description
            formatted_defects = []
            for d in raw_defects:
                d_id = d["id"]
                formatted_defects.append({
                    "id": d_id,
                    "name": TAXONOMY.get(d_id, "错色"),
                    "severity": d.get("severity", "L1"),
                    "description": d.get("description", note)
                })

            ann_all["defects"] = formatted_defects
            ann_all["review_note"] = note
            ann_all["review_status"] = "已核验"

            ann_clean["defects"] = formatted_defects
            ann_clean["review_note"] = ""
            ann_clean["review_status"] = "已核验"

            if not formatted_defects:
                ann_all["reviewed_score"] = 5.0
                ann_all["needs_rescoring"] = False
                ann_clean["reviewed_score"] = 5.0
                ann_clean["needs_rescoring"] = False
            elif any(d.get("id") == "A" for d in formatted_defects):
                ann_all["reviewed_score"] = 1.0
                ann_all["needs_rescoring"] = False
                ann_clean["reviewed_score"] = 1.0
                ann_clean["needs_rescoring"] = False
            else:
                ann_all["reviewed_score"] = None
                ann_all["needs_rescoring"] = True
                ann_clean["reviewed_score"] = None
                ann_clean["needs_rescoring"] = True

            applied_count += 1
        else:
            print(f"Warning: Task {tid} not found in annotations!")

    print(f"Successfully applied fixes to {applied_count} / {len(ROUND4_FIXES)} tasks!")

    with open(ALL_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    with open(CLEAN_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)

    print("Both all.json and clean.json updated successfully!")

if __name__ == "__main__":
    main()
