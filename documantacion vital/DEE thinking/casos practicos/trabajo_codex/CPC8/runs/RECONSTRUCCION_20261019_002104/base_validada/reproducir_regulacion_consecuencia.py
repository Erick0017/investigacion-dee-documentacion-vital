"""Exact finite historical consequence-to-policy apparatus on installed DEE4.5.

The preserved preparation is imported without changing its geometry or physics.
Historical results are compared only AFTER the fresh trajectories have ended.
RAW cuts are confined to labelled diagnostic forks and never returned to MAIN.
"""
from array import array
from datetime import datetime, timezone
from pathlib import Path
import argparse
import gc
import hashlib
import importlib.util
import json
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OLD_SHA = '65164c939621464c7d4faa800240bb1c2e25538ba9d878a65863016f57387c00'
PREPARATION_SHA = '207340cbf82f1464d328041c840a2a6e2b223751d19cb29c40b41fd56563aad7'
CASE_IDS = ('REG_V2_P21', 'REG_V2_H21', 'REG_V2_D21', 'REG_V2_D22', 'REG_V2_R21', 'REG_V2_R22')
FRAME_TICKS = (0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 15, 18)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def physical(world):
    runtime = world.runtime
    return {'tick': int(runtime.current_tick),
            'RAW_sha256': hashlib.sha256(array('Q', runtime.raw_copy()).tobytes()).hexdigest(),
            'clock_sha256': hashlib.sha256(array('Q', runtime.clock_copy()).tobytes()).hexdigest()}


def operation(world):
    from dee_thinking.consolidated import exact_receipt
    return {'channels': list(world.runtime.channel_names),
            'receipts': [exact_receipt(receipt) for receipt in world.runtime.receipts],
            'snapshot_metadata': dict(world.runtime.snapshot_metadata_entries)}


def extract_selected():
    destination = ROOT / 'genealogia/primer_cpc8/regulacion_v2'
    provenance = destination / 'PROVENANCE.json'
    if provenance.exists():
        inventory = json.loads(provenance.read_text(encoding='utf-8'))
        assert inventory['source_zip_sha256'] == OLD_SHA
        for row in inventory['members']:
            assert sha(destination / row['local']) == row['sha256']
        return destination
    candidates = list((ROOT.parent / 'historico').glob('*' + OLD_SHA + '.zip'))
    if len(candidates) != 1:
        raise FileNotFoundError('Exactly one verified protected historical source is required for initial selective extraction')
    archive = candidates[0]
    assert sha(archive) == OLD_SHA
    members = ['CPC8/src/regulacion/native_feedback.py', 'CPC8/src/regulacion/run_feedback.py',
               'CPC8/revision/REGULACION_ADQUIRIDA.json']
    for case_id in CASE_IDS:
        members += ['CPC8/resultados/regulacion/' + case_id + '/' + name for name in
                    ('CONFIG.json', 'OBSERVACIONES.json', 'RESULT.json', 'T0.deetsnap.gz', 'T9.deetsnap.gz', 'T18.deetsnap.gz')]
    rows = []
    with zipfile.ZipFile(archive) as source:
        for member in members:
            payload = source.read(member)
            relative = member.removeprefix('CPC8/')
            path = destination / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                assert path.read_bytes() == payload
            else:
                path.write_bytes(payload)
            rows.append({'source_member': member, 'local': relative, 'bytes': len(payload),
                         'sha256': hashlib.sha256(payload).hexdigest(), 'CRC32': '%08x' % source.getinfo(member).CRC})
    put(provenance, {'schema': 'CPC8R.regulation.V2.selected.provenance.v1', 'source_zip_sha256': OLD_SHA,
                     'members': rows, 'scope': 'Byte-exact selected historical sources and six primary cases; no nested historical ZIP.'})
    return destination


def capture(module, world, geometry, tick):
    frame = {'tick': tick, 'panel': {key: module.record(world, site) for key, site in geometry['ports'].items()}}
    if tick in (4, 5, 8, 9, 11, 12):
        selected = [(key, site) for key, site in geometry['ports'].items() if
                    (tick in (4, 5) and key.startswith('comparison.')) or
                    (tick in (8, 9) and key.startswith('policy.')) or
                    (tick in (11, 12) and key.startswith('interception.'))]
        frame['Moore27'] = {key: module.neighborhood(world, site) for key, site in selected}
    return frame


def delivery(frames, geometry, context):
    panel = next(row['panel'] for row in frames if row['tick'] == 15)
    rows = []
    for regulator in geometry['regulators']:
        observed = panel['delivery.' + regulator['id']]
        rows.append({'id': regulator['id'], 'source': regulator['source'], 'observed': observed,
                     'exact_useful_packet': observed['state'] > 0 and observed['semantic'] != 5 and
                     observed['s_reg'] == 3 and observed['direction'] == [1, 0, 0]})
    return {'delivery_by_route': rows,
            'requested_deliveries': sum(row['exact_useful_packet'] and row['source'] == context for row in rows),
            'other_deliveries': sum(row['exact_useful_packet'] and row['source'] != context for row in rows)}


