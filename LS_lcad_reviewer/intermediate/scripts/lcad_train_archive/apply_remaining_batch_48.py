import json
import os
import copy

BATCH_48_REVIEWS = {
  # Sheet 01 (Tasks 9474, 9479, 9480, 9481, 9484, 9485)
  9474: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "厨房实木吊柜与墙壁大面积浸染失真冰冷青蓝偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "实木吊柜暖木纹色泽严重欠饱和脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "冷青色调破坏厨房温馨烟火气。"}
    ],
    "review_note": "厨房实木吊柜与墙壁大面积浸染失真冰冷青蓝偏色，暖木纹色泽严重欠饱和脱色发暗(D-L2, E2-L2, F-L2)。"
  },
  9479: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9480: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "滑雪运动员原本鲜艳大红色的滑雪服胸前色块严重脱色错染为灰白色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "滑雪手套与裤腿微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "红色滑雪服胸前大面积欠饱和脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "红黑相间滑雪服脱色降低辨识度。"}
    ],
    "review_note": "滑雪运动员原本鲜艳大红色的滑雪服胸前色块严重欠饱和脱色褪变为灰白色(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9481: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "书房皮质沙发背阴转角处微染冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "深棕色皮质沙发背阴转角处与书架暗部色彩略显暗淡欠饱和。"}
    ],
    "review_note": "书房深棕色皮质沙发背阴转角处与书架暗部色彩略显暗淡欠饱和，微染冷灰偏色(D-L1, E2-L1)。"
  },
  9484: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9485: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 02 (Tasks 9486, 9488, 9490, 9493, 9495, 9496)
  9486: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "海滩浅水区海水与沙滩微染浑浊灰黄偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "海水水质严重欠饱和脱色发暗，清透感丧失。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "海水泛黄褪色影响海滨游憩真实感。"}
    ],
    "review_note": "阴天海滩浅水区海水与沙滩大面积浸染浑浊灰黄偏色，海水水质严重欠饱和脱色发暗(D-L1, E2-L2, F-L1)。"
  },
  9488: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "街头金属双联停车计时器外壳与立柱大面积浸染失真浓艳的冰冷青蓝偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "计时器金属立柱青蓝色调过于浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "银色金属设备错染浓艳青蓝破坏街景质感。"}
    ],
    "review_note": "街头金属双联停车计时器外壳与立柱大面积浸染失真浓艳的冰冷青蓝偏色(D-L2, E1-L2, F-L2)。"
  },
  9490: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "白色陶瓷小便斗内壁转角微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "卫生间白色陶瓷小便池内壁阴影与隔板转角色彩略显暗淡欠饱和。"}
    ],
    "review_note": "卫生间白色陶瓷小便池内壁阴影与隔板转角色彩略显暗淡欠饱和，微染冷青灰色调(D-L1, E2-L1)。"
  },
  9493: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "烤肉汉堡金黄面包与肉饼错染失真深紫红伪色斑块。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "餐桌汉堡与薯条大面积泛深紫红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "错染的深紫红杂斑色泽浓艳不自然。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "食物表面浸染紫红色严重破坏食欲真实感。"}
    ],
    "review_note": "餐桌烤肉汉堡金黄面包与肉饼大面积浸染失真深紫红偏色，杂色破坏食物食欲(C-L2, D-L2, E1-L1, F-L2)。"
  },
  9495: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "消防栓旁绿茵草坪大面积错染为失真刺眼的荧光翠绿色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "登山包与地面微泛火红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "草坪荧光绿色与登山包红色调过于浓艳溢出。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "荧光草地严重违背自然草木色调。"}
    ],
    "review_note": "消防栓旁绿茵草坪大面积错染为失真刺眼的荧光翠绿色，登山包红色调过于浓艳溢出(C-L2, D-L1, E1-L2, F-L1)。"
  },
  9496: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "铁轨上红色内燃机车车头原本饱满的大红涂装脱色错染为暗土褐色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "机车侧面与车轮微泛灰冷偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "大红机车车身严重欠饱和脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "车头脱色降低机车涂装辨识度。"}
    ],
    "review_note": "铁轨上红色内燃机车车头原本饱满的大红涂装大面积欠饱和严重脱色变暗(C-L2, D-L1, E2-L2, F-L1)。"
  },

  # Sheet 03 (Tasks 9498, 9499, 9500, 9502, 9504, 9505)
  9498: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "老式蒸汽机车车头前方红色排障器脱色错染为暗灰褐色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "机车车轮与站台微染冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "排障器红漆与红瓦建筑欠饱和严重脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "排障器脱色降低车头警示效果。"}
    ],
    "review_note": "老式蒸汽机车车头前方红色排障器与左侧红瓦建筑欠饱和严重脱色发暗(C-L2, D-L1, E2-L1, F-L1)。"
  },
  9499: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "长颈鹿活动场前景泥土地面大面积浸染失真深红褐色偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "泥土地面红色调过于浓艳不自然。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "泥土严重泛红破坏动物栖息地自然感。"}
    ],
    "review_note": "长颈鹿活动场前景泥土地面大面积浸染失真深红褐色偏色，红色调浓艳不自然(D-L2, E1-L2, F-L2)。"
  },
  9500: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "晴空下老式客运车厢上方原本蔚蓝的天空大面积脱色错染为苍白灰白色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "木质车厢边缘微泛冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "天空蓝色完全丧失，严重欠饱和脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "晴空苍白褪色降低画面开阔感。"}
    ],
    "review_note": "晴空下老式客运车厢上方原本蔚蓝的天空大面积欠饱和严重脱色发白(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9502: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9504: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9505: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "复古地铁车头深色金属车身微泛暖黄灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "驾驶室玻璃与深绿金属车漆暗部层次略显暗淡欠饱和。"}
    ],
    "review_note": "复古老式地铁车头深色金属车身与驾驶室玻璃微泛暖黄灰偏色，细节略显暗淡(D-L1, E2-L1)。"
  },

  # Sheet 04 (Tasks 9506, 9507, 9512, 9513, 9517, 9522)
  9506: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "床上银灰色笔记本电脑背面苹果Logo被严重错染为亮蓝色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "白色被褥与木质床头微泛冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "白色床单背光处略显暗淡欠饱和。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "发光苹果Logo错染亮蓝破坏数码产品真实感。"}
    ],
    "review_note": "床上银灰色笔记本电脑背面苹果Logo被错染为亮蓝色，白色被褥暗部略显欠饱和脱色(C-L2, D-L1, E2-L1, F-L1)。"
  },
  9507: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "客厅地毯与门廊转角微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "客厅地面浅色地毯与门廊转角阴影色彩略显暗淡欠饱和。"}
    ],
    "review_note": "客厅地面浅色地毯与门廊转角阴影色彩略显暗淡欠饱和，微染冷青灰色调(D-L1, E2-L1)。"
  },
  9512: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "开放式厨房实木吊柜深红木色泽微泛冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "大理石吧台与吊柜暗部色彩欠饱和略显暗淡。"}
    ],
    "review_note": "开放式厨房实木吊柜深红木色泽与大理石吧台微泛冷青偏色，色彩欠饱和略显暗淡(D-L1, E2-L1)。"
  },
  9513: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "路口立柱上两个八角形STOP停止标志牌原本鲜艳的大红底漆严重脱色错染为暗灰褐色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "立柱与背景树木微泛灰冷偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "停止牌大红底漆严重欠饱和脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "红漆脱色降低警示标志辨识度。"}
    ],
    "review_note": "路口立柱上两个八角形STOP停止标志牌原本鲜艳的大红色底漆欠饱和严重脱色褪变为暗灰褐色(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9517: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9522: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 05 (Tasks 9523, 9525, 9527, 9532, 9534, 9535)
  9523: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "野外荒漠土路边原本晴朗蔚蓝的天空大面积欠饱和严重脱色褪白，摩托车大红尾灯脱色发暗。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "天空与远山大面积泛暗土黄偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "天空蓝色完全丧失，严重欠饱和脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "晴空彻底褪灰破坏户外公路旅行感。"}
    ],
    "review_note": "野外荒漠土路边原本晴朗蔚蓝的天空大面积欠饱和严重脱色褪白，摩托车大红尾灯脱色发暗(C-L3, D-L2, E2-L3, F-L2)。"
  },
  9525: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "西门子电力机车车头原本鲜亮明黄色的涂装严重脱色错染为暗淡土黄色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "机车侧面金属与轨道微泛冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "明黄色车头大面积欠饱和脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "鲜亮黄色脱色降低电力机车外观质感。"}
    ],
    "review_note": "铁轨上西门子电力机车车头原本鲜亮明黄色的涂装大面积欠饱和严重脱色泛暗土黄色(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9527: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "厨房台面上烘烤披萨金黄芝士与大红酱料脱色，罗勒绿叶边缘微泛冷青偏色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "不锈钢工作台面微泛冷青灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "披萨烘烤酱料欠饱和脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "披萨脱色破坏食材烘烤鲜香感。"}
    ],
    "review_note": "厨房台面上烘烤披萨金黄芝士与大红酱料大面积欠饱和脱色发暗，罗勒绿叶微泛冷青偏色(C-L2, D-L1, E2-L2, F-L2)。"
  },
  9532: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "餐厅包厢男子发际线与领带转角微染冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "戴眼镜男子面部阴影与西装领带转角色彩略显暗淡欠饱和。"}
    ],
    "review_note": "餐厅包厢内戴眼镜男子面部阴影与西装领带转角色彩略显暗淡欠饱和，微染冷灰偏色(D-L1, E2-L1)。"
  },
  9534: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "黑色电磁炉上金属平底锅内红色番茄辣椒酱错染为失真深洋红紫杂色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "电磁炉表面微泛洋红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的深洋红酱汁浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "辣酱变洋红违背食材烹饪常识。"}
    ],
    "review_note": "黑色电磁炉上金属平底锅内红色番茄辣椒酱大面积错染为失真深洋红紫杂色(C-L2, D-L1, E1-L2, F-L2)。"
  },
  9535: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "沿街商铺门头招牌与遮阳篷大面积错染失真深蓝紫与深洋红伪色斑块。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "建筑立面与阳台栏杆泛深蓝紫偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的深蓝紫招牌浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "建筑招牌紫蓝伪色严重破坏街景真实感。"}
    ],
    "review_note": "沿街商铺门头招牌与遮阳篷大面积错染失真深蓝紫与深洋红伪色斑块(C-L2, D-L2, E1-L2, F-L2)。"
  },

  # Sheet 06 (Tasks 9536, 9537, 9538, 9539, 9543, 9544)
  9536: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "漫步野生象群身躯错染刺眼深洋红伪色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "草原树木与泥土微染冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "辽阔草原绿茵植被大面积欠饱和严重脱色褪白。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "象身洋红伪色破坏自然生态真实感。"}
    ],
    "review_note": "辽阔草原绿茵植被大面积欠饱和严重脱色褪白，漫步象群身躯错染刺眼深洋红伪色(C-L2, D-L1, E2-L3, F-L2)。"
  },
  9537: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "网球场原本鲜艳砖红色的红土场地脱色错染为暗淡暗土褐色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "球员白色球服背光处微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "红土球场大面积欠饱和脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "红土脱色降低球场辨识度与竞技生机。"}
    ],
    "review_note": "网球场原本鲜艳砖红色的红土场地大面积欠饱和严重脱色发暗，褪变为暗土褐色(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9538: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "海湾原本清澈碧蓝的水体彻底脱色错染为浑浊水泥灰死水。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "海面与沙滩大面积泛灰土黄偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "碧蓝水色完全丧失，严重欠饱和脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "热带海湾水体灰死彻底破坏海岛美景。"}
    ],
    "review_note": "客机低空降落海滩原本清澈碧蓝的海湾水体彻底欠饱和严重脱色褪变为浑浊水泥灰(C-L3, D-L2, E2-L3, F-L3)。"
  },
  9539: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "滑板特技背景原本温暖红艳的红砖建筑外墙彻底脱色错染为死寂灰色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "建筑立面与地面大面积泛冷青灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "红砖暖色完全丧失，严重欠饱和脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "红砖变水泥灰彻底破坏街景温度。"}
    ],
    "review_note": "滑板特技背景原本温暖红艳的红砖建筑外墙彻底欠饱和严重脱色褪变为死寂灰色(C-L3, D-L2, E2-L3, F-L3)。"
  },
  9543: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "木桌背阴处与后方男士衬衫微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "木桌上陈列成熟香蕉背阴处与后方男士衬衫暗部细节色彩略显暗淡欠饱和。"}
    ],
    "review_note": "木桌上陈列成熟香蕉背阴处与后方男士衬衫暗部细节色彩略显暗淡欠饱和(D-L1, E2-L1)。"
  },
  9544: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "泰晤士河畔大本钟塔楼、议会大厦与河面夜景大面积浸染失真火红金橙偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "夜景大本钟火红偏色浓艳溢出。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "全城大本钟泛火红破坏自然夜景幽邃感。"}
    ],
    "review_note": "泰晤士河畔大本钟塔楼、议会大厦与河面夜景大面积浸染失真火红金橙偏色(D-L2, E1-L2, F-L2)。"
  },

  # Sheet 07 (Tasks 9545, 9547, 9550, 9551, 9553, 9554)
  9545: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "卫生间木质侧墙大面积浸染暗冷灰青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "木质侧墙暖木纹色泽严重欠饱和脱色发灰。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "木板褪灰严重破坏卫生间整洁温馨质感。"}
    ],
    "review_note": "卫生间坐便器旁木质侧墙大面积欠饱和脱色发暗，暖木纹色泽严重褪色发灰(D-L2, E2-L2, F-L2)。"
  },
  9547: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9550: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "客厅交谈青年面部肤色、服饰与背景墙面大面积浸染失真火红暖黄偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "青年肤色与墙面暖红色彩略显偏浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "肤色偏红失真降低人物形象自然度。"}
    ],
    "review_note": "客厅交谈青年面部肤色、服饰与背景墙面大面积浸染失真火红暖黄偏色(D-L2, E1-L1, F-L1)。"
  },
  9551: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "现代公寓客餐厅白色吧台、地板与墙面大面积浸染失真暖黄红橙偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "室内吧台与地板红橙色调浓艳过度。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "浓艳红橙偏色破坏室内自然采光。"}
    ],
    "review_note": "现代公寓客餐厅白色吧台、地板与墙面大面积浸染失真暖黄红橙偏色，室内采光偏浓艳(D-L2, E1-L2, F-L1)。"
  },
  9553: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "室内与牧羊犬互动男子面部肤色、手臂与背景墙壁大面积浸染失真火红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "男子肤色火红色彩极度浓艳溢出。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "男子身躯通体火红严重破坏真实感。"}
    ],
    "review_note": "室内与牧羊犬互动男子面部肤色、手臂与背景墙壁大面积浸染失真火红偏色(D-L2, E1-L2, F-L2)。"
  },
  9554: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 08 (Tasks 9556, 9557, 9558, 9559, 9561, 9563)
  9556: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "夜间树林枝干阴影微染冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "夜间林间黑熊背部毛发阴影与背景树木枝干色彩略显暗淡欠饱和。"}
    ],
    "review_note": "夜间林间黑熊背部毛发阴影与背景树木枝干色彩略显暗淡欠饱和，微染冷灰偏色(D-L1, E2-L1)。"
  },
  9557: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "蓝色托盘中烘焙甜甜圈金黄焦糖表皮脱色错染为暗灰褐色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "蓝色托盘边缘微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "甜甜圈金黄表皮大面积欠饱和脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "甜品表皮脱色严重影响烘焙诱人食欲。"}
    ],
    "review_note": "蓝色托盘中烘焙甜甜圈金黄焦糖表皮大面积欠饱和严重脱色发暗，褪变为暗灰褐色(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9558: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "客厅沙发背光阴影微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "客厅粉紫提花软包沙发背阴褶皱与长毛猫背部毛发阴影色彩略显暗淡欠饱和。"}
    ],
    "review_note": "客厅粉紫提花软包沙发背阴褶皱与长毛猫背部毛发阴影色彩略显暗淡欠饱和(D-L1, E2-L1)。"
  },
  9559: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "餐桌烘烤披萨暗部微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "餐桌烘烤披萨芝士暗部与木质桌面边缘色彩略显暗淡欠饱和。"}
    ],
    "review_note": "餐桌烘烤披萨芝士暗部与木质桌面边缘色彩略显暗淡欠饱和，微染冷青灰色调(D-L1, E2-L1)。"
  },
  9561: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "宠物犬背心转角与后方背包微染冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "室内木地板上宠物犬浅色背心背阴处与后方背包阴影细节色彩略显暗淡欠饱和。"}
    ],
    "review_note": "室内木地板上宠物犬浅色背心背阴处与后方背包阴影细节色彩略显暗淡欠饱和(D-L1, E2-L1)。"
  },
  9563: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "相扑比赛展厅力士身躯皮肤与背景墙面大面积浸染失真冰冷青蓝偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "力士肤色严重欠饱和褪为病态冷灰。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "青蓝色调大面积浸染破坏体育赛事健康竞技感。"}
    ],
    "review_note": "相扑比赛展厅力士身躯皮肤与背景墙面大面积浸染失真冰冷青蓝偏色，肤色严重欠饱和褪灰(D-L2, E2-L2, F-L2)。"
  },

  # Sheet 09 (Tasks 9566, 9568, 9569, 9571, 9572, 9573)
  9566: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "马术竞技场观众席看台错染失真深洋红紫偏色斑块。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "看台观众席与广告牌大面积泛洋红紫偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "看台紫红杂斑色彩偏浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "观众席紫红杂斑破坏赛场整体秩序美感。"}
    ],
    "review_note": "马术竞技场观众席看台与广告牌大面积浸染失真深洋红紫偏色(C-L2, D-L2, E1-L1, F-L2)。"
  },
  9568: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9569: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "手部橙色卫衣袖口微染暗红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "捧青柠檬手部橙色卫衣袖口与手指背阴处色彩略显浓艳。"}
    ],
    "review_note": "捧青柠檬手部橙色卫衣袖口与手指背阴处微染暗红偏色，色彩略显浓艳(D-L1, E1-L1)。"
  },
  9571: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "低头吃料长颈鹿头部与颈部金黄网状斑纹大面积脱色错染为灰暗惨白色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "长颈鹿颈部与木质料槽大面积泛灰冷偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "金黄斑纹严重欠饱和脱色褪白。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "长颈鹿彻底褪色惨白丧失野生动物生机。"}
    ],
    "review_note": "低头吃料长颈鹿头部与颈部金黄网状斑纹大面积欠饱和严重脱色褪白，神态干瘪苍白(C-L3, D-L2, E2-L3, F-L3)。"
  },
  9572: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "餐盘中烤热狗肠与肉串大面积脱色错染为冰冷灰暗的浅紫灰死色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "白色餐盘与食物大面积泛冷紫灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "烤肉诱人金红肉色完全丧失，严重欠饱和脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "肉食呈现紫灰死色严重破坏食用可信度。"}
    ],
    "review_note": "餐盘中烤热狗肠与肉串大面积欠饱和严重脱色错染为冰冷灰暗的浅紫灰死色(C-L3, D-L2, E2-L3, F-L3)。"
  },
  9573: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "草地啄食白羽母鸡与黑母鸡背部羽毛错染刺眼深蓝紫与荧光蓝伪色斑块。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "母鸡背部与草地微泛冷青偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的深蓝紫伪色浓艳突兀。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "家禽背羽错染蓝紫伪色破坏农家自然质感。"}
    ],
    "review_note": "草地啄食白羽母鸡与黑母鸡背部羽毛错染刺眼深蓝紫与荧光蓝伪色斑块(C-L2, D-L1, E1-L2, F-L2)。"
  },

  # Sheet 10 (Tasks 9575, 9576, 9577, 9579, 9580, 9583)
  9575: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "欧式客厅金黄色提花绒面沙发脱色错染为暗淡灰黄色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "落地钟与客厅墙面微染冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "金黄绒面沙发大面积欠饱和脱色变暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "金黄沙发脱色降低了欧式客厅高贵典雅质感。"}
    ],
    "review_note": "欧式客厅金黄色提花绒面沙发大面积欠饱和严重脱色变暗，褪变为暗淡灰黄色(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9576: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "卫生间玻璃砖墙面与毛巾架大面积泛冷青紫偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "毛巾架挂毛巾与洗手台大面积欠饱和脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "冷青紫调使卫浴空间阴冷失真。"}
    ],
    "review_note": "卫生间玻璃砖墙面与毛巾架挂毛巾大面积欠饱和脱色发暗，微染冷青紫偏色(D-L2, E2-L2, F-L1)。"
  },
  9577: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "果蔬筐中红苹果与金黄香蕉表皮色泽严重脱色发暗。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "香蕉表皮微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "红苹果与香蕉大面积欠饱和脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "新鲜果品脱色影响新鲜度与商品质感。"}
    ],
    "review_note": "蓝色果蔬筐中红苹果与金黄香蕉大面积欠饱和脱色发暗，果品色泽略显暗淡(C-L2, D-L1, E2-L1, F-L1)。"
  },
  9579: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9580: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "男子面部肤色背阴处微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "头戴贝雷帽男子面部肤色背阴处与衣领转角阴影色彩略显暗淡欠饱和。"}
    ],
    "review_note": "头戴贝雷帽男子面部肤色背阴处与衣领转角阴影色彩略显暗淡欠饱和，微染冷青灰色调(D-L1, E2-L1)。"
  },
  9583: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "桌面陈列翻盖手机金属外壳与浅色背景大面积浸染失真暖黄红褐偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "手机键盘暗部层次略显暗淡欠饱和。"}
    ],
    "review_note": "桌面陈列老式翻盖手机金属外壳与浅色背景大面积浸染失真暖黄红褐偏色(D-L1, E2-L1)。"
  },

  # Sheet 11 (Tasks 9584, 9585, 9587, 9588, 9589, 9591)
  9584: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "相片中抱黑狗女孩面部肤色与粉色短袖大面积浸染失真火红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "女孩短袖与面部红色调浓艳过度溢出。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "人物肤色过度泛红破坏相片生动感。"}
    ],
    "review_note": "拍立得相片中抱黑狗开怀大笑女孩面部肤色与粉色短袖大面积浸染失真火红偏色(D-L2, E1-L2, F-L1)。"
  },
  9585: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9587: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L3", "description": "酒店客房全屋大面积浸染冰冷惨淡的冷青灰蓝偏色，暖色灯光氛围被彻底破坏。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "客房墙面、沙发与地毯严重欠饱和脱色发灰。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "温馨客房变冰冷灰蓝严重破坏居住温馨感。"}
    ],
    "review_note": "酒店客房温馨暖色灯光氛围被彻底破坏，全屋大面积浸染冰冷惨淡的冷青灰蓝偏色(D-L3, E2-L3, F-L3)。"
  },
  9588: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9589: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "红砖建筑窗台转角与百叶窗缝隙微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "红砖建筑白色百叶窗缝隙背阴处与窗台下方转角阴影色彩略显暗淡欠饱和。"}
    ],
    "review_note": "红砖建筑白色百叶窗缝隙背阴处与窗台下方转角阴影色彩略显暗淡欠饱和(D-L1, E2-L1)。"
  },
  9591: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "繁华都市街头夜景沥青路面与车流大面积浸染失真浓艳的火红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L3", "description": "路面火红反光色彩极度浓艳溢出。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "整条沥青马路浸染大红彻底破坏城市夜景自然质感。"}
    ],
    "review_note": "繁华都市街头夜景沥青路面与车流大面积浸染失真浓艳的火红偏色，霓虹倒影失真(D-L2, E1-L3, F-L2)。"
  },

  # Sheet 12 (Tasks 9594, 9595, 9597, 9598, 9599, 9601)
  9594: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9595: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "公园钟亭前方天空与草坪地面大面积浸染失真火红暗黄偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "天空与草地火红暗黄色泽过于浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "全景泛红破坏公园开阔自然采光。"}
    ],
    "review_note": "公园钟亭前方天空与草坪地面大面积浸染失真火红暗黄偏色，色泽过于浓艳(D-L2, E1-L2, F-L2)。"
  },
  9597: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "炸鱼薯条餐盘转角微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "餐盘中酥脆炸鱼背阴焦脆处与薯条底部阴影细节色彩略显暗淡欠饱和。"}
    ],
    "review_note": "餐盘中酥脆炸鱼背阴焦脆处与薯条底部阴影细节色彩略显暗淡欠饱和(D-L1, E2-L1)。"
  },
  9598: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "街舞青年原本鲜亮纯正的蓝色T恤脱色错染为暗淡深紫蓝色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "球场铁丝网泛黄褐偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "蓝色T恤与周围铁丝网色泽略显暗淡。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "服饰偏紫变暗破坏街舞动感。"}
    ],
    "review_note": "街舞青年原本鲜亮纯正的蓝色T恤错染为暗淡深紫蓝色，球场铁丝网泛黄褐偏色(C-L2, D-L1, E2-L1, F-L1)。"
  },
  9599: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "餐厅交谈男士暖黄T恤与女士浅蓝短袖大面积欠饱和脱色发暗，微染冷青偏色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "人物面部与白色桌面微泛冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "两人服饰色彩欠饱和脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "服饰脱色发暗降低就餐交谈温馨感。"}
    ],
    "review_note": "餐厅交谈男士暖黄T恤与女士浅蓝短袖大面积欠饱和脱色发暗，微染冷青偏色(C-L2, D-L1, E2-L1, F-L1)。"
  },
  9601: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 13 (Tasks 9602, 9603, 9605, 9606, 9607, 9610)
  9602: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9603: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "餐桌温暖木质桌面被颠覆性错染为刺眼深蓝紫与冷青色伪色，翻盖手机泛荧光洋红。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "桌面与背景大面积泛刺眼深蓝紫冷调。"},
      {"id": "E1", "name": "过饱和", "severity": "L3", "description": "错染的深蓝紫与荧光洋红极度浓艳溢出。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "木质桌面错染深蓝完全破坏室内空间真实感。"}
    ],
    "review_note": "餐桌温暖木质桌面被颠覆性错染为刺眼深蓝紫与冷青色伪色，翻盖手机泛荧光洋红(C-L3, D-L2, E1-L3, F-L3)。"
  },
  9605: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "卧室全屋大面积泛冰冷灰青偏色，温馨暖黄色灯光完全丧失。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "墙面与床铺大面积欠饱和严重脱色褪白。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "暖色卧室变死白冷灰破坏居家舒适感。"}
    ],
    "review_note": "卧室温馨暖黄色光照氛围彻底脱色丧失，墙面与床铺大面积欠饱和褪变为惨白冰冷灰暗(D-L2, E2-L3, F-L2)。"
  },
  9606: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "草坡繁茂绿茵草地脱色错染为暗淡枯草黄色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "白羊背毛与草地边缘微泛冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "绿茵草坪大面积欠饱和严重脱色变暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "草地枯萎发黑破坏牧场生机。"}
    ],
    "review_note": "草坡繁茂绿茵草地大面积欠饱和严重脱色发暗，绿意褪变为枯黄暗色(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9607: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9610: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "摄影棚绿幕前头戴礼帽男子面部肤色大面积浸染失真红褐偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "男子面部肤色与背景绿幕色彩浓艳不自然。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "肤色偏深红破坏肖像摄影真实感。"}
    ],
    "review_note": "摄影棚绿幕前头戴礼帽男子面部肤色大面积浸染失真红褐偏色，色泽浓艳不自然(D-L2, E1-L2, F-L1)。"
  },

  # Sheet 14 (Tasks 9613, 9614, 9615, 9617, 9618, 9619)
  9613: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "烤三明治金黄面包皮与小番茄大面积欠饱和脱色发暗，微染冷青灰色调。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "白色餐盘表面微泛冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "三明治与红番茄欠饱和褪色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "食材脱色降低餐盘诱人质感。"}
    ],
    "review_note": "餐盘中烤三明治金黄面包皮与小番茄大面积欠饱和脱色发暗，微染冷青灰色调(C-L2, D-L1, E2-L1, F-L1)。"
  },
  9614: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9615: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "客房窗边木茶几与扶手椅阴影微染冷青灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "客房窗边木茶几背光处与单人扶手椅阴影细节色彩略显暗淡欠饱和。"}
    ],
    "review_note": "客房窗边木茶几背光处与单人扶手椅阴影细节色彩略显暗淡欠饱和，微染冷青灰偏色(D-L1, E2-L1)。"
  },
  9617: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9618: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "历史老照片背景天空被颠覆性错染为刺眼荧光青绿色，沙漠地面错染高饱和火红偏色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "天空与地面大面积泛恶性青绿与火红杂色。"},
      {"id": "E1", "name": "过饱和", "severity": "L3", "description": "荧光青绿与火红色彩极度浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "历史黑白照片被恶性艳色破坏殆尽。"}
    ],
    "review_note": "历史老照片背景天空被颠覆性错染为刺眼荧光青绿色，沙漠地面错染高饱和火红偏色(C-L3, D-L2, E1-L3, F-L3)。"
  },
  9619: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "足球场后方看台观众席大面积错染刺眼深洋红紫与深蓝伪色斑块。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "球员球服边缘微染深洋红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的深洋红紫杂色浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "看台伪色斑块严重破坏足球场整洁背景。"}
    ],
    "review_note": "足球场后方看台观众席大面积错染刺眼深洋红紫与深蓝伪色斑块(C-L2, D-L1, E1-L2, F-L2)。"
  },

  # Sheet 15 (Tasks 9621, 9624, 9625, 9627, 9628, 9629)
  9621: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "后院绿茵草坪大面积脱色错染为暗淡枯草黄色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "后方充气玩具微泛冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "足球门周边绿草地大面积欠饱和严重脱色变暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "草地脱色破坏后院生机盎然感。"}
    ],
    "review_note": "后院草坪上小型白色足球门周边绿茵草地大面积欠饱和严重脱色变暗，褪为枯草色(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9624: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9625: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9627: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "斑马腹底与远景树林微染冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "非洲草原斑马群腹底阴影与远景稀疏树林暗部色彩略显暗淡欠饱和。"}
    ],
    "review_note": "非洲草原斑马群腹底阴影与远景稀疏树林暗部色彩略显暗淡欠饱和，微染冷灰偏色(D-L1, E2-L1)。"
  },
  9628: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "户外青铜长椅雕塑与就坐老者面部肤色大面积浸染失真红褐偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "青铜长椅红褐色调略显浓艳溢出。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "青铜器泛红破坏金属厚重感。"}
    ],
    "review_note": "户外青铜长椅雕塑与就坐老者面部肤色大面积浸染失真红褐偏色，金属质感失真(D-L2, E1-L1, F-L1)。"
  },
  9629: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "硬地网球场浅色地面被颠覆性严重错染为刺眼高饱和深纯蓝色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "球场地面与球员球鞋大面积泛深冷纯蓝偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的深纯蓝地面极度浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "球场地板严重伪色完全破坏网球赛场真实感。"}
    ],
    "review_note": "硬地网球场浅色地面被颠覆性严重错染为刺眼高饱和深纯蓝色伪色(C-L3, D-L2, E1-L2, F-L2)。"
  },

  # Sheet 16 (Tasks 9632, 9635, 9636, 9637, 9639, 9641)
  9632: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "桌面左侧笔记本电脑屏幕原本鲜艳明亮的暖橙色光照彻底脱色褪变为冰冷白灰色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "桌面与电脑机身泛灰暗冷调偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "屏幕暖橙色彩完全丧失，严重欠饱和脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "屏幕脱色破坏两台电脑对比的视觉焦点。"}
    ],
    "review_note": "桌面左侧笔记本电脑屏幕原本鲜艳明亮的暖橙色光照彻底脱色褪变为冰冷白灰(C-L3, D-L2, E2-L3, F-L2)。"
  },
  9635: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9636: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9637: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "车窗外原本晴朗浅蓝的天空大面积脱色错染为灰白暗色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "车内座椅与狗狗毛发背阴处微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "天空浅蓝完全丧失，小狗毛发背光处暗淡欠饱和。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "天空苍白脱色降低画面自然采光感。"}
    ],
    "review_note": "车窗外原本晴朗浅蓝的天空大面积欠饱和脱色发白，小狗毛发背光处略显暗淡(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9639: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "公园木长椅后方大树树冠叶片大面积错染为失真暗红褐偏色斑块。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "树木枝干与后方建筑微泛暗红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的暗红树叶浓艳突兀。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "茂密大树错染红斑违背夏季绿树自然常理。"}
    ],
    "review_note": "公园木长椅后方大树树冠叶片大面积错染为失真暗红褐偏色斑块(C-L2, D-L1, E1-L2, F-L2)。"
  },
  9641: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "挂在铁丝网上的网球拍拍框大面积错染刺眼荧光粉紫与深蓝伪色斑块。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "铁丝网与球拍泛杂乱深蓝紫偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的粉紫深蓝杂色浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "球拍被严重伪色污染破坏器材真实感。"}
    ],
    "review_note": "挂在铁丝网上的网球拍拍框大面积错染刺眼荧光粉紫与深蓝伪色斑块(C-L2, D-L2, E1-L2, F-L3)。"
  },

  # Sheet 17 (Tasks 9642, 9643, 9644, 9645, 9652, 9653)
  9642: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9643: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "冲浪板背阴与浪花泡沫微染冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "海滩冲浪者手中冲浪板背阴转角处与海浪翻滚泡沫阴影色彩略显暗淡欠饱和。"}
    ],
    "review_note": "海滩冲浪者手中冲浪板背阴转角处与海浪翻滚泡沫阴影色彩略显暗淡欠饱和(D-L1, E2-L1)。"
  },
  9644: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "男子怀抱宠物犬金黄棕褐色毛发微泛红褐色偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "宠物犬背部毛发与羽绒服暗部细节略显暗淡欠饱和。"}
    ],
    "review_note": "男子怀抱宠物犬金黄棕褐色毛发微泛红褐色偏色，暗部层次略显暗淡(D-L1, E2-L1)。"
  },
  9645: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "微缩沙盘绿化草木微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "微缩沙盘模型中红色小火车车厢背光处与微缩绿化草木色彩略显暗淡欠饱和。"}
    ],
    "review_note": "微缩沙盘模型中红色小火车车厢背光处与微缩绿化草木色彩略显暗淡欠饱和(D-L1, E2-L1)。"
  },
  9652: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L3", "description": "卫生间洗手台镜框、瓷砖墙面与吊柜大面积浸染失真深冷青蓝偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "镜框暖木色完全丧失，严重欠饱和脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "卫浴空间大面积冰冷青蓝严重破坏室内整洁质感。"}
    ],
    "review_note": "卫生间洗手台镜框、瓷砖墙面与吊柜大面积浸染失真深冷青蓝偏色，严重欠饱和脱色发暗(D-L3, E2-L3, F-L3)。"
  },
  9653: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "逆光飞鸟少女仰望天空原本柔和的金黄晨曦被颠覆性错染为刺眼浓艳的深湖蓝水绿色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "整幅画面大面积泛浓重深湖蓝水绿偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的深湖蓝色彩浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "晨曦逆光被深冷水绿吞噬彻底破坏浪漫诗意。"}
    ],
    "review_note": "逆光飞鸟少女仰望天空原本柔和的金黄晨曦被颠覆性错染为刺眼浓艳的深湖蓝水绿色(C-L3, D-L2, E1-L2, F-L2)。"
  },

  # Sheet 18 (Tasks 9655, 9656, 9657, 9658, 9661, 9663)
  9655: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "街边停放本田摩托车红色油箱脱色错染为暗褐灰色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "摩托车车架与路面微染冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "大红油箱严重欠饱和脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "油箱褪色降低摩托车外观质感。"}
    ],
    "review_note": "街边停放本田摩托车红色油箱大面积欠饱和严重脱色发暗，褪变为暗褐灰色(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9656: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9657: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9658: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "室内小男孩浅蓝花纹衣物下摆与床褥大面积错染刺眼深洋红紫偏色与伪色斑块。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "床单与男孩衣物微泛洋红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的深洋红紫色彩浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "男孩衣物被恶性洋红杂斑污染。"}
    ],
    "review_note": "室内小男孩浅蓝花纹衣物下摆与床褥大面积错染刺眼深洋红紫偏色与伪色斑块(C-L2, D-L1, E1-L2, F-L2)。"
  },
  9661: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "水上船屋原本暗红色的实木外墙脱色错染为暗淡灰褐色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "自行车与水面微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "暗红实木外墙大面积欠饱和脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "红木船屋脱色破坏水乡温馨感。"}
    ],
    "review_note": "水上船屋原本暗红色的实木外墙大面积欠饱和脱色发暗，褪变为暗淡灰褐色(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9663: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "浅滩木船船舷底部原本鲜艳的粉红涂装脱色错染为浅粉灰白色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "船舷与海水微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "船舷粉红涂料大面积欠饱和脱色褪白。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "船体彩漆脱色降低渔船鲜亮感。"}
    ],
    "review_note": "浅滩木船船舷底部原本鲜艳的粉红红色涂装大面积欠饱和脱色褪白(C-L2, D-L1, E2-L1, F-L1)。"
  },

  # Sheet 19 (Tasks 9665, 9668, 9671, 9672, 9674, 9675)
  9665: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "就餐女子红色上衣暗部与窗外绿茵树木严重欠饱和脱色发暗。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "窗外树木微泛灰黄偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "红衣与窗外绿树色泽略显暗淡。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "绿树与服饰脱色影响就餐温馨氛围。"}
    ],
    "review_note": "餐厅窗边就餐女子红色上衣暗部与窗外绿茵树木大面积欠饱和脱色发暗(C-L2, D-L1, E2-L1, F-L1)。"
  },
  9668: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "西餐厅高脚香槟杯与深色木质餐桌大面积浸染失真浓艳的深洋红紫红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "餐桌与酒杯洋红紫红色调浓艳过度溢出。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "餐具与桌面浸染浓艳紫红破坏高端餐厅优雅感。"}
    ],
    "review_note": "西餐厅高脚香槟杯与深色木质餐桌大面积浸染失真浓艳的深洋红紫红偏色(D-L2, E1-L2, F-L2)。"
  },
  9671: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "公路边八角形STOP停止标志牌大红色底漆脱色错染为暗红褐色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "路面柏油与立柱微染冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "红色底漆大面积欠饱和脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "红漆脱色降低交通标志辨识度。"}
    ],
    "review_note": "公路边八角形STOP停止标志牌大红色底漆大面积欠饱和脱色褪变为暗红褐色(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9672: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L3", "description": "机场大厅米黄色大理石地面与商业区大面积欠饱和严重脱色，全图浸染冰冷灰青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "大理石暖黄色调完全丧失，严重欠饱和脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "大厅冰冷死灰严重破坏现代航站楼采光氛围。"}
    ],
    "review_note": "机场大厅米黄色大理石地面与商业区大面积欠饱和严重脱色，全图浸染冰冷灰青偏色(D-L3, E2-L3, F-L3)。"
  },
  9674: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "废旧家电堆积体大面积浸染失真暗红偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "木板车上堆叠的旧式电视机废旧家电大面积欠饱和严重脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "家电堆泛暗红杂色破坏艺术装置层次。"}
    ],
    "review_note": "木板车上堆叠的旧式电视机废旧家电大面积欠饱和严重脱色，微泛红褐杂色(D-L2, E2-L2, F-L2)。"
  },
  9675: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "快艇飞驰湖面原本清澈翠绿的水体彻底脱色错染为浑浊水泥灰死水。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "湖面大面积泛灰土黄偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "清澈翠绿水体色彩完全丧失，严重欠饱和脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "翠绿湖水变水泥灰死水彻底破坏湖光山色。"}
    ],
    "review_note": "快艇飞驰湖面原本清澈翠绿的水体彻底欠饱和严重脱色褪变为浑浊水泥灰死水(C-L3, D-L2, E2-L3, F-L3)。"
  },

  # Sheet 20 (Tasks 9677, 9678, 9682, 9683, 9684, 9685)
  9677: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9678: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "工业车间大型金属钢架与地面大面积浸染失真浓艳的深洋红橙偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "车间钢架橙红色调过于浓艳溢出。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "工业厂房泛深红橙严重破坏厂区真实光照。"}
    ],
    "review_note": "工业车间大型金属钢架与地面大面积浸染失真浓艳的深洋红橙偏色(D-L2, E1-L2, F-L2)。"
  },
  9682: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "原本明黄色的立柱电线杆被颠覆性错染为刺眼的荧光青绿色伪色，STOP牌红漆脱色发暗。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "电线杆立柱泛浓艳荧光青绿偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的荧光青绿色彩极其刺眼浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "电线杆错染荧光色严重违背市政设施常理。"}
    ],
    "review_note": "原本明黄色的立柱电线杆被颠覆性错染为刺眼的荧光青绿色伪色，STOP牌红漆脱色发暗(C-L3, D-L2, E1-L2, F-L2)。"
  },
  9683: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9684: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "烘焙烤炉口转角阴影微染冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "烘焙烤炉炉口转角阴影与师傅手套背阴处细节色彩略显暗淡欠饱和。"}
    ],
    "review_note": "烘焙烤炉炉口转角阴影与师傅手套背阴处细节色彩略显暗淡欠饱和，微染冷灰偏色(D-L1, E2-L1)。"
  },
  9685: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  }
}

