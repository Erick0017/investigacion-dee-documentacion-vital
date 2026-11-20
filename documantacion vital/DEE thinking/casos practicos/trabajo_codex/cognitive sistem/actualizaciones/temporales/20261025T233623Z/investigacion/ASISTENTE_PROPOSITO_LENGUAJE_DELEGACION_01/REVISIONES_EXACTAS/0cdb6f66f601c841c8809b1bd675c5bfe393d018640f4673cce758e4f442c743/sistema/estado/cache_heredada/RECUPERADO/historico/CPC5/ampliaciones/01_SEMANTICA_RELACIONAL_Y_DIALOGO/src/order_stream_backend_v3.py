"""Native relative-order stream -> later opaque sign -> query -> current context.

Two fixed branches are stimulated equally; neither branch nor decoder reads the
history label to select an answer. The field guide is an explicit prepared
support and can change the write gate: this is a new geometry, not the old body.
"""
from pathlib import Path
import argparse
import json
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha,identity,interface,record,receipt,digest,operational,local_context,gate
from semantic_relations import PA,PB

N=67
KEY='cpc5.extension.order_stream.v1'

def prepare(case):
    import dee_thinking as d
    shift=case.get('translation',[0,0,0]);add=lambda q,v:tuple((q[i]+v[i])%N for i in range(3))
    c=add((33,25,33),shift);a=add(c,(-1,0,0));b=add(c,(1,0,0));ps=[];used=set()
    def place(q,state,load,sem,clock):
        if q in used:raise ValueError('Overlapping support')
        used.add(q);p=d.InitialPlacement();p.site=d.Coordinate(*q);p.raw=d.pack_record(state,load,0,0,0,sem);p.clock=clock;p.role='Declared fresh order body';ps.append(p)
    phase=case.get('initial_phase',260)
    place(a,1000,100,1,phase);place(b,2000,100,1,phase)
    for q,pattern,state,clock in ((a,PA,3000,31),(b,PB,4000,41)):
        for i,v in enumerate(pattern):place(add(q,v),state+i,0,4,clock+i)
    place(add(c,(0,0,1)),6100,7,4,19)
    ports=[interface('event.A',add(a,(0,-1,0)),(0,-1,0),state=5000),interface('event.B',add(b,(0,1,0)),(0,1,0),state=5001),interface('order.read',add(c,(0,-1,0)),(0,1,0))]
    names={};query={};contexts={};nameoffset=case.get('name_offpath_z',0)
    for sign,label in ((-1,'left'),(1,'right')):
        names[label]=add(c,(10*sign,-11,0));query[label]=add(c,(20*sign,-21,10));contexts[label]=add(c,(30*sign,-31,20))
        ports.append(interface('name.'+label,add(names[label],(0,0,-3+nameoffset)),(0,0,1)))
        ports.append(interface('query.'+label,add(query[label],(0,0,-3)),(0,0,1)))
        for context in (-1,1):ports.append(interface('context.'+label+('.plus' if context==1 else '.minus'),add(contexts[label],(0,0,-3*context)),(0,0,context)))
    backend=getattr(d.Backend,case.get('backend','LAZY'))
    recipe=d.OrganizationRecipe.research(N,ps,0);recipe.interfaces=ports;recipe.execution=d.TickOptions(backend,2 if backend==d.Backend.DENSE_PARALLEL else 1)
    spec={'N':N,'center':c,'A':a,'B':b,'name_hubs':names,'query_sites':query,'context_sites':contexts,
          'prepared_sites':len(ps),'interfaces':[p.name for p in ports],
          'reference_frame':'Declared event ports A/B and fixed laboratory axes, not deictic human participants',
          'prepared_function':'Relative-order body with guide, two equal-dose name branches and two context opportunities; no learned target in placements'}
    return d.OrganizationalWorld.create(recipe),spec

