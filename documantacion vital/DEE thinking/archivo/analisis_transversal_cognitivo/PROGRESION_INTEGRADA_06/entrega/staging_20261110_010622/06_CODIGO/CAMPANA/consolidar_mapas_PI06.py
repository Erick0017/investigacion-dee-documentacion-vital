"""Directed final scientific maps; read-only to product/Native stores, no engine."""
from pathlib import Path
import csv,datetime,hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=P/'estados/candidato/sistema'
MAIN='ECI02_PI03_REPRO_PI04_PI05_MAIN_01'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):
 p=Path(p);return {'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)}
def primary(execution,index):
 o=execution['outcomes'][index];p=Path(o['primary']);t=read(p)
 if sha(p)!=o['primary_sha256']or t['status']!='completed'or t.get('error')is not None:raise ValueError('Actual completed primary differs')
 a=json.loads(t['result']);rows=a['result']['rows']
 if len(rows)!=1:raise ValueError('One scientific row required')
 return a,rows[0],info(p)
def write_json(p,v):
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def write_csv(p,rows):
 with p.open('w',encoding='utf-8-sig',newline='')as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 reg=read(P/'REGISTRO_CAMPANA.json')
 if reg['Native_ticks_closed']!=7882 or reg['phase']!='NATIVE_CLOSED_ANALYSIS_AND_INCORPORATION_ONLY':raise ValueError('Science must be actually closed at the recorded cut')
 active=read(C/'sistema/estado/ACTIVO.json');card=read(C/'sistema/estado/vidas'/MAIN/'VIDA.json')
 if active['life_id']!=MAIN or card['physical']['N']!=67 or card['physical']['tick']!=824911 or card['snapshot_sha256']!='af74c8f47e43ed3b2395a338a23a6cbd42f105ec2cff4daac15b7a4d45e90832':raise ValueError('Do not overwrite a newer or different main')
 coarse=read(P/'control/PI06_AMBIENTE_NUBE_R06.json');fine=read(P/'control/PI06_CONFIRMACION_FINA_R04.json');control=read(P/'control/PI06_CONFIRMACION_CONTROL67_R04.json')
 ca,cr,cp=primary(coarse,0);fa,fr,fp=primary(fine,0);ea,er,ep=primary(control,0);fia,fir,fip=primary(control,1);c2a,c2r,c2p=primary(control,2)
 if coarse['new_ticks']!=67 or fine['new_ticks']!=15 or control['new_ticks']!=1300:raise ValueError('Actual horizons differ')
 if control['error']['message']!='Actual step exceeds preregistered finite Native bound':raise ValueError('Preserve the actual control protocol failure')
 if c2r['actual_numeric_result']!=23 or not c2r['useful_product']or c2r['native_input_summary']['applied']!=186:raise ValueError('Do not claim an absent observed useful control chain')
 resource=C/'sistema/estado/servicios_locales'/MAIN/'PI04_C2C_COORDINACION_R01/dispositivo/ESTADO_DISPOSITIVO.json'
 mainenv=read(resource)
 spec=importlib.util.spec_from_file_location('PI06_budget_read_only',P/'codigo/ejecutar_fases_PI06_R04.py')
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 ticktotal,lives,_=module.budget_ticks()
 if ticktotal!=7882 or len(lives)!=12:raise ValueError('Do not reset aggregate Native/world budget')
 worlds=[]
 for entry in lives:
  root=Path(entry['system']);life=entry['life_id'];p=root/'estado/vidas'/life/'VIDA.json';r=read(p)
  worlds.append({**entry,'card':info(p),'physical':r['physical'],'snapshot':str(root/r['snapshot']),
    'snapshot_sha256':r['snapshot_sha256'],'transport_parent':r.get('parent'),
    'not_a_principal':True,'full_world_requires_worker_and_queue':True})
 rp=read(C/'reproducibilidad/RECURSOS.json')
 aliases={k:v for k,v in rp.get('pairs',{}).items()if'PI06'in k}
 unregistered=C/'reproducibilidad/materiales/PI06_POST_INTERFERENCIA_T826449'
 if unregistered.is_dir()and 'PI06_POST_INTERFERENCIA_T826449'not in aliases:
  mf=unregistered/'EXPORTACION_SERVICIO.json'
  aliases['PI06_POST_INTERFERENCIA_T826449']={'product_relative':'reproducibilidad/materiales/PI06_POST_INTERFERENCIA_T826449',
    'manifest':info(mf),'registry_status':'Material preserved locally; registry alias not found at this inspection'}
 manuals=list(C.glob('*Manual_Maestro*Edicion_1_21.docx'))
 if len(manuals)!=1:raise ValueError('One actual governing manual only')
 manual=info(manuals[0]);manual['internal_edition_at_current_inspection']='1.32'
 publication=P/'documentos/DOCUMENTOS_PUBLICADOS_PI06_1_33.json'
 if publication.exists():
  manual['internal_edition_at_current_inspection']='1.33';manual['publication_proof']=info(publication)
  manual['visual_QA']={'status':'NOT_VALIDATED','reason':'Actual render attempts could not find LibreOffice soffice.exe; no visual approval is inferred from structural or hash checks.'}
 continuity={'schema':'DEE.PI06.final_continuity_and_evidence.v1','inspection_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'campaign':'PROGRESION_INTEGRADA_06','science_closed':True,'Native_executed_in_campaign':7882,'new_worlds':12,
  'budget':reg['budget'],'main':{'life_id':MAIN,'profile':card['profile'],'N':67,'T':824911,
    'current_snapshot':str(C/'sistema'/card['snapshot']),'current_snapshot_sha256':card['snapshot_sha256'],
    'physical':card['physical'],'ACTIVO':info(C/'sistema/estado/ACTIVO.json'),'VIDA':info(C/'sistema/estado/vidas'/MAIN/'VIDA.json'),
    'physical_parent':card.get('PI05_provenance',{}),'adopted_new_PI06_life':False,
    'snapshot_interfaces_agenda_and_native_receipts':'Inside exact complete Native snapshot, not recreated from RAW/clocks.',
    'queue':str(C/'sistema/estado/servicios_persistentes'/MAIN/'cola.sqlite3'),
    'worker':str(C/'sistema/estado/servicios_locales'/MAIN),'environment':info(resource),
    'C2C_ordinal':mainenv['ordinal'],'C2C_products':len(mainenv['products']),'C2C_resources':len(mainenv['resources']),
    'C2C_remaining_offers':len(mainenv['resources'])-mainenv['ordinal'],
    'function_current_not_materially_retested_on_main_in_PI06':True},
  'manual_current':manual,'experimental_worlds':worlds,'stable_reproducibility_materials':aliases,
  'core_results':{'development':{'source_tick':825849,'final_tick':826449,'q':[825905,826103,826307],
    'IZQ0':{'q4_q6':[-1,1,-1],'correct':1,'attempts':3,'inputs_applied':529},
    'NONE':{'q4_q6':[1,1,1],'correct':3,'attempts':3,'inputs_applied':528},
    'SHAM':{'q4_q6':[1,1,1],'correct':3,'attempts':3,'inputs_applied':529},
    'RIGHT':{'q4_q6':[-1,1,1],'correct':2,'attempts':3,'inputs_applied':529}},
   'reserved_wait11':{'q':[825916,826114,826318],'IZQ7':[-1,1,-1],'NONE':[1,1,1],
     'inputs_applied':[529,528],'ticks_each':611,'wait13':'PREPARED_NOT_EXECUTED_PROSPECTIVE_SUBSET'},
   'formed_interruption':{'q':826508,'counterflow':1,'sham':-1,'ticks_each':201,'inputs_each':177,
     'scope':'External legal diagnostic input, not acquired repair'},
   'coarse_cloud':{'execution':info(P/'control/PI06_AMBIENTE_NUBE_R06.json'),'primary':cp,
     'status':coarse['status'],'ticks':67,'births':cr['birth_inputs'],'final_RAW_support':cr['host_safety_observations'][-1]['RAW_nonzero_support'],
     'FI_executed':False,'C2C_executed':False,'no_cognitive_retention_or_loss_scored':True},
   'fine_cloud':{'execution':info(P/'control/PI06_CONFIRMACION_FINA_R04.json'),'primary':fp,
     'status':fine['status'],'ticks':15,'births':fr['birth_inputs'],'previous_RAW_support':fr['host_safety_observations'][-2],
     'first_over_3000':fr['host_safety_observations'][-1],'FI_executed':False,'C2C_executed':False},
   'existing_control':{'execution':info(P/'control/PI06_CONFIRMACION_CONTROL67_R04.json'),'status':control['status'],
     'total_ticks':1300,'environment67':{'primary':ep,'births_requested':0,'RAW_support_min':min(x['RAW_nonzero_support']for x in er['host_safety_observations']),
       'RAW_support_max':max(x['RAW_nonzero_support']for x in er['host_safety_observations'])},
     'FI':{'primary':fip,'ticks':fia['after_tick']-fia['before_tick'],'q':fir['calendar']['query_tick'],
       'normalizer_wait':fir['calendar']['timing']['wait_ticks'],'q4':fir['early_physical_choice'],'q6':fir['old_q6_choice'],'inputs':fir['Native_inputs']},
     'C2C':{'primary':c2p,'ordinal':c2r['ordinal'],'public_spec':c2r['spec'],'first_motor':c2r['first_motor'],
       'actual_operation':c2r['selected_operation'],'actual_numeric_result':c2r['actual_numeric_result'],
       'second_motor':c2r['second_motor'],'product':c2r['actual_effect']['product'],'input_summary':c2r['native_input_summary'],
       'actual_ticks':c2a['after_tick']-c2a['before_tick'],'prospective_limit':800,'excess_ticks':231,
       'prepared_query_tick':c2r['calendar']['query_tick'],'wait_from_before_to_query':c2r['calendar']['query_tick']-c2a['before_tick'],
       'same_history_learned_reference_delta_preserved':-4},
     'protocol_error_preserved':control['error'],'full_plan_completed_flag_means_requests_exist_not_gate_pass':True,
     'no_retry_no_retrospective_bound_change':True}},
  'Native_tick_accounting':reg['latest_closed_science'],
  'incorporation_scope':'No PI06 Native life promoted. A verified RP diagnostic reproduction and scientific evidence do not add acquired regulation to the main.',
  'scientific_limits':['Branches share their prefix; no independent organism count.',
    'Intermediate correct FI is phase-dependent access, not durable repair.',
    'Counterflow is an operator intervention followed by Native dynamics, not autonomous recovery.',
    'Cloud activation and SEM7 are physical descriptors, not demonstrated knowledge or functional gain.',
    'Coarse/fine cloud branches never ran FI or C2C after their safety stops.',
    'The no-supply control produced a useful real chain but violated the campaign time bound; do not mark its whole protocol passed.',
    'No new main panel12 was run in PI06; prior PI05 coverage keeps its original cuts.'],
  'next_resume':'Continue the protected PI05 main only under its existing contract; diagnose/replay PI06 in explicit new diagnostic destinations. No more Native after this campaign closure.',
  'this_map_generation_Native_ticks':0,'is_executable_backup':False}
 addition=P/'control/INCORPORACION_REPRODUCIBILIDAD_INSTRUMENTAL_PI06_R01.json'
 if addition.exists():
  ad=read(addition)
  if ad.get('applied')is not True or ad.get('new_ticks')!=0 or ad.get('principal_or_selectors_modified')is not False:raise ValueError('Do not claim an unverified instrumental deployment')
  continuity['actual_instrumental_incorporation']={'proof':info(addition),'catalog_entry_ids':ad['catalog_entry_ids'],
   'contract':ad['contract'],'contract_sha256':ad['contract_sha256'],'code_capsule':ad['code_capsule'],
   'capsule_manifest_sha256':ad['capsule_manifest_sha256'],'code_members_verified':ad['code_members_verified'],
   'Native_ticks':0,'principal_or_selectors_modified':False,'product_dispatchers_modified':ad['product_dispatchers_modified'],
   'scope':ad['scope'],'not_a_new_Main_acquisition':True}
 portable=P/'control/PRUEBA_PORTABLE_PRIMARIOS_R01/RESULTADO.json'
 if portable.exists():
  pv=read(portable)
  if pv['Native_ticks_from_actual_material_intervals']!=7882 or pv['worlds']!=12 or pv['FI_fixed_RAW_reader_checks']!=24:raise ValueError('Do not claim an unverified portable recount')
  continuity['portable_recount_actual']={'result':info(portable),'Native_executed':False,
   'native_intervals_recounted':7882,'worlds':12,'fixed_FI_RAW_reader_checks':24,
   'direct_current_Native_receipts':pv['direct_current_Native_receipts'],
   'scope':'Executed on 41 copied primaries and one copied 64-byte product. Final extraction/fence verification is a separate delivery check.'}
 write_json(P/'mapas/CONTINUIDAD_PI06.json',continuity)
 matrix=[]
 def row(family,before,observation,evidence,limits,main_status):matrix.append({'familia':family,'antes':before,'observado_PI06':observation,'fuente_localizador':evidence,'limites_asistencia':limits,'incorporacion_al_principal':main_status})
 row('Continuidad','PI05 Main N67 T824911 COMMITTED','Mismo ID, N, T y snapshot af74; ninguna promoción PI06','CONTINUIDAD_PI06.json#/main','Sólo diagnóstico en 12 mundos; no consultas materiales al principal','Sin modificación física')
 row('Evolución sin nuevos paquetes','Historia física y referencias adquiridas heredadas','938 ticks por brazo; 106→105 activos; RAW, clocks y prefijo Native exactos entre normal y global','control/CONTRASTE_BASELINE_COMPLETO_PI06_R01.json','Metadatos de identidad, servicio y segmentación R04 distintos; no iniciativa útil demostrada','No nueva capacidad adquirida')
 row('Interferencia situada','Comparación FI preparada y referencia adquirida','IZQ0: −,+,− (1/3); NONE: +,+,+ (3/3); SHAM: +,+,+ (3/3); DER: −,+,+ (2/3); mismos q','control/RECALCULO_DESARROLLO_CUATRO_BRAZOS_PI06_R01.json','12 intentos en cuatro futuros con prefijo compartido; no sujetos independientes. Un acierto intermedio no es reparación','Mecanismo experimental localizado')
 row('Reserva local','Dosis 0, datos 14/3 y calendario de desarrollo','Carga 7, datos 20/7 y espera 11: IZQ conserva −,+,− frente a NONE +,+,+','control/RECALCULO_RESERVA11_PI06_R01.json','Variación conjunta; no factorial independiente ni espera 13 ejecutada','No promovida')
 row('Interrupción causal','Portador activo +Z formado en T826449','Contraflujo legal: contacto estacionario que desaparece al paso siguiente; FI +1 frente a sham −1','control/RECALCULO_CAUSAL_INTERRUPCION_PI06_R02.json','177/177 entradas por brazo, 201 ticks; intervención externa, no reparación aprendida','Herramienta diagnóstica')
 row('Reproducción utilizable','Prefijo completo T825849 y código R01 preservados','RP Native: 600 ticks, 529 aplicadas, secuencia −,+,− y estado Native exacto','control/REPLAY_RP_PI06_PASIVIDAD_COMPLETA_R01.json','Tres coincidencias de reproducción incluyen dos fallos funcionales; no son 3/3 aciertos de función','Medio de reproducción; no aprendizaje nuevo del principal')
 row('Organización material exógena','Semilla 61001, p=0.4, 61 fuentes preparadas','58 aplicadas y 3 rechazadas por ocupación; soporte RAW 309→297471 en 67 ticks; SEM7 registrado: 5636','control/CRECIMIENTO_NUBE_RECALCULADO_PI06_R03.json','Parada de seguridad del anfitrión; sin FI ni C2C; autonomía y utilidad cognitiva no demostradas','No promovida')
 row('Confirmación de límite','Misma fixture y prefijo; seguridad anterior cada 67 ticks','Seguridad cada tick: soporte 2372 a +14 y 3007 a +15; se detiene','control/PI06_CONFIRMACION_FINA_R04.json','No se baja dosis ni cambia semilla; sin prueba funcional; el paro es del anfitrión','No autorregulación')
 row('Uso funcional sin nube','C2C adquirido y cadenas asistidas existentes','Control: soporte 309; FI +1 con 176 entradas; Native DIF 30/7→23→MU +1→producto 64 B, 186 entradas','control/PI06_CONFIRMACION_CONTROL67_R04.json#/outcomes','C2C: 1031 ticks > máximo 800; plan FAILED_PRESERVED. Secuencia y calendario preparados; no nueva estrategia','Disponibilidad puntual experimental; no promoción')
 if addition.exists():row('Incorporación instrumental','RP y catálogo previos preservados','Dos entradas instrumentales/P0, contrato, cápsula de 304 archivos y recetas preparadas o bloqueadas','control/INCORPORACION_REPRODUCIBILIDAD_INSTRUMENTAL_PI06_R01.json','0 ticks; no cambios del principal ni de sus selectores; no convertir receta preparada en replay verificado','Medios científicos incorporados; ninguna adquisición mental nueva')
 write_csv(P/'mapas/MATRIZ_ANTES_DESPUES.csv',matrix)
 coverage=[
  {'fuente':'Cognitive Manual DCS11-MM-001','cobertura_PI06':'Identidad, edición, hash y continuidad heredada; no nueva lectura integral declarada por este subagente','modalidad':'Metadatos actuales y reutilización PI05','localizador':manual['path'],'alcance':'Manual completo literal en entrega; revisión visual no atribuida'},
  {'fuente':'Thinking 4.5 MAR/LBM y corpus CORE/Ingenierías','cobertura_PI06':'Reutilización de cobertura PI01/PI02/PI03; reaperturas dirigidas de F1','modalidad':'Antecedentes reutilizados y lectura dirigida por F1','localizador':'fuentes/; INFORME_CIENTIFICO_PI06.md','alcance':'No nuevo censo ni lectura total del corpus'},
  {'fuente':'acceso_eci01.py','cobertura_PI06':'Funciones completas de lector q4/q6 y balance','modalidad':'Lectura estática dirigida','localizador':'Cognitive/sistema/capacidades/acceso_eci01.py','alcance':'Decodificador fijo; no recibe operandos ni respuesta esperada'},
  {'fuente':'percepcion_cruda_fi01.py','cobertura_PI06':'Geometría, declaración, submit y frame; geometry recalculada como AST aislado','modalidad':'Lectura estática y recálculo puro','localizador':'fuentes/SINTESIS_C2_E3_PI06_R01.json#/directed_readings','alcance':'No se importó el módulo DEE para ese recálculo'},
  {'fuente':'Runtime y kernel congelados','cobertura_PI06':'Admisión RAW!=0; Materia, XNOR, copia y DEMUX dirigidos por Root/F1','modalidad':'Lectura estática y testigo local sobre datos congelados','localizador':'fuentes/F1_TESTIGO_COPIA_Y_SUPERVIVENCIA_PI06.json','alcance':'No aislar una rama única para toda la expansión'},
  {'fuente':'Baseline 2×938','cobertura_PI06':'Primarios y snapshots completos contrastados; 25 fotogramas globales','modalidad':'Ejecución Root y recálculo pasivo','localizador':'control/CONTRASTE_BASELINE_COMPLETO_PI06_R01.json','alcance':'Pasividad acotada; diferencias de metadatos explícitas'},
  {'fuente':'Desarrollo de cuatro brazos y reserva 11','cobertura_PI06':'Todos los primarios y recibos directos recuentados; 207 fotogramas de IZQ','modalidad':'Ejecución Root y recálculo','localizador':'control/RECALCULO_DESARROLLO_CUATRO_BRAZOS_PI06_R01.json; control/RECALCULO_RESERVA11_PI06_R01.json','alcance':'No se declara análisis científico completo de las capturas de los otros brazos'},
  {'fuente':'Interrupción en dos brazos','cobertura_PI06':'Todos los primarios y 177 recibos por caso; 12 fotogramas seleccionados verificados','modalidad':'Ejecución Root y recálculo pasivo','localizador':'control/RECALCULO_CAUSAL_INTERRUPCION_PI06_R02.json','alcance':'Ocho fotogramas de interrupción exhaustivos y cuatro FI iniciales; resto FI no leído aquí'},
  {'fuente':'RP 600','cobertura_PI06':'Testigo cerrado y comparación Native completa','modalidad':'Reproducción Root y comprobación pasiva','localizador':'control/REPLAY_RP_PI06_PASIVIDAD_COMPLETA_R01.json','alcance':'Recalcular JSON no reproduce el motor'},
  {'fuente':'Nube gruesa','cobertura_PI06':'61 recibos y 12 fotogramas completos: 0..10 y 67','modalidad':'Ejecución Root y recálculo pasivo','localizador':'control/CRECIMIENTO_NUBE_RECALCULADO_PI06_R03.json','alcance':'Hueco 10→67 sin interpolación; FI y C2C no ejecutados'},
  {'fuente':'Confirmación fina R04','cobertura_PI06':'Primario, recibos y 16 fotogramas por F1; prefijo 0..10 comparado','modalidad':'Ejecución Root y recálculo F1','localizador':'control/CONFIRMACION_FINA_RECALCULADA_PI06_R04.json','alcance':'Parada del anfitrión a +15; ninguna prueba cognitiva'},
  {'fuente':'Control 67, FI y C2C','cobertura_PI06':'Los tres primarios completos leídos; recibos y efecto real contrastados','modalidad':'Ejecución Root y recálculo sin Native','localizador':'control/PI06_CONFIRMACION_CONTROL67_R04.json','alcance':'Plan fallido por horizonte; producto útil observado no ocultado'},
  {'fuente':'Nuevos R01/R02/R03/R04 y protocolos','cobertura_PI06':'Lectura, implementación y pruebas simuladas explícitas','modalidad':'Código estático y pruebas puras','localizador':'codigo/; control/*PRUEBAS_PURAS*','alcance':'Los mocks no son pruebas Native ni aprendizaje'}]
 write_csv(P/'mapas/FUENTES_Y_COBERTURA.csv',coverage)
 print(json.dumps({'Native_ticks':ticktotal,'worlds':len(worlds),'maps':[info(P/'mapas'/name)for name in('CONTINUIDAD_PI06.json','MATRIZ_ANTES_DESPUES.csv','FUENTES_Y_COBERTURA.csv')],'Native_executed_by_this_tool':False}))
if __name__=='__main__':main()
