param()
$ErrorActionPreference='Stop'
$RobloxRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$Locator=Get-Content -LiteralPath (Join-Path $RobloxRoot 'LOCALIZADORES.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if($Locator.schema -ne 'DEE.Cognitive.Roblox.Organizacion.R01'){throw 'Localizador no reconocido'}
if($Locator.fallbackToProvisionBundle -ne $false){throw 'No se permite fallback al bundle largo'}
$Runtime=[IO.Path]::GetFullPath([string]$Locator.operationalRuntime)
$Python=Join-Path $Runtime 'dependencias/producto/motor/python313/python.exe'
$Public=Join-Path $RobloxRoot ([string]$Locator.canonical_sdk_relative)
$Verifier=Join-Path $Public 'herramientas/ensamblar_publico_R06.py'
if(-not(Test-Path -LiteralPath $Python -PathType Leaf)){throw 'Falta Python del runtime corto; no se abre Native'}
if(-not(Test-Path -LiteralPath $Verifier -PathType Leaf)){throw 'Falta verificador público'}
Write-Output 'Verificación de archivos y defaults públicos; sin Native, red, SQLite ni nuevos ticks.'
& $Python -I -S -B -X utf8 $Verifier verify --root $Public
exit $LASTEXITCODE
