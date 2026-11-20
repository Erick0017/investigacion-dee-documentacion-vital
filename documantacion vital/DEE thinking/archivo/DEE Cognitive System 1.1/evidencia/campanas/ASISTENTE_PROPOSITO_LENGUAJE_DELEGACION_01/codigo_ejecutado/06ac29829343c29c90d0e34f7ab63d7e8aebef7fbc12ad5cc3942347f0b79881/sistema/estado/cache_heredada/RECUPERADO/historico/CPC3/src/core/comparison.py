"""Physical directional comparison components; no evaluator feeds this module.

Both represented values enter as independently encoded physical events. The
v27 directional reducer, not Python subtraction, composes their directions.
This module does not claim that a caller-supplied expectation is a prediction
emitted by a different body. The integration must preserve that physical link.
"""
from __future__ import annotations

from pathlib import Path
import json
import dee_thinking as d


def coordinate(q):
    return d.Coordinate(*(int(x) for x in q))


def plus(q, direction, steps=1, n=47):
    return tuple((int(q[j])+int(direction[j])*steps)%n for j in range(3))


def observed(o):
    r=o.record
    return {"tick":int(o.tick),"coordinate":[o.coordinate.x,o.coordinate.y,o.coordinate.z],
            "RAW":int(o.raw),"clock":int(o.clock),"state":int(r.state),
            "semantic":int(r.semantic),"load":int(r.s_reg),
            "direction":[r.dx,r.dy,r.dz],"active":bool(r.state>0 and r.semantic!=5)}


def physical_comparison_code(expected: int, consequence: int):
    """Fixed injective role codecs over the finite signed binary domain.

    The two signs are independently encoded. This function never compares
    them and does not calculate error or the resulting direction.
    """
    if expected not in (-1,1) or consequence not in (-1,1):
        raise ValueError("The directional comparator publishes only {-1,+1}")
    return (expected,1,0),(-consequence,0,1)


def make_interface(name,site,direction,state=1,semantic=1):
    i=d.InterfaceSpec();i.name=name;c=d.ChannelSpec();c.name=name
    c.injection_site=coordinate(site);c.direction=d.Direction(*direction)
    c.state=state;c.semantic=semantic;c.allow_experience=True;c.allow_probe=True
    i.channel=c;return i


def make_placement(site,load,direction,state=1,semantic=1,clock=0,role="prepared_resource"):
    p=d.InitialPlacement();p.site=coordinate(site)
    p.raw=d.pack_record(state,load,*direction,semantic);p.clock=clock;p.role=role
    return p


def prepare_comparison(expected,consequence,*,loads=(30,100),hub=(23,23,23),
                       arrival_tick=8,expectation_tick=0,consequence_tick=4,n=47,
                       omit=None,phase_miss=0,context_payloads=None):
    """Prepare a finite event experiment and its optional physical branch use.

    Expectation exists physically before consequence is submitted. Both
    participants follow their role codec trajectories to one fixed hub.
    Optional context packets are prepared before T0, never selected after
    reading the comparison. They meet distinct native branch products.
    """
    e,c=physical_comparison_code(expected,consequence)
    if arrival_tick<=max(expectation_tick,consequence_tick):
        raise ValueError("All transmissions need positive propagation time")
    r=d.OrganizationRecipe.research(n,[],0)
    r.execution=d.TickOptions(d.Backend.LAZY,1)
    interfaces=[]
    es=plus(hub,e,-(arrival_tick-expectation_tick),n)
    cs=plus(hub,c,-(arrival_tick-consequence_tick+phase_miss),n)
    interfaces += [make_interface("expectation",es,e),make_interface("consequence",cs,c)]
    r.interfaces=interfaces
    s=d.OrganizationSpec();s.id="comparison";s.recipe_id="directional_comparison.cpc3.v1"
    s.ports={"meeting":coordinate(hub)}
    # Comparison output can be used by a later physical query. These three
    # branches are declared geometry, not selected or repaired by the host.
    branch_targets={}
    placements=[]
    if context_payloads is not None:
        for k,dx in [("equal",0),("higher",1),("lower",-1)]:
            dr=(dx,1,1);target=plus(hub,dr,4,n)
            branch_targets[k]=target
            mediator=(1,-1,0) if dx<=0 else (-1,-1,0)
            source=plus(target,mediator,-(arrival_tick+4),n)
            placements.append(make_placement(source,int(context_payloads[k]),mediator,
                                              role="prepared_branch_information"))
            s.ports[k+"_information"]=coordinate(target)
    r.placements=placements;r.organizations=[s]
    w=d.OrganizationalWorld.create(r)
    metadata={"domain":"signed binary values, directional complementary role codecs",
              "dimension":n,"hub":list(hub),"arrival_tick":arrival_tick,
              "expectation_tick":expectation_tick,"consequence_tick":consequence_tick,
              "expected_input":expected,"consequence_input":consequence,
              "role_directions":{"expectation":list(e),"consequence":list(c)},
              "source_sites":{"expectation":list(es),"consequence":list(cs)},
              "loads":list(loads),"omit":omit,"phase_miss":phase_miss,
              "branch_targets":{k:list(v) for k,v in branch_targets.items()},
              "host_modality":"EXPERIENCE_PROTOCOL; independent fixed role codecs, no error input"}
    return w,metadata


