"""Primary-data-only calculation of native magnitude transfer and CTS retention."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/relaciones'))
from analyze_full_spatial_e1 import functional_windows


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def proof(path, scope):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'scope': scope}


def common_baseline_frames(data, baseline):
    reference = {frame['tick']: frame for frame in baseline['frames']}
    result = []
    for frame in data['frames']:
        tick = frame['tick']
        if tick not in reference:
            continue
        original = reference[tick]
        shared = sorted(set(original) & set(frame) - {'magnitude_transfer'})
        result.append({'tick': tick, 'keys_compared': shared, 'equal': all(original[key] == frame[key] for key in shared),
                       'different_keys': [key for key in shared if original[key] != frame[key]]})
    return result


def main():
    rows = []
    for primary in sorted((ROOT / 'resultados/transferencia_magnitud').glob('*/MEASUREMENTS.json')):
        data = load(primary)
        if data['schema'].endswith('causal.restore.v1'):
            cases = []
            for branch in data['rows']:
                cases.append({'condition': branch['condition'], 'modality': branch['modality'],
                              'full_final_equal_original': branch['full_final_equal_original'],
                              'receipts_equal_original': branch.get('full_receipts_equal_original', branch.get('final_receipts_equal_original')),
                              'parent_unchanged': branch['parent_unchanged'],
                              'clock_preserved': branch.get('clock_preserved', branch.get('intervention', {}).get('clock_preserved')),
                              'original_operation_preserved': branch.get('original_queue_channels_receipts_preserved', branch.get('original_operation_preserved')),
                              'native_reference_and_outputs': [{'tick': frame['tick'],
                                  'reference': frame.get('reference', frame.get('magnitude_transfer', {}).get('reference_site')),
                                  'output': frame.get('output', frame.get('magnitude_transfer', {}).get('center'))}
                                  for frame in branch['frames'] if frame['tick'] in (146, 147, 213, 214, 280, 281)],
                              'old_word616': branch['frames'][-1].get('joint') if branch['frames'][-1]['tick'] == 616 else None})
            rows.append({'case_id': primary.parent.name, 'kind': 'CAUSAL_AND_TECHNICAL', 'primary': proof(primary, 'One saved parent with two diagnostic forks and one technical continuation'),
                         'preparations': 0, 'audit_forks': data['diagnostic_forks'], 'technical_continuations': data['technical_continuations'],
                         'base_file_unchanged': data['base_file_unchanged'], 'branches': cases})
            continue
        integrated = 'magnitude_readings' in data
        readings = data['magnitude_readings'] if integrated else data['readings']
        actual_requests = data['requests'] if integrated else data['source_requests'] + data['recipient_requests']
        b_inputs = [row for row in actual_requests if row['port'].startswith('B.quantity.')]
        b_readers = [row for row in b_inputs if row['port'] == 'B.quantity.reader']
        leaked_reference = [row for row in b_inputs if row['port'].startswith('B.quantity.reference.')]
        assert not leaked_reference and data['recipient_reference_experience_calls'] == 0
        row = {'case_id': primary.parent.name, 'kind': 'FRESH_CTS' if integrated else 'STANDALONE',
               'primary': proof(primary, 'One independent preparation; controls and reserves are different whole histories'),
               'preparations': 1, 'audit_forks': 0, 'technical_continuations': 0,
               'qualified': sum(bool(value['qualified']) for value in readings), 'windows': len(readings),
               'readings': readings, 'B_reference_experience_calls': 0, 'B_actual_input_ports': sorted({value['port'] for value in b_inputs}),
               'reader_admission': dict(Counter(value['receipt']['status'] for value in b_readers)),
               'reader_interpretation': 'One reader applied then two rejectedOccupied; later successful windows use the physically persistent original reader. Not three applied/renewed probes.',
               'all_requests': len(actual_requests), 'receipt_statuses': dict(Counter(value['receipt']['status'] for value in actual_requests)),
               'external_MAIN_RAW_clock_edits': data['host_RAW_clock_edits_on_MAIN'],
               'elapsed_seconds': data['elapsed_seconds'], 'cpu_seconds': data.get('cpu_seconds')}
        if integrated:
            functions = functional_windows(data)
            old = {family: {'valid': sum(value['valid_functional_readout'] for value in functions if value['family'] == family),
                            'windows': sum(value['family'] == family for value in functions)} for family in sorted({value['family'] for value in functions})}
            baseline_id = 'CTS_R1_R31_NEW_HISTORY_CONTACT' if primary.parent.name.startswith('MCTS_R101') else 'CTS_R1_P11_NEW_CONTACT'
            baseline = ROOT / 'resultados/semantica' / baseline_id / 'MEASUREMENTS.json'
            common = common_baseline_frames(data, load(baseline))
            row.update(resources=data['geometry']['resources'], old_functional_summary=old, old_functional_windows=functions,
                       contact_social_query554=[{'receiver': value['receiver'], 'covered': value['covered'], 'physical': value['physical'], 'content': value['content']}
                                                for value in data['contact_social_observations'] if value['phase'] == 'QUERY'],
                       MODE_B428=sum(bool(value['covered']) for value in data['social_captures'] if value['phase'] == 'FORM_QUERY' and value['tick'] == 428),
                       old_word549_616=[{'tick': frame['tick'], 'all_declared_ports': frame['joint']} for frame in data['frames'] if frame['tick'] in (549, 616)],
                       initiative_use89=[{'source_candidate': receiver['source_candidate'], 'physical': receiver['contact']}
                                         for value in data['return_use_observations'] if value['tick'] == 89 for receiver in value['receivers']],
                       baseline=proof(baseline, 'Earlier CTS profile, same relevant history; global physical state is intentionally different because seven supports and a new source are present'),
                       common_old_local_frames=common, common_old_local_frames_all_equal=all(value['equal'] for value in common))
        rows.append(row)
    counts = {'primary_records': len(rows), 'preparations': sum(row['preparations'] for row in rows),
              'diagnostic_forks': sum(row['audit_forks'] for row in rows), 'technical_restored_continuations': sum(row['technical_continuations'] for row in rows),
              'standalone_preparations': sum(row['kind'] == 'STANDALONE' for row in rows), 'fresh_CTS_preparations': sum(row['kind'] == 'FRESH_CTS' for row in rows),
              'reserved_whole_histories': 2, 'new_NS_meanings_claimed': 0}
    report = {'schema': 'CPC8R.native.magnitude.transfer.audit.v1', 'counts': counts, 'rows': rows,
              'affirmative': 'An actually acquired scalar magnitude is transported by native encounters into a second comparator and used on three later actual objects. A fresh CTS profile retains earlier acquired functions while this new recipient reference remains usable.',
              'prepared': 'Source/recipient routes, zero-load formatters, seven recipient supports/interceptors, gradient comparison law, object opportunities, read times and fixed addressing.',
              'acquired': 'Only source receives the cue5 plus actual value. Its native value+5 carrier travels into recipient reference. No B reference teaching input, snapshot transplant, callback copy, learned-answer table or host comparison controls the physical response.',
              'source_continuity': 'The source carrier is rerouted/moved, not cloned. It no longer remains as the same separately accessible source record after transfer. In CTS the primary old quantity reference has its own separately counted original experiences.',
              'unpaired_control': 'Unpaired equal-dose source history leaves31 in B rather than paired36. Some numeric distinctions and two gradient signs may remain. The three-window paired relation, especially equality31+5, is not accredited by this control; do not summarize it as destruction of all memory.',
              'missing_reference': 'Omission/cut may still leave an active directional reader. A negative gradient with an absent reference is not a valid comparison of two retained operands.',
              'communication_coverage': {'measured_standalone_ticks': [3, 66, 67, 68, 69, 70, 71, 72, 73, 77, 78, 79, 80],
                                         'actual': '36Y@3 ->36XY@70 and13,53,40@73 ->36Y at20,60,40@80. Zero-load formatter encounters do not add magnitude.',
                                         'gaps': 'No full-cell genealogy is asserted for every intermediate tick74–76 or for the entire source circulation. Declared routes, actual fields/Moore windows and selective cut73 establish bounded causal transfer, not unique parent assignment by proximity.'},
              'no_general_claim': 'Finite additive acquired carrier and prepared comparator; not arbitrary bodily reinstantiation, autonomous attention, new NSM conceptual mastery, or all-architecture superiority.',
              'commands': {'standalone': 'python -I -B src/transferencia_magnitud/ejecutar.py --case REPRO --value 31 --objects 18 45 31 --out NUEVA_SALIDA',
                           'fresh_CTS': 'python -I -B src/transferencia_magnitud/run_cts.py --case MCTS_P01_SOURCE31 --out NUEVA_SALIDA',
                           'causal_CTS': 'python -I -B src/transferencia_magnitud/cts_causal_restore.py --out NUEVA_SALIDA'},
              'factory': proof(ROOT / 'src/transferencia_magnitud/cts_integrado.py', 'Fresh beforeT0 composition; no edits to frozen CTS/IUE sources'),
              'source_sha256': sha(Path(__file__))}
    put(ROOT / 'revision/TRANSFERENCIA_MAGNITUD.json', report)
    text = '''# Magnitud adquirida, transmisión nativa y uso conservado

La referencia36 adquirida por dos experiencias reales —cue5 y valor31— viaja desdeA al comparadorB sin una entrada que escriba36 enB. En3 es un portadorY; un recurso de carga0 lo redirige aXY en70; otro recurso de carga0 cancelaX en80. La magnitud se conserva en esos encuentros y B dispone de36Y. Tres objetos nuevos23/50/36 producen las respuestas+X/−X/dirección0activa en147/214/281. Se comprobaron los operandos, no sólo el signo de la salida.

Con idéntico receptor y objetos, una historia fuente11 produceB16 y respuestas−/−/−. La reserva17 con objetos12/27/17 conservaB22 y responde+/−/0. Omitir la fuente deja el operando ausente. Desacoplar su cue conserva31, no36: aún hay información física y algunas respuestas coinciden, pero falla la relación emparejada y su igualdad reservada. Esa alternativa no se borra ni se transforma en olvido total.

El corte externo exclusivamente del portador36XY ya formado en73 impideB36; el RAW idéntico conserva el estado físico y los recibos finales. Cargar73 y continuar reproduce exactamente el resultado sin repetir la enseñanza ni programar nuevas entradas. Los cortes son diagnósticos; nunca regresan aMAIN.

## Integración nueva, no cambio retrospectivo de CTS

Un perfil MagnitudeCTS nuevo añade7 soportes y11 interfaces antes deT0 al CTS congelado. La referencia fuente adicional recibe sus propias dos experiencias: no se copia la memoria antigua del E1. En el caso central hay35 materiales,131interfaces y171 solicitudes. El nuevoB conserva36 a través de tres comparaciones, mientras permanecen disponibles el orden2/2, contacto2/2, uso común1/1, palabra anterior4/4, siete lecturas de cantidad antigua, MODE B428, el retorno utilizado89 y el contacto comunicado554/559/563. La palabra antigua responde102 en549 y115 en616 sin reenseñanza.

Cada contrahistoria y reserva tiene su propio mundo nuevo. `TRANSFERENCIA_MAGNITUD.json` conserva los resultados de todos los casos, la igualdad o diferencias de las observaciones locales del CTS de referencia y los forks. No se exige igualdad del RAW global con CTS porque la preparación contiene material y experiencias adicionales. El comparador, la geometría, las ventanas y el regulador CTS siguen siendo preparados; la magnitud y asociaciones pertinentes proceden de las experiencias.

El lectorB se admitió una vez en146; los intentos213/280 fueron rechazados por ocupación. Las tres funciones se expresan mediante el lector que persiste físicamente, no mediante tres sondas renovadas. Una salida activa con operando ausente sigue siendo una salida medida, pero no cuenta como una comparación válida.

## Reproducir y auditar

`python -I -B src/transferencia_magnitud/run_cts.py --case MCTS_P01_SOURCE31 --out NUEVA_SALIDA` construye una vida nueva completa. `cts_causal_restore.py` carga el snapshot íntegro73 y continúa sin reiniciar el currículo. Las cifras y los enteros RAW/clocks originales están enlazados desde el JSON. El manifiesto de fuentes identifica el código exacto de cada ensayo; no se modificaron IUE, CTS, el producto ni el kernel. La cadena medida acredita transferencia y uso de una magnitud en este dominio finito, no conceptos NSM adicionales por denominar sus puertos.
'''
    (ROOT / 'revision/TRANSFERENCIA_MAGNITUD.md').write_text(text, encoding='utf-8')
    print(json.dumps({'counts': counts, 'profiles': [{'id': row['case_id'], 'kind': row['kind'], 'qualified': row.get('qualified'),
                      'windows': row.get('windows'), 'old_frames_equal': row.get('common_old_local_frames_all_equal')} for row in rows]}))


if __name__ == '__main__':
    main()
