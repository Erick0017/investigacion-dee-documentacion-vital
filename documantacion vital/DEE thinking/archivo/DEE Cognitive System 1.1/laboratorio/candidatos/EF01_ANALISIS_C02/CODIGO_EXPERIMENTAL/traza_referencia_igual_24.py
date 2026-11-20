"""Second narrowed witness: actual MAIN05 equality protocol, passive tracking."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,observe,moore27
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,igualdad_fisica_03 as f
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='ES01_MAIN_04';life='ES01_REF_TRACE24_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY');reference=s.record('ES01_MAIN_05')['physical']
data={'case':a.case,'life':life,'parent':s.record(parent),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'phases':[],'question':'The exact MAIN04 replay preserved the reference lane. Now identify its first functional direction change in the already recorded equality acquisition/query future. Nothing is transferred back to MAIN.'}
def cap(x,label,row):data['phases'].append({'label':label,'tick':x.tick,'result':row,'physical':physical(x.world,occupation=True)})
def trial(x):
 c=x.quantity.geometry['center'];lane=[observe(x.world,[c[0]-1,y,c[2]])for y in range(67)];sources=[r for r in lane if e.valid(r,(0,1,0))]
 if len(sources)!=1:raise ValueError('Unique starting lane carrier required')
 tracked=sources[0];oldrun=x.run_until;data['tracked_initial']=tracked;data['first_change']=None
 def watched(target):
  nonlocal tracked
  while x.tick<target and data['first_change']is None:
   t=x.tick;site=tracked['site'];destination=e.move(site,tracked['direction']);pre=moore27(x.world,destination);pre_current=moore27(x.world,site);oldrun(t+1);post=observe(x.world,destination)
   if not e.valid(post,(0,1,0)):data['first_change']={'pre_tick':t,'post_tick':x.tick,'tracked_pre':tracked,'expected_destination':destination,'pre_destination_moore':pre,'pre_current_moore':pre_current,'post_destination':post,'post_destination_moore':moore27(x.world,destination),'post_old_position_moore':moore27(x.world,site)}
   else:tracked=post
  oldrun(target)
 x.run_until=watched
 f.prepare(x);cap(x,'actual_equality_and_later_word_teaching',f.present(x,value=86,teacher=True,probe_lead=1))
 for j in range(3):cap(x,'equality_recall_'+str(j),f.query(x))
 for value in(86,56,110,86):cap(x,'current_equality_test_'+str(value),f.context(x,value=value,probe_lead=1))
 for frame in('contactoA','freeRepair5'):cap(x,'previous_'+frame,e.contact_query(x,frame=frame))
 cap(x,'previous_time',e.temporal_query(x,frame='secuenciaA'));cap(x,'previous_comparison_forms',e.query_words(x));cap(x,'equality_after_other_queries',f.query(x));data['post']=physical(x.world,occupation=True)
 data['original_future_equivalence']={k:data['post'][k]==reference[k]for k in('tick','RAW_sha256','clocks_sha256')}
 return {'tick':x.tick,'first_change_tick':None if data['first_change']is None else data['first_change']['post_tick'],'original_future_equivalence':data['original_future_equivalence']}
data['commit']=s.mutate(life,'EF01_DIAGNOSTIC_REPLAY_REFERENCE_CHANGE_EQUALITY24',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result']))
