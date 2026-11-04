"""Launch the reviewer independently of the terminal; log to the local folder."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys
import urllib.request

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker',action='store_true')
    parser.add_argument('--port',type=int,default=8092)
    args = parser.parse_args()
    if args.worker:
        logs = HERE/'local/logs'; logs.mkdir(exist_ok=True,parents=True)
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sys.stdout = (logs/f'server_{stamp}.out.log').open('w',encoding='utf-8',buffering=1)
        sys.stderr = (logs/f'server_{stamp}.err.log').open('w',encoding='utf-8',buffering=1)
        sys.argv = ['server.py','--port',str(args.port)]
        from server import main as serve
        serve(); return
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{args.port}/api/state',timeout=2) as response:
            if 'records' in json.load(response):
                print(f'Already running: http://localhost:{args.port}/'); return
    except OSError:
        pass
    pythonw = Path(sys.executable).with_name('pythonw.exe')
    command = subprocess.list2cmdline([str(pythonw),str(Path(__file__).resolve()),'--worker','--port',str(args.port)])
    # WMI-created worker has an independent parent, rather than the calling PTY.
    script = "$s=New-CimInstance -ClassName Win32_ProcessStartup -ClientOnly -Property @{ShowWindow=[uint16]0};"+ \
        "Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine='"+command.replace("'","''")+"';ProcessStartupInformation=$s} | Select-Object ProcessId,ReturnValue | ConvertTo-Json -Compress"
    result = subprocess.run(['powershell.exe','-NoProfile','-Command',script],capture_output=True,text=True,check=True)
    launched = json.loads(result.stdout)
    if launched['ReturnValue']!=0: raise RuntimeError(launched)
    print(json.dumps({'launched':launched,'url':f'http://localhost:{args.port}/'}))


if __name__=='__main__': main()
