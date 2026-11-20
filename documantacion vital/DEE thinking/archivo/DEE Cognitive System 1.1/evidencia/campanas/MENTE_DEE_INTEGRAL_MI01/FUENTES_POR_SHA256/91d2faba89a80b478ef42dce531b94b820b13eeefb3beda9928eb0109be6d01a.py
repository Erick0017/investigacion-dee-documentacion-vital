"""Third distinct family on actual late E1: contact plus event order.
One-shot direct composer, no preliminary material audit query to reteach it.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import espanol_funcional_01 as ef
configs=[(220,True,True,'AB'),(221,False,True,'AB'),(222,True,False,'AB'),(223,True,True,'BA')]

def execute():
    atomic_json(E/'RELACIONES_COMPUESTAS_PROTOCOLO_220.json',{'parent':'E1_MI01_MAIN24190','cases':configs,'frames':'Contact28,34,54 and order5,32,28; same admitted EF01 composer, no new semantics in kernel.','teaching':'Separate physical contact experience (medium3) and two events separated3ticks. Both class signals cued equally. Combination never taught as a complete answer.','evaluation':'One direct consumptive native composition, no preliminary query. Positive and missing-component/opposite-history controls. External fixed labels do not compute the conjunction.','claim_limit':'Prepared combining geometry, not learned grammar, new general NSM meanings or reusable infinite composition.'})
    for number,contact,event_b,order in configs:
        life='MI01_COMPUESTA_'+str(number);fork('E1_MI01_MAIN',life)
        def fn(a,number=number,contact=contact,event_b=event_b,order=order):
            initial=physical(a.world,occupation=True)
            if a.tick!=24190:raise ValueError('This experiment is fixed to the actual24190 MAIN prefix, not a silent later substitution')
            c=ef.contact_prepare(a,frame='MI01_CONTACTO_COMP',base=(28,34,54));cx=ef.contact_teach(a,frame='MI01_CONTACTO_COMP',present=contact,medium=3,signal=True)
            t=ef.temporal_prepare(a,frame='MI01_TIEMPO_COMP',origin=(5,32,28));tx=ef.temporal_experience(a,frame='MI01_TIEMPO_COMP',order=order,interval=3,event_b=event_b,signal=True)
            outcome=ef.compose_contact_temporal(a,contact_frame='MI01_CONTACTO_COMP',temporal_frame='MI01_TIEMPO_COMP');a.save(E/(life+'.RESULTADO.deetsnap.gz'))
            return{'initial':initial,'contact_geometry':c,'contact_experience':cx,'temporal_geometry':t,'temporal_experience':tx,'composition':outcome,'final':physical(a.world,occupation=True)}
        v=run(life,life,fn)['result'];print(json.dumps({'case':number,'composition':v['composition']['ENTE'],'legacy_bool':v['composition']['COMPOSITION_OBSERVED'],'occupation':v['final']['occupied']},ensure_ascii=False),flush=True)
if __name__=='__main__':execute()
