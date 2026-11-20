"""Passive synthesis of closed Native18: primaries, full World and own journal."""
from __future__ import annotations
from collections import Counter
import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_MAIN_R02'
OUT=ROOT/'analisis/MAIN_R02_FINAL_RECALCULO_R01'


def read(path):
    path=Path(path);before=path.read_bytes();value=json.loads(before)
    if path.read_bytes()!=before:raise RuntimeError('Frozen source changed')
    return value,{'path_relative_R05':str(path.relative_to(ROOT)),'bytes':len(before),'sha256':hashlib.sha256(before).hexdigest()}


def main():
    recalculo,rs=read(OUT/'RECALCULO.json')
    metrics,ms=read(OUT/'METRICAS_NATIVE_COMPARADORES_PENDIENTES/RESUMEN_COMPARATIVO.json')
    world,ws=read(ROOT/'evidencia/MAIN_R02_PERIODO_02/WORLD_FINAL.json')
    if ws['sha256']!='61e6f91c22d64f6b9a27a8df498110c8d48258b7e98441f095e190fd18e5f259':raise ValueError('Exact final World required')
    closure,cs=read(ROOT/'evidencia/MAIN_R02_PERIODO_02/SOURCE_OWNER_CLOSED.json')
    terminal,ts=read(ROOT/'evidencia/MAIN_R02_PERIODO_02/RESULTADO.json')
    card,vs=read(ROOT/'native/MAIN_R02/sistema/estado/vidas'/LIFE/'VIDA.json')
    if not(terminal['status']=='HORIZON_CLOSED'and terminal['owner_closed']is True and terminal['writer_drained']is True and terminal['owner_returncode']==0):raise ValueError('Exact closed final Native run required')
    if card['physical']['N']!=67 or card['physical']['tick']!=975547 or world['S']['completedCycles']!=18:raise ValueError('Final identity mismatch')
    sources=[rs,ms,ws,cs,ts,vs];events=world['events']
    cycle_by_seq={row['seq']:row['data']['cycle']for row in events if row['kind']=='FEEDBACK_COMPLETED'}
    functions=[];rejects=[];lessons=[]
    for row in sorted(recalculo['Native_functions'],key=lambda x:x['before_tick']):
        primary,source=read(Path(row['file']));sources.append(source)
        summary={key:row.get(key)for key in('seq','operation_id','kind','slot','form','left','right','before_tick','after_tick','memory_value','operation','numeric_result','input_admission_complete','public_tool_result','file_sha256')}
        summary['cycle']=cycle_by_seq[row['seq']];summary['Native_inputs']=primary['Native_inputs']
        summary['source_primary']=source
        if row['kind']=='LESSON':
            summary['visible_items']=primary['visible_tool']['items'];lessons.append(summary)
        for request in primary['requests_normalized']:
            if request['receipt']['status']!='applied':rejects.append({'cycle':summary['cycle'],**request})
        functions.append(summary)
    native_journal=ROOT/'native/MAIN_R02/sistema/estado/servicios_locales'/LIFE/'RBX02_NATIVE_C02_R02/events.jsonl'
    raw=native_journal.read_bytes();journal=[json.loads(line)for line in raw.decode('utf8').splitlines()if line.strip()]
    if native_journal.read_bytes()!=raw:raise RuntimeError('Closed journal changed')
    sources.append({'path_relative_R05':str(native_journal.relative_to(ROOT)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    pending={};outputs={};returns=[];phase_counts=Counter()
    for item in journal:
        if item.get('kind')=='PHASE_INTENT':pending[item['mode']]=item
        elif item.get('kind')=='PHASE_COMPLETED':
            mode=item['mode'];intent=pending.pop(mode,None);phase_counts[mode]+=1
            if intent is None:raise ValueError('Completed Native phase without its intent')
            result=item['result'];context=intent['context'];operation=context['operation_id']
            if mode in('eci01-rbx01-decision','eci01-rbx01-query-sensor'):
                outputs[operation]={'mode':mode,'result':result,'context':context}
            if mode=='eci01-rbx01-feedback':
                proof=result['evidence'];returns.append({'operation_id':operation,'sequence':context['sequence'],
                    'actual_failed':proof['actual_physical_failed'],'applied_failed':proof['applied_generic_failed'],
                    'pulses':proof['generic_return_pulses'],'receipt_ids':[r['id']for r in proof['outcome_receipts']],
                    'all_return_receipts_applied':all(r['receipt']['status']=='applied'for r in proof['outcome_receipts'])})
    if pending:raise ValueError('Final journal retains incomplete intents')
    action_evidence=[]
    for item in events:
        if item['kind']!='ACTION_EXECUTED':continue
        action=item['data']['action'];source=outputs.get(action['actionId']);result=source['result']if source else{}
        action_evidence.append({'seq':item['seq'],'action_id':action['actionId'],'world_action':action['name'],
            'Native_action':result.get('action'),'same_actual_action':source is not None and action['name']==result.get('action'),
            'Native_NULL':result.get('null'),'world_NULL':action.get('null'),
            'Native_tick':result.get('nativeTick'),'world_Native_tick':action.get('nativeTick'),
            'same_actual_tick':source is not None and result.get('nativeTick')==action.get('nativeTick')})
    locks=[{'seq':r['seq'],'cycle':cycle_by_seq[r['seq']],'actualCode_key_present':'actualCode'in r['data'],**r['data']}for r in events if r['kind']=='EVALUATOR_LOCK_CHECK']
    replacements=[{'seq':r['seq'],'cycle':cycle_by_seq[r['seq']],**r['data']}for r in events if r['kind']=='NUMERIC_OBJECT_REPLACED']
    contacts=[{'seq':r['seq'],'cycle':cycle_by_seq.get(r['seq']),**r['data']}for r in events if r['kind']=='PHYSICAL_CONTACT']
    summary_rows=[r for r in metrics['summary_rows']if r['arm']=='LIVE_NATIVE'and r['scope']!='COMMON_COMPLETED_PREFIX']
    final_state=world['S']
    facts={'schema':'DEE.RBX01.C02.MAIN_R02.final_facts.R01','inspection_utc':datetime.now(timezone.utc).isoformat(),
        'mode':'Passive recalculation of closed Native primaries/full World/journal; no SQLite, Native, MCP, HTTP or model execution',
        'life_id':LIFE,'N':67,'parent':'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01','parent_T':947395,'final_T':975547,'new_ticks':28152,
        'adopted_to_principal':False,'scope':'Unselected C02 experimental descendant; final environment horizon18 closed. Original critical-file preservation is recorded separately by the campaign owner.',
        'actual_function_count':len(functions),'functions_chronological':functions,'rejected_inputs_exact':rejects,
        'Native_receipt_coverage':recalculo['coverage'],'recalculation_issues':recalculo['issues'],
        'Native_phase_counts':dict(phase_counts),'actions_from_actual_Native_outputs':action_evidence,
        'all_world_actions_match_Native_output_and_tick':all(r['same_actual_action']and r['same_actual_tick']for r in action_evidence),
        'actual_action_counts':dict(Counter(r['world_action']for r in action_evidence)),
        'generic_returns':returns,'return_pulses_total':sum(r['pulses']for r in returns),
        'true_generic_failure_cycles':[cycle_by_seq[r['sequence']]for r in returns if r['actual_failed']],
        'same_failure_boolean_actually_transduced':all(r['actual_failed']==r['applied_failed']and r['all_return_receipts_applied']for r in returns),
        'periods_and_actual_metrics':summary_rows,'actual_S_final':final_state,'actual_world_boundary_final':world['boundary'],
        'actual_A_to_B_chains':recalculo['World']['chains'],'actual_A_replacements':replacements,'actual_lock_checks':locks,'actual_contacts':contacts,
        'world_contingency_exposure':{
            'lesson_cycles':[r['cycle']for r in lessons],
            'lesson_visible_items':[r['visible_items']for r in lessons],
            'reversed_world_sign_interval':[8,13],
            'any_lesson_exposed_during_reversed_interval':any(8<=r['cycle']<=13 for r in lessons),
            'gate_cycle12_observed_cause':'Key present but current B absent: codePresent=false, no actualCode field. expectedCode10 is auditor-only. Do not recast as observed rejection of code8.',
            'current_world_law_and_old_Archive_signs_differed_at_gate':True,
            'reserved_clock_opportunities_completed':6,'reserved_operand_tuple_experience':False,
            'reason_reserved_tuple_not_experienced':'One key was acquired and remained held; round1 retained its actual FAMILIAR tuple9,3,4. Later Archive visit did not acquire a new key/tuple.',
            'final_round':final_state.get('round'),'final_tuple':final_state.get('roundOperands')},
        'continuity':{'logical_session_id':world['bridge']['session_id'],'same_session_after_reopen':world['bridge']['session_id']=='9cd16fa73efc45c3b6ddf3acb7bc59c8',
            'closed_owner_exit_code':terminal['owner_returncode'],'owner_closed':terminal['owner_closed'],'writer_drained':terminal['writer_drained'],
            'bridge_closed_state':terminal['bridge_closed_state'],'ledger_intent':terminal['ledger_final']['intent'],
            'final_physical':card['physical'],'final_snapshot_storage':card['storage'],
            'continuation_limit':'Native state/full environment preserved. Existing evaluation horizon is closed18 and time scope is finite; no claim of unlimited live continuation or reopening after cutoff without a new declared protocol.'},
        'interpretation_supported':[
            'Every one of36 World action names and Native ticks matched the corresponding Native physical phase output, not a map-solving action table in the Native bridge.',
            'Signed content consistent with inherited luma+ was used five times for9+3->12 and nara- twice for actual12-4->8, through the fixed sign/opcode codec and Native arithmetic mechanism; concordant teacher inputs prevent isolating pure retention from refresh/readquisition.',
            'Both real12 intermediates used by B are linked to the previous actual A event; final B8 is tied to A version5. Numeric correctness7/7 is separate from environmental usefulness0 resources/0 deliveries.',
            'Two legal concordant-sign lesson attempts were partially admitted; compatible signed content was subsequently usable. No new reversed-sign acquisition was shown in this MAIN trajectory.',
            'Save/reopen at6 and final close at18 completed opportunities preserved the same Native genealogy and logical session. No reopening after18 or final full inherited12/12 panel was executed.'],
        'not_demonstrated':[
            'Acquired coordinated task plan, utility improvement, resource-specific objective learning or exclusive causal attribution of action changes to feedback without matched controls.',
            'Transfer to reserved operand tuples: those tuples were never presented in this trajectory despite six opportunities occurring in the reserved clock window.',
            'Native learning of the8..13 sign reversal: this life did not visit Archive during that interval.',
            'Pure intact retention versus refresh/readquisition of the concordant old word signs: this MAIN has no matched no-lesson control.',
            'General intelligence, subjective pain, energy/metabolism, autonomous recovery or universal superiority/inferiority versus references with unequal prior instructions.'],
        'comparators':'Pending final PROGRAMMED and CONVENTIONAL_AI evidence; this file contains Native-only final facts, not a completed ranking.',
        'sources':sources,'subagent_native_ticks':0,'active_SQLite_opened':False}
    target=OUT/'HECHOS_Y_ATRIBUCION_MAIN_R02_FINAL.json'
    with target.open('x',encoding='utf8')as stream:stream.write(json.dumps(facts,ensure_ascii=False,indent=2)+'\n')
    with(OUT/'TODAS_FUNCIONES_CRONOLOGICAS.csv').open('x',encoding='utf8',newline='')as stream:
        fields=('cycle','seq','kind','slot','form','left','right','memory_value','operation','numeric_result','before_tick','after_tick','input_admission_complete','operation_id','file_sha256')
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for row in functions:writer.writerow({key:row.get(key)for key in fields})
    print(json.dumps({'output':str(target.relative_to(ROOT)),'Native_actions_matched':facts['all_world_actions_match_Native_output_and_tick'],
        'actions':facts['actual_action_counts'],'functions':len(functions),'rejects':len(rejects),'generic_failures':facts['true_generic_failure_cycles'],
        'return_pulses':facts['return_pulses_total'],'lock_checks':locks,'final_T':facts['final_T']},ensure_ascii=False))


def matrix():
    facts,_=read(OUT/'HECHOS_Y_ATRIBUCION_MAIN_R02_FINAL.json')
    if facts['final_T']!=975547 or facts['actual_function_count']!=9 or facts['Native_receipt_coverage']['unique_receipts_observed']!=1527:
        raise ValueError('Exact final Native evidence required for matrix')
    with(ROOT/'fuentes/MATRIZ_REPERTORIO_BASE.csv').open(encoding='utf-8-sig',newline='')as stream:rows=list(csv.DictReader(stream))
    if len(rows)!=12:raise ValueError('Twelve base families required')
    updated={
      '01':('Dos intentos de leccion concordante, ambos parcialmente admitidos; no nueva inversion aprendida en MAIN',
            'Ciclos1/14 ofrecieron luma+/nara-;4/6 entradas aplicadas en cada uno. No visito Archive durante inversion8..13.',
            'MEMPAIR separado: cambios de signos y operaciones antes/despues,5/5 numeros; desincronia no ejecutada.',
            'No sumar el aprendizaje MEMPAIR a MAIN ni considerar formedFalse de una leccion una consulta NULL.'),
      '02':('Contenido firmado compatible con el heredado utilizable tras reapertura; retencion pura no aislada',
            'luma+ usado5 veces y nara-2, antes/despues de reapertura6; tambien hubo enseñanza concordante.',
            'DEV uso nara+ tras reapertura; alfa/contextos y demas funciones siguen con su cobertura historica.',
            'No distinguir retencion de refuerzo/readquisicion sin control sin leccion; no nuevo panel completo12/12 final.'),
      '03':('No nuevo panel de comparacion positiva/negativa/cero en C02',
            'FI128 produjo numeros12/8; ello no sustituye el contrato de comparacion heredado.',
            'Base PI10 conserva sus testigos historicos, con cero temprano y NULL tardio separados.',
            'Ningun cero numerico aparecio entre los7 calculos MAIN; ausencia de cero no es fallo del mecanismo.'),
      '04':('7/7 numeros formados y correctos para el opcode realmente emitido',
            '5 usos luma+ seleccionaron9+3->12;2 usos nara- seleccionaron actual12-4->8; todos los calculos admitidos.',
            'DEV2/2 y MEMPAIR5/5 en sus ramas; no son aprendizajes ni individuos independientes.',
            'Arbol aritmetico y codec preparados; correccion aritmetica no implica utilidad ambiental ni algoritmo adquirido.'),
      '05':('Dos transportes A real->B verificados; objetivo ambiental MAIN no conseguido',
            'B usa actual12 de A en ciclos13/18. Recurso0 y entrega0; unica cerradura en12 llego sin B vigente.',
            'DEV cadena4->5 habilito1 recogida; corte ambiental de B elimina ese efecto con0 ticks Native.',
            'Orden por estaciones preparado P0; no plan multietapa adquirido. No trasladar el recurso DEV a MAIN.'),
      '06':('36 acciones World coinciden con salidas y ticks Native',
            '18 consultas ASK,3 EXIT_0 y15 EXIT_1;0 NULL y0 SAFE_WAIT.1527 entradas:1523 aplicadas/4 rechazadas.',
            'Comparten datos dinamicos legales; referencias tienen instrucciones simbolicas de metas no equiparadas a Native.',
            'No se demuestra interpretacion separada de bits del escalar ni ventaja de seleccion de informacion.'),
      '07':('Retorno real registrado; causalidad exclusiva del aprendizaje nuevo no contrastada',
            '36 pulsos de retorno aplicados; fallo generico real en ciclos1/12/14, False en los15 restantes.',
            'MEMPAIR antes/despues no sustituye controles yoke/noaversive de MAIN; MEMCTRL no ejecutado.',
            'Cambios de rutas no prueban por si solos politica mas util, contingencia exclusiva ni un objetivo recurso adquirido.'),
      '08':('Sin prueba nueva de iniciativa o plan Native',
            'Las elecciones locales son Native; oportunidades, calendario, roles de herramientas y su invocacion por contacto son preparados.',
            'Programa externo usa jerarquia de metas+BFS; IA recibe instrucciones simbolicas; no igualdad de conocimiento previo.',
            'Comparacion descriptiva de configuraciones completas; no superioridad general ni cadena descubierta por todos.'),
      '09':('No nueva regulacion o proteccion adquirida acreditada',
            'Stock200->182 por18 consultas, peaje0/colision0; no agotamiento.4 rechazos RAW ocupados en lecciones.',
            'Cierre de editores/liberacion RAM y guardas son soporte del anfitrion, no capacidad del ente.',
            'Sin dolor, metabolismo o recuperacion autonoma inferidos; funciones antiguas no revalidadas en panel completo.'),
      '10':('Sin nuevo ensayo social de dos participantes independientes',
            'Archive ofrece señales ambientales; no interlocutor con historia propia en esta trayectoria.',
            'Mecanismos IC/MI historicos siguen atribuidos a sus vidas y contratos.',
            'No lenguaje general, negociacion ni herencia de recuerdos de otras ramas.'),
      '11':('Admisiones parciales delimitadas; no reparacion Native ni borrado global demostrados',
            '4 rejected_occupied en2 lecciones; contenido compatible posteriormente utilizable. R02 conserva recibos y aplica NO_RESULT.',
            'Primer intervalo R01/R02 tiene iguales RAW/clocks/6 IDs Native; cambia el envoltorio y la posibilidad de feedback posterior.',
            'Gestion NO_RESULT es instrumento; no autorrecuperacion ni prueba de retencion intacta.'),
      '12':('18 oportunidades cerradas en una misma genealogia, reapertura real tras6',
            'N67 T947395->975547,+28152 ticks; misma sesion logica,63 operaciones completas,0 pendientes/uncertain/noACK.',
            'DEV y MEMPAIR son ramas separadas; el principal REAL2 permanece protegido y esta candidata no se promovio.',
            'Estado final preservado; horizonte18 y alcance temporal cerrados. No reapertura posterior a18 ni panel12/12 en975547.')}
    extra=('estado_MAIN_R02','evidencia_MAIN_R02','otros_controles_y_asistencia','limite_actual')
    target=ROOT/'fuentes/MATRIZ_REPERTORIO_C02_FINAL_NATIVE.csv'
    with target.open('x',encoding='utf8',newline='')as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0])+list(extra)+['fuente_final_MAIN','comparadores'])
        writer.writeheader()
        for row in rows:
            row.update(zip(extra,updated[row['id']]))
            row.update(fuente_final_MAIN='analisis/MAIN_R02_FINAL_RECALCULO_R01/HECHOS_Y_ATRIBUCION_MAIN_R02_FINAL.json',comparadores='PENDIENTES de cierre y recálculo final; ninguna clasificacion global')
            writer.writerow(row)
    raw=target.read_bytes();print(json.dumps({'matrix':str(target.relative_to(ROOT)),'rows':len(rows),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()},ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--matrix-only',action='store_true');args=parser.parse_args()
    if args.matrix_only:matrix()
    else:main();matrix()
