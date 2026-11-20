"""Order retained by relative matter, later physical sign association and context.

The host sends A/B events, identical name cues to two fixed branches, and current
context carriers. It never reads the learned sign to choose a branch or response.
Name access uses a route transformed by a native order readout, not a response map.
"""
from pathlib import Path
import argparse
import json
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,BASE,put,sha,identity,interface,record,receipt,digest,operational,local_context,gate

N=67
PA=((-1,0,0),(-1,1,1),(0,0,1),(0,1,0))
PB=((0,-1,0),(0,0,-1),(1,-1,-1),(1,0,0))
KEY='cpc5.extension.semantic_order.v1'

def prepare(case):
    import dee_thinking as d
    shift=case.get('translation',[0,0,0]);add=lambda q,v:tuple((q[i]+v[i])%N for i in range(3))
    c=add((33,25,33),shift);a=add(c,(-1,0,0));b=add(c,(1,0,0));placements=[];used=set()
    def place(q,state,load,sem,clock):
        if q in used:raise ValueError('Overlapping supports')
        used.add(q);p=d.InitialPlacement();p.site=d.Coordinate(*q);p.raw=d.pack_record(state,load,0,0,0,sem);p.clock=clock;p.role='Fresh relative-order support';placements.append(p)
    place(a,1000,100,1,260);place(b,2000,100,1,260)
    for q,pattern,state,clock in ((a,PA,3000,31),(b,PB,4000,41)):
        for i,v in enumerate(pattern):place(add(q,v),state+i,0,4,clock+i)
    ports=[interface('event.A',add(a,(0,-1,0)),(0,-1,0),state=5000),
           interface('event.B',add(b,(0,1,0)),(0,1,0),state=5001),
           interface('order.read',add(c,(0,-1,0)),(0,1,0))]
    names={};access={};consequence={}
    for sign,label in ((-1,'left'),(1,'right')):
        h=add(c,(4*sign,0,0));names[label]=h
        access[label]=add(h,(20*sign,20,0))
        consequence[label]=add(h,(27*sign,27,0))
        ports.append(interface('name.'+label,add(h,(0,-3,0)),(0,1,0)))
        ports.append(interface('query.'+label,add(access[label],(0,-3,0)),(0,1,0)))
        for context in (-1,1):
            ports.append(interface('context.'+label+('.plus' if context==1 else '.minus'),add(consequence[label],(0,0,-3*context)),(0,0,context)))
    recipe=d.OrganizationRecipe.research(N,placements,0);recipe.interfaces=ports;recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    spec={'N':N,'center':c,'A':a,'B':b,'name_hubs':names,'access_sites':access,'context_sites':consequence,
          'initial_sites':len(placements),'interfaces':[p.name for p in ports],
          'scope':'Prepared two-branch sensor geometry; relative order must be acquired from events; no host branch choice or stored response mapping'}
    return d.OrganizationalWorld.create(recipe),spec

