"""Recalculate finite coupled-regulation evidence without evolving any Runtime."""
from pathlib import Path
from collections import Counter
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'resultados/regulacion_acoplada'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def ref(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'bytes': path.stat().st_size}


def leaves(value, prefix=''):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from leaves(item, prefix + '/' + str(key))
    elif isinstance(value, list):
        for key, item in enumerate(value):
            yield from leaves(item, prefix + '/' + str(key))
    else:
        yield prefix, value


def frame_diff(old, new):
    a, b = dict(leaves(old)), dict(leaves(new))
    return [{'field': key, 'baseline': a.get(key), 'candidate': b.get(key)} for key in sorted(a.keys() | b.keys()) if a.get(key) != b.get(key)]


def summary(path, *, full=False):
    data = read(path)
    frames = {frame['tick']: frame for frame in data['frames']}
    rows = data['regulation_readings'] if full else data['readings']
    configuration = data['configuration']
    medium = configuration['medium']
    expected_reference = configuration.get('regulation_reference', configuration.get('actual_reference')) + 5
    expected_objects = configuration.get('regulation_objects', configuration.get('actual_objects'))
    rows = [{**row, 'directional_task_correct_separate_from_operands': bool(row['output']['active'] and row['output']['direction'] ==
             [(expected_reference > expected_objects[index] + 5) - (expected_reference < expected_objects[index] + 5), 0, 0])} for index, row in enumerate(rows)]
    policy = 'P' if medium == 1 else 'Q'
    native = {tick: frames[tick]['coupled_regulation'] if full else frames[tick] for tick in (4, 5, 9, 10, 11, 15, 53, 54, 77, 78, 79)}
    stages = [
        {'role': 'actual_return', 'tick': 4, 'observation': native[4]['feedback']['actual_before_merge.1']},
        {'role': 'comparison', 'tick': 5, 'observation': native[5]['feedback']['comparison.1']},
        {'role': 'selected_policy', 'tick': 9, 'observation': native[9]['feedback']['policy.' + ('1_0' if policy == 'P' else '1_1')]},
        {'role': 'selected_action', 'tick': 10, 'observation': native[10]['feedback']['regulatory_action.' + ('1_0.P' if policy == 'P' else '1_1.Q')]},
        {'role': 'diverted_action', 'tick': 11, 'observation': native[11]['feedback']['resource_contact.' + ('1_0.P' if policy == 'P' else '1_1.Q')]},
        {'role': 'counterflow_before_interception', 'tick': 77, 'observation': native[77]['counterflows'][policy]['pre_interception_site']},
        {'role': 'native_joint_product', 'tick': 78, 'observation': native[78]['counterflows'][policy]['interception_site']},
        {'role': 'same_site_one_tick_later', 'tick': 79, 'observation': native[79]['counterflows'][policy]['interception_site']},
    ]
    result = {'case_id': data['case_id'], 'primary': ref(path), 'medium': medium, 'policy_from_native_trace': policy,
              'reference': configuration.get('regulation_reference', configuration.get('actual_reference')),
              'objects': configuration.get('regulation_objects', configuration.get('actual_objects')),
              'routing': configuration.get('routing', data['geometry']['coupled_regulation']['routing'] if full else data['geometry']['routing']), 'readings': rows, 'stages': stages,
              'original_V2_delivery15': {key: item for key, item in native[15]['feedback'].items() if key.startswith('delivery.')},
              'receipts': dict(Counter(row['receipt']['status'] for row in data['requests'])),
              'request_count': len(data['requests']), 'final_physical': data['final_physical']}
    if full:
        baseline = read(ROOT / data['base_primary'])
        baseline_frames = {row['tick']: row for row in baseline['frames']}
        differences = []
        for tick in frames.keys() & baseline_frames.keys():
            old = baseline_frames[tick]
            current = {key: value for key, value in frames[tick].items() if key != 'coupled_regulation'}
            delta = frame_diff(old, current)
            if delta:
                differences.append({'tick': tick, 'differences': delta})
        # Already published functional windows are used without refitting a
        # decoder to these candidates. All other physical differences remain.
        panel = {'order': (31, 165), 'common_join': (206,), 'joint': (281, 348, 415, 549, 616),
                 'quantity': (70, 137, 204, 338, 405, 472, 539), 'mode': (428,),
                 'initiative': (73, 76, 86, 89), 'return_use': (89,),
                 'contact_social': (554, 559, 563), 'magnitude_transfer': (146, 147, 213, 214, 280, 281)}
        comparisons = []
        for key, ticks in panel.items():
            for tick in ticks:
                comparisons.append({'field': key, 'tick': tick, 'exact_published_native_fields': frames[tick][key] == baseline_frames[tick][key]})
        for tick, fields in [(76, ('query_site',)), (86, ('effect_site',)), (143, ('renewed_site',)),
                             (147, ('renewed_effect',)), (411, ('hub', 'query_site')), (417, ('effect_site',)),
                             (478, ('renewed_site',)), (484, ('renewed_effect',))]:
            for field in fields:
                comparisons.append({'field': 'contact/*/' + field, 'tick': tick,
                    'exact_published_native_fields': all(frames[tick]['contact'][bank][field] == baseline_frames[tick]['contact'][bank][field] for bank in frames[tick]['contact'])})
        result.update(old_fields_differences=sorted(differences, key=lambda row: row['tick']), old_published_window_panel=comparisons,
                      old_published_window_panel_counts={'same': sum(row['exact_published_native_fields'] for row in comparisons), 'total': len(comparisons)},
                      baseline_primary=ref(ROOT / data['base_primary']), whole_world_equality_to_smaller_baseline_not_required=True)
        baseline_requests = {row['id']: row for row in baseline['requests']}
        result['old_receipt_differences'] = [{'id': row['id'], 'port': row['port'], 'requested_tick': row['tick'],
                                             'baseline': baseline_requests[row['id']]['receipt'], 'candidate': row['receipt']}
                                            for row in data['requests'] if row['id'] in baseline_requests and row['receipt'] != baseline_requests[row['id']]['receipt']]
        result['auxiliary_receipts'] = dict(Counter(row['receipt']['status'] for row in data['requests'] if row['port'].startswith('R.')))
    return result


