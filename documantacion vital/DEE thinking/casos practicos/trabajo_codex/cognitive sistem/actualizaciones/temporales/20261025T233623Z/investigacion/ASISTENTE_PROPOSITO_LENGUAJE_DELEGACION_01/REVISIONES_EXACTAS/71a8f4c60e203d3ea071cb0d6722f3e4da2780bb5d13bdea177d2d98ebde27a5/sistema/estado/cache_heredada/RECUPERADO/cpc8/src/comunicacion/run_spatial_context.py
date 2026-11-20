"""Native acquisition, new positions, later opaque form, social use, oneRuntime."""
import argparse,hashlib,json,os,shutil,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.pending');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(t,p)
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();cfg=json.loads(a.config.read_text(encoding='utf-8'));case=next(x for x in cfg['cases']if x['id']==a.case);a.out.mkdir(parents=True,exist_ok=False);bundle=a.out/'executed_source';sources={}
 for f in ['src/relaciones/mode_reference.py','src/relaciones/spatial_gradient.py','src/relaciones/spatial_reference.py','src/comunicacion/spatial_communication.py','src/comunicacion/spatial_context.py','src/comunicacion/run_spatial_context.py']:
  target=bundle/f;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,target);sources[f]=sha(target)
 sys.path.insert(0,str(bundle/'src'));from comunicacion.spatial_context import SpatialContextSession
 from relaciones.mode_reference import physical,move
 start=time.monotonic();m={'schema':'CPC8R.spatial_context.measurements.v1','case':case,'preparations':0,'diagnostic_forks':0,'continuations':0,'status':'RUNNING','source_sha256':sources,'configuration_sha256':sha(a.config),'frames':[],'snapshots':[],'host_RAW_clock_edits_on_MAIN':[]};put(a.out/'CONFIG.json',cfg)
 try:
  s=SpatialContextSession.create(reference_state=case.get('reference_state',17),object_states=tuple(case.get('object_states',[99,171])),context_state=case.get('context_state',233))
  m['preparations']=1;s.context_curriculum(case['reference_axis'],*case['objects'],case['context'],reference=case['reference_mode'],loads=tuple(case['loads']),current_stages=tuple(case.get('current_stages',[1,2])),form=case['form'],query=case.get('query',True),context_objects=case.get('context_objects',True),context_load=case.get('context_load',11));m['geometry']=s.geometry
  for t in [0,1,11,68,77,78,110,155,164,165,167,168,180,200,228,229,230,231,234,235,239,240,243]:
   s.run_until(t);f={'tick':t,'reference_sensor':s.observe(s.geometry['reference_sensor'])}
   if t in(167,168,234,235):f['receivers']={r['id']:[s.observe(move(r['memory_site'],(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]for r in s.geometry['communication']['receivers']}
   if t in(229,231):f['native_context_sensors']={p['receiver']+':'+str(p['candidate']):s.observe(p['center'])for p in s.geometry['native_context']['sensors']}
   m['frames'].append(f)
   if t in(0,11,78,110,165,168,200,235,243):
    path=a.out/('T'+str(t)+'.deetsnap.gz');m['snapshots'].append({'path':path.name,'physical':physical(s.world),'storage':s.save(path)})
   put(a.out/'INCREMENTAL.json',{'tick':t,'requests':s.receipts(),'social_captures':s.state.get('social_captures',[])})
  m.update(status='EXECUTED',requests=s.receipts(),captures={key:m.state['captures']for key,m in s.modes.items()},social_captures=s.state['social_captures'],final_physical=physical(s.world))
 except BaseException as e:m.update(status='TECHNICAL_ERROR',error=str(e),traceback=traceback.format_exc());raise
 finally:m['elapsed_seconds']=time.monotonic()-start;put(a.out/'MEASUREMENTS.json',m)
 print(json.dumps({'id':case['id'],'receiver':[(x['receiver'],x['request_applied'],x['covered'],x['relation'])for x in m['social_captures']if x['phase']=='FORM_QUERY']}))
if __name__=='__main__':main()
