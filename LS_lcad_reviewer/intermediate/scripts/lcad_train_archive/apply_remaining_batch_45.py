import json
import os
import copy

BATCH_45_REVIEWS = {
  # Sheet 01 (Tasks 8903, 8905, 8907, 8910, 8911, 8912)
  8903: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "窗台浅木色板面与背景米黄墙面轻微浸染冷青蓝偏色。"}
    ],
    "review_note": "窗台浅木色板面与背景米黄墙面轻微浸染冷青蓝偏色(D-L1)。"
  },
  8905: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  8907: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "地面印花地毯复杂几何花纹大面积浸染失真冷青灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "地面印花地毯暖褐色花纹严重欠饱和脱色为干瘪灰黑色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "地毯脱色严重损害室内地面真实视觉观感。"}
    ],
    "review_note": "地面印花地毯复杂暖褐色几何花纹大面积欠饱和严重脱色为干瘪灰黑色(E2-L2)，浸染冷灰偏色(D-L2)。"
  },
  8910: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  8911: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  8912: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "餐桌白布与背景餐具大面积浸染失真冷青蓝偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "餐桌玻璃水杯中黄色鲜果汁严重欠饱和脱色发灰，红烧胡萝卜块色泽暗淡。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "果汁脱色与冷色偏色影响食物新鲜感。"}
    ],
    "review_note": "餐桌玻璃水杯中黄色鲜果汁严重欠饱和脱色发灰，红烧胡萝卜块色泽暗淡(E2-L2)，餐桌白布与背景餐具大面积浸染失真冷青蓝偏色(D-L2)。"
  },

  # Sheet 02 (Tasks 8913, 8915, 8918, 8919, 8921, 8923)
  8913: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "沥青路面与背景行道树轻微浸染冷青蓝偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "双层巴士大红车漆色泽略显暗淡欠饱和。"}
    ],
    "review_note": "双层巴士大红车漆色泽略显暗淡欠饱和(E2-L1)，沥青路面与背景行道树轻微浸染冷青蓝偏色(D-L1)。"
  },
  8915: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "坐下位置原本鲜艳大红色的金属油桶被颠覆性错染为暗黄绿色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "全图浸染失真冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "人偶红色上衣严重欠饱和脱色泛灰。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "油桶恶性错色与上衣脱色严重破坏画面自然度。"}
    ],
    "review_note": "坐下位置原本鲜艳大红色的金属油桶被颠覆性错染为暗黄绿色(C-L3)，红色上衣严重欠饱和脱色(E2-L2)，全图浸染失真冷青偏色(D-L2)。"
  },
  8918: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  8919: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  8921: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  8923: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "不锈钢烤箱门板与台面轻微浸染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "烤箱把手悬挂的印花毛巾上彩色字母圆斑色彩略有暗淡褪色。"}
    ],
    "review_note": "烤箱把手悬挂的印花毛巾上彩色字母圆斑色彩略有暗淡褪色(E2-L1)，不锈钢烤箱门板与台面轻微浸染冷青偏色(D-L1)。"
  },

  # Sheet 03 (Tasks 8924, 8925, 8927, 8928, 8930, 8931)
  8924: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  8925: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  8927: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "滑板四个明亮玫红色滑轮严重欠饱和脱色为暗灰白色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "全图轻微浸染冷青灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "滑板四个玫红轮子与斗牛犬浅黄褐色背毛严重脱色褪淡。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "玫红滑轮完全失色破坏整体视觉真实感。"}
    ],
    "review_note": "滑板四个明亮玫红色滑轮严重欠饱和脱色为暗灰白色(E2-L2, C-L2)，法国斗牛犬浅黄褐色背毛色彩暗淡(E2-L2)，全图轻微浸染冷青灰偏色(D-L1)。"
  },
  8928: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  8930: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "静物油画中青黄苹果底部及葡萄串缝隙处错染失真荧光洋红伪色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "水果缝隙暗部轻微偏冷青紫调。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "青黄苹果与香蕉过度浓艳过饱和。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "洋红伪色与高饱和破坏静物画和谐度。"}
    ],
    "review_note": "静物油画中青黄苹果底部及葡萄串缝隙处错染失真荧光洋红伪色(C-L2)，苹果与香蕉过度浓艳过饱和(E1-L2)，整体视觉自然度受损(F-L2)。"
  },
  8931: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "早期双翼飞机与野外草坪历史影像整体泛暖褐灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "早期双翼飞机与跑道草坪大面积欠饱和脱色呈现暗黄灰色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "老照片上色严重脱色呈现灰白感。"}
    ],
    "review_note": "早期双翼飞机与野外草坪历史黑白影像欠饱和脱色呈现暗黄灰色(E2-L2)，整体泛暖褐灰偏色(D-L2)。"
  },

  # Sheet 04 (Tasks 8932, 8934, 8935, 8937, 8938, 8939)
  8932: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "石砖街道阴影与骑行摩托车手黑色皮衣大面积浸染失真冷青蓝偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "暗部与街道阴影色调过度浓艳过饱和。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "街道阴影泛蓝紫光影响自然真实感。"}
    ],
    "review_note": "石砖街道阴影与骑行摩托车手黑色皮衣大面积浸染失真冷青蓝偏色(D-L2)，暗部色调过度浓艳过饱和(E1-L2)。"
  },
  8934: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "雨水玻璃窗框与户外遮阳伞边缘大面积错染失真深洋红粉紫色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "全图大面积浸染失真偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "窗框伪色浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "大面积粉紫伪色破坏雨天窗景自然度。"}
    ],
    "review_note": "雨水玻璃窗框与户外遮阳伞边缘大面积错染失真深洋红粉紫色伪色(C-L2)，整体画面浸染失真偏色(D-L2)。"
  },
  8935: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  8937: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "银灰色轿车车身漆面与金属停车计时器反光轻微浸染暖红黄偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "车辆漆面反光略偏浓艳。"}
    ],
    "review_note": "银灰色轿车车身漆面与金属停车计时器反光轻微浸染暖红黄偏色且略偏浓艳(D-L1, E1-L1)。"
  },
  8938: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  8939: {
    "action": "revise",
    "defects": [
      {"id": "B", "name": "溢色", "severity": "L1", "description": "漫步棕熊爪部与翠绿草坪交界边缘轻微溢色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "草坪色泽略偏荧光黄绿调。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "草坪绿色略显浓艳。"}
    ],
    "review_note": "漫步棕熊爪部与翠绿草坪交界边缘轻微溢色(B-L1)，草坪色泽略显浓艳偏荧光黄绿调(D-L1, E1-L1)。"
  },

  # Sheet 05 (Tasks 8940, 8943, 8944, 8945, 8947, 8948)
  8940: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "越野摩托车鲜艳天蓝色减震与车架涂装错染为暗淡杂紫灰死色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "竹林地面与摩托车阴影大面积浸染失真暗红偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "越野摩托车蓝色金属漆面欠饱和脱色暗淡。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "车辆涂装恶性变色破坏视觉效果。"}
    ],
    "review_note": "竹林中停放的越野摩托车鲜艳天蓝色减震与车架涂装错染为暗淡杂紫灰死色(C-L2, E2-L2)，竹林地面大面积浸染失真偏色(D-L2, F-L2)。"
  },
  8943: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "牧场草地与马匹毛发浸染失真红橙暖偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "母马与红色小马驹毛发及草地过度浓艳失真，呈现极高饱和度火红与荧光感。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "火红火烤般的超高饱和度严重损害真实自然感。"}
    ],
    "review_note": "牧场母马与红色小马驹毛发及草地过度浓艳失真，泛极高饱和度红橙色与荧光调(E1-L2, D-L2)。"
  },
  8944: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "喷泉旁亮黄色金属立柱标牌严重欠饱和褪色为灰白淡色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "全图轻微泛冷青灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "黄色金属立柱标牌严重欠饱和褪色灰白，红色标识暗淡。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "标志性立柱严重脱色破坏视觉观感。"}
    ],
    "review_note": "喷泉旁亮黄色金属立柱标牌严重欠饱和褪色为灰白淡色(E2-L2, C-L2)，立柱红色标识暗淡，全图轻微泛冷偏色(D-L1)。"
  },
  8945: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "斑马脚下翠绿草坪严重欠饱和脱色为枯黄干枯草色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "全图大面积浸染失真冷青紫偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "草坪严重脱色为干瘪土黄淡色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "草地脱色变枯草影响生机观感。"}
    ],
    "review_note": "两只斑马脚下翠绿草坪严重欠饱和脱色为枯黄干枯草色(E2-L2, C-L2)，全图大面积浸染冷青紫偏色(D-L2)。"
  },
  8947: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "电视机旁棕色实木抽屉表面错染洋红伪色斑块。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "黑猫趴伏柜面与阴影轻微浸染冷偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "实木抽屉伪色略偏浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "木柜局部杂色伪色违和。"}
    ],
    "review_note": "电视机旁棕色实木抽屉表面错染洋红伪色斑块(C-L2)，黑猫趴伏柜面浸染冷偏色(D-L1)。"
  },
  8948: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "客厅天花板吊顶与背景乳胶漆墙面大面积错染失真深洋红紫红色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "室内天花板与墙壁大面积浸染失真暗红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "墙顶紫红色偏色浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "严重破坏室内温馨暖光的视觉真实度。"}
    ],
    "review_note": "客厅天花板吊顶与背景乳胶漆墙面大面积错染失真深洋红紫红色伪色(C-L2, D-L2)，严重破坏室内温馨暖光自然度(F-L2)。"
  },

  # Sheet 06 (Tasks 8950, 8952, 8954, 8956, 8957, 8959)
  8950: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "海边夕阳落日暖光微偏冷青蓝调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "风车彩色骨架与晚霞海面色泽略有暗淡。"}
    ],
    "review_note": "海边夕阳落日暖光微偏冷青蓝调(D-L1)，风车彩色骨架与晚霞海面色泽略有暗淡(E2-L1)。"
  },
  8952: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  8954: {
    "action": "revise",
    "defects": [
      {"id": "B", "name": "溢色", "severity": "L2", "description": "飞燕草花瓣边缘严重溢色且荧光失真。"},
      {"id": "C", "name": "错色", "severity": "L2", "description": "玻璃花瓶后方草地背景错染极其刺眼的高饱和荧光青绿色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "花瓶与花束全景浸染失真冷青蓝偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L3", "description": "草地与花朵泛高光荧光过饱和。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "刺眼荧光绿严重破坏花艺观感。"}
    ],
    "review_note": "玻璃花瓶后方草地背景错染极其刺眼的高饱和荧光青绿色(C-L2, E1-L3)，飞燕草花瓣边缘严重溢色且荧光失真(B-L2, F-L2)。"
  },
  8956: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "十字路口沥青路面与行驶摩托车轻微浸染冷青蓝偏色。"}
    ],
    "review_note": "十字路口沥青路面与行驶摩托车轻微浸染冷青蓝偏色(D-L1)。"
  },
  8957: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "木棚铁皮屋顶与杂乱木桩大面积浸染失真暖红褐偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "木材与铁皮屋顶色调过度浓艳失真。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "火红暖褐偏色使平民棚屋失真严重。"}
    ],
    "review_note": "木棚铁皮屋顶与杂乱木桩大面积浸染失真暖红褐偏色(D-L2)，色调过度浓艳失真(E1-L2, F-L2)。"
  },
  8959: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "全图轻微浸染冷青灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "古堡钟楼历史石雕外墙大面积欠饱和严重脱色为冰冷浅灰白色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "古朴石墙灰白脱色影响历史厚重感。"}
    ],
    "review_note": "古堡钟楼历史石雕外墙大面积欠饱和严重脱色为冰冷浅灰白色(E2-L2)，全图轻微浸染冷青灰偏色(D-L1)。"
  },

  # Sheet 07 (Tasks 8962, 8963, 8964, 8966, 8968, 8969)
  8962: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "长途客运大巴鲜艳亮橘黄色车头漆面严重欠饱和颠覆性脱色为苍白灰白色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "车身全景轻微泛冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "整车大红亮橘黄车漆大面积脱色为灰白色，车内红色挂饰褪色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "亮橘大巴变惨白灰严重脱离真实车貌。"}
    ],
    "review_note": "长途客运大巴鲜艳亮橘黄色车头漆面严重欠饱和颠覆性脱色为苍白灰白色(E2-L3, C-L3)，车内红色挂饰褪色，全图轻微泛冷偏色(D-L1)。"
  },
  8963: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "乱石斜坡上枯黄苔藓与浅灰岩石错染为大面积刺眼荧光青绿色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "全图浸染失真冷青偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "乱石坡面假青苔过度浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "荧光青绿石堆极不自然。"}
    ],
    "review_note": "乱石斜坡上枯黄苔藓与浅灰岩石错染为大面积刺眼荧光青绿色(C-L2, E1-L2)，全图浸染失真冷青偏色(D-L2)。"
  },
  8964: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  8966: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  8968: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "室内男女面部皮肤与手臂大面积浸染失真红橙暖偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "男女皮肤与背景饱和度过高呈现浓艳火烤感。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "火红肤色影响人物肖像自然度。"}
    ],
    "review_note": "室内男女面部皮肤与手臂大面积浸染失真红橙暖偏色，饱和度过高呈现浓艳火烤感(D-L2, E1-L2)。"
  },
  8969: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "全图浸染失真冷青灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "夜间路边金属消防栓与沥青路面严重欠饱和脱色为冰冷水泥暗灰色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "路边暖灯反光完全褪色为冰冷死灰色。"}
    ],
    "review_note": "夜间路边金属消防栓与沥青路面严重欠饱和脱色为冰冷水泥暗灰色(E2-L2)，浸染失真冷青灰偏色(D-L2)。"
  },

  # Sheet 08 (Tasks 8972, 8973, 8974, 8976, 8981, 8982)
  8972: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "浅绿餐巾与咖啡杯轻微浸染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "餐盘中烘烤肉桂卷金黄油亮色泽暗淡欠饱和。"}
    ],
    "review_note": "餐盘中烘烤肉桂卷金黄油亮色泽暗淡欠饱和(E2-L1)，浅绿餐巾与咖啡杯轻微浸染冷青偏色(D-L1)。"
  },
  8973: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "露天观景台后方蔚蓝晴空与碧蓝海面严重欠饱和颠覆性脱色为枯黄灰白死色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "全图浸染失真偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "海天一色完全脱色抹杀。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "碧蓝大海变干枯死色严重破坏画面自然感。"}
    ],
    "review_note": "露天观景台后方蔚蓝晴空与碧蓝海面严重欠饱和颠覆性脱色为枯黄灰白死色(E2-L3, C-L3)，全图浸染失真偏色(D-L2, F-L2)。"
  },
  8974: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "书桌电脑旁乳胶漆墙面与阴影大面积浸染失真暗洋红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "暗部与墙角杂色过度浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "大面积洋红阴影违和刺眼。"}
    ],
    "review_note": "书桌电脑旁乳胶漆墙面与阴影大面积浸染失真暗洋红偏色(D-L2)，暗部色调过度浓艳(E1-L2)。"
  },
  8976: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  8981: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "生日纸杯蛋糕表面明黄奶油点缀被颠覆性错染为深蓝色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "金发女孩手臂与背景墙面浸染冷青偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "纸杯蛋糕蓝色奶油过度浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "鲜黄奶油变深蓝严重失真。"}
    ],
    "review_note": "生日纸杯蛋糕表面明黄奶油点缀被颠覆性错染为深蓝色(C-L2)，金发女孩手臂与背景墙面浸染冷青偏色(D-L1, F-L2)。"
  },
  8982: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 09 (Tasks 8983, 8986, 8987, 8989, 8990, 8991)
  8983: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  8986: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  8987: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  8989: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "左侧站立男士浅粉红色长袖衬衫被严重加深错染为深大红色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "全图轻微浸染冷青偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "衬衫深大红色过度浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "男士衬衫颜色剧烈加深失真。"}
    ],
    "review_note": "左侧站立男士浅粉红色长袖衬衫被严重加深错染为深大红色(C-L2, E1-L2)，全图轻微浸染冷青偏色(D-L1)。"
  },
  8990: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "老照片全景整体泛暖褐灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "家庭老照片人物西装礼服与背景大面积欠饱和脱色泛枯黄暗褐色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "老照片上色严重脱色呈现泛黄灰阶。"}
    ],
    "review_note": "家庭老照片人物西装礼服与背景大面积欠饱和脱色泛枯黄暗褐色(E2-L2)，整体泛暖褐灰偏色(D-L2)。"
  },
  8991: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "红白格快餐纸与托盘边缘轻微浸染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "油炸薯条金黄酥脆色泽略显暗淡欠饱和。"}
    ],
    "review_note": "油炸薯条金黄酥脆色泽略显暗淡欠饱和(E2-L1)，红白格快餐纸与托盘边缘轻微浸染冷青偏色(D-L1)。"
  },

  # Sheet 10 (Tasks 8992, 8994, 8996, 8997, 9000, 9001)
  8992: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  8994: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  8996: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  8997: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "黄牛身躯与泥土路面轻微浸染冷青偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "乡间泥泞路边树木草丛色泽略偏浓艳深绿。"}
    ],
    "review_note": "乡间泥泞路边树木草丛色泽略偏浓艳深绿(E1-L1)，黄牛身躯与泥土路面轻微浸染冷青偏色(D-L1)。"
  },
  9000: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "草坪后方天空边缘与黑色重型机车金属车身轻微浸染冷青偏色。"}
    ],
    "review_note": "草坪后方天空边缘与黑色重型机车金属车身轻微浸染冷青偏色(D-L1)。"
  },
  9001: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "滑板上站立者脚穿原本极其鲜艳的大红橙色帆布鞋颠覆性严重脱色错染为惨白灰白色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "滑板木板面与鞋身浸染冷青灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "两只大红帆布鞋完全褪色为苍白灰白色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "鲜红运动鞋严重褪色惨白严重违和。"}
    ],
    "review_note": "滑板上站立者脚穿原本极其鲜艳的大红橙色帆布鞋颠覆性严重脱色错染为惨白灰白色(C-L3, E2-L3)，滑板木板面浸染冷青灰偏色(D-L2, F-L2)。"
  },

  # Sheet 11 (Tasks 9003, 9004, 9005, 9006, 9008, 9013)
  9003: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "白瓷碗盛装的鲜黄奶油南瓜汤颠覆性欠饱和脱色为惨白灰黄色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "全图微偏冷青蓝调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "金黄南瓜汤严重欠饱和脱色发白，卷饼生菜暗淡。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "浓汤脱色惨白严重影响食欲。"}
    ],
    "review_note": "白瓷碗盛装的鲜黄奶油南瓜汤颠覆性欠饱和脱色为惨白灰黄色(C-L3, E2-L2)，卷饼内嫩绿生菜色泽暗淡，全图微偏冷青蓝调(D-L1)。"
  },
  9004: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "披萨烘焙炉前面点师傅身穿的深灰黑色工作短袖被颠覆性错染为鲜亮深蓝色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "全图轻微浸染冷偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "工作短袖被误染为高饱和亮蓝色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "工作服恶意错色破坏烘焙场景真实感。"}
    ],
    "review_note": "披萨烘焙炉前面点师傅身穿的深灰黑色工作短袖被颠覆性错染为鲜亮深蓝色(C-L3, E1-L2)，全图轻微浸染冷偏色(D-L1, F-L2)。"
  },
  9005: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "楼梯阴影与毛绒玩具浸染失真暗红偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "石阶上毛绒泰迪熊与楼梯阴影大面积欠饱和脱色呈现暗紫褐色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "玩具小熊暗角失真泛紫。"}
    ],
    "review_note": "石阶上毛绒泰迪熊与楼梯阴影大面积欠饱和脱色呈现暗紫褐色(E2-L2)，浸染失真暗红偏色(D-L2)。"
  },
  9006: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "夜间白色加长礼宾车车身漆面与地砖反光浸染失真冷青紫杂色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "夜景车身与地面反射光过度浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "白车身泛紫杂斑影响整车纯净感。"}
    ],
    "review_note": "夜间超长白色加长礼宾车车身漆面与地砖反光浸染失真冷青紫杂色，色调过度浓艳(D-L1, E1-L2)。"
  },
  9008: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9013: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "室内吊顶天花板与男子所穿棕色T恤大面积浸染失真暗洋红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "T恤背部与天花板色调略偏浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "室内暗部泛紫破坏真实观感。"}
    ],
    "review_note": "室内吊顶天花板与男子所穿棕色T恤大面积浸染失真暗洋红偏色(D-L2)，整体自然度受损(F-L1)。"
  },

  # Sheet 12 (Tasks 9014, 9015, 9019, 9023, 9024, 9026)
  9014: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9015: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "人行道旁绿色木栅栏与灌木树篱大面积欠饱和脱色为暗淡灰绿色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "全图轻微浸染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街景绿化灌木丛严重欠饱和褪色发白。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "树篱失色使街道绿化感降低。"}
    ],
    "review_note": "人行道旁绿色木栅栏与灌木树篱大面积欠饱和脱色为暗淡灰绿色(E2-L2, C-L2)，全图轻微浸染冷青偏色(D-L1)。"
  },
  9019: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "石砟轨道轻微泛冷青偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "沙盘模型中微型铁路轨道旁人工草坪与树木色调略偏浓艳过饱和。"}
    ],
    "review_note": "沙盘模型中微型铁路轨道旁人工草坪与树木色调略偏浓艳过饱和(E1-L1)，石砟轨道轻微泛冷青偏色(D-L1)。"
  },
  9023: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "多发轰炸机空中编队整体泛暖褐灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "多发轰炸机空中编队历史黑白照片欠饱和脱色呈现暗土黄色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "军机老照片上色呈现淡黄脱色状态。"}
    ],
    "review_note": "多发轰炸机空中编队历史黑白照片欠饱和脱色呈现暗土黄色(E2-L2)，整体泛暖褐灰偏色(D-L2)。"
  },
  9024: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9026: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 13 (Tasks 9028, 9030, 9032, 9033, 9034, 9036)
  9028: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9030: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "沙滩主遮阳伞原本鲜艳大红橙色伞面被颠覆性错染为枯暗土黄杂色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "沙滩与沙滩椅轻微浸染冷偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "大红遮阳伞严重褪色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "鲜亮遮阳伞错染枯黄色严重破坏度假感。"}
    ],
    "review_note": "沙滩主遮阳伞原本鲜艳大红橙色伞面被颠覆性错染为枯暗土黄杂色(C-L3, E2-L2)，全图轻微浸染冷偏色(D-L1, F-L2)。"
  },
  9032: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "沙滩地面与男子肤色轻微浸染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "风筝冲浪翼板天蓝色涂装色泽略显暗淡欠饱和。"}
    ],
    "review_note": "风筝冲浪翼板天蓝色涂装色泽略显暗淡欠饱和(E2-L1)，沙滩地面与男子肤色轻微浸染冷青偏色(D-L1)。"
  },
  9033: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "溪畔岩石与身后树林轻微浸染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "金毛大狗金黄毛发色泽略显暗淡欠饱和。"}
    ],
    "review_note": "金毛大狗金黄毛发色泽略显暗淡欠饱和(E2-L1)，溪畔岩石与身后树林轻微浸染冷青偏色(D-L1)。"
  },
  9034: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "热狗包装纸与面包周围大面积浸染失真暗洋红紫伪色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "包装纸与手持区域大面积浸染失真暗红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "洋红杂色浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "破坏整体食品视觉真实度。"}
    ],
    "review_note": "热狗包装纸与面包周围大面积浸染失真暗洋红紫伪色(C-L2, D-L2)，破坏整体食品视觉真实度(F-L2)。"
  },
  9036: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 14 (Tasks 9037, 9038, 9040, 9041, 9042, 9043)
  9037: {
    "action": "meltdown_a",
    "defects": [
      {"id": "A", "name": "缺色", "severity": "", "description": "历史早期人物网球拍肖像完全未成功上色，呈现全域纯灰度未着色状态。"}
    ],
    "reviewed_score": 1.0,
    "needs_rescoring": False,
    "review_note": "【熔断项A·全域缺色】历史早期人物网球拍肖像完全未成功上色，呈现全域纯灰度未着色状态。"
  },
  9038: {
    "action": "revise",
    "defects": [
      {"id": "B", "name": "溢色", "severity": "L1", "description": "消防栓金属边缘色泽溢出。"},
      {"id": "C", "name": "错色", "severity": "L2", "description": "铸铁消防栓背景停放的翡翠浅绿色轿车错染为深暗蓝绿色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "全图浸染失真冷青偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "背景汽车暗蓝色过度浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "汽车恶性错色破坏街景协调感。"}
    ],
    "review_note": "铸铁消防栓背景停放的翡翠浅绿色轿车错染为深暗蓝绿色(C-L2)，消防栓金属边缘色泽溢出(B-L1)，全图浸染失真冷青偏色(D-L2, F-L2)。"
  },
  9040: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "厨房木质橱柜轻微浸染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "老妇人身穿浅黄色短袖与男士浅绿色短袖衬衫色泽略显暗淡欠饱和。"}
    ],
    "review_note": "老妇人身穿浅黄色短袖与男士浅绿色短袖衬衫色泽略显暗淡欠饱和(E2-L1)，厨房木质橱柜轻微浸染冷青偏色(D-L1)。"
  },
  9041: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9042: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9043: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "全图轻微泛冷青偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "斑马线前停靠摩托车车身紫色涂装与后座红色防风服色调过度浓艳过饱和。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "暗部过度加深浓艳略显失真。"}
    ],
    "review_note": "斑马线前停靠摩托车车身紫色涂装与后座红色防风服色调过度浓艳过饱和(E1-L2)，全图轻微泛冷青偏色(D-L1)。"
  },

  # Sheet 15 (Tasks 9044, 9045, 9046, 9047, 9048, 9049)
  9044: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "盛放蛋糕的白瓷盘与桌面大面积浸染失真暖黄橙偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "盘面反光与糖霜色调过度浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "白瓷盘泛黄影响洁净真实感。"}
    ],
    "review_note": "盛放蛋糕的白瓷盘与桌面大面积浸染失真暖黄橙偏色，盘面反光色调过度浓艳(D-L1, E1-L2)。"
  },
  9045: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9046: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "办公桌桌面与地面瓷砖轻微浸染冷青蓝偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "木门木纹色泽略有暗淡。"}
    ],
    "review_note": "办公桌桌面与地面瓷砖轻微浸染冷青蓝偏色(D-L1)，木门木纹色泽略有暗淡(E2-L1)。"
  },
  9047: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "全图泛冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "海边沙滩冲浪者防寒服与大黑狗暗部大面积欠饱和脱色发灰。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "人物与小狗暗部褪色平淡。"}
    ],
    "review_note": "海边沙滩冲浪者防寒服与大黑狗暗部大面积欠饱和脱色发灰(E2-L2)，全图泛冷灰偏色(D-L1)。"
  },
  9048: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9049: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "全图轻微浸染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "树林长颈鹿体表金黄褐色斑纹大面积欠饱和褪色为干瘪土灰淡色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "长颈鹿斑纹暗淡失去光泽。"}
    ],
    "review_note": "树林长颈鹿体表金黄褐色斑纹大面积欠饱和褪色为干瘪土灰淡色(E2-L2)，全图轻微浸染冷青偏色(D-L1)。"
  },

  # Sheet 16 (Tasks 9052, 9053, 9054, 9055, 9056, 9059)
  9052: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9053: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "桥梁钢结构与河流水面轻微浸染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "桥头古典红砖城堡塔楼色泽略显暗淡欠饱和。"}
    ],
    "review_note": "桥头古典红砖城堡塔楼色泽略显暗淡欠饱和(E2-L1)，桥梁钢结构与河流水面轻微浸染冷青偏色(D-L1)。"
  },
  9054: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9055: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "棒球场防撞击外墙原本鲜艳翠绿色被颠覆性错染为枯暗土黄褐色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "两名球员球服与头盔大面积浸染失真冷青紫偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "外墙由绿变枯黄，色泽严重欠饱和。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "绿色外墙大面积错色严重失真。"}
    ],
    "review_note": "棒球场防撞击外墙原本鲜艳翠绿色被颠覆性错染为枯暗土黄褐色(C-L3, E2-L2)，两名球员球服与头盔大面积浸染失真冷青紫偏色(D-L2, F-L2)。"
  },
  9056: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "商业街木质商铺粉红暖色门脸与遮阳棚大面积欠饱和褪色为暗淡土灰色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "全图轻微浸染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "店铺暖粉色门面严重欠饱和脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "复古店铺失色显得萧条。"}
    ],
    "review_note": "商业街木质商铺粉红暖色门脸与遮阳棚大面积欠饱和褪色为暗淡土灰色(E2-L2, C-L2)，全图轻微浸染冷青偏色(D-L1)。"
  },
  9059: {
    "action": "revise",
    "defects": [
      {"id": "B", "name": "溢色", "severity": "L2", "description": "执勤人员荧光背心严重溢色侵染周围车体。"},
      {"id": "C", "name": "错色", "severity": "L3", "description": "夜间路口红底白字STOP停车标牌颠覆性严重脱色错染为灰白死色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "全图失真偏色严重。"},
      {"id": "E1", "name": "过饱和", "severity": "L3", "description": "黄色荧光背心错染为刺眼高饱和荧光蓝紫色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "红色标牌脱色与荧光伪色严重损害图像真实性。"}
    ],
    "review_note": "夜间路口红底白字STOP停车标牌颠覆性严重脱色错染为灰白死色(C-L3)，执勤人员荧光背心错染为刺眼高饱和荧光蓝紫色且严重溢色(B-L2, E1-L3)，全图失真偏色严重(D-L2, F-L3)。"
  },

  # Sheet 17 (Tasks 9061, 9062, 9063, 9064, 9067, 9068)
  9061: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "港湾上方原本璀璨金黄温暖的落日晚霞天空被颠覆性脱色错染为冰冷青灰死色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "港湾水面与游船大面积浸染失真冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "金黄晚霞天空大面积欠饱和严重脱色抹杀。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "晚霞美景完全失色严重失真。"}
    ],
    "review_note": "港湾上方原本璀璨金黄温暖的落日晚霞天空被颠覆性脱色错染为冰冷青灰死色(C-L3, E2-L3)，港湾水面与游船大面积浸染失真冷青偏色(D-L2, F-L2)。"
  },
  9062: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9063: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9064: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "白雪坡面轻微泛冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "雪坡滑雪儿童身穿深色防寒服边缘色泽略显暗淡。"}
    ],
    "review_note": "雪坡滑雪儿童身穿深色防寒服边缘色泽略显暗淡(E2-L1)，白雪坡面轻微泛冷青偏色(D-L1)。"
  },
  9067: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9068: {
    "action": "meltdown_a",
    "defects": [
      {"id": "A", "name": "缺色", "severity": "", "description": "雨中撑伞路人与沿街商铺全景完全未成功着色，呈现全域纯灰阶未着色状态。"}
    ],
    "reviewed_score": 1.0,
    "needs_rescoring": False,
    "review_note": "【熔断项A·全域缺色】雨中撑伞路人与沿街商铺全景完全未成功着色，呈现全域纯灰阶未着色状态。"
  },

  # Sheet 18 (Tasks 9069, 9070, 9071, 9072, 9073, 9074)
  9069: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "瓷盘白瓷表面轻微浸染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "货架陈列传统青花瓷盘表面青蓝花纹色泽略显暗淡欠饱和。"}
    ],
    "review_note": "货架陈列传统青花瓷盘表面青蓝花纹色泽略显暗淡欠饱和(E2-L1)，瓷盘白瓷表面轻微浸染冷青偏色(D-L1)。"
  },
  9070: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9071: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "餐桌前小男孩面部皮肤大面积浸染失真红橙暖偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "男孩面部与草莓甜品色调过度浓艳过饱和。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "火红肤色略显违和。"}
    ],
    "review_note": "餐桌前小男孩面部皮肤大面积浸染失真红橙暖偏色，色调过度浓艳过饱和(D-L2, E1-L2)。"
  },
  9072: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "沥青路面泛微弱冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "夜间停车场高杆路灯金黄光芒照射下的沥青地面与车体色泽略显暗淡欠饱和。"}
    ],
    "review_note": "夜间停车场高杆路灯金黄光芒照射下的沥青地面与车体色泽略显暗淡欠饱和(E2-L1)，泛微弱冷灰偏色(D-L1)。"
  },
  9073: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9074: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "摆放白色游戏机主机的实木桌面与背景墙壁大面积错染失真深洋红紫红色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "桌面与背景墙壁大面积浸染失真暗红紫偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "背景墙洋红伪色浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "严重破坏室内正常照明的真实感。"}
    ],
    "review_note": "摆放白色游戏机主机的实木桌面与背景墙壁大面积错染失真深洋红紫红色伪色(C-L2, D-L2)，严重破坏自然光照度(F-L2)。"
  },

  # Sheet 19 (Tasks 9075, 9076, 9077, 9078, 9079, 9080)
  9075: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "女士金黄棕色长发与塑料杯冰咖啡轻微浸染暖红黄偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "头发与咖啡色调略偏浓艳。"}
    ],
    "review_note": "女士金黄棕色长发与塑料杯冰咖啡色调略偏浓艳暖红黄偏色(D-L1, E1-L1)。"
  },
  9076: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9077: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9078: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "墨西哥餐厅外墙原本鲜亮浓郁的大红外立面大面积欠饱和严重脱色为暗淡土灰粉色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "全图轻微浸染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "大红餐厅外立面严重欠饱和脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "外墙褪色发白影响商业辨识度。"}
    ],
    "review_note": "墨西哥餐厅外墙原本鲜亮浓郁的大红外立面大面积欠饱和严重脱色为暗淡土灰粉色(E2-L2, C-L2)，全图轻微浸染冷青偏色(D-L1)。"
  },
  9079: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "酒店客房暗红床罩与床头壁灯轻微浸染冷青蓝偏色。"}
    ],
    "review_note": "酒店客房暗红床罩与床头壁灯轻微浸染冷青蓝偏色(D-L1)。"
  },
  9080: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "披萨边缘泛微弱偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "烘烤披萨表面芝士与脆皮边缘色调略显浓艳过饱和。"}
    ],
    "review_note": "烘烤披萨表面芝士与脆皮边缘色调略显浓艳过饱和(E1-L1)，泛微弱偏色(D-L1)。"
  },

  # Sheet 20 (Tasks 9082, 9083, 9084, 9085, 9086, 9088)
  9082: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9083: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9084: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "男子手臂与室内白墙轻微浸染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "金毛犬背部金黄毛发色泽略显暗淡欠饱和。"}
    ],
    "review_note": "金毛犬背部金黄毛发色泽略显暗淡欠饱和(E2-L1)，男子手臂与室内白墙轻微浸染冷青偏色(D-L1)。"
  },
  9085: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "棒球击球手身穿深蓝短袖T恤错染为红褐暗色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "全图浸染失真偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "草坪与球员服饰大面积过度浓艳过饱和。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "浓艳火红草地与球员衣色违和。"}
    ],
    "review_note": "棒球击球手身穿深蓝短袖T恤错染为红褐暗色(C-L2)，草坪与球员服饰大面积过度浓艳过饱和(E1-L2)，全图浸染失真偏色(D-L2)。"
  },
  9086: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "黑狗飞身跃起咬住的原本鲜艳亮粉红色飞盘被颠覆性错染为浅天蓝色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "天空与黑狗毛发轻微泛冷偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "飞盘边缘蓝色略显突兀。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "亮粉飞盘变浅蓝常识错色严重。"}
    ],
    "review_note": "黑狗飞身跃起咬住的原本鲜艳亮粉红色飞盘被颠覆性错染为浅天蓝色(C-L3)，天空与黑狗毛发轻微泛冷偏色(D-L1, F-L2)。"
  },
  9088: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  }
}

def apply_batch_45():
    # 1. 保存 grounding_remaining_batch_45.json
    out_grounding = 'LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_45.json'
    with open(out_grounding, 'w', encoding='utf-8') as f:
        json.dump(BATCH_45_REVIEWS, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(BATCH_45_REVIEWS)} reviews to {out_grounding}")

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

    for task_id, review in BATCH_45_REVIEWS.items():
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

    print("Batch 45 applied successfully!")
    print(f"Total: {len(BATCH_45_REVIEWS)}, Passes: {pass_count} ({pass_count/len(BATCH_45_REVIEWS)*100:.2f}%), Revised: {revised_count} ({revised_count/len(BATCH_45_REVIEWS)*100:.2f}%), Meltdown A: {meltdown_count}")

if __name__ == '__main__':
    apply_batch_45()
