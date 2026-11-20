from pathlib import Path
import json,hashlib,ast
W=Path(__file__).resolve().parent;S=W/'stage'
H=Path(r'D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking')/'casos practicos/trabajo_codex/CPC9/runs/RUN_20261019_165651/core/final'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=json.loads((H/'PRUEBA_RECUPERACION_DESDE_CERO.json').read_text(encoding='utf8'))
matrix=json.loads((H/'CORE_MATRIZ_CAPACIDADES.json').read_text(encoding='utf8'))
families=['cpc1','cpc2','sem01','cpc4','cpc5','cpc6','cpc7','mcts','repertoire','rca','count','product','product_extra','ordered','stream','network','architectures','bridge','capacity','longitudinal','policy','native_loop','central','qfm','l15','need','missing','retain_early','retain_word','retain_late','social','initial_cpc8','core06','core07']
NAMES=[('Contratos causales CP01','Orden finito, calibración móvil, competencia, transmisión, acción y persistencia con controles causales propios.'),('Pronóstico por experiencia CP02','Resultados pasados escriben una relación; la organización emite antes de un objetivo ambiental independiente.'),('Asociación y acción SEM01','Una señal opaca se empareja con una consecuencia y participa después en anticipación y acción.'),('Comunicación protegida ABCD','Un producto físico de A alcanza B; el contraflujo preparado protege usos en una red de cuatro regiones.'),('Composición con respaldos adquiridos','Varias relaciones vividas y respaldos separados participan en un producto común y nuevas adquisiciones.'),('U0 y dos formas CPC6','Una trayectoria combina orden, comparación, comunicación y dos señales con lectores renovados.'),('Continuidad y revisión CPC7','Un U0 continuo adquiere bancos y formas, conserva usos muestreados y revisa selectivamente L03.'),('Orden contacto y magnitud MCTS','Una preparación N67 adquiere relaciones de orden/contacto y referencias; controla omisión y experiencias opuestas.'),('Repertorio opaco N131','Treinta y dos asociaciones seguidas de treinta y tres, consultas y revisión finita de L01 en un mundo separado.'),('Regulación contextual RCA','La consecuencia modifica una comparación y política preparada cuyo producto condiciona un acceso posterior.'),('Señal cuantitativa calibrada','Asociación auxiliar B-only con contacto normalizado, reservas y restauración, sin generalizar cardinalidad.'),('Contratos oficiales de thinking','Regresiones de construcción, entradas, observación y persistencia de los mecanismos publicados.'),('Memoria basal y reescritura contextual OBP','AB/BA/H0 y contexto local permiten retención y reescritura131→132; cortes distinguen vecinos, clock y retornos.'),('Composición sensible al orden','Dos acontecimientos y sus relaciones adquiridas producen una secuencia dependiente de orden, con cortes y sham.'),('Flujo temporal','El orden en un flujo y sus demoras cambia el uso posterior en los intervalos congelados.'),('Red de pregunta respuesta y uso','Participantes físicos preparados transportan petición y réplica y modifican una actuación posterior.'),('Arquitecturas acopladas','Comparación física de uno, dos y cuatro grupos, con recursos y límites de la preparación declarados.'),('Puente de memorias relativas y móviles','Una contribución adquirida viaja entre soportes y participa después en uso funcional.'),('Capacidad finita CPC5','Asociaciones opacas K8/16/32/65, historias opuestas, fase y controles que preservan aprendizaje durante evaluación.'),('Adquisición acumulativa32 y33','La misma organización recibe relaciones nuevas tras las iniciales y vuelve a usar ambas cohortes.'),('Selección revisable R14','Una política nativa finita cambia su realización ante consecuencias; no optimización general.'),('Bucle nativo de vida CPC3','Una trayectoria conserva relación y responde a una oportunidad ambiental mediante el protocolo histórico.'),('Comparación central actual','Una expectativa física encuentra un resultado actual independiente y cambia una marca posterior.'),('Forma móvil y acceso remoto','Una señal adquirida viaja por planos remotos y se utiliza con interfaz preparada.'),('Diagnóstico de acceso L15','Contenido transformado y lector se separan mediante cortes; el lector original puede seguir fallando.'),('Consulta por discrepancia','Una expectativa adquirida y un resultado actual condicionan una petición nativa y un uso posterior.'),('Apertura física de ausencia','Una ventana preparada ante informe ausente produce petición y uso, con dominios separados de U0.'),('Retención temprana y cortes','Copias de padres históricos distinguen contribuciones de memoria, portador y lector mediante intervenciones.'),('Retención de la forma','Las consultas tardías y controles de señal separan presencia de un soporte y acceso actual.'),('Acceso tardío por historia original','Una interacción alternativa utiliza historia anterior sin concluir destrucción por silencio local.'),('Enseñanza social por portador','La adquisición de E1 produce un mensaje físico que cambia al receptor simple y participa en su uso posterior.'),('Primer CPC8 longitudinal','Cuatro historias originales N131 incluyen asociación social, revisión selectiva y controles fuera de ruta.'),('Extinción inversión y readquisición CORE06','Un portador ordinario restablece una ruta seguida por reenseñanza emparejada; controles conservados.'),('Reprogramación funcional CORE07','Una actualización y redirección preparadas revisan la respuesta aditiva de una relación adquirida.')]
campaigns=[['CPC1'],['CPC2'],['CPC3','SEM01'],['CPC4'],['CPC5'],['CPC6'],['CPC7'],['CPC8 reconstruido'],['CPC8 reconstruido'],['CPC8 reconstruido'],['CPC8 reconstruido'],['thinking4.5'],['OBP','MBP4','thinking4.5'],['CPC5 ampliación'],['CPC5 ampliación'],['CPC5 ampliación'],['CPC6'],['CPC6'],['CPC5 ampliación'],['CPC5 ampliación'],['CPC3','Ingeniería01'],['CPC3'],['CPC3'],['CPC8 reconstruido'],['CPC8 reconstruido'],['CPC7'],['CPC7'],['CPC6'],['CPC6'],['CPC6'],['CPC8 reconstruido'],['Primer CPC8'],['CORE06','CPC3','Procesamiento Nativo'],['CORE07','CPC3','Procesamiento Nativo']]
records=[]
for i,f in enumerate(families,1):
    prev=old['family_results'][f];variants=[]
    for j,c in enumerate(prev.get('cases',[]) if isinstance(prev.get('cases'),list) else []):
        if not isinstance(c,dict):continue
        name=str(c.get('id',c.get('case_id',c.get('field',c.get('name',f+'_'+str(j+1))))))
        details={k:c[k] for k in ('field','history','gate','name','id','case_id','scope','source_configuration','configuration') if k in c}
        variants.append({'id':name,'role':'contrato y contraste histórico; no réplica biográfica independiente','conditions':details})
    if not variants:variants=[{'id':f,'role':'contrato técnico de API y física publicada','historical_tests':prev.get('tests_run')}]
    ident=f'M{i:03}'
    records.append({'id':ident,'name':NAMES[i-1][0],'function':NAMES[i-1][1],'campaigns':campaigns[i-1],'word_families':[1,2,3,4,5,6,7,8,10,11,12] if f=='cpc1' else [1,2,3,4,5,6,7,8,12],
      'variants':variants,'native':{'command':['{python}','sectores/core/ejecutar_sector.py','--mechanism',ident,'--out','{out}'],'timeout_seconds':3600 if f=='core07' else 2400,'result':'RESULTADO.json'},'recalc':None,
      'source_files':[{'original':str(H/'DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip'),'relative':'sectores/core/documentacion/INDICE_MIEMBROS.json','sha256':sha(S/'documentacion/INDICE_MIEMBROS.json'),'materialization':'Logical paths and exact private source hashes are indexed here; the store is lossless and not a ZIP of campaigns.'}],
      'expected':{'historical_recovery':prev.get('status'),'contract':prev.get('scope',NAMES[i-1][1]),'strict_comparison':'Functional fields and full physical digests, original controls and reserves; host filenames/timestamps excluded only by original documented worker.'},
      'history_status':'POSITIVO_HISTORICO_REPRODUCIDO_EN_CORE_CPC9','integrity_status':'MATERIAL_EXACTO_RECUPERADO','current_validation':'PENDIENTE_ZIP_FINAL','pending':[],
      'assistance':'Arquitectura, estímulos, lectores, calendario y evaluación preparados; respuestas físicas por motor. Los diagnósticos pertenecen al auditor.',
      'limitations':['El ID agrupa un contrato recuperado, no una facultad cognitiva independiente ni integración de todos los experimentos en una vida.',prev.get('scope','Ver el dominio de la receta original.')],
      'historical_runtime_seconds':prev.get('elapsed_seconds',0),'family':f})
