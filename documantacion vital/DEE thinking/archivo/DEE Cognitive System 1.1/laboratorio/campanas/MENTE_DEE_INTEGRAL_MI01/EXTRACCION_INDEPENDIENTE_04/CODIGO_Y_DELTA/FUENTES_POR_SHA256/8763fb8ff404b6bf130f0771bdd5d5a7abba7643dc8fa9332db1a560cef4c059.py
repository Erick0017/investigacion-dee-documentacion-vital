"""R7 uses unseen private contents to examine a fixed P0 repair."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.mente_integral_mi01 import contexto_B_preparado as builder,fallo_y_consulta as candidate
cases=[(340,'fixed43'),(341,'zero'),(342,'sham43')]
atomic_json(E/'CONTEXTO_B_RECURRENTEMENTE_R7_PROTOCOLO.json',{'cases':cases,'parent':'MI01_BASE_HISTORICA_T23453, exact identified MAIN past, not continuation of current MAIN','availability':[1,-1],'private_B_raw':[14,61],'fixed_context':43,'reason':'307 existing full local snapshots: first B request used a43 historical contextual contribution, second arrival145 succeeded but43 absent. This new stationary P0 frame is explicitly designed, not recovered memory. Full actor-return330 caused new expansion and was NOT silently substituted for this short matched failure/query contrast.','criterion':'Repeated private-dependent B output and subsequent native selection after actual failed action; controls retain the same private samples/helper0 and remove only the43frame effect. No sustained useful policy is inferred from two opportunities.','unseen_private_values':True,'source_basis':'The43 scalar was calibrated on construction traces with20/52, not chosen from these new outcomes.'})
for number,context in cases:
    life='MI01_CONTEXTO_B_'+str(number);fork('MI01_BASE_HISTORICA_T23453',life)
    def fn(a,context=context,life=life):
        from capacidades import mente_integral_mi01 as mi
        experience=mi.train(a,episode=life+'.own_experience',contexts=[-1,1],feedback='paired',center=[40,35,55])
        p=builder.prepare(a,builder='direct_failure',name=life,availability=[1,-1],private_values=[14,61],mode='intact',actor_return=False,b_context=context)
        a.save(E/(life+'.PREPARADO.deetsnap.gz'));v=candidate.advance(a,name=life);a.save(E/(life+'.FINAL.deetsnap.gz'))
        return{'experience':experience,'plan':p,'trajectory':v,'final':physical(a.world,occupation=True)}
    v=run(life,life,fn)['result'];print(json.dumps({'case':number,'commands':[[z['index'],z['native']['direction'],z['native']['s_reg']]for z in v['trajectory']['frames']if z['kind']=='command'],'private_responses':[[z['index'],z['native']['direction'],z['native']['s_reg']]for z in v['trajectory']['frames']if z['kind']=='source_tick'],'failure':[[z['index'],z['kind'],z['native']['direction'],z['native']['s_reg']]for z in v['trajectory']['failure_frames']if z['kind']in('failure_request','private_source')],'occupied':v['final']['occupied']},ensure_ascii=False),flush=True)
