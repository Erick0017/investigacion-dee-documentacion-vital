"""Read-only data selections for scenes03/05/10/11/12/13. Python stdlib only.

No coordinates, RAW, clocks or trajectories are synthesized. prep_markers are
documented opportunities and MUST be drawn separately from observed matter.
Labels identify cuts/controls; they are not a replacement narration.
"""
from pathlib import Path
from functools import lru_cache
from copy import deepcopy
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / 'fuentes'
SOURCE_NAME = 'ESCENAS_03_05_10_13.json'
FIELD_NAME = 'ESTADOS_GUARDADOS_S03_S13.json.gz'
CONTEXT_NAME = 'CONTEXTOS_U0_3D.json'


@lru_cache(None)
def _load(name):
    path = SOURCES / name
    b = path.read_bytes()
    expected = {SOURCE_NAME:'417b71efcf7ac604dfdbbac035e40b6b10ef29bbee0ebf82d24b1866bdd9b24d',
                FIELD_NAME:'81e2c2cc4c8e4b52f0bdb20823244a4b083c6878de87c3e6bbc6f3f0f9180cc4'}
    digest = hashlib.sha256(b).hexdigest()
    if name in expected and digest != expected[name]:
        raise ValueError('Frozen source hash changed: ' + str(path))
    return json.loads(gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b), {
        'path':str(path),'sha256':digest,'bytes':len(b)}


def _scene(number):
    return _load(SOURCE_NAME)[0]['scenes']['S'+number]


def _ref(name, pointer):
    return {**_load(name)[1], 'pointer':pointer}


def _points(values):
    result = []
    seen = {}
    for point in values:
        p = deepcopy(point)
        if 'raw' not in p and 'rawstr' not in p:
            raise ValueError('Observed point without RAW')
        p['rawstr'] = str(p.get('rawstr',p.get('raw')))
        p['raw'] = p['rawstr']
        if 'clock' in p or 'clockstr' in p:
            p['clockstr'] = str(p.get('clockstr',p.get('clock')))
            p['clock'] = p['clockstr']
        else:
            raise ValueError('Observed point without its recorded clock')
        key = tuple(p['site'])
        if key in seen:
            previous = seen[key]
            if (p['rawstr'],p['clockstr']) != (previous['rawstr'],previous['clockstr']):
                raise ValueError('Conflicting observations at the same cut/site')
            continue
        seen[key] = p
        result.append(p)
    return result


def _sites(values):
    return [list(x) for x in dict.fromkeys(tuple(p) for p in values)]


def _crop(points, bounds):
    lo, hi = bounds
    return [p for p in points if all(lo[j] <= p['site'][j] <= hi[j] for j in range(3))]


def _entry(identity, tick, points, focus, refs, life, n, es, en,
           markers=(), output=None, evidence=None, classification='Etapas', **extra):
    if output is not None and evidence is None:
        raise ValueError('An output requires its own retained qualified reader')
    p = _points(points)
    if any(not all(0 <= x < n for x in q['site']) for q in p):
        raise ValueError('Coordinate outside its own world')
    result = {'id':identity, 'tick':int(tick), 'points':p,
              'focus_sites':_sites(focus), 'prep_markers':_sites(markers),
              'source_refs':deepcopy(refs), 'life':life, 'N':n,
              'label_es':es, 'label_en':en, 'output_es':'', 'output_en':'',
              'classification':classification,
              'prep_markers_are_observed_RAW':False,
              'no_interpolated_material_trajectory':True}
    if output is not None:
        sign = '+' if output == 1 else '−' if output == -1 else str(output)
        result['output_es'] = 'Salida ' + sign
        result['output_en'] = 'Output ' + sign
        result['reader_evidence'] = deepcopy(evidence)
    result.update(deepcopy(extra))
    return result


