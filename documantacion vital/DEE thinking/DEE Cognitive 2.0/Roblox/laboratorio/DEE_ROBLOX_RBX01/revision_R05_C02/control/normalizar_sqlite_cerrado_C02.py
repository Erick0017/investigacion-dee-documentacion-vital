"""Root-only closed-bridge SQLite maintenance, never Native/MCP or file deletion.

Requires closed Native proof plus the bridge ProcessLease. Preserves a coherent
SQLite backup and before hashes, validates actual pending/ACK/boundary state,
then asks SQLite itself to checkpoint/TRUNCATE. Scientific table rows must remain
identical. Never blindly removes a WAL/SHM, lock or pending operation.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,sqlite3,sys
ROOT=Path(__file__).resolve().parents[1]
def load(relative,name):
    s=importlib.util.spec_from_file_location(name,ROOT/relative);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def need(x,msg):
    if not x:raise ValueError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def write(p,value):
    with p.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def files(path):
    out={}
    for suffix in('','-wal','-shm','-journal'):
        p=Path(str(path)+suffix)
        out[p.name]={'exists':p.exists(),'bytes':p.stat().st_size if p.exists()else None,'sha256':sha(p)if p.is_file()else None}
    return out
def semantics(db):
    db.row_factory=sqlite3.Row
    tables=[r[0]for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'ORDER BY name")]
    need({'bridge_meta','session','operation','boundary','action','tool_call'}<=set(tables),'Only full C02 bridge schema')
    schema=db.execute("SELECT value FROM bridge_meta WHERE key='schema'").fetchone()
    need(schema and schema[0]=='DEE.RBX01.bridge_database.C02.R01','Only exact C02 schema')
    rows={}
    for name in tables:
        quoted='"'+name.replace('"','""')+'"';values=[dict(r)for r in db.execute('SELECT *FROM '+quoted+' ORDER BY rowid')]
        raw=json.dumps(values,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
        rows[name]={'rows':len(values),'sha256':hashlib.sha256(raw.encode('utf8')).hexdigest()}
    sessions=list(db.execute('SELECT *FROM session'));need(len(sessions)==1,'Exactly one session')
    session=dict(sessions[0]);need(session['status']=='SUSPENDED_BOUNDARY'and session['phase']=='READY_QUERY','Exact suspended boundary required')
    need(db.execute("SELECT count(*)FROM operation WHERE status IN('QUEUED','RUNNING','UNCERTAIN')").fetchone()[0]==0,'Pending/uncertain operations preserved')
    need(db.execute("SELECT count(*)FROM action WHERE acknowledged!=1 OR execution_status!='EXECUTED'").fetchone()[0]==0,'Unacknowledged actions preserved')
    need(db.execute('SELECT count(*)FROM tool_call WHERE acknowledged!=1').fetchone()[0]==0,'Unacknowledged tools preserved')
    boundary=db.execute('SELECT *FROM boundary LIMIT1'.replace('LIMIT1','LIMIT 1')).fetchone()
    need(boundary and boundary['session_id']==session['id']and boundary['last_action_id']==session['last_action_id'],'Boundary mismatch')
    return {'tables':rows,'session':session,'boundary':dict(boundary)}
def maintain(args,persistence=None,bridge=None):
    need(args.root_run,'Root-only maintenance must be explicit')
    p=persistence or load('control/persistencia_C02.py','_C02_maintenance_closed_codec')
    b=bridge or load('puente/rbx02_bridge_C02.py','_C02_maintenance_bridge')
    native,proof,database=map(p.safe,(args.native_root,args.close_proof,args.bridge_database))
    output=p.safe(args.output,exists=False);need(not output.exists(),'New evidence directory only')
    context=read(native/'CONTEXTO_EJECUCION.json');life=context['life']
    card=p.closed_native_root(native,life);p.check_close(read(proof),life)
    need(database.parent==ROOT/'configuracion_privada','Only explicit private bridge DB')
    output.mkdir(parents=True);lease=None;con=None
    report={'schema':'DEE.RBX01.C02.closed_sqlite_maintenance.R01','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'Native_life_id':life,'Native_tick':card['physical']['tick'],'Native_imports':0,'Native_ticks':0,
            'MCP_calls':0,'files_deleted_by_script':0,'database':str(database),'owner_closed_proof_sha256':sha(proof)}
    try:
        lease=b.ProcessLease(database)
        report['before_files']=files(database)
        con=sqlite3.connect(str(database),isolation_level=None,timeout=5)
        con.execute('PRAGMA busy_timeout=5000')
        need(con.execute('PRAGMA quick_check').fetchone()[0]=='ok','Bridge quick_check failed')
        before=semantics(con);report['before_semantics']=before
        backup=output/'BEFORE_COHERENT_BRIDGE.sqlite3';target=sqlite3.connect(backup)
        try:con.backup(target);need(target.execute('PRAGMA quick_check').fetchone()[0]=='ok','Coherent backup integrity')
        finally:target.close()
        report['coherent_backup']={'file':str(backup),'bytes':backup.stat().st_size,'sha256':sha(backup)}
        checkpoint=list(con.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchone());report['wal_checkpoint_result']=checkpoint
        need(checkpoint[0]==0,'Checkpoint busy: preserve readers/WAL, do not delete or force')
        need(con.execute('PRAGMA quick_check').fetchone()[0]=='ok','Post-checkpoint quick_check failed')
        after=semantics(con);need(before==after,'Scientific rows changed during maintenance')
        report['after_semantics']=after
        con.close();con=None
        report['after_files']=files(database)
        for suffix in('-wal','-shm','-journal'):
            f=Path(str(database)+suffix);need(not f.exists()or f.stat().st_size==0,
                  'SQLite auxiliary still held by a reader after close; preserve, no manual deletion: '+suffix)
        p.check_sqlite(database,bridge=True)
        need(p.closed_native_root(native,life)['snapshot_sha256']==card['snapshot_sha256'],'Closed Native state changed concurrently')
        report.update(status='CLOSED_BRIDGE_CHECKPOINTED_ROWS_IDENTICAL',scientific_rows_equal=True,
                      WAL_rule='Any committed frames were preserved through SQLite backup/checkpoint, never discarded.')
    except BaseException as error:
        report.update(status='MAINTENANCE_INCOMPLETE_PRESERVED',error_type=type(error).__name__,error=str(error));raise
    finally:
        if con is not None:con.close()
        if lease is not None:lease.close()
        write(output/'MANTENIMIENTO_SQLITE_C02.json',report)
    return report
def parser():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root-run',action='store_true',required=True)
    for name in('native-root','close-proof','bridge-database','output'):p.add_argument('--'+name,type=Path,required=True)
    return p
if __name__=='__main__':print(json.dumps(maintain(parser().parse_args()),ensure_ascii=False,indent=2))
