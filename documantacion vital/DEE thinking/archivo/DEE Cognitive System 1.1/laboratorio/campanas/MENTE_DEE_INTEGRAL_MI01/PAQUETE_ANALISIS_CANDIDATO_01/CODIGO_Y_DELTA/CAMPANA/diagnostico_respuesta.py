"""Short causal window from the actual reached B-source snapshot."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
p=E/'MI01_PREGUNTA_RETORNO_90.FUENTE.deetsnap.gz';s=Store();life='MI01_RESPUESTA_096'
if s.life_dir(life).exists():raise FileExistsError(life)
s.import_state(p,life,'cpc9_integral_n67',sha(p))
from capacidades.integracion_situada_01 import ic_native_core as n
def fn(a):
    start=a.tick;B=list(a.transferred_quantity.geometry['center']);frames=[]
    for t in range(start,start+6):
        a.run_until(t);path=E/(life+'.T'+str(t)+'.deetsnap.gz');a.save(path);cells=[]
        for dx in range(-4,5):
            for dy in range(-4,5):
                for dz in range(-3,4):
                    p=[(B[0]+dx)%67,(B[1]+dy)%67,(B[2]+dz)%67];z=n.obs(a,p)
                    if z['s_reg']>=140 or (z['raw']!='0'and dx in(-1,0,1)and dy in(-1,0,1)and dz in(-1,0,1)):cells.append({'offset':[dx,dy,dz],**z})
        frames.append({'tick':t,'cells':cells,'snapshot':str(path.relative_to(R)),'sha256':sha(path),'global':physical(a.world,occupation=True)})
    return{'frames':frames}
v=run(life,life,fn)['result'];print(json.dumps([{'t':z['tick'],'cells':[p for p in z['cells']if p['s_reg']>=140]}for z in v['frames']],ensure_ascii=False),flush=True)
