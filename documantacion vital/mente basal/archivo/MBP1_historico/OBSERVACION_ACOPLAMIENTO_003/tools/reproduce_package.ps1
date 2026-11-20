param(
    [string]$Python = 'D:\Descargas\ANACONDA MINICONDA\python.exe'
)

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
if (-not (Test-Path -LiteralPath $Python)) {
    throw 'Se requiere CPython 3.13 x64; use -Python con su ruta.'
}

$env:PYTHONPATH = Join-Path $Root 'baseline\python_site'
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
$Output = Join-Path $Root 'validation_reproduction'
New-Item -ItemType Directory -Force -Path $Output | Out-Null

& $Python -B (Join-Path $Root 'tools\passive_mobile_observer.py') `
    --root $Root `
    --checkpoint (Join-Path $Root 'world\checkpoints\tick_000000214872_collect_OBS_003_FINAL_3babbbcd.deetsnap') `
    --output (Join-Path $Output 'passive_observer_final.json') `
    --validate-passivity
if ($LASTEXITCODE -ne 0) { throw 'Falló la validación pasiva' }

& $Python -B (Join-Path $Root 'tools\replay_residue_window_003.py') `
    --root $Root `
    --checkpoint (Join-Path $Root 'world\checkpoints\tick_000000193536_collect_OBS_003_REF_e1c00e61.deetsnap') `
    --to 193560 `
    --backend lazy `
    --output (Join-Path $Output 'cadence_replay_lazy.json')
if ($LASTEXITCODE -ne 0) { throw 'Falló el replay Lazy' }

$Replay = Get-Content -LiteralPath (Join-Path $Output 'cadence_replay_lazy.json') -Raw | ConvertFrom-Json
if ($Replay.events.Count -lt 1 -or $Replay.events[0].tick -ne 193559) {
    throw 'El replay no reprodujo el evento esperado de T193559'
}
[pscustomobject]@{
    reproduced = $true
    passive_observer = $true
    first_cadence_event = $Replay.events[0].tick
    live_world_accessed = $false
} | ConvertTo-Json

