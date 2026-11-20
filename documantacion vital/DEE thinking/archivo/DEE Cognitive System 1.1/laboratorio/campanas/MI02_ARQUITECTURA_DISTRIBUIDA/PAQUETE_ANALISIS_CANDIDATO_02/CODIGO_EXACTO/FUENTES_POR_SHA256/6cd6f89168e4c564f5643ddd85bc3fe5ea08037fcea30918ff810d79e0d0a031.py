"""Continue the already recorded diagnostic replay, no native or env reset."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from capacidades import arquitectura_distribuida_mi02_r8 as b
old=json.loads((E/'EXTERNO25_82251_closed_all.json').read_bytes())
def trace(a):
    requests=[];frames=[];g=b.get(a);ports=g['external_sensors'][:2]
    for sample in old['data']['result']['rows'][12:]:
        begin=sample['tick_sensor']-1
        assert a.tick==begin,'Do not hide a diagnostic rewind'
        for c in sample['codec']:requests.append(b.send(a,'MI02.external.sensor.'+c['variable'],c['origin'],c['direction'],sample['tick_sensor'],c['payload']))
        for t in range(begin+1,begin+12):
            a.run_until(t);frames.append({'index':sample['index'],'tick':t,'offset':t-begin,'Q':b.obs(a,g['Q']),'sensor_targets':[b.obs(a,p['target'])for p in ports]})
        a.run_until(sample['tick_end'])
    return{'recorded_input_replay_only':True,'not_external_closed_loop':True,'frames':frames,'requests':b.receipts(a,requests),'physical':physical(a.world,occupation=True)}
z=run('MI02_DIAGNOSTICO_SENSOR27','TRANSITO_SENSORIAL27_CONTINUAR',trace)
print(json.dumps([(v['index'],v['offset'],v['Q']['direction'])for v in z['frames']if v['offset']in(7,8)],ensure_ascii=False),flush=True)
