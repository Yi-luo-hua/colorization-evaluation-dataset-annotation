"""Apply Double Check updates for batch 7501-8000 pass tasks.
Updates reviewed_7501_8000, stream package, and full 1-10000 exports.
Follows the exact V4 schema contract from AGENTS.md.
"""
import json
import os
import shutil
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"
STREAMS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "streams"

# 40 Grounded Double Check Corrections for 7501-8000
DC_CORRECTIONS = {
    7542: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "机场行李提取大厅上方原本醒目明亮的暖黄橙色夜光航班指示灯牌在LCAD生成图中严重脱色褪白，退化为冰冷灰暗的白灰底板(Rsat=0.34)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "大厅立柱与地面反光轻微偏冷偏暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：机场行李提取大厅上方暖黄橙色夜光航班指示牌严重脱色为冰冷灰白底板(Rsat=0.34)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7556: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "主卧室内原本温润厚重的红木色实木衣柜与梳妆台在LCAD生成图中严重欠饱和脱色，褪变为冰冷灰米色(Rsat=0.58)，高档红木质感彻底丧失"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "梳妆台镜框边缘略带发青发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：主卧红木色实木衣柜与梳妆台严重欠饱和脱色为冷灰米色(Rsat=0.58)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7565: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "街头保洁员身旁圆形街区指示路牌原本为纯正清爽的天蓝色底色，在LCAD生成图中被恶性错涂为刺眼醒目的亮洋红粉色(Rsat=0.37)，街标色相彻底颠覆"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "人行道黑白拼花石砖阴影部分略微泛紫偏色"}
        ],
        "review_note": "Double Check复核改判：核查发现：街头圆形街区指示路牌原本清爽天蓝色底色被恶性错涂为亮洋红粉色(Rsat=0.37)，改判错色(C-L2)与偏色(D-L1)。"
    },
    7570: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "游览大象背部原本极其华丽喜庆的大红色金边刺绣遮阳鞍毯在LCAD生成图中大面积严重脱色褪白，退化为发脏灰白无色麻布(RedLoss=0.16)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "游客身上衣物与大象头部缰绳轻微泛暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：大象背部华丽大红金边鞍毯完全脱色褪白为发脏灰白麻布(RedLoss=0.16)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7580: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "棒球捕手身上穿着的原本鲜艳纯正的深酒红色运动长袖球衣在LCAD生成图中完全脱色褪淡，退化为死气沉沉的深黑灰色(Rsat=0.44)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "捕手身后草坪与防护护栏轻微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：棒球捕手鲜艳深酒红球衣完全脱色退化为深黑灰色(Rsat=0.44)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7622: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "冲浪巨浪卷起的浪管内壁与天空在LCAD生成图中被恶性错涂为极其刺目突兀的荧光青蓝与洋红紫晕伪色(Rsat=1.39, RedLoss=0.17)，海水自然清澈质感完全失真"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "冲浪板与近景白浪泡沫略带粉红偏色"}
        ],
        "review_note": "Double Check复核改判：核查发现：冲浪浪管内壁与天空被恶性错涂为刺目荧光青蓝与洋红紫晕伪色(Rsat=1.39)，改判错色(C-L2)与偏色(D-L1)。"
    },
    7624: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "经典复古双层客车原本沉稳高贵的经典深宝蓝色车身在LCAD生成图中被恶性错涂为暗哑的橄榄草绿色伪色，车体原貌色相完全错乱颠覆"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "左侧红色双层巴士顶部白漆略泛暖黄"}
        ],
        "review_note": "Double Check复核改判：核查发现：经典复古双层客车原本深宝蓝色车身被恶性错涂为橄榄草绿色伪色，改判错色(C-L2)与偏色(D-L1)。"
    },
    7630: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "趴卧在红白双人自行车旁的黑色牧羊犬脖颈与胸部毛皮在LCAD生成图中被恶性错涂大片极其刺眼突兀的橙红荧光色斑(RedLoss=0.20)，毛色发生严重伪色污染"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "双人自行车红色车架局部略带泛紫"}
        ],
        "review_note": "Double Check复核改判：核查发现：自行车旁趴卧黑狗颈部胸口被恶性污染大片刺目橙红荧光斑块(RedLoss=0.20)，改判错色(C-L2)与偏色(D-L1)。"
    },
    7633: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "公园长椅左侧小男孩身上原本明亮鲜艳的橙红色短袖T恤在LCAD生成图中被恶性错涂为浅天蓝色(Rsat=0.74)，衣服色相发生根本性颠覆"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "右侧小男孩短裤略带泛冷偏灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：公园长椅左侧小男孩鲜艳橙红T恤被恶性错涂为浅天蓝色，改判错色(C-L2)与偏色(D-L1)。"
    },
    7680: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "草坪旁青年男子身上原本鲜艳醒目的砖红色连帽卫衣在LCAD生成图中大面积脱色褪淡，退化为冰冷灰暗的发青深蓝灰色(RedLoss=0.16, Rsat=0.60)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "身后枯草堆与绿化林阴影轻微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：青年男子原本鲜艳砖红连帽卫衣完全脱色退化为冰冷发青暗蓝灰色(RedLoss=0.16)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7685: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "夕阳海滩上搁浅的多艘木质小渔船原本明艳的大红与翠绿色个性涂装在LCAD生成图中严重脱色褪淡，退化为暗沉脏乱的泥土灰褐色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "夕阳晚霞天空与海面交界处色彩过渡略显生硬"}
        ],
        "review_note": "Double Check复核改判：核查发现：夕阳沙滩搁浅木质渔船原本鲜红与翠绿明艳涂装严重欠饱和脱色为暗沉泥土灰(DeltaC=0.033)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7718: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "河畔绿草坡上大量休闲游客原本鲜艳亮丽的大红泳裤与亮橙色短袖在LCAD生成图中大面积脱色蜕白，退化为发脏灰白无色小斑点(RedLoss=0.18)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "河水浅滩处水体略带泛暗发绿"}
        ],
        "review_note": "Double Check复核改判：核查发现：河畔草坡休闲游客大红与亮橙色衣物大面积脱色蜕白(RedLoss=0.18)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7732: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "实木电脑书桌上原本极其鲜亮的大红色长条鼠标桌垫在LCAD生成图中完全脱色褪白，彻底退化为冰冷苍白的灰白色旧垫"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "电脑机箱外壳与木质桌面反光处轻微偏冷"}
        ],
        "review_note": "Double Check复核改判：核查发现：实木书桌上鲜亮大红长条鼠标桌垫完全脱色褪白为冰冷灰白旧垫，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7741: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "宏伟钟楼背景原本清澈明净的蔚蓝晴空在LCAD生成图中大面积欠饱和脱色，褪变为发暗阴冷的灰白阴霾天幕(Rsat=0.67)，晴天开阔感尽失"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "钟楼石雕外立面阴影略带暗褐偏色"}
        ],
        "review_note": "Double Check复核改判：核查发现：钟楼背景原本清澈蔚蓝晴空大面积欠饱和脱色为发暗灰白阴霾(Rsat=0.67)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7757: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "简陋泥房上方原本深灰锈蚀的铁皮瓦楞屋顶在LCAD生成图中被恶性错涂为极其刺目违和的荧光翠绿色伪色(DeltaC=0.047)，建筑材质完全被荧光绿篡改"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "泥土地面与行人所背香蕉略带暗黄偏色"}
        ],
        "review_note": "Double Check复核改判：核查发现：简陋泥房深灰锈蚀瓦楞铁皮屋顶被恶性错涂为刺目荧光翠绿色伪色(DeltaC=0.047)，改判错色(C-L2)与偏色(D-L1)。"
    },
    7765: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "黑漆木质餐椅上原本厚实鲜艳的深红酒红色座垫在LCAD生成图中大面积脱色黑化，彻底退化为暗沉无光的黑褐色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "餐桌中央水果盘与背后书架略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：餐椅厚实鲜艳深红酒红色座垫大面积脱色黑化为暗黑褐色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7786: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "厨房原本清爽洁净的淡天蓝色涂装墙面在LCAD生成图中严重欠饱和脱色，完全蜕变褪淡为发脏暗淡的灰白水泥墙(Rsat=0.57)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "黑白方格地砖受脱色影响略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：厨房清爽淡天蓝涂装墙面严重欠饱和脱色为发脏灰白水泥墙(Rsat=0.57)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7796: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "走廊合影学生中间小女孩身上原本鲜亮纯正的翠绿色校服毛衣在LCAD生成图中完全脱色发暗，退化为深黑蓝无色毛衣(Rsat=0.53)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "左侧宣传展板纯蓝色彩略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：走廊合影学生中间小女孩鲜亮翠绿校服毛衣完全脱色发暗为深黑蓝(Rsat=0.53)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7801: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "人行道旁原本明亮醒目的金黄橙黄色木质靠背椅在LCAD生成图中大面积脱色褪白，退化为苍白惨白的灰白色废旧木椅(Rsat=0.45)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "椅子上放置的白色键盘略带发暗灰影"}
        ],
        "review_note": "Double Check复核改判：核查发现：人行道旁明亮金黄橙黄色木椅完全脱色褪白为惨白灰白旧木椅(Rsat=0.45)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7809: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "悬崖岩壁前青年男子原本鲜艳亮丽的天蓝色无袖运动背心在LCAD生成图中完全脱色褪淡，退化为发脏灰白的暗土色汗衫(Rsat=0.41)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "身旁女子白色短裙边缘略带发暗泥土色"}
        ],
        "review_note": "Double Check复核改判：核查发现：岩壁前青年男子鲜艳天蓝色无袖运动背心完全脱色褪白为发脏灰白汗衫(Rsat=0.41)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7822: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "海滩上空翱翔的风筝原本拖曳着的鲜艳大红色长条飘带在LCAD生成图中严重脱色褪淡，蜕变为发灰无色的细微绳索(RedLoss=0.30)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "海滩潮水边缘与沙滩略带暗灰发青"}
        ],
        "review_note": "Double Check复核改判：核查发现：海滩上空风筝拖曳的鲜艳大红彩色飘带严重脱色蜕变为暗灰细绳(RedLoss=0.30)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7827: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "铁栅栏置物架上原本通透晶莹的翠绿色塑料水瓶在LCAD生成图中被恶性错涂为刺眼醒目的深蓝紫渐变伪色(Rsat=4.01)，塑料水瓶自然材质彻底失真"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "黑色金属格栅边缘略带暗蓝杂光"}
        ],
        "review_note": "Double Check复核改判：核查发现：铁栅栏架上晶莹翠绿色塑料水瓶被恶性错涂为刺目深蓝紫伪色(Rsat=4.01)，改判错色(C-L2)与偏色(D-L1)。"
    },
    7850: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "原野长颈鹿群身后原本茂密青翠的绿化大树与生机草地在LCAD生成图中大面积脱色，褪变为发干发暗的枯槁土灰色杂木林(Rsat=0.53, DeltaC=0.042)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "长颈鹿身体斑纹反光略显暗哑"}
        ],
        "review_note": "Double Check复核改判：核查发现：长颈鹿身后茂盛生机翠绿树林大面积脱色退化为枯槁土灰杂木林(Rsat=0.53)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7851: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "客运列车车头前方原本极其醒目鲜艳的大红警示横条纹在LCAD生成图中大面积脱色褪淡，退化为深灰蓝色的暗淡条纹(RedLoss=0.13, Rsat=0.60)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "站台地面黄色安全警戒线略带泛白"}
        ],
        "review_note": "Double Check复核改判：核查发现：进站列车车头前方原本醒目的大红警示横条纹大面积脱色发暗为深灰蓝(RedLoss=0.13)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7868: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "沙滩儿童手持的风筝原本鲜艳的大红色拼块在LCAD生成图中严重脱色褪淡，褪变为暗沉无光的紫灰色拼面(RedLoss=0.30)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "沙滩阴影处与远处丘陵交界处略微泛暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：沙滩儿童手持风筝大红色拼块严重脱色褪淡为暗沉紫灰色(RedLoss=0.30)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7875: {
        "defects": [
            {"id": "D", "name": "偏色", "severity": "L2", "description": "采光极好的现代卫生间原本明亮纯正的冷白浅灰墙面与瓷砖在LCAD生成图中被严重烘烤发黄，恶性偏色错涂为陈旧暖土黄色调(Rsat=2.40, DeltaC=0.041)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "白色浴缸与洗手台暗部略微泛黄土色"}
        ],
        "review_note": "Double Check复核改判：核查发现：卫生间明亮冷白浅灰墙面与瓷砖严重烘烤泛黄错涂为陈旧暖土黄色调(Rsat=2.40)，改判偏色(D-L2)与错色(C-L1)。"
    },
    7881: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "长条宴会餐桌上原本鲜亮纯正的大红色折叠餐巾、卡片与桌上红花在LCAD生成图中严重脱色褪淡，褪变为发暗脏乱的泥土黄褐色"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "高脚玻璃杯与红酒瓶光泽略微泛灰"}
        ],
        "review_note": "Double Check复核改判：核查发现：宴会餐桌大红折叠餐巾与红花严重脱色褪淡为发暗脏褐色，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7883: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "客厅后方开放式厨房原本自然温润的实木橱柜与立面在LCAD生成图中被恶性错涂为刺眼醒目的荧光黄绿色伪色(Rsat=1.69, DeltaC=0.042)，木质纹理与色调完全崩塌"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "蓝色布艺沙发边缘与原木地板受荧光黄反射略带泛绿"}
        ],
        "review_note": "Double Check复核改判：核查发现：客厅后方开放式厨房木质橱柜恶性错涂为刺目荧光黄绿色伪色(Rsat=1.69)，改判错色(C-L2)与偏色(D-L1)。"
    },
    7892: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "红发撑伞女子身穿的原本深灰褐色的户外防雨风衣在LCAD生成图中被恶性错涂为刺眼突兀的亮洋红粉紫色外套，衣服色相发生本质性颠覆"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "黄色雨伞内骨架略带紫晕偏色"}
        ],
        "review_note": "Double Check复核改判：核查发现：红发女子原本深灰褐色户外防雨风衣被恶性错涂为刺眼亮洋红粉紫色外套，改判错色(C-L2)与偏色(D-L1)。"
    },
    7894: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "大象群背后原本极其茂密青翠的深绿生机森林与灌木林在LCAD生成图中大面积脱色蜕变，退化为发干枯槁的土灰色杂木林(Rsat=0.54, DeltaC=0.058)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "大象灰色粗糙皮毛暗部略带发紫偏色"}
        ],
        "review_note": "Double Check复核改判：核查发现：大象群后方生机翠绿森林大面积脱色蜕变为枯槁土灰杂木林(Rsat=0.54)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7897: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "双层客车旁停泊的经典复古小客车原本深宝蓝色的车身涂装在LCAD生成图中严重脱色褪淡，退化为暗沉深黑灰色(Rsat=0.61)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "车窗玻璃上反光与背景绿树略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：经典复古客车深宝蓝色涂装严重脱色退化为发暗深黑灰色(Rsat=0.61)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7906: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "湿滑沥青路面上原本醒目明亮的明黄色交通导向标线与红白停步标志在LCAD生成图中严重脱色褪白，退化为发灰发暗的死灰白标(RedLoss=0.17)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "路面湿水反光略带偏暗偏冷"}
        ],
        "review_note": "Double Check复核改判：核查发现：沥青路面醒目明黄色导向标线与红白停步标严重脱色退化为发暗冷白灰标(RedLoss=0.17)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7913: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "铁轨两侧原本生机青翠的草坡植被在LCAD生成图中大面积欠饱和脱色，褪变为枯槁发暗的土灰杂草泥地(Rsat=0.49)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "铁轨枕木与道砟石暗部略显发乌"}
        ],
        "review_note": "Double Check复核改判：核查发现：铁轨两侧青翠草坡植被大面积欠饱和脱色为枯槁土灰杂草泥地(Rsat=0.49)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7920: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "极限滑板动作画报下方青年原本鲜艳夺目的大红亮橙色运动服在LCAD生成图中严重脱色褪白，彻底退化为发脏灰白无色衣(RedLoss=0.16)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "滑板台阶背阴处略显发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：极限滑板画报青年明艳大红亮橙色运动服严重脱色褪白为灰白无色衣(RedLoss=0.16)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7931: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "停机坪行李牵引车地勤作业人员身上原本鲜艳醒目的荧光橙红色安全反光背心在LCAD生成图中完全脱色褪白，退化为灰白普通背心(RedLoss=0.17, Rsat=0.32)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "客机引擎后方停机坪水泥地面略微发暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：停机坪牵引车地勤人员荧光橙红安全反光背心完全脱色褪白(RedLoss=0.17, Rsat=0.32)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7987: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "草坡高处站立男子身上原本鲜艳纯正的大红色短袖T恤在LCAD生成图中严重欠饱和脱色，褪变为发暗脏乱的土黄旧衣(DeltaC=0.037)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "草坡青翠草地边缘略带泛黄"}
        ],
        "review_note": "Double Check复核改判：核查发现：草坡站立男子鲜艳大红短袖T恤严重欠饱和脱色为发暗土黄色(DeltaC=0.037)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7993: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "围观滑板跳跃动作的青年面部与颈口处在LCAD生成图中被恶性污染大片极其刺眼突兀的亮橙黄色伪色色斑，健康肤色严重受损(RedLoss=0.15)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "身后站立观众衣服略显泛青泛暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：围观滑板青年面部与领口处被恶性污染大片突兀亮橙黄色色斑(RedLoss=0.15)，改判错色(C-L2)与偏色(D-L1)。"
    },
    7996: {
        "defects": [
            {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "原野长颈鹿奔跑的宽阔草坪与背景生机盎然的绿化树林在LCAD生成图中大面积脱色发暗，退化为发干枯槁的枯黄土灰色调(Rsat=0.58, DeltaC=0.036)"},
            {"id": "C", "name": "错色", "severity": "L1", "description": "长颈鹿身体斑纹对比度轻微下降"}
        ],
        "review_note": "Double Check复核改判：核查发现：原野长颈鹿奔跑草坪与生机绿化树林大面积脱色为枯黄土灰色调(Rsat=0.58)，改判欠饱和(E2-L2)与错色(C-L1)。"
    },
    7998: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "玻璃花瓶中原本娇艳柔嫩的粉红色玫瑰花瓣在LCAD生成图中被恶性错涂为刺眼生硬的生菜翠绿色伪色，下方黄色小花完全脱色褪白(RedLoss=0.11)"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "左侧花瓶内粉红花簇局部略带泛紫"}
        ],
        "review_note": "Double Check复核改判：核查发现：花瓶粉红玫瑰花瓣被恶性错涂为刺目生菜翠绿色伪色，下方黄花褪白(RedLoss=0.11)，改判错色(C-L2)与偏色(D-L1)。"
    },
    7999: {
        "defects": [
            {"id": "C", "name": "错色", "severity": "L2", "description": "电线杆上原本鲜亮醒目的明黄色方形指示路牌在LCAD生成图中被恶性错涂为草绿色，人力三轮车翠绿色车厢座椅恶性错涂为橙红色(RedLoss=0.28, Rsat=0.52)，多处物体色相彻底颠覆"},
            {"id": "D", "name": "偏色", "severity": "L1", "description": "两层小洋楼白色外墙与柏油路面局部略带偏冷偏暗"}
        ],
        "review_note": "Double Check复核改判：核查发现：电线杆明黄路牌恶性错涂为草绿色，人力三轮车翠绿座椅车厢错涂为橙红色(RedLoss=0.28)，改判错色(C-L2)与偏色(D-L1)。"
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
    stream_path = STREAMS_DIR / "tasks_lcad_7501_8000_stream.json"
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
    print("Applying Double Check updates for 7501-8000...")
    
    # 1. Update batch 7501-8000
    b_path = EXPORTS_DIR / "reviewed_7501_8000_20260930_182342.json"
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

    print("Double check updates for 7501-8000 completed successfully!")

if __name__ == "__main__":
    main()
