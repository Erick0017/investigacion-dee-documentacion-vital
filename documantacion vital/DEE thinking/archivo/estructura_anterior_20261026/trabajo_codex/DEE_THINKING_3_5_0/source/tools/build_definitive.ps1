[CmdletBinding()]
param(
    [ValidateSet('Debug', 'Release')]
    [string]$Configuration = 'Release',
    [string]$BuildDirectory = '',
    [string]$InstallPrefix = '',
    [string]$PythonExecutable = '',
    [switch]$SkipWheel
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if (-not $BuildDirectory) { $BuildDirectory = Join-Path $projectRoot 'build-definitive' }
if (-not $InstallPrefix) { $InstallPrefix = Join-Path $projectRoot 'install-definitive' }

function Invoke-Native([string]$Executable, [string[]]$Arguments) {
    Write-Host ("> " + $Executable + " " + ($Arguments -join ' '))
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $Executable"
    }
}

$vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
if (-not (Test-Path -LiteralPath $vswhere)) { throw 'vswhere.exe was not found.' }
$vsRoot = (& $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath).Trim()
if (-not $vsRoot) { throw 'A Visual Studio C++ installation was not found.' }
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
$ctest = Join-Path (Split-Path -Parent $cmake) 'ctest.exe'
$ninja = Join-Path $vsRoot 'Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe'
foreach ($tool in @($cmake, $ctest, $ninja)) {
    if (-not (Test-Path -LiteralPath $tool)) { throw "Required tool not found: $tool" }
}

Invoke-Native $cmake @(
    '-S', $projectRoot, '-B', $BuildDirectory, '-G', 'Ninja',
    "-DCMAKE_MAKE_PROGRAM=$ninja", "-DCMAKE_BUILD_TYPE=$Configuration",
    '-DDEE_THINKING_BUILD_TESTS=ON', '-DDEE_THINKING_BUILD_EXAMPLES=ON',
    '-DDEE_THINKING_BUILD_BENCHMARKS=ON', '-DDEE_THINKING_BUILD_PYTHON=OFF')
Invoke-Native $cmake @('--build', $BuildDirectory, '--parallel')
Invoke-Native $ctest @('--test-dir', $BuildDirectory, '-C', $Configuration, '--output-on-failure')
Invoke-Native $cmake @('--install', $BuildDirectory, '--config', $Configuration, '--prefix', $InstallPrefix)

$consumerBuild = Join-Path ([System.IO.Path]::GetTempPath()) ('dt30-consumer-' + [Guid]::NewGuid().ToString('N').Substring(0, 10))
$packageConfig = Get-ChildItem -LiteralPath $InstallPrefix -Filter dee_thinkingConfig.cmake -File -Recurse | Select-Object -First 1
if (-not $packageConfig) { throw 'Installed CMake package configuration is missing.' }
Invoke-Native $cmake @(
    '-S', (Join-Path $projectRoot 'tests\installed_consumer'), '-B', $consumerBuild,
    '-G', 'Ninja', "-DCMAKE_MAKE_PROGRAM=$ninja", "-DCMAKE_BUILD_TYPE=$Configuration",
    "-Ddee_thinking_DIR=$($packageConfig.Directory.FullName)",
    '-DCMAKE_FIND_USE_PACKAGE_REGISTRY=OFF', '-DCMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY=OFF')
Invoke-Native $cmake @('--build', $consumerBuild, '--parallel')
Invoke-Native (Join-Path $consumerBuild 'installed_consumer.exe') @()

if (-not $SkipWheel) {
    if (-not $PythonExecutable) { throw '-PythonExecutable must name a standard CPython 3.13 x64 interpreter.' }
    $identity = & $PythonExecutable -I -c 'import platform,struct,sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}|{platform.python_implementation()}|{struct.calcsize(chr(80))*8}")'
    if ($LASTEXITCODE -ne 0 -or $identity.Trim() -ne '3.13|CPython|64') {
        throw "Wheel build requires standard CPython 3.13 x64; got: $identity"
    }
    $env:CMAKE_EXECUTABLE = $cmake
    $env:CMAKE_MAKE_PROGRAM = $ninja
    $env:DEE_THINKING_CMAKE_BUILD_ROOT = Join-Path $projectRoot 'build-wheel'
    Invoke-Native $PythonExecutable @('-I', '-m', 'build', '--wheel', '--no-isolation', '--outdir', (Join-Path $projectRoot 'dist'), $projectRoot)
}

Write-Host "DEE_THINKING_DEFINITIVE_BUILD_COMPLETE=true"
