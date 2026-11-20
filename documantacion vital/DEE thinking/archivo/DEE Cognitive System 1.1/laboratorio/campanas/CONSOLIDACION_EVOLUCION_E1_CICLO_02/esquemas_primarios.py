from pathlib import Path
import json
L=Path(__file__).resolve().parent;E=L.parents[2]/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
ids=['C02_GATE_050_RETORNO','C02_MAIN_174_PUERTA','C02_MAIN_171_USO','C02_DIV_080_MINUS','C02_REC_030_RECURSO','C02_PRE_110_PLUS_RESOURCE','C02_MAIN_120_RECURSO','C02_LATE_160_CONSERVAR','C02_CAUSAL_180_CORTE_MENOS']
for i in ids:
 p=E/(i+'.json')
 if not p.exists():print(i+' NOT_FOUND');continue
 d=json.loads(p.read_text(encoding='utf8'));v=d.get('data',d.get('result',{}));v=v.get('result',v)
 out={'id':i,'keys':list(v)}
 for key in('rows','frames','requests','actions','external','guard','cuts'):
  if key not in v:continue
  q=v[key];out[key]=list(q)if isinstance(q,dict)else{'len':len(q),'first_keys':list(q[0])if q and isinstance(q[0],dict)else None}
  if key=='requests'and q:out['receipt_example']=q[0]
 if 'rows'in v and v['rows']:
  row=v['rows'][0]
  if 'social_reads'in row:out['first_social_reads']=row['social_reads']
 print(json.dumps(out,ensure_ascii=False))
