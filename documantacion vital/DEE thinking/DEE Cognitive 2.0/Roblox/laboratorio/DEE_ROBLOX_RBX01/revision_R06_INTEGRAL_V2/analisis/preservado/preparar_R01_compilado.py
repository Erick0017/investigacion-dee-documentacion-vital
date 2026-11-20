"""Explicit stdlib-only preparation of one complete closed DEV4 descendant.

Does not import DEE, open a Native owner, execute the importer or advance ticks.
A fresh destination contains a byte-preserved complete paired prefix, copied
operational code, prospective adapter and context for the official import0 API.
"""
from pathlib import Path, PurePosixPath
import argparse, ast, hashlib, json, os, re, shutil, sqlite3, stat, time

HERE=Path(__file__).resolve().parent
SOURCE_LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_DEV'
SOURCE_TICK=953651
SOURCE_SNAPSHOT='38a7c2d6ac2911ce06dd4d181cb3f697b68ac09dd892fa5041c35dfcea93ec92'
SOURCE_CARD='f68ffd0f8522b4a1d1aa3943e6872b7a140d1866e9dcf161d7ab8924f86d68ee'
SOURCE_WORLD='7813c015dbf7a8b0eef33006ce0a3864b591359c68609051fec746a6d3890435'
SOURCE_CLOSED='d516d54bea666bbf3f371e4781662a2ba49068273324c0a7f4dfddcb875b5e97'
START=1794780780;LAST_Q1=1794798600;CUTOFF=1794802380
LIFE_RE=r'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V2_(MAIN|CTRL[0-9]?|LOAD[123])'
BUNDLE=('rbx06_native_integral.py','rbx06_identity_integral.py','rbx06_funciones_native.py')
WHEEL_SHA='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'

def need(ok,text):
 if not ok:raise ValueError(text)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def write(p,v):
 with Path(p).open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def regular(path):
 path=Path(path).absolute()
 for part in(path,*path.parents):
  if part.exists()or part.is_symlink():
   m=part.lstat();need(not stat.S_ISLNK(m.st_mode)and not(getattr(m,'st_file_attributes',0)&1024),'No links/reparse points')
 return path

def member(root,name):
 need(type(name)is str and '\\'not in name and ':'not in name,'Portable relative member')
 rel=PurePosixPath(name);need(not rel.is_absolute()and rel.parts and not any(x in('.','..')for x in rel.parts),'Safe member')
 p=regular(Path(root).joinpath(*rel.parts));need(p.resolve().is_relative_to(Path(root).resolve()),'Member escaped root');return p

def tree(root):
 root=regular(root);files=[];empty=[]
 if not root.exists():return files,empty
 for folder,dirs,names in os.walk(root,followlinks=False):
  folder=regular(folder);dirs.sort();names.sort()
  for name in dirs:regular(folder/name)
  if not dirs and not names:empty.append(folder.relative_to(root).as_posix())
  for name in names:
   p=regular(folder/name);need(p.is_file(),'Regular files only');files.append((p,p.relative_to(root).as_posix()))
 return files,empty

def closed_source(system,card,proof):
 need(proof.get('ownerClosed')is True and proof.get('writerDrained')is True and proof.get('exit_code')==0,'Actual closed source owner required')
 need(proof.get('lifeId')==SOURCE_LIFE,'Exact source lifecycle')
 need(card.get('life_id')==SOURCE_LIFE and card.get('world_id')==SOURCE_LIFE and card.get('profile')=='fisica_directa','Actual complete source identity')
 need(card['physical']['N']==67 and card['physical']['tick']==SOURCE_TICK and card['snapshot_sha256']==SOURCE_SNAPSHOT,'Exact reached DEV4 cut')
 life=system/'estado/vidas'/SOURCE_LIFE
 need(not(life/'FUTURO_INTERRUMPIDO.json').exists()and not(system/'estado/locks'/(SOURCE_LIFE+'.lock')).exists(),'Source has no active/interrupted writer')
 last=json.loads((life/'HISTORIA.jsonl').read_text('utf8').splitlines()[-1])
 need(last['snapshot_sha256']==SOURCE_SNAPSHOT and last['tick']==SOURCE_TICK,'Committed source history/card agree')
 db=system/'estado/servicios_persistentes'/SOURCE_LIFE/'cola.sqlite3';regular(db)
 need(db.is_file(),'Whole persistent queue required')
 for suffix in('-wal','-journal'):
  q=Path(str(db)+suffix);need(not q.exists()or q.stat().st_size==0,'Do not copy a live WAL/journal')
 before=sha(db);con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  need(con.execute('PRAGMA integrity_check').fetchone()[0]=='ok','Source queue integrity')
  need(con.execute("SELECT COUNT(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]==0,'No ambiguous/pending operations can be omitted')
  owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0]);need(owner.get('running')is False and owner.get('tick')==SOURCE_TICK,'Closed matching queue owner')
 finally:con.close()
 need(sha(db)==before,'Read-only source queue changed');return db,before

