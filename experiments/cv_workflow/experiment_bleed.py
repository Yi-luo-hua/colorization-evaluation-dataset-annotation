"""Round22 offline B prototype:fixture calibration and fresh geometry/palette holdout."""
from pathlib import Path
import argparse
import cv2
import numpy as np
import bleed_probe as bp
import engine
import workflow as wf
from experiment_cd import transform,component

OUT=wf.OUTPUT/'bleed_round22_offline_20261013'
SETTINGS={'near_fraction':.02,'far_fraction':.08,'edge_quantile':.90}
KINDS=['identity','feather1','feather3','shift1','shift3','global_cast','whole_recolour','chroma_fade','bleed20','bleed60']


def fixture(size,diagonal,palette):
    yy,xx=np.indices((size,size));distance=(xx-(size/2+(yy-size/2)*diagonal))/np.sqrt(1+diagonal**2)
    gt=np.empty((size,size,3),np.float32)
    gt[distance<0]=[52,*palette[0]];gt[distance>=0]=[82,*palette[1]]
    return gt,distance


def variants(gt,distance,kind):
    gen=gt.copy()
    if kind.startswith('feather'):
        sigma=(1 if kind=='feather1' else 3)*min(gt.shape[:2])/256
        gen[...,1:]=cv2.GaussianBlur(gt[...,1:],(0,0),sigma)
    elif kind.startswith('shift'):
        pixels=round((1 if kind=='shift1' else 3)*min(gt.shape[:2])/256)
        gen=np.roll(gt,pixels,axis=1)
    elif kind=='global_cast':gen[...,1:]+=[8,12]
    elif kind=='whole_recolour':gen[distance>=0,1:]=np.median(gt[distance<0,1:],axis=0)
    elif kind=='chroma_fade':gen[...,1:]*=.55
    elif kind.startswith('bleed'):
        amount=.2 if kind.startswith('bleed20') else .6
        band=(distance>=0)&(distance<.055*min(gt.shape[:2]))
        span=.12 if kind.endswith('_short') else .25 if kind.endswith('_mid') else .6
        yy=np.indices(distance.shape)[0];band &= (yy>(.5-span/2)*distance.shape[0])&(yy<(.5+span/2)*distance.shape[0])
        donor=np.median(gt[distance<0,1:],axis=0)
        gen[band,1:]=gen[band,1:]*(1-amount)+donor*amount
    return gen


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--connected-contours',action='store_true');parser.add_argument('--short-spills',action='store_true');args=parser.parse_args()
    out=wf.OUTPUT/'bleed_round22_localized_20261013' if args.short_spills else wf.OUTPUT/'bleed_round22_connected_20261013' if args.connected_contours else OUT
    settings={**SETTINGS,'edge_grow_fraction':.5 if args.connected_contours or args.short_spills else 1.0}
    out.mkdir();rows=[];maps=[]
    sets={'development':[(256,0,([45,25],[0,0])),(256,.25,([-25,-30],[20,25])),(512,-.25,([15,-35],[-20,30]))],
          'confirmation':[(192,-.15,([-30,25],[30,-15])),(384,.4,([35,15],[-10,-20])),(512,0,([0,0],[40,30]))]}
    if args.short_spills:sets['confirmation']=[(224,.1,([-25,15],[15,-30])),(320,-.35,([40,-15],[-10,20])),(448,.5,([0,0],[35,15]))]
    kinds=KINDS[:-2]+['bleed20_short','bleed20_mid','bleed20','bleed60_short','bleed60_mid','bleed60'] if args.short_spills else KINDS
    for split,fixtures in sets.items():
        for index,(size,slope,palette) in enumerate(fixtures):
            gt,distance=fixture(size,slope,palette)
            for kind in kinds:
                gen=variants(gt,distance,kind);score=bp.measure(gt,gen,settings)
                rows.append({'split':split,'fixture':index,'size':size,'slope':slope,'kind':kind,'physical_bleed_target':kind.startswith('bleed'),'maximum_score':float(score.max()),'source':'constructed Lab boundary fixture'})
                maps.append(score)
    # Real retained GT negatives broaden calibration beyond ideal boundaries.
    sources=wf.read_json(wf.OUTPUT/'cd_round22_setup_20261013/selection.json')
    selected=[s for split in ['train','test'] for s in ([x for x in sources if x['split']==split][6:12] if args.short_spills and split=='test' else [x for x in sources if x['split']==split][:6])]
    cfg=wf.read_json(Path(__file__).with_name('config.json'))
    for s in selected:
        gt_rgb=engine.read_rgb(engine.ROOT/s['gt_path'],256);gt=engine.lab(gt_rgb);masks=component(gt_rgb)
        for kind in ['identity','exposure','chroma_fade','global_rotation40','component_rotation']:
            gen=engine.lab(transform(gt_rgb,kind,masks));score=bp.measure(gt,gen,settings)
            rows.append({'split':'development' if s['split']=='train' else 'confirmation','GT':s['image_id'],'kind':kind,'physical_bleed_target':False,'maximum_score':float(score.max()),'source':'real GT no-cross-boundary intervention'})
            maps.append(score)
    candidates=[]
    for cutoff in [.02,.05,.1,.15,.2,.3]:
        sizes=[bp.longest(score,cutoff) for score in maps]
        dev=[i for i,r in enumerate(rows) if r['split']=='development']
        observed=sorted(set(sizes[i] for i in dev));limits=[observed[0]/2]+[(a+b)/2 for a,b in zip(observed,observed[1:])]+[observed[-1]+.01]
        for length in limits:
            fp=sum(not rows[i]['physical_bleed_target'] and sizes[i]>length for i in dev);fn=sum(rows[i]['physical_bleed_target'] and sizes[i]<=length for i in dev)
            candidates.append({'score_cutoff':cutoff,'minimum_connected_extent':length,'FP':fp,'FN':fn,'cost':2*fp+fn})
    best=min(candidates,key=lambda x:(x['cost'],x['FP'],x['score_cutoff'],-x['minimum_connected_extent']))
    for row,score in zip(rows,maps):
        row['connected_extent']=bp.longest(score,best['score_cutoff']);row['B_candidate']=row['connected_extent']>best['minimum_connected_extent']
    summary={}
    for split in ['development','confirmation']:
        rr=[r for r in rows if r['split']==split]
        summary[split]={'positive_detected':sum(r['physical_bleed_target'] and r['B_candidate'] for r in rr),'positive_total':sum(r['physical_bleed_target'] for r in rr),'negative_flagged':sum(not r['physical_bleed_target'] and r['B_candidate'] for r in rr),'negative_total':sum(not r['physical_bleed_target'] for r in rr),'mismatches':[r for r in rr if r['physical_bleed_target']!=r['B_candidate']]}
    wf.write_json(out/'rows.json',rows);wf.write_json(out/'fit.json',{'settings':settings,'rule':best,'candidates':candidates,'fit_on_confirmation':False})
    wf.write_json(out/'summary.json',{'rows':len(rows),'real_GT':12,'summary':summary,'semantic_limit':'Constructed spill and no-spill transformations are known;no real positive B gold. Prototype remains offline,not automatic labels or default visual hints.'})
    (out/'experiment_bleed.py').write_bytes(Path(__file__).read_bytes());(out/'bleed_probe.py').write_bytes(Path(bp.__file__).read_bytes())
    print(best,summary,flush=True)


if __name__=='__main__':main()
