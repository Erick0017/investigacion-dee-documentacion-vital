"""Read-only reconciliation of exact failed DEV_FASE_01 startup. No Native/MCP.

Writes one new audit witness only. Does not erase/retry/reclassify any request,
modify original failure RESULTADO, change lock files or repair a world.
"""
from pathlib import Path
import ctypes,datetime,hashlib,importlib.util,json,sqlite3,sys
ROOT=Path(__file__).resolve().parents[1]
def need(x,msg):
    if not x:raise RuntimeError(msg)
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pid_status(pid):
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong];k.OpenProcess.restype=ctypes.c_void_p
    k.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_ulong];k.WaitForSingleObject.restype=ctypes.c_ulong
    k.CloseHandle.argtypes=[ctypes.c_void_p];k.CloseHandle.restype=ctypes.c_int
    handle=k.OpenProcess(0x100000|0x1000,False,pid)
    if not handle:
        error=ctypes.get_last_error();need(error==87,'Cannot establish owner process exit, Win32='+str(error))
        return {'pid':pid,'running':False,'method':'OpenProcess ERROR_INVALID_PARAMETER87: no process at this PID'}
    try:
        result=k.WaitForSingleObject(handle,0);need(result==0,'Exact owner process still running/unknown; preserve')
        return {'pid':pid,'running':False,'method':'Process handle signalled'}
    finally:k.CloseHandle(handle)
def main():
    d=ROOT/'native/DEV';attempt=ROOT/'evidencia/DEV_FASE_01'
    out=attempt/'RECONCILIACION_RO_CERRADO_0TICKS.json';need(not out.exists(),'Preserve prior reconciliation')
    context=read(d/'CONTEXTO_EJECUCION.json');life=context['life'];import0=read(d/'IMPORTACION_DIAGNOSTICA.json')
    rows=[json.loads(line)for line in(d/'ENSAYOS.jsonl').read_text('utf8').splitlines()]
    closed=[r for r in rows if r.get('kind')=='OWNER_CLOSED'and r.get('life')==life]
    need(closed,'Missing official child closure');child=closed[-1];run=child['run'];status=child['final_status']
    need(run=='RBX01_C02_LIVE_fcf2eb17'and child['exit_code']==0 and status['running']is False and
         status['uncertain_external_result']is False,'Not the exact closed certain failed startup')
    process=pid_status(child['pid'])
    spec=importlib.util.spec_from_file_location('_C02_readonly_closed_check',ROOT/'control/persistencia_C02.py')
    p=importlib.util.module_from_spec(spec);sys.modules[spec.name]=p;spec.loader.exec_module(p)
    card=p.closed_native_root(d,life)
    queue=d/'sistema/estado/servicios_persistentes'/life/'cola.sqlite3'
    sourcefiles=[d/'ENSAYOS.jsonl',d/'IMPORTACION_DIAGNOSTICA.json',d/'sistema/estado/vidas'/life/'VIDA.json',
                 d/'sistema'/card['snapshot'],queue,ROOT/'control/LEDGER_C02.json',attempt/'RESULTADO.json']
    before={str(f):sha(f)for f in sourcefiles}
    con=sqlite3.connect(queue.as_uri()+'?mode=ro&immutable=1',uri=True);con.row_factory=sqlite3.Row
    try:
        need(con.execute('PRAGMA quick_check').fetchone()[0]=='ok','Queue not integral')
        requests=[dict(r)for r in con.execute('SELECT id,payload,is_control,status,result,error FROM requests WHERE id LIKE ? ORDER BY seq',(run+'_%',))]
        totals={r['status']:r['n']for r in con.execute('SELECT status,count(*)n FROM requests GROUP BY status')}
        need(not any(totals.get(k,0)for k in('queued','processing','uncertain')),'Pending/uncertain Native future')
        need(len(requests)==2,'Unexpected own-startup request count')
        controls=[]
        for r in requests:
            payload=json.loads(r['payload']);result=json.loads(r['result'])if r['result']else{}
            need(r['is_control']==1 and r['status']=='completed'and payload.get('operacion')in('reanudar','detener'),
                 'A nonadministrative or uncertain own-startup request exists')
            controls.append({'id':r['id'],'status':r['status'],'payload':payload,'result':result,'error':r['error']})
        owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])
    finally:con.close()
    expected=import0['result']['physical'];keys=('N','tick','RAW_sha256','clocks_sha256')
    need(all(card['physical'][k]==expected[k]==status['physical'][k]==owner['physical'][k]for k in keys),'Physical cut changed since import0')
    ledger=read(ROOT/'control/LEDGER_C02.json');need(ledger['intent']is None and ledger['consumed']==0 and not ledger['worlds'],'C02 material ledger changed')
    need(not(attempt/'START_NATIVE_INTENT.json').exists(),'A START intent requires broader reconciliation')
    log=(attempt/'owner_utf8.log').read_text('utf8');need('SCHEMA_INTEGER'in log and 'integer(rate_limit, 1, 60)'in log,'Unexpected launcher failure')
    need(before=={str(f):sha(f)for f in sourcefiles},'Read sources changed concurrently')
    report={'schema':'DEE.RBX01.C02.failed_startup_reconciliation.R01','inspected_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status':'CLOSED_RECONCILED_ZERO_NEW_NATIVE_TICKS','life_id':life,'run':run,'new_native_ticks':0,'material_requests_in_this_attempt':0,
        'physical':{k:card['physical'][k]for k in keys},'import0_snapshot_sha256':import0['result']['snapshot_sha256'],
        'closed_snapshot_sha256':card['snapshot_sha256'],'snapshot_note':'Administrative checkpoint/history bytes may change; physical RAW/clocks/tick remain identical. No claim of binary snapshot equality.',
        'ownerClosed':True,'writerDrained':True,'owner_child_exit_code':0,'owner_launcher_exit_code':read(attempt/'RESULTADO.json')['owner_returncode'],
        'process_observation':process,'source_owner_closed':{k:child[k]for k in('kind','run','life','pid','exit_code')},
        'owner_status':{k:owner[k]for k in('running','uncertain_external_result','tick','idle_ticks','C02_host_event_driven','wall_utc')},
        'queue_quick_check':'ok','queue_status_counts':totals,'own_administrative_requests':controls,'ledger':ledger,
        'cause':'Bridge startup rejects requestsPerMinute600 against fixed legal1..60 before HTTP health/session/START. Child owner closes with0 after launcher exception; launcher exits1.',
        'original_failure_record_preserved':True,'sources_sha256':before,'Native_imports':0,'MCP_calls':0,
        'scope_limit':'Read-only reconciliation of exact DEV startup, not a material closed-loop experiment, not a restore test and not principal observation.'}
    with out.open('x',encoding='utf8')as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({'path':str(out),'sha256':sha(out),'status':report['status'],'life_id':life,'tick':card['physical']['tick'],'owner_closed':True,'new_native_ticks':0}))
if __name__=='__main__':main()
