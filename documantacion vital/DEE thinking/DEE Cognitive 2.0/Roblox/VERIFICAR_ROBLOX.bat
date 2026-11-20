@echo off
setlocal
where py >nul 2>nul
if errorlevel 1 (
  echo Se necesita CPython 3.12 o posterior para esta comprobacion pura.
  echo Native requiere el runtime autorizado CPython 3.13 x64 documentado.
  exit /b 2
)
py -3 -I -S -B -X utf8 "%~dp0herramientas\verificar_portabilidad.py" %*
exit /b %errorlevel%
