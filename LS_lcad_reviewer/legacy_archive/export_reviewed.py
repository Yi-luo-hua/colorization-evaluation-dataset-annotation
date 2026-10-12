"""Convert full Label Studio JSON exports, retaining original AI records for traceability."""
import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from prepare import TAXONOMY

def convert(paths):
    completed=[];pending=[];seen=set()
    for path in paths:
        tasks=json.loads(Path(path).read_text(encoding='utf-8-sig'))
        if not isinstance(tasks,list):raise ValueError('请选择完整 JSON 导出。')
        for task in tasks:
            data=task['data'];key=data['image_id']
            if key in seen:raise ValueError('重复图片，请勿混合试标和正式项目：'+key)
            seen.add(key)
            annotations=[a for a in task.get('annotations',[]) if not a.get('was_cancelled')]
            if len(annotations)>1:raise ValueError('多份人工标注，请先确定最终版本：'+key)
            if not annotations:pending.append({'image_id':key,'reason':'未提交人工标注'});continue
            annotation=annotations[0];results={}
            for r in annotation.get('result',[]):
                if r['from_name'] in results:raise ValueError('重复标注字段：'+key)
                results[r['from_name']]=r
            def choices(name):return results.get(name,{}).get('value',{}).get('choices',[])
            def texts(name):return '\n'.join(results.get(name,{}).get('value',{}).get('text',[]))
            if choices('review_status')!=['已核验']:pending.append({'image_id':key,'reason':'待复核或未选择核验状态'});continue
            a=choices('severity_A')
            if a not in [['命中'],['未命中']]:pending.append({'image_id':key,'reason':'缺少A判断'});continue
            defects=[];unresolved=[]
            if a==['命中']:
                defects=[{'id':'A','name':TAXONOMY['A'],'severity':'','description':texts('description_A')}]
            else:
                for code,name in TAXONOMY.items():
                    if code=='A':continue
                    values=choices('severity_'+code)
                    if len(values)!=1 or values[0] not in ['无此缺陷','L1','L2','L3']:unresolved.append(code);continue
                    if values[0]!='无此缺陷':defects.append({'id':code,'name':name,'severity':values[0],'description':texts('description_'+code)})
            if unresolved:pending.append({'image_id':key,'reason':'严重程度未确认','defects':unresolved});continue
            record=copy.deepcopy(data['baseline_record']);record.pop('gpt_score',None)
            record.update(defects=defects,original_gpt_score=data['original_record'].get('gpt_score'),
                          baseline_gpt_score=data['baseline_record'].get('gpt_score'),
                          reviewed_score=1.0 if a==['命中'] else None,needs_rescoring=a!=['命中'],
                          review_status='已核验',review_note=texts('review_note'),baseline_source=data['baseline_source'])
            record['human_review']={'task_id':task.get('id'),'annotation_id':annotation.get('id'),
                                    'completed_by':annotation.get('completed_by'),'updated_at':annotation.get('updated_at')}
            record['original_record']=data['original_record']
            completed.append(record)
    return completed,pending

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('exports',nargs='+');p.add_argument('--out',default=str(Path(__file__).parent/'exports'));args=p.parse_args()
    completed,pending=convert(args.exports);out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now().strftime('%Y%m%d_%H%M%S_%f');dest=out/f'reviewed_{stamp}.json'
    payload={'meta':{'exported_at':datetime.now(timezone.utc).isoformat(),'total_images':len(completed),
                     'note':'A命中记1分；其余须使用原离线规则重新计分。A的severity为空字符串，表示不分级。'},'annotations':completed}
    dest.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/f'pending_{stamp}.json').write_text(json.dumps(pending,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Reviewed: {len(completed)}; pending in supplied export: {len(pending)}');print(dest)
    print('Default Label Studio exports may exclude unannotated tasks; check total progress in the UI.')

if __name__=='__main__':main()
