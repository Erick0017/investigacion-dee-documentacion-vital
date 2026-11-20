[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$CMake,
    [Parameter(Mandatory = $true)][string]$Ninja,
    [Parameter(Mandatory = $true)][string]$Cxx,
    [Parameter(Mandatory = $true)][string]$VsDevCmd,
    [Parameter(Mandatory = $true)][string]$InstallRoot,
    [Parameter(Mandatory = $true)][string]$SourceRoot,
    [Parameter(Mandatory = $true)][string]$BuildRoot
)

$ErrorActionPreference = 'Stop'
$environmentCommand = "call `"$VsDevCmd`" -no_logo -arch=x64 -host_arch=x64 >nul && set"
$environmentLines = & $env:ComSpec /d /c $environmentCommand
if ($LASTEXITCODE -ne 0) { throw 'Visual Studio environment initialization failed.' }
foreach ($line in $environmentLines) {
    $separator = $line.IndexOf('=')
    if ($separator -gt 0) {
        [Environment]::SetEnvironmentVariable(
            $line.Substring(0, $separator),
            $line.Substring($separator + 1),
            'Process'
        )
    }
}
$env:PATH = "$(Split-Path -Parent $Ninja);$env:PATH"

$packageDirectory = Join-Path $InstallRoot 'lib\cmake\dee_thinking'
$seed = Join-Path $InstallRoot 'share\dee_thinking\fixtures\mbp4\OBP_FRESH_VALIDATED_T32.deetsnap'
if (-not (Test-Path -LiteralPath $packageDirectory -PathType Container)) {
    throw "Missing installed CMake package: $packageDirectory"
}
if (-not (Test-Path -LiteralPath $seed -PathType Leaf)) {
    throw "Missing installed basal seed: $seed"
}
if (Test-Path -LiteralPath $BuildRoot) {
    throw "Consumer validation build root must be new: $BuildRoot"
}

$classicBuild = Join-Path $BuildRoot 'classic'
$basalBuild = Join-Path $BuildRoot 'basal'

& $CMake -S (Join-Path $SourceRoot 'tests\installed_consumer') -B $classicBuild -G Ninja `
    -DCMAKE_BUILD_TYPE=Release `
    "-DCMAKE_MAKE_PROGRAM=$Ninja" `
    "-DCMAKE_CXX_COMPILER=$Cxx" `
    "-Ddee_thinking_DIR=$packageDirectory" `
    -DCMAKE_FIND_USE_PACKAGE_REGISTRY=OFF `
    -DCMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY=OFF
if ($LASTEXITCODE -ne 0) { throw 'Classic consumer configure failed.' }
& $CMake --build $classicBuild --parallel
if ($LASTEXITCODE -ne 0) { throw 'Classic consumer build failed.' }
& (Join-Path $classicBuild 'installed_consumer.exe')
if ($LASTEXITCODE -ne 0) { throw 'Classic consumer execution failed.' }

& $CMake -S (Join-Path $SourceRoot 'tests\consumer_basal') -B $basalBuild -G Ninja `
    -DCMAKE_BUILD_TYPE=Release `
    "-DCMAKE_MAKE_PROGRAM=$Ninja" `
    "-DCMAKE_CXX_COMPILER=$Cxx" `
    "-Ddee_thinking_DIR=$packageDirectory" `
    -DCMAKE_FIND_USE_PACKAGE_REGISTRY=OFF `
    -DCMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY=OFF
if ($LASTEXITCODE -ne 0) { throw 'Basal consumer configure failed.' }
& $CMake --build $basalBuild --parallel
if ($LASTEXITCODE -ne 0) { throw 'Basal consumer build failed.' }
& (Join-Path $basalBuild 'dee_thinking_basal_consumer.exe') $seed (Join-Path $basalBuild 'roundtrip.deetsnap')
if ($LASTEXITCODE -ne 0) { throw 'Basal consumer execution failed.' }
