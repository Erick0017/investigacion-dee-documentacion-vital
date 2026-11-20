"""Frozen tail-collision diagnostic through the existing owner, no new reader.

Guard/sham: legal state0/SEM4 at Q+(0,3,0)/(0,3,1), +3 ticks, age3183.
Noquery: no placement, age3186, then the same fixed q-1..q+7 observations.
All start from the complete T768317 source; age ends at T771503. Query cases
use the ORIGINAL task.opportunity and its exact q+6 decoder. This module never
imports DEE at import, creates a life, chooses an action or promotes anything.
"""
from pathlib import Path
import hashlib,json,os

VERSION='PI03.postread_zero_tail_diagnostic.R05b_JSON_SAFE'
KEY='DEE.Cognitive.PI03.postread_zero_tail_diagnostic.R05b'
MODE='eci01-pi03-diagnostico-cola'
FOLDER='PI03_DIAGNOSTICO_COLA_R05b'
SOURCE_T=768317
AGED_T=771503
Q=(19,54,5)
FIXED_QUERY_T=771949
FIXED_READ_T=771955
DIAGNOSTIC_PREFIX='ECI02_PI03_DIAG_'


def _modules():
    from capacidades import pi03_tarea_diferida_R02 as task
    from capacidades import progresion_integrada_03_R01 as r01
    from capacidades import pi03_credito_generico_R01_BORRADOR as helper
    return task,r01,helper


def _save(a,m):
    from dee_thinking.persistence import encode_metadata
    a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))


def get(a):
    from dee_thinking.persistence import decode_metadata
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:raise ValueError('No admitted R05 diagnostic')
    m=decode_metadata(entries[KEY])
    if m['version']!=VERSION:raise ValueError('R05 exact revision mismatch')
    return m


def validate_literal(row):
    if not isinstance(row,dict)or set(row)!={'modo','condicion'}or row['modo']!=MODE or row['condicion']not in('guard','sham','noquery'):
        raise ValueError('Only fixed guard/sham/noquery; no age, reader, target, phase or action override')


def validate(a,row,*,directory=None):
    validate_literal(row)
    task,r01,helper=_modules();p,ph= r01.protocol()
    identity=r01._identity(a,p,directory)
    if not identity['life_id'].startswith(DIAGNOSTIC_PREFIX):raise ValueError('Only an explicit ECI02_PI03_DIAG_* full clone, never a main')
    if int(a.tick)!=SOURCE_T:raise ValueError('This frozen diagnostic requires the unchanged complete T768317 source, not latest tick or a repaired future')
    if KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('An R05 diagnostic is never repeated or reset')
    m=task._get(a)
    if m.get('pending')or m.get('uncertain')or m.get('halted_reason')or m.get('supply_pending'):raise ValueError('Source task has pending/uncertain work')
    if m['opportunity']!=19 or len(m['schedule'])!=21:raise ValueError('Exact nineteen completed/two available source offers required')
    if tuple(p['origin'])!=Q:raise ValueError('Fixed source geometry differs')
    if directory is not None:
        task.operational_dependencies(a,directory)
        device=task._device(directory)
        if device.m['pending']is not None or device.m['feedback_pending']is not None or device.m['uncertain']:raise ValueError('Source external device not closed')


