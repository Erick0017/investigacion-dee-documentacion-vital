"""Prepare the explicit PREPARED-profile staging path before product reopen0.
Original conditional R01 remains literal. No Source/product/Native action.
"""
from pathlib import Path
import ast,hashlib
H=Path(__file__).resolve().parent;source=H/'incorporar_PI08_misma_identidad_R01.py';target=H/'incorporar_PI08_misma_identidad_R02.py'
if target.exists():raise FileExistsError('Prepared adopter revision preserved')
s=source.read_text('utf8')
old="  if rel.parts[0]not in('app','capacidades')or(target.suffix=='.json'and not target.name.startswith('PROTOCOLO')):raise ValueError('No engine/state/selector payloads in source delta')"
new="""  prepared_profile=rel.as_posix()=='contratos/PI08_USO_OPERATIVO_R01.json'
  if prepared_profile:
   profile=read(source)
   if profile.get('schema')!='DEE.PI08.exact_operational_profile.v1'or profile.get('status')!='PREPARED_DIAGNOSTIC'or profile.get('life_id')!=LIFE or profile.get('adoption_decision_sha256')is not None:raise ValueError('Only exact unselected PREPARED profile may be staged before promotion')
   expected_profile=dict(d['new_contract'])
   if profile!=expected_profile:raise ValueError('Prepared profile must equal the final decision template before COMMITTED fields are added')
  elif rel.parts[0]not in('app','capacidades')or(target.suffix=='.json'and not target.name.startswith('PROTOCOLO')):raise ValueError('No engine/state/selector payloads in source delta')"""
if old not in s:raise ValueError('Exact code-path allowlist baseline changed')
s=s.replace(old,new)
old="  rows.append({**item,'source':str(source),'target':str(target),'bytes':source.stat().st_size})"
new="  rows.append({**item,'source':str(source),'target':str(target),'bytes':source.stat().st_size,'deployment_role':'PREPARED_DIAGNOSTIC_PROFILE_NOT_COMMITTED'if prepared_profile else'CODE_OR_IMMUTABLE_PROTOCOL'})"
if old not in s:raise ValueError('Exact source row baseline changed')
s=s.replace(old,new)
old=" if 'app/usar_dee.py'not in seen or 'app/pi08_identidad_c2c_R01.py'not in seen:raise ValueError('Explicit reviewed launcher and same-ID administrative adapter required')"
new=old+"\n if 'contratos/PI08_USO_OPERATIVO_R01.json'not in seen:raise ValueError('Explicit prepared permission profile required before unselected product reopening')"
if old not in s:raise ValueError('Exact required-interface baseline changed')
s=s.replace(old,new)
s=s.replace("'deployed_code':rows,'administrative_mapping'","'deployed_code':rows,'prepared_permission_profile':info(S/'contratos/PI08_USO_OPERATIVO_R01.json'),'public_FI_material_before_promotion':False,'administrative_mapping'")
ast.parse(s);target.write_text(s,encoding='utf8');print(str(target));print(hashlib.sha256(target.read_bytes()).hexdigest())
