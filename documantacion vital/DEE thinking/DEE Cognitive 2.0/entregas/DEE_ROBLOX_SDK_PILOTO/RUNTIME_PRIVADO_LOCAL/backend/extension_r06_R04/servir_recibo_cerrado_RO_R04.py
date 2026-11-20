"""One original authenticated CLOSE receipt, loopback GET only, at most60s.

No Native/DEE/SQLite imports, no owner, no queue, no POST and no filesystem
mutation. Closed state/receipt/ledger SHA must be supplied by Root. All files
and owner-lock absence are rechecked immediately before delivery.
"""
from pathlib import Path, PurePosixPath
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit, parse_qs
import argparse
import hashlib
import hmac
import json
import os
import re
import time

ID=re.compile(r'SDK_DEMO_[0-9A-F]{16}')
OP=re.compile(r'[A-Za-z0-9_-]{1,90}')
HASH=re.compile(r'[0-9a-f]{64}')
MAX_FILE=8*1024*1024

def need(value,message):
    if not value:raise ValueError(message)

def root_path(path):
    p=Path(path).absolute()
    for q in reversed((p,*p.parents)):
        if os.path.lexists(q):
            s=q.lstat()
            need(not q.is_symlink() and not(getattr(s,'st_file_attributes',0)&1024),'NO_LINK_OR_REPARSE')
    return p.resolve(strict=True)

def child(root,name):
    rel=PurePosixPath(name)
    need(name and '\\' not in name and ':' not in name and not rel.is_absolute() and
         all(x not in('','.','..') for x in name.split('/')),'BOUNDED_RELATIVE_PATH')
    p=root_path(root.joinpath(*rel.parts));need(p.is_relative_to(root),'PATH_ESCAPED');return p

def raw(path):
    path=root_path(path);a=path.stat()
    need(path.is_file() and a.st_size<=MAX_FILE,'BOUNDED_REGULAR_FILE')
    value=path.read_bytes();b=path.stat()
    need((a.st_size,a.st_mtime_ns,a.st_ino)==(b.st_size,b.st_mtime_ns,b.st_ino),'FILE_CHANGED_DURING_READ')
    return value

def sha(path):return hashlib.sha256(raw(path)).hexdigest()
def read(path):return json.loads(raw(path).decode('utf-8-sig'))

class Receipt:
    def __init__(self,runtime,instance,operation,*,state_sha256,receipt_sha256,ledger_sha256):
        self.runtime=root_path(runtime)
        need(ID.fullmatch(instance) is not None and OP.fullmatch(operation) is not None,'EXACT_DIAGNOSTIC_IDS')
        for pin in(state_sha256,receipt_sha256,ledger_sha256):need(HASH.fullmatch(pin) is not None,'EXTERNAL_SHA_REQUIRED')
        self.instance=instance;self.operation=operation;self.home=child(self.runtime,'estado_demo/instancias/'+instance)
        self.pins={child(self.home,'CAPABILITIES_STATE_R06_R03.json'):state_sha256,
                   child(self.home,'capability_operations/'+operation+'.json'):receipt_sha256}
        self.statefile=next(iter(self.pins));self.receiptfile=self.home/'capability_operations'/(operation+'.json')
        self.ledgerfile=child(self.runtime,'estado_demo/LEDGER_SDK_R06.json')
        need(sha(self.ledgerfile)==ledger_sha256,'INITIAL_LEDGER_SHA_MISMATCH')
        self.cfgfile=child(self.home,'INSTANCE.json');self.pins[self.cfgfile]=sha(self.cfgfile)
        cfg=read(self.cfgfile);self.life='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_'+instance
        need(cfg['lifeId']==self.life and cfg['runtimeVersion']=='0.1.1' and cfg['validationRevision']=='R06','EXACT_R06_LIFE')
        self.sid=cfg['sessionId'];state=read(self.statefile)
        self.closed_world=read(self.ledgerfile)['worlds'][self.life]
        self.cardfile=child(self.home,'sistema/estado/vidas/'+self.life+'/VIDA.json')
        self.pins[self.cardfile]=state['closedNativeDescriptor']['cardSha256']
        self.ownerfile=child(self.home,'ENSAYOS.jsonl');self.pins[self.ownerfile]=sha(self.ownerfile)
        self.locks=('SDK_SERVICE.lock','SDK_CAPABILITIES_SERVICE.lock',
                    'sistema/estado/locks/'+self.life+'.lock',
                    'sistema/estado/vidas/'+self.life+'/FUTURO_INTERRUMPIDO.json','sistema/estado/ACTIVO.json')
        self.check()
        connection=child(self.runtime,'configuracion/CONEXION_PRIVADA.json')
        self.token=read(connection)['token']
        need(isinstance(self.token,str) and len(self.token)>=32,'PRIVATE_TOKEN_REQUIRED')

    def check(self):
        for name in self.locks:need(not os.path.lexists(self.home/name),'OWNER_OR_UNCOMMITTED_FUTURE_PRESENT')
        for path,expected in self.pins.items():need(sha(path)==expected,'CLOSED_FILE_SHA_CHANGED')
        state=read(self.statefile);row=read(self.receiptfile);ledger=read(self.ledgerfile)
        need(state['status']=='CLOSED' and state.get('lastError') is None and
             (state['instanceId'],state['sessionId'])==(self.instance,self.sid),'ACTUAL_R03_NOT_CLOSED')
        native=state['closedNativeDescriptor']
        need(native['writerClosed'] is True and native['pending']==0 and
             native['lifeId']==self.life and native['dimension']==67 and native['nativeTick']==state['nativeTick'],
             'NATIVE_DESCRIPTOR_NOT_CLOSED')
        need(row['operationId']==self.operation and row['kind']=='CLOSE' and row['status']=='COMPLETED' and
             row.get('nativeAdmissionStarted') is False and
             (row['body']['instanceId'],row['body']['sessionId'],row['body']['operationId'])==
             (self.instance,self.sid,self.operation),'ONE_ORIGINAL_COMPLETED_CLOSE_REQUIRED')
        need(all(row['value'].get(key)==value for key,value in native.items()) and
             row['value'].get('sessionId')==self.sid and row['value'].get('capabilitySequence')==state['capabilitySequence'],
             'ORIGINAL_RECEIPT_CLOSED_STATE_MISMATCH')
        world=ledger['worlds'][self.life]
        need(ledger['intents']=={} and world['reserved']==0 and
             world==self.closed_world and world.get('capability_events',0)==state['capabilitySequence'],
             'LEDGER_NOT_QUIESCENT_OR_CURSOR_MISMATCH')
        card=read(self.cardfile)
        need(card['life_id']==self.life and card['physical']['N']==67 and card['physical']['tick']==native['nativeTick'] and
             card['snapshot_sha256']==native['snapshotSha256'],'CURRENT_NATIVE_CARD_MISMATCH')
        journal=[json.loads(line) for line in raw(self.ownerfile).decode('utf-8-sig').splitlines() if line.strip()]
        need(journal and journal[-1]['kind']=='OWNER_CLOSED' and journal[-1]['exit_code']==0 and
             journal[-1]['final_status']['running'] is False,'LATEST_OWNER_NOT_CLOSED')
        return {key:row[key] for key in('operationId','kind','status','value','error','nativeAdmissionStarted','resourceWait') if key in row}

