"""Finite non-Native C02 bridge runner. Import/preflight never calls the model.

The common transport, world and mailbox ABI are unchanged. WireAdapter performs
fixed field/unit conversion only. The actual decision belongs to the selected
program or local model. This file imports no DEE owner or simulator.
"""
from __future__ import annotations
import argparse
import copy
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import secrets
import sqlite3
import sys
import threading
import time

BASE=Path(__file__).resolve().parents[1]
PRIVATE=BASE/'configuracion_privada'
MODES=('PROGRAMMED','CONVENTIONAL_AI')
MAX_CUTOFF=1794744900  # 2026-11-15 12:15 UTC, never a rolling horizon.
POLICY_SHA='b210c39efeae0f65fb91166cff7bbbe26f071f317ab78e6fd151e2ef5a730f1b'
_PRESERVED_POLICY=None
_PRESERVED_HOST=None

def need(ok,message):
    if not ok:raise ValueError(message)
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(path):return json.loads(Path(path).read_text('utf-8-sig'))
def write_new(path,data):
    with Path(path).open('x',encoding='utf-8')as f:f.write(canonical(data)+'\n');f.flush();os.fsync(f.fileno())
def safe(path,*,exists=True):
    p=Path(path).resolve(strict=exists);need(p.is_relative_to(BASE),'Outside R05 denied')
    for q in(p,*p.parents):
        if q.exists():need(not q.is_symlink()and not(getattr(q.lstat(),'st_file_attributes',0)&1024),'Links/reparse points denied')
        if q==BASE:break
    return p
