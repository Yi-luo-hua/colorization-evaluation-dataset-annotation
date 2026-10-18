"""Use the existing local owner's authentication without printing or persisting credentials."""
import base64
import json
import sqlite3
import zlib

import requests

from prepare import ROOT

BASE_URL = 'http://localhost:8080'


def authenticated_session():
    db = sqlite3.connect('file:' + str(ROOT / 'LS_lcad_reviewer/data/label_studio.sqlite3') + '?mode=ro', uri=True)
    owner = db.execute('select created_by_id from project order by id desc limit 1').fetchone()[0]
    session = requests.Session()
    session.trust_env = False
    token = db.execute('select key from authtoken_token where user_id=?', (owner,)).fetchone()
    if token:
        session.headers['Authorization'] = 'Token ' + token[0]
        response = session.get(BASE_URL + '/api/current-user/whoami', timeout=15)
        if response.ok and response.json()['id'] == owner:
            db.close()
            return session
        session.headers.pop('Authorization')
    # Reuse an existing, server-signed session belonging to the same local project owner.
    for key, encoded in db.execute("select session_key,session_data from django_session where expire_date>datetime('now') order by expire_date desc"):
        data = encoded.split(':', 1)[0]
        compressed = data.startswith('.')
        data = data.lstrip('.')
        payload = base64.urlsafe_b64decode(data + '=' * (-len(data) % 4))
        if compressed:
            payload = zlib.decompress(payload)
        info = json.loads(payload)
        if str(info.get('_auth_user_id')) != str(owner):
            continue
        session.cookies.set('sessionid', key)
        response = session.get(BASE_URL + '/api/current-user/whoami', timeout=15)
        if response.ok and response.json()['id'] == owner:
            session.get(BASE_URL + '/projects/', timeout=15)
            csrf = session.cookies.get('csrftoken')
            if csrf:
                session.headers['X-CSRFToken'] = csrf
            session.headers['Referer'] = BASE_URL + '/projects/'
            session.headers['Origin'] = BASE_URL
            db.close()
            return session
        session.cookies.clear()
    db.close()
    raise RuntimeError('No valid existing local owner session; browser login is required')


if __name__ == '__main__':
    session = authenticated_session()
    response = session.get(BASE_URL + '/api/projects', timeout=15)
    print('Existing owner authentication:', response.status_code)
    print('CSRF present:', bool(session.headers.get('X-CSRFToken')))
