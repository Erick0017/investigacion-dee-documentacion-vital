param([Parameter(Mandatory=$true)][ValidateSet('antes','despues')][string]$Modo)
$ErrorActionPreference='Stop'
$SDK=Split-Path -Parent $PSScriptRoot
$C=Split-Path -Parent (Split-Path -Parent $SDK)
$Utf8=[Text.UTF8Encoding]::new($false,$true)
$Antes=Join-Path $PSScriptRoot 'ORIGINALES_ANTES.json'
$Salida=Join-Path $PSScriptRoot ('ORIGINALES_'+$Modo.ToUpperInvariant()+'.json')
if([IO.File]::Exists($Salida)){throw 'NO_SOBRESCRIBIR_COMPROBANTE'}
function HashEstable([string]$P){
 $P=[IO.Path]::GetFullPath($P)
 $F=[IO.FileInfo]::new($P);$N=$F.Length;$T=$F.LastWriteTimeUtc.Ticks
 $B=[IO.File]::ReadAllBytes($P);$G=[IO.FileInfo]::new($P)
 if($N -ne $B.Length -or $G.Length -ne $N -or $G.LastWriteTimeUtc.Ticks -ne $T){throw 'ARCHIVO_CAMBIO_DURANTE_LECTURA'}
 $H=[Security.Cryptography.SHA256]::Create()
 try{$S=[Convert]::ToHexString($H.ComputeHash($B)).ToLowerInvariant()}finally{$H.Dispose()}
 return @{path=$P;bytes=$B.Length;sha256=$S;last_write_utc=$G.LastWriteTimeUtc.ToString('o')}
}
if($Modo -eq 'antes'){
 $Ref=Join-Path $C 'laboratorio/DEE_ROBLOX_RBX01/revision_R07_CIERRE_8_PUNTOS/control/CRITICOS_ANTES_R07.json'
 $Legacy=[IO.File]::ReadAllText($Ref,$Utf8)|ConvertFrom-Json
 $Paths=@{};foreach($R in $Legacy.files){$Paths[[IO.Path]::GetFullPath($R.path)]=$R.role}
 $ActivoPath=Join-Path $C 'sistema/estado/ACTIVO.json'
 $Activo=[IO.File]::ReadAllText($ActivoPath,$Utf8)|ConvertFrom-Json
 if($Activo.life_id -notmatch '^[A-Za-z0-9_-]+$'){throw 'ID_ACTIVO_INVALIDO'}
 $Paths[(Join-Path $C ('sistema/estado/vidas/'+$Activo.life_id+'/VIDA.json'))]='selected_current_card'
 $Paths[(Join-Path $C ('sistema/'+$Activo.snapshot))]='selected_current_snapshot'
 $LifeRoot=Join-Path $C 'sistema/estado/vidas'
 foreach($D in (Get-ChildItem -LiteralPath $LifeRoot -Directory|Where-Object{$_.Name -like '*PI11*'})){
  if(($D.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw 'PI11_REPARSE_RECHAZADO'}
  $P=Join-Path $D.FullName 'VIDA.json';if([IO.File]::Exists($P)){$Paths[$P]='preserved_PI11_card'}
  $SnapRoot=Join-Path $C 'sistema/estado/checkpoints'
  foreach($S in (Get-ChildItem -LiteralPath $SnapRoot -File -Filter ($D.Name+'.T979389.*.deetsnap.gz'))){$Paths[$S.FullName]='preserved_PI11_reference_snapshot_T979389'}
 }
 $Rows=foreach($P in $Paths.Keys){$R=HashEstable $P;$R.role=$Paths[$P];$R}
 $Report=@{schema='DEE.SDK.originals.before.v1';utc=[DateTime]::UtcNow.ToString('o');selected=$Activo;files=@($Rows);scope='Named critical originals and PI11 cards/reference snapshot only; no global inventory or full-project immutability claim';Native_calls=0}
}else{
 $Old=[IO.File]::ReadAllText($Antes,$Utf8)|ConvertFrom-Json
 $Rows=foreach($R in $Old.files){$Now=HashEstable $R.path;$Now.role=$R.role;$Now.before_sha256=$R.sha256;$Now.matches_before=($Now.sha256 -eq $R.sha256 -and $Now.bytes -eq $R.bytes);$Now}
 $Different=@($Rows|Where-Object{-not $_.matches_before})
 $Report=@{schema='DEE.SDK.originals.after.v1';utc=[DateTime]::UtcNow.ToString('o');files=@($Rows);all_named_originals_unchanged=($Different.Count -eq 0);scope=$Old.scope;Native_calls=0}
}
$Bytes=$Utf8.GetBytes(($Report|ConvertTo-Json -Depth 30)+"`n")
$Stream=[IO.File]::Open($Salida,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
try{$Stream.Write($Bytes,0,$Bytes.Length)}finally{$Stream.Dispose()}
@{output=$Salida;files=$Rows.Count;mode=$Modo;all_unchanged=$Report.all_named_originals_unchanged;Native_calls=0}|ConvertTo-Json
