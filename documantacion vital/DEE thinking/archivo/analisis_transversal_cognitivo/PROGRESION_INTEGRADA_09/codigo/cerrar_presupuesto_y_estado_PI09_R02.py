"""Cierre Root-only RO de estado/presupuesto; por defecto no lee estados.

Después de selected0, publicación1.38 y sincronizaciónR03. No abre Native,
no escribe SQLite/ACTIVO/fichas/snapshots. Actualizar REGISTRO y generar una
ficha LEER_PRIMERO requieren sus flags explícitos separados de Root.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,hashlib,importlib.util,json,os,sqlite3
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';RP=C/'reproducibilidad';REG=P/'REGISTRO_CAMPANA.json';OUTPUT=P/'control/CIERRE_PRESUPUESTO_Y_ESTADO_PI09_R01.json'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01';PARENT='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01';A='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01';LEDGER_SHA='bb1f326aa981ba00b9a6e3417700cca31d92a0d28a6e8a5ad601042bf2a26260';PROCESS_SHA='9222b2fb422bb3c19d9ed4c5bf1785d2f987dd0d5533ddf9242600a563e22107'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
def ref(p):return {'path':str(Path(p).resolve(strict=True)),'sha256':sha(p),'bytes':Path(p).stat().st_size}
def regular(p):
 for q in(Path(p),*Path(p).parents):need(not q.exists()or not(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024),'No enlaces/reparse en cierre')
def write(p,v):
 regular(p);Path(p).parent.mkdir(parents=True,exist_ok=True)
 with Path(p).open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def load(name,path,pin=None):
 if pin:need(sha(path)==pin,'Código auxiliar de cierre alterado')
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def actual(a):
 need(not OUTPUT.exists()and not(P/'PI09_ROOT_NATIVE_WRITER.lock').exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'No cerrar con escritor/mutex/futuro anterior incierto')
 registry=read(REG);budget=registry['budget'];need(budget['Native_ticks_all_branches']==220000 and budget['diagnostic_worlds_all_new']==16 and budget['owned_Native_job_memory_bytes']==512*1024*1024 and budget['Native_threads']==1,'Límites finales registrados exactos; no se amplían')
 writers=read(a.writers_proof);age=(datetime.now(timezone.utc)-datetime.fromisoformat(writers['recorded_utc'])).total_seconds();need(0<=age<=600 and(writers.get('no_live_affected_writers')is True or writers.get('all_scoped_Native_writers_closed')is True),'Proof Root fresco de escritores cerrados requerido')
 need(LIFE in writers.get('affected_life_ids',[])or any(e.get('life_id')==LIFE for e in writers.get('evidence',[])),'El principal D debe constar en el scope')
 ledger=load('PI09_final_same_identity_ledger',H/'ledger_PI09_misma_identidad_R01.py',LEDGER_SHA).ledger();need(ledger['ticks']<=budget['Native_ticks_all_branches']and ledger['world_count']<=budget['diagnostic_worlds_all_new'],'El ledger real supera límites; no declararlo dentro del presupuesto')
 process=load('PI09_final_scoped_process_checks',H/'comprobar_procesos_adopcion_D_PI09_R01.py',PROCESS_SHA);scoped=[]
 for life,item in ledger['worlds'].items():
  card=Path(item['card']);system=card.parents[3];regular(card);row=process.inspect('PI09_saved_world_final_scope',system,life);need(row.get('no_live_affected_writer')is True,'Writer/cola/lock no cerrado: '+life);scoped.append(row)
 activefile=S/'estado/ACTIVO.json';active=read(activefile);cardfile=S/'estado/vidas'/LIFE/'VIDA.json';card=read(cardfile);snap=S/card['snapshot'];need(active['life_id']==LIFE and card['life_id']==card['world_id']==LIFE and card['physical']['N']==67 and card['physical']['tick']==922371 and card['parent']['source_tick']==903603,'Principal/ascendencia final D exactos')
 need(active['snapshot_sha256']==card['snapshot_sha256']==sha(snap)and active['tick']==card['physical']['tick'],'ACTIVO/ficha/snapshot no coinciden')
 parser=load('PI09_final_snapshot_RO',RP/'observador_pasivo.py');view=parser.snapshot_view(snap);need(all(view['physical'][k]==card['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')),'Raw/clocks actuales no coinciden con ficha')
 stock={}
 for label,key,total in(('D','DEE.Cognitive.PI09.persistent_environment.D.R02',12),('R02_historical','DEE.Cognitive.PI09.selective_registered_consultation.R02',18),('FI8','DEE.Cognitive.PI09.explicit_FI_eight_offer_lot.R01',8),('FI_old_historical','DEE.Cognitive.PI07.regulated_FI_access.R01',8),('C2C','DEE.Cognitive.PI04.C2C.coordination.R01',32)):
  value=json.loads(view['metadata'][key]);n=value['ordinal'];need(type(n)is int and 0<=n<=total,'Contador finito inválido');stock[label]={'ordinal':n,'total':total,'remaining':total-n,'access':'historical_readonly'if label.endswith('historical')else'current_finite_offer_stock'}
 need(stock['D']=={'ordinal':7,'total':12,'remaining':5,'access':'current_finite_offer_stock'},'No se consumió D7postCOMMITTED; deben quedar cinco ofertas')
 need(stock['R02_historical']['ordinal']==12,'R02 histórico no puede reiniciarse ni consumirse como D')
 protected={str(p):sha(p)for p in(activefile,cardfile,snap)};db=S/'estado/servicios_persistentes'/LIFE/'cola.sqlite3';protected[str(db)]=sha(db)
 parent=read(S/'estado/vidas'/PARENT/'VIDA.json');oldA=read(S/'estado/vidas'/A/'VIDA.json');need(parent['physical']['tick']==903603 and oldA['physical']['tick']==861426 and oldA['snapshot_sha256']=='2eeef08e3bebac4e218178ed379fd99aa5fdeb03650c0454ad55c6534824c133','Antecesores quietos protegidos')
 for ident,record in((PARENT,parent),(A,oldA)):
  for p in(S/'estado/vidas'/ident/'VIDA.json',S/record['snapshot']):protected[str(p)]=sha(p)
 engine=[]
 for item in registry['protected_before'].values():
  file=Path(item['path'])
  if file.suffix.lower()in('.whl','.pyd')or file.name=='kernel_v27.cpp':need(sha(file)==item['sha256'],'Motor/kernel protegido cambió');engine.append(ref(file));protected[str(file)]=sha(file)
 selected=read(a.selected_zero);need(selected.get('life_id')==LIFE and selected.get('selected')is True and selected.get('new_ticks')==0 and selected.get('physical_unchanged')is True and selected.get('owner_closed')is True and selected.get('snapshot_sha256')==card['snapshot_sha256'],'Selected0 real cerrado y del corte actual requerido')
 if a.pre_cierre:
  status=load('PI09_final_selected_scope_only',H/'sincronizar_cierre_actual_PI09_R03.py');scope=status.selected_validation(LIFE,selected,ref(a.selected_zero),ref(a.source_function))
 else:
  sync=read(a.sync_proof);need(sync.get('schema')=='DEE.PI09.final_current_metadata.applied.R03'and sync.get('applied')is True and sync['actual_current']['life_id']==LIFE and sync['actual_current']['snapshot']['sha256']==card['snapshot_sha256'],'SincronizaciónR03 aplicada al corte actual requerida');scope=sync['actual_current']['operational_validation_scope']
 need(scope['selected_material_function_test_pending']is True and scope['selected_material_function_test_executed']is False and scope['selected_check_scope']=='ACTUAL_SELECTED_STATE0_SAVE_CLOSE_ONLY','No atribuir función material seleccionada que no se ejecutó')
 source0=read(a.source_zero);need(source0.get('closed')is True and source0.get('new_ticks')==0 and source0.get('new_Native_inputs')==0 and source0.get('physical_unchanged')is True,'Source0 real sin nuevos inputs/ticks requerida')
 sourcefun=read(a.source_function);need(sourcefun.get('closed')is True and sourcefun.get('error')is None and sourcefun.get('life_id')==LIFE and sourcefun.get('final_tick')==922371,'Última función Source cerrada del corte real requerida')
 last=[r for r in sourcefun.get('records',[])if r.get('literal',{}).get('modo')=='eci01-pi09-d-episodio'];need(last and last[-1]['rows'][0].get('actual_failed')is False,'Última función útil Source requerida')
 publication=read(a.publication);need(publication.get('schema')=='DEE.PI09.actual_complete_DOCX_publication.R01'and publication.get('internal_edition')=='1.38'and len(publication['rows'])==2,'Publicación1.38 real requerida')
 for row in publication['rows']:need(sha(Path(row['source']))==row['published_sha256']and Path(row['source']).stat().st_size==row['bytes'],'DOCX publicado cambió')
 rp_refs=[]
 for name in('RP_D6_FAMILIA_REGISTRADA_PI09_R01.json',):
  p=P/'control'/name;v=read(p);need(v.get('registered')is True,'Registro NativeRP real ausente');rp_refs.append(ref(p))
 omitted=[]
 for name in('MAPA_TRASLADO_PRODUCTO_PI09.json','MAPA_TRASLADO_D_PRODUCTO_PI09.json'):
  p=P/'control'/name;v=read(p);omitted.append({'reference':ref(p),'logical_file_bytes_at_move':v.get('logical_file_bytes'),'members_count':len(v.get('members',[])),'large_native_state_is_retained_locally_not_copied_into_small_delivery':True})
 resources=read(RP/'RECURSOS.json');recipes=[]
 for rid in('pi09_consulta_native12_familia_desde_C_R04','pi09_d6_familia_desde_DISCOVERY_T907543_R01'):
  f=RP/'recetas'/(rid+'.json');need(f.is_file(),'Receta pública faltante');recipes.append(ref(f))
 need(all(sha(Path(p))==v for p,v in protected.items()),'Estado/motor cambió durante lectura de cierre')
 return registry,{'schema':'DEE.PI09.final_budget_and_closed_state.R01','recorded_utc':datetime.now(timezone.utc).isoformat(),'closed':True,'all_scoped_Native_writers_closed':True,'Native_executed_by_closure':False,'new_Native_ticks':0,'new_worlds':0,'current_main':{'life_id':LIFE,'physical':card['physical'],'parent':card['parent'],'card':ref(cardfile),'snapshot':ref(snap),'ACTIVO':ref(activefile)},'finite_resources':stock,'actual_saved_Native_ledger':ledger,'registered_limits':budget,'Native_ticks_within_limit':True,'worlds_within_limit':True,'unused_Native_tick_allowance':budget['Native_ticks_all_branches']-ledger['ticks'],'unused_world_slots':budget['diagnostic_worlds_all_new']-ledger['world_count'],'worlds_are_not_experiences_or_capacities':True,'memory_limit_declared_and_previously_enforced_by_owned_supervisors_not_reaudited_here':budget['owned_Native_job_memory_bytes'],'storage_status':'NOT_REMEASURED_BY_THIS_LOCAL_CLOSURE_FINAL_PACKAGE_BUDGET_CHECK_IS_SEPARATE','fresh_Root_writer_proof':ref(a.writers_proof),'fresh_all_ledger_world_process_queue_checks':scoped,'selected_zero':ref(a.selected_zero),'source_zero':ref(a.source_zero),'last_actual_source_function':ref(a.source_function),'selected_material_function_test_pending':True,'selected_check_scope':'STATE0_ONLY_AFTER_COMMITTED_SOURCE_FUNCTION_AND_WHOLE_NATIVE_EQUIVALENCE_SEPARATE','publication':ref(a.publication),'final_sync':ref(a.sync_proof)if a.sync_proof else None,'final_sync_pending_after_actual_closed_facts':bool(a.pre_cierre),'Native_RP_verified':rp_refs,'public_family_recipes':recipes,'local_large_state_omission_maps':omitted,'RP_resources_current':ref(RP/'RECURSOS.json'),'protected_hashes_unchanged_during_check':protected,'protected_original_engine_files':engine,'campaign_registry_before':ref(REG),'registry_update_requested':bool(a.actualizar_registro),'historical_failures_and_inactive_rows_preserved':True,'zip_validation_and_visual_QA_not_inferred':True}
def close(a):
 old,result=actual(a);write(OUTPUT,result)
 if a.actualizar_registro:
  need(sha(REG)==result['campaign_registry_before']['sha256'],'Registro cambió antes del CAS');backup=P/'control/REGISTRO_ANTES_CIERRE_FINAL_PI09_R01.json';need(not backup.exists(),'Respaldo final anterior conservado');backup.write_bytes(REG.read_bytes());new=copy.deepcopy(old);new.setdefault('phase_before_final_closure',new.get('phase'));new.setdefault('selection_before_final_closure',copy.deepcopy(new.get('latest_actual_global_selection')));new.update(phase='CLOSED_ACTUAL_PI09',closed=True,all_scoped_Native_writers_closed=True,latest_actual_global_selection=read(S/'estado/ACTIVO.json'),final_closure=ref(OUTPUT),closed_utc=result['recorded_utc']);need(new['budget']==old['budget']and new['source_main']==old['source_main'],'No reescribir presupuesto ni origen histórico');tmp=REG.with_name(REG.name+'.FINAL_CLOSURE_WRITING');need(not tmp.exists(),'Escritura parcial de registro conservada');write(tmp,new);os.replace(tmp,REG);write(P/'control/REGISTRO_CIERRE_FINAL_APLICADO_PI09_R01.json',{'applied':True,'Native_ticks_added':0,'new_worlds':0,'before':ref(backup),'after':ref(REG),'closure':ref(OUTPUT),'budget_and_original_source_literal_preserved':True})
 if a.leer_primero:
  p=P/'LEER_PRIMERO_PI09_R01.txt';need(not p.exists(),'Ficha anterior conservada');text='PI09 — CIERRE LOCAL\n\nPrincipal: '+LIFE+' / N67 / T922371. Misma identidad trasladada completa; NATIVE T903603 y A T861426 conservados.\n\nD:5/6 útil frente3/6 sin retorno y1/6 desacoplado. Crédito genérico compartido; no se atribuye crédito específico a consulta1 ni una ley nueva. Conservación12/12 y última función Source útil anteriores al traslado. Selected0 real confirma carga/estado/guardado/cierre y equivalencia; prueba material postCOMMITTED pendiente por ventana, sin D7 ejecutada.\n\nStock D7/12:cinco ofertas disponibles. R02 y FI viejo son antecedentes de sólo lectura; FI8 y C2C conservan sus contadores actuales en el cierreJSON.\n\nReproducción: familias públicas C1 native12 y D real6 en sistema/gestionar.py reproducibilidad. IDs y destinos nuevos siempre. RP D6 reproduce6episodios,5útiles y2conflictos terminales;8peticiones incluyen preparación y estado. No8episodios.\n\nManual/Compendio1.38 publicados: ver '+str(a.publication)+'. QA visual sólo según comprobante; no inferirla de estructuraDOCX.\n\nComandos mantenidos: fuentes/COMANDOS_PUBLICOS_D_PI09_R01.txt. Ningún --nueva para el principal. No iniciar segundo propietario.\n\nArchivos grandes permanecen locales por mapas de traslado y recursosRP; esta ficha no sustituye parejas completas.\n\nComprobantes: '+str(OUTPUT)+'\n'+str(a.sync_proof)+'\n'+str(a.publication)+'\n';need(len(text)<6500,'Ficha compacta requerida');p.write_text(text,'utf8')
 print(json.dumps({'proof':str(OUTPUT),'sha256':sha(OUTPUT),'Native_ticks':result['actual_saved_Native_ledger']['ticks'],'worlds':result['actual_saved_Native_ledger']['world_count'],'remaining_D':5,'Native_executed':False,'registry_updated':bool(a.actualizar_registro),'README_created':bool(a.leer_primero)}))
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--cerrar',action='store_true');ap.add_argument('--pre-cierre',action='store_true');ap.add_argument('--writers-proof',type=Path);ap.add_argument('--selected-zero',type=Path);ap.add_argument('--source-zero',type=Path);ap.add_argument('--source-function',type=Path);ap.add_argument('--publication',type=Path);ap.add_argument('--sync-proof',type=Path);ap.add_argument('--actualizar-registro',action='store_true');ap.add_argument('--leer-primero',action='store_true');a=ap.parse_args()
 if not a.cerrar and not a.pre_cierre:print(json.dumps({'mode':'PLAN_ONLY_NO_STATE_READ','expected_main':LIFE,'tick':922371,'parent_tick':903603,'remaining_D':5,'Root_must_run_after':['selected0closed','publication1.38','syncR03applied'],'optional_explicit_Root_writes':['--actualizar-registro','--leer-primero'],'Native_executed':False}));return
 need(all(getattr(a,k)is not None for k in('writers_proof','selected_zero','source_zero','source_function','publication'))and(a.pre_cierre or a.sync_proof is not None),'Referencias explícitas requeridas; sync sólo después de pre-cierre')
 if a.pre_cierre:
  need(not a.actualizar_registro and not a.leer_primero,'Pre-cierre sólo genera hechos cerrados; REGISTRO/ficha después de sync')
  globals()['OUTPUT']=P/'control/CIERRE_PREVIO_A_SYNC_PI09_R01.json'
 close(a)
if __name__=='__main__':main()
