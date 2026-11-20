"""Prepare ONLY four DRAFT AUX schedules from one actual complete prefix.

No Native import, owner, fork creation, source edit or action selection. Root
must separately approve actual imports, identities/source freeze and execution.
"""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PARENT = 'sistema/estado/fuentes_emparejadas/APD04_MAIN_T639374_EXPLORACION_R01'
PARENT_SHA = '771e041363b39ef830603cb32ed2bbe7fc5938e4783a9dfe2a733a6e3ee4f9a8'
ENV_KEY = 'DEE.Cognitive.System.1.1.APD04.ecosystem.R01'
SOURCES = ['sistema/app/protocolo_apd04.py', 'sistema/app/usar_dee.py', 'sistema/app/cola_local.py',
           'sistema/app/servicio_persistente.py', 'sistema/capacidades/ecosistema_apd04.py',
           'sistema/capacidades/sensor_balanceado_apd04.py', 'sistema/capacidades/sensor_balanceado_apd03_r02.py',
           'sistema/capacidades/sensor_componentes_apd04.py', 'sistema/capacidades/ruta_adaptativa_apd02_04.py',
           'sistema/capacidades/selector_acrecion_nativo.py', 'sistema/capacidades/acciones_nativas_apd04.py',
           'sistema/capacidades/lexico_compartido_apd04.py', 'sistema/capacidades/mente_unificada_01.py',
           'sistema/capacidades/mente_acumulativa_r02.py', 'sistema/capacidades/lexico_generico_apd03_r02.py',
           'sistema/capacidades/percepcion_cruda_fi01.py',
           'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/ejecucion/ejecutar_plan_apd04_r03.py']


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2); stream.write('\n')
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module


