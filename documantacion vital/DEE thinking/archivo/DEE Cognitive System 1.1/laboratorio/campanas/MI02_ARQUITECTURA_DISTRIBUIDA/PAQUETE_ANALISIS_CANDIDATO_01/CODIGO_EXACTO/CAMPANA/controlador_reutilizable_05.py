"""Bounded revision R5, four cycles before deciding whether to deepen it."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from preparacion_fondo_inmovil_r5 import new_life
from capacidades import arquitectura_distribuida_mi02_r5 as b
conditions=[-1,-1,1,-1]
atomic_json(E/'CONTROLADOR_PROTOCOLO_05.json',{'revision':'R5','conditions':conditions,'hypothesis':'Remove material sinks near contact; inert state0 boundary stops overflow without supplying alive neighbours. Move fixed reader bias to existing upper anchors. State>0 codec now frozen, native contact required for utility.','not_learning':'The geometry and codec revision are investigator design. Only subsequent native changes are candidate learning.'})
for case,control,mode in[(60,'intact','intact'),(61,'intact','omit_return'),(62,'cut_action','intact'),(63,'cut_return','intact')]:
    life='MI02_CONTROLADOR_'+str(case);new_life(life,control=control)
    run(life,'CONTROLADOR_PREPARAR_'+str(case),lambda a,control=control:b.prepare(a,center=[8,8,8],control=control))
    result=run(life,'CONTROLADOR_VIVIR_'+str(case),lambda a,mode=mode:b.live(a,availability=conditions,mode=mode,trace=True))
    print(json.dumps({'case':case,'rows':[{'tick':x['critical_tick'],'choice':x['physical_choice'],'material':x['material_action'],'useful':x['useful_material_action'],'M_before':[v['s_reg']for v in x['frames'][0]['M']],'M_after':[v['s_reg']for v in x['frames'][-1]['M']]}for x in result['rows']],'occupied':result['final']['physical']['occupied']},ensure_ascii=False),flush=True)
