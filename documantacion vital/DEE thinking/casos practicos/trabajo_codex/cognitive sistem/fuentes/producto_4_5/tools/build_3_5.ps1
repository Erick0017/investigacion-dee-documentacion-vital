[CmdletBinding()]
param([string]$BuildRoot='', [string]$PythonExecutable='', [switch]$Wheel, [switch]$Tests)
$ErrorActionPreference='Stop'
$sourceRoot=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if (-not $BuildRoot) { $BuildRoot=Join-Path ([IO.Path]::GetTempPath()) ('dt35-'+[Guid]::NewGuid().ToString('N').Substring(0,12)) }
if (-not $PythonExecutable) { throw 'Pass standard CPython 3.13 x64 with build dependencies explicitly.' }
[IO.Directory]::CreateDirectory($BuildRoot) | Out-Null
$logPath=Join-Path $BuildRoot 'COMMANDS.log'
$encoding=New-Object Text.UTF8Encoding($false)
function Invoke-Checked([string]$exe,[string[]]$arguments) {
    [IO.File]::AppendAllText($logPath,('> '+$exe+' '+($arguments -join ' ') + [Environment]::NewLine),$encoding)
    & $exe @arguments 2>&1 | ForEach-Object { $line=$_.ToString(); if(-not ($line.StartsWith('Nota: inclusi') -or $line.StartsWith('Note: including file:'))) { Write-Host $line }; [IO.File]::AppendAllText($logPath,$line+[Environment]::NewLine,$encoding) }
    $code=$LASTEXITCODE
    [IO.File]::AppendAllText($logPath,('exit_code='+$code+[Environment]::NewLine),$encoding)
    if ($code -ne 0) { throw "Command failed ($code): $exe" }
}
$vswhere=Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
$vsRoot=(& $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath).Trim()
if (-not $vsRoot) { throw 'C++ toolchain not found' }
$dev=Join-Path $vsRoot 'Common7\Tools\VsDevCmd.bat'
$lines=& $env:ComSpec /d /c "call `"$dev`" -no_logo -arch=x64 -host_arch=x64 >nul && set"
if ($LASTEXITCODE -ne 0) { throw 'Toolchain initialization failed' }
$developerPath=$lines | Where-Object { $_.StartsWith('PATH=',[StringComparison]::Ordinal) } | Select-Object -First 1
foreach($line in $lines) {
    $split=$line.IndexOf('=')
    if($split -gt 0 -and -not $line.Substring(0,$split).Equals('Path',[StringComparison]::OrdinalIgnoreCase)) { [Environment]::SetEnvironmentVariable($line.Substring(0,$split),$line.Substring($split+1),'Process') }
}
if(-not $developerPath) { throw 'Compiler PATH not supplied by Visual Studio' }
$env:PATH=$developerPath.Substring(5)
$cmake=Join-Path $vsRoot 'Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe'
$ninja=Join-Path $vsRoot 'Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe'
$ctest=Join-Path (Split-Path -Parent $cmake) 'ctest.exe'
$env:PATH=(Split-Path -Parent $ninja)+';'+$env:PATH
$nativeBuild=Join-Path $BuildRoot 'native'
$install=Join-Path $BuildRoot 'install'
Invoke-Checked $cmake @('-S',$sourceRoot,'-B',$nativeBuild,'-G','Ninja',"-DCMAKE_MAKE_PROGRAM=$ninja",'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_CXX_FLAGS_RELEASE=/O2 /Ob2 /DNDEBUG','-DDEE_THINKING_BUILD_TESTS=ON','-DDEE_THINKING_BUILD_EXAMPLES=ON','-DDEE_THINKING_BUILD_BENCHMARKS=ON')
Invoke-Checked $cmake @('--build',$nativeBuild,'--parallel','2')
if($Tests) { Invoke-Checked $ctest @('--test-dir',$nativeBuild,'--output-on-failure','--output-junit',(Join-Path $BuildRoot 'CTEST.junit.xml')) }
Invoke-Checked $cmake @('--install',$nativeBuild,'--prefix',$install)
if($Wheel) {
    $env:CMAKE_EXECUTABLE=$cmake; $env:CMAKE_MAKE_PROGRAM=$ninja
    $env:CXX=(Get-Command cl.exe).Source
    $env:DEE_THINKING_RC_COMPILER=(Get-Command rc.exe).Source
    $env:DEE_THINKING_MT=(Get-Command mt.exe).Source
    $env:DEE_THINKING_CMAKE_BUILD_ROOT=Join-Path $BuildRoot 'wheel-native'
    $env:CMAKE_BUILD_PARALLEL_LEVEL='2'
    Invoke-Checked $PythonExecutable @('-I','-m','build','--wheel','--no-isolation','--outdir',(Join-Path $BuildRoot 'wheel'),$sourceRoot)
}
Write-Host "DEE35_BUILD_ROOT=$BuildRoot"
Write-Host "DEE35_INSTALL=$install"
