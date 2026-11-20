"""Revisión administrativa D: schema del perfil separado PREPARED→COMMITTED."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,text):
 p=H/name
 if p.exists():raise FileExistsError('Revisión anterior conservada')
 ast.parse(text);p.write_text(text,'utf8');return {'file':name,'sha256':sha(p)}
source=H/'incorporar_D_PI09_misma_identidad_R02.py';text=source.read_text('utf8')
old=' b=m.base();b.validate_PI09_evidence=validate;b.decision=decision;return b'
new=""" b=m.base()
 if not getattr(b,'D_separate_profile_schema_R03',False):
  original=b.adopt;before=original.__code__;old='DEE.PI09.exact_native_consultation_permission.v1';new='DEE.PI09.D.exact_operational_permission.v2'
  need(sum(type(v)is str and v==old for v in before.co_consts)==1,'Se exige una única constante de schema C1 en la copia administrativa')
  constants=tuple(new if type(v)is str and v==old else v for v in before.co_consts);original.__code__=before.replace(co_consts=constants)
  need(original.__code__.co_code==before.co_code and original.__code__.co_names==before.co_names,'Sólo cambia el schema del perfil administrativo D')
  def adopt(d,file,reopening,process):
   # Este control ocurre antes de entrar al método que podría llamar Store.promote.
   profile=b.read(b.S/'contratos/PI09_D_USO_OPERATIVO_R02.json')
   need(profile==d['new_contract']and profile.get('schema')==new and profile.get('status')=='PREPARED_DIAGNOSTIC','Antes de Store sólo el perfil D PREPARED exacto revisado')
   return original(d,file,reopening,process)
  b.adopt=adopt;b.D_separate_profile_schema_R03=True;b.D_original_adopt_with_D_schema_R03=original
 b.validate_PI09_evidence=validate;b.decision=decision;return b"""
if text.count(old)!=1:raise ValueError('Ancla R02 cambió')
text=text.replace(old,new);rows=[save('incorporar_D_PI09_misma_identidad_R03.py',text)]
source=H/'construir_decision_D_PI09_R01.py';text=source.read_text('utf8').replace('incorporar_D_PI09_misma_identidad_R02.py','incorporar_D_PI09_misma_identidad_R03.py');rows.append(save('construir_decision_D_PI09_R02.py',text))
source=H/'ejecutar_administracion_D_con_tope_PI09_R02.py';text=source.read_text('utf8').replace('incorporar_D_PI09_misma_identidad_R02.py','incorporar_D_PI09_misma_identidad_R03.py').replace('_512M_PI09_R02.json','_512M_PI09_R03.json').replace('DEE.PI09.D.owned_admin512.R02','DEE.PI09.D.owned_admin512.R03');rows.append(save('ejecutar_administracion_D_con_tope_PI09_R03.py',text))
print(json.dumps({'files':rows,'Native_executed':False,'product_writes':False,'R01_R02_sources_preserved':True}))
