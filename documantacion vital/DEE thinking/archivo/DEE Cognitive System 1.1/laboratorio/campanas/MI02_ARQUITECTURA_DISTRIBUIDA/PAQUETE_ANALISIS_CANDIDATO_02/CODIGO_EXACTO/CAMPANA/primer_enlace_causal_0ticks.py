"""Read existing R4 fields/receipts only; no native ticks or recovered answers."""
import collections,hashlib,importlib.util,json
from pathlib import Path
L=Path(__file__).resolve().parent;R=L.parents[2];E=R/'evidencia/campanas/MI02_ARQUITECTURA_DISTRIBUIDA';S=R/'sistema'
spec=importlib.util.spec_from_file_location('snapshot',S/'capacidades/observador_causal_retrospectivo_01.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
results=[]
for case in(50,51,52,53):
    p=E/('CONTROLADOR_VIVIR_'+str(case)+'.json');d=json.loads(p.read_bytes());z=d['data']['result'];rec=d['after'];x=m.Snapshot(S/rec['snapshot']);c=[8,8,8];neighbours=[];grad=[0,0,0]
    for dx in(-1,0,1):
        for dy in(-1,0,1):
            for dz in(-1,0,1):
                if not any((dx,dy,dz)):continue
                v=x.observation([c[0]+dx,c[1]+dy,c[2]+dz])
                if v['state']>0:
                    neighbours.append(v)
                    for k,h in enumerate((dx,dy,dz)):grad[k]-=h*v['s_reg']
    selected=[]
    for row in z['rows'][:2]:
        for frame in row['frames']:
            if frame['tick']in(row['critical_tick']-1,row['critical_tick'],row['critical_tick']+1,row['critical_tick']+2):
                selected.append({'tick':frame['tick'],'Q':frame['Q'],'memories':frame['M'],'alive_neighbours':[sum(v['state']>0 and v['semantic']!=5 for v in group if v['site']!=frame['M'][i]['site'])for i,group in enumerate(frame['neighbourhoods'])],'contact':frame['contacts'],'heads':frame['return_heads']})
    results.append({'case':case,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'current_Q':x.observation(c),'current_Q_neighbours':neighbours,'gradient_recomputed':grad,'requests':dict(collections.Counter(t['receipt']['status']for t in z['requests'])),'selected_first_frames':selected,'no_ticks':True})
(E/'PRIMER_ENLACE_CAUSAL_0TICKS.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
for v in results:print(json.dumps({'case':v['case'],'Q':v['current_Q'],'grad':v['gradient_recomputed'],'requests':v['requests'],'first_memory_neighbours':[(q['tick'],q['alive_neighbours'],[a['s_reg']for a in q['memories']],q['Q']['state'],q['Q']['direction'])for q in v['selected_first_frames']]},ensure_ascii=False))
