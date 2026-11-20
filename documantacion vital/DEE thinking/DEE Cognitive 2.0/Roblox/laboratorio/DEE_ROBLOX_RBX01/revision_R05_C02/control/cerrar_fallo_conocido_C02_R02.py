"""Root-only stop after one exact KNOWN failed-preserved partial admission.

Does not execute/retry a Native function, ACK a tool, edit a Native DB or erase
uncertain bridge history. After official existing-owner close0 proof ONLY, settles
the79actual ticks against the SAME ledger intent, leaving cycle/reserve unfinished.
"""
from pathlib import Path
import argparse,datetime,hashlib,http.client,importlib.util,json,sqlite3,sys,time,uuid
ROOT=Path(__file__).resolve().parents[1]
REQUEST='6fbe0205c45a49d183107acf83c21170'
BEFORE=947773
AFTER=947852
REASON='INFRASTRUCTURE'
OBSERVATIONAL_REASON='OPERATOR_STOP_AFTER_KNOWN_PARTIAL_ADMISSION'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return hashlib.sha256(canonical(v).encode('utf8')).hexdigest()
def write(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def safe(p):
    p=Path(p).absolute()
    for part in(p,*p.parents):need(not part.is_symlink()and not(part.exists()and getattr(part.lstat(),'st_file_attributes',0)&1024),'No linked/reparse paths')
    p=p.resolve();need(p.is_relative_to(ROOT),'C02 subtree only');return p
def load(relative,name):
    s=importlib.util.spec_from_file_location(name,ROOT/relative);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def validate_error(row,error):
    need(row['id']==REQUEST and row['status']=='failed_preserved'and row['is_control']==0,'Exact failed material request only')
    need(error.get('external_execution_may_be_uncertain')is False and error.get('native_tick_after_attempt')==AFTER,
         'Native future is not explicitly known at fixed partial tick')
    saved=error.get('failed_native_future_preserved',{})
    need(saved.get('physical',{}).get('tick')==AFTER and isinstance(saved.get('snapshot_sha256'),str),'Known preserved physical snapshot required')
    return saved
def inspect_native(destination,*,before_stop):
    ctx=read(destination/'CONTEXTO_EJECUCION.json');life=ctx['life']
    need(life.endswith('_RBX01_C02_MAIN')and destination==ROOT/'native/MAIN','Exact R01 experimental MAIN only; protected/revised life denied')
    system=destination/'sistema';db=system/'estado/servicios_persistentes'/life/'cola.sqlite3'
    con=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True,timeout=5);con.row_factory=sqlite3.Row
    try:
        con.execute('BEGIN');row=con.execute('SELECT *FROM requests WHERE id=?',(REQUEST,)).fetchone();need(row,'Exact Native row missing');row=dict(row)
        owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])
        pending=[dict(r)for r in con.execute("SELECT id,status,is_control FROM requests WHERE status IN('queued','processing','uncertain')")]
        con.rollback()
    finally:con.close()
    error=json.loads(row['error']);saved=validate_error(row,error);need(not pending,'Pending Native/control operation exists; no stop/settlement guessing')
    need(owner.get('tick')==owner.get('last_saved_tick')==AFTER and owner.get('uncertain_external_result')is False,'Owner physical state not the known saved cut')
    if before_stop:
        age=(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(owner['wall_utc'])).total_seconds()
        need(owner.get('running')is True and owner.get('paused')is True and 0<=age<=20,'Owner must be freshly paused before explicit stop')
    else:need(owner.get('running')is False,'Official owner has not actually closed')
    card=read(system/'estado/vidas'/life/'VIDA.json')
    for key in('N','tick','RAW_sha256','clocks_sha256'):
        need(card['physical'][key]==saved['physical'][key]==owner['physical'][key],'Physical card/cache/failed snapshot disagreement')
    failed_snapshot=safe(system/saved['snapshot']);need(sha(failed_snapshot)==saved['snapshot_sha256'],'Preserved failed snapshot changed')
    current_snapshot=safe(system/card['snapshot']);need(sha(current_snapshot)==card['snapshot_sha256'],'Current saved Native snapshot changed')
    return {'life':life,'row':row,'row_sha256':digest(row),'error':error,'owner':owner,'card':card,
            'failed_snapshot':str(failed_snapshot),'failed_snapshot_sha256':sha(failed_snapshot)}
