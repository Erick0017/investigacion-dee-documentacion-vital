"""Selective spatial-reference diagnostics; all edited branches remain separate."""
import argparse,hashlib,json,os,shutil,sys,time
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.pending');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(t,p)
def main():
 p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--target',choices=['wave','wave_and_reference_sensor'],required=True);p.add_argument('--mode',choices=['cut','sham'],required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);bundle=a.out/'executed_source';src=bundle/'src/relaciones';src.mkdir(parents=True)
 for name in ['mode_reference.py','spatial_gradient.py','spatial_reference.py','spatial_reference_diagnostics.py']:shutil.copyfile(ROOT/'src/relaciones'/name,src/name)
 sys.path.insert(0,str(bundle/'src'));from relaciones.spatial_reference import SpatialReferenceSession,move
 from relaciones.mode_reference import physical
 from dee_thinking import _native as d
 start=time.monotonic();parent=SpatialReferenceSession.load(a.parent);assert parent.tick==110;before=physical(parent.world);sites=[]
 for mg in parent.geometry['modes'].values():
  sites +=[move(b['second_site'],(b['a_axis'],b['a_axis'],0),110-b['second_tick'])for b in mg['branches']if b['stage']==1 and b['comparison_y']==0]
 if a.target=='wave_and_reference_sensor':sites.append(parent.geometry['reference_sensor'])
 edits=[];observations=[]
 for q in sites:
  o=parent.world.runtime.observe(d.Coordinate(*q));e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*q);e.raw=int(o.raw)if a.mode=='sham'else 0;e.label='fixed spatial reference '+a.target+' '+a.mode;edits.append(e);observations.append({'pre':parent.observe(q),'requested_raw':str(e.raw),'clock_edit':None})
 child=parent.world.diagnostic_fork(edits,True);parent.state['modes']={key:deepcopy(m.state)for key,m in parent.modes.items()};s=SpatialReferenceSession(child,parent.geometry,parent.state);old={key:len(m.state['captures'])for key,m in s.modes.items()}
 for obs,q in zip(observations,sites):obs['post']=s.observe(q)
 forkphysical=physical(child);s.run_until(155);sensorcheck={p['id']:s.observe(p['center'])for p in s.geometry['sensors']if p['stage']==2};s.run_until(208)
 captures={key:m.state['captures'][old[key]:]for key,m in s.modes.items()};path=a.out/'T208.deetsnap.gz';storage=s.save(path)
 m={'schema':'CPC8R.spatial_reference.diagnostic.v1','case':{'id':a.out.name,'target':a.target,'mode':a.mode},'parent':{'snapshot':str(a.parent),'sha256':sha(a.parent),'tick':110},'preparations':0,'diagnostic_forks':1,'continuations':0,'status':'EXECUTED','source_sha256':{p.name:sha(p)for p in src.glob('*.py')},'parent_physical_before':before,'parent_physical_after':physical(parent.world),'parent_unchanged':before==physical(parent.world),'fork_physical':forkphysical,'edited_sites':observations,'current_sensor_perception_preserved':sensorcheck,'captures_after_fork':captures,'requests':s.receipts(),'new_inputs_after_fork':[],'snapshot':{'path':path.name,'physical':physical(child),'storage':storage},'elapsed_seconds':time.monotonic()-start}
 put(a.out/'MEASUREMENTS.json',m);print(json.dumps({'id':a.out.name,'parent_unchanged':m['parent_unchanged'],'captures':{key:[(x['covered'],x['relation'])for x in cs]for key,cs in captures.items()}}))
if __name__=='__main__':main()
