"""Block agy's Windows browser opener only in workflow-owned child processes."""
import os
from pathlib import Path
import shutil
import subprocess
import json
import time

GUARD = Path(__file__).with_name('no_browser')/'rundll32.exe'
CLI_STATIC_FILES = ('settings.json', 'installation_id', 'jetski_state.pbtxt')


def prepare_worker_profile(profile, *, isolate_cli_store=False):
    """Isolate global customizations while retaining auth and optional CLI store."""
    profile=Path(profile).resolve()
    config=profile/'.gemini/config'
    config.mkdir(parents=True,exist_ok=True)
    for relative in ['antigravity-cli','config/projects']:
        original=Path.home()/'.gemini'/relative
        shared=profile/'.gemini'/relative
        if relative=='antigravity-cli' and isolate_cli_store:
            if shared.exists() and shared.resolve()==original.resolve():
                continue
            shared.mkdir(parents=True,exist_ok=True)
            for fname in CLI_STATIC_FILES:
                src=original/fname
                dst=shared/fname
                if src.is_file() and not dst.exists():
                    shutil.copy2(src,dst)
            continue
        if relative=='config/projects' and shared.exists() and shared.resolve()!=original.resolve():
            backup=shared.with_name('projects.local-backup-'+str(time.time_ns()))
            if not shared.resolve().is_relative_to(profile) or not backup.resolve().is_relative_to(profile):
                raise OSError('Refusing to move a project directory outside the worker profile')
            shared.rename(backup)
        if not shared.exists():
            if os.name=='nt':
                subprocess.run(['cmd.exe','/c','mklink','/J',str(shared),str(original)],
                    check=True,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                shared.symlink_to(original,target_is_directory=True)
        if shared.resolve()!=original.resolve():
            raise OSError('Worker profile must preserve the original CLI store: '+relative)
    for name,value in [('mcp_config.json',{'mcpServers':{}}),
            ('hooks.json',{'googlecloudtools.datacloud_telemetry':{'enabled':False}})]:
        path=config/name
        content=json.dumps(value)
        if not path.exists() or path.read_text(encoding='utf-8')!=content:
            path.write_text(content,encoding='utf-8')
    return profile


def batch_environment(marker, profile=None):
    if not GUARD.is_file():
        raise OSError('Batch browser guard is missing: '+str(GUARD))
    env = os.environ.copy()
    # Go exec.LookPath resolves agy's unqualified rundll32 before CreateProcess.
    env['PATH'] = str(GUARD.parent)+os.pathsep+env.get('PATH','')
    env['MCL_AUTH_BROWSER_BLOCK_LOG'] = str(Path(marker).resolve())
    if profile is not None:
        # agy mcp list uses Windows USERPROFILE; ANTIGRAVITY_GEMINI_DIR alone is ignored.
        env['USERPROFILE']=str(Path(profile).resolve())
    return env
