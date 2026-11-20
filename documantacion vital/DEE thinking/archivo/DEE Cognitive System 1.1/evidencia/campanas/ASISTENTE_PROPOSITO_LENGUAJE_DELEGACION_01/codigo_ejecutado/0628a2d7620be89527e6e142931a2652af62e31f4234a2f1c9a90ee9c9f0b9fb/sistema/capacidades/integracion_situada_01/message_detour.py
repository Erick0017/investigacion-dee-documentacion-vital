"""Admitted finite P0 message protection, not learned route selection.
Both possible private messages receive the same fixed zero opportunities.
Neither old content, expected sign nor successful branch is read here.
"""
import json,re
from dee_thinking.persistence import encode_metadata,decode_metadata
from capacidades.conductos_acceso_aa01 import turning_inputs
from . import ic_native_core as core,delayed_social as social
KEY='DEE.Cognitive.System.1.1.CICLO02.message_detour.v1'
def prepare(a,*,name,geometry='excursion8',ghost='divert'):
    if not isinstance(name,str)or not re.fullmatch(r'[A-Za-z0-9_.-]{1,48}',name):raise ValueError('New explicit short preparation ID required')
    if geometry not in('excursion8','excursion9')or ghost not in('divert','sham','none'):raise ValueError('Only identified finite geometry/ghost variants are admitted')
    p=social.get(a)
    if not p:raise ValueError('Declare the future social opportunity first; no new world or memory is created')
    p=p['plan'];T=p['source_tick'];offsets=(40,48,56)if geometry=='excursion8'else(38,47,56)
    if T+offsets[0]-3<a.tick:raise ValueError('Future turn opportunities required; no retrospective repair or favorable timing')
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    state=json.loads(decode_metadata(entries[KEY])['preparations_json'])if KEY in entries else{}
    if name in state or any(q['source_tick']==T for q in state.values()):raise ValueError('This message already has a declared detour; no duplicate dose or silent replacement')
    rr=[];turns=[];shunts=[];first,middle,last=offsets
    for b in p['banks']:
        sign=b['sign'];v0=[sign,0,1];v1=[sign,1,1];v2=[sign,-1,1]
        p1=core.move(b['birth'],v0,first-1);p2=core.move(p1,v1,middle-first);p3=core.move(p2,v2,last-middle)
        for index,(site,t,vin,vout)in enumerate(((p1,T+first,v0,v1),(p2,T+middle,v1,v2),(p3,T+last,v2,v0))):
            pulses=turning_inputs(vin,vout);turn={'bank':sign,'site':site,'tick':t,'incoming':vin,'outgoing':vout,'pulses':pulses};turns.append(turn)
            for j,q in enumerate(pulses):rr.append(core.arrive(a,'C02.message.'+name+'.turn.'+str(sign)+'.'+str(index)+'.'+str(j),site,q['direction'],t,q['payload']))
    if ghost!='none':
        for i,turn in enumerate(turns):
            direction=[(v>0)-(v<0)for v in[sum(p['direction'][axis]for p in turn['pulses'])for axis in range(3)]]
            if not any(direction):continue
            axis=next((j for j in(2,0,1)if direction[j]==0),0);v=[0,0,0];v[axis]=1 if direction[axis]==0 else-direction[axis]
            target=core.move(turn['site'],direction,6)
            if ghost=='sham':target=core.move(target,(0,0,1),19)
            when=turn['tick']+6;r=core.arrive(a,'C02.message.'+name+'.ghost.'+str(i),target,v,when,0);rr.append(r)
            shunts.append({'turn_index':i,'resource_only_direction':direction,'target':target,'tick':when,'counterflow':v,'request':r})
    result={'name':name,'prepared_at_tick':a.tick,'source_tick':T,'geometry':geometry,'offsets':list(offsets),'ghost':ghost,'turns':turns,'shunts':shunts,'requests':rr,
      'classification':'P0 prepared physical protection; content remains native. No learned attention, autonomous loss detector or P2.',
      'evidence_domain':'Late inherited C02 state: four private updates20/52/12/60, new content4/4 with divert vs2/4 sham. Old independent+ code survives first update but is lost later. No claim of global superiority.',
      'not_a_replacement':'Does not remove the back.record protection or generic assisted/prepositioned recovery; those have distinct domains.'}
    state[name]=result;a.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'preparations_json':json.dumps(state,ensure_ascii=False,separators=(',',':'))}))
    return result
