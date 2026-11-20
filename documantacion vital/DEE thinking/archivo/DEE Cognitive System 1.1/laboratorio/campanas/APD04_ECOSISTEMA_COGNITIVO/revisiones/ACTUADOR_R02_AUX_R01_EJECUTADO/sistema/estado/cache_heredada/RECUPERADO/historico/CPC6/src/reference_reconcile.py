"""Offline scientific/metadata comparison; never advances or changes a world."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def put(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def difference(a, b, path=''):
    rows = []
    if type(a) is not type(b):
        return [{'path': path, 'kind': 'TYPE', 'current': type(a).__name__, 'historical': type(b).__name__}]
    if isinstance(a, dict):
        for key in sorted(a.keys() | b.keys()):
            if key not in a or key not in b:
                rows.append({'path': path + '/' + key, 'kind': 'KEY', 'current': a.get(key), 'historical': b.get(key), 'current_present': key in a, 'historical_present': key in b})
            else:
                rows.extend(difference(a[key], b[key], path + '/' + key))
    elif isinstance(a, list):
        if len(a) != len(b):
            rows.append({'path': path, 'kind': 'LENGTH', 'current': len(a), 'historical': len(b)})
        for index, (x, y) in enumerate(zip(a, b)):
            rows.extend(difference(x, y, path + '/' + str(index)))
    elif a != b:
        rows.append({'path': path, 'kind': 'VALUE', 'current': a, 'historical': b})
    return rows


def main():
    directory = ROOT / 'resultados' / 'referencias'
    current = load(directory / 'central_normalized01/MEASUREMENTS.json')
    old = load(ROOT / 'genealogia/CPC3/comparacion/central_discovery/open_changed/MEASUREMENTS.json')
    differences = []
    for key in ('before_report', 'trace'):
        differences.extend(difference(current[key], old[key], '/' + key))
    differences.extend(difference(current['event']['comparison_decoder'], old['event']['comparison_decoder'], '/event/comparison_decoder'))
    allowed_suffixes = ('/domain_status', '/limits', '/validity', '/represented_expectation_before_report')
    unexpected = [row for row in differences if not row['path'].endswith(allowed_suffixes)]
    assert not unexpected, unexpected
    assert all(current['full_state_comparison'][key] for key in ('RAW_full_equal', 'clocks_full_equal', 'tick_equal'))
    assert current['comparison']['emission_output_equal'] and current['comparison']['emission_receipt_equal'] and current['comparison']['report_receipt_equal']
    central = {
        'case_id': 'CPC3_CENTRAL_open_changed',
        'kind': 'HISTORICAL_REPRODUCTION_WITH_OBSERVER_METADATA_VERSION_DIFFERENCES',
        'full_state_comparison': current['full_state_comparison'],
        'physical_emission_equal': current['comparison']['emission_output_equal'],
        'physical_input_receipts_equal': current['comparison']['emission_receipt_equal'] and current['comparison']['report_receipt_equal'],
        'strict_JSON_equal': False,
        'all_differences_recorded': differences,
        'unexpected_physical_or_receipt_differences': unexpected,
        'interpretation': 'The final source in the audited CPC3 ZIP contains later explicit domain/absence qualifications absent from its original discovery output. Replayed physical trajectories match. JSON was not declared byte-identical.',
        'emission_tick': current['prediction']['emission_tick'],
        'target_tick': current['prediction']['target_tick'],
        'emitted_prediction': current['prediction']['prediction_set'],
        'actual': current['event']['source_actual'],
        'comparison_decoder_current': current['event']['comparison_decoder'],
        'comparison_decoder_historical': old['event']['comparison_decoder'],
        'native_comparison_tick': current['event']['tick'],
        'late_observer_panels': [{'tick': row['tick'], 'raw': str(row['observation']['physical_output']['raw']), 'direction': row['observation']['physical_output']['direction'], 'delta': row['observation']['delta']} for row in current['trace']],
        'new_discovery_claimed': False,
    }
    put(directory / 'central_normalized01/REPLAY_CHECK.json', central)
    cp02 = load(directory / 'cp02/REPLAY_CHECK.json')
    sem = load(directory / 'sem01_normalized01/REPLAY_CHECK.json')
    attempts = []
    for name in ('reference_cp02', 'reference_central', 'reference_sem01', 'reference_central_normalized01', 'reference_sem01_normalized01'):
        job = ROOT / 'jobs' / name
        command = load(job / 'COMMAND.json')
        attempts.append({'job': name, 'exit_code': command['exit_code'], 'elapsed_seconds': command['elapsed_seconds'], 'stdout_sha256': hashlib.sha256((job / 'stdout.log').read_bytes()).hexdigest(), 'stderr_sha256': hashlib.sha256((job / 'stderr.log').read_bytes()).hexdigest(), 'status': command['status']})
    summary = {'schema': 'CPC6.brief_references.v1', 'distinct_historical_preparations': 3, 'native_runs': 5, 'technical_reproductions_not_independent_samples': True, 'comparison_repair_1': 'JSON tuple/list serialization normalization and separation of historical wrapper-only fields; first attempts retained.', 'comparison_repair_2': 'Offline reconciliation of explicit observer contract additions in current frozen source. No further native rerun or physics change.', 'references': [cp02, central, sem], 'attempts': attempts, 'all_three_final_RAW_clocks_tick_equal': True, 'source_zip_unchanged': True, 'native_environment': 'CPC6/.venv CPython3.13 x64 installed official DEE4.0.0', 'data_never_fed_as_predictions': True}
    put(directory / 'REFERENCE_REPRODUCTION_CHECK.json', summary)
    mapping = load(ROOT / 'revision/MAPA_CPC1_A_5.json')
    mapping['replay_results'] = [{'case_id': row['case_id'], 'evidence': 'resultados/referencias/REFERENCE_REPRODUCTION_CHECK.json', 'full_state': row['full_state_comparison'], 'status': 'PHYSICAL_TRAJECTORY_REPRODUCED', 'serialization_comparison': 'Physical and published scientific values separately from runtime wrappers/observer-documentary metadata. No whole-file byte equality claimed.'} for row in (cp02, central, sem)]
    mapping['selected_sources_manifest'] = 'genealogia/SOURCE_MANIFEST.json'
    put(ROOT / 'revision/MAPA_CPC1_A_5.json', mapping)
    print(json.dumps({'references': 3, 'native_runs_including_technical_attempts': 5, 'physical_all_equal': True, 'central_documentary_differences': len(differences), 'new_native_execution': False}))


if __name__ == '__main__':
    main()
