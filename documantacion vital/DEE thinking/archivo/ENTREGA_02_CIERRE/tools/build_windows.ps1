[CmdletBinding()]
param(
    [ValidateSet('Debug', 'Release', 'RelWithDebInfo', 'MinSizeRel')]
    [string]$Configuration = 'Release',
    [string]$BuildDirectory = '',
    [string]$InstallPrefix = '',
    [string]$ConsumerBuildDirectory = '',
    [switch]$SkipTests
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$buildRunId = [Guid]::NewGuid().ToString('N').Substring(0, 12)
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Add-DeeLogLine([string]$Path, [string]$Line) {
    if ($Path) {
        [System.IO.File]::AppendAllText($Path, $Line + [Environment]::NewLine, $utf8NoBom)
    }
}

function Invoke-DeeNative([string]$Executable, [string[]]$Arguments, [string]$LogPath = '') {
    Add-DeeLogLine $LogPath ("> " + $Executable + " " + ($Arguments -join ' '))
    & $Executable @Arguments 2>&1 | ForEach-Object {
        $line = $_.ToString()
        Write-Host $line
        Add-DeeLogLine $LogPath $line
    }
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "Command failed with exit code ${exitCode}: $Executable"
    }
}

function Get-DeeAbsolutePath([string]$Value, [string]$BasePath) {
    if ([System.IO.Path]::IsPathRooted($Value)) {
        return [System.IO.Path]::GetFullPath($Value)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $BasePath $Value))
}
if (-not $BuildDirectory) {
    # Provenance must come from a clean tree.  A unique default also prevents
    # stale cache flags or deleted targets from contaminating the release.
    $BuildDirectory = Join-Path $projectRoot ("build\" + $Configuration.ToLowerInvariant() + "-$buildRunId")
}
if (-not $InstallPrefix) {
    # A unique empty prefix prevents stale headers/configs from making the
    # installed-consumer test pass against a previous installation.
    $InstallPrefix = Join-Path $projectRoot ("build\install-" + $Configuration.ToLowerInvariant() + "-$buildRunId")
}
$BuildDirectory = Get-DeeAbsolutePath $BuildDirectory $projectRoot
$InstallPrefix = Get-DeeAbsolutePath $InstallPrefix $projectRoot
$captureReleaseEvidence = ($Configuration -eq 'Release' -and -not $SkipTests)
$validationDirectory = Join-Path $projectRoot 'validation'
$buildLog = ''
$ctestLog = ''
$junitPath = ''
if ($captureReleaseEvidence) {
    [System.IO.Directory]::CreateDirectory($validationDirectory) | Out-Null
    $buildLog = Join-Path $validationDirectory 'build_and_installed_consumer.log'
    $ctestLog = Join-Path $validationDirectory 'ctest.log'
    $junitPath = Join-Path $validationDirectory 'ctest.junit.xml'
    [System.IO.File]::WriteAllText($buildLog, "dee_build_log_schema=v1`n", $utf8NoBom)
    [System.IO.File]::WriteAllText($ctestLog, "dee_ctest_log_schema=v1`n", $utf8NoBom)
}
if (-not $ConsumerBuildDirectory) {
    # MSVC has a short object-path limit.  Building the independent consumer
    # below an already deep source/build tree can make even a trivial compiler
    # check fail before it reaches this package.  Keep that genuinely separate
    # consumer build in the process temp directory by default.
    $consumerBuildId = [Guid]::NewGuid().ToString('N').Substring(0, 12)
    $ConsumerBuildDirectory = Join-Path ([System.IO.Path]::GetTempPath()) ("dt2-consumer-$consumerBuildId")
} else {
    $ConsumerBuildDirectory = Get-DeeAbsolutePath $ConsumerBuildDirectory $projectRoot
}

$vswhereCandidates = @(@(
    (Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'),
    (Join-Path $env:ProgramFiles 'Microsoft Visual Studio\Installer\vswhere.exe')
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) })
if (-not $vswhereCandidates) { throw 'vswhere.exe was not found; a C++ Visual Studio installation is required.' }
$vswhere = $vswhereCandidates[0]
$instanceJson = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -format json
if ($LASTEXITCODE -ne 0) { throw 'vswhere failed while locating a C++ toolchain.' }
$instances = $instanceJson | ConvertFrom-Json
if (-not $instances) { throw 'No Visual Studio instance with the C++ toolchain was found.' }
$instance = @($instances)[0]
$vsRoot = $instance.installationPath
$vsDevCmd = Join-Path $vsRoot 'Common7\Tools\VsDevCmd.bat'
if (-not (Test-Path -LiteralPath $vsDevCmd)) { throw "VsDevCmd.bat missing in $vsRoot" }

# Import one instance's compiler environment. CMake/Ninja then come from that
# same instance, avoiding the former VS 2022/VS 18 toolchain mix.
$environmentCommand = "call `"$vsDevCmd`" -no_logo -arch=x64 -host_arch=x64 >nul && set"
$environmentLines = & $env:ComSpec /d /c $environmentCommand
if ($LASTEXITCODE -ne 0) { throw "Visual Studio environment initialization failed: $vsRoot" }
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
if (-not $developerPath) { throw "Visual Studio did not provide a compiler PATH: $vsRoot" }
$env:PATH = $developerPath.Substring(5)

$bundledCMake = Join-Path $vsRoot 'Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe'
$bundledNinja = Join-Path $vsRoot 'Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe'
if ((Test-Path -LiteralPath $bundledCMake) -and (Test-Path -LiteralPath $bundledNinja)) {
    $cmake = $bundledCMake
    $env:PATH = "$(Split-Path -Parent $bundledNinja);$env:PATH"
} else {
    $cmakeCommand = Get-Command cmake.exe -ErrorAction SilentlyContinue
    $ninjaCommand = Get-Command ninja.exe -ErrorAction SilentlyContinue
    if (-not $cmakeCommand -or -not $ninjaCommand) {
        throw "The selected Visual Studio instance has no bundled CMake/Ninja and both were not found in PATH: $vsRoot"
    }
    $cmake = $cmakeCommand.Source
}

Write-Host "DEE_TOOLCHAIN_INSTANCE=$vsRoot"
Write-Host "DEE_CMAKE=$cmake"
$ctest = Join-Path (Split-Path -Parent $cmake) 'ctest.exe'
if (-not (Test-Path -LiteralPath $ctest)) { throw "ctest.exe was not found beside CMake: $ctest" }
Write-Host "DEE_CTEST=$ctest"
Write-Host "DEE_BUILD_DIRECTORY=$BuildDirectory"

$configureArguments = @(
    '-S', $projectRoot, '-B', $BuildDirectory, '-G', 'Ninja',
    "-DCMAKE_BUILD_TYPE=$Configuration",
    '-DDEE_THINKING_BUILD_TESTS=ON',
    '-DDEE_THINKING_BUILD_EXAMPLES=ON',
    '-DDEE_THINKING_BUILD_BENCHMARKS=ON'
)
if ($Configuration -eq 'Release') {
    # Pin the single-config Ninja cache instead of trusting a stale/default
    # value.  The provenance generator independently checks these exact flags.
    $configureArguments += '-DCMAKE_CXX_FLAGS_RELEASE=/O2 /Ob2 /DNDEBUG'
}
Invoke-DeeNative $cmake $configureArguments $buildLog
Invoke-DeeNative $cmake @('--build', $BuildDirectory, '--parallel') $buildLog
if (-not $SkipTests) {
    $ctestArguments = @('--test-dir', $BuildDirectory, '-C', $Configuration, '--output-on-failure')
    if ($captureReleaseEvidence) {
        $ctestArguments += @('--output-junit', $junitPath)
    }
    Invoke-DeeNative $ctest $ctestArguments $ctestLog
    if ($captureReleaseEvidence) {
        Add-DeeLogLine $ctestLog 'dee_ctest_expected_tests=15'
        Add-DeeLogLine $ctestLog 'dee_ctest_exit_code=0'
    }
}
Invoke-DeeNative $cmake @('--install', $BuildDirectory, '--config', $Configuration, '--prefix', $InstallPrefix) $buildLog
if (-not $SkipTests) {
    # Prove the generated package is relocatable before configuring the
    # consumer.  The lookup is pinned to the relocated config and package
    # registries are disabled, so another installation cannot mask a defect.
    $relocatedPrefix = Join-Path $projectRoot ("build\relocated-" + $Configuration.ToLowerInvariant() + "-$buildRunId")
    if (Test-Path -LiteralPath $relocatedPrefix) { throw "Unexpected pre-existing relocation prefix: $relocatedPrefix" }
    Copy-Item -LiteralPath $InstallPrefix -Destination $relocatedPrefix -Recurse
    Add-DeeLogLine $buildLog 'dee_install_relocation_copy=true'
    $packageConfigs = @(Get-ChildItem -LiteralPath $relocatedPrefix -Filter 'dee_thinkingConfig.cmake' -File -Recurse)
    if ($packageConfigs.Count -ne 1) {
        throw "Expected exactly one relocated dee_thinkingConfig.cmake; found $($packageConfigs.Count)"
    }
    $packageDirectory = $packageConfigs[0].Directory.FullName
    $consumerSource = Join-Path $projectRoot 'tests\installed_consumer'
    $consumerBuild = $ConsumerBuildDirectory
    Write-Host "DEE_INSTALLED_CONSUMER_BUILD=$consumerBuild"
    Invoke-DeeNative $cmake @(
        '-S', $consumerSource, '-B', $consumerBuild, '-G', 'Ninja',
        "-DCMAKE_BUILD_TYPE=$Configuration",
        "-Ddee_thinking_DIR=$packageDirectory",
        '-DCMAKE_FIND_USE_PACKAGE_REGISTRY=OFF',
        '-DCMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY=OFF'
    ) $buildLog
    Invoke-DeeNative $cmake @('--build', $consumerBuild, '--parallel') $buildLog
    Invoke-DeeNative (Join-Path $consumerBuild 'installed_consumer.exe') @() $buildLog
}

if ($captureReleaseEvidence) {
    Add-DeeLogLine $buildLog 'dee_build_pipeline_exit_code=0'
    $pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
    if (-not $pythonCommand) { throw 'python.exe is required to generate validation provenance.' }
    $generator = Join-Path $PSScriptRoot 'generate_validation_provenance.py'
    & $pythonCommand.Source -B $generator `
        --project-root $projectRoot `
        --build-root $BuildDirectory `
        --junit $junitPath `
        --ctest-log $ctestLog `
        --build-log $buildLog `
        --output-dir $validationDirectory
    if ($LASTEXITCODE -ne 0) { throw "Validation provenance generation failed with exit code $LASTEXITCODE" }
}
exit 0
