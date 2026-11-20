"""Additive Root-only RP registration. Default prepares codigo; no RP writes.

Preserves exact canonical scientific code, complete C prefix already copied,
and actual12 analysis. Only the capsule's declared empty-directory transport
differs. Never imports DEE, executes Native or changes a principal/old recipe.
"""
from pathlib import Path
import argparse,ast,copy,datetime,hashlib,json,os,shutil
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
OLD=H/'RP_CAPSULA_PI09_R03_PROPUESTA';FIXED=H/'RECETA_RP_PI09_NATIVE12_R01_FIJADA';BUNDLE=P/'control/NATIVE12_PORTABLE_R03'
STAGE=H/'RP_INCORPORACION_PI09_R01_PREPARADA';KEY='PI09_CONSULTA_SELECTIVA_R02_TRANSPORTE_R03';RID='pi09_consulta_native12_desde_C_T884835_R03';ALIAS='PI09_C_HEREDADA_T884835';ANALYSIS='PI09_NATIVE12_ANALISIS_R01'
PAIR=RP/'materiales'/ALIAS;PROOF=P/'control/RP_CONSULTA_INCORPORADA_PI09_R01.json'
def require(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def regular(p):
 for n in(p,*p.parents):require(not n.exists()or not(n.is_symlink()or getattr(n.lstat(),'st_file_attributes',0)&1024),'No se permiten enlaces en la preservación RP')
def put(p,v):
 regular(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def copyfile(src,dst):
 regular(src);regular(dst);dst.parent.mkdir(parents=True,exist_ok=True);before=sha(src)
 with src.open('rb')as i,dst.open('xb')as o:shutil.copyfileobj(i,o)
 require(sha(src)==before==sha(dst),'La copia o su fuente cambiaron')
def verify(root,manifest):
 m=read(root/manifest)
 for row in m['files']:
  p=root/row['file'];regular(p);require(p.is_file()and p.stat().st_size==row['bytes']and sha(p)==row['sha256'],'Miembro preservado distinto: '+row['file'])
 return m
def protected():
 s=C/'sistema';active=s/'estado/ACTIVO.json';card=s/'estado/vidas'/read(active)['life_id']/'VIDA.json';r=read(card)
 return {str(p):sha(p)for p in(active,card,s/r['snapshot'])}
def prepare():
 if (STAGE/'PLAN.json').is_file():return read(STAGE/'PLAN.json')
 require(not STAGE.exists(),'Stage parcial anterior preservado')
 require(sha(PAIR/'EXPORTACION_SERVICIO.json')=='08a8e65deb2071b7653bc0ab95f3d55b8038191a4f585c6803f6d81c16e8182f','Prefijo C estable no disponible')
 require(sha(BUNDLE/'INDICE_PI09_CONSULTA_R01.json')=='ed87e9159f2ddb5134aeedf11fe576cecbcabe9689ab493b1e68545e1bc22761','Cambió el índice Native12 real')
 capsule=OLD/'capsule';verify(capsule,'SISTEMA_CODIGO.json')
 for file in sorted(capsule.rglob('*')):
  if file.is_file():copyfile(file,STAGE/'capsule'/file.relative_to(capsule))
 analysis=STAGE/'analysis'
 for file in sorted(BUNDLE.rglob('*')):
  if file.is_file():copyfile(file,analysis/file.relative_to(BUNDLE))
 wrapper='''"""RP stdlib adapter over the preserved actual Native12 recalc."""
from pathlib import Path
import argparse,importlib.util,json
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True);a=p.parse_args()
 root=a.root.resolve(strict=True);out=a.out_dir.resolve()
 if out.exists()or out==root or root.is_relative_to(out)or out.is_relative_to(root):raise ValueError('El recálculo exige un directorio nuevo fuera del material estable')
 spec=importlib.util.spec_from_file_location('PI09_preserved_recalculation',root/'RECALCULAR_CONSULTA_PI09_R01.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 result=m.calculate(root)
 if result.get('integrity_passed')is not True or result.get('completed_opportunities')!=12:raise ValueError('El recálculo conservado no verifica los doce primarios')
 out.mkdir(parents=False);(out/'RESULTADO_RECALCULO.json').write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\\n','utf8')
 print(json.dumps({'integrity_passed':True,'completed_opportunities':12,'Native_executed':False,'DEE_imports':0}))
if __name__=='__main__':main()
'''
 ast.parse(wrapper);(analysis/'RECALCULAR_RP_PI09_R01.py').write_text(wrapper,'utf8')
 rows=[{'file':f.relative_to(analysis).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(analysis.rglob('*'))if f.is_file()]
 put(analysis/'MANIFIESTO_ESTABLE.json',{'schema':'DEE.PI09.canonical12.preserved_analysis.v1','files':rows,'source_index_sha256':sha(BUNDLE/'INDICE_PI09_CONSULTA_R01.json'),'actual_source_Native12_not_replay':True})
 recipe=read(FIXED/'receta.json');require(recipe['id']==RID and recipe['code_capsule_key']==KEY and recipe['verification']['Native_replay_verified']is False,'Receta fijada incorrecta')
 recipe['analysis']={'product_relative':'reproducibilidad/materiales/'+ANALYSIS,'manifest':'MANIFIESTO_ESTABLE.json','manifest_sha256':sha(analysis/'MANIFIESTO_ESTABLE.json'),'recalculation_script':'RECALCULAR_RP_PI09_R01.py','interface':'DEE.recalculation.root_outdir.v1'}
 put(STAGE/'receta.json',recipe)
 resources=read(RP/'RECURSOS.json');require(KEY not in resources['code_capsules']and RID not in [p.stem for p in(RP/'recetas').glob('*.json')],'Sólo claves y receta RP nuevas')
 if ALIAS in resources['pairs']:require(resources['pairs'][ALIAS]['manifest_sha256']==sha(PAIR/'EXPORTACION_SERVICIO.json'),'Alias C previo distinto')
 resources['pairs'][ALIAS]={'product_relative':'reproducibilidad/materiales/'+ALIAS,'life_id':'ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_C_01','tick':884835,'manifest_sha256':sha(PAIR/'EXPORTACION_SERVICIO.json')}
 resources['code_capsules'][KEY]={'product_relative':'reproducibilidad/codigo_preservado/'+KEY,'manifest':'SISTEMA_CODIGO.json','manifest_sha256':sha(STAGE/'capsule/SISTEMA_CODIGO.json')}
 resources.setdefault('analysis_deltas',{})['PI09_NATIVE12_R01']=recipe['analysis'];put(STAGE/'RECURSOS_PROPUESTOS.json',resources)
 plan={'schema':'DEE.PI09.RP.additive_registration.CAS_plan.R01','applied':False,'Native_executed':False,'resource_before_sha256':sha(RP/'RECURSOS.json'),'resource_after_sha256':sha(STAGE/'RECURSOS_PROPUESTOS.json'),'recipe':RID,'recipe_sha256':sha(STAGE/'receta.json'),'capsule_key':KEY,'capsule_manifest_sha256':sha(STAGE/'capsule/SISTEMA_CODIGO.json'),'analysis_manifest_sha256':sha(analysis/'MANIFIESTO_ESTABLE.json'),'pair_manifest_sha256':sha(PAIR/'EXPORTACION_SERVICIO.json'),'new_RP_frontdoor_Native_replay_executed':False,'shared_RP_tools_changed':False,'protected_principal':protected()}
 put(STAGE/'PLAN.json',plan);return plan
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');a=ap.parse_args();plan=prepare()
 require(sha(RP/'RECURSOS.json')==plan['resource_before_sha256']and protected()==plan['protected_principal'],'Cambio concurrente de registro o principal; no aplicar')
 verify(STAGE/'capsule','SISTEMA_CODIGO.json');verify(STAGE/'analysis','MANIFIESTO_ESTABLE.json')
 require(sha(STAGE/'receta.json')==plan['recipe_sha256']and sha(STAGE/'RECURSOS_PROPUESTOS.json')==plan['resource_after_sha256'],'Stage de registro cambió')
 if a.aplicar:
  cap=RP/'codigo_preservado'/KEY;analysis=RP/'materiales'/ANALYSIS;recipe=RP/'recetas'/(RID+'.json')
  require(not cap.exists()and not analysis.exists()and not recipe.exists()and not PROOF.exists(),'Destino RP ya presente; se conserva')
  copyfile(RP/'RECURSOS.json',P/'control/RECURSOS_ANTES_PI09_R01.json')
  for source,dest in((STAGE/'capsule',cap),(STAGE/'analysis',analysis)):
   for file in sorted(source.rglob('*')):
    if file.is_file():copyfile(file,dest/file.relative_to(source))
  copyfile(STAGE/'receta.json',recipe);require(sha(RP/'RECURSOS.json')==plan['resource_before_sha256'],'CAS del registro cambió durante la copia')
  temp=RP/'RECURSOS.json.PI09_WRITING'
  with temp.open('xb')as f:f.write((STAGE/'RECURSOS_PROPUESTOS.json').read_bytes());f.flush();os.fsync(f.fileno())
  os.replace(temp,RP/'RECURSOS.json');require(protected()==plan['protected_principal'],'Cambió el principal durante la incorporación RP')
  put(PROOF,{**plan,'schema':'DEE.PI09.RP.additive_registration.applied.R01','applied':True,'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'recipe_path':str(recipe),'code_capsule':str(cap),'capsule_manifest':str(cap/'SISTEMA_CODIGO.json'),'analysis':str(analysis),'principal_unchanged':True,'Native_executed':False})
 file=PROOF if a.aplicar else STAGE/'PLAN.json';print(json.dumps({'mode':'APPLIED_ROOT_ONLY'if a.aplicar else'PLAN_READY_NO_RP_WRITES','proof':str(file),'sha256':sha(file),'recipe':RID,'Native_executed':False}))
if __name__=='__main__':main()
