"""Stdlib RO monitor; no Native/owner/HTTP/MCP import, action or termination.

One coherent SQLite read transaction. Ledger is read before/after because it
cannot be atomically sampled with SQLite; cache age and cross-file limits remain
explicit. Only known supplied/cached owned PIDs may be queried for host RAM/CPU.
"""
from pathlib import Path
import argparse,ctypes,datetime,hashlib,json,os,sqlite3,time
ROOT=Path(__file__).resolve().parents[1]
def need(ok,msg):
    if not ok:raise ValueError(msg)
def utc():return datetime.datetime.now(datetime.timezone.utc)
def safe(path):
    p=Path(path).absolute()
    for q in(p,*p.parents):need(not q.is_symlink()and not(q.exists()and getattr(q.lstat(),'st_file_attributes',0)&1024),'No linked/reparse monitor paths')
    p=p.resolve();need(p.is_relative_to(ROOT),'C02 subtree only');return p
def read(path):return json.loads(path.read_text('utf-8-sig'))
def hashbytes(raw):return hashlib.sha256(raw).hexdigest()
def age(value):
    try:return(utc()-datetime.datetime.fromisoformat(value)).total_seconds()
    except(TypeError,ValueError):return None
def compact_request(row):
    if row is None:return None
    row=dict(row);out={k:row.get(k)for k in('seq','id','status','is_control','arrived_utc','started_utc','finished_utc')}
    for field in('payload','result','error'):
        raw=row.get(field)
        if raw is None:continue
        out[field+'_sha256']=hashbytes(raw.encode('utf8'))
        try:value=json.loads(raw)
        except(ValueError,TypeError):out[field+'_parse']='NOT_JSON';continue
        if isinstance(value,dict):
            if field=='payload':
                out['operation']=value.get('operacion');situations=value.get('situaciones')
                if isinstance(situations,list):out['material_modes']=[s.get('modo')for s in situations if isinstance(s,dict)]
            else:out[field+'_summary']={k:value[k]for k in('type','detail','external_execution_may_be_uncertain',
                        'native_tick_after_attempt','before_tick','after_tick','operation','before_tick_cached')if k in value}
    return out
def memory(pid):
    result={'pid':pid,'scope':'HOST_RESOURCES_NOT_COGNITIVE_MEMORY'}
    if os.name!='nt':return{**result,'available':False,'reason':'WIN32_UNAVAILABLE'}
    class Counters(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong)]+[(x,ctypes.c_size_t)for x in
          ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage')]
    class FileTime(ctypes.Structure):_fields_=[('low',ctypes.c_ulong),('high',ctypes.c_ulong)]
    k=ctypes.WinDLL('kernel32',use_last_error=True);p=ctypes.WinDLL('psapi',use_last_error=True)
    k.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong];k.OpenProcess.restype=ctypes.c_void_p
    k.CloseHandle.argtypes=[ctypes.c_void_p];k.GetExitCodeProcess.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_ulong)]
    p.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.POINTER(Counters),ctypes.c_ulong]
    k.GetProcessTimes.argtypes=[ctypes.c_void_p,ctypes.POINTER(FileTime),ctypes.POINTER(FileTime),ctypes.POINTER(FileTime),ctypes.POINTER(FileTime)]
    handle=k.OpenProcess(0x0400|0x0010,False,pid)
    if not handle:return{**result,'available':False,'win32_error':ctypes.get_last_error()}
    try:
        status=ctypes.c_ulong();k.GetExitCodeProcess(handle,ctypes.byref(status));result['exit_code']=status.value;result['running']=status.value==259
        c=Counters();c.cb=ctypes.sizeof(c)
        if p.GetProcessMemoryInfo(handle,ctypes.byref(c),c.cb):result.update(available=True,working_set_bytes=c.WorkingSetSize,private_bytes=c.PrivateUsage,peak_pagefile_bytes=c.PeakPagefileUsage)
        else:result.update(available=False,win32_error=ctypes.get_last_error())
        creation,exit,kernel,user=FileTime(),FileTime(),FileTime(),FileTime()
        if k.GetProcessTimes(handle,ctypes.byref(creation),ctypes.byref(exit),ctypes.byref(kernel),ctypes.byref(user)):
            seconds=lambda f:((f.high<<32)+f.low)/10000000
            result.update(cpu_user_seconds=seconds(user),cpu_kernel_seconds=seconds(kernel),process_creation_win32_seconds=seconds(creation))
        return result
    finally:k.CloseHandle(handle)
