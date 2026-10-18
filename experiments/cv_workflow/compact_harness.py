"""Small file contract: AI writes semantic labels; host supplies administrative fields."""
from workflow import VISUAL_CATEGORIES,require_annotation_contract,ANNOTATION_CONTRACT,visual_records,merge_fixed_a


def template(request):
    require_annotation_contract(request)
    return {'schema_version':'visual_review_compact_v1',
            'reviews':{r['sample_key']:None for r in request['samples']}}


def build_prompt(request,target):
    require_annotation_contract(request)
    if request['annotation_contract']!=ANNOTATION_CONTRACT:
        from archive.A_visual_before_frozen_20261014.compact_harness import build_prompt as legacy_prompt
        return legacy_prompt(request,target)
    sheets={}
    for r in request['samples']:sheets.setdefault(r['sheet'],[]).append(r['sample_key'])
    listing='\n'.join(f'{path}: '+', '.join(keys) for path,keys in sheets.items())
    groups=request.get('sheet_groups',6)
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
    object_rule=request.get('visual_harness',{}).get('object_color_rule','')
    d_rule=request.get('visual_harness',{}).get('d_boundary_rule','全图作为一个整体呈一致色彩偏移；几个物体各自换色、局部区域共同偏移、单个大物体换色都不是D。')
    b_rule=request.get('visual_harness',{}).get('b_boundary_rule','邻接区域颜色跨过物体轮廓侵染，须看见越界关系；物体内有异色块不足以认定B。')
    bleed_evidence=''
    if request.get('visual_harness',{}).get('b_boundary_evidence',False):
        bleed_evidence=('CV边界同化候选仅导航，不是B结论；只列有支持的编号，未列不代表没有B。须看邻接轮廓处颜色从哪侧进入哪侧，无法确认就不标B。\n'+
            '\n'.join(f"{r['sample_key']}：边界候选中心x={r['bleed_evidence']['center_percent'][0]}%、y={r['bleed_evidence']['center_percent'][1]}%。" for r in request['samples'] if 'bleed_evidence' in r))
    spatial_evidence=''
    if request.get('visual_harness',{}).get('spatial_hint',False):
        spatial_evidence=('色相差数值候选中心（单幅图内坐标，左上为0%，右下为100%）；只提示位置，不是物体或标签，仍检查整图：\n'+
                          '\n'.join(f"{r['sample_key']}：x={r['spatial_hint']['center_percent'][0]}%，y={r['spatial_hint']['center_percent'][1]}%" for r in request['samples'] if r.get('spatial_hint')))
    rotation_evidence=''
    if request.get('visual_harness',{}).get('d_rotation_evidence',False):
        threshold=request['visual_harness']['rotation_threshold_degrees']
        positive_only=request['visual_harness'].get('d_rotation_positive_only',False)
        rotation_evidence=('共同色相旋转证据：角度是方向/大小，色组及网格下限是共同旋转的数值支持。仅作数值候选，色组不是物体；须确认全图作为一个整体一起偏色，几个物体变色或局部共同变化不足以标D。\n'+
            ('支持下限按生成图留色程度减弱；严重褪色区域仍参与全局范围判断。\n' if any(r['rotation_evidence'].get('method')=='GT_weighted_retained_chroma_support_v2' for r in request['samples']) else '')+
            ('只列有旋转支持的编号；未列不代表没有D，平移/白平衡偏色照常看整图。\n' if positive_only else '')+
            '\n'.join(f"{r['sample_key']}：共同角{r['rotation_evidence']['common_degrees']:.0f}°，色组下限{r['rotation_evidence']['group_q10_along_common']:.0f}°，网格下限{r['rotation_evidence']['cell_q10_along_common']:.0f}°；旋转D候选{'是' if r['rotation_evidence']['score_degrees']>=threshold else '否'}" for r in request['samples'] if not positive_only or r['rotation_evidence']['score_degrees']>=threshold))
    return f'''快速图像上色标注。自行用图片工具读取下面列出的本地看板，每张最多{groups}组（尾张可少），按S编号逐行识别各组，每张只读一次。{legend}CV数字辅助，色组不是物体。
只允许读取这些看板和修改结果文件；不查原图、目录、源码、manifest，不裁剪、补图、执行命令或复核。看完后一次写文件，不逐条修改，不写分析报告。
GT已在上游初筛中确认可用，直接作为颜色参考；这里只评价生成图，不重新判断GT资格、不移除样本、完整检查本任务六类评价。
只处理下列S编号，图上其他编号不处理。逐行检查B/C/D/E1/E2/F六类，只标清楚可见的主要缺陷，微小模糊细节跳过：
宁可漏标或宽泛描述，也不要错标。GT颜色/部位拿不准就写可靠的基本色/大类，不猜细节；类别拿不准就跳过，不凑标签。
{object_rule}
本任务已排除冻结人工A样本，只标B/C/D/E1/E2/F；不要判断或输出A。E类不因GT本身低彩度而处罚。
B={b_rule}C=物体相对GT明显换色相，即使颜色合理。
D={d_rule}色组、网格或旋转候选都不能替代全图判断；数值支持弱也不跳过D。
E1/E2=具体物体相对GT过艳/褪色，可在不同物体并存；F=明确的颜色常识/材质/光照违和，合理彩灯/反光不能仅因不同于GT标F。
生成仍明确呈另一种颜色才标C；主要褪为灰白、灰黑或低彩度灰褐优先E2，不对同一物体重复C。黄变浅蓝是C，绿褪灰褐是E2。
{spatial_evidence}
{rotation_evidence}
{bleed_evidence}
等级近似：L1轻微，L2明显改变主要颜色，L3强烈影响主体/大面积。每项只写id、severity、object、description；object具体，description一句短话含GT与生成的差异（建议35字内）。同类不同主要物体可分别记录。
直接填写本地文件 {target}：保留schema_version及全部S编号。每个null替换为缺陷数组；无主要缺陷填[]，仍有彩色不能据此填[]。只有主要判断也无法成立才填{{"uncertain":"简短原因"}}。未看的编号保留null，不能当成[]。
例如："S001":[{{"id":"C","severity":"L2","object":"外套","description":"GT红色，生成图紫色。"}}],"S002":[]。
全部完成后保存文件，只回复“文件已保存”，不在回复中返回JSON。无需自己校验，程序负责。
看板按行编号：
{listing}'''


