"""R6 separates the incoming environmental sources from the outgoing action."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from preparacion_fondo_inmovil_r6 import new_life
from capacidades import arquitectura_distribuida_mi02_r6 as b
conditions=[-1]*4+[1]*4+[-1]*3
atomic_json(E/'CONTROLADOR_PROTOCOLO_07.json',{'revision':'R6','conditions':conditions,'hypothesis':'R5 contact source rejected because it injected against the actual outbound stream. Three off-axis zero-load contributions implement the same signed contact outcome without counterflow injection. Physics, not the host, combines the actual action with those prequeued fields.','metric':'Material action at open contact required for useful action. Failed contact is separately recognized by its turned physical product. Choice agreement alone is insufficient.'})
for case,control,mode in[(70,'intact','intact'),(71,'intact','omit_return'),(72,'cut_action','intact'),(73,'cut_return','intact'),(74,'sham_cut','intact')]:
    life='MI02_CONTROLADOR_'+str(case);new_life(life,control=control)
    run(life,'CONTROLADOR_PREPARAR_'+str(case),lambda a,control=control:b.prepare(a,center=[8,8,8],control=control))
    result=run(life,'CONTROLADOR_VIVIR_'+str(case),lambda a,mode=mode:b.live(a,availability=conditions,mode=mode,trace=True))
    print(json.dumps({'case':case,'rows':[{'tick':x['critical_tick'],'availability':x['availability'],'choice':x['physical_choice'],'material':x['material_action'],'failure':x['failure_product'],'useful':x['useful_material_action'],'M_before':[v['s_reg']for v in x['frames'][0]['M']],'M_after':[v['s_reg']for v in x['frames'][-1]['M']]}for x in result['rows']],'occupied':result['final']['physical']['occupied']},ensure_ascii=False),flush=True)