def _panel(number, card_index, panel_index, identity, es, en, life=None):
    s = _scene(number)
    card = s.get('stages',s.get('transfer_stages'))[card_index]
    panel = card['panels'][panel_index]
    evidence = panel.get('reader_evidence')
    sign = None
    if evidence:
        if evidence.get('qualified') and 'record' in evidence:
            sign = evidence['record'].get('value')
        elif 'command' in evidence:
            sign = evidence.get('command')
        elif 'choice' in evidence:
            sign = evidence.get('choice')
        elif 'qualified_choice' in evidence:
            sign = evidence.get('qualified_choice')
    source = panel.get('source',{})
    root_key = 'stages' if 'stages' in s else 'transfer_stages'
    refs = [_ref(SOURCE_NAME,f'/scenes/S{number}/{root_key}/{card_index}/panels/{panel_index}')]
    if source:
        refs.append(source)
    return _entry(identity,panel['tick'],panel['points'],
        panel.get('reader_sites') or panel.get('direction_sites') or [q['site'] for q in panel['points']],
        refs,life or source.get('life') or s.get('life') or s.get('life_or_session','unknown'),
        panel['N'],es,en,
        markers=panel.get('input_sites',[])+panel.get('teaching_sites',[]),
        output=sign,evidence=evidence, reader_sites=panel.get('reader_sites',[]),
        direction_sites=panel.get('direction_sites',[]),
        observed_point_scope='Retained exact local observations; not a full field unless stated.',
        reader_source_tick=panel.get('reader_source_tick',panel['tick']))


def _context(tick, region=None, bounds=None):
    data = _load(CONTEXT_NAME)[0]
    i, frame = next((i,f) for i,f in enumerate(data['frames']) if f['tick']==tick)
    if region:
        r = frame['regions'][region]
        points = r['nonzero_points'] + r['explicitly_observed_zero_points']
    else:
        points = frame['all_nonzero_points'] + frame['original_field_reads']
    if bounds:
        points = _crop(points,bounds)
    return _points(points), [_ref(CONTEXT_NAME,f'/frames/{i}'),
                             {**data['sources'][0],'pointer':frame['source_pointer']}], frame


def cases03():
    s = _scene('03')
    saved = _load(FIELD_NAME)[0]['snapshots']['S03_MINUS_saved720458']
    refs = [_ref(FIELD_NAME,'/snapshots/S03_MINUS_saved720458'),s['source']]
    focus = [[37,33,32],[37,33,34]]
    bounds = [[27,27,30],[39,39,36]]
    out = [_entry('03_saved_global',720458,saved['points'],
                  [q['site'] for q in saved['occupied_points']],refs,s['life'],67,
                  'Estado guardado','Saved state',classification='Registro',
                  complete_nonzero_field=True,summary=saved['summary'])]
    local = _points(_crop(saved['points'],bounds)+saved['later_MA_reader_sites_observed_at_saved_cut'])
    for state,label in [('saved','Estado guardado'),('loaded','Estado reabierto')]:
        out.append(_entry('03_'+state+'_memory_roi',720458,local,focus,refs,s['life'],67,
            label,'Saved state' if state=='saved' else 'Reopened state',bounds=bounds,
            same_saved_loaded_encoded_snapshot=True,
            identity_evidence=s['identity_evidence']))
    result = s['native_result_exact_for_reader_context']
    row = result['rows'][0]
    word = row['word']
    reader = word['reader']
    out.append(_entry('03_postreopen_lexical',word['read_tick'],reader['panel'],
        [q['site'] for q in reader['candidates']],
        [*refs,{'path':s['source']['path'],'sha256':s['source']['sha256'],
                'pointer':'/cycles/1/terminal_request/result','decode':'JSON',
                'decoded_pointer':'/result/rows/0/word/reader'}],s['life'],67,
        'Consulta tras reabrir','Query after reopening',
        markers=[q['site'] for q in word['requests']],
        output=reader['formed_native_command'],evidence=reader,
        input_receipts=word['requests']))
    stage = s['stages'][2]
    memory_reader = row['interaction']['reader']
    out.append(_entry('03_postreopen_memory',stage['tick'],
        [q['point'] for q in stage['points_with_exact_local_pointers']],focus,
        [q['source'] for q in stage['points_with_exact_local_pointers']],s['life'],67,
        'Uso tras reabrir','Use after reopening',
        output=stage['qualified_summary']['memory_sign'],evidence=memory_reader,
        task_end_tick=s['coverage']['task_end_tick']))
    return out


