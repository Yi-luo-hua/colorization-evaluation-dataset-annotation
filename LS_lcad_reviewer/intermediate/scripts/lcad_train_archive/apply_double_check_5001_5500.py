import json
import os
import shutil

# 28 例经过 Double Check 高清看板逐图直审锁定的改判定义
DOUBLE_CHECK_FIXES = {
    5340: {
        "defects": [
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L2",
                "description": "黄色菱形交通警示标牌上涂鸦的鲜艳亮粉红/玫红色“WAR”英文字母严重脱色发乌为暗淡土红黑灰色，红色鲜明度显著受损。"
            },
            {
                "id": "F",
                "name": "视觉自然度",
                "severity": "L1",
                "description": "标牌涂鸦英文字母发暗发灰，与鲜明黄色警示标牌背景之间形成不协调的脏浊感。"
            }
        ],
        "note": "【Double Check 具象改判】黄色菱形警示标牌上涂鸦的亮粉红“WAR”字母严重脱色发乌蜕变为暗土红黑灰色，修正欠饱和评级并明确具体文字实体。"
    },
    5152: {
        "defects": [
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L2",
                "description": "白瓷餐盘边缘摆放的切块鲜红草莓严重脱色发乌，蜕变为暗黑紫褐色与干枯暗红褐色，新鲜浆果色泽与水润感完全丧失。"
            },
            {
                "id": "F",
                "name": "视觉自然度",
                "severity": "L1",
                "description": "草莓发暗枯槁的色泽与餐盘中其他明亮早餐食物形成突兀割裂，破坏食物真实可口度。"
            }
        ],
        "note": "【Double Check 具象改判】餐盘边缘切块鲜红草莓严重脱色发乌为暗黑紫褐色，修正欠饱和评级并具象定位草莓实体。"
    },
    5115: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L3",
                "description": "复古大众面包车侧面原本的草绿色车身涂装被灾难性错涂为大面积刺目浓艳的大红色与粉红色伪色车体，完全颠覆了车辆原本的经典涂装。"
            },
            {
                "id": "F",
                "name": "视觉自然度",
                "severity": "L2",
                "description": "面包车大面积刺目粉红伪色车身与周围自然草地和树木光影严重违和，视觉突兀感极强。"
            }
        ],
        "note": "【Double Check 具象改判】原评测 4.55 分放行存在严重漏判：复古大众面包车侧面草绿色车体被恶性错涂为浓艳大红粉色伪色车身，改判定物错色(C-L3)。"
    },
    5385: {
        "defects": [
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L2",
                "description": "吉娃娃小狗身上穿戴的原本鲜艳大红色胸背带严重脱色蜕白，蜕变为暗淡发脏的浅土黄灰褐色背带。"
            },
            {
                "id": "C",
                "name": "错色",
                "severity": "L1",
                "description": "原本正红色的宠物胸背带边缘带有局部泛绿与黄褐色伪色偏移。"
            }
        ],
        "note": "【Double Check 具象改判】原评测 4.46 分漏判：吉娃娃小狗穿戴的鲜艳大红胸背带严重脱色蜕变为暗淡浅土黄灰褐色，改判定物欠饱和(E2-L2)与错色(C-L1)。"
    },
    5424: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "海浪中男子双手扶着的亮深宝蓝色冲浪板被恶性错涂为浅青绿与蓝绿色冲浪板伪色，板面原色严重失真。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L1",
                "description": "海面浪花与人物肤色受到轻微黄绿调环境色污染。"
            }
        ],
        "note": "【Double Check 具象改判】原评测 4.46 分漏判：海浪中男子所持深宝蓝色冲浪板被恶性错涂为浅青绿与蓝绿色冲浪板伪色，改判定物错色(C-L2)。"
    },
    5098: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "黑色长方形餐盘左上方摆放的原本鲜嫩粉红色方形糕点甜品被恶性错涂为浅土黄发暗米色，甜品特有色泽完全丧失。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L1",
                "description": "餐盘白色瓷盘边缘与食材高光区域带有微弱的暖黄褐色偏移。"
            }
        ],
        "note": "【Double Check 具象改判】原评测 4.46 分漏判：餐盘左上方粉红色方形糕点甜品恶性错涂为浅土黄发暗米色，改判定物错色(C-L2)。"
    },
    5201: {
        "defects": [
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L2",
                "description": "滑板少年脚下滑板底部的鲜艳红色板底图案严重脱色蜕白，蜕变为暗淡浅灰木色，图案色彩活力显著缺失。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L1",
                "description": "室内白色顶棚及滑板场地整体略带黄褐色暖调偏移。"
            }
        ],
        "note": "【Double Check 具象改判】滑板少年脚下滑板底部的鲜艳红色板底图案严重脱色蜕白为浅灰木色，改判定物欠饱和(E2-L2)。"
    },
    5272: {
        "defects": [
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L2",
                "description": "早餐木桌上盛放的鲜红草莓果酱碗与鲜艳红色果汁饮品严重脱色蜕变，蜕变为发暗灰褐色与枯焦褐色，新鲜果实色泽严重丧失。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L1",
                "description": "白色餐具和吐司高光受到轻微红褐色环境染色。"
            }
        ],
        "note": "【Double Check 具象改判】早餐木桌上盛放的鲜红草莓果酱碗与红色果汁严重脱色褪变发暗灰褐，改判定物欠饱和(E2-L2)。"
    },
    5295: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "卫生间门楣上方张贴的亮天蓝色男厕标志牌被恶性错涂为深暗黑褐色标牌，标识原有明亮指引性色彩彻底丧失。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L1",
                "description": "门体略带浅紫红调，右侧墙壁略显发青，局部色调不够平衡。"
            }
        ],
        "note": "【Double Check 具象改判】门楣上方亮天蓝色男厕标志牌恶性错涂为深暗黑褐色标牌，改判定物错色(C-L2)。"
    },
    5209: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L3",
                "description": "海边石滩上行走的原本纯白色北极熊全身皮毛被恶性错涂为发脏发粉的红褐色与棕褐色伪色，将北极熊严重误涂为棕熊外貌。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L2",
                "description": "北极熊皮毛与周围浅色岩石石滩受到强烈的红粉色调色斑污染。"
            },
            {
                "id": "F",
                "name": "视觉自然度",
                "severity": "L2",
                "description": "北极熊皮毛异常的红褐色与极地冰原碎石滩环境严重割裂，生物学真实感完全破坏。"
            }
        ],
        "note": "【Double Check 具象改判】石滩上行走的纯白色北极熊全身被恶性错涂为发脏红褐色棕熊伪色，改判定物错色(C-L3)与偏色(D-L2)。"
    },
    5181: {
        "defects": [
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L2",
                "description": "棒球击球连续分解动作展板中小击球手佩戴的鲜艳红色棒球帽与红色球袜严重脱色发乌，蜕变为暗淡紫黑褐色与干枯深灰。"
            },
            {
                "id": "F",
                "name": "视觉自然度",
                "severity": "L1",
                "description": "运动护具与球帽色彩暗淡灰沉，缺乏少棒运动应有的饱满明快视觉质感。"
            }
        ],
        "note": "【Double Check 具象改判】棒球击球动作展板中小击球手的鲜红色棒球帽与红色球袜严重脱色发乌为暗紫黑褐色，改判定物欠饱和(E2-L2)。"
    },
    5203: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "厨房吧台右侧原本鲜艳的洋红色/紫红色艺术背景墙面被严重错涂脱色为阴暗死黑灰墙壁，原本亮眼的室内装潢主色调被彻底剥夺抹杀。"
            },
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L2",
                "description": "厨房橱柜与吧台周围区域整体色彩较为灰暗低沉，色彩饱满度明显偏低。"
            }
        ],
        "note": "【Double Check 具象改判】厨房吧台右侧洋红/紫红色艺术背景墙面严重脱色错涂为阴暗死黑灰墙壁，改判定物错色(C-L2)与欠饱和(E2-L2)。"
    },
    5306: {
        "defects": [
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L2",
                "description": "白雪覆盖街道中行人撑着的亮粉红色雨伞与儿童推车上的红色防雨罩严重脱色蜕白，蜕变为苍白浅灰白色，冰雪场景中鲜明的人工防雨色彩完全消失。"
            },
            {
                "id": "F",
                "name": "视觉自然度",
                "severity": "L1",
                "description": "雨伞与推车褪色为灰白后融入雪地背景，人物活动视觉焦点被严重削弱。"
            }
        ],
        "note": "【Double Check 具象改判】雪地中行人的亮粉红色雨伞与推车红色防雨罩严重脱色蜕变为苍白浅灰白色，改判定物欠饱和(E2-L2)。"
    },
    5220: {
        "defects": [
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L2",
                "description": "明亮窗户前悬挂的洋红粉紫色装饰布帘严重脱色褪白，蜕变为暗淡浅土灰泥色，原有的典雅紫红色彩完全剥落。"
            },
            {
                "id": "F",
                "name": "视觉自然度",
                "severity": "L1",
                "description": "窗帘布料失去色彩呈现脏灰感，与窗台周围木纹质感缺乏层次。"
            }
        ],
        "note": "【Double Check 具象改判】窗前悬挂的洋红粉紫装饰布帘严重脱色褪白为暗土灰泥色，改判定物欠饱和(E2-L2)。"
    },
    5213: {
        "defects": [
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L2",
                "description": "餐盘中热狗面包夹着的原本鲜艳红润的热狗香肠与红番茄肉酱严重脱色发乌，蜕变为暗黑紫灰色与冷灰色，肉质新鲜美味感荡然无存。"
            },
            {
                "id": "F",
                "name": "视觉自然度",
                "severity": "L1",
                "description": "热狗香肠与酱料冷灰发乌的色泽呈现非新鲜食品的暗沉视觉体验。"
            }
        ],
        "note": "【Double Check 具象改判】餐盘中热狗香肠与红番茄肉酱严重脱色发乌为暗黑紫灰色，改判定物欠饱和(E2-L2)。"
    },
    5432: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "西装革履男子胸前系着的鲜红色几何格纹领带被恶性错涂为金黄黑褐色格纹领带，领带原本亮眼的红黑对比主色调完全改变。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L2",
                "description": "人物白色衬衫、面部肤色及室内背景整体存在明显的黄褐色暖调偏移。"
            }
        ],
        "note": "【Double Check 具象改判】西装男子胸前鲜红色几何格纹领带被恶性错涂为金黄黑褐色格纹领带，改判定物错色(C-L2)。"
    },
    5064: {
        "defects": [
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L2",
                "description": "打电话年轻女士右手食指涂抹的鲜艳金橙黄色指甲油严重脱色褪白，蜕变为苍白浅灰白色，精细美甲色彩完全剥脱。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L1",
                "description": "人物面部及手部肤色整体略带偏暖偏黄偏移。"
            }
        ],
        "note": "【Double Check 具象改判】打电话年轻女士右手涂抹的鲜艳金橙黄指甲油严重脱色褪白为苍白浅灰白色，改判定物欠饱和(E2-L2)。"
    },
    5356: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "客厅背景原本鲜艳的翠绿/薄荷绿艺术墙壁被恶性错涂为灰暗冰冷的金属蓝灰色与冷灰色墙壁，原本清新的空间氛围被彻底改变。"
            },
            {
                "id": "E1",
                "name": "过饱和",
                "severity": "L2",
                "description": "前景皮质单人沙发呈现刺目浓烈的高饱和纯蓝色，与背景灰冷墙面搭配突兀。"
            },
            {
                "id": "F",
                "name": "视觉自然度",
                "severity": "L2",
                "description": "蓝色沙发的浓重艳丽与灰冷背景墙壁形成生硬割裂，室内光影与色彩搭配极不协调。"
            }
        ],
        "note": "【Double Check 具象改判】客厅背景翠绿/薄荷绿艺术墙面被恶性错涂为灰暗金属蓝灰色，改判定物错色(C-L2)。"
    },
    5493: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L3",
                "description": "绿茵草坪上玩耍的小女孩身上穿戴的亮粉红色无袖连衣裙被恶性错涂为深浅不均的紫青色与冷蓝色连衣裙伪色，服饰主色调发生颠覆性错变。"
            },
            {
                "id": "E1",
                "name": "过饱和",
                "severity": "L2",
                "description": "草坪大面积绿色饱和度过高且呈现不自然的刺目荧光感。"
            },
            {
                "id": "F",
                "name": "视觉自然度",
                "severity": "L2",
                "description": "女孩紫蓝裙子、高亮泛白建筑与荧光草坪之间色彩反差极其割裂怪异。"
            }
        ],
        "note": "【Double Check 具象改判】草坪上小女孩身穿的亮粉红色无袖连衣裙被恶性错涂为紫青色与冷蓝色伪色裙，改判定物错色(C-L3)。"
    },
    5293: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "烤架上方放置的储物盒塑料盒盖原本为鲜亮洋红色/粉红色，被恶性错涂为浓重突兀的荧光蓝紫色与深蓝色伪色。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L2",
                "description": "金属烤架、台面及餐具整体带有明显的红紫色偏色污染。"
            }
        ],
        "note": "【Double Check 具象改判】烤架上方储物盒洋粉红色塑料盒盖被恶性错涂为浓重荧光蓝紫色伪色盖，改判定物错色(C-L2)。"
    },
    5061: {
        "defects": [
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L3",
                "description": "停车架上锁着的公路自行车原本极其鲜艳夺目的洋红粉色车架涂装发生大面积恶性脱色褪白，蜕变为暗淡发脏的灰青蓝色与铁灰色。"
            },
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "自行车车架及牙盘链条区域被错误涂抹上不均匀的黄绿与灰青色伪色色斑。"
            },
            {
                "id": "F",
                "name": "视觉自然度",
                "severity": "L2",
                "description": "洋红涂装严重褪色与车轮蓝紫残色拼合突兀，导致整车机械质感极不协调。"
            }
        ],
        "note": "【Double Check 具象改判】公路自行车极其鲜艳纯正的洋红粉色车架涂装恶性脱色蜕变泛脏灰青蓝色，改判定物欠饱和(E2-L3)与错色(C-L2)。"
    },
    5054: {
        "defects": [
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L2",
                "description": "厨房水槽下方毛巾架上悬挂的鲜艳大红条纹洗碗布/擦手巾严重脱色蜕白，蜕变为暗淡浅灰白色，红色装饰条纹完全剥落。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L2",
                "description": "木质橱柜与室内墙壁整体偏黄绿，窗外树林景物带有明显的蓝紫色偏移。"
            }
        ],
        "note": "【Double Check 具象改判】水槽下方毛巾架上挂置的鲜艳大红擦手巾严重脱色蜕变为暗灰白色，改判定物欠饱和(E2-L2)。"
    },
    5140: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "面包店柜台后忙碌的年轻男子身上所穿鲜艳大红色长袖工作服被恶性错涂为灰冷深蓝灰色，原本醒目的红色着装被彻底剥夺。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L2",
                "description": "烘焙坊柜台、天花板及展示橱窗整体呈现明显的黄绿色偏色，色调沉闷浑浊。"
            },
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L2",
                "description": "除局部糕点外，店内大面积环境饱和度明显偏低。"
            }
        ],
        "note": "【Double Check 具象改判】面包店柜台后男子身穿的鲜艳大红色长袖工作服被恶性错涂为灰冷深蓝灰色，改判定物错色(C-L2)。"
    },
    5100: {
        "defects": [
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L2",
                "description": "趴在冲浪板女士身下原本清澈透亮的碧绿色泳池/海滩水体严重脱色蜕变，蜕变为发暗浑浊的浅灰白死水质感，热带度假水域清澈生机完全丧失。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L2",
                "description": "两名女士面部与躯干肤色偏橙红过热，与发灰冷暗的水面和建筑背景产生明显割裂。"
            }
        ],
        "note": "【Double Check 具象改判】冲浪板身下清澈碧绿的水体严重脱色蜕变为浑浊浅灰白质感，改判定物欠饱和(E2-L2)。"
    },
    5197: {
        "defects": [
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L3",
                "description": "极限碗池滑板场中飞跃少年身上穿戴的原本极其鲜艳纯正的大红色短袖T恤发生大面积恶性脱色蜕白，蜕变为苍白浅灰白色老头衫，运动着装色彩活力荡然无存。"
            },
            {
                "id": "B",
                "name": "溢色",
                "severity": "L1",
                "description": "少年手臂与身体轮廓边缘可见轻微红色外溢与青色边缘串色。"
            },
            {
                "id": "F",
                "name": "视觉自然度",
                "severity": "L2",
                "description": "上衣大面积褪色为苍白灰衫后与水泥碗池背景融混，极限运动主体视觉反差严重缺失。"
            }
        ],
        "note": "【Double Check 具象改判】极限滑板少年身上极其鲜艳纯正的大红色T恤严重脱色蜕变为苍白浅灰白色老头衫，改判定物欠饱和(E2-L3)。"
    },
    5020: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L2",
                "description": "公交站台前候车的女士身上所穿浅蓝色工作衬衫被恶性错涂为刺目洋红紫色的粉紫衬衫伪色，人物衣着色彩严重失真。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L2",
                "description": "大客车车身、车窗阴影及地面受到统一浓重的紫红色光晕污染。"
            }
        ],
        "note": "【Double Check 具象改判】站台候车女士身穿的浅蓝色工作衬衫被恶性错涂为刺目洋红紫伪色，改判定物错色(C-L2)。"
    },
    5161: {
        "defects": [
            {
                "id": "C",
                "name": "错色",
                "severity": "L3",
                "description": "圆形披萨饼面上铺满的鲜红番茄切片被恶性错涂为刺目浓绿与青绿色的青椒圈伪色，将番茄配料彻底篡改为青椒配料，破坏基本食材认知常识。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L2",
                "description": "披萨中央融化的奶酪区域带有不均匀的青绿色与黄绿色偏色斑块。"
            },
            {
                "id": "F",
                "name": "视觉自然度",
                "severity": "L2",
                "description": "红番茄被绿化篡改与奶酪发青破坏了披萨刚出炉的烘烤美味质感。"
            }
        ],
        "note": "【Double Check 具象改判】圆形披萨饼面上铺满的鲜红番茄切片被恶性错涂为刺目浓绿的青椒圈伪色，改判定物错色(C-L3)。"
    },
    5005: {
        "defects": [
            {
                "id": "E2",
                "name": "欠饱和",
                "severity": "L3",
                "description": "创意玩具包装纸卡左侧原本极其纯正鲜艳的大红色背景底板发生灾难性脱色蜕白，蜕变为几乎完全惨白的灰白无色状态，原有包装极具冲击力的鲜红版面荡然无存。"
            },
            {
                "id": "D",
                "name": "偏色",
                "severity": "L2",
                "description": "包装盒透明吸塑罩及木质背景带有发灰、发暗的冷灰调偏移。"
            },
            {
                "id": "F",
                "name": "视觉自然度",
                "severity": "L2",
                "description": "包装底卡大红完全蜕变苍白，使整体商品陈列质感宛如完全褪色的废旧废纸。"
            }
        ],
        "note": "【Double Check 具象改判】创意玩具包装纸卡原本极其纯正鲜艳的大红色背景严重脱色蜕变为惨白色，改判定物欠饱和(E2-L3)。"
    }
}

