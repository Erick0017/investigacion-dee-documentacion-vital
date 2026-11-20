"""Finite environmental assays on exact forks of existing E1. No host policy."""
from pathlib import Path
from collections import Counter,deque
import argparse,json,sys,random,time,hashlib
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import Store
from app.native_tools import physical,observe,moore27,atomic_json,digest_file,exact_receipt
from app.process_control import protect_current,current_resources
from dee_thinking.persistence import encode_metadata,decode_metadata
from capacidades import puente_adquirible as bridge
LAB=Path(__file__).resolve().parent
EV=ROOT/'evidencia/campanas/HABITAT_CAUSAL_Y_ESTRES_E1_01'
KEY='DEE.Cognitive.System.1.1.habitat01.v1'

def check_budget():
    budget=json.loads((LAB/'PRESUPUESTO_Y_DISENO_INICIAL.json').read_text(encoding='utf8'))
    if time.monotonic()>budget['monotonic_deadline_seconds']:raise TimeoutError('Fixed campaign budget exhausted')

def emit(a,port,payload,tick,probe=False,origin='ENVIRONMENT_FIXED_CODEC'):
    return a.input(port,int(payload),int(tick),'probe'if probe else'submit',origin)

def qround(tick):
    k=max(0,(tick-65)//67+1)
    return k,65+67*k,70+67*k

def decode_action(read):
    # Fixed actuator codec, not a comparison of observation, target or reward.
    if read['state']!=1 or read['semantic']!=1:return {'status':'NO_QUALIFIED_OUTPUT','command':0}
    vector=tuple(read['direction'])
    if vector==(1,0,0):return {'status':'NATIVE_POSITIVE_X','command':2}
    if vector==(-1,0,0):return {'status':'NATIVE_NEGATIVE_X','command':-2}
    if vector==(0,0,0):return {'status':'NATIVE_ACTIVE_NEUTRAL','command':0}
    return {'status':'CONFLICT_OUTSIDE_FIXED_CODEC','command':0}

def inherited_panel(a,*,social=True,quantity=82,old=True):
    start=physical(a.world,occupation=True);requests=[];frames=[]
    if social:
        at=45+67*((a.tick-45)//67+1)
        g=bridge.geometry(a.world);axis=-1 # chosen before this first diagnostic, not from output
        for f in g['forms']:
            for b in f['branches']:
                name='DCS11.mobile.'+f['id']+'.'+b['id']+'.readminus'
                requests.append(emit(a,name,7,at-3,True,'MATERIAL_DIAGNOSTIC_SOCIAL'))
        a.run_until(at)
        frames.append({'kind':'social','tick':a.tick,'forms':[{'id':f['id'],'branches':[{'id':b['id'],'read':observe(a.world,b['use_site'])}for b in f['branches']]}for f in g['forms']]})
    k,t,read=qround(a.tick)
    if quantity is not None:
        a.quantity.present_object(quantity,round_index=k);requests.append(emit(a,'quantity.reader',7,read-1,True,'MATERIAL_DIAGNOSTIC_QUANTITY'))
        a.run_until(read);o=observe(a.world,a.quantity.geometry['center'])
        frames.append({'kind':'quantity','tick':a.tick,'object':quantity,'read':o,'action_codec':decode_action(o),'context':moore27(a.world,a.quantity.geometry['center'])})
    if old:
        requests.append(emit(a,'TM.quantity.reader',7,read+1,True,'MATERIAL_DIAGNOSTIC_OLD_COMPARISON'));a.run_until(read+2)
        frames.append({'kind':'two_memory','tick':a.tick,'read':observe(a.world,a.two_memory.geometry['center'])})
    return {'initial':start,'frames':frames,'requests':requests,'final':physical(a.world,occupation=True),'probe_is_material':True}

def habitat_block(a,*,name,steps=8,seed=141,noise_rate=0,noise_amplitude=0,supply='full',feedback='closed',values=None):
    """Fixed finite reservoir habitat. Reservoir belongs to environment, not E1.

    Native history supplies reference78 and prepared gradient. Action2 shifts
    the NEXT presented reservoir by4 units. No host computes an optimal action.
    Exogenous RNG is independent and not marked at native ingress.
    """
    if supply not in('full','scarce','none')or feedback not in('closed','nulled','unpaired'):raise ValueError('Unknown frozen condition')
    rawmeta=dict(a.world.runtime.snapshot_metadata_entries)
    state=decode_metadata(rawmeta[KEY])if KEY in rawmeta else{'reservoir':73,'step':0,'last_command':0,'seed':seed,'generator':None,'failures':0,'stress_stopped':False}
    rng=random.Random(seed)
    if state.get('generator')is not None:
        def tup(v):return tuple(tup(x)for x in v)if isinstance(v,list)else v
        rng.setstate(tup(state['generator']))
    noise_rng=random.Random(seed+1000003)
    if state.get('noise_generator')is not None:noise_rng.setstate(tup(state['noise_generator']))
    rows=[];before=physical(a.world,occupation=True);requests=[];buffer=deque(maxlen=6)
    for local in range(steps):
        check_budget();k,t,read=qround(a.tick)
        q=int(values[local%len(values)])if values is not None else int(state['reservoir'])
        availability=supply=='full'or(supply=='scarce'and local%3==0)
        pre={'tick':a.tick,'center':observe(a.world,a.quantity.geometry['center']),'reference':observe(a.world,a.quantity.geometry['reference_site']),'object':observe(a.world,a.quantity.geometry['object_site'])}
        a.quantity.present_object(q,round_index=k)
        object_requests=[dict(x)for x in a.quantity.state['requests'][-2:]]
        requested=[]
        if availability:requested.append(emit(a,'quantity.reader',7,read-1,True,'ENVIRONMENT_READER_SUPPLY_FIXED'))
        noise=[]
        rate=0 if state.get('stress_stopped')else noise_rate
        for j in range(rate):
            # Unmarked legal peripheral writes, including possible occupied-port rejection.
            port=noise_rng.choice(['quantity.object.cue','quantity.object.resource','quantity.reader'])
            at=t+noise_rng.randrange(0,5);load=noise_rng.randrange(0,noise_amplitude+1)
            req=emit(a,port,load,at,port=='quantity.reader','EXOGENOUS_SEEDED_INPUT')
            noise.append({'port':port,'tick':at,'load':load,'id':req['id']})
        a.run_until(read);o=observe(a.world,a.quantity.geometry['center']);action=decode_action(o)
        cmd=action['command'];effect=cmd if feedback=='closed'else 0.0
        if feedback=='unpaired':effect=-state['last_command']
        # This is the environmental law, not a controller. No goal/optimal action is computed.
        exogenous=rng.choice([-3,0,3]);unclipped=q+int(2*effect)+exogenous
        nxt=max(1,min(145,unclipped))
        state['failures']=state['failures']+1 if action['status']in('NO_QUALIFIED_OUTPUT','CONFLICT_OUTSIDE_FIXED_CODEC')else 0
        if state['failures']>=3:state['stress_stopped']=True
        event_ids=[x['id']for x in object_requests+requested+noise]
        row={'block':name,'index':state['step'],'tick_start':pre['tick'],'object_tick':t,'read_tick':read,'environment_before':q,'reader_available':availability,'native_read':o,'actuator':action,'executed_command':effect,'exogenous_delta':exogenous,'environment_after':nxt,'environment_clipped':nxt!=unclipped,'noise':noise,'pre':pre,'context':moore27(a.world,a.quantity.geometry['center']),'requests':[exact_receipt(a.world.runtime.receipt(i))for i in event_ids],'physical':physical(a.world,occupation=True),'stress_stopped':state['stress_stopped']}
        rows.append(row);buffer.append(row);state.update(reservoir=nxt,step=state['step']+1,last_command=cmd)
        # Write primary observations before optional metadata/persistence can fail.
        with (EV/(name+'.rows.jsonl')).open('a',encoding='utf8')as log:log.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+'\n')
        state['generator']=json.loads(json.dumps(rng.getstate()))
        state['noise_generator']=json.loads(json.dumps(noise_rng.getstate()))
        a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(state))
        if local%4==3:
            cp=ROOT/'sistema/estado/checkpoints'/('ECO_BUFFER.'+name+'.T'+str(a.tick)+'.deetsnap.gz')
            if cp.exists():raise FileExistsError('Never overwrite a buffered complete state')
            a.save(cp)
            atomic_json(EV/(name+'.checkpoint'+str(local)+'.json'),{'path':str(cp),'sha256':digest_file(cp),'tick':a.tick,'environment_state':state,'not_an_active_pointer':True})
    state['generator']=json.loads(json.dumps(rng.getstate()));a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(state))
    return {'block':name,'condition':{'steps':steps,'seed':seed,'noise_rate':noise_rate,'noise_amplitude':noise_amplitude,'supply':supply,'feedback':feedback,'fixed_values':values},'initial':before,'rows':rows,'buffer':list(buffer),'environment_state':state,'final':physical(a.world,occupation=True),'attribution':'Hybrid environment law executed by instrument; decisions use physical direction only. No metabolism or learned control claimed.'}

