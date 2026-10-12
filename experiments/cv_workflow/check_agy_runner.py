"""Actual CLI failure modes must never become empty or fabricated labels."""
import unittest

from agy_runner import decode_response


class RunnerChecks(unittest.TestCase):
    def test_empty_partial_success_is_not_a_completed_review(self):
        with self.assertRaises(ValueError):decode_response({'status':'SUCCESS','response':''})
        with self.assertRaisesRegex(ValueError,'location'):decode_response({'status':'ERROR','response':'','error':'User location is not supported'})

    def test_plain_or_fenced_json_decodes_without_executing_code(self):
        expected={'reviews':[]}
        for response in ['{"reviews":[]}','```json\n{"reviews":[]}\n```']:
            self.assertEqual(decode_response({'status':'SUCCESS','response':response}),expected)


if __name__=='__main__':unittest.main(verbosity=2)
