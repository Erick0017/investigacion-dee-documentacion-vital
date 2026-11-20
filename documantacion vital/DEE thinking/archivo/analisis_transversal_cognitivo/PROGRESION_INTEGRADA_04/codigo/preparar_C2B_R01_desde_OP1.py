"""Build separate C2B program/protocol, preserving all prior C2 bytes."""
from pathlib import Path
import hashlib,json

def once(s,a,b):
    if s.count(a)!=1:raise ValueError("Nonunique locator: "+a[:80])
    return s.replace(a,b,1)

if __name__=="__main__":
    home=Path(__file__).resolve().parent;source=home/"pi04_coordinacion_adquirida_R02_OP1.py"
    old=source.read_bytes();oldsha="1559aa44a39e93daf196ee38359846757972d27c5f6838bf54c3d7f94228761c"
    if hashlib.sha256(old).hexdigest()!=oldsha:raise ValueError("Exact R02_OP1 source required")
    target=home/"pi04_coordinacion_simetrica_C2B.py"
    if target.exists():raise ValueError("Preserve prior C2B candidate")
    s=old.decode("utf8").replace("\r\n","\n")
    s=once(s,'VERSION = "PI04.C2.native_capability_choice_actual_result_chain.R02_CONTEXT_CUT_CANDIDATE"',
           'VERSION = "PI04.C2B.symmetric_current_native_coordination.R01_DRAFT"')
    s=once(s,'KEY = "DEE.Cognitive.PI04.C2.coordination.R01"','KEY = "DEE.Cognitive.PI04.C2B.coordination.R01"')
    s=once(s,'FOLDER = "PI04_C2_COORDINACION_R01"','FOLDER = "PI04_C2B_COORDINACION_R01"')
    s=once(s,'"PROTOCOLO_PI04_C2_R01.json"','"PROTOCOLO_PI04_C2B_R01.json"')
    s=s.replace('"eci01-pi04-c2-','"eci01-pi04-c2b-')
    s=once(s,'return _module("pi04_selector_contextual_C2_R01")','return _module("pi04_sensor_simetrico_C2B_R01")')
    s=once(s,'"DEE.PI04.C2.protocol.R01"','"DEE.PI04.C2B.protocol.R01"')
    s=once(s,'p["calibration_values"] != [0, 1, 4, 44, 47, 50]', 'p["calibration_values"] != [0, 4, 6]')
    s=s.replace('row["valor"] in (0, 1, 4, 44, 47, 50)','row["valor"] in (0, 4, 6)')
    s=s.replace('preregistered0/1/4/44/47/50','preregistered0/4/6')
    s=s.replace('.startswith("C2CAL")','.startswith("C2BCAL")')
    s=s.replace('named C2CAL diagnostic','named C2BCAL diagnostic')
    s=s.replace('Finite six-call calibration horizon','Finite three-call calibration horizon')
    # Both identical scalar packets are admitted at the exact same q+3.
    s=once(s,'requests.append(_sensor().submit_datum(a, row["valor"], q))','requests.extend(_sensor().submit_datum(a, row["valor"], q))')
    s=once(s,'requests.append(_sensor().submit_datum(a,spec["context"],q))','requests.extend(_sensor().submit_datum(a,spec["context"],q))')
    s=s.replace('context_cut omits ONE datum event entirely','context_cut omits BOTH symmetric datum events entirely')
    s=s.replace('Only the later per-opportunity scalar context datum event; no material replacement0',
                'Only the later pair of identical symmetric scalar context datum events; no material replacement0')
    s=once(s,'"A": (-1,-1,0), "B": (1,-1,0), "Q": (0,0,0), "datum": (-1,0,1),',
           '"A": (-1,-1,0), "B": (1,-1,0), "Q": (0,0,0), "datum": (-1,0,1), "datum_symmetric": (-1,0,-1),')
    extra='''def _require_original_NULL(a, directory=None):
    """Read/verify the old halted future; NEVER edit or reclassify it."""
    old = _module("pi04_coordinacion_adquirida")
    previous = old._get(a)
    if not previous.get("admitted") or previous.get("arm") != "real" or previous.get("ordinal") != 11:
        raise ValueError("C2B preparation requires the actual closed old C2 real ordinal11")
    if previous.get("pending") or previous.get("uncertain") or not str(previous.get("halted_reason", "")).startswith("First NULL/"):
        raise ValueError("Old first-NULL future must remain halted but coherent, with no pending uncertainty")
    rows = previous.get("rows", [])
    if len(rows) != 11 or rows[-1].get("first_choice") is not None or sum(row.get("first_choice") is None for row in rows) != 1:
        raise ValueError("Exactly one first NULL in the last recorded old C2 opportunity required")
    proof = None
    if directory is not None:
        proof = old.operational_dependencies(a, directory)
        if proof.get("pending") or proof.get("uncertain") or proof.get("device_pending") or proof.get("device_feedback_pending") or proof.get("device_uncertain"):
            raise ValueError("Old C2 complete device/journal is not coherent; no repair/clear performed")
    raw = json.dumps(_jsonsafe(previous), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf8")
    return {"old_KEY": old.KEY, "old_folder": old.FOLDER, "old_state_sha256": _sha(raw),
            "old_ordinal": 11, "old_halt_preserved": previous["halted_reason"],
            "old_last_tick": rows[-1]["after_tick"], "dependencies_checked": proof is not None,
            "scope": "Original C2 remains physical/history evidence; no counter, device, log or metadata rewritten"}


'''
    s=once(s,'def validate(a, row):',extra+'def validate(a, row):')
    s=once(s,'    if row["modo"] == PREPARE:\n        if KEY in _entries(a):',
           '    if row["modo"] == PREPARE:\n        _require_original_NULL(a)\n        if KEY in _entries(a):')
    s=once(s,'    before = _physical(a)\n    m = {"version": VERSION, "life_id": identity["life_id"], "prepared_tick": int(a.tick),',
           '    previous_closed = _require_original_NULL(a, directory)\n    before = _physical(a)\n    m = {"version": VERSION, "life_id": identity["life_id"], "prepared_tick": int(a.tick),')
    s=once(s,'"attribution": "External sensory/termination design only; inherited banks/history preserved"}',
           '"previous_C2_preserved": previous_closed,\n         "attribution": "External symmetric sensory interface only; same inherited banks/history; no old reset"}')
    # Keep useful failure evidence, but do not let the coherent old C2 halt
    # masquerade as a new C2B uncertain future in its own dependency function.
    compile(s,str(target),"exec");target.write_text(s,encoding="utf8",newline="")
    if source.read_bytes()!=old:raise AssertionError("Historical C2 source changed")
    oldp=home/"PROTOCOLO_PI04_C2_EVALUACION_R02.json"
    p=json.loads(oldp.read_text(encoding="utf8"));p["schema"]="DEE.PI04.C2B.protocol.R01";p["status"]="DRAFT"
    p["calibration_values"]=[0,4,6]
    p["attribution"]="UNEXECUTED C2B draft: same physical trajectory after old C2 first NULL, new explicit paired scalar-Z sensor; query0, original six-signature reader, old clocks/banks/history/resources preserved. Native learning/usefulness unverified.24new explicit offers:12development/8reserved/2retention/2future; old device/counters remain separate intact."
    if len(p["schedule"])!=24:raise ValueError("Expected original frozen24-offer horizon")
    for i,c in enumerate((2,5,7,3,5,3,2,7)):
        p["schedule"][12+i]={"stage":"reserved","context":c,"left":15 if i<4 else 17,"right":8}
    p["dependencies_sha256"]["pi04_sensor_simetrico_C2B_R01.py"]=hashlib.sha256((home/"pi04_sensor_simetrico_C2B_R01.py").read_bytes()).hexdigest()
    p["dependencies_sha256"]["pi04_coordinacion_adquirida.py"]=oldsha
    proto=home/"PROTOCOLO_PI04_C2B_R01.json"
    if proto.exists():raise ValueError("Preserve previous B protocol")
    proto.write_text(json.dumps(p,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    proof={"schema":"PI04.C2B.static_derivation.R01","source":str(source),"source_sha256":oldsha,
        "source_literal_preserved":True,"candidate":str(target),"candidate_sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
        "sensor_sha256":hashlib.sha256((home/"pi04_sensor_simetrico_C2B_R01.py").read_bytes()).hexdigest(),
        "protocol":str(proto),"protocol_sha256":hashlib.sha256(proto.read_bytes()).hexdigest(),
        "Native_ticks":0,"CS_product_modified":False,"old_C2_modified":False,"status":"DRAFT_NO_NATIVE_VALIDATION"}
    out=home.parent/"control/C2B_R01_DERIVACION_ESTATICA.json"
    if out.exists():raise ValueError("Preserve prior proof")
    out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(proof,ensure_ascii=False,indent=2))
