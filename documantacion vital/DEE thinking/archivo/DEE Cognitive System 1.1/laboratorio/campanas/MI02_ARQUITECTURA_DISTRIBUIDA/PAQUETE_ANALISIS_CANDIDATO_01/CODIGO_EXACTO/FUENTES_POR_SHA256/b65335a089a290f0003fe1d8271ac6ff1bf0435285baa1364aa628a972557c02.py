"""Integrated construction candidate, not MAIN final reserves yet."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from app.lives import WorldAdapter
from capacidades.geometria_distribuida_mi02 import unified_recipe
from capacidades import integracion_distribuida_mi02 as b
atomic_json(E/'PROTOCOLO_UNIFICADO_17.json',{'conditions':[-1]*6+[1]*4+[-1]*4,'hypothesis':'A history-produced x0 query activates a dormant B reader, whose private acquired relation returns and combines with A history. Native action consequences and local learning remain active.','codecs':'x+ motorleft, x- motorright, x0 request. No native waiting is inferred from silence.','not_MAIN_yet':'Construction trials compare a declared query cut and an omitted return, before selecting a final continuous candidate.'})
for case,control,mode in[(120,'intact','intact'),(121,'cut_query','intact'),(122,'intact','omit_return'),(123,'no_gate_resource','intact')]:
    life='MI02_UNIFICADA_'+str(case);r,g=unified_recipe(control=control);sources=archive();a=WorldAdapter(d.OrganizationalWorld.create(r));p=E/(life+'.PREPARACION_T0.deetsnap.gz');a.save(p);Store().import_state(p,life,'fisica_directa',expected=sha(p));atomic_json(E/(life+'.RECETA_T0.json'),{'sources':sources,'geometry':g,'new_untrained_T0':True,'no_E1_memory_transplant':True})
    run(life,'UNIFICADA17_ADQUIRIR_'+str(case),lambda a,g=g:b.acquire(a,geometry=g))
    z=run(life,'UNIFICADA17_VIVIR_'+str(case),lambda a,mode=mode:b.live(a,availability=[-1]*6+[1]*4+[-1]*4,mode=mode))
    print(json.dumps({'case':case,'useful':sum(bool(x['useful_material_actions'])for x in z['rows']),'queries':sum(x['query_material']for x in z['rows']),'B_active_frames':sum(f['B']['state']>0 for x in z['rows']for f in x['frames']),'rows':[{'t':x['critical_tick'],'available':x['availability'],'useful':x['useful_material_actions'],'failed':x['failed_material_actions'],'query':x['query_material'],'M':[v['s_reg']for v in x['frames'][-1]['M']]}for x in z['rows']]},ensure_ascii=False),flush=True)
