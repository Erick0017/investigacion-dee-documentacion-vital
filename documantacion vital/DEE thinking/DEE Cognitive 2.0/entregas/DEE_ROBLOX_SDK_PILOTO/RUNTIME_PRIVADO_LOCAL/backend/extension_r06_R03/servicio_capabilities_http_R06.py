"""Separate authenticated ASSISTED capabilities service after actual SDK K4.

No Native is imported on module import. Explicit start opens exactly one
official owner. POST stores one ID; GET never requeues material. CORE26 is
imported only for frozen filesystem/resource contracts, never edited.
"""
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit,parse_qs
import argparse
import hmac
import importlib.util
import json
import os
import queue
import sys
import threading
import time
sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'r06'))
from sdk_common import RUNTIME,atomic,canonical,closed_native,digest,instance_home,read,sha,IDENTIFIER
from native_factory import free_memory
from resource_wait import wait_for_resource,ResourceWaitExpired,BOOT_FREE_BYTES,PHASE_FREE_BYTES
from sdk_capabilities_R06 import MODE,VERSION,validate_request

class Conflict(RuntimeError):pass
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class Service:
    def __init__(self,instance,*,memory=free_memory,factory=None,token=None):
        self.home,self.cfg=instance_home(instance);self.scope=read(self.home/'sistema/capacidades/SDK_CAPABILITIES_SCOPE_R06.json')
        self.instance=instance;self.sid=self.cfg['sessionId'];self.life=self.cfg['lifeId']
        if (self.scope['lifeId'],self.scope['allowedLifeIds'],self.scope['sessionId'])!=(self.life,[self.life],self.sid):
            raise Conflict('Absolute per-instance capabilities scope required')
        if (self.home/'SDK_SERVICE.lock').exists():raise Conflict('Normal SDK owner must be closed')
        self.statefile=self.home/'CAPABILITIES_STATE_R06_R03.json';self.saved=read(self.statefile)
        proof=closed_native(self.home,self.cfg)
        if proof['nativeTick']!=self.saved['nativeTick']:raise Conflict('Unexpected Native change; do not reopen')
        expected=self.saved.get('closedNativeDescriptor')
        if expected and any(proof[k]!=expected[k] for k in ('nativeTick','snapshotSha256','databaseSha256','cardSha256')):
            raise Conflict('Closed Native descriptor changed')
        self.native_tick=proof['nativeTick'];self.sequence=self.saved['capabilitySequence']
        self.token=token or read(RUNTIME/'configuracion/CONEXION_PRIVADA.json')['token']
        if not isinstance(self.token,str) or len(self.token)<32:raise ValueError('Private token required')
        self.lockfile=self.home/'SDK_CAPABILITIES_SERVICE.lock'
        self.fd=os.open(self.lockfile,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        os.write(self.fd,canonical({'pid':os.getpid(),'instanceId':instance,'startedUtcEpoch':time.time()}).encode());os.fsync(self.fd)
        self.folder=self.home/'capability_operations';self.folder.mkdir(exist_ok=True)
        self.lock=threading.RLock();self.work=queue.Queue();self.memory=memory;self.factory=factory
        self.owner=None;self.status='STARTING';self.last_error=None;self.resource=None;self.stop=False
        if any(read(p)['status'] in ('PENDING','PENDING_RESOURCE','RUNNING','UNCERTAIN') for p in self.folder.glob('*.json')):
            self.status='PRESERVED_UNCERTAIN';self.last_error={'code':'PRIOR_OPERATION_NO_REPLAY'};self.thread=None
        else:
            self.thread=threading.Thread(target=self.worker,name='SDK-capabilities-single-owner',daemon=False);self.thread.start()
    def operation(self,identifier):
        if not isinstance(identifier,str) or IDENTIFIER.fullmatch(identifier) is None:raise ValueError('Finite operation ID')
        p=self.folder/(identifier+'.json')
        if not p.is_file():raise KeyError('Unknown operation')
        row=read(p);return {k:row[k] for k in ('operationId','kind','status','value','error','nativeAdmissionStarted','resourceWait') if k in row}
    def handshake(self):
        return {'instanceId':self.instance,'sessionId':self.sid,'lifeId':self.life,
            'extensionVersion':VERSION,'status':self.status,
            'capabilities':['RECALL','LESSON','NUMERIC','SOLVE','COMPOSE','COMPARE'],
            'nativeTick':self.native_tick,'capabilitySequence':self.sequence,
            'limits':{'maxEvents':self.scope['maxEvents'],'maxTicksPerEvent':4096,'globalNativeTicks':40000,
                'lastNewUtcEpoch':self.scope['lastNewUtcEpoch'],'hardFinishUtcEpoch':self.scope['native_cutoff_utc_epoch']},
            'postK4Guard':True,'worldBinding':'PRE_CAP_SDK_PAIR_NOT_CURRENT_AFTER_NATIVE_ADVANCE',
            'preCapDescriptor':self.saved['preCapDescriptor'],'lastError':self.last_error,
            'resourceWait':self.resource,'backendWriterClosed':self.owner is None}
    def submit(self,body,*,close=False):
        expected={'instanceId','sessionId','operationId'} | (set() if close else {'request'})
        if not isinstance(body,dict) or set(body)!=expected:raise ValueError('Exact capability DTO')
        if (body['instanceId'],body['sessionId'])!=(self.instance,self.sid):raise Conflict('Actual instance/session required')
        op=body['operationId']
        if not isinstance(op,str) or IDENTIFIER.fullmatch(op) is None:raise ValueError('Finite original operation ID')
        if not close:validate_request(body['request'])
        signature=digest({'close':close,'body':body});p=self.folder/(op+'.json')
        with self.lock:
            if p.exists():
                if read(p)['requestSha256']!=signature:raise Conflict('Existing operation bytes changed')
                return self.operation(op)
            if (close and self.status=='FAILED_PRESERVED' and self.owner is None and
                    (self.thread is None or not self.thread.is_alive()) and self.work.empty()):
                prior=[read(x) for x in self.folder.glob('*.json')]
                if any(x['status'] in('PENDING','PENDING_RESOURCE','RUNNING','UNCERTAIN') for x in prior):
                    raise Conflict('Preserve every pending/uncertain operation; no failed-boot close')
                if read(RUNTIME/'estado_demo/LEDGER_SDK_R06.json')['intents']:
                    raise Conflict('Native ledger intent prevents administrative exit')
                native=closed_native(self.home,self.cfg)
                if native['nativeTick']!=self.native_tick:raise Conflict('Exact closed Native tick required')
                value={**native,'kind':'FAILED_BOOT_ADMIN_CLOSED_R06','errorPreserved':self.last_error,
                       'newNativeTicks':0,'materialRetried':False,'worldPairCurrent':False}
                row={'operationId':op,'kind':'CLOSE','body':body,'requestSha256':signature,
                     'status':'COMPLETED','value':value,'nativeAdmissionStarted':False,'completedUtcEpoch':time.time()}
                atomic(p,row,new=True);self.stop=True;return self.operation(op)
            if self.status!='READY':raise Conflict('Capabilities owner not ready; preserve state')
            if any(read(x)['status'] in('PENDING','PENDING_RESOURCE','RUNNING','UNCERTAIN') for x in self.folder.glob('*.json')):
                raise Conflict('Only one original material capability at a time')
            if not close and (time.time()>=self.scope['lastNewUtcEpoch'] or self.sequence>=self.scope['maxEvents']):
                raise Conflict('Finite capability admission cutoff/horizon')
            row={'operationId':op,'kind':'CLOSE' if close else body['request']['kind'],'body':body,
                 'requestSha256':signature,'status':'PENDING','nativeAdmissionStarted':False,'admittedUtcEpoch':time.time()}
            if not close:row['capabilitySequence']=self.sequence+1
            atomic(p,row,new=True);self.work.put(op);return self.operation(op)
    def wait_resource(self,required,row=None,path=None,boot_deadline=None):
        end=self.scope['native_cutoff_utc_epoch']
        if row is None or row['kind']!='CLOSE':end=min(end,self.scope['lastNewUtcEpoch'])
        if boot_deadline is not None:end=min(end,boot_deadline)
        if row is not None:
            row.setdefault('resourceDeadlineUtcEpoch',min(time.time()+900,end));end=min(end,row['resourceDeadlineUtcEpoch'])
        def sample(v):
            self.resource=v
            if v['free']<required:
                self.status='PENDING_RESOURCE'
                if row is not None:row.update(status='PENDING_RESOURCE',resourceWait=v,nativeAdmissionStarted=False);atomic(path,row)
        value=wait_for_resource(required,deadline_utc=end,memory=self.memory,on_sample=sample)
        self.resource=None;self.status='READY' if self.owner is not None else 'STARTING';return value
    def make_owner(self):
        module=load(RUNTIME/'backend/extension_r06/owner_caps_R06.py','_sdk_capabilities_official_owner')
        return module.configured_owner(RUNTIME/'dependencias/producto',self.home,RUNTIME/'estado_demo/LEDGER_SDK_R06.json',
            tag='SDK_CAP_R06',cutoff_epoch=self.scope['native_cutoff_utc_epoch'],continuous=True)
    def save_state(self,status,**extra):
        self.saved.update(status=status,nativeTick=self.native_tick,capabilitySequence=self.sequence,**extra)
        atomic(self.statefile,self.saved)
    def worker(self):
        manager=None
        try:
            self.wait_resource(BOOT_FREE_BYTES,boot_deadline=time.time()+900)
            manager=(self.factory or self.make_owner)();self.owner=manager.__enter__();self.status='READY'
            while time.time()<self.scope['native_cutoff_utc_epoch']:
                try:op=self.work.get(timeout=1)
                except queue.Empty:continue
                p=self.folder/(op+'.json');row=read(p)
                try:
                    if row['kind']=='CLOSE':
                        row.update(status='RUNNING',nativeAdmissionStarted=False);atomic(p,row)
                        closing,manager=manager,None;closing.__exit__(None,None,None);self.owner=None
                        proof=closed_native(self.home,self.cfg)
                        value={**proof,'kind':'CLOSED_NATIVE_CAPABILITY_DESCRIPTOR_R06','sessionId':self.sid,
                               'capabilitySequence':self.sequence,'preCapDescriptor':self.saved['preCapDescriptor'],
                               'worldPairCurrent':False,'noIndependentRollbackClaim':True}
                        self.save_state('CLOSED',closedNativeDescriptor=proof)
                        row.update(status='COMPLETED',value=value,completedUtcEpoch=time.time());atomic(p,row)
                        self.status='CLOSED';self.stop=True;break
                    literal={'modo':MODE,'request':row['body']['request'],
                        'context':{'operation_id':op,'session_id':self.sid,'capability_sequence':row['capabilitySequence']}}
                    while True:
                        self.wait_resource(PHASE_FREE_BYTES,row,p)
                        row.update(status='RUNNING',nativeAdmissionStarted=True,startedUtcEpoch=time.time());atomic(p,row)
                        # Last host guard is still before owner.material/ledger.begin.
                        if self.memory()<PHASE_FREE_BYTES:
                            row.update(status='PENDING_RESOURCE',nativeAdmissionStarted=False);atomic(p,row);continue
                        result=self.owner.material(op,literal,feedback='omit',actuator='closed');break
                    rows=result.get('rows')
                    if rows is None and isinstance(result.get('result'),dict):rows=result['result'].get('rows')
                    if not isinstance(rows,list) or len(rows)!=1 or rows[0].get('version')!=VERSION:
                        raise RuntimeError('Exact Native capability result absent; preserve original ID')
                    value=rows[0];self.native_tick=value['nativeTick'];self.sequence=row['capabilitySequence']
                    self.save_state('ACTIVE_PRE_CAP_WORLD_HISTORICAL')
                    row.update(status='COMPLETED',value=value,completedUtcEpoch=time.time());atomic(p,row)
                except ResourceWaitExpired as error:
                    row.update(status='FAILED_KNOWN',nativeAdmissionStarted=False,error={'code':'RESOURCE_WAIT_EXPIRED','message':str(error),'preNativeAdmissionGuaranteed':True})
                    atomic(p,row);self.status='FAILED_PRESERVED';self.last_error=row['error'];break
                except BaseException as error:
                    row.update(status='UNCERTAIN',error={'code':'PRESERVED_NO_REPLAY','message':str(error)})
                    atomic(p,row);self.status='PRESERVED_UNCERTAIN';self.last_error=row['error'];break
        except BaseException as error:
            self.status='FAILED_PRESERVED';self.last_error={'code':'OWNER_START_OR_CLOSE_FAILED','message':str(error)}
        finally:
            if manager is not None:
                try:manager.__exit__(None,None,None)
                except BaseException as error:self.status='PRESERVED_UNCERTAIN';self.last_error={'code':'CLOSE_UNCERTAIN','message':str(error)}
            self.owner=None
            try:
                final=closed_native(self.home,self.cfg)
                self.native_tick=final['nativeTick']
                if self.last_error is None:self.status='CLOSED'
                self.save_state(self.status,closedNativeDescriptor=final,lastError=self.last_error,
                                worldPairCurrent=False)
            except BaseException as error:
                self.status='PRESERVED_UNCERTAIN';self.last_error={'code':'FINAL_CLOSED_PROOF_UNAVAILABLE','message':str(error)}
    def release(self):
        if self.thread is not None and self.thread.is_alive():raise Conflict('Native owner still active')
        os.close(self.fd);self.lockfile.unlink()

def handler(service):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*_):pass
        def reply(self,code,value):
            data=canonical(value).encode();self.send_response(code);self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
        def route(self):
            if not hmac.compare_digest(self.headers.get('Authorization',''),'Bearer '+service.token):
                self.reply(401,{'ok':False,'error':{'code':'UNAUTHORIZED'}});return
            parsed=urlsplit(self.path)
            if self.command=='GET':
                if parsed.path=='/v1/capabilities/handshake':value=service.handshake()
                elif parsed.path.startswith('/v1/capability-operations/'):
                    if parse_qs(parsed.query).get('instanceId')!=[service.instance]:raise Conflict('Exact instance query')
                    value=service.operation(parsed.path.removeprefix('/v1/capability-operations/'))
                else:raise KeyError('Unknown capability route')
                self.reply(200,{'ok':True,'result':value});return
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=8192:raise ValueError('Bounded capability JSON request')
            body=json.loads(self.rfile.read(length))
            if parsed.path=='/v1/capabilities/submit':value=service.submit(body)
            elif parsed.path=='/v1/capabilities/close':value=service.submit(body,close=True)
            else:raise KeyError('Unknown capability route')
            self.reply(202,{'ok':True,'result':value})
        def execute(self):
            try:self.route()
            except Conflict as e:self.reply(409,{'ok':False,'error':{'code':'PRESERVE_CONFLICT','message':str(e)}})
            except KeyError as e:self.reply(404,{'ok':False,'error':{'code':'NOT_FOUND','message':str(e)}})
            except (ValueError,TypeError) as e:self.reply(400,{'ok':False,'error':{'code':'SCHEMA','message':str(e)}})
            except BaseException as e:self.reply(500,{'ok':False,'error':{'code':'PRESERVE_INTERNAL','message':str(e)}})
        do_GET=execute;do_POST=execute
    return Handler

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--instance',required=True)
    p.add_argument('--port',type=int,default=8899);p.add_argument('--start-real-native',action='store_true');a=p.parse_args()
    if not a.start_real_native:p.error('Explicit Root material flag required')
    if not 1024<=a.port<=65535:p.error('Unprivileged loopback port')
    server=ThreadingHTTPServer(('127.0.0.1',a.port),BaseHTTPRequestHandler);server.timeout=1;s=None
    try:
        s=Service(a.instance);server.RequestHandlerClass=handler(s)
        while not s.stop and time.time()<s.scope['native_cutoff_utc_epoch']:server.handle_request()
    finally:
        server.server_close()
        if s is not None:
            if s.thread is not None:s.thread.join(650)
            s.release()
