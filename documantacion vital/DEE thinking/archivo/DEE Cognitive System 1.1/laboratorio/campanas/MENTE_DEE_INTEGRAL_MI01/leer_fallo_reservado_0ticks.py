"""Read the passively reproduced reserved trajectory; not an inverse kernel."""
import json,hashlib
from pathlib import Path
L=Path(__file__).resolve().parent;R=L.parents[2];E=R/'evidencia/campanas/MENTE_DEE_INTEGRAL_MI01';p=E/'MI01_470_TRAZA_RESERVA.json';d=json.loads(p.read_bytes())['data']['result'];rows=[]
for frame in d['frames']:
    for item in frame['items']:
        rows.append({'tick':frame['tick'],'occupied':frame['physical']['occupied'],'snapshot':frame['diagnostic_snapshot'],'snapshot_sha256':frame['snapshot_sha256'],**item})
first_B=next(x for x in rows if x['label']=='B_private_reply');sign=first_B['native']['direction'][0];used=[x for x in rows if x['label'].startswith('post_return_'+str(sign)+'_')]
first_bad=next((x for x in used if x['native']['direction']!=x['expected_direction']or x['native']['s_reg']!=first_B['native']['s_reg']or x['native']['state']!=1),None)
out={'native_ticks':0,'source':str(p.relative_to(R)),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'actual_first_B_reply':first_B,'measured_sign':sign,'candidate_path_first_nonmatching_turn':first_bad,'all_candidate_path_turns':used,'occupied_samples':[{'tick':x['tick'],'occupied':x['physical']['occupied'],'RAW_sha256':x['physical']['RAW_sha256']}for x in d['frames']],'limits':'Following the prepared route and equal payload is only a candidate dependency chain, not unique carrier identity. Full pre/post states and selective interventions are required for causal attribution. Diagnostic snapshots inside the bridge step are not operational continuation boundaries.'}
(E/'PRIMER_FALLO_RESERVADO_471_0TICKS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'B':{k:first_B[k]for k in('tick','occupied','native')},'first_nonmatching_turn':{k:first_bad[k]for k in('tick','occupied','label','site','expected_direction','native')}if first_bad else None,'turns':[{'tick':x['tick'],'direction':x['native']['direction'],'payload':x['native']['s_reg'],'occupied':x['occupied']}for x in used]},ensure_ascii=False))
