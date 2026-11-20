"""Narrow management regression on an explicit diagnostic fork, never MAIN."""
from pathlib import Path
import argparse,json,sys
def main():
    p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.system));from app.lives import Store,MutationRecordedError;from app.native_tools import physical,observe,moore27,atomic_json;from app.process_control import protect_current,current_resources;protect_current();a.out.mkdir(parents=True,exist_ok=False);store=Store(a.system);parent=store.status('E1_SOCIAL_11');life='FALLO_EVOLUCION_11';store.fork('E1_SOCIAL_11',life,kind='DIAGNOSTIC_COPY');reached={}
    def attempt(actor):
        receipt=actor.world.probe('TM.quantity.reader',7,3220);actor.run_until(3221);reached.update(physical=physical(actor.world),observation=observe(actor.world,actor.two_memory.geometry['center']),Moore27=moore27(actor.world,actor.two_memory.geometry['center']),request_id=int(receipt.id));raise ValueError('Explicit diagnostic exception after native evolution, not a scientific incorrect answer')
    try:store.mutate(life,'DIAGNOSTIC_FAILURE_AFTER_NATIVE_ADVANCE',attempt,{'diagnostic_only':True});raise AssertionError('Expected explicit failure did not occur')
    except MutationRecordedError as error:recorded=error.recorded_operation
    record,actor=Store(a.system).load(life);after=physical(actor.world);check=after==reached['physical']and after['tick']==3221 and Store(a.system).status('E1_SOCIAL_11')['physical']==parent['physical']and record['operations'][-1]['kind']=='FAILED_DIAGNOSTIC_FAILURE_AFTER_NATIVE_ADVANCE'
    atomic_json(a.out/'RESULTADO.json',{'schema':'DCS1.1.failure_after_native_evolution.v1','diagnostic_life':life,'parent':parent,'reached_before_exception':reached,'loaded_after_exception':after,'recorded_error':recorded,'failed_operation_preserved':check,'parent_unchanged':True,'RAW_clock_edits':False,'source':'Exact installed code from extracted candidate02; callback only provides a declared probe and advances native time before injecting a host exception.','resources':current_resources()})
    if not check:raise AssertionError('Native future was lost after exception')
    print(json.dumps({'failed_future_preserved':True,'tick':after['tick'],'parent_unchanged':True}))
if __name__=='__main__':main()
