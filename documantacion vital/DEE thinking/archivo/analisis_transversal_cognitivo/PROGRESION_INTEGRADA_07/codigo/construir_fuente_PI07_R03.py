"""Generate the new R03 source from the preserved R02 episode, never patch R02."""
from pathlib import Path
import ast,hashlib
H=Path(__file__).resolve().parent
old=(H/'pi07_regulacion_R02.py').read_text('utf8')
assert hashlib.sha256((H/'pi07_regulacion_R02.py').read_bytes()).hexdigest()=='4a8ee4f8d0b4aa738d76492b609d5fb36d8e1ad7d1d44f59c213e5351a56a133'
header='''"""PI07 R03: preserved TC actor, fixed perpendicular P0 tool and new progress.

No world is opened on import. R01/R02 sources, metadata and journals remain
literal. A single legal new sink is prepared, never banks or clocks. Evaluated
episodes require separate hash-bound closed-calibration authorization.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,uuid
from capacidades import pi07_regulacion_R02 as previous
body=previous.body
VERSION='DEE.PI07.acquired_regulation.perpendicular_environment.R03'
KEY='DEE.Cognitive.PI07.regulation.environment.R03';FOLDER='PI07_REGULACION_ENV_R03'
PROTOCOL=Path(__file__).with_name('PROTOCOLO_PI07_R03.json')
PROTOCOL_SHA='f69e8558799558a1ccceb70e0684a061a971b9521ad8985205d1662aea55d269'
PREPARE='eci01-pi07-r03-preparar';START='eci01-pi07-r03-iniciar'
CALIBRATE='eci01-pi07-r03-calibrar';EPISODE='eci01-pi07-r03-episodio';STATE='eci01-pi07-r03-estado'
NEW_MODES={PREPARE,START,CALIBRATE,EPISODE,STATE};MODES={*previous.MODES,*NEW_MODES}
ORIGIN=body.ORIGIN;PREFIX=body.PREFIX;SENSOR=body.SENSOR;CUES=body.CUES
ACTUATOR=(53,48,56);MESSAGE_READER=(54,48,56);SINK=(56,48,56)
PULSE_CHANNEL='PI07.actuator.fixed_minusX.R03';MESSAGE_CHANNEL='PI07.environment.useful_plusX.R03';SINK_CHANNEL='PI07.environment.sink.R03'
CODEC_SHA=previous.CODEC_SHA
_native=body._native;_helper=body._helper;_observe=body._observe;_physical=body._physical
_read=body._read;_motor=body._motor;_submit=body._submit;_receipts=body._receipts;_summary=body._summary;_safe=body._safe;at=body.at
def _sha(b):return hashlib.sha256(b).hexdigest()
def _hash(value):return isinstance(value,str)and len(value)==64 and all(c in '0123456789abcdef'for c in value)
def protocol(material=False):
 data=PROTOCOL.read_bytes();p=json.loads(data)
 if _sha(data)!=PROTOCOL_SHA or p.get('schema')!='DEE.PI07.regulation.protocol.R03'or p.get('status')!='SEALED_FOR_VIABILITY_AND_CONDITIONAL_EVALUATION':raise ValueError('Exact immutable prospectively sealed R03 protocol required')
 if p.get('N')!=67 or p.get('origin')!=[8,40,50]or p.get('initial_reference_payloads')!={'A':0,'B':2}or p.get('delay_laps')!=6 or p.get('max_ticks_per_episode')!=1300:raise ValueError('Unchanged inherited Native TC body/calendar required')
 if len(p.get('schedule',[]))!=18 or len(p.get('viability',{}).get('schedule',[]))!=2:raise ValueError('Frozen18 offers or two diagnostic cases differ')
 for name,h in p['dependencies_sha256'].items():
  if Path(name).name!=name or not _hash(h)or _sha(Path(__file__).with_name(name).read_bytes())!=h:raise ValueError('Preserved dependency changed: '+name)
 if p['physical_environment']['pulse']['site']!=list(ACTUATOR)or p['physical_environment']['pulse']['direction']!=[-1,0,0]or p['physical_environment']['legitimate_packet']['reader_site']!=list(MESSAGE_READER):raise ValueError('Fixed perpendicular geometry differs')
 return p,PROTOCOL_SHA
def _identity(a):
 _,_,_,decode,_=_native();entries=dict(a.world.runtime.snapshot_metadata_entries)
 identity=decode(entries[body.SYSTEM_KEY]);life=identity['life_id']
 if int(a.world.runtime.dimension)!=67 or identity.get('profile')!='fisica_directa'or not life.startswith('ECI02_PI03_REPRO_')or any(v not in life for v in('PI04_','PI05_','PI07_')):raise ValueError('Explicit inherited N67 PI07 organization required')
 system=Path(__file__).resolve().parents[1];active=system/'estado/ACTIVO.json'
 if active.exists()and json.loads(active.read_text('utf-8-sig')).get('life_id')==life:
  contract=system/'contratos/PI07_REGULACION_USO_PRINCIPAL_01.json'
  c=json.loads(contract.read_text('utf-8-sig'))if contract.is_file()else{}
  if life!='ECI02_PI03_REPRO_PI04_PI05_PI07_CAND_01'or c.get('status')!='COMMITTED'or c.get('life_id')!=life or c.get('protocol_sha256')!=PROTOCOL_SHA or not _hash(c.get('adoption_decision_sha256')):raise ValueError('No selected use without exact explicit committed R03 permission')
 return identity
def _selected(a):
 active=Path(__file__).resolve().parents[1]/'estado/ACTIVO.json'
 return active.exists()and json.loads(active.read_text('utf-8-sig')).get('life_id')==_identity(a)['life_id']
def _old_literals(a):
 entries=dict(a.world.runtime.snapshot_metadata_entries)
 return{key:entries[key]for key in(body.KEY,previous.KEY)}
def _get(a):
 _,_,_,decode,_=_native();entries=dict(a.world.runtime.snapshot_metadata_entries)
 if KEY not in entries:raise ValueError('Explicit new R03 sink preparation required')
 m=decode(entries[KEY])
 if m['version']!=VERSION:raise ValueError('Exact R03 revision required')
 return m
def _save(a,m):a.world.runtime.set_snapshot_metadata(KEY,body._encoded(m))
def _home(directory,life):return body._home(directory,life).with_name(FOLDER)
def _record(a,m,directory,event):
 home=_home(directory,_identity(a)['life_id']);home.mkdir(exist_ok=True)
 data=(json.dumps(_safe({'index':m['log_count'],'tick':int(a.tick),**event}),ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\\n').encode('utf8')
 proposed={**m,'log_count':m['log_count']+1,'log_chain_sha256':_sha(bytes.fromhex(m['log_chain_sha256'])+data)};capsule=body._encoded(proposed)
 with(home/'eventos.jsonl').open('ab')as out:out.write(data);out.flush();os.fsync(out.fileno())
 m.update(proposed);a.world.runtime.set_snapshot_metadata(KEY,capsule)
def _authorization(text,expected):
 if not isinstance(text,str)or len(text.encode('utf8'))>8192 or _sha(text.encode('utf8'))!=expected:raise ValueError('Exact external authorization text/hash required')
 auth=json.loads(text)
 required={'schema','protocol_sha256','evaluation_authorized','calibration_proofs'}
 if set(auth)!=required or auth['schema']!='DEE.PI07.R03.closed_calibration.authorization.v1'or auth['protocol_sha256']!=PROTOCOL_SHA or auth['evaluation_authorized']is not True:raise ValueError('Closed-calibration authorization must bind this exact protocol')
 proofs=auth['calibration_proofs']
 if not isinstance(proofs,list)or len(proofs)!=2 or {v.get('forced_action')for v in proofs}!={'pulso','nada'}:raise ValueError('Both actual closed calibration arms required')
 for item in proofs:
  if set(item)!={'forced_action','path','sha256','closed','viability_passed'}or not isinstance(item['path'],str)or not item['path']or not _hash(item['sha256'])or item['closed']is not True or item['viability_passed']is not True:raise ValueError('Closed passing external calibration proof required, never actor advice')
 return auth
def validate_literal(row):
 if not isinstance(row,dict):raise ValueError('One explicit R03 operation required')
 mode=row.get('modo')
 if mode not in NEW_MODES:return previous.validate_literal(row)
 if mode==PREPARE:
  if set(row)!={'modo','prefijo_sha256'}or not _hash(row['prefijo_sha256']):raise ValueError('Actual complete post28 manifest SHA required')
 elif mode==START:
  role=row.get('clase');arm=row.get('brazo');expected={'modo','clase','brazo','registro_global'}|({'autorizacion','autorizacion_sha256'}if role=='evaluation'else set())|({'plan','plan_sha256'}if arm=='yoked'else set())
  if set(row)!=expected or role not in('viability','evaluation')or arm not in('real','none','yoked')or type(row['registro_global'])is not bool or(role=='viability'and arm!='real'):raise ValueError('Explicit calibration/evaluation role, return control and observation only')
  if role=='evaluation':_authorization(row['autorizacion'],row['autorizacion_sha256'])
  if arm=='yoked':previous._plan(row['plan'],row['plan_sha256'])
 elif mode==CALIBRATE:
  if set(row)!={'modo','forzar'}or row['forzar']not in('pulso','nada'):raise ValueError('Only a declared constant diagnostic force')
 elif mode==EPISODE:
  if set(row)-{'modo','actuator_ablation','sensor_ablation'}or any(type(row[k])is not bool for k in row if k!='modo'):raise ValueError('No environment/action/answer override; explicit link cuts only')
 elif set(row)!={'modo'}:raise ValueError('State has no material parameters')
def validate(a,row):
 validate_literal(row)
 if row['modo']not in NEW_MODES:return previous.validate(a,row)
 _identity(a)
 if row['modo']==STATE:return
 p,ph=protocol(material=True)
 if _selected(a)and row['modo']not in(STATE,EPISODE):raise ValueError('Selected use permits only state and already acquired opportunity')
 if row['modo']==PREPARE:
  if KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('R03 preparation already exists; no reinstall')
  old=previous._get(a);P0=body._get(a)
  if old['ordinal']!=28 or old.get('pending')or old.get('uncertain')or not old.get('ready')or not P0.get('ready'):raise ValueError('Only actual complete closed post28 R02 organization')
  return
 m=_get(a)
 if not m.get('ready')or m['protocol_sha256']!=ph or m.get('pending')or m.get('uncertain'):raise ValueError('Closed matching R03 preparation/progress required')
 if row['modo']==START:
  if m.get('admitted')or m['ordinal']!=0 or m['rows']:raise ValueError('No re-admission, bank or counter reset')
  return
 if not m.get('admitted')or m['ordinal']>=m['control']['max_ordinal']:raise ValueError('Explicit finite environment is absent or exhausted')
 if row['modo']==CALIBRATE:
  if m['role']!='viability'or(m.get('forced_action')is not None and m['forced_action']!=row['forzar']):raise ValueError('Two fixed diagnostic cases with one constant declared force per world')
 elif m['role']!='evaluation':raise ValueError('Calibration does not authorize learned-selection evaluation')
def prepare(a,row,directory):
 validate(a,row);identity=_identity(a);p,ph=protocol(True);start=int(a.tick);old=_old_literals(a)
 points={ACTUATOR,MESSAGE_READER}|{(SINK[0]+dx,SINK[1]+dy,SINK[2]+dz)for dx in(-1,0,1)for dy in(-1,0,1)for dz in(-1,0,1)}
 checks=[{'site':list(site),'observation':_observe(a,site)}for site in sorted(points)]
 conflicts=[v for v in checks if int(v['observation']['raw'])!=0]
 names={PULSE_CHANNEL,MESSAGE_CHANNEL,SINK_CHANNEL}
 if conflicts or names.intersection(set(a.world.runtime.channel_names)):raise ValueError('Fresh whole-RAW0 new inlet/reader/sink halo and unused namespaces required; never clear supports')
 if _home(directory,identity['life_id']).exists():raise ValueError('Preserve existing R03 journal')
 m={'version':VERSION,'life_id':identity['life_id'],'protocol_sha256':ph,'prepared_tick':start,'ready':False,'admitted':False,'ordinal':0,'rows':[],'pending':{'phase':'new_sink_preparation'},'uncertain':True,'log_count':0,'log_chain_sha256':'00'*32,
  'source_post28_manifest_sha256':row['prefijo_sha256'],'R01_metadata_sha256':_sha(old[body.KEY].encode('utf8')),'R02_metadata_sha256':_sha(old[previous.KEY].encode('utf8')),'body_P0':previous._get(a)['body_P0']}
 _save(a,m);_record(a,m,directory,{'kind':'R03_NEW_SINK_LEGAL_PREPARATION_INTENT','source_manifest_sha256':row['prefijo_sha256'],'preflight':checks,'no_banks_or_clocks_written':True})
 requests=[];body._declare(a.world,SINK_CHANNEL,SINK,(0,0,0),0,4);_submit(a,SINK_CHANNEL,0,start+2,requests,site=SINK,direction=(0,0,0));used=body.SafeAdapter(a);used.run_until(start+3)
 requests=_receipts(a,requests);summary=_summary(requests,start,int(a.tick));ready=summary['applied']==1 and summary['all_terminal']
 if ready:
  body._declare(a.world,PULSE_CHANNEL,ACTUATOR,(-1,0,0));body._declare(a.world,MESSAGE_CHANNEL,ACTUATOR,(1,0,0))
 m.update(ready=ready,pending=None if summary['all_terminal']else{'phase':'unknown_sink_admission'},uncertain=not summary['all_terminal'])
 if _old_literals(a)!=old:raise RuntimeError('Historical metadata altered by new sink preparation')
 _record(a,m,directory,{'kind':'R03_NEW_SINK_PREPARED','requests':requests,'Native_inputs':summary,'ready':ready,'old_R01_R02_literal_unchanged':True})
 return{'version':VERSION,'before_tick':start,'after_tick':int(a.tick),'new_native_ticks':int(a.tick)-start,'ready':ready,'requests':requests,'Native_inputs':summary,'preflight':checks,'R01_R02_metadata_literal_unchanged':True,'scope':'One legal P0 sink, new fixed interfaces and external progress; no new learned bank or reset.'}
def initialize(a,row,directory):
 validate(a,row);m=_get(a);before=_physical(a);old=_old_literals(a);p,ph=protocol(True)
 plan=previous._plan(row['plan'],row['plan_sha256'])if row['brazo']=='yoked'else None
 auth=_authorization(row['autorizacion'],row['autorizacion_sha256'])if row['clase']=='evaluation'else None
 m.update(admitted=True,role=row['clase'],forced_action=None,control={'arm':row['brazo'],'from_ordinal':0,'max_ordinal':2 if row['clase']=='viability'else 18 if row['brazo']=='real'else 12,'yoked_values':plan['values']if plan else None,'plan_sha256':row.get('plan_sha256'),'source_evidence_sha256':plan['source_evidence_sha256']if plan else None},instrumentation={'global_enabled':row['registro_global']},authorization_sha256=row.get('autorizacion_sha256'))
 _record(a,m,directory,{'kind':'R03_EXTERNAL_CONTROL_ADMITTED_ZERO_NATIVE','role':m['role'],'control':m['control'],'plan_literal':row.get('plan'),'authorization_literal':row.get('autorizacion'),'actor_receives_control_or_permission':False})
 if before!=_physical(a)or old!=_old_literals(a):raise RuntimeError('External admission changed Native/old metadata')
 return{'version':VERSION,'new_native_ticks':0,'before_tick':int(a.tick),'after_tick':int(a.tick),'requests':[],'admitted':True,'role':m['role'],'control':m['control'],'physical_unchanged':True,'R01_R02_metadata_literal_unchanged':True}
def _return(m,actual_failed):return previous._return(m,actual_failed)
def _emit(a,motor,seed,requests,ablation):
 # No context, sensor, return arm, expected answer or private environment.
 if motor==1 and not ablation:return _submit(a,PULSE_CHANNEL,0,seed,requests,site=ACTUATOR,direction=(-1,0,0))
 return None
def _instrumented(a,m,p,q,identity):
 safe=body.SafeAdapter(a);recorder=None;used=safe;settings=p['instrumentation']
 indices=settings['viability_episode_indices']if m['role']=='viability'else settings['episode_indices']
 if m['instrumentation']['global_enabled']and m['ordinal']in indices:
  path=Path(__file__).with_name('observador_global_PI05_R01.py')
  if _sha(path.read_bytes())!=CODEC_SHA:raise ValueError('Exact validated codec required')
  spec=importlib.util.spec_from_file_location('PI07_R03_exact_global_d60',path);capture=importlib.util.module_from_spec(spec);spec.loader.exec_module(capture)
  ticks=sorted({q+c+d for c in settings['centres_relative_query']for d in settings['neighbour_tick_offsets']})
  if len(ticks)!=31:raise ValueError('Frozen31frames required')
  target=Path(__file__).resolve().parents[1]/'estado/observacion_pasiva'/identity['life_id']/('PI07_R03_'+uuid.uuid4().hex)
  recorder=capture.GlobalRecorder(target,N=67,ticks=ticks,anchor_ticks={q+c for c in settings['anchor_relative_query']},provenance={'life_id':identity['life_id'],'ordinal':m['ordinal'],'version':VERSION,'actor_receives_recording':False},max_frames=31,max_compressed_bytes=67108864)
  used=capture.CapturingAdapter(safe,ticks=ticks,recorder=recorder)
 return used,safe,recorder
'''
episode=old[old.index('def episode('):old.index('\ndef state(')]
episode=episode.replace("spec=p['schedule'][m['ordinal']]","spec=(p['viability']['schedule']if m['role']=='viability'else p['schedule'])[m['ordinal']]")
episode=episode.replace("forced=None;ablation=", "forced=row.get('forzar')if row['modo']==CALIBRATE else None;ablation=")
episode=episode.replace("body_literal_before=dict(a.world.runtime.snapshot_metadata_entries)[body.KEY]", "body_literal_before=_old_literals(a)\n if forced is not None:m['forced_action']=forced")
episode=episode.replace("native_motor=_motor(reader['choice']);motor=native_motor", "native_motor=_motor(reader['choice']);motor=(1 if forced=='pulso'else -1)if forced is not None else native_motor")
episode=episode.replace("'PI07.environment.useful_plusX.R01'", 'MESSAGE_CHANNEL')
episode=episode.replace("dict(a.world.runtime.snapshot_metadata_entries)[body.KEY]==body_literal_before", "_old_literals(a)==body_literal_before")
episode=episode.replace("dict(a.world.runtime.snapshot_metadata_entries)[body.KEY]!=body_literal_before", "_old_literals(a)!=body_literal_before")
episode=episode.replace("'R01_body_metadata_literal_unchanged':", "'R01_R02_metadata_literal_unchanged':")
episode=episode.replace("'forced':False", "'forced':forced is not None")
episode=episode.replace("'ordinal':m['ordinal'],'before_tick':start", "'ordinal':m['ordinal'],'cumulative_PI07_ordinal':28+m['ordinal'],'before_tick':start")
tail='''
def state(a):
 entries=dict(a.world.runtime.snapshot_metadata_entries)
 return{'version':VERSION,'R03_prepared':KEY in entries,'progress':_get(a)if KEY in entries else None,'R01_P0':body._get(a),'R02_preserved':previous._get(a),'physical':_physical(a),'new_native_ticks':0,'scope':'No query, preparation, supply or Native advance.'}
def dispatch(a,row,*,actuator='closed',directory=None):
 validate(a,row)
 if row['modo']not in NEW_MODES:return previous.dispatch(a,row,actuator=actuator,directory=directory)
 if row['modo']==STATE:return state(a)
 if directory is None or actuator!='closed':raise ValueError('Exact owned home and closed legal interface required')
 _home(directory,_identity(a)['life_id'])
 if row['modo']==PREPARE:return prepare(a,row,directory)
 if row['modo']==START:return initialize(a,row,directory)
 return episode(a,row,directory)
def uncertain(a):
 entries=dict(a.world.runtime.snapshot_metadata_entries)
 return previous.uncertain(a)or(KEY in entries and bool(_get(a).get('uncertain')))
def _verify_journal(a,directory,key,folder,version,ph):
 _,_,_,decode,_=_native();m=decode(dict(a.world.runtime.snapshot_metadata_entries)[key]);identity=_identity(a)
 if m['version']!=version or m['protocol_sha256']!=ph:raise ValueError('Historical protocol/revision altered')
 home=body._home(directory,identity['life_id']).with_name(folder);journal=home/'eventos.jsonl';chain='00'*32;count=0
 with journal.open('rb')as lines:
  for line in lines:json.loads(line);chain=_sha(bytes.fromhex(chain)+line);count+=1
 if chain!=m['log_chain_sha256']or count!=m['log_count']or len(m['rows'])!=m['ordinal']:raise ValueError('Historical/progress journal inconsistency')
 for row in m['rows']:
  artifact=row.get('message_artifact');file=home/('mensaje_%04d.bin'%row['ordinal'])
  if artifact is not None:
   if artifact['file']!=file.name or not file.is_file()or file.stat().st_size!=artifact['bytes']or _sha(file.read_bytes())!=artifact['sha256']:raise ValueError('Actual Native message artifact differs')
  elif row.get('message_delivered')and not file.is_file():raise ValueError('Historical message artifact missing')
 return{'KEY':key,'protocol_sha256':ph,'ordinal':m['ordinal'],'journal':str(journal),'journal_sha256':_sha(journal.read_bytes())}
def operational_dependencies(a,directory):
 entries=dict(a.world.runtime.snapshot_metadata_entries)
 if KEY not in entries:return previous.operational_dependencies(a,directory)
 p,ph=protocol();_identity(a)
 prior=[_verify_journal(a,directory,body.KEY,body.FOLDER,body.VERSION,previous.R1_PROTOCOL_SHA),_verify_journal(a,directory,previous.KEY,previous.FOLDER,previous.VERSION,_sha(previous.PROTOCOL.read_bytes()))]
 m=_get(a)
 if _sha(entries[body.KEY].encode('utf8'))!=m['R01_metadata_sha256']or _sha(entries[previous.KEY].encode('utf8'))!=m['R02_metadata_sha256']:raise ValueError('Old R01/R02 metadata literal changed after R03')
 current=_verify_journal(a,directory,KEY,FOLDER,VERSION,ph)
 return{'version':VERSION,'historical_literal_journals':prior,'R03':current,'ready':m['ready'],'admitted':m['admitted'],'ordinal':m['ordinal'],'remaining':m.get('control',{}).get('max_ordinal',0)-m['ordinal'],'pending':m['pending'],'uncertain':m['uncertain'],'new_native_ticks':0,'scope':'Same inherited Native body/history; P0 fixed perpendicular tool, external offers and actual products. No general agency or adoption implied.'}
def code_files():return list(dict.fromkeys([Path(__file__),PROTOCOL,*previous.code_files()]))
'''
new=header+episode+tail
ast.parse(new)
target=H/'pi07_regulacion_R03.py'
if target.exists():raise FileExistsError('Preserve prior new R03 source')
target.write_text(new,encoding='utf8')
print(target,hashlib.sha256(target.read_bytes()).hexdigest(),target.stat().st_size)
