#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_cv_audit_round2.py
Round 2 (Sheet 01 - Sheet 20, 共 120 组高危任务) 全量像素级直审定物改判落地脚本：
- 严格遵循 AGENTS.md 规范与权威基准 schema
- 消灭抽象代词，严格实体具象定物
- 更新 reviewed_1_10000_all.json
- 更新 reviewed_1_10000_clean.json
"""

import json
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
ALL_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_all.json"
CLEAN_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_clean.json"

ROUND2_FIXES = {
    # ================= Sheet 01 (Tasks 121 - 126) =================
    1325: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "洗手台红木浴室柜深红褐木质光泽脱色发暗，瓷砖反光略有衰减。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "浴室柜木质色调偏暗偏冷。"}
        ],
        "note": "核查发现：洗手台红木浴室柜深红褐光泽脱色发暗(E2-L2, D-L1)。"
    },
    1349: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "非洲原野金黄色草甸大面积脱色错涂为暗灰泥色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "大象身后树木生机绿意完全脱色衰退。"}
        ],
        "note": "核查发现：金黄草甸大面积脱色错涂为暗灰泥色(C-L2, E2-L2)。"
    },
    1370: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "沿街商铺大红色门框与红木门完全脱色退化为发暗黑灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "外墙暖黄漆面大面积脱色衰减。"}
        ],
        "note": "核查发现：商铺大红门框完全脱色退化为发暗黑灰色(C-L2, E2-L2)。"
    },
    1383: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "卧室粉紫暖色背景墙恶性错涂为阴冷灰绿青色调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "原木床架与被褥暖调完全脱色。"}
        ],
        "note": "核查发现：卧室粉紫暖色背景墙错涂为阴冷灰绿青色调(C-L2, E2-L2)。"
    },
    1391: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "看台平展翠绿草坪背景严重脱色衰减为发暗枯草黄褐。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "背景看台色泽偏暗发干。"}
        ],
        "note": "核查发现：看台平展翠绿草坪脱色衰减为发暗枯草黄褐(E2-L2, C-L1)。"
    },
    1396: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "步道女子鲜艳大红色短袖被彻底恶性错涂为深蓝灰色外套，中央翠绿草坪完全脱色退化为冷灰泥地。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "大红消火栓局部脱色衰减。"}
        ],
        "note": "核查发现：女子大红短袖错涂深蓝灰且草坪退化冷灰泥地(C-L3, E2-L2)。"
    },

    # ================= Sheet 02 (Tasks 127 - 132) =================
    1397: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "沙滩上大红宣传横幅与红色游艇吃水线彻底脱色蜕变黑灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "金黄色沙滩与蔚蓝晴空大面积脱色衰减。"}
        ],
        "note": "核查发现：大红横幅与游艇红线彻底脱色蜕变黑灰色(C-L2, E2-L2)。"
    },
    1405: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "背景苍翠植被山坡脱色为发暗枯草黄褐色。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "海水与山坡阴影色泽略偏冷灰。"}
        ],
        "note": "核查发现：背景苍翠植被山坡脱色为发暗枯草黄褐色(E2-L2, C-L1)。"
    },
    1435: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "浴帘上大树繁茂生机翠绿树叶严重脱色衰减。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "地面瓷砖微弱泛冷灰偏色。"}
        ],
        "note": "核查发现：浴帘上大树繁茂生机翠绿树叶严重脱色衰减(E2-L2, C-L1)。"
    },
    1441: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "空中风筝冲浪翼鲜艳大红色与黄色拼块彻底脱色退化为黑灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "蔚蓝晴空与沙滩大面积脱色衰减。"}
        ],
        "note": "核查发现：风筝冲浪翼大红与黄色拼块彻底脱色退化为黑灰色(C-L2, E2-L2)。"
    },
    1456: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "客厅窗边鲜艳大红色布艺沙发彻底脱色错涂为发暗灰褐土泥色沙发。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "室内温暖阳光色调剥离退化。"}
        ],
        "note": "核查发现：客厅窗边鲜红布艺沙发彻底脱色错涂为发暗灰褐色(C-L3, E2-L2)。"
    },
    1469: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "电脑桌周边光影微弱偏暗泛青紫冷色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "木质桌面色彩微弱脱色。"}
        ],
        "note": "核查发现：电脑桌周边光影微弱偏暗泛青紫冷色(D-L1, E2-L1)。"
    },

    # ================= Sheet 03 (Tasks 133 - 138) =================
    1477: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "室内网球场砖红土地面被错涂为暗灰绿硬地，球员鲜艳蓝色运动短裤彻底脱色为浅灰白。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "背景深蓝墙体严重脱色变暗。"}
        ],
        "note": "核查发现：网球场砖红地面错涂暗灰绿，球员蓝短裤脱色浅灰白(C-L3, E2-L2)。"
    },
    1488: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "沿街红砖建筑立面大面积严重脱色蜕变为阴冷灰白水泥色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "雪中消火栓红色漆面脱色衰减。"}
        ],
        "note": "核查发现：红砖建筑立面大面积严重脱色蜕变为阴冷灰白水泥色(C-L2, E2-L2)。"
    },
    7: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "海湾日落天际线金黄色晚霞光晕大面积脱色衰减。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "海面暮色略偏冷暗发灰。"}
        ],
        "note": "核查发现：海湾日落天际线金黄色晚霞光晕大面积脱色衰减(E2-L2, C-L1)。"
    },
    17: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "客厅温馨浅粉红色地毯完全脱色蜕变为暗灰白地毯，薄荷绿丝绒沙发褪色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "全屋复古暖彩色调严重衰退。"}
        ],
        "note": "核查发现：浅粉红地毯脱色蜕变暗灰白，薄荷绿沙发褪色(C-L2, E2-L2)。"
    },
    29: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "动物园后方生机翠绿树林大面积脱色衰减为发暗枯草色。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "沙土地面微弱泛冷。"}
        ],
        "note": "核查发现：后方生机翠绿树林大面积脱色衰减为发暗枯草色(E2-L2, C-L1)。"
    },
    112: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "海水碧蓝清澈度与冲浪服细节微弱衰减。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "海面色调轻微泛暗。"}
        ],
        "note": "核查确认：海水碧蓝清澈度与冲浪服细节微弱衰减(E2-L1, D-L1)。"
    },

    # ================= Sheet 04 (Tasks 139 - 144) =================
    121: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "树冠翠绿枝叶与原野金黄枯草大面积脱色衰退。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "树皮与草色略微偏灰暗。"}
        ],
        "note": "核查发现：树冠翠绿枝叶与原野金黄枯草大面积脱色衰退(E2-L2, C-L1)。"
    },
    125: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "左侧滑雪者亮橙黄色滑雪服彻底脱色错涂为发暗灰白素色衣服。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "红色警示旗与橙色头盔脱色衰减。"}
        ],
        "note": "核查发现：左侧滑雪者亮橙黄滑雪服彻底脱色错涂为发暗灰白(C-L2, E2-L2)。"
    },
    135: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "木质桌面边缘暖色木纹微弱脱色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "桌面与键盘略泛冷灰。"}
        ],
        "note": "核查确认：木质桌面边缘暖色木纹微弱脱色泛冷灰(E2-L1, D-L1)。"
    },
    182: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "街道背景橙色与草绿色大型商业广告横幅大面积脱色退化为暗灰黑色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "晴朗蓝天大面积脱色衰减。"}
        ],
        "note": "核查发现：街头橙色与草绿色大型商业横幅彻底脱色蜕变暗黑灰(C-L2, E2-L2)。"
    },
    193: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "钟楼石质外墙色调微弱偏灰偏暗。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "建筑暖色木石微弱脱色。"}
        ],
        "note": "核查确认：钟楼石质外墙色调微弱偏灰偏暗脱色(D-L1, E2-L1)。"
    },
    228: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "卫生间红木雕花窗框与门饰暖红褐色彻底脱色衰退为冷灰黑。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "全屋偏冷发灰。"}
        ],
        "note": "核查发现：卫生间红木雕花窗框暖红褐色彻底脱色衰退为冷灰黑(E2-L2, D-L1)。"
    },

    # ================= Sheet 05 (Tasks 145 - 150) =================
    263: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "河畔节日盛装人群鲜艳洋红、明黄、翠绿、宝蓝等五彩莎丽大面积完全脱色退化为黑白灰死色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "全图彩色信息严重枯竭崩溃。"}
        ],
        "note": "核查发现：人群鲜艳五彩莎丽大面积完全脱色退化为黑白灰死色(C-L3, E2-L3)。"
    },
    276: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "地面鲜橙色文件夹与便签纸彻底脱色退化为发暗灰黑色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "学生红棕色头发与地毯暖色大面积脱色衰减。"}
        ],
        "note": "核查发现：鲜橙色文件夹彻底脱色退化为暗灰黑，红发脱色(C-L2, E2-L2)。"
    },
    301: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "经典红砖建筑立面与薄荷绿遮阳棚招牌脱色衰减为发冷暗灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "红砖微弱偏冷偏暗。"}
        ],
        "note": "核查发现：红砖建筑立面与薄荷绿遮阳棚招牌脱色衰减为发冷暗灰(E2-L2, C-L1)。"
    },
    310: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "花岗岩石柱暖砂色与钟表铜金饰边微弱脱色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "全景微弱偏冷发灰。"}
        ],
        "note": "核查确认：花岗岩石柱暖砂色与钟表铜金饰边微弱脱色(E2-L1, D-L1)。"
    },
    350: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "大型施工脚手架鲜艳宝蓝色防尘防护网完全脱色错涂为暗褐灰色，仪仗队鲜红制服彻底脱色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "摩托车队与地面反光衰退。"}
        ],
        "note": "核查发现：宝蓝脚手架防尘网错涂暗褐灰，仪仗队红制服脱色(C-L3, E2-L2)。"
    },
    432: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "湿地水畔金黄色芦苇丛与茂密秋季树林完全脱色错涂为冰冷暗灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "水面生机暖色倒影严重剥离退化。"}
        ],
        "note": "核查发现：水畔金黄芦苇丛与树林完全脱色错涂为冰冷暗灰色(C-L2, E2-L2)。"
    },

    # ================= Sheet 06 (Tasks 151 - 156) =================
    487: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "湖面泛舟亮红木质独木舟与水中红色倒影彻底脱色错涂为深黑炭灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "晨曦暖光倒影完全剥离退化。"}
        ],
        "note": "核查发现：亮红独木舟与水中红色倒影彻底脱色错涂为深黑炭灰(C-L3, E2-L2)。"
    },
    495: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "小男孩手中鲜艳荧光橙红色飞盘彻底脱色蜕变为苍白灰白塑料盘。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "草坪翠绿生机大幅脱色衰退。"}
        ],
        "note": "核查发现：荧光橙红飞盘彻底脱色蜕变为苍白灰白塑料盘(C-L2, E2-L2)。"
    },
    3004: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "动物园长颈鹿身后苍翠公园树林大面积脱色衰减为枯褐色。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "树冠微带干枯偏色。"}
        ],
        "note": "核查发现：长颈鹿身后苍翠树林大面积脱色衰减为枯褐色(E2-L2, C-L1)。"
    },
    3017: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "繁华街头粉紫色霓虹灯广告牌彻底脱色蜕变为暗灰黑色，行人橙红信号灯脱色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街景彩色灯光衰退。"}
        ],
        "note": "核查发现：粉紫霓虹灯广告牌蜕变暗黑灰，橙红信号灯脱色(C-L2, E2-L2)。"
    },
    3040: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "卫生间白色墙面与洗手台遭受恶性烘烤严重偏脏暖黄土褐调。"}
        ],
        "note": "核查发现：卫生间白色墙面与洗手台遭受恶性烘烤偏脏暖黄土褐(D-L2)。"
    },
    3049: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "海浪白浪花与澄澈碧蓝海水脱色退化为发脏浅灰绿色。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "海水色调微弱泛灰。"}
        ],
        "note": "核查发现：海浪白浪花与澄澈碧蓝海水脱色退化为发脏浅灰绿(E2-L2, C-L1)。"
    },

    # ================= Sheet 07 (Tasks 157 - 162) =================
    3053: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "远景红砖酒店大楼与客机红蓝涂装脱色衰减为发冷暗灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "色调微弱偏冷。"}
        ],
        "note": "核查发现：远景红砖酒店大楼与客机红蓝涂装脱色衰减为发冷暗灰(E2-L2, C-L1)。"
    },
    3118: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "客厅鲜艳深宝蓝色布艺沙发、鲜红几何抱枕与草绿色茶几大面积彻底脱色错涂为发暗灰褐死色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "室内高饱和特色软装完全崩溃。"}
        ],
        "note": "核查发现：深宝蓝沙发与鲜红抱枕彻底脱色错涂为发暗灰褐死色(C-L3, E2-L3)。"
    },
    3168: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "人行道交通红绿灯明亮翠绿通行信号灯被彻底恶性错涂为刺目明黄橙色伪色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "警示牌红色三角形脱色衰减。"}
        ],
        "note": "核查发现：交通红绿灯翠绿通行信号灯彻底恶性错涂为刺目明黄橙色(C-L3, E2-L2)。"
    },
    3180: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "仿古建筑钟楼朱红色飞檐亭顶与琉璃青瓦大面积脱色蜕变发暗灰褐泥色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "古建筑彩画完全脱色衰退。"}
        ],
        "note": "核查发现：钟楼朱红飞檐与琉璃瓦脱色蜕变发暗灰褐泥色(C-L2, E2-L2)。"
    },
    3205: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "旧金山标志性复古明黄色有轨电车大面积脱色蜕变为苍白灰白无色电车。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街景彩色招牌与暖光大面积脱色。"}
        ],
        "note": "核查发现：标志性明黄色有轨电车大面积脱色蜕变为苍白灰白无色(C-L2, E2-L2)。"
    },
    3218: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "红木色实木地板与壁炉石纹微弱脱色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内微弱泛冷偏灰。"}
        ],
        "note": "核查确认：红木色实木地板与壁炉石纹微弱脱色(E2-L1, D-L1)。"
    },

    # ================= Sheet 08 (Tasks 163 - 168) =================
    3225: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "公共卫生间原本暖黄泛青瓷砖墙面与暖光照明被彻底剥离脱色为惨白冰冷灰调。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "全屋暖色瓷砖大面积脱色衰减。"}
        ],
        "note": "核查发现：卫生间暖黄泛青瓷砖被彻底剥离脱色为惨白冰冷灰调(C-L2, E2-L2)。"
    },
    3229: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "观光巴士游客鲜橙色背心与明亮粉红色POLO衫彻底脱色蜕变为苍白灰白无色短袖。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "人群彩衣完全脱色退化。"}
        ],
        "note": "核查发现：游客鲜橙背心与粉红POLO衫彻底脱色蜕变灰白素色(C-L2, E2-L2)。"
    },
    3233: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "客机机尾垂直尾翼经典鲜红色圆形航徽完全脱色衰退为苍白浅灰粉色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "跑道两侧绿化草坪与警示标脱色衰减。"}
        ],
        "note": "核查发现：机尾垂直尾翼经典鲜红航徽完全脱色衰退为苍白浅灰粉(C-L2, E2-L2)。"
    },
    3239: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "棒球场生机鲜艳翠绿外野草坪大面积彻底脱色错涂为发暗枯草土泥色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "广告看板与红土内野脱色衰减。"}
        ],
        "note": "核查发现：棒球场鲜艳翠绿草坪彻底脱色错涂为发暗枯草土泥色(C-L3, E2-L2)。"
    },
    3249: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "机车车头鲜红色“192”编号与车身装饰条纹大面积脱色退化为苍白灰白色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "站台鲜黄色安全警戒线与橙色路锥脱色衰减。"}
        ],
        "note": "核查发现：机车鲜红“192”编号大面积脱色退化为苍白灰白色(C-L2, E2-L2)。"
    },
    3268: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "窗外生机翠绿树林景观与浴缸青翠毛巾大面积脱色衰退为暗灰色。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "木质结构色调泛冷偏灰。"}
        ],
        "note": "核查发现：窗外生机翠绿树林景观与浴缸毛巾大面积脱色衰退(E2-L2, C-L1)。"
    },

    # ================= Sheet 09 (Tasks 169 - 174) =================
    3302: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "室内长廊右侧红褐色木地板彻底脱色错涂为阴冷灰白水泥地面。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "灯光温暖光晕剥离退化。"}
        ],
        "note": "核查发现：长廊右侧红褐色木地板彻底脱色错涂为阴冷灰白地面(C-L2, E2-L2)。"
    },
    3330: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "车站候车站台墙面与机车被恶性错涂为脏暗黄绿色假色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "机车局部微弱脱色。"}
        ],
        "note": "核查发现：车站候车站台墙面与机车被恶性错涂为脏暗黄绿色假色(C-L2, E2-L1)。"
    },
    3363: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "货运列车装载的大量鲜红与鲜橙色集装箱大面积彻底脱色退化为苍白灰白色集装箱。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "两侧山坡绿化树林脱色衰减。"}
        ],
        "note": "核查发现：大量鲜红与鲜橙色集装箱大面积彻底脱色退化为苍白灰白(C-L3, E2-L2)。"
    },
    3366: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "纽约无线电城音乐厅标志性鲜红与金黄色霓虹灯招牌完全脱色蜕变为暗灰白无色招牌。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "繁华街景夜景彩色灯光衰退。"}
        ],
        "note": "核查发现：无线电城标志性鲜红与金黄霓虹灯完全脱色蜕变暗灰白(C-L3, E2-L2)。"
    },
    3375: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "铁道两侧护坡生机翠绿草地大面积脱色衰退为发暗枯草泥色。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "微弱偏色发暗。"}
        ],
        "note": "核查发现：铁道两侧护坡生机翠绿草地大面积脱色衰退为发暗枯草泥色(E2-L2, C-L1)。"
    },
    3381: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "窗台国旗红蓝条纹与花盆鲜红花朵完全脱色蜕变为纯黑白灰度物。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "红木挂钟柜色泽微弱衰减。"}
        ],
        "note": "核查发现：窗台国旗红蓝条纹与鲜红花朵完全脱色蜕变为黑白灰度物(C-L2, E2-L2)。"
    },

    # ================= Sheet 10 (Tasks 175 - 180) =================
    3392: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "实木门框暖黄色泽微弱脱色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "卫生间瓷砖色调轻微泛冷。"}
        ],
        "note": "核查确认：实木门框暖黄色泽微弱脱色泛冷(E2-L1, D-L1)。"
    },
    3441: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "海鸥鲜艳朱红色鸟喙与眼圈彻底脱色退化为发黑无色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "碎石地面细节微弱脱色。"}
        ],
        "note": "核查发现：海鸥鲜艳朱红色鸟喙与眼圈彻底脱色退化为发黑无色(C-L2, E2-L1)。"
    },
    3498: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "山羊身后生机翠绿草地与树木大面积脱色衰退为枯草冷灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "右侧山羊毛色泛冷。"}
        ],
        "note": "核查发现：生机翠绿草地与树木大面积脱色衰退为枯草冷灰(E2-L2, C-L1)。"
    },
    3513: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "挡风玻璃前方晴朗湛蓝天空彻底脱色退化为惨白灰白天幕。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "高大树林生机绿意脱色衰退。"}
        ],
        "note": "核查发现：晴朗湛蓝天空彻底脱色退化为惨白灰白天幕(C-L2, E2-L2)。"
    },
    3555: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "车窗外街景暖阳与绿色交通信号灯色彩略有衰退。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "车内色调略偏冷灰。"}
        ],
        "note": "核查确认：车窗外街景暖阳与绿色交通灯色彩微弱衰退(E2-L1, D-L1)。"
    },
    3586: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "窗台悬挂的常青松柏生机翠绿花环大面积脱色变暗灰。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "窗台木纹色调微弱泛冷。"}
        ],
        "note": "核查发现：常青松柏生机翠绿花环大面积脱色变暗灰(E2-L2, D-L1)。"
    },

    # ================= Sheet 11 (Tasks 181 - 186) =================
    3655: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "海湾远景天际线蔚蓝天空与水体色彩微弱衰退。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "整体微弱偏冷发灰。"}
        ],
        "note": "核查确认：海湾远景蔚蓝天空与水体色彩微弱衰退(E2-L1, D-L1)。"
    },
    3733: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "海面上空滑翔伞与风筝鲜艳红色、紫色与橙色完全脱色退化为黑色污点。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "海滩金黄沙质与海水碧蓝脱色衰退。"}
        ],
        "note": "核查发现：滑翔伞与风筝鲜艳彩色完全脱色退化为黑色污点(C-L2, E2-L2)。"
    },
    3813: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "海角深邃湛蓝海湾海水彻底脱色错涂为发暗灰泥死水。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "沿海生机草甸与红褐碎石海滩大面积脱色衰减。"}
        ],
        "note": "核查发现：湛蓝海湾海水彻底脱色错涂为发暗灰泥死水(C-L2, E2-L2)。"
    },
    3842: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "施工现场悬挂的明黄色临时电缆与暖色管线严重脱色变白。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "地面反光略泛冷灰。"}
        ],
        "note": "核查发现：悬挂明黄临时电缆与暖色管线严重脱色变白(E2-L2, D-L1)。"
    },
    3961: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "沙漠天空中飞行的鲜艳大红色风筝飘带完全脱色衰退为苍白粉白布条。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "金黄沙丘微弱脱色。"}
        ],
        "note": "核查发现：沙漠天空鲜红风筝飘带完全脱色衰退为苍白粉白(C-L2, E2-L1)。"
    },
    3976: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "旅行箱高档亮金色黄铜金属锁扣完全脱色错涂为冰冷银白冷灰合金。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "猫咪肉垫与背景暖光微弱脱色。"}
        ],
        "note": "核查发现：旅行箱亮金色黄铜锁扣完全脱色错涂为冰冷银白冷灰(C-L2, E2-L1)。"
    },

    # ================= Sheet 12 (Tasks 187 - 192) =================
    4007: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "路边步行女子鲜红橙色外套彻底脱色错涂为深黑灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "金黄色油菜花野田与草坡脱色衰减。"}
        ],
        "note": "核查发现：女子鲜红橙色外套彻底脱色错涂为深黑灰色(C-L2, E2-L2)。"
    },
    4009: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "非洲稀树草原金黄干草甸大面积错涂为暗灰青绿。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "大草原金黄特色完全脱色退化。"}
        ],
        "note": "核查发现：草原金黄干草甸大面积错涂为暗灰青绿(C-L2, E2-L2)。"
    },
    4020: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "海滩清澈蔚蓝天空大面积彻底脱色退化为惨淡灰白天幕。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "热带海湾与远山翠绿脱色衰退。"}
        ],
        "note": "核查发现：海滩清澈蔚蓝天空彻底脱色退化为惨淡灰白天幕(C-L2, E2-L2)。"
    },
    4125: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "广阔天空柔和蔚蓝天幕与海潮蓝调大面积脱色衰减为阴冷死灰白。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "微弱偏冷偏暗。"}
        ],
        "note": "核查发现：蔚蓝天幕与海潮蓝调脱色衰减为阴冷死灰白(E2-L2, D-L1)。"
    },
    4133: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "网球男子内搭鲜红色运动T恤领口彻底脱色退化为暗灰黑。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "荧光草绿色网球与女子浅天蓝卫衣脱色衰减。"}
        ],
        "note": "核查发现：男子内搭鲜红T恤领口彻底脱色退化为暗灰黑(C-L2, E2-L2)。"
    },
    4157: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "行道树翠绿树冠与街头暖色行人衣物微弱脱色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "街景略泛冷灰。"}
        ],
        "note": "核查确认：行道树翠绿树冠与街头暖色行人衣物微弱脱色(E2-L1, D-L1)。"
    },

    # ================= Sheet 13 (Tasks 193 - 198) =================
    4168: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "卫生间木质门窗边框暖色木纹与暖调墙壁严重脱色发灰。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "微弱泛冷偏灰。"}
        ],
        "note": "核查发现：木质门窗边框暖色木纹与暖调墙壁严重脱色发灰(E2-L2, D-L1)。"
    },
    4173: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "乡村路牌顶端鲜红色“MAIN ST”路名标牌完全脱色退化为发暗黑灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "路旁翠绿草坡与蓝天大面积脱色衰减。"}
        ],
        "note": "核查发现：乡村路牌顶端鲜红“MAIN ST”标牌完全脱色蜕变黑灰(C-L2, E2-L2)。"
    },
    4181: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "烤箱把手悬挂的生机翠绿与明黄色厨房擦手巾完全脱色退化为暗灰黑抹布。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "橱柜木纹微弱脱色。"}
        ],
        "note": "核查发现：翠绿与明黄擦手巾完全脱色退化为暗灰黑抹布(C-L2, E2-L1)。"
    },
    4198: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "冲浪板板体浅黄绿调与浪花清澈度微弱脱色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "色调略偏冷暗。"}
        ],
        "note": "核查确认：冲浪板浅黄绿调与浪花清澈度微弱脱色(E2-L1, D-L1)。"
    },
    4298: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "厨房红木橱柜与实木地板大面积脱色变冷暗。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "微弱泛冷偏灰。"}
        ],
        "note": "核查发现：厨房红木橱柜与实木地板大面积脱色变冷暗(E2-L2, D-L1)。"
    },
    4319: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "马房牵马员手中鲜艳亮粉红色牵引缰绳被彻底恶性错涂为深宝蓝色伪色绳索。"}
        ],
        "note": "核查发现：牵马员手中亮粉红牵引缰绳被彻底错涂为深宝蓝色(C-L3)。"
    },

    # ================= Sheet 14 (Tasks 199 - 204) =================
    4341: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "海湾碧蓝湖水彻底脱色错涂为发暗泥灰死水。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "棕榈树翠绿生机与天空大面积脱色衰减。"}
        ],
        "note": "核查发现：海湾碧蓝湖水彻底脱色错涂为发暗泥灰死水(C-L2, E2-L2)。"
    },
    4351: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "绵羊金黄色羊毛与迷彩服暖色细节脱色变发暗灰白。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "微弱泛冷偏灰。"}
        ],
        "note": "核查发现：绵羊金黄色羊毛与迷彩服暖色细节脱色变发暗灰白(E2-L2, D-L1)。"
    },
    4369: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "男孩肤色略微泛冷泛青偏灰。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "浅褐棒球帽微弱脱色。"}
        ],
        "note": "核查确认：男孩肤色略微泛冷泛青偏灰(D-L1, E2-L1)。"
    },
    4374: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "绘本封面明黄色圆形标题徽标完全脱色蜕变为惨淡灰白色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "键盘周边色调笼罩阴冷紫灰偏色。"}
        ],
        "note": "核查发现：绘本封面明黄圆形标题徽标完全脱色蜕变惨淡灰白(C-L2, E2-L2)。"
    },
    4435: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "厨房米黄色墙壁暖感微弱衰退。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "微弱偏冷发灰。"}
        ],
        "note": "核查确认：厨房米黄色墙壁暖感微弱衰退(E2-L1, D-L1)。"
    },
    4507: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "海面上空滑翔风筝生机荧光草绿色彻底恶性错涂为深宝蓝色伪色风筝。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "雷雨天云层色阶与水体暗调失真。"}
        ],
        "note": "核查发现：荧光草绿滑翔风筝彻底恶性错涂为深宝蓝色(C-L3, E2-L2)。"
    },

    # ================= Sheet 15 (Tasks 205 - 210) =================
    4525: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "浴室金黄色实木地板与木质浴缸围板完全脱色退化为阴冷灰白水泥色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "室内温暖实木光泽彻底衰退。"}
        ],
        "note": "核查发现：金黄色实木地板与浴缸围板脱色退化为冷灰白(C-L2, E2-L2)。"
    },
    4534: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "游艇悬挂的鲜红色旗帜与船体红色吃水线彻底脱色蜕变黑灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "码头设施色彩微弱衰减。"}
        ],
        "note": "核查发现：游艇鲜红旗帜与船体吃水线彻底脱色蜕变黑灰色(C-L2, E2-L1)。"
    },
    4555: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "旷野公路摩托车鲜艳大红色前脸包围与尾灯彻底脱色退化为深黑灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "清澈深蓝天空与荒漠红褐色大面积脱色衰减。"}
        ],
        "note": "核查发现：摩托车鲜艳大红前脸包围与尾灯彻底脱色退化为深黑灰(C-L2, E2-L2)。"
    },
    4560: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "右侧男子鲜艳天蓝色短袖T恤彻底脱色错涂为深黑灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "草坪翠绿生机大幅脱色衰减。"}
        ],
        "note": "核查发现：右侧男子鲜艳天蓝色短袖彻底脱色错涂为深黑灰色(C-L3, E2-L2)。"
    },
    4614: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "渡轮金黄色跳板与江面水体大面积脱色衰退为暗灰色。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "微弱偏冷发灰。"}
        ],
        "note": "核查发现：渡轮金黄色跳板与江面水体大面积脱色衰退为暗灰(E2-L2, C-L1)。"
    },
    4616: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "机车车头鲜艳明黄色警示条纹与鲜红排障器彻底脱色错涂为发暗黑灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "铁道两侧红土碎石与蓝天大面积脱色衰减。"}
        ],
        "note": "核查发现：机车明黄警示条纹与鲜红排障器彻底脱色错涂发暗黑灰(C-L3, E2-L2)。"
    },

    # ================= Sheet 16 (Tasks 211 - 216) =================
    4629: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "动物园背景生机翠绿灌木与红褐色景石大面积脱色衰减为发冷暗灰。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "微弱偏冷发灰。"}
        ],
        "note": "核查发现：生机翠绿灌木与红褐景石大面积脱色衰减为冷暗灰(E2-L2, C-L1)。"
    },
    4636: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "街头原本冷清蒂芙尼青蓝砖墙被恶性烘烤错涂为暗暖黄褐色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "全景偏暖发黄。"}
        ],
        "note": "核查发现：冷清青蓝砖墙被恶性烘烤错涂为暗暖黄褐色(C-L2, D-L1)。"
    },
    4639: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "海滨木栈道温馨金黄原木地板大面积脱色退化为冰冷灰白水泥色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "老人衣物与海浪蓝调脱色衰减。"}
        ],
        "note": "核查发现：海滨木栈道金黄原木地板大面积脱色退化为灰白水泥色(C-L2, E2-L2)。"
    },
    4721: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "大本钟与议会大厦标志性暖金黄色砂岩立面大面积脱色衰退为冷灰褐色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "微弱偏冷偏暗。"}
        ],
        "note": "核查发现：大本钟与议会大厦暖金黄砂岩立面脱色衰退为冷灰褐(E2-L2, D-L1)。"
    },
    4741: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "维多利亚老洋房鲜艳红砖墙面与朱红陶土瓦屋顶大面积彻底脱色蜕变为阴冷水泥死灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "经典红砖建筑色彩全盘崩溃。"}
        ],
        "note": "核查发现：老洋房红砖墙面与陶土瓦屋顶彻底脱色蜕变阴冷水泥死灰(C-L3, E2-L3)。"
    },
    4746: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "街边商铺暖黄色橱窗照明与古典立面微弱脱色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "微弱偏冷发灰。"}
        ],
        "note": "核查确认：商铺暖黄色橱窗照明与古典立面微弱脱色(E2-L1, D-L1)。"
    },

    # ================= Sheet 17 (Tasks 217 - 222) =================
    4757: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "卫生间原本温馨暖黄卤素灯光与暖色地砖完全脱色退化为冰冷灰白死色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "室内暖调大面积脱色衰减。"}
        ],
        "note": "核查发现：暖黄卤素灯光与暖色地砖完全脱色退化为冰冷灰白死色(C-L2, E2-L2)。"
    },
    4778: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "海滩落日金黄色晚霞光晕与潮湿沙滩暖色倒影大面积脱色衰减。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "微弱偏冷偏暗。"}
        ],
        "note": "核查发现：海滩落日金黄晚霞光晕与暖色倒影大面积脱色衰减(E2-L2, C-L1)。"
    },
    4819: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "卫生间洁白马桶盖板被恶性错涂为脏暗米黄色，实木木板墙面泛脏。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "微弱偏色发脏。"}
        ],
        "note": "核查发现：洁白马桶盖板被恶性错涂为脏暗米黄色(C-L2, D-L1)。"
    },
    4876: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "棒球击球手鲜红色打击头盔与红色袖套彻底脱色错涂为深黑灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "红土内野泥土与球场绿地脱色衰减。"}
        ],
        "note": "核查发现：棒球击球手鲜红打击头盔与袖套彻底脱色错涂为深黑灰(C-L3, E2-L2)。"
    },
    5057: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "海滨晴朗碧蓝天空与海水大面积脱色衰退为发冷暗灰色。"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "天空与海面略偏冷暗。"}
        ],
        "note": "核查发现：海滨晴朗碧蓝天空与海水大面积脱色衰退为发冷暗灰(E2-L2, C-L1)。"
    },
    5254: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "特色图腾彩绘消火栓鲜艳大红色阀门出水口盖彻底脱色蜕变为暗黑灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "背景公园绿化树木脱色衰减。"}
        ],
        "note": "核查发现：彩绘消火栓鲜红阀门出水口盖彻底脱色蜕变为暗黑灰(C-L2, E2-L2)。"
    },

    # ================= Sheet 18 (Tasks 223 - 228) =================
    5279: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "右侧建筑外墙悬挂的鲜红色法拉利大型条幅彻底脱色退化为苍白灰白色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "大教堂红砖立面与陶瓦脱色衰减。"}
        ],
        "note": "核查发现：外墙悬挂鲜红法拉利条幅彻底脱色退化为苍白灰白(C-L2, E2-L2)。"
    },
    5357: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "路边拍照男子鲜艳牛仔蓝色长裤彻底脱色错涂为深黑灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "草地微弱脱色。"}
        ],
        "note": "核查发现：路边男子鲜艳牛仔蓝长裤彻底脱色错涂为深黑灰色(C-L2, E2-L1)。"
    },
    5361: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "厨房温馨金黄原木地板大面积脱色退化为冷灰泥色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "橱柜与高脚凳实木色彩衰退。"}
        ],
        "note": "核查发现：厨房温馨金黄原木地板大面积脱色退化为冷灰泥色(C-L2, E2-L2)。"
    },
    5368: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "海浪碧绿透明水体彻底脱色退化为发暗浑浊灰泥水。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "浪花清澈度大幅衰减。"}
        ],
        "note": "核查发现：海浪碧绿透明水体彻底脱色退化为发暗浑浊灰泥水(C-L2, E2-L2)。"
    },
    5377: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "街道背景鲜艳红砖墙面大面积彻底脱色退化为阴冷灰白水泥色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "红砖肌理色彩全盘崩溃。"}
        ],
        "note": "核查发现：背景鲜艳红砖墙面大面积彻底脱色退化为阴冷灰白水泥色(C-L3, E2-L3)。"
    },
    5399: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "海湾深邃湛蓝海浪水体彻底脱色退化为发暗灰泥水。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "远景苍翠绿化山林大面积脱色衰减。"}
        ],
        "note": "核查发现：海湾深邃湛蓝海浪水体彻底脱色退化为发暗灰泥水(C-L2, E2-L2)。"
    },

    # ================= Sheet 19 (Tasks 229 - 234) =================
    5403: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "艺术留色照片中鲜红消火栓与黄色野花严重脱色退化为发灰粉色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "主体特征红色饱和度衰退。"}
        ],
        "note": "核查发现：留色照片中鲜红消火栓严重脱色退化为发灰粉色(C-L2, E2-L2)。"
    },
    511: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "沥青路面鲜黄色弯道导向标线完全脱色退化为惨白灰白线条。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "右侧护坡生机草坪脱色衰减为发暗枯草色。"}
        ],
        "note": "核查发现：沥青路面鲜黄色弯道导向标线完全脱色蜕变惨白灰白(C-L2, E2-L2)。"
    },
    537: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "墙上艺术画作鲜艳红橙色画面与画框完全脱色退化为暗灰发黑无色画框。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "樱桃木餐桌椅暖光大面积脱色衰减。"}
        ],
        "note": "核查发现：画作鲜艳红橙色画面与画框完全脱色蜕变暗灰发黑(C-L2, E2-L2)。"
    },
    604: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "洗手台红木浴室柜深红褐色泽大面积脱色衰减为发冷暗褐灰。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "微弱偏冷发灰。"}
        ],
        "note": "核查发现：红木浴室柜深红褐色泽脱色衰减为发冷暗褐灰(E2-L2, D-L1)。"
    },
    622: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "公交候车亭鲜艳天宝蓝色金属支架与座椅彻底脱色错涂为惨白灰白色，军绿背包褪色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "阳光街景大面积脱色衰减。"}
        ],
        "note": "核查发现：候车亭天宝蓝金属支架座椅彻底脱色错涂惨白灰白(C-L3, E2-L2)。"
    },
    630: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "长椅四周生机翠绿草坪大面积彻底脱色错涂为发暗枯草土灰色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "公园绿地生机完全剥离退化。"}
        ],
        "note": "核查发现：长椅四周翠绿草坪彻底脱色错涂为发暗枯草土灰(C-L2, E2-L2)。"
    },

    # ================= Sheet 20 (Tasks 235 - 240) =================
    654: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "生机翠绿山坡草场大面积彻底脱色错涂为苍白枯草泥灰地。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "牧场绿色生机彻底剥离。"}
        ],
        "note": "核查发现：生机翠绿山坡草场大面积彻底脱色错涂为苍白枯草泥灰(C-L2, E2-L2)。"
    },
    664: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L3", "description": "行李大厅大批旅客鲜艳大红色、明黄色与亮蓝色行李箱彻底脱色蜕变为暗灰黑色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "全场高饱和彩色行李箱完全崩溃脱色。"}
        ],
        "note": "核查发现：大批鲜红、明黄与亮蓝行李箱彻底脱色蜕变为暗灰黑(C-L3, E2-L3)。"
    },
    669: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "海水湛蓝与清澈浪花微弱脱色。"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "海面略泛暗冷灰。"}
        ],
        "note": "核查确认：海水湛蓝与清澈浪花微弱脱色(E2-L1, D-L1)。"
    },
    681: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "道路背景生机翠绿山坡草坪大面积彻底脱色错涂为暗黄枯草地。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "草地生机绿意完全脱色衰退。"}
        ],
        "note": "核查发现：道路背景翠绿草坪彻底脱色错涂为暗黄枯草地(C-L2, E2-L2)。"
    },
    704: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "农场人员粉红色与蓝色外套彻底脱色退化为苍白灰白色衣服，猎犬背毛泛杂色。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "农场人物衣物大面积脱色衰减。"}
        ],
        "note": "核查发现：人员粉红与蓝外套彻底脱色蜕变苍白灰白(C-L2, E2-L2)。"
    },
    720: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "斑马与羚羊栖息的翠绿草甸大面积彻底脱色错涂为发暗泥灰死地。"},
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "背景林木翠绿枝叶脱色衰减。"}
        ],
        "note": "核查发现：斑马栖息的翠绿草甸大面积彻底脱色错涂为发暗泥灰死地(C-L2, E2-L2)。"
    }
}

def main():
    print(f"Applying visual audit fixes for {len(ROUND2_FIXES)} tasks in Round 2...")

    with open(ALL_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)
    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    all_anns = all_data["annotations"]
    clean_anns = clean_data["annotations"]

    all_map = {ann["human_review"]["task_id"]: ann for ann in all_anns}
    clean_map = {ann["human_review"]["task_id"]: ann for ann in clean_anns}

    applied_count = 0
    for tid, fix_info in ROUND2_FIXES.items():
        if tid in all_map:
            ann_all = all_map[tid]
            ann_clean = clean_map[tid]

            ann_all["defects"] = fix_info["defects"]
            ann_all["review_note"] = fix_info["note"]
            ann_all["reviewed_score"] = None
            ann_all["needs_rescoring"] = True
            ann_all["review_status"] = "已核验"

            ann_clean["defects"] = fix_info["defects"]
            ann_clean["review_note"] = ""
            ann_clean["reviewed_score"] = None
            ann_clean["needs_rescoring"] = True
            ann_clean["review_status"] = "已核验"

            applied_count += 1
        else:
            print(f"Warning: Task {tid} not found in annotations!")

    print(f"Successfully applied fixes to {applied_count} / {len(ROUND2_FIXES)} tasks!")

    with open(ALL_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    with open(CLEAN_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)

    print("Both all.json and clean.json updated successfully!")

if __name__ == "__main__":
    main()
