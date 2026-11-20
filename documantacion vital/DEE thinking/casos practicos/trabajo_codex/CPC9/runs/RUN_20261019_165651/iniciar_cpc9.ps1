param(
    [ValidateSet('interactivo','eventos','demo')][string]$Modo='interactivo',
    [string]$Eventos='',
    [string]$Salida='',
    [string]$Python='',
    [int]$Hasta=606,
    [switch]$ControlSinA,
    [switch]$Silencioso
)
$ErrorActionPreference='Stop'
$cpc9Root=$PSScriptRoot
if (-not $Python) {
    $Python=Join-Path $cpc9Root '.runtime_cpc9\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $Python)) {
        & py -3.13 (Join-Path $cpc9Root 'tools\preparar_entorno.py') --dest (Join-Path $cpc9Root '.runtime_cpc9')
        if ($LASTEXITCODE -ne 0) { throw 'No se pudo preparar el instrumento offline.' }
    }
}
if (-not $Salida) { $Salida=Join-Path $cpc9Root ('runs\demo_'+(Get-Date -Format 'yyyyMMdd_HHmmss_fff')) }
$cpc9Args=@('-I','-B',(Join-Path $cpc9Root 'ejecutar.py'),$Modo,'--out',$Salida)
if ($Modo -eq 'eventos') {
    if (-not $Eventos) { throw 'Modo eventos requiere -Eventos archivo.json' }
    $cpc9Args+=@('--events',$Eventos)
}
if ($Modo -eq 'demo') { $cpc9Args+=@('--until',$Hasta); if ($ControlSinA) { $cpc9Args+='--control-no-order-a' } }
if ($Silencioso) { $cpc9Args+='--quiet' }
& $Python @cpc9Args
if ($LASTEXITCODE -ne 0) { throw ('La ejecución terminó con código '+$LASTEXITCODE+'. Revise sus recibos y diario.') }
