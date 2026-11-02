"""Remove the former UI transport prefix, keeping description wording intact."""
from copy import deepcopy
import re

PREFIX = re.compile(r'^[^｜|\n]+[｜|]\s*(?:L[123]|不分级)\s*[｜|]')


def description_only(text):
    return '\n'.join(PREFIX.sub('', line, count=1) for line in text.split('\n'))


def clean_result(result):
    result = deepcopy(result)
    for item in result:
        if item.get('from_name', '').startswith('instances_') and item.get('type') == 'textarea':
            item['value']['text'] = [description_only(text) for text in item['value'].get('text', [])]
    return result
