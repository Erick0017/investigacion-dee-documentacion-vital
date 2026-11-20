"""Passive OS Job I/O observer. No DEE import, request, mutation or selection.

Windows class9 Extended.IoInfo is reserved and must not be interpreted as zero
I/O. Class8 returns real lifetime accounting including terminated workers.
"""
import ctypes, datetime, hashlib, importlib.util, json
from pathlib import Path
import sys, time

def main():
    root=Path(sys.argv[1]).resolve();system=root/'sistema'
    ev=root/'evidencia/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION'
    out=ev/'MEDICION_IO_OS_R01';out.mkdir(exist_ok=False)
    spec=importlib.util.spec_from_file_location('readonly_job_os',system/'app/process_control.py')
    pc=importlib.util.module_from_spec(spec);spec.loader.exec_module(pc)
    class BasicAndIo(ctypes.Structure):
        _fields_=[('BasicInfo',pc.Accounting),('IoInfo',pc.IO)]
    journal=system/'estado/entrada_sencilla/vidas/APD03_MAIN/SESIONES.jsonl'
    sources={'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'native_ticks':0,'queries_only':'QueryInformationJobObject(handle QUERY0x4, class8)',
        'why_separate_observer':'Frozen earlier scripts queried reserved class9.IoInfo. Their zeros are not measurements of zero work. No actor or frozen script is patched.',
        'authority':['https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-queryinformationjobobject',
            'https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information',
            'https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_and_io_accounting_information'],
        'scope':'Native-owner Jobs plus their actual workers; excludes supervisor/client processes outside those Jobs. CPU/RAM total tree is recorded separately; nested counts are not added.',
        'late_attachment':'Cumulative I/O is lifetime from OS Job creation, not just from observer attachment. Phase boundaries before attachment have no class8 sample.',
        'no_new_decisional_information_to_participant':True}
    (out/'ALCANCE_Y_CORRECCION.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    handles={};last={};began=time.monotonic()
    try:
        while time.monotonic()-began<5400:
            if journal.exists():
                for line in journal.read_text(encoding='utf8').splitlines():
                    if not line:continue
                    event=json.loads(line)
                    if event.get('event')!='owned_start_paused':continue
                    name=event['job_name']
                    if name in handles:continue
                    handle=pc.K.OpenJobObjectW(0x0004,False,name)
                    if handle:handles[name]=handle
            for name,handle in handles.items():
                data=BasicAndIo()
                if not pc.K.QueryInformationJobObject(handle,8,ctypes.byref(data),ctypes.sizeof(data),None):
                    raise ctypes.WinError(ctypes.get_last_error())
                row={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    'observer_elapsed_seconds':time.monotonic()-began,'job_name':name,
                    'job_active_processes':int(data.BasicInfo.ActiveProcesses),
                    'job_total_processes':int(data.BasicInfo.TotalProcesses),
                    'cpu_user_100ns':int(data.BasicInfo.TotalUserTime),'cpu_kernel_100ns':int(data.BasicInfo.TotalKernelTime),
                    'io':{k:int(getattr(data.IoInfo,k))for k,_ in pc.IO._fields_}}
                with (out/'MUESTRAS_CLASS8.jsonl').open('a',encoding='utf8') as stream:
                    stream.write(json.dumps(row,ensure_ascii=False)+'\n')
                last[name]=row
            if (ev/'MAIN_INTEGRADO_R01/REGISTROS_VENTANA.json.gz').is_file() and handles and all(v['job_active_processes']==0 for v in last.values()):break
            time.sleep(10)
        (out/'RESULTADO.json').write_text(json.dumps({'jobs':last,'observer_elapsed_seconds':time.monotonic()-began,
            'source_unchanged':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==sources['source_sha256'],
            'new_native_ticks':0,'energy':'NO MEDIDA'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    finally:
        for handle in handles.values():pc.close_job(handle)

if __name__=='__main__':main()
