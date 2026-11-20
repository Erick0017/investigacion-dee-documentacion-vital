@echo off
setlocal
call "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
set "PATH=C:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja;%PATH%"
set "CMAKE_EXE=C:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"
"%CMAKE_EXE%" -S . -B build\release -G Ninja -DCMAKE_BUILD_TYPE=Release -DDEE_THINKING_BUILD_TESTS=ON -DDEE_THINKING_BUILD_EXAMPLES=ON
if errorlevel 1 exit /b %errorlevel%
"%CMAKE_EXE%" --build build\release --parallel
exit /b %errorlevel%
