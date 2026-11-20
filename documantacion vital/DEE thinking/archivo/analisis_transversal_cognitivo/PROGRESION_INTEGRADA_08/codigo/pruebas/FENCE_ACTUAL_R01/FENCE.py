from pathlib import Path
import builtins, importlib.abc, json, os, runpy, sys, sysconfig, traceback
x=Path(sys.argv[1]).resolve(strict=True);out=Path(sys.argv[2]).resolve(strict=True)
jobs=json.loads(Path(sys.argv[3]).read_text('utf-8'));audit_file=Path(sys.argv[4]).resolve()
base=Path(sys.base_prefix).resolve();denied=[];imports=[];counts={};results=[]
def inside(p,r):
 try:p.relative_to(r);return True
 except ValueError:return False
def std(p):return inside(p,base)and 'site-packages'not in p.parts
def check(value,write=False):
 if isinstance(value,int):return
 p=Path(value).resolve()
 area='extraction'if inside(p,x)else'destination'if inside(p,out)else'stdlib'if std(p)else None
 if area is None or(write and area!='destination'):
  denied.append({'path':str(p),'write':write});raise PermissionError('Extraction fence denied '+str(p))
 counts[area]=counts.get(area,0)+1
class ImportFence(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  root=fullname.split('.')[0]
  if root in('dee_thinking','dee_universe_v27','app','capacidades','_native')or root.startswith('dee_kernel'):
   imports.append(fullname);raise ImportError('DEE/application import denied')
def hook(event,args):
 if event=='open':
  mode=args[1]if len(args)>1 else'r';flags=args[2]if len(args)>2 else 0
  writing=(isinstance(mode,str)and any(c in mode for c in'wa+x'))or(isinstance(flags,int)and bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)))
  check(args[0],writing)
 elif event in('os.listdir','os.scandir')and args and args[0]is not None:check(args[0])
 elif event in('os.remove','os.rmdir','os.mkdir','os.rename','os.replace'):
  for value in args[:2]if event in('os.rename','os.replace')else args[:1]:check(value,True)
 elif event.startswith(('socket.','subprocess.','ctypes.dlopen','os.system','os.exec','os.spawn')):
  denied.append({'event':event});raise PermissionError('Process/network/native loading denied')
sys.meta_path.insert(0,ImportFence());sys.addaudithook(hook)
error=None
try:
 for job in jobs:
  script=x.joinpath(*Path(job['script']).parts);check(script)
  argv=[v.replace('{EXTRACTION}',str(x)).replace('{OUTPUT}',str(out))for v in job['argv']]
  sys.argv=[str(script),*argv]
  try:runpy.run_path(str(script),run_name='__main__')
  except SystemExit as e:
   if e.code not in(None,0):raise
  results.append({'script':job['script'],'successful_CLI_exit':True})
except BaseException as e:
 error={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()}
finally:
 value={'schema':'DEE.PI08.extraction_access_fence.v1','denied':denied,'DEE_or_app_imports':imports,'open_counts':counts,'jobs':results,'error':error,'new_Native_ticks':0,'no_original_source_access':not denied and not imports}
 audit_file.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if error is not None:raise SystemExit(2)
