"""Independent controls:rotation versus scaling/selective change and ambiguity."""
import unittest
import copy
from pathlib import Path
import numpy as np
from workflow import read_json
from global_rotation_supported import measure
from compact_harness import build_prompt,cv_hint_text
import engine


class RotationChecks(unittest.TestCase):
    def setUp(self):
        self.cfg=read_json(Path(__file__).with_name('config.json'))
        self.gt=np.empty((64,64,3),np.float32);self.gt[...,0]=60
        for (y,x),ab in zip([(0,0),(0,32),(32,0),(32,32)],[[20,10],[-20,25],[-10,-20],[30,-10]]):self.gt[y:y+32,x:x+32,1:]=ab
        t=np.radians(35);self.R=np.array([[np.cos(t),-np.sin(t)],[np.sin(t),np.cos(t)]])

    def test_global_rotation_detected_even_when_delta_directions_differ(self):
        gen=self.gt.copy();gen[...,1:]=gen[...,1:]@self.R.T
        self.assertAlmostEqual(measure(self.gt,gen,self.cfg)['score_degrees'],35,places=4)

    def test_chroma_scaling_is_not_common_hue_rotation(self):
        gen=self.gt.copy();gen[...,1:]*=.4
        self.assertLess(measure(self.gt,gen,self.cfg)['score_degrees'],.01)

    def test_unchanged_spatial_area_rejects_selective_rotation(self):
        gen=self.gt.copy();gen[:,:48,1:]=gen[:,:48,1:]@self.R.T
        self.assertLess(measure(self.gt,gen,self.cfg)['score_degrees'],1)

    def test_single_coloured_object_global_and_local_transform_can_be_identical(self):
        gt=np.zeros((64,64,3),np.float32);gt[...,0]=60;gt[16:48,16:48,1:]=[20,10]
        global_gen=gt.copy();global_gen[...,1:]=gt[...,1:]@self.R.T
        local=gt.copy();local[16:48,16:48,1:]=local[16:48,16:48,1:]@self.R.T
        np.testing.assert_array_equal(global_gen,local)
        self.assertEqual(measure(gt,global_gen,self.cfg),measure(gt,local,self.cfg))

    def test_grayscale_has_no_defined_rotation_evidence(self):
        gt=np.zeros((64,64,3),np.float32);gt[...,0]=60
        self.assertEqual(measure(gt,gt,self.cfg)['score_degrees'],0)

    def test_faded_regions_do_not_disappear_from_scope_vote(self):
        gen=self.gt.copy();gen[...,1:]*=.05
        gen[:32,:32,1:]=self.gt[:32,:32,1:]@self.R.T
        self.assertLess(measure(self.gt,gen,self.cfg)['score_degrees'],1)

    def test_nearly_gray_rotation_has_weak_support(self):
        gen=self.gt.copy();gen[...,1:]=gen[...,1:]@self.R.T*.05
        self.assertAlmostEqual(measure(self.gt,gen,self.cfg)['score_degrees'],1.75,places=4)

    def test_moderate_fade_keeps_rotation_support(self):
        gen=self.gt.copy();gen[...,1:]=gen[...,1:]@self.R.T*.55
        self.assertAlmostEqual(measure(self.gt,gen,self.cfg)['score_degrees'],19.25,places=4)

    def test_positive_only_hint_does_not_deny_other_global_casts(self):
        request={'annotation_contract':self.cfg['annotation_contract'],'visual_harness':{
            'd_rotation_evidence':True,'d_rotation_positive_only':True,'rotation_threshold_degrees':15},
            'samples':[{'sample_key':key,'sheet':'sheet.png','rotation_evidence':{
            'score_degrees':score,'common_degrees':score,'group_q10_along_common':score,
            'cell_q10_along_common':score,'method':'GT_weighted_retained_chroma_support_v2'}} for key,score in [('S001',30),('S002',0)]]}
        prompt=build_prompt(request,'reviews.json')
        self.assertIn('S001：共同角30°',prompt);self.assertNotIn('S002：共同角',prompt)
        self.assertNotIn('旋转D候选否',prompt);self.assertIn('未列不代表没有D',prompt)
        request['visual_harness']['d_rotation_evidence']=False
        self.assertNotIn('共同色相旋转证据',build_prompt(request,'reviews.json'))

    def test_workflow_option_adds_candidate_without_changing_A_or_other_maps(self):
        gen=self.gt.copy();gen[...,1:]=gen[...,1:]@self.R.T;rgb=engine.rgb(gen)
        old_metrics,old_flags,old_maps=engine.measure(self.gt,gen,self.cfg,generated_rgb=rgb)
        self.assertNotIn('rotation_evidence',old_metrics)
        cfg=copy.deepcopy(self.cfg);cfg['experimental_d_rotation']={'support_quantile':.1,'minimum_score_degrees':15}
        metrics,flags,maps=engine.measure(self.gt,gen,cfg,generated_rgb=rgb)
        self.assertTrue(flags['d_rotation_candidate']);self.assertTrue(flags['d_candidate'])
        self.assertFalse(flags['automatic_final_decision']);self.assertEqual(flags['a_candidate'],old_flags['a_candidate'])
        self.assertEqual({k:v for k,v in metrics.items() if k!='rotation_evidence'},old_metrics)
        for key in maps:np.testing.assert_array_equal(maps[key],old_maps[key])

    def test_D_requires_whole_image_even_with_positive_rotation_hint(self):
        request={'annotation_contract':self.cfg['annotation_contract'],'samples':[],
                 'visual_harness':{'d_rotation_evidence':True,'d_rotation_positive_only':True,'rotation_threshold_degrees':15}}
        prompt=build_prompt(request,'reviews.json')
        self.assertIn('全图作为一个整体',prompt)
        self.assertIn('局部区域共同偏移',prompt)
        self.assertNotIn('D=多个物体',prompt)
        self.assertIn('数值支持弱也不跳过D',prompt)

    def test_positive_and_negative_CV_hints_keep_whole_image_D_check(self):
        manifest={'records':[{'sample_key':key,'cv_flags':{'a_candidate':False,'d_candidate':candidate},
                   'metrics':{'chroma_ratio':1.0}} for key,candidate in [('S001',True),('S002',False)]]}
        hints=cv_hint_text(manifest)
        self.assertIn('几个物体换色不够',hints)
        self.assertIn('仍检查全图是否整体偏色',hints)
        self.assertNotIn('优先检查具体物体C/E',hints)


if __name__=='__main__':unittest.main(verbosity=2)
