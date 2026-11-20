"""Prospective N0 revision: post-ten-work originals precede material panels.

No Native, shared-system edit, life creation or plan closure. Every old draft
remains intact. Diagnostic descendants are not consecutive uses of originals.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OLD = HERE / 'PROPUESTA_DOS_AUX_WAIT_R03_SAFE_N0_R03'
OUT = HERE / 'PROPUESTA_DOS_AUX_WAIT_R03_SAFE_N0_R04'


def read(p): return json.loads(p.read_bytes())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, v):
    with p.open('x', encoding='utf8', newline='\n') as f:
        json.dump(v, f, ensure_ascii=False, indent=2); f.write('\n')
def load(name, p):
    s = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


def main():
    if OUT.exists(): raise FileExistsError('Never overwrite a proposal')
    manifest = read(OLD / 'MANIFIESTO.json')
    for x in manifest['members']:
        if sha(OLD / x['file']) != x['sha256']: raise ValueError('Previous proposal changed')
    driver = load('existing_driver_N0_only_R04', ROOT / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/ejecucion/ejecutar_plan_apd04_r03.py')
    OUT.mkdir()
    checks = []
    for arm in ('REAL', 'OMIT'):
        previous = read(OLD / ('PLAN_WAIT_R03_' + arm + '_DRAFT_R02.json'))
        p = copy.deepcopy(previous)
        p['life'] = p['world_id'] = 'APD04_WAIT_R03_' + arm + '_AUX_R04'
        unchanged = [copy.deepcopy(e) for e in p['events'] if e['at_seconds'] < 780]
        p['events'] = unchanged + [{'at_seconds': 760, 'kind': 'checkpoint', 'tag': 'post10_original_pre_material_panel'}]
        p['duration_seconds'] = 780
        p['supervision_wall_limit_seconds'] = 1800
        p['scope'] += ' R04 prospective revision: original executes only ten opportunities, saves/stops and seals its actual FULL state BEFORE any material old/new-word panel. Diagnostic descendants may then receive those queries; do not count them as consecutive uses of this original.'
        p['diagnostic_panels_removed_from_original'] = True
        p['required_postSTOP_complete_pair'] = 'Actual reached original FULL, with confirmed owner stopped and queue state preserved; never substitute an earlier favorable cut.'
        p['timing_is_a_new_N0_proposal_for_Root_not_an_existing_native_result'] = True
        # Request IDs and every material/command through op10 are byte-equivalent
        # as JSON values to the prior draft. Only future life identity differs.
        expected_prefix = [e for e in previous['events'] if e['at_seconds'] < 780]
        if unchanged != expected_prefix: raise ValueError('Ten-op curriculum changed')
        test = copy.deepcopy(p); test.update(status='CLOSED_FOR_EXECUTION', initial_snapshot_sha256='0'*64, initial_tick=639374)
        driver.validate_plan(test)
        write(OUT / ('PLAN_WAIT_R03_' + arm + '_ORIGINAL_DRAFT_R04.json'), p)
        diagnostic = copy.deepcopy(previous)
        diagnostic['life'] = diagnostic['world_id'] = p['life'] + '_PANEL_DIAGNOSTICO'
        diagnostic['initial_snapshot_sha256'] = diagnostic['initial_tick'] = None
        diagnostic['required_parent_complete_pair'] = None
        diagnostic['required_parent_snapshot_sha256'] = diagnostic['required_parent_tick'] = None
        diagnostic['required_parent_life_after_actual_post10_STOP'] = p['life']
        diagnostic['proposed_identity_not_yet_imported'] = True
        diagnostic['events'] = [
            {'at_seconds': 0, 'kind': 'command', 'request_id': 'apd04_wait_' + arm.lower() + '_r04_diagnostic_old22',
             'argv': ['panel', '--nuevas', '--memorias', '--retorno', 'omit']},
            {'at_seconds': 210, 'kind': 'material', 'request_id': 'apd04_wait_' + arm.lower() + '_r04_diagnostic_clasifica',
             'situations': [{'modo': 'apd04-palabra', 'texto': 'clasifica'}], 'feedback': 'omit', 'actuator': 'closed'},
            {'at_seconds': 240, 'kind': 'material', 'request_id': 'apd04_wait_' + arm.lower() + '_r04_diagnostic_equilibra',
             'situations': [{'modo': 'apd04-palabra', 'texto': 'equilibra'}], 'feedback': 'omit', 'actuator': 'closed'},
            {'at_seconds': 280, 'kind': 'checkpoint', 'tag': 'diagnostic_post_material_retention_panel'}]
        diagnostic.update(duration_seconds=300, supervision_wall_limit_seconds=900,
            scope='Material old16+MA6 and two new-word retention on a FULL diagnostic descendant of the actual post10 original only. No teaching; queries can change its physical future. Do not attribute this separate future to original, MAIN or another arm.',
            no_original_mutation=True, matched_original_knowledge_not_acquisition_by_import=True,
            diagnostic_parent_must_be_assembled_after_original_closure=True)
        diagnostic.pop('required_P0_action_codec', None)
        dt = copy.deepcopy(diagnostic); dt.update(status='CLOSED_FOR_EXECUTION', initial_snapshot_sha256='0'*64, initial_tick=639374)
        driver.validate_plan(dt)
        write(OUT / ('PLAN_WAIT_R03_' + arm + '_PANEL_DIAGNOSTICO_DRAFT_R04.json'), diagnostic)
        checks.append({'arm': arm, 'original_work': 10, 'original_material_retention_queries': 0,
                       'diagnostic_panel_old16_MA6': True, 'diagnostic_new_word_queries': 2,
                       'all_pre780_events_exact_prior_JSON_values': True,
                       'Native_ticks': 0, 'life_or_descendant_created': False})
    c = read(OLD / 'CONTRATO_Y_CRITERIOS_WAIT_R03_R02.json')
    c['schema'] = 'APD04.WAIT_affordance_and_posteffect_contract.N0.R04'
    c['revision_R04_reason'] = 'Root requires the prospective long-reserve candidate remain at its post10 original future before material old22/new2 panels. Queries occur only in identified diagnostic descendants.'
    c['curriculum']['retention'] = 'Not in original. Same old16+MA6 and clasifica/equilibra material queries on FULL diagnostic descendants after original saved/stopped/sealed. Separate futures, not same-life consecutive use.'
    c['timing_proposal_not_yet_approved_by_Root'] = {
        'original': {'duration_seconds': 780, 'outer_guard_seconds': 1800},
        'diagnostic': {'duration_seconds': 300, 'outer_guard_seconds': 900},
        'scope': 'New prospective proposal; Root must approve execution. Guards retain exact unresolved queued/processing state, no favorable replacement.'}
    c['plan_validation'] = checks
    c['previous_source_manifest_sha256'] = sha(OLD / 'MANIFIESTO.json')
    write(OUT / 'CONTRATO_Y_CRITERIOS_WAIT_R03_R04.json', c)
    write(OUT / 'REVISION_PROSPECTIVA_N0.json', {'checks': checks, 'shared_system_edited': False,
        'Native_ticks': 0, 'status': 'DRAFT_NOT_AUTHORIZED_FOR_NATIVE',
        'old_folder': str(OLD), 'old_manifest_sha256': sha(OLD / 'MANIFIESTO.json'),
        'candidate_original_and_material_diagnostics_are_different_future_branches': True})
    shutil.copy2(Path(__file__), OUT / Path(__file__).name)
    write(OUT / 'MANIFIESTO.json', {'self_hash_excluded': True, 'members': [
        {'file': q.name, 'bytes': q.stat().st_size, 'sha256': sha(q)} for q in sorted(OUT.iterdir()) if q.is_file()]})
    if any(k.startswith('dee_thinking') for k in sys.modules): raise RuntimeError('Unexpected Native import')
    print(json.dumps({'out': str(OUT), 'Native_ticks': 0, 'manifest_sha256': sha(OUT / 'MANIFIESTO.json')}))


if __name__ == '__main__': main()
