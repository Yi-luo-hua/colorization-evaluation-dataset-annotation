"""Brightness, hue-only and rotation controls for the optional ab-distance map."""
import copy
import unittest
from pathlib import Path
import numpy as np
import engine
from workflow import read_json


class DisplayChecks(unittest.TestCase):
    def setUp(self):
        self.display=copy.deepcopy(read_json(Path(__file__).with_name('config.json'))['display'])
        self.display['mode']='ab_distance_turbo'
        self.gt=np.zeros((8,8,3),np.float32);self.gt[...,0]=50;self.gt[...,1]=20

    def test_equal_chroma_hue_change_is_visible_but_luminance_is_excluded(self):
        hue=self.gt.copy();hue[...,1]=0;hue[...,2]=20
        original={**self.display,'mode':'signed_chroma'}
        self.assertEqual(np.count_nonzero(engine.heatmap(self.gt,hue,original)),0)
        self.assertTrue(np.all(np.any(engine.heatmap(self.gt,hue,self.display)>0,axis=-1)))
        light=self.gt.copy();light[...,0]+=30
        self.assertEqual(np.count_nonzero(engine.heatmap(self.gt,light,self.display)),0)

    def test_same_ab_distance_has_same_color_across_hue_and_chroma_changes(self):
        faded=self.gt.copy();faded[...,1]=0
        stronger=self.gt.copy();stronger[...,1]=40
        direction=self.gt.copy();direction[...,2]=20
        heat=engine.heatmap(self.gt,faded,self.display)
        np.testing.assert_array_equal(heat,engine.heatmap(self.gt,stronger,self.display))
        np.testing.assert_array_equal(heat,engine.heatmap(self.gt,direction,self.display))

    def test_identity_and_deadzone_stay_black(self):
        self.assertEqual(np.count_nonzero(engine.heatmap(self.gt,self.gt,self.display)),0)
        tiny=self.gt.copy();tiny[...,2]=self.display['deadzone']/2
        self.assertEqual(np.count_nonzero(engine.heatmap(self.gt,tiny,self.display)),0)

    def test_single_orange_palette_keeps_same_distance_and_excludes_luminance(self):
        display={**self.display,'mode':'ab_distance_orange'}
        hue=self.gt.copy();hue[...,1]=0;hue[...,2]=20
        self.assertTrue(np.all(engine.heatmap(self.gt,hue,display).sum(axis=-1)>0))
        light=self.gt.copy();light[...,0]+=30
        self.assertEqual(np.count_nonzero(engine.heatmap(self.gt,light,display)),0)
        faded=self.gt.copy();faded[...,1]=0;stronger=self.gt.copy();stronger[...,1]=40
        np.testing.assert_array_equal(engine.heatmap(self.gt,faded,display),engine.heatmap(self.gt,stronger,display))


if __name__=='__main__':unittest.main(verbosity=2)