def cases05():
    s = _scene('05')
    bounds = [[26,26,2],[34,34,12]]
    out = []
    for index,tick,es,en in [(0,338,'Antes de revisión','Before revision'),
                            (1,402,'Entrada de revisión','Revision input'),
                            (2,405,'Experiencia de revisión','Revision experience'),
                            (3,472,'Consulta posterior','Later query')]:
        p = _panel('05',index,0,'05_L03_'+str(tick),es,en)
        points,refs,frame = _context(tick,bounds=bounds)
        p['points'] = _points(points+p['points'])
        p['source_refs'] += refs
        p['bounds'] = bounds
        p['complete_buffer_cut'] = frame['complete_buffers']
        p['observed_point_scope'] = frame['coverage']
        out.append(p)
    source = s['source']
    for witness in s['controls']['witnesses'][:3]:
        record = witness['after']
        assert record['covered'] and int(record['tick'])==472 and witness['same_qualified_value']
        out.append(_entry('05_witness_'+witness['form'],472,[record['physical']],
            [record['physical']['site']],
            [source,_ref(SOURCE_NAME,'/scenes/S05/controls/witnesses/'+str(s['controls']['witnesses'].index(witness)))],
            s['life'],67,'Testigo sin revisar','Unrevised witness',
            output=record['value'],evidence=record,
            witness_form=witness['form'],same_qualified_value_before_after=True,
            witness_total_in_record=13,classification='Registro'))
    return out


def cases10():
    s = _scene('10')
    out = []
    labels = {'REG_PAIRED':('Historia asociada','Paired history'),
              'REG_UNPAIRED':('Control no asociado','Unpaired control'),
              'REG_OPPOSITE':('Historia opuesta','Opposite history')}
    for arm in ('REG_PAIRED','REG_UNPAIRED','REG_OPPOSITE'):
        frames = s['source_frames_by_arm'][arm]
        for tick in (3,292,293):
            index,frame = next((i,f) for i,f in enumerate(frames) if f['tick']==tick)
            # Preserve every retained sampled RAW0 as well as nonzero RAW.
            points = frame['points']
            focus = [p['site'] for p in points if int(p.get('raw',p.get('rawstr','0'))) != 0]
            if tick in (292,293):
                ctx_index,ctx = next((i,c) for i,c in enumerate(s['contact_contexts_by_arm'][arm]) if c['tick']==tick)
                points = ctx['points']
                focus = [ctx['center']]
                refs = [_ref(SOURCE_NAME,f'/scenes/S10/contact_contexts_by_arm/{arm}/{ctx_index}')]
                scope = ctx['coverage']
            else:
                refs = [_ref(SOURCE_NAME,f'/scenes/S10/source_frames_by_arm/{arm}/{index}')]
                scope = 'Ten exact retained probes; RAW0 included; not the whole field.'
            out.append(_entry('10_'+arm+'_'+str(tick),tick,points,focus,[*refs,frame['source']],
                arm,67,*labels[arm],observed_point_scope=scope,
                direction_sites=[p['site'] for p in points if int(p.get('raw',p.get('rawstr','0'))) != 0],
                direction_is_not_a_tracked_trajectory=True))
        reader = s['arms'][arm]['qualified_readers']['Flat']
        physical = reader['observations']['function']
        e = _entry('10_'+arm+'_437',437,[physical],[physical['site']],
            [reader['source'],_ref(SOURCE_NAME,f'/scenes/S10/arms/{arm}/qualified_readers/Flat')],
            arm,67,*labels[arm],evidence=reader,classification='Registro',
            reader_evidence=reader,external_metric=s['arms'][arm]['functional_observer'],
            external_metric_is_not_native_output=True)
        available = reader['qualified_function']
        e['output_es'] = 'Función disponible' if available else 'Sin función local'
        e['output_en'] = 'Function available' if available else 'No local function'
        out.append(e)
    return out


def cases11():
    out = []
    bounds = [[26,1,42],[40,19,54]]
    for index,tick,es,en in [(0,72,'Señal y uso previo','Cue and prior use'),
                            (1,75,'Asociación registrada','Recorded association'),
                            (2,139,'Señal posterior','Later cue'),
                            (3,142,'Uso posterior','Later use')]:
        p = _panel('11',index,0,'11_cue_'+str(tick),es,en)
        points,refs,frame = _context(tick,bounds=bounds)
        p['points'] = _points(points+p['points'])
        p['source_refs'] += refs
        p['bounds'] = bounds
        p['complete_buffer_cut'] = frame['complete_buffers']
        p['observed_point_scope'] = frame['coverage']
        out.append(p)
    control = _panel('11',4,1,'11_cue_142_other_route',
                     'Otra ruta consultada','Other queried route')
    control['observed_point_scope'] = 'Exact retained reader; an uncovered/null reading is not wrong content.'
    out.append(control)
    return out


