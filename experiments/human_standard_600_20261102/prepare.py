"""Frozen, reproducible stratified review set; never writes production labels."""
import collections
import hashlib
import json
import random
import sqlite3
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DB = ROOT / 'annotation_delivery/train_val_v1_20261015/runtime/recovery5000_20261016_01/state.sqlite3'
STANDARD = Path('D:/Obsidian_document/STUDY/MCL/图像处理质量评价/上色质量评价/11.2人工打标标准.md')
SEED = 20261102


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    target = HERE / 'local'
    target.mkdir(exist_ok=True)
    if (target/'manifest.json').exists():
        print('Frozen manifest already exists; not resampling.')
        return
    with sqlite3.connect(DB.as_uri()+'?mode=ro', uri=True) as conn:
        rows = [json.loads(b) for b, in conn.execute('select body from samples order by key')]
    assert len(rows) == 22768 and all(r['state'] in ('completed', 'fixed_a') for r in rows)
    counts = collections.Counter(d['id'] for r in rows for d in r['defects'])
    cells = collections.defaultdict(list)
    for row in rows:
        rec = row['record']
        # Shared GT identities can never cross development/evaluation.
        role = ('development', 'evaluation')[int(hashlib.sha256(('600-v1/'+rec['gt_path']).encode()).hexdigest(), 16) % 2]
        ds = row['defects']
        cat = min({d['id'] for d in ds}, key=lambda c: (counts[c], c)) if ds else 'empty'
        level = max((d['severity'] for d in ds if d['id'] == cat), default='')
        cells[(role, rec['split'], rec['model'], cat, level)].append(row)
    rng = random.Random(SEED)
    selected, strata = [], []
    for role in ('development', 'evaluation'):
        for split in ('train', 'val'):
            for model in ('lcad', 'unicolor'):
                group = {k: v for k, v in cells.items() if k[:3] == (role, split, model)}
                quota = {k: 0 for k in group}
                for cat, n in [('A', 3), ('empty', 15)]:
                    ks = [k for k in group if k[3] == cat]
                    assert len(ks) == 1
                    quota[ks[0]] = min(n, len(group[ks[0]]))
                others = [k for k in sorted(group) if k[3] not in ('A', 'empty')]
                # Each observed category/level cell receives coverage; remaining
                # slots use the largest remaining population/quota ratio.
                for k in others:
                    quota[k] = 1
                for _ in range(75-sum(quota.values())):
                    k = max((k for k in others if quota[k] < len(group[k])), key=lambda k: (len(group[k])/(quota[k]+1), k))
                    quota[k] += 1
                assert sum(quota.values()) == 75
                for k in sorted(group):
                    n = quota[k]
                    population = len(group[k])
                    strata.append({'role': role, 'split': split, 'model': model, 'primary_category': k[3], 'level': k[4], 'population': population, 'sampled': n, 'inclusion_probability': n/population, 'weight': population/n})
                    chosen = rng.sample(group[k], n)
                    for row in chosen:
                        selected.append({'role': role, 'stratum': list(k), 'population': population, 'inclusion_probability': n/population, 'weight': population/n, 'source': row})
    samples = []
    for role in ('development', 'evaluation'):
        part = [s for s in selected if s['role'] == role]
        rng.shuffle(part)
        # Round-robin deal into three batches: preserve mix, do not sort by labels.
        part = [part[i] for b in range(3) for i in range(b,300,3)]
        for item in part:
            i = len(samples)+1
            row = item.pop('source')
            rec = row['record']
            samples.append({**item, 'review_index': i, 'batch': (i-1)//100+1,
                'source_sample_key': row['source_sample_key'], 'record': rec,
                'original_defects': row['defects'], 'original_state': row['state'],
                'original_provenance': row.get('provenance'),
                'original_category_checks': row.get('category_checks'),
                'ai_revision': None, 'human_status': 'not_submitted'})
    assert len(samples) == len({s['source_sample_key'] for s in samples}) == 600
    dev = {s['record']['gt_path'] for s in samples if s['role']=='development'}
    ev = {s['record']['gt_path'] for s in samples if s['role']=='evaluation'}
    assert not dev & ev
    for s in samples:
        for field in ('gt', 'model'):
            assert sha(ROOT/s['record'][field+'_path']) == s['record'][field+'_sha256']
    standard_bytes = STANDARD.read_bytes()
    (target/'standard_20261102.md').write_bytes(standard_bytes)
    write(target/'manifest.json', {'schema': 'human_reference_600_v1', 'seed': SEED,
        'source_db': str(DB), 'source_db_sha256': sha(DB),
        'standard_source': str(STANDARD), 'standard_sha256': sha(STANDARD),
        'population': len(rows), 'samples': samples, 'strata': strata,
        'source_group_disjoint': True, 'ai_draft_is_human_gold': False,
        'evaluation_policy': 'Keep evaluation labels and findings out of workflow/prompt development; human adjudication is allowed. Score only after workflow is frozen.',
        'weight_note': 'Inverse inclusion probabilities within fixed source-group partitions and mutually exclusive original-label strata. Unweighted balanced sample is not population prevalence.'})
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 20)
    for batch in range(1,7):
        folder = target/f'batch_{batch:02d}'
        folder.mkdir()
        group = [s for s in samples if s['batch'] == batch]
        write(folder/'source_snapshot.json', group)
        for offset in range(0, 100, 6):
            page = group[offset:offset+6]
            sheet = Image.new('RGB', (1560, 1014), 'white')
            draw = ImageDraw.Draw(sheet)
            for pos, sample in enumerate(page):
                x = pos%2*780
                y = pos//2*338
                draw.text((x+8,y+4), f"{sample['review_index']:03d}   GT (left) | OUTPUT (right)", fill='black', font=font)
                for col, field in enumerate(('gt_path','model_path')):
                    with Image.open(ROOT/sample['record'][field]) as image:
                        image = ImageOps.contain(image.convert('RGB'),(382,300))
                        sheet.paste(image,(x+col*390+(390-image.width)//2,y+34+(300-image.height)//2))
            sheet.save(folder/f'sheet_{offset//6+1:02d}.jpg', quality=94)
    print(json.dumps({'samples':len(samples), 'roles':dict(collections.Counter(s['role'] for s in samples)), 'source_group_overlap':len(dev&ev), 'strata':len(strata), 'groups':dict(collections.Counter('/'.join(s['stratum'][:3]) for s in samples))}))


if __name__ == '__main__':
    main()
