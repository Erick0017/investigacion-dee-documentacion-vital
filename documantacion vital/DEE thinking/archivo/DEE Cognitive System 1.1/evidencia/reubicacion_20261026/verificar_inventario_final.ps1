$ErrorActionPreference = 'Stop'
$raiz = 'D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking'
$mapa = @(Get-Content -LiteralPath (Join-Path $PSScriptRoot 'MAPA_TRASLADOS.json') -Raw | ConvertFrom-Json)
$fallos = [Collections.Generic.List[object]]::new()
$noMovidos = [Collections.Generic.HashSet[string]]::new()
$n = 0
$bytes = [long]0
$docsRespaldados = 0
$principal = Join-Path $raiz 'DEE Cognitive System 1.1'
$readmeAnterior = Join-Path $raiz 'casos practicos\trabajo_codex\DEE Cognitive System 1.1\LEER_PRIMERO.md'
Import-Csv -LiteralPath (Join-Path $PSScriptRoot 'INVENTARIO_ANTES.csv') | ForEach-Object {
  $f = $_
  $anterior = Join-Path $raiz $f.ruta
  $nuevo = $anterior
  foreach($m in $mapa) {
    if($anterior.StartsWith($m.origen+'\',[StringComparison]::OrdinalIgnoreCase)) {
      $propuesto = $m.destino + $anterior.Substring($m.origen.Length)
      if([IO.File]::Exists($propuesto)) { $nuevo = $propuesto }
      else { $nuevo = $anterior; $noMovidos.Add($m.origen) | Out-Null }
      break
    }
  }
  if($anterior -eq $readmeAnterior) {
    $nuevo = Join-Path $raiz 'archivo\reubicacion_20261026\documentos_antes\LEER_PRIMERO.md'
    $docsRespaldados++
  }
  if(-not [IO.File]::Exists($nuevo)) { $fallos.Add(@{origen=$anterior;esperado=$nuevo;error='ausente'}) }
  else {
    $info = [IO.FileInfo]::new($nuevo)
    if($info.Length -ne [long]$f.bytes -or $info.LastWriteTimeUtc.ToString('o') -ne $f.utc) { $fallos.Add(@{origen=$anterior;actual=$nuevo;error='tamano o fecha distintos'}) }
    $bytes += [long]$info.Length
  }
  $n++
}
$carpetas = @(Get-ChildItem -LiteralPath $raiz -Force | Select-Object -ExpandProperty Name)
$resultado = [ordered]@{fin_utc=[DateTime]::UtcNow.ToString('o');raiz=$raiz;archivos_originales=$n;bytes_originales_verificados=$bytes;fallos=@($fallos.ToArray());raiz_final=$carpetas;estructura_tres_carpetas=($carpetas.Count -eq 3 -and @($carpetas | Where-Object {$_ -notin @('4.5','DEE Cognitive System 1.1','archivo')}).Count -eq 0);origenes_con_archivos_aun_no_movidos=@($noMovidos);documentos_anteriores_respaldados=$docsRespaldados;borrados=0;metodo='Presencia,tamano exacto y LastWriteTimeUtc de cada archivo previo. Identidad por SHA de4816archivoscriticos en comprobante separado. README anterior conservado en archivo antes de ajustar rutas.';alcance='No certifica reejecucion de todas las capacidades ni hashes completos de toda la telemetria'}
ConvertTo-Json -InputObject $resultado -Depth 8 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'CONSERVACION_TODOS_LOS_ARCHIVOS.json') -Encoding utf8
Write-Host ("Archivosprevios=$n; bytes=$bytes; discrepancias=$($fallos.Count); raiz="+($carpetas -join ', '))
if($fallos.Count) { throw 'Discrepancias: revisar comprobante sin borrar ni corregir datos silenciosamente' }
