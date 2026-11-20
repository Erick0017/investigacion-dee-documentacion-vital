param(
    [string]$BuildDirectory = (Join-Path $PSScriptRoot '..\reproduction_build'),
    [string]$OutputDirectory = (Join-Path $PSScriptRoot '..\reproduced_results')
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
if (-not (Test-Path -LiteralPath $vswhere)) { throw 'vswhere.exe was not found' }
$vs = (& $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath).Trim()
if (-not $vs) { throw 'No Visual Studio C++ installation was found' }
$vcvars = Join-Path $vs 'VC\Auxiliary\Build\vcvars64.bat'
$cmake = Join-Path $vs 'Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe'
$ninja = Join-Path $vs 'Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe'
foreach ($path in @($vcvars, $cmake, $ninja)) {
    if (-not (Test-Path -LiteralPath $path)) { throw "Missing build dependency: $path" }
}

$line = 'call "{0}" >nul && "{1}" -S "{2}" -B "{3}" -G Ninja -DCMAKE_MAKE_PROGRAM="{4}" -DCMAKE_BUILD_TYPE=Release && "{1}" --build "{3}" --parallel' -f $vcvars,$cmake,$root,$BuildDirectory,$ninja
& $env:ComSpec /d /c $line
if ($LASTEXITCODE -ne 0) { throw "Build failed with exit code $LASTEXITCODE" }

$exe = Join-Path $BuildDirectory 'bin\dee_final_laboratory.exe'
& $exe $OutputDirectory
if ($LASTEXITCODE -ne 0) { throw "Runner failed with exit code $LASTEXITCODE" }
& (Join-Path $PSScriptRoot 'verify_results.ps1') -ResultPath (Join-Path $OutputDirectory 'results.json')

