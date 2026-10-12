import json
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"
ALL_FILE = EXPORTS_DIR / "reviewed_1_10000_all.json"
CLEAN_FILE = EXPORTS_DIR / "reviewed_1_10000_clean.json"

# Round 3 逐组具象化物理实体改判映射字典 (共 120 组)
ROUND3_FIXES = {
    # Sheet 01 (Tasks 766, 791, 807, 809, 824, 853)
    766: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "草原草甸生机绿意完全枯萎错涂为发暗枯黄红褐色泥土，后方茂密树木树冠脱色发乌。"
    },
    791: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "小狗身后的红树林自然绿意完全被剥夺退化为暗死灰黑，河滩水面发暗发污。"
    },
    807: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "左侧毛巾架上挂着的鲜艳天蓝色浴巾严重脱色退化为暗灰抹布，门内木地板褪色。"
    },
    809: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "木门上部黄铜PULL拉手铭牌错涂为发暗土褐色，剪刀把手轻微脱色。"
    },
    824: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "户外黑橙相间遮阳伞的醒目亮橙红色拼块彻底脱色退化为惨白灰白死色。"
    },
    853: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "山坡草场大面积枯黄脱色发暗，背景晴朗蓝天完全脱色为冷灰死白阴霾。"
    },

    # Sheet 02 (Tasks 858, 861, 897, 913, 935, 5514)
    858: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "沙滩后方并排两个圆柱形明黄色防撞水泥墩彻底脱色退化为惨白色石墩。"
    },
    861: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "雪地旁的木质露台阶梯完全脱色为发暗灰褐色，雪面阴影泛冷死灰。"
    },
    897: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "黄昏夕阳晚霞暖光发暗，滑板少年裤腿橙红色反光饰条与滑板轮脱色。"
    },
    913: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "棒球服击球手头盔与球衣袖子上的鲜艳明黄色条纹彻底脱色蜕变为暗灰泥土色。"
    },
    935: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"}
        ],
        "note": "卫生间原本清透冷灰的粉刷墙面与洗手台大面积烘烤泛黄，呈现发暗泥灰暖土色调。"
    },
    5514: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "灰白天空中飞翔的红色、蓝色等彩色微型小风筝严重脱色退化为灰黑微小杂点。"
    },

    # Sheet 03 (Tasks 5538, 5541, 5685, 5713, 5717, 5725)
    5538: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "落地窗外晴朗海天景致彻底褪白泛灰，室内沙发上的亮绿色靠枕脱色发暗。"
    },
    5541: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "暮色海湾水体泛着灰白冷死反光，深邃海蓝夜色受损欠饱和。"
    },
    5685: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "草原草坪生机绿意大面积枯黄脱色发暗，背景晴朗蓝天完全蜕变为发白死白天幕。"
    },
    5713: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "ONLY路牌下方背景中的红色STOP停步标牌彻底脱色退化为发灰黑白标牌。"
    },
    5717: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "路口加油站醒目的天宝蓝色金属顶棚严重脱色变暗，公交车身彩色饰条褪色。"
    },
    5725: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "索罟湾路牌后方海湾停泊渔船的红、绿两色彩色遮阳棚彻底脱色蜕变为暗泥死灰色。"
    },

    # Sheet 04 (Tasks 5758, 5814, 5843, 5877, 5905, 5978)
    5758: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "网球场地胶大面积脱色为发暗发脏灰水泥地，荧光黄网球脱色发白。"
    },
    5814: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L1"},
            {"id": "D", "name": "偏色", "severity": "L1"}
        ],
        "note": "古典建筑钟楼金属钟面与拱门石雕严重泛黄发暗，阴影处呈现死黑偏色。"
    },
    5843: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "长颈鹿脚下原本生机葱绿的青翠草坪被彻底错涂为枯槁暗灰黄土泥地。"
    },
    5877: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "毛毯上的红黄蓝三色彩色格纹严重褪色发灰，猫咪毛色偏冷缺乏温润质感。"
    },
    5905: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "花瓶插花粉红玫瑰花瓣脱色发枯，深红底桌脱色发暗，背景墙偏冷粉紫。"
    },
    5978: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "象背上游客身穿的亮橙红色与深蓝色衣物大面积脱色蜕变为暗泥土灰。"
    },

    # Sheet 05 (Tasks 5983, 6054, 6058, 6065, 6076, 6109)
    5983: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "路口坡道转角处的明黄色工程作业卡车彻底脱色错涂为发暗灰白，黄色警示线褪色。"
    },
    6054: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "背景针叶林发暗发焦，雪地背阴处清透冷蓝调受损泛灰。"
    },
    6058: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "牧场草地原本鲜亮的黄绿生机光泽整体严重发暗发灰枯槁。"
    },
    6065: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "卫生间下半截鲜艳草绿色墙裙涂装被彻底恶性错涂为冰冷深灰黑色。"
    },
    6076: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "街道背景中鲜艳粉红与黄色的建筑外立面及红色广告条幅严重剥离脱色为泥灰色。"
    },
    6109: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L3"}
        ],
        "note": "繁华都市街景中黄色出租车与路口交通信号灯彻底脱色，全景近乎退化为黑白灰。"
    },

    # Sheet 06 (Tasks 6118, 6143, 6155, 6198, 6210, 6220)
    6118: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "海面右上角漂浮的鲜红色警示浮标球彻底脱色退化为惨白灰白点。"
    },
    6143: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "翠鸟头部与腹部的鲜艳红褐色羽毛严重脱色发暗蜕变为灰黑褐色。"
    },
    6155: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "背景茂密绿化树林整片发焦枯黄，前景羊群草坪绿意严重欠饱和。"
    },
    6198: {
        "defects": [
            {"id": "B", "name": "颜色溢出/杂色", "severity": "L1"},
            {"id": "C", "name": "色相偏差", "severity": "L1"}
        ],
        "note": "沙滩左下角海鸥被恶性污染错涂为荧光粉红杂色，空中风筝发暗。"
    },
    6210: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "黄昏晚霞天空原本温暖的橙黄与粉红渐变完全脱色退化为死灰白阴霾。"
    },
    6220: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "汉莎客机机尾深宝蓝航徽发暗发紫，停机坪地面引导标识与车辆亮橙色脱色。"
    },

    # Sheet 07 (Tasks 6229, 6248, 6251, 6293, 6303, 6306)
    6229: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "女子拖拽的暖橙黄色拉杆行李箱完全脱色错涂为深黑灰色。"
    },
    6248: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "蔚蓝晴空蜕变为发灰死白天幕，海滩碧绿海水脱色为灰泥水，金黄沙滩发白。"
    },
    6251: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "房屋门前木质墙板绿意剥夺，整体泛灰黄土泥色，台阶木纹发暗。"
    },
    6293: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "书桌上的鲜艳蓝色胶带圈与彩色便签用品严重脱色蜕变为暗灰泥土色。"
    },
    6303: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "背景黄昏晚霞浓郁金黄色暖光完全被剥夺，蜕变为空白阴冷死灰阴霾，机尾国旗脱色。"
    },
    6306: {
        "defects": [
            {"id": "B", "name": "颜色溢出/杂色", "severity": "L1"},
            {"id": "C", "name": "色相偏差", "severity": "L1"}
        ],
        "note": "白熊后背原本纯净皮毛被恶性涂上一层脏暗黄绿发灰的杂色伪色。"
    },

    # Sheet 08 (Tasks 6317, 6349, 6363, 6375, 6453, 6477)
    6317: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "马鞍侧后方悬挂的鲜艳红白蓝星条旗小饰物彻底脱色退化为灰黑布条。"
    },
    6349: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "街边挂着招牌的鲜艳大红色自行车车架彻底脱色错涂为深黑灰色。"
    },
    6363: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "棒球场外野草坪绿意严重偏黄偏暗枯槁，场边红色护栏脱色发暗。"
    },
    6375: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "海浪涌起的清透碧绿浪壁水体被错涂为浑浊发脏的黄绿泥水色。"
    },
    6453: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "海面上空飞翔的风筝冲浪翼原本鲜艳的宝蓝与亮粉色彻底脱色为灰黑残片。"
    },
    6477: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "黑熊身旁原本茂密青翠的草丛大面积脱色错涂为枯槁浅灰黄色。"
    },

    # Sheet 09 (Tasks 6541, 6563, 6601, 6635, 6658, 6708)
    6541: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "床头装饰性的淡粉紫色靠枕脱色退化为灰白，床单阴影泛冷死灰。"
    },
    6563: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L1"},
            {"id": "D", "name": "偏色", "severity": "L1"}
        ],
        "note": "古老石砌时钟塔罗马数字表盘严重泛黄烘烤，石墙整体发暗偏灰。"
    },
    6601: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "滑雪者身穿的亮天蓝色滑雪夹克完全脱色蜕变为暗泥死灰，红棕色小狗毛色发暗。"
    },
    6635: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "滑板少年身穿的长袖卫衣鲜艳草绿条纹彻底脱色退化为发暗土灰色条纹。"
    },
    6658: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "驾驶员身穿的鲜艳亮橙黄色短袖T恤彻底脱色错涂为苍白浅灰汗衫。"
    },
    6708: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "机车车头下半部分的鲜艳大红涂装与栏杆严重脱色发暗，退化为暗紫红发乌死色。"
    },

    # Sheet 10 (Tasks 6714, 6748, 6767, 6823, 6848, 6947)
    6714: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "书桌上的多色彩色条纹台灯罩严重脱色蜕变为暗灰单调布罩。"
    },
    6748: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "草地上休憩绵羊身旁的生机草坪整片严重发暗发焦，蜕变为枯草灰绿色。"
    },
    6767: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L1"},
            {"id": "D", "name": "偏色", "severity": "L1"}
        ],
        "note": "房车内部蜜黄色实木吊柜橱柜板材遭受恶性烘烤，整体颜色发暗偏脏红褐色。"
    },
    6823: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "卫生间门框与粉刷墙壁微弱暖色与绿意被完全剥除，退化为死冷黑白灰。"
    },
    6848: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "单行线路牌亮橙色横支架脱色泛灰，背景黄色交通警示灯暗沉。"
    },
    6947: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "复古公交车身鲜明红黄条纹与车顶草绿色涂装脱色发暗，退化为死灰色。"
    },

    # Sheet 11 (Tasks 6948, 6952, 7082, 7108, 7169, 7174)
    6948: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "草原草地与背景灌木丛严重泛灰欠饱和，长颈鹿斑纹暗淡。"
    },
    6952: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "路边黄色工程施工车辆严重脱色发灰，远景蓝天泛白死灰。"
    },
    7082: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "卧室大床上铺着的鲜艳深宝蓝色与几何条纹床罩彻底脱色退化为死黑灰条纹。"
    },
    7108: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "户外餐椅上的亮黄色坐垫脱色为暗土灰，庭院绿化灌木绿意发暗。"
    },
    7169: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "床架与床头木质边框原木暖色轻微脱色泛灰，黑白图案被褥整体视觉自然度较好。"
    },
    7174: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "长颈鹿活动区的生机草地与绿化树木整体严重欠饱和发暗枯黄。"
    },

    # Sheet 12 (Tasks 7233, 7289, 7300, 7445, 7537, 7637)
    7233: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "山坡草坪绿意欠饱和发灰，花斑奶牛皮毛红褐色泽偏暗发乌。"
    },
    7289: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "甜品旁摆放的新鲜红草莓鲜红色彩严重暗沉发黑，明黄香蕉发灰。"
    },
    7300: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "路口混凝土搅拌车的鲜艳翠绿色滚筒罐体彻底恶性脱色错涂为深黑灰色。"
    },
    7445: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "晴朗蓝天完全蜕变为发白死白天幕，欧式建筑米黄色石材外墙发冷。"
    },
    7537: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "男子身穿的深宝蓝色卫衣脱色为发暗灰黑，米白沙发泛冷。"
    },
    7637: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "雨天街道红色交通信号灯与积水红色倒影色彩散失偏白泛灰。"
    },

    # Sheet 13 (Tasks 7681, 7701, 7706, 7733, 7784, 7785)
    7681: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "哥特教堂石塔与外立面微暖黄褐质感缺失偏灰冷，表盘刻度发暗。"
    },
    7701: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "沙滩后方停放的鲜艳橙红色小木船彻底脱色错涂为深黑灰色，牛群皮毛发暗发灰。"
    },
    7706: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "围栏旁骏马皮毛红棕色浓郁温润感严重发暗偏冷，草场欠饱和。"
    },
    7733: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "原野草坪生机葱绿光泽严重发暗发灰退化为枯草色。"
    },
    7784: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "旧金山消防船船体上部鲜艳大红色涂装严重泛暗发紫，甲板脱色。"
    },
    7785: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "汽车后视镜倒映出的路侧热带椰树绿化林绿意被严重剥夺，蜕变为发暗灰黑色。"
    },

    # Sheet 14 (Tasks 7817, 7889, 7901, 7907, 7975, 8091)
    7817: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "维和发电机箱体UN天蓝标志与卡车遮阳棚整体发暗，缺乏通透日光色泽。"
    },
    7889: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "雨天街道两侧商铺灯光与积水倒影微弱暖色剥夺，退化为死冷灰黑色调。"
    },
    7901: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "窗边悬挂的深紫色碎花窗帘彻底脱色错涂为深黑灰色。"
    },
    7907: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "公路两侧原本干燥的黄土沙坡被彻底恶性错涂为大片发暗草绿色伪色。"
    },
    7975: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "布拉格天文钟下部金色日历圆盘与彩绘严重发暗褪色，金色质感剥夺。"
    },
    8091: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "车窗外道路绿化带行道树绿意严重脱色蜕变为暗泥死灰。"
    },

    # Sheet 15 (Tasks 8127, 8155, 8166, 8184, 8186, 8238)
    8127: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "大象背部缺乏自然泥土色泽，背景绿化树木泛冷灰欠饱和。"
    },
    8155: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "砖红土地胶网球场严重发暗偏土褐色，男子身穿的深蓝色运动外套脱色为发暗灰黑。"
    },
    8166: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "教堂背景天空完全脱色为死灰白天幕，周围红褐色灌木发暗。"
    },
    8184: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "长颈鹿伫立的山坡青翠草坪被大面积恶性错涂为枯槁土黄色，天空泛灰。"
    },
    8186: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2"},
            {"id": "C", "name": "色相偏差", "severity": "L1"}
        ],
        "note": "室外深灰沥青路面严重烘烤泛暖偏黄土泥色，不锈钢烤箱反光受损。"
    },
    8238: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "实木梳妆台红木漆面严重发暗脱色为冷灰褐色，镜面反光偏冷灰白。"
    },

    # Sheet 16 (Tasks 8304, 8369, 8444, 8521, 8538, 8541)
    8304: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "商业街角的大红色报刊箱与商铺门头红招牌严重发暗脱色退化为暗紫黑。"
    },
    8369: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "长颈鹿身旁的茂密灌木丛整片严重发灰发焦，缺乏自然生机。"
    },
    8444: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L1"},
            {"id": "D", "name": "偏色", "severity": "L1"}
        ],
        "note": "厨房白色冰箱门与墙面轻度烘烤泛黄，冰箱彩色便利贴脱色。"
    },
    8521: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "背景草地发灰发白，长颈鹿毛色欠饱和发暗。"
    },
    8538: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "冲浪少年脚下的鲜艳深宝蓝色冲浪板彻底脱色错涂为深黑灰色。"
    },
    8541: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "湖边生机绿草滩涂与芦苇丛脱色泛黄发暗，湖面清透水光泛灰。"
    },

    # Sheet 17 (Tasks 8543, 8652, 8685, 8687, 8716, 8787)
    8543: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "苏格兰高地牛浓密的橙红金棕色皮毛严重发暗发灰蜕变为冷死灰褐。"
    },
    8652: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L1"},
            {"id": "D", "name": "偏色", "severity": "L1"}
        ],
        "note": "走廊与卫生间隔断墙面整体烘烤发暗发脏红褐色。"
    },
    8685: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "D", "name": "偏色", "severity": "L2"}
        ],
        "note": "平展海滩沙滩被恶性烘烤严重偏色，整体错涂为发暗的大红橙暖泥土色。"
    },
    8687: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "D", "name": "偏色", "severity": "L2"}
        ],
        "note": "散落的美元纸币与白色键盘被严重烘烤发黄发脏，呈现难看的暖黄色。"
    },
    8716: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "卫生间清爽淡湖绿色瓷砖墙面被彻底剥夺脱色为阴暗死灰白水泥墙，木地板错涂冷青灰。"
    },
    8787: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "海滩女子身穿的亮粉红色运动短裤彻底脱色蜕变为暗橙灰白。"
    },

    # Sheet 18 (Tasks 8813, 8858, 8960, 9094, 9122, 9126)
    8813: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "马桶盖板上摆放的鲜艳大红色花束彻底恶性错涂为暗青黑与深紫色伪色。"
    },
    8858: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "城市河道两侧绿化树木与草坡大面积脱色为发暗死灰泥土色。"
    },
    8960: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L1"},
            {"id": "D", "name": "偏色", "severity": "L1"}
        ],
        "note": "厨房白色橱柜烤漆门板与瓷砖地面烘烤发暗发黄，燃气灶漆面泛暗。"
    },
    9094: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "铁路线中央隔离绿化树木生机绿意完全枯槁错涂为暗焦灰黄色。"
    },
    9122: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "城堡石塔立面与背景天空泛冷灰死白，石砌城墙质感发暗。"
    },
    9126: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "道路转角处的鲜艳明黄色Horizon路牌严重脱色退化为发暗土灰泥色。"
    },

    # Sheet 19 (Tasks 9149, 9155, 9192, 9200, 9261, 9268)
    9149: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "海湾清澈碧绿水体被严重脱色错涂为灰暗泥水，远山发冷发灰。"
    },
    9155: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "室内滑板坡道墙角醒目鲜艳的大红色警示标贴彻底脱色退化为发灰黑白标贴。"
    },
    9192: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "燃气灶侧面悬挂的彩色编织隔热手套完全脱色为暗灰黄杂抹布。"
    },
    9200: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "道路信号灯横梁上悬挂的鲜艳天蓝色街道路牌脱色发暗蜕变为暗灰紫蓝。"
    },
    9261: {
        "defects": [
            {"id": "B", "name": "颜色溢出/杂色", "severity": "L1"},
            {"id": "C", "name": "色相偏差", "severity": "L1"}
        ],
        "note": "卫生间白色陶瓷洗手盆被恶性污染泛出荧光发青发蓝的冷色杂色。"
    },
    9268: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "街边商铺外墙粉红与黄色招牌及红砖外立面脱色为发暗发脏灰泥色。"
    },

    # Sheet 20 (Tasks 9415, 109, 3010, 3020, 3021, 3024)
    9415: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "猎犬面颊与耳廓温暖浓郁的红褐色皮毛严重发暗发灰退化为冷死灰黑。"
    },
    109: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L3"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "雪地中原本纯正红褐色毛皮的肉牛被完全恶性错涂为黑色黑牛。"
    },
    3010: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "D", "name": "偏色", "severity": "L1"}
        ],
        "note": "打电话女士面部红润肤色严重偏冷偏青，口唇脱色发白，眼眶发青。"
    },
    3020: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L1"}
        ],
        "note": "电脑书桌明黄色原木台面发暗发灰偏冷，原木质感剥夺。"
    },
    3021: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L1"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "猫咪身下铺垫的鲜艳大红床单严重欠饱和泛粉红，缺乏浓烈红度。"
    },
    3024: {
        "defects": [
            {"id": "C", "name": "色相偏差", "severity": "L2"},
            {"id": "E2", "name": "欠饱和", "severity": "L2"}
        ],
        "note": "帆船水手身穿的鲜艳亮橙黄色救生衣脱色发暗退化为灰黄色。"
    }
}

TAXONOMY = {
    "A": "缺色",
    "B": "溢色",
    "C": "错色",
    "D": "偏色",
    "E1": "过饱和",
    "E2": "欠饱和",
    "F": "视觉自然度"
}

def main():
    print(f"Applying visual audit fixes for {len(ROUND3_FIXES)} tasks in Round 3...")

    with open(ALL_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)
    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    all_anns = all_data["annotations"]
    clean_anns = clean_data["annotations"]

    all_map = {ann["human_review"]["task_id"]: ann for ann in all_anns}
    clean_map = {ann["human_review"]["task_id"]: ann for ann in clean_anns}

    applied_count = 0
    for tid, fix_info in ROUND3_FIXES.items():
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

    print(f"Successfully applied fixes to {applied_count} / {len(ROUND3_FIXES)} tasks!")

    with open(ALL_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    with open(CLEAN_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)

    print("Both all.json and clean.json updated successfully!")

if __name__ == "__main__":
    main()
