$ErrorActionPreference = 'Stop'
$r07Root = Split-Path -Parent $PSScriptRoot
$evidencePath = Join-Path $PSScriptRoot 'CIERRE_EDITOR_MAIN46_PARA_RAM_R07.json'
if (Test-Path -LiteralPath $evidencePath) { throw 'Preserve existing lifecycle; do not repeat' }
$sourcePath = Join-Path $r07Root 'mundo\DEE_RBX01_R07_NATIVE.rbxlx'
$worldPath = Join-Path $r07Root 'evidencia\MAIN_REAPERTURA_35_46_R07\WORLD_CHECKPOINT.json'
$closurePath = Join-Path $r07Root 'evidencia\MAIN_REAPERTURA_35_46_R07\CONCILIACION_CIERRE_R07.json'
if ((Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash.ToLower() -ne '724cb84eec14d9b6fa3b4d4eede22743f7030c1be4ad21ffb4f7d4b2acf33ab8') { throw 'Frozen experimental source changed' }
if ((Get-FileHash -LiteralPath $worldPath -Algorithm SHA256).Hash.ToLower() -ne '1fa9d6e9207e0743b4459c1382142c1d5bc2dad5868183fde1363ff20f0ed6c8') { throw 'Saved Main46 World changed/missing' }
if ((Get-FileHash -LiteralPath $closurePath -Algorithm SHA256).Hash.ToLower() -ne 'becd84d077c4fb01023593dbea9220fa0e5f2ebfcde8942aab63dd6b66f21a45') { throw 'Closed/drained Native proof changed/missing' }
$owned = Get-Process -Id 15872
$expectedStart = [DateTime]::Parse('2026-11-16T16:10:10.6996053Z').ToUniversalTime()
if ($owned.ProcessName -ne 'RobloxStudioBeta' -or [Math]::Abs(($owned.StartTime.ToUniversalTime()-$expectedStart).TotalMilliseconds) -gt 1) { throw 'PID/name/creation do not identify own Main editor' }
$expectedTitle = $sourcePath + ' - Roblox Studio'
if ($owned.MainWindowTitle -ne $expectedTitle) { throw 'Exact own Main title required' }
$record = [ordered]@{schema='DEE.R07.OwnSavedMainEditor.Close.R01';utc=[DateTime]::UtcNow.ToString('o');pid=15872;creation_utc=$owned.StartTime.ToUniversalTime().ToString('o');title=$owned.MainWindowTitle;working_set_before=$owned.WorkingSet64;private_commit_before=$owned.PrivateMemorySize64;native_owner_already_closed=$true;world46_hash_verified=$true;frozen_editor_file_hash_verified=$true;other_processes_touched=$false;reason='Release own completed editor caches for unchanged prospective RAM guard';graceful_requested=$false;forced=$false;closed=$false}
$record.graceful_requested = $owned.CloseMainWindow()
try { $null=$owned.WaitForExit(15000) } catch { }
$owned.Refresh()
if (-not $owned.HasExited) {
    # Only the fully identified, completed, saved experimental Main editor.
    # No Edit-model source mutations occurred during the runtime-only experiment.
    Stop-Process -Id 15872
    $record.forced=$true
    $null=$owned.WaitForExit(10000)
}
$record.closed=$owned.HasExited
$record.source_file_hash_after=(Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash.ToLower()
$record.world_file_hash_after=(Get-FileHash -LiteralPath $worldPath -Algorithm SHA256).Hash.ToLower()
$record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $evidencePath -Encoding UTF8
$record | ConvertTo-Json -Depth 8
if (-not $record.closed) { throw 'Own editor did not close; do not touch other processes' }
