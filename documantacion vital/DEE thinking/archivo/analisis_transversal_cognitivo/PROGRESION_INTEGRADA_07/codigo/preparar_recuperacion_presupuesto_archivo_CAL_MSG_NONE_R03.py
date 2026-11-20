"""Prepare monotonic-decrease-only resume; never execute retirement here."""
from pathlib import Path
import ast,hashlib
H=Path(__file__).resolve().parent
def main():
 source=H/'reanudar_archivo_CAL_MSG_NONE_PI07_R02.py';text=source.read_text('utf8')
 text=text.replace('ARCHIVO_CAL_MSG_NONE_PI07_REANUDADO_R02.json','ARCHIVO_CAL_MSG_NONE_PI07_REANUDADO_R03.json')
 old="zip_hash=sha(ZIP);before=g['budget'](h);need(before<=g['LIMIT'],'Current fixed5.5GBbudget exceeded; preserve all')"
 new="zip_hash=sha(ZIP);before=g['budget'](h) # Actual overrun is recorded, never relabelled as within budget."
 if text.count(old)!=1:raise ValueError('Exact former safe refusal required')
 text=text.replace(old,new)
 needle=" retired=sum(sum(r['bytes']for r in inventories[name]['files'])for name in('CAL_SERVICIO_PERSISTENTE','CAL_TRABAJADOR_LOCAL'))"
 extra="\n extraction_bytes=sum(row['bytes']for row in actual_files)\n prospective_after=before-retired-extraction_bytes+1_000_000\n need(prospective_after<=g['LIMIT'],'Verified monotonic retirement would still exceed original5.5GB; no new allocation/removal authorized')"
 if text.count(needle)!=1:raise ValueError('Exact complete verification point required')
 text=text.replace(needle,needle+extra)
 text=text.replace("'logical_original_bytes_to_retire':retired,", "'logical_original_bytes_to_retire':retired,'actual_overrun_before':max(0,before-g['LIMIT']),'fixed_budget_unchanged':g['LIMIT'],'prospective_after_with_1MB_proof_allowance':prospective_after,'verification_extract_bytes_to_remove':extraction_bytes,")
 text=text.replace("'schema':'DEE.PI07.calibration_archive.resume.R02'", "'schema':'DEE.PI07.calibration_archive.resume.R03'",1)
 text=text.replace("'status':'ARCHIVED_VERIFIED_EXACT_SIDE_WORK_REMOVED'", "'status':'ARCHIVED_VERIFIED_EXACT_SIDE_WORK_REMOVED_BUDGET_RECOVERY'",1)
 old="'logical_before_resume':before,'logical_after':g['budget'](h),'fixed_budget':g['LIMIT']"
 new="'logical_before_resume':before,'actual_overrun_observed_before':max(0,before-g['LIMIT']),'prospective_after_with_1MB_proof_allowance':prospective_after,'verification_extract_bytes_removed':extraction_bytes,'logical_after':g['budget'](h),'fixed_budget':g['LIMIT'],'original_limit_not_reset':True,'historical_peak_not_measured':True,'prior_R01_PID_and_R02_budget_refusals_preserved':True,'allocation_policy':'No new ZIP/copy/extraction; streaming revalidation of existing bytes and exact authorized retirement only; proof under1MB.'"
 if text.count(old)!=1:raise ValueError('Exact final accounting point required')
 text=text.replace(old,new)
 old=" PROOF.write_bytes(g['enc'](result));print(json.dumps("
 new=" result['within_original_budget_after']=result['logical_after']<=g['LIMIT']\n if not result['within_original_budget_after']:result['status']='ARCHIVED_VERIFIED_DECREASED_BUT_CONCURRENT_GROWTH_STILL_OVER_BUDGET'\n need(len(g['enc'](result))<1_000_000,'Proof allocation allowance exceeded')\n PROOF.write_bytes(g['enc'](result));print(json.dumps("
 if text.count(old)!=1:raise ValueError('Exact proof serialization point required')
 text=text.replace(old,new);ast.parse(text)
 target=H/'reanudar_archivo_CAL_MSG_NONE_PI07_R03.py'
 if target.exists():raise FileExistsError('Preserve prior recovery source')
 target.write_text(text,encoding='utf8');print(target,hashlib.sha256(target.read_bytes()).hexdigest())
if __name__=='__main__':main()
