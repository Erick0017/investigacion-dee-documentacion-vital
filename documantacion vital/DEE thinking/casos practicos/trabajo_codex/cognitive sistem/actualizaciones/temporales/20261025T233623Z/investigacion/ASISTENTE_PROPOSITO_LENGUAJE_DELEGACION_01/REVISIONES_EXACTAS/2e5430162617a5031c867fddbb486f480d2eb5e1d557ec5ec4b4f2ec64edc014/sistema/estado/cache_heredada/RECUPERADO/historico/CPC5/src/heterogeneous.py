"""Matched N67 cohorts: two actual relative cells and two mobile relations.

These are heterogeneous coexisting mechanisms. Only the mobile subgraph is
connected in R5; the relative cells are NOT claimed to receive its output.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import time
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT, identity, digest, interface, record, local_context, gate, receipt, put, sha
from network import geometry as mobile_geometry, interfaces_for, protocol, moved

N=67
PA=((-1,0,0),(-1,1,1),(0,0,1),(0,1,0))
PB=((0,-1,0),(0,0,-1),(1,-1,-1),(1,0,0))


def prepare(case):
    import dee_thinking as d
    shift=case.get('translation',[0,0,0]);cells={};placements=[];ports=[];occupied=set()
    add=lambda q,v:tuple((q[i]+v[i])%N for i in range(3))
    def place(q,state,load,dr=(0,0,0),sem=4,clock=0,role='support'):
        if q in occupied:raise ValueError('Initial overlap '+str(q))
        occupied.add(q);p=d.InitialPlacement();p.site=d.Coordinate(*q)
        p.raw=d.pack_record(state,load,*dr,sem);p.clock=clock;p.role=role;placements.append(p)
    for j,center in enumerate(((15,15,45),(35,35,57)),1):
        c=add(center,shift);a=add(c,(-1,0,0));b=add(c,(1,0,0));phase=260 if j==1 else 0
        place(a,1000,100,sem=1,clock=phase,role=f'm{j}.A')
        place(b,2000,100,sem=1,clock=phase,role=f'm{j}.B')
        for q,pattern,state,clock in ((a,PA,3000,31),(b,PB,4000,41)):
            for i,delta in enumerate(pattern):place(add(q,delta),state+i,0,clock=clock+i)
        if j==1:place(add(c,(0,-2,0)),6000,7,(0,1,0),clock=23,role='fixed_prepared_reader_source')
        for letter,q,v,dr,state in (('A',a,(0,-1,0),(0,-1,0),5000),('B',b,(0,1,0),(0,1,0),5001)):
            ports.append(interface(f'm{j}.{letter}',add(q,v),dr,state=state))
        ports.append(interface(f'm{j}.read',add(c,(0,-1,0)),(0,1,0)))
        cells[f'm{j}']={'A':a,'B':b,'comparator':c,'reader':add(c,(0,-1,0)),'source':add(c,(0,-2,0))}
    mobile_case={'N':N,'chains':[2] if case['coupled'] else [1,1],
                 'translation':shift,'loads':case['mobile_loads'],'query':case['query']}
    mob=mobile_geometry(mobile_case);ports+=interfaces_for(mob)
    # Same number and load of physical queries. R5's second query is an
    # explicitly external dose-control lane, not another learned component.
    dose_source=add((5,5,30),shift)
    if case['coupled']:ports.append(interface('dose_control.query',dose_source,(1,0,0)))
    recipe=d.OrganizationRecipe.research(N,placements,0);recipe.interfaces=ports
    recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    world=d.OrganizationalWorld.create(recipe)
    spec={'N':N,'cells':cells,'mobile':mob,'initial_material_sites':len(placements),
          'functional_components':4,'types':['relative','relative','mobile','mobile'],
          'coupling':'mobile stage0->mobile stage1' if case['coupled'] else 'two independent mobile components',
          'dose_control_source':list(dose_source) if case['coupled'] else None,
          'scope':'Coexistence and mobile-subgraph coupling, not mobile-to-relative integration'}
    return world,spec,mobile_case


def sample(world,spec):
    values={}
    for name,sites in spec['cells'].items():
        p={k:record(world,q) for k,q in sites.items()};a,b=p['A'],p['B']
        values[name]={'delta':a['s_reg']-b['s_reg'] if a['active'] and b['active'] else None,
                      'physical':p,'relation_available':a['active'] and b['active']}
    return {'tick':world.runtime.current_tick,'relative_cells':values}


def run_case(case,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    started=time.monotonic();engine=identity();world,spec,mobcase=prepare(case)
    config={'case':case,'geometry':spec,'source_sha256':sha(__file__),
            'criterion':'Report actual relative deltas/availability, admission, physical mobile encounters and paired resource counts; no global architecture score',
            'frozen_horizon':520,'initial_clock_preparation':'m1=260,m2=0; never reset afterT0'}
    put(output/'CONFIG.json',config)
    calls=[];rows=[];windows=[];snapshots=[];mobile_reads=[]
    def submit(port,payload,tick,kind='submit',origin='CURRENT_EXPERIENCE'):
        r=getattr(world,kind)(port,payload,tick)
        calls.append({'id':r.id,'port':port,'payload':payload,'requested_tick':tick,
                      'call_tick':world.runtime.current_tick,'kind':kind,'origin':origin})
    for j,history,start in ((1,case['relative_histories'][0],0),(2,case['relative_histories'][1],260)):
        if history not in ('AB','BA'):raise ValueError('Matched two-letter AB or BA history required')
        for slot,letter in enumerate(history):submit(f'm{j}.{letter}',3,start+slot)
    for item in protocol(mobcase,spec['mobile']):
        submit(item['channel'],item['load'],item['tick'],origin='MOBILE_TRAINING_OR_QUERY')
    if case['coupled']:submit('dose_control.query',case['query'],6,'probe','DECLARED_SECOND_QUERY_DOSE_LANE')
    for tick in (262,400):submit('m2.read',7,tick,'probe','COMMON_PHYSICAL_READER_PROBE')
    def snap(label):
        world.runtime.set_snapshot_metadata('cpc5.heterogeneous.v1',json.dumps({'schema':1,'tick':world.runtime.current_tick,'geometry':spec,'input_ids':[x['id'] for x in calls]},separators=(',',':')))
        path=output/(label+'.deetsnap');world.save_snapshot(str(path))
        snapshots.append({'file':path.name,'sha256':sha(path),'physical':digest(world)})
    snap('INITIAL_T0')
    boundaries=sorted(set([0,1,2,3,10,11,15,16,20,50,100,200,259,260,261,262,263,264,265,270,300,390,399,400,401,403,406,450,520]))
    for tick in boundaries:
        world.run_until(tick);rows.append(sample(world,spec))
        if tick in (0,1,2,260,261,262,263,264,265,399,400,401):
            windows.append({'tick':tick,'relative_context':{name:{'A':local_context(world,p['A']),'B':local_context(world,p['B']),
                    'gate_A':gate(world,p['A']),'gate_B':gate(world,p['B'])} for name,p in spec['cells'].items()}})
        for stage in spec['mobile']['stages']:
            if tick in (stage['meeting_tick']-1,stage['meeting_tick']):
                mobile_reads.append({'tick':tick,'stage':stage['index'],'phase':'post' if tick==stage['meeting_tick'] else 'pre',
                                     'center':record(world,stage['first_meeting']),
                                     'local_context':local_context(world,stage['first_meeting'])})
        if tick in (259,270,520):snap('T'+str(tick))
        put(output/'INCREMENTAL.json',{'tick':tick,'rows':rows,'mobile_encounters':mobile_reads})
    result={'schema':'CPC5.heterogeneous.measurements.v1','case':case,'engine':engine,'geometry':spec,
            'calls':calls,'receipts':[receipt(world,x['id']) for x in calls], 'rows':rows,
            'relative_gate_windows':windows,'mobile_encounters':mobile_reads,
            'snapshots':snapshots,'final':sample(world,spec),'physics':digest(world),
            'external_operations':list(world.external_operations),'host_RAW_clock_edits_after_T0':[],
            'elapsed_seconds':time.monotonic()-started,'preparations':1,
            'scope':'Four heterogeneous functional components in one continuing N67 Runtime. Same physical inventories and input loads, distinct routing of one query. Fixed renewable relative reader is prepared; learning of routing or mobile->relative transfer is not inferred.'}
    put(output/'MEASUREMENTS.json',result)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();config=json.loads(a.config.read_text(encoding='utf-8-sig'));a.output.mkdir(parents=True,exist_ok=True);index=[]
    for case in config['cases']:
        target=a.output/case['id']
        result=json.loads((target/'MEASUREMENTS.json').read_text(encoding='utf-8')) if (target/'MEASUREMENTS.json').exists() else run_case(case,target)
        row={'id':case['id'],'architecture':case['architecture'],'phase':case['phase'],
             'final_deltas':{k:v['delta'] for k,v in result['final']['relative_cells'].items()},
             'mobile_readouts':[r['center'] for r in result['mobile_encounters'] if r['phase']=='post'],
             'measurement_file':str((target/'MEASUREMENTS.json').resolve().relative_to(ROOT)) if target.resolve().is_relative_to(ROOT) else str(target.name+'/MEASUREMENTS.json'),
             'sha256':sha(target/'MEASUREMENTS.json'),'seconds':result['elapsed_seconds']}
        index.append(row);put(a.output/'INDEX.json',{'configuration_sha256':sha(a.config),'cases':index})
        print(json.dumps(row),flush=True)

if __name__=='__main__':main()
