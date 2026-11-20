"""Narrow native diagnostic replay of the S158 antecedent, not EF01 rerun.

Reuses the exact two historical teaching/event protocols, but monitors only
the candidate orbit and its actual incoming local contributors each step.
The candidate coordinate projection is NOT itself called a lineage.
"""
from pathlib import Path
import argparse,gzip,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f,igualdad_fisica_03 as eq
from instrumentos_pc01 import witness,frame,receipts,sha
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='ES01_MAIN_05'if a.case=='early'else'ES01_LEXICAL5_source_guards_strict';life='PC01_INFLUENCIA04_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'question':'Determine birth and useful context of the orbit that later carriedS158 toT22457. Fixed projection from the already traced last138steps is only a search hypothesis; each new ancestry edge must match native empty-target transport/reduction, and all occupied-target contexts remain explicit.','events':[],'changes':[],'global_samples':[]}
def q(t):
    dt=22456-t;return[(38+dt)%67,(58-dt)%67,(16-dt)%67]
def cap(x,label,row):data['events'].append({'label':label,'tick':x.tick,'result':row})
def trial(x):
    oldrun=x.run_until;path=a.out/'RUTA_CANDIDATA.jsonl.gz';stream=gzip.open(path,'wt',encoding='utf8',compresslevel=6);counts={};chain=0;longest=0;prev_raw=None
    def watched(target):
        nonlocal chain,longest,prev_raw
        while x.tick<target:
            t=x.tick;here=q(t);dest=q(t+1);source=observe(x.world,here);center=observe(x.world,dest);nbs=[observe(x.world,[(dest[0]+i)%67,(dest[1]+j)%67,(dest[2]+k)%67])for i in(-1,0,1)for j in(-1,0,1)for k in(-1,0,1)]
            incoming=[r for r in nbs if any(r['direction'])and all(abs(z)<=1 for z in r['direction'])and e.move(r['site'],r['direction'])==dest]
            unusual=center['state']>0 or len(incoming)>1;pre=witness(x.world,dest,3)if unusual else None
            oldrun(t+1);post=observe(x.world,dest)
            sums=[sum(r['direction'][j]for r in incoming)for j in range(3)];expected=incoming[0]['direction']if len(incoming)==1 else[(u>0)-(u<0)for u in sums];load=min(19664,sum(r['s_reg']for r in incoming));exact=center['state']==0 and bool(incoming)and e.valid(post,expected)and post['s_reg']==load
            edge='EXACT_EMPTY_TRANSPORT'if exact and len(incoming)==1 else'EXACT_MULTIPARENT_REDUCER'if exact else'OCCUPIED_CONTEXT'if center['state']else'NO_EXACT_EMPTY_EDGE'
            counts[edge]=counts.get(edge,0)+1
            if exact:chain+=1;longest=max(longest,chain)
            else:chain=0
            row={'pre_tick':t,'post_tick':x.tick,'source_candidate':source,'destination':dest,'destination_pre':center,'incoming_sources':incoming,'post':post,'edge':edge,'crossings_candidate':[(1 if here[j]-1>=67 else-1 if here[j]-1<0 else 0)if j==0 else(1 if here[j]+1>=67 else 0)for j in range(3)]}
            stream.write(json.dumps(row,separators=(',',':'))+'\n')
            signature=(post['raw'],tuple(post['direction']))
            changed=(post['s_reg']!=source['s_reg']or post['direction']!=source['direction']or bool(post['raw']!='0')!=bool(source['raw']!='0'))
            if unusual or changed:
                data['changes'].append({'route_step':row,'pre_radius3':pre,'post_radius3':witness(x.world,dest,3),'note':'Ifpre_radius3isnull, no pre-tick unusual candidate was detected. Full input protocol and checkpoint remain available.'})
            if x.tick%67==0:data['global_samples'].append(frame(x.world))
        return None
    x.run_until=watched
    if a.case=='early':
        f.prepare(x,frame='lexical05',mode='relative_path',origin=(38,50,8),guarded=True,renew_sources=True)
        cap(x,'teach_near3',f.teach(x,frame='lexical05',parameter=3,word='cerca',phase_shift=0));cap(x,'first_near_recall',f.query(x,frame='lexical05'));cap(x,'teach_far3_phase4',f.teach(x,frame='lexical05',parameter=-3,word='lejos',phase_shift=4));cap(x,'both_recall',f.query(x,frame='lexical05'))
        for j,(k,load)in enumerate(((-3,5),(3,3),(-3,3),(3,5),(5,3),(-5,3))):cap(x,'current_'+str(j),f.context(x,frame='lexical05',parameter=k,load=load,decoder='strict'))
        cap(x,'retention',f.query(x,frame='lexical05'));cap(x,'old_words',e.query_words(x));cap(x,'old_contact',e.contact_query(x,frame='contactoA'));cap(x,'old_free',e.contact_query(x,frame='freeRepair5'));expected='ES01_LEXICAL5_source_guards_strict'
    elif a.case=='long':
        x.run_until(e.tick_at_or_after(x.tick,phase=13,lead=4));cap(x,'teach_near5',f.teach(x,frame='lexical05',parameter=5,word='cerca',phase_shift=0));cap(x,'teach_far5',f.teach(x,frame='lexical05',parameter=-5,word='lejos',phase_shift=4));cap(x,'four_recall',f.query(x,frame='lexical05'));first=e.tick_at_or_after(x.tick,phase=13,lead=4)
        sequence=[(3,5),(-5,3),(-3,5),(5,3),(3,3),(-3,3),(-5,5),(5,5),(-3,3),(3,5),(5,3),(-5,3),(5,5),(-3,5),(3,3),(-5,5),(-3,3),(5,3),(-5,3),(3,5),(5,5),(3,3),(-3,5),(-5,3)]
        for j,(k,load)in enumerate(sequence):
            boundary=first+402*j;x.run_until(boundary);cap(x,'episode_'+str(j+1),f.context(x,frame='lexical05',parameter=k,load=load,decoder='strict',emit_word_queries=False));x.run_until(boundary+401)
        cap(x,'final_words',f.query(x,frame='lexical05'));cap(x,'prior_comparison',e.query_words(x));cap(x,'prior_contact',e.contact_query(x,frame='contactoA'));cap(x,'prior_free',e.contact_query(x,frame='freeRepair5'));cap(x,'prior_time',e.temporal_query(x,frame='secuenciaA'));cap(x,'prior_equal',eq.query(x));expected='ES01_LONG7_D_no_material_queries'
    else:raise ValueError('Known early/long coverage only')
    x.run_until=oldrun;stream.close();data['path']={'file':path.name,'sha256':sha(path),'edge_counts':counts,'longest_exact_empty_chain':longest};data['post']=physical(x.world,occupation=True);ref=s.record(expected)['physical'];data['historical_equivalence']={k:data['post'][k]==ref[k]for k in('tick','RAW_sha256','clocks_sha256')};data['receipts']=receipts(x.world.runtime)
    return{'tick':x.tick,'changes':len(data['changes']),'edges':counts,'equivalence':data['historical_equivalence']}
data['commit']=s.mutate(life,'PC01_OLDER_INFLUENCE_PROVENANCE04',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result']))
