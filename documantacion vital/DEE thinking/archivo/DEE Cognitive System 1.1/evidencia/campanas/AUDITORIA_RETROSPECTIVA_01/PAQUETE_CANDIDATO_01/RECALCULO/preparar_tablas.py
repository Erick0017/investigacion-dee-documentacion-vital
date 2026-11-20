"""Flat scientific table values, derived from existing exported evidence."""
from pathlib import Path
import sys,argparse,json,gzip,tarfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from leer_estado import load_json,fields
p=argparse.ArgumentParser();p.add_argument('--paquete',type=Path,required=True);p.add_argument('--calculos',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();q=load_json(a.calculos);ix=load_json(a.paquete/'EVIDENCIA_CAUSAL/INDICE_PRIMARIOS.json');objects={}
for name in [ix['archive'],*[v['archive']for v in ix.get('additional_archives',[])]]:
    with tarfile.open(a.paquete/'EVIDENCIA_CAUSAL'/name,'r:xz')as t:objects.update({m.name:t.extractfile(m).read()for m in t.getmembers()if m.isfile()})
recovery={v['id']:v for v in q['RECOVERY_AND_CONTROLS']};policies={v['id']:v for v in q['POLICY_HISTORY_CONTRASTS']};cadence={v['id']:v for v in q['RECIPIENT_CADENCE']}
def j(v):return json.dumps(v,ensure_ascii=False,separators=(',',':'))
def classification(key,d):
    if '/PERDIDA_Y_REAPRENDIZAJE_13/'in key:
        case=key.rsplit('/',1)[1];v=q['AA13']['cases'][case]
        return('H4_FISICO_ACOTADO'if case.startswith('wall')else'CONTROL_DE_CONVERGENCIA', 'read='+str(v['decoded_recalculated'])+'; reaprendizaje='+str(v['relearned_decoded']), 'N17: estado físico y agenda común; el archivo conserva diario del instrumento; no recuperación nativa desde ese diario','$.AA13')
    if '/CAUSAL_DESTINO_42/'in key:
        v=q['AA42']['contrasts'][key.rsplit('/',1)[1]]
        return('CONTRASTE_CAUSAL_GLOBAL_DE_UNA_CONTRIBUCION','dRAW_post='+str(v['post_RAW_differences'])+'; dClock_post='+str(v['post_clock_differences'])+'; destino='+j(v['destination']['direction']),'Diagnóstico ya ejecutado; no reparación de MAIN ni borrado demostrado de toda su historia','$.AA42')
    if key in recovery:
        v=recovery[key];used=[x for x in v['stages']if x['block']!='initial'and x['stage']=='use'];code=used[-1]['codes_from_RAW']if used else[]
        return('USO_POR_OTRO_SOPORTE'if code else'CONTROL_SIN_USO_CALIFICADO','uso='+j(code)+'; entradas posteriores de contenido='+str(len(v['later_content_inputs'])),'Redundancia por dos adquisiciones iniciales; consulta común; no reconstrucción de un bit completamente destruido','$.RECOVERY_AND_CONTROLS')
    if key in policies:
        v=policies[key];first=(v.get('first')or{}).get('direction');second=(v.get('second')or{}).get('direction')
        return('CONTRASTE_DE_HISTORIA_DE_SELECCION','selector '+j(first)+' -> '+j(second),'Consecuencias y conexiones preparadas; P2 local debe juzgarse con omisión/desacoplamiento/corte, no por cambio RAW aislado','$.POLICY_HISTORY_CONTRASTS')
    if key in cadence:
        v=cadence[key]
        return('ACCESO_RECEPTOR_FINITO',str(v['qualified_single_code_reads'])+'/'+str(v['attempted_reads'])+' lecturas de código calificadas','Sin consultas intermedias B no significa sin toda interacción; consultas no son individuos independientes','$.RECIPIENT_CADENCE')
    if key=='AA/MAIN_CONFIRMATORIO_36/main':return('MAIN_MIXTO','panel previo de seis funciones; recuperación B tardía sin código','T47146 conservado; no se sustituye por otra rama ni se infiere pérdida global por un puerto vacío','$.MAIN_EXISTING_USE')
    if key.startswith('CPC9/E1_')and'K65'in key:
        v=q['CPC9']['K65'][key.split('/',1)[1]]
        return('FALLO_DE_ACCESO_Y_OCUPACION'if'NO_EVENT'not in key else'CONTROL_SIN_ADQUISICION','; '.join(str(x['correct'])+'/'+str(x['attempted'])for x in v['windows'])+'; ocupados='+str(v['physical_T2353']['occupied']),'K65 son formas físicas, no 65 significados; no se compararon historias convergentes para probar borrado global','$.CPC9.K65')
    if key.startswith('CPC9/E1_')and'TAIL'in key:
        v=q['CPC9']['tails'][key.split('/',1)[1]]
        return('INTENTOS_MAYORITARIAMENTE_RECHAZADOS',j(v['statuses']),'NO_NEW omite cuatro intentos docentes, no las consultas restantes; finales físicos iguales no prueban inocuidad general de consultar','$.CPC9.tails')
    if key=='CPC9/CRECIMIENTO_OCUPACION':return('CAUSA_GLOBAL_NO_AISLADA','Corte local elimina nacimiento; ocupación final297971; sham298024','Un nacimiento EMPTY_XNOR no es causa única; registro de diagnóstico existente','$.CPC9')
    if '/COALESCENCIA_DIAGNOSTICA_22/'in key:
        return('CONVERGENCIA_DIAGNOSTICA_ACOTADA',j(d['post_differences']),'Contribución de trayecto libre puede desaparecer sin diferencia global; control de otra contribución conserva tránsito; no borrado global de E1','$.PC22')
    if any('/'+v+'/'in key for v in ['LECTOR_POST_TRANSFORMACION_41','RESERVA_LECTOR_TRANSFORMADO_42','CONTEXTO_UTIL_MIXTO_44']):
        return('ACCESO_DEPENDIENTE_DE_LECTOR_PREPARADO','palabras='+j(d.get('SPANISH_DECODED'))+'; accion='+j(d.get('NATIVE_ACTION_OBSERVED')),'Contenido transformado y uso asistido de alcance limitado; no autonomía ni reconstructora general','$.PC_TRANSFORMED_ACCESS')
    if '/INFLUENCIA_ANTERIOR_04/'in key:return('TRAYECTORIA_CON_ANTECEDENTES_MULTIPLES',j(d.get('path',{})),'Proyección candidata no equivale a linaje. Sufijo verificado10928-22318; nacimientos/contribuyentes previos separados','$.EXISTING_TOROIDAL_ROUTES')
    if key=='CPC9/EI_D01':return('PROCEDENCIA_INSTRUMENTAL_CANDIDATA','Sonda remote_contact.renew.left.free enT476; X+5 observadoT477','Compatible con la órbita posterior; no prueba de continuidad de linaje sin huecos hastaT45028','$.X5')
    if key=='PC/PROCEDENCIA_01/reference_trace':return('RETORNO_ACOTADO_X5_Y_OBSERVADOR','470 enlaces consecutivos y7 crucesX de X+5; no discrepancias en9520-9990','Nueva lectura de datos antiguos; no repetición experimental ni memoria funcional por recurrencia sola','$.X5.continuous_existing_window')
    if '/REFERENCIA_CAUSAL_05/'in key:return('EFECTO_MATERIAL_DE_CONSULTA',j(d.get('commit',{}).get('result')),'Contrastar omisión, fuera de ruta y fase; no toda sonda con carga0 es pasiva','REGISTRO_ORIGINAL')
    if any('/'+v+'/'in key for v in ['FUENTE_CONTEXTO_09','RUTA_CONTEXTO_09_R1']):return('CONTEXTO_DE_EFECTOS_MIXTOS',j(d.get('commit',{}).get('result')),'Corte cercano puede mejorar nueva función y perder función espacial antigua; protección lejana distingue el conflicto','REGISTRO_ORIGINAL')
    if '/GENERALIZACION_DOSIS_17/'in key:return('DEPENDENCIA_DEL_DECODIFICADOR',j(d.get('commit',{}).get('result')),'Mismas salidas requieren lector declarado sensible a dosis; no cambio retrospectivo de criterio para elevar fallos','REGISTRO_ORIGINAL')
    if '/CONTINUIDAD_OPERATIVA_49/'in key:return('CONTINUACION_TECNICA_EXISTENTE',j(d.get('commit',d.get('result',{}))),'Ramas listas no consumidas; evaluaciones son futuros separados, no adquisiciones independientes','REGISTRO_ORIGINAL')
    return('REGISTRO_CON_ALCANCE_PROPIO',j(d.get('commit',{}).get('result',d.get('status'))),'Datos originales incluidos y lecturas verificadas; no nuevo experimento ni atribución automática a MAIN','REGISTRO_ORIGINAL')

map_header=['caso_id','vida_en_registro','N','tick_inicial_registrado','tick_final_registrado','estado_informacion_o_contraste','resultado_registrado_o_recalculado','limite_de_atribucion','localizador_calculo','archivo_original','SHA256_original','miembro_primario_exportado']
map_rows=[];life_rows=[]
for e in ix['entries']:
    if e['role']!='primary':continue
    b=objects[e['member']];d=json.loads(gzip.decompress(b)if e['member'].endswith('.gz')else b);key=e['id'];typ,res,limit,loc=classification(key,d)
    pre=d.get('pre',d.get('initial_physical',{}));post=d.get('post',d.get('final_physical',{}));life=d.get('life',d.get('case_id',''))
    pre=pre if isinstance(pre,dict)else{};post=post if isinstance(post,dict)else{};n=pre.get('N',d.get('configuration',{}).get('dimension',''));t0=pre.get('tick','');t1=post.get('tick',d.get('last_complete_tick',''))
    if len(res)>1800:res=res[:1800]+' [resumen truncado sólo en tabla; registro íntegro exportado]'
    map_rows.append([key,life,n,t0,t1,typ,res,limit,loc,e['original'],e['sha256'],e['member']])
    if life:
        life_rows.append([life,'CORTE_DEL_ENSAYO_NO_PUNTERO_ACTUAL',n,t1,key,typ,res,limit,'NO_PROMOVIDA_POR_ESTA_AUDITORIA','Experimento/auxiliar/control según expediente; no réplica independiente por denominación',e['sha256']])

life_header=['vida_o_unidad_registrada','tipo_de_corte','N','tick_del_corte','evidencia_o_perfil','funcion_o_estado_medido','conservado_o_usado','perdidas_asistencia_y_limites','promocion','unidad_y_continuidad','SHA256_snapshot_o_primario']
current=[]
for d in q['existing_lives']:
    if'life'not in d:continue
    life=d['life'];s=d['summary']
    if life=='E1_SOCIAL_11':state='PREDETERMINADO_PROTEGIDO';func='4 portadores sociales, referencia78 y comparadorR36/O16 documentados previamente; no reinterrogados aquí';lim='No recibe por software los aprendizajes de AA; sólo snapshot e identidad comprobados en este corte'
    elif life=='E1_ACCESO_ADAPTATIVO_01':state='MAIN_REAL_PRESERVADO';func='Seis funciones del panel anterior usadas en el futuro real; adquisición/uso local temprano';lim='Recuperación B tardía falla; no garantía de nuevo acceso desdeT47146 ni borrado global demostrado'
    elif life.startswith('AA01_ACCESO_LISTO_'):state='ESTADO_APRENDIDO_CON_AGENDA';func='Contenido previo, redundancia y acceso aprendido;9 entradas genéricas pendientes; uso probado en copias49';lim='La consulta consume/modifica; no receptor recurrente ni futuro de MAIN; bifurcar explícitamente antes de usar'
    else:state='RECEPTOR_ALTERNATIVO_FINITO';func='Recuperación de forma recibida por lector común; continuación21 con8 objetos';lim='No transferible automáticamente a MAIN; el código recordado no describe por sí mismo la escena actual'
    current.append([life,'PUNTERO_ACTUAL_VERIFICADO_SIN_TICKS',s['N'],s['tick'],d['profile'],state,func,lim,'PREFERENTE_SIN_CAMBIO'if life=='E1_SOCIAL_11'else'COMPLEMENTARIA_NO_PROMOVIDA','Padre y snapshot completo conservados; pendientes='+str(s['pending_count']),s['encoded_sha256']])
rows={'MAPA_INFORMACION_Y_ACCESO.csv':[map_header,*map_rows],'COMPARACION_DE_VIDAS.csv':[life_header,*current,*life_rows]}
a.salida.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:len(v)-1 for k,v in rows.items()}))
