"""Optional F1: post-formation diagnostic RAW cut vs identity fork.

PREPARED ONLY. Root must seal the protocol and install only into isolated F1
systems. No actor/source rewrite, no force, no kernel change, no promotion.
One imported diagnostic life creates an identity diagnostic fork with no
future advancement, then a RAW-cut fork which alone continues. THREE world
slots, not two. The intact Native future is the previously executed reference.
"""
from pathlib import Path
import gzip
import hashlib
import importlib.util
import json
import struct
import uuid
from capacidades import pi07_regulacion_R03 as core

VERSION='DEE.PI08.F1.postformed_diagonal_diagnostic.R02'
KEY='DEE.Cognitive.PI08.F1.diagonal_diagnostic.R02'
RUN='eci01-pi08-f1-diagonal';STATE='eci01-pi08-f1-estado';MODES={RUN,STATE}
PROTOCOL=Path(__file__).with_name('PROTOCOLO_F1_DIAGONAL_PI08_R02.json')
SITE=(52,48,56);FOLDER='PI08_F1_COLA_DIAGONAL_R02'


def sha(b):return hashlib.sha256(b).hexdigest()
def _entry(a):
    raw=dict(a.world.runtime.snapshot_metadata_entries).get(KEY)
    return None if raw is None else json.loads(raw)
def _save(a,m):a.world.runtime.set_snapshot_metadata(KEY,json.dumps(m,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False))


def protocol():
    data=PROTOCOL.read_bytes();p=json.loads(data)
    if p.get('schema')!='DEE.PI08.F1.postformation_protocol.v1'or p.get('status')!='SEALED_FOR_OPTIONAL_F1_NATIVE':
        raise ValueError('Root must seal this optional diagnostic before any Native trial')
    if sha(Path(__file__).read_bytes())!=p.get('wrapper_sha256'):raise ValueError('F1 wrapper differs from its seal')
    if sha(Path(core.__file__).read_bytes())!=p['R03_source_sha256']or sha(core.PROTOCOL.read_bytes())!=p['R03_protocol_sha256']:
        raise ValueError('Exact acquired R03 body/protocol required; no actor patch')
    if p['source_tick']!=849645 or p['ordinals']!=[4,5]or p['query_ticks']!=[850015,850797]or p['hook_relative_query']!=8:
        raise ValueError('Only the declared two-opportunity POST4 diagnostic')
    if p['target_site']!=list(SITE)or p['raw_cut_value']!=0 or p['clock_edit']is not None:
        raise ValueError('One fixed RAW-only diagnostic edit, never a payload-zero birth')
    if p['world_slots_one_import_plus_two_forks']!=3 or p['maximum_Native_ticks_total']!=2600:
        raise ValueError('Conservative world/fork and finite tick budget required')
    return p,sha(data)


class _Reader:
    def __init__(self,b):self.b=memoryview(b)[:-8];self.i=0
    def take(self,n):
        if n<0 or self.i+n>len(self.b):raise ValueError('Truncated Native diagnostic snapshot')
        value=self.b[self.i:self.i+n];self.i+=n;return value
    def u8(self):return self.take(1)[0]
    def u32(self):return struct.unpack('<I',self.take(4))[0]
    def u64(self):return struct.unpack('<Q',self.take(8))[0]
    def count(self):
        n=self.u32()
        if n>1000000:raise ValueError('Native snapshot count bound')
        return n
    def text(self):
        n=self.u32()
        if n>16*1024*1024:raise ValueError('Native snapshot string bound')
        return self.take(n).tobytes().decode('utf-8')
    def skip_text(self):
        n=self.u32()
        if n>16*1024*1024:raise ValueError('Native snapshot string bound')
        self.take(n)


