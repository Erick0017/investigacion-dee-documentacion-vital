param([Parameter(Mandatory=$true)][string]$JobFile)
$ErrorActionPreference='Stop'
$job40=Get-Content -LiteralPath $JobFile -Raw | ConvertFrom-Json
$owned40=Get-CimInstance Win32_Process -Filter ("ProcessId="+[int]$job40.pid)
if(-not $owned40){Write-Output 'Owned process already absent';exit 0}
$start40=[DateTimeOffset]::Parse($job40.start_utc)
$created40=[DateTimeOffset]$owned40.CreationDate
if([Math]::Abs(($created40.ToUniversalTime()-$start40.ToUniversalTime()).TotalSeconds)-gt 20){throw 'PID reuse/creation mismatch: no termination'}
$expected40=[string]$job40.argv[2]
if(-not $owned40.CommandLine.Contains($expected40)){throw 'Command mismatch: no termination'}
Write-Output ($owned40 | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json)
& taskkill.exe /PID ([string]$owned40.ProcessId) /T /F
if($LASTEXITCODE-ne 0){throw 'Owned termination failed'}