cfg=json.loads((S/'configuraciones/CPC9_RECUPERACION.json').read_text(encoding='utf8'))
extras=[('M035','Integración física CPC9 desdeT0','Una nueva preparación continua N67 adquiere y utiliza orden, contacto, comparación, consulta e información en un mismo mundo.',['CPC9'],[1,2,4,5,6,7,11,12]),('M036','Revisión cuantitativa54 a67','Desde el padre histórico completo T884, una aportación13 cambia la referencia y respuestas reservadas frente al control de igual material fuera de ruta.',['CPC9'],[2,3,4,12]),('M037','Comunicación bidireccional y uso CPC9','Una comparación de B genera un portador que E1 asocia y utiliza; signos opuestos, omisiones, reservas, corte y sham conservados.',['CPC9'],[2,5,6,7]),('M038','Adquisición opaca65 N67 auxiliar','Experiencias progresivas adquieren formas físicas en un mundo auxiliar N67; historias opuestas, no evento, desacoplamiento y corte deF00.',['CPC9'],[2,3,11])]
for ident,name,function,camps,wf in extras:
    cases=[x for x in cfg['cases'] if x['mechanism']==ident]
    records.append({'id':ident,'name':name,'function':function,'campaigns':camps,'word_families':wf,'variants':[{'id':c['id'],'role':'positivo, control o reserva original','configuration':c['input_configuration'],'source_root':c['source_root'],'primary':c['reference']} for c in cases],
      'native':{'command':['{python}','sectores/core/ejecutar_sector.py','--mechanism',ident,'--out','{out}'],'timeout_seconds':3600,'result':'RESULTADO.json'},'recalc':None,
      'source_files':[{'original':'CPC9 fuente privada y primarios del expediente cerrado','relative':'sectores/core/configuraciones/CPC9_RECUPERACION.json','sha256':sha(S/'configuraciones/CPC9_RECUPERACION.json')}],
      'expected':{'comparison':'Igualdad exacta de geometría, todos los frames registrados, ventanas locales, recibos y estado físico final. Las rutas del anfitrión y hashes de contenedor se separan de la física.','variants':len(cases)},'history_status':'POSITIVO_HISTORICO_CON_CONTROLES','integrity_status':'FUENTES_POR_HASH_Y_PRIMARIOS_COMPLETOS_RECUPERADOS','current_validation':'PENDIENTE_ZIP_FINAL','pending':[],
      'assistance':'Diseño y agenda externos; comparación, transporte y transformación por v27. M036 carga el snapshot histórico completo incluido, sin atribuirlo a la vida actual.',
      'limitations':['Las realizaciones no son65significados NSM ni facultades simultáneas del ente actual.','M035 demuestra adquisición desdeT0; M036 es continuación declarada desde estado aprendido, no recuperación de otra biografía.']})
