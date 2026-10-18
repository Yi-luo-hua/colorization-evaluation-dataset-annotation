"""Count GT chroma strata; these are diagnostic candidates, never rejection labels."""
import argparse
import csv
import hashlib
from pathlib import Path

from workflow import read_json, write_json


def summarize(profiles,config,probes):
    with profiles.open(encoding='utf-8-sig',newline='') as source:
        rows=list(csv.DictReader(source))
    threshold=config['gt_reference']['low_chroma_mean_candidate']
    splits={}
    for split in sorted({r['split'] for r in rows}):
        subset=[r for r in rows if r['split']==split]
        strata=[]
        for probe in probes:
            selected=[r for r in subset if float(r['p95_c'])<probe]
            strata.append({'p95_chroma_below':probe,'count':len(selected),
                           'fraction':len(selected)/len(subset),'image_ids':[r['image_id'] for r in selected]})
        splits[split]={'GT_count':len(subset),
                       'low_mean_candidates':sum(float(r['mean_c'])<threshold for r in subset),
                       'near_gray_diagnostic_strata':strata}
    return {'profiles':str(profiles.resolve()),'profiles_sha256':hashlib.sha256(profiles.read_bytes()).hexdigest(),
            'low_mean_candidate_threshold':threshold,'splits':splits,
            'interpretation':'Counts describe chroma strata, not confirmed unreliable GT. No cast decision from mean a/b; no automatic skip or fixed rejection quota.',
            'reliability':config['gt_reference']['reliability']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profiles',type=Path,required=True)
    parser.add_argument('--config',type=Path,default=Path(__file__).with_name('config.json'))
    parser.add_argument('--chroma-probes',type=float,nargs='+',required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    result=summarize(args.profiles,read_json(args.config),args.chroma_probes)
    args.out.parent.mkdir(parents=True,exist_ok=True);write_json(args.out,result)
    for split,item in result['splits'].items():
        print(split,item['GT_count'],'GT;',item['low_mean_candidates'],'low-mean candidates;',
              [(r['p95_chroma_below'],r['count']) for r in item['near_gray_diagnostic_strata']])


if __name__=='__main__':main()
