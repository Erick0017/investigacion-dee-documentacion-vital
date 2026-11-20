"""Material learned request -> private B comparison -> native return code.
All routes and both message resources are fixed before any measured answer.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.integracion_situada_01 import ic_native_core as n
from capacidades.conductos_acceso_aa01 import routes_for_common_arrival
configs=[(90,'MI01_SELECTOR_PREFIJO_11','intact',20),(91,'MI01_SELECTOR_PREFIJO_11','intact',52),(92,'MI01_SELECTOR_PREFIJO_10','intact',20),(93,'MI01_SELECTOR_PREFIJO_11','cut',20),(94,'MI01_SELECTOR_PREFIJO_11','sham',20),(95,'MI01_SELECTOR_PREFIJO_11','no_command',20)]
atomic_json(E/'PREGUNTA_RETORNO_PROTOCOLO_090.json',{'cases':configs,'preparation':'Phase13 material Z request, fixed Y+0 demodulation, both-sign Z0 association and both-sign readout, all prior to results. Request exists only for physical -Y command.','semantic_claim':'Prepared routing/generic query conditioned by actually acquired selector; not a learned question-word or self-discovered missing-information criterion. Private content must originate at B.'})
for number,parent,mode,value in configs:
    life='MI01_PREGUNTA_RETORNO_'+str(number);fork(parent,life)
    def fn(a,number=number,mode=mode,value=value):
        S0=n.configuration(a)['center'];q=n.configuration(a)['last_selector_tick']+67;B=list(a.transferred_quantity.geometry['center']);rr=[]
        route=routes_for_common_arrival({'q':{'site':n.move(S0,(1,-1,0),2),'direction':[1,-1,0]}},{'q':{'site':B,'direction':[0,0,1]}},q+2,phase=13)['q']
        T=route['arrival_tick'];source=T+1;end=source+56
        if mode!='no_command':rr.append(n.arrive(a,'MI01.PR.'+str(number)+'.common',S0,(1,0,0),q,5))
        for i,turn in enumerate(route['turns']):
            for j,pulse in enumerate(turn['pulses']):rr.append(n.arrive(a,'MI01.PR.'+str(number)+'.turn.'+str(i)+'.'+str(j),turn['site'],pulse['direction'],turn['tick'],pulse['payload']))
        for port,payload in [('B.quantity.object.cue',5),('B.quantity.object.resource',value)]:
            rec=a.world.submit(port,payload,T-5);rr.append({'id':int(rec.id),'port':port,'tick':T-5,'payload':payload})
        rr.append(n.arrive(a,'MI01.PR.'+str(number)+'.Y_demod',B,(0,1,0),source,0))
        banks=[]
        for sign in(-1,1):
            birth=n.move(B,(sign,0,0));target=n.move(birth,(sign,0,1),55)
            rr.append(n.submit(a,'MI01.PR.'+str(number)+'.record.'+str(sign),n.move(birth,(0,0,1),-1),(0,0,1),source,0))
            rr.append(n.arrive(a,'MI01.PR.'+str(number)+'.read.'+str(sign),target,(0,0,-1),end,0));banks.append({'sign':sign,'birth':birth,'target':target})
        a.run_until(q);command=n.obs(a,S0)
        if mode in('cut','sham'):
            site=n.move(S0,(1,-1,0),1)
            if mode=='sham':site=n.move(site,(0,0,1),19)
            rr.append(n.submit(a,'MI01.PR.'+str(number)+'.postformed',site,(0,0,0),q,0,4))
        a.run_until(T);arrival=n.obs(a,B);a.run_until(source);answer=n.obs(a,B);a.save(E/(life+'.FUENTE.deetsnap.gz'))
        frames=[]
        for t in(source+1,source+2,end-1,end):
            a.run_until(t);frames.append({'tick':t,'banks':[{'bank':b['sign'],'position':n.move(b['birth'],(b['sign'],0,1),min(t-source-1,55)),'native':n.obs(a,n.move(b['birth'],(b['sign'],0,1),min(t-source-1,55)))}for b in banks]})
        reads=[{'sign':b['sign'],'native':n.obs(a,b['target'])}for b in banks]
        return{'command_tick':q,'command':command,'route':route,'private_value':value,'arrival':arrival,'source_tick':source,'B_answer':answer,'end_tick':end,'banks':banks,'frames':frames,'reads':reads,'requests':n.receipts(a,rr),'final':physical(a.world,occupation=True)}
    v=run(life,life,fn)['result'];print(json.dumps({'case':number,'command':v['command']['direction'],'B':v['B_answer'],'reads':v['reads'],'end':v['end_tick']},ensure_ascii=False),flush=True)
