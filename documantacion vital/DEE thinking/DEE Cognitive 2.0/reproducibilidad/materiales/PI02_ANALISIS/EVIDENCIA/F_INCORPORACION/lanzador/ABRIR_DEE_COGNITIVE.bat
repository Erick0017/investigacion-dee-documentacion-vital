@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0motor\python313\python.exe" (
  echo Falta el interprete local. Extraiga la carpeta completa de la entrega.
  pause
  exit /b 2
)
"%~dp0motor\python313\python.exe" -I -B -X utf8 "%~dp0aplicacion\inicio.py" %*
if errorlevel 1 pause
endlocal
