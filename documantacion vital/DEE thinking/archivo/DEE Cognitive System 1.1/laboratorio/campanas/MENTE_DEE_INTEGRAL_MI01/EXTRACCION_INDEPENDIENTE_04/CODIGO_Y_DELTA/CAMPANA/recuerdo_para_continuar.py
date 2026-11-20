"""Use current acquired recipient content, no re-teaching, into S40."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.mente_integral_mi01 import reusar_contenido as recall
configs=[(280,'MI01_PROTECCION_170','intact'),(281,'MI01_PROTECCION_171','intact'),(282,'MI01_PROTECCION_170','cut'),(283,'MI01_PROTECCION_170','sham')]
def execute():
    atomic_json(E/'REUSO_CONTENIDO_PROTOCOLO_280.json',{'cases':configs,'source':'Actual late received+/-145 lives170/171 after3uses, no new B input, teacher or selector retraining','fixed_resource':'GenericZ0 at BOTH possible E1 reply banks, fixed two-route native return to S40. Original matter may be diverted, not cloned.','criterion':'Opposite source histories yield opposite pureY selector or XY command if a common cue is explicit; formed-cut and equal-dose sham test causal recall.'})
    for number,parent,mode in configs:
        life='MI01_REUSO_'+str(number);fork(parent,life)
        def fn(a,number=number,mode=mode):
            initial=physical(a.world,occupation=True);p=recall.prepare(a,name=life,mode=mode,common=False);v=recall.advance(a,name=life);a.save(E/(life+'.RESULTADO.deetsnap.gz'));return{'initial':initial,'plan':p,'use':v,'final':physical(a.world,occupation=True)}
        v=run(life,life,fn)['result'];print(json.dumps({'case':number,'output':v['use']['output'],'occupied':v['final']['occupied']},ensure_ascii=False),flush=True)
if __name__=='__main__':execute()
