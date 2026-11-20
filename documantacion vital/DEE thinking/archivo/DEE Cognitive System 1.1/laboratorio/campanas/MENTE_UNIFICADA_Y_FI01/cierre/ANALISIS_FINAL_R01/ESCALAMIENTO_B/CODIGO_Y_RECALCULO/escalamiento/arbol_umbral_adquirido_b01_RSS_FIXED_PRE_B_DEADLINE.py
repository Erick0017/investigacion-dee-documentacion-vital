"""B01 candidate only. Native creation is gated behind the real block-A close.

All inputs remain separate raw physical carriers. Two root products meet with
opposite directions at ONE ephemeral current-datum port, then a fixed native
reader uses two separately acquired scalar memories. Python never injects their
sum or computes the reader's decision. No physics has validated this candidate
merely because this module parses or its offline plan has no direct crossings.
"""
from __future__ import annotations
import argparse,ctypes,gzip,hashlib,json,os,sys,time
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from preflight_arbol_crudo import forest
LAB=HERE.parent
ROOT=LAB.parents[2]
SYSTEM=ROOT/'sistema'
KEY='DEE.Cognitive.System.1.1.FI01.B01.tree_acquired_threshold.v1'
REVISION='B01.candidate.native_total_and_acquired_ephemeral_reference.1'
DEADLINE=datetime.fromisoformat('2026-10-26T01:49:35+00:00')
RSS_LIMIT=512*1024**2

def rss(peak=False):
    if os.name!='nt':return None
    class P(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('faults',ctypes.c_ulong),('peak_ws',ctypes.c_size_t),('ws',ctypes.c_size_t),('peak_pool',ctypes.c_size_t),('pool',ctypes.c_size_t),('peak_nonpool',ctypes.c_size_t),('nonpool',ctypes.c_size_t),('pagefile',ctypes.c_size_t),('peak_pagefile',ctypes.c_size_t)]
    p=P();p.cb=ctypes.sizeof(P)
    proc=ctypes.windll.kernel32.GetCurrentProcess
    proc.restype=ctypes.c_void_p;proc.argtypes=[]
    query=ctypes.windll.psapi.GetProcessMemoryInfo
    query.argtypes=[ctypes.c_void_p,ctypes.POINTER(P),ctypes.c_ulong];query.restype=ctypes.c_int
    okay=query(proc(),ctypes.byref(p),p.cb)
    return int(p.peak_ws if peak else p.ws)if okay else None

def memory_guard(limit=RSS_LIMIT):
    value=rss(peak=True)
    if value is not None and value>limit:raise MemoryError('B01 measured process RSS exceeds bounded technical budget; not a cognitive failure: '+str(value))
    if datetime.now(timezone.utc)>=DEADLINE:raise TimeoutError('Original total campaign deadline reached; no new B ticks')
    return value

