"""Prospective external-control extension only; never rewrites the old20 plan.

No DEE imports at module load. The only new metadata is a separately named
PI05 external environmental control, with two fixed previously observed FALSE
signals. It is not acquired participant memory or a newly learned policy.
"""
from pathlib import Path
import hashlib
import json

KEY='DEE.Cognitive.PI05.external_yoked_future.R01'
VERSION='DEE.PI05.external_yoked_future.R01'
PROTOCOL=Path(__file__).with_name('PROTOCOLO_PI05_TRANSITO_R01.json')
def _canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf8')
def _sha(v):return hashlib.sha256(v).hexdigest()
def _load_protocol():
    b=PROTOCOL.read_bytes();p=json.loads(b)
    if p.get('schema')!='DEE.PI05.transit.protocol.v1'or p.get('status')!='SEALED':raise ValueError('Frozen PI05 protocol required')
    x=p['yoked_future_extension']
    if x['ordinals']!=[20,21]or len(x['slots'])!=2:raise ValueError('Only the declared two future control exposures')
    for i,slot in enumerate(x['slots']):
        if slot['ordinal']!=20+i or slot['failed']is not False or slot['source_ordinal']!=20+i:raise ValueError('Exact observed REAL_RET2 FALSE/FALSE sources only')
    return x,_sha(b)

def _extension(a,m):
    from dee_thinking.persistence import decode_metadata
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:raise ValueError('Original20 yoked control exhausted; explicit PI05 future extension absent')
    e=decode_metadata(entries[KEY]);x,ph=_load_protocol()
    if e.get('version')!=VERSION or e.get('protocol_sha256')!=ph or e.get('slots')!=x['slots']:
        raise ValueError('Fixed PI05 external future control differs from frozen protocol')
    if e.get('old_plan_sha256')!=_sha(_canonical(m['plan'])):raise ValueError('Historical20 plan bytes changed')
    if e.get('prepared_ordinal')!=20 or m['arm']!='yoked' or not 20<=m['ordinal']<22:
        raise ValueError('No invented/exhausted external future signals')
    return e

def validate_future(a,m):
    _extension(a,m)
    return True

def replay_signal(a,m,calendar):
    e=_extension(a,m);slot=e['slots'][m['ordinal']-20]
    if calendar!=slot['calendar']:raise ValueError('PI05 future control calendar differs; no retiming or fallback')
    return slot['failed']

def prepare(a,c2c,directory):
    from dee_thinking.persistence import encode_metadata
    c2c._identity(a,directory,operation=c2c.STATE)
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY in entries:raise ValueError('PI05 future already registered; never overwrite or reset')
    m=c2c._get(a);x,ph=_load_protocol()
    if m.get('arm')!='yoked'or m.get('ordinal')!=20 or not m.get('admitted')or not m.get('ready'):
        raise ValueError('Only a closed, admitted inherited20-opportunity yoked control')
    if any(m.get(k)for k in('pending','uncertain','halted_reason')):raise ValueError('Preserve incomplete/halted future')
    if len(m['plan']['plan']['slots'])!=20:raise ValueError('Keep exact original20-slot plan')
    device=c2c._device(directory)
    if device.m['ordinal']!=20 or any(device.m.get(k)for k in('pending','feedback_pending','uncertain')):
        raise ValueError('Complete external device progress must agree; no reset')
    old=dict(entries);before=c2c._physical(a);old_plan=_canonical(m['plan'])
    e={'version':VERSION,'prepared_ordinal':20,'prepared_tick':int(a.tick),
       'protocol_sha256':ph,'old_plan_sha256':_sha(old_plan),'slots':x['slots'],
       'source_provenance':x['source_provenance'],
       'scope':'Researcher-prepared external control future; not acquired memory, target, strategy or cognitive regulation'}
    a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(e))
    after=c2c._physical(a);new=dict(a.world.runtime.snapshot_metadata_entries)
    if before!=after or {k:v for k,v in new.items()if k!=KEY}!=old or _canonical(c2c._get(a)['plan'])!=old_plan:
        raise RuntimeError('Zero-tick extension changed physical fields or historical metadata; preserve and stop')
    return {'version':VERSION,'new_native_ticks':0,'physical_before':before,'physical_after':after,
            'old_plan_sha256':e['old_plan_sha256'],'old_plan_preserved_exactly':True,
            'prepared_ordinal':20,'future_ordinals':[20,21],'future_failed':[False,False],
            'extension_sha256':_sha(_canonical(e)),'source_provenance':x['source_provenance'],'scope':e['scope']}
