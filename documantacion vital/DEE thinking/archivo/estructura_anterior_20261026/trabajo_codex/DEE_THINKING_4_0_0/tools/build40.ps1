param([Parameter(Mandatory=$true)][string]$SourcePath,[Parameter(Mandatory=$true)][string]$BuildRoot,[Parameter(Mandatory=$true)][string]$ProductRoot,[ValidateSet('wheel','cpp','consumer')][string]$Stage='wheel',[string]$PythonExecutable='D:\Descargas\ANACONDA MINICONDA\python.exe',[string]$ConsumerSource='')
$ErrorActionPreference='Stop'
$vswhere=Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
$vsRoot=(& $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath).Trim()
if (-not $vsRoot) { throw 'C++ toolchain unavailable' }
$dev=Join-Path $vsRoot 'Common7\Tools\VsDevCmd.bat'
$lines=& $env:ComSpec /d /c "call `"$dev`" -no_logo -arch=x64 -host_arch=x64 >nul && set"
if ($LASTEXITCODE -ne 0) { throw 'Developer environment initialization failed' }
$developerPath=$lines | Where-Object { $_.StartsWith('PATH=',[StringComparison]::Ordinal) } | Select-Object -First 1
foreach($line in $lines) { $sep=$line.IndexOf('='); if($sep -gt 0) { $key=$line.Substring(0,$sep); if(-not $key.Equals('Path',[StringComparison]::OrdinalIgnoreCase)) { [Environment]::SetEnvironmentVariable($key,$line.Substring($sep+1),'Process') } } }
if(-not $developerPath){throw 'Compiler PATH unavailable'}
$env:PATH=$developerPath.Substring(5)
$env:CXX=(Get-Command cl.exe).Source
$env:DEE_THINKING_RC_COMPILER=(Get-Command rc.exe).Source
$env:DEE_THINKING_MT=(Get-Command mt.exe).Source
$env:DISTUTILS_USE_SDK='1'
$env:MSSdk='1'
$cmake=Join-Path $vsRoot 'Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe'
$ninja=Join-Path $vsRoot 'Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe'
$ctest=Join-Path (Split-Path $cmake) 'ctest.exe'
function Native([string]$exe,[string[]]$args40) { Write-Output ('> '+$exe+' '+($args40 -join ' ')); & $exe @args40; if($LASTEXITCODE -ne 0){throw ('Command exit '+$LASTEXITCODE)} }
New-Item -ItemType Directory -Path $BuildRoot -Force | Out-Null
$record=[ordered]@{stage=$Stage;utc=[DateTimeOffset]::UtcNow.ToString('o');vs_instance=$vsRoot;cmake=$cmake;ninja=$ninja;compiler=(Get-Command cl.exe).Source;source=$SourcePath;build=$BuildRoot;python=$PythonExecutable;release_flags='/O2 /Ob2 /DNDEBUG';configuration='Release';language='C++20'}
[IO.File]::WriteAllText((Join-Path $ProductRoot ('BUILD_'+$Stage+'.json')),($record|ConvertTo-Json),[Text.UTF8Encoding]::new($false))
Native $cmake @('--version'); Native (Get-Command cl.exe).Source @('/?')
if($Stage -eq 'wheel') {
  $env:CMAKE_EXECUTABLE=$cmake; $env:CMAKE_MAKE_PROGRAM=$ninja; $env:CMAKE_BUILD_PARALLEL_LEVEL='2'; $env:DEE_THINKING_CMAKE_BUILD_ROOT=Join-Path $BuildRoot 'wheel_native'
  Native $PythonExecutable @('-I','-m','build','--wheel','--no-isolation','--outdir',(Join-Path $ProductRoot 'wheel'),$SourcePath)
} elseif($Stage -eq 'cpp') {
  Native $cmake @('-S',$SourcePath,'-B',(Join-Path $BuildRoot 'cpp'),'-G','Ninja',"-DCMAKE_MAKE_PROGRAM=$ninja",'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_CXX_FLAGS_RELEASE=/O2 /Ob2 /DNDEBUG','-DDEE_THINKING_BUILD_TESTS=ON','-DDEE_THINKING_BUILD_PYTHON=OFF','-DDEE_THINKING_BUILD_EXAMPLES=ON','-DDEE_THINKING_BUILD_BENCHMARKS=OFF')
  Native $cmake @('--build',(Join-Path $BuildRoot 'cpp'),'--parallel','2')
  Native $ctest @('--test-dir',(Join-Path $BuildRoot 'cpp'),'--output-on-failure','--timeout','900','--output-junit',(Join-Path $ProductRoot 'validation/ctest.xml'))
  Native $cmake @('--install',(Join-Path $BuildRoot 'cpp'),'--prefix',(Join-Path $ProductRoot 'install_cpp'))
} else {
  if(-not $ConsumerSource){throw 'ConsumerSource missing'}
  Native $cmake @('-S',$ConsumerSource,'-B',(Join-Path $BuildRoot 'consumer'),'-G','Ninja',"-DCMAKE_MAKE_PROGRAM=$ninja",'-DCMAKE_BUILD_TYPE=Release',('-DCMAKE_PREFIX_PATH='+(Join-Path $ProductRoot 'install_cpp')),'-DCMAKE_FIND_USE_PACKAGE_REGISTRY=OFF','-DCMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY=OFF')
  Native $cmake @('--build',(Join-Path $BuildRoot 'consumer'),'--parallel','2')
  Native (Join-Path $BuildRoot 'consumer/dee4_consumer.exe') @((Join-Path $ProductRoot 'install_cpp/share/dee_thinking/fixtures/mbp4/OBP_FRESH_VALIDATED_T32.deetsnap'),(Join-Path $ProductRoot 'validation/consumer'))
}