def run_case(case,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);started=time.monotonic();engine=identity();w,s=prepare(case)
    calls=[];rows=[];windows=[];snaps=[]
    frozen={'case':case,'geometry':s,'source_sha256':sha(__file__),
            'claim_criterion':'Paired A/B histories must differ under the same passive/physical readout; naming effect must differ from unpaired/omitted names at a route absent without naming; contextual combinations preserve x and add z only if measured',
            'decoder':'Return actual active semantic1 records above query load, retain direction vector and original fields; no label inferred from teaching logs',
            'initial_guards':'A/B clocks260, semantic4 supports; no postT0 RAW/clock editing'}
    put(out/'CONFIG.json',frozen)
    def submit(port,payload,tick,kind='submit',origin='CURRENT_EVENT'):
        r=getattr(w,kind)(port,payload,tick);calls.append({'id':int(r.id),'port':port,'payload':payload,'requested_tick':tick,'call_tick':int(w.runtime.current_tick),'kind':kind,'origin':origin})
    history=case.get('history','AB');gap=case.get('gap',1)
    if sorted(history)!=['A','B'] or type(gap) is not int or gap<1:raise ValueError('Two events AB or BA and positive interval required')
    if not case.get('history_omitted'):
        for i,letter in enumerate(history):submit('event.'+letter,case.get('event_load',3),i*gap)
    read_tick=case.get('read_tick',2)
    submit('order.read',case.get('reader_load',7),read_tick,'probe','COMMON_ORDER_READOUT')
    if case.get('name_mode','paired')!='omitted':
        name_tick=case.get('name_tick',4)+(case.get('name_mode')=='unpaired')
        for label in s['name_hubs']:submit('name.'+label,case.get('name_load',5),name_tick,origin='OPAQUE_SIGNAL_AFTER_ORDER_EXPERIENCE')
    for tick in case.get('name_query_ticks',[24,91]):
        for label in s['access_sites']:submit('query.'+label,case.get('query_load',5),tick,'probe','SAME_SYMBOL_FIXED_TWO_BRANCH_INTERFACE')
    context=case.get('context',0)
    if context not in (-1,0,1):raise ValueError('Context current direction -1,0,+1 required')
    if context:
        for label in s['context_sites']:submit('context.'+label+('.plus' if context==1 else '.minus'),case.get('context_load',3),case.get('context_tick',31),origin='CURRENT_CONTEXT_NOT_COMBINED_TARGET')
    for tick in case.get('later_order_reads',[]):submit('order.read',case.get('reader_load',7),tick,'probe','LATER_ORDER_WITHOUT_RETEACHING')
    def snapshot(label):
        # Metadata contains only geometry, physical input protocol and phase, never acquired answer.
        w.runtime.set_snapshot_metadata(KEY,json.dumps({'schema':1,'geometry':s,'tick':w.runtime.current_tick,'input_ids':[x['id'] for x in calls]},separators=(',',':')))
        path=out/(label+'.deetsnap');w.save_snapshot(str(path));snaps.append({'file':path.name,'sha256':sha(path),'physical':digest(w),'operative':operational(w)})
    snapshot('INITIAL_T0')
    horizon=case.get('horizon',110);capture=set(range(0,12))|{24,25,26,27,28,30,31,32,33,34,35,36,37,67,68,69,70,71,74,91,92,93,94,95,100,110,horizon}
    capture={t for t in capture if t<=horizon}
    for tick in sorted(capture):
        w.run_until(tick);ar,br=record(w,s['A']),record(w,s['B'])
        row={'tick':tick,'A':ar,'B':br,'delta':ar['s_reg']-br['s_reg'] if ar['active'] and br['active'] else None,
             'comparator':record(w,s['center']),
             'order_emission':{label:record(w,tuple((s['center'][i]+(1 if label=='right' else -1)*(i==0))%N for i in range(3))) for label in ('left','right')},
             'name_hubs':{k:record(w,q) for k,q in s['name_hubs'].items()},
             'name_access':{k:record(w,q) for k,q in s['access_sites'].items()},
             'context_sites':{k:record(w,q) for k,q in s['context_sites'].items()}}
        rows.append(row)
        if tick in (2,3,4,6,7,8,26,27,28,33,34,35):
            windows.append({'tick':tick,'comparator':local_context(w,s['center']),
                            'name_hubs':{k:local_context(w,q) for k,q in s['name_hubs'].items()},
                            'access':{k:local_context(w,q) for k,q in s['access_sites'].items()},
                            'context':{k:local_context(w,q) for k,q in s['context_sites'].items()},
                            'guard_A':gate(w,s['A']),'guard_B':gate(w,s['B'])})
        if tick in (4,8,28,35,horizon):snapshot('T'+str(tick))
        put(out/'INCREMENTAL.json',{'last_tick':tick,'rows':rows,'completed':False})
    result={'schema':'CPC5.extension.semantic_order.v1','case':case,'engine':engine,'geometry':s,'calls':calls,
            'receipts':[receipt(w,x['id']) for x in calls],'rows':rows,'local_windows':windows,'snapshots':snaps,
            'final_physics':digest(w),'final_operative':operational(w),'external_operations':list(w.external_operations),
            'post_T0_host_RAW_clock_edits':[],'elapsed_seconds':time.monotonic()-started,'preparations':1,
            'attribution':'Order/comparator response, name-induced routing and contextual interaction are distinct tests. Two branches/name interface prepared, associations not written as target or policy.'}
    put(out/'MEASUREMENTS.json',result)
    print(json.dumps({'case':case['id'],'final_delta':rows[-1]['delta'],'seconds':result['elapsed_seconds']}),flush=True)
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    config=json.loads(args.config.read_text(encoding='utf-8'));args.output.mkdir(parents=True,exist_ok=True)
    for case in config['cases']:
        target=args.output/case['id']
        if (target/'MEASUREMENTS.json').exists():continue
        run_case(case,target)

if __name__=='__main__':main()
