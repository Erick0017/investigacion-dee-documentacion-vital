"""Root-only bounded CAS deployment into the isolated RP_A01 continuation.
Default prepares a delta only. Never targets Cognitive or original PI07 worlds.
"""
from pathlib import Path
import argparse,ast,datetime,hashlib,json,os,shutil
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';BASE=C/'reproducibilidad/codigo_preservado/PI07_R03_LOCAL_FI_PRE34_R03';TARGET=P/'estados/RP_A01/sistema';STAGE=H/'PI08_A1_INSTALACION_R02';PLAN=P/'control/PI08_A1_HOOKS_PREPARADOS_R03.json';OUT=P/'control/PI08_A1_HOOKS_APLICADOS_R03.json'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def put(p,value):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def replace_once(text,old,new):
 if text.count(old)!=1:raise ValueError('Exact historical hook anchor changed: '+old[:75])
 return text.replace(old,new)
def prepare():
 if PLAN.exists()or STAGE.exists():raise FileExistsError('Prepared hook revision preserved')
 shutil.copytree(H/'PI08_A1_STAGE',STAGE)
 for name in('pi08_integracion_c2c_R01.py','pi08_permisos_operativos_R01.py'):shutil.copyfile(H/name,STAGE/'capacidades'/name)
 manifest=read(STAGE/'capacidades/PROTOCOLO_PI08_C2C_INTEGRACION_R01.json');manifest['files_sha256']['pi08_integracion_c2c_R01.py']=sha(STAGE/'capacidades/pi08_integracion_c2c_R01.py')
 (STAGE/'capacidades/PROTOCOLO_PI08_C2C_INTEGRACION_R01.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 profile={'schema':'DEE.PI08.exact_operational_profile.v1','status':'PREPARED_DIAGNOSTIC','life_id':LIFE,'profile':'fisica_directa','source_complete_prefix':'PI07_R03_POST4_T849645','source_complete_prefix_manifest_sha256':'06c0bd42cf408933955743465eae357a74658e8d68521da24c400a6ebe7b8575','R03_protocol_sha256':'f69e8558799558a1ccceb70e0684a061a971b9521ad8985205d1662aea55d269','FI_protocol_sha256':'4f15e2c892ab067c46338a7d89c0c6714b68f1436f936568e723a6bc1a7ccbc6','all_outer_FI_requests':True,'public_FI_domain':[0,20],'internal_C2C_FI_redirected':False,'C2C_allowed_modes':['eci01-pi04-c2c-oportunidad','eci01-pi04-c2c-estado'],'C2C_protocol_sha256':sha(STAGE/'capacidades/PROTOCOLO_PI08_C2C_32_R01.json'),'adoption_decision_sha256':None,'classification':'Explicit P0 access/permission migration; not a Native acquisition. Selected use remains blocked until actual COMMITTED adoption.'}
 put(STAGE/'contratos/PI08_USO_OPERATIVO_R01.json',profile)
 original=BASE/'app/mundo_genesis_apd05.py';world=original.read_text('utf-8-sig')
 world=replace_once(world,'        result=super()._open_locked()\n','        result=super()._open_locked()\n        from capacidades import pi08_permisos_operativos_R01 as permission\n        permission.install()  # Exact prepared/COMMITTED profile; no Native policy.\n')
 world=replace_once(world,'        return result\n\n    def validate(self,payload):',"        from capacidades import pi08_integracion_c2c_R01 as pi08\n        pi08.operational_dependencies(self.a,self.work_directory)\n        for path in (*pi08.code_files(),Path(permission.__file__)):\n            self.code_sha256['PI08/'+path.name]=hashlib.sha256(path.read_bytes()).hexdigest()\n        return result\n\n    def validate(self,payload):")
 anchor="        if row is not None and str(row.get('modo','')).startswith('eci01-pi07-'):"
 # This anchor occurs once in validate and once in execute: preserve the old
 # branches literally while inserting a mode-only PI08 instrument router.
 if world.count(anchor)!=2:raise ValueError('Exact two historical PI07 routes required')
 first=world.index(anchor);world=world[:first]+"        if row is not None and str(row.get('modo','')).startswith('eci01-pi08-c2c-'):\n            from capacidades import pi08_integracion_c2c_R01 as pi08\n            pi08.validate(self.a,row)\n            return\n"+world[first:]
 execute=world.index('    def execute(self,payload):');index=world.index(anchor,execute)
 world=world[:index]+"        if row is not None and str(row.get('modo','')).startswith('eci01-pi08-c2c-'):\n            from capacidades import pi08_integracion_c2c_R01 as pi08\n            pi08.validate(self.a,row)\n            self.before_mutation('PI08_EXPLICIT_EXTERNAL_PREPARE_COMMIT_NO_NATIVE_INPUT')\n            value=pi08.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)\n            return {'version':pi08.VERSION,'rows':[value]}\n"+world[index:]
 world=replace_once(world,"        result['PI07']=pi07.operational_dependencies(self.a,self.work_directory)\n", "        result['PI07']=pi07.operational_dependencies(self.a,self.work_directory)\n        from capacidades import pi08_integracion_c2c_R01 as pi08\n        result['PI08_integration']=pi08.operational_dependencies(self.a,self.work_directory)\n")
 world=replace_once(world,'    def external_uncertainty(self):\n','    def external_uncertainty(self):\n        from capacidades import pi08_integracion_c2c_R01 as pi08\n        if pi08.uncertain(self.a):return True\n')
 (STAGE/'app/mundo_genesis_apd05.py').write_text(world,encoding='utf8')
 cola=(BASE/'app/cola_local.py').read_text('utf-8-sig');anchor="            if str(row.get('modo','')).startswith('eci01-pi07-'):"
 cola=replace_once(cola,anchor,"            if str(row.get('modo','')).startswith('eci01-pi08-c2c-'):\n                from capacidades.pi08_integracion_c2c_R01 import validate_literal\n                validate_literal(row)\n                continue\n"+anchor);(STAGE/'app/cola_local.py').write_text(cola,encoding='utf8')
 dispatcher=(BASE/'capacidades/pi04_dispatcher.py').read_text('utf-8-sig')
 dispatcher=replace_once(dispatcher,"component=_load('pi05_c2c_ofertas_R01').effective_component(a,base,for_dependencies=for_dependencies)","component=_load('pi08_integracion_c2c_R01').effective_component(a,base,for_dependencies=for_dependencies)")
 dispatcher=replace_once(dispatcher,"component=_load('pi05_c2c_ofertas_R01').effective_component(a,original)","component=_load('pi08_integracion_c2c_R01').effective_component(a,original)")
 old="return _load('pi05_permiso_principal_R01').configure(component,a)";new="return _load('pi08_permisos_operativos_R01').configure_C2C(_load('pi05_permiso_principal_R01').configure(component,a),a)"
 if dispatcher.count(old)!=2:raise ValueError('Exact old identity permissions must remain in both paths')
 dispatcher=dispatcher.replace(old,new)
 dispatcher=replace_once(dispatcher,"    result['PI05_explicit_environment30']=_load('pi05_c2c_ofertas_R01').operational_dependencies(a,directory)\n", "    result['PI05_explicit_environment30']=_load('pi05_c2c_ofertas_R01').operational_dependencies(a,directory)\n    result['PI08_integration32']=_load('pi08_integracion_c2c_R01').operational_dependencies(a,directory)\n")
 dispatcher=replace_once(dispatcher,"def uncertain(a):\n", "def uncertain(a):\n    if _load('pi08_integracion_c2c_R01').uncertain(a):return True\n")
 dispatcher=replace_once(dispatcher,"    return list(dict.fromkeys(paths))", "    paths.extend(_load('pi08_integracion_c2c_R01').code_files())\n    paths.append(root/'pi08_permisos_operativos_R01.py')\n    return list(dict.fromkeys(paths))")
 (STAGE/'capacidades/pi04_dispatcher.py').write_text(dispatcher,encoding='utf8')
 names=['app/mundo_genesis_apd05.py','app/cola_local.py','capacidades/pi04_dispatcher.py','capacidades/pi08_integracion_c2c_R01.py','capacidades/pi08_permisos_operativos_R01.py','capacidades/PROTOCOLO_PI08_C2C_32_R01.json','capacidades/PROTOCOLO_PI08_RECHAZO34_R01.json','capacidades/PROTOCOLO_PI08_C2C_INTEGRACION_R01.json','contratos/PI08_USO_OPERATIVO_R01.json'];rows=[]
 for name in names:
  source=STAGE/name
  if source.suffix=='.py':ast.parse(source.read_text('utf-8-sig'))
  rows.append({'file':name,'source':str(source),'bytes':source.stat().st_size,'sha256':sha(source),'before_sha256':sha(BASE/name)if(BASE/name).is_file()else None})
 put(PLAN,{'schema':'DEE.PI08.A1.source_CAS_delta.v1','status':'PREPARED_NOT_APPLIED','target_system':str(TARGET),'life_id':LIFE,'files':rows,'unchanged_scientific_sources':read(H/'PI08_A1_STAGE/capacidades/PROTOCOLO_PI08_C2C_INTEGRACION_R01.json')['files_sha256'],'Native_executed':False,'scope':'One isolated same-world source update after its owner closes. All scientific R03/FI/C2C files remain literal; only exact permission, all-outer FI binding, external32 transaction and explicit routing added.'})
 return read(PLAN)
def main(a):
 plan=read(PLAN)if PLAN.exists()else prepare()
 if not a.aplicar:print(json.dumps({'plan':str(PLAN),'sha256':sha(PLAN),'files':len(plan['files']),'Native_executed':False}));return
 if OUT.exists():raise FileExistsError('Applied revision preserved')
 target=TARGET.resolve(strict=True)
 if target.is_relative_to(C.resolve())or not target.is_relative_to((P/'estados').resolve()):raise ValueError('Isolated P8target only')
 card=read(target/'estado/vidas'/LIFE/'VIDA.json')
 if card['life_id']!=LIFE or card['physical']['N']!=67:raise ValueError('Exact inherited candidate only')
 import sqlite3
 db=target/'estado/servicios_persistentes'/LIFE/'cola.sqlite3';con=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True)
 try:
  owner=con.execute("SELECT value FROM meta WHERE key='owner'").fetchone();owner=json.loads(owner[0])if owner else{};pending=con.execute("SELECT COUNT(*)FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]
 finally:con.close()
 if owner.get('running')or pending or db.with_name(db.name+'-wal').exists():raise ValueError('Closed/reconciled/noWAL owner required before source CAS')
 backup=H/'ORIGINALES_HOOKS_A1_PI08_R03'
 if backup.exists():raise FileExistsError('Existing source transition preserved')
 for row in plan['files']:
  source=Path(row['source']);destination=target/row['file']
  if sha(source)!=row['sha256']or(destination.exists()and sha(destination)!=row['before_sha256'])or(not destination.exists()and row['before_sha256']is not None):raise ValueError('Source/target CAS mismatch: '+row['file'])
 backup.mkdir()
 for row in plan['files']:
  destination=target/row['file']
  if destination.exists():old=backup/row['file'];old.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(destination,old)
  destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(row['source'],destination)
 if any(sha(target/row['file'])!=row['sha256']for row in plan['files']):raise RuntimeError('Deployment mismatch; preserve source transition')
 put(OUT,{**plan,'status':'APPLIED_SOURCE_ONLY_NO_NATIVE','applied_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_backups':str(backup),'Native_executed':False,'no_state_or_selector_changed':True})
 print(json.dumps({'proof':str(OUT),'sha256':sha(OUT),'Native_executed':False}))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');main(ap.parse_args())
