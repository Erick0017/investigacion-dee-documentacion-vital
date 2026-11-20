$ErrorActionPreference = 'Stop'
$Root = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$Utf8 = [Text.UTF8Encoding]::new($false, $true)
$PlanPath = Join-Path $Root 'control/PLAN_FINAL_R07_PREPRIVACIDAD.json'
$PlanPin = '2074ad154d9532c5ed796d10cd727ffdd97b1b90dda88eebc7c97e4d0f01079d'
$Progress = Join-Path $Root 'control/PROGRESO_EMPAQUETADO_LOCAL_R07.jsonl'
$Checked = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
function Mark($Stage, $Detail) {
    [IO.File]::AppendAllText($Progress, ((@{utc=[DateTime]::UtcNow.ToString('o');stage=$Stage;detail=$Detail}|ConvertTo-Json -Compress -Depth 10) + "`n"), $Utf8)
}
function Digest([byte[]]$Bytes) {
    $Hasher = [Security.Cryptography.SHA256]::Create()
    try { return [Convert]::ToHexString($Hasher.ComputeHash($Bytes)).ToLowerInvariant() } finally { $Hasher.Dispose() }
}
function NoLinks([string]$Path) {
    $Current = [IO.Path]::GetFullPath($Path)
    while ($Current) {
        if (-not $Checked.Contains($Current)) {
            $Attr = [IO.File]::GetAttributes($Current)
            if (($Attr -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'REPARSE_POINT_REJECTED' }
            if (($Attr -band [IO.FileAttributes]::Directory) -ne 0) { [void]$Checked.Add($Current) }
        }
        $Parent = [IO.Directory]::GetParent($Current)
        if ($null -eq $Parent) { break }; $Current = $Parent.FullName
    }
}
function ReadStable([string]$Path, [long]$Limit=8000000) {
    NoLinks $Path
    $Before = [IO.FileInfo]::new($Path)
    $Size = $Before.Length; $Time = $Before.LastWriteTimeUtc.Ticks
    if ($Size -gt $Limit) { throw 'FILE_SIZE_BOUND' }
    $Bytes = [IO.File]::ReadAllBytes($Path)
    $After = [IO.FileInfo]::new($Path)
    if ($Bytes.Length -ne $Size -or $After.Length -ne $Size -or $After.LastWriteTimeUtc.Ticks -ne $Time) { throw 'SOURCE_CHANGED' }
    return ,$Bytes
}
function WriteNew([string]$Path, [byte[]]$Bytes) {
    $Stream = [IO.File]::Open($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $Stream.Write($Bytes,0,$Bytes.Length) } finally { $Stream.Dispose() }
}
function JsonBytes($Value) { return ,$Utf8.GetBytes(($Value|ConvertTo-Json -Depth 100) + "`n") }
function SafeName([string]$Name) {
    if (-not $Name -or $Name.StartsWith('/') -or $Name.Contains('\') -or $Name.Contains(':') -or @($Name.Split('/')|Where-Object { $_ -in @('', '.', '..') }).Count) { throw 'UNSAFE_ARCHIVE_NAME' }
}
function Protect {
    $RefPath = Join-Path $Root 'control/CRITICOS_ANTES_R07.json'
    $RefBytes = ReadStable $RefPath
    $Ref = $Utf8.GetString($RefBytes)|ConvertFrom-Json
    if ($Ref.files.Count -ne 11) { throw 'EXPECTED_ELEVEN_CRITICALS' }
    $Rows = foreach ($Item in $Ref.files) {
        $Bytes = ReadStable $Item.path 20000000; $Hash = Digest $Bytes
        $Match = $Bytes.Length -eq $Item.bytes -and $Hash -eq $Item.sha256
        if (-not $Match) { throw 'PROTECTED_ORIGINAL_CHANGED' }
        @{role=$Item.role;path=$Item.path;expected_bytes=$Item.bytes;expected_sha256=$Item.sha256;current_bytes=$Bytes.Length;current_sha256=$Hash;matches_before=$Match}
    }
    return @{schema='DEE.INTEGRAL.V3.protected_files_verification.R01';utc=[DateTime]::UtcNow.ToString('o');source_reference=$RefPath;source_reference_sha256=(Digest $RefBytes);coverage='Exactly eleven named originals; not whole-project immutability.';all_eleven_unchanged=$true;files=@($Rows)}
}
if ([IO.File]::Exists($Progress)) { throw 'FRESH_PROGRESS_REQUIRED' }
Mark 'START' @{runtime=$PSVersionTable.PSVersion.ToString();scope='File-only local packaging; no Python, Node subprocess, Native, Studio, model, network or experiments.'}
$PlanBytes = ReadStable $PlanPath
if ((Digest $PlanBytes) -ne $PlanPin) { throw 'PLAN_PIN_MISMATCH' }
$Plan = $Utf8.GetString($PlanBytes)|ConvertFrom-Json
$Allowed = @($Root) + @($Plan.source_roots|ForEach-Object { [IO.Path]::GetFullPath((Join-Path $Root $_)) })
$Rows = [Collections.Generic.List[object]]::new()
foreach ($Item in $Plan.files) { $Rows.Add($Item) }
$SelfBytes = ReadStable $PSCommandPath
$Rows.Add([pscustomobject]@{source=$PSCommandPath;archive='CONTROL/empaquetado_local_R07.ps1';role='code';bytes=$SelfBytes.Length;sha256=(Digest $SelfBytes)})
$Entries = [Collections.Generic.List[object]]::new()
$Records = [Collections.Generic.List[object]]::new()
$Coverage = [Collections.Generic.List[object]]::new()
$Findings = [Collections.Generic.List[object]]::new()
$Binary = [Collections.Generic.List[object]]::new()
$Names = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$Timeout = [TimeSpan]::FromSeconds(2)
$Patterns = @(
    @('PRIVATE_KEY_PEM', '-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----'),
    @('BEARER_LITERAL', '(?i)\bBearer\s+[A-Za-z0-9._~+/-]{16,}'),
    @('ROBLOX_COOKIE_LITERAL', '(?i)\.ROBLOSECURITY\s*[:=]\s*[^\s]{24,}'),
    @('NONEMPTY_SENSITIVE_JSON_KEY', '(?i)(?<!\\)"(?:password|passwd|access_token|refresh_token|authorization|cookie|set-cookie|api_key|apikey|client_secret|private_key|roblosecurity)"\s*:\s*"(?:[^"\\]|\\.)+"')
)
$InitialProtection = Protect
$Ordinal = 0
foreach ($Item in $Rows) {
    $Ordinal++; Mark 'READ_BEGIN' @{ordinal=$Ordinal;archive=$Item.archive}
    SafeName $Item.archive
    if (-not $Names.Add($Item.archive)) { throw 'CASE_INSENSITIVE_COLLISION' }
    $Source = [IO.Path]::GetFullPath($Item.source)
    if (-not @($Allowed|Where-Object { $Source.StartsWith($_ + [IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase) }).Count) { throw 'SOURCE_OUTSIDE_EXPLICIT_ROOTS' }
    $Limit = 2000000; if ($Item.max_bytes) { $Limit = [long]$Item.max_bytes }
    if ($Limit -gt 8000000) { throw 'MEMBER_LIMIT' }
    $Bytes = ReadStable $Source $Limit; $Hash = Digest $Bytes
    if ($Bytes.Length -ne $Item.bytes -or $Hash -ne $Item.sha256) { throw ('SOURCE_PIN: ' + $Item.archive) }
    if ($Item.archive.EndsWith('.mp4')) {
        if ($Item.role -ne 'technical_capture_primary' -or $Hash -ne 'eb2a2979f0731e5a47aa1d01a0e42fbe11a194bc8936c285c9d3d38d247977cf') { throw 'UNREVIEWED_MEDIA' }
        $Binary.Add(@{archive=$Item.archive;sha256=$Hash;scope='Previously reviewed exact original Main35 clip; supplementary, not comparative movie or1080p source.'})
    } else {
        $Text = $Utf8.GetString($Bytes).TrimStart([char]0xFEFF)
        if ($Item.archive.EndsWith('.json')) { $Doc=[Text.Json.JsonDocument]::Parse($Text);$Doc.Dispose() }
        if ($Item.archive.EndsWith('.jsonl')) { foreach ($Line in ($Text -split '\r?\n')) { if ($Line.Trim()) { $Doc=[Text.Json.JsonDocument]::Parse($Line);$Doc.Dispose() } } }
        foreach ($Pattern in $Patterns) {
            try { if ([regex]::IsMatch($Text,$Pattern[1],[Text.RegularExpressions.RegexOptions]::None,$Timeout)) { $Findings.Add(@{archive=$Item.archive;kind=$Pattern[0];value_printed=$false}) } }
            catch [Text.RegularExpressions.RegexMatchTimeoutException] { $Findings.Add(@{archive=$Item.archive;kind='PRIVACY_REGEX_TIMEOUT_REQUIRES_REVIEW';value_printed=$false}) }
        }
        if ($Text.Contains('@')) {
            foreach ($At in [regex]::Matches($Text,'@')) {
                $Start=[Math]::Max(0,$At.Index-320);$Length=[Math]::Min(640,$Text.Length-$Start);$Window=$Text.Substring($Start,$Length)
                if ([regex]::IsMatch($Window,'(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',[Text.RegularExpressions.RegexOptions]::None,$Timeout)) { $Findings.Add(@{archive=$Item.archive;kind='EMAIL_CANDIDATE';value_printed=$false});break }
            }
        }
    }
    $Record=@{archive=$Item.archive;source=$Source;role=$Item.role;bytes=$Bytes.Length;sha256=$Hash}
    if ($Limit -gt 2000000) { $Record.max_bytes=$Limit }
    $Records.Add($Record);$Entries.Add(@{archive=$Item.archive;raw=$Bytes});$Coverage.Add(@{archive=$Item.archive;source=$Source;bytes=$Bytes.Length;sha256=$Hash})
    Mark 'SOURCE_VERIFIED' @{ordinal=$Ordinal;archive=$Item.archive}
}
$Privacy=@{schema='DEE.R07.file_only_privacy_local.v1';utc=[DateTime]::UtcNow.ToString('o');plan_sha256=$PlanPin;source_members=$Rows.Count;coverage=@($Coverage.ToArray());findings=@($Findings.ToArray());binary_limits=@($Binary.ToArray());scope='Heuristic exact-byte privacy review; bounded regex, email windows, not whole-project certification. No values printed.'}
$PrivacyPath=Join-Path $Root 'analisis/REVISION_PRIVACIDAD_LOCAL_R07.json'
$PrivacyBytes=JsonBytes $Privacy;WriteNew $PrivacyPath $PrivacyBytes
if ($Findings.Count) { throw 'PRIVACY_CANDIDATES_REQUIRE_CONTEXT_REVIEW' }
if ($Binary.Count -ne 1) { throw 'EXPECTED_ONE_SUPPLEMENTARY_RAW_CLIP' }
$Protection=Protect;$ProtectionBytes=JsonBytes $Protection
foreach ($Generated in @(
    @{archive='CONTROL/PRIVACIDAD_LOCAL_R07.json';raw=$PrivacyBytes;source=$PrivacyPath},
    @{archive='CONTROL/PROTECCION_CRITICOS.json';raw=$ProtectionBytes;source=$null}
)) {
    $Entries.Add(@{archive=$Generated.archive;raw=$Generated.raw});$Records.Add(@{archive=$Generated.archive;source=$Generated.source;role='verification';bytes=$Generated.raw.Length;sha256=(Digest $Generated.raw)})
}
$Manifest=@{schema='DEE.INTEGRAL.V3.content_manifest.R01';created_utc=[DateTime]::UtcNow.ToString('o');plan_sha256=$PlanPin;ZIP_is_executable_backup=$false;hash_scope='Content members, excludes manifest itself and external ZIP hash.';recalculations=$Plan.recalculations;final_recipe_execution='Not run by this file-only packager; previously verified portable proofs preserved. Any final Native/runtime replay must be reported separately.';files=@($Records.ToArray())}
$ManifestBytes=JsonBytes $Manifest;$Entries.Add(@{archive='CONTROL/MANIFIESTO_SHA256.json';raw=$ManifestBytes})
$RawTotal=0L;foreach($Item in $Entries){$RawTotal+=$Item.raw.Length}
if ($Entries.Count -gt 752 -or $RawTotal -gt 80000000) { throw 'PACKAGE_BOUND' }
$Delivery=Join-Path (Split-Path -Parent $Root) 'entrega';NoLinks $Delivery
$ZipPath=Join-Path $Delivery 'DEE_ROBLOX_CIERRE8_R07_2026_11_17_ANALISIS.zip'
$ZipStream=[IO.File]::Open($ZipPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
try {
    $Archive=[IO.Compression.ZipArchive]::new($ZipStream,[IO.Compression.ZipArchiveMode]::Create,$true)
    try { foreach ($Item in $Entries) { $Entry=$Archive.CreateEntry($Item.archive,[IO.Compression.CompressionLevel]::Optimal);$Entry.LastWriteTime=[DateTimeOffset]::new(1980,1,1,0,0,0,[TimeSpan]::Zero);$Stream=$Entry.Open();try{$Stream.Write($Item.raw,0,$Item.raw.Length)}finally{$Stream.Dispose()} } } finally { $Archive.Dispose() }
} finally { $ZipStream.Dispose() }
Mark 'ZIP_WRITTEN' $ZipPath
$ZipBytes=ReadStable $ZipPath 15000000
$Extract=Join-Path $Delivery 'VERIFICACION_LIMPIA_CIERRE8_R07_2026_11_17'
if ([IO.Directory]::Exists($Extract)) { throw 'FRESH_EXTRACTION_REQUIRED' };[void][IO.Directory]::CreateDirectory($Extract)
$Expected=@{};foreach($Item in $Records){$Expected[$Item.archive]=$Item};$Expected['CONTROL/MANIFIESTO_SHA256.json']=@{bytes=$ManifestBytes.Length;sha256=(Digest $ManifestBytes)}
$ReadStream=[IO.File]::OpenRead($ZipPath)
try {
    $Archive=[IO.Compression.ZipArchive]::new($ReadStream,[IO.Compression.ZipArchiveMode]::Read,$true)
    try {
        if ($Archive.Entries.Count -ne $Entries.Count) { throw 'MEMBER_COUNT' }
        $Seen=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
        foreach($Entry in $Archive.Entries) {
            SafeName $Entry.FullName
            if (-not $Seen.Add($Entry.FullName) -or -not $Expected.ContainsKey($Entry.FullName) -or $Entry.Length -gt 8000000) { throw 'UNEXPECTED_ZIP_MEMBER' }
            $Memory=[IO.MemoryStream]::new();$Stream=$Entry.Open();try{$Stream.CopyTo($Memory);$Bytes=$Memory.ToArray()}finally{$Stream.Dispose();$Memory.Dispose()}
            if ($Bytes.Length -ne $Expected[$Entry.FullName].bytes -or (Digest $Bytes) -ne $Expected[$Entry.FullName].sha256) { throw 'ZIP_MEMBER_HASH' }
            $Destination=[IO.Path]::GetFullPath((Join-Path $Extract $Entry.FullName))
            if (-not $Destination.StartsWith($Extract+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { throw 'EXTRACTION_ESCAPE' }
            [void][IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($Destination));WriteNew $Destination $Bytes
            if ((Digest (ReadStable $Destination)) -ne $Expected[$Entry.FullName].sha256) { throw 'EXTRACTED_FILE_HASH' }
        }
    } finally { $Archive.Dispose() }
} finally { $ReadStream.Dispose() }
$FinalProtection=Protect
foreach($Item in $Coverage){if((Digest (ReadStable $Item.source)) -ne $Item.sha256){throw 'SOURCE_CHANGED_AFTER_BUILD'}}
$Proof=@{schema='DEE.R07.final_archive_local_verification.v1';utc=[DateTime]::UtcNow.ToString('o');ZIP=$ZipPath;bytes=$ZipBytes.Length;sha256=(Digest $ZipBytes);limit_bytes=15000000;members=$Entries.Count;raw_bytes=$RawTotal;format='Standard ZIP Deflate; no password or volumes';all_member_decompression_and_SHA256=$true;clean_extraction=$Extract;all_extracted_hashes_pass=$true;critical_eleven_unchanged=$FinalProtection.all_eleven_unchanged;privacy_proof=$PrivacyPath;privacy_sha256=(Digest $PrivacyBytes);builder=$PSCommandPath;builder_sha256=(Digest $SelfBytes);scope='File-only archive verification and clean extraction, not new experiments or execution of Python recipes.';independent_CRC_recalculation=$false;Native_Studio_model_network_calls=0}
$ProofPath=Join-Path $Root 'control/VERIFICACION_ZIP_LOCAL_R07.json';WriteNew $ProofPath (JsonBytes $Proof)
Mark 'COMPLETE' $Proof
$Proof|ConvertTo-Json -Depth 20
