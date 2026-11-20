"""Frozen MAIN continuity contrasts; all scientific interventions declared."""
import argparse,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from core.entity import Entity,atomic_json,observation,write_gate
import dee_thinking as d

def run(root,case):
    start=time.monotonic();cfg=json.loads((root/'experimentos/continuidad/EXPERIMENT_CONFIG.json').read_text())
    q=next(c for c in cfg['cases'] if c['id']==case);e=Entity.create(tuple(q['origin']),q['initial_open'],80,event_state=q.get('event_state',1));rows=[];changes=[];target=root/'checkpoints/continuidad'/case;target.mkdir(parents=True,exist_ok=True)
    e.event_sink=root/'experimentos/continuidad/casos'/(case+'.jsonl')
    e.save(target/'MAIN_T0.deetsnap');e.sense();e.save(target/'AFTER_INITIAL_HISTORY.deetsnap');em=e.predict(30);rows.append({'phase':'first_read','panel':e.observe(),'emission':em});e.save(target/'FIRST_READ.deetsnap');last=e.observe()['delta']
    if q['treatment']=='memory_equalized':
        # Explicit separate DIAGNOSTIC world; MAIN native candidate never uses it.
        spec=e.world.view('body').spec;old=e.world.runtime.observe(spec.a);r=old.record;x=d.ResearchStateEdit();x.coordinate=spec.a;x.raw=d.pack_record(r.state,e.world.runtime.observe(spec.b).record.s_reg,r.dx,r.dy,r.dz,r.semantic);x.label='diagnostic equalization, clock preserved';e.world=e.world.diagnostic_fork([x],True);e._event('DIAGNOSTIC_EDIT',{'site':observation(old),'new_raw':x.raw,'clock_preserved':True});last=e.observe()['delta']
    samples=set(cfg['sample_ticks']);experience_ticks=set(cfg['experience_ticks'])
    for t in range(e.tick+1,cfg['horizon_absolute']+1):
        e._advance_to(t)
        if t in experience_ticks and q['treatment'] not in ('no_new_experience','memory_equalized'):
            past=e.habitat.sample();key='A' if past['arrived'] else 'B'
            if q['treatment']=='reversed_delivery':key='B' if key=='A' else 'A'
            e._input(key,t,{'kind':'ACTUAL_OBSERVED_PACKET' if q['treatment']=='full' else 'DECOUPLED_SENSOR_CONTROL','past':past});e.slot_index+=1
        p=e.observe()
        if p['delta']!=last:changes.append({'tick':e.tick,'before_delta':last,'after_delta':p['delta'],'a':p['a'],'b':p['b'],'gates':p['write_gates']});last=p['delta']
        if t in samples or t in experience_ticks:rows.append({'phase':'follow','panel':p})
        if t in (164,555,813,946):
            em=e.predict(30)
            rows.append({'phase':'prediction','emission':em,'panel':e.observe()})
        if t in (164,555,813):e.save(target/('T'+str(e.tick)+'.deetsnap'))
    evaluations=e.advance(0)['evaluations'];final=e.save(target/'MAIN_FINAL.deetsnap');out={'case':q,'schema':1,'config':cfg['version'],'preparation':'new H0, actual observed past packet pair, no AB/BA preset','mode':'MAIN_CONTINUOUS' if q['treatment']!='memory_equalized' else 'DIAGNOSTIC_FORK','rows':rows,'relational_changes':changes,'events':e.events,'evaluations':evaluations,'operations':e.operation_calls,'final':final,'duration_seconds':time.monotonic()-start,'operational_forks':int(q['treatment']=='memory_equalized'),'external_physical_write_calls':[x for x in e.operation_calls if x['operation'] in ('submit','probe')],'runtime_version':d.__version__,'kernel':'v27'}
    atomic_json(root/'experimentos/continuidad/casos'/(case+'.json'),out);print(json.dumps({'case':case,'changes':changes,'final_delta':e.observe()['delta'],'final_direction':e.observe()['physical_output']['direction'],'receipts':[(x['tick'],x['receipt']['status']) for x in e.events if x['kind']=='EXPERIENCE'],'final':final['sha256']},ensure_ascii=True),flush=True)
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=ROOT);a.add_argument('--case',required=True);args=a.parse_args();run(args.root,args.case)
