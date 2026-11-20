"""Frozen two-sensor, signed-actuator check on an already learned R6 life."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from capacidades import arquitectura_distribuida_mi02_externo as ext
atomic_json(E/'PROTOCOLO_EXTERNO_25.json',{'parent':'MI02_UNIFICADA_180','native_parent_tick':Store().record('MI02_UNIFICADA_180')['physical']['tick'],'seeds':[82251,82252],'steps':32,'ratio':19,'sensor_codec':'Two fixed sin/cos quantizations0..20, distinct transient context ports. Angular velocity discarded, not used to choose an action.','controls':['nulled actuator','sensors omitted','one-step delay'],'motor':'Qualified native x>=0 to+2, x<0 to-2; absent/invalid to external0. x0 has the profile declared default-left role, not waiting.','not_claimed':'External control learning, balancing competence, or independent learning samples per step.'})
for seed in(82251,82252):
    for mode,sensor in[('closed','all'),('nulled','all'),('closed','omit'),('delay1','all')]:
        life='MI02_EXTERNO25_'+str(seed)+'_'+mode+'_'+sensor;fork('MI02_UNIFICADA_180',life)
        z=run(life,'EXTERNO25_'+str(seed)+'_'+mode+'_'+sensor,lambda a,seed=seed,mode=mode,sensor=sensor:ext.run(a,steps=32,seed=seed,reset_environment=True,mode=mode,sensor_mode=sensor))
        print(json.dumps({'life':life,'positive':sum(r['executed_torque']>0 for r in z['rows']),'negative':sum(r['executed_torque']<0 for r in z['rows']),'neutral':sum(r['executed_torque']==0 for r in z['rows']),'reward_sum':sum(r['response']['reward']for r in z['rows']),'requests':len([v for r in z['rows']for v in r['requests']])}),flush=True)
