"""R4: receive the actual diagonal B product OUTSIDE its comparator.
Native generic Y/Z opportunities demodulate it without reading its sign.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.integracion_situada_01 import ic_native_core as n
from capacidades.conductos_acceso_aa01 import routes_for_common_arrival
configs=[(110,'MI01_SELECTOR_PREFIJO_11','intact',20),(111,'MI01_SELECTOR_PREFIJO_11','intact',52),(112,'MI01_SELECTOR_PREFIJO_10','intact',20),(113,'MI01_SELECTOR_PREFIJO_11','cut',20),(114,'MI01_SELECTOR_PREFIJO_11','sham',20),(115,'MI01_SELECTOR_PREFIJO_11','no_command',20)]
atomic_json(E/'CONSULTA_COMPLETA_PROTOCOLO_110.json',{'cases':configs,'difference_from_R3':'Do not install the demodulator at B (its input paths cross comparator supply). At both possible diagonal output branches, three steps downstream, equal Y+0/Z+0 resources. Then fixed53-step ballistic return and symmetricZ-0 read.','criteria':'Unique state1 sem1 pureX positive load at one fixed E1 bank, dependent on acquired request and private B stimulus; cut/no-query must remove it. Both signs provisioned before the B result.'})
for number,parent,mode,value in configs:
    life='MI01_CONSULTA_'+str(number);fork(parent,life)
    def fn(a,number=number,mode=mode,value=value):
        S0=n.configuration(a)['center'];q=n.configuration(a)['last_selector_tick']+67;B=list(a.transferred_quantity.geometry['center']);rr=[]
        route=routes_for_common_arrival({'q':{'site':n.move(S0,(1,-1,0),2),'direction':[1,-1,0]}},{'q':{'site':B,'direction':[0,0,1]}},q+2,phase=13)['q']
        T=route['arrival_tick'];source=T+1;turn=source+3;end=turn+53
        if mode!='no_command':rr.append(n.arrive(a,'MI01.C.'+str(number)+'.common',S0,(1,0,0),q,5))
        for i,t in enumerate(route['turns']):
            for j,pulse in enumerate(t['pulses']):rr.append(n.arrive(a,'MI01.C.'+str(number)+'.turn.'+str(i)+'.'+str(j),t['site'],pulse['direction'],t['tick'],pulse['payload']))
        for port,payload in [('B.quantity.object.cue',5),('B.quantity.object.resource',value)]:
            rec=a.world.submit(port,payload,T-5);rr.append({'id':int(rec.id),'port':port,'tick':T-5,'payload':payload})
        banks=[]
        for sign in(-1,1):
            P=n.move(B,(sign,-1,0),3);target=n.move(P,(sign,0,1),53)
            for label,vector in [('Y',[0,1,0]),('Z',[0,0,1])]:rr.append(n.arrive(a,'MI01.C.'+str(number)+'.assoc.'+str(sign)+'.'+label,P,vector,turn,0))
            rr.append(n.arrive(a,'MI01.C.'+str(number)+'.read.'+str(sign),target,(0,0,-1),end,0));banks.append({'sign':sign,'turn':P,'target':target})
        a.run_until(q);command=n.obs(a,S0)
        if mode in('cut','sham'):
            site=n.move(S0,(1,-1,0),1)
            if mode=='sham':site=n.move(site,(0,0,1),19)
            rr.append(n.submit(a,'MI01.C.'+str(number)+'.postformed',site,(0,0,0),q,0,4))
        a.run_until(T);arrival=n.obs(a,B);a.run_until(source);answer=n.obs(a,B);a.run_until(turn);formed=[{'sign':b['sign'],'native':n.obs(a,b['turn'])}for b in banks]
        frames=[]
        for t in(turn+1,end-1,end):
            a.run_until(t);frames.append({'tick':t,'banks':[{'bank':b['sign'],'native':n.obs(a,n.move(b['turn'],(b['sign'],0,1),t-turn))}for b in banks]})
        reads=[{'sign':b['sign'],'native':n.obs(a,b['target'])}for b in banks];a.save(E/(life+'.RECIBIDO.deetsnap.gz'))
        return{'command_tick':q,'command':command,'route':route,'private_value':value,'arrival':arrival,'source_tick':source,'B_answer':answer,'formed':formed,'end_tick':end,'banks':banks,'frames':frames,'reads':reads,'requests':n.receipts(a,rr),'final':physical(a.world,occupation=True)}
    v=run(life,life,fn)['result'];print(json.dumps({'case':number,'formed':v['formed'],'reads':v['reads'],'end':v['end_tick']},ensure_ascii=False),flush=True)
