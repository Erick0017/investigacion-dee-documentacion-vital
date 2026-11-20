"""Third declared C2 design, isolated draft. No old edits, CS or Native."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1];H=P/'codigo'

def once(s,a,b):
    if s.count(a)!=1:raise ValueError('Nonunique locator:'+a[:80])
    return s.replace(a,b,1)

if __name__=='__main__':
    src=H/'pi04_coordinacion_adquirida_R02_OP1.py';old=src.read_bytes()
    if hashlib.sha256(old).hexdigest()!='1559aa44a39e93daf196ee38359846757972d27c5f6838bf54c3d7f94228761c':raise ValueError('Exact old OP1 required')
    s=old.decode('utf8').replace('\r\n','\n')
    s=once(s,'VERSION = "PI04.C2.native_capability_choice_actual_result_chain.R02_CONTEXT_CUT_CANDIDATE"','VERSION = "PI04.C2C.single_current_early_Q_read_hold_q6.R01_DRAFT"')
    s=once(s,'KEY = "DEE.Cognitive.PI04.C2.coordination.R01"','KEY = "DEE.Cognitive.PI04.C2C.coordination.R01"')
    s=once(s,'FOLDER = "PI04_C2_COORDINACION_R01"','FOLDER = "PI04_C2C_COORDINACION_R01"')
    s=once(s,'"PROTOCOLO_PI04_C2_R01.json"','"PROTOCOLO_PI04_C2C_R01.json"')
    s=s.replace('"eci01-pi04-c2-','"eci01-pi04-c2c-')
    s=once(s,'return _module("pi04_selector_contextual_C2_R01")','return _module("pi04_sensor_central_C2C_R01")')
    s=once(s,'"DEE.PI04.C2.protocol.R01"','"DEE.PI04.C2C.protocol.R01"')
    s=once(s,'p["calibration_values"] != [0, 1, 4, 44, 47, 50]','p["calibration_values"] != [0, 4, 5]')
    s=s.replace('row["valor"] in (0, 1, 4, 44, 47, 50)','row["valor"] in (0, 4, 5)')
    s=s.replace('.startswith("C2CAL")','.startswith("C2CCAL")').replace('named C2CAL diagnostic','named C2CCAL diagnostic')
    s=s.replace('Finite six-call calibration horizon','Finite three-call calibration horizon')
    s=once(s,'    a.run_until(q+6); reader = _sensor().read_fixed(a, q)',
           '    a.run_until(q+4); reader = _sensor().read_fixed(a, q)\n    a.run_until(q+6)  # Hold observed command; downstream age/copy calendar unchanged.')
    s=once(s,'    a.run_until(cal["query_read_tick"]); first_reader=_sensor().read_fixed(a,q)',
           '    a.run_until(q+4); first_reader=_sensor().read_fixed(a,q)\n    a.run_until(cal["query_read_tick"])  # Prepared two-tick IO hold, never choose another reader.')
    s=once(s,'"first_reader":first_reader,"first_motor":first_motor,"selected_operation":operation,',
           '"first_reader":first_reader,"first_motor":first_motor,"selected_operation":operation,\n            "physical_read_tick":q+4,"actuation_availability_tick":cal["query_read_tick"],')
    added='''def _require_closed_predecessors(a, directory=None):
    """Read the two actual adverse futures, without changing their keys/logs."""
    old = _module("pi04_coordinacion_adquirida")
    former = old._get(a)
    if not former.get("admitted") or former.get("arm") != "real" or former.get("ordinal") != 11:
        raise ValueError("Actual old C2 real eleven-opportunity prefix required")
    if former.get("pending") or former.get("uncertain") or not str(former.get("halted_reason", "")).startswith("First NULL/"):
        raise ValueError("Old C2 firstNULL must remain closed/coherent and halted")
    if len(former.get("rows", [])) != 11 or former["rows"][-1].get("first_choice") is not None:
        raise ValueError("Old C2 last firstNULL row missing")
    b = _module("pi04_coordinacion_simetrica_C2B")
    bs = b._get(a)
    if not bs.get("admitted") or bs.get("arm") != "real" or bs.get("ordinal") != 3 or len(bs.get("rows", [])) != 3:
        raise ValueError("Actual C2B three-opportunity future required, not another imported life")
    if any(bs.get(k) for k in ("pending", "uncertain", "halted_reason")):
        raise ValueError("C2B must be coherently closed; no pending cleanup or repeated operation")
    dose = None
    if directory is not None:
        for module in (old, b):
            deps = module.operational_dependencies(a, directory)
            if any(deps.get(k) for k in ("pending", "uncertain", "device_pending", "device_feedback_pending", "device_uncertain")):
                raise ValueError("Predecessor journal/device is not coherent")
        journal = Path(directory) / b.FOLDER / "eventos.jsonl"
        values = []
        with journal.open("r", encoding="utf8") as lines:
            for line in lines:
                item = json.loads(line)
                if item.get("kind") == "C2_OPPORTUNITY_COMPLETED": values.append(item["result"])
        if [v["ordinal"] for v in values] != [0, 1, 2]:
            raise ValueError("All three original C2B completed primaries must be present")
        receipts = {}
        for value in values:
            groups = [value["requests"], value["native_arithmetic"]["native_operation"]["native_trial"]["requests"], value["second_native_use"]["requests"]]
            for items in groups:
                for req in items:
                    r = req["receipt"]; rid = int(req["id"])
                    if rid != r["id"] or (rid in receipts and receipts[rid] != r):
                        raise ValueError("Contradictory predecessor Native receipt alias")
                    if not value["before_tick"] <= r["requested_tick"] <= value["after_tick"]:
                        raise ValueError("Inherited/nonwindow receipt is not a new B input")
                    receipts[rid] = r
        dose = {"requested": len(receipts), "applied": sum(r["status"] == "applied" for r in receipts.values()),
                "rejected": sum(r["status"].startswith("rejected") for r in receipts.values()),
                "other": sum(r["status"] != "applied" and not r["status"].startswith("rejected") for r in receipts.values())}
        if dose != {"requested": 561, "applied": 559, "rejected": 2, "other": 0}:
            raise ValueError("C2B original three-opportunity adverse dose differs: " + repr(dose))
    return {"old_C2_KEY": old.KEY, "old_C2_ordinal": 11, "old_C2_halt": former["halted_reason"],
            "old_C2_state_sha256": _sha(json.dumps(_jsonsafe(former), sort_keys=True, separators=(",", ":")).encode("utf8")),
            "old_C2B_KEY": b.KEY, "old_C2B_ordinal": 3, "old_C2B_last_tick": bs["rows"][-1]["after_tick"],
            "old_C2B_state_sha256": _sha(json.dumps(_jsonsafe(bs), sort_keys=True, separators=(",", ":")).encode("utf8")),
            "old_C2B_actual_Native_dose": dose, "scope": "Both original histories/devices/journals remain intact; no repair/reset/reclassification of old failures"}


'''
    s=once(s,'def validate(a, row):',added+'def validate(a, row):')
    s=once(s,'    if row["modo"] == PREPARE:\n        if KEY in _entries(a):',
           '    if row["modo"] == PREPARE:\n        _require_closed_predecessors(a)\n        if KEY in _entries(a):')
    s=once(s,'    before = _physical(a)\n    m = {"version": VERSION, "life_id": identity["life_id"], "prepared_tick": int(a.tick),',
           '    predecessors = _require_closed_predecessors(a, directory)\n    before = _physical(a)\n    m = {"version": VERSION, "life_id": identity["life_id"], "prepared_tick": int(a.tick),')
    s=once(s,'"attribution": "External sensory/termination design only; inherited banks/history preserved"}',
           '"predecessors_preserved": predecessors,\n         "attribution": "External fixed earlier reader and two-tick hold only; all inherited physical banks/history/interfaces preserved"}')
    target=H/'pi04_coordinacion_central_C2C.py'
    if target.exists():raise ValueError('Preserve prior C2C draft')
    compile(s,str(target),'exec');target.write_text(s,encoding='utf8',newline='')
    if src.read_bytes()!=old:raise AssertionError('Old OP1 changed')
    p=json.loads((H/'PROTOCOLO_PI04_C2B_R01.json').read_text(encoding='utf8'));p['schema']='DEE.PI04.C2C.protocol.R01';p['status']='DRAFT';p['calibration_values']=[0,4,5]
    dev=[4,5,4,4,5,5,4,5,4,5,4,5]
    p['schedule']=[{'stage':'development','context':c,'left':16,'right':9}for c in dev]
    res=[1,6,8,2,6,3,1,8]
    p['schedule'] += [{'stage':'reserved','context':c,'left':15 if i<4 else 17,'right':8}for i,c in enumerate(res)]
    p['schedule'] += [{'stage':'retention','context':3,'left':14,'right':9},{'stage':'retention','context':6,'left':18,'right':7},
        {'stage':'retention','context':2,'left':29,'right':4},{'stage':'retention','context':6,'left':6,'right':5},
        {'stage':'retention','context':3,'left':26,'right':4},{'stage':'retention','context':7,'left':7,'right':6}]
    p['dependencies_sha256'].pop('pi04_sensor_simetrico_C2B_R01.py',None)
    p['dependencies_sha256']['pi04_sensor_central_C2C_R01.py']=hashlib.sha256((H/'pi04_sensor_central_C2C_R01.py').read_bytes()).hexdigest()
    p['dependencies_sha256']['pi04_coordinacion_simetrica_C2B.py']='d77dea2b4623457bf184b95724c7eb8e1d73a3898b2cd64cccfb35734325d677'
    p['attribution']='UNEXECUTED third declared C2 design: same actual descendant after old C2 firstNULL and C2B FI-admission failure; single original scalar datum, fixed centralQ q4 reader held untilq6, original efference/Native functions/feedback calendar.26explicit offers; twelve development contexts4/5; eight NEW reserved contexts1/6/8/2/6/3/1/8; no old keys/devices/logs/RAW/clocks/interfaces reset. Root must await port-viability diagnosis, freeze and validate instrumentation before evaluation; no claimed capacity or adoption.'
    proto=H/'PROTOCOLO_PI04_C2C_R01.json'
    if proto.exists():raise ValueError('Preserve prior C protocol')
    proto.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    proof={'schema':'PI04.C2C.third_design.static_derivation.R01','status':'DRAFT_NOT_INSTALLED_OR_NATIVE_EXECUTED',
        'source_sha256':hashlib.sha256(old).hexdigest(),'controller':str(target),'controller_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'sensor_sha256':hashlib.sha256((H/'pi04_sensor_central_C2C_R01.py').read_bytes()).hexdigest(),
        'protocol_sha256':hashlib.sha256(proto.read_bytes()).hexdigest(),'Native_ticks':0,'CS_modified':False,
        'old_C2_C2B_files_modified':False,'actual_read_q':4,'actuator_available_q':6,'same_copy_q':7,
        'physical_preparation':'NONE: no extra datum/interface/birth/RAW/clock change; metadata declaration only'}
    out=P/'control/C2C_R01_DERIVACION_ESTATICA.json'
    if out.exists():raise ValueError('Preserve prior derivation')
    out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(proof,ensure_ascii=False,indent=2))
