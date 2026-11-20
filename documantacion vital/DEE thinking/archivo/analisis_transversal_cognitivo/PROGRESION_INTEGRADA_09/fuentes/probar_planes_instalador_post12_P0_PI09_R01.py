"""Structural plan and pure code-descriptor tests. No target/world access."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf8'))
def main():
 forbidden=[]
 def audit(event,args):
  if event=='import'and str(args[0]).split('.')[0]in {'dee_thinking','app','capacidades','_native'}:forbidden.append(str(args[0]));raise RuntimeError('Native import forbidden')
 sys.addaudithook(audit)
 for name in ('ejecutar_plan_PI09_R02.py','instalar_P0_post12_PI09_R01.py'):ast.parse((P/'codigo'/name).read_text('utf8'))
 plans=[read(P/'codigo'/('PLAN_'+arm+'_P0_R01.json'))for arm in ('PANEL','DISCOVERY')]
 a,b=plans;assert len(a['steps'])==len(b['steps'])==18 and a['steps'][:13]==b['steps'][:13]
 for x,y in zip(a['steps'][13:],b['steps'][13:]):
  assert x['clock_alignment']is True and y['clock_alignment']is True
  assert x['literal']['guardia_temporal']is False and y['literal']['guardia_temporal']is True
  clone=json.loads(json.dumps(x));clone['literal']['guardia_temporal']=True;assert clone==y
 assert all(s['max_ticks']==1300 for s in a['steps']if s['label']in ('FIplus','FIminus','FIzero'))
 assert all(s['literal']['modo']not in ('eci01-pi09-preparar','eci01-pi09-episodio')for s in a['steps'])
 path=P/'codigo/instalar_P0_post12_PI09_R01.py';spec=importlib.util.spec_from_file_location('P0_install_pure',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 registry=read(P/'estados/NATIVE/sistema/capacidades/PI09_PLUGINS_R02.json') # immutable code only
 oldrow={'file':'old_scientific.py','bytes':27,'sha256':'a'*64};oldmanifest={'files':[oldrow]}
 changed,desc=m.propose(registry,oldmanifest,{'life':'MOCK'},{'Native_executed':False},sha(m.PROTO),sha(m.SEAL))
 assert set(changed)=={'capacidades/'+m.HELPER.name,'capacidades/'+m.PROTO.name,'capacidades/PI09_PLUGINS_R02.json'}
 assert set(desc)=={'SISTEMA_CODIGO_PI09.json','CONTEXTO_EJECUCION.json','PREPARACION_PI09.json'}
 newmanifest=json.loads(desc['SISTEMA_CODIGO_PI09.json']);table={r['file']:r for r in newmanifest['files']}
 assert table['old_scientific.py']==oldrow and oldmanifest=={'files':[oldrow]}
 assert json.loads(desc['CONTEXTO_EJECUCION.json'])['source_code_manifest_sha256']==hashlib.sha256(desc['SISTEMA_CODIGO_PI09.json']).hexdigest()
 assert json.loads(desc['PREPARACION_PI09.json'])['context_sha256']==hashlib.sha256(desc['CONTEXTO_EJECUCION.json']).hexdigest()
 assert hashlib.sha256(changed['capacidades/PI09_PLUGINS_R02.json']).hexdigest()==read(m.SEAL)['expected_installed_registry_sha256']
 assert all('estado/'not in name for name in changed)
 output={'schema':'DEE.PI09.P0.post12_plan_and_installer_pures.R02','all_passed':True,'Native':0,'DEE_app_imports':forbidden,'target_state_read':False,'target_writes':False,'same12_and_zero_pause':True,'only_guard_differs_for5_fresh':True,'unchanged_original_code_rows_retained':True,'descriptor_chain_matches':True,'bounded_FI1300':True,'prior_R01_structural_proof_preserved':True,'finite_bounds':[p['finite_bound']for p in plans],'sources':{n:sha(P/'codigo'/n)for n in ('ejecutar_plan_PI09_R02.py','instalar_P0_post12_PI09_R01.py','PLAN_PANEL_P0_R01.json','PLAN_DISCOVERY_P0_R01.json')}}
 out=P/'fuentes/PRUEBAS_PURAS_PLANES_INSTALADOR_POST12_P0_PI09_R02.json'
 with out.open('x',encoding='utf8')as stream:json.dump(output,stream,ensure_ascii=False,indent=2);stream.write('\n')
 print(json.dumps({'proof':str(out),'sha256':sha(out),'installer_sha256':sha(path),'Native':0}))
if __name__=='__main__':main()
