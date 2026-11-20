"""Additive Root-only D6 family registration; default stages small code/analysis.

Copies the already closed pre-D full pair once into stable RP; no re-export,
Native import, principal update or change to shared RP tools/old recipes.
"""
from pathlib import Path,PurePosixPath
import argparse,ast,datetime,hashlib,importlib.util,json,os,shutil
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';SOURCEPAIR=P/'pares/DISCOVERY_POSTPANEL_T907543'
RID='pi09_d6_familia_desde_DISCOVERY_T907543_R01';KEY='PI09_D_FAMILIA_R01';ALIAS='PI09_DISCOVERY_PRE_D_T907543';ANALYSIS='PI09_D6_ANALISIS_R01';PAIR_SHA='8500dafda573afb48ca631b1a7cd3f2cdb1131769485f49811f4f1cfac5fe067'
STAGE=H/'RP_D6_INCORPORACION_R01_PREPARADA';EXPECT=H/'RP_D6_EXPECTATIVAS_R01';CAP=H/'RP_D_FAMILIA_R01_PREPARADA/capsule';PROOF=P/'control/RP_D6_FAMILIA_INCORPORADA_PI09_R01.json'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
def regular(p):
 for n in(p,*p.parents):need(not n.exists()or not(n.is_symlink()or getattr(n.lstat(),'st_file_attributes',0)&1024),'No linked source/target')
