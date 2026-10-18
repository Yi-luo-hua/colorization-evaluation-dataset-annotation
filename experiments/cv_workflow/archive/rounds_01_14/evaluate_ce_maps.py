"""Fixed analytic display proposal, checked with physical controls on 24 GT sources."""
from pathlib import Path
import copy
import unittest
import cv2
import numpy as np
import engine
from workflow import OUTPUT,read_json,write_json


class SignalChecks(unittest.TestCase):
    def reference_display(self):
        display=read_json(Path(__file__).with_name('config.json'))['display']
        display.update(mode='signed_chroma',hue_weighting='raw')
        return display

    def test_equal_chroma_hue_change_is_visible(self):
        display=self.reference_display();display['hue_weighting']='min_chroma'
        gt=np.zeros((40,50,3),np.float32);gt[...,0]=50;gt[...,1:]=[20,0]
        gen=gt.copy();gen[...,1:]=[0,20]
        self.assertEqual(int(engine.heatmap(gt,gen,display).max()),0)
        self.assertGreater(int(engine.hue_heatmap(gt,gen,display).max()),100)
        self.assertEqual(int(engine.hue_heatmap(gt,gt,display).max()),0)

    def test_near_gray_hue_noise_does_not_compete_with_fading(self):
        display=self.reference_display()
        gt=np.zeros((40,50,3),np.float32);gt[...,0]=50;gt[...,1:]=[40,0]
        gen=gt.copy();gen[...,1:]=[0,0.1]
        self.assertGreater(int(engine.hue_heatmap(gt,gen,display).max()),0)
        display['hue_weighting']='min_chroma'
        self.assertEqual(int(engine.hue_heatmap(gt,gen,display).max()),0)
        self.assertGreater(int(engine.heatmap(gt,gen,display).max()),0)

    def test_composite_preserves_radial_loss_and_isolates_hue(self):
        display=self.reference_display()
        display.update(mode='chroma_hue_composite',hue_weighting='min_chroma')
        gt=np.zeros((40,50,3),np.float32);gt[...,0]=50;gt[...,1:]=[20,0]
        gen=gt.copy();gen[:,:25,1:]=[0,20];gen[:,25:,1:]=[10,0]
        heat=engine.heatmap(gt,gen,display)
        self.assertGreater(heat[10,10,0],heat[10,10,2])
        self.assertGreater(heat[10,35,2],heat[10,35,0])
        self.assertEqual(int(engine.heatmap(gt,gt,display).max()),0)

    def test_reliable_region_keeps_fading_and_removes_hue_noise(self):
        cfg=read_json(Path(__file__).with_name('config.json'))
        gt=np.zeros((80,80,3),np.float32);gt[...,0]=50;gt[...,1:]=[40,0]
        gen=gt.copy();gen[...,1:]=[0,.1];maps=engine.difference_maps(gt,gen)
        old=copy.deepcopy(cfg);old['regions'].pop('hue_signal',None)
        self.assertTrue(any(r['kind']=='hue_change' for r in engine.regions(maps,old)))
        new=engine.regions(maps,cfg)
        self.assertFalse(any(r['kind']=='hue_change' for r in new))
        self.assertTrue(any(r['kind']=='chroma_loss' for r in new))


def evaluate():
    cv2.setNumThreads(1);cfg=read_json(OUTPUT/'ce_signed_12_20261012/manifest.json')['configuration'];display=cfg['display']
    weighted=copy.deepcopy(display);weighted['hue_weighting']='min_chroma'
    samples=read_json(OUTPUT/'cv_d_groups_confirm_20261012/manifest.json')['samples'];rows=[]
    for image_id,stratum in samples:
        gt=engine.lab(engine.read_rgb(engine.ROOT/cfg['datasets']['val']/'image'/f'{image_id}.jpg',cfg['analysis_max_side']))
        controls=[]
        x=gt.copy();x[...,1:]=0;controls.append(('gray',engine.lab(engine.rgb(x))))
        x=gt.copy();x[...,1:]*=.1;controls.append(('radial_0.1',engine.lab(engine.rgb(x))))
        # Ideal Lab rotation isolates same-chroma hue information; RGB roundtrip separately checks gamut effects.
        x=gt.copy();x[...,1]=-gt[...,2];x[...,2]=gt[...,1];controls.extend([('hue90_ideal',x),('hue90_RGB',engine.lab(engine.rgb(x)))])
        for name,gen in controls:
            old=engine.hue_heatmap(gt,gen,display).max(-1)>0;new=engine.hue_heatmap(gt,gen,weighted).max(-1)>0
            signed=engine.heatmap(gt,gen,display).max(-1)>0
            eligible=engine.chroma(gt)>display['deadzone']
            rows.append({'image_id':image_id,'stratum':stratum,'control':name,
                         'raw_hue_visible_fraction':float(old.mean()),'weighted_hue_visible_fraction':float(new.mean()),
                         'signed_chroma_visible_fraction':float(signed.mean()),
                         'eligible_pixels':int(eligible.sum()),'raw_visible_eligible':int((old & eligible).sum()),
                         'weighted_visible_eligible':int((new & eligible).sum())})
    out=OUTPUT/'ce_display_round7_20261012';write_json(out/'numerical_records.json',rows)
    result={'GT_sources':len(samples),'controls':len(rows),'parameter_search':False,
            'GT_were_used_in_prior_D_confirmation':True,'semantic_C_E_accuracy_not_measured':True,
            'by_control':{name:{k:float(np.mean([r[k] for r in rows if r['control']==name])) for k in
                         ['raw_hue_visible_fraction','weighted_hue_visible_fraction','signed_chroma_visible_fraction']}
                         for name in sorted({r['control'] for r in rows})}}
    write_json(out/'numerical_results.json',result);print(result)


if __name__=='__main__':
    checks=unittest.main(exit=False,verbosity=2)
    if not checks.result.wasSuccessful():raise SystemExit(1)
    evaluate()
