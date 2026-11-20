param()

$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath('D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\mente basal')
$archive = Join-Path $root 'archivo'
$ledgerPath = Join-Path $archive 'reorganizacion\MOVE_LEDGER.csv'
$rows = [System.Collections.Generic.List[object]]::new()

function Assert-InRoot([string]$Path) {
    $resolved = [IO.Path]::GetFullPath($Path)
    if (-not $resolved.StartsWith($root + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -and $resolved -ne $root) {
        throw "Path escapes intended root: $resolved"
    }
    return $resolved
}

function Record-And-Move([string]$Source, [string]$Destination) {
    $src = Assert-InRoot $Source
    $dst = Assert-InRoot $Destination
    if (-not (Test-Path -LiteralPath $src)) { return }
    if (Test-Path -LiteralPath $dst) { throw "Destination already exists: $dst" }
    $item = Get-Item -LiteralPath $src -Force
    $files = if ($item.PSIsContainer) {
        @(Get-ChildItem -LiteralPath $src -Force -Recurse -File)
    } else {
        @($item)
    }
    $total = [int64]0
    foreach ($file in $files) {
        $rel = if ($item.PSIsContainer) { [IO.Path]::GetRelativePath($src, $file.FullName) } else { $file.Name }
        $targetFile = if ($item.PSIsContainer) { Join-Path $dst $rel } else { $dst }
        $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        $total += $file.Length
        $rows.Add([pscustomobject]@{
            kind = 'file'
            original_path = $file.FullName
            new_path = $targetFile
            bytes = $file.Length
            sha256 = $hash
        })
    }
    if ($item.PSIsContainer) {
        $rows.Add([pscustomobject]@{
            kind = 'directory'
            original_path = $src
            new_path = $dst
            bytes = $total
            sha256 = ''
        })
    }
    New-Item -ItemType Directory -Path (Split-Path -Parent $dst) -Force | Out-Null
    Move-Item -LiteralPath $src -Destination $dst
}

# Canonical stage archives are promoted to the clean root before their work trees move.
Record-And-Move (Join-Path $root 'mente basal persistente 2\MENTE_BASAL_PERSISTENTE_2_ABC_2H_RESULTADOS.zip') (Join-Path $root 'MENTE_BASAL_PERSISTENTE_2_ABC_2H_RESULTADOS.zip')
Record-And-Move (Join-Path $root 'mente basal persistente 3\MENTE_BASAL_PERSISTENTE_3_CURRICULUM_NATIVO_2H_RESULTADOS.zip') (Join-Path $root 'MENTE_BASAL_PERSISTENTE_3_CURRICULUM_NATIVO_2H_RESULTADOS.zip')

Record-And-Move (Join-Path $root 'MENTE_BASAL_HABITAT_PERSISTENTE_SESION_001_RESULTADOS.zip') (Join-Path $archive 'MBP1_historico\MENTE_BASAL_HABITAT_PERSISTENTE_SESION_001_RESULTADOS.zip')
Record-And-Move (Join-Path $root 'MENTE_BASAL_RECOLECCION_CUT_002_RESULTADOS.zip') (Join-Path $archive 'MBP1_historico\MENTE_BASAL_RECOLECCION_CUT_002_RESULTADOS.zip')
Record-And-Move (Join-Path $root 'MENTE_BASAL_OBSERVACION_Y_ACOPLAMIENTO_003_RESULTADOS.zip') (Join-Path $archive 'MBP1_historico\MENTE_BASAL_OBSERVACION_Y_ACOPLAMIENTO_003_RESULTADOS.zip')

$mbp1Dirs = @('.runtime','analysis','app','baseline','bin','config','delivery','docs','history','OBSERVACION_ACOPLAMIENTO_003','src','tools','validation','world')
foreach ($name in $mbp1Dirs) {
    Record-And-Move (Join-Path $root $name) (Join-Path $archive "MBP1_historico\$name")
}
Record-And-Move (Join-Path $root 'mente basal persistente 2') (Join-Path $archive 'MBP2_historico\trabajo')
Record-And-Move (Join-Path $root 'mente basal persistente 3') (Join-Path $archive 'MBP3_historico\trabajo')

$rows | Export-Csv -LiteralPath $ledgerPath -NoTypeInformation -Encoding utf8
Write-Output "MOVE_LEDGER_ROWS=$($rows.Count)"
Write-Output "MOVE_LEDGER=$ledgerPath"
