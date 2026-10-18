"""Provide complete fictional JSON examples, separate from real annotation outputs."""
from prepare import PROJECT,read,write

REVISION='result_json_examples_20261017_01'


def prepare_example(directory,request):
    example=read(PROJECT/'prompts/examples'/f'{request["stage"]}.json')
    # Only task metadata is substituted. Fictional EXAMPLE keys never enter real result rows.
    for key in ['annotation_contract','stage','packet_id','prompt_revision']:
        example[key]=request[key]
    path=(directory/'format_example.json').resolve()
    write(path,example)
    request.update(format_example_file=str(path),format_example_revision=REVISION)
    allowed=request.setdefault('allowed_read_files',[])
    for path in [str(path),request['result_file']]:
        if path not in allowed:
            allowed.append(path)
    return request


def example_instruction(request):
    return (f'先读取本轮标准JSON标注示例：{request["format_example_file"]}。'
        'EXAMPLE编号、P编号及内容均为虚构格式演示，不是本批答案；只参照字段层级，'
        '不要照抄示例的对象、描述、类别结论或条目数量。'
        f'再读取本轮结果骨架：{request["result_file"]}，保留其头字段和真实S编号，'
        '在原结构内填入本轮实际判断；缺陷对象不加reason，reason只放在原标签审核决定中。\n')