def put(p,v):
 regular(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def cp(source,target):
 regular(source);regular(target);target.parent.mkdir(parents=True,exist_ok=True);before=sha(source)
 with source.open('rb')as i,target.open('xb')as o:shutil.copyfileobj(i,o)
 need(sha(source)==before==sha(target),'Source/copy changed')
def relative(name):
 p=PurePosixPath(name);need(isinstance(name,str)and '\\'not in name and ':'not in name and not p.is_absolute()and all(v not in('.','..')for v in p.parts),'Safe manifest relative path required');return p
def verify(root,mf):
 m=read(root/mf)
 for row in m['files']:
  f=root/relative(row['file']);regular(f);need(f.is_file()and f.stat().st_size==row['bytes']and sha(f)==row['sha256'],'Changed preserved member '+row['file'])
 return m
def verify_pair(root):
 need(sha(root/'EXPORTACION_SERVICIO.json')==PAIR_SHA,'Exact complete pre-D manifest required');m=read(root/'EXPORTACION_SERVICIO.json');names=set()
 for row in m['members']:
  rel=relative(row['file']);need(row['file']not in names,'Duplicate full pair member');names.add(row['file']);f=root/rel;regular(f);need(f.is_file()and f.stat().st_size==row['bytes']and sha(f)==row['sha256'],'Full pair member differs')
 need({f.relative_to(root).as_posix()for f in root.rglob('*')if f.is_file()and f!=root/'EXPORTACION_SERVICIO.json'}==names,'Unlisted complete pair files')
 for name in m['empty_directories_preserved']:need((root/relative(name)).is_dir(),'Declared full source directory missing')
 return m
def protected():
 s=C/'sistema';active=s/'estado/ACTIVO.json';card=s/'estado/vidas'/read(active)['life_id']/'VIDA.json';r=read(card);return{str(p):sha(p)for p in(active,card,s/r['snapshot'])}
def prepare(bundle):
 if(STAGE/'PLAN.json').exists():return read(STAGE/'PLAN.json')
 need(not STAGE.exists(),'Partial prior registration proposal preserved');need((EXPECT/'receta.json').is_file(),'Actual closed Real6 expectations must be frozen first');recipe=read(EXPECT/'receta.json');need(recipe['id']==RID and recipe['code_capsule_key']==KEY and recipe['verification']['Native_replay_verified']is False,'Exact prepared D6 family recipe required')
 source=recipe['sources']['actual_real6'];proof=read(Path(source['path']));need(sha(Path(source['path']))==source['sha256']and proof['closed']is True and proof['error']is None,'Actual closed source proof changed');verify(CAP,'SISTEMA_CODIGO.json')
 need(sha(SOURCEPAIR/'EXPORTACION_SERVICIO.json')==PAIR_SHA,'Immutable pre-D full pair required');bundle=bundle.resolve(strict=True);need(bundle.is_relative_to((P/'control').resolve())and(bundle/'INDICE_D_PI09_R02.json').is_file(),'Closed actual compact D6 bundle required')
 parserfile=H/'RECALCULAR_D_PI09_R03.py';need(sha(parserfile)=='fd88add765366ee1ea7cacb58fc7fd98c09794a90b1e2c84e6d8cf0fb8cf72aa','Actual fixed R03 documentary parser required; R02 failure preserved')
 for name in('RECALCULAR_CONSULTA_PI09_R01.py','RECALCULAR_C_PI08_LITERAL.py','RECALCULAR_PRIMARIOS_PI07_LITERAL.py'):need(sha(H/name)==sha(bundle/name),'Portable literal parser differs from actual fixed-parser dependencies')
 spec=importlib.util.spec_from_file_location('PI09_D6_actual_recalculation',parserfile);parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser);actual=parser.calculate(bundle);need(actual.get('integrity_passed')is True and any(g['arm']=='real'and g['evaluation_completed']==6 for g in actual['groups']),'Actual portable Real6 must recalculate without Native')
 for file in sorted(CAP.rglob('*')):
  if file.is_file():cp(file,STAGE/'capsule'/file.relative_to(CAP))
 for file in sorted(bundle.rglob('*')):
  if file.is_file():cp(file,STAGE/'analysis'/file.relative_to(bundle))
 cp(parserfile,STAGE/'analysis/RECALCULAR_D_PI09_R03.py')
 wrapper='''from pathlib import Path
import argparse,importlib.util,json
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True);a=p.parse_args();root=a.root.resolve(strict=True);out=a.out_dir.resolve()
 if out.exists()or out==root or root.is_relative_to(out)or out.is_relative_to(root):raise ValueError('El recálculo requiere destino nuevo externo al material')
 s=importlib.util.spec_from_file_location('D6_preserved_recalc',root/'RECALCULAR_D_PI09_R03.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);value=m.calculate(root)
 if value.get('integrity_passed')is not True or not any(g['arm']=='real'and g['evaluation_completed']==6 for g in value['groups']):raise ValueError('Los seis primarios D reales no están verificados')
 out.mkdir();(out/'RESULTADO_RECALCULO.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\\n','utf8');print(json.dumps({'integrity_passed':True,'Native_executed':False,'DEE_imports':0}))
if __name__=='__main__':main()
'''
 ast.parse(wrapper);(STAGE/'analysis/RECALCULAR_RP_D6_PI09_R01.py').write_text(wrapper,'utf8');rows=[{'file':p.relative_to(STAGE/'analysis').as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted((STAGE/'analysis').rglob('*'))if p.is_file()];put(STAGE/'analysis/MANIFIESTO_ESTABLE.json',{'schema':'DEE.PI09.D6.actual_analysis.v1','files':rows,'actual_source_not_replay':True})
 recipe['analysis']={'product_relative':'reproducibilidad/materiales/'+ANALYSIS,'manifest':'MANIFIESTO_ESTABLE.json','manifest_sha256':sha(STAGE/'analysis/MANIFIESTO_ESTABLE.json'),'recalculation_script':'RECALCULAR_RP_D6_PI09_R01.py','interface':'DEE.recalculation.root_outdir.v1'};put(STAGE/'receta.json',recipe)
 resources=read(RP/'RECURSOS.json');need(KEY not in resources['code_capsules']and not(RP/'recetas'/(RID+'.json')).exists(),'Only new D family/capsule IDs')
 resources['pairs'][ALIAS]={'product_relative':'reproducibilidad/materiales/'+ALIAS,'life_id':'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01','tick':907543,'manifest_sha256':PAIR_SHA};resources['code_capsules'][KEY]={'product_relative':'reproducibilidad/codigo_preservado/'+KEY,'manifest':'SISTEMA_CODIGO.json','manifest_sha256':sha(STAGE/'capsule/SISTEMA_CODIGO.json')};resources.setdefault('analysis_deltas',{})['PI09_D6_R01']=recipe['analysis'];put(STAGE/'RECURSOS_PROPUESTOS.json',resources)
 plan={'schema':'DEE.PI09.D.RP_family.CAS_plan.R01','applied':False,'Native_executed':False,'resource_before_sha256':sha(RP/'RECURSOS.json'),'resource_after_sha256':sha(STAGE/'RECURSOS_PROPUESTOS.json'),'recipe':RID,'recipe_sha256':sha(STAGE/'receta.json'),'capsule_key':KEY,'capsule_manifest_sha256':sha(STAGE/'capsule/SISTEMA_CODIGO.json'),'pair_manifest_sha256':PAIR_SHA,'analysis_manifest_sha256':recipe['analysis']['manifest_sha256'],'source_actual6':source,'expected_dose':recipe['variants']['real6']['native_receipt_expectations'],'first_validation_life':'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DRF_20261111A','new_frontdoor_material_replay_executed':False,'shared_RP_tools_changed':False};put(STAGE/'PLAN.json',plan);return plan
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--bundle',type=Path,required=True);ap.add_argument('--aplicar',action='store_true');a=ap.parse_args();plan=prepare(a.bundle);need(sha(RP/'RECURSOS.json')==plan['resource_before_sha256'],'Concurrent RP registry change; preserve proposal');verify(STAGE/'capsule','SISTEMA_CODIGO.json');verify(STAGE/'analysis','MANIFIESTO_ESTABLE.json');need(sha(STAGE/'receta.json')==plan['recipe_sha256'],'Recipe stage changed')
 if a.aplicar:
  need(not(P/'PI09_ROOT_NATIVE_WRITER.lock').exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'Only a closed Root/RP writer window may register');cap=RP/'codigo_preservado'/KEY;analysis=RP/'materiales'/ANALYSIS;pair=RP/'materiales'/ALIAS;recipe=RP/'recetas'/(RID+'.json');need(not cap.exists()and not analysis.exists()and not recipe.exists()and not PROOF.exists(),'Existing/partial registration destinations preserved');prior=protected();m=verify_pair(SOURCEPAIR)
  if pair.exists():verify_pair(pair)
  else:
   pair.mkdir(parents=True)
   for row in m['members']:cp(SOURCEPAIR/row['file'],pair/row['file'])
   for name in m['empty_directories_preserved']:(pair/relative(name)).mkdir(parents=True,exist_ok=True)
   cp(SOURCEPAIR/'EXPORTACION_SERVICIO.json',pair/'EXPORTACION_SERVICIO.json');verify_pair(pair);verify_pair(SOURCEPAIR)
  cp(RP/'RECURSOS.json',P/'control/RECURSOS_ANTES_D_FAMILIA_PI09_R01.json')
  for src,dst in((STAGE/'capsule',cap),(STAGE/'analysis',analysis)):
   for file in sorted(src.rglob('*')):
    if file.is_file():cp(file,dst/file.relative_to(src))
  cp(STAGE/'receta.json',recipe);need(sha(RP/'RECURSOS.json')==plan['resource_before_sha256'],'RP CAS changed during copy');temp=RP/'RECURSOS.json.D_FAMILIA_WRITING';cp(STAGE/'RECURSOS_PROPUESTOS.json',temp);os.replace(temp,RP/'RECURSOS.json');need(protected()==prior,'RP registration changed the protected principal')
  put(PROOF,{**plan,'schema':'DEE.PI09.D.RP_family.applied.R01','applied':True,'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'recipe_path':str(recipe),'code_capsule':str(cap),'capsule_manifest':str(cap/'SISTEMA_CODIGO.json'),'stable_pair':str(pair),'stable_analysis':str(analysis),'principal_unchanged':True,'protected_principal':prior,'Native_executed':False})
 file=PROOF if a.aplicar else STAGE/'PLAN.json';print(json.dumps({'mode':'APPLIED_ROOT_ONLY'if a.aplicar else'PREPARED_NO_RP_WRITES','proof':str(file),'sha256':sha(file),'recipe':RID,'Native_executed':False}))
if __name__=='__main__':main()
