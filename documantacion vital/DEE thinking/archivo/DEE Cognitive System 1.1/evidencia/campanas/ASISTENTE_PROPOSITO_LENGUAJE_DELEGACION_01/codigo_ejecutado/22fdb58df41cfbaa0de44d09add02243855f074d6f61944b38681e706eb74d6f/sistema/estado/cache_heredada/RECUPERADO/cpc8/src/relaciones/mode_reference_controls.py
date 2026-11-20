"""Selective acquired-reference cuts; edited branches never feed MAIN."""
import argparse,hashlib,json,os,shutil,sys,time
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.pending');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(t,p)
def main():
 p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--mode',choices=['cut','sham'],required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 a.out.mkdir(parents=True,exist_ok=False);bundle=a.out/'executed_source';src=bundle/'src/relaciones';src.mkdir(parents=True)
 for name in ['mode_reference.py','mode_reference_controls.py']:shutil.copyfile(ROOT/'src/relaciones'/name,src/name)
 sys.path.insert(0,str(bundle/'src'));from relaciones.mode_reference import ModeReferenceSession,physical,move
 from dee_thinking import _native as d
 start=time.monotonic();parent=ModeReferenceSession.load(a.parent);assert parent.tick==110
 before=physical(parent.world);sites=[move(b['second_site'],(b['a_axis'],b['a_axis'],0),110-b['second_tick']) for b in parent.geometry['branches'] if b['stage']==1 and b['comparison_y']==0]
 edits=[];observations=[]
 for q in sites:
  o=parent.world.runtime.observe(d.Coordinate(*q));e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*q);e.raw=int(o.raw) if a.mode=='sham' else 0;e.label='fixed acquired-reference candidate site '+a.mode;edits.append(e)
  observations.append({'pre':parent.observe(q),'requested_raw':str(e.raw),'clock_edit':None})
 child=parent.world.diagnostic_fork(edits,True);s=ModeReferenceSession(child,parent.geometry,deepcopy(parent.state))
 for o,q in zip(observations,sites):o['post']=s.observe(q)
 forkphysical=physical(s.world);first_capture=len(s.state['captures']);s.run_until(200)
 target=a.out/'FINAL_T200.deetsnap.gz';storage=s.save(target);after=physical(parent.world)
 m={'schema':'CPC8R.mode_reference.control.v1','case':{'id':a.out.name,'mode':a.mode},'parent':{'snapshot':str(a.parent),'sha256':sha(a.parent),'tick':110},'preparations':0,'diagnostic_forks':1,'continuations':0,'status':'EXECUTED','source_sha256':{x.name:sha(x) for x in src.glob('*.py')},'parent_physical_before':before,'parent_physical_after':after,'parent_unchanged':before==after,'edited_sites':observations,'fork_physical':forkphysical,'captures_after_fork':s.state['captures'][first_capture:],'requests':s.receipts(),'snapshot':{'path':target.name,'storage':storage,'physical':physical(s.world)},'elapsed_seconds':time.monotonic()-start,'new_inputs_after_fork':[],'interpretation_scope':'Selective acquired-reference candidates only. Query objects, all normalization resources, independent other relation, clocks and receipts preserved.'}
 put(a.out/'MEASUREMENTS.json',m);print(json.dumps({'id':a.out.name,'parent_unchanged':m['parent_unchanged'],'captures':[(x['covered'],x['relation']) for x in m['captures_after_fork']]}))
if __name__=='__main__':main()
