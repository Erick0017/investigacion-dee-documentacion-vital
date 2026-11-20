"""Test timeout containment on our two disposable processes only."""
import argparse,ctypes,json,os,subprocess,sys,time
from ctypes import wintypes
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path);p.add_argument('--child',type=Path);p.add_argument('--grandchild',action='store_true');a=p.parse_args()
    if a.grandchild:time.sleep(20);return
    if a.child:
        child=subprocess.Popen([sys.executable,'-I',__file__,'--grandchild'],creationflags=subprocess.CREATE_NO_WINDOW)
        a.child.write_text(json.dumps({'parent_pid':os.getpid(),'child_pid':child.pid}),encoding='utf-8');child.wait();return
    sys.path.insert(0,str(a.root));from supervise40 import run,put
    marker=a.root/'validation/resumption_supervisor_processes.json';r=run(a.root,'resume_supervisor_timeout',[sys.executable,'-I',__file__,'--child',str(marker)],2)
    ids=json.loads(marker.read_text());k=ctypes.WinDLL('kernel32',use_last_error=True);k.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];k.OpenProcess.restype=wintypes.HANDLE;k.GetExitCodeProcess.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)];k.CloseHandle.argtypes=[wintypes.HANDLE];states={}
    for label,pid in ids.items():
        handle=k.OpenProcess(0x1000,False,pid)
        if not handle:states[label]={'absent_or_closed':ctypes.get_last_error()==87,'error':ctypes.get_last_error()}
        else:
            code=wintypes.DWORD();ok=k.GetExitCodeProcess(handle,ctypes.byref(code));k.CloseHandle(handle);states[label]={'exited':bool(ok and code.value!=259),'code':code.value}
    assert r['exit_code']==124 and r['owned_windows_job']['assigned']
    assert all(x.get('exited') or x.get('absent_or_closed') for x in states.values()),states
    put(a.root/'validation/RESUMPTION_SUPERVISION_CHECK.json',{'timeout_contained_own_process_tree':True,'job':r,'processes':states});print('OWNED_JOB_TIMEOUT_VERIFIED')
if __name__=='__main__':main()
