"""Root-only R02 preparation/import with exact frozen historical-code option. Default PLAN.

Preparation copies code, shares the unchanged wheel and installs only exact
instrumentation/identity hooks. Import reuses the official paired importer,
one512MiB owned Job and exact empty-directory preservation. No auto Owner.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ast,hashlib,importlib.util,json,os,re,shutil,sys,time,types
P=Path(__file__).resolve().parents[1];H=P/'codigo';P9=P.with_name('PROGRESION_INTEGRADA_09');C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';RP=C/'reproducibilidad';PY=C/'motor/python313/python.exe'
PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_';PARENT='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'
TOOLS=('reproducir.py','importar_diagnostico.py','ejecutar_diagnostico.py','propietario_diagnostico.py','observador_pasivo.py')
PARSER_SHA='dbb2a5e15d70c64112d36505197f4aebf6ff7d4092972923e17cd60c10a1c873'
WHEEL_SHA='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
ANCESTORS=('DEE.Cognitive.PI09.persistent_environment.D.R02','DEE.Cognitive.PI09.selective_registered_consultation.R02','DEE.Cognitive.PI08.conditional_sensor_register_access.C.R02','DEE.Cognitive.PI08.successive_contextual_regulation.B.R01','DEE.Cognitive.PI07.regulation.environment.R03')
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def regular(p):
 for n in(p,*p.parents):need(not n.exists()or not(n.is_symlink()or getattr(n.lstat(),'st_file_attributes',0)&1024),'No linked/reparse source or target')
def load(name,path):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def args(a):
 need(re.fullmatch('[A-Z][A-Z0-9_]{0,24}',a.slug)and re.fullmatch(re.escape(PREFIX)+'[A-Z0-9_]{1,20}',a.vida),'Exact unused PI11 slug/life required')
 pair=a.prefijo.resolve(strict=True);regular(pair)
 need(pair.parent==(P/'pares').resolve()and sha(pair/'EXPORTACION_SERVICIO.json')==a.manifest_sha256,'Explicit coherent PI11 pair and actual SHA required')
 m=read(pair/'EXPORTACION_SERVICIO.json');need((m['life_id']==PARENT or m['life_id'].startswith(PREFIX))and m['physical']['N']==67 and m['physical']['tick']>=947395,'Only actual PI10/PI11 ancestry')
 if m['life_id']!=PARENT:need(a.sistema_padre is not None,'A PI11 prefix requires its explicit prepared source system')
 dest=P/'estados'/a.slug;regular(dest)
 return pair,m,dest,dest/'sistema'
def source_files(source=S):
 files=[source/'gestionar.py',source/'iniciar_sistema.ps1']
 for folder in('app','capacidades','contratos','organizaciones'):
  for base,dirs,names in os.walk(source/folder,followlinks=False):
   dirs[:]=[d for d in dirs if d not in('__pycache__','.git','estado','runtime')]
   for d in dirs:regular(Path(base)/d)
   for name in names:
    p=Path(base)/name;regular(p)
    if p.suffix.lower()in('.pyc','.pyo','.whl','.pyd','.exe','.zip','.docx','.pdf','.mp4'):continue
    need(p.stat().st_size<=10000000,'Unexpected large code resource: inspect dependency before copying')
    files.append(p)
 need(sum(p.stat().st_size for p in files)<100000000,'Bounded source closure exceeded')
 return sorted(set(files))
def patch_hooks(system):
 f=system/'app/mundo_genesis_apd05.py';text=f.read_text('utf-8-sig');before=sha(f)
 anchor='        pi10_transport.install(self.a)\n';need(text.count(anchor)==1,'Exact inherited PI10 install anchor')
 text=text.replace(anchor,anchor+'        from capacidades import pi11_identidad_heredada_R01 as pi11_identity\n        pi11_identity.install(self.a)\n')
 for method in('validate','execute'):
  anchor='    def '+method+'(self,payload):\n        row=self._eci01_row(payload)\n';need(text.count(anchor)==1,'Exact owner '+method+' anchor')
  extra="        if row is not None and str(row.get('modo','')).startswith('eci01-pi11-'):\n            from capacidades import pi11_dispatcher_R01 as pi11\n"
  if method=='validate':extra+='            pi11.validate(self.a,row)\n            return\n'
  else:extra+="            pi11.validate(self.a,row)\n            self.before_mutation('PI11_EXPLICIT_NATIVE_HABITAT')\n            value=pi11.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)\n            return {'version':pi11.VERSION,'rows':[value]}\n"
  text=text.replace(anchor,anchor+extra)
 anchor='        return result\n\n    def validate(self,payload):';need(text.count(anchor)==1,'Exact owner code closure boundary')
 text=text.replace(anchor,"        from capacidades import pi11_dispatcher_R01 as pi11\n        pi11.operational_dependencies(self.a,self.work_directory)\n        for path in (*pi11.code_files(),*pi11_identity.code_files()):\n            self.code_sha256['PI11/'+path.name]=hashlib.sha256(path.read_bytes()).hexdigest()\n"+anchor)
 anchor='    def external_uncertainty(self):\n';need(text.count(anchor)==1,'Exact uncertainty anchor')
 text=text.replace(anchor,anchor+"        from capacidades import pi11_dispatcher_R01 as pi11\n        if pi11.uncertain(self.a):return True\n")
 ast.parse(text);f.write_text(text,'utf8');rows=[{'file':'app/mundo_genesis_apd05.py','before_sha256':before,'after_sha256':sha(f)}]
 f=system/'app/cola_local.py';text=f.read_text('utf-8-sig');before=sha(f);anchor='        for row in rows:\n';need(text.count(anchor)==1,'Exact queue row anchor')
 text=text.replace(anchor,anchor+"            if str(row.get('modo','')).startswith('eci01-pi11-'):\n                from capacidades.pi11_dispatcher_R01 import validate_literal\n                validate_literal(row)\n                continue\n")
 ast.parse(text);f.write_text(text,'utf8');rows.append({'file':'app/cola_local.py','before_sha256':before,'after_sha256':sha(f)})
 return rows
def install_actor(a,dest,system):
 need(not(system/'estado/vidas'/a.vida).exists(),'Never edit imported/live candidate code')
 actor=a.actor.resolve(strict=True)if a.actor else None
 need(actor is not None and actor.parent==H.resolve()and actor.suffix=='.py'and actor.name.startswith('pi11_'),'Explicit local PI11 actor required')
 files=[H/'pi11_dispatcher_R01.py',H/'pi11_identidad_heredada_R01.py',actor]
 for f in a.dependencia or[]:
  f=f.resolve(strict=True);need(f.parent==H.resolve()and f.suffix in('.py','.json')and 'pi11' in f.name.lower(),'Explicit local PI11 dependencies only');files.append(f)
 need(len({f.name for f in files})==len(files),'Duplicate supplied dependencies')
 for f in files:
  ast.parse(f.read_text('utf-8-sig'))if f.suffix=='.py'else read(f)
  shutil.copyfile(f,system/'capacidades'/f.name)
 registry={'schema':'DEE.PI11.fixed_plugins.R01','plugins':[actor.stem],'files_sha256':{f.name:sha(system/'capacidades'/f.name)for f in files},'body_prepared':True,'policy_selection_is_Native_not_this_registry':True}
 (system/'capacidades/PI11_PLUGINS_R01.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n','utf8')
 rows=[]
 for p in source_files(system):rows.append({'file':p.relative_to(system).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
 mf=dest/'SISTEMA_CODIGO_PI11.json';value={'schema':'DEE.PI11.exact_diagnostic_code_closure.R01','files':rows,'PI11_actor_ready':True,'old_Native_scientific_sources_literal':True,'ancestor_calendars_readonly':True}
 mf.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')
 context=read(dest/'CONTEXTO_EJECUCION.json');context['source_code_manifest_sha256']=sha(mf);context['PI11_actor_ready']=True;(dest/'CONTEXTO_EJECUCION.json').write_text(json.dumps(context,ensure_ascii=False,indent=2)+'\n','utf8')
 prep=read(dest/'PREPARACION_PI11.json');prep.update(context_sha256=sha(dest/'CONTEXTO_EJECUCION.json'),final_code_manifest_sha256=sha(mf),PI11_actor_ready=True);(dest/'PREPARACION_PI11.json').write_text(json.dumps(prep,ensure_ascii=False,indent=2)+'\n','utf8')
 return mf
def prepare(a,pair,m,dest,system):
 need(not dest.exists(),'Fresh unused code destination only')
 verifier=load('PI10_exact_standard_pair_validator',S/'app/importacion_emparejada.py');verifier.verify_export(pair)
 parser=load('PI10_code_scope_passive_parser',RP/'observador_pasivo.py');view=parser.snapshot_view(pair/'VIDA.deetsnap.gz');need(view['encoded_sha256']==m['snapshot_sha256'],'Paired snapshot differs')
 current=read(S/'estado/ACTIVO.json');need(current['life_id']==PARENT and current['tick']==947395 and current['snapshot_sha256']=='fd7372b7f2adc9040866fab8adfaca0d79e0bd18e997c0abc0651fe4fa3c23dc','Main advanced: reconcile before cloning an older cut')
 source=S
 if m['life_id']!=PARENT:
  source=a.sistema_padre.resolve(strict=True);regular(source);need(source.parent.parent==(P/'estados').resolve()and source.name=='sistema'and not(source/'estado/ACTIVO.json').exists(),'Exact isolated PI10 source only')
  source_system=source;source_card=read(source/'estado/vidas'/m['life_id']/'VIDA.json')
  if a.codigo_padre is not None:
   capsule=a.codigo_padre.resolve(strict=True);regular(capsule);need(capsule.parent==H.resolve(),'Exact bounded frozen code capsule only')
   binding=read(capsule/'CONGELACION_CODIGO_PREFIJO_PI10_R02.json');cm=capsule/'SISTEMA_CODIGO.json'
   need(binding['schema']=='DEE.PI10.neutral_prefix_code_binding.R02'and binding['source_system']==str(source_system)and binding['source_life_id']==m['life_id']and binding['source_tick']==m['physical']['tick']and binding['source_snapshot_sha256']==m['snapshot_sha256']and binding['pair_manifest_sha256']==a.manifest_sha256 and binding['capsule_manifest_sha256']==sha(cm)and binding['source_code_unchanged']is True,'Exact neutral code/prefix provenance binding required')
   for row in read(cm)['files']:need(sha(capsule/row['file'])==row['sha256'],'Frozen neutral code changed')
   history=source_system/'estado/vidas'/m['life_id']/'HISTORIA.jsonl';matches=[r for r in(read_line for read_line in (json.loads(line)for line in history.read_text('utf8').splitlines()))if r.get('snapshot_sha256')==m['snapshot_sha256']]
   need(matches,'Frozen prefix must remain a real historical snapshot of this source life; no reconstruction')
   original=read(pair/'procedencia/VIDA_ORIGINAL.json');need(original['life_id']==m['life_id']and original['snapshot_sha256']==m['snapshot_sha256']and original['physical']==m['physical'],'Original full paired source card mismatch')
   source=capsule
  else:need(source_card['snapshot_sha256']==m['snapshot_sha256']and source_card['physical']==m['physical'],'Historical source advanced: supply its exact frozen --codigo-padre, never rewind it')
 sources=source_files(source);before={str(f):sha(f)for f in sources};system.mkdir(parents=True)
 for f in sources:
  out=system/f.relative_to(source);out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,out)
 need(before=={str(f):sha(f)for f in sources},'Parent code changed during copy')
 old=read(source/'capacidades/PI10_TRANSPORTE_ANCESTRAL_R01.json')
 scope={**old,'life_id':a.vida,'role':a.rol,'PI11_source_main_life_id':PARENT,'PI11_source_main_tick':current['tick'],'PI11_source_main_snapshot_sha256':current['snapshot_sha256'],'PI11_source_immediate_life_id':m['life_id'],'PI11_source_immediate_tick':m['physical']['tick'],'PI11_source_immediate_snapshot_sha256':m['snapshot_sha256'],'PI11_source_pair_manifest_sha256':a.manifest_sha256,'old_D_R02_B_C_history_not_rewritten':True}
 scopefile=system/'capacidades/PI10_TRANSPORTE_ANCESTRAL_R01.json';scopefile.write_text(json.dumps(scope,ensure_ascii=False,indent=2)+'\n','utf8')
 experiment=system/'capacidades/PI10_EXPERIMENTO_R02.json';v=read(experiment);v['life_id']=a.vida;experiment.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
 oldregistry=system/'capacidades/PI10_PLUGINS_R01.json';v=read(oldregistry)
 for f in(scopefile,experiment):
  if f.name in v['files_sha256']:v['files_sha256'][f.name]=sha(f)
 oldregistry.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
 if 'from capacidades import pi11_identidad_heredada_R01 as pi11_identity'not in(system/'app/mundo_genesis_apd05.py').read_text('utf-8-sig'):hooks=patch_hooks(system)
 else:hooks=[{'copied_exact_PI11_parent':str(source),'no_duplicate_patching':True}]
 (system/'estado/checkpoints').mkdir(parents=True);(system/'runtime').mkdir()
 wheel='dee_thinking-4.5.0-cp313-cp313-win_amd64.whl';need(sha(S/'runtime'/wheel)==WHEEL_SHA,'Official shared engine changed');os.link(S/'runtime'/wheel,system/'runtime'/wheel)
 context={'schema':'DEE.reproduction.explicit_diagnostic.v1','life':a.vida,'recipe':'PI11_EXPLICIT_FULL_CURRENT_REAL2_CONTINUATION','variant':a.slug,'prefix':str(pair),'prefix_manifest_sha256':a.manifest_sha256,'system':str(system),'python':str(PY),'product':str(C),'destination':str(dest),'tool_sources':[{'file':name,'sha256':sha(RP/name)}for name in TOOLS],'no_implicit_selection_or_promotion':True,'root_separate_adoption_required':a.rol=='real','PI10_stock_preserved':4,'new_lot_not_a_reset':True}
 write(dest/'CONTEXTO_EJECUCION.json',context);write(dest/'PREPARACION_PI11.json',{'schema':'DEE.PI10.diagnostic_code_prepared.R01','life_id':a.vida,'role':a.rol,'system':str(system),'source_parent':m['life_id'],'source_tick':m['physical']['tick'],'source_snapshot_sha256':m['snapshot_sha256'],'parent_code_hashes':before,'localized_hook_delta':hooks,'Native_executed':False,'PI11_actor_ready':False})
 mf=install_actor(a,dest,system);print(json.dumps({'code_prepared':True,'life_id':a.vida,'system':str(system),'manifest_sha256':sha(mf),'actor_ready':bool(a.actor),'Native':0}))
def import_once(a,dest,system):
 need(Path(sys.executable).resolve()==PY.resolve(),'Root official Python only')
 prep=read(dest/'PREPARACION_PI11.json');mf=dest/'SISTEMA_CODIGO_PI11.json';context=dest/'CONTEXTO_EJECUCION.json'
 need(prep['life_id']==a.vida and prep['PI11_actor_ready']and sha(context)==prep['context_sha256']and sha(mf)==a.codigo_cerrado_sha256,'Actual ready actor/transport/code closure required')
 for row in read(mf)['files']:need(sha(system/row['file'])==row['sha256'],'Prepared source changed '+row['file'])
 for kind in('vidas','servicios_locales','servicios_persistentes'):need(not(system/'estado'/kind/a.vida).exists(),'Import identity already exists; never resend')
 marker=P/'PI11_ROOT_NATIVE_WRITER.lock';need(not marker.exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'One Root writer required')
 output=dest/'IMPORTACION_PI11.json';need(not output.exists(),'Prior partial import preserved');budget=read(P/'REGISTRO_CAMPANA.json')['budget'];need(budget['owned_Native_job_memory_bytes']==536870912,'Keep actual owner limit')
 saved=list((P/'estados').glob('*/sistema/estado/vidas/*/VIDA.json'));need(len(saved)+1<=budget['new_worlds_all'],'Prospective actual world budget exceeded')
 need(datetime.now(timezone.utc)<datetime.fromisoformat(budget['new_experimental_uses_cutoff_utc']).astimezone(timezone.utc),'No new world after prospective cutoff')
 protected=[S/'estado/ACTIVO.json',S/'estado/vidas'/PARENT/'VIDA.json',S/read(S/'estado/vidas'/PARENT/'VIDA.json')['snapshot']];before={str(p):sha(p)for p in protected}
 write(marker,{'pid':os.getpid(),'life_id':a.vida,'phase':'COMPLETE_PAIRED_IMPORT_ONLY','new_Native_ticks':0})
 sys.path.insert(0,str(system));from app import process_control as pc
 command=[str(PY),'-I','-B','-X','utf8',str(RP/'importar_diagnostico.py'),'--contexto',str(context)];started=time.monotonic();error=None;directory_proof=None;resources={};proc=job=None
 try:
  with(dest/'importar.stdout.txt').open('x',encoding='utf8')as out,(dest/'importar.stderr.txt').open('x',encoding='utf8')as err:
   proc,job,name=pc.spawn_owned(command,cwd=P,stdout=out,stderr=err,memory_limit=536870912)
   warned=False
   while proc.poll()is None:
    try:
     resources=pc.job_resources(job)
     if time.monotonic()-started>=300 and not warned:
      warned=True;write(dest/'IMPORTACION_HORIZONTE_VIVO_PI10_R01.json',{'schema':'DEE.PI10.import_horizon_live_handle_retained.R01','pid':proc.pid,'memory_limit_bytes':536870912,'automatic_retry':False,'unlogged_kill':False,'next':'Root must inspect this owned importer. Supervisor keeps its handle until actual exit.'});print('Owned importer remains live at horizon; handle retained, no retry or kill.',flush=True)
     time.sleep(.1)
    except KeyboardInterrupt:
     print('Root interruption noted; live importer handle retained until exact exit.',flush=True)
   need(proc.returncode==0,'Official importer failed; preserve partial state and logs')
  imported=read(dest/'IMPORTACION_DIAGNOSTICA.json');need(imported['new_native_ticks']==0 and imported['comparison']['physical_equal']and imported['comparison']['causal_prefix_equal']and imported['principal_selected']is False,'Exact full0tick official import required')
  pc.close_job(job);job=None
  original=P9/'codigo/directorios_pareados_PI09_R01.py';src=original.read_text('utf-8-sig');need("life.startswith('ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_')"in src,'Exact directory-transport identity anchor changed')
  src=src.replace("life.startswith('ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_')","life.startswith('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_')")
  mod=types.ModuleType('PI10_literal_directory_transport_identity_only');mod.__file__=str(original);exec(compile(src,str(original)+':PI10_path_identity_only','exec'),mod.__dict__);mod.P=P
  directory_proof=mod.materialize(system,a.vida,context,imported,proc.pid,apply=True)
 except Exception as exc:error={'type':type(exc).__name__,'detail':str(exc),'automatic_retry':False}
 unchanged=before=={p:sha(Path(p))for p in before};closed=proc is not None and proc.poll()is not None
 record={'schema':'DEE.PI11.actual_complete_current_D_import.R01','life_id':a.vida,'closed':closed,'error':error,'new_Native_ticks':0,'directory_transport':directory_proof,'protected_main_unchanged':unchanged,'resources':resources,'importer_PID':proc.pid if proc else None,'source_manifest_sha256':a.manifest_sha256}
 write(output,record)
 if error is None and closed and unchanged:marker.unlink()
 if error:raise RuntimeError(error['detail'])
 print(json.dumps({'imported':True,'proof':str(output),'life_id':a.vida,'new_Native_ticks':0,'main_unchanged':unchanged}))
def main(a):
 pair,m,dest,system=args(a)
 if a.preparar:prepare(a,pair,m,dest,system)
 elif a.instalar_actor:
  need(dest.exists()and a.actor is not None,'Existing code-only destination and explicit actor required');mf=install_actor(a,dest,system);print(json.dumps({'actor_ready':True,'manifest_sha256':sha(mf),'Native':0}))
 elif a.importar:import_once(a,dest,system)
 else:print(json.dumps({'mode':'PLAN_ONLY','life_id':a.vida,'system':str(system),'parent':PARENT,'tick':m['physical']['tick'],'next':['--preparar --actor <reviewed.py> --dependencia <each.py/json>','--importar --codigo-cerrado-sha256 ACTUAL (Root only)','Root explicit Owner; no auto start or selection'],'Native':0}))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--slug',required=True);ap.add_argument('--vida',required=True);ap.add_argument('--rol',choices=('real','none','yoked','calibration','reproduction'),default='real');ap.add_argument('--prefijo',type=Path,required=True);ap.add_argument('--manifest-sha256',required=True);ap.add_argument('--sistema-padre',type=Path);ap.add_argument('--codigo-padre',type=Path);ap.add_argument('--actor',type=Path);ap.add_argument('--dependencia',type=Path,action='append');ap.add_argument('--codigo-cerrado-sha256');g=ap.add_mutually_exclusive_group();g.add_argument('--preparar',action='store_true');g.add_argument('--instalar-actor',action='store_true');g.add_argument('--importar',action='store_true');main(ap.parse_args())
