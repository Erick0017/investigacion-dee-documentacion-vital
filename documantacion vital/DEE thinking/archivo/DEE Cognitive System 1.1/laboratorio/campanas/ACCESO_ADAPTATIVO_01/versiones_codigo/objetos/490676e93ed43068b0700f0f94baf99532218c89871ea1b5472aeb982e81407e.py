"""Finite native candidate: route use -> material consequence -> later access.

All alternative read opportunities are supplied equally. No Python callback
reads a result to choose a later route. Initial and new contents are experiences.
"""
from pathlib import Path
import argparse,sys,json,gzip
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01'))
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from instrumentos_pc01 import guard,receipts,sha,frame,witness
from dee_thinking.persistence import encode_metadata
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);life='AA01_RUTA02_'+a.case;is_e1=a.case.startswith('e1_');parent='PC01_CONTINUIDAD28_far_guard'if is_e1 else None
if parent:s.fork(parent,life,kind='CANDIDATE')
else:s.create(life,'fisica_directa',{'N':67})
successful=1 if'up'in a.case else-1;old_content=-1 if'oldminus'in a.case else 1;new_content=-1 if'minus'in a.case.removesuffix('oldminus')else 1
origin=(10,22,25);N=67
def mv(q,d,k):return[(q[i]+d[i]*k)%N for i in range(3)]
g={}
for r in(-1,1):
    h=mv(origin,(0,r,0),6)
    for c in(-1,1):
        q=mv(h,(0,0,c),6);out=mv(q,(1,r,c),4);memory=mv(out,(1,r,0),4);g[str(r)+','+str(c)]={'r':r,'c':c,'hub':h,'old_query':q,'outcome_policy':out,'new_memory':memory,'readouts':{str(z):mv(memory,(1,r,z),4)for z in(-1,1)}}
data={'case':a.case,'life':life,'parent':s.record(parent)if parent else None,'source_sha256':sha(__file__),'geometry':g,'teaching_environment':{'initial_content':old_content,'new_content':new_content,'successful_training_route':successful,'route_content_not_supplied_at_evaluation':True},'design_before':'Fixed4genericqueryopportunities, symmetric readers and feedback resources. Training has one physically blocked alternative; a successful native retrieval reaches a material feedback encounter. Its directional state can later combine with a common query to access newly taught contents. Future inputs are queued before outcomes are observed. Finite acquired-access candidate, not a global P2 verdict.','requests':[]}
def trial(x):
    data['pre']=physical(x.world,occupation=True);start=x.tick;data['epoch']=start
    def send(name,site,d,t,payload=5,semantic=1):
        req=guard(x.world,'AA01.R02.'+name,site,start+t,direction=d,semantic=semantic,payload=payload);data['requests'].append(req)
    def arrive(name,site,d,t,payload=5):send(name,mv(site,d,-3),d,t-3,payload)
    for r in(-1,1):
        h=g[str(r)+',1']['hub']
        if'no_history'not in a.case:
            arrive('LEARN.'+str(r)+'.cue',h,(-1,0,0),3,5);arrive('LEARN.'+str(r)+'.event',h,(1,0,old_content),3,11)
    for key,z in g.items():
        r=z['r'];c=z['c'];q=z['old_query'];out=z['outcome_policy'];memory=z['new_memory']
        if r!=successful:send('ENV.BLOCK.'+key,q,(0,0,0),5,0,4)
        arrive('EXPLORE.'+key,q,(1,r,0),9,5)
        if'no_feedback'not in a.case:
            site=mv(out,(0,0,1),9)if'feedback_sham'in a.case else out
            arrive('FEEDBACK.'+key,site,(-1,0,-c),13,7)
        if'no_current'not in a.case:
            arrive('NEW.'+key+'.cue',memory,(-1,0,0),17,5);arrive('NEW.'+key+'.event',memory,(1,0,new_content),17,11)
        if'cut_policy'in a.case or'sham_policy'in a.case:
            where=mv(out,(0,r,0),3)
            if'sham_policy'in a.case:where=mv(where,(1,0,0),9)
            send('POLICY_CUT.'+key,where,(0,0,0),15,0,4)
        if'no_query'not in a.case:arrive('COMMON.'+key,out,(1,0,0),80,5)
    data['future_input_schedule_complete_before_outcomes']=True;data['samples']=[]
    with gzip.open(a.out/'CAMPOS_SELECCION.jsonl.gz','xt',encoding='utf8',compresslevel=6)as stream:
        for t in(3,9,13,17,79,80,83,84,88):
            x.run_until(start+t);stream.write(json.dumps(frame(x.world),separators=(',',':'))+'\n');data['samples'].append({'relative_tick':t,'physical':physical(x.world),'sites':{key:{'policy':observe(x.world,z['outcome_policy']),'memory':observe(x.world,z['new_memory'])}for key,z in g.items()}})
            if t==13:data['feedback_witness']={key:witness(x.world,z['outcome_policy'],3)for key,z in g.items()}
    data['readouts']={key:{c:observe(x.world,site)for c,site in z['readouts'].items()}for key,z in g.items()};qualified=[]
    for key,reads in data['readouts'].items():
        for c,row in reads.items():
            if row['state']==1 and row['semantic']==1 and row['direction'][0]==1 and abs(row['direction'][1])==1 and abs(row['direction'][2])==1:qualified.append({'site_key':key,'observer_c_index':c,'native_route':row['direction'][1],'native_content':row['direction'][2],'SPANISH_DECODED':'cerca'if row['direction'][2]>0 else'lejos','raw':row['raw']})
    data['qualified_outputs']=qualified;data['receipts']=receipts(x.world.runtime);data['post']=physical(x.world,occupation=True);x.world.runtime.set_snapshot_metadata('DEE.Cognitive.System.1.1.AA01.route02',encode_metadata({'geometry':g,'epoch':start,'prepared_opportunities':True,'outcome_selection_claim':'Pending causal contrasts, not a stored answer map','readout':'state1SEM1X1absY1absZ1; YrouteZcontent','training_targets_not_used_by_participant':True}));return{'life':life,'tick':x.tick,'outputs':qualified}
data['commit']=s.mutate(life,'AA01_ROUTE_CONSEQUENCE_CANDIDATE_02',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
