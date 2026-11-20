"""Exact before/after B operand context at the two original query epochs."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.integracion_situada_01 import ic_native_core as n
def execute():
    source=E/'MI01_COLA_B_300.PREPARADO.deetsnap.gz';life='MI01_B_OPERANDOS_306';Store().import_state(source,life,'cpc9_integral_n67',sha(source))
    def fn(a):
        frames=[];geom=a.transferred_quantity.geometry;B=geom['center']
        for center in(23865,24200):
            for t in range(center-2,center+3):
                a.run_until(t);path=E/(life+'.T'+str(t)+'.deetsnap.gz');a.save(path)
                frames.append({'tick':t,'center':n.obs(a,B),'reference_hub':n.obs(a,geom['reference_hub']),'reference_site':n.obs(a,geom['reference_site']),'object_hub':n.obs(a,geom['object_hub']),'object_site':n.obs(a,geom['object_site']),'context125':[n.obs(a,n.move(B,(x,y,z)))for x in(-2,-1,0,1,2)for y in(-2,-1,0,1,2)for z in(-2,-1,0,1,2)],'snapshot':str(path.relative_to(R)),'sha256':sha(path)})
        return{'frames':frames,'final':physical(a.world,occupation=True)}
    v=run(life,life,fn)['result'];print(json.dumps([{k:z[k]for k in('tick','center','reference_site','object_site')}for z in v['frames']],ensure_ascii=False),flush=True)
if __name__=='__main__':execute()
