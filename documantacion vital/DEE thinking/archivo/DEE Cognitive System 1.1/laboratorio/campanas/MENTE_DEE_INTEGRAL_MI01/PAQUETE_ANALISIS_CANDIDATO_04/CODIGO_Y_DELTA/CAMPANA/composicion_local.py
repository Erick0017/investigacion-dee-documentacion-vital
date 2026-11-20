"""Reuse AA01 native access/content composition in the actual late E1 world."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import acceso_adaptativo_01 as aa,espanol_funcional_01 as ef,integracion_situada_01 as integrated
configs=[(30,(1,-1),(-1,1),'paired'),(31,(-1,1),(-1,1),'paired'),(32,(1,-1),(1,-1),'paired'),(33,(1,-1),(-1,1),'omit_all'),(34,(1,-1),None,'paired')]
atomic_json(E/'COMPOSICION_PROTOCOLO_030.json',{'cases':configs,'parent':'E1_MI01_MAIN21778','new_preparation_only':'Fixed known AA01 supports/interfaces; no old trained-state transplant',
 'question':'Can learned route selection and separately acquired content meet natively and affect a receiver in the late continuous organization?',
 'validity':'Recompute positive-load material signatures from RAW, not AA automatic text; zero-material directional selector variant is tested separately and never promoted silently here.',
 'contents':'Actual opaque oriented experiences, not Spanish words or answers supplied during query. Same final generic query in all histories.'})
for number,history,contents,feedback in configs:
    life='MI01_COMPOSICION_'+str(number);fork('E1_MI01_MAIN',life)
    def fn(a,number=number,history=history,contents=contents,feedback=feedback):
        initial=physical(a.world,occupation=True);ef.prepare(a)
        delay=ef.tick_at_or_after(a.tick,phase=6,lead=4)-a.tick
        plan=aa.prepare_local_episode(a,episode='MI01_'+str(number),availability=history,contents=contents,feedback=feedback,delay=delay,recipient_mode='immediate_yz')
        stages=[]
        for stage in('first','learned','content','access','received','use'):stages.append(aa.advance_local_episode(a,stage=stage))
        a.save(E/(life+'.DESPUES_USO.deetsnap.gz'));external=integrated.act_external(a,steps=1)
        return{'initial':initial,'plan':plan,'stages':stages,'external':external,'final':physical(a.world,occupation=True),
          'new_Spanish_or_NSM_meaning_claimed':False,'scope':'Acquired selection plus native opaque content composition/use. Callback only presents fixed-stage experiments during construction, not native initiative.'}
    out=run(life,'MI01_COMPOSICION_'+str(number),fn,{'history':history,'contents':contents,'feedback':feedback})['result']
    print(json.dumps({'case':number,'stages':[{'stage':v['INSTRUMENTO']['stage'],'tick':v['INSTRUMENTO']['tick'],'native':v['ENTE'],'codes_legacy':[v.get('CONTENT_CODES')]}for v in out['stages']if v['INSTRUMENTO']['stage']in('learned','access','use')], 'end':out['final']['tick']},ensure_ascii=False),flush=True)
