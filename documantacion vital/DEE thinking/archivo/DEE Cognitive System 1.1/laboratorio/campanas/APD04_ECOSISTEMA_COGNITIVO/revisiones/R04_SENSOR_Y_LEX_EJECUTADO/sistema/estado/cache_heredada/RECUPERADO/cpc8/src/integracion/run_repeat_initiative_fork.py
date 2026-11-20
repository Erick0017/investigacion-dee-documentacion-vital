"""Causal question cut/sham for the second unchanged-geometry opportunity."""
import argparse,json,shutil,sys,time
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from integracion.repeat_initiative_e1 import RepeatInitiativeE1Session
from integracion.relational_pair import physical
from integracion.run_longitudinal_e1 import put,sha
from dee_thinking import _native as d

def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();cfg=json.loads(a.config.read_text(encoding='utf8'));case=next(c for c in cfg['cases']if c['id']==a.case_id);a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pp=ROOT/'resultados/integracion'/cfg['parent_id']/cfg['parent_snapshot'];psha=sha(pp);parent=RepeatInitiativeE1Session.load(pp);parent.run_until(341);before=physical(parent.world);edits=[];rows=[]
 for branch in parent.geometry['initiative']['branches']:
  q=branch['request_probe_site'];pre=parent.observe(q);edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*q);edit.raw=0 if case['mode']=='cut'else int(pre['raw']);edit.label='SECOND_QUESTION_'+case['mode'];edits.append(edit);rows.append({'site':q,'pre':pre,'requested_raw':str(edit.raw),'clock_edit':None})
 child=parent.world.diagnostic_fork(edits,True);state=deepcopy(parent.state)
 for key in('mode','quantity','initiative'):state[key]=deepcopy(getattr(parent,key).state)
 s=RepeatInitiativeE1Session(child,parent.geometry,state,parent.identifier+'.'+case['id'])
 for row in rows:row['post']=s.observe(row['site'])
 paths=[Path(__file__)]+[ROOT/'src/integracion'/n for n in('repeat_initiative_e1.py','initiative_use_e1.py','initiative_e1.py','contact_renewal_e1.py','longitudinal_e1.py','complete_e1.py','quantity_core.py','relational_guarded_v2.py','relational_social.py','relational_ensemble.py','relational_pair_v2.py','relational_pair.py')]+[ROOT/'src/iniciativa_accion/solicitud.py',ROOT/'src/iniciativa_accion/return_use.py',ROOT/'src/comunicacion/mode_communication.py',ROOT/'src/relaciones/mode_reference.py'];outsrc=a.out/'executed_source';outsrc.mkdir()
 for path in paths:shutil.copyfile(path,outsrc/path.name)
 m={'schema':'CPC8R.repeatInitiativeE1.fork.measurements.v1','case':case,'configuration_sha256':sha(a.config),'source_sha256':{x.name:sha(x)for x in paths},'parent':{'path':str(pp.relative_to(ROOT)),'sha256':psha,'tick':340},'preparations':0,'continuations':0,'diagnostic_forks':1,'edited_sites':rows,'frames':[],'repeat_initiative_observations':[],'snapshots':[],'status':'RUNNING','host_RAW_clock_edits_on_MAIN':[]}
 for tick in(344,345,348,349,353,354,356,357,358,405,411,415,428,436,472,478,539,549):
  s.run_until(tick);m['frames'].append(s.view())
  if tick<=358:m['repeat_initiative_observations'].append(s.repeat_view(moore=True))
  m.update(last_complete_tick=s.tick,requests=sorted(s.receipts(),key=lambda r:r['id']),elapsed_seconds=time.monotonic()-start);put(a.out/'MEASUREMENTS.json',m)
 path=a.out/'T549.deetsnap.gz';storage=s.save(path);m['snapshots'].append({'path':path.name,'sha256':sha(path),'tick':549,'physical':physical(s.world),'storage':storage});baseline=json.loads((pp.parent/'MEASUREMENTS.json').read_text(encoding='utf8'));m.update(status='MEASURED',final_physical=physical(s.world),baseline_comparison549={'full_physical_equal':physical(s.world)==baseline['final_physical'],'native_receipts_equal':[r['receipt']for r in sorted(s.receipts(),key=lambda r:r['id'])]==[r['receipt']for r in baseline['requests']]},parent_file_unchanged=sha(pp)==psha,unmodified_parent_physical_equal=physical(parent.world)==before);put(a.out/'MEASUREMENTS.json',m)
 print(json.dumps({'id':case['id'],'comparison':m['baseline_comparison549'],'use357':next(r['return_use']for r in m['repeat_initiative_observations']if r['tick']==357)}),flush=True)
if __name__=='__main__':main()
