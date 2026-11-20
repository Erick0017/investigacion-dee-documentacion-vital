"""Seal the private analysis without importing or running the native engine."""
from pathlib import Path
import argparse,ast,collections,ctypes,difflib,hashlib,json,os,platform,shutil,subprocess,sys,time,zipfile

def digest(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def prepare(a):
 root=a.root.resolve();camp=root/'laboratorio/campanas/ESPANOL_FUNCIONAL_01';ev=root/'evidencia/campanas/ESPANOL_FUNCIONAL_01';stage=a.stage.resolve();stage.mkdir(parents=True,exist_ok=False);sources=[];omitted=[]
 def copy(source,relative,role):
  target=stage/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
  if digest(source)!=digest(target):raise ValueError('Nonidentical copy '+str(source))
  sources.append({'member':relative,'source':str(source),'bytes':source.stat().st_size,'sha256':digest(source),'role':role,'byte_exact_copy':True})
 def omit(source,reason):omitted.append({'source':str(source),'bytes':source.stat().st_size,'sha256':digest(source),'reason':reason})
 for p in sorted(ev.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(ev).as_posix()
  if p.suffix=='.gz':omit(p,'Complete diagnostic checkpoint retained locally; no snapshot duplicated in analysis')
  elif p.name not in('INDICE_EVIDENCIA.json',):copy(p,'EVIDENCIA_PRIMARIA/'+rel,'Original campaign measurement, resource report, control, failure or CLI output')
 for p in sorted(camp.rglob('*')):
  if not p.is_file()or'__pycache__'in p.parts:continue
  rel=p.relative_to(camp).as_posix()
  if p.suffix=='.py'or p.parent.name=='incidentes':copy(p,'CODIGO_EXPERIMENTAL/'+rel,'Experimental source including superseded methods and technical incidents')
  elif p.name.startswith('CRITERIOS_')or p.name=='PRESUPUESTO.json':copy(p,'CONFIGURACION/'+rel,'Frozen criteria or original campaign budget')
 for name in('espanol_funcional_01.py','ensenanza_relacional_02.py','ensenanza_lexica_03.py','igualdad_fisica_03.py','puente_lexico_10.py','recuperacion_magnitud_26.py','NSM65_ACTUALIZACIONES_ESPANOL_01.json'):
  copy(root/'sistema/capacidades'/name,'CAPA_SISTEMA/capacidades/'+name,'Installed optional campaign component or affected NSM overlay')
 for rel in('gestionar.py','contratos/ESPANOL_FUNCIONAL_01.json','app/lives.py','app/native_tools.py','app/process_control.py','app/access_guard.py','app/ESPANOL_FUNCIONAL_01_CONTINUAR.eventos','capacidades/puente_adquirible.py'):
  copy(root/'sistema'/rel,'CAPA_SISTEMA/'+rel,'Existing operational contract/continuity helper or changed common entry')
 helpers=['front_relations/src/tiled_order.py','front_relations/src/tiled_order_parallel.py','base_validada/cpc8/src/integracion/relational_pair.py','base_validada/cpc8/src/integracion/quantity_core.py']
 for rel in helpers:copy(root/'sistema/organizaciones/cpc9'/rel,'RECETAS_DE_REFERENCIA/'+rel,'Exact prepared event geometry or finite comparison contract used by experimental source')
 copy(root/'sistema/capacidades/NSM65_CATALOGO_OFICIAL.json','NSM65_CATALOGO_ORIGINAL.json','Unchanged linguistic catalogue; not65learned meanings')
 for name in('ADDENDUM_MANUAL_ESPANOL_FUNCIONAL_01.md','CONTINUIDAD_ESPANOL_FUNCIONAL_01.json'):
  copy(root/name,name,'Manual addendum or current complete-state pointer, not the complete snapshot')
 copy(camp/'INFORME_RESULTADOS.md','INFORME_RESULTADOS.md','Results, interpretation and limits')
 copy(camp/'recalcular.py','recalcular.py','Engine-free recalculation entry')
 for name in('DECISION_INCORPORACION.json','AUDITORIA_FLUJOS.json','CAMBIOS_CAPACIDADES_POR_VIDA.json','REANUDACION.json'):
  if(camp/name).exists():copy(camp/name,name,'Campaign decision, access attribution or continuity')
 # Catalogue rows are preserved in the system; the compact extension contract is sufficient here.
 copy(root/'sistema/capacidades/CATALOGO_CAPACIDADES.json','CATALOGO_CAPACIDADES_ACTUAL.json','Registry with previous entries unchanged and additive campaign extension')
 baseline=root/'entregas/DEE_COGNITIVE_SYSTEM_1_1_SISTEMA.zip';patch=[];baseline_checks={}
 with zipfile.ZipFile(baseline)as z:
  for rel in('gestionar.py','capacidades/CATALOGO_CAPACIDADES.json','capacidades/NSM65_CATALOGO_OFICIAL.json'):
   matches=[n for n in z.namelist()if n.endswith('/sistema/'+rel)or n=='sistema/'+rel]
   if len(matches)!=1:raise ValueError('Ambiguous original system member '+rel)
   old=z.read(matches[0]);new=(root/'sistema'/rel).read_bytes();baseline_checks[rel]={'original_member':matches[0],'original_sha256':hashlib.sha256(old).hexdigest(),'current_sha256':hashlib.sha256(new).hexdigest(),'byte_identical':old==new}
   if old!=new:patch.extend(difflib.unified_diff(old.decode('utf-8-sig').splitlines(True),new.decode('utf-8-sig').splitlines(True),fromfile='sealed_1_1/'+rel,tofile='campaign_current/'+rel))
 (stage/'CAMBIOS_SOBRE_SISTEMA_SELLADO.patch').write_text(''.join(patch),encoding='utf8')
 # Every new operational state is indexed, not copied per view or per tick.
 lives=[];selected={'E1_SOCIAL_11','E1_ESPANOL_01','ES01_CONTACT_RETURN27_refree','ES01_MAG_RELEARN26_paired_guard','ES01_LATE_ACCESS29_passive'}
 for p in sorted((root/'sistema/estado/vidas').glob('*/VIDA.json')):
  if not(p.parent.name.startswith('ES01_')or p.parent.name=='E1_ESPANOL_01'or p.parent.name=='E1_SOCIAL_11'):continue
  d=read(p);life=d['life_id'];snapshot=root/'sistema'/d['snapshot']
  if digest(snapshot)!=d['snapshot_sha256']:raise ValueError('Recorded snapshot bytes differ '+life)
  lives.append({'life_id':life,'branch':d['branch'],'parent':d.get('parent'),'profile':d['profile'],'tick':d['physical']['tick'],'physical':d['physical'],'snapshot':str(snapshot),'snapshot_bytes':snapshot.stat().st_size,'snapshot_sha256':d['snapshot_sha256'],'last_operation':d.get('operations',[{}])[-1].get('kind'),'knowledge_note':'Do not infer capabilities from a name, tick or installed catalogue. Follow the actual trial/access records.'})
  if life in selected:
   copy(p,'ESTADOS_DOCUMENTALES/'+life+'/VIDA.json','Exact operational life record; snapshot omitted')
   hist=p.parent/'HISTORIA.jsonl'
   if hist.exists():copy(hist,'ESTADOS_DOCUMENTALES/'+life+'/HISTORIA.jsonl','Exact native-state commit chain, not full world bytes')
 # Include hashes of every campaign checkpoint, including older boundaries.
 for p in sorted((root/'sistema/estado/checkpoints').glob('*')):
  if p.is_file()and(p.name.startswith('ES01_')or p.name.startswith('E1_ESPANOL_01.')):omit(p,'Full native operational state retained under sistema; analysis is not a life transport package')
 listed={x['source']for x in omitted}
 for item in lives:
  if item['life_id']in selected and item['snapshot']not in listed:omit(Path(item['snapshot']),'Selected complete state retained locally; pointer and exact hash included, not world bytes')
 state=read(root/'sistema/estado/vidas/E1_SOCIAL_11/VIDA.json')
 if state['snapshot_sha256']!='51e2ec6a41f906607848c003c6a22e3e33690f57d20dcae90c8dbbc7ab9ad396'or state['physical']['tick']!=3154:raise ValueError('Protected default life differs from campaign start')
 copy(root/'sistema/estado/ACTIVO.json','ESTADO_PREDETERMINADO_PROTEGIDO.json','Unchanged default selection')
 manual=root/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_0.docx'
 if digest(manual)!='f0d1a71f8dc4aa8d9d72aa1428b9ed62df320897ce4987353122539285f2e6e5':raise ValueError('Received manual was altered')
 omit(manual,'Original received manual preserved at system root; precise addendum included instead of duplicate Word')
 omit(baseline,'Existing whole-system sealed package not nested or rebuilt')
 for p in(root/'sistema/runtime').rglob('*.whl'):omit(p,'Official instrument retained once in operational system; no engine in analysis')
 identity=read(ev/'CONTINUIDAD_API_18/0.stdout.json')['INSTRUMENTO']['engine'];native=Path(identity['native'])
 if digest(native)!='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d':raise ValueError('Native instrument changed')
 omit(native,'Installed official native engine; not part of analysis')
 if a.kernel_source:
  if digest(a.kernel_source)!='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31':raise ValueError('Frozen source changed')
  omit(a.kernel_source,'Frozen kernel identity only; no kernel code included')
 write(stage/'IDENTIDAD_Y_PRESERVACION.json',{'instrument':identity,'baseline_contract_checks':baseline_checks,'official_nsm_catalogue_unchanged':baseline_checks['capacidades/NSM65_CATALOGO_OFICIAL.json']['byte_identical'],'stable_original_unchanged':True,'received_manual_unchanged':True,'no_34_family_rerun':True,'system_entry_imports_no_lab_or_audit_for_normal_operations':True})
 write(stage/'VIDAS_Y_GENEALOGIA.json',lives)
 # All case executions and CLI operations, including pre-physics and post-save technical failures.
 trials=[];episodes=[]
 for p in sorted(ev.rglob('EJECUCION.json')):
  for row in read(p)['cases']:
   primary=p.parent/row['case']/'PRIMARIOS.json';d=read(primary)if primary.exists()else{};result=d.get('commit',{}).get('result',{})
   trials.append({'family':p.parent.relative_to(ev).as_posix(),'case':row['case'],'kind':'SUPERVISED_CASE','exit_code':row['exit_code'],'seconds':row['seconds'],'primary':primary.relative_to(ev).as_posix()if primary.exists()else None,'life':d.get('life'),'parent_life':d.get('parent',{}).get('life_id'),'parent_tick':d.get('parent',{}).get('physical',{}).get('tick'),'final_tick':d.get('post',{}).get('tick',d.get('commit',{}).get('INSTRUMENTO',{}).get('tick')),'recorded_summary_not_verdict':result,'code_sha256_recorded':d.get('code_sha256'),'technical_failure_after_primary_saved':row['exit_code']!=0 and bool(d),'resources':row.get('resources'),'owned_job_closed':row.get('owned_job_closed')})
   for key in('episodes','queries','phases','frames'):
    for i,item in enumerate(d.get(key,[])):
     episodes.append({'primary':primary.relative_to(ev).as_posix(),'locator':'$.'+key+'['+str(i)+']','label':item.get('label',item.get('episode',item.get('round',i))),'tick':item.get('tick',item.get('word_tick',item.get('block_end'))),'parent_case':row['case'],'kind':key})
 already={r.get('primary')for r in trials if r.get('primary')}
 for p in sorted(ev.rglob('PRIMARIOS.json')):
  rel=p.relative_to(ev).as_posix()
  if rel in already:continue
  d=read(p);trials.append({'family':p.parent.relative_to(ev).as_posix(),'case':d.get('case',d.get('case_id',d.get('life',p.parent.name))),'kind':'STANDALONE_SAVED_NATIVE_RECORD','exit_code':None,'seconds':None,'primary':rel,'life':d.get('life'),'parent_life':d.get('parent',{}).get('life_id'),'parent_tick':d.get('parent',{}).get('physical',{}).get('tick'),'final_tick':d.get('post',{}).get('tick',d.get('commit',{}).get('INSTRUMENTO',{}).get('tick')),'recorded_summary_not_verdict':d.get('commit',{}).get('result',{}),'code_sha256_recorded':d.get('code_sha256'),'native_record_saved':True,'missing_process_metadata_not_invented':True})
  for key in('episodes','queries','phases','frames','teaching','lessons','reads','trials','rounds'):
   values=d.get(key,[])
   if not isinstance(values,list):continue
   for i,item in enumerate(values):
    if isinstance(item,dict):episodes.append({'primary':rel,'locator':'$.'+key+'['+str(i)+']','label':item.get('label',item.get('episode',item.get('round',i))),'tick':item.get('tick',item.get('word_tick',item.get('block_end'))),'parent_case':d.get('case',p.parent.name),'kind':key})
 for p in sorted(ev.rglob('RUTAS.json')):
  for i,d in enumerate(read(p)):
   trials.append({'family':p.parent.relative_to(ev).as_posix(),'case':d['case'],'kind':'ROUTE_DIAGNOSTIC_RECORD','exit_code':None,'seconds':None,'primary':p.relative_to(ev).as_posix(),'locator':'$['+str(i)+']','life':d['case'],'native_record_saved':True,'missing_process_metadata_not_invented':True})
   for j,row in enumerate(d.get('frames',[])):episodes.append({'primary':p.relative_to(ev).as_posix(),'locator':'$['+str(i)+'].frames['+str(j)+']','tick':row.get('tick'),'parent_case':d['case'],'kind':'route_frame'})
 for p in sorted(ev.rglob('COMANDOS.json')):
  for i,row in enumerate(read(p)):
   trials.append({'family':p.parent.relative_to(ev).as_posix(),'case':'command_'+str(i),'kind':'PUBLIC_CLI_NEW_PROCESS','exit_code':row['exit_code'],'seconds':row['seconds'],'command':row['command'],'primary':(p.parent/row['stdout']).relative_to(ev).as_posix(),'stderr':(p.parent/row['stderr']).relative_to(ev).as_posix(),'resources':row.get('resources'),'owned_job_closed':row.get('owned_job_closed')})
 write(stage/'TABLA_ENSAYOS.json',{'case_rows':trials,'subtrial_locators':episodes,'denominator_warning':'Cases, queries, deterministic replays and exact forks are not independent biological/statistical samples. Do not sum their knowledge.'})
 md=['# Tabla de ensayos y operaciones','', 'Cada fila remite a los datos exactos. Salida de proceso no equivale a conclusión científica. Las subpruebas, fases y episodios tienen localizadores en TABLA_ENSAYOS.json.','', '| Familia | Caso | Tipo | Salida | Segundos | Datos |','|---|---|---|---:|---:|---|']
 for t in trials:md.append('| '+t['family']+' | '+str(t['case'])+' | '+t['kind']+' | '+str(t['exit_code'])+' | '+(format(t['seconds'],'.3f')if t['seconds']is not None else'No registrado')+' | '+(t.get('primary')or'Fallo técnico sin PRIMARIOS')+' |')
 (stage/'TABLA_ENSAYOS.md').write_text('\n'.join(md)+'\n',encoding='utf8')
 # Source coverage: distinguish recorded identities from actual bytes available now.
 by_hash=collections.defaultdict(list)
 for item in sources:
  if item['member'].endswith(('.py','.txt')):by_hash[item['sha256']].append(item['member'])
 coverage=[]
 for p in sorted(ev.rglob('PRIMARIOS.json')):
  d=read(p);recorded={}
  if d.get('code_sha256'):recorded['runner']=d['code_sha256']
  for key in('dependency_sha256','dependencies'):
   for name,value in d.get(key,{}).items():
    if isinstance(value,str)and len(value)==64:recorded[name]=value
  coverage.append({'primary':p.relative_to(ev).as_posix(),'recorded_sources':[{'name':k,'sha256':h,'matching_included_bytes':by_hash.get(h,[]),'state':'BYTE_IDENTICAL_INCLUDED'if h in by_hash else'RECORDED_HASH_ONLY_OLDER_REVISION_NOT_ALL_BYTES_RECOVERED'}for k,h in recorded.items()]})
 write(stage/'COBERTURA_CODIGO.json',{'files':coverage,'scope':'All experimental runners and current system components are included. Some past cumulative helper revisions were not archived byte-for-byte; do not claim this ZIP re-executes every historical revision from T0. Exact old primary bytes, state hashes and current recipes are preserved.'})
 claims=[
  ('LEXICO_ADQUIRIDO',['LEXICO_ARBITRARIO_04','LEXICO_RESERVAS_05'],'Post-event arbitrary nativeX code; wrong teacher changes emitted word, no-cue/event controls distinguish acquisition','Not universal Spanish or a learned perceptual geometry'),
  ('CUATRO_CONTEXTOS',['INTEGRACION_PUENTE_12'],'All routes,10/10 trained scenes,2untrained abstentions; selective bus cut and sham','Finite panel, three physical scene presentations, not generalization to all places'),
  ('DOSIS_LARGA',['CONTINUIDAD_LEXICA_06','CONTINUIDAD_SIN_SONDAS_07'],'Matched24scene/402tick blocks,18correct6abstentions in four futures','Futures not independent samples; query dose did not solve missing+5access'),
  ('CONTACTO_Y_REAPRENDIZAJE',['CONTACTO_TARDIO_R4','CONTACTO_ACCESO_R5','RETORNO_CONTACTO_27'],'First response versus later probes; contact/free-flight, explicit late re-acquisition','No general negation; later query may teach and later access can fail again'),
  ('ORDEN_Y_COMPOSICION',['TIEMPO_TARDIO_01','MAIN_TIEMPO_03','COMPOSICION_01','TIEMPO_LEXICO_20'],'Native order histories, coincidence with contact and consequence, partial later arbitrary-word teaching','No learned grammar; original no-signal positive limits word-binding attribution'),
  ('SOCIAL',['COMUNICACION_CONTACTO_01','SOCIAL_CAUSA_RESIDUO_03','SOCIAL_RESERVAS_04','COMPRENSION_Y_SOCIAL_13'],'Native message transmission, storage and subsequent use, cut/sham and incompatible token','B not a complete mind or a general distance knower; receiver cue not universally necessary'),
  ('ACTUADOR',['ACCION_LEIDA_16'],'Native word match can survive while old actuator entry is occupied; lead1 versus equal-dose offpath','Consumptive operation, no hidden repair or continued old-reader guarantee'),
  ('PERDIDA_Y_ACCESO',['TRAZA_NEAR5_09','CAUSA_COLISION_10','PUENTE_LEXICO_10','PUENTE_LEXICO_11'],'Microscopic native collision and alternate access with omitted cue/cut/sham controls','No owner inferred only by equal load; alternate access finite and prepared'),
  ('REFERENCIA_CAUSAL',['PANEL_CONTINUIDAD_19','DIAGNOSTICO_MAGNITUD_21','REFERENCIA_PASIVA_22','TRAZA_REFERENCIA_SOCIAL_23','TRAZA_REFERENCIA_IGUAL_24','CAUSA_REFERENCIA_25'],'Exact old futures RAW/clocks reproduced; tracked reference changed inT9986, native cut/sham affects later comparisons','No assertion that all information globally disappeared or a single cause explains every interference'),
  ('REAPRENDIZAJE_CUANTITATIVO',['REAPRENDIZAJE_MAGNITUD_26'],'Native explicit reference experience plus R0:10/10 new comparisons versus2/10 or0/10','Relearning, not uninterrupted retention, cardinality or R2'),
  ('DOSIS_TARDIA',['ACCESO_TARDIO_29'],'Same late scene calendar: reduced queries7/8 trained versus6/8 full, all abstain on two untrained; word queries still available','Source bus still absent on last+5; not a complete stability solution'),
  ('CONTINUIDAD_Y_FALLOS_FINALES',['CONTINUIDAD_API_18','API_CIERRE_28','API_RESERVA_FINAL_30'],'New process save/load and actual new use; final free-reader response absent is kept','Default stable life unchanged; no global cognitive release or all-previous-capabilities guarantee')]
 mapped=[]
 for identifier,families,yes,no in claims:
  members=[x for x in sources if any(x['member'].startswith('EVIDENCIA_PRIMARIA/'+family+'/')for family in families)and(x['member'].endswith('PRIMARIOS.json')or x['member'].endswith('.stdout.json'))]
  mapped.append({'claim_id':identifier,'supports':yes,'does_not_support':no,'families':families,'primary_members':[{'member':x['member'],'source':x['source'],'bytes':x['bytes'],'sha256':x['sha256']}for x in members],'calculation_source':'recalcular.py and CALCULOS.json where applicable; exact native records remain available for independent interpretation'})
 write(stage/'AFIRMACIONES_Y_EVIDENCIA.json',mapped)
 write(stage/'INDICE_EVIDENCIA.json',{'sources':sources,'primary_locator_rule':'Member-relative JSON path and array index; source path+hash identifies the unchanged local original','all_campaign_non_snapshot_records_included':True,'native_reproduction_self_contained':False,'calculation_self_contained':True})
 write(stage/'ARCHIVOS_OMITIDOS.json',{'files':omitted,'not_deleted':True,'complete_native_states_included':False,'essential_primary_extraction_loss':False,'old_helper_revision_gap':'See COBERTURA_CODIGO.json; not represented as complete byte-exact historical source recovery'})
 write(ev/'INDICE_EVIDENCIA.json',{'schema':'DCS1.1.EF01.evidence.index.v1','sources':sources,'omitted_from_analysis_not_from_local_system':omitted,'case_count':len(trials),'primary_record_files':len(list(ev.rglob('PRIMARIOS.json'))),'state_transport_self_contained':False})
 budget=read(camp/'PRESUPUESTO.json');counter=ctypes.c_longlong();freq=ctypes.c_longlong();ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(counter));ctypes.windll.kernel32.QueryPerformanceFrequency(ctypes.byref(freq));elapsed=(counter.value-budget['start_monotonic'])/freq.value
 measured=[t for t in trials if t.get('resources')]
 costs={'measured_owned_executions':len(measured),'summed_execution_wall_seconds_not_campaign_wall':sum(t.get('seconds')or 0 for t in measured),'summed_measured_job_cpu_seconds':sum(t['resources'].get('cpu_user_seconds',0)+t['resources'].get('cpu_kernel_seconds',0)for t in measured),'max_measured_job_committed_bytes':max((t['resources'].get('peak_job_committed_bytes',0)for t in measured),default=0),'max_measured_process_committed_bytes':max((t['resources'].get('peak_process_committed_bytes',0)for t in measured),default=0),'all_reported_owned_jobs_closed':all(t.get('owned_job_closed')for t in measured),'unrecorded_execution_costs_not_imputed':True,'job_activity_metrics_are_before_the_recorded_close':True,'not_an_intelligence_speed_benchmark':True}
 write(stage/'RECURSOS_Y_PRESUPUESTO.json',{'original_budget':budget,'closing_monotonic_counter':counter.value,'frequency':freq.value,'elapsed_seconds':elapsed,'remaining_seconds':budget['budget_seconds']-elapsed,'budget_was_not_reset':True,'logical_cpu':os.cpu_count(),'platform':platform.platform(),'max_worker_memory_bytes':4294967296,'measured_costs':costs,'basic_N67_bytes':9624416,'no_energy_measurement':True})
 completed=subprocess.run([sys.executable,'-I','-B',str(stage/'recalcular.py'),'--datos',str(stage/'EVIDENCIA_PRIMARIA'),'--salida',str(stage/'CALCULOS.json')],capture_output=True,text=True,encoding='utf8',timeout=120)
 write(stage/'VERIFICACION_RECALCULO_PRESELLO.json',{'command':completed.args,'exit_code':completed.returncode,'stdout':completed.stdout,'stderr':completed.stderr,'no_native_simulation':True})
 if completed.returncode:raise ValueError('Recalculation failed '+completed.stderr)
 sizes={'included_expanded_bytes_before_manifest':sum(p.stat().st_size for p in stage.rglob('*')if p.is_file()),'exact_source_copies':len(sources),'source_original_bytes':sum(x['bytes']for x in sources),'omitted_local_bytes':sum(x['bytes']for x in omitted),'omitted_files':len(omitted),'all_non_snapshot_case_records':True}
 write(stage/'TAMANOS_Y_ALCANCE.json',sizes)
 (stage/'LEER_PRIMERO.md').write_text('# Español funcional 01\n\nAbra INFORME_RESULTADOS.md. El sistema conserva una vida acumulativa y procedimientos nuevos; los límites y los fallos también se incluyen. TABLA_ENSAYOS.md/JSON enlazan todos los casos, episodios y controles. CALCULOS.json se recalcula sin motor con `python recalcular.py --datos EVIDENCIA_PRIMARIA --salida NUEVO_CALCULO.json`.\n\nEl addendum y la ficha identifican las vidas y snapshots locales. Este análisis NO contiene el motor ni los snapshots completos y NO es un paquete para continuar una vida en otra máquina. No se reconstruyó ni reempaquetó todo el sistema. Los archivos omitidos siguen locales y tienen tamaños y hashes. Sigue siendo material privado, no automáticamente publicable.\n\nLa edición Word recibida se conservó intacta. Se entrega addendum preciso; su integración editorial al DOCX queda pendiente por ausencia del renderizador autorizado.\n',encoding='utf8')
 (stage/'COMPACTACION_Y_OMISIONES.md').write_text('# Compactación y cobertura\n\nSe incluyen sin cambiar sus bytes todos los registros no binarios de ensayo de ESPANOL_FUNCIONAL_01: controles, fracasos, recursos, respuestas y errores técnicos. La compresión ZIP es sin pérdida; no se eliminó un contraejemplo para cumplir el tamaño.\n\nSe excluyen motor, WHL, fuente congelada, ZIP anterior y checkpoints completos; ARCHIVOS_OMITIDOS.json conserva ruta, bytes y SHA-256. Las colas y metadatos necesarios para continuar siguen en los snapshots operativos locales. Los arrays y observaciones del análisis no los reemplazan.\n\nLas fuentes experimentales y componentes actuales están incluidos. COBERTURA_CODIGO.json distingue hashes registrados de revisiones antiguas cuyos bytes exactos no están todos archivados. Por ello no se afirma autosuficiencia para reproducir todas las revisiones históricas ni transportar vidas. El recálculo de las mediciones incluidas sí es independiente del motor.\n',encoding='utf8')
 members=[]
 for p in sorted(stage.rglob('*')):
  if p.is_file():members.append({'member':p.relative_to(stage).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)})
 write(stage/'MANIFIESTO_HASHES.json',{'schema':'DCS1.1.EF01.analysis.manifest.v1','members':members,'excluded_from_own_hash':['MANIFIESTO_HASHES.json'],'zip_hash_is_external':True})
 with zipfile.ZipFile(a.zip,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in sorted(stage.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(stage).as_posix())
 if a.zip.stat().st_size>=16000000:raise ValueError('Candidate exceeds absolute transfer limit; do not publish')
 print(json.dumps({'candidate':str(a.zip),'sha256':digest(a.zip),'compressed_bytes':a.zip.stat().st_size,'expanded_bytes':sum(p.stat().st_size for p in stage.rglob('*')if p.is_file()),'files':sum(p.is_file()for p in stage.rglob('*')),'case_rows':len(trials)},ensure_ascii=False))

def verify(a):
 archive=a.zip.resolve();dest=a.stage.resolve();dest.mkdir(parents=True,exist_ok=False);begin=time.perf_counter();findings=[]
 with zipfile.ZipFile(archive)as z:
  if z.testzip()is not None:raise ValueError('ZIP CRC error')
  for item in z.infolist():
   target=(dest/item.filename).resolve()
   if not target.is_relative_to(dest):raise ValueError('Unsafe ZIP member')
  z.extractall(dest)
  compressed=archive.stat().st_size;expanded=sum(x.file_size for x in z.infolist());count=len(z.infolist())
 manifest=read(dest/'MANIFIESTO_HASHES.json')
 for item in manifest['members']:
  p=dest/item['member']
  if p.stat().st_size!=item['bytes']or digest(p)!=item['sha256']:raise ValueError('Member mismatch '+item['member'])
 text_count=0;json_count=0;code_count=0
 for p in dest.rglob('*'):
  if not p.is_file():continue
  if p.suffix in('.json','.jsonl','.py','.md','.txt','.log','.patch'):
   body=p.read_text(encoding='utf-8-sig');text_count+=1
   if p.suffix=='.json':json.loads(body);json_count+=1
   elif p.suffix=='.jsonl':
    for line in body.splitlines():
     if line.strip():json.loads(line)
   elif p.suffix=='.py':ast.parse(body,filename=str(p));code_count+=1
 out=dest.parent/(dest.name+'_RECALCULO_EXTERNO.json');done=subprocess.run([sys.executable,'-I','-B',str(dest/'recalcular.py'),'--datos',str(dest/'EVIDENCIA_PRIMARIA'),'--salida',str(out)],capture_output=True,text=True,encoding='utf8',timeout=120)
 if done.returncode:raise ValueError('Extracted recalc failed '+done.stderr)
 if digest(out)!=digest(dest/'CALCULOS.json'):raise ValueError('Extracted recalculation differs')
 report={'status':'VERIFIED_ANALYSIS_CONTENT_NOT_ENGINE_RELEASE','zip':str(archive),'zip_sha256':digest(archive),'compressed_bytes':compressed,'absolute_limit_bytes':16000000,'under_absolute_limit':compressed<16000000,'expanded_bytes':expanded,'file_count':count,'crc_all_members_ok':True,'manifest_members_verified':len(manifest['members']),'utf8_text_members_read':text_count,'json_parsed':json_count,'python_sources_parsed':code_count,'extraction':str(dest),'recalculation_command':done.args,'recalculation_exit_code':done.returncode,'recalculation_stdout':done.stdout,'recalculation_byte_identical':True,'seconds':time.perf_counter()-begin,'native_simulation_repeated_for_archive':False,'native_engine_and_snapshots_not_included':True,'limits':['Not a complete system distribution','Not sufficient to continue a life without full local snapshots','No general mind, R2, human semantics or unlimited stability certification','Older cumulative helper source revisions not all byte-exact recoverable; see source coverage']}
 budget=read(dest/'RECURSOS_Y_PRESUPUESTO.json')['original_budget'];counter=ctypes.c_longlong();freq=ctypes.c_longlong();ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(counter));ctypes.windll.kernel32.QueryPerformanceFrequency(ctypes.byref(freq));elapsed=(counter.value-budget['start_monotonic'])/freq.value
 report['campaign_budget']={'original_start_utc':budget['start_utc'],'original_deadline_utc':budget['deadline_utc'],'elapsed_seconds_including_this_verification':elapsed,'budget_seconds':budget['budget_seconds'],'within_budget':elapsed<=budget['budget_seconds'],'not_reset':True}
 write(a.report,report);print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','verify']);p.add_argument('--root',type=Path);p.add_argument('--stage',type=Path,required=True);p.add_argument('--zip',type=Path,required=True);p.add_argument('--kernel-source',type=Path);p.add_argument('--report',type=Path);a=p.parse_args();prepare(a)if a.action=='prepare'else verify(a)
