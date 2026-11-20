"""Root's finite experiment schedule, not an agent action policy.

One imported diagnostic and one owner at a time. No retries or restoration.
Default only prints the fixed plan. Native runs only under --ejecutar and a
supplied hash after the central candidate has actually closed coherently.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,subprocess,sys
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';PY=C/'motor/python313/python.exe'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def main(a):
 config=H/'CONTROLES_SECUENCIALES_PI11_R01.json';v=read(config)
 need([r['slug']for r in v['arms']]==['HEREDADO01','NONE01','YOKE01'],'Exactly three prospectively prepared controls')
 if not a.ejecutar:print(json.dumps({'mode':'PLAN_ONLY','sha256':sha(config),'arms':v['arms'],'Native':0}));return
 need(Path(sys.executable).resolve()==PY.resolve()and a.config_sha256==sha(config),'Root exact interpreter and explicit frozen plan hash')
 proof=read(P/'control/PI11_MAIN01_16_OWNER_R01.json');need(proof['closed']and proof['error']is None and proof['status']=='CLOSED_FINITE_PHASE','Candidate is not actually closed; never overlap owner')
 need(not(P/'PI11_ROOT_NATIVE_WRITER.lock').exists()and not(C/'reproducibilidad/EJECUCION_MATERIAL.lock').exists(),'An owner/importer is still declared')
 intent=P/'control/CONTROLES_SECUENCIALES_PI11_R01.INTENT.json'
 with intent.open('x',encoding='utf8')as f:json.dump({'started_utc':datetime.now(timezone.utc).isoformat(),'config_sha256':sha(config),'no_automatic_retry':True},f,indent=2)
 for arm in v['arms']:
  slug=arm['slug'];dest=P/'estados'/slug;manifest=dest/'SISTEMA_CODIGO_PI11.json'
  need(sha(manifest)==arm['code_manifest_sha256'],'Control code changed before import')
  print('BEGIN_CONTROL '+slug,flush=True)
  command=[str(PY),'-I','-B','-X','utf8',str(H/'pi11_clonar_R01.py'),'--slug',slug,'--vida',arm['life_id'],'--rol',arm['role'],'--prefijo',str(P/'pares/PRINCIPAL_REAL2_T947395'),'--manifest-sha256',v['source_manifest_sha256'],'--importar','--codigo-cerrado-sha256',arm['code_manifest_sha256']]
  subprocess.run(command,cwd=P,check=True)
  plan=H/arm['plan'];need(sha(plan)==arm['plan_sha256'],'Frozen control plan changed')
  subprocess.run([str(PY),'-I','-B','-X','utf8',str(H/'pi11_ejecutar_plan_R01.py'),'--plan',str(plan),'--plan-sha256',arm['plan_sha256'],'--ejecutar'],cwd=P,check=True)
  result=read(P/'control'/(arm['tag']+'.json'));need(result['closed']and result['error']is None,'Control future preserved; no next owner')
  print('CLOSED_CONTROL '+slug+' '+str(result['final_tick']),flush=True)
 print('ALL_THREE_CONTROLS_CLOSED_NO_ADOPTION',flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--ejecutar',action='store_true');ap.add_argument('--config-sha256');main(ap.parse_args())
