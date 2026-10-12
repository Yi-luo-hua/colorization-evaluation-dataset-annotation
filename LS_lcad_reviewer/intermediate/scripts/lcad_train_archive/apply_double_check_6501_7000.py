"""Apply Double Check updates for batch 6501-7000 pass tasks.
Updates reviewed_6501_7000, stream package, and full 1-10000 exports.
Follows the exact V4 schema contract from AGENTS.md.
"""
import json
import os
import shutil
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"
STREAMS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "streams"

# 38 Grounded Double Check Corrections for 6501-7000
DC_CORRECTIONS = {
    6509: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "厨房柜台下方原本为浅米色/灰白金属面的洗碗机门在LCAD生成图中被恶性错涂为刺眼醒目的高饱和荧光柠檬黄色，色相严重错移"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "厨房背景墙壁恶性偏深发黄，室内采光色温失衡"}
        ],
        "review_note": "Double Check复核改判：核查发现：厨房柜台下方洗碗机门被恶性错涂为刺眼醒目的高饱和荧光柠檬黄色，背景墙面偏深黄，改判错色(C-L2)与偏色(D-L1)。"
    },
    6527: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "卫生间青年身旁沙皮狗原本温暖红褐色的皮毛在LCAD生成图中被恶性错涂为阴暗发黑、冰冷死灰色的脏污毛发；青年裤子原本为卡其色被恶性错涂为浅蓝牛仔色"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "背景墙面偏暗偏芥末青黄"}
        ],
        "review_note": "Double Check复核改判：核查发现：沙皮狗温暖红褐色毛皮被错涂为阴冷死灰色，青年裤子错涂为浅蓝牛仔色，改判错色(C-L2)与偏色(D-L1)。"
    },
    6544: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "奥地利航空客机垂直尾翼上原本极其醒目纯正的大红与白色相间国旗涂装条纹在LCAD生成图中被恶性错涂为深蓝色与白色条纹，航司经典红白涂装遭到篡改"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "客机机身下部与机腹背光处略微发暗发灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：奥地利航空客机垂直尾翼鲜艳纯正红白相间国旗涂装条纹被恶性错涂为深蓝白色涂装，改判错色(C-L2)与偏色(D-L1)。"
    },
    6549: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "餐盘中油炸烤虾原本鲜艳诱人的红橙色外壳在LCAD生成图中严重脱色变暗，退化为发白、土黄发灰的暗淡熟虾(RedLoss=0.18)，食物新鲜度受损"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "青椒局部边缘偏暗发褐"}
        ],
        "review_note": "Double Check复核改判：核查发现：餐盘中油炸烤虾原本鲜艳诱人的红橙色严重脱色变暗为发白土灰色熟虾(RedLoss=0.18)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6569: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "办公桌面上EMR绿色封面文件夹在LCAD生成图中完全脱色褪变为淡天蓝灰白色，鲜明绿色完全丧失"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "桌面右侧红色书籍书脊与药瓶包装脱色发暗偏灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：桌面上EMR绿色文件夹严重脱色退化为淡天蓝灰白色，右侧红色书籍脱色发暗，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6597: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "网球场击球女运动员身穿的极其鲜艳纯正的大红色短袖T恤在LCAD生成图中被恶性错涂为发暗枯黄的脏土褐色与暗棕褐色，色相严重错移"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "女运动员面部肤色在强光下略微发暗发青"}
        ],
        "review_note": "Double Check复核改判：核查发现：网球场击球女运动员身穿的鲜艳大红色短袖T恤被恶性错涂为发暗枯黄土褐色，改判错色(C-L2)与偏色(D-L1)。"
    },
    6604: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "公园长椅后方木护栏原本为普通的暗红棕褐色，在LCAD生成图中被恶性错涂为鲜艳浅粉紫色；禁止宠物小狗标牌原本为深红底色被恶性错涂为亮深宝蓝色"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白色长椅椅面略微泛浅紫冷光"}
        ],
        "review_note": "Double Check复核改判：核查发现：公园木护栏与禁止宠物小狗标牌被恶性错涂为浅粉紫色与亮深宝蓝色，改判错色(C-L2)与偏色(D-L1)。"
    },
    6616: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "卫生间毛巾架上挂着的深墨绿色毛巾在LCAD生成图中被恶性错涂为暗焦红褐色与深巧克力棕褐色；墙面嫩绿色复古瓷砖被错涂褪变为冷白灰瓷砖"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "洗手台与腰线瓷砖整体色相偏暖偏暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：卫生间毛巾架上深墨绿色毛巾被恶性错涂为暗焦红褐色，嫩绿复古瓷砖泛白变色，改判错色(C-L2)与偏色(D-L1)。"
    },
    6646: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "雪原上方原本清澈高远的晴朗蔚蓝天空在LCAD生成图中完全脱色褪白，蜕变为惨白色冷灰天幕(Rsat=0.36)，天空生机与色彩被大面积抹杀"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "雪地阴影与远景冰面整体偏冷暗沉"}
        ],
        "review_note": "Double Check复核改判：核查发现：雪原上方晴朗蔚蓝天空完全脱色褪白蜕变为惨白色冷灰天幕(Rsat=0.36)，改判欠饱和(E2-L2)与偏色(D-L1)。"
    },
    6664: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "马戏团大帐篷顶部原本浓郁纯正的洋红深红色装饰条纹与正前方标语英文字在LCAD生成图中严重脱色发暗，退化为暗紫褐色与无色浅灰(RedLoss=0.19)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "前景草地受暗光影响局部发焦泛黄"}
        ],
        "review_note": "Double Check复核改判：核查发现：马戏团大帐篷顶部鲜红装饰条纹与标语字严重脱色蜕变为暗紫褐与浅灰白(RedLoss=0.19)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6672: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "小男孩身前趴卧浮板原本鲜艳亮丽的大红色前沿在LCAD生成图中彻底脱色发白，褪变为惨白色与浅灰白(RedLoss=0.24, Rsat=2.05)，鲜红完全丧失"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "浮板背面彩绘图案局部发暗偏黑"}
        ],
        "review_note": "Double Check复核改判：核查发现：小男孩身前趴卧浮板原本鲜艳亮丽的大红色前沿彻底脱色蜕变为惨白灰白(RedLoss=0.24)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6673: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街道铁栅栏下方花坛中原本盛开的大片鲜艳洋红粉紫色小花在LCAD生成图中严重脱色发暗，退化为暗灰绿色的枯槁杂草色(RedLoss=0.18, Rsat=0.47)，花朵鲜艳度完全被剥夺"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "牵狗路人所穿的深蓝色裤子发暗偏黑"}
        ],
        "review_note": "Double Check复核改判：核查发现：街道铁栅栏下方花坛中盛开的大片鲜艳洋红粉紫小花严重脱色退化为暗灰杂草色(RedLoss=0.18)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6676: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "复古房间左侧原本刷有鲜艳纯正草绿色油漆的行李箱货架在LCAD生成图中被恶性错涂为暗黄木色与土黄色货架，草绿完全错涂"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "房间木地板与右侧木椅整体泛暗发灰褐色"}
        ],
        "review_note": "Double Check复核改判：核查发现：房间左侧原本鲜艳纯正的草绿色复古行李架被恶性错涂为暗黄木色与土黄色，改判错色(C-L2)与偏色(D-L1)。"
    },
    6677: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "厨房餐桌后方靠墙的深酒红色卡座沙发靠背在LCAD生成图中被恶性错涂为墨绿青黑色，红色调完全被冷绿青黑色篡改(RedLoss=0.16)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白色餐桌桌面在室内光照下略显偏灰发冷"}
        ],
        "review_note": "Double Check复核改判：核查发现：餐桌后方靠墙的深酒红色卡座沙发靠背被恶性错涂为墨绿青黑色(RedLoss=0.16)，改判错色(C-L2)与偏色(D-L1)。"
    },
    6703: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "桌面花篮正中盛开的火红色百合花瓣在LCAD生成图中严重脱色发绿发灰，退化为暗淡泛绿的无色花瓣(RedLoss=0.14, Rsat=0.55)，花瓣鲜红色完全丧失"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "花篮边缘配叶草绿色泽暗淡发焦"}
        ],
        "review_note": "Double Check复核改判：核查发现：桌面花篮正中盛开的火红色百合花瓣严重脱色泛绿退化为暗灰无色花瓣(RedLoss=0.14)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6704: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "盛装巡游骆驼身上原本披挂的极其鲜艳夺目的彩色挂毯与流苏在LCAD生成图中大面积脱色蜕变，退化为黑灰色暗沉布条(RedLoss=0.17)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "骆驼头部旗帜原本鲜艳明亮的橙色条纹脱色发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：盛装巡游骆驼身上披挂的鲜艳多色彩色挂毯与流苏大面积脱色蜕变黑灰暗沉布条(RedLoss=0.17)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6713: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "停机坪围栏处放置的原本极其鲜艳抢眼的洋红粉紫色行李箱在LCAD生成图中严重脱色发暗，退化为深褐灰黑色与脏污泥色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "围栏广告牌上的红色英文字样略微脱色暗淡"}
        ],
        "review_note": "Double Check复核改判：核查发现：停机坪围栏处放置的鲜艳洋红粉紫色行李箱严重脱色退化为深褐灰黑色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6733: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "客厅中央原本温暖纯正的红砖砌筑壁炉在LCAD生成图中被恶性错涂为阴冷青灰色、水泥青灰色砖石壁炉，红砖质感与色相完全颠覆"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "地毯与皮质沙发暗部略泛阴冷灰光"}
        ],
        "review_note": "Double Check复核改判：核查发现：客厅中央原本温暖纯正的红砖砌筑壁炉被恶性错涂为阴冷青灰色水泥砖石，改判错色(C-L2)与偏色(D-L1)。"
    },
    6741: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "铁桥旁河畔长椅原本鲜艳大红色的木质椅背与椅面在LCAD生成图中完全脱色褪暗，退化为灰暗泥土灰黑与枯灰褐色(Rsat=0.63)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "河流水体在桥下阴影处轻微泛灰偏绿"}
        ],
        "review_note": "Double Check复核改判：核查发现：铁桥旁河畔长椅原本鲜艳大红色的椅背与椅面完全脱色退化为灰暗泥土灰黑(Rsat=0.63)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6745: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "卫生间洗手台上方与马桶旁悬挂的一整排鲜艳明黄色毛巾在LCAD生成图中完全脱色褪白，退化为纯白与淡灰白色毛巾，明黄色彻底丢失"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "卫生间洗手盆台面与地板阴影略显发暗偏紫"}
        ],
        "review_note": "Double Check复核改判：核查发现：卫生间洗手台上方与马桶旁悬挂的一整排鲜艳明黄色毛巾完全脱色褪白为纯灰白色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6756: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "英国航空波音747客机垂直尾翼上经典的红蓝白米字旗涂装中，鲜艳纯正的红色折线在LCAD生成图中被恶性错涂为深蓝色与深黑灰，英国国旗涂装色相遭到破坏"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "机场停机坪跑道地面略微发暗发黄"}
        ],
        "review_note": "Double Check复核改判：核查发现：英国航空巨型客机垂直尾翼鲜艳红蓝米字旗涂装中的红色条纹被恶性错涂为深蓝黑灰，改判错色(C-L2)与偏色(D-L1)。"
    },
    6771: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "双门冰箱下层保鲜抽屉内原本整齐放置的鲜艳夺目的彩色易拉罐饮料与果汁包装在LCAD生成图中严重脱色发暗，退化为无色灰黑与浅灰"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "冰箱白色内衬塑料在阴影处轻微泛黄"}
        ],
        "review_note": "Double Check复核改判：核查发现：双门冰箱下层保鲜抽屉内原本鲜艳夺目的彩色易拉罐与果汁包装严重脱色发暗，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6801: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "办公桌左侧笔记本电脑屏幕上原本显示的清爽明亮的纯深天蓝色桌面壁纸/程序界面在LCAD生成图中完全脱色褪变为黑灰色终端无色屏幕"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "右侧笔记本屏幕白色文字局部偏暗发蓝"}
        ],
        "review_note": "Double Check复核改判：核查发现：办公桌左侧笔记本电脑屏幕鲜艳纯正的深天蓝色壁纸界面严重脱色退化为黑灰色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6818: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "折叠大行自行车车架横梁上放置的原本鲜明亮丽的黄色装备包/水壶套在LCAD生成图中严重脱色褪白，退化为惨白灰白无色(Rsat=0.51)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "红色自行车车架在金属阴影处略带发乌"}
        ],
        "review_note": "Double Check复核改判：核查发现：折叠大行自行车车架横梁上原本鲜明亮丽的黄色装备包严重脱色褪白为惨白色(Rsat=0.51)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6839: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "狗窝中熟睡小狗背部原本温暖浓郁的金黄棕色毛发在LCAD生成图中完全脱色退化，蜕变为惨白发灰、毫无生气的浅白毛色(Rsat=0.48)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "狗窝红色软垫边缘略微泛暗紫灰色"}
        ],
        "review_note": "Double Check复核改判：核查发现：狗窝中熟睡小狗背部原本温暖浓郁的金黄棕色毛发完全脱色退化为惨白灰白色(Rsat=0.48)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6840: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "铁轨上方行驶的电力机车车头原本极其鲜艳纯正的深海蓝色经典涂装在LCAD生成图中完全脱色发暗，退化为冷青灰色与铁灰色(Rsat=0.61)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "铁路信号架与铁轨金属在阳光下暗淡发焦"}
        ],
        "review_note": "Double Check复核改判：核查发现：铁轨上行驶的电力机车车头鲜艳深海蓝色涂装完全脱色褪变为冷青灰铁灰色(Rsat=0.61)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6850: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "腾空滑板少年身穿原本鲜明亮丽的明黄色连帽短袖上衣在LCAD生成图中完全脱色蜕变，退化为苍白浅灰白无色汗衫"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "滑板场水泥斜坡地面阴影略带偏冷青灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：腾空滑板少年身穿的鲜明亮丽黄色上衣完全脱色蜕变苍白浅灰白，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6896: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "母牛身后翻扣在草地上的小船原本极其鲜艳的大红色船底涂装在LCAD生成图中严重脱色发暗，退化为暗紫灰色与脏污土灰"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "棕色母牛皮毛在强光下略微发焦泛暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：母牛身后翻扣小船原本鲜艳的大红色船底涂装严重脱色退化为暗紫灰色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6898: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街头台阶滑板少年身穿纯正鲜艳的亮红白格纹衬衫在LCAD生成图中严重脱色褪淡；背景路边醒目的橙黄色警示路锥与施工围栏完全脱色蜕变灰黑暗淡(RedLoss=0.31)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "大理石台阶与路面阴影略微泛冷灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：街头滑板少年鲜艳红白格纹衬衫与背景橙黄色路锥施工标牌严重脱色蜕变灰黑暗淡(RedLoss=0.31)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6912: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "网球场原本平整鲜艳纯正的砖红橙色红土地面在LCAD生成图中完全脱色褪白，退化为惨白灰白色的水泥硬地(RedLoss=0.17, Rsat=0.43)，红土场地质感彻底丧失"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "发球教练运动服与手持网球色相略暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：网球场平展鲜艳的砖红橙色红土地面完全脱色退化为惨白灰白水泥硬地(RedLoss=0.17)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6931: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "公园长椅上坐着的少女原本鲜艳亮丽的橘红亮橙假发在LCAD生成图中严重发灰暗淡；身旁女子长裙上的鲜艳粉红色大面积脱色蜕变发灰"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "站立女子天蓝裙装局部发暗偏冷"}
        ],
        "review_note": "Double Check复核改判：核查发现：公园长椅少女鲜艳亮橙红假发与身旁女子粉红长裙严重脱色蜕变暗灰泛黄，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6939: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "棒球投手白色棒球服背面原本鲜艳纯正的大红色39号背号在LCAD生成图中被恶性错涂为深蓝色，大红数字变深蓝；背景看台广告牌上的鲜红文字也被错涂为暗紫蓝色"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "投球土丘泥土橙色略微泛暗发焦"}
        ],
        "review_note": "Double Check复核改判：核查发现：棒球投手球衣背面原本鲜艳纯正的大红39号背号被恶性错涂为深蓝色，广告牌红字变紫蓝，改判错色(C-L2)与偏色(D-L1)。"
    },
    6950: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "草坪中央极其醒目鲜艳的大红色消火栓在LCAD生成图中被恶性错涂为亮宝蓝色；消火栓后方原本纯正大红色的立杆警示标牌完全脱色蜕变为暗铁黑灰色(RedLoss=0.30)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "后方草坪草色略泛暗偏枯黄"}
        ],
        "review_note": "Double Check复核改判：核查发现：草坪中央鲜艳大红消火栓被恶性错涂为亮宝蓝色，红色警示标牌完全脱色蜕变铁黑灰(RedLoss=0.30)，改判错色(C-L2)与偏色(D-L1)。"
    },
    6962: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "人行道旁配电/环卫设施表面原本鲜艳纯正的生机草绿色外壳顶盖在LCAD生成图中严重脱色蜕变，退化为脏污深黑灰色与水泥灰，绿色生机被剥夺"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "人行道铺地红砖色泽略带泛暗发焦"}
        ],
        "review_note": "Double Check复核改判：核查发现：人行道旁设施原本鲜艳生机的草绿色外壳顶盖严重脱色蜕变为脏污深黑灰色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6986: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "烘焙店甜甜圈玻璃展柜边缘原本贴着的绿白相间说明标签纸条在LCAD生成图中被恶性错涂为刺眼醒目的荧光大红色与洋红色色带，色相完全错乱"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "展柜内甜甜圈与面包色相略微泛暗泛黄"}
        ],
        "review_note": "Double Check复核改判：核查发现：烘焙甜甜圈玻璃展柜边缘原本绿白相间的标价说明纸条被恶性错涂为刺目大红洋紫色，改判错色(C-L2)与偏色(D-L1)。"
    },
    6991: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "车窗视角外侧车体原本亮丽纯正的鲜黄色涂装在LCAD生成图中完全脱色褪白，退化为惨白冷灰色的无色外壳，鲜艳黄色被完全抹杀"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "车窗内饰座椅在阴影中略带泛冷偏灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：车厢外侧车体原本亮丽纯正的鲜黄色涂装完全脱色蜕变为惨白冷灰色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    6994: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "客厅正前方原本平整鲜艳的生机翠绿色背景墙壁在LCAD生成图中被恶性错涂为灰暗发脏的泥土黄褐色与阴暗水泥灰，墙面色相严重失真(RedLoss=0.16)"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "茶几上摆放的鲜红色物品脱色发暗欠饱和"}
        ],
        "review_note": "Double Check复核改判：核查发现：客厅正前方生机翠绿色的背景墙壁被恶性错涂为灰暗发脏的泥土黄褐色，茶几红物发暗，改判错色(C-L2)与欠饱和(E2-L1)。"
    },
    6997: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "前方骑行涉水大象的象夫身上穿戴的原本极其纯正的湖绿/草绿色上衣在LCAD生成图中被恶性错涂为发暗的肉粉红褐色；脚下清澈河流被恶性错涂为浑浊暗黄泥水"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "对岸草地与树木整体略微泛暗发焦"}
        ],
        "review_note": "Double Check复核改判：核查发现：大象骑手象夫原本纯正的湖绿草绿色上衣被恶性错涂为发暗肉粉红褐色，河水偏泥黄，改判错色(C-L2)与偏色(D-L1)。"
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
    stream_path = STREAMS_DIR / "tasks_lcad_6501_7000_stream.json"
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
    print("Applying Double Check updates for 6501-7000...")
    
    # 1. Update batch 6501-7000
    b_path = EXPORTS_DIR / "reviewed_6501_7000_20260930_155809.json"
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

    print("Double check updates for 6501-7000 completed successfully!")

if __name__ == "__main__":
    main()
