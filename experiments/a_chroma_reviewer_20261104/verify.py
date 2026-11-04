"""Focused persistence/API/fitting checks in an isolated temporary review store."""
import json
from pathlib import Path
import tempfile
from threading import Thread
from http.server import ThreadingHTTPServer
from urllib.request import Request,urlopen
from urllib.error import HTTPError

import numpy as np

from server import ReviewStore,handler_for
from fit import optimize,fit_model
from prepare_candidates import LOCAL,ROOT,sha,measure


def main():
    # Independent exhaustive check of the 2D prefix-sum optimizer on a tiny case.
    tiny = [{'mean_C':m,'var_ab':v,'label':l} for m,v,l in [(1,1,'A'),(3,2,'A'),(2,5,'not_A'),(6,1,'not_A'),(8,8,'not_A')]]
    result = optimize(tiny)
    assert result=={'mean_C_max':3.,'var_ab_max':2.}
    manifest = json.loads((LOCAL/'manifest.json').read_text(encoding='utf-8'))
    records = manifest['records']
    assert len(records)==600 and not manifest['errors']
    assert not ({r['gt_sha256'] for r in records if r['partition']=='training'} & {r['gt_sha256'] for r in records if r['partition']=='validation'})
    # Feature extraction matches the original human-anchor computation.
    source = json.loads((ROOT/'experiments/human_standard_600_20261102/local/A_calibration_20261104/chroma_features.json').read_text(encoding='utf-8'))
    gold = json.loads((ROOT/'experiments/human_standard_600_20261102/local/batch_02/human_archive_20261104T011149Z/human_gold.json').read_text(encoding='utf-8'))
    anchor = next(r for r in gold['reviews'] if r['review_index']==194)
    computed = measure(ROOT/anchor['record']['model_path'])
    expected = next(r['features'] for r in source['records'] if r['review_index']==194)
    assert np.isclose(computed['mean_C'],expected['mean_C'])
    assert np.isclose(computed['var_ab'],expected['var_a_plus_var_b'])
    with tempfile.TemporaryDirectory(prefix='a-review-verification-') as temp:
        store = ReviewStore(Path(temp))
        http = ThreadingHTTPServer(('127.0.0.1',0),handler_for(store))
        Thread(target=http.serve_forever,daemon=True).start()
        base = f'http://127.0.0.1:{http.server_port}'
        def request(route,body=None,origin=None):
            headers = {'Content-Type':'application/json'}
            if origin: headers['Origin']=origin
            data = json.dumps(body).encode() if body is not None else None
            with urlopen(Request(base+route,data=data,headers=headers),timeout=10) as r: return json.load(r)
        try:
            assert request('/api/state')['counts']['reviewed']==0
            assert request('/api/fit',{})['status']=='awaiting_human_labels'
            ids = [r['id'] for r in records[:2]]
            saved = request('/api/decide',{'ids':ids,'label':'A'})
            assert saved['counts']['A']==2
            assert ReviewStore(Path(temp)).state()['counts']['A']==2
            corrected = request('/api/decide',{'ids':[ids[0]],'label':'not_A'})
            undone = request('/api/undo',{'revision':corrected['undo_revision']})
            assert undone['counts']['A']==2 and undone['counts']['not_A']==0
            for origin,ids_bad,expected_status in [('https://example.org',ids,403),(None,['BAD-ID'],400)]:
                try: request('/api/decide',{'ids':ids_bad,'label':'A'},origin)
                except HTTPError as e: assert e.code==expected_status
                else: raise AssertionError('Invalid mutation was accepted')
            v = next(r for r in records if r['partition']=='validation')
            request('/api/decide',{'ids':[v['id']],'label':'A'})
            fit_one = request('/api/fit',{})
            request('/api/decide',{'ids':[v['id']],'label':'not_A'})
            fit_two = request('/api/fit',{})
            assert fit_one['thresholds']==fit_two['thresholds']
            assert v['id'] not in fit_two['training_ids'] and v['id'] in fit_two['validation_ids']
            request('/api/decide',{'ids':[v['id']],'label':'unsure'})
            fit_three = request('/api/fit',{})
            assert v['id'] not in fit_three['validation_ids']
            with urlopen(base+'/image?id='+records[0]['id']) as r: assert r.headers['Content-Type'].startswith('image/')
            exported = request('/api/export')
            assert exported['labels']==store.state()['labels']
            assert (Path(temp)/'judgments_backup.json').exists()
            # Exercise completion using synthetic decisions only in this temporary store.
            for label in ['A','not_A']:
                ids = [r['id'] for r in records if ('A' if r['mean_C']<=6 and r['var_ab']<=6 else 'not_A')==label]
                for offset in range(0,len(ids),100):
                    request('/api/decide',{'ids':ids[offset:offset+100],'label':label})
            completed = request('/api/fit',{})
            assert completed['status']=='review_round_complete' and completed['pending']==0
            assert completed['new_definite_labels']==600
            assert completed['training']['n']+completed['validation']['n']==787
        finally:
            http.shutdown(); http.server_close()
    print('PASS: queue isolation, feature parity, save/reload, correction/undo, invalid writes, image serving, export and validation-independent fitting. Real human review DB untouched.')


if __name__=='__main__': main()
