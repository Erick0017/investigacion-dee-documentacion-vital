"""Small causal-window diagnosis; no assumed carrier lineage from equal load."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.integracion_situada_01 import ic_native_core as n
fork('MI01_SELECTOR_PREFIJO_10','MI01_TRAZA_060')
def fn(a):
    initial=physical(a.world,occupation=True);plan=n.situated(a,name='MI01_TRACE60',availability=[1],mode='intact',compact=True,gap=0,stream=True,shunt='a_only',queue_only=True)
    S0=plan['center'];t=plan['plans'][0]['query_tick'];rr=[]
    for k,(v,z)in enumerate((([1,0,1],5),([1,0,-1],0))):rr.append(n.arrive(a,'MI01.trace.supply.'+str(k),S0,v,t,z))
    frames=[]
    for when in range(t-1,t+6):
        a.run_until(when);p=E/('MI01_TRAZA_060.T'+str(when)+'.deetsnap.gz');a.save(p)
        cells=[]
        for dx in range(-5,6):
            for dy in range(-5,6):
                for dz in range(-2,3):
                    q=n.obs(a,n.move(n.move(n.move(S0,(1,0,0),dx),(0,1,0),dy),(0,0,1),dz))
                    if q['raw']!='0':cells.append({'offset':[dx,dy,dz],**q})
        frames.append({'tick':when,'snapshot':str(p.relative_to(R)),'sha256':sha(p),'center':n.obs(a,S0),'nonzero_RAW_ROI':cells,'global':physical(a.world,occupation=True)})
    a.run_until(plan['end_tick']);return{'initial':initial,'plan':plan,'frames':frames,'requests':n.receipts(a,rr),'final':physical(a.world,occupation=True),'scope':'Local complete RAW/clock window and global measures. Equal payload does not identify unique lineage; full snapshots preserve outside influence.'}
v=run('MI01_TRAZA_060','MI01_TRAZA_060',fn)['result']
for z in v['frames']:
    print(json.dumps({'tick':z['tick'],'center':z['center'],'payload_cells':[p for p in z['nonzero_RAW_ROI']if p['s_reg']>0]},ensure_ascii=False),flush=True)
