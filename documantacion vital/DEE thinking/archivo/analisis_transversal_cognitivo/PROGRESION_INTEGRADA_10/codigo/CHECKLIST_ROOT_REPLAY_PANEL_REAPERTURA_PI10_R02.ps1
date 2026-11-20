param(
 [ValidateSet('Mostrar','Replay','Comparar','Permiso','PanelPreparar','PanelEjecutar','ReabrirPreparar','ReabrirEjecutar','CeroPreparar','CeroEjecutar','Ledger')][string]$Etapa='Mostrar',
 [string]$Comprobante
)
$ErrorActionPreference='Stop'
$H=$PSScriptRoot
$P=Split-Path -Parent $H
$Thinking=Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $P))
$C=Join-Path $Thinking 'DEE Cognitive 2.0'
$PY=Join-Path $C 'motor\python313\python.exe'
$RP=Join-Path $C 'reproducibilidad'
$Recipe='pi10_consulta12_familia_desde_P02_R02'
function RunPy([string]$Script,[string[]]$Arguments) {
 & $PY -I -B -X utf8 $Script @Arguments
 if ($LASTEXITCODE -ne 0) {throw "Stopped/preserved: $Script exit=$LASTEXITCODE. No automatic retry."}
}
function ExecutePlan([string]$Tag) {
 $plan=Join-Path $H ('PLAN_'+$Tag+'.json')
 if (-not(Test-Path -LiteralPath $plan)) {throw 'Generate and review the exact fresh plan first'}
 $hash=(Get-FileHash -Algorithm SHA256 -LiteralPath $plan).Hash.ToLowerInvariant()
 RunPy (Join-Path $H 'ejecutar_plan_PI10_R03.py') @('--plan',$plan,'--plan-sha256',$hash,'--ejecutar')
}
function NeedProof {
 if (-not $Comprobante) {throw 'Pass the actual last closed same-life --Comprobante; do not guess a future checkpoint'}
 if (-not(Test-Path -LiteralPath $Comprobante)) {throw 'Actual source closure proof missing'}
}
switch ($Etapa) {
 'Mostrar' {
  Write-Output 'ROOT ONLY, one material stage at a time. This default performs no Native operation.'
  Write-Output '1 Replay (requires completed RP install, Root reservation, no Root/RP writer)'
  Write-Output '2 Comparar (requires actual completed closed cold replay; do not accept RAW-only equality)'
  Write-Output '3 Permiso -Comprobante control/PI10_REAL2_B2_OWNER_R01.json (code-only delta)'
  Write-Output '4 PanelPreparar -Comprobante same B2, then inspect plan and PanelEjecutar'
  Write-Output '5 Inspect all12 scored witnesses/core10 and actual numeric binding. No reread/rescue.'
  Write-Output '6 ReabrirPreparar -Comprobante actual PANEL proof; inspect then ReabrirEjecutar (one new original offer)'
  Write-Output '7 Require the new actual function useful, then CeroPreparar -Comprobante actual REABRIR proof; inspect then CeroEjecutar'
  Write-Output '8 Root decision/adoption is a separate gated operation; no stage here promotes or edits ACTIVO.'
 }
 'Replay' {
  if ((Test-Path -LiteralPath (Join-Path $P 'PI10_ROOT_NATIVE_WRITER.lock')) -or (Test-Path -LiteralPath (Join-Path $RP 'EJECUCION_MATERIAL.lock'))) {throw 'Another writer is declared; no cold replay yet'}
  $registration=Get-Content -LiteralPath (Join-Path $P 'control\INCORPORACION_RP_ESTABLE_PI10_R02\INCORPORACION.json') -Raw | ConvertFrom-Json
  if (-not $registration.requirements_available) {throw 'Actual stable registration not completed'}
  RunPy (Join-Path $RP 'reproducir.py') @('reproducir',$Recipe,'--variante','real12','--vida','ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RPF2_20261111A','--destino',(Join-Path $P 'estados\RPF2'),'--material')
 }
 'Comparar' {RunPy (Join-Path $H 'comparar_reproduccion_PI10_R03.py') @('--fuente-par',(Join-Path $P 'pares\REAL2_12_T941139'),'--fuente-manifest-sha256','706627e093182f35efd2125e189a6527fcf4c27ba9d75dfdc21b2152a3411840','--destino-replay',(Join-Path $P 'estados\RPF2'),'--parser',(Join-Path $RP 'observador_pasivo.py'),'--salida',(Join-Path $P 'control\COMPARACION_REPRODUCCION_PI10_R03.json'))}
 'Permiso' {
  NeedProof
  $comparison=Get-Content -LiteralPath (Join-Path $P 'control\COMPARACION_REPRODUCCION_PI10_R03.json') -Raw | ConvertFrom-Json
  if (-not $comparison.overall) {throw 'Cold replay mismatch preserved; do not install public capability hooks'}
  RunPy (Join-Path $H 'aplicar_permiso_diagnostico_PI10_R02.py') @('--comprobante',$Comprobante,'--aplicar')
 }
 'PanelPreparar' {NeedProof; RunPy (Join-Path $H 'preparar_continuacion_cerrada_PI10_R02.py') @('--slug','REAL2','--fase','PANEL','--comprobante',$Comprobante,'--pasos',(Join-Path $H 'PANEL_HEREDADO_12_PI10_R03_PASOS.json'),'--escribir')}
 'PanelEjecutar' {ExecutePlan 'PI10_REAL2_PANEL_OWNER_R01'}
 'ReabrirPreparar' {NeedProof; RunPy (Join-Path $H 'preparar_continuacion_cerrada_PI10_R02.py') @('--slug','REAL2','--fase','REABRIR','--comprobante',$Comprobante,'--episodios','1','--escribir')}
 'ReabrirEjecutar' {ExecutePlan 'PI10_REAL2_REABRIR_OWNER_R01'}
 'CeroPreparar' {NeedProof; RunPy (Join-Path $H 'preparar_continuacion_cerrada_PI10_R02.py') @('--slug','REAL2','--fase','CERO','--comprobante',$Comprobante,'--pasos',(Join-Path $H 'ESTADO_CERO_PI10_R02_PASOS.json'),'--escribir')}
 'CeroEjecutar' {ExecutePlan 'PI10_REAL2_CERO_OWNER_R01'}
 'Ledger' {RunPy (Join-Path $H 'ledger_PI10_traslado_integral_R02.py') @()}
}
