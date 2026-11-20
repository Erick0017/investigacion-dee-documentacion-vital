"""Root-only recovery of a KNOWN failed passive checkpoint export (R02).

No owner/Native process or material action is opened. An already-closed Native
root and quiescent suspended bridge are required. Creates a new private export
Folder with bounded chunks, preserves the failed R01 report and the actual world.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,sys,uuid
ROOT=Path(__file__).resolve().parents[1]
def load(relative,name):
    s=importlib.util.spec_from_file_location(name,ROOT/relative);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
u=load('control/orquestar_C02.py','_C02_recovery_safe_utilities')
def run(args):
    u.need(args.root_run,'Root-only recovery must be explicit')
    native,proof,failed,config_path,output=map(u.safe,(args.native_root,args.close_proof,args.failed_report,args.config,args.output))
    u.need(not output.exists()and output.is_relative_to(ROOT/'evidencia'),'Fresh evidence output only')
    old=u.read(failed);text=json.dumps(old.get('reply',{}),ensure_ascii=False)
    u.need(old.get('status')=='TOOL_ERROR'and '200000'in text,'Only KNOWN StringValue200000 export failure, not an unknown material request')
    persistence=load('control/persistencia_C02.py','_C02_recovery_closed_codec')
    context=u.read(native/'CONTEXTO_EJECUCION.json');life=context['life']
    card=persistence.closed_native_root(native,life);persistence.check_close(u.read(proof),life)
    cfg=u.read(config_path);database=u.safe(ROOT/'configuracion_privada'/cfg['databaseFile'])
    state=u.bridge_read(database);session=state['session']if state else None
    u.need(session and session['status']=='SUSPENDED_BOUNDARY'and session['phase']=='READY_QUERY'and
           state['pending']==state['uncertain']==state['unacknowledged_actions']==state['unacknowledged_tools']==0,
           'Only closed quiescent suspended bridge may be exported')
    u.need(session['mode']=='LIVE_NATIVE'and args.world_id==cfg['worldId']and args.world_id in u.SCENES and
           args.expected_place==u.SCENES[args.world_id],'Exact Native scene/config identity')
    source_files=[native/'sistema/estado/vidas'/life/'VIDA.json',native/'sistema'/card['snapshot'],database,proof,failed]
    before={str(f):u.sha(f)for f in source_files}
    output.mkdir(parents=True)
    operator=load('control/mcp_operator_C02.py','_C02_recovery_operator')
    def mcp(tool,arguments,label,seconds=90):
        fields=dict(arguments)
        if tool!='list_roblox_studios':fields['studio_id']=args.studio_id
        extra={'wait_file':args.expected_place}if tool=='list_roblox_studios'else{}
        return u.decode_tool(operator.run(tool,fields,output/(label+'.json'),seconds,**extra))
    summary={'schema':'DEE.RBX01.C02.known_passive_export_recovery.R02','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'life_id':life,'Native_ticks':0,'Native_imports':0,'owner_opened':False,'actions_submitted':0,
             'failed_export_preserved':str(failed),'failed_export_sha256':u.sha(failed),'capture_attempts':1}
    try:
        inventory=mcp('list_roblox_studios',{},'00_inventory')
        target=next((r for r in inventory.get('studios',[])if r.get('id')==args.studio_id),None)
        u.need(target and target.get('file')==args.expected_place,'Exact existing Studio world required')
        # A separate passive shape/account guard; no scene recreation or start.
        code='assert(game:GetService("RunService"):IsStudio()and game:GetService("RunService"):IsRunning(),"PLAY_REQUIRED");local p=game:GetService("ServerScriptService").RBX01Server;local c=require(p.Config);assert(c.WorldId=="'+args.world_id+'"and c.OwnerUserId==11981994305,"WORLD_IDENTITY");assert(game:GetService("StudioService"):GetUserId()==11981994305,"ACCOUNT_IDENTITY");return {verified=true,worldId=c.WorldId,NativeStarted=false}'
        guard=mcp('execute_luau',{'datamodel_type':'Server','code':code},'01_passive_guard')
        u.need(guard.get('verified')is True,'Passive existing-world guard failed')
        checkpoint='C02R02_'+uuid.uuid4().hex
        capture_context={'checkpoint_id':checkpoint,'native_life_id':life,'native_tick':card['physical']['tick'],
                         'bridge':{'session_id':session['id'],'server_id':session['server_id'],'phase':session['phase'],
                                   'pending_count':0,'uncertain_count':0,'native_ticks_in_session':session['ticks']}}
        transport=load('control/transporte_checkpoint_C02_R02.py','_C02_recovery_transport_R02')
        world,path,total=transport.capture_world(mcp,capture_context,'recovery_'+uuid.uuid4().hex,
                                                output/'WORLD_CHECKPOINT.json',persistence.validate_world)
        u.need(world['native_tick']==card['physical']['tick']and world['boundary']['completed_opportunities']==state['boundary']['completed_cycles']and
               world['boundary']['next_opportunity']==state['boundary']['next_opportunity'],'Recovered world/closed Native/bridge boundary mismatch')
        u.need(before=={str(f):u.sha(f)for f in source_files},'Closed scientific sources changed during passive export')
        summary.update(status='RECOVERED_PASSIVE_WORLD_NATIVE_NOT_REOPENED',checkpoint_id=checkpoint,
                       world_file=str(path),world_sha256=u.sha(path),world_bytes=total,
                       native_tick=card['physical']['tick'],next_opportunity=world['boundary']['next_opportunity'],
                       native_snapshot_sha256=card['snapshot_sha256'],closed_sources_unchanged=True,
                       source_hashes=before,Play_preserved=True,stop_play_requested=False)
        u.write(output/'CHECKPOINT_LOCATOR.json',summary)
    except BaseException as error:
        summary.update(status='PASSIVE_EXPORT_FAILED_PRESERVED',error_type=type(error).__name__,error=str(error),
                       no_automatic_retry=True,Play_preserved=True);raise
    finally:u.write(output/'RESULTADO_RECUPERACION_R02.json',summary)
    return summary
def parser():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root-run',action='store_true',required=True)
    for n in('native-root','close-proof','failed-report','config','output'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--studio-id',required=True);p.add_argument('--world-id',choices=tuple(u.SCENES),required=True)
    p.add_argument('--expected-place',choices=tuple(u.SCENES.values()),required=True);return p
if __name__=='__main__':print(json.dumps(run(parser().parse_args()),ensure_ascii=False,indent=2))
