param(
    [Parameter(Mandatory=$true)][string]$PythonExecutable,
    [Parameter(Mandatory=$true)][string]$Wheel,
    [Parameter(Mandatory=$true)][string]$VenvDirectory,
    [switch]$RunProtocolPanel,
    [switch]$RunRegressionPanel
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$WheelPath = (Resolve-Path -LiteralPath $Wheel).Path
$VenvPath = [System.IO.Path]::GetFullPath($VenvDirectory)
if (-not $VenvPath.StartsWith($ProjectRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "The validation venv must remain inside the DEE thinking 3.0.0 project root"
}

& $PythonExecutable -m venv --clear $VenvPath
if ($LASTEXITCODE -ne 0) { throw "venv creation failed" }
$VenvPython = Join-Path $VenvPath "Scripts\python.exe"
$env:PYTHONNOUSERSITE = "1"
& $VenvPython -I -m pip install --no-index --no-deps --force-reinstall $WheelPath
if ($LASTEXITCODE -ne 0) { throw "wheel installation failed" }

$OutsideSource = Join-Path $VenvPath "validation_work"
New-Item -ItemType Directory -Force -Path $OutsideSource | Out-Null
Push-Location $OutsideSource
try {
    & $VenvPython -I (Join-Path $ProjectRoot "tests\python\test_wheel_api.py")
    if ($LASTEXITCODE -ne 0) { throw "wheel API tests failed" }
    & $VenvPython -I (Join-Path $ProjectRoot "tests\python\test_basal_api.py")
    if ($LASTEXITCODE -ne 0) { throw "basal API tests failed" }
    if ($RunProtocolPanel) {
        & $VenvPython -I (Join-Path $ProjectRoot "tests\python\test_integrated_protocols.py")
        if ($LASTEXITCODE -ne 0) { throw "integrated protocol tests failed" }
    }
    if ($RunRegressionPanel) {
        & $VenvPython -I (Join-Path $ProjectRoot "tests\python\test_mbp4_regressions.py")
        if ($LASTEXITCODE -ne 0) { throw "MBP4 regression tests failed" }
    }
    & $VenvPython -I -c "import dee_thinking, pathlib; print(pathlib.Path(dee_thinking.__file__).resolve()); print(dee_thinking.build_info())"
    if ($LASTEXITCODE -ne 0) { throw "installed import provenance check failed" }
} finally {
    Pop-Location
}
