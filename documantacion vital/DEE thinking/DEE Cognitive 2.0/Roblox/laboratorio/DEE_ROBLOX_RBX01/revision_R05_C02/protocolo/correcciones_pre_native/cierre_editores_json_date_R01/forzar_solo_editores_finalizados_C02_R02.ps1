param(
 [switch]$RootRun,
 [Parameter(Mandatory=$true)][string]$Output,
 [string]$HostPython='D:\Descargas\ANACONDA MINICONDA\python.exe'
)
# Root-only release of two finished experimental editors, after graceful close
# explicitly failed. Never targets a Native/launcher/C01/current R02 process.
$ErrorActionPreference='Stop'
if(-not $RootRun){throw 'Explicit RootRun required'}
$campaignRoot=[IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$expectedExe='C:\Users\Erik\AppData\Local\Roblox\Versions\version-63eb6055af4e4688\RobloxStudioBeta.exe'
$protectedPids=@(7252,13064,13416,6596,70963)
$targets=@(
 @{Pid=5392;Start='2026-11-15T05:44:24.639Z';Clone='DEV';File='DEE_RBX01_C02_DEV4.rbxlx';Closure='evidencia\DEV_REAPERTURA_R04\SOURCE_OWNER_CLOSED.json'},
 @{Pid=18244;Start='2026-11-15T05:59:51.988Z';Clone='MAIN';File='DEE_RBX01_C02.rbxlx';Closure='evidencia\MAIN_PERIODO_01\SOURCE_OWNER_CLOSED.json'}
)
function LocalPath([string]$path){
 $p=[IO.Path]::GetFullPath($path)
 if(-not $p.StartsWith($campaignRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Outside R05'}
 $cursor=$p
 while($cursor){
  if(Test-Path -LiteralPath $cursor){if((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse path denied'}}
  $next=[IO.Path]::GetDirectoryName($cursor);if($next -eq $cursor){break};$cursor=$next
 }
 return $p
}
function SaveNew([string]$path,$value){
 if(Test-Path -LiteralPath $path){throw 'Evidence overwrite denied'}
 [IO.File]::WriteAllText($path,($value|ConvertTo-Json -Depth 40)+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))
}
function HostMemory(){
 if(-not ('C02FinishedEditorsMemoryR02' -as [type])){
  Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class C02FinishedEditorsMemoryR02 {
 [StructLayout(LayoutKind.Sequential)]
 public sealed class Status {
  public UInt32 dwLength = (UInt32)Marshal.SizeOf(typeof(Status));
  public UInt32 dwMemoryLoad;
  public UInt64 ullTotalPhys, ullAvailPhys, ullTotalPageFile, ullAvailPageFile;
  public UInt64 ullTotalVirtual, ullAvailVirtual, ullAvailExtendedVirtual;
 }
 [DllImport("kernel32.dll", SetLastError=true)]
 [return: MarshalAs(UnmanagedType.Bool)]
 public static extern bool GlobalMemoryStatusEx([In, Out] Status status);
}
'@
 }
 $m=[C02FinishedEditorsMemoryR02+Status]::new()
 if(-not [C02FinishedEditorsMemoryR02]::GlobalMemoryStatusEx($m)){
  throw ('GlobalMemoryStatusEx unavailable; no invented RAM measurement. Win32='+[Runtime.InteropServices.Marshal]::GetLastWin32Error())
 }
 return @{MeasuredUtc=[DateTime]::UtcNow.ToString('o');FreePhysicalBytes=[int64]$m.ullAvailPhys;TotalPhysicalBytes=[int64]$m.ullTotalPhys;Reader='Win32.GlobalMemoryStatusEx';Scope='HOST_PHYSICAL_RAM_NOT_COGNITIVE_MEMORY'}
}
function ExactProcess($target){
 $p=Get-Process -Id $target.Pid -ErrorAction SilentlyContinue
 if($null -eq $p){return $null}
 if($protectedPids -contains $target.Pid){throw 'Protected PID'}
 if(-not ([IO.Path]::GetFullPath($p.Path)).Equals($expectedExe,[StringComparison]::OrdinalIgnoreCase) -or
    $p.StartTime.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffZ') -ne $target.Start){throw 'PID/executable/start mismatch'}
 return $p
}
$out=LocalPath $Output
if(Test-Path -LiteralPath $out){throw 'Fresh evidence directory required'}
$gracePath=LocalPath (Join-Path $campaignRoot 'evidencia\CIERRE_STUDIOS_FINALIZADOS_R01\RESULTADO_CIERRE_STUDIOS.json')
$grace=Get-Content -LiteralPath $gracePath -Raw -Encoding UTF8|ConvertFrom-Json
if($grace.Schema -ne 'DEE.RBX01.C02.finished_Studio_graceful_close.R01' -or $grace.ForcedTerminations -ne 0){throw 'Wrong graceful close proof'}
$validated=@();$frozen=@()
foreach($target in $targets){
 $row=@($grace.Targets|Where-Object {$_.Pid -eq $target.Pid})
 if($row.Count -ne 1 -or $row[0].ExpectedStartUtc -ne $target.Start -or $row[0].CloseMainWindowReturned -ne $false -or $row[0].ForceKill -ne $false){throw 'Exact earlier graceful failure missing'}
 $proofPath=LocalPath (Join-Path $campaignRoot $target.Closure)
 $proof=Get-Content -LiteralPath $proofPath -Raw -Encoding UTF8|ConvertFrom-Json
 if($proof.ownerClosed -ne $true -or $proof.writerDrained -ne $true -or $proof.source_journal_event.exit_code -ne 0 -or $proof.source_journal_event.final_status.running -ne $false){throw 'No drained Native close proof'}
 if((Get-FileHash -LiteralPath $proofPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $row[0].NativeClosed.ClosureSha256){throw 'Closure proof changed'}
 $destination=LocalPath (Join-Path $campaignRoot ('native\'+$target.Clone))
 $raw=& $HostPython -I -B (Join-Path $PSScriptRoot 'monitor_solo_lectura_C02.py') --destination $destination
 if($LASTEXITCODE -ne 0){throw 'Readonly clone monitor failed'}
 $state=($raw -join [Environment]::NewLine)|ConvertFrom-Json
 if($state.owner_cached.running -ne $false -or $state.owner_cached.uncertain_external_result -ne $false -or @($state.pending_requests).Count -ne 0 -or $state.life_id -ne $proof.lifeId){throw 'Live/uncertain old Native clone'}
 # The closed cache is necessary but not an instantaneous liveness proof.
 # Conservatively reject even PID reuse; Root may inspect that ambiguity.
 if($null -ne $state.owner_cached.pid -and $null -ne (Get-Process -Id ([int]$state.owner_cached.pid) -ErrorAction SilentlyContinue)){
  throw 'Cached old Native owner PID still exists; preserve the editor and reconcile identity first'
 }
 if(Test-Path -LiteralPath (Join-Path $destination ('sistema\estado\locks\'+$state.life_id+'.lock'))){throw 'Old clone lock exists'}
 $scenePath=LocalPath (Join-Path $campaignRoot ('mundo\'+$target.File))
 if(-not (Test-Path -LiteralPath $scenePath -PathType Leaf)){throw 'Saved old scene unavailable'}
 $frozen+=@{Path=$scenePath;Sha256=(Get-FileHash -LiteralPath $scenePath -Algorithm SHA256).Hash.ToLowerInvariant()}
 $validated+=@{Target=$target;Process=(ExactProcess $target);NativeClosed=$proofPath;Tick=$state.owner_cached.tick}
}
# Preserve current on-disk experimental source hashes. Unsaved DEV controller
# disabling was temporary instrumentation already recorded by Root, not new data.
foreach($name in @('Config_C02.luau','Body_C02.luau','Controller_C02.server.luau','EstadoPareja_C02.luau','Bridge_mailbox_C02.luau')){
 $path=LocalPath (Join-Path $campaignRoot ('mundo\'+$name))
 if(Test-Path -LiteralPath $path -PathType Leaf){$frozen+=@{Path=$path;Sha256=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}}
}
New-Item -ItemType Directory -Path $out|Out-Null
$report=@{Schema='DEE.RBX01.C02.finished_editor_force_close.R02';StartedUtc=[DateTime]::UtcNow.ToString('o');MemoryBefore=(HostMemory);GracefulProof=$gracePath;GracefulProofSha256=(Get-FileHash -LiteralPath $gracePath -Algorithm SHA256).Hash.ToLowerInvariant();ProtectedPids=$protectedPids;FrozenFiles=$frozen;Targets=@();NativeProcessesStopped=0;NativeActions=0;NoSaveOrSourceOverwrite=$true;Scope='Root confirmed both exact old editors Edit, all scientific state preserved. Only these two editor processes may be stopped.'}
SaveNew (Join-Path $out 'INTENCION_FORZAR_EDITORES.json') $report
foreach($entry in $validated){
 $p=ExactProcess $entry.Target
 $row=@{Pid=$entry.Target.Pid;ExpectedStartUtc=$entry.Target.Start;SavedScene=$entry.Target.File;NativeTick=$entry.Tick;NativeClosed=$entry.NativeClosed;StopAttempted=$false}
 if($null -eq $p){$row.Status='ALREADY_EXITED';$row.Exited=$true}
 else{
  $row.StopAttempted=$true
  Stop-Process -Id $entry.Target.Pid -ErrorAction Stop
  $row.Exited=$p.WaitForExit(15000)
  $row.Status=if($row.Exited){'EXACT_FINISHED_EDITOR_STOPPED'}else{'EXIT_NOT_CONFIRMED_NO_RETRY'}
 }
 $report.Targets+=$row;SaveNew (Join-Path $out ('PID_'+$entry.Target.Pid+'.json')) $row
}
foreach($item in $frozen){if((Get-FileHash -LiteralPath $item.Path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $item.Sha256){throw 'Saved experimental file changed; evidence preserved'}}
$report.FrozenFilesUnchanged=$true;$report.MemoryAfter=HostMemory
$report.MeasuredFreePhysicalBytesDifference=$report.MemoryAfter.FreePhysicalBytes-$report.MemoryBefore.FreePhysicalBytes
$report.MemoryDifferenceIsHostMeasurementNotCausalAttribution=$true
$report.FinishedUtc=[DateTime]::UtcNow.ToString('o')
SaveNew (Join-Path $out 'RESULTADO_FORZAR_EDITORES.json') $report
$report|ConvertTo-Json -Depth 40
