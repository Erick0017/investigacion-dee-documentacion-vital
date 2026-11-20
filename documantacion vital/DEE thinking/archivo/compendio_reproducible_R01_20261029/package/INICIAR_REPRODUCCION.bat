@echo off
setlocal
cd /d "%~dp0"
where py.exe >nul 2>nul
if errorlevel 1 (
  python -B reproducir.py menu
) else (
  py -3 -B reproducir.py menu
)
pause
