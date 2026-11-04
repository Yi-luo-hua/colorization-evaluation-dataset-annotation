"""Read-only chroma scan of the development partition; freeze a review queue."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import time

import cv2
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOCAL = HERE/'local'
sys.path.insert(0,str(ROOT/'experiments/human_standard_600_20261102'))
from prepare import DB, sha

cv2.setNumThreads(1)


def write(path,data):
    tmp = path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    tmp.replace(path)


def measure(path):
    with Image.open(path) as im:
        rgb = np.asarray(im.convert('RGB'),dtype=np.float32)/255
    ab = cv2.cvtColor(rgb,cv2.COLOR_RGB2LAB)[:,:,1:]
    return {'mean_C':float(np.linalg.norm(ab,axis=2).mean()),
        'var_ab':float(np.var(ab,axis=(0,1),dtype=np.float64).sum())}


def tier(f):
    m,v = f['mean_C'],f['var_ab']
    if m<=6 and v<=6: return 'core'
    if m<=9 and v<=16: return 'near'
    if m<=15 and v<=60: return 'boundary'
    if m<=12 and v<=200: return 'contrast'
    return None


def main():
    LOCAL.mkdir(exist_ok=True)
    if (LOCAL/'manifest.json').exists():
        print('Frozen candidate manifest exists; retained unchanged.',flush=True)
        return
    original = ROOT/'experiments/human_standard_600_20261102/local/manifest.json'
    protected = json.loads(original.read_text(encoding='utf-8'))
    excluded_GT = {s['record']['gt_sha256'] for s in protected['samples']}
    source_sha = sha(DB)
    eligible = []
    population = partition_excluded = reserved_excluded = 0
    with sqlite3.connect(DB.as_uri()+'?mode=ro',uri=True) as con:
        for key,body in con.execute('select key,body from samples order by key'):
            r = json.loads(body); rec = r['record']; population += 1
            role = int(hashlib.sha256(('600-v1/'+rec['gt_path']).encode()).hexdigest(),16)%2
            if role:
                partition_excluded += 1; continue
            if rec['gt_sha256'] in excluded_GT:
                reserved_excluded += 1; continue
            eligible.append({k:rec[k] for k in ['source_sample_key','split','model','model_path','gt_path','model_sha256','gt_sha256']})
    eligible.sort(key=lambda r:r['source_sample_key'])
    # Separate derived cache; production SQLite and images are never written.
    cache = sqlite3.connect(LOCAL/'features.sqlite3')
    cache.execute('create table if not exists features (key text primary key, image_sha text, body text)')
    cached = {key:(digest,json.loads(body)) for key,digest,body in cache.execute('select key,image_sha,body from features')}
    done = []; errors = []; started = time.time()
    def inspect(rec):
        try:
            old = cached.get(rec['source_sample_key'])
            if old and old[0]==rec['model_sha256']:
                return rec,old[1],None
            path = ROOT/rec['model_path']
            if sha(path)!=rec['model_sha256']:
                raise ValueError('source image SHA-256 changed')
            return rec,measure(path),None
        except Exception as exc:
            return rec,None,str(exc)
    with ThreadPoolExecutor(max_workers=6) as pool:
        for i,(rec,f,error) in enumerate(pool.map(inspect,eligible),1):
            if error:
                errors.append({'key':rec['source_sample_key'],'error':error})
            else:
                done.append({**rec,**f,'tier':tier(f)})
                cache.execute('insert or replace into features values (?,?,?)',
                    (rec['source_sample_key'],rec['model_sha256'],json.dumps(f)))
            if i%100==0 or i==len(eligible):
                cache.commit()
                status = {'phase':'scanning','scanned':i,'total':len(eligible),
                    'potential_candidates':sum(bool(r['tier']) for r in done),'errors':len(errors),
                    'elapsed_seconds':round(time.time()-started,1)}
                write(LOCAL/'scan_status.json',status)
                print(json.dumps(status),flush=True)
    cache.close()
    buckets = {t:[r for r in done if r['tier']==t] for t in ['core','near','boundary','contrast']}
    chosen = []
    # Include positives and difficult negatives rather than only the darkest/grayest outputs.
    for t,quota in [('core',240),('near',160),('boundary',140),('contrast',60)]:
        group = sorted(buckets[t],key=lambda r:hashlib.sha256(('A-review-v1/'+r['source_sample_key']).encode()).hexdigest())
        chosen += group[:quota]
    selected = {r['source_sample_key'] for r in chosen}
    remainder = sorted([r for r in done if r['tier'] and r['source_sample_key'] not in selected],
        key=lambda r:(['core','near','boundary','contrast'].index(r['tier']),hashlib.sha256(r['source_sample_key'].encode()).hexdigest()))
    chosen += remainder[:max(0,600-len(chosen))]
    chosen.sort(key=lambda r:hashlib.sha256(('A-blind-order-v1/'+r['source_sample_key']).encode()).hexdigest())
    for i,r in enumerate(chosen,1):
        r['id'] = f'C{i:04d}'
        r['partition'] = 'validation' if int(hashlib.sha256(('A-fit-holdout-v1/'+r['gt_sha256']).encode()).hexdigest(),16)%5==0 else 'training'
    assert not ({r['gt_sha256'] for r in chosen}&excluded_GT)
    assert len(chosen)==len({r['source_sample_key'] for r in chosen})
    assert not ({r['gt_sha256'] for r in chosen if r['partition']=='training'} & {r['gt_sha256'] for r in chosen if r['partition']=='validation'})
    manifest = {'version':'A_chroma_review_v1','created_at':datetime.now(timezone.utc).isoformat(),
        'source_db':str(DB),'source_db_sha256':source_sha,'source_rows':population,
        'evaluation_partition_excluded':partition_excluded,'reserved_GT_excluded_rows':reserved_excluded,
        'scanned':len(done),'errors':errors,'eligible_scan_total':len(eligible),
        'feature_definition':'OpenCV float32 RGB [0,1] to CIELAB; mean(C*) and Var(a*)+Var(b*), population variance.',
        'review_role':'development calibration only; not an independent evaluation dataset',
        'protected_manifest_sha256':sha(original),'candidate_bucket_counts':{k:len(v) for k,v in buckets.items()},
        'records':chosen}
    write(LOCAL/'manifest.json',manifest)
    write(LOCAL/'scan_status.json',{'phase':'ready','scanned':len(done),'total':len(eligible),
        'candidates':len(chosen),'bucket_counts':manifest['candidate_bucket_counts'],'errors':len(errors)})
    print(json.dumps({'candidates':len(chosen),'buckets':manifest['candidate_bucket_counts']}),flush=True)


if __name__=='__main__': main()