def _snapshot_fields(path,keep_raw=False):
    encoded=Path(path).read_bytes();payload=gzip.decompress(encoded);r=_Reader(payload)
    if r.take(8).tobytes()!=b'DEETSNP1'or r.u32()!=2:raise ValueError('Native v2 snapshot required')
    n=r.u32();tick=r.u64();paused=r.u8();next_id=r.u64();next_sequence=r.u64();phase=r.text();count=r.u64()
    if n!=67 or count!=n**3:raise ValueError('Exact complete N67 snapshot required')
    raw=r.take(count*8);clocks=r.take(count*8)
    raw_hash=sha(raw);clock_hash=sha(clocks);raw_copy=raw.tobytes()if keep_raw else None
    start=r.i;nc=r.count()
    for _ in range(nc):r.skip_text();r.take(31)
    channel_hash=sha(r.b[start:r.i]);start=r.i;npending=r.count()
    for _ in range(npending):
        r.take(8+8+1+8+8)
        for _ in range(r.count()):r.skip_text()
        r.take(20*r.count())
    pending_hash=sha(r.b[start:r.i]);start=r.i;nreceipts=r.count()
    for _ in range(nreceipts):
        r.take(8+1+1+8)
        if r.u8():r.take(8)
        for _ in range(r.count()):r.skip_text()
        r.skip_text()
    receipt_hash=sha(r.b[start:r.i]);backend=r.u8();threads=r.u64();causal=sha(r.b[:r.i]);metadata_start=r.i;nm=r.count()
    for _ in range(nm):r.skip_text();r.skip_text()
    if r.i!=len(r.b):raise ValueError('Unparsed Native diagnostic bytes')
    return {'snapshot':{'path':str(path),'bytes':len(encoded),'sha256':sha(encoded)},
        'N':n,'tick':tick,'RAW_sha256':raw_hash,'clocks_sha256':clock_hash,'paused':bool(paused),
        'next_event_id':next_id,'next_sequence':next_sequence,'phase':phase,'interfaces_count':nc,
        'interfaces_sha256':channel_hash,'pending_count':npending,'pending_sha256':pending_hash,
        'receipts_count':nreceipts,'receipts_sha256':receipt_hash,'backend':backend,'threads':threads,
        'Native_causal_prefix_sha256':causal,'metadata_key_count':nm,
        'metadata_serialized_sha256':sha(r.b[metadata_start:r.i]),
        'Native_complete_content_sha256':sha(r.b[:r.i]),
        'verification_scope':'Gzip CRC and full Native-v2 parse; internal Native FNV not separately recalculated.'},raw_copy


def _checkpoint(world,path,keep_raw=False):
    from app.native_tools import physical
    from dee_thinking.persistence import save_world_snapshot
    before=physical(world)
    save_world_snapshot(world,path,include_trace=True,compress=True,overwrite=False)
    after=physical(world)
    if before!=after:raise RuntimeError('Diagnostic serialization changed physical state')
    value,raw=_snapshot_fields(path,keep_raw)
    for field in('N','tick','RAW_sha256','clocks_sha256'):
        if value[field]!=before[field]:raise RuntimeError('Serialized diagnostic state is not the current physical cut')
    return value,raw


def _observe_world(world,site):
    d=core._native()[0];o=world.runtime.observe(d.Coordinate(*site));raw=int(o.raw)
    digits=[(raw>>s)&15 for s in(48,52,56)]
    return {'tick':int(o.tick),'site':list(site),'raw':str(raw),'clock':str(int(o.clock)),
        'state':raw&0xffffffff,'semantic':raw>>60,'s_reg':(raw>>32)&65535,
        'direction':[v-16 if v&8 else v for v in digits]}


def _edit(site,raw,label):
    d=core._native()[0];e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*site)
    e.raw=int(raw);e.clock=None;e.label=label;return e


