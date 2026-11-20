"""Bounded two-opportunity native failure-initiated-query experiment."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import mente_integral_mi01 as mi
from capacidades.mente_integral_mi01 import fallo_y_consulta as candidate
configs=[(260,'intact'),(261,'omit_failure_return'),(262,'cut_failure'),(263,'sham_failure'),(264,'cut_reply')]
def execute():
    atomic_json(E/'FALLO_CONSULTA_PROTOCOLO_260.json',{'parent':'MI01_BASE_HISTORICA_T23453','cases':configs,'availability':[1,-1],'private_B_raw':[20,52],'horizon':'Two335tick opportunities; actual action atsecond can make a native failure product, with a generic second-phase query opportunity16ticks later. No Python test of failure/answer dispatches the query.','law_prepared':'Fixed contact law, two-carrier failure-to-query transduction, generic clock and all possible B-content paths. Only actual content and activity are acquired.','criterion':'Initial native query ->B20->act ->native failed contact->new material question ->B52->changed later S command. Omission and postformed interventions separate products from scheduler.'})
    for number,mode in configs:
        life='MI01_FALLO_CONSULTA_'+str(number);fork('MI01_BASE_HISTORICA_T23453',life)
        def fn(a,number=number,mode=mode):
            t=mi.train(a,episode='MI01_EXT_130',contexts=[-1,1],feedback='paired',center=[40,35,55]);p=candidate.prepare(a,name=life,availability=[1,-1],private_values=[20,52],mode=mode);a.save(E/(life+'.PREPARADO.deetsnap.gz'));v=candidate.advance(a,name=life);a.save(E/(life+'.FINAL.deetsnap.gz'))
            return{'experience':t,'plan':p,'trajectory':v,'final':physical(a.world,occupation=True)}
        v=run(life,life,fn)['result'];print(json.dumps({'case':number,'commands':[[z['index'],z['native']['direction'],z['native']['s_reg']]for z in v['trajectory']['frames']if z['kind']=='command'],'failure':v['trajectory']['failure_frames'],'occupied':v['final']['occupied']},ensure_ascii=False),flush=True)
if __name__=='__main__':execute()
