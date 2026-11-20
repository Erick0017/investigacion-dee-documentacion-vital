"""CPC5 extension: bounded simultaneous repertoire; no response lookup.

Experiences form moving directional relations through frozen v27.  Each lane
occupies a distinct z plane, with no prepared or emitted z direction.  The
auditor compares received fields only AFTER all native transitions.
"""
from __future__ import annotations
import argparse
import ctypes
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from common import sha,put,identity,record,interface,receipt,digest,operational,until,local_context
ROOT=HERE.parent
KEY='cpc5.extension.capacity.v1'


def moved(q,d,t,n): return tuple((q[i]+d[i]*t)%n for i in range(3))


def memory():
    class COUNTERS(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong),
                  ('PeakWorkingSetSize',ctypes.c_size_t),('WorkingSetSize',ctypes.c_size_t),
                  ('QuotaPeakPagedPoolUsage',ctypes.c_size_t),('QuotaPagedPoolUsage',ctypes.c_size_t),
                  ('QuotaPeakNonPagedPoolUsage',ctypes.c_size_t),('QuotaNonPagedPoolUsage',ctypes.c_size_t),
                  ('PagefileUsage',ctypes.c_size_t),('PeakPagefileUsage',ctypes.c_size_t)]
    value=COUNTERS();value.cb=ctypes.sizeof(value)
    kernel=ctypes.windll.kernel32;kernel.GetCurrentProcess.restype=ctypes.c_void_p
    ok=ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.c_void_p(kernel.GetCurrentProcess()),ctypes.byref(value),value.cb)
    return {'working_set_bytes':int(value.WorkingSetSize),'peak_working_set_bytes':int(value.PeakWorkingSetSize),'available':bool(ok)}


def geometry(case):
    n,k,gap=case['N'],case['K'],case['plane_gap']
    if type(n) is not int or not 31<=n<=151 or type(k) is not int or not 1<=k<=65:
        raise ValueError('Finite extension domain N31..151, K1..65')
    if type(gap) is not int or gap<2 or gap*k>n: raise ValueError('Distinct separated toroidal z planes required')
    tr=case.get('translation',[0,0,0]);forms=[];ports=[]
    for i in range(k):
        q=tuple((x+tr[j])%n for j,x in enumerate((30,30,1+i*gap)))
        name=f'L{i+1:02d}'
        forms.append({'index':i,'name':name,'hub':list(q)})
        ports.append(interface(name+'.signal',moved(q,(-1,0,0),-3,n),(-1,0,0)))
        for sign,label in ((1,'plus'),(-1,'minus')):
            dr=(1,sign,0);ports.append(interface(name+'.event.'+label,moved(q,dr,-3,n),dr))
    return {'N':n,'K':k,'plane_gap':gap,'translation':tr,'forms':forms,
            'scope':'K opaque forms, two physical y-direction content classes; NOT K semantic concepts',
            'z_wrapping_distance_min':min(gap,n-gap*(k-1))},ports


class CapacitySession:
    def __init__(self,world,spec,state): self.world=world;self.spec=spec;self.state=state
    @classmethod
    def create(cls,case):
        import dee_thinking as d
        spec,ports=geometry(case);recipe=d.OrganizationRecipe.research(spec['N'],[],0)
        recipe.interfaces=ports;recipe.execution=d.TickOptions(d.Backend.LAZY,1)
        return cls(d.OrganizationalWorld.create(recipe),spec,{'schema':1,'calls':[],'tick':0,'phase':0})
    def submit(self,form,label,payload,tick,probe=False):
        name=form+'.'+label;r=(self.world.probe if probe else self.world.submit)(name,payload,tick)
        row={'id':int(r.id),'port':name,'payload':payload,'requested_tick':tick,'call_tick':int(self.world.runtime.current_tick),
             'modality':'PHYSICAL_PROBE' if probe else 'EXPERIENCE_PROTOCOL'}
        self.state['calls'].append(row);return int(r.id)
    def save(self,path):
        path=Path(path)
        if path.exists():raise FileExistsError(path)
        self.state['tick']=int(self.world.runtime.current_tick)
        # Geometry/timing/calls only; never acquired class/expected answer.
        self.world.runtime.set_snapshot_metadata(KEY,json.dumps({'schema':1,'geometry':self.spec,'protocol':self.state},separators=(',',':')))
        self.world.save_snapshot(str(path));return {'file':path.name,'sha256':sha(path),'physical':digest(self.world)}
    @classmethod
    def load(cls,path):
        import dee_thinking as d
        world=d.OrganizationalWorld.load_snapshot(str(path));v=json.loads(world.runtime.snapshot_metadata(KEY))
        if v['schema']!=1 or v['protocol']['tick']!=world.runtime.current_tick:raise ValueError('Wrong session snapshot')
        spec=v['geometry'];expected={p.name for p in geometry({'N':spec['N'],'K':spec['K'],'plane_gap':spec['plane_gap'],'translation':spec['translation']})[1]}
        if set(world.runtime.channel_names)!=expected:raise ValueError('Interfaces changed')
        return cls(world,spec,v['protocol'])


