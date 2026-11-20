"""Pure closed-record selections for audiovisual scenes07/08/09.

No DEE import, clock evolution, reconstruction, geometry or policy. RAW0 reads
remain explicit empty observations. Prepared markers never acquire RAW fields.
"""
from __future__ import annotations
import copy
from functools import lru_cache
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
THINK = HERE.parents[2]
DATA = HERE / 'fuentes/ESCENAS_04_06_09.json'
CONTEXT = HERE / 'fuentes/CONTEXTOS_U0_3D.json'
R08 = THINK / 'archivo/AUDIOVISUAL_R08/infraestructura/FUENTES_MECANISMOS_S06_S11_R08.json'


@lru_cache(None)
def _read(path):
    p = Path(path)
    return json.loads(p.read_text(encoding='utf-8-sig'))


def _ref(path, pointer=''):
    p = Path(path)
    return dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest(), pointer=pointer)


def _observed(obj, pointer=''):
    if isinstance(obj, dict):
        if all(k in obj for k in ('site', 'raw', 'clock')):
            out = copy.deepcopy(obj)
            out['raw'], out['clock'] = str(out['raw']), str(out['clock'])
            out.setdefault('source_pointer', pointer)
            out['observed_empty'] = int(out['raw']) == 0
            return [out]
        return [p for k, v in obj.items() for p in _observed(v, pointer+'/'+str(k))]
    if isinstance(obj, list):
        return [p for i, v in enumerate(obj) for p in _observed(v, pointer+'/'+str(i))]
    return []


def _unique(points):
    seen = {}
    for p in points:
        p = copy.deepcopy(p)
        p['raw'], p['clock'] = str(p['raw']), str(p['clock'])
        p['observed_empty'] = int(p['raw']) == 0
        key = tuple(p['site'])
        if key in seen:
            assert (p['raw'], p['clock']) == (seen[key]['raw'], seen[key]['clock'])
        else:
            seen[key] = p
    return list(seen.values())


def _case(id, tick, points, focus, refs, life, N, es, en, out_es='', out_en='',
          classification='Etapas', markers=(), **extras):
    value = dict(id=id, tick=tick, points=_unique(points), focus_sites=copy.deepcopy(focus),
                 listprep_markers=copy.deepcopy(list(markers)), source_refs=copy.deepcopy(refs),
                 life=life, N=N, label_es=es, label_en=en, output_es=out_es, output_en=out_en,
                 classification=classification,
                 transition='Editorial cut between exact retained states; no interpolated matter route',
                 **extras)
    value['prep_markers'] = copy.deepcopy(value['listprep_markers'])
    value['source_data_hash'] = hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                                        separators=(',', ':')).encode()).hexdigest()
    return value


