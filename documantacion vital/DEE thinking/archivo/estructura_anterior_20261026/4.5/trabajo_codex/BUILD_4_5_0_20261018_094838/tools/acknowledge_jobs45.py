"""Reconcile preserved failed jobs with explicit later technical evidence.

This is a release auditor only. The product never imports this acknowledgement
or uses a failed/successful outcome table to answer an experience or query.
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from package45 import put, sha, worker_audit, SUPERVISOR_SHA

MAPPING = {
    'baseline_cpc_ports_400': ('Windows atomic report replace was denied after the physical trajectory; original process result retained.',
        ['jobs/baseline_K65_Q9_recovery/COMMAND.json', 'validation/cpc_ports_4_0/INDEX_COMPLETED.json', 'validation/CPC_PORT_DIFF_final6.json']),
    'baseline_neutral_400': ('Two native long-run cases exceeded their child-task window after writing checkpoints; no new preparation used for directed continuation.',
        ['jobs/baseline_dense127_continue/COMMAND.json', 'jobs/baseline_parallel127_continue/COMMAND.json', 'validation/differential_4_0/INDEX_COMPLETED.json', 'validation/NEUTRAL_DIFF_final6.json']),
    'consolidated_cpp_build_tests': ('Three inherited CTest cases exceeded the initial 180-second test limit; original 20 passes and 3 timeouts retained.',
        ['jobs/cpp_final_affected_tests/COMMAND.json', 'validation/CPP_VERSION_ASSERTION_REPAIR.json']),
    'cpp_directed_timeout_recovery_and_trace': ('Directed completion exposed one stale expected product-version literal; physical assertions were not changed.',
        ['jobs/cpp_final_affected_tests/COMMAND.json', 'validation/CPP_VERSION_ASSERTION_REPAIR.json']),
    'early_wheel_toolchain': ('The initial relative -File path did not resolve from the build invocation directory.',
        ['jobs/early_wheel_authorized/COMMAND.json', 'jobs/final_contract_wheel_candidate6/COMMAND.json', 'validation/WHEEL_INSPECTION_FINAL.json']),
    'early_wheel_toolchain_absolute': ('Windows PowerShell rejected script execution under the default process policy; no global policy was changed.',
        ['jobs/early_wheel_authorized/COMMAND.json', 'jobs/final_contract_wheel_candidate6/COMMAND.json', 'validation/WHEEL_INSPECTION_FINAL.json']),
    'launcher_preflight01': ('Packaging metadata parser incorrectly required LF rather than accepting Windows CRLF in standard wheel headers.',
        ['validation/PACKAGING_UNIT_TESTS_CRLF.json', 'validation/launcher_preflight05_short/LAUNCHER_REPORT.json', 'validation/clean_preliminary/launcher/LAUNCHER_REPORT.json']),
    'launcher_preflight02': ('Get-FileHash was unavailable in the invoked Windows PowerShell; the launcher now uses the same SHA256 via a .NET stream.',
        ['validation/launcher_preflight05_short/LAUNCHER_REPORT.json', 'validation/clean_preliminary/launcher/LAUNCHER_REPORT.json']),
    'launcher_preflight03': ('The deeply nested development fixture installed successfully but its native module could not be loaded at that path length.',
        ['validation/launcher_preflight05_short/LAUNCHER_REPORT.json', 'validation/clean_preliminary/launcher/LAUNCHER_REPORT.json']),
    'launcher_preflight04': ('The same launcher still failed in a 251-character native-module path. The nominal 260-character guard is not a universal guarantee.',
        ['validation/launcher_preflight04/SOURCE_LAUNCHER.ps1', 'validation/launcher_preflight05_short/SOURCE_LAUNCHER.ps1', 'validation/launcher_preflight05_short/LAUNCHER_REPORT.json', 'validation/clean_preliminary/launcher/LAUNCHER_REPORT.json']),
    'legacy_actual_cpc7_candidate2_01': ('The audit caller requested a nonexistent protocol_state attribute; the actual legacy physical snapshot was preserved.',
        ['jobs/legacy_actual_cpc7_final6_01/COMMAND.json']),
    'smoke_candidate1': ('A descriptor-only initial_state_available flag legitimately differs between create and inert load. Full original descriptors and physical comparisons remain in both primaries.',
        ['validation/smoke_candidate1_02/SMOKE_REPORT.json', 'validation/clean_preliminary/smoke/SMOKE_REPORT.json']),
    'unicode_paths_candidate2': ('Unicode paths exposed native locale-dependent file I/O; the first diagnostic print also failed in cp1252. Native UTF8 conversions and trace paths were subsequently tested.',
        ['validation/clean_preliminary/unicode/UNICODE_REPORT.json', 'jobs/native_unicode_io_repair/COMMAND.json'])
}


def main():
    known = []
    unexpected = []
    for path in sorted((ROOT / 'jobs').glob('*/COMMAND.json')):
        row = json.loads(path.read_text(encoding='utf-8-sig'))
        if row['status'] == 'COMPLETED' and row['exit_code'] == 0:
            continue
        if path.parent.name not in MAPPING:
            unexpected.append(path.parent.name); continue
        cause, resolutions = MAPPING[path.parent.name]
        evidence = []
        for name in resolutions:
            target = ROOT / name
            if not target.is_file():
                raise FileNotFoundError('Missing resolution evidence: ' + name)
            if name.startswith('jobs/'):
                success = json.loads(target.read_text(encoding='utf-8-sig'))
                if success['status'] != 'COMPLETED' or success['exit_code'] != 0:
                    raise ValueError('Resolution job is not successful: ' + name)
            evidence.append({'path': name, 'sha256': sha(target)})
        known.append({'job': path.parent.name, 'status': row['status'], 'exit_code': row['exit_code'],
            'ledger_sha256': sha(path), 'cause': cause, 'resolution_evidence': evidence,
            'functional_status': 'FAILED_OR_INCOMPLETE_ORIGINAL_RETAINED_NOT_PASS',
            'closure_scope': 'Original worker completed process.wait and OwnedJob finally-close; the failure is never relabelled as a functional pass.'})
    if unexpected:
        raise ValueError('New unacknowledged failed jobs block release: ' + repr(unexpected))
    if len(known) != len(MAPPING):
        raise ValueError('Known failed ledger inventory changed')
    put(ROOT / 'validation/PRESERVED_JOB_FAILURES.json', {'schema': 'DEE45.preserved-job-failures.v1', 'jobs': known,
        'scope': 'Explicit historical nonzero exits and their later technical evidence; not scientific samples or participant response data.'})
    observed = worker_audit()
    report = {'schema': 'DEE45.publication-gate-review.v1', 'status': 'VERIFIED',
        'preserved_initial_gate_error': {'operation': 'OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION)', 'pid': 14272, 'windows_error': 5,
            'ledger': 'jobs/unicode_snapshot_trace_candidate3/COMMAND.json', 'scope': 'Original ledger was COMPLETED/0. Current PID existence/generation unknown; no further access escalation or process action.'},
        'supervisor_source_sha256': SUPERVISOR_SHA, 'unit_tests': 'validation/PACKAGING_UNIT_TESTS_FINAL_GATE.json',
        'observed_original_worker_closure': observed,
        'scope': 'Closure is not functional success. No claim of globally absent processes; inaccessible current PIDs remain unknown.'}
    put(ROOT / 'validation/PUBLICATION_GATE_REVIEW.json', report)
    print(json.dumps({'status': 'VERIFIED', 'acknowledged_nonzero_jobs': len(known), 'worker_ledgers': len(observed['records']),
                      'current_pid_unknown': [r['pid'] for r in observed['records'] if r['current_process_unknown']]}))


if __name__ == '__main__':
    main()
