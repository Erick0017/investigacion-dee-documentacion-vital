"""Recalculate a bounded historical regulation audit; no native imports/jobs."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def proof(relative, scope):
    path = ROOT / relative
    return {'path': relative, 'sha256': sha(path), 'scope': scope}


def put(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    relative = 'resultados/regulacion_consecuencia_v2_reproduccion_r1'
    summary = load(ROOT / relative / 'SUMMARY.json')
    assert summary['status'] == 'PASS' and len(summary['cases']) == 6
    product = load(ROOT / 'runtime/REFERENCE_IDENTITY_HEREDADA.json')
    source_copies = []
    archive = Path(product['archive'])
    assert sha(archive) == product['archive_sha256']
    members = ('DEE_thinking_4_5_0/source/src/informative.cpp',
               'DEE_thinking_4_5_0/source/python/dee_thinking/experimental_regulation.py')
    with zipfile.ZipFile(archive) as source:
        for member in members:
            payload = source.read(member)
            target = ROOT / 'genealogia/product45/regulation_audit' / Path(member).name
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                assert target.read_bytes() == payload
            else:
                target.write_bytes(payload)
            source_copies.append({'archive_sha256': product['archive_sha256'], 'member': member,
                                 'member_sha256': hashlib.sha256(payload).hexdigest(),
                                 'copy': target.relative_to(ROOT).as_posix()})
    put(ROOT / 'genealogia/product45/regulation_audit/PROVENANCE.json', {'members': source_copies, 'scope': 'Passive byte-exact selected product sources; no new build or operational dependency on an external lab.'})
    cases = []
    for case in summary['cases']:
        path = relative + '/' + case['case_id'] + '/MEASUREMENTS.json'
        data = load(ROOT / path)
        frames = load(ROOT / relative / case['case_id'] / 'OBSERVACIONES.json')
        selected = []
        for frame in frames:
            if frame['tick'] not in (2, 4, 5, 9, 10, 12, 15):
                continue
            prefixes = ('world_contact.',) if frame['tick'] == 2 else ('actual_before_merge.',) if frame['tick'] == 4 else ('comparison.',) if frame['tick'] == 5 else ('policy.',) if frame['tick'] == 9 else ('regulatory_action.',) if frame['tick'] == 10 else ('interception.',) if frame['tick'] == 12 else ('delivery.',)
            selected.append({'tick': frame['tick'], 'records': {key: value for key, value in frame['panel'].items() if key.startswith(prefixes)}})
        cases.append({'id': case['case_id'], 'N': case['N'], 'primary': proof(path, 'Fresh exact historical-reference preparation, not current E1'),
                      'status': case['status'], 'historical_parity': case['historical_parity'],
                      'useful_requested_deliveries': data['requested_deliveries'], 'other_deliveries': data['other_deliveries'],
                      'causal_chain_observed': selected,
                      'postT0_host_input_calls': data['postT0_host_experience_calls'], 'external_RAW_clock_MAIN_edits': data['RAW_clock_edits_on_MAIN'],
                      'diagnostic_forks': [{'condition': branch['condition'], 'requested_deliveries': branch['requested_deliveries'],
                                           'parent_unchanged': branch['parent_unchanged'], 'clock_preserved': branch['intervention']['clock_preserved'],
                                           'original_operation_preserved': branch['original_queue_channels_metadata_preserved'],
                                           'full_final_equal_MAIN_if_sham': branch.get('full_final_equal_MAIN'),
                                           'record': branch['intervention'], 'explicit_native_diagnostic_metadata_added': branch['explicit_native_diagnostic_metadata_added']}
                                          for branch in data['diagnostic_forks']]})
    finite_e1 = ROOT / 'revision/REGULACION_E1_FINITA.json'
    report = {'schema': 'CPC8R.regulation.consequence.antecedent.audit.v1',
              'affirmative_result': 'A current native contact consequence selects a later P/Q interception route under a prepared finite retain/switch transformation. The selected route preserves the corresponding useful delivery at15.',
              'mechanism': ['T0 fixed initial policyP and expectation-source geometry', 'Native zero-load action contacts current medium at2',
                            'Native actual-consequence1 returns at4', 'Physical expectation/actual comparison86 at5',
                            'Prepared R14 normalizer11 yields policy97 at9', 'Native policy plus opportunity17 emits114 onP/Q route10',
                            'Interception12 changes exposure of delivery3, measured at15'],
              'scope': 'State updated by an actual received consequence within one finite prepared episode; not learning an arbitrary update rule or a general utility-trained regulation strategy. This is a rescued historical reference, NOT a current E1 MAIN integration.',
              'native_vs_host': {'postT0_normal_host_calls': 0, 'normal_MAIN_RAW_clock_edits': [],
                                 'medium': 'Equal initial load/inventory; the current physical medium differs in direction. No future reward or desired policy is submitted.',
                                 'prepared': 'InitialP, expectation31, comparator, normalizer11, source/action routes and finite windows.',
                                 'evaluator_only': 'RequestedP/Q labels select the auditor metric after trajectories; prepare() never receives this label.'},
              'source': proof('genealogia/primer_cpc8/regulacion_v2/src/regulacion/native_feedback.py', 'Unchanged original V2 preparation207340…, no second physics or target lookup'),
              'selected_historical_provenance': proof('genealogia/primer_cpc8/regulacion_v2/PROVENANCE.json', '39 byte-exact selected historical members, no nested archive'),
              'reproduction': proof(relative + '/SUMMARY.json', 'Six historical configurations, four new explicit causal forks; RAW/clocks/tick and every recorded field/neighborhood equal'),
              'cases': cases, 'counting': {'completed_reference_preparations': 6, 'new_diagnostic_forks': 4, 'new_independent_holdouts': 0,
                                          'historical_reserved_cases_reproduced': 2, 'current_E1_individuals': 0,
                                          'prior_instrumental_attempt': 'One partial duplicate P21 preparation and one diagnostic continuation reached an overly strict metadata assert. It is preserved and not an independent scientific sample.'},
              'technical_repair': {'prior_source': proof('base_validada/intentos/reproducir_regulacion_consecuencia_v1.py', 'First exact attempt preserved'),
                                   'cause': 'Runtime.diagnostic_fork explicitly adds diagnostic_fork and diagnostic_edit_count metadata. Requiring identical complete metadata was an incorrect audit contract, not a physical difference.',
                                   'correction': 'Require all original metadata, channels and receipts unchanged; allow exactly the two documented diagnostic metadata additions. Physics/configuration/criterion/reserves unchanged.',
                                   'prior_job': proof('jobs/regulation_v2_historical_exact/COMMAND.json', 'Closed failed technical attempt'),
                                   'corrected_job': proof('jobs/regulation_v2_historical_exact_r1/COMMAND.json', 'Closed worker; 25.36s supervisor, peak236318720bytes')},
              'bounded_source_audit': [{'source': proof('genealogia/CPC7/src/action_feedback.py', 'Finite reflected-Y R14 controller; current actual observation is an external fixed sensor code'),
                                        'evidence_type': 'Historical source inspection, not newly executed complete feedback scenario',
                                        'result': 'Prepared comparison/policy controller; learned information carriers; no general utility-strategy learner.'},
                                       {'source': source_copies[0], 'evidence_type': 'Compiled product source plus the82-test regression, not another scientific trajectory',
                                        'result': 'FinitePolicySession has prepared P/Q roles/source contents, one actual consequence observation at boundary2, one fixed retain/switch episode. No arbitrary or repeated utility learning.'},
                                       {'source': source_copies[1], 'evidence_type': 'Product source inspection',
                                        'result': 'CPC5RegulationSession acquires a directional neutral pulse by paired cues; curriculum and interception opportunities are fixed. Explicitly not reinforcement or feedback-selected attention.'}],
              'R0_R1_R2': {'R0': 'Prepared fixed regulation/routing is supported.',
                            'R1': 'Acquired directional state and native consequence-updated policy can modify subsequent physical use under prepared rules.',
                            'R2': 'No validated source in this directed audit demonstrates learning a general strategy by utility without externally specifying its policy-update rule. The affirmative V2 finite state-update result remains accredited.'},
              'distinct_current_E1_R1': proof('revision/REGULACION_E1_FINITA.json', 'Separate fresh E1 finite profile, acquired direction plus four explicitly external maintenance re-exposures; no question/return IUE and not V2') if finite_e1.exists() else None,
              'reproduce_command': 'python -I -B base_validada/reproducir_regulacion_consecuencia.py --out NUEVA_SALIDA',
              'reproduction_needs_old_zip': False,
              'audit_only_source_extraction_dependency': 'This source-audit generator needs the official product archive to reverify/copy two passive sources. Native reference replay only requires the included selected sources/primaries and installed WHL.',
              'source_sha256': sha(Path(__file__))}
    put(ROOT / 'revision/REGULACION_POR_CONSECUENCIA_ANTECEDENTE.json', report)
    text = '''# Una consecuencia nativa cambia una política finita posterior

El aparato V2 conserva una realización útil: una interacción con el medio actual produce un retorno físico, éste modifica la comparación y la ruta regulatoria posterior, y la ruta elegida mantiene una entrega3 en15. P21 conservaP; H21 cambia aQ bajo la misma arquitectura preparada. No hay entradas del host después deT0 ni lectura de un resultado para escribir la acción.

Se reprodujeron seis configuraciones originales en el WHL4.5 oficial. Coinciden RAW completo, clocks y tick inicial/final18, todas las observaciones históricas y sus vecindades. P21/H21 y las dos reservas históricas traducidas entregan una unidad útil cada una; los cortes de retorno D21/D22 dejan cero. Las dimensiones se preservan literalmente: los cuatro casos centrales usanN67 y las dos reservasN131. No se cambióN para unificarlos por apariencia.

Los cuatro forks nuevos localizan la causa: cortar únicamente el portador1 ya formado en4 elimina la entrega en ambas condiciones, mientras el RAW idéntico conserva la entrega y el estado físico final completo. Clocks, cola, canales y padre no cambian. La anotación diagnóstica se guarda aparte; ninguna rama vuelve aMAIN.

## Qué estaba preparado y qué cambió

El medio aporta su dirección actual con el mismo inventario. El contacto2 produce1(±1,+1,0); después de los giros físicos, el retorno4 tiene1(∓1,0,+1). El encuentro5 produce86(0,+1,+1) o86(+1,+1,+1). El normalizador preparado11 cambia esa diferencia a97(+1,0,0) o97(0,+1,0) en9. La oportunidad17 genera114 sobre la rutaP/Q en10; la intercepción12 cambia la conservación del paquete3 en15.

La regla finita conservarP/cambiarQ, la expectativa, los normalizadores, los recursos y las ventanas fueron preparados. Lo conseguido es un **estado de política actualizado por una consecuencia física**, no el aprendizaje de una regla general de utilidad. Ésta es una referencia rescatada y reejecutada; no se añade retrospectivamente alMAIN nuevo ni equivale al regulador de contraflujos de cantidad.

El frenteR1 nuevo deE1 también está identificado por separado en `REGULACION_E1_FINITA.json`: direcciones adquiridas y cuatro reexposiciones externas mantienen su comparación final y una palabra anterior; esas reexposiciones no se convierten en feedback autónomo por llamarlas mantenimiento. Los adversos FBL y su origen exacto7 se conservan en `REGULACION_R0_R1_R2.json`.

## Procedencia y reproducción

`REGULACION_POR_CONSECUENCIA_ANTECEDENTE.json` contiene datos, hashes, fuentes y límites. El código histórico207340… y39 miembros seleccionados se preservan byte-exactos, sin anidar el ZIP anterior. El ensayo original desacertó sólo un assert de auditoría de metadatos diagnósticos: se guardó la versión anterior y se corrigió el contrato sin tocar física, criterio ni reservas.

`python -I -B base_validada/reproducir_regulacion_consecuencia.py --out NUEVA_SALIDA` reproduce las trayectorias con el producto instalado y las fuentes incluidas. No lee resultados para decidir acciones; la igualdad histórica se calcula después de finalizar cada mundo. Son seis preparaciones de referencia y cuatro forks causales, no diez aprendizajes independientes ni un nuevo éxitoR2 general.
'''
    (ROOT / 'revision/REGULACION_POR_CONSECUENCIA_ANTECEDENTE.md').write_text(text, encoding='utf-8')
    print(json.dumps({'reference_cases': 6, 'diagnostic_forks': 4, 'full_historical_parity': all(all(row['historical_parity'].values()) for row in cases),
                      'postT0_host_inputs': sum(row['postT0_host_input_calls'] for row in cases), 'current_E1_preparations': 0}))


if __name__ == '__main__':
    main()
