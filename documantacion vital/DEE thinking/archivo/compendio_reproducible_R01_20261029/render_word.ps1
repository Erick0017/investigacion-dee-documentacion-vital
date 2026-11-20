param([Parameter(Mandatory=$true)][string]$InputDocx,[Parameter(Mandatory=$true)][string]$OutputPdf)
$ErrorActionPreference = 'Stop'
$r01app = $null
$r01doc = $null
try {
    $r01input = [System.IO.Path]::GetFullPath($InputDocx)
    $r01output = [System.IO.Path]::GetFullPath($OutputPdf)
    if (-not (Test-Path -LiteralPath $r01input -PathType Leaf)) { throw 'Falta el DOCX de revisión' }
    $r01app = New-Object -ComObject Word.Application
    $r01app.Visible = $false
    $r01app.DisplayAlerts = 0
    $r01app.AutomationSecurity = 3
    $r01doc = $r01app.Documents.Open($r01input,$false,$true,$false)
    $r01doc.Repaginate()
    $r01pages = $r01doc.ComputeStatistics(2)
    $r01doc.ExportAsFixedFormat($r01output,17,$false,0,0,1,$r01pages,0,$true,$true,1,$true,$true,$false)
    [pscustomobject]@{Word=$r01app.Version;Pages=$r01pages;Input=$r01input;Output=$r01output} | ConvertTo-Json
}
finally {
    if ($null -ne $r01doc) { $r01doc.Close(0); [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($r01doc) }
    if ($null -ne $r01app) { $r01app.Quit(); [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($r01app) }
}