def run_case(case,out):
    out=Path(out)
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);started=time.monotonic();engine=identity();session=CapacitySession.create(case)
    w,spec=session.world,session.spec;n=spec['N'];calls=session.state['calls'];lessons=[];reads=[];snapshots=[];contexts=[]
    signs=case.get('directions',[1 if i%3 else -1 for i in range(spec['K'])])
    if len(signs)!=spec['K'] or any(x not in (-1,1) for x in signs):raise ValueError('One physical environmental direction per form')
    mode=case.get('mode','paired');rounds=case.get('rounds',3);query=case.get('query_payload',5)
    if mode not in ('paired','unpaired','no_symbol','no_event'):raise ValueError('Frozen exposure protocol required')
    if not 1<=rounds<=5 or type(query) is not int or not 0<=query<=65535:raise ValueError('Finite query contract')
    put(out/'CONFIG.json',{'case':case,'geometry':spec,'source_sha256':sha(__file__),'engine':engine,
       'criterion_frozen':{'available':'Applied query, active semantic1 actual direction [-1,trained_y,0], s_reg>query',
                           'same_decoder_all_histories':True,'schedule':'all lessons at0, simultaneous query at N,2N,3N',
                           'no_semantic_count':'K forms; physical contents two directions; not K NSM meanings'}})
    snapshots.append(session.save(out/'INITIAL_T0.deetsnap'))
    for form,sign in zip(spec['forms'],signs):
        ids=[]
        if mode!='no_event':ids.append(session.submit(form['name'],'event.'+('plus' if sign==1 else 'minus'),11,0))
        if mode!='no_symbol':ids.append(session.submit(form['name'],'signal',5,int(mode=='unpaired')))
        lessons.append({'form':form['name'],'physical_event_y':sign,'receipt_ids':ids})
    until(w,3+int(mode=='unpaired'))
    for row,form in zip(lessons,spec['forms']):row['after_experience']=record(w,form['hub']);row['receipts']=[receipt(w,i) for i in row['receipt_ids']]
    snapshots.append(session.save(out/f'AFTER_ACQUISITION_T{int(w.runtime.current_tick)}.deetsnap'))
    for cycle in range(1,rounds+1):
        at=n*cycle+case.get('query_phase_offset',0);until(w,at);ids=[]
        for form in spec['forms']:ids.append(session.submit(form['name'],'signal',query,at,True))
        until(w,at+2)
        for form in (spec['forms'][0],spec['forms'][-1]):
            contexts.append({'round':cycle,'form':form['name'],'before_encounter':local_context(w,form['hub'])})
        until(w,at+3)
        for form,identifier in zip(spec['forms'],ids):
            observed=record(w,form['hub']);rr=receipt(w,identifier)
            valid=rr['status']=='applied' and observed['active'] and observed['semantic']==1 and observed['s_reg']>query and observed['direction'] in ([-1,1,0],[-1,-1,0])
            reads.append({'round':cycle,'form':form['name'],'input_tick':at,'tick':at+3,'input_payload':query,
                          'physical':observed,'receipt':rr,'decoded_y':observed['direction'][1] if valid else None,
                          'decoder_valid':valid,'origin':'ENTE'})
        snapshots.append(session.save(out/f'ROUND{cycle}_T{at+3}.deetsnap'))
        put(out/'PROGRESS.json',{'case':case,'lessons':lessons,'readouts':reads,'snapshots':snapshots})
    # Evaluator starts here, after trajectory; training directions never enter decoder.
    trained={r['form']:r['after_experience']['direction'][1] for r in lessons if r['after_experience']['active']}
    metrics={}
    for cycle in range(1,rounds+1):
        rows=[r for r in reads if r['round']==cycle]
        metrics[str(cycle)]={'queries':len(rows),'applied':sum(r['receipt']['status']=='applied' for r in rows),
          'decoder_valid':sum(r['decoder_valid'] for r in rows),'matches_physical_acquisition':sum(r['decoder_valid'] and r['decoded_y']==trained.get(r['form']) for r in rows),
          'rejected':sum(r['receipt']['status']=='rejected' for r in rows),'distinct_decoded_y':sorted({r['decoded_y'] for r in rows if r['decoded_y'] is not None})}
    final=digest(w);op=operational(w);restored=CapacitySession.load(out/snapshots[-1]['file'])
    equal=digest(restored.world)==final and operational(restored.world)==op
    result={'case':case,'status':'MEASURED','source_sha256':sha(__file__),'engine':engine,'geometry':spec,
       'modality':'EXPERIENCE_PROTOCOL then PHYSICAL_PROBE; native evolution between finite events',
       'preparations':1,'forks':0,'same_RUNTIME':True,'direct_RAW_writes_after_T0':0,'direct_clock_writes_after_T0':0,
       'calls':calls,'receipts':[receipt(w,r['id']) for r in calls],'lessons':lessons,'readouts':reads,'local_contexts':contexts,
       'calculations':metrics,'checkpoints':snapshots,'final':final,'operative_final':op,
       'technical':{'save_load_physical_and_operational_equal':equal,'no_answer_map_in_metadata':True},
       'resources':{'components':spec['K'],'initial_material':0,'interfaces':3*spec['K'],'basic_buffers_bytes':32*n**3,**memory()},
       'elapsed_seconds':time.monotonic()-started,'scope':spec['scope']}
    assert equal;put(out/'MEASUREMENTS.json',result)
    print(json.dumps({'id':case['id'],'metrics':metrics,'seconds':result['elapsed_seconds']}),flush=True);return result


