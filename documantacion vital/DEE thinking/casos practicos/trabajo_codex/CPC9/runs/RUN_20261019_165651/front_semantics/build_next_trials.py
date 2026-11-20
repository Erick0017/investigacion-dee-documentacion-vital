"""Individual, bounded next contrasts justified by mechanisms actually read.

This is an auditor planning overlay, not experiences/answers loaded into DEE.
No item is called successful or feasible in E1 merely from sharing a family.
"""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

# readiness, native opportunity, decisive missing contrast, design/work estimate
# The estimates are prioritization estimates, not promises or scientific limits.
NEXT={
 'I':('EXPLORATORIO','Retorno causal propio y recibido con mismos efectos, no sólo calibración de magnitud','Necesita ligamiento material de acción propia con efecto; el piloto RP demuestra que firmas iguales no identificanactor',90),
 'YOU':('EXPLORATORIO','Ruta actual de destinatario y cambio real de emisor/receptor','Mismo signo con papeles invertidos y tercero distractor; no asignarYO/TUdesdepuertofijo',90),
 'SOMEONE':('BLOQUEO_DE_REPRESENTACION','Organizaciones con capacidades causales distintas y señales de igual aspecto','Adquirir clase de participante en ejemplar nuevo, separada de cualquier portador aislado',100),
 'SOMETHING':('BLOQUEO_DE_REPRESENTACION','Referencia material por continuidad de encuentros','Distinguir objeto continuado de copia igual y volver a utilizar una referencia variable',90),
 'PEOPLE':('PREPARACION_NUEVA','Presencia normalizada de varias fuentes con efectos y rutas distinguibles','Diferenciar varios participantes de una fuente de igual carga total; cardinalidadsola no basta',90),
 'BODY':('EXPLORATORIO','Dependencias de soporte causal propio y sensor de consecuencia interna','Aprender pertenencia funcional del soporte y separar bloqueo de lector de pérdida de soporte',90),
 'KINDS':('BLOQUEO_DE_REPRESENTACION','Múltiples ejemplares con función común y rasgos materiales variables','Generalizar función a ejemplar nuevo y excluir agrupación por un campo fijo',100),
 'PARTS':('PREPARACION_NUEVA','Retirada selectiva de soporte frente a ruta externa de igual aporte','Referencia adquirida parte-conjunto y uso ante sustitución parcial; no usar etiqueta delmódulo',75),
 'THIS':('EXPLORATORIO','Anclaje contextual por encuentro local frente a competidor','Referencia actual sin que hostseleccioneobjeto; permutar identidades',75),
 'THE_SAME':('BLOQUEO_DE_REPRESENTACION','Continuidad de un portador transformado frente a copia de igual RAW','Igual lectura y fuente distinta deben poder separarse por historia accesible; si no, declararindistinguibilidad',100),
 'OTHER':('BLOQUEO_DE_REPRESENTACION','Referente alternativo en contexto de dos continuidades','No bastaotroID: mantener relación al intercambiar señales y participantes',90),
 'ONE':('CONTRASTE_DIRIGIDO','COUNT_ACCESSv2 retiene señal; PNnormaliza dosis y PRretiene uncontacto con nuevos estados','No combinar mundos: demostrar en una nueva misma vida señal deuncontacto y uso dose-robusto',60),
 'TWO':('CONTRASTE_DIRIGIDO','COUNT_ACCESSv2 retiene señal; PNv3 conserva doscontactos bajo9parejas de dosis','Unir en una vida asociación posterior y funcionamiento dose-robusto sin perder otra relación',60),
 'SOME':('PREPARACION_NUEVA','Normalizar contribuciones materiales y conservar elegibles/completadas como dosoperandos','Subconjuntos diferentes deuniverso3/4; distinguir no vacío de uno y de todo',100),
 'ALL':('PREPARACION_NUEVA','Dosmemorias elegibles/completadas y comparación activa de igualdad','Cambiar número de oportunidades y omitir una; capacidad total debe proceder de experiencia no target externo',100),
 'MUCH_MANY':('PREPARACION_NUEVA','Magnitud adquirida o conteo normalizado frente a referencia contextual','Separar muchosobjetos de unobjetocargado; nuevas referencias y contextos',90),
 'LITTLE_FEW':('PREPARACION_NUEVA','Comparación nativa relativa conservada','Misma cantidad con marcos distintos y no confundir ausencia conpoco',90),
 'GOOD':('EXPLORATORIO','Consecuencia física conserva acceso en un contexto y lo perjudica en otro','La experiencia debe modificar selección futura según utilidad invertida, no sólo activar R14 preparado',110),
 'BAD':('EXPLORATORIO','Interferencia y posterior cambio de uso de corrientes','Historia opuesta de utilidad, misma dosis fuera de ruta, conservar percepción y acción',110),
 'BIG':('PREPARACION_NUEVA','Extensión física de soporte sensada por encuentros, no s_regrenombrado','Igual masa/carga con distinta extensión y unobjetogrande frente a variospequeños',110),
 'SMALL':('PREPARACION_NUEVA','Extensión relativa a marco material adquirido','Nueva escala y referente; no llamarpequeño a baja carga',110),
 'KNOW':('PREPARACION_NUEVA','Acceso remoto con referencia aprendida y retorno que modifica uso','Separar sinexperiencia, referencia conservada inaccesible, ausencia legítima y respuesta falsa; detector nativo explícito',75),
 'THINK':('CONTRASTE_DIRIGIDO','Dosmemorías adquiridas producen comparación nueva sin objeto reinjertado','Demuestra procesamiento interno limitado; no eleva aPENSARgeneral sin contraste funcional y señal propia',45),
 'WANT':('EXPLORATORIO','Selección de consecuencias modificada por historia material de utilidad','La política debe cambiar con utilidad, no sólo la dirección de una asociación preparada',120),
 'DONT_WANT':('EXPLORATORIO','Desvío aprendido de una corriente según consecuencias previas','Cambiar qué corriente perjudica y luego volver alcontextoanterior; silencio no es evitación',120),
 'FEEL':('BLOQUEO_DE_ATRIBUCION','Sensibilidad física a estados internos con efectos sobre acceso','Puede medirse sensibilidad funcional; no inferir experiencia subjetiva ni significado humano completo',75),
 'SEE':('BLOQUEO_DE_MODALIDAD','Canales materiales físicamente distintos, no sólo nombres de sensores','Necesita correspondencia operacional visual y adquisición nueva; unport no es visión',120),
 'HEAR':('BLOQUEO_DE_MODALIDAD','Recepción por estructura temporal/material distinta','Necesita segunda modalidad físicamente definida y transferencia cruzada; no renombrarprimera',120),
 'SAY':('CONTRASTE_DIRIGIDO','Emisión/recepción y asociación física con uso posterior en receptor','La comunicación ya puede medirse; aprender predicadoDECIR exige referencia a acto comunicativo frente a evento no comunicativo',60),
 'WORDS':('CONTRASTE_DIRIGIDO','Formas opacas adquiridas por encuentros y reutilizadas sin repetir situación','Permutar formas, variar contenidos, composición nueva; no equiparar repertorio de formas conpalabrasgenerales',60),
 'TRUE':('PREPARACION_NUEVA','Dosoperandos adquiridos pueden representar mensaje previo y acontecimiento posterior','Igualdad activa/contradicción deben surgir del encuentro, no bitTRUE anfitrión; nuevoscontenidos',75),
 'DO':('CONTRASTE_DIRIGIDO','Actuación nativa condicionada y entrega causal con controles','Separar acción propia, observación de evento y mismo efecto generado por otro; señal sólo trasfunción',60),
 'HAPPEN':('PREPARACION_NUEVA','Acontecimiento exógeno frente a consecuencia de intervención nativa','Mismo contenido y efecto con causa distinta accesible; no enviar la categoría causal correcta',70),
 'MOVE':('PREPARACION_NUEVA','Transporte físico nativo con accesos antes/después','Nuevos portadores y marco; contraste detenido con mismo recurso y señal posterior',60),
 'BE_SOMEWHERE':('PREPARACION_NUEVA','Sensor espacial de CPC8 y referencia adquirida','Localización relativa cambia función sin hostbuscarcoordenada; integrar requiere nuevaT0 y revalidación',80),
 'THERE_IS':('PREPARACION_NUEVA','Perfiles nativos de ausencia4.5 y detector material de presencia en ventana','Varios referentes y rutas; ocupado/tardío/desconocido no deben colapsar en ausencia',75),
 'BE_SOMEONE_SOMETHING':('BLOQUEO_DE_REPRESENTACION','Vínculo adquirido referencia-función y continuidad','Cambiar apariencia/papel, distinguir copia y actualización; no deducirSER de RAWigual',100),
 'IS_MINE':('BLOQUEO_DE_LIGAMIENTO','Acceso físico ligado a historia de adquisición de un soporte','Transferir soporte entre participantes y seguir posesión relativa sin diccionario de propietarios',110),
 'LIVE':('BLOQUEO_DE_ATRIBUCION','Continuidad funcional persistente y conservación de nuevas adquisiciones','Separar continuidad operacional de analogía biológica; no afirmar adquisición deVIVIR por guardarsnapshot',90),
 'DIE':('BLOQUEO_DE_ATRIBUCION','Pérdida persistente de función observada por otro con acceso alternativo','Distinguir pérdida global, bloqueo local y restauración; no inferir muerte por unpuertosilencioso',90),
 'WHEN_TIME':('PREPARACION_NUEVA','Intervalos/recurrencias relativos y memoria temporal','Consulta temporal sin transmitir tick objetivo, nuevoscomienzos y referentes',70),
 'NOW':('PREPARACION_NUEVA','Contexto físico actual encuentra memoria anterior','Cambiar inicio del episodio y separar actual de antiguo sin current_tickcomo respuesta',70),
 'BEFORE':('CONTRASTE_DIRIGIDO','Mecanismos ordenados heredados y reparaciones temporales actuales','Nuevos acontecimientos, orden e intervalos; no trasladar resultados de otroenteaE1',45),
 'AFTER':('CONTRASTE_DIRIGIDO','Orden no conmutativo con papeles realmente invertidos','Nuevaforma asociada a orden inverso en misma vida; no invertir textoANTES desdeauditor',50),
 'LONG_TIME':('PREPARACION_NUEVA','Retardos y encuentros respecto a referencia temporal adquirida','Orden igual con duraciones distintas, cambiar referencia; no tickclasificadoexternamente',90),
 'SHORT_TIME':('PREPARACION_NUEVA','Mismo mecanismo de duración con referencia y ventana explícitas','Separar corto de simultáneo y de ausencia; intervalos reservados',90),
 'FOR_SOME_TIME':('PREPARACION_NUEVA','Oportunidad persistente finita seguida de transición accesible','Variar duración/inicio sin convertir unintervalo fijo en significado general',90),
 'MOMENT':('PREPARACION_NUEVA','Encuentro puntual frente a oportunidad prolongada','Cambiar instante de comienzo y ancho de ventana; no repetir tickabsoluto',70),
 'WHERE_PLACE':('PREPARACION_NUEVA','Referencia espacial adquirida y rutas contextuales','Seleccionar retorno segúnreferencia sinquehostescojamemoria correcta; nuevo lugar y referente',90),
 'HERE':('PREPARACION_NUEVA','Anclaje físico alobservador, no origen absoluto','Mover observador y objeto por separado, marcos trasladados',90),
 'ABOVE':('PREPARACION_NUEVA','Referencia direccional adquirida y sensor espacial de mismo/opuesto lado','Invertir marco aprendido manteniendo elobjeto, no ejeZ=ARRIBA; luego forma posterior y reserva',100),
 'BELOW':('PREPARACION_NUEVA','Contraste opuesto del mismo marco direccional adquirido','Pruebaindependiente deARRIBA, cambiar marco y movimiento sin cambiar relación',100),
 'NEAR':('PREPARACION_NUEVA','Separación espacial accesible por encuentro/recorrido y marco adquirido','Rutas distintas con demoras controladas; no CPUni distancia auditada yaresuelta',100),
 'FAR':('PREPARACION_NUEVA','Referencia de separación contrastada con nueva geometría','Compensar demoras y variar recorrido/ref; no asumir que tiempo largo eslejos',100),
 'SIDE':('PREPARACION_NUEVA','Vecindad lateral relativa a orientación física','Intercambio de lados/marco con señal fija, no puerto lateral fijo',90),
 'INSIDE':('PREPARACION_NUEVA','Frontera material, conectividad y acceso a través de ella','Mismo objeto dentro/fuera, frontera abierta/cerrada e igual aporte material',110),
 'TOUCH':('CONTRASTE_DIRIGIDO','Contacto real y misma materia fuera de ruta, continuidad funcional','Atacar R32 y nuevos contactos sin reenseñar respuesta; distinguir huella física de acceso',45),
 'NOT':('PREPARACION_NUEVA','Gradiente nativo puede invertir formato direccional si el contenido ocupa±1respecto de unlector común','Operador activo sobre DOS contenidos aprendidos (orden/contacto), no cero/silencio; signo arbitrario debe seleccionar uso por experiencia',90),
 'MAYBE':('EXPLORATORIO','Evidencias incompatibles y oportunidad de acceso adicional','Distinguir incompleto, desconocido, fuente agotada y silencio; no inyectar incertidumbre calculada externamente',100),
 'CAN':('PREPARACION_NUEVA','Disponibilidad física de rutas/acciones que cambian consecuencias','Alternativas reales, cambiar disponibilidad conexperiencias y conservar función; no actuadorpresente=puedeaprendido',90),
 'BECAUSE':('PREPARACION_NUEVA','Intervención nativa seguida de efecto y memoria de relación','Separar causa alternativa/correlación con mismasobservacionesaccesibles; control causal externo no es comprensióncausal',90),
 'IF':('PREPARACION_NUEVA','Convergencia de dos estados adquiridos con una consecuencia física','Condición aprendida que cambia por historia y composiciónnueva, no sólo guardaR14preparada',90),
 'VERY':('PREPARACION_NUEVA','Magnitud/grado relativo a contexto adquirido','Separar intensidad de cantidad/recursos y usar contextos nuevos; no duplicarMÁS comoMUY',100),
 'MORE':('CONTRASTE_DIRIGIDO','Magnitud actual o dos operandos adquiridos y actualización por aporte real','Nuevosobjetos/referencias y signo aprendido después de función; comparación física preparada declarada',45),
 'LIKE_AS':('CONTRASTE_DIRIGIDO','MODE/referencia espacial adquirida con objetos nuevos','Cambiar rasgo/estado/identidad y mensaje; no confundir similitud de componente con identidad continuada',50)
}


