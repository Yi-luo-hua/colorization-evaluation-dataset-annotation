"""Actual CLI failure modes must never become empty or fabricated labels."""
import unittest
from unittest.mock import patch

from agy_runner import normalize_review,build_prompt,load_completed_file
from workflow import TAXONOMY


class RunnerChecks(unittest.TestCase):
    def file_fixture(self):
        reviewer={'environment':'fixture','model':'fixture'}
        manifest={'configuration':{'external_reviewer':reviewer},'records':[{'sample_key':'S001'}]}
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

    def test_observed_field_aliases_preserve_semantic_annotations(self):
        payload={'reviews':[{'decision':'defect','defects':[{'category':'E2','severity':'L2','object':'外套','evidence':'发灰'}]},
                            {'decision':'pass','defects':[]}]}
        result=normalize_review(payload)
        self.assertEqual(result['reviews'][0]['decision'],'defects');self.assertEqual(result['reviews'][1]['decision'],'no_defects')
        self.assertEqual(result['reviews'][0]['defects'],[{'id':'E2','severity':'L2','object':'外套','evidence':'发灰'}])
        self.assertEqual(payload['reviews'][0]['decision'],'defect');self.assertIn('category',payload['reviews'][0]['defects'][0])

    def test_file_output_prompt_allows_only_local_sheets_and_result_file(self):
        prompt=build_prompt('协议',{'samples':[{'sheet':'sheets/sheet_001.png'}]},'/batch/reviews_gemini.json')
        self.assertIn('直接修改这个本地文件：/batch/reviews_gemini.json',prompt)
        self.assertIn('不要在回复中返回JSON',prompt);self.assertIn('自行读取本地看板',prompt)
        self.assertNotIn('OUTPUT TEMPLATE',prompt);self.assertNotIn('data:image',prompt)


if __name__=='__main__':unittest.main(verbosity=2)
