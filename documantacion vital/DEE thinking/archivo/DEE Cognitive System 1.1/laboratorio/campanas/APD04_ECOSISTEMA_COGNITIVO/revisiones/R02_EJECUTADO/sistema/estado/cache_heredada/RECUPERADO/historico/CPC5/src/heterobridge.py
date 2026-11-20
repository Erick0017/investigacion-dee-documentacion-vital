"""New finite cross-family candidate: acquired mobile wave reads fresh A/B.

No preset supplies a learned history. All four teaching events are submitted
through declared interfaces. A missing or altered output remains a measurement.
"""
from pathlib import Path
import argparse
import json
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,identity,put,sha,record,local_context,gate,digest,interface,receipt
from heterogeneous import PA,PB

N=47


def prepare(case):
    import dee_thinking as d
    add=lambda q,v:tuple((q[i]+v[i])%N for i in range(3))
    c=add((25,25,25),case.get('translation',[0,0,0]))
    a=add(c,(-1,0,0));b=add(c,(1,0,0));placements=[];occupied=set()
    def place(q,state,load,sem=4,clock=0):
        if q in occupied:raise ValueError('overlapping material')
        occupied.add(q);p=d.InitialPlacement();p.site=d.Coordinate(*q)
        p.raw=d.pack_record(state,load,0,0,0,sem);p.clock=clock;p.role='Declared fresh relative body support';placements.append(p)
    place(a,1000,100,1,260);place(b,2000,100,1,260)
    for q,pat,s,clock in ((a,PA,3000,31),(b,PB,4000,41)):
        for i,delta in enumerate(pat):place(add(q,delta),s+i,0,4,clock+i)
    ports=[interface('body.A',add(a,(0,-1,0)),(0,-1,0),state=5000),
           interface('body.B',add(b,(0,1,0)),(0,1,0),state=5001)]
    hub=add(c,(0,-3,6 if case.get('offpath') else 0))
    for label,direction in (('cue',(-1,0,0)),('report',(1,1,0))):
        source=tuple((hub[i]-3*direction[i])%N for i in range(3))
        ports.append(interface('mobile.'+label,source,direction))
    recipe=d.OrganizationRecipe.research(N,placements,0);recipe.interfaces=ports
    recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    spec={'N':N,'A':a,'B':b,'comparator':c,'reader_site':add(c,(0,-1,0)),'mobile_hub':hub,
          'mobile_nominal_direction':[0,1,0],'prepared_reader_source':False,'prepared_sites':10,
          'scope':'Geometry intentionally routes the emitted mobile relation to the relative reader; acquired response must be measured'}
    return d.OrganizationalWorld.create(recipe),spec


def run_case(case,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);started=time.monotonic();engine=identity()
    world,spec=prepare(case);calls=[];rows=[];windows=[];saved=[]
    put(out/'CONFIG.json',{'case':case,'geometry':spec,'source_sha256':sha(__file__),
            'criterion':'First observe learned mobile product, reader arrival, relative delta and changed output direction under fixed interface; no output forced or calculated',
            'horizon':20})
    for i,letter in enumerate(case['history']):
        r=world.submit('body.'+letter,3,i);calls.append({'id':r.id,'port':'body.'+letter,'payload':3,'requested_tick':i,'call_tick':0})
    loads=case.get('mobile_loads',[5,7])
    if len(loads)!=2 or any(type(x) is not int or not 0<=x<=65535 for x in loads):raise ValueError('Two uint16 mobile experience loads required')
    for name,payload,tick in (('mobile.cue',loads[0],int(case.get('unpaired',False))),('mobile.report',loads[1],0)):
        r=world.submit(name,payload,tick);calls.append({'id':r.id,'port':name,'payload':payload,'requested_tick':tick,'call_tick':0})
    for tick in range(21):
        world.run_until(tick);a,b=record(world,spec['A']),record(world,spec['B'])
        target=tuple((spec['mobile_hub'][i]+max(0,tick-3)*[0,1,0][i])%N for i in range(3))
        row={'tick':tick,'A':a,'B':b,'delta':a['s_reg']-b['s_reg'] if a['active'] and b['active'] else None,
             'reader':record(world,spec['reader_site']),'comparator':record(world,spec['comparator']),
             'nominal_mobile_segment':record(world,target)}
        rows.append(row)
        if tick in (2,3,4,5,6,7,8):
            windows.append({'tick':tick,'comparator_context':local_context(world,spec['comparator']),
                  'mobile_context':local_context(world,spec['mobile_hub']),
                  'gate_A':gate(world,spec['A']),'gate_B':gate(world,spec['B'])})
        if tick in (0,2,4,8,20):
            name=f'T{tick}.deetsnap';world.save_snapshot(str(out/name));saved.append({'file':name,'sha256':sha(out/name),'physics':digest(world)})
        put(out/'INCREMENTAL.json',{'rows':rows,'last_tick':tick})
    result={'schema':'CPC5.heterogeneous_bridge.measurements.v1','case':case,'engine':engine,'geometry':spec,
            'calls':calls,'receipts':[receipt(world,x['id']) for x in calls],'rows':rows,'local_transition_windows':windows,
            'snapshots':saved,'physics':digest(world),'external_operations':list(world.external_operations),
            'host_RAW_clock_writes_after_T0':[],'preparations':1,'elapsed_seconds':time.monotonic()-started,
            'scope':'New cross-family candidate. Passive records and actual differences, not inherited guarantees or a new general cognitive capacity.'}
    put(out/'MEASUREMENTS.json',result);return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    index=[];a.output.mkdir(parents=True,exist_ok=True)
    for case in json.loads(a.config.read_text(encoding='utf-8'))['cases']:
        target=a.output/case['id']
        result=json.loads((target/'MEASUREMENTS.json').read_text(encoding='utf-8')) if (target/'MEASUREMENTS.json').exists() else run_case(case,target)
        row={'id':case['id'],'final_delta':result['rows'][-1]['delta'],
             'active_comparator':[x for x in result['rows'] if x['comparator']['active']],
             'measurement':str((target/'MEASUREMENTS.json').resolve().relative_to(ROOT)) if target.resolve().is_relative_to(ROOT) else str(target.name+'/MEASUREMENTS.json'),
             'sha256':sha(target/'MEASUREMENTS.json'),'elapsed_seconds':result['elapsed_seconds']}
        index.append(row);put(a.output/'INDEX.json',{'cases':index,'configuration_sha256':sha(a.config)});print(json.dumps(row),flush=True)

if __name__=='__main__':main()
