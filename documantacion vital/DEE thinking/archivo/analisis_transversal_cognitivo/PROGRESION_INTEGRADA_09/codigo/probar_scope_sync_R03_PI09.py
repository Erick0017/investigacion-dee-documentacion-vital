"""Pruebas puras de alcance descriptivo: STATE0 no equivale a material."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
H=Path(__file__).resolve().parent;P=H.parent;p=H/'sincronizar_cierre_actual_PI09_R03.py';sp=importlib.util.spec_from_file_location('sync_scope_pure_no_state',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);life='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01';ref={'path':'TEST_NO_FILE','sha256':'a'*64}
state={'life_id':life,'closed':True,'owner_closed':True,'selected':True,'new_ticks':0,'physical_unchanged':True,'operational_state_valid':True,'pending_reconciled':True,'stock_unchanged':True};value=m.selected_validation(life,state,ref,ref);assert value['selected_material_function_test_pending']is True and value['selected_material_function_test_executed']is False and value['selected_check_scope']=='ACTUAL_SELECTED_STATE0_SAVE_CLOSE_ONLY';checks=['state0_is_not_selected_material']
material={**state,'schema':'DEE.PI09.actual_selected_public_D_EP7.R01','status':'CLOSED_PUBLIC_MATERIAL_AND_REOPEN0','functional_success':True};value=m.selected_validation(life,material,ref,ref);assert value['selected_material_function_test_pending']is False and value['selected_material_function_test_executed']is True;checks.append('only_explicit_material_schema_can_clear_material_pending')
for k in('selected','physical_unchanged','operational_state_valid','pending_reconciled','stock_unchanged'):
 bad={**state,k:False}
 try:m.selected_validation(life,bad,ref,ref)
 except ValueError:checks.append('reject_false_'+k)
 else:raise AssertionError(k)
r=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(p)],capture_output=True,text=True,check=True);assert json.loads(r.stdout)['mode']=='PLAN_ONLY_NO_STATE_READ';checks.append('actual_default_plan_reads_no_state')
out=P/'control/PRUEBA_SCOPE_SYNC_FINAL_PI09_R03.json';assert not out.exists();data={'passed':True,'checks':checks,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'Native_executed':False,'product_writes':False,'live_states_read':False};out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'proof':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_sha256':data['source_sha256'],'checks':len(checks)}))
