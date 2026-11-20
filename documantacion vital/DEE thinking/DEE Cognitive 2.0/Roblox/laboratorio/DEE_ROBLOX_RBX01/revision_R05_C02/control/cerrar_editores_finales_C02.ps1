param(
 [switch]$RootRun,
 [switch]$Force,
 [Parameter(Mandatory=$true)][string]$EditProof,
 [Parameter(Mandatory=$true)][string]$Output,
 [string]$HostPython='D:\Descargas\ANACONDA MINICONDA\python.exe'
)
# FUTURE ONLY: both exact R02 editors must have all18 worlds/owners closed.
# No Native, Play, model, account/security, Save, file deletion or GUI launch.
# Force permits ONLY the same exact editor after CloseMainWindow returns false.
$ErrorActionPreference='Stop'
if(-not $RootRun){throw 'Explicit -RootRun required; no process touched'}
$campaignRoot=[IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$expectedExe='C:\Users\Erik\AppData\Local\Roblox\Versions\version-63eb6055af4e4688\RobloxStudioBeta.exe'
$targets=@(
 @{Pid=13064;File='DEE_RBX01_C02_R02.rbxlx';CreationFileTime=[int64]134392045744396167},
 @{Pid=7820;File='DEE_RBX01_C02_R02_PROGRAMMED.rbxlx';CreationFileTime=[int64]134392069521419811}
)
function LocalPath([string]$path){
 if(-not [IO.Path]::IsPathRooted($path)){$path=Join-Path $campaignRoot $path}
 $p=[IO.Path]::GetFullPath($path)
 if(-not $p.StartsWith($campaignRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'R05 paths only'}
 $cursor=$p
 while($cursor){
  if(Test-Path -LiteralPath $cursor){if((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse path denied'}}
  $next=[IO.Path]::GetDirectoryName($cursor);if($next -eq $cursor){break};$cursor=$next
 }
 return $p
}
function ReadJson([string]$path){
 $raw=[IO.File]::ReadAllText($path)
 if((Get-Command ConvertFrom-Json).Parameters.ContainsKey('DateKind')){return ConvertFrom-Json -InputObject $raw -DateKind String}
 return ConvertFrom-Json -InputObject $raw
}
function SaveNew([string]$path,$value){
 if(Test-Path -LiteralPath $path){throw 'Evidence overwrite denied'}
 [IO.File]::WriteAllText($path,($value|ConvertTo-Json -Depth 40)+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))
}
function Memory(){
 if(-not('C02FinalEditorsMemoryR01' -as [type])){
  Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class C02FinalEditorsMemoryR01 {
 [StructLayout(LayoutKind.Sequential)] public sealed class Status {
  public UInt32 dwLength=(UInt32)Marshal.SizeOf(typeof(Status));public UInt32 dwMemoryLoad;
  public UInt64 ullTotalPhys,ullAvailPhys,ullTotalPageFile,ullAvailPageFile,ullTotalVirtual,ullAvailVirtual,ullAvailExtendedVirtual;
 }
 [DllImport("kernel32.dll",SetLastError=true)]
 [return:MarshalAs(UnmanagedType.Bool)]public static extern bool GlobalMemoryStatusEx([In,Out]Status status);
}
'@
 }
 $m=[C02FinalEditorsMemoryR01+Status]::new()
 if(-not[C02FinalEditorsMemoryR01]::GlobalMemoryStatusEx($m)){throw 'Win32 physical memory measurement unavailable'}
 return @{MeasuredUtc=[DateTime]::UtcNow.ToString('o');FreePhysicalBytes=[int64]$m.ullAvailPhys;TotalPhysicalBytes=[int64]$m.ullTotalPhys;Reader='Win32.GlobalMemoryStatusEx';Scope='HOST_RAM_NOT_COGNITIVE_MEMORY'}
}
function ExactProcess($target){
 if($target.Pid -notin @(13064,7820) -or $target.Pid -eq 7252){throw 'Only two finished editor PIDs are allowed'}
 $p=Get-Process -Id $target.Pid -ErrorAction SilentlyContinue
 if($null -eq $p){return $null}
 if(-not([IO.Path]::GetFullPath($p.Path)).Equals($expectedExe,[StringComparison]::OrdinalIgnoreCase) -or
    $p.StartTime.ToUniversalTime().ToFileTimeUtc() -ne $target.CreationFileTime){throw 'Exact editor executable/creation identity mismatch'}
 return $p
}
$editPath=LocalPath $EditProof;$out=LocalPath $Output
if(Test-Path -LiteralPath $out){throw 'New evidence directory required'}
if(-not(Test-Path -LiteralPath $editPath -PathType Leaf)){throw 'Recent Root MCP Edit marker required'}
$validator=Join-Path $PSScriptRoot 'verificar_editores_finales_C02.py'
$raw=& $HostPython -I -B $validator --root-run --edit-proof $editPath
if($LASTEXITCODE -ne 0){throw 'Final18 scientific/owner preconditions failed; no editor was touched'}
$rawText=$raw -join [Environment]::NewLine
$proof=if((Get-Command ConvertFrom-Json).Parameters.ContainsKey('DateKind')){ConvertFrom-Json -InputObject $rawText -DateKind String}else{ConvertFrom-Json -InputObject $rawText}
if($proof.all18_closed_and_exported -ne $true){throw 'Final18 readiness absent'}
$openedPath=LocalPath 'evidencia\APERTURA_PROGRAMMED_C02_R01_RESULTADO.json'
$opened=ReadJson $openedPath
if($opened.opened_process.pid -ne 7820 -or [int64]$opened.opened_process.creation_filetime -ne [int64]134392069521419811){throw 'Original PROGRAMMED launch record mismatch'}
if((Get-FileHash -LiteralPath $expectedExe -Algorithm SHA256).Hash.ToLowerInvariant() -ne $opened.Studio_sha256){throw 'Official Studio bytes changed'}
# Validate BOTH editor identities before any close request. Any AI/C01/Native
# process is outside this literal allowlist and is never enumerated for closing.
$validated=@()
foreach($target in $targets){$p=ExactProcess $target;$validated+=@{Target=$target;Process=$p}}
New-Item -ItemType Directory -Path $out|Out-Null
$report=@{Schema='DEE.RBX01.C02.final_editors_close.R01';StartedUtc=[DateTime]::UtcNow.ToString('o');ForceFlag=[bool]$Force;MemoryBefore=(Memory);Preconditions=$proof;Targets=@();ProtectedC01Pid=7252;AnyAIProtected=$true;NativeCloseCalls=0;SaveCalls=0;FilesDeleted=0}
SaveNew (Join-Path $out 'ANTES_CIERRE_EDITORES.json') $report
foreach($entry in $validated){
 $p=ExactProcess $entry.Target
 $row=@{Pid=$entry.Target.Pid;ExpectedFile=$entry.Target.File;ExpectedCreationFileTime=$entry.Target.CreationFileTime;StopProcessAttempted=$false}
 if($null -eq $p){$row.Status='ALREADY_EXITED_NO_ACTION';$row.Exited=$true}
 else{
  $row.ActualStartUtc=$p.StartTime.ToUniversalTime().ToString('o');$row.ActualCreationFileTime=$p.StartTime.ToUniversalTime().ToFileTimeUtc()
  $row.CloseMainWindowReturned=$p.CloseMainWindow()
  if($row.CloseMainWindowReturned){$row.Exited=$p.WaitForExit(15000);$row.Status=if($row.Exited){'GRACEFULLY_EXITED'}else{'GRACEFUL_OR_SAVE_DIALOG_PENDING_NO_FORCE'}}
  elseif($Force){
   $p=ExactProcess $entry.Target
   if($null -eq $p){$row.Exited=$true;$row.Status='EXITED_BEFORE_FORCE'}
   else{$row.StopProcessAttempted=$true;Stop-Process -Id $entry.Target.Pid -ErrorAction Stop;$row.Exited=$p.WaitForExit(15000);$row.Status=if($row.Exited){'EXACT_FINISHED_EDITOR_STOPPED_AFTER_FALSE_CLOSE'}else{'EXIT_UNCONFIRMED_NO_RETRY'}}
  }else{$row.Exited=$false;$row.Status='CLOSE_FALSE_PRESERVED_WITHOUT_FORCE_FLAG'}
 }
 $report.Targets+=$row;SaveNew (Join-Path $out ('PID_'+$entry.Target.Pid+'.json')) $row
}
foreach($item in $proof.preserved_hashes.PSObject.Properties){if((Get-FileHash -LiteralPath $item.Name -Algorithm SHA256).Hash.ToLowerInvariant() -ne $item.Value){throw 'Scientific evidence/scene changed during editor close; evidence preserved'}}
$report.PreservedEvidenceAndScenesUnchanged=$true;$report.MemoryAfter=Memory
$report.MeasuredFreePhysicalBytesDifference=$report.MemoryAfter.FreePhysicalBytes-$report.MemoryBefore.FreePhysicalBytes
$report.MemoryDifferenceIsHostMeasurementNotCausalProof=$true;$report.FinishedUtc=[DateTime]::UtcNow.ToString('o')
SaveNew (Join-Path $out 'RESULTADO_CIERRE_EDITORES_FINALES.json') $report
$report|ConvertTo-Json -Depth 40
