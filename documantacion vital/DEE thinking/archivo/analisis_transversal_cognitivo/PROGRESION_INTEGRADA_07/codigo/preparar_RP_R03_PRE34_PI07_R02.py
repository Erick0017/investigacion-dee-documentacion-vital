"""Generate a new Root-only registrar from preserved R01; no Cognitive writes."""
from pathlib import Path
import hashlib
H=Path(__file__).resolve().parent
source=H/'incorporar_RP_R03_PI07_R01.py';target=H/'incorporar_RP_R03_PI07_R02.py'
if target.exists():raise FileExistsError('Prepared revision preserved')
s=source.read_text('utf-8-sig')
s=s.replace('ONE current frozen S7','ONE reconstructed, exact PRE34 S7')
s=s.replace("CAPKEY='PI07_R03_LOCAL_FI_R01'","CAPKEY='PI07_R03_LOCAL_FI_PRE34_R02'")
s=s.replace("RECIPE='pi07_r03_uso_adquirido_post4_R01'","RECIPE='pi07_r03_uso_adquirido_post4_R02'")
begin=s.index('def snapshot_sources():');end=s.index('\ndef build_recipe():',begin)
s=s[:begin]+'''def snapshot_sources():
 applied_file=P/'control/C2C34_PI07_DELTA_APLICADO_R02.json';applied=read(applied_file)
 originals=H/'ORIGINALES_C2C34_PI07_R02';rows={r['file']:r for r in applied['files']}
 added={name for name,row in rows.items()if row['before_sha256']is None}
 expected_added={'capacidades/pi07_c2c_ofertas_R01.py','capacidades/PROTOCOLO_PI07_C2C_34_R01.json','capacidades/PROTOCOLO_PI07_C2C_EXTENSION_R01.json','capacidades/pi07_permiso_principal_R02.py'}
 if added!=expected_added:raise ValueError('Exact failed34delta scope only')
 replaced={name:row['before_sha256']for name,row in rows.items()if row['before_sha256']is not None}
 if set(replaced)!={'app/mundo_genesis_apd05.py','app/cola_local.py','capacidades/pi04_dispatcher.py'}:raise ValueError('Exact3preservedPRE34beforeimages required')
 files=[]
 for parent in(S/'app',S/'capacidades',S/'contratos'):
  files.extend(p for p in parent.rglob('*')if p.is_file()and p.suffix in('.py','.json')and'__pycache__'not in p.parts)
 files+=list(S.glob('*.py'))+list(S.glob('*.json'));result=[]
 for current in sorted(set(files)):
  name=current.relative_to(S).as_posix()
  if name in added:continue
  actual=originals/name if name in replaced else current;regular(actual)
  if name in rows and sha(current)!=rows[name]['sha256']:raise ValueError('Post34source drift: '+name)
  if name in replaced and sha(actual)!=replaced[name]:raise ValueError('Changed actual PRE34beforeimage: '+name)
  result.append({'file':name,'bytes':actual.stat().st_size,'sha256':sha(actual),'source':str(actual)})
 return result

def pre34_validation(files):
 # Invoke the REAL preserved pure-Python validator, not a mocked dependency.
 # Module import and protocol checks use only stdlib and read source files.
 import importlib.util
 actual={r['file']:r for r in files};body=Path(actual['capacidades/pi04_coordinacion_central_C2C.py']['source'])
 spec=importlib.util.spec_from_file_location('PI07_PRE34_contract_check_no_Native',body);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 module.PROTOCOL=S/'capacidades/PROTOCOLO_PI05_C2C_30_R01.json';p,digest=module.protocol(material=True,evaluation=True)
 if len(p['schedule'])!=30:raise ValueError('Actual effective30contract required')
 rejected=None
 try:
  module.PROTOCOL=S/'capacidades/PROTOCOLO_PI07_C2C_34_R01.json';module.protocol(material=True,evaluation=True)
 except ValueError as exc:rejected=str(exc)
 if rejected!='One bounded2..32-opportunity schedule required':raise ValueError('Failed34contract must remain explicitly reproduced by pure validation')
 for name in('app/mundo_genesis_apd05.py','app/cola_local.py','capacidades/pi04_dispatcher.py'):
  text=Path(actual[name]['source']).read_text('utf-8-sig');ast.parse(text)
  if 'pi07_c2c_ofertas_R01'in text or'pi07_permiso_principal_R02'in text:raise ValueError('34failedhooks remain in PRE34source')
 return {'Native_imported_or_executed':False,'actual_C2C_protocol30_validator_passed':True,'effective_protocol_sha256':digest,'schedule_length':30,'failed_protocol34_validator_preserved':rejected,'restored_exact_beforeimage_files':3,'excluded_failed34_files':4,'scope':'Pure real contract/source validation; not a new material frontdoor replay or general proof of all dependency/state readiness.'}
''' +s[end:]
s=s.replace('recipe=build_recipe();files=snapshot_sources();source_manifest=', 'recipe=build_recipe();files=snapshot_sources();pre34=pre34_validation(files);source_manifest=')
s=s.replace("'product_modified':False,'CLI_replay_already_executed':False", "'product_modified':False,'CLI_replay_already_executed':False,'PRE34_contract_validation':pre34")
s=s.replace("'source_system':str(S),'source_closed_proof'", "'source_system':str(S),'reconstruction':'Exact PRE34 sources restored from 3 recorded beforeimages; 4 failed34-only files excluded. No S7state/source modified.','PRE34_contract_validation':pre34,'source_closed_proof'")
s=s.replace('One exact current enclosing source capsule;', 'One exact reconstructed PRE34 enclosing source capsule;')
s=s.replace('RP_R03_INCORPORADA_PI07_R01.json','RP_R03_INCORPORADA_PI07_R02.json')
s=s.replace('RP_R03_DOCUMENTAL_STAGE_R01','RP_R03_DOCUMENTAL_STAGE_R02')
s=s.replace('RP_RECURSOS_ANTES_R03_PI07_R01.json','RP_RECURSOS_ANTES_R03_PI07_R02.json')
s=s.replace("'closed_source_proof':{'path':str(closefile),'sha256':sha(closefile)},'source_native_reference_executed'", "'closed_source_proof':{'path':str(closefile),'sha256':sha(closefile)},'PRE34_contract_validation':pre34,'source_native_reference_executed'")
compile(s,str(target),'exec');target.write_text(s,encoding='utf8')
print(str(target));print(hashlib.sha256(target.read_bytes()).hexdigest())
