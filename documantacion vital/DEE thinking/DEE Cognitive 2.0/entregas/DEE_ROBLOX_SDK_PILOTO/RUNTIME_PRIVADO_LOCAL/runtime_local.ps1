param(
    [Parameter(Mandatory=$true)][ValidateSet('requisitos','estado','nuevo','importar','start','continue')][string]$Operacion,
    [string]$Instancia,
    [int]$Minutos=120,
    [int]$Ciclos=1,
    [string]$ContextoSHA256,
    [double]$DeadlineUtcEpoch,
    [switch]$CampanaValidacion,
    [switch]$Ejecutar
)
$ErrorActionPreference='Stop'
$SdkRuntime=[IO.Path]::GetFullPath($PSScriptRoot)
$SdkPython=Join-Path $SdkRuntime 'dependencias\producto\motor\python313\python.exe'
if(-not(Test-Path -LiteralPath $SdkPython -PathType Leaf)){throw 'Falta runtime privado oficial; ejecutar requisitos del expediente.'}
$SdkArgs=@('-I','-B')
switch($Operacion){
    'requisitos' {
        $SdkArgs+=@( (Join-Path $SdkRuntime 'backend\sdk_cli.py'),'requisitos')
        if($Instancia){$SdkArgs+=@('--instance',$Instancia)}
    }
    'estado' { $SdkArgs+=@((Join-Path $SdkRuntime 'backend\sdk_cli.py'),'estado','--instance',$Instancia) }
    'nuevo' {
        $SdkArgs+=@((Join-Path $SdkRuntime 'backend\preparacion\preparar_instancia_par28_sdk.py'))
        if($Instancia){$SdkArgs+=@('--instance-id',$Instancia)}
        if($Ejecutar){$SdkArgs+=@('--prepare','--execute-root-only')}
    }
    'importar' {
        if(-not$Ejecutar){throw 'Importar requiere -Ejecutar: carga administrativa oficial con cero ticks.'}
        $SdkArgs+=@((Join-Path $SdkRuntime 'backend\preparacion\importar_instancia_sdk.py'),'--instance',$Instancia,
            '--context-sha256',$ContextoSHA256,'--deadline-utc-epoch',[string]$DeadlineUtcEpoch,'--execute-root-only')
        if($CampanaValidacion){$SdkArgs+='--validation-campaign'}
    }
    default {
        $SdkArgs+=@((Join-Path $SdkRuntime 'backend\iniciar_sesion.py'),$Operacion,'--instance',$Instancia,
            '--minutes',[string]$Minutos,'--cycles',[string]$Ciclos)
        if($CampanaValidacion){$SdkArgs+='--validation-campaign'}
        if($Ejecutar){$SdkArgs+='--execute-real-native'}
    }
}
& $SdkPython @SdkArgs
exit $LASTEXITCODE
