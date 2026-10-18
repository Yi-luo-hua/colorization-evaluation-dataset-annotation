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
    return resize_rgb(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB),max_side)


def resize_rgb(image,max_side=None):
    if max_side and max(image.shape[:2])>max_side:
        ratio=max_side/max(image.shape[:2])
        return cv2.resize(image,(round(image.shape[1]*ratio),round(image.shape[0]*ratio)),interpolation=cv2.INTER_AREA)
    return image


def lab(rgb):
    return cv2.cvtColor(rgb.astype(np.float32)/255,cv2.COLOR_RGB2LAB)


def rgb(lab_image):
    return np.clip(np.rint(cv2.cvtColor(lab_image.astype(np.float32),cv2.COLOR_LAB2RGB)*255),0,255).astype(np.uint8)


def chroma(image):return np.linalg.norm(image[...,1:],axis=-1)


def difference_maps(gt,gen,evidence_settings=None):
    cg,cm=chroma(gt),chroma(gen);dc=cm-cg;ab=np.linalg.norm(gen[...,1:]-gt[...,1:],axis=-1)
    hue=np.sqrt(np.maximum(0,ab**2-dc**2))
    maps={'signed_dc':dc,'hue_component':hue,'hue_direction':reliable_hue(hue,cg,cm),'ab_error':ab}
    if evidence_settings:
        import color_evidence
        maps.update(color_evidence.measure(gt,gen,evidence_settings))
    return maps


def reliable_hue(hue,cg,cm):
    return hue*np.sqrt(np.minimum(cg,cm)/(np.maximum(cg,cm)+1e-8))


def measure(gt,gen,config,generated_rgb=None):
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
    d=config['d']
    ratio=float(cm.mean()/(cg.mean()+1e-8));spread_ratio=spread[1]/(spread[0]+1e-8)
    coverage=float(np.mean(distances<=d['absolute_tolerance']+d['relative_tolerance']*norm))
    active=float(np.mean(cell_norms>=d['activity_floor']))
    scale_explains=bool(gain>0 and np.linalg.norm(intercept)<d['minimum_shift'] and scalar_error<d['scale_explanation_ratio']*translation_error)
    d_flag=bool(norm>=d['minimum_shift'] and coverage>=d['minimum_coverage'] and active>=d['minimum_active_coverage'] and not scale_explains)
    ab_error=np.linalg.norm(delta,axis=-1);hue_error=np.sqrt(np.maximum(0,ab_error**2-dc**2))
    hue_direction=reliable_hue(hue_error,cg,cm)
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
             'hue_direction_p90':float(np.percentile(hue_direction,90)),
             'hue_component_max':float(hue_error.max())}
    flags={'d_candidate':d_flag,
           'scale_explains_shift':scale_explains,'automatic_final_decision':False}
    if 'global_models' in config:
        import global_models as gm
        models=gm.measure(gt,gen,config['global_models']['features'])
        row={'baseline_d':d_flag,'metrics':metrics,'models':models}
        flags.update(d_candidate=gm.predict_d(row,config['global_models']['d']))
        metrics['global_models']=models
        domain,best=min(models['gain_models'].items(),key=lambda pair:pair[1]['residual_p98'])
        metrics['gain_fit_domain']=domain
        metrics['gain_fit_residual']=best['residual_p98']
        metrics['gain_channel_imbalance']=best['relative_gain_spread']
        group_settings=config['global_models']['d'].get('color_groups')
        if group_settings:
            import d_color_groups as grouping
            evidence=grouping.measure(gt,gen,grouping.prepare_groups(gt,group_settings['features']),group_settings)
            metrics['color_groups']=evidence
            metrics['color_group_projection_q']=evidence['projection_q']
            metrics['color_group_shift_norm']=evidence['shift_norm']
            metrics['color_group_direction_coverage']=evidence['direction_coverage']
            flags['d_broad_candidate']=flags['d_candidate']
            flags['d_candidate']=grouping.predict({'baseline_d':flags['d_broad_candidate'],
                'scale_explains_shift':scale_explains,'metrics':metrics,'group_features':evidence},group_settings['rule'],config)
    rotation_settings=config.get('experimental_d_rotation')
    if rotation_settings:
        import global_rotation_supported as rotation
        evidence=rotation.measure(gt,gen,config,rotation_settings['support_quantile'])
        metrics['rotation_evidence']=evidence
        flags['d_before_rotation_candidate']=flags['d_candidate']
        flags['d_rotation_candidate']=evidence['score_degrees']>=rotation_settings['minimum_score_degrees']
        flags['d_candidate']=flags['d_candidate'] or flags['d_rotation_candidate']
    maps={'signed_dc':dc,'hue_component':hue_error,'hue_direction':hue_direction,'ab_error':ab_error}
    if config.get('color_evidence'):
        import color_evidence
        extra=color_evidence.measure(gt,gen,config['color_evidence']);maps.update(extra)
        metrics['color_evidence']={key+'_p95':float(np.percentile(value,95)) for key,value in extra.items()}
    if config.get('bleed_evidence'):
        import bleed_probe
        metrics['bleed_evidence']=bleed_probe.summary(bleed_probe.measure(gt,gen,config['bleed_evidence']),config['bleed_evidence'])
        flags['b_candidate']=metrics['bleed_evidence']['candidate']
    return metrics,flags,maps


