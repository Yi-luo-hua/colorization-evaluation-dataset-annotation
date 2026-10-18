"""Preserve non-saturation baselines through explicit item-level review decisions."""
import copy

from prepare import FOUR, SIX, write

POLICY = 'saturation_replace_other_explicit_review_delta'
SCHEMA = 'delivery_secondary_review_delta_v1'
REVISION = 'NR_secondary_compact_20261016_05'


def baseline_from_mapping(mapping):
    result = {}
    for sample, row in mapping.items():
        defects = row['baseline']['defects']
        result[sample] = {
            'other_defects': [
                {'baseline_id':f'P{index:03d}', 'defect':copy.deepcopy(defect)}
                for index, defect in enumerate(defects, 1) if defect.get('id') in FOUR],
            'old_saturation': [copy.deepcopy(d) for d in defects if d.get('id') in ['E1','E2']]}
    return result


def write_inheritance_guidance(directory, request):
    baseline = request['secondary_baseline']
    from review_contract import validate_entry
    for sample in baseline.values():
        for item in sample['other_defects']:
            error = validate_entry([item['defect']], FOUR)
            item['inherit_allowed'] = error is None
            if error:
                item['inherit_error'] = error
    write(directory/'prior_reviews.json', {'schema_version':'delivery_review_baseline_v1',
        'policy':POLICY, 'reviews':baseline,
        'note':'B/C/D/F are the review baseline; each P item requires an explicit decision. E1/E2 are reannotated.'})


def prepare_secondary_files(directory, request, mapping):
    request.update(secondary_merge_policy=POLICY, result_schema=SCHEMA, prompt_revision=REVISION,
                   secondary_baseline=baseline_from_mapping(mapping))
    write_inheritance_guidance(directory, request)
    write(directory/'reviews_gemini.json', {'schema_version':SCHEMA,
        **{key:request[key] for key in ['annotation_contract','stage','packet_id','prompt_revision']},
        'reviews':{key:None for key in mapping}, 'category_checks':{key:None for key in mapping}})


def merge_sample(value, baseline, compact=False):
    from review_contract import validate_entry
    if not isinstance(value, dict):
        raise ValueError('missing item-level secondary review')
    if 'uncertain' in value:
        raise ValueError('uncertain: ' + str(value['uncertain']))
    if set(value) != {'saturation_defects','other_decisions','other_additions'}:
        raise ValueError('expected saturation_defects/other_decisions/other_additions')
    decisions = value['other_decisions']
    original = {item['baseline_id']:copy.deepcopy(item['defect']) for item in baseline['other_defects']}
    if not isinstance(decisions, dict) or set(decisions) != set(original):
        raise ValueError('each original B/C/D/F item needs exactly one explicit decision')
    retained = copy.deepcopy(original)
    for identifier, old in original.items():
        decision = decisions[identifier]
        if not isinstance(decision,dict):
            raise ValueError('missing review decision: ' + identifier)
        action = decision.get('action')
        if not isinstance(decision.get('reason'),str) or not decision['reason'].strip():
            raise ValueError('missing review reason: ' + identifier)
        if action == 'retain':
            # Category and severity come from the baseline, never from an omitted replacement array.
            if compact and decision.get('inherit') is True:
                error = validate_entry([old], FOUR)
                if error:
                    raise ValueError(identifier + ': inherit is invalid (' + error +
                        '); retain the category/severity and explicitly write object and description')
            retained[identifier] = (copy.deepcopy(old) if compact and decision.get('inherit') is True else
                {'id':old['id'],'severity':old['severity'],
                 'object':decision.get('object'),'description':decision.get('description')})
        elif action == 'correct':
            corrected = decision.get('defect')
            error = validate_entry([corrected], FOUR)
            if error:
                raise ValueError(identifier + ': ' + error)
            retained[identifier] = copy.deepcopy(corrected)
        elif action == 'remove':
            del retained[identifier]
        elif action == 'uncertain':
            raise ValueError('unresolved baseline item: ' + identifier)
        else:
            raise ValueError('unknown review action: ' + identifier)
        if identifier in retained:
            error = validate_entry([retained[identifier]], FOUR)
            if error:
                raise ValueError(identifier + ': ' + error)
    for field, categories in [('saturation_defects',['E1','E2']),('other_additions',FOUR)]:
        error = validate_entry(value[field], categories)
        if error:
            raise ValueError(field + ': ' + error)
    return list(retained.values()) + copy.deepcopy(value['other_additions']) + copy.deepcopy(value['saturation_defects'])


def validate_delta_file(raw, request, mapping):
    from review_contract import validate_category_checks,expand_category_checks
    for field in ['annotation_contract','stage','packet_id','prompt_revision']:
        if raw.get(field) != request[field]:
            raise ValueError('Secondary result mismatch: ' + field)
    if raw.get('schema_version') != SCHEMA or not isinstance(raw.get('reviews'),dict) or set(raw['reviews']) != set(mapping):
        raise ValueError('Secondary result schema or sample set mismatch')
    accepted, pending = {}, {}
    for sample, record in mapping.items():
        identity = record['source_sample_key']
        try:
            compact = request.get('compact_transport')=='explicit_checks_v1'
            final = merge_sample(raw['reviews'][sample], request['secondary_baseline'][sample],compact)
            observations = raw.get('category_checks')
            checks=expand_category_checks(final,observations.get(sample) if isinstance(observations,dict) else None,SIX,compact)
            error = validate_category_checks(final,checks,SIX)
            if error:
                raise ValueError(error)
            accepted[identity] = final
        except (ValueError,TypeError,KeyError) as exc:
            pending[identity] = str(exc)
    return accepted, pending
