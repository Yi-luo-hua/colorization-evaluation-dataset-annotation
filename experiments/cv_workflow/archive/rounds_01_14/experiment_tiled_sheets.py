"""Six groups in a near-square board: two cards per row, three rows.

Frozen CV/source pairs; no labels, crop requests, or category hints enter the trial.
This is an experimental renderer, not the default six-row renderer.
"""
import argparse
import math
import time
from pathlib import Path

from PIL import Image,ImageDraw
import cv2

import engine
from workflow import OUTPUT,read_json,write_json,font,align,utc
from run_harness_trial import prepare_trial


def render(records,run,cfg):
    layout=cfg['sheet'];card_w=layout['width']//2;card_h=layout['card_height'];sheets=[];panes=[]
    for start in range(0,len(records),6):
        chunk=records[start:start+6]
        canvas=Image.new('RGB',(layout['width'],card_h*math.ceil(len(chunk)/2)),(240,242,245));draw=ImageDraw.Draw(canvas)
        for idx,r in enumerate(chunk):
            left=(idx%2)*card_w;top=(idx//2)*card_h;m=r['metrics']
            draw.rectangle((left+5,top+5,left+card_w-5,top+card_h-5),fill='white',outline=(200,205,215))
            draw.text((left+14,top+12),f"组{idx+1}  {r['sample_key']}",fill='black',font=font(22))
            draw.text((left+14,top+46),f"CV：彩度比{m['chroma_ratio']:.2f}；跨色组共同变化{m['color_group_shift_norm']:.1f}",fill=(65,65,70),font=font(16))
            draw.text((left+14,top+70),f"较弱色组支持{m['color_group_projection_q']:.1f}；结构保留{m['scalar_gain']:.2f}；数值不是标签",fill=(65,65,70),font=font(16))
            gt=engine.read_rgb(engine.ROOT/r['gt_path']);gen=align(gt,engine.read_rgb(engine.ROOT/r['model_path']))
            heat=engine.heatmap(engine.lab(gt),engine.lab(gen),cfg['display'])
            dimensions=[]
            for col,(pixels,title) in enumerate(zip([gt,gen,heat],['GT',r['model'].upper()+' 生成图','彩度差：红增蓝减；黑≠无错色'])):
                x=left+14+col*(layout['image_box_width']+10)
                draw.text((x,top+103),title,fill=(65,65,70),font=font(16))
                im=Image.fromarray(pixels);im.thumbnail((layout['image_box_width'],layout['image_box_height']),Image.Resampling.LANCZOS)
                canvas.paste(im,(x+(layout['image_box_width']-im.width)//2,top+136+(layout['image_box_height']-im.height)//2))
                dimensions.append(list(im.size))
            r['sheet']=f'sheets/sheet_{len(sheets)+1:03d}.png';r['sheet_row']=idx+1
            panes.append({'sample_key':r['sample_key'],'panel_sizes':dimensions})
        path=run/'sheets'/f'sheet_{len(sheets)+1:03d}.png';canvas.save(path)
        sheets.append({'path':str(path.relative_to(run)).replace('\\','/'),'sha256':engine.sha256(path),
                       'sample_keys':[r['sample_key'] for r in chunk],'groups':len(chunk),'size':list(canvas.size)})
    return sheets,panes


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--baseline',type=Path,required=True)
    parser.add_argument('--run-id',required=True);args=parser.parse_args();cv2.setNumThreads(1)
    out=OUTPUT/args.run_id;manifest=prepare_trial(args.baseline,out,'compact')
    cfg=manifest['configuration'];cfg['sheet'].update(layout='two_columns_three_rows',width=2000,card_height=650,image_box_width=314,image_box_height=500)
    started=time.perf_counter();manifest['sheets'],panes=render(manifest['records'],out,cfg)
    write_json(out/'manifest.json',manifest)
    request=read_json(out/'review_request.json');request['sheet_layout']='two_columns_three_rows';write_json(out/'review_request.json',request)
    write_json(out/'trial.json',{'baseline':str(args.baseline.resolve()),'created_at':utc(),
        'changed_surface':'six-group arrangement and photograph display size; necessary legend only',
        'same_CV_records':True,'same_source_image_hashes':True,'no_previous_labels_copied':True,
        'render_seconds':time.perf_counter()-started,'panel_dimensions':panes,
        'source_sha256':{p.name:engine.sha256(p) for p in [Path(__file__),Path(__file__).with_name('compact_harness.py')]}})
    (out/'tiled_renderer_source.py').write_bytes(Path(__file__).read_bytes())
    # Keep the IDE handoff consistent; source locations remain private.
    text=(out/'START_HERE.md').read_text(encoding='utf-8')
    (out/'START_HERE.md').write_text(text+'\n本次实验每张两列三行、共六组；按S编号，组内左GT、中生成、右热力图。\n',encoding='utf-8')
    print(out)


if __name__=='__main__':main()