def plan(n):
    life = 'APD04_IGUAL_OPORTUNIDAD_N' + str(n) + '_AUX_R01'
    prefix = 'apd04_igual_op_n' + str(n) + '_r01_'
    def material(t, label, row, feedback='omit'):
        return {'at_seconds': t, 'kind': 'material', 'request_id': prefix + label,
                'situations': [row], 'feedback': feedback, 'actuator': 'closed'}
    events = [{'at_seconds': 0, 'kind': 'command', 'request_id': prefix + 'prepared_codec_R02',
               'argv': ['configurar-actuador-ecosistema', 'R02', '--retorno', 'omit']},
              material(1, 'environment_goal0_classify', {'modo': 'apd04-cambio', 'etiqueta_objetivo': 0,
                   'palabra': 'clasifica', 'cargas': [7, 3], 'criterio': 20,
                   'mutaciones': [{'fuente': 0, 'valor': 18}, {'fuente': 1, 'valor': 24}]}),
              material(2, 'append_only' if n > 2 else 'existing_N2_state_check',
                       {'modo': 'apd04-ampliar', 'fuentes': n, 'semilla': 40520} if n > 2 else {'modo': 'apd04-estado'})]
    for i, t in enumerate((15, 90, 165, 240, 315)):
        events.append(material(t, 'opportunity_' + str(i + 1), {'modo': 'apd04-vivir', 'oportunidades': 1,
                        'sensor': 'independent_balanced', 'lexico': True, 'desacoplado': False}, 'real'))
    for i, word in enumerate(('suma', 'resta', 'compara', 'recuerda')):
        events.append(material(400 + 20 * i, 'old4_' + word, {'modo': 'apd04-palabra', 'texto': word}))
    events.append({'at_seconds': 500, 'kind': 'checkpoint', 'tag': 'actual_AUX_end_after_five_opportunities_and_old4'})
    return {'schema': 'APD04.literal_supervisor_schedule.v1', 'status': 'DRAFT_NOT_AUTHORIZED_FOR_NATIVE',
            'life': life, 'world_id': life, 'initial_snapshot_sha256': None, 'initial_tick': None,
            'parent_required_full_pair': PARENT + '/EXPORTACION_SERVICIO.json', 'parent_snapshot_sha256': PARENT_SHA,
            'parent_tick': 639374, 'proposed_branch_identity_not_yet_created': True,
            'deadline_utc': '2026-10-27T03:30:51+00:00', 'duration_seconds': 600, 'closing_reserve_seconds': 180,
            'material_wait_seconds': 30, 'result_limit_seconds': 1200, 'poll_heartbeat_seconds': 5,
            'heartbeat_seconds': 30, 'stop_control_wait_seconds': 120, 'stop_process_wait_seconds': 120,
            'supervision_wall_limit_seconds': 1800, 'outer_guard_requires_existing_supervision_wrapper': True,
            'freeze_source_paths': SOURCES[:-1], 'events': events,
            'scope': 'Exploratory dependent FULL forks of one same lived prefix, same Native N67. Fixed R03 sensor and prepared R02 actuator codec, five opportunities each. External object append only, no cache/cursor/world reset, no Native content/clock edits, no per-answer route/profile/action policy.'}


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists(): raise FileExistsError('Preserve earlier proposal bytes')
    observer_path = ROOT / 'sistema/capacidades/observador_causal_retrospectivo_01.py'
    obs = load('read_complete_prefix_metadata_only_no_native', observer_path)
    snap = obs.Snapshot(ROOT / PARENT / 'VIDA.deetsnap.gz', verify_checksum=False)
    if snap.encoded_sha256 != PARENT_SHA or snap.tick != 639374 or snap.N != 67:
        raise ValueError('Original complete prefix differs; do not substitute another')
    env = json.loads(snap.metadata[ENV_KEY])
    if len(env['objects']) != 2 or env['cursor'] != 0 or env['in_progress'] is not None or snap.pending:
        raise ValueError('Append-only matched proposal requires the actual closed two-source prefix')
    protocol = load('N0_protocol_literal_validation', ROOT / 'sistema/app/protocolo_apd04.py')
    ui = load('N0_UI_parser_not_started', ROOT / 'sistema/app/usar_dee.py')
    driver = load('N0_existing_driver_schema_only', ROOT / SOURCES[-1])
    args.out.mkdir(); sources = args.out / 'FUENTES_P0_EN_N0'; sources.mkdir(); captured = []
    for i, name in enumerate(SOURCES + ['sistema/capacidades/observador_causal_retrospectivo_01.py']):
        path = ROOT / name; b = path.read_bytes(); ast.parse(b.decode('utf8'), filename=name)
        copy_path = sources / (str(i).zfill(2) + '_' + path.name)
        with copy_path.open('xb') as stream: stream.write(b)
        if path.read_bytes() != b: raise ValueError('Source changed during N0 proposal capture')
        captured.append({'source': name, 'copy': copy_path.relative_to(args.out).as_posix(),
                         'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)})
    proofs = []
    for n in (2, 5, 10, 20):
        candidate = plan(n); test = copy.deepcopy(candidate)
        test.update(status='CLOSED_FOR_EXECUTION', initial_snapshot_sha256='0' * 64, initial_tick=639374)
        driver.validate_plan(test)
        rows = [r for e in candidate['events'] if e['kind'] == 'material' for r in e['situations']]
        for row in rows: protocol.validate_literal(row)
        commands = [ui.literal_rows(ui.command_parser().parse_args(e['argv'])) for e in candidate['events'] if e['kind'] == 'command']
        dump(args.out / ('PLAN_N' + str(n) + '_DRAFT.json'), candidate)
        proofs.append({'sources': n, 'events': len(candidate['events']), 'opportunities': 5,
                       'material_rows_static_validated': len(rows), 'commands_static_parsed': len(commands),
                       'status_remains_DRAFT': candidate['status'], 'not_world_admission_or_outcome_proof': True})
    proposal = {'schema': 'APD04.matched_prefix.equal_opportunity_N0_proposal.R01',
                'status': 'PROPOSAL_ONLY_ROOT_GO_PENDING_NO_NATIVE', 'new_Native_ticks': 0, 'new_lives': 0,
                'parent': {'full_pair_manifest': PARENT + '/EXPORTACION_SERVICIO.json',
                           'manifest_sha256': sha(ROOT / PARENT / 'EXPORTACION_SERVICIO.json'),
                           'snapshot_sha256': PARENT_SHA, 'N': 67, 'tick': 639374,
                           'metadata_original_exact_string': snap.metadata[ENV_KEY], 'native_pending': snap.pending,
                           'identity_check_scope': 'Encoded SHA and metadata/shape checked. Existing Native checksum not recalculated in this metadata-only N0 read; full operational import is still mandatory before any future evaluation.'},
                'prepared_after_fork': {'fixed_codec': 'R02: formed -1/0 INSPECT, formed +1 USE; NULL remains unformed',
                                       'fixed_sensor': 'independent_balanced, family R03, no R04 ports/anatomy installed',
                                       'goal': 0, 'word': 'clasifica', 'loads': [7, 3], 'criterion_auditor_only': 20,
                                       'mutations': [{'source': 0, 'value': 18}, {'source': 1, 'value': 24}],
                                       'seed_for_append_only_additional_objects': 40520,
                                       'do_not_call_apd04_iniciar_or_reset_cache_cursor_bins_or_N': True},
                'dose_and_timing': {'exogenous_work_opportunities_per_branch': 5, 'four_branches_total_opportunities': 20,
                                    'common_nominal_work_offsets_seconds': [15, 90, 165, 240, 315],
                                    'preparation_offsets_seconds': [0, 1, 2], 'old4_after_only_offsets': [400, 420, 440, 460],
                                    'old4_words': ['suma', 'resta', 'compara', 'recuerda'],
                                    'duration_seconds': 600, 'outer_guard_seconds_proposal': 1800,
                                    'same_opportunities_not_guaranteed_same_total_material_inputs': 'The same R03 sensor precommits the same types of sensory/generic inputs per opportunity; actual admissions/rejections, lexical/comparison tool traffic and feedback depend on Native actions. Report each category/dose and actual query phases/lateness; never silently rebalance by extra inputs.',
                                    'N2_no_append': 'Contract rejects expansion to existing size2. The same preparation slot contains apd04-estado, a non-material inspection of environmental metadata, not a claimed physical sham. Check actual preparation tick/phase equality before interpreting differences.'},
                'coverage_limits': ['All four branches descend from one trained prefix and are not four independently trained learners.',
                                    'N2 presents sources0,1,0,1,0; N5/N10/N20 present0,1,2,3,4. All first-five tag/goal bit pairs coincide; revisits/cache availability differ as part of this finite-budget sequential task.',
                                    'Only five slots of N20 are encountered, not20simultaneous observations or20examined/learned sources.',
                                    'Prefix object1 keeps observed27/version0/bin+ after its current value changes24/version1: stale environmental cache is not erased or treated as Native memory.',
                                    'Fixed pipeline and tool/actuator mappings are P0; this contrast alone cannot demonstrate a learned plan, general attention, P2, a capacity ceiling or transfer between lives.',
                                    'Native NULL is not HOLD or an inferred neutral answer. Retention old4 is a material postpanel that can change each branch.',
                                    'Measured equality of opportunity count is not equality of completed/admitted processing or walltime. Preserve rejections and incomplete operations.'],
                'frozen_metrics': ['requested/submitted/admitted/rejected/pending IDs by sensory/generic/lexical/numeric/feedback role',
                                   'selector sign from fixed raw gates and formed/unformed state, literal prepared codec and action',
                                   'useful INSPECT versus correct/classification USE, refreshed/stale cache versions and distinct source coverage',
                                   'word formed command, numerical physical direction, bins/loads actual effects and posteffect feedback',
                                   'old4 first responses, snapshots/ticks/RAW/clocks/occupancy, query phase, actual timing/lateness',
                                   'real process-group CPU/RAM/storage, never infer energy or intelligence from these resources'],
                'host_and_DEE': {'host': 'Import full branches, prepare fixed codec/sensor/calendar/environment literals, circular source view, cache and immutable decoding/evaluation; no target-selected actions, per-case route changes or response retries.',
                                 'DEE': 'Evolution of inherited and later physical state, selector emissions, lexical/numerical emissions and physical consequences of feedback. Any history-conditioned decision requires its own causal evidence.',
                                 'auditor_only': 'Seed, current private numerical values before INSPECT, source/cache versions, expected classes and metrics are not supplied to the Native selector.'},
                'proofs': proofs, 'sources_captured_at_N0_not_a_future_execution_freeze': captured,
                'before_any_Root_GO': ['Create each full fork through the existing import mechanism without advancing the parent.',
                                      'Record actual fork genealogy/encoded snapshot and operative pending state; do not use the parent encoded hash as the child encoded hash.',
                                      'Root approves exact plans/current source bytes and any real phase mismatch; keep original source/candidate failures.',
                                      'Use existing single-owner driver and process supervisor; one writer per Runtime; Root controls concurrent resource limits.',
                                      'No command here launches Native, promotes a life, edits contracts or writes the protected active state.']}
    dump(args.out / 'PROPUESTA_BREVE_Y_CRITERIOS.json', proposal)
    shutil.copy2(Path(__file__), args.out / Path(__file__).name)
    dump(args.out / 'MANIFIESTO.json', {'members': [{'file': p.relative_to(args.out).as_posix(), 'sha256': sha(p), 'bytes': p.stat().st_size}
                                                for p in sorted(args.out.rglob('*')) if p.is_file()], 'self_hash_excluded': True})
    if any(k.startswith('dee_thinking') for k in sys.modules): raise RuntimeError('N0 preparation imported Native')
    print(json.dumps({'out': str(args.out), 'branches_planned_not_created': 4, 'opportunities_planned': 20,
                      'Native_ticks': 0, 'sources_captured': len(captured), 'status': proposal['status']}, ensure_ascii=False))


if __name__ == '__main__': main()
