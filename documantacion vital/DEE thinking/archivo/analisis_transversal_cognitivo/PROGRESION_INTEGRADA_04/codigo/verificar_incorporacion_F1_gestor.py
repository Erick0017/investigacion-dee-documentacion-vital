"""Verify actual manager modes and all stdlib children; no Native allowed."""
from pathlib import Path
import hashlib,json,os,subprocess
P4=Path(__file__).resolve().parents[1];C=P4.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';CONTROL=P4/'control'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 python=C/'motor/python313/python.exe';manager=C/'sistema/gestionar.py';helper=P4/'codigo/auditar_cli_F1.py'
 protected=[manager,C/'sistema/estado/ACTIVO.json',C/'sistema/estado/vidas/ECI02_PI03_MAIN/VIDA.json',C/'sistema/estado/checkpoints/ECI02_PI03_MAIN.T775355.eab4fdb0c691.deetsnap.gz',C/'sistema/runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl',C/'motor/python313/site-packages/dee_thinking/_native.cp313-win_amd64.pyd',C/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx']
 before={str(p):sha(p)for p in protected};tests=[]
 plans=[('listar_actual',['listar'],False),('recalcular_actual',['recalcular-f1','--destino',str(CONTROL/'F1_GESTOR_REAL_R01')],False),('listar_auditado',['listar'],True),('recalcular_auditado',['recalcular-f1','--destino',str(CONTROL/'F1_GESTOR_AUDITADO_R01')],True)]
 for name,args,audit in plans:
  log=CONTROL/('F1_AUDIT_'+name);env=os.environ.copy()
  if audit:log.mkdir();env['PI04_F1_AUDIT_DIR']=str(log)
  command=[str(python),'-I','-B','-X','utf8',*([str(helper),str(manager)]if audit else[str(manager)]),'reproducibilidad',*args]
  r=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',env=env,timeout=120)
  with (CONTROL/('F1_'+name+'.stdout.json')).open('x',encoding='utf-8')as f:f.write(r.stdout)
  if r.returncode:raise RuntimeError(name+':'+r.stdout+r.stderr)
  value=json.loads(r.stdout)
  if args[0]=='listar':
   tool=next(x for x in value['external_tools']if x['id']=='PI04_F1_OBSERVADOR_COLA_AUDITOR')
   if tool['kind']!='instrumento_externo'or tool['acquisition_attributed_to_MAIN']is not False:raise ValueError('Misattributed listing')
  elif value['checks']['full_RAW_and_clocks_reconstructed_and_SHA_verified']!=47 or value['checks']['global_RAW_pairs_reconstructed_and_compared']!=28:raise ValueError('Wrong calculation')
  audits=[json.loads(p.read_text(encoding='utf-8'))for p in log.glob('*.json')]if audit else[]
  if audit and(any(x['DEE_or_app_modules']or x['blocked_operations']for x in audits)or len(audits)!=(2 if args[0]=='listar'else 3)):raise ValueError('Audit coverage/failure')
  tests.append({'name':name,'command':command,'returncode':r.returncode,'stdout_bytes':len(r.stdout.encode('utf-8')),'stderr_bytes':len(r.stderr.encode('utf-8')),'audited_processes':audits,'result':value if args[0]!='listar'else tool})
 existing=CONTROL/'F1_GESTOR_REAL_R01';files_before={p.name:sha(p)for p in existing.iterdir()}
 cmd=[str(python),'-I','-B','-X','utf8',str(manager),'reproducibilidad','recalcular-f1','--destino',str(existing)]
 bad=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=30)
 if bad.returncode!=2 or files_before!={p.name:sha(p)for p in existing.iterdir()}:raise ValueError('Existing destination not protected')
 after={str(p):sha(p)for p in protected}
 if before!=after:raise ValueError('Protected source changed; reconcile concurrent changes')
 proof={'schema':'PI04.F1.actual_manager_external_tool_verified.v1','tests':tests,'existing_destination_rejected':{'returncode':bad.returncode,'files_unchanged':True,'response':json.loads(bad.stdout)},'protected_before':before,'protected_after':after,'protected_equal':True,'Native_or_MAIN_capacity_claimed':False,'new_Native_ticks':0,'S_gestionar_modified':False,'audited_processes_total':sum(len(x['audited_processes'])for x in tests),'scope':'Actual manager and exact RP/portable sources ran; wrappers preserve target argv and recursively instrument stdlib children, refusing DEE/app imports, SQLite connections and operational-state opens.'}
 path=CONTROL/'F1_GESTOR_INCORPORADO_Y_VERIFICADO.json'
 with path.open('x',encoding='utf-8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
 regpath=RP/'RECURSOS.json';raw=regpath.read_bytes();reg=json.loads(raw);entry=reg['instrument_deltas']['PI04_F1']
 entry['operation_coverage']={'listar':'ACTUAL_MANAGER_AND_AUDITED_ROUTE_VERIFIED','recalcular-f1':'ACTUAL_MANAGER_AND_ALL_CHILDREN_AUDITED;47/47physical_cuts_and28diff','existing_destination':'REJECTED_WITHOUT_OVERWRITE','new_native_ticks':0}
 entry['operational_verification']={'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path)}
 tmp=regpath.with_name('RECURSOS.json.PI04_F1_CLOSE.tmp')
 with tmp.open('x',encoding='utf-8')as f:json.dump(reg,f,ensure_ascii=False,indent=2);f.write('\n')
 if hashlib.sha256(regpath.read_bytes()).hexdigest()!=hashlib.sha256(raw).hexdigest():raise ValueError('Concurrent registry change')
 os.replace(tmp,regpath)
 print(json.dumps({'proof':str(path),'proof_bytes':path.stat().st_size,'proof_sha256':sha(path),'RP_sha256':sha(RP/'reproducir.py'),'registry_final_sha256':sha(regpath),'protected_equal':True,'audit_processes':proof['audited_processes_total'],'new_Native_ticks':0,'existing_destination_rejected':True},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
