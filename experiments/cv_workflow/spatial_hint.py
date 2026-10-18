"""One image-relative location from existing hue candidates; no semantic labels."""


def select(record):
    candidates=[r for r in record['region_candidates'] if r['kind']=='hue_change']
    if not candidates:return None
    region=max(candidates,key=lambda r:r['pixel_fraction']*r['mean_signal'])
    box=region.get('compact_bbox_normalized',region['bbox_normalized'])
    x1,y1,x2,y2=box
    return {'center_percent':[round((x1+x2)*50),round((y1+y2)*50)],
            'candidate_kind':'hue_change','region_id':region['region_id'],
            'ranking':'seed pixel_fraction * mean_signal','box_normalized':box}
