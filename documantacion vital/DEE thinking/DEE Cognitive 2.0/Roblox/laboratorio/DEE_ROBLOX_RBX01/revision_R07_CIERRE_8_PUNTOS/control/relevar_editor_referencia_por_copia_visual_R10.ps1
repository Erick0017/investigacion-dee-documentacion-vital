$ErrorActionPreference='Stop'
$r07Root=Split-Path -Parent $PSScriptRoot
$proofPath=Join-Path $PSScriptRoot 'RELEVO_EDITOR_REFERENCIA_VISUAL_R10.json'
if(Test-Path -LiteralPath $proofPath){throw 'Lifecycle already used; reconcile only'}
$oldResult=Join-Path $r07Root 'evidencia\CONVENTIONAL_AI_R09_BLOQUE_01\RESULTADO.json'
$world=Join-Path $r07Root 'evidencia\CONVENTIONAL_AI_R09_BLOQUE_01\WORLD_CHECKPOINT.json'
$policy=Join-Path $r07Root 'comparadores\CONVENTIONAL_AI_R09_HISTORIA_01\POLICY_STATE_V3.json'
$result=Get-Content -Raw -LiteralPath $oldResult | ConvertFrom-Json
$state=Get-Content -Raw -LiteralPath $policy | ConvertFrom-Json
if(-not $result.owner_closed -or $result.global_completed -ne 29 -or $result.stop_reason -ne 'HOST_FREE_RAM_BELOW_1GiB'){throw 'Closed real29 pair required'}
if($null -ne $state.pending -or $state.session_id -ne 'R07_CONVENTIONAL_AI_R09_01'){throw 'Policy must be closed, same SID, no pending request'}
$worldHash=(Get-FileHash -LiteralPath $world -Algorithm SHA256).Hash.ToLower()
if($worldHash -ne '13d52b575e0015a158d13c29751945976a8a5d3eb028542763f5008670d4221e'){throw 'Actual saved World29 mismatch'}
$policyHash=(Get-FileHash -LiteralPath $policy -Algorithm SHA256).Hash.ToLower()
$source=Join-Path $r07Root 'mundo\DEE_RBX01_R07_NATIVE.rbxlx'
$dest=Join-Path $r07Root 'mundo\VISUAL_R10.rbxlx'
$sceneHash='724cb84eec14d9b6fa3b4d4eede22743f7030c1be4ad21ffb4f7d4b2acf33ab8'
if((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLower() -ne $sceneHash){throw 'Frozen scene bytes changed'}
if(Test-Path -LiteralPath $dest){throw 'Fresh scene filename required'}
$old=Get-Process -Id 6764
$expectedStart=[DateTime]::Parse('2026-11-17T09:00:59.6873566Z').ToUniversalTime()
if($old.ProcessName -ne 'RobloxStudioBeta' -or [Math]::Abs(($old.StartTime.ToUniversalTime()-$expectedStart).TotalMilliseconds) -gt 1){throw 'Own editor identity mismatch'}
$record=[ordered]@{schema='DEE.R07.ReferenceEditor.SafeVisualRelaunch.R10';utc=[DateTime]::UtcNow.ToString('o');old_pid=6764;old_creation=$old.StartTime.ToUniversalTime().ToString('o');old_working_set=$old.WorkingSet64;World29_sha256=$worldHash;policy_state_before_sha256=$policyHash;model_history_reset=$false;Native_ticks=0;other_editors_touched=$false;recovery_ignore_clicked=$false;recovery_files_deleted=$false;model_unload_exit=$null;old_editor_closed=$false;new_pid=$null}
# Administrative model unload only. The complete allowed transcript remains on disk.
$unloadArgs=@('-I','-B','-X','utf8','-c',"import os,subprocess,sys; e=os.environ.copy();e['OLLAMA_HOST']='127.0.0.1:11435';r=subprocess.run([r'C:\Users\Erik\AppData\Local\Programs\Ollama\ollama.exe','stop','llama3.2:latest'],env=e,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=45);sys.exit(r.returncode)")
& 'D:\Descargas\ANACONDA MINICONDA\python.exe' @unloadArgs
$record.model_unload_exit=$LASTEXITCODE
if($LASTEXITCODE -ne 0){throw 'Own model unload failed; preserve editor'}
# Force close avoids accepting or discarding the AutoRecovery prompt. All current
# experimental World/allowed model state is already saved. Recovery files remain.
Stop-Process -Id 6764 -Force
$null=$old.WaitForExit(10000)
$record.old_editor_closed=$old.HasExited
if(-not $record.old_editor_closed){throw 'Own editor still alive; no duplicate launch'}
Copy-Item -LiteralPath $source -Destination $dest
if((Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLower() -ne $sceneHash){throw 'Scene copy mismatch'}
$exe='C:\Users\Erik\AppData\Local\Roblox\Versions\version-63eb6055af4e4688\RobloxStudioBeta.exe'
$new=Start-Process -FilePath $exe -ArgumentList ('"'+$dest+'"') -PassThru -WindowStyle Normal
$record.new_pid=$new.Id
$record.new_creation_utc=$new.StartTime.ToUniversalTime().ToString('o')
$record.source=$source
$record.destination=$dest
$record.scene_sha256=$sceneHash
$record.policy_state_after_sha256=(Get-FileHash -LiteralPath $policy -Algorithm SHA256).Hash.ToLower()
$record.World29_after_sha256=(Get-FileHash -LiteralPath $world -Algorithm SHA256).Hash.ToLower()
if($record.policy_state_after_sha256 -ne $policyHash -or $record.World29_after_sha256 -ne $worldHash){throw 'Saved pair changed'}
$record.status='NEW_EDITOR_STARTED_NOT_YET_MCP_OR_CAPTURE_VERIFIED'
$record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $proofPath -Encoding UTF8
$record | ConvertTo-Json -Depth 8
