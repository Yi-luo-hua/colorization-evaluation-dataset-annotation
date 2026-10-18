"""Independent numerical/semantic invariants for the new CV explanations."""
import unittest
from pathlib import Path

import numpy as np

import engine
import global_models as gm
import region_models as rm
from workflow import read_json

SETTINGS=read_json(Path(__file__).with_name('config.json'))['global_models']['features']
REGIONS={'grow_fraction':0.25,'maximum_growth_bbox_fraction':0.8,'maximum_per_kind':2,
         'minimum_area_pixels':8,'quantile':95,'quantile_signal_floor':1.0}


class ModelChecks(unittest.TestCase):
    def test_fading_and_coloured_noise_are_not_exact_grayscale(self):
        cfg=read_json(Path(__file__).with_name('config.json'))
        y,x=np.mgrid[0:100,0:100];gt=np.zeros((100,100,3),np.float32);gt[...,0]=50
        gt[...,1]=np.where(((x//16+y//16)%2)==0,20,-20);gt[...,2]=10
        noise=np.random.default_rng(8).normal(0,0.5,gt[...,1:].shape)
        faded=gt.copy();faded[...,1:]=0.1*gt[...,1:]+noise
        _,flags,_=engine.measure(gt,faded,cfg)
        self.assertFalse(flags['a_candidate'])
        gray=gt.copy();gray[...,1:]=np.random.default_rng(8).normal(0,1,gt[...,1:].shape)
        _,flags,_=engine.measure(gt,gray,cfg)
        self.assertFalse(flags['a_candidate'])

    def test_dominant_object_change_vs_global_shift(self):
        cfg=read_json(Path(__file__).with_name('config.json'))
        gt=np.zeros((100,100,3),np.float32);gt[...,0]=50;gt[...,1:]=[-10,10]
        gt[80:,:33,1:]=[20,20];gt[80:,33:66,1:]=[0,-20];gt[80:,66:,1:]=[-20,-10]
        local=gt.copy();local[:80,:,1]+=12;local[80:,:,1]+=1.1
        _,flags,_=engine.measure(gt,local,cfg)
        self.assertTrue(flags['d_broad_candidate']);self.assertFalse(flags['d_candidate'])
        global_shift=gt.copy();global_shift[...,1]+=12
        _,flags,_=engine.measure(gt,global_shift,cfg)
        self.assertTrue(flags['d_candidate'])

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

    def test_A_ignores_GT_and_rejects_uniform_tint_and_wrong_local_colour(self):
        cfg=read_json(Path(__file__).with_name('config.json'))
        gray=np.full((80,80,3),128,np.uint8)
        colourful=gray.copy();colourful[:40]=[180,70,30];colourful[40:]=[30,80,190]
        tinted=np.full((80,80,3),[140,130,110],np.uint8)
        local=gray.copy();local[3:5,6:8]=[80,190,60]  # Colour need not match GT.
        for reference in [gray,colourful]:
            for generated,expected in [(gray,True),(tinted,False),(local,False)]:
                _,flags,_=engine.measure(engine.lab(reference),engine.lab(generated),cfg,generated_rgb=generated)
                self.assertEqual(flags['a_candidate'],expected)

    def test_original_resolution_colour_is_not_lost_by_analysis_resize(self):
        cfg=read_json(Path(__file__).with_name('config.json'))
        generated=np.full((1600,1600,3),128,np.uint8);generated[0,0]=[129,128,128]
        small=engine.resize_rgb(generated,cfg['analysis_max_side'])
        self.assertEqual(int(np.ptp(small.astype(np.int16),axis=-1).max()),0)
        _,flags,_=engine.measure(engine.lab(small),engine.lab(small),cfg,generated_rgb=generated)
        self.assertFalse(flags['a_candidate'])



if __name__=='__main__':unittest.main(verbosity=2)
