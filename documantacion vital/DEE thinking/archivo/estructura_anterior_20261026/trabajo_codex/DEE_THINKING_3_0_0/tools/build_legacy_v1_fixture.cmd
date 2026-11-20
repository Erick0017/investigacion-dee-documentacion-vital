@echo off
setlocal
set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist "%VSWHERE%" set "VSWHERE=%ProgramFiles%\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist "%VSWHERE%" exit /b 2
for /f "usebackq tokens=*" %%I in (`"%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set "VSROOT=%%I"
if not defined VSROOT exit /b 2
set "VSDEVCMD=%VSROOT%\Common7\Tools\VsDevCmd.bat"
if not exist "%VSDEVCMD%" exit /b 2
call "%VSDEVCMD%" -arch=x64 -host_arch=x64 >nul
if errorlevel 1 exit /b %errorlevel%
set "E1_ROOT=%~dp0..\.."
if not "%~1"=="" set "E1_ROOT=%~1"
if not exist "%E1_ROOT%\include\dee_thinking\runtime.hpp" exit /b 3
if not exist "%E1_ROOT%\build\release\lib\dee_thinking.lib" exit /b 4
if not exist "%~dp0..\fixtures\legacy_v1" mkdir "%~dp0..\fixtures\legacy_v1"
cl /nologo /std:c++20 /EHsc /O2 /MD /I"%E1_ROOT%\include" "%~dp0generate_legacy_v1_pending.cpp" /Fe:"%~dp0generate_legacy_v1_pending.exe" /link /LIBPATH:"%E1_ROOT%\build\release\lib" dee_thinking.lib
if errorlevel 1 exit /b %errorlevel%
"%~dp0generate_legacy_v1_pending.exe" "%~dp0..\fixtures\legacy_v1\pending_event_v1.deetsnap"
exit /b %errorlevel%
