"""Root-only code CAS; preserves the exact dead-owner pending STATE and WAL.

Reads the immutable audit proof/copy only. Does not open original SQLite,
checkpoint, remove locks, resume a request or create a second writer.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,shutil
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';STAGE=H/'CARGA_PREPARADA_PI09_R02_PROPUESTA';PROOF=P/'control/CARGA_PREPARADA_PI09_APLICADA_R02.json';PENDING='PI09_PRODUCT0_UNSELECTED_R03_PI09'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def regular(p):
 for n in(p,*p.parents):need(not n.exists()or not(n.is_symlink()or getattr(n.lstat(),'st_file_attributes',0)&1024),'No linked source/target')
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');ap.add_argument('--preservation-proof',type=Path,required=True);a=ap.parse_args();plan=read(STAGE/'PLAN.json');proof=a.preservation_proof.resolve(strict=True);need(proof.is_relative_to((P/'control').resolve()),'Exact P9 preservation proof');p=read(proof)
 need(p.get('schema')=='DEE.PI09.dead_owner.interrupted_transport_preservation.R03'and p.get('life_id')=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01'and p.get('source_raw_trio_and_markers_unchanged_during_copy')is True and p.get('logical_SQLite_integrity_of_COPY')=='ok'and p.get('original_SQLite_opened')is False and p['Win32_process'].get('no_live_affected_writer')is True and p['Win32_process'].get('present')is False,'Actual dead-owner preserved audit proof required')
 expected={'actuador':'closed','operacion':'sesion','retorno':'omit','situaciones':[{'modo':'eci01-pi09-estado'}]};pending=p['pending_in_COPY'];need(len(pending)==1 and pending[0]['id']==PENDING and pending[0]['status']=='queued'and json.loads(pending[0]['payload'])==expected,'Only the exact already-admitted STATE remains queued; no re-admission/purge')
 for row in p['files']:need(sha(Path(row['source']))==row['sha256']and sha(Path(row['copy']))==row['sha256'],'Dead-owner raw state or its preserved copy changed')
 for row in plan['files']:
  source=Path(row['source']);target=S/row['file'];regular(source);regular(target);need(sha(source)==row['sha256']and(sha(target)if target.exists()else None)==row['before_sha256'],'Exact source CAS differs')
 for ref in(plan['preparation'],plan['decision'],plan['prior_supplement']):need(sha(Path(ref['path']))==ref['sha256'],'Original preparation/decision/R01 supplement changed')
 if not a.aplicar:print(json.dumps({'mode':'PLAN_ONLY','plan':str(STAGE/'PLAN.json'),'sha256':sha(STAGE/'PLAN.json'),'pending_id':PENDING,'Native_executed':False}));return
 need(0<=(datetime.now(timezone.utc)-datetime.fromisoformat(p['recorded_utc'])).total_seconds()<=600,'Fresh dead-owner scope proof required (600s); preserve, never widen TTL')
 need(not PROOF.exists()and not(P/'PI09_ROOT_NATIVE_WRITER.lock').exists(),'No other Root writer or prior supplement')
 active=S/'estado/ACTIVO.json';active_sha=sha(active);backup=H/'CARGA_PREPARADA_PI09_ORIGINALES_R02';need(not backup.exists(),'Prior partial deployment preserved');backup.mkdir()
 for row in plan['files']:
  target=S/row['file'];source=Path(row['source'])
  if target.exists():shutil.copyfile(target,backup/target.name)
  temp=target.with_name(target.name+'.PI09_PREPARED_R02_WRITING');need(not temp.exists(),'Partial deployment preserved');shutil.copyfile(source,temp);need(sha(temp)==row['sha256'],'Copy changed');os.replace(temp,target)
 need(sha(active)==active_sha and all(sha(Path(r['source']))==r['sha256']for r in p['files']),'Administrative source CAS changed ACTIVO/card/snapshot/queue/WAL/SHM/lock')
 result={**plan,'schema':'DEE.PI09.prepared_load.administrative_supplement.applied.R02','applied':True,'recorded_utc':datetime.now(timezone.utc).isoformat(),'preservation_proof':{'path':str(proof),'sha256':sha(proof)},'critical_state_before_after_equal':True,'Native_executed':False,'new_ticks':0,'original_SQLite_opened':False,'no_locks_removed':True,'pending_STATE_preserved_by_existing_id':PENDING,'original_preparation_not_modified':True}
 with PROOF.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(PROOF),'sha256':sha(PROOF),'Native_executed':False,'pending_id_unchanged':PENDING}))
if __name__=='__main__':main()
