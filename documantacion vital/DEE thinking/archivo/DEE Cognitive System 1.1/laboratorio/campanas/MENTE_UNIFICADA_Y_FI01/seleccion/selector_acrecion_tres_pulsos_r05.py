"""Prospective low-density history selector. New anatomy, not E1 continuation.

Two equal immobile references have a native basal accretion opportunity at391.
An explicit zero-load experience inhibits only one side through native context.
The identical two-pulse query may survive for one step, acquire the difference's
direction and then disappear; fixed all-route reader does not know the history.
"""
import gzip,hashlib,json,time
from pathlib import Path
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import encode_metadata,save_world_snapshot
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/seleccion'
N=67;E=(33,33,33);A=(32,32,33);B=(34,32,33)
QUERIES=(400,420,440,460,480,520,600,700,800,900);KEY='MUFI01.selection.accretion.r05'
def add(p,v,k=1):return tuple((p[i]+k*v[i])%N for i in range(3))
def put(p,x):
    if p.exists():raise FileExistsError(p)
    p.parent.mkdir(parents=True,exist_ok=True)
    b=json.dumps(x,ensure_ascii=False,sort_keys=True).encode('utf8')
    p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
def design():
    frame={A:(1,0,1),B:(1,0,1)}
    for x in(31,35):
        for y in(31,32):
            for z in(32,33,34):frame[(x,y,z)]=(1,0,4)
    for p in((33,34,34),(33,34,32)):frame[p]=(1,0,4)
    frame[(33,33,34)]=(0,0,4)
    frame[(32,30,33)]=(0,0,4);frame[(34,30,33)]=(0,0,4)
    for p in((32,31,34),(34,31,34),(35,34,35),(31,33,33),(30,36,33),(36,36,33)):frame[p]=(0,0,4)
    ps=[]
    for p,(state,load,sem)in sorted(frame.items()):
        a=d.InitialPlacement();a.site=d.Coordinate(*p);a.raw=d.pack_record(state,load,0,0,0,sem);a.clock=0;a.role='Prepared equal baseline reference or zero-load support';ps.append(a)
    r=d.OrganizationRecipe.research(N,ps,0);r.execution=d.TickOptions(d.Backend.LAZY,1)
    return r,frame
