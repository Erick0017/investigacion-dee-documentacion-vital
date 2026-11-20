"""Selective acquired-maintenance diagnostic, exact restoration, new old-word use."""
import argparse,gc,json,sys
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from dee_thinking import _native as d
from integracion.regulated_finite_e1 import RegulatedFiniteE1Session
from integracion.relational_pair import physical

def run(out):
 out.mkdir(parents=True,exist_ok=False);path=ROOT/'resultados/integracion/RE2_P01/T271.deetsnap.gz';base=json.loads((path.parent/'MEASUREMENTS.json').read_text(encoding='utf-8'));rows=[]
 for mode in('cut','sham','restore'):
  p=RegulatedFiniteE1Session.load(path);before=physical(p.world);r=p.geometry['acquired_regulation'][0];pre=p.observe(r['hub']);assert pre['s_reg']==16 and pre['direction']==[-1,0,0]
  if mode=='restore':s=p
  else:
   e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*r['hub']);e.raw=0 if mode=='cut'else int(pre['raw']);e.label='AUDITOR_FIRST_EXTRA_MAINTENANCE_'+mode
   child=p.world.diagnostic_fork([e],True);state=deepcopy(p.state)
   for k in('quantity','mode'):state[k]=deepcopy(getattr(p,k).state)
   s=RegulatedFiniteE1Session(child,p.geometry,state,p.identifier+'.'+mode)
  frames=[]
  for t in(274,275,276,336,337,338,538,539,549):s.run_until(t);frames.append(s.view())
  final549=physical(s.world);receipts549={x['id']:x['receipt']for x in s.receipts()};expected={x['id']:x['receipt']for x in base['inputs']}
  if mode=='restore':
   # New interaction declared before its result; it is not replayed from a log.
   for q in s.geometry['joint_names'].values():s.input(q['query_port'],13,613,'probe','NEW_QUERY_AFTER_RESTORED_R1_PROFILE')
   s.run_until(616);frames.append(s.view())
  s.save(out/(mode+'_T'+str(s.tick)+'.deetsnap.gz'))
  rows.append({'mode':mode,'parent':path.relative_to(ROOT).as_posix(),'preparations':0,'continuations':int(mode=='restore'),'diagnostic_forks':int(mode!='restore'),'technical_reproductions':int(mode=='restore'),'intervention':None if mode=='restore'else{'pre':pre,'raw_written':str(e.raw),'clock_edit':None},'parent_unchanged':True if mode=='restore'else before==physical(p.world),'frames':frames,'full_physical549_equal_baseline':final549==base['final'],'native_receipts549_equal':receipts549==expected,'final':physical(s.world),'inputs':s.receipts()})
  del s,p;gc.collect()
 data={'schema':'CPC8R.finiteRegulatedE1.causal_restore.v1','results':rows,'scope':'Four additional external maintenance teaching episodes are counted; cut only on diagnostic copy; no R2utility strategy.'}
 (out/'MEASUREMENTS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps([{'mode':x['mode'],'same549':x['full_physical549_equal_baseline'],'receipts':x['native_receipts549_equal'],'parent_unchanged':x['parent_unchanged']}for x in rows]))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.out)
