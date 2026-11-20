"""Same R9 life continues; passively resolve repeated reader release/activation."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from capacidades import integracion_distribuida_mi02_r9 as b
from capacidades import arquitectura_distribuida_mi02_r8 as n
from capacidades.observador_causal_retrospectivo_01 import Snapshot,compare
life='MI02_SOCIAL_REUSABLE_240';parent=Store().record(life)
atomic_json(E/'REUTILIZACION45_FIJADA.json',{'parent':parent,'future_availability':[1]*4+[-1]*4+[1]*4,'aim':'Repeated native A queries, private-dependent B response, release and use without host activation or clearing. B private reference remains61/19; this does NOT demonstrate arbitrary new-message updating.','measurement':'Passive B/A/query/recipient fields at each actual owner tick, no dense whole-world serialization','technical_control':'Exact-prefix copy executes same protocol without the additional passive sampling; compare RAW/clocks/pending/channels/receipts after matching horizon. Not another independent acquisition.','sources':archive()})
fork(life,'MI02_SOCIAL45_SIN_REGISTRO')

def observe_cycle(a):
    g=b.saved(a)['geometry'];original=a.run_until;frames=[]
    def instrumented(t):
        while a.tick<t:
            original(a.tick+1);frames.append({'tick':a.tick,'A':n.obs(a,g['A']),'B':n.obs(a,g['B']),'query_last':n.obs(a,g['query'][-1]['head']),'contexts':[n.obs(a,r['context'])for r in g['social']['routes']]})
    a.run_until=instrumented
    try:r=b.live(a,availability=[1]*4+[-1]*4+[1]*4)
    finally:a.run_until=original
    r['passive_every_tick']=frames;r['no_host_query_activation_or_cleanup']=True;return r

run(life,'SOCIAL45_REUSE',observe_cycle)
run('MI02_SOCIAL45_SIN_REGISTRO','SOCIAL45_WITHOUT_EXTRA_OBSERVER',lambda a:b.live(a,availability=[1]*4+[-1]*4+[1]*4))
a=Store().record(life);z=Store().record('MI02_SOCIAL45_SIN_REGISTRO')
atomic_json(E/'SOCIAL45_OBSERVADOR_Y_CORTES.json',{'sampled':a,'technical_copy':z,'comparison':compare(Snapshot(S/a['snapshot']),Snapshot(S/z['snapshot']),sample_limit=8),'knowledge_never_imported_intoMAIN':True})
