"""Scan every split's GT, inspect candidates once, exclude before any colorization labeling."""
import argparse
import copy
import csv
import json
import math
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path

import cv2
import numpy as np
from PIL import Image,ImageDraw

import engine
from global_models import color_curve_residual
from workflow import OUTPUT,read_json,write_json,font,utc,verify_sources


def settings():return read_json(Path(__file__).with_name('gt_quality_screen_config.json'))


def features(path,config):
    rgb=engine.read_rgb(path,config['max_side']);lab=engine.lab(rgb);c=engine.chroma(lab);ab=lab[...,1:]
    return {'mean_chroma':float(c.mean()),'p95_chroma':float(np.percentile(c,95)),
            'hue_concentration':float(np.linalg.norm(ab.sum(axis=(0,1)))/(c.sum()+1e-8)),
            'curve_residual':color_curve_residual(lab,config['curve_bins'],config['curve_stride'])['p95']}


def scan(run):
    config=settings();cv2.setNumThreads(1);cfg=read_json(Path(__file__).with_name('config.json'))
    run.mkdir();rows=[];sources={}
    for split in config['splits']:
        pool=next((engine.ROOT/'LS_lcad_reviewer/tasks_pool'/split).glob('*lcad*.json'))
        sources[str(pool.relative_to(engine.ROOT))]=engine.sha256(pool)
        for task in read_json(pool):
            stem=Path(task['data']['original_record']['image_id']).stem
            path=engine.ROOT/cfg['datasets'][split]/'image'/f'{stem}.jpg'
            rows.append({'split':split,'image_id':stem,'gt_path':str(path.relative_to(engine.ROOT))})
    def measure(row):
        path=engine.ROOT/row['gt_path']
        return {**row,**features(path,config),'gt_sha256':engine.sha256(path)}
    started=time.monotonic()
    with ThreadPoolExecutor(max_workers=4) as pool:
        measured=[]
        for i,row in enumerate(pool.map(measure,rows),1):
            measured.append(row)
            if i%1000==0:print(f'CV GT profiles {i}/{len(rows)}',flush=True)
    prior=[r for r in measured if r['split']==config['calibration_split']]
    quantiles=config['candidate_percentiles']
    cuts={'mean_chroma':float(np.percentile([r['mean_chroma'] for r in prior],quantiles['low_mean_chroma'])),
          'curve_residual':float(np.percentile([r['curve_residual'] for r in prior],quantiles['low_curve_residual'])),
          'hue_concentration':float(np.percentile([r['hue_concentration'] for r in prior],quantiles['high_hue_concentration']))}
    candidates=[]
    for row in measured:
        reasons=[name for name,hit in [('low_mean_chroma',row['mean_chroma']<=cuts['mean_chroma']),
                 ('low_curve_residual',row['curve_residual']<=cuts['curve_residual']),
                 ('high_hue_concentration',row['hue_concentration']>=cuts['hue_concentration'])] if hit]
        row['candidate_reasons']=reasons
        if reasons:candidates.append(row)
    write_json(run/'profiles.json',{'records':measured})
    write_json(run/'candidate_selection.json',{'records':candidates})
    write_json(run/'scan.json',{'created_at':utc(),'configuration':config,'calibrated_cutoffs':cuts,'source_task_sha256':sources,
        'GT_count':len(measured),'candidate_GT_count':len(candidates),'elapsed_seconds':round(time.monotonic()-started,2),
        'splits':{s:{'GT':sum(r['split']==s for r in measured),'candidates':sum(r['split']==s for r in candidates)} for s in config['splits']},
        'interpretation':'All GT received CV screening; only candidates receive visual confirmation. Noncandidates are retained provisionally, not certified perfect.'})
    (run/'screen_source.py').write_bytes(Path(__file__).read_bytes());print(read_json(run/'scan.json'),flush=True)


