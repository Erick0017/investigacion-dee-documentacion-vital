"""Explicit administrative import mapping for ONE prospective PI05 principal.

No Native import at module load. Root executes only after a full paired import
and closed-owner checks. Nothing is acquired or merged: one current identity
leaf changes; learned fields, old rows/protocol/history and Native dynamics
must stay byte/structurally identical. Never remap an already selected world.
"""
from pathlib import Path
import copy,gzip,hashlib,json,struct
LIFE='ECI02_PI03_REPRO_PI04_PI05_MAIN_01'
KEY='DEE.Cognitive.PI04.C2C.coordination.R01'
SYSTEM='DEE.Cognitive.System.1.1.life.v1'
def _sha(b):return hashlib.sha256(b).hexdigest()
class _Reader:
    def __init__(self,b):self.b=b;self.i=0
    def take(self,n):
        if n<0 or self.i+n>len(self.b):raise ValueError('Truncated complete snapshot')
        v=self.b[self.i:self.i+n];self.i+=n;return v
    def u8(self):return self.take(1)[0]
    def u32(self):return struct.unpack('<I',self.take(4))[0]
    def u64(self):return struct.unpack('<Q',self.take(8))[0]
    def count(self):
        n=self.u32()
        if n>1000000:raise ValueError('Snapshot collection exceeds frozen bound')
        return n
    def text(self):
        n=self.u32()
        if n>16*1024**2:raise ValueError('Snapshot text exceeds frozen bound')
        return self.take(n).decode('utf8')
def _view(path):
    encoded=Path(path).read_bytes();b=gzip.decompress(encoded)if encoded[:2]==b'\x1f\x8b'else encoded;r=_Reader(b[:-8])
    if r.take(8)!=b'DEETSNP1'or r.u32()!=2:raise ValueError('Exact official Native snapshotv2 required')
    n=r.u32();tick=r.u64();r.u8();r.u64();r.u64();r.text();total=r.u64()
    if n!=67 or total!=n**3:raise ValueError('Preserve exact N67 complete arrays')
    raw=r.take(8*total);clocks=r.take(8*total)
    for _ in range(r.count()):r.text();r.take(31)
    for _ in range(r.count()):
        r.take(33)
        for _ in range(r.count()):r.text()
        for _ in range(r.count()):r.take(20)
    for _ in range(r.count()):
        r.take(18)
        if r.u8():r.take(8)
        for _ in range(r.count()):r.text()
        r.text()
    r.u8();r.u64();boundary=r.i;metadata={}
    for _ in range(r.count()):
        key=r.text();value=r.text()
        if key in metadata:raise ValueError('Duplicate Native metadata key')
        metadata[key]=value
    if r.i!=len(b)-8:raise ValueError('Unparsed bytes in Native snapshot')
    return {'physical':{'N':n,'tick':tick,'RAW_sha256':_sha(raw),'clocks_sha256':_sha(clocks)},
        'causal_prefix_sha256':_sha(b[:boundary]),'metadata':metadata,'encoded_sha256':_sha(encoded)}

def propose_identity(metadata,source_life,target_life):
    """Pure mapping proposal; source_life is paired-source WORLD identity.

    C2C's inherited current identity may be older than that world identity;
    record both, never rewrite historical IDs in rows or journals.
    """
    if target_life!=LIFE or not isinstance(source_life,str)or not source_life.startswith('ECI02_PI03_REPRO_PI04_'):
        raise ValueError('Exact prospective PI05 principal and explicit inherited source required')
    if not isinstance(metadata.get('life_id'),str)or any(metadata.get(k)for k in('pending','uncertain','halted_reason')):
        raise ValueError('Closed C2C current identity required; uncertain future preserved')
    new=copy.deepcopy(metadata);old=new['life_id'];new['life_id']=target_life
    if {k:v for k,v in new.items()if k!='life_id'}!={k:v for k,v in metadata.items()if k!='life_id'}:
        raise RuntimeError('Identity proposal changed acquired state')
    return new,{'field':'life_id','old':old,'new':target_life,'source_world_life_id':source_life,
        'historical_rows_protocol_plan_history_unchanged':True,'not_an_acquisition_or_memory_transfer':True}

