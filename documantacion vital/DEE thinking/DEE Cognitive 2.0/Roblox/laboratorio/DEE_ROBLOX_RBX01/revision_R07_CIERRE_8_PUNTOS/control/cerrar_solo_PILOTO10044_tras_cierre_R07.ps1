$ErrorActionPreference='Stop'
$r07Root=Split-Path -Parent $PSScriptRoot
$proof=Join-Path $PSScriptRoot 'CIERRE_EDITOR_PILOTO10044_TRAS_NATIVE_R07.json'
if(Test-Path -LiteralPath $proof){throw 'Preserve lifecycle; no repeated editor closure'}
$closed=Get-Content -Raw -LiteralPath (Join-Path $r07Root 'evidencia\PILOTO_OTRO_MAPA_R06\RESULTADO_LIVE.json') | ConvertFrom-Json
if(-not $closed.owner_closed -or $closed.status -ne 'ONE_LIVE_EPISODE_CLOSED'){throw 'Actual completed Pilot and closed Native owner required'}
$worldPath=Join-Path $r07Root 'evidencia\PILOTO_OTRO_MAPA_R06\WORLD_MODULE_CHECKPOINT.json'
$worldHash=(Get-FileHash -LiteralPath $worldPath -Algorithm SHA256).Hash.ToLower()
$scenePath=Join-Path $r07Root 'mundo\PILOTO_R07.rbxlx'
$sceneHash='ef39c6bf193c2f26386384e564ffcb16ab2e93c29f7b8a9e071431781dbcfd92'
if((Get-FileHash -LiteralPath $scenePath -Algorithm SHA256).Hash.ToLower() -ne $sceneHash){throw 'Frozen pilot scene changed'}
$p=Get-Process -Id 10044
$start=[DateTime]::Parse('2026-11-17T08:06:35.8755562Z').ToUniversalTime()
if($p.ProcessName -ne 'RobloxStudioBeta' -or [Math]::Abs(($p.StartTime.ToUniversalTime()-$start).TotalMilliseconds) -gt 1){throw 'Not the exact own Pilot editor'}
$record=[ordered]@{schema='DEE.R07.CompletedPilot.EditorClose.R01';utc=[DateTime]::UtcNow.ToString('o');pid=10044;creation_utc=$p.StartTime.ToUniversalTime().ToString('o');Native_owner_closed=$true;final_native_tick=$closed.final_tick;session=$closed.session_id;scene_sha256=$sceneHash;World_sha256=$worldHash;working_set_before=$p.WorkingSet64;private_commit_before=$p.PrivateMemorySize64;graceful_requested=$false;forced=$false;closed=$false;other_processes_touched=$false;purpose='Sequential reference recording under unchanged free-RAM guard'}
$record.graceful_requested=$p.CloseMainWindow()
$null=$p.WaitForExit(10000)
if(-not $p.HasExited){Stop-Process -Id 10044; $record.forced=$true; $null=$p.WaitForExit(10000)}
$record.closed=$p.HasExited
$record.scene_sha256_after=(Get-FileHash -LiteralPath $scenePath -Algorithm SHA256).Hash.ToLower()
$record.World_sha256_after=(Get-FileHash -LiteralPath $worldPath -Algorithm SHA256).Hash.ToLower()
if($record.scene_sha256_after -ne $sceneHash -or $record.World_sha256_after -ne $worldHash){throw 'Preserved files changed'}
$record | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $proof -Encoding UTF8
$record | ConvertTo-Json -Depth 5
