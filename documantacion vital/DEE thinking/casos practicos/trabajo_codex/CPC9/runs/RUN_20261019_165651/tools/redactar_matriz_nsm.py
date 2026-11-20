"""Serialize the explicitly authored manual NSM assessment, not auto-award levels.

This is an AUDITOR document tool. No participant imports this file or its
outputs. Numerical levels below are editorial adjudications with domains,
not a rule that converts directional responses into semantic mastery.
"""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
MAIN='resultados/vida_integral/EI_D01/MEDICIONES.json'
UPDATE='resultados/continuacion/E1_MAIN_884_1220/MEDICIONES.json'
OFF='resultados/continuacion/E1_CF_OFFPATH_884_1220/MEDICIONES.json'
HISTORY={
 'THERE_IS':('E1 asistido','CPC4: presencia de recurso3 sensada externamente; misma enseñanza a ambas regiones, asociación causal con forma. No existencia general ni integraciónE1CPC9.'),
 'NOT':('E1 asistido','CPC4: clase opuesta a presencia en ventana sensada externamente. No negación proposicional general. LEX_MEMORY_CUT sólo corta HAY, no esta forma.'),
 'BEFORE':('E2 limitado','CPC8R: orden de acontecimientos reales, firma adquirida y composición posterior. No se comunicó ANTES en el ensayo que comunicó contacto.'),
 'TOUCH':('E2 limitado','CPC8R: contacto contra desvío de igual material; composición, nueva asociación y comunicación utilizada por receptor. Reserva adversa preservada.'),
 'ONE':('E2 B-only','CPC8R: una contribución en papel B; otros accesos originales fallaron. No contar aparatos independientes como léxico conjunto.'),
 'TWO':('E1 acceso asistido','CPC8R: dos contribuciones y forma adquirida; acceso original falló, diagnóstico asistido no equivale a lectura operacional.'),
 'MORE':('E2 limitado','CPC8R: referencia adquirida36→47 aplicada por comparador preparado. QFM asocia un signo con primera comparación, no aprende regla MÁS universal.'),
 'LIKE_AS':('E2 limitado','CPC8R: comparación de componente de movimiento con referencia adquirida y uso contextual de información recibida. No identidad de referentes.')}
