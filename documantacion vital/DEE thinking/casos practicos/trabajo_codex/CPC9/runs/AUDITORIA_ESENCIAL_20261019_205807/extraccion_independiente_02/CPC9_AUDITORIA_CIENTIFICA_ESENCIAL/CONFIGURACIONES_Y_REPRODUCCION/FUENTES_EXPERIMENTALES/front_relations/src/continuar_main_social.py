"""Single-writer continuation of original E1, with declared external E2 ports."""
from pathlib import Path
from copy import deepcopy
import argparse,hashlib,json,os,sys,time,traceback
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from main_social_life import MainSocialSession,receiver_interfaces,schedule
from integracion.relational_pair import physical,move
from dee_thinking import _native as d
import dee_thinking
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def put(path,value):
    temp=path.with_name(path.name+'.pending.'+str(os.getpid()));temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8');os.replace(temp,path)
def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--case',required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--config',type=Path,required=True);p.add_argument('--cue-omitted',action='store_true');p.add_argument('--fork',choices=('cut','sham'));p.add_argument('--bank',default='d5');a=p.parse_args()
    if dee_thinking.__version__!='4.5.0'or sha(d.__file__)!='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'or not Path(dee_thinking.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):raise RuntimeError('Official isolated instrument required')
    a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();s=None;cfg=json.loads(a.config.read_text(encoding='utf8'));parent_hash=sha(a.parent)
    r={'schema':'CPC9.E1.late_social_continuation.v1','case_id':a.case,'preparations':0,'continuations':int(not a.fork),'diagnostic_forks':int(bool(a.fork)),
       'continuity_type':'AUDITOR_DIAGNOSTIC_FORK'if a.fork else'AUDITOR_COUNTERFACTUAL_CONTINUATION'if a.cue_omitted else'MAIN_CONTINUATION',
       'parent':{'path':str(a.parent),'sha256':parent_hash},'configuration_sha256':sha(a.config),'predictions_before_any_new_tick':cfg['predictions'],
       'MAIN_RAW_clock_edits':[],'frames':[],'snapshots':[],'route_windows':[],'status':'PREDICTIONS_WRITTEN',
       'engine':{'version':dee_thinking.__version__,'module':dee_thinking.__file__,'native_sha256':sha(d.__file__),'python':sys.executable}}
    put(a.out/'MEDICIONES.json',r)
    sources={}
    for name,module in list(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if path and Path(path).suffix=='.py'and Path(path).resolve().is_relative_to(ROOT):sources[str(Path(path).resolve())]=sha(path)
    r['source_sha256']=sources
    try:
        parent=MainSocialSession.load(a.parent);r['parent'].update(identifier=parent.identifier,physical=physical(parent.world));s=parent
        if a.fork:
            if parent.tick!=1292:raise ValueError('Messagefork requires exact1292parent')
            item=next(item for item in parent.geometry['late_E2']['banks']if item['id']==a.bank);pre=parent.observe(item['source_effect'])
            edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*item['source_effect']);edit.raw=0 if a.fork=='cut'else int(pre['raw']);edit.label='CPC9_AUDITOR_LATE_E1_MESSAGE_'+a.fork
            child=parent.world.diagnostic_fork([edit],True);s=MainSocialSession(child,parent.geometry,parent.state,parent.identifier)
            r['intervention']={'site':item['source_effect'],'pre':pre,'post':s.observe(item['source_effect']),'clock_edit':None,'parent_unchanged':r['parent']['physical']==physical(parent.world)}
        elif s.tick==1220:
            if'late_E2'in s.geometry:raise ValueError('E2 alreadyintroduced at1220')
            ports,g=receiver_interfaces(s.geometry);before=physical(s.world);prior_channels=sorted(s.world.runtime.channel_names)
            for spec in ports:s.world.declare_interface(spec)
            after=physical(s.world);s.geometry['late_E2']=g
            r['instrumental_extension']={'classification':g['introduction'],'new_interface_specs':[item[key]for item in g['banks']for key in('cue','probe','use')],
               'physical_before':before,'physical_after':after,'physical_equal':before==after,'channel_count_before':len(prior_channels),'channel_count_after':len(s.world.runtime.channel_names)}
            if before!=after:raise RuntimeError('Interface registration altered physicalstate')
            schedule(s,receiver_cue=not a.cue_omitted)
        elif s.tick!=1292:raise ValueError('Continuationparent outsidefrozen1220/1292domain')
        r['initial_physical']=physical(s.world);put(a.out/'MEDICIONES.json',r)
        def save():
            path=a.out/('T'+str(s.tick)+'.deetsnap.gz');storage=s.save(path)
            r['snapshots'].append({'path':path.name,'sha256':sha(path),'bytes':path.stat().st_size,'tick':s.tick,'storage':storage,'physical':physical(s.world)})
        save()
        ticks={1220,1277,1278,1283,1284,1286,1287,1289,1291,1292,1293,1294,1295,1296,1297,1298,1299,1344,1345,1350,1351,1353,1354,1364,1365,1370,1371}
        for tick in sorted(t for t in ticks if s.tick<t<=1371):
            s.run_until(tick);r['frames'].append({'tick':tick,'physical':physical(s.world),'view':s.view()})
            if 1291<=tick<=1299:
                r['route_windows'].append({'tick':tick,'windows':[{'id':item['id'],'nominal_route_only':True,'site':move(item['source_effect'],(0,-1,1),tick-1292),
                    'Moore27':[s.observe(move(move(item['source_effect'],(0,-1,1),tick-1292),(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]}for item in s.geometry['late_E2']['banks']]})
            if tick in(1292,1298,1371):save()
            r.update(last_complete_tick=s.tick,requests=s.receipts(),late_E2_observations=s.state['late_E2_observations'],elapsed_seconds=time.monotonic()-start,status='RUNNING');put(a.out/'MEDICIONES.json',r)
        r.update(status='MEASURED',final_physical=physical(s.world),parent_file_unchanged=sha(a.parent)==parent_hash)
    except BaseException as error:r.update(status='TECHNICAL_ERROR',error=repr(error),traceback=traceback.format_exc());raise
    finally:
        if s is not None:r.update(last_complete_tick=s.tick,requests=s.receipts(),late_E2_observations=s.state.get('late_E2_observations',[]),elapsed_seconds=time.monotonic()-start)
        r['sources_unchanged_during_execution']=all(sha(path)==digest for path,digest in sources.items());put(a.out/'MEDICIONES.json',r)
    print(json.dumps({'case':a.case,'status':r['status'],'tick':s.tick,'physical':r.get('final_physical'),'seconds':r['elapsed_seconds']}))
if __name__=='__main__':main()
