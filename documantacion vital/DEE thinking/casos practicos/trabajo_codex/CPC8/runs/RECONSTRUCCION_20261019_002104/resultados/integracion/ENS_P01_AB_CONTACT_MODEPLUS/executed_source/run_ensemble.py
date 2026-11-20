"""Independent fresh ensemble trajectories and exact finite boundary observations."""
import argparse,hashlib,json,os,shutil,sys,time,traceback
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from integracion.relational_ensemble import EnsembleSession
from integracion.relational_pair import physical,move
import dee_thinking as dee
from dee_thinking import _native as d
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 t=p.with_name(p.name+'.pending');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8');os.replace(t,p)
def main():
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf8')
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 cfg=json.loads(a.config.read_text(encoding='utf8'));case=next(c for c in cfg['cases']if c['id']==a.case_id);a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 source=a.out/'executed_source';source.mkdir();paths=[Path(__file__),ROOT/'src/integracion/relational_ensemble.py',ROOT/'src/integracion/relational_pair.py',ROOT/'src/integracion/relational_pair_v2.py',ROOT/'src/relaciones/mode_reference.py']
 for path in paths:shutil.copyfile(path,source/path.name)
 s=EnsembleSession.create(identifier=case['id'],actor_mode=case['actor_mode'],include_order=case['include_order'],include_contact=case['include_contact'],event_state_offset=case.get('event_state_offset',0),medium_load=case.get('medium_load',1),actor_state=case.get('actor_state',1))
 if dee.__version__!='4.5.0'or not Path(dee.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):raise RuntimeError('Installed isolated official4.5 required')
 m={'schema':'CPC8R.relational_ensemble.measurements.v1','case':case,'configuration_sha256':sha(a.config),'source_sha256':{x.name:sha(x)for x in paths},'engine':{'version':dee.__version__,'module':dee.__file__,'native_sha256':sha(d.__file__),'python':sys.executable},'geometry':s.geometry,'preparations':1,'continuations':0,'diagnostic_forks':0,'host_RAW_clock_edits_on_MAIN':[],'frames':[],'windows':[],'snapshots':[],'status':'RUNNING'}
 def save(tick):
  path=a.out/('T'+str(tick)+'.deetsnap.gz');proof=s.save(path);m['snapshots'].append({'path':path.name,'tick':tick,'sha256':sha(path),'physical':physical(s.world),'storage':proof})
 def checkpoint():m.update(last_complete_tick=s.tick,elapsed_seconds=time.monotonic()-start,requests=s.receipts());put(a.out/'MEASUREMENTS.json',m)
 try:
  s.curriculum(**{k:v for k,v in case.items()if k not in('id','actor_mode','event_state_offset','medium_load','actor_state')});save(0);checkpoint()
  windows={5:[s.geometry['body']['emission'],s.geometry['contact_base']],9:[x['hub']for x in s.geometry['contact'].values()],11:[x['hub']for x in s.geometry['order'].values()],31:[x['query_site']for x in s.geometry['order'].values()],76:[x['query_site']for x in s.geometry['contact'].values()],143:[x['renewed_site']for x in s.geometry['contact'].values()],165:[x['query_site']for x in s.geometry['order'].values()],170:[s.geometry['auxiliary_hub']],180:[s.geometry['mode']['other_hub']],206:[s.geometry['common_join']],210:[x['use_site']for x in s.geometry['joint_names'].values()],214:[x['delivery_site']for x in s.geometry['joint_names'].values()],281:[x['delivery_site']for x in s.geometry['joint_names'].values()],348:[x['delivery_site']for x in s.geometry['joint_names'].values()]}
  for q in s.geometry['mode']['queries']:windows.setdefault(q['parent']['query_tick'],[]).append(q['parent']['hub'])
  for b in s.geometry['mode']['branches']:
   for role in('first','second','cleanup'):windows.setdefault(b[role+'_tick'],[]).append(b[role+'_site'])
  boundaries={99,100,109,110}
  for tick in windows:boundaries.update((tick-1,tick))
  for tick in sorted(boundaries):
   s.run_until(tick);m['frames'].append(s.view())
   for target,centers in windows.items():
    if tick in(target-1,target):
     for q in centers:m['windows'].append({'tick':tick,'nominal_stage':target,'center':q,'Moore27':[s.observe(move(q,(dx,dy,dz)))for dx in(-1,0,1)for dy in(-1,0,1)for dz in(-1,0,1)]})
   if tick in(11,82,170,206,214,281,348):save(tick)
   checkpoint()
  m.update(status='MEASURED',final_physical=physical(s.world),receipt_statuses=dict(Counter(r['receipt']['status']for r in s.receipts())),mode_captures=s.mode.state['captures'])
 except BaseException as error:m.update(status='TECHNICAL_ERROR',error_type=type(error).__name__,error=str(error),traceback=traceback.format_exc());raise
 finally:checkpoint()
 print(json.dumps({'id':case['id'],'status':m['status'],'mode':[(r['stage'],r['covered'],r['relation'])for r in m.get('mode_captures',[])],'common206':next(f for f in m['frames']if f['tick']==206)['common_join'],'receipts':m.get('receipt_statuses'),'seconds':m['elapsed_seconds']}),flush=True)
if __name__=='__main__':main()