def internal_A_close(path):
    """Must run BEFORE importing DEE, creating or restoring any Runtime."""
    if not path.is_file():raise RuntimeError('BLOCK_A_NOT_CLOSED: preserve A first; no B Runtime created')
    data=json.loads(path.read_text(encoding='utf-8'))
    if data.get('bloque_A_cerrado')is not True and data.get('block_A_closed')is not True:raise RuntimeError('BLOCK_A_NOT_CLOSED: true close flag absent; no B Runtime created')
    if data.get('block',data.get('bloque','A'))!='A':raise RuntimeError('Wrong internal block close')
    memory_guard()
    return {'path':str(path.resolve()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'close_flag_verified_before_native_import':True}

def plan(level,N=67):
    if N<67 or N>131:raise ValueError('Declared new-world dimension67..131 only')
    p=forest(level,N);opened=set();sources=[];turns=[];nodes=[]
    def trans(site,side):
        x,y,z=site
        return(x,y,z+1)if side=='left'else(x,y,N-5-z)
    def direction(v,side):return list(v)if side=='left'else[v[0],v[1],-v[2]]
    for q in p['raw_sources']:
        side=q['side'];site=trans(q['site'],side);sources.append({**q,'site':list(site),'direction':direction(q['direction'],side),'head':list(trans(q['head'],side))})
    for q in p['zero_resources']:
        side=q['id'].split('.')[0];turns.append({**q,'site':list(trans(q['site'],side)),'direction':direction(q['direction'],side)})
    for q in p['nodes']:
        side=q['id'].split('.')[0];nodes.append({**q,'site':list(trans(q['site'],side))})
    # Root-to-datum route: two fixed zero turns, then pure horizontal arrivals.
    routes=[]
    for side,root,dz,dy,dx in [('left',(16,16,17),-1,1,1),('right',(50,50,N-21),1,-1,-1)]:
        J=(root[0],root[1],root[2]+2*dz)
        H=(root[0],33,N-2)
        v=(0,dy,dz);r=(dx,-dy,-dz)
        turns.extend([
          {'id':side+'.root.turnY','site':[(J[i]-v[i])%N for i in range(3)],'direction':list(v),'injection_tick_relative':1,'payload':0},
          {'id':side+'.root.turnX','site':[(H[i]-r[i])%N for i in range(3)],'direction':list(r),'injection_tick_relative':18,'payload':0}])
        for k in range(3):opened.add(tuple((root[i]+k*(0,0,dz)[i])%N for i in range(3)))
        for k in range(18):opened.add(tuple((J[i]+k*v[i])%N for i in range(3)))
        for k in range(18):opened.add(((H[0]+k*dx)%N,33,N-2))
        routes.append({'side':side,'root':list(root),'turnY':list(J),'turnX':list(H),'root_tick':0,'turnY_tick':2,'turnX_tick':19,'datum_tick':36,'final_direction':[dx,0,0]})
    for side in('left','right'):
        for site in p['opened']:
            # The two compact forests are separated by X, so infer side directly.
            if(side=='left'and site[0]<33)or(side=='right'and site[0]>33):opened.add(trans(site,side))
    for q in sources+turns:opened.add(tuple(q['site']))
    Q=(32,34,N-3);M=[(31,35,N-2),(33,35,N-2)];datum=(33,33,N-2)
    anchors={}
    def rel(v):return tuple((Q[i]+v[i])%N for i in range(3))
    for v,load in[((-1,0,1),2),((0,0,1),0),((1,0,1),0)]:anchors[rel(v)]=(load,(0,0,0))
    for sign in(-1,1):
        for v in((2*sign,1,1),(2*sign,2,1),(sign,2,1),(0,2,1)):anchors[rel(v)]=(0,(0,0,0))
    opened.update([Q,datum,*M])
    for sign in(-1,0,1):opened.add(rel((sign,-1,-1)))
    conflicts=[list(x)for x in anchors if x in opened]
    if conflicts:raise ValueError('Planned route crosses prepared comparator support: '+repr(conflicts))
    ports={};duplicates=[]
    for q in sources+turns:
        key=(tuple(q['site']),q['injection_tick_relative'])
        if key in ports:duplicates.append([ports[key],q['id']])
        ports[key]=q['id']
    if duplicates:raise ValueError('Duplicate physical input scheduling: '+repr(duplicates))
    g={'schema':'FI01.B01.tree_ephemeral_candidate.v1','revision':REVISION,'N':N,'level':level,'Q':list(Q),'memories':list(map(list,M)),'datum_site':list(datum),'raw_sources':sources,'generic_sources':turns,'nodes':nodes,'root_routes':routes,
       'anchors':[{'site':list(k),'load':v[0],'direction':list(v[1])}for k,v in sorted(anchors.items())],'opened':list(map(list,sorted(opened))),
       'leaf_relative_tick':p['raw_injection_ticks'][0],'datum_relative_tick':36,'planned_input_to_datum_ticks':36-p['raw_injection_ticks'][0],
       'not_proven':'Transport, output cone, exact learned threshold, repeated use, native integration or scaling.'}
    return g

def native_imports():
    sys.path.insert(0,str(SYSTEM))
    import dee_thinking as d
    from dee_thinking.persistence import encode_metadata,decode_metadata
    from app.lives import Store,WorldAdapter,now
    from app.native_tools import physical
    from capacidades import arquitectura_distribuida_mi02_r8 as body
    from capacidades import comparacion_efimera_mi02 as ep
    return d,encode_metadata,decode_metadata,Store,WorldAdapter,now,physical,body,ep

def recipe(g,d,boundary):
    opened=set(map(tuple,g['opened']));anchors={tuple(q['site']):(q['load'],tuple(q['direction']))for q in g['anchors']};ps=[]
    N=g['N'];inert=d.pack_record(0,0,0,0,0,4)
    for x in range(N):
        for y in range(N):
            for z in range(N):
                site=(x,y,z)
                if site in opened and site not in anchors:continue
                if boundary=='sparse'and site not in anchors:continue
                q=d.InitialPlacement();q.site=d.Coordinate(*site);q.clock=0
                q.raw=d.pack_record(1,anchors[site][0],*anchors[site][1],4)if site in anchors else inert
                q.role='Declared fixed comparator support'if site in anchors else'Inert SEM4 T0 boundary, not free learned memory'
                ps.append(q)
                if len(ps)%8192==0:memory_guard(RSS_LIMIT-48*1024**2)
    r=d.OrganizationRecipe.research(N,ps,0);r.execution=d.TickOptions(d.Backend.LAZY,1);memory_guard();return r

def read_meta(a,decode):
    e=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in e:raise ValueError('Actual B01 complete learned state required, no reconstruction fallback')
    return decode(e[KEY])

def frame(a,values,ni):
    d,encode,decode,Store,Adapter,now,physical,body,ep=ni
    s=read_meta(a,decode);g=s['geometry'];n=g['level']
    if len(values)!=n or any(type(x)is not int or not 0<=x<=32 for x in values):raise ValueError('One independent raw scalar0..32 per declared interface')
    start=a.tick;leaf_at=start+2;root_at=leaf_at-g['leaf_relative_tick'];datum_at=root_at+g['datum_relative_tick'];requests=[]
    for q in g['raw_sources']:
        requests.append(body.send(a,'FI01.B01.'+q['id'],q['site'],q['direction'],root_at+q['injection_tick_relative'],values[q['component_index']]))
    for q in g['generic_sources']:requests.append(body.send(a,'FI01.B01.'+q['id'],q['site'],q['direction'],root_at+q['injection_tick_relative'],0))
    requests.append(body.send(a,'FI01.B01.ephemeral_probe',g['Q'],(0,0,-1),datum_at,0))
    schedule=sorted(set([leaf_at-1,leaf_at,*[root_at+q['join_tick_relative']+dt for q in g['nodes']for dt in(-1,0,1)],root_at+2,root_at+19,datum_at-1,datum_at,datum_at+1,datum_at+2]))
    points={'Q':g['Q'],'datum':g['datum_site'],'memory0':g['memories'][0],'memory1':g['memories'][1]}
    points.update({q['id']:q['site']for q in g['nodes']})
    for q in g['root_routes']:
        points[q['side']+'.root.turnY']=q['turnY'];points[q['side']+'.root.turnX']=q['turnX']
    rows=[]
    for t in schedule:
        if t<start:continue
        memory_guard();a.run_until(t);rows.append({'tick':int(a.tick),'fields':{name:body.obs(a,p)for name,p in points.items()}})
    response=next(x['fields']['Q']for x in rows if x['tick']==datum_at+1)
    command=(1 if response['direction'][0]>=0 else-1)if body.qualified(response)else None
    # Fixed declared settling includes at least one full periodic crossing scale.
    a.run_until(max(datum_at+5,leaf_at+2*g['N']));memory_guard()
    s['frames']+=1;s['last_frame_end']=int(a.tick);a.world.runtime.set_snapshot_metadata(KEY,encode(s))
    return {'raw_components':values,'requested_components':n,'start_tick':start,'leaf_tick':leaf_at,'root_tick':root_at,'datum_tick':datum_at,'fixed_read_tick':datum_at+1,'formed_native_command':command,'response':response,'frames':rows,'requests':body.receipts(a,requests),'final_reference_fields':[body.obs(a,p)for p in g['memories']],'end_tick':int(a.tick),
       'assistance':'Prepared tree, raw per-port codec, generic zero turns and probe. No host sum, bank or desired action in native input; native usefulness must be evaluated separately.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=('plan','create','frames'),required=True);ap.add_argument('--level',type=int,choices=(8,16,32,64,128),default=8);ap.add_argument('--N',type=int,default=67);ap.add_argument('--life');ap.add_argument('--boundary',choices=('dense','sparse'),default='dense');ap.add_argument('--training',default='[74,12]');ap.add_argument('--observations');ap.add_argument('--out',type=Path,required=True);ap.add_argument('--cierre-interno-a',type=Path,default=LAB/'CIERRE_INTERNO_A.json');args=ap.parse_args()
    if args.out.exists():raise FileExistsError(args.out)
    if args.mode=='plan':
        result={'classification':'OFFLINE_CANDIDATE_NOT_NATIVE_EXECUTION','native_ticks':0,'geometry':plan(args.level,args.N)}
    else:
        authorization=internal_A_close(args.cierre_interno_a)
        os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
        ni=native_imports();d,encode,decode,Store,Adapter,now,physical,body,ep=ni;store=Store()
        if not args.life:raise ValueError('Explicit new or existing candidate life required')
        if args.mode=='create':
            if store.life_dir(args.life).exists():raise FileExistsError('Life exists: continue or fork it, never rebuild')
            values=json.loads(args.training)
            if len(values)!=2 or any(type(v)is not int or not 0<=v<=160 for v in values):raise ValueError('Two explicit bounded raw scalar teaching experiences')
            g=plan(args.level,args.N);r=recipe(g,d,args.boundary);memory_guard();a=Adapter(d.OrganizationalWorld.create(r));memory_guard()
            rec={'schema':'DCS1.1.life.v1','life_id':args.life,'world_id':args.life,'profile':'fisica_directa','branch':'NEW_PREPARATION_T0','parent':None,'created_utc':now(),'parameters':{'N':args.N,'architecture':REVISION,'level':args.level,'boundary':args.boundary},'knowledge':'New T0, raw teaching only after untrained checkpoint. No R9/U0/MA02 learned fields imported.','memberships':[{'id':args.life,'role':'Native aggregation and acquired relative reference in one world, not multiple views as independent matter'}]}
            with store.writer(args.life):untrained=store.commit(rec,a,{'kind':'FI01_B01_NEW_T0','authorization':authorization})
            def teach(a):
                result=ep.acquire(a,geometry=g,values=values)
                a.world.runtime.set_snapshot_metadata(KEY,encode({'revision':REVISION,'geometry':g,'frames':0,'boundary':args.boundary,'reader_never_uses_training_history':True}))
                return result
            learned=store.mutate(args.life,'FI01_B01_RAW_REFERENCE_ACQUISITION',teach,details={'raw_scalar_experiences':values,'not_an_expected_action':True})
            result={'authorization':authorization,'untrained':untrained,'learned':learned,'current_rss_bytes':rss(),'peak_rss_bytes':rss(peak=True)}
        else:
            values=json.loads(args.observations or'null')
            if not isinstance(values,list)or not 1<=len(values)<=32:raise ValueError('One to32 raw frames')
            result=store.mutate(args.life,'FI01_B01_NATIVE_FRAMES',lambda a:{'rows':[frame(a,v,ni)for v in values]},details={'independent_raw_frames':values,'authorization':authorization,'no_host_aggregate_in_inputs':True})
    result={'revision':REVISION,'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'geometry_generator_sha256':hashlib.sha256((HERE/'preflight_arbol_crudo.py').read_bytes()).hexdigest(),'result':result}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with gzip.open(args.out,'wt',encoding='utf-8',compresslevel=6)as f:json.dump(result,f,ensure_ascii=False,allow_nan=False)
    print(json.dumps({'output':str(args.out),'mode':args.mode,'physical_execution':args.mode!='plan','revision':REVISION},ensure_ascii=True))
if __name__=='__main__':main()
