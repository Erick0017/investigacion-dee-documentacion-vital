"""Root-only closed C884835 preservation, using the established paired schema.

Default is a read-only plan. --exportar performs one exact new stdlib copy.
No DEE import, owner, Native step, metadata rewrite, cleanup or rollback.
"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import argparse,ctypes,ctypes.wintypes,hashlib,importlib.util,json,os,shutil,sqlite3

P9=Path(__file__).resolve().parents[1]
P8=P9.with_name('PROGRESION_INTEGRADA_08')
C=P9.parents[2]/'DEE Cognitive 2.0'
S=P8/'estados/C_R03/sistema'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_C_01'
TICK=884835
SNAP='ef52add3d7a6a5b9e310efb815bf8ae7dd47cb968104e7b1fa5c8a2b9f726d22'
CLOSED=P8/'control/PI08_C_EVALUAR_R04.json'
CLOSED_SHA='a6d19f5e2190e1877fab54b16b8c8857e27d92d56da6ca95de92ab1d43f4b6a8'
LEGACY=P8/'codigo/exportar_B_REAL_PI08_R01.py'
LEGACY_SHA='44150798946e69b832580dc7f794a3693688e5a15ad7938009722bbf571bd062'
PARSER=C/'reproducibilidad/observador_pasivo.py'
PARSER_SHA='dbb2a5e15d70c64112d36505197f4aebf6ff7d4092972923e17cd60c10a1c873'
SERVICE_KEY='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'
C_KEY='DEE.Cognitive.PI08.conditional_sensor_register_access.C.R02'
B_KEY='DEE.Cognitive.PI08.successive_contextual_regulation.B.R01'
DEST=P9/'pares/C_HEREDADA_T884835'

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def require(ok,msg):
 if not ok:raise ValueError(msg)
def load(path,name,pin):
 require(sha(path)==pin,'Cambió dependencia conservada: '+str(path))
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def regular(p):
 for x in(p,*p.parents):
  require(not x.exists()or not(x.is_symlink()or getattr(x.lstat(),'st_file_attributes',0)&1024),'No se admiten enlaces: '+str(x))
def protected_A():
 active=C/'sistema/estado/ACTIVO.json';a=read(active);life=a.get('life_id',a.get('preferred_life'))
 require(life=='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01','La principal vigente cambió; Root debe revisar la ascendencia antes de exportar')
 card=C/'sistema/estado/vidas'/life/'VIDA.json';r=read(card)
 return {str(p):sha(p)for p in(active,card,C/'sistema'/r['snapshot'])}

def scoped_pid(pid,closed_utc):
 require(os.name=='nt'and type(pid)is int and pid>0,'Se requiere PID real de Windows')
 k=ctypes.WinDLL('kernel32',use_last_error=True)
 k.OpenProcess.argtypes=[ctypes.c_uint32,ctypes.c_int,ctypes.c_uint32];k.OpenProcess.restype=ctypes.c_void_p
 k.CloseHandle.argtypes=[ctypes.c_void_p]
 handle=k.OpenProcess(0x1000,False,pid)
 if not handle:
  error=ctypes.get_last_error();require(error==87,'No se demostró la ausencia del PID guardado')
  return {'pid':pid,'absent':True,'winerror':error}
 try:
  code=ctypes.c_uint32();require(k.GetExitCodeProcess(ctypes.c_void_p(handle),ctypes.byref(code)),'No se pudo leer el estado del PID')
  if code.value!=259:return {'pid':pid,'exited':True,'exit_code':code.value}
  size=ctypes.c_uint32(32768);buf=ctypes.create_unicode_buffer(size.value)
  require(k.QueryFullProcessImageNameW(ctypes.c_void_p(handle),0,buf,ctypes.byref(size)),'PID activo sin identidad de imagen: detener y conservar')
  creation=ctypes.wintypes.FILETIME();exit_=ctypes.wintypes.FILETIME();kernel=ctypes.wintypes.FILETIME();user=ctypes.wintypes.FILETIME()
  require(k.GetProcessTimes(ctypes.c_void_p(handle),ctypes.byref(creation),ctypes.byref(exit_),ctypes.byref(kernel),ctypes.byref(user)),'PID activo sin fecha de creación')
  ticks=(creation.dwHighDateTime<<32)|creation.dwLowDateTime
  born=datetime(1601,1,1,tzinfo=timezone.utc)+timedelta(microseconds=ticks//10)
  old=datetime.fromisoformat(closed_utc).astimezone(timezone.utc)
  official=(C/'motor/python313/python.exe').resolve()
  require(Path(buf.value).resolve()!=official and born>old+timedelta(seconds=60),'PID activo/reutilización no demostrada: no se exporta')
  return {'pid':pid,'active_PID_reused_other_image':True,'image':buf.value,'creation_utc':born.isoformat(),
          'coherent_old_owner_closed_cache_utc':closed_utc,'proof':'Different image and creation more than60s after the pinned closed old owner status. No process action.'}
 finally:k.CloseHandle(ctypes.c_void_p(handle))

def inspect():
 require(sha(CLOSED)==CLOSED_SHA,'Cambió el cierre C original')
 closed=read(CLOSED)
 require(closed['closed']is True and closed['error']is None and closed['final_tick']==TICK and closed['opportunities_completed']==6,'Se requiere el cierre C6 exacto')
 old=load(LEGACY,'PI09_old_closed_export_helpers',LEGACY_SHA);parser=load(PARSER,'PI09_passive_snapshot',PARSER_SHA)
 life=S/'estado/vidas'/LIFE;service=S/'estado/servicios_persistentes'/LIFE;worker=S/'estado/servicios_locales'/LIFE
 for root in(S,life,service,worker):regular(root);require(root.is_dir(),'Falta una raíz completa C: '+str(root))
 require(not(S/'estado/ACTIVO.json').exists(),'C debe seguir sin seleccionar')
 require(not(life/'FUTURO_INTERRUMPIDO.json').exists()and not(service/'IMPORTACION_EN_CURSO.json').exists(),'Hay un futuro C incompleto')
 cardfile=life/'VIDA.json';history=life/'HISTORIA.jsonl';card=read(cardfile);snapshot=(S/card['snapshot']).resolve(strict=True)
 require(card['life_id']==LIFE and card['world_id']==LIFE and card['profile']=='fisica_directa'and card['physical']['tick']==TICK and sha(snapshot)==card['snapshot_sha256']==SNAP,'Cambió la continuación C: no se restaura ni sustituye')
 for identity in{LIFE,card['world_id']}:require(not(S/'estado/locks'/(identity+'.lock')).exists(),'Persiste lock del mundo C')
 require(json.loads(history.read_text('utf8').splitlines()[-1])['snapshot_sha256']==SNAP,'Historia y ficha C no concuerdan')
 view=parser.snapshot_view(snapshot)
 require(all(view['physical'][k]==card['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256'))and view['physical']['N']==67,'Física C incoherente')
 native=json.loads(view['metadata'][SERVICE_KEY]);cm=json.loads(view['metadata'][C_KEY]);bm=json.loads(view['metadata'][B_KEY])
 require(cm['ordinal']==6 and cm['ready']and not cm.get('pending')and not cm.get('uncertain')and bm['ordinal']==30 and bm['control']['arm']=='real'and not bm.get('pending')and not bm.get('uncertain'),'Progreso heredado C/B no está cerrado/coherente')
 require(native['native_tick_at_checkpoint']==TICK and native['paused']and not native['uncertain_external_result'],'Protocolo Native C no está pausado/coherente')
 db=service/'cola.sqlite3';aux={x:Path(str(db)+x).stat().st_size if Path(str(db)+x).exists()else 0 for x in('-wal','-shm','-journal')}
 require(not aux['-wal']and not aux['-journal'],'No se copia una SQLite con WAL/journal no vacío')
 con=sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True);con.row_factory=sqlite3.Row
 try:
  require(con.execute('PRAGMA integrity_check').fetchone()[0]=='ok','SQLite C no íntegra')
  owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0]);counts=dict(con.execute('SELECT status,COUNT(*) FROM requests GROUP BY status'))
  require(owner.get('running')is False and owner['tick']==TICK and not owner.get('uncertain_external_result')and not any(counts.get(k,0)for k in('queued','processing','uncertain')),'Owner/transporte C pendiente o ambiguo')
  failure=old.verify_declared_precommit_failure(con,service)
  process=scoped_pid(owner['pid'],owner['wall_utc'])
  receipt=native['last_completed_receipt'];row=con.execute('SELECT * FROM requests WHERE id=?',(receipt['id'],)).fetchone()
  require(row is not None and row['status']=='completed'and row['payload_sha']==receipt['payload_sha256'],'Último recibo C no conciliado')
  outbox=service/'resultados'/(receipt['id']+'.json');require(outbox.is_file()and sha(outbox)==receipt['result_sha256'],'Outbox final C no conciliado')
 finally:con.close()
 return old,card,view,owner,counts,failure,process,aux,receipt,(life,service,worker,cardfile,history,snapshot,db)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--exportar',action='store_true');a=ap.parse_args()
 if not a.exportar:
  print(json.dumps({'mode':'PLAN_ONLY_NO_NATIVE','source_system':str(S),'life_id':LIFE,'tick':TICK,'snapshot_sha256':SNAP,'destination':str(DEST),
       'command':[str(C/'motor/python313/python.exe'),'-I','-B','-X','utf8',str(Path(__file__).resolve()),'--exportar'],
       'schema':'DEE.persistent_service.paired_export.v1','preserves_empty_directories':True,'no_source_writes':True},ensure_ascii=False,indent=2));return
 require(not DEST.exists()and not DEST.with_name(DEST.name+'_PRESERVACION.json').exists(),'Destino ya usado; no se sobrescribe')
 before_A=protected_A();old,card,view,owner,counts,failure,process,aux,receipt,paths=inspect()
 life,service,worker,cardfile,history,snapshot,db=paths
 sources=[(snapshot,Path('VIDA.deetsnap.gz')),(db,Path('cola.sqlite3')),(cardfile,Path('procedencia/VIDA_ORIGINAL.json')),(history,Path('procedencia/HISTORIA_ORIGINAL.jsonl'))];directories=[]
 for root,prefix in((service/'resultados',Path('resultados')),(worker,Path('artefactos_trabajador'))):
  members,dirs=old.tree(root);sources.extend((p,prefix/r)for p,r in members);directories.extend((prefix/Path(d)).as_posix()for d in dirs)
 before={str(p):{'bytes':p.stat().st_size,'sha256':sha(p)}for p,_ in sources}
 DEST.mkdir(parents=True)
 for name in directories:(DEST/name).mkdir(parents=True,exist_ok=True)
 rows=[]
 for p,relative in sources:
  target=DEST/relative;target.parent.mkdir(parents=True,exist_ok=True)
  with p.open('rb')as src,target.open('xb')as dst:shutil.copyfileobj(src,dst)
  require(sha(target)==before[str(p)]['sha256']and target.stat().st_size==before[str(p)]['bytes'],'Copia no íntegra: conservar destino parcial')
  rows.append({'file':relative.as_posix(),**before[str(p)]})
 after={str(p):{'bytes':p.stat().st_size,'sha256':sha(p)}for p,_ in sources}
 require(before==after and protected_A()==before_A,'Cambió una fuente o A durante la preservación')
 manifest={'schema':'DEE.persistent_service.paired_export.v1','life_id':LIFE,'profile':card['profile'],'backend':'mente_unificada',
   'native_snapshot':'VIDA.deetsnap.gz','snapshot_sha256':SNAP,'physical':card['physical'],'members':rows,'queue_journal_required':True,
   'source_record':{'life_id':LIFE,'world_id':card['world_id'],'parent':card.get('parent')},'no_engine_or_WHL':True,
   'not_a_new_cognitive_acquisition':True,'empty_directories_preserved':sorted(set(directories)),
   'expected_preserved_terminal_failure':failure,'pending_Native_agenda_preserved':view['pending_native'],
   'scope':'Exact closed C descendant of B_REAL; no fusion, Native input, metadata rewrite or source-file change.'}
 mf=DEST/'EXPORTACION_SERVICIO.json';mf.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
 proof={'schema':'DEE.PI09.inherited_C.complete_closed_preservation.R01','source_system':str(S),'life_id':LIFE,'tick':TICK,
   'snapshot_sha256':SNAP,'destination':str(DEST),'manifest_sha256':sha(mf),'members':len(rows),'bytes':sum(x['bytes']for x in rows),
   'directories':len(manifest['empty_directories_preserved']),'causal_prefix_sha256':view['causal_prefix_sha256'],'process_proof':process,
   'queue_status_counts':counts,'SQLite_auxiliaries':aux,'last_Native_receipt':receipt,'expected_preserved_terminal_failure':failure,
   'closed_C_evidence':{'path':str(CLOSED),'sha256':CLOSED_SHA},'protected_A_before':before_A,'protected_A_after':protected_A(),
   'source_files_unchanged':True,'Native_executed':False,'new_native_ticks':0,'recorded_utc':datetime.now(timezone.utc).isoformat()}
 output=DEST.with_name(DEST.name+'_PRESERVACION.json');output.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf8')
 print(json.dumps({'exported':True,'manifest':str(mf),'manifest_sha256':sha(mf),'proof':str(output),'Native_executed':False},ensure_ascii=False))
if __name__=='__main__':main()
