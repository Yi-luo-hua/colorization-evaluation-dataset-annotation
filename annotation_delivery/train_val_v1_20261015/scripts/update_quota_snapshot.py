"""Persist observed native agy /usage metadata without touching annotation state."""
import argparse
from pathlib import Path
import uuid

from pipeline_store import Store,now
from prepare import write

DEFAULT_RUN=Path(__file__).resolve().parents[1]/'runtime/recovery5000_20261016_01'


def record(store,five_hour=None,weekly=None,five_reset=None,weekly_reset=None,error=None):
    timestamp=now()
    observation={'attempted_at':timestamp,'check_id':uuid.uuid4().hex,'source':'native agy /usage',
        'dedicated_session':True,'model_prompt_sent':False}
    with store.tx() as db:
        row=db.execute("SELECT value FROM meta WHERE key='quota_monitor'").fetchone()
        import json
        monitor=json.loads(row[0]) if row else {}
        monitor.update(interval_minutes=10,last_attempt_at=timestamp,last_error=error,status='error' if error else 'ok')
        if error:
            observation['error']=error
        else:
            if five_hour is None or weekly is None or not (0<=five_hour<=100 and 0<=weekly<=100):
                raise ValueError('Both observed remaining percentages must be within 0..100')
            snapshot={'checked_at':timestamp,'source':observation['source'],'dedicated_session':True,
                'five_hour_remaining_percent':five_hour,'weekly_remaining_percent':weekly,
                'five_hour_refresh_in':five_reset,'weekly_refresh_in':weekly_reset,
                'detail':f'Gemini 五小时剩余 {five_hour:g}%，周剩余 {weekly:g}%',
                'query_interval_minutes':10,'check_id':observation['check_id']}
            Store.put_meta(db,'quota_snapshot',snapshot)
            monitor.update(last_success_at=timestamp)
            observation['snapshot']=snapshot
        Store.put_meta(db,'quota_monitor',monitor)
    directory=store.run_dir/'quota_checks';directory.mkdir(exist_ok=True)
    write(directory/(timestamp.replace(':','').replace('+','_')+'_'+observation['check_id'][:8]+'.json'),observation)
    return observation


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir',type=Path,default=DEFAULT_RUN)
    parser.add_argument('--five-hour-remaining',type=float)
    parser.add_argument('--weekly-remaining',type=float)
    parser.add_argument('--five-hour-refresh-in')
    parser.add_argument('--weekly-refresh-in')
    parser.add_argument('--error',help='Record failed query; keep last successful quota snapshot')
    args=parser.parse_args()
    observation=record(Store(args.run_dir),args.five_hour_remaining,args.weekly_remaining,
        args.five_hour_refresh_in,args.weekly_refresh_in,args.error)
    print('Quota query failed; previous snapshot preserved.' if args.error else observation['snapshot']['detail'])


if __name__=='__main__':
    main()
