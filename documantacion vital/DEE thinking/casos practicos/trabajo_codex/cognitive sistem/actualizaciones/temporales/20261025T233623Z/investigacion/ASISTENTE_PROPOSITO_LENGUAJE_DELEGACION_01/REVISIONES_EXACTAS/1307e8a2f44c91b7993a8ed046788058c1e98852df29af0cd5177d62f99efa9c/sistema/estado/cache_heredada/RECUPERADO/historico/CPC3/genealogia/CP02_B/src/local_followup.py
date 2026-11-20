import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from predictor import *

root=Path(sys.argv[1]);rows=[]
for use_probe in (False,True):
    for at in (101,292):
        s=PredictorSession.create();s.present('AB')
        if use_probe:
            s.world.probe('body.common_query',7,34);s.world.run_until(37)
        s.world.run_until(at)
        gates=[]
        for key in ('a','b'):
            g=d.inspect_write_gate(s.world.runtime,getattr(s.world.view('body').spec,key),True)
            gates.append({'key':key,'clock':g.local_clock,'n_active':g.n_active,'k':g.k,'period':g.period,'remainder':g.phase_remainder,'branch':g.branch})
        before=panel(s.world);r=s.world.submit('sensor.B',0,at);s.world.advance();after=panel(s.world)
        q=s.world.probe('body.common_query',7,s.world.runtime.current_tick);s.world.advance(3)
        rows.append({'probe_before':use_probe,'event_tick':at,'before':before,'gate_before':gates,'receipt':receipt(s.world.runtime.receipt(r.id)),
                    'after':after,'probe_receipt':receipt(s.world.runtime.receipt(q.id)),'output':observation(s.world.observe('body','comparator'))})
atomic_json(root/'resultados'/'FOLLOWUP_DISCOVERY.json',{'rows':rows})
print(json.dumps([{'probe_before':r['probe_before'],'tick':r['event_tick'],'delta_before':r['before']['delta'],'delta_after':r['after']['delta'],'receipt':r['receipt']['status'],'probe':r['probe_receipt']['status'],'gate':r['gate_before']} for r in rows]))
