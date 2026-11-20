"""Exact source4.0 versus bundled experimental4.5 regulation, after trajectories."""
from __future__ import annotations
import argparse,importlib,json,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from neutral_differential import native,put,sha,exact_array,operative,receipt,observation,hashes
ROOT=Path(__file__).resolve().parents[2];EVIDENCE=ROOT/'evidence/CPC5_regulation';CONFIG=Path(__file__).with_name('regulation_port_config.json')

def old_prepare(case,d):
    sys.path.insert(0,str(EVIDENCE));sys.path.insert(0,str(EVIDENCE/'src'))
    network=importlib.import_module('network');ref=importlib.import_module('referencias.cpc4_red.regulated_session');g=ref.describe(tuple(case['translation']));ports=ref.interfaces(d,g)
    mode=case['mode'];direction=(0,0,-1) if mode=='opposite' else (0,0,1);h=network.moved(g['regulation']['meeting'],(0,0,1),-(292-3),g['N']);extra=[]
    for label,dr in (('cue',(-1,0,0)),('report',(1,0,direction[2]))):
        ports.append(network.interface('native_regulator.'+label,network.moved(h,dr,-3,g['N']),dr));extra.append({'channel':'native_regulator.'+label,'load':0,'tick':int(label=='cue' and mode=='unpaired'),'role':'Actual neutral directional-regulator experience'})
    recipe=d.OrganizationRecipe.research(g['N'],[],0);recipe.interfaces=ports;recipe.execution=d.TickOptions(d.Backend.LAZY,1);world=d.OrganizationalWorld.create(recipe);calls=[]
    external={'id':case['id'],'roles':True,'A_history':case['a_history'],'B_history':1,'C_history':case['c_history'],'D_history':1,'neutralizer':'none'}
    for row in ref.protocol(external)+extra:
        rr=world.submit(row['channel'],row['load'],row['tick']);calls.append({**row,'receipt_id':int(rr.id),'call_tick':0,'modality':'EXPERIENCE_PROTOCOL'})
    g['learned_hub']=h
    sources={name:sha(EVIDENCE/name) for name in ('src/network.py','referencias/cpc4_red/recipe_v3.py','referencias/cpc4_red/dual_session.py','referencias/cpc4_red/regulated_session.py')}
    return world,g,calls,sources

