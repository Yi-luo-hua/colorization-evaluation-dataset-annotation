"""Rotation v2: faded GT regions retain their vote on spatial/colour scope.

The common angle uses visible colour; scope support is attenuated by retained
chroma and weighted by GT chroma. No semantic D label follows from this score.
"""
import numpy as np
import d_color_groups
from global_rotation import angular_mean, quantile, fit


def measure(gt, gen, config, support_quantile=.1):
    x=gt[...,1:];y=gen[...,1:]
    cg=np.linalg.norm(x,axis=-1);cm=np.linalg.norm(y,axis=-1)
    visible=np.minimum(cg,cm)
    angles=np.degrees(np.arctan2(x[...,0]*y[...,1]-x[...,1]*y[...,0],np.sum(x*y,axis=-1)))
    retention=np.divide(visible,cg,out=np.zeros_like(cg),where=cg>0)
    supported=angles*retention
    settings=config['global_models']['d']['color_groups']['features']
    groups=d_color_groups.prepare_groups(gt,settings);stride=settings['stride']
    a=angles.reshape(-1)[::stride];v=visible.reshape(-1)[::stride]
    s=supported.reshape(-1)[::stride];g=cg.reshape(-1)[::stride]
    ga=np.array([angular_mean(a[ix],v[ix]) for ix in groups])
    vw=np.array([np.median(v[ix]) for ix in groups])
    gw=np.array([np.median(g[ix]) for ix in groups])
    common=0.0
    if vw.sum()>0:
        distance=np.abs((ga[:,None]-ga[None,:]+180)%360-180)
        common=float(ga[np.argmin(distance@vw)])
    sign=np.sign(common)
    gs=np.array([angular_mean(s[ix],g[ix]) for ix in groups])
    group_q=quantile(sign*gs,gw,support_quantile)
    ca=[];cw=[]
    for sr,gr in zip(np.array_split(supported,config['grid_size'],0),np.array_split(cg,config['grid_size'],0)):
        for sc,gc in zip(np.array_split(sr,config['grid_size'],1),np.array_split(gr,config['grid_size'],1)):
            ca.append(angular_mean(sc,gc));cw.append(float(gc.mean()))
    cell_q=quantile(sign*np.array(ca),cw,support_quantile)
    return {'common_degrees':common,'group_q10_along_common':group_q,'cell_q10_along_common':cell_q,
            'score_degrees':max(0.0,min(abs(common),group_q,cell_q)), 'group_count':len(groups),
            'method':'GT_weighted_retained_chroma_support_v2','support_quantile':support_quantile,
            'mean_retention_GT_weighted':float(visible.sum()/cg.sum()) if cg.sum()>0 else 0.0}
