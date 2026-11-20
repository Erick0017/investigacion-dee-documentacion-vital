"""Root-only future full-pair import for the sealed PANEL/DISCOVERY identities.

Prepared before the post12 result exists. It binds actual full-pair bytes and
requires canonical native_real ordinal12; never substitutes the old C seed.
Default plan; no Native/clone execution by the coding agent.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,re,shutil
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';NATIVE=P/'estados/NATIVE'
KEY='DEE.Cognitive.PI09.selective_registered_consultation.R02'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(ok,msg):
 if not ok:raise ValueError(msg)
def load(name,path):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def arguments(a):
 seal=read(P/'codigo/SELLO_PI09_CONSULTA_R02.json')
 ids=seal['diagnostic_readonly_ids']if a.slug=='PANEL'else seal['experimental_continuation_ids']
 life='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_'+a.slug+'_01'
 require(life in ids,'Identidad no incluida en el sello prospectivo R02')
 pair=Path(a.prefijo).resolve(strict=True);allowed=[(P/'pares').resolve(),(RP/'materiales').resolve()]
 require(pair.parent in allowed and not pair.is_symlink(),'Sólo prefijo completo cerrado en paresPI09/RP')
 require(re.fullmatch(r'[0-9a-f]{64}',a.manifest_sha256)and sha(pair/'EXPORTACION_SERVICIO.json')==a.manifest_sha256,'SHA de prefijo real requerido')
 return seal,life,pair,P/'estados'/a.slug
def prepare(a,seal,life,pair,dest):
 require(not dest.exists(),'Destino ya usado; no se repite ni sustituye')
 source_system=NATIVE/'sistema';manifest=NATIVE/'SISTEMA_CODIGO_PI09.json'
 verifier=load('PI09_post12_export_validator',source_system/'app/importacion_emparejada.py');verifier.verify_export(pair)
 parser=load('PI09_post12_passive',RP/'observador_pasivo.py');v=parser.snapshot_view(pair/'VIDA.deetsnap.gz');meta=json.loads(v['metadata'][KEY]);m=read(pair/'EXPORTACION_SERVICIO.json')
 require(m['life_id']==seal['arms']['native_real']and meta['ordinal']==12 and meta['control']['arm']=='native_real'and not meta.get('pending')and not meta.get('uncertain')and v['physical']['tick']>884835,'Sólo el futuro Native-real post12 completo/coherente')
 require(not any(k.endswith('.R01')and k.startswith('DEE.Cognitive.PI09.selective_registered_consultation')for k in v['metadata']),'No se convierte una historia R01 en R02')
 system=dest/'sistema';system.mkdir(parents=True)
 original=read(manifest)
 for row in original['files']:
  name=row['file'];require(not name.startswith(('estado/','runtime/'))and '..'not in Path(name).parts,'Sólo código declarado')
  source=source_system/name;require(source.is_file()and sha(source)==row['sha256'],'Código Native cambió tras su cierre: '+name)
  target=system/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
 scopefile=system/'capacidades/PI09_TRANSPORTE_HEREDADO_R02.json';scope=read(scopefile);scope['life_id']=life
 scope['immediate_parent_post12']={'life_id':m['life_id'],'tick':v['physical']['tick'],'manifest_sha256':a.manifest_sha256,'snapshot_sha256':v['encoded_sha256']}
 scopefile.write_text(json.dumps(scope,ensure_ascii=False,indent=2)+'\n','utf8')
 (system/'estado/checkpoints').mkdir(parents=True);(system/'runtime').mkdir()
 wheel='dee_thinking-4.5.0-cp313-cp313-win_amd64.whl';source=C/'sistema/runtime'/wheel
 require(sha(source)=='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c','Motor compartido distinto');os.link(source,system/'runtime'/wheel)
 rows=[{'file':p.relative_to(system).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(system.rglob('*'))if p.is_file()and not p.is_relative_to(system/'runtime')]
 write(dest/'SISTEMA_CODIGO_PI09.json',{'schema':'DEE.PI09.post12_derived_code_closure.R03','files':rows,'source_native_code_manifest_sha256':sha(manifest),'transport_scope_rebound_only':True,'all_scientific_source_bytes_preserved':True})
 tools=('reproducir.py','importar_diagnostico.py','ejecutar_diagnostico.py','propietario_diagnostico.py','observador_pasivo.py')
 context={'schema':'DEE.reproduction.explicit_diagnostic.v1','life':life,'recipe':'PI09_NATIVE_POST12_'+a.slug,'variant':a.slug,'prefix':str(pair),'prefix_manifest_sha256':a.manifest_sha256,'system':str(system),'python':str(C/'motor/python313/python.exe'),'product':str(C),'destination':str(dest),'source_code_manifest_sha256':sha(dest/'SISTEMA_CODIGO_PI09.json'),'tool_sources':[{'file':n,'sha256':sha(RP/n)}for n in tools],'never_select_or_promote':True,'Native_PI09_metadata_life_id_left_historical':True}
 write(dest/'CONTEXTO_EJECUCION.json',context);write(dest/'PREPARACION_PI09.json',{'schema':'DEE.PI09.post12_clone_prepared.R03','life_id':life,'system':str(system),'context_sha256':sha(dest/'CONTEXTO_EJECUCION.json'),'Native_executed':False})
 print(json.dumps({'prepared':True,'system':str(system),'life_id':life,'source_tick':v['physical']['tick'],'Native_executed':False},ensure_ascii=False))
def main():
 p=argparse.ArgumentParser();p.add_argument('--slug',choices=['PANEL','DISCOVERY'],required=True);p.add_argument('--prefijo',required=True);p.add_argument('--manifest-sha256',required=True)
 g=p.add_mutually_exclusive_group();g.add_argument('--preparar',action='store_true');g.add_argument('--importar',action='store_true');a=p.parse_args();seal,life,pair,dest=arguments(a)
 if a.preparar:prepare(a,seal,life,pair,dest)
 elif a.importar:
  base=load('PI09_same_exact_import_supervisor',P/'codigo/clonar_C_PI09_R02.py');base.PAIR=pair;base.PAIR_SHA=a.manifest_sha256
  a.vida=life;base.import_once(a,dest,dest/'sistema')
 else:print(json.dumps({'mode':'PLAN_ONLY','source_full_pair':str(pair),'manifest_sha256':a.manifest_sha256,'source_requirement':'actual native_real R02ordinal12 complete state, not a physical snapshot alone','life_id':life,'system':str(dest/'sistema'),'Native_executed':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
