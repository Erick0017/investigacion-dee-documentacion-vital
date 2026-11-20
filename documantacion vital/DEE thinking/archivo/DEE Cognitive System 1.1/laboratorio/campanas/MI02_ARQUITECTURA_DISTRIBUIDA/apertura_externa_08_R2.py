"""Early inherited-E1 interface contrast, not a substitute for MAIN evaluation."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from capacidades import arquitectura_distribuida_mi02_externo as ext
atomic_json(E/'EXTERNO_PROTOCOLO_08_R2.json',{'parent':'E1_MI02_HEREDADA_A','seeds':[82001,82002],'steps_each':24,'ticks_per_step':19,'sensors':['sin(theta)','cos(theta)','angular_velocity'],'motor':'qualified native x>=0 to+2, x<0 to-2, otherwise bridge0','controls':['actual actions','nulled actions','omitted sensors'],'instrumental_correction':'First external attempt failed serializing float-valued environment into exact metadata after one actual step. Its native T27001 future preserved. R2 uses official JSON-string pattern for the external state; new identified comparison lives, no silent rewind.','not_claimed':'No learned Pendulum control from merely emitting both signed torques. Current external window exposes perception/actuator limits and possible interference.'})
for seed in(82001,82002):
    for mode,sensor in[('closed','all'),('nulled','all'),('closed','omit')]:
        name='MI02_EXTERNO08R2_'+str(seed)+'_'+mode+'_'+sensor;fork('E1_MI02_HEREDADA_A',name)
        r=run(name,'EXTERNO08R2_'+str(seed)+'_'+mode+'_'+sensor,lambda a:ext.run(a,steps=24,seed=seed,reset_environment=True,mode=mode,sensor_mode=sensor,ticks_per_step=19))
        print(json.dumps({'life':name,'nonzero':sum(x['executed_torque']!=0 for x in r['rows']),'positive':sum(x['executed_torque']>0 for x in r['rows']),'negative':sum(x['executed_torque']<0 for x in r['rows']),'reward_sum':sum(x['response']['reward']for x in r['rows'])}),flush=True)
