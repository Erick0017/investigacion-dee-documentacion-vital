@echo off
setlocal
cd /d "%~dp0"
"%~dp0motor\python313\python.exe" -I -B -X utf8 "%~dp0actualizaciones\actualizar.py" %*
set "RESULT=%ERRORLEVEL%"
if "%~1"=="" pause
exit /b %RESULT%
