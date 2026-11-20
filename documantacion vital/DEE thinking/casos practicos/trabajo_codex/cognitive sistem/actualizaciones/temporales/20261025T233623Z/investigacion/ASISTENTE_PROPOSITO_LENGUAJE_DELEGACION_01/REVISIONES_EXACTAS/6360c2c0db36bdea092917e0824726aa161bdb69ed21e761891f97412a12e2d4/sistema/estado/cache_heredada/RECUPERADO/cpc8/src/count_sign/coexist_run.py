"""Exact-source finite coexistence trial, one writer and one native world."""
import argparse,hashlib,json,os,shutil,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCES=['src/integracion/'+x+'.py'for x in('longitudinal_e1','complete_e1','quantity_core','relational_guarded_v2','relational_social','relational_ensemble','relational_pair_v2','relational_pair','contact_renewal_e1','initiative_e1','initiative_use_e1')]+['src/comunicacion/'+x+'.py'for x in('mode_communication','contact_social_e1','contact_social_regulated')]+['src/relaciones/mode_reference.py','src/iniciativa_accion/solicitud.py','src/iniciativa_accion/return_use.py','src/transferencia_magnitud/transferencia.py','src/transferencia_magnitud/cts_integrado.py','src/relaciones/contact_cardinality.py','src/count_sign/coexist.py','src/count_sign/coexist_run.py']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,m):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.pending');t.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8');os.replace(t,p)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();cfg=json.loads(a.config.read_text(encoding='utf8'));case=next(x for x in cfg['cases']if x['id']==a.case);out=a.out/case['id'];out.mkdir(parents=True,exist_ok=False);cut=out/'executed_source';hashes={}
 for rel in SOURCES:
  dst=cut/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dst);hashes[rel]=sha(dst)
 sys.path.insert(0,str(cut/'src'));from count_sign.coexist import MCTSCountSession
 from integracion.relational_pair import physical,move
 m={'schema':'CPC8R.magnitudeCTS_countF3.measurements.v1','case':case,'configuration_sha256':sha(a.config),'source_sha256':hashes,'preparations':0,'diagnostic_forks':0,'continuations':0,'frames':[],'snapshots':[],'status':'RUNNING','host_RAW_clock_edits_on_MAIN':[]};start=time.monotonic()
 prepkeys=('guard_mode','actor_mode','event_state_offset','medium_load','actor_state','quantity_guards','regulation','count_contacts','count_translation','count_actor_state','count_medium_state')
 try:
  s=MCTSCountSession.create(identifier=case['id'],**{k:v for k,v in case.items()if k in prepkeys});m.update(preparations=1,geometry=s.geometry);s.curriculum(**{k:v for k,v in case.items()if k not in('id',*prepkeys)})
  boundaries={0,3,4,5,9,10,31,69,70,72,73,76,77,79,80,86,89,99,100,103,110,136,137,143,144,146,147,165,170,203,204,206,213,214,268,271,280,281,337,338,340,344,348,404,405,411,415,417,428,471,472,478,484,486,487,499,500,538,539,549,553,554,558,559,563,616}
  for t in sorted(boundaries):
   s.run_until(t);f=s.view();f['mode'].pop('captures',None);f['mode'].pop('social_captures',None);m['frames'].append(f)
   if t in(0,10,77,144,281,549,616):
    snap=out/('T'+str(t)+'.deetsnap.gz');storage=s.save(snap);m['snapshots'].append({'path':snap.name,'tick':t,'sha256':sha(snap),'physical':physical(s.world),'storage':storage})
   m.update(last_complete_tick=t,requests=s.receipts(),elapsed_seconds=time.monotonic()-start);put(out/'MEASUREMENTS.json',m)
  m.update(status='MEASURED',final_physical=physical(s.world),requests=s.receipts(),count_observations=s.state['count_observations'],quantity_observations=s.quantity.state['observations'],magnitude_observations=s.state['magnitude_observations'],contact_social_observations=s.state['contact_social_observations'],initiative_captures=s.initiative.state['captures'],return_use_observations=s.state['return_use_observations'],renewal_observations=s.state['renewal_observations'],mode_captures=s.mode.state['captures'],social_captures=s.mode.state.get('social_captures',[]))
 except BaseException as e:m.update(status='TECHNICAL_ERROR',error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());raise
 finally:m['elapsed_seconds']=time.monotonic()-start;put(out/'MEASUREMENTS.json',m)
 print(json.dumps({'case':case['id'],'status':m['status'],'count':[(x['tick'],x['collector'])for x in m['count_observations']if x['tick']in(10,77,144)],'seconds':m['elapsed_seconds']}))
