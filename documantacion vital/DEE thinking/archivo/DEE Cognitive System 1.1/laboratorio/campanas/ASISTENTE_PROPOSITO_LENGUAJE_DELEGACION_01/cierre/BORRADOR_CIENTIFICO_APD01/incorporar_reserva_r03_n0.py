"""Derive R03 facts and draft contents only: no imports from the DEE runtime."""
import copy
import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
ROOT = HERE.parents[4]
EV = ROOT / 'evidencia/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01'
R03 = EV / 'servicio/SERVICIO_60MIN_APD_R03'
CORTE_SHA = '1d89d1feca09958682cf784199c1270ae3c590d458a2fec15c74b30f24ab6dd9'


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, data, exclusive=False):
    with p.open('xb' if exclusive else 'wb') as f:
        f.write((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf8'))


def main():
    if sha(R03/'CORTE_PARA_MANUAL.json') != CORTE_SHA:
        raise ValueError('The agreed closed R03 cut differs')
    corte = read(R03/'CORTE_PARA_MANUAL.json')
    panels = read(R03/'PANELES_Y_FUNCIONES.json')
    time = read(R03/'RECALCULO_TIEMPO_APD.json')
    apd_all = panels['APD_primitive_uses_including_composition_stages']
    apd = [r for r in apd_all if r['id'].startswith('apd62_')]
    mem_all = panels['memory_uses']
    mem = [r for r in mem_all if r['id'].startswith('apd62_')]
    assert len(apd_all) == 65 and len(apd) == 61
    assert len(mem_all) == 40 and len(mem) == 36
    assert all(r['word_matches_history'] and r['correct_given_actual_operator'] and r['real_artifact_completed'] for r in apd)
    assert all(r['matches_expected'] for r in mem)
    assert {r['route'] for r in apd} == {-1}
    within = sum(r['completed_within_prepared_modeled_budget2'] for r in apd)
    assert within == 42
    forms = {}
    for form in ('total', 'quita'):
        rows = [r for r in apd if r['form'] == form]
        forms[form] = {
            'uses': len(rows), 'matches_history': sum(r['word_matches_history'] for r in rows),
            'numeric_correct': sum(r['correct_given_actual_operator'] for r in rows),
            'artifacts_completed': sum(r['real_artifact_completed'] for r in rows),
            'within_modeled_budget2': sum(r['completed_within_prepared_modeled_budget2'] for r in rows),
            'actual_uses': rows,
        }
    assert forms['total']['uses'] == 5 and forms['quita']['uses'] == 4
    ps = corte['persistent_service']
    fn = corte['functional_results']
    assert ps['clean_closure'] is False and ps['owner_stopped'] is True
    assert corte['main']['tick'] == 325311
    src = [{'relative_ROOT': str((R03/n).relative_to(ROOT)).replace('\\','/'), 'sha256': sha(R03/n)}
           for n in ['CORTE_PARA_MANUAL.json','PANELES_Y_FUNCIONES.json','RECALCULO_SERVICIO_APD.json','RECALCULO_TIEMPO_APD.json']]
    facts = {
        'schema': 'APD01.closed_R03_facts.N0.R1', 'scope': 'Closed R03 only; R04 final remains pending',
        'native_ticks_generated_by_this_tool': 0, 'Runtime_imported': False,
        'main': corte['main'], 'paired_export': corte['paired_export'],
        'APD_new_prefix': {'prefix': 'apd62_', 'stages': len(apd), 'word_history_matches': 61,
            'numeric_correct_given_emitted_operator': 61, 'actual_artifacts': 61,
            'within_modeled_budget2': within, 'routes': {'-1':61},
            'inherited_stages_excluded':len(apd_all)-len(apd)},
        'memory_new_prefix': {'queries':len(mem), 'matches_history':36,
            'inherited_queries_excluded':len(mem_all)-len(mem),
            'last_observations_precede_remaining_idle':fn['last_memory_observations']},
        'new_forms': forms, 'teaching': fn['explicit_teaching'],
        'native_receipts':fn['native_receipts'], 'transport_denominators':fn['transport_denominators'],
        'other_functions': {k:fn[k] for k in ['native_count','composition','chains']},
        'raw128': panels['raw128'],
        'timing_and_closure': {'world_evolving_wall_seconds':ps['world_evolving_wall_seconds'],
            'owners':2,'single_owner_uninterrupted':False,'clean_closure':False,
            'owner_stopped':True,'pending_or_uncertain':False,'epoch_closed':False,
            'historical_job_process_uncertainty_preserved':True,
            'no_minutes_from_other_revisions_added':True},
        'source_capture_scope':corte['source_capture_scope'], 'sources':src,
        'R04':{'status':'PROSPECTIVE_FINAL_RESULTS_PENDING','actual_results':None},
        'limits':['No new operation algorithms or NSM meanings claimed','New stages are not independent lives',
            'All61 new routes native; no competent reversal demonstrated',
            'R03 freeze omitted actor; P26 bytes are not retrospective continuous monitoring',
            'Completed files, numeric correctness and modeled utility are distinct',
            'The final saved tick is not an extra functional panel after remaining idle'],
    }
    write(HERE/'HECHOS_R03_N0.json', facts, exclusive=True)
    archive = HERE/'_VERSIONES_INSTRUMENTALES/PRE_R03'
    archive.mkdir(parents=True, exist_ok=False)
    for name in ['COBERTURA.json','DATOS_TABLA_CAPACIDADES.json','CAPACIDADES_POR_VIDA.csv']:
        shutil.copy2(HERE/name, archive/name)
    cov = read(HERE/'COBERTURA.json')
    cov['status'] = 'BORRADOR_R03_CERRADA_R04_PENDIENTE'
    cov['main_last_examined_complete_cut'] = copy.deepcopy(corte['main'])
    cov['reserve_execution_revisions']['R03'] = {
        'status':'CLOSED_WITH_PROCESS_CLOSURE_UNCERTAINTY',
        'pause_and_reload_in_protocol':True,'ininterrupt_owner_claim':False,
        'actual_results':facts,'clean_closure':False,
    }
    cov['not_claimed'] = ['Strict one-owner R04 success','Campaign finalcut','AGI','Autonomous planner',
        'General grammar','Automatic sandbox security','Learned reversal of route usefulness',
        'R03 actor continuously monitored despite omitted freeze map entry']
    cov['reserve']['meaning'] = 'Historical R01 proposal only; closed R03 is separately counted; R04 remains prospective'
    cov['attribution_limits']['Spanish_forms_MAIN_acquired_in_closed_R03'] = 2
    cov['attribution_limits']['accumulator_key_progress_only_excludes_operand_or_offset_response'] = True
    cov['attribution_limits']['whole_life_history_may_legitimately_contain_lessons_and_results'] = True
    write(HERE/'COBERTURA.json', cov)
    table = read(HERE/'DATOS_TABLA_CAPACIDADES.json')
    rows = [r for r in table['rows'] if r[4] != 'EN_CURSO_NO_EVALUADA']
    n = len(rows)
    panel_source = str((R03/'PANELES_Y_FUNCIONES.json').relative_to(LAB.parents[2])).replace('\\','/') if False else '../../../evidencia/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01/servicio/SERVICIO_60MIN_APD_R03/PANELES_Y_FUNCIONES.json'
    # Paths outside LAB are explicitly rooted at ROOT, not implied portable files.
    panel_source = 'ROOT:evidencia/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01/servicio/SERVICIO_60MIN_APD_R03/PANELES_Y_FUNCIONES.json'
    final_sha = corte['main']['snapshot_sha256']
    def row(label,status,num=None,den=None,tick=325311,limit='',source=panel_source,req=None,applied=None,rejected=None,attribution='Misma MAIN; registros cerrados R03; sin sumar auxiliares'):
        rows.append(['ASISTENTE_MAIN',tick,'fisica_directa',label,status,num,den,req,applied,rejected,
            source,final_sha,attribution,limit])
    for key,label in [('word_history_matches','R03 nuevas etapas: signo concordante con historia'),
                      ('numeric_correct_given_emitted_operator','R03 nuevas etapas: numero correcto dada operacion emitida'),
                      ('actual_artifacts','R03 nuevas etapas: artefacto real completado')]:
        row(label,'USO_VALIDADO',facts['APD_new_prefix'][key],61,limit='61 etapas nuevas; otras4 heredadas excluidas; no61 vidas ni algoritmos aprendidos')
    row('R03 etapas dentro presupuesto ambiental2','UTILIDAD_LIMITADA',42,61,
        limit='Las61 rutas fueron nativas−; no reversión competente al cambiar conveniencia')
    row('R03 consultas nuevas memorias anteriores','USO_POSTERIOR_SEGUN_HISTORIA',36,36,
        limit='Otras4 heredadas excluidas; beta fue reenseñada+; ultimas lecturas antes de ocio final')
    row('R03 total: signo/numero/archivo tras docencia','ADQUISICION_Y_USO_EN_MAIN',5,5,
        tick=max(r['after_tick'] for r in forms['total']['actual_uses']),
        limit='Docencia2/2;5usos;3/5 dentro presupuesto; algoritmoSUM preparado')
    row('R03 quita: signo/numero/archivo tras docencia','ADQUISICION_Y_USO_EN_MAIN',4,4,
        tick=max(r['after_tick'] for r in forms['quita']['actual_uses']),
        limit='Docencia2/2;4usos dentro presupuesto; DIFERENCIAafin preparada')
    for ctx,r in sorted(fn['last_memory_observations'].items()):
        row('R03 ultima observacion '+ctx+' signo'+str(r['choice']),'OBSERVACION_FECHADA',1,1,tick=r['tick'],
            limit='No ensayo adicional al corte final; no acceso indefinido; id'+r['id'])
    row('R03 conteo nativo','FUNCION_PREPARADA_UTILIZADA',9,9,limit='Solicitudes nuevas nominales; no concepto cardinal general')
    row('R03 composiciones numericas','COMPOSICION_ASISTIDA',10,10,
        limit='Solicitudes de transporte, no etapas primitivas; orden del operador')
    row('R03 crudos128','USO_RELACION_RESERVADA',5,5,limit='5tramas, no128conceptos ni129réplicas')
    row('R03 admision nativa total ventana','RECIBOS_APLICADOS',15406,15406,
        req=15406,applied=15406,rejected=0,limit='Incluye trabajo de solicitudes heredadas; no solo61etapas nuevas')
    row('R03 transporte: admitidas entre intentos','ADMISION_TRANSPORTE',131,140,
        limit='6rechazoscapacidad+3validacion;17controlestecnicosvalidos contados aparte; no denominador nativo')
    row('R03 evolucion habilitada4411.296152s','DOS_PROPIETARIOS_CIERRE_NO_LIMPIO',
        limit='Descontadas pausas; no unicoowner continuo; Jobactive1 antesclose; no sumar R01/R02')
    rows.append(['ASISTENTE_MAIN',None,'fisica_directa','Reserva operativa R04: un propietario3720s',
        'RESULTADOS_FINALES_PENDIENTES',None,None,None,None,None,
        'ROOT:evidencia/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01/servicio/SERVICIO_60MIN_APD_R04',
        None,'Diseño prospectivo; sin atribuir resultados','No sumar R03; corte/lecturas finales requieren primarios reales'])
    table.update(rows=rows,status='BORRADOR_R03_REAL_R04_PENDIENTE',native_ticks_generated=0,
        previous_historical_rows_preserved=n)
    write(HERE/'DATOS_TABLA_CAPACIDADES.json', table)
    candidate = read(HERE/'DATOS_MANUAL_APD01_CANDIDATO_R03.json')
    candidate['schema'] = 'APD01.manual_content_candidate.R4'
    candidate['pending_results']['final_reserve_R03'] = facts
    candidate['pending_results']['prospective_reserve_R04'] = None
    for p in candidate['chapter']:
        t = p['text']
        if t.startswith('Al corte previo P26 de MAIN'):
            p['text'] = ('P26 preparó la ampliación sin enseñar total/quita: diez formas anteriores correctas y regresión numérica11/11/2. '
                'R03 continuó la misma MAIN y aplicó dos entradas docentes para total+, dos para quita− y tres para revisar beta+. '
                'Después utilizó total5/5 y quita4/4 con signos, números y archivos concordantes; total3/5 y quita4/4 quedaron dentro del presupuesto ambiental. '
                'No se trasplantaron recuerdos de las ramas léxicas. El cierre R04 posterior sigue pendiente: {{ADQUISICION_NUEVAS_FORMAS_EN_MAIN}}.')
        elif t.startswith('Una experiencia explícita con resultado docente externo'):
            p['text'] = t.replace('Metadatos operativos conservan calendario y cursor, no los operandos docentes ni el desplazamiento como una respuesta de software.',
                'La clave y el progreso específicos del acumulador conservan llegada, cursor y estado, no operandos docentes ni desplazamiento como respuesta de software. '
                'VIDA/HISTORIA y recibos sí contienen legítimamente experiencias y resultados; el actor revisado no los consulta para resolver el cálculo. No se afirma inaccesibilidad universal.')
        elif t.startswith('R03 y la revisión prospectiva R04 deben describirse'):
            p['text'] = ('R03 alcanzó T325311 con4411,296152s habilitados tras pausas y recarga entre dos propietarios. '
                'El prefijo nuevo produjo61/61 signos concordantes,61/61 números correctos dada la operación emitida y61/61 archivos; sólo42/61 dentro del presupuesto. '
                'Todas las61 rutas fueron nativas−: no hubo reversión competente. Las36/36 consultas nuevas de memorias concordaron con su historia revisada. '
                'Los totales65etapas y40consultas incluyen cuatro heredadas cada uno y no se presentan como nuevos. Conteo9/9, composiciones10/10 y crudos1285/5 fueron oportunidades distintas. '
                'Las últimas observaciones preceden al ocio restante. La reserva R04, un propietario sin pausa planificada, queda pendiente: {{RESULTADOS_RESERVAS_R03_R04}}.')
    # Keep countable process and capture limitations as separate paragraphs.
    index = next(i for i,p in enumerate(candidate['chapter']) if p['text'].startswith('32.7 Perímetro'))
    candidate['chapter'][index:index] = [
        {'style':'Normal','text':('R03 registró140intentos literales:131admitidos,6rechazos de capacidad y3de validación;17controles técnicos aparte. '
            'Aplicó15406/15406entradas nativas. Su exportación emparejada postSTOP conserva cola vacía y ningún pendiente nativo/externo, con epoch abierto. '
            'No obstante clean_closure=false: cada Job informó un proceso activo después de esperar al launcher y antes de close_job. '
            'No se resolvió si era un contador tardío o un hijo aún vivo terminado al cerrar. Ausencia posterior de PIDs no reescribe ese límite; no es un fallo cognitivo demostrado ni un cierre limpio.')},
        {'style':'Normal','text':('El mapa R03 de26fuentes omitió el actor asistente_proposito_01.py. Se conservaron sus bytes exactos P26, '
            'pero no se acredita monitoreo continuo retrospectivo ni congelación completa. El mapa prospectivo R04 de27fuentes sí lo incluye. '
            'No se suman minutos ni muestras entre revisiones para resolver estos límites.')},
    ]
    candidate['chapter'][-1]['text'] = ('Fuentes: primarios P01–P26; contrastes léxicos R01–R04; acumulación y retorno común; '
        'REFERENCIAS_EJECUTADAS_R2; corrección descriptiva del perímetro N0; reservas adversas R01/R02 y cierre real R03. '
        'La reserva operativa R04 y el paquete final permanecen pendientes de comprobantes cerrados.')
    candidate['sources_added_R03'] = src
    write(HERE/'DATOS_MANUAL_APD01_CANDIDATO_R04.json',candidate,exclusive=True)
    print(json.dumps({'facts':sha(HERE/'HECHOS_R03_N0.json'),'word_candidate':sha(HERE/'DATOS_MANUAL_APD01_CANDIDATO_R04.json'),
        'table_rows':len(rows),'prior_rows_preserved':n,'R04':'PENDING','ticks':0},ensure_ascii=False))


if __name__ == '__main__':
    main()
