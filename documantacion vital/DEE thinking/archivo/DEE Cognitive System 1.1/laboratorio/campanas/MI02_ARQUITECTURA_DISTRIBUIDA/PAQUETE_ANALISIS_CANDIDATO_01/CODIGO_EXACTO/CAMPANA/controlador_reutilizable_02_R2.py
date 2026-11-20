"""R2 only repairs metadata serialization; new lives, no R1 future overwritten."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from capacidades import arquitectura_distribuida_mi02 as b
cases=[(30,'intact','intact'),(31,'intact','omit_return'),(32,'cut_action','intact'),(33,'cut_return','intact'),(34,'sham_cut','intact')]
conditions=[-1]*5+[1]*5+[-1]*4
atomic_json(E/'CONTROLADOR_PROTOCOLO_02_R2.json',{'cases':cases,'availability':conditions,'difference_from_R1':'Tuples converted to exact JSON lists for official metadata serializer. No physical or target rule changed. R1life20 remains at failedT26.','criterion_before_results':'Actual native direction/contacts and later stored-field differences, useful must match predeclared current affordance. Same clocks and baseline samples. No new update fromPython.','independence':'New T0 diagnostic worlds, same prepared geometry. Not pooled learning of one MAIN.','controls':'Return omitted; action physically blocked; return physically blocked; same-dose off-route sham. All source admissions recorded.'})
for case,control,mode in cases:
    life='MI02_CONTROLADOR_'+str(case);create(life,41)
    run(life,'CONTROLADOR_PREPARAR_'+str(case),lambda a,control=control:b.prepare(a,center=[20,20,20],control=control))
    result=run(life,'CONTROLADOR_VIVIR_'+str(case),lambda a,mode=mode:b.live(a,availability=conditions,mode=mode,trace=True))
    print(json.dumps({'case':case,'rows':[{'tick':x['critical_tick'],'availability':x['availability'],'choice':x['physical_choice'],'M_before':[v['s_reg']for v in x['frames'][0]['M']],'M_after':[v['s_reg']for v in x['frames'][-1]['M']],'Q_after':x['frames'][-1]['Q']['direction']}for x in result['rows']],'final':result['final']['physical']},ensure_ascii=False),flush=True)
