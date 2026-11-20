"""File-only map of the preserved final Native18 experiment, never a backup.

Hashes the complete closed native/MAIN_R02 tree without copying its450MB. Reads
existing World/card/closure reports and selected shared runtime files. Does not
open SQLite, import DEE, invoke a process, or extend an execution deadline.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,sys,time
ROOT=Path(__file__).resolve().parents[1];PRODUCT=ROOT.parents[2]
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_MAIN_R02'
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
 p=Path(p);before=p.stat();h=hashlib.sha256()
 with p.open('rb')as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 after=p.stat();need((before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),'File changed during hash')
 return h.hexdigest()
def load(path,name):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def run(a):
 start=time.monotonic();paths=load('control/path_guard_C02_R03.py','_C02_file_only_map_paths')
 guard=paths.PathGuard(ROOT);dest=guard.safe(ROOT/'native/MAIN_R02')
 out=Path(a.output);out=out if out.is_absolute()else ROOT/out;out=guard.safe(out,exists=False)
 need(out.is_relative_to(ROOT/'evidencia')and not out.exists(),'Fresh C02 evidence map only')
 folder=ROOT/'evidencia/MAIN_R02_PERIODO_02'
 locator_paths=[dest/'CONTEXTO_EJECUCION.json',dest/'sistema/estado/vidas'/LIFE/'VIDA.json',
   folder/'WORLD_FINAL.json',folder/'SOURCE_OWNER_CLOSED.json',folder/'RESULTADO.json',folder/'AFTER.json',
   folder/'WORLD_RESTORE_COMPARISON.json',ROOT/'protocolo/CODE_SCOPE_C02_R02.json']
 frozen={str(p):sha(guard.safe(p))for p in locator_paths}
 context,card,world,close,result,after,restore,scope=[read(p)for p in locator_paths]
 need(context['life']==close['lifeId']==LIFE and card['physical']['N']==67 and card['physical']['tick']==975547,'Exact final experimental Native cut')
 need(close['ownerClosed']is True and close['writerDrained']is True and close['exit_code']==0
  and close['source_journal_event']['exit_code']==0 and close['source_journal_event']['final_status']['running']is False,'Existing official owner closure required')
 need(result.get('owner_closed')is True and result.get('writer_drained')is True and result.get('status')=='HORIZON_CLOSED','Actual completed horizon closure required')
 need(world['native_life_id']==LIFE and world['native_tick']==975547 and world['boundary']['completed_opportunities']==18
  and world['boundary']['next_opportunity']==19 and world['S']['completedCycles']==18,'Full18 World required')
 transport=after['bridge'];need(transport['session']['id']==world['bridge']['session_id']and transport['session']['server_id']==world['bridge']['server_id']
  and transport['session']['status']=='STOPPED'and transport['feedback_operations_completed']==18
  and transport['pending']==transport['uncertain']==transport['unacknowledged_actions']==transport['unacknowledged_tools']==0,'Existing settled18 bridge report required')
 need(after['card']['snapshot_sha256']==card['snapshot_sha256']and restore.get('equal_with_declared_geometry_tolerance')is True
      and restore.get('differences')==[],'Saved final card / actual prior World JSON restore witness mismatch')
 manifest=paths.scan_files(dest,guard,sha,100000,2000000000)
 # This shared runtime is referenced, never copied. These are selected anchors,
 # not a claim of exhaustive hash coverage of the whole CPython distribution.
 names=['motor/DEPENDENCIAS_DISTRIBUCION_ORIGEN.json','motor/python313/python.exe','motor/python313/python313.dll',
  'motor/python313/python313.zip','motor/python313/site-packages/dee_thinking/_native.cp313-win_amd64.pyd',
  'motor/python313/site-packages/dee_thinking-4.5.0.dist-info/METADATA','reproducibilidad/propietario_diagnostico.py']
 runtime=[]
 for name in names:
  p=PRODUCT/name;need(p.is_file(),'Shared required runtime anchor absent: '+name)
  runtime.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
 private=read(ROOT/'configuracion_privada/main_r02.json');db=ROOT/'configuracion_privada'/private['databaseFile']
 bridge_files=[]
 for suffix in('','-wal','-shm','-journal'):
  p=Path(str(db)+suffix)
  bridge_files.append(dict(path=str(p),exists=p.exists(),bytes=p.stat().st_size if p.exists()else None,sha256=sha(p)if p.is_file()else None))
 need(all(sha(Path(p))==h for p,h in frozen.items()),'Final source report/card/World changed concurrently');guard.recheck()
 value=dict(schema='DEE.RBX01.C02.final_local_continuation_map.R01',inspected_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
  experiment_identity=dict(life=LIFE,N=67,T=975547,adopted_as_Cognitive_principal=False,scope='Preserved C02 experimental branch; protected product principal is not replaced.'),
  import_context=context,Native_root_locator=str(dest),Native_root_manifest=manifest,
  World=dict(path=str(folder/'WORLD_FINAL.json'),bytes=(folder/'WORLD_FINAL.json').stat().st_size,sha256=frozen[str(folder/'WORLD_FINAL.json')],completed=18,next_opportunity=19),
  source_locators=[dict(path=p,sha256=h,bytes=Path(p).stat().st_size)for p,h in frozen.items()],
  final_snapshot_sha256=card['snapshot_sha256'],physical=card['physical'],
  closed_owner_report=dict(path=str(folder/'SOURCE_OWNER_CLOSED.json'),cache_wall_utc=close['source_journal_event']['final_status'].get('wall_utc'),
   historical_closure_not_instantaneous_observation=True),
  bridge_files=bridge_files,bridge_session=transport['session'],bridge_closed_report=transport,
  shared_runtime_anchors=runtime,shared_runtime_root=str(PRODUCT/'motor/python313'),runtime_coverage='Selected required anchors only; whole shared runtime remains local.',
  clock_contract='Original Native cutoff1794738600 remains unchanged. This map is not permission to execute a new Native trajectory.',
  pair_status='Final native root + original final World + closed bridge remain local. File map is not a sealed copy, executable backup, new reopen or acquisition reproduction.',
  Native_imports=0,Native_ticks=0,MCP_calls=0,HTTP_calls=0,model_calls=0,SQLite_connections=0,
  files_copied=0,elapsed_seconds=time.monotonic()-start,path_guard=guard.stats())
 with out.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
 return dict(map=str(out),bytes=out.stat().st_size,sha256=sha(out),native_files=len(manifest['files']),native_bytes=manifest['bytes'],Native_ticks=0,files_copied=0)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
 print(json.dumps(run(p.parse_args()),indent=2))
