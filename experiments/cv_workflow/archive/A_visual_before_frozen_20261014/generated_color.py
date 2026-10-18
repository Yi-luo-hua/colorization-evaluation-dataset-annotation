"""Generated-image colour presence; no GT correspondence or semantic labels."""
import numpy as np


def measure(rgb_image, settings, *, include_histogram=False):
    # Work on decoded RGB before resizing: tiny colour islands must not disappear.
    values=rgb_image.astype(np.int16)
    spread=values.max(axis=-1)-values.min(axis=-1)
    coloured=spread>settings['maximum_gray_channel_spread']
    gray_fraction=float(1-coloured.mean())
    minimum=settings.get('minimum_gray_pixel_fraction',1.0)
    result={'maximum_rgb_channel_spread':int(spread.max()),
            'colored_pixel_count':int(coloured.sum()),
            'colored_pixel_fraction':float(coloured.mean()),
            'pixels':int(spread.size),
            'measurement_size':[int(rgb_image.shape[1]),int(rgb_image.shape[0])],
            'gray_channel_tolerance':settings['maximum_gray_channel_spread'],
            'gray_pixel_fraction':gray_fraction,
            'minimum_gray_pixel_fraction':minimum,
            'strict_grayscale':bool(spread.max()==0),
            'grayscale_candidate':bool(gray_fraction>=minimum)}
    if include_histogram:
        result['rgb_channel_spread_histogram']=np.bincount(spread.ravel(),minlength=256).tolist()
    return result
