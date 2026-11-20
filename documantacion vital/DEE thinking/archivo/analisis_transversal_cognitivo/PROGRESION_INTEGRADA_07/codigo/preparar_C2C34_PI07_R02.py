"""Prepare a conditional additive external34 source delta; Root applies only."""
from pathlib import Path
import argparse,ast,hashlib,json,os,uuid
P=Path(__file__).resolve().parents[1];H=P/'codigo';S=P/'estados/candidato/sistema';D=H/'FUENTES_C2C34_PI07_R02'
FI=H/'FUENTES_ACCESO_FI_PI07_R01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def read(p):return json.loads(p.read_text('utf-8-sig'))
def main(a):
 planfile=P/'control/C2C34_PI07_DELTA_CONDICIONAL_R02.json'
 if not a.aplicar:
  if D.exists()or planfile.exists():raise FileExistsError('Preserve previous prepared delta')
  cap=D/'capacidades';cap.mkdir(parents=True);rows=[]
  fi_plan=read(P/'control/ACCESO_FI_PI07_PREPARADO_R01.json')
  for row in fi_plan['files']:
   if sha(FI/row['file'])!=row['sha256']:raise ValueError('Prepared FI source differs; do not rebase blindly')
  oldp=S/'capacidades/PROTOCOLO_PI05_C2C_30_R01.json';newp=H/'PROTOCOLO_PI07_C2C_34_R01.json'
  old=read(oldp);new=read(newp)
  if sha(oldp)!='5dda50c36fa72ea3932eded545e0bb673b40202d0d553cfa97a50ab31c67d1bc'or sha(newp)!='90c2bce8765a494dc3073ad85c61b0eb525593d88198993a9ab88c05c93ce58f':raise ValueError('Exact independently frozen public protocols required')
  if new['schedule'][:30]!=old['schedule']or len(new['schedule'])!=34:raise ValueError('Preserve all30 historical offers')
  for n in('pi04_coordinacion_central_C2C.py','PROTOCOLO_PI04_C2C_R01.json','PROTOCOLO_PI05_C2C_30_R01.json','PROTOCOLO_PI05_C2C_EXTENSION_R01.json','pi05_c2c_ofertas_R01.py'):(cap/n).write_bytes((S/'capacidades'/n).read_bytes())
  for n in('pi07_c2c_ofertas_R01.py','PROTOCOLO_PI07_C2C_34_R01.json'):(cap/n).write_bytes((H/n).read_bytes())
  manifest={'schema':'DEE.PI07.C2C.explicit_environment34.protocol.v1','status':'SEALED_BEFORE_NEW_RESERVES','original_protocol_file':oldp.name,'original_protocol_sha256':sha(oldp),'effective_protocol_file':newp.name,'effective_protocol_sha256':sha(newp),'additional_public_offers':new['schedule'][30:],'allowed_original_ordinal':30,'resources_before':30,'resources_after':34,'files_sha256':{n:sha(cap/n)for n in('pi04_coordinacion_central_C2C.py','PROTOCOLO_PI05_C2C_30_R01.json','PROTOCOLO_PI07_C2C_34_R01.json','pi05_c2c_ofertas_R01.py','PROTOCOLO_PI05_C2C_EXTENSION_R01.json','pi07_c2c_ofertas_R01.py')},'scope':'External four64Bsupplies and appended public offers only. Preserve old30prefix/KEY/logs/rows/products/rejections/clocks/RAW; no acquired new knowledge.'}
  save(cap/'PROTOCOLO_PI07_C2C_EXTENSION_R01.json',manifest)
  # Separate new revision; the previous conditional30permission is preserved.
  permission=(H/'pi07_permiso_principal_R01.py').read_text('utf8').replace('permission.R01_CONDITIONAL','permission.R02_ENV34_CONDITIONAL').replace('explicit_environment30.R01','explicit_environment34.R01').replace("DEE.Cognitive.PI05.C2C.explicit_environment34.R01","DEE.Cognitive.PI07.C2C.explicit_environment34.R01").replace('5dda50c36fa72ea3932eded545e0bb673b40202d0d553cfa97a50ab31c67d1bc',sha(newp)).replace('requires_environment30','requires_environment34')
  ast.parse(permission);(cap/'pi07_permiso_principal_R02.py').write_text(permission,encoding='utf8')
  old=(S/'capacidades/pi04_dispatcher.py').read_text('utf8');new=old.replace("_load('pi05_c2c_ofertas_R01').effective_component", "_load('pi07_c2c_ofertas_R01').effective_component")
  new=new.replace("return _load('pi05_permiso_principal_R01').configure(component,a)","return _load('pi07_permiso_principal_R02').configure(_load('pi05_permiso_principal_R01').configure(component,a),a)")
  new=new.replace("result['PI05_explicit_environment30']=", "result['PI07_explicit_environment34']=_load('pi07_c2c_ofertas_R01').operational_dependencies(a,directory)\n    result['PI05_explicit_environment30']=")
  new=new.replace("def uncertain(a):\n", "def uncertain(a):\n    if _load('pi07_c2c_ofertas_R01').uncertain(a):return True\n")
  new=new.replace("paths.append(root/'pi05_permiso_principal_R01.py')", "paths.append(root/'pi05_permiso_principal_R01.py')\n    paths.extend(_load('pi07_c2c_ofertas_R01').code_files())\n    paths.append(root/'pi07_permiso_principal_R02.py')")
  ast.parse(new);(cap/'pi04_dispatcher.py').write_text(new,encoding='utf8')
  app=D/'app';app.mkdir()
  for n in('mundo_genesis_apd05.py','cola_local.py'):
   old=(FI/'app'/n).read_text('utf8');new=old
   if n=='cola_local.py':
    needle="            if str(row.get('modo','')).startswith('eci01-pi07-'):"
    extra="            if row.get('modo')in('eci01-pi07-c2c-ampliar','eci01-pi07-c2c-extension-estado'):\n                from capacidades.pi07_c2c_ofertas_R01 import validate_literal\n                validate_literal(row)\n                continue\n"
    if old.count(needle)!=1:raise ValueError('Exact queue insertion point')
    new=old.replace(needle,extra+needle)
   else:
    needle="        if row is not None and str(row.get('modo','')).startswith('eci01-pi07-'):"
    if old.count(needle)!=2:raise ValueError('Exact owner validation/dispatch insertion points')
    first="        if row is not None and row.get('modo')in('eci01-pi07-c2c-ampliar','eci01-pi07-c2c-extension-estado'):\n            from capacidades import pi07_c2c_ofertas_R01 as supply\n            supply.validate(self.a,row)\n            return\n"
    second="        if row is not None and row.get('modo')in('eci01-pi07-c2c-ampliar','eci01-pi07-c2c-extension-estado'):\n            from capacidades import pi07_c2c_ofertas_R01 as supply\n            supply.validate(self.a,row)\n            self.before_mutation('PI07_EXPLICIT_ENVIRONMENT30_TO34_NO_NATIVE_EDIT')\n            value=supply.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)\n            return {'version':supply.VERSION,'rows':[value]}\n"
    pos=old.index(needle);new=old[:pos]+first+old[pos:];pos=new.index(needle,new.index('    def execute('));new=new[:pos]+second+new[pos:]
   ast.parse(new);(app/n).write_text(new,encoding='utf8')
  newnames=('capacidades/pi07_c2c_ofertas_R01.py','capacidades/PROTOCOLO_PI07_C2C_34_R01.json','capacidades/PROTOCOLO_PI07_C2C_EXTENSION_R01.json','capacidades/pi07_permiso_principal_R02.py')
  changed=('capacidades/pi04_dispatcher.py','app/mundo_genesis_apd05.py','app/cola_local.py')
  rows=[{'file':name,'sha256':sha(D/name),'bytes':(D/name).stat().st_size,'before_sha256':None if name in newnames else sha((FI if name.startswith('app/')else S)/name)}for name in(*newnames,*changed)]
  plan={'schema':'DEE.PI07.external34.conditional_delta.v1','status':'PREPARADO_GATES_PENDIENTES_NO_APLICADO','files':rows,'preserved':{str(p.relative_to(S)):sha(p)for p in(S/'capacidades/pi04_coordinacion_central_C2C.py',S/'capacidades/pi05_c2c_ofertas_R01.py',S/'capacidades/PROTOCOLO_PI05_C2C_30_R01.json',S/'capacidades/PROTOCOLO_PI05_C2C_EXTENSION_R01.json',S/'capacidades/pi07_regulacion_R03.py',S/'capacidades/PROTOCOLO_PI07_R03.json')},'Native_executed':False,'product_modified':False,'material_literal_if_Root_authorizes':{'modo':'eci01-pi07-c2c-ampliar'},'requires_actual_C2C_ordinal':30,'new_offers':4,'planned_uses':2,'remaining_after_two_new_uses':2,'not_learning':True,'scope':'Only Root may apply after scientific gates and closed owners; no source actor/protocol/context/choice changes.'}
  plan['prepared_FI_basis']={'proof':str(P/'control/ACCESO_FI_PI07_PREPARADO_R01.json'),'sha256':sha(P/'control/ACCESO_FI_PI07_PREPARADO_R01.json'),'scope':'Only three C2C34P0insertions ahead of the future FI facade; all new FI facade imports retained.'}
  plan['preserved'].update({'capacidades/'+name:sha(FI/'capacidades'/name)for name in('pi07_acceso_FI_regulado_R01.py','PROTOCOLO_PI07_ACCESO_FI_R01.json','acceso_integrado_eci01.py')})
  save(planfile,plan)
  print(json.dumps({'plan':str(planfile),'sha256':sha(planfile),'files':len(rows),'Native_executed':False}));return
  
 plan=read(planfile);out=P/'control/C2C34_PI07_DELTA_APLICADO_R02.json'
 if out.exists()or(P/'PI07_ROOT_NATIVE_WRITER.lock').exists()or(S/'estado/ACTIVO.json').exists():raise ValueError('Fresh closed unselected source only')
 if (S/'estado/locks').exists()and any((S/'estado/locks').iterdir()):raise ValueError('Owner locks remain')
 for row in plan['files']:
  target=S/row['file']
  if sha(D/row['file'])!=row['sha256']or(row['before_sha256']is None and target.exists())or(row['before_sha256']is not None and sha(target)!=row['before_sha256']):raise ValueError('Exact immutable source CAS failed')
 for name,h in plan['preserved'].items():
  if sha(S/name)!=h:raise ValueError('A protected actor/history file changed')
 backup=H/'ORIGINALES_C2C34_PI07_R02';backup.mkdir(exist_ok=False)
 for row in plan['files']:
  target=S/row['file']
  if row['before_sha256']is not None:
   original=backup/row['file'];original.parent.mkdir(parents=True,exist_ok=True);original.write_bytes(target.read_bytes())
  temporary=target.with_name(target.name+'.C2C34_'+uuid.uuid4().hex+'.tmp');temporary.write_bytes((D/row['file']).read_bytes());os.replace(temporary,target)
 for name,h in plan['preserved'].items():
  if sha(S/name)!=h:raise RuntimeError('Protected actor/history changed')
 plan.update(status='SOURCE_CODE_APPLIED_ZERO_NATIVE_NOT_SUPPLIED',Native_executed=False,product_modified=False,source_backup=str(backup));save(out,plan);print(json.dumps({'proof':str(out),'sha256':sha(out),'Native_executed':False}))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');main(ap.parse_args())
