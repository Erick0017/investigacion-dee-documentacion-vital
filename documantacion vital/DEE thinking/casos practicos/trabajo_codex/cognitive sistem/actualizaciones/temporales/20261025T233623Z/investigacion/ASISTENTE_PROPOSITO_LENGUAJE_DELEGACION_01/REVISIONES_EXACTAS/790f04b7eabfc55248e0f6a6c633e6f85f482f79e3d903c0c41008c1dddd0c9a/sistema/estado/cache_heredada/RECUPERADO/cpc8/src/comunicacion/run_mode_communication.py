"""Fresh shared Runtime communication trajectory with fixed submitted schedule."""
import argparse,hashlib,json,os,shutil,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.pending');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(t,p)
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();cfg=json.loads(a.config.read_text(encoding='utf-8'));case=next(x for x in cfg['cases'] if x['id']==a.case)
 a.out.mkdir(parents=True,exist_ok=False);bundle=a.out/'executed_source';sources={}
 for file in ['src/relaciones/mode_reference.py','src/comunicacion/mode_communication.py','src/comunicacion/run_mode_communication.py']:
  target=bundle/file;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/file,target);sources[file]=sha(target)
 sys.path.insert(0,str(bundle/'src'));from comunicacion.mode_communication import ModeCommunicationSession
 from relaciones.mode_reference import physical,move
 start=time.monotonic();cpu=time.process_time();m={'schema':'CPC8R.mode_communication.measurements.v1','case':case,'source_sha256':sources,'configuration_sha256':sha(a.config),'preparations':1,'diagnostic_forks':0,'continuations':0,'status':'RUNNING','snapshots':[],'frames':[],'host_RAW_clock_edits_on_MAIN':[]};put(a.out/'CONFIG.json',cfg)
 try:
  s=ModeCommunicationSession.create(object_states=tuple(case['object_states']),reference_state=case['reference_state'])
  s.acquire_reference(case['reference_direction'],case['reference_mode'],case['reference_load']);s.prepare_normalizers();s.query_object(1,case['objects'][0],case['query_loads'][0]);s.query_object(2,case['objects'][1],case['query_loads'][1]);s.acquire_other(case['other_value']);s.teach_form(case['form_mode']);s.query_receiver(enabled=case.get('query_enabled',True));s.present_context(case['context'])
  m['geometry']=s.geometry
  for t in [0,3,69,70,78,90,98,110,156,157,159,160,180,200,226,227,231,232,235]:
   s.run_until(t);frame={'tick':t}
   if t in(159,160,226,227):
    frame['receivers']={r['id']:[s.observe(move(r['memory_site'],(x,y,z))) for x in(-1,0,1) for y in(-1,0,1) for z in(-1,0,1)] for r in s.geometry['communication']['receivers']}
   m['frames'].append(frame)
   if t in(0,157,160,200,227,235):
    path=a.out/('T'+str(t)+'.deetsnap.gz');m['snapshots'].append({'path':path.name,'physical':physical(s.world),'storage':s.save(path)})
   put(a.out/'INCREMENTAL.json',{'tick':s.tick,'captures':s.state.get('social_captures',[]),'requests':s.receipts()})
  m.update(status='EXECUTED',captures=s.state['captures'],social_captures=s.state['social_captures'],requests=s.receipts(),aliases=s.state['aliases'],final_physical=physical(s.world))
 except BaseException as e:m.update(status='TECHNICAL_ERROR',error=str(e),traceback=traceback.format_exc());raise
 finally:m.update(elapsed_seconds=time.monotonic()-start,cpu_seconds=time.process_time()-cpu);put(a.out/'MEASUREMENTS.json',m)
 print(json.dumps({'id':case['id'],'response':[(r['receiver'],r['covered'],r['relation']) for r in m['social_captures'] if r['phase']=='FORM_QUERY']}))
if __name__=='__main__':main()