def causal_forks(module, parent, geometry, context, output):
    from dee_thinking import _native as native
    from dee_thinking.persistence import save_world_snapshot
    before_physical, before_operation = physical(parent), operation(parent)
    site = geometry['ports']['actual_before_merge.1']
    before = module.record(parent, site)
    assert before['state'] > 0 and before['s_reg'] == 1
    rows = []
    for condition in ('formed_actual_return_cut_T4', 'identical_RAW_return_sham_T4'):
        edit = native.ResearchStateEdit()
        edit.coordinate = native.Coordinate(*site)
        edit.raw = int(before['raw']) if 'sham' in condition else 0
        edit.clock = None
        edit.label = condition
        fork = parent.diagnostic_fork([edit], True)
        after = module.record(fork, site)
        fork_operation = operation(fork)
        original_operation_preserved = (fork_operation['channels'] == before_operation['channels'] and
                                        fork_operation['receipts'] == before_operation['receipts'] and
                                        all(fork_operation['snapshot_metadata'].get(key) == value for key, value in before_operation['snapshot_metadata'].items()))
        added_metadata = {key: value for key, value in fork_operation['snapshot_metadata'].items()
                          if key not in before_operation['snapshot_metadata']}
        assert added_metadata == {'dee_thinking.diagnostic_fork': 'true', 'dee_thinking.diagnostic_edit_count': '1'}
        row = {'condition': condition, 'modality': 'DIAGNOSTIC_FORK', 'parent_tick': 4,
               'pre_physical': physical(fork), 'intervention': {'site': site, 'before': before, 'after': after,
               'before_Moore27': module.neighborhood(parent, site), 'after_Moore27': module.neighborhood(fork, site),
               'clock_preserved': before['clock'] == after['clock']},
               'original_queue_channels_metadata_preserved': original_operation_preserved,
               'explicit_native_diagnostic_metadata_added': added_metadata, 'frames': []}
        for tick in FRAME_TICKS:
            if tick < 4:
                continue
            fork.run_until(tick)
            row['frames'].append(capture(module, fork, geometry, tick))
        row.update(delivery(row['frames'], geometry, context))
        row['final_physical'] = physical(fork)
        row['parent_unchanged'] = physical(parent) == before_physical and operation(parent) == before_operation
        row['snapshot'] = save_world_snapshot(fork, output / (condition + '_T18.deetsnap.gz'))
        put(output / (condition + '_MEASUREMENTS.json'), row)
        assert row['parent_unchanged'] and row['intervention']['clock_preserved'] and row['original_queue_channels_metadata_preserved']
        rows.append(row)
        del fork
        gc.collect()
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    started, cpu_started = time.monotonic(), time.process_time()
    import dee_thinking as dee
    from dee_thinking.persistence import load_world_snapshot, save_world_snapshot
    assert dee.__version__ == '4.5.0' and dee.kernel_identity()['kernel_version'] == 27
    assert sha(dee._native.__file__) == '17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
    assert Path(dee.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
    selected = extract_selected()
    source_path = selected / 'src/regulacion/native_feedback.py'
    assert sha(source_path) == PREPARATION_SHA
    spec = importlib.util.spec_from_file_location('preserved_regulation_V2', source_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    configurations = [json.loads((selected / 'resultados/regulacion' / case_id / 'CONFIG.json').read_text(encoding='utf-8')) for case_id in CASE_IDS]
    frozen = {'schema': 'CPC8R.consequence.policy.reference.frozen.v1', 'frozen_utc': datetime.now(timezone.utc).isoformat(),
              'adapter_sha256': sha(Path(__file__)), 'preparation_sha256': PREPARATION_SHA,
              'identity': {'library': dee.__version__, 'native': dee._native.__file__, 'python': sys.executable, 'kernel': dee.kernel_identity()},
              'case_configs_sha256': {case_id: sha(selected / 'resultados/regulacion' / case_id / 'CONFIG.json') for case_id in CASE_IDS},
              'domain': 'Original six configurations literally: P21/H21/D21/D22 N67; translated R21/R22 N131. No geometry resizing.',
              'prediction': 'Current native medium direction changes comparison and prepared P/Q policy; intact positive/reserves deliver3 on corresponding route at15. Selective formed-return cuts should remove that effect; identicalRAWshams preserve full states.',
              'horizon': 18, 'functional_target_tick': 15, 'classification': 'Reproduction of finite consequence-updated policy under a prepared R14 rule, NOT learned general regulation strategy and NOT current E1 integration.',
              'counting': {'independent_preparations': 6, 'audit_forks': 4, 'new_E1_preparations': 0},
              'host_postT0_inputs': 0, 'host_RAW_clock_edits_on_MAIN': [],
              'evaluation_information': 'Context labels and historical expected outcomes are auditor-only; participant.prepare receives only original current-world medium and preparation geometry.'}
    put(output / 'FROZEN.json', frozen)
    rows = []
    for config in configurations:
        case_id = config['case_id']
        target = output / case_id
        target.mkdir()
        geometry = config['geometry']
        assert config['preparation_code_sha256'] == PREPARATION_SHA
        world, actual_geometry = module.prepare(medium=geometry['medium'], mode=geometry['mode'], translation=tuple(geometry['translation']), n=geometry['N'], lanes=tuple(geometry['lanes']))
        assert actual_geometry == geometry
        entry = physical(world)
        historical_initial, _ = load_world_snapshot(selected / 'resultados/regulacion' / case_id / 'T0.deetsnap.gz')
        initial_equal = entry == physical(historical_initial)
        del historical_initial
        gc.collect()
        frames, checkpoints, diagnostic = [], [], []
        put(target / 'CONFIG.json', config)
        for tick in range(19):
            world.run_until(tick)
            if tick in FRAME_TICKS:
                frames.append(capture(module, world, actual_geometry, tick))
                put(target / 'OBSERVACIONES.json', frames)
            if tick in (0, 4, 9, 15, 18):
                checkpoints.append(save_world_snapshot(world, target / ('T' + str(tick) + '.deetsnap.gz')))
            if tick == 4 and case_id in ('REG_V2_P21', 'REG_V2_H21'):
                diagnostic = causal_forks(module, world, actual_geometry, config['evaluation_context_not_given_to_participant'], target)
        final = physical(world)
        observed_delivery = delivery(frames, actual_geometry, config['evaluation_context_not_given_to_participant'])
        # Historical targets enter only this post-trajectory auditor comparison.
        historical_result = json.loads((selected / 'resultados/regulacion' / case_id / 'RESULT.json').read_text(encoding='utf-8'))
        historical_frames = json.loads((selected / 'resultados/regulacion' / case_id / 'OBSERVACIONES.json').read_text(encoding='utf-8'))
        parity = {'initial_full_physical_equal': initial_equal,
                  'final_RAW_equal': final['RAW_sha256'] == historical_result['final_RAW_sha256'],
                  'final_clocks_equal': final['clock_sha256'] == historical_result['final_clock_sha256'],
                  'final_tick_equal': final['tick'] == historical_result['final_tick'],
                  'all_recorded_fields_neighborhoods_and_clocks_equal': frames == historical_frames,
                  'functional_delivery_equal': all(observed_delivery[key] == historical_result[key] for key in observed_delivery)}
        for branch in diagnostic:
            if 'sham' in branch['condition']:
                branch['full_final_equal_MAIN'] = branch['final_physical'] == final
                assert branch['full_final_equal_MAIN']
        result = {'case_id': case_id, 'mode': geometry['mode'], 'N': geometry['N'],
                  'modality': 'HISTORICAL_REFERENCE_REPRODUCTION', 'historical_configuration_sha256': frozen['case_configs_sha256'][case_id],
                  'pre_physical': entry, 'final_physical': final, 'final_operations': operation(world),
                  'checkpoints': checkpoints, 'diagnostic_forks': diagnostic, 'historical_parity': parity,
                  'postT0_host_experience_calls': 0, 'RAW_clock_edits_on_MAIN': [], **observed_delivery}
        result['status'] = 'PASS' if all(parity.values()) else 'FAIL'
        put(target / 'MEASUREMENTS.json', result)
        rows.append({'case_id': case_id, 'N': geometry['N'], 'requested_deliveries': observed_delivery['requested_deliveries'],
                     'other_deliveries': observed_delivery['other_deliveries'], 'status': result['status'],
                     'historical_parity': parity, 'diagnostic_forks': [{'condition': branch['condition'], 'requested_deliveries': branch['requested_deliveries'],
                     'other_deliveries': branch['other_deliveries'], 'final_physical': branch['final_physical']} for branch in diagnostic]})
        put(output / 'INCREMENTAL.json', {'status': 'RUNNING', 'cases': rows})
        del world
        gc.collect()
    summary = {'schema': 'CPC8R.consequence.policy.reference.summary.v1', 'status': 'PASS' if all(row['status'] == 'PASS' for row in rows) else 'FAIL',
               'cases': rows, 'counting': frozen['counting'], 'elapsed_seconds': time.monotonic() - started,
               'cpu_seconds': time.process_time() - cpu_started,
               'scope': frozen['classification'], 'source_selected_provenance': (selected / 'PROVENANCE.json').relative_to(ROOT).as_posix(),
               'source_sha256': sha(Path(__file__))}
    put(output / 'SUMMARY.json', summary)
    print(json.dumps(summary, ensure_ascii=False))
    if summary['status'] != 'PASS':
        raise AssertionError('Historical parity mismatch; actual observations retained')


if __name__ == '__main__':
    main()
