"""Family 2 discovery: physical probes in descendant forks; MAIN is never probed.

Not autonomous introspection: a scientist/external interface creates a deep
fork of native history, runs its local probe, while MAIN and the independent
environment advance by the same duration. No future environment rollout is
computed or returned. Forks are never merged. Sampling ticks are fixed.
"""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from predictor import *

root=Path(sys.argv[1]);log=AuditLog(root/'PREDICCIONES_ASSISTED_DISCOVERY.jsonl');rows=[]
s=PredictorSession(build(),PersistentTransportHabitat(True,80));s.experience_past_results();last=34
for at in (34,292,552,812):
    if at>34:
        s.world.run_until(at);s.habitat.advance(at,[]);past=s.habitat.actual_past_result(at)
        key='A' if past['arrived'] else 'B';r=s.world.submit('sensor.'+key,0,at);s.accessible.append({'sensor':key,'tick':at,'load':0,'source_past_result_tick':at,'reference_branch':False,'receipt_id':r.id});s.world.advance();s.habitat.advance(at+1,[])
    before=physical(s.world);f=s.fork();target=s.world.runtime.current_tick+30;em=f.predict([target],log,'ASSISTED_DISCOVERY_'+str(at))
    s.world.advance(3);s.habitat.advance(s.world.runtime.current_tick,[])
    # Only the observed port emission is copied to the EXTERNAL audit/session;
    # no RAW, clock, carrier or relation returns to MAIN.
    em['modality']='DIAGNOSTIC_PHYSICAL_PROBE_IN_DESCENDANT';s.emissions.append(em)
    ev=s.evaluate(target,log,'ASSISTED_DISCOVERY_'+str(at));row={'sample_tick':at,'mother_panel':panel(s.world),'offspring_emission':em,'evaluation':ev,'raw_main_before_probe':before,
        'main_received_no_probe':True,'no_fork_fusion':True};rows.append(row)
s.save(root/'checkpoints'/'ASSISTED_MAIN_DISCOVERY_FINAL.deetsnap');atomic_json(root/'resultados'/'ASSISTED_DISCOVERY.json',{'rows':rows})
print(json.dumps([{'sample_tick':r['sample_tick'],'mother_delta':r['mother_panel']['delta'],'prediction':r['offspring_emission']['prediction_set'],'error':r['evaluation']['absolute_error_binary']} for r in rows]))
