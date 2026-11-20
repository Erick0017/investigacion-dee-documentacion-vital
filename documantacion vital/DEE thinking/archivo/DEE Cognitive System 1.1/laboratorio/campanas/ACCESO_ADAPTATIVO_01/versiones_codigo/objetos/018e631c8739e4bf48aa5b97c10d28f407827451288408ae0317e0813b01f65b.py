"""Acquired access direction drives a native query into lived E1 word forms.

No new target word/reference is supplied. The two fixed transport opportunities
are prepared before outcomes. One common query is routed by native history.
Consumptive mode transmits the selected form to a material B and tests its use.
"""
from pathlib import Path
import argparse,sys,json,gzip
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args()
sys.path[:0]=[str(a.system),str(Path(__file__).parent),str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01')]
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,paisaje_causal_01 as pc
from instrumentos_pc01 import guard,receipts,sha,frame,witness
from conductos_nativos import routes_for_common_arrival
from dee_thinking.persistence import encode_metadata

protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='PC01_CONTINUIDAD28_far_guard';life='AA01_CONECTADO10_'+a.case;s.fork(parent,life,kind='CANDIDATE')
S=[32,32,49];N=67;initial=-1 if'initialdown'in a.case else 1;revised=-initial;consume='read_only'not in a.case
def mv(q,d,k):return[(q[i]+d[i]*k)%N for i in range(3)]
training={}
for j in(-1,1):
    for r in(-1,1):
        E=mv(mv(S,(j,0,0),-10),(0,r,0),10);Q=mv(E,(j,r,1),-4);H=mv(Q,(0,0,1),-6)
        training[str(j)+','+str(r)]={'j':j,'r':r,'outcome':E,'query':Q,'source':H}
data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'prepared_policy_site':S,'training_geometry':training,'initial_available_route':initial,'second_available_route':revised,'consumptive_word_use':consume,'assistance_before':'Prepared symmetric exploration, finite feedback normalization, R0 residual-route protection, generic X query, two geometric conductors and material recipient opportunities. No host branches on an observed route or word. Existing E1native learned forms are the only source of their Zcontent. No current magnitude judgment is claimed.','requests':[]}

