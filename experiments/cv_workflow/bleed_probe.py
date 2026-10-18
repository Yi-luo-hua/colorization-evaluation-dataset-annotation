"""Offline boundary-normal near/far colour assimilation evidence, not B labels."""
import cv2
import numpy as np


def measure(gt,gen,settings):
    if settings.get('remove_common_ab_shift'):
        # B is local contamination, so remove the shared whole-image translation.
        gen=gen.copy()
        gen[...,1:]-=np.median((gen[...,1:]-gt[...,1:]).reshape(-1,2),axis=0)
    h,w=gt.shape[:2];near=min(h,w)*settings['near_fraction'];far=min(h,w)*settings['far_fraction']
    gx=cv2.Sobel(gt[...,0],cv2.CV_32F,1,0,ksize=3);gy=cv2.Sobel(gt[...,0],cv2.CV_32F,0,1,ksize=3)
    magnitude=np.hypot(gx,gy);positive=magnitude[magnitude>0]
    output=np.zeros((h,w),np.float32)
    if not len(positive):return output
    high=np.quantile(positive,settings['edge_quantile']);seeds=magnitude>=high
    support=magnitude>=high*settings.get('edge_grow_fraction',1.0)
    _,labels=cv2.connectedComponents(support.astype(np.uint8),connectivity=8)
    keep=np.unique(labels[seeds]);keep=keep[keep!=0]
    edge=np.isin(labels,keep)
    nx=gx/(magnitude+1e-8);ny=gy/(magnitude+1e-8);yy,xx=np.indices((h,w),dtype=np.float32)
    edge &= (xx>far)&(xx<w-1-far)&(yy>far)&(yy<h-1-far)
    def sample(image,offset):return cv2.remap(image,(xx+offset*nx).astype(np.float32),(yy+offset*ny).astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
    for direction in [-1,1]:
        inside=sample(gt,-direction*near);outside=sample(gt,direction*near);distant=sample(gt,direction*far)
        donor_distant=sample(gt,-direction*far)
        model_inside=sample(gen,-direction*near);model_outside=sample(gen,direction*near);model_distant=sample(gen,direction*far)
        vector=inside[...,1:]-outside[...,1:];squared=np.sum(vector*vector,axis=-1);contrast=np.sqrt(squared)
        error=model_outside[...,1:]-outside[...,1:];far_error=model_distant[...,1:]-distant[...,1:]
        t=np.sum(error*vector,axis=-1)/(squared+1e-8);tf=np.sum(far_error*vector,axis=-1)/(squared+1e-8)
        error_norm=np.linalg.norm(error,axis=-1)
        orthogonal=np.linalg.norm(error-t[...,None]*vector,axis=-1)
        own_error=np.linalg.norm(model_inside[...,1:]-inside[...,1:],axis=-1)
        side_variation=np.linalg.norm(distant[...,1:]-outside[...,1:],axis=-1)
        directionality=np.maximum(0,1-orthogonal/(error_norm+1e-8))
        source_retained=np.maximum(0,1-own_error/(error_norm+1e-8))
        coherent_side=np.maximum(0,1-side_variation/(contrast+1e-8))
        if settings.get('require_stable_donor_side'):
            donor_variation=np.linalg.norm(donor_distant[...,1:]-inside[...,1:],axis=-1)
            coherent_side*=np.maximum(0,1-donor_variation/(contrast+1e-8))
        l_contrast=np.abs(inside[...,0]-outside[...,0])
        alignment=np.maximum(0,1-np.abs(model_outside[...,0]-outside[...,0])/(l_contrast+1e-8))
        # The near side must move TOWARDS the donor. A more negative far-side
        # movement cannot turn near-side movement away from the donor into leakage.
        infection=np.minimum(np.maximum(0,t),np.maximum(0,t-tf))
        score=infection*directionality*source_retained*coherent_side*alignment
        if settings.get('require_retained_recipient_far_side'):
            # Whole-recipient recolouring is weak evidence of boundary leakage.
            # Retain local contamination when the distant recipient keeps its colour.
            far_error_norm=np.linalg.norm(far_error,axis=-1)
            score*=np.maximum(0,1-far_error_norm/(error_norm+1e-8))
        if 'reference_low_chroma' in settings:
            # Weak/grey donors and mere desaturation are poor colour-infection evidence.
            donor=np.minimum(np.linalg.norm(inside[...,1:],axis=-1),np.linalg.norm(model_inside[...,1:],axis=-1))
            donor_support=np.maximum(0,donor-settings['reference_low_chroma'])/(donor+1e-8)
            contrast_support=np.maximum(0,contrast-settings['reference_low_chroma'])/(contrast+1e-8)
            model_separation=np.linalg.norm(model_inside[...,1:]-model_outside[...,1:],axis=-1)
            convergence=np.maximum(0,1-model_separation/(contrast+1e-8))
            score*=donor_support*contrast_support*convergence
            if settings.get('gt_color_direction_support'):
                # Same-hue shading/chroma contrast is weak evidence of two colours.
                # A neutral recipient is retained: coloured material can bleed onto white.
                ci=np.linalg.norm(inside[...,1:],axis=-1)
                co=np.linalg.norm(outside[...,1:],axis=-1)
                hue_gap=np.sqrt(np.maximum(0,squared-(ci-co)**2))
                neutral=settings['reference_low_chroma']/(np.minimum(ci,co)+settings['reference_low_chroma'])
                score*=neutral+(1-neutral)*hue_gap/(contrast+1e-8)
        output=np.maximum(output,np.where(edge,score,0).astype(np.float32))
    return output


def longest(score,cutoff):
    count,_,stats,_=cv2.connectedComponentsWithStats((score>cutoff).astype(np.uint8),connectivity=8)
    return float(stats[1:,cv2.CC_STAT_AREA].max()/max(score.shape)) if count>1 else 0.0


def summary(score,settings):
    count,labels,stats,centres=cv2.connectedComponentsWithStats((score>settings['score_cutoff']).astype(np.uint8),connectivity=8)
    extent=float(stats[1:,cv2.CC_STAT_AREA].max()/max(score.shape)) if count>1 else 0.0
    candidate=extent>settings['minimum_connected_extent']
    result={'candidate':candidate,'peak_response':float(score.max()),'connected_extent':extent}
    if candidate:
        largest=1+int(np.argmax(stats[1:,cv2.CC_STAT_AREA]));h,w=score.shape
        result['center_percent']=[round(100*centres[largest,0]/w),round(100*centres[largest,1]/h)]
    return result
