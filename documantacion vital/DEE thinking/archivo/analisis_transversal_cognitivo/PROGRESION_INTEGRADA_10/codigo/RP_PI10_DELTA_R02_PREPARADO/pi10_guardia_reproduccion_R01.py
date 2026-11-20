"""Stable standard-RP PI10 material guard: finite18,512MiB, no policy.

Installed beside reproducir.py, never in an actor. Only fixed literals reach
the original published driver. Two batches7+11 preserve the declared reopen
boundary. No campaign path/current-principal ID is an execution dependency.
"""
from pathlib import Path,PurePosixPath
from datetime import datetime,timezone
import argparse,ast,hashlib,importlib.util,json,os,re,runpy,subprocess,sys,time,types
HERE=Path(__file__).resolve().parent;RID='pi10_consulta18_familia_desde_P0_T922374_R01';PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RPF_';INITIAL=922374;LIMIT=536870912;BOUND=36288
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_new(p,v):
 with Path(p).open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def log(dest,value):
 with(dest/'SUPERVISION_FAMILIA_PI10_R01.jsonl').open('a',encoding='utf8')as f:f.write(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),**value},ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
def load(name,path):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def regular(p):
 for x in(p,*p.parents):need(not x.exists()or not(x.is_symlink()or getattr(x.lstat(),'st_file_attributes',0)&1024),'No linked/reparse reproduction path')
