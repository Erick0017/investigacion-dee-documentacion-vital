"""Prepare/Root-run a narrow ENVIRONMENTAL replay, never a Native execution.

Uses exact saved DEV2 world, archived Native B5 and four recorded actions. Two
fresh isolated Studio worlds compare product retained vs numeric product absent.
No arithmetic, target, route search, owner, DEE import or Native feedback exists.
"""
from pathlib import Path
import argparse,copy,datetime,hashlib,importlib.util,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
WORLD_HASH='92abff829cf4b6d16724f3b01859c50c4b7a41d495117b2ebd3331997cc150a7'
OPERATION='cb40497d81d34483b120e97e2209c7ee'
SCHEMA='DEE.C02.ENV_REPLAY.NUMERIC_LINK.R01'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
    with Path(p).open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def safe(p):
    p=Path(p).absolute()
    for part in(p,*p.parents):need(not part.is_symlink()and not(part.exists()and getattr(part.lstat(),'st_file_attributes',0)&1024),'No links/reparse')
    p=p.resolve();need(p.is_relative_to(ROOT),'C02 subtree only');return p
def load(relative,name):
    s=importlib.util.spec_from_file_location(name,ROOT/relative);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def prepare(output):
    output=safe(output);need(not output.exists(),'New preparation directory only')
    worldpath=ROOT/'evidencia/DEV_SELLADO_R02/PAREJA_C02/WORLD_CHECKPOINT.json'
    finalpath=ROOT/'evidencia/DEV_REAPERTURA_R04/WORLD_FINAL.json'
    sealpath=ROOT/'evidencia/DEV_SELLADO_R02/SELLADO_VINCULO_C02.json'
    lifefile=ROOT/'native/DEV/CONTEXTO_EJECUCION.json';life=read(lifefile)['life']
    primary=ROOT/'native/DEV/sistema/estado/servicios_locales'/life/'RBX02_NATIVE_C02/functions'/(OPERATION+'.json')
    sources={str(p):sha(p)for p in(worldpath,finalpath,sealpath,primary)}
    need(sha(worldpath)==WORLD_HASH,'Exact verified DEV2 world required')
    w,f,seal,native=map(read,(worldpath,finalpath,sealpath,primary))
    need(w['native_tick']==950523 and w['S']['station']==2 and w['S']['cycle']==w['S']['completedCycles']==2 and
         w['S']['numberAPresent']is True and w['S']['numberA']==4 and w['S']['codeBPresent']is False,'Exact measured A4 prefix required')
    event=next(e for e in f['events']if e['kind']=='FUNCTION_APPLIED'and e['data']['request'].get('slot')=='B')
    tool=copy.deepcopy(event['data']['output'])
    need(tool['numeric_result']==native['native_function']['numeric_result']==5 and tool['inputs']==[4,1]and
         tool['kind']=='CALCULATE'and tool['slot']=='B'and tool['form']=='nara','Public recorded B result must match actual Native primary')
    recorded=[]
    for seq in(5,6,7,8):
        e=next(e for e in f['events']if e['kind']=='ACTION_EXECUTED'and e['seq']==seq);a=e['data']['action']
        need(a['name']==('ASK_STATION'if seq%2 else'EXIT_0'),'Only exact four recorded actions')
        recorded.append({'name':a['name'],'null':a['null'],'actionId':'ENV_REPLAY_'+a['actionId'],
                         'sourceActionId':a['actionId'],'sourceNativeTick':a['nativeTick'],
                         'sourceNativeTicks':a['nativeTicks'],'NativeExecuted':False})
    expected={k:w[k]for k in('world_id','scenario_sha256','native_life_id','native_tick','checkpoint_id')}
    expected.update(checkpoint_sha256=seal['bound_checkpoint_sha256'],owner_closed=True,bridge_quiescent=True)
    provenance={'world_path':str(worldpath),'world_sha256':sha(worldpath),'world_final_path':str(finalpath),'world_final_sha256':sha(finalpath),
                'primary_path':str(primary),'primary_sha256':sha(primary),'operation_id':OPERATION,
                'primary_result_locator':'/native_function/numeric_result','world_tool_locator':'events[kind=FUNCTION_APPLIED,data.request.slot=B].data.output',
                'Native_after_tick_recorded':native['after_tick'],'Native_before_tick_recorded':native['before_tick']}
    payload={'schema':SCHEMA,'world':w,'restore_expected':expected,'toolResult':tool,'actions':recorded,'provenance':provenance}
    need(sources=={p:sha(Path(p))for p in sources},'Input evidence changed concurrently')
    output.mkdir(parents=True);write(output/'PAYLOAD_REPLAY_ENLACE_C02.json',payload)
    script=ROOT/'mundo/Control_Enlace_Numerico_REPLAY_C02.luau'
    protocol={'schema':SCHEMA,'scope':'ENVIRONMENTAL_LINK_NECESSITY_ONLY_NOT_LEARNING_PLAN_OR_NATIVE_REPRODUCTION',
              'frozen_before_run':True,'source_files_sha256':sources,'payload_sha256':sha(output/'PAYLOAD_REPLAY_ENLACE_C02.json'),
              'Lua_script':str(script),'Lua_script_sha256':sha(script),
              'required_modules_sha256':{name:hashlib.sha256((ROOT/'mundo'/name).read_text('utf8').encode('utf8')).hexdigest()for name in('Body_C02.luau','EstadoPareja_C02.luau')},
              'module_source_hash_rule':'Exact UTF8 source text with newline normalization toLF, as the XML builder reads it; raw local file hashes retained separately.',
              'required_module_files_sha256':{name:sha(ROOT/'mundo'/name)for name in('Body_C02.luau','EstadoPareja_C02.luau')},
              'arms':['INTACT','CUT_B'],'common_prefix_native_tick':950523,'actual_archived_product':5,
              'intervention':'Only CUT_B removes formed numeric_result at B application, not a desired answer or a Native memory edit.',
              'common_replay':'Recorded ASK_STATION/EXIT_0 for cycles3 and4, same clocks/query/toll costs; one prepared tool application0.25s.',
              'outcomes_fixed_before_run':['resourceCount delta','codeRejected delta','inventoryKey/resource','permissionStock delta','worldTime delta','formed actualCode versus NULL'],
              'predicted_mechanism':'An existing environmental lock consumes actual B; no external desired code is passed.',
              'admissible_conclusion':'A different gate consequence after product ablation supports downstream use/necessity of that recorded product in this world.',
              'excluded_claims':['new DEE decision','Native replay','new memory acquisition','learned plan','general autonomy'],
              'fresh_world_requirements':'Exact DEV4 scene/scenario; Controller disabled BEFORE Play; no mailbox/controller Bindables; never MAIN.',
              'counter_rule':'S.nativeTick held950523; S.completedCycles held2. World cycle/time advances only in replay; result is NOT a Native-continuable paired checkpoint.'}
    write(output/'PROTOCOLO_REPLAY_ENLACE_C02.json',protocol)
    return {'status':'PREPARED_NOT_EXECUTED','prepared':str(output),'payload_sha256':protocol['payload_sha256'],
            'Native_imports':0,'Native_ticks':0,'MCP_calls':0}
