param([string]$Eventos = '', [string]$Transcripcion = '')
$ErrorActionPreference = 'Stop'
$cpc7Python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $cpc7Python)) {
    py -3.13 -m venv (Join-Path $PSScriptRoot '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Se requiere CPython 3.13 x64 estándar.' }
    & $cpc7Python -I -B -m pip install --no-index --no-deps (Join-Path $PSScriptRoot 'runtime\dee_thinking-4.0.0-cp313-cp313-win_amd64.whl')
    if ($LASTEXITCODE -ne 0) { throw 'La instalación local no fue completada.' }
}
$cpc7Arguments = @('-I','-B','-X','utf8',(Join-Path $PSScriptRoot 'app\console.py'))
if ($Eventos) { $cpc7Arguments += @('--events',$Eventos) }
if ($Transcripcion) { $cpc7Arguments += @('--transcript',$Transcripcion) }
& $cpc7Python @cpc7Arguments
exit $LASTEXITCODE