def prepare(product,destination,life,freeze,freeze_sha,feedback_arm='real',teacher_mode='paired'):
 product=regular(Path(product).resolve(strict=True));dest=regular(Path(destination).absolute())
 need(dest.parent.resolve()==HERE and not dest.exists(),'Fresh absent direct native/ destination required')
 need(re.fullmatch(LIFE_RE,life)and len(life)<=91,'Explicit new integral identity only')
 need(START<=time.time()<LAST_Q1,'Prospective6h scope not current; never restart the clock')
 for context in HERE.glob('*/CONTEXTO_EJECUCION.json'):need(read(context).get('life')!=life,'Never reuse an already prepared life ID')
 freeze=regular(Path(freeze).resolve(strict=True));need(sha(freeze)==freeze_sha,'Pinned prospective source freeze')
 pins=read(freeze);need(pins.get('sealed')is True,'Root must seal code before preparation')
 need(pins.get('native_start_epoch')==START and pins.get('last_new_episode_epoch')==LAST_Q1 and pins.get('native_cutoff_epoch')==CUTOFF,'Exact prospective epochs')
 sources=pins.get('native_sources_sha256',{})
 for name in BUNDLE:need(sources.get(name)==sha(HERE/'bundle'/name),'Unfrozen bundle source '+name)
 need(feedback_arm in('real','noaversive')and teacher_mode in('paired','desync','omitted'),'Declared controls only')
 need(not life.endswith('_MAIN')or feedback_arm=='real'and teacher_mode=='paired','Main uses actual experience')
 old=HERE.parents[1]/'revision_R05_C02';system_source=old/'native/DEV/sistema'
 card_path=system_source/'estado/vidas'/SOURCE_LIFE/'VIDA.json';proof_path=old/'evidencia/DEV_REAPERTURA_R04/SOURCE_OWNER_CLOSED.json';world_path=old/'evidencia/DEV_REAPERTURA_R04/WORLD_FINAL.json'
 need(sha(card_path)==SOURCE_CARD and sha(proof_path)==SOURCE_CLOSED and sha(world_path)==SOURCE_WORLD,'Exact closed parent witnesses')
 card=read(card_path);proof=read(proof_path);world=read(world_path)
 s=world['S'];need(world['native_tick']==SOURCE_TICK and world['boundary']['native_phase']=='IDLE'and world['boundary']['completed_opportunities']==4 and world['boundary']['next_opportunity']==5,'Exact complete World/native cursor')
 need(s['numberA']==4 and s['finalCode']==5 and s['inventoryResource']is True and s['station']==5 and s['permissionStock']==196,'Carry-in is actual A4/B5/resource1, never fabricated/reset')
 db,dbsha=closed_source(system_source,card,proof);snapshot=member(system_source,card['snapshot']);need(sha(snapshot)==SOURCE_SNAPSHOT,'Native snapshot changed')
 operational=[]
 for name in('app','capacidades','contratos','organizaciones','runtime'):
  files,_=tree(system_source/name)
  for p,rel in files:
   if '__pycache__'not in p.parts and p.suffix.lower()not in('.pyc','.pyo'):operational.append((p,name+'/'+rel,sha(p)))
 for name in('gestionar.py','iniciar_sistema.ps1'):
  p=system_source/name
  if p.is_file():operational.append((p,name,sha(p)))
 wheels=[p for p,_,h in operational if p.suffix=='.whl'and h==WHEEL_SHA];need(len(wheels)==1,'Exactly one unchanged official wheel')
 worker=system_source/'estado/servicios_locales'/SOURCE_LIFE;service=db.parent
 workers,worker_empty=tree(worker);results,result_empty=tree(service/'resultados')
 need((worker/'RBX02_NATIVE_C02/events.jsonl').is_file(),'Original Native phase history required')
 before={str(p):h for p,_,h in operational};before.update({str(p):sha(p)for p in(card_path,snapshot,db,proof_path,world_path)})
 dest.mkdir();prefix=dest/'PREFIJO_DEV4_COMPLETO';prefix.mkdir();system=dest/'sistema';system.mkdir()
 shutil.copyfile(snapshot,prefix/'VIDA.deetsnap.gz');shutil.copyfile(db,prefix/'cola.sqlite3')
 for group,base_name in((workers,'artefactos_trabajador'),(results,'resultados')):
  for source,rel in group:
   target=member(prefix,base_name+'/'+rel);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
 for group,base_name in((worker_empty,'artefactos_trabajador'),(result_empty,'resultados')):
  for rel in group:member(prefix,base_name+('/'+rel if rel else'')).mkdir(parents=True,exist_ok=True)
 files,_=tree(prefix);members=[{'file':rel,'bytes':p.stat().st_size,'sha256':sha(p)}for p,rel in files]
 manifest={'schema':'DEE.persistent_service.paired_export.v1','life_id':SOURCE_LIFE,'profile':'fisica_directa','backend':'mente_unificada',
  'native_snapshot':'VIDA.deetsnap.gz','snapshot_sha256':SOURCE_SNAPSHOT,'physical':card['physical'],'members':members,'queue_journal_required':True,
  'source_record':{'life_id':SOURCE_LIFE,'world_id':SOURCE_LIFE,'parent':card.get('parent')},'no_engine_or_WHL':True,
  'not_a_new_cognitive_acquisition':True,'closed_source_export_without_native_load':True,'source_queue_sha256':dbsha,
  'empty_directories_preserved':['artefactos_trabajador'+('/'+x if x else'')for x in worker_empty]+['resultados'+('/'+x if x else'')for x in result_empty]}
 write(prefix/'EXPORTACION_SERVICIO.json',manifest)
 for source,rel,h in operational:
  target=member(system,rel);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);need(sha(target)==h,'Copied code differs')
 (system/'estado/checkpoints').mkdir(parents=True);(system/'estado/locks').mkdir()
 for name in BUNDLE:shutil.copyfile(HERE/'bundle'/name,system/'capacidades'/name)
 changed={}
 for rel in('app/mundo_genesis_apd05.py','app/cola_local.py'):
  target=system/rel;text=target.read_text('utf-8-sig');oldsha=sha(target)
  need('rbx02_native_C02'in text,'Existing C02 integration missing')
  text=text.replace('rbx02_native_C02','rbx06_native_integral').replace('rbx02_identity_C02','rbx06_identity_integral')
  ast.parse(text);target.write_text(text,encoding='utf8');changed[rel]={'before':oldsha,'after':sha(target)}
 transport=system/'capacidades/PI10_TRANSPORTE_ANCESTRAL_R01.json';v=read(transport);oldsha=sha(transport);v['life_id']=life;v['role']='rbx01';transport.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8');changed['capacidades/'+transport.name]={'before':oldsha,'after':sha(transport)}
 registry=system/'capacidades/PI10_PLUGINS_R01.json';v=read(registry);oldsha=sha(registry);v['files_sha256'][transport.name]=sha(transport);registry.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8');changed['capacidades/'+registry.name]={'before':oldsha,'after':sha(registry)}
 scope={'schema':'DEE.RBX01.fixed_native_scope.INTEGRAL.V2.R01','sealed':True,'life_id':life,'role':'main'if life.endswith('_MAIN')else'load'if'_LOAD'in life else'control',
  'source_life_id':SOURCE_LIFE,'source_tick':SOURCE_TICK,'source_snapshot_sha256':SOURCE_SNAPSHOT,'source_pair_manifest_sha256':sha(prefix/'EXPORTACION_SERVICIO.json'),
  'code_scope_manifest_sha256':freeze_sha,'sources_sha256':{n:sha(system/'capacidades'/n)for n in BUNDLE},'sensor_codec':'products_v1','parent_completed_opportunities':4,
  'max_cycles':24,'max_ticks_per_cycle':4096,'max_total_ticks':98304,'max_raw_support':10000,'monitor_tick_block':16,'max_permission_stock':200,
  'native_start_utc_epoch':START,'last_new_cycle_utc_epoch':LAST_Q1,'native_cutoff_utc_epoch':CUTOFF,'feedback_arm':feedback_arm,'teacher_mode':teacher_mode,
  'input_codec':{'Q1':'1+zone+8key+16resource+32lastFailure+64A+128B+256freshB+512AVersion+16384goalDelivery; max32766',
  'Q2':'unchanged paid0/1/2 or omission; Q2 decisions are observed even while prepared host locomotion chooses EXIT0',
  'function':'word-only Native recall -> fixed sign/opcode -> Native FI128; actual A transported unchanged'},
  'prepared_locomotion':'Host EXIT0 for new opportunities1..18; actual Native Q2 for new19..24; fixed before evaluation',
  'new_anatomy':False,'promotion':False,'raw_clocks_banks_edited':False}
 write(system/'capacidades/RBX06_NATIVE_SCOPE_INTEGRAL_V2.json',scope)
 host_source=HERE/'servicio_eventos_integral_v2.py'
 need(sources.get(host_source.name)==sha(host_source),'Host service must be frozen with Native preparation')
 shutil.copyfile(host_source,system/'app'/host_source.name)
 host={'schema':'DEE.RBX01.INTEGRAL.V2.host_scope.v1','sealed':True,'system':str(system),'life':life,
  'event_driven':True,'single_initial_resume':True,'native_cutoff_utc_epoch':CUTOFF,'immutable_source_cache':True,
  'host_sources_sha256':{name:sha(system/'app'/name)for name in('servicio_eventos_integral_v2.py','cache_fuentes_C02.py')},
  'inherited_sources_sha256':{name:sha(system/'app'/name)for name in('servicio_persistente.py','mundo_genesis_apd05.py','cola_local.py','lives.py','process_control.py')},
  'new_native_ticks_when_idle':0,'prepared_support_not_autonomous_regulation':True}
 write(system/'app/HOST_INTEGRAL_V2.json',host)
 shutil.copyfile(world_path,dest/'WORLD_PADRE_DEV4.json');write(dest/'VIDA_PADRE_DEV4.json',card)
 context={'schema':'DEE.RBX01.official_import_context.INTEGRAL.V2.R01','product':str(product),'system':str(system),'life':life,'prefix':str(prefix),
  'prefix_manifest_sha256':sha(prefix/'EXPORTACION_SERVICIO.json'),'source_life_id':SOURCE_LIFE,'source_tick':SOURCE_TICK,
  'source_snapshot_sha256':SOURCE_SNAPSHOT,'source_world':str(dest/'WORLD_PADRE_DEV4.json'),'source_world_sha256':SOURCE_WORLD,
  'source_record':str(dest/'VIDA_PADRE_DEV4.json'),'source_code_directory':str(system_source),
  'tool_sources':[{'file':n,'sha256':sha(product/'reproducibilidad'/n)}for n in('importar_diagnostico.py','observador_pasivo.py')]}
 write(dest/'CONTEXTO_EJECUCION.json',context)
 need(before=={p:sha(Path(p))for p in before},'Original closed source changed during copying; destination preserved as partial')
 need(sha(prefix/'cola.sqlite3')==dbsha and sha(prefix/'VIDA.deetsnap.gz')==SOURCE_SNAPSHOT,'Paired copies preserve original bytes')
 report={'schema':'DEE.RBX01.prepare_integral_v2.R01','life_id':life,'parent_life_id':SOURCE_LIFE,'parent_tick':SOURCE_TICK,
  'new_native_ticks':0,'Native_imported':False,'owner_opened':False,'official_import_not_yet_executed':True,
  'complete_prefix':str(prefix),'source_members':len(members),'source_bytes':sum(x['bytes']for x in members),'source_hashes_before_after_equal':True,
  'source_snapshot_sha256':SOURCE_SNAPSHOT,'source_world_sha256':SOURCE_WORLD,'code_changed_only_in_copy':changed,
  'carry_in_resource':1,'carry_in_products':{'A':4,'B':5},'operational_main_modified':False,
  'next_action':'Root: run import0_integral_v2.py explicitly, then verify full physical/causal equality before owner.'}
 write(dest/'PREPARACION_INTEGRAL_V2.json',report);return report

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--product',type=Path,required=True);p.add_argument('--destination',type=Path,required=True);p.add_argument('--life',required=True)
 p.add_argument('--freeze-manifest',type=Path,required=True);p.add_argument('--freeze-sha256',required=True)
 p.add_argument('--feedback-arm',choices=('real','noaversive'),default='real');p.add_argument('--teacher-mode',choices=('paired','omitted','desync'),default='paired')
 a=p.parse_args();print(json.dumps(prepare(a.product,a.destination,a.life,a.freeze_manifest,a.freeze_sha256,a.feedback_arm,a.teacher_mode),ensure_ascii=False,indent=2))
