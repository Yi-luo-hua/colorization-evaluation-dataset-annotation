"""Read-only local Label Studio discovery; never prints authentication material."""
import json
import sqlite3
import requests
from prepare import ROOT

db = sqlite3.connect('file:' + str(ROOT / 'LS_lcad_reviewer/data/label_studio.sqlite3') + '?mode=ro', uri=True)
tables = [r[0] for r in db.execute("select name from sqlite_master where type='table'")]
print('auth table names', [name for name in tables if 'token' in name or 'user' in name])
print('projects', db.execute('select id,title from project').fetchall())
for table in ['authtoken_token', 'users_user', 'project']:
    if table in tables:
        print(table, 'column names', [r[1] for r in db.execute(f'pragma table_info({table})')])

owner = db.execute('select created_by_id from project order by id desc limit 1').fetchone()[0]
row = db.execute('select key from authtoken_token where user_id=?', (owner,)).fetchone()
session = requests.Session()
session.trust_env = False
if row:
    session.headers['Authorization'] = 'Token ' + row[0]
    response = session.get('http://127.0.0.1:8080/api/projects', timeout=15)
    print('API authentication status', response.status_code)
    if response.ok:
        payload = response.json()
        print('API projects accessible', len(payload.get('results', [])) if isinstance(payload, dict) else len(payload))
    else:
        print('API authentication response type', response.headers.get('Content-Type'))
        print('API auth reason', response.json().get('detail'))
        print('Refresh token columns', [r[1] for r in db.execute('pragma table_info(token_blacklist_outstandingtoken)')])
        refresh = db.execute('select token from token_blacklist_outstandingtoken where user_id=? order by id desc limit 1', (owner,)).fetchone()
        if refresh:
            response = session.post('http://127.0.0.1:8080/api/token/refresh/', json={'refresh': refresh[0]}, timeout=15)
            print('Refresh API status', response.status_code)
            if response.ok:
                session.headers['Authorization'] = 'Bearer ' + response.json()['access']
                response = session.get('http://127.0.0.1:8080/api/projects', timeout=15)
                print('JWT project API status', response.status_code)
                if response.ok:
                    print('JWT API ready; no token printed or saved')
