from pathlib import Path
import json
L=Path(__file__).resolve().parent;E=L.parents[2]/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
for p in sorted(E.glob('C02_COMMIT_34*.json')):
 d=json.loads(p.read_bytes())['data']['result'];r=next(x for x in d['frames']if x['tick']==3899)
 print(json.dumps({'id':p.stem,'at3899':r['body'],'record_status':[q['receipt']['status']for q in d['record_requests']],
  'protection_status':[q['receipt']['status']for q in d['protection_requests']]},ensure_ascii=False))
