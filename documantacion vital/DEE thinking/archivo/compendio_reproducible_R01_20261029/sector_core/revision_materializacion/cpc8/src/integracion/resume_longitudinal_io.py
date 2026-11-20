"""Technical restoration from saved170; old failed measurements remain untouched."""
import argparse,json,shutil,sys,time
from copy import deepcopy
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from integracion.longitudinal_e1 import LongitudinalE1Session
from integracion.relational_pair import physical,move
from integracion.run_longitudinal_e1 import sha,put
def main():
 p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 original_path=a.parent/'MEASUREMENTS.json';old=json.loads(original_path.read_text(encoding='utf8'));snapshot=a.parent/'T170.deetsnap.gz';s=LongitudinalE1Session.load(snapshot)
 if s.tick!=170 or old['status']!='TECHNICAL_ERROR':raise ValueError('Expected saved170 and preserved interrupted attempt')
 expected={f['tick']:f for f in old['frames']if f['tick']>170};m=deepcopy(old);m.update(schema='CPC8R.longitudinalE1.technical_resume.v1',status='RUNNING',preparations=0,continuations=1,technical_reproductions=1,parent={'path':str(snapshot.relative_to(ROOT)),'sha256':sha(snapshot),'tick':170},interrupted_attempt={'primary':str(original_path.relative_to(ROOT)),'sha256':sha(original_path),'status':old['status'],'error_type':old.get('error_type'),'error':old.get('error'),'original_source_sha256':old['source_sha256']},replayed_frame_checks=[],frames=[f for f in old['frames']if f['tick']<=170],windows=[w for w in old['windows']if w['tick']<=170],inherited_snapshots=[{**x,'path':str((a.parent/x['path']).relative_to(ROOT))}for x in old['snapshots']],snapshots=[])
 for key in('error','error_type','traceback','final_physical'):m.pop(key,None)
 paths=[Path(__file__)]+[ROOT/'src/integracion'/n for n in('run_longitudinal_e1.py','longitudinal_e1.py','complete_e1.py','quantity_core.py','relational_guarded_v2.py','relational_social.py','relational_ensemble.py','relational_pair_v2.py','relational_pair.py')]+[ROOT/'src/comunicacion/mode_communication.py',ROOT/'src/relaciones/mode_reference.py'];src=a.out/'executed_source';src.mkdir()
 for path in paths:shutil.copyfile(path,src/path.name)
 m['source_sha256']={x.name:sha(x)for x in paths}
 g=s.geometry;windows={3:[g['mode']['reference_hub']],5:[g['body']['emission'],g['contact_base'],g['contact_join']],9:[q['hub']for q in g['contact'].values()],11:[q['hub']for q in g['order'].values()],31:[q['query_site']for q in g['order'].values()],76:[q['query_site']for q in g['contact'].values()],143:[q['renewed_site']for q in g['contact'].values()],165:[q['query_site']for q in g['order'].values()],170:[g['auxiliary_hub']],206:[g['common_join']],210:[q['use_site']for q in g['joint_names'].values()],214:[q['delivery_site']for q in g['joint_names'].values()],224:g['residual_guard']['sites']}
 for tick in(70,137,204,271,338,405,472,539):windows.setdefault(tick,[]).append(g['quantity']['center'])
 for tick in(281,348,415,549):windows.setdefault(tick,[]).extend(q['delivery_site']for q in g['joint_names'].values())
 for q in g['mode']['queries']:windows.setdefault(q['parent']['query_tick'],[]).append(q['parent']['hub'])
 for q in g['mode']['communication']['receivers']:
  windows.setdefault(160,[]).append(q['memory_site']);windows.setdefault(227,[]).append(q['memory_site']);windows.setdefault(232,[]).append(q['context_site']);windows.setdefault(235,[]).extend(x['site']for x in q['deliveries'].values())
 boundaries={99,100,109,110,267,268}
 for tick in windows:boundaries.update((tick-1,tick))
 for tick in sorted(t for t in boundaries if t>170):
  s.run_until(tick);frame=s.view();m['frames'].append(frame)
  if tick in expected:
   equal=frame==expected[tick];m['replayed_frame_checks'].append({'tick':tick,'exact_view_equal':equal})
   if not equal:raise RuntimeError('Technical replay differs at tick '+str(tick))
  for target,centers in windows.items():
   if tick in(target-1,target):
    for q in centers:m['windows'].append({'tick':tick,'nominal_stage':target,'center':q,'Moore27':[s.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
  if tick in(214,271,348,415,539,549):
   path=a.out/('T'+str(tick)+'.deetsnap.gz');storage=s.save(path);m['snapshots'].append({'path':path.name,'tick':tick,'sha256':sha(path),'physical':physical(s.world),'storage':storage})
  m.update(last_complete_tick=s.tick,requests=sorted(s.receipts(),key=lambda r:r['id']),elapsed_seconds=time.monotonic()-start);put(a.out/'MEASUREMENTS.json',m)
 m.update(status='MEASURED',final_physical=physical(s.world),receipt_statuses=dict(Counter(r['receipt']['status']for r in s.receipts())),mode_captures=s.mode.state['captures'],social_captures=s.mode.state.get('social_captures',[]),social_windows=s.state['social_windows'],quantity_observations=s.quantity.state['observations'],parent_file_unchanged=sha(snapshot)==m['parent']['sha256'],interrupted_primary_unchanged=sha(original_path)==m['interrupted_attempt']['sha256']);put(a.out/'MEASUREMENTS.json',m)
 print(json.dumps({'id':m['case']['id'],'technical_resume':True,'checked':m['replayed_frame_checks'],'status':m['status']}),flush=True)
if __name__=='__main__':main()
