@echo off
setlocal

call "C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%

set "DEE_THINKING_CMAKE_BUILD_ROOT=D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\b30wheel"
set "CMAKE_EXECUTABLE=C:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"
set "CMAKE_MAKE_PROGRAM=C:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe"
set "CXX=C:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\MSVC\14.50.35717\bin\Hostx64\x64\cl.exe"
set "DEE_THINKING_RC_COMPILER=C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\rc.exe"
set "DEE_THINKING_MT=C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\mt.exe"

"D:\Descargas\ANACONDA MINICONDA\python.exe" -I -m build --wheel --no-isolation --outdir dist .
exit /b %errorlevel%
