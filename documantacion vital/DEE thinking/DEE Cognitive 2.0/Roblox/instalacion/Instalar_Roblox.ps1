param([Parameter(Mandatory=$true)][string]$Destino,[string[]]$DenegarOriginal=@())
$ErrorActionPreference='Stop'
$Package=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$Manifest=Get-Content -LiteralPath (Join-Path $Package 'dependencias\MANIFIESTO_RUNTIME_R06.json') -Raw -Encoding UTF8|ConvertFrom-Json
$Zip=Join-Path (Join-Path $Package 'dependencias') ([string]$Manifest.payload.file)
$Target=[IO.Path]::GetFullPath($Destino)
if(Test-Path -LiteralPath $Target){throw 'El destino debe ser NUEVO. No se sobreescribe ni reanuda un runtime existente.'}
if($Target.TrimEnd('\').Length -le 3){throw 'No se permite una raiz de unidad'}
if($Target.StartsWith($Package+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Use una raiz corta fuera del paquete'}
$Cursor=[IO.Directory]::GetParent($Target)
while($null -ne $Cursor){if($Cursor.Exists -and ($Cursor.Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'No se permiten ancestros enlazados'};$Cursor=$Cursor.Parent}
if((Get-FileHash -LiteralPath $Zip -Algorithm SHA256).Hash.ToLowerInvariant() -ne [string]$Manifest.payload.sha256){throw 'SHA del payload incorrecto'}
Add-Type -AssemblyName System.IO.Compression.FileSystem
$Archive=[IO.Compression.ZipFile]::OpenRead($Zip)
$Prefix='dependencias/producto/motor/python313/'
[IO.Directory]::CreateDirectory($Target)|Out-Null
try {
 foreach($Entry in $Archive.Entries){
  if(-not $Entry.FullName.StartsWith($Prefix,[StringComparison]::Ordinal)){continue}
  $Tail=$Entry.FullName.Substring($Prefix.Length)
  if(-not $Tail -or $Tail.Contains('/')){continue}
  if($Tail.Contains([char]92) -or $Tail.Contains(':') -or $Tail -eq '..'){throw 'Miembro de bootstrap inseguro'}
  $Expected=@($Manifest.files|Where-Object {$_.file -ceq $Entry.FullName})
  if($Expected.Count -ne 1){throw 'Bootstrap no declarado'}
  $Out=Join-Path $Target ($Entry.FullName.Replace('/',[IO.Path]::DirectorySeparatorChar))
  [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($Out))|Out-Null
  $Source=$Entry.Open();$Output=[IO.File]::Open($Out,[IO.FileMode]::CreateNew)
  try{$Source.CopyTo($Output)}finally{$Output.Dispose();$Source.Dispose()}
  if((Get-FileHash -LiteralPath $Out -Algorithm SHA256).Hash.ToLowerInvariant() -ne [string]$Expected[0].sha256){throw 'Bootstrap hash incorrecto'}
 }
} finally {$Archive.Dispose()}
@{payloadSha256=[string]$Manifest.payload.sha256;scope='Only direct CPython bootstrap files, no Native import'}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $Target 'BOOTSTRAP_R06.json') -Encoding UTF8
$Python=Join-Path $Target 'dependencias\producto\motor\python313\python.exe'
$ExtraArguments=@()
foreach($DeniedPath in $DenegarOriginal){$ExtraArguments+=@('--denegar',$DeniedPath)}
& $Python -I -S -B -X utf8 (Join-Path $PSScriptRoot 'instalar_runtime.py') --paquete $Package --destino $Target --continuar-bootstrap @ExtraArguments
if($LASTEXITCODE -ne 0){throw 'Instalacion incompleta preservada; no abrir Native ni borrar datos automaticamente'}