def main():
    auxiliaries = [summary(path) for path in sorted(DATA.glob('RCA_*/MEASUREMENTS.json')) if path.parent.name != 'RCA_CAUSAL']
    complete = [summary(path, full=True) for path in sorted(DATA.glob('RCAM_*/MEASUREMENTS.json')) if not path.parent.name.endswith('CAUSAL')]
    causal_paths = [DATA / 'RCA_CAUSAL/MEASUREMENTS.json', DATA / 'RCAM_CAUSAL/MEASUREMENTS.json', DATA / 'RCAM_FUNCTIONAL_CAUSAL/MEASUREMENTS.json']
    causal = []
    for path in causal_paths:
        data = read(path)
        rows = []
        for row in data['rows']:
            item = {key: value for key, value in row.items() if key != 'frames' and key not in ('snapshot', 'intervention', 'final_operation')}
            if 'intervention' in row:
                item['intervention'] = {key: value for key, value in row['intervention'].items() if key != 'pre_Moore27'}
            if 'frames' in row:
                item['covered_ticks'] = [frame['tick'] for frame in row['frames']]
            if 'later_reading' in row:
                original = read(DATA / row['case_id'] / 'MEASUREMENTS.json')
                original_last = original.get('regulation_readings', original.get('readings'))[-1]
                cc = original['configuration']
                er = cc.get('regulation_reference', cc.get('actual_reference')) + 5
                eo = cc.get('regulation_objects', cc.get('actual_objects'))[-1] + 5
                output = row['later_reading']['output']
                item['directional_task_correct_separate_from_operands'] = bool(output['active'] and output['direction'] == [(er > eo) - (er < eo), 0, 0])
                item['direction_changed_from_parent137'] = output['direction'] != original_last['output']['direction']
            rows.append(item)
        causal.append({'primary': ref(path), 'diagnostic_forks': data['diagnostic_forks'], 'technical_continuations': data['technical_continuations'],
                       'diagnostic_parent_advances': data.get('diagnostic_parent_advances', 0), 'rows': rows})
    jobs = []
    for path in sorted((ROOT / 'jobs').glob('coupled_regulation*/COMMAND.json')):
        job = read(path)
        jobs.append({'record': ref(path), **{key: job.get(key) for key in ('name', 'status', 'exit_code', 'elapsed_seconds', 'peak_job_memory_bytes', 'owned_worker_waited', 'owned_job_closed', 'pid')}})
    partial = ref(DATA / 'RCAM_D02_PLUS_HIGH/INCREMENTAL.json')
    partial_data = read(DATA / 'RCAM_D02_PLUS_HIGH/INCREMENTAL.json')
    report = {'schema': 'CPC8R.consequence.coupled.regulation.audit.v1', 'status': 'MEASURED_BOUNDED_CAUSAL_EFFECT',
              'selected_MAIN_remains': 'MCTS_P01_SOURCE31, separate35-material profile; no retroactive enrichment of that subject',
              'auxiliary_preparations': auxiliaries, 'new_full_world_histories': complete, 'causal_and_restoration': causal,
              'counts': {'auxiliary_fresh_preparations': 10, 'full_fresh_histories_completed': 9,
                         'full_completed_histories_includes_one_recovered_metadata_failure': 1,
                         'additional_Runtime_construction_aborted_T0_before_exposure': 1,
                         'physical_preparation_attempts_including_aborted': 20, 'diagnostic_forks': 22,
                         'actual_cut_branches': 11, 'identical_RAW_shams': 11,
                         'technical_restores': 4, 'recovery_continuation_same_preparation': 1,
                         'diagnostic_parent_advances4_to9_not_independent': 2,
                         'heldout_auxiliary_histories': 2, 'heldout_full_world_histories': 2,
                         'later_frozen_functional_pair_fresh_worlds_not_original_holdout': 4,
                         'new_NSM_meanings_validated': 0},
              'container_counts': {'terminal_primary_JSON_containers': 22, 'partial_attempt_directories': 2,
                                   'comment': 'One partial preparation is resumed in a separate terminal container; it is counted once, not two lives.'},
              'recovered_attempt': {'incremental': partial, 'last_saved_incremental_tick': partial_data['last_complete_tick'],
                                    'full_checkpoint': ref(DATA / 'RCAM_D02_PLUS_HIGH/T4.deetsnap.gz'),
                                    'continuation': ref(DATA / 'RCAM_D02_CONTINUED_FROM4/MEASUREMENTS.json'),
                                    'individual_id_unchanged': 'RCAM_D02_PLUS_HIGH', 'additional_preparations': 0,
                                    'passive_observation_omission': 'Full optional coupled frame history is kept in primary JSON, not duplicated in bounded session metadata. No RAW/clocks, queue, input receipt or protocol request is omitted from operative persistence.'},
              'technical_attempts': ref(DATA / 'INTENTOS_TECNICOS.json'),
              'frozen_configurations': [ref(ROOT / 'configuraciones/regulacion_acoplada' / name) for name in ('FACTORIAL_CONGELADO.json', 'MCTS_FACTORIAL_CONGELADO.json', 'PAR_FUNCIONAL_CONGELADO.json')],
              'functional_pair_design_status': 'Subsequent focal design, frozen before its own execution; not a confirmatory holdout of the original factorial. Same physical geometry/decoder, new actual secondobject37 ->42, between native reference36 and contaminated43.',
              'source_current': [ref(path) for path in sorted((ROOT / 'src/regulacion_acoplada').glob('*.py'))],
              'clean_reproducer': ref(ROOT / 'tools/reproducir_regulacion_acoplada.py'),
              'native_jobs': jobs, 'job_elapsed_seconds_sum_not_campaign_duration': sum(row['elapsed_seconds'] or 0 for row in jobs),
              'maximum_job_memory_bytes': max(row['peak_job_memory_bytes'] or 0 for row in jobs),
              'all_own_jobs_closed': all(row['owned_job_closed'] and row['owned_worker_waited'] and row['status'] == 'COMPLETED' for row in jobs),
              'coverage': {'N': 67, 'AUX_horizon': 141, 'full_candidate_horizon': 616,
                           'regulated_memory': 'ADDED R.quantity comparator center(2,12,36), with its own acquired reference. This is NOT the original MCTS quantity comparator; no evidence that V2 regulates that original reader.',
                           'AUX_initial_material': 37, 'AUX_interfaces': 7, 'full_initial_material': 72, 'full_interfaces': 138,
                           'regulatory_inputs_after_T0': 0, 'AUX_actual_experience_reader_calls': 8,
                           'full_total_requests': 179, 'initial_material_increase_over_selected_MAIN': 37,
                           'full_request_admission': {'applied': 152, 'rejected_occupied': 27},
                           'changed_old_request': 'ID123 contact.renew.left.changed@477 changes RejectedOccupied toApplied, in all nine full candidates including offpath. This is not attributed specifically to consequence-dependent selection.',
                           'reader_access': 'Reader69 is Applied; repeated136 is RejectedOccupied. Correct137 is later use of a persistent reader, not a second renewed admission.',
                           'interception': 'Selected114 and residue7 yield observed121 with direction0 at78; same register0 at79.',
                           'original_contract_substitution': 'Original V2 selected action is diverted at11 before original threat12; all original delivery registers are0 at15. Literal V2 and CMCTS coexistence remain separate preserved references.',
                           'coupled_world_boundary': 'Finite real effect at137; all three late-regulator cuts in full candidates converge to their own parent full RAW/clocks/tick and receipts616. Terminal equivalence does not erase the recorded causal difference at137.',
                           'scope': 'Measured positive: current native consequence modifies subsequent P/Q selection and thereby which opposed regulator acts, preserving access137 in the matched context. The rule/expectation are prepared. Crossed contexts show that which selection is useful is not learned or revised from later utility137 in this protocol; no general-attention or self-chosen-objective claim.',
                           'uncovered': 'No unique whole-world ancestry before/after the selected observed encounter windows; no third auxiliary object or indefinite renewable-regulator claim.'}}
    (ROOT / 'revision/REGULACION_CONSECUENCIA_ACOPLADA.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# Consecuencia nativa, selección de regulador y acceso posterior', '',
        'Una consecuencia física local modifica una política finita por R14; el producto seleccionado se desvía por seis oportunidades neutras preparadas desdeT0 y neutraliza un residuo antes de que altere una comparación posterior. No hay callback que lea la respuesta para escribir el contraflujo.', '',
        '## Datos y contraste', '',
        '| Mundo | Medio actual | Referencia adquirida | Ruta | Operandos exactos137 | Lectura70/137 |',
        '|---|---:|---:|---|---|---|']
    for row in auxiliaries + complete:
        later = row['readings'][1]
        lines.append('| ' + row['case_id'] + ' | ' + str(row['medium']) + ' | ' + str(row['reference']) + ' | ' + row['routing'] + ' | ' + str(later['reference']['s_reg']) + '/' + str(later['object']['s_reg']) + ' | ' + '/'.join('correcta' if item['qualified'] else 'fuera del criterio' for item in row['readings']) + ' |')
    lines += ['', 'Con referencia31 y primer objeto16, P conserva36/50 en la segunda comparación; Q deja43/50. Con referencia11, Q conserva16/50, mientras P deja16/57. Los shams de material y las rutas desplazadas conservan dosis y muestran que no basta añadir un portador. Las reservas precongeladas usan referencia17 y objetos nuevos: ambos contextos pertinentes conservan22 y los objetos físicos correspondientes.', '',
        'El escalar de salida es7 y la segunda dirección es−X incluso en los primeros controles con operandos dañados. Los10 cortes anteriores (dentro de20 forks:10cortes+10shams) alteraron exactitud de operandos, no la dirección de respuesta137. Por eso se conservan ambos indicadores separados: respuesta direccional y estado adquirido pertinente.', '',
        '### Contraste funcional posterior, congelado antes de ejecutarse', '',
        'Con la misma geometría/cadencia/lector, se presentó referencia31 y un nuevo segundo objeto37: los operandos verdaderos son36 y42. P preserva36/42 y emite−X; Q deja43/42 y emite+X. Esto ocurrió tanto en AUX como en los nuevos mundos completos. Un corte selectivo del contraflujoP114@77 reproduce43/42,+X; el sham conserva36/42,−X. Aquí sí se modifica la respuesta a la misma consulta, además de las magnitudes. Son4 preparaciones focales y2forks adicionales, no reservas confirmatorias del factorial inicial; los resultados adversos previos no fueron sustituidos.', '',
        '## Cadena causal y persistencia', '',
        'Se registraron retorno1@4, comparación86@5, política97@9, acción114@10, desvío11, contraflujo114@77 y producto121 dirección0@78; el registro desaparece79. Las cuatro ablaciones selectivas (retorno4, política9, acción11, contraflujo77) en dos historias AUX producen8 pérdidas de exactitud137; los8 shams conservan estado físico y recibos141 completos. Los clocks de los campos intervenidos, la cola y el padre permanecen preservados.', '',
        'En los dos nuevos mundos completos seleccionados para diagnóstico inicial, cortar el contraflujo77 también cambia causalmente los operandos137; sus shams son exactos. En el contraste funcional posterior cambia además la dirección. A616 los tres cortes de contraflujo de los mundos completos vuelven a coincidir con todo el RAW/clocks/tick y recibos de su respectivo padre, pese a la diferencia intermedia. Las cuatro restauraciones técnicas (dos AUX y dos completas) continúan sin nuevas entradas y conservan estado final y recibos. No se devolvió ningún fork al MAIN.', '',
        '## Candidato compuesto y continuidad separada', '',
        'El candidato añade37 materiales y7 interfaces a la receta MCTS35, siempre antesT0:72 materiales/138 interfaces, un RuntimeN67,179 solicitudes. El regulador protege el NUEVO comparador R.quantity centrado en(2,12,36), con su propia referencia adquirida; no se demostró regulación porV2 del comparador cuantitativo originalMCTS. Es otra genealogía, no una mejora retroactiva del individuo seleccionado MCTS_P01_SOURCE31. Se midieron nueve historias completas, incluidas dos del par focal posterior; una fue recuperada del snapshot4 tras un fallo de metadatos y no cuenta como otra preparación.', '',
        'Las39 firmas publicadas de orden, consultas/contactos pertinentes, composición206/281/348/415/549/616, cantidad principal, MODE428, solicitud/retorno temprano, comunicación554/uso559/entrega563 y transferencia de magnitud son39/39 iguales por candidato en sus campos y ventanas. Existen diferencias físicas intermedias reales en registros residuales de contacto/joint; no se sustituyen por una afirmación de igualdad global. La variante offpath además cambia una lectura pasiva de iniciativa428, fuera de la ventana de uso86/89. El archivo conserva los valores exactos y sus localizadores.', '',
        'La continuidad operativa tampoco se declara idéntica a la preparación menor:179 solicitudes producen152Applied/27Occupied. La solicitud originalID123, contact.renew.left.changed@477, pasa deRejectedOccupied aApplied en los candidatos completos, incluidooffpath. Las ocho solicitudesR.quantity producen7Applied/1Occupied. La mejora de esa admisión antigua se registra como interacción compartida de la preparación, no como efecto demostrado de selección por consecuencia.', '',
        '## Preparación, experiencia y contratos', '',
        'El medio actual se distingue por su dirección física a igual inventario; la referencia cuantitativa procede de entradas reales cue5+valor. El esquema R14, la expectativa, los seis recorridos y las oportunidades son diseño preparado. La consecuencia física recibida modifica la selecciónP/Q posterior y, por ella, qué contraflujo protege el acceso137: selección local dependiente de consecuencia, con evidencia positiva finita. El cruce de contextos delimita que no aprende cuál selección resulta útil ni reajusta la regla por la utilidad posterior137. Esa frontera no elimina la selección causal efectivamente observada. No se añaden significadosNSM acreditados por este aparato.', '',
        'El desvío11 sustituye el contrato de entrega originalV2@15: aquí los cuatro registros de entrega son0, no3. La referencia literalV2 y su coexistenciaCMCTS continúan documentadas por separado. El lector69 es admitido; el segundo intento136 es rechazado por ocupación. El uso137 acredita acceso posterior con lector persistente, no dos lectores renovados.', '',
        '## Intentos y reproducción', '',
        'Se cuentan10 preparacionesAUX y9 historias completas recuperadas/terminadas, más1 Runtime construido y descartadoT0 por un nombre de canal duplicado:20 intentos de preparación física. Este último no recibió currículo ni avanzó. El fallo posterior de metadatos conservó una preparación0→76, snapshots0/4 y código exacto; la continuación4→616 corresponde al mismo individuo. Se repararon sólo nombres de canal y almacenamiento de una traza opcional, nunca física. Los frames completos permanecen en JSON; no se duplican en los metadatos operativos acotados.', '',
        'El JSON reconcilia22 forks(11cortes/11shams),4 restauraciones,1 continuación de recuperación y2 avances4→9 de padres instrumentales; no son réplicas independientes. Hay22 contenedores primarios finales y2 directorios de intentos. Los procesos propios terminaron y cerraron sus jobs. Fuentes exactas, configuraciones previas, estados indispensables y comandos están enlazados conSHA-256.', '',
        'Desde una extracción independiente, el worker `tools/reproducir_regulacion_acoplada.py` acepta `--condition plus` o `minus`, `--reference` al primario correspondiente y `--out` externo nuevo. La referencia se lee sólo después de construir/evolucionar el mundo y restaurar77→616. No usa un resultado guardado como respuesta. El trabajador de validación limpia registrará su ejecución por separado.']
    (ROOT / 'revision/REGULACION_CONSECUENCIA_ACOPLADA.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'auxiliary': len(auxiliaries), 'full_histories': len(complete), 'counts': report['counts'], 'own_jobs_closed': report['all_own_jobs_closed']}))


if __name__ == '__main__':
    main()
