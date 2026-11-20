"""Pure AST/source-hash checks on the prepared rebase, no Source writes."""
from pathlib import Path
import ast,hashlib,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';FI=H/'FUENTES_ACCESO_FI_PI07_R01';D=H/'FUENTES_C2C34_PI07_R02';OLD=H/'FUENTES_C2C34_PI07_R01';S=P/'estados/candidato/sistema'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 tests=[]
 def check(n,v):
  if not v:raise AssertionError(n)
  tests.append({'name':n,'passed':True})
 plan=json.loads((P/'control/C2C34_PI07_DELTA_CONDICIONAL_R02.json').read_text('utf8'))
 for row in plan['files']:
  check('qualified_member_'+row['file'],sha(D/row['file'])==row['sha256'])
  if row['before_sha256']is not None:
   original=FI/row['file']if row['file'].startswith('app/')else S/row['file']
   check('CAS_uses_exact_future_FI_'+row['file'],sha(original)==row['before_sha256'])
 class RemoveNewSupply(ast.NodeTransformer):
  def visit_If(self,node):
   if 'eci01-pi07-c2c-ampliar'in ast.dump(node.test):return None
   return self.generic_visit(node)
 for name in('app/mundo_genesis_apd05.py','app/cola_local.py'):
  before=ast.parse((FI/name).read_bytes());after=RemoveNewSupply().visit(ast.parse((D/name).read_bytes()))
  check('only_C2C34_hook_added_to_FI_'+name,ast.dump(before,include_attributes=False)==ast.dump(after,include_attributes=False))
 for name in('pi07_c2c_ofertas_R01.py','PROTOCOLO_PI07_C2C_34_R01.json','PROTOCOLO_PI07_C2C_EXTENSION_R01.json','pi07_permiso_principal_R02.py','pi04_dispatcher.py'):
  check('R01_supply_body_unchanged_'+name,sha(D/'capacidades'/name)==sha(OLD/'capacidades'/name))
 for name in('pi07_acceso_FI_regulado_R01.py','PROTOCOLO_PI07_ACCESO_FI_R01.json','acceso_integrado_eci01.py'):
  check('new_FI_source_pinned_'+name,plan['preserved']['capacidades/'+name]==sha(FI/'capacidades'/name))
 out=P/'control/C2C34_REBASE_FI_PI07_PRUEBAS_PURAS_R01.json'
 with out.open('x',encoding='utf8')as f:json.dump({'schema':'DEE.PI07.C2C34.FI_rebase.pure_checks.v1','tests':tests,'passed':len(tests),'Native_executed':False,'S7_or_product_modified':False,'plan_sha256':sha(P/'control/C2C34_PI07_DELTA_CONDICIONAL_R02.json'),'installer_sha256':sha(H/'preparar_C2C34_PI07_R02.py'),'scope':'Source members, anticipated exact FI CAS and full AST equality after removing ONLY new supply routing branches. No supply, Native use, adoption or actual Source application.'},f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(out),'sha256':sha(out),'passed':len(tests),'Native_executed':False}))
if __name__=='__main__':main()
