param([switch]$Demo,[int]$Semilla=1)
$ErrorActionPreference='Stop'
$Cpc6Root=$PSScriptRoot
$Cpc6Python=Join-Path $Cpc6Root '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Cpc6Python)) {
    & py -3.13 -m venv (Join-Path $Cpc6Root '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Se requiere CPython 3.13 x64 estándar.' }
    & $Cpc6Python -m pip install --no-index (Join-Path $Cpc6Root 'runtime\dee_thinking-4.0.0-cp313-cp313-win_amd64.whl')
    if ($LASTEXITCODE -ne 0) { throw 'La instalación local del WHL no terminó.' }
}
if ($Demo) { & $Cpc6Python (Join-Path $Cpc6Root 'app.py') --demo --seed $Semilla }
else { & $Cpc6Python (Join-Path $Cpc6Root 'app.py') }
exit $LASTEXITCODE
