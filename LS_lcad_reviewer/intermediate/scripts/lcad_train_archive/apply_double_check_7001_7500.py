"""Apply Double Check updates for batch 7001-7500 pass tasks.
Updates reviewed_7001_7500, stream package, and full 1-10000 exports.
Follows the exact V4 schema contract from AGENTS.md.
"""
import json
import os
import shutil
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"
STREAMS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "streams"

# 37 Grounded Double Check Corrections for 7001-7500
DC_CORRECTIONS = {
    7003: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "拥堵十字路口中大批原本鲜艳夺目的洋红粉紫出租车、鲜红出租车与明黄公交车在LCAD生成图中大面积脱色蜕变，退化为无色黑灰色车流(RedLoss=0.25, Rsat=0.30)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "斑马线两侧树木与路面阴影轻微泛暗偏冷"}
        ],
        "review_note": "Double Check复核改判：核查发现：拥堵十字路口中大批鲜艳洋红大红明黄色出租车与公交车完全脱色退化为黑灰车流(RedLoss=0.25, Rsat=0.30)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7012: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "高档卫生间镜子内置屏幕上播放的高清火红金色晚霞雪山壁纸在LCAD生成图中被恶性错涂为阴暗冷蓝灰色天幕，晚霞暖色完全被冷灰颠覆(RedLoss=0.27)"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "毛巾架旁天蓝色防尘袋与红色洗漱瓶脱色发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：镜子屏幕内显示的高清火红金色晚霞壁纸被恶性错涂为阴冷灰蓝天幕，洗漱品脱色(RedLoss=0.27)，改判错色(C-L2)与欠饱和(E2-L1)。"
    },
    7017: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "建筑外立面原本清爽干净的冷灰白色石砌砖墙在LCAD生成图中被严重烘烤发黄，恶性偏暖错涂为暖黄土褐色砖墙(Rsat=2.42)，室内外色温严重失衡"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "地面暗影与右侧垃圾桶略带泛深褐色"}
        ],
        "review_note": "Double Check复核改判：核查发现：建筑外立面原本清爽冷灰白石墙被严重烘烤恶性偏暖黄土褐色(Rsat=2.42)，改判偏色(D-L2)与错色(C-L1)。"
    },
    7022: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "沙滩上两把原本极其鲜艳夺目的亮粉红色遮阳伞在LCAD生成图中严重脱色褪淡，退化为暗沉发黄的浅土黄与米黄色普通伞(RedLoss=0.16)，鲜艳粉红彻底丧失"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "沙滩躺椅上晒太阳的女子肤色略显发乌"}
        ],
        "review_note": "Double Check复核改判：核查发现：沙滩上两把原本极其鲜艳的亮粉红色遮阳伞严重脱色褪变为浅土黄米黄色(RedLoss=0.16)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7044: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "单板滑雪运动员脚下踩着的单板滑雪板与滑雪裤原本为鲜艳纯正的明黄色，在LCAD生成图中完全脱色错涂为深蓝色与暗黑灰色(RedLoss=0.18, Rsat=0.58)，黄色色相完全丧失"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "雪地受背光阴影影响整体泛冷发灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：滑雪选手单板滑雪板与滑雪裤原本鲜艳明黄色完全脱色错涂为深蓝黑灰色(RedLoss=0.18)，改判错色(C-L2)与偏色(D-L1)。"
    },
    7050: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "街头巨大铜马雕像旁老先生身上原本身穿的军绿色工装长袖衬衫在LCAD生成图中被恶性错涂为刺眼醒目的大红色上衣(Rsat=1.44)，衣服色相发生颠覆性错变"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "身旁老太太白色短袖与周围建筑外立面整体恶性偏暖偏黄"}
        ],
        "review_note": "Double Check复核改判：核查发现：老先生身穿的原本军绿色工装长袖衬衫被恶性错涂为刺眼大红色(Rsat=1.44)，老太太衣物泛黄，改判错色(C-L2)与偏色(D-L1)。"
    },
    7066: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "雨天过街斑马线上行人手中撑着的大量原本极其鲜艳的大红、明黄、粉紫色彩色雨伞在LCAD生成图中完全脱色蜕变，退化为暗黑灰色的无色伞顶(RedLoss=0.20, Rsat=0.61)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "沥青斑马线路面湿水反光处发暗偏青"}
        ],
        "review_note": "Double Check复核改判：核查发现：雨天过街行人手中撑着的大量鲜艳大红、明黄、粉紫彩色雨伞完全脱色蜕变暗黑灰色(RedLoss=0.20)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7090: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "复古暗光房间内男子身上原本浅灰褐色的长袖衬衫在LCAD生成图中被恶性错涂为极其刺眼醒目的高饱和荧光草绿色衬衫(Rsat=1.48)，色相严重失真错涂"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "男子头发与面部阴影泛红棕色偏色"}
        ],
        "review_note": "Double Check复核改判：核查发现：男子身穿的原本浅灰褐色衬衫被恶性错涂为刺眼醒目的高饱和荧光草绿色伪色(Rsat=1.48)，改判错色(C-L2)与偏色(D-L1)。"
    },
    7104: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "长颈鹿栖息的原野草坪原本平整开阔生机翠绿，在LCAD生成图中严重欠饱和脱色发暗，退化为发灰发黄的枯干杂草地(Rsat=0.56, DeltaC=0.052)，背景大树树冠也发乌变暗褐"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "长颈鹿身上的棕黄色斑纹边缘发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：长颈鹿栖息的茂密草坪与背景大树严重欠饱和脱色，退化为枯黄发暗杂草地(Rsat=0.56)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7106: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "卫生间门边右侧原本挂着的极其鲜艳纯正的大红洋红色浴巾在LCAD生成图中被恶性错涂为暗黄土褐色毛巾，大红色完全被土黄颠覆(RedLoss=0.15)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "白色浴缸与洗手台地砖暗部略微泛冷灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：卫生间门边原本鲜艳纯正的大红洋红色浴巾被恶性错涂为暗黄土褐色(RedLoss=0.15)，改判错色(C-L2)与偏色(D-L1)。"
    },
    7113: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "草坪斜坡上远足者身上穿戴的原本极其鲜艳的亮粉红色上衣在LCAD生成图中被恶性错涂为草绿色衣服(RedLoss=0.25)，粉红色被彻底篡改为草绿色"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "草坪近景阴影处略带发灰泛暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：草坪斜坡上远足者身穿的鲜艳粉红上衣被恶性错涂为草绿色(RedLoss=0.25)，改判错色(C-L2)与偏色(D-L1)。"
    },
    7129: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "溪流乱石滩旁男子手中握着的原本纯正鲜艳的明黄色飞盘在LCAD生成图中完全脱色褪白，退化为毫无生气的惨白浅灰飞盘"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "男子腰间系着的红色装饰布带严重脱色发暗变棕褐"}
        ],
        "review_note": "Double Check复核改判：核查发现：溪流乱石滩旁男子手中握着的鲜艳明黄色飞盘严重脱色蜕变为惨白色，红布发暗，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7130: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "丰盛餐桌左后方原本极其普通的深棕原木色木椅在LCAD生成图中被恶性错涂为刺眼醒目的高饱和荧光草绿色油漆椅，木材质感与颜色完全失真错涂"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "餐盘烤肉与面饼色相略微泛红发焦"}
        ],
        "review_note": "Double Check复核改判：核查发现：餐桌左后方原本深棕色原木餐椅被恶性错涂为刺眼醒目的荧光草绿色，改判错色(C-L2)与偏色(D-L1)。"
    },
    7131: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "热带海滩原本清澈碧绿纯净的蔚蓝海水在LCAD生成图中完全脱色褪淡，蜕变为发暗发灰、浑浊肮脏的死水泥滩，海水清亮生机完全丧失"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "涉水骑手身上穿的原本鲜亮亮橙色上衣发暗发焦脱色"}
        ],
        "review_note": "Double Check复核改判：核查发现：热带海滩原本清澈碧绿纯净的蔚蓝海水完全脱色蜕变为发暗浑浊死泥水，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7168: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "草原原本荒芜阴暗的枯黄色泥泞牧场地面在LCAD生成图中被强行错涂为刺眼醒目的大片高饱和翠绿色草坪伪色(Rsat=1.62)，真实荒芜地面完全被篡改"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "母牛皮毛在阳光下略微泛偏橙发焦"}
        ],
        "review_note": "Double Check复核改判：核查发现：原本荒芜阴暗的枯黄泥泞牧场地面被强行错涂为刺眼高饱和翠绿色草坪伪色(Rsat=1.62)，改判错色(C-L2)与偏色(D-L1)。"
    },
    7184: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "摄影作品四周原本极具视觉冲击力与设计感的粗大鲜红色装饰外边框在LCAD生成图中严重脱色退化为脏污暗褐灰黑色(RedLoss=0.20)，纯正大红完全丧失"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "左侧车厢窗口原本的红色小方框脱色发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：摄影作品四周原本极具视觉冲击力的粗大鲜红色装饰外边框严重脱色退化为脏污暗褐灰黑色(RedLoss=0.20)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7204: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "水牛竞速赛事中赤膊骑手原本黝黑健康的红褐色/深棕色人体肤色在LCAD生成图中被恶性错涂为惊悚诡异的荧光翠绿色伪色，犹如涂抹荧光绿漆，人体色彩严重失真"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "飞溅泥浆水花略微泛暗偏灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：水牛竞速骑手赤膊上身被恶性错涂为惊悚诡异的荧光翠绿色伪色，改判错色(C-L2)与偏色(D-L1)。"
    },
    7213: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "广场天空中放飞的原本鲜明纯正的黄绿色小风筝在LCAD生成图中被恶性错涂为鲜艳大红洋紫色风筝；幼童浅蓝上衣被错涂为紫粉色(RedLoss=0.18)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "广场石板地面阴影处略显泛蓝偏冷"}
        ],
        "review_note": "Double Check复核改判：核查发现：天空中飞行的黄绿小风筝被恶性错涂为大红洋紫色风筝，幼童上衣错色(RedLoss=0.18)，改判错色(C-L2)与偏色(D-L1)。"
    },
    7248: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "餐盘中原本具有鲜亮诱人草莓粉红色淋面的慕斯蛋糕在LCAD生成图中严重脱色退化，蜕变为冷灰发暗、毫无食欲的脏灰土色蛋糕(DeltaC=0.047)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "餐桌右上角原本鲜艳明黄色的陶瓷茶壶脱色发白变浅黄灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：餐盘中原本具有草莓粉红淋面的甜点蛋糕严重脱色退化为发脏暗淡土灰色，黄茶壶脱白，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7256: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "游艇码头停靠的两艘白色游艇原本极其纯正鲜艳的深海蓝色船底涂装在LCAD生成图中完全脱色发黑退化为死黑灰(RedLoss=0.16, Rsat=0.64)；天空也完全脱色为惨白灰白天幕"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "码头停放的木质靠椅色相略微泛暗偏灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：游艇码头两艘白色游艇的深海蓝船底涂装与蓝天严重脱色蜕变为暗黑灰与惨白天幕(RedLoss=0.16)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7283: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "棒球场背景墙与两名球员球衣原本色彩对比鲜明（左侧大红28号、右侧浅蓝绿32号），在LCAD生成图中严重脱色发暗，背景墙变死黑灰，球衣退化为惨白与灰暗色(RedLoss=0.21, Rsat=0.62)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "棒球场泥土沙地在阴影处发乌偏冷"}
        ],
        "review_note": "Double Check复核改判：核查发现：棒球场背景墙与两名球员的红色、浅蓝绿色球衣严重脱色退化为惨白与黑灰(RedLoss=0.21)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7284: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "球场训练防护网后方原本极其醒目鲜艳的大红色广告字体与标牌在LCAD生成图中严重脱色褪淡，退化为发暗发脏的暗黑灰红字(RedLoss=0.24)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "教练身穿的黑色棒球服与球帽略微发暗失真"}
        ],
        "review_note": "Double Check复核改判：核查发现：看台护网后方原本极其鲜艳的大红广告字体与标牌严重脱色褪淡为暗黑灰(RedLoss=0.24)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7296: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "红砖立柱后方原本生机盎然的茂盛翠绿色树林在LCAD生成图中严重脱色发灰，退化成了毫无生气的枯死黄灰色杂树(Rsat=0.54, DeltaC=0.043)，蓝天也脱色蜕变灰白天幕"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "广场水泥地面反光略带偏冷青灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：红砖立柱后方原本生机盎然的茂盛翠绿树林严重脱色退化为枯槁灰暗杂树(Rsat=0.54)，改判欠饱和(E2-L2)与偏色(D-L1)。"
    },
    7311: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "无障碍卫生间墙面上原本醒目纯正的深蓝色残疾人轮椅标牌与大红色紧急求助按钮在LCAD生成图中严重脱色褪淡，退化为暗灰色与浅灰色无色标识(RedLoss=0.28, Rsat=2.22)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "防滑地面暗部区域色相略显发暗偏紫"}
        ],
        "review_note": "Double Check复核改判：核查发现：无障碍卫生间内原本醒目纯正的蓝色残疾人标识与红色紧急按钮严重脱色蜕变为暗灰浅灰(RedLoss=0.28)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7323: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "圆镜前青年男子身穿原本清新纯正的淡粉红色长袖衬衫在LCAD生成图中完全脱色褪白，退化为冷灰色、暗淡无光的浅蓝灰灰白色衬衫(Rsat=0.48)，粉红色彻底丧失"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "青年男子面部肤色在暗光下略显泛灰偏冷"}
        ],
        "review_note": "Double Check复核改判：核查发现：圆镜前青年男子身穿的原本清新纯正的淡粉红色衬衫严重脱色褪白为灰白色冷汗衫(Rsat=0.48)，改判欠饱和(E2-L2)与偏色(D-L1)。"
    },
    7324: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "毛绒泰迪熊玩偶脖子上系着的原本鲜艳夺目的洋红粉紫与草绿色相间彩色格纹领结在LCAD生成图中严重脱色发暗，退化为暗黑灰色的无色布条(RedLoss=0.29)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "泰迪熊原本温暖红褐色的刺绣鼻头暗淡发黑"}
        ],
        "review_note": "Double Check复核改判：核查发现：泰迪熊脖子上系着的鲜艳夺目洋红草绿彩色格纹领结严重脱色退化为暗黑灰无色布条(RedLoss=0.29)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7336: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "酒店圆形吊顶大床上铺放的原本极其浓郁鲜艳的洋红深红色被子与床尾毯在LCAD生成图中被恶性错涂为冷青灰色与脏暗土黄褐色被子，红色调完全被颠覆"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "床头暖黄灯光光晕略微偏暗偏灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：大床上铺放的原本浓郁鲜艳的洋红深红色被子/床尾毯被恶性错涂为暗青灰与土褐色，改判错色(C-L2)与偏色(D-L1)。"
    },
    7337: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "停机坪客机垂直尾翼与发动机短舱上原本清爽纯正的天青蓝/湖水蓝色经典航空涂装在LCAD生成图中完全脱色褪变，退化为发暗死灰色的脏冷灰色(RedLoss=0.17, Rsat=0.59)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "雨水积水地面倒影略微泛暗泛黄"}
        ],
        "review_note": "Double Check复核改判：核查发现：停机坪客机垂直尾翼与发动机短舱原本清爽纯正的天青蓝色涂装完全脱色蜕变脏冷灰色(RedLoss=0.17)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7354: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "足球比赛中红队小球员身穿的原本鲜艳纯正的大红色球衣与绿队球员的翠绿色球衣在LCAD生成图中全部被恶性错涂为深宝蓝色，两队红绿球衣被严重混淆篡改为深蓝(RedLoss=0.26)"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "草坪上滚动的鲜黄色足球严重脱色发白"}
        ],
        "review_note": "Double Check复核改判：核查发现：足球小球员原本鲜艳纯正的大红色与翠绿色球衣全被恶性错涂为深宝蓝色，红绿混淆篡改(RedLoss=0.26)，改判错色(C-L2)与欠饱和(E2-L1)。"
    },
    7398: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "厨房备餐女子身上穿戴的原本极其鲜艳纯正的芭比粉红色连帽卫衣在LCAD生成图中完全脱色褪变为浅土黄米白色的暗淡汗衫，鲜艳粉红色彻底丧失"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "橱柜木质门板在阴影处略带泛暗发焦"}
        ],
        "review_note": "Double Check复核改判：核查发现：厨房备餐女子身穿的鲜艳芭比粉红色连帽卫衣严重脱色退化为浅土黄米白汗衫，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7446: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "曼谷大皇宫前各国游客手中撑着的纯天蓝、洋红粉紫、鲜黄色彩色遮阳伞在LCAD生成图中完全脱色褪变，退化为单调乏味的浅灰白色与暗灰伞顶"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "大皇宫金色尖顶在天空映衬下暗淡泛灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：曼谷大皇宫前各国游客撑着的纯天蓝、洋红、明黄彩色遮阳伞完全脱色蜕变灰白色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7448: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "主题公园门楼上方架设的原本极其鲜艳纯正的大红色螺旋桨双翼小飞机在LCAD生成图中完全脱色褪暗，被恶性错涂为暗沉泥土绿褐色与发脏深绿军用伪装色，红色完全消失"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "前景游客身上身穿的鲜红色T恤严重脱色发暗偏褐"}
        ],
        "review_note": "Double Check复核改判：核查发现：门楼上方架设的原本鲜艳纯正的大红色螺旋桨小飞机被恶性错涂为暗沉泥土绿褐色，前景游客红衣脱色，改判错色(C-L2)与欠饱和(E2-L1)。"
    },
    7468: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "铁路桥旁左下角停放的原本极其鲜艳纯正的复古大红色小汽车在LCAD生成图中完全脱色退化，蜕变为冷铁灰色与暗淡青灰色小车(RedLoss=0.18, Rsat=0.48)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "桥上骑行者穿戴的鲜艳橙红骑行服脱色发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：左下角原本极其醒目鲜艳的复古大红色小汽车完全脱色退化为冷铁灰色(RedLoss=0.18)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7473: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "大象训练中心两名驯象员身上穿戴的原本极其纯正鲜艳的大红色民族上衣与头巾在LCAD生成图中被恶性错涂为亮洋红粉紫色(Rsat=1.48)，红色色相严重漂移"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "上方木质招牌匾额偏橙黄发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：两名驯象员原本纯正鲜艳的大红色民族上衣被恶性错涂为亮洋红粉紫色(Rsat=1.48)，改判错色(C-L2)与偏色(D-L1)。"
    },
    7486: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "会客厅中央原本纯正鲜艳的生机草绿色布艺沙发在LCAD生成图中被恶性错涂为墨绿发黑、深阴冷青黑色的脏污沙发，草绿生机被彻底剥夺(Rsat=1.36)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内原本温馨明亮的暖黄壁纸灯光整体暗淡发灰泛冷"}
        ],
        "review_note": "Double Check复核改判：核查发现：会客厅中央原本纯正鲜艳的草绿色布艺沙发被恶性错涂为墨绿发黑冷暗沙发(Rsat=1.36)，改判错色(C-L2)与偏色(D-L1)。"
    },
    7491: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "俯瞰小镇建筑群大片原本鲜艳纯正的红砖瓦屋顶与红砖外立面在LCAD生成图中严重脱色发灰，蜕变为灰蒙蒙一片水泥灰色的衰败灰暗小镇(RedLoss=0.15, Rsat=0.54)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "街道上行驶的红色小汽车脱色发黑"}
        ],
        "review_note": "Double Check复核改判：核查发现：俯瞰小镇建筑群大片原本鲜艳纯正的红砖瓦屋顶与外立面严重脱色蜕变水泥灰白暗灰色(RedLoss=0.15)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7500: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "海滩上空原本极其浓郁温暖的粉红橙金黄昏晚霞在LCAD生成图中完全脱色被剥夺，蜕变为了冰冷阴暗的冷白灰阴霾天幕(RedLoss=0.14, Rsat=0.40, DeltaC=0.043)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "海面碧蓝波涛反光发暗失色"}
        ],
        "review_note": "Double Check复核改判：核查发现：海滩上空原本极其浓郁温暖的粉红橙金黄昏晚霞完全脱色蜕变为阴冷灰白天幕(RedLoss=0.14)，改判欠饱和(E2-L2)与错色(C-L1)。"
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
    stream_path = STREAMS_DIR / "tasks_lcad_7001_7500_stream.json"
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
    print("Applying Double Check updates for 7001-7500...")
    
    # 1. Update batch 7001-7500
    b_path = EXPORTS_DIR / "reviewed_7001_7500_20260930_161800.json"
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

    print("Double check updates for 7001-7500 completed successfully!")

if __name__ == "__main__":
    main()
