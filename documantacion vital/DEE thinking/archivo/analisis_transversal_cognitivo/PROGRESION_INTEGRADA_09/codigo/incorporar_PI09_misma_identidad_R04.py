"""Conditional Root-only same-identity relocation/adoption; default read-only.

Never imports a new life or advances Native time. All actual administrative
Store loads/saves/promotions require official Python and explicit final gates.
No phase runs on import. Partial moves remain fenced for diagnosis, never
silently retried, purged or replaced with an earlier future.
"""
from pathlib import Path,PurePosixPath
import argparse,ast,datetime,hashlib,importlib.util,json,os,shutil,sqlite3,sys,copy
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';CS=P/'estados/NATIVE/sistema';H=P/'codigo';CONTROL=P/'control'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01';PARENT='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01';PARENT_T=861426;PARENT_SHA='2eeef08e3bebac4e218178ed379fd99aa5fdeb03650c0454ad55c6534824c133'
SELECTORS=('PROYECTO.json','CONTINUIDAD_DEE_COGNITIVE_2_0.json','sistema/estado/ACTIVO.json','sistema/estado/genesis/SELECCION_PERSONAL.json','aplicacion/GENESIS/SELECCION_CANDIDATA.json','sistema/capacidades/CATALOGO_CAPACIDADES.json')
PREPARED=CONTROL/'PREPARACION_TRASLADO_PRODUCTO_PI09.json';ADOPTED=CONTROL/'ADOPCION_PRODUCTO_PI09.json';INTENT=CONTROL/'TRASLADO_PRODUCTO_PI09_EN_CURSO.json';BACKUP=CONTROL/'RESPALDO_INCORPORACION_PI09'
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

