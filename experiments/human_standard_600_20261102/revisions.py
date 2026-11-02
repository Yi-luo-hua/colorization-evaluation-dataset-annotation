"""Record explicit visual judgements made in the Codex conversation."""
import json
from pathlib import Path
import sys

from prepare import HERE, ROOT, sha, write

CATEGORIES = ['A', 'B', 'C', 'D', 'E1', 'E2', 'F']


def save(path):
    manifest = json.loads((HERE/'local/manifest.json').read_text(encoding='utf-8'))
    samples = {s['review_index']: s for s in manifest['samples']}
    output = HERE/'local/revisions.json'
    reviews = json.loads(output.read_text(encoding='utf-8')) if output.exists() else {}
    for line in Path(path).read_text(encoding='utf-8-sig').splitlines():
        if not line.strip():
            continue
        number, body, *notes = line.split('|')
        i = int(number)
        assert str(i) not in reviews, f'Already frozen: {i}'
        sample = samples[i]
        defects = []
        for item in filter(None, body.split(';')):
            cat, level, obj, desc = item.split(':', 3)
            assert cat in CATEGORIES and (level in ['L1','L2','L3'] or (cat=='A' and level=='-'))
            defects.append({'id':cat,'severity':'' if cat=='A' else level,'object':obj,'description':desc})
        assert not any(d['id']=='A' for d in defects) or len(defects)==1
        page = ((i-1)%100)//6+1
        sheet = HERE/f"local/batch_{sample['batch']:02d}/sheet_{page:02d}.jpg"
        reviews[str(i)] = {'review_index':i, 'source_sample_key':sample['source_sample_key'],
            'reviewer':'Codex conversation visual review', 'standard_sha256':manifest['standard_sha256'],
            'checked_categories':CATEGORIES, 'defects':defects,
            'uncertainty_note':'|'.join(notes),
            'status':'AI_preannotation_pending_human_adjudication',
            'viewed_sheet':str(sheet.relative_to(ROOT)), 'viewed_sheet_sha256':sha(sheet),
            'viewing_limit':'Paired source images fitted within 382x300 without crops; ambiguous small features left for human zoom.',
            'original_defects':sample['original_defects']}
    write(output,reviews)
    print(f'Frozen visual drafts: {len(reviews)}/600')


if __name__ == '__main__':
    save(sys.argv[1])
