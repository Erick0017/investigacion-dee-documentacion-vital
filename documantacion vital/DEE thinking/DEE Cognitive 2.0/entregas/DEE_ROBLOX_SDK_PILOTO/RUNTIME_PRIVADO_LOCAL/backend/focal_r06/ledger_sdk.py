"""FOCAL6 accounting on the existing R06 global ledger. Never initializes it."""
from pathlib import Path
import hashlib,importlib.util,json,re,sys,time
from sdk_common import read,atomic
_spec=importlib.util.spec_from_file_location('_focal_r06_base_ledger',Path(__file__).resolve().parents[1]/'r06/ledger_sdk.py')
base=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=base;_spec.loader.exec_module(base)
base.write=atomic

class TickLedger(base.TickLedger):
    def __init__(self,path,life,max_cycles,role=None):
        self.path=Path(path).resolve();self.life=life;self.role='focal';self.max_cycles=max_cycles
        if self.path!=base.ROOT/'estado_demo/LEDGER_SDK_R06.json':
            raise ValueError('SAME_EXISTING_R06_LEDGER_REQUIRED')
        suffix=life.removeprefix(base.PREFIX)
        if not life.startswith(base.PREFIX) or re.fullmatch(r'SDK_DEMO_[0-9A-F]{16}',suffix) is None:
            raise ValueError('EXACT_FOCAL_DIAGNOSTIC_LIFE')
        cfg=read(base.ROOT/'estado_demo/instancias'/suffix/'INSTANCE.json')
        if (cfg.get('profile')!='FOCAL' or cfg.get('validationRevision')!='FOCAL_R06'
                or cfg['lifeId']!=life or max_cycles!=6 or role not in (None,'focal')):
            raise ValueError('EXPLICIT_FOCAL6_PROFILE_ONLY')
        if not self.path.is_file():raise RuntimeError('NO_LEDGER_INITIALIZATION_OR_RESET')
        self.read()

    def read(self):
        value=read(self.path);window=read(base.ROOT/'configuracion/VENTANA_R06.json')
        if (value.get('schema')!=base.SCHEMA or value.get('limit')!=40000
                or value.get('max_worlds')!=6 or value.get('sdk_global_cycles')!=3
                or window['maxNativeTicks']!=40000):
            raise ValueError('UNCHANGED_SHARED_R06_BUDGET_REQUIRED')
        if not isinstance(value.get('intents'),dict) or value['consumed']!=sum(w['consumed'] for w in value['worlds'].values()):
            raise ValueError('EXACT_SHARED_ACCOUNTING_REQUIRED')
        return value

    def register_lease(self,lease,*,expected_sha256):
        with self.lock():
            if hashlib.sha256(self.path.read_bytes()).hexdigest()!=expected_sha256:
                raise RuntimeError('SHARED_LEDGER_CHANGED')
            value=self.read()
            if value['intents']:raise RuntimeError('ANY_PENDING_INTENT_PRESERVED')
            world=value['worlds'].get(self.life)
            if world is None:
                if len(value['worlds'])>=6:raise RuntimeError('SHARED_SIX_WORLD_CAP')
                world=value['worlds'][self.life]={'consumed':0,'validation_consumed':0,'validation_cycles':0,
                    'reserved':0,'cycles':0,'role':'focal','max_cycles':6}
            if (world['role']!='focal' or world['max_cycles']!=6 or world['reserved']
                    or world['cycles']!=lease['startingCompletedCycles'] or world['consumed']!=lease['startingConsumedTicks']):
                raise RuntimeError('ACTUAL_FOCAL_COUNTERS_NO_RESET')
            if not (1<=lease['additionalCycles']<=6 and lease['cumulativeCycleCap']==world['cycles']+lease['additionalCycles']<=6):
                raise ValueError('FINITE_FOCAL6_SUPPLY')
            if not lease['validationCampaign']:raise ValueError('CURRENT_CAMPAIGN_REQUIRED')
            old=value['leases'].get(self.life)
            if old is not None:value['lease_history'].append({'life':self.life,'lease':old})
            value['leases'][self.life]=lease;atomic(self.path,value)

    def begin(self,life,identifier,mode):
        with self.lock():
            value=self.read()
            if life!=self.life or value['intents']:raise RuntimeError('ANY_PRIOR_INTENT_PRESERVED_NO_REPLAY')
            if mode not in base.MODES:raise ValueError('CLOSED_NATIVE_MODE')
            lease=value['leases'].get(life)
            if lease is None:raise RuntimeError('EXPLICIT_CLOSED_OPERATIONAL_LEASE_REQUIRED')
            world=value['worlds'][life]
            if (world['role'],world['max_cycles'])!=('focal',6):raise ValueError('SUPPLY_NEVER_RESET')
            if mode=='eci01-rbx01-decision':
                if time.time()>=lease['lastNewUtcEpoch']:raise RuntimeError('LAST_NEW_Q1_CUTOFF')
                if world['reserved'] or world['cycles']>=min(6,lease['cumulativeCycleCap']):
                    raise RuntimeError('PENDING_OR_EXHAUSTED_FOCAL_SUPPLY')
                world['reserved']=4096
                if value['validation_consumed']+sum(w['reserved'] for w in value['worlds'].values())>40000:
                    raise RuntimeError('GLOBAL40K_RESERVATION_CAP')
            elif mode!='eci01-rbx01-estado' and not world['reserved']:
                raise RuntimeError('EXISTING_EPISODE_RESERVATION_REQUIRED')
            if time.time()>=lease['hardFinishUtcEpoch']:raise RuntimeError('HARD_NATIVE_CUTOFF')
            value['intents'][life]={'life':life,'id':identifier,'mode':mode,'utc_epoch':time.time()}
            atomic(self.path,value)
