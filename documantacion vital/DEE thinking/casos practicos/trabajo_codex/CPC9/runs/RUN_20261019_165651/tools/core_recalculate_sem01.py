"""Separate nonphysical legacy repr addresses from exact native observations."""
from pathlib import Path
import json,re
RUN=Path(__file__).resolve().parents[1];p=RUN/'notes/core_audit/SEM01_v1/RECOVERY.json';v=json.loads(p.read_text(encoding='utf8'));changes=[]
for row in v['cases']:
 diffs=row['differences'].get('diagnostic_edits_actual',[])
 if not diffs:continue
 okay=all(re.sub(r' at 0x[0-9A-Fa-f]+',' at <HOST_ADDRESS>',x['actual'])==re.sub(r' at 0x[0-9A-Fa-f]+',' at <HOST_ADDRESS>',x['expected'])for x in diffs)
 changes.append({'id':row['id'],'pointer_only':okay,'original_differences':diffs});row['comparisons']['diagnostic_receipt_type_count_not_host_address_equal']=okay;row['comparisons'].pop('diagnostic_edits_actual');row['differences'].pop('diagnostic_edits_actual')
v['status']='PASS'if all(all(r['comparisons'].values())for r in v['cases'])else'FAIL';v['auditor_correction']={'physics_reexecuted':False,'original_report_preserved':str(p),'changes':changes,'scope':'LegacyrepraddressesarenotDEEphysicalstate. Exactinitial/finalRAWclocks,ticks,teaching,useframes,pre/postdiagnosticsandexternaloperationsremainunchangedandexact.'}
dest=RUN/'notes/core_audit/SEM01_RECALCULADO.json';dest.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'status':v['status'],'cases':len(v['cases'])}))
