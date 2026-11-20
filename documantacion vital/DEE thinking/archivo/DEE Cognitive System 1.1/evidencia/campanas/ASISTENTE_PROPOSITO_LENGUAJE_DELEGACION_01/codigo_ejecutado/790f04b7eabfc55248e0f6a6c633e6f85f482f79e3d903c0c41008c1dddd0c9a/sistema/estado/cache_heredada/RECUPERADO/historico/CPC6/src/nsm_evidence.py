"""Read-only scientific evidence matrix; never imported by the participant."""
import hashlib
import json
from pathlib import Path
import zipfile

from common import ROOT, put, sha


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def catalogue():
    selected = ROOT / 'genealogia/NSM65_CATALOGO_CPC4_VIA_CPC5.json'
    if not selected.exists():
        source = ROOT.parents[1] / 'CPC5_ARQUITECTURAS_COMPUESTAS_Y_APRENDIZAJE_ACUMULATIVO_RESULTADOS.zip'
        expected = 'd31972a47f12bb574a71a14d7ddca3b7a011f320eaba37dcb2ac97abe1f4ce05'
        assert sha(source) == expected
        member = 'CPC5/referencias/NSM65_CATALOGO_CPC4.json'
        with zipfile.ZipFile(source) as z:
            data = z.read(member)
        selected.write_bytes(data)
        put(ROOT / 'genealogia/NSM_SOURCE_MANIFEST.json', {'source_archive': source.name, 'source_archive_sha256': expected, 'member': member, 'file': str(selected.relative_to(ROOT)), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data), 'operation': 'BYTE_EXACT_SELECTIVE_EXTRACTION', 'previous_measurements_preserved_as_historical_statements': True, 'no_new_linguistic_download_or_research_claim': True})
    manifest = load(ROOT / 'genealogia/NSM_SOURCE_MANIFEST.json')
    assert sha(selected) == manifest['sha256']
    return load(selected), manifest


def path_case(relative):
    return str((ROOT / 'resultados' / relative / 'MEASUREMENTS.json').relative_to(ROOT))


