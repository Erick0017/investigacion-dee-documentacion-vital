"""Frozen three-epoch native spatial-sensor screening, preserving all failures."""
import argparse,hashlib,json,os,shutil,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.pending');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(t,p)
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();cfg=json.loads(a.config.read_text(encoding='utf-8'));case=next(x for x in cfg['cases']if x['id']==a.case);a.out.mkdir(parents=True,exist_ok=False);bundle=a.out/'executed_source';src=bundle/'src/relaciones';src.mkdir(parents=True)
 for name in ['spatial_arrival.py','run_spatial_arrival.py']:shutil.copyfile(ROOT/'src/relaciones'/name,src/name)
 sys.path.insert(0,str(bundle/'src'));from relaciones.spatial_arrival import SpatialSession,move
 start=time.monotonic();m={'schema':'CPC8R.spatial_arrival.measurements.v1','case':case,'preparations':1,'diagnostic_forks':0,'continuations':0,'source_sha256':{p.name:sha(p)for p in src.glob('*.py')},'config_sha256':sha(a.config),'status':'RUNNING','frames':[],'snapshots':[],'host_RAW_clock_edits_on_MAIN':[]};put(a.out/'CONFIG.json',cfg)
 try:
  s=SpatialSession.create();m['geometry']=s.geometry
  for i,episode in enumerate(case['episodes']):s.episode(i,*episode)
  ticks={0,1,2,3,4,5,6,7,8,9}
  for base,da,db in case['episodes']:ticks.update(base+k for k in [0,da,db,da+1,db+1,9,10,11,12,13,14])
  for t in sorted(ticks):
   s.run_until(t);frame={'tick':t,'body':{key:s.observe(q)for key,q in s.geometry['body'].items()}}
   if any(t==e[0]+13 for e in case['episodes']):
    p=frame['body']['emission'];v=p['direction'];frame['published_decode']={'covered':p['active'] and v[0]in(-1,1)and v[1]==-1 and v[2]==0,'reference_axis':v[0]if p['active']and v[0]in(-1,1)and v[1]==-1 and v[2]==0 else None}
   m['frames'].append(frame)
   if any(t in(e[0]+13,e[0]+14)for e in case['episodes']):
    path=a.out/('T'+str(t)+'.deetsnap.gz');m['snapshots'].append({'path':path.name,'storage':s.save(path)})
   put(a.out/'INCREMENTAL.json',{'tick':t,'requests':s.receipts()})
  m.update(status='EXECUTED',requests=s.receipts())
 except BaseException as e:m.update(status='TECHNICAL_ERROR',error=str(e),traceback=traceback.format_exc());raise
 finally:m['elapsed_seconds']=time.monotonic()-start;put(a.out/'MEASUREMENTS.json',m)
 print(json.dumps({'id':case['id'],'decode':[(f['tick'],f['published_decode'])for f in m['frames']if'published_decode'in f]}))
if __name__=='__main__':main()