def cases07():
    """B private observation -> observed encounter -> delayed social use/control."""
    s = _read(DATA)['scenes']['07']['recorded_cases']
    r = _read(R08)['cases']['IC01_SOCIAL']
    full = s['arms']['full']
    life = full['native_life_metadata']['life_id']
    ref = [full['source']]
    source = full['progress']['source']
    markers = [dict(site=q['site'], label_es='Interfaz preparada', label_en='Prepared interface',
                    kind='prepared_interface', port=q['port'], tick=q['tick'], payload=q['payload'])
               for q in full['progress']['plan']['requests'] if 'site' in q and 'generic_record' in q['port']]
    cases = [_case('07_B_source', int(source['tick']), [source], [source['site']], ref,
                   life, 67, 'Información privada de B', 'B private information',
                   classification='Registro', markers=markers,
                   private_input=full['progress']['plan']['value_private_B'],
                   attribution='The private45 input is not the received scalar7 or a motor command.')]
    local = next(f for f in r['passive_sampled_frames'] if f['tick'] == 16563)
    cases.append(_case('07_observed_encounter', 16563, local['observations'], [[20,59,40],[21,59,40]],
                       [r['passive_source'], full['source']], life, 67,
                       'Encuentro registrado', 'Recorded encounter', classification='Registro',
                       markers=markers, original_pointer='/cases/IC01_SOCIAL/passive_sampled_frames/0'))
    names = {'full': ('Mensaje recibido','Message received'),
             'cut': ('Mensaje interrumpido','Message interrupted'),
             'sham': ('Control simulado','Sham control'),
             'no_B': ('Sin nueva información de B','No new B information')}
    for armid, arm in s['arms'].items():
        rowi, row = next((i, row) for i, row in enumerate(arm['first_external_rows']) if row['tick'] == 16619)
        reads = row['social_reads']
        qualified = [v for v in reads if v['qualified']]
        assert len(qualified) <= 1
        output = ('+' if qualified[0]['bank'] > 0 else '-') if qualified else None
        cases.append(_case('07_later_'+armid, row['tick'], [v['native'] for v in reads], [[31,59,29]],
                           [arm['source']], arm['native_life_metadata']['life_id'], 67, *names[armid],
                           out_es=output if output is not None else 'Sin lectura',
                           out_en=output if output is not None else 'No reading',
                           reader_evidence=copy.deepcopy(reads),
                           original_pointer=f'/result/external/rows/{rowi}/social_reads',
                           fixed_external_wiring_separate=dict(native_command=row['native_command'],
                                                               executed_torque=row['executed_torque']),
                           attribution='The displayed symbol is the qualified native social reading, never the externally mixed torque.'))
    return cases


def cases08():
    """Same U0 preparation; comparison location is prepared, T15 RAW is absent."""
    arms = _read(DATA)['scenes']['08']['arms']
    contexts = _read(CONTEXT)
    result = []
    for armid, arm in arms.items():
        life = arm['life']
        prefix = 'Discrepancia' if armid == 'discrepant' else 'Coincidencia'
        prefixen = 'Discrepancy' if armid == 'discrepant' else 'Match'
        for tick in [15, 19, 70, 72]:
            st = next(f for f in arm['stages'] if f['tick'] == tick)
            if armid == 'discrepant':
                context = next(f for f in contexts['frames'] if f['tick'] == tick)
                points = context['all_nonzero_points'] + context['original_field_reads']
            else:
                points = st['points']
            marker, extra, classification = [], {}, 'Etapas'
            out_es = out_en = ''
            if tick == 15:
                marker = [dict(site=[43,14,42], kind='prepared_comparator_location',
                               label_es='Comparador preparado', label_en='Prepared comparator')]
                focus = [[33,25,42],[43,14,42]]
                label_es, label_en = prefix+': comparación', prefixen+': comparison'
                classification = 'Esquema'
                extra['missing_observation'] = 'No RAW/clock of comparator43,14,42 retained atT15. Marker denotes CONFIG geometry, not observed matter.'
            elif tick == 19:
                read = st['reads']['questions']['right.different']
                question = read['state'] > 0 and read['semantic'] == 1 and read['direction'] == [1,0,0]
                out_es, out_en = ('Pregunta','Question') if question else ('Sin pregunta','No question')
                focus = [[43,10,46],[47,10,46]]
                label_es, label_en = prefix+': pregunta material', prefixen+': material question'
                extra['reader_evidence'] = dict(read=read, criterion='SEM1/statepositive/direction[1,0,0] at right.different')
            elif tick == 70:
                focus = [[31,10,46],[35,10,46]]
                label_es, label_en = prefix+': acceso al banco', prefixen+': bank access'
                extra['reader_evidence'] = st['reads']['own_banks']
            else:
                focus = [[33,8,46],[33,12,46]]
                label_es, label_en = prefix+': utilización posterior', prefixen+': later use'
                extra['reader_evidence'] = st['reads']['actions']
                # Full vectors remain evidence; no new generalized action decoder.
                extra['native_vectors'] = {k: v['direction'] for k,v in st['reads']['actions'].items()}
            result.append(_case(f'08_{armid}_{tick}', tick, points, focus,
                                [arm['source'], arm['configuration_source'], _ref(CONTEXT)], life, 67,
                                label_es, label_en, out_es, out_en, classification,
                                markers=marker, current_condition=arm['condition'], **extra))
    return result


