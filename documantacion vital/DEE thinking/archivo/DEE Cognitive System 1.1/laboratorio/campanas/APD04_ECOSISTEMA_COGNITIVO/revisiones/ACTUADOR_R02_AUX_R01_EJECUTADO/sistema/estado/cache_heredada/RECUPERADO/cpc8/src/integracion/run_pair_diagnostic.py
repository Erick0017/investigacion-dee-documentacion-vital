"""Laboratory-only selective arriving-stream intervention, no return to MAIN."""
import argparse,hashlib,json,os,shutil,sys,time
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from integracion.relational_pair import physical,move
from integracion.relational_pair_v2 import PairV2
from dee_thinking import _native as d

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 t=p.with_name(p.name+'.pending');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8');os.replace(t,p)
def main():
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf8')
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 cfg=json.loads(a.config.read_text(encoding='utf8'));case=next(c for c in cfg['cases']if c['id']==a.case_id);a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 source=a.out/'executed_source';source.mkdir()
 paths=[Path(__file__),ROOT/'src/integracion/relational_pair.py',ROOT/'src/integracion/relational_pair_v2.py']
 for path in paths:shutil.copyfile(path,source/path.name)
 parent_path=ROOT/cfg['parent'];parent_sha=sha(parent_path);parent=PairV2.load(parent_path);parent.run_until(cfg['fork_tick']);before=physical(parent.world)
 candidates=cfg['fixed_candidate_sites'];groups=list(candidates)if case['mode']=='sham'else[case['mode'].removesuffix('_cut')]
 edits=[];rows=[]
 for group in groups:
  for q in candidates[group]:
   pre=parent.observe(q);e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*q);e.raw=int(pre['raw'])if case['mode']=='sham'else 0;e.label='Fixed candidate '+group+' '+case['mode'];edits.append(e)
   rows.append({'role':group,'site':q,'pre':pre,'requested_raw':str(e.raw),'clock_edit':None})
 child=parent.world.diagnostic_fork(edits,True);s=PairV2(child,parent.geometry,deepcopy(parent.state),parent.identifier+'.'+case['id'])
 for row in rows:row['post']=s.observe(row['site'])
 m={'schema':'CPC8R.relational_pair.diagnostic.v1','case':case,'configuration_sha256':sha(a.config),'source_sha256':{x.name:sha(x)for x in paths},'parent':{'snapshot':cfg['parent'],'sha256':parent_sha,'saved_tick':170,'fork_tick':cfg['fork_tick']},'preparations':0,'continuations':0,'diagnostic_forks':1,'edited_sites':rows,'parent_physical_before':before,'fork_physical':physical(s.world),'new_inputs_after_fork':[],'frames':[],'windows':[],'snapshots':[],'status':'RUNNING'}
 def save(tick):
  path=a.out/('T'+str(tick)+'.deetsnap.gz');proof=s.save(path);m['snapshots'].append({'path':path.name,'tick':tick,'sha256':sha(path),'physical':physical(s.world),'storage':proof})
 def checkpoint():m.update(last_complete_tick=s.tick,elapsed_seconds=time.monotonic()-start,requests=s.receipts());put(a.out/'MEASUREMENTS.json',m)
 save(205);checkpoint()
 for tick in(205,206,209,210,213,214,280,281):
  s.run_until(tick);m['frames'].append(s.view())
  centers=[s.geometry['common_join']]if tick in(205,206)else[p['use_site'if tick in(209,210)else'delivery_site']for p in s.geometry['joint_names'].values()]
  for q in centers:m['windows'].append({'tick':tick,'center':q,'Moore27':[s.observe(move(q,(dx,dy,dz)))for dx in(-1,0,1)for dy in(-1,0,1)for dz in(-1,0,1)]})
  if tick in(206,281):save(tick)
  checkpoint()
 baseline=json.loads((ROOT/'resultados/integracion/P2_P01_AB_CONTACT/MEASUREMENTS.json').read_text(encoding='utf8'))
 m.update(status='MEASURED',final_physical=physical(s.world),parent_physical_after=physical(parent.world),parent_snapshot_after_sha256=sha(parent_path))
 m['parent_unchanged']=m['parent_physical_before']==m['parent_physical_after']and parent_sha==m['parent_snapshot_after_sha256']
 m['baseline_comparison']={'final_physical_equal':m['final_physical']==baseline['final_physical'],'receipts_equal':m['requests']==baseline['requests'],'scope':'Physical/operational equality; snapshot wrapper provenance intentionally differs. No return to MAIN.'}
 checkpoint();print(json.dumps({'id':case['id'],'parent_unchanged':m['parent_unchanged'],'join206':m['frames'][1]['common_join'],'baseline_comparison':m['baseline_comparison']}),flush=True)
if __name__=='__main__':main()
