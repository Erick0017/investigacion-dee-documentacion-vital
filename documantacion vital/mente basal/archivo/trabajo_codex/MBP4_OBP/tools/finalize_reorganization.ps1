param()

$ErrorActionPreference = 'Stop'

$ScriptPath = $MyInvocation.MyCommand.Path
$Work = Split-Path -Parent (Split-Path -Parent $ScriptPath)
$Root = Split-Path -Parent (Split-Path -Parent $Work)
$Archive = Join-Path $Root 'archivo'
$Reorg = Join-Path $Archive 'reorganizacion'
$PostPath = Join-Path $Reorg 'POST_REORG_MANIFEST.json'
$HashesPath = Join-Path $Reorg 'HASHES.sha256'

$expectedDirectories = @('archivo', 'trabajo_codex')
$expectedZips = @(
    'MENTE_BASAL_CORTE_FINAL_1000_RESULTADOS.zip',
    'MENTE_BASAL_PERSISTENTE_2_ABC_2H_RESULTADOS.zip',
    'MENTE_BASAL_PERSISTENTE_3_CURRICULUM_NATIVO_2H_RESULTADOS.zip',
    'MENTE_BASAL_4_ORGANIZACION_BASAL_PERSISTENTE_VALIDACION_RESULTADOS.zip'
)

$top = @(Get-ChildItem -LiteralPath $Root | Sort-Object Name)
$unexpected = @($top | Where-Object {
    if ($_.PSIsContainer) { $_.Name -notin $expectedDirectories }
    else { $_.Name -notin $expectedZips }
})
if ($unexpected.Count -gt 0) {
    throw ('Unexpected root entries: ' + (($unexpected | ForEach-Object Name) -join ', '))
}

$missing = @()
foreach ($name in ($expectedDirectories + $expectedZips)) {
    if (-not (Test-Path -LiteralPath (Join-Path $Root $name))) { $missing += $name }
}
if ($missing.Count -gt 0) { throw ('Missing root entries: ' + ($missing -join ', ')) }

$fileRecords = [System.Collections.Generic.List[object]]::new()
Get-ChildItem -LiteralPath $Root -File -Recurse | Where-Object {
    $_.FullName -ne $PostPath -and $_.FullName -ne $HashesPath
} | Sort-Object FullName | ForEach-Object {
    $relative = [System.IO.Path]::GetRelativePath($Root, $_.FullName)
    $fileRecords.Add([ordered]@{
        path = $relative
        bytes = $_.Length
        last_write_utc = $_.LastWriteTimeUtc.ToString('o')
    })
}

$post = [ordered]@{
    schema = 'mbp4.post-reorg-manifest.v1'
    created_utc = [DateTimeOffset]::UtcNow.ToString('o')
    root = $Root
    root_policy = 'Only archivo, trabajo_codex, and four canonical ZIP files'
    root_entries = @($top | ForEach-Object {
        [ordered]@{
            name = $_.Name
            type = $(if ($_.PSIsContainer) { 'directory' } else { 'file' })
            bytes = $(if ($_.PSIsContainer) { $null } else { $_.Length })
        }
    })
    file_count_excluding_this_manifest_and_hash_list = $fileRecords.Count
    files = $fileRecords
    movement_ledger = 'archivo/reorganizacion/MOVE_LEDGER.csv'
    pre_manifest = 'archivo/reorganizacion/PRE_REORG_MANIFEST.json'
    note = 'Moved-file SHA-256 values are retained in MOVE_LEDGER.csv; important final artifacts are hashed in HASHES.sha256.'
}
$post | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $PostPath -Encoding utf8

$hashTargets = @(
    (Join-Path $Reorg 'PRE_REORG_MANIFEST.json'),
    (Join-Path $Reorg 'MOVE_LEDGER.csv'),
    (Join-Path $Archive 'ARCHIVO_INDEX.md'),
    $PostPath
)
foreach ($name in $expectedZips) { $hashTargets += (Join-Path $Root $name) }

$hashLines = foreach ($target in $hashTargets) {
    if (-not (Test-Path -LiteralPath $target)) { throw "Missing hash target: $target" }
    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $target).Hash.ToLowerInvariant()
    $relative = [System.IO.Path]::GetRelativePath($Root, $target).Replace('\', '/')
    "$hash  $relative"
}
$hashLines | Set-Content -LiteralPath $HashesPath -Encoding ascii

[ordered]@{
    pass = $true
    root_entries = @($top.Name)
    post_manifest = $PostPath
    hashes = $HashesPath
    files_recorded = $fileRecords.Count
} | ConvertTo-Json -Depth 4
