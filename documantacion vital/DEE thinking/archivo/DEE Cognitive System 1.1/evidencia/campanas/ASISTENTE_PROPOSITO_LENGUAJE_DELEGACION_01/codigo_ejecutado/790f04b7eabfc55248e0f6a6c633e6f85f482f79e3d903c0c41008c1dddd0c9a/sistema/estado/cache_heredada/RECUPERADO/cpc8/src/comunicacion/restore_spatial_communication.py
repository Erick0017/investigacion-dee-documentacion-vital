"""Independent-process spatial restore, optionally without the host teaching journal."""
import argparse,hashlib,json,os,shutil,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.pending');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(t,p)
def main():
 p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--reference',type=Path,required=True);p.add_argument('--prune-journal',action='store_true');p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);bundle=a.out/'executed_source'
 for f in ['src/relaciones/mode_reference.py','src/relaciones/spatial_gradient.py','src/relaciones/spatial_reference.py','src/comunicacion/spatial_communication.py','src/comunicacion/restore_spatial_communication.py']:
  target=bundle/f;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,target)
 sys.path.insert(0,str(bundle/'src'));from comunicacion.spatial_communication import SpatialCommunicationSession
 from relaciones.mode_reference import physical
 from dee_thinking.consolidated import exact_receipt
 start=time.monotonic();s=SpatialCommunicationSession.load(a.parent);assert s.tick==200;initial=physical(s.world);old=len(s.state['social_captures']);allids=[x['id']for x in s.receipts()];prune=None
 if a.prune_journal:
  old=0;count=len(s.state['requests']);s.state['requests']=[x for x in s.state['requests']if x['kind']=='probe'];s.state['social_captures']=[]
  for mode in s.modes.values():mode.state['requests']=[];mode.state['captures']=[]
  pruned=a.out/'HOST_JOURNAL_PRUNED_T200.deetsnap.gz';s.save(pruned);s=SpatialCommunicationSession.load(pruned);prune={'removed_host_nonquery_entries':count-len(s.state['requests']),'old_readout_caches_removed':True,'physical_unchanged':initial==physical(s.world),'snapshot_sha256':sha(pruned),'native_operational_history_retained':'Provenance remains in native snapshot; participant methods do not inspect it to respond.'}
 s.run_until(243);end=physical(s.world);native_receipts=[exact_receipt(s.world.runtime.receipt(i))for i in allids];newcaptures=s.state['social_captures'][old:]
 # Auditor reads expected endpoint only after native execution.
 expected=SpatialCommunicationSession.load(a.reference);ref=physical(expected.world);expectedids=[x['id']for x in expected.receipts()];checks={'RAW_clocks_tick':end==ref,'native_receipts_by_original_ids':native_receipts==[exact_receipt(expected.world.runtime.receipt(i))for i in expectedids],'channels':sorted(s.world.runtime.channel_names)==sorted(expected.world.runtime.channel_names),'protocol_count':len(s.world.protocols)==len(expected.world.protocols),'external_operations':list(s.world.external_operations)==list(expected.world.external_operations),'new_social_readouts':newcaptures==[x for x in expected.state['social_captures']if x['tick']>200]}
 path=a.out/'T243_RESTORED.deetsnap.gz';storage=s.save(path)
 m={'schema':'CPC8R.spatial_communication.restore.v1','case':{'id':a.out.name,'host_journal_pruned':a.prune_journal},'modality':'TECHNICAL_REPRODUCTION_OF_CONTINUATION','preparations':0,'diagnostic_forks':0,'continuations':1,'scientific_replica':False,'parent':{'snapshot':str(a.parent),'sha256':sha(a.parent),'tick':200},'reference_after_execution':{'snapshot':str(a.reference),'sha256':sha(a.reference)},'source_sha256':{p.relative_to(bundle).as_posix():sha(p)for p in bundle.rglob('*.py')},'new_inputs_after_restore':[],'initial':initial,'final':end,'reference_final':ref,'checks':checks,'journal_pruning':prune,'status':'PASS'if all(checks.values())else'FAIL','native_receipts':native_receipts,'social_captures_after_restore':newcaptures,'snapshot':{'path':path.name,'storage':storage},'elapsed_seconds':time.monotonic()-start,'full_operational_serialization_byte_equivalence':None}
 put(a.out/'MEASUREMENTS.json',m);print(json.dumps({'checks':checks,'status':m['status'],'pruning':prune}))
if __name__=='__main__':main()
