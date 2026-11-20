"""One-time P0 post-read support on the actual PI03 main, never a memory edit.

Qualified/deployed only after the matched R05 guard/sham/noquery evidence.
This operation installs ONE legal state0/SEM4/zero-load sink after the existing
zero reader. It advances3ticks, never queries, teaches, supplies a reward,
ages to a favorable cut or changes the fixed q+6 decoder. Native plasticity of
the acquired reference banks remains enabled. No Native import at module load.
"""
from pathlib import Path
import hashlib,json,os

VERSION='PI03.prepared_postread_zero_sink.OP3'
KEY='DEE.Cognitive.PI03.prepared_postread_zero_sink.OP3'
MODE='eci01-pi03-cola-proteger'
FOLDER='PI03_PROTECCION_COLA_OP3'
LIFE='ECI02_PI03_MAIN'
SOURCE_T=768317
SOURCE_RAW='ecb6c9acff995329c5716cd43b78d57bf5d2eaff8499e09fb4fc7412e71317b9'
SOURCE_CLOCKS='c196963604ec3adeccec408ba5be05ed741aa5f2c0cd3795f12b3c57cbff29ee'
SITE=(19,57,5)
CHANNEL='PI03.OP3.zero_output.postread_stop'


def _save(a,m):
    from dee_thinking.persistence import encode_metadata
    a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))


def get(a):
    from dee_thinking.persistence import decode_metadata
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:raise ValueError('No OP3 support installation is recorded')
    m=decode_metadata(entries[KEY])
    if m['version']!=VERSION:raise ValueError('OP3 support revision differs')
    return m


def validate_literal(row):
    if not isinstance(row,dict)or row!={'modo':MODE}:raise ValueError('Only the fixed one-time P0 support operation; no site/tick/content/reader override')


def validate(a,row,*,directory=None):
    validate_literal(row)
    from capacidades import pi03_tarea_diferida_R02 as task
    from capacidades import progresion_integrada_03_R01 as r01
    from app.native_tools import physical,observe
    p,_=r01.protocol();identity=r01._identity(a,p)
    if identity['life_id']!=LIFE or int(a.tick)!=SOURCE_T:raise ValueError('Install only in the unchanged actual Main768317, not a selected diagnostic future or reconstructed life')
    if directory is not None and Path(directory).resolve().name!=LIFE:raise ValueError('Work directory must belong to this actual main')
    if KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('Never reinstall/reset a lived OP3 support')
    actual=physical(a.world)
    if actual['N']!=67 or actual['RAW_sha256']!=SOURCE_RAW or actual['clocks_sha256']!=SOURCE_CLOCKS:raise ValueError('Source physical identity changed; preserve and reconcile from its real cut')
    state=task._get(a)
    if state['opportunity']!=19 or len(state['schedule'])!=21 or state.get('pending')or state.get('uncertain')or state.get('halted_reason'):raise ValueError('Actual source task is not the closed nineteen-completed/two-available cut')
    if int(observe(a.world,SITE)['raw'])!=0:raise ValueError('The post-read sink site is not RAW0; never clear a carrier')
    if CHANNEL in set(a.world.runtime.channel_names):raise ValueError('Prepared interface namespace already exists')
    if directory is not None:task.operational_dependencies(a,directory)


