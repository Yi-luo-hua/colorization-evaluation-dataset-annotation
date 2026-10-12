"""Quantile seeds grown into lower-signal support; purely numerical candidates."""
import cv2
import numpy as np


def regions(maps,settings):
    out=[];h,w=maps['signed_dc'].shape
    signals={'chroma_gain':np.maximum(maps['signed_dc'],0),'chroma_loss':np.maximum(-maps['signed_dc'],0),'hue_change':maps['hue_component']}
    for kind,signal in signals.items():
        high=max(settings['quantile_signal_floor'],float(np.percentile(signal,settings['quantile'])))
        # Inclusive threshold preserves flat plateaus exactly at the percentile.
        seeds=signal>=high
        low=max(settings['quantile_signal_floor'],high*settings['grow_fraction'])
        count,labels,stats,_=cv2.connectedComponentsWithStats((signal>=low).astype(np.uint8),connectivity=8)
        seed_labels=set(np.unique(labels[seeds]))-{0};candidates=[]
        for i in seed_labels:
            x,y,bw,bh,area=map(int,stats[i])
            if area<settings['minimum_area_pixels']:continue
            if bw*bh/(w*h)>settings['maximum_growth_bbox_fraction']:
                # A near-full-frame crop adds little information; recover its compact seeds.
                isolated=(seeds & (labels==i)).astype(np.uint8)
                n,separate,separate_stats,_=cv2.connectedComponentsWithStats(isolated,connectivity=8)
                for j in range(1,n):
                    sx,sy,sw,sh,sa=map(int,separate_stats[j])
                    if sa<settings['minimum_area_pixels']:continue
                    strength=float(signal[separate==j].mean())
                    candidates.append({'kind':kind,'bbox_normalized':[sx/w,sy/h,(sx+sw)/w,(sy+sh)/h],
                                       'pixel_fraction':sa/(h*w),'mean_signal':strength,
                                       'selection_cutoff':high,'growth_cutoff':high,'growth_rejected_as_diffuse':True})
                continue
            values=signal[labels==i];strength=float(values.mean())
            candidates.append({'kind':kind,'bbox_normalized':[x/w,y/h,(x+bw)/w,(y+bh)/h],
                               'pixel_fraction':area/(h*w),'mean_signal':strength,
                               'selection_cutoff':high,'growth_cutoff':low})
        candidates.sort(key=lambda r:r['pixel_fraction']*r['mean_signal'],reverse=True)
        out.extend(candidates[:settings['maximum_per_kind']])
    for i,r in enumerate(out,1):r['region_id']=f'R{i}'
    return out
