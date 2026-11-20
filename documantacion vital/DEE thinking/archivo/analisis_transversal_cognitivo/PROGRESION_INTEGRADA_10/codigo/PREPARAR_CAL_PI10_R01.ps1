param(
 [Parameter(Mandatory=$true)][ValidateSet('CAL_PLUS','CAL_MINUS')][string]$Slug,
 [Parameter(Mandatory=$true)][string]$Prefijo,
 [Parameter(Mandatory=$true)][string]$ManifestSha256,
 [switch]$Importar
)
$ErrorActionPreference='Stop'
$pi10Helpers=$PSScriptRoot
$pi10Campaign=Split-Path -Parent $pi10Helpers
$pi10Root=Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $pi10Campaign))
$pi10Product=Join-Path $pi10Root 'DEE Cognitive 2.0'
$pi10Python=Join-Path $pi10Product 'motor\python313\python.exe'
$pi10Life='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_'+$Slug+'_01'
$pi10Force=if($Slug -eq 'CAL_PLUS'){'true'}else{'false'}
$pi10Manifest=Join-Path $Prefijo 'EXPORTACION_SERVICIO.json'
if((Get-FileHash -LiteralPath $pi10Manifest -Algorithm SHA256).Hash.ToLower() -ne $ManifestSha256.ToLower()){throw 'Actual common P0 manifest SHA differs'}
& $pi10Python -I -B -X utf8 (Join-Path $pi10Helpers 'preparar_scope_PI10_R01.py') --slug $Slug --vida $pi10Life --rol calibration --brazo real --force-query $pi10Force --prefijo $Prefijo --manifest-sha256 $ManifestSha256 --escribir
if($LASTEXITCODE -ne 0){throw 'Scope preparation failed; nothing retried'}
$pi10CloneArgs=@('--slug',$Slug,'--vida',$pi10Life,'--rol','calibration','--sistema-padre',(Join-Path $pi10Campaign 'estados\P0\sistema'),'--prefijo',$Prefijo,'--manifest-sha256',$ManifestSha256)
& $pi10Python -I -B -X utf8 (Join-Path $pi10Helpers 'preparar_clon_PI10_R01.py') @pi10CloneArgs --preparar --actor (Join-Path $pi10Helpers 'pi10_consulta_adaptativa_R01.py') --dependencia (Join-Path $pi10Helpers 'pi10_dos_trazas_legales_R01.py') --dependencia (Join-Path $pi10Helpers 'pi10_entorno_dos_puertas_R01.py') --dependencia (Join-Path $pi10Helpers 'PROTOCOLO_PI10_R01.json') --dependencia (Join-Path $pi10Helpers 'PI10_EXPERIMENTO_R01.json')
if($LASTEXITCODE -ne 0){throw 'Fresh code clone failed; preserve destination, no retry'}
& $pi10Python -I -B -X utf8 (Join-Path $pi10Helpers 'preparar_plan_calibracion_PI10_R01.py') --slug $Slug --prefijo $Prefijo --manifest-sha256 $ManifestSha256 --escribir
if($LASTEXITCODE -ne 0){throw 'Finite plan preparation failed'}
$pi10CodeManifest=Join-Path $pi10Campaign ('estados\'+$Slug+'\SISTEMA_CODIGO_PI10.json')
$pi10CodeSha=(Get-FileHash -LiteralPath $pi10CodeManifest -Algorithm SHA256).Hash.ToLower()
if($Importar){
 # Root only: official complete Native load0 in the owned512MiB importer.
 # No Owner, tick, episode, selection or promotion is started here.
 & $pi10Python -I -B -X utf8 (Join-Path $pi10Helpers 'preparar_clon_PI10_R01.py') @pi10CloneArgs --codigo-cerrado-sha256 $pi10CodeSha --importar
 if($LASTEXITCODE -ne 0){throw 'Import failed; preserve all evidence and exact IDs, never retry'}
}
$pi10Plan=Join-Path $pi10Helpers ('PLAN_PI10_'+$Slug+'_OWNER_R01.json')
Write-Output ([pscustomobject]@{Slug=$Slug;Life=$pi10Life;CodeManifestSha256=$pi10CodeSha;Plan=$pi10Plan;PlanSha256=(Get-FileHash -LiteralPath $pi10Plan -Algorithm SHA256).Hash.ToLower();NativeTicks=0;Imported=[bool]$Importar;OwnerStarted=$false}|ConvertTo-Json)
