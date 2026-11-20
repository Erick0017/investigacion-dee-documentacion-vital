"""Prospective phase allocation only; total time and safety limits unchanged."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,os,shutil
P=Path(__file__).resolve().parents[1];F=P/'REGISTRO_CAMPANA.json';O=P/'control/REDISTRIBUCION_PROSPECTIVA_CIERRE_PI09_R03.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not O.exists();r=json.loads(F.read_text('utf-8-sig'));old=dict(r['budget']);hard=datetime.fromisoformat(old['hard_stop_local']);cut=datetime.fromisoformat(old['new_experimental_uses_cutoff_local']);now=datetime.now(timezone.utc)
assert now<cut and old['Native_ticks_all_branches']==220000 and old['owned_Native_job_memory_bytes']==536870912 and (hard-cut).total_seconds()==4200
new=cut+timedelta(minutes=10);assert (hard-new).total_seconds()==3600
backup=P/'control/REGISTRO_ANTES_REDISTRIBUCION_CIERRE_PI09_R03.json';shutil.copyfile(F,backup)
r['budget']['new_experimental_uses_cutoff_local']=new.isoformat();changes={k:{'before':old[k],'after':r['budget'][k]}for k in old if old[k]!=r['budget'][k]};assert set(changes)=={'new_experimental_uses_cutoff_local'}
reason='Prospective redistribution of10minutes from the70minute editorial reserve to decisive D controls/replay/conservation. Manual1.37 already published, final1.38 helper and packager prepared;60minutes of final closure remain. No optional reference displaces mandatory controls/conservation; no test criterion, total/hard deadline, ticks, memory, storage or kernel change.'
v={'schema':'DEE.PI09.prospective_phase_time_reallocation.R03','recorded_utc':now.isoformat(),'changes':changes,'hard_stop_unchanged':hard.isoformat(),'remaining_editorial_reserve_seconds':3600,'other_limits_unchanged':{k:z for k,z in old.items()if k!='new_experimental_uses_cutoff_local'},'old_record':{'path':str(backup),'sha256':sha(backup)},'reason':reason,'current_running_plan_keeps_its_original_captured_budget':True,'already_executed_science_unchanged':True,'Native_executed':False}
r['budget_revisions'].append({'path':str(O),'recorded_utc':now.isoformat(),'changes':changes,'reason':reason});tmp=F.with_name(F.name+'.PI09TIME');tmp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf8');os.replace(tmp,F);O.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'proof':str(O),'sha256':sha(O),'new_experiment_cutoff':new.isoformat(),'hard_stop_unchanged':hard.isoformat(),'Native_executed':False}))