def inspect_bridge(database):
    con=sqlite3.connect(database.as_uri()+'?mode=ro',uri=True,timeout=5);con.row_factory=sqlite3.Row
    try:
        con.execute('BEGIN');s=con.execute('SELECT *FROM session LIMIT1'.replace('LIMIT1','LIMIT 1')).fetchone()
        op=con.execute('SELECT *FROM operation WHERE id=?',(REQUEST,)).fetchone()
        pending=con.execute("SELECT count(*)FROM operation WHERE status IN('QUEUED','RUNNING')").fetchone()[0]
        uncertain=[dict(r)for r in con.execute("SELECT id,kind,status FROM operation WHERE status='UNCERTAIN'")];con.rollback()
        need(s and op and dict(op)['kind']=='function'and dict(op)['status']=='UNCERTAIN'and pending==0,
             'Expected settled uncertain FUNCTION history only')
        need(len(uncertain)==1 and uncertain[0]['id']==REQUEST,'Other uncertain history requires separate resolution')
        return {'session':dict(s),'operation':dict(op),'pending':pending,'uncertain':uncertain}
    finally:con.close()
def post_stop(config,body):
    token_path=safe(ROOT/'configuracion_privada'/config['tokenFile']);token=token_path.read_text('ascii').strip()
    con=http.client.HTTPConnection('127.0.0.1',8895,timeout=15)
    try:
        con.request('POST','/v1/stop',body=canonical(body).encode('utf8'),headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
        response=con.getresponse();raw=response.read(65537);need(len(raw)<=65536,'Bounded stop response required')
        return {'http_status':response.status,'body':json.loads(raw),'request_id':body['requestId']}
    finally:con.close()
def settle(ledger_path,life,ledger_before,module):
    current=read(ledger_path);need(current==ledger_before,'Aggregate ledger changed since guarded intent; no settlement')
    intent=current['intent'];need(intent and intent['life']==life and intent['id']==REQUEST and intent['mode']=='eci01-rbx01-function','Exact original ledger intent required')
    world_before=current['worlds'][life];max_cycles=world_before['max_cycles']
    budget=module.TickLedger(ledger_path,life,max_cycles);budget.finish(life,REQUEST,BEFORE,AFTER,intent['mode'])
    result=read(ledger_path);w=result['worlds'][life]
    need(result['consumed']==ledger_before['consumed']+79 and w['consumed']==world_before['consumed']+79 and
         w['reserved']==world_before['reserved']-79 and w['cycles']==world_before['cycles']and result['intent']is None,
         'Partial tick settlement must retain unfinished cycle/reservation')
    return result
def run(args):
    need(args.root_run,'Root-only explicit close required')
    destination,config_path,ledger_path,owner_proof,output=map(safe,(args.destination,args.config,args.ledger,args.owner_proof,args.output))
    need(not output.exists()and output.is_relative_to(ROOT/'evidencia'),'Fresh evidence output only')
    native=inspect_native(destination,before_stop=True);cfg=read(config_path)
    need(config_path.parent==ROOT/'configuracion_privada','Exact private configuration required')
    need(cfg.get('bind')=='127.0.0.1'and cfg.get('port')==8895 and cfg.get('allowControl')is False and cfg.get('apiVersion')=='RBX01.C02.v1','Only exact local Native bridge config')
    db=safe(config_path.parent/cfg['databaseFile']);bridge=inspect_bridge(db)
    need(bridge['session']['status']=='PAUSED','Bridge must be paused after known failure')
    ledger_before=read(ledger_path);intent=ledger_before['intent']
    need(intent and intent['id']==REQUEST and intent['life']==native['life']and intent['mode']=='eci01-rbx01-function','Wrong ledger future')
    output.mkdir(parents=True);write(output/'NATIVE_FAILED_ROW_BEFORE.json',native['row']);write(output/'LEDGER_INTENT_BEFORE.json',ledger_before)
    write(output/'BRIDGE_HISTORY_BEFORE.json',bridge)
    body={'apiVersion':'RBX01.C02.v1','requestId':uuid.uuid4().hex,'sessionId':bridge['session']['id'],
          'serverInstanceId':bridge['session']['server_id'],'reason':REASON}
    write(output/'STOP_INTENT_ONCE.json',{'route':'/v1/stop','body':body,'single_attempt':True,'Native_function_retry':False,'fake_ACK':False,'observational_reason':OBSERVATIONAL_REASON})
    summary={'schema':'DEE.RBX01.C02.known_partial_failure_close.R01','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'life_id':native['life'],'request_id':REQUEST,'before_tick':BEFORE,'after_tick':AFTER,'actual_partial_ticks':79,
             'Native_function_retried':False,'Native_DB_modified_by_script':False,'fake_ACK':False,'UNCERTAIN_bridge_history_cleared':False}
    try:
        try:
            reply=post_stop(cfg,body)
        except BaseException as error:
            summary['stop_transport_unknown_preserved']=type(error).__name__
            write(output/'STOP_HTTP_UNKNOWN.json',{'error_type':type(error).__name__,'no_retry':True})
        else:
            summary['stop_reply']=reply;write(output/'STOP_HTTP_REPLY.json',reply)
            need(reply.get('http_status')==200 and reply.get('body',{}).get('status')in('STOPPED','STOPPING'),
                 'Known rejected stop response; preserve without waiting, retry or settlement')
        deadline=time.monotonic()+args.wait_seconds;proof=None
        while time.monotonic()<deadline:
            if owner_proof.exists():
                candidate=read(owner_proof)
                if candidate.get('lifeId')==native['life']and candidate.get('ownerClosed')is True and candidate.get('writerDrained')is True:
                    child=candidate.get('source_journal_event',{})
                    need(child.get('exit_code')==0 and child.get('final_status',{}).get('running')is False,'Existing child close proof is not exit0')
                    proof=candidate;break
            time.sleep(1)
        need(proof is not None,'Existing owner has no close0/drain proof; preserve ledger intent and future')
        after=inspect_native(destination,before_stop=False);need(after['row_sha256']==native['row_sha256'],'Failed-preserved Native row was changed')
        history=inspect_bridge(db);need(digest(history['operation'])==digest(bridge['operation']),'UNCERTAIN bridge operation history changed')
        need(history['session']['status']=='STOPPED','Actual bridge stop not committed')
        write(output/'OWNER_CLOSE_PROOF.json',proof);write(output/'NATIVE_FAILED_ROW_AFTER.json',after['row'])
        module=load('fuentes/rbx02_owner_support_C02.py','_C02_known_failure_ledger_only')
        ledger_after=settle(ledger_path,native['life'],ledger_before,module);write(output/'LEDGER_AFTER_SETTLE79.json',ledger_after)
        summary.update(status='OFFICIAL_OWNER_CLOSED_PARTIAL79_SETTLED_CYCLE_UNFINISHED',owner_closed=True,
                       owner_proof_sha256=sha(owner_proof),failed_row_sha256=native['row_sha256'],
                       failed_snapshot_sha256=native['failed_snapshot_sha256'],ledger_before_sha256=sha(output/'LEDGER_INTENT_BEFORE.json'),
                       ledger_after_sha256=sha(ledger_path),aggregate_actual_ticks=ledger_after['consumed'],
                       unused_reserved_ticks_retained=ledger_after['worlds'][native['life']]['reserved'],
                       completed_cycles=ledger_after['worlds'][native['life']]['cycles'])
    except BaseException as error:
        summary.update(status='INCOMPLETE_PRESERVED_NO_AUTOMATIC_RETRY',error_type=type(error).__name__,error=str(error));raise
    finally:write(output/'RESULTADO_CIERRE_CONOCIDO.json',summary)
    return summary
def parser():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root-run',action='store_true',required=True)
    for n in('destination','config','owner-proof','output'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--ledger',type=Path,default=ROOT/'control/LEDGER_C02.json');p.add_argument('--wait-seconds',type=int,default=750)
    return p
if __name__=='__main__':
    a=parser().parse_args();need(1<=a.wait_seconds<=900,'Finite1..900second close wait');print(json.dumps(run(a),ensure_ascii=False,indent=2))
