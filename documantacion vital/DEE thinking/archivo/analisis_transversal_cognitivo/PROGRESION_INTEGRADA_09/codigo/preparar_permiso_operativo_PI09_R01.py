"""Prepare a conditional public-route code CAS, codigo only; never deploy."""
from pathlib import Path
import argparse,ast,hashlib,importlib.util,json,shutil
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema'
SOURCE=P/'estados/NATIVE/sistema';OUT=H/'PERMISO_OPERATIVO_PI09_R01_PROPUESTO'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def require(ok,msg):
 if not ok:raise ValueError(msg)
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def replace(text,before,after,count=1):
 require(text.count(before)==count,'Cambió el ancla exacta de transporte: '+before[:100]);return text.replace(before,after)

def build():
 require(not OUT.exists(),'Propuesta existente preservada; use otra revisión')
 spec=importlib.util.spec_from_file_location('PI09_prepared_permission',H/'pi09_permiso_operativo_R01.py');permission=importlib.util.module_from_spec(spec);spec.loader.exec_module(permission)
 for name,digest in permission.PINS.items():require(sha(SOURCE/'capacidades'/name)==digest,'Fuente científica distinta: '+name)
 files={};world=(SOURCE/'app/mundo_genesis_apd05.py').read_text('utf-8-sig')
 world=replace(world,'        permission.install()  # Exact prepared/COMMITTED profile; no Native policy.','        permission.install()  # Exact prepared/COMMITTED profile; no Native policy.\n        from capacidades import pi09_permiso_operativo_R01 as pi09_permission\n        pi09_permission.install()  # Dormant exact COMMITTED permission; no Native policy.')
 world=replace(world,'    def validate(self,payload):\n        row=self._eci01_row(payload)','    def validate(self,payload):\n        row=self._eci01_row(payload)\n        from capacidades import pi09_permiso_operativo_R01 as pi09_permission\n        pi09_permission.validate_selected_external(self.a,row)\n        if pi09_permission.routes_public(self.a,row):\n            pi09_permission.validate_public(self.a,row)\n            return')
 world=replace(world,'    def execute(self,payload):\n        row=self._eci01_row(payload)','    def execute(self,payload):\n        row=self._eci01_row(payload)\n        from capacidades import pi09_permiso_operativo_R01 as pi09_permission\n        pi09_permission.validate_selected_external(self.a,row)\n        if pi09_permission.routes_public(self.a,row):\n            pi09_permission.validate_public(self.a,row)\n            self.before_mutation("PI09_EXACT_COMMITTED_OUTER_PUBLIC_ACCESS")\n            value=pi09_permission.execute_public(self.a,row,actuator=payload.get("actuador","closed"),directory=self.work_directory)\n            return {"version":pi09_permission.VERSION,"rows":[value]}')
 world=replace(world,"        return result\n\n    def validate(self,payload):","        for path in pi09_permission.code_files():\n            self.code_sha256['PI09/public/'+path.name]=hashlib.sha256(path.read_bytes()).hexdigest()\n        return result\n\n    def validate(self,payload):")
 files['app/mundo_genesis_apd05.py']=world
 dispatch=(SOURCE/'capacidades/pi04_dispatcher.py').read_text('utf-8-sig')
 before="return _load('pi08_permisos_operativos_R01').configure_C2C(_load('pi05_permiso_principal_R01').configure(component,a),a)"
 dispatch=replace(dispatch,before,"return _load('pi09_permiso_operativo_R01').configure_C2C(_load('pi08_permisos_operativos_R01').configure_C2C(_load('pi05_permiso_principal_R01').configure(component,a),a),a)",2)
 dispatch=replace(dispatch,"    paths.append(root/'pi08_permisos_operativos_R01.py')","    paths.append(root/'pi08_permisos_operativos_R01.py')\n    paths.extend(_load('pi09_permiso_operativo_R01').code_files())")
 files['capacidades/pi04_dispatcher.py']=dispatch
 files['capacidades/pi09_permiso_operativo_R01.py']=(H/'pi09_permiso_operativo_R01.py').read_text('utf-8-sig')
 old=H.parent.parent/'PROGRESION_INTEGRADA_08/codigo/pi08_identidad_c2c_B_R01.py'
 identity=old.read_text('utf-8-sig').replace('ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_REAL_01',permission.LIFE).replace('PI08.B','PI09').replace('PI08_B','PI09').replace('prospective PI08','prospective PI09')
 files['app/pi09_identidad_c2c_R01.py']=identity
 # The launcher already opens the six-selector existing continuation. Keeping
 # it literal avoids a second import path and retains the selected-life CLI.
 launcher=S/'app/usar_dee.py';files['app/usar_dee.py']=launcher.read_text('utf-8-sig')
 rows=[]
 for name,text in files.items():
  ast.parse(text);target=OUT/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,'utf8')
  product=S/name;rows.append({'file':name,'source':str(target),'sha256':sha(target),'before_sha256':sha(product)if product.is_file()else None})
 contract={'schema':'DEE.PI09.exact_native_consultation_permission.v1','status':'PREPARED_DIAGNOSTIC','life_id':permission.LIFE,'profile':'fisica_directa','protocol_sha256':permission.PINS['PROTOCOLO_PI09_CONSULTA_R01.json'],'allowed_modes':['eci01-pi09-episodio','eci01-pi09-estado'],'all_outer_FI_requests':True,'public_FI_domain':[0,20],'internal_C2C_FI_redirected':False,'FI_protocol_sha256':permission.PINS['PROTOCOLO_PI07_ACCESO_FI_R01.json'],'C2C_protocol_sha256':permission.C2C32,'C2C_allowed_modes':['eci01-pi04-c2c-oportunidad','eci01-pi04-c2c-estado'],'frozen_files_sha256':permission.PINS,'public_arithmetic_policy':'legacy_partial','arithmetic_guard_actual_gate_met':False,'arithmetic_guard_actual_evidence':[],'all_adoption_gates_met':False,'adoption_decision_sha256':None,'finite_resources_preserved_without_reset':True,'historical_PI07_environment_material_disabled':True,'prepared_is_not_operational_approval':True}
 file=OUT/'contratos/PI09_CONSULTA_OPERATIVA_R01.json';write(file,contract)
 rows.append({'file':'contratos/PI09_CONSULTA_OPERATIVA_R01.json','source':str(file),'sha256':sha(file),'before_sha256':None})
 write(OUT/'PLAN.json',{'schema':'DEE.PI09.exact_public_permission.prepared_code_CAS.R01','applied':False,'Native_executed':False,'source_state_read':False,'life_id':permission.LIFE,'code_files':rows,'unchanged_scientific_sources':{n:{'source':str(SOURCE/'capacidades'/n),'sha256':d}for n,d in permission.PINS.items()},'same_native_identity_leaf_adapter_only':True,'default_arithmetic':'legacy_partial','new_guard_requires_actual_pair_and_reserved_gates':True,'public_route':'gestionar.py pedir SESION con eci01-balance; same ordinary four-field aritmetica-directa only after separately approved P0 policy','internal_FI_routing_unchanged':True,'Root_next':'Review code delta and actual gates. Include complete source closure plus these overrides in reasoned same-ID adoption decision. No direct deployment by this preparer.'})
 print(json.dumps({'prepared':str(OUT),'plan_sha256':sha(OUT/'PLAN.json'),'files':len(rows),'Native_executed':False,'source_state_read':False}))

if __name__=='__main__':build()
