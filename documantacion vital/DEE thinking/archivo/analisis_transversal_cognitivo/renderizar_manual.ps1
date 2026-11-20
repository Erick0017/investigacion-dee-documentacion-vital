param([Parameter(Mandatory=$true)][string]$InputDocx,[Parameter(Mandatory=$true)][string]$OutputPdf)
$ErrorActionPreference='Stop'
$taskWord=$null
$taskDoc=$null
$taskOldLinks=$null
try {
    $taskInput=[IO.Path]::GetFullPath($InputDocx)
    $taskOutput=[IO.Path]::GetFullPath($OutputPdf)
    $taskWord=New-Object -ComObject Word.Application
    $taskWord.Visible=$false
    $taskWord.DisplayAlerts=0
    $taskWord.AutomationSecurity=3
    $taskOldLinks=$taskWord.Options.UpdateLinksAtOpen
    $taskWord.Options.UpdateLinksAtOpen=$false
    $taskDoc=$taskWord.Documents.Open($taskInput,$false,$false,$false)
    $taskDoc.Fields.Update() | Out-Null
    $taskDoc.Repaginate()
    $taskDoc.Save()
    $taskPages=$taskDoc.ComputeStatistics(2)
    $taskDoc.ExportAsFixedFormat($taskOutput,17,$false,0,0,1,$taskPages,0,$true,$true,1,$true,$true,$false)
    [pscustomobject]@{Word=$taskWord.Version;Pages=$taskPages;Input=$taskInput;Output=$taskOutput;CandidateSaved=$true;OriginalOpened=$false} | ConvertTo-Json
}
finally {
    if($null -ne $taskDoc){$taskDoc.Close(0);[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskDoc)}
    if($null -ne $taskWord){
        if($null -ne $taskOldLinks){$taskWord.Options.UpdateLinksAtOpen=$taskOldLinks}
        $taskWord.Quit()
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskWord)
    }
}
