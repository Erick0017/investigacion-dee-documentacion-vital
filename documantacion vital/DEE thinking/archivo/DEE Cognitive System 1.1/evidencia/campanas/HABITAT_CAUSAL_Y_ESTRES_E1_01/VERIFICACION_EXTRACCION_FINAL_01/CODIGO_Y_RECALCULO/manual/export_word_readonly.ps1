param(
    [Parameter(Mandatory=$true)][string]$InputDocx,
    [Parameter(Mandatory=$true)][string]$OutputPdf
)
$ErrorActionPreference = 'Stop'
$sourcePath = [IO.Path]::GetFullPath($InputDocx)
$pdfPath = [IO.Path]::GetFullPath($OutputPdf)
if (-not [IO.File]::Exists($sourcePath)) { throw 'Input DOCX is absent.' }
if ([IO.File]::Exists($pdfPath)) { throw 'Refusing to overwrite an existing PDF.' }
[IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($pdfPath)) | Out-Null
$priorWordIds = @(Get-Process -Name WINWORD -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class HabitatWordWindow {
    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);
}
'@
$app = $null
$doc = $null
$ownedInstance = $false
try {
    $app = New-Object -ComObject Word.Application
    [uint32]$wordPid = 0
    [void][HabitatWordWindow]::GetWindowThreadProcessId([IntPtr]$app.Hwnd, [ref]$wordPid)
    if ($wordPid -eq 0 -or $priorWordIds -contains [int]$wordPid) {
        throw 'Word activation did not identify a new owned process; refusing to change or quit it.'
    }
    $ownedInstance = $true
    $app.Visible = $false
    $app.DisplayAlerts = 0
    $app.AutomationSecurity = 3
    $doc = $app.Documents.Open($sourcePath, $false, $true, $false)
    $doc.ExportAsFixedFormat($pdfPath, 17)
    [PSCustomObject]@{ source=$sourcePath; pdf=$pdfPath; word_process_id=$wordPid; read_only=$doc.ReadOnly; page_count=$doc.ComputeStatistics(2); bytes=(Get-Item -LiteralPath $pdfPath).Length } | ConvertTo-Json
}
finally {
    if ($null -ne $doc) { $doc.Close(0); [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($doc) }
    if ($ownedInstance -and $null -ne $app) { $app.Quit(0) }
    if ($null -ne $app) { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($app) }
}
