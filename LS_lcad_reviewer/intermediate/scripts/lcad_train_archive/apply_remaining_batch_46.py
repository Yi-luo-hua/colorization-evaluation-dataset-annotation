import json
import os
import copy

BATCH_46_REVIEWS = {
  # Sheet 01 (Tasks 9090, 9091, 9092, 9093, 9095, 9097)
  9090: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "烛光女郎金发与面部轻微浸染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "温暖烛光氛围色调欠饱和略显暗淡。"}
    ],
    "review_note": "烛光女郎金发与面部轻微浸染冷青偏色，温暖烛光氛围色调欠饱和略显暗淡(D-L1, E2-L1)。"
  },
  9091: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "抱婴儿父亲与婴儿皮肤大面积浸染冷青蓝偏色。"}
    ],
    "review_note": "抱婴儿父亲与婴儿皮肤大面积浸染冷青蓝偏色(D-L1)。"
  },
  9092: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "阳光房浅黄实木窗框与立柱被颠覆性错染为深青蓝色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "室内木质结构大面积泛青蓝偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的深青蓝窗框色彩过于浓艳突兀。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "实木窗框错染蓝青严重破坏室内温馨采光与空间真实感。"}
    ],
    "review_note": "阳光房浅黄实木窗框与立柱被颠覆性错染为深青蓝色(C-L3, D-L2, E1-L2, F-L2)。"
  },
  9093: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9095: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9097: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 02 (Tasks 9098, 9100, 9102, 9104, 9106, 9107)
  9098: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "白色列车车身与站台边缘微泛冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "列车车身原本明亮的蓝色彩条与红色腰线严重欠饱和脱色发灰。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "车身彩绘腰线脱色降低了列车外观鲜明度。"}
    ],
    "review_note": "列车车身原本明亮的蓝色彩条与红色腰线严重脱色发灰(E2-L2, D-L1, F-L1)。"
  },
  9100: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "接飞盘草坪大面积错染为失真冰冷青蓝水绿色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "整片草地与天空大面积泛冷青偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的青蓝草地色彩过于艳丽失真。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "青蓝色草坪严重违背常识。"}
    ],
    "review_note": "接飞盘草坪大面积错染为失真冰冷青蓝水绿色(C-L2, D-L2, E1-L2, F-L2)。"
  },
  9102: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "棒球场看台观众席大面积错染失真深紫红伪色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "球场看台区域泛暗红紫偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "看台紫红杂斑色泽过于浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "看台紫红杂色破坏整体棒球场视觉自然度。"}
    ],
    "review_note": "棒球场看台观众席大面积错染失真深紫红伪色(C-L2, D-L2, E1-L1, F-L2)。"
  },
  9104: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "餐桌披萨表面颠覆性错染为刺眼高饱和荧光青蓝色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "披萨边缘与餐桌微泛冷青偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L3", "description": "错染的荧光青蓝伪色极其浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "食物被严重伪色污染，丧失食用真实感。"}
    ],
    "review_note": "餐桌披萨表面颠覆性错染为刺眼高饱和荧光青蓝色伪色(C-L3, E1-L3, D-L1, F-L3)。"
  },
  9106: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9107: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "消防栓旁地面圆形底座原本鲜艳的大红油漆脱色错染为灰白色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "地面人行道微泛冷青灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "大红油漆圆盘严重欠饱和脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "红漆底盘脱色影响视觉真实感。"}
    ],
    "review_note": "消防栓旁地面圆形底座原本鲜艳的大红油漆严重脱色为灰白色(C-L2, E2-L2, D-L1, F-L1)。"
  },

  # Sheet 03 (Tasks 9108, 9110, 9112, 9114, 9115, 9116)
  9108: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "沿街建筑外墙与马车车身轻微浸染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街头历史马车与沿街建筑老照片大面积脱色发灰。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "整体色彩层次欠缺，画面干瘪。"}
    ],
    "review_note": "街头历史马车与沿街建筑老照片大面积脱色发灰(E2-L2, D-L1, F-L1)。"
  },
  9110: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9112: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "停车计时器上方原本极其鲜艳的亮荧光翠绿青蛙玩具颠覆性脱色错染为灰白暗色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "计时器金属立柱微泛冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "亮翠绿青蛙玩具翠绿油漆完全脱色干瘪。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "主体玩具色彩彻底丧失。"}
    ],
    "review_note": "停车计时器上方原本极其鲜艳的亮荧光翠绿青蛙玩具颠覆性脱色错染为灰白暗色(C-L3, E2-L3, D-L1, F-L2)。"
  },
  9114: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9115: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9116: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "蛋糕包装纸盒与餐具轻微浸染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "生日蛋糕彩色细蜡烛色泽略显暗淡欠饱和。"}
    ],
    "review_note": "生日蛋糕彩色细蜡烛色泽略显暗淡欠饱和，包装纸盒轻微浸染冷青偏色(D-L1, E2-L1)。"
  },

  # Sheet 04 (Tasks 9118, 9123, 9124, 9127, 9128, 9131)
  9118: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "九宫格拼接图客房床铺与卫生间小图微染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "客房装饰画与家具细节欠饱和暗淡。"}
    ],
    "review_note": "九宫格拼接图客房床铺与卫生间小图微染冷青偏色且暗淡(D-L1, E2-L1)。"
  },
  9123: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "棒球击球手原本青绿球衣与头盔颠覆性错染为鲜亮天蓝色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "球场地面与护栏微泛冷蓝偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的天蓝球服色彩过艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "运动员球服严重错色。"}
    ],
    "review_note": "棒球击球手原本青绿球衣与头盔颠覆性错染为鲜亮天蓝色(C-L3, E1-L2, D-L1, F-L2)。"
  },
  9124: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "打字机按键缝隙与金属底板错染失真深洋红伪色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "打字机机身大面积泛洋红暗红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "洋红暗斑色泽突兀。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "金属机械结构错染杂色。"}
    ],
    "review_note": "打字机按键缝隙与底板错染失真深洋红伪色(C-L2, D-L2, E1-L1, F-L1)。"
  },
  9127: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "钟楼周围天空与绿植轻微泛冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "古典钟楼红砖外墙大面积欠饱和严重脱色为暗淡冷青灰色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "红砖建筑脱色损害历史建筑厚重感。"}
    ],
    "review_note": "古典钟楼红砖外墙大面积欠饱和严重脱色为暗淡冷青灰色(E2-L2, D-L1, F-L1)。"
  },
  9128: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "餐桌左侧鲜红调味挤酱瓶颠覆性错染脱色为苍白浅粉白色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "餐桌台面与木椅泛青冷偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "红色酱料瓶严重褪色干瘪。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "鲜红酱瓶褪色严重破坏就餐色彩自然度。"}
    ],
    "review_note": "餐桌左侧鲜红调味挤酱瓶颠覆性错染脱色为苍白浅粉白色(C-L3, E2-L2, D-L2, F-L2)。"
  },
  9131: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 05 (Tasks 9132, 9134, 9135, 9136, 9138, 9141)
  9132: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "长条实木吧台与油烟机金属表面大面积浸染失真暗红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "木质吧台暗红偏色过于浓烈。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "厨房台面泛红失真。"}
    ],
    "review_note": "长条实木吧台与油烟机金属表面大面积浸染失真暗红偏色(D-L2, E1-L2, F-L1)。"
  },
  9134: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "卫生间白色浴缸与大理石瓷砖墙面错染失真暗洋红偏色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "瓷砖阴影泛洋红杂色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "暗洋红杂色色泽过重。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "卫生间洁具泛红影响整洁观感。"}
    ],
    "review_note": "卫生间白色浴缸与大理石瓷砖墙面错染失真暗洋红偏色(C-L2, D-L1, E1-L1, F-L1)。"
  },
  9135: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "庆典儿童原本鲜艳大红金色长袍被颠覆性错染为深洋红粉紫色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "儿童服饰边缘微泛青冷。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的深洋红过于刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "传统庆典红色服饰错染严重违背原义。"}
    ],
    "review_note": "庆典儿童原本鲜艳大红金色长袍被颠覆性错染为深洋红粉紫色(C-L3, E1-L2, D-L1, F-L2)。"
  },
  9136: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "儿童卡通动车蛋糕表面糖霜文字与奶油装饰错染失真深洋红杂色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "蛋糕托盘边缘泛暗紫偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "深洋红杂色对比过于强烈。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "儿童蛋糕装饰奶油错色突兀。"}
    ],
    "review_note": "儿童卡通动车蛋糕表面糖霜文字与奶油装饰错染失真深洋红杂色(C-L2, E1-L2, D-L1, F-L2)。"
  },
  9138: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "餐桌男士浅蓝衬衫轻微浸染冷青紫偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "餐盘烤披萨色泽略显暗淡欠饱和。"}
    ],
    "review_note": "餐桌男士浅蓝衬衫轻微浸染冷青紫偏色，披萨欠饱和(D-L1, E2-L1)。"
  },
  9141: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 06 (Tasks 9142, 9144, 9145, 9146, 9147, 9148)
  9142: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "木棚阴影与地面轻微浸染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "小牛犊棕黄毛发色泽欠饱和暗淡。"}
    ],
    "review_note": "小牛犊毛发欠饱和暗淡，木棚阴影泛冷偏色(D-L1, E2-L1)。"
  },
  9144: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9145: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "洗手台瓷砖台面与镜面边缘轻微浸染冷青偏色。"}
    ],
    "review_note": "洗手台瓷砖台面与镜面边缘轻微浸染冷青偏色(D-L1)。"
  },
  9146: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "厨房白色吊柜与天花板缝隙错染暗洋红紫伪色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "吊柜背阴处泛紫红杂斑。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "错染的紫红杂色对比略显浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "白色吊柜缝隙杂色影响整洁度。"}
    ],
    "review_note": "厨房白色吊柜与天花板缝隙错染暗洋红紫伪色(C-L2, D-L1, E1-L1, F-L1)。"
  },
  9147: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "怀抱巨大毛绒泰迪熊原本棕黄毛色被颠覆性错染为枯暗青灰土黄色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "毛绒熊身躯大面积泛冷青灰土黄色偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "玩具熊暖黄毛色严重脱色发灰。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "毛绒玩具色彩严重失真发枯。"}
    ],
    "review_note": "怀抱巨大毛绒泰迪熊原本棕黄毛色被颠覆性错染为枯暗青灰土黄色(C-L3, D-L2, E2-L2, F-L2)。"
  },
  9148: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "长颈鹿斑纹与枯草轻微浸染暖红黄偏色。"}
    ],
    "review_note": "长颈鹿斑纹与枯草轻微浸染暖红黄偏色(D-L1)。"
  },

  # Sheet 07 (Tasks 9152, 9153, 9154, 9156, 9157, 9158)
  9152: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9153: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9154: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "黄牛后方竹林草地背景错染为大面积刺眼荧光青绿色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "背景植被大面积泛冷青绿偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "青绿背景色彩过于浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "荧光绿背景破坏农田自然氛围。"}
    ],
    "review_note": "黄牛后方竹林草地背景错染为大面积刺眼荧光青绿色(C-L2, D-L2, E1-L2, F-L2)。"
  },
  9156: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "路口STOP停车标牌大面积欠饱和严重脱色褪变为暗淡灰粉色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "路牌边缘微泛冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "鲜红交通路标底色严重脱色发白。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "交通警示标志鲜明度受损。"}
    ],
    "review_note": "路口STOP停车标牌大面积欠饱和严重脱色褪变为暗淡灰粉色(C-L2, E2-L2, D-L1, F-L1)。"
  },
  9157: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9158: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 08 (Tasks 9160, 9161, 9162, 9163, 9164, 9165)
  9160: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9161: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "农场红色木板仓房门框轻微浸染洋红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "仓房木板红色漆面略显浓艳。"}
    ],
    "review_note": "农场红色木板仓房门框色泽略显浓艳偏洋红调(D-L1, E1-L1)。"
  },
  9162: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "车厢内壁与地面轻微浸染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "车厢黄色扶手与青年内搭深绿短袖色泽欠饱和略显暗淡。"}
    ],
    "review_note": "车厢黄色扶手与青年内搭深绿短袖欠饱和暗淡，内壁泛冷青偏色(D-L1, E2-L1)。"
  },
  9163: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9164: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "木棚下两头大象身躯大面积浸染失真火红暖褐偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "大象皮肤暖红偏色过于浓郁。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "灰象皮肤泛红失真违背常理。"}
    ],
    "review_note": "木棚下两头大象身躯大面积浸染失真火红暖褐偏色(D-L2, E1-L2, F-L2)。"
  },
  9165: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "户外天蓝色折叠遮阳伞伞面错染失真深洋红伪色斑块。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "遮阳伞伞布与地面泛洋红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "洋红杂色对比过于突兀浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "蓝色遮阳伞错染大块深红伪色。"}
    ],
    "review_note": "户外天蓝色折叠遮阳伞伞面错染失真深洋红伪色斑块(C-L2, D-L2, E1-L2, F-L2)。"
  },

  # Sheet 09 (Tasks 9166, 9168, 9170, 9172, 9173, 9174)
  9166: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "卫生间白色洁具与地面微泛冷青偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "卫生间蓝色墙面瓷砖与浴缸台面色泽过于浓艳刺眼。"}
    ],
    "review_note": "卫生间蓝色墙面瓷砖与浴缸台面色泽过于浓艳刺眼(D-L1, E1-L2)。"
  },
  9168: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "餐桌上白色餐盘背景与折叠餐巾被错染为刺眼高饱和荧光青绿与蓝紫色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "桌面餐具阴影泛蓝紫偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L3", "description": "错染的荧光青绿与蓝紫杂色极度浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "餐具与餐巾严重错染多色伪色破坏就餐真实度。"}
    ],
    "review_note": "餐桌上白色餐盘背景与折叠餐巾被错染为刺眼高饱和荧光青绿与蓝紫色伪色(C-L2, E1-L3, D-L1, F-L3)。"
  },
  9170: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "彩色毛绒小狗与汉堡玩具被严重颠覆性错染为刺眼火红洋红杂色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "玩具表面整体泛深红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L3", "description": "错染的火红洋红杂色对比过于强烈刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "毛绒玩具多处错色严重失真。"}
    ],
    "review_note": "彩色毛绒小狗与汉堡玩具被严重颠覆性错染为刺眼火红洋红杂色(C-L3, D-L2, E1-L3, F-L3)。"
  },
  9172: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9173: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "现代客厅右侧墙面与天花板微泛紫红杂色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "长条实木茶几与沙发色调略显暗淡欠饱和。"}
    ],
    "review_note": "现代客厅实木茶几与沙发右侧墙面微泛紫红杂色，色调欠饱和(D-L1, E2-L1)。"
  },
  9174: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "客机客舱内壁与走廊地面微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "客舱走廊旅客衣物与头顶行李架细节略显暗淡欠饱和。"}
    ],
    "review_note": "客机机舱走廊旅客衣物与头顶行李架细节略显暗淡欠饱和，微染冷青灰色调(D-L1, E2-L1)。"
  },

  # Sheet 10 (Tasks 9178, 9180, 9181, 9182, 9184, 9188)
  9178: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9180: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "背景草地与皮卡车身轻微浸染暖黄偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "棕马毛发与红色缰绳色泽偏浓艳偏红。"}
    ],
    "review_note": "棕马毛发与红色缰绳色泽偏浓艳偏红，背景草地轻微浸染暖黄偏色(D-L1, E1-L1)。"
  },
  9181: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "踢足球小男孩原本鲜艳的亮天蓝色运动球衣被错染为深灰青蓝色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "足球场草坪边缘轻微泛黄偏色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "球衣错色降低了运动赛场色彩鲜明度。"}
    ],
    "review_note": "踢足球小男孩原本鲜艳的亮天蓝色运动球衣被错染为深灰青蓝色，草坪轻微泛黄(C-L2, D-L1, F-L1)。"
  },
  9182: {
    "action": "revise",
    "defects": [
      {"id": "B", "name": "溢色", "severity": "L2", "description": "刺眼杂色在骑兵人物与马匹身躯轮廓处互相溢出渗透。"},
      {"id": "C", "name": "错色", "severity": "L2", "description": "黑白老照片背景被荒谬错染为杂乱多色斑块。"},
      {"id": "D", "name": "偏色", "severity": "L3", "description": "画面整体浸染刺眼波普多色失真偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L3", "description": "荧光红黄蓝多色伪色极度刺眼过饱和。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "历史照片被恶性杂色污染极度失真。"}
    ],
    "review_note": "骑兵与马匹黑白历史照片背景与身躯被大面积错染刺眼杂乱的荧光红黄蓝多色伪色斑块，色彩极度失真(B-L2, C-L2, D-L3, E1-L3, F-L3)。"
  },
  9184: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "大教堂白色双塔外墙与晴朗天空大面积浸染灰黄暖色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "蓝天原本青蓝色调脱色发灰。"}
    ],
    "review_note": "大教堂白色双塔外墙与晴朗天空大面积浸染灰黄暖色调，蓝天原本青蓝色调脱色发灰(D-L1, E2-L1)。"
  },
  9188: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "桌面与阴影边缘轻微浸染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "手持智能手机的手臂肤色与深色护腕欠饱和发灰发暗。"}
    ],
    "review_note": "手持智能手机的手臂肤色与深色护腕欠饱和发灰发暗，桌面与阴影轻微浸染冷青偏色(D-L1, E2-L1)。"
  },

  # Sheet 11 (Tasks 9189, 9190, 9191, 9193, 9194, 9195)
  9189: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "观光电瓶车前脸保险杠区域原本鲜明的亮黄色严重脱色错染为灰白色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "车身阴影微泛冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "前保险杠黄色油漆完全脱色发白。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "游览车鲜明色彩丧失。"}
    ],
    "review_note": "观光电瓶车前脸保险杠区域原本鲜明的亮黄色严重脱色错染为灰白色(C-L2, E2-L2, D-L1, F-L1)。"
  },
  9190: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "晴朗天空大面积被颠覆性错染为失真浑浊的青绿色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "整幅画面大面积浸染浑浊青绿偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的青绿天空过于浓艳失真。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "蓝天常识性错染为绿天严重破坏真实感。"}
    ],
    "review_note": "晴朗天空大面积被颠覆性错染为失真浑浊的青绿色，长途大客车车身浸染冷青偏色(C-L3, D-L2, E1-L2, F-L2)。"
  },
  9191: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "男士身穿的亮宝蓝色卫衣被颠覆性脱色错染为暗淡灰黑色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "男女面部肤色泛冷青灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "宝蓝色连帽卫衣严重脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "人物衣服明亮色彩彻底丧失。"}
    ],
    "review_note": "男士身穿的亮宝蓝色卫衣被颠覆性脱色错染为暗淡灰黑色，男女面部肤色泛冷青灰(C-L3, E2-L2, D-L1, F-L2)。"
  },
  9193: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "厨房浅黄墙面与不锈钢冰箱整体色调略显单一泛暖黄。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "操作台面塑料袋与杂物色彩轻微欠饱和。"}
    ],
    "review_note": "厨房浅黄墙面与不锈钢冰箱整体色调略显单一泛暖黄，台面塑料袋与杂物色彩轻微欠饱和(D-L1, E2-L1)。"
  },
  9194: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "门廊阴影与门框轻微浸染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "红色木质大门与金毛犬金黄毛发色泽略显暗淡欠饱和。"}
    ],
    "review_note": "红色木质大门与金毛犬金黄毛发色泽略显暗淡欠饱和，门廊阴影轻微浸染冷青偏色(D-L1, E2-L1)。"
  },
  9195: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "蛋糕阴影缝隙微泛冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "翻糖手提箱蛋糕提手与深色皮带细节略显暗淡欠饱和。"}
    ],
    "review_note": "翻糖手提箱蛋糕提手与深色皮带细节略显暗淡欠饱和，阴影缝隙微泛冷青偏色(D-L1, E2-L1)。"
  },

  # Sheet 12 (Tasks 9196, 9197, 9198, 9201, 9202, 9204)
  9196: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "远景奔跑同伴原本鲜艳的蓝色与橙色衣物脱色错染发暗。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "大草坡草地整体偏枯黄。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "倾斜大草坡严重欠饱和褪色发黄。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "草坪与人物衣物色彩干瘪。"}
    ],
    "review_note": "倾斜大草坡严重欠饱和褪色发黄，远景奔跑同伴原本鲜艳的蓝色与橙色衣物脱色发暗(C-L2, E2-L2, D-L1, F-L1)。"
  },
  9197: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "三位女士衣物暗部与背景微泛暗紫偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "聚会昏暗光线下女士发丝与衣物层次略显单一欠饱和。"}
    ],
    "review_note": "聚会昏暗光线下三位年轻女士发丝与衣物暗部层次略显单一微泛暗紫偏色(D-L1, E2-L1)。"
  },
  9198: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "海景露台远方地平线原本绚烂的落日橙红晚霞严重脱色褪变为灰白。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "海水与天空泛暗冷青灰。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "晚霞橙红暖金霞光彻底脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "傍晚海景丧失霞光氛围。"}
    ],
    "review_note": "海景露台远方地平线原本绚烂的落日橙红晚霞严重脱色发灰，海水与天空色调暗淡(C-L2, E2-L2, D-L1, F-L1)。"
  },
  9201: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "酒店大堂立柱与大理石地面大面积浸染失真深洋红紫偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "红色圣诞树色泽过于浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "大厅洋红偏色破坏室内自然光照感。"}
    ],
    "review_note": "酒店大堂立柱与大理石地面大面积浸染失真深洋红紫偏色，红色圣诞树过于浓艳刺眼(D-L2, E1-L1, F-L1)。"
  },
  9202: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "雨中奔跑女士撑的大红雨伞表面大面积脱色错染为暗淡灰粉色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "地面广场水泊微泛青灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "大红伞面原本极其鲜艳明烈的色彩严重欠饱和褪色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "雨伞红色脱色降低视觉焦点冲击力。"}
    ],
    "review_note": "雨中奔跑女士撑的大红雨伞表面严重欠饱和脱色为暗淡灰粉色，翠绿裙裾轻微发灰(C-L2, E2-L2, D-L1, F-L1)。"
  },
  9204: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 13 (Tasks 9205, 9206, 9208, 9209, 9210, 9212)
  9205: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "厨房木质橱柜与操作台面阴影微染暖红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "橱柜浅木板面色泽略显偏红浓艳。"}
    ],
    "review_note": "厨房木质橱柜与操作台面色调略显偏红浓艳，阴影微染暖红偏色(D-L1, E1-L1)。"
  },
  9206: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "活动板房白色墙壁与地面微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "木质办公桌与饮水机色彩略显暗淡欠饱和。"}
    ],
    "review_note": "活动板房白色墙壁与木质办公桌色彩略显暗淡欠饱和，微染冷青灰色调(D-L1, E2-L1)。"
  },
  9208: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "沙发靠背与暗部微染冷暗灰调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "女士针织开衫暗部色彩略显单调暗淡。"}
    ],
    "review_note": "沙发靠背与女士针织开衫暗部色彩略显单调暗淡，微染冷暗灰调(D-L1, E2-L1)。"
  },
  9209: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9210: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "男士面部背阴处与背景微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "烛光后方男士白色衬衫与阴影细节略显暗淡欠饱和。"}
    ],
    "review_note": "烛光后方男士面部阴影与白色衬衫细节略显暗淡欠饱和，微染冷青灰色调(D-L1, E2-L1)。"
  },
  9212: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "不锈钢餐盘内原本微黄的烘焙点心被颠覆性错染为极其刺眼失真的高饱和荧光亮绿色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "金属餐盘边缘微泛荧光绿反光。"},
      {"id": "E1", "name": "过饱和", "severity": "L3", "description": "错染的荧光亮绿伪色极其浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "点心被荧光绿伪色严重污染，丧失食物可食性。"}
    ],
    "review_note": "不锈钢餐盘内原本微黄的烘焙点心被颠覆性错染为极其刺眼失真的高饱和荧光亮绿色伪色(C-L3, E1-L3, D-L1, F-L3)。"
  },

  # Sheet 14 (Tasks 9213, 9215, 9216, 9218, 9222, 9224)
  9213: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "路旁草地与背景树林略显暗淡偏黄。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "骑车女士深色连帽卫衣色泽欠饱和褪色发灰。"}
    ],
    "review_note": "骑车女士深色连帽卫衣色泽欠饱和褪色发灰，路旁草地略显暗淡偏黄(D-L1, E2-L1)。"
  },
  9215: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9216: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9218: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "公园长椅原本鲜艳的浅天蓝色木条被错染为深灰青蓝色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "狸花猫背部毛色微泛冷发暗。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "木长椅原本明媚天蓝色彩欠饱和。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "长椅蓝漆错色偏暗。"}
    ],
    "review_note": "公园长椅原本鲜艳的浅天蓝色木条被错染为深灰青蓝色，狸花猫背部毛色略显暗淡发冷(C-L2, D-L1, E2-L1, F-L1)。"
  },
  9222: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "街边店铺深棕色木质橱窗门框被局部错染为失真泛冷的青绿杂色斑块。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "橱窗边缘泛冷青绿偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "青绿杂色斑块色泽略显突兀。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "木质门框出现青绿杂色严重破坏建筑质感。"}
    ],
    "review_note": "街边店铺深棕色木质橱窗门框被局部错染为失真泛冷的青绿杂色斑块(C-L2, D-L1, E1-L1, F-L2)。"
  },
  9224: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 15 (Tasks 9226, 9227, 9228, 9229, 9230, 9233)
  9226: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "雪地背阴处与树枝阴影微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "积雪覆盖的STOP停车标志牌红色底漆细节略显暗淡欠饱和。"}
    ],
    "review_note": "积雪覆盖的STOP停车标志牌红色底漆与雪地背阴处细节略显暗淡欠饱和，微染冷青灰色调(D-L1, E2-L1)。"
  },
  9227: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "老式客车车身原本明艳夺目的大红车顶与明黄侧围涂装被毁灭性脱色褪变为一片惨白灰暗。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "路边荒草轻微浸染冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "客车绚丽的红黄绿多色涂装全部丧失，严重欠饱和。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "客车关键色彩彻底丢失。"}
    ],
    "review_note": "老式客车车身原本明艳夺目的大红车顶与明黄侧围涂装被毁灭性脱色褪变为一片惨白灰暗(C-L3, E2-L3, D-L1, F-L2)。"
  },
  9228: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9229: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "晴朗天空边缘轻微浸染冷青灰调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "草坪与椰子树叶片色彩略显暗淡欠饱和。"}
    ],
    "review_note": "草坪与椰子树叶片色彩略显暗淡欠饱和，天空边缘轻微浸染冷青灰调(D-L1, E2-L1)。"
  },
  9230: {
    "action": "revise",
    "defects": [
      {"id": "B", "name": "溢色", "severity": "L2", "description": "卫生间红黄绿多色拼贴马赛克瓷砖接缝处存在明显色料越界溢色与杂色渗透。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "瓷砖暗缝泛暗红杂斑。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "部分红色马赛克色泽稍显浓重。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "马赛克拼贴缝隙杂色导致边缘视觉模糊杂乱。"}
    ],
    "review_note": "卫生间红黄绿多色拼贴马赛克瓷砖接缝处存在明显色料越界溢色与杂色渗透，视觉边缘杂乱(B-L2, D-L1, E1-L1, F-L2)。"
  },
  9233: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "长颈鹿身躯阴影处轻微浸染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "长颈鹿头部棕褐色斑纹与背景草地欠饱和脱色发灰。"}
    ],
    "review_note": "长颈鹿头部棕褐色斑纹与背景草地欠饱和脱色发灰，阴影轻微浸染冷青偏色(D-L1, E2-L1)。"
  },

  # Sheet 16 (Tasks 9236, 9238, 9239, 9240, 9243, 9245)
  9236: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9238: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "草地旁的明黄色消防栓原本鲜艳明丽的黄色漆面被颠覆性脱色褪变为一片灰白。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "背景路面泛冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "消防栓明黄色彩与草地完全欠饱和脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "消防栓关键警示色彩完全脱失。"}
    ],
    "review_note": "草地旁的明黄色消防栓原本鲜艳明丽的黄色漆面被颠覆性脱色褪变为一片灰白(C-L3, E2-L3, D-L1, F-L2)。"
  },
  9239: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9240: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "卫生间温馨暖黄色墙面瓷砖大面积浸染失真冷青蓝灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "陶瓷洗手池与实木镜框暗淡发灰，欠饱和严重。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "整间卫生间冷青偏色严重破坏采光氛围。"}
    ],
    "review_note": "卫生间温馨暖黄色墙面瓷砖大面积浸染失真冷青蓝灰偏色，陶瓷洗手池暗淡发灰(D-L2, E2-L2, F-L2)。"
  },
  9243: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9245: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "边缘皮尺与阴影微染冷调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "瓷盘内烤披萨饼皮色泽略显暗淡欠饱和。"}
    ],
    "review_note": "瓷盘内烤披萨饼皮色泽略显暗淡欠饱和，边缘皮尺与阴影微染冷调(D-L1, E2-L1)。"
  },

  # Sheet 17 (Tasks 9246, 9247, 9248, 9249, 9250, 9251)
  9246: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "皑皑雪地与背景浸染冰冷青蓝偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "雪地中小动物棕黄毛发严重脱色发灰。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "小动物脱色且雪地泛蓝失真。"}
    ],
    "review_note": "雪地中小动物棕黄毛发严重脱色发灰，皑皑雪地与背景浸染冰冷青蓝偏色(D-L2, E2-L2, F-L2)。"
  },
  9247: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "沙发睡垫阴影微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "熟睡小猫毛色与沙发睡垫暗部层次略显暗淡欠饱和。"}
    ],
    "review_note": "熟睡小猫毛色与沙发睡垫暗部层次略显暗淡欠饱和，微染冷青灰色调(D-L1, E2-L1)。"
  },
  9248: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9249: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9250: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "卫生间嵌入式浴缸台面与陶瓷内壁大面积浸染失真冷青蓝偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "浴缸边缘冷青蓝偏色过于浓郁。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "白色浴缸被染上青蓝反光。"}
    ],
    "review_note": "卫生间嵌入式浴缸台面与陶瓷内壁大面积浸染失真冷青蓝偏色(D-L1, E1-L2, F-L1)。"
  },
  9251: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "酒店卧室原本温暖明亮的暖金黄照明与墙面大面积脱色褪变为冰冷灰白色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "温暖灯光与金黄墙面严重脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "暖黄卧室变冷灰严重违背照明氛围。"}
    ],
    "review_note": "酒店卧室原本温暖明亮的暖金黄照明与墙面大面积脱色褪变为冰冷灰白色(D-L2, E2-L2, F-L2)。"
  },

  # Sheet 18 (Tasks 9252, 9253, 9254, 9255, 9256, 9257)
  9252: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9253: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "现代客厅白色墙壁、天花板与沙发大面积浸染失真深洋红紫偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "洋红偏色在白墙上对比突兀。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "客厅白墙泛紫红破坏自然采光。"}
    ],
    "review_note": "现代客厅白色墙壁、天花板与沙发大面积浸染失真深洋红紫偏色(D-L2, E1-L1, F-L1)。"
  },
  9254: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "自拍男士背景微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "男士面部肤色与黑白领结暗部细节略显暗淡欠饱和。"}
    ],
    "review_note": "自拍男士面部肤色与黑白领结暗部细节略显暗淡欠饱和，微染冷青灰色调(D-L1, E2-L1)。"
  },
  9255: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "窗边盆栽绿植与装饰公鸡雕塑被错染刺眼荧光青绿与洋红伪色斑块。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "窗台台面泛冷青偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "荧光绿杂色过于刺眼过饱和。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "盆栽植物伪色严重违和。"}
    ],
    "review_note": "窗边盆栽绿植与装饰公鸡雕塑被错染刺眼荧光青绿与洋红伪色斑块(C-L2, E1-L2, D-L1, F-L2)。"
  },
  9256: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9257: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "滑板场天空轻微泛冷偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "滑板公园U型池赛道暖黄色板面欠饱和脱色发灰。"}
    ],
    "review_note": "滑板公园U型池赛道暖黄色板面欠饱和脱色发灰，天空轻微泛冷偏色(D-L1, E2-L1)。"
  },

  # Sheet 19 (Tasks 9258, 9260, 9262, 9263, 9264, 9267)
  9258: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "动物标本展厅背景墙壁原本柔和的草绿色被颠覆性错染为刺眼失真的深橙红色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "展厅地面与背景大面积泛深橙红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "深橙红色背景墙过于浓艳失真。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "背景墙错色严重违背展馆柔和绿景。"}
    ],
    "review_note": "动物标本展厅背景墙壁原本柔和的草绿色被颠覆性错染为刺眼失真的深橙红色伪色(C-L2, D-L2, E1-L2, F-L2)。"
  },
  9260: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9262: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "卫生间浅青色墙面瓷砖与镜前灯光照被严重错染为枯暗泛黄偏色，色温严重失真。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "墙面瓷砖欠饱和发黄变暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "冷青瓷砖变暖黄，色温严重漂移。"}
    ],
    "review_note": "卫生间浅青色墙面瓷砖与镜前灯光照被严重错染为枯暗泛黄偏色，色温严重失真(D-L2, E2-L1, F-L1)。"
  },
  9263: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9264: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9267: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "起居室墙壁与阴影微染冷暗偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "老式电视机与音响暗部层次略显暗淡欠饱和。"}
    ],
    "review_note": "室内起居室老式电视机与音响暗部层次略显暗淡欠饱和，墙壁微染冷暗偏色(D-L1, E2-L1)。"
  },

  # Sheet 20 (Tasks 9269, 9270, 9271, 9272, 9273, 9276)
  9269: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9270: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "室内接待处木质收银柜台与后方墙面大面积浸染失真深洋红紫偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "柜台洋红偏色过于浓烈刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "木质柜台泛洋红失真。"}
    ],
    "review_note": "室内接待处木质收银柜台与后方墙面大面积浸染失真深洋红紫偏色(D-L1, E1-L2, F-L1)。"
  },
  9271: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "遮阳伞下阴影浸染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "露天咖啡座后方绿化树木与店面大面积脱色褪变为枯黄色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "绿树枯黄失真破坏街景生机。"}
    ],
    "review_note": "露天咖啡座后方绿化树木与店面大面积脱色褪变为枯黄色，遮阳伞下阴影浸染冷青灰色调(D-L2, E2-L2, F-L2)。"
  },
  9272: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9273: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "床头堆放的原本鲜红夺目的羽绒服外套大面积脱色错染为暗淡砖红灰色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "床头木板阴影微泛冷调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "鲜红羽绒服严重欠饱和脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "红色外套褪色暗淡。"}
    ],
    "review_note": "床头堆放的原本鲜红夺目的羽绒服外套大面积欠饱和严重脱色褪变为暗淡砖红灰色(C-L2, E2-L2, D-L1, F-L1)。"
  },
  9276: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "棒球场后方防守球员身穿的原本极其醒目的大红运动球衣与大红头盔被彻底脱色错染为枯暗发灰。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "球场泥土地面微泛冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "大红头盔与红色运动服完全丧失鲜明红色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "运动员关键识别红色彻底脱色。"}
    ],
    "review_note": "棒球场后方防守球员身穿的原本极其醒目的大红运动球衣与大红头盔被彻底脱色错染为枯暗发灰(C-L3, E2-L3, D-L1, F-L2)。"
  }
}