class LocalServer(HTTPServer):
    allow_reuse_address=True

def handler(receipt,delivered):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*_):pass
        def reply(self,code,value):
            data=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
            self.send_response(code);self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);self.wfile.flush()
        def do_GET(self):
            try:
                if not hmac.compare_digest(self.headers.get('Authorization',''),'Bearer '+receipt.token):
                    self.reply(401,{'ok':False,'error':{'code':'UNAUTHORIZED'}});return
                parsed=urlsplit(self.path)
                if parsed.path!='/v1/capability-operations/'+receipt.operation or parse_qs(parsed.query)!={'instanceId':[receipt.instance]}:
                    self.reply(404,{'ok':False,'error':{'code':'ONLY_ORIGINAL_CLOSE_RECEIPT'}});return
                value=receipt.check();self.reply(200,{'ok':True,'result':value});delivered[0]=True
            except BaseException as error:
                self.reply(409,{'ok':False,'error':{'code':'PRESERVE_CLOSED_EVIDENCE','message':str(error)}})
        def do_POST(self):self.reply(405,{'ok':False,'error':{'code':'READ_ONLY_NO_POST_NO_NATIVE'}})
    return Handler

def serve(receipt,port=8899,*,seconds=60,clock=time.monotonic,server_factory=LocalServer):
    need(type(seconds) is int and 1<=seconds<=60,'FINITE_RO_DELIVERY_MAX_60_SECONDS')
    need(type(port) is int and 1024<=port<=65535,'UNPRIVILEGED_LOOPBACK_PORT')
    delivered=[False];server=server_factory(('127.0.0.1',port),handler(receipt,delivered));server.timeout=1
    end=clock()+seconds
    try:
        while not delivered[0] and clock()<end:server.handle_request()
    finally:server.server_close()
    return {'status':'ORIGINAL_CLOSE_RECEIPT_DELIVERED' if delivered[0] else 'RO_DELIVERY_WINDOW_EXPIRED',
            'operationId':receipt.operation,'NativeOpened':False,'NativeExecuted':False,'filesystemModified':False}

if __name__=='__main__':
    q=argparse.ArgumentParser(description=__doc__);q.add_argument('--runtime',type=Path,required=True)
    q.add_argument('--instance',required=True);q.add_argument('--operation',required=True)
    q.add_argument('--state-sha256',required=True);q.add_argument('--receipt-sha256',required=True);q.add_argument('--ledger-sha256',required=True)
    q.add_argument('--port',type=int,default=8899);q.add_argument('--seconds',type=int,default=60);a=q.parse_args()
    receipt=Receipt(a.runtime,a.instance,a.operation,state_sha256=a.state_sha256,receipt_sha256=a.receipt_sha256,ledger_sha256=a.ledger_sha256)
    print(json.dumps({'status':'CLOSED_GUARDS_VALIDATED_BEFORE_BIND','operationId':a.operation,'NativeExecuted':False}),flush=True)
    print(json.dumps(serve(receipt,a.port,seconds=a.seconds)),flush=True)
