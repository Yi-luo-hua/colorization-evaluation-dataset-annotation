"""Validate model-written files without deciding semantic defect labels."""
import re

REFERENCE = re.compile(r'(?<![A-Za-z])GT(?![A-Za-z])|ground\s*truth|真值|参考图|原图', re.I)
HEADING = re.compile(r'^[^。！？\n]{1,30}[:：]|[（(]\s*(?:[A-F]\d?[- ]?)?L[123]\s*[）)]|\b(?:[A-F]\d?[- ]?)?L[123]\b|^[【\[].{1,20}[】\]]')
HIDDEN_HISTORY = re.compile(r'原本|本应|原为|原先|原来(?:的|是|为)|(?:由|从).{0,8}色.{0,4}(?:变为|变成|转为)')


def validate_entry(value, categories):
    if value is None:
        return 'not_written'
    if isinstance(value, dict) and set(value) == {'uncertain'}:
        return 'uncertain: ' + str(value['uncertain'])
    if not isinstance(value, list):
        return 'entry must be a defects list'
    for defect in value:
        if not isinstance(defect, dict) or set(defect) != {'id', 'severity', 'object', 'description'}:
            return 'defect fields must be id/severity/object/description'
        if defect['id'] not in categories or defect['severity'] not in ['L1', 'L2', 'L3']:
            return 'category or severity outside this stage'
        if not isinstance(defect['object'], str) or not defect['object'].strip():
            return 'missing object'
        text = defect['description']
        if not isinstance(text, str) or not text.strip():
            return 'missing description'
        if REFERENCE.search(text) or HIDDEN_HISTORY.search(text):
            return 'description contains reference comparison or hidden color history'
        if HEADING.search(text):
            return 'description contains a heading or severity code'
    return None


def expand_category_checks(defects, checks, categories, compact=False):
    if not compact or not isinstance(checks,dict):
        return checks
    result = {}
    for category,check in checks.items():
        if isinstance(check,str) and check in ['clear','hit','uncertain']:
            # The model must explicitly supply every category; no negative defaults.
            evidence = ('模型逐类审核后明确判为无此缺陷。' if check=='clear' else
                '；'.join(d['description'] for d in defects if d['id']==category) if check=='hit' else '模型明确表示待定。')
            result[category] = {'status':check,'evidence':evidence}
        else:
            result[category] = check
    return result


def validate_category_checks(defects, checks, categories):
    if not isinstance(checks, dict) or set(checks) != set(categories):
        return 'missing per-category observation records'
    hits = {d['id'] for d in defects}
    for category, check in checks.items():
        if not isinstance(check, dict) or set(check) != {'status', 'evidence'}:
            return 'category observation fields must be status/evidence'
        if check['status'] == 'uncertain':
            return 'uncertain category: ' + category
        expected = 'hit' if category in hits else 'clear'
        if check['status'] != expected or not isinstance(check['evidence'], str) or not check['evidence'].strip():
            return 'category observation inconsistent with defects: ' + category
    return None


def validate_file(raw, request, mapping):
    if not isinstance(raw,dict):
        raise ValueError('Result root must be a JSON object')
    if request.get('secondary_merge_policy') == 'saturation_replace_other_explicit_review_delta':
        from secondary_review import validate_delta_file
        return validate_delta_file(raw, request, mapping)
    for field in ['annotation_contract', 'stage', 'packet_id']:
        if raw.get(field) != request[field]:
            raise ValueError(f'Result {field} mismatch')
    if raw.get('schema_version') != 'delivery_review_compact_v2':
        raise ValueError('Result schema mismatch')
    if request.get('prompt_revision') and raw.get('prompt_revision') != request['prompt_revision']:
        raise ValueError('Prompt revision mismatch')
    if not isinstance(raw.get('reviews'),dict) or set(raw['reviews']) != set(mapping):
        raise ValueError('Result sample identity set mismatch')
    accepted, pending = {}, {}
    for key, value in raw['reviews'].items():
        error = validate_entry(value, request['checked_categories'])
        if not error and (request.get('prompt_revision') or 'category_checks' in raw):
            observations = raw.get('category_checks')
            checks=expand_category_checks(value,observations.get(key) if isinstance(observations,dict) else None,
                request['checked_categories'],request.get('compact_transport')=='explicit_checks_v1')
            error = validate_category_checks(value,checks,request['checked_categories'])
        identity = mapping[key]['source_sample_key']
        if error:
            pending[identity] = error
        else:
            accepted[identity] = value
    return accepted, pending