def run(case,out,version,config):
    out.mkdir(parents=True,exist_ok=False);started=time.monotonic();d,engine=native(version);session=None
    if version=='4.0.0':w,g,journal,sources=old_prepare(case,d)
    else:
        from dee_thinking.experimental_regulation import CPC5RegulationSession
        session=CPC5RegulationSession.create(mode=case['mode'],translation=case['translation'],a_history=case['a_history'],c_history=case['c_history']);w=session.world;g=session.geometry;journal=session.journal;sources={}
        if any(name=='network' or name.startswith('referencias.') for name in sys.modules):raise AssertionError('Candidate imported historical apparatus')
    r=w.runtime;frames=[];captures={name:{} for name in g['banks']};pending=[];restored=None;before_restore=None
    put(out/'CONFIG.json',{'case':case,'engine':engine,'configuration_sha256':sha(config),'source_sha256':sha(__file__),'constructor_sources':sources,'scope':'Source preparation functions only; original runners/terminal measurements never execute or supply responses.'})
    cfg=json.loads(config.read_text(encoding='utf8'))
    for tick in cfg['frontiers']:
        w.run_until(tick);points=dict(g['centers']);points['regulation_meeting']=g['regulation']['meeting'];dr=(0,0,-1) if case['mode']=='opposite' else (0,0,1)
        points['nominal_regulator_segment']=[(g['learned_hub'][i]+dr[i]*max(0,tick-3))%67 for i in range(3)]
        for name,b in g['banks'].items():
            points[name+'.resource']=b['resource_receiver'];points[name+'.function']=b['function_receiver']
            if tick==b['resource_read']:captures[name]['resource']=observation(r,b['resource_receiver'],d)
            if tick==b['function_read']:captures[name]['function']=observation(r,b['function_receiver'],d)
        frame={'tick':str(tick),'forms':{name:observation(r,site,d) for name,site in points.items()}}
        if tick in cfg['full_states']:frame.update({'raw':exact_array(r.raw_copy(),out/f'T{tick}.raw.u64.gz'),'clock':exact_array(r.clock_copy(),out/f'T{tick}.clock.u64.gz'),'operative':operative(r)})
        frames.append(frame)
        if tick==292:
            path=out/'PENDING_T292.deetsnap';w.save_snapshot(str(path));pending.append({'path':path.name,'tick':'292','sha256':sha(path)})
        if tick==350:
            physical=hashes(r);before_restore=operative(r)
            if session is not None:
                child=session.fork();proof=child.save_snapshot(out/'FORK_T350.deetsnap.gz');restored=CPC5RegulationSession.load_snapshot(out/'FORK_T350.deetsnap.gz')
                if restored.journal!=journal:raise AssertionError('Public session lost actual request journal')
                restore_world=restored.world
            else:
                child=w.fork();child.save_snapshot(str(out/'FORK_T350.deetsnap'));restore_world=d.OrganizationalWorld.load_snapshot(str(out/'FORK_T350.deetsnap'));restored=restore_world
            if hashes(restore_world.runtime)!=physical or hashes(r)!=physical or operative(r)!=before_restore:raise AssertionError('Restore/fork changed physical MAIN')
        put(out/'PROGRESS.json',{'case_id':case['id'],'last_tick':str(tick),'frames':frames,'captures':captures})
    final_op=operative(r);restored_world=restored.world if session is not None else restored
    (restored.run_until(437) if session is not None else restored_world.run_until(437))
    if hashes(restored_world.runtime)!=hashes(r):raise AssertionError('Public restored pending continuation differs')
    if operative(r)!=final_op:raise AssertionError('Restored branch mutated MAIN operations')
    calls=[{'id':str(item['receipt_id']),'port':item['channel'],'payload':item['load'],'at':str(item['tick']),'call_tick':'0','kind':'experience','final_receipt':receipt(r.receipt(item['receipt_id']))} for item in journal]
    # Utility is an auditor calculation AFTER all participant trajectories.
    profiles={}
    for name,pair in captures.items():
        b=g['banks'][name];rr=pair['resource'];ff=pair['function'];rv=rr['state']>0 and rr['semantic']!=5 and rr['s_reg']==3 and rr['direction']==list(b['resource_direction']);fv=ff['state']>0 and ff['semantic']!=5 and ff['s_reg']==7 and ff['direction']==list(b['supply_direction']);profiles[name]={'resource':rv,'function':fv,'external_utility':int(rv)+2*int(fv)}
    result={'schema':'DEE45.CPC_native_port.measurements.v1','case_id':case['id'],'kind':'experimental_acquired_direction_regulation','library':version,'status':'PASS','engine':engine,'constructor_sources':sources,'config_sha256':sha(config),'source_sha256':sha(__file__),'frames':frames,'readouts':[],'calls':calls,'final_operative':final_op,'checkpoints':pending,'captures':captures,'profiles':profiles,'technical':{'fork_MAIN_unchanged':True,'public_save_load_pending_future_RAW_clocks_tick_equal':True,'candidate_historical_lab_imports':[] if session is not None else None},'preparations':1,'elapsed_seconds':time.monotonic()-started,'scope':'Finite acquired zero-load direction and native occupied-material consequence; no reinforcement-selected attention, no integrated U0 membership, no new scientific replication.'}
    put(out/'RESULT.json',result);print(json.dumps({'id':case['id'],'library':version,'profiles':profiles,'seconds':result['elapsed_seconds']}),flush=True)

def suite(a):
    config=json.loads(a.config.read_text(encoding='utf8'));a.out.mkdir(parents=True,exist_ok=True);rows=[]
    for case in config['cases']:
        target=a.out/case['id'];result=target/'RESULT.json'
        if result.exists():value=json.loads(result.read_text(encoding='utf8'))
        else:
            argv=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'case','--config',str(a.config.resolve()),'--case-id',case['id'],'--expected-version',a.expected_version,'--out',str(target.resolve())]
            try:
                process=subprocess.run(argv,capture_output=True,text=True,timeout=180);value={'status':'PASS' if process.returncode==0 and result.exists() else 'FAIL','returncode':process.returncode,'stdout':process.stdout,'stderr':process.stderr}
            except subprocess.TimeoutExpired as e:value={'status':'TIMEOUT','error':str(e)}
            put(a.out/(case['id']+'.PROCESS.json'),value)
        rows.append({'case_id':case['id'],'status':value['status'],'result':case['id']+'/RESULT.json'});put(a.out/'INDEX.json',{'schema':'DEE45.experimental_regulation_port.index.v1','library':a.expected_version,'config_sha256':sha(a.config),'cases':rows})
    if any(row['status']!='PASS' for row in rows):raise SystemExit(1)
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='mode',required=True)
    for mode in ('suite','case'):
        a=sub.add_parser(mode);a.add_argument('--config',type=Path,default=CONFIG);a.add_argument('--out',type=Path,required=True);a.add_argument('--expected-version',required=True)
        if mode=='case':a.add_argument('--case-id',required=True)
    a=p.parse_args()
    if a.mode=='suite':suite(a)
    else:
        config=json.loads(a.config.read_text(encoding='utf8'));run(next(x for x in config['cases'] if x['id']==a.case_id),a.out,a.expected_version,a.config)
if __name__=='__main__':main()
