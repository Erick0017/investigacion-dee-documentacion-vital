"""Bounded source/reader simultaneity diagnosis; retain failed phase12."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.integracion_situada_01 import ic_native_core as n
from capacidades.conductos_acceso_aa01 import routes_for_common_arrival
configs=[(76,13,'native',20),(77,13,'existing_reader',20),(78,13,'native',52),(79,14,'native',20),(80,13,'no_command',20)]
atomic_json(E/'PREGUNTA_FASE_PROTOCOLO_076.json',{'cases':configs,'changed_factor':'Route co-arrival phase13 vs prior12. Matched ordinary B reader calibrates meaning of scheduled input tick. No runtime source modification.'})
for number,phase,mode,value in configs:
    life='MI01_PREGUNTA_FASE_'+str(number);fork('MI01_SELECTOR_PREFIJO_11',life)
    def fn(a,number=number,phase=phase,mode=mode,value=value):
        S0=n.configuration(a)['center'];q=n.configuration(a)['last_selector_tick']+67;B=a.transferred_quantity.geometry['center'];rr=[]
        route=routes_for_common_arrival({'q':{'site':n.move(S0,(1,-1,0),2),'direction':[1,-1,0]}},{'q':{'site':B,'direction':[0,0,1]}},q+2,phase=phase)['q']
        arrival=route['arrival_tick'];T=13+67*((arrival-13)//67)
        if mode=='existing_reader':
            rec=a.world.probe('B.quantity.reader',7,T-1);rr.append({'id':int(rec.id),'port':'B.quantity.reader','tick':T-1,'payload':7})
        else:
            if mode!='no_command':rr.append(n.arrive(a,'MI01.F.'+str(number)+'.common',S0,(1,0,0),q,5))
            for i,turn in enumerate(route['turns']):
                for j,pulse in enumerate(turn['pulses']):rr.append(n.arrive(a,'MI01.F.'+str(number)+'.turn.'+str(i)+'.'+str(j),turn['site'],pulse['direction'],turn['tick'],pulse['payload']))
        for port,payload in [('B.quantity.object.cue',5),('B.quantity.object.resource',value)]:
            rec=a.world.submit(port,payload,T-5);rr.append({'id':int(rec.id),'port':port,'tick':T-5,'payload':payload})
        frames=[]
        for t in range(min(T,arrival)-2,max(T,arrival)+3):
            a.run_until(t);frames.append({'tick':a.tick,'B':n.obs(a,B),'R':n.obs(a,a.transferred_quantity.geometry['reference_hub']),'O':n.obs(a,a.transferred_quantity.geometry['object_hub'])})
        return{'phase':phase,'mode':mode,'q':q,'arrival':arrival,'T':T,'frames':frames,'route':route,'requests':n.receipts(a,rr),'private_value':value,'final':physical(a.world,occupation=True)}
    v=run(life,life,fn)['result'];print(json.dumps({'case':number,'frames':v['frames']},ensure_ascii=False),flush=True)
