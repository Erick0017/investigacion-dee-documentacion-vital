"""Correct the auditor's tuple/file-name comparison without rerunning physics."""
import hashlib,json,sys
from pathlib import Path
RUN=Path(__file__).resolve().parents[1];CORE=RUN/'core/DEE_COGNITIVE_CORE'
sys.path.insert(0,str(CORE/'reproduccion'));from worker_core import compare_data
actualroot=RUN/'notes/core_audit/CP01_v2';mat=RUN.parents[7]/'_cpc9_core_materialized_20261019_165651'
# Resolve explicit workspace ancestor by a directory that actually contains this cut.
mat=next(p/'_cpc9_core_materialized_20261019_165651'for p in RUN.parents if(p/'_cpc9_core_materialized_20261019_165651').is_dir())
rows=[]
for field in('C01','C02','C03','C04','C05','C06','C07','C08_INTERFACE_V2'):
 a=json.loads((actualroot/'casos'/field/'RESULTADOS.json').read_text(encoding='utf8'))
 p=mat/'historico/CPC3/genealogia/CP01_C08/casos'/field/'RESULTADOS.json';b=json.loads(p.read_text(encoding='utf8'))
 diffs=compare_data(a['measurements'],b['measurements']);phys=compare_data([r['state']for r in a['checkpoints']],[r['state']for r in b['checkpoints']])
 rows.append({'field':field,'measurement_equal':not diffs,'all_full_RAW_clocks_tick_digests_equal':not phys,'measurement_differences':diffs,'physical_differences':phys,'original_primary_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'filename_metadata_differences':[(x['name'],y['name'])for x,y in zip(a['checkpoints'],b['checkpoints'])if x['name']!=y['name']]})
v={'schema':'CPC9.CP01.auditor_correction.v1','status':'PASS'if all(r['measurement_equal']and r['all_full_RAW_clocks_tick_digests_equal']for r in rows)else'FAIL','cases':rows,'physics_reexecuted':False,'correction':'Initialauditor compared live tuple vs JSONlist asdifferenttype and historical attempt2filename asphysicaldifference. Actualnativeobservations were unchanged. This report recalculates from alreadycompleted actualRESULTADOS, not regeneratedtargets.','previous_report_preserved':str(actualroot/'RECOVERY.json')}
(RUN/'notes/core_audit/CP01_RECALCULADO.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'status':v['status'],'cases':len(rows)}))