def prepare(run):
    rows=read_json(run/'candidate_selection.json')['records'];groups={}
    for row in rows:
        group=groups.setdefault(row['gt_sha256'],{'gt_path':row['gt_path'],'gt_sha256':row['gt_sha256'],'members':[]})
        group['members'].append({'split':row['split'],'image_id':row['image_id'],'kind':'dataset'})
    # Controls and already inspected difficult negatives remain internal, never disclosed to Gemini.
    diagnostic=read_json(OUTPUT/'gt_reference_round14_BF36_20261013/manifest.json')
    for row in diagnostic['records']:
        group=groups.setdefault(row['gt_sha256'],{'gt_path':row['gt_path'],'gt_sha256':row['gt_sha256'],'members':[]})
        diag=row['diagnostic'];member={'kind':diag['kind'],'expected_GT_untrusted':diag['expected_GT_untrusted'],'case':diag['case']}
        if diag['kind']=='host_visual_diagnostic':
            member.update(split=row['split'],image_id=Path(row['gt_path']).stem)
        group['members'].append(member)
    groups=list(groups.values())
    for i,g in enumerate(groups,1):g['gt_key']=f'G{i:04d}'
    (run/'sheets').mkdir();sheets=[]
    for start in range(0,len(groups),6):
        chunk=groups[start:start+6];canvas=Image.new('RGB',(1560,1440),(240,242,245));draw=ImageDraw.Draw(canvas)
        for i,g in enumerate(chunk):
            left=(i%2)*780;top=(i//2)*480
            draw.rectangle((left+8,top+8,left+772,top+472),fill='white',outline=(205,210,215))
            draw.text((left+18,top+15),g['gt_key']+'  GT',font=font(22),fill='black')
            image=Image.open(engine.ROOT/g['gt_path']).convert('RGB');image.thumbnail((740,414),Image.Resampling.LANCZOS)
            canvas.paste(image,(left+(780-image.width)//2,top+50+(414-image.height)//2))
            g['sheet']=f'sheets/GT_sheet_{len(sheets)+1:03d}.png'
        path=run/'sheets'/f'GT_sheet_{len(sheets)+1:03d}.png';canvas.save(path)
        sheets.append({'path':str(path.relative_to(run)),'sha256':engine.sha256(path),'keys':[g['gt_key'] for g in chunk]})
    write_json(run/'GT_manifest.json',{'groups':groups,'sheets':sheets,'configuration':settings(),'created_at':utc()})
    print('Prepared',len(groups),'unique candidate/control GT;',len(sheets),'six-group boards',flush=True)


def validate(entries,keys):
    if set(entries)!=set(keys):raise ValueError('GT file must cover each assigned anonymous key exactly once')
    for key,value in entries.items():
        if value=='keep':continue
        if not isinstance(value,dict) or value.get('exclude') not in ['black_and_white','abnormal_global_cast']:
            raise ValueError(f'Incomplete/invalid GT decision {key}')
        if value['exclude']=='abnormal_global_cast' and not value.get('evidence','').strip():raise ValueError('GT cast needs short scene evidence')


def prompt(listing,target):
    return ('你是快速GT质量筛选器，不做上色标注。自行用图片工具读取下列本地GT看板，每张6组，只读一次。'
        '只填写下面列出的G编号，图上其他编号不处理。允许读取指定看板及读写指定结果文件；禁止查原图、其他目录、源码、manifest，禁止命令、裁剪、补图或复核。'
        '默认保留，拿不准保留；只剔除两类：1黑白照片且主体物体没有有效颜色参考；2明显异常整体色偏，'
        '跨不同材质物体/中性色共同污染，正常场景光照不能解释。正常低饱和、白灰物体、阴天、夕阳、夜景、舞台彩灯、'
        '雪景、水下环境、单色物体主导或复古色调不单独触发。黑白占比很大但主体红伞、蓝绿玩具、蓝箱包等仍明确有颜色时保留；'
        '黑白旧照片的扫描边框/装订孔着色不算主体颜色。主体没鲜艳颜色不等于经过黑白处理；'
        '灰白物体、雾霾剪影、冷暖环境光可造成单调颜色，不能确认黑白处理时保留；颜色对照拼图不能当全图异常色偏。'
        '候选不等于低质量，不按比例凑剔除数量。'
        f'直接一次填写本地JSON文件 {target}，保留schema_version及decisions全部G编号。'
        '每个null改为"keep"或{"exclude":"black_and_white"}，整体异常色偏用'
        '{"exclude":"abnormal_global_cast","evidence":"一句跨物体异常并排除正常光照的依据"}。'
        '保留项无需描述，不标任何A/B/C/D/E/F，不写报告。保存后只回复文件已保存，不返回JSON。\n'+listing)


def run_jobs(run,workers,retry=False,timeout_override=None):
    manifest=read_json(run/'GT_manifest.json');config=manifest['configuration']
    previous=read_json(run/'GT_job_results.json') if retry else None
    if not retry:(run/'jobs').mkdir()
    prior={r['job']:r for r in previous['jobs']} if retry else {}
    recovered=[]
    if retry:
        for r in previous['jobs']:
            if r['state']=='complete':continue
            directory=run/r.get('attempt_directory',f'jobs/{r["job"]}')
            entries=read_json(directory/'GT_decisions.json')['decisions'];valid={}
            for key,value in entries.items():
                try:validate({key:value},[key])
                except ValueError:continue
                valid[key]=value
            if valid:
                recovered.append({'job':r['job']+'_file_recovered','state':'complete','GT':len(valid),'decisions':valid,
                                  'completion_basis':'Validated non-null per-GT file decisions before interrupted CLI completion'})
    known={k:v for r in ([r for r in previous['jobs'] if r['state']=='complete']+recovered if retry else []) for k,v in r['decisions'].items()}
    agy=Path.home()/'AppData/Local/agy/bin/agy.exe';jobs=[]
    for start in range(0,len(manifest['sheets']),config['sheets_per_job']):
        sheets=manifest['sheets'][start:start+config['sheets_per_job']]
        job_key=f'job_{start//config["sheets_per_job"]+1:03d}';child=run/'jobs'/job_key
        keys=[k for s in sheets for k in s['keys'] if k not in known]
        if retry:
            if not keys:continue
            child=child/f'attempt_{len(list(child.glob("attempt_*")))+2:02d}'
        child.mkdir()
        target=child/'GT_decisions.json'
        write_json(target,{'schema_version':'gt_quality_v1','decisions':dict.fromkeys(keys)})
        listing='\n'.join(str(run/s['path'])+': '+', '.join(k for k in s['keys'] if k in keys) for s in sheets if set(s['keys'])&set(keys))
        text=prompt(listing,target);(child/'prompt.txt').write_text(text,encoding='utf-8');jobs.append((child,keys,text,job_key))
    started=time.monotonic();results=[]
    def call(job):
        child,keys,text,job_key=job;begin=time.monotonic();offset=begin-started
        timeout=timeout_override or config['timeout_seconds']
        process=subprocess.Popen([str(agy),'-p',text,'--model','gemini-3.8-flash-high','--mode','accept-edits',
            '--dangerously-skip-permissions','--output-format','json','--print-timeout',f'{timeout}s','--log-file',str(child/'client.log')],
            cwd=child,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        write_json(child/'launch.json',{'agy_pid':process.pid,'started_at':utc(),'start_offset_seconds':round(offset,2),'image_input':'self-read local boards; no image attachments'})
        try:
            stdout,stderr=process.communicate(timeout=timeout+20)
        except subprocess.TimeoutExpired:
            process.kill();stdout,stderr=process.communicate()
        (child/'stdout.json').write_bytes(stdout);(child/'stderr.txt').write_bytes(stderr)
        result={'job':job_key,'attempt_directory':str(child.relative_to(run)),
                'elapsed_seconds':round(time.monotonic()-begin,2),'start_offset_seconds':round(offset,2),'GT':len(keys),'agy_pid':process.pid}
        try:
            envelope=json.loads(stdout.decode('utf-8-sig'))
            if envelope.get('status')!='SUCCESS':raise ValueError(envelope.get('error','Model did not complete'))
            entries=read_json(child/'GT_decisions.json')['decisions'];validate(entries,keys)
            result.update(state='complete',usage=envelope.get('usage'),decisions=entries)
        except (ValueError,KeyError) as error:result.update(state='failed',error=str(error))
        write_json(child/'result.json',result);print(job_key,result['state'],result['elapsed_seconds'],flush=True)
        return result
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures=[pool.submit(call,job) for job in jobs]
        for future in as_completed(futures):results.append(future.result())
    if retry:
        attempt=len(list(run.glob('GT_job_results_attempt*.json')))+1
        write_json(run/f'GT_job_results_attempt{attempt:02d}.json',previous)
        results=[r for r in previous['jobs'] if r['state']=='complete']+recovered+results
    write_json(run/'GT_job_results.json',{'elapsed_seconds':round(time.monotonic()-started,2),'workers':workers,'jobs':results,
               'timing_scope':'retry phase only' if retry else 'initial full candidate queue'})
    export_filter(run)


def export_filter(run):
    manifest=read_json(run/'GT_manifest.json');results=read_json(run/'GT_job_results.json')
    decisions={k:v for r in results['jobs'] if r['state']=='complete' for k,v in r['decisions'].items()}
    corrections=read_json(run/'GT_review_corrections.json')['corrections'] if (run/'GT_review_corrections.json').exists() else {}
    for key,correction in corrections.items():
        if key not in decisions:raise ValueError('Only completed GT decisions may receive a review correction')
        decisions[key]=correction['decision']
    excluded=[];unresolved=[];diagnostics=[]
    for group in manifest['groups']:
        value=decisions.get(group['gt_key'])
        for member in group['members']:
            if member['kind']=='dataset' or member['kind']=='host_visual_diagnostic':
                if value is None:unresolved.append({**member,'gt_key':group['gt_key']})
                elif isinstance(value,dict):excluded.append({**member,'gt_sha256':group['gt_sha256'],'reason':value['exclude'],'evidence':value.get('evidence','')})
            if 'expected_GT_untrusted' in member:
                diagnostics.append({**member,'gt_key':group['gt_key'],'decision':value})
    unique={(r['split'],r['image_id']):r for r in excluded};excluded=list(unique.values())
    counts={s:sum(r['split']==s for r in excluded) for s in settings()['splits']}
    result={'created_at':utc(),'excluded_GT':excluded,'excluded_unique_GT':len(excluded),'excluded_by_split':counts,
            'unresolved':unresolved,'visual_candidate_GT':len(manifest['groups']),
            'completed_GT':len(decisions),'failed_jobs':[r['job'] for r in results['jobs'] if r['state']!='complete'],
            'review_corrections':corrections,
            'policy':'exclude corresponding images for every model; do not label untrusted GT',
            'coverage':'Full CV screening; visual confirmation of candidates and controls only'}
    write_json(run/'excluded_GT.json',result);write_json(run/'GT_diagnostics.json',{'records':diagnostics})
    # Provisional filtered pools quarantine unresolved candidates; no production task pool changes.
    blocked=set(unique)|{(r['split'],r['image_id']) for r in unresolved}
    (run/'filtered_tasks_pool').mkdir(exist_ok=True);retained={}
    for split in settings()['splits']:
        destination=run/'filtered_tasks_pool'/split;destination.mkdir(exist_ok=True)
        for source in (engine.ROOT/'LS_lcad_reviewer/tasks_pool'/split).glob('*.json'):
            tasks=read_json(source);kept=[t for t in tasks if (split,Path(t['data']['original_record']['image_id']).stem) not in blocked]
            write_json(destination/source.name,kept);retained[source.name]={'source':len(tasks),'retained':len(kept),'excluded_or_pending':len(tasks)-len(kept)}
    write_json(run/'filtered_pool_summary.json',retained);print('Filter:',len(excluded),'GT excluded;',len(unresolved),'candidate memberships pending;',counts,flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['scan','prepare','run','retry','export']);p.add_argument('--run-id',required=True);p.add_argument('--workers',type=int,default=16);p.add_argument('--timeout',type=int)
    args=p.parse_args();run=OUTPUT/args.run_id
    if args.command=='scan':scan(run)
    elif args.command=='prepare':prepare(run)
    elif args.command=='run':run_jobs(run,args.workers)
    elif args.command=='retry':run_jobs(run,args.workers,retry=True,timeout_override=args.timeout)
    elif args.command=='export':export_filter(run)


if __name__=='__main__':main()
