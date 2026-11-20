"""Selective post-acquisition counterfactuals of the zero-load regulator.

MAIN is restored intact from the saved complete t292 world. All edits are
explicit diagnostic forks. Two frozen translated preparations independently
test the same acquired-direction mechanism. No output is returned to MAIN.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT))
from common import digest, gate, identity, local_context, operational, put, receipt, record, sha
from network import regulate
from referencias.cpc4_red.regulated_session import describe


def config():
    parent = ROOT / 'resultados/network_regulation_adverse/REG_FLAT_LEARNED_PULSE/T292.deetsnap'
    return {'schema': 'CPC5.regulation.local_counterfactual.v1',
            'frozen_utc': datetime.now(timezone.utc).isoformat(),
            'parent': parent.relative_to(ROOT).as_posix(), 'parent_sha256': sha(parent),
            'fork_tick': 292, 'horizon': 437,
            'question': 'Does occupied-destination material precedence remove the learned zero-load pulse and approaching residual, and is the pulse causally needed for later access?',
            'fork_cases': [
                {'id': 'REG_CF_REFERENCE', 'mode': 'intact', 'C_history': 1},
                {'id': 'REG_CF_REMOVE', 'mode': 'remove_RAW_only', 'C_history': 1},
                {'id': 'REG_CF_SHAM', 'mode': 'identical_RAW', 'C_history': 1},
                {'id': 'REG_CF_LOAD1', 'mode': 's_reg_0_to_1_only', 'C_history': 1}],
            'reserved_cases': [
                {'id': 'REG_H_TRANSLATED_PAIRED', 'mode': 'learned_pulse', 'A_history': 1, 'C_history': 1, 'translation': [4, -3, 2]},
                {'id': 'REG_H_TRANSLATED_UNPAIRED', 'mode': 'learned_pulse_unpaired', 'A_history': 1, 'C_history': 1, 'translation': [4, -3, 2]}],
            'prediction_registered_before_forks': {
                'reference_sham': 'Full learned-pulse future retained',
                'remove': 'Removing the t292 zero-load occupied site allows the residual to enter it at293; later Flat function differs',
                'load1': 'One unit changes payload, not occupancy; physical branch and later function may remain',
                'scope': 'Predictions are evaluated only after evolution; failure is retained. Source and derivative are exact complete world forks.'}}


def run_fork(case, cfg):
    import dee_thinking as d
    folder = ROOT / 'resultados/regulation_causal' / case['id']
    if (folder / 'MEASUREMENTS.json').exists():
        return json.loads((folder / 'MEASUREMENTS.json').read_text(encoding='utf-8'))
    folder.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    parent_path = ROOT / cfg['parent']
    if sha(parent_path) != cfg['parent_sha256']:
        raise ValueError('Frozen parent changed')
    main = d.OrganizationalWorld.load_snapshot(str(parent_path))
    if main.runtime.current_tick != cfg['fork_tick']:
        raise ValueError('Wrong fork time')
    spec = describe((0, 0, 0))
    site = tuple(spec['regulation']['meeting'])
    residual = (site[0], site[1], site[2] + 1)
    pre = record(main, site)
    if not (pre['state'] == 1 and pre['semantic'] == 1 and pre['s_reg'] == 0 and pre['direction'] == [0, 0, 1]):
        raise ValueError('The actual predicted pulse is absent; do not readjust intervention')
    initial_physics, initial_operative = digest(main), operational(main)
    raw_before, clock_before = main.runtime.raw_copy(), main.runtime.clock_copy()
    operation = case['mode']
    if operation == 'intact':
        world = main.fork()
        declared = []
    else:
        new_raw = 0 if operation == 'remove_RAW_only' else int(pre['raw'])
        if operation == 's_reg_0_to_1_only':
            new_raw = d.pack_record(pre['state'], 1, *pre['direction'], pre['semantic'])
        edit = d.ResearchStateEdit()
        edit.coordinate = d.Coordinate(*site)
        edit.raw = new_raw
        edit.label = 'CPC5 explicit diagnostic regulator ' + operation
        world = main.diagnostic_fork([edit], True)
        declared = [{'site': list(site), 'before': pre, 'after': record(world, site),
                     'requested_fields': ['RAW'] if operation == 'remove_RAW_only' else ['s_reg'] if operation == 's_reg_0_to_1_only' else [],
                     'modality': 'DIAGNOSTIC_FORK'}]
    raw_after, clock_after = world.runtime.raw_copy(), world.runtime.clock_copy()
    raw_changes = [i for i, (a, b) in enumerate(zip(raw_before, raw_after)) if a != b]
    clock_changes = [i for i, (a, b) in enumerate(zip(clock_before, clock_after)) if a != b]
    expected_changes = 1 if operation in ('remove_RAW_only', 's_reg_0_to_1_only') else 0
    if len(raw_changes) != expected_changes or clock_changes:
        raise AssertionError('Diagnostic changed undeclared sites or clocks')
    if digest(main) != initial_physics or operational(main) != initial_operative:
        raise AssertionError('MAIN changed during fork')
    # A sham adds a diagnostic ledger item, unlike an intact fork; that is declared.
    if world.runtime.channel_names != main.runtime.channel_names:
        raise AssertionError('Clone lost interfaces')
    if [receipt(world, r.id) for r in main.runtime.receipts] != [receipt(main, r.id) for r in main.runtime.receipts]:
        raise AssertionError('Clone lost receipts or queue status')
    traces, captures, snapshots = [], {b: {} for b in spec['banks']}, []
    for tick in (292, 293, 294, 350, 417, 424, 430, 431, 437):
        world.run_until(tick)
        traces.append({'tick': tick, 'pulse_site': record(world, site), 'residual_site': record(world, residual),
                       'pulse_gate': gate(world, site), 'residual_gate': gate(world, residual),
                       'Moore26_plus_center': local_context(world, site) if tick <= 294 else []})
        for name, bank in spec['banks'].items():
            if tick == bank['resource_read']:
                captures[name]['resource'] = record(world, bank['resource_receiver'])
            if tick == bank['function_read']:
                captures[name]['function'] = record(world, bank['function_receiver'])
        if tick in (292, 293, 294, 437):
            snap = folder / f'T{tick}.deetsnap'
            world.save_snapshot(str(snap))
            snapshots.append({'path': snap.relative_to(ROOT).as_posix(), 'sha256': sha(snap), 'physics': digest(world)})
        put(folder / 'INCREMENTAL.json', {'case': case, 'trace': traces, 'captures': captures})
    profiles = {}
    for name, pair in captures.items():
        bank = spec['banks'][name]
        r, f = pair['resource'], pair['function']
        rval = int(r['active'] and r['s_reg'] == 3 and r['direction'] == list(bank['resource_direction']))
        fval = int(f['active'] and f['s_reg'] == 7 and f['direction'] == list(bank['supply_direction']))
        profiles[name] = {'F': fval, 'R': rval, 'external_utility': 2 * fval + rval}
    unchanged = digest(main) == initial_physics and operational(main) == initial_operative
    if not unchanged:
        raise AssertionError('MAIN changed during diagnostic evolution')
    result = {'schema': 'CPC5.regulation.counterfactual.v1', 'case': case, 'engine': identity(),
              'parent': cfg['parent'], 'parent_sha256': cfg['parent_sha256'],
              'modality': 'DIAGNOSTIC_FORK' if operation != 'intact' else 'INTACT_REPLAY_FORK',
              'source_preparation': {'existing_acquired_pulse': pre, 'restored_complete_operative_parent': initial_operative},
              'initial_physics': initial_physics, 'interventions': declared,
              'verified_RAW_indices_changed': raw_changes, 'verified_clock_indices_changed': clock_changes,
              'trace': traces, 'captures': captures, 'profiles': profiles,
              'external_utility': sum(v['external_utility'] for v in profiles.values()),
              'receipts': [receipt(world, r.id) for r in world.runtime.receipts], 'input_calls': [],
              'checkpoints': snapshots, 'final_state': digest(world),
              'technical': {'parent_MAIN_physical_and_operative_unchanged': unchanged,
                            'RAW_site_change_count': len(raw_changes), 'clock_site_change_count': len(clock_changes),
                            'queue_receipts_interfaces_initially_preserved': True},
              'code_sha256': sha(__file__), 'status': 'MEASURED',
              'elapsed_seconds': time.monotonic() - started,
              'scope': 'Post-acquisition selective intervention at292. MAIN remains unchanged. No claim of reinforcement-selected attention or universal regulatory mechanism.'}
    put(folder / 'MEASUREMENTS.json', result)
    print(json.dumps({'id': case['id'], 'utility': result['external_utility'], 'profiles': profiles}), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case')
    args = parser.parse_args()
    frozen = ROOT / 'configuraciones/regulation_causal.json'
    if not frozen.exists():
        put(frozen, config())
    cfg = json.loads(frozen.read_text(encoding='utf-8'))
    rows = []
    for case in cfg['fork_cases']:
        if args.case and args.case != case['id']:
            continue
        value = run_fork(case, cfg)
        rows.append({'id': case['id'], 'profile': value['profiles'], 'utility': value['external_utility']})
        put(ROOT / 'resultados/regulation_causal/INDEX.json', {'configuration': cfg, 'cases_completed_this_call': rows})
    for case in cfg['reserved_cases']:
        if args.case and args.case != case['id']:
            continue
        out = ROOT / 'resultados/regulation_causal' / case['id']
        if (out / 'MEASUREMENTS.json').exists():
            value = json.loads((out / 'MEASUREMENTS.json').read_text(encoding='utf-8'))
        else:
            value = regulate(case, out)
        rows.append({'id': case['id'], 'profile': value['profiles'], 'utility': value['external_utility']})
        put(ROOT / 'resultados/regulation_causal/INDEX.json', {'configuration': cfg, 'cases_completed_this_call': rows})


if __name__ == '__main__':
    main()
