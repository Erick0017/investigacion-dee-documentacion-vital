"""R7 bounded contact-source crossing correction, no after-the-fact rescue."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from preparacion_fondo_inmovil_r7 import new_life
from capacidades import arquitectura_distribuida_mi02_r7 as b
atomic_json(E/'CONTROLADOR_PROTOCOLO_09.json',{'revision':'R7','availability':[-1,-1,1,-1],'hypothesis':'R6 control sources for r0 and r1 crossed one tick before distinct contacts and combined, removing a requiredZ contribution. Fixed r0 geometric helper triple now avoids that intersection; outcome still requires an actual Q action.','budget_rule':'If physical first links remain absent after this bounded revision, stop extending this family and investigate distributed cooperation.'})
for case,control,mode in[(80,'intact','intact'),(81,'intact','omit_return'),(82,'cut_return','intact')]:
    life='MI02_CONTROLADOR_'+str(case);new_life(life,control=control)
    run(life,'CONTROLADOR_PREPARAR_'+str(case),lambda a,control=control:b.prepare(a,center=[8,8,8],control=control))
    z=run(life,'CONTROLADOR_VIVIR_'+str(case),lambda a,mode=mode:b.live(a,availability=[-1,-1,1,-1],mode=mode,trace=True))
    print(json.dumps({'case':case,'rows':[{'t':x['critical_tick'],'choice':x['physical_choice'],'failure':x['failure_product'],'useful':x['useful_material_action'],'M_after':[v['s_reg']for v in x['frames'][-1]['M']]}for x in z['rows']]},ensure_ascii=False),flush=True)