class PostFormationAdapter:
    """One exact q+8 hook; callbacks keep pure Fake tests away from Native."""
    def __init__(self,base,*,holder,q,arm,ticks,recorder,directory,enable_fork,
                 observe,checkpoint,make_edit):
        self.base=base;self.holder=holder;self.q=q;self.arm=arm;self.ticks=tuple(sorted(set(ticks)))
        self.recorder=recorder;self.directory=Path(directory);self.enable_fork=enable_fork
        self.observe=observe;self.checkpoint=checkpoint;self.make_edit=make_edit
        self.hook_seen=False;self.fork_count=0;self.intervention=None
    @property
    def world(self):return self.base.world
    @property
    def tick(self):return int(self.base.tick)
    def __getattr__(self,name):return getattr(self.base,name)
    def _apply(self):
        self.hook_seen=True;record=self.observe(self.world,SITE)
        valid=record['state']>0 and record['semantic']==1 and record['s_reg']==0 and record['direction']==[-1,0,1]
        self.intervention={'hook_tick':self.tick,'fixed_site':list(SITE),'before_observation':record,
                           'target_signature_present':valid,'diagnostic_edit_applied':False,
                           'not_Native_acquired_regulation':True}
        if not valid:
            self.intervention['status']='NO_FIXED_TARGET_NO_SEARCH_NO_EDIT'
            return
        parent=self.world
        before,raw=self.checkpoint(parent,self.directory/'Q8_PARENT_BEFORE.deetsnap.gz',True)
        # Structural identity fork only. It never advances and is never attached.
        self.fork_count+=1
        identity=parent.diagnostic_fork([self.make_edit(SITE,int(record['raw']),'PI08_F1_STRUCTURAL_IDENTITY_R02')],True)
        identity_state,_=self.checkpoint(identity,self.directory/'Q8_IDENTITY_NO_FUTURE.deetsnap.gz',False)
        parent_after_identity,_=self.checkpoint(parent,self.directory/'Q8_PARENT_AFTER_IDENTITY.deetsnap.gz',False)
        preserved=('N','tick','RAW_sha256','clocks_sha256','paused','next_event_id','next_sequence','phase',
                   'interfaces_count','interfaces_sha256','pending_count','pending_sha256',
                   'receipts_count','receipts_sha256','backend','threads','metadata_key_count',
                   'metadata_serialized_sha256','Native_causal_prefix_sha256','Native_complete_content_sha256')
        identity_equal={key:before[key]==identity_state[key] for key in preserved}
        parent_identity_equal={key:before[key]==parent_after_identity[key] for key in preserved}
        self.intervention.update(identity_sham_snapshot=identity_state,
            parent_after_identity_snapshot=parent_after_identity,identity_sham_preserved_fields=identity_equal,
            identity_sham_parent_preserved_fields=parent_identity_equal,
            identity_sham_future_Native_ticks=0,identity_sham_scope='Structural same-cut identity only, no Native future control')
        if not all(identity_equal.values()) or not all(parent_identity_equal.values()):
            self.intervention['status']='IDENTITY_STRUCTURAL_EQUALITY_FAILED_STOP'
            raise RuntimeError('Identity fork or original parent differs in Native metadata/phase/causal content; F1 stops')
        # The second fork is made from the original same-cut parent, not from a
        # potentially modified identity branch. Only this cut branch advances.
        replacement=0
        self.fork_count+=1
        branch=parent.diagnostic_fork([self.make_edit(SITE,replacement,'PI08_F1_RAW_CUT_R02')],True)
        after,_=self.checkpoint(branch,self.directory/'Q8_BRANCH_AFTER.deetsnap.gz',False)
        parent_after,_=self.checkpoint(parent,self.directory/'Q8_PARENT_AFTER.deetsnap.gz',False)
        idx=((SITE[0]*67+SITE[1])*67+SITE[2])*8
        expected=bytearray(raw);expected[idx:idx+8]=replacement.to_bytes(8,'little')
        equal={key:before[key]==after[key] for key in preserved if key not in
               ('RAW_sha256','Native_causal_prefix_sha256','Native_complete_content_sha256')}
        if not all(equal.values()) or sha(expected)!=after['RAW_sha256']:
            raise RuntimeError('Cut fork changed more than the one declared RAW field')
        if parent_after['Native_complete_content_sha256']!=before['Native_complete_content_sha256']:
            raise RuntimeError('The original parent Native state including metadata was modified')
        self.holder.world=branch
        self.intervention.update(status='DIAGNOSTIC_RAW_CUT_AFTER_STRUCTURAL_IDENTITY',
            diagnostic_edit_applied=True,raw_replacement='0',clock_edit=None,
            before_snapshot=before,branch_after_snapshot=after,parent_after_snapshot=parent_after,
            preserved_Native_fields=equal,parent_Native_causal_prefix_unchanged=True,
            parent_Native_complete_content_unchanged=True,
            exact_expected_one_site_RAW_patch=True,additional_Native_Runtime_forks=2,
            after_observation=self.observe(branch,SITE))

    def run_until(self,target):
        if type(target)is not int or target<self.tick:raise ValueError('No diagnostic rewind')
        answer=None
        for boundary in self.ticks:
            if self.tick<=boundary<=target:
                if boundary>self.tick:answer=self.base.run_until(boundary)
                if self.recorder is not None:self.recorder.capture(self.base)
                if self.enable_fork and not self.hook_seen and boundary==self.q+8:self._apply()
        if self.tick<target:answer=self.base.run_until(target)
        return answer


