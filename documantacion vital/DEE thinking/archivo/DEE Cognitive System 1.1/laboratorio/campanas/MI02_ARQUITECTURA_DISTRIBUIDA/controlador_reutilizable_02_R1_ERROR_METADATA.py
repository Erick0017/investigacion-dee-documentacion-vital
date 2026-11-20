"""First native recurrent controller, own experience and phase-gated consequence."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from capacidades import arquitectura_distribuida_mi02 as b
cases=[(20,'intact','intact'),(21,'intact','omit_return'),(22,'cut_action','intact'),(23,'cut_return','intact'),(24,'sham_cut','intact')]
atomic_json(E/'CONTROLADOR_PROTOCOLO_02.json',{'cases':cases,'availability':[-1]*5+[1]*5+[-1]*4,'criterion_before_results':'Native Q action from persistent acquired fields; useful must match the current world affordance. First baseline acquisition is not utility learning. Compare actual memory differences and later common Q, not just activity.','history':'Independent new T0 worlds with identical prepared source laws/initial raw baseline10,10; no trained fields imported. Not five independent biological subjects or a general-policy evaluation.','new_physical_mechanism':'Ordinary local neighbour context can alter native friction increments at an odd391 boundary. Requires actual contact and path. Check omitted return, action interception, return interception and sham.','no_hidden_update':'The source law reads availability only before responses. It does not read Q to select a correction or write memory contents.'})
for case,control,mode in cases:
    life='MI02_CONTROLADOR_'+str(case);create(life,41)
    run(life,'CONTROLADOR_PREPARAR_'+str(case),lambda a,control=control:b.prepare(a,center=[20,20,20],control=control))
    result=run(life,'CONTROLADOR_VIVIR_'+str(case),lambda a,mode=mode:b.live(a,availability=[-1]*5+[1]*5+[-1]*4,mode=mode,trace=True))
    print(json.dumps({'case':case,'rows':[{'tick':x['critical_tick'],'availability':x['availability'],'choice':x['physical_choice'],'M_before':[v['s_reg']for v in x['frames'][0]['M']],'M_after':[v['s_reg']for v in x['frames'][-1]['M']],'Q_after':x['frames'][-1]['Q']['direction']}for x in result['rows']],'final':result['final']['physical']},ensure_ascii=False),flush=True)
