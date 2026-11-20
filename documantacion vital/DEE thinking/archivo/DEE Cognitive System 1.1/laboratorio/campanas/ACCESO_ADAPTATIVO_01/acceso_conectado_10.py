"""Native two-experience revision of the same moving access-policy support.

Paired successful route outcomes converge on one support. The second pair can
reverse a previously acquired direction without a route teacher, host branch
on results, RAW edits, or content supplied during final common access.
"""
from pathlib import Path
import argparse,sys,json,gzip
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01'))
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from instrumentos_pc01 import guard,receipts,sha,frame,witness
from dee_thinking.persistence import encode_metadata
from capacidades import espanol_funcional_01 as e,paisaje_causal_01 as pc
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);life='AA01_INTEGRADA08_'+a.case;parent='PC01_CONTINUIDAD28_far_guard'if a.case.startswith('e1_')else None
if parent:s.fork(parent,life,kind='CANDIDATE')
else:s.create(life,'fisica_directa',{'N':67})
S=[32,32,49] if 'z17'in a.case else [45,32,32];N=67;distance=10;first_policy=13+distance;second_policy=first_policy+67;final_query=first_policy+134
def mv(q,d,k):return[(q[i]+d[i]*k)%N for i in range(3)]
initial=-1 if'initialdown'in a.case else 1;revised=initial if'sameutility'in a.case else-initial;content=-1 if'minus'in a.case else 1;g={}
for j in(-1,1):
    for r in(-1,1):
        E=mv(mv(S,(j,0,0),-distance),(0,r,0),distance);Q=mv(E,(j,r,1),-4);H=mv(Q,(0,0,1),-6);g[str(j)+','+str(r)]={'j':j,'r':r,'outcome':E,'query':Q,'source':H}
