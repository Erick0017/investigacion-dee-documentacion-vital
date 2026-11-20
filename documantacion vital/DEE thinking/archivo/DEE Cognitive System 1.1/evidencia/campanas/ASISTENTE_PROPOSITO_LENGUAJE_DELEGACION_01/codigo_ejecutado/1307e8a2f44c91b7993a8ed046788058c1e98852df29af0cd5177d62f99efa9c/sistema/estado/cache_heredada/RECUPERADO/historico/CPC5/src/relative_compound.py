"""Two acquired relative memories, native joint readout, matched geometry controls.

The source/reader/centres are prepared, not trained snapshots.  A common pair
of physical probes is evaluated by v27.  No external combining of responses.
"""
import argparse
import json
from pathlib import Path
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, digest, gate, identity, interface, local_context, put, receipt, record, sha, until

PA = ((-1,0,0),(-1,1,1),(0,0,1),(0,1,0))
PB = ((0,-1,0),(0,0,-1),(1,-1,-1),(1,0,0))
N = 47
KEY = 'cpc5.relative_compound.neutral.v1'


def prepare(case):
    import dee_thinking as d
    offset = case.get('translation', [0,0,0])
    def add(q, delta): return tuple((q[i] + delta[i]) % N for i in range(3))
    centers = [(15,15,15), (25,15,15 if case.get('coupled',True) else 29)]
    starts = case.get('lesson_ticks', [0,65])
    placements = []; ports = []; occupied = set(); spec = {'memories': {}, 'N': N, 'geometry': 'two actual relative cells'}
    def place(site, state, load, direction=(0,0,0), semantic=4, clock=0, role='support'):
        if site in occupied: raise ValueError('Preparation overlap at ' + str(site))
        occupied.add(site); p=d.InitialPlacement(); p.site=d.Coordinate(*site)
        p.raw=d.pack_record(state,load,*direction,semantic); p.clock=clock; p.role=role; placements.append(p)
    for index, center in enumerate(centers):
        name = 'M'+str(index+1); center=add(center,offset); a=add(center,(-1,0,0)); b=add(center,(1,0,0))
        phase=(260-starts[index])%780
        place(a,1000,100,semantic=1,clock=phase,role=name+'.A');place(b,2000,100,semantic=1,clock=phase,role=name+'.B')
        for q,pattern,s,clock in ((a,PA,3000,31),(b,PB,4000,41)):
            for j,v in enumerate(pattern): place(add(q,v),s+j,0,clock=clock+j,role=name+'.support')
        if case.get('reader','probe')=='persistent':place(add(center,(0,-2,0)),6000,7,(0,1,0),clock=23,role=name+'.reader')
        for letter,q,v,dr in (('A',a,(0,-1,0),(0,-1,0)),('B',b,(0,1,0),(0,1,0))):
            ports.append(interface(name+'.'+letter,add(q,v),dr,state=5000 if letter=='A' else 5001))
        ports.append(interface(name+'.read',add(center,(0,-1,0)),(0,1,0)))
        spec['memories'][name]={'A':a,'B':b,'center':center,'read_site':add(center,(0,-1,0)), 'initial_clock':phase}
    spec['joint']=add((20,20,15),offset)
    spec['joint_out']=add(spec['joint'],(0,4,0))
    recipe=d.OrganizationRecipe.research(N,placements,0);recipe.interfaces=ports
    backend={'Lazy':d.Backend.LAZY,'Dense':d.Backend.DENSE_SEQUENTIAL,'Parallel':d.Backend.DENSE_PARALLEL}[case.get('backend','Lazy')]
    recipe.execution=d.TickOptions(backend,1)
    return d.OrganizationalWorld.create(recipe),spec


def sample(world,spec):
    memories={}
    for name,s in spec['memories'].items():
        a,b=record(world,s['A']),record(world,s['B'])
        memories[name]={'A':a,'B':b,'delta':a['s_reg']-b['s_reg'] if a['active'] and b['active'] else None,
                        'reader':record(world,s['read_site']),'expression':record(world,s['center'])}
    return {'tick':world.runtime.current_tick,'memories':memories,'joint':record(world,spec['joint']),
            'joint_out':record(world,spec['joint_out'])}


def run_case(case,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);put(out/'CONFIG.json',case)
    started=time.monotonic();engine=identity();world,spec=prepare(case)
    calls=[];rows=[];states=[];contexts=[]
    def call(port,value,tick,kind):
        r=getattr(world,kind)(port,value,tick)
        calls.append({'id':r.id,'port':port,'payload':value,'requested_tick':tick,'call_tick':world.runtime.current_tick,'kind':kind})
    def snap(label):
        world.runtime.set_snapshot_metadata(KEY,json.dumps({'version':1,'geometry':spec,'phase':label,'tick':world.runtime.current_tick},separators=(',',':')))
        path=out/(label+'.deetsnap');world.save_snapshot(str(path));states.append({'path':path.name,'sha256':sha(path),'physics':digest(world)})
    snap('INITIAL_T0')
    for j,history in enumerate(case.get('histories',['AB','BA'])):
        if history not in ('AB','BA','H0'):raise ValueError('History AB/BA/H0 only')
        for slot,letter in enumerate(history if history!='H0' else ''):
            call(f'M{j+1}.{letter}',3,case.get('lesson_ticks',[0,65])[j]+slot,'submit')
    query_ticks=case.get('query_ticks',[70,130])
    for tick in query_ticks:
        for j in (1,2):call(f'M{j}.read',7,tick,'probe')
    horizon=int(case.get('horizon',160))
    boundaries={0,2,64,67,horizon,*query_ticks,*[x+3 for x in query_ticks],*[x+9 for x in query_ticks]}
    full_window=set(range(0,8))|set(range(63,85))|set(range(128,146))
    if case.get('passive',True):
        observe_ticks=full_window|set(range(0,horizon+1,10))
    else: observe_ticks={horizon}
    for tick in range(horizon+1):
        if tick in observe_ticks:
            rows.append(sample(world,spec))
            if tick in boundaries:put(out/'INCREMENTAL.json',{'rows':rows,'calls':calls,'actual_tick':tick})
        if tick in (0,1,65,66,70,71,72,73,74,75,76,77,78,79,80):
            contexts.append({'tick':tick,'memory_gates':{name:{letter:gate(world,p[letter]) for letter in ('A','B')} for name,p in spec['memories'].items()},
                             'joint_neighborhood':local_context(world,spec['joint'])})
        if tick in boundaries:snap('T'+str(tick))
        if tick<horizon:world.advance()
    result={'case':case,'engine':engine,'N':N,'backend':case.get('backend','Lazy'),'ports':spec,'calls':calls,
            'receipts':[receipt(world,x['id']) for x in calls], 'rows':rows,'gate_and_joint_windows':contexts,
            'snapshots':states,'final':sample(world,spec),'physics':digest(world),'source_sha256':sha(__file__),
            'external_operations':list(world.external_operations),'elapsed_seconds':time.monotonic()-started,
            'preparation_count':1,'continuation':True,'host_raw_edits':[],'host_clock_edits':[],
            'scope':'Native joint readout candidate; two memories acquired at separate epochs. Resource-identical displaced control. A fork observer does not feed MAIN.'}
    put(out/'MEASUREMENTS.json',result)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--case',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    r=run_case(json.loads(a.case.read_text(encoding='utf-8')),a.output)
    print(json.dumps({'id':r['case']['id'],'final_deltas':{k:v['delta'] for k,v in r['final']['memories'].items()},
                      'joint_events':[{ 'tick':x['tick'],'joint':x['joint']} for x in r['rows'] if x['joint']['active']]}))
