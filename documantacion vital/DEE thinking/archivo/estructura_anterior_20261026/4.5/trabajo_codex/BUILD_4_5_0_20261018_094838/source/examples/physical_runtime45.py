"""Direct physics: no cognitive recipe, no learned answer or hidden source."""
import json
import dee_thinking as d

def main():
    w=d.Runtime(11)
    assert w.current_tick==0 and w.metrics().raw_support==0
    c=d.ChannelSpec();c.name='local';c.injection_site=d.Coordinate(3,4,5)
    c.state=101;c.direction=d.Direction(1,0,0);c.semantic=1
    c.allow_experience=True;c.allow_probe=True;w.register_channel(c)
    request=w.experience('local',0,17)
    raw=w.raw_copy();clocks=w.clock_copy();w.observe(c.injection_site)
    assert raw==w.raw_copy() and clocks==w.clock_copy()
    w.advance(3)
    rows=[]
    for x in range(11):
        o=w.observe(d.Coordinate(x,4,5));r=o.record
        if o.raw:
            rows.append({'site':[x,4,5],'raw':str(o.raw),'clock':str(o.clock),
                'state':r.state,'s_reg':r.s_reg,'semantic':r.semantic,'direction':[r.dx,r.dy,r.dz]})
    before=(w.current_tick,w.raw_copy(),w.clock_copy())
    branch=w.fork();branch.advance(2)
    assert before==(w.current_tick,w.raw_copy(),w.clock_copy())
    receipt=w.receipt(request.id)
    print(json.dumps({'provenance':'INSTRUMENTO','version':d.__version__,
        'empty_runtime_cognitive_support':0,'receipt':str(receipt.status),
        'requested_tick':receipt.requested_tick,'effective_tick':receipt.effective_tick,
        'main_tick':w.current_tick,'diagnostic_branch_tick':branch.current_tick,
        'passive_observer_preserved_state':True,'main_unchanged_by_branch':True,
        'observations':rows},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
