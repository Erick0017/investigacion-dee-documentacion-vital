@echo off
setlocal EnableExtensions
set "TARGET=%~1"
if not defined TARGET set "TARGET=build\Release\bin\dee_thinking_consumer.exe"
if not exist "%TARGET%" (
  echo Target not found: %TARGET% 1>&2
  exit /b 2
)
set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist "%VSWHERE%" set "VSWHERE=%ProgramFiles%\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist "%VSWHERE%" (
  echo vswhere.exe not found 1>&2
  exit /b 3
)
for /f "usebackq tokens=*" %%I in (`"%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set "VSROOT=%%I"
if not defined VSROOT (
  echo Visual Studio C++ toolchain not found 1>&2
  exit /b 4
)
call "%VSROOT%\Common7\Tools\VsDevCmd.bat" -no_logo -arch=x64 -host_arch=x64 >nul
if errorlevel 1 exit /b %errorlevel%
dumpbin /DEPENDENTS "%TARGET%"
exit /b %errorlevel%
