"""Short native failure product -> information request candidate.
All opportunities exist in advance; Python never tests a failed action to
choose a reader. The two phase windows and their sign mapping are prepared.
"""
from capacidades.integracion_situada_01 import ic_native_core as n
from capacidades.conductos_acceso_aa01 import turning_inputs
from . import saved,put
from . import habitat_nativo as base,consulta_nativa as query,retorno_selector as reply

def prepare(a,*,name,availability,private_values,mode='intact',actor_return=False,include_initial_failure=False):
    if mode not in('intact','omit_failure_return','cut_failure','sham_failure','cut_reply'):raise ValueError('Explicit direct-failure contrast')
    p=base.prepare(a,name=name,availability=availability,private_values=private_values,mode='intact'if actor_return else'omit_actor_return')
    extra=[];opportunities=[];S=p['S'];F=n.move(S,(0,1,0),8);vin=[-1,1,0];vout=[0,-1,0];pulses=turning_inputs(vin,vout)
    for z in(p['plans']if include_initial_failure else p['plans'][1:]):
        i=z['index'];q=z['query_tick'];trigger=q+16
        if mode!='omit_failure_return':
            for k,pulse in enumerate(pulses):extra.append(n.arrive(a,'MI01.failure.'+name+'.turn.'+str(i)+'.'+str(k),F,pulse['direction'],q+8,pulse['payload']))
        # Same prepared material opportunity, whether or not a failure arrives.
        extra.append(n.arrive(a,'MI01.failure.'+name+'.common.'+str(i),S,(1,0,0),trigger,0))
        ghost=[(x>0)-(x<0)for x in[sum(v['direction'][j]for v in pulses)for j in range(3)]];guard=n.move(F,ghost,2)
        extra.append(n.submit(a,'MI01.failure.'+name+'.ghost_guard.'+str(i),guard,(0,0,0),q+9,0,4))
        if mode in('cut_failure','sham_failure'):
            site=n.move(F,vin,-1)
            if mode=='sham_failure':site=n.move(site,(0,0,1),19)
            extra.append(n.submit(a,'MI01.failure.'+name+'.post_action.'+str(i),site,(0,0,0),q+6,0,4))
        qp=query.prepare(a,name=name+'.FQ'+str(i),private_value=z['private_B_raw'],query_tick=trigger,drive=False,wire_external=False,reader_guard=True,late_protection='full')
        rp=reply.prepare(a,query_name=qp['name'],name=name+'.FR'+str(i),common=False,mode='cut'if mode=='cut_reply'else'intact',ghost_guard='local')
        opportunities.append({'index':i,'failure_site':F,'product_tick':q+8,'trigger_tick':trigger,'query_name':qp['name'],'reply_name':rp['name'],'return_tick':rp['arrival_tick']})
    cfg=saved(a);body=cfg['native_habitats'][name];body['original_end_tick']=body['end_tick'];body['end_tick']=max([body['end_tick']]+[z['return_tick']for z in opportunities]);body['direct_failure']={'mode':mode,'actor_return':actor_return,'include_initial_failure':include_initial_failure,'opportunities':opportunities,'requests':extra,'frames':[],'prepared_not_learned':'A native failed+action product can become a generic query command through a fixed two-carrier turn; absence of a product is not translated to failure by Python.'};put(a,cfg);return body

def advance(a,*,name,until=None):
    cfg=saved(a);body=cfg['native_habitats'][name];until=body['end_tick']if until is None else until;events={}
    if until<a.tick:raise ValueError('No failure-candidate rewind')
    for z in body['direct_failure']['opportunities']:
        qp=cfg['material_queries'][z['query_name']]
        for kind,t,site in [('failure_product',z['product_tick'],z['failure_site']),('failure_request',z['trigger_tick'],body['S']),('private_source',qp['source_tick'],qp['B']),('failure_return',z['return_tick'],body['S'])]:
            if a.tick<t<=until:events.setdefault(t,[]).append((kind,z['index'],site))
    rows=[];base_frames=[]
    for t in sorted(events):
        base_frames.extend(base.advance(a,name=name,until=t)['frames'])
        for kind,i,site in events[t]:rows.append({'tick':t,'kind':kind,'index':i,'native':n.obs(a,site)})
    base_frames.extend(base.advance(a,name=name,until=until)['frames']);cfg=saved(a);body=cfg['native_habitats'][name];body['direct_failure']['frames'].extend(rows);put(a,cfg)
    return{'frames':base_frames,'failure_frames':rows,'tick':a.tick,'requests':n.receipts(a,body['direct_failure']['requests'])}
