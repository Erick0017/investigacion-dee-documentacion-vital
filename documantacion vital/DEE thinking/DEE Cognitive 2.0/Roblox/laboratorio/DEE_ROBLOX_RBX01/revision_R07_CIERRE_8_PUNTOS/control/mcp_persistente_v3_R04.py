"""Explicit Root operator session: one official SDK process, serial tool calls.

Import does not connect. No Native/model/credentials. No automatic retry of ANY
call. Unknown replies latch the session; a late receipt may be reconciled under
its original RPC ID. Reconnect/repeat is explicit and restricted to a caller-
declared read. Native/action IDs inside arguments are never changed.
"""
from pathlib import Path
import argparse,base64,datetime,hashlib,importlib.util,json,queue,sys,threading,time,uuid
ROOT=Path(__file__).resolve().parents[1]
SDK_SOURCE=ROOT.parent/'revision_R05_C02/control/studio_mailbox_relay_C02_R07.py'
SDK_SHA='a4f55877761f17781621adc2fe9235b4166538e17011a825e70c9451b0b25f64'
ALLOWED={'list_roblox_studios','get_studio_state','inspect_instance','search_game_tree',
         'script_read','script_search','script_grep','get_console_output','execute_luau','multi_edit','start_stop_play','save_place'}
READ_TOOLS={'list_roblox_studios','get_studio_state','inspect_instance','search_game_tree','script_read','script_search','script_grep','get_console_output'}
def need(ok,message):
    if not ok:raise RuntimeError(message)
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write_new(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def decode_text(result):
    for block in result.get('content',[]):
        if block.get('type')=='text':
            try:
                value=json.loads(block['text'])
                if isinstance(value,str):value=json.loads(value)
                if isinstance(value,(dict,list)):return value
            except(ValueError,TypeError):pass
    return None
def sdk():
    need(sha(SDK_SOURCE)==SDK_SHA,'Preserved official persistent SDK wrapper differs')
    spec=importlib.util.spec_from_file_location('_r06_preserved_sdk',SDK_SOURCE)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module);return module

