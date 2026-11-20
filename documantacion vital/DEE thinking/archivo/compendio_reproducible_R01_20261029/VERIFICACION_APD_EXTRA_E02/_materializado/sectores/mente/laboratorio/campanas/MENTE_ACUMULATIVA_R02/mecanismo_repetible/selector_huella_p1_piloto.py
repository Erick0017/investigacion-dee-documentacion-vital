"""Two-level native selector pilot, new T0 N67, no host bank decision.
An earlier generic touch creates an XNOR history latch. A later identical zero
query meets a prepared local field whose gradient can emit X or Y. Both memory
routes and both signed gate resources are always available. The fixed observer
reads all four downstream gates, never the history latch or an expected bank.
"""
import gzip,hashlib,json,time
from pathlib import Path
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import encode_metadata,save_world_snapshot
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA_R02/mecanismo_repetible';OUT.mkdir(parents=True,exist_ok=True)
N=67;E=(33,33,33);D=(34,32,33);V=[(1,0,0),(0,1,0)]
def add(p,v,k=1):return tuple((p[i]+k*v[i])%N for i in range(3))
def put(p,x):
    if p.exists():raise FileExistsError(p)
    b=json.dumps(x,ensure_ascii=False,sort_keys=True).encode();p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
def design():
    # Missing XNOR partner is D+Z; its negative partner is prepared.
    offsets=[(0,0,-1),(-1,0,0),(1,0,0),(-1,0,-1),(1,0,1),(-1,-1,-1),(1,1,1)]
    prepared={add(D,v):0 for v in offsets}
    # Query spill terminator, paired about D to preserve the XNOR condition.
    prepared[add(E,(0,0,1))]=0;prepared[add(E,(2,-2,-1))]=0
    # Selector support outside D's Moore neighborhood, plus a fixed scalar1.
    prepared[add(E,(-1,1,1))]=0;prepared[add(E,(-1,1,-1))]=0;prepared[add(E,(-1,0,0))]=1
    if E in prepared or D in prepared:raise ValueError('Do not preload selector or history latch')
    placements=[]
    for pos,value in sorted(prepared.items()):
        p=d.InitialPlacement();p.site=d.Coordinate(*pos);p.raw=d.pack_record(1,value,0,0,0,4);p.clock=0;p.role='Prepared local geometry and fixed scalar offset; not acquired history';placements.append(p)
    recipe=d.OrganizationRecipe.research(N,placements,0);recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    return recipe,prepared
def run(label,touch=True,contents=(1,-1),query=True):
    recipe,frame=design();w=d.OrganizationalWorld.create(recipe);requests=[];rows=[]
    def obs(p):return exact_observation(w.runtime.observe(d.Coordinate(*p)))
    def send(name,site,v,t,value):
        if name not in set(w.runtime.channel_names):
            c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site);c.direction=d.Direction(*v);c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=True
            it=d.InterfaceSpec();it.name=name;it.channel=c;w.declare_interface(it)
        r=w.submit(name,value,t);requests.append({'id':int(r.id),'port':name,'site':site,'direction':v,'tick':t,'payload':value})
    def snapshot(name):
        w.runtime.set_snapshot_metadata('MA02.P1.SELECTOR.v1',encode_metadata({'label':label,'tick':int(w.runtime.current_tick),'N':N,'E':list(E),'D':list(D),'V':[list(v)for v in V],'requests':json.loads(json.dumps(requests)),'scope':'Operational interfaces and recorded interventions only; no target reader.'}))
        p=OUT/(label+'.'+name+'.deetsnap.gz');proof=save_world_snapshot(w,p,compress=True)
        return{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'proof':proof}
    initial=snapshot('T0')
    for i,(v,sign,t)in enumerate(zip(V,contents,(0,67))):
        h=add(E,v,3);cue=(0,1,0)if i==0 else(1,0,0);teacher=(-cue[0],-cue[1],sign)
        send('experience.cue.'+str(i),add(h,cue,-3),cue,t,5)
        send('experience.event.'+str(i)+'.'+str(sign),add(h,teacher,-3),teacher,t,11)
    if touch:
        P=add(D,(0,0,1));direction=(0,1,0)
        send('generic.touch',add(P,direction,-3),direction,10,0)
    if query:send('generic.current.query',add(E,(0,0,1),-3),(0,0,1),130,0)
    for i,v in enumerate(V):
        for sign in(-1,1):
            gate=add(add(E,v,4),(0,0,sign));direction=(-v[0],-v[1],0)
            send('generic.gate.'+str(i)+'.'+str(sign),add(gate,direction,-2),direction,136,7)
    for t in sorted({0,3,9,10,11,12,13,14,15,66,67,70,129,*range(130,146)}):
        w.run_until(t)
        rows.append({'tick':t,'history_latch':obs(D),'selector':obs(E),'native_routes':[obs(add(E,v,k))for v in V for k in(1,2,3)],'gates':[obs(add(add(E,v,4),(0,0,s)))for v in V for s in(-1,1)],'local_context':[obs(add(E,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
    read=next(r for r in rows if r['tick']==138);candidates=[]
    for p in read['gates']:
        if p['state']>0 and p['semantic']==1 and p['direction']in([0,0,-1],[0,0,1]):candidates.append({'site':p['site'],'sign':p['direction'][2]})
    final=snapshot('T145');result={'schema':'MA02.native_history_selector.pilot.1','identifier':label,'N':N,'new_T0':True,'history_touch':touch,'contents_for_evaluator_only':contents,'current_query':query,'preparation':[{'site':p,'s_reg':v}for p,v in sorted(frame.items())],'initial_snapshot':initial,'final_snapshot':final,'rows':rows,'read_tick':138,'candidates':candidates,'decoded_sign':candidates[0]['sign']if len(candidates)==1 else None,'receipts':[{**r,'receipt':exact_receipt(w.runtime.receipt(r['id']))}for r in requests],'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'New P0 geometry, acquired touch trace candidate selects X/Y access by native local gradient. No host observes latch to choose memory/marker routes. First-use finite pilot; policy learning/R2 and repeated retention not assumed.'}
    put(OUT/(label+'.json.gz'),result)
    print(json.dumps({'label':label,'latch14':next(r['history_latch']for r in rows if r['tick']==14),'selector134':next(r['selector']for r in rows if r['tick']==134),'candidates':candidates,'decoded':result['decoded_sign'],'statuses':[r['receipt']['status']for r in result['receipts']]},ensure_ascii=False),flush=True)
if __name__=='__main__':
    put(OUT/'PROTOCOLO_SELECTOR_HUELLA_P1.json',{'before_first_tick_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'hypothesis':'Generic past touch completes XNOR frame and leaves SEM7load1; later identical zero probe at E sees native gradient from D plus fixed counteranchor. No history -> +X; history -> +Y. Both query distinct acquired memory columns.','current_probe':'same source,direction,load0,timing130 in both histories; all both-sign gate resources for both banks at136, no host choice of bank','observer_frozen':'all four gates at138, accept unique pureZ SEM1 statepositive; no D/history/token/target in decoder','arms':'touch/omit, opposite acquired contents, no-current-query. Same initial anatomy and generic future resources.','criteria':'latch causally differs; selector X/Y and downstream memory use should follow native history; content permutation changes response without choosing another observer; noquery should not produce attributed current answer','horizon':145,'scope':'First pilot of two-level native P1, not P2/R2, perfect memory or integrated-main claim.'})
    run('MA02_P1_TOUCH');run('MA02_P1_NO_TOUCH',False);run('MA02_P1_OPPOSITE',True,(-1,1));run('MA02_P1_NO_QUERY',True,(1,-1),False)
