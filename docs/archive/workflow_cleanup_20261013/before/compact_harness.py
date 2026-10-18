"""Small file contract: AI writes semantic labels; host supplies administrative fields."""
import json
from workflow import TAXONOMY


def template(request):
    return {'schema_version':'visual_review_compact_v1',
            'reviews':{r['sample_key']:None for r in request['samples']}}


def reference_rule(request):
    policy=request.get('gt_reference_policy')
    if policy not in ['visual_confirm_BF_only','visual_confirm_reference_free','visual_confirm_exclude']:return ''
    if request.get('gt_reliability'):
        gate=('默认信任GT，不主动寻找坏GT，拿不准仍用GT检查七类。仅两种可判不可信：'
                'black_and_white=确为黑白图且无有效物体颜色；abnormal_global_cast=明显异常整体色偏，跨不同物体共同污染，且正常场景光照不能解释。'
                '自然低饱和、白灰物体、阴天、夜景、夕阳、舞台彩灯、雪景、水下环境或单色物体主导不单独构成坏GT；尚有明确颜色不能当黑白。'
                '低彩度候选不是不可信名单，不按比例凑数量。')
        reason='整体异常色偏用GT_reason="abnormal_global_cast"并加GT_evidence一句说明跨物体异常及排除正常光照的依据。'
        if policy=='visual_confirm_exclude':
            return (gate+'确认GT不可信时直接弃用该样本，不检查或标注生成图，写{"exclude_GT":"black_and_white"}；'
                    '异常整体色偏写{"exclude_GT":"abnormal_global_cast","GT_evidence":"一句场景依据"}。'
                    '不用BF_only、NR或缺陷空数组表示弃用，程序从交付和抽检流包中剔除。')
        if policy=='visual_confirm_reference_free':
            return (gate+'仅确认GT不可信后，该行改用{"NR":[缺陷项],"GT_reason":"black_and_white"}，无缺陷NR填[]；'+reason+
                    'NR只看中列生成图，不用GT、差分热图或CV相对数值定缺陷：检查A/B/D/E1/E2/F，跳过C；'
                    'A仅语义上应有多种物体颜色却全图灰阶/单色失败；D仅不同物体及中性材质共同不合理染色，正常环境暖冷光不罚；'
                    'E1仅具体物体颜色明显刺眼/霓虹化或彩色细节损失；E2仅本应有颜色的物体明显灰白褪色，自然低彩度不罚。'
                    '有颜色但不能判断原色不标C；颜色违背常识归F。不要因生成比坏GT更彩色就扣E1。'
                    'NR描述只写生成图可见缺陷，不引用GT色差；拿不准的D/E跳过，不因缺GT参考填uncertain。')
        return gate+'确认不可信时暂沿用B/F范围，写{"BF_only":[],"GT_reason":"black_and_white"}（有B/F则填缺陷数组）；'+reason+'跳过A/C/D/E1/E2，不因新增颜色扣E1，不因GT参考问题填uncertain。'
    return ('GT确无有效彩色参考（如黑白旧照片）时只检查B/F，跳过A/C/D/E1/E2；'
            '该行写{"BF_only":[缺陷项]}，没有B/F写{"BF_only":[]}，不因缺彩色参考填uncertain。'
            '低彩度候选须看GT确认，阴影/白灰物体或仍有明确颜色的场景不自动跳过。')


