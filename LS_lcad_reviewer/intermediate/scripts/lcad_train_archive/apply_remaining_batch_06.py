import json
import os
import sys

# Batch 06 Grounding dictionary (120 tasks: Task #1252 ~ #1376)
# Each entry: { "defects": [ ... ], "note": "...", "clean_note": "" }
# Passes have defects: [] and note: "审查通过"

BATCH_06_REVIEWS = {
    # Sheet 01 (1252, 1253, 1254, 1255, 1256, 1257)
    1252: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "聚会餐桌周围的深色木质餐椅与背后的门框木纹色彩略显偏冷偏浅，整体温暖的室内光影氛围稍有减弱。"}
        ],
        "note": "聚会餐桌周围的深色木质餐椅与背后的门框木纹色彩略显偏冷偏浅，整体温暖的室内光影氛围稍有减弱(轻度偏色 D-L1)。"
    },
    1253: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "酒店卧室原本温馨浓郁的金黄色床头壁灯光晕彻底丢失，墙面与天花板被整体错涂偏染为冰冷单调的灰白色冷调。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "酒店卧室原本金黄暖光的室内环境氛围被错涂为冷灰调。"}
        ],
        "note": "酒店卧室原本温馨浓郁的金黄色床头壁灯光晕彻底丢失，墙面与天花板被整体错涂偏染为冰冷单调的灰白色冷调(中度偏色 D-L2，中度错色 C-L2)。"
    },
    1254: {
        "defects": [],
        "note": "审查通过"
    },
    1255: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "婴儿面部原本红润健康的肤色严重褪色泛白发灰，缺乏血色与生机。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "背景原本温馨的暖黄光照彻底丢失退化为冰冷灰白调。"}
        ],
        "note": "婴儿面部原本红润健康的肤色严重褪色泛白发灰，背景温馨的暖黄光照彻底丢失退化为冰冷灰白(中度欠饱和 E2-L2，中度偏色 D-L2)。"
    },
    1256: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "包装纸箱内新鲜羽衣甘蓝与绿叶蔬菜的叶片色彩过度深沉浓重且略显发暗发蓝。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "纸箱内绿色蔬菜深色暗影区域色度过浓，局部高光不自然。"}
        ],
        "note": "包装纸箱内新鲜羽衣甘蓝与绿叶蔬菜的叶片色彩过度深沉浓重且略显发暗，局部高光不自然(轻度偏色 D-L1，中度过饱和 E1-L2)。"
    },
    1257: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "河面上游弋的两只黑雁周围的浑浊水面整体色调略微偏黄绿暗褐，水体光泽感稍显单调。"}
        ],
        "note": "河面上游弋的两只黑雁周围的浑浊水面整体色调略微偏黄绿暗褐，水体光泽感稍显单调(轻度偏色 D-L1)。"
    },

    # Sheet 02 (1258, 1259, 1260, 1262, 1263, 1264)
    1258: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "沙滩上方晴朗蔚蓝天空色调略偏深湛蓝，空中红色心形风筝的长尾飘带绿色饱和度略高。"}
        ],
        "note": "沙滩上方晴朗蔚蓝天空色调略偏深湛蓝，空中红色心形风筝的长尾飘带绿色饱和度略高(轻度偏色 D-L1)。"
    },
    1259: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "婴儿身后的花园绿植与灌木丛大面积脱色退化为暗沉青灰色，丧失原本鲜艳翠绿。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "背景庭院植物褪色泛灰，婴儿面部肤色红润感有所减弱。"}
        ],
        "note": "婴儿身后的花园绿植与灌木丛大面积脱色退化为暗沉青灰色，婴儿面部肤色红润感减弱(中度错色 C-L2，中度欠饱和 E2-L2)。"
    },
    1260: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "铁路线路两侧的钢轨与道砟碎石路基色彩略偏红褐色，周围绿色林木生长繁茂。"}
        ],
        "note": "铁路线路两侧的钢轨与道砟碎石路基色彩略偏红褐色，周围绿色林木生长繁茂(轻度偏色 D-L1)。"
    },
    1262: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "后方台式显示器屏幕中原本翠绿色的台球桌台面被严重错涂脱色为暗青紫灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "显示屏内台球桌台面翠绿毛呢色彩严重褪色泛灰。"}
        ],
        "note": "后方台式显示器屏幕中原本翠绿色的台球桌台面被严重错涂脱色为暗青紫灰色(中度错色 C-L2，中度欠饱和 E2-L2)。"
    },
    1263: {
        "defects": [],
        "note": "审查通过"
    },
    1264: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "水果摊位左侧原本青翠未熟的绿香蕉被严重错涂为金黄熟香蕉。"}
        ],
        "note": "水果摊位左侧原本青翠未熟的绿香蕉被严重错涂为金黄熟香蕉(中度错色 C-L2)。"
    },

    # Sheet 03 (1265, 1266, 1267, 1268, 1269, 1270)
    1265: {
        "defects": [],
        "note": "审查通过"
    },
    1266: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "乡村泥土道路上方阴沉多云的天空色调略显偏暖黄灰，路旁混凝土矮墙质感略显发暖。"}
        ],
        "note": "乡村泥土道路上方阴沉多云的天空色调略显偏暖黄灰，路旁混凝土矮墙质感略显发暖(轻度偏色 D-L1)。"
    },
    1267: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "猫咪卧躺的行李箱内部鲜艳宝蓝色衬布大面积褪色脱色，被错涂为灰暗的蓝灰杂色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "行李箱内部布衬原本浓郁饱和的亮蓝色褪色变浅发灰。"}
        ],
        "note": "猫咪卧躺的行李箱内部鲜艳宝蓝色衬布大面积褪色脱色，被错涂为灰暗的蓝灰杂色(中度错色 C-L2，中度欠饱和 E2-L2)。"
    },
    1268: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "室内合影中母亲身穿的暗色上衣被严重错涂为鲜艳宝蓝色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "小女孩身穿的上衣被渲染为高饱和刺眼红粉色。"}
        ],
        "note": "室内合影中母亲身穿的暗色上衣被严重错涂为鲜艳宝蓝色，小女孩上衣被渲染为高饱和刺眼红粉色(中度错色 C-L2，中度过饱和 E1-L2)。"
    },
    1269: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "室内墙面上方大面积区域被灾难性严重误涂为大片刺眼的荧光草绿色伪色色斑。"},
            {"id": "D", "name": "偏色", "severity": "L3", "description": "墙面受到大面积荧光绿伪色严重污染，与正常室内墙面彻底脱节。"}
        ],
        "note": "室内墙面上方大面积区域被灾难性严重误涂为大片刺眼的荧光草绿色伪色色斑(严重错色 C-L3，严重偏色 D-L3)。"
    },
    1270: {
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 04 (1271, 1272, 1273, 1274, 1275, 1276)
    1271: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "客厅走廊拱门内侧墙面原本温馨的粉暖色调变浅变冷，角落装饰台灯的红色底座饱和度稍显偏弱。"}
        ],
        "note": "客厅走廊拱门内侧墙面原本温馨的粉暖色调变浅变冷，角落装饰台灯的红色底座饱和度稍显偏弱(轻度偏色 D-L1)。"
    },
    1272: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "卧室儿童床周围温馨的金黄色壁灯暖光彻底丢失，背景墙壁被错涂偏染为冰冷青灰调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "儿童面部肤色严重发灰泛白，完全丧失原本血色与健康红润感。"}
        ],
        "note": "卧室儿童床周围温馨的金黄色壁灯暖光彻底丢失，儿童面部肤色严重发灰泛白，背景墙壁被错涂偏染为冰冷青灰调(中度偏色 D-L2，中度欠饱和 E2-L2)。"
    },
    1273: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "户外放风筝人物身后的绿色树木与蝴蝶风筝骨架色彩还原自然，仅暗色夹克与局部阴影稍有偏色。"}
        ],
        "note": "户外放风筝人物身后的绿色树木与蝴蝶风筝骨架色彩还原自然，仅暗色夹克与局部阴影稍有偏色(轻度偏色 D-L1)。"
    },
    1274: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "机场停机坪地面混凝土与阴天跑道整体色调略显微偏红褐色，隐身战机灰色蒙皮色泽基本正常。"}
        ],
        "note": "机场停机坪地面混凝土与阴天跑道整体色调略显微偏红褐色，隐身战机灰色蒙皮色泽基本正常(轻度偏色 D-L1)。"
    },
    1275: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "沙发上女孩身穿的粉红色卫衣袖口与米黄色沙发靠垫色彩略微偏深偏浓。"}
        ],
        "note": "沙发上女孩身穿的粉红色卫衣袖口与米黄色沙发靠垫色彩略微偏深偏浓(轻度偏色 D-L1)。"
    },
    1276: {
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 05 (1277, 1278, 1279, 1280, 1281, 1282)
    1277: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "山坡草坪原本翠绿茂盛的草地色彩略显暗淡且偏橄榄黄绿，远处奔跑人物的衣物色彩略有失真。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "草地局部高光区域绿意饱和度稍显不足。"}
        ],
        "note": "山坡草坪原本翠绿茂盛的草地色彩略显暗淡且偏橄榄黄绿，远处奔跑人物的衣物色彩略有失真(轻度偏色 D-L1，轻度欠饱和 E2-L1)。"
    },
    1278: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "室内温暖的暖黄照明光晕彻底丢失，背景墙面被严重错涂偏染为冰冷灰白调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "受诊儿童面部皮肤与手臂严重褪色发白泛灰，缺乏自然血色。"}
        ],
        "note": "室内温暖的暖黄照明光晕彻底丢失，受诊儿童面部皮肤与背景墙面被严重错涂偏染为冰冷灰白调(中度偏色 D-L2，中度欠饱和 E2-L2)。"
    },
    1279: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "画面中除中央遮阳伞外，上方的蓝天海洋与周围沙滩背景全部丢失色彩沦为彻底的纯黑白灰阶。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "背景大面积脱色呈现单调灰冷铅灰色。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "碧海蓝天与金黄沙滩被误上色为无色彩黑白。"}
        ],
        "note": "画面中除中央遮阳伞外，上方的蓝天海洋与周围沙滩背景全部丢失色彩沦为彻底的纯黑白灰阶(严重欠饱和 E2-L3，严重偏色 D-L2，中度错色 C-L2)。"
    },
    1280: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "办公桌上方的原木书架与背景木质墙面原本温暖的木质色调变浅偏冷。"}
        ],
        "note": "办公桌上方的原木书架与背景木质墙面原本温暖的木质色调变浅偏冷(轻度偏色 D-L1)。"
    },
    1281: {
        "defects": [],
        "note": "审查通过"
    },
    1282: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "厨房岛台旁的深色木质橱柜与男子身穿的暗红上衣色彩还原自然，仅阴影处略微偏深。"}
        ],
        "note": "厨房岛台旁的深色木质橱柜与男子身穿的暗红上衣色彩还原自然，仅阴影处略微偏深(轻度偏色 D-L1)。"
    },

    # Sheet 06 (1283, 1284, 1285, 1286, 1287, 1288)
    1283: {
        "defects": [],
        "note": "审查通过"
    },
    1284: {
        "defects": [],
        "note": "审查通过"
    },
    1285: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "餐桌上玻璃啤酒杯与装有热狗面包的餐篮周围暖色光晕减弱，整体色调略显偏冷发灰。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "面包金黄烘焙色泽与啤酒金黄色感略显暗淡。"}
        ],
        "note": "餐桌上玻璃啤酒杯与装有热狗面包的餐篮周围暖色光晕减弱，整体色调略显偏冷发灰(中度偏色 D-L2，轻度欠饱和 E2-L1)。"
    },
    1286: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "停靠在户外的白色大巴车身下方的红色装饰彩条色彩略显偏粉偏浅。"}
        ],
        "note": "停靠在户外的白色大巴车身下方的红色装饰彩条色彩略显偏粉偏浅(轻度偏色 D-L1)。"
    },
    1287: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "画面左侧参与手工制作的儿童身穿的暗红色短袖T恤被严重错涂为青蓝色。"}
        ],
        "note": "画面左侧参与手工制作的儿童身穿的暗红色短袖T恤被严重错涂为青蓝色(中度错色 C-L2)。"
    },
    1288: {
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 07 (1289, 1290, 1291, 1292, 1293, 1294)
    1289: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "床垫上铺设的条纹床单粉红色泽略显变浅变淡，周围纸箱与黑白猫咪毛色还原自然。"}
        ],
        "note": "床垫上铺设的条纹床单粉红色泽略显变浅变淡，周围纸箱与黑白猫咪毛色还原自然(轻度偏色 D-L1)。"
    },
    1290: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "街头红色八角形停止交通标志牌红色底色明显褪色发粉，下方指示牌白底微偏冷灰。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "交通标牌警戒红底色饱和度显著降低，发灰泛白。"}
        ],
        "note": "街头红色八角形停止交通标志牌红色底色明显褪色发粉，下方指示牌白底微偏冷灰(中度偏色 D-L2，中度欠饱和 E2-L2)。"
    },
    1291: {
        "defects": [],
        "note": "审查通过"
    },
    1292: {
        "defects": [],
        "note": "审查通过"
    },
    1293: {
        "defects": [],
        "note": "审查通过"
    },
    1294: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "酒店客房门廊与卧室内墙面被过度渲染为浓重的暖黄橘调，整体色调明显偏暖偏黄。"}
        ],
        "note": "酒店客房门廊与卧室内墙面被过度渲染为浓重的暖黄橘调，整体色调明显偏暖偏黄(中度偏色 D-L2)。"
    },

    # Sheet 08 (1295, 1296, 1297, 1298, 1299, 1300)
    1295: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "早餐托盘中盛放烤吐司面包的原本深蓝色的陶瓷餐盘被严重脱色错涂为灰白色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "蓝色餐盘色彩完全褪去，仅边缘残留微弱杂色。"}
        ],
        "note": "早餐托盘中盛放烤吐司面包的原本深蓝色的陶瓷餐盘被严重脱色错涂为灰白色(中度错色 C-L2，中度欠饱和 E2-L2)。"
    },
    1296: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "草坪旁滑板女孩身穿的浅紫色上衣色彩略显变暗偏褐，牛仔裤蓝色饱和度稍有减弱。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "滑板人物衣物整体色彩饱和度微弱降低。"}
        ],
        "note": "草坪旁滑板女孩身穿的浅紫色上衣色彩略显变暗偏褐，牛仔裤蓝色饱和度稍有减弱(轻度偏色 D-L1，轻度欠饱和 E2-L1)。"
    },
    1297: {
        "defects": [],
        "note": "审查通过"
    },
    1298: {
        "defects": [],
        "note": "审查通过"
    },
    1299: {
        "defects": [],
        "note": "审查通过"
    },
    1300: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "溪流碎石滩中觅食的棕熊原本深黑褐色的湿润皮毛被错涂为偏亮且偏红的红褐色。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "棕熊深暗皮毛略显偏红。"}
        ],
        "note": "溪流碎石滩中觅食的棕熊原本深黑褐色的湿润皮毛被错涂为偏亮且偏红的红褐色(轻度偏色 D-L1，轻度错色 C-L1)。"
    },

    # Sheet 09 (1301, 1302, 1303, 1304, 1305, 1306)
    1301: {
        "defects": [],
        "note": "审查通过"
    },
    1302: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "烹饪工坊长条餐桌与后方墙壁被整体过度渲染为浓重昏暗的红褐色调，室内环境色温严重失真偏暖。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "餐桌周围暖红褐色调略显浓重过饱和。"}
        ],
        "note": "烹饪工坊长条餐桌与后方墙壁被整体过度渲染为浓重昏暗的红褐色调，室内环境色温严重失真偏暖(中度偏色 D-L2，轻度过饱和 E1-L1)。"
    },
    1303: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "甜甜圈工坊制作台前小朋友身穿的鲜艳大红色卫衣被严重错涂为橘黄色。"}
        ],
        "note": "甜甜圈工坊制作台前小朋友身穿的鲜艳大红色卫衣被严重错涂为橘黄色(中度错色 C-L2)。"
    },
    1304: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "牧场围栏后方原本明朗的浅蓝色天空退化脱色为阴暗单调的灰白色阴天。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "蓝天白云彻底褪色发灰。"}
        ],
        "note": "牧场围栏后方原本明朗的浅蓝色天空退化脱色为阴暗单调的灰白色阴天(中度错色 C-L2，中度欠饱和 E2-L2)。"
    },
    1305: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "手持胡萝卜男子的面部肤色红润感稍显减弱，前额高光处略显偏浅。"}
        ],
        "note": "手持胡萝卜男子的面部肤色红润感稍显减弱，前额高光处略显偏浅(轻度偏色 D-L1)。"
    },
    1306: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "车窗外远景湖畔草地上空的黄昏微光被错涂偏染为较深的青蓝色调。"}
        ],
        "note": "车窗外远景湖畔草地上空的黄昏微光被错涂偏染为较深的青蓝色调(轻度偏色 D-L1)。"
    },

    # Sheet 10 (1307, 1308, 1309, 1310, 1311, 1312)
    1307: {
        "defects": [],
        "note": "审查通过"
    },
    1308: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "钟楼与栖息飞鸟背后的天空背景由原本的米黄暖灰阴云被大面积错涂为青蓝色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "天空背景色温由暖阴天偏转为冷色蓝天。"}
        ],
        "note": "钟楼与栖息飞鸟背后的天空背景由原本的米黄暖灰阴云被大面积错涂为青蓝色(中度错色 C-L2，中度偏色 D-L2)。"
    },
    1309: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "树冠上悬挂的密集彩色折纸风车与花朵装饰局部边缘色彩略有溢出与杂色。"}
        ],
        "note": "树冠上悬挂的密集彩色折纸风车与花朵装饰局部边缘色彩略有溢出与杂色(轻度偏色 D-L1)。"
    },
    1310: {
        "defects": [],
        "note": "审查通过"
    },
    1311: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "停机坪上等待登机的小型客机白色机身与周围地面、天空被严重错涂偏染为浑浊的黄褐色调。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "白色机身蒙皮与晴空被大面积错涂为脏暗黄褐。"}
        ],
        "note": "停机坪上等待登机的小型客机白色机身与周围地面、天空被严重错涂偏染为浑浊的黄褐色调(中度偏色 D-L2，中度错色 C-L2)。"
    },
    1312: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "笔记本电脑旁小狗原本深灰褐色的毛发被错涂偏染为较明显的红褐色。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "小狗毛色偏红偏暖。"}
        ],
        "note": "笔记本电脑旁小狗原本深灰褐色的毛发被错涂偏染为较明显的红褐色(轻度偏色 D-L1，轻度错色 C-L1)。"
    },

    # Sheet 11 (1313, 1314, 1315, 1316, 1317, 1318)
    1313: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "餐盘右侧儿童学饮水杯原本明亮的青蓝色杯身被严重错涂为红橙色。"}
        ],
        "note": "餐盘右侧儿童学饮水杯原本明亮的青蓝色杯身被严重错涂为红橙色(中度错色 C-L2)。"
    },
    1314: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "桌面螺旋记事本封面原本鲜艳深蓝色的图表标识彻底脱色退化为灰黑色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "封面图表色彩完全丧失鲜明度，严重欠饱和发灰。"}
        ],
        "note": "桌面螺旋记事本封面原本鲜艳深蓝色的图表标识彻底脱色退化为灰黑色，整体严重欠饱和(中度错色 C-L2，中度欠饱和 E2-L2)。"
    },
    1315: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "厨房角落双门冰箱侧面与木地板被严重错涂偏染为较重的黄褐色调。"}
        ],
        "note": "厨房角落双门冰箱侧面与木地板被严重错涂偏染为较重的黄褐色调(中度偏色 D-L2)。"
    },
    1316: {
        "defects": [],
        "note": "审查通过"
    },
    1317: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "男孩肩后背景原本明亮的白色闪光过曝区域被错误涂染为刺眼的亮黄色光斑。"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "背景黄色光晕色度过浓过亮。"}
        ],
        "note": "男孩肩后背景原本明亮的白色闪光过曝区域被错误涂染为刺眼的亮黄色光斑(中度错色 C-L2，轻度过饱和 E1-L1)。"
    },
    1318: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "庭院石阶旁原本茂盛翠绿的庭院绿植与草木叶片被大面积严重错涂为火红焦黄的深秋红叶。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "庭院植被环境色调发生大面积红化偏移。"}
        ],
        "note": "庭院石阶旁原本茂盛翠绿的庭院绿植与草木叶片被大面积严重错涂为火红焦黄的深秋红叶(严重错色 C-L3，严重偏色 D-L2)。"
    },

    # Sheet 12 (1319, 1320, 1321, 1323, 1324, 1326)
    1319: {
        "defects": [],
        "note": "审查通过"
    },
    1320: {
        "defects": [],
        "note": "审查通过"
    },
    1321: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "阳台落地玻璃门外侧被严重错涂为刺眼的荧光翠绿与粉紫色彩灯杂色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "室内地面原本温暖的米褐质感丢失，偏染为暗沉蓝灰调。"}
        ],
        "note": "阳台落地玻璃门外侧被严重错涂为刺眼的荧光翠绿与粉紫色彩灯杂色，室内地面原本温暖的米褐质感丢失(中度错色 C-L2，中度偏色 D-L2)。"
    },
    1323: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "窗台纱帘与窗框周围明媚温暖的明黄色阳光照射彻底丢失，被大面积错涂为冰冷空洞的灰白色冷调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "阳光明黄暖意完全退化褪色发灰。"}
        ],
        "note": "窗台纱帘与窗框周围明媚温暖的明黄色阳光照射彻底丢失，被大面积错涂为冰冷空洞的灰白色冷调(中度偏色 D-L2，中度欠饱和 E2-L2)。"
    },
    1324: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "餐盘下方原本清爽淡蓝色的桌布色彩褪色偏淡变灰，烤面包片烘烤焦黄感略显偏深。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "桌布浅蓝色调饱和度略有减弱。"}
        ],
        "note": "餐盘下方原本清爽淡蓝色的桌布色彩褪色偏淡变灰，烤面包片烘烤焦黄感略显偏深(轻度偏色 D-L1，轻度欠饱和 E2-L1)。"
    },
    1326: {
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 13 (1327, 1328, 1329, 1330, 1331, 1332)
    1327: {
        "defects": [],
        "note": "审查通过"
    },
    1328: {
        "defects": [],
        "note": "审查通过"
    },
    1329: {
        "defects": [],
        "note": "审查通过"
    },
    1330: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "卫生间左侧原本鲜艳醒目的红色隔断墙面被严重错涂为墨绿色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "右侧蓝色瓷砖墙面色彩偏差明显，整体偏暗偏杂。"}
        ],
        "note": "卫生间左侧原本鲜艳醒目的红色隔断墙面被严重错涂为墨绿色，右侧蓝色瓷砖墙面色彩偏差明显(严重错色 C-L3，严重偏色 D-L2)。"
    },
    1331: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "木质长椅上方窗台周围原本葱郁茂盛的翠绿爬山虎藤蔓被严重大面积错涂为紫红色花叶。"}
        ],
        "note": "木质长椅上方窗台周围原本葱郁茂盛的翠绿爬山虎藤蔓被严重大面积错涂为紫红色花叶(严重错色 C-L3)。"
    },
    1332: {
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 14 (1333, 1334, 1335, 1336, 1337, 1338)
    1333: {
        "defects": [],
        "note": "审查通过"
    },
    1334: {
        "defects": [],
        "note": "审查通过"
    },
    1335: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "蛋糕托盘上逼真皮鞋造型翻糖蛋糕的皮革棕褐色泽略显发红发浅。"}
        ],
        "note": "蛋糕托盘上逼真皮鞋造型翻糖蛋糕的皮革棕褐色泽略显发红发浅(轻度偏色 D-L1)。"
    },
    1336: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "孔雀华丽的蓝绿色羽毛边缘与颈部局部高光略显偏暗偏浓。"}
        ],
        "note": "孔雀华丽的蓝绿色羽毛边缘与颈部局部高光略显偏暗偏浓(轻度偏色 D-L1)。"
    },
    1337: {
        "defects": [],
        "note": "审查通过"
    },
    1338: {
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 15 (1339, 1340, 1341, 1342, 1343, 1344)
    1339: {
        "defects": [],
        "note": "审查通过"
    },
    1340: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "自行车后方背景原本璀璨鲜亮的金黄绿树林冠大面积严重脱色褪色，呈现暗淡的灰绿发灰质感。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "秋季金黄色树叶明度与纯度明显丧失。"}
        ],
        "note": "自行车后方背景原本璀璨鲜亮的金黄绿树林冠大面积严重脱色褪色，呈现暗淡的灰绿发灰质感(中度错色 C-L2，中度欠饱和 E2-L2)。"
    },
    1341: {
        "defects": [],
        "note": "审查通过"
    },
    1342: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "盛放香蕉果实的编织竹篮外围原本深色的木质桌面被严重错涂偏染为刺眼的洋红紫红色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "木质托盘与桌面环境色偏染严重。"}
        ],
        "note": "盛放香蕉果实的编织竹篮外围原本深色的木质桌面被严重错涂偏染为刺眼的洋红紫红色(中度错色 C-L2，中度偏色 D-L2)。"
    },
    1343: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "大白熊玩偶与婴儿身下的床单底色由原本温馨的米黄暖调被错涂偏染为浅青蓝色。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "床单米黄色被错涂为青蓝色。"}
        ],
        "note": "大白熊玩偶与婴儿身下的床单底色由原本温馨的米黄暖调被错涂偏染为浅青蓝色(中度偏色 D-L2，中度错色 C-L2)。"
    },
    1344: {
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 16 (1345, 1346, 1347, 1348, 1350, 1351)
    1345: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "雪场滑雪者身穿的原声明亮橘黄色滑雪防寒服明显褪色发浅，饱和度有所降低。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "滑雪防寒服橘黄色泽略偏米褐色。"}
        ],
        "note": "雪场滑雪者身穿的原声明亮橘黄色滑雪防寒服明显褪色发浅，饱和度有所降低(轻度欠饱和 E2-L1，轻度偏色 D-L1)。"
    },
    1346: {
        "defects": [],
        "note": "审查通过"
    },
    1347: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "网球拍拍线上放置的原本鲜艳亮橙粉色的网球被严重错涂为荧光黄绿色。"}
        ],
        "note": "网球拍拍线上放置的原本鲜艳亮橙粉色的网球被严重错涂为荧光黄绿色(中度错色 C-L2)。"
    },
    1348: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "会议室主席台后方原本深灰色的背景板与人物所处环境被错涂偏染为较重的红褐色。"}
        ],
        "note": "会议室主席台后方原本深灰色的背景板与人物所处环境被错涂偏染为较重的红褐色(轻度偏色 D-L1)。"
    },
    1350: {
        "defects": [],
        "note": "审查通过"
    },
    1351: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "牧场草坪原本鲜绿葱郁的青草色彩略显偏暗偏黄，近处黄牛毛色光泽稍显单调。"}
        ],
        "note": "牧场草坪原本鲜绿葱郁的青草色彩略显偏暗偏黄，近处黄牛毛色光泽稍显单调(轻度偏色 D-L1)。"
    },

    # Sheet 17 (1352, 1353, 1354, 1355, 1356, 1357)
    1352: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "红色停止标志牌周围原本青翠的松针林木被严重错涂为焦黄红褐色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "树林环境整体呈现秋季深红偏色，标志牌红色显暗发旧。"}
        ],
        "note": "红色停止标志牌周围原本青翠的松针林木被严重错涂为焦黄红褐色，标志牌红色显暗发旧(中度错色 C-L2，中度偏色 D-L2)。"
    },
    1353: {
        "defects": [],
        "note": "审查通过"
    },
    1354: {
        "defects": [],
        "note": "审查通过"
    },
    1355: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "飞行客机背景原本纯净湛蓝的晴朗蓝天被彻底错涂脱色为灰暗单调的黄灰阴天。"},
            {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "蓝天色彩彻底退化丧失，整体呈现死灰铅灰色。"}
        ],
        "note": "飞行客机背景原本纯净湛蓝的晴朗蓝天被彻底错涂脱色为灰暗单调的黄灰阴天(严重错色 C-L3，严重欠饱和 E2-L3)。"
    },
    1356: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "马厩木质围栏与矮种马皮毛整体被错涂偏染为较明显的红褐色调。"}
        ],
        "note": "马厩木质围栏与矮种马皮毛整体被错涂偏染为较明显的红褐色调(轻度偏色 D-L1)。"
    },
    1357: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "餐桌上玻璃杯中原本鲜红晶莹的果汁饮品被严重错涂为暗褐色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "鲜牛肉切片色泽略偏淡粉，生鲜质感稍弱。"}
        ],
        "note": "餐桌上玻璃杯中原本鲜红晶莹的果汁饮品被严重错涂为暗褐色，鲜牛肉切片色泽略偏淡(中度错色 C-L2，轻度偏色 D-L1)。"
    },

    # Sheet 18 (1358, 1359, 1360, 1361, 1362, 1363)
    1358: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "室内长颈鹿背后的石壁与周围环境被大面积严重错涂偏染为浓重的红褐色调。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "石壁原本清爽的青绿自然色调被误涂为焦赭红褐色。"}
        ],
        "note": "室内长颈鹿背后的石壁与周围环境被大面积严重错涂偏染为浓重的红褐色调(中度偏色 D-L2，中度错色 C-L2)。"
    },
    1359: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "酒店客房内原本中性明亮的室内照明被严重过度渲染为刺眼浓烈的红橙暖光，墙面与人物衬衫严重偏色。"},
            {"id": "E1", "name": "过饱和", "severity": "L2", "description": "室内暖红光照饱和度极度浓烈刺眼。"}
        ],
        "note": "酒店客房内原本中性明亮的室内照明被严重过度渲染为刺眼浓烈的红橙暖光，墙面与人物衬衫严重偏色(中度偏色 D-L2，中度过饱和 E1-L2)。"
    },
    1360: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "木案板上切开的苹果果肉原本新鲜清爽的乳白色被严重错涂偏染为暗黄褐色。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "苹果切面色泽严重变暗变黄，显现氧化腐败质感。"}
        ],
        "note": "木案板上切开的苹果果肉原本新鲜清爽的乳白色被严重错涂偏染为暗黄褐色(中度错色 C-L2，中度偏色 D-L2)。"
    },
    1361: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "卫生间小便池周围原本冷色调的浅蓝瓷砖墙面被严重错涂为暖黄米色。"},
            {"id": "C", "name": "错色", "severity": "L2", "description": "冷青色瓷砖被错配为暖黄色调。"}
        ],
        "note": "卫生间小便池周围原本冷色调的浅蓝瓷砖墙面被严重错涂为暖黄米色(中度偏色 D-L2，中度错色 C-L2)。"
    },
    1362: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "西餐餐盘中原本鲜艳亮丽的熟胡萝卜与配菜严重褪色发灰，酱汁与土豆泥偏暗冷。"},
            {"id": "D", "name": "偏色", "severity": "L2", "description": "热菜原本浓郁诱人的暖色调褪化变冷。"}
        ],
        "note": "西餐餐盘中原本鲜艳亮丽的熟胡萝卜与配菜严重褪色发灰，酱汁与土豆泥偏暗冷(中度欠饱和 E2-L2，中度偏色 D-L2)。"
    },
    1363: {
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 19 (1364, 1365, 1366, 1367, 1368, 1369)
    1364: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "大象身后悬挂的原本鲜艳红色的丰容玩具严重脱色退化为暗褐死灰，周围绿草略显暗沉。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "红色织物玩具严重脱色失去色彩。"}
        ],
        "note": "大象身后悬挂的原本鲜艳红色的丰容玩具严重脱色退化为暗褐死灰，周围绿草略显暗沉(中度错色 C-L2，中度欠饱和 E2-L2)。"
    },
    1365: {
        "defects": [],
        "note": "审查通过"
    },
    1366: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "厨房窗台上摆放的小花瓶内原本鲜艳明黄色的插花花朵严重脱色为灰白色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "黄色花瓣色彩完全丢失褪白。"}
        ],
        "note": "厨房窗台上摆放的小花瓶内原本鲜艳明黄色的插花花朵严重脱色为灰白色(中度错色 C-L2，中度欠饱和 E2-L2)。"
    },
    1367: {
        "defects": [],
        "note": "审查通过"
    },
    1368: {
        "defects": [],
        "note": "审查通过"
    },
    1369: {
        "defects": [],
        "note": "审查通过"
    },

    # Sheet 20 (1371, 1372, 1373, 1374, 1375, 1376)
    1371: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "赛马场跑道泥土地表色泽偏鲜亮黄橙色，远景树冠色调略显失真偏蓝。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "红土赛道略微偏黄。"}
        ],
        "note": "赛马场跑道泥土地表色泽偏鲜亮黄橙色，远景树冠色调略显失真偏蓝(轻度偏色 D-L1，轻度错色 C-L1)。"
    },
    1372: {
        "defects": [],
        "note": "审查通过"
    },
    1373: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "电脑书桌上方墙壁由原本温馨的米黄暖调被错涂偏染为冷淡青蓝灰色，小相框边缘略有偏色。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "墙壁整体色调偏冷变青。"}
        ],
        "note": "电脑书桌上方墙壁由原本温馨的米黄暖调被错涂偏染为冷淡青蓝灰色，小相框边缘略有偏色(轻度偏色 D-L1，轻度错色 C-L1)。"
    },
    1374: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "甜品盘中盛放巧克力蛋糕的白色瓷盘与刀叉金属反光略显偏冷偏青。"}
        ],
        "note": "甜品盘中盛放巧克力蛋糕的白色瓷盘与刀叉金属反光略显偏冷偏青(轻度偏色 D-L1)。"
    },
    1375: {
        "defects": [],
        "note": "审查通过"
    },
    1376: {
        "defects": [],
        "note": "审查通过"
    }
}


