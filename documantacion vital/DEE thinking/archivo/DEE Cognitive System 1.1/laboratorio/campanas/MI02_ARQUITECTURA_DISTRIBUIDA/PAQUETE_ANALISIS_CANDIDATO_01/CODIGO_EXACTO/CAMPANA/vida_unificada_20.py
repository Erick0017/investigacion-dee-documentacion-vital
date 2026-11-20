"""R4 blank persistent social recipients, dual-role x0 honestly declared."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from app.lives import WorldAdapter
from capacidades.geometria_distribuida_mi02_r4 import unified_recipe
from capacidades import integracion_distribuida_mi02_r4 as b
atomic_json(E/'PROTOCOLO_UNIFICADO_20.json',{'conditions':[-1]*5+[1]*6+[-1]*4,'N':26,'hypothesis':'R3 responses entered A context and changed native directions, but only on the phase opposite motor contact. Blank supported recipients now retain physically delivered B content for use at later contacts. R0 balanced code keeps its actual default-left motor role while its stream can initiate B query; no exclusive action/ask policy is claimed.','controls':['formed-query cut','formed-message cut','returncut','private history reversed'],'not_preloaded':'Recipients begin empty and get no teacher. Generic zero-load support does not contain the private sign.'})
for case,control,private in[(160,'intact',(47,17)),(161,'cut_query',(47,17)),(162,'cut_message',(47,17)),(163,'cut_return',(47,17)),(164,'intact',(17,47))]:
    life='MI02_UNIFICADA_'+str(case);r,g=unified_recipe(control=control);sources=archive();a=WorldAdapter(d.OrganizationalWorld.create(r));p=E/(life+'.PREPARACION_T0.deetsnap.gz');a.save(p);Store().import_state(p,life,'fisica_directa',expected=sha(p));atomic_json(E/(life+'.RECETA_T0.json'),{'sources':sources,'geometry':g,'new_untrained_T0':True,'no_E1_memory_transplant':True})
    run(life,'UNIFICADA20_ADQUIRIR_'+str(case),lambda a,g=g,private=private:b.acquire(a,geometry=g,private=private))
    z=run(life,'UNIFICADA20_VIVIR_'+str(case),lambda a:b.live(a,availability=[-1]*5+[1]*6+[-1]*4))
    print(json.dumps({'case':case,'useful':sum(bool(x['useful_material_actions'])for x in z['rows']),'queries':sum(x['query_material']for x in z['rows']),'B_active_frames':sum(f['B']['state']>0 for x in z['rows']for f in x['frames']),'rows':[{'t':x['critical_tick'],'available':x['availability'],'useful':x['useful_material_actions'],'failed':x['failed_material_actions'],'query':x['query_material'],'M':[v['s_reg']for v in x['frames'][-1]['M']]}for x in z['rows']]},ensure_ascii=False),flush=True)
