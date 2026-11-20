[CmdletBinding()]
param([string]$BuildDirectory = '')

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
function Get-DeeAbsolutePath([string]$Value, [string]$BasePath) {
    if ([System.IO.Path]::IsPathRooted($Value)) {
        return [System.IO.Path]::GetFullPath($Value)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $BasePath $Value))
}
if (-not $BuildDirectory) { $BuildDirectory = Join-Path $projectRoot 'build\release' }
$BuildDirectory = Get-DeeAbsolutePath $BuildDirectory $projectRoot

$vswhereCandidates = @(@(
    (Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'),
    (Join-Path $env:ProgramFiles 'Microsoft Visual Studio\Installer\vswhere.exe')
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) })
if (-not $vswhereCandidates) { throw 'vswhere.exe was not found.' }
$instanceJson = & $vswhereCandidates[0] -latest -products * `
    -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -format json
if ($LASTEXITCODE -ne 0) { throw 'vswhere failed.' }
$instances = $instanceJson | ConvertFrom-Json
if (-not $instances) { throw 'No Visual Studio C++ instance was found.' }
$vsRoot = @($instances)[0].installationPath
$ctest = Join-Path $vsRoot 'Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\ctest.exe'
if (-not (Test-Path -LiteralPath $ctest)) {
    $command = Get-Command ctest.exe -ErrorAction SilentlyContinue
    if (-not $command) { throw "ctest was not found in the selected instance or PATH: $vsRoot" }
    $ctest = $command.Source
}

Write-Host "DEE_TEST_TOOLCHAIN_INSTANCE=$vsRoot"
Write-Host "DEE_CTEST=$ctest"
& $ctest --test-dir $BuildDirectory --output-on-failure
exit $LASTEXITCODE
