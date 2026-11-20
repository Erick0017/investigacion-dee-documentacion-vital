param(
    [string]$Python313,
    [switch]$Interactivo,
    [string]$Salida = 'sesion_CPC5_nueva'
)
$ErrorActionPreference = 'Stop'
$cpc5LocalPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$cpc5Wheel = Join-Path $PSScriptRoot 'runtime\dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'
$cpc5Expected = '17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623'
if ((Get-FileHash -LiteralPath $cpc5Wheel -Algorithm SHA256).Hash.ToLowerInvariant() -ne $cpc5Expected) {
    throw 'El wheel no corresponde al instrumento congelado.'
}
if (-not (Test-Path -LiteralPath $cpc5LocalPython)) {
    if (-not $Python313) {
        throw 'Indique -Python313 con la ruta de CPython3.13 x64 instalado; el paquete no incluye un interprete.'
    }
    & $Python313 -c "import sys; assert sys.version_info[:2]==(3,13) and sys.maxsize>2**32"
    if ($LASTEXITCODE -ne 0) { throw 'Se requiere CPython3.13 x64.' }
    & $Python313 -m venv (Join-Path $PSScriptRoot '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear el entorno local.' }
}
& $cpc5LocalPython -m pip install --no-index --no-deps $cpc5Wheel
if ($LASTEXITCODE -ne 0) { throw 'Fallo la instalacion offline del instrumento.' }
& $cpc5LocalPython -c "import sys,dee_thinking as d; assert sys.version_info[:2]==(3,13); assert d.__version__=='4.0.0'; assert d.kernel_identity()['kernel_version']==27; print(d.__file__)"
if ($LASTEXITCODE -ne 0) { throw 'Identidad importada incorrecta.' }
$cpc5Output = Join-Path $PSScriptRoot $Salida
if (Test-Path -LiteralPath $cpc5Output) { throw 'La salida ya existe. Indique otra con -Salida; las sesiones se conservan.' }
$cpc5Arguments = @((Join-Path $PSScriptRoot 'ejecutar.py'), 'demostracion', '--salida', $cpc5Output)
if (-not $Interactivo) {
    $cpc5Arguments += @('--eventos', (Join-Path $PSScriptRoot 'configuraciones\demo_integrado.json'))
}
& $cpc5LocalPython @cpc5Arguments
if ($LASTEXITCODE -ne 0) { throw 'La demostracion termino con errores; revise su DIALOGO.jsonl conservado.' }
