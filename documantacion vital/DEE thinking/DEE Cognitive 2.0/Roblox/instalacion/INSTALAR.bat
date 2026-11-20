@echo off
setlocal EnableExtensions DisableDelayedExpansion
if "%~1"=="" (
  echo Uso: INSTALAR.bat "C:\DEE_RBX_RT_NUEVO" [origen_a_denegar_1] [origen_a_denegar_2]
  exit /b 2
)
for %%I in ("%~dp0..") do set "_DEE_PACKAGE=%%~fI"
for %%I in ("%~1") do set "_DEE_DEST=%%~fI"
rem Read-only path guard. No execution-policy changes or .ps1 execution.
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -Command "$ErrorActionPreference='Stop'; $p=[IO.Path]::GetFullPath($env:_DEE_DEST); $r=[IO.Path]::GetFullPath($env:_DEE_PACKAGE); if((Test-Path -LiteralPath $p) -or $p.TrimEnd([char]92).Length -le 3 -or $p.StartsWith($r+[char]92,[StringComparison]::OrdinalIgnoreCase) -or $r.StartsWith($p+[char]92,[StringComparison]::OrdinalIgnoreCase)){exit 2}; $d=[IO.Directory]::GetParent($p); while($null -ne $d){if($d.Exists -and ($d.Attributes -band [IO.FileAttributes]::ReparsePoint)){exit 3}; $d=$d.Parent}; exit 0"
if errorlevel 1 exit /b 2
set "_DEE_HASH="
set /p "_DEE_EXPECTED="<"%_DEE_PACKAGE%\dependencias\PAYLOAD_R06.sha256"
for /f "skip=1 delims=" %%H in ('certutil.exe -hashfile "%_DEE_PACKAGE%\dependencias\DEE_ROBLOX_RUNTIME_PRIVADO_R06.zip" SHA256') do if not defined _DEE_HASH set "_DEE_HASH=%%H"
if /I not "%_DEE_EXPECTED%"=="%_DEE_HASH: =%" (
 echo SHA-256 incorrecto. No se extrae ni ejecuta nada.
 exit /b 3
)
where.exe tar.exe >nul 2>nul
if errorlevel 1 (
 echo Falta tar.exe incluido en Windows compatibles. Use Python autorizado y el instalador documentado.
 exit /b 4
)
mkdir "%_DEE_DEST%"
if errorlevel 1 exit /b 5
>"%_DEE_DEST%\EXTRACCION_TAR_R06.sha256" echo %_DEE_EXPECTED%
tar.exe -xf "%_DEE_PACKAGE%\dependencias\DEE_ROBLOX_RUNTIME_PRIVADO_R06.zip" -C "%_DEE_DEST%"
if errorlevel 1 (
 echo Extraccion incompleta preservada. No abrir Native ni reintentar sobre este destino.
 exit /b 6
)
if "%~2"=="" (
 "%_DEE_DEST%\dependencias\producto\motor\python313\python.exe" -I -S -B -X utf8 "%~dp0instalar_runtime.py" --paquete "%_DEE_PACKAGE%" --destino "%_DEE_DEST%" --finalizar-extraido
) else (
 "%_DEE_DEST%\dependencias\producto\motor\python313\python.exe" -I -S -B -X utf8 "%~dp0instalar_runtime.py" --paquete "%_DEE_PACKAGE%" --destino "%_DEE_DEST%" --finalizar-extraido --denegar "%~2" --denegar "%~3"
)
exit /b %ERRORLEVEL%
