"""Directed reproduction from public code, a clean directory and saved state."""
import argparse,json,sys,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from predictor import *


def main(package,output):
    package=Path(package).resolve();output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True);log=AuditLog(output/'PREDICCIONES.jsonl')
    # Fresh reserved geometry: actual past-result acquisition, not terminal load.
    s=PredictorSession(build((22,20,24),3),PersistentTransportHabitat(False));s.experience_past_results();em=s.predict([70],log,'FRESH_REPRODUCTION',11)
    assert em['emission_tick']<70;assert em['prediction_set']==[False];s.save(output/'EMITTED_T37.deetsnap')
    t=PredictorSession.load(output/'EMITTED_T37.deetsnap');assert physical(t.world)==physical(s.world)
    live=t.predict_passive([80],log,'FRESH_RESTORED_LIVE');a=s.evaluate(70,log,'FRESH_REPRODUCTION');b=t.evaluate(70,log,'FRESH_RESTORED_PENDING');assert physical(s.world)==physical(t.world)
    c=t.evaluate(80,log,'FRESH_RESTORED_LIVE');assert a['absolute_error_binary']==0 and b['absolute_error_binary']==0 and c['absolute_error_binary']==0
    # Continue an acquired maternal MAIN, without reconstructing its history.
    source=package/'checkpoints'/'ASSISTED_R0_PAIRED_RESULTS_FINAL.deetsnap';u=PredictorSession.load(source);before=physical(u.world);v=u.fork();target=u.world.runtime.current_tick+30
    new=v.predict([target],log,'ACQUIRED_CONTINUATION',modality='DIAGNOSTIC_PHYSICAL_PROBE_IN_DESCENDANT');assert physical(u.world)==before
    u.world.advance(3);u.habitat.advance(u.world.runtime.current_tick,[]);u.emissions.append(new);e=u.evaluate(target,log,'ACQUIRED_CONTINUATION');u.save(output/'CONTINUED_ACQUIRED_MAIN.deetsnap')
    result={'runtime_version':d.__version__,'kernel':d.kernel_identity(),'working_directory':str(Path.cwd()),'module_path':d.__file__,
        'fresh_physical_output':em['physical_output'],'fresh_error':a['absolute_error_binary'],'restore_error':c['absolute_error_binary'],
        'continued_acquired_output':new['physical_output'],'continued_error':e['absolute_error_binary'],'continued_tick':u.world.runtime.current_tick,
        'all_technical_asserts_completed':True,'private_workspace_dependency':False,'terminal_snapshot_used_as_answer':False}
    assert e['absolute_error_binary']==0;atomic_json(output/'REPRODUCTION_CHECK.json',result);print(json.dumps(result))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--package',required=True);p.add_argument('--output',required=True);a=p.parse_args();main(a.package,a.output)
