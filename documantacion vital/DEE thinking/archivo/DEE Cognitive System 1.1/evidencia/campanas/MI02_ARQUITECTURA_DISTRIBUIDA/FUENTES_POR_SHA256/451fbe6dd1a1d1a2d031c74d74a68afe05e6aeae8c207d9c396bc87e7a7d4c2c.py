"""Finite severity contrasts on identical complete R6 prefix, no repairs."""
import sys,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from capacidades import integracion_distribuida_mi02_r6 as shared
from capacidades import arquitectura_distribuida_mi02_r8 as n

plan=[('none',0,19,0),('nominal',16,19,20),('amplitude',16,19,1000),('destructive',160,1,1000),('away_sham',160,1,1000)]
atomic_json(E/'ESTRES37_FIJADO.json',{'source_life':'MI02_UNIFICADA_180','source':Store().record('MI02_UNIFICADA_180'),'variants':plan,'seed':82370,'window':320,'followup_availability':[-1]*3+[1]*3,'criteria':'Admitted/rejected sensor packets, changes in acquired fields, actual contact utility/absence/conflict and native B activity. No phase repair, clearing, memory reset or lower stress after a bad result. Each branch continues after its own stress history.','not_claimed':'Independent minds from shared prefix, infinite resilience, energy metabolism or learned regulation','sources':archive()})

def perturb(a,label,count,cadence,cap):
    g=shared.saved(a)['geometry'];start=a.tick;rr=[];rng=random.Random(82370);before=shared.state(a)
    for i in range(count):
        for p in g['external_sensors'][:2]:
            v=p['direction']if label!='away_sham'else[-z for z in p['direction']]
            rr.append(n.send(a,'MI02.stress.'+label+'.'+p['name'],p['origin'],v,start+1+i*cadence,rng.randrange(cap+1)))
    frames=[]
    for dt in(1,2,5,7,8,16,32,64,128,160,192,256,320):
        a.run_until(start+dt);frames.append({'tick':a.tick,'A':n.obs(a,g['A']),'B':n.obs(a,g['B']),'M':[n.obs(a,p)for p in n.get(a)['memories']]})
    return{'variant':label,'before':before,'requests':n.receipts(a,rr),'passive_frames':frames,'after':shared.state(a),'all_scheduled_noise_finished':not a.world.runtime.pending_inputs}

cuts=[]
for label,count,cadence,cap in plan:
    life='MI02_ESTRES37_'+label;fork('MI02_UNIFICADA_180',life)
    run(life,'ESTRES37_'+label,lambda a,label=label,count=count,cadence=cadence,cap=cap:perturb(a,label,count,cadence,cap))
    stress_cut=Store().record(life)
    run(life,'ESTRES37_USO_'+label,lambda a:shared.live(a,availability=[-1]*3+[1]*3))
    cuts.append({'life':life,'after_stress':stress_cut,'after_use':Store().record(life)})
atomic_json(E/'ESTRES37_CORTES.json',cuts)
