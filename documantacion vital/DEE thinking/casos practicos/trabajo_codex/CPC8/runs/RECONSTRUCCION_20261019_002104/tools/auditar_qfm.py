"""Causal memory/access check, exact continuation and recalculable QFM audit."""
import argparse,gc,json,sys
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from dee_thinking import _native as d
from cantidad_forma_movil import MobileNamedQuantitySession
from cantidad_forma import NamedQuantitySession
from cantidad_renovable import physical,move

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def run(out):
 out.mkdir(parents=True,exist_ok=False);rows=[];primary=ROOT/'resultados/cantidad/QFM_P01';base=read(primary/'MEASUREMENTS.json')
 a=NamedQuantitySession.load(ROOT/'resultados/cantidad/QF_P01/T140.deetsnap.gz');a140=physical(a.world);a.run_until(207);old207=[{'sign':b['sign'],'z_planes':[a.observe(move(b['normalized_bank'],(0,0,1),z))for z in range(3)]}for b in a.geometry['form_banks']];del a;gc.collect()
 b=MobileNamedQuantitySession.load(primary/'T140.deetsnap.gz');new140=physical(b.world);del b;gc.collect()
 for mode in('cut','sham','restore'):
  p=MobileNamedQuantitySession.load(primary/('T139.deetsnap.gz'if mode!='restore'else'T140.deetsnap.gz'));before=physical(p.world);edits=[];interventions=[]
  if mode=='restore':s=p
  else:
   for b in p.geometry['form_banks']:
    q=move(b['normalized_bank'],(0,-1,0));o=p.observe(q);e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*q);e.raw=0 if mode=='cut'else int(o['raw']);e.label='AUDITOR_QFM_ACQUIRED_MOVING_MEMORY_'+mode;edits.append(e);interventions.append({'pre':o,'requested_raw':str(e.raw),'clock_edit':None})
   child=p.world.diagnostic_fork(edits,True);s=MobileNamedQuantitySession(child,p.geometry,deepcopy(p.state))
  traces=[]
  for t in(139,140,141,206,207,208,273,274,276):
   if t<s.tick:continue
   s.run_until(t);traces.append({'tick':t,'banks':[{'sign':b['sign'],'planes':[s.observe(move(b['normalized_bank'],(0,0,1),z))for z in range(4)],'initial_query_Moore27':[s.observe(move(b['normalized_bank'],(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]}for b in s.geometry['form_banks']],'independent_auxiliary':s.observe(s.geometry['auxiliary_hub'])})
  s.save(out/(mode+'_T276.deetsnap.gz'));rows.append({'mode':mode,'preparations':0,'diagnostic_forks':int(mode!='restore'),'continuations':int(mode=='restore'),'technical_reproductions':int(mode=='restore'),'interventions':interventions,'observations':traces,'inputs':s.receipts(),'parent_unchanged':True if mode=='restore'else physical(p.world)==before,'full_physical276_equal_reference':physical(s.world)==base['final'],'native_receipts_equal_reference':{x['id']:x['receipt']for x in s.receipts()}=={x['id']:x['receipt']for x in base['inputs']},'final':physical(s.world)});del s,p;gc.collect()
 cases=[]
 for name in('QFM_P01','QFM_H01','QFM_N01','QFM_C01','QFM_R01'):
  m=read(ROOT/'resultados/cantidad'/name/'MEASUREMENTS.json');cases.append({'case_id':name,'source':'resultados/cantidad/'+name+'/MEASUREMENTS.json','configuration':m['configuration'],'word_trials':m['word_calculations'],'word_correct_count':sum(x['correct']for x in m['word_calculations']),'denominator':3,'quantity_current_readings':[{'tick':x['tick'],'center':x['center'],'pre_operands':next(y for y in m['observations']if y['tick']==x['tick']-1)}for x in m['observations']if x['tick']in(70,137,204)]})
 result={'schema':'CPC8R.quantity.remote_word_audit.v1','original_and_new_full_physical140_equal':a140==new140,'original_query207_actual_support_planes':old207,'cases':cases,'diagnostic_and_restore':rows,'rule':'Native renewed normalization changes direction but retains an actual Zdisplacement. New readers follow the declared geometric support, never select bank from observed class.','scope':'Three qualified later cue reads of a particular acquired comparison association; the comparison operation is prepared. This is a complementary world, not automatically in E1 or proof of general MORE semantics. Other quantity capabilities must be scored separately; preserving a word does not prove all later operands remain intact.'}
 (out/'MEASUREMENTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(ROOT/'revision/CANTIDAD_FORMA_Y_ACCESO.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'same140':a140==new140,'words':[{'id':x['case_id'],'correct':x['word_correct_count']}for x in cases],'forks':[{'mode':x['mode'],'parent_unchanged':x['parent_unchanged'],'full276':x['full_physical276_equal_reference']}for x in rows]}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.out)
