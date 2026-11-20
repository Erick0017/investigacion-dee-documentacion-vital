"""R3 engineering hypothesis: return outside the dense shared-memory zone."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from capacidades import arquitectura_distribuida_mi02_r3 as b
cases=[(40,'intact','intact'),(41,'intact','omit_return'),(42,'cut_action','intact'),(43,'cut_return','intact'),(44,'sham_cut','intact')]
conditions=[-1]*5+[1]*5+[-1]*4
atomic_json(E/'CONTROLADOR_PROTOCOLO_03.json',{'cases':cases,'availability':conditions,'revision':'R3 changes physical return paths and absorber positions. New T0 lives. No repair of R2.','geometry_hypothesis':'A shared intermediate return at[0,0,2] has enough permanent neighbours to persist and alter both memories. Route first outside the memory region, then approach only the relevant scalar field. Both inactive return ghosts point at fixed SEM4, not into memories. This is a testable engineering hypothesis, not an E1 discovery.','utility':'Action state1sem1(x,-1,-1);x>=0left,x<0right. A true null direction is not mapped to a useful wait. Current availability chosen before observing action.','checks':'Compare memories, native neighbour counts and actual source admission as well as later utility; no external native-state update.','scope':'Phase-dependent plasticity candidate; repeated fixed source-port law, not autonomous resource replenishment.'})
for case,control,mode in cases:
    life='MI02_CONTROLADOR_'+str(case);create(life,41)
    run(life,'CONTROLADOR_PREPARAR_'+str(case),lambda a,control=control:b.prepare(a,center=[20,20,20],control=control))
    result=run(life,'CONTROLADOR_VIVIR_'+str(case),lambda a,mode=mode:b.live(a,availability=conditions,mode=mode,trace=True))
    print(json.dumps({'case':case,'rows':[{'tick':x['critical_tick'],'availability':x['availability'],'choice':x['physical_choice'],'M_before':[v['s_reg']for v in x['frames'][0]['M']],'M_after':[v['s_reg']for v in x['frames'][-1]['M']],'Q_after':x['frames'][-1]['Q']['direction']}for x in result['rows']],'final':result['final']['physical']},ensure_ascii=False),flush=True)
