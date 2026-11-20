"""Root-only dead-PID transport lock reconciliation; no SQLite/Native import.

Uses the already preserved raw interruption proof. Never changes queued ID,
WAL/SHM, snapshot, card, outbox or failures. Removes only its exact dead lock.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01';OUT=P/'control/CONCILIACION_LOCK_PRODUCTO_PI09_R04.json'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--conciliar',action='store_true');ap.add_argument('--preservation-proof',type=Path,required=True);a=ap.parse_args();file=a.preservation_proof.resolve(strict=True);need(file.is_relative_to((P/'control').resolve()),'Actual P9 preservation proof required');p=read(file)
 need(p['schema']=='DEE.PI09.dead_owner.interrupted_transport_preservation.R03'and p['life_id']==LIFE and p['source_raw_trio_and_markers_unchanged_during_copy']is True and p['logical_SQLite_integrity_of_COPY']=='ok','Exact preserved dead-owner copy required')
 installed=P/'control/CARGA_PREPARADA_PI09_APLICADA_R02.json';proof=read(installed);need(proof.get('applied')is True and proof['preservation_proof']['sha256']==sha(file),'Actual corrected full-payload gate must be applied first')
 for row in proof['files']:need(sha(S/row['file'])==row['sha256'],'Applied full-payload source changed')
 lock=S/'estado/locks'/(LIFE+'.lock');row=next(r for r in p['files']if Path(r['source'])==lock);need(lock.is_file()and sha(lock)==row['sha256']and read(lock)['pid']==p['Win32_process']['pid'],'Only the exact preserved stale lock may reconcile')
 for item in p['files']:need(sha(Path(item['source']))==item['sha256']and sha(Path(item['copy']))==item['sha256'],'Preserved card/snapshot/queue/raw journal/lock changed')
 module=H/'comprobar_procesos_afectados_PI09_R01.py';sp=importlib.util.spec_from_file_location('PI09_lock_only_pid_check',module);check=importlib.util.module_from_spec(sp);sp.loader.exec_module(check);process=check.pid_proof(p['cached_owner_from_COPY']);need(process.get('present')is False and process.get('no_live_affected_writer')is True,'Exact original owner PID must currently be absent; no process is stopped')
 need(not(P/'PI09_ROOT_NATIVE_WRITER.lock').exists(),'Root writer exists; never clear it or create another')
 if not a.conciliar:print(json.dumps({'mode':'PLAN_ONLY','exact_lock':str(lock),'pending_STATE_id':p['pending_in_COPY'][0]['id'],'process':process,'Native_executed':False}));return
 need(not OUT.exists(),'Reconciliation already recorded or partial future preserved');lock.unlink()
 need(all(sha(Path(i['source']))==i['sha256']for i in p['files']if Path(i['source'])!=lock),'Something other than the exact stale lock changed')
 result={'schema':'DEE.PI09.dead_owner.exact_stale_lock_reconciliation.R04','recorded_utc':datetime.now(timezone.utc).isoformat(),'life_id':LIFE,'preservation':{'path':str(file),'sha256':sha(file)},'full_payload_gate':{'path':str(installed),'sha256':sha(installed)},'actual_Win32_process':process,'only_removed_lock':{'path':str(lock),'preserved_sha256':row['sha256'],'preserved_copy':row['copy']},'pending_STATE_id_unchanged':p['pending_in_COPY'][0]['id'],'SQLite_WAL_SHM_card_snapshot_unchanged':True,'original_SQLite_opened':False,'Native_imported_or_executed':False,'new_ticks':0,'next':'Root may start exactly one Owner with corrected sources and complete the existing queued STATE by its same ID; do not re-admit it.'}
 with OUT.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(OUT),'sha256':sha(OUT),'Native_executed':False,'existing_STATE_not_resubmitted':True}))
if __name__=='__main__':main()
