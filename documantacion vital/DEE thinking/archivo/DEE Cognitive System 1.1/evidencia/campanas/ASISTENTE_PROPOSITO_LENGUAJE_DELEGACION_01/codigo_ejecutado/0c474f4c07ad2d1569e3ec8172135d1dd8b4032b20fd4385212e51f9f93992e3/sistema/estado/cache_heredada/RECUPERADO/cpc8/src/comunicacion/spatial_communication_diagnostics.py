"""Native spatial message and acquired receiver-memory interventions, separate branches."""
import argparse,hashlib,json,os,shutil,sys,time
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.pending');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(t,p)
def main():
 p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--target',choices=['message','receiver_memory'],required=True);p.add_argument('--mode',choices=['cut','sham','same_load_flip_y'],required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);bundle=a.out/'executed_source'
 for f in ['src/relaciones/mode_reference.py','src/relaciones/spatial_gradient.py','src/relaciones/spatial_reference.py','src/comunicacion/spatial_communication.py','src/comunicacion/spatial_communication_diagnostics.py']:
  target=bundle/f;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,target)
 sys.path.insert(0,str(bundle/'src'));from comunicacion.spatial_communication import SpatialCommunicationSession
 from relaciones.mode_reference import physical,move
 from dee_thinking import _native as d
 start=time.monotonic();parent=SpatialCommunicationSession.load(a.parent);expected=165 if a.target=='message'else 200;assert parent.tick==expected;sites=[]
 if a.target=='message':
  for mg in parent.geometry['modes'].values():sites+=[q['parent']['hub']for q in mg['queries']if q['stage']==2]
 else:sites=[move(r['memory_site'],(r['reference_axis'],r['comparison_y'],0),32)for r in parent.geometry['communication']['receivers']]
 before=physical(parent.world);edits=[];observations=[]
 for q in sites:
  o=parent.world.runtime.observe(d.Coordinate(*q));raw=int(o.raw);new=raw
  if a.mode=='cut':new=0
  if a.mode=='same_load_flip_y':
   v=o.record
   if int(v.dx)in(-1,1)and int(v.dz)==1:new=d.pack_record(int(v.state),int(v.s_reg),int(v.dx),int(v.dx)if int(v.dy)==0 else 0,int(v.dz),int(v.semantic))
  e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*q);e.raw=new;e.label='Spatial message or memory '+a.mode;edits.append(e);observations.append({'pre':parent.observe(q),'requested_raw':str(new),'clock_edit':None})
 child=parent.world.diagnostic_fork(edits,True);parent.state['modes']={key:deepcopy(m.state)for key,m in parent.modes.items()};s=SpatialCommunicationSession(child,parent.geometry,parent.state);old=len(s.state['social_captures'])
 for obs,q in zip(observations,sites):obs['post']=s.observe(q)
 forkphysical=physical(child);s.run_until(243);path=a.out/'T243.deetsnap.gz';storage=s.save(path)
 m={'schema':'CPC8R.spatial_communication.diagnostic.v1','case':{'id':a.out.name,'target':a.target,'mode':a.mode},'parent':{'snapshot':str(a.parent),'sha256':sha(a.parent),'tick':expected},'preparations':0,'diagnostic_forks':1,'continuations':0,'status':'EXECUTED','source_sha256':{p.relative_to(bundle).as_posix():sha(p)for p in bundle.rglob('*.py')},'parent_physical_before':before,'parent_physical_after':physical(parent.world),'parent_unchanged':before==physical(parent.world),'fork_physical':forkphysical,'edited_sites':observations,'social_captures_after_fork':s.state['social_captures'][old:],'requests':s.receipts(),'new_inputs_after_fork':[],'snapshot':{'path':path.name,'physical':physical(child),'storage':storage},'elapsed_seconds':time.monotonic()-start,'modality':'AUTHORIZED_DIAGNOSTIC_BRANCH_NOT_MAIN_POLICY'}
 put(a.out/'MEASUREMENTS.json',m);print(json.dumps({'id':a.out.name,'parent_unchanged':m['parent_unchanged'],'query':[(x['receiver'],x['request_applied'],x['covered'],x['relation'])for x in m['social_captures_after_fork']if x['phase']=='FORM_QUERY']}))
if __name__=='__main__':main()
