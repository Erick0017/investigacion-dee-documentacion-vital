from pathlib import Path
import ctypes,ctypes.wintypes as w,json,os,subprocess
B=Path(__file__).resolve().parent.parent;K=ctypes.WinDLL('kernel32',use_last_error=True);N=ctypes.WinDLL('ntdll');K.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];K.OpenProcess.restype=w.HANDLE;K.CloseHandle.argtypes=[w.HANDLE];N.NtQueryInformationProcess.argtypes=[w.HANDLE,w.ULONG,w.LPVOID,w.ULONG,ctypes.POINTER(w.ULONG)];N.NtQueryInformationProcess.restype=w.LONG
class US(ctypes.Structure):_fields_=[('Length',w.USHORT),('MaximumLength',w.USHORT),('Buffer',ctypes.c_void_p)]
raw=subprocess.check_output(['powershell.exe','-NoProfile','-Command','Get-Process python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],text=True)
selected=[];handles=[]
for token in raw.split():
    pid=int(token)
    if pid==os.getpid():continue
    h=K.OpenProcess(0x1000,False,pid)
    if not h:continue
    needed=w.ULONG();N.NtQueryInformationProcess(h,60,None,0,ctypes.byref(needed));buffer=ctypes.create_string_buffer(needed.value or 32768);status=N.NtQueryInformationProcess(h,60,buffer,len(buffer),ctypes.byref(needed))
    line=ctypes.wstring_at(ctypes.cast(buffer,ctypes.POINTER(US)).contents.Buffer,ctypes.cast(buffer,ctypes.POINTER(US)).contents.Length//2) if status>=0 else ''
    text=line.replace('/','\\').lower()
    if 'extraccion_02\\dee_compendio_reproducible\\reproducir.py' in text and 'verificacion_core_e02' in text and 'todos' in text and '--sector core' in text:
        selected.append({'pid':pid,'exact_command_line':line});handles.append(h)
    else:K.CloseHandle(h)
if not selected:raise RuntimeError('No own E02 launcher identified; nothing terminated')
for row in selected:
    run=subprocess.run([str(Path(os.environ['SystemRoot'])/'System32/taskkill.exe'),'/PID',str(row['pid']),'/T','/F'],capture_output=True,text=True,errors='replace');row.update(taskkill_returncode=run.returncode,stdout=run.stdout,stderr=run.stderr)
for h in handles:K.CloseHandle(h)
report={'scope':'Only exact own E02 launcher tree; C03 and originals do not match.','reason':'M034 NativePASS plus4complete-state comparisons already preserved; redundant M035 prefix stopped by host after that completed result. Not cognitive failure.','own_processes':selected,'M035_prefix':'HOST_ABORT_INCOMPLETE_NOT_COUNTED','original_Cognitive_modified':False}
(B/'VERIFICACION_CORE_E02/HOST_ABORT_E02.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(report,ensure_ascii=False))
