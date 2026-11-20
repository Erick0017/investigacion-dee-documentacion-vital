"""Declared physical extension after measured same-support accumulation failure.
New supports receive legal experiences in the SAME inherited world; no learned
fields are copied and no old support is cleared. Not autonomous anatomy.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import mente_integral_mi01 as mi,integracion_situada_01 as integrated
from capacidades.mente_integral_mi01 import consulta_nativa as query
from capacidades.integracion_situada_01 import ic_native_core as n
center=[40,35,55]
configs=[(130,[-1,1],'paired','intact',20),(131,[-1,1],'paired','intact',52),(132,[1,-1],'paired','intact',20),(133,[-1,1],'omit','intact',20),(134,[-1,1],'paired','cut',20),(135,[-1,1],'paired','sham',20)]
atomic_json(E/'EXTENSION_PROTOCOLO_130.json',{'parent':'E1_MI01_MAIN23453','prepared_new_center':center,'cases':configs,'reason':'MAIN122 command became direction0 after repeated AA use onS50. Existing world/history preserved; this new preparation is externally designed anatomy, not repair by deleting old content. Same branch acquisitions remain actual experiences, no successful world transplant.','predeclared_readout':'Same XY state1sem1; material B request and same fixed two E1 reply banks. External actuator reads all fixed declared ports, not the desired private sign.'})
for number,history,feedback,mode,value in configs:
    life='MI01_EXTENSION_'+str(number);fork('E1_MI01_MAIN',life)
    def fn(a,number=number,history=history,feedback=feedback,mode=mode,value=value):
        initial=physical(a.world,occupation=True);pre=n.obs(a,center)
        experience=mi.train(a,episode='MI01_EXT_'+str(number),contexts=history,feedback=feedback,center=center)
        p=query.prepare(a,name='MI01_EXT_'+str(number),private_value=value,mode=mode)
        frames=query.advance(a,until=p['end_tick']);snapshot=E/(life+'.RECIBIDO.deetsnap.gz');a.save(snapshot)
        use=integrated.act_external(a,steps=2)
        return{'initial':initial,'new_component_pre':pre,'preparation_change_external':True,'experience':experience,'plan':p,'trajectory':frames,'external':use,'final':physical(a.world,occupation=True)}
    v=run(life,life,fn,{'history':history,'feedback':feedback,'mode':mode,'center':center})['result']
    print(json.dumps({'case':number,'last_experience':v['experience']['captures'][-1]['selector'],'events':[z for z in v['trajectory']['events']if z['kind']in('command','received')],'external':[{'tick':z['tick'],'torque':z['native_command'],'new_reply':[r for r in z['social_reads']if r['target']in([32,56,26],[10,56,26])]}for z in v['external']['rows']]},ensure_ascii=False),flush=True)
