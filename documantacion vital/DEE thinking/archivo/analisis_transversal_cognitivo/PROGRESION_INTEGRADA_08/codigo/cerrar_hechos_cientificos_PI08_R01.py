"""Passive final PI08 scientific facts. P8 JSON only; no DEE/Native imports."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import ctypes,hashlib,importlib.util,json,sqlite3
P=Path(__file__).resolve().parents[1];H=P/'codigo';R=P.parents[2];C=R/'DEE Cognitive 2.0';S=C/'sistema';RP=C/'reproducibilidad'
A='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01';OLD='ECI02_PI03_REPRO_PI04_PI05_MAIN_01'
OUT=P/'control/CIERRE_CIENTIFICO_PI08_R01.json';PROTECTION=P/'control/PROTECCION_ESTADOS_MOTOR_CIERRE_PI08_R01.json'
def require(ok,text):
 if not ok:raise ValueError(text)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
 digest=hashlib.sha256()
 with Path(p).open('rb')as f:
  for part in iter(lambda:f.read(1024*1024),b''):digest.update(part)
 return digest.hexdigest()
def ref(p):return{'path':str(Path(p).resolve()),'sha256':sha(p)}
def put(p,value):
 with p.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
require(not OUT.exists()and not PROTECTION.exists(),'Existing final closure protected; no overwrite')
require(not(P/'PI08_ROOT_NATIVE_WRITER.lock').exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'A scoped material writer remains')
facts=read(H/'CIERRE_CIENTIFICO_PI08_R01_PLANTILLA.json');reg=read(P/'REGISTRO_CAMPANA.json')
cp=P/'control/PI08_C_PREPARAR_R04.json';ce=P/'control/PI08_C_EVALUAR_R04.json';nf=P/'control/PI08_B_NONE_AUTOPSIA_PANEL_R02.json'
prep,evaluation,none=read(cp),read(ce),read(nf)
require(prep['closed']and evaluation['closed']and prep['error']is None and evaluation['error']is None,'Actual coherent C phases required')
require(prep['new_Native_ticks']==3 and evaluation['new_Native_ticks']==9381 and evaluation['opportunities_completed']==6 and evaluation['joint_useful']==5,'C measured6/5 and9384ticks required')
require(prep['Native_inputs']['unique_requested']==1 and evaluation['Native_inputs']['unique_requested']==1141 and prep['Native_inputs']['status_counts']=={'applied':1}and evaluation['Native_inputs']['status_counts']=={'applied':1141},'C exact1142Applied')
require(evaluation['questions_applied']==evaluation['questions_scheduled']==evaluation['extra_bits_released']==4,'Four actual questions/released bits')
valid=0
for row in evaluation['records']:
 valid+=int(row['first_stage']['Native_selection_valid']and row['first_stage']['reader']['choice']is not None)
 valid+=int(row['second_stage']['reader']['choice']is not None)
require(valid==12,'C exact12 non-NULL Native selections required')
require(none['closed']and none['owner_closed']and none['error']is None and none['panel_correct']==10 and none['panel_witnesses']==12 and none['new_Native_ticks']==2859 and none['Native_inputs']=={'unique_requested':947,'status_counts':{'applied':947}},'Actual None10/12/947Applied/2859ticks required')
numeric={r['label']:r for r in none['rows']if r['label']in('number13','number8')}
require(numeric['number13']['observed']==7 and numeric['number8']['observed']==2 and numeric['number8']['literal']['izquierda']==7,'None actual7 transported into7−5→2')
comparison=[r for r in none['phase_and_dose_comparison']if r['label']in{r['label']for r in none['rows']if'expected_evaluator_only'in r}]
require(len(comparison)==12 and all(r['before_tick_equal']and r['after_tick_equal']and r['current_Native_inputs']==r['reference_Native_inputs']for r in comparison),'None and Real twelve witnesses must match actual times/doses')
parser=load('PI08_final_passive_snapshot_parser',RP/'observador_pasivo.py')
ledger=load('PI08_existing_engine_pin_constants',H/'medir_ledger_y_almacenamiento_PI08_R01.py')
kernel=ctypes.WinDLL('kernel32',use_last_error=True)
kernel.OpenProcess.argtypes=[ctypes.c_uint32,ctypes.c_int,ctypes.c_uint32];kernel.OpenProcess.restype=ctypes.c_void_p
kernel.CloseHandle.argtypes=[ctypes.c_void_p];kernel.GetExitCodeProcess.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint32)]
kernel.QueryFullProcessImageNameW.argtypes=[ctypes.c_void_p,ctypes.c_uint32,ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_uint32)]
kernel.GetProcessTimes.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p]
def process(pid,owner):
 if pid is None:return{'pid':None,'cached_import_not_started':True,'no_live_old_owner':True}
 handle=kernel.OpenProcess(0x1000,False,int(pid))
 if not handle:
  error=ctypes.get_last_error();require(error==87,'Cannot prove scoped cached PID absent')
  return{'pid':pid,'present':False,'Windows_error':error,'no_live_old_owner':True}
 try:
  code=ctypes.c_uint32();require(kernel.GetExitCodeProcess(handle,ctypes.byref(code)),'GetExitCodeProcess failed')
  if code.value!=259:return{'pid':pid,'present':True,'exit_code':code.value,'no_live_old_owner':True}
  creation=ctypes.c_uint64();exit_time=ctypes.c_uint64();kt=ctypes.c_uint64();ut=ctypes.c_uint64();require(kernel.GetProcessTimes(handle,ctypes.byref(creation),ctypes.byref(exit_time),ctypes.byref(kt),ctypes.byref(ut)),'GetProcessTimes failed')
  created=datetime(1601,1,1,tzinfo=timezone.utc)+timedelta(microseconds=creation.value//10)
  wall=datetime.fromisoformat(owner['wall_utc'].replace('Z','+00:00')).astimezone(timezone.utc)
  buf=ctypes.create_unicode_buffer(4096);length=ctypes.c_uint32(len(buf));require(kernel.QueryFullProcessImageNameW(handle,0,buf,ctypes.byref(length)),'Query image failed')
  require(owner.get('running')is False and created>wall,'A cached original owner may still be live; do not infer closure')
  return{'pid':pid,'present':True,'current_image':buf.value,'creation_utc':created.isoformat(),'cached_closed_owner_wall':wall.isoformat(),'chronologically_reused_PID':True,'no_live_old_owner':True}
 finally:kernel.CloseHandle(handle)
status=[]
scopes=[(S,A),(S,OLD),(P/'estados/C_R03/sistema',evaluation['life_id']),
 (P/'estados/B_NONE_R01/sistema',none['life_id']),
 (P/'estados/RP_A_PANEL12_R01/sistema','ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_ARP_PANEL12_01')]
f1=read(P/'control/PI08_F1_CUT_R03.json')
for home in(P/'estados').iterdir():
 card=home/'sistema/estado/vidas'/f1['life_id']/'VIDA.json'
 if card.exists():scopes.append((home/'sistema',f1['life_id']))
for system,life in scopes:
 cardfile=system/'estado/vidas'/life/'VIDA.json';card=read(cardfile);service=system/'estado/servicios_persistentes'/card['world_id'];db=service/'cola.sqlite3';wal=Path(str(db)+'-wal')
 require(not(system/'estado/locks'/(card['world_id']+'.lock')).exists()and not(wal.exists()and wal.stat().st_size),'Live lock/nonemptyWAL in affected closed scope')
 con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  require(con.execute('pragma integrity_check').fetchone()[0]=='ok','Closed queue integrity')
  ownerrow=con.execute("select value from meta where key='owner'").fetchone();owner=json.loads(ownerrow[0])if ownerrow else{}
  unresolved=con.execute("select id,status from requests where status in('queued','processing','uncertain')").fetchall()
  require(owner.get('running')is False,'Affected owner still reports running')
  if life!=f1['life_id']:require(not unresolved,'Unresolved non-F1 material queue')
  pid=process(owner.get('pid'),owner)
 finally:con.close()
 status.append({'life_id':life,'system':str(system),'cached_owner':owner,'process':pid,'unresolved':unresolved,'pending_F1_diagnostic_preserved':life==f1['life_id'],'future_marker_preserved':(cardfile.parent/'FUTURO_INTERRUMPIDO.json').exists()})
maincardfile=S/'estado/vidas'/A/'VIDA.json';maincard=read(maincardfile);mainview=parser.snapshot_view(S/maincard['snapshot']);active=read(S/'estado/ACTIVO.json')
require(active['life_id']==A and active['tick']==861426 and maincard['snapshot_sha256']=='2eeef08e3bebac4e218178ed379fd99aa5fdeb03650c0454ad55c6534824c133'and mainview['encoded_sha256']==maincard['snapshot_sha256'],'Actual protected MainA changed')
require(mainview['physical']=={k:maincard['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')},'A raw/clock/card mismatch')
mainbaseline=evaluation['protected_before'];require(mainbaseline==evaluation['protected_after']and all(sha(Path(path))==value for path,value in mainbaseline.items()),'A critical hashes changed from actual C protection')
old=reg['source_main'];require(sha(Path(old['card']['path']))==old['card']['sha256']and sha(Path(old['snapshot']['path']))==old['snapshot']['sha256'],'Old PI05 literal card/snapshot changed')
oldview=parser.snapshot_view(Path(old['snapshot']['path']));require(oldview['physical']=={k:old['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')},'Old PI05 RAW/clocks changed')
engines=[]
for name,(path,pin)in ledger.ENGINE_PINS.items():
 actual=sha(path);require(actual==pin,'Frozen engine/kernel changed: '+name);engines.append({'name':name,'path':str(path),'sha256':actual,'matches_fixed_pin':True})
require(not(S/'capacidades/pi08_revision_flexible_B_R01.py').exists()and not(S/'contratos/PI08_B_USO_OPERATIVO_R01.json').exists(),'B must not be deployed to Main')
protection={'schema':'DEE.PI08.final_passive_protection.R01','recorded_utc':datetime.now(timezone.utc).isoformat(),'Native_executed':False,'DEE_imported':False,'global_Root_mutex_absent':True,'RP_material_mutex_absent':True,
 'all_scoped_Native_writers_closed':True,'status_scopes':status,'current_A':{'card':ref(maincardfile),'snapshot':ref(S/maincard['snapshot']),'physical':mainview['physical'],'encoded_snapshot_sha256':mainview['encoded_sha256']},
 'old_PI05_unchanged':{'card':old['card'],'snapshot':old['snapshot'],'physical':oldview['physical'],'literal_hashes_match_start':True},'engine_and_kernel_pins':engines,'B_not_deployed':True,
 'F1_failed_future_not_repaired':True,'scope':'Closed-source passive verification only; no requests, Native imports, source writes, marker deletion or process termination.'}
put(PROTECTION,protection)
facts['sources']['C_prepare']=ref(cp);facts['sources']['C_final']=ref(ce);facts['sources']['NONE_final']=ref(nf)
facts['sources']['F1_failed_summary']=ref(P/'control/PI08_F1_CUT_R03.json');facts['sources']['passive_protection']=ref(PROTECTION)
facts['sources']['A_panel_registration']=ref(RP/'verificaciones'/RID/('ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_ARP_PANEL12_01.json')) if False else facts['sources']['A_panel_registration']
for key,entry in facts['sources'].items():
 path=Path(entry['path']).resolve(strict=True);require(sha(path)==entry['sha256'],'Final source reference missing/stale: '+key)
facts['outcomes']['C']={'closed':True,'status':'CLOSED_FINITE_PHASE_NO_ADOPTION','summary':'Prepared two-stage conditional information flow:5/6 useful,12/12 valid Native selections,4 applied material questions and4 actual released bits used at the second TC. Technical external register/fixed order are P0; no first-query temporal-credit learning, causal value-of-information or planning claim.',
 'source_tick':875451,'final_tick':884835,'new_Native_ticks_including_prepare':9384,'prepare_ticks':3,'evaluation_ticks':9381,'Native_requested':1142,'Native_applied':1142,'useful':5,'opportunities':6,'valid_Native_selections':12,'questions_applied':4,'real_extra_bits_released':4,'adopted':False,'external_register_P0':True}
facts['outcomes']['NONE']={'closed':True,'status':'CLOSED_EXISTING_FUTURE_DIAGNOSTIC_10_OF12','summary':'Prospective existing None18 future:10/12,947Applied,2859ticks. SUM6+7→7 and actualDIF7−5→2 match the Real panel at identical12-step absolute times/doses. This weakens a B-contingent-damage interpretation; A availability was positive at its different complete cut/phase. No specific age/phase microcause is isolated.',
 'initial_tick':875451,'final_tick':878310,'new_Native_ticks':2859,'Native_requested':947,'Native_applied':947,'correct':10,'witnesses':12,'actual_sum':7,'actual_next_left':7,'actual_difference':2,'same_absolute_panel_phase_and_dose_as_Real':True,'B_original_None18_score13_preserved':True,'new_worlds':0}
facts['outcomes']['F1'].update(status='FAILED_IDENTITY_AUDIT_DIAGNOSTIC_PRESERVED_NO_LIVE_WRITER',closed=True,pending_diagnostic_preserved=True,
 actual_imported_worlds=1,actual_identity_forks=1,actual_raw_cut_forks=0,
 summary='The Native diagnostic stopped at the identity-fork equality audit; the intended raw cut was not executed. Its future/error and underreported original fork counter are preserved. Root prospective reassignment documents the one actual identity fork and the uncreated cut slot. No live F1 writer remains; no causal cut success is claimed.')
facts['main_actual'].update(physical=maincard['physical'],source_current_card=ref(maincardfile),source_current_snapshot=ref(S/maincard['snapshot']))
facts.update(closed=True,all_scoped_Native_writers_closed=True,closed_utc=datetime.now(timezone.utc).isoformat(),Native_executed_by_closure=0,DEE_imports_by_closure=0,
 scope='Final scientific facts with actual A protected; B/C remain separate unadopted histories, F1 failure preserved. Editorial publication remains a separate future proof.')
facts['documentation_target'].update(publication_confirmed=False,publication_proof=None,actual_source_edition_at_closure=read(C/'PROYECTO.json')['manual_internal_edition'])
put(OUT,facts)
print(json.dumps({'facts':str(OUT),'sha256':sha(OUT),'closed':True,'all_scoped_writers_closed':True,'documentation_publication_confirmed':False,'passive_protection':str(PROTECTION),'passive_protection_sha256':sha(PROTECTION),'Native_executed':0}))
