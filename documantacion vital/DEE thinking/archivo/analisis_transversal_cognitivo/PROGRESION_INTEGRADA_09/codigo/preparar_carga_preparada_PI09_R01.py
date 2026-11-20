"""Prepare only a two-file administrative supplement; Root reviews/applies."""
from pathlib import Path
import ast,hashlib,json,shutil
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';OUT=H/'CARGA_PREPARADA_PI09_R01_PROPUESTA'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if OUT.exists():raise FileExistsError('Prior proposal preserved')
 OUT.mkdir();permission=S/'capacidades/pi09_permiso_operativo_R01.py';text=permission.read_text('utf-8-sig')
 before=' _PRIOR_IDENTITY=old._identity;old._identity=_legacy_identity;_INSTALLED=True'
 if text.count(before)!=1:raise ValueError('Exact permission install anchor changed')
 text=text.replace(before,before+'\n from capacidades import pi09_carga_preparada_R01 as prepared_load\n prepared_load.install()')
 before='def validate_selected_external(a,row):\n'
 if text.count(before)!=1:raise ValueError('Exact external validation anchor changed')
 text=text.replace(before,before+' from capacidades import pi09_carga_preparada_R01 as prepared_load\n prepared_load.guard_external(a,row)\n')
 before=' files=[Path(__file__),*(Path(__file__).with_name(n)for n in PINS)]'
 if text.count(before)!=1:raise ValueError('Exact permission code closure anchor changed')
 text=text.replace(before," files=[Path(__file__),Path(__file__).with_name('pi09_carga_preparada_R01.py'),*(Path(__file__).with_name(n)for n in PINS)]")
 ast.parse(text);(OUT/permission.name).write_text(text,'utf8');shutil.copyfile(H/'pi09_carga_preparada_R01.py',OUT/'pi09_carga_preparada_R01.py')
 prepared=P/'control/PREPARACION_TRASLADO_PRODUCTO_PI09.json';m=json.loads(prepared.read_text('utf-8-sig'))
 rows=[{'file':'capacidades/'+name,'source':str(OUT/name),'sha256':sha(OUT/name),'before_sha256':sha(S/'capacidades'/name)if(S/'capacidades'/name).exists()else None}for name in(permission.name,'pi09_carga_preparada_R01.py')]
 plan={'schema':'DEE.PI09.prepared_load.administrative_supplement.CAS_plan.R01','Native_executed':False,'applied':False,'preparation':{'path':str(prepared),'sha256':sha(prepared)},'decision':m['decision'],'files':rows,'transport_literal_unchanged':True,'body_3b815_literal_unchanged':True,'states_only_while_unselected':True,'old_failure_preserved':True,'adopter_requires_explicit_supplement_validation':True}
 (OUT/'PLAN.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'plan':str(OUT/'PLAN.json'),'sha256':sha(OUT/'PLAN.json'),'files':rows}))
if __name__=='__main__':main()
