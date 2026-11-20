"""Preserve literal R01 and build the isolated, narrow context-input cut R02."""
from pathlib import Path
import hashlib,json

def replace_once(text,old,new):
    if text.count(old)!=1:raise ValueError("Source locator is not unique: "+old[:80])
    return text.replace(old,new,1)

if __name__=="__main__":
    home=Path(__file__).resolve().parent
    original=home/"pi04_coordinacion_adquirida.py"
    before=original.read_bytes()
    expected="df7eb3c24a47f42e86ed5814bbd3330f67d84babcc83c3447c1d648766dada25"
    if hashlib.sha256(before).hexdigest()!=expected:raise ValueError("Published R01 changed; refuse rewrite")
    output=home/"pi04_coordinacion_adquirida_R02.py"
    if output.exists():raise ValueError("R02 already exists; preserve it")
    text=before.decode("utf8")
    text=replace_once(text,'VERSION = "PI04.C2.native_capability_choice_actual_result_chain.R01_CANDIDATE"',
        'VERSION = "PI04.C2.native_capability_choice_actual_result_chain.R02_CONTEXT_CUT_CANDIDATE"')
    text=replace_once(text,'STATE = "eci01-pi04-c2-estado"\nMODES = {PREPARE, CALIBRATE, ADMIT, OPPORTUNITY, STATE}',
        'STATE = "eci01-pi04-c2-estado"\nCUT_CONTEXT = "eci01-pi04-c2-cortar-contexto"\nMODES = {PREPARE, CALIBRATE, ADMIT, OPPORTUNITY, STATE, CUT_CONTEXT}')
    text=replace_once(text,'ARMS = {"real", "none", "yoked", "link_cut", "actuator_null"}',
        'ARMS = {"real", "none", "yoked", "link_cut", "actuator_null", "context_cut"}')
    text=replace_once(text,'mode in {PREPARE, OPPORTUNITY, STATE}', 'mode in {PREPARE, OPPORTUNITY, STATE, CUT_CONTEXT}')
    text=replace_once(text,'row.get("brazo") in ARMS - {"yoked"}', 'row.get("brazo") in ARMS - {"yoked", "context_cut"}')
    text=replace_once(text,'    protocol(material=True, evaluation=True)\n    if identity',
        '    protocol(material=True, evaluation=True)\n    if row["modo"] == CUT_CONTEXT:\n        _validate_context_cut(p, identity, m)\n        return\n    if identity')
    text=replace_once(text,'    if m["ordinal"] >= len(p["schedule"]):\n        raise ValueError("Frozen opportunities exhausted; no automatic supply or restart")',
        '    if m["arm"] == "context_cut" and (not 12 <= m["ordinal"] < 20 or p["schedule"][m["ordinal"]]["stage"] != "reserved"):\n        raise ValueError("Context-cut control is limited to the eight reserved opportunities; no retention")\n    if m["ordinal"] >= len(p["schedule"]):\n        raise ValueError("Frozen opportunities exhausted; no automatic supply or restart")')
    text=replace_once(text,'    requests.append(_sensor().submit_datum(a,spec["context"],q))',
        '    if m["arm"] != "context_cut":\n        requests.append(_sensor().submit_datum(a,spec["context"],q))\n    # context_cut omits ONE datum event entirely: no zero/sham/replacement.\n    # All generic queries, six-site reader, real Native functions and feedback remain.')
    text=replace_once(text,'"before_tick":start,"after_tick":int(a.tick),"calendar":cal,"normalized_calendar":normalized,',
        '"before_tick":start,"after_tick":int(a.tick),"calendar":cal,"normalized_calendar":normalized,\n            "context_input_supplied":m["arm"] != "context_cut",')
    marker='def _home(directory):'
    added='''def _validate_context_cut(p, identity, m):
    """Pure administrative guard; not a sensor/reader or learned decision."""
    life = identity["life_id"]
    if not life.startswith(PREFIX) or "CTX_CUT_" not in life[len(PREFIX):] or life.endswith("CTX_CUT_"):
        raise ValueError("Only an explicitly named PI04_*CTX_CUT_* diagnostic clone")
    if m.get("arm") != "real" or not m.get("admitted") or not m.get("ready") or m.get("ordinal") != 12:
        raise ValueError("Context cut only after exactly twelve completed real training opportunities")
    if any(m.get(k) for k in ("pending", "uncertain", "halted_reason")) or "context_cut_provenance" in m:
        raise ValueError("Cut requires a closed, uncut future; no overwrite/retry")
    if len(m.get("rows", [])) != 12 or any(row.get("stage") != "development" for row in m["rows"]):
        raise ValueError("Twelve actually recorded development rows required")
    if len(p["schedule"]) < 20 or any(row["stage"] != "reserved" for row in p["schedule"][12:20]):
        raise ValueError("Exactly the following eight reserved opportunities must be available")


def cut_context(a, directory):
    """Explicit zero-tick diagnostic lesion, never a Native learned action.

    The existing hardware identity guard with the exact owned directory rejects
    ACTIVO. No RAW/clocks/reader/port/resource is edited, and no datum is emitted.
    """
    validate(a, {"modo": CUT_CONTEXT})
    p, ph, identity = _identity(a, directory)  # Includes inherited no-ACTIVO guard.
    m = _get(a); _validate_context_cut(p, identity, m)
    deps = operational_dependencies(a, directory)
    if deps.get("device_pending") or deps.get("device_feedback_pending") or deps.get("device_uncertain"):
        raise ValueError("Device must be closed before diagnostic cut")
    file = _home(directory) / "CORTE_CONTEXTO.json"
    if file.exists() or file.with_name(file.name + ".pending").exists():
        raise ValueError("Existing context lesion proof preserved; no overwrite")
    before = _physical(a)
    m["arm"] = "context_cut"
    m["context_cut_provenance"] = {"source_arm": "real", "source_ordinal": 12,
        "source_tick": int(a.tick), "relative_proof": file.name,
        "scope": "External diagnostic omission of current context only; not acquired sensor selection"}
    _save(a, m)
    after = _physical(a)
    proof = {"version": VERSION, "life_id": identity["life_id"], "protocol_sha256": ph,
        "ordinal": 12, "arm_before": "real", "arm_after": "context_cut", "before": before, "after": after,
        "physical_equal": before == after, "new_native_ticks": int(a.tick)-before["tick"],
        "omitted": "Only the later per-opportunity scalar context datum event; no material replacement0",
        "preserved": "All query/support events, six-site q+6 reader, efference, actual FI/MU, device and generic real return"}
    _atomic(file, proof)
    _record(a, m, directory, {"kind": "C2_CONTEXT_DIAGNOSTIC_CUT", "proof": proof,
                            "relative_file": file.name, "sha256": _sha(file.read_bytes())})
    if before != after:
        raise RuntimeError("Unexpected physical change in administrative lesion; preserve and stop")
    return proof


'''
    text=replace_once(text,marker,added+marker)
    text=replace_once(text,'    if row["modo"]==ADMIT:return admit(a,row,directory)\n    return opportunity(a,directory)',
        '    if row["modo"]==ADMIT:return admit(a,row,directory)\n    if row["modo"]==CUT_CONTEXT:return cut_context(a,directory)\n    return opportunity(a,directory)')
    compile(text,str(output),"exec")
    output.write_text(text,encoding="utf8",newline="")
    if original.read_bytes()!=before:raise AssertionError("Original R01 was changed")
    proof={"schema":"PI04.C2.R02.static_revision.v1","original":str(original),"original_sha256":expected,
           "original_unchanged":True,"revision":str(output),"revision_sha256":hashlib.sha256(output.read_bytes()).hexdigest(),
           "Native_imports":False,"Native_ticks":0,"protocol_modified":False,
           "changes":["Explicit posttrain12 context-input diagnostic cut only","Omit datum event, no zero substitute",
                      "Fixed reader/functions/efference/outcome retained","Eight reserved limit; no control retention",
                      "Strict diagnostic identity/no-ACTIVO inherited guard; journal/JSON proof and physical equality"]}
    target=home.parent/"control"/"C2_REVISION_R02_GENERADA.json"
    if target.exists():raise ValueError("Preserve prior revision proof")
    target.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(proof,ensure_ascii=False,indent=2))
