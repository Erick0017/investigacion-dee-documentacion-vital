import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import dee_thinking as d
from laboratorio import *
from supervision import atomic_json

def gate(w):
    g=d.inspect_write_gate(w.runtime,w.view('body').spec.b,True)
    return {k:getattr(g,k) for k in ('local_clock','n_active','period','k','phase_remainder','survives','protected','ordinary_increment_eligible','state','semantic') if hasattr(g,k)}

def main(root):
    e=CaseEvidence(root,'DISCOVERY_02_INTERFACES',{'method':'same relative body, physically transient input states','states':[3,1000],'feedback_delays':[255],'no_clock_edit':True,'not_holdout':True})
    rows=[]
    for state in (1,3,1000):
        for arm in ('return','no_return'):
            w=make_body(event_state=state);admitted=body_experience(w,['A','B']);first,w=body_probe(w,in_fork=False)
            native_before=body_panel(w);target=w.runtime.current_tick+255
            pending=w.submit('E_B',0,target).id if arm=='return' else None;w.run_until(target)
            before=body_panel(w);g=gate(w);site=next(i.channel.injection_site for i in w.interfaces if i.name=='E_B');port=reading(w.runtime.observe(site));w.advance();after=body_panel(w);w.advance(8);second,f=body_probe(w)
            row={'state':state,'arm':arm,'initial_receipts':admitted,'first_response':first['response'],'initial_delta':native_before['delta'],'before':before,'gateB':g,'input_port_before':port,'after':after,'second_response':second['response'],'retained_delta':body_panel(w)['delta'],'feedback_receipt':receipt(w.runtime.receipt(pending)) if pending else None};rows.append(row)
    e.finish(rows);atomic_json(Path(root)/'resultados/DISCOVERY_02.json',rows)
    print(json.dumps([{'state':x['state'],'arm':x['arm'],'delta0':x['initial_delta'],'delta1':x['retained_delta'],'gateB':x['gateB'],'feedback':x['feedback_receipt'],'response':x['second_response']['direction'],'port':x['input_port_before']} for x in rows],indent=2))

if __name__=='__main__':main(sys.argv[1])
