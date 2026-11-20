"""Alternate physical access after original-port occupancy, same finite U0."""
import argparse
import json
from pathlib import Path
import time

from common import ROOT, identity, put, sha, record, receipt, digest, operational, local_context, gate, interface
from integrated import create
import action_feedback
import order_memory


def run(case, cfg, out):
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    engine = identity()
    s = create(adapter=True)
    w = s.world
    body = s.geometry['body']
    adapter = s.geometry['adapter']
    site = order_memory.add(body['center'], cfg['interface']['relative_site'])
    before_interface = digest(w)
    w.declare_interface(interface(cfg['interface']['name'], site, cfg['interface']['direction']))
    assert digest(w) == before_interface
    s.geometry['retention_interface'] = {'site': list(site), **cfg['interface'], 'declared_at': 0, 'inert_physical_identity_verified': True}
    rows = []
    windows = []
    snapshots = []
    tick_query = case['read_tick']
    def snap(label):
        value = s.save(out / (label + '.deetsnap'))
        value['path'] = label + '.deetsnap'
        snapshots.append(value)
        put(out / 'SNAPSHOTS.json', snapshots)
    if case['history'] != 'NONE':
        s.stimulate(order_memory.experience(case['history']))
    s.stimulate([{'port': 'order.read', 'payload': 7, 'tick': 2, 'kind': 'probe', 'origin': 'COMMON_FIRST_READER'}])
    s.stimulate(action_feedback.source_protocol(adapter, {'P': 1, 'Q': -1}))
    s.stimulate(action_feedback.query_protocol(adapter))
    put(out / 'CONFIG.json', {'case': case, 'configuration_sha256': sha(ROOT / 'configuraciones/RETENTION_D02_ALTERNATE_ACCESS.json'), 'code_sha256': sha(__file__), 'core_code_sha256': {name: sha(ROOT / 'src' / name) for name in ('integrated.py', 'order_memory.py', 'action_feedback.py')}, 'geometry': s.geometry})
    snap('T0')
    query_id = None
    for tick in range(tick_query + 5):
        s.advance_to(tick)
        row = {'tick': tick, 'body': order_memory.observations(w, body), 'reader': record(w, site)}
        if tick in (5, 15, 19, 20, 23, 33):
            row['adapter'] = action_feedback.capture(w, adapter)
        rows.append(row)
        if tick == 5:
            s.stimulate(action_feedback.actual_protocol(adapter, -1))
        if tick == tick_query:
            before_query = {'physical': digest(w), 'body': row['body'], 'reader': row['reader'], 'gates': {name: gate(w, q) for name, q in (('A', body['A']), ('B', body['B']), ('center', body['center']), ('reader', site))}}
            snap('BEFORE_QUERY_T' + str(tick))
            if not case.get('omit_query'):
                s.stimulate([{'port': cfg['interface']['name'], 'payload': case['payload'], 'tick': tick, 'kind': 'probe', 'origin': 'ALTERNATE_PHYSICAL_READER_NO_RETEACHING'}])
                query_id = s.requests[-1]['id']
        if tick_query <= tick <= tick_query + 4:
            windows.append({'tick': tick, 'reader': local_context(w, site), 'center': local_context(w, body['center'])})
        if tick in (5, 23, 33, tick_query, tick_query + 1, tick_query + 4):
            if tick != tick_query:
                snap('T' + str(tick))
            put(out / 'INCREMENTAL.json', {'last_complete_tick': tick, 'rows': rows, 'requests': s.receipts()})
    rr = receipt(w, query_id) if query_id is not None else {'status': 'NOT_REQUESTED_SHAM'}
    panel = [{'tick_after_query': r['tick'] - tick_query, 'reader': r['reader'], 'original_port': r['body']['emission'], 'center': r['body']['center'], 'delta': r['body']['delta']} for r in rows if r['tick'] >= tick_query]
    result = {'schema': 'CPC6.retention.alternate_access.v1', 'case': case, 'engine': engine, 'geometry': s.geometry, 'criterion': cfg['readout'], 'rows': rows, 'local_windows': windows, 'before_query': before_query, 'query_receipt': rr, 'post_query_panel': panel, 'requests': s.receipts(), 'snapshots': snapshots, 'final_physical': digest(w), 'final_operational': operational(w), 'external_RAW_clock_edits_after_T0': [], 'R1_reteaching_after_T1': False, 'world_recreated': False, 'scope': 'Finite alternate reader discovery and predeclared later payload/cadence variations; passive field measurements separated from applied physical probe.', 'elapsed_seconds': time.monotonic() - started, 'status': 'MEASURED'}
    put(out / 'MEASUREMENTS.json', result)
    print(json.dumps({'id': case['id'], 'receipt': rr['status'], 'before_raw': before_query['reader']['raw'], 'delta': before_query['body']['delta'], 'reader_panel': [(p['tick_after_query'], p['reader']['s_reg'], p['reader']['direction'], p['reader']['active']) for p in panel], 'seconds': result['elapsed_seconds']}), flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, default=ROOT / 'configuraciones/RETENTION_D02_ALTERNATE_ACCESS.json')
    parser.add_argument('--out', type=Path, default=ROOT / 'resultados/RETENTION_D02_ALTERNATE_ACCESS')
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text(encoding='utf-8-sig'))
    args.out.mkdir(parents=True, exist_ok=True)
    index = []
    for case in cfg['cases']:
        target = args.out / case['id']
        if (target / 'MEASUREMENTS.json').exists():
            result = json.loads((target / 'MEASUREMENTS.json').read_text(encoding='utf-8'))
        else:
            result = run(case, cfg, target)
        index.append({'case': case, 'evidence': str((target / 'MEASUREMENTS.json').relative_to(ROOT)), 'receipt': result['query_receipt'], 'delta_before': result['before_query']['body']['delta'], 'post_query_panel': result['post_query_panel']})
        put(args.out / 'INDEX.json', index)
