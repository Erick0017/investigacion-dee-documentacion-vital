param([Parameter(Position=0,ValueFromRemainingArguments=$true)][string[]]$Comandos, [string]$PythonExecutable)
$ErrorActionPreference = 'Stop'
if (-not $PythonExecutable) {
    $localPython = Join-Path $PSScriptRoot '..\motor\python313\python.exe'
    if (-not (Test-Path -LiteralPath $localPython)) { $localPython = Join-Path $PSScriptRoot '.entorno\Scripts\python.exe' }
    if (Test-Path -LiteralPath $localPython) { $PythonExecutable = $localPython }
    else { throw 'Indique -PythonExecutable con CPython 3.13 x64 y DEE thinking 4.5 instalado; no se creará otra vida ni se usará otra versión silenciosamente.' }
}
if (-not $Comandos -or $Comandos.Count -eq 0) {
    $project = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot '..\PROYECTO.json') | ConvertFrom-Json
    $Comandos = @('estado','--vida',[string]$project.selected_life)
}
& $PythonExecutable -I -B -X utf8 (Join-Path $PSScriptRoot 'gestionar.py') @Comandos
if ($LASTEXITCODE -ne 0) { throw ('El gestor terminó con código ' + $LASTEXITCODE) }
