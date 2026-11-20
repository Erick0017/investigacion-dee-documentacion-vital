"""Drop-in World transport for FUTURE R06 blocks only; actor/body unchanged.

Persistent official SDK + byte-verified Zstd. Import defines classes only. Root
must first compare the frozen-byte transfer and use a fresh output directory.
"""
from pathlib import Path
import hashlib,importlib.util,json,sys,time,uuid
ROOT=Path(__file__).resolve().parents[1]
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
BASE=load(ROOT/'control/run_integrated_v3_R07_REFERENCIAS.py','_r07_reference_world_base_R07')
CLIENT=load(ROOT/'control/mcp_persistente_v3_R06.py','_r06_persistent_world_client')
COMP=load(ROOT/'control/transporte_comprimido_v3.py','_r06_compressed_world_bytes')
def compare_values(before,after):
    """Full JSON values; tolerance ONLY for the declared geometric fields."""
    ignored={'S.mode','S.reason','S.latency','close_requested','observer.segment'}
    geometry={'body_pose','cframe','size','color','transparency','linearVelocity','angularVelocity','pivotOffset','customPhysicalProperties'}
    packed={'Vector3','Color3','CFrame','UDim','UDim2','NumberRange'};diff=[]
    def visit(a,b,path='',tolerant=False):
        if path in ignored:return
        if type(a)in(int,float)and type(b)in(int,float):
            if not(abs(a-b)<=1e-5 if tolerant else a==b):diff.append({'path':path,'before':a,'after':b})
        elif isinstance(a,dict)and isinstance(b,dict):
            for key in sorted(set(a)|set(b)):
                p=key if not path else path+'.'+key
                if p in ignored:continue
                if key not in a or key not in b:diff.append({'path':p,'kind':'missing_key'});continue
                typed=key=='v'and a.get('_type')in packed and a.get('_type')==b.get('_type')
                visit(a[key],b[key],p,tolerant or key in geometry or typed)
        elif isinstance(a,list)and isinstance(b,list):
            if len(a)!=len(b):diff.append({'path':path,'kind':'array_length','before':len(a),'after':len(b)})
            else:
                for i,(x,y)in enumerate(zip(a,b)):visit(x,y,path+'['+str(i)+']',tolerant)
        elif type(a)is not type(b)or a!=b:diff.append({'path':path,'before':a,'after':b})
    visit(before,after)
    return {'equal_with_declared_geometry_tolerance':not diff,'geometry_absolute_tolerance':1e-5,
      'ignored_technical_UI_paths':sorted(ignored),'differences':diff,'Native_imports':0,'new_native_ticks':0}
def verify_restore_events(source,restored,identity):
    old=source['events'];new=restored['events']
    if new[:len(old)]!=old:raise RuntimeError('Historical World events altered during restore; no Native')
    added=new[len(old):];kinds=[row.get('kind')for row in added]
    mandatory=['MOTOR_PREPARED','R07_MOTOR_ENVIRONMENT_PREPARATION','R07_TECHNICAL_IDENTITY']
    if kinds not in (mandatory,['R07_COMMON_NAVIGATION_GEOMETRY']+mandatory):
        raise RuntimeError('Restore added an undeclared event/action; no Native')
    for row in added:
        data=row.get('data',{});kind=row['kind']
        if kind=='R07_COMMON_NAVIGATION_GEOMETRY':
            if type(data.get('oldDecorativeCollidersDisabled'))is not int or not 0<=data['oldDecorativeCollidersDisabled']<=10000:
                raise RuntimeError('Bounded declared decorative collider preparation required')
        elif kind=='MOTOR_PREPARED':
            if data.get('kind')!='HUMANOID_PATHFINDING' or data.get('semantic_destination_selected_by_motor')is not False:
                raise RuntimeError('Motor preparation cannot select a semantic destination')
            pivot=data.get('preservedPivot')
            if not isinstance(pivot,list)or len(pivot)!=12 or any(type(x)not in(int,float)for x in pivot):
                raise RuntimeError('Exact prepared motor pivot required')
            if any(abs(x-y)>1e-5 for x,y in zip(pivot,source['body_pose'])):
                raise RuntimeError('Prepared motor changed the inherited body pivot')
        elif kind=='R07_MOTOR_ENVIRONMENT_PREPARATION':
            if data.get('native_ticks_advanced')!=0 or data.get('semanticPolicy')is not False or data.get('floorAndObstaclesPrepared')is not True:
                raise RuntimeError('Only declared zero-Native motor/environment preparation allowed')
        elif kind=='R07_TECHNICAL_IDENTITY':
            if data.get('current')!=identity or data.get('Native_memory_edited')is not False or data.get('products_preserved')is not True:
                raise RuntimeError('Exact technical identity/preserved products required')
    return kinds