def cases12():
    s = _scene('12')
    out = []
    labels = [(0,0,'12_source_initial','Origen: estado inicial','Source: initial state'),
              (1,0,'12_source_after','Origen: experiencia previa','Source: prior experience'),
              (2,0,'12_first_trained','Primer uso: con experiencia','First use: trained'),
              (2,1,'12_first_control','Primer uso: control','First use: control'),
              (3,0,'12_opposite_trained','Regla opuesta: con experiencia','Opposite rule: trained'),
              (3,1,'12_opposite_control','Regla opuesta: control','Opposite rule: control')]
    for card,index,identity,es,en in labels:
        panel = s['transfer_stages'][card]['panels'][index]
        basename = Path(panel['source']['path']).name
        life = s['life_by_source_record'][basename]['life']
        p = _panel('12',card,index,identity,es,en,life)
        p['experiment'] = 'ENTE02_TRANSFER'
        p['first_action_before_new_destination_feedback'] = card == 2
        p['reader_source_tick'] = panel.get('reader_source_tick',panel['tick'])
        p['opposite_rule'] = card == 3
        out.append(p)
    another = s['another_experiment']
    for index,arm in enumerate(('ref_sham_zero','ref_sham_two')):
        p = another['stages'][2]['panels'][index]
        reader = p['reader_evidence']
        life = another['life_by_arm'][arm]['life']
        out.append(_entry('12_aggregate_'+arm,16702,p['points'],p['reader_sites'],
            [p['source'],_ref(SOURCE_NAME,f'/scenes/S12/another_experiment/stages/2/panels/{index}')],
            life,67,'Otro ensayo: aportes múltiples','Another test: multiple contributions',
            output=reader['choice'],evidence=reader,
            experiment='FI01_B05 aggregate128; separate life and N67',
            actual_leaf_tick=p['actual_leaf_tick'],reader_sites=p['reader_sites']))
    return out


def cases13():
    s = _scene('13')
    full = _load(FIELD_NAME)[0]['snapshots']['S13_principal727225']
    refs = [_ref(FIELD_NAME,'/snapshots/S13_principal727225'),s['selected_checkpoint']]
    out = [_entry('13_principal_global',727225,full['points'],
        [p['site'] for p in full['occupied_points']],refs,s['life'],67,
        'Instancia: estado guardado','Instance: saved state',classification='Registro',
        complete_nonzero_field=True,summary=full['summary'])]
    for index,bounds in enumerate(([[12,11,13],[18,17,17]],[[42,11,43],[48,17,47]])):
        points = _crop(full['points'],bounds)
        out.append(_entry('13_principal_region_'+str(index+1),727225,points,
            [p['site'] for p in points if p['state']],refs,s['life'],67,
            'Región del mismo estado','Region of the same state',classification='Registro',bounds=bounds,
            no_function_inferred_from_region_position=True))
    for key,es,en in [('LEX_luma','Asociación consultada','Queried association'),
                      ('MA_PRE','Memoria consultada','Queried memory')]:
        p = s['reader_panels'][key]
        out.append(_entry('13_'+key,p['tick'],p['points'],p['reader_sites'],
            [p['source'],_ref(SOURCE_NAME,'/scenes/S13/reader_panels/'+key)],
            s['source_candidate_life'],67,es,en,
            markers=[q['site'] for q in p.get('input_receipts',[])],
            output=p['output'],evidence=p['reader_contract'],
            published_as=s['life'],same_documented_lineage=True,
            reader_sites=p['reader_sites'],input_receipts=p.get('input_receipts',[])))
    c = s['comparison']
    out.append(_entry('13_comparison',c['tick'],[c['point']],[c['point']['site']],
        [c['source'],_ref(SOURCE_NAME,'/scenes/S13/comparison')],s['source_candidate_life'],67,
        'Comparación consultada','Queried comparison',
        output=c['choice'],evidence={'contract':'ECI01.early_access.P0.R1','source':c['source'],
                                   'query_tick':c['query_tick'],'choice':c['choice']},
        published_as=s['life'],same_documented_lineage=True,
        fixed_prepared_P0_access=True))
    return out


def all_cases():
    return {number:globals()['cases'+number]() for number in ('03','05','10','11','12','13')}


if __name__ == '__main__':
    cases = all_cases()
    print(json.dumps({k:[{'id':v['id'],'tick':v['tick'],'N':v['N'],'life':v['life'],
                         'points':len(v['points']),'output_es':v['output_es']}
                        for v in values] for k,values in cases.items()},ensure_ascii=False,indent=2))