def run(label,history='A',query=True):
    recipe,frame=design();w=d.OrganizationalWorld.create(recipe);requests=[];rows=[];shots=[]
    def obs(p):return exact_observation(w.runtime.observe(d.Coordinate(*p)))
    def send(name,p,v,t):
        if name not in set(w.runtime.channel_names):
            c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*p);c.direction=d.Direction(*v);c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=True
            i=d.InterfaceSpec();i.name=name;i.channel=c;w.declare_interface(i)
        r=w.submit(name,0,t);requests.append({'id':int(r.id),'port':name,'site':list(p),'direction':list(v),'tick':t,'payload':0})
    if history in('A','B'):
        target=add(A if history=='A'else B,(0,-1,0));v=(0,0,1)
        send('experience.contact.'+history,add(target,v,-3),v,388)
    if query:
        for q in QUERIES:
            send('common.query',add(E,(0,0,1),-3),(0,0,1),q)
            for suffix,target,v in [('plus',(34,34,34),(1,0,1)),('minus',(32,34,33),(-1,-1,0))]:
                send('common.support.'+suffix,add(target,v,-3),v,q)
    def snap():
        w.runtime.set_snapshot_metadata(KEY,encode_metadata({'identity':label,'architecture':'equal_reference_accretion_double_probe_r01','N':N,'tick':int(w.runtime.current_tick),'requests':requests,'interfaces':'explicit zero-load physical experience and common probe only','scope':'New T0 organization; no inherited E1 or MA02 knowledge'}))
        p=OUT/(label+'.T'+str(w.runtime.current_tick)+'.deetsnap.gz');proof=save_world_snapshot(w,p,compress=True)
        shots.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'proof':proof})
    snap()
    ts=sorted({0,1,10,100,387,388,389,390,391,392,393,399,490,910,*[q+k for q in QUERIES for k in range(10)]})
    roi=sorted({add(E,(x,y,z))for x in range(-3,4)for y in range(-3,4)for z in range(-2,3)})
    for t in ts:
        w.run_until(t)
        raw=w.runtime.raw_copy()
        rows.append({'tick':t,'A':obs(A),'B':obs(B),'E':obs(E),'roi':[obs(p)for p in roi],'global_active':sum(int(int(a)&0xffffffff)>0 for a in raw),'global_nonzero_raw':sum(int(a)!=0 for a in raw)})
        if t in(392,490,910):snap()
    results=[]
    for q in QUERIES:
        rr=next(r for r in rows if r['tick']==q+6);by={tuple(p['site']):p for p in rr['roi']};accepted=[]
        for sign in(-1,1):
            p=by[add(E,(sign,1,0),2)]
            if p['state']>0 and p['semantic']==1 and p['direction']==[sign,1,0]:accepted.append({'site':p['site'],'choice':sign,'raw':p['raw'],'clock':p['clock']})
        results.append({'query':q,'read_tick':q+6,'candidates':accepted,'choice':accepted[0]['choice']if len(accepted)==1 else None})
    result={'schema':KEY,'identifier':label,'new_T0':True,'history_for_evaluator_only':history,'query':query,'N':N,'preparation':[{'site':p,'state':v[0],'s_reg':v[1],'semantic':v[2]}for p,v in sorted(frame.items())],'rows':rows,'results':results,'snapshots':shots,'requests':[dict(r,receipt=exact_receipt(w.runtime.receipt(r['id'])))for r in requests],'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Phase-specific P1 selector candidate, not policy/R2. All signals payload0; fixed reader of both native routes.'}
    put(OUT/(label+'.json.gz'),result)
    print(json.dumps({'label':label,'refs392':[{k:next(r for r in rows if r['tick']==392)[k]for k in('A','B','E')}],'choices':[r['choice']for r in results],'selectors':[next(r['E']for r in rows if r['tick']==q+4)for q in QUERIES],'statuses':[r['receipt']['status']for r in result['requests']]},ensure_ascii=False),flush=True)
if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    put(OUT/'PROTOCOLO_ACRECION_R05.json',{'fixed_before_first_tick_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'based_on':'R04 preservednegative:4/10A,6/10B. ContactP emitsinitial+Z beforeturnandcreatessecondsourceatP+Z. Querysupportminus entersreferencehistoryregionprearrival. R05 preventsP+Zspilland placesbothquerysupports inY+hemispherewithindependent lowdensityapproaches; staticEanchors movedtomiddleY+planes. Alltemporaryforwardpaths/outputsfixedstate0SEM4terminated, notexternalcleanup. MultipleP0factors notisolatedfactorial.','hypothesis':'4static+2temporaryneighbor query controlsEoneupdates, bothapproachesavoidreferencecontext andeachother; fixedterminators preventcurrentsfromrecurring.','new_T0':True,'arms':['touchA','touchB','no_teaching','touchA_no_query'],'history':'samezerocontact+Zin391, fixedstopsP+ZandP-Y','future_query':{'ticks':list(QUERIES),'three_pulses':'primarytoE+Z; S1=E+(1,1,1),v(1,0,1);S2=E+(-1,1,0),v(-1,-1,0); alwaysallthree'},'reader_frozen':'Both E+2(-1,+1,0) andE+2(+1,+1,0), SEM1statepositive matchingdirectionatq+6.','predictions':{'touchA':-1,'touchB':1,'no_teaching':None,'no_query':None},'horizon':910,'scope':'Preparedtermination+routingP0; acquiredreferenceanddirectionP1onlyifdemonstrated; noP2.'})
    run('MUFI_S05_TOUCH_A','A');run('MUFI_S05_TOUCH_B','B');run('MUFI_S05_NO_TEACH','none');run('MUFI_S05_NO_QUERY','A',False)
