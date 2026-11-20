from pathlib import Path
import json
L=Path(__file__).resolve().parent;E=L.parents[2]/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
for name in('C02_SEPOP_357_USO4','C02_SEPOP_362_USO_TRAS_APRENDER'):
 d=json.loads((E/(name+'.json')).read_bytes())['result']['result']
 print(json.dumps({'id':name,'rows':[{'tick':r['tick'],'codes':[(z['bank'],z['target'],z['native']['s_reg'])for z in r['social_reads']if z['qualified']],'torque':r['executed_torque']}for r in d['rows']]},ensure_ascii=False))
for name in('SEPARACION_INCORPORACION_PARIDAD_357','SEPARACION_INCORPORACION_FINAL_364'):
 print((E/(name+'.json')).read_text(encoding='utf8'))
