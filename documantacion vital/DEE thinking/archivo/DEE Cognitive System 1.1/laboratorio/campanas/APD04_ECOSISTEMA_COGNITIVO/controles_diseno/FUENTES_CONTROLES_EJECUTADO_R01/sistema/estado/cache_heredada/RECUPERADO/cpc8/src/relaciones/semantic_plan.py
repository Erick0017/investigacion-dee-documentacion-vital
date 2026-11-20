"""Exact documented65 inventory and independently testable CPC8 reconstruction dossiers.

This generator supplies evaluator criteria, never a participant's meaning map.
No resulting JSON is imported by native participants, sensors or decoders.
"""
import argparse,hashlib,json
from pathlib import Path
from zipfile import ZipFile

LEVELS={
 'E0':'No operacionalizada o no demostrada en esta realización.',
 'E1':'Asociación física dependiente de experiencia.',
 'E2':'Conservación y reutilización después de otras adquisiciones.',
 'E3':'Generalización a experiencias reservadas.',
 'E4':'Composición funcional no enseñada completamente.',
 'E5':'Comunicación y utilización por otro ente.'}
STATES=['Positiva','Parcial','Negativa válida','Indeterminada','Rechazada','Fuera de dominio','No ejecutada']

# Operational questions, not definitions declared to have been learned.
# Columns: candidate relation | actual experience | reserved variation.
PROPOSALS={
'I':('referente del emisor actual','cambiar qué participante emite conservando señal','intercambio de emisor y tercer distractor'),
'YOU':('destinatario actual distinto del emisor','dirigir mensajes a receptores alternos','nuevo interlocutor con mismo símbolo'),
'SOMEONE':('fuente con continuidad funcional de participante','acciones de cuerpos persistentes frente a portadores inertes','participantes con soporte diferente'),
'SOMETHING':('referente físico recuperable en una tarea','interacción con objetos de distintos soportes','nuevo objeto con consecuencias comparables'),
'PEOPLE':('conjunto de participantes operacionales','interacciones con varios individuos y roles cambiantes','cambiar miembros sin cambiar tarea colectiva'),
'BODY':('soporte organizado con continuidad funcional','perturbar o desplazar partes de un individuo','soporte diferente con función conservada'),
'KINDS':('clase funcional frente a apariencia compartida','varios ejemplos con igual consecuencia y controles visuales','miembro nuevo con rasgos distintos'),
'PARTS':('dependencia componente-conjunto','retirada selectiva, sham y rescate instrumentado','otro componente con papel comparable'),
'THIS':('referencia ostensiva de la interacción actual','señal local apunta a referentes alternos','nuevo referente y señal idéntica'),
'THE_SAME':('identidad funcional pese a transformación','seguir un referente con cambios frente a duplicado parecido','cambio de soporte y coincidencia espacial distractora'),
'OTHER':('referente distinto, no simple RAW diferente','consultar pares con identidad y rasgos cruzados','referentes nuevos con rasgos coincidentes'),
'ONE':('cardinalidad de un acontecimiento distinguible','un encuentro frente a dosis igual en varios encuentros','nuevo tipo de acontecimiento y distinta carga'),
'TWO':('cardinalidad dos sin bit externo de conteo','dos acontecimientos separados y control de dosis','intervalos y referentes nuevos'),
'SOME':('subconjunto no vacío en dominio finito','múltiples miembros con consecuencias locales','cambiar miembros y tamaño del dominio'),
'ALL':('cobertura de un dominio finito declarado','panel de miembros con contraejemplo localizado','nuevo dominio finito y orden de acceso'),
'MUCH_MANY':('cantidad relativa a referencia y contexto','variar número de acontecimientos manteniendo dosis total','nuevos valores a ambos lados de referencia'),
'LITTLE_FEW':('cantidad pequeña respecto a referencia','igualar carga y variar unidades independientes','cambiar referencia sin fijar un paquete como poco'),
'GOOD':('consecuencia favorable a función declarada','variar recursos, necesidad y acción posible','mismo paquete cambia de valor con contexto'),
'BAD':('consecuencia adversa a función declarada','consecuencias limitadas con alternativa y sham','otro contexto invierte valoración'),
'BIG':('extensión del referente en marco operacional','variar geometría manteniendo inventario cuando sea viable','referentes de otra clase con extensión comparable'),
'SMALL':('menor extensión sin usar carga como definición','cambios de soporte y controles de inventario','nuevo marco y objetos'),
'KNOW':('información accesible y utilizable por participante','historias privadas, consultas y contraste causal','nuevo problema que requiere esa información'),
'THINK':('estado predictivo operativo antes del resultado','emisión previa con horizonte y contraste posterior','predicción nueva con error posible'),
'WANT':('selección persistente relativa a oportunidades','acciones alternativas y consecuencias de contexto','invertir disponibilidad y coste'),
'DONT_WANT':('evitación selectiva relativa a consecuencias','misma oportunidad con historias y necesidades distintas','relevancia invertida, sin inferir vivencia subjetiva'),
'FEEL':('sensibilidad interna operacional explícita','perturbaciones limitadas y vías sensoriales declaradas','distintos cambios con efectos comparables; no fenomenología'),
'SEE':('acceso a una modalidad sensorial declarada','rutas presentes y bloqueadas, con otros sensores intactos','nuevo referente y aislamiento de señales laterales'),
'HEAR':('acceso temporal a señales de otra fuente','mensajes secuenciales mediante sensor declarado','fuente nueva y cambio de modalidad; analogía no asumida'),
'SAY':('emisión comunicativa dependiente de experiencia','emisor con historia privada y receptor que utiliza mensaje','otro contenido, canal cortado y receptor virgen'),
'WORDS':('formas comunicativas con uso adquirido','señales opacas vinculadas después de función nativa','forma nueva, etiquetas intercambiadas y uso reservado'),
'TRUE':('correspondencia de una emisión con consecuencia','predicciones emitidas antes de medir el objetivo','contenidos distintos, incluyendo error y ambigüedad'),
'DO':('contribución causal de una acción propia','acción nativa frente a omisión y replay desacoplado','otro actuador con misma función causal'),
'HAPPEN':('acontecimiento observado distinto de acción propia','eventos externos y efectos de actuadores','cambiar el origen manteniendo observables locales'),
'MOVE':('desplazamiento con identidad operacional conservada','trayectorias y transformaciones nativas','otro portador, ruta y marco; no mover arrays'),
'BE_SOMEWHERE':('localización en marco declarado','interacciones de un referente con accesos locales','trasladar referente y marco por separado'),
'THERE_IS':('presencia accesible de varios referentes','encuentros positivos y ventanas de ausencia explícitas','referente nuevo y otro acceso, no sóloR3'),
'BE_SOMEONE_SOMETHING':('atribución de identidad o función a referente','ejemplos con transformaciones y distractores','nuevo soporte que preserva función'),
'IS_MINE':('relación de acceso entre participante y recurso','intercambiar poseedor y oportunidades de acceso','nuevo recurso e intercambio de participantes'),
'LIVE':('continuidad operacional sostenida','periodos de conservación y consumo con recursos finitos','otro soporte con continuidad comparable; no vida biológica'),
'DIE':('pérdida operacional irreversible en horizonte declarado','cortes acotados, recuperación y controles de acceso','distinguir fallo del lector de pérdida funcional'),
'WHEN_TIME':('referencia temporal entre acontecimientos','eventos locales sin calendario que revele respuesta','otro orden e intervalos'),
'NOW':('presente de una interacción local','consultas con estados que cambian y referencia accesible','otro participante con reloj operacional propio'),
'BEFORE':('R(A,B) cambia al invertir acontecimientos','presentarA/B en ambos órdenes, nunca bit de orden','nuevos estados sensoriales e intervalos'),
'AFTER':('relación inversa conservando participantes','mismos acontecimientos con papeles de consulta invertidos','nuevos referentes e intervalos'),
'LONG_TIME':('duración relativa a referencia física','intervalos entre contactos sin enseñar número de ticks','otra cadencia y acontecimientos'),
'SHORT_TIME':('intervalo corto respecto a referencia','duraciones con igualdad de dosis y orden','cambiar referencia temporal'),
'FOR_SOME_TIME':('persistencia durante intervalo acotado','espera sin entradas y uso posterior','otro horizonte sin reenseñanza'),
'MOMENT':('coincidencia en una ventana operacional','encuentros simultáneos y pequeños desfases','otros acontecimientos y otra ventana justificada'),
'WHERE_PLACE':('pregunta por ubicación con acceso utilizable','rutas y referentes en marcos físicos','nuevo referente y posición relativa'),
'HERE':('lugar relativo al interlocutor actual','cambiar origen de consulta y conservar relación','otro emisor y marco desplazado'),
'ABOVE':('relación espacial con marco explícito','intercambiar posiciones y referentes','nuevo objeto y marco orientado; no gravedad universal asumida'),
'BELOW':('inversa espacial en marco declarado','mismos objetos con inversión de roles','referentes distintos y cambio de marco'),
'NEAR':('acceso local o recorrido corto relativo','comparar encuentros con rutas y velocidades controladas','otro contexto, periodicidad toroidal explícita'),
'FAR':('mayor separación operacional','cambios de ruta y distancia medidos por separado','otro modo de transporte sin confundir espera con distancia'),
'SIDE':('lateralidad relativa a referencia','intercambiar lados con mismos referentes','nuevo marco y espejo controlado'),
'INSIDE':('pertenencia a región o estructura funcional','cruzar límites y cambiar acceso','otro límite sin bit externo de pertenencia'),
'TOUCH':('contacto causal nativo distinto de cercanía','pre/post encuentro y sham próximo','otro par; Moore26 no implica por sí solo contacto'),
'NOT':('negación operacional aplicable a varios contenidos','ausencias y opuestos con detector y ventana explícitos','contenido nuevo, no sólo ausencia de un puerto'),
'MAYBE':('clase de posibilidades por información insuficiente','estados indistinguibles por acceso actual y consulta extra','nuevo par de posibilidades sin confianza inventada'),
'CAN':('disponibilidad de una función o acción','oportunidades, rutas bloqueadas y actuador conservado','otra oportunidad con mismo mecanismo'),
'BECAUSE':('dependencia causal comprobada','intervenciones dirigidas con sham y rescate','nueva consecuencia; explicación externa rotulada'),
'IF':('uso condicionado por contexto accesible','mismo contenido cambia efecto por contexto físico','combinación contenido-contexto no enseñada completa'),
'VERY':('intensidad relativa en familia definida','varios grados y controles de cantidad e inventario','nuevo referente con escala justificada'),
'MORE':('comparación diferencial no mera carga final','pares con referencias y representaciones cambiantes','nueva referencia y valores no enseñados'),
'LIKE_AS':('similitud funcional dentro de tarea','rasgos iguales con función distinta y viceversa','referente nuevo, métrica congelada')}


