"""Conditional D product code proposal, never applies or reads a live state.

Reuse the current product UI/native public route, add exact D branch routing,
and keep the original Native R02 scope/registry. Source Discovery's full code
manifest is checked; all byte differences are explicit reviewed code rows.
"""
from pathlib import Path
import argparse,ast,copy,hashlib,json,shutil
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';SOURCE=P/'estados/DISCOVERY/sistema'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def once(t,a,b):need(t.count(a)==1,'Exact operational merge anchor changed '+a[:100]);return t.replace(a,b)
def patch_world(text):
 need('pi09_permiso_operativo_D_R01'not in text,'Prior D merge preserved')
 anchor='        pi09_permission.install()  # Dormant exact COMMITTED permission; no Native policy.'
 text=once(text,anchor,anchor+'\n        from capacidades import pi09_permiso_operativo_D_R01 as d_permission\n        d_permission.install()  # Exact PREPARED/COMMITTED Discovery; old Native remains available.')
 lines=[];transports=dispatchers=0
 for line in text.splitlines():
  lines.append(line);indent=line[:len(line)-len(line.lstrip())]
  if line.strip()=='from capacidades import pi09_transporte_heredado_R02 as pi09_transport':
   transports+=1;lines.extend((indent+'from capacidades import pi09_transporte_D_R02 as d_transport',indent+'if d_transport.applies(self.a):pi09_transport=d_transport'))
  if line.strip()=='from capacidades import pi09_dispatcher_R02 as pi09':
   dispatchers+=1;lines.extend((indent+'from capacidades import pi09_transporte_D_R02 as d_transport',indent+'if d_transport.applies(self.a):',indent+'    from capacidades import pi09_dispatcher_D_R02 as pi09'))
 need(transports==10 and dispatchers==5,'Exact ten ancestry and five dispatcher hooks required');text='\n'.join(lines)+'\n'
 validate="""        from capacidades import pi09_permiso_operativo_D_R01 as d_permission
        d_permission.validate_external(self.a,row,payload=payload)
        if d_permission.routes_public(self.a,row):
            d_permission.validate_public(self.a,row)
            return
"""
 execute="""        from capacidades import pi09_permiso_operativo_D_R01 as d_permission
        d_permission.validate_external(self.a,row,payload=payload)
        if d_permission.routes_public(self.a,row):
            self.before_mutation('PI09_D_EXACT_COMMITTED_OUTER_FI8_ACCESS')
            value=d_permission.execute_public(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)
            return {'version':d_permission.VERSION,'rows':[value]}
"""
 text=once(text,'    def validate(self,payload):\n        row=self._eci01_row(payload)','    def validate(self,payload):\n        row=self._eci01_row(payload)\n'+validate.rstrip('\n'))
 text=once(text,'    def execute(self,payload):\n        row=self._eci01_row(payload)','    def execute(self,payload):\n        row=self._eci01_row(payload)\n'+execute.rstrip('\n'))
 anchor='        return result\n\n    def validate(self,payload):'
 text=once(text,anchor,"        for path in d_permission.code_files():\n            self.code_sha256['PI09_D/public/'+path.name]=hashlib.sha256(path.read_bytes()).hexdigest()\n"+anchor)
 ast.parse(text);return text
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source-system',type=Path,default=SOURCE);ap.add_argument('--destino',type=Path,required=True);ap.add_argument('--contract',type=Path);a=ap.parse_args();source=a.source_system.resolve(strict=True);out=a.destino.resolve();need(source==SOURCE.resolve()and out.is_relative_to(H.resolve())and not out.exists(),'Only exact Discovery source and fresh code-only proposal under H')
 mf=source.parent/'SISTEMA_CODIGO_PI09.json';m=read(mf);need(m.get('D_permissions_resolved')is True,'Actual declared D source closure required; do not prepare from a partial installation')
 files={r['file']:r for r in m['files']}
 for row in m['files']:need(sha(source/row['file'])==row['sha256'],'Source code/config differs from declared closure '+row['file'])
 need((source/'capacidades/PI09_TRANSPORTE_D_R02.json').is_file()and read(source/'capacidades/PI09_TRANSPORTE_D_R02.json')['role']=='real','Only the exact real Discovery D source')
 out.mkdir();cap=out/'codigo';overrides={};world=(S/'app/mundo_genesis_apd05.py').read_text('utf-8-sig');overrides['app/mundo_genesis_apd05.py']=patch_world(world).encode('utf8')
 queue=(S/'app/cola_local.py').read_text('utf-8-sig');anchor='from capacidades.pi09_dispatcher_R02 import validate_literal';need(queue.count(anchor)==1,'Current Native queue hook changed');queue=queue.replace(anchor,'from capacidades.pi09_literal_producto_D_R01 import validate_literal');ast.parse(queue);overrides['app/cola_local.py']=queue.encode('utf8')
 dispatcher=(S/'capacidades/pi04_dispatcher.py').read_text('utf-8-sig');needle="return _load('pi09_permiso_operativo_R01').configure_C2C("
 lines=dispatcher.splitlines();count=0
 for i,line in enumerate(lines):
  if needle in line:
   prefix,expression=line.split('return ',1);lines[i]=prefix+"return _load('pi09_permiso_operativo_D_R01').configure_C2C("+expression+',a)';count+=1
 need(count==2,'Current two Native C2C permissions required');dispatcher='\n'.join(lines)+'\n';ast.parse(dispatcher);overrides['capacidades/pi04_dispatcher.py']=dispatcher.encode('utf8')
 # Keep Native global transport/registry and UI; D uses a separate ancestor
 # scope only in its private Python transport, installed by the new profile.
 for name in('capacidades/PI09_TRANSPORTE_HEREDADO_R02.json','capacidades/PI09_PLUGINS_R02.json','capacidades/pi09_dispatcher_R02.py','app/usar_dee.py'):
  overrides[name]=(S/name).read_bytes()
 overrides['capacidades/PI09_TRANSPORTE_D_ANCESTRO_R02.json']=(source/'capacidades/PI09_TRANSPORTE_HEREDADO_R02.json').read_bytes()
 for name in('pi09_permiso_operativo_D_R01.py','pi09_literal_producto_D_R01.py'):overrides['capacidades/'+name]=(H/name).read_bytes()
 leaf=(H/'PERMISO_OPERATIVO_PI09_R01_PROPUESTO/app/pi09_identidad_c2c_R01.py').read_text('utf-8-sig');leaf=leaf.replace("LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01'","LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'");leaf=once(leaf,"metadata.get('life_id')not in(OLD,LIFE)","metadata.get('life_id')not in(OLD,'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01',LIFE)");ast.parse(leaf);overrides['app/pi09_identidad_c2c_D_R01.py']=leaf.encode('utf8')
 permission=__import__('importlib.util',fromlist=['util']);spec=permission.spec_from_file_location('D_profile_template_only',H/'pi09_permiso_operativo_D_R01.py');module=permission.module_from_spec(spec);spec.loader.exec_module(module)
 contract={'schema':'DEE.PI09.D.exact_operational_permission.v2','status':'PREPARED_DIAGNOSTIC','life_id':module.LIFE,'profile':'fisica_directa','protocol_sha256':module.PINS['PROTOCOLO_PI09_D_R02.json'],'allowed_modes':[module.D_EP,module.D_STATE],'all_outer_FI_requests':True,'public_FI_domain':[0,20],'public_FI_backend':'explicit_FI8_same_frozen_body','internal_C2C_FI_redirected':False,'C2C_protocol_sha256':module.C2C_PROTOCOL,'frozen_files_sha256':module.PINS,'public_arithmetic_policy':'legacy_partial','historical_R02_material_disabled':True,'historical_PI07_material_disabled':True,'all_adoption_gates_met':False,'adoption_decision_sha256':None,'prepared_is_not_approval':True}
 if a.contract:
  actual=read(a.contract);need({k:v for k,v in actual.items()if k not in('all_adoption_gates_met','prepared_is_not_approval')}=={k:v for k,v in contract.items()if k not in('all_adoption_gates_met','prepared_is_not_approval')}and actual.get('all_adoption_gates_met')is True,'Root-approved exact final contract only');contract=actual
 overrides['contratos/PI09_D_USO_OPERATIVO_R02.json']=(json.dumps(contract,ensure_ascii=False,indent=2)+'\n').encode('utf8')
 # Explicit source closure, plus product-preserving administrative overrides.
 rows=[];names=set(files)|set(overrides)
 for name in sorted(names):
  data=overrides.get(name,(source/name).read_bytes()if name in files else b'');target=S/name
  if name not in overrides and target.is_file()and sha(target)==files[name]['sha256']:continue
  file=cap/name;file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(data);ast.parse(data)if file.suffix=='.py'else read(file)
  rows.append({'file':name,'source':str(file),'sha256':sha(file),'bytes':len(data),'before_sha256':sha(target)if target.exists()else None,'kind':'administrative_override'if name in overrides else'literal_D_source_closure'})
 plan={'schema':'DEE.PI09.D.operational_delta.conditional_CAS_plan.R01','Native_executed':False,'product_writes':False,'source_code_manifest':{'path':str(mf),'sha256':sha(mf)},'approved_code_files':rows,'new_contract':contract,'scientific_D_R02_C_B_bodies_preserved':True,'Native_global_scope_and_UI_preserved':True,'D_private_ancestor_scope_separate':True,'Root_approval_and_six_actual_gates_required':True,'first_milestone_kept_selected_until_actual_promote':True}
 (out/'PLAN.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'plan':str(out/'PLAN.json'),'sha256':sha(out/'PLAN.json'),'files':len(rows),'Root_approved':contract['all_adoption_gates_met'],'Native_executed':False}))
if __name__=='__main__':main()
