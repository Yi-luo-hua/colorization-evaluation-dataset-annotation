"""Actual CLI failure modes must never become empty or fabricated labels."""
import unittest
from unittest.mock import patch

from agy_runner import normalize_review,load_completed_file
from workflow import TAXONOMY,ANNOTATION_CONTRACT
from compact_harness import expand,build_prompt
from pathlib import Path
from workflow import read_json
import numpy as np
import engine


class RunnerChecks(unittest.TestCase):
    def test_compact_file_preserves_labels_and_explicit_completion(self):
        manifest,_=self.file_fixture()
        defect={'id':'C','severity':'L2','object':'外套','description':'GT红色，生成紫色。'}
        raw={'schema_version':'visual_review_compact_v1','reviews':{'S001':[defect]}}
        with patch('agy_runner.read_json',return_value=raw):
            _,payload=load_completed_file(manifest,'file.json',{'status':'SUCCESS'})
        self.assertEqual(payload['reviews'][0]['defects'],[defect])
        self.assertNotIn('gt_color',payload['reviews'][0]['defects'][0])
        for entries in [{'S001':None},{}, {'S001':[], 'S002':[]}]:
            with self.assertRaises(ValueError):expand(manifest,{'reviews':entries})

    def test_compact_does_not_bypass_A_terminal_or_evidence_rules(self):
        manifest,_=self.file_fixture()
        for defects in [[{'id':'A','severity':'L3','object':'全图','description':'灰阶'}],
                        [{'id':'C','severity':'L2','object':'','description':'变紫色'}]]:
            raw={'schema_version':'visual_review_compact_v1','reviews':{'S001':defects}}
            with patch('agy_runner.read_json',return_value=raw):
                with self.assertRaises(ValueError):load_completed_file(manifest,'file.json',{'status':'SUCCESS'})

    def file_fixture(self):
        reviewer={'environment':'fixture','model':'fixture'}
        manifest={'configuration':{'external_reviewer':reviewer,'annotation_contract':ANNOTATION_CONTRACT},'records':[{'sample_key':'S001'}]}
        payload={'schema_version':'visual_review_v1','reviewer':reviewer,'reviews':[{'sample_key':'S001','inspection_complete':True,
                 'checked_categories':list(TAXONOMY),'decision':'no_defects','defects':[],'uncertainties':[],'needs_crops':[]}]}
        return manifest,payload

    def test_plain_acknowledgement_uses_written_file_not_reply(self):
        manifest,payload=self.file_fixture()
        with patch('agy_runner.read_json',return_value=payload) as reader:
            raw,result=load_completed_file(manifest,'reviews_gemini.json',{'status':'SUCCESS','response':'文件已保存'})
            reader.assert_called_once_with('reviews_gemini.json');self.assertEqual(raw,payload);self.assertEqual(result,payload)

    def test_ack_without_completed_file_is_not_finished_annotation(self):
        manifest,payload=self.file_fixture();payload['reviews'][0]['inspection_complete']=False
        with patch('agy_runner.read_json',return_value=payload):
            with self.assertRaises(ValueError):load_completed_file(manifest,'reviews_gemini.json',{'status':'SUCCESS','response':'文件已保存'})
        with self.assertRaisesRegex(ValueError,'location'):load_completed_file(manifest,'unused.json',{'status':'ERROR','error':'User location is not supported'})

    def test_complete_file_survives_interrupted_stream_without_new_model_call(self):
        manifest,_=self.file_fixture()
        defect={'id':'C','severity':'L2','object':'外套','description':'GT红色，生成蓝色。'}
        raw={'schema_version':'visual_review_compact_v1','reviews':{'S001':[defect]}}
        with patch('agy_runner.Path.exists',return_value=True),patch('agy_runner.read_json',return_value=raw):
            _,payload=load_completed_file(manifest,'written.json',{'status':'ERROR','error':'The stream was interrupted.'})
        self.assertEqual(payload['reviews'][0]['defects'],[defect])

    def test_interrupted_stream_with_null_file_still_needs_recovery(self):
        manifest,_=self.file_fixture()
        raw={'schema_version':'visual_review_compact_v1','reviews':{'S001':None}}
        with patch('agy_runner.Path.exists',return_value=True),patch('agy_runner.read_json',return_value=raw):
            with self.assertRaisesRegex(ValueError,'Uninspected'):
                load_completed_file(manifest,'written.json',{'status':'ERROR','error':'The stream was interrupted.'})

    def test_observed_field_aliases_preserve_semantic_annotations(self):
        payload={'reviews':[{'decision':'defect','defects':[{'category':'E2','severity':'L2','object':'外套','evidence':'发灰'}]},
                            {'decision':'pass','defects':[]}]}
        result=normalize_review(payload)
        self.assertEqual(result['reviews'][0]['decision'],'defects');self.assertEqual(result['reviews'][1]['decision'],'no_defects')
        self.assertEqual(result['reviews'][0]['defects'],[{'id':'E2','severity':'L2','object':'外套','evidence':'发灰'}])
        self.assertEqual(payload['reviews'][0]['decision'],'defect');self.assertIn('category',payload['reviews'][0]['defects'][0])

    def test_file_output_prompt_allows_only_local_sheets_and_result_file(self):
        prompt=build_prompt({'annotation_contract':ANNOTATION_CONTRACT,'samples':[{'sample_key':'S001','sheet':'sheets/sheet_001.png'}]},'/batch/reviews_gemini.json')
        self.assertIn('直接填写本地文件 /batch/reviews_gemini.json',prompt)
        self.assertIn('不在回复中返回JSON',prompt);self.assertIn('自行用图片工具读取',prompt)
        self.assertNotIn('OUTPUT TEMPLATE',prompt);self.assertNotIn('data:image',prompt)

    def test_original_RGB_evidence_does_not_imply_E2_or_GT_qualification(self):
        cfg=read_json(Path(__file__).with_name('config.json'))
        image=np.full((80,80,3),[130,125,120],np.uint8)
        metrics,flags,_=engine.measure(engine.lab(image),engine.lab(image),cfg,generated_rgb=image)
        self.assertFalse(flags['a_candidate'])
        request={'annotation_contract':ANNOTATION_CONTRACT,'samples':[{'sample_key':'S001','sheet':'sheets/sheet_001.png','generated_color':metrics['generated_color']}],
                 'visual_harness':{'a_rgb_evidence':True}}
        prompt=build_prompt(request,'reviews.json')
        self.assertIn('S001：RGB最大通道差10',prompt)
        self.assertNotIn('对应颜色结构',prompt)
        self.assertIn('不标A不等于自动标E2',prompt)



if __name__=='__main__':unittest.main(verbosity=2)
