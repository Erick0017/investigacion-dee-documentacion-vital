"""Freeze exact source before a bounded new count-form trajectory."""
import argparse,hashlib,json,os,shutil,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCES=['src/count_sign/session.py','src/count_sign/run.py','src/relaciones/contact_cardinality.py','src/integracion/quantity_core.py']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,m):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.pending');t.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8');os.replace(t,p)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--config',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--case');args=a.parse_args();cfg=json.loads(args.config.read_text(encoding='utf8'));rows=[]
 for case in cfg['cases']:
  if args.case and args.case!=case['id']:continue
  out=args.out/case['id'];out.mkdir(parents=True,exist_ok=False);cut=out/'executed_source';hashes={}
  for f in SOURCES:
   dst=cut/f;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,dst);hashes[f]=sha(dst)
  sys.path.insert(0,str(cut/'src'));from count_sign.session import CountSignSession
  from dee_thinking import _native as d
  from array import array
  def physical(w):
   r=w.runtime;return{'tick':int(r.current_tick),'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}
  m={'schema':'CPC8R.count_sign.measurements.v1','case':case,'configuration_sha256':sha(args.config),'source_sha256':hashes,'preparations':0,'diagnostic_forks':0,'continuations':0,'frames':[],'snapshots':[],'status':'RUNNING','host_RAW_clock_edits_on_MAIN':[]};start=time.monotonic()
  try:
   s=CountSignSession.create(case);m['preparations']=1;m['geometry']=s.geometry;s.curriculum(form=case.get('form','paired'),route=case.get('route',True),query=case.get('query',True))
   ticks=s.geometry['ticks'];boundary={0,4,5,9,10,12,13,14,16,17,18,19,20,21,103,170}
   for target in(ticks['reference'],ticks['comparison'],ticks['form'],*ticks['queries']):boundary.update((target-2,target-1,target,target+1))
   for t in sorted(boundary):
    v=s.run_until(t);v['physical']=physical(s.world)
    if t in(4,5,9,10,13,14,17,18,20,ticks['reference'],ticks['comparison']-1,ticks['comparison'],ticks['form']-1,ticks['form'],ticks['queries'][0]-1,ticks['queries'][0]):
     centers=[s.geometry['count']['collector'],s.geometry['joint17'],s.geometry['reference_hub20'],s.geometry['quantity']['center']]+[p['memory_site']for p in s.geometry['names']]
     from count_sign.session import move
     v['Moore27']=[{'center':q,'readings':[s.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]}for q in centers]
    m['frames'].append(v);m['last_complete_tick']=t
    if t in(0,10,ticks['reference'],ticks['comparison'],ticks['form'],*ticks['queries']):
     path=out/('T'+str(t)+'.deetsnap.gz');storage=s.save(path);m['snapshots'].append({'path':path.name,'sha256':sha(path),'tick':t,'physical':physical(s.world),'storage':storage})
    m['requests']=s.receipts();m['elapsed_seconds']=time.monotonic()-start;put(out/'MEASUREMENTS.json',m)
   m.update(status='MEASURED',final_physical=physical(s.world),requests=s.receipts())
  except BaseException as e:m.update(status='TECHNICAL_ERROR',error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());raise
  finally:m['elapsed_seconds']=time.monotonic()-start;put(out/'MEASUREMENTS.json',m)
  rows.append({'case_id':case['id'],'path':str((out/'MEASUREMENTS.json').relative_to(ROOT)),'sha256':sha(out/'MEASUREMENTS.json')});print(json.dumps({'case':case['id'],'status':m['status'],'first_query':next(f['names']for f in m['frames']if f['tick']==ticks['queries'][0])}))
 put(args.out/'INDEX.json',{'cases':rows})
