"""One bounded follow-up: where does the locally rescued reply fail next?"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from controles_desde_prefijo_fijado import prefix,name
from capacidades.mente_integral_mi01 import externo_selector as motor,saved
from capacidades.integracion_situada_01 import ic_native_core as n
life='MI01_SEGUNDO_OBSTACULO_479';fork('E1_MI01_MAIN',life,checkpoint=prefix())
atomic_json(E/'SEGUNDO_OBSTACULO_PROTOCOLO_479.json',{'basis':'476guard restores150 atK25009/R25011 but NOT S25154;477sham preserves338 and failed route. Do not call the first clash a complete explanation.','scope':'Replay the same prepared guard, seven external steps, passive observations at each first-reply return turn. No second repair, no new decoder or future imported to MAIN.','stop_rule':'Locate the next missing/misrouted signature, preserve it and close this diagnostic family rather than designing an unlimited succession of guards.'})
def fn(a):
    guard=n.submit(a,'MI01.second_obstacle.guard188',[24,57,41],(0,0,0),25007,0,4);g=saved(a);h=g['native_habitats'][name];f=h['direct_failure']['opportunities'][0];rp=g['selector_returns'][f['reply_name']];events={};original=a.run_until;frames=[]
    for sign,route in rp['routes'].items():
        for i,turn in enumerate(route['turns']):
            for dt in(-1,0):events.setdefault(turn['tick']+dt,[]).append({'sign':sign,'turn_index':i,'site':turn['site'],'expected_outgoing':turn['outgoing'],'is_post':dt==0})
    def passive(t):
        for when in sorted(v for v in events if a.tick<v<=t):
            original(when);items=[{**z,'native':n.obs(a,z['site'])}for z in events[when]];p=E/(life+'.T'+str(when)+'.DIAGNOSTICO_NO_OPERATIVO.deetsnap.gz');a.save(p);frames.append({'tick':when,'items':items,'physical':physical(a.world,occupation=True),'snapshot':str(p.relative_to(R)),'sha256':sha(p)})
        original(t)
    a.run_until=passive
    try:r=motor.run(a,steps=7,mode='closed',feedback='cost',transition=True,habitat=name,motor_codec='native_body_roles')
    finally:a.run_until=original
    return{'external':r,'frames':frames,'guard':n.receipts(a,[guard]),'final':physical(a.world,occupation=True),'scope':'Selected full diagnostic pre/post worlds; no supported continuation from an in-flight bridge snapshot. Final Store boundary is complete.'}
v=run(life,'MI01_479_SEGUNDO_OBSTACULO',fn)['result'];points=[{'tick':f['tick'],'occupied':f['physical']['occupied'],**z}for f in v['frames']for z in f['items']if z['sign']=='1'and z['is_post']];print(json.dumps(points,ensure_ascii=False))
