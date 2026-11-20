param()
$ErrorActionPreference='Stop'
$ProductRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$Current=Join-Path $ProductRoot 'Roblox/sdk/VERIFICAR.ps1'
if(-not(Test-Path -LiteralPath $Current -PathType Leaf)){throw 'Falta entrada canónica de verificación'}
& $Current
exit $LASTEXITCODE
