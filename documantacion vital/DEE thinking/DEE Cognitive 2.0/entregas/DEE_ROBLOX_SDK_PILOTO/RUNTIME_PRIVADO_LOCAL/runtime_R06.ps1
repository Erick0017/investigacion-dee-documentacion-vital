param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('requisitos','estado','crear-ledger-nuevo','start','continue')]
    [string]$Command,
    [string]$Instance,
    [ValidateRange(45,360)][int]$Minutes=180,
    [ValidateRange(1,3)][int]$Cycles=1,
    [switch]$ExecuteRealNative
)
$ErrorActionPreference='Stop'
$taskRuntime= $PSScriptRoot
$taskPython=Join-Path $taskRuntime 'dependencias\producto\motor\python313\python.exe'
if($Command -in @('start','continue')){
    if(-not $Instance){throw 'Explicit SDK diagnostic instance required'}
    $taskScript=Join-Path $taskRuntime 'backend\r06\iniciar_sesion.py'
    $taskArgs=@('-I','-B',$taskScript,$Command,'--instance',$Instance,'--minutes',"$Minutes",'--cycles',"$Cycles",'--validation-campaign')
    if($ExecuteRealNative){$taskArgs+='--execute-real-native'}
}else{
    $taskScript=Join-Path $taskRuntime 'backend\r06\sdk_cli.py'
    $taskArgs=@('-I','-B',$taskScript,$Command)
    if($Instance){$taskArgs+=@('--instance',$Instance)}
}
& $taskPython @taskArgs
exit $LASTEXITCODE
