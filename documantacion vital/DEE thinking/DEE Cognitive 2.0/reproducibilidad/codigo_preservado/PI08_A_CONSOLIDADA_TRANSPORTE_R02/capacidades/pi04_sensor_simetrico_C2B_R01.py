"""C2B candidate: two identical scalar datum events symmetric in Z.

Import is stdlib only. Preparation declares ONE extra interface at a verified
RAW0 site and preserves every physical record/clock. No birth, clamp, reset,
new Runtime or learned-field transplant is performed. The root alone executes.
The existing plus-Z datum/terminators/six-signature q+6 reader are reused.
"""
from pathlib import Path
import importlib.util

VERSION="PI04.C2B.dual_identical_datum_symmetric_Z.R01_CANDIDATE"
KEY="DEE.Cognitive.PI04.C2B.symmetric_sensor.R01"
EXTRA_CHANNEL="PI04.C2B.CURRENT.R01.datum.minusZ"
ORIGIN=(19,54,5)
PLUS_SITE=(18,54,6)
MINUS_SITE=(18,54,4)
N=67
_OLD=None

def _old():
    global _OLD
    if _OLD is None:
        file=Path(__file__).with_name("pi04_selector_contextual_C2_R01.py")
        spec=importlib.util.spec_from_file_location("C2B_preserved_original_sensor",file)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);_OLD=m
    return _OLD

def geometry():
    return {"N":N,"origin":list(ORIGIN),"datum_sites":[list(PLUS_SITE),list(MINUS_SITE)],
            "datum_payloads":"Same exact current scalar c at both sites; no sign/answer-dependent selection",
            "datum_relative_to_query":3,"query_payload":0,"reader_relative_to_query":6,
            "reader":"Unmodified six-site/six-signature inherited sensor read_fixed",
            "prepared_change":"Only declare extra peripheral interface; no physical placement/birth/clock edit",
            "hypothesis":"Symmetric spatial contributions may remove the net Z component; not yet validated Native"}

def preflight(a):
    d,exact,_,decode,_,entries,life=_old()._guard(a)
    if _old().KEY not in entries or decode(entries[_old().KEY])["version"]!=_old().VERSION:
        raise ValueError("Inherited original sensory preparation required; never rebuild its stops")
    def obs(p):return exact(a.world.runtime.observe(d.Coordinate(*p)))
    extra=obs(MINUS_SITE);plus=obs(PLUS_SITE)
    return {"version":VERSION,"life_id":life,"tick":int(a.tick),"extra_site":list(MINUS_SITE),
            "extra":extra,"inherited_plus":plus,"already_prepared":KEY in entries,
            "extra_channel_exists":EXTRA_CHANNEL in set(a.world.runtime.channel_names),
            "eligible":KEY not in entries and EXTRA_CHANNEL not in set(a.world.runtime.channel_names)
                       and int(extra["raw"])==0 and int(plus["raw"])==0,
            "scope":"Only current RAW/current interface facts; inactive nonzero RAW is never cleared"}

def prepare(a):
    d,_,_,_,encode,_,life=_old()._guard(a)
    check=preflight(a)
    if not check["eligible"]:raise ValueError("Unsafe symmetric sensor preflight; preserve: "+repr(check))
    from app.native_tools import physical
    before=physical(a.world)
    c=d.ChannelSpec();c.name=EXTRA_CHANNEL;c.injection_site=d.Coordinate(*MINUS_SITE)
    c.direction=d.Direction(0,0,0);c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=False
    i=d.InterfaceSpec();i.name=EXTRA_CHANNEL;i.channel=c;a.world.declare_interface(i)
    after=physical(a.world)
    if before!=after:raise RuntimeError("Peripheral declaration unexpectedly changed Native physical arrays/time")
    a.world.runtime.set_snapshot_metadata(KEY,encode({"version":VERSION,"life_id":life,
        "prepared_tick":int(a.tick),"geometry":geometry(),"scope":"New prepared interface only; no acquired association installed"}))
    return {"version":VERSION,"preflight":check,"requests":[],"before":before,"after":after,
            "physical_equal":True,"new_native_ticks":0,"extra_interface":EXTRA_CHANNEL,
            "inherited_plus_channel":"PI04.C2.CURRENT.R01.datum","geometry":geometry(),"verified_function":False}

def submit_datum(a,value,query_tick):
    _,_,_,decode,_,entries,_=_old()._guard(a)
    if KEY not in entries or decode(entries[KEY])["version"]!=VERSION:
        raise ValueError("Explicit symmetric sensor preparation required")
    if type(value)is not int or not 0<=value<=512:raise ValueError("One exact identity scalar0..512")
    if type(query_tick)is not int or query_tick+3<=int(a.tick):raise ValueError("Fixed future q+3 boundary only")
    # Same input value/tick independent of response, target, operation or route.
    first=_old().submit_datum(a,value,query_tick)
    r=a.world.submit(EXTRA_CHANNEL,value,query_tick+3)
    second={"id":int(r.id),"channel":EXTRA_CHANNEL,"payload":value,"requested_tick":query_tick+3,
            "site":list(MINUS_SITE),"codec":"Second identical scalar c; symmetric-Z preparation, no selected answer"}
    return [first,second]

def read_fixed(a,query_tick):
    # EXACT old predicate, sites and q+6; no new favourable channel/window.
    return _old().read_fixed(a,query_tick)
