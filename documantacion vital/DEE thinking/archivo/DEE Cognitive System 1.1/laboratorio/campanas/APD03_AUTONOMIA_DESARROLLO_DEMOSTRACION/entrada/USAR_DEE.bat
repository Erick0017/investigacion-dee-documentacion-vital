@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0motor\python313\python.exe" (
  echo Falta el interprete incluido. Extraiga cognitive_sistem_colaborador.zip completo.
  exit /b 2
)
"%~dp0motor\python313\python.exe" -I -B -X utf8 "%~dp0usar_dee.py" %*
exit /b %ERRORLEVEL%
