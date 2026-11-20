"""Frozen two-sensor, signed-actuator check on an already learned R6 life."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from capacidades import arquitectura_distribuida_mi02_externo_r4 as ext
atomic_json(E/'PROTOCOLO_EXTERNO_28.json',{'parent':'MI02_UNIFICADA_180','native_parent_tick':Store().record('MI02_UNIFICADA_180')['physical']['tick'],'seeds':[82281,82282],'steps':32,'ratio':19,'sensor_codec':'Two fixed sin/cos quantizations0..20; action read fixed at+7 after five-step transport and one native Q update. +8 read was after transient sensory content had left. This is a fixed instrumental correction, not per-answer window selection.','controls':['nulled actuator','sensors omitted','one-step delay'],'motor':'Qualified native x>=0 to+2, x<0 to-2; invalid to external0','not_claimed':'External control learning or balancing competence.'})
for seed in(82281,82282):
    for mode,sensor in[('closed','all'),('nulled','all'),('closed','omit'),('delay1','all')]:
        life='MI02_EXTERNO28_'+str(seed)+'_'+mode+'_'+sensor;fork('MI02_UNIFICADA_180',life)
        z=run(life,'EXTERNO28_'+str(seed)+'_'+mode+'_'+sensor,lambda a,seed=seed,mode=mode,sensor=sensor:ext.run(a,steps=32,seed=seed,reset_environment=True,mode=mode,sensor_mode=sensor))
        print(json.dumps({'life':life,'positive':sum(r['executed_torque']>0 for r in z['rows']),'negative':sum(r['executed_torque']<0 for r in z['rows']),'neutral':sum(r['executed_torque']==0 for r in z['rows']),'reward_sum':sum(r['response']['reward']for r in z['rows']),'requests':len([v for r in z['rows']for v in r['requests']])}),flush=True)
