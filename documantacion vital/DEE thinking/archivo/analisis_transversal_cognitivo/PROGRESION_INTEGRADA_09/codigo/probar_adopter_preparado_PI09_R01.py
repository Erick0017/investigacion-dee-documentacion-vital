"""Actual bounded code/selector CAS + negative approval tests, no Native."""
from pathlib import Path
import copy,hashlib,importlib.util,json,sys
H=Path(__file__).resolve().parent;OUT=H/'PRUEBA_ADOPTER_PI09_R01'
def main():
 if OUT.exists():raise FileExistsError('Prueba anterior preservada')
 OUT.mkdir();sp=importlib.util.spec_from_file_location('PI09_actual_conditional_adopter',H/'incorporar_PI09_misma_identidad_R02.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 delta=json.loads((H/'DELTA_OPERATIVO_PI09_R01.json').read_text('utf8'));contract=json.loads((H/'PERMISO_OPERATIVO_PI09_R01_PROPUESTO/contratos/PI09_CONSULTA_OPERATIVA_R01.json').read_text('utf8'));d={'new_contract':contract,'approved_code_files':delta['approved_code_files'],'selectors_cas':delta['selectors_cas']};tests=[]
 def check(n,v):
  if v is not True:raise AssertionError(n)
  tests.append({'name':n,'pass':True})
 def rejects(n,fn):
  try:fn()
  except (ValueError,FileNotFoundError):check(n,True);return
  raise AssertionError(n)
 rows=m.code(d);check('actual_complete_current_code_CAS',len(rows)==len(delta['approved_code_files']));m.selector_cas(d);check('actual_six_selector_CAS_read_only',len(d['selectors_cas'])==6)
 bad=copy.deepcopy(d);bad['approved_code_files'][0]['before_sha256']='00'*32;rejects('changed_product_source_CAS_denied',lambda:m.code(bad))
 bad=copy.deepcopy(d);bad['approved_code_files']=[r for r in bad['approved_code_files']if r['file']!='capacidades/pi09_transporte_heredado_R02.py'];rejects('missing_new_identity_transport_denied',lambda:m.code(bad))
 proposal=OUT/'NOT_APPROVED.json';proposal.write_text('{"approved_for_adoption":false}','utf8');rejects('unapproved_proposal_denied_before_material',lambda:m.decision(proposal))
 check('no_DEE_import_or_world',not any(n=='app'or n.startswith(('app.','dee_thinking'))for n in sys.modules))
 result={'schema':'DEE.PI09.conditional_adopter.actual_CAS_pure_tests.R01','passed':len(tests),'tests':tests,'actual_code_and_six_selector_hashes_checked':True,'source_state_read':False,'Native_executed':False,'DEE_imports':0,'product_modified':False,'not_actual_adoption_or_reopen':True}
 file=OUT/'RESULTADO.json';file.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'passed':len(tests),'proof':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'Native_executed':False}))
if __name__=='__main__':main()
