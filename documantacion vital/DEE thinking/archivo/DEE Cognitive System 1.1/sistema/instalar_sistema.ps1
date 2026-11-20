param([Parameter(Mandatory=$true)][string]$Python313)
$ErrorActionPreference = 'Stop'
& $Python313 -I -c "import sys,struct;assert sys.version_info[:2]==(3,13) and struct.calcsize('P')==8;print(sys.version)"
if ($LASTEXITCODE -ne 0) { throw 'Se requiere CPython 3.13 x64 real.' }
$entornoDcs = Join-Path $PSScriptRoot '.entorno'
if (Test-Path -LiteralPath $entornoDcs) { throw 'El entorno ya existe. No se sobrescribe: compruebe su identidad o use otro directorio de extracción.' }
& $Python313 -I -m venv $entornoDcs
if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear el entorno aislado.' }
$pythonDcs = Join-Path $entornoDcs 'Scripts\python.exe'
$wheelDcs = Join-Path $PSScriptRoot 'runtime\dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
$hashDcs = (Get-FileHash -Algorithm SHA256 -LiteralPath $wheelDcs).Hash.ToLowerInvariant()
if ($hashDcs -ne '09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c') { throw 'Identidad WHL incorrecta; no se instala otro motor.' }
& $pythonDcs -I -m pip install --no-index --no-deps $wheelDcs
if ($LASTEXITCODE -ne 0) { throw 'Falló la instalación local.' }
& $pythonDcs -I -B -X utf8 (Join-Path $PSScriptRoot 'gestionar.py') version
if ($LASTEXITCODE -ne 0) { throw 'La importación no cumple la identidad oficial.' }
Write-Output 'Instalación privada terminada. Iniciar_sistema.ps1 carga la vida activa; no crea una nueva.'
