"""Convert a full Label Studio JSON export into reviewed V4 records."""
import argparse, copy, json
from datetime import datetime, timezone
from pathlib import Path
TAXONOMY={"A":"缺色","B":"溢色","C":"错色","D":"偏色","E1":"过饱和","E2":"欠饱和","F":"视觉自然度"}
def convert(paths):
 completed=[]; pending=[]; seen=set()
 for path in paths:
  tasks=json.loads(Path(path).read_text(encoding="utf-8-sig"))
  if not isinstance(tasks,list): raise ValueError("请选择 Label Studio 的完整 JSON 导出格式")
  for task in tasks:
   data=task["data"]; key=data["image_id"]
   if key in seen: raise ValueError("重复图片："+key)
   seen.add(key); anns=[a for a in task.get("annotations",[]) if not a.get("was_cancelled")]
   if len(anns)>1: raise ValueError("同一任务有多份人工标注，请先确定最终版本："+key)
   if not anns: pending.append({"image_id":key,"reason":"未提交人工标注"}); continue
   ann=anns[0]; results={}
   for r in ann.get("result",[]): results[r["from_name"]]=r
   def ch(n): return results.get(n,{}).get("value",{}).get("choices",[])
   def txt(n): return "\n".join(results.get(n,{}).get("value",{}).get("text",[]))
   if ch("review_status") != ["已核验"]: pending.append({"image_id":key,"reason":"待复核或未选择已核验"}); continue
   a=ch("severity_A")
   if a not in (["命中"],["未命中"]): pending.append({"image_id":key,"reason":"缺少 A 判断"}); continue
   defects=[]; unresolved=[]
   if a==["命中"]: defects=[{"id":"A","name":"缺色","severity":"","description":txt("description_A")}]
   else:
    for code,name in TAXONOMY.items():
     if code=="A": continue
     v=ch("severity_"+code)
     if len(v)!=1 or v[0] not in ("无此缺陷","L1","L2","L3"): unresolved.append(code); continue
     if v[0]!="无此缺陷": defects.append({"id":code,"name":name,"severity":v[0],"description":txt("description_"+code)})
   if unresolved: pending.append({"image_id":key,"reason":"严重程度未确认","defects":unresolved}); continue
   rec=copy.deepcopy(data["original_record"]); rec["defects"]=defects; rec["original_gpt_score"]=data["original_record"].get("gpt_score"); rec["review_status"]="已核验"; rec["review_note"]=txt("review_note"); rec["reviewed_score"]=1.0 if a==["命中"] else None; rec["needs_rescoring"]=a!=["命中"]; rec["human_review"]={"task_id":task.get("id"),"annotation_id":ann.get("id"),"completed_by":ann.get("completed_by"),"updated_at":ann.get("updated_at")}
   completed.append(rec)
 return completed,pending
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("exports",nargs="+"); ap.add_argument("--out",default=str(Path(__file__).parent/"exports")); a=ap.parse_args(); done,pending=convert(a.exports); out=Path(a.out); out.mkdir(parents=True,exist_ok=True); stamp=datetime.now().strftime("%Y%m%d_%H%M%S"); (out/f"reviewed_{stamp}.json").write_text(json.dumps({"meta":{"exported_at":datetime.now(timezone.utc).isoformat(),"total_images":len(done),"needs_rescoring":True},"annotations":done},ensure_ascii=False,indent=2),encoding="utf-8"); (out/f"pending_{stamp}.json").write_text(json.dumps(pending,ensure_ascii=False,indent=2),encoding="utf-8"); print("reviewed",len(done),"pending",len(pending))
if __name__=="__main__": main()
