"""D experiment: equal votes across GT color groups, rather than pixel area.

Color groups are numerical evidence, not objects. No semantic final decisions.
"""
import numpy as np


def prepare_groups(gt, settings):
    x = gt.reshape(-1, 3)[::settings['stride']]
    bins = np.floor(x / np.array([settings['l_bin_width'], settings['ab_bin_width'], settings['ab_bin_width']])).astype(int)
    _, membership, counts = np.unique(bins, axis=0, return_inverse=True, return_counts=True)
    return [np.flatnonzero(membership == i) for i, n in enumerate(counts)
            if n / len(x) >= settings['minimum_group_fraction']]


def measure(gt, gen, groups, settings):
    if not groups:
        return {'group_count': 0, 'common_da': 0.0, 'common_db': 0.0, 'shift_norm': 0.0,
                'direction_coverage': 0.0, 'projection_q': 0.0, 'group_vectors': []}
    delta = (gen[..., 1:] - gt[..., 1:]).reshape(-1, 2)[::settings['features']['stride']]
    vectors = np.array([np.median(delta[ix], axis=0) for ix in groups])
    common = np.median(vectors, axis=0)
    norm = float(np.linalg.norm(common))
    projection = vectors @ (common / (norm + 1e-8))
    cosine = projection / (np.linalg.norm(vectors, axis=1) + 1e-8)
    return {'group_count': len(groups), 'common_da': float(common[0]), 'common_db': float(common[1]),
            'shift_norm': norm, 'direction_coverage': float(np.mean(cosine >= settings['direction_cosine'])),
            'projection_q': float(np.percentile(projection, settings['projection_quantile'])),
            'group_vectors': vectors.tolist()}


def predict(row, parameters, cv_config):
    f = row['group_features']; m = row['metrics']
    # Keep v4's exposure veto and exact white-balance branch.
    gain_settings = cv_config['global_models']['d']; encoded = m['global_models']['gain_models']['encoded']
    if (encoded['fit_valid_fraction'] >= gain_settings['minimum_fit_fraction'] and
        encoded['relative_gain_spread'] < gain_settings['minimum_gain_spread'] and
        encoded['residual_p98'] <= gain_settings['maximum_gain_residual_p98']):
        return False
    exact_gain = any(g['fit_valid_fraction'] >= gain_settings['minimum_fit_fraction'] and
                     g['relative_gain_spread'] >= gain_settings['minimum_gain_spread'] and
                     g['residual_p98'] <= gain_settings['maximum_gain_residual_p98'] and
                     g['effect_p50'] >= gain_settings['minimum_gain_effect']
                     for g in m['global_models']['gain_models'].values())
    translation = ((row['baseline_d'] or not parameters['require_baseline']) and
                   m['active_pixel_coverage'] >= gain_settings['minimum_pixel_coverage'] and
                   f['shift_norm'] >= parameters['minimum_shift'] and
                   f['direction_coverage'] >= parameters['minimum_direction_coverage'] and
                   f['projection_q'] >= parameters['minimum_group_projection'] and
                   m['scalar_gain'] >= parameters['minimum_scalar_gain'] and
                   not row.get('scale_explains_shift', False))
    return bool(exact_gain or translation)
