"""Continue actual R6 candidate and matched controls through two reversals."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from capacidades import integracion_distribuida_mi02_r6 as b
seq=[1]*6+[-1]*5
atomic_json(E/'PROTOCOLO_UNIFICADO_24.json',{'parent_lives':[180,181,182,184],'continuation_conditions':seq,'not_resets':True,'question':'Does the retained private-context advantage coexist with later action learning, and what reversal cost does it introduce?','controls':'Original query-cut/message-cut/opposite-private histories continue from their own real endpoints, not patched or merged states.'})
for case in(180,181,182,184):
    z=run('MI02_UNIFICADA_'+str(case),'UNIFICADA24_VIVIR_'+str(case),lambda a:b.live(a,availability=seq))
    print(json.dumps({'case':case,'useful':sum(bool(v['useful_material_actions'])for v in z['rows']),'opportunities':len(z['rows']),'rows':[(v['critical_tick'],v['availability'],v['useful_material_actions'],v['failed_material_actions'],[m['s_reg']for m in v['frames'][-1]['M']])for v in z['rows']],'B':z['final']['regions']['B']},ensure_ascii=False),flush=True)
