$ErrorActionPreference = 'Stop'
$recordPath = Join-Path $PSScriptRoot 'CIERRE_EDITOR_PILOTO_ROOT_R01.json'
if (Test-Path -LiteralPath $recordPath) { throw 'Existing closure record; reconcile, never repeat automatically.' }
$scenePath = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\mundo\PILOTO_R07.rbxlx'))
$expectedHash = 'ef39c6bf193c2f26386384e564ffcb16ab2e93c29f7b8a9e071431781dbcfd92'
$actualHash = (Get-FileHash -LiteralPath $scenePath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actualHash -ne $expectedHash) { throw 'Scene bytes changed; preserve editor.' }
$entry = Get-CimInstance -ClassName Win32_Process -Filter 'ProcessId=16172'
if (-not $entry) { throw 'Pilot PID absent; reconcile only.' }
$createdUtc = $entry.CreationDate.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss')
if ($entry.Name -ne 'RobloxStudioBeta.exe' -or $createdUtc -ne '2026-11-16T18:33:11') { throw 'Pilot PID identity changed.' }
if (-not $entry.CommandLine.EndsWith(('"' + $scenePath + '"'), [StringComparison]::OrdinalIgnoreCase)) { throw 'Wrong Studio file; preserve.' }
$record = [ordered]@{ utc=[DateTime]::UtcNow.ToString('o'); processId=16172; creationUtc=$createdUtc; commandLine=$entry.CommandLine; file=$scenePath; scene_sha256=$actualHash; MCP_state_verified='Edit'; no_Native_ever_opened_on_this_editor=$true; action='CLOSE_ONLY_OWN_PREPARED_PILOT_EDITOR'; gracefulRequested=$false; forceUsed=$false; closed=$false }
$record | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $recordPath -Encoding utf8
$targetProcess = Get-Process -Id 16172
$record.gracefulRequested = $targetProcess.CloseMainWindow()
Start-Sleep -Seconds 5
$remaining = Get-Process -Id 16172 -ErrorAction SilentlyContinue
if ($remaining) {
  # This exact editor contains only the immutable prepared map, no Native
  # owner, no material episode and no subsequent edits. Never another PID.
  if ($remaining.StartTime.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss') -ne $createdUtc) { throw 'PID reused; no force.' }
  Stop-Process -Id 16172 -Force
  $record.forceUsed=$true
  Start-Sleep -Seconds 2
}
$record.closed = -not [bool](Get-Process -Id 16172 -ErrorAction SilentlyContinue)
$record.after_scene_sha256 = (Get-FileHash -LiteralPath $scenePath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($record.after_scene_sha256 -ne $expectedHash) { throw 'Unexpected scene modification.' }
$record | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $recordPath -Encoding utf8
$record | ConvertTo-Json -Depth 6
