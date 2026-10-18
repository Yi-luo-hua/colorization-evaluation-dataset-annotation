"""Numbered generated-only contact sheets for human A screening."""
import argparse
import csv
import hashlib
import html
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--screen',type=Path,required=True)
    parser.add_argument('--run-id',required=True)
    parser.add_argument('--minimum-gray-fraction',type=float,default=.5)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[2]
    source=args.screen/'records.json'
    rows=json.loads(source.read_text(encoding='utf-8'))
    selected=sorted((r for r in rows if r['generated_color']['gray_pixel_fraction']>=args.minimum_gray_fraction),
                    key=lambda r:(-r['generated_color']['gray_pixel_fraction'],r['sample_key']))
    out=root/'LS_lcad_reviewer/intermediate/experiments'/args.run_id
    (out/'sheets').mkdir(parents=True)
    heading=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',29)
    small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
    cols,per_sheet,card_w,card_h,margin,header=4,24,424,356,20,90
    mapping=[];sheets=[]
    for start in range(0,len(selected),per_sheet):
        chunk=selected[start:start+per_sheet];page=start//per_sheet+1
        name=f'sheet_{page:03d}_{start+1:04d}-{start+len(chunk):04d}.png'
        canvas=Image.new('RGB',(margin*2+cols*card_w,header+math.ceil(len(chunk)/cols)*card_h+margin),(238,241,245))
        draw=ImageDraw.Draw(canvas)
        draw.text((margin,14),f'A人工审查 · 第{page:02d}张 · 序号 {start+1:04d}—{start+len(chunk):04d}',font=heading,fill=(27,43,59))
        draw.text((margin,55),'只看生成图；只需记录不是A的序号。允许极少量局部留色；GT已排除仅作提示。',font=small,fill=(63,75,87))
        for i,r in enumerate(chunk):
            number=start+i+1;row,col=divmod(i,cols);left=margin+col*card_w;top=header+row*card_h
            draw.rounded_rectangle((left,top,left+card_w-10,top+card_h-10),radius=8,fill='white',outline=(208,216,225))
            draw.text((left+12,top+5),f'{number:04d}',font=heading,fill=(20,37,57))
            if not r['GT_eligible']:draw.text((left+card_w-125,top+14),'GT已排除',font=small,fill=(155,90,21))
            image_path=root/r['model_path']
            with Image.open(image_path) as original:
                pixels=original.convert('RGB');pixels.thumbnail((card_w-26,card_h-58),Image.Resampling.LANCZOS)
                canvas.paste(pixels,(left+(card_w-10-pixels.width)//2,top+43+(card_h-58-pixels.height)//2))
            mapping.append({'number':number,'review_id':f'{number:04d}','source_sample_key':r['sample_key'],
                            'split':r['split'],'model':r['model'],'task_idx':r['task_idx'],
                            'gray_pixel_fraction':r['generated_color']['gray_pixel_fraction'],
                            'GT_eligible':r['GT_eligible'],'sheet':f'sheets/{name}','sheet_row':row+1,'sheet_column':col+1,
                            'source_model_path':r['model_path'],'source_model_sha256':hashlib.sha256(image_path.read_bytes()).hexdigest()})
        canvas.save(out/'sheets'/name)
        sheets.append({'page':page,'path':f'sheets/{name}','number_start':start+1,'number_end':start+len(chunk),
                       'images':len(chunk),'size':list(canvas.size),'sha256':hashlib.sha256((out/'sheets'/name).read_bytes()).hexdigest()})
        print(f'Board {page}: {start+1:04d}-{start+len(chunk):04d}',flush=True)
    assert len({r['source_sample_key'] for r in mapping})==len(selected)
    assert [r['number'] for r in mapping]==list(range(1,len(selected)+1))
    summary={'created_at':datetime.now(timezone.utc).isoformat(),'state':'awaiting_user_manual_A_review',
             'source_screen':str(args.screen),'source_records_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
             'minimum_gray_fraction':args.minimum_gray_fraction,'pixel_channel_tolerance':rows[0]['generated_color']['gray_channel_tolerance'],
             'images':len(selected),'GT_eligible':sum(r['GT_eligible'] for r in selected),
             'excluded_GT_source':sum(not r['GT_eligible'] for r in selected),'sheets':len(sheets),'images_per_sheet':per_sheet,
             'layout':'4 columns x 6 rows, last sheet shorter','order':'gray fraction descending, source_sample_key ascending for ties',
             'no_labels_on_boards':True,'generated_only':True,'no_native_calls':True,
             'no_new_labels_written':True,'GT_exclusions_unchanged':True,'active_annotation_threshold_unchanged':True}
    (out/'manifest.json').write_text(json.dumps({'summary':summary,'sheets':sheets,'records':mapping},ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    with (out/'image_number_mapping.csv').open('w',encoding='utf-8-sig',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=mapping[0].keys());writer.writeheader();writer.writerows(mapping)
    cards='\n'.join(f'<a class="card" href="{html.escape(s["path"])}" target="_blank"><img loading="lazy" src="{html.escape(s["path"])}"><strong>第{s["page"]:02d}张 · {s["number_start"]:04d}—{s["number_end"]:04d}</strong></a>' for s in sheets)
    index=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>A人工审查看板</title>
<style>body{{font-family:"Microsoft YaHei",sans-serif;background:#eef1f5;color:#1b2b3b;margin:32px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px}}.card{{background:white;padding:12px;border-radius:10px;color:inherit;text-decoration:none}}img{{width:100%;display:block;margin-bottom:12px}}p{{line-height:1.7}}</style>
<h1>A人工审查看板 · {len(selected)}张生成图</h1><p>近灰像素占比≥{args.minimum_gray_fraction:.0%}；共{len(sheets)}张看板，每张最多24图，按行从左到右阅读。点击缩略图打开大图，可放大查看。<br>序号全局固定，按近灰比例从高到低排列。看完告诉我不是A的序号即可，例如“12、27、103”。可另列不确定序号；未审查不会自动记为A。<br>GT合格{summary['GT_eligible']}张，已排除{summary['excluded_GT_source']}张；后者即使判断为A也保持上游排除。<br>A允许极少量局部留色；主体或多个主要区域仍明显彩色、整图统一泛黄/棕色等单色不属于A。</p><div class="grid">{cards}</div></html>'''
    (out/'index.html').write_text(index,encoding='utf-8')
    readme=f'''# A人工审查：生成图近灰占比≥{args.minimum_gray_fraction:.0%}

{len(selected)}张生成图，{len(sheets)}张PNG看板；每张24图（4列×6行），末张{len(selected)%per_sheet or per_sheet}图。

打开index.html浏览全部看板，点击缩略图放大；也可直接打开sheets目录。编号0001—{len(selected):04d}全局固定，按灰阶占比从高到低排列。只显示生成图和序号，不展示旧标签、源路径或灰阶数值。

看完告诉我不是A的序号即可，可分批回复，并另外指出不确定编号；尚未审查的图片不会自动标A。

GT合格{summary['GT_eligible']}张，GT已排除{summary['excluded_GT_source']}张（图上注明）。后者仅供全量审查，不重新进入标注。当前正式筛选门槛仍90%，此次50%只生成独立人工审查包。

image_number_mapping.csv及manifest.json保存编号、源身份、看板行列对应关系；原图、旧结果及正式导出均不修改。
'''
    (out/'README.md').write_text(readme,encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False));print(out)


if __name__=='__main__':main()
