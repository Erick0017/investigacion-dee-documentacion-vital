param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('prepare','start','status','stop','repackage')]
    [string]$Action,
    [switch]$Trial,
    [double]$DurationSeconds = 0
)

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$Python = 'D:\Descargas\ANACONDA MINICONDA\python.exe'
$Campaign = Join-Path $Root 'app\campaign.py'
$Launcher = Join-Path $Root 'app\launch_process.py'
$ModeArgs = @()
if ($Trial) { $ModeArgs += '--trial' }
if ($DurationSeconds -gt 0) { $ModeArgs += @('--duration-seconds', [string]$DurationSeconds) }

switch ($Action) {
    'prepare' {
        & $Python -B $Campaign prepare @ModeArgs
        if ($LASTEXITCODE -ne 0) { throw 'MBP2 preparation failed' }
    }
    'start' {
        $SupervisorDir = if ($Trial) { Join-Path $Root 'test_campaign\supervisor' } else { Join-Path $Root 'supervisor' }
        New-Item -ItemType Directory -Force -Path $SupervisorDir | Out-Null
        $Handshake = Join-Path $SupervisorDir 'independent_supervisor_launch.json'
        $Stdout = Join-Path $SupervisorDir 'supervisor.stdout.log'
        $Stderr = Join-Path $SupervisorDir 'supervisor.stderr.log'
        $Args = @(
            '--python', $Python,
            '--script', $Campaign,
            '--cwd', $Root,
            '--stdout', $Stdout,
            '--stderr', $Stderr,
            '--handshake', $Handshake,
            '--', 'supervise'
        ) + $ModeArgs
        & $Python -B $Launcher @Args
        if ($LASTEXITCODE -ne 0) { throw 'Independent MBP2 supervisor launch failed' }
    }
    'status' {
        & $Python -B $Campaign status @ModeArgs
        if ($LASTEXITCODE -ne 0) { throw 'MBP2 status failed' }
    }
    'stop' {
        & $Python -B $Campaign stop @ModeArgs
        if ($LASTEXITCODE -ne 0) { throw 'MBP2 safe stop/finalization failed' }
    }
    'repackage' {
        & $Python -B $Campaign repackage @ModeArgs
        if ($LASTEXITCODE -ne 0) { throw 'MBP2 immutable repackage failed' }
    }
}
