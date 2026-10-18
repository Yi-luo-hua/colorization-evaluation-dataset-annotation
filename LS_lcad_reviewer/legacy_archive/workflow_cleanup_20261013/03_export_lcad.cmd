@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (echo Drag the complete Label Studio JSON export onto this file.&pause&exit /b 1)
if not exist ".venv\Scripts\python.exe" (echo Run 01_install_lcad.cmd first.&pause&exit /b 1)
".venv\Scripts\python.exe" -X utf8 "%~dp0export_reviewed_lcad.py" %*
pause
