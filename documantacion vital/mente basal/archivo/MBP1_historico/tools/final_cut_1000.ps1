param(
    [switch]$ValidateOnly
)

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$Python = 'D:\Descargas\ANACONDA MINICONDA\python.exe'
$Habitat = Join-Path $Root 'tools\habitat.ps1'
$Builder = Join-Path $Root 'tools\build_final_cut_1000.py'
$Final = Join-Path $Root 'MENTE_BASAL_CORTE_FINAL_1000_RESULTADOS.zip'
$AutomationDir = Join-Path $Root 'history\automation'
$LockPath = Join-Path $AutomationDir 'FINAL_1000_20261005.lock'
$CompletePath = Join-Path $AutomationDir 'FINAL_1000_20261005_COMPLETED.json'
$LogPath = Join-Path $AutomationDir 'FINAL_1000_20261005.log'
$RequestId = 'FINAL_1000_20261005'
$Target = [datetimeoffset]::Parse('2026-10-05T10:00:00-06:00')

function Read-WorldStatus {
    Get-Content -LiteralPath (Join-Path $Root 'world\status.json') -Raw | ConvertFrom-Json
}

function Write-Log([string]$Message) {
    $Line = ('{0} {1}' -f [datetimeoffset]::UtcNow.ToString('o'), $Message)
    Add-Content -LiteralPath $LogPath -Value $Line -Encoding UTF8
}

$Status = Read-WorldStatus
if ($Status.world_id -ne 'MENTE-BASAL-001') { throw 'Unexpected world_id; refusing final cut' }
if (-not (Test-Path -LiteralPath $Python)) { throw 'Configured CPython runtime is unavailable' }
if (-not (Test-Path -LiteralPath $Habitat)) { throw 'habitat.ps1 is unavailable' }
if (-not (Test-Path -LiteralPath $Builder)) { throw 'final package builder is unavailable' }

if ($ValidateOnly) {
    [pscustomobject]@{
        validation_only = $true
        target_local = $Target.ToString('o')
        world_id = $Status.world_id
        session_id = $Status.session_id
        state = $Status.state
        tick = $Status.tick
        final_output = $Final
        output_already_exists = (Test-Path -LiteralPath $Final)
        will_modify_world = $false
    } | ConvertTo-Json
    exit 0
}

if ([datetimeoffset]::Now -lt $Target) {
    throw ('Refusing early execution before {0}' -f $Target.ToString('o'))
}
if (Test-Path -LiteralPath $Final) {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $Archive = [System.IO.Compression.ZipFile]::OpenRead($Final)
    try {
        if (-not ($Archive.Entries.FullName -contains 'MENTE_BASAL_CORTE_FINAL_1000/FINAL_VALIDATION.json')) {
            throw 'Existing final ZIP lacks validation record'
        }
    } finally { $Archive.Dispose() }
    exit 0
}

New-Item -ItemType Directory -Force -Path $AutomationDir | Out-Null
$Lock = $null
try {
    $Lock = [System.IO.File]::Open($LockPath, [System.IO.FileMode]::CreateNew,
        [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    Write-Log ('START world={0} session={1} tick={2} state={3}' -f $Status.world_id,$Status.session_id,$Status.tick,$Status.state)
    if ($Status.state -notin @('RUNNING','PAUSED')) {
        throw ('World is not available for a safe live cut: {0}' -f $Status.state)
    }
    $Started = [datetimeoffset]::UtcNow
    $CutOutput = & $Habitat -Action collect-stop -RequestId $RequestId 2>&1
    $CutOutput | ForEach-Object { Write-Log ('COLLECT_STOP ' + $_.ToString()) }
    if ($LASTEXITCODE -ne 0) { throw 'collect-stop failed' }

    $Descriptor = Get-ChildItem -LiteralPath (Join-Path $Root 'history\collections') `
        -Filter ('cut_' + $RequestId + '_t*.json') |
        Where-Object { $_.LastWriteTimeUtc -ge $Started.UtcDateTime.AddMinutes(-1) } |
        Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    $Collection = Get-ChildItem -LiteralPath (Join-Path $Root 'history\collections') `
        -Filter ('MENTE_BASAL_COLLECTION_' + $RequestId + '_T*.zip') |
        Where-Object { $_.LastWriteTimeUtc -ge $Started.UtcDateTime.AddMinutes(-1) } |
        Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    if ($null -eq $Descriptor -or $null -eq $Collection) {
        throw 'collect-stop did not publish its descriptor and source collection'
    }
    $DescriptorData = Get-Content -LiteralPath $Descriptor.FullName -Raw | ConvertFrom-Json
    if (-not $DescriptorData.stop_after) { throw 'Published descriptor is not stop_after=true' }

    $Deadline = [datetimeoffset]::UtcNow.AddMinutes(2)
    do {
        $StoppedStatus = Read-WorldStatus
        if ($StoppedStatus.state -in @('STOPPED','STOPPED_SAFE') -and [int64]$StoppedStatus.tick -eq [int64]$DescriptorData.end_tick) { break }
        if ([datetimeoffset]::UtcNow -ge $Deadline) { throw 'Worker did not reach confirmed STOPPED state' }
        Start-Sleep -Seconds 1
    } while ($true)

    $BuildOutput = & $Python -B $Builder --source $Collection.FullName --output $Final `
        --descriptor $Descriptor.FullName --world-status (Join-Path $Root 'world\status.json') 2>&1
    $BuildOutput | ForEach-Object { Write-Log ('PACKAGE ' + $_.ToString()) }
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $Final)) {
        throw 'final package validation/publication failed'
    }
    $FinalHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Final).Hash.ToLowerInvariant()
    $Completed = [ordered]@{
        schema = 'mente-basal.final-cut-1000.completion.v1'
        completed_utc = [datetimeoffset]::UtcNow.ToString('o')
        world_id = $StoppedStatus.world_id
        session_id = $StoppedStatus.session_id
        end_tick = [int64]$StoppedStatus.tick
        state = $StoppedStatus.state
        descriptor = $Descriptor.FullName
        source_collection = $Collection.FullName
        final_zip = $Final
        final_zip_sha256 = $FinalHash
    }
    $TemporaryComplete = $CompletePath + '.tmp'
    $Completed | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $TemporaryComplete -Encoding UTF8
    Move-Item -LiteralPath $TemporaryComplete -Destination $CompletePath -Force
    Write-Log ('COMPLETE tick={0} sha256={1}' -f $StoppedStatus.tick,$FinalHash)
    $Completed | ConvertTo-Json -Depth 5
} catch {
    if (-not (Test-Path -LiteralPath $AutomationDir)) {
        New-Item -ItemType Directory -Force -Path $AutomationDir | Out-Null
    }
    Write-Log ('FAILED ' + $_.Exception.Message)
    throw
} finally {
    if ($null -ne $Lock) { $Lock.Dispose() }
    if (Test-Path -LiteralPath $LockPath) { Remove-Item -LiteralPath $LockPath -Force }
}
