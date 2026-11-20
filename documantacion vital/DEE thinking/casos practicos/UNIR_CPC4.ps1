$ErrorActionPreference = 'Stop'
$cpc4Name = 'CPC4_COMUNICACION_NATIVA_Y_META_ROSETTA_RESULTADOS.zip'
$cpc4Target = Join-Path $PSScriptRoot $cpc4Name
$cpc4Expected = '4a14a81f913a434a8e54e47c0c700d7ee54418bb16913aedded8bf49a3294723'

if (Test-Path -LiteralPath $cpc4Target) {
    if ((Get-FileHash -LiteralPath $cpc4Target -Algorithm SHA256).Hash.ToLowerInvariant() -eq $cpc4Expected) {
        Write-Output 'El ZIP original completo ya existe y su SHA-256 es correcto. No se modifico.'
        return
    }
    throw 'Ya existe un archivo con el nombre de destino y otro hash. No se sobrescribira.'
}

$cpc4Parts = @("$cpc4Target.001", "$cpc4Target.002")
foreach ($cpc4Part in $cpc4Parts) {
    if (-not (Test-Path -LiteralPath $cpc4Part -PathType Leaf)) {
        throw "Falta la parte: $cpc4Part"
    }
}
$cpc4Temporary = "$cpc4Target.reuniendo.tmp"
$cpc4Output = [System.IO.File]::Open($cpc4Temporary, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write)
try {
    foreach ($cpc4Part in $cpc4Parts) {
        $cpc4Input = [System.IO.File]::OpenRead($cpc4Part)
        try { $cpc4Input.CopyTo($cpc4Output) } finally { $cpc4Input.Dispose() }
    }
} finally { $cpc4Output.Dispose() }

if ((Get-FileHash -LiteralPath $cpc4Temporary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $cpc4Expected) {
    throw "Las partes no reconstruyen el SHA-256 esperado. Se conserva el temporal: $cpc4Temporary"
}
Move-Item -LiteralPath $cpc4Temporary -Destination $cpc4Target -ErrorAction Stop
Write-Output "ZIP reconstruido y SHA-256 verificado: $cpc4Target"