def main():
    original, provenance = catalogue()
    assert original['count'] == len(original['entries']) == 65
    assert len({entry['id'] for entry in original['entries']}) == 65
    order_evidence = ['resultados/INTEGRATION_CONTROLS_01/INDEX.json', 'resultados/RETENTION_D01/INDEX.json', 'resultados/RETENTION_D02_ALTERNATE_ACCESS/INDEX.json', 'resultados/RETENTION_SYNTHESIS.json']
    consolidation_evidence = ['resultados/D04_OPEN_LANDING/INDEX.json', 'resultados/CONSOLIDATION_CONTROLS_01/INDEX.json']
    longitudinal_evidence = [path_case('D05_LONGITUDINAL/L01_U0_continuous_Qminus'), path_case('D05_LONGITUDINAL/L02_U0_continuous_Qplus'), path_case('D05_LONGITUDINAL/L03_no_evaluation_load')]
    language_evidence = [path_case('D02_LANGUAGE_DISCOVERY/U0_D04_native_to_name'), path_case('D02_LANGUAGE_DISCOVERY/U0_D05_unpaired_name'), path_case('D02_LANGUAGE_DISCOVERY/U0_D06_no_name'), path_case('D04_OPEN_LANDING/C04_open_Qminus'), path_case('D04_OPEN_LANDING/C05_open_Qplus')]
    profiles = [
        {'id': 'ORDEN_2EVENTOS', 'capability': 'Two physical event orders alter a relative body and native early output; later physical access can re-express part of that history.', 'prepared': 'N67 sensor ports A/B, basal phase260, guide and common reader; the participant is not given a precomputed before/after bit.', 'acquired': 'Different admitted event histories AB/BA; initial delta and emitted direction differ.', 'domain': 'Specific A/B referents, onset0, gap1, first reader2/output5; renewed access69 and cadence-sensitive alternatives.', 'evidence': order_evidence, 'NSM_candidates': ['NSM65.BEFORE', 'NSM65.AFTER'], 'limit': 'A/B-order operational discrimination is not a general abstraction of ANTES/DESPUES across arbitrary identities and intervals; two signs of one relation are not two independently acquired primitives.'},
        {'id': 'CONTACTO_R2', 'capability': 'A native information product reaches and writes a second relative support; its subsequent answer depends on that acquired relation.', 'prepared': 'Second support fromT0 at(44,53,30), open B landing, phase171; no trained state installed.', 'acquired': 'Native contact90 changes delta to+1 for Q- and-1 for Q+; queued physical query94 emits opposite directions97.', 'domain': 'Right-mismatch Q path in N67; support geometry and phase171 are essential.', 'evidence': consolidation_evidence, 'NSM_candidates': ['NSM65.TOUCH'], 'limit': 'Measured native contact/write and causal intervention; the word TOCAR has not been taught as a general relational predicate.'},
        {'id': 'INFORMACION_RECIBIDA', 'capability': 'Different source experiences produce native communicated content, late physical use, and a second acquired relation while original history remains physically available.', 'prepared': 'Finite reflected-Y controller and source routes; each candidate source receives separate exposures. Positive-Q requires extra contributors.', 'acquired': 'Q content is acquired by paired physical exposures, selected/used through v27, retained in R2; not chosen by a Python target table.', 'domain': 'Finite source-policy and communication opportunities, not an arbitrary reusable question-answer network.', 'evidence': consolidation_evidence + longitudinal_evidence, 'NSM_candidates': ['NSM65.KNOW', 'NSM65.SAY'], 'limit': 'Usable received information does not by itself demonstrate metaknowledge SABER or the full semantics of DECIR.'},
        {'id': 'FORMA_01', 'capability': 'A later fixed opaque sign re-expresses received directional content through a real physical query.', 'prepared': 'Equal simultaneous dose on all candidate language lanes; the interface chooses no content-dependent correct branch.', 'acquired': 'Paired sign exposure40 with native received carrier43; query50 produces content-dependent output53. Unpaired/omitted controls lack the decoded taught signature.', 'domain': 'One opaque sign protocol with two directional outcomes and finite prepared routes. The two directions are not counted as two NSM primitives.', 'evidence': language_evidence, 'NSM_candidates': [], 'limit': 'The renderer supplies the literal syntax FORMA_01 and the direction number; no Spanish NSM word, bidirectional language or semantic grammar is thereby established.'}
    ]
    second_form_evidence = [path_case('D07_TWO_FORMS/' + name) for name in ('F01_AB_Qminus_twoforms', 'F02_BA_Qplus_twoforms', 'F03_AB_unpaired_secondform', 'F04_AB_omitted_secondform', 'F05_AB_delayed_secondquery')]
    profiles.append({'id': 'FORMA_02', 'capability': 'A second opaque form is taught only after the original order-history function has been physically re-expressed through the renewed reader.', 'prepared': 'Both candidate dy-sign routes and equal-dose teaching/query inputs exist fromT0; fixed source geometry transports the native69/70 old-history expression to a teaching encounter80.', 'acquired': 'Opaque teaching pulse requested77 meets native history product80; common form-only query87 yields output90: AB(1,-1,-1), BA(1,+1,-1), load23. Unpaired and omitted teaching do not produce the decoded signature.', 'domain': 'Specific renewed order-history expression, N67, reading69/70, teaching80, query90. The delayed67 query in157 did not re-express the same signature.', 'evidence': second_form_evidence, 'NSM_candidates': [], 'limit': 'One additional bounded opaque association, not the general primitives ANTES/DESPUES. Subsequent remote reader trials establish FORM_01 access again162 after FORM_02 teaching80/query90. FORM_02 delayed access157 remains adverse, and a joint new composition of the two sign meanings is not demonstrated.'})
    word_bus_files = [path_case('R03_WORD_BUS_V2/' + name) for name in ('WR01_BA_balanced_Qminus', 'WR02_BA_balanced_Qplus', 'WR03_AB_balanced_Qminus', 'WR04_BA_no_repeat', 'WR05_BA_unpaired_name')]
    word_bus_cases = [load(ROOT / file) for file in word_bus_files]
    profiles[3]['evidence'].extend(word_bus_files + ['resultados/WORD_BUS_CONTROLS_01/INDEX.json'])
    profiles[3]['later_access_after_second_association'] = {'measured': True, 'schedule': 'First FORM_01 query53 -> later FORM_02 association80/query90 -> fresh repeated FORM_01 request117 and native remote supply -> content response162, same MAIN without reset.', 'new_prepared_resource': 'Fixed remote neutral reader ports exist fromT0, both candidate stores stimulated equally. Native delay44 supplies an additional physical query resource; no source/value-selected host routing.', 'reserved_variations': 'BA andAB histories, balanced source codec, event load5, late query13, language query11 and remote reader11. Three positive worlds plus no-repeat and unpaired-name controls.', 'physical_outcomes': 'With common scalar load11, Q- produces native direction(-1,0,-1), Q+ produces(+1,0,-1) in162. No-repeat and unpaired-name controls have no decoded target162; the unpaired first form preserves the second form output90.', 'causal_readout': 'Late carrier cut160 removes target162 while stored R2delta persists; identical sham restores the parent trajectory. Equalizing only A/Bdelta160 does not remove WB02 target162: late access uses richer native expression context, not scalar delta alone.', 'decoder_provenance': 'Discovery V1 used -dx and misread physical polarity. Its errors remain. V2=dx was frozen before the new R03 reserve worlds, not retrospectively relabelled as discovery success.', 'scope': 'Measured reuse of the first operational sign after acquiring the second, using an explicit new reader resource. Not unlimited renewable access, two general NSM primitives, or joint semantic composition.'}
    profiles[4]['evidence'].extend(word_bus_files)
    profiles[4]['separability_contrasts'] = {'old_history_constant': 'WR01 BA/Q- versus WR02 BA/Q+: FORM_01 changes v, FORM_02 remains h=+1.', 'new_content_constant': 'WR01 BA/Q- versus WR03 AB/Q-: FORM_01 remains v=-1, FORM_02 changes h=+1 to-1.', 'scope': 'Two operational contents can vary separately over these three reserve cells. This is not a complete four-cell factorial or a new composed sentence.'}
    late_path = ROOT / 'resultados/LATE_ACCESS_CALCULATIONS.json'
    late_access = load(late_path) if late_path.exists() else None
    if late_access:
        profiles[0]['evidence'].extend(['resultados/LATE_ACCESS_01/INDEX.json', 'resultados/LATE_ACCESS_CALCULATIONS.json'])
        profiles[0]['late_post_R2_use'] = {'domain': 'Two same-age110 parents, original historiesAB/BA and newQ- content already acquired at90 in distinct prepared banks. Third/final bounded access family.', 'mechanism': 'A fixed interface at center-2z is declared inertly at110; new probes110/111 are applied without clearing cells. Their local route/persistence profiles differ by whole history afterR2.', 'observed': 'Both first responses111 share(-1,-1,-1); AB then has a recorded outgoing17 carrier in neighboring(32,24,30) at112, whileBA maintains a local17 field. Both no-query shams remain empty.', 'scope': 'A real new physical interaction afterR2 and preserved R1/R2 deltas, not a new abstract ANTES/NO predicate or proof that one scalar uniquely causes the contrast.'}
    special = {
        'NSM65.BEFORE': ('ORDEN_2EVENTOS', 'A occurred beforeB in this fixed local event grammar; new referents/intervals are a distinct unexecuted abstraction test.'),
        'NSM65.AFTER': ('ORDEN_2EVENTOS', 'The inverse description of the same local A/B order contrast; not an additional independent learned semantic mechanism.'),
        'NSM65.TOUCH': ('CONTACTO_R2', 'Native contact and its acquisition consequence are measured; learning the Spanish relation tocar or generalizing it is not yet tested.'),
        'NSM65.KNOW': ('INFORMACION_RECIBIDA', 'A retained and usable received distinction is measured; representing who knows what remains a separate test.'),
        'NSM65.SAY': ('INFORMACION_RECIBIDA', 'Products transport acquired information; speech acts, interlocutor roles and arbitrary conventions are not equated with this finite carrier.'),
    }
    warnings = {
        'NSM65.I': 'U0/P/Q and module IDs are investigator identities, not an acquired deictic YO relation. No role-switching deictic test.',
        'NSM65.YOU': 'A fixed destination ID is not acquired TU. Current addressee versus distractor and swapped speaker must be physically distinguished.',
        'NSM65.THERE_IS': 'Silence, rejected input, extinct reader and absent material remain separate states. The earlier bounded HAY/R3 association is preserved in the historical catalogue, not newly generalized here.',
        'NSM65.NOT': 'No query silence, timeout or missing record is classified as a learned content-general NO. Earlier bounded historical NO remains a separate claim.',
        'NSM65.THE_SAME': 'Equal delta with distinct reader context is a counterexample to equating one scalar with functional identity; no learned general MISMO predicate.',
        'NSM65.OTHER': 'Two different physical vectors do not by themselves teach the relation OTRO independently of coordinates or direction classes.',
        'NSM65.GOOD': 'A declared functional consequence and a prepared finite policy do not establish a learned context-relative BUENO predicate.',
        'NSM65.BAD': 'A local damaging/unhelpful consequence does not establish general MALO, intention or subjective suffering.',
        'NSM65.FEEL': 'No phenomenal claim follows from a physical state, damage score or current readout.',
        'NSM65.THINK': 'Native memory/comparison are measured mechanisms; the human primitive PENSAR requires its own operational test.',
        'NSM65.CAN': 'Physical availability and admitted access can be instrumented; a content-general learned possibility predicate is not tested.',
        'NSM65.BECAUSE': 'Causal statements here are instrumented fork comparisons, not spontaneous participant explanations.'
    }
    entries = []
    for entry in original['entries']:
        identifier = entry['id']
        candidate, scope = special.get(identifier, (None, 'The catalogue form remains a documented target; no dedicated currentCPC6 acquisition test for this primitive.'))
        linked = next((p for p in profiles if p['id'] == candidate), None)
        entries.append({'id': identifier, 'forma_es': entry['forma_es'], 'variantes_documentadas': entry.get('variantes_documentadas', []), 'glosa_inglesa_id': entry['glosa_inglesa_id'], 'grupo_documental': entry['grupo_documental'], 'fuentes': entry['fuentes'], 'prior_exact_catalogue_file': provenance['file'], 'prior_dimensions_preserved': entry['dimensiones_independientes'], 'current_CPC6': {'catalogued_in_interface_resource': True, 'operation_related_to_candidate_executed': candidate is not None, 'candidate_native_relation': candidate, 'operational_scope': scope, 'NSM_form_physical_signal_taught': False, 'NSM_meaning_association_observed': False, 'NSM_meaning_retention_measured': False, 'NSM_meaning_reserved_use': False, 'NSM_meaning_communication_measured': False, 'NSM_meaning_situation_to_form_emitted': False, 'NSM_meaning_composition_measured': False, 'state': 'EJECUTADO_ANTECEDENTE_OPERACIONAL_NO_PRIMITIVO_GENERAL' if candidate else 'PLANIFICADO_PARA_PRUEBA_SEMANTICA_PROPIA', 'evidence': linked['evidence'] if linked else [], 'preparation_contribution': linked['prepared'] if linked else None, 'acquired_contribution': linked['acquired'] if linked else None, 'remaining_test': warnings.get(identifier, scope)}})
    longitudinal = []
    for file in longitudinal_evidence:
        data = load(ROOT / file)
        chosen_ticks = (5, 23, 53, 69, 70, 90, 94, 97, 161, 162, 170)
        longitudinal.append({'case_id': data['case']['id'], 'same_MAIN': True, 'evidence': file, 'requests_of_interest': [q for q in data['requests'] if q['port'].startswith('renewed.') or q['port'] == 'consolidated.order.read'], 'panels': [{'tick': row['tick'], 'R1_delta': row['body']['delta'], 'R2_delta': row.get('consolidation', {}).get('delta'), 'opaque_sign': row.get('decoded_language'), 'renewed': row.get('renewed')} for row in data['rows'] if row['tick'] in chosen_ticks], 'last_tick': data['rows'][-1]['tick']})
    second_form_panels = []
    for file in second_form_evidence:
        data = load(ROOT / file)
        second_form_panels.append({'case_id': data['case']['id'], 'same_MAIN': True, 'evidence': file, 'first_form53': next(row.get('decoded_language') for row in data['rows'] if row['tick'] == 53), 'second_form_windows': [{'tick': row['tick'], 'decoded': row.get('decoded_order_language'), 'physical': row.get('order_language')} for row in data['rows'] if row['tick'] in (70, 80, 90, 157)], 'requests': [q for q in data['requests'] if q['port'].startswith('order_form.')], 'general_joint_semantic_composition_tested': False})
    reserved_word_panels = []
    for file, data in zip(word_bus_files, word_bus_cases):
        row53 = next(row for row in data['rows'] if row['tick'] == 53)
        row90 = next(row for row in data['rows'] if row['tick'] == 90)
        row162 = next(row for row in data['rows'] if row['tick'] == 162)
        reserved_word_panels.append({'case_id': data['case']['id'], 'evidence': file, 'first_form53': row53.get('decoded_language'), 'second_form90': row90.get('decoded_order_language'), 'first_form_renewed162': row162.get('decoded_word_bus'), 'raw_native_targets162': row162.get('word_bus'), 'same_MAIN': True, 'word_bus_receipts': [q for q in data['requests'] if q['port'].startswith('word_bus.')], 'older_query_ports_receipts117': [q for q in data['requests'] if q['port'].startswith('language.query.') and q['tick'] == 117], 'declared_decoder': data['case'].get('word_bus_decoder'), 'complete_two_form_composition_tested': False})
    payload = {'schema': 'CPC6.NSM65.evidence.v1', 'instrument': 'DEE thinking4.0.0/v27 frozen', 'source_catalogue': provenance, 'linguistic_sources': original['sources'], 'catalogued_forms': 65, 'current_full_NSM_meanings_claimed': 0, 'current_operational_native_profiles': len(profiles), 'current_opaque_sign_protocols_with_association': 2, 'first_opaque_sign_later_use_after_second_association': {'measured': True, 'tick': 162, 'explicit_additional_native_reader_resource': True, 'second_form_unlimited_reuse_claimed': False}, 'counting_rule': 'A directional outcome, output load, ID, prepared channel or inherited catalogue entry is not counted as a new primitive. ANTES/DESPUES share one bounded order mechanism. FORMA_01 and FORMA_02 are two operational sign protocols, each with directional outcomes; not two demonstrated NSM primitives.', 'inherited_claims': {'source_summary_preserved': original['measured_scope_summary'], 'not_reexecuted_as_65_current_semantic_tests': True}, 'native_profiles': profiles, 'entries': entries, 'longitudinal_current_evidence': longitudinal, 'second_form_current_evidence': second_form_panels, 'reserved_word_bus_current_evidence': reserved_word_panels, 'late_post_R2_access_evidence': {'summary': 'resultados/LATE_ACCESS_CALCULATIONS.json', 'measured': bool(late_access), 'controlled_continuations': 6 if late_access else 0}, 'scientific_layers': {'data': 'Exact current measurements and source catalogue fields; RAW/clocks retained as strings in primary records.', 'calculations': 'Counts are catalogue65, related operational profiles5, opaque sign protocols2, and current full primitive claims0. No global intelligence score.', 'provisional_reading': ['Experience creates distinctions that remain usable as physical emissions and acquired secondary relations; later signs can re-express received content and a bounded original order-history function.', 'The current experiment supports a concrete route toward operational semantics, not substitution of a linguistic inventory for an acquired ontology.', 'Old and new native relations occur in the same MAIN in the longitudinal cases. The late110/111 continuations also execute genuinely new original-region interactions afterR2 acquisition90; their access mechanisms, route profiles and causal sufficiency remain distinct.', 'The new reserved remote-reader worlds close first-sign use after second-sign learning: FORM_01 at53 -> FORM_02 at90 -> fresh FORM_01 request117/read162. Two contents vary separately in three reserve cells; an entirely new combined semantic query remains open.', 'Scalar R2delta was causally necessary for early97 signature, whereas its late160 equalization did not change word-bus162 response. Functional memory includes distributed expression context and cannot be reduced to that scalar alone.', 'Association of fixed opaque forms with native directions is not yet an NSM word, general relation abstraction, bidirectional dialogue, role-preserving grammar or knowledge of arbitrary things.']}, 'auditor_only': True, 'participant_imports_this_matrix': False, 'generator_code_sha256': sha(__file__)}
    put(ROOT / 'revision/NSM65_EVIDENCIAS.json', payload)
    print(json.dumps({'catalogued': 65, 'operational_profiles': len(profiles), 'opaque_sign_protocols': 2, 'full_NSM_meanings_claimed': 0, 'longitudinal_cases': len(longitudinal), 'matrix': 'revision/NSM65_EVIDENCIAS.json'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
