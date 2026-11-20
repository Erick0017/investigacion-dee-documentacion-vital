"""Persistent life manager. Routing is explicit, never chosen from audit targets."""
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime,timezone
from uuid import uuid4
import json,os,re,sys
import dee_thinking as d
from dee_thinking import RepertoireSession,IntegratedSession
from dee_thinking.remote_reader import RemoteReaderSession
from dee_thinking.persistence import encode_metadata,decode_metadata,load_world_snapshot,save_world_snapshot
from dee_thinking.consolidated import exact_receipt
from .native_tools import SYSTEM_KEY,identity,physical,observe,atomic_json,digest_file

SYSTEM_ROOT=Path(__file__).resolve().parents[1]

class MutationRecordedError(RuntimeError):
    def __init__(self,original,record):
        self.recorded_operation={'life_id':record['life_id'],'snapshot_sha256':record['snapshot_sha256'],'tick':record['physical']['tick'],'failed_attempt_preserved':True,'no_implicit_rollback':True,'original_error_type':type(original).__name__}
        super().__init__(type(original).__name__+': '+str(original)+'; failed attempt saved at tick '+str(record['physical']['tick'])+' snapshot '+record['snapshot_sha256'])
def now():return datetime.now(timezone.utc).isoformat()
def validate_id(value):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,90}',value):raise ValueError('Life ID requires1–91 ASCII letters/digits/_.-')
    return value
def read(path):return json.loads(Path(path).read_text(encoding='utf8'))
def legacy_class():
    source=SYSTEM_ROOT/'organizaciones/cpc9/src'
    if str(source)not in sys.path:sys.path.insert(0,str(source))
    from vida_repertorio_extension import MainWithRepertoire
    return MainWithRepertoire

class WorldAdapter:
    def __init__(self,world):self.world=world
    @property
    def tick(self):return int(self.world.runtime.current_tick)
    def run_until(self,tick):return self.world.run_until(tick)
    def save(self,path):return save_world_snapshot(self.world,path,compress=True)

