"""Prospective N0-only reserve template. Never launches Native or fills a future identity."""
import copy
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
OLD = HERE / 'PROPUESTA_RESERVA60_WAIT_R03_REAL_N0_R02'
OUT = HERE / 'PROPUESTA_RESERVA60_VISTA_PERSISTENTE_POST6_N0_R01'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def emit(p, value):
    with p.open('x', encoding='utf8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


def main():
    if OUT.exists():
        raise FileExistsError('Preserve every proposal revision')
    for member in json.loads((OLD / 'MANIFIESTO.json').read_bytes())['members']:
        if sha(OLD / member['file']) != member['sha256']:
            raise ValueError('Previous proposal changed')
    old = json.loads((OLD / 'PLAN_RESERVA60_WAIT_R03_REAL_DRAFT_R02.json').read_bytes())
    p = copy.deepcopy(old)
    p.update(
        status='DRAFT_NOT_AUTHORIZED_FOR_NATIVE',
        life='APD04_VISTA_PERSISTENTE_REAL_POST10_REAL_R01',
        world_id='APD04_VISTA_PERSISTENTE_REAL_POST10_REAL_R01',
        initial_snapshot_sha256=None,
        initial_tick=None,
        candidate_genealogy=None,
        required_prepared_view_policy='inspeccion_persistente',
        assembly_revision='APD04.reserve60.N0.persistent_REAL.post6.R01',
    )
    p['scope'] = (
        'Prospective continuation of the predesignated persistentREAL view arm only, '
        'after its actual six-op future is complete, cleanly STOPped and sealed FULL. '
        'The current trials are still open when this template is prepared; no future '
        'tick/hash/quality is invented. No automatic execution, fallback, repair, '
        'cache clear, memory merge, old22 panel, alternative-life selection or favorable rewind. '
        'Preserves the exact 64-event/43-work exogenous calendar, fixed R03 quality, '
        'sensor and old environmental work-gain metric. A pending or uncertain original '
        'is not an operational candidate merely because this template exists.'
    )
    p['candidate_scope'] = (
        'Root designated PERSISTENTE_REAL before view outcomes. A usable actual FULL '
        'and explicit Root GO are required. No substitution by circularREAL, OMIT, '
        'SAFE or a favorable past is authorized by this proposal.'
    )
    p['after_window_pending']['request_id'] = 'apd04_persistent_real_reserve_exact_pending_r01'
    # Request IDs belong to the new reserve, not to a replay of any earlier calendar.
    for event in p['events']:
        if 'request_id' in event:
            event['request_id'] = 'persistent_r01_' + event['request_id']
    c = p['coverage_and_criteria']
    c['source_counts'] = (
        '2/5/10/20 are external source counts in NativeN67, append-only. Persistent '
        'view retains only unique formed INSPECT with closed actuator. Forty-three '
        'scheduled opportunities do not imply 23 eligible events, twenty distinct '
        'sources visited, twenty observations simultaneous or twenty learned concepts. '
        'Measure source/cursor before and after every actual returned opportunity.'
    )
    c['negative_transfer'] = (
        'The opportunity at2880 has equal loads after the A lesson. Do not infer '
        'eligibility from a circular cursor forecast. Actual source/tag, a selected USE '
        'and a valid numeric emission are required to say the balance function was used. '
        'At acquired reference21 the fixed balance bias20 may fail; preserve that result.'
    )
    c['initial_environment_mutation'] = (
        'The original literal mutations16/25 remain. If the actual six-op arm contains '
        'environmental values31/14, this is a new exogenous change back to16/25, '
        'with actual versions/caches/bin/cursor preserved. It is not Native re-teaching '
        'or insertion of a reference. No outcome-conditioned retargeting.'
    )
    c['requested_vs_emitted_tool'] = (
        'Record the literal requested word separately from the formed lexical tool '
        'and actual operation. Old_gain can be positive for an effect from another '
        'tool under the frozen implementation; this is not automatically correct '
        'word comprehension. Do not alter feedback or the frozen metric retrospectively.'
    )
    c['reference_prediction_auditor_only'] = (
        'Measure actual initial Mu reference offline, if exact support is available. '
        'If20, A predicts21 and subsequent B20. Never reinterpret A as19, change '
        'criteria to fit responses, restore clocks or insert a favorable reference.'
    )
    p['required_actual_preGO_proofs'] = [
        'The designated persistentREAL six-op future completed all six IDs, or Root explicitly changes the scope in a new revision. This template does not waive completion.',
        'Actual owner STOP and Job0 confirmed; exact current FULL snapshot, queues, interfaces, SQLite requests and environment preserved; actual snapshot/hash/tick/genealogy supplied before sealing.',
        'No pending or uncertain request is skipped; no old22 or standalone new2 panel was run on the candidate original.',
        'Actual viewpolicy inspection_persistente, actioncodecR03 and fixed quality contract verified from current state; sensor independent_balanced and frozen sources unchanged.',
        'Adverse/uncertain or unusable persistentREAL remains preserved. No automatic fallback or rewind. Explicit Root GO still required.',
        'Reserve IDs are new, source/cursor/cache versions remain actual. One final pending43 calibrationID is preserved without counting its execution.',
    ]
    # Only logistics/metadata and fresh transport IDs changed, not exposures/criteria.
    for a, b in zip(p['events'], old['events']):
        aa, bb = dict(a), dict(b)
        aa.pop('request_id', None)
        bb.pop('request_id', None)
        if aa != bb:
            raise ValueError('A literal exposure changed')
    if len(p['events']) != 64 or p['duration_seconds'] != 3600:
        raise ValueError('Unexpected frozen calendar')
    OUT.mkdir()
    emit(OUT / 'PLAN_RESERVA60_PERSISTENTE_REAL_DRAFT_R01.json', p)
    emit(OUT / 'CRITERIOS_Y_ESTADO_N0.json', {
        'status': 'DRAFT_ONLY_NO_NATIVE_GO', 'Native_ticks': 0,
        'future_identity_known': False, 'candidate_original': p['life'],
        'exact_old_exposures_preserved': True,
        'request_IDs_new_prefix_only': True,
        'scheduled_events': 64, 'scheduled_work': 43,
        'eligibility_or_actual_coverage_inferred_from_plan': False,
        'minimum_window_seconds': 3600, 'local_closing_seconds': 4500,
        'hard_seconds': 4800, 'closing_seconds': 300,
        'absolute_deadline_unchanged': p['deadline_utc'],
        'source_proposal_SHA': sha(OLD / 'MANIFIESTO.json'),
        'no_current_life_or_system_source_read_or_edited': True,
    })
    shutil.copy2(Path(__file__), OUT / Path(__file__).name)
    emit(OUT / 'MANIFIESTO.json', {'self_hash_excluded': True, 'members': [
        {'file': q.name, 'bytes': q.stat().st_size, 'sha256': sha(q)}
        for q in sorted(OUT.iterdir()) if q.is_file()
    ]})
    print(json.dumps({'out': str(OUT), 'manifest_SHA': sha(OUT / 'MANIFIESTO.json'), 'Native_ticks': 0}))


if __name__ == '__main__':
    main()
