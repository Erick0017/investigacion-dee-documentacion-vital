"""Native selected reply vs resource-only precursor: selective P0/sham."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import mente_integral_mi01 as mi
from capacidades.mente_integral_mi01 import consulta_nativa as query,retorno_selector as reply
configs=[(210,20,'intact','local'),(211,52,'intact','local'),(212,20,'intact','sham'),(213,52,'intact','sham'),(214,52,'cut','local'),(215,52,'sham','local')]
atomic_json(E/'PROTECCION_RETORNO_PROTOCOLO_210.json',{'parent':'MI01_BASE_HISTORICA_T23453','cases':configs,'causal_prior':'187 exact snapshot reconstruction: XY0 precursor36,39,43 plusX14536,40,43 enter empty37,40,43; reducer givesXY145 and diverts it. No new input at that instant186; this is prior physical context.','intervention':'Same generic SEM4 on predecessor35,38,43 atarrival-66 for BOTH private contents; equal-doseZ+19sham. No raw edits or response-dependent choice.','criterion':'Both private contents cause their appropriate opposite native XY actions at S; formed-reply cut removes the action and sham preserves it. Old phase29 results remain separate.'})
for number,value,mode,guard in configs:
    life='MI01_RETORNO_PROTEGIDO_'+str(number);fork('MI01_BASE_HISTORICA_T23453',life)
    def fn(a,number=number,value=value,mode=mode,guard=guard):
        training=mi.train(a,episode='MI01_EXT_130',contexts=[-1,1],feedback='paired',center=[40,35,55]);p=query.prepare(a,name='MI01_Q_'+str(number),private_value=value,reader_guard=True,late_protection='full')
        r=reply.prepare(a,query_name=p['name'],name=life,mode=mode,ghost_guard=guard);result=reply.advance(a,name=life);a.save(E/(life+'.DECISION.deetsnap.gz'))
        return{'experience':training,'query':p,'return':r,'use':result,'final':physical(a.world,occupation=True)}
    v=run(life,life,fn)['result'];print(json.dumps({'case':number,'output':v['use']['output'],'guard':v['return']['guard_record'],'occupation':v['final']['occupied']},ensure_ascii=False),flush=True)
