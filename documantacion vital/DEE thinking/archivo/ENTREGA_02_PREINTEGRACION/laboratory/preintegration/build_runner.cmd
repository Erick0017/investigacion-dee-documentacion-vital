@echo off
setlocal
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul
if errorlevel 1 exit /b %errorlevel%
cl /nologo /std:c++20 /O2 /EHsc /MD /I"..\..\include" runners\preintegration_runner.cpp /link /LIBPATH:"..\..\build\Release\lib" dee_thinking.lib /OUT:build\preintegration_runner.exe
exit /b %errorlevel%
