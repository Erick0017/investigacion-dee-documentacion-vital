"""Final bounded Root-selected early P0 view reserve, N0 preparation only."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = HERE / 'PROPUESTA_RESERVA60_VISTA_PERSISTENTE_POST6_N0_R01'
OUT = HERE / 'PROPUESTA_RESERVA60_PERSISTENCIA_TEMPRANA_N0_R01'
DRIVER = HERE / 'EJECUTOR_TRES_VISTAS_REAL_POST10_N0_R02/ejecutar_plan_apd04_r04.py'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_bytes())
def emit(p, value):
    with p.open('x', encoding='utf8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


def main():
    if OUT.exists(): raise FileExistsError('Preserve earlier bytes and adverse futures')
    for m in read(BASE / 'MANIFIESTO.json')['members']:
        if sha(BASE / m['file']) != m['sha256']: raise ValueError('Earlier template changed')
    old = read(BASE / 'PLAN_RESERVA60_PERSISTENTE_REAL_DRAFT_R01.json')
    p = copy.deepcopy(old)
    life = 'APD04_PERSISTENCIA_TEMPRANA_RESERVA_R01'
    p.update(life=life, world_id=life, initial_snapshot_sha256=None, initial_tick=None,
        status='DRAFT_NOT_AUTHORIZED_FOR_NATIVE', candidate_genealogy=None,
        assembly_revision='APD04.reserve60.early_P0_persistent_SAFE639374.N0.R01')
    p['required_actual_parent'] = {
        'life': 'APD04_MAIN', 'tick': 639374,
        'snapshot_sha256': '771e041363b39ef830603cb32ed2bbe7fc5938e4783a9dfe2a733a6e3ee4f9a8',
        'pair_manifest_sha256': '5d938d56497571fb4af8ac814eac0cde59214814afb7f3d9280543ea074ca6db',
        'pair_directory': 'sistema/estado/fuentes_emparejadas/APD04_MAIN_T639374_EXPLORACION_R01',
        'not_the_favorable_future_of_OMIT_or_view_arms': True,
    }
    for index, event in enumerate(p['events']):
        if 'request_id' in event:
            event['request_id'] = 'apd04_early_persistent_r01_event_' + str(index).zfill(3)
    initial = p['events'][0]
    initial['at_seconds'] = 2
    initial['situations'] = [{'modo': 'apd04-cambio', 'etiqueta_objetivo': 0,
        'palabra': 'clasifica', 'cargas': [7, 3], 'criterio': 20,
        'mutaciones': [{'fuente': 0, 'valor': 31}, {'fuente': 1, 'valor': 14}]}]
    p['events'] = [
        {'at_seconds': 0, 'kind': 'command', 'request_id': 'apd04_early_persistent_r01_P0_actuator_R03',
         'argv': ['configurar-actuador-ecosistema', 'R03', '--retorno', 'omit']},
        {'at_seconds': 1, 'kind': 'command', 'request_id': 'apd04_early_persistent_r01_P0_view',
         'argv': ['configurar-vista-ecosistema', 'inspeccion_persistente', '--retorno', 'omit']},
    ] + p['events']
    p['after_window_pending']['request_id'] = 'apd04_early_persistent_reserve_exact_pending_r01'
    p['scope'] = (
        'Last bounded Root-designated alternative: a new FULL fork of actual SAFE_MAIN639374, '
        'not a repaired continuation or a favorable future selected from the late view arms. '
        'The persistent view and R03 actuator are prepared before the first opportunity by '
        'generic enums. This engineering timing is P0, not learned autonomy. Preserves '
        'actual inherited Native matter/history/cache/bin/cursor; initial literal external '
        'change31/14, goal0, clasifica, loads7/3, criterion20 was fixed before this Native '
        'evaluation. It does not import words or targets into Native memory. Remaining '
        '43-work reserve agenda, old_gain and newquality are unchanged. Actual import '
        'identity/hash/tick and explicit Root GO must precede execution.'
    )
    p['candidate_scope'] = (
        'Prospectively selected early preparation from SAFE, identity separate from '
        'persistentREALpost10 and its adverse/uncertain future. No claim of a causal '
        'head-to-head of early/late exposure, because their prior histories differ. '
        'Never replace the protected active E1 or merge histories.'
    )
    p['required_prepared_view_policy'] = 'inspeccion_persistente'
    p['P0_configuration_in_agenda_not_yet_in_imported_state'] = True
    c = p['coverage_and_criteria']
    c['initial_environment_mutation'] = (
        'Only the literal initial environmental values31/14, goal0, clasifica, loads7/3, '
        'criterion20 differ prospectively from the earlier64-event calendar. First event '
        'is now at2sec, following fixed P0 actuator/view commands0/1. No cache/bin/cursor '
        'reset, no NativeRAW/clock writes, no target-dependent source selection.'
    )
    c['early_vs_late'] = (
        'A new branch from FULLSAFE639374 installs the identical P0 view before the '
        'first R03 exposure. Late arms descend from REALpost10 and remain preserved; '
        'different accumulated histories prevent attributing every difference solely '
        'to viewport timing. The test measures one actual continuing trajectory.'
    )
    p['required_actual_preGO_proofs'] = [
        'Imported child derives from exact declared SAFE639374 FULL, not post10 or OMIT, with RAW/clocks/interfaces/pending/receipts and transport proved from the actual import.',
        'Actual child identity/hash/tick/genealogy are filled and no owner has advanced it before reserve; active protected E1 remains unchanged.',
        'Two generic P0 commands precede first opportunity; no old22 standalone material panel on this candidate before reserve.',
        'R03 sensor independent_balanced, actuatorR03, fixed quality, persistent view enum and exact source hashes are frozen; no response-based switching.',
        'All scheduled43 work IDs and final queuedID are new to this life. Actual eligible count/source coverage/NULL/rejection and lateness are measured, not inferred.',
        'Explicit Root GO, available owner slot (global max2), min3600/local4500/hard4800/closing300 and original absolute deadline are enforced.',
    ]
    p['proposed_existing_LAB_R04_driver'] = {'source': str(DRIVER), 'sha256': sha(DRIVER),
        'scope': 'Exact already-used R04 driver copied in sealed view executor; no new Native manager.'}
    # No later exposure altered, only first environment and two initial generic P0 commands.
    for a, b in zip(p['events'][3:], old['events'][1:]):
        aa, bb = dict(a), dict(b)
        aa.pop('request_id', None); bb.pop('request_id', None)
        if aa != bb: raise ValueError('A later literal exposure changed')
    if len(p['events']) != 66: raise ValueError('Unexpected agenda length')
    spec = importlib.util.spec_from_file_location('R04_static_validator_N0_only', DRIVER)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    test = copy.deepcopy(p)
    test.update(status='CLOSED_FOR_EXECUTION', initial_tick=639374, initial_snapshot_sha256='0' * 64)
    module.validate_plan(test)
    OUT.mkdir()
    emit(OUT / 'PLAN_RESERVA60_PERSISTENCIA_TEMPRANA_DRAFT_R01.json', p)
    emit(OUT / 'CRITERIOS_Y_VALIDACION_N0.json', {
        'status': 'DRAFT_NO_NATIVE_GO', 'Native_ticks': 0, 'owners_started': 0,
        'candidate': life, 'actual_child_import_not_yet_known': True,
        'generic_P0_commands_added': 2, 'initial_env_change_fixed_prospectively': True,
        'all_later63_events_identical_except_new_request_IDs': True,
        'scheduled_work': 43, 'source_counts': [2, 5, 10, 20],
        'actual_eligible_or_distinct_sources_inferred': False,
        'fixed_quality_contract': p['required_posteffect_quality_contract'],
        'old_work_gain_unchanged': True, 'NULL_is_not_WAIT': True,
        'original_deadline': p['deadline_utc'], 'min3600_local4500_hard4800_close300': True,
        'previous_template_manifest_SHA': sha(BASE / 'MANIFIESTO.json'),
        'driver_static_validation_passed': True, 'S_or_life_edit': False,
    })
    shutil.copy2(Path(__file__), OUT / Path(__file__).name)
    emit(OUT / 'MANIFIESTO.json', {'self_hash_excluded': True, 'members': [
        {'file': q.name, 'bytes': q.stat().st_size, 'sha256': sha(q)}
        for q in sorted(OUT.iterdir()) if q.is_file()]})
    print(json.dumps({'out': str(OUT), 'manifest_SHA': sha(OUT / 'MANIFIESTO.json'),
        'plan_SHA': sha(OUT / 'PLAN_RESERVA60_PERSISTENCIA_TEMPRANA_DRAFT_R01.json'), 'Native_ticks': 0}))


if __name__ == '__main__': main()
