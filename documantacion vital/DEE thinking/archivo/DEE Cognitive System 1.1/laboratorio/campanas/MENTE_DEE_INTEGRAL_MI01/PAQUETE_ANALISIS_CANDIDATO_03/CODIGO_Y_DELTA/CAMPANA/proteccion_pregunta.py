"""Late finite query: separate route interception and association ghosts.
All resource paths are predefined; no correct reply or online repair selected.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import mente_integral_mi01 as mi,integracion_situada_01 as integrated
from capacidades.mente_integral_mi01 import consulta_nativa as query
configs=[(170,[-1,1],'paired','full',20),(171,[-1,1],'paired','full',52),(172,[-1,1],'paired','corridor',20),(173,[-1,1],'paired','sham_ghosts',20),(174,[1,-1],'paired','full',20),(175,[-1,1],'omit','full',20)]
atomic_json(E/'PROTECCION_PREGUNTA_PROTOCOLO_170.json',{'parent':'E1_MI01_MAIN23453','cases':configs,'before_evaluation':'All variants fixed before results. Geometry center40,35,55; original query route.','hypothesis':'Old zero association products recur afterN and join new Y/Z resources, changing the actual content carrier toXYZ rather thanXZ. Native SEM4 on the resource-only YZ path does not lie on the intended material XZ path. Fixed downstream reader guards separately absorb unused Z- probes.','attribution':'Prepared P0 fixtures, not autonomous cleanup or learned inhibition; old raw/clock never edited. Old3code functions measured at subsequent motor slots.'})
for number,history,feedback,protect,value in configs:
    life='MI01_PROTECCION_'+str(number);fork('E1_MI01_MAIN',life)
    def fn(a,number=number,history=history,feedback=feedback,protect=protect,value=value):
        initial=physical(a.world,occupation=True);teaching=mi.train(a,episode='MI01_EXT_130',contexts=history,feedback=feedback,center=[40,35,55]);p=query.prepare(a,name=life,private_value=value,reader_guard=True,late_protection=protect)
        tr=query.advance(a,until=p['end_tick']);a.save(E/(life+'.RECIBIDO.deetsnap.gz'));use=integrated.act_external(a,steps=3)
        return{'initial':initial,'experience':teaching,'plan':p,'trajectory':tr,'external':use,'final':physical(a.world,occupation=True)}
    v=run(life,life,fn)['result'];print(json.dumps({'case':number,'formed':[z for z in v['trajectory']['events']if z['kind']=='association'],'received':[z for z in v['trajectory']['events']if z['kind']=='received'],'new_wire':[[[r['bank'],r['native']['s_reg'],r['qualified']]for r in z['social_reads']if r['target']in([32,56,26],[10,56,26])]for z in v['external']['rows']],'occupation':v['final']['occupied']},ensure_ascii=False),flush=True)