def regions(maps,config,prefer_compact=False):
    """Connected numerical candidates, not semantic object masks; no extra images."""
    out=[];settings=config['regions'];h,w=maps['signed_dc'].shape
    if settings.get('hue_signal')=='hue_direction':maps={**maps,'hue_component':maps['hue_direction']}
    if settings.get('hue_signal')=='retained_hue':maps={**maps,'hue_component':maps['retained_hue']}
    if 'grow_fraction' in settings:
        import region_models
        return region_models.anchored_regions(maps,settings,prefer_compact=prefer_compact)
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
    if display.get('mode') in ['ab_distance_turbo','ab_distance_orange']:
        strength=np.linalg.norm(gen[...,1:]-gt[...,1:],axis=-1)
        amplitude=np.clip((strength-display['deadzone'])/(display['maximum']-display['deadzone']),0,1)**display['gamma']
        if display['mode']=='ab_distance_orange':return np.rint(np.array([255,185,35])*amplitude[...,None]).astype(np.uint8)
        heat=cv2.cvtColor(cv2.applyColorMap(np.rint(amplitude*255).astype(np.uint8),cv2.COLORMAP_TURBO),cv2.COLOR_BGR2RGB)
        heat[strength<=display['deadzone']]=0
        return heat
    dc=chroma(gen)-chroma(gt)
    strength=np.abs(dc)
    colors=np.where((dc>0)[...,None],np.array([255,45,115]),np.array([35,185,255]))
    if display.get('mode')=='chroma_hue_composite':
        hue=hue_display_signal(gt,gen,display)
        colors=np.where((hue>strength)[...,None],np.array([255,185,35]),colors)
        strength=np.maximum(strength,hue)
    amplitude=np.clip((strength-display['deadzone'])/(display['maximum']-display['deadzone']),0,1)**display['gamma']
    return np.rint(colors*amplitude[...,None]).astype(np.uint8)


def hue_display_signal(gt,gen,display):
    maps=difference_maps(gt,gen)
    return maps['hue_direction'] if display.get('hue_weighting')=='min_chroma' else maps['hue_component']


def hue_heatmap(gt,gen,display):
    signal=hue_display_signal(gt,gen,display)
    amplitude=np.clip((signal-display['deadzone'])/(display['maximum']-display['deadzone']),0,1)**display['gamma']
    return np.rint(np.array([255,185,35])*amplitude[...,None]).astype(np.uint8)
