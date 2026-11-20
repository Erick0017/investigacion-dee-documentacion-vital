"""A separate process continues the same contact memory through later learning.

Its queued future experiences and renewed query are preserved by the snapshot.
The final technical reference is opened only after native evolution finishes.
"""
import argparse,hashlib,json,sys,time
from pathlib import Path
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(a.parent/'executed_source/src'))
    from relaciones.contact_consequence import ContactSession,physical
    start=time.monotonic();source=a.parent/'T83.deetsnap.gz';s=ContactSession.load(source);before=physical(s.world);s.run_until(160);actual=physical(s.world);receipts=s.receipts();captures=[r for r in s.state['captures'] if r['tick']>83]
    # No expected/target/state reference was opened before the trajectory ended.
    reference=ContactSession.load(a.parent/'FINAL_T160.deetsnap.gz');expected=physical(reference.world)
    result={'schema':'CPC8.contact_consequence.restore.v1','modality':'TECHNICAL_REPRODUCTION_OF_CONTINUATION','preparations':0,'continuations':1,'diagnostic_forks':0,
        'parent':{'snapshot':str(source),'sha256':sha(source),'physical':before},'new_external_participant_inputs':[],
        'queued_inputs_and_protocols_preserved':True,'actual_final':actual,'reference_final':expected,'RAW_clocks_tick_equal':actual==expected,'receipts_equal':receipts==reference.receipts(),
        'continued_captures':captures,'source_sha256':sha(a.parent/'executed_source/src/relaciones/contact_consequence.py'),'elapsed_seconds':time.monotonic()-start,'status':'EXECUTED'}
    (a.out/'MEASUREMENTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'physical_equal':actual==expected,'receipts_equal':result['receipts_equal']}))
if __name__=='__main__':main()