def _record(a,m,directory,event):
    from dee_thinking.persistence import encode_metadata
    folder=Path(directory)/FOLDER;folder.mkdir(parents=True,exist_ok=True)
    data=(json.dumps({'index':m['log_count'],'tick':int(a.tick),**event},ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf-8')
    next_count=m['log_count']+1;next_chain=hashlib.sha256(bytes.fromhex(m['log_chain_sha256'])+data).hexdigest()
    encode_metadata(dict(m,log_count=next_count,log_chain_sha256=next_chain))
    with(folder/'eventos.jsonl').open('ab')as f:f.write(data);f.flush();os.fsync(f.fileno())
    m['log_count']=next_count;m['log_chain_sha256']=next_chain;_save(a,m)


def dispatch(a,row,*,directory=None,actuator='closed'):
    if directory is None or actuator!='closed':raise ValueError('Existing actual owner/directory required')
    validate(a,row,directory=directory)
    folder=Path(directory)/FOLDER
    if folder.exists():raise ValueError('Unmatched prior installation files are preserved; no retry')
    from dee_thinking import _native as d
    from dee_thinking.consolidated import exact_receipt
    from app.native_tools import physical,observe
    refs=[(18,53,5),(20,53,5)]
    before=physical(a.world,occupation=True);before_refs=[observe(a.world,p)for p in refs]
    m={'version':VERSION,'ready':False,'uncertain':True,'source_physical':before,'source_tick':SOURCE_T,
       'site':list(SITE),'channel':CHANNEL,'log_count':0,'log_chain_sha256':'00'*32,
       'classification':'External prepared P0 support after the fixed zero-output reader; no learned regulation or inserted association',
       'qualification':'Matched R05 guard/sham/noquery qualification is required by the installation builder, retained in the campaign evidence and Manual.'}
    _save(a,m);_record(a,m,directory,{'kind':'ONE_TIME_P0_SUPPORT_INTENT','before_references':before_refs})
    c=d.ChannelSpec();c.name=CHANNEL;c.injection_site=d.Coordinate(*SITE);c.direction=d.Direction(0,0,0);c.state=0;c.semantic=4;c.allow_experience=True;c.allow_probe=False
    i=d.InterfaceSpec();i.name=CHANNEL;i.channel=c;a.world.declare_interface(i)
    requested=SOURCE_T+2;receipt=a.world.submit(CHANNEL,0,requested)
    m['request_id']=int(receipt.id);m['requested_tick']=requested;_save(a,m)
    a.run_until(SOURCE_T+3)
    actual=observe(a.world,SITE);rr=exact_receipt(a.world.runtime.receipt(int(receipt.id)))
    after_refs=[observe(a.world,p)for p in refs]
    refs_unchanged=all(int(x['raw'])==int(y['raw'])for x,y in zip(before_refs,after_refs))
    m['ready']=rr['status']=='applied'and int(actual['raw'])==(4<<60)and refs_unchanged
    m['uncertain']=not m['ready'];m['final_tick']=int(a.tick)
    result={'version':VERSION,'prepared':m['ready'],'receipt':rr,'support':actual,
            'before':before,'after':physical(a.world,occupation=True),'before_references':before_refs,'after_references':after_refs,
            'inherited_reference_RAW_unchanged':refs_unchanged,'new_native_ticks':int(a.tick)-SOURCE_T,
            'material_queries':0,'feedbacks':0,'reference_clock_edits':0,
            'scope':'Actual main receives legal prepared support. No skills copied from controls; usefulness, continued learning and conservation must be verified on this same continuation.'}
    _record(a,m,directory,{'kind':'ONE_TIME_P0_SUPPORT_RESULT','result':result})
    if not m['ready']:raise ValueError('Support not qualified at the reached state; preserve rather than reset')
    return result


def uncertain(a):
    return KEY in dict(a.world.runtime.snapshot_metadata_entries)and bool(get(a)['uncertain'])


def operational_dependencies(a,directory):
    if KEY not in dict(a.world.runtime.snapshot_metadata_entries):return{'version':VERSION,'admitted':False,'new_native_ticks':0}
    from app.native_tools import observe
    m=get(a);file=Path(directory)/FOLDER/'eventos.jsonl';chain=bytes(32);count=0
    with file.open('rb')as f:
        for line in f:
            if json.loads(line)['index']!=count:raise ValueError('OP3 support journal index differs')
            chain=hashlib.sha256(chain+line).digest();count+=1
    if count!=m['log_count']or chain.hex()!=m['log_chain_sha256']:raise ValueError('OP3 support/journal metadata differs')
    if int(observe(a.world,SITE)['raw'])!=(4<<60):raise ValueError('Prepared post-read support not intact')
    return{'version':VERSION,'admitted':True,'ready':m['ready'],'uncertain':m['uncertain'],'site':list(SITE),
           'journal':str(file),'journal_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),
           'classification':m['classification'],'new_native_ticks':0}
