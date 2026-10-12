# -*- coding: utf-8 -*-
"""
Part 1: Groundings for Sheet 01 ~ Sheet 10 (Tasks 1 to 60) for batch 9501~10000
"""

GROUNDINGS_PART1 = {
    # === SHEET 01 ===
    9565: {
        "score": 2.75,
        "defects": [
            {"category": "C", "level": "L2", "description": "背景墙面与餐桌白桌布整体严重烘烤泛黄发暗偏暖红黄调"},
            {"category": "E1", "level": "L2", "description": "餐桌餐具与墙壁局部过饱和发焦失真"}
        ],
        "review_notes": "室内餐桌原本洁净清爽的冷白墙面与白桌布被严重烘烤发黄发暗，偏暖红黄调过饱和，原评5.0误判。"
    },
    9634: {
        "score": 1.65,
        "defects": [
            {"category": "B", "level": "L3", "description": "羊圈男子深青灰色工作服外套恶性错色为刺目紫红褐红上衣偏暖红黄调"},
            {"category": "C", "level": "L2", "description": "背景砖墙与草料大面积烘烤泛暗黄"}
        ],
        "review_notes": "农场羊圈抱羊男子原本深青灰色工作服外套被灾难性错涂为刺目紫红褐红上衣，原评5.0纯属虚标。"
    },
    9633: {
        "score": 2.20,
        "defects": [
            {"category": "F", "level": "L2", "description": "笔记本电脑屏幕与桌面操作台轮廓严重溢色偏暖红黄调"},
            {"category": "E1", "level": "L2", "description": "桌面各处局部过饱和发暗发焦"}
        ],
        "review_notes": "笔记本电脑清爽壁纸与桌面被强行错涂泛黄发暗，桌面甚至溢出刺目杂色，溢色比1.70。"
    },
    9902: {
        "score": 1.55,
        "defects": [
            {"category": "B", "level": "L3", "description": "后方原本鲜艳大红色的毛绒泰迪熊玩偶恶性错色为阴冷死黑深炭灰色偏冷青蓝调"},
            {"category": "F", "level": "L2", "description": "前排白熊爱心领结轮廓严重溢色"}
        ],
        "review_notes": "后方泰迪熊玩偶原本通体鲜艳大红色，被模型彻底剥夺红色错涂为阴冷死黑炭灰色，原评5.0极其荒唐。"
    },
    9670: {
        "score": 1.70,
        "defects": [
            {"category": "B", "level": "L3", "description": "地毯上玩耍小孩身穿的深墨绿色外套恶性错色为深宝蓝色冷青蓝外套偏冷青蓝调"},
            {"category": "C", "level": "L2", "description": "地面地毯阴影大面积偏冷青蓝发乌"}
        ],
        "review_notes": "地毯上小男孩身穿的深墨绿外套被完全错涂为深宝蓝色，原评5.0严重失真。"
    },
    9727: {
        "score": 2.80,
        "defects": [
            {"category": "C", "level": "L2", "description": "卫生间天花板与上部墙面大面积泛黄烘烤偏暖红黄调"},
            {"category": "E1", "level": "L1", "description": "深绿瓷砖墙面混杂暖棕发脏局部过饱和"}
        ],
        "review_notes": "卫生间原本清爽的绿瓷砖与白色天花板被整体烘烤泛黄泛焦，偏暖红黄调，原评5.0误判。"
    },

    # === SHEET 02 ===
    9729: {
        "score": 1.65,
        "defects": [
            {"category": "B", "level": "L3", "description": "吃热狗男孩身穿的清新草绿色短袖T恤恶性脱色为惨白死灰泛冷衣服偏冷青蓝调"},
            {"category": "E2", "level": "L2", "description": "人物衣物与背景局部严重欠饱和"}
        ],
        "review_notes": "吃热狗男孩左肩原本清新的草绿色短袖T恤被模型彻底脱色漂白为惨白死灰色，原评5.0纯属误判。"
    },
    9943: {
        "score": 1.65,
        "defects": [
            {"category": "B", "level": "L3", "description": "行李箱内上方正中间折叠纯黑色衣物恶性错色为刺目鲜艳橙红棕黄色偏暖红黄调"},
            {"category": "C", "level": "L2", "description": "箱体内衬布料大面积偏暖烘烤"}
        ],
        "review_notes": "行李箱内上方纯黑色的折叠衣物竟然被强行错涂成刺目橙红棕黄色，原评5.0彻底误判。"
    },
    9555: {
        "score": 2.40,
        "defects": [
            {"category": "F", "level": "L2", "description": "STOP停止标志牌立柱与底座轮廓严重溢色溢出冷蓝光"},
            {"category": "E2", "level": "L2", "description": "立柱下方红白相间反光警示斜条纹红色严重脱色"}
        ],
        "review_notes": "夜间STOP标志立柱下方鲜艳红白相间的反光警示条纹红色完全丢失脱色，立柱轮廓溢色严重，原评5.0误判。"
    },
    9969: {
        "score": 2.70,
        "defects": [
            {"category": "C", "level": "L2", "description": "水果摊前排成熟金黄香蕉严重脱色发暗偏冷青蓝调"},
            {"category": "E2", "level": "L2", "description": "香蕉果皮局部严重欠饱和发青灰"}
        ],
        "review_notes": "水果摊前排新鲜金黄香蕉严重脱色泛青泛乌，原有成熟金黄色泽完全丧失，原评5.0误判。"
    },
    9501: {
        "score": 1.60,
        "defects": [
            {"category": "B", "level": "L3", "description": "路边摊小贩身穿的灰白色棉服外套恶性错色为刺目大红色防寒服偏暖红黄调"},
            {"category": "E1", "level": "L2", "description": "棉服大红色局部过饱和刺目破坏画面真实感"}
        ],
        "review_notes": "席地而坐的路边摊小贩原本穿普通灰白棉服外套，竟然被强行错涂为鲜艳刺目大红防寒服，原评2.17偏高。"
    },
    9509: {
        "score": 2.10,
        "defects": [
            {"category": "E1", "level": "L3", "description": "手部皮肤严重过饱和烘烤呈现刺目焦黄红橙色"},
            {"category": "C", "level": "L2", "description": "桌面白纸与背景整体严重偏暖红黄调"}
        ],
        "review_notes": "手部皮肤被烘烤得如烤焦面包呈现刺目焦黄红橙色，过饱和比高达4.21，桌面白纸严重泛黄。"
    },

    # === SHEET 03 ===
    9542: {
        "score": 2.60,
        "defects": [
            {"category": "C", "level": "L2", "description": "卧室床单被褥与墙壁整体严重烘烤泛红发暖偏暖红黄调"},
            {"category": "E1", "level": "L2", "description": "床单与室内环境局部过饱和发暗发焦"}
        ],
        "review_notes": "卧室内原本清爽自然的冷调光线与白被褥被全盘烘烤泛红发暖，过饱和比2.04。"
    },
    9616: {
        "score": 2.20,
        "defects": [
            {"category": "B", "level": "L3", "description": "客厅单人扶手椅原本淡灰浅绿恶性错色为暖棕褐色布艺椅"},
            {"category": "E1", "level": "L2", "description": "全屋墙面极度过饱和烘烤为焦糖暖黄色偏暖红黄调"}
        ],
        "review_notes": "客厅右侧单人扶手椅原本淡灰浅绿色被剥夺错涂为暖棕褐色，全屋墙面极度过饱和烘烤为焦糖黄色。"
    },
    9659: {
        "score": 2.20,
        "defects": [
            {"category": "B", "level": "L3", "description": "床上哈士奇雪橇犬原本冷灰黑白相间毛发恶性错色为焦黄暖棕黄色毛发偏暖红黄调"},
            {"category": "E1", "level": "L2", "description": "狗狗毛发与床品局部过饱和烘烤失真"}
        ],
        "review_notes": "床上两只哈士奇雪橇犬自然的冷灰黑白毛发被错涂为刺目焦黄暖棕毛发，烘烤严重。"
    },
    9699: {
        "score": 1.55,
        "defects": [
            {"category": "B", "level": "L3", "description": "卫生间白色马桶与陶瓷面被全盘烘烤错色为发脏恶心的土黄焦黄色偏暖红黄调"},
            {"category": "E2", "level": "L2", "description": "R2D2机器人垃圾桶顶盖宝蓝色严重脱色发乌"}
        ],
        "review_notes": "纯白马桶与墙面被全盘烘烤为发脏土黄焦褐色，R2D2机器人宝蓝顶盖严重脱色，偏色Delta_C高达0.24。"
    },
    9919: {
        "score": 2.70,
        "defects": [
            {"category": "E2", "level": "L2", "description": "理发师手部皮肤严重脱色苍白泛青缺乏自然血色"},
            {"category": "F", "level": "L1", "description": "手指与理发工具边缘轮廓轻度溢色偏暖红黄调"}
        ],
        "review_notes": "理发师双手原本健康红润的深色皮肤严重脱色泛青苍白，工具边缘溢色，原评5.0误判。"
    },
    9948: {
        "score": 2.65,
        "defects": [
            {"category": "F", "level": "L2", "description": "工艺陶瓷花瓶瓶身大红受损且立体花朵边缘轮廓严重溢色偏冷青蓝调"},
            {"category": "C", "level": "L1", "description": "展柜内部背景偏冷青暗化"}
        ],
        "review_notes": "展示柜精美花瓶大红色漆面受损泛冷，立体花朵装饰轮廓严重溢色，原评5.0误判。"
    },

    # === SHEET 04 ===
    9649: {
        "score": 1.60,
        "defects": [
            {"category": "B", "level": "L3", "description": "夜间滑板下半部分柏油公路路面恶性错色为刺目惊悚的大红色暖橙色偏暖红黄调"},
            {"category": "E1", "level": "L3", "description": "路面极度过饱和烘烤破坏夜景基调"}
        ],
        "review_notes": "夜间滑板原本深灰黑色的柏油公路路面被强行错涂成刺目大红橙色，过饱和比高达4.88，原评2.17偏高。"
    },
    9772: {
        "score": 2.40,
        "defects": [
            {"category": "B", "level": "L2", "description": "黑熊周围原本清澈纯净的青蓝水体恶性错色为浑浊草绿黄水偏草绿黄调"},
            {"category": "C", "level": "L2", "description": "黑熊头部毛发偏黄发暗"}
        ],
        "review_notes": "水池中黑熊周围清澈天蓝水体被完全涂抹成浑浊草绿黄水，原评5.0误判。"
    },
    9813: {
        "score": 2.80,
        "defects": [
            {"category": "C", "level": "L2", "description": "落地窗外晴朗蓝天海景全盘烘烤泛黄且室内天花板偏焦糖暖黄偏暖红黄调"},
            {"category": "E1", "level": "L1", "description": "客厅内饰与沙发布面局部烘烤过度"}
        ],
        "review_notes": "海景公寓落地窗外开阔蓝天全盘烘烤泛黄，室内天花板也是刺目焦糖黄色，原评5.0误判。"
    },
    9827: {
        "score": 2.30,
        "defects": [
            {"category": "B", "level": "L3", "description": "前排驯象员身穿的纯正鲜艳宝蓝色短袖T恤严重脱色发乌为暗褐深灰色偏暖红黄调"},
            {"category": "C", "level": "L2", "description": "画架与大象躯干整体泛暗黄烘烤"}
        ],
        "review_notes": "驯象员原本鲜艳纯正的宝蓝短袖T恤严重脱色发乌成暗褐深灰色，原评5.0纯属误判。"
    },
    9835: {
        "score": 2.75,
        "defects": [
            {"category": "C", "level": "L2", "description": "背景晴朗蔚蓝天空严重泛黄烘烤偏暖红黄调"},
            {"category": "E2", "level": "L1", "description": "红色消防栓油漆色泽褪色发暗"}
        ],
        "review_notes": "背景晴朗蔚蓝天空全盘泛黄烘烤，消防栓大红色脱色变暗，原评5.0误判。"
    },
    9508: {
        "score": 3.10,
        "defects": [
            {"category": "C", "level": "L1", "description": "公园两旁树冠枝叶翠绿色微弱暗化且草坪偏黄发暗偏暖红黄调"},
            {"category": "E2", "level": "L1", "description": "林荫道树梢生机感轻度欠饱和"}
        ],
        "review_notes": "公园林荫道树木枝叶生机微弱暗化，草坪略偏黄绿，原评5.0脱离GT，适度微调。"
    },

    # === SHEET 05 ===
    9540: {
        "score": 2.35,
        "defects": [
            {"category": "F", "level": "L2", "description": "香蕉后方暗色背景墙角产生大块刺目荧光翠绿恶性溢色杂斑偏暖红黄调"},
            {"category": "E1", "level": "L2", "description": "香蕉果皮局部过饱和溢色"}
        ],
        "review_notes": "香蕉后方暗色墙角无中生有溢出大片刺目荧光翠绿杂斑，过饱和比2.96，溢色比1.50，原评5.0误判。"
    },
    9673: {
        "score": 1.65,
        "defects": [
            {"category": "B", "level": "L3", "description": "树枝上的风筝原本鲜艳天蓝色主翼面恶性错色为刺目橙红橘粉色偏暖红黄调"},
            {"category": "C", "level": "L2", "description": "光秃秃树枝与背景天空泛焦黄暗化"}
        ],
        "review_notes": "风筝原本鲜艳夺目的天蓝色主翼竟被彻底错涂为刺目橙红粉色，原评5.0纯属误判。"
    },
    9693: {
        "score": 2.30,
        "defects": [
            {"category": "E1", "level": "L3", "description": "餐盘切片鲜橙果肉极度过饱和刺目泛焦"},
            {"category": "C", "level": "L2", "description": "白色餐盘与木质桌面大面积烘烤偏暖红黄调"}
        ],
        "review_notes": "餐盘里切片橙子极度过饱和刺目，过饱和比高达6.29，木质桌面严重烘烤泛黄，原评5.0误判。"
    },
    9728: {
        "score": 2.65,
        "defects": [
            {"category": "B", "level": "L2", "description": "桌面中间原本纯正深蓝色的零钱包与小布袋脱色泛乌为深灰褐色偏暖红黄调"},
            {"category": "E2", "level": "L1", "description": "各色杂物小袋色彩轻度欠饱和发暗"}
        ],
        "review_notes": "桌面上深蓝色的零钱包严重脱色发乌为深灰褐色，杂物背景发焦偏黄，原评5.0误判。"
    },
    9830: {
        "score": 2.30,
        "defects": [
            {"category": "B", "level": "L3", "description": "木栈道散步人群中间鲜艳大红色遮阳伞恶性脱色为惨白淡粉色伞偏草绿黄调"},
            {"category": "C", "level": "L2", "description": "湖面水体与树林远景发暗泛绿"}
        ],
        "review_notes": "栈道行人中间原本鲜艳大红色的遮阳伞完全脱色蜕变惨白浅粉伞，原评5.0严重误判。"
    },
    9879: {
        "score": 2.30,
        "defects": [
            {"category": "B", "level": "L3", "description": "草坪右侧小男孩身穿的深墨绿短袖T恤恶性错色为枯黄灰褐色且胸口严重溢出色斑偏洋红紫调"},
            {"category": "F", "level": "L2", "description": "男孩手臂与衣物轮廓洋红紫调溢色"}
        ],
        "review_notes": "草坪右侧小男孩原本深墨绿的短袖T恤错涂为枯黄灰褐色，胸口处严重溢出紫红伪色，原评5.0误判。"
    },

    # === SHEET 06 ===
    9894: {
        "score": 2.90,
        "defects": [
            {"category": "C", "level": "L1", "description": "商业街夜景整体暗部偏冷青蓝调发暗"},
            {"category": "E2", "level": "L1", "description": "建筑外立面霓虹灯广告牌大红色脱色变暗"}
        ],
        "review_notes": "商业街广告牌大红色霓虹灯严重脱色泛冷，街景暗部偏冷青蓝调，原评5.0误判。"
    },
    9899: {
        "score": 2.85,
        "defects": [
            {"category": "C", "level": "L2", "description": "冰箱冷藏室内壁顶部与后壁大面积烘烤泛暖黄发焦偏暖红黄调"},
            {"category": "E1", "level": "L1", "description": "塑料隔板边缘暖光局部过饱和"}
        ],
        "review_notes": "冰箱内部清爽纯净的冷白色塑料内壁被严重烘烤发黄发焦，破坏低温冷藏质感，原评5.0误判。"
    },
    9968: {
        "score": 1.65,
        "defects": [
            {"category": "B", "level": "L3", "description": "欧洲老街沿街建筑二楼外墙恶性错涂诡异刺目荧光翠绿色泛光偏草绿黄调"},
            {"category": "C", "level": "L2", "description": "街道地面与深处建筑偏暖红黄暗化"}
        ],
        "review_notes": "欧洲老街夜景二楼建筑外墙被强行错涂上诡异惊悚的荧光翠绿泛光，破坏整条街夜景氛围，原评5.0荒唐。"
    },
    9975: {
        "score": 2.30,
        "defects": [
            {"category": "B", "level": "L3", "description": "湖畔清澈纯净的蔚蓝湖水水体恶性错色为发暗浑浊草绿黄水偏草绿黄调"},
            {"category": "C", "level": "L2", "description": "大树倒影与岸边草木暗部偏绿发乌"}
        ],
        "review_notes": "湖畔清澈蔚蓝的湖水被模型彻底错涂为发暗发绿的浑浊死水，水体质感严重受损，原评5.0误判。"
    },
    9985: {
        "score": 2.75,
        "defects": [
            {"category": "C", "level": "L2", "description": "巡游车斗彩色拼色大伞大红拼面脱色变暗偏暖红黄调"},
            {"category": "E2", "level": "L1", "description": "彩虹伞面各拼块色彩饱和度失真"}
        ],
        "review_notes": "巡游皮卡车斗中彩虹伞鲜艳的大红色拼块严重脱色泛乌，整体光影混乱，原评5.0误判。"
    },
    9511: {
        "score": 2.45,
        "defects": [
            {"category": "E1", "level": "L2", "description": "古典圆形挂钟透光表盘极度过饱和烘烤为刺目金黄大火球偏暖红黄调"},
            {"category": "F", "level": "L2", "description": "挂钟圆形边框轮廓严重溢色溢出黄晕"}
        ],
        "review_notes": "圆形大挂钟原本雅致淡雅的象牙白透光表盘被严重过饱和烘烤成刺眼金黄大火球，溢色比1.73，原评5.0误判。"
    },

    # === SHEET 07 ===
    9520: {
        "score": 2.15,
        "defects": [
            {"category": "B", "level": "L3", "description": "婴儿身穿的鲜艳大红波点短袖上衣严重脱色退化为发暗枯黄褐色偏暖红黄调"},
            {"category": "E1", "level": "L2", "description": "大人与婴儿皮肤局部过饱和烘烤"}
        ],
        "review_notes": "小婴儿原本穿鲜艳大红色波点上衣，被严重脱色泛黄暗褐，过饱和比2.42，原评2.36偏高。"
    },
    9578: {
        "score": 1.50,
        "defects": [
            {"category": "B", "level": "L3", "description": "雪山斜坡滑雪运动员原本鲜艳纯正大红色滑雪服灾难性错涂为深蓝色滑雪服偏暖红黄调"},
            {"category": "F", "level": "L2", "description": "滑雪运动员服饰边缘轮廓严重溢色"}
        ],
        "review_notes": "滑雪手身上原本鲜艳纯正的大红色滑雪服被灾难性错涂成深海蓝色，红色脱色率高达0.98，恶性错色硬伤！"
    },
    9590: {
        "score": 2.20,
        "defects": [
            {"category": "F", "level": "L2", "description": "桌面物品轮廓严重溢色溢出杂斑"},
            {"category": "B", "level": "L2", "description": "随身深蓝色小皮包严重脱色泛紫发暗偏暖红黄调"}
        ],
        "review_notes": "桌面原本纯正深蓝色的随身皮具小包脱色泛紫变暗，轮廓溢色比高达2.16，原评2.17偏高。"
    },
    9700: {
        "score": 2.25,
        "defects": [
            {"category": "B", "level": "L3", "description": "宽敞大客厅大面积铺设的浅灰米白地毯恶性错色为高饱和焦黄橙红色偏暖红黄调"},
            {"category": "E1", "level": "L2", "description": "客厅地面与天花板过饱和烘烤如火炉"}
        ],
        "review_notes": "大客厅浅灰米白色地毯被整体严重烘烤成极度刺目的焦黄橙红色，如置身火炉，过饱和比1.82。"
    },
    9992: {
        "score": 2.75,
        "defects": [
            {"category": "C", "level": "L2", "description": "展厅机车金属车架与地面偏暖红黄烘烤"},
            {"category": "E2", "level": "L1", "description": "后方观众身穿的宝蓝色连帽夹克褪色发灰"}
        ],
        "review_notes": "展厅机车周围观众宝蓝外套褪色发灰，机车金属车架偏焦黄烘烤，过饱和比2.30。"
    },
    9516: {
        "score": 2.70,
        "defects": [
            {"category": "C", "level": "L2", "description": "维多利亚凤冠鸠背部翅膀深酒红羽斑严重脱色发青冷暗偏冷青蓝调"},
            {"category": "E2", "level": "L1", "description": "鸟儿羽毛自然斑斓色泽轻度欠饱和"}
        ],
        "review_notes": "凤冠鸠翅膀上原本醒目的深酒红羽毛斑块脱色泛冷泛青，羽毛偏冷青蓝调，原评5.0误判。"
    },

    # === SHEET 08 ===
    9524: {
        "score": 2.30,
        "defects": [
            {"category": "B", "level": "L3", "description": "青年脚下原本葱翠碧绿的平整大草坪大面积脱色为发暗枯黄褐色偏洋红紫调"},
            {"category": "C", "level": "L2", "description": "背景树林暗部偏紫红发暗"}
        ],
        "review_notes": "橄榄球青年脚下原本一整片葱翠碧绿的大草坪被彻底脱色退化为发暗枯黄褐草地，生机全失，原评5.0误判。"
    },
    9526: {
        "score": 2.30,
        "defects": [
            {"category": "B", "level": "L3", "description": "厨房聚餐女子身穿的鲜艳大红色长裤严重脱色为发乌暗黑灰色偏冷青蓝调"},
            {"category": "C", "level": "L2", "description": "餐台台面与地面暗部偏冷青暗化"}
        ],
        "review_notes": "厨房女子身穿的鲜艳大红色长裤严重脱色变暗黑灰色，周围餐台也发暗泛冷，原评5.0误判。"
    },
    9541: {
        "score": 2.45,
        "defects": [
            {"category": "B", "level": "L2", "description": "车库门内操作台背景墙面被大面积错涂阴冷诡异青冷灰蓝与紫色偏冷青蓝调"},
            {"category": "F", "level": "L1", "description": "门框边缘轮廓轻度溢色"}
        ],
        "review_notes": "车库工作台原本温馨的暖木白墙面被大面积错涂阴冷青灰蓝紫色光晕，原评5.0误判。"
    },
    9564: {
        "score": 2.80,
        "defects": [
            {"category": "E1", "level": "L2", "description": "动物园沙土地面与长颈鹿身躯过饱和烘烤偏红橙调偏暖红黄调"},
            {"category": "C", "level": "L1", "description": "遮阳棚立柱与沙地色温发焦"}
        ],
        "review_notes": "动物园长颈鹿躯干与沙土地面严重烘烤过饱和，过饱和比2.11，原评5.0误判。"
    },
    9574: {
        "score": 2.35,
        "defects": [
            {"category": "E1", "level": "L3", "description": "棕褐色马匹毛发极度过饱和烘烤呈现刺目红铜色大红橙色偏暖红黄调"},
            {"category": "C", "level": "L2", "description": "周围牵马人员与背景帐篷偏暖烘烤"}
        ],
        "review_notes": "高头大马原本自然的棕褐色毛发被严重烘烤为极度刺目的红铜红橙色，Delta_C达0.20，原评5.0误判。"
    },
    9586: {
        "score": 1.55,
        "defects": [
            {"category": "B", "level": "L3", "description": "网球女选手原本鲜艳纯正玫红色长袖球衣灾难性错涂为浅灰蓝白色上衣偏暖红黄调"},
            {"category": "C", "level": "L2", "description": "背景挡板脱色发白且球场地面烘烤泛黄"}
        ],
        "review_notes": "网球女将身上原本鲜艳夺目的玫红长袖球衣竟然被彻底错涂成了浅灰蓝白色，局部色偏高达0.77，恶性硬伤！"
    },

    # === SHEET 09 ===
    9620: {
        "score": 2.10,
        "defects": [
            {"category": "B", "level": "L3", "description": "傍晚街头近景水泥路面与滑道恶性错色为刺目极度浓艳的荧光洋红紫色偏洋红紫调"},
            {"category": "E1", "level": "L2", "description": "路面荧光洋红色块极度过饱和刺目"}
        ],
        "review_notes": "近景深色柏油路面被强行涂抹上大片刺目极度浓艳的荧光洋红紫色光晕，原评5.0纯属误判。"
    },
    9666: {
        "score": 2.35,
        "defects": [
            {"category": "B", "level": "L3", "description": "电脑前狗狗背后原本温馨暖黄的墙壁大面积严重脱色为阴冷发暗青灰冷白墙偏冷青蓝调"},
            {"category": "C", "level": "L2", "description": "室内整体光照完全丧失温暖感"}
        ],
        "review_notes": "背景原本极其温馨暖黄的居室墙壁被完全剥夺暖色，蜕变成冰冷阴惨的青灰白墙，原评5.0误判。"
    },
    9667: {
        "score": 2.30,
        "defects": [
            {"category": "B", "level": "L3", "description": "红土网球场女选手原本纯正鲜艳大红色运动背心恶性错色为冷调洋红粉紫色偏洋红紫调"},
            {"category": "C", "level": "L2", "description": "红土球场砖红色地面轻度脱色泛暗"}
        ],
        "review_notes": "女网球选手身穿的纯正大红背心被错涂为冷调洋红粉紫色，偏色Delta_C高达0.26，原评5.0误判。"
    },
    9704: {
        "score": 1.60,
        "defects": [
            {"category": "B", "level": "L3", "description": "棒球击球手佩戴的鲜艳大红色护腕与手套恶性错色为鲜艳宝蓝色手套偏草绿黄调"},
            {"category": "C", "level": "L2", "description": "球场看台背景与衣服阴影处泛黄偏色"}
        ],
        "review_notes": "棒球手腕部原本纯正鲜艳的大红色护腕和手套，竟然被彻底错涂成了鲜艳宝蓝色，原评5.0极其荒唐。"
    },
    9709: {
        "score": 2.10,
        "defects": [
            {"category": "B", "level": "L3", "description": "电视机顶猫咪背后原本极其浓郁温馨的焦糖暖橙黄色墙壁大面积脱色为惨淡浅灰白偏冷青蓝调"},
            {"category": "E2", "level": "L2", "description": "室内环境色彩严重欠饱和"}
        ],
        "review_notes": "居室原本浓郁温馨的焦糖暖橙黄墙壁被完全剥夺暖色，退化为冷淡惨白浅灰墙，Delta_C高达0.26。"
    },
    9748: {
        "score": 2.75,
        "defects": [
            {"category": "C", "level": "L2", "description": "纸袋包装的面包三明治与内馅整体色泽严重欠饱和泛冷偏冷青蓝调"},
            {"category": "E2", "level": "L1", "description": "烤肉与外皮金黄酥脆色泽暗淡缺失"}
        ],
        "review_notes": "外卖纸袋中金黄牛角三明治严重脱色泛冷，烤肉色泽阴冷发灰，原评5.0误判。"
    },

    # === SHEET 10 ===
    9750: {
        "score": 2.45,
        "defects": [
            {"category": "B", "level": "L2", "description": "四轮马车原本鲜艳醒目的明黄色车箱与车轮脱色发焦黑红偏暖红黄调"},
            {"category": "C", "level": "L2", "description": "背景红砖欧式建筑整体烘烤泛黑暗化"}
        ],
        "review_notes": "四轮马车明黄色车身与车轮脱色发焦暗黑，背景建筑烘烤过度，偏色Delta_C为0.16。"
    },
    9778: {
        "score": 2.40,
        "defects": [
            {"category": "B", "level": "L3", "description": "城市广场钟楼背景原本清澈湛蓝的晴空严重脱色蜕变为发脏发暗阴霾灰白天空偏暖红黄调"},
            {"category": "C", "level": "L2", "description": "广场车辆与建筑立面暗部偏黄烘烤"}
        ],
        "review_notes": "钟楼背景原本纯净湛蓝的晴空被彻底脱色退化为发脏阴暗的灰白阴天，Delta_C达0.24，原评5.0误判。"
    },
    9779: {
        "score": 2.80,
        "defects": [
            {"category": "C", "level": "L2", "description": "餐桌上编织餐垫桌布红白蓝丰富线条色泽失真偏冷青蓝调"},
            {"category": "E2", "level": "L1", "description": "红色编织线脱色泛乌变暗"}
        ],
        "review_notes": "甜甜圈餐桌编织桌布原本红白蓝的丰富色泽偏冷泛灰，红色线条脱色，原评5.0误判。"
    },
    9787: {
        "score": 2.30,
        "defects": [
            {"category": "B", "level": "L3", "description": "意大利比萨饼上原本新鲜翠绿的蔬菜叶恶性错色为焦黄枯烂菜叶色偏暖红黄调"},
            {"category": "E1", "level": "L2", "description": "比萨饼皮与肉酱局部过饱和焦化"}
        ],
        "review_notes": "比萨饼表面新鲜翠绿的罗勒/芝麻菜叶被完全烘烤为枯黄焦烂菜色，饼皮过饱和发焦，原评5.0误判。"
    },
    9795: {
        "score": 1.55,
        "defects": [
            {"category": "B", "level": "L3", "description": "击球小男孩原本纯正鲜艳的大红色短袖球衣灾难性错涂为鲜艳宝蓝色球衣偏冷青蓝调"},
            {"category": "C", "level": "L2", "description": "看台围网与观众暗部偏冷青泛乌"}
        ],
        "review_notes": "小男孩身上原本鲜艳大红色的棒球球衣被灾难性错涂为鲜艳宝蓝色，原评5.0彻底荒谬。"
    },
    9798: {
        "score": 2.65,
        "defects": [
            {"category": "B", "level": "L2", "description": "聚餐左侧女士身穿的亮黄色针织开衫外套脱色泛冷为浅蓝紫灰色偏冷青蓝调"},
            {"category": "C", "level": "L1", "description": "餐桌桌布与室内光线偏冷青发暗"}
        ],
        "review_notes": "聚餐左侧女士身穿的亮黄针织上衣脱色泛冷蜕变为浅紫蓝灰色，餐桌环境偏冷，原评4.46偏高。"
    }
}
