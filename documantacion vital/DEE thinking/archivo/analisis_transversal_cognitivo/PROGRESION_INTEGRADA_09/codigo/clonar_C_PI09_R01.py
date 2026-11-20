"""Root-only PI09 code preparation + official complete-pair importer.

Default plan. --preparar copies bounded code only; --importar opens the exact
official importer in one512MiB Job, then restores declared empty directories.
Neither flag is executed by the coding agent. No auto owner/start/retry.
"""
from pathlib import Path
import argparse,ast,datetime,hashlib,importlib.util,json,os,re,shutil,sys,time
P=Path(__file__).resolve().parents[1];P8=P.with_name('PROGRESION_INTEGRADA_08');C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';PY=C/'motor/python313/python.exe'
SOURCE=P8/'estados/C_R03/sistema';PAIR=P/'pares/C_HEREDADA_T884835';PAIR_SHA='08a8e65deb2071b7653bc0ab95f3d55b8038191a4f585c6803f6d81c16e8182f'
MANIFEST=P8/'codigo/FUENTES_C_PI08_R03_PREPARADAS/SISTEMA_CODIGO.json';MANIFEST_SHA='e63983fab77cb8b55e0a2cc61d90cf73d37eeacd68b7849af7ed629258695a6a'
FILES=('pi09_transporte_heredado_R01.py','pi09_dispatcher_R01.py','pi09_consulta_selectiva_R01.py','pi09_aritmetica_diagnostica_R01.py','PROTOCOLO_PI09_CONSULTA_R01.json','SELLO_PI09_CONSULTA_R01.json')
PLUGINS=('pi09_consulta_selectiva_R01','pi09_aritmetica_diagnostica_R01')
TOOLS=('reproducir.py','importar_diagnostico.py','ejecutar_diagnostico.py','propietario_diagnostico.py','observador_pasivo.py')
def require(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,path):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def regular(p):
 for x in(p,*p.parents):require(not x.exists()or not(x.is_symlink()or getattr(x.lstat(),'st_file_attributes',0)&1024),'No se admiten enlaces')
