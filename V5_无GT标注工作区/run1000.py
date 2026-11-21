"""Single-pass V5 dispatcher backed by the existing 16-lane transactional queue."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
import time
import zipfile
from collections import Counter

from single1000 import MODEL, PUBLIC, ROOT, RUN, REPO, packet, sample
from validate import validate
sys.path.append(str(REPO/"annotation_delivery/train_val_v1_20261015/scripts"))
from pipeline_store import OwnerLock, Store, now, pid_alive
from visual_receipts import read_visual_receipts
from batch_auth import batch_environment
from quota_control import explicit_exhaustion

store=Store(RUN)
stop=threading.Event()
finished=threading.Event()
role="secondary_chroma"


def keys(paths):
    return ["/".join(("train" if p.startswith("9_14") else "val",Path(p).parent.name,Path(p).stem)) for p in paths]


def seed(paths):
    if store.rows():return
    with store.tx() as db:
        for index,key in enumerate(keys(paths)):
            store.put_sample(db,dict(source_sample_key=key,state=role+"_ready",stage=role,group_id=f"{index//10+1:03}",ready_at="0"))
    for i in range(1,17):
        worker=store.worker(f"W{i:02}")
        worker.update(role="V5 单轮")
        store.worker(worker["worker_id"],worker)


def first_event(log):
    if log.exists():
        with log.open(encoding="utf-8-sig",errors="replace") as stream:
            try:return json.loads(stream.readline()).get("conversation_id")
            except ValueError:pass


def accept(md,cid,rows,worker,attempt):
    if not cid:raise ValueError("缺少原生会话 ID")
    body=md.read_text(encoding="utf8")
    images=[md.parent/path for path in re.findall(r"!\[[RS]\d+\]\(([^)]+)\)",body)]
    aliases={os.path.abspath(p):str(p.resolve()) for p in images}
    targets=[{"path":p} for p in set(aliases)|set(aliases.values())]
    reads=read_visual_receipts(cid,targets)
    seen={Path(p).resolve() for p in reads["seen"]}
    reads["missing"]=[str(p) for p in images if p.resolve() not in seen]
    if reads["missing"]:raise ValueError("缺少成功读图凭证："+", ".join(Path(p).name for p in reads["missing"]))
    validate(md)
    result=md.parent/re.search(r"结果写入 (.*)",body)[1]
    mapping=json.loads((ROOT/"local/task_index"/(result.stem+".json")).read_text(encoding="utf8"))
    report={keys([mapping[r["id"]]])[0]:r for r in json.loads(result.read_text(encoding="utf-8-sig"))}
    expected={r["source_sample_key"] for r in rows}
    if set(report)!=expected:raise ValueError("S 编号与队列源身份不一致")
    (RUN/(md.parent.name+".receipts.json")).write_text(json.dumps(reads,ensure_ascii=False),encoding="utf8")
    with store.tx() as db:
        for r in rows:
            review=report[r["source_sample_key"]]
            r.update(state="completed",checks=review["checks"],defects=review["defects"],notes=review.get("notes",{}),
                     qa_failures=attempt-1,provenance=dict(worker_id=worker,conversation_id=cid,result_path=str(result.resolve()),finished_at=now()))
            store.put_sample(db,r)
        store.put_meta(db,"state_updated_at",now())


def command_loop():
    while not finished.wait(1):
        store.update_meta(heartbeat_at=now())
        for c in store.pending_commands():
            if c["action"] in ("stop","quota-stop"):
                stop.set()
            if c["action"]=="continue-blocked":
                (RUN/"CONTINUE").write_text(now(),encoding="utf8")
            store.ack(c["id"])


def lane(number,paths,agy,pilot):
    name=f"W{number:02}"
    worker=store.worker(name)
    def status(**fields):
        worker.update(fields)
        store.worker(name,worker)
    while not stop.is_set():
        reserved=worker.get("pending_resume")
        if reserved:
            rows=[r for r in store.rows() if r["source_sample_key"] in reserved["keys"]]
            cid=worker.get("conversation_id")
        else:
            rows=store.claim(role,name)
            if not rows:return
            cid=None
        n=int(rows[0]["group_id"])
        md=packet(n,paths)
        pending=dict(keys=[r["source_sample_key"] for r in rows],batch=n)
        status(pending_resume=pending,current_task=md.parent.name,role="V5 单轮",started_at=now(),conversation_id=cid)
        feedback=""
        for attempt in range(1,7):
            if stop.is_set():return
            log=RUN/f"b{n:03}.{attempt}.jsonl"
            err=log.with_suffix(".err")
            existing=reserved and attempt==1 and worker.get("pid") and log.exists()
            adopt=existing or (n==1 and attempt==1 and pilot and log.exists())
            if adopt:
                pid=worker["pid"] if existing else pilot
                cid=first_event(log)
                process=None
            else:
                if log.exists():
                    log=RUN/f"b{n:03}.{attempt}.{time.time_ns()}.jsonl"
                    err=log.with_suffix(".err")
                prompt=f"读取 {md}，按文档顺序用 read_file 并行查看指定 PNG，一次视觉标注。仅使用 read_file、write_file。不得读取其他任务、源目录或旧答案，不使用终端、搜索、委派、脚本或验收工具。按文档在 {PUBLIC} 下对应的 _results 路径直接写 JSON，随即结束。"
                args=[agy,"--model",MODEL,"--mode","accept-edits","--output-format","stream-json"]
                if cid:
                    args+=["--conversation",cid]
                    prompt=f"继续 {md.parent.name}/任务.md。只用 read_file 和 write_file，保留已经完成的内容；禁止运行命令、查找源码、检查宿主或自行处理回执。仅补齐实际缺项。"+feedback
                with log.open("wb") as out, err.open("wb") as errors:
                    process=subprocess.Popen(args+["--print",prompt],cwd=PUBLIC,stdout=out,stderr=errors,
                                             env=batch_environment(RUN/f"auth-{name}.json"),creationflags=subprocess.CREATE_NO_WINDOW)
                pid=process.pid
            status(pid=pid,status="running",retry_count=attempt-1)
            while (process.poll() is None if process else pid_alive(pid)):
                if stop.wait(1):
                    if process:process.terminate();process.wait()
                    elif pid_alive(pid):os.kill(pid,15)
                    status(status="awaiting_continue",pid=None)
                    return
                if not cid:
                    cid=first_event(log)
                    if cid:status(conversation_id=cid)
            actual=first_event(log)
            try:
                if not actual or cid and actual!=cid:raise ValueError("会话身份异常")
                cid=actual
                accept(md,cid,rows,name,attempt)
                status(status="idle",pid=None,current_task=None,pending_resume=None,retry_count=0,conversation_id=None)
                break
            except (ValueError,OSError,TypeError,KeyError) as exc:
                feedback=str(exc)
                store.event("validation_failure",worker_id=name,batch=n,attempt=attempt,detail=feedback)
                if explicit_exhaustion(err.read_text(encoding="utf8",errors="replace") if err.exists() else ""):
                    from quota_control import pause_for_quota
                    pause_for_quota(store,{"source":"current agy stderr","batch":n},"current agy stderr",force=True)
                    stop.set();store.update_meta(phase="quota_paused")
                if not actual or attempt==6 or stop.is_set():
                    status(status="awaiting_continue",pid=None,last_error=feedback,conversation_id=cid)
                    return
                status(status="retry_wait",pid=None,last_error=feedback,conversation_id=cid)
                if stop.wait(20):return


def pack():
    rows=store.rows()
    if len(rows)!=1000 or any(r["state"]!="completed" for r in rows):return
    report={"completed":len(rows),"categories":dict(Counter(d["category"] for r in rows for d in r["defects"])),
            "empty_defects":sum(not r["defects"] for r in rows),
            "uncertain_images":sum("uncertain" in r["checks"].values() for r in rows),
            "retried_images":sum(bool(r.get("qa_failures")) for r in rows)}
    for file,data in [("reviews.json",rows),("summary.json",report)]:
        (RUN/file).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf8")
    with zipfile.ZipFile(RUN/"V5_单轮1000.zip","w",zipfile.ZIP_DEFLATED) as z:
        for file in ["reviews.json","summary.json","samples.json"]:z.write(RUN/file,file)
        for p in RUN.glob("*.receipts.json"):z.write(p,"receipts/"+p.name)
        for file in ["规则.md","标注步骤.md"]:z.write(ROOT/file,file)
    store.update_meta(phase="completed")


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--agy",required=True)
    parser.add_argument("--pilot-pid",type=int)
    a=parser.parse_args()
    with OwnerLock(RUN):
        paths=sample();seed(paths)
        store.update_meta(owner_pid=os.getpid(),heartbeat_at=now(),phase="running",state_updated_at=now(),
                          preflight={"ready":True},session_fault_policy="continue_five_then_pool_v4",
                          dispatch_control={"version":1,"owner_pid":os.getpid()})
        watcher=threading.Thread(target=command_loop,daemon=True);watcher.start()
        try:
            with ThreadPoolExecutor(max_workers=16) as pool:
                futures=[pool.submit(lane,i,paths,a.agy,a.pilot_pid) for i in range(1,17)]
                for f in futures:f.result()
            pack()
        finally:
            finished.set();watcher.join()
            store.update_meta(owner_pid=None,heartbeat_at=now())
