"""Unknown judgments must not inflate negative counts or agreement scores."""
import unittest

from review_boundaries import compare,tally
from workflow import TAXONOMY


class BoundaryChecks(unittest.TestCase):
    def test_unknowns_are_not_negative_truth(self):
        m=tally([(True,True),(False,True),(None,False),(False,None)])
        self.assertEqual((m['evaluated'],m['unresolved'],m['tp'],m['fp'],m['tn']),(2,2,1,1,0))

    def test_uncertain_ai_does_not_become_no_defect(self):
        reviewer={'environment':'fixture','model':'fixture'};key='val/lcad/000000000001'
        manifest={'configuration':{'external_reviewer':reviewer},'records':[{'sample_key':key,'cv_flags':{'a_candidate':True,'d_candidate':True}}]}
        visual={'schema_version':'visual_review_v1','reviewer':reviewer,'reviews':[{'sample_key':key,'inspection_complete':True,
                  'checked_categories':list(TAXONOMY),'decision':'uncertain','defects':[],'uncertainties':['需要原图确认'],'needs_crops':[]}]}
        result=compare(manifest,visual)
        self.assertEqual(result['visual_unresolved'],1);self.assertEqual(result['A_disagreements'],0)
        self.assertIsNone(result['records'][0]['visual_A']);self.assertFalse(result['records'][0]['cv_D_after_A'])
        self.assertNotIn('human_reference_metrics',result)


if __name__=='__main__':unittest.main(verbosity=2)