def run(args):
    need(args.root_run,'Actual MCP replay is Root-only')
    prepared,output=map(safe,(args.prepared,args.output));need(not output.exists(),'Fresh result directory only')
    protocol=read(prepared/'PROTOCOLO_REPLAY_ENLACE_C02.json');payloadpath=prepared/'PAYLOAD_REPLAY_ENLACE_C02.json'
    need(sha(payloadpath)==protocol['payload_sha256'],'Prepared input changed')
    script=safe(protocol['Lua_script']);need(sha(script)==protocol['Lua_script_sha256'],'Replay script changed after freeze')
    payload=read(payloadpath);world=payload['world'];need(world['world_id']=='RBX01_R05_C02_DEV4','DEV only')
    output.mkdir(parents=True);u=load('control/orquestar_C02.py','_C02_environment_replay_safe_utils')
    operator=load('control/mcp_operator_C02.py','_C02_environment_replay_operator')
    def mcp(tool,fields,label,seconds=120):
        fields=dict(fields)
        if tool!='list_roblox_studios':fields['studio_id']=args.studio_id
        extra={'wait_file':'DEE_RBX01_C02_DEV4.rbxlx'}if tool=='list_roblox_studios'else{}
        return u.decode_tool(operator.run(tool,fields,output/(label+'.json'),seconds,**extra))
    inventory=mcp('list_roblox_studios',{},'00_inventory');target=next((x for x in inventory.get('studios',[])if x.get('id')==args.studio_id),None)
    need(target and target.get('file')=='DEE_RBX01_C02_DEV4.rbxlx','Exact isolated DEV Studio only')
    guard='assert(game:GetService("RunService"):IsStudio()and game:GetService("RunService"):IsRunning(),"FRESH_PLAY_REQUIRED");local p=game:GetService("ServerScriptService").RBX01Server;assert(p.Controller.Disabled,"CONTROLLER_MUST_BE_DISABLED");local s=game:GetService("ServerStorage");assert(not s:FindFirstChild("RBX01Mailbox_C02")and not s:FindFirstChild("RBX01Checkpoint_C02")and not s:FindFirstChild("C02NumericReplayPayload"),"FRESH_NO_CONTROLLER_OR_BRIDGE");local c=require(p.Config);assert(c.WorldId=="RBX01_R05_C02_DEV4"and c.ScenarioFingerprint=="'+world['scenario_sha256']+'","SAME_DEV_SCENARIO_REQUIRED");assert(game:GetService("StudioService"):GetUserId()==11981994305,"OWNER");return{verified=true,BodySource=p.Body_C02.Source,StateSource=p.EstadoPareja_C02.Source}'
    sources=mcp('execute_luau',{'datamodel_type':'Server','code':guard},'01_fresh_no_bridge_guard')
    for key,name in(('BodySource','Body_C02.luau'),('StateSource','EstadoPareja_C02.luau')):
        need(hashlib.sha256(sources[key].replace('\r\n','\n').encode('utf8')).hexdigest()==protocol['required_modules_sha256'][name],
             'Actual replay module differs from prepared source: '+name)
    raw=payloadpath.read_bytes();chunks=[raw[i:i+16000]for i in range(0,len(raw),16000)]
    setup='local s=game:GetService("ServerStorage");assert(not s:FindFirstChild("C02NumericReplayPayload"),"PAYLOAD_ALREADY_EXISTS");local f=Instance.new("Folder");f.Name="C02NumericReplayPayload";f:SetAttribute("Protocol","'+SCHEMA+'");f:SetAttribute("Condition","'+args.condition+'");f:SetAttribute("Count",'+str(len(chunks))+');f:SetAttribute("Complete",false);f.Parent=s;return{prepared=true}'
    mcp('execute_luau',{'datamodel_type':'Server','code':setup},'02_payload_folder_once')
    for index,chunk in enumerate(chunks,1):
        text=chunk.hex();code='local f=game:GetService("ServerStorage").C02NumericReplayPayload;local name=string.format("chunk_%05d",'+str(index)+');assert(not f:FindFirstChild(name),"NO_CHUNK_RETRY");local v=Instance.new("StringValue");v.Name=name;v.Value="'+text+'";v.Parent=f;return{index='+str(index)+',hex=v.Value}'
        reply=mcp('execute_luau',{'datamodel_type':'Server','code':code},'02_chunk_%05d'%index);need(reply.get('hex')==text,'Exact payload bytes not admitted; preserve without execution')
    mcp('execute_luau',{'datamodel_type':'Server','code':'game:GetService("ServerStorage").C02NumericReplayPayload:SetAttribute("Complete",true);return{complete=true}'},'02_payload_complete')
    write(output/'INTENCION_UNICA_REPLAY.json',{'condition':args.condition,'scope':'ENVIRONMENT_ONLY','Native_ticks':0,'single_attempt':True,'replay_allowed_after_unknown_result':False})
    result=mcp('execute_luau',{'datamodel_type':'Server','code':script.read_text('utf8')},'03_execute_environment_replay_once',180)
    need(result.get('NativeExecuted')is False and result.get('NativeTicksExecuted')==0,'Replay must not claim Native execution')
    total,count=result['bytes'],result['count'];pieces=[]
    for index in range(1,count+1):
        code='local f=game:GetService("ServerStorage").C02NumericReplayResult;assert(f:GetAttribute("Complete"));return{index='+str(index)+',hex=f[string.format("chunk_%05d",'+str(index)+')].Value,total=f:GetAttribute("TotalBytes")}'
        part=mcp('execute_luau',{'datamodel_type':'Server','code':code},'04_result_%05d'%index)
        need(part['index']==index and part['total']==total,'Replay result chunk mismatch');pieces.append(bytes.fromhex(part['hex']))
    raw=b''.join(pieces);need(len(raw)==total,'Incomplete replay result');data=json.loads(raw.decode('utf8'))
    path=output/'RESULTADO_AMBIENTAL_REPLAY_C02.json'
    with path.open('xb')as f:f.write(raw)
    summary={'scope':'ACTUAL_STUDIO_ENVIRONMENTAL_REPLAY_NO_NATIVE','condition':args.condition,'actual_result':result,
             'result_file':str(path),'result_sha256':sha(path),'Native_ticks':0,'Native_imports':0,
             'host_replayed_all_actions':True,'paired_checkpoint_continuable':False,'Play_preserved':True}
    write(output/'RESUMEN_REPLAY_C02.json',summary);return summary
def parser():
    p=argparse.ArgumentParser(description=__doc__);mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare',action='store_true');mode.add_argument('--run',action='store_true')
    p.add_argument('--root-run',action='store_true');p.add_argument('--output',type=Path,required=True)
    p.add_argument('--prepared',type=Path);p.add_argument('--studio-id');p.add_argument('--condition',choices=('INTACT','CUT_B'))
    return p
if __name__=='__main__':
    a=parser().parse_args()
    if a.prepare:result=prepare(a.output)
    else:
        need(a.prepared and a.studio_id and a.condition,'Explicit prepared source, Studio ID and condition required');result=run(a)
    print(json.dumps(result,ensure_ascii=False,indent=2))
