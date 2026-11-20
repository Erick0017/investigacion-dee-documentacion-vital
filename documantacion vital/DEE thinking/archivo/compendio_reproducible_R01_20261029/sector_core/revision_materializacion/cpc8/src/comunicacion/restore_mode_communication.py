"""Independent-process restore; expected trajectory loaded only after execution."""
import argparse,hashlib,json,os,shutil,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.pending');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(t,p)
def main():
 p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--reference',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);bundle=a.out/'executed_source'
 for f in ['src/relaciones/mode_reference.py','src/comunicacion/mode_communication.py','src/comunicacion/restore_mode_communication.py']:
  q=bundle/f;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,q)
 sys.path.insert(0,str(bundle/'src'));from comunicacion.mode_communication import ModeCommunicationSession
 from relaciones.mode_reference import physical
 start=time.monotonic();s=ModeCommunicationSession.load(a.parent);assert s.tick==200;initial=physical(s.world);old=len(s.state['social_captures']);s.run_until(235);end=physical(s.world);requests=s.receipts()
 # Only after native target has run does the auditor read the reference.
 expected=ModeCommunicationSession.load(a.reference);ref=physical(expected.world)
 checks={'RAW_clocks_tick':end==ref,'all_receipts':requests==expected.receipts(),'channels':sorted(s.world.runtime.channel_names)==sorted(expected.world.runtime.channel_names),'protocol_count':len(s.world.protocols)==len(expected.world.protocols),'external_operations':list(s.world.external_operations)==list(expected.world.external_operations),'social_readouts':s.state['social_captures']==expected.state['social_captures']}
 path=a.out/'T235_RESTORED.deetsnap.gz';storage=s.save(path)
 m={'schema':'CPC8R.mode_communication.restore.v1','case':{'id':a.out.name},'modality':'TECHNICAL_REPRODUCTION_OF_CONTINUATION','preparations':0,'diagnostic_forks':0,'continuations':1,'scientific_replica':False,'parent':{'snapshot':str(a.parent),'sha256':sha(a.parent),'tick':200},'reference_after_execution':{'snapshot':str(a.reference),'sha256':sha(a.reference)},'source_sha256':{p.relative_to(bundle).as_posix():sha(p) for p in bundle.rglob('*.py')},'new_inputs_after_restore':[],'initial':initial,'final':end,'reference_final':ref,'checks':checks,'status':'PASS' if all(checks.values()) else 'FAIL','requests':requests,'social_captures_after_restore':s.state['social_captures'][old:],'snapshot':{'path':path.name,'storage':storage},'elapsed_seconds':time.monotonic()-start,'full_operational_serialization_byte_equivalence':None,'scope':'Exact physical, receipt, channel, protocol-count, external-operation and published response continuation checks; wrapper snapshot metadata byte identity is not asserted.'}
 put(a.out/'MEASUREMENTS.json',m);print(json.dumps({'checks':checks,'status':m['status']}))
if __name__=='__main__':main()
