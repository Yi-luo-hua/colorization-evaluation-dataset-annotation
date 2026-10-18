"""Neutral region numbers on existing boards; no category/semantic hints or crops."""
import argparse
from pathlib import Path
from PIL import Image,ImageDraw

import engine
from workflow import OUTPUT,read_json,write_json,font
from run_harness_trial import prepare_trial


def iou(a,b):
    inter=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
    area=lambda x:(x[2]-x[0])*(x[3]-x[1])
    return inter/(area(a)+area(b)-inter+1e-8)


def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--run-id',required=True)
    args=p.parse_args();out=OUTPUT/args.run_id;m=prepare_trial(args.baseline,out,'compact')
    parameters=read_json(Path(__file__).with_name('roi_overlay_config.json'))
    m['configuration']['sheet']['roi_overlay']=parameters;inventory=[]
    for s in m['sheets']:
        image=Image.open(out/s['path']).convert('RGB');draw=ImageDraw.Draw(image)
        for r in [r for r in m['records'] if r['sheet']==s['path']]:
            selected=[]
            for candidate in sorted(r['region_candidates'],key=lambda x:x['pixel_fraction']*x['mean_signal'],reverse=True):
                box=candidate[parameters['bbox_source']]
                if all(iou(box,c[parameters['bbox_source']])<=parameters['maximum_overlap_iou'] for c in selected):selected.append(candidate)
                if len(selected)==parameters['maximum_regions']:break
            im=Image.open(engine.ROOT/r['gt_path']);im.thumbnail((500,320));w,h=im.size
            top=(r['sheet_row']-1)*430+94+(320-h)//2
            for col in range(3):
                left=18+col*515+(500-w)//2
                for idx,c in enumerate(selected,1):
                    x1,y1,x2,y2=c[parameters['bbox_source']];bounds=(left+x1*w,top+y1*h,left+x2*w,top+y2*h)
                    draw.rectangle(bounds,outline='black',width=4);draw.rectangle(bounds,outline=(255,205,50),width=2)
                    label=str(idx);x,y=bounds[:2]
                    draw.rectangle((x,y,x+19,y+22),fill=(255,205,50));draw.text((x+2,y),label,fill='black',font=font(16))
            inventory.append({'sample_key':r['sample_key'],'selected_regions':selected})
        image.save(out/s['path']);s['sha256']=engine.sha256(out/s['path'])
    write_json(out/'manifest.json',m)
    request=read_json(out/'review_request.json');request['roi_overlay']=True;write_json(out/'review_request.json',request)
    write_json(out/'roi_overlay_selection.json',{'parameters':parameters,'records':inventory,
               'labels_used':False,'object_semantics_used':False,'regions_are_not_segmentation':True})
    (out/'overlay_renderer_source.py').write_bytes(Path(__file__).read_bytes())
    write_json(out/'trial.json',{'baseline':str(args.baseline.resolve()),'changed_surface':'numerical candidate rectangles plus neutral legend',
        'same_CV_records':True,'same_source_image_hashes':True,'no_previous_labels_copied':True,
        'parameters_fitted_to_labels':False,'source_sha256':engine.sha256(Path(__file__))})
    print(out)


if __name__=='__main__':main()
