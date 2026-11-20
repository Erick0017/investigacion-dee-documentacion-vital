param([Parameter(Mandatory=$true)][string]$Cpc3Root)
$ErrorActionPreference = 'Stop'
$cpcResolved = [IO.Path]::GetFullPath($Cpc3Root).TrimEnd('\')
$caseRoot = Split-Path (Split-Path $cpcResolved -Parent) -Parent
$scopePrefix = $caseRoot.TrimEnd('\') + '\'
$migrationPath = Join-Path $cpcResolved 'MIGRACION_Y_LIMPIEZA.json'
$proofPath = Join-Path $cpcResolved 'resultados\CLEAN_REPRODUCTION.json'
$proof = Get-Content -LiteralPath $proofPath -Raw | ConvertFrom-Json
if (-not $proof.verified -or -not $proof.inherited_reference_reproduced -or -not $proof.new_result_reproduced -or -not $proof.snapshot_new_question -or -not $proof.no_old_path_dependency) { throw 'Independent reproduction prerequisites not satisfied' }
$publication = Get-Content -LiteralPath (Join-Path $cpcResolved 'staging\PUBLICATION.json') -Raw | ConvertFrom-Json
$officialPath = Join-Path $caseRoot 'CPC3_ENTE_COGNITIVO_CAUSAL_DEE_3_5_0_RESULTADOS.zip'
if ((Get-FileHash -LiteralPath $officialPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $publication.sha256) { throw 'Published CPC3 identity changed' }
$migration = Get-Content -LiteralPath $migrationPath -Raw | ConvertFrom-Json
$allowed = @(
  (Join-Path $caseRoot 'CASOS_PRACTICOS_01_DEE_THINKING_3_5_0_8_CAMPOS_RESULTADOS.zip'),
  (Join-Path $caseRoot 'CP02_A_PRODUCTO_DEE_3_5_0_RESULTADOS.zip'),
  (Join-Path $caseRoot 'CP02_B_ENTE_PREDICTIVO_DEE_3_5_0_RESULTADOS.zip'),
  (Join-Path $caseRoot 'trabajo_codex\CP01_8_CAMPOS'),
  (Join-Path $caseRoot 'trabajo_codex\CP02_DOS_LINEAS')
)
$resolvedTargets = @($migration.cleanup_targets | ForEach-Object { [IO.Path]::GetFullPath([string]$_.absolute_path).TrimEnd('\') })
if ($resolvedTargets.Count -ne 5 -or @($resolvedTargets | Select-Object -Unique).Count -ne 5 -or @(Compare-Object ($allowed | Sort-Object) ($resolvedTargets | Sort-Object)).Count -ne 0) { throw 'Cleanup requires exactly the five individually authorized targets' }
foreach ($parentPackage in $migration.parents) {
  if ($allowed -notcontains [string]$parentPackage.path) { throw 'Unlisted parent package in migration record' }
  if ((Get-FileHash -LiteralPath ([string]$parentPackage.path) -Algorithm SHA256).Hash.ToLowerInvariant() -ne [string]$parentPackage.sha256) { throw 'Historical parent changed since migration; cleanup stopped' }
}
$receipts = @()
foreach ($targetEntry in $migration.cleanup_targets) {
  $targetPath = [IO.Path]::GetFullPath([string]$targetEntry.absolute_path).TrimEnd('\')
  if (-not $targetPath.StartsWith($scopePrefix,[StringComparison]::OrdinalIgnoreCase) -or $targetPath -eq $caseRoot -or $allowed -notcontains $targetPath) { throw "Unsafe or unlisted target: $targetPath" }
  $receipt = [ordered]@{ absolute_path=$targetPath; removed=$false; recoverable_backup_created=$false; sha256_before=$null; error=$null }
  try {
    $ancestor = Split-Path $targetPath -Parent
    while ($ancestor) {
      $parentItem = Get-Item -LiteralPath $ancestor -Force
      if (($parentItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Reparse ancestor not followed: $ancestor" }
      $nextAncestor = Split-Path $ancestor -Parent
      if ($nextAncestor -eq $ancestor) { break }
      $ancestor = $nextAncestor
    }
    if (Test-Path -LiteralPath $targetPath) {
      $stack = [Collections.Generic.Stack[string]]::new()
      $stack.Push($targetPath)
      while ($stack.Count -gt 0) {
        $itemPath = $stack.Pop()
        $item = Get-Item -LiteralPath $itemPath -Force
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Reparse point not followed: $itemPath" }
        $absoluteItem = [IO.Path]::GetFullPath($item.FullName)
        if (-not ($absoluteItem -eq $targetPath -or $absoluteItem.StartsWith($targetPath+'\',[StringComparison]::OrdinalIgnoreCase))) { throw "Escaped target: $absoluteItem" }
        if ($item.PSIsContainer) {
          foreach ($child in Get-ChildItem -LiteralPath $itemPath -Force) { $stack.Push($child.FullName) }
        }
      }
      if (-not (Get-Item -LiteralPath $targetPath).PSIsContainer) { $receipt.sha256_before = (Get-FileHash -LiteralPath $targetPath -Algorithm SHA256).Hash.ToLowerInvariant() }
      Remove-Item -LiteralPath $targetPath -Recurse -Force
    }
    $receipt.removed = -not (Test-Path -LiteralPath $targetPath)
  } catch { $receipt.error = $_.Exception.Message }
  $receipts += [pscustomobject]$receipt
}
$migration | Add-Member -NotePropertyName cleanup_receipts -NotePropertyValue $receipts -Force
$allRemoved = @($receipts | Where-Object { -not $_.removed }).Count -eq 0
$migration.cleanup_status = if ($allRemoved) { 'COMPLETED_EXPLICIT_TARGETS_ONLY' } else { 'PARTIAL_EXPLICIT_TARGETS_ONLY' }
$migration | Add-Member -NotePropertyName cleanup_utc -NotePropertyValue ([DateTimeOffset]::UtcNow.ToString('o')) -Force
[IO.File]::WriteAllText($migrationPath,($migration | ConvertTo-Json -Depth 80),[Text.UTF8Encoding]::new($false))
$receipts | ConvertTo-Json -Depth 5
if (-not $allRemoved) { exit 2 }
