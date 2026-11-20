"""Late interference diagnostic; edited branches are not operational MAINs."""
import argparse,hashlib,json,os,shutil,sys,time
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from integracion.relational_ensemble import EnsembleSession
from integracion.relational_pair import physical,move
from dee_thinking import _native as d
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 t=p.with_name(p.name+'.pending');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8');os.replace(t,p)
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 cfg=json.loads(a.config.read_text(encoding='utf8'));case=next(c for c in cfg['cases']if c['id']==a.case_id);a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 pp=ROOT/'resultados/integracion'/cfg['parent_id']/cfg['snapshot'];psha=sha(pp);parent=EnsembleSession.load(pp);assert parent.tick==cfg['fork_tick'];before=physical(parent.world)
 paths=[Path(__file__),ROOT/'src/integracion/relational_ensemble.py',ROOT/'src/integracion/relational_pair.py',ROOT/'src/integracion/relational_pair_v2.py',ROOT/'src/relaciones/mode_reference.py'];src=a.out/'executed_source';src.mkdir()
 for path in paths:shutil.copyfile(path,src/path.name)
 edits=[];rows=[]
 for key,q in parent.geometry['joint_names'].items():
  site=q['delivery_site'];pre=parent.observe(site);v=pre['direction'];selected=pre['active']and pre['semantic']==1 and v[0]in(-1,1)and v[1:]==[1,1]
  e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*site);e.raw=0 if case['mode']=='cut'and selected else int(pre['raw']);e.label='Laboratory residual direction class '+case['mode'];edits.append(e);rows.append({'candidate':key,'site':site,'selected':selected,'pre':pre,'requested_raw':str(e.raw),'clock_edit':None})
 child=parent.world.diagnostic_fork(edits,True);s=EnsembleSession(child,parent.geometry,deepcopy(parent.state),parent.identifier+'.'+case['id'])
 for row in rows:row['post']=s.observe(row['site'])
 for q in s.geometry['joint_names'].values():s.input(q['query_port'],cfg['query_payload'],cfg['query_tick'],'probe','EXPLICIT_NEW_WORD_QUERY_LAB_BRANCH')
 m={'schema':'CPC8R.ensemble.interference_diagnostic.v1','case':case,'parent':{'path':str(pp.relative_to(ROOT)),'sha256':psha,'tick':parent.tick},'configuration_sha256':sha(a.config),'source_sha256':{x.name:sha(x)for x in paths},'preparations':0,'continuations':0,'diagnostic_forks':1,'edited_sites':rows,'parent_physical_before':before,'fork_physical':physical(s.world),'frames':[],'windows':[],'snapshots':[],'status':'RUNNING'}
 for tick in(348,363,364,414,415):
  s.run_until(tick);m['frames'].append(s.view());centers=[cfg['predicted_encounter']['site']]if tick in(363,364)else[q['delivery_site']for q in s.geometry['joint_names'].values()]
  for q in centers:m['windows'].append({'tick':tick,'center':q,'Moore27':[s.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
  m.update(last_complete_tick=s.tick,requests=s.receipts(),elapsed_seconds=time.monotonic()-start);put(a.out/'MEASUREMENTS.json',m)
 final=a.out/'T415.deetsnap.gz';storage=s.save(final);m['snapshots'].append({'path':final.name,'sha256':sha(final),'tick':s.tick,'storage':storage});m.update(status='MEASURED',final_physical=physical(s.world),parent_physical_after=physical(parent.world),parent_sha256_after=sha(pp));m['parent_unchanged']=before==m['parent_physical_after']and psha==m['parent_sha256_after']
 baseline=json.loads((ROOT/'resultados/integracion/ENS_L01_RESTORE_NEW_QUERY/MEASUREMENTS.json').read_text());m['baseline_comparison']={'final_physical_equal':m['final_physical']==baseline['final_physical'],'receipts_equal':m['requests']==baseline['requests']};put(a.out/'MEASUREMENTS.json',m)
 print(json.dumps({'id':case['id'],'parent_unchanged':m['parent_unchanged'],'comparison':m['baseline_comparison'],'selected_sites':sum(r['selected']for r in rows),'word415':{k:v['delivery_site']for k,v in m['frames'][-1]['joint'].items()}}),flush=True)
if __name__=='__main__':main()