class CompressedWorld(BASE.LegacyWorld):
    def __init__(self,studio,output,record,*,expected_place='DEE_RBX01_R07_NATIVE.rbxlx'):
        self.studio,self.output,self.record=studio,Path(output),record;self.serial=0;self.export_serial=0
        remaining=min(43200,int(BASE.FINISH-time.time()))
        if remaining<=0:raise RuntimeError('R06 transport deadline expired; no new SDK session')
        self.session=CLIENT.Session(studio,expected_place,self.output/'MCP_PERSISTENTE',seconds=remaining).__enter__()
        self.record('MCP_PERSISTENT_CONNECTED',source_sha256=hashlib.sha256((ROOT/'control/mcp_persistente_v3_R06.py').read_bytes()).hexdigest(),
            compression_source_sha256=hashlib.sha256((ROOT/'control/transporte_comprimido_v3.py').read_bytes()).hexdigest(),
            sdk_pid=self.session.client.process.pid)
    def mcp(self,code,label,seconds=180):
        self.serial+=1
        self.record('MCP_INTENT',label=label,code_sha256=hashlib.sha256(code.encode()).hexdigest(),persistent=True)
        # Preserve Lua arrays through MCP. Its structured table serializer uses
        # numeric-key objects; JSONEncode is the actual public packet ABI.
        wire='local r06Value=(function()\n'+code+'\nend)();return game:GetService("HttpService"):JSONEncode(r06Value)'
        report=self.session.run('execute_luau',{'studio_id':self.studio,'datamodel_type':'Server','code':wire},
            self.output/f'MCP_{self.serial:04d}_{label}.json',seconds)
        result=BASE.decode(report);self.record('MCP_COMPLETED',label=label,result=result,persistent=True);return result
    def initialize(self,state,identity,source_sha):
        # Same serialization as the original runner's old hex input. The
        # original document SHA remains the externally bound state anchor.
        raw=json.dumps(state,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf8')
        transfer='IMPORT_'+uuid.uuid4().hex[:16]
        meta=COMP.compressed_import(self.session,self.studio,raw,transfer,self.output/'IMPORT_ZSTD')
        expected={k:state[k]for k in('world_id','scenario_sha256','native_life_id','native_tick','checkpoint_id')}
        expected.update(checkpoint_sha256=source_sha,owner_closed=True,bridge_quiescent=True)
        # initialize's full restored.controller includes the complete ancestral
        # command history and may exceed the SDK text envelope. Return only its
        # technical ACK; the following compressed capture still verifies ALL
        # World contents, not a summary of that state.
        apply_code=COMP.import_apply_code(meta,expected,identity)
        compact='local r07Ack=(function()\n'+apply_code+'\nend)();return {restored={checkpoint_id=r07Ack.restored.checkpoint_id},S=r07Ack.S,phase=r07Ack.phase,original_events=r07Ack.original_events,current_events=r07Ack.current_events,new_Native_ticks=r07Ack.new_Native_ticks}'
        result=self.mcp(compact,'restore_apply_once_zstd_compact_ack')
        self.record('WORLD_COMPRESSED_IMPORT_VERIFIED',meta=meta,original_document_sha256=source_sha,
            serialization='Same exact compact UTF8JSON as original World.initialize; Native ticks0 during transfer/apply')
        # Before opening the Native owner, verify the applied complete World.
        # Only new audit-document identity/observer segment may differ.
        restored=self.checkpoint('R07_VERIFY_RESTORE_'+uuid.uuid4().hex[:12],self.output/'WORLD_RESTORED_BEFORE_NATIVE.json')
        before=json.loads(json.dumps(state));after=json.loads(json.dumps(restored))
        appended_preparation=verify_restore_events(state,restored,identity)
        before['events']=[];after['events']=[]
        after['checkpoint_id']=before['checkpoint_id']
        initial_environment_clone=(state['native_life_id']!=identity['life'] or state['world_id']!=restored['world_id'])
        if initial_environment_clone:
            # Every inherited S field is preserved except transport/UI fields.
            # New motor anatomy and additional motor bookkeeping are explicit
            # preparation, not Native learning; original raw source is retained.
            old_s=before['S'];new_s=after['S']
            inherited={key:new_s.get(key)for key in old_s}
            for key in ('lifeId','sessionId'):inherited[key]=old_s.get(key)
            before={'S':old_s};after={'S':inherited}
        comparison=compare_values(before,after)
        comparison.update(excluded_auditor_event='exact declared motor preparation and one identity event; old prefix checked byte-meaning exactly', appended_preparation_events=appended_preparation,
          checkpoint_document_identity_excluded=True,Native_owner_not_opened_yet=True,
          prepared_motor_anatomy_change=initial_environment_clone, comparison_mode='PARENT_CONTENTS_AND_COUNTERS_WITH_DECLARED_NEW_MOTOR_ANATOMY' if initial_environment_clone else 'SAME_PAIR_FULL_STATE_REOPEN',
          Native_memory_transferred_to_reference=False)
        with(self.output/'WORLD_RESTORE_COMPARISON.json').open('x',encoding='utf8')as f:json.dump(comparison,f,ensure_ascii=False,indent=2)
        if not comparison['equal_with_declared_geometry_tolerance']:
            raise RuntimeError('Applied World differs outside declared technical fields/geometry tolerance; no Native opened')
        self.record('WORLD_RESTORE_SEMANTICS_VERIFIED',comparison=comparison)
        return result
    def checkpoint(self,checkpoint_id,path):
        # Called by the original loop ONLY AFTER configured_owner has exited.
        source='local h=game:GetService("HttpService");return h:JSONEncode(require(game:GetService("ServerScriptService").RBX01Server.WorldAPI_R07).checkpoint('+json.dumps(checkpoint_id)+'))'
        self.export_serial+=1
        result=COMP.compressed_export(self.session,self.studio,source,'EXPORT_'+uuid.uuid4().hex[:16],self.output/('EXPORT_ZSTD_'+str(self.export_serial).zfill(2)))
        raw=Path(result['path']).read_bytes();path=Path(path)
        if path.exists():raise FileExistsError('Original World output preserved')
        with path.open('xb')as f:f.write(raw)
        state=json.loads(raw)
        self.record('WORLD_CHECKPOINT_SAVED',path=str(path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),
            boundary=state['boundary'],compressed_transport=result['meta'],
            owner_closed_required_by_call_order=True,new_Native_ticks=0)
        return state
    def close(self):self.session.close()
