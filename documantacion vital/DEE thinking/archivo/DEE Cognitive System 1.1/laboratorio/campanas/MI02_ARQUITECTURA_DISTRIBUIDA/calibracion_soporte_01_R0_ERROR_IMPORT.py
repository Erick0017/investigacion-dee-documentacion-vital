"""Native stationary acquired memories: discriminate repeated reading and loss.
No target sign is supplied to a probe; empty initial memory sites are shown.
"""
from comun_mi02 import *
center=[15,15,15]
offsets=[(-1,1,0),(1,1,0)]
tetra=[[(sx,0,0),(0,sy,0),(0,0,sz),(sx,sy,sz)]for sx in(-1,1)for sy in(-1,1)for sz in(-1,1)]
add=lambda p,v:tuple(p[i]+v[i]for i in range(3))
near=lambda p,q:max(abs(p[i]-q[i])for i in range(3))<=1 and p!=q
mem=[tuple(v)for v in offsets];Q=(0,0,0);valid=[]
for i,t in enumerate(tetra):
    for j,u in enumerate(tetra):
        ss=set(add(mem[0],v)for v in t)|set(add(mem[1],v)for v in u)
        if Q in ss or any(m in ss for m in mem):continue
        counts=[sum(near(m,p)for p in ss)for m in mem]
        countQ=sum(near(Q,p)for p in ss)+2+2 # acquired two memories + two bias observers
        if counts==[4,4]and countQ>=6:valid.append({'tetra_indices':[i,j],'supports':sorted(ss),'mem_counts_without_reader':counts,'Q_neighbours_after_learning':countQ})
atomic_json(E/'GEOMETRIA_SOPORTE_01.json',{'native_ticks':0,'question':'Can a common material reader use independently acquired stationary scalar histories repeatedly? Later updates require a separate mechanism.','candidates':valid,'no_expected_answer_used':True})
if not valid:raise RuntimeError('No support geometry fits declared neighbour constraints')
plan=valid[0];supports=plan['supports'];bias=[(-1,-1,1),(-1,-1,-1)]
for case,values in[(10,(17,52)),(11,(52,17)),(12,(None,None))]:
    life='MI02_SOPORTE_'+str(case);create(life,41)
    def fn(a,values=values):
        rr=[]
        for k,v in enumerate(supports+bias):rr.append(submit(a,'MI02.frame.'+str(k),add(center,v),(0,0,0),0,1 if v in bias else 0,4))
        frames=[]
        def record(tag):frames.append({'tag':tag,'physical':physical(a.world,occupation=True),'memories':[obs(a,add(center,v))for v in mem],'reader':obs(a,center),'downstream':[obs(a,add(center,(s,-2,0)))for s in(-2,2)]})
        a.run_until(7);record('before_acquisition')
        for k,value in enumerate(values):
            if value is not None:rr.append(submit(a,'MI02.history.'+str(k),add(center,mem[k]),(0,0,0),8+4*k,value))
        a.run_until(19);record('after_acquisition')
        rr.append(submit(a,'MI02.common_reader',center,(0,0,-1),20,7))
        for t in(20,21,22,23,24,30,61,101,201,391,392,521,782):
            a.run_until(t);record('read_'+str(t))
        return{'geometry':plan,'bias':bias,'raw_acquisition_values':values,'frames':frames,'requests':receipts(a,rr),'scope':'One generic probe, passive uses afterwards. Scalar teaching is an experience at an empty declared input, not an overwrite. Spatial/gradient comparison law is prepared.'}
    v=run(life,'SOPORTE_ESTACIONARIO_'+str(case),fn,{'values':values,'horizon':782,'probe_count':1,'reserve':'Not a language/general-learning test. Opposite histories and absence control.'});print(json.dumps({'case':case,'frames':[{'tag':x['tag'],'M':[z['s_reg']for z in x['memories']],'dir':x['reader']['direction'],'state':x['reader']['state'],'occupied':x['physical']['occupied']}for x in v['frames']]},ensure_ascii=False),flush=True)
