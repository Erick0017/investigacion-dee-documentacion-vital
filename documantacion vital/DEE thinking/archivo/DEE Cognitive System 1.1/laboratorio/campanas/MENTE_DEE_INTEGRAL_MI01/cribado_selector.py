"""Directed compatibility test: reuse AA/IC01 learning, no old trained state."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as integrated
from capacidades.integracion_situada_01 import ic_native_core as native,ic_body
from dee_thinking import _native as d
protocol={'question':'Can the previously exhausted late E1 geometry acquire a new local selector from admissible consequence experiences and use it in a recurrent native action/outcome loop?',
 'parent':'E1_MI01_MAIN after its actual first MI01 external step','histories':[(10,'paired',[1,-1]),(11,'paired',[-1,1]),(12,'omit',[1,-1])],
 'common_native_world_availability':[1,1,-1,-1,1,-1], 'preparation':'Existing AA/IC01 S50 anatomy and generic resources; no field writes or learned-state transplant',
 'reader':'ic_body.qualified: state1/semantic1/payload>0/direction(+X,±Y,0)','utility':'Selected Y equals currently available material route; first decision vs post-consequence decisions separate',
 'bounds':'6opportunities per world, phase/cadence native52ticks, no favorable waiting or repairs. End plus1external step measured, not competent control claim.'}
atomic_json(E/'SELECTOR_PROTOCOLO_010.json',protocol)
for number,feedback,history in protocol['histories']:
    name='MI01_SELECTOR_'+str(number);fork('E1_MI01_MAIN',name)
    def fn(a,feedback=feedback,history=history,number=number):
        start=physical(a.world,occupation=True)
        train=native.train(a,episode='MI01_TRAIN_'+str(number),contexts=history,feedback=feedback)
        checkpoint=E/(name+'.DESPUES_EXPERIENCIA.deetsnap.gz');a.save(checkpoint)
        rows=native.situated(a,name='MI01_BODY_'+str(number),availability=protocol['common_native_world_availability'],mode='intact',compact=True,gap=0,stream=True,shunt='a_only')
        end_body=physical(a.world,occupation=True)
        use=integrated.act_external(a,steps=1)
        return{'initial':start,'training':train,'native_world_rows':rows,'end_native_world':end_body,'external':use,'final':physical(a.world,occupation=True),
          'prepared_learning_law_not_invented':'AA01 consequence direction and physical route law reused; new selector content/history acquired here',
          'no_auditor_answer_sent':True}
    result=run(name,'MI01_SELECTOR_'+str(number),fn,{'feedback':feedback,'history':history,'protocol':'SELECTOR_PROTOCOLO_010.json'})['result']
    print(json.dumps({'case':number,'actions':[{'tick':z['query_tick'],'available':z['availability'],'native':z['action'],'qualified':ic_body.qualified(z['action']),'useful':ic_body.qualified(z['action'])and z['action']['direction'][1]==z['availability']}for z in result['native_world_rows']],'end':result['final']['tick']},ensure_ascii=False),flush=True)
# Official CPC7/U0 factory is inspected as an untrained recipe, not a world.
options=d.IntegratedOptions();prepared=d.prepare_integrated_u0(options);g=prepared.geometry()
atomic_json(E/'CPC7_U0_PREGUNTA_MECANISMO_RECUPERADO.json',{'source':'Official4.5 NativePreparation geometry descriptor, no world created','native_ticks':0,'preparation_not_a_life':True,
 'need':g.get('need'),'actions':g.get('actions'),'action_inputs':g.get('action_inputs'),'body':g.get('body'),'ticks':g.get('ticks'),
 'scope':'Conditional physical query mechanism recovered as architecture only. No U0 learned memory or CPC7 biography copied into E1.'})
