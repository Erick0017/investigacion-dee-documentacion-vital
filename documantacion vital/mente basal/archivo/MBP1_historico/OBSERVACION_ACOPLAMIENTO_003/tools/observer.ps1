param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('start','status','stop')]
    [string]$Action
)

$ErrorActionPreference = 'Stop'
$Area = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$Root = (Resolve-Path -LiteralPath (Join-Path $Area '..')).Path
$Python = 'D:\Descargas\ANACONDA MINICONDA\python.exe'
$Runtime = Join-Path $Area 'observer_runtime'
$Status = Join-Path $Runtime 'observer_status.json'
$Stop = Join-Path $Runtime 'observer.stop'
$PidFile = Join-Path $Runtime 'observer.pid'
$env:PYTHONPATH = Join-Path $Root 'baseline\python_site'
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONUTF8 = '1'

switch ($Action) {
    'start' {
        New-Item -ItemType Directory -Force -Path $Runtime | Out-Null
        if (Test-Path -LiteralPath $PidFile) { throw 'Observer PID file already exists' }
        $stdout = Join-Path $Runtime 'observer.stdout.log'
        $stderr = Join-Path $Runtime 'observer.stderr.log'
        # Start-Process flattens ArgumentList to one command line on Windows.
        # Quote every path explicitly because this workspace contains spaces.
        $Script = Join-Path $Area 'tools\observer_follower.py'
        $arguments = @(
            '-B',
            ('"{0}"' -f $Script),
            '--root', ('"{0}"' -f $Root),
            '--area', ('"{0}"' -f $Area),
            '--poll-seconds', '15'
        )
        $process = Start-Process -FilePath $Python -ArgumentList $arguments -WorkingDirectory $Area -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
        [pscustomobject]@{ launched = $true; pid = $process.Id; area = $Area } | ConvertTo-Json
    }
    'status' {
        if (-not (Test-Path -LiteralPath $Status)) { throw 'Observer status is not available' }
        Get-Content -LiteralPath $Status -Raw
    }
    'stop' {
        New-Item -ItemType File -Force -Path $Stop | Out-Null
        [pscustomobject]@{ stop_requested = $true; path = $Stop } | ConvertTo-Json
    }
}
