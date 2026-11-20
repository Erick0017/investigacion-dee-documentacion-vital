"""Documentary projection only: exact historical inventory and CPC7 evidence scope.

No Runtime, trajectory, model or learning is created. Plans are explicitly
unevaluated and never consumed by a participant or a response decoder.
"""
from pathlib import Path
from copy import deepcopy
from collections import Counter
import hashlib,json

ROOT=Path(__file__).resolve().parents[2]
CATALOGUE=ROOT/'genealogia/CPC5/referencias/NSM65_CATALOGO_CPC4.json'
EXPECTED='e0f29290d800a74150b7e386fe2437dcc92b99bbd587b6cfef8e38c80067ae7e'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))


# These are prospective operational tasks, not semantic definitions of NSM.
TASKS={
 'I':'Referencia relativa al emisor actual, conservando una misma señal al intercambiar papeles.',
 'YOU':'Referencia al destinatario actual, distinguiéndolo del emisor y de un tercer interlocutor.',
 'SOMEONE':'Reconocer una presencia de participante a través de más de una identidad y soporte.',
 'SOMETHING':'Reconocer un acontecimiento u objeto presente sin reducirlo a una carga fija.',
 'PEOPLE':'Distinguir varias organizaciones participantes frente a objetos no participantes.',
 'BODY':'Vincular una señal a la organización que sostiene una función, admitiendo sustitución parcial de soporte.',
 'KINDS':'Adquirir una distinción de clase que se utilice en ejemplares nuevos, no sólo separar grupos del auditor.',
 'PARTS':'Distinguir parte y conjunto mediante contribuciones causales y sustituciones controladas.',
 'THIS':'Señalar un referente presente con una relación accesible, variando identidad y coordenada.',
 'THE_SAME':'Conservar una relación de igualdad funcional al cambiar ejemplar, carga y lugar.',
 'OTHER':'Utilizar una diferencia funcional pertinente variando ambas alternativas y el contexto.',
 'ONE':'Distinguir una contribución de varias mediante acontecimientos separados, sin definir uno como una carga.',
 'TWO':'Distinguir dos contribuciones de una y de tres sin codificar desde fuera el total correcto.',
 'SOME':'Utilizar una distinción parcial de un conjunto en tareas con tamaño y miembros variables.',
 'ALL':'Comprobar cobertura de un conjunto variable con consecuencias accesibles; no sólo un timeout externo.',
 'MUCH_MANY':'Ordenar cantidades observables bajo una referencia común, sin confundir inventario con s_reg.',
 'LITTLE_FEW':'Utilizar cantidades menores bajo referencias cambiantes, comparando las mismas oportunidades.',
 'GOOD':'Adquirir una relación entre consecuencia y función contextual, cambiando cuál consecuencia sostiene esa función.',
 'BAD':'Adquirir una relación entre consecuencia y coste funcional, sin fijar un paquete universalmente perjudicial.',
 'BIG':'Distinguir extensión operacional en un marco declarado, manteniendo aparte carga e inventario.',
 'SMALL':'Distinguir menor extensión operacional entre ejemplares y marcos; no equiparar pequeño a poca carga.',
 'KNOW':'Distinguir información utilizable por la organización de soporte presente pero inaccesible, con consulta pertinente.',
 'THINK':'Definir primero una operación interna utilizable y contrastarla; evolución interna sola no enseña pensar.',
 'WANT':'Definir un sesgo de elección operacional revisable por experiencia sin adjudicar experiencia fenomenológica.',
 'DONT_WANT':'Contrastar una evitación operacional con imposibilidad de actuar y con ausencia de señal, sin atribución subjetiva.',
 'FEEL':'Requiere una definición operacional explícita independiente de un score de daño; no realizada en CPC7.',
 'SEE':'Relacionar una interfaz sensorial local con consecuencias accesibles; distinguirla de la observación global del auditor.',
 'HEAR':'Definir otra familia sensorial y sus contrastes; no llamar oír al mero transporte de cualquier portador.',
 'SAY':'Asociar una emisión adquirida a un destinatario y un efecto; distinguir comunicar de emitir materia.',
 'WORDS':'Utilizar señales por sus correspondencias adquiridas, variando formas y evitando tablas de significado en el renderer.',
 'TRUE':'Contrastar una afirmación o emisión previa con un acontecimiento posterior accesible, sin inyectar la evaluación correcta.',
 'DO':'Vincular una señal a una intervención propia que modifica una consecuencia, con actuador y ruta comprobados.',
 'HAPPEN':'Vincular una señal a una transición observable no reducida a la acción propia ni al tick del calendario.',
 'MOVE':'Vincular una señal a desplazamiento medido, distinguiéndolo de emisión, desaparición y traslado de la observación.',
 'BE_SOMEWHERE':'Utilizar una localización relativa a interfaces del participante con traslaciones y marcos reservados.',
 'THERE_IS':'Ampliar la presencia en una ventana sensorial concreta a varios contenidos y contextos con controles de acceso.',
 'BE_SOMEONE_SOMETHING':'Distinguir identidad funcional y presencia, variando soporte y posición del referente.',
 'IS_MINE':'Definir una relación de acceso o pertenencia causal que sobreviva al intercambio de papeles, no un alias del auditor.',
 'LIVE':'Definir continuidad de una función durante un horizonte y asociar la señal mediante experiencias; no adjudicar biología.',
 'DIE':'Distinguir pérdida irreversible en el dominio de pérdida de lector o de acceso, sin enseñar mediante destrucción innecesaria.',
 'WHEN_TIME':'Utilizar relaciones temporales de acontecimientos, no recibir la respuesta por un tick absoluto codificado.',
 'NOW':'Anclar un acontecimiento presente desde la interfaz local, variando calendario, retraso y oportunidad.',
 'BEFORE':'Adquirir y nombrar un orden con acontecimientos e intervalos nuevos; separar ese uso del aparato AB/BA preparado.',
 'AFTER':'Adquirir y nombrar la relación temporal inversa conservando intérprete y variando acontecimientos e intervalos.',
 'LONG_TIME':'Discriminar duración relativa con referencias físicas accesibles y cambios de escala; no un umbral privado del host.',
 'SHORT_TIME':'Discriminar menor duración bajo referencia variable y mantenerla distinta de llegada anticipada por distancia.',
 'FOR_SOME_TIME':'Vincular persistencia limitada a una ventana temporal accesible, sin convertir un timeout del programa en percepción.',
 'MOMENT':'Definir una apertura temporal operacional y variar su posición respecto a acontecimientos.',
 'WHERE_PLACE':'Usar información espacial local para responder una consulta nueva sin que el auditor seleccione el sitio correcto.',
 'HERE':'Anclar localización al participante actual, variando emisor y posición, no a una coordenada fija.',
 'ABOVE':'Aprender una relación espacial en un marco declarado con ejemplares y posiciones nuevos.',
 'BELOW':'Aprender la relación espacial inversa manteniendo fijo el marco y variando posiciones de ambos referentes.',
 'NEAR':'Adquirir una relación de proximidad dentro de un marco y escala declarados, con wrapping controlado.',
 'FAR':'Adquirir distancia relativa con escala y periodicidad explícitas, evitando que sólo cambie tiempo de espera.',
 'SIDE':'Adquirir una relación lateral respecto a un marco del participante, variando orientación y posiciones.',
 'INSIDE':'Adquirir pertenencia a una región físicamente definida, distinguiéndola de acceso a un puerto.',
 'TOUCH':'Vincular una señal a interacción local efectiva, distinguiéndola de vecindad y de correlación.',
 'NOT':'Ampliar la asociación local NO a varios contenidos, distinguiendo negación, ausencia física, silencio, cero y rechazo.',
 'MAYBE':'Representar posibilidades accesibles y usar una consulta adicional pertinente sin fabricar confianza desde el auditor.',
 'CAN':'Distinguir disponibilidad funcional de resultado ejecutado, usando experiencia e intervenciones comparables.',
 'BECAUSE':'Seleccionar o producir una relación causal utilizable; separar explicación instrumentada de introspección del ente.',
 'IF':'Utilizar una dependencia condicional adquirida en combinaciones reservadas, no sólo una guardia fija de diseño.',
 'VERY':'Aprender una modificación de grado respecto a una escala operacional estable y nuevas referencias.',
 'MORE':'Comparar incrementos de una magnitud especificada conservando unidades y contexto, sin restar RAW como escalar.',
 'LIKE_AS':'Utilizar semejanza funcional entre preparaciones nuevas; no convertir cercanía de un embedding en concepto.'
}


