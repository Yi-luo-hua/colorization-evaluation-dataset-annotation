"""Reproducible experiment report and source/output integrity checks."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

import experiment_v1 as ex
import refine_v2 as v2


def load_rows(path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        raw=list(csv.DictReader(f))
    out=[]
    for row in raw:
        result={}
        for k,value in row.items():
            if k in ['image_id','partition','intervention','hidden_fractions','model']:
                result[k]=value
            elif k in ['a_intervention','d_intervention','original_size_mismatch','analysis_resize']:
                result[k]=value=='True'
            elif k in ['cell_norms','cell_distances']:
                result[k]=json.loads(value)
            else:
                result[k]=float(value) if value else None
        out.append(result)
    return out


def metric_line(name,result):
    return f"| {name} | {result['precision']:.2%} | {result['recall']:.2%} | {result['f1']:.4f} | {result['fp']} | {result['fn']} |"


def main():
    cfg=json.loads(Path(__file__).with_name('config_v1.json').read_text(encoding='utf-8'))
    out=ex.BASE/'intermediate'/'audits'/cfg['experiment_id'];sheets=ex.BASE/'intermediate'/'inspection_sheets'/cfg['experiment_id']
    old=json.loads((out/'candidate_parameters.json').read_text(encoding='utf-8'));new=json.loads((out/'v2_results.json').read_text(encoding='utf-8'))
    gt=json.loads((out/'gt_statistics.json').read_text(encoding='utf-8'))['per_image'];labels=json.loads((out/'legacy_label_statistics.json').read_text(encoding='utf-8'))['groups']
    rows=load_rows(out/'v2_synthetic_metrics.csv');lock=[r for r in rows if r['partition']=='lockbox']
    a_pred=v2.a_predict(lock,new['A']['parameters'],old['A']['parameters'])
    d_pred=v2.d_predict(lock,new['D']['parameters']) & ~a_pred
    cascade={'A':ex.confusion([r['a_intervention'] for r in lock],a_pred),'D_after_A':ex.confusion([r['d_intervention'] for r in lock],d_pred),
             'true_D_wrongly_routed_to_A':int(np.sum(a_pred & np.array([r['d_intervention'] for r in lock])))}
    ex.save_json(out/'cascade_diagnostic.json',cascade)
    with (out/'gt_profiles.csv').open(encoding='utf-8-sig') as f:profiles=list(csv.DictReader(f))
    nearly_gray=sum(float(r['mean_c'])<2.5 for r in profiles if r['split']=='train')
    old_a_eligible_failure=sum(float(r['mean_c'])<=8 for r in profiles if r['split']=='train')
    hue=[r for r in lock if r['intervention'].startswith('local_hue_') and r['area_fraction']<0.1]
    p90_blind=sum(r['hue_component_p90']<1 and r['hue_component_max']>10 for r in hue)
    sensitivity=json.loads((out/'resolution_sensitivity.json').read_text(encoding='utf-8'))
    display=json.loads((out/'display_deadzone_ablation.json').read_text(encoding='utf-8'))['groups']
    d=new['D']['results']['lockbox'];ci=new['D']['lockbox_cluster_bootstrap']
    text=[
        '# 图像上色评价工作流：GT统计与CV机制实验第一轮',
        '',
        '日期：2026-10-12。结论：空间共同偏移、未变化区域覆盖及彩度缩放解释联合使用，在当前合成干预上明显优于全图均值；A单色分支仍有误熔断风险；双向彩度图可辅助定位，但不能单独发现所有错色。所有阈值仍为实验候选，未修改正式工具链或任何源标签。',
        '',
        '## 1. 数据、分区与结果边界',
        '',
        '- GT本底：训练集10,000张、验证集1,428张，合计11,428张；每张保留尺寸、彩度分位数、灰阶比例与色度中心统计。',
        '- 真实对照：验证集LCAD/Unicolor各1,428组，共2,856组。GT只计一次，旧标签按模型分别统计。',
        '- 原始标签来源：两套数据目录的labels/annotations.json，均是模型预标注，不能当作新的人工缺陷真值。未将这些标签用于阈值拟合。',
        '- 验证集按GT ID的固定哈希分区：1,030张用于校准，398张留出；同一GT的两个模型始终同区。测试集完全未读取。',
        '- v1合成实验：96张GT，每张33种干预，共3,168例；48张校准、48张留出。',
        '- v2：v1全部96张进入开发集，新增48张此前未用于合成实验的GT作为新留出；共144张GT、4,752例，其中新留出1,584例。v2超参数只用开发集搜索。',
        '- 干预包含恒等、JPEG对照、灰阶、固定色调、正负全图偏移、25%/50%/75%局部偏移、1%/5%/25%/50%区域换色、全图彩度缩放、局部彩度增减并存、全图偏移叠加局部变化。',
        '- 合成A/D标记指已知干预类别；不等于人类认可的缺陷或严重度。矩形不是物体分割。干预经过Lab→RGB→Lab，保留色域限制带来的变化。',
        '- 统计最长边缩至256像素；12个高差异真实样本补做原尺寸敏感性检查，不能据此证明全部小物体特征在缩放后稳定。',
        '- 没有运行独立AI盲审A/B，也没有人工锚定L1/L2/L3。当前代理查看了8张三联样例，只用于渲染和证据检查。',
        '',
        '## 2. GT本底怎样辅助参数选择',
        '',
        '| GT逐图平均彩度 C* | P1 | P5 | P50 | P95 | 最小值 |',
        '|---|---:|---:|---:|---:|---:|'
    ]
    for split,name in [('train','训练'),('val','验证')]:
        q=gt[split]['mean_c'];text.append(f"| {name} | {q['p1']:.2f} | {q['p5']:.2f} | {q['p50']:.2f} | {q['p95']:.2f} | {q['p0']:.2f} |")
    text.extend([
        '',
        f'训练GT中有{nearly_gray}张平均彩度小于2.5；如果仅按生成图绝对彩度判断，连忠实复制GT也可能被误伤。旧规则要求GT均值>8才判缺色，会使{old_a_eligible_failure}张GT对应的真正灰阶失败难以触发该规则。需要GT条件化和“不足以判断”的出口，而非单一绝对阈值。',
        '',
        f"训练GT的C*<3像素比例最高为{gt['train']['gray_fraction_c_lt_3']['p100']:.2%}，验证GT最高为{gt['val']['gray_fraction_c_lt_3']['p100']:.2%}；高灰阶占比可以来自真实图像。",
        '',
        '用途：GT分布用于低彩度边界选样、分层抽样和给搜索范围提供依据；各模型对照分布用于可视化动态范围。GT分位数不能直接推出缺陷阈值或L1/L2/L3。',
        '',
        '## 3. 旧标签分布：仅用于探索',
        '',
        '| 来源 | A | B | C | D | E1 | E2 | F | 无缺陷 |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|'
    ])
    for group,counts in labels.items():text.append('| '+group+' | '+' | '.join(str(counts[k]['images']) for k in ['A','B','C','D','E1','E2','F','NONE'])+' |')
    text.extend([
        '',
        '不同缺陷可以并存，各列不能相加当图像总数。真实对照按旧标签分组的物理指标存在明显重叠；旧“无缺陷”组也有较大色差。LCAD训练原标签无缺陷4,692张，而历史过程复核交付无缺陷954张，两个标签来源不能混为一套真值。',
        '',
        '## 4. D全图偏色：同一新留出集上的比较',
        '',
        '| 方法 | 精确率 | 召回率 | F1 | 误报 | 漏报 |',
        '|---|---:|---:|---:|---:|---:|'
    ])
    text.extend([metric_line('均值偏移（v1校准所得阈值6）',new['D']['lockbox_tuned_mean_rule']),metric_line('v1网格共同偏移',new['D']['lockbox_v1_rule']),metric_line('v2共同偏移＋活动覆盖＋缩放解释',d)])
    text.extend([
        '',
        f"D在新留出集评估1,488例（排除A干预），正例432、负例1,056。v2对75%局部偏移的误报为{d['by_intervention']['local_shift_area_0.75']['fp']}/48；4次剩余误报均来自彩度增加干预，3次漏报来自负向全图偏移。",
        '',
        f"按48张GT整组重采样500次，D的F1 95% bootstrap区间为[{ci['f1_95_interval'][0]:.4f}, {ci['f1_95_interval'][1]:.4f}]。没有把同一GT的33个变体当成独立图像。该区间只反映本套合成干预，不代表真实标注准确率。",
        '',
        'v2先估计网格共同ab变化，再要求足够多网格确实发生变化；同时拟合“彩度统一缩放＋色度平移”，在缩放明显更能解释变化且平移很小时，抑制D。标量拟合目前是最小二乘诊断，不是物体级颜色成因的证明。',
        '',
        'v2候选参数：',
        '```json',json.dumps(new['D']['parameters'],ensure_ascii=False,indent=2),'```',
        '',
        '范围限制：仅覆盖当前方向、强度、矩形位置和加性ab偏移模型。尚未验证真实白平衡变化、局部照明、非线性色彩映射、大面积同材质场景及真实物体分割。不能据此自动交付D标签。',
        '',
        '## 5. A缺色与熔断风险',
        '',
        f"v2新留出：精确率{new['A']['results']['lockbox']['precision']:.2%}、召回率{new['A']['results']['lockbox']['recall']:.2%}；灰阶干预48/48检出，固定色调干预38/48检出。6次误报都来自真正的全图偏移，不能自动熔断。",
        '',
        f"按A→D级联诊断，有{cascade['true_D_wrongly_routed_to_A']}个真实D干预被A错误抢先路由；D级联召回率为{cascade['D_after_A']['recall']:.2%}。必须验证完整路由，不能只报D独立分支的分数。",
        '',
        '额外低彩度边界：训练GT彩度最低的100张，恒等/JPEG各一次，共200例。A/D均无误报；这是机制反例检查，不是总体误报率证明。',
        '',
        '建议：灰阶失败与固定色调失败分别评估。当前单色集中度分支留在“候选复核”，不要把颜色朝同一方向集中直接等同于全图上色失败。',
        '',
        '## 6. 双向彩度差图显示参数实验',
        '',
        '正向红/品红、负向蓝/青、近零黑色。跨样本共用强度范围。v1由JPEG控制计算的隐藏范围12.25已被否定：',
        '',
        '| 干预 | 隐藏范围1时中位像素隐藏比例 | 隐藏范围12.25时中位隐藏比例 |',
        '|---|---:|---:|'
    ])
    for name in ['global_chroma_scale_0.7','global_chroma_scale_1.3','mixed_chroma_gain_loss']:
        group=display[name];text.append(f"| {name} | {group['1.0']['p50']:.2%} | {group['12.251697349548339']['p50']:.2%} |")
    text.extend([
        '',
        '上述统计是全部像素的隐藏比例，不是缺陷召回率。JPEG控制混入边缘与色度抽样差异，不能作为所有有效弱色差的统一噪声上界。',
        '',
        f"v2展示候选：隐藏范围1、共同强度上限{new['display']['maximum']:.2f}、gamma=0.6。上限来自验证校准区真实对照abs(ΔC*)逐图P95的P95；gamma和隐藏范围仍是显式候选，并未完成主观可见度校准。",
        '',
        f"小区域换色诊断：面积小于10%的288个新留出换色干预中，有{p90_blind}例全图色相分量P90<1但像素最大值>10。这里1与10仅用于展示全图分位数盲点，不作为C阈值。",
        '',
        '等彩度90度换色的已检查例子中，夜景左半边交通灯、招牌等变绿，而彩度图大部分近黑。AI必须查看原始对照；C候选不能仅从ΔC*高亮或全图P90寻找。',
        '',
        f"12个极端真实样本，缩放统计与原尺寸统计的abs(ΔC*) P95最大绝对差为{max(abs(r['analysis_abs_dc_p95']-r['native_abs_dc_p95']) for r in sensitivity):.2f}。后续小物体候选和渲染应额外在原尺寸确认。",
        '',
        '## 7. 已检查的视觉证据',
        '',
        '- real_01：浴室木门从棕色变成浓蓝紫，洗手台也变蓝；红/品红显示彩度增加，不能只标E1而漏掉C。',
        '- real_04：黄色火焰纹摩托车油箱、绿色摩托车和黄色座椅褪为灰白，蓝/青能定位彩度损失。',
        '- real_07：玩具熊红帽和红围巾变青蓝；背景橘红变绿。差图方向并不等于这些物体真实颜色变化的语义。',
        '- real_10：网球草地变紫、运动员皮肤和衣服泛黄；草地彩度降低显示蓝，仍需GT对照识别错色。',
        '- synthetic_mixed_chroma_gain_loss：左侧彩度增加、右侧降低，红蓝同时存在，方向渲染正确。',
        '- synthetic_local_shift_area_0.75：右侧原色仍存在，为大区域局部变化提供反例。',
        '- synthetic_grayscale：全图彩度损失呈蓝，生成图真实为灰阶。',
        '- synthetic_local_hue_90_area_0.5：明显换色但差图近黑，验证其限制。',
        '',
        '## 8. 交付与下一实验',
        '',
        '- gt_profiles.csv / gt_statistics.json：逐图GT统计与总体分布。',
        '- legacy_label_statistics.json / legacy_label_metric_associations.json：旧标签数量及与GT/模型物理指标的关系。',
        '- validation_pair_metrics.csv：全部验证模型对照指标。',
        '- synthetic_metrics.csv / v2_synthetic_metrics.csv：两轮合成干预原始结果。',
        '- candidate_parameters.json / v2_results.json：搜索结果、候选参数、分干预混淆统计与GT整组bootstrap。',
        '- display_deadzone_ablation.json / resolution_sensitivity.json：显示隐藏范围实验、尺寸敏感性。',
        '- scripts/cv_workflow_experiments/visual_harness_v1.md：少图输入、类别边界、物体级输出和盲审方案。',
        '- inspection_sheets/cv_workflow_experiment_20261012_01/v2/：12个真实样例与6个可控样例；v1旧图仅保留供失败分析。',
        '',
        '后续优先：用人工确认的真实案例验证D混淆与A误熔断，再进行二图/三图/三图加摘要的独立视觉A/B。本轮不对B/F和L1/L2/L3宣称算法校准完成。',
        '',
        '## 9. 复现',
        '',
        '使用项目内置Python；从工作区根目录顺序运行以下脚本，不使用--reuse-gt即可全量重算。参数全部位于config_v1.json/config_v2.json。',
        '',
        '```powershell',
        '& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\LS_lcad_reviewer\intermediate\scripts\cv_workflow_experiments\experiment_v1.py',
        '& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\LS_lcad_reviewer\intermediate\scripts\cv_workflow_experiments\refine_v2.py',
        '& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\LS_lcad_reviewer\intermediate\scripts\cv_workflow_experiments\summarize.py',
        '```'
    ])
    (out/'experiment_report.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    # Verify source labels and production deliverable remained byte-identical to run start.
    manifest=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
    source_matches={p:hashlib.sha256((ex.ROOT/p).read_bytes()).hexdigest()==sha for p,sha in manifest['source_files'].items()}
    assert all(source_matches.values()),source_matches
    assert len(profiles)==11428 and len(load_rows(out/'validation_pair_metrics.csv'))==2856
    assert len({r['image_id'] for r in lock})==48 and len(lock)==1584
    assert not ({r['image_id'] for r in rows if r['partition']=='development'} & {r['image_id'] for r in lock})
    assert len(list((sheets/'v2').glob('*.png')))==18
    checks={'source_hashes_match':source_matches,'gt_count':11428,'real_pair_count':2856,'new_lockbox_sources':48,'new_lockbox_cases':1584,
            'v2_preview_images':18,'rendered_images_visually_checked':8,'independent_visual_AB_executed':False,
            'test_split_used':False,'production_labels_changed':False}
    ex.save_json(out/'verification.json',checks)
    files=[p for p in out.iterdir() if p.is_file() and p.name!='output_hashes.json']+list((sheets/'v2').glob('*.png'))
    ex.save_json(out/'output_hashes.json',{str(p.relative_to(ex.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    print(json.dumps({'nearly_gray_gt':nearly_gray,'old_gt_gt8_exclusions':old_a_eligible_failure,'small_hue_p90_blind':p90_blind,'cascade':cascade,'verification':'PASS'},ensure_ascii=False,indent=2))
    print(out/'experiment_report.md')


if __name__=='__main__':main()
