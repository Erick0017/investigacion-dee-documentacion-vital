"""Exact source/trajectory runner for the final parallel access family."""
import argparse,hashlib,json,os,shutil,sys,time,traceback
from pathlib import Path
from array import array
ROOT=Path(__file__).resolve().parents[2]
SOURCES=['src/count_sign/branch_session.py','src/count_sign/branch_run.py','src/count_sign/session.py','src/relaciones/contact_cardinality.py','src/integracion/quantity_core.py']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,m):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.pending');t.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8');os.replace(t,p)
def physical(w):
 r=w.runtime;return{'tick':int(r.current_tick),'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case');a=p.parse_args();cfg=json.loads(a.config.read_text(encoding='utf8'));index=[]
 for case in cfg['cases']:
  if a.case and a.case!=case['id']:continue
  out=a.out/case['id'];out.mkdir(parents=True,exist_ok=False);cut=out/'executed_source';hashes={}
  for f in SOURCES:
   dst=cut/f;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,dst);hashes[f]=sha(dst)
  sys.path.insert(0,str(cut/'src'));from count_sign.branch_session import BranchCountSignSession
  from count_sign.session import move
  m={'schema':'CPC8R.count_sign.parallel.measurements.v1','case':case,'configuration_sha256':sha(a.config),'source_sha256':hashes,'preparations':0,'diagnostic_forks':0,'continuations':0,'frames':[],'snapshots':[],'host_RAW_clock_edits_on_MAIN':[],'status':'RUNNING'};start=time.monotonic()
  try:
   s=BranchCountSignSession.create(case);m['preparations']=1;m['geometry']=s.geometry;s.curriculum(form=case.get('form','paired'),route=case.get('route',True),query=case.get('query',True))
   for t in(0,4,5,9,10,19,20,23,24,25,89,90,91,92,93,94,95,103,113,114,115,147,148,149,170,171):
    frame=s.run_until(t);frame['physical']=physical(s.world)
    if t in(19,20,23,24,90,91,93,94,113,114,147,148):
     qlist=[b['quantity']['center']for b in s.geometry['branches']]+[p['memory_site'if t<100 else'query1_site'if t<140 else'query2_site']for p in s.geometry['names']]
     frame['Moore27']=[{'center':q,'readings':[s.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]}for q in qlist]
    m['frames'].append(frame);m['last_complete_tick']=t;m['requests']=s.receipts();m['elapsed_seconds']=time.monotonic()-start
    if t in(0,10,24,91,94,114,148,171):
     path=out/('T'+str(t)+'.deetsnap.gz');storage=s.save(path);m['snapshots'].append({'path':path.name,'tick':t,'sha256':sha(path),'storage':storage,'physical':physical(s.world)})
    put(out/'MEASUREMENTS.json',m)
   m.update(status='MEASURED',final_physical=physical(s.world),requests=s.receipts())
  except BaseException as e:m.update(status='TECHNICAL_ERROR',error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());raise
  finally:m['elapsed_seconds']=time.monotonic()-start;put(out/'MEASUREMENTS.json',m)
  index.append({'case_id':case['id'],'path':str((out/'MEASUREMENTS.json').relative_to(ROOT)),'sha256':sha(out/'MEASUREMENTS.json')});print(json.dumps({'case':case['id'],'query1':next(x['names']for x in m['frames']if x['tick']==114)}))
 put(a.out/'INDEX.json',{'cases':index})
