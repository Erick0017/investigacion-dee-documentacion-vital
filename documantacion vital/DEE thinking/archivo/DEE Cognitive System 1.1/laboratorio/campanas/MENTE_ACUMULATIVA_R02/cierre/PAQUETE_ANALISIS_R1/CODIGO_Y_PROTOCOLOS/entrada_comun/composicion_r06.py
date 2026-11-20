"""R06: composición por recurrencia de dos accesos R03 sin restauración final.
Corrige R05: sus recursos diagonales se coalescieron ANTES del gate.
"""
import importlib.util,json,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('r05_exact',HERE/'composicion_r05.py');p=importlib.util.module_from_spec(sp);sp.loader.exec_module(p)
b=p.b;r=p.r
def inward_query(s,i,t,enabled=True,resources=True):
    v=b.V[i]
    if enabled:s.send('common.token.'+str(i),b.I,v,5,t)
    if resources:
        for sign in(-1,1):
            for stage,z,arrival in [('select',1,4),('back',2,5)]:
                dest=r.move(v,4,z*sign);dv=(-v[0],-v[1],0)
                s.send('joint.r06.'+stage+'.'+str(i)+'.'+str(sign),b.add(dest,dv,-2),dv,7,t+arrival-2)
p.inward_query=inward_query
# New explicit function rather than patching the executed R05 physics bytes.
def joint(s,t,first=True,second=True,resource=True,delay=0):
    before=s.save('pre_joint_'+str(t));inward_query(s,0,t,first)
    st=t+67+delay;inward_query(s,1,st,second)
    if resource:
        for sg in(-1,1):
            dest=(b.I[0],b.I[1],(b.I[2]+6*sg)%67);dv=(1,1,0)
            s.send('joint.r06.resource.'+str(sg),b.add(dest,dv,-2),dv,7,st+7)
    frames=[];panel=[]
    for tick in sorted(set(list(range(t,t+11))+list(range(st-2,st+12)))):
        s.world.run_until(tick);pts=set()
        for z in range(-8,9):
            for x in range(-1,7):
                pts.add(((b.I[0]+x)%67,b.I[1],(b.I[2]+z)%67));pts.add((b.I[0],(b.I[1]+x)%67,(b.I[2]+z)%67))
        frames.append({'tick':tick,'sites':[s.observe(pos)for pos in sorted(pts)]})
        if tick==st+9:panel=[s.observe((b.I[0],b.I[1],(b.I[2]+6*sg)%67))for sg in(-1,1)]
    cs=[{'site':o['site'],'sign':o['direction'][2]}for o in panel if o['state']>0 and o['semantic']==1 and o['direction'][:2]==[0,0] and o['direction'][2]in(-1,1)]
    row={'kind':'joint','first_request':first,'second_request':second,'generic_resource':resource,'second_delay':delay,'first_tick':t,'second_tick':st,'read_tick':st+9,'end_tick':s.tick,'fixed_panel':panel,'candidates':cs,'decoded_sign':cs[0]['sign']if len(cs)==1 else None,'pre_snapshot':before,'frames':frames,'scope':'Prepared signed concordance using first acquired contribution after one toroidal recurrence; partial destructive composition, not learned conjunction or general equality.'}
    s.rows.append(row);return row
if __name__=='__main__':
    b.put(b.OUT/'PROTOCOLO_COMPOSICION_R06.json',{'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'difference_from_R05':'Two validated R03 stages, no final restore, central rendezvous±6Z atsecond+9','no_host_comparison':True,'cases':'bothminus,mixed,omitfirst,omitsecond,noresource,delay1','first_tick':1474,'new_exploration_after_failed_R05':True,'fixed_reader':'pureZ across BOTH central sites; no target passed'})
    for label,prefix,a,bq,c,dt in [('MA02_R06_BOTH_MINUS','MA02_R04_MAIN.T1414.deetsnap.gz',True,True,True,0),('MA02_R06_MIXED','MA02_RESTAURACION_R03B_MAIN.T1012.deetsnap.gz',True,True,True,0),('MA02_R06_OMIT_FIRST','MA02_R04_MAIN.T1414.deetsnap.gz',False,True,True,0),('MA02_R06_OMIT_SECOND','MA02_R04_MAIN.T1414.deetsnap.gz',True,False,True,0),('MA02_R06_NORESOURCE','MA02_R04_MAIN.T1414.deetsnap.gz',True,True,False,0),('MA02_R06_DELAY1','MA02_R04_MAIN.T1414.deetsnap.gz',True,True,True,1)]:
        s,init=p.p.load(b.OUT/prefix,label);joint(s,1474,a,bq,c,dt);p.p.emit(s,init)