def load_adapter(profile,path):
    if profile=='cpc9_integral_n67':return legacy_class().load(path)
    if profile=='repertorio_fisico_4_5':return RepertoireSession.load(path)
    if profile=='u0_integrado_4_5':return IntegratedSession.load(path)
    if profile=='fisica_directa':return WorldAdapter(load_world_snapshot(path)[0])
    if profile=='repertorio_n67_independiente':
        source=SYSTEM_ROOT/'capacidades'
        if str(source)not in sys.path:sys.path.insert(0,str(source))
        # Explicit name avoids collision with the recovered primitive module.
        import importlib.util
        spec=importlib.util.spec_from_file_location('_dcs11_repertoire_adapter',source/'repertorio_n67.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        return module.SystemRepertoire67.load(path)
    raise ValueError('Profile is not an admitted loader: '+profile)

def build_adapter(profile,life_id,parameters):
    if profile=='cpc9_integral_n67':return legacy_class().create(identifier=life_id,**parameters)
    if profile=='repertorio_fisico_4_5':return RepertoireSession.create(identifier=life_id,**parameters)
    if profile=='u0_integrado_4_5':return IntegratedSession.create(identifier=life_id,**parameters)
    if profile=='fisica_directa':
        n=parameters.pop('N',11)
        if parameters:raise ValueError('Unknown direct-physics preparation arguments')
        return WorldAdapter(d.OrganizationalWorld.create(d.OrganizationRecipe.research(n,[],0)))
    if profile=='repertorio_n67_independiente':
        import importlib.util
        spec=importlib.util.spec_from_file_location('_dcs11_repertoire_adapter',SYSTEM_ROOT/'capacidades/repertorio_n67.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        return module.SystemRepertoire67.create(identifier=life_id,**parameters)
    raise ValueError('Unknown/unadmitted preparation profile')

class Store:
    def __init__(self,root=None):
        self.root=Path(root or SYSTEM_ROOT).resolve();self.state=self.root/'estado';identity(self.root)
    def life_dir(self,life):return self.state/'vidas'/validate_id(life)
    def record(self,life=None):
        selected_default=life is None;active=None
        if life is None:
            active=read(self.state/'ACTIVO.json');life=active.get('life_id',active.get('preferred_life'))
            if not life:raise ValueError('No active life. Use an explicit create/import/fork operation.')
        rec=read(self.life_dir(life)/'VIDA.json')
        if selected_default and active.get('snapshot_sha256')and rec.get('snapshot_sha256')!=active['snapshot_sha256']:raise ValueError('ACTIVE_POINTER_OUT_OF_SYNC: restore the explicit life and reselect it; never rewind it silently')
        return rec
    def snapshot(self,record):
        p=(self.root/record['snapshot']).resolve(strict=True)
        if not p.is_relative_to(self.state.resolve()):raise ValueError('Operational state outside system package')
        expected=record.get('snapshot_sha256',(record.get('parent')or{}).get('encoded_sha256'))
        if expected and digest_file(p)!=expected:raise ValueError('Life snapshot hash mismatch')
        return p
    def load(self,life=None):
        rec=self.record(life)
        interrupted=self.life_dir(rec['life_id'])/'FUTURO_INTERRUMPIDO.json'
        if interrupted.exists():raise ValueError('INTERRUPTED_NATIVE_FUTURE: the latest committed pointer is not the last evolved state. Inspect '+str(interrupted)+'; explicitly branch/import an identified full checkpoint, never silently rewind this life.')
        journal=self.life_dir(rec['life_id'])/'HISTORIA.jsonl'
        if journal.exists():
            lines=journal.read_text(encoding='utf8').splitlines()
            if lines and json.loads(lines[-1])['snapshot_sha256']!=rec.get('snapshot_sha256'):raise ValueError('INCOMPLETE_COMMIT: journal and life pointer disagree; no automatic old-state fallback or life rewind')
        a=load_adapter(rec['profile'],self.snapshot(rec))
        expected=rec['physical'];actual=physical(a.world)
        for key in('tick','RAW_sha256','clocks_sha256'):
            if actual[key]!=expected[key]:raise ValueError('Life state changed under the recorded identity')
        if actual['N']!=expected['N']:raise ValueError('Dimension changed under the same life')
        entries=dict(a.world.runtime.snapshot_metadata_entries)
        if SYSTEM_KEY in entries:
            m=decode_metadata(entries[SYSTEM_KEY])
            if m['life_id']!=rec['life_id']or m['world_id']!=rec['world_id']:raise ValueError('Native system metadata identity differs')
        return rec,a
    @contextmanager
    def writer(self,world_id):
        folder=self.state/'locks';folder.mkdir(parents=True,exist_ok=True);path=folder/(validate_id(world_id)+'.lock');token=uuid4().hex
        fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
        with os.fdopen(fd,'w',encoding='ascii')as f:json.dump({'pid':os.getpid(),'token':token},f)
        try:yield
        finally:
            if path.exists()and read(path).get('token')==token:path.unlink()
    def commit(self,rec,adapter,operation,*,activate=False):
        life=validate_id(rec['life_id']);directory=self.life_dir(life);directory.mkdir(parents=True,exist_ok=True)
        rec=dict(rec);old=rec.get('snapshot_sha256',(rec.get('parent')or{}).get('encoded_sha256'));rec['software_version']='1.1.0';rec['updated_utc']=now()
        rec['operations']=list(rec.get('operations',[]))+[operation]
        offset=rec.get('operation_count_offset',0)
        if type(offset)is not int or offset<0:raise ValueError('Operation-count archive offset must be an exact nonnegative integer')
        context={'schema':'DCS1.1.life.native_metadata.v1','life_id':life,'world_id':rec['world_id'],'profile':rec['profile'],'branch':rec['branch'],'parent':rec.get('parent'),'software_version':'1.1.0','tick':int(adapter.tick),'previous_checkpoint_sha256':old,'operation_count':offset+len(rec['operations'])}
        adapter.world.runtime.set_snapshot_metadata(SYSTEM_KEY,encode_metadata(context))
        filename=life+'.T'+str(adapter.tick)+'.'+uuid4().hex[:12]+'.deetsnap.gz';target=self.state/'checkpoints'/filename
        storage=adapter.save(target);rec.update(snapshot=target.relative_to(self.root).as_posix(),snapshot_sha256=digest_file(target),storage=storage,physical=physical(adapter.world,occupation=True),interfaces=len(adapter.world.interfaces),protocols=len(adapter.world.protocols),availability='CONTINUABLE_WITH_DECLARED_PROTOCOL')
        journal=directory/'HISTORIA.jsonl'
        with journal.open('a',encoding='utf8')as f:json.dump({'life_id':life,'previous_snapshot_sha256':old,'snapshot_sha256':rec['snapshot_sha256'],'tick':int(adapter.tick),'operation':operation,'timestamp':rec['updated_utc']},f,ensure_ascii=False);f.write('\n');f.flush();os.fsync(f.fileno())
        atomic_json(directory/'VIDA.json',rec)
        activefile=self.state/'ACTIVO.json';active=read(activefile)if activefile.exists()else{}
        if activate or active.get('life_id',active.get('preferred_life'))==life:
            atomic_json(activefile,{'schema':'DCS1.1.active.v1','life_id':life,'profile':rec['profile'],'world_id':rec['world_id'],'snapshot':rec['snapshot'],'snapshot_sha256':rec['snapshot_sha256'],'tick':int(adapter.tick),'updated_utc':now(),'no_implicit_new_world':True})
        return rec
    def create(self,life,profile,parameters=None,activate=False):
        validate_id(life)
        if self.life_dir(life).exists():raise FileExistsError('Life identity is already present; use fork or continue')
        rec={'schema':'DCS1.1.life.v1','life_id':life,'world_id':life,'profile':profile,'branch':'NEW_PREPARATION_T0','parent':None,'created_utc':now(),'parameters':dict(parameters or{}),'knowledge':'No objective associations are imported; acquisition requires later experience.','memberships':[{'id':life,'role':'Whole runtime, not a duplicate per internal region'}]}
        with self.writer(life):return self.commit(rec,build_adapter(profile,life,dict(parameters or{})),{'kind':'CREATE_T0','parameters':parameters or{}},activate=activate)
    def fork(self,source,target,*,activate=False,kind='EXACT_FORK',checkpoint=None):
        validate_id(target)
        if self.life_dir(target).exists():raise FileExistsError('Fork identity already exists')
        parent=self.record(source);source_file=self.snapshot(parent)
        if checkpoint:
            source_file=(self.root/checkpoint).resolve(strict=True)
            if not source_file.is_relative_to((self.state/'checkpoints').resolve()):raise ValueError('Fork checkpoint must be in the system operational state')
            a=load_adapter(parent['profile'],source_file);entries=dict(a.world.runtime.snapshot_metadata_entries)
            if SYSTEM_KEY in entries and decode_metadata(entries[SYSTEM_KEY])['life_id']!=parent['life_id']:raise ValueError('Checkpoint belongs to a different life; use explicit import')
        else:
            parent,a=self.load(source)
            source_file=self.snapshot(parent)
        record={'schema':'DCS1.1.life.v1','life_id':target,'world_id':target,'profile':parent['profile'],'branch':kind,'parent':{'life_id':parent['life_id'],'snapshot_sha256':digest_file(source_file),'tick':int(a.tick),'historical_parent':parent.get('parent')},'created_utc':now(),'legacy_identifier':getattr(a,'identifier',None),'knowledge':'Inherited only through exact complete parent state, not newly acquired by this fork','memberships':parent.get('memberships',[{'id':target,'role':'Whole runtime including inherited internal regions'}])}
        with self.writer(target):return self.commit(record,a,{'kind':kind,'past_unchanged_through_tick':int(a.tick),'parent_physical':physical(a.world)},activate=activate)
    def import_state(self,path,life,profile,expected=None):
        import shutil
        validate_id(life);path=Path(path).resolve(strict=True);actual=digest_file(path)
        if expected and actual!=expected:raise ValueError('Explicit imported snapshot identity mismatch')
        if self.life_dir(life).exists():raise FileExistsError('Imported life identity already present')
        if path.suffix!='.gz':raise ValueError('System imported operational storage currently requires an explicit .gz snapshot')
        target=self.state/'checkpoints'/('import.'+life+'.'+actual[:16]+'.deetsnap.gz')
        if target.exists():raise FileExistsError('Existing import copy protected')
        with path.open('rb')as src,target.open('xb')as dst:shutil.copyfileobj(src,dst)
        adapter=load_adapter(profile,target);rec={'schema':'DCS1.1.life.v1','life_id':life,'world_id':life,'profile':profile,'branch':'EXPLICIT_IMPORTED_CONTINUITY','parent':{'encoded_sha256':actual,'source_name':path.name,'source_tick':int(adapter.tick)},'created_utc':now(),'legacy_identifier':getattr(adapter,'identifier',None),'knowledge':'Inherited native state only; no acquisition is attributed to import'}
        with self.writer(life):return self.commit(rec,adapter,{'kind':'IMPORT_COMPLETE_STATE','source_sha256':actual,'new_preparation':False,'native_tick_preserved':int(adapter.tick)})
    def export_life(self,life,output):
        import shutil
        rec,adapter=self.load(life);output=Path(output).resolve()
        if output.exists():raise FileExistsError('Export output must be a new directory')
        output.mkdir(parents=True);source=self.snapshot(rec);target=output/'VIDA.deetsnap.gz'
        with source.open('rb')as src,target.open('xb')as dst:shutil.copyfileobj(src,dst)
        atomic_json(output/'EXPORTACION.json',{'schema':'DCS1.1.whole_life_export.v1','life':rec,'snapshot':'VIDA.deetsnap.gz','sha256':digest_file(target),'physical':physical(adapter.world),'required_instrument':'Official DEE thinking4.5 plus DCS1.1 matching profile code','not_a_new_individual':True,'memberships_share_one_snapshot':True})
        return{'path':str(output),'snapshot_sha256':digest_file(target),'tick':int(adapter.tick),'files':2}
    def mutate(self,life,kind,callback,details=None):
        rec=self.record(life)
        if rec['branch']=='HISTORICAL_IMPORTED_CHECKPOINT':raise ValueError('Imported historical checkpoints are protected; create an explicit fork before continuing')
        with self.writer(rec['world_id']):
            rec,a=self.load(rec['life_id']);before=physical(a.world)
            try:result=callback(a)
            except Exception as error:
                # A compound request can admit an input before a later argument
                # fails. Never discard its pending queue or evolved native world
                # and silently return a favorable previous checkpoint.
                failed={'kind':'FAILED_'+kind,'before':before,'after':physical(a.world),'details':details or{},'error':{'type':type(error).__name__,'detail':str(error)},'no_implicit_rollback':True}
                rec=self.commit(rec,a,failed)
                raise MutationRecordedError(error,rec)from error
            op={'kind':kind,'before':before,'after':physical(a.world),'details':details or{},'result':result}
            rec=self.commit(rec,a,op);return{'INSTRUMENTO':{'life_id':rec['life_id'],'profile':rec['profile'],'operation':kind,'tick':int(a.tick),'snapshot_sha256':rec['snapshot_sha256']},'result':result,'physical':rec['physical']}
    def status(self,life=None):
        rec,a=self.load(life);return{'INSTRUMENTO':{'software':'1.1.0','life_id':rec['life_id'],'profile':rec['profile'],'branch':rec['branch'],'parent':rec.get('parent'),'tick':int(a.tick),'N':int(a.world.runtime.dimension),'interfaces':len(a.world.interfaces),'snapshot_sha256':digest_file(self.snapshot(rec))},'physical':physical(a.world,occupation=True),'INTERPRETACION':'Loading verifies the complete stored world; functional access must be tested by declared probes. No new individual is created.'}
    def list_lives(self):
        rows=[]
        for path in sorted((self.state/'vidas').glob('*/VIDA.json')):
            record=read(path)
            if(path.parent/'FUTURO_INTERRUMPIDO.json').exists():record={**record,'availability':'INTERRUPTED_UNRECORDED_FUTURE_NORMAL_LOAD_BLOCKED','continuity_warning':'The stored pointer is historical, not the last evolved state; explicit full-cut branch/import required.'}
            rows.append(record)
        return rows
    def select(self,life):
        rec,a=self.load(life)
        if rec['branch']=='HISTORICAL_IMPORTED_CHECKPOINT':raise ValueError('Select a validated continuation fork, not a protected historical parent')
        with self.writer(rec['world_id']):
            atomic_json(self.state/'ACTIVO.json',{'schema':'DCS1.1.active.v1','life_id':rec['life_id'],'world_id':rec['world_id'],'profile':rec['profile'],'tick':int(a.tick),'snapshot':rec['snapshot'],'snapshot_sha256':digest_file(self.snapshot(rec)),'selection':'EXPLICIT_USER_OR_RECORDED_PROMOTION','updated_utc':now()})
        return self.status(life)
    def promote(self,life,decision):
        """An explicit human/auditor decision, not an automatic cognition score."""
        data=read(decision);rec,a=self.load(life)
        required=('decision_id','route','scope','gains','losses','uncertainties','evidence','regression_coverage')
        if any(k not in data for k in required):raise ValueError('Promotion requires a reasoned decision with gains, losses, uncertainty and tested coverage')
        if data['route']not in('COMPATIBLE','ARCHITECTURAL'):raise ValueError('Promotion route must be explicit')
        if data.get('life_id')!=life or data.get('snapshot_sha256')!=rec['snapshot_sha256']:raise ValueError('Promotion decision does not identify this exact current life checkpoint')
        previous=read(self.state/'ACTIVO.json')if(self.state/'ACTIVO.json').exists()else None
        journal=self.state/'PROMOCIONES.jsonl';record={'schema':'DCS1.1.explicit_promotion.v1','phase':'PREPARED','timestamp':now(),'decision':data,'decision_sha256':digest_file(decision),'previous_active':previous,'new_life_id':life,'new_snapshot_sha256':rec['snapshot_sha256'],'no_life_rewind':True}
        # Record the decision before the atomic active-pointer substitution.
        with self.writer('promotion_registry'):
            with journal.open('a',encoding='utf8')as f:json.dump(record,f,ensure_ascii=False);f.write('\n');f.flush();os.fsync(f.fileno())
            result=self.select(life)
            with journal.open('a',encoding='utf8')as f:json.dump({'schema':record['schema'],'phase':'COMMITTED','timestamp':now(),'decision_id':data['decision_id'],'decision_sha256':record['decision_sha256'],'life_id':life,'snapshot_sha256':rec['snapshot_sha256']},f,ensure_ascii=False);f.write('\n');f.flush();os.fsync(f.fileno())
        return {'INSTRUMENTO':result,'INTERPRETACION':'Explicit bounded promotion changes the preferred life, never its past or the old branch. It does not certify a mind.'}
