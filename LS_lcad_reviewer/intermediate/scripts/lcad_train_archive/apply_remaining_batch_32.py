# -*- coding: utf-8 -*-
"""
应用 Batch 32 审核具象定物判决字典并双向同步至正式交付文件
Batch 32: Task #6472 ~ #6657 (共 120 组)
"""

import json
import os
import re

# 120 组人工直审与具象定物判决字典
REVIEWS_B32 = {
    # Sheet 01
    6472: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6473: {
        "score": 2.47,
        "severities": {"D": "L2", "F": "L1"},
        "note": "餐厅酒吧吧台木质台面与吊顶暗部阴影大面积浸染浓重深焦糖红黄褐色，色温过暖偏色(D-L2, F-L1)。"
    },
    6474: {
        "score": 2.43,
        "severities": {"E2": "L2", "D": "L1", "F": "L2"},
        "note": "街边停放的重型摩托车翠绿与天蓝双色金属漆面大面积严重脱色褪为苍白暗灰蓝，金属光泽受损(E2-L2, D-L1, F-L2)。"
    },
    6476: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    6478: {
        "score": 5.0,
        "severities": {"E2": "L1", "D": "L1", "F": "L1"},
        "note": "小型客机登机旅客身穿的鲜艳正红色防风外套大面积欠饱和褪色为发暗灰紫粉红(E2-L1, D-L1, F-L1)。"
    },
    6479: {
        "score": 5.0,
        "severities": {"C": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：棒球场上挥棒运动员身穿的深蓝色长袖运动上衣被严重错涂为鲜艳亮红色(C-L2, F-L1)。"
    },

    # Sheet 02
    6480: {
        "score": 1.01,
        "severities": {"C": "L3", "D": "L2", "E2": "L2", "F": "L3"},
        "note": "戴眼镜女子身穿的鲜亮紫红色衬衫颠覆性彻底脱色错涂为发暗灰白调，金黄背景墙面严重冷化失真(C-L3, D-L2, E2-L2, F-L3)。"
    },
    6481: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6484: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6485: {
        "score": 2.47,
        "severities": {"D": "L2", "F": "L1"},
        "note": "复古酒吧红砖墙面与天花板暗部阴影大面积浸染浓重深焦糖红黄褐色，色温过暖偏色(D-L2, F-L1)。"
    },
    6486: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6487: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 03
    6488: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    6489: {
        "score": 5.0,
        "severities": {"E2": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：早餐纸袋表面印制的鲜亮红色宣传大字严重脱色褪为暗灰白，纸袋整体欠饱和(E2-L2, D-L1, F-L1)。"
    },
    6490: {
        "score": 2.61,
        "severities": {},
        "note": "审查通过"
    },
    6491: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6492: {
        "score": 4.55,
        "severities": {"D": "L2", "E1": "L1", "F": "L2"},
        "note": "体感游戏男玩家身穿的红色条纹短袖T恤与室内白墙大面积严重偏向浓艳的深焦糖红黄调，过饱和偏色(D-L2, E1-L1, F-L2)。"
    },
    6494: {
        "score": 5.0,
        "severities": {"D": "L1", "F": "L1"},
        "note": "面包房墨绿色木质复古门面与金黄色招牌文字大面积泛发暗草绿黄偏色，色调沉稳感略有受损(D-L1, F-L1)。"
    },

    # Sheet 04
    6495: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6496: {
        "score": 1.06,
        "severities": {"D": "L2", "E1": "L1", "F": "L2"},
        "note": "大象群身后茂密深绿丛林大面积严重偏向浓艳的枯草焦黄与暖黄褐色，绿意受损过饱和(D-L2, E1-L1, F-L2)。"
    },
    6497: {
        "score": 2.47,
        "severities": {},
        "note": "审查通过"
    },
    6499: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6502: {
        "score": 5.0,
        "severities": {"E2": "L1", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：雨天街头行人撑开的鲜艳大红雨伞大面积欠饱和严重脱色褪为发暗肉粉灰(E2-L1, D-L1, F-L1)。"
    },
    6503: {
        "score": 5.0,
        "severities": {"E2": "L2", "D": "L1", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：小男孩手中制作的彩色菱形风筝彩纸与串旗大面积欠饱和严重脱色褪为暗灰，色泽鲜活感丧失(E2-L2, D-L1, F-L2)。"
    },

    # Sheet 05
    6504: {
        "score": 2.61,
        "severities": {},
        "note": "审查通过"
    },
    6505: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6506: {
        "score": 5.0,
        "severities": {"D": "L2", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：床上小狗身下的浅蓝色床单大面积浸染浓重深紫色与青紫假色伪色(D-L2, F-L2)。"
    },
    6513: {
        "score": 2.14,
        "severities": {"C": "L3", "D": "L2", "E1": "L2", "F": "L3"},
        "note": "厨房深绿色橡胶切割垫板被颠覆性严重错涂为大面积浓烈刺目的深焦糖朱红褐色，严重错色失真(C-L3, D-L2, E1-L2, F-L3)。"
    },
    6514: {
        "score": 2.73,
        "severities": {},
        "note": "审查通过"
    },
    6515: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 06
    6518: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6519: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6520: {
        "score": 2.43,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "老式公交车奶油白与暗红车漆表面及街道背景大面积浸染浓重深焦糖红黄褐色，过饱和偏色(D-L2, E1-L2, F-L2)。"
    },
    6521: {
        "score": 2.32,
        "severities": {"D": "L2", "E2": "L1", "F": "L2"},
        "note": "卧室双人床大红床单与米黄色墙面大面积偏向阴冷发青暗冷蓝灰调，暖光氛围冷化受损(D-L2, E2-L1, F-L2)。"
    },
    6522: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6524: {
        "score": 2.56,
        "severities": {"D": "L2", "F": "L2"},
        "note": "客厅窗台白纱窗帘与上方墙面大面积泛起浓重刺目的深紫罗兰冷紫伪色杂光(D-L2, F-L2)。"
    },

    # Sheet 07
    6525: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6526: {
        "score": 2.34,
        "severities": {},
        "note": "审查通过"
    },
    6530: {
        "score": 5.0,
        "severities": {"E1": "L1", "D": "L1", "F": "L1"},
        "note": "沙滩奔跑小狗嘴里叼着的红绿拼色飞盘玩具边缘颜色过度浓艳偏刺目，过饱和失真(E1-L1, D-L1, F-L1)。"
    },
    6531: {
        "score": 5.0,
        "severities": {"C": "L3", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：小男孩身穿的黑白灰横条纹上衣与黑色长裤被严重错涂为鲜艳亮蓝色条纹衫与亮红色长裤(C-L3, F-L2)。"
    },
    6532: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6533: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 08
    6534: {
        "score": 2.73,
        "severities": {"E2": "L1", "D": "L1", "F": "L1"},
        "note": "红绿灯树艺术雕塑上点亮的红黄绿交通信号灯大面积欠饱和褪色发暗，灯光点亮感减弱(E2-L1, D-L1, F-L1)。"
    },
    6535: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6537: {
        "score": 2.56,
        "severities": {"E2": "L2", "D": "L1", "F": "L1"},
        "note": "草坪上吹泡泡小女孩身穿的鲜红短袖T恤大面积严重欠饱和脱色褪为暗灰肉粉色(E2-L2, D-L1, F-L1)。"
    },
    6538: {
        "score": 4.17,
        "severities": {},
        "note": "审查通过"
    },
    6540: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6547: {
        "score": 1.01,
        "severities": {"C": "L3", "D": "L1", "E1": "L3", "F": "L3"},
        "note": "草地上两匹棕马的马头、马鬃与背部被颠覆性荒谬错涂为极其刺目的荧光亮天蓝色与紫红伪色，严重失真(C-L3, D-L1, E1-L3, F-L3)。"
    },

    # Sheet 09
    6548: {
        "score": 2.73,
        "severities": {"C": "L2", "D": "L1", "E2": "L2", "F": "L2"},
        "note": "陶瓷马桶周边的生机翠绿草坪大面积严重脱色错涂为发暗灰白泥土地，环境生机受损(C-L2, D-L1, E2-L2, F-L2)。"
    },
    6552: {
        "score": 5.0,
        "severities": {"E2": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：老式电脑显示器屏幕上原本鲜艳发光的幽蓝人脸图像大面积欠饱和褪色为暗黑灰白(E2-L2, D-L1, F-L1)。"
    },
    6553: {
        "score": 5.0,
        "severities": {"E2": "L2", "D": "L1", "F": "L2"},
        "note": "原5.0满分严重漏检，核查发现：庭院木桌后方茂密翠绿的树冠灌木大面积欠饱和严重褪色发暗，丧失生机活力(E2-L2, D-L1, F-L2)。"
    },
    6554: {
        "score": 4.46,
        "severities": {"E1": "L2", "D": "L1", "F": "L1"},
        "note": "雪地上弯腰男子身穿的长裤被涂抹上过于浓艳刺目的亮海藻绿色，过饱和失真(E1-L2, D-L1, F-L1)。"
    },
    6556: {
        "score": 2.17,
        "severities": {"D": "L2", "E2": "L1", "F": "L2"},
        "note": "书桌上原本鲜亮橙红的书籍封面大面积褪色偏向发暗阴冷青灰调，暖光氛围冷化失真(D-L2, E2-L1, F-L2)。"
    },
    6557: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 10
    6562: {
        "score": 2.17,
        "severities": {"D": "L2", "E2": "L1", "F": "L1"},
        "note": "海滩蓝白遮阳伞下的金黄沙滩大面积欠饱和褪色偏向暗冷青灰调，阳光沙滩活力受损(D-L2, E2-L1, F-L1)。"
    },
    6564: {
        "score": 2.47,
        "severities": {"D": "L2", "E1": "L1", "F": "L1"},
        "note": "酒吧品酒女士面部肤色及背景橡木酒桶大面积浸染浓重深焦糖红黄褐色，过饱和偏色(D-L2, E1-L1, F-L1)。"
    },
    6565: {
        "score": 4.46,
        "severities": {},
        "note": "审查通过"
    },
    6566: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6567: {
        "score": 2.47,
        "severities": {"E2": "L2", "D": "L1", "F": "L1"},
        "note": "卫生间下半部浅蓝色装饰瓷砖大面积严重脱色褪为发暗青灰白，清爽瓷砖质感丧失(E2-L2, D-L1, F-L1)。"
    },
    6568: {
        "score": 2.43,
        "severities": {"D": "L2", "E1": "L1", "F": "L2"},
        "note": "棒球场翠绿草坪与红褐跑道大面积浸染浓重焦糖红黄偏色，后方蓝色广告牌泛紫失真(D-L2, E1-L1, F-L2)。"
    },

    # Sheet 11
    6571: {
        "score": 2.14,
        "severities": {},
        "note": "审查通过"
    },
    6572: {
        "score": 2.47,
        "severities": {},
        "note": "审查通过"
    },
    6573: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6574: {
        "score": 1.01,
        "severities": {"C": "L3", "D": "L2", "E2": "L2", "F": "L3"},
        "note": "塑料杯中原本清亮诱人的金黄色啤酒被颠覆性错涂为浑浊发黑的深紫暗灰色液体，严重错色失真(C-L3, D-L2, E2-L2, F-L3)。"
    },
    6575: {
        "score": 2.61,
        "severities": {},
        "note": "审查通过"
    },
    6576: {
        "score": 4.46,
        "severities": {"C": "L3", "D": "L2", "E2": "L2", "F": "L2"},
        "note": "酒店客房双人床上原本温暖明亮的金黄色床单被褥彻底脱色错涂为冰冷暗淡的灰白床单，暖光氛围冷化(C-L3, D-L2, E2-L2, F-L2)。"
    },

    # Sheet 12
    6577: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6578: {
        "score": 5.0,
        "severities": {"D": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：拼贴数字生日蛋糕白色糖霜边缘及周围阴影大面积泛发暗冷青蓝与深紫伪色杂光(D-L2, F-L1)。"
    },
    6579: {
        "score": 2.47,
        "severities": {"D": "L2", "F": "L2"},
        "note": "手持虎牌啤酒玻璃瓶瓶身与酒标区域大面积泛起浓重刺目的深紫罗兰冷紫伪色杂斑(D-L2, F-L2)。"
    },
    6580: {
        "score": 1.07,
        "severities": {"D": "L2", "E1": "L1", "F": "L2"},
        "note": "大象背上红裙女子及象皮表面大面积浸染浓重深焦糖红黄褐色，天空与树木色调严重过暖偏色(D-L2, E1-L1, F-L2)。"
    },
    6582: {
        "score": 2.56,
        "severities": {"E1": "L2", "D": "L1", "F": "L1"},
        "note": "奔跑黑马身上披着的红黄条纹马衣饱和度过度浓艳偏刺目荧光红，周围泛发暗色偏(E1-L2, D-L1, F-L1)。"
    },
    6583: {
        "score": 2.25,
        "severities": {"D": "L2", "F": "L2"},
        "note": "篮球场上防守球员白色无袖球衣及背景木板墙暗处大面积泛发暗冷紫与青蓝阴影伪色(D-L2, F-L2)。"
    },

    # Sheet 13
    6584: {
        "score": 5.0,
        "severities": {"D": "L2", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：抱热狗小女孩身穿的鲜艳玫红羽绒服大面积泛发暗暖橙红黄偏色，色相偏移失真(D-L2, F-L1)。"
    },
    6586: {
        "score": 4.17,
        "severities": {},
        "note": "审查通过"
    },
    6587: {
        "score": 2.17,
        "severities": {"D": "L2", "F": "L2"},
        "note": "发光液晶电视屏幕周围墙面与暗部阴影大面积浸染浓重深紫罗兰与冷青蓝伪色杂斑(D-L2, F-L2)。"
    },
    6588: {
        "score": 2.47,
        "severities": {},
        "note": "审查通过"
    },
    6591: {
        "score": 2.47,
        "severities": {"D": "L2", "E1": "L2", "F": "L2"},
        "note": "餐盘中原味糖霜甜甜圈表面大面积浸染浓艳刺目的深焦糖橙红暖调，过饱和偏色(D-L2, E1-L2, F-L2)。"
    },
    6592: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 14
    6593: {
        "score": 2.61,
        "severities": {"D": "L2", "E2": "L1", "F": "L2"},
        "note": "室内体感游戏男玩家宝蓝短袖欠饱和发暗，右侧木门及地面大面积浸染深紫冷紫假色(D-L2, E2-L1, F-L2)。"
    },
    6594: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6595: {
        "score": 2.61,
        "severities": {"D": "L2", "F": "L2"},
        "note": "雪地上奔跑黑狗身下的大面积雪原与远景天空大面积偏向浓重阴冷的青蓝冷紫调(D-L2, F-L2)。"
    },
    6596: {
        "score": 2.47,
        "severities": {},
        "note": "审查通过"
    },
    6598: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6599: {
        "score": 5.0,
        "severities": {"E2": "L1", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：夜景双层巴士车身原本鲜明的金黄色涂装线条大面积严重脱色褪为暗灰白色(E2-L1, D-L1, F-L1)。"
    },

    # Sheet 15
    6600: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6603: {
        "score": 1.06,
        "severities": {"D": "L2", "E2": "L2", "F": "L3"},
        "note": "沙漠履带装甲车金黄沙漠迷彩车身大面积偏向发暗阴冷青蓝灰与暗紫调，沙漠戈壁色温严重失真(D-L2, E2-L2, F-L3)。"
    },
    6606: {
        "score": 2.36,
        "severities": {},
        "note": "审查通过"
    },
    6607: {
        "score": 2.47,
        "severities": {},
        "note": "审查通过"
    },
    6609: {
        "score": 4.46,
        "severities": {"C": "L3", "E2": "L2", "D": "L1", "F": "L2"},
        "note": "戴眼镜男士身穿的鲜亮正红色斯坦福印花运动卫衣颠覆性脱色错涂为发暗灰绿泥土色，严重错色失真(C-L3, E2-L2, D-L1, F-L2)。"
    },
    6610: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },

    # Sheet 16
    6611: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6612: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6613: {
        "score": 1.05,
        "severities": {},
        "note": "审查通过"
    },
    6614: {
        "score": 5.0,
        "severities": {"C": "L2", "E2": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：青年男子额头上佩戴的鲜红运动发带大面积被错涂为刺目的黄绿色发带，胸前红带欠饱和(C-L2, E2-L1, F-L1)。"
    },
    6615: {
        "score": 2.43,
        "severities": {},
        "note": "审查通过"
    },
    6618: {
        "score": 2.43,
        "severities": {"C": "L3", "D": "L2", "E2": "L2", "F": "L3"},
        "note": "黑猫仰躺的沙发上铺着的鲜亮黄绿色碎花毛毯彻底脱色错涂为冰冷暗淡的灰白冷调，严重失真(C-L3, D-L2, E2-L2, F-L3)。"
    },

    # Sheet 17
    6619: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6621: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6623: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6624: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6626: {
        "score": 2.47,
        "severities": {"D": "L1", "F": "L1"},
        "note": "卫生间墙面上张贴的鲜亮大红十字急救标识大面积泛发暗暖橙红黄偏色，色相轻微偏移(D-L1, F-L1)。"
    },
    6629: {
        "score": 2.12,
        "severities": {"D": "L2", "F": "L2"},
        "note": "街道上遛狗男青年身穿的深色短袖T恤胸前大面积泛起浓重刺目的深紫罗兰冷紫伪色杂斑(D-L2, F-L2)。"
    },

    # Sheet 18
    6630: {
        "score": 2.61,
        "severities": {},
        "note": "审查通过"
    },
    6631: {
        "score": 1.02,
        "severities": {"D": "L2", "F": "L2"},
        "note": "黑熊身后茂密树枝灌木大面积泛起浓重发暗的深紫假色与异常杂色光晕(D-L2, F-L2)。"
    },
    6632: {
        "score": 4.55,
        "severities": {},
        "note": "审查通过"
    },
    6633: {
        "score": 5.0,
        "severities": {"C": "L2", "D": "L1", "F": "L1"},
        "note": "原5.0满分严重漏检，核查发现：露台聚餐男青年身穿的鲜亮大红色短袖T恤被严重错涂为发暗的深焦糖棕橙色(C-L2, D-L1, F-L1)。"
    },
    6636: {
        "score": 2.47,
        "severities": {},
        "note": "审查通过"
    },
    6637: {
        "score": 1.15,
        "severities": {"C": "L3", "E2": "L2", "D": "L1", "F": "L2"},
        "note": "路边停放的三轮货车原本鲜明醒目的明黄色金属车架颠覆性彻底脱色错涂为发暗青灰黑调，严重错色失真(C-L3, E2-L2, D-L1, F-L2)。"
    },

    # Sheet 19
    6639: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6640: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6641: {
        "score": 1.0,
        "severities": {},
        "note": "审查通过"
    },
    6642: {
        "score": 2.3,
        "severities": {},
        "note": "审查通过"
    },
    6643: {
        "score": 2.43,
        "severities": {"D": "L2", "E1": "L1", "F": "L2"},
        "note": "牵手两人身穿的清爽水洗浅蓝牛仔裤被涂抹上过于浓艳刺目的深海蓝与冷靛蓝调，过饱和偏色(D-L2, E1-L1, F-L2)。"
    },
    6645: {
        "score": 2.17,
        "severities": {"D": "L2", "E1": "L1", "F": "L2"},
        "note": "骑马小男孩身穿的白色短袖与骏马皮毛大面积浸染浓重刺目的深焦糖红黄褐色，过饱和偏暖(D-L2, E1-L1, F-L2)。"
    },

    # Sheet 20
    6647: {
        "score": 2.47,
        "severities": {},
        "note": "审查通过"
    },
    6648: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6649: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6652: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    },
    6656: {
        "score": 1.08,
        "severities": {"C": "L2", "D": "L1", "E1": "L2", "F": "L2"},
        "note": "棒球场挥棒男子身穿的深黑色短袖T恤被严重错涂为刺目亮宝蓝色，草坪过饱和偏向浓艳金黄(C-L2, D-L1, E1-L2, F-L2)。"
    },
    6657: {
        "score": 5.0,
        "severities": {},
        "note": "审查通过"
    }
}

DEFECT_NAME_MAP = {
    "A": "缺色",
    "B": "溢色",
    "C": "错色",
    "D": "偏色",
    "E1": "过饱和",
    "E2": "欠饱和",
    "F": "视觉自然度"
}

def build_defect_list(severities, note):
    """根据严重度字典与定物描述构建标准 defects 列表"""
    defects = []
    clean_desc = re.sub(r"[\(（][A-Z0-9\s,\-]+[\)）]", "", note).strip()
    clean_desc = re.sub(r"【.*?】", "", clean_desc).strip()
    clean_desc = re.sub(r"^原5\.0满分严重漏检，核查发现：", "", clean_desc).strip()

    order = ["A", "B", "C", "D", "E1", "E2", "F"]
    for d_id in order:
        if d_id in severities:
            sev = severities[d_id]
            defects.append({
                "id": d_id,
                "name": DEFECT_NAME_MAP[d_id],
                "severity": "" if d_id == "A" else sev,
                "description": clean_desc
            })
    return defects

def validate_reviews(reviews):
    """前置强校验：确保断言 100% 通过"""
    print(f"[*] 开始断言校验 Batch 32 定物判决字典 (共 {len(reviews)} 组)...")
    assert len(reviews) == 120, f"任务数不为 120: {len(reviews)}"

    abstract_words = ["关键区域", "某些区域", "局部区域", "特定区域", "局部关键", "整体区域"]

    for tid, r in reviews.items():
        sevs = r["severities"]
        note = r["note"]

        # 1. 抽象代词断言
        for word in abstract_words:
            assert word not in note, f"Task #{tid} 违规包含抽象代词 '{word}': {note}"

        # 2. 互斥断言 E1 / E2
        assert not ("E1" in sevs and "E2" in sevs), f"Task #{tid} 同时存在互斥标签 E1 和 E2!"

        # 3. 缺色 A 断言
        if "A" in sevs:
            assert sevs["A"] == "", f"Task #{tid} 缺色 A 的 severity 必须为 ''，实际为 '{sevs['A']}'"

        # 4. 放行断言
        if not sevs:
            assert note == "审查通过", f"Task #{tid} 无缺陷但 note 不为 '审查通过': {note}"

    print("[PASS] 100% 规则契约与反抽象代词断言核验通过！")

def main():
    validate_reviews(REVIEWS_B32)

    base_dir = r"d:\学业文件\MCL\上色评价_数据集标注\LS_lcad_reviewer"
    intermediate_dir = os.path.join(base_dir, "intermediate")
    all_export_path = os.path.join(base_dir, "exports", "reviewed_1_10000_all.json")
    clean_export_path = os.path.join(base_dir, "exports", "reviewed_1_10000_clean.json")
    grounding_out_path = os.path.join(intermediate_dir, "audits", "grounding_remaining_batch_32.json")

    # 1. 导出中间定物字典
    with open(grounding_out_path, "w", encoding="utf-8") as f:
        json.dump(REVIEWS_B32, f, ensure_ascii=False, indent=2)
    print(f"[+] 导出中间定物字典 -> {grounding_out_path}")

    # 2. 读取两份全量导出文件并同步更新
    with open(all_export_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)
    with open(clean_export_path, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    all_tasks = all_data["annotations"]
    clean_tasks = clean_data["annotations"]

    updated_count = 0
    pass_count = 0
    fail_count = 0
    a_melt_count = 0

    for tid, r in REVIEWS_B32.items():
        idx = tid - 1  # 1-based to 0-based
        sevs = r["severities"]
        note = r["note"]
        defects = build_defect_list(sevs, note)

        # 确定 review_note
        if not sevs:
            all_note = "审查通过"
            pass_count += 1
        else:
            all_note = note
            fail_count += 1
            if "A" in sevs:
                a_melt_count += 1

        is_a_melt = ("A" in sevs)
        reviewed_score = 1.0 if is_a_melt else None
        needs_rescoring = False if is_a_melt else True

        # 更新 all_tasks
        item_all = all_tasks[idx]
        item_all["defects"] = defects
        item_all["review_status"] = "已核验"
        item_all["review_note"] = all_note
        item_all["reviewed_score"] = reviewed_score
        item_all["needs_rescoring"] = needs_rescoring

        # 更新 clean_tasks (纯净交付版 review_note 统一为 "")
        item_clean = clean_tasks[idx]
        item_clean["defects"] = defects
        item_clean["review_status"] = "已核验"
        item_clean["review_note"] = ""
        item_clean["reviewed_score"] = reviewed_score
        item_clean["needs_rescoring"] = needs_rescoring

        updated_count += 1

    print(f"[*] 成功更新 {updated_count} 组任务！放行通过: {pass_count} 组，改判扣分: {fail_count} 组（其中缺色A熔断: {a_melt_count} 组）")

    # 写回文件
    with open(all_export_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"[+] 写回全量详细交付文件 -> {all_export_path}")

    with open(clean_export_path, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"[+] 写回全量纯净交付文件 -> {clean_export_path}")

if __name__ == "__main__":
    main()