def validate_literal(row):
    if isinstance(row,dict)and row.get('modo')==STATE and set(row)=={'modo'}:return
    if (isinstance(row,dict)and set(row)=={'modo','arm','stage'}and row['modo']==RUN
            and row['arm']=='raw_cut'and row['stage']in('first','next')):return
    raise ValueError('Only fixed first/next raw_cut diagnostic with structural identity; no adjustable coordinate, clock or force')


def _world_holder(a):
    # The actual owner wraps app.lives.WorldAdapter once in HabitatAdapter.
    # Preserve that wrapper and its progress; replace only its documented base.
    candidate=a
    if type(a).__name__=='HabitatAdapter'and type(a).__module__=='capacidades.adapter_habitat_R04':
        candidate=vars(a).get('base')
    if (candidate is None or type(candidate).__name__!='WorldAdapter'
            or type(candidate).__module__!='app.lives'or'world'not in vars(candidate)):
        raise ValueError('Only the inspected WorldAdapter, optionally wrapped once by HabitatAdapter')
    return candidate


def validate(a,row):
    validate_literal(row)
    if row['modo']==STATE:return
    p,ph=protocol();identity=core._identity(a);life=identity['life_id']
    if life!=p['allowed_lives'][row['arm']]or core._selected(a):raise ValueError('Exact unselected F1 life required; no principal control')
    campaign=Path(p['campaign_root']).resolve(strict=True);system=Path(__file__).resolve().parents[1]
    if not system.is_relative_to(campaign/'estados'):raise ValueError('Only isolated PI08 diagnostic code, never product installation')
    _world_holder(a)
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    habitat_key='DEE.Cognitive.PI02.continuous_workbench.R04'
    if habitat_key in entries:
        habitat=core._native()[3](entries[habitat_key])
        if habitat.get('enabled')is not False or habitat.get('uncertain')or habitat.get('active')is not None:
            raise ValueError('Inherited habitat must remain paused and certain; do not add background work')
    core.validate(a,{'modo':core.EPISODE});progress=core._get(a);prior=_entry(a)
    i=0 if row['stage']=='first'else 1
    if progress['ordinal']!=p['ordinals'][i]or int(a.tick)!=p['before_ticks'][i]:raise ValueError('Known complete POST4/next cut required')
    if row['stage']=='first':
        if prior is not None:raise ValueError('F1 ID already used; do not replay an ambiguous operation')
        physical=core._physical(a)
        if any(physical[k]!=v for k,v in p['source_physical'].items()):raise ValueError('Starting physical source differs')
    elif prior is None or prior.get('completed_operations')!=1 or prior.get('arm')!=row['arm']or prior.get('pending')is not None:
        raise ValueError('Next observation must follow this same actual diagnostic continuation')
    if not hasattr(a.world,'diagnostic_fork'):raise ValueError('Required public diagnostic API is absent')