ASSESSMENT={
 'BEFORE':{'level':'E2','domain':'Orden funcional dentro de la preparación N67; acontecimiento/participante suministrados, transformación relativa y formas posteriores.',
   'dimensions':{'A':'POSITIVA: acontecimientos reales, no bit ANTES','B':'POSITIVA: historia altera firma material','C':'POSITIVA: lectura y consecuencia posteriores','D':'POSITIVA_LIMITADA: forma opaca asociada después','E':'POSITIVA_FINITA: continuidad y usos posteriores, con pérdidas tardías','F':'PARCIAL_ADVERSA: reservas de preparación no equivalen a transferencia de signo; R31 y MAINtardío fallan','G':'POSITIVA_FUNCIONAL_LIMITADA: encuentro común orden/contacto; no gramática productiva','H':'NO_DEMOSTRADA_EN_MAIN: comunicación temporal positiva sólo auxiliar; ensayos tardíos MAIN fallaron','I':'SI_EN_E1_DOMINIO_FINITO','J':'Geometría, rutas, oportunidades y traducción física preparadas; respuestas no seleccionadas desde targets'},
   'evidence':[MAIN,'resultados/vida_integral/EI_C03_NO_ORDER_A/MEDICIONES.json','resultados/vida_integral/EI_R31_REVERSED_COMBINATION/MEDICIONES.json','front_relations/resultados/EI_R31_WORD_DIAGNOSTIC/MEDICIONES.json']},
 'TOUCH':{'level':'E2','domain':'Contacto físico en rutas declaradas contra desvío/omisión y conservación de su señal; no sentido humano universal.',
   'dimensions':{'A':'POSITIVA: interacción material y control sin contacto','B':'POSITIVA: efecto dependiente de experiencia','C':'POSITIVA: forma y consecuencia posteriores','D':'POSITIVA_LIMITADA: asociación posterior física','E':'POSITIVA_FINITA: uso después de otras adquisiciones; renovación477/483 falla','F':'PARCIAL: variaciones auxiliares y reservas positivas/adversas, no transferencia universal','G':'POSITIVA_LIMITADA: uso conjunto con orden y recurso contextual','H':'POSITIVA_LIMITADA: contacto aprendido participa en nueva adquisición de B y uso posterior, no segunda mente completa','I':'SI_EN_E1_DOMINIO_FINITO','J':'Contextos, codificación de entrada y oportunidades de enseñanza preparados; sensores no sustituyen el encuentro'},
   'evidence':[MAIN,'front_relations/revision/CONTACT_ACCESS_RECALCULO.json','front_relations/revision/RELACIONES_RECALCULO.json']},
 'TWO':{'level':'E2','domain':'Dos contribuciones/contactos calibrados originan una firma adquirida y consultable; no regla cardinal abstracta ni UNO/DOS léxicos simultáneos.',
   'dimensions':{'A':'POSITIVA: dos contactos físicos','B':'POSITIVA: la coincidencia con forma altera el portador','C':'POSITIVA: emisión posterior cualificada','D':'POSITIVA_LIMITADA: una forma opaca, no palabra española','E':'POSITIVA_FINITA:12lecturas114–818; recuperación1287/1354 y continuidad posterior; deterioro bajo extensión65 registrado','F':'NO_DEMOSTRADA_EN_E1: robustez a dosis pertenece a auxiliares con su propia enseñanza','G':'NO_DEMOSTRADA_COMO_COMPOSICION_SEMANTICA','H':'NO_DEMOSTRADA_PARA_TWO','I':'SI: una historia de dos contribuciones en E1','J':'Lector/cadencia y codificación de dosis preparados; no contador externo de contactos como respuesta'},
   'evidence':[MAIN,'resultados/vida_integral/EI_C01_NO_COUNT_FORM/MEDICIONES.json',UPDATE,'front_relations/resultados/E1_MAIN_1220_1371/MEDICIONES.json']},
 'MORE':{'level':'E3','domain':'Transferencia cuantitativa finita: una referencia material adquirida y revisada se usa frente a objetos nuevos en un comparador nativo preparado. No se afirma aprendizaje de la ley comparativa ni dominio de la palabra MÁS.',
   'dimensions':{'A':'POSITIVA: aportes materiales y objetos actuales, no clase ya calculada','B':'POSITIVA: referencia adquirida54 y revisión real+13→67','C':'POSITIVA: comparación depende de referencia y objeto actuales','D':'PARCIAL: formas de resultado/retorno asociadas; no signo que nombre y generalice todo el operador','E':'POSITIVA_FINITA: nueva adquisición conserva operandos36/16 en usos943/1010/1077/1144','F':'POSITIVA_RESERVA_ACOTADA: predicciones previas ante57/57/70/11,4/4 en MAIN y4/4 en control fuera de ruta, con patrones distintos','G':'POSITIVA_COMPOSICION_FISICA: dos operandos aprendidos y operadores preparados; no productividad semántica abierta','H':'PARCIAL_CAUSAL: transferencia de respaldo adquirido a B y resultado recibido; retorno negativo tiene asociación residual por defecto','I':'SI: referencia y revisiones en el mismo E1','J':'Ley/gradiente, geometría, lectores y respaldo adquirido mediante exposiciones adicionales son recursos declarados; Python no calcula ni inyecta la comparación'},
   'evidence':[MAIN,UPDATE,OFF,'resultados/retorno/RET_CAUSAL/MEDICIONES.json','resultados/retorno/RET_CAUSAL_MINUS/MEDICIONES.json','resultados/retorno/RET_V3_R31_SOURCE23_OBJECT16/MEDICIONES.json','resultados/retorno/RET_V3_R32_SOURCE23_OBJECT35/MEDICIONES.json']},
 'LIKE_AS':{'level':'E2','domain':'Semejanza de un componente de movimiento con referencia direccional adquirida, mediante normalizadores/rutas preparados. No igualdad de referente ni parecido humano general.',
   'dimensions':{'A':'POSITIVA: referente direccional actual','B':'POSITIVA: referencia sólo aparece por experiencia','C':'POSITIVA_LIMITADA: comparación nativa con otro portador','D':'PARCIAL: formas finitas y codificación declaradas, no nombre universal del operador','E':'POSITIVA_FINITA: retención y segunda adquisición en dominio MCTS','F':'TRANSFERENCIA_FISICA_DOCUMENTADA: nuevos portadores; no reserva semántica confirmatoria CPC9 que justifique elevar automáticamenteE3','G':'PARCIAL: composición de componentes/rutas, operador preparado','H':'POSITIVA_LIMITADA: contenido de referencia recibido participa en función de receptor; no identidad ni deíxis','I':'SI_EN_E1_MCTS','J':'Comparador y todos los normalizadores candidatos preparados, referencia adquirida; no selección de rama por target'},
   'evidence':[MAIN,'base_validada/cpc8/src/relaciones/mode_reference.py','base_validada/cpc8/src/comunicacion/mode_communication.py']}}
