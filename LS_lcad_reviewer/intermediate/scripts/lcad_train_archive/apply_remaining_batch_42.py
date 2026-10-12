import json
import os
import subprocess

# 1. 定义 Batch 42 (任务 8328 ~ 8524 共 120 个任务) 的全量精确审核定物字典
reviews = {
    # === Sheet 01 ===
    8328: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "马术场地沙土地面与周围看台大面积浸染失真偏暗的冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "场地中奔跑的骏马棕红毛发及骑手衣物略显欠饱和褪色发暗。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "沙土冷蓝调与骑手环境光影对比生硬不自然。"}
        ],
        "note": "马术场地沙土地面与周围看台大面积浸染失真偏暗的冷青蓝偏色，骏马棕红毛发欠饱和褪色发暗（D-L2, E2-L1, F-L1）。"
    },
    8329: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "桌面上摆放的生日庆祝蛋糕表面原本清爽的浅蓝与白色奶油装饰被颠覆性严重错涂为过度浓艳刺眼的荧光深洋红紫色伪色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "餐桌托盘与周围背景阴影微染深暗红紫偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "蛋糕表面洋红紫色涂层色彩饱和度极度浓烈溢出。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "蛋糕异色严重违背常规食品真实感。"}
        ],
        "note": "桌面上摆放的生日庆祝蛋糕表面原本清爽的浅蓝与白色奶油装饰被颠覆性严重错涂为过度浓艳刺眼的荧光深洋红紫色伪色（C-L3, D-L1, E1-L2, F-L2）。"
    },
    8330: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "铁道内燃机车车头正面标志性的明黄色金属涂装被大面积严重脱色错涂为暗淡灰白淡黄色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "铁轨碎石路基与车身暗部微染冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "机车车头亮黄涂装严重脱色欠饱和。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "机车涂装色彩暗淡削弱工业质感。"}
        ],
        "note": "铁道内燃机车车头正面标志性的明黄色金属涂装大面积欠饱和严重脱色褪变为暗淡灰白淡黄色（C-L2, D-L1, E2-L2, F-L1）。"
    },
    8333: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "林地前斑马黑白皮毛交界处及地面泥土略微浸染轻微红褐色暖偏色。"}
        ],
        "note": "林地前斑马黑白皮毛交界处及地面泥土略微浸染轻微红褐色暖偏色（轻度偏色 D-L1）。"
    },
    8334: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内地面木质地板与运动鞋表面大面积浸染暗冷灰青色偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "地面上玩耍的幼猫毛发略显欠饱和偏冷发灰。"}
        ],
        "note": "室内地面木质地板与运动鞋表面大面积浸染暗冷灰青色偏色，幼猫毛发略显欠饱和偏冷（D-L1, E2-L1）。"
    },
    8335: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "广场水池中陈列的艺术雕塑花瓣表面原本淡雅色彩被大面积错染为深洋红紫杂色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "雕塑基座与周围水池大面积浸染失真偏暗的冷青紫偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "雕塑花瓣局部洋红色过饱和浓艳。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "公共雕塑色彩对比突兀不够自然。"}
        ],
        "note": "广场水池中陈列的艺术雕塑花瓣表面大面积浸染失真偏浓艳的深洋红紫偏色与杂色（C-L2, D-L2, E1-L1, F-L2）。"
    },

    # === Sheet 02 ===
    8336: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8337: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白瓷餐盘中的金属刀叉表面及餐具边缘色彩略显欠饱和褪色偏暗冷灰。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "盘中盛放的面包食物略显暗淡缺乏刚出炉的暖黄光泽。"}
        ],
        "note": "白瓷餐盘中的金属刀叉表面及餐具边缘色彩略显欠饱和褪色偏暗冷灰（D-L1, E2-L1）。"
    },
    8339: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8346: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "手持相机男子身穿的西装外套面料与面部阴影大面积浸染失真深重的深红紫冷偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "男子身后木门与西装反光局部过度浓艳发红。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "深红紫阴影破坏人物自然肤色与衣物质感。"}
        ],
        "note": "手持相机男子身穿的西装外套面料与面部阴影大面积浸染失真深重的深红紫冷偏色（D-L2, E1-L1, F-L2）。"
    },
    8347: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "网球场上网球选手面部肤色及手持网球拍手柄局部略显偏暗冷灰色调。"}
        ],
        "note": "网球场上网球选手面部肤色及手持网球拍手柄局部略显偏暗冷灰色调（轻度偏色 D-L1）。"
    },
    8348: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },

    # === Sheet 03 ===
    8350: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "广场后方背景绿化草坪色彩过度浓艳刺眼且局部接近荧光黄绿。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "草地植被饱和度异常过高。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "过于浓绿的草坪与水泥地面显得生硬。"}
        ],
        "note": "广场后方背景绿化草坪色彩过度浓艳刺眼且局部接近荧光黄绿（D-L1, E1-L2, F-L1）。"
    },
    8352: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8353: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8354: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8356: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "快餐柜台后方原本温暖中性的室内墙壁与金属操作台面被颠覆性严重错涂为大面积浓艳刺眼的亮天青蓝色伪色。"},
            {"id": "D", "name": "偏色", "severity": "L3", "description": "柜台前方点餐区地面大面积浸染失真深重的青蓝冷偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "青蓝色墙面色彩浓度严重溢出。"},
            {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "室内环境大面积刺目青蓝色彻底破坏餐厅真实氛围。"}
        ],
        "note": "快餐柜台后方原本温暖中性的室内墙壁与金属操作台面被颠覆性严重错涂为大面积浓艳刺眼的亮天青蓝色伪色（C-L3, D-L3, E1-L2, F-L3）。"
    },
    8357: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "机场跑道外侧原本干旱浅黄色的沙土地面被大面积严重错涂为异常草绿色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "跑道水泥路面阴影微染冷青蓝偏色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "沙土地面泛绿违背机场干旱跑道地貌特征。"}
        ],
        "note": "机场跑道外侧原本干旱浅黄色的沙土地面被大面积严重错涂为异常草绿色（C-L2, D-L2, F-L2）。"
    },

    # === Sheet 04 ===
    8358: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8359: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8361: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8363: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8364: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "花瓶中插置的花枝原本娇艳的粉红色花瓣大面积欠饱和严重脱色褪变为苍白灰白色死色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "花瓶暗部与衬托绿叶微染暗冷灰色调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "粉红花朵几乎彻底脱色失去生机。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "花朵褪色失去插花鲜活感。"}
        ],
        "note": "花瓶中插置的花枝原本娇艳的粉红色花瓣大面积欠饱和严重脱色褪变为苍白灰白色死色（C-L2, D-L1, E2-L2, F-L1）。"
    },
    8365: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "盛放蔬菜奶油浓汤的陶瓷碗外壁原本清新的浅薄荷绿色被大面积错染为失真偏浓艳的深洋红紫色偏色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "餐桌托盘与餐具周围浸染深重红紫暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "汤碗洋红紫涂层饱和度偏高。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "餐具严重偏紫破坏美食就餐氛围。"}
        ],
        "note": "盛放蔬菜奶油浓汤的陶瓷碗外壁原本清新的浅薄荷绿色被大面积错染为失真偏浓艳的深洋红紫色偏色（C-L3, D-L2, E1-L1, F-L2）。"
    },

    # === Sheet 05 ===
    8366: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8368: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "餐桌大理石盘与意式香肠披萨表面红酱浸染过度偏深红暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "番茄酱与烤肉边缘色彩略显过度浓艳。"}
        ],
        "note": "餐桌大理石盘与意式香肠披萨表面红酱偏深红过饱和（D-L2, E1-L1）。"
    },
    8371: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "木质餐桌与方盒礼品表面大面积欠饱和偏暗冷发灰。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "餐桌周围物品色彩暗淡脱色。"}
        ],
        "note": "木质餐桌与方盒礼品表面欠饱和偏暗冷发灰（D-L1, E2-L1）。"
    },
    8372: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8374: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "卫生间马桶瓷砖与镜面大面积欠饱和褪色偏暗灰冷青色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "浴室内各物件表面反光脱色发灰。"}
        ],
        "note": "卫生间马桶瓷砖与镜面大面积欠饱和褪色偏暗灰冷色（D-L2, E2-L1）。"
    },
    8378: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "壁灯照明下浴室面盆与墙面微偏深暗暖橙色。"}
        ],
        "note": "壁灯照明下浴室面盆与墙面微偏深暗暖橙色（轻度偏色 D-L1）。"
    },

    # === Sheet 06 ===
    8379: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "高山草甸上羊群后方山体植被大面积严重脱色欠饱和错涂为灰暗死色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "山坡草木绿色几乎完全褪尽。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "高山草场色彩发黑缺乏生机。"}
        ],
        "note": "高山草甸上羊群后方山体植被大面积严重脱色欠饱和错涂为灰暗死色（D-L2, E2-L2, F-L2）。"
    },
    8380: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "盘中华夫饼与陶瓷杯表面浸染失真偏暗冷灰偏色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "烘焙糕点表面冷暗无光泽。"}
        ],
        "note": "盘中华夫饼与陶瓷杯表面浸染失真偏暗冷灰偏色（D-L2, F-L1）。"
    },
    8381: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8382: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "海面冲浪者身后原本开阔清澈的浅海海面大面积欠饱和严重脱色错涂为浑浊暗沉灰泥色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "海浪边缘与冲浪板微染暗灰褐色偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "海水原本蔚蓝清澈色彩彻底脱落。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "海面浑浊污秽破坏冲浪水上运动真实感。"}
        ],
        "note": "海面冲浪者身后原本开阔清澈的浅海海面大面积欠饱和严重脱色错涂为浑浊暗沉灰泥色（C-L3, D-L2, E2-L2, F-L2）。"
    },
    8386: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8389: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "海滨休闲露天座椅黄色与橙色金属椅表面色彩过度浓艳刺眼。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "金属椅高光区域色彩浓度偏高。"}
        ],
        "note": "海滨休闲露天座椅黄色与橙色金属椅表面色彩过度浓艳刺眼（D-L1, E1-L1）。"
    },

    # === Sheet 07 ===
    8390: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "厨房白色橱柜台面及瓷砖表面色彩欠饱和微偏冷灰。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "橱柜台面各器皿色彩略显脱色发暗。"}
        ],
        "note": "厨房白色橱柜台面及瓷砖表面色彩欠饱和微偏冷灰（D-L1, E2-L1）。"
    },
    8391: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8393: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "卧室双人床红白条纹床单织物表面大面积浸染失真红棕暖偏色。"}
        ],
        "note": "卧室双人床红白条纹床单织物表面大面积浸染失真红棕暖偏色（中度偏色 D-L2）。"
    },
    8394: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "走廊合影人群西装与地面大面积浸染失真偏暗冷青偏色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "人物肤色与冷青地面对比生硬。"}
        ],
        "note": "走廊合影人群西装与地面大面积浸染失真偏暗冷青偏色（D-L2, F-L1）。"
    },
    8396: {
        "status": "revised",
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "沙滩海鸟身后原本蔚蓝晴空大面积几乎彻底脱色为纯灰白黑白灰度，严重欠饱和。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "天空几乎完全黑白化失去色彩感。"}
        ],
        "note": "沙滩海鸟身后原本蔚蓝晴空大面积几乎彻底脱色为纯灰白黑白灰度，严重欠饱和（E2-L3, F-L2）。"
    },
    8399: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "客厅布艺沙发与窗帘大面积浸染失真发暗黄褐偏色。"}
        ],
        "note": "客厅布艺沙发与窗帘大面积浸染失真发暗黄褐偏色（中度偏色 D-L2）。"
    },

    # === Sheet 08 ===
    8401: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8402: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8403: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "雪地滑雪者身穿的亮黄色防风外套被大面积严重脱色错涂为灰暗浅军绿色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "雪坡阴影与雪具微染冷青色偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "滑雪外套鲜艳黄色褪变发灰。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "滑雪外套色彩暗淡缺乏运动服饰醒目质感。"}
        ],
        "note": "雪地滑雪者身穿的亮黄色防风外套被大面积严重脱色错涂为灰暗浅军绿色（C-L2, D-L1, E2-L2, F-L1）。"
    },
    8404: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "厨房操作台厨师白色工作服及案板食物浸染过度浓艳深红偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "台面食材酱料饱和度过高。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "工作服泛深红显得反常不自然。"}
        ],
        "note": "厨房操作台厨师白色工作服及案板食物浸染过度浓艳深红偏色（D-L1, E1-L2, F-L1）。"
    },
    8407: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "沙滩海浪背景原本纯净湛蓝的晴空与海水被颠覆性错涂为大面积浓艳刺眼的洋红紫与死黄杂色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "沙滩与海浪大面积浸染失真偏暗的紫红偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "洋红色天空浓度异常溢出。"},
            {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "海天严重变色彻底丧失海滨风景真实度。"}
        ],
        "note": "沙滩海浪背景原本纯净湛蓝的晴空与海水被颠覆性错涂为大面积浓艳刺眼的洋红紫与死黄杂色（C-L3, D-L2, E1-L2, F-L3）。"
    },
    8411: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白瓷盘中盛放的热炒牛肉与青菜配菜表面色彩过度浓艳刺眼。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "牛肉酱汁与绿叶蔬菜饱和度偏高。"}
        ],
        "note": "白瓷盘中盛放的热炒牛肉与青菜配菜表面色彩过度浓艳刺眼（D-L1, E1-L1）。"
    },

    # === Sheet 09 ===
    8412: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "暗部门洞阴影与地面微染深红褐偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "老旧民居明黄色斑驳外墙涂装色彩过度浓艳刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "墙面色彩对比过强不够自然。"}
        ],
        "note": "老旧民居明黄色斑驳外墙涂装色彩过度浓艳刺眼，暗部门洞阴影与地面微染深红褐偏色（D-L1, E1-L2, F-L1）。"
    },
    8413: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8414: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "竞技场沙土地面与看台背景横幅广告牌大面积浸染失真偏深红偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "沙土地面色彩过度浓艳发红。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "整体色彩层级微受影响。"}
        ],
        "note": "竞技场沙土地面与看台背景横幅广告牌大面积浸染失真偏深红偏色，沙土色彩过度浓艳发红（D-L1, E1-L1, F-L1）。"
    },
    8415: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8420: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8422: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },

    # === Sheet 10 ===
    8423: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "厨房灶台前女子身旁放置的织物衣物浸染失真深蓝紫偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "案板上的面饼局部烘烤焦黄色彩略显过度浓艳。"}
        ],
        "note": "厨房灶台前女子身旁放置的织物衣物浸染失真深蓝紫偏色，案板上的面饼局部烘烤焦黄色彩略显过度浓艳（D-L1, E1-L1）。"
    },
    8424: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8425: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8426: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "空中漂浮的小风筝原本鲜艳的红色涂装被明显错涂为深蓝色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "草地边缘暗部微染冷青色偏色。"}
        ],
        "note": "空中漂浮的小风筝原本鲜艳的红色涂装被明显错涂为深蓝色，草地边缘暗部微染冷青色偏色（C-L2, D-L1）。"
    },
    8428: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "树林前的深绿色街道英文路牌与红色八角形停止路标金属牌表面大面积浸染暗冷灰青色偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "红绿交通标牌色彩略显暗淡欠饱和。"}
        ],
        "note": "树林前的深绿色街道英文路牌与红色八角形停止路标金属牌表面大面积浸染暗冷灰青色偏色，红绿交通标牌色彩略显暗淡欠饱和（D-L1, E2-L1）。"
    },
    8429: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "餐盘中摆放的千层切片蛋糕表面原本温暖可口的橙黄色奶油与果酱被颠覆性严重错涂为诡异冰冷的浅冰蓝与发灰白伪色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "周围餐盘与桌面大面积浸染失真深重的深冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "蛋糕整体色彩欠饱和发冷。"},
            {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "严重违背食品常理与视觉真实感。"}
        ],
        "note": "餐盘中摆放的千层切片蛋糕表面原本温暖可口的橙黄色奶油与果酱被颠覆性严重错涂为诡异冰冷的浅冰蓝与发灰白伪色（C-L3, D-L2, E2-L1, F-L3）。"
    },

    # === Sheet 11 ===
    8430: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8431: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "街头合影人群面部肤色与身穿的条纹外套织物表面大面积浸染失真偏暗的冷灰青色偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "后方游行标语横幅与背景天空色彩略显暗淡欠饱和。"}
        ],
        "note": "街头合影人群面部肤色与身穿的条纹外套织物表面大面积浸染失真偏暗的冷灰青色偏色，后方游行标语横幅与背景天空色彩略显暗淡欠饱和（D-L1, E2-L1）。"
    },
    8432: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8433: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8434: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8436: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "长颈鹿圈舍周围黄色外墙局部错染为暗青杂色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "原本温暖明亮的沙土地面与外墙建筑被大面积浸染失真深重的暗冷青蓝偏色与杂色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "沙地局部严重脱色发冷灰暗。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "整体视觉氛围严重失调。"}
        ],
        "note": "长颈鹿圈舍周围原本温暖明亮的沙土地面与外墙建筑被大面积浸染失真深重的暗冷青蓝偏色与杂色（C-L2, D-L2, E2-L1, F-L2）。"
    },

    # === Sheet 12 ===
    8437: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8438: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "绿草地上立足的翠鸟腹部羽毛与颈侧羽毛被大面积错染为过度浓艳刺眼的深红紫色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "鸟身周围草地微染红褐暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "翠鸟羽毛红色过度浓艳饱和。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "破坏飞禽原本自然生动的羽毛质感。"}
        ],
        "note": "绿草地上立足的翠鸟腹部羽毛与颈侧羽毛被大面积错染为过度浓艳刺眼的深红紫色（C-L2, D-L1, E1-L2, F-L2）。"
    },
    8440: {
        "status": "revised",
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "农场栅栏后方的灌木树林与茂盛草木大面积欠饱和严重脱色褪变为暗淡灰暗的浅灰白死色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "植被层次与画面真实感明显受损。"}
        ],
        "note": "农场栅栏后方的灌木树林与茂盛草木大面积欠饱和严重脱色褪变为暗淡灰暗的浅灰白死色（E2-L2, F-L1）。"
    },
    8442: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "室内客厅墙壁与天花板表面大面积浸染失真偏暗的暖黄褐偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "右侧墙面暖色照明过度浓艳偏深。"}
        ],
        "note": "室内客厅墙壁与天花板表面大面积浸染失真偏暗的暖黄褐偏色，右侧墙面暖色照明过度浓艳偏深（D-L2, E1-L1）。"
    },
    8443: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "瓷砖地面阴影微染冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "卫生间马桶上方的墙面与挂画织物表面大面积欠饱和脱色褪变为冷淡苍白灰阶。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "黑猫周围光影生硬缺乏真实过渡。"}
        ],
        "note": "卫生间马桶上方的墙面与挂画织物表面大面积欠饱和脱色褪变为冷淡苍白灰阶（D-L1, E2-L2, F-L1）。"
    },
    8445: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "拉车黄牛白色背脊皮毛与周围马车遮阳顶棚大面积浸染失真深重的暗红紫暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "背部高光与布料色彩过度浓艳刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "破坏原本自然的牲畜毛皮质感。"}
        ],
        "note": "拉车黄牛白色背脊皮毛与周围马车遮阳顶棚大面积浸染失真深重的暗红紫暖偏色（D-L1, E1-L2, F-L1）。"
    },

    # === Sheet 13 ===
    8447: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "动物园园区内漫步的大象粗糙灰褐色皮肤大面积浸染失真偏暗的红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "象身与后方草木色彩略显过度浓艳。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "破坏原本自然的野生象皮褶皱灰阶质感。"}
        ],
        "note": "动物园园区内漫步的大象粗糙灰褐色皮肤大面积浸染失真偏暗的红棕暖偏色（D-L2, E1-L1, F-L1）。"
    },
    8448: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "婴儿床边摆放的原本棕黄色的毛绒小熊玩偶被颠覆性严重错涂为荧光亮绿与青蓝异色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "面部与床褥微染暖红偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "婴儿身穿的红色连体衣与玩具表面色彩过度浓艳刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "画面视觉真实感明显受损。"}
        ],
        "note": "婴儿床边摆放的原本棕黄色的毛绒小熊玩偶被颠覆性严重错涂为荧光亮绿与青蓝异色（C-L3, D-L1, E1-L2, F-L2）。"
    },
    8450: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "农田菜地中密集成簇的花椰菜深绿叶片大面积偏暗灰冷青色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "叶片欠饱和脱色失去鲜活青绿色泽。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "叶脉细节发虚缺乏生机活力。"}
        ],
        "note": "农田菜地中密集成簇的花椰菜深绿叶片大面积欠饱和褪色偏暗灰冷青色（D-L1, E2-L1, F-L1）。"
    },
    8451: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "烛光晚宴餐桌后方的背景墙面与男士身穿的深色西装大面积浸染失真发暗的冷青蓝偏色与杂色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "烛光暖调被生硬破坏。"}
        ],
        "note": "烛光晚宴餐桌后方的背景墙面与男士身穿的深色西装大面积浸染失真发暗的冷青蓝偏色与杂色（D-L2, F-L1）。"
    },
    8453: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "椅背上方搭挂的原本鲜艳桃粉色的羽绒外套大面积严重脱色错褪变为发暗冷灰白色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "下方双肩包织物表面微染冷青色偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "粉红羽绒外套脱色严重欠饱和。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "破坏整体静物色彩鲜活度。"}
        ],
        "note": "椅背上方搭挂的原本鲜艳桃粉色的羽绒外套大面积欠饱和严重脱色褪变为发暗冷灰白色（C-L2, D-L1, E2-L2, F-L2）。"
    },
    8455: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "旷野树林前的斑马黑白条纹与长颈鹿黄色皮毛斑纹大面积浸染失真偏重的红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "背景枯木林与动物躯体色彩过度浓艳发红。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "破坏野生动物原本自然和谐的色彩观感。"}
        ],
        "note": "旷野树林前的斑马黑白条纹与长颈鹿黄色皮毛斑纹大面积浸染失真偏重的红棕暖偏色（D-L2, E1-L1, F-L1）。"
    },

    # === Sheet 14 ===
    8456: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8457: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "后方林木阴影微染暗褐暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "白色木质围栏旁的明黄色金属消防栓及周围盛开的红色花灌木色彩略显过度浓艳偏深。"}
        ],
        "note": "白色木质围栏旁的明黄色金属消防栓及周围盛开的红色花灌木色彩略显过度浓艳偏深（D-L1, E1-L1）。"
    },
    8458: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8460: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "复古红色观光缆车车头顶部金属构架与挡风玻璃周围被大面积错染为过度浓艳刺眼的荧光深洋红色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "车厢内饰木质结构浸染深冷暗紫偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "车头洋红漆面浓度严重溢出。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "严重破坏电车原本真实的机械工业质感。"}
        ],
        "note": "复古红色观光缆车车头顶部金属构架与挡风玻璃周围被大面积错染为过度浓艳刺眼的荧光深洋红色（C-L2, D-L1, E1-L2, F-L2）。"
    },
    8463: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8464: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "三层金属下午茶点心架上摆放的水果蛋糕与马卡龙甜品大面积欠饱和严重脱色褪变为冰冷暗淡的灰白淡青死色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "周围瓷质茶具与桌面大面积浸染失真深重的暗冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "甜品色彩几乎彻底脱落失去可口光泽。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "甜品完全丧失可口诱人的新鲜感。"}
        ],
        "note": "三层金属下午茶点心架上摆放的水果蛋糕与马卡龙甜品大面积欠饱和严重脱色褪变为冰冷暗淡的灰白淡青死色（C-L2, D-L2, E2-L2, F-L2）。"
    },

    # === Sheet 15 ===
    8465: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8466: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "热带雨林水池中的母子大象灰褐色象皮表面大面积浸染失真偏暗的红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "后方茂密树林灌木叶片色彩过度浓艳深绿。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "植被与动物皮层色彩层次略显失真。"}
        ],
        "note": "热带雨林水池中的母子大象灰褐色象皮表面大面积浸染失真偏暗的红棕暖偏色（D-L1, E1-L2, F-L1）。"
    },
    8467: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "城市车行道沥青路面与远景高层建筑外立面大面积浸染失真偏暗的暗黄褐偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "前方白色小客车与背景天空色彩略显暗淡欠饱和。"}
        ],
        "note": "城市车行道沥青路面与远景高层建筑外立面大面积浸染失真偏暗的暗黄褐偏色，前方白色小客车与背景天空色彩略显暗淡欠饱和（D-L2, E2-L1）。"
    },
    8468: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8470: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内木地板与背景米黄色墙面微染暖红偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "客厅木质电视柜上的液晶电视屏幕画面色彩略显过度浓艳偏深。"}
        ],
        "note": "客厅木质电视柜上的液晶电视屏幕画面色彩略显过度浓艳偏深，室内木地板与背景米黄色墙面微染暖红偏色（D-L1, E1-L1）。"
    },
    8471: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "厨房白色瓷砖操作台面与窗台金属边框大面积浸染失真偏暗的红棕暖偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "窗外原本明亮的自然采光与浅蓝天光略显欠饱和脱色发灰。"}
        ],
        "note": "厨房白色瓷砖操作台面与窗台金属边框大面积浸染失真偏暗的红棕暖偏色，窗外原本明亮的自然采光与浅蓝天光略显欠饱和脱色发灰（D-L2, E2-L1）。"
    },

    # === Sheet 16 ===
    8476: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8477: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "灶台前沿金属边缘微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "厨房白色电烤炉灶台与金属汤锅表面色彩略显欠饱和脱色发灰。"}
        ],
        "note": "厨房白色电烤炉灶台与金属汤锅表面色彩略显欠饱和脱色发灰（D-L1, E2-L1）。"
    },
    8478: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "实木立柜与地板阴影微染深红褐偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "客厅两侧摆放的皮质单人沙发鲜红皮面色彩过度浓艳刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "局部色彩对比过于生硬突兀。"}
        ],
        "note": "客厅两侧摆放的皮质单人沙发鲜红皮面色彩过度浓艳刺眼（D-L1, E1-L2, F-L1）。"
    },
    8479: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "小鸭儿童车上放置的原本鲜艳的大红色塑料水盆被颠覆性严重错涂为过度浓艳刺眼的荧光深绿色与青黑杂色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "周围草地与推车边缘微染暗红偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "绿色水盆饱和度过度浓烈刺目。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "塑料制品原本纯净鲜艳的玩具色彩严重失真。"}
        ],
        "note": "小鸭儿童车上放置的原本鲜艳的大红色塑料水盆被颠覆性严重错涂为过度浓艳刺眼的荧光深绿色与青黑杂色（C-L3, D-L1, E1-L2, F-L2）。"
    },
    8480: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内阴影微染冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "室内地毯上趴卧的猫咪浅棕色毛发及后方粉色布艺靠垫色彩略显欠饱和脱色偏淡灰。"}
        ],
        "note": "室内地毯上趴卧的猫咪浅棕色毛发及后方粉色布艺靠垫色彩略显欠饱和脱色偏淡灰（D-L1, E2-L1）。"
    },
    8482: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "象舍展区内站在画架前的大象灰褐色皮肤大面积浸染失真偏暗的红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "后方驯兽师身穿的长袍织物与沙土地面色彩过度浓艳发红。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "大象皮层丧失原本自然的灰白褶皱层次。"}
        ],
        "note": "象舍展区内站在画架前的大象灰褐色皮肤大面积浸染失真偏暗的红棕暖偏色（D-L2, E1-L2, F-L1）。"
    },

    # === Sheet 17 ===
    8483: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "雪面阴影微染冷青灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "开阔雪山上的积雪阴影与远景冰川大面积欠饱和脱色偏暗灰冷色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "高山雪景原有的清透冰蓝质感略显发闷。"}
        ],
        "note": "开阔雪山上的积雪阴影与远景冰川大面积欠饱和脱色偏暗灰冷色（D-L1, E2-L1, F-L1）。"
    },
    8485: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "室内客厅左侧白色墙面与地毯表面大面积浸染失真偏暗的暖黄褐偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "右侧落地玻璃门采光区域略显欠饱和发灰偏暗。"}
        ],
        "note": "室内客厅左侧白色墙面与地毯表面大面积浸染失真偏暗的暖黄褐偏色（D-L2, E2-L1）。"
    },
    8488: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "白色陶瓷水果盘中放置的原本翠绿鲜嫩的青苹果表皮大面积欠饱和严重脱色错涂为暗淡黄灰色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "周围橙子表皮微染暗褐暖偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "青苹果脱色失去新鲜青翠感。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "破坏新鲜青果的水灵质感。"}
        ],
        "note": "白色陶瓷水果盘中放置的原本翠绿鲜嫩的青苹果表皮大面积欠饱和严重脱色错涂为暗淡黄灰色（C-L2, D-L1, E2-L1, F-L1）。"
    },
    8491: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8492: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "周围海面水体与背景天空微染深暗冷青蓝偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "海面上漂浮的白色小型木船船身及彩色遮阳伞表面色彩略显过度浓艳。"}
        ],
        "note": "海面上漂浮的白色小型木船船身及彩色遮阳伞表面色彩略显过度浓艳，周围海面水体与背景天空微染深暗冷青蓝偏色（D-L1, E1-L1）。"
    },
    8493: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },

    # === Sheet 18 ===
    8494: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "餐桌木纹与儿童面部阴影大面积微染深暗红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "木桌前就餐的右侧小女孩身穿的粉红背心织物色彩过度浓艳刺眼。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "破坏童装原本清爽柔和的质感。"}
        ],
        "note": "木桌前就餐的右侧小女孩身穿的粉红背心织物色彩过度浓艳刺眼（D-L1, E1-L2, F-L1）。"
    },
    8495: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "窗外原本明朗清爽的蓝天背景被错染为浑浊发黄的暗灰白杂色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "窗台前摆放的插花玻璃瓶与绿植叶片大面积浸染失真偏暗的红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "绿植枝叶色彩过度浓艳发深。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "画面自然采光感严重受损。"}
        ],
        "note": "窗台前摆放的插花玻璃瓶与绿植叶片大面积浸染失真偏暗的红棕暖偏色，窗外蓝天错染黄灰杂色（C-L2, D-L2, E1-L1, F-L2）。"
    },
    8497: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "壁炉暗部微染冷青灰色偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "客厅实木壁炉上方白色装饰柜与米黄色背景墙面大面积欠饱和脱色偏暗灰冷色。"}
        ],
        "note": "客厅实木壁炉上方白色装饰柜与米黄色背景墙面大面积欠饱和脱色偏暗灰冷色（D-L1, E2-L1）。"
    },
    8498: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "快餐托盘中放置的烘焙面包糕点原本金黄松软的表皮被颠覆性严重错涂为诡异发霉般的冰冷浅蓝紫伪色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "周围托盘与台面微染冷青蓝偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "右侧塑料杯装果汁饮品色彩过度浓艳偏深。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "食品色彩严重失真违背常理。"}
        ],
        "note": "快餐托盘中放置的烘焙面包糕点原本金黄松软的表皮被颠覆性严重错涂为诡异发霉般的冰冷浅蓝紫伪色（C-L3, D-L1, E1-L1, F-L2）。"
    },
    8499: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "斑马圈舍内的泥土地面与斑马原本黑白相间的条纹毛皮大面积浸染失真深重的暗黄褐暖偏色。"},
            {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "使得动物毛色与环境光照显得浑浊发暗。"}
        ],
        "note": "斑马圈舍内的泥土地面与斑马原本黑白相间的条纹毛皮大面积浸染失真深重的暗黄褐暖偏色（D-L2, F-L1）。"
    },
    8502: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "街头蛋糕店正门外立面与悬挂的 CAKESHOP 招牌原本温暖明亮的橙黄色木纹涂装被大面积错涂为冰冷生硬的青蓝与暗紫杂色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "橱窗边缘与街道地面大面积浸染失真深重的冷青偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "橱窗展示台色彩欠饱和褪色发冷。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "店面温馨甜品氛围严重失真。"}
        ],
        "note": "街头蛋糕店正门外立面与悬挂的 CAKESHOP 招牌原本温暖明亮的橙黄色木纹涂装被大面积错涂为冰冷生硬的青蓝与暗紫杂色（C-L2, D-L2, E2-L1, F-L2）。"
    },

    # === Sheet 19 ===
    8503: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8505: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "木质切菜案板与桌面大面积浸染失真偏暗的冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "原本温暖的木纹色彩欠饱和褪色发冷灰。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "披萨与沙拉边缘光影生硬。"}
        ],
        "note": "木质切菜案板与桌面大面积浸染失真偏暗的冷青蓝偏色（D-L2, E2-L1, F-L2）。"
    },
    8506: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "奶牛躯体与远景天空微染暗冷灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "暮色草地上的青草植被大面积欠饱和严重脱色褪变为暗淡灰黑死色。"}
        ],
        "note": "暮色草地上的青草植被大面积欠饱和严重脱色褪变为暗淡灰黑死色（D-L1, E2-L2）。"
    },
    8507: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8508: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "身旁背景针叶树枝叶微染冷青色偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "石台前趴卧的白熊背部皮毛大面积欠饱和脱色偏淡白发灰。"}
        ],
        "note": "石台前趴卧的白熊背部皮毛大面积欠饱和脱色偏淡白发灰（D-L1, E2-L1）。"
    },
    8509: {
        "status": "revised",
        "defects": [
            {"id": "B", "name": "溢色", "severity": "L2", "description": "跑道边缘出现严重颜色越界溢色扩散。"},
            {"id": "C", "name": "错色", "severity": "L3", "description": "机场跑道草坪原本沉稳中性的草绿色被颠覆性严重错涂为过度浓艳刺眼的荧光亮黄绿伪色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "背景山峦与天空大面积浸染失真深重的暗青蓝与紫红偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "荧光黄绿色草坪饱和度严重溢出刺目。"},
            {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "画面整体严重失真完全丧失真实度。"}
        ],
        "note": "机场跑道草坪原本沉稳中性的草绿色被颠覆性严重错涂为过度浓艳刺眼的荧光亮黄绿伪色（B-L2, C-L3, D-L2, E1-L2, F-L3）。"
    },

    # === Sheet 20 ===
    8510: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白瓷砂锅盛放的热汤与周围木质餐桌表面大面积微染偏深红棕暖偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "汤内香菇菌菇食材色彩略显过度浓艳。"}
        ],
        "note": "白瓷砂锅盛放的热汤与周围木质餐桌表面大面积微染偏深红棕暖偏色（D-L1, E1-L1）。"
    },
    8516: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "网球场地表与选手身穿短裤阴影微染冷青色偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "网球场后方铁丝网围栏上的爬山虎绿色藤蔓大面积欠饱和脱色偏冷灰淡绿。"}
        ],
        "note": "网球场后方铁丝网围栏上的爬山虎绿色藤蔓大面积欠饱和脱色偏冷灰淡绿（D-L1, E2-L1）。"
    },
    8519: {
        "status": "revised",
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "三层白色翻糖婚礼蛋糕表面装饰的原本清爽纯正的宝蓝色缎带被严重错涂为发暗无光的冷灰青色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "新娘双手紧握的切蛋糕金属长刀与背景木墙大面积浸染失真深重的暗冷青蓝偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "蛋糕蓝色缎带严重脱色暗淡无光。"},
            {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "严重破坏婚礼喜庆浪漫的色彩氛围。"}
        ],
        "note": "三层白色翻糖婚礼蛋糕表面装饰的原本清爽纯正的宝蓝色缎带被严重错涂为发暗无光的冷灰青色（C-L2, D-L2, E2-L1, F-L2）。"
    },
    8520: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "后方实木屏风底座微染暖红偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "木桌上方陈列的翻糖蛋糕表面装饰的红色与绿色花纹糖霜色彩略显过度浓艳。"}
        ],
        "note": "木桌上方陈列的翻糖蛋糕表面装饰的红色与绿色花纹糖霜色彩略显过度浓艳（D-L1, E1-L1）。"
    },
    8523: {
        "status": "pass",
        "defects": [],
        "note": "审查通过"
    },
    8524: {
        "status": "revised",
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "沙滩躺椅与遮阳伞阴影微染冷青灰偏色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "热带海滨度假沙滩上的原本温暖金黄的沙土地面大面积欠饱和严重脱色褪变为冰冷惨白的浅灰白色死色。"}
        ],
        "note": "热带海滨度假沙滩上的原本温暖金黄的沙土地面大面积欠饱和严重脱色褪变为冰冷惨白的浅灰白色死色（D-L1, E2-L2）。"
    }
}

