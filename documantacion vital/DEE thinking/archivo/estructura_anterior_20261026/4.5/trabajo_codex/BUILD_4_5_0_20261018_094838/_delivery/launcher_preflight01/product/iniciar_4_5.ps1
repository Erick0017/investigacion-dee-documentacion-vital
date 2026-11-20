param(
    [string]$PythonExecutable = 'python',
    [string]$Events = '',
    [string]$Transcript = ''
)
$ErrorActionPreference = 'Stop'
$product45Root = [IO.Path]::GetFullPath($PSScriptRoot)
$wheel45Name = 'dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
$wheel45Path = Join-Path $product45Root ('wheel\' + $wheel45Name)
$env45Path = Join-Path $product45Root '.mente45_env'
$marker45Path = Join-Path $env45Path 'DEE_THINKING_45_ENV.json'
if (-not (Test-Path -LiteralPath $wheel45Path -PathType Leaf)) { throw 'No se encuentra el WHL 4.5 del paquete.' }
$base45Check = 'import json,struct,sys,sysconfig; assert sys.implementation.name=="cpython" and sys.version_info[:2]==(3,13) and struct.calcsize("P")==8 and not sysconfig.get_config_var("Py_GIL_DISABLED"), "Se requiere CPython 3.13 x64 estandar (con GIL)"; print(json.dumps({"python":sys.executable,"version":sys.version,"bits":64,"standard_gil":True}))'
# Base64 avoids native argument quoting differences between Windows PowerShell
# 5.1 and PowerShell 7; it is transparent source transport, not executable data
# from an experiment or evaluator.
$base45Encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($base45Check))
$base45Command = "import base64;exec(base64.b64decode('$base45Encoded'))"
& $PythonExecutable -I -B -c $base45Command
if ($LASTEXITCODE -ne 0) { throw 'El interprete elegido no es CPython 3.13 x64 estandar.' }
$wheel45Hash = (Get-FileHash -LiteralPath $wheel45Path -Algorithm SHA256).Hash.ToLowerInvariant()
$manifest45Path = Join-Path $product45Root 'MANIFEST.json'
if (Test-Path -LiteralPath $manifest45Path -PathType Leaf) {
    $manifest45 = Get-Content -LiteralPath $manifest45Path -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($manifest45.schema -ne 'DEE45.manifest.v1' -or $manifest45.archive_root -ne 'DEE_thinking_4_5_0') { throw 'El manifiesto no corresponde al paquete 4.5.' }
    $wheel45Rows = @($manifest45.files | Where-Object { $_.path -ceq ('wheel/' + $wheel45Name) })
    if ($wheel45Rows.Count -ne 1 -or $wheel45Rows[0].sha256 -ine $wheel45Hash -or [int64]$wheel45Rows[0].bytes -ne (Get-Item -LiteralPath $wheel45Path).Length) {
        throw 'El hash o el tamano del WHL no coincide con MANIFEST.json.'
    }
} else {
    throw 'Falta MANIFEST.json. Use el paquete verificado completo, no una copia aislada del lanzador.'
}
if (Test-Path -LiteralPath $env45Path) {
    if (-not (Test-Path -LiteralPath $marker45Path -PathType Leaf)) { throw 'La carpeta .mente45_env ya existe sin marcador propio; se conserva sin modificar.' }
    $marker45 = Get-Content -LiteralPath $marker45Path -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($marker45.schema -ne 'DEE45.local-environment.v1' -or $marker45.wheel_sha256 -ine $wheel45Hash) {
        throw 'El entorno existente pertenece a otro corte; se conserva sin modificar. Extraiga este paquete en otra carpeta.'
    }
} else {
    & $PythonExecutable -I -B -m venv $env45Path
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear el entorno local de este paquete.' }
    $marker45 = [ordered]@{schema='DEE45.local-environment.v1'; version='4.5.0'; wheel_sha256=$wheel45Hash; source='wheel incluido, instalacion offline no editable'}
    [IO.File]::WriteAllText($marker45Path, ($marker45 | ConvertTo-Json), [Text.UTF8Encoding]::new($false))
}
$env45Python = Join-Path $env45Path 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $env45Python -PathType Leaf)) { throw 'El entorno propio no tiene interprete; no se modifican otros entornos.' }
& $env45Python -I -B -c $base45Command
if ($LASTEXITCODE -ne 0) { throw 'El entorno local no cumple CPython 3.13 x64 estandar.' }
& $env45Python -I -B -m pip install --no-index --no-deps --disable-pip-version-check $wheel45Path
if ($LASTEXITCODE -ne 0) { throw 'Fallo la instalacion offline del WHL incluido.' }
$identity45Path = Join-Path $product45Root 'RELEASE_IDENTITY.json'
if (-not (Test-Path -LiteralPath $identity45Path -PathType Leaf)) { throw 'Falta RELEASE_IDENTITY.json del paquete.' }
$identity45 = Get-Content -LiteralPath $identity45Path -Raw -Encoding UTF8 | ConvertFrom-Json
$import45Check = 'import hashlib,pathlib,sys; import dee_thinking as d; assert d.__version__=="4.5.0" and d.kernel_identity()["kernel_version"]==27; site=pathlib.Path(sys.prefix).resolve()/"Lib"/"site-packages"; native=pathlib.Path(d._native.__file__).resolve(); assert pathlib.Path(d.__file__).resolve().is_relative_to(site) and native.is_relative_to(site); assert hashlib.sha256(native.read_bytes()).hexdigest()==sys.argv[1]; print("DEE thinking 4.5.0 / kernel v27 / site-packages verificado")'
$import45Encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($import45Check))
$import45Command = "import base64;exec(base64.b64decode('$import45Encoded'))"
& $env45Python -I -B -c $import45Command $identity45.native_sha256
if ($LASTEXITCODE -ne 0) { throw 'La identidad del modulo instalado no coincide con este paquete.' }
$dialogue45Args = @('-I', '-B', '-m', 'dee_thinking.consolidated_dialogue')
if ($Events) {
    $events45Path = if ([IO.Path]::IsPathRooted($Events)) { [IO.Path]::GetFullPath($Events) } else { [IO.Path]::GetFullPath((Join-Path $product45Root $Events)) }
    if (-not (Test-Path -LiteralPath $events45Path -PathType Leaf)) { throw 'No existe el archivo de eventos solicitado.' }
    $dialogue45Args += @('--events', $events45Path, '--strict')
}
if ($Transcript) {
    $transcript45Path = if ([IO.Path]::IsPathRooted($Transcript)) { [IO.Path]::GetFullPath($Transcript) } else { [IO.Path]::GetFullPath((Join-Path $product45Root $Transcript)) }
    $dialogue45Args += @('--transcript', $transcript45Path)
}
Write-Host 'Interfaz estructurada en espanol. Escriba ayuda para consultar la gramatica real.'
Push-Location -LiteralPath $product45Root
try {
    & $env45Python @dialogue45Args
    if ($LASTEXITCODE -ne 0) { throw 'La sesion termino con error; conserve su transcripcion y recibos.' }
} finally { Pop-Location }