for ident,kind,name,wf in [('M039','CORE15','Observadores de propagación CORE15',[1,3]),('M040','CORE16','Información oculta y observación CORE16',[1,3]),('M041','CORE17','Reparación soportada y compresión CORE17',[3,5,10])]:
    records.append({'id':ident,'name':name,'function':'Recálculo de las mediciones y adjudicaciones archivadas del mecanismo; código histórico de ejecución y controles preservados en el almacén.','campaigns':[kind],'word_families':wf,'variants':[{'id':kind,'role':'observadores archivados y controles, no nueva ejecución'}],
      'native':None,'recalc':{'command':['{python}','sectores/core/ejecutar_sector.py','--mechanism',ident,'--out','{out}','--recalc'],'timeout_seconds':300,'result':'RESULTADO.json'},
      'source_files':[{'original':'Core CPC9 conserva primarios y runners de '+kind,'relative':'sectores/core/reproduccion/recalcular_observadores.py','sha256':sha(S/'reproduccion/recalcular_observadores.py')}],
      'expected':{'calculation':'El recálculo original de Core identifica denominadores y mediciones deCORE15/16/17; no es transición nativa.'},'history_status':'POSITIVO_HISTORICO_CON_LIMITES','integrity_status':'CODIGO_Y_PRIMARIOS_RECUPERADOS','current_validation':'PENDIENTE_RECALCULO_ZIP_FINAL',
      'pending':['La reproducción nativa de este conjunto anterior requiere integrar sus árboles padre/entornos y ejercer el contrato histórico; sólo se ofrece recálculo, aunque los runners archivados se conservan.'],
      'assistance':'Observadores externos; reparaciónCORE17 mediante respaldo y portador preparado, sin autorregeneración general.','limitations':['No se declara Native reproducido por recalcular JSON.']})
