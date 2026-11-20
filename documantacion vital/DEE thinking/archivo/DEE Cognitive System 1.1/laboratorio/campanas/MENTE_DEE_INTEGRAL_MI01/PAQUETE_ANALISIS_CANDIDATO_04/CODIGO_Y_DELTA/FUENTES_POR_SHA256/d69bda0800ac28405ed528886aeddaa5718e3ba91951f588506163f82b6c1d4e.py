"""Compare fixed corridor alternative and selective interception/sham.
The exact first-failure predecessor139 determines the intervention hypothesis;
these are new reserved engineering contrasts, not edited old results.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import mente_integral_mi01 as mi,integracion_situada_01 as integrated
from capacidades.mente_integral_mi01 import consulta_nativa as query
from capacidades.integracion_situada_01 import ic_native_core as n
configs=[(160,'original',True,20,'none'),(161,'lift6',True,20,'none'),(162,'lift6',True,52,'none'),(163,'original',True,20,'selective'),(164,'original',True,20,'sham'),(165,'lift6',False,20,'none')]
atomic_json(E/'DESVIO_PROTOCOLO_160.json',{'parent':'E1_MI01_MAIN23453','cases':configs,'identified_event':'139 first lost signatureT23791 at66,59,55, adjacent Z+7; local origin is tested, not a unique particle identity','lift6':'Same total travel/end phase, six final Z+ steps commute before long X+ corridor; fixed before answers, not learned avoidance.','intercept':'SEM4 at66,59,53 atT23787; matchedY+19 sham. Native legal input, not RAW clearing. Both existing message codes remain measured by fixed external wires.','reader_guard':'Prepared downstream SEM4 absorbs only unused Z- readout trajectories; no host filter. Input rejection remains a result.'})
for number,route,guard,value,intercept in configs:
    life='MI01_DESVIO_'+str(number);fork('E1_MI01_MAIN',life)
    def fn(a,number=number,route=route,guard=guard,value=value,intercept=intercept):
        initial=physical(a.world,occupation=True);training=mi.train(a,episode='MI01_EXT_130',contexts=[-1,1],feedback='paired',center=[40,35,55])
        p=query.prepare(a,name='MI01_DESVIO_'+str(number),private_value=value,route_revision=route,reader_guard=guard);extra=[]
        if intercept!='none':
            site=[66,59 if intercept=='selective'else 11,53];extra.append(n.submit(a,'MI01.corridor.intercept.'+str(number),site,(0,0,0),23787,0,4))
        frames=query.advance(a,until=p['end_tick']);snap=E/(life+'.RECIBIDO.deetsnap.gz');a.save(snap);use=integrated.act_external(a,steps=2)
        return{'initial':initial,'experience':training,'plan':p,'trajectory':frames,'interception_requests':n.receipts(a,extra),'external':use,'final':physical(a.world,occupation=True)}
    v=run(life,life,fn,{'route':route,'guard':guard,'intercept':intercept})['result'];print(json.dumps({'case':number,'events':[z for z in v['trajectory']['events']if z['kind']in('arrival','received')],'external_newcodes':[[{'bank':r['bank'],'load':r['native']['s_reg'],'valid':r['qualified']}for r in z['social_reads']if r['target']in([32,56,26],[10,56,26])]for z in v['external']['rows']],'occupation':v['final']['occupied']},ensure_ascii=False),flush=True)
