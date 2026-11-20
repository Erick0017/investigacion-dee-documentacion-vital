param(
  [ValidateSet('status','stop','repackage')]
  [string]$Action = 'status'
)
$Root = Split-Path -Parent $PSScriptRoot
$Python = 'D:\Descargas\ANACONDA MINICONDA\python.exe'
& $Python -B (Join-Path $Root 'app\campaign.py') $Action --campaign-root $Root
exit $LASTEXITCODE
