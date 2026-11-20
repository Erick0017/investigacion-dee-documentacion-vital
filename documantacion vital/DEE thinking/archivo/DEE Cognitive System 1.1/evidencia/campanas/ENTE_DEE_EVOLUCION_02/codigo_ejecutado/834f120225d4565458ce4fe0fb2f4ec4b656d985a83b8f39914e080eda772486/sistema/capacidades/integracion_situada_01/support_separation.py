"""Finite prepared two-pulse restoration/separation of existing supports.
Geometry and timing are fixed BEFORE content evaluation. No old sign, word,
reference, target, field write, host repair callback or extra decoder is used.
"""
import json,re
from dee_thinking.persistence import encode_metadata,decode_metadata
from . import ic_native_core as core,delayed_social as social,lateral_social
KEY='DEE.Cognitive.System.1.1.CICLO02.support_separation.v1'
def prepare(a,*,name,mode='paired'):
    if not isinstance(name,str)or not re.fullmatch(r'[A-Za-z0-9_.-]{1,48}',name):raise ValueError('New explicit short preparation ID required')
    if mode not in('paired','sham','lift_only'):raise ValueError('Only the identified finite preparation/controls are admitted')
    p=social.get(a)
    if not p:raise ValueError('A declared social episode is required; no silent new world or memory')
    p=p['plan'];entries=dict(a.world.runtime.snapshot_metadata_entries)
    if lateral_social.KEY not in entries:raise ValueError('This limited preparation requires the declared lateral coupling')
    lateral=json.loads(decode_metadata(entries[lateral_social.KEY])['preparations_json'])
    if not any(v['source_tick']==p['source_tick']and not v['sham']for v in lateral.values()):raise ValueError('The current episode has no declared real lateral preparation')
    anchor=p['end_tick']+67
    if anchor%67!=3 or a.tick>anchor+1:raise ValueError('Prepare before the first application boundary; no retrospective repair after coalescence')
    old=json.loads(decode_metadata(entries[KEY])['preparations_json'])if KEY in entries else{}
    if name in old or any(v['anchor_tick']==anchor for v in old.values()):raise ValueError('This opportunity was already declared; no hidden repeated dose')
    b=next(z for z in p['banks']if z['sign']==-1)
    first=core.move(core.move(b['target'],(-1,0,0),4),(0,0,-1),6)
    second=core.move(first,(-1,0,1),3);rr=[];layout=[]
    for index,(site,v,t)in enumerate(((first,[0,0,1],anchor+4),(second,[0,0,-1],anchor+7))):
        if index==1 and mode=='lift_only':continue
        target=core.move(site,(0,1,0),19)if mode=='sham'else site
        request=core.arrive(a,'C02.support_separation.'+name+'.'+str(index),target,v,t,0);rr.append(request)
        layout.append({'target':target,'direction':v,'tick':t,'request':request})
    result={'name':name,'prepared_at':a.tick,'anchor_tick':anchor,'source_tick':p['source_tick'],'mode':mode,'layout':layout,'requests':rr,
       'classification':'P0 assisted finite native reorientation. Existing transformed content supplies the recovered sign/load; no learned loss detector or P2 strategy.',
       'scope':'Late N67 C02 layout: inaccessible-X-Z7 returns to the existing negative-z26 reader and avoids coalescing with+X7 atz23. Both zeros carry no acquired answer. Same fixed readers in every control.',
       'limits':'Not universal reconstruction of destroyed information. First three uses preserve both old codes and lateral new code; later private52 update loses the new lateral access while old codes survive. Calendar/support selection remains prepared.'}
    old[name]=result;a.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'preparations_json':json.dumps(old,ensure_ascii=False,separators=(',',':'))}))
    return result
