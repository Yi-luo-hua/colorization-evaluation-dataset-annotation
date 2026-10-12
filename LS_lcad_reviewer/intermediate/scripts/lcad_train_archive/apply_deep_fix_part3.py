#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_deep_fix_part3.py
精准应用 Part 3 (Batch 5, Task ID 2001-2500, 81 个高危样本) 的视觉大图直审改判结果：
- 严格遵循 AGENTS.md 规范与基准 schema
- 消灭抽象代词，严格实体定物
- 更新 reviewed_1_10000_all.json
- 更新 reviewed_1_10000_clean.json
"""

import json
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
ALL_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_all.json"
CLEAN_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_clean.json"

# Part 3 (81 例) 视觉大图核验改判映射
PART3_REVIEWS = {
    # Sheet 01
    2007: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "餐厅背景窗户与红色窗帘恶性错涂暗蓝紫伪色，室内光影严重失真。"}],
        "note": "核查发现：餐厅背景窗户与红色窗帘恶性错涂暗蓝紫伪色(C-L2)。"
    },
    2008: {
        "defects": [{"id": "C", "name": "错色", "severity": "L1", "description": "公园开阔草坪生机翠绿轻度衰减，空中风筝色彩饱和度略降。"}],
        "note": "核查发现：公园开阔草坪生机翠绿轻度衰减，空中风筝色彩饱和度略降(C-L1)。"
    },
    2016: {
        "defects": [],
        "note": "模型对停机坪白色轻型客机、沥青跑道及远方地平线上色逼真协调，结构边缘无溢色，物理自洽放行。"
    },
    2017: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "卫生间米白色挂壁电话机恶性错涂为浅天蓝色伪色，塑料本体色彩倒错。"}],
        "note": "核查发现：卫生间米白色挂壁电话机恶性错涂为浅天蓝色伪色(C-L2)。"
    },
    2020: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "青年男子纯白礼服大面积泛冷蓝灰伪色，衣物面料原有白洁质感明显受损。"}],
        "note": "核查发现：青年男子纯白礼服大面积泛冷蓝灰伪色(C-L2)。"
    },
    2029: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "甜品盘边缘与瓷勺大面积溢出刺目蓝紫伪色，烤布丁焦糖暖色调衰减。"}],
        "note": "核查发现：甜品盘边缘与瓷勺大面积溢出刺目蓝紫伪色(C-L2)。"
    },

    # Sheet 02
    2032: {
        "defects": [{"id": "C", "name": "错色", "severity": "L1", "description": "台阶右侧绿化树木生机翠绿轻度衰减偏暗。"}],
        "note": "核查发现：台阶右侧绿化树木生机翠绿轻度衰减偏暗(C-L1)。"
    },
    2039: {
        "defects": [],
        "note": "模型对室内演讲学者西装、面部光影及背景投影幻灯片文字上色精准自然，无溢色杂色，物理自洽放行。"
    },
    2042: {
        "defects": [{"id": "C", "name": "错色", "severity": "L1", "description": "卫生间窗帘砖红色调轻度衰减偏暗褐。"}],
        "note": "核查发现：卫生间窗帘砖红色调轻度衰减偏暗褐(C-L1)。"
    },
    2043: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "厨房窗户与木质橱柜表面恶性错涂刺目洋红紫与青蓝伪色，室内光影严重失调。"}],
        "note": "核查发现：厨房窗户与木质橱柜表面恶性错涂刺目洋红紫与青蓝伪色(C-L2)。"
    },
    2047: {
        "defects": [],
        "note": "模型对庄园长条形白色楼房、草坪吃草耕牛及明亮天空上色准确真实，透视光影自然，物理自洽放行。"
    },
    2048: {
        "defects": [{"id": "C", "name": "错色", "severity": "L1", "description": "停机坪天空与云层轻微泛暖暗红微偏色。"}],
        "note": "核查发现：停机坪天空与云层轻微泛暖暗红微偏色(C-L1)。"
    },

    # Sheet 03
    2049: {
        "defects": [],
        "note": "模型对街口交通信号红灯、掉头指示牌与背景绿化树木上色精准逼真，物理指标自洽放行。"
    },
    2057: {
        "defects": [],
        "note": "模型对小球员金黄色运动上衣、面部自然肤色及球棒质感上色鲜活准确，物理自洽放行。"
    },
    2059: {
        "defects": [],
        "note": "模型对卫生间白色瓷砖墙面、洁具及金属置物架上色干净逼真，物理指标自洽放行。"
    },
    2075: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "办公卡座深红隔断严重脱色暗化蜕变为灰褐色，赛车车身局部偏暗。"}],
        "note": "核查发现：办公卡座深红隔断严重脱色暗化蜕变为灰褐色(C-L2)。"
    },
    2086: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "厨房白色烤箱门与台面橱柜恶性错涂大面积刺目蓝紫伪色，室内色调严重失真。"}],
        "note": "核查发现：厨房白色烤箱门与台面橱柜恶性错涂大面积刺目蓝紫伪色(C-L2)。"
    },
    2104: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "餐桌鲜艳大红饮料杯与调料瓶严重脱色暗化，炸薯条金黄色泽衰减。"}],
        "note": "核查发现：餐桌鲜艳大红饮料杯与调料瓶严重脱色暗化(C-L2)。"
    },

    # Sheet 04
    2110: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "铁轨中间停靠的机车标志性宝蓝车体严重脱色蜕变为暗冷铁灰，车身色彩彻底丧失。"}],
        "note": "核查发现：中间机车标志性宝蓝车体严重脱色蜕变为暗冷铁灰(C-L2)。"
    },
    2111: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "路口地勤作业人员荧光橙红反光背心严重脱色发白，背景行道树色泽略暗。"}],
        "note": "核查发现：地勤作业人员荧光橙红反光背心严重脱色发白(C-L2)。"
    },
    2114: {
        "defects": [],
        "note": "模型对日式餐厅木质吧台、吊顶原木横梁及操作区光影上色逼真协调，氛围温馨，物理自洽放行。"
    },
    2116: {
        "defects": [],
        "note": "模型对托盘中巧克力甜甜圈釉面光泽、彩色糖针点缀及背景光影上色逼真协调，物理指标自洽放行。"
    },
    2119: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "背景街市集市大红遮阳伞与商户彩色衣物严重脱色发灰发暗。"}],
        "note": "核查发现：背景集市大红遮阳伞与商户彩色衣物严重脱色发灰发暗(C-L2)。"
    },
    2121: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "网球运动员亮橙红运动背心严重脱色错涂为发暗灰紫伪色，球场地表微弱暗化。"}],
        "note": "核查发现：网球选手亮橙红运动背心严重脱色错涂为发暗灰紫伪色(C-L2)。"
    },

    # Sheet 05
    2136: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "棒球看台观众席彩色服饰与内场红土地面严重脱色暗化泛灰。"}],
        "note": "核查发现：棒球看台观众席彩色服饰与内场红土地面严重脱色暗化泛灰(C-L2)。"
    },
    2139: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "沙滩浅水处游客手持鲜亮橙红浮板严重脱色蜕变为暗灰白色。"}],
        "note": "核查发现：沙滩游客手持鲜亮橙红浮板严重脱色蜕变为暗灰白色(C-L2)。"
    },
    2140: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "轿车车体与车窗玻璃大面积恶性错涂刺目冷青蓝与紫红伪色，反光失真。"}],
        "note": "核查发现：轿车车体与车窗玻璃大面积恶性错涂刺目冷青蓝与紫红伪色(C-L2)。"
    },
    2142: {
        "defects": [],
        "note": "模型对金属围栏后方大象身躯毛色、自然光照及围观游人上色逼真协调，物理指标自洽放行。"
    },
    2143: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "男童手中原本明黄色的塑料飞盘恶性错涂为浅天蓝色伪色。"}],
        "note": "核查发现：男童手中原本明黄色的塑料飞盘恶性错涂为浅天蓝色伪色(C-L2)。"
    },
    2150: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "背景温馨暖米黄色墙面恶性错涂为冰冷死灰色伪色，室内温馨感破坏。"}],
        "note": "核查发现：背景温馨暖米黄色墙面恶性错涂为冰冷死灰色伪色(C-L2)。"
    },

    # Sheet 06
    2154: {
        "defects": [],
        "note": "模型对草坪扑捡飞盘青年、翠绿草地及背景红砖拱门上色逼真协调，结构清晰，物理自洽放行。"
    },
    2158: {
        "defects": [],
        "note": "模型对复古墨绿色瓷砖墙面与白色洗手盆台面上色沉稳准确，光影自然，物理自洽放行。"
    },
    2164: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "快递货车经典双色Logo中醒目的橙色“Ex”严重脱色蜕变为灰黑暗字，品牌标识色彩受损。"}],
        "note": "核查发现：货车Logo中醒目的橙色“Ex”严重脱色蜕变为灰黑暗字(C-L2)。"
    },
    2180: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "街景街面严重错涂刺目洋红紫伪色，机车队员制服背后金色刺绣脱色暗化。"}],
        "note": "核查发现：街景街面严重错涂刺目洋红紫伪色，背后金色刺绣脱色暗化(C-L2)。"
    },
    2188: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "街头背景停靠的厢式小汽车车身大面积恶性错涂为刺眼荧光青绿伪色。"}],
        "note": "核查发现：背景停靠的厢式小汽车车身大面积恶性错涂为刺眼荧光青绿伪色(C-L2)。"
    },
    2189: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "轻型飞机经典鲜艳酒红机腹与条纹涂装被彻底剥夺，恶性错涂为暗灰黄褐伪色。"}],
        "note": "核查发现：轻型飞机经典鲜艳酒红机腹与条纹恶性错涂为暗灰黄褐伪色(C-L2)。"
    },

    # Sheet 07
    2194: {
        "defects": [],
        "note": "模型对办公桌面木纹质感、外设键盘鼠标及咖啡杯上色逼真协调，光影质感自然，物理指标自洽放行。"
    },
    2197: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "左侧儿童手中明黄色塑料飞盘严重脱色蜕变为灰白色，儿童服饰略偏暗。"}],
        "note": "核查发现：左侧儿童手中明黄飞盘严重脱色蜕变为灰白色(C-L2)。"
    },
    2207: {
        "defects": [],
        "note": "模型对广场停放的重型摩托车队金属镀铬、背景松树及沥青地面上色精准逼真，物理指标自洽放行。"
    },
    2221: {
        "defects": [{"id": "C", "name": "错色", "severity": "L1", "description": "客厅飘窗木质百叶窗与茶几暗部饱和度轻度衰减偏暗。"}],
        "note": "核查发现：客厅飘窗木质百叶窗与茶几暗部饱和度轻度衰减偏暗(C-L1)。"
    },
    2225: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "极限滑板底部标志性鲜艳大红底板涂装严重脱色褪白为暗粉灰。"}],
        "note": "核查发现：滑板底部标志性鲜艳大红底板涂装严重脱色褪白为暗粉灰(C-L2)。"
    },
    2235: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "海滩女子身穿的鲜亮荧光粉红比基尼内衬严重脱色衰减为暗灰色。"}],
        "note": "核查发现：海滩女子鲜亮荧光粉红比基尼内衬严重脱色衰减为暗灰色(C-L2)。"
    },

    # Sheet 08
    2236: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "客厅红色布艺沙发与落地窗框大面积错涂暗紫红伪色，环境光温严重偏色。"}],
        "note": "核查发现：客厅红色布艺沙发与窗框大面积错涂暗紫红伪色(C-L2)。"
    },
    2240: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "卧室内小狗所卧金黄色床单严重脱色蜕变为暗土灰色，温暖质感彻底丧失。"}],
        "note": "核查发现：卧室内小狗所卧金黄色床单严重脱色蜕变为暗土灰色(C-L2)。"
    },
    2242: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "地面鲜艳翠绿波纹地毯严重脱色暗化，木桌上天蓝外壳笔记本偏紫。"}],
        "note": "核查发现：地面鲜艳翠绿波纹地毯严重脱色暗化，笔记本天蓝外壳偏紫(C-L2)。"
    },
    2248: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "激浪中冲浪者脚下鲜艳明黄冲浪板严重脱色蜕变为暗灰黄绿色。"}],
        "note": "核查发现：激浪中冲浪者脚下鲜艳明黄冲浪板严重脱色蜕变为暗灰黄绿色(C-L2)。"
    },
    2250: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "室内男子纯白T恤被严重污染泛冷蓝灰伪色，背景墙面微偏冷。"}],
        "note": "核查发现：室内男子纯白T恤被严重污染泛冷蓝灰伪色(C-L2)。"
    },
    2254: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "母亲所穿天蓝色短袖上衣严重脱色暗化退化为黑灰色，婴儿肤色轻度偏色。"}],
        "note": "核查发现：母亲所穿天蓝色短袖上衣严重脱色暗化退化为黑灰色(C-L2)。"
    },

    # Sheet 09
    2255: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "不锈钢烤箱门与玻璃大面积恶性错涂刺目青蓝伪色，内部烤鸡焦糖色泽衰减。"}],
        "note": "核查发现：不锈钢烤箱门与玻璃大面积恶性错涂刺目青蓝伪色(C-L2)。"
    },
    2257: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "洗手台大面积木质镜框边缘恶性错涂为刺眼深宝蓝伪色。"}],
        "note": "核查发现：洗手台木质镜框边缘恶性错涂为刺眼深宝蓝伪色(C-L2)。"
    },
    2261: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "公共卫生间整排红木隔板门恶性错涂为暗青蓝紫伪色，木材质感严重受损。"}],
        "note": "核查发现：公共卫生间整排红木隔板门恶性错涂为暗青蓝紫伪色(C-L2)。"
    },
    2264: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "滑板公园天空与背景绿树严重偏色泛紫发暗，左侧道具脱色。"}],
        "note": "核查发现：滑板公园天空与背景绿树严重偏色泛紫发暗(C-L2)。"
    },
    2267: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "悬挂处理的整串青香蕉被恶性错涂为刺眼荧光浓绿伪色，厂房流水线大面积泛紫。"}],
        "note": "核查发现：悬挂整串青香蕉被恶性错涂为刺眼荧光浓绿伪色(C-L2)。"
    },
    2277: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "街头妇女所穿鲜艳明黄与大红传统纱丽严重脱色暗化泛灰。"}],
        "note": "核查发现：街头妇女所穿鲜艳明黄与大红纱丽严重脱色暗化泛灰(C-L2)。"
    },

    # Sheet 10
    2282: {
        "defects": [],
        "note": "模型对街头滑板少年深蓝短袖、滑板轮廓及街道阴影上色真实协调，物理指标自洽放行。"
    },
    2291: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "重型内燃机车车头醒目明黄导向条纹严重脱色发暗，铁轨两侧草地枯萎泛冷灰。"}],
        "note": "核查发现：机车车头醒目明黄导向条纹严重脱色发暗，两侧草地枯萎泛灰(C-L2)。"
    },
    2298: {
        "defects": [],
        "note": "模型对卫浴空间白色瓷砖、洗手台盆及印花浴帘上色干净自然，微弱色差属合理室内采光，物理自洽放行。"
    },
    2312: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "复古卧室窗台采光与左侧墙面恶性错涂为阴冷荧光青绿伪色，室内暖调失衡。"}],
        "note": "核查发现：复古卧室窗台采光与左侧墙面恶性错涂为阴冷荧光青绿伪色(C-L2)。"
    },
    2323: {
        "defects": [],
        "note": "模型对窗边厨房白色橱柜、不锈钢水槽及窗外红砖建筑上色逼真协调，采光明暗自然，物理自洽放行。"
    },
    2338: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "近景渔船天蓝色船体甲板大面积恶性错涂为刺眼洋红紫伪色，海湾船群色彩错乱。"}],
        "note": "核查发现：近景渔船天蓝色船体甲板大面积恶性错涂为刺眼洋红紫伪色(C-L2)。"
    },

    # Sheet 11
    2350: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "城际通勤列车标志性大红车身涂装严重脱色发暗，桥下涂鸦艺术字色彩衰减。"}],
        "note": "核查发现：列车标志性大红车身涂装严重脱色发暗，桥下涂鸦色彩衰减(C-L2)。"
    },
    2358: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "夜景观景钟楼发光表盘恶性错涂为刺眼荧光青绿伪色，钟塔四周严重泛紫偏色。"}],
        "note": "核查发现：夜景钟楼发光表盘恶性错涂为刺眼荧光青绿伪色(C-L2)。"
    },
    2367: {
        "defects": [],
        "note": "模型对卫浴空间米黄墙砖、淋浴隔断玻璃及白色洁具上色干净自然，明暗光影协调，物理指标自洽放行。"
    },
    2368: {
        "defects": [],
        "note": "模型对海滩低空展翅海鸥羽色、远处海浪及沙滩漫步游人上色生动自然，物理指标自洽放行。"
    },
    2380: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "美发师手部皮肤大面积恶性错涂为阴冷深青蓝伪色，顾客粉红金属发夹脱色。"}],
        "note": "核查发现：美发师手部皮肤大面积恶性错涂为阴冷深青蓝伪色(C-L2)。"
    },
    2387: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "户外餐桌透明啤酒杯壁恶性错涂刺眼深宝蓝伪色，巧克力蛋糕与甜点色泽衰减。"}],
        "note": "核查发现：透明啤酒杯壁恶性错涂刺眼深宝蓝伪色(C-L2)。"
    },

    # Sheet 12
    2407: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "木屋餐厅天花板木梁与墙面严重错涂刺目青蓝紫伪色，室内色温严重紊乱。"}],
        "note": "核查发现：木屋餐厅天花板木梁与墙面严重错涂刺目青蓝紫伪色(C-L2)。"
    },
    2414: {
        "defects": [],
        "note": "模型对野生动物园稀树草坡、长颈鹿身躯斑纹及自然光影上色逼真生动，物理指标自洽放行。"
    },
    2417: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "男童幼嫩面部与手臂肤色严重泛阴冷青灰偏色，女孩手中粉红纸牌脱色。"}],
        "note": "核查发现：男童面部与手臂肤色严重泛阴冷青灰偏色，女孩粉红纸牌脱色(C-L2)。"
    },
    2428: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "卫生间实木墙面原本深红木色被彻底剥夺，恶性错涂为阴森深墨绿青黑伪色。"}],
        "note": "核查发现：卫生间深红实木墙面被恶性错涂为阴森深墨绿青黑伪色(C-L2)。"
    },
    2430: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "巡逻骑警标志性荧光亮黄安全外套恶性错涂为刺眼青绿伪色。"}],
        "note": "核查发现：巡逻骑警标志性荧光亮黄外套恶性错涂为刺眼青绿伪色(C-L2)。"
    },
    2433: {
        "defects": [{"id": "C", "name": "错色", "severity": "L1", "description": "卫生间洗手台台面暗部木质红褐色调轻度衰减偏暗。"}],
        "note": "核查发现：洗手台台面暗部木质红褐色调轻度衰减偏暗(C-L1)。"
    },

    # Sheet 13
    2448: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "卫生间米黄地面瓷砖与墙面恶性错涂为阴冷死灰青蓝伪色，环境暖意丧失。"}],
        "note": "核查发现：卫生间米黄瓷砖与墙面恶性错涂为阴冷死灰青蓝伪色(C-L2)。"
    },
    2458: {
        "defects": [],
        "note": "模型对室内滑板碗池水泥质感、高台滑板少年及暗部光影上色自然协调，物理自洽放行。"
    },
    2470: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "白色Wii遥控器半透明硅胶保护套大面积恶性错涂为刺眼粉紫伪色。"}],
        "note": "核查发现：白色Wii遥控器半透明硅胶保护套大面积恶性错涂为刺眼粉紫伪色(C-L2)。"
    },
    2475: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "烘烤披萨表面新鲜番茄酱与金黄奶酪严重脱色暗化为暗紫灰，熟成感丧失。"}],
        "note": "核查发现：披萨表面新鲜番茄酱与金黄奶酪严重脱色暗化为暗紫灰(C-L2)。"
    },
    2482: {
        "defects": [{"id": "C", "name": "错色", "severity": "L1", "description": "酒店客房天花板边缘与窗帘暗部轻微泛冷青蓝微偏色。"}],
        "note": "核查发现：酒店客房天花板边缘与窗帘暗部轻微泛冷青蓝微偏色(C-L1)。"
    },
    2485: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "卫生间盆栽生机翠绿观叶植物叶片大面积恶性错涂为暗枯紫褐伪色。"}],
        "note": "核查发现：盆栽生机翠绿观叶植物大面积恶性错涂为暗枯紫褐伪色(C-L2)。"
    },

    # Sheet 14
    2489: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "自行车车筐内原本极其鲜艳的大红包装袋被恶性错涂为发暗深棕褐色伪色。"}],
        "note": "核查发现：自行车车筐内原本鲜艳的大红包装袋恶性错涂为发暗深棕褐色伪色(C-L2)。"
    },
    2494: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "台阶席地年轻女子鲜艳大红针织衫严重脱色错涂为发暗枯黄土褐色伪色，青年浅蓝T恤脱色蜕白。"}],
        "note": "核查发现：台阶席地年轻女子大红针织衫严重脱色错涂为发暗枯黄土褐色伪色(C-L2)。"
    },
    2499: {
        "defects": [{"id": "C", "name": "错色", "severity": "L2", "description": "高速公路原本标志性纯深蓝底色的机场指路标牌大面积恶性错涂为刺眼洋红暗褐色伪色。"}],
        "note": "核查发现：机场指路标牌标志性深蓝底色大面积恶性错涂为刺眼洋红暗褐色伪色(C-L2)。"
    }
}

def main():
    print(f"Total Part 3 fixes defined: {len(PART3_REVIEWS)}")
    assert len(PART3_REVIEWS) == 81, f"Expected 81 fixes, got {len(PART3_REVIEWS)}"

    with open(ALL_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    anns_all = all_data["annotations"]
    anns_clean = clean_data["annotations"]

    updated_count = 0
    for ann_a, ann_c in zip(anns_all, anns_clean):
        tid = ann_a["human_review"]["task_id"]
        if tid in PART3_REVIEWS:
            rev = PART3_REVIEWS[tid]
            has_defect_a = any(d.get("id") == "A" for d in rev["defects"])

            # 更新 all_data
            ann_a["defects"] = rev["defects"]
            ann_a["review_note"] = rev["note"]
            ann_a["reviewed_score"] = 1.0 if has_defect_a else None
            ann_a["needs_rescoring"] = not has_defect_a
            ann_a["review_status"] = "已核验"

            # 更新 clean_data (review_note 严格保持 "")
            ann_c["defects"] = rev["defects"]
            ann_c["review_note"] = ""
            ann_c["reviewed_score"] = 1.0 if has_defect_a else None
            ann_c["needs_rescoring"] = not has_defect_a
            ann_c["review_status"] = "已核验"

            updated_count += 1

    print(f"Updated {updated_count} Part 3 high-risk items in memory.")
    assert updated_count == 81, f"Expected 81 updated items, got {updated_count}"

    with open(ALL_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved: {ALL_FILE.name}")

    with open(CLEAN_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved: {CLEAN_FILE.name}")

    print("\n[SUCCESS] Part 3 deep fix successfully applied to all exports!")

if __name__ == "__main__":
    main()
