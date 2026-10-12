import json
import os
import copy

BATCH_49_REVIEWS = {
  # Sheet 01 (Tasks 9689, 9690, 9691, 9694, 9695, 9696)
  9689: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9690: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "卧室床头暖黄色壁灯照耀下，原本洁白的羽绒被面与枕头表面被轻微杂染泛暖黄橙色调。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "卧室床头灯光照射区域微带偏暖偏橙调。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "被褥微染暖橙色影响纯净睡梦质感。"}
    ],
    "review_note": "卧室床头暖黄色壁灯照耀下，原本洁白的羽绒被面与枕头表面被轻微杂染泛暖黄橙色调(C-L1, D-L1, F-L1)。"
  },
  9691: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9694: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9695: {
    "action": "revise",
    "defects": [
      {"id": "D", "name": "偏色", "severity": "L1", "description": "街道停靠警车背景处的多层红砖建筑外墙存在轻微偏暖红调。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "红砖建筑外墙红褐色调过于浓郁刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "外墙红砖过饱和略失年代厚重感。"}
    ],
    "review_note": "街道停靠警车背景处的多层红砖建筑外墙红褐色调过于浓郁刺眼，红砖墙面存在轻微过饱和与偏暖红调(D-L1, E1-L1, F-L1)。"
  },
  9696: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "丝芙兰橱窗内陈列的大型毛绒玩具棕熊全身棕褐色毛发大面积欠饱和褪变为暗灰绿褐色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "橱窗内鲜花与装饰织物严重泛冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "毛绒玩具皮毛光泽严重欠饱和脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "冷青色调破坏商业橱窗精致观感。"}
    ],
    "review_note": "丝芙兰橱窗前陈列的大型毛绒玩具棕熊全身棕褐色毛发大面积欠饱和褪变为暗灰绿褐色，橱窗内鲜花与装饰织物严重泛冷青伪色(C-L2, D-L2, E2-L1, F-L2)。"
  },

  # Sheet 02 (Tasks 9698, 9702, 9703, 9705, 9707, 9708)
  9698: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "餐盘中法棍面包三明治表皮原本诱人的金黄色烘烤色泽泛冷发暗。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "盛放三明治的白色纸盘表面显现轻微冷青色偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "法棍面包麦香焦色轻度欠饱和脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "三明治面包冷沉色泽削弱食欲。"}
    ],
    "review_note": "餐盘中法棍面包三明治表皮原本诱人的金黄色烘烤色泽泛冷发暗，盛放的白色纸盘表面显现轻微冷青色偏色(C-L1, D-L1, E2-L1, F-L1)。"
  },
  9702: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9703: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "维多利亚风格木质洋房深色屋顶与外立面木质护墙板在晴空下泛轻微冷青色调。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "古典洋房建筑外立面浸染微冷青偏色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "花园草坪绿意略显不均。"}
    ],
    "review_note": "维多利亚风格木质洋房深色屋顶与外立面木质护墙板在晴空下泛轻微冷青色调，花园草坪绿意略显不均(C-L1, D-L1, F-L1)。"
  },
  9705: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "街道交通提示牌上方的红色圆形警示灯漆面严重欠饱和脱色褪变为粉白灰。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "右侧砖石建筑红砖外墙轻微泛灰偏冷。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "交通警示灯红色油漆严重欠饱和脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "交通标牌褪色丧失警示醒目感。"}
    ],
    "review_note": "街道交通提示牌上方的红色圆形警示灯漆面严重欠饱和脱色褪变为粉白灰，右侧砖石建筑红砖外墙轻微泛灰褪色(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9707: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "厨房上方原本温暖棕色的木质壁橱柜门与台面被轻微错染杂带冷青绿调。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "白色瓷砖墙面与料理台泛微冷青偏色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "冷色偏光削弱厨房温馨氛围。"}
    ],
    "review_note": "厨房上方原本温暖棕色的木质壁橱柜门与台面被轻微错染杂带冷青绿调，白色瓷砖墙面泛微冷色(C-L1, D-L1, F-L1)。"
  },
  9708: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "夜色中深绿色铸铁复古街头大钟表壳与内部发光钟盘表面轻微泛偏暖橙黄调。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "大钟夜间照明区域整体微染偏暖偏黄调。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "钟表表盘暖色发散降低夜视清透感。"}
    ],
    "review_note": "夜色中深绿色铸铁复古街头大钟表壳与内部发光钟盘表面轻微泛偏暖橙黄调(C-L1, D-L1, F-L1)。"
  },

  # Sheet 03 (Tasks 9712, 9713, 9714, 9717, 9720, 9721)
  9712: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9713: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "室内办公桌左侧白色储物柜与后方白墙表面显现不自然的淡紫红色杂色泛染。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "储物柜受光面微染淡紫红偏色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "白墙与储物柜紫红杂色破坏洁净感。"}
    ],
    "review_note": "室内办公桌左侧白色储物柜与后方白墙表面显现不自然的淡紫红色杂色泛染(C-L1, D-L1, F-L1)。"
  },
  9714: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "滑板少年脚下滑板坡道地面的彩色涂鸦彩绘大面积欠饱和褪色发白。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "背景湛蓝晴空饱和度偏低泛暗。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "街头涂鸦明艳橙黄与湛蓝晴空大面积欠饱和褪色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "滑板场地色彩暗淡削弱运动活力。"}
    ],
    "review_note": "滑板少年脚下滑板坡道地面的彩色涂鸦彩绘大面积欠饱和褪色发白，背景湛蓝晴空饱和度偏低泛暗(C-L1, D-L1, E2-L2, F-L1)。"
  },
  9717: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "运河游船旁户外露天餐桌前年轻男士面部肤色微带偏暗。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "后方绿荫河道与游船边缘色调偏暗沉。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "河道阴影暗调略显生硬。"}
    ],
    "review_note": "运河游船旁户外露天餐桌前年轻男士面部肤色微带偏暗，后方绿荫河道与游船边缘色调偏暗沉(C-L1, D-L1, F-L1)。"
  },
  9720: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "黑色猎犬脚下的草坪绿草与地上的荧光绿飞盘色泽欠饱和偏暗。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "草坪整体绿意泛冷灰沉闷。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "绿茵草坪与飞盘色彩轻度欠饱和。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "草地沉闷冷调略失阳光草坪活力。"}
    ],
    "review_note": "黑色猎犬脚下的草坪绿草与地上的荧光绿飞盘色泽欠饱和偏暗，草坪整体绿意泛冷灰沉闷(C-L1, D-L1, E2-L1, F-L1)。"
  },
  9721: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "昏暗光线下女士操作的笔记本电脑屏幕强烈反光处泛荧光红橙杂色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "后方墙壁显现轻微冷绿偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "屏幕高光反射区暖红杂色轻度过饱和。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "反光杂色破坏夜视暗调真实感。"}
    ],
    "review_note": "昏暗光线下女士操作的笔记本电脑屏幕强烈反光处泛荧光红橙杂色，后方墙壁显现轻微冷绿偏色(C-L1, D-L1, E1-L1, F-L1)。"
  },

  # Sheet 04 (Tasks 9722, 9723, 9725, 9732, 9735, 9736)
  9722: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9723: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "街道转角处红色八角形STOP停车警示标志牌红漆表面明显欠饱和脱色泛粉白。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "右侧树冠绿意略显暗淡偏冷。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "STOP停车标牌警示红漆轻度欠饱和褪色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "交通标志红漆褪色降低辨识度。"}
    ],
    "review_note": "街道转角处红色八角形STOP停车警示标志牌红漆表面明显欠饱和脱色泛粉白，右侧树冠绿意略显暗淡(C-L1, D-L1, E2-L1, F-L1)。"
  },
  9725: {
    "action": "meltdown_a",
    "defects": [
      {"id": "A", "name": "缺色", "severity": "", "description": "全图上色严重失败，画面彻底退化为纯黑白灰阶图像，全域无任何色彩呈现（熔断项 A）。"}
    ],
    "review_note": "全图上色严重失败，画面彻底退化为纯黑白灰阶图像，全域无任何色彩呈现（熔断项 A）。"
  },
  9732: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9735: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "室内活动现场右侧男士身穿的原本鲜艳大红色长袖POLO衫严重欠饱和脱色褪变为黯淡砖粉色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "周围人群服饰与环境整体严重泛冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "男士大红POLO衫鲜亮纯色大面积脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "人群服饰严重泛灰破坏现场生动氛围。"}
    ],
    "review_note": "室内活动现场右侧男士身穿的原本鲜艳大红色长袖POLO衫严重欠饱和脱色褪变为黯淡砖粉色，周围人群服饰整体泛灰失真(C-L2, D-L2, E2-L2, F-L1)。"
  },
  9736: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "烘焙面包夹心卷金黄脆皮表面与洋葱碎屑轻微泛偏暖橙黄调。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "面包馅料与表皮整体微染偏暖偏橙调。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "微弱偏暖调略显厚重。"}
    ],
    "review_note": "烘焙面包夹心卷金黄脆皮表面与洋葱碎屑轻微泛偏暖橙黄调(C-L1, D-L1, F-L1)。"
  },

  # Sheet 05 (Tasks 9740, 9741, 9742, 9743, 9745, 9747)
  9740: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9741: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "餐桌丰盛宴席摆放的盛有青翠绿叶蔬菜与凉拌红苋菜的白瓷盘表面存在轻度偏暖杂染。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "菜肴盛装盘边缘微染暖黄偏色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "白瓷盘暖黄杂染略影响摆盘清爽度。"}
    ],
    "review_note": "餐桌丰盛宴席摆放的盛有青翠绿叶蔬菜与凉拌红苋菜的白瓷盘表面存在轻度偏暖杂染(C-L1, D-L1, F-L1)。"
  },
  9742: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9743: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9745: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "浴室洗手台木质浴室柜与台面在暖光照明下显现轻微偏暖黄调。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "浴室柜与米黄瓷砖墙微染偏暖偏黄调。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "暖黄色调略微加深台面反光。"}
    ],
    "review_note": "浴室洗手台木质浴室柜与台面在暖光照明下显现轻微偏暖黄调(C-L1, D-L1, F-L1)。"
  },
  9747: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 06 (Tasks 9749, 9751, 9752, 9754, 9755, 9757)
  9749: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9751: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "树枝上栖息的五彩鹦鹉原本鲜艳的红色羽毛与黄绿胸腹部严重脱色，背景原本清澈的浅天蓝色幕布彻底欠饱和脱色褪变为单调冷水泥灰。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "背景天空与羽毛大面积浸染死寂冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "五彩鹦鹉羽色与浅蓝背景近乎完全脱色失活。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "背景与鸟羽大面积泛灰严重破坏画面美感。"}
    ],
    "review_note": "树枝上栖息的五彩鹦鹉原本鲜艳的红色羽毛与黄绿胸腹部严重欠饱和脱色，背景原本清澈的浅天蓝色幕布彻底欠饱和脱色褪变为单调冷水泥灰(C-L3, D-L2, E2-L3, F-L2)。"
  },
  9752: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9754: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "餐台前静坐的小男孩白色衣领与背景成熟明黄香蕉表面显现轻微偏暖暗调。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "男孩面部肤色与衣领微染偏暖偏黄调。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "暖调略加深阴影暗部。"}
    ],
    "review_note": "餐台前静坐的小男孩白色衣领与背景成熟明黄香蕉表面显现轻微偏暖暗调(C-L1, D-L1, F-L1)。"
  },
  9755: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9757: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "沙滩上停靠的木质渔船原本鲜艳的青绿色与粉红漆面船体彻底欠饱和严重脱色褪变为暗灰黑色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "阴天沙滩与海浪大面积浸染沉闷冷灰调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "彩色木质渔船漆面完全脱色丧失色彩活力。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "木质渔船脱色发黑严重违背原图真实生动风貌。"}
    ],
    "review_note": "沙滩上停靠的木质渔船原本鲜艳的青绿色与粉红漆面船体彻底欠饱和严重脱色褪变为暗灰黑色，船身彩色涂漆完全丧失(C-L3, D-L1, E2-L3, F-L2)。"
  },

  # Sheet 07 (Tasks 9758, 9759, 9760, 9761, 9762, 9766)
  9758: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "巨型多肉仙人掌植物园中游客手持的原本鲜艳明亮的青蓝色雨伞严重错染泛黄棕，身穿的大红色防风外套出现欠饱和脱色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "仙人掌园区植物与游客衣物微染黄褐偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "游客雨伞与红色外套饱和度显著不足。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "雨伞错色变脏降低旅游场景鲜活性。"}
    ],
    "review_note": "巨型多肉仙人掌植物园中游客手持的原本鲜艳明亮的青蓝色雨伞严重错染泛黄棕，身穿的大红色防风外套出现欠饱和脱色(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9759: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "蓝白格子桌布上摆放的新鲜烘烤披萨表面奶酪与肉馅泛绿杂色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "桌布与啤酒杯区域显现轻度偏冷偏蓝调。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "桌布蓝白格纹与金黄啤酒过于浓艳过饱和。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "披萨奶酪泛绿影响美食真实感。"}
    ],
    "review_note": "蓝白格子桌布上摆放的新鲜烘烤披萨表面奶酪与肉馅泛绿杂色，周围两杯精酿啤酒金黄酒液与桌布蓝白格纹呈现轻度过饱和(C-L1, D-L1, E1-L2, F-L1)。"
  },
  9760: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "棒球场内野比赛红土区域泥土原本红润的色泽偏向枯黄。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "击球手与捕手运动球衣局部色彩略有失真偏黄。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "内野红土偏枯黄色泽影响球场真实质感。"}
    ],
    "review_note": "棒球场内野比赛红土区域泥土原本红润的色泽偏向枯黄，击球手与捕手运动球衣局部色彩略有失真(C-L1, D-L1, F-L1)。"
  },
  9761: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "室内静物台面上原本温暖米黄色的香奈儿手提纸袋与木质桌面被颠覆性错染为深紫黑与冰冷青蓝色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "全图环境色温发生严重冷青与紫蓝偏移。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "青蓝色桌面与紫黑背景过饱和刺眼。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "极具破坏性的冷青偏色彻底颠覆原图雅致暖调。"}
    ],
    "review_note": "室内静物台面上原本温暖米黄色的香奈儿手提纸袋与木质桌面被颠覆性错染为深紫黑与冰冷青蓝色伪色，全图环境色温发生严重冷青偏移(C-L3, D-L2, E1-L2, F-L3)。"
  },
  9762: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9766: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "跑道前排展示的红色法拉利与黄色兰博基尼等超跑车漆大面积欠饱和严重脱色变暗。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "跑道沥青与观赛人群整体偏冷灰暗沉。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "鲜红与亮黄超跑标志性车漆严重欠饱和褪色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "顶级超跑车漆暗淡发灰严重违背车展盛况。"}
    ],
    "review_note": "跑道前排展示的红色法拉利与黄色兰博基尼等超跑车漆大面积欠饱和严重脱色变暗，观赛人群色彩较为灰暗(C-L2, D-L1, E2-L2, F-L1)。"
  },

  # Sheet 08 (Tasks 9767, 9768, 9769, 9771, 9773, 9775)
  9767: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9768: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "餐桌前正襟危坐的小型吉娃娃犬面部毛发与身后室内墙壁轻微偏冷青暗沉。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "室内环境微染冷青色调，失去原片温暖光影。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "微冷调影响温馨宠物就餐画面。"}
    ],
    "review_note": "餐桌前正襟危坐的小型吉娃娃犬面部毛发与身后室内墙壁轻微偏冷青暗沉，光影氛围略失原片温暖(C-L1, D-L1, F-L1)。"
  },
  9769: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "酒店客房大床原本铺盖的素雅米白色床单被颠覆性错染为极其刺眼、极其浓烈的高饱和荧光亮黄色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "床头照明区过分偏暖偏黄。"},
      {"id": "E1", "name": "过饱和", "severity": "L3", "description": "床铺大面积荧光亮黄极度刺眼浓艳。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "刺眼荧光黄完全破坏客房素净睡眠环境。"}
    ],
    "review_note": "酒店客房大床原本铺盖的素雅米白色床单被颠覆性错染为极其刺眼、极其浓烈的高饱和荧光亮黄色伪色(C-L2, D-L1, E1-L3, F-L2)。"
  },
  9771: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "卧室上方墙壁原本粉红暖调的乳胶漆墙面被严重常识性错染为暗淡草绿色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "床头花布窗帘色调失真偏暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "粉红墙面变绿草绿严重冲突破坏卧室软装搭配。"}
    ],
    "review_note": "卧室上方墙壁原本粉红暖调的乳胶漆墙面被严重常识性错染为暗淡草绿色伪色，床头花布窗帘色调失真(C-L3, D-L1, F-L2)。"
  },
  9773: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9775: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 09 (Tasks 9776, 9777, 9781, 9782, 9784, 9785)
  9776: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "骑在亚洲象背上的女士身穿的深粉红背心略显脱色偏淡。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "象背周围雨林与河流光影微带偏暗偏偏蓝冷调。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "背心略褪色微损骑象人物生动感。"}
    ],
    "review_note": "骑在亚洲象背上的女士身穿的深粉红背心略显脱色偏淡，象背周围雨林与河流光影微带偏色(C-L1, D-L1, F-L1)。"
  },
  9777: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9781: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9782: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "室内玩耍幼猫脚下的原本温暖深红棕色实木地板彻底欠饱和严重脱色褪变为冰冷灰水泥地色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "全屋地面与墙角浸染单调冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "木地板原本红润饱和度完全归零丧失。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "暖木地板变冷灰地面严重破坏居家温馨质感。"}
    ],
    "review_note": "室内玩耍幼猫脚下的原本温暖深红棕色实木地板彻底欠饱和严重脱色褪变为冰冷灰水泥地色，幼猫皮毛暗淡无光(C-L3, D-L2, E2-L3, F-L2)。"
  },
  9784: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "草地放风筝场景原本泛着温暖晚霞橙黄色落日光辉的壮阔天空彻底欠饱和严重脱色褪变为单调死寂的冷灰天空。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "全场黄昏天光完全丧失暖橙色调，严重泛冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "壮美晚霞落日光彩完全脱色熄灭。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "绚烂晚霞变阴沉死灰天空极具违和感。"}
    ],
    "review_note": "草地放风筝场景原本泛着温暖晚霞橙黄色落日光辉的壮阔天空彻底欠饱和严重脱色褪变为单调死寂的冷灰天空(C-L3, D-L2, E2-L3, F-L2)。"
  },
  9785: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 10 (Tasks 9786, 9789, 9790, 9792, 9793, 9794)
  9786: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "室内半掩房门透出的明亮暖光走廊与右侧老旧CRT显示器黑色外壳边缘呈现轻微偏暗沉。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "门框木质边线与内室微染偏暖偏暗调。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "光线过渡稍欠平滑。"}
    ],
    "review_note": "室内半掩房门透出的明亮暖光走廊与右侧老旧CRT显示器黑色外壳边缘呈现轻微偏暗沉(C-L1, D-L1, F-L1)。"
  },
  9789: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "室内手持白色手柄体验体感游戏的女士面部与淡绿色背心连衣裙表面显现轻微偏暖暗调。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "人物与墙壁微染暖黄偏色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "肤色稍泛暖暗。"}
    ],
    "review_note": "室内手持白色手柄体验体感游戏的女士面部与淡绿色背心连衣裙表面显现轻微偏暖暗调(C-L1, D-L1, F-L1)。"
  },
  9790: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9792: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "快餐早餐托盘原本明亮温暖的橙黄色塑料餐盘被颠覆性错染为极其刺眼的荧光草绿色与青蓝色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "全图环境色温发生灾难性冷绿与冷青偏移。"},
      {"id": "E1", "name": "过饱和", "severity": "L3", "description": "塑料托盘荧光草绿极度浓艳刺目。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "橙黄托盘变荧光绿完全颠覆快餐食品视觉信赖。"}
    ],
    "review_note": "快餐早餐托盘原本明亮温暖的橙黄色塑料餐盘被颠覆性错染为极其刺眼的荧光草绿色与青蓝色伪色，餐巾纸与咖啡纸杯严重偏色失真(C-L3, D-L2, E1-L3, F-L3)。"
  },
  9793: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "雪地滑雪女士身穿的原本鲜艳明亮的青蓝色滑雪冲锋衣轻微欠饱和脱色偏深暗。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "雪山阴影与冲锋衣微染冷青灰色调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "青蓝滑雪服轻度欠饱和发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "滑雪服变暗略失雪原运动鲜艳辨识度。"}
    ],
    "review_note": "雪地滑雪女士身穿的原本鲜艳明亮的青蓝色滑雪冲锋衣轻微欠饱和脱色偏深暗，周围茫茫白雪与针叶树林色彩基本自然(C-L1, D-L1, E2-L1, F-L1)。"
  },
  9794: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "海滨观景平台护栏旁红色消防栓铸铁表面红漆微带偏暗。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "后方海湾水面与大桥色调平缓偏暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "海滨空气透视感微弱受损。"}
    ],
    "review_note": "海滨观景平台护栏旁红色消防栓铸铁表面红漆微带偏暗，后方海湾与大桥色调平缓(C-L1, D-L1, F-L1)。"
  },

  # Sheet 11 (Tasks 9796, 9797, 9799, 9800, 9801, 9804)
  9796: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "海滩沙地上方远处停放的深红色小轿车车漆严重欠饱和脱色褪变为暗灰黑色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "沙滩与天空微染冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "深红色轿车车漆欠饱和严重脱色变暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "红车褪色变黑破坏海滨游憩场景真实度。"}
    ],
    "review_note": "海滩沙地上方远处停放的深红色小轿车车漆严重欠饱和脱色褪变为暗灰黑色(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9797: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "牧场围栏内站立的棕色骏马脚下草坪过饱和偏鲜亮。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "后方白色农场建筑外墙略带杂色偏暖。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "草地草绿饱和度过高微显刺目。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "草地过翠削弱天然牧场质朴感。"}
    ],
    "review_note": "牧场围栏内站立的棕色骏马脚下草坪过饱和偏鲜亮，后方白色农场建筑外墙略带杂色(C-L1, D-L1, E1-L1, F-L1)。"
  },
  9799: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "雨中古寺院落中撑黄伞前行的三位僧侣所穿的明亮橘红色僧袍色泽偏浓郁。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "石板地面与古建墙体略显偏暗微染暖红调。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "僧袍高饱和稍显突兀。"}
    ],
    "review_note": "雨中古寺院落中撑黄伞前行的三位僧侣所穿的明亮橘红色僧袍色泽偏浓郁，石板地面略显偏暗(C-L1, D-L1, F-L1)。"
  },
  9800: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "瓷砖餐桌上摆放的美食甜点瓷盘周围蓝色花纹与白瓷砖缝隙轻微泛冷青偏色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "瓷砖台面整体微染偏冷偏青调。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "冷青色调略降甜品温暖诱人感。"}
    ],
    "review_note": "瓷砖餐桌上摆放的美食甜点瓷盘周围蓝色花纹与白瓷砖缝隙轻微泛冷青偏色(C-L1, D-L1, F-L1)。"
  },
  9801: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9804: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "1933年芝加哥世博会纪念折叠小刀象牙白刀柄上红字标识与金属刀片表面微带偏暖微黄调。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "不锈钢刀刃反光面微染暖黄杂色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "金属反光稍失银冷锐利感。"}
    ],
    "review_note": "1933年芝加哥世博会纪念折叠小刀象牙白刀柄上红字标识与金属刀片表面微带偏暖微黄调(C-L1, D-L1, F-L1)。"
  },

  # Sheet 12 (Tasks 9806, 9807, 9808, 9810, 9814, 9815)
  9806: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9807: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "黑色餐桌上白色大餐盘内盛放的土豆泥与融化奶酪酱汁边缘微显淡红杂色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "盘饰生菜边缘与餐盘高光区微染暖红偏色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "酱汁杂染微红略影响料理质感。"}
    ],
    "review_note": "黑色餐桌上白色大餐盘内盛放的土豆泥与融化奶酪酱汁边缘微显淡红杂色(C-L1, D-L1, F-L1)。"
  },
  9808: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9810: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "机场滑行跑道上达美航空客机白色机身与红蓝相间垂直尾翼涂装微显偏暗沉。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "跑道水泥路面与阴云天空微染偏灰偏冷调。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "客机白色机体略欠高光通透感。"}
    ],
    "review_note": "机场滑行跑道上达美航空客机白色机身与红蓝相间垂直尾翼涂装微显偏暗沉(C-L1, D-L1, F-L1)。"
  },
  9814: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9815: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 13 (Tasks 9819, 9820, 9821, 9822, 9823, 9826)
  9819: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9820: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "厨房料理台托盘上摆放的不锈钢水壶金属壶身与茶具表面微泛偏暖色调。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "不锈钢反光与台面瓷砖微染暖黄偏色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "金属表面略欠冰冷银光质感。"}
    ],
    "review_note": "厨房料理台托盘上摆放的不锈钢水壶金属壶身与茶具表面微泛偏暖色调(C-L1, D-L1, F-L1)。"
  },
  9821: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "远山脚下草地上吃草的原本红栗色马匹被常识性错染为苍灰白色马身。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "草地绿意略显不均偏冷灰。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "栗色马匹变白灰毛发降低牧场活力。"}
    ],
    "review_note": "远山脚下草地上吃草的原本红栗色马匹被常识性错染为苍灰白色马身，草地绿意略显不均(C-L2, D-L1, F-L1)。"
  },
  9822: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "卧室床头背景原本鲜艳大红色的乳胶漆实墙被严重颠覆性错染为暗淡土黄绿色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "全图色温严重紊乱，红墙变黄绿严重偏离基准。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "主墙恶性错色彻底破坏现代卧室装饰风格。"}
    ],
    "review_note": "卧室床头背景原本鲜艳大红色的乳胶漆实墙被严重颠覆性错染为暗淡土黄绿色伪色，全图色温严重紊乱(C-L3, D-L2, F-L3)。"
  },
  9823: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "室内过道红色立柱与后方墙壁表面显现不均匀的冷紫灰色偏色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "立柱与人物服饰微染冷紫青偏色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "过道立柱杂色降低室内空间整洁感。"}
    ],
    "review_note": "室内过道红色立柱与后方墙壁表面显现不均匀的冷紫灰色偏色(C-L1, D-L1, F-L1)。"
  },
  9826: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 14 (Tasks 9828, 9831, 9832, 9834, 9837, 9838)
  9828: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "草地上坐着的大型毛绒泰迪熊棕色绒毛与小女孩身旁秋季枯草泛冷青偏色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "草地与泰迪熊暗部微染冷青灰色调。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "暖阳质感略微受损。"}
    ],
    "review_note": "草地上坐着的大型毛绒泰迪熊棕色绒毛与小女孩身旁秋季枯草泛冷青偏色，暖阳质感略微受损(C-L1, D-L1, F-L1)。"
  },
  9831: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "电脑机房白色长条操作台上多台显示器屏幕荧光色彩偏浓艳。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "木质台面与墙面微染偏暖偏黄调。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "左侧显示器屏幕明黄高光过饱和。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "屏幕过亮反光降低操作台真实感。"}
    ],
    "review_note": "电脑机房白色长条操作台上多台显示器屏幕荧光色彩偏浓艳，左侧屏幕明黄高光过饱和(C-L1, D-L1, E1-L1, F-L1)。"
  },
  9832: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "棒球场比赛场地原本淡黄褐色的内野红土与击球区地面被彻底颠覆性错染为极其刺眼、荒诞的荧光芭比粉红伪色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "内野全域发生恶性洋红与芭比粉红偏移。"},
      {"id": "E1", "name": "过饱和", "severity": "L3", "description": "球场泥土极度刺眼高饱和荧光粉红。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "荒谬的粉红泥土彻底摧毁竞技棒球场真实感。"}
    ],
    "review_note": "棒球场比赛场地原本淡黄褐色的内野红土与击球区地面被彻底颠覆性错染为极其刺眼、荒诞的荧光芭比粉红伪色，全场发生恶性色彩错配(C-L3, D-L2, E1-L3, F-L3)。"
  },
  9834: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "室内手持游戏手柄的青年身穿的红白相间菱格针织毛衣与面部肤色微带偏暗偏暖。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "青年面部与毛衣微染暖红偏色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "暖调加深阴影层次。"}
    ],
    "review_note": "室内手持游戏手柄的青年身穿的红白相间菱格针织毛衣与面部肤色微带偏暗偏暖(C-L1, D-L1, F-L1)。"
  },
  9837: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9838: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "现代开放式厨房白色整体橱柜与大理石吧台台面整体泛轻微暖黄偏色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "厨房全景微染偏暖偏黄调。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "光影略失GT原图冷白通透质感。"}
    ],
    "review_note": "现代开放式厨房白色整体橱柜与大理石吧台台面整体泛轻微暖黄偏色，光影略失GT冷白通透质感(C-L1, D-L1, F-L1)。"
  },

  # Sheet 15 (Tasks 9840, 9841, 9842, 9843, 9844, 9845)
  9840: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "幼教玩具角木制书架上陈列的儿童绘本封面与毛绒玩偶表面微显偏暗偏暖。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "玩具角木盒与书籍暗部微染暖黄偏色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "色调稍厚微失活泼。"}
    ],
    "review_note": "幼教玩具角木制书架上陈列的儿童绘本封面与毛绒玩偶表面微显偏暗偏暖(C-L1, D-L1, F-L1)。"
  },
  9841: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "户外集市摊位白色塑料货箱与折叠货架呈现刺眼的紫红色偏色杂染。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "摊贩所穿深蓝外套与地面杂染紫红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "塑料货箱紫红杂色过饱和刺目。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "紫红杂染破坏户外市集自然光感。"}
    ],
    "review_note": "户外集市摊位白色塑料货箱与折叠货架呈现刺眼的紫红色偏色杂染，摊贩所穿深蓝外套轻度过饱和(C-L1, D-L1, E1-L2, F-L1)。"
  },
  9842: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "电脑桌老旧显示器下方张贴的复古旅行日历彩印图案大面积欠饱和严重脱色褪白。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "木质写字台面与墙面泛冷灰沉闷。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "复古日历彩绘色彩脱色发白失活。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "日历脱色降低复古海报艺术韵味。"}
    ],
    "review_note": "电脑桌老旧显示器下方张贴的复古旅行日历彩印图案大面积欠饱和严重脱色褪白，木质写字台面泛灰沉闷(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9843: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "甜品拼盘左上角小碗中盛放的原本淡粉红色草莓酸奶被错染为浅黄乳酪色。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "餐盘白色瓷碗边缘微染偏暖偏黄调。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "酸奶错色微损甜点搭配协调性。"}
    ],
    "review_note": "甜品拼盘左上角小碗中盛放的原本淡粉红色草莓酸奶被错染为浅黄乳酪色(C-L1, D-L1, F-L1)。"
  },
  9844: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9845: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "卧室内原本充满温馨暖黄光泽的实木大衣柜与书桌表面彻底欠饱和严重脱色褪变为冰冷灰水泥色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "全室光影氛围遭受颠覆性冷青与死寂水泥灰偏色破坏。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "木质大衣柜原本温暖饱满的木色彻底脱色归零。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "温馨暖居彻底褪变为阴森冰冷水泥毛坯房质感。"}
    ],
    "review_note": "卧室内原本充满温馨暖黄光泽的实木大衣柜与书桌表面彻底欠饱和严重脱色褪变为冰冷灰水泥色，全室光影氛围遭受颠覆性冷青偏色破坏(C-L3, D-L2, E2-L3, F-L3)。"
  },

  # Sheet 16 (Tasks 9846, 9848, 9849, 9850, 9852, 9853)
  9846: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "手中包裹白色餐巾纸的烘焙卷饼焦黄外皮与内部融化奶酪馅料微带偏暖微黄调。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "卷饼与手指肤色微染偏暖偏橙调。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "微暖色调略显沉重。"}
    ],
    "review_note": "手中包裹白色餐巾纸的烘焙卷饼焦黄外皮与内部融化奶酪馅料微带偏暖微黄调(C-L1, D-L1, F-L1)。"
  },
  9848: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "酒店双床客房床头壁灯烘托下，实木床头板、床尾装饰织毯与白色羽绒被面过饱和泛浓郁红橙色调。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "室内照明整体偏暖红橙调。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "床头暖光泛浓郁红橙过饱和。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "过分浓郁暖光降低客房素净感。"}
    ],
    "review_note": "酒店双床客房床头壁灯烘托下，实木床头板、床尾装饰织毯与白色羽绒被面过饱和泛浓郁红橙色调(C-L1, D-L1, E1-L1, F-L1)。"
  },
  9849: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9850: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9852: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "暮色海滨手持风筝的青年背后原本深邃澄澈的深蓝色黄昏天空被颠覆性错染为极其反常的浑浊红褐色与粉红暮霭伪色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "天空与海水发生严重暖红褐色相错位。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "浑浊红褐天空高光区过饱和刺目。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "黄昏深蓝天空变浑浊红褐色彻底摧毁海滨暮色意境。"}
    ],
    "review_note": "暮色海滨手持风筝的青年背后原本深邃澄澈的深蓝色黄昏天空被颠覆性错染为极其反常的浑浊红褐色与粉红暮霭伪色，全图色相严重错位(C-L3, D-L2, E1-L2, F-L3)。"
  },
  9853: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "冬季萧瑟密林树干间隐约伫立的两匹马匹与林下枯枝落叶地面色彩略显暗沉泛灰。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "树林深处暗部微染冷灰偏色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "林间光影层次稍欠明澈。"}
    ],
    "review_note": "冬季萧瑟密林树干间隐约伫立的两匹马匹与林下枯枝落叶地面色彩略显暗沉泛灰(C-L1, D-L1, F-L1)。"
  },

  # Sheet 17 (Tasks 9854, 9855, 9857, 9858, 9859, 9861)
  9854: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "浅海浪花边策马缓行的人群与马匹剪影微显偏暗，海浪白沫与沙滩色泽平淡。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "海面浪花与浅水区微染冷灰偏色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "海滨水天交界处略显扁平。"}
    ],
    "review_note": "浅海浪花边策马缓行的人群与马匹剪影微显偏暗，海浪白沫与沙滩色泽平淡(C-L1, D-L1, F-L1)。"
  },
  9855: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "料理台烤箱旁刚出炉的意式披萨表面奶酪烘烤金黄色泽偏暗沉欠饱和。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "深色油醋瓶与酒瓶边缘微带冷调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "刚出炉披萨焦黄色泽轻度欠饱和。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "烘焙披萨金黄感不足略降美味可口度。"}
    ],
    "review_note": "料理台烤箱旁刚出炉的意式披萨表面奶酪烘烤金黄色泽偏暗沉欠饱和，深色油醋瓶与酒瓶边缘微带冷调(C-L1, D-L1, E2-L1, F-L1)。"
  },
  9857: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "滑雪场雪地上年长滑雪者佩戴的亮橙色领带与后方选手鲜红滑雪服大面积欠饱和脱色泛粉白。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "皑皑雪原与针叶松林背景略显灰暗偏冷。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "亮橙领带与红滑雪服严重脱色变暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "标志性运动服饰脱色发灰削弱生机。"}
    ],
    "review_note": "滑雪场雪地上年长滑雪者佩戴的亮橙色领带与后方选手鲜红滑雪服大面积欠饱和脱色泛粉白，皑皑雪原略显灰暗(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9858: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9859: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "室内门廊门洞透视出的洗手间白色面盆与木质门框在灯光下微带偏暖微黄调。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "门廊瓷砖与门框暗部微染暖黄偏色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "暖调加深室内阴影。"}
    ],
    "review_note": "室内门廊门洞透视出的洗手间白色面盆与木质门框在灯光下微带偏暖微黄调(C-L1, D-L1, F-L1)。"
  },
  9861: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 18 (Tasks 9862, 9863, 9865, 9866, 9867, 9868)
  9862: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "水果摊位上方悬挂的成熟香蕉串明黄果皮过于浓艳过饱和。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "下方彩色格子花纹台布泛荧光偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "大挂香蕉明黄荧光感过强。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "过饱和黄色削弱成熟水果天然质感。"}
    ],
    "review_note": "水果摊位上方悬挂的成熟香蕉串明黄果皮过于浓艳过饱和，下方彩色格子花纹台布泛荧光偏色(C-L1, D-L1, E1-L2, F-L1)。"
  },
  9863: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "欧洲老街历史建筑药房外立面与上空原本清澈浅蓝的天空大面积欠饱和严重脱色褪变为死寂冷灰。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "街景建筑石砖墙面整体泛冷灰暗沉。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "浅蓝天空与红砖外墙大面积欠饱和褪色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "天空失色令欧洲老街显得压抑沉闷。"}
    ],
    "review_note": "欧洲老街历史建筑药房外立面与上空原本清澈浅蓝的天空大面积欠饱和严重脱色褪变为死寂冷灰(C-L1, D-L1, E2-L2, F-L1)。"
  },
  9865: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "洗手间圆形防雾镜周边原本温暖明黄色的隐藏环形灯带被颠覆性错染为刺眼的紫红霓虹伪色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "圆形镜框与墙壁严重泛紫红霓虹偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "紫红霓虹光带过于刺目浓烈。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "暖黄灯带变紫红霓虹彻底违背高级卫浴设计常理。"}
    ],
    "review_note": "洗手间圆形防雾镜周边原本温暖明黄色的隐藏环形灯带被颠覆性错染为刺眼的紫红霓虹伪色(C-L3, D-L2, E1-L2, F-L2)。"
  },
  9866: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "客厅台灯与吊灯照射下，左侧乳胶漆墙面与电视机背景墙呈现不自然的紫红色偏色杂染。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "墙体高光区微染紫红偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L1", "description": "紫红杂染略显饱和。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "背景墙杂色降低居家光影纯度。"}
    ],
    "review_note": "客厅台灯与吊灯照射下，左侧乳胶漆墙面与电视机背景墙呈现不自然的紫红色偏色杂染(C-L1, D-L1, E1-L1, F-L1)。"
  },
  9867: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9868: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "独立卫浴淋浴房原本泛着温馨暖黄光泽的米黄色瓷砖墙面与地面彻底欠饱和严重脱色褪变为冰冷灰白色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "全室卫浴设施与玻璃门框浸染死寂冰冷冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "米黄瓷砖原本温暖舒适的色彩完全脱色归零。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "温馨暖黄卫浴褪变为冰冷灰白毛坯感。"}
    ],
    "review_note": "独立卫浴淋浴房原本泛着温馨暖黄光泽的米黄色瓷砖墙面与地面彻底欠饱和严重脱色褪变为冰冷灰白色，全室暖意完全丧失(C-L2, D-L2, E2-L3, F-L2)。"
  },

  # Sheet 19 (Tasks 9869, 9870, 9871, 9873, 9874, 9878)
  9869: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "客机舷窗俯瞰云海场景原本清亮蔚蓝的天空大面积欠饱和严重脱色褪变为单调灰白，喷气发动机进气道前缘红色涂漆严重褪色变暗。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "云层与天空整体泛冷灰沉闷。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "高空湛蓝晴空与引擎红漆欠饱和严重脱色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "万米高空晴空失色削弱航拍纯净感。"}
    ],
    "review_note": "客机舷窗俯瞰云海场景原本清亮蔚蓝的天空大面积欠饱和严重脱色褪变为单调灰白，喷气发动机进气道前缘红色涂漆严重褪色变暗(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9870: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "会议室内与会人员面前摆放笔记本电脑的原本温暖金黄色长条实木会议桌表面严重欠饱和脱色泛灰沉闷。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "会议室桌面与墙壁微染冷灰偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "实木会议桌暖木光泽严重脱色发暗。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "桌面泛灰降低商务办公场景生动性。"}
    ],
    "review_note": "会议室内与会人员面前摆放笔记本电脑的原本温暖金黄色长条实木会议桌表面严重欠饱和脱色泛灰沉闷(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9871: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9873: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L1", "description": "热带村落茅草屋顶简易木棚周围茂密椰子树树冠与草地微显偏暗沉。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "椰树阴影与茅草屋檐微染偏冷偏暗调。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "热带阳光透亮感轻微受损。"}
    ],
    "review_note": "热带村落茅草屋顶简易木棚周围茂密椰子树树冠与草地微显偏暗沉(C-L1, D-L1, F-L1)。"
  },
  9874: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9878: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },

  # Sheet 20 (Tasks 9880, 9881, 9882, 9883, 9885, 9887)
  9880: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "摆满精装图书的红色实木书架中央格放置的毛绒泰迪熊玩具被严重错染为灰紫色，实木书架红漆偏暗。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "泰迪熊绒毛与书册侧脊泛灰紫偏色。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "玩偶泛紫降低书房陈列温馨度。"}
    ],
    "review_note": "摆满精装图书的红色实木书架中央格放置的毛绒泰迪熊玩具被严重错染为灰紫色，实木书架红漆偏暗(C-L2, D-L1, F-L1)。"
  },
  9881: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9882: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "梳妆镜前自拍女士身穿的原本鲜艳大红色抓绒连帽卫衣彻底欠饱和严重脱色褪变为冰冷灰绿色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "红卫衣与镜中背景大面积浸染死灰冷青偏色。"},
      {"id": "E2", "name": "欠饱和", "severity": "L3", "description": "大红色抓绒卫衣鲜艳纯色彻底脱色消失。"},
      {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "鲜红卫衣褪变为灰绿死色严重失真。"}
    ],
    "review_note": "梳妆镜前自拍女士身穿的原本鲜艳大红色抓绒连帽卫衣彻底欠饱和严重脱色褪变为冰冷灰绿色，红色染料完全丧失(C-L3, D-L2, E2-L3, F-L2)。"
  },
  9883: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L2", "description": "烘焙工坊玻璃展示圆罩内摆放的曲奇饼干与面包表面原本金黄焦脆烘烤色泽严重欠饱和脱色变灰。"},
      {"id": "D", "name": "偏色", "severity": "L1", "description": "全店暖光氛围偏冷，玻璃展示罩泛冷灰调。"},
      {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "糕点烘焙金黄色泽大面积脱色发白。"},
      {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "曲奇饼干脱色发灰严重削弱食欲感。"}
    ],
    "review_note": "烘焙工坊玻璃展示圆罩内摆放的曲奇饼干与面包表面原本金黄焦脆烘烤色泽严重欠饱和脱色变灰，全店暖光氛围偏冷(C-L2, D-L1, E2-L2, F-L1)。"
  },
  9885: {
    "action": "pass",
    "defects": [],
    "review_note": "审查通过"
  },
  9887: {
    "action": "revise",
    "defects": [
      {"id": "C", "name": "错色", "severity": "L3", "description": "动物园长颈鹿脚下原本翠绿青葱的草坪与后方繁茂树冠被荒诞颠覆性错染为大面积刺眼焦红褐色与铁锈红杂色伪色。"},
      {"id": "D", "name": "偏色", "severity": "L2", "description": "草坪与植物发生颠覆性铁锈红与焦褐色偏色。"},
      {"id": "E1", "name": "过饱和", "severity": "L2", "description": "红褐伪色草地过饱和刺目。"},
      {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "青青草原变焦红荒漠彻底违背生态自然常理。"}
    ],
    "review_note": "动物园长颈鹿脚下原本翠绿青葱的草坪与后方繁茂树冠被荒诞颠覆性错染为大面积刺眼焦红褐色与铁锈红杂色伪色，全场生态色彩彻底错配(C-L3, D-L2, E1-L2, F-L3)。"
  }
}

