"""Bounded diagnostic branches separate occupied-reader access from representation."""
import argparse,json,shutil,sys,time
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from integracion.relational_guarded_v2 import GuardedV2Session
from integracion.relational_pair import physical,move
from integracion.run_longitudinal_e1 import put,sha
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt

def gate(s,q):
 g=d.inspect_write_gate(s.world.runtime,d.Coordinate(*q),True)
 return{key:getattr(g,key)for key in('absolute_tick','local_clock','center_available','n_active','hadron','rule_value','survives_material_rule','semantic_protected','write_protected','k','period','phase_remainder','ordinary_increment_condition','branch','demux_status')}

def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();cfg=json.loads(a.config.read_text(encoding='utf8'));case=next(x for x in cfg['cases']if x['id']==a.case_id);a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pp=ROOT/'resultados/integracion'/cfg['parent_id']/cfg['snapshot'];psha=sha(pp);parent=GuardedV2Session.load(pp);parent_phys=physical(parent.world)
 child=parent.world.diagnostic_fork([],True);state=deepcopy(parent.state);state['mode']=deepcopy(parent.mode.state);s=GuardedV2Session(child,parent.geometry,state,parent.identifier+'.'+case['id']);body=s.geometry['body'];aux=None;aux_receipt=None
 paths=[Path(__file__)]+[ROOT/'src/integracion'/n for n in('relational_guarded_v2.py','relational_social.py','relational_ensemble.py','relational_pair_v2.py','relational_pair.py')]+[ROOT/'src/comunicacion/mode_communication.py',ROOT/'src/relaciones/mode_reference.py'];src=a.out/'executed_source';src.mkdir()
 for path in paths:shutil.copyfile(path,src/path.name)
 m={'schema':'CPC8R.orderAccess.diagnostic.measurements.v1','case':case,'configuration_sha256':sha(a.config),'source_sha256':{x.name:sha(x)for x in paths},'parent':{'path':str(pp.relative_to(ROOT)),'sha256':psha,'tick':415},'preparations':0,'continuations':0,'diagnostic_forks':1,'frames':[],'windows':[],'gates':[],'edits':[],'snapshots':[],'host_RAW_clock_edits_on_MAIN':[],'status':'RUNNING','alternative_requests':[],'interpretation_modality':'AUDITOR_DIAGNOSTIC_ONLY_NOT_MAIN_PERCEPTION'}
 if case['new_events']:
  for letter,tick in zip(case['new_events'],(469,470)):s.input('order.'+letter,3,tick,origin='NEW_CURRENT_EVENT_ON_OLD_SENSOR_NO_TEACHING_MAP')
 s.input('order.read',7,472,'probe','EXPLICIT_COMMON_ORDER_READER_LATE')
 for q in s.geometry['joint_names'].values():s.input(q['query_port'],11,479,'probe','OLD_COMPOSITE_WORD_QUERY_AFTER_NEW_EVENTS_NO_RETEACHING')
 if case['operation']=='alternative_z':
  q=move(body['center'],(0,0,-1));channel=d.ChannelSpec();channel.name='AUDITOR.order.alternative_z';channel.injection_site=d.Coordinate(*q);channel.direction=d.Direction(0,0,1);channel.state=1;channel.semantic=1;channel.allow_experience=True;channel.allow_probe=True;before=physical(s.world);s.world.runtime.register_channel(channel);m['inert_channel_registration']={'site':q,'direction':[0,0,1],'before':before,'after':physical(s.world),'physical_unchanged':before==physical(s.world),'modality':'DIAGNOSTIC_INTERFACE_NOT_MAIN'};aux=s.world.runtime.probe(channel.name,469,7);aux_receipt=int(aux.id);m['alternative_requests'].append({'id':aux_receipt,'port':channel.name,'payload':7,'requested_tick':469,'call_tick':s.tick})
 for tick in tuple(range(468,478))+(479,481,482):
  s.run_until(tick)
  if tick==472 and case['operation']in('cut_reader','sham_reader'):
   q=body['emission'];pre=s.observe(q);before=physical(s.world);edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*q);edit.raw=0 if case['operation']=='cut_reader'else int(pre['raw']);edit.label='ASSISTED_READER_ACCESS_'+case['operation'];child=s.world.diagnostic_fork([edit],True);state=deepcopy(s.state);state['mode']=deepcopy(s.mode.state);s=GuardedV2Session(child,s.geometry,state,s.identifier);m['edits'].append({'tick':472,'site':q,'pre':pre,'post':s.observe(q),'clock_edit':None,'raw_requested':str(edit.raw),'unmodified_fork_parent_physical':before})
  m['frames'].append(s.view())
  for q in body.values():
   m['windows'].append({'tick':tick,'center':q,'Moore27':[s.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
  for key in('center','emission'):m['gates'].append({'tick':tick,'role':key,'site':body[key],'gate':gate(s,body[key])})
  if aux_receipt is not None:m['alternative_requests'][0]['receipt']=exact_receipt(s.world.runtime.receipt(aux_receipt))
  if tick in(470,472,475,482):
   path=a.out/('T'+str(tick)+'.deetsnap.gz');storage=s.save(path);m['snapshots'].append({'path':path.name,'tick':tick,'sha256':sha(path),'physical':physical(s.world),'storage':storage})
  m.update(last_complete_tick=s.tick,requests=sorted(s.receipts(),key=lambda r:r['id']),elapsed_seconds=time.monotonic()-start);put(a.out/'MEASUREMENTS.json',m)
 m.update(status='MEASURED',final_physical=physical(s.world),parent_file_unchanged=sha(pp)==psha,parent_runtime_unchanged=physical(parent.world)==parent_phys)
 if case.get('reference'):
  baseline=json.loads((ROOT/'resultados/integracion'/case['reference']/'MEASUREMENTS.json').read_text(encoding='utf8'));m['prior_continuation_comparison']={'full_physical_equal':m['final_physical']==baseline['final_physical'],'native_receipts_equal':[r['receipt']for r in m['requests']]==[r['receipt']for r in sorted(baseline['requests'],key=lambda r:r['id'])]}
 put(a.out/'MEASUREMENTS.json',m);print(json.dumps({'id':case['id'],'reader':[(r['port'],r['receipt']['status'])for r in m['requests']if r['port']=='order.read'],'alternative':m['alternative_requests'],'comparison':m.get('prior_continuation_comparison'),'center470':next(f['body']['center']for f in m['frames']if f['tick']==470),'emission475':next(f['body']['emission']for f in m['frames']if f['tick']==475)}),flush=True)
if __name__=='__main__':main()
