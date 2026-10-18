"""Compare CV and external observations; accuracy requires explicit human references."""
import argparse
from pathlib import Path

import engine
from workflow import read_json,write_json,verify_sources,validate_reviews,utc


def tally(pairs):
    known=[(target,prediction) for target,prediction in pairs if target is not None and prediction is not None]
    tp=sum(t and p for t,p in known);fp=sum(not t and p for t,p in known)
    fn=sum(t and not p for t,p in known);tn=sum(not t and not p for t,p in known)
    return {'evaluated':len(known),'unresolved':len(pairs)-len(known),'tp':tp,'fp':fp,'fn':fn,'tn':tn,
            'precision':tp/(tp+fp) if tp+fp else None,'recall':tp/(tp+fn) if tp+fn else None}


def compare(manifest,visual,reference=None):
    ai=validate_reviews(manifest,visual);ref={}
    if reference is not None:
        if reference.get('schema_version')!='boundary_reference_v1':raise ValueError('Wrong reference version')
        entries=reference['reviews'];keys=[r['sample_key'] for r in entries]
        if len(keys)!=len(set(keys)) or set(keys)!=set(ai):raise ValueError('Reference must list each sample exactly once')
        for r in entries:
            if any(r.get(k) is not None and type(r[k]) is not bool for k in ['A','D']):raise ValueError('Reference A/D must be boolean or null')
            if any(r.get(k) is not None for k in ['A','D']) and (r.get('inspected') is not True or not r.get('evidence','').strip()):raise ValueError('Answered references need inspected=true and evidence')
            if r.get('A') is True and r.get('D') is True:raise ValueError('Terminal A cannot coexist with D')
            ref[r['sample_key']]=r
    rows=[]
    for item in manifest['records']:
        key=item['sample_key'];review=ai[key]
        resolved=review['decision']!='uncertain' and not review['uncertainties'] and not review['needs_crops']
        present={d['id'] for d in review['defects']}
        cv_a=item['cv_flags']['a_candidate'];cv_d=item['cv_flags']['d_candidate']
        row={'sample_key':key,'cv_A':cv_a,'cv_D':cv_d,'cv_D_after_A':cv_d and not cv_a,
             'visual_A':('A' in present) if resolved else None,
             'visual_D':('D' in present) if resolved else None,
             'visual_decision':review['decision'],'visual_defects':review['defects'],
             'uncertainties':review['uncertainties'],'needs_crops':review['needs_crops'],
             'reference_A':ref.get(key,{}).get('A'),'reference_D':ref.get(key,{}).get('D')}
        row['A_disagreement']=row['visual_A'] is not None and row['visual_A']!=cv_a
        row['D_disagreement']=row['visual_D'] is not None and row['visual_D']!=row['cv_D_after_A']
        rows.append(row)
    result={'created_at':utc(),'samples':len(rows),'GT_clusters':len({r.get('source_sample_key',r['sample_key']).split('/')[-1] for r in manifest['records']}),
            'visual_unresolved':sum(bool(r['visual_decision']=='uncertain' or r['uncertainties'] or r['needs_crops']) for r in rows),
            'A_disagreements':sum(r['A_disagreement'] for r in rows),'D_disagreements':sum(r['D_disagreement'] for r in rows),
            'warning':'CV-versus-AI agreement is not accuracy. Diagnostic selection is not representative.',
            'records':rows}
    if ref:
        result['human_reference_metrics']={name:tally([(r[target],r[prediction]) for r in rows]) for name,target,prediction in
                    [('CV_A','reference_A','cv_A'),('CV_D_cascade','reference_D','cv_D_after_A'),
                     ('visual_A','reference_A','visual_A'),('visual_D','reference_D','visual_D')]}
    return result


