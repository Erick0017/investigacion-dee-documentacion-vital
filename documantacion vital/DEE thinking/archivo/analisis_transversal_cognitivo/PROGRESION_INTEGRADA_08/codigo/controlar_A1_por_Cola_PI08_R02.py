"""Root-only actual Cognitive queue tests, no new world/import and no Native
input/advance. PRE leaves real C2C30 active; A2 alone performs the valid commit.
POST checks transport/business idempotence on the already committed future.
Default prints the exact finite plan; --ejecutar is required to open an owner.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,sys
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';S=P/'estados/RP_A01/sistema';PY=C/'motor/python313/python.exe';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01'
C2KEY='DEE.Cognitive.PI04.C2C.coordination.R01';R3KEY='DEE.Cognitive.PI07.regulation.environment.R03';EXTKEY='DEE.Cognitive.PI08.C2C.prepared_environment32.R01'
def read(path):return json.loads(path.read_text('utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def put(path,value):
 with path.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def tree(home):return {p.relative_to(home).as_posix():sha(p)for p in sorted(home.rglob('*'))if p.is_file()}
def saved_view(parser):
 card=read(S/'estado/vidas'/LIFE/'VIDA.json');file=S/card['snapshot']
 if sha(file)!=card['snapshot_sha256']:raise ValueError('Actual saved pointer differs')
 return card,file,parser.snapshot_view(file)
def main(args):
 output=P/'control'/('PI08_A1_'+args.fase.upper()+'CONTROL_REAL_R02.json')
 if output.exists():raise FileExistsError('Existing actual test preserved; never auto-repeat')
 if not args.ejecutar:
  print(json.dumps({'mode':'PLAN_ONLY','phase':args.fase,'life_id':LIFE,'NativeRuntime_opened':False,'new_Native_inputs':0,'new_Native_ticks':0,'PRE_order':['invalid34expectedrejected_invalid','prepare32completedtoken','declaredprecommitexpectedfailed_preserved','repeatEXACTsamepreparetransportID','statezero','saveclose'],'POST_order':['verifyoriginalcompletedcommitID','repeatEXACTsamecommittransportID','newrequestsamecommittokenidempotent','statezero','saveclose']}));return
 parser=load('PI08_A1_passive_snapshot_parser',RP/'observador_pasivo.py');oldcard,oldfile,oldview=saved_view(parser);olddevice=S/'estado/servicios_locales'/LIFE/'PI04_C2C_COORDINACION_R01/dispositivo';oldtree=tree(olddevice);initial_tick=oldview['physical']['tick'];rows=[];owner=None
 critical=[C/'sistema/estado/ACTIVO.json',C/'sistema/estado/vidas/ECI02_PI03_REPRO_PI04_PI05_MAIN_01/VIDA.json'];protected={str(p):sha(p)for p in critical}
 if args.fase=='pre':
  current=json.loads(oldview['metadata'][C2KEY])
  if current['ordinal']!=30 or EXTKEY in oldview['metadata']:raise ValueError('Actual intact real30future required before PRE; no manufactured progress')
 else:
  if not args.commit_id:raise ValueError('Exact already completed A2commit ID required for POST')
  pre=read(P/'control/PI08_A1_PRECONTROL_REAL_R01.json');token=pre['token'];current=json.loads(oldview['metadata'][EXTKEY])
  if current.get('phase')!='COMMITTED'or current['token']!=token:raise ValueError('Only actual successful A2commit can receive POSTchecks')
 driver=load('PI08_existing_queue_owner_only',RP/'propietario_diagnostico.py');driver.configure(P,S,PY)
 def call(owner,label,literal,status='completed'):
  identifier='PI08_A1_'+args.fase.upper()+'_'+label+'_R01';owner.material(identifier,literal,feedback='omit',actuator='closed',allow_failure=True);file=P/'ensayos'/(identifier+'.json');saved=read(file)
  if saved['status']!=status:raise ValueError('Actual status differs; preserve request, no replay: '+identifier+' '+saved['status'])
  error=json.loads(saved['error'])if saved.get('error')else None
  if error and(error.get('checkpoint_error')or error.get('external_execution_may_be_uncertain')):raise ValueError('Uncertain/checkpoint-failed future preserved; no next request')
  value=json.loads(saved['result'])if saved.get('result')else None
  if value and(value['before_tick']!=initial_tick or value['after_tick']!=initial_tick):raise ValueError('Unexpected Native advance in administrative test')
  row=value['result']['rows'][0]if value else None;rows.append({'label':label,'id':identifier,'literal':literal,'status':saved['status'],'primary':str(file),'sha256':sha(file),'error':error,'row':row});return saved,row
 def same_transport(owner,identifier,literal):
  before=owner.q.get(identifier)
  if before is None or before['status']!='completed':raise ValueError('Only exact known-completed transport may be deliberately duplicated')
  payload=json.loads(before['payload'])
  if payload.get('operacion')!='sesion'or payload.get('situaciones')!=[literal]or payload.get('actuador','closed')!='closed'or payload.get('retorno','real')not in('real','omit'):raise ValueError('Actual completed transport must match the fixed literal; never invent feedback/settings')
  admission=owner.q.put(identifier,payload);after=owner.q.get(identifier)
  if admission.get('admission')!='existing_same_transport_request'or before!=after:raise ValueError('Idempotent transport changed an existing request')
  return {'id':identifier,'admission':admission['admission'],'same_request_bytes_and_terminal_record':True,'Native_reexecuted':False}
 try:
  with driver.Owner(LIFE,'PI08_A1_'+args.fase.upper())as owner:
   if args.fase=='pre':
    invalid,_=call(owner,'INVALID34',{'modo':'eci01-pi08-c2c-preparar','propuesta':'control34'},'rejected_invalid')
    error=json.loads(invalid['error'])
    if 'One bounded2..32-opportunity schedule required'not in error.get('detail',''):raise ValueError('The actual original34finite validator must be the rejecting cause')
    prepared,response=call(owner,'PREPARE',{'modo':'eci01-pi08-c2c-preparar'});token=response['token']
    call(owner,'INTERRUPT',{'modo':'eci01-pi08-c2c-prueba-precommit','token':token},'failed_preserved')
    duplicate=same_transport(owner,'PI08_A1_PRE_PREPARE_R01',{'modo':'eci01-pi08-c2c-preparar'})
   else:
    literal={'modo':'eci01-pi08-c2c-confirmar','token':token};duplicate=same_transport(owner,args.commit_id,literal)
    _,response=call(owner,'TOKEN_IDEMPOTENT',literal)
    if not response.get('already_committed')or not response.get('no_resources_or_experiences_repeated'):raise ValueError('Business token was not actually idempotent')
   call(owner,'STATE',{'modo':'eci01-pi08-c2c-estado'});owner.control('guardar')
  closed=owner.proc.poll()==0 and not(owner.q.get_meta('owner')or{}).get('running')
  if not closed or owner.q.outstanding():raise ValueError('Owner did not close/reconcile coherently')
  card,file,view=saved_view(parser);fields={k:oldview[k]==view[k]for k in('physical','causal_prefix_sha256','interfaces','pending_native','native_receipts','phase')};invariants={'C2C_metadata_literal_unchanged':oldview['metadata'][C2KEY]==view['metadata'][C2KEY],'R03_metadata_literal_unchanged':oldview['metadata'][R3KEY]==view['metadata'][R3KEY],'original30device_all_bytes_unchanged':oldtree==tree(olddevice),'protected_main_hashes_unchanged':all(sha(Path(p))==v for p,v in protected.items())}
  if args.fase=='pre':invariants['new32_KEY_not_committed']=EXTKEY not in view['metadata']
  valid=all(fields.values())and all(invariants.values())
  result={'schema':'DEE.PI08.A1.actual_queue_'+args.fase+'.v1','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'life_id':LIFE,'initial_tick':initial_tick,'final_tick':view['physical']['tick'],'new_Native_ticks':0,'new_Native_inputs':0,'NativeRuntime_opened':True,'closed':closed,'criteria_met':valid,'token':token,'rows':rows,'same_transport_test':duplicate,'full_Native_field_equalities':fields,'invariants':invariants,'before_snapshot':{'path':str(oldfile),'sha256':sha(oldfile)},'after_snapshot':{'path':str(file),'sha256':sha(file)},'no_other_world_imported_or_restored':True,'scope':'Actual existing Cognitive owner/queue/dispatcher; Runtime loading/checkpoint is technical. No Native cognitive input, birth or time advance. PREnever commits32; A2does the validcommit. Rejected34 and declared precommit failure remain recorded.'}
  put(output,result);print(json.dumps({'proof':str(output),'sha256':sha(output),'closed':closed,'criteria_met':valid,'token':token,'new_Native_ticks':0}));return 0 if valid else 2
 except BaseException as exc:
  failure=output.with_name(output.stem+'_FALLO_PRESERVADO.json')
  if not failure.exists():put(failure,{'schema':'DEE.PI08.A1.actual_queue.failure.v1','phase':args.fase,'life_id':LIFE,'initial_tick':initial_tick,'rows':rows,'error':type(exc).__name__+': '+str(exc),'automatic_retry':False,'owner_running_cache':None if owner is None else owner.q.get_meta('owner')})
  raise
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--fase',choices=('pre','post'),required=True);ap.add_argument('--commit-id');ap.add_argument('--ejecutar',action='store_true');raise SystemExit(main(ap.parse_args()))
