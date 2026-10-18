"""Alternative global explanations and brightness-conditioned color structure.

sRGB transfer functions: https://www.w3.org/TR/css-color-4/#predefined-sRGB
All classification cutoffs live in experiment configuration, not this module.
"""
import cv2
import numpy as np


def to_linear(values):
    return np.where(values<=0.04045,values/12.92,((values+0.055)/1.055)**2.4)


def to_srgb(values):
    values=np.clip(values,0,1)
    return np.where(values<=0.0031308,12.92*values,1.055*values**(1/2.4)-0.055)


def color_curve_residual(image,bins,stride):
    """Cross-fit ab(L) on disjoint pixels: no same-pixel interpolation optimism."""
    flat=image.reshape(-1,3)[::stride]
    residuals=[]
    for fold in [0,1]:
        train=flat[fold::2];test=flat[1-fold::2]
        ordering=np.argsort(train[:,0]);groups=np.array_split(ordering,bins)
        centers=np.array([[np.median(train[g,0]),*np.median(train[g,1:],axis=0)] for g in groups if len(g)])
        unique,indices=np.unique(centers[:,0],return_index=True);centers=centers[indices]
        prediction=np.column_stack([np.interp(test[:,0],unique,centers[:,c]) for c in [1,2]])
        residuals.extend(np.linalg.norm(test[:,1:]-prediction,axis=1).tolist())
    return {f'p{q}':float(np.percentile(residuals,q)) for q in [50,95,99]}


def gain_explanation(gt,gen,settings):
    # Lab input originated from 8-bit RGB. Roundtrip here recovers the same domain.
    x=cv2.cvtColor(gt.astype(np.float32),cv2.COLOR_LAB2RGB)
    y=cv2.cvtColor(gen.astype(np.float32),cv2.COLOR_LAB2RGB)
    x=np.rint(np.clip(x,0,1)*255)/255;y=np.rint(np.clip(y,0,1)*255)/255
    output={}
    for domain in ['encoded','linear']:
        xx=x if domain=='encoded' else to_linear(x)
        yy=y if domain=='encoded' else to_linear(y)
        gains=[];fractions=[]
        for c in range(3):
            valid=(x[...,c]>=settings['signal_floor']) & (x[...,c]<1-1/255) & (y[...,c]>1/255) & (y[...,c]<1-1/255)
            fractions.append(float(valid.mean()))
            gains.append(float(np.median(yy[...,c][valid]/xx[...,c][valid])) if valid.any() else 1.0)
        prediction=np.clip(xx*np.array(gains),0,1)
        if domain=='linear':prediction=to_srgb(prediction)
        pred_lab=cv2.cvtColor(prediction.astype(np.float32),cv2.COLOR_RGB2LAB)
        residual=np.linalg.norm(pred_lab[...,1:]-gen[...,1:],axis=-1)
        effect=np.linalg.norm(pred_lab[...,1:]-gt[...,1:],axis=-1)
        geometric_mean=float(np.exp(np.mean(np.log(np.maximum(gains,1e-8)))))
        relative=np.array(gains)/geometric_mean
        output[domain]={'gains':gains,'fit_valid_fraction':min(fractions),
                        'relative_gain_spread':float(relative.max()-relative.min()),
                        'residual_p95':float(np.percentile(residual,95)),
                        'residual_p98':float(np.percentile(residual,98)),
                        'effect_p50':float(np.percentile(effect,50)),'effect_p95':float(np.percentile(effect,95))}
    return output


def measure(gt,gen,settings):
    return {'gain_models':gain_explanation(gt,gen,settings)}


def predict_d(row,params):
    encoded=row['models']['gain_models']['encoded']
    exposure=(encoded['fit_valid_fraction']>=params['minimum_fit_fraction'] and
              encoded['relative_gain_spread']<params['minimum_gain_spread'] and
              encoded['residual_p98']<=params['maximum_gain_residual_p98'])
    if exposure:return False
    translation=row['baseline_d'] and row['metrics']['active_pixel_coverage']>=params['minimum_pixel_coverage']
    gains=False
    for model in row['models']['gain_models'].values():
        gains |= (model['fit_valid_fraction']>=params['minimum_fit_fraction'] and
                  model['relative_gain_spread']>=params['minimum_gain_spread'] and
                  model['residual_p98']<=params['maximum_gain_residual_p98'] and
                  model['effect_p50']>=params['minimum_gain_effect'])
    return bool(translation or gains)
