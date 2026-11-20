"""Online relative memory with a native replenished reader, adapted from I02.

This is an independent component cohort, not the historical CPC4 individual or
the ABCD mobile genealogy. Source preparation is fixed; any new experience is
submitted through declared ports. No host clearing, clock update or repair.
"""
from pathlib import Path
from array import array
import argparse,hashlib,json,sys,time
from campaign import ROOT,PARENT,put,sha
sys.path.insert(0,str(PARENT))
from src.common import interface,observe,receipt

PA=((-1,0,0),(-1,1,1),(0,0,1),(0,1,0))
PB=((0,-1,0),(0,0,-1),(1,-1,-1),(1,0,0))

def digest(world):
    r=world.runtime
    return {'tick':r.current_tick,'RAW':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),
            'clocks':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}

def prepare(case):
    import dee_thinking as d
    n=int(case.get('N',17));c=tuple(case.get('origin',(n//2,)*3));phase=int(case.get('phase',260))
    def add(q,v):return tuple((q[i]+v[i])%n for i in range(3))
    a=add(c,(-1,0,0));b=add(c,(1,0,0));placements=[];occupied=set()
    def place(q,state,load,dr=(0,0,0),semantic=4,clock=0,role='support'):
        if q in occupied:raise ValueError('Preparation overlap')
        occupied.add(q);p=d.InitialPlacement();p.site=d.Coordinate(*q);p.raw=d.pack_record(state,load,*dr,semantic);p.clock=clock;p.role=role;placements.append(p)
    place(a,1000,100,semantic=1,clock=phase,role='plastic_A')
    place(b,2000,100,semantic=1,clock=phase,role='plastic_B')
    for center,pattern,state,clock in ((a,PA,3000,31),(b,PB,4000,41)):
        for i,v in enumerate(pattern):place(add(center,v),state+i,0,clock=clock+i)
    source=add(c,(0,-2,0))
    if case.get('reader','persistent')!='absent':
        place(source,6000,7,(0,1,0),semantic=4 if case.get('reader','persistent')=='persistent' else 1,clock=23,role='reader_supply')
    ports={'A':a,'B':b,'comparator':c,'reader_source':source,'reader':add(c,(0,-1,0))}
    interfaces=[]
    directions=case.get('event_directions',{'A':[0,0,-1],'B':[0,0,1]})
    for name,center,offset in (('A',a,(0,-1,0)),('B',b,(0,1,0))):
        dr=tuple(directions[name])
        for delay in (0,):
            q=add(center,offset);item=interface('event.'+name,q,dr,state=5000 if name=='A' else 5001)
            interfaces.append(item);ports['event.'+name]=q
    recipe=d.OrganizationRecipe.research(n,placements,0);recipe.interfaces=interfaces;recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    return d.OrganizationalWorld.create(recipe),ports

def sample(world,ports):
    import dee_thinking as d
    values={name:observe(world,q) for name,q in ports.items()}
    a,b=values['A'],values['B']
    gates={}
    for name in ('A','B'):
        g=d.inspect_write_gate(world.runtime,d.Coordinate(*ports[name]),False)
        gates[name]={k:getattr(g,k) for k in ('local_clock','center_available','n_active','hadron','rule_value','survives_material_rule','semantic_protected','write_protected','k','period','phase_remainder','ordinary_increment_condition','branch','demux_status')}
    return {'tick':world.runtime.current_tick,'delta':a['s_reg']-b['s_reg'] if a['active'] and b['active'] else None,
            'physical':values,'gates':gates}

def run(case,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);put(out/'CONFIG.json',case)
    import shutil
    shutil.copyfile(__file__,out/'EXECUTED_SOURCE.py')
    w,ports=prepare(case);start=time.monotonic();ids=[];calls=[]
    def submit(name,t):
        r=w.submit('event.'+name,case.get('event_load',0),t);ids.append(r.id)
        calls.append({'tick_of_call':w.runtime.current_tick,'requested_tick':t,'channel':'event.'+name,'load':case.get('event_load',0),'receipt_id':r.id})
    history=case.get('history','AB')
    for i,name in enumerate(history if history in ('AB','BA') else ''):submit(name,i)
    for event in case.get('additional_events',[]):submit(event['site'],event['tick'])
    checkpoints=set(case.get('checkpoints',[0,2,50,195,260,390,520]))
    horizon=int(case.get('horizon',520));rows=[];gate_occasions=[]
    for t in range(horizon+1):
        row=sample(w,ports)
        if t in checkpoints or t<6 or t%10==0 or any(x['ordinary_increment_condition'] for x in row['gates'].values()):rows.append(row)
        for name,g in row['gates'].items():
            if g['ordinary_increment_condition']:gate_occasions.append({'tick':t,'center':name,**g})
        if t in checkpoints:w.save_snapshot(str(out/('T'+str(t)+'.deetsnap')))
        if t<horizon:w.advance()
    final=sample(w,ports)
    result={'case':case,'ports':ports,'source_sha256':sha(__file__),'rows':rows,'gate_occasions':gate_occasions,
            'final':final,'physics':digest(w),'receipts':[receipt(w,i) for i in ids],'actual_submit_calls':calls,
            'runtime_external_operations':list(w.external_operations),'elapsed_seconds':time.monotonic()-start,
            'modality':'EXPERIENCE_PROTOCOL plus NATIVE_EVOLUTION plus PASSIVE_OBSERVATION',
            'scope':'A separate adapted I02 cohort. Prepared renewable reader is not by itself experience-modified regulation; constructor is not a reproduction of the historical Runtime file format.'}
    put(out/'MEASUREMENTS.json',result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--case',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    r=run(json.loads(a.case.read_text(encoding='utf-8-sig')),a.output)
    print(json.dumps({'id':r['case']['id'],'delta':r['final']['delta'],'comparator':r['final']['physical']['comparator'],'elapsed':r['elapsed_seconds']}))
