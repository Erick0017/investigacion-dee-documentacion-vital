"""New T0 candidate: four acquired paths, one sensory site, two common outputs.
Fixed token->incoming direction is apparatus, NOT a learned routing policy.
All candidate output-turn resources are supplied, regardless of stored signs.
"""
import gzip,hashlib,json,os,time
from pathlib import Path
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import encode_metadata,save_world_snapshot
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA/mecanismo';OUT.mkdir(parents=True,exist_ok=True)
N=31;I=(15,15,15);V=[(1,0,0),(0,1,0),(-1,0,0),(0,-1,0)]
def add(a,b,k=1):return tuple((a[j]+k*b[j])%N for j in range(3))
def vec(v,z):return(v[0],v[1],z)
def put(p,x):
    if p.exists():raise FileExistsError(p)
    b=json.dumps(x,ensure_ascii=False,sort_keys=True).encode();p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
def run(label,signs):
    recipe=d.OrganizationRecipe.research(N,[],0);recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    w=d.OrganizationalWorld.create(recipe);requests=[];rows=[]
    def send(name,p,v,value,t):
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*p);c.direction=d.Direction(*v)
        c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=True
        it=d.InterfaceSpec();it.name=name;it.channel=c
        if name not in set(w.runtime.channel_names):w.declare_interface(it)
        r=w.submit(name,value,t);requests.append({'id':int(r.id),'name':name,'site':list(p),'direction':list(v),'value':value,'tick':t});return r
    def obs(p):return exact_observation(w.runtime.observe(d.Coordinate(*p)))
    def snap(t):
        w.runtime.set_snapshot_metadata('MA.COMMON.ROUTER.v1',encode_metadata({'label':label,'N':N,'I':list(I),'V':[list(v)for v in V],'requests':requests,'rows':rows,'tick':t,'source':'new T0; no trained EO memories'}))
        p=OUT/(label+'.T'+str(t)+'.deetsnap.gz');proof=save_world_snapshot(w,p,compress=True);return{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'proof':str(proof)}
    initial=snap(0)
    def teach(i,sign,t):
        v=V[i];h=add(I,v,3);ev=vec(tuple(-x for x in v),sign)
        send('common.token.'+str(i),I,v,5,t)
        if sign is not None:send('experience.'+str(i)+'.'+str(sign),add(h,ev,-3),ev,11,t)
        w.run_until(t+3);rows.append({'kind':'teach','i':i,'sign':sign,'tick':t+3,'hub':obs(h)})
    def query(i,t):
        v=V[i];h=add(I,v,3)
        send('common.token.'+str(i),I,v,5,t)
        # Supply both signs/all four routes: no host branch on stored content.
        for j,u in enumerate(V):
            for sg in (-1,1):
                target=add(add(I,u,4),(0,0,sg))
                for k,z in enumerate((-1,1)):
                    r=vec(tuple(-x for x in u),z);distance=1+(int(sg==-1 and z==-1))
                    send('generic.'+str(j)+'.'+str(sg)+'.'+str(z),add(target,r,-distance),r,0,t+4-distance)
        w.run_until(t+3);pre=obs(h)
        w.run_until(t+4);turn=obs(add(add(I,v,4),(0,0,signs[i] or 1)))
        w.run_until(t+8);out={str(sg):obs(add(I,(0,0,sg),5))for sg in(-1,1)}
        rows.append({'kind':'query','i':i,'input_tick':t,'tick':t+8,'hub':pre,'turn':turn,'outputs':out})
    for i in range(3):teach(i,signs[i],i*N)
    for q,i in enumerate((2,0,1),start=3):query(i,q*N)
    teach(3,signs[3],6*N)
    for q,i in enumerate((3,1,0,2),start=7):query(i,q*N)
    final=snap(int(w.runtime.current_tick))
    receipts=[{**r,'receipt':exact_receipt(w.runtime.receipt(r['id']))}for r in requests]
    result={'label':label,'geometry':{'N':N,'common_input':I,'token_directions':V,'outputs':[add(I,(0,0,s),5)for s in(-1,1)]},'signs_for_auditor_only':signs,'initial':initial,'final':final,'rows':rows,'receipts':receipts,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'NEW LIFE. Prepared common sensory routing; not learned selection. Native learned content should select one of two common output sites.'}
    put(OUT/(label+'.json.gz'),result)
    print(json.dumps({'label':label,'tick':w.runtime.current_tick,'queries':[r for r in rows if r['kind']=='query']},ensure_ascii=False),flush=True)
if __name__=='__main__':
    put(OUT/'PROTOCOLO_ENRUTADOR_COMUN_PILOTO.json',{'before_run_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'geometry':'N31 empty T0 four learned moving supports, common I15,15,15, four token incoming directions, generic turns all routes, two common outputs at z10/20','training_signs':[1,-1,1,-1],'control_signs':[-1,1,-1,1],'criterion':'first3 and first4 queries arrive common output matching historical consequence, without teacher during query; retain first3 afterfourth; no target in query resources','scope':'exploratory prototype, fail retained, not declared operative before reserve'})
    run('MA_COMMON_ROUTER_PILOT',[1,-1,1,-1]);run('MA_COMMON_ROUTER_OPPOSITE',[-1,1,-1,1])
