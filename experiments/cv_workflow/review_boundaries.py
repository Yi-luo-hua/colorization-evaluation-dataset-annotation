"""Current six-category visual instructions; legacy diagnostics live in archive."""
from workflow import ANNOTATION_CONTRACT,visual_records


def write_start_instructions(run,manifest):
    if manifest['configuration']['annotation_contract']!=ANNOTATION_CONTRACT:
        from archive.A_visual_before_frozen_20261014.review_boundaries import write_start_instructions as legacy_start
        return legacy_start(run,manifest)
    count=len(visual_records(manifest));groups=manifest['configuration']['sheet']['groups_per_sheet']
    if not count:
        text='# 固定A结果已保存\n\n此批全部来自冻结人工A名单，只标A命中。没有看板或模型任务，不调用Gemini。\n'
    else:
        text=f"""# 六类视觉标注：{count}条，A已在程序分流

使用gemini-3.8-flash-high。读取review_request.json、review_template.json和列出的{len(manifest['sheets'])}张PNG，每张最多{groups}组，尾张可少。

只评价B/C/D/E1/E2/F，不判断或输出A。GT已经上游确认可用，直接对照物体颜色，不重审GT或缩减这六类。

每张看板只读一次，不查原图、manifest/任务池/源码，不裁剪、补图或重复复核。GT色取左列、生成色取中列；热图色不是物体色，CV数值不是标签。

宁可漏标或可靠宽泛描述，不猜颜色/部位。B须看见邻接颜色跨界侵染；C须明显换色相；D严格全图整体一起偏色；E1/E2绑定具体物体，褪灰优先E2，不重复同物体C；F须明确颜色常识/材质/光照违和。

从review_template.json创建reviews_gemini.json，只填写列出的S编号。每个null替换为缺陷数组或[]；每项id/severity/object/description，临时L1/L2/L3，一句短证据。主要判断不能成立才填uncertain。保存一次，只回复“文件已保存”，不返回JSON或分析报告。

固定A结果由程序另存并汇聚，不进入此看板/请求，也不由模型修改。
"""
    (run/'START_HERE.md').write_text(text,encoding='utf-8')