def cases09():
    """Native consequence-reference contrast, then an explicitly different service."""
    data = _read(DATA)['scenes']['09']
    results = []
    for armid, arm in data['acquired_reference']['data']['arms'].items():
        for rowidx in [0, 1]:
            row = arm['data']['rows'][rowidx]
            suffix = 'con retorno' if armid == 'full' else 'sin retorno'
            ensuffix = 'with feedback' if armid == 'full' else 'without feedback'
            results.append(_case(f'09_reference_{armid}_{rowidx}', row['tick']-1,
                                _observed(row['native_pre']), [[49,35,35],[50,35,35],[51,35,35]],
                                [arm['source']], arm['life'], arm['N'],
                                'Referencia '+suffix, 'Reference '+ensuffix,
                                classification='Registro', reference=row['native_pre']['reference']['s_reg'],
                                object=row['native_pre']['object']['s_reg'],
                                force_sensor=row['force_sensor'],
                                original_pointer=f'/data/result/rows/{rowidx}/native_pre'))
            sign = '+' if row['native_action'] > 0 else '-' if row['native_action'] < 0 else '0'
            results.append(_case(f'09_action_{armid}_{rowidx}', row['tick'], [row['native_response']],
                                [[50,35,35]], [arm['source']], arm['life'], arm['N'],
                                'Acción '+suffix, 'Action '+ensuffix, sign, sign, 'Registro',
                                reader_evidence=dict(actual_native_response=row['native_response'],
                                                     fixed_transduction_native_action=row['native_action'],
                                                     valid=row['valid']),
                                observed_environment=row['environment'],
                                auditor_only=dict(useful=row['useful_auditor_only'],utility=row['utility_auditor_only']),
                                original_pointer=f'/data/result/rows/{rowidx}',
                                generic_return_requests=[q for q in row['requests'] if 'reference' in q['port']]))
    ext = data['external_service']['data']
    e, life, n = ext['data'], ext['life'], ext['N']
    results.append(_case('09_external_before', int(e['before']['tick']), _observed(e['before']),
                        [[5,15,15],[6,14,14],[7,15,15]], [ext['source']], life, n,
                        'Nuevo ensayo: estado DEE', 'New experiment: DEE state',
                        original_pointer='/result/result/before'))
    frame = next(f for f in e['frames'] if int(f['tick']) == 96562)
    results.append(_case('09_external_native_action', 96562, _observed(frame),
                        [[5,13,13],[6,13,13],[7,13,13]], [ext['source']], life, n,
                        'Salida nativa al actuador', 'Native output to actuator',
                        str(e['formed_native_command']), str(e['formed_native_command']),
                        reader_evidence=e['reader'], original_pointer='/result/result/frames/3',
                        external_execution_separate=e['executed_external_command']))
    results.append(_case('09_external_contact', int(e['consequence']['observed_at_tick']), [], [],
                        [ext['source']], life, n, 'Contacto externo registrado', 'Recorded external contact',
                        classification='Esquema', external_event=e['observed_result'],
                        external_model=e['environment_after']['law'],
                        job_completed=e['job_completed'],
                        original_pointer='/result/result/observed_result',
                        attribution='External fixture observation, not DEE matter or a successful service.'))
    q = next(q for q in e['requests'] if q['id'] == e['consequence']['tactile_request_id'])
    results.append(_case('09_external_actual_feedback', int(q['tick']), [], [q['site']], [ext['source']],
                        life, n, 'Retorno del contacto real', 'Actual contact feedback',
                        classification='Esquema',
                        markers=[dict(site=q['site'], kind='documented_input_interface',
                                      label_es='Entrada táctil',label_en='Tactile input',
                                      tick=q['tick'], port=q['port'])],
                        entry_receipt=q['receipt'], entry_payload=q['payload'],
                        actual_consequence=e['consequence'], original_pointer='/result/result/requests',
                        missing_observation='No RAW at tactile entry96565 is retained; show the admitted interface receipt, not a fabricated particle.'))
    return results