def apply_batch_48():
    base_dir = r"d:\学业文件\MCL\上色评价_数据集标注\LS_lcad_reviewer"
    grounding_path = os.path.join(base_dir, "intermediate", "audits", "grounding_remaining_batch_48.json")
    all_path = os.path.join(base_dir, "exports", "reviewed_1_10000_all.json")
    clean_path = os.path.join(base_dir, "exports", "reviewed_1_10000_clean.json")

    # 1. 导出 grounding_remaining_batch_48.json
    with open(grounding_path, 'w', encoding='utf-8') as f:
        json.dump(BATCH_48_REVIEWS, f, indent=2, ensure_ascii=False)
    print(f"Saved grounding reviews to {grounding_path}")

    # 2. 读取全量文件
    with open(all_path, 'r', encoding='utf-8') as f:
        all_data = json.load(f)

    with open(clean_path, 'r', encoding='utf-8') as f:
        clean_data = json.load(f)

    # 建立 task_id 索引 (human_review.task_id)
    all_idx_map = {item['human_review']['task_id']: i for i, item in enumerate(all_data['annotations'])}
    clean_idx_map = {item['human_review']['task_id']: i for i, item in enumerate(clean_data['annotations'])}

    pass_count = 0
    revised_count = 0
    meltdown_count = 0

    for task_id, review in BATCH_48_REVIEWS.items():
        if task_id not in all_idx_map or task_id not in clean_idx_map:
            print(f"Warning: task_id {task_id} not found in annotations!")
            continue

        anno_all = all_data['annotations'][all_idx_map[task_id]]
        anno_clean = clean_data['annotations'][clean_idx_map[task_id]]

        action = review['action']
        defects = review['defects']
        review_note = review['review_note']

        if action == 'pass':
            pass_count += 1
            # 放行项: defects 清空, note 统一为 "审查通过"
            anno_all['defects'] = []
            anno_all['review_status'] = "已核验"
            anno_all['review_note'] = "审查通过"
            anno_all['reviewed_score'] = None
            anno_all['needs_rescoring'] = True

            anno_clean['defects'] = []
            anno_clean['review_status'] = "已核验"
            anno_clean['review_note'] = "审查通过"
            anno_clean['reviewed_score'] = None
            anno_clean['needs_rescoring'] = True

        elif action == 'meltdown_a':
            meltdown_count += 1
            # 熔断项A: reviewed_score 锁定 1.0, needs_rescoring False
            anno_all['defects'] = defects
            anno_all['review_status'] = "已核验"
            anno_all['review_note'] = review_note
            anno_all['reviewed_score'] = 1.0
            anno_all['needs_rescoring'] = False

            anno_clean['defects'] = defects
            anno_clean['review_status'] = "已核验"
            anno_clean['review_note'] = review_note
            anno_clean['reviewed_score'] = 1.0
            anno_clean['needs_rescoring'] = False

        else:
            revised_count += 1
            # 具象改判项
            anno_all['defects'] = defects
            anno_all['review_status'] = "已核验"
            anno_all['review_note'] = review_note
            anno_all['reviewed_score'] = None
            anno_all['needs_rescoring'] = True

            anno_clean['defects'] = defects
            anno_clean['review_status'] = "已核验"
            anno_clean['review_note'] = review_note
            anno_clean['reviewed_score'] = None
            anno_clean['needs_rescoring'] = True

    with open(all_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    with open(clean_path, 'w', encoding='utf-8') as f:
        json.dump(clean_data, f, indent=2, ensure_ascii=False)

    print("Batch 48 applied successfully!")
    print(f"Total: {len(BATCH_48_REVIEWS)}, Passes: {pass_count} ({pass_count/len(BATCH_48_REVIEWS)*100:.2f}%), Revised: {revised_count} ({revised_count/len(BATCH_48_REVIEWS)*100:.2f}%), Meltdown A: {meltdown_count}")

if __name__ == '__main__':
    apply_batch_48()