def dispatch(a,row,*,actuator='closed',directory=None):
    validate(a,row)
    if row['modo']==STATE:return{'version':VERSION,'state':_entry(a),'new_native_ticks':0,'scope':'Administrative read only'}
    if actuator!='closed'or directory is None:raise ValueError('Existing one-owner closed interface and exact home required')
    p,ph=protocol();identity=core._identity(a);prior_f1=_entry(a);home=core._home(directory,identity['life_id']).with_name(FOLDER)
    home.mkdir(exist_ok=True);i=0 if row['stage']=='first'else 1
    refs=[core._observe(a,core.at(v))for v in((-1,-1,0),(1,-1,0))]
    cal=core._helper().schedule_trial(int(a.tick)+16,int(refs[0]['clock'])+16,6);q=cal['query_tick']
    if q!=p['query_ticks'][i]:raise ValueError('Actual fixed calendar differs; no retiming')
    path=Path(__file__).with_name('observador_global_PI05_R01.py')
    if sha(path.read_bytes())!=p['codec_sha256']:raise ValueError('Fixed lossless recorder differs')
    spec=importlib.util.spec_from_file_location('PI08_F1_exact_global',path);capture=importlib.util.module_from_spec(spec);spec.loader.exec_module(capture)
    target=home/('OP%d_'%i+uuid.uuid4().hex);ticks=[q+t for t in p['capture_relative_ticks']]
    recorder=capture.GlobalRecorder(target,N=67,ticks=ticks,anchor_ticks={q+t for t in p['anchor_relative_ticks']},
        provenance={'life_id':identity['life_id'],'version':VERSION,'arm':row['arm'],'stage':row['stage'],
                    'actor_receives_recording':False,'q8_frame_is_before_external_edit':True,
                    'edited_q8_state_is_preserved_separately_in_snapshot':True},max_frames=24,max_compressed_bytes=32*1024*1024)
    wrapped=PostFormationAdapter(a,holder=_world_holder(a),q=q,arm=row['arm'],ticks=ticks,recorder=recorder,directory=target,
        enable_fork=i==0,observe=_observe_world,checkpoint=_checkpoint,make_edit=_edit)
    metadata={'version':VERSION,'protocol_sha256':ph,'arm':row['arm'],'completed_operations':i,
              'pending':row['stage'],'diagnostic_only_do_not_adopt':True,'first_intervention':(prior_f1 or{}).get('first_intervention')}
    _save(a,metadata)
    try:
        result=core.dispatch(wrapped,{'modo':core.EPISODE},actuator=actuator,directory=directory)
        if result['new_native_ticks']>1300:raise RuntimeError('Actual finite per-op diagnostic bound exceeded')
        recording=recorder.close()
        summary=(None if wrapped.intervention is None else {
            'status':wrapped.intervention['status'],
            'target_signature_present':wrapped.intervention['target_signature_present'],
            'diagnostic_edit_applied':wrapped.intervention['diagnostic_edit_applied'],
            'external_report_directory':str(target)})
        metadata.update(completed_operations=i+1,pending=None,
            first_intervention=summary if i==0 else(prior_f1 or{}).get('first_intervention'),
            additional_forks_this_operation=wrapped.fork_count)
        _save(a,metadata)
        output={'version':VERSION,'arm':row['arm'],'stage':row['stage'],'original_result':result,
            'diagnostic_intervention':wrapped.intervention,'external_global_capture':recording,
            'new_native_ticks':result['new_native_ticks'],'additional_Native_Runtime_forks':wrapped.fork_count,
            'world_slot_accounting':'One imported life + structural identity fork(no future) + continued cut fork:3slots if target forms.',
            'scope':'External RAW-only cut after structural identity-fork equality at fixed observed formation. '
                    'Not a Native action, learned regulation, legal payload-zero birth or adoptable future. '
                    'Sham may be compared with actual RP_A01 intact physical references; equality is measured, never assumed.'}
        with(target/'RESULTADO_DIAGNOSTICO.json').open('x',encoding='utf-8')as f:json.dump(output,f,ensure_ascii=False,indent=2);f.write('\n')
        return output
    except BaseException as error:
        if not recorder.closed:recorder.close()
        metadata.update(pending='failed_preserved',error=type(error).__name__,fork_count_seen=wrapped.fork_count)
        _save(a,metadata);raise


def uncertain(a):
    m=_entry(a)
    return core.uncertain(a)or bool(m and m.get('pending'))
def operational_dependencies(a,directory):
    return{'version':VERSION,'diagnostic':_entry(a),'R03':core.operational_dependencies(a,directory),
           'no_promotion_authorized':True,'new_native_ticks':0}
def code_files():return list(dict.fromkeys([Path(__file__),PROTOCOL,*core.code_files()]))