class Session:
    def __init__(self,studio_id,expected_place,output_directory,*,seconds=7200,_client_factory=None):
        need(isinstance(studio_id,str)and studio_id and isinstance(expected_place,str)and expected_place,'Exact Studio identity/file required')
        need(1<=seconds<=32400,'Finite SDK session lifetime required')
        self.studio_id,self.expected_place=studio_id,expected_place
        self.directory=Path(output_directory);need(not self.directory.exists(),'Fresh MCP session evidence directory only')
        self.seconds=seconds;self.deadline=time.monotonic()+seconds;self.factory=_client_factory
        self.client=None;self.lock=threading.Lock();self.pending=None;self.epoch=0;self.last_identifier=0
        self.closed=False;self.schemas={};self.session_id='MCP_SESSION_'+uuid.uuid4().hex
    def _log(self,kind,**values):
        with(self.directory/'SESSION.jsonl').open('a',encoding='utf8')as f:f.write(json.dumps(dict(utc=stamp(),kind=kind,session_id=self.session_id,epoch=self.epoch,**values),ensure_ascii=False,separators=(',',':'))+'\n');f.flush()
    def _bootstrap(self):
        need(time.monotonic()<self.deadline,'Finite session expired')
        factory=self.factory or sdk().MCPClient
        self.client=factory(max(1,self.deadline-time.monotonic()));self.client.identifier=self.last_identifier
        self.epoch+=1
        initialized=self.client.call('initialize',{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'DEE-R06-Root-Persistent','version':'R01'}},timeout=120)
        need(isinstance(initialized,dict)and 'serverInfo'in initialized,'Official SDK initialization rejected')
        self.client.call('notifications/initialized',notification=True)
        listing=self.client.call('tools/list',{},timeout=120)
        self.schemas={v['name']:v for v in listing.get('tools',[])}
        need({'execute_luau','list_roblox_studios'}<=self.schemas.keys(),'Official tools not ready; no polling/relaunch/mutation attempted')
        raw=self.client.call('tools/call',{'name':'list_roblox_studios','arguments':{}},timeout=120)
        inventory=decode_text(raw)
        need(isinstance(inventory,dict)and isinstance(inventory.get('studios'),list),'Structured Studio inventory required')
        target=next((x for x in inventory['studios']if x.get('id')==self.studio_id),None)
        need(target is not None and target.get('file')==self.expected_place,'Exact Studio/file not connected; never choose another target')
        self.last_identifier=self.client.identifier
        bootstrap=self.directory/('BOOTSTRAP_'+str(self.epoch)+'.json')
        write_new(bootstrap,dict(initialized=initialized,tools=listing,inventory=raw,target=target,
            sdk_source=str(SDK_SOURCE),sdk_sha256=SDK_SHA,pid=getattr(getattr(self.client,'process',None),'pid',None)))
        self._log('CONNECTED',bootstrap=str(bootstrap),bootstrap_sha256=sha(bootstrap),sdk_pid=getattr(getattr(self.client,'process',None),'pid',None))
    def __enter__(self):
        self.directory.mkdir(parents=True);self._log('OPEN_INTENT',studio_id=self.studio_id,expected_place=self.expected_place,seconds=self.seconds)
        try:self._bootstrap()
        except BaseException:
            self.close();raise
        return self
    def _report(self,call_id,tool,args,out,rpc_id,result,started,*,attempt=1,reconciled=False):
        for index,block in enumerate(result.get('content',[])):
            if block.get('type')=='image':
                raw=base64.b64decode(block.pop('data'),validate=True);suffix='.png'if block.get('mimeType')=='image/png'else'.jpg'
                image=out.with_name(out.stem+'_image_'+str(index)+suffix)
                with image.open('xb')as f:f.write(raw)
                block.update(local_image=str(image),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        report=dict(schema='DEE.RBX01.official_MCP_operator_call.C02',status='TOOL_ERROR'if result.get('isError')else'REPLIED',
            tool=tool,arguments=args,reply={'jsonrpc':'2.0','id':rpc_id,'result':result},
            persistent_session=self.session_id,transport_epoch=self.epoch,logical_call_id=call_id,attempt=attempt,
            elapsed_seconds=time.monotonic()-started,reconciled_late_reply=reconciled,
            Native_imported_by_client=False,credentials_read=False,sdk_pid=getattr(getattr(self.client,'process',None),'pid',None))
        write_new(out,report);self._log('CALL_REPLIED',logical_call_id=call_id,rpc_id=rpc_id,output=str(out),status=report['status'],elapsed_seconds=report['elapsed_seconds'])
        return report
    def run(self,tool,arguments,output,timeout=180,*,read_only=False,_logical_call_id=None,_attempt=1):
        with self.lock:
            need(not self.closed and self.client is not None,'Explicit open persistent session required')
            need(self.pending is None,'Prior reply unknown; reconcile original ID before another call')
            need(tool in ALLOWED and isinstance(arguments,dict)and 1<=timeout<=300,'Closed tool/arguments/bounded timeout')
            need(tool in self.schemas,'Tool not present in this one SDK discovery')
            need(set(self.schemas[tool].get('inputSchema',{}).get('required',[]))<=arguments.keys(),'Missing required actual SDK fields')
            if tool!='list_roblox_studios':need(arguments.get('studio_id')==self.studio_id,'Different Studio target refused')
            need(not read_only or tool in READ_TOOLS or tool=='execute_luau','Mutation tool cannot be declared read-only')
            output=Path(output);need(not output.exists(),'Preserve previous call result')
            intent=output.with_name(output.stem+'.INTENT.json');need(not intent.exists(),'Preserve previous call intent')
            call_id=_logical_call_id or'CALL_'+uuid.uuid4().hex;rpc_id=self.client.identifier+1;started=time.monotonic()
            info=dict(logical_call_id=call_id,rpc_id=rpc_id,tool=tool,arguments=arguments,read_only=read_only,
                      attempt=_attempt,utc=stamp(),session_id=self.session_id,transport_epoch=self.epoch,no_automatic_retry=True)
            write_new(intent,info);self._log('CALL_INTENT',**{k:v for k,v in info.items()if k not in('session_id','transport_epoch','utc')})
            try:
                result=self.client.call('tools/call',{'name':tool,'arguments':arguments},timeout=timeout)
                self.last_identifier=self.client.identifier
                return self._report(call_id,tool,arguments,output,rpc_id,result,started,attempt=_attempt)
            except BaseException as error:
                self.last_identifier=self.client.identifier
                known=getattr(error,'sdk_result',None)
                unknown=not(isinstance(known,dict)and known.get('id')==rpc_id)
                report=dict(schema='DEE.RBX01.official_MCP_operator_call.C02',status='FAILED_PRESERVED',tool=tool,arguments=arguments,
                    logical_call_id=call_id,rpc_id=rpc_id,transport_epoch=self.epoch,attempt=_attempt,error_type=type(error).__name__,error=str(error),
                    actual_sdk_error_reply=known,reply_unknown=unknown,no_automatic_retry=True,Native_imported_by_client=False)
                write_new(output,report);self._log('CALL_FAILED_PRESERVED',logical_call_id=call_id,rpc_id=rpc_id,reply_unknown=unknown,output=str(output))
                if unknown:self.pending=dict(info,started=started)
                raise
    def reconcile_pending(self,output,timeout=60):
        """Wait for the SAME already-sent RPC reply. Sends no RPC or mutation."""
        with self.lock:
            need(self.pending is not None and self.client is not None,'No unknown receipt to reconcile')
            need(1<=timeout<=120,'Bounded receipt reconciliation only');p=self.pending
            end=min(self.deadline,time.monotonic()+timeout)
            while time.monotonic()<end:
                try:reply=self.client.incoming.get(timeout=max(.01,end-time.monotonic()))
                except queue.Empty:break
                if reply.get('id')==p['rpc_id']:
                    need('result'in reply,'Original RPC returned error; preserve explicit SDK error')
                    result=self._report(p['logical_call_id'],p['tool'],p['arguments'],Path(output),p['rpc_id'],reply['result'],p['started'],attempt=p['attempt'],reconciled=True)
                    self.pending=None;return result
                need(not(reply.get('transportEOF')or reply.get('invalidProtocolLine')),'Original SDK transport unavailable; unknown receipt preserved')
            raise TimeoutError('Original RPC receipt remains unknown; nothing resent')
    def reconnect_read_only(self):
        """Explicit transport reopen after an unknown READ, never repeats it."""
        with self.lock:
            need(self.pending is not None and self.pending['read_only'],'Unknown mutation cannot reconnect/retry through this method')
            pending=self.pending.copy();self.client.close();self.client=None
            self._bootstrap();self.pending=None
            self._log('EXPLICIT_READ_RECONNECT_NO_REPLAY',logical_call_id=pending['logical_call_id'],old_rpc_id=pending['rpc_id'])
            return pending
    def repeat_read_explicit(self,pending,output,timeout=180):
        need(pending.get('read_only')is True,'Only an explicitly reconciled read may be repeated')
        return self.run(pending['tool'],pending['arguments'],output,timeout,read_only=True,
                        _logical_call_id=pending['logical_call_id'],_attempt=pending['attempt']+1)
    def close(self):
        if self.closed:return
        self.closed=True
        if self.client is not None:
            self.last_identifier=self.client.identifier;self.client.close()
        if self.directory.is_dir():self._log('CLOSED',unknown_original_request_preserved=self.pending,closes_only_owned_sdk_child=True)
    def __exit__(self,*args):self.close()

_session=None
def configure(studio_id,expected_place,output_directory,*,seconds=7200):
    global _session
    need(_session is None,'Persistent default session already configured')
    _session=Session(studio_id,expected_place,output_directory,seconds=seconds);return _session.__enter__()
def run(tool,arguments,output,seconds=180,wait_file=None):
    need(wait_file is None,'No automatic discovery polling in persistent operator')
    need(_session is not None,'Root must call configure once, not autostart a process percall')
    return _session.run(tool,arguments,output,seconds)
def close():
    global _session
    if _session is not None:_session.close();_session=None

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--probe-read-only',action='store_true')
    p.add_argument('--studio-id',required=True);p.add_argument('--expected-place',required=True)
    p.add_argument('--code',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();need(a.probe_read_only,'Only explicit two-read Root probe CLI')
    code=a.code.read_text(encoding='utf-8-sig')
    with Session(a.studio_id,a.expected_place,a.output,seconds=600)as s:
        reports=[s.run('execute_luau',dict(studio_id=a.studio_id,datamodel_type='Server',code=code),a.output/(str(i)+'_READ.json'),120,read_only=True)for i in(1,2)]
        values=[decode_text(x['reply']['result'])for x in reports]
        proof=dict(schema='DEE.R06.PersistentMCP.TwoReadProbe.R01',same_sdk_pid=reports[0]['sdk_pid']==reports[1]['sdk_pid'],
            semantic_equal=values[0]==values[1],elapsed_seconds=[x['elapsed_seconds']for x in reports],
            scope='Root-declared read-only samples; no automatic replay, no Native/model request issued by this client')
        write_new(a.output/'PROBE_RESULT.json',proof);print(json.dumps(proof,ensure_ascii=False))
