@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0motor\python313\python.exe" (
  echo Falta el interprete portatil incluido. Extraiga toda la carpeta.
  exit /b 2
)
"%~dp0motor\python313\python.exe" -I -B -X utf8 "%~dp0actualizaciones\actualizar.py" --solo-zip
set "RESULT=%ERRORLEVEL%"
if "%~1"=="" pause
exit /b %RESULT%