PREREQUISITES={
 'I':'ACTION_TRACE_V2: origen causal propio frente a otra acción, misma consecuencia común. Falta signo deíctico y rol relativo adquirido.',
 'YOU':'ACTION_TRACE_V2: inversión real de actuador; no equivalencia A=YO/B=TÚ. Falta ligamiento adquirido a interlocutor actual.',
 'ONE':'COUNT_ACCESS/PRESENCE_REMOTE: asociación conservada en ONE_A/ONE_B, mundos distintos de E1. AuxE2 calibrado; dosis robusta del primer conteo no es transferencia de su signo.',
 'KNOW':'Consulta: historias locales suficientes/insuficientes y respuesta recibida alteran emisión. Falta adquirir significado SABER, no sólo disponer de información.',
 'THINK':'Dos operandos adquiridos producen nueva comparación; operador preparado. No todo procesamiento equivale a PENSAR aprendido.',
 'DO':'Comando físico produce acción y traza porv27; acción solicitada externamente, no agencia o palabra HACER general adquirida.',
 'THERE_IS':'PRESENCE_COUNT/REMOTE diferencia0/1/2 contactos; falta asociación existencial nueva de E1. Asociación histórica CPC4 preservada aparte.',
 'NOT':'CONTENT_REFLECTION cambia +X↔−X con mismo portador7; operador preparado, no negación adquirida. CPC4 asociación asistida preservada aparte.',
 'BECAUSE':'Intervenciones causales aisladas, traza de acción y consecuencia. Eso demuestra causalidad del auditor, no explicación causal general aprendida por E1.'}
def witness(name):
    p=ROOT/name
    return{'member':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()if p.exists()else None,'coverage':'Read primary member and tick/localizer described in CALCULOS/front reports; no automatic global lineage inferred'}
