"""C2C candidate: ONE inherited datum, fixed central Q read at q+4.

No DEE import or execution at import. Preparation changes metadata only,
requiring all inherited interfaces; no new channel, birth, RAW/clocks or N.
The host holds the measured command until q+6 before arithmetic/efference.
"""
from pathlib import Path
import importlib.util
VERSION="PI04.C2C.single_datum_fixed_central_Q_q4.R01_CANDIDATE"
KEY="DEE.Cognitive.PI04.C2C.central_sensor.R01"
ORIGIN=(19,54,5)
_OLD=None

def _old():
    global _OLD
    if _OLD is None:
        p=Path(__file__).with_name("pi04_selector_contextual_C2_R01.py")
        s=importlib.util.spec_from_file_location("C2C_preserved_original_single_sensor",p)
        m=importlib.util.module_from_spec(s);s.loader.exec_module(m);_OLD=m
    return _OLD

def geometry():
    return {"N":67,"datum_sites":[[18,54,6]],"query_payload":0,"datum_relative_to_query":3,
            "reader_site":list(ORIGIN),"reader_relative_to_query":4,"actuator_available_relative_to_query":6,
            "signature":"Active SEM1 atQ, direction[dx,+1,z], dx=-1/0/+1,z=-1/0; unique physical record",
            "scope":"Earlier fixed instrument before possible output-route interception, not a newly acquired sensor or measured internal trajectory"}

def prepare(a):
    _,_,_,decode,encode,entries,life=_old()._guard(a)
    if KEY in entries:raise ValueError("C2C preparation already exists; no reinterpretation/reinstall")
    if _old().KEY not in entries or decode(entries[_old().KEY])["version"]!=_old().VERSION:
        raise ValueError("Actual inherited original sensory interfaces required; no replacement anatomy")
    names=set(a.world.runtime.channel_names)
    required={"PI04.C2.CURRENT.R01.datum","PI03.TC.R01.query","PI03.TC.R01.support.plus","PI03.TC.R01.support.minus"}
    if not required<=names:raise ValueError("Missing original single-datum/query interfaces")
    from app.native_tools import physical
    before=physical(a.world)
    a.world.runtime.set_snapshot_metadata(KEY,encode({"version":VERSION,"life_id":life,"prepared_tick":int(a.tick),"geometry":geometry()}))
    after=physical(a.world)
    if before!=after:raise RuntimeError("Administrative sensor declaration changed physical arrays/time")
    return {"version":VERSION,"before":before,"after":after,"physical_equal":True,"new_native_ticks":0,
            "requests":[],"new_interfaces":0,"new_births":0,"geometry":geometry(),"verified_function":False}

def submit_datum(a,value,query_tick):
    _,_,_,decode,_,entries,_=_old()._guard(a)
    if KEY not in entries or decode(entries[KEY])["version"]!=VERSION:raise ValueError("Explicit C2C sensor preparation required")
    return _old().submit_datum(a,value,query_tick)

def read_fixed(a,query_tick):
    d,exact,_,decode,_,entries,_=_old()._guard(a)
    if KEY not in entries or decode(entries[KEY])["version"]!=VERSION:raise ValueError("Explicit C2C sensor preparation required")
    if type(query_tick)is not int or int(a.tick)!=query_tick+4:raise ValueError("Exact fixed q+4 central reader only; no window search")
    o=exact(a.world.runtime.observe(d.Coordinate(*ORIGIN)))
    v=list(o["direction"])
    valid=int(o["state"])>0 and int(o["semantic"])==1 and len(v)==3 and v[0]in(-1,0,1)and v[1]==1 and v[2]in(-1,0)
    return {"version":VERSION,"tick":int(a.tick),"observation":o,
            "candidates":[{"choice":v[0],"site":list(ORIGIN),"direction":v}]if valid else[],
            "choice":v[0]if valid else None,"zero_is_not_NULL":True,
            "physical_read_tick":query_tick+4,"available_for_actuation_tick":query_tick+6,
            "decoder":"Single fixed central Q record, SEM1 active and exact Y+1/Z-1or0 signature; no history/expected/current-value argument",
            "functional_validation_pending":True}
