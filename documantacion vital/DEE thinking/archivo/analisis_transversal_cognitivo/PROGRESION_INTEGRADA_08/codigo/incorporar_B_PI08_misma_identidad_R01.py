"""Conditional Root-only same-identity relocation/adoption; default read-only.

Never imports a new life or advances Native time. All actual administrative
Store loads/saves/promotions require official Python and explicit final gates.
No phase runs on import. Partial moves remain fenced for diagnosis, never
silently retried, purged or replaced with an earlier future.
"""
from pathlib import Path,PurePosixPath
import argparse,ast,datetime,hashlib,importlib.util,json,os,shutil,sqlite3,sys,copy
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';CS=P/'estados/B_REAL_R01/sistema';H=P/'codigo';CONTROL=P/'control'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_REAL_01';PARENT='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01';PARENT_T=861426;PARENT_SHA='2eeef08e3bebac4e218178ed379fd99aa5fdeb03650c0454ad55c6534824c133'
SELECTORS=('PROYECTO.json','CONTINUIDAD_DEE_COGNITIVE_2_0.json','sistema/estado/ACTIVO.json','sistema/estado/genesis/SELECCION_PERSONAL.json','aplicacion/GENESIS/SELECCION_CANDIDATA.json','sistema/capacidades/CATALOGO_CAPACIDADES.json')
PREPARED=CONTROL/'PREPARACION_TRASLADO_PRODUCTO_PI08_B.json';ADOPTED=CONTROL/'ADOPCION_PRODUCTO_PI08_B.json';INTENT=CONTROL/'TRASLADO_PRODUCTO_PI08_B_EN_CURSO.json';BACKUP=CONTROL/'RESPALDO_INCORPORACION_PI08_B'
GATES=('functional_gain','conservation','causal_controls','source_reopening','new_function_at_final_cut','decisive_recipe_replay')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def info(p):p=Path(p);return{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def regular(p):
 for q in(Path(p),*Path(p).parents):
  if q.exists()and(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked/reparse target: '+str(q))
def bounded(p,root,existing=True):
 regular(p);p=Path(p).resolve(strict=existing)
 if not p.is_relative_to(Path(root).resolve()):raise ValueError('Target outside explicit workspace: '+str(p))
 return p
def relative(v):
 p=PurePosixPath(v)
 if not isinstance(v,str)or '\\'in v or ':'in v or p.is_absolute()or any(x in('.','..')for x in p.parts):raise ValueError('Safe portable relative path required')
 return p
def write(p,v,replace=False):
 p=Path(p);regular(p);p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists()and not replace:raise FileExistsError('Preserved existing proof: '+str(p))
 tmp=p.with_name(p.name+'.PI08_WRITING')
 with tmp.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def parser():
 file=C/'reproducibilidad/observador_pasivo.py';spec=importlib.util.spec_from_file_location('PI08_relocation_passive',file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def parent(selected=True):
 card=read(S/'estado/vidas'/PARENT/'VIDA.json')
 if card['physical']['N']!=67 or card['physical']['tick']!=PARENT_T or card['snapshot_sha256']!=PARENT_SHA or sha(S/card['snapshot'])!=PARENT_SHA:raise ValueError('Protected principal advanced; do not replace a later continuation')
 if selected and read(S/'estado/ACTIVO.json')['life_id']!=PARENT:raise ValueError('A different current principal is selected')
 return card
def official():
 if Path(sys.executable).resolve()!= (C/'motor/python313/python.exe').resolve()or sys.version_info[:2]!=(3,13):raise ValueError('Root official existing Python3.13 required for administrative Store phase')
def proof_writers(file,systems):
 file=bounded(file,P);proof=read(file);stamp=datetime.datetime.fromisoformat(proof['recorded_utc'].replace('Z','+00:00'));age=(datetime.datetime.now(datetime.timezone.utc)-stamp.astimezone(datetime.timezone.utc)).total_seconds()
 if not 0<=age<=600 or proof.get('no_live_affected_writers')is not True or not proof.get('scope')or not proof.get('evidence')or not{LIFE,PARENT}<=set(proof.get('affected_life_ids',[])):raise ValueError('Fresh scoped PID/closed-owner proof required; cached runningFalse alone is insufficient')
 for system,life in systems:
  cardfile=system/'estado/vidas'/life/'VIDA.json'
  if not cardfile.exists():continue
  card=read(cardfile);db=system/'estado/servicios_persistentes'/card['world_id']/'cola.sqlite3'
  for marker in(system/'estado/locks'/(card['world_id']+'.lock'),cardfile.parent/'FUTURO_INTERRUMPIDO.json',db.parent/'IMPORTACION_EN_CURSO.json'):
   if marker.exists():raise ValueError('Live/uncertain marker: '+str(marker))
  if db.with_name(db.name+'-wal').exists()and db.with_name(db.name+'-wal').stat().st_size:raise ValueError('Nonempty WAL: preserve and diagnose')
  con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
  try:
   if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Queue integrity failure')
   row=con.execute("SELECT value FROM meta WHERE key='owner'").fetchone();owner=None if row is None else json.loads(row[0]);pending=con.execute("SELECT id,status FROM requests WHERE status IN('queued','processing','uncertain')").fetchall()
   if pending or(owner and owner.get('running')is not False):raise ValueError('Unresolved queue/owner preserved; never purge or resubmit')
  finally:con.close()
 return info(file)
def decision(file):
 d=read(file);required={'approved_for_adoption','life_id','source_snapshot_sha256','source_tick','gates','approved_code_files','selectors_cas','catalog_entry','new_contract','scope','gains','losses','uncertainties','assistance','evidence','regression_coverage','process_proof'}
 if not required<=set(d)or d['approved_for_adoption']is not True or d['life_id']!=LIFE:raise ValueError('Actual reasoned final approval required; no prospective promotion')
 for name in GATES:
  gate=d['gates'].get(name,{})
  if gate.get('satisfied')is not True or not gate.get('criterion')or not gate.get('result')or not gate.get('evidence'):raise ValueError('Missing actual empirical gate: '+name)
 refs=d['evidence']+[e for gate in d['gates'].values()for e in gate.get('evidence',[])]
 for item in refs:
  source=bounded(item['path'],P)
  if sha(source)!=item['sha256']:raise ValueError('Actual evidence hash differs')
 if set(d['selectors_cas'])!=set(SELECTORS):raise ValueError('All six existing product references need CAS')
 contract=d['new_contract']
 if contract.get('schema')!='DEE.PI08.B.exact_operational_profile.v1'or contract.get('life_id')!=LIFE or contract.get('all_outer_FI_requests')is not True or contract.get('internal_C2C_FI_redirected')is not False or contract.get('public_FI_domain')!=[0,20]or contract.get('all_adoption_gates_met')is not True or contract.get('C2C_protocol_sha256')!='0cf6bf8508e071a1c8cf1448023a096bc43336d66b8a1deb98f488b29b4205fd':raise ValueError('Exact approved B use/publicFI/C2C32 profile required')
 validate_B_evidence(d)
 for witness in('PI08_A1_PRECONTROL_REAL_R01.json','PI08_A1_POSTCONTROL_REAL_R02.json'):
  proof=read(CONTROL/witness)
  if proof.get('life_id')!=PARENT or proof.get('closed')is not True or proof.get('criteria_met')is not True or proof.get('new_Native_ticks')!=0 or not all(proof.get('full_Native_field_equalities',{}).values()):raise ValueError('Actual full-route A1 prepare/commit/idempotence/reopen witnesses required: '+witness)
 return d
def validate_B_evidence(d):
 required={'B_actual_closed_arms','B_conservation_proof','B_source_full_pair'}
 if not required<=set(d):raise ValueError('Actual B four-arm/panel/source references required')
 seal_file=H/'SELLO_PI08_B_R01.json';seal=read(seal_file)
 if sha(seal_file)!='98a54759d0d4bae2e53a6f432962b08e92f2b3836ee98b98b3b44dad7ae8779e':raise ValueError('Frozen B seal changed')
 arms=d['B_actual_closed_arms']
 if set(arms)!={'real','none','yoked','reference'}:raise ValueError('All four prospectively sealed B arms required')
 for role,ref in arms.items():
  file=bounded(ref['path'],P);actual=read(file)
  if sha(file)!=ref['sha256']or actual.get('role')!=role or actual.get('life_id')!=seal['research_life_ids'][role]or actual.get('status')!='CLOSED_18_OPPORTUNITIES'or actual.get('closed')is not True or actual.get('error')is not None or actual.get('opportunities_completed')!=18 or actual.get('initial_tick')!=861426 or actual.get('protocol_sha256')!=seal['protocol_sha256']or actual.get('seal_sha256')!=sha(seal_file):raise ValueError('Missing/incomplete actual B arm: '+role)
  if role=='real'and actual.get('final_tick')!=d['source_tick']:raise ValueError('Actual real source cut differs')
 ref=d['B_conservation_proof'];file=bounded(ref['path'],P);panel=read(file)
 if sha(file)!=ref['sha256']or panel.get('life_id')!=seal['conservation_life_id']or any(panel.get(key)is not True for key in('closed','owner_closed','criteria_met','C2C_last_offer_product','adopted_A_unchanged','B_episode_never_called'))or panel.get('error')is not None or panel.get('panel_correct')!=12 or panel.get('panel_witnesses')!=12:raise ValueError('Actual closed12+lastC2C conservation clone required')
 pair_ref=d['B_source_full_pair'];pair=bounded(pair_ref['path'],P);manifest=pair/'EXPORTACION_SERVICIO.json';m=read(manifest)
 if sha(manifest)!=pair_ref['manifest_sha256']or m['life_id']!=LIFE or m['physical']['tick']!=d['source_tick']or m['physical']['N']!=67 or panel['source_manifest_sha256']!=sha(manifest):raise ValueError('Panel must derive from the actual complete real B source')
 if sha(pair/m['native_snapshot'])!=m['snapshot_sha256']:raise ValueError('Complete learned B snapshot corrupted')
 template=read(H/'PERMISO_B_OPERATIVO_R02_PROPUESTO/contratos/PI08_B_USO_OPERATIVO_R01.DRAFT.json')
 if d['new_contract'].get('frozen_files_sha256')!=template['frozen_files_sha256']or d['new_contract'].get('B_allowed_modes')!=template['B_allowed_modes']or d['new_contract'].get('C2C_allowed_modes')!=template['C2C_allowed_modes']:raise ValueError('Exact frozen-only operational B permission required')
 return True

def selector_cas(d,allow_selected=False):
 for rel,h in d['selectors_cas'].items():
  if allow_selected and rel=='sistema/estado/ACTIVO.json'and read(C/rel).get('life_id')==LIFE:continue
  if sha(C/rel)!=h:raise ValueError('Concurrent selector/catalog change: '+rel)
def code(d):
 rows=[];seen=set()
 for name,digest in d['new_contract']['frozen_files_sha256'].items():
  if Path(name).name!=name or sha(CS/'capacidades'/name)!=digest:raise ValueError('Actual frozen B scientific source changed before deployment: '+name)
 for item in d['approved_code_files']:
  rel=relative(item['file']);target=bounded(S/rel,S,False);source=Path(item['source']).resolve(strict=True);regular(source)
  if rel.as_posix()in seen:raise ValueError('Duplicate approved source target')
  seen.add(rel.as_posix())
  if not(source.is_relative_to(CS.resolve())or source.is_relative_to(H.resolve()))or source.suffix not in('.py','.json'):raise ValueError('Only explicit bounded Cognitive source/protocol bytes')
  prepared_profile=rel.as_posix()=='contratos/PI08_B_USO_OPERATIVO_R01.json'
  if prepared_profile:
   profile=read(source)
   if profile.get('schema')!='DEE.PI08.B.exact_operational_profile.v1'or profile.get('status')!='PREPARED_DIAGNOSTIC'or profile.get('life_id')!=LIFE or profile.get('adoption_decision_sha256')is not None:raise ValueError('Only exact unselected PREPARED profile may be staged before promotion')
   expected_profile=dict(d['new_contract'])
   if profile!=expected_profile:raise ValueError('Prepared profile must equal the final decision template before COMMITTED fields are added')
  elif rel.parts[0]not in('app','capacidades')or(target.suffix=='.json'and not target.name.startswith('PROTOCOLO')and rel.as_posix()!='capacidades/SELLO_PI08_B_R01.json'):raise ValueError('No engine/state/selector payloads in source delta')
  if sha(source)!=item['sha256']or(target.exists()and sha(target)!=item.get('before_sha256'))or(not target.exists()and item.get('before_sha256')is not None):raise ValueError('Approved code CAS differs')
  if source.suffix=='.py':ast.parse(source.read_bytes())
  else:read(source)
  rows.append({**item,'source':str(source),'target':str(target),'bytes':source.stat().st_size,'deployment_role':'PREPARED_DIAGNOSTIC_PROFILE_NOT_COMMITTED'if prepared_profile else'CODE_OR_IMMUTABLE_PROTOCOL'})
 required=('app/pi08_identidad_c2c_B_R01.py','app/usar_dee.py','capacidades/pi07_regulacion_R01.py','capacidades/PROTOCOLO_PI07_R01.json','capacidades/pi07_regulacion_R02.py','capacidades/PROTOCOLO_PI07_R02.json','capacidades/pi07_regulacion_R03.py','capacidades/PROTOCOLO_PI07_R03.json','capacidades/pi07_acceso_FI_regulado_R01.py','capacidades/PROTOCOLO_PI07_ACCESO_FI_R01.json','capacidades/pi08_integracion_c2c_R01.py','capacidades/PROTOCOLO_PI08_C2C_32_R01.json','capacidades/PROTOCOLO_PI08_C2C_INTEGRACION_R01.json','capacidades/pi08_permisos_operativos_R01.py')
 for name in required:
  if name not in seen and not(S/name).is_file():raise ValueError('Missing required operational/identity dependency before movement: '+name)
 if 'app/usar_dee.py'not in seen or 'app/pi08_identidad_c2c_B_R01.py'not in seen:raise ValueError('Explicit reviewed launcher and same-ID administrative adapter required')
 for name in('app/mundo_genesis_apd05.py','app/cola_local.py','capacidades/pi04_dispatcher.py','capacidades/pi08_permiso_B_operativo_R03.py','capacidades/pi08_revision_flexible_B_R01.py','capacidades/pi08_revision_flexible_B_episodio_R01.py','capacidades/PROTOCOLO_PI08_B_R01.json','capacidades/SELLO_PI08_B_R01.json'):
  if name not in seen:raise ValueError('Explicit reviewed B permission/literal dependency must be in approved delta: '+name)
 if 'contratos/PI08_B_USO_OPERATIVO_R01.json'not in seen:raise ValueError('Explicit prepared permission profile required before unselected product reopening')
 return rows
def inventory(d):
 state=CS/'estado';cardfile=state/'vidas'/LIFE/'VIDA.json';card=read(cardfile)
 if card['life_id']!=LIFE or card['world_id']!=LIFE or card['physical']['N']!=67 or card['physical']['tick']!=d['source_tick']or card['snapshot_sha256']!=d['source_snapshot_sha256']:raise ValueError('Exact frozen same-identity source cut required')
 roots=[state/name/LIFE for name in('vidas','servicios_persistentes','servicios_locales')];items=[]
 for root in roots:
  bounded(root,state)
  for file in sorted([root,*root.rglob('*')]):
   regular(file);rel=file.relative_to(state).as_posix();target=S/'estado'/rel
   items.append({'source':str(file),'target':str(target),'relative':rel,'kind':'directory'if file.is_dir()else'file',**({}if file.is_dir()else{'bytes':file.stat().st_size,'sha256':sha(file)})})
 snapshots=sorted({*(state/'checkpoints').glob(LIFE+'.T*.deetsnap.gz'),*(state/'checkpoints').glob('import.'+LIFE+'.*.deetsnap.gz')})
 if not snapshots or (CS/card['snapshot']).resolve()not in {p.resolve()for p in snapshots}:raise ValueError('Current/all same-life checkpoints missing')
 for file in snapshots:
  bounded(file,state/'checkpoints');rel=file.relative_to(state).as_posix();items.append({'source':str(file),'target':str(S/'estado'/rel),'relative':rel,'kind':'file','bytes':file.stat().st_size,'sha256':sha(file)})
 hashes={r['sha256']for r in items if r['kind']=='file'and r['relative'].startswith('checkpoints/')}
 for line in(state/'vidas'/LIFE/'HISTORIA.jsonl').read_text('utf8').splitlines():
  row=json.loads(line)
  if row['snapshot_sha256']not in hashes or(row.get('previous_snapshot_sha256')and row['previous_snapshot_sha256']not in hashes):raise ValueError('A history checkpoint is outside the complete named set; preserve and diagnose, do not guess')
 return card,roots,snapshots,items
def native_equal(a,b):
 if a['physical']!=b['physical']or a['causal_prefix_sha256']!=b['causal_prefix_sha256']:raise ValueError('Native physical/interface/agenda/receipt prefix changed')
 keys=set(a['metadata'])|set(b['metadata']);changed=[]
 for key in keys:
  if a['metadata'].get(key)==b['metadata'].get(key):continue
  changed.append(key)
  if key=='DEE.Cognitive.System.1.1.life.v1'or key=='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'or key.startswith('DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1.queue.'):continue
  if key=='DEE.Cognitive.PI04.C2C.coordination.R01':
   old=json.loads(a['metadata'][key]);new=json.loads(b['metadata'][key])
   if new.get('life_id')==LIFE and old.get('life_id')in(PARENT,LIFE)and {k:v for k,v in old.items()if k!='life_id'}=={k:v for k,v in new.items()if k!='life_id'}:continue
  raise ValueError('Nonadministrative metadata changed: '+key)
 return{'complete_Native_prefix_equal':True,'physical_equal':True,'changed_metadata_keys_all_listed':sorted(changed),'only_C2C_current_identity_leaf_allowed':True,'new_ticks':0}
def prepare(d,file,process):
 official()
 if PREPARED.exists()or INTENT.exists():raise FileExistsError('Existing relocation phase preserved; no blind repeated movement')
 parent();selector_cas(d);writers=proof_writers(process,[(S,PARENT),(CS,LIFE)]);rows=code(d);card,roots,snapshots,items=inventory(d)
 for root in roots:
  if(S/'estado'/root.relative_to(CS/'estado')).exists():raise FileExistsError('Target life/service/worker exists')
 for checkpoint in snapshots:
  if(S/'estado/checkpoints'/checkpoint.name).exists():raise FileExistsError('Target checkpoint name exists')
 if CS.drive.lower()!=S.drive.lower():raise ValueError('Same-volume bounded moves only; no implicit recursive copy/delete')
 BACKUP.mkdir(exist_ok=False)
 for rel in SELECTORS:
  dest=BACKUP/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(C/rel,dest)
 for row in rows:
  target=Path(row['target'])
  if target.exists():
   backup=BACKUP/'codigo'/row['file'];backup.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(target,backup)
 manifest=CONTROL/'MAPA_TRASLADO_PRODUCTO_PI08_B.json';write(manifest,{'source_system':str(CS),'target_system':str(S),'same_life_id':LIFE,'same_world_id':LIFE,'historical_parent_literal_preserved':card['parent'],'members':items,'logical_file_bytes':sum(r.get('bytes',0)for r in items),'not_a_new_life_or_import':True})
 source_snapshot=CS/card['snapshot'];before=parser().snapshot_view(source_snapshot)
 write(INTENT,{'phase':'INTENT_NOT_PROMOTED','decision':info(file),'source_snapshot':info(source_snapshot),'map':info(manifest),'writers':writers,'Native_ticks':0})
 for row in rows:
  target=Path(row['target']);target.parent.mkdir(parents=True,exist_ok=True);temp=target.with_name(target.name+'.PI08_DEPLOY');shutil.copyfile(row['source'],temp)
  if sha(temp)!=row['sha256']:raise ValueError('Code copy hash failure')
  os.replace(temp,target)
 for root in roots:
  target=bounded(S/'estado'/root.relative_to(CS/'estado'),S/'estado',False);target.parent.mkdir(parents=True,exist_ok=True);os.rename(bounded(root,CS/'estado'),target)
 for checkpoint in snapshots:os.rename(bounded(checkpoint,CS/'estado/checkpoints'),bounded(S/'estado/checkpoints'/checkpoint.name,S/'estado/checkpoints',False))
 for row in items:
  target=Path(row['target']);regular(target)
  if row['kind']=='directory':
   if not target.is_dir():raise ValueError('Moved empty directory missing')
  elif not target.is_file()or target.stat().st_size!=row['bytes']or sha(target)!=row['sha256']:raise ValueError('Moved file hash/size differs; stop without promotion')
 # The original same-identity Native bytes already moved. Only the required
 # administrative C2C current-life leaf may now change through existing Store.
 sys.path[:0]=[str(S),str(S/'app')]
 from app.lives import Store
 from app.pi08_identidad_c2c_B_R01 import rebind_moved_C2C_identity
 mapping=rebind_moved_C2C_identity(Store(S),LIFE,manifest,sha(manifest))
 current=read(S/'estado/vidas'/LIFE/'VIDA.json');after=parser().snapshot_view(S/current['snapshot']);comparison=native_equal(before,after);parent();selector_cas(d)
 receipt={'schema':'DEE.PI08.B.same_identity.prepared_product.R01','phase':'PREPARED_MOVED_NOT_PROMOTED','at':now(),'decision':info(file),'life_id':LIFE,'source_native_before':before['physical'],'preserved_moved_source_snapshot':'sistema/'+card['snapshot'],'original_source_snapshot_sha256':card['snapshot_sha256'],'map':info(manifest),'deployed_code':rows,'prepared_permission_profile':info(S/'contratos/PI08_B_USO_OPERATIVO_R01.json'),'public_FI_material_before_promotion':False,'administrative_mapping':mapping,'comparison':comparison,'world_id_preserved':True,'history_parent_unchanged':current['parent']==card['parent'],'new_ticks':0,'next':'Root actual unselected product Owner load/state/save/close0, then --adopt with its real reopening witness. No repeated science.'};write(PREPARED,receipt);return receipt
def native_commit(decision_id,digest):
 journal=S/'estado/PROMOCIONES.jsonl'
 if not journal.exists():return None
 for line in reversed(journal.read_text('utf8').splitlines()):
  row=json.loads(line)
  if row.get('phase')=='COMMITTED'and row.get('decision_id')==decision_id and row.get('life_id')==LIFE and row.get('snapshot_sha256')==digest:return row
 return None
def adopt(d,file,reopening,process):
 official()
 if ADOPTED.exists():return read(ADOPTED)
 prepared=read(PREPARED)
 if prepared['decision']['sha256']!=sha(file):raise ValueError('Decision changed after relocation')
 proof=read(reopening);card=read(S/'estado/vidas'/LIFE/'VIDA.json')
 if proof.get('life_id')!=LIFE or proof.get('new_ticks')!=0 or proof.get('snapshot_sha256')!=card['snapshot_sha256']or any(proof.get(k)is not True for k in('physical_unchanged','pending_reconciled','operational_state_valid','owner_closed')):raise ValueError('Actual coherent product reopening0 witness required')
 writers=proof_writers(process,[(S,PARENT),(S,LIFE)]);parent(False);selector_cas(d,True)
 before=parser().snapshot_view(C/prepared['preserved_moved_source_snapshot']);after=parser().snapshot_view(S/card['snapshot']);comparison=native_equal(before,after)
 for row in prepared['deployed_code']:
  if sha(S/row['file'])!=row['sha256']:raise ValueError('Deployed source changed after preparation')
 reasoned={k:d[k]for k in('scope','gains','losses','uncertainties','evidence','regression_coverage')};identifier=d.get('decision_id','PI08_ADOPCION_B_OPERATIVA_01');promotion=CONTROL/'DECISION_PROMOCION_PRODUCTO_PI08_B.json'
 reasoned.update(decision_id=identifier,route='COMPATIBLE',life_id=LIFE,snapshot_sha256=card['snapshot_sha256'],source_decision=info(file),reopening_proof=info(reopening),same_identity_relocation=prepared['map'],real_historical_parent=card['parent'])
 witness=native_commit(identifier,card['snapshot_sha256'])
 if witness is None:
  parent();write(promotion,reasoned);sys.path[:0]=[str(S),str(S/'app')];from app.lives import Store
  result=Store(S).promote(LIFE,promotion);witness=native_commit(identifier,card['snapshot_sha256'])
  if witness is None:raise ValueError('No matching Native COMMITTED witness; no metadata success asserted')
 else:result={'existing_COMMITTED_not_repeated':witness}
 # Publish exact permission immediately, before any selected Owner starts.
 contract=dict(d['new_contract']);contract.update(status='COMMITTED',life_id=LIFE,adoption_decision_sha256=sha(promotion),actual_native_commit_witness=witness)
 path=S/'contratos/PI08_B_USO_OPERATIVO_R01.json'
 if path.exists()and read(path)!=contract:
  prior=read(path)
  if prior.get('schema')!='DEE.PI08.B.exact_operational_profile.v1'or prior.get('life_id')!=LIFE or prior.get('status')!='PREPARED_DIAGNOSTIC':raise FileExistsError('Another permission contract preserved')
  write(CONTROL/'PERFIL_PREPARADO_ANTES_COMMITTED_PI08_B.json',prior)
  write(path,contract,True)
 elif not path.exists():write(path,contract)
 project=read(C/'PROYECTO.json');continuity=read(C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json');personal=read(S/'estado/genesis/SELECCION_PERSONAL.json');config=read(C/'aplicacion/GENESIS/SELECCION_CANDIDATA.json');catalog=read(S/'capacidades/CATALOGO_CAPACIDADES.json')
 project.setdefault('PI08_A_operational_adoption_historical',copy.deepcopy(project.get('operational_adoption')));project.setdefault('PI08_A_latest_selected_use_historical',copy.deepcopy(project.get('latest_selected_use')));project.setdefault('prior_selection_PI08_B',{'selected_life':project.get('selected_life'),'parent':project.get('parent'),'latest_saved_tick':project.get('latest_saved_tick')});project.update(selected_life=LIFE,latest_saved_tick=card['physical']['tick'],operational_current_cut=card['physical'],operational_current_snapshot={'path_relative_to_product':'sistema/'+card['snapshot'],'sha256':card['snapshot_sha256']},latest_selected_use=None,selected_operational_use_pending=True,parent=card['parent'],current_available_lives=list(dict.fromkeys([LIFE,*project.get('current_available_lives',[])])),operational_adoption={'decision_id':identifier,'scope':d['scope'],'physical_cut':card['physical'],'same_identity_relocation_map':str(CONTROL/'MAPA_TRASLADO_PRODUCTO_PI08_B.json'),'previous_principal_preserved':True})
 personal.update(life_id=LIFE,world_id=card['world_id'],current_saved_tick=card['physical']['tick'],current_saved_snapshot_sha256=card['snapshot_sha256'],first_selected_utc=now(),explicit_operational_adoption=identifier)
 config.setdefault('PI08_B_prior_selected_seed',dict(config));config.update(source_alias=LIFE,source_life=LIFE,source_tick=card['physical']['tick'],source_snapshot_sha256=card['snapshot_sha256'],current_operational_snapshot_sha256=card['snapshot_sha256'],current_operational_tick=card['physical']['tick'],current_operational_world_id=card['world_id'],source_paired_export_manifest=None,paired_export_manifest_sha256=None,existing_continuation_only=True,entry_availability='EXISTING_COMPLETE_CONTINUATION_SAME_ID_NO_NEW_IMPORT_SEED',explicit_operational_adoption=identifier,selection_scope='Open the existing moved committed continuation. No new world or fallback to an old paired seed.')
 continuity.setdefault('PI08_A_latest_operational_use_historical',copy.deepcopy(continuity.get('latest_operational_use')));continuity.setdefault('prior_cut_PI08_B',{k:continuity.get(k)for k in('life_id','world_id','physical_cut','parent','latest_snapshot')});continuity.update(latest_operational_use={'source_B_REAL_closed18':d['B_actual_closed_arms']['real'],'scope':'Actual learned source work before same-ID relocation; selected public/B use remains an explicit next operational gate.'},updated_utc=now(),life_id=LIFE,world_id=card['world_id'],profile=card['profile'],physical_cut=card['physical'],parent=card['parent'],latest_snapshot={'path_relative_to_product':'sistema/'+card['snapshot'],'sha256':card['snapshot_sha256']},identity_card={'path_relative_to_product':'sistema/estado/vidas/'+LIFE+'/VIDA.json','sha256':sha(S/'estado/vidas'/LIFE/'VIDA.json')},personal_selection=personal,selected_seed=config,operational_directories=['sistema/estado/'+n+'/'+LIFE for n in('vidas','servicios_persistentes','servicios_locales')],PI08_B_same_identity_relocation_map=str(CONTROL/'MAPA_TRASLADO_PRODUCTO_PI08_B.json'),proof={'promotion_decision':str(promotion),'product_reopening':str(reopening)},new_ticks_for_this_selection=0)
 entry=dict(d['catalog_entry']);entry.update(validated_lives=[{'life_id':LIFE,'physical':card['physical'],'snapshot_sha256':card['snapshot_sha256']}],implementation=[r['file']for r in prepared['deployed_code']],contract='contratos/PI08_B_USO_OPERATIVO_R01.json',assistance=d['assistance'],source_decision=str(file));catalog['entries']=[entry,*[e for e in catalog['entries']if e.get('id')!=entry['id']]]
 catalog.setdefault('PI08_B_prior_current_principal',catalog.get('current_principal'))
 catalog['current_principal']={'life_id':LIFE,'profile':card['profile'],'N':card['physical']['N'],'tick':card['physical']['tick'],'snapshot_sha256':card['snapshot_sha256'],'selection':'COMMITTED','world_id':card['world_id'],'prior_principal':{'life_id':PARENT,'tick':PARENT_T,'snapshot_sha256':PARENT_SHA},'actual_persistence_parent':card['parent'],'adoption_witness':str(ADOPTED),'unselected_zero_reopening_witness':str(reopening),'updated_utc':now(),'scope':'One selected same-identity successor. Old principal descriptors are historical; no branch memory fusion.'}
 # Existing Supervisor protocol prevents the launcher from trying import_new.
 transport=S/'estado/entrada_sencilla/vidas'/LIFE/'PROTOCOLO.json'
 protocol={'schema':'DEE.simple_entry.protocol.v1','life_id':LIFE,'world_id':card['world_id'],'source_snapshot_sha256':card['snapshot_sha256'],'source_life':LIFE,'pending_material':None,'uncertain_preserved':False,'history_is_transport_not_native_memory':True,'never_automatic_material_retry':True,'genesis_explicit_existing_life':True,'registered_existing_continuation_at':now(),'not_an_import_or_new_life':True}
 if transport.exists():raise FileExistsError('Existing entry protocol needs explicit reconciliation; never overwrite')
 write(transport,protocol)
 for rel,value in(('PROYECTO.json',project),('CONTINUIDAD_DEE_COGNITIVE_2_0.json',continuity),('sistema/estado/genesis/SELECCION_PERSONAL.json',personal),('aplicacion/GENESIS/SELECCION_CANDIDATA.json',config),('sistema/capacidades/CATALOGO_CAPACIDADES.json',catalog)):write(C/rel,value,True)
 parent(False);receipt={'schema':'DEE.PI08.B.same_identity.adopted_product.R01','phase':'COMMITTED','at':now(),'life_id':LIFE,'record':card,'Native_promotion':result,'commit_witness':witness,'contract':info(path),'reopening_proof':info(reopening),'comparison':comparison,'selected_references':{rel:info(C/rel)for rel in SELECTORS},'entry_protocol':info(transport),'writer_proof':writers,'new_ticks_for_movement_mapping_promotion':0,'source_history_not_rewritten':True,'old_principal_preserved':{'life_id':PARENT,'tick':PARENT_T,'snapshot_sha256':PARENT_SHA},'next':'Root actual selected Owner0 state/save/close, verify no physical change. No automatic material test.'};write(ADOPTED,receipt);return receipt
def main():
 ap=argparse.ArgumentParser(description=__doc__);group=ap.add_mutually_exclusive_group();group.add_argument('--prepare-move',action='store_true');group.add_argument('--adopt',action='store_true');ap.add_argument('--decision',type=Path);ap.add_argument('--reopening-proof',type=Path);ap.add_argument('--process-proof',type=Path);a=ap.parse_args()
 if not a.prepare_move and not a.adopt:
  print(json.dumps({'mode':'READ_ONLY_NO_NATIVE_IMPORT_NO_WRITES','source_system':str(CS),'target_system':str(S),'same_life_and_world_id':LIFE,'protected_principal':PARENT,'protected_tick':PARENT_T,'required_decision_fields':['approved_for_adoption','life_id','source_snapshot_sha256','source_tick','gates','approved_code_files','selectors_cas','catalog_entry','new_contract','scope','gains','losses','uncertainties','assistance','evidence','regression_coverage','process_proof'],'required_gates':GATES,'moves':['vidas/LIFE','servicios_persistentes/LIFE','servicios_locales/LIFE','all exact CAND.T* and import.CAND.* checkpoints including history closure'],'prepared_exists':PREPARED.exists(),'adopted_exists':ADOPTED.exists(),'Native_executed':False}));return
 if a.decision is None:raise ValueError('Explicit sealed final decision required')
 file=bounded(a.decision,P);d=decision(file);process=a.process_proof or Path(d['process_proof'])
 if a.adopt and a.reopening_proof is None:raise ValueError('Actual unselected reopening0 proof required')
 result=prepare(d,file,process)if a.prepare_move else adopt(d,file,bounded(a.reopening_proof,P),process)
 print(json.dumps({'proof':str(PREPARED if a.prepare_move else ADOPTED),'phase':result['phase'],'Native_ticks_advanced':0},ensure_ascii=False))
if __name__=='__main__':main()
