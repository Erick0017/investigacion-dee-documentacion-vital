"""Post-trajectory comparison, preserving the initial incorrect auditor criteria."""
import json,sys
from pathlib import Path
RUN=Path(__file__).resolve().parents[1];CORE=RUN/'core/DEE_COGNITIVE_CORE';sys.path.insert(0,str(CORE/'reproduccion'))
from worker_core import assess_repertoire
mat=next(p/'_cpc9_core_materialized_20261019_165651'for p in RUN.parents if(p/'_cpc9_core_materialized_20261019_165651').is_dir());base=RUN/'notes/core_audit/K65_v1';rows=[]
for name in('K65_PAIRED','K65_UNPAIRED','K65_RESERVE','K65_REVISION_CADENCE','K65_REVISION_OFFPATH'):
 v=json.loads((base/name/'MEASUREMENTS.json').read_text(encoding='utf8'));rows.append(assess_repertoire(mat,name,v))
out={'schema':'CPC9.K65.auditor_correction.v1','status':'PASS'if all(r['passed']for r in rows)else'FAIL','cases':rows,'physics_reexecuted':False,'initial_auditor_report_preserved':str(base/'RECOVERY.json'),'correction':'Theinitialauditorincorrectlyassumedunpairedhistoriesmustremainbelow65afterallqueries,andalloffpathotherrelationsmuststay64. Frozenhistoricaladverseresultsare32→65→65and63/64respectively. Thisauditcomparesexactnativeobservations/inputs/finalstate,notaretuneddecoderornewpositiveclaim.'}
(RUN/'notes/core_audit/K65_RECALCULADO.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'status':out['status'],'comparisons':[(r['case'],r['exact_historical_checks'])for r in rows]}))
