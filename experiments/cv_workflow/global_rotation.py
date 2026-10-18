"""Common hue rotation evidence across GT colour groups and spatial cells.

Thresholds are fitted externally; groups/cells are not semantic objects.
"""
import numpy as np
import d_color_groups


def quantile(values,weights,q):
    values=np.asarray(values);weights=np.asarray(weights)
    if not len(values) or weights.sum()==0:return 0.0
    order=np.argsort(values);x=values[order];w=weights[order]
    return float(np.interp(q*w.sum(),np.cumsum(w),x))


def angular_mean(angles,weights):
    return float(np.degrees(np.angle(np.sum(weights*np.exp(1j*np.radians(angles))))))


def measure(gt,gen,config):
    x=gt[...,1:];y=gen[...,1:]
    cross=x[...,0]*y[...,1]-x[...,1]*y[...,0]
    dot=np.sum(x*y,axis=-1)
    angles=np.degrees(np.arctan2(cross,dot))
    # Continuous chroma weight avoids making nearly-grey angles decisive.
    weight=np.minimum(np.linalg.norm(x,axis=-1),np.linalg.norm(y,axis=-1))
    settings=config['global_models']['d']['color_groups']['features'];stride=settings['stride']
    groups=d_color_groups.prepare_groups(gt,settings)
    flat_angle=angles.reshape(-1)[::stride];flat_weight=weight.reshape(-1)[::stride]
    group_angles=np.array([angular_mean(flat_angle[ix],flat_weight[ix]) for ix in groups])
    group_weights=np.array([np.median(flat_weight[ix]) for ix in groups])
    if group_weights.sum()==0:
        return {'common_degrees':0.0,'group_q10_along_common':0.0,'cell_q10_along_common':0.0,'score_degrees':0.0,'group_count':len(groups)}
    distance=np.abs((group_angles[:,None]-group_angles[None,:]+180)%360-180)
    common=float(group_angles[np.argmin(distance@group_weights)])
    direction=np.sign(common)
    group_q=quantile(direction*group_angles,group_weights,0.1)
    cell_angles=[];cell_weights=[]
    for ar,wr in zip(np.array_split(angles,config['grid_size'],0),np.array_split(weight,config['grid_size'],0)):
        for a,w in zip(np.array_split(ar,config['grid_size'],1),np.array_split(wr,config['grid_size'],1)):
            cell_angles.append(angular_mean(a,w));cell_weights.append(float(w.mean()))
    cell_q=quantile(direction*np.array(cell_angles),cell_weights,0.1)
    score=max(0.0,min(abs(common),group_q,cell_q))
    return {'common_degrees':common,'group_q10_along_common':group_q,'cell_q10_along_common':cell_q,
            'score_degrees':score,'group_count':len(groups)}


def fit(rows):
    scores=sorted(set(r['rotation']['score_degrees'] for r in rows))
    thresholds=[scores[0]/2]+[(a+b)/2 for a,b in zip(scores,scores[1:])]+[scores[-1]+1]
    results=[]
    for threshold in thresholds:
        fp=fn=0
        for row in rows:
            predicted=row['baseline_D'] or row['rotation']['score_degrees']>=threshold
            fp+=int(predicted and not row['physical_global_target'])
            fn+=int(not predicted and row['physical_global_target'])
        results.append({'minimum_rotation_score_degrees':threshold,'false_positive':fp,'false_negative':fn,'cost':2*fp+fn})
    best=min(results,key=lambda r:(r['cost'],r['false_positive'],-r['minimum_rotation_score_degrees']))
    return {'rule':best,'search':results,'fit_objective':'2*physical_local_or_scale_FP + physical_global_FN; development only',
            'semantic_limit':'A full-frame transform or numerical colour group does not prove multi-object D.'}
