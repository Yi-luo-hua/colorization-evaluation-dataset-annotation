@echo off
setlocal
cd /d "%~dp0"

call :find_python
if not defined LOCAL_PYTHON (
    where uv >nul 2>&1
    if errorlevel 1 (
        echo Local Python 3.11 is missing. Install uv and run this file again.
        pause
        exit /b 1
    )
    uv python install 3.11 --install-dir "%~dp0.python" --no-bin --no-registry
    if errorlevel 1 goto failed
    call :find_python
)
if not defined LOCAL_PYTHON goto failed

if not exist ".venv\Scripts\python.exe" (
    "%LOCAL_PYTHON%" -m venv ".venv"
    if errorlevel 1 goto failed
)

".venv\Scripts\python.exe" -m pip --version >nul 2>&1
if errorlevel 1 ".venv\Scripts\python.exe" -m ensurepip --upgrade
".venv\Scripts\python.exe" -m pip install --no-cache-dir "label-studio==1.23.0"
if errorlevel 1 goto failed
echo Installation completed. Double-click 02_start_lcad.cmd next.
pause
exit /b 0

:find_python
for /d %%D in ("%~dp0.python\cpython-3.11*-windows-x86_64-none") do if exist "%%~fD\python.exe" set "LOCAL_PYTHON=%%~fD\python.exe"
exit /b 0

:failed
echo Installation failed.
pause
exit /b 1
