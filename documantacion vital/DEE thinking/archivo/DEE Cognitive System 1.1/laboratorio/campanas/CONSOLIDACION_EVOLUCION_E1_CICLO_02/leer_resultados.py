"""Lectura compacta de registros; cero ticks y ningún Runtime."""
from pathlib import Path
import json
EV=Path(__file__).resolve().parents[2].parents[0]/'evidencia' # overwritten explicitly below
ROOT=Path(__file__).resolve().parent.parents[2]
EV=ROOT/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'

def q(r):return r.get('state')==1 and r.get('semantic')==1 and r.get('s_reg',0)>0
for p in sorted(EV.glob('C02_SOCIAL_0*.json')):
    d=json.loads(p.read_text(encoding='utf8'))['data']['result'];reads=[]
    for frame in d['frames']:
        if frame['tick']in [3420+67*i for i in range(7)]:
            reads.append({'tick':frame['tick'],'codes':[(r['sign'],r['read']['direction'],r['read']['s_reg'])for r in frame['reads']if 'read'in r and q(r['read'])]})
    print(json.dumps({'case':p.stem,'occupied':d['final']['occupied'],'tick':d['final']['tick'],'reads':reads,
          'legacy_delivery':[{r['sign']:r.get('delivery')for r in f['reads']}for f in d['frames']if f['tick']==3441]},ensure_ascii=False))
for p in sorted(EV.glob('C02_ACT_0*.json')):
    d=json.loads(p.read_text(encoding='utf8'))['data']['result'];rows=d['rows'];acts=[r['action']for r in rows]
    valid=[q(r)and r['direction'][0]==1 and abs(r['direction'][1])==1 and r['direction'][2]==0 for r in acts]
    useful=[v and a['direction'][1]==r['availability']for v,a,r in zip(valid,acts,rows)]
    print(json.dumps({'case':p.stem,'valid':sum(valid),'useful':sum(useful),'total':len(rows),
          'actions':[(a['direction'],a['s_reg'])for a in acts],'final':d['final']},ensure_ascii=False))
for p in sorted(EV.glob('C02_REC_0*.json')):
    d=json.loads(p.read_text(encoding='utf8'))['data']['result'];end=d['plan']['end_tick'];codes=[]
    for f in d['frames']:
        if f['tick']in(end,end+3,end+67,end+134,end+201,end+268):
            codes.append({'tick':f['tick'],'reads':[(r['sign'],k,r[k]['direction'],r[k]['s_reg'])for r in f['regions']for k in('original','alternative')if q(r[k])]})
    print(json.dumps({'case':p.stem,'codes':codes,'occupied':d['final']['occupied']},ensure_ascii=False))
