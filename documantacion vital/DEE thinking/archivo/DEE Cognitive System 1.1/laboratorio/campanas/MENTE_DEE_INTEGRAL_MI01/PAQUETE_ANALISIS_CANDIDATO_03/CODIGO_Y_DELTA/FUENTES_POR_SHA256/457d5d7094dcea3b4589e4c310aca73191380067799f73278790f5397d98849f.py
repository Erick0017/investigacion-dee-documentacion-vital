"""Fixed generic positive resource, not host restoration of learned state."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.integracion_situada_01 import ic_native_core as n,ic_body as b
from capacidades import integracion_situada_01 as integrated
def command_material(v):return v['state']==1 and v['semantic']==1 and v['direction'][0]==1 and abs(v['direction'][1])==1 and v['direction'][2]==0
contexts=[1]*6+[-1]*6+[1]*6+[-1]*6
configs=[(50,5,False),(51,5,True),(52,7,False)]
atomic_json(E/'SUMINISTRO_PROTOCOLO_050.json',{'cases':configs,'contexts':contexts,'source':'MI01_SELECTOR_PREFIJO_10',
 'inputs':'Two generic carriers at EVERY common opportunity: (+X,+Z) with fixed5or7 and (+X,-Z) with0, so Z cancels without supplying Y. Same dose, no missing-memory inspection.',
 'comparison':'Sham shiftedY19. Native output atS, material request two steps downstream, and actual contact recorded separately. Fixed external supply is not endogenous metabolism or learned maintenance.'})
for number,load,sham in configs:
    life='MI01_SUMINISTRO_'+str(number);fork('MI01_SELECTOR_PREFIJO_10',life)
    def fn(a,number=number,load=load,sham=sham):
        initial=physical(a.world,occupation=True);plan=n.situated(a,name='MI01_SUPPLY_'+str(number),availability=contexts,mode='intact',compact=True,gap=0,stream=True,shunt='a_only',queue_only=True)
        S0=plan['center'];target=n.move(S0,(0,1,0),19)if sham else S0;rr=[]
        for i,p in enumerate(plan['plans']):
            for k,(v,z)in enumerate((([1,0,1],load),([1,0,-1],0))):rr.append(n.arrive(a,'MI01.supply.'+str(number)+'.'+str(i)+'.'+str(k),target,v,p['query_tick'],z))
        rows=[];g=n.configuration(a)
        for i,p in enumerate(plan['plans']):
            t=p['query_tick'];a.run_until(t);action=n.obs(a,S0);a.run_until(t+2)
            ports={str(r):n.obs(a,n.move(S0,(1,r,0),2))for r in(-1,1)}
            a.run_until(t+4);contacts={str(r):n.obs(a,n.move(S0,(1,r,0),4))for r in(-1,1)}
            a.run_until(p['return_tick']);post=n.obs(a,S0);g['last_selector_tick']=a.tick;g['stream_action_tick']=a.tick;n.save(a,g)
            r=action['direction'][1]if command_material(action)else 0
            executed=bool(r and contacts[str(r)]['state']==1 and contacts[str(r)]['direction']==[1 if r==p['availability']else-1,r,0])
            rows.append({'index':i,'tick':t,'availability':p['availability'],'action':action,'downstream_request_ports':ports,'contacts':contacts,'post':post,
              'payload_bearing':b.qualified(action),'material':command_material(action),'choice_useful':bool(r and r==p['availability']),'executed':executed,'useful':executed and r==p['availability']})
        use=integrated.act_external(a,steps=1)
        return{'initial':initial,'plan':plan,'supply_requests':n.receipts(a,rr),'rows':rows,'external':use,'final':physical(a.world,occupation=True)}
    out=run(life,'MI01_SUMINISTRO_'+str(number),fn,{'fixed_load':load,'sham':sham})['result']
    print(json.dumps({'case':number,'positive':sum(z['payload_bearing']for z in out['rows']),'material':sum(z['material']for z in out['rows']),'executed':sum(z['executed']for z in out['rows']),'useful':sum(z['useful']for z in out['rows']),
      'last_ports':out['rows'][-1]['downstream_request_ports'],'final_occupation':out['final']['occupied']},ensure_ascii=False),flush=True)