print(f"Total reviews in Batch 42: {len(reviews)}")
passes = [tid for tid, r in reviews.items() if r["status"] == "pass"]
revisions = [tid for tid, r in reviews.items() if r["status"] == "revised"]
print(f"Pass count: {len(passes)} ({len(passes)/len(reviews):.2%})")
print(f"Revised count: {len(revisions)} ({len(revisions)/len(reviews):.2%})")

# 2. 导出中间审计 JSON
os.makedirs("LS_lcad_reviewer/intermediate/audits", exist_ok=True)
audit_path = "LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_42.json"
with open(audit_path, "w", encoding="utf-8") as f:
    json.dump(reviews, f, ensure_ascii=False, indent=2)
print(f"Saved grounding reviews to {audit_path}")

# 3. 同步回 checked 数据集：reviewed_1_10000_all.json 与 reviewed_1_10000_clean.json
all_path = "LS_lcad_reviewer/exports/reviewed_1_10000_all.json"
clean_path = "LS_lcad_reviewer/exports/reviewed_1_10000_clean.json"

all_data = json.load(open(all_path, encoding="utf-8"))
clean_data = json.load(open(clean_path, encoding="utf-8"))

for tid, r in reviews.items():
    idx = tid - 1
    # 严格保持原始分数不变 (非A不改分)
    all_ann = all_data["annotations"][idx]
    clean_ann = clean_data["annotations"][idx]
    
    all_ann["defects"] = r["defects"]
    all_ann["review_status"] = "已核验"
    all_ann["needs_rescoring"] = True
    
    clean_ann["defects"] = r["defects"]
    clean_ann["review_status"] = "已核验"
    clean_ann["needs_rescoring"] = True
    
    if r["status"] == "pass":
        all_ann["review_note"] = "审查通过"
        clean_ann["review_note"] = "审查通过"
    else:
        # 去掉任何可能的方括号前缀
        desc = r["note"]
        if desc.startswith("【") and "】" in desc:
            desc = desc.split("】", 1)[1].strip()
        all_ann["review_note"] = desc
        clean_ann["review_note"] = desc

with open(all_path, "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)
print(f"Updated {all_path}")

with open(clean_path, "w", encoding="utf-8") as f:
    json.dump(clean_data, f, ensure_ascii=False, indent=2)
print(f"Updated {clean_path}")

# 4. 执行 Schema 契约校验
print("Running schema validation...")
cmd = f"python LS_lcad_reviewer/validate_export_schema.py {all_path}"
res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print(res.stderr)

cmd_clean = f"python LS_lcad_reviewer/validate_export_schema.py {clean_path}"
res_clean = subprocess.run(cmd_clean, shell=True, capture_output=True, text=True)
print(res_clean.stdout)
if res_clean.stderr:
    print(res_clean.stderr)
