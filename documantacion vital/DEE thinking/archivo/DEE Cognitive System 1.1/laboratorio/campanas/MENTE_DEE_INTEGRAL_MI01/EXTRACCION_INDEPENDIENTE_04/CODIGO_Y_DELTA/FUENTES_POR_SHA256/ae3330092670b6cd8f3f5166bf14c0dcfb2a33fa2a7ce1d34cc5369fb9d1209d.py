"""Bounded construction contrast; no training reset or memory transplant."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.mente_integral_mi01 import preparacion_compartida as compiler,fallo_y_consulta as candidate

configs=[(330,True),(331,False)]
atomic_json(E/'BUCLE_CONSECUENCIAS_DISENO_R6.json',{'parent':'E1_MI01_MAIN T24752','cases':configs,'availability':[1,-1,1,-1,1],'private_B_raw':[20,52,20,52,20],'question':'Does restoring the declared native actor-consequence route sustain the decision loop, unlike the short failure-only apparatus?','not_claimed':'The turn mapping and opportunities are prepared. Native consequences may alter subsequent command content; no broad R2 claim.'})
for number,actor_return in configs:
    life='MI01_BUCLE_'+str(number);fork('E1_MI01_MAIN',life)
    def fn(a,number=number,actor_return=actor_return):
        p=compiler.prepare(a,builder='direct_failure',name=life,availability=[1,-1,1,-1,1],private_values=[20,52,20,52,20],mode='intact',actor_return=actor_return)
        a.save(E/(life+'.PREPARADO.deetsnap.gz'));v=candidate.advance(a,name=life);a.save(E/(life+'.FINAL.deetsnap.gz'))
        return{'plan':p,'trajectory':v,'final':physical(a.world,occupation=True)}
    v=run(life,life,fn)['result'];print(json.dumps({'case':number,'commands':[[z['index'],z['native']['direction'],z['native']['s_reg']]for z in v['trajectory']['frames']if z['kind']=='command'],'requests':[[z['index'],z['native']['direction'],z['native']['s_reg']]for z in v['trajectory']['failure_frames']if z['kind']=='failure_request'],'occupied':v['final']['occupied']},ensure_ascii=False),flush=True)
