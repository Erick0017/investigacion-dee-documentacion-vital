"""Prepared physical peripheral shielding, not a host packet filter.

Only two legacy record injection sites are occupied through legal inputs.
Admission remains the unmodified official engine's decision. Communication
must be independently retained via the already admitted delayed native route.
"""
import json,re
from dee_thinking.persistence import encode_metadata,decode_metadata
from app.native_tools import physical,observe
from . import ic_native_core as core
KEY='DEE.Cognitive.System.1.1.CICLO02.legacy_record_guard.v1'
def get(a):
    e=dict(a.world.runtime.snapshot_metadata_entries)
    return json.loads(decode_metadata(e[KEY])['guard_json'])if KEY in e else None

def divert_record(a,*,name,record_tick,sham=False,terminate=False):
    """Fixed native counterflow after entry, both record branches equally.

    Unlike the unsuccessful stationary injection-site guard, no material is
    placed beside the private object's initial transit. Zero pulses meet the
    Y cue one tick downstream after B's output has formed. No packet is erased
    or selected using its acquired sign; optional termination is a native
    prepared observer outside that private object path, not a Python cleanup.
    """
    if not isinstance(name,str)or not re.fullmatch(r'[A-Za-z0-9_.-]{1,48}',name):raise ValueError('Explicit preparation ID')
    if type(record_tick)is not int or record_tick-2<a.tick or type(sham)is not bool or type(terminate)is not bool:raise ValueError('Future fixed record timing and explicit physical variant required')
    old=get(a)or{'episodes':{}}
    if name in old.get('episodes',{}):raise ValueError('Episode already prepared; never reseed silently')
    ports={p.name:p for p in a.world.interfaces};rr=[];layout=[]
    for label in('minus','plus'):
        ch=ports['back.'+label+'.record'].channel
        site=[ch.injection_site.x,ch.injection_site.y,ch.injection_site.z]
        if [ch.direction.dx,ch.direction.dy,ch.direction.dz]!=[0,1,0]:raise ValueError('Legacy record geometry outside the tested contract')
        meet=core.move(site,(0,1,0));target=core.move(meet,(0,0,1),19)if sham else meet
        rr.append(core.arrive(a,'C02.record_diversion.'+name+'.'+label,target,(0,0,-1),record_tick+1,0))
        end=core.move(meet,(0,1,-1),8)
        if terminate:
            end_target=core.move(end,(0,0,1),19)if sham else end
            rr.append(core.submit(a,'C02.record_terminator.'+name+'.'+label,end_target,(0,0,0),record_tick-2,0,4))
        layout.append({'bank':label,'legacy_injection':site,'meeting':meet,'counterflow_target':target,'meeting_tick':record_tick+1,'predicted_deflected_direction':[0,1,-1],'optional_terminator':end})
    ep={'name':name,'declared_at':a.tick,'record_tick':record_tick,'sham':sham,'terminate':terminate,'layout':layout,'requests':rr,
        'classification':'Prepared finite P0 route intervention, not learned selection or deletion of old matter.'}
    old.setdefault('episodes',{})[name]=ep
    a.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'guard_json':json.dumps(old,ensure_ascii=False,separators=(',',':'))}))
    return ep
def install(a,*,name,sham=False):
    if get(a)is not None:raise ValueError('Peripheral guard already declared; no hidden reseeding')
    if not isinstance(name,str)or not re.fullmatch(r'[A-Za-z0-9_.-]{1,48}',name)or type(sham)is not bool:raise ValueError('Explicit name and control required')
    ports={p.name:p for p in a.world.interfaces};rows=[];rr=[];at=a.tick+2
    for label in('minus','plus'):
        p=ports['back.'+label+'.record'].channel
        actual=[p.injection_site.x,p.injection_site.y,p.injection_site.z]
        site=core.move(actual,(0,0,1),9)if sham else actual
        pre=observe(a.world,site)
        rr.append(core.submit(a,'C02.legacy_guard.'+name+'.'+label,site,(0,0,0),at,0,4))
        rows.append({'bank':label,'legacy_injection':actual,'guard_site':site,'pre':pre})
    a.run_until(at)
    for row in rows:row['post']=observe(a.world,row['guard_site'])
    result={'name':name,'sham':sham,'prepared_tick':at,'sites':rows,'requests':core.receipts(a,rr),
            'classification':'Prepared P0 peripheral interface protection. Not learned filtering or removal of existing matter.',
            'tradeoff':'Legacy record inputs may be rejected_occupied. The delayed social route is separate and must be tested; do not call this preservation of the old record interface.',
            'physical':physical(a.world,occupation=True)}
    a.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'guard_json':json.dumps(result,ensure_ascii=False,separators=(',',':'))}))
    return result
