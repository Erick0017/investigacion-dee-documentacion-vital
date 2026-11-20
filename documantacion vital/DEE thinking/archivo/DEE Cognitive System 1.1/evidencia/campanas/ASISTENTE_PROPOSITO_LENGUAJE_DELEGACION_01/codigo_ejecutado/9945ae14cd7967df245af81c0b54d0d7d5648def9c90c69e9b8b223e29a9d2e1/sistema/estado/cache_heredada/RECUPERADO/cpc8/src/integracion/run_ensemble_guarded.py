"""Explicit preparation adapter plus a fixed third query in the SAME Runtime."""
import argparse,json,shutil,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from integracion import run_ensemble
from integracion.relational_guarded import GuardedEnsembleSession
from integracion.relational_pair import physical,move

def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 case=next(c for c in json.loads(a.config.read_text(encoding='utf8'))['cases']if c['id']==a.case_id);holder={}
 class SelectedGuard(GuardedEnsembleSession):
  @classmethod
  def create(cls,**options):
   s=super().create(guard_mode=case['guard_mode'],**options);holder['session']=s;return s
  def curriculum(self,**options):
   options.pop('guard_mode',None);super().curriculum(**options)
   for q in self.geometry['joint_names'].values():self.input(q['query_port'],9,412,'probe','THIRD_SIGNAL_QUERY_WITHOUT_RETEACHING_FIXED_T0')
 extra_paths=(Path(__file__),ROOT/'src/integracion/relational_guarded.py',ROOT/'src/integracion/relational_social.py',ROOT/'src/comunicacion/mode_communication.py')
 adapter={'factory':'integracion.relational_guarded.GuardedEnsembleSession','guard_mode':case['guard_mode'],'source_sha256':{p.name:run_ensemble.sha(p)for p in extra_paths},'scope':'Explicit T0 preparation parameter; not readout-based target selection'}
 original=run_ensemble.put
 def put(path,value):
  if Path(path).name=='MEASUREMENTS.json':value={**value,'factory_adapter':adapter}
  return original(path,value)
 run_ensemble.EnsembleSession=SelectedGuard;run_ensemble.put=put
 sys.argv=[sys.argv[0],'--config',str(a.config),'--case-id',a.case_id,'--out',str(a.out)];run_ensemble.main()
 # Still the original freshly-created Runtime, not a snapshot reset or new preparation.
 s=holder['session'];m=json.loads((a.out/'MEASUREMENTS.json').read_text(encoding='utf8'));m['status']='RUNNING_CONTINUATION';started=time.monotonic()
 for tick in(363,364,411,412,414,415):
  s.run_until(tick);m['frames'].append(s.view())
  for q in s.geometry['joint_names'].values():m['windows'].append({'tick':tick,'nominal_stage':415,'center':q['delivery_site'],'Moore27':[s.observe(move(q['delivery_site'],(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
  m.update(last_complete_tick=s.tick,requests=s.receipts());put(a.out/'MEASUREMENTS.json',m)
 path=a.out/'T415.deetsnap.gz';storage=s.save(path);m['snapshots'].append({'path':path.name,'tick':415,'sha256':run_ensemble.sha(path),'physical':physical(s.world),'storage':storage});m.update(status='MEASURED',final_physical=physical(s.world),continuation_seconds=time.monotonic()-started,social_captures=s.mode.state.get('social_captures',[]),social_windows=s.state['social_windows'])
 put(a.out/'MEASUREMENTS.json',m)
 for path in extra_paths:shutil.copyfile(path,a.out/'executed_source'/path.name)
 print(json.dumps({'id':case['id'],'guard':s.geometry['residual_guard'],'word415':{k:v['delivery_site']for k,v in m['frames'][-1]['joint'].items()}}),flush=True)
if __name__=='__main__':main()
