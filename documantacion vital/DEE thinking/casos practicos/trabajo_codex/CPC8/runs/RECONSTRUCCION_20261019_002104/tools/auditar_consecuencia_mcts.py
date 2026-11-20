"""Recalculate coexistence, finite policy and late causal controls from fields."""
from pathlib import Path
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/relaciones'))
from analyze_full_spatial_e1 import functional_windows


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def proof(path, scope):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'scope': scope}


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def deliveries(panel, geometry, medium):
    records = []
    requested = 'P' if medium == 1 else 'Q'
    for regulator in geometry['regulators']:
        observed = panel['delivery.' + regulator['id']]
        valid = bool(observed['active'] and observed['semantic'] != 5 and observed['s_reg'] == 3 and observed['direction'] == [1, 0, 0])
        records.append({'id': regulator['id'], 'source': regulator['source'], 'physical': observed, 'useful_delivery3': valid})
    return {'requested_route_auditor_only': requested, 'requested_count': sum(value['useful_delivery3'] and value['source'] == requested for value in records),
            'other_count': sum(value['useful_delivery3'] and value['source'] != requested for value in records), 'records': records}


def previous_fields(data, baseline):
    reference = {frame['tick']: frame for frame in baseline['frames']}
    rows = []
    for frame in data['frames']:
        if frame['tick'] not in reference:
            continue
        original = reference[frame['tick']]
        keys = sorted(set(original) & set(frame) - {'consequence_policy'})
        rows.append({'tick': frame['tick'], 'keys_compared': keys, 'different_keys': [key for key in keys if original[key] != frame[key]],
                     'different_values': {key: {'baseline': original[key], 'combined': frame[key]} for key in keys if original[key] != frame[key]},
                     'equal': all(original[key] == frame[key] for key in keys)})
    return rows


def functional_summary(data):
    rows = functional_windows(data)
    return {'families': {family: {'valid': sum(row['valid_functional_readout'] for row in rows if row['family'] == family),
                                 'windows': sum(row['family'] == family for row in rows)} for family in sorted({row['family'] for row in rows})}, 'rows': rows}


