"""One frozen fresh MCTS+coupled-regulation candidate, not the selected MAIN."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys
import time
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from integracion.quantity_core import physical
from transferencia_magnitud.run_cts import SOURCES
from regulacion_acoplada.mcts import CoupledMagnitudeCTSSession


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', required=True)
    parser.add_argument('--medium', required=True, choices=(-1, 1), type=int)
    parser.add_argument('--reference', type=int, default=31)
    parser.add_argument('--objects', nargs=2, type=int, default=[16, 45])
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    primary_config = ROOT / 'configuraciones/transferencia_magnitud/CTS_CONGELADO.json'
    base_case = json.loads(primary_config.read_text(encoding='utf-8'))['cases'][0]
    sources = list(SOURCES) + ['src/transferencia_magnitud/' + name for name in ('transferencia.py', 'cts_integrado.py')]
    sources += ['src/regulacion_acoplada/' + name for name in ('aparato.py', 'mcts.py', 'run_mcts.py')]
    sources += ['src/regulacion_consecuencia/native_feedback_component.py']
    hashes = {}
    for relative in sources:
        target = args.out / 'executed_source' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
        hashes[relative] = sha(target)
    config = {'case_id': args.case, 'base_case': base_case, 'medium': args.medium, 'regulation_reference': args.reference,
              'regulation_objects': args.objects, 'only_geometry': 'Literal AUX coupling, zero initial overlaps; no translations or source base edits',
              'criterion': 'Old MCTS exact local fields at matched windows plus coupled reference/objects70/137; whole-state equality to smaller baseline not expected.',
              'frozen_before_evolution': True, 'source_sha256': hashes, 'base_configuration_sha256': sha(primary_config)}
    put(args.out / 'CONFIG.json', config)
    prepkeys = ('guard_mode', 'actor_mode', 'include_order', 'include_contact', 'event_state_offset', 'medium_load', 'actor_state', 'quantity_guards', 'regulation')
    started, cpu = time.monotonic(), time.process_time()
    session = CoupledMagnitudeCTSSession.create(identifier=args.case, medium=args.medium, **{key: value for key, value in base_case.items() if key in prepkeys})
    session.curriculum(regulation_reference=args.reference, regulation_objects=args.objects,
                       **{key: value for key, value in base_case.items() if key not in ('id', *prepkeys)})
    result = {'case_id': args.case, 'schema': 'CPC8R.coupledRegulationMCTS.measurements.v1', 'status': 'RUNNING',
              'preparations': 1, 'diagnostic_forks': 0, 'technical_continuations': 0, 'configuration': config,
              'geometry': session.geometry, 'frames': [], 'snapshots': [], 'host_MAIN_RAW_clock_edits': []}
    baseline_path = ROOT / 'resultados/transferencia_magnitud/MCTS_P01_SOURCE31/MEASUREMENTS.json'
    baseline = json.loads(baseline_path.read_text(encoding='utf-8'))
    baseline_frames = {row['tick']: row for row in baseline['frames']}
    for tick in sorted(set(baseline_frames) | {2, 4, 5, 9, 10, 11, 15, 53, 54, 69, 70, 77, 78, 79, 136, 137, 141}):
        session.run_until(tick)
        frame = session.view()
        frame['mode'].pop('captures', None)
        frame['mode'].pop('social_captures', None)
        result['frames'].append(frame)
        if tick in (0, 4, 77, 141, 549, 616):
            result['snapshots'].append(session.save(args.out / ('T' + str(tick) + '.deetsnap.gz')))
        result.update(last_complete_tick=tick, requests=session.receipts(), elapsed_seconds=time.monotonic() - started)
        put(args.out / 'INCREMENTAL.json', result)
    # Compare native observations only, after all world trajectories have run.
    common = []
    for frame in result['frames']:
        if frame['tick'] not in baseline_frames:
            continue
        main_fields = {key: value for key, value in frame.items() if key != 'coupled_regulation'}
        old = baseline_frames[frame['tick']]
        common.append({'tick': frame['tick'], 'same_observed_fields': main_fields == old,
                       'differing_top_fields': [key for key in old if main_fields.get(key) != old[key]]})
    readings = []
    for index, tick in enumerate((70, 137)):
        pre = next(frame['coupled_regulation']['quantity'] for frame in result['frames'] if frame['tick'] == tick - 1)
        post = next(frame['coupled_regulation']['quantity'] for frame in result['frames'] if frame['tick'] == tick)
        er, eo = args.reference + 5, args.objects[index] + 5
        readings.append({'tick': tick, 'reference': pre['reference_site'], 'object': pre['object_site'], 'output': post['center'],
                         'qualified': pre['reference_site']['active'] and pre['reference_site']['s_reg'] == er and pre['object_site']['active'] and pre['object_site']['s_reg'] == eo
                         and post['center']['active'] and post['center']['direction'] == [(er > eo) - (er < eo), 0, 0]})
    result.update(status='MEASURED', old_field_comparison=common, regulation_readings=readings, final_physical=physical(session.world),
                  base_primary=baseline_path.relative_to(ROOT).as_posix(), base_primary_sha256=sha(baseline_path),
                  requests=session.receipts(), elapsed_seconds=time.monotonic() - started, cpu_seconds=time.process_time() - cpu)
    put(args.out / 'MEASUREMENTS.json', result)
    print(json.dumps({'case_id': args.case, 'old_differences': [row for row in common if not row['same_observed_fields']], 'regulation': readings}))


if __name__ == '__main__':
    main()
