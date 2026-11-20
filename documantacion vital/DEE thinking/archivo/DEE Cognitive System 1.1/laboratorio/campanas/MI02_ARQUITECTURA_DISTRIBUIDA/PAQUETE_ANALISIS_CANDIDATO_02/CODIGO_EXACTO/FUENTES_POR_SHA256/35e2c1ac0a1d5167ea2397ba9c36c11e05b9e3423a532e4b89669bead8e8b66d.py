"""Continue the actual R8 lives; no reset on environment reversal."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from capacidades import arquitectura_distribuida_mi02_r8 as b
conditions=[-1]*5+[1]*7+[-1]*6
atomic_json(E/'PROTOCOLO_ACUMULACION_13.json',{'existing_parents':['MI02_CONTROLADOR_90','MI02_CONTROLADOR_91','MI02_CONTROLADOR_92'],'future_availability':conditions,'frozen_R8_architecture':True,'hypothesis':'R8 changed a later direction after recurrent physical consequences, but first environment reversal preceded useful adaptation. Longer fixed environmental runs distinguish learned adjustment from a single irreversible switch.','metric':'Actual material action at an available contact, not Q label alone. Retain all early mistakes and both reversals. No external reference memory update.'})
for case,mode in[(90,'intact'),(91,'omit_return'),(92,'intact')]:
    z=run('MI02_CONTROLADOR_'+str(case),'ACUMULACION13_'+str(case),lambda a,mode=mode:b.live(a,availability=conditions,mode=mode,trace=True))
    print(json.dumps({'case':case,'useful':sum(x['useful_material_action']for x in z['rows']),'requested_opportunities':len(z['rows']),'rows':[{'t':x['critical_tick'],'available':x['availability'],'choice':x['physical_choice'],'useful':x['useful_material_action'],'failure':x['failure_product'],'M':[v['s_reg']for v in x['frames'][-1]['M']]}for x in z['rows']]},ensure_ascii=False),flush=True)
