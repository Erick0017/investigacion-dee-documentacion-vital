"""New frozen actuator revision, not retrospective alteration of old metrics.
State1/semantic1/XY orientation may be material information even at s_reg0.
No-action, omitted-return and postformed-cut controls test that distinction.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.integracion_situada_01 import ic_native_core as n,ic_body as old_body
from capacidades import integracion_situada_01 as integrated
def physical_command(v):return v['state']==1 and v['semantic']==1 and v['direction'][0]==1 and abs(v['direction'][1])==1 and v['direction'][2]==0
contexts=[1,1,1,-1,-1,-1,-1,1,1,1,-1,-1,1,1,-1,1,1,1,1,-1,-1,-1,1,1]
configs=[(40,'intact','none'),(41,'omit_return','none'),(42,'no_action','none'),(43,'intact','cut'),(44,'intact','sham')]
atomic_json(E/'DIRECCION_CERO_CRITERIO_PREVIO_040.json',{'revision':'MI01.material-direction.r1','frozen_before_new_reserved_sequences':True,
 'motivation_exploratory':'Exploratory20 continues native XY orientation after its payload metric is exhausted. Its old4/18 count remains unchanged. A new codec may use material direction only if the fixed causal controls support it.',
 'command':'state1 semantic1 direction(+X,+/-Y,0), regardless of s_reg; direction0/pureY/state0 are not commands. Both positive-load and zero-load counts reported.',
 'contexts':contexts,'cases':configs,'cut':'Both outgoing routes at predeclared cycle4, two steps after formed output; same-dose sham Z+19. No route chosen from expected answer.',
 'scope':'Prepared actuator law, possible native history/feedback use. Not an energy claim, learned word, global policy or reinterpretation of old PASS.',
 'effective_action_criterion':'Native choice atS AND its material consequence at branch contactP. A postformed cut can leave an apparently useful emitted choice but no executed physical contact; count separately.'})
for number,mode,cut in configs:
    life='MI01_DIRECCION_'+str(number);fork('MI01_SELECTOR_PREFIJO_10',life)
    def fn(a,number=number,mode=mode,cut=cut):
        initial=physical(a.world,occupation=True)
        plan=n.situated(a,name='MI01_DIR_'+str(number),availability=contexts,mode=mode,compact=True,gap=0,stream=True,shunt='a_only',queue_only=True)
        rows=[];rr=[];S0=plan['center'];g=n.configuration(a)
        for index,p in enumerate(plan['plans']):
            t=p['query_tick'];a.run_until(t);action=n.obs(a,S0)
            if index==4 and cut!='none':
                a.save(E/(life+'.ANTES_CORTE.deetsnap.gz'))
                for sign in(-1,1):
                    site=n.move(S0,(1,sign,0),2)
                    if cut=='sham':site=n.move(site,(0,0,1),19)
                    rr.append(n.submit(a,'MI01.DIR.cut.'+str(number)+'.'+str(sign),site,(0,0,0),t+1,0,4))
            a.run_until(t+4);contact={str(r):n.obs(a,n.move(S0,(1,r,0),4))for r in(-1,1)}
            a.run_until(p['return_tick']);post=n.obs(a,S0);g['last_selector_tick']=a.tick;g['stream_action_tick']=a.tick;n.save(a,g)
            emitted=physical_command(action);r=action['direction'][1]if emitted else 0
            target_direction=[1 if r==p['availability']else-1,r,0]
            reached=bool(emitted and contact[str(r)]['state']==1 and contact[str(r)]['semantic']==1 and contact[str(r)]['direction']==target_direction)
            rows.append({'index':index,'tick':t,'availability':p['availability'],'action':action,'native_contact':contact,'next_native':post,
             'positive_load_old_codec':old_body.qualified(action),'material_direction_new_codec':physical_command(action),
             'native_route':r,'choice_useful':emitted and r==p['availability'],'contact_executed':reached,
             'useful':reached and r==p['availability']})
        native_end=physical(a.world,occupation=True);use=integrated.act_external(a,steps=1)
        return{'initial':initial,'plan':plan,'rows':rows,'cut_requests':n.receipts(a,rr),'all_requests':[n.receipts(a,z)for z in plan['requests']],
          'native_end':native_end,'external':use,'final':physical(a.world,occupation=True),'new_codec_not_applied_to_historical_scores':True}
    out=run(life,'MI01_DIRECCION_'+str(number),fn,{'mode':mode,'cut':cut,'criterion':'DIRECCION_CERO_CRITERIO_PREVIO_040.json'})['result']
    print(json.dumps({'case':number,'old_positive_load':sum(z['positive_load_old_codec']for z in out['rows']),'new_material':sum(z['material_direction_new_codec']for z in out['rows']),
      'useful':sum(z['useful']for z in out['rows']),'after4':[[z['index'],z['action']['s_reg'],z['native_route'],z['availability']]for z in out['rows'][4:]],'cuts':out['cut_requests']},ensure_ascii=False),flush=True)