def main():
    print(f"Total reviews in Batch 06 dictionary: {len(BATCH_06_REVIEWS)}")
    assert len(BATCH_06_REVIEWS) == 120, f"Expected 120, got {len(BATCH_06_REVIEWS)}"

    # Check passes vs defect counts
    passes = [tid for tid, r in BATCH_06_REVIEWS.items() if len(r['defects']) == 0]
    defects = [tid for tid, r in BATCH_06_REVIEWS.items() if len(r['defects']) > 0]
    print(f"Pass count: {len(passes)}, Grounded defect count: {len(defects)}")

    # 1. Save grounding audit JSON
    audit_path = "LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_06.json"
    os.makedirs(os.path.dirname(audit_path), exist_ok=True)
    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump(BATCH_06_REVIEWS, f, ensure_ascii=False, indent=2)
    print(f"Saved audit reviews to {audit_path}")

    # 2. Update reviewed_1_10000_all.json
    all_path = "LS_lcad_reviewer/exports/reviewed_1_10000_all.json"
    with open(all_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    updated_all = 0
    for ann in all_data["annotations"]:
        tid = ann["human_review"]["task_id"]
        if tid in BATCH_06_REVIEWS:
            r = BATCH_06_REVIEWS[tid]
            ann["defects"] = r["defects"]
            ann["review_note"] = r["note"]
            ann["review_status"] = "已核验"
            updated_all += 1

    print(f"Updated {updated_all} tasks in {all_path}")
    with open(all_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    # 3. Update reviewed_1_10000_clean.json
    clean_path = "LS_lcad_reviewer/exports/reviewed_1_10000_clean.json"
    with open(clean_path, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    updated_clean = 0
    for ann in clean_data["annotations"]:
        tid = ann["human_review"]["task_id"]
        if tid in BATCH_06_REVIEWS:
            r = BATCH_06_REVIEWS[tid]
            ann["defects"] = r["defects"]
            ann["review_note"] = ""  # Clean version has empty review_note
            ann["review_status"] = "已核验"
            updated_clean += 1

    print(f"Updated {updated_clean} tasks in {clean_path}")
    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)

    print("Batch 06 updates successfully applied!")

if __name__ == "__main__":
    main()
