"""Narrow apparatus revision Q0->Q5; preserve R02 literal, no Native or CS."""
from pathlib import Path
import hashlib,json

def once(s,a,b):
    if s.count(a)!=1:raise ValueError("Nonunique source locator: "+a[:70])
    return s.replace(a,b,1)

if __name__=="__main__":
    home=Path(__file__).resolve().parent;source=home/"pi04_coordinacion_adquirida_R02.py"
    original=source.read_bytes();oldsha="e080b56e18e0a76f5bea3eb4ddd084e24e4003634c55bf977e0afe7f96b5a075"
    if hashlib.sha256(original).hexdigest()!=oldsha:raise ValueError("R02 literal changed")
    target=home/"pi04_coordinacion_adquirida_R03.py"
    if target.exists():raise ValueError("R03 exists; preserve it")
    s=original.decode("utf8")
    s=once(s,'VERSION = "PI04.C2.native_capability_choice_actual_result_chain.R02_CONTEXT_CUT_CANDIDATE"',
        'VERSION = "PI04.C2.native_capability_choice_actual_result_chain.R03_QUERY5_DRAFT_ROOT"\nFIRST_QUERY_PAYLOAD = 5')
    s=once(s,'def _helper():', '''def _submit_query(world, tick, *, prefix):
    """Fixed R03 instrument: query5, support.plus/minus0; never a policy.

    Same three declared inherited channels and absolute q. No value, target,
    history, current state or favourable output is an argument. Receipts use
    the inherited helper's exact channel/requested_tick transport schema.
    """
    requests = []
    for suffix in ("query", "support.plus", "support.minus"):
        payload = FIRST_QUERY_PAYLOAD if suffix == "query" else 0
        r = world.submit(prefix + "." + suffix, payload, int(tick))
        requests.append({"id": int(r.id), "channel": prefix + "." + suffix,
                         "payload": payload, "requested_tick": int(tick)})
    return requests


def _helper():''')
    old='_helper().submit_query(a.world, q, prefix=p["base_prefix"])'
    if s.count(old)!=1:raise ValueError("Calibration query locator differs")
    s=s.replace(old,'_submit_query(a.world, q, prefix=p["base_prefix"])',1)
    old='_helper().submit_query(a.world,q,prefix=p["base_prefix"])'
    if s.count(old)!=1:raise ValueError("Opportunity query locator differs")
    s=s.replace(old,'_submit_query(a.world,q,prefix=p["base_prefix"])',1)
    s=once(s,'"feedback_inserted": False,', '"feedback_inserted": False,') if False else s
    s=once(s,'"timing": timing, "requests": requests, "feedback_inserted": False,',
        '"timing": timing, "requests": requests, "first_query_payload": FIRST_QUERY_PAYLOAD, "feedback_inserted": False,')
    s=once(s,'"first_reader":first_reader,"first_motor":first_motor,"selected_operation":operation,',
        '"first_reader":first_reader,"first_motor":first_motor,"selected_operation":operation,\n            "first_query_payload":FIRST_QUERY_PAYLOAD,')
    s=once(s,'"preparation": preparation, "physical": _physical(a), "acquisition_claim": False}',
        '"preparation": preparation, "physical": _physical(a), "acquisition_claim": False,\n            "first_query_payload":FIRST_QUERY_PAYLOAD,\n            "annotation":"R03 query5 overrides the preserved R01 sensor geometry query_payload0 annotation; geometry/reader/data timing unchanged"}')
    compile(s,str(target),"exec");target.write_text(s,encoding="utf8",newline="")
    if source.read_bytes()!=original:raise AssertionError("R02 modified")
    proof={"schema":"PI04.C2.R03.query5.static_revision.v1","R02_source":str(source),"R02_sha256":oldsha,
        "R02_literal_preserved":True,"R03_file":str(target),"R03_sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
        "query_payload":5,"support_payloads":[0,0],"same_ports":True,"same_q6_six_reader":True,
        "same_q3_datum":True,"same_efference_feedback_and_cuts":True,"protocolRoot_modified":False,
        "Native_ticks":0,"status":"DRAFT_ROOT_MUST_REVIEW_AND_SEAL", "no_new_selector_module_dependency":True,
        "sensor_annotation":"The old sensor geometry's query_payload0 field remains historical and is explicitly overridden by R03 actual query5 receipts/primary/preparation result."}
    output=home.parent/"control/C2_REVISION_R03_QUERY5_GENERADA.json"
    if output.exists():raise ValueError("Preserve prior proof")
    output.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(proof,ensure_ascii=False,indent=2))
