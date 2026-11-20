"""Bounded physical renewal/causality tests, fixed before outputs."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as integrated
from capacidades.integracion_situada_01 import ic_native_core as n,ic_body as b
contexts=[1]*6+[-1]*6+[1]*6
configs=[(20,0,'a_only','intact'),(21,0,'all','intact'),(22,1,'a_only','intact'),(23,5,'all','intact'),(24,0,'a_only','omit_return'),(25,0,'a_only','no_action')]
atomic_json(E/'RENOVACION_PROTOCOLO_020.json',{'source_complete':str(E/'MI01_SELECTOR_10.DESPUES_EXPERIENCIA.deetsnap.gz'),
  'configs':configs,'contexts_material_availability':contexts,'no_future_choice_read_by_host':True,
  'criterion':'Each physically valid choice versus route availability. Sustained function means later native payload-bearing actions and useful consequence-conditioned switch, not zero-load ghosts. No post-result repair.'})
for number,gap,shunt,mode in configs:
    life='MI01_RENOVACION_'+str(number);fork('MI01_SELECTOR_10',life,checkpoint=str(E/'MI01_SELECTOR_10.DESPUES_EXPERIENCIA.deetsnap.gz'))
    def fn(a,gap=gap,shunt=shunt,mode=mode,number=number):
        start=physical(a.world,occupation=True)
        rows=n.situated(a,name='MI01_RENEW_'+str(number),availability=contexts,mode=mode,compact=True,gap=gap,stream=True,shunt=shunt)
        native_end=physical(a.world,occupation=True);out=integrated.act_external(a,steps=1)
        return{'initial':start,'rows':rows,'native_end':native_end,'external':out,'final':physical(a.world,occupation=True),'no_answer_selected_from_host':True}
    v=run(life,'MI01_RENOVACION_'+str(number),fn,{'gap':gap,'shunt':shunt,'mode':mode})['result']
    rr=v['rows'];print(json.dumps({'case':number,'gap':gap,'mode':mode,'valid':sum(b.qualified(x['action'])for x in rr),
       'useful':sum(b.qualified(x['action'])and x['action']['direction'][1]==x['availability']for x in rr),
       'choices':[[x['query_tick'],x['action']['s_reg'],x['action']['direction'],x['availability']]for x in rr],
       'end':v['final']['tick'],'social_codes':[z['qualified']for z in v['external']['rows'][0]['social_reads']]},ensure_ascii=False),flush=True)
