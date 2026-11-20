param(
    [Parameter(Mandatory=$true)][string]$OutputZip,
    [Parameter(Mandatory=$true)][string]$StageRoot
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$stage = [IO.Path]::GetFullPath($StageRoot)
$output = [IO.Path]::GetFullPath($OutputZip)
if ($stage.StartsWith($root + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'StageRoot must be outside the source tree to prevent recursive packaging'
}
if (Test-Path -LiteralPath $stage) { throw "Stage already exists: $stage" }
if (Test-Path -LiteralPath $output) { throw "Output already exists: $output" }
New-Item -ItemType Directory -Path $stage | Out-Null

$items = @(
    'CMakeLists.txt', 'README.md', 'baseline', 'bin', 'config', 'docs',
    'runners', 'tools', 'validation', 'results\final_run', 'results\exploratory'
)
foreach ($item in $items) {
    $source = Join-Path $root $item
    if (-not (Test-Path -LiteralPath $source)) { throw "Missing package item: $item" }
    $parent = Split-Path -Parent (Join-Path $stage $item)
    if ($parent) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    Copy-Item -LiteralPath $source -Destination (Join-Path $stage $item) -Recurse -Force
}

$files = Get-ChildItem -LiteralPath $stage -Recurse -File | Sort-Object FullName
$entries = foreach ($file in $files) {
    $relative = $file.FullName.Substring($stage.Length + 1).Replace('\','/')
    [ordered]@{
        path = $relative
        bytes = $file.Length
        sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $file.FullName).Hash.ToLowerInvariant()
    }
}
$payloadBytes = [Int64]0
foreach ($entry in @($entries)) {
    $payloadBytes += [Int64]$entry['bytes']
}
$manifest = [ordered]@{
    schema = 'dee-thinking-final-laboratory-package-v1'
    campaign_id = 'DEE_THINKING_ENTREGA_02_FINAL_FOCUSED_LAB_20261004'
    payload_file_count = @($entries).Count
    payload_bytes = $payloadBytes
    payload = @($entries)
}
$manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $stage 'MANIFEST.json') -Encoding UTF8
@($entries | ForEach-Object { "$($_.sha256)  $($_.path)" }) | Set-Content -LiteralPath (Join-Path $stage 'HASHES.sha256') -Encoding UTF8

Add-Type -AssemblyName System.IO.Compression.FileSystem
[IO.Compression.ZipFile]::CreateFromDirectory($stage, $output, [IO.Compression.CompressionLevel]::Optimal, $false)
$archive = [IO.Compression.ZipFile]::OpenRead($output)
try {
    if ($archive.Entries.Count -ne (@($entries).Count + 2)) {
        throw "Unexpected ZIP member count: $($archive.Entries.Count)"
    }
    if ($null -eq $archive.GetEntry('MANIFEST.json') -or $null -eq $archive.GetEntry('HASHES.sha256')) {
        throw 'ZIP lacks manifest or hashes'
    }
} finally {
    $archive.Dispose()
}
Write-Output "PACKAGE_CREATED=$output"
Write-Output "PAYLOAD_FILES=$(@($entries).Count)"
Write-Output "ZIP_SHA256=$((Get-FileHash -Algorithm SHA256 -LiteralPath $output).Hash.ToLowerInvariant())"
