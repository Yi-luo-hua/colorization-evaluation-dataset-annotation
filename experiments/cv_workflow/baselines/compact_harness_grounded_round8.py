"""Small file contract: AI writes semantic labels; host supplies administrative fields."""
import json
from workflow import TAXONOMY


def template(request):
    return {'schema_version':'visual_review_compact_v1',
            'reviews':{r['sample_key']:None for r in request['samples']}}


def build_prompt(request,target):
    sheets={}
    for r in request['samples']:sheets.setdefault(r['sheet'],[]).append(r['sample_key'])
    listing='\n'.join(f'{path}: '+', '.join(keys) for path,keys in sheets.items())
    legend=('每行左GT、中生成；右列内左小图是彩度差（正红负蓝），右小图是色相差（橙色）。红蓝不自动等于E1/E2，橙色不自动等于C，仍须对照GT具体物体。'
            if request.get('display',{}).get('mode')=='chroma_hue' else '每行左GT、中生成、右彩度差；正红负蓝，黑色不保证无错色。')
    if request.get('display',{}).get('mode')=='chroma_hue_composite':
        legend='每行左GT、中生成、右差分图：彩度增红、减蓝；色相方向差更强时显示橙色。颜色不是缺陷标签，仍须对照GT物体。'
    return f'''快速图像上色标注。自行用图片工具读取下面6组/张的本地看板，每张只读一次。{legend}CV数字辅助，色组不是物体。
只允许读取这些看板和修改结果文件；不查原图、目录、源码、manifest，不裁剪、补图、执行命令或复核。看完后一次写文件，不逐条修改，不写分析报告。
检查每行全部七类，只标清楚可见的主要缺陷，微小模糊细节跳过：
A=全图灰阶/单色上色失败，GT本身低彩度不罚，A唯一且severity=""；仍有清楚已着色的物体时不用A，全图较灰不等于A。
B=具体物体颜色越界；C=物体相对GT换色，即使颜色合理。
D=多个物体/背景共同偏移，单个大物体换色不是D；色组支持弱或结构保留近0/负时优先看C/E2。
E1/E2=具体物体相对GT过艳/褪色，可在不同物体并存；F=明确的颜色常识/材质/光照违和，不因C/D自动追加。
主要褪色成浅灰白、没有明显换色相时优先E2，明显换色相才标C；不要因单纯褪色给同一物体重复追加C。
先认清左侧GT实际颜色再比较；白灰表面的小色斑/反光不扩大为整件物体的GT颜色，不从生成图倒推GT。
等级近似：L1轻微局部，L2明显改变物体主要颜色，L3强烈影响主体/大面积。每项只写id、severity、object、description；object具体，description一句短话含GT与生成的差异（建议35字内）。同类不同主要物体可分别记录。
直接填写本地文件 {target}：保留schema_version及全部S编号。每个null替换为缺陷数组；无主要缺陷填[]。只有主要判断也无法成立才填{{"uncertain":"简短原因"}}。未看的编号保留null，不能当成[]。
例如："S001":[{{"id":"C","severity":"L2","object":"外套","description":"GT红色，生成图紫色。"}}],"S002":[]。
全部完成后保存文件，只回复“文件已保存”，不在回复中返回JSON。无需自己校验，程序负责。
看板按行编号：
{listing}'''


def expand(manifest,raw):
    expected={r['sample_key'] for r in manifest['records']};entries=raw['reviews']
    if set(entries)!=expected:raise ValueError('Compact file must contain every sample exactly once')
    reviews=[]
    for key,value in entries.items():
        if value is None:raise ValueError(f'Uninspected compact sample: {key}')
        if isinstance(value,dict):
            uncertainty=value['uncertain'];defects=[];decision='uncertain';uncertainties=[uncertainty]
        elif isinstance(value,list):
            defects=value;decision='defects' if value else 'no_defects';uncertainties=[]
        else:raise ValueError('Compact entry must be defects list or uncertainty')
        reviews.append({'sample_key':key,'inspection_complete':True,'checked_categories':list(TAXONOMY),
                        'decision':decision,'defects':defects,'uncertainties':uncertainties,'needs_crops':[]})
    return {'schema_version':'visual_review_v1','reviewer':manifest['configuration']['external_reviewer'],
            'completion_fields_source':'host derived from non-null compact entries under seven-category instruction',
            'reviews':reviews}


def cv_hint_text(manifest):
    rows=[]
    for r in manifest['records']:
        f=r['cv_flags'];m=r['metrics']
        # All signs remain candidates; the model still checks every row visually.
        hints=[]
        if f['a_candidate']:hints.append('A候选，快速确认是否全图灰阶/单色失败')
        elif f['d_candidate']:hints.append('D候选，确认是否多个物体共同偏移')
        else:hints.append('D共同证据不足，优先检查具体物体C/E')
        if not f['a_candidate']:hints.append(f"彩度比{m['chroma_ratio']:.2f}")
        rows.append(r['sample_key']+' '+';'.join(hints))
    return '\nCV导航（不是标签；不能凭候选免看图或自动添加缺陷）：\n'+'\n'.join(rows)
