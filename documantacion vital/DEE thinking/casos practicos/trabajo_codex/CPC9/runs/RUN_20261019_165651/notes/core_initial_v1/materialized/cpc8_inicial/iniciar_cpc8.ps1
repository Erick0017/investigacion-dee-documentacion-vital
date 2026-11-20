param([ValidateSet('interactivo','eventos','verificar-datos')][string]$Modo='interactivo',[string]$Archivo,[string]$Python313)
$ErrorActionPreference='Stop'
$cpc8Root=$PSScriptRoot
$cpc8PathBytes=[Text.Encoding]::UTF8.GetBytes($cpc8Root)
$cpc8PathHash=[BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash($cpc8PathBytes)).Replace('-','').Substring(0,12)
$cpc8Env=Join-Path ([IO.Path]::GetTempPath()) ('DEE_CPC8_45_'+$cpc8PathHash)
$cpc8Python=Join-Path $cpc8Env 'Scripts\python.exe'
if(-not(Test-Path -LiteralPath $cpc8Python)) {
    $cpc8Base=if($Python313) {$Python313} else {(Get-Command python -ErrorAction Stop).Source}
    & $cpc8Base -I -c "import sys,struct;assert sys.version_info[:2]==(3,13) and struct.calcsize('P')==8,'Se requiere CPython3.13 x64'"
    if($LASTEXITCODE -ne 0) {throw 'Seleccione CPython3.13 x64 en PATH; no se instala otra versión automáticamente.'}
    & $cpc8Base -I -m venv $cpc8Env
    if($LASTEXITCODE -ne 0) {throw 'No se pudo crear el entorno aislado.'}
}
$cpc8Wheel=Join-Path $cpc8Root 'runtime\dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
if((Get-FileHash -LiteralPath $cpc8Wheel -Algorithm SHA256).Hash.ToLower() -ne '09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c') {throw 'Hash del instrumento distinto.'}
& $cpc8Python -I -m pip install --no-index --no-deps --force-reinstall $cpc8Wheel
if($LASTEXITCODE -ne 0) {throw 'La instalación offline falló.'}
& $cpc8Python -I -c "import hashlib,sys;from pathlib import Path;import dee_thinking as d;from dee_thinking import _native;assert d.__version__=='4.5.0';assert hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest()=='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d';print('Instrumento verificado:',d.__version__,_native.__file__)"
if($LASTEXITCODE -ne 0) {throw 'La importación no corresponde al instrumento oficial esperado.'}
if($Modo -eq 'eventos') {
    if(-not [IO.Path]::IsPathRooted($Archivo)) {$Archivo=Join-Path $cpc8Root $Archivo}
    & $cpc8Python -I -B (Join-Path $cpc8Root 'ejecutar.py') eventos $Archivo
}
else {& $cpc8Python -I -B (Join-Path $cpc8Root 'ejecutar.py') $Modo}
exit $LASTEXITCODE
