"""A query's own native reply, not host assistance, selects later command."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import mente_integral_mi01 as mi
from capacidades.mente_integral_mi01 import consulta_nativa as query,retorno_selector as reply
from capacidades.integracion_situada_01 import ic_native_core as n
configs=[(180,20,'intact'),(181,52,'intact'),(182,20,'cut'),(183,20,'sham'),(184,20,'omit')]
atomic_json(E/'RETORNO_DECISION_PROTOCOLO_180.json',{'parent':'E1_MI01_MAIN23453','cases':configs,'geometry':'Extension40,35,55 with full finite P0 protection. All possible sign paths and common X0 fixed before private B answer.','criterion':'After the actual native query, private20 vs52 must cause opposite XY commands at SAME support with no host-provided sign. Postformed reply cut vs sham and omitted return discriminate route use.','not_claimed':'The sign mapping, turns and common command clock are prepared. No missing-memory detector, general policy learning or cloning the content to simultaneous destinations.'})
for number,value,mode in configs:
    life='MI01_RETORNO_'+str(number);fork('E1_MI01_MAIN',life)
    def fn(a,number=number,value=value,mode=mode):
        start=physical(a.world,occupation=True);teaching=mi.train(a,episode='MI01_EXT_130',contexts=[-1,1],feedback='paired',center=[40,35,55])
        p=query.prepare(a,name='MI01_Q_'+str(number),private_value=value,reader_guard=True,late_protection='full')
        r=reply.prepare(a,query_name=p['name'],name=life,mode=mode);a.save(E/(life+'.ANTES_RESPUESTA.deetsnap.gz'))
        result=reply.advance(a,name=life);a.save(E/(life+'.DECISION.deetsnap.gz'))
        return{'initial':start,'experience':teaching,'query':p,'return':r,'use':result,'final':physical(a.world,occupation=True)}
    v=run(life,life,fn)['result'];print(json.dumps({'case':number,'output':v['use']['output'],'arrival':v['return']['arrival_tick'],'occupation':v['final']['occupied']},ensure_ascii=False),flush=True)