def apply_batch_49():
    grounding_path = "LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_49.json"
    with open(grounding_path, 'w', encoding='utf-8') as f:
        json.dump(BATCH_49_REVIEWS, f, indent=2, ensure_ascii=False)
    print(f"Saved grounding reviews to {os.path.abspath(grounding_path)}")

    # Update both exports
    for target in ['reviewed_1_10000_all.json', 'reviewed_1_10000_clean.json']:
        export_path = os.path.join('LS_lcad_reviewer/exports', target)
        if not os.path.exists(export_path):
            print(f"File not found: {export_path}")
            continue

        with open(export_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        is_clean = 'clean' in target
        updated_count = 0
        pass_count = 0
        revised_count = 0
        meltdown_count = 0

        # Mapping annotations by task_id in human_review
        for ann in data['annotations']:
            hr = ann.get('human_review', {})
            t_id = hr.get('task_id')
            if t_id in BATCH_49_REVIEWS:
                rev = BATCH_49_REVIEWS[t_id]
                updated_count += 1
                
                if rev['action'] == 'pass':
                    pass_count += 1
                    ann['defects'] = []
                    ann['review_status'] = "已核验"
                    ann['review_note'] = "" if is_clean else "审查通过"
                    ann['reviewed_score'] = None
                    ann['needs_rescoring'] = True
                elif rev['action'] == 'meltdown_a':
                    meltdown_count += 1
                    ann['defects'] = rev['defects']
                    ann['review_status'] = "已核验"
                    ann['review_note'] = "" if is_clean else rev['review_note']
                    ann['reviewed_score'] = 1.0
                    ann['needs_rescoring'] = False
                else: # revise
                    revised_count += 1
                    ann['defects'] = rev['defects']
                    ann['review_status'] = "已核验"
                    ann['review_note'] = "" if is_clean else rev['review_note']
                    ann['reviewed_score'] = None
                    ann['needs_rescoring'] = True

        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Updated {target}: {updated_count} tasks matched (Pass: {pass_count}, Revise: {revised_count}, Meltdown A: {meltdown_count})")

    print(f"Batch 49 applied successfully!")
    print(f"Total: {len(BATCH_49_REVIEWS)}, Passes: {sum(1 for r in BATCH_49_REVIEWS.values() if r['action'] == 'pass')} ({sum(1 for r in BATCH_49_REVIEWS.values() if r['action'] == 'pass')/len(BATCH_49_REVIEWS):.2%}), Revised: {sum(1 for r in BATCH_49_REVIEWS.values() if r['action'] == 'revise')} ({sum(1 for r in BATCH_49_REVIEWS.values() if r['action'] == 'revise')/len(BATCH_49_REVIEWS):.2%}), Meltdown A: {sum(1 for r in BATCH_49_REVIEWS.values() if r['action'] == 'meltdown_a')}")

if __name__ == '__main__':
    apply_batch_49()
