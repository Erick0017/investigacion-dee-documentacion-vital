from pathlib import Path
import json
L=Path(__file__).resolve().parent;E=L.parents[2]/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
for name in('C02_DETOUR_230_CONSERVAR','C02_DETOUR_231_SHAM'):
 d=json.loads((E/(name+'.json')).read_bytes())['data']['result'];out={'id':name,'final':d['final'],'frames':[{'tick':f['tick'],'old':{k:f['old_expected'][k]for k in('state','s_reg','direction')}}for f in d['frames']],'uses':[]}
 for use in d['uses']:
  for row in use['rows']:out['uses'].append({'tick':row['tick'],'codes':[{'bank':z['bank'],'site':z['target'],'load':z['native']['s_reg']}for z in row['social_reads']if z['qualified']],'torque':row['executed_torque'],'quantity':row['native']})
 out['requests']={k:[r['receipt']['status']for r in d[k]]for k in('first_detour_requests','second_detour_requests')}
 print(json.dumps(out,ensure_ascii=False))
for name in('C02_RET_291_USO','C02_RET_293_USO_ANTERIOR','C02_LATOP_306_USO','C02_LATOP_309_SIN_NUEVO_B'):
 p=E/(name+'.json')
 if not p.exists():continue
 d=json.loads(p.read_bytes())['result']['result']
 print(json.dumps({'id':name,'rows':[{'tick':r['tick'],'codes':[(z['bank'],z['target'],z['native']['s_reg'])for z in r['social_reads']if z['qualified']],'torque':r['executed_torque']}for r in d['rows']]},ensure_ascii=False))
for p in sorted(E.glob('C02_DETOUR_24*.json')):
 d=json.loads(p.read_bytes())['data']['result'];out={'id':p.stem,'episodes':[],'final':d['final']}
 for e in d['episodes']:
  r=e['use']['rows'][0];out['episodes'].append({'private':e['private_object'],'tick':r['tick'],'codes':[(z['bank'],z['target'],z['native']['s_reg'])for z in r['social_reads']if z['qualified']],'torque':r['executed_torque']})
 print(json.dumps(out,ensure_ascii=False))
