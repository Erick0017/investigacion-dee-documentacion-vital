"""Generate exact analysis matrices from existing records only. Zero ticks."""
import json,hashlib,sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import recalcular_mi01 as audit
L=Path(__file__).resolve().parent;R=L.parents[2];S=R/'sistema';E=R/'evidencia/campanas/MENTE_DEE_INTEGRAL_MI01';O=L/'EXPORTACION_ANALISIS';O.mkdir(exist_ok=True)
calc=audit.calculate(E);(E/'CALCULOS_MI01_FINAL.json').write_text(json.dumps(calc,ensure_ascii=False,indent=2),encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text(x):return 'n/a'if x is None else str(x)
def record(life):return json.loads((S/'estado/vidas'/life/'VIDA.json').read_bytes())
def matrix(filename,headers,rows):return{'filename':filename,'headers':headers,'rows':[[text(x)for x in r]for r in rows]}

trials=[]
for p in sorted(E.glob('*.json')):
    if p.name.endswith('.PRE_REGISTRO.json'):continue
    d=json.loads(p.read_bytes())
    if not isinstance(d,dict)or'id'not in d:continue
    if'data'not in d and'returncode'not in d:continue
    v=audit.body(d);life=d.get('life');before=d.get('before',{}).get('physical',{});after=d.get('after',{}).get('physical',{})
    if not life:
        argv=d.get('argv',[])
        if'--vida'in argv:life=argv[argv.index('--vida')+1]
    kind='contraste de vida'if'data'in d else'operación del gestor'
    t0=before.get('tick');t1=after.get('tick')
    if isinstance(v,dict):
        t0=t0 if t0 is not None else(v.get('initial_native',v.get('initial',{})).get('tick')if isinstance(v.get('initial_native',v.get('initial',{})),dict)else None)
        t1=t1 if t1 is not None else d.get('result',{}).get('physical',v.get('physical',v.get('final_native',v.get('final',{})))).get('tick')
    error=d.get('error')or(d.get('result',{}).get('error')if d.get('returncode')else None)
    state='error instrumental o fuera de dominio; ver primario'if error or d.get('returncode',0)!=0 else'ejecutado; resultado físico, no PASS cognitivo'
    if isinstance(v,dict)and'rows'in v:description=str(len(v['rows']))+'filas físicas; no réplicas independientes'
    elif isinstance(v,dict)and'trajectory'in v:description=str(len(v['trajectory'].get('frames',[])))+'observaciones de trayectoria'
    else:description='fuente y controles localizados en el primario'
    trials.append([d['id'],life or'n/a',kind,t0,t1,state,description,p.name,sha(p)])

caps=[]
def cap(life,tick,function,mode,evidence,current,limit):caps.append([life,tick,function,mode,evidence,current,limit])
cap('E1_MI01_MAIN',21711,'tres códigos y mecanismos escalares heredados','herencia exacta, no adquisición nueva','INICIO_Y_PADRE;004panel','corte inicial','No hereda el futuro divergente21/21 de MAIN C2 ni65significados')
cap('E1_MI01_MAIN','operación100','composición selección Y y contenido Z','aprendizajes separados y combinación preparada','MI01_100_MAIN_COMPOSICION','uso nativo finito observado','El segundo uso103 falló; no composición reusable general')
cap('E1_MI01_MAIN',23453,'continuidad tras interferencia y pregunta fallida','misma biografía, sin reinicio','MI01_120-123','tres códigos anteriores todavía utilizables','Selector15 dejó de producir la pregunta prevista')
cap('E1_MI01_MAIN',23922,'petición material y recepción positiva145 de B','extensión40 preparada; contenido dependiente de experiencia','MI01_190-192','respuesta obtenida en su propia trayectoria','P0protección, P1historia; no detección aprendida general de falta de memoria')
cap('E1_MI01_MAIN',24190,'uso de tres códigos7 y positivo145','lector/actuador legado preparado','MI01_193_MAIN_UTILIZA','cuatro usos externos con los cuatro campos cualificados','No control aprendido de Pendulum ni posibilidad ilimitada de enseñanza')
cap('E1_MI01_MAIN',24420,'contacto y orden AB combinados nativamente','experiencias separadas; articulador fijo','MI01_310-314','31en unión y38en consecuencia','Operación consumptiva; no gramática o lenguaje libre')
cap('E1_MI01_MAIN',24525,'uso anterior después de contacto/orden','mismo cuerpo y puente','MI01_315_MAIN_RETENCION_EXTERNA','dos usos de los campos anteriores','No garantiza su conservación después del programa ampliado')
cap('E1_MI01_MAIN',24752,'reutilización del código positivo propio','acceso genérico P0 sin nuevo docente','MI01_320-321','+Y145 obtenido de materia adquirida','No recupera el valor privado20; negativa281falló; iniciativa del operador')
cap('E1_MI01_MAIN',24835,'solicitud iniciada por un producto de acción fallida','iniciación nativa en ventana preparada','MI01_411;423frames;350/351','XY-150 material, no callback de fracaso Python','Ley de transducción preparada; no una estrategia aprendida P2/R2')
cap('E1_MI01_MAIN',25005,'respuesta privada de B después de solicitud','B y conductos del mismo Runtime','MI01_411/473','respuesta +150 válida','No llegó como uso válido al selector; no se cuenta aprendizaje completo de ese mensaje')
cap('E1_MI01_MAIN',27834,'evaluación integrada fijada','9oportunidades,47pasos externos','MI01_411-413;SELLO_EVALUACION_FIJADA','1acción perjudicial,0contactos útiles,46neutrales externos','Los neutros son del puente; no una decisión aprendida de esperar')
cap('E1_MI01_MAIN',28169,'continuación real, estado adverso','guardar/cargar/entradas pendientes/puente','MI01_430-438;440','297240ocupados; cola0; accesos evaluados no disponibles','No borrado global probado; los originales y el pasado funcional se conservan')
cap('MI01_VARIACION_LIBRE_490',28236,'RAW estacionario durante67intervalos sin entrada','herramienta externa de observación','MI01_490','68muestreos,1hash RAW,clocks diferentes','Sólo ese horizonte/estado; no igualdad causal completa, muerte o estabilidad ilimitada')
for life,evidence in[('MI01_CONSULTA_110','110vs112/113/115'),('MI01_CONSULTA_111','111vs112/113/115')]:cap(life,'histórico de ensayo','solicitud por historia y respuesta privada','P0anatomía/P1contenido',evidence,'ambos signos recibidos en vidas separadas','No se suman como memorias simultáneas de MAIN')
for life in('MI01_PROTECCION_170','MI01_PROTECCION_171'):cap(life,'corte de ensayo','protección local y uso de signo recibido','P0eficaz con controles172/173',life,'3/3usos en cada rama','No implica regulación autónoma ni protección universal')
for life in('MI01_RETORNO_PROTEGIDO_210','MI01_RETORNO_PROTEGIDO_211'):cap(life,24015,'respuesta social cambia el siguiente código de decisión','transformación nativa P1 con rutas P0',life+';214corte/215sham','XY+145 oXY-145 según la vida','No política aprendida general ni selección de interlocutor')
cap('MI01_COMPARTIDO_270',24350,'producto de fracaso inicia pregunta posterior','P0turno/P1estado','270vs271/272/273','pregunta24031; segunda respuesta original falló','306prueba llegada aB; no sólo fallo de transporte')
cap('MI01_REUSO_280',24350,'reutilización de código positivo','P0genérico/P1contenido','280vs281/282/283','positivo recuperado; negativo no','Desvío de materia, no clonación ni recuerdo universal')
cap('MI01_CONTEXTO_B_344',24350,'respuesta B repetida para contenido bajo','referencia43 física fija P0, no aprendida','344vs341/343/347;348recibos','dos respuestas positivas y selector positivo','Parte de los apoyos0 solicitados se rechazó; especialización finita')
cap('MI01_ESPECIALIZACION_OPERATIVA_495',24484,'uso real por gestor de la especialización','bifurcación344,codec firmado fijo','495-499','1/3órdenes motoras no neutrales','Carga/guardado/recarga comprobados; no actuación sostenida')
cap('MI01_COALESCENCIA_476',25154,'restauración local de ruta tras interferencia188','interceptor externo P0 diagnóstico','476vs477;475','150localmente restaurado, pero S siguió fallando','No recuperación funcional extremo a extremo; no se promovió ni se importó aMAIN')
cap('E1_SOCIAL_11',3154,'predeterminado protegido anterior','estado histórico conservado','INICIO_Y_PADRE; comprobación de originales al cierre','no avanzado ni reemplazado','No adquiere las capacidades MI01 por figurar en la biblioteca')

assistance=[
['Selección de padre y vida','investigador','E1triple21711 elegido antes de resultados','no decisión deE1','INICIO_Y_PADRE'],
['Geometría de conductos','instrumento de preparación','calcula rutas y horarios admisibles antes de uso','no planificación de la tarea porE1','habitat_nativo.exact_route'],
['Extensión del soporte40','investigador','anatomía y cambio de lector durante construcción','no crecimiento anatómico aprendido','MAIN190;contratoMI01'],
['Oportunidades y reloj','entorno preparado','dos ventanas y9oportunidades335ticks','no iniciativa temporal general','SELLO_EVALUACION_FIJADA'],
['Contenido de selección','ente','cambia nativamente por experiencias','no escrito porPython ni importado desde un futuro','30-34;190-192'],
['Pregunta por producto de acción','ente bajo aparato P0','el producto físico habilita XY- en oportunidad común','no if falla entonces recupera enPython','270-274;MAIN411'],
['Información privada','B/entorno','magnitudes sólo ingresan por interfaces deB','B no es segunda mente completa','110/111;340-347'],
['Referencia43 de B','investigador','campo fijo y apoyos0 solicitados para comparación','no referencia aprendida; solicitudes no siempre aplicadas','348;contratoMI01'],
['Interceptores y shams','investigador','preparación/intervención física legal v27','no autorregulación ni limpieza automática','160-175;210-215;476/477'],
['Compilador de preparación','instrumento','deduplica únicamente paquetes físicamente idénticos','no selección de respuestas ni cambio de admisión','245;R4;input_compilation'],
['Codec sensorial','instrumento externo','seno cuantizado y límite de primera muestra por ranura','descarta coseno/velocidad; no calcula torque óptimo','externo_selector.run'],
['Actuador','puente externo','correspondencia fija de salida nativa a torque','neutral por código inválido no es decisión aprendida','411-413;450-452'],
['Consecuencia externa','entorno/codec','coste real vuelve al circuito escalar original','no actualización calculada del selector S','ic_external;externo_selector'],
['Español','traductor fijo','texto sólo para firmas físicas reconocidas','no gramática/LLM que complete el contenido','150-153;220-223'],
['Observación pasiva','auditor','registra campos sin entradas','no habilidad perceptiva deE1','470inocuidad exacta'],
['Métricas y clasificación','auditor','recalcula después de la trayectoria','no señal accesible que elija respuesta','recalcular_mi01.py'],
['Cambios de ventana','currículo ambiental','retardo y retiro de coste fijados antes de uso','no cambio aprendido de estrategia por horario','411-413;SELLO']]

evaluation=[]
for w in calc['frozen_windows']:evaluation.append(['externa','E1_MI01_MAIN',w['id'],w['last_tick'],w['steps'],w['positive_load_motor_outputs'],0,w['final_native']['occupied'],w['sensor_and_cost_requests'],w['receipt_statuses_at_window_end'].get('applied',0),sum(v for k,v in w['receipt_statuses_at_window_end'].items()if k.startswith('rejected')),w['reward_sum'],'recuentos al fin de ventana; pendientes no omitidos'])
for r in calc['frozen_native_opportunities']:evaluation.append(['nativa','E1_MI01_MAIN',r['index'],r['tick'],1,int(r['positive_load_act']or r['positive_load_question']),int(r['useful_contact']),'n/a','n/a','n/a','n/a',r['predefined_utility'],'disponibilidad'+str(r['availability'])+';carga'+str(r['native_command']['s_reg'])])
for k,z in calc['stress'].items():
    status=collections.Counter(r['receipt']['status']for r in z['shock_requests'])
    for stage in z['stages']:evaluation.append(['estrés nativo sin avanzar Pendulum',k,stage['tag'],stage['physical']['tick'],'n/a','n/a','n/a',stage['physical']['occupied'],len(z['shock_requests']),status.get('applied',0),sum(v for a,v in status.items()if a.startswith('rejected')),'n/a','pulso fijo; mismo prefijo completo en ambos brazos'])

tables=[matrix('ENSAYOS_Y_CONTROLES.csv',['ID','Vida','Unidad','Tick_inicio','Tick_fin','Estado_de_ejecucion','Cobertura_descriptiva','Fuente','SHA256_fuente'],trials),matrix('CAPACIDADES_POR_VIDA_Y_MOMENTO.csv',['Vida','Momento','Funcion','Atribucion','Evidencia','Estado_observado','Limite'],caps),matrix('FRONTERAS_DE_ASISTENCIA.csv',['Componente','Responsable','Funcion','No_demuestra','Fuente'],assistance),matrix('EVALUACION_FIJADA_Y_ESTRES.csv',['Tipo','Vida','ID','Tick','Oportunidades_o_pasos','Salidas_positivas_validas','Contactos_utiles','Ocupados','Solicitudes','Aplicadas','Rechazadas','Utilidad_o_recompensa','Nota'],evaluation)]
(L/'TABLAS_DATOS.json').write_text(json.dumps({'tables':tables,'native_ticks':0,'derived_values':'Recalculados desde primarios; las tablas selladas no alimentan respuestas de E1.','counts':{'trial_operation_rows':len(trials),'capability_moment_rows':len(caps),'assistance_rows':len(assistance),'evaluation_rows':len(evaluation)}},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'counts':[len(t['rows'])for t in tables],'classification_proposed':'capacidades adaptativas especializadas sin integración suficiente','final_main':record('E1_MI01_MAIN')['physical'],'native_ticks':0},ensure_ascii=False))
