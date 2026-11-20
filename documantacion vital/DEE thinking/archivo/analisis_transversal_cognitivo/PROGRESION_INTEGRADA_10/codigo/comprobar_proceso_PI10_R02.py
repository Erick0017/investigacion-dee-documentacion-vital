"""Read-only exact never-owned-import guard, preserving strict used-owner checks.

No PID/lock/queue repair or Native imports. An absent cached owner PID alone
is never safe: only exact closed0tick import evidence and unchanged imported
card/snapshot/SQLite permit the narrow first-owner path.
"""
from pathlib import Path
import hashlib,importlib.util,json,sqlite3
P=Path(__file__).resolve().parents[1];OLD=P.with_name('PROGRESION_INTEGRADA_09')/'codigo/comprobar_procesos_adopcion_D_PI09_R01.py';PIN='9222b2fb422bb3c19d9ed4c5bf1785d2f987dd0d5533ddf9242600a563e22107'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def inspect(role,system,life):
 need(sha(OLD)==PIN,'Original strict scoped process checker changed');sp=importlib.util.spec_from_file_location('PI10_original_strict_used_owner_guard',OLD);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);system=Path(system).resolve(strict=True);result=m.inspect(role,system,life)
 if result.get('no_live_affected_writer'):return result
 # Do not relax any actual previously-owned process/PID/queue condition.
 if result.get('Win32_process',{}).get('reason')!='No actual cached owner PID':return result
 if system.parent.parent!=(P/'estados').resolve()or not life.startswith('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_'):return result
 db=Path(result['SQLite']['path']);need(result['SQLite']['integrity_check']=='ok'and not result['SQLite']['unresolved']and not result['preserved_marker_paths']and result['SQLite']['WAL_bytes']==result['SQLite']['SHM_bytes']==0,'Imported no-PID source must still be integral, idle and marker-free')
 con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 try:owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])
 finally:con.close()
 need(owner.get('running')is False and owner.get('imported_not_yet_started')is True and not owner.get('pid'),'Only actual never-owned imported cache, no fabricated absent-PID repair')
 proof_file=system.parent/'IMPORTACION_PI10.json';proof=read(proof_file);need(proof.get('schema')=='DEE.PI10.actual_complete_current_D_import.R01'and proof.get('life_id')==life and proof.get('closed')is True and proof.get('error')is None and proof.get('new_Native_ticks')==0 and proof.get('protected_main_unchanged')is True,'Exact Root complete closed import0 proof required')
 imported_file=system.parent/'IMPORTACION_DIAGNOSTICA.json';imported=read(imported_file);need(imported['life']==life and imported['new_native_ticks']==0 and imported['principal_selected']is False and imported['comparison']['physical_equal']and imported['comparison']['causal_prefix_equal'],'Official unchanged complete paired import required')
 supplement=proof['directory_transport'];need(supplement['applied']and supplement['Native_card_snapshot_SQLite_and_A_all_unchanged']and supplement['new_Native_ticks']==supplement['new_Native_inputs']==supplement['files_written']==0,'Exact reviewed directory-only supplement required')
 for key in('card','snapshot','SQLite'):
  path=Path(result[key]['path']);need(supplement['critical_hashes_before'].get(str(path))==sha(path),'Imported '+key+' changed: first-owner exception no longer applies')
 source=read(system.parent/'CONTEXTO_EJECUCION.json');need(source['life']==life and source['prefix_manifest_sha256']==proof['source_manifest_sha256']==imported['result']['verification']['manifest_sha256'],'Current scope/full import proof identity mismatch')
 need(sha(Path(source['prefix'])/'EXPORTACION_SERVICIO.json')==proof['source_manifest_sha256'],'Original paired prefix changed')
 process=m.pid_proof({'pid':proof['importer_PID'],'running':False,'wall_utc':supplement.get('recorded_utc')});need(process['no_live_affected_writer'],'Actual importer PID not proven exited/absent')
 result['no_live_affected_writer']=True;result['never_owned_exact_closed_import_exception']={'schema':'DEE.PI10.never_owned_exact_closed_import_guard.R02','import_proof':{'path':str(proof_file),'sha256':sha(proof_file)},'official_import':{'path':str(imported_file),'sha256':sha(imported_file)},'actual_importer_process_fresh':process,'imported_card_snapshot_SQLite_literal_unchanged':True,'cached_owner_imported_not_yet_started':True,'no_states_queues_locks_or_processes_modified':True,'strict_used_owner_checks_unchanged':True};return result
