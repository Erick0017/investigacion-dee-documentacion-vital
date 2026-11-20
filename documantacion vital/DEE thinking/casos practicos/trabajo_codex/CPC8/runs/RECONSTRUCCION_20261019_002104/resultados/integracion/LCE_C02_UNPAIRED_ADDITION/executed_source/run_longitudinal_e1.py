"""Fresh confirmed-candidate trajectories; exact source and primary observations."""
import argparse,hashlib,json,os,shutil,sys,time,traceback
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from integracion.longitudinal_e1 import LongitudinalE1Session
from integracion.relational_pair import physical,move
import dee_thinking as dee
from dee_thinking import _native as d
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 t=p.with_name(p.name+'.pending');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8');os.replace(t,p)
def main():
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf8')
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 cfg=json.loads(a.config.read_text(encoding='utf8'));case=next(c for c in cfg['cases']if c['id']==a.case_id);a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 if dee.__version__!='4.5.0'or not Path(dee.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):raise RuntimeError('Official isolated4.5 required')
 paths=[Path(__file__)]+[ROOT/'src/integracion'/n for n in('longitudinal_e1.py','complete_e1.py','quantity_core.py','relational_guarded_v2.py','relational_social.py','relational_ensemble.py','relational_pair_v2.py','relational_pair.py')]+[ROOT/'src/comunicacion/mode_communication.py',ROOT/'src/relaciones/mode_reference.py'];src=a.out/'executed_source';src.mkdir()
 for path in paths:shutil.copyfile(path,src/path.name)
 prepkeys=('guard_mode','actor_mode','include_order','include_contact','event_state_offset','medium_load','actor_state','quantity_guards');prep={k:case[k]for k in prepkeys if k in case};s=LongitudinalE1Session.create(identifier=case['id'],**prep)
 m={'schema':'CPC8R.longitudinalE1.measurements.v1','case':case,'configuration_sha256':sha(a.config),'source_sha256':{x.name:sha(x)for x in paths},'engine':{'version':dee.__version__,'module':dee.__file__,'native_sha256':sha(d.__file__),'python':sys.executable},'geometry':s.geometry,'preparations':1,'continuations':0,'diagnostic_forks':0,'host_RAW_clock_edits_on_MAIN':[],'frames':[],'windows':[],'snapshots':[],'status':'RUNNING','predictions_recorded_before_targets':cfg['predeclared_decoders']}
 def save(tick):
  path=a.out/('T'+str(tick)+'.deetsnap.gz');storage=s.save(path);m['snapshots'].append({'path':path.name,'tick':tick,'sha256':sha(path),'physical':physical(s.world),'storage':storage})
 def checkpoint():m.update(last_complete_tick=s.tick,requests=sorted(s.receipts(),key=lambda r:r['id']),elapsed_seconds=time.monotonic()-start);put(a.out/'MEASUREMENTS.json',m)
 try:
  s.curriculum(**{k:v for k,v in case.items()if k not in('id','guard_mode','actor_mode','event_state_offset','medium_load','actor_state','quantity_guards')});save(0);checkpoint()
  g=s.geometry;windows={3:[g['mode']['reference_hub']],5:[g['body']['emission'],g['contact_base'],g['contact_join']],9:[q['hub']for q in g['contact'].values()],11:[q['hub']for q in g['order'].values()],31:[q['query_site']for q in g['order'].values()],76:[q['query_site']for q in g['contact'].values()],143:[q['renewed_site']for q in g['contact'].values()],165:[q['query_site']for q in g['order'].values()],170:[g['auxiliary_hub']],206:[g['common_join']],210:[q['use_site']for q in g['joint_names'].values()],214:[q['delivery_site']for q in g['joint_names'].values()],224:g['residual_guard']['sites']}
  for tick in(70,137,204,271,338,405,472,539):windows.setdefault(tick,[]).append(g['quantity']['center'])
  for tick in(281,348,415,549):windows.setdefault(tick,[]).extend(q['delivery_site']for q in g['joint_names'].values())
  for q in g['mode']['queries']:windows.setdefault(q['parent']['query_tick'],[]).append(q['parent']['hub'])
  for q in g['mode']['communication']['receivers']:
   windows.setdefault(160,[]).append(q['memory_site']);windows.setdefault(227,[]).append(q['memory_site']);windows.setdefault(232,[]).append(q['context_site']);windows.setdefault(235,[]).extend(x['site']for x in q['deliveries'].values())
  boundaries={99,100,109,110,267,268}
  for tick in windows:boundaries.update((tick-1,tick))
  for tick in sorted(boundaries):
   s.run_until(tick);m['frames'].append(s.view())
   for target,centers in windows.items():
    if tick in(target-1,target):
     for q in centers:m['windows'].append({'tick':tick,'nominal_stage':target,'center':q,'Moore27':[s.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
   if tick in(11,170,214,271,348,415,539,549):save(tick)
   checkpoint()
  m.update(status='MEASURED',final_physical=physical(s.world),receipt_statuses=dict(Counter(r['receipt']['status']for r in s.receipts())),mode_captures=s.mode.state['captures'],social_captures=s.mode.state.get('social_captures',[]),social_windows=s.state['social_windows'],quantity_observations=s.quantity.state['observations'])
 except BaseException as error:m.update(status='TECHNICAL_ERROR',error_type=type(error).__name__,error=str(error),traceback=traceback.format_exc());raise
 finally:checkpoint()
 print(json.dumps({'id':case['id'],'status':m['status'],'receipts':m.get('receipt_statuses'),'quantity':[(x['tick'],x['center']['direction'],x['center']['active'])for x in m.get('quantity_observations',[])if x['tick']in(70,137,204,338,405,472,539)],'word549':{k:v['delivery_site']for k,v in m['frames'][-1]['joint'].items()},'seconds':m['elapsed_seconds']}),flush=True)
if __name__=='__main__':main()
