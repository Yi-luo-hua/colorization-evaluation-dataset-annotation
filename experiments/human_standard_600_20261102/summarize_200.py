"""Reproducible descriptive summary of the first 200 human-finalized samples."""
from collections import Counter
import json

from prepare import HERE, sha, write
from descriptions import description_only

SOURCES = [HERE/'local/batch_01/human_archive_20261104T005549Z/human_gold.json',
    HERE/'local/batch_02/human_archive_20261104T011149Z/human_gold.json']
CATEGORIES = ['A','B','C','D','E1','E2','F']


def levels(defects):
    if any(d['id']=='A' for d in defects):
        return {'A':''}
    return {c:max(d['severity'] for d in defects if d['id']==c)
        for c in CATEGORIES if any(d['id']==c for d in defects)}


def descriptions(defects):
    active = levels(defects)
    return {c:'\n'.join(description_only(d['description']).strip() for d in defects if d['id']==c).strip()
        for c in active}


def summarize():
    docs = [json.loads(p.read_text(encoding='utf-8')) for p in SOURCES]
    rows = sorted([r for d in docs for r in d['reviews']],key=lambda r:r['review_index'])
    preserved = [r for d in docs for r in d['human_finalized_preserved']]
    assert len(preserved)==len({r['source_sample_key'] for r in preserved})==200
    assert len(rows)==len({r['source_sample_key'] for r in rows})==187
    table = {c:{'old':0,'human':0,'added':0,'removed_or_A_overridden':0,'grade_up':0,'grade_down':0,
        'same_grade':0,'human_levels':Counter()} for c in CATEGORIES}
    overview,changes,maxima,combinations = Counter(),Counter(),Counter(),Counter()
    segments = {}
    changed_examples = []
    for r in rows:
        old,new = levels(r['original_defects']),levels(r['defects'])
        overview['no_defect' if not new else 'A_only' if 'A' in new else 'non_A_defect'] += 1
        overview['old_no_defect'] += not old
        overview['old_A_only'] += 'A' in old
        overview['human_category_records'] += len(new)
        overview['old_category_records'] += len(old)
        overview['multiple_categories'] += len(new)>1
        combinations['+'.join(sorted(new)) or 'none'] += 1
        maxima['A' if 'A' in new else max(new.values(),default='none')] += 1
        label_change = old!=new
        changes['category_or_grade_changed'] += label_change
        changes['category_set_changed'] += old.keys()!=new.keys()
        changes['grade_only_changed'] += old.keys()==new.keys() and label_change
        changes['description_only_changed'] += not label_change and descriptions(r['original_defects'])!=descriptions(r['defects'])
        changes['unchanged_active_labels_and_text'] += not label_change and descriptions(r['original_defects'])==descriptions(r['defects'])
        changes['old_empty_new_nonempty'] += not old and bool(new)
        changes['old_nonempty_new_empty'] += bool(old) and not new
        for c in CATEGORIES:
            cell = table[c]
            cell['old'] += c in old; cell['human'] += c in new
            cell['added'] += c not in old and c in new
            cell['removed_or_A_overridden'] += c in old and c not in new
            if c in new:
                cell['human_levels'][new[c] or 'not_graded'] += 1
            if c in old and c in new:
                cell['grade_up'] += new[c]>old[c]
                cell['grade_down'] += new[c]<old[c]
                cell['same_grade'] += new[c]==old[c]
        for key in ['model','split']:
            value = key+':'+r['record'][key]
            segment = segments.setdefault(value,Counter())
            segment['samples'] += 1; segment['no_defect'] += not new
            segment['category_or_grade_changed'] += label_change
            for c in new: segment[c] += 1
        if label_change:
            changed_examples.append({'review_index':r['review_index'],'old_levels':old,'human_levels':new,
                'old_descriptions':descriptions(r['original_defects']),'human_descriptions':descriptions(r['defects'])})
    assert sum(overview[k] for k in ['no_defect','A_only','non_A_defect'])==187
    assert changes['category_or_grade_changed']+changes['description_only_changed']+changes['unchanged_active_labels_and_text']==187
    for cell in table.values():
        assert cell['old']+cell['added']-cell['removed_or_A_overridden']==cell['human']
        assert sum(cell['human_levels'].values())==cell['human']
    output = {'scope':'first 200 development samples only; 187 GT-usable rows for defect statistics',
        'sources':[{'path':str(p),'sha256':sha(p)} for p in SOURCES],
        'batches':[{'batch':d['batch'],'finalized':d['counts']['finalized'],'gold':len(d['reviews']),
            'excluded':[r['review_index'] for r in d['gt_excluded']],
            'pending':[r['review_index'] for r in d['issues']]} for d in docs],
        'unique_GT_187':len({r['record']['gt_sha256'] for r in rows}),
        'unique_GT_200':len({r['gt_quality']['screening']['gt_sha256'] for r in preserved}),
        'overview':overview,'changes':changes,'categories':table,'max_severity_per_image':maxima,
        'common_combinations':combinations.most_common(),'segments':segments,
        'changed_examples':changed_examples,
        'inherited_A_template_indices':[r['review_index'] for r in rows if 'A' in levels(r['defects'])
            and any('允许少量局部留色' in d['description'] for d in r['defects'])],
        'A_interpretation':'Human A decisions are authoritative; faint whole-image tint and small residual color are compatible with A. Inherited wording is not a pending label error. See A_CALIBRATION_20261104.md.',
        'qualifications':['Counts are per image/category, with original multiple instances collapsed to maximum severity.',
            'A overrides other categories; absence under A is not a negative category judgment.',
            'Stratified, unweighted calibration subset; rates are not population rates or independent workflow evaluation.',
            'Category/grade disagreements do not measure description accuracy; no new visual adjudication performed.']}
    write(HERE/'local/summary_200_20261104.json',output)
    print(json.dumps({k:v for k,v in output.items() if k not in ['changed_examples','qualifications','sources']},ensure_ascii=True))


if __name__=='__main__': summarize()
