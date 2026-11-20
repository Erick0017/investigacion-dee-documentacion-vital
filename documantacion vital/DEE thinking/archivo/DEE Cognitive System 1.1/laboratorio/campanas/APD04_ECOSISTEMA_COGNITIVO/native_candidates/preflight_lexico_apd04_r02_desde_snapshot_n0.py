"""Pure offline full-snapshot preflight; no engine import or new Native ticks."""
from pathlib import Path
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[4]
LAB = ROOT / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
OUT = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/ADMISION_LEXICA_R01/PREFLIGHT_R02_N0.json'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    source = LAB / 'native_candidates/lexico_compartido_apd04_r02.py'
    lex = load('prospective_diagonal_lexical_design', source)
    observer_path = ROOT / 'sistema/capacidades/observador_causal_retrospectivo_01.py'
    observer = load('existing_offline_full_snapshot_observer', observer_path)
    record = json.loads((ROOT / 'sistema/estado/vidas/APD04_CALIB_R02/VIDA.json').read_text(encoding='utf8'))
    path = ROOT / 'sistema' / record['snapshot']
    snapshot = observer.Snapshot(path)
    if snapshot.encoded_sha256 != 'daeafab436a2b9aed2029b6c91744b6f7677b66fc676bd16f6975b5aa21a5a91':
        raise ValueError('Another AUX continuation exists; no favorable snapshot substitution')
    design = lex.geometry()
    rows = []
    for row in design['preparation_sites'] + design['new_ports'] + design['new_hubs']:
        rows.append({**row, 'requires_RAW_zero': True})
    for row in design['common_reader']:
        rows.append({**row, 'requires_RAW_zero': row['form'] in lex.NEW_FORMS,
            'historical_read_only': row['form'] not in lex.NEW_FORMS})
    for row in rows:
        row['observation'] = snapshot.observation(row['site'])
    conflicts = [row for row in rows if row['requires_RAW_zero'] and int(row['observation']['raw'])]
    static = lex.compatibility_geometry()
    result = {'schema': 'APD04.lexical.offline_preflight.v1',
        'revision': 'R02_positive_XY_second_and_final_declared_design',
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'source_file': source.relative_to(ROOT).as_posix(),
        'observer_file': observer_path.relative_to(ROOT).as_posix(),
        'observer_sha256': hashlib.sha256(observer_path.read_bytes()).hexdigest(),
        'life': 'APD04_CALIB_R02', 'tick': snapshot.tick,
        'full_snapshot': path.relative_to(ROOT).as_posix(),
        'snapshot_sha256': snapshot.encoded_sha256,
        'snapshot_checksum_valid': snapshot.checksum_valid,
        'static_compatibility': static, 'geometry': design,
        'all_sources_hubs_gates': rows, 'required_RAW_zero_conflicts': conflicts,
        'admissible_at_this_snapshot': not conflicts and static['admissible_static_design'],
        'native_ticks': 0, 'Runtime_created': False,
        'physical_admission_performed': False,
        'source_choice_not_based_on_teaching_accuracy': True,
        'scope': 'Offline vacancy only at the actual rejected AUX postSTOP cut. '
                 'Live P0 admission must recheck full RAW at its actual operation tick. '
                 'No success, causal isolation, acquired word or retained function follows from this preflight.'}
    if OUT.exists():
        raise FileExistsError('Preserve the original R02 passive preflight; do not replace it')
    with OUT.open('x', encoding='utf8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({key: result[key] for key in (
        'source_sha256', 'tick', 'snapshot_sha256', 'snapshot_checksum_valid',
        'required_RAW_zero_conflicts', 'admissible_at_this_snapshot', 'native_ticks', 'Runtime_created')},
        ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
