"""Root-only bounded import0 batch; no ticks or world owners in this supervisor."""
from pathlib import Path
import argparse, ctypes, datetime, json, os, subprocess, sys, time
ROOT=Path(__file__).resolve().parents[1]
PRODUCT=ROOT.parents[2]
ROLES=('CTRL1','LOAD1','LOAD2','LOAD3','PILOT')
LATEST_START=1794852000  #18:00UTC, prospective setup margin, not an engine limit.
END=1794863220

class Memory(ctypes.Structure):
    _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong),
        ('totalPhys',ctypes.c_ulonglong),('availPhys',ctypes.c_ulonglong),
        ('totalPage',ctypes.c_ulonglong),('availPage',ctypes.c_ulonglong),
        ('totalVirtual',ctypes.c_ulonglong),('availVirtual',ctypes.c_ulonglong),
        ('availExtended',ctypes.c_ulonglong)]

def available():
    m=Memory();m.length=ctypes.sizeof(m)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
        raise OSError('Cannot measure host memory')
    return m.availPhys

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--execute-root-only',action='store_true')
    a=p.parse_args()
    if not a.execute_root_only:raise ValueError('Explicit Root execution required')
    out=ROOT/'control/IMPORTACIONES_PRE_NATIVE_R01'
    if out.exists()or time.time()>=LATEST_START:raise ValueError('Fresh bounded batch only')
    # Three additional512MiBJobs plus a3.5GiB host reserve. MAIN is separately owned.
    initial=available()
    if initial < (3.5+1.5)*1024**3:raise ValueError('Insufficient measured free RAM')
    for role in ROLES:
        d=ROOT/'native'/role
        if not (d/'CONTEXTO_EJECUCION.json').is_file():raise ValueError('FS preparation missing: '+role)
        if any((d/x).exists()for x in ('IMPORT0_JOB.json','IMPORTACION_DIAGNOSTICA.json','IMPORT0_HORIZONTE_FS_R02.json')):
            raise ValueError('Prior import must be reconciled, not replayed: '+role)
    out.mkdir();events=out/'EVENTS.jsonl'
    def record(kind,**v):
        with events.open('a',encoding='utf8')as f:
            f.write(json.dumps({'utc':now(),'kind':kind,**v},ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
    record('BATCH_STARTED',roles=ROLES,additional_parallel_max=3,free_RAM_bytes=initial,Native_ticks=0)
    pending=list(ROLES);running={};results=[]
    while pending or running:
        for role,(proc,stdout,stderr,started)in list(running.items()):
            code=proc.poll()
            if code is not None:
                stdout.close();stderr.close()
                row={'role':role,'pid':proc.pid,'exit_code':code,'wall_seconds':time.monotonic()-started}
                results.append(row);record('IMPORT0_SUPERVISOR_CLOSED',**row);del running[role]
        while pending and len(running)<3:
            if time.time()>=LATEST_START:
                record('UNSTARTED_DEADLINE',roles=pending);pending=[];break
            if available()<3.5*1024**3:
                record('UNSTARTED_MEMORY_GUARD',roles=pending,available_RAM_bytes=available());pending=[];break
            role=pending.pop(0);d=ROOT/'native'/role
            stdout=(out/(role+'.stdout.txt')).open('xb');stderr=(out/(role+'.stderr.txt')).open('xb')
            cmd=[sys.executable,'-I','-B',str(ROOT/'native/import0_v3_R02_horizonte_FS.py'),
                '--execute-root-only','--product',str(PRODUCT),'--destination',str(d),
                '--native-cutoff-utc-epoch',str(END)]
            proc=subprocess.Popen(cmd,cwd=ROOT,stdout=stdout,stderr=stderr)
            running[role]=(proc,stdout,stderr,time.monotonic())
            record('IMPORT0_SUPERVISOR_STARTED',role=role,pid=proc.pid,command=cmd)
        if running:time.sleep(.5)
    value={'schema':'DEE.RBX07.pre_material_import_batch.R01','utc':now(),'results':results,
        'all_five_supervisors_exit0':len(results)==5 and all(x['exit_code']==0 for x in results),
        'Native_ticks':0,'world_owners_opened':0,'scope':'Import/load plus exact complete copy only; read each child comparison before material use.'}
    with(out/'RESULTADO.json').open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(value,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