ing=json.loads((S/'configuraciones/INGENIERIAS_RECUPERACION.json').read_text(encoding='utf8'))
for ident,name,fn in [('M042','Transformación específica de historia ING05','El mismo segundo acontecimiento produce una transformación distinta según historia; factorialW00/W10/W01/W11, rutas separadas, retención y geometrías nuevas.'),('M043','Reutilización causal posterior al anfitrión ING06','Historias distintas modifican la evolución y oportunidades futuras de soportes preparados, con controles H0/HA/HB, RAW y oportunidades equivalentes.'),('M044','Memoria relativa y lector renovado ING02','Diferencias entre dos soportes persisten y se usan mediante lectores renovados; un banco de ocho relaciones de orden se utiliza en paralelo, con controles de historia y fuente.'),('M047','Recurrencia con fuentes persistentes ING01','La gramática física preparada renueva una oscilación de dos ticks en el contrato R04 corregido, frente a fuentes ausentes, finitas y escritor incorrecto. Los clocks siguen evolucionando.')]:
    cs=[x for x in ing['cases'] if x['mechanism']==ident]
    records.append({'id':ident,'name':name,'function':fn,'campaigns':[{'M042':'Ingeniería05','M043':'Ingeniería06','M044':'Ingeniería02','M047':'Ingeniería01'}[ident],'Procesamiento Nativo'],'word_families':[1,3,5,9],
      'variants':[{'id':x['id'],'role':'protocolo histórico con controles y reservas','entry':x['entry'],'primary':x['references']} for x in cs],
      'native':{'command':['{python}','sectores/core/ejecutar_sector.py','--mechanism',ident,'--out','{out}'],'timeout_seconds':3600,'result':'RESULTADO.json'},
      'recalc':{'command':['{python}','sectores/core/ejecutar_sector.py','--mechanism',ident,'--out','{out}','--recalc'],'timeout_seconds':300,'result':'RESULTADO.json'} if ident in ('M042','M043') else None,
      'source_files':[{'original':'ZIP original '+{'M042':'INGENIERIA_05','M043':'INGENIERIA_06','M044':'INGENIERIA_02','M047':'INGENIERIA_01'}[ident],'relative':'sectores/core/configuraciones/INGENIERIAS_RECUPERACION.json','sha256':sha(S/'configuraciones/INGENIERIAS_RECUPERACION.json')}],
      'expected':{'comparison':'Todos los campos científicos JSON y todos los arreglosRAW/clocks del NPZ se comparan exactamente; rutas, versión dehost y hora separadas. Kernel/package/wheellegacy fijados porhash.','legacy_wheel':'motor/dee_universe_v27-27.0.0-cp313-cp313-win_amd64.whl','legacy_wheel_sha256':'69297e6f06761c8b2f65d24a3fd7a2f16a3f67595a7f9660739ab65f47abc939'},
      'history_status':'POSITIVO_HISTORICO_CON_CONTROLES','integrity_status':'CODIGO_CONFIGURACION_Y_ESTADOS_RAW_PRIMARIOS_RECUPERADOS','current_validation':'PENDIENTE_ZIP_FINAL','pending':[],
      'assistance':'Preparaciones y experiencias físicas iniciadas externamente en las fronteras congeladas; sondas en copias diagnósticas. Se usa el runtime histórico original, no una migración silenciosa a4.5.',
      'limitations':['Cambio de futuros no equivale a política autónoma general ni a contingencia nueva no precargada.','El modo recálculo deriva el factorialNRD05 deRAW; en los otros NPZ sólo indexa y verifica datos. La reproducción física completa está en modo nativo.']})
