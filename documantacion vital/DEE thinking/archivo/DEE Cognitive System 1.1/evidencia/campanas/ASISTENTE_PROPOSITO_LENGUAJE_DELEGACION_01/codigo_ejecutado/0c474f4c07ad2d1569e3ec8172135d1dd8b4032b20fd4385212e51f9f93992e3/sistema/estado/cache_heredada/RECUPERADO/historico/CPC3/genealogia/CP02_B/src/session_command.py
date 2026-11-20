"""One bounded, single-writer native command process for the usable session."""
import argparse,json,random,shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from predictor import *


def handle(a):
    folder=Path(a.output).resolve();folder.mkdir(parents=True,exist_ok=True);state=folder/'CURRENT.deetsnap';side=folder/'SESSION.json';log=AuditLog(folder/'PREDICCIONES.jsonl')
    cmd=a.command;args=a.arguments
    if cmd=='nuevo':
        if len(args) not in (1,2,3):raise ValueError('nuevo semilla [directo|asistido] [cambio_tick|none]')
        seed=int(args[0]);mode=args[1] if len(args)>1 else 'directo';change=None if len(args)<3 or args[2]=='none' else int(args[2])
        if mode not in ('directo','asistido'):raise ValueError('mode directo|asistido')
        s=PredictorSession(build(),PersistentTransportHabitat(random.Random(seed).getrandbits(1)==1,change));s.save(state)
        atomic_json(side,{'schema':1,'run_id':'SESSION_'+str(time.time_ns()),'mode':mode,'explicit_restart':True,'seed_evaluator_only':seed,'completed_goals':[]})
        return {'operation':cmd,'tick':32,'new_instance':True,'mode':mode,'hidden_condition_exposed':False}
    if cmd=='cargar':
        if len(args)!=1:raise ValueError('cargar snapshot')
        s=PredictorSession.load(args[0]);s.save(state);atomic_json(side,{'schema':1,'run_id':'RESTORED_'+str(time.time_ns()),'mode':'asistido','explicit_restart':False,'completed_goals':[]})
        return {'operation':cmd,'tick':s.world.runtime.current_tick,'continued_existing_native_history':True,'mode':'asistido (explicit default after load)'}
    if not state.exists():raise ValueError('No instance; use nuevo or cargar')
    s=PredictorSession.load(state);meta=json.loads(side.read_text(encoding='utf-8'));run=meta['run_id']
    if cmd=='experiencia':
        if not args and s.world.runtime.current_tick==32:
            rs=s.experience_past_results();result={'operation':cmd,'receipts':rs,'panel':panel(s.world),'source':'past actual primary and inverse reference outcomes, not future targets'}
        else:
            if len(args)!=1:raise ValueError('experiencia [tick] (tick optional only for initial primary/reference pair)')
            at=int(args[0]);current=s.world.runtime.current_tick
            if at<current or at-current>1500:raise ValueError('sample tick future and at most1500 ticks away')
            s.world.run_until(at);s.habitat.advance(at,[]);past=s.habitat.actual_past_result(at);key='A' if past['arrived'] else 'B'
            r=s.world.submit('sensor.'+key,0,at);s.accessible.append({'sensor':key,'tick':at,'source_past_result_tick':at,'reference_branch':False,'load':0,'receipt_id':r.id});s.world.advance();s.habitat.advance(at+1,[])
            result={'operation':cmd,'observed_past_outcome':past,'receipt':receipt(s.world.runtime.receipt(r.id)),'panel':panel(s.world)}
    elif cmd=='predice':
        if not args:raise ValueError('predice tick_objetivo [tick_objetivo...]')
        ts=list(map(int,args));current=s.world.runtime.current_tick
        if max(ts)-current>1500:raise ValueError('Maximum future horizon1500')
        identifier=run+'_EM'+str(len(s.emissions))
        if meta['mode']=='asistido':
            f=s.fork();result=f.predict(ts,log,identifier,modality='DIAGNOSTIC_PHYSICAL_PROBE_IN_DESCENDANT');s.world.advance(3);s.habitat.advance(s.world.runtime.current_tick,[]);s.emissions.append(result)
        else:result=s.predict(ts,log,identifier)
    elif cmd=='resultado':
        if len(args)!=1:raise ValueError('resultado tick_objetivo')
        target=int(args[0]);em=next((x for x in reversed(s.emissions) if target in x['target_ticks']),None)
        if em is None:raise ValueError('No prior prospective emission for this target')
        result=s.evaluate(target,log,em['run_id']);meta['completed_goals'].append(target)
    elif cmd=='avanzar':
        if len(args)!=1:raise ValueError('avanzar cantidad_ticks')
        count=int(args[0])
        if not 0<=count<=1500:raise ValueError('advance0..1500')
        s.world.advance(count);s.habitat.advance(s.world.runtime.current_tick,[]);result={'operation':cmd,'tick':s.world.runtime.current_tick,'panel':panel(s.world)}
    elif cmd=='observar':
        if args:raise ValueError('observar takes no arguments')
        result={'operation':cmd,'panel':panel(s.world),'live_output':observation(s.world.observe('body','comparator')),'observer':'external passive scientist; not native introspection'}
    elif cmd=='guardar':
        if len(args)!=1:raise ValueError('guardar path')
        s.save(args[0]);result={'operation':cmd,'saved':str(Path(args[0]).resolve()),'tick':s.world.runtime.current_tick,'sha256':hashlib.sha256(Path(args[0]).read_bytes()).hexdigest()}
    else:raise ValueError('Unknown command')
    s.save(state);atomic_json(side,meta);return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('command');p.add_argument('arguments',nargs='*');a=p.parse_args()
    try:print(json.dumps({'accepted':True,'result':handle(a)},ensure_ascii=False))
    except Exception as e:print(json.dumps({'accepted':False,'error':type(e).__name__+': '+str(e)},ensure_ascii=False));raise SystemExit(2)
