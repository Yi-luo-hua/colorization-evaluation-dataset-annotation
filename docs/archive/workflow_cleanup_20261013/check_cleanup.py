"""Check archive integrity, current GT preparation and local Markdown links without model calls."""
import ast
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

root=Path(__file__).resolve().parents[3]
audit=Path(__file__).parent
sys.path.insert(0,str(root/'experiments/cv_workflow'))
import gt_quality_gate
from workflow import OUTPUT,read_json,write_json

plan=read_json(audit/'cleanup_manifest.json')
for item in plan['archive_files']:
    destination=root/item['destination']
    assert destination.is_file() and hashlib.sha256(destination.read_bytes()).hexdigest()==item['sha256']
    if item['source']!='LS_lcad_reviewer/使用说明_lcad师弟.md':assert not (root/item['source']).exists()
for relative,digest in plan['protected_sha256'].items():
    assert hashlib.sha256((root/relative).read_bytes()).hexdigest()==digest,relative

# Ordinary GT preparation must work with only this run's candidates, not the cancelled BF experiment.
rows=read_json(OUTPUT/'gt_quality_all_splits_20261013/candidate_selection.json')['records'][:2]
with tempfile.TemporaryDirectory(prefix='GT_cleanup_check_',dir=OUTPUT) as directory:
    run=Path(directory);write_json(run/'candidate_selection.json',{'records':rows})
    gt_quality_gate.prepare(run)
    manifest=read_json(run/'GT_manifest.json')
    assert len(manifest['groups'])==2 and len(manifest['sheets'])==1
    assert all(m['kind']=='dataset' for g in manifest['groups'] for m in g['members'])

archived_names={Path(r['source']).stem for r in plan['archive_files'] if r['source'].endswith('.py')}
for path in (root/'experiments/cv_workflow').glob('*.py'):
    tree=ast.parse(path.read_text(encoding='utf-8-sig'))
    for node in ast.walk(tree):
        modules=([node.module] if isinstance(node,ast.ImportFrom) else [a.name for a in node.names]) if isinstance(node,(ast.Import,ast.ImportFrom)) else []
        assert not set(modules)&archived_names,(path.name,modules)

documents=[root/'README.md',root/'AGENTS.md',root/'LS_lcad_reviewer/使用说明_lcad师弟.md']
documents+=list((root/'docs').glob('*.md'))+list((root/'docs/experiments').glob('*.md'))
documents+=list((root/'experiments/cv_workflow').glob('*.md'))+[root/'experiments/cv_workflow/archive/rounds_01_14/README.md']
broken=[];links=0
for path in documents:
    text=path.read_text(encoding='utf-8-sig')
    text=re.sub(r'```[\s\S]*?```','',text)
    for target in re.findall(r'\]\(([^)]+)\)',text):
        target=target.strip('<>').split('#')[0]
        if not target or re.match(r'^[a-zA-Z]+://',target):continue
        resolved=(path.parent/target).resolve();links+=1
        if not resolved.exists():broken.append({'document':str(path.relative_to(root)),'target':target})
result={'archived_files_byte_identical':len(plan['archive_files']),
        'protected_configuration_numerical_modules_GT_registry_unchanged':True,
        'GT_prepare_without_historical_dependency':True,'no_active_import_of_archived_modules':True,
        'checked_local_links':links,'broken_links':broken,'model_calls':0}
write_json(audit/'verification.json',result)
print(json.dumps(result,ensure_ascii=False,indent=2))
assert not broken
