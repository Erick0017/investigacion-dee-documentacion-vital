"""Final bounded native access attempt after R2 acquisition; no physical edits."""
import argparse
import json
from pathlib import Path
import time

from common import ROOT, identity, put, sha, record, receipt, digest, operational, local_context, gate, interface
from integrated import Session
import order_memory


def parent_path(name):
    return ROOT / 'resultados/D06_BILATERAL' / name / 'T110.deetsnap'


def survey(cfg, out):
    out.mkdir(parents=True, exist_ok=False)
    parents = []
    for name in cfg['parents']:
        path = parent_path(name)
        s = Session.load(path)
        body = s.geometry['body']
        g = s.geometry['consolidation']
        before = digest(s.world)
        observations = []
        for candidate in cfg['candidate_priority']:
            site = order_memory.add(body['center'], candidate['offset'])
            observations.append({'candidate': candidate, 'site': list(site), 'observation': record(s.world, site), 'neighborhood': local_context(s.world, site), 'gate': gate(s.world, site)})
        assert digest(s.world) == before
        parents.append({'parent_case': name, 'parent_snapshot': str(path.relative_to(ROOT)), 'parent_sha256': sha(path), 'physical_before': before, 'physical_after': digest(s.world), 'R1': order_memory.observations(s.world, body), 'R2_right': order_memory.observations(s.world, g), 'R2_left': order_memory.observations(s.world, g['left']), 'candidates': observations})
    chosen = None
    for index, candidate in enumerate(cfg['candidate_priority']):
        if all(p['candidates'][index]['observation']['raw'] == '0' for p in parents):
            chosen = candidate
            break
    result = {'schema': 'CPC6.late_access.survey.v1', 'engine': identity(), 'config_sha256': sha(ROOT / 'configuraciones/LATE_ACCESS_01.json'), 'code_sha256': sha(__file__), 'selection_rule': cfg['selection_rule_auditor'], 'parents': parents, 'selected': chosen, 'native_probe_outcomes_used_for_selection': False, 'additional_world_evolution': False, 'status': 'PASSIVE_SURVEY_COMPLETE' if chosen else 'NO_COMMON_EMPTY_CANDIDATE_IN_PANEL'}
    put(out / 'SURVEY.json', result)
    print(json.dumps({'selected': chosen, 'empty': {p['parent_case']: [(r['candidate']['id'], r['observation']['raw'] == '0') for r in p['candidates']] for p in parents}}), flush=True)
    return result


def run(parent, arm, cfg, selected, out):
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    path = parent_path(parent)
    s = Session.load(path)
    body = s.geometry['body']
    g = s.geometry['consolidation']
    site = order_memory.add(body['center'], selected['offset'])
    physical_before = digest(s.world)
    prefix_operations = operational(s.world)
    name = 'late.original_access.' + selected['id']
    s.world.declare_interface(interface(name, site, selected['direction']))
    assert digest(s.world) == physical_before
    s.geometry['late_access'] = {'declared_at': 110, 'site': list(site), 'direction': selected['direction'], 'name': name, 'source': 'AUDITOR_FIXED_GEOMETRIC_ACCESS_METADATA_NOT_MATTER'}
    snapshots = []
    rows = []
    query_id = None
    query_tick = 110 if arm == 'probe110' else 111 if arm == 'probe111' else None
    def snap(label):
        value = s.save(out / (label + '.deetsnap'))
        value['path'] = label + '.deetsnap'
        snapshots.append(value)
        put(out / 'SNAPSHOTS.json', snapshots)
    snap('BEFORE_PROBE_T110')
    if query_tick is not None:
        s.stimulate([{'port': name, 'payload': cfg['probe_payload'], 'tick': query_tick, 'kind': 'probe', 'origin': 'COMMON_LATE_R1_PHYSICAL_PROBE_AFTER_R2_ACQUISITION'}])
        query_id = s.requests[-1]['id']
    for tick in range(110, cfg['horizon'] + 1):
        s.advance_to(tick)
        rows.append({'tick': tick, 'new_reader': record(s.world, site), 'reader_neighborhood': local_context(s.world, site), 'body_R1': order_memory.observations(s.world, body), 'R2_right': order_memory.observations(s.world, g), 'R2_left': order_memory.observations(s.world, g['left'])})
        if tick in (112, cfg['horizon']):
            snap('T' + str(tick))
        put(out / 'INCREMENTAL.json', {'last_complete_tick': tick, 'rows': rows, 'query_id': query_id, 'requests': s.receipts()})
    parent_loaded_after = Session.load(path)
    assert digest(parent_loaded_after.world) == physical_before
    result = {'schema': 'CPC6.late_access.continuation.v1', 'parent': parent, 'parent_snapshot': str(path.relative_to(ROOT)), 'parent_sha256': sha(path), 'arm': arm, 'mode': 'CONTROLLED_CONTINUATION_NOT_NEW_PREPARATION', 'engine': identity(), 'source_sha256': sha(__file__), 'config_sha256': sha(ROOT / 'configuraciones/LATE_ACCESS_01.json'), 'selected_access': selected, 'geometry': s.geometry, 'declaration_tick': 110, 'declaration_physical_identity_verified': True, 'query_tick': query_tick, 'query_receipt': receipt(s.world, query_id) if query_id is not None else {'status': 'NOT_REQUESTED_SHAM'}, 'rows': rows, 'requests': s.receipts(), 'snapshots': snapshots, 'parent_operational_before': prefix_operations, 'physical_before': physical_before, 'final_physical': digest(s.world), 'final_operational': operational(s.world), 'original_parent_snapshot_unchanged': True, 'external_RAW_clock_writes': [], 'R1_reteaching': False, 'prepared_worlds': 0, 'continued_boundaries': 1, 'elapsed_seconds': time.monotonic() - started, 'status': 'MEASURED'}
    put(out / 'MEASUREMENTS.json', result)
    print(json.dumps({'parent': parent, 'arm': arm, 'receipt': result['query_receipt']['status'], 'reader': [(r['tick'], r['new_reader']['s_reg'], r['new_reader']['direction'], r['new_reader']['active']) for r in rows]}), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--survey-only', action='store_true')
    args = parser.parse_args()
    cfg = json.loads((ROOT / 'configuraciones/LATE_ACCESS_01.json').read_text(encoding='utf-8-sig'))
    out = ROOT / 'resultados/LATE_ACCESS_01'
    if (out / 'SURVEY.json').exists():
        passive = json.loads((out / 'SURVEY.json').read_text(encoding='utf-8'))
    else:
        passive = survey(cfg, out)
    if args.survey_only or passive['selected'] is None:
        return
    index = []
    for parent in cfg['parents']:
        for arm in cfg['arms']:
            target = out / (parent + '_' + arm)
            if (target / 'MEASUREMENTS.json').exists():
                result = json.loads((target / 'MEASUREMENTS.json').read_text(encoding='utf-8'))
            else:
                result = run(parent, arm, cfg, passive['selected'], target)
            index.append({'parent': parent, 'arm': arm, 'evidence': str((target / 'MEASUREMENTS.json').relative_to(ROOT)), 'receipt': result['query_receipt'], 'reader': [r['new_reader'] for r in result['rows']]})
            put(out / 'INDEX.json', index)


if __name__ == '__main__':
    main()
