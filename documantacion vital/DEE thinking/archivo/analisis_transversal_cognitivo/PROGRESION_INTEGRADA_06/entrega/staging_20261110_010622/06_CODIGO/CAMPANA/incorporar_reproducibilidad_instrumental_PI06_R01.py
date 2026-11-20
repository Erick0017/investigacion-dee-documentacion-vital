"""Additive PI06 instrument preservation/registration. Root alone uses --aplicar.

Default reads originals and writes a reviewable plan under PI06/codigo only.
No engine import, Native advancement, principal mutation or operational code
deployment. New recipes do not turn experimental futures into a principal.
"""
from pathlib import Path,PurePosixPath
from datetime import datetime,timezone
import argparse,ast,copy,hashlib,json,os,shutil,sqlite3,uuid
P=Path(__file__).resolve().parents[1];H=P/'codigo';S=P/'estados/candidato/sistema'
C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
STAGE=H/'RP_PI06_CIERRE_INSTRUMENTAL_R01';CAP='PI06_ORGANIZACION_INSTRUMENTOS_CIERRE_R04'
ALIAS='PI06_POST_INTERFERENCIA_T826449';PAIR_SHA='3e2e728b31b4f8e8b9bac165251c670c1f4691e5f4c1946895302d865be90e14'
MAIN='ECI02_PI03_REPRO_PI04_PI05_MAIN_01';SNAP='af74c8f47e43ed3b2395a338a23a6cbd42f105ec2cff4daac15b7a4d45e90832'
CONTRACT='contratos/PI06_REPRODUCIBILIDAD_INSTRUMENTAL_R01.json'
PINNED={'app/mundo_genesis_apd05.py':'4764ace6bb59196d35516928b86cee35baf1795236fe7cf56bdc786b284bf4c6',
 'app/cola_local.py':'226400a07b2ec18ef3796491e98caa89b369a2bba6ec078326a0486b0ec0ec84',
 'capacidades/pi06_organizacion_R01.py':'c2cec3a42ea9c033869a2c689564ea51faac079f929b51cc271463b396477285',
 'capacidades/pi06_interrupcion_R02.py':'80643a9d81ee92225350d3bc81a94d7e65c685e4c1b1f27b932cd9956454ef72',
 'capacidades/pi06_ambiente_R03.py':'9d06316836e24f915da74116d9b70f3eafa51bd0062934d974ee2a08ca8e99c6',
 'capacidades/pi06_ambiente_fino_R04.py':'69feb30ebbe621091ce9297f755021476ef2218df2cc177e8bb9b3baf8b1f280'}
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def encoded(x):return (json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf8')
def save(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as f:f.write(encoded(x))
def regular(p):
 for q in(p,*p.parents):
  if q.exists()and(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked source or target: '+str(q))
def rel(name):
 r=PurePosixPath(name)
 if not isinstance(name,str)or '\\'in name or ':'in name or r.is_absolute()or not r.parts or r.as_posix()!=name or any(x in('..','.')for x in r.parts):raise ValueError('Unsafe member path')
 return Path(*r.parts)
def check_members(root,rows):
 seen=set();total=0
 for r in rows:
  f=root/rel(r['file']);regular(f)
  if r['file']in seen or not f.resolve().is_relative_to(root.resolve())or not f.is_file()or f.stat().st_size!=r['bytes']or sha(f)!=r['sha256']:raise ValueError('Preserved material differs: '+r['file'])
  seen.add(r['file']);total+=r['bytes']
 return {'files':len(seen),'bytes':total}
def code_rows():
 omit={'estado','runtime','__pycache__','.git','.venv','site-packages','node_modules','documentacion'};rows=[]
 for base,dirs,names in os.walk(S,followlinks=False):
  base=Path(base);regular(base);dirs[:]=[n for n in dirs if n not in omit]
  for name in dirs:regular(base/name)
  for name in sorted(names):
   f=base/name;regular(f)
   if f.suffix not in('.pyc','.pyo'):rows.append({'file':f.relative_to(S).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)})
 rows.sort(key=lambda x:x['file']);index={r['file']:r['sha256']for r in rows}
 if any(index.get(name)!=h for name,h in PINNED.items()):raise ValueError('Current frozen S6 revision differs; do not update this qualified closure silently')
 return rows
def full_pair():
 pair=RP/'materiales'/ALIAS;regular(pair);mf=pair/'EXPORTACION_SERVICIO.json'
 if sha(mf)!=PAIR_SHA:raise ValueError('Use the already conserved complete post-interference pair; no large new copy')
 m=read(mf)
 if m['schema']!='DEE.persistent_service.paired_export.v1'or m.get('queue_journal_required')is not True or m['physical']['tick']!=826449 or m['physical']['N']!=67:raise ValueError('Exact complete pair required')
 checked=check_members(pair,m['members'])
 for name in m.get('empty_directories_preserved',[]):
  d=pair/rel(name);regular(d)
  if not d.is_dir():raise ValueError('A declared paired directory is missing')
 db=pair/'cola.sqlite3'
 if any(Path(str(db)+suffix).exists()for suffix in('-wal','-shm','-journal')):raise ValueError('Frozen standalone paired SQLite only')
 con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  if con.execute('pragma integrity_check').fetchone()[0]!='ok':raise ValueError('Pair SQLite integrity failure')
 finally:con.close()
 return pair,m,checked
def primary(proof_name,label):
 proof=P/'control'/proof_name;p=read(proof)
 if p.get('closed')is not True:raise ValueError('An original diagnostic has not closed')
 row=next(x for x in p['outcomes']if x['label']==label);f=Path(row['primary']);regular(f)
 if not f.resolve().is_relative_to((P/'ensayos').resolve())or sha(f)!=row['primary_sha256']:raise ValueError('Original current-operation primary identity differs')
 x=read(f);x=x['result'];x=json.loads(x)if isinstance(x,str)else x
 x=x['result']if 'result'in x and isinstance(x['result'],dict)and 'rows'in x['result']else x
 return p,x['rows'][0],{'path':str(proof),'sha256':sha(proof),'primary':str(f),'primary_sha256':sha(f)}
def step(label,literal,expected,path,*,all_applied=True):
 return {'label':label,'literal':literal,'feedback':'omit','actuator':'closed','receipt_paths':[['result','rows',0,'requests']],
  'stop_on_unapplied_receipt':all_applied,'read_path':path,'expected':expected,'stop_on_NULL':True}
def base_recipe(name,title):
 return {'schema':'DEE.reproduction.recipe.v1','id':name,'title':title,'revision':'R01_PREPARADA_REPLAY_NATIVE_PENDIENTE',
  'prefix':ALIAS,'code_capsule_key':CAP,'requires_explicit_material':True,
  'verification':{'state':'PREPARADA_REPLAY_NATIVE_PENDIENTE','Native_replay_verified':False},
  'assistance':['Operator chooses the frozen prefix, source geometry, timing, FI128 protocol and fixed readers. Every result is Native; references are evaluator-only.',
   'This is a diagnostic mechanism, not a learned intervention, autonomous repair or principal acquisition.'],
  'limitations':['A recipe is not an executed replay. Only R01 has a separate actual Native cold-replay verification.',
   'The complete prefix is shared history, not independent organisms. Material0 and NULL stay distinct.',
   'The principal PI05 N67 T824911 is unchanged and has not acquired PI06 diagnostic histories.']}
def make_recipes():
 name='pi06_interrupcion_causal_y_sham_R02';r=base_recipe(name,'PI06 R02: intervención legal contraflujo y sham, FI posterior');r.update(required_life_prefix='ECI02_PI03_REPRO_PI04_PI05_PI06_',reproduction_enabled=True,variants={})
 for arm,pn,label,expected in(('contraflujo','PI06_CUT_CONTRA_R02.json','INTERVENIR_CONTRAFLUJO',1),('sham','PI06_CUT_SHAM_R02.json','INTERVENIR_SHAM',-1)):
  p,v,evidence=primary(pn,'FI_INTACTO')
  if p['initial_tick']!=826449 or p['final_tick']!=826650 or p['new_ticks']!=201 or v['early_physical_choice']!=expected or v['old_q6_choice']!=expected or v['Native_inputs']['applied']!=176:raise ValueError('R02 original result differs')
  r['variants'][arm]={'batches':[[step('INTERVENIR',{'modo':'eci01-pi06-interrupcion','condicion':arm,'captura':'normal'},826452,['after_tick']),
    step('FI_INTACTO',{'modo':'eci01-pi06-fiplus','condicion':'intacto','izquierda':14,'derecha':3,'captura':'normal'},expected,['result','rows',0,'early_physical_choice'])]],
   'final_checks':[{'label':'fixed_q6','operation':'value','values':[{'step':'FI_INTACTO','path':['result','rows',0,'old_q6_choice']}],'expected':expected},
    {'label':'201ticks','operation':'difference','values':[{'step':'FI_INTACTO','path':['after_tick']},{'step':'INTERVENIR','path':['before_tick']}],'expected':201}],
   'native_receipt_expectations':{'unique_requested':177,'applied':177,'rejected':0,'pending_or_other':0},'original_execution':evidence}
 r['limitations'].append('Prepared normal-capture replay differs from the original global capture; it is not already validated passivity for this R02 intervention.')
 n='pi06_nube_fija_y_parada_host_R03';cloud=base_recipe(n,'PI06 R03: nube material fija y parada de seguridad del anfitrión')
 p,v,evidence=primary('PI06_AMBIENTE_NUBE_R06.json','AMBIENTE_NUBE')
 if p['status']!='HOST_SAFETY_STOP_CLOSED'or p['new_ticks']!=67 or v['birth_inputs']['applied']!=58 or v['birth_inputs']['rejected_occupied']!=3:raise ValueError('Preserve the actual cloud stop and adverse admissions')
 cloud.update(required_life_prefix='ECI02_PI03_REPRO_PI04_PI05_PI06_R03_',reproduction_enabled=False,
  blockers=['No new PI06 Native world/tick budget remains; any future material replication requires a new reviewed resource authorization.',
   'The historical R03 check every67ticks allowed near-global dense support before the finite host stop. It is preserved literally, not silently replaced by R04.',
   'R04 observed first safety crossing at+15 but has exact historical IDs and is not a fresh-ID executable recipe.'],
  variants={'nube_historica_bloqueada':{'batches':[[step('NUBE',{'modo':'eci01-pi06-ambiente','condicion':'nube','captura':'normal'},True,['result','rows',0,'host_safety_stop'],all_applied=False)]],
   'native_receipt_expectations':{'unique_requested':61,'applied':58,'rejected':3,'pending_or_other':0},
   'final_checks':[{'label':'67ticks_host_stop','operation':'value','values':[{'step':'NUBE','path':['result','rows',0,'new_native_ticks']}],'expected':67}],
   'original_execution':evidence}},historical_R04_evidence=[{'path':str(P/'control'/n),'sha256':sha(P/'control'/n)}for n in('PI06_CONFIRMACION_FINA_R04.json','PI06_CONFIRMACION_CONTROL67_R04.json')])
 cloud['verification']['state']='MATERIAL_PRESERVADO_EJECUCION_BLOQUEADA'
 cloud['limitations']+=['R03 produced no FI/C2C observation. A HostSafety stop is no measured functional failure or learned regulation.',
  'R04 control advanced1300ticks and was FAILED_PRESERVED for its declared bound; no retrospective bound change or adoption.']
 return {r['id']:r,cloud['id']:cloud}
def protected():
 act=C/'sistema/estado/ACTIVO.json';a=read(act);cardfile=C/'sistema/estado/vidas'/MAIN/'VIDA.json';card=read(cardfile)
 if a['life_id']!=MAIN or card['physical']['tick']!=824911 or card['snapshot_sha256']!=SNAP:raise ValueError('Selected principal differs; reconcile, never overwrite')
 files=[act,cardfile,C/'sistema'/card['snapshot'],RP/'codigo_preservado/PI06_ORGANIZACION_DIAGNOSTICO_R01/SISTEMA_CODIGO.json',RP/'recetas/pi06_transitorio_izq0_y_continuacion_R01.json']
 files +=[RP/n for n in('reproducir.py','importar_diagnostico.py','ejecutar_diagnostico.py','propietario_diagnostico.py','observador_pasivo.py')]
 return {str(p):sha(p)for p in files}
def closed_source():
 if (S/'estado/ACTIVO.json').exists()or (P/'PI06_ROOT_NATIVE_WRITER.lock').exists()or(RP/'EJECUCUCION_MATERIAL.lock').exists()or(RP/'EJECUCION_MATERIAL.lock').exists():raise ValueError('A selected/active/uncertain source blocks application')
 locks=S/'estado/locks'
 if locks.exists()and any(locks.iterdir()):raise ValueError('An S6 owner lock remains')
 for d in(S/'estado/servicios_persistentes').iterdir():
  db=d/'cola.sqlite3'
  if not db.exists():continue
  if any(Path(str(db)+s).exists()for s in('-wal','-shm','-journal')):raise ValueError('An S6 SQLite auxiliary is live/uncertain')
  q=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
  try:
   tables={r[0]for r in q.execute("select name from sqlite_master where type='table'")}
   if 'meta'in tables:
    row=q.execute("select value from meta where key='owner'").fetchone()
    if row and json.loads(row[0]).get('running'):raise ValueError('An S6 owner still reports running')
  finally:q.close()
def main(a):
 regular(STAGE);catalog=C/'sistema/capacidades/CATALOGO_CAPACIDADES.json';resource=RP/'RECURSOS.json';contract=C/'sistema'/CONTRACT
 if not a.aplicar:
  if STAGE.exists():raise FileExistsError('The first proposal is preserved; do not overwrite it')
  before=protected();rows=code_rows();pair,pm,pc=full_pair();recipes=make_recipes();oldres=resource.read_bytes();oldcat=catalog.read_bytes();cfg=json.loads(oldres);cat=json.loads(oldcat)
  if cat['schema']!='DCS1.1.capabilities.registry.v1':raise ValueError('Actual catalog schema differs')
  if contract.exists():raise FileExistsError('Existing PI06 instrumental contract protected')
  pairentry={'alias':ALIAS,'product_relative':pair.relative_to(C).as_posix(),'manifest_sha256':PAIR_SHA,'life_id':pm['life_id'],'tick':826449,'members':pc['files'],'bytes':pc['bytes'],'not_a_second_principal':True}
  if ALIAS in cfg.setdefault('pairs',{})and any(cfg['pairs'][ALIAS].get(k)!=pairentry[k]for k in('product_relative','manifest_sha256','life_id','tick')):raise ValueError('Stable pair alias conflicts')
  cfg['pairs'][ALIAS]={**cfg['pairs'].get(ALIAS,{}),**pairentry}
  if CAP in cfg.setdefault('code_capsules',{}):raise ValueError('Fresh capsule key required')
  capsule_manifest={'schema':'DEE.Cognitive.frozen_source_capsule.v1','id':CAP,'source_root':str(S),'files':rows,'created_utc':datetime.now(timezone.utc).isoformat(),'engine_shared_once':True,'Native_executed_by_preservation':False,
   'scope':'Frozen diagnostic R01-R04 tools; no state/engine/kernel copy and no principal adoption.'}
  manifest_bytes=encoded(capsule_manifest);mfsha=hashlib.sha256(manifest_bytes).hexdigest();capentry={'product_relative':(RP/'codigo_preservado'/CAP).relative_to(C).as_posix(),'manifest':'SISTEMA_CODIGO.json','manifest_sha256':mfsha}
  cfg['code_capsules'][CAP]=capentry
  entries=[{'id':'PI06_INSTRUMENTACION_Y_REPRODUCCION_01','name':'Evolución finita, observación global y reproducción diagnóstica PI06','kind':'instrumento_externo_y_procedimiento_P0','status':'AVAILABLE_IN_REPRODUCIBILITY_WITH_LIMITS',
   'implementation':['reproducibilidad/reproducir.py','reproducibilidad/recetas/pi06_transitorio_izq0_y_continuacion_R01.json'],'contract':CONTRACT,
   'principal_acquisition':False,'principal_unchanged':{'life_id':MAIN,'N':67,'T':824911,'snapshot_sha256':SNAP},'Native_replayed':['R01:600ticks,529/529,-1,+1,-1; complete Native state/prefix equality proved separately'],
   'limits':['1/3 useful FI outputs in that diagnostic sequence; replay coincidence is not3/3 cognitive success.','Observation passivity demonstrated only in the recorded bounded comparisons, not universally.']},
   {'id':'PI06_INTERRUPCION_Y_AMBIENTE_EXPERIMENTAL_01','name':'Interrupción causal local y ambiente material fijo: herramientas/evidencia preservadas','kind':'mecanismo_experimental_preparado_P0_sin_adquisicion_principal','status':'AVAILABLE_AS_EXPERIMENTAL_RECIPES_WITH_BLOCKERS',
    'implementation':['reproducibilidad/codigo_preservado/'+CAP,'reproducibilidad/recetas/pi06_interrupcion_causal_y_sham_R02.json','reproducibilidad/recetas/pi06_nube_fija_y_parada_host_R03.json'],'contract':CONTRACT,
    'principal_acquisition':False,'R02':'Original paired201ticks/177inputs each; contraflow+1,sham-1. Fresh Native replay pending.',
    'R03':'Cloud58applied/3occupied, host stop+67; no FI/C2C. New execution blocked.',
    'R04':'Fine same pulse host stop+15; control failed declared bound at+1300. Fixed historical IDs; no fresh-ID recipe or adoption.',
    'limits':['No learned protection, spontaneous regulation, new mental faculty or autonomous repair is established.','Shared prefixes are matched controls, not independent organisms.']}]
  ids={x['id']for x in cat['entries']}
  if any(x['id']in ids for x in entries):raise ValueError('Existing catalog entries protected')
  cat['entries'].extend(entries)
  contract_data={'schema':'DEE.PI06.instrumental_reproducibility.contract.v1','status':'INSTRUMENTAL_AVAILABLE_NOT_PRINCIPAL_ADOPTION','principal_unchanged':{'life_id':MAIN,'N':67,'T':824911,'snapshot_sha256':SNAP},
   'code_capsule':capentry,'complete_prefix':pairentry,'recipes':{n:{'reproduction_enabled':r['reproduction_enabled'],'state':r['verification']['state']}for n,r in recipes.items()},
   'R04_fixed_identity_instrument_not_fresh_replay':True,'no_new_Native_executed_by_registration':True,'no_operational_dispatcher_or_selector_change':True}
  STAGE.mkdir();save(STAGE/'SISTEMA_CODIGO_PROPUESTO.json',capsule_manifest);(STAGE/'RECURSOS_ANTES.json').write_bytes(oldres);(STAGE/'CATALOGO_ANTES.json').write_bytes(oldcat)
  save(STAGE/'RECURSOS_PROPUESTO.json',cfg);save(STAGE/'CATALOGO_PROPUESTO.json',cat);save(STAGE/'CONTRATO_PROPUESTO.json',contract_data)
  for n,r in recipes.items():save(STAGE/'recetas'/(n+'.json'),r)
  if protected()!=before or code_rows()!=rows:raise ValueError('Original critical/code changed during proposal')
  plan={'schema':'DEE.PI06.instrumental_RP_addition.plan.v1','Native_executed':False,'new_ticks':0,'code_capsule_id':CAP,'code_files':len(rows),'code_bytes':sum(x['bytes']for x in rows),
   'no_large_pair_copy':True,'existing_pair':pairentry,'existing_pair_checked':pc,'protected':before,'cas':{str(resource):hashlib.sha256(oldres).hexdigest(),str(catalog):hashlib.sha256(oldcat).hexdigest()},
   'staged_files':{p.relative_to(STAGE).as_posix():sha(p)for p in STAGE.rglob('*')if p.is_file()},'catalog_entry_ids':[x['id']for x in entries],
   'source_S6_modified':False,'product_operational_code_or_state_modified':False,'R01_literal_unchanged':True,'R02_replay_not_yet_executed':True,'R03_blocked':True,'R04_no_fresh_identity_recipe':True}
  save(STAGE/'PLAN.json',plan);print(json.dumps({'plan':str(STAGE/'PLAN.json'),'sha256':sha(STAGE/'PLAN.json'),'code_files':len(rows),'code_bytes':plan['code_bytes'],'Native_executed':False},ensure_ascii=False));return
 plan=read(STAGE/'PLAN.json');closed_source();before=protected()
 if before!=plan['protected']:raise ValueError('A protected original changed since the reviewed plan')
 for name,h in plan['staged_files'].items():
  if sha(STAGE/rel(name))!=h:raise ValueError('Reviewed proposal bytes changed')
 for name,h in plan['cas'].items():
  if sha(Path(name))!=h:raise ValueError('Resources/catalog CAS changed; preserve proposal and reconcile')
 manifest=read(STAGE/'SISTEMA_CODIGO_PROPUESTO.json');rows=code_rows()
 if manifest['files']!=rows:raise ValueError('S6 source differs from the reviewed capsule')
 full_pair();dest=RP/'codigo_preservado'/CAP;regular(dest)
 if dest.exists()or contract.exists():raise FileExistsError('Fresh additive capsule/contract only; no overwrite or blind retry')
 for n in('pi06_interrupcion_causal_y_sham_R02','pi06_nube_fija_y_parada_host_R03'):
  if (RP/'recetas'/(n+'.json')).exists():raise FileExistsError('A proposed recipe already exists')
 dest.mkdir()
 for row in rows:
  f=dest/rel(row['file']);f.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(S/row['file'],f)
 check_members(dest,rows);shutil.copyfile(STAGE/'SISTEMA_CODIGO_PROPUESTO.json',dest/'SISTEMA_CODIGO.json')
 if code_rows()!=rows:raise ValueError('Source changed during copying; preserve partial capsule')
 for f in(STAGE/'recetas').glob('*.json'):
  with (RP/'recetas'/f.name).open('xb')as out:out.write(f.read_bytes())
 with contract.open('xb')as out:out.write((STAGE/'CONTRATO_PROPUESTO.json').read_bytes())
 for target,proposed in((resource,STAGE/'RECURSOS_PROPUESTO.json'),(catalog,STAGE/'CATALOGO_PROPUESTO.json')):
  if sha(target)!=plan['cas'][str(target)]:raise ValueError('Concurrent catalog/resource change before CAS')
  tmp=target.with_name(target.name+'.PI06_'+uuid.uuid4().hex+'.tmp')
  with tmp.open('xb')as out:out.write(proposed.read_bytes());out.flush();os.fsync(out.fileno())
  if sha(target)!=plan['cas'][str(target)]:raise ValueError('Concurrent catalog/resource change; preserved staged temp')
  os.replace(tmp,target)
 after=protected()
 if after!=before:raise RuntimeError('Protected main, RP tools or R01 literal changed; do not claim unchanged')
 proof={'schema':'DEE.PI06.instrumental_RP_addition.applied.v1','recorded_utc':datetime.now(timezone.utc).isoformat(),'applied':True,'Native_executed':False,'new_ticks':0,
  'plan':str(STAGE/'PLAN.json'),'plan_sha256':sha(STAGE/'PLAN.json'),'code_capsule':str(dest),'capsule_manifest_sha256':sha(dest/'SISTEMA_CODIGO.json'),
  'code_members_verified':check_members(dest,rows),'complete_pair_not_copied':plan['existing_pair'],'catalog_entry_ids':plan['catalog_entry_ids'],
  'contract':str(contract),'contract_sha256':sha(contract),'resources_sha256':sha(resource),'catalog_sha256':sha(catalog),'protected_before':before,'protected_after':after,
  'principal_or_selectors_modified':False,'product_dispatchers_modified':False,'RP_Python_tools_modified':False,'old_R01_capsule_and_recipe_unchanged':True,
  'scope':'Experimental instruments/P0 and recoverable evidence only. No new mental capacity, principal acquisition, autonomous regulation or promotion.'}
 output=P/'control/INCORPORACION_REPRODUCIBILIDAD_INSTRUMENTAL_PI06_R01.json';save(output,proof)
 print(json.dumps({'proof':str(output),'sha256':sha(output),'Native_executed':False,'new_ticks':0},ensure_ascii=False))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');main(ap.parse_args())
