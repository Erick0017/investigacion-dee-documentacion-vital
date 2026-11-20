"""Late native-carrier and learned-relation selective controls in complete forks."""
import json
from pathlib import Path
import time

from common import ROOT, put, sha, identity, record, receipt, digest, operational, local_context, gate
from integrated import Session
import consolidation


def run(parent, mechanism, arm, cfg, out):
    import dee_thinking as d
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    parent_folder = ROOT / 'resultados/D04_OPEN_LANDING' / parent['case_id']
    start_tick = 88 if mechanism == 'late_native_carrier_T88' else 90
    source_path = parent_folder / ('T' + str(start_tick) + '.deetsnap')
    main = Session.load(source_path)
    g = main.geometry['consolidation']
    if mechanism == 'learned_relative_delta_T93':
        main.advance_to(93)
    before_physical = digest(main.world)
    before_operations = operational(main.world)
    if mechanism == 'late_native_carrier_T88':
        site = ((44 + 65 * parent['value_direction']) % 67, 53, 28)
        before = record(main.world, site)
        assert before['active'] and before['semantic'] == 1, before
        replacement = 0 if arm == 'selective_cut' else int(before['raw'])
        edit_description = 'Remove only this already emitted native carrier at88; preserve its clock and every other site.'
    else:
        site = g['A']
        before = record(main.world, site)
        b = record(main.world, g['B'])
        r = main.world.runtime.observe(d.Coordinate(*site)).record
        replacement = d.pack_record(r.state, b['s_reg'], r.dx, r.dy, r.dz, r.semantic) if arm == 'selective_cut' else int(before['raw'])
        edit_description = 'Equalize only A.s_reg toB.s_reg at93, preserving A state/direction/semantic/clock, all other sites and the pending query.'
    edit = d.ResearchStateEdit()
    edit.coordinate = d.Coordinate(*site)
    edit.raw = replacement
    edit.label = 'CPC6_EXPLICIT_CONSOLIDATION_' + mechanism + '_' + arm
    w = main.world.diagnostic_fork([edit], True)
    s = Session(w, main.geometry, main.requests, parent['case_id'] + '_DIAGNOSTIC_' + mechanism + '_' + arm)
    after = record(w, site)
    assert after['clock'] == before['clock']
    assert digest(main.world) == before_physical
    if mechanism == 'learned_relative_delta_T93':
        assert all(before[key] == after[key] for key in ('state', 'direction', 'semantic'))
    snaps = []
    rows = []
    def save(label):
        value = s.save(out / (label + '.deetsnap'))
        value['path'] = label + '.deetsnap'
        snaps.append(value)
        put(out / 'SNAPSHOTS.json', snaps)
    save('AFTER_INTERVENTION_T' + str(s.world.runtime.current_tick))
    start = s.world.runtime.current_tick
    for tick in range(start, cfg['readout_tick'] + 1):
        s.advance_to(tick)
        if tick in cfg['causal_windows']:
            rows.append({'tick': tick, 'body_R1': s.observe()['body'], 'consolidation_R2': consolidation.capture(w, g), 'center_context': local_context(w, g['center']), 'A_context': local_context(w, g['A']), 'B_context': local_context(w, g['B']), 'gate_A': gate(w, g['A']), 'gate_B': gate(w, g['B']), 'intervened_site': record(w, site)})
            if tick in (89, 90, 93, 94, 97):
                save('T' + str(tick))
        if tick in (90, 94, 97):
            put(out / 'INCREMENTAL.json', {'last_complete_tick': tick, 'rows': rows, 'requests': s.receipts()})
    assert digest(main.world) == before_physical
    assert operational(main.world) == before_operations
    pending_queries = [q for q in s.receipts() if q['port'] == 'consolidated.order.read']
    assert len(pending_queries) == 1 and pending_queries[0]['tick'] == 94, pending_queries
    parent_result = json.loads((parent_folder / 'MEASUREMENTS.json').read_text(encoding='utf-8'))
    baseline = next(row for row in parent_result['rows'] if row['tick'] == 97)['consolidation']
    final = rows[-1]['consolidation_R2']
    result = {'schema': 'CPC6.consolidation.causal_control.v1', 'parent_case': parent['case_id'], 'parent_snapshot': str(source_path.relative_to(ROOT)), 'parent_snapshot_sha256': sha(source_path), 'parent_measurements_sha256': sha(parent_folder / 'MEASUREMENTS.json'), 'mechanism': mechanism, 'arm': arm, 'modality': 'DIAGNOSTIC_FORK', 'engine': identity(), 'source_sha256': sha(__file__), 'config_sha256': sha(ROOT / 'configuraciones/CONSOLIDATION_CONTROLS_01.json'), 'intervention': {'site': list(site), 'before': before, 'after': after, 'description': edit_description, 'clock_preserved': True}, 'rows': rows, 'requests': s.receipts(), 'query_already_queued_in_parent': pending_queries, 'response97': final, 'unmodified_parent_response97': baseline, 'response97_identical_to_parent': final == baseline, 'MAIN_physical_before': before_physical, 'MAIN_physical_after': digest(main.world), 'MAIN_operational_unchanged': True, 'snapshots': snaps, 'final_physical': digest(w), 'final_operational': operational(w), 'postfork_added_inputs': [], 'scope': 'Selective causal interventions after original emission/acquisition; no omitted-fromT0 replacement and no results returned to MAIN.', 'elapsed_seconds': time.monotonic() - started, 'status': 'MEASURED'}
    put(out / 'MEASUREMENTS.json', result)
    print(json.dumps({'parent': parent['case_id'], 'mechanism': mechanism, 'arm': arm, 'delta97': final['delta'], 'response97': final['emission'], 'query_receipt': pending_queries[0]['receipt'], 'identical_parent97': result['response97_identical_to_parent'], 'MAIN_unchanged': True}), flush=True)
    return result


if __name__ == '__main__':
    cfg = json.loads((ROOT / 'configuraciones/CONSOLIDATION_CONTROLS_01.json').read_text(encoding='utf-8-sig'))
    root = ROOT / 'resultados/CONSOLIDATION_CONTROLS_01'
    root.mkdir(parents=True, exist_ok=True)
    index = []
    for parent in cfg['parents']:
        for mechanism in cfg['mechanisms']:
            for arm in cfg['arms']:
                identifier = parent['case_id'] + '_' + mechanism + '_' + arm
                out = root / identifier
                if (out / 'MEASUREMENTS.json').exists():
                    value = json.loads((out / 'MEASUREMENTS.json').read_text(encoding='utf-8'))
                else:
                    value = run(parent, mechanism, arm, cfg, out)
                index.append({'id': identifier, 'parent': parent['case_id'], 'mechanism': mechanism, 'arm': arm, 'evidence': str((out / 'MEASUREMENTS.json').relative_to(ROOT)), 'delta97': value['response97']['delta'], 'emission97': value['response97']['emission'], 'receipt': value['query_already_queued_in_parent'][0]['receipt'], 'MAIN_unchanged': value['MAIN_operational_unchanged']})
                put(root / 'INDEX.json', index)
