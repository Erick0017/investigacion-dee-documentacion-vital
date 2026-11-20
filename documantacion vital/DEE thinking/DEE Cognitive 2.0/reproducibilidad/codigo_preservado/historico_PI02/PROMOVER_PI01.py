"""Adopción PI01 por contratos existentes; dry-run por defecto.

--prepare importa el par completo y cuatro módulos, sin cambiar principal.
Después el responsable realiza la reapertura0ticks y registra su comprobante.
--adopt promueve el checkpoint vigente y sincroniza selectores documentales.
El agente autor de este script no ejecutó ninguna fase Native.
"""
from pathlib import Path,PurePosixPath
import argparse,ast,datetime,gzip,hashlib,json,os,shutil,sqlite3,struct,sys

sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent.parent
R=P.parent.parent.parent
C=R/'DEE Cognitive 2.0'
S=C/'sistema'
CS=P/'estados/candidato/sistema'
LIFE='ECI02_PI01_MAIN'
PARENT='ECI02_OPERATIVA_PRINCIPAL_01'
PARENT_T=727225
FINAL_T=735843
PARENT_SHA='46e275be49a1e8df9b823e3c533156d91fa66a79477872a125efabfa350470d4'
SYSTEM_KEY='DEE.Cognitive.System.1.1.life.v1'
SERVICE_KEY='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'
FOUR=['capacidades/progresion_integrada_01.py','capacidades/pi01_traza_legal_base.py','app/mundo_genesis_apd05.py','app/cola_local.py']
PROCESS_CHECKS=[]
BASELINE={
 'sistema/app/mundo_genesis_apd05.py':'1de175972447c21e940a6f85781088738ff7de827b83b9570c75bdb0d9ceb154',
 'sistema/app/cola_local.py':'4dcf136fb6a8f514e61ab143fc1f5ee55cfcbb168ed36ae91ba8cc22bbd50e1a',
 'PROYECTO.json':'b937fbf36ad1076bc3f0c605f8e727e47119ead6a3d73dc829691f79e6117242',
 'CONTINUIDAD_DEE_COGNITIVE_2_0.json':'780438dbaa0b01c7d3263f00f10dfbc0fd2d61a2e8eb00d6cd72ca4dfcbabfd5',
 'sistema/estado/ACTIVO.json':'8bdfd2f25f88b7094ae8d4ec1317bff3b37cdcbefab96991d0cbcdfee8c70ac1',
 'sistema/estado/genesis/SELECCION_PERSONAL.json':'567601d6367959c0a5ab19b1891005780ff585261a0acba1310a739e8e615fbf',
 'aplicacion/GENESIS/SELECCION_CANDIDATA.json':'e404a9e580b4db398b3c661923ed830ecbccde454790639dca152616956a1378',
 'sistema/capacidades/CATALOGO_CAPACIDADES.json':'a6a6b8e694ee8b8ca8da13ab8081c7ff0eadd2161d68b68da920770d7080dc45'}

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def atomic(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_name(p.name+'.pi01.tmp')
 with q.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
 os.replace(q,p)
def inside(p,root):
 p=Path(p).resolve(strict=True);root=Path(root).resolve(strict=True)
 if not p.is_relative_to(root):raise ValueError('Ruta fuera del árbol autorizado: '+str(p))
 for q in (p,*p.parents):
  if q==root.parent:break
  if q.is_symlink()or(getattr(q.stat(),'st_file_attributes',0)&1024):raise ValueError('Enlace/reparse point no admitido: '+str(q))
 return p
def copy_new(src,dst):
 src=Path(src);dst=Path(dst);dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():
  if sha(src)!=sha(dst):raise FileExistsError('Copia previa distinta protegida: '+str(dst))
  return
 with src.open('rb')as a,dst.open('xb')as b:shutil.copyfileobj(a,b)
 if sha(src)!=sha(dst):raise ValueError('Copia no íntegra: '+str(dst))

class Reader:
 def __init__(self,b):self.b=b;self.i=0
 def take(self,n):
  if n<0 or self.i+n>len(self.b):raise ValueError('Snapshot truncado')
  a=self.b[self.i:self.i+n];self.i+=n;return a
 def u8(self):return self.take(1)[0]
 def u32(self):return struct.unpack('<I',self.take(4))[0]
 def u64(self):return struct.unpack('<Q',self.take(8))[0]
 def text(self):
  n=self.u32()
  if n>16*1024**2:raise ValueError('Texto de snapshot fuera de límite')
  return self.take(n).decode('utf8')
 def count(self):
  n=self.u32()
  if n>1000000:raise ValueError('Colección fuera de límite')
  return n

def snapshot_view(path):
 encoded=Path(path).read_bytes();b=gzip.decompress(encoded)if encoded[:2]==b'\x1f\x8b'else encoded
 r=Reader(b[:-8])
 if r.take(8)!=b'DEETSNP1'or r.u32()!=2:raise ValueError('Snapshot no es v2 conocido')
 n=r.u32();tick=r.u64();r.u8();r.u64();r.u64();phase=r.text();total=r.u64()
 if total!=n**3 or total>128**3*4:raise ValueError('Dimensiones inválidas')
 raw=r.take(8*total);clocks=r.take(8*total);channels=r.count()
 for _ in range(channels):r.text();r.take(12+4+12+3)
 pending=r.count()
 for _ in range(pending):
  r.take(8+8+1+8+8)
  for _ in range(r.count()):r.text()
  for _ in range(r.count()):r.take(12+8)
 receipts=r.count()
 for _ in range(receipts):
  r.take(8+1+1+8)
  if r.u8():r.take(8)
  for _ in range(r.count()):r.text()
  r.text()
 r.u8();r.u64();prefix=r.i;metadata={}
 for _ in range(r.count()):
  k=r.text();v=r.text()
  if k in metadata:raise ValueError('Clave duplicada')
  metadata[k]=v
 if r.i!=len(b)-8:raise ValueError('Bytes no interpretados en snapshot')
 return {'physical':{'N':n,'tick':tick,'RAW_sha256':hashlib.sha256(raw).hexdigest(),'clocks_sha256':hashlib.sha256(clocks).hexdigest()},
         'encoded_sha256':hashlib.sha256(encoded).hexdigest(),'causal_prefix_sha256':hashlib.sha256(b[:prefix]).hexdigest(),
         'interfaces':channels,'pending_native':pending,'native_receipts':receipts,'phase':phase,'metadata':metadata,
         'scope':'Lectura binaria pasiva. GzipCRC y hashes comprobados; no se recalcula aquí FNV interno ni se restaura mundo.'}

def compare_native(a,b,allow_service=False):
 if a['physical']!=b['physical']or a['causal_prefix_sha256']!=b['causal_prefix_sha256']:raise ValueError('Cambió estado físico/agenda/interfaces/recibos durante migración0ticks')
 excluded={SYSTEM_KEY}
 if allow_service:excluded|={k for k in set(a['metadata'])|set(b['metadata'])if k==SERVICE_KEY or k.startswith(SERVICE_KEY+'.queue.')}
 changed=[k for k in set(a['metadata'])|set(b['metadata'])if k not in excluded and a['metadata'].get(k)!=b['metadata'].get(k)]
 if changed:raise ValueError('Cambió metadata no administrativa: '+repr(changed))
 return {'physical_equal':True,'causal_prefix_equal':True,'metadata_equal_except':sorted(excluded),'new_ticks':0}

def verify_pair(root):
 root=inside(root,P);index=root/'EXPORTACION_SERVICIO.json';m=read(index)
 if m.get('schema')!='DEE.persistent_service.paired_export.v1'or m.get('life_id')!=LIFE or m.get('queue_journal_required')is not True:raise ValueError('No es el par completo de MAIN')
 expected=set();resources=[]
 for item in m['members']:
  name=item['file'];rel=PurePosixPath(name)
  if not isinstance(name,str)or '\\'in name or ':'in name or rel.is_absolute()or '..'in rel.parts or name in expected:raise ValueError('Miembro inseguro/repetido')
  path=inside(root/rel,root)
  if not path.is_file()or path.stat().st_size!=item['bytes']or sha(path)!=item['sha256']:raise ValueError('Miembro alterado: '+name)
  expected.add(name)
  if name.startswith('artefactos_trabajador/PI01_RESOURCE_BANK_R04/'):resources.append(item)
 actual={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()and p!=index}
 if actual!=expected or not{'VIDA.deetsnap.gz','cola.sqlite3'}<=expected or not resources:raise ValueError('Par incompleto o recursos PI01 ausentes')
 view=snapshot_view(root/'VIDA.deetsnap.gz')
 if view['physical']['tick']!=FINAL_T or view['physical']['N']!=67 or view['encoded_sha256']!=m['snapshot_sha256']:raise ValueError('Corte distinto del autorizado')
 for k,v in view['physical'].items():
  if m['physical'][k]!=v:raise ValueError('Manifest físico no corresponde')
 con=sqlite3.connect((root/'cola.sqlite3').as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('SQLite exportado corrupto')
  counts=dict(con.execute('SELECT status,count(*) FROM requests GROUP BY status'))
  outstanding=[dict(zip(('id','status','payload'),r))for r in con.execute("SELECT id,status,payload FROM requests WHERE status IN('queued','processing','uncertain')")]
  for row in outstanding:
   if row['status']!='processing'or json.loads(row['payload'])!={'operacion':'exportar'}:raise ValueError('Pendiente ajeno al recibo de exportación: no descartar/repetir')
 finally:con.close()
 return m,view,{'manifest_sha256':sha(index),'members':len(expected),'resource_members':resources,'queue_counts':counts,'outstanding':outstanding,'no_native_import':True}

def no_writers():
 for system in (S,CS):
  lock=system/'estado/locks'
  if lock.exists()and list(lock.glob('*.lock')):raise ValueError('Hay locks de mundo; no se borran ni se fuerza escritura: '+str(lock))
 proof_path=P/'control/PROCESOS_CIERRE_PI01.json';proof=read(proof_path)
 stamp=next((proof[k]for k in('recorded_utc','checked_utc','inspected_utc','timestamp','recorded')if k in proof),None)
 if not isinstance(stamp,str):raise ValueError('Prueba de procesos sin fecha explícita')
 checked=datetime.datetime.fromisoformat(stamp.replace('Z','+00:00'))
 if checked.tzinfo is None:raise ValueError('Prueba de procesos sin zona horaria')
 age=(datetime.datetime.now(datetime.timezone.utc)-checked.astimezone(datetime.timezone.utc)).total_seconds()
 if not 0<=age<=600:raise ValueError('Prueba de procesos fuera de los últimos10min; refrescar sin iniciar otro mundo')
 result=proof.get('result',{})
 if type(result.get('exit_code'))is not int or result['exit_code']!=0 or 'output'not in result or result['output']not in('',None,[]):raise ValueError('La prueba de procesos no acredita salida vacía/exit0')
 caches=[]
 for system in (S,CS):
  for life in (PARENT,LIFE):
   db=system/'estado/servicios_persistentes'/life/'cola.sqlite3'
   if not db.is_file():continue
   wal=db.with_name(db.name+'-wal');shm=db.with_name(db.name+'-shm')
   # Immutable is valid only for a standalone closed database. A WAL must have
   # its already existing SHM for read-only coherent access, never copied away.
   has_wal=wal.exists()and wal.stat().st_size>0
   if has_wal and not shm.exists():raise ValueError('WAL sin SHM; no afirmar lectura coherente de owner: '+str(db))
   uri=db.as_uri()+'?mode=ro'+(''if has_wal else'&immutable=1')
   con=sqlite3.connect(uri,uri=True)
   try:
    row=con.execute("SELECT value FROM meta WHERE key='owner'").fetchone();owner=json.loads(row[0])if row else None
   finally:con.close()
   caches.append({'system':str(system),'life_id':life,'owner':owner,'SQLite_WAL_present':has_wal,
    'interpretation':'Published historical cache only; running:true without a current matching process is not evidence of a live writer. Fresh bounded process proof and world locks govern the check.'})
 check={'at':now(),'process_proof_sha256':sha(proof_path),'process_proof_age_seconds':age,'process_scope':proof.get('scope','Use only the exact filter and output recorded in proof; no whole-application census asserted'),
  'world_locks_found':0,'process_output_empty':True,'owner_caches':caches}
 PROCESS_CHECKS.append(check)
 return check

def protect_parent(check_selectors=True):
 card=read(S/'estado/vidas'/PARENT/'VIDA.json')
 if card['physical']['tick']!=PARENT_T or card['snapshot_sha256']!=PARENT_SHA or sha(S/card['snapshot'])!=PARENT_SHA:raise ValueError('El principal anterior avanzó/cambió; reconciliar desde el nuevo corte')
 if check_selectors:
  active=read(S/'estado/ACTIVO.json');project=read(C/'PROYECTO.json')
  if active['life_id']!=PARENT or active['snapshot_sha256']!=PARENT_SHA or project['selected_life']!=PARENT:raise ValueError('Selección concurrente/ajena; no sustituirla')
 return card

def validation(path):
 v=read(path)
 if v.get('approved_for_adoption')is not True or v.get('life_id')!=LIFE:raise ValueError('Falta decisión explícita del responsable para esta vida')
 # These figures are not an automatic cognition verdict; root must explain limits.
 for k in('scope','gains','losses','uncertainties','evidence','regression_coverage'):
  if k not in v:raise ValueError('Decisión incompleta: '+k)
 return v

def contract(record):
 return {'schema':'DEE.PI01.bounded_operational_contract.R04','version':'PI01.integrated_access_and_resources.R04','life_id':LIFE,
 'scope':'Native history-dependent0/1access selection, fixed codec to inherited MA/FI, actual resource consequence and generic return. Operator offers opportunities.',
 'profile':record['profile'],'physical_cut':record['physical'],'physical_parent':{'life_id':PARENT,'tick':PARENT_T,'snapshot_sha256':PARENT_SHA},
 'implementation':FOUR,'teacher_or_target_in_evaluation':False,'assistance':['Prepared two-route trace and legal interfaces','Fixed0->MA_alfa/1->FI codec','Fixed access readers and consequence-return timing','Operator initiates each opportunity'],
 'evidence':{'reserved_real':[16,18],'reserved_omit':[12,18],'nulled':[0,18],'retention_panel':[12,12],'retention_panel_tick':735466,'reopen_tick':FINAL_T,'sample_scope':'Shared-past branches, not independent organisms; bounded fixed curriculum, not general R2.'},
 'limits':['No autonomous timing of opportunities or self-generated multistep plan','No general autonomous recovery, language or competent general policy','18reserved cases, plus one documented continuation; no universal stability','State/environment cannot be reset or combined with alternative lives'],
 'manager_owner':'motor/python313/python.exe -I -B -X utf8 sistema/gestionar.py mente-unificada-iniciar --vida ECI02_PI01_MAIN --backend mente_unificada --eci01 --pausado --intervalo 60 --guardar-cada 3600 --max-segundos 7200',
 'literal_status':[{'modo':'eci01-pi01-estado'}],'literal_next_opportunity':[{'modo':'eci01-pi01-paso'}],
 'request':'Existing mente-unificada-pedir --vida ECI02_PI01_MAIN --situaciones <literal JSON list> --id <new unique ID> --esperar 240; resume before material FIFO and pause afterwards.',
 'complete_state':['Native snapshot including interfaces/agenda/receipts/protocols','estado/servicios_persistentes/ECI02_PI01_MAIN/cola.sqlite3 and resultados','estado/servicios_locales/ECI02_PI01_MAIN including PI01_RESOURCE_BANK_R04','VIDA.json, HISTORIA.jsonl and migration provenance'],
 'GUI':'Existing menu selects the life. propietario_genesis.py uses GenesisNativeWorld directly; CLI requires --eci01. PI01 literals use manager JSON; GUI text grammar has no PI01 shortcut.'}

def prepare(v,descriptor):
 no_writers();protect_parent()
 for rel,h in BASELINE.items():
  if sha(C/rel)!=h:raise ValueError('Cambió código/selector desde revisión estática: '+rel)
 if(S/'estado/vidas'/LIFE).exists():raise FileExistsError('La identidad ya existe; no reemplazar/reimportar')
 pair=Path(descriptor['pair']['directory']);m,source,verification=verify_pair(pair)
 if verification['manifest_sha256']!=descriptor['pair']['manifest_sha256']:raise ValueError('Descriptor final no corresponde al par')
 source_record=read(CS/'estado/vidas'/LIFE/'VIDA.json')
 if source_record['physical']['tick']!=FINAL_T:raise ValueError('La trayectoria fuente avanzó después del cierre autorizado')
 source_now=snapshot_view(CS/source_record['snapshot']);compare_native(source,source_now,allow_service=True)
 freeze=P/'codigo/revisiones/R04_CONGELADA';deployment=read(P/'control/DESPLIEGUE_R04.json')
 expected={r['file']:r['sha256']for r in deployment['files']}
 for rel in FOUR:
  if sha(freeze/rel)!=expected[rel]or sha(CS/rel)!=expected[rel]:raise ValueError('Código R04 distinto al congelado: '+rel)
  ast.parse((freeze/rel).read_text(encoding='utf8'))
 backup=P/'control/ADOPCION_PI01_RESPALDO'
 for rel in BASELINE:copy_new(C/rel,backup/rel)
 no_writers();protect_parent()
 # Only the four declared Cognitive modules, never engine/WHL/kernel.
 for rel in FOUR:
  target=S/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(freeze/rel,target)
  if sha(target)!=expected[rel]:raise ValueError('Copia código no íntegra')
 localpair=S/'estado/pares_iniciales'/LIFE
 if localpair.exists():raise FileExistsError('Par local previo protegido; revisar interrupción')
 shutil.copytree(pair,localpair)
 # Import uses the existing official Cognitive full-pair contract. Only root runs it.
 sys.path[:0]=[str(S),str(S/'app')]
 from app.lives import Store
 from app.importacion_emparejada import import_pair,verify_export
 verify_export(localpair)
 store=Store(S);result=import_pair(store,localpair,LIFE)
 rec=store.record(LIFE);imported=snapshot_view(S/rec['snapshot']);native_comparison=compare_native(source,imported)
 provenance=store.life_dir(LIFE)/'PROCEDENCIA_PI01'
 copy_new(CS/'estado/vidas'/LIFE/'VIDA.json',provenance/'VIDA_FUENTE.json')
 copy_new(CS/'estado/vidas'/LIFE/'HISTORIA.jsonl',provenance/'HISTORIA_FUENTE.jsonl')
 migration={'schema':'DEE.PI01.same_identity_store_migration.v1','life_id':LIFE,'source_system':str(CS),'target_system':str(S),'source_native_tick':FINAL_T,
 'physical_parent':{'life_id':PARENT,'tick':PARENT_T,'snapshot_sha256':PARENT_SHA},'source_parent':source_record.get('parent'),
 'source_record_snapshot_sha256':source_record['snapshot_sha256'],'export_snapshot_sha256':m['snapshot_sha256'],'imported_snapshot_sha256':rec['snapshot_sha256'],
 'same_identity_in_separate_store':True,'no_new_individual_or_acquisition':True,'native_comparison':native_comparison,
 'why_encoded_sha_changes':'Official import_state commits administrative SYSTEM_KEY metadata and serializes a new checkpoint. Physical fields and other native metadata are verified equal; original source record/history remain literal.',
 'paired_export_manifest_sha256':sha(localpair/'EXPORTACION_SERVICIO.json'),'source_record_preserved':'PROCEDENCIA_PI01/VIDA_FUENTE.json','source_history_preserved':'PROCEDENCIA_PI01/HISTORIA_FUENTE.jsonl','at':now()}
 # Add provenance only; keep the import parent's real snapshot, never edit memory.
 rec['PI01_migration']=migration;atomic(store.life_dir(LIFE)/'VIDA.json',rec);atomic(provenance/'MIGRACION.json',migration)
 checks=[]
 for item in m['members']:
  name=item['file']
  if name.startswith('artefactos_trabajador/'):
   target=S/'estado/servicios_locales'/LIFE/Path(name).relative_to('artefactos_trabajador')
  elif name.startswith('resultados/'):target=S/'estado/servicios_persistentes'/LIFE/name
  else:continue
  if sha(target)!=item['sha256']:raise ValueError('Artefacto no llegó íntegro: '+name)
  checks.append(name)
 atomic(S/'contratos/PROGRESION_INTEGRADA_01_R04.json',contract(rec))
 protect_parent();no_writers()
 receipt={'schema':'DEE.PI01.prepared_product.v1','at':now(),'life_id':LIFE,'phase':'PREPARED_NOT_PROMOTED','import_result':result,'migration':migration,
 'source_view':{k:x for k,x in source.items()if k!='metadata'},'verification':verification,'copied_worker_and_outbox_files':len(checks),
 'source_record_sha256':sha(provenance/'VIDA_FUENTE.json'),'module_hashes':expected,'previous_principal_unchanged':True,
 'writer_checks':PROCESS_CHECKS,'next':'Root must reopen this product life0ticks, verify resource/queue/protocol continuity, close owner, write REAPERTURA_PRODUCTO_PI01.json, then --adopt.'}
 atomic(P/'control/PREPARACION_PRODUCTO_PI01.json',receipt)
 return receipt

def adopt(v,proof):
 no_writers();protect_parent();prepared=read(P/'control/PREPARACION_PRODUCTO_PI01.json')
 if prepared['life_id']!=LIFE or proof.get('life_id')!=LIFE or proof.get('new_ticks')!=0 or proof.get('physical_unchanged')is not True or proof.get('pending_reconciled')is not True or proof.get('resources_valid')is not True:
  raise ValueError('Falta comprobante explícito de reapertura0ticks, conciliación y recursos')
 sys.path[:0]=[str(S),str(S/'app')]
 from app.lives import Store
 store=Store(S);rec=store.record(LIFE);view=snapshot_view(S/rec['snapshot'])
 source=snapshot_view(S/'estado/pares_iniciales'/LIFE/'VIDA.deetsnap.gz');native_comparison=compare_native(source,view,allow_service=True)
 if rec['physical']['tick']!=FINAL_T:raise ValueError('Avance posterior: no adoptar automáticamente otro corte')
 con=sqlite3.connect((S/'estado/servicios_persistentes'/LIFE/'cola.sqlite3').as_uri()+'?mode=ro',uri=True)
 try:
  if con.execute("SELECT count(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]:raise ValueError('Transporte aún pendiente: no purgar ni reenviar')
 finally:con.close()
 for rel,h in prepared['module_hashes'].items():
  if sha(S/rel)!=h:raise ValueError('Cambió código desde importación: '+rel)
 # The exact checkpoint after product close, never the earlier imported pointer.
 decision={k:v[k]for k in('scope','gains','losses','uncertainties','evidence','regression_coverage')}
 decision.update(decision_id='PI01_R04_ADOPCION_OPERATIVA_01',route='COMPATIBLE',life_id=LIFE,snapshot_sha256=rec['snapshot_sha256'],
  lineage=rec.get('PI01_migration'),reopening_proof=str(P/'control/REAPERTURA_PRODUCTO_PI01.json'),at=now())
 decision_path=P/'control/DECISION_PROMOCION_PI01.json';atomic(decision_path,decision)
 catalog=read(S/'capacidades/CATALOGO_CAPACIDADES.json')
 if any(r.get('id')=='PI01_ACCESO_CONSECUENCIAS_R04'for r in catalog['entries']):raise ValueError('Entrada PI01 previa inesperada; no duplicar')
 protect_parent();no_writers();result=store.promote(LIFE,decision_path)
 active=read(S/'estado/ACTIVO.json')
 if active['life_id']!=LIFE or active['snapshot_sha256']!=rec['snapshot_sha256']:raise ValueError('Promoción no apunta al checkpoint vigente')
 pair=S/'estado/pares_iniciales'/LIFE;oldconfig=read(C/'aplicacion/GENESIS/SELECCION_CANDIDATA.json')
 selected={**oldconfig,'source_alias':LIFE,'source_life':LIFE,'source_tick':FINAL_T,'source_snapshot_sha256':sha(pair/'VIDA.deetsnap.gz'),
 'paired_export_manifest_sha256':sha(pair/'EXPORTACION_SERVICIO.json'),'source_paired_export_manifest':(pair/'EXPORTACION_SERVICIO.json').relative_to(C).as_posix(),
 'selection_scope':'Same physical PI01 life migrated by full-pair contract; default opens the existing current life, never imports this seed over it.',
 'current_operational_snapshot_sha256':rec['snapshot_sha256'],'explicit_operational_adoption':decision['decision_id']}
 project=read(C/'PROYECTO.json');previous={'selected_life':project['selected_life'],'latest_saved_tick':project['latest_saved_tick'],'parent':project.get('parent'),'operational_adoption':project.get('operational_adoption')}
 available=list(dict.fromkeys([LIFE,*project.get('current_available_lives',[])]))
 project.update(selected_life=LIFE,latest_saved_tick=FINAL_T,parent=rec.get('parent'),current_available_lives=available,
  prior_selection_PI01=previous,operational_adoption={'decision_id':decision['decision_id'],'scope':v['scope'],'physical_cut':rec['physical'],'full_pair_local':pair.relative_to(C).as_posix(),'previous_principal_preserved':True})
 personal=read(S/'estado/genesis/SELECCION_PERSONAL.json');personal.update(life_id=LIFE,world_id=rec['world_id'],first_selected_utc=now(),explicit_operational_adoption=decision['decision_id'])
 continuity=read(C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json');prior={k:continuity.get(k)for k in('life_id','world_id','physical_cut','parent','latest_snapshot','identity_card','operational_directories','selected_seed','proof')}
 continuity.update(updated_utc=now(),life_id=LIFE,world_id=rec['world_id'],profile=rec['profile'],physical_cut=rec['physical'],parent=rec.get('parent'),
  latest_snapshot={'path_relative_to_product':'sistema/'+rec['snapshot'],'sha256':rec['snapshot_sha256']},
  identity_card={'path_relative_to_product':'sistema/estado/vidas/'+LIFE+'/VIDA.json','sha256':sha(store.life_dir(LIFE)/'VIDA.json')},
  personal_selection=personal,current_available_lives=available,selected_seed=selected,prior_cut_PI01=prior,PI01_migration=rec.get('PI01_migration'),
  operational_directories=['sistema/estado/'+r+'/'+LIFE for r in('vidas','servicios_persistentes','servicios_locales','pares_iniciales')],
  proof={'promotion_decision':str(decision_path),'product_reopening':str(P/'control/REAPERTURA_PRODUCTO_PI01.json'),'evidence_is_provenance_not_actor_input':True},new_ticks_for_this_selection=0)
 catalog['entries'].insert(0,{'id':'PI01_ACCESO_CONSECUENCIAS_R04','version':'PI01.R04','implementation':FOUR,
 'availability':'OPERATIVO_DOMINIO_ACOTADO','integration':'One actual shared-world genealogy; operator-initiated opportunities, native route choice, fixed method codec, actual file resource and outcome return.',
 'validated_lives':[{'life_id':LIFE,'physical':rec['physical'],'snapshot_sha256':rec['snapshot_sha256']}],
 'contract':'contratos/PROGRESION_INTEGRADA_01_R04.json','assistance':contract(rec)['assistance'],'limits':contract(rec)['limits'],'reserved_results':{'real':[16,18],'omit':[12,18],'nulled':[0,18]},'retention_panel_cut':735466,'retention_panel':[12,12]})
 atomic(C/'PROYECTO.json',project);atomic(C/'aplicacion/GENESIS/SELECCION_CANDIDATA.json',selected)
 atomic(S/'estado/genesis/SELECCION_PERSONAL.json',personal);atomic(C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json',continuity)
 atomic(S/'capacidades/CATALOGO_CAPACIDADES.json',catalog);atomic(S/'contratos/PROGRESION_INTEGRADA_01_R04.json',contract(rec))
 protect_parent(check_selectors=False)
 receipt={'schema':'DEE.PI01.adopted_product.v1','at':now(),'life_id':LIFE,'phase':'COMMITTED','promotion':result,'record':rec,
 'native_comparison':native_comparison,'selected_by_project':read(C/'PROYECTO.json')['selected_life'],'selected_by_personal':read(S/'estado/genesis/SELECCION_PERSONAL.json')['life_id'],
 'active':active,'writer_checks':PROCESS_CHECKS,'new_ticks_for_migration_and_promotion':0,'protected_parent':{'life_id':PARENT,'tick':PARENT_T,'snapshot_sha256':PARENT_SHA},
 'reversal':'Use the existing Store.promote/select contract with protected parent and preserved previous selectors; no world rewind or deletion.'}
 atomic(P/'control/ADOPCION_PRODUCTO_PI01.json',receipt)
 return receipt

def main():
 parser=argparse.ArgumentParser(description=__doc__);phase=parser.add_mutually_exclusive_group()
 phase.add_argument('--dry-run',action='store_true');phase.add_argument('--prepare',action='store_true');phase.add_argument('--adopt',action='store_true')
 parser.add_argument('--validation',type=Path,default=P/'control/VALIDACION_ADOPCION_R04.json')
 parser.add_argument('--pair-descriptor',type=Path,default=P/'control/PAR_FINAL_PI01.json')
 parser.add_argument('--reopening-proof',type=Path,default=P/'control/REAPERTURA_PRODUCTO_PI01.json')
 args=parser.parse_args()
 if not(args.prepare or args.adopt):
  print(json.dumps({'mode':'DRY_RUN_NO_NATIVE_IMPORT_NO_WRITES','product':str(C),'source_system':str(CS),'life_id':LIFE,
   'phases':['--prepare requires explicit validation; copies four modules and imports complete pair, no promotion','root reopens product0ticks and closes owner','--adopt uses exact new checkpoint and existing Store.promote'],
   'validation_available':args.validation.is_file(),'pair_descriptor_available':args.pair_descriptor.is_file(),'reopening_proof_available':args.reopening_proof.is_file(),
   'required_validation_fields':['approved_for_adoption:true','life_id:ECI02_PI01_MAIN','scope','gains','losses','uncertainties','evidence','regression_coverage'],
   'required_reopening_fields':['life_id:ECI02_PI01_MAIN','new_ticks:0','physical_unchanged:true','pending_reconciled:true','resources_valid:true'],
   'baseline_comparison':{rel:{'expected':h,'actual':sha(C/rel),'same':sha(C/rel)==h}for rel,h in BASELINE.items()}},ensure_ascii=False,indent=2));return
 v=validation(args.validation)
 result=prepare(v,read(args.pair_descriptor))if args.prepare else adopt(v,read(args.reopening_proof))
 print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
