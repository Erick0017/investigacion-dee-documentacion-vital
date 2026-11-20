"""Finite retention discovery on the current integrated U0, no core edits."""
import argparse
import json
from pathlib import Path
import time

from common import ROOT, identity, put, sha, record, receipt, digest, operational, local_context, gate
from integrated import create
import order_memory
import action_feedback


def decode(item, admitted):
    if not admitted:
        return {'status': 'INPUT_NOT_APPLIED', 'direction_class': None}
    if not item['active']:
        return {'status': 'NO_ACTIVE_RESPONSE_IN_FIXED_WINDOW', 'direction_class': None}
    dr = item['direction']
    if item['semantic'] == 1 and dr[0] in (-1, 1) and dr[1:] == [-1, 0]:
        return {'status': 'DIRECTIONAL_RESPONSE', 'direction_class': dr[0]}
    return {'status': 'OTHER_PHYSICAL_RESPONSE', 'direction_class': None}


def run(case, config, out):
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    engine = identity()
    s = create(adapter=case['adapter'])
    w = s.world
    geometry = s.geometry['body']
    adapter = s.geometry['adapter']
    rows = []
    snapshots = []
    decisive = []
    read_tick = case['read_tick']
    def snap(label):
        value = s.save(out / (label + '.deetsnap'))
        value['path'] = label + '.deetsnap'
        snapshots.append(value)
        put(out / 'SNAPSHOTS.json', snapshots)
    if case['history'] != 'NONE':
        s.stimulate(order_memory.experience(case['history']))
    s.stimulate([{'port': 'order.read', 'payload': 7, 'tick': 2, 'kind': 'probe', 'origin': 'COMMON_FIRST_ORDER_QUERY'}])
    if adapter:
        s.stimulate(action_feedback.source_protocol(adapter, config['source_values']))
        s.stimulate(action_feedback.query_protocol(adapter))
    put(out / 'CONFIG.json', {'case': case, 'frozen_config_sha256': sha(ROOT / 'configuraciones/RETENTION_D01.json'), 'code_sha256': sha(__file__), 'core_code_sha256': {name: sha(ROOT / 'src' / name) for name in ('integrated.py', 'order_memory.py', 'action_feedback.py')}, 'geometry': s.geometry})
    snap('PREPARED_T0')
    for tick in range(read_tick + config['readout_delay'] + 1):
        s.advance_to(tick)
        row = {'tick': tick, 'body': order_memory.observations(w, geometry)}
        if adapter:
            row['adapter'] = action_feedback.capture(w, adapter)
        rows.append(row)
        if tick == 5 and adapter:
            # Actual current consequence selected by the experiment generator;
            # it is never computed from U0's forecast or its error.
            s.stimulate(action_feedback.actual_protocol(adapter, config['actual']))
        if tick in (5, 23, 33):
            snap('T' + str(tick))
        if tick == read_tick:
            before = row['body']
            pre_physical = digest(w)
            pre_gates = {name: gate(w, site) for name, site in (('A', geometry['A']), ('B', geometry['B']), ('center', geometry['center']), ('read_port', geometry['emission_site']))}
            decisive.append({'tick': tick, 'kind': 'BEFORE_OLD_RELATION_QUERY', 'center_context': local_context(w, geometry['center']), 'read_context': local_context(w, geometry['emission_site']), 'write_gates': pre_gates})
            snap('BEFORE_RETAINED_QUERY_T' + str(tick))
            s.stimulate([{'port': 'order.read', 'payload': config['query_payload'], 'tick': tick, 'kind': 'probe', 'origin': 'RETENTION_QUERY_NO_RETEACHING'}])
            query_id = s.requests[-1]['id']
        if read_tick < tick <= read_tick + 3:
            decisive.append({'tick': tick, 'kind': 'AFTER_OLD_RELATION_QUERY', 'center_context': local_context(w, geometry['center']), 'read_context': local_context(w, geometry['emission_site'])})
        if tick in (5, 23, 33, read_tick, read_tick + 3):
            put(out / 'INCREMENTAL.json', {'last_complete_tick': tick, 'rows': rows, 'requests': s.receipts()})
    final = rows[-1]['body']
    actual_receipt = receipt(w, query_id)
    decoded = decode(final['emission'], actual_receipt['status'] == 'applied')
    first = decode(rows[5]['body']['emission'], s.receipts()[0 if case['history'] == 'NONE' else 2]['receipt']['status'] == 'applied')
    snap('AFTER_RETAINED_QUERY_T' + str(w.runtime.current_tick))
    result = {'schema': 'CPC6.retention.case.v1', 'case': case, 'engine': engine, 'geometry': s.geometry, 'readout_contract': config['criterion'], 'rows': rows, 'decisive_neighborhoods': decisive, 'requests': s.receipts(), 'snapshots': snapshots, 'first_direction': first, 'before_old_query': before, 'before_old_query_physical': pre_physical, 'before_old_query_gates': pre_gates, 'retention_receipt': actual_receipt, 'retention_emission': final['emission'], 'retention_decode': decoded, 'delta_before': before['delta'], 'delta_after': final['delta'], 'final_physical': digest(w), 'final_operational': operational(w), 'MAIN_edits_RAW_clocks_after_T0': [], 'original_order_reteaching_after_T1': False, 'source_exposures': len([q for q in s.requests if q['port'].startswith('feedback.source.')]), 'query_consumption_effect_recorded': True, 'continuity': {'prepared_worlds': 1, 'tick_monotonic': True, 'forks': 0, 'restores': 0}, 'scope': 'Three fixed cadence discoveries plus predeclared opposite/no-history controls; this reader is physically renewed, not a promise of arbitrary-time or unlimited memory access.', 'elapsed_seconds': time.monotonic() - started, 'status': 'MEASURED'}
    put(out / 'MEASUREMENTS.json', result)
    print(json.dumps({'id': case['id'], 'tick': w.runtime.current_tick, 'delta_before': result['delta_before'], 'receipt': actual_receipt['status'], 'readout': decoded, 'direction': final['emission']['direction'], 'seconds': result['elapsed_seconds']}), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, default=ROOT / 'configuraciones/RETENTION_D01.json')
    parser.add_argument('--out', type=Path, default=ROOT / 'resultados/RETENTION_D01')
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding='utf-8-sig'))
    args.out.mkdir(parents=True, exist_ok=True)
    index = []
    for case in config['cases']:
        target = args.out / case['id']
        if (target / 'MEASUREMENTS.json').exists():
            result = json.loads((target / 'MEASUREMENTS.json').read_text(encoding='utf-8'))
        else:
            result = run(case, config, target)
        index.append({'case': case, 'evidence': str((target / 'MEASUREMENTS.json').relative_to(ROOT)), 'delta_before': result['delta_before'], 'receipt': result['retention_receipt'], 'readout': result['retention_decode'], 'first_direction': result['first_direction'], 'source_exposures': result['source_exposures']})
        put(args.out / 'INDEX.json', index)


if __name__ == '__main__':
    main()
