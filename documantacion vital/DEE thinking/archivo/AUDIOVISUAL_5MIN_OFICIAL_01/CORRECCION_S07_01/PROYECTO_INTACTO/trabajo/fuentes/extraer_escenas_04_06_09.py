"""Extract closed audiovisual evidence. Pure stdlib; no DEE import or execution.

The output records observed states and qualified readings, never interpolated
physical paths. All clocks/RAW payloads remain decimal strings.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
THINK = HERE.parents[3]
assert THINK.name == 'DEE thinking', THINK
R12 = THINK / 'archivo/AUDIOVISUAL_R12'
R08 = THINK / 'archivo/AUDIOVISUAL_R08'
PILOT = THINK / 'archivo/PILOTO_3D_COMPOSICION_10s'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def load(path):
    path = Path(path)
    if path.suffix == '.gz':
        with gzip.open(path, 'rt', encoding='utf-8') as f:
            return json.load(f)
    return json.loads(path.read_text(encoding='utf-8-sig'))


def ref(path, pointer=''):
    p = Path(path)
    return dict(path=str(p), bytes=p.stat().st_size, sha256=sha(p), pointer=pointer)


def stage(c, tick, groups=None, only_forms=None):
    """Sparse original observations plus exact structured reader fields."""
    i, f = next((i, f) for i, f in enumerate(c['frames']) if int(f['tick']) == tick)
    rf = c['recorded_frames_exact'][i]
    assert int(rf['tick']) == tick
    groups = groups or ['body', 'forms', 'questions', 'own_banks', 'actions', 'names']
    exact = {k: copy.deepcopy(rf[k]) for k in groups if k in rf}
    if only_forms is not None and 'forms' in exact:
        exact['forms'] = {k: v for k, v in exact['forms'].items() if k in only_forms}
    points = copy.deepcopy(f['points'])
    return dict(tick=tick, N=f['N'], points=points, reads=exact,
                source_pointer=f['source_pointer'],
                source=c['source'], extraction_pointer=f'/frames/{i}',
                coverage=f['scope'], interpolation='NONE; editorial cut between saved states')


def check_sources(obj):
    """Check only cited physical files, deduplicate. Never search the corpus."""
    found = {}
    def walk(x):
        if isinstance(x, dict):
            p, expected = x.get('path'), x.get('sha256')
            if isinstance(p, str) and len(str(expected)) == 64:
                found[p] = expected
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(obj)
    rows = []
    for path, expected in sorted(found.items()):
        p = Path(path)
        row = dict(path=path, expected_sha256=expected, exists=p.is_file())
        if p.is_file():
            row.update(bytes=p.stat().st_size, actual_sha256=sha(p))
            row['equal'] = row['actual_sha256'] == expected
        rows.append(row)
    return rows


def main(replace=False):
    up = R12 / 'evidencia_u0/U0_DATOS_R12.json.gz'
    mp = R08 / 'infraestructura/FUENTES_MECANISMOS_S06_S11_R08.json'
    cp = PILOT / 'subtrabajo/evidencia/COMPOSICION_CPC9_DATOS.json'
    ip = R12 / 'evidencia_reutilizada/INTERVENCIONES_R12.json'
    u, m, comp, intervention = map(load, [up, mp, cp, ip])
    main_u = u['cases']['IR_P01_GUARDED_M1']
    alt_u = u['cases']['IR_R607_GUARDED_M1']
    match_u = u['cases']['IR_MATCH_CURRENT']

    memory_arms = {}
    for name, c in [('AB_minus', main_u), ('BA_plus', alt_u)]:
        memory_arms[name] = dict(
            life=c['case']['id'], profile=c['geometry']['kind'], N=c['geometry']['N'],
            condition=c['case'], source=c['source'], configuration_source=c['configuration_source'],
            stages=[stage(c, t, ['forms'], ['L03']) for t in [0, 3, 335, 338]],
            exact_L03_calls=[x for x in c['calls_exact'] if x['port'].startswith('L03.') and int(x['at']) <= 335],
            qualified_readings=[dict(row_index=i, **x) for i, x in enumerate(c['readouts_exact'])
                                if x.get('form') == 'L03' and x.get('panel') in ['LOWER_204', 'LOWER_338']])

    scene04 = dict(
        title='Historia adquirida y consulta posterior', evidence_type='Etapas',
        campaign='CPC7 native port thinking 4.5.0; archived U0 preparations',
        arms=memory_arms,
        causal_summary='The same L03.signal payload5, T335 query yields opposite qualified directional contents at T338 after different acquired histories.',
        controls=dict(same_query=True, same_N=True, clock_buffers_equal_T338=True,
                      distinct_RAW_buffers_T338=True, source_checks=u['checks']['T338_complete_buffer_equalities'],
                      confounds='The two archived preparations also differ in AB/BA history, actual report and other bank contents; not an isolated single-factor memory ablation.'),
        assistance=['Initial anatomical supports/interfaces, six fixed guards and query timetable were prepared.',
                    'Query initiation is external; read content depends on native physical history.'],
        limits=['Two physical content classes; no attribution of65meanings.',
                'These U0 lives are not the current ECI02 individual.',
                'No physical trajectory is inferred across unrecorded ticks.'])

    scene06 = dict(
        title='Composición y reutilización', evidence_type='Etapas',
        life=comp.get('life', 'EI_D01'), profile='CPC9 closed integral experiment', N=67,
        source=ref(cp), primary_sources=comp['primary_sources'],
        stages=comp['stages'], exact_local_composition=comp['exact_local_composition'],
        generic_use_input=comp['common_use_resource7'], controls=comp['controls'],
        causal_summary='Observed26+30 antecedents atT205 form56 atT206; a generic7 use opportunity is admittedT207; the qualified plus.changed site yields63 atT210. Cut arrival0 yields7; sham56 rewrite yields63.',
        coverage=comp['coverage'],
        assistance=['Common generic7 and physical interfaces were supplied by the historical apparatus.',
                    'Cut and sham are historical diagnostic interventions in distinct copies.'],
        limits=comp['rendering_constraints'],
        essential_rule='Do not generalize cut0 to removalZ or other reading planes; no invented encounter atT207–209.')

    social = copy.deepcopy(m['cases']['IC01_SOCIAL'])
    # Dense local snapshots remain separate from the finite narrative stages.
    social.pop('passive_sampled_frames', None)
    for arm in social['arms'].values():
        original = load(arm['source']['path'])
        arm['native_life_metadata'] = original['INSTRUMENTO']
        arm['closed_parent_spec'] = original['result']['spec']
        arm['native_life_metadata_source_pointer'] = '/INSTRUMENTO'
    scene07 = dict(
        title='Comunicación física y uso posterior', evidence_type='Etapas',
        campaign='INTEGRACION_COGNITIVA_SITUADA_E1_01', N=67,
        recorded_cases=social, historical_intervention=intervention['IC01'],
        causal_summary='A private input45 toB forms a physical scalar7 with direction−; generic acquisition/retrieval opportunities allow a later qualified social− reading atT16619. Material cut produces no qualified social reading; sham retains it.',
        native_output='Qualified social direction−, distinct from the external torque0 calculated by fixed prepared actuator wiring.',
        recipient_scope='The material receiver/interacting organization is not an independently demonstrated complete mind.',
        limits=['Do not display torque0/1 as the DEE social symbol.',
                'Sparse stages do not establish unique genealogy across the delay.',
                'Separate cut requests are recorded, but no separate admission receipts2652/2653 were retained; SEM4 itself is observed atT16563.',
                'Not general language or autonomous interlocutor selection.'])

    discrepancy = {}
    for name, c in [('discrepant', main_u), ('matching_current', match_u)]:
        discrepancy[name] = dict(
            life=c['case']['id'], profile=c['geometry']['kind'], N=67,
            condition=c['case'], source=c['source'], configuration_source=c['configuration_source'],
            stages=[stage(c, t, ['body', 'questions', 'own_banks', 'actions']) for t in [5, 11, 15, 19, 69, 70, 72]],
            prepared_need_geometry=c['geometry']['need'],
            prepared_bank_geometry=c['geometry']['banks'],
            prepared_action_geometry=c['geometry']['actions'],
            material_calls=[x for x in c['calls_exact'] if 'actual' in x['port'] or 'own.use' in x['port']])
    scene08 = dict(
        title='Discrepancia, pregunta material y utilización', evidence_type='Etapas',
        campaign='CPC7 native port thinking 4.5.0; archived U0 preparations',
        arms=discrepancy,
        causal_summary='The discrepant right comparison emits horizontal request atT19; matching-current control does not emit that horizontal request. The prepared common opportunityT69 is followed by different native use atT72.',
        reader_contract=dict(question='At right.different[47,10,46], SEM1/statepositive horizontal direction[1,0,0] is the prepared question class; stationary or other vectors are not counted as that request.',
                             action='At own.use.minus[33,8,46], native use requires the stored-class directional component; common input by itself remains[0,0,1] and is not that use.'),
        assistance=['Comparator, routes, guards, current-report inputs and common action opportunities are designed.',
                    'The comparison-dependent material question is native; opportunity timing is external.'],
        limits=['Matching-current is a closed technical variant, not a new scientific reserve.',
                'Do not call an externally scheduled query autonomous initiative.',
                'Not a general policy for uncertainty or absence; not the current ECI02 life.'])

    cycle = copy.deepcopy(m['cases']['CYCLE02_RETURN'])
    external = copy.deepcopy(m['cases']['ENTE01_RETURN'])
    scene09 = dict(
        title='Consecuencia recibida y actuación posterior', evidence_type='Etapas y Esquema',
        acquired_reference=dict(campaign='CONSOLIDACION_EVOLUCION_E1_CICLO_02',
                                evidence_type='Etapas', data=cycle,
                                causal_summary='From identicalT17289 RAW/clock hashes: both first actions open andwear6. Intact return adds a physical6 through the declared generic reference ports; omit arm gets no return. At common later force2, reference11 versus5 yields opposite native actions. The intact-return action is useful in this fixed environment, the omitted-return action is not.',
                                assistance=['The environment resistance/wear and return transduction are prepared external laws.',
                                            'Utility is auditor-only and is not fed back as the correct action.'],
                                limits=cycle['limits']),
        external_service=dict(campaign='ENTE_DEE_OPERATIVO_01', life=external['life'], N=external['N'],
                              evidence_type='Registros y Esquema', data=external,
                              causal_summary='Closed external fixture receives a command derived from a qualified native reading, executes movement/contact, then sends actual tactile feedback atT96565. This displayed row is closed_gate_contact/job_completedfalse, not a successful service.',
                              scheme='Any rendered gate/actuator/contact/return outside the DEE cells is explanatory geometry of the recorded external law, not a DEE-native particle path.',
                              assistance=['Fixed external codec, body/fixture, supplies, actuator map and reader.',
                                          'No PID, target lookup or correct-next-action update is introduced by this extractor.'],
                              limits=external['limits']),
        separation='These are separate campaigns, architectures and lives: show NUEVO ENSAYO between them; do not merge history or call the external fixture a closed-v27 habitat.')

    output = dict(
        schema='DEE.audiovisual5min.selected_mechanisms.v1',
        created_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        new_DEE_ticks=0, DEE_imports=False, simulations_or_replays=False,
        extractor=ref(__file__),
        sources=[ref(up), ref(mp), ref(cp), ref(ip)],
        scenes={'04': scene04, '06': scene06, '07': scene07, '08': scene08, '09': scene09},
        general_visual_contract=['RAW/clocks are provenance, not onscreen self-explanatory semantics.',
                                 'All point positions must remain observed integer coordinates.',
                                 'No motion is invented across sparse temporal gaps; cuts/crossfades are editorial.',
                                 'Each campaign/life change must be declared; no cross-life capability union.'])
    output['cited_file_checks'] = check_sources(output)
    output['cited_file_mismatches'] = [x for x in output['cited_file_checks'] if x.get('equal') is False]
    if output['cited_file_mismatches']:
        raise ValueError('A cited file hash differs; output withheld')
    path = HERE / 'ESCENAS_04_06_09.json'
    if path.exists() and not replace:
        raise FileExistsError(path)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(output, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    temporary.replace(path)
    print(json.dumps(dict(path=str(path), bytes=path.stat().st_size, sha256=sha(path),
                          cited_files=len(output['cited_file_checks']),
                          unavailable=sum(not x['exists'] for x in output['cited_file_checks']),
                          new_DEE_ticks=0), ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--replace', action='store_true', help='Replace only this generated audiovisual JSON')
    main(parser.parse_args().replace)
