"""Continuación R04 y contrastes desde el mismo pasado R03B completo."""
import hashlib,importlib.util,json,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('r03_exact',HERE/'restauracion_r03.py');p=importlib.util.module_from_spec(sp);sp.loader.exec_module(p)
r=p.r;b=r.b
def load(path,label):
    w,_=b.load_world_snapshot(path,max_bytes=512*1024**2)
    m=b.decode_metadata(dict(w.runtime.snapshot_metadata_entries)[b.KEY])
    s=b.Common(label,w,m['requests'],[])
    return s,{'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_life':m['label'],'tick':s.tick,'fork_type':'full physical continuation, no imported learned fields'}
def revise(s,i,sign,t,mode='double'):
    v=b.V[i];h=b.add(b.I,v,3);ev=(-v[0],-v[1],sign)
    before=s.save('pre_revision_'+str(t))
    s.send('common.token.'+str(i),b.I,v,5,t)
    s.send('experience.'+str(i)+'.'+str(sign),b.add(h,ev,-3),ev,11,t)
    if mode=='double':
        extra=(0,0,sign);s.send('contrast.second.'+str(i)+'.'+str(sign),b.add(h,extra,-3),extra,11,t)
    elif mode=='sham':
        extra=(0,0,sign);target=b.add(h,(0,1,0),13);s.send('contrast.sham.'+str(i)+'.'+str(sign),b.add(target,extra,-3),extra,11,t)
    s.world.run_until(t+3)
    s.rows.append({'kind':'revision','bank':i,'new_signal':sign,'input_tick':t,'tick':s.tick,'mode':mode,'pre_snapshot':before,'hub':s.observe(h)})
def emit(s,initial):
    final=s.save('T'+str(s.tick));out=s.export(initial,final);b.put(b.OUT/(s.label+'.R04.json.gz'),out)
    print(json.dumps({'life':s.label,'tick':s.tick,'rows':[{k:v for k,v in x.items()if k in('kind','mode','request_token','decoded_sign','read_tick','new_signal','hub','candidates')}for x in s.rows]},ensure_ascii=False),flush=True)
def main():
    b.put(b.OUT/'PROTOCOLO_CONTINUIDAD_R04.json',{'utc_frozen':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'prefix':'MA02_RESTAURACION_R03B_MAIN T1012, all controls fork exact full state','reader':'R03 all eight pureZ sites atq+4, frozen, no token or target','sequence':'revise0 using two opposite signal experiences; first-use unchanged1, revised0, unchanged3,unchanged2,revised0','revision_control':'same dose second signal diverted13Y','recovery_controls':'request+resources, no_request, no_markers, no_restoration, select-marker displaced, request after whole-period delay; common age matched by known N schedule','no_P2_claim':True})
    prefix=b.OUT/'MA02_RESTAURACION_R03B_MAIN.T1012.deetsnap.gz'
    for label,mode in [('MA02_R04_MAIN','double'),('MA02_R04_SINGLE_REV','single'),('MA02_R04_REV_SHAM','sham')]:
        s,init=load(prefix,label);revise(s,0,-1,1072,mode)
        for j,i in enumerate([1,0,3,2,0],17):r.query(s,i,j*67,trace=True)
        emit(s,init)
    for label,markers,request,restore in [('MA02_R04_QUERY_RESOURCE',True,True,True),('MA02_R04_NOQUERY',True,False,True),('MA02_R04_NOMARKERS',False,True,True),('MA02_R04_NORESTORE',True,True,False)]:
        s,init=load(prefix,label);r.query(s,0,1072,markers=markers,request=request,restoration=restore,trace=True)
        for j,i in enumerate([2,1,0,3],17):r.query(s,i,j*67,trace=True)
        emit(s,init)
if __name__=='__main__':main()
