"""R4 first finite test. All data, including no learning, remain primary."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from preparacion_fondo_inmovil import new_life
from capacidades import arquitectura_distribuida_mi02_r4 as b
conditions=[-1]*4+[1]*4+[-1]*3
atomic_json(E/'CONTROLADOR_PROTOCOLO_04.json',{'availability':conditions,'new_design':'R4 leaves fixed open channels, material anchors and native state0SEM4 background. This is externally prepared P0, not erasing an E1 landscape or learned regulation. New livesT0.','learning_hypothesis':'The same native return can change local neighbour conditions during an odd391boundary and hence subsequent Q choices. No message or update value is delivered to memories.','controls':'No-return/action-cut/return-cut/sham, if first intact trajectory gives a usable link. Execution may be bounded to the informative contrasts, not invented positives.','cost_of_architecture':'Pinned zero-state sites are nonzeroRAW and causal constraints. Low state-positive occupation is not free memory.'})
for case,control,mode in[(50,'intact','intact'),(51,'intact','omit_return'),(52,'cut_action','intact'),(53,'cut_return','intact'),(54,'sham_cut','intact')]:
    life='MI02_CONTROLADOR_'+str(case);new_life(life,control=control)
    run(life,'CONTROLADOR_PREPARAR_'+str(case),lambda a,control=control:b.prepare(a,center=[8,8,8],control=control))
    result=run(life,'CONTROLADOR_VIVIR_'+str(case),lambda a,mode=mode:b.live(a,availability=conditions,mode=mode,trace=True))
    print(json.dumps({'case':case,'rows':[{'tick':x['critical_tick'],'availability':x['availability'],'choice':x['physical_choice'],'M_before':[v['s_reg']for v in x['frames'][0]['M']],'M_after':[v['s_reg']for v in x['frames'][-1]['M']],'Q_after':x['frames'][-1]['Q']['direction']}for x in result['rows']],'final':result['final']['physical']},ensure_ascii=False),flush=True)
