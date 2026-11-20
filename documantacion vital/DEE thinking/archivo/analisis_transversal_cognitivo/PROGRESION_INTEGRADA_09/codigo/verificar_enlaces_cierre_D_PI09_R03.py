"""Comprobaciones administrativas finales nuevas, sin estados ni Native."""
from pathlib import Path
import ast,hashlib,importlib.util,json,subprocess,sys
H=Path(__file__).resolve().parent;P=H.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
checks=[]
sp=importlib.util.spec_from_file_location('D_final_snapshot_output_binding',H/'incorporar_D_PI09_misma_identidad_R02.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
m.m.decision=lambda file:{'protected_parent_snapshot_sha256':'a'*64};m.decision(None);assert m.base().PARENT_SHA=='a'*64;checks.append('dynamic_protected_parent_SHA_in_actual_move_receipt_namespace')
for name,args in(('construir_decision_D_PI09_R01.py',['--help']),('preparar_referencias_D_PI09_R01.py',['--help']),('usar_principal_D_EP7_PI09_R01.py',[]),('usar_principal_NATIVE_EP12_PI09_R01.py',[])):
 r=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(H/name),*args],capture_output=True,text=True,check=True)
 if not args:assert json.loads(r.stdout)['mode']=='PLAN_ONLY_NO_STATE_OR_NATIVE'
 checks.append('actual_safe_CLI_'+name)
admin=(H/'ejecutar_administracion_D_con_tope_PI09_R02.py').read_text('utf8');assert 'incorporar_D_PI09_misma_identidad_R02.py'in admin and '512*1024*1024'in admin;ast.parse(admin);checks.append('admin_R02_points_to_Source0_guard_with_512MiB')
for name,mode,before,after in(('usar_principal_D_EP7_PI09_R01.py','eci01-pi09-d-episodio',7,8),('usar_principal_NATIVE_EP12_PI09_R01.py','eci01-pi09-episodio',12,13)):
 t=(H/name).read_text('utf8');ast.parse(t);assert f"'modo':'{mode}'"in t and f"'ordinal_before':{before},'ordinal_after':{after}"in t and "'--retorno','real'"in t and "'REOPEN0'"not in t and "'_REOPEN0'"in t;checks.append('fixed_public_material_then_reopen0_'+name)
out=P/'control/VERIFICACION_ENLACES_CIERRE_D_PI09_R03.json';assert not out.exists();names=('incorporar_D_PI09_misma_identidad_R02.py','construir_decision_D_PI09_R01.py','preparar_referencias_D_PI09_R01.py','ejecutar_administracion_D_con_tope_PI09_R02.py','usar_principal_D_EP7_PI09_R01.py','usar_principal_NATIVE_EP12_PI09_R01.py')
result={'schema':'DEE.PI09.D.final_admin_and_public_CLI.pure_checks.R03','passed':True,'checks':checks,'previous_source0_24checks':{'path':str(P/'control/PRUEBA_CIERRE_PREPARADO_D_PI09_R02.json'),'sha256':sha(P/'control/PRUEBA_CIERRE_PREPARADO_D_PI09_R02.json')},'actual_Native_execution':False,'Native_imports':False,'live_card_or_SQL_reads':False,'product_writes':False,'current_code_sha256':{n:sha(H/n)for n in names}}
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'proof':str(out),'sha256':sha(out),'passed':True,'checks':len(checks)}))
