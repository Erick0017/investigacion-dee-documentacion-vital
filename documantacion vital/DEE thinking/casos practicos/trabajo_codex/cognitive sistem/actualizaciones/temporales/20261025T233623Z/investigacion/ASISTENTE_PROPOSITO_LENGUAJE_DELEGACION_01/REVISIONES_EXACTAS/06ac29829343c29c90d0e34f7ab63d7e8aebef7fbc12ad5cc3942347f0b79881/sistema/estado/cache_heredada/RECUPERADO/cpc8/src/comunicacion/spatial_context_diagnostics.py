"""Selective interruption of a native context carrier, never of the response."""
import argparse,hashlib,json,os,shutil,sys,time
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.pending');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(t,p)
def main():
 p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--mode',choices=['cut','sham'],required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);bundle=a.out/'executed_source'
 for f in ['src/relaciones/mode_reference.py','src/relaciones/spatial_gradient.py','src/relaciones/spatial_reference.py','src/comunicacion/spatial_communication.py','src/comunicacion/spatial_context.py','src/comunicacion/spatial_context_diagnostics.py']:
  target=bundle/f;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,target)
 sys.path.insert(0,str(bundle/'src'));from comunicacion.spatial_context import SpatialContextSession
 from relaciones.mode_reference import move,physical
 from dee_thinking import _native as d
 start=time.monotonic();parent=SpatialContextSession.load(a.parent);assert parent.tick==235;oldquery=[x for x in parent.state['social_captures']if x['phase']=='FORM_QUERY'];parent.run_until(239);before=physical(parent.world);sites=[move(p['arrival_site'],(0,p['candidate'],0),-1)for p in parent.geometry['native_context']['sensors']]
 edits=[];observations=[]
 for q in sites:
  o=parent.world.runtime.observe(d.Coordinate(*q));e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*q);e.raw=int(o.raw)if a.mode=='sham'else 0;e.label='Native context carrier '+a.mode;edits.append(e);observations.append({'pre':parent.observe(q),'requested_raw':str(e.raw),'clock_edit':None})
 parent.state['modes']={key:deepcopy(m.state)for key,m in parent.modes.items()};child=parent.world.diagnostic_fork(edits,True);s=SpatialContextSession(child,parent.geometry,parent.state);old=len(s.state['social_captures'])
 for o,q in zip(observations,sites):o['post']=s.observe(q)
 forkphysical=physical(child);s.run_until(243);path=a.out/'T243.deetsnap.gz';storage=s.save(path)
 m={'schema':'CPC8R.spatial_context.diagnostic.v1','case':{'id':a.out.name,'mode':a.mode},'parent':{'snapshot':str(a.parent),'sha256':sha(a.parent),'saved_tick':235,'continued_without_new_inputs_to_fork_tick':239},'preparations':0,'diagnostic_forks':1,'continuations':0,'status':'EXECUTED','source_sha256':{p.relative_to(bundle).as_posix():sha(p)for p in bundle.rglob('*.py')},'parent_physical_before':before,'parent_physical_after':physical(parent.world),'parent_unchanged':before==physical(parent.world),'fork_physical':forkphysical,'edited_sites':observations,'query_before_fork_inherited_not_new':oldquery,'social_captures_after_fork':s.state['social_captures'][old:],'requests':s.receipts(),'new_inputs_after_fork':[],'snapshot':{'path':path.name,'physical':physical(child),'storage':storage},'elapsed_seconds':time.monotonic()-start}
 put(a.out/'MEASUREMENTS.json',m);print(json.dumps({'id':a.out.name,'parent_unchanged':m['parent_unchanged'],'active_deliveries':[(x['receiver'],x['physical']['direction'])for x in m['social_captures_after_fork']if x['phase']=='DELIVERY'and x['physical']['active']]}))
if __name__=='__main__':main()