def apply_batch_46():
    # 1. 保存 grounding_remaining_batch_46.json
    out_grounding = 'LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_46.json'
    with open(out_grounding, 'w', encoding='utf-8') as f:
        json.dump(BATCH_46_REVIEWS, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(BATCH_46_REVIEWS)} reviews to {out_grounding}")

    # 2. 读取并增量更新 reviewed_1_10000_all.json 和 reviewed_1_10000_clean.json
    all_path = 'LS_lcad_reviewer/exports/reviewed_1_10000_all.json'
    clean_path = 'LS_lcad_reviewer/exports/reviewed_1_10000_clean.json'

    all_data = json.load(open(all_path, 'r', encoding='utf-8'))
    clean_data = json.load(open(clean_path, 'r', encoding='utf-8'))

    # 构建 task_id 索引映射
    all_anno_map = {anno['human_review']['task_id']: anno for anno in all_data['annotations']}
    clean_anno_map = {anno['human_review']['task_id']: anno for anno in clean_data['annotations']}

    pass_count = 0
    revised_count = 0
    meltdown_count = 0

    for task_id, review in BATCH_46_REVIEWS.items():
        anno_all = all_anno_map[task_id]
        anno_clean = clean_anno_map[task_id]

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

    print("Batch 46 applied successfully!")
    print(f"Total: {len(BATCH_46_REVIEWS)}, Passes: {pass_count} ({pass_count/len(BATCH_46_REVIEWS)*100:.2f}%), Revised: {revised_count} ({revised_count/len(BATCH_46_REVIEWS)*100:.2f}%), Meltdown A: {meltdown_count}")

if __name__ == '__main__':
    apply_batch_46()
