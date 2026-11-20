"""Root documentary closure only. No Native import, state repair or lock removal."""
from pathlib import Path
import datetime, hashlib, json, subprocess
P=Path(__file__).resolve().parents[1]
C=P.parents[2]/'DEE Cognitive 2.0'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'file':str(p),'sha256':sha(p)}
def main():
 out=P/'control/CIERRE_OPERATIVO_FALLIDO_PI07_R01.json'
 if out.exists():raise FileExistsError('Preserve existing closure')
 ledger=P/'control/LEDGER_FINAL_GUARDADO_PI07_R01.json';ld=read(ledger)
 if (ld['Native_ticks_all_branches'],ld['diagnostic_worlds'])!=(83178,14):raise ValueError('Actual saved ledger differs')
 job=P/'control/JOB_Y_SNAPSHOT_FALLO_C2C34_PI07_R01.json';j=read(job)
 if j['exact_named_job_probe']['winerror']!=2 or j['exact_named_job_probe']['processes_stopped']:raise ValueError('Exact failed job absence proof required')
 ps="foreach($i in @(19224,19956)){ $p=Get-Process -Id $i -ErrorAction SilentlyContinue; [pscustomobject]@{id=$i;present=($null -ne $p)} | ConvertTo-Json -Compress }"
 q=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',ps],capture_output=True,text=True,encoding='utf8',timeout=30,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 if q.returncode:raise RuntimeError('Scoped PID query failed')
 pids=[json.loads(x)for x in q.stdout.splitlines()if x.strip()]
 if len(pids)!=2 or any(x['present']for x in pids):raise ValueError('A known affected process still exists')
 record=read(P/'REGISTRO_CAMPANA.json');protected={}
 for name in ('ACTIVO.json','VIDA.json','.deetsnap.gz'):
  found=[(Path(k),v)for k,v in record['protected_before'].items()if str(k).endswith(name)]
  if len(found)!=1:raise ValueError('Exact protected original expected: '+name)
  path,expected=found[0];current=sha(path)
  if current!=expected['sha256']:raise ValueError('Protected principal changed')
  protected[str(path)]={'before':expected['sha256'],'after':current,'equal':True}
 files=[ledger,job,P/'control/INSPECCION_FALLO_C2C34_PI07_R01.json',P/'control/COMPARACION_FUTURO_FALLIDO_C2C34_PI07_R01.json',P/'control/CIERRE_CONJUNTO_MATERIAL_PI07_R01.json',P/'control/DIAGNOSTICO_INCOMPATIBILIDAD_C2C34_PI07_R01.json',P/'control/RP_R03_INCORPORADA_PI07_R02.json']
 value={'schema':'DEE.PI07.scientific_negative_operational_closure.v1','status':'FAILED_CANDIDATE_PRESERVED_NO_LIVE_AFFECTED_WRITER','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'science_closed':True,'scientific_investigation_closed':True,'no_adoption':True,'no_live_affected_writers':True,'affected_pid_inventory_complete':False,'affected_job_scope_complete':True,'known_affected_pids':pids,'affected_writer_pids':[19224,19956],'exact_job_probe':j['exact_named_job_probe'],'owner_closed_gracefully':False,'historical_native_child_PID':'Not recorded; no invented enumeration. The unique enclosing job is absent, and its inherited safety adapter checks child membership before Native creation. This is scoped job/process evidence, never a global no-process claim.','failed_run':'PI07_CIERRE_CONJUNTO_FASE0_c1f133cf','candidate_life_id':'ECI02_PI03_REPRO_PI04_PI05_PI07_CAND_01','last_stable_native_tick':866067,'last_functional_native_tick_before_P0':866067,'new_native_ticks_in_failed_P0':0,'candidate_operational_state':'PARTIAL_INCONSISTENT_PRESERVED_NOT_CONTINUABLE','saved_failed_snapshot':j['saved_snapshot'],'last_stable_wording_limit':'The failed snapshot at the same tick preserves protocol34/uncertainty; it is not the preceding operational30 cut. Physical Native equality is not whole operational equality.','Native_ticks_all_branches':83178,'diagnostic_worlds':14,'source_evidence':[ref(p)for p in files],'preserved_failure_evidence_files':[ref(p)for p in files[1:6]],'source_refs':[ref(p)for p in files],'protected_principal_before_after':protected,'recovery':'No restore, replay, repair, queue purge, lock removal, new acquisition or promotion performed. Failed source/runtime files and all historical cuts remain local. New R03 reproduction uses the complete POST4 prefix and an exact PRE34 source capsule, with explicit new frontdoor replay pending.','work30_and_R03_EP16_executed':False,'Native_executed_by_closure':False}
 out.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'file':str(out),'sha256':sha(out),'science_closed':True,'Native_executed':False}))
if __name__=='__main__':main()
