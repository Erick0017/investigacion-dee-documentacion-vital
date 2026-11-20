from pathlib import Path
import json
L=Path(__file__).resolve().parent;E=L.parents[2]/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
for name in('C02_LATDIAG_314_MATERIAL','C02_LATDIAG_315_PASIVO'):
 d=json.loads((E/(name+'.json')).read_bytes())['data']['result'];f=d['first_departure']
 print(json.dumps({'id':name,'first_departure':f,'initial':d['initial'],'final':d['final']},ensure_ascii=False))
for name in('C02_LATDIAG_316_USO_PASIVO','C02_FINAL_320_USO','C02_FINAL_323_USO','C02_FINAL_326_USO'):
 p=E/(name+'.json')
 if not p.exists():continue
 d=json.loads(p.read_bytes())['result']['result']
 print(json.dumps({'id':name,'rows':[{'tick':r['tick'],'codes':[(z['bank'],z['target'],z['native']['s_reg'])for z in r['social_reads']if z['qualified']],'torque':r['executed_torque']}for r in d['rows']]},ensure_ascii=False))
