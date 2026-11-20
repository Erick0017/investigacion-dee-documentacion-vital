@echo off
setlocal
set "CTEST_EXE=C:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\ctest.exe"
"%CTEST_EXE%" --test-dir build\release --output-on-failure
exit /b %errorlevel%