memories={str(p):mv(S,(1,p,0),4)for p in(-1,1)};data={'case':a.case,'life':life,'parent':s.record(parent)if parent else None,'source_sha256':sha(__file__),'geometry':{'policy':S,'training_routes':g,'memories':memories},'external_experiences':{'initial_available_route':initial,'second_available_route':revised,'new_content':content},'criteria_before':'At19two independent native retrieval outcomes produce Y-only strategy at common support. At86same support receives new consequences. Query at153 supplies only +X, equally declared access memories have content acquired at90. NativeYselectswhichmemoryisreached; nativeZ reports content. Negative controls must not be scored by inferred targets. No acquisition provided during final query.','requests':[]}
def trial(x):
    start=x.tick;data['epoch']=start;data['pre']=physical(x.world,occupation=True)
    def send(name,site,d,t,payload=5,sem=1):data['requests'].append(guard(x.world,'AA01.R04.'+name,site,start+t,direction=d,semantic=sem,payload=payload))
    def arrive(name,site,d,t,payload=5):send(name,mv(site,d,-3),d,t-3,payload)
    data['fixed_calendar']={'first_policy':first_policy,'second_policy':second_policy,'final_common_query':final_query,'separation':distance}
    data['prepared_residual_interceptors']=[]
    if '_r2'in a.case:
        for key,z in g.items():
            candidates=[('environment_pulse',mv(z['query'],(1,0,0),6),13),('unqualified_feedback',mv(z['outcome'],(0,-z['r'],-1),4),16)]
            for label,site,tick in candidates:
                actual=mv(site,(0,0,1),12)if'support_sham'in a.case else site
                send('PREPARED_SUPPORT.'+key+'.'+label,actual,(0,0,0),tick,0,4);data['prepared_residual_interceptors'].append({'site':actual,'tick':start+tick,'role':label,'P0_not_selected_by_organism':True})
    for roundno,(epoch,available)in enumerate(((0,initial),(67,revised))):
        if roundno and'no_second'in a.case:continue
        for key,z in g.items():
            r=z['r'];j=z['j'];H=z['source'];Q=z['query'];E=z['outcome'];tag=str(roundno)+'.'+key
            if'no_history'not in a.case:arrive('EXP.'+tag+'.cue',H,(-1,0,0),epoch+3,5);arrive('EXP.'+tag+'.sample',H,(1,0,1),epoch+3,11)
            if r!=available:send('ENV.'+tag,Q,(1,0,0),epoch+8,3)
            arrive('EXPLORE.'+tag,Q,(j,r,0),epoch+9,5)
            if not(roundno and'no_feedback'in a.case):
                E2=mv(E,(0,0,1),9)if roundno and'feedback_sham'in a.case else E
                arrive('CONSEQUENCE.'+tag+'.1',E2,(0,-r,-1),epoch+13,7);arrive('CONSEQUENCE.'+tag+'.2',E2,(0,-r,0),epoch+13,7)
    for p,M in memories.items():arrive('NEW.'+p+'.cue',M,(-1,0,0),final_query+4-67,5);arrive('NEW.'+p+'.event',M,(1,0,content),final_query+4-67,11)
    if'no_final_query'not in a.case:arrive('COMMON_QUERY',S,(1,0,0),final_query,5)
    if'cut_policy'in a.case or'sham_policy'in a.case:
        # Same physical intervention for all histories; not chosen from a read.
        for r in(-1,1):
            where=mv(S,(0,r,0),2)
            if'sham_policy'in a.case:where=mv(where,(1,0,0),12)
            send('CUT.'+str(r),where,(0,0,0),second_policy+1,0,4)
    data['all_inputs_scheduled_before_outcome_reading']=True;data['samples']=[]
    with gzip.open(a.out/'CAMPOS_REVISION.jsonl.gz','xt',encoding='utf8',compresslevel=6)as stream:
        for t in(3,9,13,first_policy-1,first_policy,70,76,80,second_policy-1,second_policy,second_policy+1,final_query+4-67,final_query-1,final_query,final_query+4,final_query+8):
            x.run_until(start+t);stream.write(json.dumps(frame(x.world),separators=(',',':'))+'\n');data['samples'].append({'relative_tick':t,'policy':observe(x.world,S),'physical':physical(x.world)})
            if t in(first_policy-1,first_policy,second_policy-1,second_policy):data['witness_'+str(t)]=witness(x.world,S,3)
            if t==first_policy:data['first_learned_snapshot']=x.save(a.out/'ESTRATEGIA_ANTES_REVISION_COMPLETA.deetsnap.gz')
    outputs=[];data['readouts']={}
    for p,M in memories.items():
        for c in(-1,1):
            site=mv(M,(1,int(p),c),4);row=observe(x.world,site);data['readouts'][p+','+str(c)]=row
            if row['state']==1 and row['semantic']==1 and row['direction'][0]==1 and abs(row['direction'][1])==1 and abs(row['direction'][2])==1:outputs.append({'native_access_branch':row['direction'][1],'content':row['direction'][2],'SPANISH_DECODED':'cerca'if row['direction'][2]>0 else'lejos','record':row})
    data['qualified_outputs']=outputs;data['module_end']=physical(x.world,occupation=True);data['old_after']={'less':e.context(x,value=64,method='B'),'more':e.context(x,value=117,method='B'),'near':pc.current_dose(x,parameter=3,load=4),'far':pc.current_dose(x,parameter=-3,load=6),'contact':e.contact_query(x,frame='contactoA'),'free':e.contact_query(x,frame='freeRepair5')};data['receipts']=receipts(x.world.runtime);data['post']=physical(x.world,occupation=True);data['distance_revision']=distance;data['strategy_times']=[first_policy,second_policy,final_query];x.world.runtime.set_snapshot_metadata('DEE.Cognitive.System.1.1.AA01.strategy04',encode_metadata({'geometry':data['geometry'],'epoch':start,'query':'genericXonly','scope':'Two prepared learning opportunities with native outcome feedback; no global autonomy verdict','metadata_not_a_route_or_content_target':True}));return{'life':life,'tick':x.tick,'strategy_first':data['samples'][4]['policy']['direction'],'strategy_second':data['samples'][9]['policy']['direction'],'outputs':outputs,'old_words':[r.get('SPANISH_DECODED',r.get('TRADUCCION',{}).get('SPANISH_DECODED'))for r in data['old_after'].values()]}
data['commit']=s.mutate(life,'AA01_STRATEGY_REVISION_NATIVE_CONSEQUENCES_04',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
