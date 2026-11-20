$ErrorActionPreference='Stop'
$resultPath=Join-Path $PSScriptRoot 'APERTURA_PILOTO_R06_ROOT.json'
if(Test-Path -LiteralPath $resultPath){throw 'Existing opening receipt: reconcile instead of launching twice.'}
$scene=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\mundo\PILOTO_R07.rbxlx'))
$exe='C:\Users\Erik\AppData\Local\Roblox\Versions\version-63eb6055af4e4688\RobloxStudioBeta.exe'
if(-not(Test-Path -LiteralPath $exe)){throw 'Existing Studio binary unavailable; no reinstall.'}
$sceneHash=(Get-FileHash -LiteralPath $scene -Algorithm SHA256).Hash.ToLowerInvariant()
if($sceneHash -ne 'ef39c6bf193c2f26386384e564ffcb16ab2e93c29f7b8a9e071431781dbcfd92'){throw 'Prepared pilot scene changed.'}
$record=[ordered]@{utc=[DateTime]::UtcNow.ToString('o');scene=$scene;scene_sha256=$sceneHash;exe=$exe;action='OPEN_ONLY_OWN_PREPARED_PILOT';Native_requests=0;published=$false;status='INTENT'}
$record | ConvertTo-Json | Set-Content -LiteralPath $resultPath -Encoding utf8
$child=Start-Process -FilePath $exe -ArgumentList ('"'+$scene+'"') -WindowStyle Hidden -PassThru
$record.status='STARTED_NOT_YET_MCP_VERIFIED'
$record.process_id=$child.Id
$record.creation_utc=$child.StartTime.ToUniversalTime().ToString('o')
$record | ConvertTo-Json | Set-Content -LiteralPath $resultPath -Encoding utf8
$record | ConvertTo-Json
