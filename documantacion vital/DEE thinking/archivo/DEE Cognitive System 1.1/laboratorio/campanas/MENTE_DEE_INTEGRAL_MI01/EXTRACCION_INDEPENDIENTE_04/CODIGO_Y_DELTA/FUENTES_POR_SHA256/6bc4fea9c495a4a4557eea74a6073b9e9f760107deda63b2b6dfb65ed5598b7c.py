"""One exact failed-path replay with passive causal windows, not a rerun suite."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import mente_integral_mi01 as mi,integracion_situada_01 as integrated
from capacidades.mente_integral_mi01 import consulta_nativa as query
from capacidades.integracion_situada_01 import ic_native_core as n
life='MI01_EXTENSION_DIAG_136';fork('E1_MI01_MAIN',life)
def fn(a):
    train=mi.train(a,episode='MI01_EXT_130',contexts=[-1,1],feedback='paired',center=[40,35,55])
    p=query.prepare(a,name='MI01_EXT_130',private_value=20);frames=[]
    for index,t in enumerate(p['route']['turns']):
        for when in(t['tick']-1,t['tick'],t['tick']+1):
            if when<a.tick:continue
            a.run_until(when);path=E/(life+'.T'+str(when)+'.deetsnap.gz');a.save(path)
            frames.append({'index':index,'tick':when,'turn':t,'center':n.obs(a,t['site']),'incoming':[n.obs(a,n.move(t['site'],v,-1))for v in[t['incoming']]+[q['direction']for q in t['pulses']]],'outgoing_site':n.obs(a,n.move(t['site'],t['outgoing'])),'snapshot':str(path.relative_to(R)),'sha256':sha(path)})
    query.advance(a,until=p['end_tick']);use=integrated.act_external(a,steps=2)
    return{'experience':train,'plan':p,'frames':frames,'external':use,'final':physical(a.world,occupation=True)}
v=run(life,life,fn)['result'];print(json.dumps([{'index':z['index'],'tick':z['tick'],'native':z['center'],'out':z['outgoing_site']}for z in v['frames']],ensure_ascii=False),flush=True)
