"""Four finite causal forks of late word-bus access; no hidden readout policy."""
import json
import time
from common import ROOT, put, sha, identity, record, digest, operational, local_context, gate
from integrated import Session
import order_memory


def run(case, cfg, out):
    import dee_thinking as d
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    parent_dir = ROOT / 'resultados/B01_WORD_BUS' / case['parent']
    snapshot = parent_dir / 'T160.deetsnap'
    main = Session.load(snapshot)
    right = main.geometry['consolidation']
    left = right['left']
    targets = main.geometry['word_bus']['parts']
    physical_before = digest(main.world)
    operative_before = operational(main.world)
    if case['mechanism'] == 'late_bus_carrier':
        site = cfg['bus_cut_site']
        before = record(main.world, site)
        assert before['active'] and before['semantic'] == 1 and before['direction'] == [0, 0, 1] and before['s_reg'] == 7, before
        raw = 0 if case['arm'] == 'selective_cut' else int(before['raw'])
    else:
        site = right['A']
        before = record(main.world, site)
        other = record(main.world, right['B'])
        r = main.world.runtime.observe(d.Coordinate(*site)).record
        raw = d.pack_record(r.state, other['s_reg'], r.dx, r.dy, r.dz, r.semantic) if case['arm'] == 'selective_cut' else int(before['raw'])
    edit = d.ResearchStateEdit()
    edit.coordinate = d.Coordinate(*site)
    edit.raw = raw
    edit.label = 'EXPLICIT_WORD_BUS_DIAGNOSTIC_' + case['id']
    fork = main.world.diagnostic_fork([edit], True)
    s = Session(fork, main.geometry, main.requests, 'WORD_BUS_DIAGNOSTIC_' + case['id'])
    after = record(fork, site)
    assert after['clock'] == before['clock']
    if case['mechanism'] == 'R2_relative_memory':
        assert all(after[key] == before[key] for key in ('state', 'semantic', 'direction'))
    rows = []
    snapshots = []
    def save(label):
        value = s.save(out / (label + '.deetsnap'))
        value['path'] = label + '.deetsnap'
        snapshots.append(value)
        put(out / 'SNAPSHOTS.json', snapshots)
    save('AFTER_INTERVENTION_T160')
    for tick in cfg['windows']:
        s.advance_to(tick)
        rows.append({'tick': tick, 'bus_approach': record(fork, cfg['bus_cut_site']), 'targets': {name: record(fork, item['target']) for name, item in targets.items()}, 'right_R2': order_memory.observations(fork, right), 'left_R2': order_memory.observations(fork, left), 'R1': s.observe()['body'], 'target_contexts': {name: local_context(fork, item['target']) for name, item in targets.items()}, 'right_center_context': local_context(fork, right['center']), 'gates': {'A': gate(fork, right['A']), 'B': gate(fork, right['B'])}})
        if tick in (161, 162, 163):
            save('T' + str(tick))
        put(out / 'INCREMENTAL.json', {'last_complete_tick': tick, 'rows': rows})
    assert digest(main.world) == physical_before
    assert operational(main.world) == operative_before
    original = json.loads((parent_dir / 'MEASUREMENTS.json').read_text(encoding='utf-8'))
    original162 = next(row for row in original['rows'] if row['tick'] == 162)
    current162 = next(row for row in rows if row['tick'] == 162)
    compare = {name: {'current': value, 'parent': original162['word_bus'][name]['target'], 'equal': value == original162['word_bus'][name]['target']} for name, value in current162['targets'].items()}
    result = {'schema': 'CPC6.word_bus.causal_control.v1', 'case': case, 'engine': identity(), 'parent_snapshot': str(snapshot.relative_to(ROOT)), 'parent_sha256': sha(snapshot), 'parent_measurements_sha256': sha(parent_dir / 'MEASUREMENTS.json'), 'source_sha256': sha(__file__), 'config_sha256': sha(ROOT / 'configuraciones/WORD_BUS_CONTROLS_01.json'), 'intervention': {'site': list(site), 'before': before, 'after': after, 'clock_preserved': True, 'mechanism': case['mechanism'], 'RAW_after': str(raw)}, 'rows': rows, 'comparison162': compare, 'new_participant_inputs_after_fork': [], 'all_parent_requests': s.receipts(), 'snapshots': snapshots, 'MAIN_physical_before': physical_before, 'MAIN_physical_after': digest(main.world), 'MAIN_operational_unchanged': True, 'parent_snapshot_unchanged_sha256': sha(snapshot), 'final_physical': digest(fork), 'final_operational': operational(fork), 'scope': 'Fresh late neutral reader supply versus retained relative memory; the observer records exact physical outputs and never applies discovery polarity decoder to decide success.', 'elapsed_seconds': time.monotonic() - started, 'status': 'MEASURED'}
    put(out / 'MEASUREMENTS.json', result)
    print(json.dumps({'id': case['id'], 'parent': case['parent'], 'delta160': rows[0]['right_R2']['delta'], 'delta162': current162['right_R2']['delta'], 'right_target162': current162['targets']['right'], 'right_equal_parent': compare['right']['equal'], 'MAIN_unchanged': True}), flush=True)
    return result


if __name__ == '__main__':
    cfg = json.loads((ROOT / 'configuraciones/WORD_BUS_CONTROLS_01.json').read_text(encoding='utf-8-sig'))
    root = ROOT / 'resultados/WORD_BUS_CONTROLS_01'
    root.mkdir(parents=True, exist_ok=True)
    index = []
    for case in cfg['cases']:
        out = root / case['id']
        if (out / 'MEASUREMENTS.json').exists():
            result = json.loads((out / 'MEASUREMENTS.json').read_text(encoding='utf-8'))
        else:
            result = run(case, cfg, out)
        row162 = next(row for row in result['rows'] if row['tick'] == 162)
        index.append({'case': case, 'evidence': str((out / 'MEASUREMENTS.json').relative_to(ROOT)), 'right_target162': row162['targets']['right'], 'right_delta162': row162['right_R2']['delta'], 'right_equal_parent': result['comparison162']['right']['equal'], 'MAIN_operational_unchanged': result['MAIN_operational_unchanged']})
        put(root / 'INDEX.json', index)
