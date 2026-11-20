"""N0 prospective three-action contract and two DRAFT AUX schedules.

SAFE parent supersedes the unexecuted pre60 proposal. No shared S edit, Native
import/run, fork creation, plan closure or response-conditioned host decision.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PATCH = 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/native_candidates/PROPUESTA_ACTUADOR_R03_R02'
PARENT = 'sistema/estado/fuentes_emparejadas/APD04_MAIN_T639374_EXPLORACION_R01'
PARENT_SHA = '771e041363b39ef830603cb32ed2bbe7fc5938e4783a9dfe2a733a6e3ee4f9a8'
PAIR_SHA = '5d938d56497571fb4af8ac814eac0cde59214814afb7f3d9280543ea074ca6db'
QUALITY = 'APD04.posteffect_quality.relevant_gain_or_irrelevant_formed_wait.R03.v1'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name, p):
    s = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def dump(p, v):
    with p.open('x', encoding='utf8', newline='\n') as f: json.dump(v, f, ensure_ascii=False, indent=2); f.write('\n')


def make_plan(arm):
    life = 'APD04_WAIT_R03_' + arm + '_AUX_R02'
    prefix = 'apd04_wait_' + arm.lower() + '_r02_'
    def event(t, label, row, feedback='omit'):
        return {'at_seconds': t, 'kind': 'material', 'request_id': prefix + label,
                'situations': [row], 'feedback': feedback, 'actuator': 'closed'}
    events = [{'at_seconds': 0, 'kind': 'command', 'request_id': prefix + 'prepared_actuator_R03',
               'argv': ['configurar-actuador-ecosistema', 'R03', '--retorno', 'omit']},
              event(1, 'first_context_goal1_and_values', {'modo': 'apd04-cambio', 'etiqueta_objetivo': 1,
                    'palabra': 'clasifica', 'cargas': [7, 3], 'criterio': 20,
                    'mutaciones': [{'fuente': 0, 'valor': 16}, {'fuente': 1, 'valor': 25}]}),
              event(80, 'common_goal0_before_opportunity2', {'modo': 'apd04-cambio', 'etiqueta_objetivo': 0}),
              event(375, 'goal1_before_opportunity6', {'modo': 'apd04-cambio', 'etiqueta_objetivo': 1})]
    for i in range(10):
        events.append(event(15 + 75 * i, 'opportunity_' + str(i + 1).zfill(2),
                {'modo': 'apd04-vivir', 'oportunidades': 1, 'sensor': 'independent_balanced',
                 'lexico': True, 'desacoplado': False}, 'real' if arm == 'REAL' else 'omit'))
    events += [{'at_seconds': 780, 'kind': 'command', 'request_id': prefix + 'retention_old16_MA6',
                'argv': ['panel', '--nuevas', '--memorias', '--retorno', 'omit']},
               event(990, 'retention_clasifica', {'modo': 'apd04-palabra', 'texto': 'clasifica'}),
               event(1020, 'retention_equilibra', {'modo': 'apd04-palabra', 'texto': 'equilibra'}),
               {'at_seconds': 1070, 'kind': 'checkpoint', 'tag': 'actual_wait_AUX_end_no_reset'}]
    events.sort(key=lambda e: e['at_seconds'])
    return {'schema': 'APD04.literal_supervisor_schedule.v1', 'status': 'DRAFT_NOT_AUTHORIZED_FOR_NATIVE',
            'life': life, 'world_id': life, 'initial_snapshot_sha256': None, 'initial_tick': None,
            'proposed_identity_not_yet_imported': True, 'required_parent_complete_pair': PARENT,
            'required_parent_snapshot_sha256': PARENT_SHA, 'required_parent_tick': 639374,
            'required_P0_action_codec': 'R03', 'required_posteffect_quality_contract': QUALITY,
            'deadline_utc': '2026-10-27T03:30:51+00:00', 'duration_seconds': 1100,
            'closing_reserve_seconds': 180, 'material_wait_seconds': 30, 'result_limit_seconds': 1200,
            'poll_heartbeat_seconds': 5, 'heartbeat_seconds': 30, 'stop_control_wait_seconds': 120,
            'stop_process_wait_seconds': 120, 'supervision_wall_limit_seconds': 2400,
            'outer_guard_requires_existing_supervision_wrapper': True,
            'freeze_source_paths': ['sistema/app/protocolo_apd04.py', 'sistema/app/usar_dee.py', 'sistema/app/cola_local.py',
                'sistema/app/servicio_persistente.py', 'sistema/capacidades/ecosistema_apd04.py',
                'sistema/capacidades/sensor_balanceado_apd04.py', 'sistema/capacidades/sensor_balanceado_apd03_r02.py',
                'sistema/capacidades/ruta_adaptativa_apd02_04.py', 'sistema/capacidades/selector_acrecion_nativo.py',
                'sistema/capacidades/sensor_componentes_apd04.py', 'sistema/capacidades/acciones_nativas_apd04.py',
                'sistema/capacidades/lexico_compartido_apd04.py', 'sistema/capacidades/mente_unificada_01.py',
                'sistema/capacidades/mente_acumulativa_r02.py', 'sistema/capacidades/lexico_generico_apd03_r02.py',
                'sistema/capacidades/percepcion_cruda_fi01.py'],
            'events': events,
            'scope': 'Two dependent SAFE-history FULL forks, one preset three-action affordance. First exposure goal1/tag0 is not a forced failure; a genuine WAIT may be correct. A fixed goal0 change precedes common opportunity2. Only work feedback differs REAL/OMIT. Native output, not the evaluator, selects INSPECT/WAIT/USE.',
            'timing_is_a_new_N0_proposal_for_Root_not_an_existing_native_result': True}


def main():
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument('--out', type=Path, required=True); a = ap.parse_args()
    if a.out.exists(): raise FileExistsError('Keep all earlier preparations')
    if sha(ROOT / PARENT / 'EXPORTACION_SERVICIO.json') != PAIR_SHA: raise ValueError('SAFE pair differs')
    parser = load('read_SAFE_metadata_no_Native', ROOT / 'sistema/capacidades/observador_causal_retrospectivo_01.py')
    snapshot = parser.Snapshot(ROOT / PARENT / 'VIDA.deetsnap.gz', verify_checksum=False)
    if snapshot.encoded_sha256 != PARENT_SHA or snapshot.tick != 639374: raise ValueError('Wrong complete SAFE parent')
    env_text = snapshot.metadata['DEE.Cognitive.System.1.1.APD04.ecosystem.R01']; env = json.loads(env_text)
    if snapshot.pending or env['in_progress'] is not None or len(env['objects']) != 2 or env['cursor'] != 0:
        raise ValueError('Pending/shape mismatch; do not recreate a favorable parent')
    protocol = load('proposed_R03_literals_only', ROOT / PATCH / 'sistema/app/protocolo_apd04.py')
    ui = load('proposed_R03_UI_parser_only', ROOT / PATCH / 'sistema/app/usar_dee.py')
    driver = load('existing_driver_schema_only', ROOT / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/ejecucion/ejecutar_plan_apd04_r03.py')
    plans = [make_plan(arm) for arm in ('REAL', 'OMIT')]; checks = []
    for p in plans:
        test = copy.deepcopy(p); test.update(status='CLOSED_FOR_EXECUTION', initial_snapshot_sha256='0' * 64, initial_tick=639374)
        driver.validate_plan(test)
        for e in p['events']:
            if e['kind'] == 'material':
                for r in e['situations']: protocol.validate_literal(r)
            elif e['kind'] == 'command': ui.literal_rows(ui.command_parser().parse_args(e['argv']))
        checks.append({'life_not_created': p['life'], 'events': len(p['events']), 'work_opportunities': 10,
                       'static_literals_pass_proposed_R03_contract_not_installed': True, 'Native_ticks': 0})
    x, y = copy.deepcopy(plans[0]), copy.deepcopy(plans[1])
    for p in (x, y):
        p['life'] = p['world_id'] = 'SAME_ID_FOR_N0_COMPARISON_ONLY'
        for e in p['events']:
            if 'request_id' in e: e['request_id'] = e['request_id'].replace('real', 'ARM').replace('omit', 'ARM')
            if e['kind'] == 'material' and e['situations'][0]['modo'] == 'apd04-vivir': e['feedback'] = 'SAME_FOR_N0_COMPARISON_ONLY'
    if x != y: raise ValueError('The two plans differ beyond identity and declared work feedback')
    a.out.mkdir()
    for arm, p in zip(('REAL', 'OMIT'), plans): dump(a.out / ('PLAN_WAIT_R03_' + arm + '_DRAFT_R02.json'), p)
    contract = {'schema': 'APD04.WAIT_affordance_and_posteffect_contract.N0.R02',
        'status': 'PROPOSAL_NOT_INSTALLED_NO_NATIVE_GO', 'Native_ticks': 0,
        'quality_contract': QUALITY,
        'prepared_fixed_action_codec': {'-1': 'INSPECT', '0': 'WAIT', '1': 'USE'},
        'WAIT_formation': 'Exactly one coherent sign0 emission at the unchanged historical three-gate Native reader. Recalculate from uint64 RAW state low32, semantic high4, signed direction nibbles48/52/56 and fixed gate coordinates. NULL/ambiguous/out-of-reader matter is not WAIT.',
        'domain': {'sensor': 'R03 independent_balanced', 'Native_N': 67, 'actuator': 'closed',
                   'out_of_domain': 'Explicit unavailable/no defined quality, no silent neutral action or success. Do not generalize to nulled actuators.'},
        'old_work_gain_preserved': 'The existing new useful INSPECT/classification/balance gain is unchanged for INSPECT/USE; WAIT always contributes0. counters.useful remains this old metric.',
        'new_quality': {'WAIT': 'formed_unique_sign0 AND tag!=goal AND all task environmental objects/loads are unchanged by this action',
                        'INSPECT_USE': 'Exactly old_work_gain, not relaxed maintenance/correctness',
                        'NULL_ambiguous': False,
                        'task_signature': 'All objects (including order,id,tag,value,version,observed cache,bin) plus loads. Only cursor/episode/counters/protocol diaries excluded, since those always advance by prepared opportunity scheduling.'},
        'posteffect_feedback': 'REAL maps new_quality to existing SUCCESS/FAILURE only AFTER actual emission/effect. Existing SUCCESS introduces no new positive port; it omits the FAILURE contact. OMIT advances the same declared consequence window but supplies no outcome contact. Neither carries the desired action/content.',
        'accounting': ['old_work_gain, new_quality, valid formed action, WAIT correctness, stale-cache/current-version correctness, retention and admissions remain separate.',
                       'Old reserve43 retains its frozen23tag-eligible/20ineligible analysis and all original outcomes; this new affordance cannot retrospectively improve it.',
                       'The new10-op curriculum has5relevant and5irrelevant slots under the prepared circular cursor. Potential WAIT usefulness is not a prediction that Native forms0.',
                       'The relevant already-complete task still may have no NEW gain; R03 changes only the absence of a legitimate ignore action, not all limitations of the old reward.'],
        'parent': {'pair': PARENT, 'pair_manifest_sha256': PAIR_SHA, 'snapshot_sha256': PARENT_SHA,
                   'tick': 639374, 'N': 67, 'environment_metadata_original_exact_string': env_text,
                   'cache_warning': 'Actual SAFE object0 observedNone; object1 observed27/version0/bin+. Do not insert pre60 caches18/24 or erase cache1. Mutations16/25 are declared current-world changes; they do not teach a cache.'},
        'curriculum': {'op1': 'goal1/tag0 atsource0; useful outcome is observed, not forced',
                       'op2': 'same fixed common opportunity in both arms: goal0/tag1 atsource1, after the declared goal change',
                       'op3_5': 'goal0; same body/history continues', 'op6_10': 'goal1; same body/history continues',
                       'retention': 'Same post10 old16+MA6 material panel and subsequent clasifica/equilibra queries in each arm, no re-teaching.'},
        'controls_and_scope': ['REAL versus OMIT, same full past and exogenous schedule; not independent learners.',
                              'Compare actual inputs, phases, initial equivalence and later choices; different consequent environment states after different Native actions are legitimate interactive divergence, not hidden copying.',
                              'A correct WAIT or changed selection remains a local exploratory result. Useful/contextual or P2 claims require causal consequence contrast plus a new held-out opportunity, not these design/test examples alone.',
                              'No guarantee of WAIT, adaptation, retention or viability; preserve invalid/rejected/pending/late/incomplete operations.',
                              'No current MAIN, protected E1, R02 reserve, software or snapshots are edited here.'],
        'patch_reference': {'folder': PATCH, 'manifest_sha256': sha(ROOT / PATCH / 'MANIFIESTO_PROPUESTA_N0.json'),
                            'quality_tests': '12pure software cases and17legacyCLI checks in PRUEBAS_P0_N0.json, not Native trials',
                            'test_file_sha256': sha(ROOT / PATCH / 'PRUEBAS_P0_N0.json')},
        'plan_validation': checks, 'plans_equal_except_identity_and_work_feedback': True,
        'timing_proposal_not_yet_approved_by_Root': {'duration_seconds': 1100, 'outer_guard_seconds': 2400,
                       'reason': 'Allows10opportunities, old22panel and2newword retention. Not inherited from a prior900s schedule. Root must approve prospective duration or issue another revision before any closure; actual completion/admission is not guaranteed.'}}
    dump(a.out / 'CONTRATO_Y_CRITERIOS_WAIT_R03_R02.json', contract)
    dump(a.out / 'ANTECEDENTE_PRE60_NO_EJECUTADO.json', {'status': 'SUPERSEDED_PRETEST_INSTRUCTION_ONLY_NO_PLAN_FILE_WAS_CREATED',
         'old_parent_tick': 656420, 'old_parent_snapshot_sha256': '3d058c7424dba43a47b653579e1226681ae82ed8a21b203f6acc8f91af5eab0e',
         'old_curriculum_requested': '5goal0→5goal1', 'old_cache_real_parent': '18/version1 and24/version1; no such values are copied into the newSAFE branch',
         'reason_for_change': 'Root changed the candidate prospectively after dense growth in the ongoing R02 reserve, before any R03 Native GO.',
         'Native_ticks': 0, 'not_a_rewritten_experiment': True})
    shutil.copy2(Path(__file__), a.out / Path(__file__).name)
    dump(a.out / 'MANIFIESTO.json', {'members': [{'file': p.name, 'sha256': sha(p), 'bytes': p.stat().st_size}
                                             for p in sorted(a.out.iterdir()) if p.is_file()], 'self_hash_excluded': True})
    if any(k.startswith('dee_thinking') for k in sys.modules): raise RuntimeError('N0 imported Native')
    print(json.dumps({'out': str(a.out), 'two_DRAFTs': True, 'parent_tick': 639374,
                      'same_except_identity_and_work_feedback': True, 'Native_ticks': 0, 'patch_installed': False}))


if __name__ == '__main__': main()
