"""R02: same common sensory location, no output-turn traffic; fixed passive panel.
The fixed observer scans all hubs, never chooses a bank from the request token.
"""
import gzip,hashlib,json,time
from pathlib import Path
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import encode_metadata,decode_metadata,save_world_snapshot,load_world_snapshot
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA/mecanismo';OUT.mkdir(parents=True,exist_ok=True)
N=31;I=(15,15,15);V=[(1,0,0),(0,1,0),(-1,0,0),(0,-1,0)]
KEY='MA.COMMON.ROUTER.R02.v1'
def add(a,b,k=1):return tuple((a[j]+k*b[j])%N for j in range(3))
def vec(v,z):return(v[0],v[1],z)
def put(p,x):
    if p.exists():raise FileExistsError(p)
    b=json.dumps(x,ensure_ascii=False,sort_keys=True).encode();p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
class Common:
    def __init__(self,label,world=None,requests=None,rows=None):
        self.label=label;self.requests=requests or [];self.rows=rows or []
        if world is None:
            recipe=d.OrganizationRecipe.research(N,[],0);recipe.execution=d.TickOptions(d.Backend.LAZY,1)
            world=d.OrganizationalWorld.create(recipe)
        self.world=world
    @property
    def tick(self):return int(self.world.runtime.current_tick)
    def send(self,name,p,v,value,t):
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*p);c.direction=d.Direction(*v);c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=True
        it=d.InterfaceSpec();it.name=name;it.channel=c
        if name not in set(self.world.runtime.channel_names):self.world.declare_interface(it)
        r=self.world.submit(name,value,t);self.requests.append({'id':int(r.id),'name':name,'site':list(p),'direction':list(v),'value':value,'tick':t});return r
    def observe(self,p):return exact_observation(self.world.runtime.observe(d.Coordinate(*p)))
    def save(self,label):
        self.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'label':self.label,'N':N,'I':list(I),'V':[list(v)for v in V],'requests':self.requests,'rows':self.rows,'tick':self.tick,'source':'NEW T0 no EO trained fields'}))
        p=OUT/(self.label+'.'+label+'.deetsnap.gz');proof=save_world_snapshot(self.world,p,compress=True)
        return{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'proof':str(proof)}
    @classmethod
    def load(cls,path):
        w,_=load_world_snapshot(path,max_bytes=512*1024**2);m=decode_metadata(dict(w.runtime.snapshot_metadata_entries)[KEY]);return cls(m['label'],w,m['requests'],m['rows'])
    def teach(self,i,sign,t,mode='paired'):
        v=V[i];h=add(I,v,3);ev=vec(tuple(-x for x in v),sign)
        self.send('common.token.'+str(i),I,v,5,t)
        if mode!='no_event':self.send('experience.'+str(i)+'.'+str(sign),add(h,ev,-3),ev,11,t)
        self.world.run_until(t+3);self.rows.append({'kind':'teach','i':i,'sign':sign,'mode':mode,'tick':t+3,'hub':self.observe(h)})
    def query(self,i,t):
        self.send('common.token.'+str(i),I,V[i],5,t);self.world.run_until(t+3)
        panel=[self.observe(add(I,v,3))for v in V];candidates=[]
        for j,p in enumerate(panel):
            if p['state']>0 and p['semantic']==1 and p['direction'][:2]==list(V[j][:2]) and p['direction'][2]in(-1,1):
                candidates.append({'site':p['site'],'sign':p['direction'][2]})
        answer=candidates[0]['sign']if len(candidates)==1 else None
        row={'kind':'query','request_token':i,'input_tick':t,'tick':t+3,'fixed_panel':panel,'candidates':candidates,'decoded_sign':answer,'decode_scope':'Fixed all-site native vector criterion; token never selects observer or expected sign.'}
        self.rows.append(row);return row
    def export(self,initial,final):
        receipts=[{**r,'receipt':exact_receipt(self.world.runtime.receipt(r['id']))}for r in self.requests]
        result={'label':self.label,'geometry':{'N':N,'common_input':I,'token_directions':V,'passive_panel':[add(I,v,3)for v in V]},'initial':initial,'final':final,'rows':self.rows,'receipts':receipts,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'New T0, typed sensory direction prepared routing, one world; learned signed history returned by fixed all-hub reader, not learned policy.'}
        put(OUT/(self.label+'.json.gz'),result)
        return result
def run(label,signs,mode='paired'):
    s=Common(label);initial=s.save('T0')
    for i in range(3):s.teach(i,signs[i],i*N,mode)
    for q,i in enumerate((2,0,1),start=3):s.query(i,q*N)
    s.teach(3,signs[3],6*N,mode)
    for q,i in enumerate((3,1,0,2),start=7):s.query(i,q*N)
    final=s.save('T'+str(s.tick));s.export(initial,final)
    print(json.dumps({'label':label,'tick':s.tick,'queries':[{k:r[k]for k in('request_token','decoded_sign','tick','candidates')}for r in s.rows if r['kind']=='query']},ensure_ascii=False),flush=True)
if __name__=='__main__':
    put(OUT/'PROTOCOLO_ENRUTADOR_COMUN_R02.json',{'before_run_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'revision':'Remove all turn-resource inputs; retain common input and four native storage routes. Fixed observer reads all four hubs, not token-indexed expert.', 'reader':'unique state>0 semantic1 vector XY matching its physical hub radial direction, nonzero Z sign; otherwise null','sequence':'three acquire, firstthreequery, fourthacquire, firstfourquery; no teachers in query','control':'opposite history and cues without events; allsameN31/schedule/cuevalues','scope':'Prepared context addressing P0, acquired contents P1; no learned selection/semantic breadth asserted'})
    run('MA_COMMON_R02_PAIRED',[1,-1,1,-1]);run('MA_COMMON_R02_OPPOSITE',[-1,1,-1,1]);run('MA_COMMON_R02_NOEVENT',[1,-1,1,-1],'no_event')
