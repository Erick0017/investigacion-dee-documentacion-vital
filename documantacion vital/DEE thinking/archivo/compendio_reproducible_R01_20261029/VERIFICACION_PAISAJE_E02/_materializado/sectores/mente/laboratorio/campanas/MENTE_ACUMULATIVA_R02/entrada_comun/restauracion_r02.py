"""R02: acceso por excursión y restauración de la órbita de contenido.
Recursos genéricos de ambos signos; observador fijo de todas las rutas.
"""
import importlib.util,json,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r01',HERE/'sonda_coincidencia_r01.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
b=p.b;d=b.d

def move(v,k,z=0):
    x=b.add(b.I,v,k);return(x[0],x[1],(x[2]+z)%b.N)
def guard_sites():
    return sorted({move(v,k,z*s) for v in b.V for s in(-1,1) for k,z in [(2,1),(2,2),(5,3)]})
def make(label,guards=True):
    places=[]
    if guards:
        for pos in guard_sites():
            x=d.InitialPlacement();x.site=d.Coordinate(*pos);x.raw=d.pack_record(0,0,0,0,0,4);x.clock=0;x.role='Prepared inert terminator for unused generic resource, no content'
            places.append(x)
    recipe=d.OrganizationRecipe.research(b.N,places,0);recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    return b.Common(label,d.OrganizationalWorld.create(recipe))
def read_gate(s):
    candidates=[];panel=[]
    for v in b.V:
        for sign in(-1,1):
            site=move(v,4,sign);o=s.observe(site);panel.append(o)
            if o['state']>0 and o['semantic']==1 and o['direction']==[0,0,sign]:candidates.append({'site':o['site'],'sign':sign})
    return panel,candidates
def query(s,i,t,markers=True,request=True,restoration=True,trace=False):
    v=b.V[i]
    before=s.save('pre_'+str(t))
    ids=[]
    if request:ids.append(s.send('common.token.'+str(i),b.I,v,5,t))
    if markers:
        for sign in(-1,1):
            for stage,k,z,di,arrival in [('select',4,1,-1,4),('back',4,2,-1,5),('restore',3,3,1,6)]:
                if stage!='select' and not restoration:continue
                target=move(v,k,z*sign);dv=(di*v[0],di*v[1],0)
                ids.append(s.send('generic.'+stage+'.'+str(i)+'.'+str(sign),b.add(target,dv,-2),dv,7,t+arrival-2))
    frames=[]
    for q in range(t,t+8):
        s.world.run_until(q)
        points=set()
        for vv in b.V:
            for k in(2,3,4,5):
                for z in range(-4,5):points.add(move(vv,k,z))
        if trace:frames.append({'tick':q,'sites':[s.observe(pos)for pos in sorted(points)]})
        if q==t+4:panel,candidates=read_gate(s)
    row={'kind':'query','request_token':i,'input_tick':t,'read_tick':t+4,'end_tick':s.tick,'markers':markers,'request':request,'restoration':restoration,'fixed_panel':panel,'candidates':candidates,'decoded_sign':candidates[0]['sign']if len(candidates)==1 else None,'pre_snapshot':before,'frames':frames,'observer_uses_target_or_token':False}
    s.rows.append(row);return row
def run(label,signs,guards=True):
    s=make(label,guards);start=s.save('T0')
    for i,sgn in enumerate(signs[:3]):s.teach(i,sgn,i*67)
    for j,i in enumerate([2,0,1,2,0,1],3):query(s,i,j*67,trace=True)
    s.teach(3,signs[3],9*67)
    for j,i in enumerate([3,0,2,1,3,1],10):query(s,i,j*67,trace=True)
    end=s.save('T'+str(s.tick));result=s.export(start,end)
    b.put(b.OUT/(label+'.R02.json.gz'),result)
    print(json.dumps({'label':label,'tick':s.tick,'queries':[{k:x[k]for k in('request_token','decoded_sign','read_tick','candidates')}for x in s.rows if x['kind']=='query']},ensure_ascii=False),flush=True)
if __name__=='__main__':
    b.put(b.OUT/'PROTOCOLO_RESTAURACION_R02.json',{'fixed_before_tick_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'revision':'R02 restorative excursion','sequence':'learn3,queryinterleave6,learn4,queryinterleave6','reader':'unique pure Z signed carrier across ALL eight fixed gate sites at query+4; no token or target used by decoder','geometry':{'N':b.N,'I':b.I,'V':b.V,'guards':guard_sites()},'resources':'7 all three stages both possible signs, fixed typed token→geometry codec. P0 preparation not acquired selector.','hypothesis':'Return query-transformed content to original XY column, preserving later use; terminate unused markers by prepared SEM4.','contrast':'opposite acquired contents; no guards control'})
    run('MA02_RESTAURACION_R02_MAIN',[1,-1,1,-1]);run('MA02_RESTAURACION_R02_OPPOSITE',[-1,1,-1,1]);run('MA02_RESTAURACION_R02_NOGUARD',[1,-1,1,-1],False)
