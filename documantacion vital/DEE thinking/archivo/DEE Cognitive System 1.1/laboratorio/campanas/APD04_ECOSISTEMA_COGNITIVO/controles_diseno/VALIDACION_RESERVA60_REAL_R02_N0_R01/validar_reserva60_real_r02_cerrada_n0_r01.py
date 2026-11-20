"""Read-only N0 validation of Root's already closed reserve; never closes/runs it."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PLAN = 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/ejecucion/PLAN_RESERVA60_REAL_R02_CERRADO_R01.json'
PAIR = 'sistema/estado/fuentes_emparejadas/APD04_ACTUADOR_REAL_R02_T656420_PRE_RESERVA_R01'
PAIR_SHA = 'ffd99f416fa0339884a21d2ddd85c817e60dccda1d2f56a57291555717ab0d96'
SNAP_SHA = '3d058c7424dba43a47b653579e1226681ae82ed8a21b203f6acc8f91af5eab0e'
BEFORE = 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/RESERVA60_REAL_R02_R01/TRAYECTORIA/ANTES_DE_NATIVE.json'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_bytes())
def load(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def dump(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2); stream.write('\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    if a.out.exists(): raise FileExistsError('Preserve earlier N0 validation')
    original = (ROOT / PLAN).read_bytes(); p = json.loads(original)
    r02 = load('closed_R02_assembler_no_native', HERE / 'preparar_plan_reserva60_apd04_n0_r02.py'); r01 = r02.base()
    expected = r02.make(r01, p['life'], p['world_id'], 'independent_balanced', SNAP_SHA, 656420,
                        p.get('resume_pending_id'), True, p['candidate_genealogy'])
    if expected != p: raise ValueError('Closed plan differs from declared exact assembler output')
    driver = load('driver_static_validation_only', ROOT / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/ejecucion/ejecutar_plan_apd04_r03.py')
    driver.validate_plan(p)
    protocol = load('protocol_static_only', ROOT / 'sistema/app/protocolo_apd04.py')
    ui = load('literal_parser_no_execution', ROOT / 'sistema/app/usar_dee.py')
    rows = [row for e in p['events'] if e['kind'] == 'material' for row in e['situations']]
    for row in rows + p['after_window_pending']['situations']: protocol.validate_literal(row)
    for e in p['events']:
        if e['kind'] == 'command': ui.literal_rows(ui.command_parser().parse_args(e['argv']))
    works = [e for e in p['events'] if e['kind'] == 'material' and e['situations'][0]['modo'] == 'apd04-vivir']
    if len(works) != 43 or any(e['situations'][0]['sensor'] != 'independent_balanced' or e['feedback'] != 'real'
                              or e['situations'][0]['desacoplado'] or not e['situations'][0]['lexico'] for e in works):
        raise ValueError('Sensor/feedback/lexicon assistance differs from fixed43work specification')
    forbidden = [row for row in rows if row['modo'] in ('apd04-r04-admitir', 'apd04-iniciar') or row.get('sensor') == 'independent_two_pairs']
    if forbidden: raise ValueError('R04 admission or silent world reset in agenda')
    if sha(ROOT / PAIR / 'EXPORTACION_SERVICIO.json') != PAIR_SHA: raise ValueError('Exact full pair changed')
    obs = load('pre_reserve_full_metadata_parser_only', ROOT / 'sistema/capacidades/observador_causal_retrospectivo_01.py')
    s = obs.Snapshot(ROOT / PAIR / 'VIDA.deetsnap.gz', verify_checksum=False)
    if s.tick != 656420 or s.N != 67 or s.encoded_sha256 != SNAP_SHA: raise ValueError('Wrong actual selected full snapshot')
    env = json.loads(s.metadata['DEE.Cognitive.System.1.1.APD04.ecosystem.R01'])
    if env['action_codec'] != 'R02' or len(env['objects']) != 2 or env['cursor'] != 0 or env['in_progress'] is not None or s.pending:
        raise ValueError('The actual inherited codec/environment/protocol differs from reserved preparation')
    ref_a, ref_b = s.observation([14, 14, 15]), s.observation([16, 14, 15])
    reference = ref_b['s_reg'] - ref_a['s_reg']
    before = read(ROOT / BEFORE); congruence = []
    for src in before['sources']:
        origin = Path(src['source']); copy = (ROOT / BEFORE).parent / src['copy']
        if sha(origin) != src['sha256'] or sha(copy) != src['sha256']:
            raise ValueError('Actual source or archived before-Native bytes diverged: ' + origin.name)
        congruence.append({'source': origin.relative_to(ROOT).as_posix(), 'copy': copy.relative_to(ROOT).as_posix(),
                           'sha256': src['sha256'], 'actual_equals_execution_copy': True})
    # This forecast describes only the already prepared circular environmental
    # cursor and static tag/goal eligibility. It NEVER predicts/chooses an action.
    count = 2; cursor = env['cursor']; goal = env['goal_tag']; word = env['word']; criterion = 20; slots = []
    for e in p['events']:
        if e['kind'] != 'material': continue
        row = e['situations'][0]
        if row['modo'] == 'apd04-ampliar': count = row['fuentes']
        elif row['modo'] == 'apd04-cambio':
            goal = row.get('etiqueta_objetivo', goal); word = row.get('palabra', word); criterion = row.get('criterio', criterion)
        elif row['modo'] == 'apd04-vivir':
            slots.append({'request_id': e['request_id'], 'at_seconds': e['at_seconds'], 'source_count': count,
                          'prepared_circular_source_id': cursor, 'tag': cursor % 2, 'goal_tag': goal, 'word': word,
                          'auditor_criterion': criterion, 'new_usefulness_eligible_by_tag_only': cursor % 2 == goal,
                          'action_and_actual_usefulness_not_predicted': True})
            cursor = (cursor + 1) % count
    eligible = sum(r['new_usefulness_eligible_by_tag_only'] for r in slots)
    result = {'schema': 'APD04.closed_reserve.read_only_N0_review.R01', 'new_Native_ticks': 0,
              'plan': PLAN, 'plan_sha256': hashlib.sha256(original).hexdigest(), 'status_unchanged': p['status'],
              'exact_R02_assembler_values_equal': True, 'literal_events': len(p['events']), 'material_rows': len(rows),
              'work_opportunities': len(works), 'no_R04_admission_or_world_reset': True,
              'generic_posteffect_feedback': 'Frozen real SUCCESS/FAILURE after action/effect, transduced by fixed route. No correct-action or expected-content instruction in work payloads. Explicit A/B lessons and fixed public current-value calibration are separately scheduled interventions.',
              'full_start': {'pair': PAIR, 'pair_manifest_sha256': PAIR_SHA, 'snapshot_sha256': SNAP_SHA,
                             'tick': s.tick, 'N': s.N, 'paused': s.paused, 'phase': s.phase, 'tick_mod_391': s.tick % 391,
                             'pending_native': s.pending, 'environment_original_values': env,
                             'Mu_A_observation': ref_a, 'Mu_B_observation': ref_b,
                             'passive_relative_reference_B_minus_A': reference,
                             'Mu_A_B_clocks_equal_saved_world_tick': ref_a['clock'] == ref_b['clock'] == str(s.tick),
                             'route_A': s.observation([24, 12, 53]), 'route_B': s.observation([26, 12, 53]),
                             'R04_pair_metadata_present': any('two_balanced_raw_pairs' in k for k in s.metadata),
                             'scope': 'Offline SHA/format/metadata/RAW observation. Existing checksum not rerun; no functional query, Native admission or future reference trajectory is tested.'},
              'sources_compared_to_actual_before_Native_copies': congruence,
              'prepared_cursor_eligibility_forecast_auditor_only': slots,
              'new_usefulness_tag_eligible_slots': eligible, 'new_usefulness_tag_ineligible_slots': len(slots) - eligible,
              'utility_scope_not_a_metric_change': ['The fixed useful flag measures a NEW task-relevant environmental gain, not every valid/correct response or conserved capability.',
                'Every slot with tag!=goal is useful=false for INSPECT/USE by definition; Native abstention is not rewarded as successful ignoring. This limits the denominator, not Native capacity.',
                'INSPECT of an unchanged current cache and correct USE of an already equal bin are useful=false; correct_classifications remains separate when the cached version is current.',
                'Initial object1 already has bin+; mutation24→25 keeps expected+ but makes its24/version1 cache stale. No valid refreshed repeated+ classification would be NEW unless another action first changed the bin.',
                'When a task is already completed there may be no possible new gain until a relevant exogenous change; repeated FAILURE feedback then is a feature/limit of this frozen reward definition, not proof of forgotten knowledge.',
                'The equal5/5 negative-transfer slot at2880 visits source7tag1/goal0 under this circular schedule, so usefulness is false regardless. A real numerical emission/gap change can still be examined separately if Native USE reaches balance.',
                'Do not change feedback, target matching or newness criteria after seeing reserved results. Preserve main denominators and interpret valid/correct/reused/new/useful distinctly.',
                'Static planned rates, source counts and predictions are not realized admissions, twenty simultaneous observations or independent samples.'],
              'no_S_plan_life_queue_changes': True}
    if (ROOT / PLAN).read_bytes() != original: raise ValueError('Plan changed during N0 review')
    if any(k.startswith('dee_thinking') for k in sys.modules): raise RuntimeError('N0 imported Native')
    a.out.mkdir(); dump(a.out / 'VALIDACION_Y_ALCANCE_METRICA.json', result)
    shutil.copy2(Path(__file__), a.out / Path(__file__).name)
    print(json.dumps({'out': str(a.out), 'plan_sha256': result['plan_sha256'], 'events': len(p['events']),
                      'work43': len(works), 'source_copies_equal': len(congruence), 'Mu_reference': reference,
                      'tag_eligible': eligible, 'tag_ineligible': len(slots) - eligible, 'Native_ticks': 0}, ensure_ascii=False))


if __name__ == '__main__': main()
