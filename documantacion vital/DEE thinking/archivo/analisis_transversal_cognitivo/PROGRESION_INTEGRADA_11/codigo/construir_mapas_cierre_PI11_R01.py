"""Build small PI11 maps/reading entry from explicit actual CLOSED evidence.

No Native, owner, SQLite, Word or operational writes. --schema prints the
final Native closure shape. --native-closure FILE --facts CLOSED_REPORT_FACTS
--out-dir NEW_DIRECTORY writes five small artifacts only after validation.
Without --out-dir it prints a read-only plan. It never promotes MAIN or
represents partial POST4 as4/4. The protected PI10 selection is read literally.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import csv
import hashlib
import io
import json
import re
import xml.etree.ElementTree as ET
import zipfile

P = Path(__file__).resolve().parents[1]
R = P.parents[2]
C = R / 'DEE Cognitive 2.0'
PROTECTED = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'
PROTECTED_T = 947395
PROTECTED_SNAPSHOT = 'fd7372b7f2adc9040866fab8adfaca0d79e0bd18e997c0abc0651fe4fa3c23dc'
MANUAL = C / 'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'
COMP = R / 'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx'
PUBLICATION = P / 'documentos/PUBLICACION_EDICION_1_40_PI11_R01.json'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text('utf-8-sig'))


def regular(path):
    p = Path(path).absolute()
    for node in (p, *p.parents):
        need(not node.is_symlink(), 'No linked path')
        if node.exists():
            need(not (getattr(node.lstat(), 'st_file_attributes', 0) & 1024), 'No reparse path')
    need(p.is_file() and p.resolve().is_relative_to(R.resolve()), 'Actual existing DEE source required')
    return p.resolve()


def info(p):
    p = regular(p)
    return {'path': str(p), 'bytes': p.stat().st_size, 'sha256': sha(p)}


def pinned(ref):
    p = regular(ref.get('path', ref.get('source')))
    need(re.fullmatch('[0-9a-f]{64}', ref.get('sha256', '')) and sha(p) == ref['sha256'], 'Actual closed source hash changed')
    return p


def pointer(value, path):
    for key in path:
        value = value[key]
    return value


def core_panel(proof_ref):
    proof_path = pinned(proof_ref)
    owner = read(proof_path)
    need(owner.get('closed') is True and owner.get('error') is None and owner.get('status') == 'CLOSED_FINITE_PHASE', 'Actually closed successful panel required')
    plan_path = regular(owner['plan'])
    need(sha(plan_path) == owner['plan_sha256'], 'Original frozen panel plan changed')
    plan = read(plan_path)
    need(owner['initial_tick'] == 972419 and owner['final_tick'] == 975259 and owner['new_Native_ticks'] == 2840,
         'This map is the actual T975259panel, not a later/full-panel claim')
    rows = []
    by_label = {record['label']: record for record in owner['records']}
    for step in plan['steps']:
        if 'read_path' not in step:
            continue
        record = by_label[step['label']]
        primary_path = regular(record['primary'])
        need(sha(primary_path) == record['sha256'], 'Complete panel primary changed')
        primary = read(primary_path)
        actual = pointer(primary, step['read_path'])
        need(actual == record['actual'] and record['expected'] == step['expected']
             and record['correct'] is (actual == step['expected']), 'Panel field/declared read_path mismatch')
        rows.append({'label': step['label'], 'actual': actual, 'expected': step['expected'], 'correct': actual == step['expected'],
                     'life_id': owner['life_id'], 'before_tick': record['before_tick'], 'after_tick': record['after_tick'],
                     'read_path': step['read_path'], 'primary': info(primary_path), 'literal': record['literal']})
    need(len(rows) == 12 and sum(row['correct'] for row in rows) == 12, 'Actual complete12/12published core panel required')
    number13 = next(row for row in rows if row['label'] == 'number13')
    number8 = next(row for row in rows if row['label'] == 'number8')
    need(number8['literal']['izquierda'] == number13['actual'], 'Second operation must receive the first real produced integer')
    return {'owner_proof': info(proof_path), 'plan': info(plan_path), 'life_id': owner['life_id'],
            'initial_tick': 972419, 'final_tick': 975259, 'Native_ticks': 2840,
            'correct': 12, 'responded': 12, 'requested': 12, 'rows': rows,
            'not_twelve_independent_concepts': True, 'later_complete_panel_claimed': False}


def document_state():
    publication = read(regular(PUBLICATION))
    need(publication.get('internal_edition') == '1.40', 'Generate final maps after actual publication1.40')
    documents = {}
    for p in (MANUAL, COMP):
        current = info(p)
        matches = [row for row in publication['rows'] if Path(row['published']['path']).resolve() == p.resolve()]
        need(len(matches) == 1 and matches[0]['published']['sha256'] == current['sha256'], 'Current full document differs from publication')
        with zipfile.ZipFile(p) as z:
            need(z.testzip() is None, 'Current DOCX CRC failure')
            node = ET.fromstring(z.read('docProps/core.xml')).find('{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}version')
            need(node is not None and node.text == '1.40', 'Actual internal edition1.40 required')
        documents['manual' if p == MANUAL else 'compendium'] = current
    return {**documents, 'publication': info(PUBLICATION), 'internal_edition': '1.40',
            'visual_status': publication['visual_status'], 'new_render_performed_by_mapper': False}


def find_arm(facts, role):
    rows = [a for a in facts['arms'] if a['role'].casefold() == role.casefold()]
    need(len(rows) == 1 and rows[0]['status'] == 'executed_closed', 'Final measured arm required: ' + role)
    return rows[0]


def build(native_path, facts_path):
    native_path = regular(native_path); facts_path = regular(facts_path)
    native_before = sha(native_path); facts_before = sha(facts_path)
    closure = read(native_path); facts = read(facts_path)
    need(closure.get('schema') == 'DEE.PI11.final_native_closure.R01'
         and closure.get('closed_for_documentary_read') is True and closure.get('native_running') is False,
         'Actual final Native closure required; do not finalize while RP remains pending')
    need(closure.get('principal_adopted') is False, 'This version preserves the actual PI11 non-adoption; different future requires explicit revision')
    need(facts.get('schema') == 'DEE.PI11.closed_report_facts.R01' and facts.get('closed_for_report') is True, 'Actual closed report facts required')
    need(datetime.fromisoformat(facts['cut_utc'].replace('Z', '+00:00')).tzinfo is not None, 'Actual timezone-aware final cut required')
    active_path = C / 'sistema/estado/ACTIVO.json'; active = read(regular(active_path))
    need(active['life_id'] == PROTECTED and active['tick'] == PROTECTED_T and active['snapshot_sha256'] == PROTECTED_SNAPSHOT,
         'Protected principal changed; never project the experimental future into it')
    selected = facts['selected_life']
    need(selected['life_id'] == active['life_id'] and selected['T'] == active['tick'] and selected['snapshot_sha256'] == active['snapshot_sha256'], 'Report selection differs from ACTIVO')
    card_path = C / 'sistema/estado/vidas' / active['life_id'] / 'VIDA.json'; card = read(regular(card_path))
    snapshot_path = regular(C / 'sistema' / card['snapshot'])
    need(card['physical']['N'] == 67 and card['physical']['tick'] == active['tick']
         and sha(snapshot_path) == active['snapshot_sha256'], 'Protected coherent card/snapshot mismatch')
    protected = {'ACTIVO': info(active_path), 'VIDA': info(card_path), 'snapshot': info(snapshot_path)}
    core = core_panel(closure['panel']['owner_proof'])
    experimental = closure['main_experimental']
    need(experimental['life_id'] == core['life_id'] and experimental['N'] == 67
         and experimental['last_observed_tick'] == 979389, 'Actual adverse MAIN identity/observed cut required')
    need(experimental.get('last_saved_tick') is None or type(experimental['last_saved_tick']) is int,
         'Saved checkpoint cut must be actual or explicitly unknown, never inferred from observed tick')
    post = closure['post_panel']
    need(post['requested'] == 4 and post['completed'] == 2 and post['completed_ticks'] == [1852, 1564]
         and post['partial_ticks'] == 714 and post['unexecuted'] == 1
         and post['last_observed_tick'] == 979389 and post['stopped_by_host'] is True,
         'Actual2complete+1partial+1unexecuted safety-stop window required; never4/4')
    need(core['final_tick'] + sum(post['completed_ticks']) + post['partial_ticks'] == post['last_observed_tick'], 'POST4tick accounting conflict')
    post_proof = info(pinned(post['source'])); autopsy = info(pinned(closure['autopsy']))
    # An incomplete Native-return sequence can already have a known, committed
    # external effect. A NULL transport result must not erase that event.
    autopsy_value = read(autopsy['path'])
    need(autopsy_value.get('schema') == 'DEE.PI11.passive.closure_autopsy.R01', 'Actual closed autopsy required')
    completed_post = autopsy_value['two_completed_post_episodes']
    need(len(completed_post) == 2 and all(row['resource']['physical_delivered'] is False for row in completed_post),
         'Known two completed POSTresults must not be presented as successful deliveries')
    third = autopsy_value['failed_third']
    committed = third['environmental_consequence_already_committed']
    third_result_path = pinned(committed['source']); actual_third = read(third_result_path)
    need(actual_third == committed['result'] and actual_third['ordinal'] == 18
         and actual_third['tick'] == 979181 and actual_third['actual_route'] == 0
         and actual_third['available_bin'] == 1 and actual_third['certificate_valid'] is True
         and actual_third['command_valid'] is True and actual_third['physical_delivered'] is False,
         'Actual committed third environmental consequence differs; do not replace it withNULL')
    environment = third['environment_at_end']
    need(environment['completed'] == 19 and environment['open_offer'] is None
         and third['saved_pending_Native'] == 0, 'Separate environment/Native completion levels changed')
    future_returns = [third['intent']['calendar'][stage]['outcome_injection_tick'] for stage in ('second', 'first')]
    need(future_returns == [979453, 980235] and all(t > post['last_observed_tick'] for t in future_returns),
         'Original not-yet-admitted return calendar differs')
    known_post = {'requested_opportunities': 4, 'admitted_opportunities': 3,
                  'environment_actions_committed': 3, 'physical_deliveries': 0,
                  'Native_sequences_completed': 2, 'Native_sequences_partial': 1,
                  'opportunities_not_executed': 1,
                  'third_environmental_consequence': {'source': info(third_result_path), 'result': actual_third},
                  'third_environmental_effect_is_known': True,
                  'third_Native_generic_returns_not_yet_admitted': future_returns,
                  'environment_completed_counter': environment['completed'], 'environment_open_offer': None,
                  'environment_last_recorded_tick': environment['tick'],
                  'transport_result_NULL_is_not_unknown_environmental_effect': True}
    for key, value in known_post.items():
        need(key not in post or post[key] == value, 'Explicit post closure contradicts actual committed environmental evidence')
    post = {**post, **known_post}
    rp = closure['reproduction']; rp_result_path = pinned(rp['result']); rp_actual = read(rp_result_path)
    need(rp['status'] in ('COMPLETED', 'BLOCKED', 'FAILED_PRESERVED', 'PRESERVED_PARTIAL'), 'Actual terminal RP outcome, not a future positive')
    strict = None; comparison = None
    if rp.get('comparison') is not None:
        comparison_path = pinned(rp['comparison']); comparison = info(comparison_path)
        value = read(comparison_path)
        need(type(value.get('overall')) is bool and value.get('new_Native_ticks') == 0, 'Actual passive strict replay comparison required')
        strict = value['overall']
    if rp['status'] == 'COMPLETED':
        need(rp_actual.get('status') == 'COMPLETED' and rp_actual.get('owner_closed_coherently') is True,
             'Reported completed RP needs real coherent completion result')
    need(type(rp['product_recipe_available']) is bool, 'Explicit actual product recipe availability required')
    recipe = info(pinned(rp['recipe'])) if rp.get('recipe') is not None else None
    if rp['product_recipe_available']:
        need(recipe is not None and Path(recipe['path']).is_relative_to((C / 'reproducibilidad').resolve()),
             'Product recipe claim requires actual preserved recipe inside Cognitive')
    states = []
    for row in closure['local_state_manifests']:
        need(row['role'] and row['scope'], 'Actual local state role/scope required')
        ref = info(pinned(row))
        states.append({'role': row['role'], 'manifest': ref, 'scope': row['scope'],
                       'full_state_rehashed_by_this_mapper': False})
    need({'PRINCIPAL', 'PREFIJO_MAIN', 'ADVERSO_MAIN', 'SEMILLA_RP_R02'} <= {s['role'] for s in states},
         'Preserve explicit full-state locators for principal,prefix,adverse future and readonly RPseed')
    docs = document_state()
    main = find_arm(facts, closure.get('main_arm_role', 'MAIN'))
    base = find_arm(facts, closure.get('baseline_arm_role', 'HEREDADO'))
    need(main['completed'] == base['completed'] == 16 and main['attributed'] == 8 and base['attributed'] == 9
         and main['FI_uses'] == 10 and base['FI_uses'] == 16 and main['certificate_reuses'] == 2,
         'Use actual MAIN16/HEREDADO16cost-benefit facts; this map is not a favorable future')
    reduction = 100 * (base['FI_uses'] - main['FI_uses']) / base['FI_uses']
    matrix = []
    for row in core['rows']:
        matrix.append({'function': row['label'], 'principal_before': PROTECTED, 'principal_before_T': PROTECTED_T,
                       'principal_final': PROTECTED, 'principal_final_T': PROTECTED_T,
                       'previous_principal_panel_T': 943970, 'experimental_life': core['life_id'],
                       'experimental_test_T': row['after_tick'], 'actual': row['actual'], 'expected': row['expected'],
                       'correct': row['correct'], 'incorporation': 'Principal unchanged; experimental12/12only atT975259',
                       'assistance': 'Prepared API and material query/read_path; real Native result',
                       'limit': 'Not a complete panel atT979389 or a fresh panel of protected principalT947395',
                       'source': row['primary']['path'], 'source_sha256': row['primary']['sha256']})
    matrix.extend([
        {'function': 'PI11 Native-gated FI renewal/reuse', 'principal_before': PROTECTED, 'principal_before_T': PROTECTED_T,
         'principal_final': PROTECTED, 'principal_final_T': PROTECTED_T, 'previous_principal_panel_T': 943970,
         'experimental_life': core['life_id'], 'experimental_test_T': 972419, 'actual': '8/16 usos atribuibles; 10 FI; 2 reusos',
         'expected': 'System-level cost/benefit measured separately', 'correct': 'Not an intelligence score',
         'incorporation': 'Experimental only; not acquired by protected MAIN',
         'assistance': 'Fixed scheduler/curriculum, RAWage9 and external certificate; Native output gates FIcontinuation',
         'limit': 'Global16: FIexecutions−37.5%; one fewer attributed product vs9/16. No FI savings demonstrated in reserve; no energy/tick savings or general superiority.',
         'source': str(native_path), 'source_sha256': sha(native_path)},
        {'function': 'PI11 POST4availability/reopening', 'principal_before': PROTECTED, 'principal_before_T': PROTECTED_T,
         'principal_final': PROTECTED, 'principal_final_T': PROTECTED_T, 'previous_principal_panel_T': 943970,
         'experimental_life': core['life_id'], 'experimental_test_T': 979389,
         'actual': '4 requested; 3 admitted/3 environmental actions; 0 deliveries; 2 Native complete+1partial714ticks+1unexecuted',
         'expected': 'Known third route0/bin1 atT979181 is notNULL; Native returns remained incomplete',
         'correct': 'Safety-truncated; no promotion', 'incorporation': 'Adverse future preserved, no adoption',
         'assistance': 'External operational safety guard stopped host',
         'limit': 'Third external effect known, Native progress uncertain/incomplete; no later full-panel, automatic recovery or universal failure claim',
         'source': post_proof['path'], 'source_sha256': post_proof['sha256']},
        {'function': 'PI11 diagnostic acquisition recipe', 'principal_before': PROTECTED, 'principal_before_T': PROTECTED_T,
         'principal_final': PROTECTED, 'principal_final_T': PROTECTED_T, 'previous_principal_panel_T': 943970,
         'experimental_life': rp_actual.get('life', rp.get('life_id', 'Explicit RPresult')),
         'experimental_test_T': rp.get('final_tick', 'See actual RPresult'), 'actual': rp['status'],
         'expected': 'Actual replay including original errors', 'correct': strict if strict is not None else 'Not verified',
         'incorporation': 'Product diagnostic recipe available' if rp['product_recipe_available'] else 'No product recipe claim',
         'assistance': 'Full prefixed state and fixed instruments; reproduction is a separate diagnostic history',
         'limit': 'Never a learned PI11capacity of protected MAIN; deterministic replay is not an independent individual',
         'source': str(rp_result_path), 'source_sha256': sha(rp_result_path)}])
    continuity = {'schema': 'DEE.PI11.final_continuity_map.R01', 'cut_utc': facts['cut_utc'],
                  'principal': {'life_id': PROTECTED, 'N': 67, 'T': PROTECTED_T, 'status': 'COMMITTED',
                                'snapshot_sha256': PROTECTED_SNAPSHOT, 'adopted_PI11': False,
                                'protected_files': protected, 'fresh_material_use_by_this_mapper': False,
                                'latest_known_full_principal_panel_T': 943970, 'latest_known_public_use_T': 947395},
                  'experimental_PI11': experimental, 'core_panel': core, 'post_panel': post,
                  'reproduction': {'status': rp['status'], 'result': info(rp_result_path), 'strict_comparison': comparison,
                                   'strict_overall_actual': strict, 'product_recipe_available': rp['product_recipe_available'], 'recipe': recipe},
                  'Native_control_comparison': {'MAIN16': main, 'HEREDADO16': base, 'FI_execution_reduction_percent': reduction,
                                                'attributed_product_difference': main['attributed']-base['attributed'],
                                                'reserved_FI_savings_demonstrated': False,
                                                'energy_or_tick_savings_demonstrated': False},
                  'documents': docs, 'autopsy': autopsy, 'local_states': states,
                  'sources': {'native_closure': info(native_path), 'closed_report_facts': info(facts_path)},
                  'new_Native_ticks_by_mapper': 0, 'one_principal_only': True,
                  'resume_scope': 'Use protected PI10principal only. PI11adverse future remains evidence; any further use requires explicit diagnostic reconciliation, not silent rewind.'}
    omissions = {'schema': 'DEE.PI11.localized_large_omissions.R01', 'cut_utc': facts['cut_utc'],
                 'not_an_operational_backup': True, 'retained_local_state_manifests': states,
                 'protected_principal_snapshot': protected['snapshot'],
                 'reason': 'Small analysis package omits complete operational states/SQLite/engine/telemetry; these are preserved locally and not deleted.',
                 'additional': closure.get('additional_omissions', []), 'all_omitted_bytes_rehashed': False}
    locations = {'schema': 'DEE.PI11.local_state_routes.R01', 'principal_full_product': str(C),
                 'principal_card': protected['VIDA'], 'principal_snapshot': protected['snapshot'],
                 'principal_required_components': ['snapshot', 'VIDA', 'interfaces/agenda inside complete state',
                                                   'services SQLite and associated coherent files', 'queues/receipts/outbox',
                                                   'worker artifacts', 'finite resources', 'code/contracts'],
                 'manifests': states, 'experimental_adverse_directory': str(P/'estados/MAIN01'),
                 'map_does_not_certify_only_RAW_clocks_as_complete': True,
                 'documents': docs, 'recipes': recipe, 'no_sources_moved_or_archived': True}
    reading = (
        'DEE PI11 CIERRE DE ETAPA\n\nCorte real: ' + facts['cut_utc'] + '\n'
        'Principal conservado: ' + PROTECTED + ', N67/T947395, COMMITTED. No se adoptó PI11.\n'
        'PI11 experimental: ' + experimental['life_id'] + ', último observado T979389; consultar por separado su último checkpoint guardado.\n'
        'MAIN16 obtuvo 8/16 usos atribuibles frente a 9/16 del heredado; ejecutó 10 FI frente a 16, −37.5% de operaciones FI, con 2 reusos. Coste: un producto menos. La reserva no acreditó ahorro FI. No es ahorro energético ni superioridad general.\n'
        'El núcleo 12/12 se comprobó sólo en la candidata hasta T975259. POST4: cuatro solicitadas, tres admitidas y tres actuaciones ambientales, sin entregas. Dos secuencias Native completas (1852+1564 ticks), una parcial de 714 ticks y una sin ejecutar; HostSafetyStop. La tercera actuó en T979181, ruta 0 frente a recurso en bin 1, con certificado válido: ese efecto es conocido aunque el retorno Native quedó incompleto. No 4/4 ni nuevo panel posterior.\n'
        'RP actual: ' + rp['status'] + '; comparación estricta: ' + str(strict) + '. Receta en el producto: ' + str(rp['product_recipe_available']) + '. Reproducir una adquisición en un clon no enseña al principal.\n'
        'Manual rector DCS11-MM-001, edición 1.40, conserva nombre Edicion_1_21; Compendio 1.40 completo. Estado visual: ' + docs['visual_status'] + '.\n\n'
        'Orden de lectura: continuidad corriente y Manual; informe único y matriz; protocolo y autopsia; primarios, controles y recálculos. El índice PI01–PI10 existente conserva la trayectoria; no se anidan sus ZIP.\n'
        'El anfitrión prepara oportunidades, tiempos, correspondencias y suministro. El certificado es externo y el RAW técnico tiene 9 ticks de antigüedad; no son memoria Native ni energía.\n'
        'Los manifiestos locales indican estados completos y semilla readonly R02. Este ZIP de análisis no los sustituye, no cambia el ente y no es respaldo ejecutable. No se ejecutaron ticks al construir estos mapas.\n'
    )
    output_files = {
        '00_LEER_PRIMERO.txt': reading,
        'CONTINUIDAD_PI11_FINAL.json': json.dumps(continuity, ensure_ascii=False, indent=2)+'\n',
        'MAPA_RUTAS_Y_ESTADOS_PI11.json': json.dumps(locations, ensure_ascii=False, indent=2)+'\n',
        'OMISIONES_LOCALIZADAS_PI11.json': json.dumps(omissions, ensure_ascii=False, indent=2)+'\n'}
    s = io.StringIO(newline=''); writer = csv.DictWriter(s, fieldnames=list(matrix[0])); writer.writeheader(); writer.writerows(matrix)
    output_files['MATRIZ_ANTES_DESPUES_PI11.csv'] = s.getvalue()
    need(all(sha(Path(ref['path'])) == ref['sha256'] for ref in protected.values()), 'Protected source changed during map construction')
    need(sha(native_path) == native_before and sha(facts_path) == facts_before, 'Final closure/facts changed during map construction')
    return output_files


def schema():
    ref = {'path': 'ABSOLUTE_ACTUAL_FILE', 'sha256': 'ACTUAL_SHA256'}
    return {'schema': 'DEE.PI11.final_native_closure.R01', 'closed_for_documentary_read': False,
            'native_running': True, 'principal_adopted': False,
            'main_experimental': {'life_id': 'ACTUAL_MAIN01', 'N': 67, 'last_observed_tick': 979389, 'last_saved_tick': None},
            'panel': {'owner_proof': ref},
            'post_panel': {'requested': 4, 'completed': 2, 'completed_ticks': [1852, 1564], 'partial_ticks': 714,
                           'unexecuted': 1, 'last_observed_tick': 979389, 'stopped_by_host': True, 'source': ref},
            'autopsy': ref,
            'reproduction': {'status': 'ACTUAL_TERMINAL_RP_STATUS', 'result': ref, 'comparison': None,
                             'recipe': None, 'product_recipe_available': False},
            'local_state_manifests': [{'role': role, **ref, 'scope': 'Actual state preservation scope, including limits'}
                                      for role in ('PRINCIPAL', 'PREFIJO_MAIN', 'ADVERSO_MAIN', 'SEMILLA_RP_R02')],
            'main_arm_role': 'MAIN', 'baseline_arm_role': 'HEREDADO', 'additional_omissions': []}


def main(args):
    if args.schema:
        print(json.dumps(schema(), ensure_ascii=False, indent=2)); return
    need(args.native_closure is not None and args.facts is not None, 'Explicit actual final Native closure and report facts required')
    files = build(args.native_closure, args.facts)
    if args.out_dir:
        dest = Path(args.out_dir).absolute()
        need(not dest.exists() and not dest.is_symlink() and dest.parent.is_dir() and dest.resolve().is_relative_to(P.resolve()), 'New map directory limited to this campaign')
        for node in dest.parents:
            need(not node.is_symlink() and not (getattr(node.lstat(), 'st_file_attributes', 0) & 1024), 'No linked map destination')
        dest.mkdir()
        rows = []
        for name, text in files.items():
            path = dest/name
            with path.open('x', encoding='utf8', newline='') as f:
                f.write(text)
            rows.append(info(path))
        print(json.dumps({'directory': str(dest), 'files': rows, 'new_Native_ticks': 0, 'product_modified': False}, ensure_ascii=False))
    else:
        print(json.dumps({'mode': 'READ_ONLY_PLAN', 'artifacts': list(files), 'writes': 0, 'new_Native_ticks': 0}, ensure_ascii=False))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--schema', action='store_true')
    ap.add_argument('--native-closure', type=Path)
    ap.add_argument('--facts', type=Path)
    ap.add_argument('--out-dir', type=Path)
    main(ap.parse_args())
