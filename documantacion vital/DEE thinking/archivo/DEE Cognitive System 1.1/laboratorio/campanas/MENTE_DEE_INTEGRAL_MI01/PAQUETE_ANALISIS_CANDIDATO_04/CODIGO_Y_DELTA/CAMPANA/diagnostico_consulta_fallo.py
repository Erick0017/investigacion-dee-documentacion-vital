"""One actual failure-triggered request path; no alternate future imported."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.mente_integral_mi01 import saved
from capacidades.integracion_situada_01 import ic_native_core as n
def execute():
    source=E/'MI01_COMPARTIDO_270.PREPARADO.deetsnap.gz';life='MI01_FALLO_RUTA_DIAG_290';Store().import_state(source,life,'cpc9_integral_n67',sha(source))
    def fn(a):
        cfg=saved(a);p=cfg['material_queries']['MI01_COMPARTIDO_270.FQ1'];frames=[]
        a.run_until(p['query_tick']);command=n.obs(a,p['S'])
        for i,t in enumerate(p['route']['turns']):
            for when in(t['tick']-1,t['tick'],t['tick']+1):
                if when<a.tick:continue
                a.run_until(when);q={'index':i,'tick':when,'turn':t,'native':n.obs(a,t['site']),'context125':[n.obs(a,n.move(t['site'],(x,y,z)))for x in(-2,-1,0,1,2)for y in(-2,-1,0,1,2)for z in(-2,-1,0,1,2)]};frames.append(q)
                if when==t['tick']:
                    path=E/(life+'.T'+str(when)+'.deetsnap.gz');a.save(path);q['snapshot']=str(path.relative_to(R));q['sha256']=sha(path)
        a.run_until(p['source_tick']);answer=n.obs(a,p['B'])
        return{'plan':p,'command':command,'frames':frames,'B':answer,'requests':n.receipts(a,p['requests']),'final':physical(a.world,occupation=True)}
    v=run(life,life,fn)['result'];print(json.dumps({'command':v['command'],'turns':[{'index':z['index'],'tick':z['tick'],'native':z['native'],'outgoing':z['turn']['outgoing']}for z in v['frames']if z['tick']==z['turn']['tick']],'B':v['B']},ensure_ascii=False),flush=True)
if __name__=='__main__':execute()
