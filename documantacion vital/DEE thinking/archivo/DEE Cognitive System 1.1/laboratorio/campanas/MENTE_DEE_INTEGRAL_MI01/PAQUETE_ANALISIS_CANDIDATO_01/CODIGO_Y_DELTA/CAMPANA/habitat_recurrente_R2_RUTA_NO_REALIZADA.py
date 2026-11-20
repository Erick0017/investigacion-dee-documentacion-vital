"""Finite complete native body comparison before frozen integrated reserves."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import mente_integral_mi01 as mi
from capacidades.mente_integral_mi01 import habitat_nativo as habitat
configs=[(235,'intact'),(236,'omit_actor_return'),(237,'cut_actor'),(238,'sham_actor'),(239,'cut_question')]
availability=[1,1,-1,-1,1,1];private=[20,20,52,52,20,20]
atomic_json(E/'HABITAT_PROTOCOLO_R2_235.json',{'parent':'MI01_BASE_HISTORICA_T23453','revision':'R2 explicit orthogonal final approach and odd triangular prefix when required; R1failed preparation230 retained with its pending future, not reused','cases':configs,'availability':availability,'private_B_raw':private,'utility_auditor':'Actual positive route contact yields+1whenavailable, -1whenunavailable; no action0. Query use/content and command validity reported separately. The law,335tick opportunities and sign mapping are prepared, not learned.','criterion':'Actual query -> private response -> changed S command -> actual native contact -> consequent later native command, not host scheduling a skill after seeing its answer. Body opportunities all frozen before first action.','coverage':'Six correlated opportunities per actual branch, not six learners. Fixed native horizon includes six335tick returns.'})
for number,mode in configs:
    life='MI01_HABITAT_'+str(number);fork('MI01_BASE_HISTORICA_T23453',life)
    def fn(a,number=number,mode=mode):
        training=mi.train(a,episode='MI01_EXT_130',contexts=[-1,1],feedback='paired',center=[40,35,55]);p=habitat.prepare(a,name=life,availability=availability,private_values=private,mode=mode)
        a.save(E/(life+'.PREPARADO.deetsnap.gz'));r=habitat.advance(a,name=life);a.save(E/(life+'.FINAL.deetsnap.gz'))
        return{'experience':training,'plan':p,'trajectory':r,'final':physical(a.world,occupation=True)}
    v=run(life,life,fn)['result'];print(json.dumps({'case':number,'commands':[[z['index'],z['native']['direction'],z['native']['s_reg']]for z in v['trajectory']['frames']if z['kind']=='command'],'contacts':[[z['index'],z['native']['direction'],z['native']['s_reg']]for z in v['trajectory']['frames']if z['kind']=='contact'],'occupation':v['final']['occupied']},ensure_ascii=False),flush=True)