def update_batch_export():
    batch_path = "exports/reviewed_5001_5500_20260930_142848.json"
    print(f"Updating batch export: {batch_path}")
    with open(batch_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated_count = 0
    for ann in data["annotations"]:
        t_id = ann.get("human_review", {}).get("task_id")
        if t_id in DOUBLE_CHECK_FIXES:
            fix = DOUBLE_CHECK_FIXES[t_id]
            ann["defects"] = fix["defects"]
            ann["review_note"] = fix["note"]
            ann["review_status"] = "已核验"
            ann["reviewed_score"] = None
            ann["needs_rescoring"] = True
            updated_count += 1

    with open(batch_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Batch export updated successfully. Count: {updated_count}")

def update_stream():
    stream_path = "streams/tasks_lcad_5001_5500_stream.json"
    print(f"Updating stream: {stream_path}")
    with open(stream_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated_count = 0
    for item in data:
        t_id = item["data"].get("task_idx")
        if t_id in DOUBLE_CHECK_FIXES:
            fix = DOUBLE_CHECK_FIXES[t_id]
            item["data"]["review_tag"] = "洛熙视觉改判"
            item["data"]["review_note"] = fix["note"]
            item["data"]["review_status"] = "已核验"
            if "original_record" in item["data"] and "comparison" in item["data"]["original_record"]:
                item["data"]["original_record"]["comparison"]["defects"] = fix["defects"]
            updated_count += 1

    with open(stream_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Stream updated successfully. Count: {updated_count}")

def update_full_exports():
    # 过程版（保留详细 review_note）
    full_process_files = [
        "exports/reviewed_1_10000_20260930_200411.json",
        "exports/reviewed_1_10000_all.json"
    ]
    for p in full_process_files:
        if not os.path.exists(p):
            continue
        print(f"Updating process export: {p}")
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        cnt = 0
        for ann in data["annotations"]:
            t_id = ann.get("human_review", {}).get("task_id")
            if t_id in DOUBLE_CHECK_FIXES:
                fix = DOUBLE_CHECK_FIXES[t_id]
                ann["defects"] = fix["defects"]
                ann["review_note"] = fix["note"]
                ann["review_status"] = "已核验"
                ann["reviewed_score"] = None
                ann["needs_rescoring"] = True
                cnt += 1
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Updated {cnt} in {p}")

    # 纯净版（review_note 清空为 ""）
    clean_files = [
        "exports/reviewed_1_10000_clean_20260930_202516.json",
        "exports/reviewed_1_10000_clean.json"
    ]
    for p in clean_files:
        if not os.path.exists(p):
            continue
        print(f"Updating clean export: {p}")
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        cnt = 0
        for ann in data["annotations"]:
            t_id = ann.get("human_review", {}).get("task_id")
            if t_id in DOUBLE_CHECK_FIXES:
                fix = DOUBLE_CHECK_FIXES[t_id]
                ann["defects"] = fix["defects"]
                ann["review_note"] = ""
                ann["review_status"] = "已核验"
                ann["reviewed_score"] = None
                ann["needs_rescoring"] = True
                cnt += 1
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Updated {cnt} in {p}")

if __name__ == "__main__":
    update_batch_export()
    update_stream()
    update_full_exports()
    print("ALL DOUBLE CHECK UPDATES APPLIED TO 5001-5500!")
