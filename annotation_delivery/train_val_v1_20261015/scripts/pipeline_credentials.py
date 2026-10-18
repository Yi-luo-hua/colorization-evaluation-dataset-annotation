"""Local Windows-protected Label Studio PAT; access JWTs remain in process memory."""
import base64
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import time
import urllib.request
from urllib.parse import urlparse

CREDENTIAL_FILE = Path(os.environ.get('LOCALAPPDATA',Path.home()/'AppData/Local'))/'MCLAnnotation/labelstudio.pat.dpapi'
_cache = {}


def payload(token):
    try:
        segment=token.split('.')[1]
        return json.loads(base64.urlsafe_b64decode(segment+'='*(-len(segment)%4)))
    except (IndexError,ValueError):
        return {}


def local_pat():
    if os.name!='nt' or not CREDENTIAL_FILE.exists():
        return None
    class Blob(ctypes.Structure):
        _fields_=[('size',wintypes.DWORD),('data',ctypes.POINTER(ctypes.c_ubyte))]
    raw=bytes.fromhex(CREDENTIAL_FILE.read_text(encoding='ascii').strip())
    buffer=ctypes.create_string_buffer(raw)
    incoming=Blob(len(raw),ctypes.cast(buffer,ctypes.POINTER(ctypes.c_ubyte)))
    outgoing=Blob()
    crypto=ctypes.WinDLL('crypt32',use_last_error=True)
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    crypto.CryptUnprotectData.argtypes=[ctypes.POINTER(Blob),ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(Blob)]
    kernel.LocalFree.argtypes=[ctypes.c_void_p]
    if not crypto.CryptUnprotectData(ctypes.byref(incoming),None,None,None,None,1,ctypes.byref(outgoing)):
        raise OSError('Label Studio credential cannot be decrypted by the current Windows user')
    try:
        return ctypes.string_at(outgoing.data,outgoing.size).decode('utf-16-le').rstrip('\0')
    finally:
        kernel.LocalFree(outgoing.data)


def access_token(base):
    token=os.environ.get('LABEL_STUDIO_API_KEY')
    if not token:
        if urlparse(base).hostname not in ['localhost','127.0.0.1','::1']:
            raise ValueError('Locally stored PAT is only enabled for local Label Studio')
        token=local_pat()
    if not token or payload(token).get('token_type')!='refresh':
        return token
    if _cache.get('source')==token and _cache.get('expires',0)>time.time()+30:
        return _cache['access']
    request=urllib.request.Request(base.rstrip('/')+'/api/token/refresh/',method='POST',
        headers={'Content-Type':'application/json'},data=json.dumps({'refresh':token}).encode())
    with urllib.request.urlopen(request,timeout=15) as response:
        access=json.load(response)['access']
    _cache.update(source=token,access=access,expires=payload(access)['exp'])
    return access
