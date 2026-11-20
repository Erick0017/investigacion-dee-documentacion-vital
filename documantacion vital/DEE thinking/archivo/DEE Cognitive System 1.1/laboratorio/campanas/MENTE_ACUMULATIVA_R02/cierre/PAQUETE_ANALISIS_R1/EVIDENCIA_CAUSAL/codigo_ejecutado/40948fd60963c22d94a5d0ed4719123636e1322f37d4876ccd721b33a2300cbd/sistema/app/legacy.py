"""Explicit inherited-family validation, separate from the active life.

The participant constructors remain native. Old primary references are read by
the inherited auditor only after each trajectory; they never route life inputs.
"""
from pathlib import Path
from datetime import datetime,timezone
import ctypes,json,os,subprocess,sys,time
from .native_tools import atomic_json,digest_file
from .process_control import spawn_owned,job_resources,terminate_job,close_job

def owned_memory(process):
    if os.name!='nt':return None
    class Counters(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong),('PeakWorkingSetSize',ctypes.c_size_t),('WorkingSetSize',ctypes.c_size_t),('QuotaPeakPagedPoolUsage',ctypes.c_size_t),('QuotaPagedPoolUsage',ctypes.c_size_t),('QuotaPeakNonPagedPoolUsage',ctypes.c_size_t),('QuotaNonPagedPoolUsage',ctypes.c_size_t),('PagefileUsage',ctypes.c_size_t),('PeakPagefileUsage',ctypes.c_size_t),('PrivateUsage',ctypes.c_size_t)]
    c=Counters();c.cb=ctypes.sizeof(c)
    if not ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.c_void_p(int(process._handle)),ctypes.byref(c),c.cb):return None
    return{'working_set':int(c.WorkingSetSize),'peak_working_set':int(c.PeakWorkingSetSize),'private_bytes':int(c.PrivateUsage)}

