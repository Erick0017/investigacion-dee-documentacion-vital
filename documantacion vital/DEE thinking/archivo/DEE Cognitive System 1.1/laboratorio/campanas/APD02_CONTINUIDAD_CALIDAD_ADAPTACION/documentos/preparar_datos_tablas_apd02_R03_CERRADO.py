"""Closed-source scalar table data, not CSV authoring and no native imports."""
import argparse,hashlib,json
from pathlib import Path
LAB=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    if a.salida.exists():raise FileExistsError('Preserve earlier table candidate')
    paths={
        'REPERTORIO':'../../../evidencia/campanas/APD02_CONTINUIDAD_CALIDAD_ADAPTACION/RECALCULO_REPERTORIO_R01.json',
        'CADENA':'cierre/MAIN_CADENA_APD02_R03/REFERENCIA_CADENA_MAIN.json',
        'CALIDAD':'cierre/MAIN_CALIDAD_COMPOSICION_APD02_R03/REFERENCIA_CALIDAD_COMPOSICION_MAIN.json',
        'R03_ADVERSO':'cierre/MAIN_RUTA_ABAB_APD02_R03/REFERENCIA_RUTA_ABAB.json',
        'R04_MAIN':'cierre/MAIN_RUTA04_APD02_R01/REFERENCIA_RUTA04_MAIN.json',
        'ACUM_LEX':'cierre/ACUMULADOR_Y_AUTOPSIA_LEXICA_R02/MANIFIESTO.json',
        'LEX_AUTOPSIA':'lenguaje/RESULTADOS_CONSULTA_R02.md',
        'GOAL_AUX':'cierre/OBJETIVO_ACLARACION_AUX_R03/REFERENCIA_OBJETIVO_R03.json',
        'GOAL_MAIN':'cierre/MAIN_OBJETIVO_PENDIENTE_Y_REAPERTURA_R01/REFERENCIA_MAIN_OBJETIVO_R02.json',
        'R04_AUX':'mecanismo/CIERRE_MECANISMO_APD02_R01/INFORME_MECANISMO_APD02.md',
        'R04_CUT':'mecanismo/CIERRE_CORTE_R04_R01/MANIFIESTO.json',
        'POLITICAS':'mecanismo/POLITICAS_R04_R3/REFERENCIA.json',
        'POLITICAS_TEXTO':'mecanismo/COMPARACION_POLITICAS_R04.md',
        'CALIDAD_PURA':'cierre/CALIDAD_APD02_R04/MANIFIESTO.json',
        'CONTEXTO':'mecanismo/contexto/CIERRE_CONTEXTO_R01/REFERENCIA.json',
        'CONTEXTO_INFORME':'mecanismo/contexto/CIERRE_CONTEXTO_R01/INFORME_CONTEXTO_SENSORIAL.md',
        'CONTEXTO_MANIFIESTO':'mecanismo/contexto/CIERRE_CONTEXTO_R01/MANIFIESTO.json',
        'CONTINUIDAD_EN_CURSO':'CONTINUIDAD_EN_CURSO_APD02.json'}
    # Resolve the two evidence references explicitly; all others are LAB-local.
    root=LAB.parents[2]
    resolved={key:(root/'evidencia/campanas/APD02_CONTINUIDAD_CALIDAD_ADAPTACION/RECALCULO_REPERTORIO_R01.json'if key=='REPERTORIO'else LAB/rel)for key,rel in paths.items()}
    for key,f in resolved.items():
        if not f.is_file():raise FileNotFoundError(str(key)+': '+str(f))
    source_index={k:{'localizador':str(f.relative_to(root)).replace('\\','/'),'sha256':sha(f),'bytes':f.stat().st_size}for k,f in resolved.items()}
    chain=read(resolved['CADENA']);qc=read(resolved['CALIDAD']);r3=read(resolved['R03_ADVERSO']);r4=read(resolved['R04_MAIN']);goal=read(resolved['GOAL_MAIN'])
    cap=[]
    def capability(key,life,moment,function,result,num,den,unit,assistance,limit,cite):
        cap.append(dict(id=key,vida_expediente=life,momento=moment,funcion=function,resultado=result,numerador=num,denominador=den,unidad=unit,asistencia=assistance,limite=limit,fuentes=cite))
    capability('C01','APD02_BASELINE','T361114–T366179','Panel MA de memorias contextuales','Signos históricos − − + − − +',6,6,'contextos MA','Consultas y lector preparados','No es el panel de formas léxicas alfa…zeta; no suma capacidades MAIN','REPERTORIO#/baseline/old')
    capability('C02','APD02_BASELINE','T361114–T366179','Seis formas españolas heredadas','suma diferencia agrega resta total quita con número y archivo correctos',6,6,'formas con tarea','Codec y aritmética preparados','Baseline diagnóstico, no MAIN ni nuevos aprendizajes','REPERTORIO#/baseline/forms')
    capability('C03','APD02_MAIN','MAIN_CADENA_R01 cerrado','Dos asociaciones funcionales nuevas','compara→comparación actual; recuerda→consulta',2,2,'usos funcionales','Docencia explícita; signo→interacción preparado; contexto operador','No producción de español ni dos operaciones numéricas nuevas','CADENA#/new_language')
    capability('C04','APD02_MAIN','MAIN_CADENA_R01 cerrado','Calidad del número utilizado y escrito','Ocho de nueve números utilizados o en archivo corresponden a la petición original',chain['APD_quality']['numeric_correct_original_request'],chain['APD_quality']['requested'],'solicitudes APD','Verificación posterior externa','En el badcase DEE dio 15 antes del fault; la perturbación produjo 16 utilizado y escrito. No es 8/9 cálculos nativos antes del fault.','CADENA#/APD_quality; CADENA#/APD_quality/cases')
    capability('C05','APD02_MAIN','MAIN_CADENA_R01 cerrado','Acumulación renovada','Ocho incrementos secuenciales, sin reset del cursor',8,8,'usos de acumulación','Renovación física y calendario P0','No suma binaria general ni inicio autónomo','CADENA#/recirculating_accumulator')
    capability('C06','APD02_MAIN R03 adverso','T370673–T391957','Ruta física','Doce formas emitieron, pero no hubo ruta válida',0,12,'solicitudes de ruta','Preparación R03 incompatible en un puerto omitido','No se ejecutó ningún proveedor; futuro negativo preservado','R03_ADVERSO#/APD; R03_ADVERSO#/blocker')
    capability('C07','APD02_MAIN R04','T391957–T413062','Cálculo y archivo seleccionado','Doce números y archivos correctos',12,12,'tareas APD','Anatomía R04 y proveedor único preparados','No implica cumplimiento de recursos','R04_MAIN#/APD')
    capability('C08','APD02_MAIN R04','A3 B2 A4 B3','Utilidad bajo coste','Ocho dentro de presupuesto; cuatro RESOURCE_LIMIT',8,12,'tareas APD','Ley externa de precios y categoría común','Coste 28 modelado, no CPU; no política general','R04_MAIN#/APD; POLITICAS_TEXTO')
    capability('C09','APD02_R04_ACTUAL_real','T391957–T407640','Uso y utilidad auxiliar','Ocho cifras y archivos, cuatro dentro de presupuesto',4,8,'tareas útiles AUX','Preparación R04; consecuencia de acción real','Coste24; historia distinta de MAIN; no trasplante','R04_AUX; POLITICAS_TEXTO')
    capability('C10','APD02_MAIN','MAIN_CALIDAD_Y_COMPOSICION_R01','Operador pertinente','Concordancia con petición original',qc['APD_primitives']['all']['semantic_correct'],18,'oportunidades primitivas','Docencia y evaluador privado posterior','Un operador equivocado dejó archivo real incorrecto','CALIDAD#/APD_primitives/all')
    capability('C11','APD02_MAIN','MAIN_CALIDAD_Y_COMPOSICION_R01','Número del proveedor','Correcto según operación original',17,18,'números antes de efecto','Aritmética nativa o proveedor externo explícito','Incluye18 correcto sin archivo; no17 entregas correctas','CALIDAD#/APD_primitives/all/provider_number_correct_original_request')
    capability('C12','APD02_MAIN','MAIN_CALIDAD_Y_COMPOSICION_R01','Presencia y validez de archivo','Archivo real válido como archivo',17,18,'efectos','Escritura y lectura posterior sintéticas','Incluye archivo con9 para agrega[13,4], semánticamente incorrecto','CALIDAD#/APD_primitives/all/valid_real_files')
    capability('C13','APD02_MAIN','MAIN_CALIDAD_Y_COMPOSICION_R01','Número en archivo y entrega','Correcto y dentro de límites',16,18,'oportunidades primitivas','Evaluación posterior común','Un SEMANTIC_ERROR y un FILESYSTEM_ERROR; contenedor no suma otra tarea','CALIDAD#/APD_primitives/all')
    capability('C14','APD02_MAIN','T432909 lector C','Agregación de 128 componentes crudos','Agregado nativo 64 y selección +',1,1,'trama conjunta de 128 componentes','Árbol y codec preparados; referencia adquirida','No son 128 conceptos ni relevancia individual nueva en APD02','CALIDAD#/raw128')
    capability('C15','APD02_MAIN','MAIN_CALIDAD_Y_COMPOSICION_R01','Composición de tres etapas','Resultado11 con efectos intermedios reales',3,3,'etapas comprometidas','Orden suma resta total suministrado','No plan aprendido ni gramática general','CALIDAD#/assisted_composition')
    capability('C16','Cuatro AUX GOAL','OBJETIVO_NATIVO_R03 cerrado','Objetivo consultable','Tres metas con archivo; omit conserva cuatro QUERY sin archivo',3,4,'mundos dependientes','Codec ACT/QUERY, oportunidades y parada P0','Visible también preguntó; no percepción semántica de ausencia','GOAL_AUX')
    capability('C17','APD02_MAIN','T443018–T454808','Objetivos en orden variable','11 por QUERY→ACT; 13 por ACT; 14 por ACT fallido→QUERY→ACT',3,3,'objetivos; seis oportunidades','Mapa de acciones, ley de consecuencia y parada preparados','Cuatro fragmentos no son cuatro objetivos; no planner','GOAL_MAIN#/goal_results')
    capability('C18','APD02_MAIN','Cambio PID 90468→92020','Continuación pendiente','Mismo ID, secuencia 1629, payload y llegada; sin requeue',1,1,'petición pendiente','Cola y propietario de servicio externos','Contador 1→2 en QUERY y final 3 tras ACT; epoch 6 abierto','GOAL_MAIN#/cross_process; GOAL_MAIN#/transport')
    capability('C19','APD02_MAIN','Después de pending completado','Nueva entrada y retención','suma [0,32]→32; MA old6 conservado',6,6,'memorias MA posteriores','Consultas materiales seleccionadas por operador','Separado del panel léxico de 14 formas; no son 20 facultades','GOAL_MAIN#/other_functions')
    capability('C20','APD02_MAIN','Después de objetivos','Acumulación con demora','Incremento 0, tres períodos→45; cursor 15→16',1,1,'uso de acumulación','Renovación P0 solicitada','Sin reset ni nueva docencia; no mantenimiento autónomo','GOAL_MAIN#/other_functions')
    capability('C21','RESERVA_CONTINUA_60M_R01','VIVA al preparar datos','Continuidad larga','PENDIENTE_INCORPORAR_CORTE_REAL','N/A','N/A','no resultado todavía','42eventos prospectivos','No acreditar hora,42eventos,beta ni estadofinal','CONTINUIDAD_EN_CURSO')
    capability('C22','Distribución actual','Pendiente','Full y Word1.16','PENDIENTE_INCORPORAR_CORTE_REAL','N/A','N/A','no probado todavía','Root realizará cierre y pruebas','No heredar prueba de FullAPD01 ni anticipar DOCX','CONTINUIDAD_EN_CURSO')
    capability('C23','AUX contexto lateral','CIERRE_CONTEXTO_R01','Sensibilidad material inicial','Bits públicos 0 y 1 produjeron respectivamente − y 0 en las primeras entradas',2,2,'primeras lecturas por historia','Canal sensorial y lector fijo preparados','El sensor permaneció ocupado; las dos entradas siguientes se rechazaron. No es mecanismo reutilizable ni aprendizaje de ausencia.','CONTEXTO; CONTEXTO_INFORME')
    capability('C24','AUX contexto superior FI01','CIERRE_CONTEXTO_R01','Sensor reutilizable con salida parcial','Cuatro bits aplicados: bit 0 produjo −; bit 1 dejó el lector sin salida',2,4,'emisiones válidas tras entradas aplicadas','Sensor superior y seis puertas fijadas antes de datos','Para bit 1 no hubo QUERY utilizable; no se seleccionó otro lector después.','CONTEXTO; CONTEXTO_INFORME')
    capability('C25','Cuatro AUX contexto','CIERRE_CONTEXTO_R01','Admisión sensorial total','Ocho consultas, seis entradas sensoriales aplicadas y dos rechazadas',6,8,'entradas sensoriales','Bit público ausente/presente, no acción correcta ni b privado','Dos respuestas posteriores a rechazo no acreditan uso del bit nuevo. No se ejecutó tarea ambiental.','CONTEXTO; CONTEXTO_MANIFIESTO')
    capability('C26','ROI retrospectiva','Pendiente de revisión del agente','Observación externa N0','PENDIENTE_INCORPORAR_ANALISIS_ROI','N/A','N/A','sin capacidad funcional atribuida','Herramienta del auditor, cero ticks','Una diferencia regional no acredita recuperación ni uso nativo.','CONTEXTO_INFORME')
    fronts=[]
    def front(name,state,coverage,result,untested,cites):fronts.append(dict(frente=name,estado=state,cobertura=coverage,resultado=result,no_probado=untested,fuentes=cites))
    # Each row is a separate evidential domain; no aggregate cognitive score.
    front('Continuidad biográfica','CLOSED','N = 67; padre ASISTENTE_MAIN T361114; descendiente MAIN T454808','Memoria y hechos ambientales continuados sin T0','Estado posterior de reserva y promoción global','GOAL_MAIN; CONTINUIDAD_EN_CURSO')
    front('Lenguaje funcional','CLOSED_LIMITADO','Seis bifurcaciones R01; dos formas nuevas; lector común de 28 puertas','Correspondencias opuestas cambian función','Español libre, sintaxis y nuevas primitivas NSM65','REPERTORIO#/language; CADENA#/new_language')
    front('Conteo de repertorio','CLOSED_ALCANCE','Catorce formas léxicas: seis nombres alfa…zeta y ocho españolas; panel MA de seis contextos separado','No sumar 6 + 14 como conocimientos independientes','Catorce facultades distintas o 65 significados','REPERTORIO; CADENA; GOAL_MAIN')
    front('Historia A y B','CLOSED_NEGATIVO','Factorial de cuatro mundos: no consulta, sólo B, sólo A, A→B','A→B conserva 9/12; los otros conservan 12/12','Borrado global, linaje único o causa de resta resuelta','ACUM_LEX; LEX_AUTOPSIA')
    front('Renovación acumulador','CLOSED_LIMITADO','Siete casos R01/R02; contenidos opuestos; omisión, sham y demoras','Usos posteriores al quinto sin reset; MAIN continúa','Suma binaria general, metabolismo, R2 o iniciativa','ACUM_LEX; CADENA; GOAL_MAIN')
    front('Calidad postacción','CLOSED','Pruebas puras R04 y dos ventanas MAIN; operador, número, archivo y recursos separados','Errores numérico, semántico y de archivo conservados','Corrección online como facultad interna o seguridad OS','CALIDAD_PURA; CADENA#/APD_quality; CALIDAD#/APD_primitives')
    front('Interfaz adversa R03','CLOSED_NEGATIVO','Doce no response y doce rechazos; puerto con state 0 y RAW no nulo','Preflight omitió un requisito bloqueado','Que sea la única causa o que quitarlo sea solución suficiente','R03_ADVERSO#/blocker')
    front('Selección por consecuencia R04','CLOSED_LOCAL','Doce tareas MAIN, ocho AUX; omisión, sham, desfase y corte del producto formado','El cambio depende de la consecuencia de la acción propia','Política desde cero, calendario autónomo o R2 general','R04_MAIN; R04_AUX; R04_CUT')
    front('Referencias de políticas','CLOSED_ANALITICO','MAIN A3/B2/A4/B3 y AUX A2/B3/A1/B2','MAIN coste 28 y 8 útiles; AUX coste 24 y 4 útiles; coincide con WSLS','Políticas no ejecutadas contra DEE; ahorro general de CPU no medido','POLITICAS; POLITICAS_TEXTO')
    front('Composición y crudos128','CLOSED_PREPARADO','Una trama de 128 componentes→64; tres etapas→11','Agregado, efectos reales y referencia utilizados','128 conceptos, planificador o invención de herramienta','CALIDAD#/raw128; CALIDAD#/assisted_composition')
    front('Objetivo y aclaración','CLOSED_LOCAL','Cuatro AUX y tres objetivos MAIN en seis oportunidades','QUERY revela b real y ACT usa el dato observado','Sensor nativo de missing o planificación semántica','GOAL_AUX; GOAL_MAIN#/goal_results')
    front('Pending entre procesos','CLOSED','Un ID admitido una vez; mismo SHA completo; dos PID','Contador 1→2→3; entrada nueva después de completar pendiente','No se ejecutó importación del backup con fila processing','GOAL_MAIN#/cross_process; GOAL_MAIN#/transport')
    front('Frontera de asistencia','CLOSED_ALCANCE','Fuentes del actor revisadas; codec, objetivo y evaluador preparados','No lookup de respuestas en el flujo auditado','Sandbox OS universal o ausencia de b privado en todo estado del host','CALIDAD_PURA; GOAL_MAIN#/scope')
    front('Contexto sensorial','CLOSED_SENSIBILIDAD','Ocho consultas; seis entradas aplicadas y dos rechazadas; dos geometrías prefijadas','Lateral sensible inicialmente pero no reutilizable; superior aplica cuatro bits pero bit 1 no emite','Política contextual aprendida, QUERY útil para bit 1 o percepción semántica de ausencia','CONTEXTO; CONTEXTO_MANIFIESTO')
    front('ROI retrospectiva','PENDIENTE_N0','Análisis del auditor pendiente de revisión, sin nuevos ticks','No se atribuye capacidad recuperada','Recuperación nativa, linaje único o memoria funcional por mera diferencia regional','CONTEXTO_INFORME')
    front('Reserva60min','PENDIENTE','42 eventos prospectivos; propietario en progreso','PENDIENTE_INCORPORAR_CORTE_REAL','Duración alcanzada, cierre y últimas funciones','CONTINUIDAD_EN_CURSO')
    front('Distribución y manual','PENDIENTE','Sólo borrador editorial','No se han probado aquí Full ni Word 1.16','Paquete actual, portabilidad y representación visual','CONTINUIDAD_EN_CURSO')
    trials=[]
    def trial(name,life,control,requested,applied,rejected,outcome,unit,scope,cites):trials.append(dict(ensayo=name,vida_o_ramas=life,historia_y_control=control,solicitado=requested,aplicado=applied,rechazado=rejected,respuesta_o_resultado=outcome,unidad=unit,atribucion=scope,fuentes=cites))
    trial('MAIN_CADENA_R01','APD02_MAIN','Cadena propia: dos enseñanzas nuevas y ocho usos del acumulador',1843,1843,0,'Nueve APD: 8 SUCCESS y 1 NUMERIC_ERROR; 17 admisiones = 13 materiales + 4 controles','entradas nativas únicas','No contar el ledger duplicado','CADENA')
    trial('LEX_R01','Seis AUX dependientes','paired, opposite, omitted, A_only, B_only, B_then_A','Ver por brazo','Ver por brazo','Ver por brazo','paired/opposite/A_only/B_then_A conservan 12/12; B_only 9/12; omitted 12/12','controles de asociación','No seis individuos independientes','REPERTORIO#/language')
    trial('LEX_R02_A0B0','AUX de padre completo','B− enseñado; ni consulta A ni consulta B',182,182,0,'Panel anterior 12/12','entradas nativas','Control de edad común','ACUM_LEX; LEX_AUTOPSIA')
    trial('LEX_R02_A0B1','AUX de padre completo','B− enseñado; sólo consulta B',189,189,0,'B−; panel anterior 12/12','entradas nativas','B sola no explica la pérdida','ACUM_LEX; LEX_AUTOPSIA')
    trial('LEX_R02_A1B0','AUX de padre completo','B− enseñado; sólo consulta A sin memoria A',189,189,0,'A nula; panel anterior 12/12','entradas nativas','A sola no explica la pérdida','ACUM_LEX; LEX_AUTOPSIA')
    trial('LEX_R02_A1B1','AUX de padre completo','B− enseñado; consulta A→consulta B',196,193,3,'A/B nulas; panel anterior 9/12','entradas nativas','Efecto conjunto del protocolo; no se demostró borrado de memorias','ACUM_LEX; LEX_AUTOPSIA')
    trial('ACUM_R01_REAL','Copia completa MAIN T361114','Ocho incrementos y retorno genérico real',16,16,0,'25, 29, 29, 36, 38, 41, 42, 42','entradas nativas; ocho oportunidades','Datos crudos secuenciales, no cifra recuperada de metadatos','ACUM_LEX')
    trial('ACUM_R01_OMIT','Copia completa MAIN T361114','Mismos ocho incrementos, sin retorno',8,8,0,'Ocho oportunidades sin respuesta numérica','entradas nativas','Control sin renovar acceso','ACUM_LEX')
    trial('ACUM_R01_SHAM','Copia completa MAIN T361114','Ocho incrementos, retorno de igual dosis fuera de interacción',16,16,0,'Ocho oportunidades sin respuesta numérica','entradas nativas','Control material, no limpieza del host','ACUM_LEX')
    trial('MAIN_RUTA_ABAB_R03','APD02_MAIN adverso','Doce tareas tras preparación R03',442,430,12,'Doce palabras válidas; cero rutas; cero proveedores','entradas nativas','RAW no vacío con state 0; soporte minus bloqueado','R03_ADVERSO')
    trial('AUX_R04_REAL','APD02_R04_ACTUAL_real','A2/B3/A1/B2 con consecuencia común','Ocho tareas','Ocho respuestas',0,'Ocho números y archivos; cuatro útiles; coste 24','tareas APD','No MAIN; ningún trasplante','R04_AUX')
    trial('AUX_R04_OMIT_SHAM_DESYNC','Tres controles dependientes','Dos primeras tareas A, retorno omitido, sham o desfasado','Dos por brazo','Dos por brazo',0,'0→0 y coste 10; real 0→− y coste 6','tareas por brazo','Contraste causal; no ocho tareas por control','R04_AUX')
    trial('AUX_R04_CUT','Tres controles dependientes','Conservar, cortar o sham del producto ya formado','Ver primario','Ver primario','Ver primario','Próxima ruta −/0/−; panel anterior 6/6','corte selectivo','Intervención diagnóstica, no regulación autónoma','R04_CUT')
    trial('MAIN_RUTA_R04','APD02_MAIN','A3/B2/A4/B3; 25 admisiones = 21 materiales + 4 controles',1650,1650,0,'Doce números y archivos; ocho útiles; cuatro RESOURCE_LIMIT; coste 28','entradas nativas','Historia propia; no repetición AUX','R04_MAIN')
    trial('MAIN_CALIDAD_COMPOSICION','APD02_MAIN','Quince directas y tres etapas asistidas','18 primitivas','18 proveedores',0,'17 números pertinentes; 17 archivos; 16 entregas; un error semántico y uno FS','oportunidades primitivas','Contenedor no se cuenta como etapa extra','CALIDAD#/APD_primitives')
    trial('MAIN_RAW128','APD02_MAIN','128 componentes 1/0 alternados',176,176,0,'C nativo 64; selección +','entradas nativas; una trama','Agregado preparado; no 128 conceptos','CALIDAD#/raw128')
    trial('GOAL_AUX_R03','Cuatro AUX dependientes','hidden real, hidden omit, visible y reserved DIFF','Cuatro mundos','Cuatro primeras QUERY',0,'Tres metas con archivo; omit mantiene cuatro QUERY; panel común 14/14 en todos','mundos dependientes','QUERY visible redundante refuta missing semántico general','GOAL_AUX')
    trial('MAIN_GOAL_PENDING_REOPEN','APD02_MAIN','Tres objetivos, seis oportunidades, dos PID y mismo ID pendiente',915,915,0,'17 admisiones = 9 materiales + 8 controles; archivos 11, 13, 14 y 32 nuevo','entradas nativas únicas','Contador 1→2→3; no requeue ni importación de memorias','GOAL_MAIN')
    trial('CONTEXTO_R01_TOTAL','Cuatro AUX del mismo padre T454808','Dos geometrías y secuencias de bits 0→1 y 1→0',8,6,2,'Seis lecturas válidas, pero dos siguieron a entradas rechazadas; cuatro válidas entre seis entradas aplicadas','consultas y entradas sensoriales','No tarea ambiental, docencia ni consecuencia de calidad; consultas no son individuos','CONTEXTO; CONTEXTO_INFORME; CONTEXTO_MANIFIESTO')
    trial('CONTEXTO_R01_LATERAL','Dos AUX de contexto lateral','Mismo RAW/clocks/tick inicial; sólo futuros bits opuestos',4,2,2,'Primer bit 0→− y 1→0; después persisten sin admitir el nuevo bit','entradas sensoriales','Sensibilidad inicial positiva, renovación fallida por ocupación; no limpiar soporte','CONTEXTO; CONTEXTO_INFORME')
    trial('CONTEXTO_R01_FI01','Dos AUX de contexto superior','Mismo RAW/clocks/tick inicial; bits 0→1 y 1→0',4,4,0,'[−,None] y [None,−]; bit 1 deja seis RAW del lector en cero','entradas sensoriales','Fuente reutilizable no implica interfaz de acción completa','CONTEXTO; CONTEXTO_INFORME')
    trial('ROI_N0','Auditor externo','Sin nueva física; análisis aún pendiente','N/A','N/A','N/A','PENDIENTE_INCORPORAR_ANALISIS_ROI','sin ensayo funcional','No llamar recuperación a un análisis regional','CONTEXTO_INFORME')
    trial('RESERVA_CONTINUA_60M_R01','APD02_MAIN vivo','42 eventos prospectivos','N/A','N/A','N/A','PENDIENTE_INCORPORAR_CORTE_REAL','no resultado todavía','No anticipar hora, cierre, beta ni Full','CONTINUIDAD_EN_CURSO')
    result={'schema':'APD02.scalar_table_candidates.R03','status':'CLOSED_SOURCES_PLUS_EXPLICIT_PENDING_ROWS_NOT_FINAL',
        'new_native_ticks':0,'csv_or_DOCX_written':False,'root_must_author_CSV_with_required_artifact_workflow':True,
        'cell_semantics':{'numeric_zero':'Retain integer0; never export through value-or-empty.','not_applicable':'Explicit N/A is notzero.','nonadditive':'Different counts have declared units; do notpooltaskspartialscontrolsandarrays.','forms':'Common14lexicalforms=6Greeknames+8Spanishforms; sixMAcontextmemoriesareaseparatemeasure,not20faculties.'},
        'sources':source_index,'tables':{}}
    for key,rows in(('CAPACIDADES_POR_VIDA_Y_MOMENTO',cap),('COBERTURA_FRENTES',fronts),('ENSAYOS_Y_CONTROLES',trials)):
        headers=list(rows[0]);assert all(list(row)==headers for row in rows)
        assert all(type(value)in(str,int,float,bool)for row in rows for value in row.values())
        result['tables'][key]={'headers':headers,'rows':rows,'row_count':len(rows)}
    with a.salida.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,sort_keys=True,indent=2)
    print(json.dumps({'sha256':sha(a.salida),'tables':{k:v['row_count']for k,v in result['tables'].items()},'sources':len(source_index),'new_native_ticks':0},ensure_ascii=False))
if __name__=='__main__':main()
