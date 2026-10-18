"""Reuse frozen sheets/CV for a new prompt trial; never copy previous labels."""
import argparse
import copy
import shutil
from pathlib import Path
from workflow import read_json,write_json,utc,verify_sources,OUTPUT,require_annotation_contract


def prepare_trial(baseline,out,harness,selected_sheet=None,model=None,selected_sheets=None):
    baseline=baseline.resolve();manifest=copy.deepcopy(verify_sources(baseline))
    require_annotation_contract(manifest['configuration'])
    selection=set(selected_sheets) if selected_sheets is not None else ({selected_sheet} if selected_sheet is not None else None)
    if selection is not None:
        manifest['sheets']=[s for s in manifest['sheets'] if s['path'] in selection]
        manifest['records']=[r for r in manifest['records'] if r.get('sheet') in selection]
        if 'fixed_A_provenance' in manifest:
            manifest['fixed_A_provenance']['samples']=sum(r.get('annotation_route')=='fixed_A' for r in manifest['records'])
    out.mkdir();(out/'sheets').mkdir()
    for sheet in manifest['sheets']:shutil.copy2(baseline/sheet['path'],out/sheet['path'])
    for name in ['review_request.json','review_template.json','ANTIGRAVITY_HANDOFF.md']:
        shutil.copy2(baseline/name,out/name)
    manifest['created_at']=utc();manifest['state']='awaiting_external_visual_review'
    manifest['configuration']['visual_harness']['output_contract']=harness
    if model:
        manifest['configuration']['external_reviewer']['model']=model
        for name in ['review_request.json','review_template.json']:
            data=read_json(out/name);data['reviewer']=manifest['configuration']['external_reviewer'];write_json(out/name,data)
    if selection is not None:
        request=read_json(out/'review_request.json')
        request['samples']=[r for r in request['samples'] if r['sheet'] in selection]
        keys={r['sample_key'] for r in manifest['records']}
        write_json(out/'review_request.json',request)
        if harness=='compact':
            from compact_harness import template
            write_json(out/'review_template.json',template(request))
        else:
            data=read_json(out/'review_template.json');data['reviews']=[r for r in data['reviews'] if r['sample_key'] in keys]
            write_json(out/'review_template.json',data)
    write_json(out/'manifest.json',manifest)
    from review_boundaries import write_start_instructions
    write_start_instructions(out,manifest)
    write_json(out/'trial.json',{'baseline':str(baseline),'changed_surface':'prompt and output contract',
               'same_sheet_hashes':True,'same_CV_records':True,'no_previous_labels_copied':True,'harness':harness})
    return manifest


def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',required=True,type=Path);p.add_argument('--run-id',required=True)
    p.add_argument('--harness',choices=['full','compact'],default='compact');p.add_argument('--model');args=p.parse_args()
    out=OUTPUT/args.run_id;prepare_trial(args.baseline,out,args.harness,model=args.model)
    print(out)


if __name__=='__main__':main()