for ident,name,fn in [('M045','Interfaz preexistente transformada PROC02','Un frente condicionado por historia transforma un componente ya preparado; EARLY yLATE conservan14sitios pero cambian RAW y el resultado de los diagnósticos2/0/2.'),('M046','Calibración de fluctuación y respuesta PROC03','Los observables, calibración, controles y selección de modelo se recalculan desde series primarias; el corte Discovery original sigueUNINFORMATIVE.')]:
    records.append({'id':ident,'name':name,'function':fn,'campaigns':['Procesos02' if ident=='M045' else 'Procesos03'],'word_families':[1,3,9],
      'variants':[{'id':x,'role':'preparación histórica con controles y observación pasiva'} for x in (['MAIN_S0','FRESH_V1','FRESH_V2','diagnóstico de centros','comparación conjunta'] if ident=='M045' else ['calibración','discovery y controles'])],
      'native':{'command':['{python}','sectores/core/ejecutar_sector.py','--mechanism',ident,'--out','{out}'],'timeout_seconds':3600,'result':'RESULTADO.json'} if ident=='M045' else None,
      'recalc':{'command':['{python}','sectores/core/ejecutar_sector.py','--mechanism',ident,'--out','{out}','--recalc'],'timeout_seconds':1200,'result':'RESULTADO.json'},
      'source_files':[{'original':'Paquete privado original de'+('PROCESOS02' if ident=='M045' else 'PROCESOS03'),'relative':'sectores/core/ejecutar_ingenierias.py','sha256':sha(S/'ejecutar_ingenierias.py'),'data_prefix':'procesos02/' if ident=='M045' else 'procesos03/'}],
      'expected':{'comparison':'PROC02 compara todos los campos físicos y567arrays exactos frente alprimario. PROC03 recomputa las funciones originales de calibración ydiscovery sinNative, con igualdad numérica del contrato.'},
      'history_status':'POSITIVO_FISICO_ACOTADO' if ident=='M045' else 'INSTRUMENTO_Y_DISCOVERY_ARCHIVADO_SIN_OPERADOR_ELEGIDO','integrity_status':'FUENTES_CONFIGURACIONES_Y_PRIMARIOS_RECUPERADOS','current_validation':'PENDIENTE_ZIP_FINAL',
      'pending':[] if ident=='M045' else ['No se ofrece reproducción nativa de las33696transiciones deDiscovery; esta vía sólo recalcula evidencia y conserva su runner original completo.'],
      'assistance':'Observación y diagnósticos del investigador; fuentes y oportunidades iniciales preparadas, sin decisiones suministradas al participante.',
      'limitations':['Las variaciones de clock no se interpretan como fasecuántica ni los perfiles medidos como termodinámica universal.','Interfaz transformada y diagnósticos en copias no implican reparación o regulación autónoma.']})
