@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0motor\python313\python.exe" (
  echo Falta el interprete portatil incluido. Extraiga todo el ZIP, no solo este archivo.
  exit /b 2
)
"%~dp0motor\python313\python.exe" -I -B -X utf8 "%~dp0actualizaciones\arrancar.py" %*
set "RESULT=%ERRORLEVEL%"
if "%~1"=="" pause
exit /b %RESULT%
