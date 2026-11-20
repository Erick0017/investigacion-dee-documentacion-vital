from pathlib import Path
import json,gzip
L=Path(__file__).resolve().parent;E=L.parents[2]/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
m=json.loads((E/'CALCULOS_REPETIBLES.json').read_bytes())
for k,v in m['social_cases'].items():
 if not k.startswith('C02_CAUSAL_'):continue
 print(json.dumps({'id':k,'expected':v['B_expected_auditor_only'],'frames':[{'tick':f['tick'],'codes':f['codes']}for f in v['frames']],
  'cuts':v['cuts'],'record_requests':v['record_requests'],'occupation':[{'tick':q['tick'],'occupied':q['occupied']}for q in v['occupation']]},ensure_ascii=False))
for k in('C02_MAIN_171_USO','C02_MAIN_172_USO','C02_MAIN_175_EXTERNO','C02_ACCESS_120_USO4'):
 if k not in m['external_cases']:continue
 print(json.dumps({'id':k,'rows':[{'tick':r['tick'],'qualified':[(z['bank'],z['site'],z['fields']['s_reg'])for z in r['social']if z['qualified']],'torque':r['torque']}for r in m['external_cases'][k]['rows']]},ensure_ascii=False))
for k in('C02_REPET_190_DOS_CAPAS','C02_REPET_191_UNA_CAPA','C02_REPET_192_SIN_PERDIDA_PREVIA','C02_REPET_193_SIN_CONTENIDO'):
 p=E/'EXPORTACION/EVIDENCIA_CAUSAL/PRIMARIOS'/(k+'.json.gz');d=json.loads(gzip.decompress(p.read_bytes()))['payload'];qs=d['query_ticks']
 print(json.dumps({'id':k,'query_ticks':qs,'frames':[{'tick':f['tick'],'codes':[(z['bank'],z['zoffset'],z['read']['s_reg'])for z in f['ports']if z['read']['state']==1 and z['read']['semantic']==1 and z['read']['s_reg']>0 and z['read']['direction']==[z['bank'],0,0]]}for f in d['frames']if f['tick']in(qs[0]+3,qs[0]+67,qs[1]+3)],
   'uses':[(r['tick'],[(x['bank'],x['site'],x['fields'])for x in r['social']if x['qualified']])for r in m['recovery_cases'][k]['rows']]},ensure_ascii=False))
