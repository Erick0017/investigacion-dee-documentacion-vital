param(
    [Parameter(Mandatory=$true)][string]$Docx,
    [Parameter(Mandatory=$true)][string]$Proof,
    [switch]$Ejecutar,
    [switch]$RenderAllPages,
    [int[]]$RenderPages=@(),
    [ValidateRange(72,150)][int]$Dpi=100,
    [string]$ShortWorkDirectory=''
)
# ROOT ONLY. Preparation/default PLAN never activates Word or authors a DOCX.
# Run under a separate Root supervisor limited to120s. On timeout the witness
# identifies only a genuinely new owned WINWORD PID; never stop old10732.
$ErrorActionPreference='Stop'
$P7=[IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$Workspace=[IO.Path]::GetFullPath((Get-Item -LiteralPath $P7).Parent.Parent.Parent.Parent.Parent.FullName)
$Docs=Join-Path $P7 'documentos'
$InputPath=[IO.Path]::GetFullPath($Docx)
$ProofPath=[IO.Path]::GetFullPath($Proof)
$AllowedNames=@('DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx','COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx')

function Require([bool]$Value,[string]$Message){if(-not $Value){throw $Message}}
function Within([string]$Path,[string]$Root){
    $a=[IO.Path]::GetFullPath($Path);$b=[IO.Path]::GetFullPath($Root).TrimEnd('\')
    return $a.StartsWith($b+'\',[StringComparison]::OrdinalIgnoreCase)
}
function Check-NoReparse([string]$Path){
    $p=[IO.Path]::GetFullPath($Path)
    while($p -and ((Within $p $Workspace) -or $p -eq $Workspace)){
        if(Test-Path -LiteralPath $p){
            $item=Get-Item -Force -LiteralPath $p
            Require (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) ('Reparse path refused: '+$p)
        }
        if($p -eq $Workspace){break};$p=Split-Path -Parent $p
    }
}
function File-Info([string]$Path){
    $i=Get-Item -LiteralPath $Path
    return [ordered]@{path=$i.FullName;bytes=$i.Length;sha256=(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()}
}

Require (Within $InputPath $Docs) 'Only PI07 staged documents may be opened'
Require (($AllowedNames -contains [IO.Path]::GetFileName($InputPath))) 'Unexpected staged DOCX filename'
$InputParent=Split-Path -Leaf (Split-Path -Parent $InputPath)
Require ($InputParent.StartsWith('staging_1_34_',[StringComparison]::Ordinal)) 'A literal1.34 staging directory is required'
Require (Within $ProofPath $Docs) 'Witness must remain inside PI07/documentos'
Require ([IO.Path]::GetExtension($ProofPath) -eq '.json') 'JSON witness required'
Require (-not ($RenderAllPages -and $RenderPages.Count -gt 0)) 'Choose all or explicit pages'
if(-not $Ejecutar){
    [ordered]@{mode='READ_ONLY_PLAN_NO_COM_NO_DOCX_AUTHORING';input=$InputPath;proof=$ProofPath;Native_ticks=0;supervisor_seconds=120;requires='Root marker/authoring and all Native closure precede execution';old_WINWORD_must_not_be_quit=10732}|ConvertTo-Json -Depth 8
    return
}

Check-NoReparse $InputPath;Check-NoReparse $ProofPath
Require (Test-Path -LiteralPath $InputPath -PathType Leaf) 'Staged DOCX missing'
Require (-not (Test-Path -LiteralPath $ProofPath)) 'Witness already exists'
Require (-not (Test-Path -LiteralPath ($ProofPath+'.writing'))) 'Prior witness partial exists'
$Source=File-Info $InputPath
if(-not $ShortWorkDirectory){$ShortWorkDirectory=Join-Path $Workspace ('PI07_WORDQA_'+[DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss')+'_'+[Guid]::NewGuid().ToString('N').Substring(0,8))}
$ShortRoot=[IO.Path]::GetFullPath($ShortWorkDirectory)
Require (Within $ShortRoot $Workspace) 'QA directory outside workspace'
Require ((Split-Path -Leaf $ShortRoot).StartsWith('PI07_WORDQA_',[StringComparison]::Ordinal)) 'Explicit short QA prefix required'
Require (-not (Test-Path -LiteralPath $ShortRoot)) 'Fresh QA directory required'
Check-NoReparse $ShortRoot
New-Item -ItemType Directory -Path $ShortRoot|Out-Null
$QAInput=Join-Path $ShortRoot 'input.docx';$PDF=Join-Path $ShortRoot 'document.pdf'
Require ($QAInput.Length -lt 210 -and $PDF.Length -lt 210) 'Word short-path budget exceeded'
[IO.File]::Copy($InputPath,$QAInput,$false)
Require ((File-Info $QAInput).sha256 -eq $Source.sha256) 'Literal short QA copy differs'
(Get-Item -LiteralPath $QAInput).IsReadOnly=$true
$Before=@(Get-Process -Name WINWORD -ErrorAction SilentlyContinue|ForEach-Object{$_.Id})
$Witness=[ordered]@{schema='DEE.PI07.Word_isolated_readonly_export.R01';status='STARTED';stage='BEFORE_COM';started_utc=[DateTime]::UtcNow.ToString('o');supervisor_deadline_utc=[DateTime]::UtcNow.AddSeconds(120).ToString('o');source_staged=$Source;short_work_directory=$ShortRoot;literal_QA_copy=$QAInput;original_WINWORD_PIDs=$Before;protected_unowned_PID=10732;owned_word_PID=$null;owned_process_start_utc=$null;owned_HWND=$null;Native_ticks=0;DOCX_authoring_performed=$false;visual_review_performed=$false;cleanup_performed=$false;source_original_unchanged=$null}
function Save-Witness{
    $json=$script:Witness|ConvertTo-Json -Depth 20
    $temporary=$script:ProofPath+'.writing'
    [IO.File]::WriteAllText($temporary,$json+"`n",[Text.UTF8Encoding]::new($false))
    Move-Item -Force -LiteralPath $temporary -Destination $script:ProofPath
}
Save-Witness
$Word=$null;$Document=$null;$Owned=$false;$OwnedPID=$null;$OwnedStartTicks=$null
function Own-Identity-Still-Matches{
    if(-not $script:Owned){return $false}
    $current=Get-Process -Id $script:OwnedPID -ErrorAction SilentlyContinue
    if($null -eq $current){return $false}
    try{return $current.ProcessName -eq 'WINWORD' -and $current.StartTime.ToUniversalTime().Ticks -eq $script:OwnedStartTicks}catch{return $false}
}
try{
    if(-not ('PI07WordWindowIdentity' -as [type])){
        Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public static class PI07WordWindowIdentity { [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId); }'
    }
    $Word=New-Object -ComObject Word.Application
    # Do not set a property, close a document, or Quit until HWND proves ownership.
    $hwnd=[IntPtr]$Word.Hwnd;[uint32]$wpid=0
    [void][PI07WordWindowIdentity]::GetWindowThreadProcessId($hwnd,[ref]$wpid)
    Require ($wpid -gt 0 -and $wpid -ne 10732 -and $Before -notcontains [int]$wpid) 'Activation returned an existing/unowned Word PID; no properties or Quit permitted'
    $process=Get-Process -Id $wpid
    Require ($process.ProcessName -eq 'WINWORD') 'HWND is not WINWORD'
    $Owned=$true;$OwnedPID=[int]$wpid;$OwnedStartTicks=$process.StartTime.ToUniversalTime().Ticks
    $Witness.owned_word_PID=$OwnedPID;$Witness.owned_process_start_utc=$process.StartTime.ToUniversalTime().ToString('o');$Witness.owned_HWND=$hwnd.ToInt64();$Witness.stage='OWNERSHIP_PROVEN_BEFORE_OPEN';Save-Witness
    $Word.Visible=$false;$Word.DisplayAlerts=0;$Word.AutomationSecurity=3;$Word.ScreenUpdating=$false
    $Word.Options.UpdateLinksAtOpen=$false;$Word.Options.SaveNormalPrompt=$false
    $Witness.stage='OPENING_LITERAL_STAGED_COPY_READONLY';Save-Witness
    $Document=$Word.Documents.Open($QAInput,$false,$true,$false)
    Require ($Document.ReadOnly -eq $true) 'Word did not open the QA copy read-only'
    Require (Own-Identity-Still-Matches) 'Owned Word identity changed before export'
    $Witness.stage='EXPORTING_FULL_DOCUMENT_PDF';Save-Witness
    # PDF17; entire document; content only; no open-after-export; headings bookmarks.
    $Document.ExportAsFixedFormat($PDF,17,$false,0,0,1,1,0,$false,$false,1,$true,$true,$false)
    Require (Test-Path -LiteralPath $PDF -PathType Leaf) 'Word returned without a PDF'
    Require ((Get-Item -LiteralPath $PDF).Length -gt 0) 'Empty PDF'
    $Witness.PDF=File-Info $PDF;$Witness.stage='PDF_EXPORTED';Save-Witness
    $Document.Close(0);[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($Document);$Document=$null
    if(Own-Identity-Still-Matches){$Word.Quit(0);$Witness.owned_Quit_requested=$true}
    [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($Word)
    $Word=$null
    $pdfinfo=Get-Command pdfinfo.exe -ErrorAction SilentlyContinue
    if($null -eq $pdfinfo){$pdfinfo=Get-Command pdfinfo -ErrorAction SilentlyContinue}
    Require ($null -ne $pdfinfo) 'PDF exported; Poppler pdfinfo unavailable'
    $infoText=(& $pdfinfo.Source $PDF 2>&1|Out-String);$exit=$LASTEXITCODE
    Require ($exit -eq 0) ('pdfinfo failed: '+$infoText)
    $match=[regex]::Match($infoText,'(?m)^Pages:\s*(\d+)\s*$')
    Require $match.Success 'pdfinfo did not report page count'
    $Count=[int]$match.Groups[1].Value;Require ($Count -gt 0) 'PDF has no pages'
    $Witness.page_count=$Count;$Witness.pdfinfo_executable=$pdfinfo.Source
    $Witness.pdfinfo_output=$infoText;$PNGs=@()
    if($RenderAllPages -or $RenderPages.Count -gt 0){
        $ppm=Get-Command pdftoppm.exe -ErrorAction SilentlyContinue
        if($null -eq $ppm){$ppm=Get-Command pdftoppm -ErrorAction SilentlyContinue}
        Require ($null -ne $ppm) 'pdftoppm unavailable'
        $pages=if($RenderAllPages){@(1..$Count)}else{@($RenderPages|Sort-Object -Unique)}
        foreach($page in $pages){
            Require ($page -ge 1 -and $page -le $Count) 'Requested page outside actual PDF'
            $prefix=Join-Path $ShortRoot ('page_'+$page.ToString('D4'))
            & $ppm.Source -f $page -l $page -singlefile -png -r $Dpi $PDF $prefix 2>&1|Out-Null
            Require ($LASTEXITCODE -eq 0) ('pdftoppm failed on page'+$page)
            $image=$prefix+'.png';Require (Test-Path -LiteralPath $image -PathType Leaf) 'PNG missing'
            $PNGs+=([ordered]@{page=$page;file=(File-Info $image)})
        }
        $Witness.pdftoppm_executable=$ppm.Source
    }
    $Witness.PNGs=$PNGs;$Witness.rendered_page_count=$PNGs.Count
    $Witness.all_pages_rendered=($PNGs.Count -eq $Count)
    $Witness.status='EXPORTED_PDF_AND_METADATA_VERIFIED';$Witness.stage='COMPLETE'
}catch{
    $Witness.status='FAILED_PRESERVED';$Witness.error_type=$_.Exception.GetType().FullName
    $Witness.error_message=$_.Exception.Message;$Witness.error_hresult=$_.Exception.HResult
}finally{
    if($Document -and (Own-Identity-Still-Matches)){
        try{$Document.Close(0)}catch{$Witness.close_error=$_.Exception.Message}
    }
    if($Word -and (Own-Identity-Still-Matches)){
        try{$Word.Quit(0);$Witness.owned_Quit_requested=$true}catch{$Witness.quit_error=$_.Exception.Message}
    }
    if($Document){try{[void][Runtime.InteropServices.Marshal]::ReleaseComObject($Document)}catch{}}
    if($Word){try{[void][Runtime.InteropServices.Marshal]::ReleaseComObject($Word)}catch{}}
    $Witness.finished_utc=[DateTime]::UtcNow.ToString('o')
    $Witness.owned_word_process_exit_observed=($Owned -and $null -eq (Get-Process -Id $OwnedPID -ErrorAction SilentlyContinue))
    $Witness.source_original_unchanged=((File-Info $InputPath).sha256 -eq $Source.sha256)
    $Witness.short_copy_unchanged=((File-Info $QAInput).sha256 -eq $Source.sha256)
    $Witness.generated_short_path_bytes=(@(Get-ChildItem -File -LiteralPath $ShortRoot)|Measure-Object -Property Length -Sum).Sum
    $Witness.short_QA_directory_must_be_counted_in_campaign_storage=$true
    $Witness.visual_review_performed=$false # Root must actually inspect the rendered pages.
    Save-Witness
}
$Witness|ConvertTo-Json -Depth 20
if($Witness.status -eq 'FAILED_PRESERVED'){exit 1}
