"""Last bounded construction family, from actual current MAIN, no retraining."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.mente_integral_mi01 import contexto_B_preparado as builder,fallo_y_consulta as candidate
cases=[(350,'fixed43','intact'),(351,'fixed43','omit_failure_return'),(352,'zero','intact')]
atomic_json(E/'FALLO_INICIAL_R8_PROTOCOLO.json',{'cases':cases,'parent':'E1_MI01_MAIN T24752, own acquired+Y145 preserved','availability':[-1,-1,1,1],'private_raw':[14,61,14,61],'change':'Same native failure product opportunity also exists at the first encounter; this is a declared timing/generalization extension of270, not a host observation of failure. No new S training.','criterion':'Native first act failure, formed question, B reply, subsequent query/action choices and at least one useful positive contact after the environment changes. Every incomplete chain is retained.','limits':'P0 failure-detection/transduction law and scalar frame remain prepared. No general R2 claim.'})
for number,context,mode in cases:
    life='MI01_FALLO_INICIAL_'+str(number);fork('E1_MI01_MAIN',life)
    def fn(a,life=life,context=context,mode=mode):
        p=builder.prepare(a,builder='direct_failure',name=life,availability=[-1,-1,1,1],private_values=[14,61,14,61],mode=mode,actor_return=False,include_initial_failure=True,b_context=context)
        a.save(E/(life+'.PREPARADO.deetsnap.gz'));v=candidate.advance(a,name=life);a.save(E/(life+'.FINAL.deetsnap.gz'))
        return{'plan':p,'trajectory':v,'final':physical(a.world,occupation=True)}
    v=run(life,life,fn)['result'];print(json.dumps({'case':number,'commands':[[z['index'],z['native']['direction'],z['native']['s_reg']]for z in v['trajectory']['frames']if z['kind']=='command'],'failure':[[z['index'],z['kind'],z['native']['direction'],z['native']['s_reg']]for z in v['trajectory']['failure_frames']if z['kind']in('failure_request','private_source','failure_return')],'occupied':v['final']['occupied']},ensure_ascii=False),flush=True)