def main():
    if sha(CATALOGUE)!=EXPECTED:raise ValueError('Historical inventory identity changed')
    old=json.loads(CATALOGUE.read_text(encoding='utf-8-sig'))
    if old['count']!=65 or len(old['entries'])!=65 or len({e['id'] for e in old['entries']})!=65:raise ValueError('Not the exact65 inventory')
    forms={e['glosa_inglesa_id'] for e in old['entries']}
    if forms!=set(TASKS):raise ValueError('Plan keys do not correspond exactly to documentary inventory')
    manifest=read('genealogia/SOURCE_MANIFEST.json')
    def locate(value):
        if isinstance(value,dict):
            if value.get('file')=='genealogia/CPC5/referencias/NSM65_CATALOGO_CPC4.json':return value
            for v in value.values():
                r=locate(v)
                if r:return r
        elif isinstance(value,list):
            for v in value:
                r=locate(v)
                if r:return r
        return None
    provenance=locate(manifest)
    if not provenance or provenance['member_sha256']!=EXPECTED:raise ValueError('Historical selection not reconciled')
    references={
        'ORDER_BODY':{'path':'src/order_memory.py','scope':'Preparador y lectura de historia AB/BA; no señal ANTES/DESPUÉS aprendida.'},
        'COMPARISON':{'path':'resultados/endogenous/COMPARISON_SUMMARY.json','scope':'Comparación direccional que condiciona una pregunta; no MISMO/OTRO general.'},
        'FALLBACK':{'path':'resultados/endogenous/FALLBACK_SUMMARY.json','scope':'Apertura finita para ausencia de informe actual; no NO ni TAL VEZ general.'},
        'SELECTIVE':{'path':'resultados/selective_native/ANALYSIS.json','scope':'Pregunta nativa→memoria propia→uso→asociación posterior de una forma opaca; no semántica NSM.'},
        'REPERTOIRE':{'path':'resultados/comparadores/B2_FINAL/INDEX.json','scope':'Comparador de16formas y dos clases físicas; no16significados humanos.'},
        'ENSEMBLE':{'path':'resultados/ensemble/ENSEMBLE_SUMMARY.json','scope':'Coexistencia de1/2/4especialistas; no YO/TÚ, cooperación aprendida o conocimiento colectivo por suma.'},
        'UPDATE':{'path':'resultados/update_methods/ANALYSIS.json','scope':'Revisión de una correspondencia conservando otra en K2; no regla NSM de cambio.'},
        'RECURRENT':{'path':'resultados/endogenous/RECURRENT_SUMMARY.json','scope':'Oportunidad interna recurrente e inhibición preparadas; no querer, atención aprendida ni decisión general.'},
        'CAPACITY65_TECHNICAL':{'path':'resultados/reference_capacity65_01/REFERENCE.json','scope':'Reproducción técnica exacta de la fuente publicada CPC5:65formas opacas, dos clases, N131, sin integración en U0 ni65significados NSM.'},
        'INTEGRATED_REVISION':{'path':'resultados/integrated_revision/ANALYSIS.json','scope':'Cuatro nuevas preparaciones N67: cadena propia y signo142, retención338 y revisión deL03 con otras13utilizables472. El signo no fue vuelto a consultar después de402.'}
    }
    for ref in references.values():ref['sha256']=sha(ROOT/ref['path'])
    analogies={
        'THE_SAME':['COMPARISON'],'OTHER':['COMPARISON'],'KNOW':['SELECTIVE','FALLBACK'],
        'SAY':['SELECTIVE'],'WORDS':['SELECTIVE','REPERTOIRE','CAPACITY65_TECHNICAL'],'TRUE':['COMPARISON'],
        'DO':['SELECTIVE'],'HAPPEN':['COMPARISON'],'MOVE':['SELECTIVE'],
        'WHEN_TIME':['ORDER_BODY'],'BEFORE':['ORDER_BODY'],'AFTER':['ORDER_BODY'],
        'THERE_IS':['FALLBACK'],'NOT':['FALLBACK'],'MAYBE':['FALLBACK'],
        'CAN':['SELECTIVE'],'BECAUSE':['COMPARISON'],'IF':['COMPARISON'],
        'PARTS':['SELECTIVE'],'BODY':['ORDER_BODY']
    }
    entries=[]
    for i,e in enumerate(old['entries']):
        key=e['glosa_inglesa_id'];historical={k:deepcopy(v) for k,v in e.items() if k in (
            'dimensiones_independientes','respuesta_a_palabra','full_NSM_semantics','native_domain_meaning','observed_forms_by_case')}
        row={k:deepcopy(e[k]) for k in ('id','orden_tabla','glosa_inglesa_id','grupo_documental','forma_es',
            'variantes_documentadas','forma_fuente','fuentes','normalizacion_editorial')}
        row['registro_documental']={'estado':'REGISTRADA_EN_CATALOGO_DE_REFERENCIA','source_pointer':f'/entries/{i}',
            'catalogue_sha256':EXPECTED,'word_is_not_acquired_meaning':True}
        row['historico']=historical
        row['historico']['contexto_rutas']='Las rutas de evidencia contenidas en el registro histórico son relativas a CPC4, tal como las preserva el catálogo dentro de CPC5. Son procedencia heredada, no nuevas ejecuciones CPC7.'
        row['operacional']={'estado':'CANDIDATO_NO_ENSAYADO_COMO_PRIMITIVA_NSM_EN_CPC7','funcion_propuesta':TASKS[key],
            'funcion_relacionada_medida_sin_acreditar_significado':analogies.get(key,[]),
            'evidencia_de_adquisicion_semantica_CPC7':[]}
        row['plan']={'estado':'NO_EJECUTADO_EN_ESTE_CORTE','secuencia':'Establecer función prelingüística, introducir señal arbitraria fija después por experiencia, consultar sin reenseñar y reservar nuevos ejemplos, roles o contextos.',
            'controles':['misma interfaz y decoder con historias diferentes','sin emparejamiento y sin experiencia pertinente','memoria/ruta intervenida frente a sham','respuesta física y uso posterior sin tabla externa'],
            'restriccion':'El plan no autoriza otra ejecución ni cuenta como preparación; el corpus de65entradas no es una ontología interna instalada.'}
        for dimension in ('entrenamiento','retencion','uso','comunicacion','composicion'):
            row[dimension]={'estado':'NO_EVALUADO_PARA_ESTA_PRIMITIVA_EN_CPC7','evidencia_CPC7':[]}
        row['emision_situacion_a_forma']={'estado':'NO_EVALUADA_COMO_PRIMITIVA_NSM_EN_CPC7','evidencia_CPC7':[]}
        row['individuo']={'CPC7':None,'nota':'Las realizaciones opacas se enumeran por separado; no se suman a este significado.'}
        row['horizonte']={'CPC7_adquisicion_semantica':None,'CPC7_retencion_semantica':None,
            'nota':'Los ticks de mecanismos relacionados no son un horizonte acreditado de esta palabra.'}
        row['alcance']='Los mecanismos relacionados y los estados históricos conservan su dominio local. Ninguno convierte esta entrada en una primitiva NSM general adquirida.'
        entries.append(row)
    selective=read('resultados/selective_native/ANALYSIS.json')
    capacity_reference=read('resultados/reference_capacity65_01/REFERENCE.json')
    capacity_rows=[]
    for entry in capacity_reference['results']:
        path='resultados/reference_capacity65_01/'+entry['primary'];m=read(path)
        if sha(ROOT/path)!=entry['primary_sha256']:raise ValueError('Capacity primary identity mismatch')
        capacity_rows.append({'case':entry['id'],'primary':path,'sha256':entry['primary_sha256'],
            'N':m['case']['N'],'K':m['case']['K'],'read_ticks':sorted({r['tick'] for r in m['readouts']}),
            'readout_admission':dict(Counter(r['receipt']['status'] for r in m['readouts'])),
            'calculated_rounds':entry['calculations'],
            'save_load_physical_and_operative_equal':m['technical']['save_load_physical_and_operational_equal']})
    integrated_revision=read('resultados/integrated_revision/ANALYSIS.json')
    result={'schema':'CPC7.NSM65.evidence_scope.v1','kind':'DOCUMENTARY_REANALYSIS_NO_NATIVE_EXECUTION',
        'proyecto':'DEE Universe / INVESTIGACION DEE','autor_proyecto':'Ivan Erick Tlaltecatl Morales',
        'catalogue_provenance':provenance,'catalogue_sha256':EXPECTED,'inventory_count':65,
        'source_scope':'Inventario español histórico exacto; fuentes preservadas, no investigadas de nuevo en esta proyección. Las65formas no se presentan como65capacidades.',
        'sources':deepcopy(old['sources']),
        'source_resolution':'Identificadores de fuentes idénticos a los del catálogo histórico. Fechas de consulta y artefactos son los de ese corte; no se afirma haber descargado o redistribuido aquí los textos completos.',
        'counting':{'documentary_entries':65,'historical_entries_with_limited_association':2,
            'CPC7_general_NSM_meanings_credited':0,'CPC7_NSM_word_training_cases':0,
            'CPC7_lower_opaque_forms':14,'CPC7_high_candidate_memory_banks':2,
            'CPC7_opaque_physical_content_classes':2,'CPC7_later_opaque_name_protocols':1,
            'separate_technical_reference_opaque_forms':65,'separate_technical_reference_content_classes':2,
            'separate_technical_reference_preparations':2,'separate_technical_reference_integrated_in_U0':False},
        'counting_scope':'Catorce formas inferiores más dos bancos altos son16formas físicas candidatas, no16relaciones semánticas distintas. Un signo posterior recupera contenido de uno de dos bancos seleccionados; no es una primitiva adicional por defecto.',
        'native_realizations_not_NSM_equivalence':[
            {'id':'OPAQUE_16','mechanism':'Dieciséis señales en interfaces fijas, dos clases direccionales; las catorce inferiores mezclan seis antiguas y ocho nuevas en MAIN.',
             'evidence':'SELECTIVE','individual':'U0_SELECTIVE, una identidad por caso','horizon':'Primera adquisición3; nueva adquisición137; paneles204 y338.',
             'retention_scope':selective['domain']['retention'],'NSM_mapping':None},
            {'id':'ORDER_AB_BA','mechanism':'Relación diferencial de un cuerpo preparado que depende del orden de experiencias AB/BA y emite una dirección en5.',
             'evidence':['ORDER_BODY','COMPARISON'],'individual':'Una identidad por preparación; no todas las cohortes son el mismo MAIN.',
             'horizon':'Referencia de memoria relativa medida hasta100; ensemble hasta72. El lector tardío puede ser rechazado.',
             'NSM_mapping':None},
            {'id':'OPAQUE_NAME_SELECTED_CONTENT','mechanism':'Tras pregunta19, memoria propia70 y uso72, una señal opaca emparejada75 permite respuesta física142.',
             'evidence':'SELECTIVE','individual':'El mismo U0 por caso de selección; nombres emparejados, desacoplados y omitidos en cohortes diferenciadas.',
             'horizon':'Asociación75; consulta139 y respuesta142. No se verifica emisión espontánea situación→palabra ni sintaxis NSM.',
             'covered_records':selective['counts']['covered_opaque_sign_responses142'],
             'independent_preparations_with_response':selective['counts']['independent_preparations_with_covered_sign142'],
             'NSM_mapping':None},
            {'id':'CPC5_CAPACITY65_EXACT_TECHNICAL_REFERENCE','mechanism':'Sesenta y cinco formas opacas separadas en planos N131, emparejadas con dos clases direccionales; reproducción de fuente y configuración publicadas, no ampliación del MAIN integrado.',
             'evidence':'CAPACITY65_TECHNICAL','source_sha256':capacity_reference['same_source_as_published_CPC5'],
             'individual':'Dos preparaciones de referencia independientes del U0: historia publicada y control sin acontecimiento.',
             'horizon':'Lecturas134,265,396;65/65cubiertas por ronda en la historia emparejada, con consulta9. Control195/195rechazadas por ocupación.',
             'primary_observations':capacity_rows,'reproduction_not_new_generalization_claim':True,
             'control_interpretation':'La falta de consultas aplicadas es un resultado de admisión; no se convierte en respuesta física0 ni en prueba de todas las causas posibles.',
             'NSM_mapping':None},
            {'id':'U0_INTEGRATED_LOCAL_REVISION','mechanism':'La misma continuidad recibe una nueva consecuencia paraL03en402; una segunda ruta docente permite respuesta revisada en472 mientras otras13correspondencias conservan uso.',
             'evidence':'INTEGRATED_REVISION','individual':'Cuatro preparaciones nuevas: tratamiento, auxiliares fuera de ruta, guardas fuera de ruta y reserva. No son la continuación de los archivos de selección anteriores.',
             'horizon':'Pregunta19; banco propio70; acción72; señal opaca142; paneles204/338; experiencia de revisión402; panel472.',
             'treatment_and_reserve':['IR_P01_GUARDED_M1','IR_R607_GUARDED_M1'],
             'other13_retained_at472':True,'one_old_relation_replaced_not_both_contents_retained':True,
             'opaque_name_retention_after_revision402':'NO_CONSULTADA_EN_ESTE_PANEL',
             'control_scope':integrated_revision['integrated_update_contrast'],'NSM_mapping':None}
        ],
        'references':references,'entries':entries,
        'interpretation':'Las asociaciones locales HAY/NO del catálogo anterior se conservan como datos heredados. CPC7 aporta más correspondencias consultables, revisión local y una cadena de pregunta propia/uso/nueva asociación. Se documentan esos mecanismos positivamente sin reetiquetarlos como dominio de65primitivas.'}
    out=ROOT/'revision/NSM65_EVIDENCIAS.json';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    check=json.loads(out.read_text(encoding='utf-8'))
    lexical=('id','orden_tabla','glosa_inglesa_id','grupo_documental','forma_es','variantes_documentadas','forma_fuente','fuentes','normalizacion_editorial')
    assert len(check['entries'])==65 and all(all(a[k]==b[k] for k in lexical) for a,b in zip(check['entries'],old['entries']))
    assert all(a['historico']['dimensiones_independientes']==b['dimensiones_independientes'] for a,b in zip(check['entries'],old['entries']))
    print(json.dumps({'output':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'exact_lexical_inventory_and_historical_states':True,
                      'entries':65,'new_NSM_semantic_training_claims':0}))

if __name__=='__main__':main()
