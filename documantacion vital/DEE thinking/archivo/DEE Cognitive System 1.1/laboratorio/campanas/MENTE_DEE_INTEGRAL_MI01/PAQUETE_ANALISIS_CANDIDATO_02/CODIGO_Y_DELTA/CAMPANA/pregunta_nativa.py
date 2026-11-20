"""One prepared material request conduit; no host response-selected query.
Contrasts actual learned +/- command, postformed cut and no query drive.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.integracion_situada_01 import ic_native_core as n
from capacidades.conductos_acceso_aa01 import routes_for_common_arrival

s=Store()
p=E/'MI01_SELECTOR_11.DESPUES_EXPERIENCIA.deetsnap.gz'
if not s.life_dir('MI01_SELECTOR_PREFIJO_11').exists():s.import_state(p,'MI01_SELECTOR_PREFIJO_11','cpc9_integral_n67',sha(p))
configs=[(70,'MI01_SELECTOR_PREFIJO_10','intact',20),(71,'MI01_SELECTOR_PREFIJO_11','intact',20),(72,'MI01_SELECTOR_PREFIJO_11','cut',20),(73,'MI01_SELECTOR_PREFIJO_11','sham',20),(74,'MI01_SELECTOR_PREFIJO_11','intact',52),(75,'MI01_SELECTOR_PREFIJO_11','no_query',20)]
atomic_json(E/'PREGUNTA_PROTOCOLO_070.json',{'cases':configs,'decoder':'B native +/-X readout; both present and absent route resources kept; source command not selected by desired answer','assistance':'Only generic turns and B-private object are externally supplied. No host schedules the B reader based on output; the physical learned -Y path is the reader.'})
for number,parent,mode,value in configs:
    life='MI01_PREGUNTA_'+str(number);fork(parent,life)
    def fn(a,number=number,mode=mode,value=value):
        initial=physical(a.world,occupation=True);g=n.configuration(a);S0=g['center'];last=g['last_selector_tick'];q=last+67*max(1,(a.tick+5-last+66)//67)
        B=list(a.geometry['cpc9_return']['B_quantity']['center']) if 'B_quantity'in a.geometry.get('cpc9_return',{})else[21,59,40]
        starts={'query':{'site':n.move(S0,(1,-1,0),2),'direction':[1,-1,0]}};ends={'query':{'site':B,'direction':[0,0,1]}}
        route=routes_for_common_arrival(starts,ends,q+2,phase=12)['query'];T=route['arrival_tick']+1;rr=[]
        if mode!='no_query':rr.append(n.arrive(a,'MI01.Q.'+str(number)+'.common',S0,(1,0,0),q,5))
        for i,turn in enumerate(route['turns']):
            for j,pulse in enumerate(turn['pulses']):rr.append(n.arrive(a,'MI01.Q.'+str(number)+'.turn.'+str(i)+'.'+str(j),turn['site'],pulse['direction'],turn['tick'],pulse['payload']))
        # Fixed B raw private stimulus through its existing public interface.
        for port,payload in [('B.quantity.object.cue',5),('B.quantity.object.resource',value)]:
            rec=a.world.submit(port,payload,T-5);rr.append({'id':int(rec.id),'port':port,'tick':T-5,'payload':payload})
        a.run_until(q);source=n.obs(a,S0);a.save(E/(life+'.ANTES_TRAMO.deetsnap.gz'))
        if mode in('cut','sham'):
            site=n.move(S0,(1,-1,0),1)
            if mode=='sham':site=n.move(site,(0,0,1),19)
            rr.append(n.submit(a,'MI01.Q.'+str(number)+'.postformed',site,(0,0,0),q,0,4))
        frames=[]
        for turn in route['turns']:
            a.run_until(turn['tick']);frames.append({'tick':a.tick,'turn':turn,'native':n.obs(a,turn['site'])})
        a.run_until(T-1);arrived=n.obs(a,B);a.run_until(T);answer=n.obs(a,B)
        a.save(E/(life+'.RESPUESTA.deetsnap.gz'))
        return{'initial':initial,'q':q,'B_source_tick':T,'route':route,'mode':mode,'private_value_only_B':value,'source':source,'turns':frames,'arrival':arrived,'B_response':answer,'requests':n.receipts(a,rr),'final':physical(a.world,occupation=True),'no_direct_B_reader_supplied':True}
    v=run(life,life,fn,{'mode':mode,'private_B':value})['result']
    print(json.dumps({'case':number,'source':v['source'],'arrived':v['arrival'],'B':v['B_response'],'T':v['B_source_tick']},ensure_ascii=False),flush=True)
