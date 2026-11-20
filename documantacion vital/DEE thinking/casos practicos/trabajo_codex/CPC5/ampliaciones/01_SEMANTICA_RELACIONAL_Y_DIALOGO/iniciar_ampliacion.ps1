param([string]$Python313='python',[switch]$Interactivo,[ValidateSet('longitudinal','orden','dialogo','red3')][string]$Recorrido='longitudinal',[string]$Salida='')
$ErrorActionPreference='Stop'
$cpc5Base=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$cpc5Wheel=Join-Path $cpc5Base 'runtime\dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'
if ((Get-FileHash -LiteralPath $cpc5Wheel -Algorithm SHA256).Hash.ToLowerInvariant() -ne '17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623') { throw 'Identidad del wheel distinta' }
& $Python313 -I -c 'import sys; assert sys.version_info[:2]==(3,13) and sys.maxsize>2**32'
if ($LASTEXITCODE -ne 0) { throw 'Se requiere CPython3.13 x64' }
$cpc5Env=Join-Path $PSScriptRoot '.venv'
$cpc5Python=Join-Path $cpc5Env 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $cpc5Python)) {
    & $Python313 -I -m venv $cpc5Env
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear el entorno aislado' }
    & $cpc5Python -I -m pip install --no-index --no-deps $cpc5Wheel
    if ($LASTEXITCODE -ne 0) { throw 'Instalacion offline fallida' }
}
if (-not $Salida) { $Salida=Join-Path $PSScriptRoot ('sesiones\'+[DateTime]::Now.ToString('yyyyMMdd_HHmmss')) }
if (Test-Path -LiteralPath $Salida) { throw 'La salida existe; seleccione otra para conservarla' }
$cpc5Args=@('-I','-B',(Join-Path $PSScriptRoot 'ejecutar.py'),'demostracion','--salida',$Salida)
if (-not $Interactivo) { $cpc5Args+=@('--eventos',(Join-Path $PSScriptRoot ('configuraciones\demo_'+$Recorrido+'.json'))) }
& $cpc5Python @cpc5Args
exit $LASTEXITCODE
