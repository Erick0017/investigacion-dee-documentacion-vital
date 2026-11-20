"""Offline source/interface check at the sealed complete MAIN prefix, no ticks."""
from pathlib import Path
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[4]
LAB = ROOT / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
PAIR = ROOT / 'sistema/estado/fuentes_emparejadas/APD04_MAIN_T639374_EXPLORACION_R01'
OUT = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/PREFLIGHT_SENSOR_R04_N0.json'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    sensor_path = LAB / 'native_candidates/sensor_dos_pares_balanceados_apd04_r04.py'
    sensor = load('declared_four_source_sensor', sensor_path)
    observer_path = ROOT / 'sistema/capacidades/observador_causal_retrospectivo_01.py'
    observer = load('existing_offline_whole_snapshot_reader', observer_path)
    snapshot = observer.Snapshot(PAIR / 'VIDA.deetsnap.gz')
    if snapshot.encoded_sha256 != '771e041363b39ef830603cb32ed2bbe7fc5938e4783a9dfe2a733a6e3ee4f9a8':
        raise ValueError('Another prefix was supplied; do not inspect a favorable replacement')
    design = sensor.specification()
    source_observations = [snapshot.observation(site) for site in
        design['inherited_tag_sources'] + design['new_goal_sources']]
    raw_conflicts = [row for row in source_observations if int(row['raw'])]
    existing = [{'name': name, **channel} for name, channel in snapshot.channels.items()
                if channel['site'] in design['new_goal_sources']]
    lex = load('finite_current_lexical_geometry', LAB / 'native_candidates/lexico_compartido_apd04_r02.py')
    inventory = lex._inventory(lex.FORM_CODEC)
    lexical_points = {tuple(row['site']) for rows in inventory.values() for row in rows}
    lexical_intersection = sorted({tuple(site) for site in design['new_goal_sources']} & lexical_points)
    result = {'schema': 'APD04.four_source_sensor.offline_preflight.v1',
        'source_file': sensor_path.relative_to(ROOT).as_posix(),
        'source_sha256': hashlib.sha256(sensor_path.read_bytes()).hexdigest(),
        'observer_file': observer_path.relative_to(ROOT).as_posix(),
        'observer_sha256': hashlib.sha256(observer_path.read_bytes()).hexdigest(),
        'full_snapshot': (PAIR / 'VIDA.deetsnap.gz').relative_to(ROOT).as_posix(),
        'snapshot_sha256': snapshot.encoded_sha256, 'tick': snapshot.tick,
        'snapshot_checksum_valid': snapshot.checksum_valid,
        'source_observations': source_observations,
        'nonzero_RAW_conflicts': raw_conflicts,
        'existing_interfaces_at_new_sources': existing,
        'current_18_form_lexical_intersection': [list(x) for x in lexical_intersection],
        'static_R04_geometry': sensor.static_compatibility(),
        'admissible_at_the_sealed_prefix': not raw_conflicts and not existing
            and not lexical_intersection and sensor.static_compatibility()['no_listed_address_overlap'],
        'new_physical_interfaces_declared': 0, 'Runtime_created': False,
        'native_ticks': 0,
        'scope': 'One prospectively fixed additional P0 sensory design. No testing of answers '
                 'selected these sources. Live actual-tick preflight remains mandatory; '
                 'neither useful processing, acquired contextual attention nor isolation is established.'}
    if OUT.exists():
        raise FileExistsError('Preserve the original passive preflight')
    with OUT.open('x', encoding='utf8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({key: result[key] for key in ('source_sha256', 'tick',
        'source_observations', 'existing_interfaces_at_new_sources',
        'current_18_form_lexical_intersection', 'admissible_at_the_sealed_prefix',
        'Runtime_created', 'native_ticks')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