GROUPS={
 'participantes':{'I','YOU','SOMEONE','PEOPLE','BODY','IS_MINE','SAY','WORDS','HEAR'},
 'referencia_identidad':{'SOMETHING','KINDS','PARTS','THIS','THE_SAME','OTHER','BE_SOMEONE_SOMETHING','LIKE_AS'},
 'cantidad_comparacion':{'ONE','TWO','SOME','ALL','MUCH_MANY','LITTLE_FEW','BIG','SMALL','VERY','MORE'},
 'accion_contexto':{'GOOD','BAD','WANT','DONT_WANT','DO','HAPPEN','LIVE','DIE','CAN','BECAUSE','IF','TOUCH'},
 'informacion':{'KNOW','THINK','FEEL','SEE','TRUE','NOT','MAYBE'},
 'tiempo':{'WHEN_TIME','NOW','BEFORE','AFTER','LONG_TIME','SHORT_TIME','FOR_SOME_TIME','MOMENT'},
 'espacio':{'MOVE','BE_SOMEWHERE','THERE_IS','WHERE_PLACE','HERE','ABOVE','BELOW','NEAR','FAR','SIDE','INSIDE'}
}
LOCAL_BLOCKERS={
 'participantes':'Falta una unión física reutilizable de emisor/destinatario/participante que cambie de papel; IDs del investigador no la suministran.',
 'referencia_identidad':'Falta demostrar referencia o clase funcional conservada ante transformaciones y distractores; igualdad de dirección no acredita identidad de referente.',
 'cantidad_comparacion':'Falta representación de unidades independientes y referencia comparativa; una carga agregada puede confundir cantidad, dosis y soporte.',
 'accion_contexto':'Falta conservar y usar la dependencia causal específica entre acción, contexto y consecuencia más allá del aparato preparado.',
 'informacion':'Falta una salida nativa sobre información accesible/insuficiente con detector definido; un juicio del auditor no puede sustituirla.',
 'tiempo':'Falta reutilizar la relación temporal con nuevos acontecimientos e intervalos en el mismo individuo; un reloj global o bit de orden externo la resolvería gratuitamente.',
 'espacio':'Falta referencia espacial física conservada y acceso con nuevos referentes; coordenadas del auditor no son percepción del participante.'
}
def family(key):
    matches=[name for name,keys in GROUPS.items() if key in keys]
    if len(matches)!=1:raise ValueError('Every prime needs exactly one shared mechanism family: '+key)
    return matches[0]
