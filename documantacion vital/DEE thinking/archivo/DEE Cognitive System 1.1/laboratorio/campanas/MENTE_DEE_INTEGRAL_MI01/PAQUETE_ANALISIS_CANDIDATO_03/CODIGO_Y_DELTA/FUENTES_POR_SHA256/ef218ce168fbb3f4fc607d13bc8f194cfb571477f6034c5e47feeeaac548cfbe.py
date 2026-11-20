"""R4 corrects identical simultaneous fixture collisions, not task answers."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import mente_integral_mi01 as mi
from capacidades.mente_integral_mi01 import preparacion_compartida as compiler,fallo_y_consulta as candidate
configs=[(270,'intact'),(271,'omit_failure_return'),(272,'cut_failure'),(273,'sham_failure'),(274,'cut_reply')]
def execute():
    atomic_json(E/'FALLO_COMPARTIDO_PROTOCOLO_R4_270.json',{'parent':'MI01_BASE_HISTORICA_T23453','cases':configs,'availability':[1,-1],'private_B_raw':[20,52],'reason_for_revision':'245 original receipts: every duplicated static guard has native status6, not applied. R3 was an invalid multi-cycle preparation, not evidence of a universal integration limit.','new_preparation':'Only byte-identical future packets are requested once; logical aliases and dose change recorded. Conflicting nonidentical requests still face ordinary frozen v27 admission. No cleanup or runtime action filtering.','criterion':'Native query/B20, later native act, actual failed contact, native phase45query, B52 and a later decision. Omitted consequence and formed-product cut/sham compare with identical compilation.','horizon':'Two335tick opportunities. All inputs frozen before responses; no host checks failure to decide a request.'})
    for number,mode in configs:
        life='MI01_COMPARTIDO_'+str(number);fork('MI01_BASE_HISTORICA_T23453',life)
        def fn(a,number=number,mode=mode):
            t=mi.train(a,episode='MI01_EXT_130',contexts=[-1,1],feedback='paired',center=[40,35,55]);p=compiler.prepare(a,builder='direct_failure',name=life,availability=[1,-1],private_values=[20,52],mode=mode);a.save(E/(life+'.PREPARADO.deetsnap.gz'));v=candidate.advance(a,name=life);a.save(E/(life+'.FINAL.deetsnap.gz'))
            return{'experience':t,'plan':p,'trajectory':v,'final':physical(a.world,occupation=True)}
        v=run(life,life,fn)['result'];print(json.dumps({'case':number,'compiler':[v['plan']['input_compilation']['logical_requests'],v['plan']['input_compilation']['unique_physical_requests']],'commands':[[z['index'],z['native']['direction'],z['native']['s_reg']]for z in v['trajectory']['frames']if z['kind']=='command'],'failure':v['trajectory']['failure_frames'],'occupied':v['final']['occupied']},ensure_ascii=False),flush=True)
if __name__=='__main__':execute()
