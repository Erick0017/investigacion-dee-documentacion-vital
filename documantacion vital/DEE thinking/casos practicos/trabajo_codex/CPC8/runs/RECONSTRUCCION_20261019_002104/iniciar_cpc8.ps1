param([switch]$Interactivo,[string]$Salida="",[ValidateSet('magnitud_social','contacto_social','integrada','basica')][string]$Perfil='magnitud_social')
$ErrorActionPreference = 'Stop'
$expRoot = $PSScriptRoot
$wheelPath = Join-Path $expRoot 'runtime\dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
$expectedHash = '09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
if ((Get-FileHash -LiteralPath $wheelPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedHash) { throw 'WHL diferente del instrumento oficial documentado.' }
$envRoot = Join-Path $expRoot '.entorno_cpc8'
$expPython = Join-Path $envRoot 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $expPython)) {
    Write-Host 'Creando entorno privado CPython3.13x64. No se cambia el Python del sistema.'
    & py -3.13 -m venv $envRoot
    if ($LASTEXITCODE -ne 0) { throw 'Se necesita CPython3.13x64. Consulte LEEME para usar otro ejecutable compatible.' }
    & $expPython -I -m pip install --no-index --no-deps $wheelPath
    if ($LASTEXITCODE -ne 0) { throw 'Falló la instalación local.' }
}
if (-not $Salida) { $Salida = Join-Path $expRoot ('sesion_visitante_' + [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss_fff')) }
$entryPath = Join-Path $expRoot 'ejecutar.py'
& $expPython -I -B -c "import hashlib,pathlib,struct,sys,dee_thinking as d; from dee_thinking import _native as n; assert sys.version_info[:2]==(3,13) and struct.calcsize('P')==8 and d.__version__=='4.5.0' and pathlib.Path(d.__file__).resolve().is_relative_to(pathlib.Path(sys.prefix).resolve()) and hashlib.sha256(pathlib.Path(n.__file__).read_bytes()).hexdigest()=='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d', 'Se necesita el instrumento oficial4.5.0 en CPython3.13x64'"
if ($LASTEXITCODE -ne 0) { throw 'El entorno local no corresponde al instrumento documentado; no se cambió el Python del sistema.' }
Write-Host "Perfil seleccionado: $Perfil. Por defecto se ejecuta la nueva vida magnitud_social; los eventos anteriores permanecen disponibles."
if ($Interactivo) {
    Write-Host "Para iniciar una instancia sin experiencias escriba: crear MI_E1 $Perfil"
    & $expPython -I -B $entryPath demo --interactivo --salida $Salida
}
else {
    $eventsByProfile = @{'magnitud_social'='demo_magnitud_social.jsonl';'contacto_social'='demo_contacto_social.jsonl';'integrada'='demo_integrada.jsonl';'basica'='demo_e1.jsonl'}
    & $expPython -I -B $entryPath demo --eventos (Join-Path $expRoot ('configuraciones\' + $eventsByProfile[$Perfil])) --salida $Salida
}
if ($LASTEXITCODE -ne 0) { throw 'La sesión terminó con un error explícito; conserve su telemetría.' }
