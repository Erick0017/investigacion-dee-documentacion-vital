param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('bootstrap','create','start','status','panel','advance','pause','resume','release','profile','experience','save','collect','collect-stop','stop','replay','evaluate')]
    [string]$Action,
    [int64]$Count = 0,
    [string]$Channel = 'external.port.alpha',
    [int]$Load = 0,
    [int64]$Tick = -1,
    [string]$RequestId = '',
    [string]$StartCheckpoint = '',
    [string]$Segment = '',
    [int64]$ToTick = 0,
    [string]$ExpectedCheckpoint = ''
)

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$Python = 'D:\Descargas\ANACONDA MINICONDA\python.exe'
$App = Join-Path $Root 'app\habitat.py'
$Launcher = Join-Path $Root 'app\launch_worker.py'
$Wheel = Join-Path $Root 'baseline\dee_thinking-2.2.0-cp313-cp313-win_amd64.whl'
$Site = Join-Path $Root 'baseline\python_site'
$env:PYTHONPATH = $Site
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONUTF8 = '1'

function Invoke-CommandRequest([string]$Operation, [hashtable]$Arguments) {
    $Json = $Arguments | ConvertTo-Json -Compress
    & $Python -B $App command --root $Root --operation $Operation --arguments $Json
    if ($LASTEXITCODE -ne 0) { throw "Habitat command failed: $Operation" }
}

switch ($Action) {
    'bootstrap' {
        New-Item -ItemType Directory -Force -Path $Site | Out-Null
        & $Python -m pip install --no-index --no-deps --upgrade --target $Site $Wheel
        if ($LASTEXITCODE -ne 0) { throw 'Local wheel installation failed' }
    }
    'create' {
        & $Python -B $App init --root $Root --config (Join-Path $Root 'config\habitat.template.json')
        if ($LASTEXITCODE -ne 0) { throw 'Habitat initialization failed' }
    }
    'start' {
        & $Python -B $Launcher --root $Root --python $Python
        if ($LASTEXITCODE -ne 0) { throw 'Independent worker launch failed' }
    }
    'status' {
        & $Python -B $App status --root $Root
    }
    'panel' {
        & $Python -B (Join-Path $Root 'tools\panel.py') --root $Root --output (Join-Path $Root 'analysis\panel_latest.html')
        if ($LASTEXITCODE -ne 0) { throw 'Passive panel generation failed' }
    }
    'advance' {
        if ($Count -le 0) { throw 'Use -Count with a positive tick count' }
        Invoke-CommandRequest 'advance' @{ count = $Count }
    }
    'pause' { Invoke-CommandRequest 'pause' @{} }
    'resume' { Invoke-CommandRequest 'resume' @{} }
    'release' { Invoke-CommandRequest 'release_autonomy' @{} }
    'profile' { Invoke-CommandRequest 'experience_profile' @{ profile = 'late_context' } }
    'experience' {
        $Arguments = @{ channel = $Channel; load = $Load; origin = 'user' }
        if ($Tick -ge 0) { $Arguments.tick = $Tick }
        Invoke-CommandRequest 'experience' $Arguments
    }
    'save' { Invoke-CommandRequest 'save' @{ reason = 'user_requested' } }
    'collect' {
        if (-not $RequestId) { $RequestId = 'COLLECT_' + (Get-Date -Format 'yyyyMMddTHHmmss') }
        $Text = & $Python -B $App command --root $Root --operation collect --arguments (@{ request_id = $RequestId } | ConvertTo-Json -Compress)
        if ($LASTEXITCODE -ne 0) { throw 'Live collection cut failed' }
        $Response = $Text | ConvertFrom-Json
        $Descriptor = Join-Path $Root $Response.descriptor
        $Output = Join-Path $Root ('history\collections\MENTE_BASAL_COLLECTION_' + $RequestId + '_T' + $Response.tick_after + '.zip')
        & $Python -B $App package --root $Root --descriptor $Descriptor --output $Output
        if ($LASTEXITCODE -ne 0) { throw 'Collection packaging failed' }
    }
    'collect-stop' {
        if (-not $RequestId) { $RequestId = 'COLLECT_STOP_' + (Get-Date -Format 'yyyyMMddTHHmmss') }
        $Text = & $Python -B $App command --root $Root --operation collect_stop --arguments (@{ request_id = $RequestId } | ConvertTo-Json -Compress)
        if ($LASTEXITCODE -ne 0) { throw 'Collection-and-stop cut failed' }
        $Response = $Text | ConvertFrom-Json
        $Descriptor = Join-Path $Root $Response.descriptor
        $Output = Join-Path $Root ('history\collections\MENTE_BASAL_COLLECTION_' + $RequestId + '_T' + $Response.tick_after + '.zip')
        & $Python -B $App package --root $Root --descriptor $Descriptor --output $Output
        if ($LASTEXITCODE -ne 0) { throw 'Collection packaging failed' }
    }
    'stop' { Invoke-CommandRequest 'stop' @{ reason = 'user_stop' } }
    'replay' {
        if (-not $StartCheckpoint -or -not $Segment -or $ToTick -le 0) {
            throw 'Replay requires -StartCheckpoint, -Segment and -ToTick'
        }
        $Output = Join-Path $Root ('analysis\replay_T' + $ToTick + '_' + (Get-Date -Format 'yyyyMMddTHHmmss') + '.deetsnap')
        $Args = @('-B',$App,'replay','--root',$Root,'--start',$StartCheckpoint,'--segment',$Segment,'--to',$ToTick,'--output',$Output)
        if ($ExpectedCheckpoint) { $Args += @('--expected',$ExpectedCheckpoint) }
        & $Python @Args
        if ($LASTEXITCODE -ne 0) { throw 'Replay failed' }
    }
    'evaluate' {
        if (-not $StartCheckpoint) { throw 'Evaluate requires -StartCheckpoint' }
        $Output = Join-Path $Root ('analysis\evaluation_' + (Get-Date -Format 'yyyyMMddTHHmmss') + '.json')
        & $Python -B $App evaluate --checkpoint $StartCheckpoint --output $Output
        if ($LASTEXITCODE -ne 0) { throw 'Evaluation failed' }
    }
}
