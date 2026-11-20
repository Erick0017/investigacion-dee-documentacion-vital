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
SCHEMA='DEE.C02.ENV_REPLAY.NUMERIC_LINK.R02'
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
    output=safe(output);need(not output.exists(),'New R02 preparation directory only')
    previous=ROOT/'evidencia/CONTROL_ENLACE_NUMERICO_PREPARADO_R01'
    old=read(previous/'PROTOCOLO_REPLAY_ENLACE_C02.json');old_payload=previous/'PAYLOAD_REPLAY_ENLACE_C02.json'
    need(sha(old_payload)==old['payload_sha256'],'Prior prepared payload changed')
    payload=read(old_payload)
    need(payload['provenance']['world_sha256']==WORLD_HASH and payload['world']['native_tick']==950523,'Exact same historical world required')
    for name,expected in old['required_modules_sha256'].items():
        need(hashlib.sha256((ROOT/'mundo'/name).read_text('utf8').encode('utf8')).hexdigest()==expected,
             'Replay must reuse identical validated Body/State modules: '+name)
    payload['schema']=SCHEMA
    script=ROOT/'mundo/Control_Enlace_Numerico_REPLAY_C02_R02.luau'
    failure=ROOT/'evidencia/CONTROL_ENLACE_NUMERICO_INTACT_R01/03_execute_environment_replay_once.json'
    need(failure.exists()and 'C02_EXACT_CURSOR'in failure.read_text('utf8'),'Preserve exact known R01 environmental failure')
    output.mkdir(parents=True);write(output/'PAYLOAD_REPLAY_ENLACE_C02.json',payload)
    protocol=copy.deepcopy(old);protocol.update(schema=SCHEMA,payload_sha256=sha(output/'PAYLOAD_REPLAY_ENLACE_C02.json'),
        Lua_script=str(script),Lua_script_sha256=sha(script),
        counter_rule='ENVIRONMENTAL completedCycles advances3/4 after replayed feedback. Archived Native completedCycles stays2 separately; Native tick held950523. Not a Native-continuable pair.',
        previous_preparation=str(previous),previous_protocol_sha256=sha(previous/'PROTOCOLO_REPLAY_ENLACE_C02.json'),
        previous_failure=str(failure),previous_failure_sha256=sha(failure),
        technical_correction='Only replay loop cursor: obey existing Body.beginCycle exact-cursor contract; no Body/State/Native change.')
    write(output/'PROTOCOLO_REPLAY_ENLACE_C02.json',protocol)
    return {'status':'PREPARED_R02_NOT_EXECUTED','prepared':str(output),'payload_sha256':protocol['payload_sha256'],
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
