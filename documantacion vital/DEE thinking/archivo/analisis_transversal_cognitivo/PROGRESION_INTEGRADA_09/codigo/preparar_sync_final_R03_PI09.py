"""R03 distingue disponibilidad STATE0 de una prueba material seleccionada."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=H/'sincronizar_cierre_actual_PI09_R02.py';target=H/'sincronizar_cierre_actual_PI09_R03.py'
if target.exists():raise FileExistsError('R03 anterior conservada')
text=source.read_text('utf8');anchor='def prepare(a):'
function="""def selected_validation(life,use,use_ref,source_ref=None):
 material=use.get('material_public_use_executed')is True or(use.get('schema')in('DEE.PI09.actual_selected_public_D_EP7.R01','DEE.PI09.actual_selected_public_NATIVE_EP12.R01')and use.get('status')=='CLOSED_PUBLIC_MATERIAL_AND_REOPEN0')
 need(use.get('life_id')==life and(use.get('closed')is True or use.get('owner_closed')is True),'Prueba seleccionada cerrada y de la misma vida requerida')
 if not material:need(use.get('selected')is True and use.get('new_ticks')==0 and use.get('physical_unchanged')is True,'Sólo STATE0 seleccionada con igualdad física se describe como disponibilidad operativa')
 return {'selected_material_function_test_pending':not material,'selected_material_function_test_executed':material,'selected_material_function_success':use.get('functional_success')if material else None,'selected_check_scope':'ACTUAL_SELECTED_MATERIAL_AND_REOPEN0'if material else'ACTUAL_SELECTED_STATE0_SAVE_CLOSE_ONLY','selected_check':use_ref,'last_actual_source_function':source_ref,'source_function_is_not_a_post_COMMITTED_material_test':True,'same_body_and_whole_Native_equivalence_are_separate_validated_evidence':True}

"""
assert text.count(anchor)==1;text=text.replace(anchor,function+anchor)
old=" if a.use_proof:\n  use=a.use_proof.resolve(strict=True);need(use.is_relative_to(P.resolve()),'Actual selected use proof under P9');u=read(use);need(u.get('life_id')==life and(u.get('closed')is True or u.get('owner_closed')is True),'Actual selected use must be closed and correctly bound');project['latest_selected_use']=ref(use);continuity['latest_operational_use']=ref(use);principal['latest_actual_selected_use']=ref(use);project['selected_operational_use_pending']=False"
new=""" source_ref=None
 if a.source_function_proof:
  source=a.source_function_proof.resolve(strict=True);need(source.is_relative_to(P.resolve()),'Función Source bajo P9');proof=read(source);need(proof.get('life_id')==life and proof.get('closed')is True and proof.get('error')is None,'Última función Source cerrada de la misma vida');source_ref=ref(source)
 if a.use_proof:
  use=a.use_proof.resolve(strict=True);need(use.is_relative_to(P.resolve()),'Actual selected use proof under P9');u=read(use);validation=selected_validation(life,u,ref(use),source_ref)
  if life.endswith('DISCOVERY_01')and validation['selected_material_function_test_pending']:need(source_ref is not None,'STATE0 D exige referencia separada a la última función Source real')
  project['latest_selected_use']=ref(use);continuity['latest_operational_use']=ref(use);principal['latest_actual_selected_use']=ref(use);project['selected_operational_use_pending']=False
  info['operational_validation_scope']=validation
  for value in(project,continuity,principal):value.update(selected_material_function_test_pending=validation['selected_material_function_test_pending'],selected_material_function_test_executed=validation['selected_material_function_test_executed'],PI09_selected_validation_scope=validation)
 else:
  for value in(project,continuity,principal):value['selected_material_function_test_pending']=True
"""
assert text.count(old)==1;text=text.replace(old,new)
text=text.replace("ap.add_argument('--use-proof',type=Path);","ap.add_argument('--use-proof',type=Path);ap.add_argument('--source-function-proof',type=Path);").replace('CAS_plan.R02','CAS_plan.R03').replace('applied.R02','applied.R03').replace('SINCRONIZACION_FINAL_ACTUAL_PI09_R02.json','SINCRONIZACION_FINAL_ACTUAL_PI09_R03.json').replace('SINCRONIZACION_FINAL_PI09_R02','SINCRONIZACION_FINAL_PI09_R03')
ast.parse(text);target.write_text(text,'utf8');print(json.dumps({'file':str(target),'sha256':sha(target),'product_writes':False,'Native_executed':False,'R02_preserved':sha(source)}))