def _record(a,m,directory,event):
    from dee_thinking.persistence import encode_metadata
    folder=Path(directory)/FOLDER;folder.mkdir(parents=True,exist_ok=True)
    data=(json.dumps({'index':m['log_count'],'tick':int(a.tick),**event},ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf-8')
    next_count=m['log_count']+1;next_chain=hashlib.sha256(bytes.fromhex(m['log_chain_sha256'])+data).hexdigest()
    prospective=dict(m,log_count=next_count,log_chain_sha256=next_chain)
    encode_metadata(prospective)  # STRICT preflight BEFORE appending a journal line.
    with(folder/'eventos.jsonl').open('ab')as f:f.write(data);f.flush();os.fsync(f.fileno())
    m['log_count']=next_count;m['log_chain_sha256']=next_chain;_save(a,m)


def _capture(a,label):
    task,r01,helper=_modules()
    from app.native_tools import observe,physical
    core=set(helper.geometry_footprint(Q,halo=0))
    # Full local context for the old-Y/new-Z encounter, not only a port.
    core.update(helper.at(Q,(x,y,z))for x in range(-2,3)for y in range(-2,3)for z in range(-2,3))
    row=[(Q[0],y,Q[2])for y in range(67)]
    def obs(site):
        o=observe(a.world,site);o['raw']=str(o['raw']);o['clock']=str(o['clock']);return o
    return {'kind':'PASSIVE_FIXED_FRAME','label':label,'physical':physical(a.world,occupation=True),
            'core_and_encounter_context':[obs(s)for s in sorted(core)],
            'entire_zero_Y_row':[obs(s)for s in row],
            'fixed_q6_reader_sites':[obs(helper.at(Q,v))for v in helper.READER_OFFSETS],
            'coverage':'Fixed mechanism core + comparator Moore radius2 + complete67site central Y row; global RAW/clocks hashes/occupation. Not complete-world physical genealogy.'}


class PassiveMonitoredAdapter:
    """Split only the SAME admitted owner's run_until; never another Runtime."""
    def __init__(self,base,m,directory,query_tick):
        self.base=base;self.m=m;self.directory=directory
        self.milestones={query_tick+k:'q%+d'%k for k in range(-1,8)}
        self.captured=[]
    @property
    def world(self):return self.base.world
    @property
    def tick(self):return self.base.tick
    def save(self,path):return self.base.save(path)
    def run_until(self,target):
        if type(target)is not int or target<int(self.tick):raise ValueError('No rewind or fractional physical boundary')
        for t,label in sorted(self.milestones.items()):
            if int(self.tick)<t<=target:
                self.base.run_until(t)
                _record(self,self.m,self.directory,_capture(self,label))
                self.captured.append(t)
        if int(self.tick)<target:self.base.run_until(target)


def dispatch(a,row,*,directory=None,actuator='closed'):
    if directory is None or actuator!='closed':raise ValueError('Existing owned diagnostic directory and fixed actuator required')
    validate(a,row,directory=directory)
    task,r01,helper=_modules();case=row['condicion'];prefix='PI03.R05.'+case
    home=Path(directory)/FOLDER
    if home.exists():raise ValueError('Preserved diagnostic files already exist; no overwrite/retry')
    m={'version':VERSION,'case':case,'source_tick':SOURCE_T,'age_target':AGED_T,
       'fixed_query_tick':FIXED_QUERY_T,'fixed_reader_tick':FIXED_READ_T,
       'uncertain':True,'completed':False,'guard':None,'log_count':0,'log_chain_sha256':'00'*32}
    _save(a,m);_record(a,m,directory,{'kind':'FROZEN_DIAGNOSTIC_INTENT','literal':row,
        'protocol':{'source_T':SOURCE_T,'age_target':AGED_T,'delay_laps':4,'query_tick':FIXED_QUERY_T,'read_tick':FIXED_READ_T,'record_offsets':list(range(-1,8)),
                    'guard_offset':[0,3,0],'sham_offset':[0,3,1],'noquery_material_inputs':0,'no_reader_change':True}})
    _record(a,m,directory,_capture(a,'source_before_any_intervention'))
    # File-only complete exports may omit empty directories. OP2 already
    # restores these declared structural slots; record any remaining empty-slot
    # creation explicitly. No resource, product, receipt or Native state reset.
    device=task._device(directory);restored=[]
    for folder in('reservoir','inflight_minus','inflight_plus','inflight_silence','products','rejected'):
        p=device.home/folder
        if p.exists()and not p.is_dir():raise ValueError('Structural slot is not a directory')
        if not p.exists():p.mkdir();restored.append(folder)
    _record(a,m,directory,{'kind':'DECLARED_EMPTY_DEVICE_DIRECTORIES','created_if_missing':restored,'native_ticks':0,'resources_created':0})
    if case!='noquery':
        from dee_thinking import _native as native
        from dee_thinking.consolidated import exact_receipt
        from app.native_tools import observe
        delta=(0,3,0)if case=='guard'else(0,3,1);site=helper.at(Q,delta)
        before=observe(a.world,site)
        if int(before['raw'])!=0:raise ValueError('Guard/sham requires exactRAW0; never clear occupied/inactive material')
        channel=prefix+'.postread_terminator'
        if channel in set(a.world.runtime.channel_names):raise ValueError('Fresh guard channel namespace required')
        c=native.ChannelSpec();c.name=channel;c.injection_site=native.Coordinate(*site);c.direction=native.Direction(0,0,0);c.state=0;c.semantic=4;c.allow_experience=True;c.allow_probe=False
        i=native.InterfaceSpec();i.name=channel;i.channel=c;a.world.declare_interface(i)
        requested=int(a.tick)+2;receipt=a.world.submit(channel,0,requested)
        a.run_until(SOURCE_T+3)
        rr=exact_receipt(a.world.runtime.receipt(int(receipt.id)));after=observe(a.world,site)
        m['guard']={'site':list(site),'offset':list(delta),'channel':channel,'request_id':int(receipt.id),'requested_tick':requested,'receipt':rr,'before':before,'after':after,
                    'scope':'External P0 support, state0/SEM4/zero charge; preserves inherited clocks and all acquired reference fields'}
        _record(a,m,directory,{'kind':'LEGAL_GUARD_OR_SHAM_PREPARATION','preparation':m['guard']})
        if rr['status']!='applied'or int(after['raw'])!=(4<<60):raise ValueError('Legal support not admitted; preserve reached future')
    # +3+3183 for guard/sham, +3186 for noquery, exactly the same final age.
    a.run_until(AGED_T)
    _record(a,m,directory,_capture(a,'equal_age_before_fixed_query'))
    from app.native_tools import observe
    refs=[observe(a.world,helper.at(Q,v))for v in((-1,-1,0),(1,-1,0))]
    if int(refs[0]['clock'])%782!=int(refs[1]['clock'])%782:raise ValueError('Reference clock phases differ; no clock repair')
    calendar=helper.schedule_trial(int(a.tick),int(refs[0]['clock']),4)
    if calendar['query_tick']!=FIXED_QUERY_T or calendar['query_read_tick']!=FIXED_READ_T:raise ValueError('Frozen calendar no longer matches; no phase/window search')
    monitored=PassiveMonitoredAdapter(a,m,directory,FIXED_QUERY_T)
    if case=='noquery':
        monitored.run_until(FIXED_QUERY_T+7)
        task_state=task._get(a);task_state['halted_reason']='R05_NOQUERY_TERMINAL_CONTROL: no task action or query performed'
        task._record(a,task_state,directory,{'kind':'R05_NOQUERY_TERMINAL_CONTROL','new_task_queries':0,'new_task_actions':0})
        value={'kind':'noquery_equal_age_control','material_query_inputs':[],'task_action':None,'reader_reinterpreted':False}
    else:
        # The existing task still submits its original3query inputs and uses
        # q+6 alone. No expected sign is supplied and no alternative reader used.
        value=task.opportunity(monitored,directory)
    m['uncertain']=False;m['completed']=True;m['final_tick']=int(a.tick)
    _record(a,m,directory,{'kind':'DIAGNOSTIC_COMPLETED','fixed_calendar':calendar,'captured_ticks':monitored.captured,'actual_task_result':value})
    return {'version':VERSION,'case':case,'source_tick':SOURCE_T,'final_tick':int(a.tick),'new_native_ticks':int(a.tick)-SOURCE_T,
            'guard_preparation':m['guard'],'calendar':calendar,'captured_ticks':monitored.captured,
            'actual_task_result':value,'reader_contract_unchanged':True,
            'scope':'Diagnostic full clone only. Guard is prepared support; useful/reproducible mechanism needs the matched sham/noquery contrasts. No promotion or automatic repair.'}


def uncertain(a):
    return KEY in dict(a.world.runtime.snapshot_metadata_entries)and bool(get(a)['uncertain'])


def operational_dependencies(a,directory):
    if KEY not in dict(a.world.runtime.snapshot_metadata_entries):return{'version':VERSION,'admitted':False,'new_native_ticks':0}
    m=get(a);file=Path(directory)/FOLDER/'eventos.jsonl';chain=bytes(32);count=0
    with file.open('rb')as f:
        for line in f:
            if json.loads(line)['index']!=count:raise ValueError('R05 journal index differs')
            chain=hashlib.sha256(chain+line).digest();count+=1
    if count!=m['log_count']or chain.hex()!=m['log_chain_sha256']:raise ValueError('R05 full-world metadata/journal mismatch')
    if m['guard']:
        from app.native_tools import observe
        if int(observe(a.world,m['guard']['site'])['raw'])!=(4<<60):raise ValueError('Prepared R05 support is no longer intact')
    return{'version':VERSION,'admitted':True,'case':m['case'],'uncertain':m['uncertain'],'completed':m['completed'],
           'journal':str(file),'journal_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'log_count':count,
           'scope':'No query or advancement; preserve this journal with the complete owned world/agenda/receipts and task/device files.'}
