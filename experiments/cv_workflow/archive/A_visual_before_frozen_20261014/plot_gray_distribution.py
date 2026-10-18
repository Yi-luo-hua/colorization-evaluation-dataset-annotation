"""Plot one-percentage-point generated-image near-gray distribution from a saved screen."""
import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--screen',type=Path,required=True)
    parser.add_argument('--run-id',required=True)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[2]
    out=root/'LS_lcad_reviewer/intermediate/experiments'/args.run_id
    out.mkdir()
    source=args.screen/'records.json'
    rows=json.loads(source.read_text(encoding='utf-8'))
    groups={'all':rows,**{s:[r for r in rows if r['split']==s] for s in ['train','val','test']},
            **{m:[r for r in rows if r['model']==m] for m in ['lcad','unicolor']},
            'GT_eligible':[r for r in rows if r['GT_eligible']],
            'excluded_GT_source':[r for r in rows if not r['GT_eligible']]}
    values={k:np.array([r['generated_color']['gray_pixel_fraction'] for r in v]) for k,v in groups.items()}
    edges=np.arange(101)/100
    counts={k:np.histogram(v,bins=edges)[0] for k,v in values.items()}
    bins=[{'lower_percent':i,'upper_percent':i+1,'interval':f'[{i}%,{i+1}%' + (']' if i==99 else ')'),
           **{k:int(v[i]) for k,v in counts.items()}} for i in range(100)]
    cumulative=[{'minimum_gray_percent':i,**{k:int(np.count_nonzero(v>=i/100)) for k,v in values.items()}} for i in range(101)]
    for filename,table in [('gray_fraction_bins_1pct.csv',bins),('gray_fraction_threshold_counts.csv',cumulative)]:
        with (out/filename).open('w',encoding='utf-8-sig',newline='') as handle:
            writer=csv.DictWriter(handle,fieldnames=table[0].keys());writer.writeheader();writer.writerows(table)
    assert sum(b['all'] for b in bins)==len(rows)
    tolerance=rows[0]['generated_color']['gray_channel_tolerance']
    summary={'created_at':datetime.now(timezone.utc).isoformat(),'source_screen':str(args.screen),
             'source_records_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
             'generated_images':len(rows),'counts':{k:len(v) for k,v in groups.items()},
             'gray_pixel_definition':f'decoded original RGB max(channel)-min(channel) <= {tolerance} / 255',
             'bin_width_percentage_points':1,'bin_intervals':'[lower,upper), last [99%,100%]',
             'threshold_counts':{str(i):cumulative[i] for i in [80,85,90,91,92,93,94,95,96,97,98,99,100]},
             'new_image_decodes':0,'new_native_calls':0,'not_A_label_counts':True}
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    plt.rcParams.update({'font.family':'Microsoft YaHei','axes.unicode_minus':False,'font.size':11})
    fig,axes=plt.subplots(3,1,figsize=(12,12),layout='constrained')
    palette={'all':('#172b3a','全量'),'train':('#2769a7','训练集'),'val':('#df8c28','验证集'),'test':('#319b83','测试集')}
    x=np.arange(100)+0.5
    for key,(color,label) in palette.items():
        for ax in axes[:2]:
            ax.plot(x,counts[key],color=color,label=f'{label}（{len(values[key]):,}张）',linewidth=1.8 if key=='all' else 1.2)
        axes[2].plot(np.arange(80,101),[cumulative[i][key] for i in range(80,101)],color=color,label=label,marker='o',markersize=3)
    axes[0].set(title='全量分布 · 每1个百分点一个区间',xlim=(0,100),ylabel='图片数量')
    axes[0].legend(frameon=False,ncol=2)
    axes[1].set(title='80%—100%近灰区间放大 · 与上图相同的1%统计',xlim=(80,100),ylabel='每个区间的图片数量')
    axes[1].set_ylim(0,max(counts['all'][80:])*1.15 or 1)
    axes[1].set_xticks(np.arange(80,101,1));axes[1].tick_params(axis='x',labelsize=9)
    axes[1].plot(x[80:],counts['all'][80:],'o',color=palette['all'][0],markersize=3)
    axes[2].set(title='筛查门槛对应的候选量 · 占比≥门槛（不是A确认数）',xlim=(80,100),ylabel='达到门槛的图片数量')
    axes[2].set_xticks(np.arange(80,101,1));axes[2].tick_params(axis='x',labelsize=9)
    for ax in axes:
        ax.grid(alpha=.18);ax.spines[['top','right']].set_visible(False)
        ax.set_xlabel('生成图中近灰像素占比（%）')
    axes[2].annotate(f"≥90%：{cumulative[90]['all']}张",xy=(90,cumulative[90]['all']),xytext=(92,cumulative[90]['all']+18),arrowprops={'arrowstyle':'-','color':'#172b3a'})
    fig.suptitle(f'生成图近灰像素占比分布 · {len(rows):,}张\n原分辨率RGB通道差≤{tolerance}/255；含上游排除GT对应的生成图',fontsize=16)
    fig.supxlabel('前两图的点为1%区间中点；区间左闭右开，最后一个包含100%。统计占比不直接认定A。',fontsize=9)
    fig.savefig(out/'gray_fraction_distribution.png',dpi=160)
    fig.savefig(out/'gray_fraction_distribution.svg')
    plt.close(fig)
    print(json.dumps(summary['threshold_counts'],ensure_ascii=False))
    print(out)


if __name__=='__main__':main()
