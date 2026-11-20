"""STAGED four-op interface-reliability probe on a full committed14 clone.

No DEE, owner, world, file or process on import. Original R02 f7ba09... is
delegated literally. Three exogenous events are armed at once before the
first new choice. No decoder, bank, clock, base schedule or original is edited.
The result is exploratory and is never promoted automatically.
Technical R02: bind the immediate Main14 parent explicitly while preserving
the transport's historical source_main_* D fields. Scientific EXT_R01
protocol, keys, readers, inputs, channels, calendar and feedback stay literal.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,itertools,json,os

VERSION='DEE.PI10.four_op_device_reliability_extension.R01'
KEY='DEE.Cognitive.PI10.four_op_device_reliability_extension.R01'
FOLDER='PI10_DISPOSITIVO_EXT_R01';PROTOCOL=Path(__file__).with_name('PROTOCOLO_PI10_EXT_R01.json')
ARM0='eci01-pi10-ext-armar';EP='eci01-pi10-episodio';STATE='eci01-pi10-estado';MODES={ARM0,EP,STATE}
BASE_SHA='f7ba09cfea3ea93337ead47368ebbd9baba71b8590787aafe4515e6261cedf06'
MAIN='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'
COMPETITOR='PI10.EXT.R01.question_minusX';COMPETITOR_SITE=(35,40,30)
OLD_SINK=(36,40,30);SEM4_RAW=4<<60
def need(ok,why):
 if not ok:raise ValueError(why)
def sha(data):return hashlib.sha256(data).hexdigest()
def read(path):return json.loads(Path(path).read_text('utf-8-sig'))
def body():
 from capacidades import pi10_consulta_adaptativa_R02 as b
 need(sha(Path(b.__file__).read_bytes())==BASE_SHA,'Literal original R02 actor changed')
 return b
def encoded(value):return body().encoded(value)
def save(a,m):a.world.runtime.set_snapshot_metadata(KEY,encoded(m))
def current(a):
 entries=dict(a.world.runtime.snapshot_metadata_entries)
 need(KEY in entries,'Extension must be armed explicitly once before use')
 return json.loads(entries[KEY])
def protocol(a,material=False):
 b=body();p=read(PROTOCOL);c=b.config(a)
 need(p.get('schema')=='DEE.PI10.four_op_device_extension.protocol.R01','Exact extension protocol')
 need(p.get('base_actor_sha256')==BASE_SHA and p.get('ordinals')==[14,15,16,17]and p.get('competitor_ordinals')==[14,15]and p.get('extra_preview_ordinal')==17,'Fixed extension ordinals, never selected from actual answers')
 need(c['role']=='evaluation'and c['arm']=='real'and c['trace_control']=='none'and c.get('force_query')is None,'Only an unforced real diagnostic continuation')
 if material:
  need(p.get('status')=='SEALED_FOR_DIAGNOSTIC_EXT'and p.get('Root_execution_authorized')is True,'Root decides only after main adoption and remaining real resource budget')
  src=p['source_main'];need(src.get('life_id')==MAIN and src.get('ordinal')==14 and src.get('N')==67 and len(src.get('snapshot_sha256',''))==64,'Actual post-COMMITTED main14 source binding required')
  pair_ref=src['full_pair_manifest'];pair_path=Path(pair_ref['path']).resolve(strict=True);need(sha(pair_path.read_bytes())==pair_ref['sha256'],'Actual complete main14 export manifest differs');pair=read(pair_path)
  need(pair.get('life_id')==MAIN and pair.get('snapshot_sha256')==src['snapshot_sha256']and all(pair['physical'][k]==v for k,v in src['physical'].items()),'Extension must derive from actual Main14 complete export, not a relabelled control')
  _,base_ph,_=b.protocol(a,True);need(p.get('base_protocol_sha256')==base_ph,'Original R02 table/protocol must remain literal')
  ref=p['committed_proof'];q=Path(ref['path']).resolve(strict=True);need(sha(q.read_bytes())==ref['sha256'],'Actual COMMITTED proof bytes differ');v=read(q)
  need(v.get('phase')=='COMMITTED'and v.get('life_id')==MAIN,'No pre-adoption source may arm the extension')
 return p,sha(PROTOCOL.read_bytes()),c
def home(directory,a):
 base=body().home(directory,body().identity(a)['life_id']);need(base.is_dir(),'Complete inherited R02 artifact folder required')
 return base.parent/FOLDER
def parent_literals(a):
 b=body();out=b.old_literals(a);entries=dict(a.world.runtime.snapshot_metadata_entries);out[b.KEY]=entries[b.KEY];return out
def preflight(a):
 b=body();points={tuple(COMPETITOR_SITE[k]+d[k]for k in range(3))for d in itertools.product((-1,0,1),repeat=3)}
 rows=[{'site':list(s),**b.observe(a,s)}for s in sorted(points)];center=b.observe(a,COMPETITOR_SITE)
 unknown=[r for r in rows if int(r['raw'])!=0 and not(tuple(r['site'])==OLD_SINK and int(r['raw'])==SEM4_RAW)]
 return {'tick':int(a.tick),'site':list(COMPETITOR_SITE),'target':center,'halo1':rows,'exact_old_SEM4_exception_preserved':True,'eligible':int(center['raw'])==0 and not unknown,'unknown_RAW_conflicts':unknown,'scope':'Actual whole RAW before declaration. Known sink36 is not empty and is never rewritten. Future admission/effects remain measured.'}
def plan_calendars(a,ordinals=(14,15,16,17)):
 b=body();_,g,d,exact,_=b.native();origin=(24,12,12);now=int(a.tick)
 refs1=g.bank_observations(a,d,exact,origin);refs2=g.bank_observations(a,d,exact,g.OLD_ORIGIN)
 need(refs1['reference_clocks'][0]%782==refs1['reference_clocks'][1]%782 and refs2['reference_clocks'][0]%782==refs2['reference_clocks'][1]%782,'Actual paired reference clocks must be compatible')
 planned=[];cursor=now
 for ordinal in ordinals:
  cal=g.two_selector_calendar(cursor,refs1['reference_clocks'][0]+cursor-now,refs2['reference_clocks'][0]+cursor-now)
  planned.append({'ordinal':ordinal,'start_tick':cursor,'calendar':cal});cursor=cal['first']['settled_after_tick']
 return planned,{'q1':refs1,'q2':refs2,'scope':'Arithmetic clock projection only, clocks advance by elapsed Native ticks. No future RAW/bank content/target is read; calendar is not changed after an answer.'}
def validate_literal(row):
 need(isinstance(row,dict)and set(row)=={'modo'}and row.get('modo')in MODES,'Fixed extension mode only; no action, site, target or decoder override')
def validate(a,row):
 validate_literal(row);b=body();b.validate(a,{'modo':STATE})
 if row['modo']==STATE:return
 p,ph,_=protocol(a,True);m=b._get(a);need(not m.get('pending')and not m.get('uncertain')and m.get('ready')and m.get('admitted'),'Preserve uncertain/incomplete original future')
 if row['modo']==ARM0:
  need(KEY not in dict(a.world.runtime.snapshot_metadata_entries)and m['ordinal']==14 and len(m['rows'])==14,'One complete main14 descendant, exactly four remaining; no stock reset/re-arm')
  need(m.get('admission_control')=={'role':'evaluation','arm':'real','trace_control':'none','force_query':None},'Do not relabel a calibration/control history as the main continuation')
  need(b.identity(a)['life_id']!=MAIN,'Original main protected; explicit diagnostic clone required')
  finish=datetime.fromisoformat(p['hard_finish_utc'].replace('Z','+00:00'));need(finish.tzinfo is not None and(finish.astimezone(timezone.utc)-datetime.now(timezone.utc)).total_seconds()>=720 and p.get('Root_hard_aggregate_budgets_checked')is True,'At least twelve real minutes and Root hard-budget confirmation before arming; no deadline reset')
  actual=b.physical(a);expected=p['source_main']['physical'];need(set(expected)=={'N','tick','RAW_sha256','clocks_sha256'}and all(actual[k]==v for k,v in expected.items()),'Exact full current-source physical binding before arming')
  from capacidades import pi10_transporte_ancestral_R01 as transport
  cfg=transport.config();src=p['source_main']
  need(cfg.get('source_immediate_life_id')==src['life_id']and cfg.get('source_immediate_tick')==src['physical']['tick']and cfg.get('source_immediate_snapshot_sha256')==src['snapshot_sha256']and cfg.get('source_immediate_manifest_sha256')==src['full_pair_manifest']['sha256'],'Clone importer must bind exact immediate Main14 ID/tick/snapshot/full manifest; historical D source_main_* stays literal')
  basep,_,_=b.protocol(a,True);need(basep['schedule'][17]['cue']=='none','Extra17 is a declared addition to the unchanged None opportunity')
  return
 ext=current(a);need(ext.get('armed')and not ext.get('uncertain')and ext['protocol_sha256']==ph and m['ordinal']==ext['next_ordinal']and 14<=m['ordinal']<18,'Exact armed extension progression, no retry')
def ext_receipts(a,events):
 exact=body().native()[4]
 return [{**v,'receipt':exact(a.world.runtime.receipt(v['id']))}for v in events]
def arm(a,directory):
 validate(a,{'modo':ARM0});b=body();p,ph,_=protocol(a,True);before=b.physical(a);old=parent_literals(a);check=preflight(a)
 need(check['eligible'],'Occupied competitor RAW/halo; preserve, no cleanup/relocation')
 need(COMPETITOR not in set(a.world.runtime.channel_names),'New competitor namespace only')
 calendars,refs=plan_calendars(a);folder=home(directory,a);need(not folder.exists(),'Existing partial extension artifacts preserved');folder.mkdir()
 m={'version':VERSION,'armed':False,'uncertain':True,'protocol_sha256':ph,'source_main':p['source_main'],'arming_life_id':b.identity(a)['life_id'],'arming_tick':int(a.tick),'start_ordinal':14,'next_ordinal':14,'end_ordinal':18,'calendars':calendars,'events':[],'rows':[]}
 save(a,m)
 try:
  h=b.native()[0];h._channel(a.world,COMPETITOR,COMPETITOR_SITE,(-1,0,0),1,1)
  specs=[(14,COMPETITOR,calendars[0]['calendar']['first']['seed_tick']),(15,COMPETITOR,calendars[1]['calendar']['first']['seed_tick']),(17,b.Z_CHANNEL,calendars[3]['calendar']['first']['query_tick']-2)]
  for ordinal,channel,tick in specs:
   need(tick>int(a.tick),'All environmental events must be future before the first choice')
   r=a.world.submit(channel,0,tick);m['events'].append({'ordinal':ordinal,'channel':channel,'payload':0,'requested_tick':tick,'id':int(r.id),'scheduled_wall_utc':datetime.now(timezone.utc).isoformat(),'scheduled_before_first_new_choice':True})
  need(b.physical(a)==before and parent_literals(a)==old,'ARM0 may change interfaces/agenda, not RAW/clocks/stock/banks/history')
  initial_events=ext_receipts(a,m['events']);ready=all(v['receipt']['status']=='queued'for v in initial_events)
  m.update(armed=ready,uncertain=not ready);save(a,m)
  out={'version':VERSION,'report_recorded_utc':datetime.now(timezone.utc).isoformat(),'armed':ready,'arming_tick':int(a.tick),'new_native_ticks':0,'material_future_events_requested':3,'material_future_events_queued':sum(v['receipt']['status']=='queued'for v in initial_events),'preflight':check,'calendars':calendars,'reference_observations':refs,'events':initial_events,'original_R02_and_ancestors_literal_unchanged':True,'not_passive':'One interface and three legal future inputs are external apparatus/environment preparation. They are not Native agency or acquired content.'}
  data=(json.dumps(out,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf8')
  with(folder/'ARM0.json').open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
  return out
 except BaseException:
  m['uncertain']=True;save(a,m);raise
def episode(a,directory):
 validate(a,{'modo':EP});b=body();ext=current(a);ordinal=ext['next_ordinal'];planned=ext['calendars'][ordinal-14]
 need(int(a.tick)==planned['start_tick'],'Unexpected intervening Native time; do not retime armed environment')
 current_cal,_=plan_calendars(a,(ordinal,));need(current_cal[0]['calendar']==planned['calendar'],'Actual clock calendar differs; no adaptive rescheduling')
 folder=home(directory,a);need(folder.is_dir(),'Existing extension artifact home')
 try:
  result=b.dispatch(a,{'modo':EP},actuator='closed',directory=directory)
  need(result['ordinal']==ordinal and result['calendar']==planned['calendar'],'Base episode did not follow its original actual calendar')
  extras=ext_receipts(a,[v for v in ext['events']if v['ordinal']==ordinal]);all_events=ext_receipts(a,ext['events'])
  need(all(v['receipt']['status']=='applied'or v['receipt']['status'].startswith('rejected')for v in extras),'Due external event has an ambiguous receipt; preserve')
  report={'schema':VERSION,'report_recorded_utc':datetime.now(timezone.utc).isoformat(),'life_id':result['life_id'],'ordinal':ordinal,'before_tick':result['before_tick'],'after_tick':result['after_tick'],'base_actor_sha256':BASE_SHA,
   'original_base_witness':{'file':'../'+b.FOLDER+'/episodio_%04d.json'%ordinal,'sha256':sha((b.home(directory,result['life_id'])/('episodio_%04d.json'%ordinal)).read_bytes())},
   'base_Native_inputs':result['Native_inputs'],'external_events_due_this_episode':extras,'all_armed_event_receipts_at_this_cut':all_events,
   'actual_question':{'request':result['first_stage']['question_request'],'observation':result['first_stage']['question_observation'],'sample_register':result['first_stage']['sample_register']},
   'actual_q1':result['first_stage']['reader'],'actual_q2':result['second_stage']['reader'],'actual_FI':result['second_stage']['FI']['old_q6_choice'],'actual_resource':result['resource'],'actual_failed':result['actual_failed'],'returned_failed':result['returned_failed'],
   'interpretation':'Additional environment events were scheduled before choices. A changed signature is measured, never replaced by expected content. Physical delivery and attributed useful use remain separate. Exploratory clone only; no subjective state or automatic adoption.'}
  path=folder/('episodio_EXT_%04d.json'%ordinal);need(not path.exists(),'Do not overwrite a reached extension episode');data=(json.dumps(report,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf8')
  with path.open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
  ext['rows'].append({'ordinal':ordinal,'after_tick':int(a.tick),'file':path.name,'bytes':len(data),'sha256':sha(data)});ext['next_ordinal']+=1;save(a,ext)
  return {**result,'extension_protocol':VERSION,'extension_witness':ext['rows'][-1],'extra_environment_receipts':extras,'automatic_adoption':False}
 except BaseException:
  ext['uncertain']=True;save(a,ext);raise
def state(a):
 b=body();v=b.state(a);entries=dict(a.world.runtime.snapshot_metadata_entries)
 return {**v,'extension_version':VERSION,'extension':json.loads(entries[KEY])if KEY in entries else None,'new_native_ticks':0}
def dispatch(a,row,*,actuator='closed',directory=None):
 validate(a,row)
 if row['modo']==STATE:return state(a)
 need(actuator=='closed'and directory is not None,'Explicit owned closed diagnostic context required')
 return arm(a,directory)if row['modo']==ARM0 else episode(a,directory)
def uncertain(a):
 entries=dict(a.world.runtime.snapshot_metadata_entries);return body().uncertain(a)or(KEY in entries and json.loads(entries[KEY]).get('uncertain',False))
def operational_dependencies(a,directory):
 out=body().operational_dependencies(a,directory);entries=dict(a.world.runtime.snapshot_metadata_entries)
 if KEY not in entries:return out
 ext=json.loads(entries[KEY]);folder=home(directory,a)
 need((folder/'ARM0.json').is_file(),'Arming witness missing')
 for ref in ext['rows']:
  file=folder/ref['file'];need(file.is_file()and file.stat().st_size==ref['bytes']and sha(file.read_bytes())==ref['sha256'],'Extension witness changed/missing')
 receipts=ext_receipts(a,ext['events']);due_pending=[v for v in receipts if v['requested_tick']<=int(a.tick)and v['receipt']['status']!='applied'and not v['receipt']['status'].startswith('rejected')]
 need(not due_pending,'Due external event unresolved; never purge/re-arm')
 return {**out,'extension':{'version':VERSION,'armed':ext['armed'],'next_ordinal':ext['next_ordinal'],'remaining_original_stock':18-ext['next_ordinal'],'uncertain':ext['uncertain'],'actual_extra_receipts':receipts,'new_ticks':0}}
def code_files():return (Path(__file__),PROTOCOL,*body().code_files())
