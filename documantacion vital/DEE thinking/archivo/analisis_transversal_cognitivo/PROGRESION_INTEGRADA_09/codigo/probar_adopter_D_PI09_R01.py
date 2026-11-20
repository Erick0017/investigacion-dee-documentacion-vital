"""Pure administrative reuse/evidence fences, no state or DEE import."""
from pathlib import Path
import copy,hashlib,importlib.util,json
H=Path(__file__).resolve().parent;OUT=H/'PRUEBA_ADOPTER_D_PI09_R01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if OUT.exists():raise FileExistsError('Prior test preserved')
 OUT.mkdir();file=H/'incorporar_D_PI09_misma_identidad_R01.py';spec=importlib.util.spec_from_file_location('D_adopter_pure',file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);b=m.base();checks=[]
 assert b.LIFE==m.LIFE and b.PARENT==m.PARENT and b.CS==m.CS and b.PARENT_T==903603;checks.append('exact_same_Discovery_target_and_quiet_Native_parent')
 assert b.parent is m.parent and b.decision is m.decision and b.code is m.code and b.native_equal is m.native_equal;checks.append('all_material_administrative_entry_functions_use_D_fences')
 assert b.prepare.__globals__['LIFE']==m.LIFE and b.adopt.__globals__['LIFE']==m.LIFE and b.prepare.__globals__['ADOPTED']==b.ADOPTED;checks.append('actual_reused_move_and_promote_functions_resolve_D_namespace')
 assert b.ADOPTED.name=='ADOPCION_D_PRODUCTO_PI09.json'and b.PREPARED.name=='PREPARACION_TRASLADO_D_PRODUCTO_PI09.json';checks.append('C1_actual_receipts_are_never_overwritten')
 assert b.adopt.__code__.co_filename.endswith(':D_admin_identity_and_paths_only')and sha(m.BASE)==m.BASE_SHA;checks.append('reviewed_whole_move_engine_literal_source_pinned')
 p=OUT/'UNAPPROVED_FAKE.json';p.write_text(json.dumps({'approved_for_adoption':False})+'\n','utf8')
 try:m.decision(p);raise AssertionError('Unapproved accepted')
 except ValueError:checks.append('unapproved_decision_rejected_before_any_state_or_gate_read')
 source={'physical':{'N':67,'tick':1,'RAW_sha256':'A','clocks_sha256':'B'},'causal_prefix_sha256':'same','metadata':{'DEE.Cognitive.PI09.persistent_environment.D.R02':'{"ordinal":7}','DEE.Cognitive.PI09.selective_registered_consultation.R02':'{"ordinal":12}','DEE.Cognitive.PI04.C2C.coordination.R01':json.dumps({'life_id':m.ANCESTOR,'ordinal':31,'rows':[1,2],'device':'literal'})}}
 target=copy.deepcopy(source);target['metadata']['DEE.Cognitive.PI04.C2C.coordination.R01']=json.dumps({'life_id':m.LIFE,'ordinal':31,'rows':[1,2],'device':'literal'});assert m.native_equal(source,target)['complete_Native_prefix_equal'];checks.append('single_C2C_administrative_leaf_allowed_no_rows_or_device_change')
 for key in('DEE.Cognitive.PI09.persistent_environment.D.R02','DEE.Cognitive.PI09.selective_registered_consultation.R02'):
  bad=copy.deepcopy(target);bad['metadata'][key]='{"ordinal":0}'
  try:m.native_equal(source,bad);raise AssertionError('History reset accepted')
  except ValueError:checks.append('historical_or_D_counter_reset_rejected_'+key)
 bad=copy.deepcopy(target);bad['physical']['tick']=2
 try:m.native_equal(source,bad);raise AssertionError('Native tick changed')
 except ValueError:checks.append('zero_advance_native_equality_not_weakened')
 result={'schema':'DEE.PI09.D.same_identity_adopter.pure_tests.R01','passed':len(checks),'checks':checks,'Native_executed':False,'DEE_imports':0,'real_card_SQLite_or_snapshot_read':False,'conditional_actual_six_gates_and_Root_decision_still_required':True,'source_sha256':sha(file),'literal_reused_engine_sha256':m.BASE_SHA};proof=OUT/'RESULTADO.json';proof.write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps({'passed':len(checks),'proof':str(proof),'sha256':sha(proof),'Native_executed':False}))
if __name__=='__main__':main()
