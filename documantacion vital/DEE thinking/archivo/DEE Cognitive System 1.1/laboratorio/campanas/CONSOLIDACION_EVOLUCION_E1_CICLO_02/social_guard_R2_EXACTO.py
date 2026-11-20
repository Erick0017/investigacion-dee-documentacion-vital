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