def screen(config,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);rows=[]
    for case in config['cases']:
        target=out/case['id']
        if (target/'MEASUREMENTS.json').exists():m=json.loads((target/'MEASUREMENTS.json').read_text(encoding='utf-8'))
        else:m=run_case(case,target)
        rows.append({'case':case,'calculations':m['calculations'],'file':str((target/'MEASUREMENTS.json').relative_to(ROOT)),
                     'sha256':sha(target/'MEASUREMENTS.json'),'elapsed_seconds':m['elapsed_seconds']})
        put(out/'INDEX.json',{'configuration':config,'cases':rows})
    return rows


def continuation(snapshot,out,payload=9):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);identity();session=CapacitySession.load(snapshot)
    before=digest(session.world);before_op=operational(session.world);n=session.spec['N'];at=(before['tick']//n+1)*n
    until(session.world,at);ids=[]
    for form in session.spec['forms']:ids.append(session.submit(form['name'],'signal',payload,at,True))
    until(session.world,at+3)
    reads=[{'form':f['name'],'physical':record(session.world,f['hub']),'receipt':receipt(session.world,i)} for f,i in zip(session.spec['forms'],ids)]
    cp=session.save(out/'CONTINUED.deetsnap')
    result={'status':'MEASURED','source_sha256':sha(__file__),'parent':str(snapshot),'parent_sha256':sha(snapshot),'before':before,
        'before_operative':before_op,'after':digest(session.world),'readouts':reads,'checkpoint':cp,'scope':'Other-process same physical and operative session; no teaching map loaded'}
    put(out/'CONTINUATION.json',result);print(json.dumps({'continued':len(reads),'tick':result['after']['tick']}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['worker','screen','continue']);p.add_argument('--case',type=Path);p.add_argument('--config',type=Path);p.add_argument('--snapshot',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.command=='screen':screen(json.loads(a.config.read_text(encoding='utf-8')),a.out)
    elif a.command=='worker':run_case(json.loads(a.case.read_text(encoding='utf-8')),a.out)
    else:continuation(a.snapshot,a.out)
