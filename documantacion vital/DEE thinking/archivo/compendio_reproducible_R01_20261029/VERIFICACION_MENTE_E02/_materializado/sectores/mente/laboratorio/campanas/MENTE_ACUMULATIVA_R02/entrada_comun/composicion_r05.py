"""R05: una primera relación vuelve y coincide con una segunda adquirida.
No decoder calcula igualdad. Sólo se acepta el producto nativo Z del encuentro.
Exploración en bifurcaciones; la composición puede consumir soportes originales.
"""
import importlib.util,json,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('r04_exact',HERE/'continuar_r04.py');p=importlib.util.module_from_spec(sp);sp.loader.exec_module(p)
r=p.r;b=p.b

def inward_query(s,i,t,enabled=True,resources=True):
    v=b.V[i]
    if enabled:s.send('common.token.'+str(i),b.I,v,5,t)
    if resources:
        # Recursos opuestos en Z conservan el signo que únicamente aporta la
        # memoria. Dos componentes XY revierten el radial, no conocen contenido.
        for branch in(-1,1):
            target=r.move(v,4,branch)
            for dz in(-1,1):
                dv=(-v[0],-v[1],dz)
                s.send('joint.turn.'+str(i)+'.'+str(branch)+'.'+str(dz),b.add(target,dv,-2),dv,7,t+2)

def joint(s,t,first=True,second=True,resource=True,delay=0):
    before=s.save('pre_joint_'+str(t));inward_query(s,0,t,first)
    second_t=t+67+delay;inward_query(s,1,second_t,second)
    if resource:
        for branch in(-1,1):
            dest=(b.I[0],b.I[1],(b.I[2]+5*branch)%b.N);dv=(1,1,0)
            s.send('joint.resource.'+str(branch),b.add(dest,dv,-2),dv,7,second_t+6)
    frames=[];panel=[]
    # Resolución selectiva antes y alrededor de ambos encuentros y del retorno.
    times=sorted(set(list(range(t,t+10))+list(range(second_t-2,second_t+11))))
    for tick in times:
        s.world.run_until(tick)
        pts=set()
        for z in range(-7,8):
            for x in range(-1,7):
                pts.add(((b.I[0]+x)%67,b.I[1],(b.I[2]+z)%67));pts.add((b.I[0],(b.I[1]+x)%67,(b.I[2]+z)%67))
        frames.append({'tick':tick,'sites':[s.observe(pos) for pos in sorted(pts)]})
        if tick==second_t+8:panel=[s.observe((b.I[0],b.I[1],(b.I[2]+5*sgn)%67))for sgn in(-1,1)]
    candidates=[{'site':o['site'],'sign':o['direction'][2]} for o in panel if o['state']>0 and o['semantic']==1 and o['direction'][:2]==[0,0] and o['direction'][2]in(-1,1)]
    row={'kind':'joint','first_request':first,'second_request':second,'generic_resource':resource,'second_delay':delay,'first_tick':t,'second_tick':second_t,'read_tick':second_t+8,'end_tick':s.tick,'fixed_panel':panel,'candidates':candidates,'decoded_sign':candidates[0]['sign']if len(candidates)==1 else None,'pre_snapshot':before,'frames':frames,'scope':'Prepared sequential coincidence of two acquired streams; NOT learned conjunction policy; content consumed into joint product is measured afterward.'}
    s.rows.append(row);return row
if __name__=='__main__':
    b.put(b.OUT/'PROTOCOLO_COMPOSICION_R05.json',{'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'cases':'both history signs minus; mixedhistory plus/minus; omitfirst; omitsecond; nojointresource; delaysecond1','first_query_tick':1474,'second_query_tick':1541,'fixed_reader':'two central Z sites atsecond+8, unique pureZ only; no token/target passed','resource':'both possible signs and both radial generic turns fixed; no correct sign transmitted','coverage':'Forked exploration. Same world two contexts and one return period67; not independent learners.'})
    for label,prefix,first,second,resource,delay in [
      ('MA02_R05_BOTH_MINUS','MA02_R04_MAIN.T1414.deetsnap.gz',True,True,True,0),
      ('MA02_R05_MIXED','MA02_RESTAURACION_R03B_MAIN.T1012.deetsnap.gz',True,True,True,0),
      ('MA02_R05_OMIT_FIRST','MA02_R04_MAIN.T1414.deetsnap.gz',False,True,True,0),
      ('MA02_R05_OMIT_SECOND','MA02_R04_MAIN.T1414.deetsnap.gz',True,False,True,0),
      ('MA02_R05_NORESOURCE','MA02_R04_MAIN.T1414.deetsnap.gz',True,True,False,0),
      ('MA02_R05_DELAY1','MA02_R04_MAIN.T1414.deetsnap.gz',True,True,True,1)]:
        s,init=p.load(b.OUT/prefix,label);row=joint(s,1474,first,second,resource,delay);p.emit(s,init)
