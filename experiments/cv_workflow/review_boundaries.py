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
             'visual_A':('A' in present) if resolved else None,'visual_D':('D' in present) if resolved else None,
             'visual_decision':review['decision'],'visual_defects':review['defects'],
             'uncertainties':review['uncertainties'],'needs_crops':review['needs_crops'],
             'reference_A':ref.get(key,{}).get('A'),'reference_D':ref.get(key,{}).get('D')}
        row['A_disagreement']=row['visual_A'] is not None and row['visual_A']!=cv_a
        row['D_disagreement']=row['visual_D'] is not None and row['visual_D']!=row['cv_D_after_A']
        rows.append(row)
    result={'created_at':utc(),'samples':len(rows),'GT_clusters':len({r['sample_key'].split('/')[-1] for r in rows}),
            'visual_unresolved':sum(r['visual_A'] is None for r in rows),
            'A_disagreements':sum(r['A_disagreement'] for r in rows),'D_disagreements':sum(r['D_disagreement'] for r in rows),
            'warning':'CV-versus-AI agreement is not accuracy. Diagnostic selection is not representative.',
            'records':rows}
    if ref:
        result['human_reference_metrics']={name:tally([(r[target],r[prediction]) for r in rows]) for name,target,prediction in
                    [('CV_A','reference_A','cv_A'),('CV_D_cascade','reference_D','cv_D_after_A'),
                     ('visual_A','reference_A','visual_A'),('visual_D','reference_D','visual_D')]}
    return result


def init(run,manifest):
    target=run/'master_reference_template.json'
    if target.exists():raise ValueError('Reference template already exists')
    write_json(target,{'schema_version':'boundary_reference_v1','reviewer':'主人',
               'warning':'Only fill after personal inspection; model suggestions do not become human truth automatically.',
               'reviews':[{'sample_key':r['sample_key'],'inspected':False,'A':None,'D':None,'evidence':''} for r in manifest['records']]})
    instructions=f'''# 真实边界小试：交给Antigravity的任务

请在本批次使用主人指定的gemini-3.8-flash-high。工作目录：{run}。

读取本目录ANTIGRAVITY_HANDOFF.md、review_request.json和review_template.json，依次打开sheets内的{len(manifest['sheets'])}张看板，逐行完成全部{len(manifest['records'])}个样本的视觉审核。每张6组，分别对照GT、生成图和双向彩度差。只依据图像和本次中性遥测；不要读取manifest、screen或selection文件中的候选/旧标签/旧分数。

重点独立观察：全图颜色结构失败还是强欠饱和；多个物体/背景共同偏移还是单个物体换色；同图不同物体的彩度变化。CV数值不是答案。检查全部七类，具体物体分别记录；非A严重度尚未锚定时填null，不能为了导出猜等级。

从模板另存reviews_gemini.json，保留每个完整sample_key。每行填写inspection_complete、checked_categories、decision、defects、uncertainties和needs_crops。证据不足时留uncertain和裁剪请求，不能假装完成。A的severity必须为空字符串，其他标签等级可暂留null。

只交回这份JSON，不导出正式数据、不修改CV代码或参数。若请求裁剪，先返回needs_crops，我会生成对应GT/模型二联图后继续。

主人暂时只需运行这次视觉任务，并告诉洛熙JSON已保存。master_reference_template.json留待洛熙筛出分歧后由主人亲自核对；先不需要全量人工标注。人工参考只确认A/D是否存在，可保持未判项为null。
'''
    (run/'START_HERE.md').write_text(instructions,encoding='utf-8');print(run/'START_HERE.md')


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