def selector_cas(d,allow_selected=False):
 for rel,h in d['selectors_cas'].items():
  if allow_selected and rel=='sistema/estado/ACTIVO.json'and read(C/rel).get('life_id')==LIFE:continue
  if sha(C/rel)!=h:raise ValueError('Concurrent selector/catalog change: '+rel)
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
 manifest=CONTROL/'MAPA_TRASLADO_PRODUCTO_PI09.json';write(manifest,{'source_system':str(CS),'target_system':str(S),'same_life_id':LIFE,'same_world_id':LIFE,'historical_parent_literal_preserved':card['parent'],'members':items,'logical_file_bytes':sum(r.get('bytes',0)for r in items),'not_a_new_life_or_import':True})
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
 from app.pi09_identidad_c2c_R01 import rebind_moved_C2C_identity
 mapping=rebind_moved_C2C_identity(Store(S),LIFE,manifest,sha(manifest))
 current=read(S/'estado/vidas'/LIFE/'VIDA.json');after=parser().snapshot_view(S/current['snapshot']);comparison=native_equal(before,after);parent();selector_cas(d)
 receipt={'schema':'DEE.PI09.same_identity.prepared_product.R01','phase':'PREPARED_MOVED_NOT_PROMOTED','at':now(),'decision':info(file),'life_id':LIFE,'source_native_before':before['physical'],'preserved_moved_source_snapshot':'sistema/'+card['snapshot'],'original_source_snapshot_sha256':card['snapshot_sha256'],'map':info(manifest),'deployed_code':rows,'prepared_permission_profile':info(S/'contratos/PI09_CONSULTA_OPERATIVA_R01.json'),'public_FI_material_before_promotion':False,'administrative_mapping':mapping,'comparison':comparison,'world_id_preserved':True,'history_parent_unchanged':current['parent']==card['parent'],'new_ticks':0,'next':'Root actual unselected product Owner load/state/save/close0, then --adopt with its real reopening witness. No repeated science.'};write(PREPARED,receipt);return receipt
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
 # Original preparation/decision stay immutable. Only the independently
 # reviewed two-file PREPARED-load administrative supplement may supersede
 # the corresponding source hash, with its original beforeimage proved.
 supplement_file=CONTROL/'CARGA_PREPARADA_PI09_APLICADA_R01.json';supplement=read(supplement_file)
 if supplement.get('schema')!='DEE.PI09.prepared_load.administrative_supplement.applied.R01'or supplement.get('applied')is not True or supplement.get('critical_state_before_after_equal')is not True or supplement.get('Native_executed')is not False or supplement['preparation']['sha256']!=sha(PREPARED)or supplement['decision']['sha256']!=sha(file):raise ValueError('Exact closed administrative source supplement required')
 proposed=read(H/'CARGA_PREPARADA_PI09_R01_PROPUESTA/PLAN.json')
 if supplement['files']!=proposed['files']:raise ValueError('Administrative supplement differs from reviewed plan')
 patches={r['file']:r for r in supplement['files']}
 if set(patches)!={'capacidades/pi09_permiso_operativo_R01.py','capacidades/pi09_carga_preparada_R01.py'}:raise ValueError('Only the exact two administrative sources may change')
 for row in prepared['deployed_code']:
  patch=patches.get(row['file'])
  if patch and patch['before_sha256']!=row['sha256']:raise ValueError('Administrative source beforeimage differs')
  if sha(S/row['file'])!=(patch['sha256']if patch else row['sha256']):raise ValueError('Deployed source changed outside the reviewed supplement')
 for row in supplement['files']:
  if sha(S/row['file'])!=row['sha256']or sha(Path(row['source']))!=row['sha256']:raise ValueError('Supplement source changed')
 if patches['capacidades/pi09_carga_preparada_R01.py']['before_sha256']is not None:raise ValueError('New administrative helper unexpectedly replaces a prior body')
 reasoned={k:d[k]for k in('scope','gains','losses','uncertainties','evidence','regression_coverage')};identifier=d.get('decision_id','PI08_ADOPCION_B_OPERATIVA_01');promotion=CONTROL/'DECISION_PROMOCION_PRODUCTO_PI09.json'
 reasoned.update(decision_id=identifier,route='COMPATIBLE',life_id=LIFE,snapshot_sha256=card['snapshot_sha256'],source_decision=info(file),reopening_proof=info(reopening),same_identity_relocation=prepared['map'],real_historical_parent=card['parent'])
 witness=native_commit(identifier,card['snapshot_sha256'])
 if witness is None:
  parent();write(promotion,reasoned);sys.path[:0]=[str(S),str(S/'app')];from app.lives import Store
  result=Store(S).promote(LIFE,promotion);witness=native_commit(identifier,card['snapshot_sha256'])
  if witness is None:raise ValueError('No matching Native COMMITTED witness; no metadata success asserted')
 else:result={'existing_COMMITTED_not_repeated':witness}
 # Publish exact permission immediately, before any selected Owner starts.
 contract=dict(d['new_contract']);contract.update(status='COMMITTED',life_id=LIFE,adoption_decision_sha256=sha(promotion),actual_native_commit_witness=witness)
 path=S/'contratos/PI09_CONSULTA_OPERATIVA_R01.json'
 if path.exists()and read(path)!=contract:
  prior=read(path)
  if prior.get('schema')!='DEE.PI09.exact_native_consultation_permission.v1'or prior.get('life_id')!=LIFE or prior.get('status')!='PREPARED_DIAGNOSTIC':raise FileExistsError('Another permission contract preserved')
  write(CONTROL/'PERFIL_PREPARADO_ANTES_COMMITTED_PI09.json',prior)
  write(path,contract,True)
 elif not path.exists():write(path,contract)
 project=read(C/'PROYECTO.json');continuity=read(C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json');personal=read(S/'estado/genesis/SELECCION_PERSONAL.json');config=read(C/'aplicacion/GENESIS/SELECCION_CANDIDATA.json');catalog=read(S/'capacidades/CATALOGO_CAPACIDADES.json')
 project.setdefault('PI08_A_operational_adoption_historical',copy.deepcopy(project.get('operational_adoption')));project.setdefault('PI08_A_latest_selected_use_historical',copy.deepcopy(project.get('latest_selected_use')));project.setdefault('prior_selection_PI09',{'selected_life':project.get('selected_life'),'parent':project.get('parent'),'latest_saved_tick':project.get('latest_saved_tick')});project.update(selected_life=LIFE,latest_saved_tick=card['physical']['tick'],operational_current_cut=card['physical'],operational_current_snapshot={'path_relative_to_product':'sistema/'+card['snapshot'],'sha256':card['snapshot_sha256']},latest_selected_use=None,selected_operational_use_pending=True,parent=card['parent'],current_available_lives=list(dict.fromkeys([LIFE,*project.get('current_available_lives',[])])),operational_adoption={'decision_id':identifier,'scope':d['scope'],'physical_cut':card['physical'],'same_identity_relocation_map':str(CONTROL/'MAPA_TRASLADO_PRODUCTO_PI09.json'),'previous_principal_preserved':True})
 personal.update(life_id=LIFE,world_id=card['world_id'],current_saved_tick=card['physical']['tick'],current_saved_snapshot_sha256=card['snapshot_sha256'],first_selected_utc=now(),explicit_operational_adoption=identifier)
 config.setdefault('PI09_prior_selected_seed',dict(config));config.update(source_alias=LIFE,source_life=LIFE,source_tick=card['physical']['tick'],source_snapshot_sha256=card['snapshot_sha256'],current_operational_snapshot_sha256=card['snapshot_sha256'],current_operational_tick=card['physical']['tick'],current_operational_world_id=card['world_id'],source_paired_export_manifest=None,paired_export_manifest_sha256=None,existing_continuation_only=True,entry_availability='EXISTING_COMPLETE_CONTINUATION_SAME_ID_NO_NEW_IMPORT_SEED',explicit_operational_adoption=identifier,selection_scope='Open the existing moved committed continuation. No new world or fallback to an old paired seed.')
 continuity.setdefault('PI08_A_latest_operational_use_historical',copy.deepcopy(continuity.get('latest_operational_use')));continuity.setdefault('prior_cut_PI09',{k:continuity.get(k)for k in('life_id','world_id','physical_cut','parent','latest_snapshot')});continuity.update(latest_operational_use={'source_PI09_NATIVE_closed12':d['PI09_actual_closed_arms']['native_real'],'scope':'Actual Native12 source before same-ID relocation. Selected public use remains a separate operational test.'},updated_utc=now(),life_id=LIFE,world_id=card['world_id'],profile=card['profile'],physical_cut=card['physical'],parent=card['parent'],latest_snapshot={'path_relative_to_product':'sistema/'+card['snapshot'],'sha256':card['snapshot_sha256']},identity_card={'path_relative_to_product':'sistema/estado/vidas/'+LIFE+'/VIDA.json','sha256':sha(S/'estado/vidas'/LIFE/'VIDA.json')},personal_selection=personal,selected_seed=config,operational_directories=['sistema/estado/'+n+'/'+LIFE for n in('vidas','servicios_persistentes','servicios_locales')],PI09_same_identity_relocation_map=str(CONTROL/'MAPA_TRASLADO_PRODUCTO_PI09.json'),proof={'promotion_decision':str(promotion),'product_reopening':str(reopening)},new_ticks_for_this_selection=0)
 entry=dict(d['catalog_entry']);entry.update(validated_lives=[{'life_id':LIFE,'physical':card['physical'],'snapshot_sha256':card['snapshot_sha256']}],implementation=[r['file']for r in prepared['deployed_code']],contract='contratos/PI09_CONSULTA_OPERATIVA_R01.json',assistance=d['assistance'],source_decision=str(file));catalog['entries']=[entry,*[e for e in catalog['entries']if e.get('id')!=entry['id']]]
 catalog.setdefault('PI09_prior_current_principal',catalog.get('current_principal'))
 catalog['current_principal']={'life_id':LIFE,'profile':card['profile'],'N':card['physical']['N'],'tick':card['physical']['tick'],'snapshot_sha256':card['snapshot_sha256'],'selection':'COMMITTED','world_id':card['world_id'],'prior_principal':{'life_id':PARENT,'tick':PARENT_T,'snapshot_sha256':PARENT_SHA},'actual_persistence_parent':card['parent'],'adoption_witness':str(ADOPTED),'unselected_zero_reopening_witness':str(reopening),'updated_utc':now(),'scope':'One selected same-identity successor. Old principal descriptors are historical; no branch memory fusion.'}
 # Existing Supervisor protocol prevents the launcher from trying import_new.
 transport=S/'estado/entrada_sencilla/vidas'/LIFE/'PROTOCOLO.json'
 protocol={'schema':'DEE.simple_entry.protocol.v1','life_id':LIFE,'world_id':card['world_id'],'source_snapshot_sha256':card['snapshot_sha256'],'source_life':LIFE,'pending_material':None,'uncertain_preserved':False,'history_is_transport_not_native_memory':True,'never_automatic_material_retry':True,'genesis_explicit_existing_life':True,'registered_existing_continuation_at':now(),'not_an_import_or_new_life':True}
 if transport.exists():raise FileExistsError('Existing entry protocol needs explicit reconciliation; never overwrite')
 write(transport,protocol)
 for rel,value in(('PROYECTO.json',project),('CONTINUIDAD_DEE_COGNITIVE_2_0.json',continuity),('sistema/estado/genesis/SELECCION_PERSONAL.json',personal),('aplicacion/GENESIS/SELECCION_CANDIDATA.json',config),('sistema/capacidades/CATALOGO_CAPACIDADES.json',catalog)):write(C/rel,value,True)
 parent(False);receipt={'schema':'DEE.PI09.same_identity.adopted_product.R01','phase':'COMMITTED','at':now(),'life_id':LIFE,'record':card,'Native_promotion':result,'commit_witness':witness,'contract':info(path),'reopening_proof':info(reopening),'comparison':comparison,'selected_references':{rel:info(C/rel)for rel in SELECTORS},'entry_protocol':info(transport),'writer_proof':writers,'new_ticks_for_movement_mapping_promotion':0,'source_history_not_rewritten':True,'administrative_source_supplement':info(supplement_file),'old_principal_preserved':{'life_id':PARENT,'tick':PARENT_T,'snapshot_sha256':PARENT_SHA},'next':'Root actual selected Owner0 state/save/close, verify no physical change. No automatic material test.'};write(ADOPTED,receipt);return receipt
def main():
 ap=argparse.ArgumentParser(description=__doc__);group=ap.add_mutually_exclusive_group();group.add_argument('--prepare-move',action='store_true');group.add_argument('--adopt',action='store_true');ap.add_argument('--decision',type=Path);ap.add_argument('--reopening-proof',type=Path);ap.add_argument('--process-proof',type=Path);a=ap.parse_args()
 if not a.prepare_move and not a.adopt:
  print(json.dumps({'mode':'READ_ONLY_NO_NATIVE_IMPORT_NO_WRITES','source_system':str(CS),'target_system':str(S),'same_life_and_world_id':LIFE,'protected_principal':PARENT,'protected_tick':PARENT_T,'required_decision_fields':['approved_for_adoption','life_id','source_snapshot_sha256','source_tick','gates','approved_code_files','selectors_cas','catalog_entry','new_contract','scope','gains','losses','uncertainties','assistance','evidence','regression_coverage','process_proof'],'required_gates':GATES,'moves':['vidas/LIFE','servicios_persistentes/LIFE','servicios_locales/LIFE','all exact CAND.T* and import.CAND.* checkpoints including history closure'],'prepared_exists':PREPARED.exists(),'adopted_exists':ADOPTED.exists(),'Native_executed':False}));return
 if a.decision is None:raise ValueError('Explicit sealed final decision required')
 file=bounded(a.decision,P);d=decision(file);process=a.process_proof or Path(d['process_proof'])
 if a.adopt and a.reopening_proof is None:raise ValueError('Actual unselected reopening0 proof required')
 result=prepare(d,file,process)if a.prepare_move else adopt(d,file,bounded(a.reopening_proof,P),process)
 print(json.dumps({'proof':str(PREPARED if a.prepare_move else ADOPTED),'phase':result['phase'],'Native_ticks_advanced':0},ensure_ascii=False))

def decision(file):
 d=read(file);required={'approved_for_adoption','life_id','source_snapshot_sha256','source_tick','gates','approved_code_files','selectors_cas','catalog_entry','new_contract','scope','gains','losses','uncertainties','assistance','evidence','regression_coverage','process_proof','PI09_actual_closed_arms','PI09_source_full_pair','PI09_reproduction_result','PI09_reproduction_comparison','PI09_conservation_proof','PI09_source_reopening_proof'}
 if not required<=set(d)or d['approved_for_adoption']is not True or d['life_id']!=LIFE:raise ValueError('Actual reasoned Root approval required; no prospective promotion')
 for name in GATES:
  gate=d['gates'].get(name,{})
  if gate.get('satisfied')is not True or not gate.get('criterion')or not gate.get('result')or not gate.get('evidence'):raise ValueError('Missing actual empirical gate: '+name)
 for item in d['evidence']+[e for gate in d['gates'].values()for e in gate.get('evidence',[])]:
  if sha(bounded(item['path'],P))!=item['sha256']:raise ValueError('Actual evidence hash differs')
 if set(d['selectors_cas'])!=set(SELECTORS):raise ValueError('All six existing product references require CAS')
 c=d['new_contract'];template=read(H/'PERMISO_OPERATIVO_PI09_R01_PROPUESTO/contratos/PI09_CONSULTA_OPERATIVA_R01.json')
 immutable=('schema','life_id','profile','protocol_sha256','allowed_modes','all_outer_FI_requests','public_FI_domain','internal_C2C_FI_redirected','FI_protocol_sha256','C2C_protocol_sha256','C2C_allowed_modes','frozen_files_sha256','finite_resources_preserved_without_reset','historical_PI07_environment_material_disabled')
 if any(c.get(k)!=template.get(k)for k in immutable)or c.get('status')!='PREPARED_DIAGNOSTIC'or c.get('adoption_decision_sha256')is not None or c.get('all_adoption_gates_met')is not True:raise ValueError('Exact separately prepared PI09 public/Native/C2C profile required')
 if c.get('public_arithmetic_policy')not in('legacy_partial','P0_phase19_fixed'):raise ValueError('Explicit public arithmetic scope required')
 if c['public_arithmetic_policy']=='P0_phase19_fixed':
  refs=c.get('arithmetic_guard_actual_evidence',[])
  if c.get('arithmetic_guard_actual_gate_met')is not True or len(refs)<2:raise ValueError('Actual paired/reserved P0 evidence required before public guard')
  for ref in refs:
   if sha(bounded(ref['path'],P))!=ref['sha256']:raise ValueError('P0 evidence changed')
 validate_PI09_evidence(d)
 return d

def evidence(ref):
 file=bounded(ref['path'],P)
 if sha(file)!=ref['sha256']:raise ValueError('Actual proof bytes changed')
 return read(file)

def validate_PI09_evidence(d):
 seal=read(H/'SELLO_PI09_CONSULTA_R02.json')
 if sha(H/'SELLO_PI09_CONSULTA_R02.json')!='30e0160fa4bdb05dd258295611a68416ddab7858fc06d1f9cea7e9b67df931d8':raise ValueError('Frozen normalized PI09 seal changed')
 arms=d['PI09_actual_closed_arms']
 if set(arms)!={'native_real','always_real','never','always_desacoplado'}:raise ValueError('All four actual prospectively declared PI09 arms required')
 for role,ref in arms.items():
  proof=evidence(ref);ops=[r for r in proof.get('records',[])if r.get('literal',{}).get('modo')=='eci01-pi09-episodio']
  if proof.get('life_id')!=seal['arms'][role]or proof.get('initial_tick')!=884835 or proof.get('closed')is not True or proof.get('error')is not None or len(ops)!=12:raise ValueError('Missing closed actual twelve-opportunity arm: '+role)
  for index,op in enumerate(ops):
   row=op['rows'][0]
   if row.get('ordinal')!=index or row.get('query_control')!=('native'if role=='native_real'else'never'if role=='never'else'always')or row.get('Native_inputs',{}).get('all_terminal')is not True:raise ValueError('Incomplete/misbound material PI09 arm')
  if role=='native_real'and proof['final_tick']!=d['source_tick']:raise ValueError('Approved source cut differs from canonical Native12')
 pair_ref=d['PI09_source_full_pair'];pair=bounded(pair_ref['path'],P);m=read(pair/'EXPORTACION_SERVICIO.json')
 if sha(pair/'EXPORTACION_SERVICIO.json')!=pair_ref['manifest_sha256']or m['life_id']!=LIFE or m['physical']['tick']!=d['source_tick']or sha(pair/m['native_snapshot'])!=m['snapshot_sha256']:raise ValueError('Actual complete canonical source pair required')
 reopened=evidence(d['PI09_source_reopening_proof'])
 expected_fields={'physical','causal_prefix_sha256','interfaces','pending_native','native_receipts','phase'}
 if(reopened.get('schema')!='DEE.PI09.mature_source.public_reopening0.R01'or reopened.get('life_id')!=LIFE or reopened.get('closed')is not True or reopened.get('owner_closed')is not True or type(reopened.get('new_ticks'))is not int or reopened['new_ticks']!=0 or reopened.get('new_Native_inputs')!=0 or reopened.get('initial_tick')!=d['source_tick']or reopened.get('final_tick')!=d['source_tick']or set(reopened.get('Native_field_equalities',{}))!=expected_fields or not all(reopened['Native_field_equalities'].values())or any(reopened.get(k)is not True for k in('physical_unchanged','causal_prefix_equal','operational_state_valid','pending_reconciled','stock_unchanged','all_scientific_metadata_literal_unchanged','source_code_unchanged','current_principal_unchanged'))):raise ValueError('Actual mature same-identity source public reopen0 with full Native/stock equality required')
 if reopened['before_snapshot']['sha256']!=m['snapshot_sha256']or reopened['after_snapshot']['sha256']!=d['source_snapshot_sha256']or reopened['snapshot_sha256']!=d['source_snapshot_sha256']:raise ValueError('Frozen canonical full pair -> current zero-reopened checkpoint binding differs')
 if reopened['stock_before']!=reopened['stock_after']or reopened['stock_after']!={'PI09':{'ordinal':12,'total':18,'remaining':6},'C2C':{'ordinal':31,'total':32,'remaining':1},'FI':{'ordinal':4,'total':8,'remaining':4}}:raise ValueError('Current finite source stock changed during reopen0')
 result=evidence(d['PI09_reproduction_result'])
 if result.get('status')!='COMPLETED'or result.get('owner_closed_coherently')is not True or result.get('criteria_met')is not True or result.get('life')not in seal['native_reproduction_ids']:raise ValueError('Actual full RP frontdoor cold12 result required')
 comparison=evidence(d['PI09_reproduction_comparison'])
 if comparison.get('physical_equal')is not True or comparison.get('causal_prefix_equal')is not True or comparison.get('unexpected_metadata_changes')!=[]:raise ValueError('Full actual Native replay comparison with narrow explained identity differences required')
 conservation=evidence(d['PI09_conservation_proof'])
 if conservation.get('closed')is not True or conservation.get('error')is not None:raise ValueError('Actual closed prospective conservation/challenge evidence required')
 if d['new_contract']['public_arithmetic_policy']=='P0_phase19_fixed'and not d['gates']['conservation']['satisfied']:raise ValueError('No untested public arithmetic repair')
 return True

def code(d):
 rows=[];seen=set();c=d['new_contract']
 for name,digest in c['frozen_files_sha256'].items():
  if Path(name).name!=name or sha(CS/'capacidades'/name)!=digest:raise ValueError('Scientific source changed: '+name)
 for item in d['approved_code_files']:
  rel=relative(item['file']);name=rel.as_posix();source=Path(item['source']).resolve(strict=True);target=bounded(S/rel,S,False);regular(source)
  if name in seen:raise ValueError('Repeated source delta target')
  seen.add(name)
  if not(source.is_relative_to(CS.resolve())or source.is_relative_to(H.resolve()))or source.suffix not in('.py','.json')or rel.parts[0]not in('app','capacidades','contratos')and name!='gestionar.py':raise ValueError('Only explicit reviewed current source/protocol/permission bytes; no engine/state')
  if rel.parts[0]=='contratos':
   if name!='contratos/PI09_CONSULTA_OPERATIVA_R01.json'or read(source)!=c:raise ValueError('Only the exact approved PREPARED contract may deploy before selection')
  if sha(source)!=item['sha256']or(target.exists()and sha(target)!=item.get('before_sha256'))or(not target.exists()and item.get('before_sha256')is not None):raise ValueError('Code CAS differs: '+name)
  ast.parse(source.read_bytes())if source.suffix=='.py'else read(source)
  rows.append({**item,'source':str(source),'target':str(target),'bytes':source.stat().st_size})
 required={'app/mundo_genesis_apd05.py','app/cola_local.py','app/pi09_identidad_c2c_R01.py','app/usar_dee.py','capacidades/pi04_dispatcher.py','capacidades/pi09_permiso_operativo_R01.py','capacidades/pi09_transporte_heredado_R02.py','capacidades/PI09_TRANSPORTE_HEREDADO_R02.json','capacidades/pi09_dispatcher_R02.py','capacidades/PI09_PLUGINS_R02.json','capacidades/pi09_consulta_selectiva_R02.py','capacidades/PROTOCOLO_PI09_CONSULTA_R01.json','capacidades/SELLO_PI09_CONSULTA_R02.json','contratos/PI09_CONSULTA_OPERATIVA_R01.json'}
 if not required<=seen:raise ValueError('Missing exact public/identity/dispatcher/whole-source required delta')
 if c['public_arithmetic_policy']=='P0_phase19_fixed'and 'capacidades/pi09_aritmetica_temporal_P0_R01.py'not in seen:raise ValueError('Approved P0 public helper missing')
 # Entire current dependency closure must remain available after the delta.
 source_manifest=read(P/'estados/NATIVE/SISTEMA_CODIGO_PI09.json')
 for original in source_manifest['files']:
  name=original['file']
  if name in seen:continue
  target=S/name
  if not target.is_file()or sha(target)!=original['sha256']:raise ValueError('Uncovered current dependency closure: '+name)
 return rows

if __name__=='__main__':main()
