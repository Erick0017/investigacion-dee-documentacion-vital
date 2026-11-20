param(
    [switch]$RootRun,
    [Parameter(Mandatory=$true)][string]$Output,
    [string]$HostPython = 'D:\Descargas\ANACONDA MINICONDA\python.exe'
)
# Root-only host resource operation. NEVER Stop-Process/Kill, never targets a
# Native owner, C01 or new R02. WM_CLOSE may expose a save dialog; that remains
# unresolved and is reported, not forced. Parent already confirmed both Edit.
$ErrorActionPreference = 'Stop'
if (-not $RootRun) { throw 'Explicit -RootRun required; no process has been touched.' }
$campaignRoot = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$expectedExe = 'C:\Users\Erik\AppData\Local\Roblox\Versions\version-63eb6055af4e4688\RobloxStudioBeta.exe'
$keepPids = @(7252,13064)
$targets = @(
    @{ Pid=5392; StartUtc='2026-11-15T05:44:24.639Z'; File='DEE_RBX01_C02_DEV4.rbxlx'; Clone='DEV'; Closure='evidencia\DEV_REAPERTURA_R04\SOURCE_OWNER_CLOSED.json' },
    @{ Pid=18244; StartUtc='2026-11-15T05:59:51.988Z'; File='DEE_RBX01_C02.rbxlx'; Clone='MAIN'; Closure='evidencia\MAIN_PERIODO_01\SOURCE_OWNER_CLOSED.json' }
)
function Assert-LocalPath([string]$PathValue) {
    $full = [IO.Path]::GetFullPath($PathValue)
    if (-not ($full.Equals($campaignRoot,[StringComparison]::OrdinalIgnoreCase) -or
        $full.StartsWith($campaignRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase))) {
        throw 'Audit path outside R05 campaign.'
    }
    $cursor = $full
    while ($cursor) {
        if (Test-Path -LiteralPath $cursor) {
            $item = Get-Item -LiteralPath $cursor -Force
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse path denied.' }
        }
        $parent = [IO.Path]::GetDirectoryName($cursor)
        if ($parent -eq $cursor) { break }
        $cursor = $parent
    }
    return $full
}
function Save-NewJson([string]$PathValue,$Value) {
    if (Test-Path -LiteralPath $PathValue) { throw 'Preserve existing close evidence.' }
    $json = $Value | ConvertTo-Json -Depth 30
    [IO.File]::WriteAllText($PathValue,$json+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))
}
function Get-CloneClosedProof($Target) {
    $destination = Assert-LocalPath (Join-Path $campaignRoot ('native\'+$Target.Clone))
    $closurePath = Assert-LocalPath (Join-Path $campaignRoot $Target.Closure)
    if (-not (Test-Path -LiteralPath $closurePath)) { throw ('Missing official closure proof: '+$Target.Clone) }
    $proof = Get-Content -LiteralPath $closurePath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($proof.ownerClosed -ne $true -or $proof.writerDrained -ne $true -or
        $proof.source_journal_event.exit_code -ne 0 -or $proof.source_journal_event.final_status.running -ne $false) {
        throw ('Native closure not proved: '+$Target.Clone)
    }
    $monitor = Join-Path $campaignRoot 'control\monitor_solo_lectura_C02.py'
    $text = & $HostPython -I -B $monitor --destination $destination
    if ($LASTEXITCODE -ne 0) { throw ('Readonly clone monitor failed: '+$Target.Clone) }
    $state = ($text -join [Environment]::NewLine) | ConvertFrom-Json
    if ($state.owner_cached.running -ne $false -or $state.owner_cached.uncertain_external_result -ne $false -or
        @($state.pending_requests).Count -ne 0 -or $state.life_id -ne $proof.lifeId) {
        throw ('Clone has a live/uncertain owner or pending requests: '+$Target.Clone)
    }
    $lock = Join-Path $destination ('sistema\estado\locks\'+$state.life_id+'.lock')
    if (Test-Path -LiteralPath $lock) { throw ('Native lock exists; no Studio close attempted: '+$Target.Clone) }
    return @{ Life=$state.life_id; CachedTick=$state.owner_cached.tick; Running=$state.owner_cached.running;
        PendingRequests=@($state.pending_requests).Count; ClosurePath=$closurePath;
        ClosureSha256=(Get-FileHash -LiteralPath $closurePath -Algorithm SHA256).Hash.ToLowerInvariant() }
}
$outputDir = Assert-LocalPath $Output
if (Test-Path -LiteralPath $outputDir) { throw 'New output directory required; no overwrite.' }
if (-not (Test-Path -LiteralPath $HostPython -PathType Leaf)) { throw 'Existing host Python unavailable.' }
# Validate ALL targets/Native closures before requesting ANY window close.
$validated = @()
foreach ($target in $targets) {
    if ($keepPids -contains $target.Pid) { throw 'Protected Studio PID was accidentally targeted.' }
    $closed = Get-CloneClosedProof $target
    $process = Get-Process -Id $target.Pid -ErrorAction SilentlyContinue
    if ($null -eq $process) {
        $validated += @{ Target=$target; NativeClosed=$closed; AlreadyExited=$true }; continue
    }
    $actualExe = [IO.Path]::GetFullPath($process.Path)
    $actualStart = $process.StartTime.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
    if (-not $actualExe.Equals($expectedExe,[StringComparison]::OrdinalIgnoreCase) -or $actualStart -ne $target.StartUtc) {
        throw ('Exact executable/start-time identity mismatch, no windows touched: PID '+$target.Pid)
    }
    $validated += @{ Target=$target; NativeClosed=$closed; AlreadyExited=$false; Process=$process;
        VerifiedExe=$actualExe; VerifiedStartUtc=$actualStart }
}
New-Item -ItemType Directory -Path $outputDir | Out-Null
$report = @{ Schema='DEE.RBX01.C02.finished_Studio_graceful_close.R01'; StartedUtc=[DateTime]::UtcNow.ToString('o');
    ProtectedPids=$keepPids; Targets=@(); NativeActions=0; NativeProcessesStopped=0; ForcedTerminations=0;
    EditModeScope='Both target Studios previously confirmed Edit by Root MCP; helper invokes no MCP and does not change Play.' }
Save-NewJson (Join-Path $outputDir 'INTENCION_CIERRE.json') @{ Targets=$targets; ProtectedPids=$keepPids; Mode='CloseMainWindow only'; NativeClosures=$validated.NativeClosed }
foreach ($entry in $validated) {
    $row = @{ Pid=$entry.Target.Pid; ExpectedFile=$entry.Target.File; ExpectedStartUtc=$entry.Target.StartUtc;
        NativeClosed=$entry.NativeClosed; ForceKill=$false }
    if ($entry.AlreadyExited) { $row.Status='ALREADY_EXITED_NO_ACTION'; $row.ProcessExited=$true }
    else {
        $process = $entry.Process
        # Revalidate immediately before WM_CLOSE; never rely on PID alone.
        $process.Refresh()
        if ($process.HasExited) { $row.Status='EXITED_BEFORE_REQUEST'; $row.ProcessExited=$true }
        elseif ($process.StartTime.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffZ') -ne $entry.VerifiedStartUtc -or
            -not ([IO.Path]::GetFullPath($process.Path)).Equals($entry.VerifiedExe,[StringComparison]::OrdinalIgnoreCase)) {
            $row.Status='IDENTITY_CHANGED_NO_ACTION'; $row.ProcessExited=$false
        } else {
            try {
                $row.CloseMainWindowReturned = $process.CloseMainWindow()
                if ($row.CloseMainWindowReturned) { $row.ProcessExited = $process.WaitForExit(15000) }
                else { $row.ProcessExited = $false }
                $row.Status = if ($row.ProcessExited) { 'GRACEFULLY_EXITED' } else { 'WINDOW_OR_SAVE_DIALOG_PENDING_NO_FORCE' }
            } catch { $row.Status='CLOSE_REQUEST_REJECTED_NO_FORCE'; $row.ErrorType=$_.Exception.GetType().FullName; $row.ProcessExited=$false }
        }
    }
    $report.Targets += $row
    Save-NewJson (Join-Path $outputDir ('PID_'+$entry.Target.Pid+'.json')) $row
}
$report.FinishedUtc = [DateTime]::UtcNow.ToString('o')
Save-NewJson (Join-Path $outputDir 'RESULTADO_CIERRE_STUDIOS.json') $report
$report | ConvertTo-Json -Depth 30
