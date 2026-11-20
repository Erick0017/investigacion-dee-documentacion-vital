"""Fresh narrow read-only patch safety for closed DISCOVERY, no Native."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];S=P/'estados/DISCOVERY/sistema';L='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'
def main(a):
 assert not(P/'PI09_ROOT_NATIVE_WRITER.lock').exists()
 f=P/'codigo/comprobar_procesos_afectados_PI09_R01.py';sp=importlib.util.spec_from_file_location('PI09_single_closed_discovery',f);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 e=m.inspect('closed_discovery_for_code_preparation',S,L)
 out=a.salida.resolve();assert out.is_relative_to((P/'control').resolve())and not out.exists()
 v={'schema':'DEE.PI09.scoped_code_patch_process_proof.R01','recorded_utc':datetime.now(timezone.utc).isoformat(),'system':str(S.resolve()),'life_id':L,'safe_to_patch':e['no_live_affected_writer'],'no_live_affected_writers':e['no_live_affected_writer'],'scope':'Only the named closed unselected DISCOVERY code; this is no claim about pending PRODUCT transport.','evidence':e,'Native_imported_or_executed':False,'world_or_code_modified':False,'reuse_limit_seconds':600}
 out.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'proof':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'safe_to_patch':v['safe_to_patch']}))
 if not v['safe_to_patch']:raise SystemExit(2)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--salida',type=Path,required=True);main(p.parse_args())
