"""Passive CPC9 closure accounting; never imports or evolves a DEE Runtime.

Recalculate owned-job costs, primary container categories and root snapshot
integrity. No historical archive, unrelated process or scientific judgement is
queried. Generated summaries are explicitly pre-seal unless --sealed is given.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def ref(path):
    return {'member': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'bytes': path.stat().st_size}


def budget_clock(budget):
    value = {'recorded_budget': budget, 'observed_utc': datetime.now(timezone.utc).isoformat()}
    if sys.platform == 'win32':
        import ctypes
        frequency = ctypes.c_int64()
        counter = ctypes.c_int64()
        k = ctypes.WinDLL('kernel32', use_last_error=True)
        if not k.QueryPerformanceFrequency(ctypes.byref(frequency)) or not k.QueryPerformanceCounter(ctypes.byref(counter)):
            raise OSError('Cannot read original monotonic clock')
        if frequency.value != budget['monotonic_frequency']:
            raise ValueError('Monotonic frequency changed; do not restart original clock')
        elapsed = (counter.value - budget['monotonic_start']) / frequency.value
        value.update(observed_counter=counter.value, monotonic_frequency=frequency.value,
                     elapsed_seconds_from_original_start=elapsed,
                     remaining_seconds=max(0, budget['budget_seconds'] - elapsed),
                     remaining_experiment_seconds_before_close_reserve=max(0, budget['budget_seconds'] - elapsed - budget['reserve_close_seconds']))
    else:
        value['monotonic_measurement_status'] = 'Unavailable: original QPC reference requires Windows; original budget is preserved, never restarted.'
    return value


def primary_paths():
    paths = set()
    for name in ('MEDICIONES.json', 'MEASUREMENTS.json'):
        paths.update((ROOT / 'resultados').rglob(name))
    for front in ROOT.glob('front_*'):
        for name in ('MEDICIONES.json', 'MEASUREMENTS.json'):
            paths.update((front / 'resultados').rglob(name))
    return sorted(paths)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, default=ROOT / 'revision')
    p.add_argument('--sealed', action='store_true', help='Only after explicit candidate sealing; never makes scientific outcomes positive')
    a = p.parse_args()
    start = time.monotonic()
    budget_path = ROOT / 'PRESUPUESTO.json'
    budget = read(budget_path)
    jobs = []
    unresolved = []
    for folder in sorted((ROOT / 'jobs').iterdir()):
        if not folder.is_dir():
            continue
        path = folder / 'COMMAND.json'
        if path.exists():
            row = read(path)
            elapsed = row.get('elapsed_seconds')
            queued = row.get('slot_wait_seconds', 0)
            jobs.append({'member': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'name': row.get('name', folder.name),
                'status': row.get('status'), 'exit_code': row.get('exit_code'), 'worker_pid_recorded': row.get('pid'),
                'native_slot_required': row.get('native_slot_required'), 'started_utc': row.get('started_utc'), 'finished_utc': row.get('finished_utc'),
                'elapsed_wall_seconds_including_queue': elapsed, 'slot_wait_seconds': queued,
                'nonqueue_wall_seconds_setup_process_cleanup': None if elapsed is None else max(0, elapsed - queued),
                'timeout_seconds': row.get('timeout_seconds'), 'memory_limit_bytes': row.get('memory_limit_bytes'),
                'peak_process_memory_bytes': row.get('peak_process_memory_bytes'), 'peak_job_memory_bytes': row.get('peak_job_memory_bytes'),
                'owned_worker_waited': row.get('owned_worker_waited'), 'owned_job_closed': row.get('owned_job_closed'),
                'error': row.get('error')})
        elif (folder / 'START.json').exists():
            initial = read(folder / 'START.json')
            cancellation = folder / 'CANCELACION.json'
            unresolved.append({'start': ref(folder / 'START.json'), 'status': initial.get('status'), 'pid': initial.get('pid'),
                'cancellation': ref(cancellation) if cancellation.exists() else None,
                'external_Core_verification_not_in_CPC9_payload': folder.name.casefold().startswith('core_clean_'),
                'classification': 'Explicitly cancelled before Runtime' if cancellation.exists() else 'No final COMMAND; launch/process status not established from this artifact alone'})
    primary = []
    totals = Counter()
    snapshots_expected = {}
    integer_fields = ('preparations', 'continuations', 'diagnostic_forks', 'forks', 'technical_replays', 'passive_saved_state_loads', 'technical_restored_continuations')
    for path in primary_paths():
        data = read(path)
        row = ref(path) | {'schema': data.get('schema'), 'status': data.get('status'),
                          'case_id': data.get('case_id', data.get('case')), 'reported_counts': {key: data[key] for key in integer_fields if type(data.get(key)) is int}}
        primary.append(row)
        for key, value in row['reported_counts'].items():
            totals[key] += value
        for snapshot in data.get('snapshots', []):
            if not isinstance(snapshot, dict):
                continue
            name = snapshot.get('path', snapshot.get('file'))
            storage = snapshot.get('storage', {})
            if not name or not isinstance(storage, dict):
                continue
            q = path.parent / Path(name).name
            if q.is_relative_to(ROOT / 'resultados') or q.is_relative_to(ROOT / 'checkpoints'):
                snapshots_expected.setdefault(q.resolve(), []).append({'source': path.relative_to(ROOT).as_posix(),
                    'encoded_sha256': storage.get('encoded_sha256', snapshot.get('sha256')), 'encoded_bytes': storage.get('encoded_bytes'),
                    'decoded_sha256': storage.get('decoded_sha256'), 'decoded_bytes': storage.get('decoded_bytes')})
    checkpoint_paths = set()
    for folder in (ROOT / 'resultados', ROOT / 'checkpoints'):
        checkpoint_paths.update(folder.rglob('*.deetsnap.gz'))
        checkpoint_paths.update(folder.rglob('*.deetsnap'))
    snapshot_rows = []
    for path in sorted(checkpoint_paths):
        row = ref(path)
        h = hashlib.sha256()
        length = 0
        try:
            with (gzip.open(path, 'rb') if path.name.endswith('.gz') else path.open('rb')) as f:
                for block in iter(lambda: f.read(1024 * 1024), b''):
                    h.update(block)
                    length += len(block)
            row.update(decoded_bytes=length, decoded_sha256=h.hexdigest(), gzip_crc_verified=path.name.endswith('.gz'))
            expected = snapshots_expected.get(path.resolve(), [])
            row['primary_references'] = expected
            row['all_recorded_storage_fields_match'] = all(
                (value.get('encoded_sha256') in (None, row['sha256'])) and (value.get('encoded_bytes') in (None, row['bytes'])) and
                (value.get('decoded_sha256') in (None, row['decoded_sha256'])) and (value.get('decoded_bytes') in (None, length)) for value in expected)
            row['status'] = 'INTEGRITY_OK' if row['all_recorded_storage_fields_match'] else 'REFERENCE_MISMATCH'
        except Exception as error:
            row.update(status='READ_OR_CRC_ERROR', error=repr(error))
        snapshot_rows.append(row)
    wave_path = ROOT / 'resultados/auditoria/CRECIMIENTO_OCUPACION/MEDICIONES.json'
    wave = read(wave_path) if wave_path.exists() else None
    passive_copies = None
    if wave and wave.get('first_birth') and wave.get('profile'):
        passive_copies = wave['first_birth']['tick'] - wave['profile'][0]['tick'] + 1
    clock = budget_clock(budget)
    machine = ROOT / 'revision/MAQUINA.json'
    resources = {'schema': 'CPC9.resources.accounting.v1', 'mode': 'SEALED_AUDIT' if a.sealed else 'PRESEAL_AUDIT',
        'clock': clock, 'budget_source': ref(budget_path), 'machine_source': ref(machine) if machine.exists() else None,
        'machine_observation': read(machine) if machine.exists() else None,
        'jobs': jobs, 'unfinished_command_records': unresolved,
        'job_totals': {'command_files': len(jobs), 'status_counts': dict(Counter(x['status'] for x in jobs)),
            'status_and_exit_counts': {str(key): value for key, value in Counter((x['status'], x['exit_code']) for x in jobs).items()},
            'native_workers_launched_with_pid': sum(bool(x['native_slot_required'] and x['worker_pid_recorded']) for x in jobs),
            'queue_wall_seconds_sum': sum(x['slot_wait_seconds'] or 0 for x in jobs),
            'elapsed_wall_seconds_sum': sum(x['elapsed_wall_seconds_including_queue'] or 0 for x in jobs),
            'nonqueue_wall_seconds_sum': sum(x['nonqueue_wall_seconds_setup_process_cleanup'] or 0 for x in jobs),
            'largest_recorded_peak_process_memory_bytes': max((x['peak_process_memory_bytes'] or 0 for x in jobs), default=0),
            'largest_recorded_peak_job_memory_bytes': max((x['peak_job_memory_bytes'] or 0 for x in jobs), default=0),
            'limits_used_bytes': dict(Counter(str(x['memory_limit_bytes']) for x in jobs)),
            'cpu_seconds': None, 'energy_joules': None},
        'measurement_contract': {'elapsed_is_not_CPU': True, 'job_sums_are_not_campaign_duration': True,
            'queue_is_not_simulated_ticks': True, 'ticks_are_not_wall_seconds': True,
            'peak_memory_provider': 'Recorded Windows JobObject PeakProcessMemoryUsed/PeakJobMemoryUsed; committed memory, not an electrical-energy measurement.',
            'CPU': 'No per-job CPU counters were recorded; none is inferred from elapsed or queue time.',
            'electrical_energy': 'Not measured; no conversion from s_reg, time or TDP.',
            'basic_buffer_formula': '32*N**3 bytes, plus native structures, observer arrays, Python, copies and metadata.',
            'main_N': 67, 'main_basic_buffer_bytes': 32 * 67**3,
            'scope': 'Only this campaign jobs/artifacts. No unrelated process or team was inspected.'},
        'primary_container_totals': {'containers': len(primary), 'reported_counts_sum_not_independent_individuals': dict(totals),
            'status_counts': dict(Counter(str(x['status']) for x in primary)), 'rows': primary,
            'counting_limit': 'MEDICIONES.json and MEASUREMENTS.json under root/front result directories only; indexes/summaries are not counted again. Reported counts remain even in failed/partial attempts. They are declarations, not a global census of all native worlds, nor independent scientific replications. Fields forks and diagnostic_forks are kept distinct, not blindly added.'},
        'explicit_wave_reconciliation': {'source': ref(wave_path) if wave else None,
            'passive_pre_tick_world_forks': passive_copies, 'retained_birth_parent_copies': int(bool(wave and wave.get('first_birth'))),
            'lesion_or_sham_forks': wave.get('diagnostic_forks') if wave else None,
            'interpretation': '73 physical pre-tick copies (one retained at first birth) plus2 later diagnostic interventions. No new independent trained individuals; no copy was returned to MAIN.'},
        'main_individuals_in_this_genealogy': 1,
        'regeneration_budget': 'Future clean verification has a new explicitly invoked finite budget; PRESUPUESTO original is never restarted.'}
    required = ['LEER_PRIMERO.md', 'LEEME.md', 'USO_PRIVADO.md', 'PROVENANCE.json', 'DEPENDENCIAS.json', 'REANUDACION.json',
                'revision/LECTURA_PROVISIONAL.md', 'revision/NSM65_EVIDENCIAS.json', 'revision/CALCULOS.json', 'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl',
                'tools/sintesis_cpc9.py', 'tools/auditar_composicion_e1.py']
    controls = {'schema': 'CPC9.closure.control.v1', 'mode': resources['mode'], 'observed_utc': clock['observed_utc'],
        'status': 'PRESEAL_CHECKS_RECORDED_NOT_RELEASE_VERIFICATION',
        'required_file_presence': {name: (ROOT / name).is_file() for name in required},
        'root_checkpoint_audit': {'files': len(snapshot_rows), 'compressed_or_stored_bytes': sum(x['bytes'] for x in snapshot_rows),
            'decoded_bytes': sum(x.get('decoded_bytes', 0) for x in snapshot_rows),
            'with_recorded_storage_references': sum(bool(x.get('primary_references')) for x in snapshot_rows),
            'without_storage_references_hash_and_CRC_only': sum(not bool(x.get('primary_references')) for x in snapshot_rows),
            'status_counts': dict(Counter(x['status'] for x in snapshot_rows)), 'rows': snapshot_rows,
            'scope': 'Root resultados/checkpoints; front_relations snapshot integrity is separately preserved in front_relations/revision/CHECKPOINTS_INTEGRIDAD.json.',
            'does_not_claim_native_reproduction': True},
        'technical_failures_preserved': [
            {'job': 'ROOT_LATE_MEMORY_CAUSAL', 'state': 'Worker ran, assertion failed', 'reason': 'The first late-memory diagnostic failed the full-future match after not accounting for the pending current reader.',
             'primary': 'resultados/auditoria/MEMORIAS_TARDIAS_2283/MEDICIONES.json', 'job_error': 'jobs/ROOT_LATE_MEMORY_CAUSAL/stderr.log'},
            {'job': 'ROOT_LATE_MEMORY_CAUSAL_AUDIT_R1', 'state': 'SyntaxError before Runtime', 'archived_code': 'genealogia/code_by_hash/97b178ebf9c404acb164d804ab07b8ee53aa0b7ef5729781cd77172343c959df.py',
             'job_error': 'jobs/ROOT_LATE_MEMORY_CAUSAL_AUDIT_R1/stderr.log', 'not_participant_failure': True},
            {'job': 'ROOT_LATE_MEMORY_CAUSAL_AUDIT_R1_SYNTAXFIX', 'state': 'Final corrected audit measured',
             'primary': 'resultados/auditoria/MEMORIAS_TARDIAS_2283_R1/MEDICIONES.json', 'diagnostic_forks': 5,
             'not_MAIN_learning': True}],
        'archival_syntax_policy': 'Historical invalid source is retained under genealogy with its failure. AST validation applies only to active code, never claims that archival failed exports compile.',
        'job_lifecycle_control': {'completed_workers_without_wait_or_closed_job': [x['name'] for x in jobs if x['worker_pid_recorded'] and (x['owned_worker_waited'] is not True or x['owned_job_closed'] is not True)],
            'start_only_records': unresolved, 'foreign_process_scan': False,
            'external_Core_proof_policy': 'Core clean proof may still be executing in its own supervised job. jobs/core_CLEAN_* is deliberately outside the CPC9 ZIP; its final receipt is delivered externally. This preseal audit does not claim all campaign processes are already closed.',
            'interpretation': 'A missing final record is not proof of an active Runtime. Resolve owned START-only records explicitly before final release.'},
        'release_checks_still_external': ['Candidate seal and source selection fingerprint', 'Exact ZIP hash/CRC/manifests',
            'New isolated offline installation', 'Fresh seven-segment E1 replay and causal control', 'Cross-process persistence and later interaction',
            'Primary-data recalculation', 'Transport segmentation and full byte reconstruction'],
        'integrity_vs_reproduction': 'CRC/hashes establish bytes; physical replay establishes the listed finite functional contracts. Neither alone demonstrates NSM65 acquisition.'}
    resources['auditor_elapsed_seconds'] = time.monotonic() - start
    write(a.out / 'RECURSOS_Y_COSTES.json', resources)
    write(a.out / 'CONTROL_DE_CIERRE.json', controls)
    unresolved_count = sum(x['cancellation'] is None and not x['external_Core_verification_not_in_CPC9_payload'] for x in unresolved)
    external_core_count = sum(x['external_Core_verification_not_in_CPC9_payload'] for x in unresolved)
    md = ('# Control técnico de cierre CPC9\n\n'
          'Auditoría pasiva anterior al sello; no es todavía verificación del ZIP final. No se creó ni avanzó ningún Runtime.\n\n'
          f"Se localizaron {len(jobs)} registros COMMAND y {len(unresolved)} START sin COMMAND ({unresolved_count} de CPC9 sin cancelación explícita; {external_core_count} de verificación Core externa). "
          'COMPLETED significa fin de proceso: se conservan códigos de salida no cero y resultados adversos. Las esperas de cola y el tiempo de pared no se convierten en CPU. No se midió electricidad.\n\n'
          f"Se verificaron por streaming {len(snapshot_rows)} checkpoints root: SHA-256 del archivo, CRC gzip y SHA-256/longitud descomprimidos, contrastados con recibos de almacenamiento cuando existen. "
          'La integridad de bytes no sustituye reproducción física.\n\n'
          f"La onda incluyó {passive_copies} copias pasivas pre-tick, además de dos forks de corte/sham; no son75 individuos. "
          'El fallo de reconstrucción tardía V1 y la revisión V2 con SyntaxError antes del Runtime permanecen; R1 corregida se registró por separado.\n\n'
          'E1 sigue siendo una genealogía principal; preparaciones auxiliares, forks y reproducciones técnicas no se suman como conocimientos simultáneos ni réplicas independientes. '
          'Los detalles y localizadores constan en RECURSOS_Y_COSTES.json y CONTROL_DE_CIERRE.json. Falta sellar, extraer e instalar el ZIP exacto y ejecutar su comprobación externa.\n')
    (a.out / 'CONTROL_DE_CIERRE.md').write_text(md, encoding='utf-8')
    print(json.dumps({'jobs': len(jobs), 'primary_containers': len(primary), 'root_checkpoints': len(snapshot_rows),
        'checkpoint_failures': sum(x['status'] != 'INTEGRITY_OK' for x in snapshot_rows), 'start_only_unresolved': unresolved_count,
        'external_Core_proof_pending': external_core_count,
        'passive_wave_copies': passive_copies, 'elapsed_seconds': time.monotonic() - start}, ensure_ascii=False))


if __name__ == '__main__':
    main()
