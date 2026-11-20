"""Root-reviewed documentary closure; default is read-only, never Native.

Only four existing JSON targets may change. Main selectors, states, code,
PROYECTO and Word documents are protected, not writable by this helper.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, copy, hashlib, json, os

P = Path(__file__).resolve().parents[1]
C = P.parents[2] / 'DEE Cognitive 2.0'
RP = C / 'reproducibilidad'
MAIN = 'ECI02_PI03_REPRO_PI04_PI05_MAIN_01'
MAIN_SHA = 'af74c8f47e43ed3b2395a338a23a6cbd42f105ec2cff4daac15b7a4d45e90832'
STAGE = P / 'control/CIERRE_DOCUMENTAL_NO_ADOPCION_PI07_R01'
APPLIED = P / 'control/CIERRE_DOCUMENTAL_NO_ADOPCION_PI07_R01.json'
DECISION = P / 'control/DECISION_NO_ADOPCION_PI07.json'
TARGETS = {
    'campaign': P / 'REGISTRO_CAMPANA.json',
    'continuity': C / 'CONTINUIDAD_DEE_COGNITIVE_2_0.json',
    'catalogue': C / 'sistema/capacidades/CATALOGO_CAPACIDADES.json',
    'transversal': P.parent / 'REVISION_TRANSVERSAL.json',
}
IDS = ['PI07_OBSERVACION_Y_REPRODUCCION_R02_01',
       'PI07_REGULACION_CONTEXTUAL_EXPERIMENTAL_R03_01']


def require(ok, message):
    if not ok:
        raise ValueError(message)


def safe(path):
    path = Path(path).absolute()
    for item in (path, *path.parents):
        if item.exists() and (item.is_symlink() or getattr(item.lstat(), 'st_file_attributes', 0) & 1024):
            raise ValueError('Linked paths are not accepted: ' + str(item))
    return path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    safe(path)
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')


def write_new(path, value):
    with Path(path).open('xb') as stream:
        stream.write(encoded(value))


def at(value, path):
    require(isinstance(path, list) and 1 <= len(path) <= 12, 'Explicit bounded JSON field path required')
    for key in path:
        value = value[key]
    return value


def checked_ref(record):
    path = safe(record['file']).resolve(strict=True)
    require(path.is_relative_to(P.resolve()) or path.is_relative_to(RP.resolve()),
            'Evidence must be a preserved PI07 or RP file')
    require(sha(path) == record['sha256'], 'Evidence SHA changed: ' + str(path))
    return path, read(path)


def owner_scope_checked(closure):
    path, proof = checked_ref(closure['owner_proof'])
    handles = proof['scoped_process_handles']
    require(len(handles) == 2 and {v['pid'] for v in handles} == {19224, 19956}
            and all(v['determined'] is True and v['present'] is False for v in handles),
            'The two scoped process handles are not both determined absent')
    require(closure.get('owner_scope') == 'TWO_SCOPED_HANDLES_ABSENT_NATIVE_CHILD_NOT_IDENTIFIED'
            and closure.get('no_more_Native_actions') is True,
            'Preserve the unverified child/process scope; never claim global owner absence')
    require((datetime.now(timezone.utc).timestamp() - path.stat().st_mtime) < 1800,
            'Scoped process witness is older than30minutes')
    return path, proof


def protected():
    active_path = C / 'sistema/estado/ACTIVO.json'
    card_path = C / 'sistema/estado/vidas' / MAIN / 'VIDA.json'
    active, card = read(active_path), read(card_path)
    require(active['life_id'] == MAIN and card['physical']['N'] == 67
            and card['physical']['tick'] == 824911 and card['snapshot_sha256'] == MAIN_SHA,
            'The actual principal advanced or differs; no stale closure may replace it')
    snapshot = C / 'sistema' / card['snapshot']
    require(sha(snapshot) == MAIN_SHA, 'Protected snapshot bytes differ')
    paths = [active_path, card_path, snapshot, C / 'PROYECTO.json']
    paths.extend(Path(name) for name in read(TARGETS['campaign'])['protected_before']
                 if Path(name) != TARGETS['continuity'])
    result = {}
    for path in dict.fromkeys(paths):
        safe(path)
        result[str(path)] = sha(path)
    return result


def build(close_path):
    close_path = safe(close_path).resolve(strict=True)
    require(close_path.is_relative_to(P.resolve()), 'One actual PI07 closure witness required')
    closure = read(close_path)
    require(closure.get('science_closed') is True,
            'Science must actually be closed, including its preserved blocked future')
    ledger_path, ledger = checked_ref(closure['native_ledger'])
    ticks = at(ledger, closure['native_ledger']['ticks_path'])
    worlds = at(ledger, closure['native_ledger']['worlds_path'])
    require(type(ticks) is int and 0 < ticks <= 100000 and type(worlds) is int and worlds <= 14,
            'Actual total Native ticks/world count invalid')
    require(ticks == closure['Native_ticks_all_branches'] and worlds == closure['diagnostic_worlds'],
            'Closure numbers must match their exact ledger fields')
    owner_path, owner = owner_scope_checked(closure)
    before_protected = protected()
    failure_path = P / 'control/CIERRE_CONJUNTO_MATERIAL_PI07_R01.json'
    failure = read(failure_path)
    require(failure['criteria_met'] is False and failure['status'] == 'FAILED_PRESERVED'
            and failure['new_Native_ticks'] == 0 and failure['final_tick'] == 866067,
            'The actual failed integration witness differs')
    comparison = P / 'control/COMPARACION_R03_REAL_NOFAIL_YOKE_Y_CORTES_PI07_R02.json'
    require(read(comparison)['all_comparability_checks_passed'], 'Closed matched comparisons required')
    c2c = P / 'control/C2C_CONSERVACION_VERIFICADA_PI07_R03.json'
    require(read(c2c)['material_success'] is True, 'Actual corrected three-group C2C check missing')
    panel = P / 'control/PI07_PANEL_ACCESO_R02.json'
    panel_data = read(panel)
    require(panel_data['closed'] and panel_data['criteria_met']
            and panel_data['correct'] == panel_data['tested'] == 12, 'Actual new panel12 missing')
    rp2_path, rp2 = checked_ref(closure['RP_R02_Native_replay'])
    require(rp2['Native_dose1464_all_applied'] is True
            and all(v['all_complete_Native_fields_equal'] is True for v in rp2['cuts'].values())
            and rp2['bounded_comparison_criteria_met'] is False,
            'Actual Native replay and its negative persistent-state criterion must both be preserved')
    recipe2 = RP / 'recetas/pi07_r02_8_ep04.json'
    require(recipe2.is_file(), 'The actual stable R02 recipe is absent')
    rp3 = closure.get('RP_R03_preservation')
    rp3_path = None
    if rp3 is not None:
        rp3_path, rp3_data = checked_ref(rp3)
        require(rp3_data.get('schema') == 'DEE.PI07.R03.experimental_RP_registration.v1'
                and rp3_data.get('status') == 'REGISTERED_USABLE_EXPERIMENTAL_RECIPE_NO_MAIN_ADOPTION'
                and rp3_data.get('Native_executed_by_registration') is False
                and rp3_data.get('new_frontdoor_CLI_material_replay_executed') is False,
                'Require the actual R03 registration, preserving its unexecuted CLI replay limit')
        registered_recipe = Path(rp3_data['recipe']['path']).resolve(strict=True)
        require(registered_recipe.is_relative_to(RP.resolve())
                and sha(registered_recipe) == rp3_data['recipe']['sha256'], 'Registered R03 recipe differs')
    now = datetime.now(timezone.utc).isoformat()
    principal = {'life_id': MAIN, 'N': 67, 'T': 824911, 'snapshot_sha256': MAIN_SHA}
    record = {
        'schema': 'DEE.PI07.scientific_no_adoption.closure.v1', 'recorded_utc': now,
        'Native_ticks_all_branches': ticks, 'diagnostic_worlds': worlds,
        'principal_Native_ticks': 0, 'selected_principal': principal,
        'experimental_life_id': 'ECI02_PI03_REPRO_PI04_PI05_PI07_CAND_01',
        'last_closed_functional_cut': {'N': 67, 'T': 866067,
            'scope': 'Closed C2C28/29 before the0tick failed supply; not a claim of coherent reopening after the partial transaction.'},
        'adopted': False, 'adoption_status': 'BLOCKED_TECHNICAL_FINAL_ENVIRONMENT_AND_CHECKPOINT',
        'report': str(P / 'INFORME_CIENTIFICO_PI07.md'),
        'science': {'R02': '28opportunities,22FI correct,19/19messages; no useful acquired pulse protection.',
            'R03_matched12': 'Complete11/12 real,10/12 constant nonfailure,6/12 yoked; FI12/12 each; messages7/8,6/8,2/8.',
            'R03_scope': 'Initial protection transfers the history acquired in R02 through a prepared perpendicular tool. A real message cost at8 modifies later selection at10. No self-initiated sequence, discovered anatomy or general agency.',
            'retention': 'Restore1/2; after reopening2/2 with an actual useful pulse at14. Later general access newpanel12/12 and inherited C2C2/2 remain separate cuts.',
            'legacy_negative': 'Original API panel stopped5/6 at a wrong material FI14/3 result,176/176 admitted; it remains a real historical failure.',
            'integration_negative': '34-resource protocol violates the unchanged body maximum32. The final attempt advances0Native ticks, cannot checkpoint coherently, and leaves an uncertain external future. No work30 or R03episode16 occurred.'},
        'evidence': [{'file': str(path), 'sha256': sha(path)}
                     for path in (close_path, ledger_path, owner_path, failure_path, comparison, c2c, panel, rp2_path)],
        'RP_R02_scope': 'Original Native replay of8 opportunities is verified physically atEP04/EP08 with1464/1464inputs. The strict whole-persistent-state comparison failed due to queue.0 atEP04; that criterion is not widened.',
        'RP_R03_scope': 'Preserved recipe and source, not a newly executed Native CLI replay.' if rp3_path else 'Preservation/recipe pending; no availability claimed.',
        'Native_adoption_or_new_dispatcher_deployment': False,
        'owner_inspection_scope': closure['owner_scope'],
        'global_Native_child_absence_verified': False,
    }
    if rp3_path:
        record['evidence'].append({'file': str(rp3_path), 'sha256': sha(rp3_path)})
    old = {key: read(path) for key, path in TARGETS.items()}
    for key, value in old.items():
        require('PI07_scientific_closure' not in value, 'Existing PI07 closure is immutable: ' + key)
    proposed = copy.deepcopy(old)
    prior_keys = ('phase', 'new_Native_ticks_closed', 'principal_Native_ticks', 'last_progress_utc')
    proposed['campaign']['PI07_prior_closure_fields'] = {key: old['campaign'].get(key) for key in prior_keys}
    proposed['campaign'].update(phase='EXPERIMENTATION_CLOSED_NO_ADOPTION_TECHNICAL_FUTURE_BLOCKED',
        new_Native_ticks_closed=ticks, principal_Native_ticks=0, last_progress_utc=now,
        PI07_scientific_closure=record)
    proposed['continuity']['PI07_scientific_closure'] = record
    proposed['transversal']['PI07_scientific_closure'] = {
        'recorded_utc': now, 'campaign': str(P), 'report': record['report'],
        'source_coverage': str(P / 'mapas/FUENTES_Y_COBERTURA.csv'),
        'actual_Native_ticks': ticks, 'diagnostic_worlds': worlds,
        'adopted': False, 'principal_unchanged': principal,
        'scope': 'Directed PI07 reading and executed experiments only. No new full-corpus review or retroactive rewrite of earlier sources.'}
    catalogue = proposed['catalogue']; entries = catalogue['entries']
    require(not set(IDS).intersection(item['id'] for item in entries), 'PI07 catalogue IDs already exist')
    entries.extend([
        {'id': IDS[0], 'name': 'Observación y reproducción física acotadas de PI07 R02',
         'kind': 'instrumento_externo_y_procedimiento_P0',
         'status': 'AVAILABLE_IN_REPRODUCIBILITY_WITH_EXPLICIT_PERSISTENT_STATE_LIMIT',
         'implementation': ['reproducibilidad/recetas/pi07_r02_8_ep04.json'],
         'principal_acquisition': False, 'principal_unchanged': principal,
         'actual_Native_replay': {'file': str(rp2_path), 'sha256': sha(rp2_path)},
         'limits': [record['RP_R02_scope'], 'Replay matches physical observations; it does not establish successful learned protection in R02.']},
        {'id': IDS[1], 'name': 'Regulación contextual PI07 R03: procedimiento experimental preservado',
         'kind': 'procedimiento_experimental_P1_con_aparato_P0',
         'status': 'PRESERVED_EXPERIMENTAL_PROCEDURE_NOT_PRINCIPAL_ACQUISITION' if rp3_path else 'DOCUMENTED_PROCEDURE_PRESERVATION_PENDING',
         'implementation': [registered_recipe.relative_to(C).as_posix(), str(rp3_path)] if rp3_path else [str(P / 'codigo/PROTOCOLO_PI07_R03.json')],
         'principal_acquisition': False, 'principal_unchanged': principal,
         'original_experimental_life': record['experimental_life_id'],
         'results': record['science'], 'new_Native_CLI_replay_verified': False,
         'limits': ['Sequence, sensor codec, tool and opportunities are prepared; no general autonomous agency.',
                    'The final34-resource integration is blocked and is not an operational extension.',
                    record['RP_R03_scope']]},
    ])
    catalogue['PI07_scientific_closure'] = {'recorded_utc': now, 'principal_acquisition': False,
        'current_principal_unchanged': True, 'catalogue_ids': IDS,
        'closure_report': record['report'], 'decision': str(DECISION)}
    require(catalogue['entries'][:-2] == old['catalogue']['entries'], 'Old catalogue prefix changed')
    decision = {'schema': 'DEE.PI07.reasoned_no_adoption.v1', 'recorded_utc': now,
        'adopted': False, 'status': record['adoption_status'], 'current_principal': principal,
        'experimental_cut': record['last_closed_functional_cut'],
        'actual_final_attempt': {'file': str(failure_path), 'sha256': sha(failure_path)},
        'reasons': [record['science']['integration_negative']],
        'positive_scientific_results_preserved': record['science'],
        'no_retry_no_rollback_no_memory_merge': True}
    if DECISION.exists():
        existing = read(DECISION)
        require(existing.get('adopted') is False, 'Existing actual decision contradicts no-adoption')
        decision = existing
    return old, proposed, decision, before_protected, close_path


def prepare(close_path):
    require(not STAGE.exists(), 'Existing stage is immutable')
    old, proposed, decision, protected_hashes, close_path = build(close_path)
    STAGE.mkdir()
    changes = []
    for key, target in TARGETS.items():
        original = target.read_bytes()
        backup = STAGE / (key + '_ANTES_LITERAL.json')
        backup.write_bytes(original)
        changed = STAGE / (key + '_PROPUESTO.json')
        changed.write_bytes(encoded(proposed[key]))
        changes.append({'key': key, 'target': str(target), 'before_sha256': hashlib.sha256(original).hexdigest(),
                        'backup': str(backup), 'proposed': str(changed), 'after_sha256': sha(changed)})
    write_new(STAGE / 'DECISION_PROPUESTA.json', decision)
    plan = {'schema': 'DEE.PI07.documentary_no_adoption.plan.v1', 'Native_ticks': 0,
        'closure': {'file': str(close_path), 'sha256': sha(close_path)},
        'changes': changes, 'protected': protected_hashes,
        'decision_preexists': DECISION.exists(), 'decision_before_sha256': sha(DECISION) if DECISION.exists() else None,
        'decision_proposed_sha256': sha(STAGE / 'DECISION_PROPUESTA.json'),
        'allowed_targets_only': list(map(str, TARGETS.values())), 'catalogue_added_ids': IDS}
    write_new(STAGE / 'PLAN.json', plan)
    print(json.dumps({'plan': str(STAGE / 'PLAN.json'), 'sha256': sha(STAGE / 'PLAN.json'),
                      'new_Native_ticks': 0, 'targets': list(TARGETS)}, ensure_ascii=False))


def apply():
    plan_path = STAGE / 'PLAN.json'; plan = read(plan_path)
    require(not APPLIED.exists(), 'No repeated publication')
    require(plan['schema'] == 'DEE.PI07.documentary_no_adoption.plan.v1', 'Exact reviewed stage required')
    checked_ref(plan['closure'])
    # Fresh owner condition rechecked without rebuilding timestamps or stages.
    closure = read(plan['closure']['file']); owner_path, owner = owner_scope_checked(closure)
    require(protected() == plan['protected'], 'Protected main/source descriptor changed')
    require(set(plan['allowed_targets_only']) == set(map(str, TARGETS.values())), 'Changed write allowlist')
    for item in plan['changes']:
        require(Path(item['target']) == TARGETS[item['key']], 'Target escaped whitelist')
        require(sha(item['target']) == item['before_sha256'], 'CAS rejected current JSON change: ' + item['key'])
        require(sha(item['backup']) == item['before_sha256'] and sha(item['proposed']) == item['after_sha256'],
                'Literal backup or proposed JSON changed')
    require(sha(STAGE / 'DECISION_PROPUESTA.json') == plan['decision_proposed_sha256'], 'Decision stage changed')
    if plan['decision_preexists']:
        require(sha(DECISION) == plan['decision_before_sha256'], 'Existing decision changed')
    else:
        require(not DECISION.exists(), 'A newer decision now exists')
    applied = []
    try:
        for item in plan['changes']:
            target = Path(item['target']); temporary = target.with_name(target.name + '.PI07_DOC_PENDING')
            require(not temporary.exists(), 'Uncertain prior documentary write remains')
            with temporary.open('xb') as stream:
                stream.write(Path(item['proposed']).read_bytes()); stream.flush(); os.fsync(stream.fileno())
            require(sha(target) == item['before_sha256'], 'Concurrent CAS change before replace')
            os.replace(temporary, target)
            require(sha(target) == item['after_sha256'], 'Written documentary bytes differ')
            applied.append({'target': str(target), 'before_sha256': item['before_sha256'], 'after_sha256': sha(target)})
        if not plan['decision_preexists']:
            with DECISION.open('xb') as stream:
                stream.write((STAGE / 'DECISION_PROPUESTA.json').read_bytes())
        after = protected()
        require(after == plan['protected'], 'Protected original changed during documentary write')
    except Exception as exc:
        write_new(STAGE / 'FALLO_DOCUMENTAL_PRESERVADO.json', {'applied_so_far': applied,
            'error': type(exc).__name__ + ': ' + str(exc), 'no_automatic_rollback': True})
        raise
    proof = {'schema': 'DEE.PI07.documentary_no_adoption.applied.v1', 'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'applied': True, 'new_Native_ticks': 0, 'Native_executed': False, 'adopted': False,
        'plan': str(plan_path), 'plan_sha256': sha(plan_path), 'changes': applied,
        'catalogue_ids': IDS, 'selected_principal_unchanged': True,
        'protected_before': plan['protected'], 'protected_after': after,
        'decision': {'file': str(DECISION), 'sha256': sha(DECISION)},
        'scope': 'Existing documentation and catalogue only. No new main experience, operational dispatcher, selector or binary deployment.'}
    write_new(APPLIED, proof)
    print(json.dumps({'proof': str(APPLIED), 'sha256': sha(APPLIED), 'new_Native_ticks': 0,
                      'adopted': False, 'targets': len(applied)}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(); group = parser.add_mutually_exclusive_group()
    group.add_argument('--preparar', action='store_true'); group.add_argument('--aplicar', action='store_true')
    parser.add_argument('--cierre', type=Path); args = parser.parse_args()
    if args.preparar:
        require(args.cierre is not None, 'Use --preparar --cierre <actual closed evidence JSON>')
        prepare(args.cierre)
    elif args.aplicar:
        apply()
    else:
        print(json.dumps({'read_only': True, 'new_Native_ticks': 0, 'targets': {k: str(v) for k, v in TARGETS.items()},
            'required_closure_fields': ['science_closed', 'no_more_Native_actions', 'owner_scope=TWO_SCOPED_HANDLES_ABSENT_NATIVE_CHILD_NOT_IDENTIFIED', 'Native_ticks_all_branches',
                'diagnostic_worlds', 'native_ledger{file,sha256,ticks_path,worlds_path}',
                'owner_proof{file,sha256}', 'RP_R02_Native_replay{file,sha256}',
                'RP_R03_preservation{file,sha256} optional, actual REGISTERED_USABLE_EXPERIMENTAL_RECIPE_NO_MAIN_ADOPTION required']}, ensure_ascii=False))

if __name__ == '__main__':
    main()
