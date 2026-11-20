"""PC01 auditor instruments. Never used to choose a participant's answer.

Sparse frames preserve every RAW!=0 (including state zero) and all clock
exceptions. Radius3 witnesses cover the conservative composed DEMUX read set
of a complete v27 tick; this is not a claim of radius1 closed dynamics.
"""
from array import array
from collections import Counter,defaultdict
from pathlib import Path
import gzip,hashlib,json,tempfile

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def packed(v):
    def s(k):
        x=(v>>k)&15
        return x-16 if x&8 else x
    return {'raw':str(v),'state':v&0xffffffff,'s_reg':(v>>32)&65535,'direction':[s(48),s(52),s(56)],'semantic':(v>>60)&15}
def coord(i,n):return[i//(n*n),(i//n)%n,i%n]
def idx(p,n):return(p[0]*n+p[1])*n+p[2]
def receipts(rt):
    from dee_thinking.consolidated import exact_receipt
    r=rt.receipts
    return[exact_receipt(x)for x in(r()if callable(r)else r)]
def native_digest(rt):
    # Official serializer includes full input queue, channels, receipts, clocks,
    # pause/execution context and metadata. Read-only save into ASCII temp.
    with tempfile.TemporaryDirectory(prefix='pc01-native-')as folder:
        p=Path(folder)/'world.deetsnap';rt.save_snapshot(str(p))
        return{'native_bytes':p.stat().st_size,'native_sha256':sha(p)}
def snapshot_state(a,path):
    return a.save(path)
def frame(world,*,full_clocks=True):
    rt=world.runtime;n=int(rt.dimension);t=int(rt.current_tick);raw=rt.raw_copy();clocks=rt.clock_copy()
    mode=Counter(clocks).most_common(1)[0][0]
    rows=[[i,str(v),str(clocks[i])]for i,v in enumerate(raw)if v!=0]
    exceptions=[[i,str(v)]for i,v in enumerate(clocks)if v!=mode]if full_clocks else None
    incoming=defaultdict(list);occupied=0;statezero=0;semantic=Counter();blocks=Counter()
    for i,vr,clock in rows:
        v=int(vr);f=packed(v);p=coord(i,n);occupied+=bool(f['state']);statezero+=not bool(f['state']);semantic[str(f['semantic'])]+=1;blocks[','.join(str(c//8)for c in p)]+=1
        direction=f['direction']
        if any(direction):
            dest=[(p[k]+direction[k])%n for k in range(3)]
            # Native buscar_fuente_demux only examines source Moore26.
            if all(abs(d)<=1 for d in direction):incoming[idx(dest,n)].append(i)
    encounters=[]
    for dest,sources in incoming.items():
        if len(sources)>1 or raw[dest]!=0:
            encounters.append({'destination':coord(dest,n),'destination_raw':str(raw[dest]),'sources':sources,'kind':'MULTIPLE_BALLISTIC'if len(sources)>1 else'BALLISTIC_TO_RAW_NONZERO'})
    return{'tick':t,'N':n,'RAW_sha256':hashlib.sha256(array('Q',raw).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',clocks).tobytes()).hexdigest(),'raw_nonzero':len(rows),'occupied':occupied,'state_zero_raw_nonzero':statezero,'rows':rows,'clock_default':str(mode),'clock_exceptions':exceptions,'semantics':dict(semantic),'blocks8':dict(blocks),'encounters':encounters}
def witness(world,site,radius=3):
    from app.native_tools import observe
    n=int(world.runtime.dimension)
    return{'site':list(site),'radius':radius,'metric':'toroidal_Chebyshev','tick':int(world.runtime.current_tick),'records':[observe(world,[(site[0]+x)%n,(site[1]+y)%n,(site[2]+z)%n])for x in range(-radius,radius+1)for y in range(-radius,radius+1)for z in range(-radius,radius+1)]}
def guard(world,name,site,tick,*,direction=(0,0,0),semantic=4,payload=0):
    import dee_thinking as d
    from dee_thinking.consolidated import exact_receipt
    ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*site);ch.direction=d.Direction(*direction);ch.state=1;ch.semantic=semantic;ch.allow_experience=True;ch.allow_probe=True
    p=d.InterfaceSpec();p.name=name;p.channel=ch;world.declare_interface(p);r=world.submit(name,payload,tick)
    return{'id':int(r.id),'channel':name,'site':list(site),'tick':tick,'payload':payload,'direction':list(direction),'semantic':semantic,'submitted':exact_receipt(r)}
class Trace:
    def __init__(self,a,path,*,start=None,end=None,stride=1):
        self.a=a;self.path=Path(path);self.start=start if start is not None else a.tick;self.end=end;self.stride=stride;self.original=a.run_until;self.count=0;self.last=None;self.boundaries=[];self.seen_receipts={};self.stream=gzip.open(self.path,'xt',encoding='utf8',compresslevel=6)
    def capture(self):
        if self.last==self.a.tick:return
        f=frame(self.a.world);self.stream.write(json.dumps(f,separators=(',',':'))+'\n');self.count+=1;self.last=self.a.tick
    def install(self):
        self.capture_if();self.a.run_until=self.run;return self
    def capture_if(self):
        t=self.a.tick
        if t>=self.start and(self.end is None or t<=self.end)and((t-self.start)%self.stride==0):self.capture()
    def run(self,target):
        r=receipts(self.a.world.runtime);new=[x for x in r if self.seen_receipts.get(str(x['id']))!=x]
        if new:self.boundaries.append({'tick_before_run':self.a.tick,'target':target,'receipts':new});self.seen_receipts.update({str(x['id']):x for x in r})
        while self.a.tick<target:
            if self.a.tick<self.start:step=min(target,self.start)
            elif self.end is not None and self.a.tick>=self.end:step=target
            else:step=min(target,self.a.tick+1)
            self.original(step);self.capture_if()
        return None
    def close(self):
        self.a.run_until=self.original;self.stream.close()
        return{'file':self.path.name,'sha256':sha(self.path),'frames':self.count,'start':self.start,'end':self.end,'stride':self.stride,'receipt_boundaries':self.boundaries,'clock_and_raw_exact':True,'not_a_complete_operational_snapshot':True}

