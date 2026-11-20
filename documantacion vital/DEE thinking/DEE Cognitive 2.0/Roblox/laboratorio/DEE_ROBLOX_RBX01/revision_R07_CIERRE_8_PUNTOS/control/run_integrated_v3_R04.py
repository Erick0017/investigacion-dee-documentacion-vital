"""Explicit Root-only Native + Studio loop. Import/help never start DEE or Studio.

All material IDs are durable before submission. Unknown material calls stop the
run; no alternate ID, automatic retry, target/answer or fallback calculator.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,sys,time,uuid
ROOT=Path(__file__).resolve().parents[1]
C02=ROOT.parent/'revision_R05_C02'
PRODUCT=ROOT.parents[2]
FINISH=1794874020 # 2026-11-17T00:07:00Z; validated from protocol below.
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p,name):
 spec=importlib.util.spec_from_file_location(name,p);mod=importlib.util.module_from_spec(spec)
 sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
def literal(text):
 for n in range(20):
  x='='*n
  if ']'+x+']' not in text:return '(['+x+'[!'+text+']'+x+']):sub(2)'
 raise ValueError('Lua delimiter')
def decode(report):
 need(report.get('status')=='REPLIED','MCP unknown; preserve ID and stop')
 value=report['reply']['result'];need(not value.get('isError'),'MCP rejected; preserve')
 for block in value.get('content',[]):
  if block.get('type')=='text':
   try:
    x=json.loads(block['text'])
    if isinstance(x,str):x=json.loads(x)
    if isinstance(x,(dict,list)):return x
   except(ValueError,TypeError):pass
 raise ValueError('No structured MCP result')
class LegacyWorld:
 def __init__(self,studio,output,record):
  self.studio=studio;self.output=output;self.record=record;self.serial=0
  self.operator=load(C02/'control/mcp_operator_C02.py','_r06_operator')
 def mcp(self,code,label,seconds=180):
  self.serial+=1
  self.record('MCP_INTENT',label=label,code_sha256=hashlib.sha256(code.encode()).hexdigest())
  result=decode(self.operator.run('execute_luau',{'studio_id':self.studio,'datamodel_type':'Server','code':code},
    self.output/f'MCP_{self.serial:04d}_{label}.json',seconds))
  self.record('MCP_COMPLETED',label=label,result=result)
  return result
 def initialize(self,state,identity,source_sha):
  # Existing source is transported byte-exact in bounded ASCII hex chunks.
  raw=json.dumps(state,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf8')
  self.mcp("local s=game:GetService('ServerStorage');assert(not s:FindFirstChild('R06Restore'));local f=Instance.new('Folder');f.Name='R06Restore';f.Parent=s;return {created=true}",'restore_init')
  for i in range(0,len(raw),3500):
   self.mcp("local f=game:GetService('ServerStorage').R06Restore;local n='c"+str(i//3500)+"';assert(not f:FindFirstChild(n));local v=Instance.new('StringValue');v.Name=n;v.Value='"+raw[i:i+3500].hex()+"';v.Parent=f;return {stored=true}",f'restore_chunk_{i//3500:04d}')
  expected={k:state[k] for k in ('world_id','scenario_sha256','native_life_id','native_tick','checkpoint_id')}
  expected.update(checkpoint_sha256=source_sha,owner_closed=True,bridge_quiescent=True)
  code="""local h=game:GetService('HttpService');local f=game:GetService('ServerStorage').R06Restore;local t={};for i=0,COUNT do local x=f['c'..i].Value;t[#t+1]=(x:gsub('..',function(v)return string.char(tonumber(v,16))end))end;local state=h:JSONDecode(table.concat(t));local api=require(game:GetService('ServerScriptService').RBX01Server.WorldAPI_R07);return api.initialize(state,h:JSONDecode(EXPECTED),h:JSONDecode(IDENTITY))""".replace('COUNT',str((len(raw)-1)//3500)).replace('EXPECTED',literal(json.dumps(expected))).replace('IDENTITY',literal(json.dumps(identity)))
  return self.mcp(code,'restore_apply_once')
 def call(self,identifier,kind,data):
  code="local h=game:GetService('HttpService');return require(game:GetService('ServerScriptService').RBX01Server.WorldAPI_R07).call("+literal(identifier)+','+literal(kind)+',h:JSONDecode('+literal(json.dumps(data,ensure_ascii=False,separators=(',',':'),allow_nan=False))+'))'
  return self.mcp(code,kind)
 def checkpoint(self,checkpoint_id,path):
  # Only at fully acknowledged boundary. Chunk data is private auditor transport.
  code="local h=game:GetService('HttpService');local s=game:GetService('ServerStorage');assert(not s:FindFirstChild('R06Export'));local f=Instance.new('Folder');f.Name='R06Export';local raw=h:JSONEncode(require(game:GetService('ServerScriptService').RBX01Server.WorldAPI_R07).checkpoint("+literal(checkpoint_id)+"));for i=1,#raw,12000 do local v=Instance.new('StringValue');v.Name='c'..math.floor((i-1)/12000);v.Value=(raw:sub(i,i+11999):gsub('.',function(c)return string.format('%02x',string.byte(c))end));v.Parent=f end;f:SetAttribute('bytes',#raw);f:SetAttribute('chunks',math.ceil(#raw/12000));f.Parent=s;return {bytes=#raw,chunks=math.ceil(#raw/12000)}"
  info=self.mcp(code,'checkpoint_export_once');parts=[]
  for i in range(info['chunks']):
   v=self.mcp("return {hex=game:GetService('ServerStorage').R06Export.c"+str(i)+".Value}",f'checkpoint_read_{i:04d}')
   parts.append(bytes.fromhex(v['hex']))
  raw=b''.join(parts);need(len(raw)==info['bytes'],'Checkpoint transport bytes')
  state=json.loads(raw);path.write_bytes(raw)
  self.record('WORLD_CHECKPOINT_SAVED',path=str(path),sha256=sha(path),bytes=len(raw),boundary=state['boundary'])
  return state
def _world_class():
 return load(ROOT/'control/world_comprimido_v3_R04.py','_r07_world_transport').CompressedWorld

class World:
 instances=[]
 def __new__(cls,*args,**kwargs):
  instance=_world_class()(*args,**kwargs);cls.instances.append(instance);return instance

def _execute(a):
 protocol={'native_hard_finish_utc':'2026-11-17T00:07:00Z','deadline_new_episodes_utc':'2026-11-16T23:00:00Z'}
 finish=datetime.datetime.fromisoformat(protocol['native_hard_finish_utc'].replace('Z','+00:00')).timestamp()
 new_cut=datetime.datetime.fromisoformat(protocol['deadline_new_episodes_utc'].replace('Z','+00:00')).timestamp()
 dest=a.destination.resolve(strict=True);output=a.output.resolve()
 need(dest.is_relative_to(ROOT/'native') and not output.exists() and output.is_relative_to(ROOT/'evidencia'),'Explicit fresh diagnostic destination/output')
 need(time.time()<new_cut-600,'No new block without finite margin')
 context=read(dest/'CONTEXTO_EJECUCION.json');life=context['life']
 need(life.startswith('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_') and life.rsplit('_',1)[-1] in ('MAIN','CTRL1','CTRL','PILOT'),'Only explicitly scoped R07 candidate/control/pilot')
 state=read(a.world);need(state['native_tick']==read(dest/'sistema/estado/vidas'/life/'VIDA.json')['physical']['tick'],'Native and world cut differ')
 need(29<=a.stop_cycle<=52 and a.stop_cycle>=state['boundary']['next_opportunity'],'Finite new opportunities')
 output.mkdir(parents=True);journal=output/'EVENTS.jsonl'
 def record(kind,**fields):
  with journal.open('a',encoding='utf8')as f:
   f.write(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kind':kind,**fields},ensure_ascii=False,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
 session=a.session or (state['S']['sessionId'] if state['native_life_id']==life and state['world_id']=='RBX01_CIERRE8_R07' else 'R07_MAIN_'+uuid.uuid4().hex[:20])
 identity={'life':life,'session':session,'participant':'LIVE_NATIVE'}
 world=World(a.studio_id,output,record,expected_place=a.expected_place)
 restored=world.initialize(state,identity,sha(a.world));record('RESTORED',result=restored,identity=identity)
 support=load(ROOT/'native/owner_support_v3_R04.py','_r07_support')
 adapters=load(ROOT/'native/adapter_v3.py','_r07_adapter')
 rows=[];record('PROTOCOL_STARTED',prospective_protocol=protocol,identity=identity,source_world=str(a.world),source_tick=state['native_tick'])
 with support.configured_owner(PRODUCT,dest,a.ledger,tag='R07_INTEGRAL',cutoff_epoch=finish,continuous=True)as owner:
  adapter=adapters.create_adapter({'owner':owner})
  def native(kind,payload,obs,cycle):
   operation='R07_'+session+'_'+str(cycle).zfill(2)+'_'+kind.upper()
   ctx={'session_id':session,'sequence':obs['seq'],'observation_id':obs['observationId'],'operation_id':operation,'mode':'LIVE_NATIVE'}
   record('NATIVE_INTENT',cycle=cycle,phase=kind,payload=payload,context=ctx)
   started=time.perf_counter();out=adapter.execute(kind,payload,ctx)
   record('NATIVE_COMPLETED',cycle=cycle,phase=kind,operation_id=operation,result=out,wall_seconds=time.perf_counter()-started)
   return out,operation
  for cycle in range(state['boundary']['next_opportunity'],a.stop_cycle+1):
   need(time.time()<new_cut,'New episode cutoff')
   base='WORLD_'+session+'_'+str(cycle).zfill(2)+'_'
   begun=world.call(base+'BEGIN','begin',{'cycle':cycle});obs=begun['observation']
   first,first_id=native('decision',{'observation':obs},obs,cycle)
   moved=world.call(base+'Q1','action',{'action':{'name':first['action'],'actionId':first_id,'nativeTick':first['nativeTick'],'null':first.get('null',False)}})
   route=None;tool=None;actual=None;op_id=first_id
   if 'observation'in moved:
    obs=moved['observation'];route,op_id=native('query_sensor',{'observation':obs},obs,cycle)
    moved=world.call(base+'Q2','action',{'action':{'name':route['action'],'actionId':op_id,'nativeTick':route['nativeTick'],'null':route.get('null',False)}})
   if moved.get('tool'):
    made,function_id=native('function',{'tool':moved['tool']},obs,cycle);tool=made['toolResult'];actual=tool.get('numeric_result')
    world.call(base+'TOOL','tool',{'output':tool,'nativeTick':made['nativeTick'],'operationId':function_id})
   fields=world.call(base+'FEEDBACK_FIELDS','feedback_fields',{})
   returned,feedback_id=native('feedback',fields['feedback'],fields['observation'],cycle)
   final=world.call(base+'COMPLETE','complete',{'nativeTick':returned['nativeTick'],'operationId':feedback_id})
   row={'cycle':cycle,'new_opportunity':cycle-28,'Native_Q1':first,'Native_Q2':route,'tool_result':tool,
    'actual_numeric':actual,'world_result':moved['result'],'executed_route':moved.get('executed_name'),
    'Native_route':moved.get('selected_name'),'state_after':final['S'],'boundary':final['boundary'],
    'host_order_prepared':False}
   rows.append(row);record('OPPORTUNITY_COMPLETED',**row)
  saved=owner.control('guardar');record('OFFICIAL_SAVE_COMPLETED',request_id=saved.get('id'))
 record('OWNER_CLOSED',life=life,expected_tick=rows[-1]['state_after']['nativeTick'])
 final=world.checkpoint('R07_PAIR_'+session+'_C'+str(a.stop_cycle),output/'WORLD_CHECKPOINT.json')
 result={'schema':'DEE.RBX01.R07.integrated.result.R01','identity':identity,'source_tick':state['native_tick'],
 'final_tick':final['native_tick'],'new_opportunities_completed':len(rows),'global_completed':a.stop_cycle,
 'rows':rows,'owner_closed':True,'new_Native_ticks':final['native_tick']-state['native_tick'],
 'world_checkpoint':str(output/'WORLD_CHECKPOINT.json'),'world_sha256':sha(output/'WORLD_CHECKPOINT.json'),
 'principal_modified':False,'new_scenario_sha256':final['scenario_sha256']}
 (output/'RESULTADO.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
 world.close()
 print(json.dumps({k:v for k,v in result.items()if k!='rows'},ensure_ascii=False))
def execute(a):
 try:return _execute(a)
 finally:
  for instance in World.instances:instance.close()
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute-root-only',action='store_true')
 p.add_argument('--destination',type=Path);p.add_argument('--world',type=Path);p.add_argument('--output',type=Path)
 p.add_argument('--ledger',type=Path);p.add_argument('--studio-id');p.add_argument('--stop-cycle',type=int);p.add_argument('--session');p.add_argument('--expected-place',default='DEE_RBX01_R07_NATIVE.rbxlx')
 a=p.parse_args();need(a.execute_root_only,'Explicit Root execution only; use --help for inspection')
 need(all((a.destination,a.world,a.output,a.ledger,a.studio_id,a.stop_cycle)),'All explicit diagnostic parameters required')
 execute(a)
