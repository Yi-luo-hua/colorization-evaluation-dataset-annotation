"""Filesystem handoff to Antigravity. Does not call or configure its model."""
import argparse
import copy
import importlib.util
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

import cv2
from PIL import Image, ImageDraw, ImageFont

import engine

BASE=engine.ROOT/'LS_lcad_reviewer'
OUTPUT=BASE/'intermediate'/'experiments'
TAXONOMY={'A':'缺色','B':'溢色','C':'错色','D':'偏色','E1':'过饱和','E2':'欠饱和','F':'视觉自然度'}


def read_json(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write_json(path,data):Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def utc():return datetime.now(timezone.utc).isoformat()


def align(gt,gen):
    return cv2.resize(gen,(gt.shape[1],gt.shape[0]),interpolation=cv2.INTER_LINEAR) if gt.shape!=gen.shape else gen


def model_image(directory,stem):
    for extension in ['.png','.jpg','.jpeg']:
        p=directory/f'{stem}{extension}'
        if p.exists():return p
    raise FileNotFoundError(f'No generated image for {directory}/{stem}')


def font(size):return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size)


def render(records,run,cfg):
    layout=cfg['sheet'];size=layout['groups_per_sheet'];sheets=[]
    if size!=6:raise ValueError('Current handoff contract requires six groups per sheet')
    for start in range(0,len(records),size):
        chunk=records[start:start+size];canvas=Image.new('RGB',(layout['width'],layout['card_height']*len(chunk)),(240,242,245));draw=ImageDraw.Draw(canvas)
        for row,r in enumerate(chunk):
            top=row*layout['card_height'];m=r['metrics']
            draw.rectangle((8,top+5,layout['width']-8,top+layout['card_height']-5),fill='white',outline=(200,205,215))
            draw.text((18,top+10),f"行{row+1}  {r['sample_key']}",fill='black',font=font(20))
            draw.text((18,top+39),f"CV测量：彩度保留比 {m['chroma_ratio']:.2f}；共同色度变化 {m['robust_shift_norm']:.1f}；网格一致覆盖 {m['common_coverage']:.0%}；CV平稳不代表无缺陷",fill=(65,65,70),font=font(16))
            gt=engine.read_rgb(engine.ROOT/r['gt_path']);gen=align(gt,engine.read_rgb(engine.ROOT/r['model_path']))
            heat=engine.heatmap(engine.lab(gt),engine.lab(gen),cfg['display'])
            for col,(pixels,title) in enumerate(zip([gt,gen,heat],['GT',r['model'].upper()+' 生成图','双向彩度差：正红负蓝，近零不保证无错色'])):
                left=18+col*515;draw.text((left,top+68),title,fill=(65,65,70),font=font(16))
                image=Image.fromarray(pixels);image.thumbnail((layout['image_box_width'],layout['image_box_height']),Image.Resampling.LANCZOS)
                canvas.paste(image,(left+(layout['image_box_width']-image.width)//2,top+94+(layout['image_box_height']-image.height)//2))
            r['sheet']=f'sheets/sheet_{len(sheets)+1:03d}.png';r['sheet_row']=row+1
        name=f'sheet_{len(sheets)+1:03d}.png';path=run/'sheets'/name;canvas.save(path)
        sheets.append({'path':f'sheets/{name}','sha256':engine.sha256(path),'sample_keys':[r['sample_key'] for r in chunk],'groups':len(chunk),'size':list(canvas.size)})
    return sheets


def prepare(args,cfg):
    if not re.fullmatch(r'[A-Za-z0-9_-]+',args.run_id):raise ValueError('run-id must be a single identifier')
    if args.start<1 or args.end<args.start:raise ValueError('Invalid inclusive task range')
    run=OUTPUT/args.run_id
    if run.exists():raise ValueError(f'Existing run must not be overwritten: {run}')
    records=[];sources={}
    for model in (['lcad','unicolor'] if args.model=='both' else [args.model]):
        files=list((BASE/'tasks_pool'/args.split).glob(f'*{model}*.json'))
        if len(files)!=1:raise ValueError(f'Expected one task pool for {args.split}/{model}, found {len(files)}')
        tasks=read_json(files[0]);sources[str(files[0].relative_to(engine.ROOT))]=engine.sha256(files[0])
        if args.end>len(tasks):raise ValueError('Range exceeds task pool')
        dataset=engine.ROOT/cfg['datasets'][args.split]
        for index,task in enumerate(tasks[args.start-1:args.end],args.start):
            original=copy.deepcopy(task['data']['original_record']);stem=Path(original['image_id']).stem
            g=dataset/'image'/f'{stem}.jpg';p=model_image(dataset/'model'/model,stem)
            gr=engine.read_rgb(g,cfg['analysis_max_side']);mr=align(gr,engine.read_rgb(p,cfg['analysis_max_side']))
            metrics,flags,maps=engine.measure(engine.lab(gr),engine.lab(mr),cfg)
            region_side=cfg['regions'].get('max_side',cfg['analysis_max_side'])
            if region_side!=cfg['analysis_max_side']:
                rg=engine.read_rgb(g,region_side);rm_=align(rg,engine.read_rgb(p,region_side))
                maps=engine.difference_maps(engine.lab(rg),engine.lab(rm_))
            records.append({'sample_key':f'{args.split}/{model}/{stem}','task_idx':index,'split':args.split,'model':model,
                            'gt_path':str(g.relative_to(engine.ROOT)),'model_path':str(p.relative_to(engine.ROOT)),
                            'gt_sha256':engine.sha256(g),'model_sha256':engine.sha256(p),
                            'original_record':original,'source_task_data':copy.deepcopy(task['data']),
                            'metrics':metrics,'cv_flags':flags,'region_analysis_max_side':region_side,
                            'region_candidates':engine.regions(maps,cfg,prefer_compact=p.suffix.lower() in ['.jpg','.jpeg'])})
    run.mkdir(parents=True);(run/'sheets').mkdir()
    sheets=render(records,run,cfg)
    manifest={'schema_version':'cv_handoff_v1','created_at':utc(),'state':'awaiting_external_visual_review',
              'source_code_sha256':{p.name:engine.sha256(p) for p in [Path(__file__),Path(engine.__file__),Path(__file__).with_name('global_models.py'),Path(__file__).with_name('region_models.py')]},
              'configuration':cfg,'source_task_sha256':sources,'records':records,'sheets':sheets}
    write_json(run/'manifest.json',manifest)
    summary_keys=['chroma_ratio','robust_shift_norm','common_da','common_db','common_coverage','active_grid_coverage','dc_p05','dc_p95','hue_component_max']
    if 'global_models' in cfg:
        summary_keys=['chroma_ratio','brightness_conditioned_color_ratio','reference_color_retention',
                      'robust_shift_norm','common_da','common_db','common_coverage','active_grid_coverage','active_pixel_coverage',
                      'scalar_gain','scalar_intercept_norm','scalar_fit_median_error','translation_fit_median_error',
                      'gain_fit_domain','gain_fit_residual','gain_channel_imbalance',
                      'dc_p05','dc_p95','hue_component_max']
    request={'schema_version':'visual_review_v1','reviewer':cfg['external_reviewer'],'sheet_groups':6,
             'display':cfg['display'],'warning':'Numerical candidates are not labels. Do not access historical defect labels or scores during blind review.',
             'samples':[{**{k:r[k] for k in ['sample_key','sheet','sheet_row','gt_path','model_path','region_candidates']},
                         'metrics':{k:r['metrics'][k] for k in summary_keys}} for r in records]}
    write_json(run/'review_request.json',request)
    template={'schema_version':'visual_review_v1','reviewer':cfg['external_reviewer'],
              'reviews':[{'sample_key':r['sample_key'],'inspection_complete':False,'decision':'uncertain','defects':[],
                          'checked_categories':[],'uncertainties':['尚未视觉审核'],'needs_crops':[]} for r in records]}
    write_json(run/'review_template.json',template)
    (run/'ANTIGRAVITY_HANDOFF.md').write_text(Path(__file__).with_name('ANTIGRAVITY_HANDOFF.md').read_text(encoding='utf-8'),encoding='utf-8')
    print(f'Prepared {len(records)} samples, {len(sheets)} six-group sheets: {run}')


def verify_sources(run):
    manifest=read_json(run/'manifest.json')
    for r in manifest['records']:
        for field in ['gt','model']:
            if engine.sha256(engine.ROOT/r[f'{field}_path'])!=r[f'{field}_sha256']:raise ValueError(f'Source image changed: {r["sample_key"]}')
    for p,sha in manifest['source_task_sha256'].items():
        if engine.sha256(engine.ROOT/p)!=sha:raise ValueError(f'Source task pool changed: {p}')
    for s in manifest['sheets']:
        if engine.sha256(run/s['path'])!=s['sha256']:raise ValueError(f'Sheet changed: {s["path"]}')
    return manifest


def validate_reviews(manifest,payload,strict=False):
    if payload.get('schema_version')!='visual_review_v1':raise ValueError('Wrong review schema version')
    if payload.get('reviewer')!=manifest['configuration']['external_reviewer']:raise ValueError('Reviewer metadata must match the configured Antigravity handoff')
    rows=payload.get('reviews',[]);keys=[r.get('sample_key') for r in rows]
    expected={r['sample_key'] for r in manifest['records']}
    if len(keys)!=len(set(keys)) or set(keys)!=expected:raise ValueError('Each manifest sample must have exactly one review; no missing/duplicate/extra samples')
    checked=set(TAXONOMY)
    for r in rows:
        if r.get('inspection_complete') is not True:raise ValueError(f'Incomplete inspection: {r["sample_key"]}')
        if len(r.get('checked_categories',[]))!=7 or set(r['checked_categories'])!=checked:raise ValueError('All seven categories must be checked exactly once')
        decision=r.get('decision');defects=r.get('defects');uncertainties=r.get('uncertainties');crops=r.get('needs_crops')
        if decision not in ['defects','no_defects','uncertain'] or not isinstance(defects,list) or not isinstance(uncertainties,list) or not isinstance(crops,list):raise ValueError('Invalid decision/list fields')
        if decision=='defects' and not defects:raise ValueError('Defects decision needs evidence')
        if decision=='no_defects' and (defects or uncertainties or crops):raise ValueError('No-defects decision conflicts with unresolved evidence')
        if decision=='uncertain' and not (uncertainties or crops):raise ValueError('Uncertain decision needs reason or crop request')
        if strict and (decision=='uncertain' or uncertainties or crops):raise ValueError('Resolve uncertainty/crops before candidate export')
        for d in defects:
            if d.get('id') not in TAXONOMY:raise ValueError('Unknown defect ID')
            for field in ['object','location','gt_color','generated_color','evidence']:
                if not isinstance(d.get(field),str) or not d[field].strip():raise ValueError(f'Defect requires concrete {field}')
            severity=d.get('severity')
            if d['id']=='A' and severity!='':raise ValueError('A severity must be empty')
            if d['id']!='A' and severity not in [None,'L1','L2','L3']:raise ValueError('Invalid severity')
            if strict and d['id']!='A' and severity is None:raise ValueError('Uncalibrated severity cannot be exported')
        if any(d['id']=='A' for d in defects) and (len(defects)!=1 or decision!='defects'):raise ValueError('A must be the sole terminal defect')
    return {r['sample_key']:r for r in rows}


def import_reviews(args):
    run=Path(args.batch).resolve();manifest=verify_sources(run);payload=read_json(args.reviews)
    validate_reviews(manifest,payload)
    if (run/'visual_reviews.json').exists():raise ValueError('Use a new run for another review iteration; never silently overwrite imported reviews')
    payload['received_at']=utc();write_json(run/'visual_reviews.json',payload)
    manifest['state']='visual_results_imported_pending_resolution';write_json(run/'manifest.json',manifest)
    print('Imported complete sample coverage; uncertain decisions and uncalibrated severities remain pending.')


def export_candidate(args):
    run=Path(args.batch).resolve();manifest=verify_sources(run);reviews=read_json(run/'visual_reviews.json');mapping=validate_reviews(manifest,reviews,strict=True)
    destination=run/'exports';destination.mkdir(exist_ok=True)
    target=destination/'reviewed_candidate.json'
    if target.exists():raise ValueError('Candidate export already exists')
    annotations=[]
    for r in manifest['records']:
        review=mapping[r['sample_key']];original=r['original_record'];defects=[]
        for d in review['defects']:
            defects.append({'id':d['id'],'name':TAXONOMY[d['id']],'severity':d['severity'],
                            'description':f"{d['location']}的{d['object']}：GT为{d['gt_color']}，生成图为{d['generated_color']}；{d['evidence']}"})
        a=any(d['id']=='A' for d in defects)
        annotations.append({'image_id':original['image_id'],'file_path':original['file_path'],'source_dataset':original['source_dataset'],'role':original['role'],
                            'defects':defects,'gpt_score':original['gpt_score'],'labeling_model':original['labeling_model'],'labeling_timestamp':original['labeling_timestamp'],
                            'original_gpt_score':original['gpt_score'],'review_status':'已核验','review_note':'；'.join(d['description'] for d in defects) if defects else '审查通过',
                            'reviewed_score':1.0 if a else None,'needs_rescoring':not a,
                            'human_review':{'task_id':r['task_idx'],'annotation_id':r['task_idx'],'completed_by':0,'updated_at':reviews['received_at']}})
    data={'meta':{'exported_at':utc(),'total_images':len(annotations),'needs_rescoring':True},'annotations':annotations}
    temporary=destination/'reviewed_candidate.pending.json';write_json(temporary,data)
    script=BASE/'core_pipeline'/'validate_export_schema.py';spec=importlib.util.spec_from_file_location('export_contract_validator',script);validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)
    if not validator.validate_file(temporary):raise ValueError('Candidate failed official schema validation')
    temporary.replace(target)
    # SQLite/human reviewer IDs are not fabricated: completed_by=0 denotes external AI only.
    write_json(destination/'provenance.json',{'external_reviewer':reviews['reviewer'],'review_file_sha256':engine.sha256(run/'visual_reviews.json'),
               'configuration_version':manifest['configuration']['version'],'completed_by_0':'external AI, not a human Label Studio reviewer',
               'experimental_candidate_only':True,'production_ready':manifest['configuration']['production_ready']})
    stream=[]
    for r,item in zip(manifest['records'],annotations):
        result=[{'from_name':'review_status','to_name':'colorized','type':'choices','value':{'choices':['已核验']}},
                {'from_name':'review_note','to_name':'colorized','type':'textarea','value':{'text':[item['review_note']]}}]
        for code in TAXONOMY:
            group=[d for d in item['defects'] if d['id']==code]
            severity=('命中' if group else '未命中') if code=='A' else max([d['severity'] for d in group],default='无此缺陷')
            result.append({'from_name':f'severity_{code}','to_name':'colorized','type':'choices','value':{'choices':[severity]}})
            if group:result.append({'from_name':f'description_{code}','to_name':'colorized','type':'textarea','value':{'text':['\n'.join(f"[{d['severity']}] {d['description']}" for d in group)]}})
        stream.append({'data':r['source_task_data'],'predictions':[{'model_version':manifest['configuration']['version'],'result':result}]})
    write_json(destination/'tasks_reviewed_stream.json',stream)
    manifest['state']='experimental_candidate_exported';write_json(run/'manifest.json',manifest)
    print(f'Validated candidate (not published or copied to formal exports): {target}')


def crop(args):
    run=Path(args.batch).resolve();manifest=verify_sources(run);record=next(r for r in manifest['records'] if r['sample_key']==args.sample_key)
    x1,y1,x2,y2=args.bbox
    if not all(math.isfinite(x) for x in args.bbox) or not (0<=x1<x2<=1 and 0<=y1<y2<=1):raise ValueError('bbox must be normalized x1 y1 x2 y2')
    g=engine.read_rgb(engine.ROOT/record['gt_path']);m=align(g,engine.read_rgb(engine.ROOT/record['model_path']))
    h,w=g.shape[:2];bounds=(int(x1*w),int(y1*h),int(x2*w),int(y2*h))
    if bounds[2]<=bounds[0] or bounds[3]<=bounds[1]:raise ValueError('Crop is empty')
    crops=run/'crops';crops.mkdir(exist_ok=True)
    name=record['sample_key'].replace('/','_')+f'_{len(list(crops.glob("*.png")))+1:03d}.png';parts=[]
    for pixels in [g,m]:
        im=Image.fromarray(pixels).crop(bounds);im.thumbnail((900,900));parts.append(im)
    canvas=Image.new('RGB',(sum(im.width for im in parts),max(im.height for im in parts)+35),'white');draw=ImageDraw.Draw(canvas)
    offset=0
    for label,im in zip(['GT','生成图'],parts):draw.text((offset+4,4),label,fill='black',font=font(18));canvas.paste(im,(offset,35));offset+=im.width
    canvas.save(crops/name);print(crops/name)


def main():
    parser=argparse.ArgumentParser(description='Experimental CV → six-group sheets → Antigravity → strict candidate export')
    parser.add_argument('--config',type=Path,default=Path(__file__).with_name('config.json'));sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare');p.add_argument('--model',choices=['lcad','unicolor','both'],default='both');p.add_argument('--split',choices=['train','val','test'],default='val');p.add_argument('--start',type=int,default=1);p.add_argument('--end',type=int,default=12);p.add_argument('--run-id',required=True)
    p=sub.add_parser('verify');p.add_argument('--batch',required=True)
    p=sub.add_parser('import-reviews');p.add_argument('--batch',required=True);p.add_argument('--reviews',required=True)
    p=sub.add_parser('export-candidate');p.add_argument('--batch',required=True)
    p=sub.add_parser('crop');p.add_argument('--batch',required=True);p.add_argument('--sample-key',required=True);p.add_argument('--bbox',nargs=4,type=float,required=True)
    args=parser.parse_args();cv2.setNumThreads(1)
    if args.command=='prepare':prepare(args,read_json(args.config))
    elif args.command=='verify':m=verify_sources(Path(args.batch).resolve());print(f"PASS: {len(m['records'])} source pairs and {len(m['sheets'])} sheets unchanged; state={m['state']}")
    elif args.command=='import-reviews':import_reviews(args)
    elif args.command=='export-candidate':export_candidate(args)
    elif args.command=='crop':crop(args)


if __name__=='__main__':
    try:main()
    except (ValueError,FileNotFoundError) as error:raise SystemExit(f'BLOCKED: {error}')
