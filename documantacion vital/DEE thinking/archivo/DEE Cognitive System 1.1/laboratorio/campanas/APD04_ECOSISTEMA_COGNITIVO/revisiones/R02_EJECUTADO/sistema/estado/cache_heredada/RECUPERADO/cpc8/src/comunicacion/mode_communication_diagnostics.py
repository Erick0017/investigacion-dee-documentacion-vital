"""Selective message or acquired receiver-memory diagnostics; no MAIN edits."""
import argparse,hashlib,json,os,shutil,sys,time
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.pending');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(t,p)
def main():
 p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--target',choices=['message','receiver_memory'],required=True);p.add_argument('--mode',choices=['cut','sham'],required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);bundle=a.out/'executed_source'
 for f in ['src/relaciones/mode_reference.py','src/comunicacion/mode_communication.py','src/comunicacion/mode_communication_diagnostics.py']:
  q=bundle/f;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,q)
 sys.path.insert(0,str(bundle/'src'));from comunicacion.mode_communication import ModeCommunicationSession
 from relaciones.mode_reference import physical,move
 from dee_thinking import _native as d
 start=time.monotonic();parent=ModeCommunicationSession.load(a.parent);expected=157 if a.target=='message' else 200;assert parent.tick==expected
 sites=[q['parent']['hub'] for q in parent.geometry['queries'] if q['stage']==2] if a.target=='message' else [move(r['memory_site'],(r['reference_axis'],r['compared_y'],0),40) for r in parent.geometry['communication']['receivers']]
 before=physical(parent.world);edits=[];observations=[]
 for q in sites:
  o=parent.world.runtime.observe(d.Coordinate(*q));e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*q);e.raw=int(o.raw) if a.mode=='sham' else 0;e.label='fixed '+a.target+' candidate '+a.mode;edits.append(e);observations.append({'pre':parent.observe(q),'requested_raw':str(e.raw),'clock_edit':None})
 child=parent.world.diagnostic_fork(edits,True);s=ModeCommunicationSession(child,parent.geometry,deepcopy(parent.state));old=len(s.state.get('social_captures',[]))
 for o,q in zip(observations,sites):o['post']=s.observe(q)
 fork_physical=physical(child);s.run_until(235);path=a.out/'T235.deetsnap.gz';storage=s.save(path)
 m={'schema':'CPC8R.mode_communication.diagnostic.v1','case':{'id':a.out.name,'target':a.target,'mode':a.mode},'parent':{'snapshot':str(a.parent),'sha256':sha(a.parent),'tick':expected},'preparations':0,'diagnostic_forks':1,'continuations':0,'status':'EXECUTED','source_sha256':{p.relative_to(bundle).as_posix():sha(p) for p in bundle.rglob('*.py')},'parent_physical_before':before,'parent_physical_after':physical(parent.world),'parent_unchanged':before==physical(parent.world),'fork_physical':fork_physical,'edited_sites':observations,'social_captures_after_fork':s.state['social_captures'][old:],'requests':s.receipts(),'snapshot':{'path':path.name,'physical':physical(child),'storage':storage},'new_inputs_after_fork':[],'elapsed_seconds':time.monotonic()-start}
 put(a.out/'MEASUREMENTS.json',m);print(json.dumps({'id':a.out.name,'parent_unchanged':m['parent_unchanged'],'query':[(x['covered'],x['relation']) for x in m['social_captures_after_fork'] if x['phase']=='FORM_QUERY']}))
if __name__=='__main__':main()