def trial(x):
    start=x.tick;data['epoch']=start;data['pre']=physical(x.world,occupation=True);words=e.prepare(x)['words']
    def send(name,site,d,t,payload=0,sem=1):
        request=guard(x.world,'AA01.L10.'+name,site,t,direction=d,semantic=sem,payload=payload);data['requests'].append(request)
    def arrive(name,site,d,t,payload=0):send(name,mv(site,d,-3),d,t-3,payload)
    # Acquisition and revision use only nonlinguistic material route trials.
    for key,z in training.items():
        for label,site,t in(('pulse',mv(z['query'],(1,0,0),6),13),('feedback',mv(z['outcome'],(0,-z['r'],-1),4),16)):
            if'support_sham'in a.case:site=mv(site,(0,0,1),12)
            send('SUPPORT.'+key+'.'+label,site,(0,0,0),start+t,0,4)
    for episode,(offset,available)in enumerate(((0,initial),(67,revised))):
        if episode and'no_second'in a.case:continue
        for key,z in training.items():
            r=z['r'];j=z['j'];tag=str(episode)+'.'+key
            if'no_history'not in a.case:
                arrive('LEARN.'+tag+'.cue',z['source'],(-1,0,0),start+offset+3,5);arrive('LEARN.'+tag+'.sample',z['source'],(1,0,1),start+offset+3,11)
            if r!=available:send('ENV.'+tag,z['query'],(1,0,0),start+offset+8,3)
            arrive('EXPLORE.'+tag,z['query'],(j,r,0),start+offset+9,5)
            if not(episode and'no_feedback'in a.case):
                E=mv(z['outcome'],(0,0,1),9)if episode and'feedback_sham'in a.case else z['outcome']
                arrive('CONSEQUENCE.'+tag+'.1',E,(0,-r,-1),start+offset+13,7);arrive('CONSEQUENCE.'+tag+'.2',E,(0,-r,0),start+offset+13,7)
    if'no_query'not in a.case:arrive('GENERIC_QUERY',S,(1,0,0),start+157,5)
    if'cut_policy'in a.case or'sham_policy'in a.case:
        for r in(-1,1):
            site=mv(S,(0,r,0),2)
            if'sham_policy'in a.case:site=mv(site,(1,0,0),12)
            send('POLICY_CUT.'+str(r),site,(0,0,0),start+91,0,4)
    # Both pre-existing form addresses are declared regardless of past utility.
    mapping={'1':'menos','-1':'más'};starts={};endpoints={}
    for key,word in mapping.items():
        branch=int(key);signature=words[word]['signature'];starts[key]={'site':mv(S,(1,branch,0),4),'direction':[1,branch,0]}
        direction=[-signature[0],-signature[1],0]if consume else[0,0,signature[2]]
        endpoints[key]={'site':words[word]['hub'],'direction':direction}
    plans=routes_for_common_arrival(starts,endpoints,start+161,phase=6);goal=plans['1']['arrival_tick'];data['fixed_conductors']=plans;data['goal_tick']=goal;data['form_mapping']=mapping;data['existing_form_geometry']=words
    for key,plan in plans.items():
        for index,turn in enumerate(plan['turns']):
            for k,pulse in enumerate(turn['pulses']):
                point=mv(turn['site'],(0,1,0),12)if'relay_sham'in a.case else turn['site']
                arrive('RELAY.'+key+'.'+str(index)+'.'+str(k),point,pulse['direction'],turn['tick'],pulse['payload'])
    if'source_cut'in a.case or'source_sham'in a.case:
        for word,item in words.items():
            site=mv(item['hub'],item['signature'],-4)
            if'source_sham'in a.case:site=mv(site,(0,1,0),12)
            send('SOURCE_CUT.'+word,site,(0,0,0),goal-5,0,4)
    B={}
    if consume:
        for word,item in words.items():
            for z in(-1,1):
                hub=mv(item['hub'],(0,0,z),4);key=word+'.'+str(z);B[key]={'hub':hub,'z':z,'query_tick':goal+71,'effect':mv(hub,(1,1,z),4)}
                arrive('B.ACQUIRE.'+key,hub,(1,0,0),goal+4,5);arrive('B.LATER_QUERY.'+key,hub,(0,1,0),goal+71,7);arrive('B.USE.'+key,B[key]['effect'],(-1,-1,0),goal+75,5)
    data['B_geometry']=B;data['all_future_inputs_scheduled_before_outcome_observation']=True
    moments={start+22,start+23,start+89,start+90,start+156,start+157,start+160,start+161,goal-1,goal,goal+4}
    for plan in plans.values():
        for turn in plan['turns']:moments.update((turn['tick']-1,turn['tick']))
    if consume:moments.update((goal+70,goal+71,goal+75))
    data['samples']=[]
    with gzip.open(a.out/'CAMPOS_ACCESO_CONECTADO.jsonl.gz','xt',encoding='utf8',compresslevel=6)as stream:
        for tick in sorted(moments):
            x.run_until(tick);stream.write(json.dumps(frame(x.world),separators=(',',':'))+'\n')
            sample={'tick':tick,'policy':observe(x.world,S),'physical':physical(x.world)};data['samples'].append(sample)
            if tick in(start+23,start+90):data['policy_witness_'+str(tick-start)]=witness(x.world,S,3)
            if tick==start+90:data['learned_strategy_complete']=x.save(a.out/'ESTRATEGIA_APRENDIDA_Y_COLA_COMPLETA.deetsnap.gz')
            if tick==goal-1:
                data['pre_access']={word:{'native_source':observe(x.world,mv(item['hub'],item['signature'],-1)),'query_source':observe(x.world,mv(item['hub'],endpoints[key]['direction'],-1)),'witness':witness(x.world,item['hub'],3)}for key,word in mapping.items()for item in[words[word]]}
            if tick==goal:data['accessed_forms']={word:observe(x.world,item['hub'])for word,item in words.items()}
            if tick==goal+4:data['B_acquired']={key:observe(x.world,item['hub'])for key,item in B.items()}
            if consume and tick==goal+71:data['B_recalled']={key:observe(x.world,item['hub'])for key,item in B.items()}
            if consume and tick==goal+75:data['B_used']={key:observe(x.world,item['effect'])for key,item in B.items()}
    data['module_end']=physical(x.world,occupation=True)
    data['old_after']={'less':e.context(x,value=64,method='B'),'more':e.context(x,value=117,method='B'),'near':pc.current_dose(x,parameter=3,load=4),'far':pc.current_dose(x,parameter=-3,load=6),'contact':e.contact_query(x,frame='contactoA'),'free':e.contact_query(x,frame='freeRepair5')}
    data['receipts']=receipts(x.world.runtime);data['post']=physical(x.world,occupation=True)
    x.world.runtime.set_snapshot_metadata('DEE.Cognitive.System.1.1.AA01.connected10',encode_metadata({'policy_site':S,'epoch':start,'goal_tick':goal,'prepared_fixed_routes':plans,'consumptive':consume,'query_was_generic':True,'B':B,'not_a_current_magnitude_judgment':True,'no_route_target_in_metadata':True}))
    native_actions={word:row['direction']for word,row in data['accessed_forms'].items()if row['state']==1 and row['semantic']==1 and row['direction']in([0,0,-1],[0,0,1])}
    return{'life':life,'tick':x.tick,'goal':goal,'strategy_samples':[(r['tick'],r['policy']['direction'])for r in data['samples']if r['tick']in(start+23,start+90)],'native_source_actions':native_actions,'B_recall':{key:row['direction']for key,row in data.get('B_recalled',{}).items()if row['state']==1},'B_use':{key:row['direction']for key,row in data.get('B_used',{}).items()if row['state']==1},'old_words':[r.get('SPANISH_DECODED',r.get('TRADUCCION',{}).get('SPANISH_DECODED'))for r in data['old_after'].values()]}
data['commit']=s.mutate(life,'AA01_ACQUIRED_SELECTION_CONNECTED_TO_LIVED_FORMS_10',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
