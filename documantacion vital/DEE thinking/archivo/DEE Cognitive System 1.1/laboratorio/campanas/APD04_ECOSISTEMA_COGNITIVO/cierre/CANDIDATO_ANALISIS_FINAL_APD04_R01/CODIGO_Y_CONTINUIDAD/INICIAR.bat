@echo off
setlocal
set "DEE_ROOT=%~dp0"
if not exist "%DEE_ROOT%motor\python313\python.exe" (
  echo Falta motor\python313\python.exe. Conserve completa la carpeta DEE Cognitive System 1.1.
  exit /b 2
)
cd /d "%DEE_ROOT%motor\python313"
"%DEE_ROOT%motor\python313\python.exe" -I -B -X utf8 "%DEE_ROOT%iniciar_local.py" %*
set "DEE_RESULT=%ERRORLEVEL%"
if "%~1"=="" pause
exit /b %DEE_RESULT%