def build_prompt(request,target):
    sheets={}
    for r in request['samples']:sheets.setdefault(r['sheet'],[]).append(r['sample_key'])
    listing='\n'.join(f'{path}: '+', '.join(keys) for path,keys in sheets.items())
    legend=('每行左GT、中生成；右列内左小图是彩度差（正红负蓝），右小图是色相差（橙色）。红蓝不自动等于E1/E2，橙色不自动等于C，仍须对照GT具体物体。'
            if request.get('display',{}).get('mode')=='chroma_hue' else '每行左GT、中生成、右彩度差；正红负蓝，黑色不保证无错色。')
    if request.get('display',{}).get('mode')=='chroma_hue_composite':
        legend='每行左GT、中生成、右差分图：彩度增红、减蓝；色相方向差更强时显示橙色。颜色不是缺陷标签，仍须对照GT物体。'
    if request.get('display',{}).get('mode')=='ab_distance_turbo':
        legend='每行左GT、中生成、右总色度差Δab；黑色低差，蓝→绿→黄→红表示差异增大。仅比较Lab的a/b，不含亮度；亮区可为换色或彩度变化，仍对照GT物体，热图颜色不是缺陷标签。'
    if request.get('display',{}).get('mode')=='ab_distance_orange':
        legend='每行左GT、中生成、右总色度差Δab；橙色越亮差异越大，不含亮度差。亮区可为换色或彩度变化，热图颜色不是缺陷标签，仍对照GT物体。'
    if request.get('sheet_layout')=='two_columns_three_rows':
        legend='每张两列三行共六组，按S编号；每组左GT、中生成、右彩度差，正红负蓝，黑色不保证无错色。'
    if request.get('roi_overlay'):
        legend+='黄框1/2仅标出数值差异候选位置，不是物体分割或缺陷答案；仍对照整幅图。'
    gt_rule=reference_rule(request)
    candidates=request.get('low_chroma_GT_candidates',[])
    if candidates:gt_rule+='低彩度GT候选：'+','.join(candidates)+'，不是排除名单。'
    return f'''快速图像上色标注。自行用图片工具读取下面6组/张的本地看板，每张只读一次。{legend}CV数字辅助，色组不是物体。
只允许读取这些看板和修改结果文件；不查原图、目录、源码、manifest，不裁剪、补图、执行命令或复核。看完后一次写文件，不逐条修改，不写分析报告。
检查每行全部七类，只标清楚可见的主要缺陷，微小模糊细节跳过：
A=全图灰阶/单色上色失败，GT本身低彩度不罚，A唯一且severity=""。
B=具体物体颜色越界；C=物体相对GT换色，即使颜色合理。
D=多个物体/背景共同偏移，单个大物体换色不是D；色组支持弱或结构保留近0/负时优先看C/E2。
E1/E2=具体物体相对GT过艳/褪色，可在不同物体并存；F=明确的颜色常识/材质/光照违和，不因C/D自动追加。
主要褪色成浅灰白、没有明显换色相时优先E2，明显换色相才标C；不要因单纯褪色给同一物体重复追加C。
{gt_rule}
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
        if isinstance(value,dict) and 'exclude_GT' in value:
            reviews.append({'sample_key':key,'inspection_complete':True,'checked_categories':[],
                            'review_scope':'excluded_GT','decision':'excluded_GT','GT_reason':value['exclude_GT'],
                            **({'GT_evidence':value['GT_evidence']} if 'GT_evidence' in value else {}),
                            'defects':[],'uncertainties':[],'needs_crops':[]})
            continue
        scope_key=next((k for k in ['BF_only','NR'] if isinstance(value,dict) and k in value),None)
        restricted=scope_key is not None
        if restricted:
            defects=value[scope_key];decision='defects' if defects else 'no_defects';uncertainties=[]
        elif isinstance(value,dict):
            uncertainty=value['uncertain'];defects=[];decision='uncertain';uncertainties=[uncertainty]
        elif isinstance(value,list):
            defects=value;decision='defects' if value else 'no_defects';uncertainties=[]
        else:raise ValueError('Compact entry must be defects list or uncertainty')
        categories=(['B','F'] if scope_key=='BF_only' else [k for k in TAXONOMY if k!='C']) if restricted else list(TAXONOMY)
        reviews.append({'sample_key':key,'inspection_complete':True,'checked_categories':categories,
                        **({'review_scope':'reference_free_BF_only' if scope_key=='BF_only' else 'reference_free_visual',
                            **{k:value[k] for k in ['GT_reason','GT_evidence'] if k in value}} if restricted else {}),
                        'decision':decision,'defects':defects,'uncertainties':uncertainties,'needs_crops':[]})
    return {'schema_version':'visual_review_v1','reviewer':manifest['configuration']['external_reviewer'],
            'completion_fields_source':'host derived from non-null compact entries under configured category scope',
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
