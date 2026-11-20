"""R5: fixed downstream B-reader interception, native vs equal-dose sham."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import mente_integral_mi01 as mi
from capacidades.mente_integral_mi01 import preparacion_compartida as compiler,fallo_y_consulta as candidate
configs=[(300,'intact','native'),(301,'intact','sham'),(302,'cut_failure','native'),(303,'sham_failure','native'),(304,'cut_reply','native'),(305,'omit_failure_return','native')]
atomic_json(E/'COLA_B_PROTOCOLO_R5_300.json',{'parent':'MI01_BASE_HISTORICA_T23453','cases':configs,'availability':[1,-1],'private_B_raw':[20,52],'hypothesis':'After B uses the initial request, its continued Z+ carrier may return and/or alter later B access. A fixed semantic4 fixture four steps beyond B vsX+19sham tests that influence, without deleting the response or re-teaching its content. Initial source and later source are separate outcomes.','known_R4':'Native failure->question was causal270vs271/272/273, but B did not answer that second phase45question. Full closure NOT inherited as a fact.','criterion':'Same initial query/use must remain; failed action then initiates a question and a new private B answer must influence the later S. If only emission improves, classify partial.'})
for number,mode,guard in configs:
    life='MI01_COLA_B_'+str(number);fork('MI01_BASE_HISTORICA_T23453',life)
    def fn(a,number=number,mode=mode,guard=guard):
        t=mi.train(a,episode='MI01_EXT_130',contexts=[-1,1],feedback='paired',center=[40,35,55]);p=compiler.prepare(a,builder='direct_failure',b_tail_guard=guard,name=life,availability=[1,-1],private_values=[20,52],mode=mode);a.save(E/(life+'.PREPARADO.deetsnap.gz'));v=candidate.advance(a,name=life);a.save(E/(life+'.FINAL.deetsnap.gz'))
        return{'experience':t,'plan':p,'trajectory':v,'final':physical(a.world,occupation=True)}
    v=run(life,life,fn)['result'];print(json.dumps({'case':number,'commands':[[z['index'],z['native']['direction'],z['native']['s_reg']]for z in v['trajectory']['frames']if z['kind']=='command'],'failure':v['trajectory']['failure_frames'],'occupied':v['final']['occupied']},ensure_ascii=False),flush=True)
