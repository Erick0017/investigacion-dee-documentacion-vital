"""Replay recorded observations for timing diagnosis only, not a closed-loop run."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from capacidades import arquitectura_distribuida_mi02_r8 as b
old=json.loads((E/'EXTERNO25_82251_closed_all.json').read_bytes());base=old['before']['snapshot'];life='MI02_DIAGNOSTICO_SENSOR27';fork(old['before']['life_id'],life,base)
def trace(a):
    samples=old['data']['result']['rows'][:12];requests=[];frames=[];g=b.get(a);ports=g['external_sensors'][:2]
    for sample in samples:
        begin=sample['tick_sensor']-1
        for c in sample['codec']:requests.append(b.send(a,'MI02.external.sensor.'+c['variable'],c['origin'],c['direction'],sample['tick_sensor'],c['payload']))
        for t in range(begin+1,begin+12):
            a.run_until(t);frames.append({'index':sample['index'],'tick':t,'offset':t-begin,'Q':b.obs(a,g['Q']),'sensor_paths':{p['name']:[b.obs(a,b.xyz(a,p['origin'],p['direction'],k))for k in range(6)]for p in ports}})
        a.run_until(sample['tick_end'])
    return{'replayed_recorded_inputs_only':True,'not_an_external_interaction_or_new_policy':True,'source_sha256':sha(E/'EXTERNO25_82251_closed_all.json'),'frames':frames,'requests':b.receipts(a,requests),'physical':physical(a.world,occupation=True)}
z=run(life,'TRANSITO_SENSORIAL27',trace)
print(json.dumps({'frames':[(v['index'],v['offset'],v['Q']['direction'],[(name,path[-1]['state'],path[-1]['s_reg'])for name,path in v['sensor_paths'].items()])for v in z['frames']if v['offset']in(6,7,8)]},ensure_ascii=False),flush=True)
