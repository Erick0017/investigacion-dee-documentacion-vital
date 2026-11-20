"""Root-only exact two-file CAS supplement after scoped closed-process proof."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,shutil
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';STAGE=H/'CARGA_PREPARADA_PI09_R01_PROPUESTA';PROOF=P/'control/CARGA_PREPARADA_PI09_APLICADA_R01.json'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def regular(p):
 for n in(p,*p.parents):need(not n.exists()or not(n.is_symlink()or getattr(n.lstat(),'st_file_attributes',0)&1024),'No linked administrative source/target')
def critical():
 active=S/'estado/ACTIVO.json';paths=[active]
 for life in('ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01','ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01'):
  card=S/'estado/vidas'/life/'VIDA.json';r=read(card);paths.extend((card,S/r['snapshot'],S/'estado/servicios_persistentes'/r['world_id']/'cola.sqlite3'))
 return {str(p):sha(p)for p in paths}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');ap.add_argument('--process-proof',type=Path);a=ap.parse_args();plan=read(STAGE/'PLAN.json')
 for row in plan['files']:
  source=Path(row['source']);target=S/row['file'];regular(source);regular(target);need(sha(source)==row['sha256']and(sha(target)if target.exists()else None)==row['before_sha256'],'Exact code CAS differs')
 need(sha(Path(plan['preparation']['path']))==plan['preparation']['sha256']and sha(Path(plan['decision']['path']))==plan['decision']['sha256'],'Original preparation/decision changed')
 if not a.aplicar:print(json.dumps({'mode':'PLAN_ONLY','plan':str(STAGE/'PLAN.json'),'sha256':sha(STAGE/'PLAN.json'),'Native_executed':False}));return
 need(a.process_proof is not None and not PROOF.exists()and not(P/'PI09_ROOT_NATIVE_WRITER.lock').exists(),'Fresh explicit closed process proof and no Root writer required')
 process=a.process_proof.resolve(strict=True);need(process.is_relative_to((P/'control').resolve()),'Scoped process proof under P9/control');p=read(process)
 age=(datetime.now(timezone.utc)-datetime.fromisoformat(p['recorded_utc'])).total_seconds();need(p.get('schema')=='DEE.PI09.affected_writer_scope.v1'and p.get('no_live_affected_writers')is True and 0<=age<=600,'Actual fresh no-live-writer proof required')
 need(any(r.get('role')=='product_successor'and r.get('present')and r.get('no_live_affected_writer')for r in p['evidence']),'Exact moved product Native must be closed')
 before=critical();backup=H/'CARGA_PREPARADA_PI09_ORIGINALES_R01';need(not backup.exists(),'Previous partial deployment preserved');backup.mkdir()
 for row in plan['files']:
  target=S/row['file'];source=Path(row['source'])
  if target.exists():shutil.copyfile(target,backup/target.name)
  temp=target.with_name(target.name+'.PI09_PREPARED_WRITING');need(not temp.exists(),'Prior partial source deployment preserved');shutil.copyfile(source,temp);need(sha(temp)==row['sha256'],'Copy changed');os.replace(temp,target)
 need(critical()==before,'Administrative source supplement changed critical state')
 result={**plan,'schema':'DEE.PI09.prepared_load.administrative_supplement.applied.R01','applied':True,'recorded_utc':datetime.now(timezone.utc).isoformat(),'process_proof':{'path':str(process),'sha256':sha(process)},'critical_state_before_after_equal':True,'critical_state':before,'Native_executed':False,'new_ticks':0,'old_R02_transport_and_scientific_body_unchanged':True,'original_preparation_not_modified':True}
 with PROOF.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(PROOF),'sha256':sha(PROOF),'Native_executed':False,'critical_state_unchanged':True}))
if __name__=='__main__':main()
