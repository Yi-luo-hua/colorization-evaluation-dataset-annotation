"""Codec calibration and known interventions for generated-only grayscale A."""
import argparse
import importlib.util
from pathlib import Path

import cv2
import numpy as np

import engine
import generated_color
from workflow import OUTPUT, read_json, write_json, utc, verify_sources


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-id',required=True)
    parser.add_argument('--sources',type=Path,nargs='+',required=True)
    parser.add_argument('--legacy-snapshot',type=Path,required=True)
    args=parser.parse_args()
    out=OUTPUT/args.run_id
    out.mkdir();(out/'images').mkdir()
    cfg=read_json(Path(__file__).with_name('config.json'))
    old_cfg=read_json(args.legacy_snapshot/'config.json')
    spec=importlib.util.spec_from_file_location('legacy_A_diagnostic',args.legacy_snapshot/'global_models.py')
    legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
    gray=np.broadcast_to(np.arange(256,dtype=np.uint8)[None,:,None],(96,256,3)).copy()
    codec=[]
    for extension,qualities in [('.png',[None]),('.jpg',[50,75,90,95,100])]:
        for quality in qualities:
            params=[] if quality is None else [cv2.IMWRITE_JPEG_QUALITY,quality]
            ok,encoded=cv2.imencode(extension,cv2.cvtColor(gray,cv2.COLOR_RGB2BGR),params)
            assert ok
            decoded=cv2.cvtColor(cv2.imdecode(encoded,cv2.IMREAD_COLOR),cv2.COLOR_BGR2RGB)
            evidence=generated_color.measure(decoded,cfg['a'])
            codec.append({'format':extension,'quality':quality,**evidence})
    observed_gray_spread=max(r['maximum_rgb_channel_spread'] for r in codec)
    assert observed_gray_spread==cfg['a']['maximum_gray_channel_spread']
    write_json(out/'codec_calibration.json',{'gray_RGB_levels':256,'controls':codec,
        'maximum_observed_gray_channel_spread':observed_gray_spread,
        'note':'Exact grayscale codec baseline, not a human visibility threshold or a noise allowance.'})
    sources={}
    for batch in args.sources:
        for r in verify_sources(batch)['records']:
            sources.setdefault(r['gt_path'],r)
    results=[]
    for number,(path,record) in enumerate(sources.items(),1):
        source=engine.read_rgb(engine.ROOT/path)
        gray=cv2.cvtColor(source,cv2.COLOR_RGB2GRAY)
        neutral=np.repeat(gray[...,None],3,axis=-1)
        h,w=gray.shape
        local=neutral.copy();local[:max(2,h//12),:max(2,w//12)]=[160,60,130]
        tiny=neutral.copy();tiny[0,0]=[129,128,128]
        variants={'grayscale':neutral,
                  'uniform_warm':np.broadcast_to(np.array([145,130,110],np.uint8),source.shape).copy(),
                  'brightness_tint':np.clip(neutral.astype(np.int16)+[12,0,-8],0,255).astype(np.uint8),
                  'fading_08':np.rint(neutral*0.92+source*0.08).astype(np.uint8),
                  'wrong_local_color':local,'one_pixel_one_level':tiny,'identity':source}
        reference=engine.lab(engine.resize_rgb(source,cfg['analysis_max_side']))
        for kind,image in variants.items():
            target=out/'images'/f'G{number:03d}_{kind}.png'
            ok,encoded=cv2.imencode('.png',cv2.cvtColor(image,cv2.COLOR_RGB2BGR));assert ok
            encoded.tofile(target)
            decoded=engine.read_rgb(target)
            analysed=engine.lab(engine.resize_rgb(decoded,cfg['analysis_max_side']))
            metrics,flags,_=engine.measure(reference,analysed,cfg,generated_rgb=decoded)
            a=old_cfg['a']
            baseline=((metrics['mean_c_model']<=a['maximum_mean_chroma'] and metrics['chroma_ratio']<=a['maximum_chroma_ratio']) or
                      (metrics['centered_spread_model']<=a['maximum_centered_spread'] and metrics['spread_ratio']<=a['maximum_spread_ratio']))
            old=legacy.predict_a({'baseline_a':baseline,'models':legacy.measure(reference,analysed,old_cfg['global_models']['features']),
                                 'metrics':metrics},old_cfg['global_models']['a'])
            expected=kind=='grayscale'
            results.append({'GT_path':path,'GT_sha256':record['gt_sha256'],'intervention':kind,
                'image':str(target.relative_to(engine.ROOT)),'image_sha256':engine.sha256(target),
                'expected_A':expected,'candidate_A':flags['a_candidate'],'legacy_A_candidate':old,
                'generated_color':metrics['generated_color'],
                'tolerance_sensitivity':{str(t):generated_color.measure(decoded,{**cfg['a'],'maximum_gray_channel_spread':t})['grayscale_candidate'] for t in [0,1,2]}})
    write_json(out/'records.json',results)
    summary={'created_at':utc(),'configuration':cfg,'GT_count':len(sources),'controls':len(results),
        'A_controls':sum(r['expected_A'] for r in results),'non_A_controls':sum(not r['expected_A'] for r in results),
        'candidate_A_misses':sum(r['expected_A'] and not r['candidate_A'] for r in results),
        'candidate_A_false_positives':sum(not r['expected_A'] and r['candidate_A'] for r in results),
        'legacy_A_false_positives_under_new_definition':sum(not r['expected_A'] and r['legacy_A_candidate'] for r in results),
        'all_source_hashes_unchanged':all(engine.sha256(engine.ROOT/p)==r['gt_sha256'] for p,r in sources.items()),
        'limits':'Known pixel interventions only. One-pixel controls test resolution loss, not human-visible defect labels. No real-sample accuracy or Gemini label claim.'}
    write_json(out/'summary.json',summary)
    assert summary['candidate_A_misses']==summary['candidate_A_false_positives']==0
    print(summary)


if __name__=='__main__':main()
