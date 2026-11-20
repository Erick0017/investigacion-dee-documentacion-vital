"""Native spatial-reference trajectory; no objective answer reaches the session."""
import argparse,hashlib,json,os,shutil,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.pending');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(t,p)
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();cfg=json.loads(a.config.read_text(encoding='utf-8'));case=next(x for x in cfg['cases']if x['id']==a.case);a.out.mkdir(parents=True,exist_ok=False);bundle=a.out/'executed_source';src=bundle/'src/relaciones';src.mkdir(parents=True)
 for name in ['mode_reference.py','spatial_gradient.py','spatial_reference.py','run_spatial_reference.py']:shutil.copyfile(ROOT/'src/relaciones'/name,src/name)
 sys.path.insert(0,str(bundle/'src'));from relaciones.spatial_reference import SpatialReferenceSession,move
 from relaciones.mode_reference import physical
 start=time.monotonic();m={'schema':'CPC8R.spatial_reference.measurements.v1','case':case,'preparations':0,'diagnostic_forks':0,'continuations':0,'source_sha256':{p.name:sha(p)for p in src.glob('*.py')},'config_sha256':sha(a.config),'status':'RUNNING','frames':[],'snapshots':[],'host_RAW_clock_edits_on_MAIN':[]};put(a.out/'CONFIG.json',cfg)
 try:
  s=SpatialReferenceSession.create(reference_state=case.get('reference_state',17),object_states=tuple(case.get('object_states',[99,171])));m['preparations']=1;m['geometry']=s.geometry;s.curriculum(case['reference_axis'],case['objects'][0],case['objects'][1],case['reference_mode'],tuple(case['loads']),tuple(case.get('current_stages',[1,2])))
  for t in [0,1,2,3,10,11,12,67,68,69,77,78,79,86,98,106,110,154,155,156,164,165,166,180,208]:
   s.run_until(t);frame={'tick':t,'reference_sensor':s.observe(s.geometry['reference_sensor'])}
   if t in(10,11,12,77,78,79,164,165,166):
    frame['query_neighborhoods']={key+':'+q['parent']['id']:[s.observe(move(q['parent']['hub'],(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]for key,g in s.geometry['modes'].items()for q in g['queries']if t in(q['parent']['query_tick']-1,q['parent']['query_tick'],q['parent']['query_tick']+1)or(t in(10,11,12)and q['stage']==1)}
   if t in(68,69,155,156):frame['current_sensors']={p['id']:s.observe(p['center'])for p in s.geometry['sensors']if p['stage']==(1 if t<100 else 2)}
   m['frames'].append(frame)
   if t in(0,11,78,110,165,208):
    path=a.out/('T'+str(t)+'.deetsnap.gz');m['snapshots'].append({'path':path.name,'physical':physical(s.world),'storage':s.save(path)})
   put(a.out/'INCREMENTAL.json',{'tick':t,'requests':s.receipts(),'captures':{key:m.state['captures']for key,m in s.modes.items()}})
  m.update(status='EXECUTED',requests=s.receipts(),captures={key:m.state['captures']for key,m in s.modes.items()},final_physical=physical(s.world))
 except BaseException as e:m.update(status='TECHNICAL_ERROR',error=str(e),traceback=traceback.format_exc());raise
 finally:m['elapsed_seconds']=time.monotonic()-start;put(a.out/'MEASUREMENTS.json',m)
 print(json.dumps({'id':case['id'],'captures':{key:[(x['tick'],x['stage'],x['covered'],x['relation'],x['physical']['direction'])for x in cs]for key,cs in m['captures'].items()}}))
if __name__=='__main__':main()
