"""Selective diagnostic forks; full MAIN remains untouched and is never fed back."""
import argparse
import json
from pathlib import Path
import time

from common import ROOT, identity, put, sha, record, receipt, digest, operational, local_context, gate
from integrated import Session


def run(base_name, arm, cfg, out):
    import dee_thinking as d
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    base_path = ROOT / 'resultados/RETENTION_D02_ALTERNATE_ACCESS' / base_name / 'BEFORE_QUERY_T69.deetsnap'
    main = Session.load(base_path)
    before_main = digest(main.world)
    body = main.geometry['body']
    site = main.geometry['retention_interface']['site']
    before_a = record(main.world, body['A'])
    before_b = record(main.world, body['B'])
    edit = d.ResearchStateEdit()
    edit.coordinate = d.Coordinate(*body['A'])
    old = main.world.runtime.observe(edit.coordinate).record
    edit.raw = d.pack_record(old.state, before_b['s_reg'], old.dx, old.dy, old.dz, old.semantic) if arm == 'equalize_A_to_B' else int(before_a['raw'])
    edit.label = 'CPC6_RETENTION_EXPLICIT_DIAGNOSTIC_' + arm
    world = main.world.diagnostic_fork([edit], True)
    s = Session(world, main.geometry, main.requests, 'RETENTION_DIAGNOSTIC_' + base_name + '_' + arm)
    after_a = record(world, body['A'])
    assert after_a['clock'] == before_a['clock']
    assert before_main == digest(main.world)
    assert all(after_a[key] == before_a[key] for key in ('state', 'semantic', 'direction'))
    snap_pre = s.save(out / 'AFTER_INTERVENTION_T69.deetsnap')
    s.stimulate([{'port': 'retention.z_reader', 'payload': cfg['payload'], 'tick': cfg['read_tick'], 'kind': 'probe', 'origin': 'CAUSAL_FORK_COMMON_READER'}])
    query_id = s.requests[-1]['id']
    panel = []
    for tick in cfg['observation_window']:
        s.advance_to(tick)
        obs = s.observe()
        panel.append({'tick': tick, 'reader': record(world, site), 'body': obs['body'], 'reader_context': local_context(world, site), 'center_context': local_context(world, body['center'])})
    assert digest(main.world) == before_main
    snap_post = s.save(out / 'AFTER_QUERY_T73.deetsnap')
    result = {'schema': 'CPC6.retention.causal.v1', 'base': base_name, 'base_snapshot': str(base_path.relative_to(ROOT)), 'base_sha256': sha(base_path), 'arm': arm, 'mode': 'DIAGNOSTIC_FORK', 'engine': identity(), 'configuration_sha256': sha(ROOT / 'configuraciones/RETENTION_C01_CAUSAL.json'), 'source_sha256': sha(__file__), 'intervention': {'site': body['A'], 'before_A': before_a, 'after_A': after_a, 'unchanged_B': before_b, 'clock_unchanged': True, 'fields_changed': ['s_reg'] if arm == 'equalize_A_to_B' else [], 'all_other_sites_and_fields_forked': True}, 'pre_MAIN': before_main, 'post_MAIN': digest(main.world), 'MAIN_unchanged': True, 'query_receipt': receipt(world, query_id), 'post_query_panel': panel, 'requests': s.receipts(), 'snapshot_before': snap_pre, 'snapshot_after': snap_post, 'final_physical': digest(world), 'final_operational': operational(world), 'elapsed_seconds': time.monotonic() - start, 'status': 'MEASURED'}
    put(out / 'MEASUREMENTS.json', result)
    print(json.dumps({'base': base_name, 'arm': arm, 'receipt': result['query_receipt']['status'], 'delta_before': before_a['s_reg'] - before_b['s_reg'], 'delta_after_intervention': after_a['s_reg'] - before_b['s_reg'], 'reader': [(r['tick'], r['reader']['s_reg'], r['reader']['direction']) for r in panel], 'MAIN_unchanged': True}), flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, default=ROOT / 'configuraciones/RETENTION_C01_CAUSAL.json')
    parser.add_argument('--out', type=Path, default=ROOT / 'resultados/RETENTION_C01_CAUSAL')
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text(encoding='utf-8-sig'))
    args.out.mkdir(parents=True, exist_ok=True)
    index = []
    for base in cfg['bases']:
        for arm in cfg['arms']:
            target = args.out / (base + '_' + arm)
            if (target / 'MEASUREMENTS.json').exists():
                result = json.loads((target / 'MEASUREMENTS.json').read_text(encoding='utf-8'))
            else:
                result = run(base, arm, cfg, target)
            index.append({'base': base, 'arm': arm, 'evidence': str((target / 'MEASUREMENTS.json').relative_to(ROOT)), 'receipt': result['query_receipt'], 'MAIN_unchanged': result['MAIN_unchanged'], 'reader': [{'tick': r['tick'], 'physical': r['reader']} for r in result['post_query_panel']]})
            put(args.out / 'INDEX.json', index)
