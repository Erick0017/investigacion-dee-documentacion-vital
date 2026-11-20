"""MI02 uses the existing Store and official owner. Exact source capture first."""
import hashlib,json,shutil,subprocess,sys,time
from pathlib import Path
L=Path(__file__).resolve().parent;R=L.parents[2];S=R/'sistema';E=R/'evidencia/campanas/MI02_ARQUITECTURA_DISTRIBUIDA'
sys.path.insert(0,str(S))
from app.lives import Store
from app.native_tools import atomic_json,physical
from app.process_control import protect_current
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
protect_current()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def budget(closure=False):
    b=json.loads((L/'PRESUPUESTO.json').read_bytes())
    if time.monotonic()>b['monotonic_deadline']-(0 if closure else 2400):raise TimeoutError('MI02 fixed cutoff; reserve final closure')
    return b
def archive():
    out=E/'FUENTES_POR_SHA256';out.mkdir(exist_ok=True);paths={L/'comun_mi02.py',Path(sys.argv[0]).resolve(),S/'gestionar.py'}
    for module in list(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            p=Path(name).resolve()
            if p.suffix=='.py'and(p.is_relative_to(S)or p.is_relative_to(L)):paths.add(p)
    records=[]
    for p in sorted(paths):
        if not p.is_file():continue
        h=sha(p);target=out/(h+p.suffix)
        if not target.exists():shutil.copy2(p,target)
        records.append({'path':str(p.relative_to(R)),'sha256':h,'exact_bytes':str(target.relative_to(R))})
    return records
def create(life,n):
    budget();sources=archive();r=Store().create(life,'fisica_directa',{'N':n});atomic_json(E/(life+'.T0.json'),{'native_ticks':0,'record':r,'sources':sources});return r
def fork(parent,life,checkpoint=None):budget();return Store().fork(parent,life,checkpoint=checkpoint,kind='MI02_IDENTIFIED_EXACT_FORK')
def run(life,id,fn,details=None):
    budget();p=E/(id+'.json')
    if p.exists():raise FileExistsError('No repeated trajectory '+id)
    s=Store();before=s.record(life);sources=archive();atomic_json(E/(id+'.PRE_REGISTRO.json'),{'id':id,'before':before,'details':details,'sources':sources})
    try:v=s.mutate(life,id,fn,details or{})
    except Exception as ex:
        atomic_json(p,{'id':id,'life':life,'before':before,'after':s.record(life),'error':{'type':type(ex).__name__,'detail':str(ex)},'sources':sources});raise
    out={'id':id,'life':life,'before':before,'after':s.record(life),'data':v,'sources':sources};atomic_json(p,out);print(id+' T'+str(v['physical']['tick']),flush=True);return v['result']
def obs(a,p):return exact_observation(a.world.runtime.observe(d.Coordinate(*p)))
def move(a,p,v,k=1):return[(p[i]+v[i]*k)%int(a.world.runtime.dimension)for i in range(3)]
def submit(a,name,p,v,t,value=0,sem=1):
    old=next((q for q in a.world.interfaces if q.name==name),None)
    if old is None:
        ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*p);ch.direction=d.Direction(*v);ch.state=1;ch.semantic=sem;ch.allow_experience=True;ch.allow_probe=True;it=d.InterfaceSpec();it.name=name;it.channel=ch;a.world.declare_interface(it)
    else:
        c=old.channel;assert([c.injection_site.x,c.injection_site.y,c.injection_site.z],[c.direction.dx,c.direction.dy,c.direction.dz],c.semantic)==(list(p),list(v),sem)
    r=a.world.submit(name,value,t);return{'id':int(r.id),'port':name,'site':list(p),'direction':list(v),'tick':t,'payload':value,'semantic':sem}
def receipts(a,rows):return[{**r,'receipt':exact_receipt(a.world.runtime.receipt(r['id']))}for r in rows]
