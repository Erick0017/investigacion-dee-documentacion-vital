"""Passive locks/order guards for the separate FOCAL6 host. No Native imports."""
from pathlib import Path
import json, os, time, uuid
from sdk_common import RUNTIME, atomic, read, safe, sha, validate_pair

REGISTRY='estado_demo/PARTICIPANTES_FOCAL_R06.json'
SERIAL='estado_demo/SDK_NATIVE_SERIAL_R06.lock'

def other_services_closed(runtime=RUNTIME):
    runtime=Path(runtime).resolve(strict=True)
    homes=runtime/'estado_demo/instancias'
    if not homes.exists():return
    for home in homes.iterdir():
        if not home.is_dir():continue
        cfgpath=home/'INSTANCE.json'
        if not cfgpath.is_file():continue
        cfg=read(cfgpath)
        if cfg.get('validationRevision') not in ('R06','FOCAL_R06'):continue
        for name in ('SDK_SERVICE.lock','SDK_CAPABILITIES_SERVICE.lock'):
            if (home/name).exists():
                raise RuntimeError('OTHER_R06_SERVICE_LOCK_PRESERVED:'+home.name+'/'+name)

def participant_guard(instance_id, condition, runtime=RUNTIME, *, starting=False):
    runtime=Path(runtime).resolve(strict=True)
    registry=read(safe(runtime,REGISTRY,exists=True))
    rows=registry['participants']
    if [r['condition'] for r in rows] not in (['OSCILANTE'],['OSCILANTE','CONTROL']):
        raise ValueError('FROZEN_OSC_THEN_CONTROL_ORDER')
    if starting and len(rows)!=2:raise ValueError('BOTH_PREPARED_BEFORE_FIRST_FOCAL')
    own=[r for r in rows if r['instanceId']==instance_id and r['condition']==condition]
    if len(own)!=1 or own[0]['status']!='PREPARED_NOT_IMPORTED':
        raise ValueError('EXACT_RESERVED_FOCAL_PARTICIPANT')
    if starting and condition=='CONTROL':
        osc=rows[0];home=safe(runtime,'estado_demo/instancias/'+osc['instanceId'],exists=True)
        cfg=read(home/'INSTANCE.json');pair=validate_pair(home,cfg)
        ledger=read(runtime/'estado_demo/LEDGER_SDK_R06.json');world=ledger['worlds'][cfg['lifeId']]
        if (cfg['completedCycles']!=6 or world['cycles']!=6 or world['reserved']!=0
                or ledger['intents'] or pair['snapshot']['state']['completedOpportunities']!=6
                or pair['backendProof'].get('backendWriterClosed') is not True
                or pair['backendProof'].get('bridgeQuiescent') is not True):
            raise RuntimeError('OSC6_MUST_BE_SEALED_CLOSED_BEFORE_CONTROL')
    return registry

class SerialGuard:
    def __init__(self,runtime=RUNTIME):
        self.runtime=Path(runtime).resolve(strict=True)
        self.path=self.runtime/SERIAL;self.token=uuid.uuid4().hex;self.fd=None
    def acquire(self):
        other_services_closed(self.runtime)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.fd=os.open(self.path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        os.write(self.fd,json.dumps({'pid':os.getpid(),'token':self.token,'started':time.time()}).encode())
        os.fsync(self.fd)
    def release_closed(self):
        if self.fd is not None:os.close(self.fd);self.fd=None
        if read(self.path).get('token')!=self.token:raise RuntimeError('SERIAL_LOCK_IDENTITY_CHANGED')
        self.path.unlink()
    def preserve(self):
        if self.fd is not None:os.close(self.fd);self.fd=None
        # Keep the lock on any uncertain failure; never delete stale locks automatically.
