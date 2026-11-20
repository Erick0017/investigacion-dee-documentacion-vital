$ErrorActionPreference = 'Stop'
$registro = $PSScriptRoot
$raiz = 'D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking'
$limite = [IO.Path]::GetFullPath($raiz).TrimEnd('\') + '\'
$mapa = @(Get-Content -LiteralPath (Join-Path $registro 'MAPA_TRASLADOS.json') -Raw | ConvertFrom-Json)
function Validar([string]$ruta) {
  $p = [IO.Path]::GetFullPath($ruta)
  if(-not $p.StartsWith($limite,[StringComparison]::OrdinalIgnoreCase)) { throw "Fuera de la raiz autorizada: $p" }
  return $p
}
$procesos = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match '^(python|pythonw|ipython|jupyter|WINWORD|soffice|soffice.bin)$' })
if($procesos.Count) { throw 'Proceso potencialmente afectado: no se mueve ni termina ninguno' }
$operaciones = [Collections.Generic.List[object]]::new()
function Completar([string]$fuente,[string]$destino) {
  $fuente = Validar $fuente
  $destino = Validar $destino
  $item = Get-Item -LiteralPath $fuente -Force
  if($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
    $esperado = Join-Path $raiz 'casos practicos\trabajo_codex\DEE Cognitive System 1.1\laboratorio\campanas\CONSOLIDACION_1_1\herramientas\node_modules'
    $destinoExterno = 'C:\Users\Erik\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules'
    if($fuente -ne $esperado -or $item.LinkType -ne 'Junction' -or $item.Target -ne $destinoExterno) { throw "Reparse point no reconocido: $fuente" }
    if(Test-Path -LiteralPath $destino) {
      $residuo = Validar (Join-Path $raiz 'archivo\incidente_traslado_20261026\copia_parcial_node_modules')
      if(Test-Path -LiteralPath $residuo) { throw 'Residuo previo ya preservado; revisar antes de continuar' }
      [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($residuo)) | Out-Null
      [IO.Directory]::Move($destino,$residuo)
      $operaciones.Add(@{fuente=$destino;destino=$residuo;tipo='Residuo de intento inicial preservado; no borrado'})
    }
    # Rename del enlace NTFS mismo; nunca enumerar ni modificar su destino C:.
    [IO.Directory]::Move($fuente,$destino)
    $operaciones.Add(@{fuente=$fuente;destino=$destino;tipo='Junction preservada sin seguirla';target=$destinoExterno})
    return
  }
  if(-not(Test-Path -LiteralPath $destino)) {
    $padre = [IO.Path]::GetDirectoryName($destino)
    if(-not(Test-Path -LiteralPath $padre)) { [IO.Directory]::CreateDirectory($padre) | Out-Null }
    if($item.PSIsContainer) { [IO.Directory]::Move($fuente,$destino) }
    else { [IO.File]::Move($fuente,$destino) }
    $operaciones.Add(@{fuente=$fuente;destino=$destino;tipo='traslado sin sobrescribir'})
  } elseif($item.PSIsContainer -and [IO.Directory]::Exists($destino)) {
    foreach($hijo in @(Get-ChildItem -LiteralPath $fuente -Force)) { Completar $hijo.FullName (Join-Path $destino $hijo.Name) }
    # No se borran ni siquiera los directorios vacios de origen: viajan al archivo con su padre.
  } elseif(-not $item.PSIsContainer -and [IO.File]::Exists($destino)) {
    if((Get-FileHash -LiteralPath $fuente -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath $destino -Algorithm SHA256).Hash) { throw "Colision de contenidos: $fuente" }
    $operaciones.Add(@{fuente=$fuente;destino=$destino;tipo='duplicado identico preservado en ambas ubicaciones'})
  } else { throw "Colision de tipos: $fuente" }
}
try {
  foreach($m in $mapa) {
    Validar $m.origen | Out-Null
    Validar $m.destino | Out-Null
    if(Test-Path -LiteralPath $m.origen) {
      Write-Host ('COMPLETAR: '+$m.origen+' -> '+$m.destino)
      Completar $m.origen $m.destino
    } elseif(-not(Test-Path -LiteralPath $m.destino)) { throw "Ausentes fuente y destino: $($m.origen)" }
  }
} finally {
  ConvertTo-Json -InputObject @($operaciones.ToArray()) -Depth 6 | Set-Content -LiteralPath (Join-Path $registro 'OPERACIONES_CONTINUACION.json') -Encoding utf8
}
$fallos = [Collections.Generic.List[object]]::new()
$n = 0
$bytes = [long]0
Import-Csv -LiteralPath (Join-Path $registro 'INVENTARIO_ANTES.csv') | ForEach-Object {
  $f = $_
  $anterior = Join-Path $raiz $f.ruta
  $nuevo = $anterior
  foreach($m in $mapa) {
    if($anterior.StartsWith($m.origen+'\',[StringComparison]::OrdinalIgnoreCase)) {
      $nuevo = $m.destino + $anterior.Substring($m.origen.Length)
      break
    }
  }
  if(-not [IO.File]::Exists($nuevo)) { $fallos.Add(@{origen=$anterior;esperado=$nuevo;error='ausente'}) }
  else {
    $info = [IO.FileInfo]::new($nuevo)
    if($info.Length -ne [long]$f.bytes -or $info.LastWriteTimeUtc.ToString('o') -ne $f.utc) { $fallos.Add(@{origen=$anterior;esperado=$nuevo;error='tamano o fecha distintos'}) }
    $bytes += [long]$info.Length
  }
  $n++
}
$carpetas = @(Get-ChildItem -LiteralPath $raiz -Force | Select-Object -ExpandProperty Name)
$resultado = [ordered]@{fin_utc=[DateTime]::UtcNow.ToString('o');raiz=$raiz;archivos_antes=$n;bytes_verificados=$bytes;fallos=@($fallos);raiz_final=$carpetas;movimientos=$mapa;borrados=0;incidente='Move-Item inicial obtuvo AccessDenied tras traslado parcial; continuacion sin sobrescribir y con rename de directorios validado';tipo_verificacion='Todos los archivos: presencia,tamano,LastWriteTimeUtc. SHA criticos en comprobante separado'}
$resultado | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $registro 'TRASLADO_VERIFICADO.json') -Encoding utf8
if($fallos.Count) { throw "Hay $($fallos.Count) discrepancias; datos conservados, revisar informe" }
if(@($carpetas | Where-Object { $_ -notin @('4.5','DEE Cognitive System 1.1','archivo') }).Count -or $carpetas.Count -ne 3) { throw 'La raiz no coincide con las tres carpetas solicitadas' }
Write-Host "Conservados $n archivos, $bytes bytes; tres carpetas en raiz; cero borrados."
