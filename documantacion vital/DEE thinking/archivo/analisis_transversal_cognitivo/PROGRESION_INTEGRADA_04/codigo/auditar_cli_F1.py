"""Audited runner of actual stdlib manager/RP/F1 sources, including children."""
from pathlib import Path
import datetime,json,os,runpy,subprocess,sys
HELPER=Path(__file__).resolve();P4=HELPER.parents[1];PRODUCT=P4.parents[2]/'DEE Cognitive 2.0'
target=Path(sys.argv[1]).resolve();arguments=sys.argv[2:];folder=Path(os.environ['PI04_F1_AUDIT_DIR']).resolve()
allowed={PRODUCT/'sistema/gestionar.py',PRODUCT/'reproducibilidad/reproducir.py',PRODUCT/'reproducibilidad/observadores/F1_PI04/RECALCULAR_F1.py'}
if target not in allowed:raise ValueError('Audit target not allowed')
events={'target':str(target),'arguments':arguments,'opened_project_files':[],'blocked_operations':[],'child_commands':[]}
def hook(event,args):
 if event=='import'and isinstance(args[0],str)and(args[0]in('app','_native')or args[0].startswith(('app.','dee_thinking'))):
  events['blocked_operations'].append(['import',args[0]]);raise RuntimeError('DEE/app/Native import forbidden')
 if event.startswith('sqlite3.connect'):
  events['blocked_operations'].append(['sqlite3.connect']);raise RuntimeError('No SQLite connection in read-only F1 modes')
 if event=='open'and isinstance(args[0],(str,bytes)):
  path=Path(args[0]).resolve()
  if path.is_relative_to(PRODUCT/'sistema/estado'):
   events['blocked_operations'].append(['state_open',str(path)]);raise RuntimeError('No operational state access in F1 audit')
  if path.is_relative_to(PRODUCT):events['opened_project_files'].append(str(path))
original_run=subprocess.run
def audited_run(command,*args,**kwargs):
 if not isinstance(command,(list,tuple))or kwargs.get('shell'):raise RuntimeError('Unbounded command forbidden')
 candidates=[i for i,x in enumerate(command)if str(x).endswith(('reproducir.py','RECALCULAR_F1.py'))]
 if len(candidates)!=1:raise RuntimeError('Unexpected child command')
 i=candidates[0];child=Path(command[i]).resolve()
 if child not in allowed:raise RuntimeError('Unexpected child source')
 events['child_commands'].append([str(x)for x in command])
 wrapped=[str(command[0]),'-I','-B','-X','utf8',str(HELPER),str(child),*[str(x)for x in command[i+1:]]]
 return original_run(wrapped,*args,**kwargs)
sys.addaudithook(hook);subprocess.run=audited_run
sys.argv=[str(target),*arguments]
try:runpy.run_path(str(target),run_name='__main__')
finally:
 events['DEE_or_app_modules']=[x for x in sys.modules if x in('app','_native')or x.startswith(('app.','dee_thinking'))]
 events['at']=datetime.datetime.now(datetime.timezone.utc).isoformat();events['new_Native_ticks']=0
 with (folder/(str(os.getpid())+'.json')).open('x',encoding='utf-8')as f:json.dump(events,f,ensure_ascii=False,indent=2)