def main():
    source=ROOT/'front_semantics/revision/NSM65_PLAN_CPC9.json';plan=json.loads(source.read_text(encoding='utf8'));entries=[]
    for old in plan['entries']:
        e=deepcopy(old);key=e['id'].removeprefix('NSM65.');assessment=ASSESSMENT.get(key)
        if 'dimensiones_A_J' in e:
            e['planned_dimensions_not_results']=e.pop('dimensiones_A_J')
        if 'dimensions_A_J' in e:
            e['planned_dimensions_not_results']=e.pop('dimensions_A_J')
        e['historical_positive']=({'summary':HISTORY[key][0],'domain':HISTORY[key][1],
           'provenance':'front_semantics/revision/NSM65_APOYO_EVIDENCIAL.json and companion Core historical exact members; not attributed to E1CPC9'}if key in HISTORY else None)
        e['E1_level']=assessment['level']if assessment else'E0'
        e['level_temporal_scope']='Maximum positive evidence within the named finite life/domain, not simultaneous availability at its final tick2493'
        e['terminal_access_2493']='NOT_ESTABLISHED: 177/178 final requests rejected occupied; final TM readings active semantic7 load1 direction0 are not the qualified earlier response7X. Rejection is not proof of erasure.'
        e['E1_equivalence_to_complete_human_meaning']=False
        e['manual_assessment_scope']=assessment['domain']if assessment else'No acquisition of this primitiva is claimed in E1-CPC9. Positive auxiliary or historical evidence remains separately preserved; a physical prerequisite alone is not its meaning.'
        e['dimensions_A_J']=assessment['dimensions']if assessment else{
            'A':'PREREQUISITE_EXECUTED_ONLY'if key in PREREQUISITES else'NO_EXPERIMENTO_SEMANTICO_EJECUTADO',
            'B':'NO_ADQUISICION_DE_ESTA_PRIMITIVA_DEMOSTRADA','C':'Ver función precursora si existe; no se cambia su atribución',
            'D':'NO_FORMA_DE_ESTA_PRIMITIVA_ADQUIRIDA','E':'NO_RETENCION_DE_ESTA_PRIMITIVA_DEMOSTRADA',
            'F':'NO_GENERALIZACION_DE_ESTA_PRIMITIVA_DEMOSTRADA','G':'NO_COMPOSICION_SEMANTICA_DE_ESTA_PRIMITIVA_DEMOSTRADA',
            'H':'NO_COMUNICACION_DE_ESTA_PRIMITIVA_DEMOSTRADA','I':'No trasladar conocimiento AUX/histórico a E1',
            'J':'La pregunta del evaluador y los prerrequisitos preparados no suministran el significado al participante'}
        e['dimensions_A_J_scope']='E1-CPC9 only. Historical/auxiliary fields are separate; negative E1 dimensions never negate their positive evidence.'
        if key in ('BEFORE','TOUCH'):
            e['dimensions_A_J']['G']='POSITIVA_COMPOSICION_FUNCIONAL_FINITA: two actual arrivals26/30 form56(1,1,1); cutting either or erasingX/Z at equal56 removes target use210/214, sham reproduces full884. The fixed apparatus composition is positive, not merely transport. Content/role binding and reserved transfer of the acquired temporal-contact form remain unestablished.'
            e['independent_evidence_profile']='E2 plus positive finite G composition. Cumulative summary does not erase this result or demand open grammar.'
            e['primary_composition_witness']=witness('resultados/auditoria/COMPOSICION_E1/MEDICIONES.json')
        e['primary_witnesses']=[witness(x)for x in assessment['evidence']]if assessment else[]
        e['prerequisite_experiment']=PREREQUISITES.get(key)
        e['auxiliary_level']='E2_LIMITADO'if key=='ONE'else'Ver dominios individuales; no máximo agregado automático'
        e['experimental_status']='EJECUTADO_POSITIVO_CON_LIMITACIONES'if assessment else'EJECUTADO_PRERREQUISITO_NO_ADQUISICION_SEMANTICA'if key in PREREQUISITES else'NO_EJECUTADO_COMO_ADQUISICION_SEMANTICA'
        e['remaining_specific_blocker']=old['dependencias']
        entries.append(e)
    if len(entries)!=65 or len({x['id']for x in entries})!=65:raise AssertionError('Official65 inventory identity lost')
    catalogue=deepcopy(plan['catalogue'])
    catalogue['original_plan_path']=catalogue.get('path')
    catalogue['path']='genealogia/NSM65_CATALOGO_4_5.json'
    catalogue['included_sha256']=hashlib.sha256((ROOT/catalogue['path']).read_bytes()).hexdigest()
    out={'schema':'CPC9.NSM65.manual_adjudication.v1','catalogue':catalogue,'plan_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
      'adjudication':'Manual, by named function/individual/domain; this tool only serializes the authored decisions. Neither source nor data is imported by a participant.',
      'source_bibliography_scope':'Bibliographic provenance inherited from actually recovered2026-10-17 catalogue, not a claim of new web access or reading inaccessible chapters in CPC9.',
      'temporal_scope':'Levels summarize bounded positive episodes, never five relations claimed available at2493. Consult VIDA_PRINCIPAL/RETENCION for last actual uses and later failures.',
      'summary_level_rule':'Conservative cumulative summary, not the independent A-J profile: E4 summary requires qualified F transfer/content binding as well as positive G. BEFORE/TOUCH have positive finite G and E2 summaries; no generality is required to recognize their actual finite composition.',
      'summary':{'entries':65,'E1_levels':dict(Counter(e['E1_level']for e in entries)),
        'E1_operational_ids':[x['id']for x in entries if x['E1_level']!='E0'],
        'physical_prerequisite_or_limited_function_investigated_ids':[x['id']for x in entries if x['E1_level']!='E0'or x['prerequisite_experiment']],
        'historical_positive_ids':[x['id']for x in entries if x['historical_positive']],
        'not_a_count_of_human_meanings_mastered':True,'E1_quantitative_reserved_transfer':'MORE only in the precisely stated native comparator domain',
        'productive_semantic_grammar':'INDETERMINATE_NOT_DEMONSTRATED','productivity_question_remains_open':True,'no_E4_E5_global_primitive_awards':True},
      'entries':entries}
    dest=ROOT/'revision/NSM65_EVIDENCIAS.json';dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(out['summary'],ensure_ascii=False))
if __name__=='__main__':main()
