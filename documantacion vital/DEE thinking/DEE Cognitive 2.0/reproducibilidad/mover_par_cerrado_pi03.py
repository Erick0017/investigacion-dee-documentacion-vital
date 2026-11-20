"""Verifica y, sólo con --aplicar, mueve UN export completo cerrado a RP.

No Native, copias masivas, promoción ni edición del estado exportado. Conserva
un mapa de procedencia: las rutas históricas de los recibos siguen intactas.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,sqlite3,subprocess,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;C=HERE.parent;DEE=C.parent
P=DEE/'archivo/analisis_transversal_cognitivo/PROGRESION_INTEGRADA_03'
CS=P/'estados/candidato/sistema';LIFE='ECI02_PI03_MAIN'
sys.path.insert(0,str(HERE))
from preservar_revision_pi03 import pair_check,valid_name,sha,read,bounded_source,unlinked
from observador_pasivo import snapshot_view,compare_native

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write_new(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('x',encoding='utf-8')as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--origen',required=True,type=Path)
 ap.add_argument('--alias',required=True);ap.add_argument('--tick',required=True,type=int)
 ap.add_argument('--manifest-sha256',required=True);ap.add_argument('--cierre',required=True,type=Path)
 ap.add_argument('--aplicar',action='store_true');ap.add_argument('--comprobante',type=Path)
 a=ap.parse_args();alias=valid_name(a.alias);source=bounded_source(a.origen)
 root=CS/'estado/servicios_persistentes'/LIFE/'exportaciones'
 if source.parent!=root or not source.is_dir():raise ValueError('Only one explicit MAIN closed export directly under the existing exportaciones directory')
 destination=HERE/'materiales'/alias
 if destination.exists():raise FileExistsError('Existing stable destination is protected')
 unlinked(destination.parent,DEE)
 if source.drive.casefold()!=destination.drive.casefold():raise ValueError('Only same-volume atomic relocation; no copy/delete fallback')
 proof_path=bounded_source(a.cierre);proof=read(proof_path)
 stamp=datetime.datetime.fromisoformat(proof['recorded_utc'].replace('Z','+00:00'))
 if stamp.tzinfo is None:raise ValueError('Zoned close/process proof required')
 age=(datetime.datetime.now(datetime.timezone.utc)-stamp).total_seconds()
 if not 0<=age<=600 or proof.get('no_live_affected_writers')is not True or LIFE not in proof.get('affected_life_ids',[])or not proof.get('evidence'):
  raise ValueError('Fresh explicit no-live-affected-owner proof is required')
 db=CS/'estado/servicios_persistentes'/LIFE/'cola.sqlite3'
 if (Path(str(db)+'-wal').exists()and Path(str(db)+'-wal').stat().st_size):raise ValueError('Source queue WAL is not closed')
 con=sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  owner=json.loads(con.execute("select value from meta where key='owner'").fetchone()[0])
  pending=con.execute("select id,status from requests where status in('queued','processing','uncertain')").fetchall()
 finally:con.close()
 if owner.get('running')or pending:raise ValueError('Source owner/requests are not closed')
 ps='$x=@(Get-Process -Id '+str(int(owner['pid']))+' -ErrorAction SilentlyContinue | Select-Object Id,ProcessName); ConvertTo-Json -InputObject $x -Compress'
 checked=subprocess.run(['powershell.exe','-NoProfile','-Command',ps],capture_output=True,text=True,check=True)
 if json.loads(checked.stdout or '[]'):raise ValueError('Recorded source owner PID still exists')
 entry={'source':str(source),'manifest_sha256':a.manifest_sha256,'life_id':LIFE,'N':67,'tick':a.tick}
 _,manifest,before=pair_check(entry)
 card=read(CS/'estado/vidas'/LIFE/'VIDA.json')
 if any(card['physical'][k]!=manifest['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')):
  raise ValueError('Source MAIN advanced or is not the exact closed export')
 # Saving/closing after an export can legitimately update administrative
 # service/system metadata without a Native step. Encoded hashes need not be
 # equal: compare the complete physical/causal prefix plus ALL non-service
 # metadata with the same established migration contract instead.
 current=snapshot_view(CS/card['snapshot']);exported=snapshot_view(source/'VIDA.deetsnap.gz')
 if current['encoded_sha256']!=card['snapshot_sha256']:raise ValueError('Current source checkpoint differs from its card')
 source_comparison=compare_native(exported,current,allow_service=True)
 cfg_path=HERE/'RECURSOS.json';cfgbytes=cfg_path.read_bytes();cfg=json.loads(cfgbytes)
 if alias in cfg['pairs']:raise FileExistsError('Existing alias must not be reassigned')
 report={'schema':'DEE.PI03.closed_pair_relocation.v1','recorded_utc':now(),'source':str(source),'destination':str(destination),
         'alias':alias,'life_id':LIFE,'N':67,'tick':a.tick,'manifest_sha256':a.manifest_sha256,
         'source_owner_pid_checked_absent':owner['pid'],'closed_process_proof':{'path':str(proof_path),'sha256':sha(proof_path)},
         'before':before,'applied':False,'completed':False,'new_native_ticks':0,'DEE_imports':0,'ACTIVO_changed':False,
         'historical_provenance_rewritten':False,'full_pair_copy_created':False}
 report['source_to_export_causal_comparison']=source_comparison
 report['source_checkpoint_encoded_sha256']=card['snapshot_sha256']
 report['export_snapshot_encoded_sha256']=manifest['snapshot_sha256']
 if not a.aplicar:print(json.dumps(report,ensure_ascii=False,indent=2));return 0
 if a.comprobante is None:raise ValueError('Explicit new relocation proof required')
 output=a.comprobante.absolute();unlinked(output.parent,DEE)
 if not output.is_relative_to(P)or output.exists():raise ValueError('A new proof within the existing PI03 campaign is required')
 stage=output.with_name(output.stem+'_EN_CURSO.json');write_new(stage,report)
 destination.parent.mkdir(parents=True,exist_ok=True);source.rename(destination)
 after_entry={**entry,'source':str(destination)};_,_,after=pair_check(after_entry)
 if after!=before:raise ValueError('Post-move verification differs; preserve destination and stage, never retry')
 if source.exists():raise ValueError('Original export still exists after move')
 if cfg_path.read_bytes()!=cfgbytes:raise ValueError('Resource registry changed concurrently; moved complete pair is preserved and stage records the interruption')
 cfg['pairs'][alias]={'product_relative':destination.relative_to(C).as_posix(),'manifest_sha256':a.manifest_sha256,
      'life_id':LIFE,'N':67,'tick':a.tick,'role':'final','source':str(source),
      'source_relocation':{'proof':str(output),'origin':str(source),'current':str(destination),'manifest_sha256':a.manifest_sha256}}
 tmp=cfg_path.with_name('RECURSOS.'+alias+'.writing')
 with tmp.open('x',encoding='utf-8')as f:json.dump(cfg,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,cfg_path)
 report.update(applied=True,completed=True,completed_utc=now(),after=after,previous_RECURSOS_sha256=hashlib.sha256(cfgbytes).hexdigest(),current_RECURSOS_sha256=sha(cfg_path),
               operational_state_and_global_snapshots_moved=False,original_path_absent=True)
 write_new(output,report);print(json.dumps(report,ensure_ascii=False,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
