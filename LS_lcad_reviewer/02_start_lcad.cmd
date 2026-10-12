@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\label-studio.exe" (echo Run 01_install_lcad.cmd first.&pause&exit /b 1)

for %%I in ("%~dp0..") do set "IMAGE_ROOT=%%~fI"
set "LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true"
set "LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=%IMAGE_ROOT%"
set "LABEL_STUDIO_BASE_DATA_DIR=%~dp0data"
set "LATEST_VERSION_CHECK=false"

echo Image root: %IMAGE_ROOT%
echo Open http://localhost:8080 and keep this window open.
".venv\Scripts\label-studio.exe" start --data-dir "%~dp0data" --port 8080 --no-browser
pause