def run(args):
    protect_current();check_budget();EV.mkdir(parents=True,exist_ok=True);store=Store()
    if args.command=='fork':
        rec=store.fork(args.source,args.life,kind='DIAGNOSTIC_COPY',checkpoint=args.checkpoint);print(json.dumps({'life':args.life,'tick':rec['physical']['tick'],'sha256':rec['snapshot_sha256']}));return
    if args.command=='init':
        for life,kind in(('E1_ECO_MAIN','EXACT_FORK'),('ECO_BASELINE_01','DIAGNOSTIC_COPY'),('ECO_EARLY_SHOCK_01','DIAGNOSTIC_COPY'),('ECO_MOUNT_CONTROL_01','DIAGNOSTIC_COPY')):
            if store.life_dir(life).exists():raise FileExistsError('Identity already exists; inspect and continue, never silently rerun: '+life)
            rec=store.fork('E1_SOCIAL_11',life,kind=kind);print(json.dumps({'life':life,'tick':rec['physical']['tick'],'sha256':rec['snapshot_sha256']}),flush=True)
        return
    life=args.life
    if life=='E1_SOCIAL_11':raise ValueError('Protected parent never mutated')
    if args.command=='panel':fn=lambda a:inherited_panel(a)
    else:
        def fn(a):
            trace=None
            if args.trace:
                sys.path.insert(0,str(ROOT/'laboratorio/campanas/PAISAJE_CAUSAL_01'))
                from instrumentos_pc01 import Trace
                trace=Trace(a,EV/(args.name+'.trace.jsonl.gz'),start=a.tick,end=a.tick+220,stride=1).install()
            try:return habitat_block(a,name=args.name,steps=args.steps,seed=args.seed,noise_rate=args.rate,noise_amplitude=args.amplitude,supply=args.supply,feedback=args.feedback)
            finally:
                if trace:atomic_json(EV/(args.name+'.trace_index.json'),trace.close())
    output=EV/(args.name+'.json')
    if output.exists():raise FileExistsError('Never overwrite trial output')
    result=store.mutate(life,'HABITAT01_'+args.command.upper(),fn,{'campaign':'HABITAT_CAUSAL_Y_ESTRES_E1_01','source_sha256':digest_file(__file__),'condition':vars(args)})
    result['receipts']=[exact_receipt(r)for r in store.load(life)[1].world.runtime.receipts]
    atomic_json(output,result);print(json.dumps({'life':life,'file':str(output),'tick':result['INSTRUMENTO']['tick'],'sha256':result['INSTRUMENTO']['snapshot_sha256']},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['init','fork','panel','block']);p.add_argument('--life',default='E1_ECO_MAIN');p.add_argument('--source',default='E1_SOCIAL_11');p.add_argument('--checkpoint');p.add_argument('--trace',action='store_true');p.add_argument('--name',default='INIT');p.add_argument('--steps',type=int,default=8);p.add_argument('--seed',type=int,default=141);p.add_argument('--rate',type=int,default=0);p.add_argument('--amplitude',type=int,default=0);p.add_argument('--supply',default='full');p.add_argument('--feedback',default='closed');run(p.parse_args())