def rebind_imported_C2C_identity(store,target_life,source_life):
    if target_life!=LIFE:raise ValueError('Only the declared prospective PI05 principal; no generic memory editor')
    active=store.state/'ACTIVO.json'
    if active.exists():
        selected=json.loads(active.read_text('utf-8-sig'))
        if selected.get('life_id',selected.get('preferred_life'))==target_life:raise ValueError('Map only before selection; never rewrite selected principal')
    imported=store.state/'servicios_persistentes'/target_life/'IMPORTACION.json'
    mapping=json.loads(imported.read_text('utf-8-sig'))
    if mapping['source_life_id']!=source_life or mapping['new_life_id']!=target_life:raise ValueError('Exact full-pair identity provenance mismatch')
    from dee_thinking.persistence import decode_metadata
    from capacidades import pi04_coordinacion_central_C2C as component
    with store.writer(target_life):
        rec,a=store.load(target_life);before_path=store.snapshot(rec);before=_view(before_path)
        entries=dict(a.world.runtime.snapshot_metadata_entries)
        if KEY not in entries or json.loads(entries[SYSTEM])['life_id']!=target_life:raise ValueError('Complete imported current system/C2C identity required')
        old=decode_metadata(entries[KEY]);new,leaf=propose_identity(old,source_life,target_life)
        if old['life_id']==target_life:
            return {'schema':'DEE.PI05.C2C.identity_mapping.v1','changed':False,'new_ticks':0,'already_current':True,
                'target_life_id':target_life,'source_life_id':source_life,
                'metadata_old_life_id':old['life_id'],'metadata_new_life_id':target_life,
                'leaf':leaf,'physical':before['physical'],'causal_prefix_sha256':before['causal_prefix_sha256']}
        component._save(a,new)
        op={'kind':'EXPLICIT_ADMINISTRATIVE_C2C_CURRENT_IDENTITY_REBIND_PI05','new_native_ticks':0,'leaf':leaf,
            'source_import_manifest_sha256':mapping['verification']['manifest_sha256'],
            'not_a_new_acquisition_or_memory_copy':True,'past_native_source_and_rows_preserved':True}
        after_rec=store.commit(rec,a,op,activate=False);after_path=store.snapshot(after_rec);after=_view(after_path)
    if before['physical']!=after['physical']or before['causal_prefix_sha256']!=after['causal_prefix_sha256']:
        raise RuntimeError('Administrative identity changed physical/interface/agenda/receipt Native prefix; preserve and stop')
    before_meta=before['metadata'];after_meta=after['metadata']
    if set(before_meta)!=set(after_meta):raise RuntimeError('Metadata key set changed outside current identity')
    changed=[k for k in before_meta if before_meta[k]!=after_meta[k]]
    if set(changed)-{SYSTEM,KEY}:raise RuntimeError('Unrelated metadata changed')
    if json.loads(after_meta[KEY])!=new or {k:v for k,v in json.loads(before_meta[KEY]).items()if k!='life_id'}!={k:v for k,v in json.loads(after_meta[KEY]).items()if k!='life_id'}:
        raise RuntimeError('More than the one C2C current identity leaf changed')
    return {'schema':'DEE.PI05.C2C.identity_mapping.v1','changed':True,'target_life':target_life,'source_life':source_life,
        'target_life_id':target_life,'source_life_id':source_life,
        'metadata_old_life_id':old['life_id'],'metadata_new_life_id':target_life,
        'new_ticks':0,'before_snapshot':str(before_path),'after_snapshot':str(after_path),'before_encoded_sha256':before['encoded_sha256'],
        'after_encoded_sha256':after['encoded_sha256'],'physical_before':before['physical'],'physical_after':after['physical'],
        'causal_prefix_before':before['causal_prefix_sha256'],'causal_prefix_after':after['causal_prefix_sha256'],
        'changed_metadata_keys':changed,'allowed_C2C_changed_leaves':['life_id'],'leaf':leaf,
        'all_other_C2C_fields_and_nonadministrative_metadata_unchanged':True,'source_originals_modified':False,
        'scope':'Technical current identity after complete same-world import only, not learning/fusion/reacquisition. Original full source and historical IDs remain evidence.'}
