# -*- coding: utf-8 -*-
"""
apply_remaining_batch_20.py - Apply Batch 20 (Tasks #4340 ~ #4514) Reviews
"""

import json
import os
import re

BATCH_NO = 20
GROUNDING_FILE = "LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_20.json"
ALL_FILE = "LS_lcad_reviewer/exports/reviewed_1_10000_all.json"
CLEAN_FILE = "LS_lcad_reviewer/exports/reviewed_1_10000_clean.json"

BANNED_WORDS = [
    "局部关键区域", "关键主体或背景", "轮廓边缘处", "局部细节", "重要区域", "某些区域", "局部画面",
    "画面关键区域", "边缘区域", "主体部分", "背景区域", "关键物体", "部分区域"
]

def make_pass_review(task_id):
    return {
        "status": "PASS",
        "defects": [],
        "note": "审查通过"
    }

def make_revision_review(task_id, defects, note):
    return {
        "status": "REVISION",
        "defects": defects,
        "note": note
    }

REVIEWS = {
    # Sheet 01
    4340: make_pass_review(4340),
    4342: make_revision_review(4342, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "厨房操作台瓷砖表面与白面粉粉刷背景明显偏冷灰白，丧失GT烘焙操作间的温馨暖黄光照环境。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "木质披萨铲上的披萨饼鲜红番茄粒与红酱点缀错涂为暗沉发污的灰褐色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "新鲜绿叶蔬菜碎与罗勒叶略显发灰暗淡，饱和度偏低。"}
    ], "厨房操作台瓷砖表面与白面粉粉刷背景明显偏冷灰白，披萨饼鲜红番茄粒与红酱点缀错涂为暗沉灰褐色(D-L2, C-L2, E2-L1)"),
    4343: make_revision_review(4343, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "荒山陡坡岩石表面与枯草全域偏异常明黄色调，缺乏GT山岩的自然砂石灰褐色。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "两只野生大角羊（盘羊）背部浅褐灰色被毛错涂并混入暗黄绿杂色。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "山体向阳面高光区域略显泛黄过曝，视觉可信度轻微受损。"}
    ], "荒山陡坡岩石表面与枯草全域偏异常明黄色调，大角羊背部被毛错涂并混入暗黄绿杂色(D-L2, C-L2, F-L1)"),
    4344: make_revision_review(4344, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "室内实木书架与镜面反射区域整体色温严重偏冷暗黄绿，丧失GT室内温馨纯正的红木琥珀暖光。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "书架上排列的彩色书籍书脊错涂为暗淡灰黑色，色彩饱和度明显流失。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "灰猫被毛与眼眸金黄色泽略显干瘪暗淡，欠饱和。"}
    ], "室内实木书架与镜面反射区域整体色温严重偏冷暗黄绿，书架书籍书脊错涂为暗淡灰黑色(D-L2, C-L2, E2-L1)"),
    4345: make_revision_review(4345, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "逆光街景中的路面、建筑立面与天空逆光区域严重偏冷灰绿，彻底丢失GT夕阳斜射的温暖金黄漫射光感。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "行人深色服饰、自行车车身与商铺招牌严重发暗发灰脱色，呈现明显的欠饱和灰度感。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "画面左上方逆光光晕边缘生硬发白，自然度欠佳。"}
    ], "逆光街景中的路面、建筑立面与天空逆光区域严重偏冷灰绿，行人服饰与自行车严重发灰脱色(D-L2, E2-L2, F-L1)"),
    4346: make_pass_review(4346),

    # Sheet 02
    4348: make_revision_review(4348, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "街角建筑外墙下部原本的淡青蓝多彩涂鸦艺术墙面被大面积严重错涂为刺眼的荧光草绿色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "建筑上部红砖结构立面全域偏冷暗青蓝灰，彻底失去真实砖红色泽。"},
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "底部翠绿涂鸦色调过于浓艳刺眼，高光严重溢出。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "墙面与消防栓周边人工伪色明显，视觉自然度极差。"}
    ], "建筑外墙下部淡青蓝涂鸦艺术墙面大面积严重错涂为荧光草绿色，上部红砖立面偏冷暗青蓝灰(C-L3, D-L2, E1-L2, F-L2)"),
    4349: make_pass_review(4349),
    4352: make_revision_review(4352, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "室内墙面与相框展示区全域偏冷青蓝调，丧失GT居室暖黄温馨的氛围光照。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "摆放在木架上的陶瓷花盆盆身暖红光照被错涂为冰冷浅灰白色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "绿植叶片与泥土欠缺生机，整体明度发暗且饱和度略低。"}
    ], "室内墙面与相框展示区全域偏冷青蓝调，陶瓷花盆暖红光照错涂为冰冷浅灰白(D-L2, C-L2, E2-L1)"),
    4354: make_revision_review(4354, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "荒漠风蚀岩石地貌与洞穴峭壁全域偏暗灰黄褐，丧失GT砂岩天然红褐暖色调。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "探险人员身穿的深蓝色户外冲锋衣被错涂为发暗青灰黑色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "男子白色防晒遮阳帽与面部受光面色彩欠饱和发暗。"}
    ], "荒漠风蚀岩石地貌与峭壁全域偏暗灰黄褐，探险男子深蓝色冲锋衣错涂为发暗青灰黑(D-L2, C-L2, E2-L1)"),
    4355: make_revision_review(4355, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "农场双轮马车金黄色辐条木质大轮圈局部错涂并混入发暗紫色杂斑。"},
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "马车红漆后挡板与侧板红漆过度浓艳刺眼，呈现荧光品红倾向。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "轮辐与砖墙交接处存在轻度伪色杂质，影响视觉自然度。"}
    ], "双轮马车金黄木质轮圈错涂并混入发暗紫色杂斑，红漆车身过度浓艳呈荧光品红(C-L2, E1-L2, F-L1)"),
    4357: make_revision_review(4357, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "街头巡逻骑警骑乘的高大骏马栗褐色毛皮被严重错涂为发暗的紫红色调，完全违背生物真实常理。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "城市马路地面与背景白色建筑立面整体偏冷暗青灰。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "马身反光与鞍座边缘呈现不自然的人工紫斑，视觉真实感极差。"}
    ], "骑警骑乘的栗褐色骏马毛皮被严重错涂为发暗紫红色调，背景路面偏冷暗青灰(C-L3, D-L2, F-L2)"),

    # Sheet 03
    4358: make_revision_review(4358, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "办公室内桌面、笔记本外壳与采光区域整体严重偏冷青绿调，丧失GT窗边阳光洒入的自然温润感。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "人体工学座椅暖色扶手与深色衣物略显发暗褪色，缺乏生动光泽。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "窗边大面积高光过度泛白，视觉自然度略微欠佳。"}
    ], "办公桌面、笔记本外壳与采光区域整体严重偏冷青绿调，座椅扶手与衣物略显发暗褪色(D-L2, E2-L1, F-L1)"),
    4359: make_revision_review(4359, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "墙壁悬挂的两幅装饰画金色实木画框被错涂为暗沉发暗的灰褐色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "客厅粉刷壁纸墙面整体偏冷暗浅灰白，彻底脱失GT典雅温馨的暖米黄色泽。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "白色陶瓷花瓶反光与台面饰品轻度欠饱和发灰。"}
    ], "悬挂装饰画金色实木画框错涂为暗沉灰褐，客厅壁纸墙面整体偏冷暗浅灰白(C-L2, D-L2, E2-L1)"),
    4360: make_revision_review(4360, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "桌面书籍《Bill Bryson Shakespeare》书脊与封面的经典正红色块错涂为暗沉紫红偏褐。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "右上角深色背包与外套织物表面略偏冷紫暗调。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "书籍白色封面上的英文印刷标题与书页侧边轻微发灰欠饱和。"}
    ], "书籍《Bill Bryson Shakespeare》书脊正红色块错涂为暗沉紫红偏褐，背包略偏冷紫暗调(C-L2, D-L1, E2-L1)"),
    4361: make_revision_review(4361, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "摆放蛋糕的桌面明亮温暖的金黄色衬底被彻底错涂为冰冷浅灰白色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "巧克力蛋糕切面与红白包装礼盒整体环境光严重偏冷暗青灰。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "顶层雪白奶油与红色包装盒丝带色泽暗淡，欠缺明亮活力。"}
    ], "摆放蛋糕桌面金黄色衬底彻底错涂为冰冷浅灰白，巧克力蛋糕切面偏冷暗青灰(C-L3, D-L2, E2-L1)"),
    4362: make_revision_review(4362, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "餐盘中原本鲜嫩诱人的橙红三文鱼刺身生鱼片与烤肉块被严重错涂为发暗青白泛紫，呈现变质色相。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "白色餐盘、配菜炒面与红色餐垫全域严重偏冷青蓝调，丧失GT诱人的熟食色泽。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "刺身表面泛起诡异冷青色高光斑块，视觉自然度极差。"}
    ], "餐盘中橙红三文鱼刺身与烤肉块严重错涂为发暗青白泛紫，餐盘与餐垫严重偏冷青蓝(C-L3, D-L2, F-L2)"),
    4363: make_revision_review(4363, [
        {"id": "D", "name": "偏色", "severity": "L1", "description": "水泥地面与金属工业管道表面阴影偏冷紫暗调。"},
        {"id": "B", "name": "溢色", "severity": "L1", "description": "粉红色毛绒公仔头部粉红边缘向金属立柱接缝处产生轻微溢色晕染。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "毛绒玩偶浅粉红衣裳与耳廓细节局部暗淡发灰，欠饱和。"}
    ], "水泥地面与金属管道阴影偏冷紫暗调，粉红毛绒公仔边缘向金属立柱轻微溢色(D-L1, B-L1, E2-L1)"),

    # Sheet 04
    4364: make_revision_review(4364, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "运动员面部与手臂肌肤色温严重偏冷苍白泛暗紫，丧失GT健美红润的古铜色肤质感。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "背景看台深蓝色塑料座椅局部错涂并泛起杂乱紫黑色斑块。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "大红色无袖运动背心下摆与边缘光泽欠饱和发暗。"}
    ], "运动员面部与手臂肌肤偏冷苍白泛暗紫，背景看台深蓝座椅错涂并混入紫黑色斑(D-L2, C-L2, E2-L1)"),
    4365: make_revision_review(4365, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "等候大厅一整排原本深墨绿色的塑料连排座椅被荒唐错涂为暗沉芥末土黄色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "墙壁、天花板与挂钟受光面偏冷暗黄绿杂色，丧失室内干净整洁的漫射光。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "座椅大面积错色导致整体画面视觉可信度严重失真。"}
    ], "等候大厅深墨绿塑料连排座椅荒唐错涂为暗沉芥末土黄，墙壁受光面偏暗黄绿杂色(C-L3, D-L2, F-L2)"),
    4368: make_revision_review(4368, [
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "棒球击球手与捕手的深蓝头盔与球衣过度浓艳刺眼，呈现荧光高饱和宝蓝色。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "外野翠绿草坪条纹高光区域错涂为偏荧光的嫩黄绿色。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "人物护具与草坪交界处色彩过渡生硬，略显刺眼。"}
    ], "棒球选手深蓝头盔与球衣过度浓艳呈荧光宝蓝，外野草坪条纹错涂为荧光嫩黄绿(E1-L2, C-L2, F-L1)"),
    4371: make_revision_review(4371, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "两位女士面部与手臂皮肤全域偏冷紫暗红，呈现严重的晒伤样假色与斑驳感。"},
        {"id": "B", "name": "溢色", "severity": "L1", "description": "宝蓝色短袖上衣领口边缘向颈部肤色区域发生轻微溢色晕染。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "阳光下翠绿草坪局部明度发暗，欠饱和。"}
    ], "女士面部与手臂皮肤偏冷紫暗红呈严重假色晒伤感，宝蓝上衣边缘向颈部轻微溢色(D-L2, B-L1, E2-L1)"),
    4372: make_pass_review(4372),
    4375: make_revision_review(4375, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "白瓷餐盘中烘烤披萨原本焦香金黄的面饼边缘与芝士被彻底错涂为冰冷浅青灰白，毫无烘焙熟食质感。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "白色餐盘、餐桌台面与上方食客手臂肤色全域偏冷暗青灰。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "芝士表面泛起冷青色反光伪色，视觉自然度极差。"}
    ], "烘烤披萨焦香金黄面饼边缘与芝士彻底错涂为冰冷浅青灰白，餐桌与食客手臂偏冷暗青灰(C-L3, D-L2, F-L2)"),

    # Sheet 05
    4376: make_pass_review(4376),
    4377: make_revision_review(4377, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "汹涌巨浪掀起的碧绿清澈海水管涌大面积错涂为浑浊暗淡的黄褐橄榄色。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "白色浪花泡沫受光面略偏暗暖黄。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "冲浪手黑色保暖胶衣与白色冲浪板欠缺明暗对比，略发灰暗。"}
    ], "巨浪管涌碧绿清澈海水大面积错涂为浑浊黄褐橄榄色，白色浪花略偏暗暖黄(C-L2, D-L1, E2-L1)"),
    4378: make_pass_review(4378),
    4379: make_revision_review(4379, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "餐桌台面、白色瓷盘与刀叉高光区域偏冷暗青灰，丧失GT餐馆温馨暖黄灯光。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "烘焙披萨金黄芝士与边缘焦斑错涂为发暗黄褐杂色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "侧面小盘新鲜蔬菜沙拉生菜叶片发暗泛灰，欠饱和。"}
    ], "餐桌台面与白色瓷盘偏冷暗青灰，披萨金黄芝士与边缘焦斑错涂为发暗黄褐(D-L2, C-L2, E2-L1)"),
    4382: make_revision_review(4382, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "办公书桌、背景木门与粉刷墙壁整体严重偏冷灰紫调，丧失GT室内木质天然红褐暖意。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "桌面散乱报纸与资料旁摆放的蓝色织物错涂为发暗青灰黑色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "各种文件纸张与打印纸发灰暗淡，欠缺明快层次感。"}
    ], "书桌、背景木门与粉刷墙壁严重偏冷灰紫调，散乱报纸旁蓝色织物错涂为发暗青灰黑(D-L2, C-L2, E2-L1)"),
    4383: make_pass_review(4383),

    # Sheet 06
    4385: make_revision_review(4385, [
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "奔腾骏马栗色毛皮与马颈受光面过度浓艳刺眼，呈现火红橙色高饱和度倾向。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "背景树冠叶片与草地整体色调微偏荧光黄绿。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "马身肌肉反光处高光溢出轻微失真。"}
    ], "骏马栗色毛皮与马颈受光面过度浓艳呈火红橙色，背景树林微偏荧光黄绿(E1-L2, D-L1, F-L1)"),
    4387: make_pass_review(4387),
    4388: make_revision_review(4388, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "城市十字路口黄昏时分深邃纯净的宝蓝青蓝夜空被彻底错涂为发暗阴沉的灰白色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "道路沥青路面、路灯与车辆车流全域偏冷暗青灰，丧失GT暮色苍穹下的环境反光。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "远处城市天际线建筑轮廓与路灯光芒严重脱色泛灰，欠饱和。"}
    ], "十字路口黄昏深邃宝蓝夜空彻底错涂为发暗阴沉灰白色，路面与车辆偏冷暗青灰(C-L3, D-L2, E2-L2)"),
    4389: make_revision_review(4389, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "摆在洗手台上的男士除臭剂（Speed Stick）鲜艳宝蓝瓶身与标识错涂为发暗墨蓝紫色。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "左侧多功能护理液瓶身上醒目的红色印刷文字错涂为暗沉发灰的暗红褐色。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "洗手台背景瓷砖与粉刷墙面略偏冷暗浅灰白。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "彩色牙刷刷柄饰条与剃须刀按钮色泽轻微欠饱和。"}
    ], "男士除臭剂宝蓝瓶身错涂为发暗墨蓝紫，护理液红色印刷文字错涂为暗红褐(C-L2, C-L2, D-L1, E2-L1)"),
    4390: make_revision_review(4390, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "玻璃茶几玻璃瓶中插放的明黄色鲜花花瓣错涂为暗沉发污的灰黄绿色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "客厅米白色布艺沙发、地板与玻璃桌面整体偏冷暗青灰调。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "花束中粉红玫瑰与嫩绿枝叶略显发暗脱色，饱和度偏低。"}
    ], "玻璃花瓶中明黄色鲜花错涂为发暗灰黄绿，布艺沙发与地板偏冷暗青灰(C-L2, D-L2, E2-L1)"),
    4394: make_revision_review(4394, [
        {"id": "D", "name": "偏色", "severity": "L1", "description": "餐桌台面、餐巾纸与披萨烤盘边缘阴影轻度偏冷暗紫褐调。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "烘烤玛格丽特披萨表面的鲜红番茄酱汁与金色芝士焦边饱和度略低发暗。"}
    ], "餐桌台面与餐巾纸阴影轻度偏冷暗紫褐，玛格丽特披萨番茄酱与芝士略显欠饱和发暗(D-L1, E2-L1)"),

    # Sheet 07
    4395: make_pass_review(4395),
    4397: make_revision_review(4397, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "餐桌上切块草莓蛋糕的粉嫩草莓奶油糖霜错涂为暗沉发污的灰褐橙色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "餐厅背景木质酒架、相框与女孩面部肤色全域偏冷暗青灰，丧失室内温馨暖光。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "蛋糕侧边海绵蛋糕体与奶油层色彩欠饱和发暗。"}
    ], "切块草莓蛋糕粉嫩奶油糖霜错涂为暗沉灰褐橙色，餐厅木质酒架与女孩肤色偏冷暗青灰(C-L2, D-L2, E2-L1)"),
    4398: make_revision_review(4398, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "酒店客房床头背景墙与两侧台灯暖黄投射光照严重偏俗艳的冷粉红洋紫调，完全失真。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "白色大床上的深酒红色靠垫与紫色抱枕错涂为暗沉紫灰色。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "床头台灯周围光晕色彩生硬失真，整体视觉自然度明显劣化。"}
    ], "床头背景墙与台灯暖黄投射光照严重偏俗艳冷粉红洋紫，酒红靠垫错涂为暗沉紫灰(D-L2, C-L2, F-L2)"),
    4400: make_revision_review(4400, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "男子身穿的鲜艳大红色针织毛衣错涂为暗沉发闷的深紫暗红色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "室内门框、走廊粉刷墙面与金属剪刀反光整体严重偏冷灰青蓝调。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "男子面部与张开的大嘴内部呈现杂乱不自然的暗紫伪色色斑。"}
    ], "男子大红色针织毛衣错涂为暗沉深紫暗红，门框与粉刷墙面严重偏冷灰青蓝(C-L2, D-L2, F-L2)"),
    4403: make_revision_review(4403, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "苍鹭栖息的户外灌木丛与青翠草坪被大面积严重错涂为暗沉枯黄橄榄色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "苍鹭羽毛、长颈与背景光照全域偏暗灰褐，丧失自然生机。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "湿地草场绿植严重发暗发灰脱色，呈现明显的欠饱和衰败感。"}
    ], "户外灌木丛与青翠草坪大面积严重错涂为暗沉枯黄橄榄色，苍鹭体表偏暗灰褐发灰(C-L3, D-L2, E2-L2)"),
    4404: make_revision_review(4404, [
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "果蔬摊位陈列的红辣椒与番茄果皮过度浓艳刺眼，呈现荧光品红高光溢出。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "前方货架上的金黄柠檬与柑橘错涂为偏冷荧光亮黄绿。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "果蔬箱交界处存在细微色光溢出杂质，视觉自然度略微受损。"}
    ], "果蔬摊红辣椒与番茄果皮过度浓艳呈荧光品红，金黄柠檬与柑橘错涂为荧光亮黄绿(E1-L2, C-L2, F-L1)"),

    # Sheet 08
    4405: make_pass_review(4405),
    4406: make_pass_review(4406),
    4407: make_revision_review(4407, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "室内聚会暗光下年轻男子的面部与颈部肤色严重偏冷暗青黄调，呈现不健康的病态面色。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "男子身穿的酒红色翻领衬衫错涂为暗沉发闷的深褐红色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "男子手中的玻璃水杯高光与背景彩灯色彩发暗欠饱和。"}
    ], "男子面部肤色严重偏冷暗青黄调呈病态面色，酒红色翻领衬衫错涂为暗沉深褐红(D-L2, C-L2, E2-L1)"),
    4408: make_revision_review(4408, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "城市路口上空原本明亮淡暖黄白色的日光云天被彻底错涂为冰冷浓重的青绿天蓝色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "街景道路沥青路面、金属护栏与背景米黄建筑外墙全域偏冷暗青灰。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "天空异常青蓝伪色与地面色温剧烈冲突，视觉真实感极差。"}
    ], "日光云天彻底错涂为冰冷浓重青绿天蓝色，道路路面与米黄建筑外墙偏冷暗青灰(C-L3, D-L2, F-L2)"),
    4409: make_pass_review(4409),
    4411: make_pass_review(4411),

    # Sheet 09
    4412: make_revision_review(4412, [
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "街角药房上方咖啡馆霓虹招牌与文字过度浓艳刺眼，呈现荧光高饱和紫红色。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "德国药房标志性的正红色“A”字形招牌边缘错涂并溢出洋红杂色。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "地铁站蓝色指示牌与金属立柱整体色调微偏冷紫暗调。"}
    ], "咖啡馆霓虹招牌与文字过度浓艳呈荧光紫红，药房正红色“A”字招牌错涂并混入洋红(E1-L2, C-L2, D-L1)"),
    4413: make_revision_review(4413, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "排练室原本温暖明亮的米黄色粉刷背景墙面被彻底错涂为冰冷浅灰白色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "男女舞者面部与手臂皮肤全域偏冷苍白泛暗蓝，呈现严重的失血冷灰感。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "黑色舞蹈服饰与背景木质镜框严重脱色发灰，欠饱和。"}
    ], "排练室米黄色粉刷背景墙彻底错涂为冰冷浅灰白，男女舞者皮肤偏冷苍白泛暗蓝(C-L3, D-L2, E2-L2)"),
    4414: make_revision_review(4414, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "盛放披萨纸盒周边的暖橙黄色木质餐桌台面被彻底错涂为冰冷浅灰白色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "烘焙披萨金黄芝士、面饼边缘与硬纸板外壳全域偏冷暗青灰。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "披萨表面芝士油光泛起冷青色伪色高光，视觉诱人性严重失真。"}
    ], "盛放披萨纸盒暖橙黄木质餐桌彻底错涂为冰冷浅灰白，烘焙披萨芝士偏冷暗青灰(C-L3, D-L2, F-L2)"),
    4415: make_pass_review(4415),
    4418: make_revision_review(4418, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "男子面部五官与双手阴影严重偏冷暗紫黑杂色，丧失阳光下的自然血色。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "青年双手捧着的半透明明黄色塑料飞盘中心错涂并混入发暗绿黄色斑块。"},
        {"id": "E1", "name": "过饱和", "severity": "L1", "description": "亮黄色连帽卫衣受光面局部过于浓艳，暗部对比过硬。"}
    ], "男子面部五官与双手阴影严重偏冷暗紫黑，明黄色塑料飞盘中心错涂发暗绿黄斑(D-L2, C-L2, E1-L1)"),
    4420: make_pass_review(4420),

    # Sheet 10
    4421: make_revision_review(4421, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "铁道沙盘模型中粉白相间条纹货运车厢错涂为发暗灰紫暗色。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "铁轨前方明黄色微缩工程推土机模型错涂为暗淡土灰黄色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "各节列车模型车身彩绘涂装整体严重发灰脱色，欠饱和。"}
    ], "铁道沙盘模型粉白条纹车厢错涂为发暗灰紫，明黄工程推土机模型错涂为暗淡土灰黄(C-L2, C-L2, E2-L2)"),
    4422: make_revision_review(4422, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "铁路两旁多层红砖居民建筑外墙偏暗紫褐灰，丧失GT红砖天然温润的陶土暖红。"},
        {"id": "E1", "name": "过饱和", "severity": "L1", "description": "行驶中的通勤列车深蓝车身在受光面局部过于浓艳，饱和度偏高。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "轨道护坡下方的绿化树木局部错涂为偏冷青灰色。"}
    ], "铁路两旁红砖建筑外墙偏暗紫褐灰，通勤列车深蓝车身在受光面局部过饱和(D-L2, E1-L1, C-L2)"),
    4423: make_revision_review(4423, [
        {"id": "D", "name": "偏色", "severity": "L1", "description": "客厅实木地板、电视柜与置物架阴影略偏冷灰青蓝调。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "白色陈列柜内陈列的多彩玩偶手办与工艺品色彩略显发暗欠饱和。"}
    ], "客厅实木地板与电视柜略偏冷灰青蓝调，白色陈列柜玩偶手办色彩欠饱和发暗(D-L1, E2-L1)"),
    4425: make_revision_review(4425, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "大象活动区背景茂密的翠绿树冠被错涂为发暗枯黄的橄榄绿褐色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "背景林木与沙地整体严重发灰脱色，饱和度比值仅0.64，欠饱和明显。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "亚洲象皮肤褶皱全域略偏暗褐灰调。"}
    ], "大象活动区背景翠绿树冠错涂为发暗枯黄橄榄绿褐，沙地与林木严重发灰脱色(C-L2, E2-L2, D-L1)"),
    4426: make_pass_review(4426),
    4427: make_revision_review(4427, [
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "厨房水槽下方的红色桌布裙边与墙面红瓷砖过度浓艳刺眼，呈现荧光洋红倾向。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "厨房粉刷墙壁与微波炉外壳全域偏暗灰青绿杂色，丧失干净暖白环境光。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "红色台裙边缘高光溢出，视觉自然度欠佳。"}
    ], "水槽下方红色桌布裙边与红瓷砖过度浓艳呈荧光洋红，粉刷墙面偏暗灰青绿(E1-L2, D-L2, F-L1)"),

    # Sheet 11
    4428: make_revision_review(4428, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "店铺大门上方“Palau”发光字招牌原本明亮温暖的金黄色底色被严重错涂为冰冷浅天蓝色。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "门头石砌立面与上方挂钟边缘微偏冷青灰暗调。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "橱窗内陈列的各色微缩玩具车模彩绘细节轻度欠饱和。"}
    ], "店铺大门“Palau”发光字招牌原本金黄色底色严重错涂为冰冷浅天蓝(C-L3, D-L1, E2-L1)"),
    4430: make_revision_review(4430, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "室内玩耍幼童身穿的浅粉紫色长袖睡衣被错涂褪色为发暗的灰白色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "背景实木书架、书籍书脊与幼童面部肤色全域偏冷暗青黄调。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "两名儿童面部缺乏红润血色，睡衣色彩欠饱和发暗。"}
    ], "幼童浅粉紫色睡衣错涂褪色为发暗灰白，实木书架与幼童肤色偏冷暗青黄(C-L2, D-L2, E2-L1)"),
    4431: make_revision_review(4431, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "胶片拍摄的海天日落晚霞地平线原本浓郁的暖橙红与金黄余晖被彻底错涂为冰冷发白的青天光。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "整个胶片画幅四周黑色边框与水面反射全域偏冷暗青蓝调。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "画面中心受光区域严重欠饱和脱色，饱和度比值仅0.30，色彩流失严重。"}
    ], "海天日落晚霞地平线原本暖橙红余晖彻底错涂为冰冷发白青天光，受光区严重脱色(C-L3, D-L2, E2-L2)"),
    4433: make_revision_review(4433, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "虎斑猫颈部佩戴的鲜艳红蓝小项圈错涂为暗沉发灰的暗红褐色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "猫咪倚靠的真皮沙发皮革靠背全域偏冷暗灰褐，丧失GT原图温润的暖肉桂粉色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "虎斑猫面部黄褐斑纹与眼眸欠缺明亮色泽，略显发暗。"}
    ], "虎斑猫颈部红蓝小项圈错涂为暗沉暗红褐，真皮沙发靠背偏冷暗灰褐(C-L2, D-L2, E2-L1)"),
    4436: make_revision_review(4436, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "人物服饰、婴儿车遮阳棚与古建筑砖墙阴影严重偏冷紫暗调。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "背景花园绿树与灌木受光面错涂为偏刺眼的荧光翠绿色。"},
        {"id": "E1", "name": "过饱和", "severity": "L1", "description": "背景树冠高光区域饱和度过高，略显浓艳失真。"}
    ], "人物服饰与婴儿车遮阳棚阴影严重偏冷紫暗调，背景花园绿树错涂为荧光翠绿(D-L2, C-L2, E1-L1)"),
    4437: make_revision_review(4437, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "户外积雪木屋侧壁与废弃冰箱内部阴影严重偏冷暗紫红杂色，违背自然采光规律。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "老化冰箱塑料内胆的泛黄陈旧色泽错涂为暗沉灰白并夹杂紫斑。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "木板接缝与雪地边缘呈现明显人工伪色，视觉自然度极差。"}
    ], "积雪木屋侧壁与废弃冰箱内部严重偏冷暗紫红杂色，老化冰箱内胆错涂发灰带紫斑(D-L2, C-L2, F-L2)"),

    # Sheet 12
    4438: make_pass_review(4438),
    4439: make_revision_review(4439, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "白纸餐盘中金黄烘烤的汉堡面包顶盖与黄油土豆泥被错涂为冰冷浅青灰白，丧失GT诱人热食暖色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "餐桌台面、餐叉与室内背景全域偏冷暗青灰调。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "食物表面严重脱色泛白，饱和度比值仅0.54，欠饱和严重。"}
    ], "汉堡面包顶盖与黄油土豆泥错涂为冰冷浅青灰白，餐桌与背景偏冷暗青灰(C-L3, D-L2, E2-L2)"),
    4440: make_revision_review(4440, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "餐厅后厨传菜保温台头顶高强度红外保温红光被彻底错涂为冰冷惨白的不锈钢冷青光。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "金属置物架、白色餐盘与后厨瓷砖立面全域偏冷青绿调，彻底背离真实光源。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "画面整体红暖色调严重脱色，饱和度比值骤降至0.26，欠饱和严重。"}
    ], "后厨出餐保温台头顶高强度红外保温红光被彻底错涂为冰冷惨白不锈钢冷青光(C-L3, D-L2, E2-L2)"),
    4443: make_revision_review(4443, [
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "庆祝生日的圆形奶油蛋糕天蓝色抹面涂层过度浓艳刺眼，呈现荧光高饱和电光蓝。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "蛋糕顶端插着的金色五角星蜡烛装饰错涂为发暗荧光黄褐色。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "蛋糕边缘与深色托盘交界处高光溢出，视觉自然度欠佳。"}
    ], "圆形奶油蛋糕天蓝色抹面涂层过度浓艳呈荧光电光蓝，金色五角星蜡烛错涂发暗黄褐(E1-L2, C-L2, F-L1)"),
    4444: make_pass_review(4444),
    4445: make_revision_review(4445, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "餐桌上标志性大红色可口可乐纸杯（Coca-Cola）被大面积错涂为暗沉发污的深紫暗红色。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "热狗面包上浇淋的鲜艳金黄芥末酱错涂为暗淡黄褐色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "快餐厅木质餐桌与玻璃窗外街景整体严重偏冷暗青蓝调。"}
    ], "大红色可口可乐纸杯被大面积错涂为暗沉深紫暗红，热狗金黄芥末酱错涂为黄褐色(C-L3, C-L2, D-L2)"),

    # Sheet 13
    4446: make_revision_review(4446, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "豪华浴室粉刷天花板、镜柜门框与白色大理石浴缸偏冷暗青蓝调，丧失GT温馨暖光。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "浴缸后方装饰性摩洛哥风格蓝白花纹瓷砖错涂为发暗青灰蓝色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "摆放整齐的白色折叠浴巾与洗浴用品阴影欠饱和发暗。"}
    ], "豪华浴室天花板与大理石浴缸偏冷暗青蓝，摩洛哥蓝白花纹瓷砖错涂为发暗青灰蓝(D-L2, C-L2, E2-L1)"),
    4447: make_revision_review(4447, [
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "女士双手佩戴的防烫隔热烘焙手套过度浓艳刺眼，呈现荧光草绿色高饱和溢出。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "女士身穿的深酒红色高领针织衫错涂为偏冷荧光洋红色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "厨房背景粉刷墙壁与橱柜门板全域偏浑浊黄绿杂色，视觉自然度极差。"}
    ], "女士防烫隔热烘焙手套过度浓艳呈荧光草绿，深酒红针织衫错涂为荧光洋红(E1-L2, C-L2, D-L2)"),
    4448: make_revision_review(4448, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "美式校车车身标志性的明亮铬黄色漆面错涂为发暗偏褐的土灰黄色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "背景高大茂密的翠绿树木严重发灰脱色，饱和度比值仅0.66，绿意明显流失。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "沥青道路路面与校车黑色保险杠整体偏冷暗青灰。"}
    ], "美式校车标志性铬黄色车漆错涂为暗沉发褐土灰黄，背景茂密翠绿树木严重发灰脱色(C-L2, E2-L2, D-L1)"),
    4449: make_revision_review(4449, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "亚洲象宽厚身躯与象鼻皮肤全域偏暗红紫杂色，严重偏离野生大象天然砂灰本色。"},
        {"id": "E1", "name": "过饱和", "severity": "L1", "description": "背景树冠叶片与草地受光面饱和度过高，呈现刺眼的翠黄色。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "象皮受光面与阴影交界处呈现不自然假色过渡。"}
    ], "亚洲象身躯与象鼻皮肤全域偏暗红紫杂色，背景树林受光面过度浓艳偏翠黄(D-L2, E1-L1, F-L1)"),
    4450: make_revision_review(4450, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "斑马栖息地背景茂密灌木树丛错涂为发暗枯黄的灰橄榄色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "背景绿植林地整体发灰脱色，饱和度比值低至0.60，欠饱和明显。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "斑马黑白条纹皮毛暗部略偏冷青蓝暗调。"}
    ], "斑马栖息地背景茂密树丛错涂为发暗枯黄灰橄榄色，绿植严重脱色泛灰(C-L2, E2-L2, D-L1)"),
    4455: make_revision_review(4455, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "驾驶室车顶遮阳板与内饰软包面料被错涂为发暗的灰粉紫色。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "金毛寻回犬金黄色被毛与车门把手略偏冷暗红褐。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "车窗外海港水面与工业码头远景色彩略显发暗欠饱和。"}
    ], "驾驶室内饰遮阳板软包面料错涂为发暗灰粉紫，金毛犬金黄被毛略偏冷暗红褐(C-L2, D-L1, E2-L1)"),

    # Sheet 14
    4457: make_pass_review(4457),
    4458: make_pass_review(4458),
    4460: make_pass_review(4460),
    4461: make_revision_review(4461, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "室内粉刷墙面、门框与窗帘整体严重偏冷灰青绿调，丧失GT温馨居家暖黄光感。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "两名年轻女性面部与手臂皮肤略显发灰脱色，缺乏红润血色。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "人物受光边缘色温过渡略显生硬。"}
    ], "室内粉刷墙面与窗帘严重偏冷灰青绿调，年轻女性面部与手臂皮肤略显发灰脱色(D-L2, E2-L1, F-L1)"),
    4462: make_revision_review(4462, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "海滩背景中辽阔的蔚蓝大海与晴朗天空被彻底错涂为阴沉冰冷的灰白色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "沙滩白色躺椅、遮阳伞与细沙地面全域偏冷暗青灰调。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "碧海蓝天大面积严重脱色泛灰，饱和度比值低至0.35，欠饱和严重。"}
    ], "辽阔蔚蓝大海与晴朗天空彻底错涂为阴沉冰冷灰白色，沙滩全景严重脱色泛灰(C-L3, D-L2, E2-L2)"),
    4463: make_revision_review(4463, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "自助餐桌左侧玻璃杯中原本鲜艳金黄的鲜榨橙汁错涂为发暗青黄杂色。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "餐盘中烘烤印度薄饼与浓汁咖喱整体微偏暗灰青绿调。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "白色瓷盘与桌面餐巾高光色彩略显欠饱和发暗。"}
    ], "玻璃杯中金黄鲜榨橙汁错涂为发暗青黄杂色，餐盘中印度薄饼与咖喱微偏暗灰青绿(C-L2, D-L1, E2-L1)"),

    # Sheet 15
    4464: make_pass_review(4464),
    4465: make_revision_review(4465, [
        {"id": "D", "name": "偏色", "severity": "L1", "description": "人物面部肤色与街景车辆反光略偏暗暖黄红调。"},
        {"id": "E1", "name": "过饱和", "severity": "L1", "description": "女性身穿的碎花衬衫花卉图案色调偏高饱和洋红，略显过浓。"}
    ], "人物面部肤色略偏暗暖黄红，碎花衬衫花卉图案色调偏高饱和洋红(D-L1, E1-L1)"),
    4467: make_revision_review(4467, [
        {"id": "D", "name": "偏色", "severity": "L1", "description": "室内实木地板、斗柜台面与壁炉周边略偏冷暗青灰调，缺少GT木质天然温润感。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "白色多屉储物柜抽屉把手与踢脚线高光略显欠饱和发暗。"}
    ], "室内实木地板与斗柜略偏冷暗青灰调，储物柜把手与踢脚线略显欠饱和发暗(D-L1, E2-L1)"),
    4468: make_pass_review(4468),
    4470: make_pass_review(4470),
    4472: make_revision_review(4472, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "轨道站台边缘极其醒目的明黄色安全警示地面盲道被彻底错涂为发暗冰冷的泥灰白色。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "站台右侧深红色支撑金属立柱错涂为暗沉发黑的灰青色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "站台地面、坐椅与远处遮阳雨棚全域偏冷暗青灰调，欠饱和严重。"}
    ], "站台边缘明黄安全警示盲道彻底错涂为发暗泥灰白，深红金属立柱错涂为暗沉灰青(C-L3, C-L2, D-L2)"),

    # Sheet 16
    4474: make_revision_review(4474, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "牧场缓坡上开阔茂密的青翠草坪被大面积严重错涂为发暗枯黄的泥土橄榄色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "草坡上的放牧黄牛被毛与远景山丘全域偏冷暗黄褐杂色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "绿地草场大面积脱色衰败，欠饱和严重。"}
    ], "牧场缓坡青翠草坪大面积严重错涂为发暗枯黄泥土橄榄色，放牧黄牛偏冷暗黄褐(C-L3, D-L2, E2-L2)"),
    4475: make_revision_review(4475, [
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "阴雨天执勤骑警身穿的高可见度荧光黄绿骑行反光服过度浓艳刺眼，高光严重溢出。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "湿滑沥青路面上摆放的橙红色交通路障锥筒错涂为偏冷荧光粉红色。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "警用摩托车金属反光与雨天路面积水倒影略偏冷暗紫蓝调。"}
    ], "骑警荧光黄绿骑行反光服过度浓艳刺眼，橙红路障锥筒错涂为荧光粉红(E1-L2, C-L2, D-L1)"),
    4476: make_revision_review(4476, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "历史建筑遗迹与沙土废墟原本明亮温暖的金黄暖橙色阳光外墙被彻底错涂为冰冷浅灰白色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "漫步的黑色牲畜体表、石砌地基与天空全域偏冷暗青灰调。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "遗迹全景严重褪色泛灰，饱和度比值仅0.51，苍白失真。"}
    ], "历史石砌废墟原本金黄暖橙色阳光外墙彻底错涂为冰冷浅灰白，全景褪色泛灰(C-L3, D-L2, E2-L2)"),
    4477: make_revision_review(4477, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "哥特式红砖教堂建筑外墙、钟楼立面与路面全域偏冷暗紫褐灰，丧失GT红砖建筑的天然古朴暖意。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "街头红绿灯交通信号灯罩与白色车辆高光略显欠饱和发暗。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "建筑尖顶与阴沉天空交界处存在轻度暗调失真。"}
    ], "红砖教堂建筑外墙与钟楼偏冷暗紫褐灰，交通信号灯罩略显欠饱和发暗(D-L2, E2-L1, F-L1)"),
    4478: make_revision_review(4478, [
        {"id": "B", "name": "溢色", "severity": "L2", "description": "床单上印染的鲜艳红花染料严重越界向仰卧小猫纯白腹部与四肢毛发发生溢色渗透。"},
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "花卉被褥面料上的大红与玫粉花朵图案过度浓艳刺眼，呈现荧光洋红倾向。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "猫毛表面大面积被粉红假色污染，视觉真实感极差。"}
    ], "床单印染红花染料严重越界向仰卧小猫纯白腹部溢色渗透，花卉图案过度浓艳(B-L2, E1-L2, F-L2)"),
    4479: make_pass_review(4479),

    # Sheet 17
    4480: make_revision_review(4480, [
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "水果摊位悬挂的成熟香蕉与青绿西瓜受光面过度浓艳，呈现刺眼的荧光黄绿色高光溢出。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "摊主身穿的白色T恤阴影与摊位顶棚略偏冷紫暗调。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "水果堆与人物轮廓交接处略带杂色溢出，视觉自然度受损。"}
    ], "水果摊悬挂香蕉与青绿西瓜过度浓艳呈荧光黄绿溢出，摊主白色T恤略偏冷紫暗调(E1-L2, D-L1, F-L1)"),
    4481: make_revision_review(4481, [
        {"id": "E1", "name": "过饱和", "severity": "L3", "description": "男子撑开的遮阳伞与扎染短袖上衣过度浓艳刺眼至极，呈现极为恶性的人工荧光品红与高饱和电光蓝暴击。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "男子面部五官、浓密胡须与颈部皮肤全域偏冷暗青紫杂色，严重伪色失真。"},
        {"id": "F", "name": "视觉自然度", "severity": "L3", "description": "画面整体被剧烈荧光色斑完全污染，视觉真实度彻底崩溃。"}
    ], "遮阳伞与扎染上衣过度浓艳刺眼呈荧光品红与电光蓝，男子面部与胡须全域偏冷暗青紫(E1-L3, D-L2, F-L3)"),
    4482: make_revision_review(4482, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "浴室瓷砖墙面、白色洗手台与塑料浴帘整体严重偏冷灰青蓝调，丧失GT温馨明亮的暖米黄色调。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "白色陶瓷浴缸与窗台反光严重发灰暗淡，欠饱和。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "窗外光线与室内瓷砖阴影过渡略显冰冷生硬。"}
    ], "浴室瓷砖墙面与塑料浴帘整体严重偏冷灰青蓝调，陶瓷浴缸发灰暗淡欠饱和(D-L2, E2-L1, F-L1)"),
    4483: make_revision_review(4483, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "动物园草坪与后方茂密森林大面积被严重错涂为发暗枯黄的泥土橄榄褐色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "长颈鹿网状斑纹皮毛与黑色大鸟体表全域偏暗灰褐色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "绿植生态环境整体缺乏生机，呈现欠饱和衰败感。"}
    ], "动物园草坪与茂密森林大面积严重错涂为发暗枯黄泥土橄榄褐，长颈鹿皮毛偏暗灰褐(C-L3, D-L2, E2-L1)"),
    4484: make_revision_review(4484, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "考拉毛绒公仔原本蓬松自然的浅灰褐色毛发被荒唐错涂为暗沉发污的红棕锈褐色。"},
        {"id": "B", "name": "溢色", "severity": "L1", "description": "考拉颈部蓝色丝带边缘向胸前白色软毛发生轻度溢色晕染。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "毛绒玩具身体色彩与沥青地面反光显得突兀生硬。"}
    ], "考拉毛绒公仔浅灰褐毛发荒唐错涂为暗沉红棕锈褐，颈部蓝丝带边缘轻度溢色(C-L3, B-L1, F-L1)"),
    4485: make_revision_review(4485, [
        {"id": "D", "name": "偏色", "severity": "L1", "description": "昏暗室内红色墙面与折叠桌金属支架整体微偏冷暗紫红杂色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "笔记本电脑屏幕发光与键盘白色高光细节略显欠饱和发暗。"}
    ], "室内红色墙面微偏冷暗紫红杂色，笔记本电脑屏幕高光细节略显欠饱和发暗(D-L1, E2-L1)"),

    # Sheet 18
    4488: make_revision_review(4488, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "帐篷开口外原本生机盎然的青翠户外草坪被彻底错涂为发暗灰白无色的泥草地。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "帐篷内就餐男女的黄色翻领短袖与黑白条纹上衣全域偏冷暗青灰调。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "人物面部肤色发暗脱色，欠缺阳光下的红润感。"}
    ], "帐篷外青翠草坪彻底错涂为发暗灰白泥草地，就餐男女黄色上衣偏冷暗青灰(C-L3, D-L2, E2-L1)"),
    4493: make_revision_review(4493, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "客厅复古真皮沙发皮革表面与实木茶几整体偏冷暗紫褐杂色，脱失GT典雅的暖棕琥珀色泽。"},
        {"id": "E1", "name": "过饱和", "severity": "L1", "description": "桌面红色台灯与书籍封面红色彩印局部饱和度过高。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "摊开的白色乐谱纸张边缘泛起轻微紫暗色斑，自然度欠佳。"}
    ], "客厅真皮沙发与茶几偏冷暗紫褐杂色，桌面红色台灯与书籍封面局部饱和度过高(D-L2, E1-L1, F-L1)"),
    4496: make_pass_review(4496),
    4497: make_revision_review(4497, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "丛林游览区背景茂密的热带雨林树木大面积错涂为发暗枯黄的灰橄榄色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "背景森林植被严重发灰脱色，饱和度比值仅0.53，欠饱和明显。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "大象背上的红色坐垫毯与河流泥水全域微偏暗褐灰调。"}
    ], "丛林背景热带雨林树木错涂为发暗枯黄灰橄榄色，森林植被严重发灰脱色(C-L2, E2-L2, D-L1)"),
    4498: make_revision_review(4498, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "交通信号灯上方点亮的圆形红灯错涂为发暗浑浊的紫红色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "信号灯明黄色金属外壳全域偏暗灰黄褐杂色。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "红色与绿色信号灯光晕边缘色彩生硬泛白，视觉自然度极差。"}
    ], "交通信号灯圆形红灯错涂为发暗浑浊紫红，明黄金属外壳偏暗灰黄褐杂色(C-L2, D-L2, F-L2)"),
    4499: make_revision_review(4499, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "摆放果汁与新鲜果蔬的暖橙红色背景台面被大面积错涂为暗沉冰冷的泥灰褐色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "绿色玻璃罐装果蔬奶昔与青苹果表面阴影偏冷暗青灰。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "紫色洋葱与黄色香蕉果皮色彩饱和度偏低，略显发暗。"}
    ], "暖橙红色背景台面大面积错涂为暗沉泥灰褐色，绿色玻璃罐果蔬汁阴影偏冷暗青灰(C-L3, D-L2, E2-L1)"),

    # Sheet 19
    4500: make_revision_review(4500, [
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "客厅墨绿色布艺沙发与全铺草绿地毯过度浓艳刺眼，呈现荧光草绿色高饱和溢出。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "室内粉刷墙面、门框与白色窗帘全域偏发闷的暗黄绿色调。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "地毯与墙脚线交界处高光色泽刺眼，视觉自然度欠佳。"}
    ], "客厅墨绿布艺沙发与草绿地毯过度浓艳呈荧光草绿，粉刷墙面偏发闷暗黄绿(E1-L2, D-L2, F-L1)"),
    4501: make_pass_review(4501),
    4502: make_revision_review(4502, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "废弃浴室剥落霉变的天花板、破旧浴缸与马桶表面整体严重偏冷灰青蓝调，丧失真实风化锈蚀的黄褐泥污感。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "墙壁瓷砖与金属管道大面积发暗脱色，呈现欠饱和的干瘪灰度。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "破损天花板与墙面阴影过渡生硬发黑。"}
    ], "废弃浴室剥落天花板与浴缸严重偏冷灰青蓝调，瓷砖与金属管道大面积发暗脱色(D-L2, E2-L2, F-L1)"),
    4503: make_revision_review(4503, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "阳光照射下的干燥砂土地面与泥土路面被错涂为发暗冰冷的泥灰白色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "树荫下卧倒的黑牛体表与小棕狗毛皮全域偏冷暗青灰调。"},
        {"id": "E2", "name": "欠饱和", "severity": "L1", "description": "背景树木受光面与地面受光区域色彩欠饱和发暗。"}
    ], "干燥砂土地面被错涂为发暗泥灰白，树荫下黑牛与小棕狗毛皮偏冷暗青灰(C-L2, D-L2, E2-L1)"),
    4504: make_revision_review(4504, [
        {"id": "C", "name": "错色", "severity": "L2", "description": "露台陈列的巨大彩绘红陶水瓮罐身浓郁的红褐色烧陶釉面错涂为暗沉发黄的土棕色。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "背景海湾蔚蓝深邃的海水与远处高楼错涂为发白浅青灰天蓝色。"},
        {"id": "D", "name": "偏色", "severity": "L1", "description": "露台地面与近景栏杆整体微偏暗灰青绿调。"}
    ], "彩绘红陶水瓮红褐色烧陶釉面错涂为暗沉土棕，海湾蔚蓝海水错涂为浅青灰天蓝(C-L2, C-L2, D-L1)"),
    4505: make_revision_review(4505, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "走廊暖黄色碎花壁纸墙面、踢脚线与天花板整体严重偏浑浊的暗黄绿杂色。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "走廊白色室内木门门板表面与上方挂钟边缘错涂并混入发暗冷青灰斑。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "走廊尽头采光与前庭暖光交接处色调失调，自然度受损。"}
    ], "走廊暖黄色壁纸墙面严重偏浑浊暗黄绿杂色，白色木门表面混入冷青灰斑(D-L2, C-L2, F-L1)"),

    # Sheet 20
    4506: make_revision_review(4506, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "公园广场草坪背景原本葱郁茂盛的翠绿树林被彻底错涂为发暗枯败的浅灰白色。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "四面大钟基座的天然红砖砌体与深棕铜质表壳错涂为暗沉无光泽的深灰黑色。"},
        {"id": "E2", "name": "欠饱和", "severity": "L2", "description": "画面绿植大面积脱色泛灰，饱和度比值仅0.41，欠饱和严重。"}
    ], "公园广场原本葱郁茂盛翠绿树林彻底错涂为发暗浅灰白，大钟红砖基座错涂为深灰黑(C-L3, C-L2, E2-L2)"),
    4508: make_revision_review(4508, [
        {"id": "D", "name": "偏色", "severity": "L2", "description": "超市生鲜货架堆放的金黄甜橙与柑橘表皮全域偏冷发暗的黄褐杂色，丧失新鲜诱人光泽。"},
        {"id": "C", "name": "错色", "severity": "L2", "description": "货架右侧陈列的新鲜绿叶蔬菜被错涂为发暗橄榄灰绿色。"},
        {"id": "E1", "name": "过饱和", "severity": "L1", "description": "果蔬陈列柜荧光灯照明高光区域局部对比略硬。"}
    ], "生鲜货架金黄甜橙表皮偏冷发暗黄褐杂色，新鲜绿叶蔬菜错涂为发暗橄榄灰绿(D-L2, C-L2, E1-L1)"),
    4510: make_pass_review(4510),
    4511: make_revision_review(4511, [
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "乡村餐馆实木吧台橱柜、木地板与红色方格野餐桌布过度浓艳刺眼，呈现荧光高饱和橙红色。"},
        {"id": "D", "name": "偏色", "severity": "L2", "description": "餐厅粉刷墙面与天花板受光面全域偏发闷的暗红黄色调。"},
        {"id": "F", "name": "视觉自然度", "severity": "L1", "description": "吧台酒架与高光区域反光过艳，视觉自然度明显受损。"}
    ], "实木吧台橱柜与红色方格野餐桌布过度浓艳呈荧光橙红，粉刷墙面偏发闷暗红黄(E1-L2, D-L2, F-L1)"),
    4513: make_revision_review(4513, [
        {"id": "C", "name": "错色", "severity": "L3", "description": "白瓷果盘正前方贴有卡通大笑表情的鲜亮金橙色甜橙被极其荒唐地彻底错涂为荧光草绿色，严重违背真实物体属性。"},
        {"id": "E1", "name": "过饱和", "severity": "L2", "description": "果盘周围其他橙子与柠檬果皮色调过度浓艳刺眼，呈现荧光高饱和倾向。"},
        {"id": "F", "name": "视觉自然度", "severity": "L2", "description": "荒唐的错色导致整体静物画面视觉真实感彻底崩塌。"}
    ], "贴有卡通笑脸的金橙色甜橙被荒唐彻底错涂为荧光草绿，周围果皮过度浓艳(C-L3, E1-L2, F-L2)"),
    4514: make_pass_review(4514),
}

