[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Install,[Parameter(Mandatory=$true)][string]$BuildRoot,[string]$ConsumerSource='')
$ErrorActionPreference='Stop'
if(-not $ConsumerSource){$ConsumerSource=Join-Path $PSScriptRoot '..\examples\external_3_5'}
$vswhere=Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
$vsRoot=(& $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath).Trim()
if(-not $vsRoot){throw 'C++ toolchain missing'}
$dev=Join-Path $vsRoot 'Common7\Tools\VsDevCmd.bat'
$lines=& $env:ComSpec /d /c "call `"$dev`" -no_logo -arch=x64 -host_arch=x64 >nul && set"
if($LASTEXITCODE -ne 0){throw 'Developer environment initialization failed'}
$developerPath=$lines | Where-Object {$_.StartsWith('PATH=',[StringComparison]::Ordinal)} | Select-Object -First 1
foreach($line in $lines){$split=$line.IndexOf('=');if($split -gt 0 -and -not $line.Substring(0,$split).Equals('Path',[StringComparison]::OrdinalIgnoreCase)){[Environment]::SetEnvironmentVariable($line.Substring(0,$split),$line.Substring($split+1),'Process')}}
if(-not $developerPath){throw 'Developer PATH missing'}
$env:PATH=$developerPath.Substring(5)
$cmake=Join-Path $vsRoot 'Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe'
$ninja=Join-Path $vsRoot 'Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe'
& $cmake -S $ConsumerSource -B $BuildRoot -G Ninja "-DCMAKE_MAKE_PROGRAM=$ninja" "-DCMAKE_PREFIX_PATH=$Install" -DCMAKE_BUILD_TYPE=Release
if($LASTEXITCODE -ne 0){throw 'External consumer configure failed'}
& $cmake --build $BuildRoot --parallel 2
if($LASTEXITCODE -ne 0){throw 'External consumer build failed'}
