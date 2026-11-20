[CmdletBinding()]
param(
    [string]$BuildDirectory = '',
    [string]$JunitPath = '',
    [switch]$SkipTests
)

$ErrorActionPreference = 'Stop'
$sourceRoot = (Resolve-Path $PSScriptRoot).Path
if (-not $BuildDirectory) {
    $id = [Guid]::NewGuid().ToString('N').Substring(0, 12)
    $BuildDirectory = Join-Path ([System.IO.Path]::GetTempPath()) "dt2-preintegration-candidates-$id"
}
$BuildDirectory = [System.IO.Path]::GetFullPath($BuildDirectory)

$vswhereCandidates = @(@(
    (Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'),
    (Join-Path $env:ProgramFiles 'Microsoft Visual Studio\Installer\vswhere.exe')
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) })
if (-not $vswhereCandidates) { throw 'vswhere.exe was not found.' }
$instanceJson = & $vswhereCandidates[0] -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -format json
if ($LASTEXITCODE -ne 0) { throw 'vswhere failed.' }
$instances = $instanceJson | ConvertFrom-Json
if (-not $instances) { throw 'No Visual Studio C++ instance was found.' }
$vsRoot = @($instances)[0].installationPath
$vsDevCmd = Join-Path $vsRoot 'Common7\Tools\VsDevCmd.bat'

$environmentLines = & $env:ComSpec /d /c "call `"$vsDevCmd`" -no_logo -arch=x64 -host_arch=x64 >nul && set"
if ($LASTEXITCODE -ne 0) { throw 'Visual Studio environment initialization failed.' }
$developerPath = $environmentLines | Where-Object { $_.StartsWith('PATH=', [StringComparison]::Ordinal) } | Select-Object -First 1
foreach ($line in $environmentLines) {
    $separator = $line.IndexOf('=')
    if ($separator -gt 0) {
        $name = $line.Substring(0, $separator)
        if (-not $name.Equals('Path', [StringComparison]::OrdinalIgnoreCase)) {
            [Environment]::SetEnvironmentVariable($name, $line.Substring($separator + 1), 'Process')
        }
    }
}
if (-not $developerPath) { throw 'Visual Studio did not provide PATH.' }
$env:PATH = $developerPath.Substring(5)

$cmake = Join-Path $vsRoot 'Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe'
$ninja = Join-Path $vsRoot 'Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe'
if (-not (Test-Path -LiteralPath $cmake) -or -not (Test-Path -LiteralPath $ninja)) {
    throw 'The selected Visual Studio instance has no bundled CMake/Ninja.'
}
$ctest = Join-Path (Split-Path -Parent $cmake) 'ctest.exe'
$env:PATH = "$(Split-Path -Parent $ninja);$env:PATH"

Write-Host "DEE_CANDIDATE_SOURCE=$sourceRoot"
Write-Host "DEE_CANDIDATE_BUILD=$BuildDirectory"
& $cmake -S $sourceRoot -B $BuildDirectory -G Ninja -DCMAKE_BUILD_TYPE=Release '-DCMAKE_CXX_FLAGS_RELEASE=/O2 /Ob2 /DNDEBUG'
if ($LASTEXITCODE -ne 0) { throw 'Candidate configure failed.' }
& $cmake --build $BuildDirectory --parallel
if ($LASTEXITCODE -ne 0) { throw 'Candidate build failed.' }
if (-not $SkipTests) {
    $args = @('--test-dir', $BuildDirectory, '-C', 'Release', '--output-on-failure')
    if ($JunitPath) {
        $junitParent = Split-Path -Parent ([System.IO.Path]::GetFullPath($JunitPath))
        if ($junitParent) { [System.IO.Directory]::CreateDirectory($junitParent) | Out-Null }
        $args += @('--output-junit', [System.IO.Path]::GetFullPath($JunitPath))
    }
    & $ctest @args
    if ($LASTEXITCODE -ne 0) { throw 'Candidate tests failed.' }
}
