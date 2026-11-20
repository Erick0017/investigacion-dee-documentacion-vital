"""Fixed-before-run reserved curricula and actual-action controls for R8."""
import random,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from retorno_exterior_11 import createbody
from capacidades import arquitectura_distribuida_mi02_r8 as b
rng=random.Random(82161);conditions=[]
for sign in(-1,1,-1,1):conditions.extend([sign]*rng.randrange(4,7))
second=[1]*4+[-1]*6+[1]*5+[-1]*5
atomic_json(E/'RESERVA_RETORNO_16_FIJADA.json',{'conditions':conditions,'second_history':second,'cases':{'141':'intact','142':'sham','143':'cut_action','144':'intact other history'},'no_posthoc_phase_search':True,'hypothesis':'A recurrent actual action/consequence path, not merely native age or readout labels, permits useful adjustment across reversals.','independence':'New T0 lives, deterministic common architecture. Opportunities within a life are dependent, not independent replicates.'})
for case,control,seq in[(141,'intact',conditions),(142,'sham_cut',conditions),(143,'cut_action',conditions),(144,'intact',second)]:
    life='MI02_RESERVA_RETORNO_'+str(case);createbody(life,control);run(life,'RESERVA16_PREPARAR_'+str(case),lambda a:b.prepare(a,center=[8,8,8]))
    z=run(life,'RESERVA16_VIVIR_'+str(case),lambda a,seq=seq:b.live(a,availability=seq,trace=True))
    print(json.dumps({'case':case,'useful_material':sum(x['useful_material_action']for x in z['rows']),'opportunities':len(z['rows']),'choices':[x['physical_choice']for x in z['rows']],'conditions':seq}),flush=True)