for record in records:
    if record['id']=='M038':
        record['recalc']={'command':['{python}','sectores/core/ejecutar_sector.py','--mechanism','M038','--out','{out}','--recalc'],'timeout_seconds':300,'result':'RESULTADO.json'}
        record['expected']['negative_recalculation']='Cinco primarios de límites: tres barridosMAIN57/65,53/65,4/65; controlesNO_EVENT/UNPAIRED0/65; tail177rechazos de178nuevos pedidos y RAW/clocks/tickfinalesT2493iguales aNO_NEW. No prueba identidad causal completa ni65significados.'
    if record['id'] not in ('M039','M040','M041'):continue
    number=int(record['id'][1:])-24
    record['native']={'command':['{python}','sectores/core/ejecutar_sector.py','--mechanism',record['id'],'--out','{out}'],'timeout_seconds':4800 if number==16 else 3600,'result':'RESULTADO.json'}
    record['name']={15:'Propagación y contrastes de observador CORE15',16:'Operador, accesibilidad y capacidades nativas CORE16',17:'Reconstrucción mediante respaldo y cociente causal CORE17'}[number]
    record['function']={15:'Se reproducen los seis contratos congelados de movimiento, reducer, cierre espacial,clock, opacidad y propagación, conservando canarios fallidos.',16:'Se reproducen cuatro holdouts: operador, transferencia/regeneración/protección, probabilidades y orden/fase; los mecanismos deterministas no acreditan fenómenos cuánticos.',17:'Una política redundante reconstruye una función mediante portador preparado, con siete brazos y84realizaciones; un representante reducido conserva los futuros ensayados.'}[number]
    record['pending']=[]
    record['limitations']=['Las construcciones y sondas son preparación del investigador; no se atribuyen a la vida actual ni a una mente general.','Reproducción completa de los holdouts enumerados, no de todas las exploraciones históricas de estas campañas.','El recálculo sigue separado de las nuevas transiciones nativas.']
    record['expected']['native_comparison']='Fuentes y desafíos originales exactos; todos los campos científicos de los primarios se comparan, excluyendo sólo entorno del anfitrión, fecha y hashes que contienen esas fechas. Se coteja identidad del ABI histórico.'
    record['variants']=[{'id':name,'role':'holdout original con controles, no nueva investigación'} for name in {15:['seis contratos de expansión'],16:['operador','capacidades','probabilidades','orden y fase'],17:['reparación respaldada siete brazos','factorR0']}[number]]