def inspect(args):
    started=utc();destination=safe(args.destination);ledger_path=safe(args.ledger)
    context=read(destination/'CONTEXTO_EJECUCION.json');life=context['life']
    need(destination.parent==ROOT/'native'and '_RBX01_C02_'in life,'Explicit diagnostic clone only')
    database=destination/'sistema/estado/servicios_persistentes'/life/'cola.sqlite3'
    ledger_before=ledger_path.read_bytes()
    con=sqlite3.connect(database.as_uri()+'?mode=ro',uri=True,timeout=5);con.row_factory=sqlite3.Row
    try:
        con.execute('BEGIN');owner_row=con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()
        owner=json.loads(owner_row[0])if owner_row else{}
        latest=con.execute('SELECT *FROM requests ORDER BY seq DESC LIMIT1'.replace('LIMIT1','LIMIT 1')).fetchone()
        material=con.execute('SELECT *FROM requests WHERE is_control=0 ORDER BY seq DESC LIMIT1'.replace('LIMIT1','LIMIT 1')).fetchone()
        counts={r['status']:r['n']for r in con.execute('SELECT status,count(*)n FROM requests GROUP BY status')}
        pending=[compact_request(r)for r in con.execute("SELECT *FROM requests WHERE status IN('queued','processing','uncertain') ORDER BY seq")]
        con.rollback()
    finally:con.close()
    ledger_after=ledger_path.read_bytes();ledger=json.loads(ledger_after.decode('utf-8-sig'))
    keys=('life_id','pid','running','paused','tick','last_saved_tick','idle_ticks','material_calls','uncertain_external_result',
          'host_elapsed_seconds','wall_utc','C02_host_event_driven','physical')
    pids=set(args.pid or[])
    if type(owner.get('pid'))is int:pids.add(owner['pid'])
    imported=None;importpath=destination/'IMPORT0_JOB.json'
    if importpath.exists():
        raw=read(importpath);imported={k:raw[k]for k in('status','exit_code','new_native_ticks','life_id','physical','memory_limit_bytes','pid')if k in raw}
        if raw.get('samples'):imported['last_sample']=raw['samples'][-1]
    result={'schema':'DEE.RBX01.C02.readonly_monitor.R01','started_utc':started.isoformat(),'finished_utc':utc().isoformat(),
        'life_id':life,'owner_cached':{k:owner[k]for k in keys if k in owner},'owner_cache_age_seconds':age(owner.get('wall_utc')),
        'latest_request':compact_request(latest),'latest_material_request':compact_request(material),
        'request_status_counts':counts,'pending_requests':pending,'ledger_current':ledger,
        'ledger_before_sha256':hashbytes(ledger_before),'ledger_after_sha256':hashbytes(ledger_after),
        'ledger_stable_during_sqlite_read':ledger_before==ledger_after,'cross_file_snapshot_atomic':False,
        'import0_cached':imported,'known_owned_process_resources':[memory(pid)for pid in sorted(pids)],
        'Native_imports':0,'Native_actions':0,'MCP_calls':0,'HTTP_requests':0,
        'limitations':'Owner physical tick is cached at wall_utc, not an instantaneous Native observation. Queue+ledger have separate transactions; a completed request with ledger intent may be a host completion gap. No pending ID is retried.'}
    if args.output:
        output=safe(args.output);need(not output.exists(),'New report only')
        with output.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,required=True)
    p.add_argument('--ledger',type=Path,default=ROOT/'control/LEDGER_C02.json');p.add_argument('--pid',type=int,action='append')
    p.add_argument('--output',type=Path);a=p.parse_args();print(json.dumps(inspect(a),ensure_ascii=False,indent=2))
