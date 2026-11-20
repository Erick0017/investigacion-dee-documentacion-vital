"""Two initially untrained relative relations in one continuing Research world.

The first reader is replenished by a prepared semantic4 source. The second
relation is exposed later and uses a declared finite physical reader. This
tests cumulative retention, not four-person communication or learned utility.
"""
from pathlib import Path
import argparse,json,sys,time,shutil
from campaign import ROOT,PARENT,put,sha
sys.path.insert(0,str(PARENT))
from src.common import observe,receipt,interface
from sustained_regulation import PA,PB,digest

def prepare(case):
    import dee_thinking as d
    n=47;shift=case.get('translation',[0,0,0]);centers=[(14,14,14),(32,32,32)]
    placements=[];interfaces=[];spec={};occupied=set()
    def moved(q,v):return tuple((q[i]+v[i])%n for i in range(3))
    def place(q,state,load,dr=(0,0,0),sem=4,clock=0,role='support'):
        if q in occupied:raise ValueError('Initial overlap')
        occupied.add(q);p=d.InitialPlacement();p.site=d.Coordinate(*q);p.raw=d.pack_record(state,load,*dr,sem);p.clock=clock;p.role=role;placements.append(p)
    for j,center in enumerate(centers,1):
        c=moved(center,shift);a=moved(c,(-1,0,0));b=moved(c,(1,0,0));phase=260 if j==1 else case.get('second_phase',0)
        place(a,1000,100,sem=1,clock=phase,role=f'memory{j}.A');place(b,2000,100,sem=1,clock=phase,role=f'memory{j}.B')
        for q,pat,s,clock in ((a,PA,3000,31),(b,PB,4000,41)):
            for i,v in enumerate(pat):place(moved(q,v),s+i,0,clock=clock+i)
        if j==1 and case.get('reader1','persistent')!='absent':
            place(moved(c,(0,-2,0)),6000,7,(0,1,0),4 if case.get('reader1','persistent')=='persistent' else 1,23,'reader1')
        for name,q,offset,dr,state in (('A',a,(0,-1,0),(0,-1,0),5000),('B',b,(0,1,0),(0,1,0),5001)):
            interfaces.append(interface(f'm{j}.{name}',moved(q,offset),dr,state=state))
        interfaces.append(interface(f'm{j}.read',moved(c,(0,-1,0)),(0,1,0)))
        spec[str(j)]={'A':a,'B':b,'comparator':c,'reader':moved(c,(0,-1,0)),'source':moved(c,(0,-2,0))}
    recipe=d.OrganizationRecipe.research(n,placements,0);recipe.interfaces=interfaces;recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    return d.OrganizationalWorld.create(recipe),spec

def sample(w,spec):
    data={}
    for name,ports in spec.items():
        r={k:observe(w,q) for k,q in ports.items()};a,b=r['A'],r['B']
        data[name]={'delta':a['s_reg']-b['s_reg'] if a['active'] and b['active'] else None,'physical':r}
    return {'tick':w.runtime.current_tick,'memories':data}

def run(case,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'EXECUTED_SOURCE.py');put(out/'CONFIG.json',case)
    w,spec=prepare(case);calls=[];ids=[];started=time.monotonic()
    for j,key,start in ((1,'history1',0),(2,'history2',260)):
        h=case.get(key,'AB')
        for i,label in enumerate(h if h in ('AB','BA') else ''):
            r=w.submit(f'm{j}.{label}',3,start+i);ids.append(r.id);calls.append({'operation':'experience','channel':f'm{j}.{label}','load':3,'tick':start+i,'id':r.id})
    for tick in case.get('second_queries',[262,400]):
        r=w.probe('m2.read',7,tick);ids.append(r.id);calls.append({'operation':'physical_probe','channel':'m2.read','load':7,'tick':tick,'id':r.id})
    rows=[];snapshots={0,2,259,262,265,399,403,520};horizon=case.get('horizon',520)
    for t in range(horizon+1):
        if t<6 or 258<=t<=270 or 398<=t<=406 or t%10==0:rows.append(sample(w,spec))
        if t in snapshots:w.save_snapshot(str(out/f'T{t}.deetsnap'))
        if t<horizon:w.advance()
    result={'case':case,'spec':spec,'rows':rows,'final':sample(w,spec),'digest':digest(w),'calls':calls,
            'receipts':[receipt(w,x) for x in ids],'runtime_external_operations':list(w.external_operations),
            'source_sha256':sha(__file__),'elapsed_seconds':time.monotonic()-started,
            'scope':'Two fresh cells coexist from T0; no learned snapshot transplanted. Fixed replenishment/separation versus experience-dependent acquisition are distinct.'}
    put(out/'MEASUREMENTS.json',result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--case',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    r=run(json.loads(a.case.read_text(encoding='utf-8-sig')),a.output);print(json.dumps({'id':r['case']['id'],'final':{k:v['delta'] for k,v in r['final']['memories'].items()},'elapsed':r['elapsed_seconds']}))
