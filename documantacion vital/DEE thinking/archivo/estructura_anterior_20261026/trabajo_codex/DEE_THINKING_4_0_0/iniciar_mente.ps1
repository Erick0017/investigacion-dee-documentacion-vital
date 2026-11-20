param(
    [ValidateSet('continuidad','comparacion','politica','informacion','relaciones','composicion','mundo_nativo')]
    [string]$Perfil = 'continuidad',
    [string]$Python = 'py',
    [string]$Eventos = '',
    [string]$Sesion = '',
    [string]$Cargar = '',
    [ValidateSet('principal','reservada')]
    [string]$Preparacion = 'principal'
)
$ErrorActionPreference = 'Stop'
if ($Perfil -eq 'mundo_nativo') {
    $appPath = Join-Path $PSScriptRoot 'app\mundo_nativo.py'
    $appArguments = @('-I','-B',$appPath,'--preparacion',$Preparacion)
} else {
    $appPath = Join-Path $PSScriptRoot 'app\conversar.py'
    $appArguments = @('-I','-B',$appPath,'--perfil',$Perfil)
}
if ($Eventos) { $appArguments += @('--eventos',$Eventos) }
if ($Sesion) { $appArguments += @('--sesion',$Sesion) }
if ($Cargar) { $appArguments += @('--cargar',$Cargar) }
if ($Python -eq 'py') { & py -3.13 @appArguments } else { & $Python @appArguments }
exit $LASTEXITCODE
