"""Candidate CV measurements. No semantic labels or automatic verified decisions."""
import hashlib
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_rgb(path, max_side=None):
    bgr=cv2.imdecode(np.fromfile(path,dtype=np.uint8),cv2.IMREAD_COLOR)
    if bgr is None:raise ValueError(f'Cannot decode {path}')
    if max_side and max(bgr.shape[:2])>max_side:
        ratio=max_side/max(bgr.shape[:2]);bgr=cv2.resize(bgr,(round(bgr.shape[1]*ratio),round(bgr.shape[0]*ratio)),interpolation=cv2.INTER_AREA)
    return cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)


def lab(rgb):
    return cv2.cvtColor(rgb.astype(np.float32)/255,cv2.COLOR_RGB2LAB)


def rgb(lab_image):
    return np.clip(np.rint(cv2.cvtColor(lab_image.astype(np.float32),cv2.COLOR_LAB2RGB)*255),0,255).astype(np.uint8)


def chroma(image):return np.linalg.norm(image[...,1:],axis=-1)


def measure(gt,gen,config):
    if gt.shape!=gen.shape:raise ValueError('Align RGB images before Lab measurement')
    cg,cm=chroma(gt),chroma(gen);delta=gen[...,1:]-gt[...,1:];dc=cm-cg
    vectors=[]
    for block_row in np.array_split(delta,config['grid_size'],axis=0):
        vectors.extend(np.median(block.reshape(-1,2),axis=0) for block in np.array_split(block_row,config['grid_size'],axis=1))
    vectors=np.array(vectors);common=np.median(vectors,axis=0);norm=float(np.linalg.norm(common))
    distances=np.linalg.norm(vectors-common,axis=1);cell_norms=np.linalg.norm(vectors,axis=1)
    x=gt[...,1:].reshape(-1,2)[::4];y=gen[...,1:].reshape(-1,2)[::4];xm=x.mean(0);ym=y.mean(0)
    gain=float(np.sum((x-xm)*(y-ym))/(np.sum((x-xm)**2)+1e-8));intercept=ym-gain*xm
    scalar_error=float(np.median(np.linalg.norm(y-gain*x-intercept,axis=1)))
    translation_error=float(np.median(np.linalg.norm(y-x-common,axis=1)))
    spread=[];concentrations=[]
    for image in [gt,gen]:
        ab=image[...,1:].reshape(-1,2);center=np.median(ab,axis=0)
        spread.append(float(np.percentile(np.linalg.norm(ab-center,axis=1),95)))
        concentrations.append(float(np.linalg.norm(ab.sum(0))/(np.linalg.norm(ab,axis=1).sum()+1e-8)))
    a=config['a'];d=config['d'];mono=config['monochrome_review']
    ratio=float(cm.mean()/(cg.mean()+1e-8));spread_ratio=spread[1]/(spread[0]+1e-8)
    a_flag=bool((cm.mean()<=a['maximum_mean_chroma'] and ratio<=a['maximum_chroma_ratio']) or
                (spread[1]<=a['maximum_centered_spread'] and spread_ratio<=a['maximum_spread_ratio']))
    coverage=float(np.mean(distances<=d['absolute_tolerance']+d['relative_tolerance']*norm))
    active=float(np.mean(cell_norms>=d['activity_floor']))
    scale_explains=bool(gain>0 and np.linalg.norm(intercept)<d['minimum_shift'] and scalar_error<d['scale_explanation_ratio']*translation_error)
    d_flag=bool(norm>=d['minimum_shift'] and coverage>=d['minimum_coverage'] and active>=d['minimum_active_coverage'] and not scale_explains)
    ab_error=np.linalg.norm(delta,axis=-1);hue_error=np.sqrt(np.maximum(0,ab_error**2-dc**2))
    metrics={'mean_c_gt':float(cg.mean()),'mean_c_model':float(cm.mean()),'chroma_ratio':ratio,
             'centered_spread_model':spread[1],'spread_ratio':spread_ratio,
             'hue_concentration_gt':concentrations[0],'hue_concentration_model':concentrations[1],
             'common_da':float(common[0]),'common_db':float(common[1]),'robust_shift_norm':norm,
             'common_coverage':coverage,'active_grid_coverage':active,
             'active_pixel_coverage':float(np.mean(ab_error>=d['activity_floor'])),
             'scalar_gain':gain,'scalar_intercept_norm':float(np.linalg.norm(intercept)),
             'scalar_fit_median_error':scalar_error,'translation_fit_median_error':translation_error,
             'cell_distances':distances.tolist(),'cell_norms':cell_norms.tolist(),
             'dc_p05':float(np.percentile(dc,5)),'dc_p95':float(np.percentile(dc,95)),
             'abs_dc_p95':float(np.percentile(np.abs(dc),95)),
             'hue_component_p90':float(np.percentile(hue_error,90)),
             'hue_component_max':float(hue_error.max())}
    flags={'a_candidate':a_flag,'d_candidate':d_flag,
           'monochrome_review_only':bool(concentrations[1]>=mono['minimum_hue_concentration'] and concentrations[1]-concentrations[0]>=mono['minimum_concentration_increase']),
           'scale_explains_shift':scale_explains,'automatic_final_decision':False}
    return metrics,flags,{'signed_dc':dc,'hue_component':hue_error,'ab_error':ab_error}


def regions(maps,config):
    """Connected numerical candidates, not semantic object masks; no extra images."""
    out=[];settings=config['regions'];h,w=maps['signed_dc'].shape
    signals={'chroma_gain':np.maximum(maps['signed_dc'],0),'chroma_loss':np.maximum(-maps['signed_dc'],0),'hue_change':maps['hue_component']}
    for kind,signal in signals.items():
        cutoff=max(settings['quantile_signal_floor'],float(np.percentile(signal,settings['quantile'])))
        mask=(signal>cutoff).astype(np.uint8)
        count,labels,stats,_=cv2.connectedComponentsWithStats(mask,connectivity=8)
        candidates=[]
        for i in range(1,count):
            x,y,bw,bh,area=map(int,stats[i])
            if area<settings['minimum_area_pixels']:continue
            strength=float(np.mean(signal[labels==i]))
            candidates.append({'kind':kind,'bbox_normalized':[x/w,y/h,(x+bw)/w,(y+bh)/h],
                               'pixel_fraction':area/(w*h),'mean_signal':strength,'selection_cutoff':cutoff})
        candidates.sort(key=lambda r:r['pixel_fraction']*r['mean_signal'],reverse=True)
        out.extend(candidates[:settings['maximum_per_kind']])
    for i,r in enumerate(out,1):r['region_id']=f'R{i}'
    return out


def heatmap(gt,gen,display):
    dc=chroma(gen)-chroma(gt)
    amplitude=np.clip((np.abs(dc)-display['deadzone'])/(display['maximum']-display['deadzone']),0,1)**display['gamma']
    colors=np.where((dc>0)[...,None],np.array([255,45,115]),np.array([35,185,255]))
    return np.rint(colors*amplitude[...,None]).astype(np.uint8)
