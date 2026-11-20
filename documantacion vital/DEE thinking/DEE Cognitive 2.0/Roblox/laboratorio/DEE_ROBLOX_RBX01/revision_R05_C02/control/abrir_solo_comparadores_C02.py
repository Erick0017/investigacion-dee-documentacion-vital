"""Root-only bounded opening of one frozen comparator Studio editor.

No Play, Native, model, MCP, credentials, auth or account changes. Import and
--help are inert. Only two closed local RBXLX filenames are accepted. A launch
intent is durable before Popen; an ambiguous launch is never retried silently.
"""
from pathlib import Path
import argparse,ctypes,datetime,hashlib,json,os,subprocess,time
ROOT=Path(__file__).resolve().parents[1]
STUDIO=Path(r'C:\Users\Erik\AppData\Local\Roblox\Versions\version-63eb6055af4e4688\RobloxStudioBeta.exe')
SCENES={'PROGRAMMED':'DEE_RBX01_C02_R02_PROGRAMMED.rbxlx',
        'CONVENTIONAL_AI':'DEE_RBX01_C02_R02_CONVENTIONAL_AI.rbxlx'}
MIN_FREE_BYTES=1_800_000_000
MANIFEST='protocolo/FUENTES_CONGELADAS_EVALUACION_R03.json'
REGISTRY='control/APERTURAS_COMPARADORES_C02.jsonl'
def need(ok,message):
 if not ok:raise RuntimeError(message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def safe(path,root=ROOT):
 p=Path(path).absolute();base=Path(root).resolve()
 need(p==base or p.is_relative_to(base),'R05 subtree only')
 for q in(p,*p.parents):
  need(not q.is_symlink()and not(q.exists()and getattr(q.lstat(),'st_file_attributes',0)&1024),'No linked/reparse paths')
 return p.resolve()
def validate_scene(participant,root=ROOT):
 need(participant in SCENES,'Closed participant allowlist only')
 manifest=safe(Path(root)/MANIFEST,root);m=json.loads(manifest.read_text('utf-8-sig'))
 need(m.get('target')==18 and m.get('boundary')==6 and m.get('reserve')==[13,18],'Exact prospective18/6 scenario')
 entry=m['scenes'][participant];need(entry['file']==SCENES[participant],'Fixed scene filename only')
 scene=safe(Path(root)/'mundo'/SCENES[participant],root)
 need(scene.is_file()and scene.suffix=='.rbxlx','Existing local RBXLX only')
 need(scene.stat().st_size==entry['bytes']and sha(scene)==entry['sha256'],'Frozen scene bytes/hash mismatch')
 fp=m.get('scenarioFingerprint');need(isinstance(fp,str)and len(fp)==64 and all(c in'0123456789abcdef'for c in fp),'Frozen fingerprint missing')
 return dict(scene=scene,sha256=entry['sha256'],bytes=entry['bytes'],scenarioFingerprint=fp,
             manifest=str(manifest),manifest_sha256=sha(manifest),participant=participant)
class MemoryStatus(ctypes.Structure):
 _fields_=[('dwLength',ctypes.c_ulong),('dwMemoryLoad',ctypes.c_ulong),
           ('ullTotalPhys',ctypes.c_ulonglong),('ullAvailPhys',ctypes.c_ulonglong),
           ('ullTotalPageFile',ctypes.c_ulonglong),('ullAvailPageFile',ctypes.c_ulonglong),
           ('ullTotalVirtual',ctypes.c_ulonglong),('ullAvailVirtual',ctypes.c_ulonglong),
           ('ullAvailExtendedVirtual',ctypes.c_ulonglong)]
def host_memory():
 need(os.name=='nt','Windows-only launcher')
 s=MemoryStatus();s.dwLength=ctypes.sizeof(s)
 need(ctypes.WinDLL('kernel32',use_last_error=True).GlobalMemoryStatusEx(ctypes.byref(s)),'Win32 memory reading failed')
 return dict(measured_utc=utc(),total_physical_bytes=s.ullTotalPhys,available_physical_bytes=s.ullAvailPhys,
             memory_load_percent=s.dwMemoryLoad,scope='HOST_RAM_NOT_DEE_MEMORY')
def process_identity(pid):
 k=ctypes.WinDLL('kernel32',use_last_error=True);k.OpenProcess.restype=ctypes.c_void_p
 h=k.OpenProcess(0x1000,False,int(pid))
 if not h:return None
 try:
  code=ctypes.c_ulong();need(k.GetExitCodeProcess(ctypes.c_void_p(h),ctypes.byref(code)),'ExitCode unavailable')
  if code.value!=259:return None
  size=ctypes.c_ulong(32768);buf=ctypes.create_unicode_buffer(size.value)
  need(k.QueryFullProcessImageNameW(ctypes.c_void_p(h),0,buf,ctypes.byref(size)),'Executable identity unavailable')
  times=[ctypes.c_ulonglong()for _ in range(4)]
  need(k.GetProcessTimes(ctypes.c_void_p(h),*(ctypes.byref(x)for x in times)),'Process start identity unavailable')
  epoch=times[0].value/10_000_000-11_644_473_600
  return dict(pid=int(pid),executable=str(Path(buf.value)),creation_filetime=times[0].value,
              start_utc=datetime.datetime.fromtimestamp(epoch,datetime.timezone.utc).isoformat())
 finally:k.CloseHandle(ctypes.c_void_p(h))
def check_registry(rows,identity):
 intents={};finished=set()
 for row in rows:
  if row.get('kind')=='LAUNCH_INTENT':intents[row['launch_id']]=row
  elif row.get('kind')in('PROCESS_STARTED','LAUNCH_FAILED_NO_PROCESS'):
   finished.add(row['launch_id'])
   if row.get('kind')=='PROCESS_STARTED':
    live=identity(row['process']['pid'])
    need(live is None,'A previously opened comparator PID is still live; reconcile it instead of opening another')
 unresolved=set(intents)-finished
 need(not unresolved,'Unresolved prior GUI launch intent; no automatic retry')
 return dict(prior_launches=len(intents),prior_live_pids=0,unresolved_intents=0)
def new_json(path,value):
 with Path(path).open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def run(a):
 need(a.root_run,'Explicit --root-run required')
 info=validate_scene(a.participant);out=safe(a.output)
 result_path=out.with_name(out.stem+'_RESULTADO.json')
 need(out.is_relative_to(ROOT/'evidencia')and out.suffix=='.json'and not out.exists(),'Fresh evidence JSON in R05 only')
 need(not result_path.exists(),'Fresh result JSON required before GUI launch')
 need(out.parent.is_dir(),'Use an existing evidence directory')
 need(STUDIO.is_file()and STUDIO.name=='RobloxStudioBeta.exe','Fixed official Studio executable unavailable')
 need(not STUDIO.is_symlink()and not(STUDIO.lstat().st_file_attributes&1024),'Linked Studio executable denied')
 registry=safe(ROOT/REGISTRY)
 rows=[]if not registry.exists()else[json.loads(x)for x in registry.read_text('utf8').splitlines()if x.strip()]
 prior=check_registry(rows,process_identity)
 studio_hash=sha(STUDIO)
 memory=host_memory();need(memory['available_physical_bytes']>MIN_FREE_BYTES,'Require more than1.8GB measured free physical RAM')
 launch_id=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_'+a.participant
 def append(kind,**fields):
  with registry.open('a',encoding='utf8')as f:
   f.write(json.dumps(dict(utc=utc(),kind=kind,launch_id=launch_id,participant=a.participant,**fields),ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
 intent=dict(schema='DEE.RBX01.C02.comparator_GUI_open.R01',launch_id=launch_id,requested_utc=utc(),
             participant=a.participant,scene=str(info['scene']),scene_sha256=info['sha256'],scene_bytes=info['bytes'],
             fingerprint=info['scenarioFingerprint'],manifest=info['manifest'],manifest_sha256=info['manifest_sha256'],
             Studio_executable=str(STUDIO),Studio_sha256=studio_hash,memory_before=memory,prior_registry=prior,
             window_request='STARTUPINFO STARTF_USESHOWWINDOW SW_HIDE',Play_calls=0,Native_calls=0,MCP_calls=0,model_calls=0)
 # Exclusive evidence file is also a launch reservation: the same output cannot
 # be used twice. Root is sole launcher. The durable journal detects unknowns.
 new_json(out,intent);append('LAUNCH_INTENT',output=str(out),scene=intent['scene'],scene_sha256=intent['scene_sha256'])
 startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
 try:
  p=subprocess.Popen([str(STUDIO),str(info['scene'])],cwd=info['scene'].parent,shell=False,
                     startupinfo=startup,creationflags=getattr(subprocess,'CREATE_NEW_PROCESS_GROUP',0))
 except OSError as error:
  append('LAUNCH_FAILED_NO_PROCESS',error_type=type(error).__name__);raise
 # No automatic relaunch if Studio exits or hands off to another process.
 ident=process_identity(p.pid)
 if ident is None:
  append('PROCESS_EXITED_OR_HANDOFF_UNVERIFIED',pid=p.pid,returncode=p.poll())
  raise RuntimeError('GUI launch returned an exited/handoff process; preserve intent and reconcile via Studio inventory')
 need(Path(ident['executable']).resolve()==STUDIO.resolve(),'Started executable mismatch; no process is stopped automatically')
 append('PROCESS_STARTED',process=ident,scene=intent['scene'],output=str(out))
 result=dict(intent,opened_process=ident,recorded_utc=utc(),status='EDITOR_PROCESS_STARTED_PLAY_NOT_REQUESTED',
             memory_after=host_memory(),window_actual_visibility_not_verified=True,
             source_scene_unchanged=sha(info['scene'])==info['sha256'],registry=str(registry))
 need(result['source_scene_unchanged'],'Frozen scene changed externally during launch')
 new_json(result_path,result);return result
def parser():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root-run',action='store_true',required=True)
 p.add_argument('--participant',choices=tuple(SCENES),required=True);p.add_argument('--output',type=Path,required=True);return p
if __name__=='__main__':print(json.dumps(run(parser().parse_args()),ensure_ascii=False,indent=2))
