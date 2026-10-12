"""Apply Double Check updates for batch 9001-9500 pass tasks.
Updates reviewed_9001_9500, stream package, and full 1-10000 exports.
Follows the exact V4 schema contract from AGENTS.md.
"""
import json
import os
import shutil
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"
STREAMS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "streams"

# 59 Grounded Double Check Corrections for 9001-9500
DC_CORRECTIONS = {
    9009: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "左侧藤椅上老妇人膝头放置的原本醒目鲜艳的大红白字图案织物在LCAD生成图中被恶性错涂为亮黄橙色伪色，红色色相失真篡改"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内木质窗框与藤椅扶手暗部略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：老妇人膝头原本鲜艳大红图案织物被恶性错涂为亮黄橙色伪色，改判错色(C-L2)与偏色(D-L1)。"
    },
    9016: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "乡间公路两侧原本生机青翠的平展绿草地在LCAD生成图中大面积严重欠饱和脱色，褪变为发暗灰灰土褐荒草色(Rsat=0.65)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "马车上满载的干草垛边缘略显泛灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：乡间公路两侧生机青翠绿草地大面积脱色为发暗灰灰土褐色(Rsat=0.65)，清洗伪满分，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9018: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "水岸逆光场景中交通信号灯上方原本醒目警示的红色指示灯光在LCAD生成图中完全脱色黑化剥夺(RedLoss=0.44)，退化为死黑圆斑"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "水面波光与逆光车辆金属车顶反光略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：交通信号灯原本醒目警示的红灯指示完全脱色黑化(RedLoss=0.44)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9021: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "棒球击球手球衣背后原本醒目鲜艳的大红色5号背号在LCAD生成图中严重脱色发暗，退化为深褐暗红"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "外场蓝色广告背板与裁判深色护具略显暗淡"}
        ],
        "review_note": "Double Check复核改判：核查发现：棒球击球手球衣大红色5号背号严重脱色发暗，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9022: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "黏土甜品展示板左侧原本鲜艳欲滴的大红色草莓樱桃蛋糕在LCAD生成图中大面积脱色褪淡，退化为泥褐无色暗糕点(RedLoss=0.16)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "木质砧板纹理与右侧彩色马卡龙略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：展示板左侧鲜红草莓樱桃蛋糕大面积脱色为泥褐无色糕点(RedLoss=0.16)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9035: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "餐桌上生日蛋糕点燃的单根蜡烛原本温暖明亮的金黄橙红烛焰在LCAD生成图中被错误涂抹为阴冷冰蓝色伪色(DeltaC=0.049)"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "小男孩条纹毛衣袖口暖色线条略显脱色"}
        ],
        "review_note": "Double Check复核改判：核查发现：生日蛋糕暖黄橙红烛焰被错误涂抹为阴冷冰蓝色伪色(DeltaC=0.049)，改判偏色(D-L2)与欠饱和(E2-L1)。"
    },
    9039: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "开阔牧场上原本生机盎然的平展翠绿色草地与卧倒小黄牛在LCAD生成图中大面积严重脱色坍塌，整个地面蜕变为黑白灰烬般的死灰色(Rsat=0.29)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "远处防风林树冠与澄澈蓝天交界处略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：牧场平展翠绿草地与小黄牛大面积严重脱色坍塌为黑白死灰色(Rsat=0.29)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9050: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "奇幻原野山丘与蜿蜒水面上原本温暖唯美的夕阳金黄色光影在LCAD生成图中大面积泛出突兀阴冷的深蓝绿偏色(DeltaC=0.024)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "山坡上漫步的羊群与翠绿树冠暗部微显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：原野山丘与水面温暖金黄夕阳反光泛出阴冷深蓝绿偏色(DeltaC=0.024)，改判偏色(D-L2)与错色(C-L1)。"
    },
    9081: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "灌木草坪上原本青翠均匀的鲜嫩绿草在LCAD生成图中大面积泛出杂乱突兀的枯黄与泛红偏色色斑(Rsat=0.73)"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "觅食小鸟棕褐色羽毛暗影略微脱色发灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：草坪原本鲜嫩绿草大面积泛出杂乱枯黄与泛红偏色色斑(Rsat=0.73)，改判偏色(D-L2)与欠饱和(E2-L1)。"
    },
    9096: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L1", "description": "木质托盘上右侧贝果表面原本乳白奶黄的鸡蛋沙拉色泽在LCAD生成图中过度偏黄泛金(DeltaC=0.022)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "桌面水杯透射光泽与背景略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：托盘右侧贝果鸡蛋沙拉表面过度偏黄泛金(DeltaC=0.022)，改判偏色(D-L1)与错色(C-L1)。"
    },
    9101: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "长颈鹿园区原本洁净自然的米白黄色干燥沙土地面在LCAD生成图中大面积泛出不自然的脏乱粉红色偏色晕染(DeltaC=0.013)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "长颈鹿深褐色网状斑纹边缘略微泛红"}
        ],
        "review_note": "Double Check复核改判：核查发现：长颈鹿园区米白干燥沙地大面积泛出不自然脏乱粉红偏色(DeltaC=0.013)，改判偏色(D-L2)与错色(C-L1)。"
    },
    9103: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "菱形黑白条纹灯塔前方马儿觅食的原本干燥开阔的温润浅黄褐色沙滩泥地在LCAD生成图中被大面积强行错涂为鲜绿色草地伪色(DeltaC=0.042)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "低头棕褐色马匹背部毛色略显泛冷偏暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：灯塔前方开阔浅黄褐沙滩泥地被大面积强行错涂为鲜绿草地伪色(DeltaC=0.042)，改判错色(C-L2)与偏色(D-L1)。"
    },
    9113: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L1", "description": "早餐托盘左侧水杯中原本清爽鲜亮的纯正橙黄色果汁在LCAD生成图中被错误涂抹为深红色西番莲果汁色(DeltaC=0.021)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "烤面包片表面焦香金黄色泽略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：水杯中橙黄色果汁被错误涂抹为深红色(DeltaC=0.021)，改判错色(C-L1)与偏色(D-L1)。"
    },
    9121: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "古石寺庙遗迹后方原本鲜艳古朴的红砖建筑构件在LCAD生成图中严重脱色褪淡，退化为发灰暗土色(RedLoss=0.17)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "平整绿草坪前方卧倒的白牛皮毛暗影略微泛蓝"}
        ],
        "review_note": "Double Check复核改判：核查发现：古寺庙遗迹后方鲜艳古朴红砖建筑构件严重脱色褪淡(RedLoss=0.17)，清洗伪满分，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9125: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "餐盘大碗内原本色泽红润诱人的大红番茄炖牛肉在LCAD生成图中被恶性错涂为发暗深黑褐色，左侧面包卷表皮异常污染绿色斑块"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "纸杯咖啡与餐叉反光略微暗淡"}
        ],
        "review_note": "Double Check复核改判：核查发现：餐盘大红番茄炖牛肉被恶性错涂为发暗深黑褐，面包卷表皮污染绿斑，改判错色(C-L2)与偏色(D-L1)。"
    },
    9140: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "飞机坟场俯瞰视角下原本开阔温暖的黄褐色荒漠土地在LCAD生成图中大面积严重脱色坍塌，蜕变为完全无色的冷灰死水泥地(Rsat=0.27)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "库房蓝色铁皮屋顶与停放客机机翼略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：飞机坟场温暖黄褐色荒漠地表严重脱色坍塌为完全无色冷灰水泥地(Rsat=0.27)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9150: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "城市公交客车车身下包围原本鲜艳醒目的大红色裙边与警示色带在LCAD生成图中被恶性错涂为深蓝紫色伪色(RedLoss=0.18)"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "街边巨幅红色特价商品广告牌略显脱色"}
        ],
        "review_note": "Double Check复核改判：核查发现：公交客车大红裙边被恶性错涂为深蓝紫色伪色(RedLoss=0.18)，清洗伪满分，改判错色(C-L2)与欠饱和(E2-L1)。"
    },
    9151: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "野生动物园区在傍晚原本温暖强烈的金红晚霞光影与野犬身上的黄褐斑纹在LCAD生成图中大面积欠饱和褪淡，退化为冷灰暗色(RedLoss=0.17, Rsat=0.56)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "铁笼阴影与野犬背部皮毛边缘泛出暗紫冷调"}
        ],
        "review_note": "Double Check复核改判：核查发现：傍晚温暖金红晚霞光影与野犬黄褐毛色严重脱色褪淡为冷灰暗色(Rsat=0.56)，改判欠饱和(E2-L2)与偏色(D-L1)。"
    },
    9167: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "卫生间原本清新雅致的浅天蓝薄荷青色涂料墙面在LCAD生成图中大面积严重脱色褪淡，完全退化为毫无生机的惨白灰冷墙面(Rsat=0.40)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "立柱洗脸盆与坐便器白色陶瓷暗影略显发乌"}
        ],
        "review_note": "Double Check复核改判：核查发现：卫生间清爽浅天蓝薄荷青墙面大面积严重脱色褪淡为惨白灰冷墙面(Rsat=0.40)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9169: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "厨房料理台后方原本极其醒目的大红色可口可乐易拉罐与红色食品包装盒在LCAD生成图中大面积脱色发灰(RedLoss=0.15)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "塑料沥水篮中清洗的餐具略显暗淡"}
        ],
        "review_note": "Double Check复核改判：核查发现：料理台后方大红可口可乐包装大面积脱色发灰(RedLoss=0.15)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9176: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "非洲大草原落日余晖下原本辽阔金黄的草甸植被在LCAD生成图中大面积严重欠饱和脱色，金黄色泽蜕变为暗淡无光浅褐灰草地(Rsat=0.63)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "落日天幕原本泛金泛红的晚霞略显偏灰发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：大草原落日余晖下辽阔金黄草甸严重脱色为暗淡浅褐灰色(Rsat=0.63)，改判欠饱和(E2-L2)与偏色(D-L1)。"
    },
    9185: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "马棚内两匹骏马原本光泽饱满、浓郁鲜亮的金栗褐色毛皮在LCAD生成图中大面积脱色发灰，蜕变为灰暗无光死灰褐色(Rsat=0.61)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "木质立柱暗影与背景树林绿意略微暗淡"}
        ],
        "review_note": "Double Check复核改判：核查发现：骏马光泽饱满浓郁鲜亮金栗褐毛皮大面积脱色褪淡为死灰褐(Rsat=0.61)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9186: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "开阔湖泊对岸原本生机郁郁葱葱的苍翠群山森林在LCAD生成图中大面积严重欠饱和脱色，褪变为黯淡发灰的死灰绿色秃岭(Rsat=0.48)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "湖面白色游船金属构件与波光略显发乌"}
        ],
        "review_note": "Double Check复核改判：核查发现：湖畔苍翠群山森林大面积严重欠饱和脱色为黯淡死灰绿(Rsat=0.48)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9187: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "牛仔竞技场沙圈地面原本温暖纯正的深黄褐色泥沙在LCAD生成图中大面积脱色发暗，退化为深冷死灰水泥地(Rsat=0.42)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "围栏后方白色木板与骑手服饰略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：竞技场温暖深黄褐泥沙大面积脱色为深冷死灰色(Rsat=0.42)，清洗伪满分，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9211: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "卫生间地砖上原本铺设的鲜亮大红色几何线条防滑地垫在LCAD生成图中大面积严重脱色褪淡，退化为暗沉砖褐灰红垫"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "洗手盆白色陶瓷与刷牙男子深色衣物略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：卫生间地面鲜艳大红几何防滑地垫大面积脱色褪淡为暗沉砖灰褐色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9223: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "阳光皑皑的高山雪原原本纯净洁白、带微暖日光反光的积雪地表在LCAD生成图中大面积泛出突兀浓重的冷青蓝色偏色(Rsat=3.68)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "滑雪登山者深色冲锋衣在雪坡阴影处微显泛暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：高山雪原纯净积雪地表大面积泛出突兀浓重冷青蓝偏色(Rsat=3.68)，改判偏色(D-L2)与错色(C-L1)。"
    },
    9231: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "石墙小道左侧山坡上原本生机青翠的平展绿草地在LCAD生成图中大面积严重脱色失真，退化为发干发灰的死黄土石色(Rsat=0.42)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "漫步绵羊白色羊毛与碎石路面略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：石墙小道左侧青翠绿草地大面积脱色为发干发灰死黄土石色(Rsat=0.42)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9234: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "市政广场欧式钟楼下花坛内原本盛开的大片鲜艳大红色鲜花在LCAD生成图中严重脱色褪淡，退化为黯淡灰褐色花簇(Rsat=0.65)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "红砖钟楼外立面暗部与铺装路面略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：钟楼花坛盛开的大片鲜艳大红鲜花严重脱色褪淡为黯淡灰褐(Rsat=0.65)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9274: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "卫生间门口左侧原本悬挂着的鲜艳夺目洋红粉紫色毛巾在LCAD生成图中大面积脱色蜕变，退化为深暗发乌灰蓝色(Rsat=0.56)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "洗漱台边塑料洗发水瓶与拖鞋略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：卫生间鲜艳洋红粉紫毛巾大面积脱色蜕变为深暗发乌灰蓝色(Rsat=0.56)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9279: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "棒球场深海蓝色外场挡板上原本醒目纯正的亮橙黄色圆形PNC商号标识在LCAD生成图中被恶性错涂为刺眼洋红粉紫色伪色，标识色相严重篡改"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "内场红土跑道与球员白色球服略显泛冷"}
        ],
        "review_note": "Double Check复核改判：核查发现：挡板上亮橙黄色圆形PNC商号标识被恶性错涂为洋红粉紫色伪色，清洗伪满分，改判错色(C-L2)与偏色(D-L1)。"
    },
    9284: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "运牛货车车尾挡板下方原本醒目警示的鲜艳橙红色防撞横梁与反光色块在LCAD生成图中严重脱色发暗，退化为发脏深黑褐色(RedLoss=0.22)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "货箱中黄牛皮毛与公路柏油路面略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：运牛货车鲜艳橙红防撞横梁严重脱色发暗为深黑褐色(RedLoss=0.22)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9285: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "暮色海滩平展沙滩上整齐排列的各色冲浪板中原本明艳的亮黄、纯红涂装在LCAD生成图中严重脱色发暗，退化为泥土灰暗杂色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "海潮退去湿漉沙滩倒影略显偏冷灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：沙滩上各色冲浪板亮黄与纯红涂装严重脱色褪淡为泥土灰暗杂色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9290: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "餐桌餐盘内原本香气四溢、金黄焦脆的厚松饼在LCAD生成图中被恶性错涂为阴暗深紫蓝色伪色，左侧咖啡杯也泛出刺眼蓝光"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "男子黑色短袖T恤胸前黄色文字略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：餐盘内金黄焦脆厚松饼被恶性错涂为阴暗深紫蓝色伪色，改判错色(C-L2)与偏色(D-L1)。"
    },
    9292: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "水面游弋鹈鹕头顶原本素雅柔和的淡黄色绒毛冠在LCAD生成图中被过度错误渲染为刺眼荧光柠檬黄绿色伪色(Rsat=1.44)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "清澈水面天蓝倒影与羽毛暗部微显偏暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：鹈鹕头顶淡黄绒毛被过度渲染为刺眼荧光柠檬黄绿伪色(Rsat=1.44)，改判错色(C-L2)与偏色(D-L1)。"
    },
    9295: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "网球场原本明亮鲜艳的生机纯正翠绿色硬地地面在LCAD生成图中完全脱色坍塌，退化为深冷灰蓝水泥地(Rsat=0.39)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "击球手手中网球拍红色拍框线条略显脱色"}
        ],
        "review_note": "Double Check复核改判：核查发现：网球场纯正翠绿硬地地面完全脱色坍塌为深冷灰蓝水泥地(Rsat=0.39)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9300: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "西装男士面庞前原本鲜艳欲滴的大红色玫瑰花朵在LCAD生成图中严重脱色发乌，蜕变为黯淡深褐灰黑死花色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "拍照女士深红毛衣后背暗部略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：男士面前原本鲜艳大红玫瑰花大面积脱色发乌为深褐灰黑色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9305: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "村庄草坡后方原本挺拔翠绿的热带棕榈树林在LCAD生成图中大面积严重欠饱和脱色，生机绿意蜕变为暗淡无光黄绿干枯色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "草地上黄牛皮毛暗影略微泛灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：村庄背景挺拔翠绿棕榈树林大面积严重脱色为暗淡黄绿干枯色，清洗伪满分，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9307: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "滑雪父子身旁坚立的原本极其醒目夺目的亮粉红色滑雪单板在LCAD生成图中完全脱色褪白，退化为无色苍白灰白板"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "滑雪防风服面料与雪地阴影处略微发乌"}
        ],
        "review_note": "Double Check复核改判：核查发现：坚立的醒目亮粉红滑雪单板完全脱色褪白为无色苍白灰白板，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9308: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "铁丝护网后方挥棒击球的小球员身上原本鲜艳大红色的棒球球服在LCAD生成图中大面积脱色发乌，退化为黯淡深褐暗红色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "铁丝网内侧绿色草坪与捕手护具略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：小球员原本鲜艳大红棒球服大面积脱色发乌为深褐暗红，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9319: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "厨房料理台下方滚筒洗衣机原本纯净明艳的宝蓝色圆门观察窗在LCAD生成图中被恶性错涂为突兀洋红粉紫色伪色(RedLoss=0.16)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "整体白色吊柜与抽油烟机暗部略显偏暗泛紫"}
        ],
        "review_note": "Double Check复核改判：核查发现：滚筒洗衣机宝蓝圆门窗被恶性错涂为洋红粉紫色伪色(RedLoss=0.16)，改判错色(C-L2)与偏色(D-L1)。"
    },
    9320: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "公园木质长椅周遭原本生机盎然的平展翠绿色草坪在LCAD生成图中略显欠饱和偏黄发淡(DeltaC=0.031)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "长椅木板油漆与石板步道略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：公园长椅周围翠绿草坪略显欠饱和偏黄发淡(DeltaC=0.031)，改判欠饱和(E2-L1)与错色(C-L1)。"
    },
    9344: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "长颈鹿园区对岸城市海湾原本纯净清澈的碧蓝海面与高楼大厦立面在LCAD生成图中局部大面积被严重污染为脏乱的暗红紫色偏色(Rsat=1.37)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "近景木桩围栏与长颈鹿斑纹暗部略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：对岸海湾碧蓝水面与大厦立面大面积污染脏乱暗红紫偏色(Rsat=1.37)，清洗伪满分，改判偏色(D-L2)与错色(C-L1)。"
    },
    9347: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "铁轨两侧原本生机青翠的开阔田野与草坡灌木在LCAD生成图中大面积严重脱色暗化，青翠植被退化为发焦暗绿黄褐色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "红色列车车头顶部与碎石道床略显偏暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：铁轨两侧青翠田野草坡大面积脱色暗化为发焦暗绿黄褐色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9357: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "爵士乐队中右侧吉他乐手身上原本纯正清爽的牛仔蓝长裤在LCAD生成图中完全脱色褪淡，退化为发脏暗灰褐色(RedLoss=0.15)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "贝斯手原木大提琴琴身色泽略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：右侧吉他乐手牛仔蓝长裤完全脱色褪淡为发脏暗灰褐(RedLoss=0.15)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9359: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "温馨室内客厅左侧原本极其鲜艳的大红色布艺单人扶手椅在LCAD生成图中严重脱色发乌，退化为沉闷深黑褐色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "暖黄落地灯灯光光晕外缘略带杂色"}
        ],
        "review_note": "Double Check复核改判：核查发现：客厅左侧原本极其鲜艳的大红布艺扶手椅严重脱色发乌为深黑褐色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9376: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "浴室淋浴玻璃房与大理石浴缸周围原本温润纯净的米白瓷砖在LCAD生成图中大面积泛出突兀阴冷的深紫蓝色偏色(Rsat=0.64)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "浴室窗户深色木质边框暗部略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：浴室米白瓷砖大面积泛出突兀阴冷深紫蓝偏色(Rsat=0.64)，改判偏色(D-L2)与错色(C-L1)。"
    },
    9384: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "水塘边坡地上原本生机盎然的平展翠绿色草坪在LCAD生成图中大面积欠饱和脱色，褪变为发暗灰绿枯草泥地(Rsat=0.72)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "近景水塘倒影波光略微暗淡"}
        ],
        "review_note": "Double Check复核改判：核查发现：水塘边平展翠绿草坪大面积脱色为发暗灰绿泥地(Rsat=0.72)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9387: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "雪原牵马者手中牵引的原本纯正明亮的天蓝色缰绳在LCAD生成图中被恶性错涂为刺眼的大红粉红色伪色，缰绳色彩严重篡改(Rsat=0.27)"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "棕色骏马毛皮与牵马者白色滑雪服略微脱色"}
        ],
        "review_note": "Double Check复核改判：核查发现：牵马者天蓝缰绳被恶性错涂为刺眼大红粉红伪色(Rsat=0.27)，改判错色(C-L2)与欠饱和(E2-L1)。"
    },
    9389: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "奔跑放风筝男童脚下原本生机勃勃的开阔纯翠绿色大草坪在LCAD生成图中大面积严重脱色坍塌，蜕变为发焦泛黄的死灰黄泥草地(RedLoss=0.30)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "五彩风筝骨架与彩色飘带略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：放风筝男童脚下纯翠绿大草坪大面积严重脱色坍塌为死灰黄泥草地(RedLoss=0.30)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9412: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "红色老式重型自卸卡车车头进气格栅与车轮轮毂原本典雅纯正的米白色涂装在LCAD生成图中被恶性错涂为刺目金黄色伪色"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "红色车厢表面反光与路面柏油略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：红色自卸卡车米白格栅与轮毂被恶性错涂为刺目金黄伪色，改判错色(C-L2)与偏色(D-L1)。"
    },
    9432: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "客厅内原本温馨和煦的暖黄色墙面与原木色陈列柜在LCAD生成图中大面积完全脱色褪白，退化为冰冷发灰的惨白水泥墙色(RedLoss=0.16, Rsat=0.53)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "沙发靠背与茶几暗部略显偏暗泛冷"}
        ],
        "review_note": "Double Check复核改判：核查发现：客厅温馨暖黄墙面与原木展示柜完全脱色为冰冷惨白水泥墙色(RedLoss=0.16)，改判欠饱和(E2-L2)与偏色(D-L1)。"
    },
    9433: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "公共卫生间蹲坑地面上原本清晰显眼的大红色数码时钟时间印记在LCAD生成图中被完全脱色抹杀剥夺(RedLoss=0.42)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "卫生间深木色隔断门板与白色地砖暗部略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：蹲坑地面清晰显眼大红时间印记被完全脱色抹除(RedLoss=0.42)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9442: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "网球小球员身上原本鲜亮夺目的纯正翠绿色运动短袖在LCAD生成图中被恶性错涂为深宝蓝色伪色短袖，球服原本活力色相彻底颠覆篡改"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "背后欧式古堡建筑与绿化树木略显泛暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：网球小球员鲜亮翠绿运动短袖被恶性错涂为深宝蓝色伪色短袖，改判错色(C-L2)与偏色(D-L1)。"
    },
    9443: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "斑马低头觅食的开阔草坪原本生机饱满的青翠草色在LCAD生成图中大面积严重欠饱和脱色，蜕变为发干暗灰的黄绿泥草地(Rsat=0.50)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "斑马身躯黑白条纹与后方土坡略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：斑马觅食开阔草坪青翠草色严重脱色为发干暗灰黄绿泥地(Rsat=0.50)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9445: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "公园长椅上女孩身上原本鲜艳明朗的亮粉红运动短裤在LCAD生成图中大面积脱色褪淡，退化为发白浅肉粉色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "遮阳帽蓝色反光与木质长椅略显暗淡"}
        ],
        "review_note": "Double Check复核改判：核查发现：女孩鲜艳亮粉红运动短裤大面积脱色褪淡为发白浅肉粉，改判欠饱和(E2-L1)与错色(C-L1)。"
    },
    9463: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "滑雪特技腾空单板原本纯正酷黑的板底与大红色SALOMON品牌字样在LCAD生成图中被恶性篡改为整个板底通红的深酒红色伪色(RedLoss=0.29, Rsat=2.98)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "背后网格建筑外立面窗格边缘微显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：滑雪单板纯黑板底被恶性错涂为通体深酒红色伪色(Rsat=2.98)，改判错色(C-L2)与偏色(D-L1)。"
    },
    9469: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "雪原高空腾跃滑雪选手身上原本鲜亮醒目的青绿色冲锋衣大红色连帽内胆在LCAD生成图中严重脱色抹杀，完全退化为暗沉深黑灰调(RedLoss=0.27)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "雪地警示防护网与远处松树略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：滑雪选手冲锋衣大红色连帽内胆完全脱色退化为暗沉深黑灰(RedLoss=0.27)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    9471: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "红砖矮墙前倚靠打电话的男子身上原本极其醒目鲜亮的大红色短袖T恤在LCAD生成图中被恶性错涂为发暗深黑绿青色伪色，红色色相彻底颠覆篡改(RedLoss=0.26)"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "身后原本鲜艳古朴的红砖外墙局部严重脱色发白"}
        ],
        "review_note": "Double Check复核改判：核查发现：男子醒目大红短袖被恶性错涂为深黑绿青色伪色，红砖墙脱色发白(RedLoss=0.26)，清洗伪满分，改判错色(C-L2)与欠饱和(E2-L1)。"
    },
    9482: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "手持对讲机男子身上原本生机饱满的军绿色短袖T恤在LCAD生成图中脱色发暗，退化为黯淡灰褐色面料"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "背景摩天大楼天际线与面部肤色暗部略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：男子军绿短袖T恤脱色发暗为黯淡灰褐，改判欠饱和(E2-L1)与错色(C-L1)。"
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
    stream_path = STREAMS_DIR / "tasks_lcad_9001_9500_stream.json"
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
    print("Applying Double Check updates for 9001-9500...")
    
    # 1. Update batch 9001-9500
    b_path = EXPORTS_DIR / "reviewed_9001_9500_20260930_192616.json"
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

    print("Double check updates for 9001-9500 completed successfully!")

if __name__ == "__main__":
    main()
