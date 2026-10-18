"""User-authorized one-parameter previews on all real non-A visual pairs.

Population statistics plus numbered examples; never applies a parameter choice.
"""
import argparse
import csv
import copy
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from pathlib import Path
import time

import cv2
import numpy as np
from PIL import Image,ImageDraw

import engine
import color_evidence
from workflow import OUTPUT,read_json,write_json,utc,align,font


VARIANTS=[('q90','selection_quantile',90),('base','selection_quantile',95),
          ('q98','selection_quantile',98),('area4','minimum_area_pixels',4),
          ('area16','minimum_area_pixels',16)]


def candidate_mask(signal,settings,percentile_cache):
    q=settings['selection_quantile']
    if q not in percentile_cache:
        threshold=max(settings['minimum_signal'],float(np.percentile(signal,q)))
        count,labels,stats,_=cv2.connectedComponentsWithStats((signal>threshold).astype(np.uint8),connectivity=8)
        # Area * component mean is the component signal sum.
        sums=np.bincount(labels.ravel(),weights=signal.ravel(),minlength=count)
        percentile_cache[q]=(threshold,labels,stats,sums)
    threshold,labels,stats,sums=percentile_cache[q]
    valid=[i for i in range(1,len(stats)) if stats[i,cv2.CC_STAT_AREA]>=settings['minimum_area_pixels']]
    selected=sorted(valid,key=lambda i:sums[i],reverse=True)[:settings['maximum_regions']]
    mask=np.isin(labels,selected)
    return mask,{'regions':len(selected),'selected_pixel_fraction':float(mask.mean()),'cutoff':threshold}


def load_pair(record,cfg):
    gt=engine.read_rgb(engine.ROOT/record['gt_path'])
    gen=align(gt,engine.read_rgb(engine.ROOT/record['model_path']))
    return gt,gen,engine.lab(gt),engine.lab(gen)


def select_examples(rows,family,maximum=12):
    score_key='q_change_fraction' if family=='quantile' else 'area_change_fraction'
    ordered=sorted((r for r in rows if r[score_key]>0),key=lambda r:r[score_key],reverse=True)
    chosen=[];used=set()
    def add(r):
        gt_key=(r['split'],r['image_id'])
        if gt_key not in used:
            chosen.append(r);used.add(gt_key)
    for split in ['train','val','test']:
        for model in ['lcad','unicolor']:
            item=next((r for r in ordered if r['split']==split and r['model']==model and (r['split'],r['image_id']) not in used),None)
            if item:add(item)
    for r in ordered:
        if len(chosen)>=maximum:break
        add(r)
    return chosen[:maximum]


