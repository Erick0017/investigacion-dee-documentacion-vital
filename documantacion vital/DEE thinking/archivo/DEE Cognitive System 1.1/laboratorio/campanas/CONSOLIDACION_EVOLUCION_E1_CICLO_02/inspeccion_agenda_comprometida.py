from pathlib import Path
import json
L=Path(__file__).resolve().parent;E=L.parents[2]/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
for p in sorted(E.glob('C02_COMMIT_34*.json')):
 d=json.loads(p.read_bytes())['data']['result'];rows=[]
 for f in d['frames']:
  codes=[z['sign']for z in f['ports']if z['read']['state']==1 and z['read']['semantic']==1 and z['read']['s_reg']>0 and z['read']['direction']==[z['sign'],0,0]]
  if f['tick']%67==3 or f['tick']==3363:rows.append({'tick':f['tick'],'B':f.get('B'),'codes':codes,'occupied':f['global']['occupied']})
 print(json.dumps({'id':p.stem,'private':d['private_value'],'body_initial':d['body_initial'],'rows':rows,'final':d['final']},ensure_ascii=False))
