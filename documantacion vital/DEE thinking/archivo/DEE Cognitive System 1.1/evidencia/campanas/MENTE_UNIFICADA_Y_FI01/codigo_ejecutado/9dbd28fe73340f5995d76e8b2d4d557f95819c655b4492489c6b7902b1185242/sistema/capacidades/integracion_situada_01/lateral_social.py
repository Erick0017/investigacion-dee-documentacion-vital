"""Executable experimental single-episode lateral coupling.
Known later failures are contractual, not hidden by an automatic rollback.
This is a prepared native encoding/decoding opportunity, not learned anatomy.
"""
import json,re
from dee_thinking.persistence import encode_metadata,decode_metadata
from . import ic_native_core as core,delayed_social as social,ic_external as external
KEY='DEE.Cognitive.System.1.1.CICLO02.lateral_social.v1'
def prepare(a,*,name,sham=False):
    if not isinstance(name,str)or not re.fullmatch(r'[A-Za-z0-9_.-]{1,48}',name)or type(sham)is not bool:raise ValueError('Explicit preparation ID and physical control required')
    p=social.get(a);bridge=external.saved(a)
    if not p or not bridge or bridge['readout']!='magnitude':raise ValueError('Existing future social opportunity and magnitude bridge required; no silent world creation')
    p=p['plan'];T=p['source_tick']
    if T-3<a.tick:raise ValueError('Freeze both sign paths before the private response; no answer-selected lateral coding')
    entries=dict(a.world.runtime.snapshot_metadata_entries);old=json.loads(decode_metadata(entries[KEY])['preparations_json'])if KEY in entries else{}
    if name in old or any(v['source_tick']==T for v in old.values()):raise ValueError('Preparation already declared, no duplicate dose')
    rr=[];banks=[];parallel=list(bridge['social_ports'])
    for b in p['banks']:
        site=core.move(b['birth'],(0,1,0),-1)
        if sham:site=core.move(site,(0,1,0),19)
        rr.append(core.submit(a,'C02.lateral.'+name+'.encodeY.'+str(b['sign']),site,(0,1,0),T,0))
        target=core.move(b['target'],(0,1,0),56)
        for v,label in(([0,0,-1],'Z'),([0,-1,0],'Y')):
            rr.append(core.arrive(a,'C02.lateral.'+name+'.read'+label+'.'+str(b['sign']),target,v,p['end_tick'],0))
        alt={**b,'target':target,'access':'fixed_lateral_Yplus56','incoming_direction':[b['sign'],1,1]};banks.append(alt)
        if not any(q['sign']==alt['sign']and q['target']==alt['target']for q in parallel):parallel.append(alt)
    result={'name':name,'source_tick':T,'prepared_at':a.tick,'sham':sham,'banks':banks,'requests':rr,'same_arrival_phase':True,
      'classification':'Admitted experimental P0 preparation with a verified first-episode retention/communication effect. NOT a stable accumulating architecture.',
      'known_adverse':'In270 later opposite/new updates lost fixed-port access and the fourth exposure expanded occupation to297938. Remote native sink variant must not be presumed a fix.',
      'limits':'Two fixed content-free encoding resources and four reader resources, both signs, no copied code or N change. No learned Y reference, autonomous strategy, P2 or unlimited stability.'}
    bridge['social_ports']=parallel;external.store(a,bridge);old[name]=result
    a.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'preparations_json':json.dumps(old,ensure_ascii=False,separators=(',',':'))}))
    return result