def load(relative,module_name):
    path=safe(BASE/relative);spec=importlib.util.spec_from_file_location(module_name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def pack_public(kind,payload):
    """Exactly the invertible Native Q1 codec; no hidden scene field is copied."""
    need(kind in ('decision','query_sensor','function','feedback'),'Known operation')
    if kind in ('decision','query_sensor'):
        obs=payload.get('observation',payload);sensors=obs.get('sensors',obs)
        need(isinstance(sensors,dict),'Body observation dictionary required')
        if kind=='decision':
            zone=sensors.get('publicContactCode');key=sensors.get('inventoryKey')
            resource=sensors.get('inventoryResource');failure=sensors.get('lastFailure');available=sensors.get('queryAvailable')
            need(type(zone)is int and 0<=zone<=5 and all(type(v)is bool for v in(key,resource,failure,available)),'Legal C02 public fields')
            return {'percept_datum':1+zone+8*int(key)+16*int(resource)+32*int(failure),'query_available':available}
        signal=sensors.get('stationSignal');need(type(signal)is int and signal in(-1,0,1,2),'Legal Q2 signal')
        return {'station_signal':signal}
    if kind=='feedback':
        value=payload.get('materialConsequence');need(type(value)is bool,'Actual consequence Boolean required')
        return {'failure':value}
    need(isinstance(payload.get('tool'),dict),'Canonical visible tool required')
    # The policy's closed whitelist independently strips unexpected tool fields.
    return {'tool':copy.deepcopy(payload['tool'])}

def wire_output(kind,result):
    """Closed ABI normalization, never arithmetic/correct-answer selection."""
    out=copy.deepcopy(result)
    if kind=='function' and out.get('toolResult',{}).get('kind')=='LESSON':
        tool=out['toolResult'];items=tool.pop('items',None)
        if items is not None:tool['updates']=items
        tool.setdefault('memory_value',None);tool.setdefault('operation',None);tool.setdefault('numeric_result',None)
        tool.setdefault('reason','VISIBLE_LESSON_OBSERVED')
    if kind in('decision','query_sensor')and out.get('action')=='SAFE_WAIT':
        # Common wire permits no material action for SAFE_WAIT. Preserve whether
        # a model voluntarily chose it, separately from a missing/invalid reply.
        evidence=out.setdefault('evidence',{})
        evidence['wire_safe_wait_null']=True;evidence['policy_original_null']=out.get('null')
        out['null']=True
    return out

class WireAdapter:
    def __init__(self,policy,cutoff):
        self.policy=policy;self.identity=policy.participant;self.cutoff=cutoff
        self.public_life_id='COMPARATOR_'+self.identity+'_'+policy.run_id
    def execute(self,kind,payload,context):
        need(time.time()<self.cutoff,'Prospective comparator cutoff reached; no new inference')
        return wire_output(kind,self.policy.execute(kind,pack_public(kind,payload),context))

def source_pins():
    paths=('puente/run_comparador_C02.py','puente/rbx02_bridge_C02.py','comparadores/adaptadores_C02.py','comparadores/cliente_ia_local_C02.py')
    return {p:sha(safe(BASE/p))for p in paths}

def db_read(path):
    con=sqlite3.connect(Path(path).as_uri()+'?mode=ro',uri=True);con.row_factory=sqlite3.Row
    try:
        tables={r[0]for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        need({'session','operation','action','tool_call','boundary','checkpoint_binding'}<=tables,'Not a C02 bridge database')
        row=con.execute('SELECT * FROM session WHERE singleton=1').fetchone()
        pending=con.execute("SELECT count(*)FROM operation WHERE status!='COMPLETED'").fetchone()[0]
        ops=[dict(r)for r in con.execute('SELECT id,kind,payload,context,result FROM operation ORDER BY admitted')]
        unacked=con.execute("SELECT count(*)FROM action WHERE acknowledged!=1 OR execution_status!='EXECUTED'").fetchone()[0]
        tools=con.execute('SELECT count(*)FROM tool_call WHERE acknowledged!=1').fetchone()[0]
        boundary=con.execute('SELECT * FROM boundary WHERE singleton=1').fetchone()
        binding=con.execute('SELECT * FROM checkpoint_binding WHERE singleton=1').fetchone()
        return {'session':dict(row)if row else None,'pending':pending,'operations':ops,'unacknowledged_actions':unacked,
            'unacknowledged_tools':tools,'boundary':dict(boundary)if boundary else None,'binding':dict(binding)if binding else None,
            'integrity':con.execute('PRAGMA quick_check').fetchone()[0]}
    finally:con.close()

def compare_states(db,policy):
    need(policy.get('pending')is None and db['pending']==0 and db['integrity']=='ok','Pending/uncertain or corrupt state preserved')
    need(db['unacknowledged_actions']==db['unacknowledged_tools']==0,'Unacknowledged actual actuation/tool preserved')
    session=db['session'];need(session and session['mode']==policy['participant']and session['id']==policy['session_id'],'Bridge/policy session mismatch')
    need(session['ticks']==0,'Non-Native comparator cannot claim Native ticks')
    need(len(db['operations'])==len(policy['cache']),'Bridge/policy operation coverage mismatch')
    for op in db['operations']:
        need(op['id']in policy['cache'],'Completed bridge operation missing in policy state')
        public=pack_public(op['kind'],json.loads(op['payload']))
        if op['kind']=='function':public=public['tool']
        signature=hashlib.sha256(canonical({'kind':op['kind'],'public':public,'context':json.loads(op['context'])}).encode('utf-8')).hexdigest()
        need(policy['cache'][op['id']]['signature']==signature,'Bridge/policy public experience or context mismatch')
        expected=wire_output(op['kind'],policy['cache'][op['id']]['result']);actual=json.loads(op['result'])
        if op['kind']in('decision','query_sensor'):
            action=expected['action'];expected['action']={'actionId':op['id'],'name':action,'nativeTick':None,'nativeTicks':0,'null':expected['null']}
        need(canonical(actual)==canonical(expected),'Bridge/policy completed response mismatch')
    return {'session_id':session['id'],'status':session['status'],'phase':session['phase'],'completed_operations':len(db['operations']),
        'completed_cycles':db['boundary']['completed_cycles']if db['boundary']else None,'native_ticks':0,'coherent':True}

def preflight(args):
    bridge=load('puente/rbx02_bridge_C02.py','_C02_comparator_bridge_preflight')
    config_path=safe(args.config);config,_private_token=bridge.load_private_config(config_path)
    need(config_path.parent==PRIVATE.resolve() and config['bind']=='127.0.0.1'and config['port']==8895,'Only fixed R05 loopback8895')
    need(config['ownerUserId']==11981994305 and config['allowControl']is True,'Explicit C02 comparator account/mode required')
    need(config['worldId']in('RBX01_R05_C02_V1','RBX01_R05_C02_DEV4','RBX01_R05_C02_CTRL6'),'Known prepared C02 world')
    need(type(args.cutoff_utc_epoch)in(int,float)and time.time()<args.cutoff_utc_epoch<=MAX_CUTOFF,'Finite prospective cutoff required')
    need(args.participant in MODES and re.fullmatch(r'[A-Za-z0-9_-]{1,80}',args.run_id),'Explicit participant/run identity')
    directory=safe(args.policy_directory,exists=False)
    need(directory.is_relative_to(BASE/'comparadores') and directory!=(BASE/'comparadores'),'Explicit isolated comparator state directory')
    need(sha(BASE/'comparadores/adaptadores_C02.py')==POLICY_SHA,'Frozen policy changed')
    pins=source_pins();meta=directory/'RUNNER_IDENTITY_C02.json';policy_file=directory/'POLICY_STATE_C02.json'
    need(not(directory/'policy_writer.lock').exists(),'Existing policy writer/uncertain stale lock preserved')
    need(not policy_file.with_name(policy_file.name+'.WRITING').exists(),'Incomplete policy transaction preserved')
    database=config['databaseFile'];coherence=None
    if args.resume:
        need(config['resumeAllowed']is True and policy_file.is_file()and meta.is_file()and database.is_file(),'Bound full comparator resume required')
        identity=read(meta);policy=read(policy_file)
        need(identity['source_files_sha256']==pins and identity['participant']==args.participant and identity['run_id']==args.run_id,'Comparator code/identity changed after checkpoint')
        need(identity['database']==str(database)and identity['config_path']==str(config_path),'Transport file identity changed')
        need(policy['run_id']==args.run_id and policy['participant']==args.participant,'Own history identity mismatch')
        closures=sorted(directory.glob('CIERRE_COMPARADOR_*.json'))
        need(bool(closures),'No completed comparator closure to resume')
        closure=read(closures[-1])
        need(closure.get('policy_checkpoint',{}).get('sha256')==sha(policy_file),'Own history changed after the saved comparator closure')
        db=db_read(database);coherence=compare_states(db,policy)
        need(coherence['status']=='SUSPENDED_BOUNDARY'and db['binding']is not None,'Only explicitly bound quiescent boundary can resume')
    else:
        need(not directory.exists()or not any(directory.iterdir()),'Fresh comparator directory must be absent/empty')
        need(not database.exists(),'Fresh comparator requires an unused bridge database')
    if args.participant=='CONVENTIONAL_AI':
        prepared=read(BASE/'comparadores/MODELO_LOCAL_PREPARADO_C02.json')
        need(prepared,'Existing local model metadata required')
        ledger=read(BASE/'comparadores/CUOTA_LLM_C02.json')
        need(ledger['limit']==128 and ledger['used']<128,'Actual remaining global model quota required')
    return bridge,config_path,config,directory,pins,coherence

def serve(args):
    global _PRESERVED_POLICY,_PRESERVED_HOST
    bridge,config_path,config,directory,pins,coherence=preflight(args)
    policies=load('comparadores/adaptadores_C02.py','_C02_public_comparator_policies')
    directory.mkdir(parents=True,exist_ok=True)
    policy=policies.create(args.participant,directory,run_id=args.run_id,resume=args.resume)
    adapter=WireAdapter(policy,args.cutoff_utc_epoch);identity=directory/'RUNNER_IDENTITY_C02.json'
    if not args.resume:write_new(identity,{'schema':'DEE.RBX01.C02.comparator_runner.v1','created_utc':utc(),
        'participant':args.participant,'run_id':args.run_id,'config_path':str(config_path),'database':str(config['databaseFile']),
        'source_files_sha256':pins,'native_imported':False,'simulator_imported':False,'public_rules_sha256':policy.state['rules_sha256']})
    _config,token=bridge.load_private_config(config_path)
    host=None;server=None;monitor_done=threading.Event();drained=False;closed_reason='STARTUP_FAILED'
    start=time.time()
    try:
        host=bridge.Bridge(config['databaseFile'],token,config['ownerUserId'],adapter,world_id=config['worldId'],
            session_seconds=config['sessionSeconds'],rate_limit=config['requestsPerMinute'],allow_control=True,resume_allowed=config['resumeAllowed'])
        with host.lock:
            startup_session=host.db.execute('SELECT status FROM session WHERE singleton=1').fetchone()
            startup_audit_floor=host.db.execute('SELECT COALESCE(MAX(id),0) FROM audit').fetchone()[0]
        resume_gate=bridge.ResumeBootstrapGate(args.resume,startup_session['status']if startup_session else None,startup_audit_floor,600)
        server=bridge.BridgeHTTPServer((config['bind'],config['port']),host)
        def finite_service():
            nonlocal closed_reason
            idle=time.monotonic()+bridge.bootstrap_idle_window(config['sessionSeconds'])
            while not monitor_done.wait(.5):
                with host.lock:
                    row=host.db.execute('SELECT * FROM session WHERE singleton=1').fetchone()
                    if row:row=host._session()
                    pending=host.db.execute("SELECT 1 FROM operation WHERE status IN('QUEUED','RUNNING')").fetchone()
                    newest_resume=host.db.execute("SELECT COALESCE(MAX(id),0) FROM audit WHERE event='SESSION_RESUMED'").fetchone()[0]
                    resume_wait=resume_gate.observe(newest_resume)
                    terminal=row is not None and row['status']in('STOPPED','EXPIRED','SUSPENDED_BOUNDARY')and not pending
                    if resume_wait=='AWAIT_EXPLICIT_RESUME'and row is not None and row['status']=='SUSPENDED_BOUNDARY':terminal=False
                    expired=time.time()>=args.cutoff_utc_epoch
                    never_started=row is None and time.monotonic()>=idle
                    resume_timeout=resume_wait=='RESUME_BOOTSTRAP_TIMEOUT'and not pending
                if terminal or expired or never_started or resume_timeout:
                    closed_reason='BOUNDARY_OR_STOP'if terminal else'ABSOLUTE_CUTOFF'if expired else'RESUME_GATE_TIMEOUT_PRESERVED'if resume_timeout else'BOOTSTRAP_IDLE'
                    server.shutdown();return
        monitor=threading.Thread(target=finite_service,name='C02-comparator-finite',daemon=True);monitor.start()
        print(canonical({'status':'COMPARATOR_HOST_READY','participant':args.participant,'run_id':args.run_id,
            'bind':'127.0.0.1','port':8895,'cutoff_utc_epoch':args.cutoff_utc_epoch,'native_imported':False}),flush=True)
        server.serve_forever(poll_interval=.5)
    except KeyboardInterrupt:closed_reason='INTERRUPT_PRESERVED'
    finally:
        monitor_done.set()
        if server is not None:server.server_close()
        if host is not None:
            # Model timeout180s; preserve an unresolved writer rather than close
            # its policy files while execution is still in progress.
            try:bridge.drain_bridge(host,wait_seconds=200);drained=True
            except bridge.BridgeDrainTimeout:
                _PRESERVED_POLICY,_PRESERVED_HOST=policy,host
                print(canonical({'status':'COMPARATOR_DRAIN_TIMEOUT_PRESERVED','participant':args.participant,
                    'run_id':args.run_id,'policyWriterClosed':False,'nativeOwnerOpened':False,'noAutomaticRetry':True}),flush=True)
                raise
        if host is None or drained:
            checkpoint=policy.checkpoint()if policy.state.get('pending')is None else None
            policy.close()
            db=db_read(config['databaseFile'])if config['databaseFile'].exists()else None
            coherence=None;coherence_error=None
            if db and db['session']and checkpoint:
                try:coherence=compare_states(db,policy.state)
                except ValueError as error:coherence_error=str(error)
            report={'schema':'DEE.RBX01.C02.comparator_closure.v1','utc':utc(),'participant':args.participant,'run_id':args.run_id,
                'status':'CLOSED','closed_reason':closed_reason,'writerDrained':drained,'policyWriterClosed':True,
                'nativeOwnerOpened':False,'nativeTicks':0,'promoted':False,'wall_seconds':time.time()-start,
                'policy_checkpoint':checkpoint,'database':str(config['databaseFile']),
                'database_sha256':sha(config['databaseFile'])if config['databaseFile'].exists()else None,'coherence':coherence,'coherence_error':coherence_error,
                'world_checkpoint':'Must be captured/bound separately; this is not a Native or physical-world backup.'}
            output=directory/('CIERRE_COMPARADOR_'+str(time.time_ns())+'.json');write_new(output,report)
            print(canonical(dict(report,closure_file=str(output))),flush=True)
    return report

def prepare_config(args):
    need(args.participant in MODES,'Declared comparator only')
    need(re.fullmatch(r'[A-Za-z0-9_-]{1,64}',args.config_name),'Simple private configuration name')
    need(time.time()<args.cutoff_utc_epoch<=MAX_CUTOFF,'Finite prospective cutoff')
    PRIVATE.mkdir(exist_ok=True);config=PRIVATE/(args.config_name+'.json');token=PRIVATE/(args.config_name+'.token')
    database=PRIVATE/(args.config_name+'.sqlite3')
    need(not any(x.exists()for x in(config,token,database)),'Existing private comparator files preserved')
    seconds=max(30,min(28800,int(args.cutoff_utc_epoch-time.time())))
    data={'apiVersion':'RBX01.C02.v1','bind':'127.0.0.1','port':8895,'ownerUserId':11981994305,
        'worldId':args.world_id,'sessionSeconds':seconds,'requestsPerMinute':60,'allowControl':True,
        'tokenFile':token.name,'databaseFile':database.name,'resumeAllowed':True}
    with token.open('x',encoding='ascii')as f:f.write(secrets.token_urlsafe(48))
    write_new(config,data)
    return {'config':str(config),'participant':args.participant,'world_id':args.world_id,'token_printed':False,'native_opened':False}

def parser():
    p=argparse.ArgumentParser(description=__doc__);m=p.add_mutually_exclusive_group(required=True)
    m.add_argument('--prepare-config',action='store_true');m.add_argument('--preflight',action='store_true');m.add_argument('--serve',action='store_true')
    p.add_argument('--participant',choices=MODES,required=True);p.add_argument('--cutoff-utc-epoch',type=float,required=True)
    p.add_argument('--config',type=Path);p.add_argument('--policy-directory',type=Path);p.add_argument('--run-id');p.add_argument('--resume',action='store_true')
    p.add_argument('--config-name');p.add_argument('--world-id',choices=('RBX01_R05_C02_V1','RBX01_R05_C02_DEV4','RBX01_R05_C02_CTRL6'),default='RBX01_R05_C02_V1')
    return p

if __name__=='__main__':
    a=parser().parse_args()
    if a.prepare_config:print(canonical(prepare_config(a)))
    else:
        need(a.config and a.policy_directory and a.run_id,'Explicit config, isolated policy-directory and run-id required')
        if a.preflight:
            _,config_path,config,directory,pins,coherence=preflight(a)
            print(canonical({'status':'PREFLIGHT_ONLY','participant':a.participant,'config':str(config_path),'policy_directory':str(directory),
                'resume':a.resume,'source_files_sha256':pins,'coherence':coherence,'writes':False,'model_calls':0,'native_imported':False}))
        else:serve(a)