def decode_comparison(o):
    """External presentation of the current native result; never feedback."""
    r=o.record
    if not(r.state>0 and r.semantic!=5):return {"state":"NO_NATIVE_PRODUCT","relation":None}
    dr=(r.dx,r.dy,r.dz)
    if dr[1:]!=(1,1):return {"state":"OUTSIDE_MATCHED_PRODUCT_DOMAIN","relation":None}
    return {"state":"MATCHED_DIRECTIONAL_PRODUCT","relation":
            "same" if dr[0]==0 else "expected_positive_consequence_negative" if dr[0]>0
            else "expected_negative_consequence_positive"}


def run_comparison(spec,output=None):
    w,m=prepare_comparison(**spec)
    trace=[];receipts=[];scheduled=set();horizon=m["arrival_tick"]+7
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        w.save_snapshot(str(output/"T0.deetsnap"))
    while w.runtime.current_tick<=horizon:
        t=w.runtime.current_tick
        for name,j in [("expectation",0),("consequence",1)]:
            at=m[name+"_tick"]
            if t==at and name not in scheduled and m["omit"]!=name:
                x=w.submit(name,m["loads"][j],at);scheduled.add(name);receipts.append(x.id)
        pts={"meeting":coordinate(m["hub"])}
        pts.update({k:coordinate(q) for k,q in m["branch_targets"].items()})
        trace.append({"tick":t,"sites":{k:observed(w.runtime.observe(q)) for k,q in pts.items()}})
        if t==m["arrival_tick"] and output:w.save_snapshot(str(output/"MEETING.deetsnap"))
        if t==horizon:break
        w.advance()
    meet=next(x for x in trace if x["tick"]==m["arrival_tick"])["sites"]["meeting"]
    o=w.runtime.observe(coordinate(m["hub"]))
    # Decode the captured historical record, not an expected answer.
    rec=d.decode_record(meet["RAW"])
    relation=("same" if rec.dx==0 else "positive_discrepancy" if rec.dx>0 else "negative_discrepancy") \
        if meet["active"] and (rec.dy,rec.dz)==(1,1) else None
    result={"metadata":m,"trace":trace,"meeting":meet,"decoded_relation":relation,
            "receipts":[{"id":i,"status":str(w.runtime.receipt(i).status),
                         "reason":w.runtime.receipt(i).reason,
                         "effective_tick":w.runtime.receipt(i).effective_tick} for i in receipts],
            "final_tick":w.runtime.current_tick,"external_operations":list(w.external_operations),
            "no_post_T0_direct_RAW_or_clock_edits":True,
            "attribution":"Native finite comparator and branch use; expectation origin is an external protocol here"}
    if output:
        w.save_snapshot(str(output/"FINAL.deetsnap"))
        (output/"MEASUREMENTS.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result
