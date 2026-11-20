$ErrorActionPreference='Stop'
$r07Root=Split-Path -Parent $PSScriptRoot
$receipt=Join-Path $PSScriptRoot 'APERTURA_MAIN_REFERENCIAS_R07_ROOT.json'
if(Test-Path -LiteralPath $receipt){throw 'Preserve lifecycle; no duplicate launch'}
$closed=Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'CIERRE_EDITOR_MAIN46_PARA_RAM_R07.json') | ConvertFrom-Json
if(-not $closed.closed){throw 'Previous own Main editor must be closed'}
$pilot=Get-Content -Raw -LiteralPath (Join-Path $r07Root 'evidencia\PILOTO_OTRO_MAPA_R06\RESULTADO_LIVE.json') | ConvertFrom-Json
if(-not $pilot.owner_closed -or $pilot.status -ne 'ONE_LIVE_EPISODE_CLOSED'){throw 'Pilot closed result required before sequential references'}
$file=Join-Path $r07Root 'mundo\DEE_RBX01_R07_NATIVE.rbxlx'
$expectedHash='724cb84eec14d9b6fa3b4d4eede22743f7030c1be4ad21ffb4f7d4b2acf33ab8'
if((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLower() -ne $expectedHash){throw 'Frozen map source mismatch'}
$exe='C:\Users\Erik\AppData\Local\Roblox\Versions\version-63eb6055af4e4688\RobloxStudioBeta.exe'
# Visible is explicitly necessary for the user-requested real comparison recording.
$p=Start-Process -FilePath $exe -ArgumentList ('"'+$file+'"') -PassThru -WindowStyle Normal
$value=[ordered]@{schema='DEE.R07.ReferenceOnlyStudio.Launch.R01';utc=[DateTime]::UtcNow.ToString('o');pid=$p.Id;creation_utc=$p.StartTime.ToUniversalTime().ToString('o');file=$file;source_sha256=$expectedHash;window_style='Normal, required for real requested video';purpose='Non-Native reference environment only; does not reopen final Native Main';Native_ticks=0;status='STARTED_NOT_YET_MCP_VERIFIED'}
$value | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $receipt -Encoding UTF8
$value | ConvertTo-Json -Depth 5
