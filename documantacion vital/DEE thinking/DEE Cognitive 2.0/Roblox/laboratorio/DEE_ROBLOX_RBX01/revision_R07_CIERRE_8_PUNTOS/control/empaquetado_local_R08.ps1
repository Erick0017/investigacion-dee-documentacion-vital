$ErrorActionPreference='Stop'
$ActualBuilderPath=$PSCommandPath
$Root=[IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$Utf8=[Text.UTF8Encoding]::new($false,$true)
$Checked=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$Progress=Join-Path $Root 'control/PROGRESO_EMPAQUETADO_LOCAL_R08.jsonl'
$OriginalPath=Join-Path $Root 'control/empaquetado_local_R07.ps1'
$OriginalText=[IO.File]::ReadAllText($OriginalPath,$Utf8)
$FunctionStart=$OriginalText.IndexOf('function Mark(')
$FunctionEnd=$OriginalText.IndexOf("if ([IO.File]::Exists(`$Progress))")
if($FunctionStart -lt 0 -or $FunctionEnd -le $FunctionStart){throw 'HELPER_BOUNDARY'}
. ([ScriptBlock]::Create($OriginalText.Substring($FunctionStart,$FunctionEnd-$FunctionStart)))
if([IO.File]::Exists($Progress)){throw 'FRESH_RESUME_PROGRESS_REQUIRED'}
Mark 'START_RESUME' 'Reuse completed533-file scan; only resolve privacy alerts, preserve originals.'
$PlanPin='2074ad154d9532c5ed796d10cd727ffdd97b1b90dda88eebc7c97e4d0f01079d'
$PlanPath=Join-Path $Root 'control/PLAN_FINAL_R07_PREPRIVACIDAD.json'
$PlanBytes=ReadStable $PlanPath
if((Digest $PlanBytes) -ne $PlanPin){throw 'PLAN_PIN'}
$Plan=$Utf8.GetString($PlanBytes)|ConvertFrom-Json
$OldPrivacyPath=Join-Path $Root 'analisis/REVISION_PRIVACIDAD_LOCAL_R07.json'
$OldBytes=ReadStable $OldPrivacyPath
$Old=$Utf8.GetString($OldBytes)|ConvertFrom-Json
if($Old.plan_sha256 -ne $PlanPin -or $Old.source_members -ne 533){throw 'PRIOR_COMPLETED_SCAN_REQUIRED'}
$OldSelf=@($Old.coverage|Where-Object{$_.archive -eq 'CONTROL/empaquetado_local_R07.ps1'})
if($OldSelf.Count -ne 1 -or (Digest (ReadStable $OriginalPath)) -ne $OldSelf[0].sha256){throw 'ORIGINAL_HELPER_PIN'}
$Omit=@('control/CUA_MAIN_R07_ACTIVACION_UNICA_R02.json','pruebas/privacy_incremental_R08_test.py')
$Omitted=@($Old.coverage|Where-Object{$_.archive -in $Omit}|ForEach-Object{@{archive=$_.archive;source=$_.source;bytes=$_.bytes;sha256=$_.sha256;retained_locally=$true;reason='Nonessential authorization audit or email-test fixture; omitted conservatively, not classified as an actual exposed credential.'}})
$CachePath=Join-Path $Root 'analisis/REVISION_PRIVACIDAD_PLAN_R03.json'
$CacheBytes=ReadStable $CachePath
if((Digest $CacheBytes)-ne '1995ad8cec29cec7a324616457579cec11b33d618f06010fa55dd45d143763ca'){throw 'CACHE_PIN'}
$Cache=$Utf8.GetString($CacheBytes)|ConvertFrom-Json
if(@($Cache.findings).Count){throw 'CACHE_NOT_CLEAN'}
$Cached=@{};foreach($Row in $Cache.coverage){$Cached[$Row.source.ToLowerInvariant()+'|'+$Row.sha256+'|'+$Row.bytes]=$true}
Add-Type -TypeDefinition @'
using System;
using System.Collections;
using System.Collections.Generic;
public static class R07SensitiveKeys {
 static HashSet<string> K = new HashSet<string>(StringComparer.OrdinalIgnoreCase){"password","passwd","access_token","refresh_token","authorization","cookie","set-cookie","api_key","apikey","client_secret","private_key",".roblosecurity","roblosecurity"};
 public static List<string> Find(object root) { var r=new List<string>(); Walk(root,"",r);return r; }
 static void Walk(object v,string p,List<string> r) {
  if(v is IDictionary) { foreach(DictionaryEntry e in (IDictionary)v) { string k=Convert.ToString(e.Key),q=p+"/"+k; if(K.Contains(k) && e.Value is string && !String.IsNullOrWhiteSpace((string)e.Value))r.Add(q); if(e.Value is IDictionary || (e.Value is IEnumerable && !(e.Value is string)))Walk(e.Value,q,r); } }
  else if(v is IEnumerable && !(v is string)) { int i=0;foreach(object x in (IEnumerable)v){if(x is IDictionary || (x is IEnumerable && !(x is string)))Walk(x,p+"/"+i,r);i++;} }
 }
}
'@
$LinearOptions=[Text.RegularExpressions.RegexOptions]::NonBacktracking -bor [Text.RegularExpressions.RegexOptions]::IgnoreCase
$Patterns=@('-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----','\bBearer\s+[A-Za-z0-9._~+/-]{16,}','\.ROBLOSECURITY\s*[:=]\s*[^\s]{24,}')
$Resolved=[Collections.Generic.List[object]]::new()
foreach($Alert in $Old.findings){
 if($Alert.archive -in $Omit){continue}
 if($Alert.kind -ne 'PRIVACY_REGEX_TIMEOUT_REQUIRES_REVIEW'){throw 'UNRESOLVED_ALERT_KIND'}
 $Row=@($Old.coverage|Where-Object{$_.archive -eq $Alert.archive})
 if($Row.Count -ne 1){throw 'ALERT_SOURCE'};$Row=$Row[0]
 $Bytes=ReadStable $Row.source
 if((Digest $Bytes)-ne $Row.sha256){throw 'ALERT_SOURCE_CHANGED'}
 $Key=$Row.source.ToLowerInvariant()+'|'+$Row.sha256+'|'+$Row.bytes
 if($Cached.ContainsKey($Key)){$Resolved.Add(@{archive=$Alert.archive;method='REUSE_EXACT_HASH_SOURCE_AND_BYTES_R03';candidates=0});continue}
 Mark 'LINEAR_ALERT_REVIEW' $Alert.archive
 $Text=$Utf8.GetString($Bytes).TrimStart([char]0xFEFF)
 foreach($Pattern in $Patterns){if([regex]::IsMatch($Text,$Pattern,$LinearOptions,[TimeSpan]::FromSeconds(20))){throw ('PRIVACY_LITERAL_REQUIRES_REVIEW: '+$Alert.archive)}}
 $Found=[Collections.Generic.List[string]]::new()
 if($Alert.archive.EndsWith('.json')){$Obj=ConvertFrom-Json -InputObject $Text -AsHashtable -Depth 100;foreach($Key in [R07SensitiveKeys]::Find($Obj)){$Found.Add($Key)}}
 elseif($Alert.archive.EndsWith('.jsonl')){foreach($Line in ($Text -split '\r?\n')){if($Line.Trim()){$Obj=ConvertFrom-Json -InputObject $Line -AsHashtable -Depth 100;foreach($Key in [R07SensitiveKeys]::Find($Obj)){$Found.Add($Key)}}}}
 if($Found.Count){throw ('PRIVACY_KEY_REQUIRES_REVIEW: '+$Alert.archive)}
 $Resolved.Add(@{archive=$Alert.archive;method='LINEAR_NONBACKTRACKING_LITERALS_AND_STRUCTURED_KEYS';candidates=0;email_check='Previously completed bounded email scan retained.'})
}
$Entries=[Collections.Generic.List[object]]::new();$Records=[Collections.Generic.List[object]]::new();$Coverage=[Collections.Generic.List[object]]::new()
$Names=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
foreach($Row in $Old.coverage){
 if($Row.archive -in $Omit){continue};SafeName $Row.archive
 if(-not $Names.Add($Row.archive)){throw 'COLLISION'}
 $Bytes=ReadStable $Row.source
 if($Bytes.Length -ne $Row.bytes -or (Digest $Bytes) -ne $Row.sha256){throw 'FROZEN_SOURCE_CHANGED'}
 $Def=@($Plan.files|Where-Object{$_.archive -eq $Row.archive})
 if($Def.Count -eq 0 -and $Row.archive -eq 'CONTROL/empaquetado_local_R07.ps1'){$Def=@([pscustomobject]@{role='code';max_bytes=2000000})}
 if($Def.Count -ne 1){throw 'SOURCE_DEFINITION'}
 $Record=@{archive=$Row.archive;source=$Row.source;role=$Def[0].role;bytes=$Bytes.Length;sha256=$Row.sha256}
 if($Def[0].max_bytes -gt 2000000){$Record.max_bytes=$Def[0].max_bytes}
 $Entries.Add(@{archive=$Row.archive;raw=$Bytes});$Records.Add($Record);$Coverage.Add($Row)
}
$SelfBytes=ReadStable $ActualBuilderPath
$SelfRow=@{archive='CONTROL/empaquetado_local_R08.ps1';source=$ActualBuilderPath;role='code';bytes=$SelfBytes.Length;sha256=(Digest $SelfBytes)}
$Entries.Add(@{archive=$SelfRow.archive;raw=$SelfBytes});$Records.Add($SelfRow);$Coverage.Add($SelfRow)
$Entries.Add(@{archive='CONTROL/PRIVACIDAD_PREVIA_ALERTAS_R07.json';raw=$OldBytes});$Records.Add(@{archive='CONTROL/PRIVACIDAD_PREVIA_ALERTAS_R07.json';source=$OldPrivacyPath;role='verification';bytes=$OldBytes.Length;sha256=(Digest $OldBytes)})
$Privacy=@{schema='DEE.R07.privacy_resumed_incremental.R08';utc=[DateTime]::UtcNow.ToString('o');original_completed_scan=$OldPrivacyPath;original_scan_sha256=(Digest $OldBytes);plan_sha256=$PlanPin;prior_scanned=533;resolved_alerts=@($Resolved.ToArray());conservative_omissions=$Omitted;remaining_candidates=0;omitted_files_preserved_locally=$true;generated_builder='Known authored file-only source, no credentials embedded.';scope='Reuse completed checks; linear review only for unresolved timeouts, exact-byte hashes rechecked. No secret values printed.'}
$PrivacyPath=Join-Path $Root 'analisis/REVISION_PRIVACIDAD_LOCAL_R08.json';$PrivacyBytes=JsonBytes $Privacy;WriteNew $PrivacyPath $PrivacyBytes
Mark 'PRIVACY_RESOLVED' @{sources=$Coverage.Count;omitted=$Omitted.Count;alerts_resolved=$Resolved.Count}
$TailStart=$OriginalText.IndexOf('$Protection=Protect;$ProtectionBytes=JsonBytes $Protection')
if($TailStart -lt 0){throw 'PACKAGING_TAIL_BOUNDARY'}
$Tail=$OriginalText.Substring($TailStart).Replace('$PSCommandPath','$ActualBuilderPath').Replace('CONTROL/PRIVACIDAD_LOCAL_R07.json','CONTROL/PRIVACIDAD_LOCAL_R08.json')
. ([ScriptBlock]::Create($Tail))
