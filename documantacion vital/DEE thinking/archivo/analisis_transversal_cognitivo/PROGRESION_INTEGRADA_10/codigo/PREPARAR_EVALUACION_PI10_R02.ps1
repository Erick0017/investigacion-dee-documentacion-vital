param(
 [Parameter(Mandatory=$true)][string]$Slug,
 [string]$Fase='F0',
 [Parameter(Mandatory=$true)][string]$Prefijo,
 [Parameter(Mandatory=$true)][string]$ManifestSha256,
 [Parameter(Mandatory=$true)][string]$SistemaPadre,
 [string]$CodigoPadre,
 [Parameter(Mandatory=$true)][int]$Episodios,
 [ValidateSet('real','nonfailure','yoked')][string]$Brazo='real',
 [ValidateSet('none','cut','sham')][string]$Traza='none',
 [string]$YokeSource,
 [string]$YokeManifestSha256,
 [switch]$Importar
)
$ErrorActionPreference='Stop'
$pi10Helpers=$PSScriptRoot
$pi10Campaign=Split-Path -Parent $pi10Helpers
$pi10Root=Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $pi10Campaign))
$pi10Python=Join-Path $pi10Root 'DEE Cognitive 2.0\motor\python313\python.exe'
$pi10Life='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_'+$Slug+'_01'
$pi10Role=if($Brazo -eq 'nonfailure'){'none'}elseif($Brazo -eq 'yoked'){'yoked'}else{'real'}
$pi10ScopeArgs=@('--slug',$Slug,'--fase',$Fase,'--vida',$pi10Life,'--brazo',$Brazo,'--traza',$Traza,'--prefijo',$Prefijo,'--manifest-sha256',$ManifestSha256,'--episodios',[string]$Episodios,'--escribir')
if($YokeSource){$pi10ScopeArgs+=@('--yoke-source',$YokeSource,'--yoke-manifest-sha256',$YokeManifestSha256)}
& $pi10Python -I -B -X utf8 (Join-Path $pi10Helpers 'preparar_evaluacion_PI10_R02.py') @pi10ScopeArgs
if($LASTEXITCODE -ne 0){throw 'Prospective scope/plan failed; no clone imported'}
$pi10CloneArgs=@('--slug',$Slug,'--vida',$pi10Life,'--rol',$pi10Role,'--sistema-padre',$SistemaPadre,'--prefijo',$Prefijo,'--manifest-sha256',$ManifestSha256)
if($CodigoPadre){$pi10CloneArgs+=@('--codigo-padre',$CodigoPadre)}
& $pi10Python -I -B -X utf8 (Join-Path $pi10Helpers 'preparar_clon_PI10_R02.py') @pi10CloneArgs --preparar --actor (Join-Path $pi10Helpers 'pi10_consulta_adaptativa_R02.py') --dependencia (Join-Path $pi10Helpers 'pi10_dos_trazas_legales_R01.py') --dependencia (Join-Path $pi10Helpers 'pi10_entorno_dos_puertas_R01.py') --dependencia (Join-Path $pi10Helpers 'PROTOCOLO_PI10_R02.json') --dependencia (Join-Path $pi10Helpers 'PI10_EXPERIMENTO_R02.json')
if($LASTEXITCODE -ne 0){throw 'Fresh exact code preparation failed; preserve partial destination'}
$pi10CodeManifest=Join-Path $pi10Campaign ('estados\'+$Slug+'\SISTEMA_CODIGO_PI10.json')
$pi10CodeSha=(Get-FileHash -LiteralPath $pi10CodeManifest -Algorithm SHA256).Hash.ToLower()
if($Importar){
 & $pi10Python -I -B -X utf8 (Join-Path $pi10Helpers 'preparar_clon_PI10_R02.py') @pi10CloneArgs --codigo-cerrado-sha256 $pi10CodeSha --importar
 if($LASTEXITCODE -ne 0){throw 'Root import0 failed; preserve state, no retry'}
}
$pi10Plan=Join-Path $pi10Helpers ('PLAN_PI10_'+$Slug+'_'+$Fase+'_OWNER_R01.json')
Write-Output ([pscustomobject]@{Life=$pi10Life;Plan=$pi10Plan;PlanSha256=(Get-FileHash -LiteralPath $pi10Plan -Algorithm SHA256).Hash.ToLower();CodeManifestSha256=$pi10CodeSha;Imported=[bool]$Importar;OwnerStarted=$false;NewNativeTicks=0}|ConvertTo-Json)
