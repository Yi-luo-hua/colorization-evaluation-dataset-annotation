import json
import os
import copy

BATCH_47_REVIEWS = {
  # Sheet 01 (Tasks 9277, 9278, 9283, 9287, 9288, 9289)
  9277: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "室内折叠轮椅与婴儿推车扶手把手被错染为暗淡灰黑色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "推车靠垫与周围地面微泛冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "推车把手粉红色漆面与靠垫严重欠饱和脱色发灰。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "把手严重脱色影响童车细节质感。"}
    ],
    "review_note": "室内折叠轮椅与推车粉红把手与靠垫脱色发灰(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9278: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "手持手柄男孩粗条纹针织衫与面部大面积浸染失真火红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "男孩面部与衣服红色调浓艳过度溢出。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "人物肤色与衣服严重偏红失真。"}
    ],
    "review_note": "手持手柄男孩粗条纹针织衫与面部浸染失真火红偏色(D-L2, E1-L2, F-L1)。"
  },
  9283: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9287: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "林间泥土小道与草地边缘错染失真暗红偏色斑块。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "林地小径大面积泛暗红褐色调。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "小径泥土红色调偏浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "林间小道错染红斑违背自然泥土常理。"}
    ],
    "review_note": "林间泥土小道错染失真暗红偏色斑块(C-L2, D-L2, E1-L1, F-L2)。"
  },
  9288: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "飞镖运动员白色运动短袖与背景墙壁大面积浸染冰冷青蓝偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "背景墙壁青蓝杂色略显浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "冷青色调大面积浸染使室内氛围冰冷失真。"}
    ],
    "review_note": "飞镖运动员白色运动短袖与背景墙壁大面积浸染冰冷青蓝偏色(D-L2, E1-L1, F-L2)。"
  },
  9289: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "餐桌瓷盘边缘与鲜切西瓜大面积浸染失真冷青蓝偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "餐盘边缘青蓝杂色浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "食物表面浸染青蓝杂斑严重违背食用常理。"}
    ],
    "review_note": "餐桌瓷盘边缘与鲜切西瓜大面积浸染失真冷青蓝偏色(D-L2, E1-L2, F-L2)。"
  },

  # Sheet 02 (Tasks 9291, 9293, 9296, 9297, 9298, 9301)
  9291: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "餐厅厨师鲜红色围裙色泽严重脱色发暗，错染为暗褐红色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "厨师白色工作服与餐桌微泛冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "鲜红围裙欠饱和褪色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "围裙脱色降低了厨房生动感。"}
    ],
    "review_note": "餐厅厨师鲜红色围裙色泽欠饱和褪色发暗(C-L2, D-L1, E2-L1, F-L1)。"
  },
  9293: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "草地与棕熊背毛微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "大棕熊棕黄皮毛与周围绿草地欠饱和脱色发暗。"}
    ],
    "review_note": "大棕熊皮毛与草地欠饱和脱色发暗，微染冷青灰色调(D-L1, E2-L1)。"
  },
  9296: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "整片海面与浪花大面积泛暗灰冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "蔚蓝大海海水毁灭性脱色褪变为一片暗淡水泥灰。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "大海严重脱色失去水体通透质感。"}
    ],
    "review_note": "蔚蓝大海海水毁灭性脱色褪变为一片暗淡水泥灰(D-L2, E2-L3, F-L2)。"
  },
  9297: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9298: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "丛林草地与远景树木微泛灰冷偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "青年连帽风衣与草坪大面积欠饱和脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "户外草木脱色显干瘪枯萎。"}
    ],
    "review_note": "丛林草地与青年连帽风衣大面积欠饱和脱色发暗(D-L1, E2-L2, F-L1)。"
  },
  9301: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "女士原本明亮浅黄毛衣被颠覆性错染为刺眼荧光翠绿色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "女士毛衣与怀抱小狗毛发边缘大面积泛翠绿偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的翠绿伪色过于浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "衣物错染翠绿完全破坏画面真实质感。"}
    ],
    "review_note": "女士原本明亮浅黄毛衣被颠覆性错染为刺眼荧光翠绿色伪色(C-L3, D-L2, E1-L2, F-L2)。"
  },

  # Sheet 03 (Tasks 9302, 9303, 9304, 9310, 9311, 9315)
  9302: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "白发老人衬衫暗部与背景墙面微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "老人面部肤色与衬衫背光处略显暗淡欠饱和。"}
    ],
    "review_note": "白发老人衬衫暗部与背景墙面色彩略显暗淡欠饱和，微染冷青灰色调(D-L1, E2-L1)。"
  },
  9303: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "越野滑雪运动员原本翠绿色滑雪服严重脱色错染为深灰黑色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "雪地暗部与选手滑雪手套微泛冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "翠绿滑雪服严重欠饱和褪色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "滑雪服严重褪色降低了运动辨识度。"}
    ],
    "review_note": "越野滑雪运动员原本翠绿色滑雪服严重脱色错染为深灰黑(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9304: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "餐厅百叶窗窗框与墙面大面积错染刺眼深洋红与蓝紫色伪色斑块。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "窗台与墙面阴影大面积泛洋红蓝紫偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的深洋红杂斑浓艳突兀。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "窗框紫红伪色斑块严重破坏室内整洁质感。"}
    ],
    "review_note": "餐厅百叶窗窗框与墙面大面积错染刺眼深洋红与蓝紫色伪色斑块(C-L2, D-L2, E1-L2, F-L2)。"
  },
  9310: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "新鲜香蕉表皮原本青绿未成熟部位被错染为深黄褐色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "香蕉表皮与果蒂微泛暗红黄偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "深黄褐色泽偏深沉浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "青绿蕉柄错色破坏水果新鲜度。"}
    ],
    "review_note": "新鲜香蕉表皮原本青绿未成熟部位被错染为深黄褐色(C-L2, D-L1, E1-L1, F-L1)。"
  },
  9311: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "柏油马路地面原本明黄色的交通标线大面积脱色错染为暗灰白色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "路面柏油微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "黄色斑马线与路标严重欠饱和脱色发白。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "交通标线脱色破坏道路标识真实感。"}
    ],
    "review_note": "柏油马路地面原本黄色交通标线大面积欠饱和脱色发白(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9315: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "豪华卫生间白色瓷砖与陶瓷台面浸染失真红褐偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "瓷砖台面红褐色调过于深浓溢出。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "卫生间白色陶瓷大面积泛红偏色破坏清洁感。"}
    ],
    "review_note": "豪华卫生间白色瓷砖与陶瓷台面浸染失真红褐偏色(D-L2, E1-L2, F-L1)。"
  },

  # Sheet 04 (Tasks 9316, 9318, 9321, 9322, 9323, 9324)
  9316: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9318: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "沙发靠垫与毛绒小熊被错染为荧光青绿与蓝紫色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "沙发区域泛青蓝与深紫冷调偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的青绿与紫蓝杂色刺眼浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "毛绒玩具被伪色严重污染。"}
    ],
    "review_note": "沙发靠垫与毛绒小熊被错染荧光青绿与蓝紫色伪色(C-L2, D-L2, E1-L2, F-L2)。"
  },
  9321: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9322: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "盘中焗烤土豆泥配菜青豆被错染为浑浊青蓝色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "白色餐盘表面微染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "蔬菜青豆与土豆表面欠饱和略显暗淡。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "青豆偏蓝破坏食物新鲜度。"}
    ],
    "review_note": "盘中焗烤土豆泥配菜青豆被错染为浑浊青蓝色(C-L2, D-L1, E2-L1, F-L1)。"
  },
  9323: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "公园长椅与林间小道微染冷青偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "白桦林树木叶片与草坪色泽略显偏浓艳。"}
    ],
    "review_note": "公园白桦林树木叶片与草坪色泽略显偏浓艳，长椅微染冷青偏色(D-L1, E1-L1)。"
  },
  9324: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 05 (Tasks 9325, 9326, 9328, 9329, 9330, 9331)
  9325: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "滑板少年砖红色连帽卫衣严重脱色错染为暗淡灰黑色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "少年面部与地面微染冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "砖红卫衣大面积欠饱和严重脱色变暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "卫衣脱色降低服饰鲜明度。"}
    ],
    "review_note": "滑板少年砖红色连帽卫衣大面积欠饱和严重脱色变暗(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9326: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "前景欢呼男士大红色短袖严重脱色错染为灰褐色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "男士手臂与背光处微泛灰冷偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "大红短袖欠饱和严重脱色褪色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "红短袖褪色影响庆祝氛围生动感。"}
    ],
    "review_note": "前景欢呼男士大红色短袖欠饱和严重脱色变暗(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9328: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9329: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "咨询台右侧粉红色宣传海报大面积欠饱和脱色发暗，错染为灰白色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "柜台桌面与隔板微泛冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "海报粉红色彩欠饱和褪色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "海报脱色影响宣传辨识度。"}
    ],
    "review_note": "咨询台右侧粉红色宣传海报大面积欠饱和脱色发暗(C-L2, D-L1, E2-L1, F-L1)。"
  },
  9330: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "非洲草原长颈鹿身躯与草地大面积浸染失真火红暖橙偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "长颈鹿黄色斑纹与草原红色调过于浓艳溢出。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "全图火红偏色严重破坏草原真实光照感。"}
    ],
    "review_note": "非洲草原长颈鹿身躯与草地大面积浸染失真火红暖橙偏色(D-L2, E1-L2, F-L2)。"
  },
  9331: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "阁楼厨房天花板木质斜顶被错染为失真暗红偏色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "木梁与天花板边缘泛暗红暖色调。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的暗红天花板色泽浓艳不自然。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "木质屋顶泛红破坏室内温馨自然感。"}
    ],
    "review_note": "阁楼厨房天花板木质斜顶被错染为失真暗红偏色(C-L2, D-L1, E1-L2, F-L1)。"
  },

  # Sheet 06 (Tasks 9332, 9333, 9334, 9336, 9338, 9339)
  9332: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "白色瓷碗与餐桌面大面积浸染冷青蓝偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "瓷碗边缘青蓝杂色略显浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "冷青色调破坏食物餐具温馨感。"}
    ],
    "review_note": "红甜椒丝欠饱和暗淡，白色瓷碗与桌面浸染冷青蓝偏色(D-L1, E1-L1, F-L1)。"
  },
  9333: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "新鲜西兰花花球被毁灭性脱色错染为惨白灰暗无生机。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "盘子边缘微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "翠绿西兰花翠绿色完全丧失，严重欠饱和脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "蔬菜惨白失去新鲜食材食用质感。"}
    ],
    "review_note": "新鲜西兰花花球被毁灭性脱色褪变为惨白灰暗(C-L3, D-L1, E2-L3, F-L2)。"
  },
  9334: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "果盘边缘与香蕉暗部微染暗黄灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "红苹果暗部与香蕉皮色泽略显暗淡欠饱和。"}
    ],
    "review_note": "果盘红苹果与香蕉暗部微染暗黄灰色调(D-L1, E2-L1)。"
  },
  9336: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9338: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "街景建筑墙面与通话西装男士大面积错染失真冷青灰偏色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "整幅画面大面积泛青灰冷调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "人物肤色与街景色彩欠饱和脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "街景冰冷青灰丧失城市生机。"}
    ],
    "review_note": "街景与通话西装男士大面积浸染失真冷青灰偏色(C-L2, D-L2, E2-L2, F-L2)。"
  },
  9339: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "生鲜冷柜蔬菜陈列边缘错染失真深洋红伪色斑块。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "冷柜边框与反光板微泛洋红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的深洋红杂斑浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "蔬菜货架紫红伪色严重违背常理。"}
    ],
    "review_note": "生鲜冷柜蔬菜陈列边缘错染失真深洋红伪色斑块(C-L2, D-L1, E1-L2, F-L2)。"
  },

  # Sheet 07 (Tasks 9340, 9341, 9342, 9343, 9345, 9348)
  9340: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9341: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L3", "description": "室内网球场地板、球网与墙壁大面积浸染严重失真的暗紫红褐色偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "网球场色彩层次严重脱色发枯发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "全场紫褐色调严重失真破坏空间真实感。"}
    ],
    "review_note": "室内网球场大面积浸染严重失真的暗紫红褐色偏色(D-L3, E2-L3, F-L3)。"
  },
  9342: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "小黑狗奔跑草坪被错染为失真刺眼的荧光青绿色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "小黑狗毛发高光微染青蓝偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "草坪荧光翠绿色彩过于浓艳溢出。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "荧光草地违背自然草木常理。"}
    ],
    "review_note": "小黑狗奔跑草坪错染为失真刺眼的荧光青绿色(C-L2, D-L1, E1-L2, F-L1)。"
  },
  9343: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "室内旋转木马游乐场大面积浸染冰冷青蓝紫杂色，彩绘被错染。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "木马身躯与顶棚支柱泛青蓝偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "旋转木马原本温暖金黄彩绘欠饱和严重脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "游乐设施冷调偏色破坏欢乐温馨氛围。"}
    ],
    "review_note": "室内旋转木马游乐场大面积浸染冰冷青蓝紫杂色(C-L2, D-L2, E2-L2, F-L2)。"
  },
  9345: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "苹果酒易拉罐翠绿色标签大字被颠覆性错染为深洋红粉紫色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "易拉罐金属罐身微泛冷青偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的深洋红字体过于浓艳突兀。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "标签大字颠覆性错色严重破坏商业包装真实度。"}
    ],
    "review_note": "苹果酒易拉罐翠绿色标签大字被颠覆性错染为深洋红粉紫色(C-L3, D-L1, E1-L2, F-L2)。"
  },
  9348: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 08 (Tasks 9350, 9351, 9352, 9353, 9354, 9355)
  9350: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9351: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9352: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "白色微波炉外壳背光处微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "微波炉按键面板与机身暗部色彩略显暗淡欠饱和。"}
    ],
    "review_note": "白色微波炉外壳背光处略显暗淡欠饱和，微染冷青灰色调(D-L1, E2-L1)。"
  },
  9353: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9354: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "客房九宫格各小图室内壁炉与家具暗部微染冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "客房家具木质纹理与地毯背光处略显暗淡欠饱和。"}
    ],
    "review_note": "客房九宫格各小图室内壁炉与家具暗部层次略显暗淡欠饱和(D-L1, E2-L1)。"
  },
  9355: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "历史黑白照片整幅画面大面积浸染灰黄褐偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "全图严重欠饱和干瘪发灰，缺乏色彩生机。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "全图灰褐偏色使黑白照片老旧干瘪。"}
    ],
    "review_note": "历史黑白照片整幅画面大面积浸染灰黄褐偏色，欠饱和干瘪(D-L2, E2-L3, F-L2)。"
  },

  # Sheet 09 (Tasks 9358, 9362, 9363, 9364, 9365, 9366)
  9358: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "餐盘煎肉排暗部与薯条背阴处微染暗黄灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "煎肉排焦香色泽略显暗淡欠饱和。"}
    ],
    "review_note": "餐盘煎肉排暗部与薯条背阴处略显暗淡欠饱和(D-L1, E2-L1)。"
  },
  9362: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9363: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9364: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "夜市果蔬摊遮阳棚与陈列架错染失真深蓝紫偏色与杂斑。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "货架阴影大面积泛深蓝紫偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的深蓝紫杂斑浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "果蔬摊被蓝紫杂斑污染破坏夜市烟火气。"}
    ],
    "review_note": "夜市果蔬摊遮阳棚与陈列架错染失真深蓝紫偏色与杂斑(C-L2, D-L2, E1-L2, F-L2)。"
  },
  9365: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9366: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 10 (Tasks 9367, 9368, 9369, 9370, 9372, 9373)
  9367: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "女士手中飘扬鲜艳大红丝巾被颠覆性脱色褪变为惨白灰暗无色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "女士风衣与背光处微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "大红丝巾红色完全丧失，严重欠饱和脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "丝巾彻底褪色严重破坏画面视觉焦点。"}
    ],
    "review_note": "女士手中飘扬鲜艳大红丝巾被颠覆性脱色褪变为惨白灰暗(C-L3, D-L1, E2-L3, F-L2)。"
  },
  9368: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9369: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9370: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "背景大红可口可乐易拉罐被颠覆性脱色褪变为惨白灰黑色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "桌面与背景大面积泛冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "经典红色易拉罐严重欠饱和脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "经典红罐褪色严重违背商业标识常识。"}
    ],
    "review_note": "背景大红可口可乐易拉罐被颠覆性脱色褪变为惨白灰黑色(C-L3, D-L2, E2-L3, F-L2)。"
  },
  9372: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "卧室双人床提花被褥与熟睡花猫白色毛发大面积浸染冷青灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "床单与猫咪背光处色彩略显暗淡欠饱和。"}
    ],
    "review_note": "卧室双人床提花被褥与熟睡花猫白色毛发大面积浸染冷青灰偏色(D-L1, E2-L1)。"
  },
  9373: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 11 (Tasks 9375, 9377, 9378, 9381, 9382, 9383)
  9375: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "床铺天蓝色床单被颠覆性错染为高饱和鲜红色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "卧室床铺大面积泛深红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L3", "description": "错染的鲜红床单色泽极度浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "蓝天床单错染大红彻底破坏卧室平静氛围。"}
    ],
    "review_note": "床铺天蓝色床单被颠覆性错染为高饱和鲜红色伪色(C-L3, D-L2, E1-L3, F-L3)。"
  },
  9377: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9378: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "机械设备箱体表面大面积错染刺眼深洋红与蓝紫伪色。"},
      {"id": "D", "name": "偏色", "severity": "L3", "description": "工业设备金属外壳泛浓重深洋红紫偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "紫红伪色斑块浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "金属机械严重错染伪色破坏工业真实感。"}
    ],
    "review_note": "机械设备箱体表面大面积错染刺眼深洋红与蓝紫伪色(C-L2, D-L3, E1-L2, F-L3)。"
  },
  9381: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "庭院木质甲板表面边缘接缝微染冷青灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "户外木质甲板略显暗淡欠饱和。"}
    ],
    "review_note": "庭院木质甲板表面略显暗淡欠饱和，边缘接缝微染冷青灰偏色(D-L1, E2-L1)。"
  },
  9382: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "农场围栏与草坡背光处微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "牛群棕黑毛发与草坡色彩欠饱和暗淡脱色。"}
    ],
    "review_note": "农场围栏牛群毛发与草坡欠饱和暗淡脱色(D-L1, E2-L1)。"
  },
  9383: {
    "action": "revise",
    "defects": [
      {"id": "B", "name": "溢色", "severity": "L2", "description": "雨伞伞面深洋红伪色越界严重渗透侵染周围背景。"},
      {"id": "C", "name": "错色", "severity": "L2", "description": "天蓝色卡通折叠伞面大面积错染深洋红紫偏色斑块。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "伞面与手柄大面积泛深紫红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的深洋红色彩浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "雨伞大面积伪色与严重溢色破坏整体画面。"}
    ],
    "review_note": "天蓝色卡通折叠伞面大面积错染深洋红紫偏色斑块，溢色严重(B-L2, C-L2, D-L2, E1-L2, F-L3)。"
  },

  # Sheet 12 (Tasks 9385, 9386, 9390, 9394, 9396, 9399)
  9385: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "电脑办公桌面暗部与键盘转角微染冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "桌面木质纹理与显示器底座略显暗淡欠饱和。"}
    ],
    "review_note": "电脑办公桌面暗部与键盘转角细节略显暗淡欠饱和(D-L1, E2-L1)。"
  },
  9386: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "仰卧滑雪选手大红滑雪服严重脱色错染为暗褐红色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "雪地反光与选手头盔微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "红色滑雪服欠饱和严重脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "红色滑雪服脱色降低雪场动感。"}
    ],
    "review_note": "仰卧滑雪选手大红滑雪服欠饱和严重脱色发暗(C-L2, D-L1, E2-L1, F-L1)。"
  },
  9390: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9394: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "荒原草木与远景地平线微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "荒原长颈鹿网状斑纹与灌木草地大面积欠饱和严重脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "荒原动物与植被脱色显干瘪苍白。"}
    ],
    "review_note": "荒原长颈鹿网状斑纹与灌木草地大面积欠饱和严重脱色(D-L1, E2-L2, F-L1)。"
  },
  9396: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "水塘边沙滩泥地大面积浸染失真火红暖黄偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "泥土地面红色调浓艳过度溢出。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "泥土严重泛红破坏水边自然湿地质感。"}
    ],
    "review_note": "水塘边沙滩泥地大面积浸染失真火红暖黄偏色(D-L2, E1-L2, F-L2)。"
  },
  9399: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "聚餐男女面部阴影与金属冰桶暗部微染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "餐桌人物面部肤色背阴处略显暗淡欠饱和。"}
    ],
    "review_note": "聚餐男女面部阴影与金属冰桶暗部略显暗淡欠饱和(D-L1, E2-L1)。"
  },

  # Sheet 13 (Tasks 9400, 9401, 9402, 9403, 9404, 9405)
  9400: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "披萨烘烤饼皮与盘沿暗部微染暗黄灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "披萨焦香芝士与肉粒色泽略显暗淡欠饱和。"}
    ],
    "review_note": "披萨焦香饼皮与盘沿暗部略显暗淡欠饱和(D-L1, E2-L1)。"
  },
  9401: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "花园原木长椅暖黄色木质纹理严重脱色错染为枯黑灰暗。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "长椅支架与周围草地微染冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "原木长椅木质色泽严重欠饱和褪色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "木椅发黑发枯破坏花园温馨感。"}
    ],
    "review_note": "花园原木长椅暖黄色木质纹理严重脱色褪变为枯黑灰暗(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9402: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "黑白花猫毛发暗部与墙面微染冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "黑白花猫双眼微绿与背景色彩大面积欠饱和严重脱色干瘪。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "猫咪瞳孔脱色失去灵动神采。"}
    ],
    "review_note": "黑白花猫双眼微绿与墙面色彩大面积欠饱和严重脱色干瘪(D-L1, E2-L3, F-L2)。"
  },
  9403: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "切块蛋糕白色奶油与瓷盘边缘大面积浸染失真冷青蓝偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "奶油边缘青蓝杂色略显浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "甜品奶油大面积泛冷青色违背可口常识。"}
    ],
    "review_note": "切块蛋糕白色奶油与瓷盘边缘大面积浸染失真冷青蓝偏色(D-L2, E1-L1, F-L2)。"
  },
  9404: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "玄关高帮帆布鞋原本鲜艳大红色鞋帮欠饱和脱色褪变为暗灰褐色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "帆布鞋橡胶包头微染冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "红色鞋帮欠饱和脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "红鞋脱色降低了鞋履辨识度。"}
    ],
    "review_note": "玄关高帮帆布鞋原本鲜艳大红色鞋帮欠饱和脱色褪变为暗灰褐(C-L2, D-L1, E2-L1, F-L1)。"
  },
  9405: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "木桌陈列女包暗部与桌角微染冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "陈列粉红女包与深红钱包皮革色泽略显暗淡欠饱和。"}
    ],
    "review_note": "木桌陈列粉红女包与深红钱包皮革色泽略显暗淡欠饱和(D-L1, E2-L1)。"
  },

  # Sheet 14 (Tasks 9406, 9407, 9408, 9409, 9410, 9413)
  9406: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "旧式电视机机壳背光处微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "室内电视机与木桌阴影色彩略显暗淡欠饱和。"}
    ],
    "review_note": "室内旧式电视机背光处与木桌阴影色彩略显暗淡欠饱和(D-L1, E2-L1)。"
  },
  9407: {
    "action": "revise",
    "defects": [
      {"id": "B", "name": "溢色", "severity": "L3", "description": "女孩身躯与衣服刺眼暖黄与深洋红伪色严重溢出色块外侵染周围空间。"},
      {"id": "C", "name": "错色", "severity": "L2", "description": "站立女孩身躯大面积错染刺眼暖黄与深洋红伪色斑块。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "人物与背景大面积泛深红黄紫杂乱偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的暖黄洋红伪色极其浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "人物被恶性伪色大面积污染破坏真实感。"}
    ],
    "review_note": "站立女孩身躯大面积错染刺眼暖黄与深洋红伪色斑块，溢色严重(B-L3, C-L2, D-L2, E1-L2, F-L3)。"
  },
  9408: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9409: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "农场草坡木栅栏与背阴处微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "草坡羊群毛发背阴处与木栅栏细节略显暗淡欠饱和。"}
    ],
    "review_note": "农场草坡羊群毛发背阴处与木栅栏细节略显暗淡欠饱和(D-L1, E2-L1)。"
  },
  9410: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "草木背景与车身金属反光微泛冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "复古摩托车金属车身与背景草木大面积欠饱和严重脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "车身脱色失去金属油润光泽。"}
    ],
    "review_note": "复古摩托车金属车身与背景草木大面积欠饱和严重脱色(D-L1, E2-L2, F-L1)。"
  },
  9413: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 15 (Tasks 9414, 9418, 9419, 9420, 9421, 9423)
  9414: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "公园折叠椅游客大红色短袖严重脱色错染为灰褐暗色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "游客手臂肤色与折叠椅微泛冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "大红短袖欠饱和严重脱色变暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "短袖脱色破坏户外游憩生机。"}
    ],
    "review_note": "公园折叠椅游客大红色短袖欠饱和严重脱色变暗(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9418: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9419: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "海滨椰子树、海浪与阴云天空大面积浸染失真暗红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "天空暗红云层色泽略显偏浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "热带海滩泛红破坏自然海滨气候感。"}
    ],
    "review_note": "海滨椰子树、海浪与阴云天空大面积浸染失真暗红偏色(D-L2, E1-L1, F-L2)。"
  },
  9420: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "餐桌男士面部肤色与披萨边缘微泛火红暖偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "男士面部红润与披萨色泽略显偏红浓艳。"}
    ],
    "review_note": "餐桌男士面部肤色与披萨边缘色泽略显偏红浓艳(D-L1, E1-L1)。"
  },
  9421: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "甜品盘抹茶果冻与树莓果肉错染刺眼荧光青绿与深洋红伪色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "白色甜品盘边缘微泛冷青偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的荧光青绿与洋红色彩浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "甜品伪色斑块破坏精致甜点真实食欲感。"}
    ],
    "review_note": "甜品盘抹茶果冻与树莓果肉错染刺眼荧光青绿与深洋红伪色(C-L2, D-L1, E1-L2, F-L2)。"
  },
  9423: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 16 (Tasks 9425, 9426, 9427, 9428, 9429, 9430)
  9425: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "三轮摩托车车架暗部与塑料瓶装回收物微染暗灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "车斗装载的塑料瓶与车轮阴影色彩略显暗淡欠饱和。"}
    ],
    "review_note": "街头三轮摩托车装载塑料瓶与车轮阴影色彩略显暗淡欠饱和(D-L1, E2-L1)。"
  },
  9426: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "大象背上游客红色短袖严重脱色错染为暗灰褐色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "草地与大象身躯微泛灰冷偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "红短袖与周边草坪欠饱和褪色发枯。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "游客服饰脱色降低骑象生动感。"}
    ],
    "review_note": "骑象游客鲜红短袖欠饱和脱色变暗，草坡发枯(C-L2, D-L1, E2-L1, F-L1)。"
  },
  9427: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "黑色蛋糕盘沿与翻糖边缘微染暗红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "切块蛋糕粉红翻糖奶油色泽略显偏浓艳。"}
    ],
    "review_note": "黑盘中切块蛋糕粉红翻糖奶油色泽略显偏浓艳(D-L1, E1-L1)。"
  },
  9428: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "天空飞舞的彩色风筝大面积严重脱色错染为灰白暗色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "草坪与天空背景微染冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "多色风筝欠饱和脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "风筝脱色失去放风筝的热闹生机。"}
    ],
    "review_note": "户外草坪放风筝人群天空风筝严重脱色发灰(C-L2, D-L1, E2-L1, F-L1)。"
  },
  9429: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9430: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "棒球击球手历史黑白照片整幅画面大面积浸染暗灰红褐偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "历史黑白照片全图严重欠饱和干瘪发灰。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "灰红褐色调覆盖使黑白人物照片浑浊不自然。"}
    ],
    "review_note": "棒球击球手黑白历史照片整幅画面大面积浸染暗灰红褐偏色，严重干瘪(D-L2, E2-L3, F-L2)。"
  },

  # Sheet 17 (Tasks 9431, 9435, 9438, 9439, 9440, 9444)
  9431: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "餐厅餐桌前戴眼镜男子面部肤色、黑色短袖与大盘披萨大面积浸染失真火红暖橙偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "男子面部与披萨暖红色彩偏浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "火红偏色严重破坏人物肤色自然度。"}
    ],
    "review_note": "餐厅餐桌前戴眼镜男子面部肤色与披萨大面积浸染失真火红暖橙偏色(D-L2, E1-L1, F-L2)。"
  },
  9435: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "草地废弃破船上方原本鲜艳的天蓝色遮阳篷布被颠覆性错染为暗红褐色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "破船残骸木料与背景杂草微泛红褐偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "错染的红褐色篷布色泽略显偏浓。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "蓝色船篷错染暗红颠覆真值常理。"}
    ],
    "review_note": "草地废弃破船上方原本天蓝色遮阳篷布被颠覆性错染为暗红褐色伪色(C-L3, D-L1, E1-L1, F-L2)。"
  },
  9438: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "花瓶中白色雏菊的花瓣、黄色花心与枝叶密集边缘错染失真深蓝紫与洋红色伪色斑块。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "花瓶颈部与桌面微泛冷青偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "错染的深蓝紫伪色浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "白花密集区域紫蓝伪色严重违背鲜花常理。"}
    ],
    "review_note": "花瓶中白色雏菊的花瓣、黄色花心与枝叶密集边缘错染失真深蓝紫与洋红色伪色斑块(C-L2, D-L1, E1-L2, F-L2)。"
  },
  9439: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "欧式古典教堂石砌钟楼外墙色调微染暖黄灰色偏色。"}
    ],
    "review_note": "欧式古典教堂石砌钟楼外墙色调微染暖黄灰色偏色(D-L1)。"
  },
  9440: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "丘陵草坡前景黄泥土埂与白羊背阴处微染暖灰褐色偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "丘陵绿草坡前景泥土埂与趴卧小羊背阴处色彩层次略显暗淡欠饱和。"}
    ],
    "review_note": "丘陵绿草坡前景泥土埂与趴卧小羊背阴处色彩层次略显暗淡欠饱和(D-L1, E2-L1)。"
  },
  9444: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "金属立柱上八角形STOP停止标志牌原本鲜艳的大红色底漆欠饱和脱色发暗，边缘贴纸色泽暗淡。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "标志牌白色英文字母微泛冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "红色底板大面积欠饱和脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "停止牌脱色降低警示标志辨识度。"}
    ],
    "review_note": "金属立柱上八角形STOP停止标志牌原本鲜艳的大红色底漆欠饱和脱色发暗，贴纸暗淡(C-L2, D-L1, E2-L1, F-L1)。"
  },

  # Sheet 18 (Tasks 9446, 9448, 9451, 9452, 9453, 9454)
  9446: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "室内静物背景墙壁与白色桌布被严重错染为浓重刺眼的深洋红色伪色偏色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "全幅静物大面积泛浓厚深洋红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "深洋红杂色极度浓艳溢出。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "白墙与桌布错染大红彻底破坏静物素雅氛围。"}
    ],
    "review_note": "室内静物背景墙壁与白色桌布被严重错染为浓重刺眼的深洋红色伪色偏色(C-L3, D-L2, E1-L2, F-L3)。"
  },
  9448: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "稀树草原背景原本晴朗蔚蓝的天空大面积欠饱和严重脱色褪变为一片浑浊灰黄色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "草原天空与草地大面积泛灰土黄偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "蓝天天色完全丧失，严重欠饱和脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "晴空褪变为浑浊灰黄严重破坏自然景观可信度。"}
    ],
    "review_note": "稀树草原背景原本晴朗蔚蓝的天空大面积欠饱和严重脱色褪变为一片浑浊灰黄色(C-L3, D-L2, E2-L3, F-L3)。"
  },
  9451: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "客厅沙发左侧靠枕与男孩坐垫被错染为刺眼的荧光黄绿色与失真红褐色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "沙发靠枕与坐垫泛杂乱黄绿与暗红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "荧光黄绿杂色浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "靠枕错染荧光色严重破坏家居温馨真实感。"}
    ],
    "review_note": "客厅沙发左侧靠枕与男孩坐垫被错染为刺眼的荧光黄绿色与失真红褐色伪色(C-L2, D-L2, E1-L2, F-L2)。"
  },
  9452: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9453: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9454: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "海滩木桩上海鸟眼部周围原本鲜艳的金黄色皮肤大面积欠饱和严重脱色发白。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "海鸟背部羽毛与沙滩微泛灰冷偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "眼周金黄裸皮严重脱色发灰。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "鸟眼部黄色特征丢失影响生物自然神韵。"}
    ],
    "review_note": "海滩木桩上海鸟眼部周围原本鲜艳的金黄色皮肤大面积欠饱和严重脱色发白(C-L2, D-L1, E2-L2, F-L1)。"
  },

  # Sheet 19 (Tasks 9455, 9456, 9457, 9459, 9460, 9465)
  9455: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "河畔现代高楼玻璃幕墙与天空大面积浸染失真浓艳的冰冷青蓝偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "高楼幕墙与天空青蓝色调浓艳过度溢出。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "全城泛深冷青色破坏真实都市天际线景观。"}
    ],
    "review_note": "河畔现代高楼玻璃幕墙与天空大面积浸染失真浓艳的冰冷青蓝偏色(D-L2, E1-L2, F-L2)。"
  },
  9456: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "办公桌暗部与墙角微染暗黄灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "办公桌上电脑显示器背光处、键盘边缘与墙角阴影色彩略显暗淡欠饱和。"}
    ],
    "review_note": "办公桌上电脑显示器背光处、键盘边缘与墙角阴影色彩略显暗淡欠饱和(D-L1, E2-L1)。"
  },
  9457: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "盛放小花猫的塑料盆边缘与内侧大面积错染为失真刺眼的荧光翠绿色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "猫咪毛发高光与背景微泛翠绿偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "塑料盆荧光绿色浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "荧光塑料盆严重违背真实塑料制品色泽。"}
    ],
    "review_note": "盛放小花猫的塑料盆边缘与内侧大面积错染为失真刺眼的荧光翠绿色伪色(C-L2, D-L1, E1-L2, F-L2)。"
  },
  9459: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "餐盘边缘与烤香蕉暗部微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "餐盘中烤香蕉表皮与果肉焦糖色泽大面积欠饱和脱色变暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "甜点脱色发灰破坏可口诱人质感。"}
    ],
    "review_note": "餐盘中烤香蕉表皮与果肉焦糖色泽大面积欠饱和脱色变暗，微染冷青灰色调(D-L1, E2-L2, F-L1)。"
  },
  9460: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9465: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "客厅地面浅色地毯与躺椅罩布被颠覆性严重错染为刺眼浓艳的深洋红紫红伪色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "室内木质窗框与踢脚线微泛红紫偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L3", "description": "地毯与罩布深洋红色彩极度浓艳刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "大面积刺眼洋红地毯严重破坏客厅自然素雅氛围。"}
    ],
    "review_note": "客厅地面浅色地毯与躺椅罩布被颠覆性严重错染为刺眼浓艳的深洋红紫红伪色(C-L3, D-L1, E1-L3, F-L3)。"
  },

  # Sheet 20 (Tasks 9466, 9467, 9468, 9470, 9472, 9473)
  9466: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9467: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "室内餐桌旁聚会女士服饰严重脱色错染为灰青冷调。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "人物肤色与背景窗帘微泛冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "女士服饰与桌面各色饮料瓶大面积欠饱和脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "服饰与饮品脱色破坏聚会热闹生机。"}
    ],
    "review_note": "室内餐桌旁聚会女士服饰与桌面各色饮料瓶大面积欠饱和脱色发暗，微染冷青灰色调(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9468: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "客厅沙发与小狗毛发微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "客厅沙发上趴卧小狗金黄色毛发与米黄靠垫色泽略显暗淡欠饱和。"}
    ],
    "review_note": "客厅沙发上趴卧小狗金黄色毛发与米黄靠垫色泽略显暗淡欠饱和，微染冷青灰色调(D-L1, E2-L1)。"
  },
  9470: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L2", "description": "厨房双门冰箱上方背景墙面与找寻食物男子面部肤色浸染失真红褐偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "背景墙面红褐色调偏浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "厨房墙面大面积泛红偏色破坏室内自然采光感。"}
    ],
    "review_note": "厨房双门冰箱上方背景墙面与找寻食物男子面部肤色浸染失真红褐偏色(D-L2, E1-L1, F-L1)。"
  },
  9472: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "陶瓷马桶转角与瓷砖接缝微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "卫生间马桶座圈上蹲坐猫咪毛发背阴处与陶瓷马桶转角阴影色彩略显暗淡欠饱和。"}
    ],
    "review_note": "卫生间马桶座圈上蹲坐猫咪毛发背阴处与陶瓷马桶转角阴影色彩略显暗淡欠饱和(D-L1, E2-L1)。"
  },
  9473: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "浴室柜背光阴影与镜框转角微染暗灰褐色偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "卫生间白色浴室柜背光阴影与镜框暗部细节色泽略显暗淡欠饱和。"}
    ],
    "review_note": "卫生间白色浴室柜背光阴影与镜框暗部细节色泽略显暗淡欠饱和(D-L1, E2-L1)。"
  }
}

def apply_batch_47():
    base_dir = r"d:\学业文件\MCL\上色评价_数据集标注\LS_lcad_reviewer"
    grounding_path = os.path.join(base_dir, "intermediate", "audits", "grounding_remaining_batch_47.json")
    all_path = os.path.join(base_dir, "exports", "reviewed_1_10000_all.json")
    clean_path = os.path.join(base_dir, "exports", "reviewed_1_10000_clean.json")

    # 1. 导出 grounding_remaining_batch_47.json
    with open(grounding_path, 'w', encoding='utf-8') as f:
        json.dump(BATCH_47_REVIEWS, f, indent=2, ensure_ascii=False)
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

    for task_id, review in BATCH_47_REVIEWS.items():
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

    print("Batch 47 applied successfully!")
    print(f"Total: {len(BATCH_47_REVIEWS)}, Passes: {pass_count} ({pass_count/len(BATCH_47_REVIEWS)*100:.2f}%), Revised: {revised_count} ({revised_count/len(BATCH_47_REVIEWS)*100:.2f}%), Meltdown A: {meltdown_count}")

if __name__ == '__main__':
    apply_batch_47()