def main():
    plan=json.loads((ROOT/'revision/NSM65_PLAN_CPC9.json').read_text(encoding='utf8'));assert set(NEXT)=={e['glosa_fuente']for e in plan['entries']}
    entries=[]
    for e in plan['entries']:
        readiness,mechanism,contrast,minutes=NEXT[e['glosa_fuente']]
        entries.append({'id':e['id'],'forma_es':e['forma_es'],'catalogue_sha256':e['catalogue_sha256'],
            'readiness':readiness,'native_opportunity':mechanism,'decisive_next_contrast':contrast,
            'estimated_design_and_check_minutes_not_promise':minutes,'individual_question':e['funcion_a_investigar'],
            'existing_vs_new':'Toda modificación de geometría/materia exige nueva preparación desdeT0; no insertar soporte ni memoria entrenada enMAIN.',
            'primary_scope':'Usar sólo datos de una continuidad declarada; los componentes de otrosmundos se conservan como auxiliares.',
            'nonpromotion':'Planificación individual, no prueba positiva. Contrastes compartidos no acreditan automáticamente varias primitivas.'})
    data={'schema':'CPC9.NSM65.remaining_native_opportunities.v1','count':65,
        'selection_advice':'En presupuesto restante priorizar pocos contrastes concluyentes de temporal/contacto, dosmemorias, cardinalidadnormalizada y una familia lógica activa. No repartirlo por65rótulos ni agotar en búsqueda de identidad sin ligamiento.',
        'estimates_rule':'Estimaciones pueden solaparse por familia, no se suman como cronograma ni demuestran viabilidad. No reinician presupuesto global.',
        'concrete_physics_leads':{'contact_count':'src/presence_count.py; src/presence_remote.py; resultados/PRESENCE_COUNT_* yPRESENCE_REMOTE_*',
            'two_acquired_operands':'src/two_memory.py; resultados/TWO_MEMORY_CONFIRMATORY',
            'identity_counterexample':'src/perspective_aux.py; resultados/REL_PERSPECTIVE_AUX_V1'},
        'entries':entries}
    p=ROOT/'revision/NSM65_ENSAYOS_JUSTIFICADOS_RESTANTES.json';p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'entries':len(entries),'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
