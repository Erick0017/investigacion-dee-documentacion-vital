"""Stdlib-only atomic R07 aggregate budget; importing starts no owner or ticks."""
from pathlib import Path
from contextlib import contextmanager
import json,os,re,time
ROOT=Path(__file__).resolve().parents[1]
LIMIT=160000;MAX_WORLDS=6;LAST_NEW=1794909600;CUTOFF=1794913620
PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_'
CAPS={'main':24,'control':6,'load':3,'pilot':3}
def role_for(life):
    suffix=life.removeprefix(PREFIX)
    if not life.startswith(PREFIX):raise ValueError('R07_ONLY_LIFE')
    if suffix=='MAIN':return'main'
    if re.fullmatch(r'CTRL[0-9]?',suffix):return'control'
    if suffix in('LOAD1','LOAD2','LOAD3'):return'load'
    if suffix=='PILOT':return'pilot'
    raise ValueError('FINITE_ROLE_ID')
def write(path,value):
    temporary=path.with_name(path.name+'.WRITING')
    with temporary.open('x',encoding='utf-8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(temporary,path)
def protected_load_slots(value):
    total=0
    for suffix in('LOAD1','LOAD2','LOAD3'):
        w=value['worlds'].get(PREFIX+suffix,{})
        total+=max(0,3-w.get('cycles',0)-int(w.get('reserved',0)>0))
    return total
class TickLedger:
    SCHEMA='DEE.RBX07.prospective_native_budget.V3.R01'
    def __init__(self,path,life,max_cycles,role=None):
        self.path=Path(path).resolve();self.life=life;self.role=role_for(life);self.max_cycles=max_cycles
        if life!='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_PILOT':raise ValueError("R07_RENEWAL_ONLY_UNUSED_PILOT")
        if role not in(None,self.role)or CAPS[self.role]!=max_cycles:raise ValueError('DECLARED_ROLE_SUPPLY')
        if not self.path.is_relative_to(ROOT):raise ValueError('ONE_R07_LEDGER')
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.lock():
            if not self.path.exists():raise RuntimeError('LEASE_REQUIRES_ORIGINAL_LEDGER_NO_RESET')
            if not self.path.exists():write(self.path,{'schema':self.SCHEMA,'limit':LIMIT,'max_worlds':MAX_WORLDS,'consumed':0,'worlds':{},'intents':{},
                'last_new_episode_epoch':LAST_NEW,'cutoff_epoch':CUTOFF,'max_ticks_per_cycle':4096,
                'protected_load_lives':[PREFIX+x for x in('LOAD1','LOAD2','LOAD3')],'protected_load_initial_slots':9,
                'historical_R06_consumed_not_new_R07_dose':53176,'source_tick_per_new_life':991187})
            self.read()
    @contextmanager
    def lock(self):
        # Technical metadata wait only. Never delete a foreign/stale lock, never
        # repeat a material request. Admission clocks are rechecked after lock.
        path=self.path.with_name(self.path.name+'.LOCK');token=os.urandom(16).hex();deadline=time.monotonic()+60
        while True:
            try:fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY);break
            except FileExistsError:
                if time.monotonic()>=deadline:raise RuntimeError('LEDGER_LOCK_PRESERVED_NO_STALE_DELETE')
                time.sleep(.02)
        try:
            with os.fdopen(fd,'w',encoding='utf-8')as f:json.dump({'pid':os.getpid(),'life':self.life,'token':token},f);f.flush();os.fsync(f.fileno())
            yield
        finally:
            if path.exists()and json.loads(path.read_text('utf-8')).get('token')==token:path.unlink()
    def read(self):
        v=json.loads(self.path.read_text('utf-8'))
        if v.get('schema')!=self.SCHEMA or v.get('limit')!=LIMIT or v.get('max_worlds')!=MAX_WORLDS or not isinstance(v.get('intents'),dict):raise ValueError('FROZEN_GLOBAL_BUDGET')
        if v.get('last_new_episode_epoch')!=LAST_NEW or v.get('cutoff_epoch')!=CUTOFF:raise ValueError('EXPLICIT_LEASE_HEADER_MIGRATION_REQUIRED')
        if v['consumed']!=sum(w['consumed']for w in v['worlds'].values()):raise ValueError('GLOBAL_DOSE_MISMATCH')
        return v
    def begin(self,life,identifier,mode):
        with self.lock():
            v=self.read()
            if life!=self.life or life in v['intents']:raise RuntimeError('PRIOR_INTENT_PRESERVED_NO_RETRY')
            if life not in v['worlds']:
                if len(v['worlds'])>=MAX_WORLDS:raise RuntimeError('SIX_WORLD_BUDGET')
                missing_load=sum(PREFIX+x not in v['worlds']for x in('LOAD1','LOAD2','LOAD3'))
                if self.role!='load'and len(v['worlds'])+1+missing_load>MAX_WORLDS:raise RuntimeError('PROTECTED_THREE_LOAD_WORLD_SLOTS')
                v['worlds'][life]={'consumed':0,'reserved':0,'cycles':0,'max_cycles':self.max_cycles,'role':self.role}
            w=v['worlds'][life]
            if w['max_cycles']!=self.max_cycles or w['role']!=self.role:raise ValueError('SUPPLY_CANNOT_RESET')
            if mode=='eci01-rbx01-decision':
                if time.time()>=LAST_NEW:raise RuntimeError('NO_NEW_Q1_AFTER23UTC')
                if w['reserved']or w['cycles']>=self.max_cycles:raise RuntimeError('OPPORTUNITY_PENDING_OR_EXHAUSTED')
                w['reserved']=4096
                protected=protected_load_slots(v)*4096
                if v['consumed']+sum(x['reserved']for x in v['worlds'].values())+protected>LIMIT:raise RuntimeError('BUDGET_OR_PROTECTED_LOAD_ALLOCATION')
            elif mode not in('eci01-rbx01-query-sensor','eci01-rbx01-function','eci01-rbx01-feedback','eci01-rbx01-estado'):raise ValueError('CLOSED_NATIVE_MODES')
            elif mode!='eci01-rbx01-estado'and not w['reserved']:raise RuntimeError('NO_RESERVED_PARENT_OPPORTUNITY')
            if time.time()>=CUTOFF:raise RuntimeError('ABSOLUTE00_07UTC_NOV17_CUTOFF')
            v['intents'][life]={'life':life,'id':identifier,'mode':mode,'utc_epoch':time.time()};write(self.path,v)
    def finish(self,life,identifier,before,after,mode):
        with self.lock():
            v=self.read();i=v['intents'].get(life);w=v['worlds'][life]
            if not i or(i['life'],i['id'],i['mode'])!=(life,identifier,mode):raise RuntimeError('EXACT_ACTUAL_INTENT_REQUIRED')
            n=after-before
            if not(0<=n<=w['reserved'])and not(mode=='eci01-rbx01-estado'and n==0):raise RuntimeError('UNEXPECTED_ADVANCE_INTENT_PRESERVED')
            v['consumed']+=n;w['consumed']+=n;w['reserved']-=n
            if mode=='eci01-rbx01-feedback':w['reserved']=0;w['cycles']+=1
            if w['consumed']>self.max_cycles*4096 or v['consumed']>LIMIT:raise RuntimeError('BUDGET_EXCEEDED_PRESERVED')
            w['last_completed']={**i,'before_tick':before,'after_tick':after,'actual_ticks':n};v['last_completed']=w['last_completed'];del v['intents'][life];write(self.path,v)