def closed(context,dest,stage):
 life=context['life'];s=dest/'sistema';cardfile=s/'estado/vidas'/life/'VIDA.json'
 if not cardfile.is_file():return False
 card=read(cardfile);db=s/'estado/servicios_persistentes'/life/'cola.sqlite3'
 if any(Path(str(db)+x).exists()and Path(str(db)+x).stat().st_size for x in('-wal','-journal'))or(s/'estado/locks'/(life+'.lock')).exists()or(cardfile.parent/'FUTURO_INTERRUMPIDO.json').exists():return False
 import sqlite3
 con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':return False
  owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])
  if owner.get('running')is not False or con.execute("SELECT COUNT(*)FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]:return False
 finally:con.close()
 if stage=='import':
  f=dest/'IMPORTACION_DIAGNOSTICA.json'
  return f.is_file()and read(f)['life']==life and read(f)['new_native_ticks']==0 and read(f)['comparison']['physical_equal']and read(f)['comparison']['causal_prefix_equal']
 f=dest/'RESULTADO_REPRODUCCION.json'
 return f.is_file()and read(f).get('status')=='COMPLETED'and read(f).get('owner_closed_coherently')is True
def preserve_empty_directories(context,dest):
 s=dest/'sistema';life=context['life'];need(closed(context,dest,'import'),'Exact complete closed import0 before directory-only preservation');pair=Path(context['prefix']).resolve(strict=True);m=read(pair/'EXPORTACION_SERVICIO.json');need(sha(pair/'EXPORTACION_SERVICIO.json')==context['prefix_manifest_sha256'],'Paired source changed');worker=s/'estado/servicios_locales'/life;service=s/'estado/servicios_persistentes'/life;cardfile=s/'estado/vidas'/life/'VIDA.json';card=read(cardfile);critical=[cardfile,s/card['snapshot'],service/'cola.sqlite3'];before={str(p):sha(p)for p in critical};created=[]
 for name in sorted(m['empty_directories_preserved'],key=lambda x:(len(PurePosixPath(x).parts),x)):
  rel=PurePosixPath(name);need(not rel.is_absolute()and '\\'not in name and ':'not in name and all(x not in('.','..')for x in rel.parts),'Exact safe source directory')
  if rel.parts[0]=='artefactos_trabajador':target=worker.joinpath(*rel.parts[1:])
  elif rel.parts[0]=='resultados':target=service.joinpath(*rel.parts)
  else:raise ValueError('Only declared worker/result source directories')
  regular(target)
  if target.exists():need(target.is_dir(),'Directory occupied by file');continue
  source=pair.joinpath(*rel.parts);regular(source);need(source.is_dir()and not any(p.is_file()for p in source.rglob('*'))and target.parent.is_dir(),'Missing data/ancestor is not repaired')
  target.mkdir();created.append(name)
 need(before=={str(p):sha(p)for p in critical},'Directory-only preservation altered physical/SQLite bytes');value={'schema':'DEE.PI10.RP.exact_source_empty_directories.v1','declared':len(m['empty_directories_preserved']),'created':created,'critical_unchanged':True,'new_Native_ticks':0,'new_Native_inputs':0,'files_written_to_state':0};write_new(dest/'DIRECTORIOS_FAMILIA_PI10_R01.json',value)
def run_supervised(api,args):
 need(args.receta==RID and args.variante=='real18'and args.material is True and re.fullmatch(re.escape(PREFIX)+r'[A-Z0-9]{1,10}',args.vida),'Explicit fresh PI10 real18 material family only');recipe=api.recipe(RID);guard=recipe['material_supervisor'];need(guard.get('schema')=='DEE.PI10.RP.owned_finite18.v1'and guard.get('sha256')==sha(Path(__file__))and guard.get('memory_limit_bytes')==LIMIT and guard.get('Native_bound')==BOUND,'Exact frozen512MiB/18episode guard contract');dest=api.fresh_destination(args.destino);saved_run=subprocess.run
 # The old RP manager still performs the copy/import/driver/registry/lock
 # transactions. This wrapper changes only the two child process launches.
 sys.path.insert(0,str(api.PRODUCT/'sistema'));from app import process_control as pc
 def owned_run(command,*pos,**kw):
  need(not pos and isinstance(command,list)and Path(command[0]).resolve()==(api.PRODUCT/'motor/python313/python.exe').resolve(),'Exact existing Python child command only');need(command[-2:]==['--contexto',str(dest/'CONTEXTO_EJECUCION.json')],'Fixed new diagnostic context only')
  stage='import'if str(HERE/'importar_diagnostico.py')in command else'driver'if str(HERE/'ejecutar_diagnostico.py')in command else None;need(stage is not None,'No other process/provider in this recipe');context=read(dest/'CONTEXTO_EJECUCION.json')
  if stage=='driver':command=[command[0],'-I','-B','-X','utf8',str(Path(__file__)),'--driver-context',str(dest/'CONTEXTO_EJECUCION.json')]
  need(not kw.get('shell')and kw.get('stdout')is not None and kw.get('stderr')is not None,'Fixed captured nonshell child only');proc,job,name=pc.spawn_owned(command,cwd=dest,stdout=kw['stdout'],stderr=kw['stderr'],memory_limit=LIMIT);start=time.monotonic();last=-10;warned=False
  log(dest,{'kind':'OWNED_NATIVE_STAGE_STARTED','stage':stage,'pid':proc.pid,'job':name,'memory_limit_bytes':LIMIT,'guard_sha256':sha(Path(__file__))})
  while True:
   try:
    resources=pc.job_resources(job)
    if time.monotonic()-last>=3:log(dest,{'kind':'OWNED_NATIVE_RESOURCES','stage':stage,'pid':proc.pid,'elapsed_seconds':time.monotonic()-start,**resources});last=time.monotonic()
    code=proc.poll();active=resources.get('job_active_processes',0)
    if code is not None and active==0:break
    if code==0 and active==1 and closed(context,dest,stage):
     log(dest,{'kind':'EXPLICIT_COHERENT_IDLE_BRIDGE_CLOSE','stage':stage,'pending_requests':0,'completed_saved_state_verified':True,'only_remaining_owned_idle_processes':1});pc.close_job(job);job=None;break
    if time.monotonic()-start>=1800 and not warned:warned=True;log(dest,{'kind':'HORIZON_REACHED_LIVE_HANDLE_RETAINED','stage':stage,'forced_kill':False,'automatic_retry':False});print('PI10 owned stage remains live; handle retained, no retry.',flush=True)
    time.sleep(.2)
   except KeyboardInterrupt:log(dest,{'kind':'INTERRUPT_LIVE_HANDLE_RETAINED','automatic_retry':False})
  code=proc.wait(timeout=1)
  if job is not None:pc.close_job(job)
  log(dest,{'kind':'OWNED_NATIVE_STAGE_FINISHED','stage':stage,'pid':proc.pid,'exit_code':code,'elapsed_seconds':time.monotonic()-start})
  if code==0 and stage=='import':preserve_empty_directories(context,dest)
  return subprocess.CompletedProcess(command,code)
 subprocess.run=owned_run;api._PI10_FAMILY_GUARD_ACTIVE=True
 try:return api.run_material(args)
 finally:subprocess.run=saved_run;api._PI10_FAMILY_GUARD_ACTIVE=False
def driver(context_file):
 context_file=Path(context_file).resolve(strict=True);dest=context_file.parent;c=read(context_file);recipe=c['fixed_recipe'];need(c['recipe']==RID and c['variant']=='real18'and recipe['material_supervisor']['sha256']==sha(Path(__file__)),'Exact finite family context');batches=recipe['variants']['real18']['batches'];need([len(b)for b in batches]==[9,12],'Exact ADMIT+7EP+STATE /11EP+STATE batches');steps=[s for batch in batches for s in batch];modes=[s['literal']['modo']for s in steps];need(modes==['eci01-pi10-admitir']+['eci01-pi10-episodio']*7+['eci01-pi10-estado']+['eci01-pi10-episodio']*11+['eci01-pi10-estado'],'Fixed eighteen actual episodes only')
 source=HERE/'propietario_diagnostico.py';toolpins={r['file']:r['sha256']for r in c['tool_sources']};need(sha(source)==toolpins[source.name],'Published owner source changed');text=source.read_text('utf-8-sig');anchor="'--max-segundos','7200'";need(text.count(anchor)==1,'Published finite-owner command changed');text=text.replace(anchor,"'--max-segundos','1800'");ast.parse(text);service=types.ModuleType('propietario_diagnostico');service.__file__=str(source);exec(compile(text,str(source)+':PI10_fixed_finite_host_horizon_only','exec'),service.__dict__);sys.modules['propietario_diagnostico']=service;original=service.Owner.material;index=0;cursor=INITIAL;started=time.monotonic();record={'schema':'DEE.PI10.RP.fixed18_driver_guard.v1','initial_tick':INITIAL,'Native_bound':BOUND,'rows':[],'actor_inputs_or_decoder_changed':False,'expected_values_passed_to_actor':False};out=dest/'GUARDIA_DRIVER_FAMILIA_PI10_R01.json'
 def save():
  tmp=out.with_name(out.name+'.WRITING');tmp.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8');os.replace(tmp,out)
 def material(owner,identifier,literal,*pos,**kw):
  nonlocal index,cursor
  need(index<len(steps)and time.monotonic()-started<1800,'Finite material input/time limit reached; close and preserve');step=steps[index];need(identifier==c['life']+'_'+step['label']and literal==step['literal']and kw.get('feedback','omit')==step.get('feedback','omit')and kw.get('actuator','closed')==step.get('actuator','closed')and 'actual_integer_binding'not in step,'Exact fixed literal/transport only');value=original(owner,identifier,literal,*pos,**kw);delta=value['after_tick']-value['before_tick'];bound=2016 if literal['modo']=='eci01-pi10-episodio'else 0
  record['rows'].append({'index':index,'label':step['label'],'id':identifier,'before_tick':value['before_tick'],'after_tick':value['after_tick'],'actual_ticks':delta,'max_ticks':bound});save();need(value['before_tick']==cursor and 0<=delta<=bound and value['after_tick']-INITIAL<=BOUND,'Unexpected Native advance/horizon; preserve exact future');cursor=value['after_tick'];index+=1;return value
 service.Owner.material=material;save();sys.argv=[str(HERE/'ejecutar_diagnostico.py'),'--contexto',str(context_file)]
 try:runpy.run_path(str(HERE/'ejecutar_diagnostico.py'),run_name='__main__')
 except SystemExit as exc:record.update(status='COMPLETED_DRIVER'if exc.code in(None,0)and index==21 else'STOPPED_PRESERVED',exit_code=exc.code,final_tick=cursor,new_Native_ticks=cursor-INITIAL,completed_steps=index);save();raise
 except BaseException as exc:record.update(status='STOPPED_PRESERVED',error=repr(exc),final_tick=cursor,new_Native_ticks=cursor-INITIAL,completed_steps=index,automatic_retry=False);save();raise
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--driver-context',type=Path,required=True);driver(ap.parse_args().driver_context)
