"""Read-only evaluation of the preregistered B criteria; never approves adoption.

Missing material evidence produces a false gate. No Native/DEE is imported,
no source life is opened, and no scientific criterion or original is edited.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, importlib.util, json

P = Path(__file__).resolve().parents[1]
H = P / 'codigo'
REAL = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_REAL_01'
ROLES = ('real', 'none', 'yoked', 'reference')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ref(path):
    path = Path(path).resolve(strict=True)
    return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha(path)}


def primary(path):
    p = read(path)
    require(p['status'] == 'completed' and not p.get('error'), 'Unclosed conservation primary')
    r = json.loads(p['result']) if isinstance(p['result'], str) else p['result']
    return r['result']['rows'][0]


def evaluate(args):
    bundle = Path(args.bundle).resolve(strict=True)
    spec = importlib.util.spec_from_file_location('PI08_B_actual_pure_comparison', H / 'RECALCULAR_B_PI08_R01.py')
    parser = importlib.util.module_from_spec(spec); spec.loader.exec_module(parser)
    compared = parser.calculate(bundle, 'INDICE_B_PI08_R01.json')
    index = read(bundle / 'INDICE_B_PI08_R01.json')
    protocol = read(bundle / index['protocol']['file'])
    require(compared['integrity_passed'] and compared['Native_executed'] is False, 'Pure comparison did not pass')
    require(protocol['B_criteria']['B_adoption'].startswith('Only after preservingA'), 'Unexpected preregistered B criterion')
    evidence = [ref(bundle / 'INDICE_B_PI08_R01.json'), ref(bundle / index['protocol']['file'])]
    arms, armrefs = {}, {}
    for role in ROLES:
        a = index['arms'].get(role, {})
        entry = a.get('summary')
        if entry:
            path = bundle / entry['file']; require(sha(path) == entry['sha256'], 'Changed closed-arm proof')
            arms[role] = read(path); armrefs[role] = ref(path); evidence.append(ref(path))
    closed4 = len(arms) == 4 and all(
        a['schema'] == 'DEE.PI08.B.actual_nonperiodic_arm.R01' and a['role'] == role
        and a['status'] == 'CLOSED_18_OPPORTUNITIES' and a['closed'] is True
        and a['error'] is None and a['opportunities_completed'] == 18
        and a['initial_tick'] == protocol['source_A']['T']
        for role, a in arms.items())
    rows = compared['arms']['real']['rows']; stats = compared['denominators']
    revisions = compared['arms']['real']['revisions']
    meaningful = revisions['both_directions_observed_STATE1'] and len(rows) == 18
    comparisons = compared['comparisons']
    causal = closed4 and all(comparisons[r]['calendars_all_equal'] for r in ('none', 'yoked', 'reference'))
    causal = causal and comparisons['yoked']['same_true_false_return_dose'] and comparisons['yoked']['actual_manipulation_mismatches'] > 0
    # The criterion asks for the actual benchmark and measured manipulation,
    # not superiority over every material reference or identical later worlds.
    causal = causal and all(r['returned_failed'] == r['actual_failed'] for r in rows)
    final_tick = rows[-1]['after_tick']

    conservation = None; conservation_ref = None; conserved = False; reopened = False
    if args.conservacion:
        conservation_ref = ref(args.conservacion); conservation = read(args.conservacion)
        evidence.append(conservation_ref)
        require(conservation['schema'] == 'DEE.PI08.B.real_clone_conservation.R01', 'Unexpected conservation schema')
        require(conservation['source_B_REAL'] == REAL and conservation['initial_tick'] == final_tick, 'Unmatched availability prefix')
        conserved = (conservation['closed'] is True and conservation['owner_closed'] is True
            and conservation['criteria_met'] is True and conservation['error'] is None
            and conservation['panel_correct'] == conservation['panel_witnesses'] == 12
            and conservation['C2C_last_offer_product'] is True and conservation['adopted_A_unchanged'] is True
            and conservation['B_episode_never_called'] is True
            and all(k == 'applied' for k in conservation['Native_inputs']['status_counts']))
        for entry in conservation['rows']:
            path = Path(entry['primary']); require(sha(path) == entry['primary_sha256'], 'Conservation primary changed')
            primary(path)
            if entry.get('actual_product'):
                p = entry['actual_product']; data = Path(p['path']).read_bytes()
                require(len(data) == p['bytes'] == 64 and sha(p['path']) == p['sha256'], 'Actual C2C product missing/changed')
                require(int.from_bytes(data[:2], 'little') == entry['actual_numeric_result'], 'Product does not carry actual Native number')
        before, after = conservation['states'].get('B_pre'), conservation['states'].get('B_post')
        reopened = conserved and before is not None and after is not None and before['progress'] == after['progress']
        reopened = reopened and before['progress']['ordinal'] == 30 and not before['progress']['pending'] and not before['progress']['uncertain']

    full_pair = None; pair_ref = None; source_ok = False
    if args.fuente:
        pair = Path(args.fuente).resolve(strict=True); manifest = pair / 'EXPORTACION_SERVICIO.json'
        data = read(manifest); pair_ref = {'path': str(pair), 'manifest_sha256': sha(manifest)}
        require(data['schema'] == 'DEE.persistent_service.paired_export.v1' and data['life_id'] == REAL, 'Wrong whole B source')
        require(data['physical']['N'] == 67 and data['physical']['tick'] == final_tick, 'Source is not the evaluated final B cut')
        require(sha(pair / data['native_snapshot']) == data['snapshot_sha256'], 'Whole-source snapshot changed')
        source_ok = conservation is not None and conservation['source_manifest_sha256'] == sha(manifest)
        full_pair = {'path': str(pair), 'manifest_sha256': sha(manifest), 'physical': data['physical'], 'snapshot_sha256': data['snapshot_sha256']}
        evidence.append(ref(manifest))

    rpA_path = P / 'control/RP_A01_REAL_PI08_R01.json'; rpA = read(rpA_path); evidence.append(ref(rpA_path))
    inherited_replay = (rpA['actual_Native_run'] is True and rpA['local_criteria_met'] is True
        and rpA['physical_coincidence'] is True and rpA['coherent_closed'] is True
        and rpA['recipe'] == 'pi07_r03_uso_adquirido_post4_R03' and rpA['variant'] == 'normal_op4'
        and rpA['Native_receipts']['unique_requested'] == rpA['Native_receipts']['applied'] == 184)
    means = None; means_ref = None; means_ok = False
    if args.medios:
        means_ref = ref(args.medios); means = read(args.medios); evidence.append(means_ref)
        require(means['schema'] == 'DEE.PI08.B.RP.acquisition18_preservation.applied.R01', 'Unexpected stable means registration')
        recipe = Path(means['recipe_path']); capsule = Path(means['code_capsule'])
        require(sha(recipe) == means['recipe_sha256'], 'Registered B recipe changed')
        manifests = [Path(means['capsule_manifest'])] if means.get('capsule_manifest') else []
        manifests += [capsule / n for n in ('SISTEMA_CODIGO.json', 'MANIFIESTO_CODIGO.json', 'MANIFIESTO.json', 'MANIFIESTO_ESTABLE.json')]
        cm = next((p for p in manifests if p.is_file() and sha(p) == means['capsule_manifest_sha256']), None)
        require(cm is not None, 'Registered full B capsule manifest missing/changed')
        require(cm.resolve().is_relative_to(capsule.resolve()), 'Registered B manifest is outside its capsule')
        src = means['source_prefix']; require(sha(Path(src['path']) / 'EXPORTACION_SERVICIO.json') == src['manifest_sha256'] == protocol['source_A']['manifest_sha256'], 'Stable acquisition source changed')
        bp = means['actual_B18_proof']; require(sha(bp['path']) == bp['sha256'] == armrefs.get('real', {}).get('sha256'), 'Registered B18 evidence is another run')
        means_ok = means['applied'] is True and means['Native_executed'] is False and means['B_new_CLI_replay_verified'] is False
        evidence += [ref(recipe), ref(cm)]

    def gate(criterion, value, refs):
        return {'criterion': criterion, 'result': bool(value), 'evidence': [r for r in refs if r]}
    gates = {
      'functional_gain': gate(protocol['B_criteria']['history_revision_supported'], meaningful, [evidence[0], armrefs.get('real')]),
      'conservation': gate('Representative exact twelve-use panel plus actual final C2C32 product in a whole B clone; no old-history reset.', conserved, [conservation_ref]),
      'causal_controls': gate(protocol['B_criteria']['causal_contingency'] + ' Actual material external reference retained even if it matches or exceeds B.', causal, list(armrefs.values())),
      'source_reopening': gate('Full evaluated B source preserved and reopened materially in the paired diagnostic availability clone; adopted A protected.', reopened and source_ok, [conservation_ref, ref(Path(args.fuente) / 'EXPORTACION_SERVICIO.json') if args.fuente else None]),
      'new_function_at_final_cut': gate('Actual final B episode at the source cut remains useful with a valid Native selection, and whole-prefix reopened B progress stays intact; no B episode is attributed after the retention panel.', len(rows) == 18 and rows[-1]['complete_opportunity'] and rows[-1]['Native_selection_valid'] and reopened and source_ok, [armrefs.get('real'), conservation_ref]),
      'decisive_recipe_replay': gate('Complete stable B capsule/recipe and preserved acquisition prefix, plus actual bounded replay of the inherited literal R03 mechanism. This is NOT a new B CLI replay.', means_ok and inherited_replay, [means_ref, ref(rpA_path)])}
    return {'schema': 'DEE.PI08.B.combined_actual_gates.R01', 'utc': datetime.now(timezone.utc).isoformat(),
       'life_id': REAL, 'N': 67, 'T': final_tick, 'Native_executed': False, 'DEE_imported': False,
       'gates': gates, 'all_fixed_evidence_gates_met': all(v['result'] for v in gates.values()),
       'approval': False, 'adoption_performed': False, 'Root_reasoned_decision_required': True,
       'B_actual_closed_arms': armrefs, 'B_conservation_proof': conservation_ref, 'B_source_full_pair': pair_ref,
       'B_new_CLI_replay_verified': False, 'B_CLI_replay_status': 'PREPARED_NOT_EXECUTED',
       'inherited_RP_replay_scope': 'Actual A normal_op4; identical inherited R03 scientific body only. B18 is a new continuation from shared A, not an independent replay.',
       'denominators': stats, 'revisions': revisions, 'comparisons': comparisons,
       'conservation_cut': {'source_tick': final_tick, 'diagnostic_final_tick': conservation['final_tick']} if conservation else None,
       'scope': 'Local repeated nonperiodic history-dependent regulation with fixed sensory, actuator, efference and consequence contracts. Host still schedules the sequence.',
       'gains': 'Both directions of actual same-STATE1 costly-to-useful revision and useful subsequent function are retained across the complete18-opportunity horizon.',
       'losses': 'All adjustment errors and failed Native packet admissions remain in the denominators. FI products and message deliveries are separate outcomes.',
       'uncertainties': 'Final Native delta can equal A initial delta; this broadens tested trajectory, not a new learning law or guaranteed better final policy. Shared-prefix controls are not independent individuals. Dose-matched yoke may retain information.',
       'assistance': 'Prepared public environmental offers, two-bit sensor codec, fixed actuator/transducer, reader windows and six-lap return schedule. External contextual WSLS controls only its own reference clone.',
       'regression_coverage': 'Exact current diagnostic twelve uses plus final C2C use, with explicit regulated FI route; historical legacy-route failures are not erased and no entire corpus is claimed.',
       'evidence': evidence, 'full_source': full_pair}


def main(args):
    value = evaluate(args)
    if args.salida:
        target = Path(args.salida).resolve(); require(target.is_relative_to((P / 'control').resolve()) and not target.exists(), 'New P8/control output only')
        with target.open('x', encoding='utf8') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2); stream.write('\n')
        print(json.dumps({'path': str(target), 'sha256': sha(target), 'all_gates': value['all_fixed_evidence_gates_met'], 'gates': {k:v['result'] for k,v in value['gates'].items()}}))
    else:
        print(json.dumps({'read_only': True, 'all_gates': value['all_fixed_evidence_gates_met'], 'gates': {k:v['result'] for k,v in value['gates'].items()}}))


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--bundle', required=True); cli.add_argument('--conservacion'); cli.add_argument('--fuente'); cli.add_argument('--medios'); cli.add_argument('--salida')
    main(cli.parse_args())