def expand(manifest,raw):
    require_annotation_contract(manifest['configuration'])
    if manifest['configuration']['annotation_contract']!=ANNOTATION_CONTRACT:
        from archive.A_visual_before_frozen_20261014.compact_harness import expand as legacy_expand
        return legacy_expand(manifest,raw)
    expected={r['sample_key'] for r in visual_records(manifest)};entries=raw['reviews']
    if set(entries)!=expected:raise ValueError('Compact file must contain every visual sample exactly once; frozen A samples are not model tasks')
    reviews=[]
    for key,value in entries.items():
        if value is None:raise ValueError(f'Uninspected compact sample: {key}')
        if isinstance(value,dict) and set(value)=={'uncertain'}:
            defects=[];decision='uncertain';uncertainties=[value['uncertain']]
        elif isinstance(value,list):
            defects=value;decision='defects' if value else 'no_defects';uncertainties=[]
        else:raise ValueError('Compact entry must be defects list or uncertainty')
        if any(d.get('id') not in VISUAL_CATEGORIES for d in defects):raise ValueError('Visual model may only write B/C/D/E1/E2/F')
        reviews.append({'sample_key':key,'inspection_complete':True,'checked_categories':VISUAL_CATEGORIES.copy(),
                        'decision':decision,'defects':defects,'uncertainties':uncertainties,'needs_crops':[]})
    return {'schema_version':'visual_review_v1','reviewer':manifest['configuration']['external_reviewer'],
            'completion_fields_source':'six visual categories from model files; A-only results from frozen human decisions',
            'fixed_A_provenance':manifest.get('fixed_A_provenance'),
            'reviews':merge_fixed_a(manifest,reviews)}


def cv_hint_text(manifest):
    if manifest['configuration']['annotation_contract']!=ANNOTATION_CONTRACT:
        from archive.A_visual_before_frozen_20261014.compact_harness import cv_hint_text as legacy_hint
        return legacy_hint(manifest)
    rows=[]
    for r in visual_records(manifest):
        f=r['cv_flags'];m=r['metrics']
        hint='数值D候选，确认是否全图整体偏色' if f['d_candidate'] else 'D数值支持弱，仍检查全图整体偏色'
        rows.append(r['sample_key']+' '+hint+f"；彩度比{m['chroma_ratio']:.2f}")
    return '\nCV导航（不是标签）：\n'+'\n'.join(rows)
