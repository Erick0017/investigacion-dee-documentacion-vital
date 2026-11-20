param(
    [Parameter(Mandatory=$true)][string]$PythonExecutable,
    [Parameter(Mandatory=$true)][string]$Wheel,
    [Parameter(Mandatory=$true)][string]$VenvDirectory,
    [switch]$RunProtocolPanel
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$WheelPath = (Resolve-Path -LiteralPath $Wheel).Path
$VenvPath = [System.IO.Path]::GetFullPath($VenvDirectory)
if (-not $VenvPath.StartsWith($ProjectRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "The validation venv must remain inside ENTREGA_02_DEFINITIVA"
}

& $PythonExecutable -m venv --clear $VenvPath
if ($LASTEXITCODE -ne 0) { throw "venv creation failed" }
$VenvPython = Join-Path $VenvPath "Scripts\python.exe"
$env:PYTHONNOUSERSITE = "1"
& $VenvPython -m pip install --no-deps --force-reinstall $WheelPath
if ($LASTEXITCODE -ne 0) { throw "wheel installation failed" }

$OutsideSource = Join-Path $VenvPath "validation_work"
New-Item -ItemType Directory -Force -Path $OutsideSource | Out-Null
Push-Location $OutsideSource
try {
    & $VenvPython (Join-Path $ProjectRoot "tests\python\test_wheel_api.py")
    if ($LASTEXITCODE -ne 0) { throw "wheel API tests failed" }
    if ($RunProtocolPanel) {
        & $VenvPython (Join-Path $ProjectRoot "tests\python\test_integrated_protocols.py")
        if ($LASTEXITCODE -ne 0) { throw "integrated protocol tests failed" }
    }
    & $VenvPython -c "import dee_thinking, pathlib; print(pathlib.Path(dee_thinking.__file__).resolve()); print(dee_thinking.build_info())"
    if ($LASTEXITCODE -ne 0) { throw "installed import provenance check failed" }
} finally {
    Pop-Location
}

