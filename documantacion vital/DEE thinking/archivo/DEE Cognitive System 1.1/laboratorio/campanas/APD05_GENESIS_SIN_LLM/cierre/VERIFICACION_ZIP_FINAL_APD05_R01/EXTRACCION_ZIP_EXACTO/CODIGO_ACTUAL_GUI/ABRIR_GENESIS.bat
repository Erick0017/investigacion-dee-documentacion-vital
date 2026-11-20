@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0motor\python313\python.exe" (
  echo Falta el CPython 3.13 x64 local. Extraiga el paquete operativo completo.
  pause
  exit /b 2
)
"%~dp0motor\python313\python.exe" -I -B -X utf8 "%~dp0aplicacion\GENESIS\genesis.py" %*
if errorlevel 1 pause
endlocal
