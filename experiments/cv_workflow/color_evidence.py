"""Local colour evidence after removing same-hue chroma scaling.

Low chroma weakens the evidence continuously. This produces no defect labels.
"""
import cv2
import numpy as np


def measure(gt,gen,settings):
    x=gt[...,1:];y=gen[...,1:]
    cg=np.linalg.norm(x,axis=-1);cm=np.linalg.norm(y,axis=-1)
    gain=np.maximum(0,np.sum(x*y,axis=-1)/(cg*cg+1e-8))
    residual=np.linalg.norm(y-gain[...,None]*x,axis=-1)
    retained=np.minimum(cg,cm)
    support=np.maximum(0,retained-settings['reference_low_chroma'])/(retained+1e-8)
    hue=residual*support
    return {'retained_hue':hue,'chroma_loss':np.maximum(0,cg-cm),'chroma_gain':np.maximum(0,cm-cg)}


def outline(heat,gt,gen,settings):
    h,w=heat.shape[:2];ratio=min(1,settings['max_side']/max(h,w))
    size=(round(w*ratio),round(h*ratio))
    small_gt=cv2.resize(gt,size,interpolation=cv2.INTER_AREA)
    small_gen=cv2.resize(gen,size,interpolation=cv2.INTER_AREA)
    signal=measure(small_gt,small_gen,settings)['retained_hue']
    cutoff=max(settings['minimum_signal'],float(np.percentile(signal,settings['selection_quantile'])))
    count,labels,stats,_=cv2.connectedComponentsWithStats((signal>cutoff).astype(np.uint8),connectivity=8)
    selected=sorted([i for i in range(1,count) if stats[i,cv2.CC_STAT_AREA]>=settings['minimum_area_pixels']],
        key=lambda i:stats[i,cv2.CC_STAT_AREA]*float(signal[labels==i].mean()),reverse=True)[:settings['maximum_regions']]
    mask=np.isin(labels,selected).astype(np.uint8)
    mask=cv2.resize(mask,(w,h),interpolation=cv2.INTER_NEAREST)
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    result=heat.copy();width=max(1,round(settings['contour_width']*max(h,w)/settings['render_reference_side']))
    cv2.drawContours(result,contours,-1,(255,185,35),width,lineType=cv2.LINE_AA)
    return result