def main():
    baseline_path = ROOT / 'resultados/transferencia_magnitud/MCTS_P01_SOURCE31/MEASUREMENTS.json'
    baseline = load(baseline_path)
    cfg = load(ROOT / 'configuraciones/regulacion_consecuencia/MCTS_V2_CONGELADO.json')
    rows = []
    directory = ROOT / 'resultados/regulacion_consecuencia_integrada'
    for case in cfg['cases']:
        primary = directory / case['id'] / 'MEASUREMENTS.json'
        data = load(primary)
        assert data['status'] == 'MEASURED' and data['last_complete_tick'] == 616
        geometry = data['geometry']['consequence_regulation']
        fields = data['consequence_policy_observations']
        bytick = {frame['tick']: frame['panel'] for frame in fields}
        native_delivery = deliveries(bytick[15], geometry, case['consequence_medium'])
        source_case = 'REG_V2_P21' if case['consequence_medium'] == 1 else 'REG_V2_H21'
        historical = load(ROOT / 'genealogia/primer_cpc8/regulacion_v2/resultados/regulacion' / source_case / 'OBSERVACIONES.json')
        parity = []
        for historical_frame in historical:
            tick = historical_frame['tick']
            if tick not in bytick:
                continue
            equal = []
            for name, old in historical_frame['panel'].items():
                actual = bytick[tick][name]
                equal.append({'port': name, 'exact_fields_equal_except_translated_site': all(actual[key] == old[key] for key in ('tick', 'raw', 'clock', 'state', 's_reg', 'direction', 'semantic'))})
            parity.append({'tick': tick, 'ports': equal, 'all_equal': all(value['exact_fields_equal_except_translated_site'] for value in equal)})
        old_fields = previous_fields(data, baseline)
        social = [{'receiver': value['receiver'], 'covered': value['covered'], 'physical': value['physical']} for value in data['contact_social_observations'] if value['phase'] == 'QUERY']
        rows.append({'case_id': case['id'], 'primary': proof(primary, 'One fresh combined world fromT0, no cloned/trained preparation'),
                     'medium': case['consequence_medium'], 'native_deliveries15': native_delivery,
                     'translated_historical_port_parity': parity, 'all_historical_component_ports_equal': all(value['all_equal'] for value in parity),
                     'old_MCTS_fields': old_fields, 'all_old_MCTS_local_fields_equal': all(value['equal'] for value in old_fields),
                     'MCTS_functional_summary': functional_summary(data), 'new_magnitude_readings': data['magnitude_readings'],
                     'contact_social554': social, 'word616': data['frames'][-1]['joint'], 'resources': data['geometry']['resources'],
                     'all_global_requests': len(data['requests']), 'V2_new_runtime_interfaces': 0, 'V2_postT0_host_inputs': 0,
                     'MAIN_RAW_clock_edits': data['host_RAW_clock_edits_on_MAIN'], 'final_physical': data['final_physical']})
    causal_path = directory / 'CMCTS_CAUSAL/MEASUREMENTS.json'
    causal = load(causal_path)
    causal_rows = []
    for branch in causal['rows']:
        parent = next(row for row in rows if row['case_id'] == branch['case_id'])
        primary = load(directory / branch['case_id'] / 'MEASUREMENTS.json')
        panel = next(frame['consequence_policy'] for frame in branch['frames'] if frame['tick'] == 15)
        old = previous_fields(branch, baseline)
        causal_rows.append({'parent_case_id': branch['case_id'], 'condition': branch['condition'],
                            'delivery15': deliveries(panel, primary['geometry']['consequence_regulation'], parent['medium']),
                            'intervention': branch['intervention'], 'parent_unchanged': branch['parent_unchanged'],
                            'clock_preserved': branch['intervention']['clock_preserved'], 'operation_preserved': branch['original_operation_preserved'],
                            'base_unchanged': branch['base_file_unchanged'], 'full_final_equal_original': branch['full_final_equal_original'],
                            'receipts_equal_original': branch['receipts_equal_original'], 'old_MCTS_local_fields_all_equal': all(value['equal'] for value in old),
                            'old_MCTS_fields': old, 'final_word616': branch['frames'][-1]['joint']})
    report = {'schema': 'CPC8R.consequenceMagnitudeCTS.audit.v1',
              'capacity_measured': 'Current native contact consequence selects a later finite prepared P/Q interception policy while the previous MCTS local functions coexist in the same freshRuntime through616.',
              'scope': 'Physical coexistence, not proof that the prepared V2 policy is learned, optimized by utility, or causally used by the other MCTS decision domains. The public selected MCTS application remains unchanged; this is a separate auxiliary candidate profile.',
              'counting': {'primary_containers': 3, 'new_preparations': 2, 'diagnostic_forks': 4, 'total_trajectories': 6,
                           'independent_reserved_worlds': 0, 'historical_opposite_medium_contrast': 1},
              'single_geometry': proof(ROOT / 'configuraciones/regulacion_consecuencia/MCTS_V2_CONGELADO.json', 'Translation fixed before both histories; no geometry adjustment after outcome'),
              'inert_preflight_and_diff': proof(ROOT / 'configuraciones/regulacion_consecuencia/PREFLIGHT_Y_PROCEDENCIA.json', 'Zero Runtime allocations;59materialssource35+24;131interfaces; no initial material overlap; originalclocks/directions/payloads retained'),
              'technical_preflight_attempts': proof(ROOT / 'configuraciones/regulacion_consecuencia/INTENTOS_TECNICOS.json', 'Console/metadata preflight corrections before Runtime construction; no scientific geometry/criterion change'),
              'source': proof(ROOT / 'src/regulacion_consecuencia/mcts.py', 'One sole OrganizationalWorld.create after merging inert recipes, no auxiliaryRuntime or result lookup'),
              'baseline': proof(baseline_path, 'Original frozen fresh MCTS profile; not modified or relabelled as containing V2'),
              'normal_histories': rows, 'causal_primary': proof(causal_path, 'Four fullstate fork continuations4→616, originalinputqueue unchanged'),
              'causal_forks': causal_rows,
              'prepared': 'InitialP clock11, expectation31, R14 normalizers, comparison and P/Qroutes, supplies, all finitewindows. V2 has no external channel/input afterT0.',
              'native_state_update': 'Equal-inventory current medium± changes contact2, actualreturn4, comparison5, policy9, selectedinterception10/12 and delivery15. No host outcome read selects an input.',
              'interaction_limits': 'No initial overlap is not itself a noninterference proof. Exact old local fields are compared at shared windows; global RAW differs because24additionalphysicalrecords remain in the universe. No deletion, clock reset or favorable snapshot restoration is used.',
              'observed_nonfunctional_interference': {'case': 'CMCTS_P01_CURRENT_PLUS', 'tick': 73,
                  'site': [16, 12, 18], 'prepared_old_port': 'joint.minus.changed.use_site',
                  'baseline': {'raw': '0', 'state': 0, 's_reg': 0, 'direction': [0, 0, 0], 'clock': '73'},
                  'combined': {'raw': '2238007587071066113', 'state': 1, 's_reg': 11, 'direction': [-1, 0, -1], 'clock': '73'},
                  'functional_result': 'This is not a frozen joint-use readwindow; later commonfunction, jointwords and all original sampled functional windows remain valid. It disproves strict local noninterference throughout time, not measured retention.',
                  'source_candidate_not_certified_genealogy': 'The unused prepared V2 normalizer11 atpolicy.1_1 site13,12,15 in9 has direction(-1,0,-1); a64tick free continuation lands exactly16,12,18 at73. Observed coordinates/load/direction fit, but all intermediate encounters9→73 were not reconstructed, so no unique ancestry is asserted.',
                  'causal_fork_coverage': 'Fork comparison frames do not include73. Their all_old_local_fields_equal flags apply only to their listed shared windows, not to every tick or the normal positive73observation.'},
              'reproduce_command': 'python -I -B src/regulacion_consecuencia/run.py --case CMCTS_P01_CURRENT_PLUS --out NUEVA_SALIDA',
              'no_full_R2_or_NSM_claim': True, 'source_sha256': sha(Path(__file__))}
    put(ROOT / 'revision/REGULACION_POR_CONSECUENCIA_EN_MCTS.json', report)
    text = '''# Consecuencia nativa y conservación del repertorio en una preparación compuesta

Un candidato nuevo incorpora el aparato finitoV2 en el mismoRuntime queMCTS desdeT0. Sus dos medios actuales, de igual carga e inventario, modifican el retorno físico y la rutaP/Q posterior. El contacto2 produce el retorno4; la comparación5 cambia la política9, que encuentra oportunidades de acción10 y modifica la intercepción12 y la entrega3 en15. No se introduce ninguna entrada del host en este componente después deT0.

La adaptación conserva el constructor físico original: cambia sólo el nombre de su fábrica y devuelve una receta inerte en vez de crear otroRuntime. El diff exacto se guarda en la prevalidación. Se utiliza una única traslación(-25,-25,-20), fijada antes de las pruebas. Los24 registros originales mantienen carga, dirección y clocks, incluida la política inicial preparada de clock11. El mundo conjunto tiene59 materiales y131interfaces; no se suponía aislamiento por el mero hecho de no solapar materia inicial.

La coexistencia conserva el panel funcional: orden2/2, contacto2/2, uso común1/1, palabras4/4, cantidad antigua7/7, nueva magnitud3/3, contacto comunicado554 y palabra616115 en ambas historias. No implica ausencia completa de interacción: el positivo contiene en73 un portador11(−1,0,−1) en el puerto antiguo de uso `minus.changed`(16,12,18), vacío enMCTS de referencia. Esa no era una ventana de uso evaluada y las funciones posteriores se conservaron. Coincide con la continuación balística del normalizador11 no consumido en9, pero no se reconstruye por esa coincidencia una genealogía única9→73. Los forks no muestrearon73: sus igualdades locales se refieren sólo a sus propias ventanas registradas.

Los datos incluyen dos vidas completas0→616 y cuatro forks causales4→616. Cada corte elimina únicamente el retorno1 ya formado; cada sham escribe su RAW idéntico sin cambiar clock ni cola. Los estados del padre quedan intactos y ninguna rama diagnóstica vuelve aMAIN. Las fichas JSON conservan la entrega15, el panel anterior de MCTS, los campos históricos V2 traducidos y los estados completos finales.

El significado del resultado sigue siendo finito: una consecuencia física modifica el **estado** de una política bajo una reglaR14 preparada. No se aprendió esa regla ni se acreditó una estrategia general por utilidad. Tampoco se afirma que esta decisiónV2 alimente las otras tareas MCTS: se estudia su coexistencia y la conservación de funciones en un mismo mundo. Es otro candidato nuevo, no una modificación retrospectiva del individuo MCTS elegido para la aplicación.

`REGULACION_POR_CONSECUENCIA_EN_MCTS.json` contiene los valores y controles completos. `python -I -B src/regulacion_consecuencia/run.py --case CMCTS_P01_CURRENT_PLUS --out NUEVA_SALIDA` genera una trayectoria nueva; no reproduce respuestas guardadas. El catálogo NSM y la aplicación anterior no se modificaron por añadir este componente preparado.
'''
    (ROOT / 'revision/REGULACION_POR_CONSECUENCIA_EN_MCTS.md').write_text(text, encoding='utf-8')
    print(json.dumps({'normal': [{'id': row['case_id'], 'delivery15': row['native_deliveries15']['requested_count'],
                      'V2_port_parity': row['all_historical_component_ports_equal'], 'old_MCTS_local_fields_equal': row['all_old_MCTS_local_fields_equal'],
                      'functions': row['MCTS_functional_summary']['families']} for row in rows],
                      'forks': [{'id': row['parent_case_id'], 'condition': row['condition'], 'delivery15': row['delivery15']['requested_count'],
                      'full_final_equal': row['full_final_equal_original'], 'old_MCTS_fields_equal': row['old_MCTS_local_fields_all_equal']} for row in causal_rows]}))


if __name__ == '__main__':
    main()