def checked(p,digest):require(p.is_file()and sha(p)==digest,'Cambió fuente fijada: '+str(p));return p
def arguments(a):
 require(re.fullmatch(r'[A-Z][A-Z0-9_]{0,24}',a.slug),'Slug PI09 explícito requerido')
 require(re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_[A-Za-z0-9_]{1,32}',a.vida),'Identidad PI09 exacta con prefijo autorizado')
 dest=P/'estados'/a.slug;regular(dest);return dest,dest/'sistema'
def prepare(a,dest,system):
 require(not dest.exists(),'Destino ya usado; conservarlo y no reimportar')
 checked(PAIR/'EXPORTACION_SERVICIO.json',PAIR_SHA);checked(MANIFEST,MANIFEST_SHA)
 rp=load('PI09_RP_STATIC_CHECK',RP/'reproducir.py');paircheck=rp.verify_pair({'product_relative':PAIR.relative_to(C).as_posix(),'manifest_sha256':PAIR_SHA,'life_id':read(PAIR/'EXPORTACION_SERVICIO.json')['life_id'],'tick':884835})if PAIR.is_relative_to(C)else None
 # verify_export is stdlib; it is loaded without importing app/DEE.
 verifier=load('PI09_STD_EXPORT_VALIDATOR',SOURCE/'app/importacion_emparejada.py');verifier.verify_export(PAIR)
 parser=load('PI09_PASSIVE_PARSER',RP/'observador_pasivo.py');view=parser.snapshot_view(PAIR/'VIDA.deetsnap.gz')
 require(view['physical']['tick']==884835 and view['encoded_sha256']=='ef52add3d7a6a5b9e310efb815bf8ae7dd47cb968104e7b1fa5c8a2b9f726d22','Prefijo C distinto')
 system.mkdir(parents=True);inputs=[]
 for row in read(MANIFEST)['files']:
  name=row['file'];require(not name.startswith(('estado/','runtime/'))and '..'not in Path(name).parts,'Sólo fuente de código')
  src=SOURCE/name;expected=row['sha256']
  if name=='app/mundo_genesis_apd05.py':expected='2cb1449fd7ad8d6188c52a1ff57d160506e4eff687b0317beab441f2e025ad9c'
  checked(src,expected);target=system/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target);inputs.append({'file':name,'sha256':expected})
 extra=SOURCE/'capacidades/pi08_identidad_B_readonly_C_R01.py';checked(extra,'8abba39fd72046172ff914a6714e9151286db5420db85eef49655090268eeb63');shutil.copyfile(extra,system/'capacidades'/extra.name)
 for name in('mundo_genesis_apd05.py','cola_local.py'):shutil.copyfile(P/'codigo/HOOKS_PI09_R03_PREPARADOS/app'/name,system/'app'/name)
 for name in FILES:
  source=P/'codigo'/name;require(source.is_file(),'Falta fuente PI09: '+name)
  if source.suffix=='.py':ast.parse(source.read_text('utf-8-sig'))
  shutil.copyfile(source,system/'capacidades'/name)
 scope={'schema':'DEE.PI09.exact_inherited_transport_scope.R01','life_id':a.vida,'source_C_tick':884835,'source_C_snapshot_sha256':view['encoded_sha256'],
  'source_C_manifest_sha256':PAIR_SHA,'literal_sources_sha256':{n:sha(SOURCE/'capacidades'/n)for n in('pi08_consulta_condicional_C_R03.py','pi08_revision_flexible_B_R01.py','pi08_consulta_condicional_C_segunda_R02.py','SELLO_PI08_C_R03.json','SELLO_PI08_B_R01.json')},
  'inherited_metadata_sha256':{k:hashlib.sha256(view['metadata'][k].encode('utf8')).hexdigest()for k in('DEE.Cognitive.PI08.conditional_sensor_register_access.C.R02','DEE.Cognitive.PI08.successive_contextual_regulation.B.R01')},
  'scope':'Administrative cloned identity only; old C/B metadata and scientific sources literal; only STATE/deps of ancestors.'}
 write(system/'capacidades/PI09_TRANSPORTE_HEREDADO_R01.json',scope)
 write(system/'capacidades/PI09_PLUGINS_R01.json',{'schema':'DEE.PI09.fixed_plugins_source_registry.R01','plugins':list(PLUGINS),'files_sha256':{n:sha(system/'capacidades'/n)for n in FILES}})
 (system/'estado/checkpoints').mkdir(parents=True);(system/'runtime').mkdir()
 wheel='dee_thinking-4.5.0-cp313-cp313-win_amd64.whl';source=C/'sistema/runtime'/wheel;checked(source,'09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c');os.link(source,system/'runtime'/wheel)
 rows=[{'file':p.relative_to(system).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(system.rglob('*'))if p.is_file()and not p.is_relative_to(system/'runtime')]
 write(dest/'SISTEMA_CODIGO_PI09.json',{'schema':'DEE.PI09.cloned_code_closure.R01','files':rows,'source_manifest_sha256':MANIFEST_SHA,'source_system':str(SOURCE),'scientific_old_B_C_sources_literal':True})
 context={'schema':'DEE.reproduction.explicit_diagnostic.v1','life':a.vida,'recipe':'PI09_EXPLICIT_FULL_C_CONTINUATION','variant':a.slug,'prefix':str(PAIR),'prefix_manifest_sha256':PAIR_SHA,'system':str(system),'python':str(PY),'product':str(C),'destination':str(dest),'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tool_sources':[{'file':n,'sha256':sha(RP/n)}for n in TOOLS],'never_select_or_promote':True,'source_code_manifest_sha256':sha(dest/'SISTEMA_CODIGO_PI09.json')}
 write(dest/'CONTEXTO_EJECUCION.json',context);write(dest/'PREPARACION_PI09.json',{'schema':'DEE.PI09.diagnostic_code_prepared.R01','life_id':a.vida,'system':str(system),'context_sha256':sha(dest/'CONTEXTO_EJECUCION.json'),'Native_executed':False,'source_C_B_metadata_not_rewritten':True})
 print(json.dumps({'prepared':True,'system':str(system),'life_id':a.vida,'files':len(rows),'Native_executed':False},ensure_ascii=False))
def import_once(a,dest,system):
 info=read(dest/'PREPARACION_PI09.json');context=dest/'CONTEXTO_EJECUCION.json';require(info['life_id']==a.vida and sha(context)==info['context_sha256'],'Contexto cambiado')
 for row in read(dest/'SISTEMA_CODIGO_PI09.json')['files']:checked(system/row['file'],row['sha256'])
 for folder in('vidas','servicios_persistentes','servicios_locales'):require(not(system/'estado'/folder/a.vida).exists(),'Identidad ya importada: no se reenvía')
 require(not(dest/'IMPORTACION_DIAGNOSTICA.json').exists(),'Ya existe resultado de importación')
 marker=P/'PI09_ROOT_NATIVE_WRITER.lock';require(not marker.exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'Hay un escritor/importador no conciliado')
 before=sha(C/'sistema/estado/ACTIVO.json');token=os.urandom(16).hex();write(marker,{'pid':os.getpid(),'token':token,'life_id':a.vida,'operation':'OFFICIAL_FULL_IMPORT_ONLY'})
 sys.path.insert(0,str(system));from app import process_control as pc
 command=[str(PY),'-I','-B','-X','utf8',str(RP/'importar_diagnostico.py'),'--contexto',str(context)]
 process=job=None;error=None;directory_proof=None;resources={};begun=time.monotonic()
 try:
  with(dest/'importar.stdout.txt').open('x',encoding='utf8')as out,(dest/'importar.stderr.txt').open('x',encoding='utf8')as err:
   process,job,name=pc.spawn_owned(command,cwd=P,stdout=out,stderr=err,memory_limit=536870912)
   while process.poll()is None:
    resources=pc.job_resources(job)
    require(time.monotonic()-begun<300,'Espera de importación agotada: conservar futuro/Job/marker sin reintentar')
    time.sleep(.1)
   require(process.returncode==0,'Falló el importador oficial: conservar estado/logs')
  imported=read(dest/'IMPORTACION_DIAGNOSTICA.json');require(imported['new_native_ticks']==0 and imported['comparison']['physical_equal']and imported['comparison']['causal_prefix_equal']and imported['principal_selected']is False,'No se verificó importación0 completa')
  pc.close_job(job);job=None
  transport=load('PI09_exact_directories',P/'codigo/directorios_pareados_PI09_R01.py')
  directory_proof=transport.materialize(system,a.vida,context,imported,process.pid,apply=True)
  require(sha(C/'sistema/estado/ACTIVO.json')==before,'Cambió A protegida')
 except Exception as exc:error={'type':type(exc).__name__,'detail':str(exc),'automatic_retry':False}
 closed=process is not None and process.poll()is not None
 proof={'schema':'DEE.PI09.actual_complete_C_import.R01','life_id':a.vida,'status':'IMPORTED_CLOSED_NO_NATIVE_TICKS'if error is None else'FAILED_IMPORT_PRESERVED','closed':closed,'error':error,'new_Native_ticks':0,'importer_Runtime_opened':process is not None,'resources':resources,'directory_transport':directory_proof,'source_pair_manifest_sha256':PAIR_SHA,'principal_A_unchanged':sha(C/'sistema/estado/ACTIVO.json')==before}
 write(dest/'IMPORTACION_PI09.json',proof)
 if error is None and closed and read(marker).get('token')==token:marker.unlink()
 if error:raise RuntimeError(error['detail'])
 print(json.dumps({'imported':True,'proof':str(dest/'IMPORTACION_PI09.json'),'new_Native_ticks':0},ensure_ascii=False))
def main():
 p=argparse.ArgumentParser();p.add_argument('--slug',required=True);p.add_argument('--vida',required=True);g=p.add_mutually_exclusive_group();g.add_argument('--preparar',action='store_true');g.add_argument('--importar',action='store_true');a=p.parse_args();dest,system=arguments(a)
 if a.preparar:prepare(a,dest,system)
 elif a.importar:import_once(a,dest,system)
 else:print(json.dumps({'mode':'PLAN_ONLY','source_pair':str(PAIR),'manifest_sha256':PAIR_SHA,'life_id':a.vida,'system':str(system),'steps':['same command --preparar (code only)','same command --importar (Root official0tick importer + exact empty dirs)','Root explicit owner only after IMPORTACION_PI09 closed'], 'Native_executed':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
