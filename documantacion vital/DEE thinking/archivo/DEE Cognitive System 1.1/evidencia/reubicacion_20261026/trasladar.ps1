param([switch]$Ejecutar)
$ErrorActionPreference = 'Stop'
$raiz = 'D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking'
$registro = $PSScriptRoot
$archivo = Join-Path $raiz 'archivo\estructura_anterior_20261026'
$original = Join-Path $raiz 'casos practicos\trabajo_codex\DEE Cognitive System 1.1'
$principal = Join-Path $raiz 'DEE Cognitive System 1.1'
$mapa = @([ordered]@{origen=$original; destino=$principal; motivo='Fuente operativa completa, conservada como principal'})
foreach($nombre in @('2.2.0','3.0','3.5','4.0','casos practicos','trabajo_codex')) {
  $mapa += [ordered]@{origen=(Join-Path $raiz $nombre); destino=(Join-Path $archivo $nombre); motivo='Antecedente conservado sin borrar'}
}
$mapa += [ordered]@{origen=(Join-Path $raiz '4.5\trabajo_codex'); destino=(Join-Path $archivo '4.5\trabajo_codex'); motivo='Construccion historica; producto oficial permanece en 4.5'}
$limite = [IO.Path]::GetFullPath($raiz).TrimEnd('\') + '\'
foreach($movimiento in $mapa) {
  $fuente = (Resolve-Path -LiteralPath $movimiento.origen).Path
  $destino = [IO.Path]::GetFullPath($movimiento.destino)
  if(-not $fuente.StartsWith($limite,[StringComparison]::OrdinalIgnoreCase) -or -not $destino.StartsWith($limite,[StringComparison]::OrdinalIgnoreCase)) { throw 'Destino o fuente fuera de DEE thinking' }
  if(Test-Path -LiteralPath $destino) { throw "Ya existe destino; no se sobrescribe: $destino" }
  if((Get-Item -LiteralPath $fuente).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Fuente es reparse point: $fuente" }
}
$mapa | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $registro 'MAPA_TRASLADOS.json') -Encoding utf8
$mapa | ForEach-Object { [pscustomobject]$_ } | Format-Table origen,destino -Wrap
if(-not $Ejecutar) { return }
$procesos = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match '^(python|pythonw|ipython|jupyter|WINWORD|soffice|soffice.bin)$' })
if($procesos.Count) { $procesos | Select-Object Id,ProcessName,Path | Format-Table; throw 'Proceso potencialmente afectado: traslado detenido, sin terminarlo' }
if(Test-Path -LiteralPath (Join-Path $registro 'INVENTARIO_ANTES.csv')) { throw 'Ya existe inventario; no repetir traslado silenciosamente' }
Write-Host 'Inventariando archivos sin alterar contenidos...'
$lista = @(Get-ChildItem -LiteralPath $raiz -File -Recurse -Force | ForEach-Object {
  [pscustomobject]@{ruta=$_.FullName.Substring($limite.Length); bytes=$_.Length; utc=$_.LastWriteTimeUtc.ToString('o')}
})
$lista | Export-Csv -LiteralPath (Join-Path $registro 'INVENTARIO_ANTES.csv') -Encoding utf8 -NoTypeInformation
$inicio = [DateTime]::UtcNow.ToString('o')
foreach($movimiento in $mapa) {
  $padre = [IO.Path]::GetDirectoryName($movimiento.destino)
  if(-not(Test-Path -LiteralPath $padre)) { New-Item -ItemType Directory -Path $padre -Force | Out-Null }
  Write-Host ('TRASLADO: ' + $movimiento.origen + ' -> ' + $movimiento.destino)
  Move-Item -LiteralPath $movimiento.origen -Destination $movimiento.destino
}
$fallos = [Collections.Generic.List[object]]::new()
$suma = [long]0
foreach($f in $lista) {
  $anterior = Join-Path $raiz $f.ruta
  $nuevo = $anterior
  foreach($movimiento in $mapa) {
    if($anterior.StartsWith($movimiento.origen+'\',[StringComparison]::OrdinalIgnoreCase)) {
      $nuevo = $movimiento.destino + $anterior.Substring($movimiento.origen.Length)
      break
    }
  }
  if(-not [IO.File]::Exists($nuevo)) { $fallos.Add(@{origen=$anterior;esperado=$nuevo;error='ausente'}); continue }
  $info = [IO.FileInfo]::new($nuevo)
  if($info.Length -ne [long]$f.bytes -or $info.LastWriteTimeUtc.ToString('o') -ne $f.utc) { $fallos.Add(@{origen=$anterior;esperado=$nuevo;error='tamano o fecha de contenido distinto'}) }
  $suma += [long]$info.Length
}
$carpetas = @(Get-ChildItem -LiteralPath $raiz -Force | Select-Object -ExpandProperty Name)
$resultado = [ordered]@{inicio_utc=$inicio; fin_utc=[DateTime]::UtcNow.ToString('o'); raiz=$raiz; archivos_antes=$lista.Count; bytes_verificados=$suma; tipo_verificacion='Presencia, tamano y LastWriteTimeUtc de todos los archivos; hashes criticos en comprobante separado'; fallos=@($fallos); raiz_final=$carpetas; movimientos=$mapa; borrados=0}
$resultado | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $registro 'TRASLADO_VERIFICADO.json') -Encoding utf8
if($fallos.Count) { throw "Hay $($fallos.Count) discrepancias: revisar comprobante; no se borro nada" }
if(@($carpetas | Where-Object { $_ -notin @('4.5','DEE Cognitive System 1.1','archivo') }).Count -or $carpetas.Count -ne 3) { throw 'Raiz no coincide con las tres carpetas solicitadas' }
Write-Host ("Conservados $($lista.Count) archivos, $suma bytes; raiz con tres carpetas; cero borrados.")
