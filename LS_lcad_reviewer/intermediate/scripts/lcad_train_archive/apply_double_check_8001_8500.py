"""Apply Double Check updates for batch 8001-8500 pass tasks.
Updates reviewed_8001_8500, stream package, and full 1-10000 exports.
Follows the exact V4 schema contract from AGENTS.md.
"""
import json
import os
import shutil
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"
STREAMS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "streams"

# 38 Grounded Double Check Corrections for 8001-8500
DC_CORRECTIONS = {
    8003: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "海面上方进港客机垂直尾翼上原本醒目的鲜艳橙红色航徽条纹在LCAD生成图中严重脱色褪淡，退化为发灰暗褐条纹(Rsat=1.71)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "近景海水波浪略显泛暗偏蓝"}
        ],
        "review_note": "Double Check复核改判：核查发现：民航客机垂直尾翼原本醒目的鲜艳橙红航徽条纹严重脱色褪淡为发灰暗褐条纹(Rsat=1.71)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8011: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "非洲原野斑马群漫步的原本开阔生机青翠草坪在LCAD生成图中大面积欠饱和脱色，褪变为发灰发暗的死灰绿草地(Rsat=0.50, DeltaC=0.032)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "斑马身体黑白斑纹边缘略显发乌"}
        ],
        "review_note": "Double Check复核改判：核查发现：非洲原野开阔生机青翠草坪大面积欠饱和脱色为发暗死灰绿草地(Rsat=0.50)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8012: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "网球场原本明亮鲜艳的深海蓝色硬地地面在LCAD生成图中完全脱色蜕变，退化为发脏阴暗的深灰黑水泥地(DeltaC=0.046)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "网球选手深蓝色短袖与球拍略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：网球场明亮鲜艳深海蓝色硬地地面完全脱色蜕变为发脏深灰黑水泥地(DeltaC=0.046)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8022: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "滑雪双板原本鲜艳纯正的彩虹条纹个性涂装在LCAD生成图中局部严重脱色褪淡，鲜艳洋红与纯正青蓝完全蜕变发白(RedLoss=0.26, Rsat=1.84)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "雪地背阴处阴影略带偏冷泛蓝"}
        ],
        "review_note": "Double Check复核改判：核查发现：滑雪双板鲜艳彩虹条纹涂装局部严重脱色褪淡，鲜红青蓝蜕变发白(RedLoss=0.26)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8055: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "城市道路上骑行者脚下的公路自行车原本醒目亮丽的明黄色金属车架在LCAD生成图中严重脱色褪白，退化为苍白灰白无色车架(Rsat=0.58, RedLoss=0.17)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "骑行者白色短袖与柏油路面略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：公路自行车醒目亮丽明黄色金属车架严重脱色褪白(Rsat=0.58)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8060: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "生日宴会上老妇人身上原本洁净素雅的米白羊毛开衫被恶性错涂为脏乱粉红色，桌上原本生机盎然的翠绿餐垫严重脱色蜕白(DeltaC=0.029)"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "生日蛋糕上点缀的烛光与草莓糖霜略微褪色"}
        ],
        "review_note": "Double Check复核改判：核查发现：老妇人米白开衫被恶性错涂为脏乱粉红色，桌上翠绿餐垫严重脱色褪白(DeltaC=0.029)，改判错色(C-L2)与欠饱和(E2-L1)。"
    },
    8061: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "餐椅靠背上原本搭着的鲜艳大红色外套在LCAD生成图中被恶性错涂为暗哑黄绿色伪色(DeltaC=0.025)，大红色相完全失真篡改"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "室内木质餐桌与橱柜暗部略微泛冷灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：餐椅靠背上搭着的鲜艳大红外套被恶性错涂为暗哑黄绿色伪色(DeltaC=0.025)，改判错色(C-L2)与偏色(D-L1)。"
    },
    8063: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "湿地大象群栖息的原本开阔红褐色滩涂泥地在LCAD生成图中被大面积强行错涂为淡黄绿色草地伪色，红泥自然地质完全被错误草皮抹杀"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "大象灰色皮毛暗影处略带偏冷发青"}
        ],
        "review_note": "Double Check复核改判：核查发现：湿地大象群栖息的原本红褐色滩涂泥地被大面积强行错涂为淡黄绿色草地伪色，改判错色(C-L2)与偏色(D-L1)。"
    },
    8081: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "棒球场内场平展翠绿草皮与教练身穿的深蓝色风衣在LCAD生成图中局部恶性错涂为刺眼青蓝杂色色斑(DeltaC=0.038)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "投手土质球丘边缘略带发红偏色"}
        ],
        "review_note": "Double Check复核改判：核查发现：棒球场翠绿草皮与教练深蓝风衣局部恶性错涂为刺眼青蓝杂色色斑(DeltaC=0.038)，改判错色(C-L2)与偏色(D-L1)。"
    },
    8094: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "医疗护理室内原本醒目的洋红粉紫药盒与彩色标识在LCAD生成图中大面积严重脱色褪淡，退化为发脏灰褐色(RedLoss=0.22)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "白色输液架与输液袋反光略显发乌"}
        ],
        "review_note": "Double Check复核改判：核查发现：医疗护理室内醒目洋红粉紫药盒与彩色标识大面积脱色退化为发脏灰褐色(RedLoss=0.22)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8104: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "深绿旅行箱内小猫身旁原本鲜艳的亮粉色织物与明黄色行李挂牌严重脱色褪淡，褪变为暗暗灰土色(RedLoss=0.22, Rsat=1.53)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "小猫白色毛皮阴影局部略显暗青"}
        ],
        "review_note": "Double Check复核改判：核查发现：旅行箱内小猫身旁鲜艳亮粉色织物与黄色行李牌严重脱色为暗灰土色(RedLoss=0.22)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8112: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "网球女将身上原本明艳鲜亮的纯正黄色运动短袖在LCAD生成图中完全脱色褪白，退化为普通无色纯白短袖(Rsat=0.50, DeltaC=0.039)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "网球拍握把与蓝色遮阳帽略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：网球女将身上原本明艳纯正黄色运动短袖完全脱色褪白为无色白短袖(Rsat=0.50)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8136: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "观景看台上身穿大红色短袖T恤的男子上衣在LCAD生成图中大面积脱色褪淡，退化为发脏浅土灰白色(RedLoss=0.15, Rsat=0.71)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "身旁游客撑着的雨伞伞布边缘略显发乌"}
        ],
        "review_note": "Double Check复核改判：核查发现：看台上身穿大红短袖T恤男子上衣大面积脱色褪淡为发脏浅土灰白色(RedLoss=0.15)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8138: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "玻璃花瓶中原本娇艳柔嫩的单支粉红色玫瑰花瓣在LCAD生成图中被恶性错涂为刺眼醒目的亮橙黄色伪色(RedLoss=0.47, Rsat=1.23)，花卉品种质感被彻底篡改"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "满天星白色小花与绿叶边缘略微泛黄偏色"}
        ],
        "review_note": "Double Check复核改判：核查发现：花瓶中娇艳柔嫩的单支粉红玫瑰花瓣被恶性错涂为亮橙黄色伪色(RedLoss=0.47)，改判错色(C-L2)与偏色(D-L1)。"
    },
    8163: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "狭窄街区两侧原本灯火通明的商铺橱窗与暖黄外立面大面积脱色褪白，退化为阴冷灰白水泥街景(Rsat=0.45, RedLoss=0.16)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "街道石砖路面潮湿反光处略显偏冷"}
        ],
        "review_note": "Double Check复核改判：核查发现：街区两侧灯火通明的商铺橱窗与暖黄外立面大面积脱色褪白为阴冷灰白街景(Rsat=0.45)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8201: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "围栏后围观小斑马的游客身上原本鲜艳纯正的洋红粉裤与亮蓝短裤严重欠饱和脱色，褪为暗沉灰白(Rsat=0.55)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "小斑马身上黑白条纹边缘略显发乌"}
        ],
        "review_note": "Double Check复核改判：核查发现：围观游客鲜艳纯正洋红粉裤与亮蓝短裤严重欠饱和脱色为暗沉灰白(Rsat=0.55)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8211: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "依靠石墙席地而坐的青年男子胸前原本鲜艳纯正的红色印花领带在LCAD生成图中被恶性错涂为黄绿色伪色，领带饰品色相发生根本性颠覆"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "背后石砖墙体与男子牛仔裤略微泛冷灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：青年男子胸前原本鲜艳纯正的红色印花领带被恶性错涂为黄绿色伪色，改判错色(C-L2)与偏色(D-L1)。"
    },
    8220: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "卫生间黑色大理石浴缸台面与地砖原本沉稳黑白质感在LCAD生成图中被严重欠饱和脱色，褪变为发暗冷灰调(Rsat=0.32, DeltaC=0.031)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "白色马桶与浴缸内壁微带灰影"}
        ],
        "review_note": "Double Check复核改判：核查发现：卫生间黑色大理石浴缸台面与地砖原本沉稳质感严重欠饱和脱色为发暗冷灰调(Rsat=0.32)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8222: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "餐盘中原本鲜亮纯正的金黄色柠檬切片在LCAD生成图中被恶性错涂为青柠绿色伪色，水果色相完全被颠覆"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "烤肉排与炸薯条暗部略微泛红褐色偏色"}
        ],
        "review_note": "Double Check复核改判：核查发现：餐盘中鲜亮金黄色柠檬切片被恶性错涂为青柠绿色伪色，改判错色(C-L2)与偏色(D-L1)。"
    },
    8224: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "阳光沙滩背景原本清澈明净的蔚蓝海面与晴空大面积严重脱色褪淡，退化为发灰阴霾，沙滩遮阳伞下的红色包袋完全脱色发白(Rsat=0.44, RedLoss=0.18)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "白色沙滩躺椅阴影处略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：沙滩背景蔚蓝海面与晴空大面积严重脱色褪淡为发灰阴霾，红色包袋脱色(Rsat=0.44)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8227: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "窗边看猫咪的室内原本温馨暖黄的漆面墙壁大面积脱色褪白，蜕变为冰冷苍白的灰白墙面(Rsat=0.48, DeltaC=0.045)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "窗外红砖建筑外墙略微泛青发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：室内原本温馨暖黄漆面墙壁大面积脱色褪白为冰冷苍白灰白墙面(Rsat=0.48)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8263: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "客厅茶几上原本盛开绚烂的鲜艳大红与金黄色插花花束大面积严重脱色，蜕变为发灰暗淡的灰白枯花(Rsat=0.59, DeltaC=0.025)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "沙发上人物衣物阴影处略带发灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：客厅茶几原本盛开的鲜艳大红与金黄插花花束大面积脱色蜕变为暗淡灰白枯花(Rsat=0.59)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8280: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "步行街打伞女子臂弯挎着的原本鲜亮明黄色的时尚手提包大面积脱色褪淡，退化为暗哑土黄褐色(RedLoss=0.11)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "女子黑色连衣裙与沥青路面略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：步行街打伞女子原本鲜亮明黄手提包大面积脱色褪淡为暗哑土黄褐色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8301: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "阳光下合影男子面部原本健康自然的面部肤色在LCAD生成图中被严重过度烘烤，恶性偏色为发红发紫的焦黑重度偏色(Rsat=1.84, DeltaC=0.028)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "金色领带与浅蓝色衬衫光泽略显混杂发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：合影男子面部健康肤色被严重过度烘烤发红发紫焦黑重度偏色(Rsat=1.84)，改判偏色(D-L2)与错色(C-L1)。"
    },
    8308: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "赶羊群牧民身后原本苍翠葱郁的青山绿化林与草坡大面积严重脱色，退化为发干枯槁的荒芜灰泥色(Rsat=0.59, DeltaC=0.044)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "羊群羊毛反光微显发乌"}
        ],
        "review_note": "Double Check复核改判：核查发现：牧民身后原本苍翠葱郁青山树林与草坡大面积脱色退化为发干枯槁荒芜灰泥色(Rsat=0.59)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8331: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "办公卡位原本干净整洁的米黄织物隔断墙在LCAD生成图中被恶性错涂为发脏发暗的深灰绿色调(DeltaC=0.034)，隔断墙自然温馨感彻底丧失"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "电脑显示器外壳与键盘略带发青发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：办公卡位原本米黄织物隔断墙被恶性错涂为发脏发暗的深灰绿色调(DeltaC=0.034)，改判错色(C-L2)与偏色(D-L1)。"
    },
    8332: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "冲浪运动员脚下的冲浪板板头原本鲜亮纯正的大红色涂装严重脱色褪淡，退化为发灰无色涂装(RedLoss=0.20)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "冲浪服袖口与海水浪花反光略微泛暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：冲浪板板头原本鲜亮纯正大红色涂装严重脱色褪淡为发灰无色涂装(RedLoss=0.20)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8345: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "野餐桌上原本鲜亮活泼的红白方格印花桌布在LCAD生成图中大面积脱色错涂为发暗黄褐色格纹(DeltaC=0.033)，红色方格色相完全丧失"},
            {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "盘中蛋糕与水果表面微有褪色"}
        ],
        "review_note": "Double Check复核改判：核查发现：野餐桌原本鲜亮红白方格印花桌布大面积脱色错涂为发暗黄褐色格纹(DeltaC=0.033)，改判错色(C-L2)与欠饱和(E2-L1)。"
    },
    8373: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "乘船游客身上原本鲜红的棒球帽与快艇鲜艳纯正的大红色船体内侧在LCAD生成图中完全脱色褪淡，退化为发脏暗黑灰(Rsat=0.48, RedLoss=0.14)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "近景海面波浪微显发暗发青"}
        ],
        "review_note": "Double Check复核改判：核查发现：游客鲜红棒球帽与快艇大红船体内侧完全脱色褪淡退化为发脏暗黑灰(Rsat=0.48)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8384: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "客厅玩体感游戏的年轻男子身上原本朴素的浅灰橄榄绿短袖T恤被恶性错涂为刺眼醒目的亮洋红粉紫色伪色，衣服色相发生本质性篡改颠覆"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "身后白色书架与木质地板略微泛紫偏色"}
        ],
        "review_note": "Double Check复核改判：核查发现：年轻男子原本浅灰橄榄绿短袖T恤被恶性错涂为刺眼醒目的亮洋红粉紫色伪色，改判错色(C-L2)与偏色(D-L1)。"
    },
    8385: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "货运列车前方原本鲜亮醒目的联合太平洋明黄色重型机车车头大面积欠饱和脱色，褪变为发暗脏灰泥黄(Rsat=0.43, RedLoss=0.15)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "铁轨枕木与道砟石略微发乌发灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：货运列车前方鲜亮醒目的明黄色机车车头大面积脱色褪淡为发暗灰泥黄(Rsat=0.43)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8397: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "卫生间上方原本洁净的白色瓷砖墙壁在LCAD生成图中被恶性错涂大面积突兀的深洋红紫晕伪色，墙面材质完全被暗紫伪色破坏"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "粉色马桶盖边缘与地面瓷砖略显发灰泛暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：卫生间上方白色瓷砖墙壁被恶性错涂大面积突兀的深洋红紫晕伪色，改判错色(C-L2)与偏色(D-L1)。"
    },
    8439: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "餐厅厨房左侧进门通道与门框在LCAD生成图中被恶性错涂为大片刺目突兀的亮洋红粉色伪色(RedLoss=0.16)，原本不锈钢金属感完全被紫粉篡改"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "厨房不锈钢烹饪灶台反光处略微偏冷"}
        ],
        "review_note": "Double Check复核改判：核查发现：餐厅厨房左侧通道与门框被恶性错涂为大片刺目突兀亮洋红粉色伪色(RedLoss=0.16)，改判错色(C-L2)与偏色(D-L1)。"
    },
    8454: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街头执勤交警身上原本醒目明亮的荧光橙红与明黄安全反光背心在LCAD生成图中完全脱色褪白，退化为普通发灰白背心(RedLoss=0.18)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "自行车金属车架与沥青地面微显暗黑"}
        ],
        "review_note": "Double Check复核改判：核查发现：交警身上醒目明亮的荧光橙红与明黄安全反光背心完全脱色褪白为灰白背心(RedLoss=0.18)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8469: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "象群身后原本生机盎然的平展翠绿色草坪大面积欠饱和脱色，褪变为发暗枯黄的泥土杂草色(Rsat=1.39, DeltaC=0.023)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "母象与小象背部皮毛反光微显泛红偏色"}
        ],
        "review_note": "Double Check复核改判：核查发现：象群身后生机盎然的平展翠绿草坪大面积欠饱和脱色为发暗枯黄泥土色(DeltaC=0.023)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8474: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "行李箱内放置的原本鲜艳亮丽的粉红色女士皮包在LCAD生成图中被恶性错涂为暗哑黄绿褐色，皮包原本优雅色相被彻底篡改"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "小猫皮毛与右侧黑色漆皮手袋略显发暗偏冷"}
        ],
        "review_note": "Double Check复核改判：核查发现：行李箱内鲜艳粉红色女士皮包被恶性错涂为暗哑黄绿褐色，改判错色(C-L2)与偏色(D-L1)。"
    },
    8484: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "卫生间原本清爽明净的浅天蓝色涂装墙壁在LCAD生成图中大面积欠饱和脱色，褪变为暗淡无色灰白墙面(RedLoss=0.16)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "白色洗手盆边缘与镜面阴影微显发灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：卫生间清爽浅天蓝色涂装墙壁大面积欠饱和脱色为暗淡灰白墙面(RedLoss=0.16)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    8486: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "宴会餐厅原本优雅清爽的薄荷浅绿色涂装墙面在LCAD生成图中大面积严重脱色，蜕变为发暗灰白水泥墙(DeltaC=0.026)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "餐桌上点缀的花卉与白色餐巾略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：宴会餐厅优雅清爽薄荷浅绿色涂装墙面大面积严重脱色为发暗灰白水泥墙(DeltaC=0.026)，改判欠饱和(E2-L2)与错色(C-L1)。"
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
    stream_path = STREAMS_DIR / "tasks_lcad_8001_8500_stream.json"
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
    print("Applying Double Check updates for 8001-8500...")
    
    # 1. Update batch 8001-8500
    b_path = EXPORTS_DIR / "reviewed_8001_8500_20260930_184910.json"
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

    print("Double check updates for 8001-8500 completed successfully!")

if __name__ == "__main__":
    main()