def blocker(key,op,reserve):
    return {'mechanism_gap':LOCAL_BLOCKERS[family(key)],'exact_missing_trial':reserve,'candidate_scope':op,'status':'No ejecutada en esta reconstrucción; no incapacidad universal'}

def build(wheel,out,revision):
    digest=hashlib.sha256(wheel.read_bytes()).hexdigest()
    if digest!='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c':raise ValueError('Wrong official4.5wheel')
    member='dee_thinking/data/NSM65_CATALOGO_HISTORICO.json'
    with ZipFile(wheel) as z:data=z.read(member)
    h=hashlib.sha256(data).hexdigest()
    if h!='e0f29290d800a74150b7e386fe2437dcc92b99bbd587b6cfef8e38c80067ae7e':raise ValueError('Catalogue cut differs')
    catalogue=json.loads(data);assert len(catalogue['entries'])==65
    rows=[]
    for original in catalogue['entries']:
        key=original['id'].split('.',1)[1];op,exposure,reserve=PROPOSALS[key]
        rows.append({'operational_question':'¿La experiencia de '+exposure+' permite utilizar '+op+' ante '+reserve+', sin nueva enseñanza ni acceso al target?', 'shared_mechanism_family':family(key), 'concrete_local_blocker':blocker(key,op,reserve), 'new_MAIN_evidence_inherited':False, 'id':original['id'],'forma_es':original['forma_es'],'variantes':original['variantes_documentadas'],
            'fuentes':original['fuentes'],'documentary_registration':True,'current_CPC8R_level':'E0',
            'operational_candidate':op,'participants_and_relation':'Explicit referents, roles, context and time must be preserved; not reconstructed by renderer',
            'experiences_before_label':exposure,'physical_signal':'Not assigned by catalogue; assign fixed opaque physical cue only in a frozen executed configuration',
            'preparation_vs_acquisition':'Preparation may provide sensors/routes/readers; the asserted relation must differ through admitted history',
            'retention_test':'Fresh physical query after another acquisition and a no-input wait, without re-teaching the earlier answer',
            'reserved_generalization':reserve,'communicative_use':'Message must depend on sender experience, travel inside shared Runtime and alter recipient use',
            'composition_test':'Teach constituent relations separately; reserve a complete combination, role inversion and context change',
            'minimal_controls':['same interface/opposite history','unpaired experience','no pertinent experience','memory/access selective cut','physical sham','perception/actuator control'],
            'levels':{level:{'definition':definition,'state':'No ejecutada','evidence':[],'scope':None} for level,definition in LEVELS.items()},
            'historical_dimensions_retained_separately':{'scope':'Historical catalogue only; never evidence of this reconstruction MAIN','dimensions':original['dimensiones_independientes']},
            'semantic_equivalence_to_full_human_prime_demonstrated':False})
    assert len(rows)==65 and len({x['id'] for x in rows})==65 and set(PROPOSALS)=={x['id'].split('.',1)[1] for x in rows}
    out.mkdir(parents=True,exist_ok=True);(out/'NSM65_CATALOGO_4_5.json').write_bytes(data)
    revision.parent.mkdir(parents=True,exist_ok=True)
    result={'schema':'CPC8R.NSM65.dossiers.v1','kind':'AUDITOR_CRITERIA_NOT_PARTICIPANT_MEMORY','count':65,
        'source':{'wheel':wheel.name,'wheel_sha256':digest,'member':member,'catalogue_sha256':h,'sources':catalogue['sources']},
        'levels':LEVELS,'allowed_trial_states':STATES,'current_executed_semantic_claims':0,'entries':rows,
        'scope':'All65 have operational dossiers, not65 learned meanings. Every level starts unexecuted for this reconstruction; historical positives are provenance, not inherited MAIN abilities.'}
    revision.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'dossiers':65,'source_sha256':h,'new_semantic_claims':0}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--wheel',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--revision',type=Path,required=True)
    a=p.parse_args();build(a.wheel,a.out,a.revision)
