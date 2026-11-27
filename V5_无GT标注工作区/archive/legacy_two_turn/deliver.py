"""Export a portable review bundle once all 1,000 records have passed."""
from collections import Counter
import csv
import io
import json
import statistics
import zipfile
import argparse
import time
from single1000 import COMPLETION_ARCHIVE, PORTABLE_ARCHIVE
from run1000 import RUN,REPO,ROOT,store,sample,keys


def export():
    paths=sample()
    by_key={row["source_sample_key"]:row for row in store.rows()}
    ordered=keys(paths)
    if len(set(ordered))!=1000 or set(ordered)!=set(by_key):
        raise ValueError("抽样清单与实际样本身份不一致")
    if any(by_key[k]["state"]!="completed" for k in ordered):
        raise ValueError("仍有未验收样本")
    reviews=[]
    table=io.StringIO(newline="")
    writer=csv.writer(table)
    writer.writerow(["源编号","生成图","类别","等级","对象","描述","七类状态","判定备注"])
    summary=Counter()
    statuses=Counter()
    severity=Counter()
    calls=list(RUN.glob("b*.jsonl"))
    timings={"examples": [], "label": []}
    for n in range(1,101):
        for phase, durations in timings.items():
            first=min(RUN.glob(f"b{n:03}.{phase}.*.jsonl"),default=None)
            if not first:
                continue
            for line in first.open(encoding="utf-8-sig",errors="replace"):
                if '"event":"result"' not in line:
                    continue
                result=json.loads(line)["result"]
                if result.get("status")=="SUCCESS":
                    durations.append(result["duration_seconds"])
    final=RUN/PORTABLE_ARCHIVE
    temp=final.with_suffix(".partial")
    with zipfile.ZipFile(temp,"w",compression=zipfile.ZIP_DEFLATED) as z:
        for p,key in zip(paths,ordered):
            r=by_key[key];image="images/"+key+Path(p).suffix
            z.write(REPO/p,image,compress_type=zipfile.ZIP_STORED)
            review=dict(key=key,image=image,checks=r["checks"],defects=r["defects"],notes=r.get("notes",{}),
                        conversation_id=r["provenance"]["conversation_id"])
            reviews.append(review)
            summary["有已确认缺陷"]+=bool(r["defects"])
            summary["无缺陷"]+=not r["defects"]
            for cat,state in r["checks"].items():statuses[cat+" "+state]+=1
            for d in r["defects"] or [{}]:
                if d:severity[d["category"]+"-"+d["severity"]]+=1
                writer.writerow([key,image,*(d.get(k,"") for k in ("category","severity","object","description")),
                                 json.dumps(r["checks"],ensure_ascii=False),json.dumps(review["notes"],ensure_ascii=False)])
        facts={"样本数":len(reviews),"两轮任务包":100,"有原生调用日志的尝试数":len(calls),
               "含补试的任务包数":sum(any(len(list(RUN.glob(f"b{n:03}.{phase}.*.jsonl")))>1
                                             for phase in timings) for n in range(1,101)),
               "首次成功调用耗时中位数_秒":{phase:statistics.median(values) if values else None
                                          for phase,values in timings.items()},
               "样本统计":dict(summary),"类别状态计数":dict(statuses),"缺陷条目等级计数":dict(severity),
               "口径":"按可见证据逐类判定。执行指标和模型判定均不代表人工准确率。"}
        z.writestr("reviews.json",json.dumps(reviews,ensure_ascii=False,indent=2))
        z.writestr("summary.json",json.dumps(facts,ensure_ascii=False,indent=2))
        z.writestr("标注明细.csv",table.getvalue().encode("utf-8-sig"))
        for p in [ROOT/"规则.md",ROOT/"标注步骤.md",RUN/"samples.json"]:
            z.write(p,p.name)
        for p in sorted(RUN.glob("*.receipts.json")):z.write(p,"receipts/"+p.name)
    with zipfile.ZipFile(temp) as z:
        if z.testzip() or len([n for n in z.namelist() if n.startswith("images/")])!=1000:
            raise ValueError("ZIP 完整性检查失败")
    temp.replace(final)
    return final


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--when-ready",action="store_true")
    if parser.parse_args().when_ready:
        while not (RUN/COMPLETION_ARCHIVE).is_file():
            time.sleep(30)
    print(export())
