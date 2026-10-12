"""Apply Double Check updates for batch 9501-10000 pass tasks.
Updates reviewed_9501_10000, stream package, and full 1-10000 exports.
Follows the exact V4 schema contract from AGENTS.md.
"""
import json
import os
import shutil
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"
STREAMS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "streams"

# 64 Grounded Double Check Corrections for 9501-10000
DC_CORRECTIONS = {
    9510: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "唐人街街景中交通信号灯上方原本醒目警示的红色指示灯与建筑上方大红灯笼在LCAD生成图中严重脱色黑化剥夺(RedLoss=0.58, Rsat=0.64)，退化为死黑圆斑"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "行人过街白色标牌与后方中式招牌暗部略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：交通信号灯红灯指示与大红灯笼严重脱色黑化(RedLoss=0.58)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9514: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "单轨列车车身原本醒目鲜艳的大红色SYDNEY宣传横幅与红色标识在LCAD生成图中大面积严重脱色抹杀(RedLoss=0.78)，退化为灰暗无色条带"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "站台建筑金属立面与下方绿化带暗部略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：单轨列车大红色宣传横幅与标识大面积严重脱色退化为灰暗无色(RedLoss=0.78)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9518: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "海滩奔跑宠物犬脚下原本温润浅黄褐色的干爽沙滩地面在LCAD生成图中大面积脱色泛白，蜕变为冰冷惨白的死灰水泥色(RedLoss=0.78, Rsat=0.65)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "阴天云层暗部与小狗背部棕黑杂毛略微泛暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：海滩原本温润浅黄褐色沙地大面积脱色为冰冷惨白死灰色(RedLoss=0.78)，改判欠饱和(E2-L2)与偏色(D-L1)。"
    },
    9519: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "推婴儿车男子手中原本醒目鲜艳的大红色塑料水杯与身后路人红帽在LCAD生成图中严重脱色褪淡(Rsat=0.44)，退化为发脏浅灰粉色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "右侧男子身上原本鲜亮的天蓝色牛仔衬衫脱色发灰泛绿"}
        ],
        "review_note": "Double Check复核改判：核查发现：男子手中大红塑料水杯严重脱色褪淡，牛仔衬衫脱色泛绿(Rsat=0.44)，清洗伪满分，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9529: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "卫生间原本清爽明亮的窗外自然采光与白色瓷砖洗手台在LCAD生成图中被全屋烘烤为极其浓重突兀的暖黄偏色(DeltaC=0.079, Rsat=1.34)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "淋浴玻璃隔断与右侧墙角暗部过度泛黄焦化"}
        ],
        "review_note": "Double Check复核改判：核查发现：卫生间全屋被浓重烘烤为突兀暖黄偏色(DeltaC=0.079)，改判偏色(D-L2)与错色(C-L1)。"
    },
    9530: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "沙滩空中飞跃的原本极其醒目鲜亮纯正的亮黄色飞盘在LCAD生成图中被恶性篡改错涂为突兀鲜艳的粉红亮红色伪色(RedLoss=0.92)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "远处防波堤海水与沙滩游客衣物暗部略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：空中原本纯正亮黄飞盘被恶性错涂为突兀粉红亮红伪色(RedLoss=0.92)，改判错色(C-L2)与偏色(D-L1)。"
    },
    9531: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "卫生间马桶右侧原本鲜艳醒目的大红马桶刷与黄色软管在LCAD生成图中严重脱色发暗，退化为深紫暗灰调(RedLoss=0.21)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "窗台上绿色小盆栽叶片略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：马桶旁大红马桶刷与黄色软管严重脱色发暗(RedLoss=0.21)，改判欠饱和(E2-L1)与错色(C-L1)。"
    },
    9533: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "餐桌前微笑女士身上原本鲜艳纯正的深海蓝色短袖T恤在LCAD生成图中被恶性篡改错涂为浓艳紫红洋红色伪色，蓝色色相彻底颠覆篡改(Rsat=1.23)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "盘中烤披萨表面起司与罗勒叶略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：女士身上深海蓝短袖被恶性错涂为浓艳紫红洋红伪色(Rsat=1.23)，改判错色(C-L2)与偏色(D-L1)。"
    },
    9546: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "老式浴缸卫生间室内木饰墙面与暖气片在LCAD生成图中过度浓艳烘烤，全景泛出极其突兀刺目的浓重红橙焦化偏色(Rsat=1.62)"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "顶灯照明区域边缘产生不自然的橙红光晕"}
        ],
        "review_note": "Double Check复核改判：核查发现：卫生间室内木饰墙面全景泛出突兀浓重红橙焦化偏色(Rsat=1.62)，改判偏色(D-L2)与过饱和(E1-L1)。"
    },
    9548: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "沙滩冲浪板旁红发小男孩身上原本鲜亮纯正的鲜红色短袖T恤在LCAD生成图中被恶性错涂为浅冷淡紫粉白色伪色，后方冲浪板红色饰条严重脱色"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "沙滩沙粒色泽与蓝色冲浪板边缘微显泛白"}
        ],
        "review_note": "Double Check复核改判：核查发现：红发男孩鲜红短袖被恶性错涂为冷淡紫粉白色伪色，冲浪板红条脱色，改判错色(C-L2)与欠饱和(E2-L1)。"
    },
    9549: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "温莎城堡古堡石塔上方原本清澈的浅淡蓝天在LCAD生成图中大面积脱色为单调死灰天幕，时钟金色钟盘严重失色暗化(Rsat=0.48, RedLoss=0.23)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "古石墙立面背光暗部微显泛冷泛绿"}
        ],
        "review_note": "Double Check复核改判：核查发现：古堡蓝天大面积脱色为死灰天幕，金色钟盘失色暗化(Rsat=0.48)，改判欠饱和(E2-L2)与偏色(D-L1)。"
    },
    9552: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "复古白色燃气灶原本洁白平整的烤漆金属立面与烤箱门在LCAD生成图中被大面积污染侵蚀，泛出大片脏乱突兀的红褐紫灰偏色色斑(DeltaC=0.088)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "灶台上方旋钮与侧面金属烤面包机冷光反射略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：复古白色烤漆燃气灶立面大面积污染泛出红褐紫灰偏色(DeltaC=0.088)，清洗伪满分，改判偏色(D-L2)与错色(C-L1)。"
    },
    9560: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "公交车厢内原本温暖唯美的金色阳光斜射光斑在LCAD生成图中被彻底剥夺脱色为惨白无色强光，后排乘客醒目红色衣着完全脱色黑化(RedLoss=0.87, Rsat=0.29)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "深色皮质座椅靠背阴影处微显发灰泛冷"}
        ],
        "review_note": "Double Check复核改判：核查发现：车厢内金色阳光光斑彻底脱色为惨白，乘客红衣完全黑化(RedLoss=0.87)，改判欠饱和(E2-L2)与偏色(D-L1)。"
    },
    9562: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "高架桥下右下角原本极其醒目的大红色KFC招牌立柱与红色小轿车在LCAD生成图中严重脱色褪淡(RedLoss=0.50)，完全蜕变为沉闷暗灰死色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "车道中央隔离带原本嫩绿的绿化灌木丛略显暗淡"}
        ],
        "review_note": "Double Check复核改判：核查发现：右下角大红KFC招牌立柱与红色小车严重脱色为暗灰死色(RedLoss=0.50)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9570: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "雪景街道路灯原本温暖自然的暖白淡黄圆形灯罩在LCAD生成图中被恶性涂抹为极其突兀惊悚的高饱和荧光洋红粉紫光球伪色(Rsat=2.02)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "撑伞雪中漫步路人衣物与积雪地面略显发脏偏暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：路灯暖白淡黄灯罩被恶性错涂为高饱和荧光洋红粉紫光球伪色(Rsat=2.02)，改判错色(C-L2)与偏色(D-L1)。"
    },
    9582: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "碎花被褥上斯纳普饮料瓶身原本鲜艳明亮的水果标签与粉红花纹在LCAD生成图中脱色发暗，退化为暗灰混杂色(DeltaC=0.072)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "黑色小狗毛发高光与背景墙角略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：碎花被褥上饮料瓶水果标签与粉红花纹脱色发暗(DeltaC=0.072)，改判欠饱和(E2-L1)与偏色(D-L1)。"
    },
    9592: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "生态大巴车身正面与侧面上方原本极其醒目明艳的大红色BIOGAS TOUR品牌标语在LCAD生成图中被恶性篡改错涂为发暗深黑紫蓝伪色"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "大巴侧面草坪拉花与车顶行李架边缘微显脱色"}
        ],
        "review_note": "Double Check复核改判：核查发现：大巴车身醒目大红品牌标语被恶性错涂为深黑紫蓝伪色，清洗伪满分，改判错色(C-L2)与欠饱和(E2-L1)。"
    },
    9593: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "黄昏栈桥水面上原本生机唯美的金色晚霞天空与波光倒影在LCAD生成图中被大面积彻底抹杀脱色，完全蜕变为阴沉死寂的单调冷死灰(RedLoss=0.82, Rsat=0.38)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "木质栈桥立柱与骑行游人背影略显发乌"}
        ],
        "review_note": "Double Check复核改判：核查发现：黄昏水面金色晚霞倒影被彻底抹杀脱色为阴沉死寂冷死灰(RedLoss=0.82)，改判欠饱和(E2-L2)与偏色(D-L1)。"
    },
    9596: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "餐厅后厨掌勺厨师身上原本鲜亮的天蓝色围裙与帽子装饰线条在LCAD生成图中脱色发暗，退化为黯淡灰白色(RedLoss=0.32, Rsat=0.75)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "灶台上方不锈钢大锅反光与黄光照明暗部略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：后厨厨师天蓝围裙与帽子饰线脱色发暗为灰白色(RedLoss=0.32)，改判欠饱和(E2-L1)与错色(C-L1)。"
    },
    9600: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "玻璃餐盒内原本鲜艳明亮的小胡萝卜在LCAD生成图中大面积脱色褪淡，退化为暗哑土橙黄无光泽色相"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "西兰花翠绿花冠与白花菜边缘略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：玻璃餐盒内鲜艳小胡萝卜大面积脱色褪淡为暗哑土橙黄，改判欠饱和(E2-L1)与错色(C-L1)。"
    },
    9604: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "足球场上后方替补席球员身穿的原本明艳醒目的亮黄色荧光背心在LCAD生成图中大面积脱色褪白，蜕变为苍白浅灰无色背心(DeltaC=0.062)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "奔跑争球的红队球员大红球袜暗部略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：足球场替补席球员亮黄荧光背心大面积脱色褪白为苍白浅灰(DeltaC=0.062)，清洗伪满分，改判欠饱和(E2-L1)与错色(C-L1)。"
    },
    9608: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "欧洲城市广场钟楼建筑屋顶原本极其醒目的尖顶大红色塔冠在LCAD生成图中大面积脱色抹杀(RedLoss=0.61)，蜕变为灰白无色水泥色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "街角商业建筑拱门立面与街道游人暗部略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：城市广场钟楼建筑屋顶尖顶大红塔冠大面积脱色蜕变为灰白色(RedLoss=0.61)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9609: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "电脑书桌右侧原本鲜艳醒目的大红长条鼠标垫与左右两侧大红色办公椅扶手在LCAD生成图中严重脱色抹杀(RedLoss=0.86, Rsat=0.58)，退化为死黑灰暗"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "显示器壁纸天蓝色泽与玻璃桌面反光微显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：电脑桌大红长条鼠标垫与大红办公椅严重脱色抹杀为死黑灰暗(RedLoss=0.86)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9622: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "草原山脚下奔腾黑马背景的原本清爽淡蓝灰的天空与远山在LCAD生成图中被大面积烘烤为极其浑浊浓重的土黄红褐偏色(Rsat=1.84)"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "近处草场暗部草皮过度泛红焦化"}
        ],
        "review_note": "Double Check复核改判：核查发现：黑马背景淡蓝天与远山被大面积烘烤为浑浊土黄红褐偏色(Rsat=1.84)，改判偏色(D-L2)与过饱和(E1-L1)。"
    },
    9623: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "街头行驶的经典双层客车原本极其醒目纯正的鲜艳宝蓝色车身在LCAD生成图中被灾难性恶性错涂为发暗灰泥色米褐土黄色伪色，车体色相彻底颠覆篡改(DeltaC=0.051)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "车身侧面电影广告橙色海报边缘略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：双层客车经典宝蓝色车身被灾难性恶性错涂为灰泥米褐土黄伪色(DeltaC=0.051)，改判错色(C-L2)与偏色(D-L1)。"
    },
    9626: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "街道路口左侧原本生机古朴的红砖居民建筑外立面与红色招牌在LCAD生成图中大面积脱色褪淡(RedLoss=0.18)，退化为冰冷水泥死灰调"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "行道树葱郁树冠与路面越野军绿卡车微显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：街道路口左侧红砖建筑外墙与红色招牌脱色为水泥死灰(RedLoss=0.18)，清洗伪满分，改判欠饱和(E2-L1)与错色(C-L1)。"
    },
    9630: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "头戴安全帽的小女孩手中原本极其醒目鲜艳可爱的亮粉红色毛绒泰迪熊在LCAD生成图中被恶性篡改错涂为嫩黄色毛绒熊伪色，右侧女孩原本亮粉红色的安全帽被错涂为惨白灰白色"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "小女孩牛仔短裤与背景绿树边缘微显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：女孩鲜艳粉红泰迪熊被恶性错涂为嫩黄熊伪色，粉红安全帽错涂惨白，清洗伪满分，改判错色(C-L2)与欠饱和(E2-L1)。"
    },
    9631: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "户外披萨餐桌后方左上角路人身上原本鲜亮明艳的亮黄色短袖在LCAD生成图中被恶性篡改错涂为发脏发黑的深褐黑灰色伪色(Rsat=1.54)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "前方面对镜头男子面部与浅色衬衫微显泛红偏暖"}
        ],
        "review_note": "Double Check复核改判：核查发现：左上角路人原本亮黄短袖被恶性错涂为发脏深褐黑灰伪色(Rsat=1.54)，清洗伪满分，改判错色(C-L2)与偏色(D-L1)。"
    },
    9638: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "餐盘中热狗长面包夹心内原本鲜红欲滴的番茄肉酱在LCAD生成图中脱色发暗，退化为黯淡褐黑混杂色(RedLoss=0.16)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "后方炸薯条金黄色泽与吸油纸暗部略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：热狗夹心鲜红番茄肉酱脱色发暗为黯淡褐黑色(RedLoss=0.16)，改判欠饱和(E2-L1)与错色(C-L1)。"
    },
    9646: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "草坪奔跑接飞盘的小男孩身上原本极其明艳醒目的亮黄色短袖T恤在LCAD生成图中大面积彻底脱色褪淡，完全退化为苍白浅灰无色汗衫(DeltaC=0.088, Rsat=0.61)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "脚下青翠草坪在LCAD生成图中大面积发暗褪变灰土枯黄色"}
        ],
        "review_note": "Double Check复核改判：核查发现：奔跑男孩身上亮黄短袖彻底脱色退化为苍白浅灰无色汗衫(DeltaC=0.088)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9647: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "十字路口上方原本极其醒目的明黄色交通信号灯罩与前车原本鲜艳的大红色刹车尾灯在LCAD生成图中大面积脱色黑化(RedLoss=0.69, Rsat=0.44)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "背景春季开花树木花冠与道路绿化带略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：十字路口明黄信号灯罩与大红汽车尾灯大面积脱色黑化(RedLoss=0.69)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9648: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "林地空地上原本温润自然的棕黄色泥土地面与骏马毛皮在LCAD生成图中全景大面积严重脱色坍塌，整个场景退化为单调冷灰死暗单色调(RedLoss=0.41, Rsat=0.33)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "背景树林枝干背光处泛出轻微暗紫冷色"}
        ],
        "review_note": "Double Check复核改判：核查发现：林地温润泥土地与骏马大面积严重脱色坍塌为单调冷灰死暗单色(Rsat=0.33)，改判欠饱和(E2-L2)与偏色(D-L1)。"
    },
    9650: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "浪花中冲浪男子身上原本鲜亮醒目的红色冲浪短裤在LCAD生成图中脱色发暗，退化为深褐暗红"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白色浪花泡沫与灰色海面泛出突兀噪点(Rsat=1.90)"}
        ],
        "review_note": "Double Check复核改判：核查发现：冲浪男子红色短裤脱色发暗，海浪泛出噪点偏色(Rsat=1.90)，改判欠饱和(E2-L1)与偏色(D-L1)。"
    },
    9660: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "卫生间圆镜前原本洁净冷白的瓷砖墙面与洗手台在LCAD生成图中大面积污染侵蚀，泛出极其突兀不自然的脏乱暗黄偏绿偏色(RedLoss=0.50, Rsat=0.67)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "女子自拍时黑色衣服与深色长发边缘略显发乌"}
        ],
        "review_note": "Double Check复核改判：核查发现：卫生间冷白瓷砖墙面大面积泛出突兀脏乱暗黄偏绿偏色(RedLoss=0.50)，改判偏色(D-L2)与错色(C-L1)。"
    },
    9662: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "街头悬挂在蓝色圆形自行车标志下方的告示提示标牌原本鲜艳醒目的亮橙黄色底板在LCAD生成图中被恶性篡改错涂为发暗枯黄暗绿橄榄色伪色(RedLoss=0.42)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "街道两旁高楼大厦金属幕墙暗部微显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：街头提示标牌原本亮橙黄底板被恶性错涂为发暗枯黄暗绿橄榄色伪色(RedLoss=0.42)，改判错色(C-L2)与偏色(D-L1)。"
    },
    9669: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "雪原铁道上复古客运列车车厢原本纯净清澈的浅淡蓝天在LCAD生成图中被大面积严重污染，泛出极其突兀脏乱的青绿黄褐色阴霾偏色(DeltaC=0.089)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "铁轨积雪高光与车厢金属外壳边缘略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：客运车厢蓝天大面积严重污染泛出青绿黄褐阴霾偏色(DeltaC=0.089)，改判偏色(D-L2)与错色(C-L1)。"
    },
    9676: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "复古艺术客厅上方原本清爽淡蓝色的窗框与淡黄墙面在LCAD生成图中被恶性错涂为刺眼荧光青蓝与高饱和紫红伪色，色彩杂乱失控(DeltaC=0.082)"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "地毯、伞具与家具暗部产生严重荧光溢色"}
        ],
        "review_note": "Double Check复核改判：核查发现：复古客厅窗框与墙面被恶性错涂为刺眼荧光青蓝与高饱和紫红伪色(DeltaC=0.082)，改判错色(C-L2)与过饱和(E1-L1)。"
    },
    9680: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "洗手间发光圆形镜子后方原本极具质感与辨识度的浓郁深酒红色漆面墙壁在LCAD生成图中被大面积灾难性恶性错涂为浑浊暗淡的泥灰土黄褐色伪色(DeltaC=0.077, RedLoss=0.33)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "大理石洗手台面与镜框边缘略显暗沉"}
        ],
        "review_note": "Double Check复核改判：核查发现：洗手间深酒红漆面墙壁被大面积灾难性错涂为浑浊泥灰土黄褐伪色(DeltaC=0.077)，改判错色(C-L2)与偏色(D-L1)。"
    },
    9681: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "度假海滩上原本密密麻麻排列的鲜艳大红与亮黄色遮阳伞群与游人泳装在LCAD生成图中大面积严重脱色抹杀(RedLoss=0.80, DeltaC=0.081)，全部退化为灰黑死暗"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "浅海清澈海水与沙滩近处游人微显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：度假海滩原本鲜艳大红与亮黄遮阳伞群严重脱色退化为灰黑死暗(RedLoss=0.80)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9686: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "城市街道军用运输卡车后斗两侧原本极其醒目警示的大红橙色反光示宽标识在LCAD生成图中完全脱色黑化(RedLoss=0.74)，蜕变为暗沉死黑圆框"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "街道前方小轿车车尾灯与人行道树木略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：运输卡车后斗大红橙色反光示宽标识完全脱色黑化(RedLoss=0.74)，清洗伪满分，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9687: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "厨房台面上排列的原本醒目鲜艳的大红色调料罐盖子与大红色加州阳光葡萄干纸盒在LCAD生成图中大面积脱色褪淡(RedLoss=0.44, Rsat=0.67)，完全退化为灰褐无色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "木质橱柜抽屉与台面散落食物略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：厨房调料罐大红盖子与大红葡萄干包装盒大面积脱色为灰褐色(RedLoss=0.44)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9706: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "喂牛槽后方饲养员身上原本醒目的紫色工作服与黑牛耳部明黄耳标在LCAD生成图中脱色发暗，退化为深暗灰黑色(RedLoss=0.36, Rsat=0.68)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "槽中饲料与牛棚围栏边缘略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：饲养员紫色工作服与明黄耳标脱色发暗为深暗灰黑(RedLoss=0.36)，改判欠饱和(E2-L1)与错色(C-L1)。"
    },
    9715: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "雪原越野滑雪选手身上原本极其醒目夺目的亮粉红洋红色滑雪夹克在LCAD生成图中大面积彻底脱色抹杀(RedLoss=0.95)，完全退化为苍白死灰无色风衣"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "滑雪杖与背景松树防护林枝叶边缘略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：滑雪选手身上亮粉红洋红夹克彻底脱色抹杀为苍白死灰(RedLoss=0.95)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9719: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "雪山峰顶登山滑雪者身上原本极其鲜艳醒目的大红色专业滑雪冲锋裤在LCAD生成图中大面积脱色黑化(RedLoss=0.91, Rsat=0.57)，完全退化为暗沉深黑炭灰裤"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "左下角原本鲜艳的大红滑雪服与背包略显暗沉"}
        ],
        "review_note": "Double Check复核改判：核查发现：登山滑雪者大红滑雪冲锋裤大面积脱色黑化为深黑炭灰(RedLoss=0.91)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9724: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "无障碍卫生间上方吊挂的辅助抬升梯原本极其醒目明艳的橙红色横档梯级在LCAD生成图中完全脱色褪白(RedLoss=0.36, Rsat=0.57)，蜕变为冰冷惨白的纯灰白色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "马桶扶手金属反光与侧面瓷砖缝隙微显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：无障碍卫生间辅助抬升梯橙红梯级完全脱色褪白为纯灰白色(RedLoss=0.36)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9730: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "餐桌上热炒大圆盘下方原本极其鲜亮纯正的深宝蓝色釉面瓷砖台面在LCAD生成图中大面积严重脱色褪淡(RedLoss=0.55, Rsat=0.66)，蜕变为苍白浅灰无色瓷砖"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "炒菜中胡萝卜与红椒切片边缘略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：餐桌深宝蓝釉面瓷砖大面积严重脱色褪淡为苍白浅灰(RedLoss=0.55)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9731: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "微波炉控制面板右侧原本彩色醒目的红蓝黄三色数字按钮与指示图标在LCAD生成图中完全脱色黑化(RedLoss=0.75)，退化为死黑单色按键"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "炉腔内巴哥犬浅黄褐色毛皮略显脱色发灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：微波炉彩色控制按钮与指示图标完全脱色黑化为死黑单色(RedLoss=0.75)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9734: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "机场候机厅行李推车上方原本极其醒目明艳的亮黄色发光导向灯箱在LCAD生成图中完全脱色漂白为惨白无色发光盒，右侧女孩原本鲜艳的大红色卫衣严重脱色发暗"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "行李推车格纹行李袋与地毯暗部略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：机场亮黄导向灯箱完全漂白为惨白，女孩大红卫衣严重脱色发暗，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9737: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街道停车收费机正面原本醒目明艳的橙红色投币说明标识与上方深海蓝色P字停车标牌在LCAD生成图中严重脱色褪淡(RedLoss=0.17, Rsat=0.64)，完全失真暗化"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "白色欧式建筑外立面与街景蓝天略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：停车收费机橙红说明标与深海蓝P字标牌严重脱色褪淡(RedLoss=0.17)，清洗伪满分，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9738: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "广阔海面天际线上原本具有深邃蓝灰层次的海水色泽在LCAD生成图中脱色泛平，完全退化为单调暗沉的死灰水泥色(Rsat=0.62)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "远方货轮金属轮廓与近处皮划艇边缘微显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：海面海水深邃蓝灰层次脱色退化为单调暗沉死灰色(Rsat=0.62)，改判欠饱和(E2-L1)与偏色(D-L1)。"
    },
    9739: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "公园长椅与自行车旁原本生机盛放的粉红紫红色樱花树冠在LCAD生成图中大面积严重脱色漂白(RedLoss=0.41, Rsat=0.54)，完全褪变为枯萎灰白色的残花杂木"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "树荫下青翠草坪在LCAD生成图中略显发暗偏黄"}
        ],
        "review_note": "Double Check复核改判：核查发现：盛开粉红紫红樱花树冠大面积严重脱色漂白为灰白色(RedLoss=0.41)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9753: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "密林树枝间雏鸟猫头鹰周围原本生机苍翠的鲜嫩绿苔藓与树叶在LCAD生成图中被恶性错涂为发暗深青蓝死寂冷色，猫头鹰眼睛错涂荧光冷蓝(RedLoss=0.56, Rsat=0.60)"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "雏鸟棕褐色绒毛在LCAD生成图中严重脱色发灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：密林翠绿苔藓被恶性错涂为发暗深青蓝色，猫头鹰眼错涂冷蓝(RedLoss=0.56)，改判错色(C-L2)与欠饱和(E2-L1)。"
    },
    9764: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "走廊门框内原本洁净冷白的瓷砖卫生间立面与天花板在LCAD生成图中被大面积严重污染烘烤，全室泛出极其突兀脏乱的黄绿泥浆偏色(DeltaC=0.085)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "地面地毯原本墨绿图案与毛巾架略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：卫生间立面与天花板全室泛出突兀脏乱黄绿泥浆偏色(DeltaC=0.085)，清洗伪满分，改判偏色(D-L2)与错色(C-L1)。"
    },
    9765: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "海浪中站立冲浪女孩身上原本极其明艳醒目的亮黄色防晒冲浪服与冲浪板红色饰边在LCAD生成图中严重脱色褪白，后方俯卧女孩原本亮粉红色的冲浪服完全脱色褪淡(Rsat=0.60, DeltaC=0.084)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "海浪翻滚泡沫与海水交界处微显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：冲浪女孩亮黄冲浪服与板边红线脱色褪白，俯卧女孩粉红服脱色(Rsat=0.60)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9774: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "温馨卧室角落落地灯原本温暖唯美的金色照度光晕与暖桃黄墙面在LCAD生成图中被恶性篡改为阴森冰冷的冷紫灰偏色暗调(DeltaC=0.087, RedLoss=0.58)"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "窗帘几何挂毯彩色条纹在LCAD生成图中脱色泛暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：落地灯温暖金光与暖桃黄墙面被恶性篡改为阴森冷紫灰偏色(DeltaC=0.087)，改判偏色(D-L2)与欠饱和(E2-L1)。"
    },
    9780: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L1", "description": "餐盘烤披萨表面原本生机青翠的菠菜罗勒绿叶在LCAD生成图中被恶性烘烤为焦黑干枯的深褐酱色伪色(DeltaC=0.057)"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "红酱起司表面焦斑略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：披萨表面青翠罗勒菠菜叶被恶性烘烤为焦黑干枯深褐色(DeltaC=0.057)，清洗伪满分，改判错色(C-L1)与欠饱和(E2-L1)。"
    },
    9788: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "河道戏水大象周围原本温暖浑浊的浅黄褐色泥水池在LCAD生成图中被恶性错涂为极其突兀不自然的生硬浅青绿发光水体，大象背部皮肤泛出严重冷蓝紫偏色(DeltaC=0.081, RedLoss=0.40)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "右上方土坡泥地暗部微显发暗泛冷"}
        ],
        "review_note": "Double Check复核改判：核查发现：泥水池被恶性错涂为生硬浅青绿发光水体，大象背部泛冷蓝紫偏色(DeltaC=0.081)，改判偏色(D-L2)与错色(C-L1)。"
    },
    9791: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "黄昏拥堵公路上前行车辆原本鲜艳醒目的大红色刹车尾灯与橙黄转向警示灯在LCAD生成图中脱色发暗，退化为发灰暗红色斑(RedLoss=0.36)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "高速隔离带中央绿色路标标牌略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：车辆大红刹车尾灯与橙黄转向灯脱色发暗为灰暗红斑(RedLoss=0.36)，改判欠饱和(E2-L1)与错色(C-L1)。"
    },
    9811: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "雪原飞跃单板滑雪选手原本色彩鲜艳的大红色滑雪板底涂装图案在LCAD生成图中大面积脱色发暗(RedLoss=0.47)，退化为深褐暗红"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "激荡起的雪粉边缘与天空交界处微显泛暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：滑雪板底鲜艳大红图案大面积脱色发暗退化为深褐暗红(RedLoss=0.47)，改判欠饱和(E2-L1)与错色(C-L1)。"
    },
    9812: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "动物园长颈鹿身后原本生机青翠的整片绿化树林与远方摩天大楼天际线在LCAD生成图中大面积严重脱色坍塌，完全退化为灰冷死寂的阴沉暗灰(DeltaC=0.091, Rsat=0.47, RedLoss=0.77)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "长颈鹿原本温暖饱满的红褐网状斑纹略显脱色褪淡"}
        ],
        "review_note": "Double Check复核改判：核查发现：长颈鹿身后翠绿树林大面积严重脱色坍塌为灰冷死寂暗灰色(DeltaC=0.091)，清洗伪满分，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9825: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内网球场女运动员原本自然白皙的健康肤色在LCAD生成图中被严重过度偏色烘烤，泛出极其突兀不自然的荧光橙红亮色(DeltaC=0.056, Rsat=1.29)"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "身后深色广告挡板边缘产生轻微色溢"}
        ],
        "review_note": "Double Check复核改判：核查发现：网球女运动员肤色泛出突兀不自然荧光橙红偏色(DeltaC=0.056)，改判偏色(D-L1)与过饱和(E1-L1)。"
    },
    9839: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "复古火车站台下方悬挂的原本温暖醒目的金黄色TICKETS售票处指示牌在LCAD生成图中完全脱色褪白(Rsat=0.54, RedLoss=0.30)，退化为冰冷灰白死板标牌"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "站台钢构拱顶暖光照明与餐饮咖啡标牌略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：金黄售票处指示牌完全脱色褪白为灰白色死板标牌(Rsat=0.54)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9847: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "农家大树下停放的白色卡车上方原本晴朗湛蓝的蓝天在LCAD生成图中脱色泛白为苍白浅灰蓝(RedLoss=0.30)，大树生机翠绿略显退化"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "树冠背阴处枝叶略微泛冷发青"}
        ],
        "review_note": "Double Check复核改判：核查发现：晴朗蓝天脱色泛白为苍白浅灰蓝，大树树冠发青泛冷(RedLoss=0.30)，改判欠饱和(E2-L1)与偏色(D-L1)。"
    },
    9860: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "雪原疾驰雪地摩托骑手身上原本鲜艳醒目的大红色滑雪服与雪地车大红贴花在LCAD生成图中大面积严重脱色抹杀(RedLoss=0.71, Rsat=0.34)，完全蜕变为暗沉死黑灰"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "飞溅雪粉与远景黑夜雪道边缘略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：雪地摩托骑手大红滑雪服与红贴花严重脱色蜕变为死黑灰(RedLoss=0.71)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9864: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "客运火车卧铺包厢原本素雅中性的灰色包厢内饰在LCAD生成图中全景泛出极其突兀刺目的浓重深暗紫蓝偏色(Rsat=1.80)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "窗外明媚阳光照射的翠绿原野田地边缘微显色相发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：火车包厢内饰全景泛出突兀刺目的浓重深暗紫蓝偏色(Rsat=1.80)，改判偏色(D-L2)与错色(C-L1)。"
    },
    9877: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "卫浴空间原本温馨明亮的暖黄浅桃色墙面与木质洗手柜在LCAD生成图中被严重污染，泛出大片不自然的冷灰偏绿偏紫脏乱暗调(DeltaC=0.089, RedLoss=0.26)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "白色浴帘与马桶陶瓷立面反光略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：卫浴暖黄墙面被严重污染泛出冷灰偏绿偏紫脏乱暗调(DeltaC=0.089)，清洗伪满分，改判偏色(D-L2)与错色(C-L1)。"
    },
    9886: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "长椅上身穿白色西装男子内搭的原本极其清爽纯正的鲜艳湖蓝色衬衫在LCAD生成图中严重脱色褪淡(RedLoss=0.19)，退化为黯淡浅灰蓝"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "胸前金黄色领带与红色地砖略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：白西装男子鲜艳湖蓝衬衫严重脱色褪淡为黯淡浅灰蓝(RedLoss=0.19)，清洗伪满分，改判欠饱和(E2-L1)与错色(C-L1)。"
    },
    9892: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "停机坪草地上停放的小型螺旋桨客机机身原本极其醒目纯正的大红色贯穿式涂装拉花在LCAD生成图中被灾难性恶性错涂为深黑深青蓝色伪色，红色色相彻底颠覆篡改"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "机翼下方绿草地在LCAD生成图中大面积脱色泛黄泛灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：客机机身醒目大红涂装拉花被灾难性恶性错涂为深黑深青蓝伪色，改判错色(C-L2)与欠饱和(E2-L1)。"
    },
    9897: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "复古客厅墙面原本温暖雅致的金色条纹壁纸与暖木框在LCAD生成图中被严重污染侵蚀，全景大面积泛出突兀脏乱的青绿发冷死灰色偏色(DeltaC=0.096, RedLoss=0.75)"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "墙上悬挂的兽皮挂毯与印花单人扶手椅略显脱色"}
        ],
        "review_note": "Double Check复核改判：核查发现：客厅金色条纹壁纸大面积泛出突兀脏乱青绿发冷死灰偏色(DeltaC=0.096)，改判偏色(D-L2)与欠饱和(E2-L1)。"
    },
    9904: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "门廊合影兄弟身后原本生机古朴的暖红橙色红砖外立面在LCAD生成图中被大面积严重污染，完全泛出极其不自然脏乱的冷暗紫灰水泥色偏色(DeltaC=0.090, RedLoss=0.74)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "白色门框与花盆花卉边缘微显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：红砖外立面大面积严重污染泛出冷暗紫灰水泥色偏色(DeltaC=0.090)，改判偏色(D-L2)与错色(C-L1)。"
    },
    9905: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "雨中怀抱幼儿身上原本鲜艳醒目纯正的大红色短袖上衣在LCAD生成图中被恶性篡改错涂为发暗灰黄土棕褐色伪色，红色色相彻底颠覆篡改(DeltaC=0.067)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "撑伞成年男子手臂肤色与深色伞面略显泛暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：幼儿身上大红短袖被恶性错涂为发暗灰黄土棕褐伪色(DeltaC=0.067)，改判错色(C-L2)与偏色(D-L1)。"
    },
    9908: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "滑板碗池飞跃青年身后开阔草坪与远处大红小汽车在LCAD生成图中大面积脱色褪淡(RedLoss=0.89)，青年鞋面大红细节完全脱色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "水泥碗池立面光影与远处路灯略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：滑板青年身后草坪与大红汽车大面积脱色，鞋面红饰脱色(RedLoss=0.89)，改判欠饱和(E2-L1)与错色(C-L1)。"
    },
    9912: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "手捧甜甜圈女孩纸盒内原本五彩缤纷的彩虹糖粒装饰与纸帽上鲜艳大红品牌LOGO在LCAD生成图中大面积严重脱色发暗(RedLoss=0.40, DeltaC=0.071)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "身后原本温暖的室内墙面泛出暗沉泛绿杂色"}
        ],
        "review_note": "Double Check复核改判：核查发现：甜甜圈五彩糖粒与大红品牌LOGO严重脱色发暗，背景泛暗绿杂色(RedLoss=0.40)，清洗伪满分，改判欠饱和(E2-L2)与偏色(D-L1)。"
    },
    9913: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "石块建筑外墙边伫立的原本极其醒目纯正的大红色消防栓在LCAD生成图中被灾难性恶性篡改错涂为突兀鲜亮的翠绿色伪色，红绿严重混淆篡改(RedLoss=0.78, Rsat=1.70)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "石墙缝隙与废弃黑白电视机外壳略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：大红消防栓被灾难性恶性错涂为突兀翠绿色伪色(RedLoss=0.78, Rsat=1.70)，改判错色(C-L2)与偏色(D-L1)。"
    },
    9914: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "海浪中滑水选手脚下原本温润明亮的金色夕阳海面与青绿浪花在LCAD生成图中全景大面积严重脱色坍塌，整个水面退化为死寂黑白的暗灰死水(RedLoss=0.93, Rsat=0.32, DeltaC=0.082)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "天空暗部与浪花翻滚阴影处微显发暗泛冷"}
        ],
        "review_note": "Double Check复核改判：核查发现：夕阳海面金色波光与青绿浪花全景严重脱色坍塌为死寂黑白死水(RedLoss=0.93)，改判欠饱和(E2-L2)与偏色(D-L1)。"
    },
    9917: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "山坡公路俯冲滑板选手身上原本极其醒目鲜亮的大红色短裤在LCAD生成图中大面积严重脱色黑化(RedLoss=0.61, Rsat=0.62, DeltaC=0.075)，完全退化为暗沉深黑死灰裤"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "头盔上蓝色保护条与公路山坡泥土略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：俯冲滑板选手大红短裤大面积严重脱色黑化为深黑死灰色(RedLoss=0.61)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9927: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "岸边系留小船原本鲜艳的大红色饰条在LCAD生成图中脱色发暗，水面芦苇与对岸茂密树木生机翠绿色彩略显退化(RedLoss=0.25)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "水面波光倒影与小船木质船壳微显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：岸边小船大红饰条脱色发暗，水面芦苇与翠绿树冠略显退化(RedLoss=0.25)，清洗伪满分，改判欠饱和(E2-L1)与错色(C-L1)。"
    },
    9929: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "现代卫生间原本中性清爽的冷白灰瓷砖立面与洁具在LCAD生成图中被严重污染烘烤，全景大面积泛出突兀不自然的脏乱暖黄泛粉偏色(DeltaC=0.084, Rsat=1.51)"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "马桶座圈与水龙头金属反光边缘泛出暗红杂色"}
        ],
        "review_note": "Double Check复核改判：核查发现：现代卫生间冷白灰瓷砖立面全景泛出突兀脏乱暖黄泛粉偏色(DeltaC=0.084)，改判偏色(D-L2)与过饱和(E1-L1)。"
    },
    9930: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "夜雨雾霭街道路口原本具有清爽蓝冷雾霭反差与暖路灯对比的夜景在LCAD生成图中全景被恶性烘烤为极其单调刺目浓烈的全红橙焦化偏色(DeltaC=0.072)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "醒目STOP红牌反光与电线杆线缆细节完全失真"}
        ],
        "review_note": "Double Check复核改判：核查发现：夜雨雾霭街景被全景烘烤为极其单调刺目浓烈的红橙焦化偏色(DeltaC=0.072)，改判偏色(D-L2)与错色(C-L1)。"
    },
    9949: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "港湾船坞左下角停靠的机动船原本极其鲜亮夺目的大红色船壳与设备在LCAD生成图中完全脱色黑化(RedLoss=0.64)，彻底蜕变为沉闷死灰深黑铁壳"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "码头停泊游艇桅杆与远处都市天际线微显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：船坞大红机动船船壳完全脱色黑化为沉闷死灰深黑铁壳(RedLoss=0.64)，清洗伪满分，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9950: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "多屏幕电脑书房原本温馨自然的实木橱柜与暖光照明在LCAD生成图中被大面积严重污染，整个工作台与屏幕泛出突兀刺目的浓重深暗紫蓝偏色(DeltaC=0.075, RedLoss=0.48)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "实木地板与左侧电视柜阴影过度发暗焦化"}
        ],
        "review_note": "Double Check复核改判：核查发现：电脑书房全室被大面积污染泛出突兀刺目的浓重深暗紫蓝偏色(DeltaC=0.075)，清洗伪满分，改判偏色(D-L2)与错色(C-L1)。"
    },
    9973: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "走廊左侧卧室房门内隐约可见的原本鲜艳明亮的大红色健身球与运动装备在LCAD生成图中大面积脱色黑化(RedLoss=0.50, Rsat=0.65)，退化为深黑灰暗"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "走廊暖白墙壁与右侧洗手间照明光泽微显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：卧室门内大红健身球与装备大面积脱色黑化为深黑灰暗(RedLoss=0.50)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9981: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "池中北极熊玩耍的原本极其清亮纯正的鲜艳半透明天蓝色塑料半球罩在LCAD生成图中脱色发暗，退化为深暗沉闷深蓝灰(DeltaC=0.038)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "北极熊头部洁白毛发在LCAD生成图中略微泛黄"}
        ],
        "review_note": "Double Check复核改判：核查发现：北极熊天蓝塑料球脱色发暗退化为深暗蓝灰，熊毛微显泛黄，清洗伪满分，改判欠饱和(E2-L1)与偏色(D-L1)。"
    },
    9982: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "风暴大浪海面上空远方原本极其醒目的一抹鲜艳大红色冲浪风筝在LCAD生成图中被完全剥夺抹杀(RedLoss=0.99, Rsat=0.36)，整个惊涛骇浪场景退化为单调冷灰黑白"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "乌云暗部与海水翻滚浪花细节略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：海面远方鲜艳大红冲浪风筝完全剥夺抹杀，海面退化为冷灰黑白(RedLoss=0.99)，改判欠饱和(E2-L2)与偏色(D-L1)。"
    },
    9995: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "室内客厅地面原本清爽素净的浅米白色地毯与拉杆箱在LCAD生成图中被全屋严重烘烤偏色，泛出突兀不自然的脏乱暗黄偏红混浊色调(DeltaC=0.080, Rsat=1.35)"},
            {"id": "E1", "name": "过饱和", "severity": "L1", "description": "虎斑猫背部条纹与电视柜深色漆面过度焦化"}
        ],
        "review_note": "Double Check复核改判：核查发现：客厅米白地毯与拉杆箱全屋泛出突兀脏乱暗黄偏红混浊偏色(DeltaC=0.080)，改判偏色(D-L2)与过饱和(E1-L1)。"
    },
    9997: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "现代卫生间毛巾架上原本生机清爽的嫩绿色毛巾与洗手池边天蓝色洗发水瓶在LCAD生成图中严重脱色褪淡(RedLoss=0.22, Rsat=0.54)，蜕变为暗淡无色灰白"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "瓷砖墙面与热水器金属外壳微显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：毛巾架嫩绿毛巾与天蓝洗发水瓶严重脱色褪淡为暗淡灰白(Rsat=0.54)，改判欠饱和(E2-L1)与错色(C-L1)。"
    },
    9998: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "现代挤奶厅栏位中奶牛身上原本饱满温润的金黄浅褐色皮毛在LCAD生成图中大面积严重脱色发暗(RedLoss=0.59, Rsat=0.53)，退化为冰冷灰暗死黑调，窗外蓝天亦脱色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "金属挤奶架与地面橡胶垫略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：奶牛饱满金黄浅褐皮毛大面积脱色发暗为冰冷灰暗死黑(RedLoss=0.59)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9999: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "热带沙滩近景停泊的原本具有温润哑光薄荷浅绿质感的皮划艇在LCAD生成图中被恶性错涂为极其刺目惊悚的高饱和荧光翠绿塑料伪色，沙滩游客绿色泳裤错涂为刺眼青蓝，海滩遮阳伞严重偏绿失色"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "沙滩细腻白沙在LCAD生成图中略微发灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：皮划艇被恶性错涂为刺目高饱和荧光翠绿塑料伪色，泳裤错涂青蓝(DeltaC=0.041)，改判错色(C-L2)与偏色(D-L1)。"
    },
    10000: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "合力顶起水桶的左侧年轻女子身上原本极其鲜艳明快的大红黑条纹短袖在LCAD生成图中大面积严重脱色褪淡(RedLoss=0.18)，完全蜕变为暗淡无色的浅灰暗粉残色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "绿色塑料水桶与长袍深黄褐色织物边缘略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：压轴第10000条任务左侧女子大红黑条纹短袖严重脱色蜕变为暗淡无色浅灰暗粉(RedLoss=0.18)，改判欠饱和(E2-L2)与错色(C-L1)。"
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
    stream_path = STREAMS_DIR / "tasks_lcad_9501_10000_stream.json"
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
    print(f"Applying Double Check updates for 9501-10000 ({len(DC_CORRECTIONS)} tasks)...")
    
    # 1. Update batch 9501-10000
    b_path = EXPORTS_DIR / "reviewed_9501_10000_20260930_194247.json"
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

    print("Double check updates for 9501-10000 completed successfully!")

if __name__ == "__main__":
    main()