def render_examples(rows,family,out,cfg):
    settings=cfg['color_evidence'];variants=['q90','base','q98'] if family=='quantile' else ['area4','base','area16']
    labels=['P90','P95 当前','P98'] if family=='quantile' else ['面积≥4','面积≥8 当前','面积≥16']
    cards=[];sheets=[]
    for start in range(0,len(rows),6):
        chunk=rows[start:start+6];canvas=Image.new('RGB',(1800,80+len(chunk)*350),(239,242,246));draw=ImageDraw.Draw(canvas)
        draw.text((18,12),'C参数人工选择 · '+('选区百分位' if family=='quantile' else '最小连通面积'),font=font(25),fill=(25,43,60))
        draw.text((18,49),'左GT / 生成图；后三列仅改变一项参数。彩度增红减蓝，橙轮廓是候选，不是标签。',font=font(17),fill=(65,75,85))
        for row,r in enumerate(chunk):
            top=80+row*350;number=start+row+1
            draw.rectangle((8,top+4,1792,top+346),fill='white',outline=(203,211,220))
            draw.text((18,top+10),f"{'Q' if family=='quantile' else 'M'}{number:03d}",font=font(23),fill=(25,43,60))
            gt,gen,gl,ml=load_pair(r,cfg);heat=engine.heatmap(gl,ml,cfg['display']);images=[gt,gen]
            for key in variants:
                variant=next(v for v in VARIANTS if v[0]==key);params={**settings,variant[1]:variant[2]}
                images.append(color_evidence.outline(heat,gl,ml,params))
            for col,(pixels,label) in enumerate(zip(images,['GT','生成图',*labels])):
                left=18+col*355;draw.text((left,top+44),label,font=font(18),fill=(50,60,72))
                im=Image.fromarray(pixels);im.thumbnail((338,265),Image.Resampling.LANCZOS)
                canvas.paste(im,(left+(338-im.width)//2,top+74+(265-im.height)//2))
            cards.append({'example_id':f"{'Q' if family=='quantile' else 'M'}{number:03d}",'source_sample_key':r['sample_key'],
                          'split':r['split'],'model':r['model'],'selection_reason':'large mask difference with split/model diversity; not representative accuracy examples',
                          'variants':{key:r['variants'][key] for key in variants}})
        path=f'sheets/{family}_{len(sheets)+1:02d}.png';canvas.save(out/path)
        sheets.append({'path':path,'examples':[r['example_id'] for r in cards[-len(chunk):]],'size':list(canvas.size),'sha256':engine.sha256(out/path)})
    return {'examples':cards,'sheets':sheets}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-id',required=True);parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args();cfg_path=Path(__file__).with_name('config.json');cfg=read_json(cfg_path);cfg_hash=engine.sha256(cfg_path)
    source=OUTPUT/'full_GT_reference_calibration_20261014_01/visual_pair_records.json';pairs=read_json(source)
    fixed_path=engine.ROOT/cfg['a']['confirmed_manifest'];fixed={r['source_sample_key'] for r in read_json(fixed_path)['records'] if r['GT_eligible']}
    assert len(pairs)==28302 and not any(r['sample_key'] in fixed for r in pairs)
    out=OUTPUT/args.run_id;(out/'sheets').mkdir(parents=True);(out/'config_snapshot.json').write_bytes(cfg_path.read_bytes())
    groups=defaultdict(list)
    for r in pairs:groups[(r['split'],r['sample_key'].split('/')[-1])].append(r)
    write_json(out/'manifest.json',{'created_at':utc(),'state':'running','visual_pairs':len(pairs),'source_GT':len(groups),
        'configuration':cfg,'variants':VARIANTS,'source_sha256':{str(p.relative_to(engine.ROOT)):engine.sha256(p) for p in [cfg_path,source,fixed_path,Path(__file__),Path(color_evidence.__file__),Path(engine.__file__)]},
        'one_parameter_at_a_time':True,'new_native_calls':0,'main_configuration_not_modified':True})
    cv2.setNumThreads(1);started=time.monotonic()
    def measure(item):
        (split,image_id),rr=item;gp=engine.ROOT/cfg['datasets'][split]/'image'/f'{image_id}.jpg'
        gt=engine.read_rgb(gp);gl=engine.lab(gt);h,w=gt.shape[:2];ratio=min(1,cfg['color_evidence']['max_side']/max(h,w));size=(round(w*ratio),round(h*ratio))
        sg=cv2.resize(gl,size,interpolation=cv2.INTER_AREA);result=[]
        for r in rr:
            gen=align(gt,engine.read_rgb(engine.ROOT/r['model_path']));ml=engine.lab(gen);sm=cv2.resize(ml,size,interpolation=cv2.INTER_AREA)
            signal=color_evidence.measure(sg,sm,cfg['color_evidence'])['retained_hue'];cache={};masks={};stats={}
            for key,parameter,value in VARIANTS:
                masks[key],stats[key]=candidate_mask(signal,{**cfg['color_evidence'],parameter:value},cache)
            for key in stats:
                stats[key]['change_from_baseline_fraction']=float(np.logical_xor(masks[key],masks['base']).mean())
                stats[key]['candidate_added']=stats[key]['regions']>0 and stats['base']['regions']==0
                stats[key]['candidate_removed']=stats[key]['regions']==0 and stats['base']['regions']>0
            result.append({'sample_key':r['sample_key'],'split':split,'model':r['model'],'image_id':image_id,
                           'gt_path':str(gp.relative_to(engine.ROOT)),'model_path':r['model_path'],'analysis_size':list(size),
                           'variants':stats,'q_change_fraction':float(np.logical_xor(masks['q90'],masks['q98']).mean()),
                           'area_change_fraction':float(np.logical_xor(masks['area4'],masks['area16']).mean())})
        return result
    rows=[]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for i,result in enumerate(pool.map(measure,groups.items()),1):
            rows.extend(result)
            if i%1000==0:print(f'C parameter statistics: {i}/{len(groups)} GT; {len(rows)} pairs',flush=True)
    assert len(rows)==len(pairs) and len({r['sample_key'] for r in rows})==len(pairs)
    write_json(out/'records.json',rows)
    def summarize(rr):
        table=[]
        for key,parameter,value in VARIANTS:
            ss=[r['variants'][key] for r in rr];n=len(rr)
            table.append({'variant':key,'parameter':parameter,'value':value,'images':n,
                'candidate_images':sum(s['regions']>0 for s in ss),'candidate_image_percent':100*sum(s['regions']>0 for s in ss)/n,
                'mean_regions':float(np.mean([s['regions'] for s in ss])),
                'mean_selected_pixel_percent':100*float(np.mean([s['selected_pixel_fraction'] for s in ss])),
                'changed_images':sum(s['change_from_baseline_fraction']>0 for s in ss),
                'changed_image_percent':100*sum(s['change_from_baseline_fraction']>0 for s in ss)/n,
                'mean_changed_pixel_percent':100*float(np.mean([s['change_from_baseline_fraction'] for s in ss])),
                'candidate_added_images':sum(s['candidate_added'] for s in ss),'candidate_removed_images':sum(s['candidate_removed'] for s in ss)})
        return table
    table=summarize(rows)
    summary={'created_at':utc(),'state':'awaiting_user_parameter_choice','scope':'all 28302 GT-eligible non-A real visual pairs',
        'visual_pairs':len(rows),'source_GT':len(groups),'table':table,
        'by_split':{s:summarize([r for r in rows if r['split']==s]) for s in cfg['datasets']},
        'by_model':{m:summarize([r for r in rows if r['model']==m]) for m in ['lcad','unicolor']},
        'population_coverage_not_semantic_accuracy':True,'selection_is_not_semantic_object_segmentation':True,
        'rendering_measurement':'same full-resolution Lab then Lab resize <=256 as production outline renderer',
        'numeric_optimization':'component area times mean ranked by equivalent component signal sum',
        'fixed_low_chroma_reference':cfg['color_evidence']['reference_low_chroma'],'fixed_display_maximum':cfg['display']['maximum'],
        'elapsed_statistics_seconds':round(time.monotonic()-started,2),'new_native_calls':0,'labels_unchanged':True,
        'main_config_sha256_before':cfg_hash,'main_config_sha256_after':engine.sha256(cfg_path)}
    with (out/'statistics.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=table[0].keys());writer.writeheader();writer.writerows(table)
    with (out/'by_split_statistics.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['split',*table[0].keys()]);writer.writeheader()
        for split,tt in summary['by_split'].items():writer.writerows({'split':split,**r} for r in tt)
    previews={family:render_examples(select_examples(rows,family),family,out,cfg) for family in ['quantile','area']}
    write_json(out/'preview_manifest.json',previews);write_json(out/'summary.json',summary)
    build_report(out,summary,previews)
    manifest=read_json(out/'manifest.json');manifest['state']='awaiting_user_parameter_choice';write_json(out/'manifest.json',manifest)
    print(table,flush=True);print(out,flush=True)


def build_report(out,summary,previews):
    import html
    import json
    table=summary['table'];tr=''.join(f"<tr><td>{r['variant']}</td><td>{r['candidate_images']:,} / {r['candidate_image_percent']:.2f}%</td><td>{r['mean_selected_pixel_percent']:.3f}%</td><td>{r['changed_image_percent']:.2f}%</td><td>+{r['candidate_added_images']} / −{r['candidate_removed_images']}</td></tr>" for r in table)
    gallery=''.join(f'<section><h2>{"选区百分位：P90 / P95 / P98" if family=="quantile" else "最小面积：4 / 8 / 16像素"}</h2><p>固定另一项为当前值；从全量中选变化明显的案例，兼顾三个split与两个模型。案例编号仅在本展示中使用。</p>'+''.join(f'<a href="{s["path"]}" target="_blank"><img loading="lazy" src="{s["path"]}"></a>' for s in data['sheets'])+'</section>' for family,data in previews.items())
    page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>C参数分档选择</title>
<style>body{{font-family:"Microsoft YaHei",sans-serif;background:#eef2f6;color:#1c3043;margin:24px auto;max-width:1450px;padding:0 22px}}section,.panel{{background:white;border-radius:12px;padding:22px;margin:20px 0}}table{{border-collapse:collapse;width:100%;background:white}}th,td{{padding:12px;border-bottom:1px solid #dce3eb;text-align:left}}img{{width:100%;display:block;margin:18px 0;border:1px solid #dce3eb}}p{{line-height:1.75}}select,button,textarea{{font:inherit;padding:10px;margin:6px}}textarea{{width:85%}}.note{{color:#526476}}</style>
<h1>C橙轮廓：参数分档展示</h1><p>全部28,302条非A视觉样本。每次只改一项；当前P95、面积≥8，最多两区域。全量低彩度参照{summary['fixed_low_chroma_reference']:.6f}、热图上限{summary['fixed_display_maximum']:.6f}固定。没有调用Gemini、改标签或改主配置。</p>
<div class="panel"><h2>全量统计</h2><p class="note">候选图片比例=至少一个橙轮廓区域的图片数/全部样本。区域比例=被选区域像素占比的逐图平均，并非橙线描边占比。变化图片比例=相对当前档候选掩膜发生变化。它们都不是错色率、准确率或召回率。</p>
<table><thead><tr><th>档位</th><th>候选图片 / 比例</th><th>平均候选区域比例</th><th>相对当前档变化图片</th><th>新增 / 消失候选图片</th></tr></thead><tbody>{tr}</tbody></table>
<p>q90=P90/面积8；base=P95/面积8；q98=P98/面积8；area4=P95/面积4；area16=P95/面积16。</p><p><a href="statistics.csv">全量CSV</a> · <a href="by_split_statistics.csv">分数据集CSV</a> · <a href="summary.json">统计记录</a></p></div>
{gallery}<div class="panel"><h2>你的选择</h2><p>选择后生成回复文字，复制发给洛熙。此页面不会修改项目配置；两项联合选择尚未作为组合运行。</p>
<label>百分位 <select id="q"><option>90</option><option selected>95</option><option>98</option></select></label>
<label>最小面积 <select id="a"><option>4</option><option selected>8</option><option>16</option></select></label><button onclick="makeChoice()">生成选择文字</button><br><textarea id="reply" rows="2" readonly></textarea></div>
<script>function makeChoice(){{document.getElementById('reply').value='C橙轮廓：选区百分位P'+document.getElementById('q').value+'，最小面积'+document.getElementById('a').value+'像素。';}}makeChoice();</script></html>'''
    (out/'index.html').write_text(page,encoding='utf-8')
    lines=['# C橙轮廓：人工参数选择','',f"全量{summary['visual_pairs']:,}条非A视觉样本，{summary['source_GT']:,}张对应GT；A名单和主配置未改。打开index.html看统计和并排PNG。",'',
           'P90/P95/P98固定面积8；面积4/8/16固定P95。仅单参数分档，没有联合矩阵或合成控制。使用当前生产outline的Lab缩放口径；候选数量/面积不是语义缺陷率。','',
           '| 档位 | 候选图片比例 | 平均选区占比 | 变化图片比例 |','|---|---:|---:|---:|']
    lines += [f"| {r['variant']} | {r['candidate_image_percent']:.2f}% | {r['mean_selected_pixel_percent']:.3f}% | {r['changed_image_percent']:.2f}% |" for r in table]
    lines+=['','每个参数挑最多12条变化明显的案例，并兼顾train/val/test及LCAD/Unicolor；不展示旧标签，案例选择有意富集变化，不能当随机准确率样本。序号Q/M只用于此展示，身份对应在preview_manifest.json。','',
            '等待主人决定档位后再应用。主配置前后SHA256记录在summary.json，源配置和代码哈希在manifest.json；每条/每档统计在records.json，无新标签或模型调用。']
    (out/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


if __name__=='__main__':main()
