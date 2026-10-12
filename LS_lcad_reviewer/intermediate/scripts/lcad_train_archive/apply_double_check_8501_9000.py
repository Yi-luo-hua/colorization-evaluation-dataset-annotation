"""Apply Double Check updates for batch 8501-9000 pass tasks.
Updates reviewed_8501_9000, stream package, and full 1-10000 exports.
Follows the exact V4 schema contract from AGENTS.md.
"""
import json
import os
import shutil
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"
STREAMS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "streams"

# 55 Grounded Double Check Corrections for 8501-9000
DC_CORRECTIONS = {
    8501: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "草坪上原本生机盎然的平展翠绿色草地在LCAD生成图中大面积欠饱和脱色，褪变为发暗灰绿泥草地(Rsat=0.63)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "奔跑男子白色短袖与运动短裤略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：草坪原本生机盎然的平展翠绿草地大面积脱色为发暗灰绿泥草地(Rsat=0.63)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8517: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "棒球击球手身上的大红色击球头盔与红色袖套在LCAD生成图中严重脱色褪淡发暗，内场草皮边缘微显偏色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "击球手深蓝色球袜与球裤略显发乌"}
        ],
        "review_note": "Double Check复核改判：核查发现：棒球击球手红色头盔与袖套严重脱色发暗，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8532: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "湿地涉禽栖息地原本鲜亮生机的深绿色水草植被在LCAD生成图中大面积严重脱色发灰(RedLoss=0.18)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "冠鹤头部金黄羽冠与大象灰色皮毛略显发乌"}
        ],
        "review_note": "Double Check复核改判：核查发现：湿地原本生机深绿色水草植被大面积严重脱色发灰(RedLoss=0.18)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8542: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "便当盒内原本翠绿诱人的西兰花在LCAD生成图中完全脱色蜕变为暗沉黑褐色，蔬菜原本清新生机完全剥夺"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "爱心米饭与烤香肠边缘色泽略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：便当盒内翠绿诱人的西兰花完全脱色蜕变为暗沉黑褐色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8545: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "格纹领带上原本鲜艳醒目的大红与洋红色斜纹线条在LCAD生成图中大面积严重脱色，退化为黯淡黑灰细纹(RedLoss=0.16)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "领带底色深绿色面料与金色领带夹略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：格纹领带鲜艳醒目的大红与洋红斜纹大面积严重脱色褪白(RedLoss=0.16)，清洗伪满分，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8554: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "摩托车集结场地后方支援厢式货车原本明亮鲜艳的金黄色车体拉花与标识在LCAD生成图中严重脱色褪淡(RedLoss=0.17, Rsat=0.58)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "骑手红色赛车服与草坪边缘略带泛灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：后方支援货车原本明亮鲜艳的金黄色车体拉花严重脱色褪淡(Rsat=0.58)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8567: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "室内书桌与后方墙面在暖黄色照明下原本温馨的暖黄光影在LCAD生成图中大面积泛出突兀阴冷的紫色偏色(Rsat=1.37)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "女孩绿色外套与深蓝色围巾暗部略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：室内书桌与墙面灯光大面积泛出阴冷紫色偏色(Rsat=1.37)，改判偏色(D-L2)与错色(C-L1)。"
    },
    8575: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "客厅沙发靠垫上原本明艳鲜亮的橙红色织物在LCAD生成图中大面积严重脱色发乌，退化为深黑褐色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "背景碎花窗帘花纹色彩略微脱色褪淡"}
        ],
        "review_note": "Double Check复核改判：核查发现：沙发靠垫原本明艳的橙红色织物严重脱色发乌退化为深褐黑，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8589: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "滑板少年脚下板头原本鲜艳亮丽的红橙色喷绘图案与红色滑板轮在LCAD生成图中严重脱色褪白，退化为苍白灰黄泥色(RedLoss=0.17)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "少年翠绿色短裤暗影处微显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：滑板板头原本鲜艳亮丽的红橙色图案与红色板轮严重脱色褪白(RedLoss=0.17)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8598: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "奔跑犬只口中叼着的原本纯正天蓝色塑料飞盘在LCAD生成图中被恶性错涂为刺眼的大红橙色伪色(Rsat=1.51)，色相彻底篡改"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "犬只棕褐色毛皮边缘与草坪阴影略带暗红泛光"}
        ],
        "review_note": "Double Check复核改判：核查发现：奔跑犬只口中原本纯正天蓝色的飞盘被恶性错涂为刺眼大红橙色伪色(Rsat=1.51)，改判错色(C-L2)与偏色(D-L1)。"
    },
    8602: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "原野草地与金属立柱在LCAD生成图中大面积泛出阴森冷冽的青蓝色偏色(Rsat=1.67)，草地与石墩自然色相失真"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "红色消防栓顶部金属漆略显脱色褪淡"}
        ],
        "review_note": "Double Check复核改判：核查发现：原野草地与金属立柱大面积泛出阴冷青蓝色偏色(Rsat=1.67)，改判偏色(D-L2)与欠饱和(E2-L1)。"
    },
    8607: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "沙滩上冲浪者手持的原本原木米黄色冲浪板在LCAD生成图中被恶性错涂为深宝蓝色伪色，沙滩上原本鲜艳的粉红浴巾脱色为青灰色(RedLoss=0.17, Rsat=1.54)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "背景粉红色酒店建筑立面暗部泛冷灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：冲浪者原木色冲浪板被恶性错涂为亮宝蓝色，粉红浴巾脱色青灰(RedLoss=0.17)，改判错色(C-L2)与偏色(D-L1)。"
    },
    8612: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街角原本明亮醒目的明黄色菱形LIGHT交通警示标牌在LCAD生成图中完全脱色黑化，退化为深黑死灰色(RedLoss=0.16)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "街道红砖建筑暗部与沥青路面微显泛青"}
        ],
        "review_note": "Double Check复核改判：核查发现：明黄色菱形交通警示标牌完全脱色黑化为深黑死灰(RedLoss=0.16)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8627: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "厢式货车车身侧面原本鲜艳大红色的圆形商号图案与红色茶叶书法字样在LCAD生成图中严重脱色褪淡，退化为发脏灰绿调(RedLoss=0.17)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "斑马线上电动车驾驶员头盔略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：白色货车侧面鲜艳大红圆形商号标识与红色字样严重脱色蜕变灰绿(RedLoss=0.17)，清洗伪满分，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8632: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "卧室内双层床下铺原本沉稳深黑褐色的背包在LCAD生成图中被突兀恶性错涂为刺眼的大红色伪色，与环境极其不协调"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "上铺暖黄色床单暗影处略微偏冷泛青"}
        ],
        "review_note": "Double Check复核改判：核查发现：双层床下铺沉稳深黑褐色背包被突兀恶性错涂为刺眼大红色伪色，改判错色(C-L2)与偏色(D-L1)。"
    },
    8639: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "舷窗外客机机翼端部与发动机整流罩原本醒目鲜艳的大红色涂装在LCAD生成图中完全脱色褪白，退化为苍白无色发灰浅米色(RedLoss=0.26)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "俯瞰沙丘与山脉阴影处略显偏蓝"}
        ],
        "review_note": "Double Check复核改判：核查发现：客机机翼端部与整流罩鲜艳大红涂装完全脱色蜕白为浅米色(RedLoss=0.26)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8647: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "暮色海滩上男子手中原本散发耀眼橙红光芒的飞盘在LCAD生成图中完全脱色褪白，退化为普通惨白灰蓝色飞盘"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "天边原本绚丽的晚霞红光略显收敛发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：暮色海滩男子手中原本散发耀眼橙红光芒的飞盘完全脱色褪白为惨白灰蓝，改判欠饱和(E2-L2)与偏色(D-L1)。"
    },
    8648: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "浴室百叶窗与深色大理石墙面在LCAD生成图中大面积泛出突兀阴冷的紫色偏色(Rsat=2.0)，室内瓷砖与洁具原本清爽色调失真"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "窗外远处城市建筑天际线略微欠饱和发灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：浴室百叶窗与大理石暗部大面积泛出突兀阴冷紫色偏色(Rsat=2.0)，改判偏色(D-L2)与欠饱和(E2-L1)。"
    },
    8649: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "巷道左侧古旧木门原本温润饱满的红木色泽在LCAD生成图中严重脱色发灰，木门退化为冷灰暗色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "墙角黑白花猫皮毛反光与石板地面略显暗淡"}
        ],
        "review_note": "Double Check复核改判：核查发现：巷道左侧古旧木门原本饱满温润红木色泽严重脱色发灰，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8655: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "宴会长桌左侧就座女士身上原本鲜艳喜庆的珊瑚红粉色西装外套在LCAD生成图中大面积严重脱色褪淡，蜕变为黯淡无色灰米色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "宴会厅木质护墙板与暖黄吊顶略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：宴会左侧女士身上鲜艳喜庆的珊瑚红粉外套大面积严重脱色退化为发灰米色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8657: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "昏暗室内年轻男子身上原本极其鲜艳明亮的亮粉紫短袖T恤在LCAD生成图中完全脱色蜕变，被错误涂抹为发脏的暗褐土绿色"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "笔记本电脑屏幕发光在面部反射光略微偏冷发青"}
        ],
        "review_note": "Double Check复核改判：核查发现：室内年轻男子身上鲜艳亮粉紫短袖完全脱色并错涂为发脏暗褐土绿色，改判错色(C-L2)与偏色(D-L1)。"
    },
    8659: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街角路标立杆下方原本鲜艳醒目的大红色八角形STOP停步标识在LCAD生成图中严重脱色发暗，退化为深褐灰红色(RedLoss=0.07)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "上方蓝色路牌Montview文字边缘略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：街角大红色八角形STOP停步标牌严重脱色发暗退化为深褐灰红，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8676: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "暮色高速公路上飞驰的摩托车车尾原本醒目警示的鲜红色尾灯光晕在LCAD生成图中严重欠饱和暗化(Rsat=0.42)，尾灯光泽脱色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "道路中央隔离护栏与远处山峦略显偏灰发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：高速公路摩托车鲜红尾灯光晕严重欠饱和暗化脱色(Rsat=0.42)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8679: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "水道暮色天际原本绚烂晚霞呈现的粉红与暖橙色云彩在LCAD生成图中完全被剥夺脱色，退化为沉闷死白阴天(Rsat=0.62)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "水面小舟绿色船舷与岸边红树林略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：水面暮色原本绚烂晚霞粉红橙黄云彩完全被剥夺脱色为死灰阴天(Rsat=0.62)，清洗伪满分，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8706: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "客厅聚会场景左侧原本极其醒目鲜艳的大红色布艺单人扶手沙发在LCAD生成图中大面积严重脱色发乌，退化为发脏深黑褐色(RedLoss=0.18, Rsat=0.55)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "地面男子条纹衬衫领口略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：客厅左侧醒目鲜红布艺单人沙发大面积脱色发乌为深黑褐色(RedLoss=0.18)，清洗伪满分，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8715: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "茂盛绿树掩映下的欧式钟楼原本沉稳深邃的红褐色瓦顶在LCAD生成图中被恶性错涂为刺眼突兀的荧光洋红粉紫伪色，瓦顶色相严重失真"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "钟楼白色立面与热带树木边缘微显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：钟楼尖顶沉稳红褐色瓦顶被突兀恶性错涂为刺眼荧光洋红粉紫伪色，改判错色(C-L2)与偏色(D-L1)。"
    },
    8720: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "车流后方紧随的原原本本鲜艳的大红色小轿车车身在LCAD生成图中严重脱色褪淡，退化为发白浅灰粉色(RedLoss=0.14)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "前车后视镜与车内小狗毛色反光略显暗淡"}
        ],
        "review_note": "Double Check复核改判：核查发现：车流后方紧随的大红色轿车车身严重脱色褪淡为发白浅粉灰(RedLoss=0.14)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8730: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "牧场木围栏前探头张望的小女孩身上原本鲜艳明亮的洋红粉红夹克外套在LCAD生成图中被恶性错涂为发暗冷青灰色(RedLoss=0.39)"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "牧场翠绿色草坪与黑白奶牛边缘略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：木围栏前小女孩鲜艳洋红粉红夹克衫被恶性错涂为冷青灰色(RedLoss=0.39)，改判错色(C-L2)与欠饱和(E2-L1)。"
    },
    8757: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "雪原上方原本澄澈深邃的纯净蔚蓝天空在LCAD生成图中大面积严重欠饱和脱色，退化为灰暗土灰阴霾天(Rsat=0.64)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "雪地摩托车与滑雪者衣着背阴处微显偏暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：雪原上方纯净蔚蓝晴空大面积严重欠饱和脱色为灰暗阴霾天(Rsat=0.64)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8763: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "道路施工区域原本鲜亮醒目的亮橙黄色安全隔离路障在LCAD生成图中严重脱色褪淡发灰(RedLoss=0.16, Rsat=0.53)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "街头飞驰机车尾灯与建筑外立面略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：道路施工区域亮橙黄安全隔离路障严重脱色发暗发灰(RedLoss=0.16)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8777: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "滑板公园左侧围观青年身上原本鲜艳夺目的大红色短袖T恤在LCAD生成图中严重脱色褪淡，退化为暗沉深黑灰色(RedLoss=0.20)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "强逆光阳光光晕外缘略带暗紫杂色"}
        ],
        "review_note": "Double Check复核改判：核查发现：滑板公园左侧围观青年原本鲜艳大红短袖严重脱色退化为发灰暗色(RedLoss=0.20)，清洗伪满分，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8786: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "棒球场内场原本温润饱满的红褐色红土跑道在LCAD生成图中大面积欠饱和脱色发暗，退化为冷灰暗褐色(Rsat=0.63)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "击球手身后平整草坪边缘略微泛冷紫偏色"}
        ],
        "review_note": "Double Check复核改判：核查发现：棒球场内场红褐色红土跑道大面积欠饱和脱色发暗，草地泛冷紫(Rsat=0.63)，改判欠饱和(E2-L2)与偏色(D-L1)。"
    },
    8791: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "展厅卫生间地面上原本醒目排列的红黑相间几何地砖中红砖部分在LCAD生成图中严重脱色发乌，完全退化为深黑死灰色(RedLoss=0.18)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "绿色盆栽绿叶与白色坐便器瓷砖反光略显暗淡"}
        ],
        "review_note": "Double Check复核改判：核查发现：展厅地砖原本红黑相间之鲜艳红砖部分严重脱色退化为死黑灰(RedLoss=0.18)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8796: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "蛋糕表面由多彩糖粒拼成的字母E图案中原本五彩缤纷的红、黄、绿多色彩粒在LCAD生成图中大面积严重脱色失真，退化为单调发暗蓝青色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "蛋糕底部白色奶油裱花与托盘略显泛暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：蛋糕表面字母E彩糖装饰中原本五彩红黄绿彩色糖粒严重脱色失真为单调青蓝色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8798: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "海滨天际原本纯净澄澈的青蓝渐变天空在LCAD生成图中局部大面积泛出突兀脏乱的暖黄橙褐色云层偏色(RedLoss=0.17)，破坏纯净天幕"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "岸边停靠车辆与护栏暗部略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：海滨天际原本纯净青蓝天空大面积泛出脏乱暖黄橙褐偏色(RedLoss=0.17)，改判偏色(D-L2)与错色(C-L1)。"
    },
    8821: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街角原本醒目亮丽的八角形大红色STOP停步标识在LCAD生成图中严重脱色发暗，退化为黯淡棕褐发脏红色(RedLoss=0.14)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "行人蓝色衬衫与背后红砖建筑立面略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：街角大红STOP停步标识严重脱色发暗退化为黯淡棕褐色(RedLoss=0.14)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8832: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "路沿水鸟身后背景停靠的客运巴士原本鲜艳大红色的车身外立面在LCAD生成图中严重脱色褪淡，退化为沉闷泥褐红色(RedLoss=0.19)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "水泥路面与绿化带灌机边缘略显偏灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：背景客运巴士原本鲜艳大红色车身严重脱色褪淡为泥褐红色(RedLoss=0.19)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8836: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "铁丝网后方原本醒目明亮的黄色棒球球棒与悬挂球衣原本纯正明艳的亮蓝色内衬在LCAD生成图中严重脱色发灰(Rsat=0.59)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "白色条纹棒球服面料与手套皮革略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：铁丝网后黄色球棒与球衣亮蓝内衬严重脱色发灰(Rsat=0.59)，清洗伪满分，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8847: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "城市公交客车车身侧面贯穿的原本鲜艳大红色装饰条纹在LCAD生成图中完全脱色黑化，退化为发脏黑灰色装饰带"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "车流前方白色小轿车与路面标线略显暗淡"}
        ],
        "review_note": "Double Check复核改判：核查发现：城市公交侧面原本鲜艳大红色装饰条纹完全脱色退化为发脏黑灰，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8857: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街头金属立柱上原本鲜艳醒目的大红色STOP停步标牌在LCAD生成图中严重脱色发暗，退化为泥土红褐色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "行人伸出的手臂肤色阴影处略显暗沉"}
        ],
        "review_note": "Double Check复核改判：核查发现：街头大红色STOP停步标牌严重脱色发暗退化为泥土红褐色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8860: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "客厅左侧原本端庄典雅的墨绿色布艺单人扶手椅在LCAD生成图中被恶性错涂为浓重暖巧克力红褐色伪色，高贵墨绿色相彻底被篡改"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "客厅壁炉暗部与木质地板边缘略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：客厅左侧端庄墨绿色布艺扶手椅被恶性错涂为浓重巧克力红褐色伪色，改判错色(C-L2)与偏色(D-L1)。"
    },
    8864: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "铁轨上行驶的内燃机车车头及后方客车车厢原本鲜艳醒目的大红色警示横条纹在LCAD生成图中严重脱色褪淡，退化为发灰无色线条(RedLoss=0.23)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "碎石道床与列车深蓝色车顶略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：内燃机车车头与车厢鲜艳大红警示条纹严重脱色褪淡为无色发灰(RedLoss=0.23)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8879: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "滑板小女孩身上原本明艳亮丽的嫩黄色短袖T恤与粉色安全头盔在LCAD生成图中大面积脱色泛白，退化为惨白无色服饰"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "地面平整水泥板接缝与滑板轮略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：滑板小女孩身上嫩黄色短袖与粉色安全帽脱色泛白退化为惨白，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8894: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "路口交通信号灯原本耀眼醒目的大红指示灯与后方行道树原本鲜红的秋季红叶在LCAD生成图中严重脱色发暗，红光与红叶蜕变为深暗灰绿色(RedLoss=0.21)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "斑马线上骑自行车市民衣着略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：交通信号灯大红指示灯与行道树鲜红秋叶严重脱色蜕变为深暗灰绿(RedLoss=0.21)，清洗伪满分，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8900: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "窗外原本生机青翠郁郁葱葱的树冠枝叶在LCAD生成图中大面积欠饱和失色，退化为死气沉沉的暗灰绿色(Rsat=0.45)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "笔记本电脑屏幕上显示图像色彩略显暗淡"}
        ],
        "review_note": "Double Check复核改判：核查发现：窗外生机青翠树冠枝叶大面积欠饱和失色为死气暗灰绿(Rsat=0.45)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8909: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "网球场内原本鲜亮纯正的红土砖红地面在LCAD生成图中大面积严重脱色发灰，退化为黯淡灰紫色硬地"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "击球球员白色遮阳帽与防风护网略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：网球场鲜亮纯正的砖红红土地面大面积严重脱色发灰为黯淡灰紫硬地，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8920: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "历史红砖钟楼建筑周围原本生机勃勃的苍翠绿化树林在LCAD生成图中大面积严重欠饱和脱色，蜕变为发干枯黄灰褐色树木(Rsat=0.67)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "钟楼红砖外墙阴影处略显偏冷泛青"}
        ],
        "review_note": "Double Check复核改判：核查发现：历史红砖钟楼周围苍翠绿化树林大面积脱色为发干枯黄灰褐(Rsat=0.67)，改判欠饱和(E2-L2)与偏色(D-L1)。"
    },
    8922: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "草坪玩耍青年中女士原本鲜艳明朗的明黄色条纹背心与男士身上的酒红色短袖T恤在LCAD生成图中严重脱色发暗，退化为泛冷蓝灰与深暗褐色(RedLoss=0.19)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "背景砖石围墙与开阔草坪边缘略显偏暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：草坪青年明黄条纹背心与男士酒红T恤严重脱色发暗(RedLoss=0.19)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8933: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "碧绿水湾游船上乘员身上原本醒目明亮的大红色冲锋衣与救生装备在LCAD生成图中完全脱色发乌，退化为深暗黑灰色(RedLoss=0.29)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "岸边生机灌木与清澈湖水波光边缘略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：游船乘员身上鲜艳大红冲锋衣与救生装备完全脱色发乌为深暗黑灰(RedLoss=0.29)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8936: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "网球场原本明亮鲜艳的砖红红土球场地面在LCAD生成图中大面积严重脱色褪淡，退化为发白灰土褐色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "球员手中网球拍鲜黄色网线略显暗淡"}
        ],
        "review_note": "Double Check复核改判：核查发现：网球场明亮鲜艳的砖红红土球场地面大面积脱色褪淡为发白灰土褐，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8941: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "客厅壁炉旁原本温润的原木色双门陈列展示立柜在LCAD生成图中被恶性错涂为冰冷浅蓝灰色油漆柜，原木天然纹理与温暖色相彻底失真"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "壁炉两侧原本鲜艳夺目的红地毯局部略显欠饱和脱色"}
        ],
        "review_note": "Double Check复核改判：核查发现：壁炉旁温润原木陈列立柜被恶性错涂为冰冷浅蓝灰油漆柜，红地毯微脱色，清洗伪满分，改判错色(C-L2)与欠饱和(E2-L1)。"
    },
    8970: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "公交客车侧身原本深黑灰色金属车体面板在LCAD生成图中被大面积突兀错涂为刺眼的大红色伪色面板，金属机体色相发生恶性篡改"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "站台等车女士米色大衣与粉色围巾暗部略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：公交客车侧身深黑灰金属面板被大面积突兀错涂为大红色伪色面板，改判错色(C-L2)与偏色(D-L1)。"
    },
    8977: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "运河岸边停靠的三轮货运自行车原本明艳鲜亮的亮黄色金属车架在LCAD生成图中完全脱色黑化，蜕变为沉闷发暗的深黑灰色车架"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "货车红色木箱与绿色箱盖边缘微显泛暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：三轮货运自行车明艳亮黄金属车架完全脱色黑化为深黑灰车架，清洗伪满分，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8980: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "原野围栏前儿童原本鲜艳夺目的深紫色印花短袖在LCAD生成图中严重脱色退化为发脏深黑灰，身旁幼儿原本鲜亮清爽的嫩绿色短袖完全褪色蜕变为浅灰白色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "围栏后方高地牛棕黄色毛皮边缘微显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：儿童鲜艳深紫短袖脱色为深黑灰，身旁幼儿鲜亮嫩绿短袖褪色蜕变浅灰白，清洗伪满分，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8999: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "混凝土墙面上方立杆指示牌内原本鲜艳明亮的蓝色底板与大红亮黄色电脑图形标识在LCAD生成图中完全脱色黑白化，退化为深黑死灰色(RedLoss=0.16, Rsat=0.51)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "停靠的黑色小汽车反光与车顶行李架略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：立杆指示牌内鲜艳蓝色底板与大红亮黄电脑图形标识完全脱色黑白化(RedLoss=0.16)，改判欠饱和(E2-L2)与错色(C-L1)。"
    }
}

def update_export_file(file_path: Path, is_clean: bool = False):
    if not file_path.exists():
        print(f"File not found: {file_path}")
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
    stream_path = STREAMS_DIR / "tasks_lcad_8501_9000_stream.json"
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
    print("Applying Double Check updates for 8501-9000...")
    
    # 1. Update batch 8501-9000
    b_path = EXPORTS_DIR / "reviewed_8501_9000_20260930_190928.json"
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

    print("Double check updates for 8501-9000 completed successfully!")

if __name__ == "__main__":
    main()