def run_families(system_root,out,*,families=None,max_workers=2,total_seconds=3600,job_seconds=900,memory_limit=4*1024**3):
    system_root=Path(system_root).resolve();out=Path(out).resolve()
    if out.exists():raise FileExistsError('Use a new legacy validation directory')
    out.mkdir(parents=True);core=system_root/'capacidades/core';cfg=json.loads((core/'FAMILIAS.json').read_bytes());families=list(families or cfg['families'])
    if not set(families)<=set(cfg['families'])|{'product_persistence'}:raise ValueError('Unknown inherited family')
    start=time.monotonic();deadline=start+total_seconds;mat=system_root/'estado/cache_heredada/RECUPERADO';mat.parent.mkdir(parents=True,exist_ok=True);proof=mat.parent/'MATERIALIZACION.json'
    report={'schema':'DCS1.1.legacy.validation.v1','status':'RUNNING','started_utc':datetime.now(timezone.utc).isoformat(),'families_requested':families,'family_results':{},'commands':[],'max_workers':max_workers,'max_memory_per_worker':memory_limit,'historical_archives_opened':False,'active_life_modified':False,'modality':'Fresh independent auxiliary reproductions of finite inherited contracts, never knowledge summed intoE1'}
    def save():report['elapsed_seconds']=time.monotonic()-start;atomic_json(out/'REGRESION_HEREDADA.json',report)
    if not proof.is_file():
        argv=[sys.executable,'-I','-B',str(core/'scripts/materializar.py'),'--out',str(mat)]
        for prefix in cfg['prefixes']:argv+=['--prefix',prefix]
        began=time.monotonic()
        with(out/'materializar.stdout.log').open('w',encoding='utf8')as stdout,(out/'materializar.stderr.log').open('w',encoding='utf8')as stderr:
            result=subprocess.run(argv,stdout=stdout,stderr=stderr,timeout=min(600,total_seconds),creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        report['commands'].append({'kind':'MATERIALIZATION','argv':argv,'exit_code':result.returncode,'seconds':time.monotonic()-began})
        if result.returncode:report['status']='MATERIALIZATION_ERROR';save();raise RuntimeError('Inherited materialization failed; see logs')
        atomic_json(proof,{'status':'PASS','index_sha256':digest_file(core/'documentacion/INDICE_MIEMBROS.json'),'store_sha256':digest_file(core/'mecanismos/RECUPERACION_POR_HASH.jsonl.gz'),'prefixes':cfg['prefixes']})
    pending=list(families);running=[]
    try:
        while pending or running:
            while pending and len(running)<max_workers and time.monotonic()<deadline:
                family=pending.pop(0);target=out/('native_'+family)
                script='worker_legacy_core.py'if family in cfg['optional_numeric_families']else'worker_initial_cpc8.py'if family=='initial_cpc8'else'worker_social.py'if family=='social'else'worker_extension.py'if family in cfg['extensions']else'worker_retention.py'if family in cfg['retention']else'worker_core.py'
                argv=[sys.executable,'-I','-B',str(core/'reproduccion'/script)]
                if family in cfg['optional_numeric_families']:argv+=['--family',family,'--numpy-root',str(system_root/'runtime/optional_numeric')]
                else:argv+=[family.removeprefix('retain_')if family in cfg['retention']else family]
                argv+=['--materialized',str(mat),'--out',str(target)]
                stdout=(out/(family+'.stdout.log')).open('w',encoding='utf8');stderr=(out/(family+'.stderr.log')).open('w',encoding='utf8');proc,job,job_name=spawn_owned(argv,cwd=out,stdout=stdout,stderr=stderr,memory_limit=memory_limit);entry={'family':family,'argv':argv,'owned_pid':proc.pid,'owned_job':job_name,'started':time.monotonic(),'status':'RUNNING','launcher_peak_working_set':0};report['commands'].append(entry);running.append((proc,entry,stdout,stderr,target,job,job_name));print('START',family,proc.pid,flush=True);save()
            for item in running[:]:
                proc,entry,stdout,stderr,target,job,job_name=item;mem=owned_memory(proc);entry.update(job_resources(job))
                if mem:entry['launcher_peak_working_set']=max(entry['launcher_peak_working_set'],mem['peak_working_set'])
                reason='MEMORY_LIMIT'if mem and mem['private_bytes']>memory_limit else'TOTAL_TIME_LIMIT'if time.monotonic()>deadline else'JOB_TIME_LIMIT'if time.monotonic()-entry['started']>job_seconds else None
                if reason and proc.poll()is None:terminate_job(job);entry['limit_reason']=reason
                code=proc.poll()
                if code is None:continue
                proc.wait();stdout.close();stderr.close();entry.update(job_resources(job));close_job(job);entry.update(exit_code=code,status='COMPLETED'if code==0 else'FAILED',elapsed_seconds=time.monotonic()-entry['started'],owned_process_waited=True,owned_job_closed=True,kill_on_close=True)
                value=json.loads((target/'RECOVERY.json').read_bytes())if(target/'RECOVERY.json').exists()else{'status':'PROCESS_FAILED_WITHOUT_PRIMARY','exit_code':code}
                report['family_results'][entry['family']]=value;running.remove(item);print('END',entry['family'],value.get('status'),round(entry['elapsed_seconds'],2),flush=True);save()
            if time.monotonic()>deadline and pending:
                for family in pending:report['family_results'][family]={'status':'NOT_EXECUTED_TOTAL_TIME_LIMIT'}
                pending=[]
            if running:time.sleep(1)
    finally:
        for proc,entry,stdout,stderr,target,job,job_name in running:
            if proc.poll()is None:terminate_job(job)
            proc.wait();entry.update(job_resources(job));close_job(job);stdout.close();stderr.close();entry['owned_process_waited']=True;entry['owned_job_closed']=True
    report['status']='COMPLETED';report['counts']={s:sum(x.get('status')==s for x in report['family_results'].values())for s in sorted({v.get('status')for v in report['family_results'].values()})};save();return report
