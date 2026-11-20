"""Post-reserve causal diagnosis. P0 interception, never a MAIN repair."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from controles_desde_prefijo_fijado import prefix,name
from capacidades.mente_integral_mi01 import externo_selector as motor
from capacidades.integracion_situada_01 import ic_native_core as n
cases=[(476,'intercept_188'),(477,'offpath_sham')]
atomic_json(E/'COALESCENCIA_INTERVENCION_PROTOCOLO_476.json',{'cases':cases,'prefix_sha256':sha(prefix()),'discovery':'473/475 full states: target[25,56,41] empty25008, incoming150from[24,56,40]dir+X+Z and188from[24,57,41]dir+X-Y, post338dir+X-Y+Z25009. This is a multiple-antecedent native combination, not unique packet lineage.','intervention':'Legal SEM4load0 at[24,57,41] boundary25007, before the188formation/arrival. Same dose/time atZ+19 for sham. This changes the local physical context and is explicitly a prepared P0 intervention, not a learned strategy or an algebraically pure deletion.','criteria':'Guard must be admitted; B native150 remains; local unwanted338 combination changes; measure downstream R and S without changing decoders. Test seven external steps and three old code ports at their original phase3.','scope':'Exploratory causal check selected AFTER the fixed evaluation. Does not change its scores/architecture, does not import any future to MAIN and does not establish188is useless elsewhere.'})
for number,mode in cases:
    life='MI01_COALESCENCIA_'+str(number);fork('E1_MI01_MAIN',life,checkpoint=prefix())
    def fn(a,mode=mode,life=life):
        site=[24,57,41]
        if mode=='offpath_sham':site=n.move(site,(0,0,1),19)
        req=n.submit(a,'MI01.postreserve.'+life,site,(0,0,0),25007,0,4);before=n.obs(a,site);frames=[];original=a.run_until
        def watch(t):
            for when in(25005,25007,25008,25009,25011,25061,25154):
                if a.tick<when<=t:
                    original(when);p=E/(life+'.T'+str(when)+'.DIAGNOSTICO_NO_OPERATIVO.deetsnap.gz');a.save(p);frames.append({'tick':when,'B':n.obs(a,[21,59,40]),'K':n.obs(a,[25,56,41]),'intrusive_site':n.obs(a,[24,57,41]),'R':n.obs(a,[27,56,43]),'S':n.obs(a,[40,35,55]),'old_banks':[n.obs(a,q)for q in([31,59,26],[11,59,23],[11,48,29])],'physical':physical(a.world,occupation=True),'diagnostic_snapshot':str(p.relative_to(R)),'sha256':sha(p)})
            original(t)
        a.run_until=watch
        try:v=motor.run(a,steps=7,mode='closed',feedback='cost',transition=True,habitat=name,motor_codec='native_body_roles')
        finally:a.run_until=original
        return{'external':v,'guard_request':n.receipts(a,[req])[0],'guard_before':before,'frames':frames,'final':physical(a.world,occupation=True),'not_claimed':'No learned autonomous protection or generalR2. Alternative diagnostic branch, not a rewritten reserved MAIN.'}
    v=run(life,'MI01_'+str(number)+'_COALESCENCIA_INTERVENCION',fn)['result'];print(json.dumps({'case':number,'receipt':v['guard_request']['receipt'],'frames':[{'tick':r['tick'],'K':r['K'],'R':r['R'],'S':r['S']}for r in v['frames']],'actions':[r['executed_torque']for r in v['external']['rows']]},ensure_ascii=False),flush=True)
