"""Selected technical reproduction with and without additional passive witnesses."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from capacidades import integracion_distribuida_mi02_r6 as b
from capacidades import arquitectura_distribuida_mi02_r8 as n
from capacidades.observador_causal_retrospectivo_01 import Snapshot,compare
old=json.loads((E/'UNIFICADA22_VIVIR_180.json').read_bytes());checkpoint=old['before']['snapshot'];outcomes=[]
for enabled in(False,True):
    life='MI02_TESTIGO26_'+('on'if enabled else'off');fork('MI02_UNIFICADA_180',life,checkpoint)
    def experiment(a):
        rows=[];checkpoints=[];original=a.run_until;g=b.saved(a)['geometry']
        def monitored(t):
            original(t)
            if enabled and 1170<=t<=1245:
                centers={'A':g['A'],'B':g['B'],'gate':g['query'][-1]['head']}
                fields={name:{'center':n.obs(a,p),'moore27':[n.obs(a,n.xyz(a,p,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]}for name,p in centers.items()}
                rows.append({'tick':t,'centers':fields,'query_turns':[n.obs(a,v['head'])for v in g['query']],'social_routes':[{'sign':r['sign'],'heads':[n.obs(a,p)for p in r['heads']],'recipient':n.obs(a,r['context'])}for r in g['social']['routes']]})
                if t in(1174,1205,1228,1230):
                    p=E/(life+'.T'+str(t)+'.DIAGNOSTICO_COMPLETO.deetsnap.gz');a.save(p);checkpoints.append({'tick':t,'file':str(p.relative_to(R)),'sha256':sha(p),'complete_world_with_original_future_inputs':True,'not_a_normal_operational_cut':'Detailed audit witness, not offered as a completed protocol continuation.'})
        a.run_until=monitored
        try:result=b.live(a,availability=[-1]*4+[1]*3)
        finally:a.run_until=original
        return{'result':result,'passive_witnesses':rows,'diagnostic_checkpoints':checkpoints,'instrument':'Additional native.observe calls only; no inputs, no selected actions, no agenda edits.'}
    run(life,'OBSERVACION26_'+str(enabled),experiment);outcomes.append(Store().record(life))
a=Snapshot(S/outcomes[0]['snapshot']);z=Snapshot(S/outcomes[1]['snapshot']);reference=Snapshot(S/old['after']['snapshot']);comparison=compare(a,z);reference_comparison=compare(a,reference)
atomic_json(E/'OBSERVACION26_VERIFICACION.json',{'with_without_additional_witnesses':comparison,'with_original_execution':reference_comparison,'identity_metadata_differences_declared':True,'technical_reproduction_not_independent_acquisition':True})
assert comparison['RAW_different_sites']==0 and comparison['clock_different_sites']==0 and comparison['pending_equal']and comparison['receipts_equal']and comparison['channels_equal']
assert reference_comparison['RAW_different_sites']==0 and reference_comparison['clock_different_sites']==0 and reference_comparison['pending_equal']and reference_comparison['receipts_equal']
print('Passive witness equality and selected technical reproduction verified',flush=True)