def run_case(case,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);start=time.monotonic();w,s=prepare(case);calls=[];rows=[];snaps=[];windows=[]
    identity_value=identity();put(out/'CONFIG.json',{'case':case,'geometry':s,'source_sha256':sha(__file__),
         'criterion':'Record retained A/B relation, native branches, named-route access above isolated query load and full directional context outcome; no classification supplied to world',
         'decoder':'Native active semantic1 product with nonzero dx at declared query sites; preserve direction vector and load, null otherwise',
         'scope':'Operational order discrimination with a phase-prepared sensor, subsequent fixed opaque sign experience; not arbitrary names or full ANTES/YO/TU semantics'})
    def submit(port,load,tick,kind='submit',origin='CURRENT_EVENT'):
        r=getattr(w,kind)(port,load,tick);calls.append({'id':int(r.id),'port':port,'payload':load,'requested_tick':tick,'call_tick':w.runtime.current_tick,'kind':kind,'origin':origin})
    onset=case.get('onset',0)
    if not case.get('history_omitted'):
        for i,letter in enumerate(case.get('history','AB')):submit('event.'+letter,case.get('event_load',3),onset+i*case.get('gap',1))
    if not case.get('reader_omitted'):submit('order.read',case.get('reader_load',7),onset+case.get('read_at',2),'probe','COMMON_ORDER_PHYSICAL_READOUT')
    if case.get('name_mode','paired')!='omitted':
        for label in s['name_hubs']:submit('name.'+label,case.get('name_load',5),onset+case.get('name_tick',12),origin='SAME_OPAQUE_SIGN_AFTER_NATIVE_ORDER_PHASE')
    for tick in case.get('query_ticks',[22,89]):
        for label in s['query_sites']:submit('query.'+label,case.get('query_load',5),onset+tick,'probe','SIGN_ALONE_EQUAL_BRANCH_STIMULATION')
    ctx=case.get('context',0)
    if ctx:
        for label in s['context_sites']:submit('context.'+label+('.plus' if ctx==1 else '.minus'),case.get('context_load',3),onset+case.get('context_tick',32),origin='CURRENT_CONTEXT_DIRECTION_ONLY')
    for tick in case.get('later_order_reads',[]):submit('order.read',case.get('reader_load',7),tick,'probe','ORDER_REUSE_WITHOUT_RETEACHING')
    def snap(label):
        w.runtime.set_snapshot_metadata(KEY,json.dumps({'schema':1,'tick':w.runtime.current_tick,'geometry':s,'input_ids':[c['id'] for c in calls]},separators=(',',':')))
        path=out/(label+'.deetsnap');w.save_snapshot(str(path));snaps.append({'file':path.name,'sha256':sha(path),'physical':digest(w),'operative':operational(w)})
    snap('INITIAL_T0');horizon=case.get('horizon',100)
    boundaries=set(range(0,12))|{12,13,14,15,16,22,23,24,25,26,27,32,33,34,35,36,37,67,68,69,70,71,74,89,90,91,92,93,94,100}
    events=[onset+case.get('read_at',2)+i for i in range(0,5)]
    events += [onset+case.get('name_tick',12)+i for i in range(0,5)]
    events += [onset+t+i for t in case.get('query_ticks',[22,89]) for i in range(0,5)]
    events += [onset+case.get('context_tick',32)+i for i in range(0,5)] if ctx else []
    boundaries={t+onset for t in boundaries if t+onset<=horizon}|{horizon}|{t for t in events if t<=horizon}
    for tick in sorted(boundaries):
        w.run_until(tick);ar,br=record(w,s['A']),record(w,s['B'])
        row={'tick':tick,'A':ar,'B':br,'delta':ar['s_reg']-br['s_reg'] if ar['active'] and br['active'] else None,
             'comparator':record(w,s['center']),
             'names':{k:record(w,q) for k,q in s['name_hubs'].items()},'queries':{k:record(w,q) for k,q in s['query_sites'].items()},
             'context':{k:record(w,q) for k,q in s['context_sites'].items()}}
        row['decoded_name_response']={k:{'dx':r['direction'][0],'dy':r['direction'][1],'dz':r['direction'][2],'load':r['s_reg'],'raw':r['raw']} if r['active'] and r['semantic']==1 and r['direction'][0]!=0 else None for k,r in row['queries'].items()}
        rows.append(row)
        if tick-onset in (3,4,5,14,15,16,24,25,26,34,35,36):
            windows.append({'tick':tick,'comparator':local_context(w,s['center']),
                    'name':{k:local_context(w,q) for k,q in s['name_hubs'].items()},
                    'query':{k:local_context(w,q) for k,q in s['query_sites'].items()},
                    'context':{k:local_context(w,q) for k,q in s['context_sites'].items()},'guard_A':gate(w,s['A']),'guard_B':gate(w,s['B'])})
        if tick-onset in (4,16,26,36) or tick==horizon:snap('T'+str(tick))
        put(out/'INCREMENTAL.json',{'tick':tick,'rows':rows})
    result={'schema':'CPC5.extension.order_stream.measurements.v1','case':case,'engine':identity_value,'geometry':s,
            'calls':calls,'receipts':[receipt(w,c['id']) for c in calls],'rows':rows,'local_windows':windows,'snapshots':snaps,
            'final_physical':digest(w),'final_operative':operational(w),'external_operations':list(w.external_operations),
            'post_T0_host_RAW_clock_edits':[],'preparations':1,'elapsed_seconds':time.monotonic()-start,
            'coverage':'Fixed observed points and encounter windows; no unique genealogy asserted beyond observed native segments'}
    put(out/'MEASUREMENTS.json',result);print(json.dumps({'id':case['id'],'seconds':result['elapsed_seconds'],'final_delta':rows[-1]['delta']}),flush=True);return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    for case in json.loads(args.config.read_text(encoding='utf-8'))['cases']:
        target=args.output/case['id']
        if (target/'MEASUREMENTS.json').exists():continue
        run_case(case,target)

if __name__=='__main__':main()
