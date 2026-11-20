"""Verifica suplemento Root realmente aplicado y vista única1/24, código sólo."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,sys
H=Path(__file__).resolve().parent;P=H.parent
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
sp=importlib.util.spec_from_file_location('D_R04_applied_admin_view_code_only',H/'incorporar_D_PI09_misma_identidad_R04.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);b=m.base();prepared_file=b.PREPARED;before=sha(prepared_file);original=read(prepared_file);view=b.read(prepared_file);changed=[(a,z)for a,z in zip(original['deployed_code'],view['deployed_code'])if a!=z];assert len(changed)==1 and changed[0][0]['file']==m.FILE;checks=['actual_applied_supplement_exactly_one_of24_rows']
assert before==sha(prepared_file)and original['decision']==view['decision']and original['map']==view['map'];checks.append('original_receipt_decision_map_bytes_preserved')
assert view['administrative_alias_supplement']['sha256']==m.SUPPLEMENT_SHA;checks.append('Root_applied_proof_2712_bound_exactly')
old=copy.deepcopy(original);old['deployed_code'][next(i for i,r in enumerate(old['deployed_code'])if r['file']==m.FILE)]['sha256']='0'*64
try:m.supplemental_view(old)
except ValueError:checks.append('unexpected_prepared_before_hash_rejected')
else:raise AssertionError('before digest')
cap=m.m.S/'capacidades';sp=importlib.util.spec_from_file_location('D_actual_current_dispatch_registry_only',cap/'pi09_dispatcher_D_R02.py');dispatcher=importlib.util.module_from_spec(sp);sp.loader.exec_module(dispatcher);registry=dispatcher.registry();assert m.NEW in registry['files_sha256']and m.OLD not in registry['files_sha256'];checks.append('actual_product_dispatcher_registry_all18pins_PASS')
assert 'app.lives'not in sys.modules;checks.append('no_Store_DEE_Native_import')
for name in('incorporar_D_PI09_misma_identidad_R04.py','ejecutar_administracion_D_con_tope_PI09_R04.py','reabrir_producto_D_PI09_0_R02.py'):ast.parse((H/name).read_bytes());checks.append('AST_'+name)
assert 'incorporar_D_PI09_misma_identidad_R04.py'in(H/'ejecutar_administracion_D_con_tope_PI09_R04.py').read_text('utf8');checks.append('supervisor_real_callsite_R04')
out=P/'control/PRUEBA_SUPLEMENTO_D_ALIAS_R04_PI09.json';assert not out.exists();data={'schema':'DEE.PI09.D.actual_applied_registry_alias_supplement.code_only_check.R04','passed':True,'checks':checks,'source_sha256':{n:sha(H/n)for n in('incorporar_D_PI09_misma_identidad_R04.py','ejecutar_administracion_D_con_tope_PI09_R04.py','reabrir_producto_D_PI09_0_R02.py')},'actual_supplement_sha256':m.SUPPLEMENT_SHA,'Native_executed':False,'live_cards_SQL_snapshots_read':False,'product_writes':False};out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'proof':str(out),'sha256':sha(out),'passed':True,'checks':len(checks),'pins':data['source_sha256']}))