def write_start_instructions(run,manifest):
    policy=manifest['configuration']['visual_harness']
    if policy.get('mode')=='fast_single_pass':
        output_instruction=('从review_template.json创建reviews_gemini.json，保持schema_version和全部S编号；看过的null替换为缺陷数组或[]，缺陷只填id/severity/object/description，一句描述包括GT与生成差异。主要判断不成立可填uncertain原因。未看保留null。'
                            if policy.get('output_contract')=='compact' else '保持全部匿名sample_key及七类checked_categories，完成行inspection_complete=true。')
        reference_instruction='GT已由上游初筛确认可用，直接作为参考；这里只检查生成图七类缺陷，不重新判断GT资格、不移除样本或缩减类别。'
        instructions=f'''# 快速轻量标注：只看六组大图，一次完成

使用主人指定的gemini-3.8-flash-high。工作目录：{run}

1. 读取review_request.json、review_template.json和ANTIGRAVITY_HANDOFF.md。只打开请求列出的{len(manifest['sheets'])}张六组看板，按S001等匿名编号完成全部{len(manifest['records'])}行。
2. **速度第一：大图单次审查后直接写JSON。禁止查找/打开单张原图，禁止读manifest、任务池、数据目录或源码反查位置，禁止crop、补图、重复复核。小而模糊的细节跳过，标注明确可见的主要缺陷；不要为追求完美拖慢整批。**
3. A是全图颜色结构失败；C是具体物体相对GT明显换色相；主要褪色成浅灰白而未明显换色相优先E2，不因单纯褪色重复追加C；D是多物体/背景共同偏移；E1/E2绑定具体物体；B须看见越界，F须看见常识不自然。不跟随CV数值自动贴标签。
{reference_instruction}
4. 逐物体写短描述，evidence一句即可，不穷举小物体。A等级=""；非A按临时视觉规则给L1轻微、L2明显、L3强烈且影响主要主体/大面积，允许近似，后续迭代校准。只有主要判断也无法成立时才留uncertain；不因少量细节看不清就让整行待定。needs_crops固定[]。
5. 直接填写本地reviews_gemini.json。{output_instruction} 整批一次保存，不逐条反复修改，不在回复中返回JSON。不要读脚本、运行--help或自行编写重复校验；程序直接读取该文件完成后处理。
6. 保存JSON后结束，只回复文件已保存。不写长篇报告，不等待人工补图/逐项批准，不修改算法或导出正式数据。
'''
        (run/'START_HERE.md').write_text(instructions,encoding='utf-8');return
    instructions=f'''# 真实边界小试：交给Antigravity的任务

请在本批次使用主人指定的gemini-3.8-flash-high。工作目录：{run}。

读取本目录ANTIGRAVITY_HANDOFF.md、review_request.json和review_template.json，依次打开sheets内的{len(manifest['sheets'])}张看板，逐行完成全部{len(manifest['records'])}个样本的视觉审核。每张6组，分别对照GT、生成图和双向彩度差。只依据图像和本次中性遥测；不要读取manifest、screen或selection文件中的候选/旧标签/旧分数。

重点独立观察：全图颜色结构失败还是强欠饱和；多个物体/背景共同偏移还是单个物体换色；同图不同物体的彩度变化。CV数值不是答案。检查全部七类，具体物体分别记录；非A严重度尚未锚定时填null，不能为了导出猜等级。

从模板另存reviews_gemini.json，保留每个匿名sample_key（S001等）。每行填写inspection_complete、checked_categories、decision、defects、uncertainties和needs_crops。证据不足时留uncertain，不能假装完成。A的severity必须为空字符串，其他标签等级可暂留null。

**效率硬约束：只打开review_request列出的六组大看板，禁止查找或逐张打开原始GT/模型图片，禁止读取manifest/任务池/数据目录来反查编号，也禁止调用逐图crop或自行写裁剪脚本。先完成全部大图的所有行，不能边看一行边跳到原图复读。**

仅当具体物体确因尺寸太小无法辨认时，填needs_crops=[{{"sample_key":"S001","bbox":[0.1,0.1,0.3,0.3],"reason":"说明看不清的具体物体"}}]；每样本最多一个局部请求，不请求整幅图。不要把一般标签分歧当作看不清。先保存完整初稿，然后自动执行以下命令，无需等待主人/洛熙补图：

```powershell
& "{engine.ROOT/'LS_lcad_reviewer/.venv/Scripts/python.exe'}" -B -X utf8 "{Path(__file__).with_name('workflow.py')}" build-detail-sheets --batch "{run}" --reviews "{run/'reviews_gemini.json'}"
```

程序自动汇总局部GT/模型/彩度差为六组看板，不向你提供原图路径。只读取命令返回的detail看板，更新完整reviews_gemini.json，删除已解决的needs_crops。最多{policy['maximum_detail_rounds']}轮、每轮{policy['maximum_detail_samples_per_round']}个局部样本，局部框≤全图{policy['maximum_detail_bbox_fraction']:.0%}，拒绝整图请求；超预算或仍无法确定的项保留uncertain后自动结束，不再查原图、不等待人工介入。未请求局部补充时不要执行命令。

只交回这份JSON，不导出正式数据、不修改CV代码或参数。本次视觉审查不依赖人工补图；人工参考是后续算法评价的独立过程。
'''
    (run/'START_HERE.md').write_text(instructions,encoding='utf-8')


def init(run,manifest):
    target=run/'master_reference_template.json'
    if target.exists():raise ValueError('Reference template already exists')
    write_json(target,{'schema_version':'boundary_reference_v1','reviewer':'主人',
               'warning':'Only fill after personal inspection; model suggestions do not become human truth automatically.',
               'reviews':[{'sample_key':r['sample_key'],'inspected':False,'A':None,'D':None,'evidence':''} for r in manifest['records']]})
    write_start_instructions(run,manifest);print(run/'START_HERE.md')


def main():
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('init');p.add_argument('--batch',type=Path,required=True)
    p=sub.add_parser('compare');p.add_argument('--batch',type=Path,required=True);p.add_argument('--reviews',type=Path,required=True);p.add_argument('--reference',type=Path)
    args=parser.parse_args();run=args.batch.resolve();manifest=verify_sources(run)
    if args.command=='init':init(run,manifest);return
    result=compare(manifest,read_json(args.reviews),read_json(args.reference) if args.reference else None)
    result['reviews_sha256']=engine.sha256(args.reviews)
    if args.reference:result['reference_sha256']=engine.sha256(args.reference)
    directory=run/'boundary_assessments';directory.mkdir(exist_ok=True)
    target=directory/(utc().replace(':','-')+'.json');write_json(target,result)
    print({k:v for k,v in result.items() if k!='records'});print(target)


if __name__=='__main__':main()
