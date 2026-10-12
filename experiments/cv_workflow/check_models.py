"""Independent numerical/semantic invariants for the new CV explanations."""
import unittest
from pathlib import Path

import numpy as np

import engine
import global_models as gm
import region_models as rm
from workflow import read_json

SETTINGS=read_json(Path(__file__).with_name('optimization_config.json'))['features']
REGIONS={'grow_fraction':0.25,'maximum_growth_bbox_fraction':0.8,'maximum_per_kind':2,
         'minimum_area_pixels':8,'quantile':95,'quantile_signal_floor':1.0}


class ModelChecks(unittest.TestCase):
    def test_srgb_known_values_and_roundtrip(self):
        rgb=np.array([0,0.04045,0.5,1.0])
        np.testing.assert_allclose(gm.to_linear(rgb),[0,0.00313080495356,0.214041140482,1],atol=1e-10)
        np.testing.assert_allclose(gm.to_srgb(gm.to_linear(rgb)),rgb,atol=3e-8)

    def test_known_encoded_gain_recovery(self):
        y,x=np.mgrid[0:100,0:120];rgb=np.stack([0.15+0.5*x/120,0.1+0.45*y/100,0.2+0.4*(x+y)/220],axis=-1)
        gains=np.array([1.1,1.0,0.9]);gt=engine.lab(np.rint(rgb*255).astype(np.uint8));gen=engine.lab(np.rint(rgb*gains*255).astype(np.uint8))
        model=gm.gain_explanation(gt,gen,SETTINGS)['encoded']
        np.testing.assert_allclose(model['gains'],gains,atol=0.01)
        self.assertLess(model['residual_p98'],0.75)

    def test_plateau_at_quantile_is_not_lost(self):
        signal=np.zeros((100,100),np.float32);signal[10:35,20:60]=10
        maps={'signed_dc':signal,'hue_component':np.zeros_like(signal)}
        new=rm.anchored_regions(maps,REGIONS)
        self.assertTrue(any(r['bbox_normalized']==[0.2,0.1,0.6,0.35] and r['kind']=='chroma_gain' for r in new))

    def test_full_monochrome_vs_retained_color(self):
        y,x=np.mgrid[0:100,0:100];gt=np.zeros((100,100,3),np.float32);gt[...,0]=50
        gt[...,1]=np.where(((x//16+y//16)%2)==0,20,-20);gt[...,2]=10
        gen=gt.copy();gen[...,1]=6;gen[...,2]=9
        params={'quantile':95,'minimum_gt_curve_residual':0.5,'maximum_model_curve_residual':2,'maximum_curve_ratio':0.15,'maximum_retained_fraction':0.005}
        row={'baseline_a':False,'models':gm.measure(gt,gen,SETTINGS)}
        self.assertTrue(gm.predict_a(row,params))
        gen[:10,:10]=gt[:10,:10];row['models']=gm.measure(gt,gen,SETTINGS)
        self.assertFalse(gm.predict_a(row,params))

    def test_identical_gray_reference_is_not_coloring_failure(self):
        image=np.zeros((80,80,3),np.float32);image[...,0]=50
        params={'quantile':95,'minimum_gt_curve_residual':0.5,'maximum_model_curve_residual':2,'maximum_curve_ratio':0.15,'maximum_retained_fraction':0.005}
        row={'baseline_a':True,'models':gm.measure(image,image,SETTINGS)}
        self.assertFalse(gm.predict_a(row,params))

    def test_severe_desaturation_preserves_reference_color_pattern(self):
        y,x=np.mgrid[0:80,0:80];gt=np.zeros((80,80,3),np.float32);gt[...,0]=50
        gt[...,1]=np.where((x//16+y//16)%2==0,20,-20);gt[...,2]=10
        gen=gt.copy();gen[...,1:]*=0.1
        params={'quantile':95,'minimum_gt_curve_residual':0.5,'maximum_model_curve_residual':2,'maximum_curve_ratio':0.15,'maximum_retained_fraction':0.005,
                'scale_competition':{'minimum_retained_gain':0.03,'maximum_intercept':0.5,'maximum_residual':0.5}}
        row={'baseline_a':True,'models':gm.measure(gt,gen,SETTINGS),
             'metrics':{'scalar_gain':0.1,'scalar_intercept_norm':0,'scalar_fit_median_error':0}}
        self.assertFalse(gm.predict_a(row,params))


if __name__=='__main__':unittest.main(verbosity=2)