coverage=[]
for row in matrix['rows']:
    ident=row['id'];covered=[]
    if ident.startswith('CP01'):covered=['M001']
    elif ident.startswith('CP02'):covered=['M002']
    elif ident=='SEM01':covered=['M003']
    elif ident.startswith('CPC4'):covered=['M004']
    elif ident=='CPC5_COMPOUND':covered=['M005']
    elif ident=='CPC5_CAPACITY65':covered=['M019']
    elif ident=='CPC5_LONGITUDINAL65':covered=['M020']
    elif ident=='CPC5_ORDER_AND_DIALOGUE':covered=['M014','M015','M016']
    elif ident in ('CPC6_INTEGRATED','CPC6_TWO_FORMS'):covered=['M006']
    elif ident=='CPC6_RETENTION_CAUSAL':covered=['M028','M029','M030']
    elif ident=='CPC6_ARCHITECTURES':covered=['M017','M018']
    elif ident=='CORE06_RELEARNING':covered=['M033']
    elif ident=='CORE07_REPROGRAMMING':covered=['M034']
    elif ident=='CPC3_POLICY':covered=['M021']
    elif ident=='ING01_R04_R14':covered=['M021','M047']
    elif ident=='ING02_RELATIVE':covered=['M044']
    elif ident=='CPC3_MAIN_AND_COMPARISON':covered=['M022','M023']
    elif ident.startswith('CPC7_'):
        covered=['M007'] if ident in ('CPC7_U0_CONTINUITY','CPC7_SELECTIVE_REVISION_M1_M2','CPC7_DIRECTIONAL_COMPOSITION_AND_POST_NAME') else ['M026'] if ident=='CPC7_PREPARED_DISCREPANCY_REQUEST' else ['M027'] if ident=='CPC7_ABSENCE_APERTURE' else []
    elif ident=='MBP4_CONTEXTUAL_REWRITE':covered=['M013']
    elif ident.startswith('PRODUCT'):covered=['M012','M013']
    elif ident.startswith('CORE15'):covered=['M039']
    elif ident.startswith('CORE16'):covered=['M040']
    elif ident.startswith('CORE17'):covered=['M041']
    elif ident.startswith('ING05'):covered=['M042']
    elif ident.startswith('ING06'):covered=['M043']
    elif ident=='PROCESOS_OBSERVERS':covered=['M039','M040','M045','M046']
    elif ident=='PROC02_PREEXISTING_INTERFACE':covered=['M045']
    elif ident=='PROC03_EXCHANGE_DISCOVERY':covered=['M046']
    elif ident=='CPC8_MAIN_ORDER_CONTACT' or ident=='CPC8_MAIN_QUANTITY_UPDATE':covered=['M008']
    elif ident in ('CPC8_CONTACT_SOCIAL','CPC8_MAGNITUDE_SOCIAL'):covered=['M031']
    elif ident=='CPC8_K65_PUBLISHED':covered=['M009']
    elif ident=='CPC8_RCA_REGULATION':covered=['M010']
    elif ident=='CPC8_COUNT_SIGN':covered=['M011']
    elif ident=='CPC8_QFM_MOVING_FORM':covered=['M024']
    elif ident=='CPC8_L15_DIAGNOSIS':covered=['M025']
    status='CUBIERTA_POR_CONTRATO' if covered else 'DOCUMENTAL_SIN_NUEVO_MECANISMO_EJECUTABLE' if ident in ('PROCESAMIENTO_NATIVO','FISICA_META_ROSETTA','FISICA_UNI1_LATER_REDUCTION','CPC7_NSM65_SCOPE') else 'PENDIENTE'
    reason='' if covered else 'Síntesis o catálogo documental: no constituye una realización física adicional.' if status.startswith('DOCUMENTAL') else 'El Core preserva el resultado y sus fuentes, pero no ofrece en este corte un protocolo nativo aislado específico adicional.'
    coverage.append({'historical_row':ident,'mechanism':row['mechanism'],'destination':status,'covered_by':covered,'reason':reason,'historical_detail':row})
for p in S.rglob('*.py'):ast.parse(p.read_text(encoding='utf8'),filename=str(p))
index=json.loads((S/'documentacion/INDICE_MIEMBROS.json').read_text(encoding='utf8'))
result={'sector':'core','stage_root':str(S),'mechanisms':records,'coverage':coverage,'notes':['34familias originales son contratos de recuperación; no34facultades cognitivas independientes.','MBP4/OBP contextual se cubre enM013 con regresiones que incluyen primarios, cortes y continuaciones completas.','Store único porSHA materializa código y datos en resultados; no contieneZIPs de campañas ni dependencias a las carpetas originales.'],
 'dependencies':[{'name':'dee_thinking','version':'4.5.0','wheel':'motor/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl','sha256':'09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'},{'name':'dee_universe_v27','version':'27.0.0 historicalABI','wheel':'motor/dee_universe_v27-27.0.0-cp313-cp313-win_amd64.whl','sha256':'69297e6f06761c8b2f65d24a3fd7a2f16a3f67595a7f9660739ab65f47abc939'},{'name':'numpy','version':'2.2.6','path':'codigo_comun/terceros','scope':'CORE06/07, Ingenierías01/02/05/06 y Procesos02/03'}],
 'materialized_index':index,'store_bytes':(S/'mecanismos/RECUPERACION_POR_HASH.jsonl.gz').stat().st_size,'historical_core_archive':{'original':str(H/'DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip'),'sha256':sha(H/'DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip')},
 'native_started':False,'read_scope':'Word actual; Core original privado; primarios, fuentes y estados CPC9 seleccionados; paquetes originales ING05/06; no nueva campaña.'}
(W/'sector.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'mechanisms':len(records),'variants':sum(len(x['variants']) for x in records),'coverage_rows':len(coverage),'pending_rows':[x['historical_row'] for x in coverage if x['destination']=='PENDIENTE'],'store_bytes':result['store_bytes']},ensure_ascii=False))
