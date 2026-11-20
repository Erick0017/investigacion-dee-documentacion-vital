from pathlib import Path
import json
L=Path(__file__).resolve().parent;E=L.parents[2]/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
for p in sorted(E.glob('C02_SEPARA_33*.json')):
 d=json.loads(p.read_bytes())['data']['result'];stages=[]
 for label,use in(('first',d['first_uses']),('new_B',d['new_use']),('last',d['last_use'])):
  for r in use['rows']:stages.append({'stage':label,'tick':r['tick'],'codes':[(z['bank'],z['target'],z['native']['s_reg'])for z in r['social_reads']if z['qualified']],'torque':r['executed_torque']})
 print(json.dumps({'id':p.stem,'interventions':[r['receipt']['status']for r in d['requests']],'uses':stages,'final':d['final'],'planned_cut':d['planned_cut']},ensure_ascii=False))