def main():
    print(f"Total reviews in Batch {BATCH_NO}: {len(REVIEWS)}")
    assert len(REVIEWS) == 120, f"Expected 120 reviews, got {len(REVIEWS)}"

    # 1. Check banned words
    banned_hits = []
    for tid, rev in REVIEWS.items():
        text_to_check = rev["note"]
        for d in rev.get("defects", []):
            text_to_check += " " + d["description"]
        for bw in BANNED_WORDS:
            if bw in text_to_check:
                banned_hits.append((tid, bw))

    if banned_hits:
        print(f"[FAIL] Found {len(banned_hits)} banned words:")
        for tid, bw in banned_hits:
            print(f"  Task #{tid}: {bw}")
        raise ValueError("Please remove banned words from reviews!")
    else:
        print("[PASS] Zero banned words detected across all descriptions and notes.")

    # 2. Count stats
    pass_count = sum(1 for r in REVIEWS.values() if r["status"] == "PASS")
    rev_count = sum(1 for r in REVIEWS.values() if r["status"] == "REVISION")
    print(f"[STAT] Pass: {pass_count} ({pass_count/len(REVIEWS)*100:.1f}%), Revisions: {rev_count} ({rev_count/len(REVIEWS)*100:.1f}%)")

    # 3. Save grounding JSON
    with open(GROUNDING_FILE, "w", encoding="utf-8") as f:
        json.dump(REVIEWS, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved grounding JSON to {os.path.abspath(GROUNDING_FILE)}")

    # 4. Synchronize into reviewed_1_10000_all.json and clean.json
    print("\nSynchronizing into reviewed_1_10000_all.json and clean.json...")
    with open(ALL_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    all_task_map = {ann["human_review"]["task_id"]: ann for ann in all_data["annotations"]}
    clean_task_map = {ann["human_review"]["task_id"]: ann for ann in clean_data["annotations"]}

    for tid, rev in REVIEWS.items():
        if tid not in all_task_map:
            print(f"[WARN] Task #{tid} not found in all_data annotations!")
            continue

        ann_all = all_task_map[tid]
        ann_clean = clean_task_map[tid]

        if rev["status"] == "PASS":
            ann_all["review_status"] = "已核验"
            ann_all["review_note"] = "审查通过"
            ann_all["defects"] = []
            ann_all["reviewed_score"] = None
            ann_all["needs_rescoring"] = True

            ann_clean["review_status"] = "已核验"
            ann_clean["review_note"] = ""
            ann_clean["defects"] = []
            ann_clean["reviewed_score"] = None
            ann_clean["needs_rescoring"] = True
        else:
            # Check for defect A
            has_a = any(d["id"] == "A" for d in rev["defects"])
            ann_all["review_status"] = "已核验"
            ann_all["review_note"] = rev["note"]
            ann_all["defects"] = rev["defects"]
            ann_all["reviewed_score"] = 1.0 if has_a else None
            ann_all["needs_rescoring"] = False if has_a else True

            ann_clean["review_status"] = "已核验"
            ann_clean["review_note"] = ""
            ann_clean["defects"] = rev["defects"]
            ann_clean["reviewed_score"] = 1.0 if has_a else None
            ann_clean["needs_rescoring"] = False if has_a else True

    with open(ALL_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Successfully updated {os.path.abspath(ALL_FILE)}")

    with open(CLEAN_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Successfully updated {os.path.abspath(CLEAN_FILE)}")

if __name__ == "__main__":
    main()
