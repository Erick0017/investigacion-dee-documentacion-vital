param(
    [Parameter(Mandatory=$true)][string]$PythonExecutable,
    [string]$OutputDirectory = "dist"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Vswhere = Join-Path ${env:ProgramFiles(x86)} "Microsoft Visual Studio\Installer\vswhere.exe"
if (-not (Test-Path -LiteralPath $Vswhere)) {
    throw "vswhere.exe was not found; provide CMake and Ninja on PATH instead"
}
$VsRoot = (& $Vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.CMake.Project -property installationPath).Trim()
if (-not $VsRoot) { throw "No Visual Studio installation with CMake support was found" }

$VsDevCmd = Join-Path $VsRoot "Common7\Tools\VsDevCmd.bat"
if (-not (Test-Path -LiteralPath $VsDevCmd)) { throw "VsDevCmd.bat is missing" }
$EnvironmentDump = & $env:ComSpec /s /c "`"$VsDevCmd`" -arch=x64 -host_arch=x64 >nul && set"
if ($LASTEXITCODE -ne 0) { throw "VsDevCmd failed with exit code $LASTEXITCODE" }
$ImportedEnvironment = [System.Collections.Generic.Dictionary[string,string]]::new(
    [System.StringComparer]::OrdinalIgnoreCase)
foreach ($Line in $EnvironmentDump) {
    if ($Line -match '^([^=]+)=(.*)$') {
        # cmd.exe may expose both PATH and Path. Keep the first value emitted
        # by VsDevCmd so a stale inherited spelling cannot overwrite it.
        if (-not $ImportedEnvironment.ContainsKey($Matches[1])) {
            $ImportedEnvironment.Add($Matches[1], $Matches[2])
        }
    }
}
foreach ($Entry in $ImportedEnvironment.GetEnumerator()) {
    [Environment]::SetEnvironmentVariable($Entry.Key, $Entry.Value, 'Process')
}
$CompilerCommand = Get-Command cl.exe -ErrorAction SilentlyContinue
if (-not $CompilerCommand) {
    throw "VsDevCmd completed but cl.exe is not available on PATH"
}
$env:CXX = $CompilerCommand.Source
$env:CC = $CompilerCommand.Source

$env:CMAKE_EXECUTABLE = Join-Path $VsRoot "Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"
$env:CMAKE_MAKE_PROGRAM = Join-Path $VsRoot "Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe"
if (-not (Test-Path -LiteralPath $env:CMAKE_EXECUTABLE)) { throw "CMake executable is missing" }
if (-not (Test-Path -LiteralPath $env:CMAKE_MAKE_PROGRAM)) { throw "Ninja executable is missing" }
$env:DEE_THINKING_CMAKE_BUILD_ROOT = Join-Path $env:TEMP ("dt22-wheel-" + $PID)

$ResolvedOutput = Join-Path $ProjectRoot $OutputDirectory
New-Item -ItemType Directory -Force -Path $ResolvedOutput | Out-Null
Push-Location $ProjectRoot
try {
    & $PythonExecutable -m build --wheel --no-isolation --outdir $ResolvedOutput
    if ($LASTEXITCODE -ne 0) { throw "Wheel build failed with exit code $LASTEXITCODE" }
} finally {
    Pop-Location
}
