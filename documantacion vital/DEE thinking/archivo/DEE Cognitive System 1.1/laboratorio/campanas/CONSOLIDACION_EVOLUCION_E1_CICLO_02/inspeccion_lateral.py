from pathlib import Path
import json
L=Path(__file__).resolve().parent;E=L.parents[2]/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
for p in sorted([*E.glob('C02_LATERAL_27*.json'),*E.glob('C02_LATERAL_28*.json')]):
 d=json.loads(p.read_bytes())['data']['result'];episodes=[]
 for e in d['episodes']:
  r=e['use']['rows'][0]
  episodes.append({'private':e['private_object'],'tick':r['tick'],'codes':[(z['bank'],z['target'],z['native']['s_reg'])for z in r['social_reads']if z['qualified']],'torque':r['executed_torque'],'occupied':e['after']['occupied']})
 print(json.dumps({'id':p.stem,'episodes':episodes,'final':d['final']},ensure_ascii=False))
