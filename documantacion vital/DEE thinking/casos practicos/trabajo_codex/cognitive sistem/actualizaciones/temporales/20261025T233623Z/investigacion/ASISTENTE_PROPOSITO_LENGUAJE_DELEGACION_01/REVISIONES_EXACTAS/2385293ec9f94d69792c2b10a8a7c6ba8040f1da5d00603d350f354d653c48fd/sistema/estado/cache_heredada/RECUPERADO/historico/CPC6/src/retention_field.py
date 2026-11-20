"""Finite diagnostic localization of distributed reader context, not MAIN repair."""
import json
from pathlib import Path
import time
from common import ROOT, put, sha, identity, record, receipt, digest, operational, local_context
from integrated import Session


def run(base, arm, cfg, out):
    import dee_thinking as d
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    path = ROOT / 'resultados/RETENTION_D02_ALTERNATE_ACCESS' / base / 'BEFORE_QUERY_T69.deetsnap'
    main = Session.load(path)
    body = main.geometry['body']
    center = body['center']
    n = main.world.runtime.dimension
    site = main.geometry['retention_interface']['site']
    physical_before = digest(main.world)
    targets = []
    edits = []
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            for dz in range(-2, 3):
                q = [(center[0] + dx) % n, (center[1] + dy) % n, (center[2] + dz) % n]
                r = record(main.world, q)
                if q in (body['A'], body['B']) or not r['active'] or r['semantic'] != 1:
                    continue
                edit = d.ResearchStateEdit()
                edit.coordinate = d.Coordinate(*q)
                edit.raw = 0 if arm == 'local_semantic1_field_cut' else int(r['raw'])
                edit.label = 'EXPLICIT_LOCAL_READER_DIAGNOSTIC_' + arm
                targets.append({'before': r, 'new_raw': str(edit.raw)})
                edits.append(edit)
    fork = main.world.diagnostic_fork(edits, True)
    s = Session(fork, main.geometry, main.requests, 'RETENTION_FIELD_DIAGNOSTIC_' + base + '_' + arm)
    for item in targets:
        item['after'] = record(fork, item['before']['site'])
        assert item['after']['clock'] == item['before']['clock']
        assert item['after']['raw'] == item['new_raw']
    assert record(fork, body['A']) == record(main.world, body['A'])
    assert record(fork, body['B']) == record(main.world, body['B'])
    pre = s.save(out / 'INTERVENED_T69.deetsnap')
    s.stimulate([{'port': 'retention.z_reader', 'payload': cfg['query_payload'], 'tick': cfg['query_tick'], 'kind': 'probe', 'origin': 'POST_LOCAL_FIELD_DIAGNOSTIC_COMMON_READER'}])
    query = s.requests[-1]['id']
    panel = []
    for tick in range(cfg['query_tick'], cfg['horizon'] + 1):
        s.advance_to(tick)
        panel.append({'tick': tick, 'reader': record(fork, site), 'body': s.observe()['body'], 'local_context': local_context(fork, site)})
    assert digest(main.world) == physical_before
    post = s.save(out / 'AFTER_QUERY_T73.deetsnap')
    result = {'schema': 'CPC6.retention.field_localization.v1', 'base': base, 'base_snapshot': str(path.relative_to(ROOT)), 'base_sha256': sha(path), 'arm': arm, 'engine': identity(), 'source_sha256': sha(__file__), 'configuration_sha256': sha(ROOT / 'configuraciones/RETENTION_C02_FIELD.json'), 'intervention_region': cfg['intervention_region'], 'interventions': targets, 'query_receipt': receipt(fork, query), 'panel': panel, 'MAIN_before': physical_before, 'MAIN_after': digest(main.world), 'MAIN_unchanged': True, 'snapshots': [pre, post], 'final_physical': digest(fork), 'final_operational': operational(fork), 'scope': 'Diagnostic deletion of local semantic1 expression field with A/B charges/supports untouched. This is not a spontaneous recovery or a MAIN regulation mechanism.', 'elapsed_seconds': time.monotonic() - started, 'status': 'MEASURED'}
    put(out / 'MEASUREMENTS.json', result)
    print(json.dumps({'base': base, 'arm': arm, 'edited_sites': len(targets), 'receipt': result['query_receipt']['status'], 'delta_after_cut': panel[0]['body']['delta'], 'reader': [(r['tick'], r['reader']['s_reg'], r['reader']['direction'], r['reader']['active']) for r in panel]}), flush=True)
    return result


if __name__ == '__main__':
    cfg = json.loads((ROOT / 'configuraciones/RETENTION_C02_FIELD.json').read_text(encoding='utf-8-sig'))
    directory = ROOT / 'resultados/RETENTION_C02_FIELD'
    directory.mkdir(parents=True, exist_ok=True)
    index = []
    for base in cfg['bases']:
        for arm in cfg['arms']:
            out = directory / (base + '_' + arm)
            if (out / 'MEASUREMENTS.json').exists():
                result = json.loads((out / 'MEASUREMENTS.json').read_text(encoding='utf-8'))
            else:
                result = run(base, arm, cfg, out)
            index.append({'base': base, 'arm': arm, 'evidence': str((out / 'MEASUREMENTS.json').relative_to(ROOT)), 'edited_sites': len(result['interventions']), 'receipt': result['query_receipt'], 'reader': [{'tick': r['tick'], 'physical': r['reader']} for r in result['panel']]})
            put(directory / 'INDEX.json', index)
