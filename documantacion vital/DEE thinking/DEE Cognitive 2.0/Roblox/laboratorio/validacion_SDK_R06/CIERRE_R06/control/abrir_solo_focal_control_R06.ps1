param([switch]$NativeReadyConfirmed,[switch]$PreviousFocalClosedConfirmed)
$ErrorActionPreference='Stop'
if(-not $NativeReadyConfirmed -or -not $PreviousFocalClosedConfirmed){throw 'Root must confirm the serial Native boundaries first'}
$Workspace='D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests'
$Scene=Join-Path $Workspace '_sdk_r06_valid_20261118\DEE_FOCAL_CONTROL_R06_01.rbxlx'
$Exe='C:\Users\Erik\AppData\Local\Roblox\Versions\version-63eb6055af4e4688\RobloxStudioBeta.exe'
$Record=Join-Path (Split-Path -Parent $PSScriptRoot) 'APERTURA_FOCAL_CONTROL_01.json'
if(Test-Path -LiteralPath $Record){throw 'Existing launch record: reconcile; never launch twice'}
$ResolvedScene=(Resolve-Path -LiteralPath $Scene).Path
if(-not $ResolvedScene.StartsWith($Workspace+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Unexpected scene location'}
if((Get-Item -LiteralPath $ResolvedScene).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Linked scene rejected'}
if((Get-FileHash -LiteralPath $ResolvedScene -Algorithm SHA256).Hash.ToLowerInvariant() -ne '0729b993e4312579e86756707ff574e760d9c36107d5d9c04fd463537e08f664'){throw 'Private control scene changed'}
if(-not(Test-Path -LiteralPath $Exe -PathType Leaf)){throw 'Known Studio executable missing'}
$Launch=[ordered]@{status='STARTING';scene=$ResolvedScene;exe=$Exe;utc=[DateTime]::UtcNow.ToString('o');purpose='Only the six-opportunity nonconsuming paired control'}
$Launch|ConvertTo-Json|Set-Content -LiteralPath $Record -Encoding utf8
$Studio=Start-Process -FilePath $Exe -ArgumentList @('-task','EditFile','-localPlaceFile',('"'+$ResolvedScene+'"')) -WindowStyle Hidden -PassThru
$Launch.status='OPENED'
$Launch['pid']=$Studio.Id
$Launch['startUtc']=$Studio.StartTime.ToUniversalTime().ToString('o')
$Launch|ConvertTo-Json|Set-Content -LiteralPath $Record -Encoding utf8
$Launch|ConvertTo-Json
