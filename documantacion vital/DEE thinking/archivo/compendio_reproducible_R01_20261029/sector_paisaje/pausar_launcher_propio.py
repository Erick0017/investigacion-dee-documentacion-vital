"""Detiene sólo el gestor propio después de terminar un mecanismo; no Native."""
from pathlib import Path
import ctypes,json,time
from ctypes import wintypes as w
ROOT_PID=68196;WORKER_PID=99488
OUT=Path(r'C:\Users\Erik\AppData\Local\Temp\DEE_R01_E03_i_51tke0\paisaje')
k=ctypes.WinDLL('kernel32',use_last_error=True);n=ctypes.WinDLL('ntdll')
k.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];k.OpenProcess.restype=w.HANDLE;k.CloseHandle.argtypes=[w.HANDLE]
k.WaitForSingleObject.argtypes=[w.HANDLE,w.DWORD];k.WaitForSingleObject.restype=w.DWORD
n.NtQueryInformationProcess.argtypes=[w.HANDLE,w.ULONG,w.LPVOID,w.ULONG,ctypes.POINTER(w.ULONG)];n.NtQueryInformationProcess.restype=w.LONG
n.NtSuspendProcess.argtypes=[w.HANDLE];n.NtSuspendProcess.restype=w.LONG
n.NtResumeProcess.argtypes=[w.HANDLE];n.NtResumeProcess.restype=w.LONG
k.TerminateProcess.argtypes=[w.HANDLE,w.UINT];k.TerminateProcess.restype=w.BOOL
def command(h):
 size=w.ULONG();n.NtQueryInformationProcess(h,60,None,0,ctypes.byref(size));data=ctypes.create_string_buffer(size.value);status=n.NtQueryInformationProcess(h,60,data,size.value,ctypes.byref(size));assert status==0
 length=ctypes.c_ushort.from_buffer(data).value;ptr=ctypes.c_void_p.from_buffer(data,8).value;return ctypes.wstring_at(ptr,length//2)
root=k.OpenProcess(0x1000|0x800|0x1|0x100000,False,ROOT_PID);worker=k.OpenProcess(0x100000|0x1000,False,WORKER_PID)
if not root or not worker:raise ctypes.WinError(ctypes.get_last_error())
record={'root_pid':ROOT_PID,'worker_pid':WORKER_PID,'manager_command':command(root),'worker_command':command(worker),'native_runtime_suspended':False,'scope':'Sólo gestor propio de reproducción y espera de procesoM101; no se alteran estados ni protocolos.'}
assert 'reproducir.py todos --sector paisaje'in record['manager_command']and str(OUT)in record['manager_command']
assert 'native M101'in record['worker_command']and str(OUT)in record['worker_command']
suspended=False
try:
 status=n.NtSuspendProcess(root);record['suspend_status']=status;assert status==0;suspended=True
 (OUT/'PAUSA_GESTOR_PROPIO.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8');print('Gestor suspendido; M101 continúa.',flush=True)
 # Espera de supervisión local acotada. Si el hijo no acaba, vuelve a dejar
 # al gestor atender su timeout original; nunca mata una simulación activa.
 status=k.WaitForSingleObject(worker,25*60*1000);record['wait_worker_status']=status
 if status==0:
  record['worker_completed_before_stop']=True;record['manager_terminated']=bool(k.TerminateProcess(root,0));suspended=False
 else:record['manager_resumed']=n.NtResumeProcess(root)==0;suspended=False
finally:
 if suspended:n.NtResumeProcess(root)
 k.CloseHandle(worker);k.CloseHandle(root)
 (OUT/'PAUSA_GESTOR_PROPIO.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(record,ensure_ascii=False),flush=True)
