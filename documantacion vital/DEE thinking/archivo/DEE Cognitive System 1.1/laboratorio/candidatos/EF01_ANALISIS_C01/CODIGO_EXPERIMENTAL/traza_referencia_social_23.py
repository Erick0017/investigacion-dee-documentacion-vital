"""Instrument an exact diagnostic replay only to localize a reference change.

This is not a new independent sample or a future returned to MAIN.
"""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,observe,moore27
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='ES01_MAIN_03';life='ES01_REF_TRACE23_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY');reference=s.record('ES01_MAIN_04')['physical']
data={'case':a.case,'life':life,'parent':s.record(parent),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'phases':[],
 'question':'Localize the first departure of the physically tracked Y reference during the already recorded MAIN04 social protocol. Exact finalRAW/clocks equivalence is required before using this as a witness of that original future. It is a diagnostic replay, not new acquired knowledge.'}
def cap(x,label,row):data['phases'].append({'label':label,'tick':x.tick,'result':row,'physical':physical(x.world,occupation=True)})
def trial(x):
 c=x.quantity.geometry['center'];lane=[observe(x.world,[c[0]-1,y,c[2]])for y in range(67)];sources=[r for r in lane if e.valid(r,(0,1,0))]
 if len(sources)!=1:raise ValueError('Unique physical starting lane carrier required; do not infer ancestry from equal load')
 tracked=sources[0];oldrun=x.run_until;data['tracked_initial']=tracked;data['first_change']=None;data['trace_ticks_before_change']=0
 def observed_run(target):
  nonlocal tracked
  while x.tick<target and data['first_change']is None:
   t=x.tick;site=tracked['site'];destination=e.move(site,tracked['direction']);pre=moore27(x.world,destination);oldrun(t+1);post=observe(x.world,destination);data['trace_ticks_before_change']+=1
   if not e.valid(post,(0,1,0)):
    data['first_change']={'pre_tick':t,'post_tick':x.tick,'tracked_pre':tracked,'expected_destination':destination,'pre_destination_moore':pre,'post_destination':post,'post_destination_moore':moore27(x.world,destination),'post_old_position_moore':moore27(x.world,site)}
   else:tracked=post
  oldrun(target)
 x.run_until=observed_run
 for source,com in(('contactoA','socialToca'),('freeRepair5','socialFree')):
  cap(x,'transmit_'+com,e.contact_social(x,source_frame=source,communication=com,distance=7));cap(x,'original_source_after_'+com,e.contact_query(x,frame=source))
 for com in('socialToca','socialFree'):cap(x,'return_reuse_'+com,e.contact_social_query(x,communication=com))
 for value in(66,108):cap(x,'new_current_context_'+str(value),e.context(x,value=value,method='B'))
 for source in('contactoA','freeRepair5'):cap(x,'original_relation_retention_'+source,e.contact_query(x,frame=source))
 cap(x,'time_retention',e.temporal_query(x,frame='secuenciaA'));cap(x,'comparison_forms',e.query_words(x));data['post']=physical(x.world,occupation=True)
 data['original_future_equivalence']={k:data['post'][k]==reference[k]for k in('tick','RAW_sha256','clocks_sha256')}
 return {'tick':x.tick,'first_change_tick':None if data['first_change']is None else data['first_change']['post_tick'],'original_future_equivalence':data['original_future_equivalence']}
data['commit']=s.mutate(life,'EF01_DIAGNOSTIC_REPLAY_FIRST_REFERENCE_LANE_CHANGE23',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result']))
