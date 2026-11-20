param(
    [string]$ResultPath = (Join-Path $PSScriptRoot '..\results\final_run\results.json')
)

$ErrorActionPreference = 'Stop'
$result = Get-Content -Raw -LiteralPath $ResultPath | ConvertFrom-Json

function Require([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}

Require ($result.technical_checks.technical_ok -eq $true) 'technical_ok is false'
Require ($result.technical_checks.f1_expected_relations -eq $true) 'F1 relation check failed'
Require ($result.technical_checks.f2_expected_mediation -eq $true) 'F2 mediation check failed'
Require ($result.technical_checks.all_inputs_applied_at_t0 -eq $true) 'an input was not applied at t0'
Require ($result.technical_checks.no_backend_fallback -eq $true) 'backend fallback occurred'
Require ($result.technical_checks.selected_lazy_dense_raw_clock_exact -eq $true) 'Lazy/Dense mismatch'
Require (($result.comparisons.f3_distinct_upstream_responses -join ',') -eq '4149,4151') 'F3 upstream panel changed'
Require (($result.comparisons.f3_downstream_use2_outputs -join ',') -eq '67,67') 'F3 downstream panel changed'

Write-Output 'RESULTS_VALID=TRUE'

